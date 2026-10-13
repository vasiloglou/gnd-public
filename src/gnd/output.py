from __future__ import annotations

import json
from typing import Any

from gnd import checking_service as api_module
from gnd import payloads as report_module
from gnd import transition, verbalize
from gnd.checker import CheckReport
from gnd.checker import band as checker_band
from gnd.model import Model, ValidationIssue, derivation_classifications


def _print_issues(issues: list[ValidationIssue]) -> None:
    """Render structured validation issues. Widened from ModelValidationError so
    the population loader's issues (D-04) reach the same renderer rather than
    being flattened into a summary string.

    Capped at ``report.MAX_POPULATION_ISSUES`` (WR-01). That bound used to apply
    only where issues were SERIALIZED, so the JSON payload for a systematically
    malformed 3.1 MB population was a correct 63 KB while this renderer wrote
    32 MB — a 10x amplification of the input, and ~100 MB of stdout at the 10 MB
    file cap. Bound every untrusted-input-proportional resource where it is
    PRODUCED, not only where it is serialized. The elision is reported, never
    silent, exactly as ``issues_truncated`` is in the payload."""
    shown = issues[: report_module.MAX_POPULATION_ISSUES]
    for issue in shown:
        print(f"ERROR at {issue.path}: {issue.message} [{issue.rule_id}]")
    if len(issues) > len(shown):
        print(
            f"... and {len(issues) - len(shown)} further issue(s) elided "
            f"(cap {report_module.MAX_POPULATION_ISSUES}); use --format json for "
            f"the machine-readable payload, which reports issues_total."
        )

def _print_trace(model: Model, model_path: str) -> None:
    """What a transition run WOULD evaluate. Reporting only (D6).

    It exists on `validate` and not on `check` because `check` returns a
    verdict, and a flag meaning "report instead of decide" does not belong on a
    command whose job is to decide. It cannot be dropped for size either: it is
    the only surface that emits `operations_digest`, and a required field no
    command produces is a format defect.
    """
    print("TRACE")
    print(f"  model_digest      {transition.transition_model_identity(model)}")
    print(f"  operations_digest {transition.operations_digest(model.operations)}")

    print("COMPILED OBLIGATIONS")
    print("  Eligible standing subsets: snapshots check these only with --compiled-operations.")
    print("  Step preconditions, dynamic rules and frames still require a walk.")
    any_compiled = False
    for operation in model.operations:
        op_id = str(operation.get("id"))
        for entry in model.compiled_obligations(op_id):
            if not entry.get("subset"):
                continue
            any_compiled = True
            subset = entry["subset"]
            print(
                f"  [{entry['modality']}] {verbalize.path_segment(op_id)}."
                f"{verbalize.path_segment(str(entry['obligation']))} -> "
                f"every {verbalize.path_segment(str(subset['of']))} fact has a "
                f"matching {verbalize.path_segment(str(subset['in']))} fact"
            )
            print(f"      {entry['locator']}")
    if not any_compiled:
        print("  (none)")

    print("RETAINED (transition-only)")
    any_retained = False
    for operation in model.operations:
        op_id = str(operation.get("id"))
        for entry in model.compiled_obligations(op_id):
            reason = entry.get("transition-only")
            if not reason:
                continue
            any_retained = True
            print(
                f"  {verbalize.path_segment(op_id)}."
                f"{verbalize.path_segment(str(entry['obligation']))}: "
                f"transition-only: {verbalize.line_text(str(reason))}"
            )
    if not any_retained:
        print("  (none)")

    print("DERIVATION STABILITY")
    classifications = derivation_classifications(model.model_dump())
    for classification in classifications:
        dependencies = ", ".join(
            verbalize.path_segment(dependency)
            for dependency in classification.asserted_dependencies
        )
        print(
            f"  {verbalize.path_segment(classification.fact_type)}: "
            f"{classification.stability} (dependencies: {dependencies})"
        )
    if not classifications:
        print("  (none)")

    print("FRAME MODALITY BY FACT TYPE")
    # Over EVERY operation, because no walk has been supplied: this is what the
    # model would produce, and a walk narrows it to the fact types it touches.
    grading = transition.frame_modalities(model)
    for fact_type_id in sorted(grading):
        modality, operations = grading[fact_type_id]
        names = ", ".join(verbalize.path_segment(name) for name in operations)
        print(f"  {verbalize.path_segment(fact_type_id)}: {modality} ({names})")
    if not grading:
        print("  (none)")

def _print_projected_text(payload: dict[str, Any]) -> None:
    """Render only the already-projected tree on declaration-bearing routes."""

    from gnd.redaction import render_text_header

    header = render_text_header(payload)
    if header is None:
        raise ValueError("projected text requires redaction metadata")
    print(header)
    transition_block = payload.get("transition")
    if isinstance(transition_block, dict):
        for step in transition_block.get("steps") or []:
            changes = step.get("derived_changes") if isinstance(step, dict) else None
            if not changes:
                continue
            print(
                f"STEP {step.get('index')} ({verbalize.path_segment(str(step.get('operation')))})"
            )
            _print_derived_change_summaries(changes)
    print(report_module.render_json(payload))

def _constraint_verdict_line(verdict: Any, indent: str = "  ") -> str:
    """ONE rendering of a constraint verdict, for every surface that prints one.

    Extracted by the phase-2 refactoring review (protocol section 8, step 5).
    There were two copies here -- the blocking and advisory arms below print the
    same three fields the same way -- and the transition arm was about to add a
    third. Three copies of a line is how a format drifts between the report a
    reader sees for a snapshot check and the one they see for a walk, over the
    same underlying verdict.
    """
    return (
        f"{indent}[{verdict.verdict}] {verbalize.path_segment(verdict.constraint_ref)}: "
        f"{verbalize.line_text(verdict.message)}"
    )

def _derivation_verdict_lines(
    verdict: Any,
    indent: str = "  ",
) -> list[str]:
    """Render one derivation obligation and its ordered findings."""

    lines = [
        (
            f"{indent}[{verdict.verdict}] "
            f"{verbalize.path_segment(verdict.derivation_ref)}: "
            f"{verbalize.line_text(verdict.message)}"
        )
    ]
    lines.extend(
        f"{indent}  [{finding.kind}] {verbalize.line_text(finding.message)}"
        for finding in verdict.findings
    )
    return lines

def _print_report(report: CheckReport) -> None:
    blocking = [
        verdict
        for verdict in report.verdicts
        if verdict.modality == "alethic" and verdict.verdict != "pass"
    ]
    advisory = [
        verdict
        for verdict in report.verdicts
        if verdict.modality == "deontic" and verdict.verdict != "pass"
    ]

    print("BLOCKING (alethic)")
    if blocking:
        for verdict in blocking:
            print(_constraint_verdict_line(verdict))
    else:
        print("  (none)")

    print("ADVISORY (deontic)")
    if advisory:
        for verdict in advisory:
            print(_constraint_verdict_line(verdict))
    else:
        print("  (none)")

    if report.derivations:
        print("DERIVATIONS (alethic)")
        for verdict in report.derivations:
            for line in _derivation_verdict_lines(verdict):
                print(line)

    counts = report.counts()
    print(
        f"pass={counts['pass']} fail={counts['fail']} warning={counts['warning']} "
        f"unchecked={counts['unchecked']} vacuous={counts['vacuous']}"
    )

    if report.coverage:
        print("COVERAGE")
        for fact_type_id, entry in report.coverage.items():
            print(
                f"  {verbalize.path_segment(fact_type_id)}: {entry.declared}, facts={entry.facts}"
            )

def _band(report: CheckReport) -> int:
    """Delegate to :func:`gnd.checker.band` — the ONE owner of the exit-band rule.

    Band 3 returns earlier from the load arms, so it never reaches here. The
    precedence 3 > 1 > 4 > 2 > 0 (D-08) lives in ``checker.band`` so the Phase 2/4
    measurement harness reads the same rule the CLI does — a second copy is how
    exit bands drift apart.
    """
    return checker_band(report)

def _print_transition(
    walk: Any, warnings: list[ValidationIssue], *, computed_post: dict[str, Any] | None = None
) -> None:
    """Text rendering: four families, printed as four sections and never merged.

    A reader who wants one number reads the exit code; a reader who wants to fix
    something needs to know WHICH family found it, because a pre-state defect
    and an undeclared side effect call for entirely different work.
    """
    for warning in warnings:
        print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")

    def render(verdicts: list[Any], indent: str = "  ") -> None:
        for verdict in verdicts:
            where = verbalize.path_segment(verdict.locator)
            print(f"{indent}[{verdict.verdict}] {where}: {verbalize.line_text(verdict.message)}")

    print("PRE-STATE")
    _print_check_verdicts(walk.pre_snapshot)
    render(walk.pre_snapshot_verdicts)
    for step in walk.steps:
        print(f"STEP {step.index} ({verbalize.path_segment(step.operation)})")
        _print_derived_change_summaries(step.derived_changes)
        render(step.verdicts)
        _print_check_verdicts(step.intermediate, label="  intermediate")
    if computed_post is None:
        print("FRAME")
        for grading in walk.frame_grading:
            print(
                f"  {verbalize.path_segment(grading.fact_type)}: {grading.modality} "
                f"({grading.reason}; {', '.join(map(verbalize.path_segment, grading.operations))})"
            )
        render(walk.frame_verdicts)
    else:
        print("COMPUTED POST")
        print(json.dumps(computed_post, allow_nan=False))
        print("FRAME COMPARISON: not applicable -- post is computed")
    print("POST-STATE")
    _print_check_verdicts(walk.post_snapshot)

def _print_derived_change_summaries(changes: Any) -> None:
    for change in changes or []:
        if isinstance(change, dict):
            fact_type = change.get("fact_type")
            added = change.get("added") or []
            removed = change.get("removed") or []
        else:
            fact_type = change.fact_type
            added = change.added
            removed = change.removed
        print(f"DERIVED {verbalize.path_segment(str(fact_type))}: +{len(added)} -{len(removed)}")

def _print_check_verdicts(report: CheckReport, label: str = "  snapshot") -> None:
    for verdict in report.verdicts:
        if verdict.verdict != "pass":
            print(_constraint_verdict_line(verdict, f"{label} "))

def _live_assurance(
    model, populations, result, band, trace, *, steps=None, extraction_route="not-applicable"
):
    from gnd.assurance_transport import prepare_execution

    block, execution = api_module._certify_assurance(
        model,
        populations,
        result,
        band,
        trace,
        steps=steps,
        extraction_route=extraction_route,
    )
    if execution is not None:
        prepare_execution(execution)
    return block

def _print_admission_text(payload: dict[str, Any]) -> None:
    section = payload["admission"]
    for row in section["admitted"]:
        ref = row["fact_ref"]
        print(f"ADMITTED {ref['fact_type']}[{ref['index']}]")
    for row in section["blocked"]:
        ref = row["fact_ref"]
        print(f"BLOCKED {ref['fact_type']}[{ref['index']}]: {', '.join(row['blocked_by'])}")

def _canonical_payload(payload: dict[str, Any]) -> str:
    """One deterministic JSON line. Two runs over one unchanged panel print the
    same bytes, so a recorded review summary is reproduced rather than trusted."""

    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

_print_issues.__module__ = "gnd.cli"
_print_trace.__module__ = "gnd.cli"
_print_projected_text.__module__ = "gnd.cli"
_constraint_verdict_line.__module__ = "gnd.cli"
_derivation_verdict_lines.__module__ = "gnd.cli"
_print_report.__module__ = "gnd.cli"
_band.__module__ = "gnd.cli"
_print_transition.__module__ = "gnd.cli"
_print_derived_change_summaries.__module__ = "gnd.cli"
_print_check_verdicts.__module__ = "gnd.cli"
_live_assurance.__module__ = "gnd.cli"
_print_admission_text.__module__ = "gnd.cli"
_canonical_payload.__module__ = "gnd.cli"
