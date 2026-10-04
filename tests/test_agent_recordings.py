"""The recorded agent sessions are intact, replayable and secret-free."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
from importlib.resources import files
from pathlib import Path

import pytest

from gnd import api

APPROVALS = files("gnd") / "examples" / "approvals"
RECORDINGS = Path(str(APPROVALS / "recordings"))
MANIFEST = json.loads((RECORDINGS / "manifest.json").read_text())


@pytest.mark.parametrize("name", sorted(MANIFEST["recordings"]))
def test_recorded_bytes_match_the_manifest(name):
    files_ = MANIFEST["recordings"][name]["files"]
    assert files_
    for relative, digest in files_.items():
        assert hashlib.sha256((RECORDINGS / relative).read_bytes()).hexdigest() == digest


def test_every_committed_file_is_in_the_manifest():
    listed = {relative for entry in MANIFEST["recordings"].values() for relative in entry["files"]}
    on_disk = {str(p.relative_to(RECORDINGS)) for p in RECORDINGS.rglob("*") if p.is_file()}
    assert on_disk - listed == {"manifest.json", "results.json", "README.md", "TASK.md"}


def test_every_recorded_attempt_replays_to_its_recorded_band(tmp_path):
    root = tmp_path / "walk"
    (root / "input").mkdir(parents=True)
    (root / "cand").mkdir()
    shutil.copy(str(APPROVALS / "model.orm.yaml"), root / "model.orm.yaml")
    state = (APPROVALS / "state.pop.yaml").read_text().replace("model: model.orm.yaml", "model: ../model.orm.yaml")
    (root / "input/state.pop.yaml").write_text(state)
    replayed = 0
    for name in MANIFEST["recordings"]:
        for attempt in sorted((RECORDINGS / name).glob("attempt-*")):
            shutil.copy(attempt / "steps.json", root / "cand/steps.json")
            recorded = json.loads((attempt / "feedback.json").read_text())["required"][0]["band"]
            report = api.transition(root / "model.orm.yaml", root / "input/state.pop.yaml", root / "cand/steps.json")
            assert report["exit_code"] == recorded, (name, attempt.name)
            replayed += 1
    assert replayed >= 10


def test_results_table_matches_the_stated_findings():
    results = json.loads((RECORDINGS / "results.json").read_text())
    runs = [run for row in results["sessions"] for run in row["runs"]]
    assert len(runs) == 29
    rejected = [band for run in runs for band in run["bands"] if band != 0]
    assert (len(rejected), rejected.count(3), rejected.count(1)) == (20, 14, 6)
    for run in runs:
        assert run["bands"][-1] == 0 if run["disposition"] == "accepted" else run["bands"][-1] != 0
        assert run["attempts"] == len(run["bands"]) <= results["max_attempts"]


def test_recordings_contain_no_paths_or_credentials():
    for path in RECORDINGS.rglob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for needle in ("/Users/", "/private/", "/home/", "sk-", "Bearer", "API_KEY="):
                assert needle not in text, (path, needle)


def test_gateway_wraps_a_reply_as_the_closed_file_bundle():
    spec = importlib.util.spec_from_file_location("gnd_example_gateway", str(APPROVALS / "openrouter_gateway.py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    bundle = json.loads(module.bundle('```json\n{"steps": []}\n```'))
    assert set(bundle) == {"schema_version", "files"} and bundle["schema_version"] == 1
    (row,) = bundle["files"]
    assert row["path"] == "steps.json" and set(row) == {"path", "content_base64"}
    import base64
    assert json.loads(base64.b64decode(row["content_base64"])) == {"steps": []}
