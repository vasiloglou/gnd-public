"""Complete448original saved-judgment branches; all575registration subjects."""
from __future__ import annotations

import atexit
import base64
import gzip
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
from pathlib import Path

import pytest

import tests.support

PACKS = [{'target': 'tests/fixtures/public-v71-full-judgments/closure-01.json.gz', 'target_sha256': '818000dc3746ab752817310188f577ef16dc2781e676896361d9c47d34c0ff12', 'bytes': 253289, 'expanded_bytes': 2080317, 'expanded_sha256': 'f75b426be40e48f75e76b66d8239518335f896fd6405279f3ac42dd8ffff2d86', 'members': 405}, {'target': 'tests/fixtures/public-v71-full-judgments/closure-02.json.gz', 'target_sha256': 'cd0a72eee056b05b00eca4b65c7a86fca652aa9fb8ffbba67f61ff7b0ade1e5c', 'bytes': 159505, 'expanded_bytes': 1021860, 'expanded_sha256': 'a8840babc16e326cc4dd958cb9764fab6f18af2703fe86d42bb066143c124575', 'members': 173}]
ROSTER_SHA256 = '481804d4fa24791d4438c8b1508e3989d5d1a14b825a9d48bb96667b8bcb8c04'

def _materialize():
    temporary=tempfile.TemporaryDirectory(prefix="gnd-public-v71-full-judgments-")
    root=Path(temporary.name).resolve()
    actual={}
    for pin in PACKS:
        path=Path(__file__).parent.parent/pin["target"]
        packed=path.read_bytes()
        assert len(packed)<=1048576 and len(packed)==pin["bytes"]
        assert hashlib.sha256(packed).hexdigest()==pin["target_sha256"]
        with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
            raw=stream.read(2097153)
        assert len(raw)<=2097152 and len(raw)==pin["expanded_bytes"]
        assert hashlib.sha256(raw).hexdigest()==pin["expanded_sha256"]
        members=json.loads(raw)
        assert len(members)==pin["members"]
        for row in members:
            name=row["path"]
            assert name not in actual
            actual[name]=(row["bytes"],row["sha256"],row["mode"])
            relative=Path(name)
            assert not relative.is_absolute() and ".." not in relative.parts
            payload=base64.b64decode(row["base64"],validate=True)
            assert (len(payload),hashlib.sha256(payload).hexdigest(),row["mode"])==actual[name]
            assert len(payload)<=1048576
            path=root/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(payload)
            path.chmod(row["mode"])
    assert len(actual)==578
    assert hashlib.sha256(json.dumps(actual,sort_keys=True,separators=(",", ":")).encode()).hexdigest()==ROSTER_SHA256
    return temporary,root

_TEMPORARY,ROOT=_materialize()
atexit.register(_TEMPORARY.cleanup)

def _load(name):
    spec=importlib.util.spec_from_file_location("public_v71_full_"+name,ROOT/"evidence"/(name+".py"))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

_JUDGMENTS=_load("judgment_cases")
_SESSIONS=_load("session_cases")
_CENSUS=_load("census_scope")
CORPUS=_JUDGMENTS.CORPUS
INPUTS=_JUDGMENTS.INPUTS
CASES=INPUTS["cases"]
ANSWERS={row["id"]:row for row in json.loads((CORPUS/"answers.json").read_bytes())["cases"]}

def execute(row,root,monkeypatch):
    with monkeypatch.context() as scoped:
        scoped.setitem(sys.modules,"tests.support.v71_session_cases",_SESSIONS)
        scoped.setitem(sys.modules,"tests.support.census_scope",_CENSUS)
        scoped.setattr(tests.support,"census_scope",_CENSUS,raising=False)
        scoped.setitem(sys.modules,"tests.test_v71_phase5_judgments",sys.modules[__name__])
        return _JUDGMENTS.execute(row,root,monkeypatch)


def assert_answer(observed, expected):
    for name, value in expected.items():
        if name != "id":
            assert name in observed, f"missing observation: {name}"
            assert observed[name] == value, (
                f"{name}: observed {observed[name]!r}, expected {value!r}"
            )


def validate_corpus(root: Path):
    manifest = json.loads((root / "manifest.json").read_bytes())
    assert manifest["schema_version"] == 1
    actual = {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and p.name != "manifest.json"
    }
    assert set(manifest["files"]) == actual
    for relative, entry in manifest["files"].items():
        path = root / relative
        assert not path.is_symlink()
        raw = path.read_bytes()
        assert entry == {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    inputs = json.loads((root / "inputs.json").read_bytes())
    answers = json.loads((root / "answers.json").read_bytes())["cases"]
    rows = inputs["cases"]
    assert len({r["id"] for r in rows}) == len(rows)
    assert len({r["id"] for r in answers}) == len(answers)
    assert {r["id"] for r in rows} == {r["id"] for r in answers}
    for domain in ("dispatch", "release"):
        assert {r["branch"] for r in rows if r["domain"] == domain} == {
            f"J{i:02d}" for i in range(1, 41)
        }
    for row in rows:
        assert set(row) == {"id", "domain", "branch", "mode", "parameters", "story"}
        assert row["story"] and row["parameters"]["variant"]
        assert not set(row) & {"outcome", "expected", "admission", "repair"}
    assert all(set(r) > {"id"} for r in answers)
    assert {r["mode"] for r in rows} == {
        "policy",
        "binding",
        "confidence",
        "confidence-invalid",
        "confidence-integration",
        "projection",
        "mechanical",
        "reference",
        "contract",
        "compat",
        "session",
        "session-protection",
        "replay",
        "limit",
        "hostile",
        "privacy",
        "sentinel",
        "work",
        "instrument",
    }
    for domain in ("dispatch", "release"):
        policy = json.loads((root / domain / "policy.json").read_bytes())
        receipts = json.loads((root / domain / "receipts.json").read_bytes())
        for receipt in receipts["receipts"]:
            # Independent byte identity check, not policy admission/calibration.
            assert receipt["external_evidence"] is None
            from gnd.artifacts import canonical_json_bytes

            value = hashlib.sha256(canonical_json_bytes(receipt, exact_numbers=True)).hexdigest()
            assert {"judge_id": receipt["judge_id"], "receipt_sha256": value} in policy[
                "trusted_receipts"
            ]


@pytest.mark.parametrize("row", CASES, ids=lambda row: row["id"])
def test_phase5_branch(row, tmp_path, monkeypatch):
    assert_answer(execute(row, tmp_path, monkeypatch), ANSWERS[row["id"]])

