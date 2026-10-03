"""Optional aggregate compiler seats; no default engine execution."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

import duckdb
import pytest

from gnd.checker import exact_extension_envelope, structured_extension_facts
from gnd.model import Model, analyze_declared_aggregate, semantic_validate
from gnd.population import load_population_bytes
from tests.support.v62_phase4_corpus import CASES_DOC, FIXTURE, document, population_document

pytestmark = pytest.mark.derivation_oracle

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


def _souffle_term(term: object, variables: dict[str, str]) -> str:
    if isinstance(term, dict) and term.get("fn") == "mod":
        left, right = (_souffle_term(arg, variables) for arg in term["args"])
        return f"((({left}) % ({right}) + ({right})) % ({right}))"
    return _sql_term(term, variables)


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


def _mod_denominators(term: object) -> list[object]:
    if not isinstance(term, dict) or set(term) != {"fn", "args"}:
        return []
    args = term["args"]
    found = [args[1]] if term["fn"] == "mod" else []
    for arg in args:
        found.extend(_mod_denominators(arg))
    return found


def _postwhere_denominators(rule: dict[str, Any]) -> list[tuple[list[dict], object]]:
    comparisons = rule.get("where") or []
    return [
        (comparisons[:index], denominator)
        for index, comparison in enumerate(comparisons)
        for side in ("left", "right")
        for denominator in _mod_denominators(comparison[side])
    ]


def _head_denominators(rule: dict[str, Any]) -> list[tuple[list[dict], object]]:
    return [
        (rule.get("where") or [], denominator)
        for term in rule["head"].values()
        for denominator in _mod_denominators(term)
    ]


def _body_primitives(model: dict[str, Any], rule: dict[str, Any]) -> dict[str, str]:
    facts = _fact_index(model)
    primitives = _primitives(model)
    return {
        term[1:]: primitives[
            next(
                role["object_type"]
                for role in facts[atom["fact_type"]]["roles"]
                if role["role_name"] == role_name
            )
        ]
        for atom in rule["body"]
        for role_name, term in atom["bind"].items()
    }


def _probe_comparison(
    comparison: dict[str, Any], rule: dict[str, Any], refs: dict[str, str], render: Any
) -> str:
    if rule["aggregate"]["fn"] == "avg":
        return _rational_comparison(
            comparison,
            refs,
            rule["aggregate"]["as"][1:],
            '"__numerator"' if render is _sql_term else "Numerator",
            '"__denominator"' if render is _sql_term else "Denominator",
            render,
        )
    return (
        f"{render(comparison['left'], refs)} {comparison['operator']} "
        f"{render(comparison['right'], refs)}"
    )


def _postwhere_probe_model(
    model: dict[str, Any], head_id: str, available_heads: list[str]
) -> dict[str, Any]:
    probe = deepcopy(model)
    rules = _aggregate_rules(model)
    probe["fact_types"] = [
        fact
        for fact in probe["fact_types"]
        if fact["id"] not in rules or fact["id"] in available_heads or fact["id"] == head_id
    ]
    _aggregate_rules(probe)[head_id]["where"] = []
    return probe


def _duckdb_unavailable(model: dict[str, Any], population: dict[str, Any]) -> dict[str, dict]:
    facts = _fact_index(model)
    primitives = _primitives(model)
    rules = _aggregate_rules(model)
    unavailable: dict[str, dict] = {}
    available_heads: list[str] = []
    for head_id in _rule_order(model):
        rule = rules[head_id]
        source_failure = next(
            (atom["fact_type"] for atom in rule["body"] if atom["fact_type"] in unavailable),
            None,
        )
        if source_failure is not None:
            unavailable[head_id] = {
                "reason": unavailable[source_failure]["reason"],
                "source_relation": source_failure,
            }
            continue
        denominators = _mod_denominators(rule["aggregate"]["of"])
        if denominators:
            prefix_model = deepcopy(model)
            prefix_model["fact_types"] = [
                fact
                for fact in model["fact_types"]
                if fact["id"] not in rules or fact["id"] in available_heads
            ]
            previous = _duckdb_rows(prefix_model, population)
            connection = duckdb.connect(":memory:")
            try:
                for source_id in {atom["fact_type"] for atom in rule["body"]}:
                    roles = facts[source_id]["roles"]
                    columns = ", ".join(
                        f'"{role["role_name"]}" '
                        + ("BIGINT" if primitives[role["object_type"]] == "Integer" else "VARCHAR")
                        for role in roles
                    )
                    connection.execute(f'CREATE TABLE "{source_id}" ({columns})')
                    rows = (
                        previous[source_id]
                        if source_id in rules
                        else population["facts"].get(source_id, [])
                    )
                    if rows:
                        connection.executemany(
                            f'INSERT INTO "{source_id}" VALUES ({", ".join("?" for _ in roles)})',
                            [tuple(row[role["role_name"]] for role in roles) for row in rows],
                        )
                source_sql, refs = _sql_body(rule)
                for denominator in denominators:
                    expression = _sql_term(denominator, refs)
                    connector = " AND " if " WHERE " in source_sql else " WHERE "
                    found = connection.execute(
                        f"SELECT EXISTS(SELECT 1 FROM {source_sql}{connector}{expression} = 0)"
                    ).fetchone()[0]
                    if found:
                        unavailable[head_id] = {
                            "reason": "term:mod-zero",
                            "source_relation": None,
                        }
                        break
            finally:
                connection.close()
        diagnostic_denominators = [*_postwhere_denominators(rule), *_head_denominators(rule)]
        if head_id not in unavailable and diagnostic_denominators:
            probe = _postwhere_probe_model(model, head_id, available_heads)
            rows = _duckdb_rows(probe, population, diagnostic_head=head_id)[head_id]
            if rows:
                groups = _group(model, rule)
                primitive_by_name = _body_primitives(model, rule)
                function = rule["aggregate"]["fn"]
                names = [
                    *groups,
                    *(
                        ["__numerator", "__denominator"]
                        if function == "avg"
                        else ["__aggregate_value"]
                    ),
                ]
                refs = {name: f'"{name}"' for name in groups}
                if function != "avg":
                    refs[rule["aggregate"]["as"][1:]] = '"__aggregate_value"'
                connection = duckdb.connect(":memory:")
                try:
                    columns = ", ".join(
                        f'"{name}" '
                        + (
                            "BIGINT"
                            if name.startswith("__") or primitive_by_name[name] == "Integer"
                            else "VARCHAR"
                        )
                        for name in names
                    )
                    connection.execute(f"CREATE TABLE post_aggregate ({columns})")
                    connection.executemany(
                        f"INSERT INTO post_aggregate VALUES ({', '.join('?' for _ in names)})",
                        [tuple(row[name] for name in names) for row in rows],
                    )
                    for preceding, denominator in diagnostic_denominators:
                        expression = _sql_term(denominator, refs)
                        prior = [
                            _probe_comparison(item, rule, refs, _sql_term) for item in preceding
                        ]
                        found = connection.execute(
                            "SELECT EXISTS(SELECT 1 FROM post_aggregate WHERE "
                            + (
                                " AND ".join(f"({item})" for item in prior) + " AND "
                                if prior
                                else ""
                            )
                            + expression
                            + " = 0)"
                        ).fetchone()[0]
                        if found:
                            unavailable[head_id] = {
                                "reason": "term:mod-zero",
                                "source_relation": None,
                            }
                            break
                finally:
                    connection.close()
        if head_id not in unavailable:
            available_heads.append(head_id)
    return unavailable


def _souffle_unavailable(model: dict[str, Any], population: dict[str, Any]) -> dict[str, dict]:
    executable = shutil.which("souffle")
    if executable is None:
        pytest.skip("Souffle aggregate seat is not installed")
    facts = _fact_index(model)
    primitives = _primitives(model)
    rules = _aggregate_rules(model)
    unavailable: dict[str, dict] = {}
    available_heads: list[str] = []
    for head_id in _rule_order(model):
        rule = rules[head_id]
        source_failure = next(
            (atom["fact_type"] for atom in rule["body"] if atom["fact_type"] in unavailable),
            None,
        )
        if source_failure is not None:
            unavailable[head_id] = {
                "reason": unavailable[source_failure]["reason"],
                "source_relation": source_failure,
            }
            continue
        denominators = _mod_denominators(rule["aggregate"]["of"])
        if denominators:
            prefix_model = deepcopy(model)
            prefix_model["fact_types"] = [
                fact
                for fact in model["fact_types"]
                if fact["id"] not in rules or fact["id"] in available_heads
            ]
            previous = _souffle_rows(prefix_model, population) if available_heads else {}
            with tempfile.TemporaryDirectory(prefix="gnd-v62-p4-souffle-undefined-") as directory:
                root = Path(directory)
                program = [".decl invalid(value:number)"]
                body_calls: list[str] = []
                symbols: dict[str, str] = {}
                for atom in rule["body"]:
                    source_id = atom["fact_type"]
                    source = f"r_{source_id}"
                    roles = facts[source_id]["roles"]
                    columns = ", ".join(
                        f"r{index}:"
                        + ("number" if primitives[role["object_type"]] == "Integer" else "symbol")
                        for index, role in enumerate(roles)
                    )
                    source_rows = (
                        previous[source_id]
                        if source_id in rules
                        else population["facts"].get(source_id, [])
                    )
                    (root / f"{source_id}.facts").write_text(
                        "".join(
                            "\t".join(str(row[role["role_name"]]) for role in roles) + "\n"
                            for row in source_rows
                        ),
                        encoding="utf-8",
                    )
                    program.extend(
                        [
                            f".decl {source}({columns})",
                            f'.input {source}(filename="{source_id}.facts")',
                        ]
                    )
                    for term in atom["bind"].values():
                        symbols[term[1:]] = f"V_{term[1:]}"
                    body_args = [symbols[atom["bind"][role["role_name"]][1:]] for role in roles]
                    body_calls.append(f"{source}({', '.join(body_args)})")
                for denominator in denominators:
                    program.append(
                        f"invalid(1) :- {', '.join(body_calls)}, "
                        f"{_souffle_term(denominator, symbols)} = 0."
                    )
                program.append('.output invalid(filename="invalid.csv")')
                path = root / "undefined.dl"
                path.write_text("\n".join(program) + "\n", encoding="utf-8")
                completed = subprocess.run(
                    [executable, "-F", str(root), "-D", str(root), str(path)],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    check=False,
                )
                assert completed.returncode == 0, completed.stdout + completed.stderr
                if (root / "invalid.csv").read_text(encoding="utf-8").strip():
                    unavailable[head_id] = {"reason": "term:mod-zero", "source_relation": None}
        diagnostic_denominators = [*_postwhere_denominators(rule), *_head_denominators(rule)]
        if head_id not in unavailable and diagnostic_denominators:
            probe = _postwhere_probe_model(model, head_id, available_heads)
            rows = _souffle_rows(probe, population, diagnostic_head=head_id)[head_id]
            if rows:
                with tempfile.TemporaryDirectory(
                    prefix="gnd-v62-p4-souffle-post-undefined-"
                ) as directory:
                    root = Path(directory)
                    program = [".decl invalid(value:number)"]
                    groups = _group(model, rule)
                    function = rule["aggregate"]["fn"]
                    names = [
                        *groups,
                        *(
                            ["__numerator", "__denominator"]
                            if function == "avg"
                            else ["__aggregate_value"]
                        ),
                    ]
                    primitive_by_name = _body_primitives(model, rule)
                    columns = ", ".join(
                        f"r{index}:"
                        + (
                            "number"
                            if name.startswith("__") or primitive_by_name[name] == "Integer"
                            else "symbol"
                        )
                        for index, name in enumerate(names)
                    )
                    program.extend(
                        [
                            f".decl post({columns})",
                            '.input post(filename="post.facts")',
                        ]
                    )
                    (root / "post.facts").write_text(
                        "".join("\t".join(str(row[name]) for name in names) + "\n" for row in rows),
                        encoding="utf-8",
                    )
                    group_symbols = {name: f"V_{name}" for name in groups}
                    symbols = dict(group_symbols)
                    if function != "avg":
                        symbols[rule["aggregate"]["as"][1:]] = "Result"
                    body_args = [
                        *(group_symbols[name] for name in groups),
                        *(["Numerator", "Denominator"] if function == "avg" else ["Result"]),
                    ]
                    body = f"post({', '.join(body_args)})"
                    for preceding, denominator in diagnostic_denominators:
                        prior = [
                            _probe_comparison(item, rule, symbols, _souffle_term)
                            for item in preceding
                        ]
                        program.append(
                            f"invalid(1) :- {body}, "
                            + ", ".join([*prior, f"{_souffle_term(denominator, symbols)} = 0"])
                            + "."
                        )
                    program.append('.output invalid(filename="invalid.csv")')
                    path = root / "undefined.dl"
                    path.write_text("\n".join(program) + "\n", encoding="utf-8")
                    completed = subprocess.run(
                        [executable, "-F", str(root), "-D", str(root), str(path)],
                        capture_output=True,
                        text=True,
                        timeout=120,
                        check=False,
                    )
                    assert completed.returncode == 0, completed.stdout + completed.stderr
                    if (root / "invalid.csv").read_text(encoding="utf-8").strip():
                        unavailable[head_id] = {"reason": "term:mod-zero", "source_relation": None}
        if head_id not in unavailable:
            available_heads.append(head_id)
    return unavailable


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


def _souffle_rows(
    model: dict[str, Any], population: dict[str, Any], *, diagnostic_head: str | None = None
) -> dict[str, list[dict]]:
    executable = shutil.which("souffle")
    if executable is None:
        pytest.skip("Souffle aggregate seat is not installed")
    facts = _fact_index(model)
    primitives = _primitives(model)
    aggregate_rules = _aggregate_rules(model)
    source_ids = {
        atom["fact_type"]
        for rule in aggregate_rules.values()
        for atom in rule["body"]
        if atom["fact_type"] not in aggregate_rules
    }
    program: list[str] = []
    with tempfile.TemporaryDirectory(prefix="gnd-v62-p4-souffle-") as directory:
        root = Path(directory)
        for source_id in sorted(source_ids):
            roles = facts[source_id]["roles"]
            columns = ", ".join(
                f"{role['role_name']}:"
                + ("number" if primitives[role["object_type"]] == "Integer" else "symbol")
                for role in roles
            )
            program.append(f".decl r_{source_id}({columns})")
            program.append(f'.input r_{source_id}(filename="{source_id}.facts")')
            encoded = []
            for row in population["facts"].get(source_id, []):
                encoded.append("\t".join(str(row[role["role_name"]]) for role in roles))
            (root / f"{source_id}.facts").write_text(
                "\n".join(encoded) + ("\n" if encoded else ""), encoding="utf-8"
            )
        for head_id in _rule_order(model):
            rule = aggregate_rules[head_id]
            assert not rule.get("negate")
            variable_types: dict[str, str] = {}
            for atom in rule["body"]:
                roles_by_name = {
                    role["role_name"]: role for role in facts[atom["fact_type"]]["roles"]
                }
                for role_name, term in atom["bind"].items():
                    assert isinstance(term, str) and term.startswith("$")
                    variable_types[term[1:]] = (
                        "number"
                        if primitives[roles_by_name[role_name]["object_type"]] == "Integer"
                        else "symbol"
                    )
            groups = _group(model, rule)
            over = [item[1:] for item in rule["aggregate"]["over"]]
            fn = rule["aggregate"]["fn"]
            value_type = (
                variable_types[rule["aggregate"]["of"][1:]]
                if isinstance(rule["aggregate"]["of"], str)
                else "number"
            )
            contribution_columns = [
                *(f"g{index}:{variable_types[name]}" for index, name in enumerate(groups)),
                *(f"o{index}:{variable_types[name]}" for index, name in enumerate(over)),
                f"value:{value_type}",
            ]
            contribution = f"c_{head_id}"
            program.append(f".decl {contribution}({', '.join(contribution_columns)})")
            variable_symbols = {name: f"V_{name}" for name in variable_types}
            body_calls = []
            for atom in rule["body"]:
                source_id = atom["fact_type"]
                source_roles = facts[source_id]["roles"]
                role_terms = atom["bind"]
                body_args = [
                    variable_symbols[role_terms[role["role_name"]][1:]] for role in source_roles
                ]
                source_relation = (
                    f"out_{source_id}" if source_id in aggregate_rules else f"r_{source_id}"
                )
                body_calls.append(f"{source_relation}({', '.join(body_args)})")
            contribution_args = [
                *(variable_symbols[name] for name in groups),
                *(variable_symbols[name] for name in over),
                _souffle_term(rule["aggregate"]["of"], variable_symbols),
            ]
            program.append(
                f"{contribution}({', '.join(contribution_args)}) :- " + ", ".join(body_calls) + "."
            )
            aggregate = f"a_{head_id}"
            aggregate_columns = [
                *(f"g{index}:{variable_types[name]}" for index, name in enumerate(groups)),
                *(["numerator:number", "denominator:number"] if fn == "avg" else ["result:number"]),
            ]
            program.append(f".decl {aggregate}({', '.join(aggregate_columns)})")
            group_vars = [f"G{index}" for index in range(len(groups))]
            wildcards = ["_" for _ in range(len(over) + 1)]
            anchor = f"{contribution}({', '.join([*group_vars, *wildcards])})"
            inner = f"{contribution}({', '.join([*group_vars, *(f'O{index}' for index in range(len(over))), 'Value'])})"
            if fn == "count":
                calculation = f"Result = count : {inner}"
            elif fn == "avg":
                calculation = f"Numerator = sum Value : {inner}, Denominator = count : {inner}"
            else:
                calculation = f"Result = {fn} Value : {inner}"
            aggregate_result = ["Numerator", "Denominator"] if fn == "avg" else ["Result"]
            program.append(
                f"{aggregate}({', '.join([*group_vars, *aggregate_result])}) :- "
                f"{anchor}, {calculation}."
            )
            head_roles = facts[head_id]["roles"]
            output = f"out_{head_id}"
            if head_id == diagnostic_head:
                diagnostic_types = [
                    *(variable_types[name] for name in groups),
                    *(["number", "number"] if fn == "avg" else ["number"]),
                ]
                output_columns = [f"r{index}:{kind}" for index, kind in enumerate(diagnostic_types)]
            else:
                output_columns = [
                    f"r{index}:"
                    + ("number" if primitives[role["object_type"]] == "Integer" else "symbol")
                    for index, role in enumerate(head_roles)
                ]
            program.append(f".decl {output}({', '.join(output_columns)})")
            arguments = []
            head_assignments = []
            aggregated_variables = {
                **{name: group_vars[index] for index, name in enumerate(groups)},
                **({rule["aggregate"]["as"][1:]: "Result"} if fn != "avg" else {}),
            }
            if head_id == diagnostic_head:
                arguments = [*group_vars, *aggregate_result]
            else:
                for role in head_roles:
                    term = rule["head"][role["role_name"]]
                    if isinstance(term, dict):
                        symbol = f"H{len(arguments)}"
                        arguments.append(symbol)
                        head_assignments.append(
                            f"{symbol} = {_souffle_term(term, aggregated_variables)}"
                        )
                    else:
                        arguments.append(_souffle_term(term, aggregated_variables))
            comparisons = []
            for comparison in rule.get("where") or []:
                if fn == "avg":
                    comparisons.append(
                        _rational_comparison(
                            comparison,
                            aggregated_variables,
                            rule["aggregate"]["as"][1:],
                            "Numerator",
                            "Denominator",
                            _souffle_term,
                        )
                    )
                else:
                    comparisons.append(
                        f"{_souffle_term(comparison['left'], aggregated_variables)} "
                        f"{comparison['operator']} "
                        f"{_souffle_term(comparison['right'], aggregated_variables)}"
                    )
            program.append(
                f"{output}({', '.join(arguments)}) :- "
                f"{aggregate}({', '.join([*group_vars, *aggregate_result])})"
                + (
                    ", " + ", ".join([*head_assignments, *comparisons])
                    if head_assignments or comparisons
                    else ""
                )
                + "."
            )
            program.append(f'.output {output}(filename="{output}.csv")')
        program_path = root / "aggregate.dl"
        program_path.write_text("\n".join(program) + "\n", encoding="utf-8")
        completed = subprocess.run(
            [executable, "-F", str(root), "-D", str(root), str(program_path)],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        assert completed.returncode == 0, (
            completed.stdout + completed.stderr + "\n" + "\n".join(program)
        )
        result: dict[str, list[dict]] = {}
        for head_id in _aggregate_rules(model):
            lines = (root / f"out_{head_id}.csv").read_text(encoding="utf-8").splitlines()
            if head_id == diagnostic_head:
                rule = aggregate_rules[head_id]
                groups = _group(model, rule)
                names = [
                    *groups,
                    *(
                        ["__numerator", "__denominator"]
                        if rule["aggregate"]["fn"] == "avg"
                        else ["__aggregate_value"]
                    ),
                ]
                primitive_by_name = _body_primitives(model, rule)
                result[head_id] = sorted(
                    [
                        {
                            name: (
                                int(value)
                                if name.startswith("__") or primitive_by_name[name] == "Integer"
                                else value
                            )
                            for name, value in zip(names, line.split("\t"), strict=True)
                        }
                        for line in lines
                    ],
                    key=lambda row: tuple(row[name] for name in groups),
                )
            else:
                roles = facts[head_id]["roles"]
                result[head_id] = _sorted_rows(
                    head_id,
                    [
                        {
                            role["role_name"]: (
                                int(value)
                                if primitives[role["object_type"]] == "Integer"
                                else value
                            )
                            for role, value in zip(roles, line.split("\t"), strict=True)
                        }
                        for line in lines
                    ],
                    facts,
                )
        return result


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


def _pyrel_envelope(model: dict[str, Any], population: dict[str, Any]) -> dict[str, Any]:
    executable = shutil.which("uv")
    if executable is None:
        pytest.skip("uv is required for the isolated PyRel aggregate seat")
    oracle = Path(__file__).resolve().parent / "oracles/pyrel_v62_aggregate_oracle.py"
    analyses: dict[str, list[str]] = {}
    for head_id, rule in _aggregate_rules(model).items():
        analysis = analyze_declared_aggregate(model, rule)
        assert analysis is not None and analysis.issue is None, analysis
        analyses[head_id] = list(analysis.group_variables)
    with tempfile.TemporaryDirectory(prefix="gnd-v62-p4-pyrel-") as directory:
        output = Path(directory) / "result.json"
        completed = subprocess.run(
            [executable, "run", "--locked", "--script", str(oracle)],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
            env={
                **os.environ,
                "GND_AGG_MODEL": json.dumps(model),
                "GND_AGG_POPULATION": json.dumps(population),
                "GND_AGG_ANALYSIS": json.dumps(analyses),
                "GND_AGG_OUTPUT": str(output),
                "RAI_BUILD_DIR": str(Path(directory) / "build"),
            },
        )
        assert completed.returncode == 0, completed.stdout + completed.stderr
        payload = json.loads(output.read_text(encoding="utf-8"))
    assert set(payload) == {"schema_version", "backend", "version", "relations", "unavailable"}
    assert (payload["schema_version"], payload["backend"], payload["version"]) == (
        1,
        "pyrel",
        "1.30.1",
    )
    assert set(payload["relations"]) | set(payload["unavailable"]) == set(_aggregate_rules(model))
    return payload


def _pyrel_rows(model: dict[str, Any], population: dict[str, Any]) -> dict[str, list[dict]]:
    payload = _pyrel_envelope(model, population)
    assert not payload["unavailable"]
    return payload["relations"]


def test_p01_p02_p03_p04_p05_p06_p07_p08_four_engines_compile_all_five_functions() -> None:
    model_document = document()
    population = population_document()
    production = _production_rows(model_document, population)
    duckdb_rows = _duckdb_rows(model_document, population)
    souffle_rows = _souffle_rows(model_document, population)
    pyrel_rows = _pyrel_rows(model_document, population)
    assert production == duckdb_rows == souffle_rows == pyrel_rows
    assert production == {
        "scenario_count": [
            {"scenario": "north", "count": 3},
            {"scenario": "south", "count": 1},
        ],
        "scenario_sum": [
            {"scenario": "north", "sum": 320},
            {"scenario": "south", "sum": 180},
        ],
        "scenario_min": [
            {"scenario": "north", "min": 100},
            {"scenario": "south", "min": 180},
        ],
        "scenario_max": [
            {"scenario": "north", "max": 120},
            {"scenario": "south", "max": 180},
        ],
        "scenario_mean_ok": [{"scenario": "north"}],
    }


def test_p09_noninjective_of_and_duplicate_proof_do_not_collapse_or_multiply() -> None:
    model_document = document()
    population = population_document()
    model_document["fact_types"][1]["derivation_rule"]["aggregate"]["of"] = {
        "fn": "mod",
        "args": ["$rb", 2],
    }
    population["facts"]["observation"].append(population["facts"]["observation"][0].copy())
    assert len(population["facts"]["observation"]) == 5
    production = _production_rows(model_document, population)
    duckdb_rows = _duckdb_rows(model_document, population)
    souffle_rows = _souffle_rows(model_document, population)
    pyrel_rows = _pyrel_rows(model_document, population)
    assert production == duckdb_rows == souffle_rows == pyrel_rows
    assert production["scenario_count"] == [
        {"scenario": "north", "count": 3},
        {"scenario": "south", "count": 1},
    ]
    assert len({row["rb"] % 2 for row in population["facts"]["observation"]}) == 1


def test_p09_negative_mod_of_uses_floor_semantics_in_all_four_seats() -> None:
    model_document = document()
    population = population_document()
    model_document["fact_types"][2]["derivation_rule"]["aggregate"]["of"] = {
        "fn": "mod",
        "args": [{"fn": "neg", "args": ["$rb"]}, 30],
    }
    production = _production_rows(model_document, population)
    assert production["scenario_sum"] == [
        {"scenario": "north", "sum": 40},
        {"scenario": "south", "sum": 0},
    ]
    assert production == _duckdb_rows(model_document, population)
    assert production == _souffle_rows(model_document, population)
    assert production == _pyrel_rows(model_document, population)


def _join_and_upper_case(*, unavailable: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    model_document = document()
    population = population_document()
    model_document["object_types"].append(
        {"id": "tag", "name": "Tag", "kind": "value", "primitive": "String"}
    )
    model_document["fact_types"].append(
        {
            "id": "sample_mark",
            "reading": "{Sample} bears {Tag}",
            "roles": [
                {"object_type": "sample", "role_name": "sample"},
                {"object_type": "tag", "role_name": "tag"},
            ],
        }
    )
    model_document["fact_types"].append(
        {
            "id": "scenario_count_total",
            "reading": "{Scenario} has total {Integer}",
            "roles": [
                {"object_type": "scenario", "role_name": "scenario"},
                {"object_type": "integer", "role_name": "total"},
            ],
            "derivation": "derived",
            "derivation_rule": {
                "body": [
                    {
                        "fact_type": "scenario_count",
                        "bind": {"scenario": "$scenario", "count": "$count"},
                    }
                ],
                "aggregate": {
                    "fn": "sum",
                    "of": "$count",
                    "over": ["$scenario"],
                    "as": "$total",
                },
                "head": {"scenario": "$scenario", "total": "$total"},
            },
        }
    )
    count_rule = model_document["fact_types"][1]["derivation_rule"]
    count_rule["body"].append(
        {"fact_type": "sample_mark", "bind": {"sample": "$sample", "tag": "$tag"}}
    )
    if unavailable:
        count_rule["aggregate"]["of"] = {"fn": "mod", "args": ["$rb", 0]}
    population["facts"]["sample_mark"] = [
        {"sample": row["sample"], "tag": "primary"} for row in population["facts"]["observation"]
    ] + [{"sample": "north-1", "tag": "secondary"}]
    population["population"]["covers"].extend(["sample_mark", "scenario_count_total"])
    population["facts"]["scenario_count_total"] = [
        {"scenario": "north", "total": 3},
        {"scenario": "south", "total": 1},
    ]
    return model_document, population


def test_p09_two_atom_duplicate_proof_and_upper_aggregate_match_four_seats() -> None:
    model_document, population = _join_and_upper_case()
    production = _production_rows(model_document, population)
    assert production["scenario_count"] == [
        {"scenario": "north", "count": 3},
        {"scenario": "south", "count": 1},
    ]
    assert production["scenario_count_total"] == [
        {"scenario": "north", "total": 3},
        {"scenario": "south", "total": 1},
    ]
    assert production == _duckdb_rows(model_document, population)
    assert production == _souffle_rows(model_document, population)
    assert production == _pyrel_rows(model_document, population)


def test_p08_sum_post_filter_compiles_in_all_four_seats() -> None:
    model_document, population = document(), population_document()
    model_document["fact_types"][2]["derivation_rule"]["where"] = [
        {"operator": ">", "left": "$sum", "right": 0}
    ]
    production = _production_rows(model_document, population)
    assert production["scenario_sum"] == [
        {"scenario": "north", "sum": 320},
        {"scenario": "south", "sum": 180},
    ]
    assert production == _duckdb_rows(model_document, population)
    assert production == _souffle_rows(model_document, population)
    assert production == _pyrel_rows(model_document, population)


@pytest.mark.parametrize(
    "comparison",
    [
        {"operator": "<", "left": 100, "right": "$mean"},
        {"operator": ">", "left": {"fn": "add", "args": ["$mean", 1]}, "right": 100},
    ],
)
def test_p08_average_post_filter_admits_legal_operand_order_and_terms(comparison: dict) -> None:
    model_document, population = document(), population_document()
    model_document["fact_types"][5]["derivation_rule"]["where"] = [comparison]
    production = _production_rows(model_document, population)
    assert production["scenario_mean_ok"] == [
        {"scenario": "north"},
        {"scenario": "south"},
    ]
    assert production == _duckdb_rows(model_document, population)
    assert production == _souffle_rows(model_document, population)
    assert production == _pyrel_rows(model_document, population)


def test_p08_average_comparison_admits_nested_integer_mod_term() -> None:
    model_document, population = document(), population_document()
    model_document["fact_types"][5]["derivation_rule"]["where"] = [
        {
            "operator": ">",
            "left": {
                "fn": "add",
                "args": [
                    "$mean",
                    {"fn": "mod", "args": [{"fn": "add", "args": [1, 1]}, 2]},
                ],
            },
            "right": 100,
        }
    ]
    assert semantic_validate(model_document) == []
    production = _production_rows(model_document, population)
    assert production["scenario_mean_ok"] == [{"scenario": "north"}, {"scenario": "south"}]
    assert production == _duckdb_rows(model_document, population)
    assert production == _souffle_rows(model_document, population)
    assert production == _pyrel_rows(model_document, population)


def test_p08_average_comparison_preserves_binary_float_literal() -> None:
    model_document, population = document(), population_document()
    model_document["fact_types"][5]["derivation_rule"]["where"] = [
        {"operator": "=", "left": "$mean", "right": 0.1}
    ]
    population["facts"]["observation"] = [
        {"scenario": "north", "sample": f"n-{index}", "rb": int(index == 0)} for index in range(10)
    ]
    assert semantic_validate(model_document) == []
    production = _production_rows(model_document, population)
    assert production["scenario_mean_ok"] == []
    assert production == _duckdb_rows(model_document, population)
    assert production == _souffle_rows(model_document, population)
    assert production == _pyrel_rows(model_document, population)


def test_p06_computed_integer_aggregate_head_compiles_in_four_seats() -> None:
    model_document, population = document(), population_document()
    model_document["fact_types"][2]["derivation_rule"]["head"]["sum"] = {
        "fn": "add",
        "args": ["$sum", 1],
    }
    production = _production_rows(model_document, population)
    assert production["scenario_sum"] == [
        {"scenario": "north", "sum": 321},
        {"scenario": "south", "sum": 181},
    ]
    assert production == _duckdb_rows(model_document, population)
    assert production == _souffle_rows(model_document, population)
    assert production == _pyrel_rows(model_document, population)


def test_p05_global_count_compiles_in_all_four_seats() -> None:
    model_document, population = document(), population_document()
    count_fact = model_document["fact_types"][1]
    count_fact["reading"] = "{Integer} is the observation count"
    count_fact["roles"] = [role for role in count_fact["roles"] if role["role_name"] == "count"]
    count_fact["derivation_rule"]["head"] = {"count": "$count"}
    model_document["fact_types"] = [model_document["fact_types"][0], count_fact]
    model_document["constraints"] = []
    model_document["operations"] = []
    population["population"]["covers"] = ["observation", "scenario_count"]
    population["facts"] = {
        "observation": population["facts"]["observation"],
        "scenario_count": [{"count": 4}],
    }
    production = _production_rows(model_document, population)
    assert production == {"scenario_count": [{"count": 4}]}
    assert production == _duckdb_rows(model_document, population)
    assert production == _souffle_rows(model_document, population)
    assert production == _pyrel_rows(model_document, population)


def test_p10_four_engines_report_unavailable_for_undefined_contribution() -> None:
    model_document = document()
    population_document_ = population_document()
    model_document["fact_types"][1]["derivation_rule"]["aggregate"]["of"] = {
        "fn": "mod",
        "args": ["$rb", 0],
    }
    model = Model.model_validate(model_document)
    population = load_population_bytes(
        json.dumps(population_document_).encode(), source="undefined-aggregate.json", model=model
    )
    production = exact_extension_envelope(model, population)["unavailable"]
    expected = {"scenario_count": {"reason": "term:mod-zero", "source_relation": None}}
    assert {
        head: {"reason": row["reason"], "source_relation": row["source_relation"]}
        for head, row in production.items()
    } == expected
    assert _duckdb_unavailable(model_document, population_document_) == expected
    assert _souffle_unavailable(model_document, population_document_) == expected
    assert _pyrel_envelope(model_document, population_document_)["unavailable"] == expected


def test_p10_undefined_post_aggregate_comparison_is_unavailable_in_four_seats() -> None:
    model_document, population_document_ = document(), population_document()
    model_document["fact_types"][2]["derivation_rule"]["where"] = [
        {"operator": "=", "left": {"fn": "mod", "args": ["$sum", 0]}, "right": 0}
    ]
    model = Model.model_validate(model_document)
    population = load_population_bytes(
        json.dumps(population_document_).encode(),
        source="undefined-post-aggregate.json",
        model=model,
    )
    production = exact_extension_envelope(model, population)["unavailable"]
    expected = {"scenario_sum": {"reason": "term:mod-zero", "source_relation": None}}
    assert {
        head: {"reason": row["reason"], "source_relation": row["source_relation"]}
        for head, row in production.items()
    } == expected
    assert _duckdb_unavailable(model_document, population_document_) == expected
    assert _souffle_unavailable(model_document, population_document_) == expected
    assert _pyrel_envelope(model_document, population_document_)["unavailable"] == expected


def test_p10_false_post_filter_precedes_later_undefined_comparison_in_four_seats() -> None:
    model_document, population_document_ = document(), population_document()
    model_document["fact_types"][2]["derivation_rule"]["where"] = [
        {"operator": ">", "left": "$sum", "right": 1_000},
        {"operator": "=", "left": {"fn": "mod", "args": ["$sum", 0]}, "right": 0},
    ]
    model = Model.model_validate(model_document)
    population = load_population_bytes(
        json.dumps(population_document_).encode(), source="false-before-undefined.json", model=model
    )
    assert exact_extension_envelope(model, population)["unavailable"] == {}
    assert _duckdb_unavailable(model_document, population_document_) == {}
    assert _souffle_unavailable(model_document, population_document_) == {}
    assert _pyrel_envelope(model_document, population_document_)["unavailable"] == {}


def test_p10_unprojected_aggregate_value_still_compiles_unavailability() -> None:
    model_document, population_document_ = document(), population_document()
    observation, sum_fact = model_document["fact_types"][0], model_document["fact_types"][2]
    sum_fact["reading"] = "{Scenario} has a selected total"
    sum_fact["roles"] = [sum_fact["roles"][0]]
    sum_fact["derivation_rule"]["head"] = {"scenario": "$scenario"}
    sum_fact["derivation_rule"]["where"] = [
        {
            "operator": "=",
            "left": {
                "fn": "mod",
                "args": ["$sum", {"fn": "sub", "args": ["$sum", "$sum"]}],
            },
            "right": 0,
        }
    ]
    model_document["fact_types"] = [observation, sum_fact]
    model_document["constraints"] = []
    model_document["operations"] = []
    population_document_["population"]["covers"] = ["observation", "scenario_sum"]
    population_document_["facts"] = {
        "observation": population_document_["facts"]["observation"],
        "scenario_sum": [],
    }
    assert semantic_validate(model_document) == []
    model = Model.model_validate(model_document)
    population = load_population_bytes(
        json.dumps(population_document_).encode(), source="hidden-aggregate.json", model=model
    )
    production = exact_extension_envelope(model, population)["unavailable"]
    expected = {"scenario_sum": {"reason": "term:mod-zero", "source_relation": None}}
    assert {
        head: {"reason": row["reason"], "source_relation": row["source_relation"]}
        for head, row in production.items()
    } == expected
    assert _duckdb_unavailable(model_document, population_document_) == expected
    assert _souffle_unavailable(model_document, population_document_) == expected
    assert _pyrel_envelope(model_document, population_document_)["unavailable"] == expected


@pytest.mark.parametrize("first_false", [False, True])
def test_p10_exact_average_post_filter_unavailability_respects_written_order(
    first_false: bool,
) -> None:
    model_document, population_document_ = document(), population_document()
    rule = model_document["fact_types"][5]["derivation_rule"]
    rule["where"] = [
        *([{"operator": "<", "left": "$mean", "right": 0}] if first_false else []),
        {"operator": "=", "left": {"fn": "mod", "args": [1, 0]}, "right": 0},
    ]
    assert semantic_validate(model_document) == []
    model = Model.model_validate(model_document)
    population = load_population_bytes(
        json.dumps(population_document_).encode(), source="avg-post-unavailable.json", model=model
    )
    expected = (
        {}
        if first_false
        else {"scenario_mean_ok": {"reason": "term:mod-zero", "source_relation": None}}
    )
    production = exact_extension_envelope(model, population)["unavailable"]
    assert {
        head: {"reason": row["reason"], "source_relation": row["source_relation"]}
        for head, row in production.items()
    } == expected
    assert _duckdb_unavailable(model_document, population_document_) == expected
    assert _souffle_unavailable(model_document, population_document_) == expected
    assert _pyrel_envelope(model_document, population_document_)["unavailable"] == expected


def test_p10_computed_head_unavailability_propagates_in_four_seats() -> None:
    model_document, population_document_ = _join_and_upper_case()
    model_document["fact_types"][1]["derivation_rule"]["head"]["count"] = {
        "fn": "mod",
        "args": ["$count", 0],
    }
    assert semantic_validate(model_document) == []
    model = Model.model_validate(model_document)
    population = load_population_bytes(
        json.dumps(population_document_).encode(), source="head-unavailable.json", model=model
    )
    expected = {
        "scenario_count": {"reason": "term:mod-zero", "source_relation": None},
        "scenario_count_total": {"reason": "term:mod-zero", "source_relation": "scenario_count"},
    }
    production = exact_extension_envelope(model, population)["unavailable"]
    assert {
        head: {"reason": row["reason"], "source_relation": row["source_relation"]}
        for head, row in production.items()
    } == expected
    assert _duckdb_unavailable(model_document, population_document_) == expected
    assert _souffle_unavailable(model_document, population_document_) == expected
    assert _pyrel_envelope(model_document, population_document_)["unavailable"] == expected


@pytest.mark.parametrize("source", ["of", "post-where"])
def test_p10_lower_aggregate_unavailability_propagates_in_all_four_seats(source: str) -> None:
    model_document, population_document_ = _join_and_upper_case(unavailable=source == "of")
    if source == "post-where":
        model_document["fact_types"][1]["derivation_rule"]["where"] = [
            {"operator": "=", "left": {"fn": "mod", "args": ["$count", 0]}, "right": 0}
        ]
    model = Model.model_validate(model_document)
    population = load_population_bytes(
        json.dumps(population_document_).encode(), source="undefined-upper.json", model=model
    )
    production = exact_extension_envelope(model, population)["unavailable"]
    expected = {
        "scenario_count": {"reason": "term:mod-zero", "source_relation": None},
        "scenario_count_total": {
            "reason": "term:mod-zero",
            "source_relation": "scenario_count",
        },
    }
    assert {
        head: {"reason": row["reason"], "source_relation": row["source_relation"]}
        for head, row in production.items()
    } == expected
    assert _duckdb_unavailable(model_document, population_document_) == expected
    assert _souffle_unavailable(model_document, population_document_) == expected
    assert _pyrel_envelope(model_document, population_document_)["unavailable"] == expected

