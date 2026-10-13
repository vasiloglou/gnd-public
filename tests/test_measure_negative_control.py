"""The permanent negative control: the measurement must be able to report a bad number.

A false-pass rate of exactly 0.0 for every constraint is the expected result if
the checker is sound — and ALSO the expected result if the harness is broken
(RESEARCH Pitfall 5). Only this control distinguishes them: feed the harness a
checker whose authoritative correspondence decision returns ``pass``
unconditionally and require the
report to say so, at the rate AND at the exit code. UNMARKED and offline on
purpose — it runs in the default lane, forever.

**The cohort (C2).** The broken-run floor is asserted over the ALETHIC
CONDITIONAL false-pass rate — ``false_pass / expected_nonpass``, never ``/ n``
(over ``n`` the >=0.9 floor would be unreachable or denominator-dependent). The
cohort is the ``expected_nonpass`` observations: predicted ``ground_truth`` in
{violated, no-subjects}, restricted to alethic constraints, EXCLUDING the
observations whose ``expected_verdict`` is ``vacuous`` — exactly the deletion
(``empty-fact-type``) and coverage-omission (``drop-fact-type-from-covers``)
operators' emptied constraints. Those legitimately reach ``vacuous`` under ANY
checker: the vacuity clauses fire BEFORE ``_evaluate``, so even an always-pass
stub never sees them, and leaving them in would dilute the floor for a reason
that says nothing about detection.

**The control on the control — read this before "tidying" it.** The rate
assertion and the exit-code assertion are EACH re-run against the real checker
in their OWN ``pytest.raises(AssertionError)`` block, one assert per block. A
single block holding both is satisfied by whichever fails first, so the second
may never execute and its ability to fail is never demonstrated — the exact
shape of gate this project has shipped five times. If either flip block ever
goes green-by-not-raising because the real rate climbed to 0.9 or the real exit
reached 6, that is a CHECKER DEFECT under D-01 — reproduce it, fix it, promote a
corpus case; do NOT loosen the threshold and do NOT merge the blocks.
"""

from __future__ import annotations

import inspect
import json
from dataclasses import replace
from pathlib import Path

import pytest

import gnd.checker
import gnd.correspondence
import gnd.semantic_spec
from gnd import cli
from gnd.checker import band, check
from gnd.cli import _cmd_measure, main
from gnd.measure.score import classify
from gnd.model import load_model
from gnd.population import load_population
from gnd.synth.provenance import read_sidecar

REPO_ROOT = Path(__file__).resolve().parent.parent
FULL_VOCAB = REPO_ROOT / "tests" / "fixtures" / "models" / "full_vocabulary.orm.yaml"
SETFAM = REPO_ROOT / "tests" / "fixtures" / "checker" / "setfam.orm.yaml"

#: The floor the broken run must clear. NOT the expected value — the measured
#: broken-run rate is recorded in the plan SUMMARY as a number.
BROKEN_FLOOR = 0.9


@pytest.fixture(scope="module")
def corpus(tmp_path_factory) -> Path:
    """One violating corpus for the whole module (fv, fixed seeds, offline)."""
    out = tmp_path_factory.mktemp("negative-control")
    rc = main(
        [
            "synth",
            str(FULL_VOCAB),
            "--out",
            str(out),
            "--class",
            "violating",
            "--seed",
            "11",
            "--baseline-seed",
            "11",
        ]
    )
    assert rc == 0
    return out


@pytest.fixture(scope="module")
def model():
    return load_model(str(FULL_VOCAB))


def _observations(model, corpus_dir: Path) -> list[tuple[str, str, object, str]]:
    """(ref, modality, ExpectedState, observed_verdict) over the whole corpus,
    with the CURRENT ``gnd.checker.check`` — so a monkeypatched authoritative
    correspondence decision is what gets measured, with no production hook of
    any kind."""
    index = json.loads((corpus_dir / "index.json").read_text(encoding="utf-8"))
    rows: list[tuple[str, str, object, str]] = []
    for entry in index["populations"]:
        # CORPUS-ROOT-RELATIVE entries (CR-01) — joined to the root, exactly as
        # `gnd measure` resolves them.
        population_path = corpus_dir / entry["population"]
        sidecar = read_sidecar(population_path.with_suffix(".meta.json"))
        population = load_population(str(population_path), model=model)
        report = check(model, population)
        for verdict in report.verdicts:
            rows.append(
                (
                    verdict.constraint_ref,
                    verdict.modality,
                    sidecar.expectations[verdict.constraint_ref],
                    verdict.verdict,
                )
            )
    return rows


def _alethic_conditional_false_pass_rate(rows) -> tuple[float, int]:
    """``false_pass / expected_nonpass`` over the negative-control cohort (C2).

    Cohort definition — see the module docstring: alethic, predicted ground
    truth in {violated, no-subjects}, expected verdict != vacuous (the deletion
    and coverage-omission exclusion).
    """
    cohort = [
        (ref, modality, expected, observed)
        for ref, modality, expected, observed in rows
        if modality == "alethic"
        and expected.ground_truth in ("violated", "no-subjects")
        and expected.expected_verdict != "vacuous"
    ]
    assert cohort, "the negative-control cohort is empty — nothing is being measured"
    false_passes = sum(
        1
        for _ref, modality, expected, observed in cohort
        if classify(expected, observed, modality) == "false_pass"
    )
    return false_passes / len(cohort), len(cohort)


def _forced_correspondence(verdict):
    """Build a test-only replacement for the one authoritative decision seam."""

    def decide(adapted, *, variant_aliases=None, reference_work=None):
        real = _REAL_EVALUATE_SNAPSHOT(adapted, variant_aliases=variant_aliases, reference_work=reference_work)
        scope = f"composition:oracle-verdict:n-a:{verdict}"
        # The retired evaluator seam was reached only after applicability and
        # mechanical-support refusals. Preserve those authentic abstentions;
        # force only findings for which a semantic decision was due.
        findings = tuple(
            finding
            if finding.verdict in {"vacuous", "unchecked"}
            else replace(
                finding,
                scope_id=scope,
                verdict=verdict,
                reason_code="stubbed" if verdict == "unchecked" else None,
                witness=(),
                witness_keys=(),
                applicable_scope_ids=(scope,),
            )
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

    return decide


_REAL_EVALUATE_SNAPSHOT = gnd.correspondence.evaluate_snapshot
_ALWAYS_PASS = _forced_correspondence("pass")


@pytest.fixture(scope="module")
def real_run(model, corpus, tmp_path_factory):
    """The real checker's baseline — computed ONCE, asserted in the tests."""
    out = tmp_path_factory.mktemp("real") / "measurement.json"
    exit_code = _cmd_measure(str(FULL_VOCAB), str(corpus), "json", str(out))
    rate, cohort_n = _alethic_conditional_false_pass_rate(_observations(model, corpus))
    payload = json.loads(out.read_text(encoding="utf-8"))
    return {"rate": rate, "cohort_n": cohort_n, "exit": exit_code, "payload": payload}


def test_the_real_baseline_is_positively_asserted_on_both_halves(real_run) -> None:
    """Step 1: the real checker's rate is < 0.9 AND `gnd measure` exits 0 —
    ASSERTED, never merely recorded, or the flip blocks below would rest on
    assertions that may never execute."""
    assert real_run["rate"] < BROKEN_FLOOR
    assert real_run["exit"] == 0


def test_an_always_pass_checker_is_reported_at_the_rate(monkeypatch, model, corpus) -> None:
    """Fed a checker that returns `pass` unconditionally, the alethic CONDITIONAL
    false-pass rate over the expected_nonpass cohort reaches >= 0.9."""
    monkeypatch.setattr(gnd.correspondence, "evaluate_snapshot", _ALWAYS_PASS)
    rate, cohort_n = _alethic_conditional_false_pass_rate(_observations(model, corpus))
    assert cohort_n > 0
    assert rate >= BROKEN_FLOOR, (
        f"the harness reported {rate:.4f} over {cohort_n} expected-nonpass "
        f"observations against an always-pass checker — it is measuring nothing"
    )


def test_an_always_pass_checker_is_reported_at_the_exit_code(
    monkeypatch, model, corpus, tmp_path
) -> None:
    """...and `gnd measure` exits 6 (EXIT_CHECKER_DEFECT): by D-01 an alethic
    checker false pass is a reproducible defect, not a rate to write down."""
    monkeypatch.setattr(gnd.correspondence, "evaluate_snapshot", _ALWAYS_PASS)
    out = tmp_path / "broken.json"
    exit_code = _cmd_measure(str(FULL_VOCAB), str(corpus), "json", str(out))
    assert exit_code == 6
    payload = json.loads(out.read_text(encoding="utf-8"))
    kinds = {defect["kind"] for defect in payload["checker_defects"]}
    assert "false-pass" in kinds
    # Every defect record carries what a reader needs to REGENERATE the input.
    for defect in payload["checker_defects"]:
        assert set(defect) >= {
            "kind",
            "constraint_ref",
            "modality",
            "population",
            "sidecar",
            "expected_verdict",
            "observed_verdict",
            "seed",
        }


def test_the_rate_flip_control_fails_against_the_real_checker(real_run) -> None:
    """Flip block ONE — exactly one assert. See the module docstring before
    merging this with its sibling: a shared block is satisfied by whichever
    fails first, and the second assertion's ability to fail is never shown."""
    with pytest.raises(AssertionError):
        assert real_run["rate"] >= BROKEN_FLOOR


def test_the_exit_flip_control_fails_against_the_real_checker(real_run) -> None:
    """Flip block TWO — exactly one assert, independently proven able to fail."""
    with pytest.raises(AssertionError):
        assert real_run["exit"] == 6


# --------------------------------------------------------------------------- #
# masked_by_vacuity — a separate counter, exercised by a deletion operator
# --------------------------------------------------------------------------- #


def test_masked_by_vacuity_is_exercised_by_a_deletion_operator_case(real_run, corpus) -> None:
    """`(violated, vacuous)` is a DISJOINT cell that is ALSO summed into the
    published undecided rate — visible without leaving the denominator. The
    family-emptied mandatory (`empty-fact-type`) is the exercising case: its
    instances stay observable, so ground truth is violated while the checker
    (correctly, per D-12 clause 1) answers vacuous."""
    masked_rows = [
        row
        for row in real_run["payload"]["per_constraint"]
        if row["cells"]["masked_by_vacuity"] > 0
    ]
    assert masked_rows, "no masked_by_vacuity cell was exercised"
    for row in masked_rows:
        assert row["undecided_rate"] > 0.0  # re-absorbed into undecided (D-02)
        assert sum(row["cells"].values()) == row["n"]  # still a partition cell
    # And the exercising population really is a deletion-operator case whose
    # sidecar predicted the mask: {violated, vacuous}.
    deletion_sidecars = [
        read_sidecar(path) for path in (corpus / "violating").glob("*.empty-fact-type.meta.json")
    ]
    assert any(
        state.ground_truth == "violated" and state.expected_verdict == "vacuous"
        for sidecar in deletion_sidecars
        for state in sidecar.expectations.values()
    )


# --------------------------------------------------------------------------- #
# the deontic carve-out — scored against the VERDICT, never acceptance
# --------------------------------------------------------------------------- #


def test_a_violated_deontic_constraint_is_scored_against_the_verdict(model, corpus) -> None:
    """A violated deontic constraint yields `warning` while the run's
    `acceptance_ready` is unaffected — so measuring deontic constraints against
    acceptance would report 0% false-pass BY CONSTRUCTION. The false pass is
    `(expected warning, observed pass)`, taken against the verdict."""
    index = json.loads((corpus / "index.json").read_text(encoding="utf-8"))
    deontic_case = None
    for entry in index["populations"]:
        population_path = corpus / entry["population"]
        sidecar = read_sidecar(population_path.with_suffix(".meta.json"))
        violates = sidecar.violates or []
        if violates and all(
            sidecar.expectations[ref].expected_verdict == "warning" for ref in violates
        ):
            deontic_case = (population_path, sidecar)
            break
    assert deontic_case is not None, "no purely-deontic violating case in the corpus"
    population_path, sidecar = deontic_case
    population = load_population(str(population_path), model=model)
    report = check(model, population)
    observed = {v.constraint_ref: v.verdict for v in report.verdicts}
    for ref in sidecar.violates:
        expected = sidecar.expectations[ref]
        assert observed[ref] == "warning"  # the violated deontic yields warning
        assert classify(expected, "warning", "deontic") == "correct"
        # The false pass is measured against the VERDICT: observing `pass` on a
        # violated deontic constraint scores false_pass.
        assert classify(expected, "pass", "deontic") == "false_pass"
    # acceptance_ready is UNAFFECTED by the deontic violation: full_vocabulary's
    # baseline band is 4 (the alethic textual), and it stays 4 — the deontic
    # warning moved nothing.
    assert band(report) == 4


# --------------------------------------------------------------------------- #
# D-21: wrong_attribution == 0, pinned — and the pin proven able to fail
# --------------------------------------------------------------------------- #


def test_wrong_attribution_is_zero_on_the_real_run(real_run) -> None:
    assert real_run["payload"]["coverage_summary"]["wrong_attribution"] == 0
    for row in real_run["payload"]["per_constraint"]:
        assert row["wrong_attribution"] == 0


def test_a_mislabelled_sidecar_drives_wrong_attribution_nonzero_and_exits_6(
    tmp_path,
) -> None:
    """The pin's own negative control: a sidecar whose `violates` set is
    deliberately edited to exclude a genuinely violated constraint produces a
    non-zero counter, a checker_defects[] entry of kind `wrong_attribution`, and
    exit 6 — while the partition invariant stands (the observation still lands
    in false_fail; wrong_attribution double-counts it under its own name)."""
    out = tmp_path / "corpus"
    rc = main(
        [
            "synth",
            str(SETFAM),
            "--out",
            str(out),
            "--class",
            "violating",
            "--seed",
            "5",
            "--baseline-seed",
            "5",
        ]
    )
    assert rc == 0

    # Find an isolating alethic case and relabel its violated ref `satisfied`.
    target_ref = None
    for sidecar_path in sorted((out / "violating").glob("*.meta.json")):
        document = json.loads(sidecar_path.read_text(encoding="utf-8"))
        violates = document.get("violates") or []
        if (
            len(violates) == 1
            and document["expectations"][violates[0]]["expected_verdict"] == "fail"
        ):
            target_ref = violates[0]
            document["violates"] = []
            document["isolating"] = False
            document["expectations"][target_ref] = {
                "ground_truth": "satisfied",
                "expected_verdict": "pass",
                "reason": None,
            }
            sidecar_path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
            # The index is a redundant cache of the sidecar — `gnd measure`
            # exits 3 on ANY index/sidecar disagreement (the binding guard added
            # in Phase 2's review-fix round). A *coherent* mislabel therefore
            # edits both files; an incoherent one is caught upstream as
            # malformed corpus input and never reaches the attribution scorer
            # this control exists to exercise.
            index_path = out / "index.json"
            index = json.loads(index_path.read_text(encoding="utf-8"))
            rel = f"violating/{sidecar_path.name}"
            for entry in index["populations"]:
                if entry["sidecar"] == rel:
                    entry["violates"] = []
                    entry["isolating"] = False
                    break
            index_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
            break
    assert target_ref is not None

    result = tmp_path / "measurement.json"
    exit_code = _cmd_measure(str(SETFAM), str(out), "json", str(result))
    assert exit_code == 6
    payload = json.loads(result.read_text(encoding="utf-8"))
    assert payload["coverage_summary"]["wrong_attribution"] >= 1
    wrong = [d for d in payload["checker_defects"] if d["kind"] == "wrong_attribution"]
    assert wrong
    assert any(d["constraint_ref"] == target_ref for d in wrong)
    # The partition invariant from plan 04 still holds on every row —
    # wrong_attribution double-counts a false_fail under a name, it does not
    # remove it from the partition or add a seventh cell.
    for row in payload["per_constraint"]:
        assert sum(row["cells"].values()) == row["n"]
    target_row = next(
        row for row in payload["per_constraint"] if row["constraint_ref"] == target_ref
    )
    assert target_row["wrong_attribution"] >= 1
    assert target_row["cells"]["false_fail"] >= 1


# --------------------------------------------------------------------------- #
# T-02-21: no production bypass substitutes the checker
# --------------------------------------------------------------------------- #


def test_no_flag_env_var_or_keyword_substitutes_the_checker() -> None:
    """The stub above is applied by monkeypatch in the test process ONLY. No
    parameter of `check()` or `_cmd_measure()` accepts a checker substitute —
    the same no-bypass rule `load_population(..., model=)` carries (D-18), and
    for the same reason: a bypass is the first thing a failing agent reaches
    for."""
    signature = inspect.signature(check)
    assert list(signature.parameters) == [
        "model", "population", "references", "compiled_operations",
    ]
    assert signature.parameters["references"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["references"].default is None
    assert signature.parameters["compiled_operations"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["compiled_operations"].default is False
    assert list(inspect.signature(cli._cmd_measure).parameters) == [
        "model_path",
        "populations",
        "output_format",
        "out",
        # plan 06's D-14 promotion target — a DESTINATION for defect-revealing
        # inputs, never a checker substitute.
        "promote",
        # Phase 4's trusted output projection switch; it changes presentation,
        # never the checker implementation or measured semantics.
        "unredacted",
    ]


# --------------------------------------------------------------------------- #
# F-6: the ABSTAINING directions — reported at the rate, not at the exit code
# --------------------------------------------------------------------------- #

#: The floor the abstaining runs must clear on the undecided rate, and the
#: ceiling the real run must stay under. Mirrors BROKEN_FLOOR's role: not the
#: expected value, the threshold below which the harness is measuring nothing.
ABSTENTION_FLOOR = 0.9


_ALWAYS_VACUOUS = _forced_correspondence("vacuous")
_ALWAYS_UNCHECKED = _forced_correspondence("unchecked")


@pytest.fixture(scope="module")
def abstaining_runs(corpus, tmp_path_factory):
    """Both abstaining directions, measured once each with the REAL pipeline.

    ``monkeypatch`` is function-scoped, so the substitution is made and undone
    explicitly here; the substitution still exists nowhere but this process
    (T-02-21).
    """
    out = tmp_path_factory.mktemp("abstaining")
    runs: dict[str, dict] = {}
    real = gnd.correspondence.evaluate_snapshot
    for name, stub in (
        ("vacuous", _ALWAYS_VACUOUS),
        ("unchecked", _ALWAYS_UNCHECKED),
    ):
        payload_path = out / f"{name}.json"
        gnd.correspondence.evaluate_snapshot = stub
        try:
            exit_code = _cmd_measure(str(FULL_VOCAB), str(corpus), "json", str(payload_path))
        finally:
            gnd.correspondence.evaluate_snapshot = real
        runs[name] = {
            "exit": exit_code,
            "payload": json.loads(payload_path.read_text(encoding="utf-8")),
        }
    return runs


@pytest.mark.parametrize("direction", ["vacuous", "unchecked"])
def test_an_always_abstaining_checker_collapses_every_row_s_coverage(
    abstaining_runs, direction
) -> None:
    """F-6: the always-``pass`` control was the only direction pinned.

    A checker that regressed into ABSTENTION leaves the exit code and
    ``checker_defects`` untouched — so the permanent control stayed green while
    the checker decided nothing at all. The signal is present and loud, in
    ``coverage``: it is the fraction of observations the checker DECIDED, and it
    goes to 0.0 on every row.
    """
    rows = abstaining_runs[direction]["payload"]["per_constraint"]
    assert rows
    assert max(row["coverage"] for row in rows) == 0.0, (
        "the checker decided nothing and per-row coverage did not say so"
    )


@pytest.mark.parametrize("direction", ["vacuous", "unchecked"])
def test_an_always_abstaining_checker_is_reported_at_the_undecided_rate(
    abstaining_runs, direction
) -> None:
    """D-02's third number, doing the job it exists for.

    Folding "we couldn't decide" into either error rate is the error this
    project has been correcting throughout; the corollary is that the undecided
    rate has to MOVE when the checker stops deciding.
    """
    rows = abstaining_runs[direction]["payload"]["per_constraint"]
    assert max(row["undecided_rate"] for row in rows) >= ABSTENTION_FLOOR


@pytest.mark.parametrize("direction", ["vacuous", "unchecked"])
def test_an_expected_abstention_is_not_inflated_by_the_undecided_rate(
    abstaining_runs, direction
) -> None:
    """The control on the two above (C3): the rate must not be satisfied by
    counting EVERY abstention.

    ``constraints[13]`` is the alethic ``textual`` — expected-unchecked BY
    DESIGN, because nothing about it is mechanically evaluable. It is never
    routed through ``_evaluate`` at all, so the stub never sees it and its row
    stays wholly ``correct``. Without this, an undecided rate that simply
    counted abstentions would pass the two tests above while telling a reader
    nothing.
    """
    rows = {
        row["constraint_ref"]: row
        for row in abstaining_runs[direction]["payload"]["per_constraint"]
    }
    textual = next(row for row in rows.values() if row["constraint_type"] == "textual")
    assert textual["undecided_rate"] == 0.0
    assert textual["cells"]["correct"] == textual["n"]


@pytest.mark.parametrize("direction", ["vacuous", "unchecked"])
def test_the_abstaining_directions_exit_0_with_no_defect_and_that_is_the_point(
    abstaining_runs, direction
) -> None:
    """Pinned as DESIGN, not as an oversight — read before "fixing" it.

    Under D-01 an abstention is not a checker defect: a defect is a
    reproducible wrong answer, and "I did not decide" is not an answer. Under
    D-02 it is a rate to write down. So exit 0 with ``checker_defects: []`` is
    correct here, and the two tests above are where the alarm lives. This test
    exists so that a future change moving the alarm TO the exit code has to
    change a test that says why the exit code is not the alarm — rather than
    leaving both silent, which is the state F-6 found.
    """
    run = abstaining_runs[direction]
    assert run["exit"] == 0
    assert run["payload"]["checker_defects"] == []


def test_the_coverage_flip_control_fails_against_the_real_checker(real_run) -> None:
    """Flip block THREE — exactly one assert, per the module docstring."""
    with pytest.raises(AssertionError):
        assert max(row["coverage"] for row in real_run["payload"]["per_constraint"]) == 0.0


def test_the_undecided_flip_control_fails_against_the_real_checker(real_run) -> None:
    """Flip block FOUR — exactly one assert, independently proven able to fail."""
    with pytest.raises(AssertionError):
        assert (
            max(row["undecided_rate"] for row in real_run["payload"]["per_constraint"])
            >= ABSTENTION_FLOOR
        )
