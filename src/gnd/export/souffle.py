"""Deterministic offline lowering to Souffle's bounded relational fragment."""

import hashlib
import json
from dataclasses import replace
from datetime import date

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from gnd import input_policy as _rf7_input
from gnd.model import (
    ModelLoadError,
    ModelValidationError,
    _iter_constraints,
    iter_derivation_clauses,
)
from gnd.population import PopulationLoadError
from gnd.witness import io as witness_io
from gnd.witness.types import DEFAULT_LIMITS as WITNESS_LIMITS

from .souffle_types import DEFAULT_LIMITS, ExportResult, checked_limits, refused

INPUT_ERRORS = (
    ValueError,
    TypeError,
    KeyError,
    OSError,
    UnicodeError,
    RecursionError,
    ModelLoadError,
    ModelValidationError,
    PopulationLoadError,
    YAMLError,
)


class Unsupported(ValueError):
    """Valid input outside the selected fragment."""


def wire(document):
    return (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def parse(raw, fmt, limits=DEFAULT_LIMITS):
    if type(raw) is not bytes or len(raw) > limits.document_bytes or fmt not in {"json", "yaml"}:
        raise ValueError("document boundary")
    wl = replace(
        WITNESS_LIMITS,
        bytes=limits.document_bytes,
        container_depth=limits.container_depth,
        scalar_bytes=limits.scalar_bytes,
        numeric_digits=limits.numeric_digits,
    )
    if fmt == "json":
        return witness_io.parse_wire(raw, limits=wl)
    _rf7_input.guard_yaml(raw, max_bytes=limits.document_bytes, max_depth=limits.container_depth)
    y = YAML(typ="safe")
    y.allow_duplicate_keys = False
    doc = y.load(raw)
    witness_io.validate_witness_structure(doc, limits=wl)
    return doc


def token(value, primitive):
    if primitive == "String" and type(value) is str:
        return "s:" + value.encode().hex()
    if primitive == "Boolean" and type(value) is bool:
        return "b:" + str(int(value))
    if primitive in {"Integer", "Number"} and type(value) is int:
        return f"n:{value}:1"
    if (
        primitive == "Date"
        and type(value) is str
        and date.fromisoformat(value).isoformat() == value
    ):
        return "d:" + value
    if primitive == "Duration" and type(value) is int and value >= 0:
        return "u:" + str(value)
    raise Unsupported("scalar outside fragment")


def admit(model_bytes, candidate_bytes, model_format, candidate_format, reference_inputs, limits):
    md, pd = (
        parse(model_bytes, model_format, limits),
        parse(candidate_bytes, candidate_format, limits),
    )
    if type(md) is not dict or type(md.get("version", 1)) is not int:
        raise ValueError("model version")
    wl = replace(
        WITNESS_LIMITS,
        bytes=limits.document_bytes,
        container_depth=limits.container_depth,
        scalar_bytes=limits.scalar_bytes,
        numeric_digits=limits.numeric_digits,
    )
    model, candidate, refs = witness_io.intake(md, pd, reference_inputs, limits=wl)
    rows, origins = {}, []
    roles = witness_io.roster(model)
    owners = {f: d["id"] for d in model.reference_populations for f in d["fact_types"]}
    for i, ft in enumerate(model.fact_types):
        fid = ft["id"]
        pop = refs[owners[fid]] if fid in owners else candidate
        values = pop.facts.get(fid, [])
        rows[fid] = values
        if ft.get("derivation"):
            if values:
                raise Unsupported("derived input assertions")
        elif fid not in pop.covers:
            raise Unsupported("partial base coverage")
        for n, row in enumerate(values):
            origins.append(
                {
                    "input": f"i{i}",
                    "source_ordinal": n,
                    "fact_type": fid,
                    "origin": {
                        "kind": "reference" if fid in owners else "candidate",
                        "reference_id": owners.get(fid),
                        "fact_index": n,
                    },
                }
            )
    clauses = [
        (f, list(iter_derivation_clauses(f.get("derivation_rule"))))
        for f in model.fact_types
        if f.get("derivation")
    ]
    sites = sum(
        len(c.get("body", [])) + len(c.get("negate", [])) + len(c.get("where", []))
        for _, cs in clauses
        for c in cs
    )
    nc = sum(len(cs) for _, cs in clauses)
    nr = sum(map(len, rows.values()))
    cells = sum(len(r) for rs in rows.values() for r in rs)
    charge = (
        len(model.fact_types)
        + sum(map(len, roles.values()))
        + nc
        + sites
        + sum(len(c["head"]) for _, cs in clauses for c in cs)
        + nr
        + cells
    )
    measured = {
        "fact_types": len(model.fact_types),
        "roles": max(map(len, roles.values()), default=0),
        "clauses": nc,
        "atom_sites": sites,
        "input_rows": nr,
        "encoded_cells": cells,
    }
    if any(v > getattr(limits, k) for k, v in measured.items()):
        raise ValueError("shape ceiling")
    for fid, rs in rows.items():
        for row in rs:
            for role, primitive in roles[fid]:
                token(row[role], primitive)
    for f, cs in clauses:
        if (
            not isinstance(f.get("derivation_rule"), dict)
            or not cs
            or f.get("derivation") == "semiderived"
        ):
            raise Unsupported("opaque derivation")
        for c in cs:
            a = c.get("aggregate")
            if c.get("where") and not a:
                raise Unsupported("scalar filters")
            if a and (
                a.get("fn") != "count"
                or c.get("negate")
                or any(
                    w.get("left") != a["as"]
                    or type(w.get("right")) is not int
                    or w.get("operator") not in {"=", "!=", "<", "<=", ">", ">="}
                    for w in c.get("where", [])
                )
            ):
                raise Unsupported("count fragment")
            for fid, terms in [(f["id"], c["head"])] + [
                (a["fact_type"], a["bind"]) for a in c.get("body", []) + c.get("negate", [])
            ]:
                for role, primitive in roles[fid]:
                    v = terms[role]
                    if isinstance(v, (dict, list)):
                        raise Unsupported("expression")
                    if not (type(v) is str and v.startswith("$")):
                        token(v, primitive)
    if any(
        p not in {"String", "Boolean", "Integer", "Number", "Date", "Duration"}
        for rs in roles.values()
        for _, p in rs
    ):
        raise Unsupported("primitive")
    return model, candidate, refs, rows, origins, roles, charge, measured


def render_souffle(
    model_bytes,
    candidate_bytes,
    *,
    model_format="yaml",
    candidate_format="json",
    reference_inputs=(),
    limits=DEFAULT_LIMITS,
):
    try:
        checked_limits(limits)
        model, candidate, _refs, rows, origins, roles, charge, counts = admit(
            model_bytes, candidate_bytes, model_format, candidate_format, reference_inputs, limits
        )
        if charge > limits.emission_visits:
            return refused(4, "work-limit")
        relations, rules, program, files = [], [], [], {}
        names = {f["id"]: f"r{i}" for i, f in enumerate(model.fact_types)}

        def rule_record(symbol, native, kind, fid, index):
            rules.append(
                {
                    "symbol": symbol,
                    "native_rule": native,
                    "kind": kind,
                    "fact_type": fid,
                    "clause_index": index,
                }
            )

        for i, ft in enumerate(model.fact_types):
            fid, derived = ft["id"], bool(ft.get("derivation"))
            rs = [
                {"name": r["role_name"], "object_type": r["object_type"], "primitive": p}
                for r, (_, p) in zip(ft["roles"], roles[fid], strict=True)
            ]
            relations.append(
                {
                    "fact_type": fid,
                    "symbol": f"r{i}",
                    "input": None if derived else f"i{i}",
                    "roles": rs,
                    "derived": derived,
                }
            )
            decl = ", ".join(f"c{n}:symbol" for n in range(len(rs)))
            program.append(f".decl r{i}({decl})")
            if not derived:
                program += [
                    f".decl i{i}({decl}, source_ordinal:unsigned)",
                    f'.input i{i}(IO=file, filename="i{i}.facts")',
                ]
                vs = ", ".join(f"C{n}" for n in range(len(rs)))
                program.append(f"r{i}({vs}) :- i{i}({vs}, _).")
                rule_record(f"r{i}", 1, "input", fid, None)
                files[f"facts/i{i}.facts"] = "".join(
                    "\t".join([token(row[r], p) for r, p in roles[fid]] + [str(n)]) + "\n"
                    for n, row in enumerate(rows[fid])
                ).encode()
        aux = 0
        for ft in model.fact_types:
            if not ft.get("derivation"):
                continue
            fid, symbol = ft["id"], names[ft["id"]]
            for index, clause in enumerate(iter_derivation_clauses(ft["derivation_rule"])):
                variables = {}

                def term(t, p, variables=variables):
                    if type(t) is str and t.startswith("$"):
                        return variables.setdefault(t, f"V{len(variables)}")
                    return json.dumps(token(t, p))

                body = []
                for kind in ("body", "negate"):
                    for atom in clause.get(kind, []):
                        args = ", ".join(
                            term(atom["bind"][r], p) for r, p in roles[atom["fact_type"]]
                        )
                        body.append(
                            ("!" if kind == "negate" else "")
                            + names[atom["fact_type"]]
                            + f"({args})"
                        )
                a = clause.get("aggregate")
                if not a:
                    head = ", ".join(term(clause["head"][r], p) for r, p in roles[fid])
                    program.append(f"{symbol}({head}) :- {', '.join(body)}.")
                    rule_record(symbol, index + 1, "derivation", fid, index)
                else:
                    groups = sorted(
                        {
                            v
                            for v in clause["head"].values()
                            if type(v) is str and v.startswith("$") and v != a["as"]
                        }
                    )
                    keys = groups + a["over"] + [a["of"]]
                    c, counted = f"c{aux}", f"a{aux}"
                    aux += 1
                    program += [
                        f".decl {c}(" + ", ".join(f"v{n}:symbol" for n in range(len(keys))) + ")",
                        f"{c}({', '.join(variables[v] for v in keys)}) :- {', '.join(body)}.",
                        f".decl {counted}("
                        + ", ".join(
                            [*(f"g{n}:symbol" for n in range(len(groups))), "result:number"]
                        )
                        + ")",
                    ]
                    gs = [f"G{n}" for n in range(len(groups))]
                    anchor = gs + ["_"] * (len(keys) - len(groups))
                    inner = gs + [f"O{n}" for n in range(len(keys) - len(groups))]
                    program.append(
                        f"{counted}({', '.join(gs + ['Result'])}) :- {c}({', '.join(anchor)}), Result = count : {c}({', '.join(inner)})."
                    )
                    head = [
                        'cat("n:", cat(to_string(Result), ":1"))'
                        if clause["head"][r] == a["as"]
                        else gs[groups.index(clause["head"][r])]
                        if clause["head"][r] in groups
                        else term(clause["head"][r], p)
                        for r, p in roles[fid]
                    ]
                    filters = [
                        f"Result {w['operator']} {w['right']}" for w in clause.get("where", [])
                    ]
                    program.append(
                        f"{symbol}({', '.join(head)}) :- "
                        + ", ".join([f"{counted}({', '.join(gs + ['Result'])})", *filters])
                        + "."
                    )
                    for s, k in [
                        (c, "count-contribution"),
                        (counted, "count-aggregate"),
                        (symbol, "count-result"),
                    ]:
                        rule_record(s, index + 1 if s == symbol else 1, k, fid, index)
            program.append(f'.output {symbol}(IO=file, filename="{symbol}.csv")')
        files.update(
            {
                "program.dl": ("\n".join(program) + "\n").encode(),
                "symbols.json": wire(
                    {
                        "version": 1,
                        "encoding": "souffle-token-v1",
                        "relations": relations,
                        "rules": rules,
                    }
                ),
                "origins.json": wire({"version": 1, "rows": origins}),
                "inputs/model.json": model_bytes,
                "inputs/candidate.json": candidate_bytes,
            }
        )
        for n, (rid, raw) in enumerate(sorted(reference_inputs)):
            files[f"inputs/reference-{n}.json"] = raw
        binding = witness_io.identity(model, candidate, reference_inputs)
        binding.update(
            model_raw_sha256=digest(model_bytes), candidate_raw_sha256=digest(candidate_bytes)
        )
        manifest = {
            "version": 1,
            "kind": "souffle-derivation-program",
            "support_profile": "souffle-relational-v1",
            "encoding": "souffle-token-v1",
            "assurance": "none",
            "binding": binding,
            "input_formats": {"model": model_format, "candidate": candidate_format},
            "excluded": {
                "constraint_evaluation": "all",
                "constraint_ids": [
                    c.get("id") or path
                    for path, c in _iter_constraints(model.model_dump(mode="json"))
                ],
                "operations": "all",
            },
            "files": [
                {"path": k, "bytes": len(v), "sha256": digest(v)} for k, v in sorted(files.items())
            ],
            "limits": vars(limits),
        }
        files["manifest.json"] = wire(manifest)
        if sum(map(len, files.values())) > limits.bundle_bytes:
            return refused(4, "work-limit")
        return ExportResult(
            counts={
                **{k: counts[k] for k in ("fact_types", "clauses", "input_rows", "encoded_cells")},
                "emission_visits": charge,
            },
            files=files,
        )
    except Unsupported:
        return refused(2, "fragment-unsupported")
    except INPUT_ERRORS:
        return refused()
