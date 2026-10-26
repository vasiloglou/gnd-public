"""IK3: measuring host-labelled populations, ``gnd measure --labels`` (induced-knowledge).

Spec: .gnd-planning/milestones/induced-knowledge/notes/phase-IK3-spec.md. Under
IK3-D1 the cases are an owner-approved corpus: inputs in
tests/fixtures/induced_knowledge/ik3-corpus/cases.json, hand-written answers in
expected.json, and stories in that directory's README.md.
"""

from __future__ import annotations

import hashlib
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
CORPUS = REPO_ROOT / "tests" / "fixtures" / "induced_knowledge" / "ik3-corpus"
CASES = json.loads((CORPUS / "cases.json").read_text(encoding="utf-8"))
EXPECTED = json.loads((CORPUS / "expected.json").read_text(encoding="utf-8"))["cases"]
MANIFEST_CAP = 1024 * 1024
SYNTH = REPO_ROOT / "tests" / "fixtures" / "public-launch-phase-3" / "measurement"
SYNTH_MODEL = REPO_ROOT / "tests" / "fixtures" / "public-launch-phase-2" / "model.orm.yaml"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _header(work: Path, mode: str) -> dict[str, Any]:
    return {"schema_version": "gnd-labels/1", "model_sha256": _sha(work / CASES["model"]),
            "mode": mode}


def _generated(work: Path, kind: str) -> Path:
    path = work / f"{kind.lower()}.labels.json"
    ok = _sha(work / "pops" / "ok.yaml")
    if kind == "NEAR-CAP":
        rules = {ref: {"fires_on": "negative"} for ref in (
            "id:u_person_team", "id:m_person_grade", "fact_types[person_has_skill].constraints[0]")}
        populations = [{"id": str(i), "path": "pops/ok.yaml", "sha256": ok,
                        "class": "negative" if i % 2 else "positive"} for i in range(8000)]
        document = {**_header(work, "class"), "populations": populations, "rules": rules}
        path.write_text(json.dumps(document, separators=(",", ":")), encoding="utf-8")
        assert path.stat().st_size <= MANIFEST_CAP
    elif kind == "OVER-CAP":
        document = {**_header(work, "class"), "populations": [
            {"id": "ok", "path": "pops/ok.yaml", "sha256": ok, "class": "positive"}],
            "rules": {"id:u_person_team": {"fires_on": "negative", "pad": "x" * MANIFEST_CAP}}}
        path.write_text(json.dumps(document), encoding="utf-8")
        assert path.stat().st_size > MANIFEST_CAP
    elif kind == "RULES-OVER":
        document = {**_header(work, "class"), "populations": [
            {"id": "ok", "path": "pops/ok.yaml", "sha256": ok, "class": "positive"}],
            "rules": {f"id:r{i}": {"fires_on": "negative"} for i in range(1025)}}
        path.write_text(json.dumps(document), encoding="utf-8")
    else:
        raise AssertionError(kind)
    return path


def _prepare(tmp_path: Path, case: dict[str, Any]) -> list[str]:
    work = tmp_path / "corpus"
    shutil.copytree(CORPUS, work, symlinks=True)
    (work / "pops" / "link.yaml").symlink_to(work / "pops" / "ok.yaml")
    model = str(work / CASES["model"])
    argv = case["argv"]
    if case["manifest"] is not None:
        source = ["--labels", str(work / case["manifest"])]
        return ["measure", model, *source, *[a if a != "." else str(work) for a in argv],
                "--format", "json"]
    marker = argv[0]
    if marker == "NO-SOURCE":
        return ["measure", model, "--format", "json"]
    if marker == "MISSING":
        return ["measure", model, "--labels", str(work / "absent.labels.json"), "--format", "json"]
    return ["measure", model, "--labels", str(_generated(work, marker)), "--format", "json"]


def _cells(report: dict[str, Any]) -> dict[str, dict[str, int]]:
    return {row["constraint_ref"]: row["cells"] for row in report["per_constraint"]}


def _defects(report: dict[str, Any]) -> list[dict[str, Any]]:
    keys = ("kind", "constraint_ref", "modality", "population", "expected_verdict",
            "observed_verdict")
    return [{key: row[key] for key in keys} for row in report["checker_defects"]]


def _rules(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["ref"]: {"fires_on": row["fires_on"], "cells": row["cells"]}
            for row in report["rules"]}


LABELLED_CASES = [c for c in CASES["cases"] if c["id"] not in {"X1", "D1"}]


@pytest.mark.parametrize("case", LABELLED_CASES, ids=lambda case: case["id"])
def test_ik3_corpus(tmp_path: Path, case: dict[str, Any]) -> None:
    answer = EXPECTED[case["id"]]
    argv = _prepare(tmp_path, case)
    result = run_main(argv)
    output = (result.stdout + result.stderr).decode("utf-8", errors="replace")
    assert result.returncode == answer["exit"], output
    if "schema_version" not in answer:
        assert not result.stdout.strip().startswith(b'{"schema_version"'), output
        return
    report = json.loads(result.stdout)
    assert report["schema_version"] == answer["schema_version"]
    assert "labels" in report
    if answer["schema_version"] == 4:
        assert _cells(report) == answer["cells"]
        assert _defects(report) == answer["defects"]
        for absent in ("seeds", "pools", "generator_version", "pool_source"):
            assert absent not in report
    else:
        assert _rules(report) == answer["rules"]
    if "work_ceiling" in answer:
        assert 0 < report["labels"]["work"]["total"] <= answer["work_ceiling"]


def test_answer_key_covers_every_case() -> None:
    assert set(EXPECTED) == {case["id"] for case in CASES["cases"]}


def test_x1_parity_with_synth_report(tmp_path: Path) -> None:
    answer = EXPECTED["X1"]
    work = tmp_path / "faker"
    shutil.copytree(SYNTH / "02-corpus" / "movie" / "faker", work)
    index = json.loads((work / "index.json").read_text(encoding="utf-8"))
    populations = []
    for row in index["populations"]:
        sidecar = json.loads((work / row["sidecar"]).read_text(encoding="utf-8"))
        expectations = {
            ref: {key: value for key, value in state.items() if value is not None}
            for ref, state in sidecar["expectations"].items()
        }
        populations.append({"id": row["population"], "path": row["population"],
                            "sha256": _sha(work / row["population"]),
                            "expectations": expectations})
    manifest = work / "parity.labels.json"
    manifest.write_text(json.dumps({"schema_version": "gnd-labels/1",
                                    "model_sha256": _sha(SYNTH_MODEL), "mode": "expected-state",
                                    "populations": populations}), encoding="utf-8")
    result = run_main(["measure", str(SYNTH_MODEL), "--labels", str(manifest), "--format", "json"])
    assert result.returncode == answer["exit"], result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["schema_version"] == answer["schema_version"]
    golden = json.loads((REPO_ROOT / answer["per_constraint_equals"]).read_text(encoding="utf-8"))
    ignored = set(answer["ignored_row_fields"])

    def rows(document: dict[str, Any]) -> list[dict[str, Any]]:
        return [{k: v for k, v in row.items() if k not in ignored}
                for row in document["per_constraint"]]

    assert rows(report) == rows(golden)
    assert report["checker_defects"] == golden["checker_defects"] == []


def test_d1_determinism(tmp_path: Path) -> None:
    case = next(c for c in CASES["cases"] if c["id"] == EXPECTED["D1"]["deterministic_over"])
    argv = _prepare(tmp_path, case)
    outputs = set()
    for seed in ("1", "2"):
        completed = subprocess.run(
            [sys.executable, "-m", "gnd", *argv], cwd=REPO_ROOT, capture_output=True, check=False,
            env={**os.environ, "PYTHONHASHSEED": seed},
        )
        assert completed.returncode == EXPECTED["D1"]["exit"], completed.stderr
        outputs.add(completed.stdout)
    assert len(outputs) == 1
