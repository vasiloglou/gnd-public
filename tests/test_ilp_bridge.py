"""IK5: the ILP bridge, ``gnd export ilp`` and ``gnd import ilp-rules`` (induced-knowledge).

Spec: .gnd-planning/milestones/induced-knowledge/notes/phase-IK5-spec.md. Under
IK5-D1 the cases are an owner-approved corpus: inputs in
tests/fixtures/induced_knowledge/ik5-corpus/cases.json, hand-written answers in
expected.json and expected-export/, and stories in that directory's README.md.
The learner outputs are hand-authored in Popper's printed syntax (IK5-D13 (a)).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from support.cli_runner import run_main

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS = REPO_ROOT / "tests" / "fixtures" / "induced_knowledge" / "ik5-corpus"
CASES = json.loads((CORPUS / "cases.json").read_text(encoding="utf-8"))
EXPECTED = json.loads((CORPUS / "expected.json").read_text(encoding="utf-8"))
ANSWERS = EXPECTED["cases"]
BY_ID = {case["id"]: case for case in CASES["cases"]}


def _work(tmp_path: Path) -> Path:
    work = tmp_path / "corpus"
    if not work.exists():
        shutil.copytree(CORPUS, work, symlinks=True)
        (work / "pops" / "link.yaml").symlink_to(work / "pops" / "n1.yaml")
    return work


def _argv(work: Path, case: dict[str, Any], out: Path) -> list[str]:
    model = str(work / CASES["model"])
    manifest = str(work / case["manifest"])
    if case["command"] == "export":
        return ["export", "ilp", model, "--labels", manifest, "--target", case["target"],
                "--out", str(out)]
    return ["import", "ilp-rules", model, str(work / case["clauses"]), "--labels", manifest,
            "--reported-coverage", str(work / case["run"]), "--target", case["target"],
            "--out", str(out), "--format", "json"]


def _tree(root: Path) -> dict[str, bytes]:
    return {path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*")) if path.is_file()}


def _run(tmp_path: Path, case: dict[str, Any]) -> tuple[Any, Path]:
    work = _work(tmp_path)
    out = tmp_path / f"{case['id'].lower()}.out"
    if case.get("out_exists") or case["id"] == "XE3":
        out.mkdir() if case["command"] == "export" else out.write_text("{}\n", encoding="utf-8")
    return run_main(_argv(work, case, out)), out


CORPUS_CASES = [case for case in CASES["cases"] if case["command"] != "preview"]


@pytest.mark.parametrize("case", CORPUS_CASES, ids=lambda case: case["id"])
def test_ik5_corpus(tmp_path: Path, case: dict[str, Any]) -> None:
    answer = ANSWERS[case["id"]]
    existed = case.get("out_exists") or case["id"] == "XE3"
    result, out = _run(tmp_path, case)
    stdout = result.stdout.decode("utf-8", errors="replace")
    stderr = result.stderr.decode("utf-8", errors="replace")
    assert result.returncode == answer["exit"], stdout + stderr
    if "refusal" in answer:
        assert answer["refusal"] in stderr, stderr
        if "clause" in answer:
            assert f"clause {answer['clause']}" in stderr, stderr
    if answer["exit"] != 0:
        if not existed:
            assert not out.exists(), "a refused run wrote its output"
        return
    if case["command"] == "export":
        assert answer["export_sha256"] in stdout
        assert _tree(out) == _tree(CORPUS / answer["tree"])
        return
    proposal = json.loads(out.read_text(encoding="utf-8"))
    added = [operation["after"] for operation in proposal["operations"]]
    assert added == answer["constraints"]
    assert all(operation["kind"] == "add" for operation in proposal["operations"])
    report = json.loads(stdout)
    assert report["schema_version"] == "gnd-ilp-import/1"
    assert {str(k): row["vacuous"] for k, row in enumerate(report["clauses"])} == answer["vacuous"]


def test_answer_key_covers_every_case() -> None:
    assert {case["id"] for case in CASES["cases"]} == set(ANSWERS)


def test_popper_and_neutral_imports_add_the_same_rules(tmp_path: Path) -> None:
    """I1 and I2 differ only in the method spelling and the evidence digests."""
    def core(constraint: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in constraint.items() if key != "provenance"}

    assert [core(c) for c in ANSWERS["I1"]["constraints"]] == [
        core(c) for c in ANSWERS["I2"]["constraints"]]


def test_i3_the_proposal_previews(tmp_path: Path) -> None:
    result, out = _run(tmp_path, BY_ID["I1"])
    assert result.returncode == 0, result.stderr
    work = _work(tmp_path)
    preview = run_main([
        "evolve", "preview", str(work / CASES["model"]), str(out), "--workspace", str(tmp_path),
        "--records", str(tmp_path / "records"), "--out", str(tmp_path / "preview.json"),
    ])
    assert preview.returncode == ANSWERS["I3"]["exit"], preview.stdout + preview.stderr


def test_d1_export_is_the_same_under_two_hash_seeds(tmp_path: Path) -> None:
    work = _work(tmp_path)
    trees = []
    for seed in ("0", "1"):
        out = tmp_path / f"seed{seed}"
        completed = subprocess.run(
            [sys.executable, "-m", "gnd", *_argv(work, BY_ID["X1"], out)], cwd=REPO_ROOT,
            env={**os.environ, "PYTHONHASHSEED": seed}, capture_output=True, timeout=120, check=False,
        )
        assert completed.returncode == 0, completed.stderr
        trees.append(_tree(out))
    assert trees[0] == trees[1] == _tree(CORPUS / ANSWERS["X1"]["tree"])
