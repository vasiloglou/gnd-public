"""The mutation layer: model-derived predictions, verified per case (D-05').

Task 1's standard: the prediction is computed per (model, constraint, operator)
TRIPLE — the same operator predicts different sets on different models — and the
two ways a mutation can lie (violating more than predicted; violating nothing)
are both mechanically caught. The two silent no-ops research measured are shipped
here as REJECTION tests, test-local and deliberately NOT in ``OPERATORS``: they
are not operators, they are the mechanical proof the empty-observed-set branch
fires.
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from random import Random

import pytest

from gnd.checker import IMPLEMENTED_FAMILIES, CheckReport, ConstraintVerdict, check
from gnd.model import load_model
from gnd.population import load_population
from gnd.synth.assemble import assemble_conforming
from gnd.synth.mutate import (
    OPERATORS,
    ExpectedState,
    Mutation,
    PredictionMismatch,
    compare_observed,
    emit_violating,
    enumerate_violating,
    family_coverage,
    operators_for,
    predict_violations,
)
from gnd.synth.oracle import mutations as mutate

REPO_ROOT = Path(__file__).resolve().parent.parent
RING = REPO_ROOT / "tests" / "fixtures" / "checker" / "ring.orm.yaml"
SETFAM = REPO_ROOT / "tests" / "fixtures" / "checker" / "setfam.orm.yaml"
FULL_VOCAB = REPO_ROOT / "tests" / "fixtures" / "models" / "full_vocabulary.orm.yaml"

ALL_MODELS = [RING, SETFAM, FULL_VOCAB]


def _baseline(model_path: Path, tmp_path: Path, seed: int = 1):
    model = load_model(str(model_path))
    assembly = assemble_conforming(model, seed, model_ref=model_path.name)
    baseline_file = tmp_path / f"baseline.{model_path.stem}.json"
    baseline_file.write_text(json.dumps(assembly.doc), encoding="utf-8")
    population = load_population(str(baseline_file), model=model)
    return model, assembly, check(model, population)


# --------------------------------------------------------------------------- #
# the registry, as shipped
# --------------------------------------------------------------------------- #

#: The plan's operator table, verbatim — the SUMMARY diffs the shipped registry
#: against RESEARCH's measured names through this literal.
_EXPECTED_OPERATORS = {
    "duplicate-covered-role-value",
    "exact-duplicate-row",
    "duplicate-joined-tuple",
    "roster-add-instance",
    "new-entity-plays-role",
    "remove-all-disjunctive-role-plays",
    "drop-fact-from-group",
    "add-facts-past-ceiling",
    "remove-fact-from-last-covering-group",
    "drop-joined-group-below-min",
    "close-3-cycle",
    "close-2-cycle",
    "add-self-loop",
    "edit-value-out-of-range",
    "add-fact-with-out-of-range-new-entity",
    "introduce-distinct-instance",
    "add-player-missing-subset-role",
    "remove-tuple-from-equality-side",
    "add-overlapping-tuple",
    "play-both-exclusive-or-roles",
    "play-neither-exclusive-or-role",
    "invert-value-comparison-operands",
    "place-instance-in-two-subtypes",
    "remove-instance-from-all-subtypes",
    "drop-fact-type-from-covers",
    "empty-fact-type",
}


def test_the_registry_ships_the_26_measured_operator_names_and_no_rejects() -> None:
    shipped = {t.name for templates in OPERATORS.values() for t in templates}
    assert shipped == _EXPECTED_OPERATORS
    # The two measured silent no-ops are REJECTED — test-local demonstrations
    # below, never registry entries (Qwen-LOW).
    assert "empty-unconstrained-fact-type" not in shipped
    assert "off-by-one-inside-max-bound" not in shipped


# --------------------------------------------------------------------------- #
# family coverage — derived from the checker's own constant (A4)
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("model_path", ALL_MODELS, ids=lambda p: p.stem)
def test_every_declared_implemented_family_has_an_operator_or_a_named_mechanism(
    model_path, tmp_path
) -> None:
    """Iterates ``checker.IMPLEMENTED_FAMILIES`` — never a hand-typed family
    list, which is how a family becomes silently unmeasured (A4). For every
    family this model declares: >=1 applicable operator, or a not-derivable
    record naming the mechanism."""
    model, assembly, _report = _baseline(model_path, tmp_path)
    coverage = family_coverage(model, assembly.doc)
    declared_families = {
        str(constraint.get("type"))
        for _ref, constraint, _ft in mutate._constraint_iter_with_ref(model)
    }
    for family in IMPLEMENTED_FAMILIES:
        if family not in declared_families:
            continue
        entry = coverage[family]
        assert entry["operators"] or entry["not_derivable"], (
            f"family {family!r} on {model_path.name} has neither an applicable "
            f"operator nor a recorded non-derivability"
        )
        for record in entry["not_derivable"]:
            assert record["mechanism"], f"stand-down without a mechanism: {record}"


def test_full_vocabulary_has_an_applicable_operator_for_every_declared_family(
    tmp_path,
) -> None:
    """On the all-families model, coverage is not merely 'recorded absent': every
    implemented family full_vocabulary declares has at least one APPLICABLE
    operator (the stand-downs are per-constraint, per-shape)."""
    model, assembly, _report = _baseline(FULL_VOCAB, tmp_path)
    coverage = family_coverage(model, assembly.doc)
    for family, entry in coverage.items():
        assert entry["operators"], f"family {family!r} has no applicable operator on full_vocabulary"


# --------------------------------------------------------------------------- #
# the ring implication lattice — computed from co-declared variants
# --------------------------------------------------------------------------- #

_LATTICE_MODEL = textwrap.dedent(
    """\
    version: 1
    source: {kind: text-conversation, confidence: standard, mode: guided}
    object_types:
      - id: node
        name: Node
        kind: entity
        reference: {mode: popular, value_type: node_id}
      - id: node_id
        name: NodeId
        kind: value
        primitive: Integer
    fact_types:
      - id: rel_solo
        reading: "{Node:a} solo {Node:b}"
        roles:
          - {object_type: node, role_name: a}
          - {object_type: node, role_name: b}
        constraints:
          - type: ring
            variant: acyclic
            source: explicit
            status: confirmed
            modality: alethic
            provenance: {user_quote: "acyclic alone."}
      - id: rel_lattice
        reading: "{Node:a} lattice {Node:b}"
        roles:
          - {object_type: node, role_name: a}
          - {object_type: node, role_name: b}
        constraints:
          - type: ring
            variant: acyclic
            source: explicit
            status: confirmed
            modality: alethic
            provenance: {user_quote: "acyclic beside its lattice siblings."}
          - type: ring
            variant: asymmetric
            source: explicit
            status: confirmed
            modality: alethic
            provenance: {user_quote: "asymmetric co-declared."}
          - type: ring
            variant: irreflexive
            source: explicit
            status: confirmed
            modality: alethic
            provenance: {user_quote: "irreflexive co-declared."}
    """
)


def test_the_ring_lattice_is_computed_from_co_declared_variants(tmp_path) -> None:
    """The SAME operator (add-self-loop) predicts ONE ref where `acyclic` stands
    alone and THREE where `asymmetric` and `irreflexive` sit beside it — the
    lattice is a property of the fact type's co-declared variants, never a
    static per-operator constant."""
    model_file = tmp_path / "lattice.orm.yaml"
    model_file.write_text(_LATTICE_MODEL, encoding="utf-8")
    model, assembly, _report = _baseline(model_file, tmp_path)

    solo_ref = "fact_types[rel_solo].constraints[0]"
    solo_ops, _ = operators_for(model, solo_ref, assembly.doc)
    solo_loop = next(m for m in solo_ops if m.name == "add-self-loop")
    solo_doc = solo_loop.apply(json.loads(json.dumps(assembly.doc)), model, solo_ref, Random(1))
    solo_predicted = predict_violations(model, assembly.doc, solo_doc)
    assert set(solo_predicted) == {solo_ref}

    lattice_ref = "fact_types[rel_lattice].constraints[0]"
    lattice_ops, _ = operators_for(model, lattice_ref, assembly.doc)
    lattice_loop = next(m for m in lattice_ops if m.name == "add-self-loop")
    lattice_doc = lattice_loop.apply(
        json.loads(json.dumps(assembly.doc)), model, lattice_ref, Random(1)
    )
    lattice_predicted = predict_violations(model, assembly.doc, lattice_doc)
    assert set(lattice_predicted) == {
        "fact_types[rel_lattice].constraints[0]",
        "fact_types[rel_lattice].constraints[1]",
        "fact_types[rel_lattice].constraints[2]",
    }
    for state in lattice_predicted.values():
        assert state.ground_truth == "violated"
        assert state.expected_verdict == "fail"


def test_a_3_cycle_isolates_acyclic_where_a_self_loop_cannot(tmp_path) -> None:
    """The lattice's useful direction: `acyclic` CAN be isolated (cycle length
    >= 3) on the very fact type where a self-loop entails all three."""
    model_file = tmp_path / "lattice.orm.yaml"
    model_file.write_text(_LATTICE_MODEL, encoding="utf-8")
    model, assembly, _report = _baseline(model_file, tmp_path)
    lattice_ref = "fact_types[rel_lattice].constraints[0]"
    ops, _ = operators_for(model, lattice_ref, assembly.doc)
    cycle = next(m for m in ops if m.name == "close-3-cycle")
    doc = cycle.apply(json.loads(json.dumps(assembly.doc)), model, lattice_ref, Random(1))
    predicted = predict_violations(model, assembly.doc, doc)
    assert set(predicted) == {lattice_ref}


# --------------------------------------------------------------------------- #
# new-instance exposure — computed from the model's object-type-scoped constraints
# --------------------------------------------------------------------------- #

_BARE_EXPOSURE_MODEL = textwrap.dedent(
    """\
    version: 1
    source: {kind: text-conversation, confidence: standard, mode: guided}
    object_types:
      - id: person
        name: Person
        kind: entity
        reference: {mode: popular, value_type: person_id}
      - id: person_id
        name: PersonId
        kind: value
        primitive: Integer
      - id: person_name
        name: PersonName
        kind: value
        primitive: String
    fact_types:
      - id: person_has_name
        reading: "{Person} has {PersonName}"
        roles:
          - {object_type: person, role_name: person}
          - {object_type: person_name, role_name: name}
        constraints:
          - type: uniqueness
            roles: [person]
            source: explicit
            status: confirmed
            modality: alethic
            provenance: {user_quote: "One name per person."}
          - type: mandatory
            role: person
            source: explicit
            status: confirmed
            modality: alethic
            provenance: {user_quote: "Every person has a name."}
    """
)

_CARDINALITY_ADDENDUM = textwrap.dedent(
    """\
    constraints:
      - type: cardinality
        scope: object
        object_type: person
        bound: {max: 1}
        source: user-supplied
        status: confirmed
        modality: alethic
        provenance: {user_note: "Exactly one person exists."}
    """
)


def test_new_instance_exposure_grows_with_the_models_object_scoped_constraints(
    tmp_path,
) -> None:
    """The SAME roster-add predicts ONE ref on a bare model and MORE THAN ONE
    once a `cardinality` is declared on the same object type — isolation is a
    property of the (model, constraint, operator) triple (D-05')."""
    mandatory_ref = "fact_types[person_has_name].constraints[1]"

    bare_file = tmp_path / "bare.orm.yaml"
    bare_file.write_text(_BARE_EXPOSURE_MODEL, encoding="utf-8")
    bare_model, bare_assembly, _ = _baseline(bare_file, tmp_path)
    ops, _ = operators_for(bare_model, mandatory_ref, bare_assembly.doc)
    roster_add = next(m for m in ops if m.name == "roster-add-instance")
    bare_doc = roster_add.apply(
        json.loads(json.dumps(bare_assembly.doc)), bare_model, mandatory_ref, Random(1)
    )
    bare_predicted = predict_violations(bare_model, bare_assembly.doc, bare_doc)
    assert set(bare_predicted) == {mandatory_ref}

    exposed_file = tmp_path / "exposed.orm.yaml"
    exposed_file.write_text(_BARE_EXPOSURE_MODEL + _CARDINALITY_ADDENDUM, encoding="utf-8")
    exposed_model, exposed_assembly, _ = _baseline(exposed_file, tmp_path)
    ops, _ = operators_for(exposed_model, mandatory_ref, exposed_assembly.doc)
    roster_add = next(m for m in ops if m.name == "roster-add-instance")
    exposed_doc = roster_add.apply(
        json.loads(json.dumps(exposed_assembly.doc)), exposed_model, mandatory_ref, Random(1)
    )
    exposed_predicted = predict_violations(exposed_model, exposed_assembly.doc, exposed_doc)
    assert mandatory_ref in exposed_predicted
    assert "constraints[0]" in exposed_predicted  # the cardinality, exposed
    assert len(exposed_predicted) > 1


# --------------------------------------------------------------------------- #
# the typed prediction (C3) — vacuous is not "violated"
# --------------------------------------------------------------------------- #


def test_predict_is_a_typed_map_where_deletion_and_duplication_differ(tmp_path) -> None:
    """`predict` returns dict[str, ExpectedState]. A deletion operator's entries
    carry {no-subjects, vacuous} while a duplicate's carry {violated, fail} —
    the distinction a flat frozenset[str] could not express (C3)."""
    model, assembly, _report = _baseline(SETFAM, tmp_path)
    uniq_ref = "fact_types[booking_by_person].constraints[0]"
    ops, _ = operators_for(model, uniq_ref, assembly.doc)

    duplicate = next(m for m in ops if m.name == "duplicate-covered-role-value")
    dup_doc = duplicate.apply(json.loads(json.dumps(assembly.doc)), model, uniq_ref, Random(1))
    dup_predicted = duplicate.predict(model, assembly.doc, dup_doc)
    assert isinstance(dup_predicted, dict)
    assert all(isinstance(state, ExpectedState) for state in dup_predicted.values())
    assert dup_predicted[uniq_ref].ground_truth == "violated"
    assert dup_predicted[uniq_ref].expected_verdict == "fail"

    deletion = next(m for m in ops if m.name == "empty-fact-type")
    del_doc = deletion.apply(json.loads(json.dumps(assembly.doc)), model, uniq_ref, Random(1))
    del_predicted = deletion.predict(model, assembly.doc, del_doc)
    assert del_predicted[uniq_ref].ground_truth == "no-subjects"
    assert del_predicted[uniq_ref].expected_verdict == "vacuous"


def test_a_family_emptied_mandatory_is_the_masked_cell_not_a_no_subject(tmp_path) -> None:
    """Emptying `booking_by_person` leaves bookings observable through
    `booking_of_room`, so the mandatory's ground truth is VIOLATED while the
    correct checker still answers vacuous — {violated, vacuous}, plan 04's
    masked_by_vacuity cell, never {no-subjects} and never 'correct'."""
    model, assembly, _report = _baseline(SETFAM, tmp_path)
    uniq_ref = "fact_types[booking_by_person].constraints[0]"
    mandatory_ref = "fact_types[booking_by_person].constraints[1]"
    ops, _ = operators_for(model, uniq_ref, assembly.doc)
    deletion = next(m for m in ops if m.name == "empty-fact-type")
    doc = deletion.apply(json.loads(json.dumps(assembly.doc)), model, uniq_ref, Random(1))
    predicted = deletion.predict(model, assembly.doc, doc)
    assert predicted[mandatory_ref].ground_truth == "violated"
    assert predicted[mandatory_ref].expected_verdict == "vacuous"
    assert predicted[mandatory_ref].reason == "masked-by-fact-type-vacuity"


# --------------------------------------------------------------------------- #
# the two measured silent no-ops — REJECTION tests, test-local (Qwen-LOW)
# --------------------------------------------------------------------------- #


def _rejected_empty_unconstrained_fact_type(doc, model, ref, rng):
    """Research's measured no-op #1: emptying a fact type no delta-visible
    constraint ranges over changes zero verdicts."""
    doc["facts"].pop("assignment_has_overtime_hours", None)
    return doc


def _rejected_off_by_one_inside_max_bound(doc, model, ref, rng):
    """Research's measured no-op #2: one more fact still INSIDE a `max` bound
    violates nothing."""
    rows = doc["facts"]["person_takes_course"]
    rows.append(dict(rows[0]))
    return doc


def test_emptying_role_scoped_value_subjects_predicts_vacuity(
    tmp_path,
) -> None:
    model, assembly, report = _baseline(FULL_VOCAB, tmp_path)
    mutation = Mutation(
        name="empty-unconstrained-fact-type",
        family="rejected",
        target="constraints[4]",
        apply=_rejected_empty_unconstrained_fact_type,
        predict=predict_violations,
    )
    case = emit_violating(
        model, assembly.doc, report, mutation, "constraints[4]", tmp_path / "role-empty.json", Random(1)
    )
    state = case.predicted["constraints[4]"]
    assert state.ground_truth == "no-subjects"
    assert state.expected_verdict == "vacuous"


def test_rejected_off_by_one_inside_max_bound_raises_on_the_empty_observed_set(
    tmp_path,
) -> None:
    model, assembly, report = _baseline(SETFAM, tmp_path)
    target = "fact_types[person_takes_course].constraints[0]"
    mutation = Mutation(
        name="off-by-one-inside-max-bound",
        family="rejected",
        target=target,
        apply=_rejected_off_by_one_inside_max_bound,
        predict=predict_violations,
    )
    with pytest.raises(PredictionMismatch) as excinfo:
        emit_violating(
            model, assembly.doc, report, mutation, target, tmp_path / "noop2.json", Random(1)
        )
    assert excinfo.value.mutation_name == "off-by-one-inside-max-bound"
    assert excinfo.value.observed == {}


def test_the_observed_set_is_one_expression_including_vacuous(tmp_path) -> None:
    """The deletion trap (Qwen-MEDIUM): the observed set INCLUDES vacuous
    transitions, so a deletion operator whose prediction is {no-subjects,
    vacuous} matches instead of spuriously mismatching."""
    model, assembly, report = _baseline(SETFAM, tmp_path)
    uniq_ref = "fact_types[booking_by_person].constraints[0]"
    ops, _ = operators_for(model, uniq_ref, assembly.doc)
    deletion = next(m for m in ops if m.name == "empty-fact-type")
    case = emit_violating(
        model, assembly.doc, report, deletion, uniq_ref, tmp_path / "del.json", Random(1)
    )
    assert "vacuous" in set(case.observed.values())
    assert set(case.observed) == set(case.predicted)


# --------------------------------------------------------------------------- #
# per-case verification over the full cross product (the D-05' loop)
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("model_path", ALL_MODELS, ids=lambda p: p.stem)
def test_every_enumerated_case_matches_its_prediction_against_the_real_checker(
    model_path, tmp_path
) -> None:
    """The full (constraint x operator) enumeration: every emitted case loads
    clean, and every predicted set (keys AND expected verdicts) matches the real
    checker's observed delta. The isolating fraction is recorded as a
    measurement, not assumed from operator names."""
    model, assembly, report = _baseline(model_path, tmp_path)
    cases, stand_downs = enumerate_violating(model, assembly.doc)
    assert cases, f"{model_path.name} enumerated no violating cases"
    isolating = 0
    for index, (ref, mutation) in enumerate(cases):
        case = emit_violating(
            model,
            assembly.doc,
            report,
            mutation,
            ref,
            tmp_path / f"case{index}.json",
            Random(1000 + index),
        )
        assert case.observed, f"{mutation.name} on {ref}: empty observed set admitted"
        assert set(case.observed) == set(case.predicted)
        for pred_ref, state in case.predicted.items():
            assert case.observed[pred_ref] == state.expected_verdict
        isolating += case.isolating
    fraction = isolating / len(cases)
    # A measurement, not an assumption: some fraction isolates, some does not —
    # and on every model here both classes are non-degenerate OR everything
    # isolates because each constraint owns its own fact type (the ring model).
    assert 0.0 < fraction <= 1.0
    for record in stand_downs:
        assert record["mechanism"]


def test_compare_observed_flags_an_unpredicted_ref_and_a_wrong_verdict(tmp_path) -> None:
    """The mismatch machinery itself is proven able to fail in both directions:
    a ref observed but not predicted, and a predicted verdict that differs."""
    model, assembly, report = _baseline(SETFAM, tmp_path)
    uniq_ref = "fact_types[booking_by_person].constraints[0]"
    ops, _ = operators_for(model, uniq_ref, assembly.doc)
    duplicate = next(m for m in ops if m.name == "duplicate-covered-role-value")
    doc = duplicate.apply(json.loads(json.dumps(assembly.doc)), model, uniq_ref, Random(1))
    doc["population"]["label"] = "violating"
    file = tmp_path / "cmp.json"
    file.write_text(json.dumps(doc), encoding="utf-8")
    mutated_report = check(model, load_population(str(file), model=model))

    # Direction 1: predicted map missing the observed ref.
    observed, discrepancies = compare_observed({}, report, mutated_report, target=uniq_ref)
    assert observed
    assert any(d["observed_verdict"] == "fail" and d["predicted"] is None for d in discrepancies)

    # Direction 2: right ref, wrong expected verdict.
    wrong = {
        uniq_ref: ExpectedState(ground_truth="violated", expected_verdict="warning", reason=None)
    }
    _observed, discrepancies = compare_observed(wrong, report, mutated_report, target=uniq_ref)
    assert any(
        d["constraint_ref"] == uniq_ref and d["observed_verdict"] == "fail" for d in discrepancies
    )


def _report(*verdicts: tuple[str, str, str]) -> CheckReport:
    """A CheckReport from ``(constraint_ref, modality, verdict)`` triples."""
    return CheckReport(
        verdicts=[
            ConstraintVerdict(
                scope_id=f"composition:oracle-verdict:n-a:{verdict}",
                constraint_ref=ref,
                constraint_type="uniqueness",
                modality=modality,
                source="explicit",
                status="confirmed",
                verdict=verdict,
                message="synthetic",
                reason_code="textual-not-mechanical" if verdict == "unchecked" else None,
            )
            for ref, modality, verdict in verdicts
        ]
    )


@pytest.mark.parametrize(
    ("before", "after", "predicted_verdict"),
    [
        ("warning", "pass", "pass"),
        ("vacuous", "pass", "pass"),
        ("pass", "unchecked", "unchecked"),
    ],
    ids=["deontic-repaired", "join-filled", "became-undecidable"],
)
def test_the_observed_delta_spans_all_five_verdict_states(
    before: str, after: str, predicted_verdict: str
) -> None:
    """WR-05: a predicted transition to `pass`/`unchecked` must be MATCHABLE.

    The observed delta used to be filtered to ``fail``/``warning``/``vacuous``,
    so a prediction of ``{satisfied, pass}`` (a mutation that incidentally
    repairs a deontic violation, or rows landing in a previously-empty join —
    the baseline is only guaranteed free of ALETHIC fails) could only ever appear
    in ``set(predicted) - set(observed)``. That aborted the whole ``gnd synth``
    run at exit 6 as a prediction/observation mismatch, pointing at the checker
    when the cause was the filter — and a reader is told to treat that quarantine
    as a candidate checker defect to reproduce, fix and promote.
    """
    ref = "fact_types[x].constraints[0]"
    baseline = _report((ref, "deontic", before))
    mutated = _report((ref, "deontic", after))
    predicted = {
        ref: ExpectedState(
            ground_truth="satisfied", expected_verdict=predicted_verdict, reason=None
        )
    }

    observed, discrepancies = compare_observed(predicted, baseline, mutated, target=ref)

    assert observed == {ref: after}, "the transition never reached the observed delta"
    assert discrepancies == [], discrepancies


def test_an_unchanged_verdict_is_still_not_a_transition() -> None:
    """The other half: widening the states must not turn every verdict into a
    delta. A silent no-op stays an empty observed set, which is itself a
    discrepancy."""
    ref = "fact_types[x].constraints[0]"
    baseline = _report((ref, "alethic", "pass"))
    unchanged = _report((ref, "alethic", "pass"))

    observed, discrepancies = compare_observed({}, baseline, unchanged, target=ref)

    assert observed == {}
    assert discrepancies and discrepancies[0]["constraint_ref"] == ref


def test_mutation_value_draw_uses_all_constraints_and_plural_range_unions():
    from random import Random

    from gnd.model import Model
    from gnd.synth.mutate import _out_of_spec_value, _valid_value

    model = Model(
        version=1,
        object_types=[{"id": "n", "kind": "value", "primitive": "Number"}],
        fact_types=[
            {
                "id": "observed",
                "reading": "{n} was observed",
                "roles": [{"object_type": "n", "role_name": "n"}],
                "constraints": [
                    {
                        "type": "value",
                        "object_type": "n",
                        "role_ref": {"fact_type": "observed", "role": "n"},
                        "range": {"min": -8, "max": 8},
                        "modality": "alethic",
                    }
                ],
            }
        ],
        constraints=[
            {
                "type": "value",
                "object_type": "n",
                "ranges": [
                    {"min": -10, "max": -5},
                    {"min": 5, "max": 10},
                ],
                "modality": "alethic",
            }
        ],
    )

    value = _valid_value(model, "observed", "n", "n", Random(11))
    outside = _out_of_spec_value(model.constraints[0])

    assert -8 <= value <= -5 or 5 <= value <= 8
    assert outside is not None
    assert not (-10 <= outside <= -5 or 5 <= outside <= 10)


# --------------------------------------------------------------------------- #
# task 2 — `gnd synth --class violating`: the CLI, the sidecar, the quarantine
# --------------------------------------------------------------------------- #


def _cli_violating(model_path: Path, out: Path, extra: list[str] | None = None) -> int:
    from gnd.cli import main

    return main(
        [
            "synth",
            str(model_path),
            "--out",
            str(out),
            "--class",
            "violating",
            "--seed",
            "1",
            *(extra or []),
        ]
    )


def _corpus_populations(out: Path) -> list[Path]:
    return [
        p
        for p in (out / "violating").glob("*.json")
        if not p.name.startswith("pool.")
        and not p.name.endswith(".meta.json")
        and not p.name.endswith(".discrepancy.json")
    ]


@pytest.mark.parametrize("model_path", ALL_MODELS, ids=lambda p: p.stem)
def test_cli_violating_emits_one_case_per_constraint_operator_pair(
    model_path, tmp_path
) -> None:
    """`gnd synth --class violating` exits 0, emits the full cross product with a
    sidecar each, records every case AND every not-derivable in index.json, and
    every emitted population re-loads clean against the model."""
    out = tmp_path / "o"
    assert _cli_violating(model_path, out) == 0

    model = load_model(str(model_path))
    assembly = assemble_conforming(model, 1, model_ref=model_path.name)
    cases, stand_downs = enumerate_violating(model, assembly.doc)

    populations = _corpus_populations(out)
    assert len(populations) == len(cases)
    index = json.loads((out / "index.json").read_text(encoding="utf-8"))
    indexed = [e for e in index["populations"] if e["class"] == "violating"]
    assert len(indexed) == len(cases)
    assert len(index["not_derivable"]) == len(stand_downs)
    for record in index["not_derivable"]:
        assert record["mechanism"]

    for population_file in populations:
        loaded = load_population(str(population_file), model=model)  # exit != 3
        assert loaded.label == "violating"


def test_violating_sidecars_carry_the_five_new_keys_and_the_typed_map(tmp_path) -> None:
    from gnd.synth.provenance import read_sidecar

    out = tmp_path / "o"
    assert _cli_violating(SETFAM, out, ["--baseline-seed", "7"]) == 0
    sidecars = sorted((out / "violating").glob("*.meta.json"))
    assert sidecars
    model = load_model(str(SETFAM))
    declared = {ref for ref, _c, _ft in mutate._constraint_iter_with_ref(model)}
    for sidecar_path in sidecars:
        sidecar = read_sidecar(sidecar_path)
        assert sidecar.class_ == "violating"
        assert sidecar.violates, "a violating sidecar must record the predicted SET"
        assert sidecar.violates_target in sidecar.violates or sidecar.violates_target in declared
        assert sidecar.isolating == (len(sidecar.violates) == 1)
        assert sidecar.isolation_verified is True
        assert sidecar.baseline_seed == 7  # traceable to the baseline it mutated
        # The typed expectations cover EVERY constraint, with the predicted
        # refs' ground truth being the PREDICTION (C1), not a checker echo.
        assert declared <= set(sidecar.expectations)
        for ref in sidecar.violates:
            assert sidecar.expectations[ref].ground_truth in ("violated", "no-subjects")


def test_the_isolating_fraction_is_reported_as_a_number_per_model(tmp_path, capsys) -> None:
    from gnd.cli import main

    out = tmp_path / "o"
    rc = main(
        [
            "synth",
            str(FULL_VOCAB),
            "--out",
            str(out),
            "--class",
            "violating",
            "--seed",
            "1",
            "--format",
            "json",
        ]
    )
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload["isolating_fraction"], float)
    assert 0.0 < payload["isolating_fraction"] < 1.0  # fv has BOTH classes (D-05')
    assert payload["isolating_cases"] + payload["set_attributed_cases"] == len(
        [e for e in payload["populations"] if e["class"] == "violating"]
    )


def test_class_all_emits_every_class_against_one_pool(tmp_path) -> None:
    """Plan 05 pinned two classes here; plan 06 lands the third, so ``all`` now
    means all THREE labels — and still exactly one pool behind them."""
    from gnd.cli import main
    from gnd.synth.provenance import read_sidecar

    out = tmp_path / "o"
    rc = main(
        ["synth", str(SETFAM), "--out", str(out), "--class", "all", "--seed", "3"]
    )
    assert rc == 0
    index = json.loads((out / "index.json").read_text(encoding="utf-8"))
    classes = {entry["class"] for entry in index["populations"]}
    assert classes == {"conforming", "boundary", "violating"}
    # One pool, shared: every sidecar's pool_sha256 agrees (C4's precondition).
    hashes = {
        read_sidecar(p).pool_sha256
        for p in out.rglob("*.meta.json")
    }
    assert len(hashes) == 1


def test_a_deliberate_misprediction_quarantines_types_the_discrepancy_and_exits_6(
    tmp_path, monkeypatch
) -> None:
    """The fault-injection proof the loud path is EXERCISED (C1): an operator
    whose prediction is deliberately wrong makes the CLI quarantine the case to
    <out>/quarantine/, emit a typed discrepancy, and exit 6 — the case RETAINED,
    the sidecar carrying the (wrong) PREDICTION rather than being relabelled to
    match observation, and exit 5 never used for a disagreement."""
    from gnd.cli import main
    from gnd.synth.provenance import read_sidecar

    honest = mutate.predict_violations

    def lying_predict(model, baseline_doc, mutated_doc):
        predicted = honest(model, baseline_doc, mutated_doc)
        if predicted:
            predicted.pop(min(predicted))  # mis-predict: drop one violated ref
        return predicted

    monkeypatch.setattr(mutate, "predict_violations", lying_predict)
    out = tmp_path / "o"
    rc = main(
        ["synth", str(SETFAM), "--out", str(out), "--class", "violating", "--seed", "1"]
    )
    assert rc == 6  # EXIT_QUARANTINE — never 5 (reserved for structural GeneratorError)

    quarantined = [
        p
        for p in (out / "quarantine").glob("*.json")
        if not p.name.endswith(".meta.json") and not p.name.endswith(".discrepancy.json")
    ]
    assert len(quarantined) == 1  # RETAINED, not discarded
    case = quarantined[0]
    discrepancies = json.loads(
        case.with_suffix(".discrepancy.json").read_text(encoding="utf-8")
    )
    assert discrepancies
    for record in discrepancies:
        assert record["kind"] == "prediction-observation-mismatch"
        assert set(record) >= {"constraint_ref", "predicted", "observed_verdict", "kind"}

    # The sidecar is NOT relabelled to match observation: the ref the lying
    # prediction dropped is absent from `violates`, present in the discrepancy.
    sidecar = read_sidecar(case.with_suffix(".meta.json"))
    dropped = {d["constraint_ref"] for d in discrepancies if d["predicted"] is None}
    assert dropped
    assert not dropped & set(sidecar.violates or [])
    assert sidecar.isolation_verified is False  # the checker did NOT confirm this case

    # And the case was moved out of the corpus directory, not double-counted.
    assert not any(case.name == p.name for p in _corpus_populations(out))


def test_boundary_class_is_derived_and_is_never_a_silent_conforming_run(tmp_path) -> None:
    """Plan 05 pinned ``--class boundary`` at exit 64 (an explicit refusal, not a
    silent stub). Plan 06 implements it, so the pin becomes its successor: the
    run succeeds AND produces cases that are genuinely boundary-labelled — never
    a conforming run wearing a boundary flag."""
    from gnd.cli import main

    out = tmp_path / "o"
    rc = main(["synth", str(SETFAM), "--out", str(out), "--class", "boundary", "--seed", "1"])
    assert rc == 0
    index = json.loads((out / "index.json").read_text(encoding="utf-8"))
    assert index["populations"]
    assert {entry["class"] for entry in index["populations"]} == {"boundary"}
    assert not (out / "conforming").exists()
    # The unreachable bounds are REPORTED, not silently dropped.
    assert index["not_derivable"]
