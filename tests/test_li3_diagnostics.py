"""LI3 gated diagnostics cases and the preregistered measurement."""

import copy
import hashlib
import json
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


def test_candidates_are_proposals_bound_to_their_sources():
    from gnd.examples.literature.name_diagnostics import diagnose

    data = read("cases.json")
    before = copy.deepcopy(data)
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


def test_high_occurrence_count_is_bounded():
    from gnd.examples.literature.name_diagnostics import diagnose

    seed = read("cases.json")["occurrences"][0]
    rows = [{**seed, "id": f"d{i}", "work": f"d{i}", "contexts": [f"d{i}"],
             "key": {**seed["key"], "source": f"d{i}", "value": f"name{i:03d}"},
             "evidence": {**seed["evidence"], "source": f"d{i}"}} for i in range(500)]
    started = time.monotonic()
    assert diagnose({"schema": "literature-name-occurrences/1", "occurrences": rows}) == []
    assert time.monotonic() - started < 10
