"""The conforming class's expectation is DERIVED, never copied off the checker (CR-02).

``_build_expectations`` took ``ground_truth`` from the constructive witness — the
independent oracle C1 asked for — but took ``expected_verdict`` from the verdict
the checker had just emitted for that very population. Every conforming
observation therefore agreed with its own expectation by construction, so
``classify`` scored it ``correct`` whatever the checker said, including an
abstention.

The reproduction below is the F-05 over-correction the plan lists six controls
against, made concrete: a checker that answers ``vacuous`` for every ``value``
constraint over a fully-populated, satisfied universe. Before the fix the
published ``undecided_rate`` read **0.0** while the checker abstained on 100% of
those observations. ``CELLS[('alethic', 'satisfied', 'vacuous')]`` is
``undecided``, and D-02 exists so "we couldn't decide" is never folded away.

The second-order effect is pinned too: once an abstention becomes the
expectation, a LATER, FIXED checker returning ``pass`` scores a ``false_pass`` —
so repairing a checker made the committed corpus report a defect.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

import gnd.correspondence
import gnd.semantic_spec
from gnd.checker import check
from gnd.cli import _cmd_measure, main
from gnd.model import load_model
from gnd.population import load_population
from gnd.synth.assemble import _direct_subtypes, assemble_conforming
from gnd.synth.provenance import read_sidecar

REPO_ROOT = Path(__file__).resolve().parent.parent
FULL_VOCAB = REPO_ROOT / "tests" / "fixtures" / "models" / "full_vocabulary.orm.yaml"

#: Captured before any monkeypatch so the stub can delegate for every other family.
_REAL_EVALUATE = gnd.correspondence.evaluate_snapshot


def _spuriously_vacuous(adapted, *, variant_aliases=None, reference_work=None):
    """A checker defect of exactly the shape F-05 was: abstain where a decision
    was due, over a universe that is populated and satisfied."""
    real = _REAL_EVALUATE(adapted, variant_aliases=variant_aliases, reference_work=reference_work)
    scope = "composition:oracle-verdict:n-a:vacuous"
    findings = tuple(
        replace(
            finding,
            scope_id=scope,
            verdict="vacuous",
            reason_code=None,
            witness=(),
            witness_keys=(),
            applicable_scope_ids=(scope,),
        )
        if finding.family == "value" and finding.verdict not in {"vacuous", "unchecked"}
        else finding
        for finding in real.findings
    )
    result_band = gnd.semantic_spec.band_of(
        tuple((finding.modality, finding.verdict) for finding in findings)
    )
    return gnd.correspondence.SnapshotDecision(
        findings=findings,
        band=result_band,
        acceptance_ready=result_band == 0,
        semantic_decision=gnd.semantic_spec.decision_of(result_band),
    )


def _value_refs(model) -> list[str]:
    from gnd.synth.assemble import _constraint_iter_with_ref

    return [
        ref
        for ref, constraint, _ft in _constraint_iter_with_ref(model)
        if str(constraint.get("type")) == "value"
    ]


def test_a_spuriously_vacuous_checker_is_published_as_undecided(monkeypatch, tmp_path):
    """The reproduction, end to end: synth then measure with the stub active."""
    out = tmp_path / "corpus"
    payload_path = tmp_path / "m.json"

    monkeypatch.setattr(gnd.correspondence, "evaluate_snapshot", _spuriously_vacuous)
    assert (
        main(
            [
                "synth",
                str(FULL_VOCAB),
                "--out",
                str(out),
                "--seed",
                "1",
                "--class",
                "conforming",
                "--format",
                "json",
            ]
        )
        == 0
    )
    _cmd_measure(str(FULL_VOCAB), str(out), "json", str(payload_path))
    monkeypatch.undo()

    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    model = load_model(str(FULL_VOCAB))
    value_refs = set(_value_refs(model))
    assert value_refs, "the fixture must declare value constraints for this to mean anything"

    rows = {row["constraint_ref"]: row for row in payload["per_constraint"]}
    for ref in value_refs:
        row = rows[ref]
        assert row["cells"]["correct"] == 0, (
            f"{ref}: an abstention over a satisfied, populated universe scored "
            f"`correct` — the expectation was copied from the observation"
        )
        assert row["cells"]["undecided"] == row["n"]
        assert row["undecided_rate"] == 1.0, (
            f"{ref}: published undecided_rate {row['undecided_rate']} while the "
            f"checker abstained on every observation"
        )


def test_the_sidecar_records_the_derived_verdict_not_the_observed_one(monkeypatch, tmp_path):
    """The same defect at the artifact level: the sidecar must say `pass`.

    ``pass`` is what a CORRECT checker emits for a satisfied, populated ``value``
    constraint; the stub said ``vacuous``. If the sidecar records ``vacuous``,
    every downstream rate is measured against the defect.
    """
    out = tmp_path / "corpus"
    monkeypatch.setattr(gnd.correspondence, "evaluate_snapshot", _spuriously_vacuous)
    assert (
        main(
            [
                "synth",
                str(FULL_VOCAB),
                "--out",
                str(out),
                "--seed",
                "1",
                "--class",
                "conforming",
                "--format",
                "json",
            ]
        )
        == 0
    )
    monkeypatch.undo()

    sidecar = read_sidecar(next((out / "conforming").glob("*.meta.json")))
    model = load_model(str(FULL_VOCAB))
    for ref in _value_refs(model):
        state = sidecar.expectations[ref]
        assert (state.ground_truth, state.expected_verdict) == ("satisfied", "pass"), (
            f"{ref}: the sidecar recorded {state.expected_verdict!r}, which is what "
            f"the stubbed checker said, not what a correct checker should emit"
        )


def test_fixing_a_checker_abstention_does_not_report_a_false_pass(monkeypatch, tmp_path):
    """The second-order effect, pinned.

    Generate under the abstaining checker, then measure with the REAL one. Once
    the expectation was the abstention, ``classify``'s expected-unchecked rule
    scored the repaired ``pass`` as a ``false_pass`` and the run exited 6:
    fixing a checker made the corpus report a defect.
    """
    out = tmp_path / "corpus"
    payload_path = tmp_path / "m.json"

    monkeypatch.setattr(gnd.correspondence, "evaluate_snapshot", _spuriously_vacuous)
    assert (
        main(
            [
                "synth",
                str(FULL_VOCAB),
                "--out",
                str(out),
                "--seed",
                "1",
                "--class",
                "conforming",
                "--format",
                "json",
            ]
        )
        == 0
    )
    monkeypatch.undo()

    # The REAL checker now decides those constraints correctly.
    exit_code = _cmd_measure(str(FULL_VOCAB), str(out), "json", str(payload_path))

    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    model = load_model(str(FULL_VOCAB))
    rows = {row["constraint_ref"]: row for row in payload["per_constraint"]}
    for ref in _value_refs(model):
        assert rows[ref]["cells"]["false_pass"] == 0, (
            f"{ref}: a repaired checker scored a false pass against a corpus whose "
            f"expectation was the old defect"
        )
        assert rows[ref]["cells"]["correct"] == rows[ref]["n"]
    assert exit_code == 0, "no checker defect exists here — the checker is the real one"


def test_the_oracle_never_reads_the_report(monkeypatch):
    """Structural, not behavioural: ``_build_expectations`` takes no report.

    A signature that cannot accept the checker's output cannot copy from it. This
    is the guard that survives a future edit re-introducing "just use the observed
    verdict when the oracle is unsure".
    """
    import inspect

    from gnd.synth.assemble import _build_expectations

    parameters = set(inspect.signature(_build_expectations).parameters)
    assert "report" not in parameters, (
        "_build_expectations regained access to the checker's report — the only "
        "reason to pass it in is to copy a verdict out of it (CR-02)"
    )


def test_the_derived_expectation_matches_the_real_checker_on_a_clean_baseline():
    """The control on the control: with the REAL checker, the independent oracle
    and the observation agree on every constraint.

    Without this, the tests above would pass equally well against an oracle that
    is simply wrong — the disagreement they detect has to be the checker's.
    """
    from gnd.synth.assemble import _build_expectations, _constraint_iter_with_ref

    model = load_model(str(FULL_VOCAB))
    assembly = assemble_conforming(model, 1, model_ref=FULL_VOCAB.name)
    expectations = _build_expectations(model, assembly.doc, _direct_subtypes(model))

    declared = {ref for ref, _c, _ft in _constraint_iter_with_ref(model)}
    assert set(expectations) == declared, "every declared constraint is labelled"

    path = Path(__file__).parent / "_tmp_expectation_independence.json"
    try:
        path.write_text(json.dumps(assembly.doc), encoding="utf-8")
        report = check(model, load_population(str(path), model=model))
    finally:
        path.unlink(missing_ok=True)
    for verdict in report.verdicts:
        assert expectations[verdict.constraint_ref].expected_verdict == verdict.verdict, (
            f"{verdict.constraint_ref}: the independent oracle says "
            f"{expectations[verdict.constraint_ref].expected_verdict!r}, the real "
            f"checker says {verdict.verdict!r}"
        )


@pytest.mark.parametrize("seed", [1, 7, 13])
def test_no_constraint_is_left_unlabelled_on_the_corpus_model(seed):
    """The `None` branch is a REFUSAL, so it must not fire on a model in the
    committed corpus — if it did, `gnd synth` would exit 5 there."""
    model = load_model(str(FULL_VOCAB))
    assembly = assemble_conforming(model, seed, model_ref=FULL_VOCAB.name)
    from gnd.synth.assemble import _constraint_iter_with_ref

    assert set(assembly.expectations) == {ref for ref, _c, _ft in _constraint_iter_with_ref(model)}
