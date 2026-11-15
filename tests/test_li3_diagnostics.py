"""LI3 gated diagnostics cases and the preregistered measurement."""

import copy
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "src/gnd/examples/literature/diagnostics"


def read(name):
    return json.loads((CORPUS / name).read_bytes())


def invoke(path):
    return subprocess.run([sys.executable, "-m", "gnd.examples.literature.name_diagnostics", str(path)],
                          check=False, capture_output=True, text=True)


def test_named_pairs_and_flow_matching():
    case = read("case-outcomes.json")
    run = invoke(CORPUS / "cases.json")
    assert run.returncode == case["exit_code"], run.stderr
    report = json.loads(run.stdout)
    assert report["input_sha256"] == hashlib.sha256((CORPUS / "cases.json").read_bytes()).hexdigest()
    results = {tuple(item["occurrences"]): item["kind"] for item in report["candidates"]}
    assert all(results[tuple(pair)] == kind for pair, kind in case["required"])
    assert results.get(tuple(case["forbidden_homonym"])) != "homonym"
    # Without the shared introducing work the identical cross-field name is flagged.
    from gnd.examples.literature.name_diagnostics import diagnose

    data = read("cases.json")
    for row in data["occurrences"][-2:]:
        row["introducing_works"] = []
    flagged = {tuple(item["occurrences"]): item["kind"] for item in diagnose(data)}
    assert flagged[tuple(case["forbidden_homonym"])] == "homonym"
    assert flagged["flows-review", "sbi-frontier"] == "family"


def test_candidates_are_proposals_bound_to_their_sources():
    from gnd.composition_resolution import parse_resolution
    from gnd.examples.literature.name_diagnostics import diagnose
    from gnd.model import load_model
    from gnd.model_index import ModelIndex

    data = read("cases.json")
    before = copy.deepcopy(data)
    index = ModelIndex.for_model(load_model(CORPUS.parent / "resolution/model.orm.yaml"))
    rows = {row["id"]: row for row in data["occurrences"]}
    proposed = {}
    for item in diagnose(data):
        decision = item["resolution"]
        members = [rows[identifier] for identifier in item["occurrences"]]
        assert decision["decision"] == "unresolved"
        assert decision["keys"] == [row["key"] for row in members]
        assert decision["evidence"] == [row["evidence"] | {"key": number}
                                         for number, row in enumerate(members)]
        assert decision["input_sha256"] == {row["key"]["source"]: row["population_sha256"] for row in members}
        assert len(set(decision["placeholders"])) == 2
        wire = {"schema": "gnd-resolution/1", "object_types": ["method"], "decisions": [decision]}
        assert parse_resolution(json.dumps(wire).encode(), index, tuple(decision["input_sha256"])).decisions == [decision]
        for row, placeholder in zip(members, decision["placeholders"], strict=True):
            assert proposed.setdefault(row["id"], placeholder) == placeholder
    assert data == before


@pytest.mark.parametrize("broken", ["json", "duplicate-key", "top-level", "row", "digest", "over-limit"])
def test_malformed_refuses_without_traceback(tmp_path, broken):
    path = tmp_path / "input.json"
    data = read("cases.json")
    if broken == "row":
        data["occurrences"][0]["contexts"] = [[]]
    if broken == "digest":
        data["occurrences"][0]["population_sha256"] = "invalid"
    if broken == "over-limit":
        data["occurrences"] *= 50
    encodings = {"json": b"{", "duplicate-key": b'{"occurrences": [], "occurrences": []}', "top-level": b"[]"}
    path.write_bytes(encodings.get(broken, json.dumps(data).encode()))
    run = invoke(path)
    assert run.returncode == read("case-outcomes.json")["malformed_exit"], run.stderr
    assert "Traceback" not in run.stderr
    report = json.loads(run.stdout)
    assert report["exit_code"] == 3 and report["candidates"] == []
    if broken == "over-limit":
        assert report["reason"] == "input:occurrence-limit"


def test_high_occurrence_count_is_bounded():
    from gnd.examples.literature.name_diagnostics import diagnose

    seed = read("cases.json")["occurrences"][0]
    rows = [{**seed, "id": f"d{i}", "work": f"d{i}", "contexts": ["same-context"],
             "key": {**seed["key"], "source": f"d{i}", "value": f"name{i:03d}name{i:03d}"},
             "evidence": {**seed["evidence"], "source": f"d{i}"}} for i in range(500)]
    started = time.monotonic()
    assert diagnose({"schema": "literature-name-occurrences/1", "occurrences": rows}) == []
    assert time.monotonic() - started < 10


@pytest.mark.parametrize("word", ["family", "families", "methods", "variants"])
def test_a_generic_family_word_alone_is_not_a_name(word):
    from gnd.examples.literature.name_diagnostics import diagnose

    data = read("cases.json")
    seed = data["occurrences"][0]
    data["occurrences"] = [
        {**seed, "id": label, "work": label, "contexts": [label],
         "key": {**seed["key"], "source": label, "value": f"{label} {word}"},
         "evidence": {**seed["evidence"], "source": label}}
        for label in ("AlphaFold", "Boltz", "OpenCap", "VampNet")
    ]
    assert diagnose(data) == []


def test_large_candidate_output_refuses_before_publication():
    from gnd.examples.literature.assurance_report import Refusal
    from gnd.examples.literature.name_diagnostics import diagnose

    seed = read("cases.json")["occurrences"][0]
    rows = [{**seed, "id": f"d{i}", "work": f"d{i}", "contexts": [f"d{i}"],
             "key": {**seed["key"], "source": f"d{i}", "value": "TRACE"},
             "evidence": {**seed["evidence"], "source": f"d{i}"}} for i in range(500)]
    started = time.monotonic()
    with pytest.raises(Refusal) as error:
        diagnose({"schema": "literature-name-occurrences/1", "occurrences": rows})
    assert error.value.reason == "input:candidate-limit"
    assert time.monotonic() - started < 10


def test_measurement_sampler_and_grader_liveness():
    from gnd.examples.literature.diagnostic_measurement import score

    registered = read("labels.json")["labels"]
    labels = {tuple(row["pair"]): row["kind"] for row in registered}
    oracle = [{"kind": kind, "occurrences": list(pair)} for pair, kind in labels.items() if kind is not None]
    measured = score(oracle, labels)
    assert all(row["status"] == "pass" and row["false_discoveries"] == 0 for row in measured.values())
    assert sum(row["denominator"] for row in measured.values()) == 100
    assert all(row["denominator"] >= 20 for row in measured.values())
    assert score(list(reversed(oracle)), labels) == measured
    assert all(row["status"] == "fail" for row in score(oracle, {}).values())
    undersized = score(oracle[:3], labels)
    assert {row["status"] for row in undersized.values()} == {"unmeasured"}
    assert sum(row["denominator"] for row in undersized.values()) == 3


def test_case_variant_needs_acronym_casing_with_shared_context():
    from gnd.examples.literature.name_diagnostics import diagnose

    data = read("cases.json")
    left, right = data["occurrences"][:2]
    right["contexts"] = left["contexts"] = ["shared"]
    data["occurrences"] = [left, right]
    assert [item["kind"] for item in diagnose(data)] == ["homonym"]
    left["key"]["value"], right["key"]["value"] = "AlphaFold", "Alphafold"
    assert diagnose(data) == []


def test_fifo_is_refused_before_opening(tmp_path):
    from gnd.examples.literature.name_diagnostics import main

    fifo = tmp_path / "not-a-file"
    os.mkfifo(fifo)
    result = subprocess.run([sys.executable, "-m", main.__module__, str(fifo)],
                            capture_output=True, text=True, check=False, timeout=3)
    assert result.returncode == 3
    assert json.loads(result.stdout)["candidates"] == []


def test_non_ascii_values_survive_an_ascii_stdout(tmp_path, monkeypatch):
    data = read("cases.json")
    left, right = data["occurrences"][:2]
    left["key"]["value"] = right["key"]["value"] = "Échelle"
    data["occurrences"] = [left, right]
    path = tmp_path / "input.json"
    path.write_text(json.dumps(data))
    monkeypatch.setenv("PYTHONIOENCODING", "ascii")
    result = invoke(path)
    assert result.returncode == 0, result.stderr
    candidates = json.loads(result.stdout)["candidates"]
    assert candidates[0]["resolution"]["keys"][0]["value"] == "Échelle"


def test_wrong_kind_counts_at_the_measured_boundary():
    from gnd.examples.literature.diagnostic_measurement import score

    pairs = [(f"source-{i:02}", "target") for i in range(20)]
    candidates = [{"kind": "homonym", "occurrences": list(pair)} for pair in pairs]
    labels = {pair: ("synonym" if index < 4 else "homonym") for index, pair in enumerate(pairs)}
    at_floor = score(candidates, labels)["homonym"]
    assert at_floor["status"] == "pass" and at_floor["false_discovery_fraction"] == [4, 20]
    labels[pairs[4]] = "synonym"
    assert score(candidates, labels)["homonym"]["status"] == "fail"
