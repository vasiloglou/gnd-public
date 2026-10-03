"""D5: is per-step invariant checking affordable, measured against a gate fixed
BEFORE the numbers existed.

After every step the evaluator re-validates the whole resulting state. That
catches an operation whose intermediate state is illegal even though its start
and end states are fine -- but N steps over a population that grows each step is
theta(N*M + N^2/2), and design rule 2 forbids per-step work quadratic in a count
the input controls.

The gate two review rounds rejected said "accept on the timing test's numbers"
and then "reject if growth is worse than linear", neither of which can fail: no
estimator, no threshold, and benchmark points where the quadratic term is ~5% of
the total and invisible under noise. What follows is the repaired version, and
every number in it was chosen before a measurement was taken:

* **Measure where the term is visible.** Small population, many steps -- at
  M=100 the quadratic share climbs from roughly 10% at N=25 to 50% at N=200.
* **Estimator**: the least-squares slope of log(median elapsed) against log(N),
  after subtracting fixed overhead measured as a one-step walk at the same M.
* **Pass mark**: the slope predicted by a UNIT-COEFFICIENT reading of the cost
  model at these exact points, plus 10%. The first version fixed a round 1.25 in
  advance, and N*M + N^2/2 with both coefficients at 1 predicts 1.275 at M=100
  over N in {25..200}, so that gate failed a correct implementation.

  **The honest statement of what that shows, corrected after adversarial
  review.** Theta(N*M + N^2/2) fixes no coefficients: a cost with one tenth the
  quadratic coefficient sits in the same class and gives slope 1.039 here, so
  "no implementation could have passed 1.25" was too strong -- what was true is
  that THIS implementation, whose per-step cost really is one full check over a
  state that grows by one fact per step, could not. The ceiling below is
  therefore a calibrated assumption about the coefficients, not a consequence of
  the complexity class, and it is written down as one. (The prediction is also
  computed without subtracting the one-step overhead that the MEASURED series
  subtracts; applying the same subtraction moves it to about 1.291, which the
  10% tolerance absorbs either way.)

  The gate still asks design rule 2's question -- is the implementation worse
  than its own calibrated cost? -- and can still fail: the ceiling is about
  1.40, and a per-step check gone quadratic in the POPULATION, or one re-walking
  the trace each step, lands at 2.0. Whether the calibrated cost is acceptable
  at all is a separate decision, taken by the owner on the absolute numbers.
* **Admissibility**: 5 repetitions per point, median taken, and the fit must
  reach R^2 >= 0.95 -- below that the measurement is re-run, never read as a
  pass. A noisy run is not evidence of anything.
* **The fallback is named in advance**, so nothing is argued afterwards: if the
  gate fails, per-step checking becomes INCREMENTAL -- re-check only constraints
  touching a fact type the step modified. That is sound rather than a corner
  cut, because an untouched fact type's facts are identical to the previous
  state, which was already validated.

The measurement runs under a marker so an ordinary suite run stays fast; the
phase record quotes the numbers and the machine.
"""

from __future__ import annotations

import json
import math
import statistics
import time
from pathlib import Path
from typing import Any

import pytest
from test_public_transition_walks import MODEL

from gnd import transition
from gnd.model import load_model
from gnd.population import load_population_bytes

REPO_ROOT = Path(__file__).resolve().parent.parent

N_POINTS = (25, 50, 100, 200)
M_FIXED = 100
M_POINTS = (100, 1_000, 10_000)
N_FIXED = 10
REPETITIONS = 5
#: Tolerance over the cost model's own prediction. Wide enough for timing noise
#: on a development machine, narrow enough that a genuinely quadratic
#: implementation (slope -> 2.0) cannot hide inside it.
SLOPE_TOLERANCE = 1.10
MIN_R_SQUARED = 0.95


def _predicted_slope(points: tuple[int, ...], cost) -> float:
    """The log-log slope theta(N*M + N^2/2) itself produces at these points.

    Derived rather than assumed: the gate must be built from the cost model the
    design states, or it is a number someone picked.
    """
    return _slope_and_fit(list(points), [cost(point) for point in points])[0]


def _population(model, facts: int):
    """A legal population of roughly `facts` facts, all in one fact type.

    `expense_has_tag` carries no uniqueness constraint, so it can hold many
    facts per expense without the population itself being illegal -- the
    benchmark measures checking cost, not violation counting.
    """
    document = {
        "population": {
            "model": str(MODEL),
            "source": "synthetic",
            "covers": ["expense_has_tag"],
        },
        "facts": {
            "expense_has_tag": [
                {"expense": 1_000 + index, "tag": f"t{index}"} for index in range(facts)
            ]
        },
    }
    payload = (json.dumps(document) + "\n").encode("utf-8")
    return load_population_bytes(payload, source="<benchmark>", model=model)


def _walk(steps: int) -> list[dict[str, Any]]:
    """`steps` tag operations, each on its own expense so nothing collides."""
    return [
        {"op": "tag_expense", "bindings": {"expense": 5_000 + index, "new_tag": f"n{index}"}}
        for index in range(steps)
    ]


def _median_seconds(model, population, steps: int) -> float:
    walk = _walk(steps)
    timings = []
    for _ in range(REPETITIONS):
        started = time.perf_counter()
        transition.evaluate(model, population, population, walk)
        timings.append(time.perf_counter() - started)
    return statistics.median(timings)


def _slope_and_fit(xs: list[float], ys: list[float]) -> tuple[float, float]:
    """Least-squares slope of log y against log x, and the fit's R^2."""
    log_x = [math.log(x) for x in xs]
    log_y = [math.log(y) for y in ys]
    n = len(log_x)
    mean_x = sum(log_x) / n
    mean_y = sum(log_y) / n
    covariance = sum((x - mean_x) * (y - mean_y) for x, y in zip(log_x, log_y, strict=True))
    variance = sum((x - mean_x) ** 2 for x in log_x)
    slope = covariance / variance
    intercept = mean_y - slope * mean_x
    residual = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(log_x, log_y, strict=True))
    total = sum((y - mean_y) ** 2 for y in log_y)
    return slope, (1.0 - residual / total if total else 1.0)


@pytest.mark.slow
def test_per_step_checking_scales_linearly_in_the_number_of_steps() -> None:
    model = load_model(MODEL)
    population = _population(model, M_FIXED)
    overhead = _median_seconds(model, population, 1)
    measured = {n: _median_seconds(model, population, n) for n in N_POINTS}
    adjusted = [max(measured[n] - overhead, 1e-9) for n in N_POINTS]
    slope, r_squared = _slope_and_fit(list(N_POINTS), adjusted)

    predicted = _predicted_slope(N_POINTS, lambda n: n * M_FIXED + n * n / 2)
    ceiling = predicted * SLOPE_TOLERANCE
    report = ", ".join(f"N={n}: {measured[n] * 1000:.1f}ms" for n in N_POINTS)
    assert r_squared >= MIN_R_SQUARED, (
        f"the fit is too noisy to decide anything (R^2={r_squared:.3f}); re-run "
        f"on an idle machine rather than reading this as a pass. {report}"
    )
    assert slope <= ceiling, (
        f"per-step invariant checking grows as N^{slope:.3f} at M={M_FIXED}, worse "
        f"than the N^{predicted:.3f} its own cost model predicts (ceiling "
        f"{ceiling:.3f}). Something re-walks work it should not. The pre-named "
        f"fallback applies: incremental re-checking -- only the constraints "
        f"touching a fact type the step modified. {report}"
    )


@pytest.mark.slow
def test_per_step_checking_scales_linearly_in_the_population_size() -> None:
    """The second sweep GATES rather than informs -- a reviewer asked what the M
    measurements decided, and the answer was nothing.

    If this one fails, the finding is that the CHECKER is superlinear in
    population size. This phase may not touch checker.py, so that goes in the
    record as a finding rather than triggering a redesign here.
    """
    model = load_model(MODEL)
    measured = {}
    for facts in M_POINTS:
        population = _population(model, facts)
        measured[facts] = _median_seconds(model, population, N_FIXED)
    slope, r_squared = _slope_and_fit(list(M_POINTS), [measured[m] for m in M_POINTS])
    # At fixed N the cost model is theta(N*M + N^2/2), whose N^2/2 term is a
    # CONSTANT here -- so the prediction in M is linear, slope 1.0.
    ceiling = 1.0 * SLOPE_TOLERANCE
    report = ", ".join(f"M={m}: {measured[m] * 1000:.1f}ms" for m in M_POINTS)
    assert r_squared >= MIN_R_SQUARED, f"fit too noisy (R^2={r_squared:.3f}). {report}"
    assert slope <= ceiling, (
        f"checking grows as M^{slope:.3f} at N={N_FIXED}, over the {ceiling:.2f} "
        f"ceiling a linear-in-M model predicts. This is a finding about "
        f"checker.check, which this phase must not modify -- record it, do not "
        f"redesign around it. {report}"
    )
