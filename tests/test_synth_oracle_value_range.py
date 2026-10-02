"""The independent oracle's ``value``-family semantics (02-VERIFICATION F-1, F-2).

Since CR-02 the constructive witness is the **sole** source of every published
expectation, so a wrong witness does not merely miss something — it publishes
the checker's correct verdict as an error. Verification found two instances in
one pass, both in the ``value`` family, both in the same direction that names
the checker for the oracle's mistake:

* **F-1** — ``_witness`` read ``allowed`` and ``range`` and never ``ranges``,
  the plural form ``orm-meta.schema.json``'s ``oneOf`` permits and the checker
  implements. The loop body never ran, so the witness returned SATISFIED over a
  population violating every interval, and ``gnd measure`` published
  ``false_fail_rate: 1.0`` at exit 0 against a checker correct on every
  population.
* **F-2** — ``_in_range`` returned ``False`` (violated) for every non-numeric
  value, though the meta-schema types range bounds ``["string", "number"]`` and
  constraint-reference.md calls the family *"numeric / character ranges"*. Over
  a String- or Date-domain range the oracle labelled a CONFORMING population
  violated, and the shipped fixture ``unresolvable_bound.orm.yaml`` quarantined
  at exit 6 as ``candidate-false-pass`` — blaming the checker for the one
  normative answer available to it.

Every test here was written RED against the pre-fix tree and observed to fail
for the reason its assertion names. Each guard is mutation-checked in
02-REVIEW-FIX.md: the receipts record which test turns red when the guard is
removed.

The controls matter as much as the locks. ``_value_witness`` could satisfy the
F-1 test by answering "violated" to every ``ranges`` constraint, and the F-2
guard could satisfy its test by abstaining on every value; the paired
``…_lies_in_the_second_range`` and ``…_still_decides_two_strings`` tests are
what make those cheap answers fail.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gnd.checker import check
from gnd.cli import main
from gnd.measure.score import ExpectedState, classify
from gnd.model import load_model
from gnd.population import load_population
from gnd.synth.assemble import _direct_subtypes, _in_range, _witness

REPO_ROOT = Path(__file__).resolve().parent.parent
UNRESOLVABLE_BOUND = (
    REPO_ROOT / "tests" / "fixtures" / "adversarial" / "models" / "unresolvable_bound.orm.yaml"
)

# --------------------------------------------------------------------------- #
# fixtures — models built inline, so the shape under test is visible beside the
# assertion rather than one directory away
# --------------------------------------------------------------------------- #

_HEADER = """\
version: 1
source: { kind: text-conversation, confidence: standard, mode: guided }
object_types:
  - id: item
    name: Item
    kind: entity
    reference: { mode: popular, value_type: item_id }
  - id: item_id
    name: ItemId
    kind: value
    primitive: String
  - id: qty
    name: Qty
    kind: value
    primitive: %(primitive)s
fact_types:
  - id: item_has_qty
    reading: "{Item} has qty {Qty}"
    roles:
      - { object_type: item, role_name: item }
      - { object_type: qty, role_name: qty }
constraints:
  - type: value
    object_type: qty
"""

_PROVENANCE = """\
    source: explicit
    status: confirmed
    modality: %(modality)s
    provenance:
      user_quote: "A quantity is 1 to 10, or 90 to 100."
"""

_PLURAL_RANGES = """\
    ranges:
      - { min: 1, max: 10 }
      - { min: 90, max: 100 }
"""


def _ranges_model(tmp_path: Path, *, modality: str = "alethic") -> Path:
    path = tmp_path / f"plural_ranges_{modality}.orm.yaml"
    path.write_text(
        _HEADER % {"primitive": "Integer"}
        + _PLURAL_RANGES
        + _PROVENANCE % {"modality": modality},
        encoding="utf-8",
    )
    return path


def _string_range_model(tmp_path: Path) -> Path:
    """A Date-domain range — bounds typed ``string`` by the meta-schema, ordered
    lexically-and-therefore-chronologically by ISO-8601 construction."""
    path = tmp_path / "date_range.orm.yaml"
    path.write_text(
        _HEADER % {"primitive": "Date"}
        + "    range: { min: '2020-01-01', max: '2029-12-31' }\n"
        + _PROVENANCE % {"modality": "alethic"},
        encoding="utf-8",
    )
    return path


def _doc(model_ref: str, qty: object) -> dict:
    return {
        "population": {
            "model": model_ref,
            "source": "synthetic",
            "covers": ["item_has_qty"],
        },
        "facts": {"item_has_qty": [{"item": "i1", "qty": qty}]},
    }


def _witness_of(model_path: Path, qty: object) -> bool | None:
    model = load_model(str(model_path))
    doc = _doc(model_path.name, qty)
    return _witness(model.constraints[0], None, doc, model, _direct_subtypes(model))


def _checker_verdict(model_path: Path, tmp_path: Path, qty: object) -> str:
    model = load_model(str(model_path))
    pop_path = tmp_path / "population.json"
    pop_path.write_text(json.dumps(_doc(model_path.name, qty)), encoding="utf-8")
    report = check(model, load_population(str(pop_path), model=model))
    return next(v.verdict for v in report.verdicts if v.constraint_ref == "constraints[0]")


def _expected_state(model_path: Path, qty: object):
    from gnd.synth.mutate import expected_state

    model = load_model(str(model_path))
    doc = _doc(model_path.name, qty)
    return expected_state(model.constraints[0], None, doc, model, _direct_subtypes(model))


# --------------------------------------------------------------------------- #
# F-1 — the plural `ranges` form
# --------------------------------------------------------------------------- #


def test_the_witness_reports_violated_over_a_value_outside_every_range(tmp_path) -> None:
    """RED before the fix: ``True``.

    ``qty=50`` is outside ``[1,10]`` and outside ``[90,100]``. The pre-fix
    witness read only ``constraint['range']``, found ``None``, skipped the loop
    body and returned the initial ``True`` — SATISFIED over a population that
    violates the constraint on its only fact.
    """
    model_path = _ranges_model(tmp_path)
    assert _witness_of(model_path, 50) is False


def test_the_checker_and_the_witness_now_agree_on_the_violating_population(
    tmp_path,
) -> None:
    """The disagreement F-1 manufactured, gone. The checker was always right
    here; it is the oracle that changed."""
    model_path = _ranges_model(tmp_path)
    assert _checker_verdict(model_path, tmp_path, 50) == "fail"
    assert _witness_of(model_path, 50) is False


@pytest.mark.parametrize("qty", [1, 5, 10, 90, 100])
def test_the_witness_reports_satisfied_when_a_value_lies_in_either_range(
    tmp_path, qty
) -> None:
    """The control on the F-1 lock, and the reason this is an implementation of
    the disjunction rather than a blanket abstention.

    ``ranges`` is a DISJUNCTION (constraint-reference.md: *"one or more numeric
    / character ranges"*), so a value conforms when it lies in ANY interval —
    including the second. A witness that answered "violated" to every ``ranges``
    constraint would pass the test above and fail this one.
    """
    model_path = _ranges_model(tmp_path)
    assert _witness_of(model_path, qty) is True
    assert _checker_verdict(model_path, tmp_path, qty) == "pass"


def test_the_published_expectation_for_a_ranges_violation_is_violated(tmp_path) -> None:
    """The path that actually reaches a payload.

    ``expected_state`` is the sole source of every sidecar expectation since
    CR-02, and it reads this witness. Before the fix it published
    ``{satisfied, pass}`` over a population violating every interval.
    """
    model_path = _ranges_model(tmp_path)
    state = _expected_state(model_path, 50)
    assert state is not None
    assert (state.ground_truth, state.expected_verdict) == ("violated", "fail")


def test_a_deontic_ranges_violation_no_longer_scores_a_fabricated_false_fail(
    tmp_path,
) -> None:
    """F-3, which F-1 caused and F-1's fix closes.

    Making the constraint deontic walks the whole pipeline clean — the C1
    quarantine inspects alethic failures only — so ``gnd measure`` published
    ``false_fail_rate: 1.0`` at exit 0, ``checker_defects: []``, against a
    checker correct on every population. The rate was the oracle's, not the
    checker's: expectation ``{satisfied, pass}`` against an observed ``warning``
    lands on ``CELLS[('deontic', 'satisfied', 'warning')] == 'false_fail'``.
    """
    model_path = _ranges_model(tmp_path, modality="deontic")
    observed = _checker_verdict(model_path, tmp_path, 50)
    assert observed == "warning"

    state = _expected_state(model_path, 50)
    assert state is not None
    assert (state.ground_truth, state.expected_verdict) == ("violated", "warning")

    outcome = classify(
        ExpectedState(ground_truth=state.ground_truth, expected_verdict=state.expected_verdict),
        observed,
        "deontic",
    )
    assert outcome == "correct"


# --------------------------------------------------------------------------- #
# F-2 — a bound the value cannot be ordered against
# --------------------------------------------------------------------------- #


def test_the_witness_makes_no_claim_over_a_bound_it_cannot_order(tmp_path) -> None:
    """RED before the fix: ``False`` — VIOLATED.

    ``unresolvable_bound.orm.yaml`` is the shipped fixture whose ``mass`` type
    carries a unit-based reference, so ``resolve_primitive`` returns ``None``,
    the loader's type check is deliberately skipped (D-05: resolve or skip,
    never guess), and a String reaches an alethic numeric range intact. The
    checker declines (``bound-type-mismatch``, band 4); the oracle must decline
    too, and used to convict.
    """
    model = load_model(str(UNRESOLVABLE_BOUND))
    doc = {
        "population": {
            "model": UNRESOLVABLE_BOUND.name,
            "source": "synthetic",
            "covers": ["batch_has_mass"],
        },
        "facts": {"batch_has_mass": [{"batch": "b1", "mass": "heavy"}]},
    }
    assert _witness(model.constraints[0], None, doc, model, _direct_subtypes(model)) is None


def test_the_shipped_fixture_no_longer_quarantines_the_checker(tmp_path, capsys) -> None:
    """The verifier's own reproduction, flipped.

    Before: ``exit 6``, a retained ``quarantine/`` case whose record reads
    ``kind: candidate-false-pass``, ``constraints[0]: witness=violated
    observed=unchecked`` — and 02-MEASUREMENT.md obliges a reader of exit 6 to
    *"reproduce, fix, and promote a corpus case"*, sending them after a checker
    defect that does not exist.

    After: ``exit 5``, ``not-derivable``, the same honest outcome
    ``uncomparable_literal.orm.yaml`` already gets from ``_comparison_literal``
    two functions away. The generator cannot label this constraint, and says so
    about ITSELF.
    """
    out = tmp_path / "out"
    assert main(["synth", str(UNRESOLVABLE_BOUND), "--class", "conforming", "--seed", "1", "--out", str(out)]) == 5
    captured = capsys.readouterr()
    assert "no independent expected-state oracle" in captured.out + captured.err
    assert "candidate-false-pass" not in captured.out + captured.err
    assert not (out / "quarantine").exists()


def test_the_witness_still_decides_a_string_domain_range(tmp_path) -> None:
    """The control on the F-2 lock: abstention is for values with NO order, not
    for every value that is not a number.

    ``orm-meta.schema.json`` types range bounds ``["string", "number"]`` and the
    checker orders strings, so a Date-domain range is decidable in both
    directions. A guard that answered ``None`` to everything non-numeric would
    pass the two tests above and fail this one.
    """
    model_path = _string_range_model(tmp_path)
    assert _witness_of(model_path, "2021-06-15") is True
    assert _checker_verdict(model_path, tmp_path, "2021-06-15") == "pass"
    assert _witness_of(model_path, "2019-12-31") is False
    assert _checker_verdict(model_path, tmp_path, "2019-12-31") == "fail"


@pytest.mark.parametrize(
    ("value", "why"),
    [
        (True, "bool<:int and True == 1, so a boolean lands INSIDE 1..100"),
        (float("nan"), "every ordered comparison with NaN is unordered (IEEE 754 §5.11)"),
        ("heavy", "a string has no order against a numeric bound"),
    ],
)
def test_values_with_no_order_against_a_numeric_bound_yield_no_claim(value, why) -> None:
    """Three values, three pre-fix answers, none of them ``None``.

    ``True`` and ``"heavy"`` returned ``False`` (convicted); ``nan`` passed the
    ``isinstance(value, (int, float))`` guard and then returned ``True``
    (acquitted), because the answer was derived from the NEGATION and both
    ``nan < 1`` and ``nan > 100`` are ``False``. Both directions of the same
    missing third answer.
    """
    assert _in_range(value, {"min": 1, "max": 100}, "Integer") is None, why


def test_an_offset_datetime_is_ordered_as_an_instant_not_as_text() -> None:
    """Lexical order agrees with chronology for a ``Date`` and NOT for a
    ``DateTime`` carrying an offset.

    ``10:00+02:00`` is ``08:00Z`` — before the ``09:00Z`` minimum — but sorts
    AFTER it as text. Comparing the strings would have the oracle claim
    satisfied where the constraint is violated, which is the F-1 failure mode
    reached through a different door.
    """
    bounds = {"min": "2021-06-15T09:00:00Z"}
    assert _in_range("2021-06-15T10:00:00+02:00", bounds, "DateTime") is False
    assert _in_range("2021-06-15T10:00:00Z", bounds, "DateTime") is True
    # Naive against aware: Python raises rather than inventing an offset, and so
    # the oracle makes no claim rather than inventing one for it.
    assert _in_range("2021-06-15T10:00:00", bounds, "DateTime") is None


def test_one_undecidable_member_withdraws_the_claim_for_the_whole_constraint(
    tmp_path,
) -> None:
    """A population holding one DECIDED violation and one unorderable value.

    The reference does not settle which wins, and the mechanism does: the
    checker answers ``unchecked`` here by an explicitly deliberate rule
    (undecidable outranks offending, so the constraint as a whole was not
    evaluated). A witness claiming ``violated`` would meet that correct
    abstention as ``witness=violated observed=unchecked`` and quarantine it as a
    ``candidate-false-pass`` — F-2's exact shape, one population over. The
    oracle abstains instead.
    """
    model = load_model(str(UNRESOLVABLE_BOUND))
    doc = {
        "population": {
            "model": UNRESOLVABLE_BOUND.name,
            "source": "synthetic",
            "covers": ["batch_has_mass"],
        },
        "facts": {
            "batch_has_mass": [{"batch": "b1", "mass": 500}, {"batch": "b2", "mass": "heavy"}],
        },
    }
    assert _witness(model.constraints[0], None, doc, model, _direct_subtypes(model)) is None

    pop_path = tmp_path / "mixed.json"
    pop_path.write_text(json.dumps(doc), encoding="utf-8")
    report = check(model, load_population(str(pop_path), model=model))
    observed = next(v.verdict for v in report.verdicts if v.constraint_ref == "constraints[0]")
    assert observed == "unchecked"


def test_the_disjunction_stays_open_when_one_interval_cannot_decide() -> None:
    """A value inside no DECIDED interval, with one interval undecidable.

    That interval might have been the satisfied one, so the disjunction is open
    — the same rule the single-range case applies, at the union.
    """
    ranges = [{"min": 1, "max": 10}, {"min": "a", "max": "z"}]
    from gnd.synth.assemble import _range_union_claim

    assert _range_union_claim(50, ranges, None) is None
    assert _range_union_claim(5, ranges, None) is True
