# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["relationalai==1.30.1", "ruamel.yaml==0.19.1"]
# ///
"""Independent structured-derivation compiler for the opt-in parity seat.

Reads raw YAML 1.2 and executes relational joins, projection and negation in
PyRel's local DuckDB backend. Scalar encoding implements the normative table in
representation-format.md, "Scalar and tuple identity"; no GND code is imported.
All engine fields contain identity strings, preserving exact numeric identity
without an intermediate floating-point conversion. This is a fixture oracle,
not a replacement for model validation.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import date, datetime
from importlib.metadata import version
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any


def _load_yaml(path: Path) -> dict[str, Any]:
    from ruamel.yaml import YAML

    document = YAML(typ="safe").load(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise TypeError(f"expected a mapping in {path}")
    return document


def _primitive(
    object_id: str, objects: dict[str, dict[str, Any]], seen: frozenset[str] = frozenset()
) -> str | None:
    if object_id in seen:
        raise ValueError("cyclic object reference")
    declaration = objects[object_id]
    if declaration.get("kind") == "value":
        return declaration.get("primitive")
    reference = declaration.get("reference") or {}
    if reference.get("value_type"):
        return _primitive(reference["value_type"], objects, seen | {object_id})
    if declaration.get("inherits_reference"):
        inherited = {
            _primitive(parent, objects, seen | {object_id})
            for parent in declaration.get("subtype_of", [])
        } - {None}
        if len(inherited) == 1:
            return inherited.pop()
    return None


def _identity(value: Any, primitive: str | None) -> str:
    # YAML timestamps may arrive as date objects; population strings retain
    # their spelling and are deliberately not normalized to instants.
    if isinstance(value, (date, datetime)):
        value = value.isoformat()
    if isinstance(value, bool):
        if primitive not in {None, "Boolean"}:
            raise ValueError(f"boolean is not a {primitive} scalar")
        payload = ["boolean", value]
    elif isinstance(value, (int, float)):
        if primitive not in {None, "Integer", "Float", "Number"}:
            raise ValueError(f"number is not a {primitive} scalar")
        if isinstance(value, float):
            if not math.isfinite(value) or primitive == "Integer":
                raise ValueError("invalid numeric scalar")
            numerator, denominator = value.as_integer_ratio()
        else:
            numerator, denominator = value, 1
        payload = ["number", [numerator, denominator]]
    elif isinstance(value, str):
        if primitive not in {None, "String", "Date", "DateTime", "Binary"}:
            raise ValueError(f"string is not a {primitive} scalar")
        payload = ["string", value]
    else:
        raise TypeError(f"not a supported scalar: {type(value).__name__}")
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _ordered_heads(facts: dict[str, dict[str, Any]]) -> list[str]:
    heads = {name for name, fact in facts.items() if isinstance(fact.get("derivation_rule"), dict)}
    dependencies = {
        name: {
            atom["fact_type"]
            for atom in facts[name]["derivation_rule"]["body"]
            + facts[name]["derivation_rule"].get("negate", [])
        } & heads
        for name in heads
    }
    ordered = []
    while dependencies:
        ready = sorted(name for name, needs in dependencies.items() if not needs)
        if not ready:
            raise ValueError("structured derivations must be acyclic")
        ordered.extend(ready)
        for name in ready:
            del dependencies[name]
        for needs in dependencies.values():
            needs.difference_update(ready)
    return ordered


def _atom_fragment(
    atom: dict[str, Any], variables: dict[str, Any], facts: dict[str, dict[str, Any]],
    primitives: dict[str, dict[str, str | None]], relations: dict[str, Any],
) -> Any:
    from relationalai.semantics import String

    name = atom["fact_type"]
    terms = []
    for role in facts[name]["roles"]:
        role_name = role["role_name"]
        if role_name not in atom["bind"]:
            terms.append(String.ref())
            continue
        term = atom["bind"][role_name]
        if isinstance(term, str) and term.startswith("$") and len(term) > 1:
            if term not in variables:
                variables[term] = String.ref()
            terms.append(variables[term])
        else:
            terms.append(_identity(term, primitives[name][role_name]))
    return relations[name](*terms)


def derive(
    model: dict[str, Any], population: dict[str, Any]
) -> dict[str, tuple[tuple[str, ...], ...]]:
    from relationalai.config import Config
    from relationalai.semantics import Model, String, not_
    from relationalai.semantics.frontend.base import Field

    facts = {fact["id"]: fact for fact in model["fact_types"]}
    objects = {obj["id"]: obj for obj in model["object_types"]}
    ordered = _ordered_heads(facts)
    derived = set(ordered)
    primitives = {
        name: {role["role_name"]: _primitive(role["object_type"], objects) for role in fact["roles"]}
        for name, fact in facts.items()
    }
    engine = Model(
        "gnd_derivation_oracle",
        config=Config(
            connections={"local": {"type": "duckdb", "path": ":memory:"}},
            default_connection="local",
            deployment={"schema": "gnd_derivation", "auto_deploy": True},
        ),
    )
    relations = {
        name: engine.Relationship(
            fields=[Field(f"role_{index}", String) for index, _ in enumerate(fact["roles"])],
            short_name=f"fact_{ordinal}",
        )
        for ordinal, (name, fact) in enumerate(facts.items())
    }
    for name, fact in facts.items():
        if name in derived:
            continue  # supplied derived/semiderived rows are claims, never input
        rows = (population.get("facts") or {}).get(name, []) or []
        atoms = [
            relations[name](
                *[
                    _identity(row[role["role_name"]], primitives[name][role["role_name"]])
                    for role in fact["roles"]
                ]
            )
            for row in rows
        ]
        if atoms:
            engine.define(*atoms)

    for name in ordered:
        rule = facts[name]["derivation_rule"]
        variables: dict[str, Any] = {}
        positive = [
            _atom_fragment(atom, variables, facts, primitives, relations) for atom in rule["body"]
        ]
        negative = [
            not_(_atom_fragment(atom, variables, facts, primitives, relations))
            for atom in rule.get("negate", [])
        ]
        head = [variables[rule["head"][role["role_name"]]] for role in facts[name]["roles"]]
        engine.where(*positive, *negative).define(relations[name](*head))

    extensions = {}
    for name in ordered:
        columns = [String.ref() for _ in facts[name]["roles"]]
        frame = engine.where(relations[name](*columns)).select(*columns).to_df()
        rows = {tuple(row) for row in frame.itertuples(index=False, name=None)}
        extensions[name] = tuple(sorted(rows))
    return extensions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", type=Path)
    parser.add_argument("population", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    installed_version = version("relationalai")
    if installed_version != "1.30.1":
        raise RuntimeError(f"unexpected relationalai version: {installed_version}")
    model = _load_yaml(args.model)
    if any(
        isinstance(fact.get("derivation_rule"), dict)
        and "clauses" in fact["derivation_rule"]
        for fact in model.get("fact_types", [])
    ):
        print(
            "pyrel-recursive-clauses-unsupported: the isolated PyRel v1 oracle "
            "has no native recursive-clause lowering",
            file=sys.stderr,
        )
        return 2
    # The parent supplies scratch explicitly. Direct script calls are isolated too.
    with TemporaryDirectory(prefix="pyrel-derivation-") as scratch:
        os.environ.setdefault("RAI_BUILD_DIR", scratch)
        extensions = derive(model, _load_yaml(args.population))
        document = {
            "schema_version": 1,
            "backend": "pyrel",
            "version": installed_version,
            "extensions": extensions,
        }
        args.out.write_text(
            json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
