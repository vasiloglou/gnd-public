"""Exact source Phase4 corpus guards over full approved closure; gate pending."""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest

import tests.support
from tests import test_public_v71_full_judgments as closure

CORPUS = closure.ROOT / "tests/fixtures/v71/phase4"
INPUTS = json.loads((CORPUS / "inputs.json").read_text())
CASES = INPUTS["cases"]
ANSWERS = {r["id"]: r for r in json.loads((CORPUS / "answers.json").read_text())["cases"]}

@pytest.fixture(autouse=True)
def _exact_census_dependency(monkeypatch):
    monkeypatch.setitem(sys.modules, "tests.support.census_scope", closure._CENSUS)
    monkeypatch.setattr(tests.support, "census_scope", closure._CENSUS, raising=False)

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


def test_corpus_integrity() -> None:
    validate_corpus(CORPUS)


def test_case_answer_bijection() -> None:
    assert len(CASES) == len(ANSWERS) == 450
    assert sum(r["domain"] == "dispatch" for r in CASES) == 225
    assert sum(r["domain"] == "release" for r in CASES) == 225


@pytest.mark.parametrize("mutation", ["answer", "missing", "unlisted", "symlink"])
def test_known_dirty_corpus_is_rejected(tmp_path: Path, mutation: str) -> None:
    copied = tmp_path / "corpus"
    shutil.copytree(CORPUS, copied)
    if mutation == "answer":
        path = copied / "answers.json"
        path.write_text(path.read_text().replace('"status": "ok"', '"status": "dirty"', 1))
    elif mutation == "missing":
        (copied / "dispatch/candidate.pop.json").unlink()
    elif mutation == "unlisted":
        (copied / "unlisted.json").write_text("{}")
    else:
        path = copied / "dispatch/candidate.pop.json"
        path.unlink()
        path.symlink_to(CORPUS / "dispatch/candidate.pop.json")
    with pytest.raises(AssertionError):
        validate_corpus(copied)


def test_dangling_registration_is_rejected() -> None:
    from tests.support import census_scope

    original = census_scope.V71_REGISTERED_DOCUMENTS
    try:
        census_scope.V71_REGISTERED_DOCUMENTS = original | {
            "tests/fixtures/v71/phase4/missing.json"
        }
        with pytest.raises(ValueError, match="registry mismatch"):
            census_scope.verify_v71_registration(require_tracked=False)
    finally:
        census_scope.V71_REGISTERED_DOCUMENTS = original


def test_answers_remain_split() -> None:
    assert "answers.json" in (CORPUS / "README.md").read_text()
    for row in CASES:
        assert not set(row) & {"exit_code", "status", "expected"}


