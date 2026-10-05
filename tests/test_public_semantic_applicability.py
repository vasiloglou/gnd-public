"""Applicability denominator controls over every admitted generic branch pair."""
from __future__ import annotations

import pytest
import test_public_branch_runtime as corpus

from gnd import checker
from gnd import semantic_registry as registry

ADMITTED = tuple(
    key for key, row in corpus.BUILD_BY_ID.items() if row.get("admission") != "unvalidated"
)


@pytest.mark.parametrize("case_id", ADMITTED)
def test_applicability_contains_every_executed_snapshot_route(case_id, tmp_path):
    model, population = corpus._build(case_id, tmp_path)
    with registry.capture_branches() as classified:
        applicable = registry.applicable_scope_ids(model, population)
    assert classified == set(), "classifying applicability must not claim verdict execution"
    with registry.capture_branches() as reached:
        report = checker.check(model, population)
        checker.band(report)
    assert reached <= set(applicable), (case_id, sorted(reached - set(applicable)))
    assert applicable == tuple(sorted(set(applicable)))

