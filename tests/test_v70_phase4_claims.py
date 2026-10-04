from __future__ import annotations

import json
from pathlib import Path

import pytest
from ruamel.yaml import YAML
from support.v70_phase4 import _derivation, _positive, _unknown_positive, _write

from gnd import api


def test_possible_claim_is_resolved_by_definite_proof_and_reversed_by_removal(tmp_path: Path) -> None:
    model, population = _unknown_positive()
    population["facts"]["inferred"].append({"record": "R1", "item": "B"})
    paths = _write(tmp_path, model, population)
    assert _derivation(api.check(*paths, admission=True))["reason_code"] == "derived-unknown"

    population["facts"]["observed"].append({"record": "R1", "item": "B"})
    paths = _write(tmp_path, model, population)
    assert _derivation(api.check(*paths, admission=True))["verdict"] == "pass"

    population["facts"]["observed"] = [row for row in population["facts"]["observed"]
                                         if row["record"] != "R1"]
    paths = _write(tmp_path, model, population)
    assert [row["kind"] for row in _derivation(api.check(*paths, admission=True))["findings"]] == [
        "derived-extension-unsound"
    ]

def test_semiderived_missing_is_definite_but_out_surplus_is_legal(tmp_path: Path) -> None:
    model, population = _positive()
    model["fact_types"][1]["derivation"] = "semiderived"
    population["facts"]["inferred"] = []
    paths = _write(tmp_path, model, population)
    assert [row["kind"] for row in _derivation(api.check(*paths, admission=True))["findings"]] == [
        "derived-extension-incomplete"
    ]
    population["facts"]["inferred"] = [
        {"record": "R0", "item": "A"}, {"record": "R9", "item": "Z"}
    ]
    paths = _write(tmp_path, model, population)
    assert _derivation(api.check(*paths, admission=True))["verdict"] == "pass"

def test_uncovered_derivation_keeps_its_closed_reason(tmp_path: Path) -> None:
    model, population = _unknown_positive()
    population["population"]["covers"].remove("inferred")
    population["facts"]["inferred"] = []
    paths = _write(tmp_path, model, population)
    assert _derivation(api.check(*paths, admission=True))["reason_code"] == "derivation-not-covered"

def test_exact_term_unavailability_is_distinct_from_unknown(tmp_path: Path) -> None:
    root = Path(__file__).parent / "fixtures/v62-phase3"
    model = YAML(typ="safe").load((root / "models/exact-terms.orm.yaml").read_text())
    population = YAML(typ="safe").load((root / "populations/term-clean.pop.yaml").read_text())
    population["format_version"] = 2
    population["facts"]["input"].extend([
        {"ticket": "bad", "value": 10, "divisor": 0},
        {"ticket": {"$opaque": "unreadable-ticket"}, "value": 5, "divisor": 1},
    ])
    paths = _write(tmp_path, model, population)
    payload = api.check(*paths, admission=True)
    assert payload["exit_code"] == 4
    assert {row["reason_code"] for row in payload["derivations"]} == {"term:mod-zero"}

def test_loader_admitted_opaque_claim_has_a_noninternal_verdict(tmp_path: Path) -> None:
    model, population = _positive()
    population["facts"]["inferred"][0]["item"] = {"$opaque": "claimed-unreadable"}
    payload = api.check(*_write(tmp_path, model, population), admission=True)
    assert payload["exit_code"] != 70
    assert _derivation(payload)["verdict"] == "unchecked"
    assert "$opaque" not in json.dumps(_derivation(payload))
    assert "claimed-unreadable" not in json.dumps(_derivation(payload))

@pytest.mark.parametrize("derivation", ["derived", "semiderived"])
@pytest.mark.parametrize("membership", ["in", "out", "unknown"])
@pytest.mark.parametrize("claimed", [True, False])
def test_claim_table_cells(
    tmp_path: Path, derivation: str, membership: str, claimed: bool,
) -> None:
    model, population = _positive()
    model["fact_types"][1]["derivation"] = derivation
    if membership == "in":
        if not claimed:
            population["facts"]["inferred"] = []
    elif membership == "out":
        if claimed:
            population["facts"]["inferred"].append({"record": "R9", "item": "Z"})
    else:
        population["facts"]["observed"].append({
            "record": "R1", "item": {"$opaque": "unknown"}
        })
        if claimed:
            population["facts"]["inferred"].append({"record": "R1", "item": "B"})
    verdict = _derivation(api.check(*_write(tmp_path, model, population), admission=True))
    expected = {
        ("in", True): ("pass", []),
        ("in", False): ("fail", ["derived-extension-incomplete"]),
        ("out", False): ("pass", []),
        ("unknown", True): ("unchecked", ["derived-extension-unresolved"]),
        ("unknown", False): ("pass", []),
    }
    if membership == "out" and claimed:
        expected_value = (("fail", ["derived-extension-unsound"])
                          if derivation == "derived" else ("pass", []))
    else:
        expected_value = expected[(membership, claimed)]
    assert (verdict["verdict"], [row["kind"] for row in verdict["findings"]]) == expected_value
