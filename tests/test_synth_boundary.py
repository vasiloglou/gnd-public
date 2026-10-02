"""The D-06 boundary class: derivation, ε, predicted verdicts, unreachable bounds.

Task 1's standard is TOTALITY, not thoroughness: every constrained parameter the
model declares yields either boundary cases carrying a predicted verdict the real
checker confirmed, or a ``NotDerivable`` record naming the mechanism that makes
the bound unreachable. The two lists together account for every parameter, and
that totality is asserted rather than assumed.

The traps research named get their own tests, because they are where a uniform
"one below the bound" deriver fabricates measurements:

- ``frequency {min: 1}`` — the below-bound group does not OCCUR, and a
  non-occurring group is satisfied. Emitting the case would manufacture a
  violating label the checker correctly passes: a fabricated false pass.
- ``cardinality {min: >= 1}`` over an empty universe — a DECIDED FAILURE, not
  vacuity, and the adversarial corpus already pins it.
- multi-role ``exclusive-or`` — the disjunctive half is undefined at arity > 1,
  so there is no inside case at all.
- ``ring reflexive`` — LOCAL, so a case built over the whole roster manufactures
  a false failure.
- ε at magnitude — a fixed ``1e-9`` rounds back to the bound on a large float and
  produces a boundary whose two sides serialize identically (C11).
"""

from __future__ import annotations

import json
import math
from datetime import date, datetime, timedelta
from pathlib import Path
from random import Random

import pytest

from gnd.checker import IMPLEMENTED_FAMILIES, check
from gnd.model import Model, load_model
from gnd.population import load_population
from gnd.synth import boundary as boundary_module
from gnd.synth.assemble import assemble_conforming
from gnd.synth.boundary import (
    DATE_RESOLUTION,
    DATETIME_RESOLUTION,
    BoundaryCase,
    BoundaryPredictionMismatch,
    NoOrdering,
    NotDerivable,
    boundary_neighbour,
    compare_boundary_observed,
    derive_boundary_cases,
    emit_boundary,
    enumerate_boundary,
    predict_boundary,
)
from gnd.synth.provenance import CASE_KIND_TO_LABEL, ExpectedState

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "tests" / "fixtures"
RING = FIXTURES / "checker" / "ring.orm.yaml"
SETFAM = FIXTURES / "checker" / "setfam.orm.yaml"
FULL_VOCAB = FIXTURES / "models" / "full_vocabulary.orm.yaml"
XOR_MULTIROLE = FIXTURES / "adversarial" / "models" / "xor_multirole.orm.yaml"
REFERENCE_VALUE_TYPE = FIXTURES / "adversarial" / "models" / "reference_value_type.orm.yaml"
FLOAT_RANGE = FIXTURES / "adversarial" / "models" / "float_range.orm.yaml"
PARTITION_EXCLUSIVE = FIXTURES / "adversarial" / "models" / "partition_exclusive.orm.yaml"

ALL_MODELS = [RING, SETFAM, FULL_VOCAB]


def _baseline(model_path: Path, seed: int = 1):
    model = load_model(str(model_path))
    assembly = assemble_conforming(model, seed, model_ref=model_path.name)
    return model, assembly.doc


def _constraint_refs(model):
    from gnd.synth.assemble import _constraint_iter_with_ref

    return [ref for ref, _c, _ft in _constraint_iter_with_ref(model)]


# --------------------------------------------------------------------------- #
# ε — the minimal representable step (C11)
# --------------------------------------------------------------------------- #


def test_integer_neighbour_is_one_step_in_each_direction():
    assert boundary_neighbour(10, "Integer", +1) == (11, "1")
    assert boundary_neighbour(10, "Integer", -1) == (9, "1")
    assert boundary_neighbour(-5, "Integer", -1) == (-6, "1")


@pytest.mark.parametrize(
    "bound",
    [
        0.0,
        1.0,
        -1.0,
        1e-300,  # very small
        -1e-300,
        1e300,  # very large — where a fixed 1e-9 delta is a NO-OP
        -1e300,
        1234567890123456.0,
    ],
)
def test_float_neighbour_uses_nextafter_and_differs_after_serialization(bound):
    """C11: a fixed 1e-9 rounds back to the bound at magnitude.

    ``1e300 + 1e-9 == 1e300`` exactly, so a constant-delta deriver would emit an
    "outside" case byte-identical to its "inside" twin — a silent no-op wearing a
    boundary label. ``math.nextafter`` cannot do that, and the assertion is made
    against the SERIALIZED form because that is what the population file carries.
    """
    up, up_eps = boundary_neighbour(bound, "Float", +1)
    down, down_eps = boundary_neighbour(bound, "Float", -1)
    assert up == math.nextafter(bound, math.inf)
    assert down == math.nextafter(bound, -math.inf)
    assert json.dumps(up) != json.dumps(bound)
    assert json.dumps(down) != json.dumps(bound)
    assert float(up_eps) > 0.0
    assert float(down_eps) > 0.0


def test_a_fixed_1e9_epsilon_would_be_a_no_op_at_magnitude():
    """The measured reason the constant was refused — stated as a test."""
    assert 1e300 + 1e-9 == 1e300
    assert json.dumps(1e300 + 1e-9) == json.dumps(1e300)
    stepped, _eps = boundary_neighbour(1e300, "Float", +1)
    assert json.dumps(stepped) != json.dumps(1e300)


def test_date_and_datetime_resolutions_are_stated_explicitly():
    """DateTime is one MICROSECOND, not one second: ISO-8601 fractional seconds
    are valid, so "one second" would mislabel an inside case as outside."""
    assert DATE_RESOLUTION == timedelta(days=1)
    assert DATETIME_RESOLUTION == timedelta(microseconds=1)

    value, eps = boundary_neighbour("2020-06-15", "Date", +1)
    assert value == "2020-06-16" and eps == "P1D"
    assert date.fromisoformat(value) - date.fromisoformat("2020-06-15") == DATE_RESOLUTION

    value, eps = boundary_neighbour("2020-06-15T12:00:00", "DateTime", +1)
    assert eps == "PT0.000001S"
    delta = datetime.fromisoformat(value) - datetime.fromisoformat("2020-06-15T12:00:00")
    assert delta == DATETIME_RESOLUTION
    assert json.dumps(value) != json.dumps("2020-06-15T12:00:00")


def test_string_and_boolean_have_no_step_only_membership():
    with pytest.raises(NoOrdering, match="MEMBERSHIP"):
        boundary_neighbour("abc", "String", +1)
    with pytest.raises(NoOrdering, match="MEMBERSHIP"):
        boundary_neighbour(True, "Boolean", -1)


def test_a_non_finite_float_bound_has_no_representable_neighbour():
    with pytest.raises(NoOrdering, match="not finite"):
        boundary_neighbour(float("inf"), "Float", +1)


@pytest.mark.parametrize(
    ("bound", "primitive", "direction"),
    [
        ("0001-01-01", "Date", -1),
        ("9999-12-31", "Date", +1),
        ("0001-01-01T00:00:00", "DateTime", -1),
        ("9999-12-31T23:59:59.999999", "DateTime", +1),
        (-float.fromhex("0x1.fffffffffffffp+1023"), "Float", -1),
        (float.fromhex("0x1.fffffffffffffp+1023"), "Float", +1),
        (-float.fromhex("0x1.fffffffffffffp+1023"), "Number", -1),
        (float.fromhex("0x1.fffffffffffffp+1023"), "Number", +1),
    ],
)
def test_extreme_bounds_without_an_outward_value_are_not_derivable(
    bound, primitive, direction
):
    with pytest.raises(NoOrdering, match="no (finite )?representable"):
        boundary_neighbour(bound, primitive, direction)


def test_strict_serialization_failure_becomes_no_ordering(monkeypatch):
    def fail_serialization(_value):
        raise ValueError("strict JSON refused the scalar")

    monkeypatch.setattr(boundary_module, "_serialise", fail_serialization)
    with pytest.raises(NoOrdering, match="strict JSON"):
        boundary_neighbour(1.0, "Float", +1)


def test_inherited_reference_roles_are_governed_for_placement_and_emptying():
    from gnd.synth.assemble import _direct_subtypes
    from gnd.synth.boundary import _reference_targets, _shrink_object_universe
    from gnd.synth.frontier import _empty_object_universe

    model = Model(
        version=1,
        object_types=[
            {
                "id": "movie",
                "kind": "entity",
                "reference": {"mode": "popular", "value_type": "movie_id"},
            },
            {
                "id": "short_film",
                "kind": "entity",
                "subtype_of": ["movie"],
                "inherits_reference": True,
                "derivation": "asserted",
            },
            {"id": "movie_id", "kind": "value", "primitive": "Integer"},
            {"id": "title", "kind": "value", "primitive": "String"},
        ],
        fact_types=[
            {
                "id": "short_has_title",
                "reading": "{short} has {title}",
                "roles": [
                    {"object_type": "short_film", "role_name": "short"},
                    {"object_type": "title", "role_name": "title"},
                ],
            }
        ],
    )
    constraint = {
        "type": "value",
        "object_type": "movie_id",
        "allowed": [500],
    }
    baseline = {
        "facts": {"short_has_title": [{"short": 500, "title": "Gamma"}]},
        "instances": {},
    }
    children = _direct_subtypes(model)

    assert _reference_targets(constraint, model) == [("short_has_title", "short")]

    shrunk = json.loads(json.dumps(baseline))
    _shrink_object_universe(shrunk, model, "movie_id", 0, children)
    assert shrunk["facts"]["short_has_title"] == []

    emptied = json.loads(json.dumps(baseline))
    _empty_object_universe(emptied, model, "movie_id", children)
    assert emptied["facts"]["short_has_title"] == []


def test_a_neighbour_that_serialises_identically_is_refused_loudly(monkeypatch):
    """The assertion the plan requires: inside and outside must DIFFER after
    serialization, and a step that round-trips back is a loud refusal, not a
    quietly emitted no-op."""
    monkeypatch.setattr(boundary_module.math, "nextafter", lambda value, _target: value)
    with pytest.raises(NoOrdering, match="serializes identically"):
        boundary_neighbour(2.5, "Float", +1)


def test_exclusive_bounds_are_exercised_in_both_directions():
    """An exclusive minimum makes the BOUND ITSELF the outside case and ``a + ε``
    the inside one — read the flags, do not assume inclusivity."""
    model = load_model(str(FULL_VOCAB))
    doc = assemble_conforming(model, 1, model_ref=FULL_VOCAB.name).doc
    # constraints[7] is the role-scoped hours range {min: 0, max: 200} with no
    # explicit inclusivity flags (default inclusive).
    inclusive_ref = next(
        ref
        for ref in _constraint_refs(model)
        if _resolve_type(model, ref) == "value" and _has_range(model, ref)
    )
    cases, _downs = derive_boundary_cases(model, inclusive_ref, doc, Random(3))
    by_name = {c.name: c for c in cases}
    bounds = _range_of(model, inclusive_ref)
    assert by_name["range-min-inside"].placed_value == bounds["min"]
    assert by_name["range-max-inside"].placed_value == bounds["max"]
    assert by_name["range-min-outside"].placed_value == bounds["min"] - 1
    assert by_name["range-max-outside"].placed_value == bounds["max"] + 1

    # Now flip the flags: the bound moves to the OUTSIDE side in both directions.
    exclusive = _with_exclusive_bounds(model, inclusive_ref)
    cases, _downs = derive_boundary_cases(exclusive, inclusive_ref, doc, Random(3))
    by_name = {c.name: c for c in cases}
    assert by_name["range-min-outside"].placed_value == bounds["min"]
    assert by_name["range-min-inside"].placed_value == bounds["min"] + 1
    assert by_name["range-max-outside"].placed_value == bounds["max"]
    assert by_name["range-max-inside"].placed_value == bounds["max"] - 1


def _resolve_type(model, ref):
    from gnd.synth.mutate import _resolve

    return str(_resolve(model, ref)[0].get("type"))


def _has_range(model, ref):
    from gnd.synth.mutate import _resolve

    return (_resolve(model, ref)[0].get("range") or {}).get("min") is not None


def _range_of(model, ref):
    from gnd.synth.mutate import _resolve

    return dict(_resolve(model, ref)[0]["range"])


def _with_exclusive_bounds(model, ref):
    import copy

    from gnd.synth.mutate import _resolve

    clone = copy.deepcopy(model)
    constraint, _ft = _resolve(clone, ref)
    constraint["range"]["min_inclusive"] = False
    constraint["range"]["max_inclusive"] = False
    return clone


def test_float_bounds_derive_through_nextafter_on_a_real_model():
    """``float_range.orm.yaml`` declares ``{min: -50, max: 60}`` on a Float value
    type: the derived neighbours must be nextafter steps, not integer ones."""
    model, doc = _baseline(FLOAT_RANGE)
    ref = next(r for r in _constraint_refs(model) if _resolve_type(model, r) == "value")
    cases, downs = derive_boundary_cases(model, ref, doc, Random(5))
    assert not downs
    by_name = {c.name: c for c in cases}
    assert by_name["range-max-outside"].placed_value == math.nextafter(60, math.inf)
    assert by_name["range-min-outside"].placed_value == math.nextafter(-50, -math.inf)
    for case in cases:
        assert case.epsilon is None or float(case.epsilon) > 0


# --------------------------------------------------------------------------- #
# per-family derivation, verified against the REAL checker
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("model_path", ALL_MODELS, ids=lambda p: p.stem)
def test_every_derived_case_predicted_verdict_is_confirmed_by_the_real_checker(
    model_path, tmp_path
):
    """The admission rule: a case is a measurement input only when its DERIVED
    prediction and the checker's observation agree. Every emitted case is
    written, re-loaded, checked, and compared over the FULL expectation map."""
    model, doc = _baseline(model_path)
    cases, _downs = enumerate_boundary(model, doc, Random(7))
    assert cases, f"{model_path.stem} derived no boundary cases at all"
    for index, case in enumerate(cases):
        admitted = emit_boundary(model, case, tmp_path / f"{model_path.stem}.{index}.json")
        assert admitted.predicted_verdict is not None or case.family == "textual"
        assert admitted.observed_verdict == admitted.predicted_verdict


@pytest.mark.parametrize("model_path", ALL_MODELS, ids=lambda p: p.stem)
def test_cases_and_not_derivable_records_account_for_every_constraint(model_path):
    """TOTALITY: no constraint the model declares is silently absent from both
    lists. A gap in the derivation must appear as a mechanism, never as
    nothing."""
    model, doc = _baseline(model_path)
    cases, downs = enumerate_boundary(model, doc, Random(7))
    accounted = {c.constraint_ref for c in cases} | {d.constraint_ref for d in downs}
    declared = set(_constraint_refs(model))
    assert declared - accounted == set()


@pytest.mark.parametrize("model_path", ALL_MODELS, ids=lambda p: p.stem)
def test_every_not_derivable_record_names_a_mechanism(model_path):
    model, doc = _baseline(model_path)
    _cases, downs = enumerate_boundary(model, doc, Random(7))
    for down in downs:
        assert isinstance(down, NotDerivable)
        assert len(down.reason) > 30, down
        assert down.as_record()["mechanism"] == down.reason
        assert down.as_record()["case_kind"] == "boundary"


@pytest.mark.parametrize("model_path", ALL_MODELS, ids=lambda p: p.stem)
def test_every_emitted_population_carries_a_d10_label(model_path, tmp_path):
    """D-15 keeps the population format shut: the header ``label`` stays one of
    D-10's THREE values however many case kinds the sidecar distinguishes."""
    model, doc = _baseline(model_path)
    cases, _downs = enumerate_boundary(model, doc, Random(7))
    observed_labels = set()
    for index, case in enumerate(cases):
        path = tmp_path / f"{model_path.stem}.{index}.json"
        emit_boundary(model, case, path)
        observed_labels.add(json.loads(path.read_text())["population"]["label"])
    assert observed_labels <= {"conforming", "boundary", "violating"}
    assert observed_labels == {"boundary"}


def test_frequency_min_one_lower_side_is_not_derivable_with_the_occurring_groups_mechanism():
    """THE trap. At ``min = 1`` the below-bound group has size 0, which means it
    does not OCCUR — and Halpin's occurring-groups semantics make a non-occurring
    group satisfied. A deriver that emitted it anyway would manufacture a case
    labelled violating that the checker correctly passes."""
    model, doc = _baseline(FULL_VOCAB)
    ref = next(
        r
        for r in _constraint_refs(model)
        if _resolve_type(model, r) == "frequency"
        and (_bound_of(model, r).get("min") == 1)
    )
    _cases, downs = derive_boundary_cases(model, ref, doc, Random(9))
    lower = [d for d in downs if d.side == "min-outside"]
    assert len(lower) == 1
    assert "occurring-groups" in lower[0].reason
    assert "constraint-reference.md:360" in lower[0].reason
    assert "does not OCCUR" in lower[0].reason


def _bound_of(model, ref):
    from gnd.synth.mutate import _resolve

    return dict(_resolve(model, ref)[0].get("bound") or {})


def test_cardinality_min_over_an_empty_universe_predicts_fail_not_vacuity(tmp_path):
    """``m − 1 = 0`` with ``m >= 1`` is a DECIDED FAILURE. The corpus case
    ``an-unmet-lower-bound-over-nothing-is-still-a-failure`` pins the same rule
    from the other side."""
    model, doc = _baseline(FULL_VOCAB)
    ref = next(
        r
        for r in _constraint_refs(model)
        if _resolve_type(model, r) == "cardinality" and _bound_of(model, r).get("min")
    )
    cases, _downs = derive_boundary_cases(model, ref, doc, Random(11))
    below = next(c for c in cases if c.name == "universe-below-min")
    admitted = emit_boundary(model, below, tmp_path / "below-min.json")
    assert admitted.predicted_verdict == "fail"
    assert admitted.observed_verdict == "fail"
    assert admitted.predicted[ref].ground_truth == "violated"
    assert "DECIDED FAILURE" in below.description


def test_cardinality_min_zero_has_no_fabricated_negative_outside_case():
    from gnd.synth.mutate import _existing_members

    model = Model(
        version=1,
        object_types=[{"id": "item", "kind": "value", "primitive": "String"}],
        fact_types=[],
        constraints=[
            {
                "type": "cardinality",
                "scope": "object",
                "object_type": "item",
                "bound": {"min": 0},
                "modality": "alethic",
            }
        ],
    )
    doc = {
        "population": {"model": "m.orm.yaml", "source": "synthetic"},
        "instances": {"item": ["a", "b", "c"]},
        "facts": {},
    }

    cases, downs = derive_boundary_cases(model, "constraints[0]", doc, Random(11))

    assert [case.name for case in cases] == ["universe-at-min"]
    at_min = cases[0]
    assert at_min.side == "inside"
    assert at_min.placed_value == 0
    assert len(_existing_members(at_min.doc, model, "item")) == 0
    lower = [down for down in downs if down.side == "min-outside"]
    assert len(lower) == 1
    assert "cannot be negative" in lower[0].reason


def test_the_corpus_case_that_pins_the_same_rule_still_passes():
    """The adversarial corpus's own statement of the rule, re-asserted here so a
    change to the deriver that contradicted it would fail twice."""
    import subprocess
    import sys

    adversarial = FIXTURES / "adversarial"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "gnd",
            "check",
            str(adversarial / "models" / "no_subjects_cardinality_min.orm.yaml"),
            str(adversarial / "populations" / "no_subjects_cardinality_min.yaml"),
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        check=False,
    )
    assert result.returncode == 1, result.stdout + result.stderr


def test_multirole_exclusive_or_has_no_inside_case_and_is_unchecked_outside(tmp_path):
    """The disjunctive half is UNDEFINED at arity > 1
    (``constraint-reference.md:319-331``), so a clean exclusion half is
    ``unchecked`` at band 4 and there is no inside case to derive."""
    model, doc = _baseline(XOR_MULTIROLE)
    ref = next(r for r in _constraint_refs(model) if _resolve_type(model, r) == "exclusive-or")
    cases, downs = derive_boundary_cases(model, ref, doc, Random(13))
    inside = [d for d in downs if d.side == "inside"]
    assert len(inside) == 1
    assert "undefined at arity > 1" in inside[0].reason
    assert not [c for c in cases if c.side == "inside"]

    outside = next(c for c in cases if c.side == "outside")
    admitted = emit_boundary(model, outside, tmp_path / "xor-multirole.json")
    # A tuple in two sequences PROVES the constraint broken however the
    # undecidable half would have gone (D-08 precedence 1 > 4), so the outside
    # case is a violation, not band 4.
    assert admitted.predicted_verdict == "fail"
    assert admitted.observed_verdict == "fail"
    assert admitted.predicted[ref].ground_truth == "violated"

    # And the CLEAN exclusion half is the band-4 route the undecided rate lives
    # on: same model, no overlap, `xor-disjunctive-undefined`.
    clean = BoundaryCase(ref, "exclusive-or", "clean", "frontier", doc, "no overlap")
    clean_admitted = emit_boundary(model, clean, tmp_path / "xor-clean.json")
    assert clean_admitted.predicted_verdict in ("unchecked", "vacuous")


def test_a_reflexive_ring_boundary_is_built_over_PARTICIPANTS_not_the_roster(tmp_path):
    """Reflexivity is LOCAL (Halpin, ``constraint-reference.md:404-426``):
    non-participants are not constrained, so a case built over the whole roster
    manufactures a false failure. The deriver produces the local one — proven by
    checking that its removal target still participates through another edge."""
    from gnd.synth.mutate import _resolve, _ring_edges

    model, doc = _baseline(RING)
    ref = next(
        r
        for r in _constraint_refs(model)
        if _resolve_type(model, r) == "ring"
        and str(_resolve(model, r)[0].get("variant")) == "reflexive"
    )
    cases, _downs = derive_boundary_cases(model, ref, doc, Random(17))
    outside = next(c for c in cases if c.side == "outside")
    _constraint, ft = _resolve(model, ref)
    _from_role, _to_role, before = _ring_edges(doc, model, ft)
    _f, _t, after = _ring_edges(outside.doc, model, ft)
    removed = [edge for edge in before if edge not in after]
    assert len(removed) == 1
    node = removed[0][0]
    assert removed[0][0] == removed[0][1], "the removed edge must be a SELF-edge"
    # The node must STILL participate — otherwise it is no longer a participant
    # and local reflexivity would not constrain it, self-cancelling the case.
    assert any(node in edge for edge in after), (
        "the boundary case removed the node from the ring entirely; local "
        "reflexivity does not constrain a non-participant, so the case would "
        "self-cancel"
    )
    admitted = emit_boundary(model, outside, tmp_path / "reflexive.json")
    assert admitted.predicted_verdict in ("fail", "warning")
    assert admitted.observed_verdict == admitted.predicted_verdict


def test_acyclic_boundary_closes_a_cycle_of_length_three_to_isolate(tmp_path):
    """``k + 1 >= 3`` deliberately: a 2-cycle or a self-loop would also cross
    ``asymmetric`` / ``irreflexive`` and lose the isolation the table asks for."""
    from gnd.synth.mutate import _resolve

    model, doc = _baseline(RING)
    ref = next(
        r
        for r in _constraint_refs(model)
        if _resolve_type(model, r) == "ring"
        and str(_resolve(model, r)[0].get("variant")) == "acyclic"
    )
    cases, _downs = derive_boundary_cases(model, ref, doc, Random(19))
    outside = next(c for c in cases if "cycle-of-3" in c.name)
    admitted = emit_boundary(model, outside, tmp_path / "acyclic.json")
    # On ring.orm.yaml each variant owns its own fact type, so the 3-cycle
    # isolates: exactly one constraint changes state.
    changed = {
        ref_
        for ref_, state in admitted.predicted.items()
        if state.expected_verdict in ("fail", "warning")
    }
    assert changed == {ref}


def test_a_value_bound_is_also_placed_as_an_ENTITY_reference_value(tmp_path):
    """F-01: the universe of a reference value type includes the entity values
    that denote instances of the types it identifies. A boundary set that only
    populated roles typed to the value type would miss the path F-01 closed —
    and on this model there IS no such role."""
    model, doc = _baseline(REFERENCE_VALUE_TYPE)
    refs = [r for r in _constraint_refs(model) if _resolve_type(model, r) == "value"]
    assert refs
    admitted_any = False
    for ref in refs:
        cases, downs = derive_boundary_cases(model, ref, doc, Random(23))
        assert not downs, downs
        assert cases
        for index, case in enumerate(cases):
            admitted = emit_boundary(model, case, tmp_path / f"ref.{ref}.{index}.json")
            assert admitted.observed_verdict == admitted.predicted_verdict
            admitted_any = True
    assert admitted_any


def test_a_subtype_partition_with_derivation_only_membership_stands_down():
    """Derivation-rule-only membership is observable to no population, so the
    violating and boundary cells are not measurable — recorded with the
    mechanism rather than counted covered."""
    model, doc = _baseline(FULL_VOCAB)
    ref = next(
        r for r in _constraint_refs(model) if _resolve_type(model, r) == "subtype-partition"
    )
    cases, downs = derive_boundary_cases(model, ref, doc, Random(29))
    assert {d.side for d in downs} == {"inside", "outside"}
    assert all("DERIVATION-ONLY" in d.reason for d in downs)
    assert [c.side for c in cases] == ["frontier"]


def test_an_observable_subtype_partition_does_derive(tmp_path):
    """Resolution (a): ``partition_exclusive.orm.yaml`` carries ASSERTED subtypes
    observable through subtype-typed roles, so the family is actually measured
    rather than credited."""
    model, doc = _baseline(PARTITION_EXCLUSIVE)
    ref = next(
        r for r in _constraint_refs(model) if _resolve_type(model, r) == "subtype-partition"
    )
    cases, downs = derive_boundary_cases(model, ref, doc, Random(31))
    assert not downs
    assert {c.side for c in cases} == {"inside", "outside"}
    for index, case in enumerate(cases):
        admitted = emit_boundary(model, case, tmp_path / f"partition.{index}.json")
        assert admitted.observed_verdict == admitted.predicted_verdict
    outside = next(c for c in cases if c.side == "outside")
    admitted = emit_boundary(model, outside, tmp_path / "partition-outside.json")
    assert admitted.predicted_verdict == "fail"


def test_a_derived_subtype_with_observed_membership_is_not_labelled_unchecked():
    model = Model(
        version=1,
        object_types=[
            {"id": "super", "kind": "value", "primitive": "String"},
            {
                "id": "left",
                "kind": "value",
                "primitive": "String",
                "subtype_of": ["super"],
                "derivation": "derived",
            },
            {
                "id": "right",
                "kind": "value",
                "primitive": "String",
                "subtype_of": ["super"],
                "derivation": "derived",
            },
        ],
        fact_types=[
            {
                "id": "left_seen",
                "reading": "{left} was seen",
                "roles": [{"object_type": "left", "role_name": "left"}],
            },
            {
                "id": "right_seen",
                "reading": "{right} was seen",
                "roles": [{"object_type": "right", "role_name": "right"}],
            },
        ],
        constraints=[
            {
                "type": "subtype-partition",
                "supertype": "super",
                "subtypes": ["left", "right"],
                "exclusive": True,
                "exhaustive": True,
                "modality": "alethic",
            }
        ],
    )
    doc = {
        "population": {
            "model": "m.orm.yaml",
            "source": "synthetic",
            "covers": ["left_seen", "right_seen"],
        },
        "facts": {
            "left_seen": [{"left": "L"}],
            "right_seen": [{"right": "R"}],
        },
    }

    cases, _downs = derive_boundary_cases(model, "constraints[0]", doc, Random(31))
    assert cases
    assert all(case.case_kind != "unchecked" for case in cases)


def test_textual_emits_exactly_one_case_per_model_predicting_unchecked(tmp_path):
    model, doc = _baseline(FULL_VOCAB)
    cases, _downs = enumerate_boundary(model, doc, Random(37))
    textual = [c for c in cases if c.family == "textual"]
    assert len(textual) == 1
    admitted = emit_boundary(model, textual[0], tmp_path / "textual.json")
    assert admitted.predicted_verdict == "unchecked"
    verdict = next(
        v for v in admitted.report.verdicts if v.constraint_ref == textual[0].constraint_ref
    )
    assert verdict.reason_code == "textual-not-mechanical"


def test_an_external_uniqueness_boundary_asserts_the_join_yields_rows():
    """Otherwise it is a vacuity case wearing a boundary label (F-05) — the
    boundary-class analogue of plan 03's positive non-degeneracy gate."""
    from gnd.synth.assemble import _seq_tuples
    from gnd.synth.mutate import _resolve

    model, doc = _baseline(FULL_VOCAB)
    ref = next(
        r
        for r in _constraint_refs(model)
        if _resolve_type(model, r) == "uniqueness"
        and _resolve(model, r)[0].get("scope") == "external"
    )
    cases, _downs = derive_boundary_cases(model, ref, doc, Random(41))
    inside = next(c for c in cases if c.side == "inside")
    seq = list(_resolve(model, ref)[0].get("role_refs") or [])
    assert len(_seq_tuples(inside.doc, model, seq)) >= 1
    assert "non-degenerate" in inside.description

    # Emptying the join makes the case NOT derivable rather than a boundary case
    # carrying a vacuous verdict.
    emptied = json.loads(json.dumps(doc))
    for role_ref in seq:
        emptied.setdefault("facts", {})[str(role_ref["fact_type"])] = []
    _cases2, downs2 = derive_boundary_cases(model, ref, emptied, Random(41))
    assert any("ZERO rows" in d.reason for d in downs2)


def test_join_scoped_set_family_boundaries_refuse_an_empty_side():
    """Kimi: a perturbation that empties a join is ``NotDerivable``, never a
    boundary case wearing a vacuity verdict."""
    model, doc = _baseline(SETFAM)
    for family in ("subset", "equality", "exclusion"):
        refs = [r for r in _constraint_refs(model) if _resolve_type(model, r) == family]
        if not refs:
            continue
        ref = refs[0]
        emptied = json.loads(json.dumps(doc))
        emptied["facts"] = {}
        _cases, downs = derive_boundary_cases(model, ref, emptied, Random(43))
        assert any(d.side == "inside" for d in downs), family


def test_equality_derives_BOTH_removal_directions():
    """Two directions, two cases — the D-06 table is explicit that one is not
    enough."""
    model, doc = _baseline(SETFAM)
    ref = next(r for r in _constraint_refs(model) if _resolve_type(model, r) == "equality")
    cases, downs = derive_boundary_cases(model, ref, doc, Random(47))
    names = {c.name for c in cases}
    reasons = {d.side for d in downs}
    for label in ("a", "b"):
        assert (
            f"one-tuple-removed-from-side-{label}" in names
            or f"outside-side-{label}" in reasons
        ), f"side {label} is neither derived nor recorded"
    assert "one-tuple-removed-from-side-a" in names or "one-tuple-removed-from-side-b" in names


# --------------------------------------------------------------------------- #
# admission, quarantine, and the C1 discipline
# --------------------------------------------------------------------------- #


def test_a_deliberately_wrong_prediction_raises_a_typed_mismatch(tmp_path, monkeypatch):
    """C1: the derivation is authoritative and the checker observational, so a
    disagreement is a typed discrepancy the caller quarantines — never a
    relabelling of the prediction to match observation."""
    model, doc = _baseline(FULL_VOCAB)
    cases, _downs = enumerate_boundary(model, doc, Random(53))
    case = next(c for c in cases if c.side == "inside")

    real_predict = boundary_module.predict_boundary

    def lying_predict(model_, doc_):
        predicted = real_predict(model_, doc_)
        predicted[case.constraint_ref] = ExpectedState(
            ground_truth="violated", expected_verdict="fail", reason="deliberate lie"
        )
        return predicted

    monkeypatch.setattr(boundary_module, "predict_boundary", lying_predict)
    with pytest.raises(BoundaryPredictionMismatch) as raised:
        emit_boundary(model, case, tmp_path / "lie.json")
    discrepancy = next(
        d
        for d in raised.value.discrepancies
        if d["constraint_ref"] == case.constraint_ref
    )
    assert discrepancy["kind"] == "prediction-observation-mismatch"
    assert discrepancy["predicted"]["expected_verdict"] == "fail"
    assert discrepancy["observed_verdict"] == "pass"
    # The PREDICTION is retained, never rewritten to the observation.
    assert raised.value.predicted[case.constraint_ref].expected_verdict == "fail"


def test_compare_reports_every_disagreement_over_the_full_map():
    model, doc = _baseline(FULL_VOCAB)
    predicted = predict_boundary(model, doc)
    path = Path(__file__).parent / "_tmp_full_map.json"
    try:
        path.write_text(json.dumps(doc), encoding="utf-8")
        report = check(model, load_population(str(path), model=model))
    finally:
        path.unlink(missing_ok=True)
    assert compare_boundary_observed(predicted, report) == []
    flipped = dict(predicted)
    a_ref = min(predicted)
    flipped[a_ref] = ExpectedState(
        ground_truth="violated", expected_verdict="fail", reason=None
    )
    assert [d["constraint_ref"] for d in compare_boundary_observed(flipped, report)] == [a_ref]


def test_a_structurally_invalid_boundary_population_is_a_generator_error(tmp_path):
    """Exit 5 stays reserved for a structural GeneratorError: a population that
    fails re-admission contributes zero verdicts and therefore zero errors."""
    from gnd.synth.assemble import GeneratorError

    model, doc = _baseline(FULL_VOCAB)
    broken = json.loads(json.dumps(doc))
    broken["facts"]["employee_has_name"].append({"employee": "not-an-integer-id"})
    case = BoundaryCase(
        "constraints[0]", "uniqueness", "broken", "inside", broken, "deliberately invalid"
    )
    with pytest.raises(GeneratorError, match="re-admission"):
        emit_boundary(model, case, tmp_path / "broken.json")


# --------------------------------------------------------------------------- #
# the case-kind -> label mapping and the CLI
# --------------------------------------------------------------------------- #


def test_case_kind_to_label_maps_five_kinds_onto_three_frozen_labels():
    assert set(CASE_KIND_TO_LABEL) == {
        "conforming",
        "boundary",
        "violating",
        "no-subjects",
        "unchecked",
    }
    assert set(CASE_KIND_TO_LABEL.values()) == {"conforming", "boundary", "violating"}
    assert CASE_KIND_TO_LABEL["no-subjects"] == "boundary"
    assert CASE_KIND_TO_LABEL["unchecked"] == "boundary"


def test_cli_class_boundary_emits_cases_sidecars_and_an_index(tmp_path):
    import subprocess
    import sys

    out = tmp_path / "corpus"
    result = subprocess.run(
        [
            sys.executable, "-m", "gnd", "synth", str(FULL_VOCAB),
            "--out", str(out), "--class", "boundary", "--seed", "1", "--format", "json",
        ],
        capture_output=True, text=True, cwd=str(REPO_ROOT), check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["exit_code"] == 0
    assert len(payload["populations"]) >= 40
    assert payload["not_derivable"], "the unreachable bounds must be REPORTED"
    assert (out / "index.json").exists()

    from gnd.synth.provenance import read_sidecar

    sided = 0
    for entry in payload["populations"]:
        sidecar = read_sidecar(entry["sidecar"])
        assert sidecar.class_ == "boundary"
        # THREE case kinds share the `boundary` LABEL: the bound frontier itself
        # plus the two frontiers D-10's three values cannot name.
        assert sidecar.case_kind in ("boundary", "no-subjects", "unchecked")
        assert CASE_KIND_TO_LABEL[sidecar.case_kind] == sidecar.class_
        assert sidecar.target == entry["target"]
        assert sidecar.predicted_verdict == entry["predicted_verdict"]
        assert sidecar.boundary_side in ("inside", "outside", "frontier")
        assert sidecar.expectations
        if sidecar.epsilon is not None:
            sided += 1
        if sidecar.not_derivable:
            assert all("mechanism" in record for record in sidecar.not_derivable)
    assert sided > 0, "at least one case must record its DERIVED neighbour"


def test_schema_sync_untouched_by_the_boundary_class():
    """D-15: the boundary class adds five case kinds and touches no schema."""
    schema = REPO_ROOT / "src" / "gnd" / "schema" / "population.schema.json"
    text = schema.read_text(encoding="utf-8")
    assert '"conforming"' in text and '"boundary"' in text and '"violating"' in text
    assert "case_kind" not in text
    assert "no-subjects" not in text


@pytest.mark.parametrize("model_path", ALL_MODELS, ids=lambda p: p.stem)
def test_every_implemented_family_the_model_declares_is_accounted_for(model_path):
    """A4: derived from ``checker.IMPLEMENTED_FAMILIES``, never a hand list."""
    from gnd.synth.mutate import _resolve

    model, doc = _baseline(model_path)
    cases, downs = enumerate_boundary(model, doc, Random(59))
    declared = {
        str(_resolve(model, ref)[0].get("type"))
        for ref in _constraint_refs(model)
    }
    covered = {c.family for c in cases} | {d.family for d in downs}
    for family in declared & set(IMPLEMENTED_FAMILIES):
        assert family in covered, family
