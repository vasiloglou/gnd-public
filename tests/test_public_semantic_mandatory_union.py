"""Current semantic family controls on reviewed generic branch inputs."""
from __future__ import annotations

from pathlib import Path

import pytest
import test_public_branch_runtime as corpus

from gnd import semantic_spec as spec
from gnd.semantic_adapter import adapt_snapshot
from gnd.semantic_ir import IRConstraint, SnapshotIR


def _snapshot(case_id: str, tmp_path: Path) -> tuple[IRConstraint, SnapshotIR]:
    model, population = corpus._build(case_id, tmp_path)
    snapshot = adapt_snapshot(model, population)
    case = next(row for row in corpus.CASES["cases"] if row["id"] == case_id)
    constraint = next(row for row in snapshot.constraints if row.ref == case["ref"])
    return constraint, snapshot


@pytest.mark.parametrize(
    "case_id,state,witness",
    [
        ("P2-012", 1, []),
        ("P2-013", 0, ["3/1", "4/1"]),
        ("P2-014", 0, ["3/1", "4/1"]),
        ("P2-015", -1, []),
    ],
)
def test_frozen_mandatory_disjunctive_cases_match_nf_mand_disj_1(
    tmp_path: Path, case_id: str, state: int, witness: list[str]
) -> None:
    constraint, snapshot = _snapshot(case_id, tmp_path)
    before = hash(snapshot)
    assert spec.mandatory_disjunctive_state(constraint, snapshot) == state
    assert spec.mandatory_disjunctive_holds(constraint, snapshot) is (state == 1)
    assert [value.token for value in spec.mandatory_disjunctive_witness(constraint, snapshot)] == witness
    assert hash(snapshot) == before

