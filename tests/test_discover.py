"""IK4: constraint discovery, ``gnd discover`` (induced-knowledge milestone).

Spec: .gnd-planning/milestones/induced-knowledge/notes/phase-IK4-spec.md. Under
IK4-D1 the cases are an owner-approved corpus: inputs in
tests/fixtures/induced_knowledge/ik4-corpus/cases.json, hand-written answers in
expected.json, and stories in that directory's README.md.
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
CORPUS = REPO_ROOT / "tests" / "fixtures" / "induced_knowledge" / "ik4-corpus"
CASES = json.loads((CORPUS / "cases.json").read_text(encoding="utf-8"))
EXPECTED = json.loads((CORPUS / "expected.json").read_text(encoding="utf-8"))["cases"]
ENVELOPE = {"source", "status", "modality", "provenance"}
POPULATION_CAP = 10 * 1024 * 1024


def _generated(kind: str, header_from: Path) -> str:
    header = header_from.read_text(encoding="utf-8").split("instances:")[0]
    if kind == "over-cap":
        rows = "".join(f'    - {{ person: {i}, team: "A" }}\n' for i in range(400_000))
        return header + "instances: {}\nfacts:\n  person_in_team:\n" + rows
    recipe = CASES["generated"]["near-cap"]
    people = recipe["persons"]
    parts = [
        "  person_in_team:\n",
        *(f'    - {{ person: {i}, team: "T{i % 200}" }}\n' for i in range(people)),
        "  person_has_grade:\n",
        *(f'    - {{ person: {i}, grade: "g{i % 5}" }}\n' for i in range(people)),
        "  team_led_by:\n",
        *(f'    - {{ team: "T{t}", leader: {t} }}\n' for t in range(200)),
        "  person_has_skill:\n",
        *(
            f'    - {{ person: {i}, skill: "s{(i + j) % 50}" }}\n'
            for i in range(people)
            for j in range(2)
        ),
    ]
    return header + "instances: {}\nfacts:\n" + "".join(parts)


def _prepare(tmp_path: Path, case: dict[str, Any]) -> tuple[list[str], Path, Path, Path]:
    model = tmp_path / case["model"]
    shutil.copyfile(CORPUS / case["model"], model)
    population_name = case["population"]
    if population_name.startswith("GENERATED:"):
        kind = population_name.split(":", 1)[1]
        population = tmp_path / f"{kind}.population.yaml"
        population.write_text(
            _generated(kind, CORPUS / "staff.population.yaml"), encoding="utf-8"
        )
    else:
        population = tmp_path / population_name
        if (CORPUS / population_name).exists():
            shutil.copyfile(CORPUS / population_name, population)
    out = tmp_path / "proposal.json"
    report = tmp_path / "report.json"
    if case.get("out_is_symlink"):
        target = tmp_path / "elsewhere.json"
        target.write_text("{}\n", encoding="utf-8")
        out.symlink_to(target)
    common = list(CASES["common_argv"])
    for flag in case.get("omit", []):
        index = common.index(flag)
        del common[index : index + 2]
    argv = [
        "discover", str(model), str(population), *common, *case["argv"],
        "--out", str(out), "--report", str(report),
    ]
    return argv, model, out, report


def _host(ref: str) -> str | None:
    if ref.startswith("fact_types["):
        return ref[len("fact_types[") : ref.index("]")]
    return None


def _core(constraint: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in constraint.items() if key not in ENVELOPE}


def _emitted(report: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "family": row["family"],
            "host": _host(row["ref"]),
            "constraint": _core(row["constraint"]),
            "support": row["support"],
            "examples": row["constraint"]["provenance"]["induction"]["examples"],
        }
        for row in report["emitted"]
    ]


@pytest.mark.parametrize("case", CASES["cases"], ids=lambda case: case["id"])
def test_ik4_corpus(tmp_path: Path, case: dict[str, Any]) -> None:
    answer = EXPECTED[case["id"]]
    argv, model, out, report_path = _prepare(tmp_path, case)
    result = run_main(argv)
    output = (result.stdout + result.stderr).decode("utf-8", errors="replace")
    assert result.returncode == answer["exit"], output
    if answer["exit"] != 0:
        return
    report = json.loads(report_path.read_text(encoding="utf-8"))
    emitted = _emitted(report)
    for row in emitted:
        support = row.pop("support")
        assert support["numerator"] == support["denominator"] > 0, row
        row["support"] = support["numerator"]
    if "emitted" in answer:
        expected = answer["emitted"]
        shown = [
            {key: value for key, value in row.items() if key != "examples" or "examples" in want}
            for row, want in zip(emitted, expected, strict=False)
        ]
        assert len(emitted) == len(expected)
        assert shown == expected
    for row in answer.get("present", []):
        assert {k: v for k, v in emitted[[e["constraint"] for e in emitted].index(row["constraint"])].items() if k != "examples"} == row
    for row in answer.get("absent", []):
        assert {"host": row["host"], "constraint": row["constraint"]} not in [
            {"host": e["host"], "constraint": e["constraint"]} for e in emitted
        ]
    if "rejected" in answer:
        assert report["rejected"] == answer["rejected"]
    if "suppressed" in answer:
        assert {k: v for k, v in report["suppressed"].items() if v} == answer["suppressed"]
    for key, value in answer.get("skipped", {}).items():
        skipped = report["skipped"][key]
        assert (sum(skipped.values()) if isinstance(skipped, dict) else skipped) == value
    for key, value in answer.get("bounds", {}).items():
        assert report["bounds"][key] == value
    if "near_misses" in answer:
        assert [
            {"family": row["family"], "host": row["host"], "constraint": _core(row["constraint"]),
             "violations": row["violations"], "subjects": row["subjects"],
             "counterexamples": row["counterexamples"]}
            for row in report["near_misses"]
        ] == answer["near_misses"]
    assert out.exists() is answer["proposal"]
    assert (report["proposal"] is not None) is answer["proposal"]
    if "work_ceiling" in answer:
        population = Path(argv[2])
        assert population.stat().st_size <= answer["population_bytes_max"]
        assert 0 < report["work"]["total"] <= answer["work_ceiling"]
    if answer.get("preview_exit") is not None:
        preview = run_main([
            "evolve", "preview", str(model), str(out), "--workspace", str(tmp_path),
            "--records", str(tmp_path / "records"), "--out", str(tmp_path / "preview.json"),
        ])
        assert preview.returncode == answer["preview_exit"], preview.stdout + preview.stderr
    if answer.get("deterministic"):
        first = (out.read_bytes(), report_path.read_bytes())
        for seed in ("1", "2"):
            out.unlink()
            subprocess.run(
                [sys.executable, "-m", "gnd", *argv], check=True, cwd=REPO_ROOT,
                env={**os.environ, "PYTHONHASHSEED": seed}, capture_output=True,
            )
            assert (out.read_bytes(), report_path.read_bytes()) == first


def test_answer_key_covers_every_case() -> None:
    assert set(EXPECTED) == {case["id"] for case in CASES["cases"]}
