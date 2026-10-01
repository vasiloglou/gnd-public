"""The scoring core: the cell table, the partition invariant, the conditional
denominators, the n==0 guard, and the all-masked degenerate case (Task 1).

Every assertion here defends one property of "a metric that cannot come out
badly": the six cells partition the evidence, a lookup miss raises rather than
defaulting, duplicating conforming cases cannot move the false-pass rate, and a
constraint whose evidence is entirely masked cannot report three perfect zeroes.
"""

from __future__ import annotations

import random

import pytest

from gnd.measure.score import (
    CELLS,
    OUTCOMES,
    CellLookupError,
    Observation,
    PartitionError,
    classify,
    score_constraint,
    withholds_acceptance,
)
from gnd.synth.provenance import ExpectedState

# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #


def _exp(ground_truth: str, expected_verdict: str, reason: str | None = None) -> ExpectedState:
    return ExpectedState(
        ground_truth=ground_truth, expected_verdict=expected_verdict, reason=reason
    )


def _obs(ground_truth: str, expected_verdict: str, observed: str, modality: str) -> Observation:
    return Observation(_exp(ground_truth, expected_verdict), observed, modality)


# --------------------------------------------------------------------------- #
# 1. the cell table is total, 30 keys, and each outcome is a named OUTCOME
# --------------------------------------------------------------------------- #


def test_cells_is_total_over_all_thirty_keys() -> None:
    """2 modalities x 3 ground-truth states x 5 verdicts = 30 keys, all present,
    every value one of the six disjoint outcomes."""
    assert len(CELLS) == 30
    for (modality, ground_truth, verdict), outcome in CELLS.items():
        assert modality in ("alethic", "deontic")
        assert ground_truth in ("satisfied", "violated", "no-subjects")
        assert verdict in ("pass", "fail", "warning", "unchecked", "vacuous")
        assert outcome in OUTCOMES


#: The RESEARCH table, transcribed cell by cell (§"The full cell table"). ALETHIC
#: verbatim; DEONTIC is the same with fail/warning swapped and a deontic fail
#: impossible. A reviewer diffs THIS literal against RESEARCH, and the code's
#: CELLS against this.
_EXPECTED_ALETHIC = {
    ("satisfied", "pass"): "correct",
    ("satisfied", "fail"): "false_fail",
    ("satisfied", "warning"): "tool_defect",
    ("satisfied", "unchecked"): "undecided",
    ("satisfied", "vacuous"): "undecided",
    ("violated", "pass"): "false_pass",
    ("violated", "fail"): "correct",
    ("violated", "warning"): "tool_defect",
    ("violated", "unchecked"): "undecided",
    ("violated", "vacuous"): "masked_by_vacuity",
    ("no-subjects", "pass"): "false_pass",
    ("no-subjects", "fail"): "false_fail",
    ("no-subjects", "warning"): "tool_defect",
    ("no-subjects", "unchecked"): "undecided",
    ("no-subjects", "vacuous"): "correct",
}
_EXPECTED_DEONTIC = {
    ("satisfied", "pass"): "correct",
    ("satisfied", "fail"): "tool_defect",
    ("satisfied", "warning"): "false_fail",
    ("satisfied", "unchecked"): "undecided",
    ("satisfied", "vacuous"): "undecided",
    ("violated", "pass"): "false_pass",
    ("violated", "fail"): "tool_defect",
    ("violated", "warning"): "correct",
    ("violated", "unchecked"): "undecided",
    ("violated", "vacuous"): "masked_by_vacuity",
    ("no-subjects", "pass"): "false_pass",
    ("no-subjects", "fail"): "tool_defect",
    ("no-subjects", "warning"): "false_fail",
    ("no-subjects", "unchecked"): "undecided",
    ("no-subjects", "vacuous"): "correct",
}


@pytest.mark.parametrize("ground_truth,verdict,outcome", [
    (gt, v, o) for (gt, v), o in _EXPECTED_ALETHIC.items()
])
def test_alethic_cells_match_research(ground_truth: str, verdict: str, outcome: str) -> None:
    assert CELLS[("alethic", ground_truth, verdict)] == outcome


@pytest.mark.parametrize("ground_truth,verdict,outcome", [
    (gt, v, o) for (gt, v), o in _EXPECTED_DEONTIC.items()
])
def test_deontic_cells_match_research(ground_truth: str, verdict: str, outcome: str) -> None:
    assert CELLS[("deontic", ground_truth, verdict)] == outcome


# --------------------------------------------------------------------------- #
# 2. the expected-unchecked-by-design rows (C3 / Qwen / Kimi-HIGH)
# --------------------------------------------------------------------------- #


def test_textual_expected_unchecked_scores_correct_when_it_abstains() -> None:
    """`textual-not-mechanical`: {satisfied, unchecked} observed unchecked is a
    CORRECT abstention by design, NOT a coverage-gap undecided (C3). The reason
    code distinguishes it from a genuine gap."""
    textual = _exp("satisfied", "unchecked", "textual-not-mechanical")
    assert classify(textual, "unchecked", "alethic") == "correct"


def test_textual_expected_unchecked_pass_is_a_false_pass() -> None:
    """The checker claimed a decision it must not make on a textual constraint."""
    textual = _exp("satisfied", "unchecked", "textual-not-mechanical")
    assert classify(textual, "pass", "alethic") == "false_pass"


def test_textual_expected_unchecked_fail_is_a_tool_defect() -> None:
    """A `fail` on an unevaluable constraint is impossible — a tool defect."""
    textual = _exp("satisfied", "unchecked", "textual-not-mechanical")
    assert classify(textual, "fail", "alethic") == "tool_defect"


def test_a_genuine_coverage_gap_is_undecided_not_correct() -> None:
    """A DECIDED expectation the checker abstained on is a real undecided —
    distinguishable from the textual case above only via the expectation, which
    is exactly what C3's typed ExpectedState carries."""
    decided = _exp("satisfied", "pass", None)
    assert classify(decided, "unchecked", "alethic") == "undecided"


# --------------------------------------------------------------------------- #
# 2b. CELLS is the ONLY path — no exact-agreement short-circuit (CR-03)
# --------------------------------------------------------------------------- #

#: Every ``(modality, ground_truth, verdict)`` triple the table does NOT score
#: ``correct`` or ``masked_by_vacuity``. A sidecar naming one of these as its
#: ``expected_verdict`` is claiming the checker answers a violated (or empty)
#: universe correctly with the very verdict the table calls an error — an
#: internally inconsistent expectation, and the shape the deleted short-circuit
#: turned into ``correct``.
_INCONSISTENT_EXPECTATIONS = [
    (modality, ground_truth, verdict)
    for modality, table in (("alethic", _EXPECTED_ALETHIC), ("deontic", _EXPECTED_DEONTIC))
    for (ground_truth, verdict), outcome in table.items()
    if outcome not in ("correct", "masked_by_vacuity") and verdict != "unchecked"
]


@pytest.mark.parametrize(
    "modality,ground_truth,verdict", _INCONSISTENT_EXPECTATIONS, ids=lambda v: str(v)
)
def test_an_expectation_the_table_calls_an_error_is_refused(
    modality: str, ground_truth: str, verdict: str
) -> None:
    """`(violated, pass)` and `(no-subjects, pass)` are NOT `correct`.

    ``classify`` used to return ``correct`` for ANY exact agreement between the
    expectation and the observation, with a single carve-out for
    ``(violated, vacuous)``. That made the published table not the thing that
    decides the two cells this phase exists to watch: a sidecar saying
    ``{ground_truth: violated, expected_verdict: pass}`` scored a false pass as
    ``correct``. The table is now the only path, and an expectation it scores as
    an error is refused rather than defaulted.
    """
    from gnd.measure.score import InconsistentExpectationError

    expectation = ExpectedState.model_construct(
        ground_truth=ground_truth, expected_verdict=verdict, reason=None
    )
    with pytest.raises(InconsistentExpectationError):
        classify(expectation, verdict, modality)


@pytest.mark.parametrize(
    "modality,ground_truth,verdict,outcome",
    [
        (m, gt, v, o)
        for m, table in (("alethic", _EXPECTED_ALETHIC), ("deontic", _EXPECTED_DEONTIC))
        for (gt, v), o in table.items()
        if o in ("correct", "masked_by_vacuity") and v != "unchecked"
    ],
    ids=lambda v: str(v),
)
def test_a_consistent_expectation_meeting_its_own_verdict_scores_from_the_table(
    modality: str, ground_truth: str, verdict: str, outcome: str
) -> None:
    """The other side of the same coin, including the ONE documented exception.

    ``(violated, vacuous)`` observed ``vacuous`` stays ``masked_by_vacuity`` even
    though the generator predicted the vacuity — the prediction being right does
    not make "no subjects" a decision over a violated universe (D-02).
    """
    expectation = _exp(ground_truth, verdict)
    assert classify(expectation, verdict, modality) == outcome


def test_the_flagged_pairs_score_exactly_as_the_table_says() -> None:
    """The three reproductions from the review, pinned by value."""
    from gnd.measure.score import InconsistentExpectationError

    for expectation, observed, modality in (
        (("violated", "pass"), "pass", "alethic"),
        (("no-subjects", "pass"), "pass", "alethic"),
        (("satisfied", "warning"), "warning", "alethic"),
    ):
        state = ExpectedState.model_construct(
            ground_truth=expectation[0], expected_verdict=expectation[1], reason=None
        )
        with pytest.raises(InconsistentExpectationError):
            classify(state, observed, modality)

    # And with a CONSISTENT expectation, the same observations land in the cells
    # the table publishes rather than in `correct`.
    assert classify(_exp("violated", "fail"), "pass", "alethic") == "false_pass"
    assert classify(_exp("no-subjects", "vacuous"), "pass", "alethic") == "false_pass"


# --------------------------------------------------------------------------- #
# 3. a lookup miss RAISES rather than defaulting
# --------------------------------------------------------------------------- #


def test_a_new_verdict_state_raises_rather_than_defaulting() -> None:
    """A future verdict the table does not know must fail loud, so it cannot leak
    out of all three rates and improve each one."""
    decided = _exp("satisfied", "pass", None)
    with pytest.raises(CellLookupError):
        classify(decided, "brand-new-verdict", "alethic")


def test_a_new_ground_truth_state_raises() -> None:
    """`ground_truth` is a typed Literal, so a novel state can only reach the
    scorer by bypassing validation (a future generator writing a new label). The
    lookup must still raise rather than default."""
    weird = ExpectedState.model_construct(
        ground_truth="unheard-of-state", expected_verdict="pass", reason=None
    )
    with pytest.raises(CellLookupError):
        classify(weird, "fail", "alethic")


# --------------------------------------------------------------------------- #
# 4. the partition invariant
# --------------------------------------------------------------------------- #


#: The `(modality, ground_truth, expected_verdict)` triples a sidecar may
#: legitimately carry: exactly those the table scores `correct` (a correct
#: checker's answer), the `{violated, vacuous}` masked exception, and the
#: expected-unchecked-by-design rows rule 1 owns. Derived from CELLS rather than
#: listed, so the random sweep below cannot drift away from the guard (CR-03).
_CONSISTENT_EXPECTATIONS = [
    (modality, ground_truth, verdict)
    for (modality, ground_truth, verdict), outcome in CELLS.items()
    if outcome in ("correct", "masked_by_vacuity") or verdict == "unchecked"
]


def test_partition_holds_on_random_count_vectors() -> None:
    """Over randomised observation vectors, the six counters always sum to n.

    Expectations are drawn from the CONSISTENT set: an inconsistent one is now a
    refusal, not a scored cell (CR-03), so feeding them here would assert the
    partition over inputs the scorer is contracted to reject.
    """
    rng = random.Random(1234)
    verdicts = ("pass", "fail", "warning", "unchecked", "vacuous")
    for _ in range(200):
        observations = []
        for _ in range(rng.randint(0, 40)):
            modality, gt, ev = rng.choice(_CONSISTENT_EXPECTATIONS)
            observations.append(_obs(gt, ev, rng.choice(verdicts), modality))
        score = score_constraint(observations)
        assert sum(score.cells.values()) == score.n == len(observations)


def test_a_miscategorised_observation_is_refused_loudly(monkeypatch: pytest.MonkeyPatch) -> None:
    """The accounting refuses an observation that does not land in one of the six
    named cells rather than silently dropping it. A dropped observation is how
    the partition would break (sum < n), so score_constraint fails loud —
    PartitionError is the sum guard, and a bucket that is not one of the six
    raises before it can even be summed. Either way the miscategorisation cannot
    pass silently and quietly improve a rate."""
    import gnd.measure.score as score_mod

    real = score_mod.classify
    calls = {"n": 0}

    def liar(expected, observed, modality):
        calls["n"] += 1
        # One observation is miscategorised into a bucket the six-cell counter
        # does not carry — the accounting must not absorb it silently.
        return "not-a-real-outcome" if calls["n"] == 1 else real(expected, observed, modality)

    observations = [_obs("satisfied", "pass", "pass", "alethic") for _ in range(4)]
    monkeypatch.setattr(score_mod, "classify", liar)
    with pytest.raises((PartitionError, KeyError)):
        score_mod.score_constraint(observations)


# --------------------------------------------------------------------------- #
# 5. conditional denominators + the dilution metamorphic test (C2)
# --------------------------------------------------------------------------- #


def test_false_pass_rate_uses_the_conditional_denominator() -> None:
    """false_pass_rate = false_pass / expected_nonpass, not / n."""
    # 2 violated observations, one of which the checker false-passes; plus 8
    # satisfied conforming observations.
    obs = [
        _obs("violated", "fail", "pass", "alethic"),  # false pass
        _obs("violated", "fail", "fail", "alethic"),  # correct
    ] + [_obs("satisfied", "pass", "pass", "alethic") for _ in range(8)]
    score = score_constraint(obs)
    assert score.expected_nonpass == 2
    assert score.false_pass == 1
    assert score.false_pass_rate == 0.5  # 1/2, NOT 1/10


def test_dilution_does_not_move_the_false_pass_rate() -> None:
    """Duplicating unrelated SATISFIED observations adds to satisfied and n but
    not to expected_nonpass or false_pass — the mechanical proof the denominator
    is conditional, not prevalence (C2)."""
    base = [
        _obs("violated", "fail", "pass", "alethic"),  # false pass
        _obs("violated", "fail", "fail", "alethic"),  # correct
    ]
    lean = score_constraint(base)
    diluted = score_constraint(base + [_obs("satisfied", "pass", "pass", "alethic")] * 500)
    assert lean.false_pass_rate == diluted.false_pass_rate == 0.5
    assert diluted.n == 502 and lean.n == 2  # n moved, the rate did not


def test_false_fail_rate_uses_satisfied_denominator() -> None:
    obs = [
        _obs("satisfied", "pass", "fail", "alethic"),  # false fail
        _obs("satisfied", "pass", "pass", "alethic"),  # correct
        _obs("satisfied", "pass", "pass", "alethic"),  # correct
    ]
    score = score_constraint(obs)
    assert score.satisfied == 3
    assert score.false_fail == 1
    assert score.false_fail_rate == pytest.approx(1 / 3)


# --------------------------------------------------------------------------- #
# 6. the n==0 / zero-denominator guard (Gemini)
# --------------------------------------------------------------------------- #


def test_no_observations_yields_none_rates_not_zero_division() -> None:
    score = score_constraint([])
    assert score.n == 0
    assert score.false_pass_rate is None
    assert score.false_fail_rate is None
    assert score.undecided_rate is None
    assert score.coverage is None


def test_zero_expected_nonpass_yields_none_false_pass_rate() -> None:
    """A conforming-only corpus: no violating cases, so false_pass_rate is None
    (no data), NOT 0.0 — the C2/Gemini distinction the SUMMARY must preserve."""
    obs = [_obs("satisfied", "pass", "pass", "alethic") for _ in range(5)]
    score = score_constraint(obs)
    assert score.expected_nonpass == 0
    assert score.false_pass_rate is None
    assert score.false_fail_rate == 0.0  # satisfied != 0, so this rate is real


# --------------------------------------------------------------------------- #
# 7. the all-masked degenerate case, named
# --------------------------------------------------------------------------- #


def test_all_masked_by_vacuity_is_not_three_perfect_zeroes() -> None:
    """A constraint whose entire evidence is (violated, vacuous) reports
    undecided_rate == 1.0 and coverage == 0.0 — never false_pass 0.0 /
    false_fail 0.0 / undecided 0.0 over zero decided evidence."""
    obs = [_obs("violated", "fail", "vacuous", "alethic") for _ in range(7)]
    score = score_constraint(obs)
    assert score.cells["masked_by_vacuity"] == 7
    assert score.undecided_rate == 1.0
    assert score.coverage == 0.0
    assert score.decided == 0
    # false_pass numerator is 0 but its denominator (expected_nonpass) is visible.
    assert score.false_pass == 0
    assert score.expected_nonpass == 7
    assert score.false_pass_rate == 0.0  # 0/7 — a real rate with a visible base
    # The undecided rate re-absorbs masked_by_vacuity (D-02), so it is NOT zero.
    assert score.undecided_rate != 0.0


# --------------------------------------------------------------------------- #
# 8. the deontic carve-out on a NON-textual deontic constraint (Kimi)
# --------------------------------------------------------------------------- #


def test_deontic_false_pass_is_measured_against_the_verdict() -> None:
    """A violated deontic constraint expects `warning`; an observed `pass` is the
    false pass. Measuring against acceptance would report 0% by construction,
    because a deontic warning does not withhold acceptance."""
    violated_deontic = _exp("violated", "warning", None)
    assert classify(violated_deontic, "pass", "deontic") == "false_pass"
    assert classify(violated_deontic, "warning", "deontic") == "correct"


def test_withholds_acceptance_matches_pattern_3() -> None:
    """vacuous withholds for either modality; fail/unchecked only when alethic."""
    assert withholds_acceptance("vacuous", "alethic") is True
    assert withholds_acceptance("vacuous", "deontic") is True
    assert withholds_acceptance("fail", "alethic") is True
    assert withholds_acceptance("fail", "deontic") is False
    assert withholds_acceptance("unchecked", "alethic") is True
    assert withholds_acceptance("unchecked", "deontic") is False
    assert withholds_acceptance("pass", "alethic") is False
    assert withholds_acceptance("warning", "deontic") is False
