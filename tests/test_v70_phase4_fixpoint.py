from __future__ import annotations

import json
from itertools import pairwise
from pathlib import Path

from ruamel.yaml import YAML
from support.v70_phase4 import FIXTURE, _derivation, _positive, _unknown_positive, _write

from gnd import api, checker
from gnd.model import load_model
from gnd.population import load_population


def test_known_false_where_eliminates_an_opaque_candidate(tmp_path: Path) -> None:
    model, population = _unknown_positive()
    model["fact_types"][1]["derivation_rule"]["where"] = [
        {"operator": "=", "left": "$r", "right": "R2"}
    ]
    population["facts"]["inferred"] = [{"record": "R1", "item": "B"}]
    paths = _write(tmp_path, model, population)
    verdict = _derivation(api.check(*paths, admission=True))
    assert verdict["verdict"] == "fail"
    assert [row["kind"] for row in verdict["findings"]] == ["derived-extension-unsound"]

    model["fact_types"][1]["derivation_rule"]["where"][0]["left"] = "$i"
    model["fact_types"][1]["derivation_rule"]["where"][0]["right"] = "B"
    population["facts"]["inferred"].insert(0, {"record": "R0", "item": "A"})
    paths = _write(tmp_path, model, population)
    verdict = _derivation(api.check(*paths, admission=True))
    assert [row["kind"] for row in verdict["findings"]] == [
        "derived-extension-unsound", "derived-extension-unresolved"
    ]

def test_aggregate_contribution_uncertainty_preserves_other_group(tmp_path: Path) -> None:
    model, population = _unknown_positive()
    model["object_types"].append({"id": "integer", "name": "Integer", "kind": "value", "primitive": "Integer"})
    inferred = model["fact_types"][1]
    inferred["reading"] = "{Record} has count {Integer}"
    inferred["roles"][1] = {"object_type": "integer", "role_name": "count"}
    inferred["derivation_rule"]["aggregate"] = {
        "fn": "count", "of": "$i", "over": ["$i"], "as": "$count"
    }
    inferred["derivation_rule"]["head"] = {"record": "$r", "count": "$count"}
    population["facts"]["observed"].append({"record": "R1", "item": "B"})
    population["facts"]["inferred"] = [
        {"record": "R0", "count": 1}, {"record": "R1", "count": 2}
    ]
    paths = _write(tmp_path, model, population)
    verdict = _derivation(api.check(*paths, admission=True))
    assert verdict["verdict"] == "unchecked"
    assert verdict["findings"][0]["witness"] == {"record": "R1", "count": 2}

def test_a_second_clause_supplies_definite_proof(tmp_path: Path) -> None:
    model, population = _unknown_positive()
    model["fact_types"].insert(1, {
        "id": "certain", "reading": "{Record} certainly contains {Item}",
        "roles": [
            {"object_type": "record", "role_name": "record"},
            {"object_type": "item", "role_name": "item"},
        ],
    })
    original = model["fact_types"][2]["derivation_rule"]
    model["fact_types"][2]["derivation_rule"] = {
        "clauses": [original, {
            "body": [{"fact_type": "certain", "bind": {"record": "$r", "item": "$i"}}],
            "head": {"record": "$r", "item": "$i"},
        }]
    }
    population["population"]["covers"].insert(1, "certain")
    population["facts"]["certain"] = [{"record": "R1", "item": "B"}]
    population["facts"]["inferred"].append({"record": "R1", "item": "B"})
    paths = _write(tmp_path, model, population)
    assert _derivation(api.check(*paths, admission=True))["verdict"] == "pass"

def test_eval_mono_and_outcome_safe_over_an_opaque_cycle(tmp_path: Path) -> None:
    model = YAML(typ="safe").load((FIXTURE / "recursive.orm.yaml").read_text())
    population = json.loads((FIXTURE / "recursive.pop.json").read_text())
    population["facts"]["edge"][1]["target"] = {"$opaque": "unreadable-node"}
    paths = _write(tmp_path, model, population)
    loaded = load_model(paths[0])
    admitted = load_population(paths[1], model=loaded)
    growth: list[tuple[frozenset, frozenset]] = []

    def observe(head: str, must: frozenset, may: frozenset) -> None:
        if head == "reaches":
            growth.append((must, may))

    checker._evaluate_stratified_extensions(
        loaded, checker._base_relations(loaded, admitted), observe_partial=observe
    )
    assert len(growth) > 2
    assert all(must <= may for must, may in growth)
    assert all(before_must <= after_must and before_may <= after_may
               for (before_must, before_may), (after_must, after_may)
               in pairwise(growth))
    assert _derivation(api.check(*paths, admission=True))["reason_code"] == "derived-unknown"
    population["facts"]["edge"].append({"source": "X", "target": {"$opaque": "another"}})
    paths = _write(tmp_path, model, population)
    assert _derivation(api.check(*paths, admission=True))["reason_code"] == "derived-unknown"

def test_identical_marker_labels_do_not_prove_a_join(tmp_path: Path) -> None:
    model, population = _positive()
    model["fact_types"].insert(1, {
        "id": "second", "reading": "{Record} also contains {Item}",
        "roles": [
            {"object_type": "record", "role_name": "record"},
            {"object_type": "item", "role_name": "item"},
        ],
    })
    model["fact_types"][2]["derivation_rule"]["body"].append({
        "fact_type": "second", "bind": {"record": "$r", "item": "$i"}
    })
    unknown = {"record": "R1", "item": {"$opaque": "same-label"}}
    population["population"]["covers"].append("second")
    population["facts"]["observed"] = [unknown]
    population["facts"]["second"] = [unknown]
    population["facts"]["inferred"] = [{"record": "R1", "item": "B"}]
    verdict = _derivation(api.check(*_write(tmp_path, model, population), admission=True))
    assert verdict["verdict"] == "unchecked"
    assert verdict["reason_code"] == "derived-unknown"
