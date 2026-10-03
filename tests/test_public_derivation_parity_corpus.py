"""Independent local SQL parity and frozen receipt binding guards; no foreign seat execution."""
from __future__ import annotations

import atexit
import gzip
import hashlib
import io
import json
import math
import tempfile
from pathlib import Path
from types import MappingProxyType
from typing import Any

import duckdb
import pytest
from support.digests import sha256_file as _sha256

from gnd.checker import _base_relations, _identity_token, _python_extension_calculator
from gnd.model import ModelValidationError, load_model
from gnd.population import PopulationValidationError, load_population


def _materialize_public_corpus():
    packed = (Path(__file__).parent / "fixtures/public-derivation-parity/closure.json.gz").read_bytes()
    assert len(packed) <= 65536
    assert hashlib.sha256(packed).hexdigest() == '131a4349e636bb2401044343d122ef0a3884ebce877b4eaaaaef4df2ad77418b'
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(524289)
    assert len(raw) <= 524288
    assert hashlib.sha256(raw).hexdigest() == 'd96cd93e94daafd6362effd03ef344d4c1d05e17b4e2be0684c55a3dba4987dc'
    documents = json.loads(raw)
    assert set(documents) == {'cases/wire-v3-string-only/model.orm.yaml', 'cases/oracle-evaluator-bug-red/population.yaml', 'cases/wire-session-v4-refused/population.yaml', 'cases/wire-session-v4-refused/model.orm.yaml', 'cases/wire-v4-requires-derivations/population.yaml', 'cases/band-4-over-2/model.orm.yaml', 'cases/wire-address-distinct/model.orm.yaml', 'cases/obligation-derived-missing/model.orm.yaml', 'cases/obligation-semiderived-missing/population.yaml', 'cases/eval-disconnected-product/model.orm.yaml', 'cases/constraint-semiderived-computed-view/population.yaml', 'cases/constraint-original-output-order/model.orm.yaml', 'cases/oracle-oracle-defect-recorded/population.yaml', 'cases/eval-grounded-pseudo-component/population.yaml', 'cases/eval-positive-single/model.orm.yaml', 'cases/wire-v4-requires-derivations/model.orm.yaml', 'cases/obligation-derived-exact/model.orm.yaml', 'cases/eval-negated-present/population.yaml', 'cases/eval-dollar-variable-normalized/population.yaml', 'cases/oracle-unknown-mismatch-red/model.orm.yaml', 'cases/oracle-independent-codec-goldens/population.yaml', 'expected.json', 'cases/eval-unresolved-primitive-metadata/population.yaml', 'cases/constraint-mandatory-uncovered-vacuous-plus-band4/model.orm.yaml', 'cases/eval-boolean-number-separated/model.orm.yaml', 'cases/wire-v3-nonstructured/population.yaml', 'cases/wire-invalid-model-v3/model.orm.yaml', 'cases/eval-boolean-number-separated/population.yaml', 'cases/oracle-production-codec-mutation-red/model.orm.yaml', 'cases/eval-bare-dollar-literal/population.yaml', 'cases/oracle-production-mutation-red/model.orm.yaml', 'cases/oracle-production-codec-mutation-red/population.yaml', 'cases/wire-v3-string-only/population.yaml', 'cases/witness-hash-seed-stable/population.yaml', 'cases/constraint-constraint-view-isolated/model.orm.yaml', 'cases/constraint-derived-empty-claim-vacuous/model.orm.yaml', 'cases/eval-bare-dollar-literal/model.orm.yaml', 'cases/constraint-all-extensions-before-constraints/model.orm.yaml', 'cases/obligation-semiderived-surplus/model.orm.yaml', 'cases/obligation-derived-surplus/model.orm.yaml', 'cases/oracle-souffle-present-simulated/population.yaml', 'cases/wire-address-distinct/population.yaml', 'cases/obligation-unlisted-semiderived-empty-computed/model.orm.yaml', 'cases/eval-derived-poison-ignored/population.yaml', 'cases/obligation-semiderived-missing/model.orm.yaml', 'cases/witness-hash-seed-stable/model.orm.yaml', 'cases/wire-v4-structured-check/model.orm.yaml', 'cases/constraint-derived-claim-view/population.yaml', 'cases/eval-projection-dedup/model.orm.yaml', 'cases/constraint-duplicate-final-walk-red/population.yaml', 'cases/constraint-two-families/model.orm.yaml', 'cases/wire-invalid-model-v3/population.yaml', 'cases/constraint-evaluator-view-isolated/population.yaml', 'cases/wire-v3-nested-model-dump-unchanged/population.yaml', 'cases/band-1-over-4/model.orm.yaml', 'cases/oracle-production-mutation-red/population.yaml', 'cases/obligation-unlisted-derived-nonempty-computed/model.orm.yaml', 'cases/obligation-opaque-string-only-v3/model.orm.yaml', 'cases/wire-v4-check-internal/model.orm.yaml', 'cases/eval-positive-chain-small-head/model.orm.yaml', 'cases/wire-text-json-parity/population.yaml', 'cases/eval-grounded-pseudo-component/model.orm.yaml', 'cases/constraint-all-extensions-before-constraints/population.yaml', 'cases/constraint-semiderived-computed-nonvacuous/model.orm.yaml', 'cases/wire-address-coherent/model.orm.yaml', 'cases/obligation-opaque-mixed-unlisted/population.yaml', 'cases/obligation-opaque-mixed-listed/population.yaml', 'cases/band-2/model.orm.yaml', 'cases/obligation-derived-missing/population.yaml', 'cases/band-1-over-4/population.yaml', 'cases/wire-v4-verify-internal/population.yaml', 'cases/cost-quadratic-mutation-red/population.yaml', 'cases/wire-v4-structured-validate/population.yaml', 'cases/wire-v4-check-internal/population.yaml', 'cases/obligation-unlisted-semiderived-empty-computed/population.yaml', 'cases/wire-v4-verify-internal/model.orm.yaml', 'cases/wire-v3-nonstructured/model.orm.yaml', 'cases/obligation-semiderived-exact/model.orm.yaml', 'cases/eval-unresolved-primitive-metadata/model.orm.yaml', 'cases/constraint-mandatory-uncovered-vacuous-plus-band4/population.yaml', 'cases/eval-integer-float-merged/population.yaml', 'cases/oracle-independent-codec-goldens/model.orm.yaml', 'cases/cost-quadratic-mutation-red/model.orm.yaml', 'cases/oracle-oracle-defect-recorded/model.orm.yaml', 'cases/eval-negated-absent/population.yaml', 'cases/cost-chain-counted/model.orm.yaml', 'cases/eval-positive-chain-small-head/population.yaml', 'cases/constraint-original-output-order/population.yaml', 'cases/eval-projection-dedup/population.yaml', 'cases/wire-v3-model-dump-unchanged/model.orm.yaml', 'cases/eval-negated-absent/model.orm.yaml', 'cases/eval-semiderived-surplus-upper-ignored/population.yaml', 'cases/obligation-derived-both-differences/population.yaml', 'cases/cost-disconnected-counted/population.yaml', 'cases/witness-missing-canonical/population.yaml', 'cases/oracle-unknown-mismatch-red/population.yaml', 'cases/wire-v4-validate-internal/model.orm.yaml', 'cases/constraint-unlisted-derived-claim-inert/model.orm.yaml', 'cases/wire-v4-population-refusal/model.orm.yaml', 'cases/wire-address-coherent/population.yaml', 'cases/obligation-unlisted-semiderived-nonempty-computed/population.yaml', 'cases/oracle-souffle-absent-simulated-visible/population.yaml', 'cases/band-4-over-2/population.yaml', 'cases/oracle-cross-backend-disposition-red/population.yaml', 'cases/band-0/population.yaml', 'cases/oracle-duckdb-match/model.orm.yaml', 'cases/eval-derived-poison-ignored/model.orm.yaml', 'cases/oracle-spec-gap-red/model.orm.yaml', 'cases/cost-disconnected-counted/model.orm.yaml', 'cases/eval-positive-single/population.yaml', 'cases/wire-v4-population-refusal/population.yaml', 'cases/wire-v4-validate-internal/population.yaml', 'cases/wire-v3-nested-model-dump-unchanged/model.orm.yaml', 'cases/eval-negated-empty-relation/model.orm.yaml', 'cases/eval-all-eight-primitives/model.orm.yaml', 'cases/eval-dollar-variable-normalized/model.orm.yaml', 'cases/witness-offending-canonical/model.orm.yaml', 'cases/obligation-unlisted-derived-empty-computed/model.orm.yaml', 'cases/eval-integer-float-merged/model.orm.yaml', 'cases/constraint-duplicate-final-walk-red/model.orm.yaml', 'cases/band-1/model.orm.yaml', 'cases/obligation-derived-both-differences/model.orm.yaml', 'cases/obligation-opaque-string-only-v3/population.yaml', 'cases/wire-v4-structured-check/population.yaml', 'cases/obligation-semiderived-surplus/population.yaml', 'cases/witness-offending-canonical/population.yaml', 'cases/obligation-derived-surplus/population.yaml', 'cases/constraint-constraint-view-isolated/population.yaml', 'cases/eval-depth3-dependency-order/model.orm.yaml', 'cases/obligation-unlisted-derived-empty-computed/population.yaml', 'cases/obligation-opaque-mixed-unlisted/model.orm.yaml', 'cases/eval-depth3-dependency-order/population.yaml', 'cases/oracle-encoding-bug-recorded/population.yaml', 'cases/oracle-encoding-bug-recorded/model.orm.yaml', 'cases/wire-v3-rejects-derivations/model.orm.yaml', 'cases/band-0/model.orm.yaml', 'cases/constraint-two-families/population.yaml', 'cases/band-70-not-verdict/population.yaml', 'cases/obligation-unlisted-derived-nonempty-computed/population.yaml', 'cases/constraint-one-final-walk/population.yaml', 'cases/oracle-evaluator-bug-red/model.orm.yaml', 'cases/eval-disconnected-product/population.yaml', 'cases/oracle-spec-gap-red/population.yaml', 'cases/obligation-semiderived-exact/population.yaml', 'cases/oracle-stale-disposition-red/population.yaml', 'cases/band-70-not-verdict/model.orm.yaml', 'cases/eval-negated-empty-relation/population.yaml', 'cases/oracle-souffle-present-simulated/model.orm.yaml', 'cases/constraint-derived-claim-view/model.orm.yaml', 'cases/cost-chain-counted/population.yaml', 'cases/witness-missing-canonical/model.orm.yaml', 'cases/wire-v3-rejects-derivations/population.yaml', 'cases/eval-all-eight-primitives/population.yaml', 'cases/wire-text-json-parity/model.orm.yaml', 'oracle-receipt.json', 'cases/wire-v4-structured-validate/model.orm.yaml', 'cases/constraint-unlisted-derived-claim-inert/population.yaml', 'cases/constraint-derived-empty-claim-vacuous/population.yaml', 'cases/constraint-semiderived-computed-nonvacuous/population.yaml', 'cases/obligation-unlisted-semiderived-nonempty-computed/model.orm.yaml', 'cases/oracle-stale-disposition-red/model.orm.yaml', 'cases/obligation-derived-exact/population.yaml', 'cases/band-1/population.yaml', 'cases/constraint-semiderived-computed-view/model.orm.yaml', 'cases/constraint-one-final-walk/model.orm.yaml', 'cases/oracle-souffle-absent-simulated-visible/model.orm.yaml', 'cases/constraint-evaluator-view-isolated/model.orm.yaml', 'cases/eval-semiderived-surplus-upper-ignored/model.orm.yaml', 'cases/oracle-cross-backend-disposition-red/model.orm.yaml', 'cases/obligation-opaque-mixed-listed/model.orm.yaml', 'cases/band-2/population.yaml', 'cases/eval-negated-present/model.orm.yaml', 'cases/wire-v3-model-dump-unchanged/population.yaml', 'cases/oracle-duckdb-match/population.yaml'}
    temporary = tempfile.TemporaryDirectory(prefix="gnd-public-derivation-parity-")
    root = Path(temporary.name).resolve()
    for name, text in documents.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return temporary, root

_TEMPORARY, CORPUS = _materialize_public_corpus()
atexit.register(_TEMPORARY.cleanup)
ANSWER_KEY = json.loads((CORPUS / "expected.json").read_text(encoding="utf-8"))
RECEIPT = CORPUS / "oracle-receipt.json"
CODEC_VERSION = "gnd-identity-json/1"
DISPOSITIONS = {"evaluator-bug", "encoding-bug", "spec-gap", "oracle-defect"}
BLOCKING_DISPOSITIONS = {"evaluator-bug", "spec-gap"}
PYREL_VERSION = "1.30.1"

def _quote(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'

def _oracle_variable(term: Any) -> str | None:
    if isinstance(term, str) and term.startswith("$") and len(term) > 1:
        return term[1:]
    return None

def _primitive_index(
    model: Any,
) -> tuple[dict[str, str | None], dict[str, list[tuple[str, str | None]]]]:
    primitives = {
        str(object_type.get("id")): object_type.get("primitive")
        for object_type in model.object_types
    }
    roles = {
        str(fact_type.get("id")): [
            (str(role.get("role_name")), primitives.get(str(role.get("object_type"))))
            for role in fact_type.get("roles") or []
        ]
        for fact_type in model.fact_types
    }
    return primitives, roles

def _oracle_identity_token(value: Any, primitive: str | None) -> str:
    """Independent implementation of the normative typed scalar table."""
    if primitive == "Boolean":
        if not isinstance(value, bool):
            raise TypeError("Boolean requires bool")
        payload: list[Any] = ["boolean", value]
    elif primitive in {"Integer", "Float", "Number"}:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{primitive} requires a number")
        if isinstance(value, float):
            if not math.isfinite(value):
                raise ValueError("non-finite number")
            numerator, denominator = value.as_integer_ratio()
        else:
            numerator, denominator = value, 1
        common = math.gcd(numerator, denominator)
        numerator //= common
        denominator //= common
        if denominator < 0:
            numerator, denominator = -numerator, -denominator
        payload = ["number", [numerator, denominator]]
    elif primitive in {"String", "Date", "DateTime", "Binary", None}:
        if not isinstance(value, str):
            if primitive is None and isinstance(value, bool):
                payload = ["boolean", value]
            elif primitive is None and isinstance(value, (int, float)):
                if isinstance(value, float) and not math.isfinite(value):
                    raise ValueError("non-finite number")
                numerator, denominator = value.as_integer_ratio()
                payload = ["number", [numerator, denominator]]
            else:
                raise TypeError(f"{primitive} requires a string")
        else:
            payload = ["string", value]
    else:
        raise ValueError(f"unknown primitive {primitive}")
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

def _oracle_clauses(rule: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    """Independent raw-YAML normalization; never import the product iterator."""
    if "clauses" not in rule:
        return (rule,)
    shared = {key: value for key, value in rule.items() if key != "clauses"}
    return tuple({**shared, **clause} for clause in rule["clauses"])

def _oracle_strata(model: Any) -> list[tuple[str, ...]]:
    structured = {
        str(fact_type["id"]): fact_type
        for fact_type in model.fact_types
        if isinstance(fact_type.get("derivation_rule"), dict)
    }
    dependencies = {
        head: {
            str(atom["fact_type"])
            for clause in _oracle_clauses(fact_type["derivation_rule"])
            for key in ("body", "negate")
            for atom in clause.get(key) or []
        } & structured.keys()
        for head, fact_type in structured.items()
    }
    # Kosaraju is deliberately independent of gnd.model.derivation_strata.
    seen: set[str] = set()
    finished: list[str] = []

    def visit(node: str) -> None:
        seen.add(node)
        for child in sorted(dependencies[node]):
            if child not in seen:
                visit(child)
        finished.append(node)

    for node in sorted(structured):
        if node not in seen:
            visit(node)
    reverse: dict[str, set[str]] = {node: set() for node in structured}
    for node, children in dependencies.items():
        for child in children:
            reverse[child].add(node)
    seen.clear()
    components = []
    for root in reversed(finished):
        if root in seen:
            continue
        pending = [root]
        seen.add(root)
        members = []
        while pending:
            node = pending.pop()
            members.append(node)
            for parent in reverse[node] - seen:
                seen.add(parent)
                pending.append(parent)
        components.append(tuple(sorted(members)))
    component_of = {head: i for i, component in enumerate(components) for head in component}
    remaining = set(range(len(components)))
    prerequisites = {
        i: {component_of[child] for head in component for child in dependencies[head]}
        - {i}
        for i, component in enumerate(components)
    }
    ordered = []
    while remaining:
        ready = sorted(
            (i for i in remaining if not prerequisites[i] & remaining),
            key=lambda i: components[i],
        )
        if not ready:
            raise AssertionError("condensed oracle graph is cyclic")
        ordered.extend(components[i] for i in ready)
        remaining.difference_update(ready)
    return ordered

def _oracle_order(model: Any) -> list[str]:
    return [head for component in _oracle_strata(model) for head in component]

def _duckdb_extensions(model: Any, population: Any) -> dict[str, tuple[tuple[str, ...], ...]]:
    if any(
        "clauses" in fact_type.get("derivation_rule", {})
        for fact_type in model.fact_types
        if isinstance(fact_type.get("derivation_rule"), dict)
    ) or any(
        len(component) > 1 for component in _oracle_strata(model)
    ):
        return _duckdb_scc_extensions(model, population)
    _primitives, roles = _primitive_index(model)
    fact_types = {str(fact_type.get("id")): fact_type for fact_type in model.fact_types}
    table = {fact_type_id: f"r{index}" for index, fact_type_id in enumerate(fact_types)}
    connection = duckdb.connect(":memory:")

    def install(fact_type_id: str, rows: list[tuple[str, ...]]) -> None:
        columns = roles[fact_type_id]
        definition = ", ".join(
            [*(f"{_quote(name)} VARCHAR" for name, _ in columns), '"__source_ordinal" BIGINT']
        )
        connection.execute(f"DROP TABLE IF EXISTS {_quote(table[fact_type_id])}")
        connection.execute(f"CREATE TABLE {_quote(table[fact_type_id])} ({definition})")
        if rows:
            placeholders = ",".join("?" for _column in range(len(columns) + 1))
            connection.executemany(
                f"INSERT INTO {_quote(table[fact_type_id])} VALUES ({placeholders})",
                [(*row, ordinal) for ordinal, row in enumerate(rows)],
            )

    for fact_type_id, fact_type in fact_types.items():
        source_rows = (
            []
            if isinstance(fact_type.get("derivation_rule"), dict)
            else population.facts.get(fact_type_id, [])
        )
        install(
            fact_type_id,
            [
                tuple(
                    _oracle_identity_token(row[role_name], primitive)
                    for role_name, primitive in roles[fact_type_id]
                )
                for row in source_rows
            ],
        )

    extensions: dict[str, tuple[tuple[str, ...], ...]] = {}
    for head_id in _oracle_order(model):
        rule = fact_types[head_id]["derivation_rule"]
        aliases = [f"a{index}" for index, _atom in enumerate(rule["body"])]
        from_sql = " CROSS JOIN ".join(
            f"{_quote(table[str(atom['fact_type'])])} AS {_quote(alias)}"
            for alias, atom in zip(aliases, rule["body"], strict=True)
        )
        variables: dict[str, str] = {}
        predicates: list[str] = []
        parameters: list[str] = []
        for alias, atom in zip(aliases, rule["body"], strict=True):
            atom_id = str(atom["fact_type"])
            primitive_by_role = dict(roles[atom_id])
            for role_name, term in atom["bind"].items():
                expression = f"{_quote(alias)}.{_quote(str(role_name))}"
                variable = _oracle_variable(term)
                if variable is None:
                    predicates.append(f"{expression} = ?")
                    parameters.append(
                        _oracle_identity_token(term, primitive_by_role[str(role_name)])
                    )
                elif variable in variables:
                    predicates.append(f"{expression} = {variables[variable]}")
                else:
                    variables[variable] = expression
        for neg_index, atom in enumerate(rule.get("negate") or []):
            neg_alias = f"n{neg_index}"
            atom_id = str(atom["fact_type"])
            primitive_by_role = dict(roles[atom_id])
            clauses: list[str] = []
            for role_name, term in atom["bind"].items():
                expression = f"{_quote(neg_alias)}.{_quote(str(role_name))}"
                variable = _oracle_variable(term)
                if variable is None:
                    clauses.append(f"{expression} = ?")
                    parameters.append(
                        _oracle_identity_token(term, primitive_by_role[str(role_name)])
                    )
                else:
                    clauses.append(f"{expression} = {variables[variable]}")
            predicates.append(
                "NOT EXISTS (SELECT 1 FROM "
                f"{_quote(table[atom_id])} AS {_quote(neg_alias)} WHERE "
                + " AND ".join(clauses)
                + ")"
            )
        select = []
        for role_name, _primitive in roles[head_id]:
            term = rule["head"][role_name]
            variable = _oracle_variable(term)
            select.append(f"{variables[variable]} AS {_quote(role_name)}")
        query = "SELECT DISTINCT " + ", ".join(select) + " FROM " + from_sql
        if predicates:
            query += " WHERE " + " AND ".join(predicates)
        rows = sorted(
            tuple(str(value) for value in row)
            for row in connection.execute(query, parameters).fetchall()
        )
        extensions[head_id] = tuple(rows)
        install(head_id, rows)
    connection.close()
    return extensions

def _duckdb_scc_extensions(model: Any, population: Any) -> dict[str, tuple[tuple[str, ...], ...]]:
    """Compile all clauses of each SCC to DuckDB's native recursive CTE."""
    _primitives, roles = _primitive_index(model)
    fact_types = {str(row["id"]): row for row in model.fact_types}
    table = {head: f"r{index}" for index, head in enumerate(fact_types)}
    connection = duckdb.connect(":memory:")

    def install(head: str, rows: list[tuple[str, ...]]) -> None:
        columns = roles[head]
        definition = ", ".join(
            [*(f"{_quote(name)} VARCHAR" for name, _ in columns), '"__source_ordinal" BIGINT']
        )
        connection.execute(f"DROP TABLE IF EXISTS {_quote(table[head])}")
        connection.execute(f"CREATE TABLE {_quote(table[head])} ({definition})")
        if rows:
            placeholders = ",".join("?" for _ in range(len(columns) + 1))
            connection.executemany(
                f"INSERT INTO {_quote(table[head])} VALUES ({placeholders})",
                [(*row, index) for index, row in enumerate(rows)],
            )

    for head, fact_type in fact_types.items():
        source_rows = (
            [] if isinstance(fact_type.get("derivation_rule"), dict)
            else population.facts.get(head, [])
        )
        install(head, [
            tuple(_oracle_identity_token(row[role], primitive) for role, primitive in roles[head])
            for row in source_rows
        ])

    extensions: dict[str, tuple[tuple[str, ...], ...]] = {}
    try:
        for component in _oracle_strata(model):
            members = set(component)
            if len(component) == 1 and any(
                "aggregate" in clause
                for clause in _oracle_clauses(fact_types[component[0]]["derivation_rule"])
            ):
                head = component[0]
                rows = sorted({
                    row
                    for clause in _oracle_clauses(fact_types[head]["derivation_rule"])
                    for row in _duckdb_count_clause(connection, table, roles, head, clause)
                })
                extensions[head] = tuple(rows)
                install(head, rows)
                continue
            width = max(len(roles[head]) for head in component)
            fragments: list[tuple[bool, str, list[str]]] = []
            for head in component:
                for clause in _oracle_clauses(fact_types[head]["derivation_rule"]):
                    if "aggregate" in clause or "where" in clause:
                        raise ValueError("DuckDB recursive parity oracle has no exact-term lowering")
                    aliases = [f"a{index}" for index, _ in enumerate(clause["body"])]
                    sources = []
                    variables: dict[str, str] = {}
                    predicates = []
                    parameters: list[str] = []
                    recursive = False
                    for alias, atom in zip(aliases, clause["body"], strict=True):
                        atom_id = str(atom["fact_type"])
                        if atom_id in members:
                            recursive = True
                            sources.append(f"{_quote('scc')} AS {_quote(alias)}")
                            predicates.append(f"{_quote(alias)}.{_quote('tag')} = '{atom_id}'")
                        else:
                            sources.append(f"{_quote(table[atom_id])} AS {_quote(alias)}")
                        primitive_by_role = dict(roles[atom_id])
                        role_index = {name: i for i, (name, _) in enumerate(roles[atom_id])}
                        for role_name, term in atom["bind"].items():
                            column = f"c{role_index[role_name]}" if atom_id in members else role_name
                            expression = f"{_quote(alias)}.{_quote(column)}"
                            variable = _oracle_variable(term)
                            if variable is None:
                                predicates.append(f"{expression} = ?")
                                parameters.append(
                                    _oracle_identity_token(term, primitive_by_role[role_name])
                                )
                            elif variable in variables:
                                predicates.append(f"{expression} = {variables[variable]}")
                            else:
                                variables[variable] = expression
                    for index, atom in enumerate(clause.get("negate") or []):
                        atom_id = str(atom["fact_type"])
                        alias = f"n{index}"
                        tests = []
                        primitive_by_role = dict(roles[atom_id])
                        for role_name, term in atom["bind"].items():
                            expression = f"{_quote(alias)}.{_quote(role_name)}"
                            variable = _oracle_variable(term)
                            if variable is None:
                                tests.append(f"{expression} = ?")
                                parameters.append(
                                    _oracle_identity_token(term, primitive_by_role[role_name])
                                )
                            else:
                                tests.append(f"{expression} = {variables[variable]}")
                        predicates.append(
                            f"NOT EXISTS (SELECT 1 FROM {_quote(table[atom_id])} AS {_quote(alias)} "
                            f"WHERE {' AND '.join(tests)})"
                        )
                    selects = [f"'{head}' AS {_quote('tag')}"]
                    for role_name, primitive in roles[head]:
                        term = clause["head"][role_name]
                        variable = _oracle_variable(term)
                        value = (
                            variables[variable] if variable is not None
                            else "'" + _oracle_identity_token(term, primitive).replace("'", "''") + "'"
                        )
                        selects.append(value)
                    selects.extend("NULL::VARCHAR" for _ in range(width - len(roles[head])))
                    sql = "SELECT " + ", ".join(selects) + " FROM " + " CROSS JOIN ".join(sources)
                    if predicates:
                        sql += " WHERE " + " AND ".join(predicates)
                    fragments.append((recursive, sql, parameters))
            anchor = [row for row in fragments if not row[0]]
            recursive_rows = [row for row in fragments if row[0]]
            if not anchor:
                empty = ", ".join("NULL::VARCHAR" for _ in range(width + 1))
                anchor = [(False, f"SELECT {empty} WHERE FALSE", [])]
            columns = ", ".join([_quote("tag"), *(_quote(f"c{i}") for i in range(width))])
            parts = [*anchor, *recursive_rows]
            anchor_sql = " UNION ".join(sql for _recursive, sql, _params in anchor)
            if len(anchor) > 1:
                anchor_sql = f"SELECT * FROM ({anchor_sql})"
            recursive_sql = " UNION ".join(sql for _recursive, sql, _params in recursive_rows)
            if len(recursive_rows) > 1:
                recursive_sql = f"SELECT * FROM ({recursive_sql})"
            query = (
                f"WITH RECURSIVE {_quote('scc')}({columns}) AS ("
                + anchor_sql
                + (" UNION " + recursive_sql if recursive_rows else "")
                + f") SELECT {columns} FROM {_quote('scc')}"
            )
            params = [param for _recursive, _sql, values in parts for param in values]
            all_rows = connection.execute(query, params).fetchall()
            for head in component:
                rows = sorted({
                    tuple(str(value) for value in row[1 : 1 + len(roles[head])])
                    for row in all_rows if row[0] == head
                })
                extensions[head] = tuple(rows)
                install(head, rows)
    finally:
        connection.close()
    return extensions

def _duckdb_count_clause(
    connection: Any,
    table: dict[str, str],
    roles: dict[str, list[tuple[str, str | None]]],
    head: str,
    clause: dict[str, Any],
) -> list[tuple[str, ...]]:
    """Native distinct-contribution count for one independently projected clause."""
    aggregate = clause.get("aggregate") or {}
    if aggregate.get("fn") != "count":
        raise ValueError("DuckDB aggregate parity supports count in multi-clause rules")
    sources = []
    variables: dict[str, str] = {}
    predicates = []
    params: list[Any] = []
    for index, atom in enumerate(clause["body"]):
        atom_id = str(atom["fact_type"])
        alias = f"a{index}"
        sources.append(f"{_quote(table[atom_id])} AS {_quote(alias)}")
        primitive_by_role = dict(roles[atom_id])
        for role_name, term in atom["bind"].items():
            expression = f"{_quote(alias)}.{_quote(role_name)}"
            variable = _oracle_variable(term)
            if variable is None:
                predicates.append(f"{expression} = ?")
                params.append(_oracle_identity_token(term, primitive_by_role[role_name]))
            elif variable in variables:
                predicates.append(f"{expression} = {variables[variable]}")
            else:
                variables[variable] = expression
    result_name = str(aggregate["as"])[1:]
    groups = sorted({
        variable
        for term in clause["head"].values()
        if (variable := _oracle_variable(term)) is not None and variable != result_name
    })
    contribution = [
        *(f"{variables[name]} AS {_quote('g' + str(index))}" for index, name in enumerate(groups)),
        *(f"{variables[str(name)[1:]]} AS {_quote('o' + str(index))}"
          for index, name in enumerate(aggregate["over"])),
        f"{variables[str(aggregate['of'])[1:]]} AS {_quote('value')}",
    ]
    query = "WITH contribution AS (SELECT DISTINCT " + ", ".join(contribution)
    query += " FROM " + " CROSS JOIN ".join(sources)
    if predicates:
        query += " WHERE " + " AND ".join(predicates)
    query += "), counted AS (SELECT "
    group_columns = [_quote("g" + str(index)) for index in range(len(groups))]
    query += ", ".join([*group_columns, f"COUNT(*) AS {_quote('result')}"])
    query += " FROM contribution"
    if group_columns:
        query += " GROUP BY " + ", ".join(group_columns)
    else:
        query += " HAVING COUNT(*) > 0"
    query += ") SELECT "
    outputs = []
    for role_name, primitive in roles[head]:
        term = clause["head"][role_name]
        variable = _oracle_variable(term)
        if variable == result_name:
            outputs.append("'[\"number\",[' || CAST(result AS VARCHAR) || ',1]]'")
        elif variable is not None:
            outputs.append(_quote("g" + str(groups.index(variable))))
        else:
            outputs.append("'" + _oracle_identity_token(term, primitive).replace("'", "''") + "'")
    query += ", ".join(outputs) + " FROM counted"
    post = []
    for comparison in clause.get("where") or []:
        left = _oracle_variable(comparison["left"])
        if left != result_name or _oracle_variable(comparison["right"]) is not None:
            raise ValueError("DuckDB count parity requires a result-to-literal comparison")
        post.append(f"result {comparison['operator']} ?")
        params.append(comparison["right"])
    if post:
        query += " WHERE " + " AND ".join(post)
    return [tuple(str(value) for value in row) for row in connection.execute(query, params).fetchall()]

def _canonical_digest(
    model: Any,
    token_rows: dict[str, tuple[tuple[str, ...], ...]],
) -> str:
    document = []
    for fact_type in model.fact_types:
        fact_type_id = str(fact_type.get("id"))
        if not isinstance(fact_type.get("derivation_rule"), dict):
            continue
        rows = [[json.loads(token) for token in row] for row in token_rows[fact_type_id]]
        rows.sort(key=lambda row: json.dumps(row, ensure_ascii=False, separators=(",", ":")))
        document.append({"fact_type": fact_type_id, "rows": rows})
    encoded = json.dumps(
        document,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(encoded).hexdigest()

def _production_digest(model: Any, population: Any) -> str:
    calculated = _python_extension_calculator(model, _base_relations(model, population))
    rows = {
        fact_type_id: tuple(
            tuple(_identity_token(value).decode() for value in row) for row in relation.rows
        )
        for fact_type_id, relation in calculated.extensions.items()
    }
    return _canonical_digest(model, rows)

def _parity_matches(model: Any, population: Any) -> bool:
    oracle = _canonical_digest(model, _duckdb_extensions(model, population))
    return oracle == _production_digest(model, population)

def _case_paths(case: dict[str, Any]) -> tuple[Path, Path]:
    root = CORPUS / str(case["path"])
    return root / "model.orm.yaml", root / "population.yaml"

def _parity_cases() -> list[dict[str, Any]]:
    selected = []
    for case in ANSWER_KEY["cases"]:
        model_path, population_path = _case_paths(case)
        try:
            model = load_model(model_path)
            load_population(population_path, model=model)
        except (ModelValidationError, PopulationValidationError):
            continue
        if any(
            isinstance(fact_type.get("derivation_rule"), dict) for fact_type in model.fact_types
        ):
            selected.append(case)
    return selected

def _assert_recorded_observation(
    *,
    case_id: str,
    backend: str,
    model_digest: str,
    population_digest: str,
    production_digest: str,
    backend_digest: str,
    version: str,
) -> None:
    """Apply the one receipt policy shared by all direct backend lanes."""
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    rows = {row.get("case_id"): row for row in receipt.get("cases", [])}
    row = rows.get(case_id)
    assert isinstance(row, dict), f"receipt has no row for {case_id}"
    assert _receipt_row_is_admissible(
        row,
        backend=backend,
        current={
            "model": model_digest,
            "population": population_digest,
            "production": production_digest,
            "backend": backend_digest,
            "version": version,
        },
    ), f"{case_id}: unbound or blocking {backend} result"

def _receipt_row_is_admissible(
    row: dict[str, Any],
    *,
    backend: str,
    current: dict[str, str],
) -> bool:
    if not _receipt_row_is_bound(row, backend=backend, current=current):
        return False
    result = row["results"][backend]
    if result.get("digest") != current["backend"]:
        return False
    if "version" in current and result.get("version") != current["version"]:
        return False
    if result["status"] == "matched":
        return True
    return result["disposition"] not in BLOCKING_DISPOSITIONS

def _receipt_row_is_bound(
    row: dict[str, Any],
    *,
    backend: str,
    current: dict[str, str],
) -> bool:
    if row.get("model_sha256") != current["model"]:
        return False
    if row.get("population_sha256") != current["population"]:
        return False
    if row.get("production_sha256") != current["production"]:
        return False
    result = row.get("results", {}).get(backend)
    if not isinstance(result, dict) or set(result) != {
        "status",
        "version",
        "digest",
        "disposition",
    }:
        return False
    if result["status"] == "matched":
        return (
            isinstance(result["version"], str)
            and result["digest"] == current["production"]
            and result["disposition"] is None
        )
    if result["status"] == "skipped":
        return (
            result["version"] is None and result["digest"] is None and result["disposition"] is None
        )
    return (
        result["status"] == "mismatched"
        and isinstance(result["version"], str)
        and isinstance(result["digest"], str)
        and result["digest"] != current["production"]
        and result["disposition"] in DISPOSITIONS
    )

def _nonempty_case() -> tuple[Any, Any]:
    for case in PARITY_CASES:
        model_path, population_path = _case_paths(case)
        model = load_model(model_path)
        population = load_population(population_path, model=model)
        result = _python_extension_calculator(model, _base_relations(model, population))
        if any(relation.rows for relation in result.extensions.values()):
            return model, population
    raise AssertionError("the frozen parity corpus must contain a non-empty extension")


PARITY_CASES = _parity_cases()

@pytest.mark.parametrize("case", PARITY_CASES, ids=[str(case["id"]) for case in PARITY_CASES])
def test_duckdb_matches_production(case: dict[str, Any]) -> None:
    model_path, population_path = _case_paths(case)
    model = load_model(model_path)
    population = load_population(population_path, model=model)
    _assert_recorded_observation(
        case_id=str(case["id"]),
        backend="duckdb",
        model_digest=_sha256(model_path),
        population_digest=_sha256(population_path),
        production_digest=_production_digest(model, population),
        backend_digest=_canonical_digest(model, _duckdb_extensions(model, population)),
        version=duckdb.__version__,
    )

def test_oracle_receipt_is_canonical_and_current() -> None:
    raw = RECEIPT.read_text(encoding="utf-8")
    receipt = json.loads(raw)
    assert (
        raw
        == json.dumps(
            receipt,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + "\n"
    )
    assert set(receipt) == {"schema_version", "identity_codec_version", "cases"}
    assert receipt["schema_version"] == 1
    assert receipt["identity_codec_version"] == CODEC_VERSION
    assert [row["case_id"] for row in receipt["cases"]] == [case["id"] for case in PARITY_CASES]
    for case, row in zip(PARITY_CASES, receipt["cases"], strict=True):
        assert set(row["results"]) == {"duckdb", "pyrel", "souffle"}
        model_path, population_path = _case_paths(case)
        model = load_model(model_path)
        population = load_population(population_path, model=model)
        production = _production_digest(model, population)
        duckdb_digest = _canonical_digest(model, _duckdb_extensions(model, population))
        common = {
            "model": _sha256(model_path),
            "population": _sha256(population_path),
            "production": production,
        }
        assert _receipt_row_is_admissible(
            row,
            backend="duckdb",
            current={
                **common,
                "backend": duckdb_digest,
                "version": duckdb.__version__,
            },
        )
        for backend, expected_version in (
            ("souffle", "2.5"),
            ("pyrel", PYREL_VERSION),
        ):
            result = row["results"][backend]
            if result["status"] == "skipped":
                assert _receipt_row_is_bound(row, backend=backend, current=common)
            else:
                assert _receipt_row_is_admissible(
                    row,
                    backend=backend,
                    current={
                        **common,
                        "backend": result["digest"],
                        "version": expected_version,
                    },
                )

def test_seeded_evaluator_mutation_makes_duckdb_parity_red(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Deleting one computed row must be caught by the independent SQL seat."""
    model, population = _nonempty_case()
    original = _python_extension_calculator

    def drop_first_row(model: Any, relations: Any) -> Any:
        result = original(model, relations)
        extensions = dict(result.extensions)
        fact_type_id = next(
            fact_type_id for fact_type_id, relation in extensions.items() if relation.rows
        )
        relation = extensions[fact_type_id]
        extensions[fact_type_id] = relation.__class__(
            relation.fact_type,
            relation.roles,
            relation.rows[1:],
            relation.identity_codec_version,
        )
        return result.__class__(MappingProxyType(extensions), result.counted_operations)

    assert _parity_matches(model, population)
    with monkeypatch.context() as mutation:
        mutation.setitem(globals(), "_python_extension_calculator", drop_first_row)
        assert not _parity_matches(model, population)
        assert _oracle_identity_token(1, "Integer") == '["number",[1,1]]'

def test_seeded_production_codec_mutation_makes_parity_red_but_goldens_stay_green(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model, population = _nonempty_case()
    assert _parity_matches(model, population)

    def wrong_production_codec(_value: Any) -> bytes:
        return b'["mutated","identity"]'

    with monkeypatch.context() as mutation:
        mutation.setitem(globals(), "_identity_token", wrong_production_codec)
        assert not _parity_matches(model, population)
        assert _oracle_identity_token(True, "Boolean") == '["boolean",true]'
        assert _oracle_identity_token(1, "Integer") == '["number",[1,1]]'

