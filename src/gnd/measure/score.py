"""The verdict x ground-truth cell table, the partition invariant, and the rates.

This is the densest module in the phase and the one place "a metric that cannot
come out badly" would arrive through the *accounting* rather than the data. Two
mechanisms make that impossible:

1. **The six outcomes PARTITION the evidence.** Every (constraint, population)
   observation lands in exactly one of ``correct``, ``false_pass``,
   ``false_fail``, ``undecided``, ``masked_by_vacuity``, ``tool_defect`` and
   :func:`score_constraint` asserts ``sum(cells) == n``, raising
   :class:`PartitionError` — in production code, not only in a test. Without
   that assertion a future miscategorisation would leak cases out of all three
   published rates and improve every one of them.

2. **The cell lookup is TOTAL and a miss RAISES.** :data:`CELLS` materialises
   the RESEARCH table over all 30 ``(modality, ground_truth, verdict)`` keys;
   :func:`classify` never calls ``.get`` with a default, because a default is
   precisely how a new verdict or ground-truth state escapes every rate. An
   unrecognised key is a :class:`CellLookupError`.

**Conditional denominators (C2 — the load-bearing fix).** The published
``false_pass_rate`` is ``false_pass / expected_nonpass`` (the cases that SHOULD
be caught), NOT ``false_pass / n``. A prevalence share (``/n``) would let adding
unrelated conforming populations drive the headline toward zero without any
change in detection. ``false_fail_rate`` is likewise ``false_fail / satisfied``.
Every numerator ships beside its denominator, and a zero denominator yields
``None`` (never a ``ZeroDivisionError``) so a targeted subset of the corpus
reports "no data" rather than crashing.

**The undecided rate keeps ``vacuous`` inside it (D-02).**
``undecided_rate = (undecided + masked_by_vacuity) / n``. ``masked_by_vacuity``
is a DISJOINT cell in the partition — research asked for a named counter, not
for removal from the denominator — so it is visible AND re-absorbed, never a
silent leak.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from typing import Literal

from gnd.checker import Verdict
from gnd.synth.provenance import ExpectedState, GroundTruth

__all__ = [
    "CELLS",
    "OUTCOMES",
    "CellLookupError",
    "ConstraintScore",
    "InconsistentExpectationError",
    "Observation",
    "Outcome",
    "PartitionError",
    "classify",
    "score_constraint",
    "score_run",
    "withholds_acceptance",
]

Outcome = Literal[
    "correct",
    "false_pass",
    "false_fail",
    "undecided",
    "masked_by_vacuity",
    "tool_defect",
]

#: The six disjoint outcome labels, in the canonical order the payload and the
#: partition assertion use. They are exhaustive: :func:`classify` returns exactly
#: one of these for every input, so the six counters sum to the observation count.
OUTCOMES: tuple[Outcome, ...] = (
    "correct",
    "false_pass",
    "false_fail",
    "undecided",
    "masked_by_vacuity",
    "tool_defect",
)

_MODALITIES: tuple[str, ...] = ("alethic", "deontic")
_GROUND_TRUTHS: tuple[GroundTruth, ...] = ("satisfied", "violated", "no-subjects")
_VERDICTS: tuple[Verdict, ...] = ("pass", "fail", "warning", "unchecked", "vacuous")

#: Verdicts that count as a DECISION (coverage numerator). ``unchecked`` and
#: ``vacuous`` are abstentions, not decisions.
_DECIDED: frozenset[str] = frozenset({"pass", "fail", "warning"})


class PartitionError(AssertionError):
    """The six outcome counters did not sum to the observation count.

    A subclass of :class:`AssertionError` so it reads as the invariant breach it
    is. Raised by :func:`score_constraint` in PRODUCTION code (not only a test):
    if it ever fires, an observation was double-counted or dropped, and every
    rate computed from the counts is untrustworthy. It names the shortfall so
    the miscategorised state is findable.
    """


class CellLookupError(KeyError):
    """A ``(modality, ground_truth, verdict)`` triple is not in :data:`CELLS`.

    Raised rather than defaulted (see the module docstring). A miss means a new
    verdict state, ground-truth state, or modality reached the scorer — which
    must fail loud, because a default would file the new state under some
    existing outcome and improve or worsen a rate silently.
    """


class InconsistentExpectationError(CellLookupError):
    """A sidecar's ``(ground_truth, expected_verdict)`` pair contradicts :data:`CELLS`.

    An expectation names the verdict a CORRECT checker should emit, so the table
    must score that pair ``correct`` — or ``masked_by_vacuity``, the one
    documented exception (``{violated, vacuous}``: the generator can legitimately
    predict the vacuity, and the pair still has to stay visible in its own
    counter rather than score ``correct``). Anything else — ``{violated, pass}``,
    ``{no-subjects, pass}``, ``{satisfied, warning}`` — is a sidecar claiming the
    checker answers correctly with the very verdict the table calls an error.

    This is the class :func:`classify`'s exact-agreement short-circuit used to
    swallow: it returned ``correct`` whenever the observation equalled the
    expectation, so the two cells this phase exists to watch were decided by the
    short-circuit rather than by the published table. Refused, never defaulted.
    """


def _base_outcome(modality: str, ground_truth: str, verdict: str) -> Outcome:
    """The RESEARCH cell table as a rule (the DECIDED-expectation slice).

    Alethic table (RESEARCH §"The full cell table"):

    | gt \\ verdict | pass       | fail        | warning | unchecked | vacuous     |
    | satisfied     | correct    | false_fail  | defect  | undecided | undecided   |
    | violated      | false_pass | correct     | defect  | undecided | masked      |
    | no-subjects   | false_pass | false_fail  | defect  | undecided | correct     |

    Deontic is the same with ``fail`` and ``warning`` swapped: a violated deontic
    yields ``warning`` (correct), and ``fail`` never occurs (``_violation_verdict``
    maps a deontic violation to ``warning``), so a deontic ``fail`` is a
    ``tool_defect``. Rates for deontic compare against the VERDICT, not
    acceptance (the carve-out), which is why ``warning`` is the decided-violation
    verdict here rather than an accept.
    """
    # The impossible modality/verdict combos are tool defects regardless of
    # ground truth: an alethic warning never occurs, and a deontic fail never
    # occurs (checker.py:903, _violation_verdict).
    if modality == "alethic" and verdict == "warning":
        return "tool_defect"
    if modality == "deontic" and verdict == "fail":
        return "tool_defect"

    # The decided-accept verdict is `pass` for both modalities; the decided-
    # violation verdict (`fail` alethic / `warning` deontic) is the only other
    # decided verdict that reaches here, the impossible combos having returned
    # `tool_defect` above.
    accept = "pass"

    if verdict == "unchecked":
        # An abstention where a decision was due — a genuine coverage gap.
        return "undecided"
    if verdict == "vacuous":
        if ground_truth == "no-subjects":
            return "correct"  # decided "no subjects" over a genuinely empty universe
        if ground_truth == "violated":
            return "masked_by_vacuity"  # the checker had data and answered "no subjects"
        return "undecided"  # satisfied + vacuous: precision loss, an abstention

    # A decided verdict (accept or violation) from here on.
    if ground_truth == "satisfied":
        return "correct" if verdict == accept else "false_fail"
    if ground_truth == "violated":
        if verdict == accept:
            return "false_pass"  # the cell that matters — a violation waved through
        return "correct"  # the violation verdict on a violated universe
    # no-subjects: an accept is a false pass (F-02/F-05); the violation verdict on
    # a genuinely empty universe is a false FAIL. The cardinality-min-over-empty
    # exception does NOT reach here — it is labelled `violated` at derivation time,
    # so it routes through the `violated` branch above where `fail` is correct.
    if verdict == accept:
        return "false_pass"
    return "false_fail"


#: The materialised total cell table — all 30 ``(modality, ground_truth,
#: verdict)`` keys, so the accounting is auditable as DATA and a lookup miss
#: raises. Diff this against RESEARCH §"The full cell table" cell by cell.
CELLS: dict[tuple[str, str, str], Outcome] = {
    (modality, ground_truth, verdict): _base_outcome(modality, ground_truth, verdict)
    for modality, ground_truth, verdict in product(_MODALITIES, _GROUND_TRUTHS, _VERDICTS)
}


def withholds_acceptance(verdict: str, modality: str) -> bool:
    """Research Pattern 3, verbatim: does this verdict withhold acceptance?

    The projection of run-level ``acceptance_ready`` onto one constraint, pinned
    to :func:`gnd.checker.band` ``== 0`` by ``tests/test_measure_projection.py``.
    ``vacuous`` withholds for EITHER modality (``has_vacuous`` is not
    modality-filtered — checker.py:118-120); ``fail`` and ``unchecked`` withhold
    only when alethic (their two siblings ARE modality-filtered). A duplicated
    comprehension is how exit bands drift apart, so this mirrors the three
    ``CheckReport`` properties rather than re-deriving acceptance.
    """
    if verdict == "vacuous":
        return True
    return modality == "alethic" and verdict in ("fail", "unchecked")


def classify(expected: ExpectedState, observed: str, modality: str) -> Outcome:
    """Score one observation into exactly one of the six :data:`OUTCOMES`.

    Total and mutually exclusive. The observed verdict is compared against the
    EXPECTED one, so an expected-unchecked-by-design constraint (a ``textual``
    alethic, a derivation-only ``subtype-partition``) scores ``correct`` when it
    abstains rather than inflating the undecided rate (C3).

    Order matters:

    1. **Abstention by design** (``expected_verdict == 'unchecked'``): the
       checker is EXPECTED not to decide. ``unchecked`` is ``correct``; a
       ``pass``/``warning`` is a ``false_pass`` (it claimed a decision it must
       not make); a ``fail`` is a ``tool_defect`` (impossible on an unevaluable
       constraint); a ``vacuous`` is ``masked_by_vacuity``.
    2. **The expectation itself must be consistent with the table.** Its
       ``(ground_truth, expected_verdict)`` pair is checked against
       :data:`CELLS`, which must score it ``correct`` — or
       ``masked_by_vacuity``, the ONE documented exception
       (``{violated, vacuous}``: the generator can legitimately predict the
       vacuity — plan 05's family-emptied ``mandatory``, whose instances stay
       observable elsewhere — and the pair still has to stay visible in its own
       counter rather than score ``correct`` and vanish). Anything else is an
       :class:`InconsistentExpectationError`.
    3. The RESEARCH table then decides EVERY remaining case, via a TOTAL lookup
       that RAISES on a miss.

    There is deliberately **no exact-agreement short-circuit**. The one this
    replaces returned ``correct`` whenever ``observed == expected_verdict``,
    carving out only ``(violated, vacuous)`` — so ``(violated, pass)`` and
    ``(no-subjects, pass)``, the two cells the F-02/F-05 defect family lives in,
    were decided by the short-circuit rather than by the table a reviewer audits.
    A consistent expectation meeting its own verdict lands on a ``correct`` cell
    anyway; the table says so, which is the point.
    """
    if expected.expected_verdict == "unchecked":
        if observed == "unchecked":
            return "correct"
        if observed in ("pass", "warning"):
            return "false_pass"
        if observed == "vacuous":
            return "masked_by_vacuity"
        # fail on a constraint the checker must not mechanically decide.
        return "tool_defect"

    expectation_key = (modality, expected.ground_truth, expected.expected_verdict)
    if expectation_key not in CELLS:
        raise CellLookupError(
            f"no cell for the EXPECTATION {expectation_key!r} — a new verdict, "
            f"ground-truth, or modality state reached the scorer. Refusing to "
            f"default it (a default is how a state leaks out of every published "
            f"rate and improves each one)."
        )
    if CELLS[expectation_key] not in ("correct", "masked_by_vacuity"):
        raise InconsistentExpectationError(
            f"the sidecar claims ground_truth={expected.ground_truth!r} is "
            f"answered correctly by {expected.expected_verdict!r}, but the cell "
            f"table scores that pair {CELLS[expectation_key]!r} — an internally "
            f"inconsistent expectation, refused rather than defaulted to "
            f"'correct'."
        )

    key = (modality, expected.ground_truth, observed)
    if key not in CELLS:
        raise CellLookupError(
            f"no cell for {key!r} — a new verdict, ground-truth, or modality "
            f"state reached the scorer. Refusing to default it (a default is how "
            f"a state leaks out of every published rate and improves each one)."
        )
    return CELLS[key]


@dataclass(frozen=True)
class Observation:
    """One scored (constraint, population) datum: the expectation the sidecar
    recorded, the verdict the checker emitted, and the modality."""

    expected: ExpectedState
    observed: str
    modality: str


def _rate(numerator: int, denominator: int) -> float | None:
    """A rate, or ``None`` when the denominator is zero (Gemini n==0 guard).

    A zero denominator is "no data", not a division error — a targeted subset of
    the corpus, or a constraint with no violating cases, reports ``None`` rather
    than crashing the whole run.
    """
    if denominator == 0:
        return None
    return numerator / denominator


@dataclass
class ConstraintScore:
    """The scored result for one constraint over the whole corpus.

    Carries the six raw counters (the partition audit trail), the two
    conditional denominators, the three published rates each beside its
    numerator and denominator, coverage, and the two selective rates. Nothing
    here averages across constraints — every number is one constraint's own.
    """

    n: int
    cells: dict[str, int]
    decided: int
    coverage: float | None
    #: Denominators, published so a rate can never be read without its base.
    expected_nonpass: int
    satisfied: int
    #: Published rates (conditional denominators — C2).
    false_pass_rate: float | None
    false_fail_rate: float | None
    undecided_rate: float | None
    #: Selective rates, conditioned on the checker having decided.
    selective_false_pass: float | None
    selective_false_fail: float | None
    ground_truth_states_seen: list[str] = field(default_factory=list)

    @property
    def false_pass(self) -> int:
        return self.cells["false_pass"]

    @property
    def false_fail(self) -> int:
        return self.cells["false_fail"]


def score_constraint(
    observations: list[Observation], *, population_count: int | None = None
) -> ConstraintScore:
    """Fold a constraint's observations into the six cells and the rates.

    Asserts TWO invariants and raises :class:`PartitionError` on either — both in
    production code, not only in a test, because both are the audit path's
    backbone:

    * **the partition**, ``sum(cells) == n``: no observation double-counted or
      dropped between the classification and the counters;
    * **the census**, ``n == population_count``: every population in the corpus
      contributed exactly one observation to this row.

    The census is the WR-01 reconciliation's missing half (02-VERIFICATION F-4).
    That check is SET-based — ``declared - scored`` — so it sees a constraint
    that vanishes from EVERY population and cannot see one that vanishes from
    SOME. Dropping half the ring corpus's verdicts for one ref left the row at
    ``n=36`` of 72 with every rate still reading 0.0, ``coverage_fraction`` still
    1.0, and exit 0: half the evidence gone under an unchanged number. The
    partition alone cannot catch it either — 36 observations partition perfectly
    into 36 cells.

    ``population_count`` is optional so a caller scoring a subset (a unit test,
    an ad-hoc probe) is not forced to assert a census it does not have; the
    aggregate report always supplies it.
    """
    cells: dict[str, int] = dict.fromkeys(OUTCOMES, 0)
    expected_nonpass = 0
    satisfied = 0
    decided = 0
    states_seen: set[str] = set()

    for obs in observations:
        outcome = classify(obs.expected, obs.observed, obs.modality)
        cells[outcome] += 1
        states_seen.add(obs.expected.ground_truth)
        if obs.expected.ground_truth in ("violated", "no-subjects"):
            expected_nonpass += 1
        if obs.expected.ground_truth == "satisfied":
            satisfied += 1
        if obs.observed in _DECIDED:
            decided += 1

    n = len(observations)
    total = sum(cells.values())
    if total != n:
        raise PartitionError(
            f"the six outcome counters sum to {total} but there were {n} "
            f"observations — an observation was double-counted or dropped, so "
            f"every rate is untrustworthy. Cells: {cells}."
        )
    if population_count is not None and n != population_count:
        raise PartitionError(
            f"this constraint was scored on {n} observation(s) over a corpus of "
            f"{population_count} population(s) — it is missing from "
            f"{population_count - n} of them (or double-counted in "
            f"{n - population_count}), so every rate below is computed on a "
            f"denominator its reader cannot see. A rate over half the evidence "
            f"reads exactly like a rate over all of it."
        )

    undecided_masked = cells["undecided"] + cells["masked_by_vacuity"]
    return ConstraintScore(
        n=n,
        cells=cells,
        decided=decided,
        coverage=_rate(decided, n),
        expected_nonpass=expected_nonpass,
        satisfied=satisfied,
        false_pass_rate=_rate(cells["false_pass"], expected_nonpass),
        false_fail_rate=_rate(cells["false_fail"], satisfied),
        undecided_rate=_rate(undecided_masked, n),
        selective_false_pass=_rate(cells["false_pass"], decided),
        selective_false_fail=_rate(cells["false_fail"], decided),
        ground_truth_states_seen=sorted(states_seen),
    )


def score_run(
    observations_by_ref: dict[str, list[Observation]],
    *,
    population_count: int | None = None,
) -> dict[str, ConstraintScore]:
    """Score every constraint independently. Keys preserved; no cross-constraint
    aggregation — D-01 forbids a single blended accuracy number.

    ``population_count`` is forwarded to each row's census invariant (F-4).
    """
    return {
        ref: score_constraint(obs, population_count=population_count)
        for ref, obs in observations_by_ref.items()
    }
