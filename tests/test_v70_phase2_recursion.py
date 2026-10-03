from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from gnd.api import transition
from gnd.checker import band, check, structured_extension_view
from gnd.model import ModelValidationError, load_model
from gnd.population import load_population
from gnd.transition import model_digest, operations_digest

FIXTURE = Path(__file__).parent / "fixtures/v70-phase2"

CASES = json.loads((FIXTURE / "cases.json").read_text())["cases"]

ANSWERS = json.loads((FIXTURE / "answers.json").read_text())["cases"]

def _model(variant: str) -> dict:
    doc = YAML(typ="safe").load((FIXTURE / "model.orm.yaml").read_text())
    facts = {row["id"]: row for row in doc["fact_types"]}
    reach = facts["reaches"]
    rule = reach["derivation_rule"]
    if variant == "base":
        pass
    elif variant == "legacy_sugar":
        reach["derivation_rule"] = copy.deepcopy(rule["clauses"][0])
    elif variant == "root_head":
        rule["head"] = copy.deepcopy(rule["clauses"][0]["head"])
        for clause in rule["clauses"]:
            clause.pop("head")
    elif variant == "root_one_clause":
        rule["head"] = copy.deepcopy(rule["clauses"][0]["head"])
        rule["clauses"] = [rule["clauses"][0]]
        rule["clauses"][0].pop("head")
    elif variant == "no_seed_clause":
        rule["clauses"] = [rule["clauses"][1]]
    elif variant == "empty_clauses":
        rule["clauses"] = []
    elif variant == "mixed_head":
        rule["head"] = copy.deepcopy(rule["clauses"][0]["head"])
    elif variant == "mixed_body":
        rule["body"] = copy.deepcopy(rule["clauses"][0]["body"])
    elif variant == "unknown_clause_key":
        rule["clauses"][1]["or"] = []
    elif variant == "malformed_second_body":
        rule["clauses"][1]["body"] = "not an atom array"
    elif variant == "unsafe_second_head":
        rule["clauses"][1]["head"]["target"] = "$ghost"
    elif variant == "unsafe_second_negate":
        rule["clauses"][1]["negate"] = [{"fact_type": "blocked", "bind": {"target": "$ghost"}}]
    elif variant == "duplicate_clause":
        rule["clauses"].append(copy.deepcopy(rule["clauses"][0]))
    elif variant in {"exact_recursive", "exact_recursive_false", "exact_undefined"}:
        right = 2 if variant == "exact_recursive" else 3
        left: object = {"fn": "add", "args": [1, 1]}
        if variant == "exact_undefined":
            left = {"fn": "mod", "args": [1, 0]}
            right = 0
        rule["clauses"][1]["where"] = [{"operator": "=", "left": left, "right": right}]
    elif variant == "mutual_positive":
        doc["fact_types"].append(
            {
                "id": "same_reach",
                "reading": "{Node} has the same reach to {Node}",
                "roles": copy.deepcopy(reach["roles"]),
                "derivation": "derived",
                "derivation_rule": {
                    "body": [{"fact_type": "reaches", "bind": {"source": "$x", "target": "$y"}}],
                    "head": {"source": "$x", "target": "$y"},
                },
            }
        )
        rule["clauses"].append(
            {
                "body": [{"fact_type": "same_reach", "bind": {"source": "$x", "target": "$y"}}],
                "head": {"source": "$x", "target": "$y"},
            }
        )
    elif variant == "negative_self":
        facts["open_reach"]["derivation_rule"]["negate"] = [
            {"fact_type": "open_reach", "bind": {"source": "$x", "target": "$y"}}
        ]
    elif variant == "negative_mutual":
        rule["clauses"][1]["negate"] = [
            {"fact_type": "open_reach", "bind": {"source": "$x", "target": "$y"}}
        ]
        doc["fact_types"].append(
            {
                "id": "reach_notice",
                "reading": "{Node} has a reach notice for {Node}",
                "roles": copy.deepcopy(reach["roles"]),
                "derivation": "derived",
                "derivation_rule": {
                    "body": [{"fact_type": "reaches", "bind": {"source": "$x", "target": "$y"}}],
                    "head": {"source": "$x", "target": "$y"},
                },
            }
        )
    elif variant == "mixed_polarity":
        rule["clauses"][1]["body"].append(
            {
                "fact_type": "open_reach",
                "bind": {"source": "$x", "target": "$y"},
            }
        )
        rule["clauses"][1]["negate"] = [
            {"fact_type": "open_reach", "bind": {"source": "$x", "target": "$y"}}
        ]
    elif variant == "aggregate_lower":
        doc["object_types"].append(
            {"id": "number", "name": "Number", "kind": "value", "primitive": "Integer"}
        )
        doc["fact_types"].append(
            {
                "id": "reach_count",
                "reading": "{Node} has {Number} reach paths",
                "roles": [
                    {"object_type": "node", "role_name": "source"},
                    {"object_type": "number", "role_name": "count"},
                ],
                "derivation": "derived",
                "derivation_rule": {
                    "body": [{"fact_type": "reaches", "bind": {"source": "$x", "target": "$y"}}],
                    "aggregate": {"fn": "count", "of": "$y", "over": ["$y"], "as": "$count"},
                    "head": {"source": "$x", "count": "$count"},
                },
            }
        )
    elif variant in {"root_aggregate", "root_aggregate_where"}:
        doc["object_types"].append(
            {"id": "number", "name": "Number", "kind": "value", "primitive": "Integer"}
        )
        aggregate_rule = {
            "clauses": [
                {"body": [{"fact_type": "edge", "bind": {"source": "A", "target": "$y"}}]},
                {"body": [{"fact_type": "edge", "bind": {"source": "B", "target": "$y"}}]},
            ],
            "aggregate": {"fn": "count", "of": "$y", "over": ["$y"], "as": "$count"},
            "head": {"label": "branch", "count": "$count"},
        }
        if variant == "root_aggregate_where":
            aggregate_rule["where"] = [{"operator": "<", "left": "$count", "right": 2}]
        doc["fact_types"].append(
            {
                "id": "branch_count",
                "reading": "{Node} has branch count {Number}",
                "roles": [
                    {"object_type": "node", "role_name": "label"},
                    {"object_type": "number", "role_name": "count"},
                ],
                "derivation": "derived",
                "derivation_rule": aggregate_rule,
            }
        )
    elif variant == "aggregate_self":
        doc["object_types"].append(
            {"id": "number", "name": "Number", "kind": "value", "primitive": "Integer"}
        )
        doc["fact_types"].append(
            {
                "id": "reach_count",
                "reading": "{Node} has {Number} reach paths",
                "roles": [
                    {"object_type": "node", "role_name": "source"},
                    {"object_type": "number", "role_name": "count"},
                ],
                "derivation": "derived",
                "derivation_rule": {
                    "body": [{"fact_type": "reach_count", "bind": {"source": "$x", "count": "$n"}}],
                    "aggregate": {"fn": "count", "of": "$n", "over": ["$n"], "as": "$count"},
                    "head": {"source": "$x", "count": "$count"},
                },
            }
        )
    elif variant == "value_invention":
        doc["object_types"].append(
            {"id": "number", "name": "Number", "kind": "value", "primitive": "Integer"}
        )
        doc["fact_types"].extend(
            [
                {
                    "id": "seed_n",
                    "reading": "{Number} is a seed",
                    "roles": [{"object_type": "number", "role_name": "n"}],
                },
                {
                    "id": "closure_n",
                    "reading": "{Number} is in the numeric closure",
                    "roles": [{"object_type": "number", "role_name": "n"}],
                    "derivation": "derived",
                    "derivation_rule": {
                        "clauses": [
                            {
                                "body": [{"fact_type": "seed_n", "bind": {"n": "$n"}}],
                                "head": {"n": "$n"},
                            },
                            {
                                "body": [{"fact_type": "closure_n", "bind": {"n": "$n"}}],
                                "head": {"n": {"fn": "add", "args": ["$n", 1]}},
                            },
                        ]
                    },
                },
            ]
        )
    elif variant == "semiderived_surplus":
        reach["derivation"] = "semiderived"
    else:
        raise AssertionError(f"unknown model variant {variant}")
    return doc

def _population(variant: str, *, base: str = "pre.pop.json") -> dict:
    doc = json.loads((FIXTURE / base).read_text())
    facts = doc["facts"]
    if variant == "base":
        pass
    elif variant == "legacy_direct":
        facts["reaches"] = [
            row for row in facts["reaches"] if row != {"source": "A", "target": "C"}
        ]
    elif variant == "mutual":
        facts["same_reach"] = copy.deepcopy(facts["reaches"])
        doc["population"]["covers"].append("same_reach")
    elif variant == "missing_transitive":
        facts["reaches"] = [
            row for row in facts["reaches"] if row != {"source": "A", "target": "C"}
        ]
    elif variant in {"extra_claim", "semiderived_surplus"}:
        facts["reaches"].append({"source": "X", "target": "Y"})
    elif variant == "upper_surplus_claim":
        facts["reaches"].append({"source": "X", "target": "Y"})
        facts["open_reach"].append({"source": "X", "target": "Y"})
    elif variant == "uncovered_reaches":
        doc["population"]["covers"].remove("reaches")
        facts.pop("reaches")
    elif variant == "unblocked":
        facts["blocked"] = []
        facts["open_reach"] = copy.deepcopy(facts["reaches"])
    elif variant in {"branch_one", "branch_two"}:
        facts["branch_count"] = [{"label": "branch", "count": 1 if variant == "branch_one" else 2}]
        doc["population"]["covers"].append("branch_count")
    else:
        raise AssertionError(f"unknown population variant {variant}")
    return doc

def _write_model(root: Path, variant: str) -> Path:
    path = root / "model.orm.yaml"
    with path.open("w") as stream:
        YAML().dump(_model(variant), stream)
    return path

def _write_population(
    root: Path, variant: str, *, name: str = "pre.pop.json", base: str = "pre.pop.json"
) -> Path:
    path = root / name
    path.write_text(json.dumps(_population(variant, base=base), indent=2) + "\n")
    return path

def _walk_rows(kind: str) -> list[dict]:
    template = json.loads((FIXTURE / "walk.steps.template.json").read_text())["steps"]
    if kind == "clean" or kind == "missing_coverage":
        return template
    if kind == "early_visit":
        return [template[1], template[0], template[2]]
    if kind == "retract_only":
        return [template[2]]
    if kind == "retract_then_visit":
        return [template[2], {"op": "visit", "bindings": {"source": "A", "target": "C"}}]
    if kind == "mutual_refresh":
        return [template[0], template[2]]
    if kind == "no_touch":
        return [{"op": "visit", "bindings": {"source": "A", "target": "C"}}]
    raise AssertionError(f"unknown walk variant {kind}")

def _write_steps(root: Path, model, kind: str) -> Path:
    path = root / "walk.steps.json"
    path.write_text(
        json.dumps(
            {
                "steps_schema": 1,
                "model": "model.orm.yaml",
                "model_digest": model_digest(model),
                "operations_digest": operations_digest(model.operations),
                "steps": _walk_rows(kind),
            },
            indent=2,
        )
        + "\n"
    )
    return path

@pytest.mark.parametrize(
    "row",
    [row for row in CASES if row["lane"] not in {"consumer", "parity", "scaling", "docs", "pins"}],
    ids=lambda row: row["id"],
)
def test_owner_answer_case(row: dict, tmp_path: Path) -> None:
    ident = row["id"]
    expected = ANSWERS[ident]
    model_path = _write_model(tmp_path, row["variant"])
    if row["lane"] == "validate":
        if expected["exit"] == 0:
            load_model(model_path)
            return
        with pytest.raises(ModelValidationError) as refusal:
            load_model(model_path)
        issues = refusal.value.issues
        assert expected["rule"] in {issue.rule_id for issue in issues}, ident
        matching = [issue for issue in issues if issue.rule_id == expected["rule"]]
        if "site" in expected:
            assert any(expected["site"] in f"{issue.path} {issue.message}" for issue in matching), (
                ident
            )
        if "cycle" in expected:
            joined = " ".join(issue.message for issue in matching)
            assert all(member in joined for member in expected["cycle"]), ident
            if "edge" in expected:
                assert expected["edge"] in joined, ident
        if "not_cycle_member" in expected:
            assert expected["not_cycle_member"] not in " ".join(
                issue.message for issue in matching
            ), ident
        return

    model = load_model(model_path)
    population_path = _write_population(tmp_path, row.get("population", "base"))
    population = load_population(population_path, model=model)
    if row["lane"] == "check":
        report = check(model, population)
        assert band(report) == expected["exit"], ident
        if "rows" in expected:
            view = structured_extension_view(model, population)
            roles = expected.get("roles", ["source", "target"])
            actual = [[fact[role] for role in roles] for fact in view.facts[expected["head"]]]
            assert sorted(actual) == sorted(expected.get("rows", actual)), ident
        if "finding" in expected:
            witnesses = [
                finding.witness
                for verdict in report.derivations
                if verdict.fact_type == expected["head"]
                for finding in verdict.findings
                if finding.kind == expected["finding"]
            ]
            assert witnesses, ident
            if "witness" in expected:
                assert any(
                    [witness[role] for role in expected.get("roles", ["source", "target"])]
                    == expected["witness"]
                    for witness in witnesses
                ), ident
        if "reason" in expected:
            assert any(
                verdict.fact_type == expected["head"] and verdict.reason_code == expected["reason"]
                for verdict in report.derivations
            )
        if "excluded_surplus" in expected:
            upper = view.facts[expected["head"]]
            assert not any(
                [fact["source"], fact["target"]] == expected["excluded_surplus"] for fact in upper
            ), ident
        return

    assert row["lane"] == "walk"
    kind = row["walk"]
    if kind == "missing_coverage":
        doc = json.loads(population_path.read_text())
        doc["population"]["covers"].remove("edge")
        population_path.write_text(json.dumps(doc, indent=2) + "\n")
    steps_path = _write_steps(tmp_path, model, kind)
    post_path = None
    if kind == "clean":
        post_path = _write_population(tmp_path, "base", name="post.pop.json", base="post.pop.json")
    payload = transition(model_path, population_path, steps_path, post_path, unredacted=True)
    assert payload["exit_code"] == expected["exit"], ident
    if "rule" in expected:
        assert expected["rule"] in {issue["rule_id"] for issue in payload["issues"]}
    if kind == "early_visit":
        first = payload["transition"]["steps"][0]
        assert any(
            item["kind"] == expected["kind"] and item["verdict"] == expected["verdict"]
            for item in first["verdicts"]
        ), ident
    if kind == "retract_then_visit":
        second = payload["transition"]["steps"][1]
        assert any(
            item["kind"] == expected["kind"] and item["verdict"] == expected["verdict"]
            for item in second["verdicts"]
        ), ident
    if kind == "clean":
        steps = payload["transition"]["steps"]
        reach_change = next(
            item for item in steps[0]["derived_changes"] if item["fact_type"] == "reaches"
        )
        assert [[item["source"], item["target"]] for item in reach_change["added"]] == expected[
            "step_1_added"
        ]
        reach_change = next(
            item for item in steps[2]["derived_changes"] if item["fact_type"] == "reaches"
        )
        assert [[item["source"], item["target"]] for item in reach_change["removed"]] == expected[
            "step_3_removed"
        ]
    if kind == "no_touch":
        assert not payload["transition"]["steps"][0].get("derived_changes")
    if kind == "retract_only":
        reach_change = next(
            item
            for item in payload["transition"]["steps"][0]["derived_changes"]
            if item["fact_type"] == expected["head"]
        )
        removed = sorted([row["source"], row["target"]] for row in reach_change["removed"])
        assert removed == [["A", "C"], ["B", "C"]], ident
    if kind == "mutual_refresh":
        first, second = payload["transition"]["steps"]
        for step, change_key in ((first, "added"), (second, "removed")):
            changed = {item["fact_type"]: item for item in step["derived_changes"]}
            assert {"reaches", "same_reach"} <= set(changed), ident
            assert changed["reaches"][change_key] == changed["same_reach"][change_key]


def test_old_grammar_surrogate_loads_every_non_recursive_field(tmp_path: Path) -> None:
    """Replace only the future rule, then exercise the existing model/pop loaders."""
    from gnd.model import load_model
    from gnd.population import load_population

    model = YAML(typ="safe").load((FIXTURE / "model.orm.yaml").read_text())
    replacement = {
        "body": [{"fact_type": "edge", "bind": {"source": "$x", "target": "$y"}}],
        "head": {"source": "$x", "target": "$y"},
    }
    next(f for f in model["fact_types"] if f["id"] == "reaches")["derivation_rule"] = replacement
    path = tmp_path / "model.orm.yaml"
    with path.open("w") as stream:
        YAML().dump(model, stream)
    loaded = load_model(path)
    for name in ("pre.pop.json", "post.pop.json"):
        population = load_population(FIXTURE / name, model=loaded)
        assert set(population.facts) == {fact["id"] for fact in model["fact_types"]}
