"""Current aggregate receipt and exact-integer boundary guards."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

import duckdb
import pytest

from gnd.checker import structured_extension_facts
from gnd.model import Model, analyze_declared_aggregate
from gnd.population import load_population_bytes
from tests.support import public_parity_disposition as derivation_parity
from tests.support.v62_phase4_corpus import CASES_DOC, FIXTURE, document, population_document


def _aggregate_rules(model: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        fact["id"]: fact["derivation_rule"]
        for fact in model["fact_types"]
        if isinstance(fact.get("derivation_rule"), dict)
        and isinstance(fact["derivation_rule"].get("aggregate"), dict)
    }


def _fact_index(model: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {fact["id"]: fact for fact in model["fact_types"]}


def _primitives(model: dict[str, Any]) -> dict[str, str]:
    return {row["id"]: row["primitive"] for row in model["object_types"]}


def _sorted_rows(head_id: str, rows: list[dict], facts: dict[str, dict[str, Any]]) -> list[dict]:
    names = [role["role_name"] for role in facts[head_id]["roles"]]
    return sorted(rows, key=lambda row: tuple(row[name] for name in names))


def _rule_order(model: dict[str, Any]) -> list[str]:
    rules = _aggregate_rules(model)
    ordered: list[str] = []
    visiting: set[str] = set()

    def visit(head: str) -> None:
        if head in ordered:
            return
        assert head not in visiting, "aggregate parity program is cyclic"
        visiting.add(head)
        for atom in rules[head]["body"]:
            source = atom["fact_type"]
            if source in rules:
                visit(source)
        visiting.remove(head)
        ordered.append(head)

    for head in rules:
        visit(head)
    return ordered


def _sql_body(rule: dict[str, Any]) -> tuple[str, dict[str, str]]:
    assert not rule.get("negate"), "parity aggregate body has no negation"
    sources: list[str] = []
    variables: dict[str, str] = {}
    equalities: list[str] = []
    for index, atom in enumerate(rule["body"]):
        alias = f"b{index}"
        sources.append(f'"{atom["fact_type"]}" AS {alias}')
        for role, term in atom["bind"].items():
            assert isinstance(term, str) and term.startswith("$")
            name = term[1:]
            expression = f'{alias}."{role}"'
            if name in variables:
                equalities.append(f"{expression} = {variables[name]}")
            else:
                variables[name] = expression
    suffix = " WHERE " + " AND ".join(equalities) if equalities else ""
    return " CROSS JOIN ".join(sources) + suffix, variables


def _group(model: dict[str, Any], rule: dict[str, Any]) -> tuple[str, ...]:
    analysis = analyze_declared_aggregate(model, rule)
    assert analysis is not None and analysis.issue is None, analysis
    return analysis.group_variables


def _sql_term(term: object, variables: dict[str, str]) -> str:
    if isinstance(term, str) and term.startswith("$"):
        return variables[term[1:]]
    if not isinstance(term, dict):
        return json.dumps(term)
    args = [_sql_term(arg, variables) for arg in term["args"]]
    function = term["fn"]
    if function == "mod":
        return f"mod(mod({args[0]}, {args[1]}) + {args[1]}, {args[1]})"
    if function == "neg":
        return f"(-{args[0]})"
    if function == "abs":
        return f"abs({args[0]})"
    if function in {"add", "sub", "mul"}:
        operator = {"add": "+", "sub": "-", "mul": "*"}[function]
        return f"({args[0]} {operator} {args[1]})"
    raise AssertionError(f"unsupported parity term: {function}")


def _rational_term(
    term: object,
    variables: dict[str, str],
    aggregate_name: str,
    numerator: str,
    denominator: str,
    render: Any,
) -> tuple[str, str]:
    if term == f"${aggregate_name}":
        return numerator, denominator
    if type(term) is float:
        exact_numerator, exact_denominator = term.as_integer_ratio()
        return str(exact_numerator), str(exact_denominator)
    if not isinstance(term, dict):
        return render(term, variables), "1"
    function = term["fn"]
    if function == "mod":
        return render(term, variables), "1"
    parts = [
        _rational_term(arg, variables, aggregate_name, numerator, denominator, render)
        for arg in term["args"]
    ]
    if function == "neg":
        return f"(-{parts[0][0]})", parts[0][1]
    if function == "abs":
        return f"abs({parts[0][0]})", parts[0][1]
    left_num, left_den = parts[0]
    right_num, right_den = parts[1]
    if function in {"add", "sub"}:
        operator = "+" if function == "add" else "-"
        return (
            f"(({left_num}) * ({right_den}) {operator} ({right_num}) * ({left_den}))",
            f"(({left_den}) * ({right_den}))",
        )
    if function == "mul":
        return f"(({left_num}) * ({right_num}))", f"(({left_den}) * ({right_den}))"
    raise AssertionError(f"unsupported rational term: {function}")


def _rational_comparison(
    comparison: dict[str, Any],
    variables: dict[str, str],
    aggregate_name: str,
    numerator: str,
    denominator: str,
    render: Any,
) -> str:
    left_num, left_den = _rational_term(
        comparison["left"], variables, aggregate_name, numerator, denominator, render
    )
    right_num, right_den = _rational_term(
        comparison["right"], variables, aggregate_name, numerator, denominator, render
    )
    return f"(({left_num}) * ({right_den})) {comparison['operator']} (({right_num}) * ({left_den}))"


def _duckdb_rows(
    model: dict[str, Any], population: dict[str, Any], *, diagnostic_head: str | None = None
) -> dict[str, list[dict]]:
    facts = _fact_index(model)
    primitives = _primitives(model)
    connection = duckdb.connect(":memory:")
    try:
        for fact_id, fact in facts.items():
            if fact.get("derivation") == "derived":
                continue
            rows = population["facts"].get(fact_id, [])
            roles = fact["roles"]
            columns = ", ".join(
                f'"{role["role_name"]}" '
                + ("BIGINT" if primitives[role["object_type"]] == "Integer" else "VARCHAR")
                for role in roles
            )
            connection.execute(f'CREATE TABLE "{fact_id}" ({columns})')
            if rows:
                placeholders = ", ".join("?" for _ in roles)
                connection.executemany(
                    f'INSERT INTO "{fact_id}" VALUES ({placeholders})',
                    [tuple(row[role["role_name"]] for role in roles) for row in rows],
                )
        result: dict[str, list[dict]] = {}
        for head_id in _rule_order(model):
            rule = _aggregate_rules(model)[head_id]
            source_sql, variables = _sql_body(rule)
            groups = _group(model, rule)
            over = [item[1:] for item in rule["aggregate"]["over"]]
            contribution = [
                *(f"{variables[name]} AS g{index}" for index, name in enumerate(groups)),
                *(f"{variables[name]} AS o{index}" for index, name in enumerate(over)),
                f"{_sql_term(rule['aggregate']['of'], variables)} AS value",
            ]
            cte = (
                "WITH contribution AS (SELECT DISTINCT "
                + ", ".join(contribution)
                + f" FROM {source_sql}), "
            )
            group_columns = [f"g{index}" for index in range(len(groups))]
            function = rule["aggregate"]["fn"]
            if function == "avg":
                aggregates = "sum(value) AS numerator, count(*) AS denominator"
            else:
                expression = "count(*)" if function == "count" else f"{function}(value)"
                aggregates = f"{expression} AS result"
            select_agg = ", ".join([*group_columns, aggregates])
            group_clause = " GROUP BY " + ", ".join(group_columns) if group_columns else ""
            having = " HAVING count(*) > 0" if not group_columns else ""
            cte += f"aggregated AS (SELECT {select_agg} FROM contribution{group_clause}{having}) "
            predicates: list[str] = []
            aggregated_variables = {name: f"g{index}" for index, name in enumerate(groups)}
            if function != "avg":
                aggregated_variables[rule["aggregate"]["as"][1:]] = "result"
            for comparison in rule.get("where") or []:
                if function == "avg":
                    predicates.append(
                        _rational_comparison(
                            comparison,
                            aggregated_variables,
                            rule["aggregate"]["as"][1:],
                            "numerator",
                            "denominator",
                            _sql_term,
                        )
                    )
                else:
                    predicates.append(
                        f"{_sql_term(comparison['left'], aggregated_variables)} "
                        f"{comparison['operator']} "
                        f"{_sql_term(comparison['right'], aggregated_variables)}"
                    )
            if head_id == diagnostic_head:
                output = [f'g{index} AS "{name}"' for index, name in enumerate(groups)]
                if function == "avg":
                    output.extend(['numerator AS "__numerator"', 'denominator AS "__denominator"'])
                    role_names = [*groups, "__numerator", "__denominator"]
                else:
                    output.append('result AS "__aggregate_value"')
                    role_names = [*groups, "__aggregate_value"]
            else:
                output = []
                for role in facts[head_id]["roles"]:
                    term = rule["head"][role["role_name"]]
                    expression = _sql_term(term, aggregated_variables)
                    output.append(f'{expression} AS "{role["role_name"]}"')
                role_names = [role["role_name"] for role in facts[head_id]["roles"]]
            query = cte + "SELECT " + ", ".join(output) + " FROM aggregated"
            if predicates:
                query += " WHERE " + " AND ".join(predicates)
            rows = connection.execute(query).fetchall()
            decoded = [dict(zip(role_names, row, strict=True)) for row in rows]
            result[head_id] = (
                sorted(decoded, key=lambda row: tuple(row[name] for name in groups))
                if head_id == diagnostic_head
                else _sorted_rows(head_id, decoded, facts)
            )
            connection.execute(f'CREATE TABLE "{head_id}" AS {query}')
        return result
    finally:
        connection.close()


def _production_rows(
    model_document: dict[str, Any], population_document_: dict[str, Any]
) -> dict[str, list[dict]]:
    model = Model.model_validate(model_document)
    population = load_population_bytes(
        json.dumps(population_document_).encode(),
        source=FIXTURE / CASES_DOC["population"],
        model=model,
    )
    rows = structured_extension_facts(model, population)
    return {head: [dict(row) for row in rows[head]] for head in _aggregate_rules(model_document)}


def test_p11_p12_aggregate_parity_dispositions_are_blocking_or_byte_bound() -> None:
    production = _production_rows(document(), population_document())
    current = {
        "model": hashlib.sha256((FIXTURE / CASES_DOC["model"]).read_bytes()).hexdigest(),
        "population": hashlib.sha256((FIXTURE / CASES_DOC["population"]).read_bytes()).hexdigest(),
        "production": hashlib.sha256(
            json.dumps(production, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "backend": "0" * 64,
        "version": duckdb.__version__,
    }
    row = {
        "model_sha256": current["model"],
        "population_sha256": current["population"],
        "production_sha256": current["production"],
        "results": {
            "duckdb": {
                "status": "mismatched",
                "version": current["version"],
                "digest": current["backend"],
                "disposition": None,
            },
            "souffle": {
                "status": "mismatched",
                "version": "2.5",
                "digest": "1" * 64,
                "disposition": "oracle-defect",
            },
        },
    }
    for disposition in (None, "evaluator-bug", "spec-gap", "unknown"):
        candidate = deepcopy(row)
        candidate["results"]["duckdb"]["disposition"] = disposition
        assert not derivation_parity._receipt_row_is_admissible(
            candidate, backend="duckdb", current=current
        )
    for disposition in ("encoding-bug", "oracle-defect"):
        candidate = deepcopy(row)
        candidate["results"]["duckdb"]["disposition"] = disposition
        assert derivation_parity._receipt_row_is_admissible(
            candidate, backend="duckdb", current=current
        )
        for field in ("model_sha256", "population_sha256", "production_sha256"):
            stale = deepcopy(candidate)
            stale[field] = "f" * 64
            assert not derivation_parity._receipt_row_is_admissible(
                stale, backend="duckdb", current=current
            )
    assert not derivation_parity._receipt_row_is_admissible(
        row, backend="duckdb", current=current
    ), "another backend's disposition cannot admit DuckDB's mismatch"


def _numeric_scope_snapshot() -> dict[str, object]:
    model_doc, population_doc = document(), population_document()
    wide_value = 1 << 63
    population_doc["facts"]["observation"][0]["rb"] = wide_value
    production = _production_rows(model_doc, population_doc)
    north_sum = next(row["sum"] for row in production["scenario_sum"] if row["scenario"] == "north")
    assert north_sum == wide_value + 220
    with pytest.raises(duckdb.ConversionException, match="INT64"):
        _duckdb_rows(model_doc, population_doc)
    return {
        "four_seat_scope": "exact receipt cases only",
        "outside_receipt": "no external-engine parity claim",
        "wide_input_control": {
            "input_integer": str(wide_value),
            "production_north_sum": str(north_sum),
            "duckdb": "encoding-bug",
            "souffle": "unclaimed",
            "pyrel": "unclaimed",
        },
    }


def test_p12_wide_integer_is_exact_in_production_but_outside_external_parity() -> None:
    assert _numeric_scope_snapshot() == {
        "four_seat_scope": "exact receipt cases only",
        "outside_receipt": "no external-engine parity claim",
        "wide_input_control": {
            "input_integer": "9223372036854775808",
            "production_north_sum": "9223372036854776028",
            "duckdb": "encoding-bug",
            "souffle": "unclaimed",
            "pyrel": "unclaimed",
        },
    }

