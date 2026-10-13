"""Scalar/origin algorithm contracts; no fabricated domain population."""
from collections.abc import Iterator, Sequence
from dataclasses import replace

import pytest

from gnd import correspondence as c
from gnd.semantic_adapter import SnapshotObservation, ValueOrigin
from gnd.semantic_ir import Scalar


def scalar(token: str = "1/1") -> Scalar:
    return Scalar("number", token, 1, 1, True, "number")


def origin(value: Scalar, raw: object = 1, role: str = "x", row: int = 0,
           source: str = "admitted", derived: str | None = None,
           deps: tuple = ()) -> ValueOrigin:
    return ValueOrigin(source, ("facts", "f", row, role), value, "number", raw, derived, deps)


def finding(value: Scalar, *, keys: tuple[str, ...] = (), rows: int = 3) -> c.CorrespondedFinding:
    return c.CorrespondedFinding("scope", "constraint", "subset", "alethic", "fail",
                                None, tuple((value,) for _ in range(rows)), keys, ("scope",))


def test_exact_spelling_unused_order_and_cycle_reuse() -> None:
    value = scalar()
    obs = SnapshotObservation((origin(value, 1), origin(value, 1.0, row=1)), (), (), ())
    result = c.project_finding(finding(value), obs)
    assert result.witness == ((1,), (1.0,), (1,))
    assert [type(row[0]) for row in result.witness] == [int, float, int]
    assert result.fact_refs == (("f", 0), ("f", 1))


def test_canonical_ambiguity_includes_consumed_and_role_filter() -> None:
    target = scalar(); a = scalar(); b = scalar()
    origins = (origin(a, 1, "x"), origin(b, 1.0, "y", 1))
    assert c._origin_value(target, origins, {0}) is c._MISSING
    assert c._origin_value(target, origins, set(), witness_key="$v") is c._MISSING
    value = c._origin_value(target, origins, set(), witness_key="x")
    assert type(value) is int and value == 1
    assert type(c._origin_value(b, origins, set())) is float
    assert c._origin_value(target, (origins[0],), {0}) == 1


def test_provenance_and_coordinate_policies_differ() -> None:
    value = scalar()
    invalid = origin(value, 7, "other", 9, "derived")
    admitted = origin(value, 1, "x", 2)
    derived = origin(value, 1.0, "x", 3, "derived", "f", (("facts", "seed", 0),))
    obs = SnapshotObservation((invalid, admitted, derived), (), (), ())
    result = c.project_finding(finding(value, keys=("x",), rows=2), obs)
    assert [type(row["x"]) for row in result.witness] == [int, float]
    assert result.fact_refs == (("f", 2), ("f", 3), ("f", 9))
    with pytest.raises(ValueError, match="admissible origin"):
        c.project_finding(finding(value, rows=1), replace(obs, origins=(invalid,)))
    invalid_admitted = replace(admitted, dependency_paths=(("facts", "seed", 0),))
    assert c._origin_value(value, (invalid_admitted,), set()) is c._MISSING


class CountingOrigins(Sequence[ValueOrigin]):
    def __init__(self, values: tuple[ValueOrigin, ...]) -> None:
        self.values = values
        self.walks = 0

    def __len__(self) -> int:
        return len(self.values)

    def __getitem__(self, key):
        return self.values[key]

    def __iter__(self) -> Iterator[ValueOrigin]:
        self.walks += 1
        return iter(self.values)


def test_snapshot_walks_origins_once_and_resets_used_per_finding(monkeypatch) -> None:
    value = scalar()
    origins = CountingOrigins((origin(value, 1), origin(value, 1.0, row=1)))
    obs = SnapshotObservation(origins, (), (), ())
    decision = c.SnapshotDecision((finding(value), finding(value)), 0, False, "refuse")
    original = c.project_finding
    calls = []
    def dispatch(row, observation):
        calls.append(observation)
        return original(row, observation)
    monkeypatch.setattr(c, "project_finding", dispatch)
    result = c.project_snapshot(decision, obs)
    assert calls == [obs, obs]
    assert result.findings[0] == result.findings[1]
    assert [type(row[0]) for row in result.findings[1].witness] == [int, float, int]
    assert origins.walks <= 1


def test_nested_snapshot_and_exception_restore_context(monkeypatch) -> None:
    value = scalar(); other = scalar("2/1")
    obs = SnapshotObservation((origin(value, 1),), (), (), ())
    nested = SnapshotObservation((origin(other, 2),), (), (), ())
    decision = c.SnapshotDecision((finding(value, rows=1),), 0, False, "refuse")
    original = c.project_finding
    def dispatch(row, observation):
        if observation is obs:
            inner = c.project_snapshot(replace(decision, findings=(finding(other, rows=1),)), nested)
            assert inner.findings[0].witness == ((2,),)
        return original(row, observation)
    monkeypatch.setattr(c, "project_finding", dispatch)
    assert c.project_snapshot(decision, obs).findings[0].witness == ((1,),)
    with pytest.raises(ValueError, match="admissible origin"):
        c.project_snapshot(replace(decision, findings=(finding(other, rows=1),)), obs)
    assert c.project_finding(finding(other, rows=1), nested).witness == ((2,),)
    assert c.project_snapshot(decision, obs).findings[0].witness == ((1,),)


@pytest.mark.parametrize("raw", [None, False])
def test_false_and_null_are_values(raw) -> None:
    value = scalar()
    assert c._origin_value(value, (origin(value, raw),), set()) is raw


def test_keyed_arity_and_unused_bad_coordinates_remain_unchanged() -> None:
    value = scalar(); other = scalar("2/1")
    bad = replace(origin(other), path=("facts", "f", "unused-bad-index", "x"))
    obs = SnapshotObservation((origin(value), bad), (), (), ())
    assert c.project_finding(finding(value, rows=1), obs).fact_refs == (("f", 0),)
    with pytest.raises(ValueError, match="zip"):
        c.project_finding(replace(finding(value, rows=1), witness_keys=("x", "y")), obs)


def test_indexed_canonical_selection_order_and_cross_bucket_consumption() -> None:
    value = scalar(); a = scalar(); b = scalar()
    obs = SnapshotObservation((origin(a, 1, "x"), origin(b, 1, "x", 1)), (), (), ())
    row = replace(finding(value, keys=("x",), rows=1), witness=((a,), (value,), (value,)))
    assert c.project_finding(row, obs).witness == ({"x": 1}, {"x": 1}, {"x": 1})
    from gnd.semantic_origins import OriginIndex, OriginSelection
    used = set()
    selected = OriginSelection(OriginIndex(obs.origins), used)
    assert selected.value(a, None) == (True, 1) and used == {0}
    assert selected.value(value, "x") == (True, 1) and used == {0, 1}
    assert selected.value(value, "x") == (True, 1) and used == {0, 1}
    assert selected.value(value, "missing") == (False, None)
    assert selected.value(Scalar("boolean", "1/1", 1, 1, False, "boolean"), None) == (False, None)


def test_context_tokens_are_restored_after_error() -> None:
    value = scalar()
    obs = SnapshotObservation((), (), (), ())
    decision = c.SnapshotDecision((finding(value, rows=1),), 0, False, "refuse")
    assert c._ORIGIN_INDEX.get() is None and c._ORIGIN_SELECTION.get() is None
    with pytest.raises(ValueError, match="admissible origin"):
        c.project_snapshot(decision, obs)
    assert c._ORIGIN_INDEX.get() is None and c._ORIGIN_SELECTION.get() is None
