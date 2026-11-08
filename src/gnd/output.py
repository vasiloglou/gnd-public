from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from itertools import islice
from types import SimpleNamespace
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
    for line in _issue_lines(issues):
        print(line)


def _issue_lines(issues: Sequence[Any], total: int | None = None) -> list[str]:
    """The ``ERROR at`` lines for ``issues`` (objects with path, message and rule_id).

    The one home of the cap and the elision line, shared by the object route
    (``_print_issues``) and the projected-payload route; ``total`` is the
    payload's ``issues_total`` when the rows were already capped upstream.
    """
    shown = issues[: report_module.MAX_POPULATION_ISSUES]
    lines = [f"ERROR at {issue.path}: {issue.message} [{issue.rule_id}]" for issue in shown]
    elided = max(len(issues), total or 0) - len(shown)
    if elided > 0:
        lines.append(
            f"... and {elided} further issue(s) elided "
            f"(cap {report_module.MAX_POPULATION_ISSUES}); use --format json for "
            f"the machine-readable payload, which reports issues_total."
        )
    return lines

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
    """Render only the already-projected tree on declaration-bearing routes.

    The historical entry point (ROF2 D2): it picks the route's printer from the
    payload -- ``verify`` by its command, a walk by its ``post`` (set on every
    transition payload, refusals included), else check/validate -- so no caller
    gets the report as text through it. Each command calls its own printer.
    """

    from gnd.redaction import render_text_header

    if render_text_header(payload) is None:
        raise ValueError("projected text requires redaction metadata")
    if payload.get("command") == "verify":
        _print_projected_verify_text(payload)
    elif payload.get("post") in ("declared", "computed"):
        _print_projected_transition_text(payload)
    else:
        _print_projected_check_text(payload)

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

def _identified_verdict_lines(
    verdict: Any, declared: Mapping[str, tuple[str, str | None, str, str | None]] | None
) -> list[str]:
    """A constraint verdict line, named by its declared address and followed by its remedy.

    ``declared`` maps a positional ref to (address, remedy, message, novelty)
    for ``check --rule-ids``; the message is the version-15 one, which differs
    from the report's for a failing acyclic rule (RC2), and the novelty is
    ``new`` or ``standing`` under ``--baseline`` (RC3). Without it, the line is
    the plain one.
    """
    if declared is None or verdict.constraint_ref not in declared:
        return [_constraint_verdict_line(verdict)]
    address, remedy, message, novelty = declared[verdict.constraint_ref]
    named = verbalize.path_segment(verdict.constraint_ref)
    if address != verdict.constraint_ref:
        named = f"{verbalize.path_segment(address)} ({named})"
    outcome = verdict.verdict if novelty is None else f"{verdict.verdict}, {novelty}"
    line = f"  [{outcome}] {named}: {verbalize.line_text(message)}"
    if remedy is None:
        return [line]
    return [line, f"    remedy: {verbalize.line_text(remedy)}"]


def print_baseline(block: Mapping[str, Any] | None) -> None:
    """The ``--baseline`` summary, with the warning for keys that move when rules are inserted."""
    if block is None:
        return
    print(f"BASELINE {verbalize.line_text(block['population'])}")
    print(
        f"  new={block['new']} standing={block['standing']} resolved={block['resolved']} "
        f"positional_keyed={block['positional_keyed']} undecided={block['undecided']}"
    )
    if block["positional_keyed"]:
        print(
            f"warning: {block['positional_keyed']} baseline keys use positional addresses; "
            "they move if a constraint is inserted above them."
        )


def print_vacuous_acceptance(payload: Mapping[str, Any]) -> None:
    """The ``--allow-vacuous`` closing line, when the option accepted a vacuous rule."""
    vacuous = payload.get("counts", {}).get("vacuous", 0)
    if payload.get("allow_vacuous") and vacuous:
        print(f"vacuous accepted: {vacuous} rules have nothing to judge yet (--allow-vacuous).")


def _rows(value: Any) -> list[Any]:
    """``value`` if it is a list, else no rows: a payload value of any other shape is skipped."""
    return value if isinstance(value, list) else []


def _text(value: Any) -> str:
    """Printable text for a payload value, total and bounded: only scalars are rendered.

    A string is itself; a number is its decimal text (a number past the
    interpreter's digit limit prints a placeholder instead of raising); anything
    else, including a container of any depth, is a placeholder. Never ``str()`` of
    an arbitrary payload value: that is where a deep or hostile value raises.
    """
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    if isinstance(value, (bool, int, float)):
        try:
            return str(value)
        except ValueError:
            return "<number>"
    return "<non-text>"


def _row_views(rows: Any) -> list[SimpleNamespace]:
    """Verdict rows as attribute views, total over any payload value.

    The line formatters read attributes; a payload row is a mapping that may be
    missing keys or carry non-text values (the renderer is total over any
    mapping, design rule 1). Anything that is not a mapping is skipped.
    """
    views = []
    for row in _rows(rows):
        if not isinstance(row, Mapping):
            continue
        findings = [
            SimpleNamespace(kind=_text(f.get("kind")), message=_text(f.get("message")))
            for f in _rows(row.get("findings"))
            if isinstance(f, Mapping)
        ]
        ref = row.get("constraint_ref", "")
        views.append(
            SimpleNamespace(
                verdict=_text(row.get("verdict")),
                modality=_text(row.get("modality")),
                # Kept as supplied when it is a plain key, so a ``declared`` lookup
                # by the caller's own reference still finds its entry.
                # (An integer too long to print becomes the placeholder.)
                constraint_ref=(
                    ref
                    if isinstance(ref, str) or (isinstance(ref, int) and _text(ref) != "<number>")
                    else _text(ref)
                ),
                derivation_ref=_text(row.get("derivation_ref")),
                message=_text(row.get("message")),
                reason_code=_text(row.get("reason_code")),
                findings=findings,
            )
        )
    return views


def _with_reason(lines: list[str], view: SimpleNamespace, show_reason: bool) -> list[str]:
    """Append the row's reason code to its first line when the message does not carry it.

    A projection replaces a message that would show instance detail, and the
    row's ``reason_code`` (a rule identity, never instance detail) is then the
    only place the cause survives; the projected routes show it.
    """
    if show_reason and view.reason_code and view.reason_code not in view.message:
        lines = [f"{lines[0]} [reason: {verbalize.line_text(view.reason_code)}]", *lines[1:]]
    return lines


def render_check_rows(
    payload: Mapping[str, Any],
    declared: Mapping[str, tuple[str, str | None, str, str | None]] | None = None,
    *,
    show_reason: bool = False,
) -> list[str]:
    """The check layout from a payload's rows: the one home of this text.

    Both the plain route (``_print_report``, which adapts its report object into
    rows) and the projected routes (``_projected_check_lines``) render through
    here, so the two layouts cannot drift. It reads ``verdicts``, ``derivations``,
    ``counts`` and ``coverage`` and nothing else, never the unprojected report
    object, and is total over any mapping.
    """
    views = _row_views(payload.get("verdicts"))
    blocking = [v for v in views if v.modality == "alethic" and v.verdict != "pass"]
    advisory = [v for v in views if v.modality == "deontic" and v.verdict != "pass"]
    lines = ["BLOCKING (alethic)"]
    for verdict in blocking:
        lines.extend(_with_reason(_identified_verdict_lines(verdict, declared), verdict, show_reason))
    if not blocking:
        lines.append("  (none)")
    lines.append("ADVISORY (deontic)")
    for verdict in advisory:
        lines.extend(_with_reason(_identified_verdict_lines(verdict, declared), verdict, show_reason))
    if not advisory:
        lines.append("  (none)")
    derivations = _row_views(payload.get("derivations"))
    if derivations:
        lines.append("DERIVATIONS (alethic)")
        for verdict in derivations:
            lines.extend(_with_reason(_derivation_verdict_lines(verdict), verdict, show_reason))
    counts = payload.get("counts")
    counts = counts if isinstance(counts, Mapping) else {}
    count = {key: _text(counts.get(key, 0)) for key in ("pass", "fail", "warning", "unchecked", "vacuous")}
    lines.append(
        f"pass={count['pass']} fail={count['fail']} warning={count['warning']} "
        f"unchecked={count['unchecked']} vacuous={count['vacuous']}"
    )
    coverage = payload.get("coverage")
    if isinstance(coverage, Mapping) and coverage:
        lines.append("COVERAGE")
        for fact_type_id, entry in coverage.items():
            entry = entry if isinstance(entry, Mapping) else {}
            lines.append(
                f"  {verbalize.path_segment(fact_type_id)}: "
                f"{_text(entry.get('declared'))}, facts={_text(entry.get('facts'))}"
            )
    return lines


def _print_report(
    report: CheckReport,
    declared: Mapping[str, tuple[str, str | None, str, str | None]] | None = None,
) -> None:
    rows = {
        "verdicts": [verdict.model_dump() for verdict in report.verdicts],
        "derivations": [verdict.model_dump() for verdict in report.derivations],
        "counts": report.counts(),
        "coverage": {
            fact_type_id: {"declared": entry.declared, "facts": entry.facts}
            for fact_type_id, entry in report.coverage.items()
        },
    }
    print("\n".join(render_check_rows(rows, declared)))


_MAX_COUNT = 10**15


def _projected_preamble(payload: Mapping[str, Any]) -> tuple[list[str], list[str] | None]:
    """The warning lines, and the closing lines when issues or an error end the output.

    Shared by every projected route, in the plain routes' order: warnings;
    issues (capped, with the elision line), which end the output; an error with
    no issues. The second value is ``None`` when the route's body follows.
    """
    lines = []
    for warning in _rows(payload.get("warnings"))[: report_module.MAX_POPULATION_ISSUES]:
        if isinstance(warning, Mapping):
            lines.append(
                f"WARNING at {_text(warning.get('path'))}: {_text(warning.get('message'))} "
                f"[{_text(warning.get('rule_id'))}]"
            )
    # The cap is applied to the read: rows past it are never visited or copied.
    supplied = _rows(payload.get("issues"))
    rows = list(
        islice((row for row in supplied if isinstance(row, Mapping)), report_module.MAX_POPULATION_ISSUES)
    )
    if rows:
        total = payload.get("issues_total")
        # A total that is not a plausible count (not an int, or too long to print) is ignored.
        if not isinstance(total, int) or isinstance(total, bool) or not 0 <= total <= _MAX_COUNT:
            total = 0
        issues = [
            SimpleNamespace(
                path=_text(row.get("path")),
                message=_text(row.get("message")),
                rule_id=_text(row.get("rule_id")),
            )
            for row in rows
        ]
        return lines, _issue_lines(issues, max(len(supplied), total))
    error = payload.get("error")
    if error:
        message = error.get("message") if isinstance(error, Mapping) else error
        prefix = "INTERNAL ERROR" if payload.get("exit_code") == 70 else "ERROR"
        return lines, [f"{prefix}: {_text(message)}"]
    return lines, None


def _projected_check_lines(payload: Mapping[str, Any]) -> list[str]:
    """Text for a check or validate payload that was already projected.

    Reads only the payload (never the unprojected report), so what the projection
    removed cannot come back. Order: the shared preamble; a validate success;
    otherwise the check layout.
    """
    lines, closing = _projected_preamble(payload)
    if closing is not None:
        return lines + closing
    exit_code = payload.get("exit_code")
    if payload.get("command") == "validate":
        if exit_code != 0:
            return [*lines, f"ERROR: validate exited {_text(exit_code)} without a reported cause"]
        return [*lines, f"OK: {_text(payload.get('model'))} is a valid GND ORM model"]
    return lines + render_check_rows(payload, show_reason=True)


def _walk_views(rows: Any) -> list[SimpleNamespace]:
    """Walk verdict rows (pre-state, step, frame) as attribute views, total over any value."""
    return [
        SimpleNamespace(
            verdict=_text(row.get("verdict")),
            locator=_text(row.get("locator")),
            message=_text(row.get("message")),
            reason_code=_text(row.get("reason_code")),
        )
        for row in _rows(rows)
        if isinstance(row, Mapping)
    ]


def _walk_verdict_lines(rows: Any, show_reason: bool) -> list[str]:
    lines = []
    for view in _walk_views(rows):
        line = (
            f"  [{view.verdict}] {verbalize.path_segment(view.locator)}: "
            f"{verbalize.line_text(view.message)}"
        )
        lines.extend(_with_reason([line], view, show_reason))
    return lines


def _snapshot_lines(snapshot: Any, label: str, show_reason: bool) -> list[str]:
    """The non-pass constraint verdicts of one embedded snapshot, ``label`` first."""
    rows = snapshot.get("verdicts") if isinstance(snapshot, Mapping) else None
    lines = []
    for view in _row_views(rows):
        if view.verdict != "pass":
            line = _constraint_verdict_line(view, f"{label} ")
            lines.extend(_with_reason([line], view, show_reason))
    return lines


def _derived_change_lines(changes: Any) -> list[str]:
    lines = []
    for change in _rows(changes):
        if isinstance(change, Mapping):
            added = len(_rows(change.get("added")))
            removed = len(_rows(change.get("removed")))
            lines.append(
                f"DERIVED {verbalize.path_segment(_text(change.get('fact_type')))}: "
                f"+{added} -{removed}"
            )
    return lines


def _json_line(value: Any) -> str:
    """One JSON line, as the plain route prints a computed post; a placeholder if it cannot be."""
    try:
        return json.dumps(value, allow_nan=False)
    except (TypeError, ValueError, RecursionError):
        return "<non-text>"


def render_transition_rows(
    block: Mapping[str, Any], *, post: str | None, show_reason: bool = False
) -> list[str]:
    """The walk layout from a ``transition`` block's rows: the one home of this text.

    Four families, printed as four sections and never merged. Both the plain
    route (``_print_transition``, which adapts its report object into rows) and
    the projected route render through here. ``post == "computed"`` selects the
    computed-post section in place of the frame section. Total over any mapping.
    """
    lines = ["PRE-STATE"]
    lines.extend(_snapshot_lines(block.get("pre_snapshot"), "  snapshot", show_reason))
    lines.extend(_walk_verdict_lines(block.get("pre_snapshot_verdicts"), show_reason))
    for step in _rows(block.get("steps")):
        if not isinstance(step, Mapping):
            continue
        operation = _text(step.get("operation"))
        lines.append(f"STEP {_text(step.get('index'))} ({verbalize.path_segment(operation)})")
        lines.extend(_derived_change_lines(step.get("derived_changes")))
        lines.extend(_walk_verdict_lines(step.get("verdicts"), show_reason))
        lines.extend(_snapshot_lines(step.get("intermediate"), "  intermediate", show_reason))
    if post == "computed":
        lines.append("COMPUTED POST")
        lines.append(_json_line(block.get("computed_post")))
        lines.append("FRAME COMPARISON: not applicable -- post is computed")
    else:
        lines.append("FRAME")
        for grading in _rows(block.get("frame_grading")):
            if not isinstance(grading, Mapping):
                continue
            operations = ", ".join(
                verbalize.path_segment(_text(name)) for name in _rows(grading.get("operations"))
            )
            lines.append(
                f"  {verbalize.path_segment(_text(grading.get('fact_type')))}: "
                f"{_text(grading.get('modality'))} ({_text(grading.get('reason'))}; {operations})"
            )
        lines.extend(_walk_verdict_lines(block.get("frame_verdicts"), show_reason))
    lines.append("POST-STATE")
    lines.extend(_snapshot_lines(block.get("post_snapshot"), "  snapshot", show_reason))
    return lines


def _projected_transition_lines(payload: Mapping[str, Any]) -> list[str]:
    """Text for a projected walk payload: the preamble, then the walk if it was evaluated.

    A walk that was refused before it ran (``evaluated`` false) prints only what
    the plain route prints then: the warnings and the issues or error.
    """
    lines, closing = _projected_preamble(payload)
    if closing is not None:
        return lines + closing
    block = payload.get("transition")
    if isinstance(block, Mapping) and block.get("evaluated") is True:
        post = payload.get("post")
        return lines + render_transition_rows(
            block, post=post if isinstance(post, str) else None, show_reason=True
        )
    return lines


def extraction_line(extraction: Any) -> str:
    """``EXTRACTION: state=<state>[ (<reason>)]``: the one home of verify's extraction line."""
    block = extraction if isinstance(extraction, Mapping) else {}
    reason = _text(block.get("reason"))
    return f"EXTRACTION: state={_text(block.get('state'))}" + (f" ({reason})" if reason else "")


def _projected_verify_lines(payload: Mapping[str, Any]) -> list[str]:
    """Text for a projected verify payload: the preamble, the extraction line, the check layout."""
    lines, closing = _projected_preamble(payload)
    if closing is not None:
        return lines + closing
    return [
        *lines,
        extraction_line(payload.get("extraction")),
        *render_check_rows(payload, show_reason=True),
    ]


def _print_projected_header(payload: Mapping[str, Any]) -> None:
    """The ``REDACTION`` header, printed only when there are declarations to name.

    A payload projected only for temporal terms has none, and a header for a
    policy that does not exist would mislead (plan D2).
    """

    from gnd.redaction import render_text_header

    metadata = payload.get("redaction")
    if isinstance(metadata, Mapping) and metadata.get("declarations"):
        header = render_text_header(payload)
        if header is not None:
            print(header)


def _print_projected_check_text(payload: dict[str, Any]) -> None:
    """``check``/``validate`` text on a declaration-bearing or temporal route."""
    _print_projected_header(payload)
    print("\n".join(_projected_check_lines(payload)))


def _print_projected_transition_text(payload: dict[str, Any]) -> None:
    """Walk text (``check --pre --steps``) on a declaration-bearing or temporal route."""
    _print_projected_header(payload)
    print("\n".join(_projected_transition_lines(payload)))


def _print_projected_verify_text(payload: dict[str, Any]) -> None:
    """``verify`` text on a declaration-bearing route."""
    _print_projected_header(payload)
    print("\n".join(_projected_verify_lines(payload)))

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
    # An adapter: the report object becomes rows and the one walk renderer prints
    # them, so the plain and projected walk layouts cannot drift (ROF2).
    block = walk.model_dump()
    block["computed_post"] = computed_post
    post = "declared" if computed_post is None else "computed"
    print("\n".join(render_transition_rows(block, post=post)))

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
