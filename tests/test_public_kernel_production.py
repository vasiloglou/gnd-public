"""Kernel/bridge/public-projection mutation gates over reviewed generic slice inputs.
No proof tool or certificate reader runs in this module.
"""
from __future__ import annotations

import json
from typing import Any

import pytest
from test_public_slice_runtime import CASES, CORPUS
from test_public_slice_runtime import EXPECTED as SLICE_EXPECTED

from gnd import checker as checker_module
from gnd import proof_bridge, proof_kernel
from gnd.checker import band, check
from gnd.model import load_model
from gnd.population import load_population
from gnd.report import build_check_payload

EXPECTED = SLICE_EXPECTED["cases"]
CASE_BY_ID = {row["id"]: row for row in CASES["cases"]}


IN_SCOPE_IDS = tuple(
    case_id for case_id in sorted(EXPECTED) if EXPECTED[case_id]["whole_result_in_scope"]
)


DIGEST = "sha256:" + "0" * 64


def _load(case_id: str):
    row = CASE_BY_ID[case_id]
    model = load_model(CORPUS / row["model"])
    return model, load_population(CORPUS / row["population"], model=model)


def _public(case_id: str) -> dict[str, Any]:
    model, population = _load(case_id)
    report = check(model, population)
    exit_code = band(report)
    return build_check_payload(
        exit_code,
        str(CORPUS / CASE_BY_ID[case_id]["model"]),
        str(CORPUS / CASE_BY_ID[case_id]["population"]),
        schema_version=5,
        model_digest=DIGEST,
        report=report,
    )


def _raising(name: str):
    def sentinel(*_arguments: Any, **_keywords: Any):
        raise AssertionError(f"the legacy {name} decided an in-scope Phase 1 constraint")

    return sentinel


@pytest.mark.parametrize("case_id", IN_SCOPE_IDS)
def test_public_check_consumes_kernel(case_id: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """T10. Phase 3 removed the legacy evaluators; bands remain unchanged."""
    assert not hasattr(checker_module, "_check_mandatory")
    assert not hasattr(checker_module, "_check_frequency")
    monkeypatch.setattr(checker_module, "_vacuity_message", _raising("_vacuity_message"))
    model, population = _load(case_id)
    report = check(model, population)
    assert band(report) == EXPECTED[case_id]["band"]
    assert report.counts() == EXPECTED[case_id]["counts"]


@pytest.mark.parametrize("case_id", IN_SCOPE_IDS)
def test_public_payload_parity(case_id: str) -> None:
    """T11. The N8 fields on the wire are the projection's, values and order."""
    payload = _public(case_id)
    answer = EXPECTED[case_id]
    assert payload["exit_code"] == answer["band"]
    assert payload["acceptance_ready"] == answer["acceptance_ready"]
    assert payload["counts"] == answer["counts"]
    assert payload["coverage"] == {
        fact_type_id: {"declared": declared, "facts": facts}
        for fact_type_id, declared, facts in answer["coverage"]
    }
    assert [row["constraint_ref"] for row in payload["verdicts"]] == [
        row["constraint_ref"] for row in answer["verdicts"]
    ]
    assert [row["verdict"] for row in payload["verdicts"]] == [
        row["verdict"] for row in answer["verdicts"]
    ]
    # A14.2: the PUBLIC family spelling reaches the wire, never `textual-refusal`.
    assert [row["constraint_type"] for row in payload["verdicts"]] == [
        row["constraint_type"] for row in answer["verdicts"]
    ]
    # A14.3: today's family-specific witness shapes, byte for byte.
    assert [row["offending_facts"] for row in payload["verdicts"]] == [
        row["witness"] if row["constraint_type"] != "mandatory" else [w[0] for w in row["witness"]]
        for row in answer["verdicts"]
    ]


def test_the_trace_is_absent_when_one_constraint_is_out_of_scope() -> None:
    """A partial trace cannot carry a whole-result claim, so there is none."""
    for case_id in sorted(EXPECTED):
        model, population = _load(case_id)
        report = check(model, population)
        assert (report.phase1_trace is not None) == EXPECTED[case_id]["whole_result_in_scope"], (
            case_id
        )


KERNEL_MUTATIONS = (
    (
        "M06",
        "phase1_decide",
        lambda value: proof_kernel.SliceVerdict(
            value.constraint_ref, value.family, value.modality, "pass", None, ()
        ),
    ),
    ("M07", "_violation", lambda modality: "pass"),
    ("M08", "_mandatory_witness", lambda universe, players: ()),
)


ADAPTER_MUTATIONS = (
    ("M11", "covers", lambda value: _replace(value, covered=not value.covered)),
    (
        "M13",
        "multiplicity",
        lambda value: _replace(
            value, groups=tuple(proof_kernel.SliceGroup(g.key, 1) for g in value.groups)
        ),
    ),
    ("M14", "roster", lambda value: _replace(value, universe=value.universe[:1])),
    (
        "M15",
        "identity",
        lambda value: _replace(value, players=tuple(player.upper() for player in value.players)),
    ),
    ("M16", "bounds", lambda value: _replace(value, minimum=value.maximum, maximum=value.minimum)),
)


def test_m12_witness_order_is_observable_in_the_kernel_and_not_on_the_wire() -> None:
    """M12, discharged where it CAN be discharged, and its gap pinned as data.

    Witness order is a claim N8 makes, and reversing the universe changes the
    witness only when two members are missing at once. No approved corpus case
    has two, so the public path cannot observe this mutation -- A14.5 froze the
    answers, so the gap is recorded rather than closed by inventing a case. The
    ordering claim is therefore discharged against the kernel directly, and the
    absence is asserted so that a later phase adding the case has to delete this
    line on purpose.
    """
    ordered = proof_kernel._mandatory_witness(("a1", "b2"), ())
    assert [list(row) for row in ordered] == [["a1"], ["b2"]]
    reversed_universe = proof_kernel._mandatory_witness(("b2", "a1"), ())
    assert [list(row) for row in reversed_universe] == [["b2"], ["a1"]]
    assert ordered != reversed_universe

    two_missing = [
        case_id
        for case_id in IN_SCOPE_IDS
        for row in EXPECTED[case_id]["verdicts"]
        if row["slice_family"] == "mandatory" and len(row["witness"]) > 1
    ]
    assert two_missing == [], (
        "a corpus case now has two missing members, so M12 belongs in the public "
        "bridge gate above -- move it and delete this control"
    )


def _replace(value: proof_kernel.SliceInput, **changes: Any) -> proof_kernel.SliceInput:
    import dataclasses

    return dataclasses.replace(value, **changes)


def _observable_signature(case_id: str) -> tuple[Any, ...]:
    """Everything a Phase 1 mutation is allowed to be observed by.

    The public payload AND the evidence lane, because Phase 1 deliberately adds
    no wire field (section 8): when the adapter refuses, the seam falls back to
    the legacy evaluator and the WIRE cannot distinguish a refusal from an
    ordinary verdict. That fallback is by design, so the bridge gate observes the
    trace the design created for exactly this purpose. Watching the payload alone
    would have made six mutation rows unfalsifiable, which is how a gate that
    cannot fail gets written.
    """
    model, population = _load(case_id)
    report = check(model, population)
    trace = report.phase1_trace
    payload = build_check_payload(
        band(report),
        str(CORPUS / CASE_BY_ID[case_id]["model"]),
        str(CORPUS / CASE_BY_ID[case_id]["population"]),
        schema_version=5,
        model_digest=DIGEST,
        report=report,
    )
    return (
        payload["exit_code"],
        json.dumps(payload["counts"], sort_keys=True),
        json.dumps(
            [
                [row["constraint_ref"], row["verdict"], row["offending_facts"], row["reason_code"]]
                for row in payload["verdicts"]
            ],
            sort_keys=True,
        ),
        trace is None,
        json.dumps(
            []
            if trace is None
            else [
                [
                    slice_verdict.constraint_ref,
                    slice_verdict.family,
                    slice_verdict.verdict,
                    slice_verdict.reason_code,
                    [list(row) for row in slice_verdict.witness],
                    sorted(value.universe),
                    sorted(value.players),
                    [[list(group.key), group.count] for group in value.groups],
                    [value.minimum, value.maximum],
                    value.covered,
                ]
                for value, slice_verdict in trace.rows
            ],
            sort_keys=True,
        ),
    )


@pytest.mark.parametrize(("identifier", "target", "replacement"), KERNEL_MUTATIONS)
def test_a_kernel_mutation_changes_the_public_result(
    identifier: str, target: str, replacement: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """M06-M10. If the shipped verdict did not move, production is not consuming
    the kernel -- it is running beside it, which r2 A1 refuses by name."""
    before = {case_id: _observable_signature(case_id) for case_id in IN_SCOPE_IDS}
    # BOTH bindings: `checker` and `report` imported these names at import time,
    # so patching only the defining module leaves the consumer holding the
    # original -- which is how three of these rows first passed while changing
    # nothing at all.
    monkeypatch.setattr(proof_kernel, target, replacement, raising=False)
    monkeypatch.setattr(proof_bridge, target, replacement, raising=False)
    monkeypatch.setattr(checker_module, target, replacement, raising=False)
    from gnd.semantic_registry import UnregisteredBranchError

    moved = []
    for case_id in IN_SCOPE_IDS:
        try:
            changed = _observable_signature(case_id) != before[case_id]
        except UnregisteredBranchError:
            # Phase 2's constructor guard rejects a mutant that contradicts
            # its registered outcome. This is an observed internal failure,
            # mapped to CLI 70, not an unchanged successful public result.
            changed = True
        if changed:
            moved.append(case_id)
    assert moved, f"{identifier} left every public result unchanged"


def test_phase3_retired_the_phase1_band_and_public_witness_projection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """M09/M10 no longer own shipped semantics after the Phase 3 handoff."""
    before = {case_id: _public(case_id) for case_id in IN_SCOPE_IDS}
    monkeypatch.setattr(proof_kernel, "_band_of", lambda *_args: 0)
    monkeypatch.setattr(proof_bridge, "public_witness", lambda _row: [])
    after = {case_id: _public(case_id) for case_id in IN_SCOPE_IDS}
    assert after == before


@pytest.mark.parametrize(("identifier", "field", "mutate"), ADAPTER_MUTATIONS)
def test_an_adapter_mutation_changes_the_public_result(
    identifier: str, field: str, mutate: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """M11-M16. Each admitted-value field carries meaning, so a change to it must
    reach the wire. A field the bridge could drop silently is a field the
    correspondence claim does not actually cover."""
    before = {case_id: _observable_signature(case_id) for case_id in IN_SCOPE_IDS}
    original = proof_bridge.adapt_phase1_slice

    def mutated(*arguments: Any, **keywords: Any):
        value = original(*arguments, **keywords)
        return None if value is None else mutate(value)

    monkeypatch.setattr(proof_bridge, "adapt_phase1_slice", mutated)
    monkeypatch.setattr(checker_module, "adapt_phase1_slice", mutated)
    moved = [
        case_id for case_id in IN_SCOPE_IDS if _observable_signature(case_id) != before[case_id]
    ]
    assert moved, f"{identifier} changed {field} and no public result moved"


def test_refusals_are_recorded_with_the_ratified_vocabulary() -> None:
    """Review finding R12: A14.4 ratified the refusal vocabulary and nothing
    read it -- a refused constraint left no trace anywhere, against section
    5.2's 'recorded as refusal-to-certify, never as absence'. The report now
    carries one (ref, reason) row per refused constraint, matched here
    against the answer key's own refusal column for every out-of-scope row.
    C15's evidence-not-current is the runner's to record, not the checker's,
    and is deliberately absent from this ledger."""
    for case_id in sorted(EXPECTED):
        model, population = _load(case_id)
        report = check(model, population)
        expected_rows = [
            (row["constraint_ref"], row["refusal_reason_code"])
            for row in EXPECTED[case_id]["verdicts"]
            if not row["in_scope"] and "refusal_reason_code" in row
        ]
        assert list(report.phase1_refusals) == expected_rows, case_id

