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
    for number, row in enumerate(index["populations"]):
        sidecar = json.loads((work / row["sidecar"]).read_text(encoding="utf-8"))
        expectations = {
            ref: {key: value for key, value in state.items() if value is not None}
            for ref, state in sidecar["expectations"].items()
        }
        populations.append({"id": f"p{number}", "path": row["population"],
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


# ---- implementation tests (spec section 8: T1, T2, T5, T7, T8) ---------------

NAMED_CAUSES = {
    "E4": "cell table scores that pair",
    "E5": "unlabelled",
    "E6": "write 'id:u_person_team'",
    "E7": "no constraint has id 'nope'",
    "E8": "was written for model sha256",
    "E9": "not the manifest's",
    "E10": "populations/0/path",
    "E11": "failed to load",
    "E12": "symbolic link",
    "E15": "does not exist",
    "E16": "not valid JSON",
    "E17": "byte cap",
    "E18": "not valid JSON",
    "E19": "Additional properties",
    "E20": "populations/0/path",
    "E21": "names no constraint",
    "E22": "reason",
    "E23": "populations/0",
    "E24": "populations",
    "C3": "no constraint has id 'nope'",
    "C4": "rules",
    "C5": "rules",
}


@pytest.mark.parametrize("case_id", sorted(NAMED_CAUSES))
def test_t2_refusals_name_their_cause(tmp_path: Path, case_id: str) -> None:
    case = next(c for c in CASES["cases"] if c["id"] == case_id)
    result = run_main(_prepare(tmp_path, case))
    payload = json.loads(result.stdout)
    assert payload["exit_code"] == EXPECTED[case_id]["exit"]
    assert NAMED_CAUSES[case_id] in payload["error"], payload["error"]
    assert "per_constraint" not in payload and "rules" not in payload


def _schema_validator() -> Any:
    from jsonschema import Draft202012Validator

    from gnd.measure.report import load_measurement_schema

    return Draft202012Validator(load_measurement_schema())


@pytest.mark.parametrize("case_id", ["E1", "E2", "E3", "C1", "C2"])
def test_t5_labelled_reports_validate(tmp_path: Path, case_id: str) -> None:
    case = next(c for c in CASES["cases"] if c["id"] == case_id)
    report = json.loads(run_main(_prepare(tmp_path, case)).stdout)
    errors = list(_schema_validator().iter_errors(report))
    assert not errors, [error.message for error in errors]
    assert report["redaction"]["mode"] == "applied"
    work = report["labels"]["work"]
    assert work["total"] == work["populations"] + work["label_rows"] <= work["ceiling"]


def test_t5_schema_refuses_a_mixed_variant(tmp_path: Path) -> None:
    case = next(c for c in CASES["cases"] if c["id"] == "E2")
    report = json.loads(run_main(_prepare(tmp_path, case)).stdout)
    validator = _schema_validator()
    for mutate in (
        lambda r: r.update(seeds=[1]),
        lambda r: r.update(rules=[]),
        lambda r: r["checker_defects"][0].update(seed=1),
        lambda r: r.update(schema_version=5),
        lambda r: r.pop("labels"),
    ):
        broken = json.loads(json.dumps(report))
        mutate(broken)
        assert list(validator.iter_errors(broken)), mutate


def test_t1_schema_bounds_hold_directly() -> None:
    """C-F3: the 10,000 bound cannot be reached under the 1 MiB cap, so it is
    tested against the schema itself."""
    from jsonschema import Draft202012Validator

    schema = json.loads((REPO_ROOT / "src/gnd/labels.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    entry = {"id": "a", "path": "p.yaml", "sha256": "0" * 64, "class": "positive"}
    base = {"schema_version": "gnd-labels/1", "model_sha256": "0" * 64, "mode": "class",
            "rules": {"id:x": {"fires_on": "negative"}}}
    assert not list(validator.iter_errors({**base, "populations": [entry] * 10000}))
    assert list(validator.iter_errors({**base, "populations": [entry] * 10001}))
    assert list(validator.iter_errors({**base, "populations": [entry], "rules": {}}))
    long_ref = "id:" + "x" * 254
    assert list(validator.iter_errors({**base, "populations": [entry],
                                       "rules": {long_ref: {"fires_on": "negative"}}}))
    expected = {"schema_version": "gnd-labels/1", "model_sha256": "0" * 64,
                "mode": "expected-state",
                "populations": [{"id": "a", "path": "p.yaml", "sha256": "0" * 64,
                                 "expectations": {"constraints[0]": {
                                     "ground_truth": "satisfied", "expected_verdict": "pass"}}}]}
    assert not list(validator.iter_errors(expected))
    assert list(validator.iter_errors({**expected, "rules": base["rules"]}))


def test_t1_whitespace_in_a_pattern_string_is_refused(tmp_path: Path) -> None:
    case = next(c for c in CASES["cases"] if c["id"] == "E1")
    argv = _prepare(tmp_path, case)
    manifest = Path(argv[argv.index("--labels") + 1])
    document = json.loads(manifest.read_text(encoding="utf-8"))
    document["populations"][0]["id"] = "ok\n"
    manifest.write_text(json.dumps(document), encoding="utf-8")
    payload = json.loads(run_main(argv).stdout)
    assert payload["exit_code"] == 3 and "whitespace" in payload["error"]


def test_t8_promote_is_refused_with_labels(tmp_path: Path) -> None:
    case = next(c for c in CASES["cases"] if c["id"] == "E1")
    argv = _prepare(tmp_path, case)
    result = run_main([*argv, "--promote", str(tmp_path / "promoted")])
    assert result.returncode == 64
    assert not (tmp_path / "promoted").exists()


def test_t8_missing_model_is_66_after_the_manifest(tmp_path: Path) -> None:
    case = next(c for c in CASES["cases"] if c["id"] == "E1")
    argv = _prepare(tmp_path, case)
    argv[1] = str(tmp_path / "absent.orm.yaml")
    assert json.loads(run_main(argv).stdout)["exit_code"] == 66
    manifest = Path(argv[argv.index("--labels") + 1])
    manifest.write_text("{}", encoding="utf-8")
    assert json.loads(run_main(argv).stdout)["exit_code"] == 3


def test_t8_validation_order_is_pinned() -> None:
    """Spec §4 rule 3: manifest, then model, then binding, then populations."""
    import inspect

    from gnd.measure import service

    source = inspect.getsource(service._measure_labels)
    order = ["read_label_manifest(", "load_model(", "bind_manifest(", "score_populations("]
    positions = [source.index(token) for token in order]
    assert positions == sorted(positions)


def test_t8_a_symlinked_manifest_is_74(tmp_path: Path) -> None:
    case = next(c for c in CASES["cases"] if c["id"] == "E1")
    argv = _prepare(tmp_path, case)
    manifest = Path(argv[argv.index("--labels") + 1])
    link = manifest.with_name("link.labels.json")
    link.symlink_to(manifest)
    argv[argv.index("--labels") + 1] = str(link)
    assert run_main(argv).returncode == 74


def test_t7_text_rendering_for_both_modes(tmp_path: Path) -> None:
    for case_id, marker in (("E2", "CHECKER DEFECTS: 1"), ("C1", "fires_on=negative")):
        case = next(c for c in CASES["cases"] if c["id"] == case_id)
        argv = [a for a in _prepare(tmp_path / case_id, case) if a not in ("--format", "json")]
        result = run_main(argv)
        assert marker in result.stdout.decode("utf-8")
