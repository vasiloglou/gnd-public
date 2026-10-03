"""Phase 6 corpus-first compatibility lane; no answer-generating producer."""

import hashlib
import importlib.util
import json

import pytest
from test_public_v72_semantic_owner_inputs import (
    ROOT,
    _complete_witness_domains,  # noqa: F401 -- pytest fixture
)

from gnd import checker

HASHES = {
    "tests/fixtures/v72/phase6/inputs.json": "15aff43e9b4206ffe8a6580279920e1f268616b7e005faacb2d8109682a078d0",
    "tests/fixtures/v72/phase6/answers.json": "5c5562d787048f5852b957cc0c7ded2c405af7ce87265530a52aa5b7ac8f519c",
    ".gnd-planning/milestones/v7.2/evidence/phase-6/characterize.py": "783ffbb83b289c832bec0b3e035a6cf20bbd918b70fee414497c43eb56fb8350",
    ".gnd-planning/milestones/v7.2/evidence/phase-6/baseline-before-r2.json": "39e27c99858f0b9221fd69fc211298c10ce712b87a72654eefc3f4a6096f4fc3",
}
for relative, digest in HASHES.items():
    assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
CORPUS = ROOT / "tests/fixtures/v72/phase6"
CASES = json.loads((CORPUS / "inputs.json").read_text())["cases"]
ANSWERS = {
    r["id"]: r["expected"] for r in json.loads((CORPUS / "answers.json").read_text())["cases"]
}
EVIDENCE = ROOT / ".gnd-planning/milestones/v7.2/evidence/phase-6"
SPEC = importlib.util.spec_from_file_location("p6_characterize", EVIDENCE / "characterize.py")
CHARACTERIZE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHARACTERIZE)
BEFORE = {
    r["id"]: r["observation"]
    for r in json.loads((EVIDENCE / "baseline-before-r2.json").read_text())["cases"]
}


@pytest.mark.parametrize("row", CASES, ids=lambda row: row["id"])
def test_calculator_join_compatibility(row):
    assert callable(getattr(checker, "_clause_bindings", None)), (
        "shared production binding owner is absent"
    )
    actual = CHARACTERIZE.observe(row)
    expected = ANSWERS[row["id"]]
    if row["consumer"] == "calculator":
        assert actual["relations"]["output"]["rows"] == expected["rows"]
    else:
        assert {key: actual[key] for key in expected} == expected
    assert actual == BEFORE[row["id"]], (
        "rows, ordered lineage, report and every work field must remain exact"
    )


@pytest.mark.parametrize("size", [12, 24])
def test_dense_recursive_occurrence_variants(size):
    before = json.loads((EVIDENCE / "dense-before.json").read_text())[str(size)]
    actual = CHARACTERIZE.dense(size)
    assert actual["reference_agrees"]
    assert actual["rows"] == actual["expected_rows"] == size * (size - 1) // 2
    assert actual["production_work"] == before["production_work"]
    assert actual["reference_pair_probes"] == before["reference_pair_probes"]
    assert actual["seconds"] < 5


@pytest.mark.parametrize("kind", ["empty", "selected"])
def test_selective_refresh_binding_owner(kind):
    from dataclasses import asdict

    m, p = CHARACTERIZE.model_population("negation")
    view = checker.structured_extension_view(
        m,
        p,
        refresh=[] if kind == "empty" else ["output"],
        previous={"output": ({"value": 2}, {"value": 3})},
    )
    actual = {
        "facts": {k: [dict(r) for r in rows] for k, rows in view.facts.items()},
        "work": asdict(view.work),
        "recomputed": list(view.recomputed),
    }
    assert actual == json.loads((EVIDENCE / "refresh-before.json").read_text())[kind]
    assert actual["facts"]["output"] == (
        [{"value": 2}, {"value": 3}] if kind == "empty" else [{"value": 2}]
    )


def test_shared_binding_mutant_is_discriminated(monkeypatch):
    original = checker._clause_bindings

    def skip_negation(rule, facts, work):
        return original({key: value for key, value in rule.items() if key != "negate"}, facts, work)

    monkeypatch.setattr(checker, "_clause_bindings", skip_negation)
    for engine in ("legacy", "exact", "scc"):
        row = {"consumer": "calculator", "engine": engine, "variant": "negation"}
        observed = CHARACTERIZE.observe(row)
        assert observed["relations"]["output"]["rows"] == [[2], [3]]
        assert observed != BEFORE[engine + "-negation"]
        assert observed["relations"]["output"]["rows"] != ANSWERS[engine + "-negation"]["rows"]
        with pytest.raises(AssertionError):
            test_calculator_join_compatibility({"id": engine + "-negation", **row})


@pytest.mark.parametrize("domain", ["dispatch", "release"])
def test_production_inference_fault_remains_independently_invalid(domain, tmp_path, monkeypatch):
    from dataclasses import replace

    from tests.support import v71_witness_cases as helper

    b = helper.bundle(domain, tmp_path / "fault")
    b["domain"] = domain
    helper.comparison(b, {"primitive": "Integer", "left": 2, "operator": "=", "right": 3})
    helper.save(b)
    clean = helper.produce(b)
    assert clean["exit_code"] == 2 and clean["results"][0]["status"] == "missing"
    original = checker.compare_terms
    reached = []

    def false_success(*args, **kwargs):
        result = original(*args, **kwargs)
        if result.available and result.value is False:
            reached.append((args, kwargs))
            return replace(result, value=True)
        return result

    monkeypatch.setattr(checker, "compare_terms", false_success)
    corrupted = helper.produce(b)
    assert reached, "fault must execute inside actual production inference"
    assert corrupted["exit_code"] == 0 and corrupted["results"][0]["status"] == "proved"
    assert any(node["kind"] == "comparison" for node in corrupted["certificate"]["nodes"])
    still_active = len(reached)
    independent = helper.kernel(b, corrupted["certificate"])
    assert independent["exit_code"] == 1
    assert independent["results"][0]["status"] == "invalid"
    assert checker.compare_terms is false_success and len(reached) == still_active


@pytest.mark.parametrize("domain", ["dispatch", "release"])
def test_replay_blocks_direct_and_transitive_production_inference(domain, tmp_path, monkeypatch):
    from gnd import terms
    from tests.support import v71_witness_cases as helper

    b = helper.bundle(domain, tmp_path / "sentinel")
    b["domain"] = domain
    helper.save(b)
    helper.no_evaluator(monkeypatch)

    def forbidden(*args, **kwargs):
        raise AssertionError("replay crossed an inference boundary")

    for name in (
        "_clause_bindings",
        "_joined_bindings",
        "_partial_bindings",
        "compare_terms",
        "evaluate_term",
        "materialize_scalar",
    ):
        monkeypatch.setattr(checker, name, forbidden)
    monkeypatch.setattr(terms, "compare_terms", forbidden)
    assert helper.kernel(b)["results"][0]["status"] == "proved"
    helper.comparison(b, {"primitive": "Integer", "left": 2, "operator": "=", "right": 3})
    helper.save(b)
    invalid = helper.kernel(b)
    assert invalid["exit_code"] == 1 and invalid["results"][0]["status"] == "invalid"


@pytest.mark.parametrize("source", ["gnd.witness.kernel", "gnd.witness.io"])
def test_import_boundary_detects_direct_and_transitive_inference(source):
    spec = importlib.util.spec_from_file_location("p6_inventory", EVIDENCE / "inventory.py")
    inventory = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inventory)
    actual = inventory.inference_imports()
    # Complete module reachability includes dormant production imports; it is not isolation.
    assert "gnd.checker" in actual["closure"] and "gnd.terms" in actual["closure"]
    assert not any(
        "_clause_bindings" in row["names"] for row in actual["potential_inference_imports"]
    )
    planted = inventory.inference_imports({source: "from gnd.checker import _clause_bindings"})
    assert any(
        row["source"] == source and "_clause_bindings" in row["names"]
        for row in planted["potential_inference_imports"]
    )
