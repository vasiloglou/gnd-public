"""Exact170 current correspondence projection cases over generic branch inputs."""
from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path

import pytest
from test_public_branch_runtime import _build

from gnd.correspondence import correspond_snapshot, project_snapshot


def _public_projection():
    path = Path(__file__).parent / "fixtures/public-branch-runtime/projection.json.gz"
    assert path.is_file() and not path.is_symlink()
    with path.open("rb") as stream:
        packed = stream.read(32769)
    assert len(packed) <= 32768
    assert hashlib.sha256(packed).hexdigest() == "bce0795a71ce68a2b97683a0f0f2cb4d76ff05d0b6d10b26096a44fbd4d3eb4e"
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(262145)
    assert len(raw) <= 262144
    document = json.loads(raw)
    assert len(document["cases"]) == len(document["answers"]) == 170
    return document["cases"], document["answers"]

CASES, ANSWERS = _public_projection()
def _direct_cases() -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    prefixes = (
        "snapshot:",
        "applicability:vacuity:",
        "applicability:join:",
        "applicability:implemented:",
    )
    for row in CASES:
        target = ANSWERS[row["case_id"]]["verdicts"][0]
        fixture = row["fixture"]
        if (
            fixture.startswith("proof/v6/scope/corpus/cases.json#")
            and target["scope_id"].startswith(prefixes)
            and ":phase1" not in target["scope_id"]
        ):
            rows.append((row["case_id"], fixture.split("#", 1)[1]))
    return rows


@pytest.mark.parametrize(("case_id", "phase2_case_id"), _direct_cases())
def test_frozen_semantic_rows_reach_the_correspondence_projection(
    case_id: str, phase2_case_id: str, tmp_path: Path
) -> None:
    model, population = _build(phase2_case_id, tmp_path)
    adapted, decision = correspond_snapshot(model, population)
    projection = project_snapshot(decision, adapted.observation)
    expected = ANSWERS[case_id]["verdicts"][0]
    finding = next(
        row for row in projection.findings if row.constraint_id == expected["constraint_ref"]
    )
    assert finding.scope_id == expected["scope_id"]
    assert finding.verdict == expected["verdict"]
    assert finding.reason_code == expected["reason_code"]
    assert json.loads(json.dumps(finding.witness)) == expected["witness"]

