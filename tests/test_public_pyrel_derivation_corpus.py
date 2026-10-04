"""Original complete-corpus dirty controls and manual/current runtime checks."""
from __future__ import annotations

import copy
import json

import pytest
import test_public_derivation_parity_corpus as parity
from support.public_pyrel_derivation_corpus import ANSWERS, ROOT, assert_manifest, cases, tuples


@pytest.mark.parametrize(
    "fault",
    [
        "empty",
        "drop",
        "duplicate",
        "reorder",
        "model-hash",
        "population-hash",
        "digest",
        "tuple",
        "head",
        "arity",
    ],
)
def test_pyrel_corpus_checker_rejects_dirty_data(fault):
    rows = copy.deepcopy(cases())
    if fault == "empty":
        rows.clear()
    elif fault == "drop":
        rows.pop()
    elif fault == "duplicate":
        rows[-1] = rows[0]
    elif fault == "reorder":
        rows[:2] = list(reversed(rows[:2]))
    elif fault in {"model-hash", "population-hash", "digest"}:
        key = fault.replace("-hash", "_sha256")
        rows[0][key] = "0" * 64
    elif fault == "tuple":
        rows[0]["extensions"]["result"] = [['["string","wrong"]']]
    elif fault == "head":
        rows[0]["extensions"].clear()
    else:
        rows[0]["extensions"]["result"] = [[]]
    with pytest.raises(AssertionError):
        assert_manifest(rows)

@pytest.mark.parametrize("case", cases()[-2:], ids=lambda c: c["id"])
def test_manual_control_answers_agree_with_existing_engines(case):
    model = parity.load_model(ROOT / case["model"])
    population = parity.load_population(ROOT / case["population"], model=model)
    expected = tuples(json.loads((ANSWERS / "manual.json").read_text())[case["id"]])
    assert parity._duckdb_extensions(model, population) == expected
    assert parity._production_digest(model, population) == case["digest"]
    assert parity._canonical_digest(model, expected) == case["digest"]

@pytest.mark.parametrize("changed", ["model", "population"])
def test_live_comparator_rejects_input_byte_drift(changed, tmp_path, monkeypatch):
    from pyrel_derivation_corpus_support import assert_observation

    case = copy.deepcopy(cases()[0])
    receipt = json.loads(parity.RECEIPT.read_text())
    row = next(r for r in receipt["cases"] if r["case_id"] == case["id"])
    row["results"]["pyrel"] = {
        "status": "matched",
        "version": "1.30.1",
        "digest": case["digest"],
        "disposition": None,
    }
    target = tmp_path / "receipt.json"
    target.write_text(json.dumps(receipt))
    monkeypatch.setattr(parity, "RECEIPT", target)
    assert_observation(case, tuples(case["extensions"]))
    changed_path = tmp_path / (changed + ".yaml")
    changed_path.write_bytes((ROOT / case[changed]).read_bytes() + b"\n# changed bytes\n")
    case[changed] = str(changed_path)
    with pytest.raises(AssertionError, match="input bytes changed"):
        assert_observation(case, tuples(case["extensions"]))

