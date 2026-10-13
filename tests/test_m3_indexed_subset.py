"""Indexed subset dispatch must preserve the frozen public and scalar contracts."""
import runpy
from dataclasses import replace
from pathlib import Path

import pytest
from test_public_branch_runtime import _build
from test_public_semantic_composition import _case

from gnd import api, semantic_rows, semantic_spec
from gnd.constraint_families import FAMILIES, resolve_hook
from gnd.correspondence import correspond_snapshot
from gnd.semantic_adapter import canonical_scalar

CASES = tuple(f"P2-{i:03d}" for i in range(86, 92))


@pytest.mark.parametrize("case_id", CASES)
def test_subset_public_result_avoids_quadratic_provider(case_id, tmp_path, monkeypatch):
    model, population = _build(case_id, tmp_path)
    expected = api.check(model, population)

    def reject(*args):
        raise AssertionError("quadratic pure subset provider reached")

    monkeypatch.setattr(semantic_spec, "_family_result_subset", reject)
    assert api.check(model, population) == expected


@pytest.mark.parametrize("case_id", CASES)
def test_subset_oracle_parity(case_id, tmp_path):
    constraint, snapshot, _ = _case(case_id, tmp_path)
    expected = semantic_spec.verdict_of(constraint, snapshot)
    assert semantic_rows.indexed_subset_verdict(constraint, snapshot) == expected
    model, population = _build(case_id, tmp_path)
    _, decision = correspond_snapshot(model, population)
    finding = next(r for r in decision.findings if r.constraint_id == constraint.ref)
    assert (finding.verdict, finding.reason_code, finding.witness) == expected


@pytest.mark.parametrize("values", [
    [(True,), (1,), (1.0,), (None,), (False,), (0,), (0.0,)],
    [("a", "b"), ("a",), ("b", "a"), ("a", "b")],
    [("2020-01-01T00:00:00Z",), ("2019-12-31T19:00:00-05:00",)],
])
def test_typed_identity_order_and_first_representative(values):
    rows = [tuple(canonical_scalar(v, None) for v in row) for row in values]
    expected = tuple(semantic_spec.canonical_distinct_rows(rows))
    assert semantic_rows.canonical_rows(rows) == expected
    for row in semantic_rows.canonical_rows(rows):
        assert any(row is original for original in rows)


def test_production_hook_registered_only_for_subset():
    assert FAMILIES["subset"].production == "indexed_subset_verdict"
    assert callable(resolve_hook(FAMILIES["subset"].production, vars(semantic_rows)))
    assert all(entry.production is None for name, entry in FAMILIES.items() if name != "subset")


@pytest.mark.parametrize("changes", [
    {"variant": "unknown"}, {"sequences": ()}, {"refused": "opaque-value"},
])
def test_subset_invalid_shape_refuses_like_oracle(changes, tmp_path):
    constraint, snapshot, _ = _case("P2-086", tmp_path)
    constraint = replace(constraint, **changes)
    assert semantic_rows.indexed_subset_verdict(constraint, snapshot) == semantic_spec.verdict_of(constraint, snapshot)


def test_native_measurement_counts_canonicalization_identity_work():
    root = Path(__file__).resolve().parents[1]
    measure = runpy.run_path(str(root / ".gnd-planning/milestones/analytics-m3-repairs/evidence/phase-7-native-layer.py"))["measure_identity_work"]
    scalar = canonical_scalar(1, None)
    rows, _, count = measure(lambda: semantic_rows.canonical_rows([(scalar,), (scalar,)]))
    assert rows == ((scalar,),)
    assert count == 2
