"""Complete450 original v71 session branches over the reviewed full575 closure."""
import hashlib
import json
import sys
from pathlib import Path

import pytest

from tests.support import v71_phase4_full_runtime as sessions

CORPUS = sessions.CORPUS
INPUTS = sessions.INPUTS
ANSWERS = sessions.ANSWERS
CASES = INPUTS["cases"]
assert_answer = sessions.assert_answer

def execute(row, root, monkeypatch):
    with monkeypatch.context() as scoped:
        scoped.setitem(sys.modules, "tests.test_v71_phase4_sessions", sys.modules[__name__])
        return sessions.execute(row, root, scoped)

def validate_corpus(root: Path) -> None:
    manifest = json.loads((root / "manifest.json").read_text())
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
        data = path.read_bytes()
        assert entry == {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    inputs = json.loads((root / "inputs.json").read_text())
    answers = json.loads((root / "answers.json").read_text())["cases"]
    rows = inputs["cases"]
    assert len({r["id"] for r in rows}) == len(rows)
    assert len({r["id"] for r in answers}) == len(answers)
    assert {r["id"] for r in rows} == {r["id"] for r in answers}
    for domain in ("dispatch", "release"):
        assert {r["branch"] for r in rows if r["domain"] == domain} == {
            f"B{i:02d}" for i in range(1, 31)
        }
    assert all(set(r) == {"id", "domain", "branch", "mode", "parameters"} for r in rows)
    assert all(set(r) > {"id"} for r in answers)
    assert {r["mode"] for r in rows} == {
        "patch",
        "patch-intake",
        "session",
        "publication",
        "admission",
        "public-report",
        "rank",
        "feedback",
        "annotation",
        "contract",
        "compat",
        "limit",
        "work",
        "instrument",
    }


@pytest.mark.parametrize("row", CASES, ids=lambda row: row["id"])
def test_phase4_branch(row: dict, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = execute(row, tmp_path, monkeypatch)
    assert_answer(result, ANSWERS[row["id"]])

