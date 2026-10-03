"""Owner-gated RED corpus for the finite v7.1 witness contract.

The baseline feature guard intentionally makes every runtime case RED while the
lane is absent. That is authoring evidence, not execution of the later branches.
"""

from __future__ import annotations

import copy
import hashlib
import json
import time
from pathlib import Path

import pytest
from support.public_v71_witness_corpus import ANSWERS, CORPUS, INPUTS, assert_answer, execute

CASES = [row for row in INPUTS["cases"] if row["lane"] == "default"]


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
    inputs = json.loads((root / "inputs.json").read_text())["cases"]
    answers = json.loads((root / "answers.json").read_text())["cases"]
    assert len({r["id"] for r in inputs}) == len(inputs)
    assert len({r["id"] for r in answers}) == len(answers)
    assert {r["id"] for r in inputs} == {r["id"] for r in answers}
    assert {r["branch"] for r in inputs} == {f"B{i:02d}" for i in range(1, 29)}
    for domain in ("dispatch", "release"):
        assert {r["branch"] for r in inputs if r["domain"] == domain} == {
            f"B{i:02d}" for i in range(1, 29)
        }
    for row in answers:
        assert type(row["exit_code"]) is int and row["exit_code"] in range(5)
        assert row["status"] in {
            None,
            "proved",
            "missing",
            "unknown",
            "unsupported",
            "invalid",
            "input-refused",
            "resource-refused",
        }


def test_corpus_integrity() -> None:
    validate_corpus(CORPUS)


def test_case_answer_bijection() -> None:
    assert len(INPUTS["cases"]) == 266
    assert len(CASES) == 258
    assert len(ANSWERS) == 266
    assert sum(r["lane"] == "derivation_oracle" for r in INPUTS["cases"]) == 8


def test_known_dirty_answer_is_rejected(tmp_path: Path) -> None:
    import shutil

    copied = tmp_path / "corpus"
    shutil.copytree(CORPUS, copied)
    answers = json.loads((copied / "answers.json").read_text())
    answers["cases"][0]["exit_code"] = 4
    (copied / "answers.json").write_text(json.dumps(answers))
    with pytest.raises(AssertionError):
        validate_corpus(copied)


def test_known_missing_fixture_is_rejected(tmp_path: Path) -> None:
    import shutil

    copied = tmp_path / "corpus"
    shutil.copytree(CORPUS, copied)
    (copied / "dispatch/direct.witness.json").unlink()
    with pytest.raises(AssertionError):
        validate_corpus(copied)




def test_answers_remain_split() -> None:
    readme = (CORPUS / "README.md").read_text()
    assert "answers.json" in readme
    assert "expected_exit" not in json.dumps(INPUTS)
    assert not set(copy.deepcopy(INPUTS["cases"])[0]) & {"exit_code", "status"}


@pytest.mark.parametrize("row", CASES, ids=lambda row: row["id"])
def test_phase3_branch(row: dict, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    started = time.monotonic()
    measurement = {}
    result = execute(row, tmp_path, monkeypatch, measurement=measurement)
    assert_answer(result, ANSWERS[row["id"]])
    if row["mode"] in {"input-limit", "work-limit", "diamond", "view-limit"}:
        assert (
            time.monotonic()
            - started
            - measurement["baseline_seconds"]
            - measurement["fixture_seconds"]
            - measurement["inherited_intake_seconds"]
            <= 10
        ), "selected added-layer control exceeded 10s"


@pytest.fixture(autouse=True)
def _original_relative_fixture_coordinates(monkeypatch):
    # Legacy check branches retain their original relative fixture arguments.
    monkeypatch.chdir(CORPUS.parents[3])
