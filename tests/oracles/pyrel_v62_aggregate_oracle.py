# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["relationalai==1.30.1"]
# ///
"""Independent PyRel compiler for the approved Phase 4 aggregate fragment."""

from __future__ import annotations

import json
import operator
import os
from importlib.metadata import version
from pathlib import Path
from typing import Any

from relationalai.config import Config
from relationalai.semantics import (
    Int,
    Model,
    String,
)
from relationalai.semantics import (
    count as rai_count,
)
from relationalai.semantics import (
    max as rai_max,
)
from relationalai.semantics import (
    min as rai_min,
)
from relationalai.semantics import (
    sum as rai_sum,
)
from relationalai.semantics.frontend.base import Field


def _rules(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        fact["id"]: fact["derivation_rule"]
        for fact in document["fact_types"]
        if isinstance(fact.get("derivation_rule"), dict)
        and isinstance(fact["derivation_rule"].get("aggregate"), dict)
    }


def _rule_order(document: dict[str, Any]) -> list[str]:
    rules = _rules(document)
    ordered: list[str] = []
    visiting: set[str] = set()

    def visit(head: str) -> None:
        if head in ordered:
            return
        assert head not in visiting, "PyRel aggregate parity program is cyclic"
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


def _term(term: object, refs: dict[str, Any]) -> Any:
    if isinstance(term, str) and term.startswith("$"):
        return refs[term[1:]]
    if not isinstance(term, dict):
        return term
    args = [_term(arg, refs) for arg in term["args"]]
    function = term["fn"]
    if function == "mod":
        return args[0] % args[1]
    if function == "neg":
        return -args[0]
    if function == "abs":
        return abs(args[0])
    if function == "add":
        return args[0] + args[1]
    if function == "sub":
        return args[0] - args[1]
    if function == "mul":
        return args[0] * args[1]
    raise AssertionError(f"unsupported PyRel parity term: {function}")


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


def _comparison_predicate(comparison: dict[str, Any], refs: dict[str, Any]) -> Any:
    return {
        "<": operator.lt,
        "<=": operator.le,
        "=": operator.eq,
        "!=": operator.ne,
        ">=": operator.ge,
        ">": operator.gt,
    }[comparison["operator"]](_term(comparison["left"], refs), _term(comparison["right"], refs))


def _rational_term(
    term: object, refs: dict[str, Any], aggregate_name: str, numerator: Any, denominator: Any
) -> tuple[Any, Any]:
    if term == f"${aggregate_name}":
        return numerator, denominator
    if type(term) is float:
        return term.as_integer_ratio()
    if not isinstance(term, dict):
        return _term(term, refs), 1
    if term["fn"] == "mod":
        return _term(term, refs), 1
    parts = [
        _rational_term(arg, refs, aggregate_name, numerator, denominator) for arg in term["args"]
    ]
    function = term["fn"]
    if function == "neg":
        return -parts[0][0], parts[0][1]
    if function == "abs":
        return abs(parts[0][0]), parts[0][1]
    left_num, left_den = parts[0]
    right_num, right_den = parts[1]
    if function == "add":
        return left_num * right_den + right_num * left_den, left_den * right_den
    if function == "sub":
        return left_num * right_den - right_num * left_den, left_den * right_den
    if function == "mul":
        return left_num * right_num, left_den * right_den
    raise AssertionError(f"unsupported rational term: {function}")


def _average_predicate(
    comparison: dict[str, Any],
    refs: dict[str, Any],
    aggregate_name: str,
    numerator: Any,
    denominator: Any,
) -> Any:
    left_num, left_den = _rational_term(
        comparison["left"], refs, aggregate_name, numerator, denominator
    )
    right_num, right_den = _rational_term(
        comparison["right"], refs, aggregate_name, numerator, denominator
    )
    return {
        "<": operator.lt,
        "<=": operator.le,
        "=": operator.eq,
        "!=": operator.ne,
        ">=": operator.ge,
        ">": operator.gt,
    }[comparison["operator"]](left_num * right_den, right_num * left_den)


def _denominator_is_zero_for_survivors(
    query: Any,
    preceding: list[Any],
    denominator_term: object,
    refs: dict[str, Any],
    group_refs: list[Any],
) -> bool:
    surviving = query.where(*preceding)
    if surviving.select(*group_refs).to_df().empty:
        return False
    predicate = _term(denominator_term, refs) == 0
    if isinstance(predicate, bool):
        return predicate
    return not surviving.where(predicate).select(*group_refs).to_df().empty


def _compile(
    document: dict[str, Any], population: dict[str, Any], analyses: dict[str, list[str]]
) -> tuple[dict[str, list[dict]], dict[str, dict[str, str]]]:
    facts = {fact["id"]: fact for fact in document["fact_types"]}
    primitives = {row["id"]: row["primitive"] for row in document["object_types"]}
    rules = _rules(document)
    source_ids = {
        atom["fact_type"]
        for rule in rules.values()
        for atom in rule["body"]
        if atom["fact_type"] not in rules
    }
    model = Model(
        "gnd_v62_phase4_aggregate_parity",
        config=Config(
            connections={"local": {"type": "duckdb", "path": ":memory:"}},
            default_connection="local",
            deployment={"schema": "gnd_v62_phase4_aggregate", "auto_deploy": True},
        ),
    )
    sources = {}
    for source_id in sorted(source_ids):
        roles = facts[source_id]["roles"]
        relationship = model.Relationship(
            fields=[
                Field(
                    role["role_name"],
                    Int if primitives[role["object_type"]] == "Integer" else String,
                )
                for role in roles
            ],
            short_name=source_id,
        )
        sources[source_id] = relationship
        model.define(
            *(
                relationship(*(row[role["role_name"]] for role in roles))
                for row in population["facts"].get(source_id, [])
            )
        )

    results: dict[str, list[dict]] = {}
    unavailable: dict[str, dict[str, str]] = {}
    functions = {"count": rai_count, "sum": rai_sum, "min": rai_min, "max": rai_max}
    for head_id in _rule_order(document):
        rule = rules[head_id]
        if rule.get("negate"):
            raise AssertionError("unsupported PyRel parity body")
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
        variable_primitives: dict[str, str] = {}
        for atom in rule["body"]:
            source_roles = {role["role_name"]: role for role in facts[atom["fact_type"]]["roles"]}
            for role_name, term in atom["bind"].items():
                variable_primitives[term[1:]] = primitives[source_roles[role_name]["object_type"]]
        refs = {
            name: (Int.ref() if primitive == "Integer" else String.ref())
            for name, primitive in variable_primitives.items()
        }
        body_calls = []
        for atom in rule["body"]:
            source_id = atom["fact_type"]
            args = [refs[atom["bind"][role["role_name"]][1:]] for role in facts[source_id]["roles"]]
            body_calls.append(sources[source_id](*args))
        group_names = tuple(analyses[head_id])
        group_refs = [refs[name] for name in group_names]
        aggregate_args = [
            *(refs[item[1:]] for item in rule["aggregate"]["over"]),
            _term(rule["aggregate"]["of"], refs),
        ]
        function = rule["aggregate"]["fn"]
        query = model.where(*body_calls)
        has_zero_divisor = False
        for denominator in _mod_denominators(rule["aggregate"]["of"]):
            predicate = _term(denominator, refs) == 0
            if isinstance(predicate, bool):
                if not predicate:
                    continue
                invalid = query.select(*group_refs).to_df()
            else:
                invalid = model.where(*body_calls, predicate).select(*group_refs).to_df()
            has_zero_divisor |= not invalid.empty
        if has_zero_divisor:
            unavailable[head_id] = {"reason": "term:mod-zero", "source_relation": None}
            continue
        if function == "avg":
            numerator = rai_sum(*aggregate_args).per(*group_refs)
            denominator = rai_count(*aggregate_args).per(*group_refs)
            average_refs = {name: ref for name, ref in zip(group_names, group_refs, strict=True)}
            post_refs = {
                **average_refs,
                rule["aggregate"]["as"][1:]: numerator / denominator,
            }
            if any(
                _denominator_is_zero_for_survivors(
                    query,
                    [
                        _average_predicate(
                            item,
                            average_refs,
                            rule["aggregate"]["as"][1:],
                            numerator,
                            denominator,
                        )
                        for item in preceding
                    ],
                    denominator_term,
                    post_refs,
                    group_refs,
                )
                for preceding, denominator_term in [
                    *_postwhere_denominators(rule),
                    *_head_denominators(rule),
                ]
            ):
                unavailable[head_id] = {"reason": "term:mod-zero", "source_relation": None}
                continue
            predicates = []
            for comparison in rule.get("where") or []:
                if predicates and query.where(*predicates).select(*group_refs).to_df().empty:
                    break
                predicates.append(
                    _average_predicate(
                        comparison,
                        average_refs,
                        rule["aggregate"]["as"][1:],
                        numerator,
                        denominator,
                    )
                )
            projection_refs = average_refs
        else:
            aggregate_value = functions[function](*aggregate_args).per(*group_refs)
            comparison_refs = {
                **{name: ref for name, ref in zip(group_names, group_refs, strict=True)},
                rule["aggregate"]["as"][1:]: aggregate_value,
            }
            if any(
                _denominator_is_zero_for_survivors(
                    query,
                    [_comparison_predicate(item, comparison_refs) for item in preceding],
                    denominator_term,
                    comparison_refs,
                    group_refs,
                )
                for preceding, denominator_term in [
                    *_postwhere_denominators(rule),
                    *_head_denominators(rule),
                ]
            ):
                unavailable[head_id] = {"reason": "term:mod-zero", "source_relation": None}
                continue
            predicates = []
            for comparison in rule.get("where") or []:
                if predicates and query.where(*predicates).select(*group_refs).to_df().empty:
                    break
                predicates.append(_comparison_predicate(comparison, comparison_refs))
            projection_refs = comparison_refs
        head_roles = facts[head_id]["roles"]
        head_values = [
            _term(rule["head"][role["role_name"]], projection_refs) for role in head_roles
        ]
        frame = query.where(*predicates).select(*head_values).to_df()
        rows = []
        for values in frame.itertuples(index=False, name=None):
            row = {}
            for role, value in zip(head_roles, values, strict=True):
                row[role["role_name"]] = (
                    int(value) if primitives[role["object_type"]] == "Integer" else str(value)
                )
            rows.append(row)
        names = [role["role_name"] for role in facts[head_id]["roles"]]
        results[head_id] = sorted(rows, key=lambda row: tuple(row[name] for name in names))
        head_roles = facts[head_id]["roles"]
        relationship = model.Relationship(
            fields=[
                Field(
                    role["role_name"],
                    Int if primitives[role["object_type"]] == "Integer" else String,
                )
                for role in head_roles
            ],
            short_name=head_id,
        )
        sources[head_id] = relationship
        model.define(
            *(
                relationship(*(row[role["role_name"]] for role in head_roles))
                for row in results[head_id]
            )
        )
    return results, unavailable


def main() -> None:
    document = json.loads(os.environ["GND_AGG_MODEL"])
    population = json.loads(os.environ["GND_AGG_POPULATION"])
    analyses = json.loads(os.environ["GND_AGG_ANALYSIS"])
    relations, unavailable = _compile(document, population, analyses)
    output = {
        "schema_version": 1,
        "backend": "pyrel",
        "version": version("relationalai"),
        "relations": relations,
        "unavailable": unavailable,
    }
    Path(os.environ["GND_AGG_OUTPUT"]).write_text(
        json.dumps(output, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
