"""Interpret snapshot reports at the Python boundary, including failed runs."""
import json
from copy import deepcopy
from importlib.resources import files
from pathlib import Path

import pytest
from support.cli_runner import run_main

from gnd import api

CORPUS = Path(__file__).parent / "fixtures/rc4-allow-vacuous"
MODEL = CORPUS / "models/graph.orm.yaml"


@pytest.mark.parametrize(("example", "population", "admission", "version", "status"), [
    ("quoted_claims", "gap.pop.json", False, 7, "accepted"),
    ("dispatch", "seed.pop.json", False, 12, "violated"),
    ("dispatch", "seed.pop.json", True, 14, "violated"),
    ("quoted_claims", "missing.pop.json", False, 7, "invalid-input"),
])
def test_real_check_envelopes(example, population, admission, version, status):
    root = files("gnd").joinpath("examples", example)
    raw = api.check(root / "model.orm.json", root / population, admission=admission)
    original = deepcopy(raw)
    assert int(raw["schema_version"]) == version
    verdict = api.snapshot_verdict(raw)
    assert verdict["status"] == status
    assert verdict["exit_code"] == raw["exit_code"]
    assert verdict["constraints"] == raw.get("report", raw)["verdicts"]
    if status == "invalid-input":
        assert verdict["diagnostics"] and raw["counts"]["fail"] == 0
    assert raw == original


def test_wrapper_failure_and_malformed_reports(monkeypatch):
    root = files("gnd").joinpath("examples", "dispatch")
    raw = api.check(root / "model.orm.json", root / "seed.pop.json")
    outer = {**raw, "exit_code": 3, "outcome": "ill_formed"}
    assert api.snapshot_verdict(outer)["status"] == "invalid-input"
    assert api.snapshot_verdict(outer)["constraints"] == []
    assert api.snapshot_verdict({**raw, "schema_version": 99})["status"] == "unsupported-schema"
    monkeypatch.setenv("GND_DISCLOSURE", "customer")
    safe = api.snapshot_verdict(raw)
    assert all(set(row) == {"verdict"} for row in safe["constraints"])
    malformed = api.snapshot_verdict({**raw, "report": "private scalar"})
    assert malformed["status"] == "invalid-report" and "private scalar" not in str(malformed)


@pytest.mark.parametrize(("kind", "expected"), [("vacuous-only", 0), ("fail-and-vacuous", 1),
                                                ("unchecked-and-vacuous", 4)])
def test_python_cli_vacuity_parity(kind, expected):
    pop = CORPUS / "populations" / (kind + ".pop.yaml")
    raw = api.check(MODEL, pop, allow_vacuous=True)
    cli = run_main(["check", str(MODEL), str(pop), "--allow-vacuous", "--format", "json"])
    assert cli.returncode == raw["exit_code"] == expected
    assert json.loads(cli.stdout)["counts"] == raw["counts"]
    assert "vacuous" in [v["verdict"] for v in api.snapshot_verdict(raw)["constraints"]]
    if expected == 0:
        plain = api.check(MODEL, pop)
        assert plain == api.check(MODEL, pop, allow_vacuous=False)
        assert api.snapshot_verdict(plain)["status"] == "vacuous"


def test_vacuity_refuses_invalid_combinations_before_loading():
    with pytest.raises(TypeError, match="boolean"):
        api.check("missing-model", "missing-pop", allow_vacuous=1)
    for option in ("admission", "compiled_operations"):
        with pytest.raises(ValueError, match="plain snapshot"):
            api.check("missing-model", "missing-pop", allow_vacuous=True, **{option: True})


@pytest.mark.parametrize(("outcomes", "expected"), [([], "violated"), (None, "unchecked"),
                                                   ([{"id": "a"}], "accepted")])
def test_requested_inventory_grounds_outcome_coverage(tmp_path, outcomes, expected):
    model = tmp_path / "model.orm.json"
    roles = [{"role_name": "id", "object_type": "item"}]
    facts = [{"id": name, "reading": "{Item} is " + name, "roles": roles}
             for name in ("requested", "recorded")]
    rule = {"id": "needs_result", "type": "guarded", "source": "explicit", "status": "confirmed",
            "modality": "alethic", "provenance": {"user_quote": "Each request needs a result."},
            "antecedent": [{"fact_type": "requested", "bind": {"id": "$x"}}],
            "consequent": {"exists": {"atoms": [{"fact_type": "recorded", "bind": {"id": "$x"}}]}}}
    model.write_text(json.dumps({"version": 1, "model_id": "requests", "object_types": [
        {"id": "item", "name": "Item", "kind": "value", "primitive": "String"}],
        "fact_types": facts, "constraints": [rule]}))
    pop = tmp_path / "seen.json"
    rows = {"requested": [{"id": "a"}]}
    if outcomes is not None:
        rows["recorded"] = outcomes
    pop.write_text(json.dumps({"population": {"model": model.name, "source": "fixture", "covers": list(rows)},
                               "facts": rows}))
    raw = api.check(model, pop, allow_vacuous=True)
    assert api.snapshot_verdict(raw)["status"] == expected


@pytest.mark.parametrize("mode", ["internal", "customer"])
def test_null_derivation_list_in_real_report(monkeypatch, mode):
    root = files("gnd").joinpath("examples", "approvals")
    raw = api.check(root / "model.orm.yaml", root / "state.pop.yaml")
    assert raw["derivations"] is None
    monkeypatch.setenv("GND_DISCLOSURE", mode)
    assert api.snapshot_verdict(raw)["derivations"] == []


@pytest.mark.parametrize("kwarg", ["anchors", "document"])
def test_vacuity_and_anchored_options_are_mutually_exclusive(kwarg):
    with pytest.raises(ValueError, match="plain snapshot"):
        api.check("missing-model", "missing-pop", allow_vacuous=True, **{kwarg: "missing"})
