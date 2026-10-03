

from __future__ import annotations

import time

from gnd.exp import session_contract, session_eval


def _declaration(required_count: int):
    required = tuple(
        session_contract.RequiredOperation(op=f"op-{index}", bindings_subset={"value": index})
        for index in range(required_count)
    )
    return session_contract.WalkAcceptance(required_ops=required, forbidden_ops=())


def test_s01_eight_thousand_steps_and_two_thousand_floors_finish_under_five_seconds() -> None:
    steps = [
        {"op": f"op-{index % 2000}", "bindings": {"value": index % 2000, "extra": index}}
        for index in range(8000)
    ]
    started = time.monotonic()
    gaps = session_eval.walk_floor_gaps(_declaration(2000), steps)
    elapsed = time.monotonic() - started
    assert gaps == ()
    assert elapsed < 5.0


def test_s02_declared_work_bound_is_linear_while_nested_control_is_not(monkeypatch) -> None:
    observed_scalar_work = 0
    scalar_key = session_eval._walk_scalar_key

    def counted_scalar_key(value):
        nonlocal observed_scalar_work
        observed_scalar_work += 1
        return scalar_key(value)

    monkeypatch.setattr(session_eval, "_walk_scalar_key", counted_scalar_key)
    steps = [
        {"op": f"op-{index % 2000}", "bindings": {"value": index % 2000, "extra": index}}
        for index in range(8000)
    ]
    assert session_eval.walk_floor_gaps(_declaration(2000), steps) == ()
    step_bindings = 8000 * 2
    required_pairs = 2000
    forbidden_ids = 0
    linear_bound = step_bindings + required_pairs + forbidden_ids + 4 * (8000 + 2000)
    nested_control = 8000 * 2000
    assert observed_scalar_work <= linear_bound
    assert linear_bound < nested_control
    assert nested_control > linear_bound * 100
