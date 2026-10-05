"""Current semantic family controls on reviewed generic branch inputs."""
from __future__ import annotations

from pathlib import Path

import pytest
import test_public_branch_runtime as corpus

from gnd import semantic_spec as spec
from gnd.semantic_adapter import adapt_snapshot


def _frozen(case_id: str, tmp_path: Path):
    model, population = corpus._build(case_id, tmp_path)
    snapshot = adapt_snapshot(model, population)
    reference = corpus.CASE_BY_ID[case_id]["ref"]
    return next(row for row in snapshot.constraints if row.ref == reference), snapshot


FROZEN = {
    "P2-001": ("uniqueness", 1, []),
    "P2-002": ("uniqueness", 0, [["b1", "1/1"], ["b1", "2/1"]]),
    "P2-003": ("uniqueness", 0, [["b1", "1/1"], ["b1", "2/1"]]),
    "P2-004": ("uniqueness", 0, [["i1", "1/1"], ["i2", "1/1"]]),
    "P2-005": ("uniqueness", 1, []),
    "P2-006": ("uniqueness", 0, [["1/1", "R1"]]),
    "P2-007": ("uniqueness", 0, [["1/1", "R1"]]),
    "P2-039": ("frequency", 1, []),
    "P2-040": ("frequency", 0, [["2/1"]]),
    "P2-041": ("frequency", 0, [["p1"]]),
    "P2-042": ("frequency", 1, []),
    "P2-043": ("frequency", 0, [["1/1", "R1"]]),
    "P2-044": ("frequency", 0, [["1/1", "R1"]]),
    "P2-131": ("cardinality", 1, []),
    "P2-132": ("cardinality", 0, [["R1"], ["R2"], ["R3"], ["R4"]]),
    "P2-133": ("cardinality", 0, [["R1"], ["R2"], ["R3"], ["R4"]]),
    "P2-134": ("cardinality", 1, []),
    "P2-135": ("cardinality", 0, [["1/1"], ["5/1"], ["6/1"]]),
    "P2-136": ("cardinality", 0, [["1/1"], ["5/1"], ["6/1"]]),
}


@pytest.mark.parametrize("case_id", tuple(FROZEN))
def test_frozen_counting_cases_match_normative_clauses(tmp_path: Path, case_id: str) -> None:
    constraint, snapshot = _frozen(case_id, tmp_path)
    family, state, witness = FROZEN[case_id]
    before = hash(snapshot)
    assert getattr(spec, family + "_state")(constraint, snapshot) == state
    assert getattr(spec, family + "_holds")(constraint, snapshot) is (state == 1)
    actual = getattr(spec, family + "_witness")(constraint, snapshot)
    assert [[value.token for value in row] for row in actual] == witness
    assert hash(snapshot) == before

