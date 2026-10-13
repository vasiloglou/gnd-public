"""Frozen hand-narrated policy controls, separately from native execution."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from gnd.api import check

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests/fixtures/pyrel_applications"
MATRIX = json.loads((CORPUS / "matrix.json").read_text())
ANSWERS = json.loads((CORPUS / "answers.json").read_text())


def test_matrix_exhausts_exact_models_and_controls():
    actual = set()
    for name in MATRIX["models"]:
        model = ROOT / "src/gnd/examples" / name
        doc = json.loads(model.read_text())
        entries = [f"fact_types[{f['id']}].constraints[{i}]"
                   for f in doc["fact_types"] for i, _ in enumerate(f.get("constraints", []))]
        entries += [f"constraints[{i}]" for i, _ in enumerate(doc.get("constraints", []))]
        entries += ["derivation:" + f["id"] for f in doc["fact_types"]
                    if f.get("derivation") == "derived"]
        actual.update((name, ref) for ref in entries)
    assert actual == {(r["model"], r["ref"]) for r in MATRIX["obligations"]}
    assert len(actual) == MATRIX["obligation_count"] == 61
    assert len(MATRIX["cases"]) == MATRIX["case_count"] == 124
    assert set(ANSWERS) == set(MATRIX["cases"])
    for row in MATRIX["obligations"]:
        model = ROOT / "src/gnd/examples" / row["model"]
        assert hashlib.sha256(model.read_bytes()).hexdigest() == row["model_sha256"]
        assert ANSWERS[row["positive"]]["expected"] == "pass"
        assert ANSWERS[row["negative"]]["expected"] in {"fail", "warning"}
        assert MATRIX["cases"][row["negative"]]["story"]


@pytest.mark.parametrize("name", MATRIX["cases"])
def test_frozen_story_matches_public_gnd_report(name):
    case, answer = MATRIX["cases"][name], ANSWERS[name]
    report = check(ROOT / case["model"], ROOT / case["population"], unredacted=True)
    observed = {r["constraint_ref"]: r["verdict"] for r in report["verdicts"]}
    observed.update({r["derivation_ref"]: r["verdict"] for r in report.get("derivations") or []})
    assert observed[case["target"]] == case["expected"]
    assert observed == answer["observed_gnd_verdicts"]
    assert report["exit_code"] == answer["observed_gnd_exit"]


def test_declared_consumer_paths_and_runtime_copies_exist():
    for consumer in MATRIX["consumers"]:
        assert (ROOT / consumer).exists(), consumer
    packaged = ROOT / "src/gnd/examples/release_governance/runtime-environment"
    for name in ["pyproject.toml", "uv.lock"]:
        assert (ROOT / "tutorials/runtimes" / name).read_bytes() == (packaged / name).read_bytes()


def test_inventory_checker_rejects_omitted_obligation(monkeypatch):
    monkeypatch.setitem(MATRIX, "obligations", MATRIX["obligations"][:-1])
    with pytest.raises(AssertionError):
        test_matrix_exhausts_exact_models_and_controls()


def test_inventory_checker_rejects_changed_model_identity(monkeypatch):
    changed = [dict(row) for row in MATRIX["obligations"]]
    changed[0]["model_sha256"] = "0" * 64
    monkeypatch.setitem(MATRIX, "obligations", changed)
    with pytest.raises(AssertionError):
        test_matrix_exhausts_exact_models_and_controls()
