"""Machine-readable check/validate payload assembly (D-10, D-11, D-12).

``--format json`` emits one of two versioned, fixed-shape tagged records on
every exit path that carries a verdict — 0, 1, 2, 3, 4 and 70. Version 3 is the
frozen non-structured shape; version 4 adds the required ``derivations`` key
after a structured model loads. Exit 64 (argparse usage error) deliberately
emits none: the format flag is not known until ``parse_args()`` returns, and a
malformed invocation is a harness error rather than a verdict.

Two invariants make this module worth its existence:

1. **One report, two renderings.** Every field is serialized FROM the same
   :class:`~gnd.checker.CheckReport` and :class:`~gnd.model.ValidationIssue`
   objects the text renderer in :mod:`gnd.cli` consumes — ``counts`` is
   ``report.counts()`` passed through unchanged, never rebuilt. A JSON payload
   that disagreed with the text output would be a worse defect than the silent
   pass this phase exists to close. If the payload ever needs a value the
   ``CheckReport`` does not carry, add it to ``CheckReport``.
2. **Fixed shape within each version.** Every key belonging to the selected
   version is always present with an empty default, rather than changing per
   outcome. ``outcome`` is the exit discriminator; ``schema_version`` selects
   the closed wire variant. This is what makes either field meaningful.

The payload is described by ``src/gnd/report.schema.json`` (Draft 2020-12).
That schema is deliberately vendored-only and lives OUTSIDE ``src/gnd/schema/``
— it is a runtime OUTPUT contract, not an interchange format the
``gnd-orm-core`` skill documents authoring rules for. See
``tests/test_schema_sync.py``'s docstring.

Security note: untrusted fact values (agent output) reach this payload only via
``json.dumps``, which escapes quote, backslash, newline and control characters
correctly (T-01.1-04). ``issues`` is capped by :data:`MAX_POPULATION_ISSUES` so
a systematically malformed 10 MB population cannot produce an unbounded payload
(T-01.1-02) — the same posture as ``MAX_POPULATION_BYTES``/``MAX_YAML_EVENTS``:
bound every untrusted-input-proportional resource.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from importlib.resources import files
from typing import Any, Literal

from pydantic import TypeAdapter

from gnd import transition_kernel
from gnd.assurance import AssuranceBlockV1, semantic_decision_for_band
from gnd.checker import CheckReport
from gnd.model import Model, ValidationIssue, structured_derivation_ids
from gnd.semantic_registry import record_branch

#: Payload key-set version. Phase 4 consumes these keys — bump ONLY on a
#: breaking change to the key set or to a value's meaning (D-12).
#: /2: the Phase 2.1 payload contract, pinned once for the whole phase
#: (PANEL-3) — three changes under one bump: (a) verdicts gained required
#: ``source``/``status`` (R-01); (b) the always-present top-level
#: ``extraction`` key (R-03''/PANEL-3), empty except under ``gnd verify``;
#: (c) the ``command`` enum gained ``verify``. Plans 03/04 write INTO this
#: contract and must NOT bump again.
BASE_PAYLOAD_SCHEMA_VERSION = 3
DERIVATION_PAYLOAD_SCHEMA_VERSION = 4
#: /5, /6 (v5.1 Phase 3, D-P3.1): the model-bound successors of 3 and 4. Every
#: check/verify payload emitted AFTER a model loads names the exact model that
#: produced it. Versions 3 and 4 are frozen and keep forbidding `model_digest`,
#: because a single new version cannot preserve two closed fixed shapes: a v5
#: with an optional `derivations` would destroy the discriminator that makes
#: `schema_version` mean anything (invariant 2 above).
MODEL_BOUND_BASE_PAYLOAD_SCHEMA_VERSION = 5
MODEL_BOUND_DERIVATION_PAYLOAD_SCHEMA_VERSION = 6
PAYLOAD_SCHEMA_VERSION = BASE_PAYLOAD_SCHEMA_VERSION
ReportSchemaVersion = Literal[3, 4, 5, 6, 7, 8, 9, 10, 11, 13]

#: The pairing, as two membership tests rather than four inequalities repeated
#: at every site. `schema_version` selects a POINT on both axes: whether the
#: payload carries derivation obligations, and whether it names its model.
MODEL_BOUND_PAYLOAD_SCHEMA_VERSIONS: frozenset[int] = frozenset(
    {MODEL_BOUND_BASE_PAYLOAD_SCHEMA_VERSION, MODEL_BOUND_DERIVATION_PAYLOAD_SCHEMA_VERSION}
)
DERIVATION_PAYLOAD_SCHEMA_VERSIONS: frozenset[int] = frozenset(
    {DERIVATION_PAYLOAD_SCHEMA_VERSION, MODEL_BOUND_DERIVATION_PAYLOAD_SCHEMA_VERSION}
)

#: Upper bound on the ``issues`` array. A 10 MB agent output with a
#: systematically wrong role name would otherwise produce hundreds of thousands
#: of records and a payload larger than its own input, killing the retry loop's
#: context window. The elision is reported, never silent: ``issues_total``
#: carries the pre-truncation count and ``issues_truncated`` the flag.
MAX_POPULATION_ISSUES = 200

#: Exit code -> the ``outcome`` discriminator. Band 4 is "could not decide",
#: which is precisely the distinction this payload exists to make legible.
_OUTCOMES: dict[int, str] = {
    0: "accepted",
    1: "violated",
    2: "inadequate",
    3: "ill_formed",
    4: "indeterminate",
    70: "internal_error",
}

_EMPTY_COUNTS: dict[str, int] = {
    "pass": 0,
    "fail": 0,
    "warning": 0,
    "unchecked": 0,
    "vacuous": 0,
}


def load_report_schema() -> dict[str, Any]:
    """The Draft 2020-12 schema describing this payload.

    Loaded through ``importlib.resources`` like the model and population
    schemas, so the contract ships with the installed package rather than
    living only in the source tree.
    """
    schema_text = files("gnd").joinpath("report.schema.json").read_text(encoding="utf-8")
    return json.loads(schema_text)


def _error_record(error: BaseException | None) -> dict[str, str] | None:
    if error is None:
        return None
    return {"type": type(error).__name__, "message": str(error)}


def _issue_records(
    issues: list[ValidationIssue] | None,
) -> tuple[list[dict[str, Any]], int, bool]:
    """Serialize issues, capped at :data:`MAX_POPULATION_ISSUES` (T-01.1-02)."""
    records = [issue.model_dump() for issue in issues or []]
    total = len(records)
    truncated = total > MAX_POPULATION_ISSUES
    return records[:MAX_POPULATION_ISSUES], total, truncated


def payload_schema_version(model: Model | None) -> ReportSchemaVersion:
    """Select the FROZEN report variant for this model's derivation class.

    Retained unchanged for the surfaces v5.1 Phase 3 deliberately did not move
    -- `gnd validate`, `gnd check --steps`, and coverage's compatibility arm,
    which must still be able to name what a legacy v3/v4 source should have
    been. Check and verify select through
    :func:`model_bound_payload_schema_version` instead.
    """

    if model is not None and structured_derivation_ids(model):
        return DERIVATION_PAYLOAD_SCHEMA_VERSION
    return BASE_PAYLOAD_SCHEMA_VERSION


def model_bound_payload_schema_version(model: Model) -> ReportSchemaVersion:
    """Select the MODEL-BOUND report variant after successful model load.

    Deliberately separate from :func:`payload_schema_version` rather than a
    widening of it: that function has two other consumers, and moving all of
    them would migrate `validate` and `transition` payloads that r2 R1 never
    named -- a second blast radius for no claim (IF-P3-5). The argument is
    non-optional because there is no model-bound version to select before a
    model exists; a pre-load error stays on version 3 and carries no digest,
    because there is no model identity to claim yet.
    """

    if structured_derivation_ids(model):
        return MODEL_BOUND_DERIVATION_PAYLOAD_SCHEMA_VERSION
    return MODEL_BOUND_BASE_PAYLOAD_SCHEMA_VERSION


def _base_payload(
    command: str,
    exit_code: int,
    model_path: str | None,
    population_path: str | None,
    *,
    schema_version: ReportSchemaVersion,
    model_digest: str | None,
    issues: list[ValidationIssue] | None,
    warnings: list[ValidationIssue] | None,
    error: BaseException | None,
) -> dict[str, Any]:
    # The pairing is enforced HERE, at the one place every payload is built,
    # rather than trusted at each of the nine call sites. A v5 payload without
    # a digest and a v3 payload with one are both refused before serialization:
    # the schema would reject either, and a builder that could construct one is
    # a defect the emitter should not be the first to notice.
    requires_digest = schema_version in MODEL_BOUND_PAYLOAD_SCHEMA_VERSIONS
    if requires_digest and model_digest is None:
        raise ValueError(f"a version {schema_version} payload must name the model that produced it")
    if not requires_digest and schema_version not in {7, 8} and model_digest is not None:
        raise ValueError(f"version {schema_version} is frozen and cannot carry a model digest")
    issue_records, issues_total, issues_truncated = _issue_records(issues)
    payload = {
        "schema_version": schema_version,
        "tool": "gnd",
        "command": command,
        "outcome": _OUTCOMES.get(exit_code, "internal_error"),
        "exit_code": exit_code,
        # D-08: acceptance is claimable at band 0 and nowhere else.
        "acceptance_ready": exit_code == 0,
        "model": model_path,
    }
    # Immediately after `model`, so a reader meets the coordinate and the
    # identity together and the rebaseline delta from v3/v4 is exactly two keys.
    if requires_digest or schema_version in {7, 8}:
        payload["model_digest"] = model_digest
    payload.update(
        {
            "population": population_path,
            "counts": dict(_EMPTY_COUNTS),
            "verdicts": [],
        }
    )
    if schema_version in DERIVATION_PAYLOAD_SCHEMA_VERSIONS:
        payload["derivations"] = []
    elif schema_version in {7, 8}:
        payload["derivations"] = None
    payload.update(
        {
            "coverage": {},
            # PANEL-3 / R-03'': present on EVERY payload — including
            # internal_error at 70 and every validate payload (this builder is
            # shared; a per-command variant record is exactly what invariant 2
            # above argues against). Empty by default; populated only by
            # `gnd verify` (plan 03).
            "extraction": {},
            "issues": issue_records,
            "issues_total": issues_total,
            "issues_truncated": issues_truncated,
            "warnings": [warning.model_dump() for warning in warnings or []],
            "error": _error_record(error),
            # Phase 2: always present, three-valued. null = not a transition run;
            # {evaluated: false} = a walk refused before evaluation; {evaluated:
            # true} = a walk that ran. The key exists on EVERY payload for the same
            # reason `extraction` does -- a consumer must never branch before
            # reading a key -- and the three values exist so "not a walk" and "a
            # walk we refused" are distinguishable without reading exit_code.
            "transition": None,
        }
    )
    return payload


def _plain_containers(value: Any) -> Any:
    """Replace read-only containers with plain ones, touching no scalar.

    Only the CONTAINER changes: keys are copied as they are, never coerced,
    and every leaf -- including a non-finite float -- arrives at
    :func:`emit` exactly as the checker produced it, so the CR-04 guard still
    sees what it was written to catch.
    """

    if isinstance(value, Mapping):
        return {key: _plain_containers(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain_containers(item) for item in value]
    return value


def _serializable_verdicts(verdicts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Make ``offending_facts`` rows serializable without changing what they say.

    A violating fact is READ from the population, which stores rows as
    ``MappingProxyType`` so nothing downstream can mutate the data it is
    judging. That protection is a storage decision and is not part of the
    verdict, but it travelled into the payload, and ``json.dumps`` refuses a
    ``mappingproxy`` with a ``TypeError`` that :func:`emit`'s CR-04 guard --
    deliberately narrow, and about ``ValueError`` -- does not catch. So
    ``--format json`` printed a traceback and NO payload at all on exactly the
    exit path a retry loop most needs one, contradicting D-11 (IF-P3-11).

    Copying the container here rather than dumping the report in pydantic's
    JSON mode is deliberate. JSON mode raises on the same value even earlier,
    before the CR-04 guard can degrade a non-representable float into the
    payload-shaped internal error D-11 promises, and it would additionally
    re-render every other scalar in a verdict -- a change the 638-row report
    rebaseline pins byte for byte. This changes the emitted bytes only where
    they were previously unemittable.
    """

    for verdict in verdicts:
        verdict["offending_facts"] = _plain_containers(verdict["offending_facts"])
    return verdicts


def build_check_payload(
    exit_code: int,
    model_path: str,
    population_path: str,
    *,
    schema_version: ReportSchemaVersion = BASE_PAYLOAD_SCHEMA_VERSION,
    model_digest: str | None = None,
    assurance: AssuranceBlockV1 | None = None,
    structured: bool = False,
    _assurance_surface: str | None = None,
    report: CheckReport | None = None,
    issues: list[ValidationIssue] | None = None,
    warnings: list[ValidationIssue] | None = None,
    error: BaseException | None = None,
) -> dict[str, Any]:
    """Assemble the ``check`` payload from the objects the text path consumes."""
    payload = _base_payload(
        "check",
        exit_code,
        model_path,
        population_path,
        schema_version=schema_version,
        model_digest=model_digest,
        issues=issues,
        warnings=warnings,
        error=error,
    )
    if (
        schema_version not in DERIVATION_PAYLOAD_SCHEMA_VERSIONS
        and schema_version not in {7, 8}
        and report is not None
        and report.derivations
    ):
        record_branch("report:check:n-a:incompatible-schema")
        raise ValueError(f"a v{schema_version} check payload cannot hide derivation obligations")
    if report is not None:
        payload["counts"] = report.counts()
        dumped = report.model_dump()
        payload["verdicts"] = _serializable_verdicts(dumped["verdicts"])
        payload["coverage"] = dumped["coverage"]
        if report.phase1_trace is not None:
            # Retain the inherited Phase 1 observation identities while the
            # stable wire values come from the one Phase 3 projection.
            record_branch("report:check:phase1:counts")
            record_branch("report:check:phase1:verdict-row")
            record_branch("report:check:phase1:coverage")
            record_branch("report:check:phase1:band")
            record_branch("report:check:phase1:acceptance")
        else:
            record_branch("report:check:n-a:counts")
            record_branch("report:check:n-a:verdict-row")
            record_branch("report:check:n-a:coverage")
        if schema_version in DERIVATION_PAYLOAD_SCHEMA_VERSIONS or (
            schema_version in {7, 8} and (structured or report.derivations)
        ):
            payload["derivations"] = []
            for verdict in report.derivations:
                row = verdict.model_dump(mode="json")
                # The address already carries the fact type's identity.
                row.pop("fact_type")
                payload["derivations"].append(row)
                record_branch("report:check:n-a:derivation-row")
    else:
        record_branch("report:check:n-a:envelope-only")
    if schema_version in {7, 8}:
        decision = semantic_decision_for_band(exit_code)
        block = assurance if assurance is not None else AssuranceBlockV1(decision)
        if not isinstance(block, AssuranceBlockV1) or block.semantic_decision != decision:
            raise ValueError("assurance does not describe this report band")
        payload["assurance"] = block.as_dict()
        surface = _assurance_surface or (
            "derivation"
            if structured or (report is not None and report.derivations)
            else "snapshot"
        )
        record_branch(f"report:assurance:{surface}:projected")
        if structured and payload["derivations"] is None:
            payload["derivations"] = []
    elif assurance is not None:
        raise ValueError("legacy report cannot carry assurance")
    return payload


def build_verify_payload(
    exit_code: int,
    model_path: str,
    population_path: str,
    *,
    extraction: Mapping[str, Any],
    schema_version: ReportSchemaVersion = BASE_PAYLOAD_SCHEMA_VERSION,
    model_digest: str | None = None,
    assurance: AssuranceBlockV1 | None = None,
    structured: bool = False,
    report: CheckReport | None = None,
    issues: list[ValidationIssue] | None = None,
    warnings: list[ValidationIssue] | None = None,
    error: BaseException | None = None,
) -> dict[str, Any]:
    """Project a completed or refused verify route from the check payload.

    Keeping this seam outside the CLI makes the authenticated route's payload
    projection directly testable without pretending that sidecar I/O belongs
    in the pure correspondence proof.
    """
    payload = build_check_payload(
        exit_code,
        model_path,
        population_path,
        schema_version=schema_version,
        model_digest=model_digest,
        assurance=assurance,
        structured=structured,
        report=report,
        issues=issues,
        warnings=warnings,
        error=error,
    )
    payload["command"] = "verify"
    payload["extraction"] = dict(extraction)
    return payload


def _serializable_transition_document(report: Any) -> dict[str, Any]:
    """Normalize only witness containers before the existing JSON-mode dump."""
    def verdicts(rows):
        return [
            row.model_copy(update={"offending_facts": _plain_containers(row.offending_facts)})
            for row in rows
        ]

    def snapshot(value):
        return value.model_copy(update={"verdicts": verdicts(value.verdicts)})

    copied = report.model_copy(update={
        "pre_snapshot": snapshot(report.pre_snapshot),
        "pre_snapshot_verdicts": verdicts(report.pre_snapshot_verdicts),
        "steps": [
            step.model_copy(update={
                "verdicts": verdicts(step.verdicts),
                "intermediate": snapshot(step.intermediate),
            })
            for step in report.steps
        ],
        "frame_verdicts": verdicts(report.frame_verdicts),
        "post_snapshot": snapshot(report.post_snapshot),
    })
    dumped = copied.model_dump(mode="json")

    def has_nonfinite(value):
        if isinstance(value, Mapping):
            return any(has_nonfinite(item) for item in value.values())
        if isinstance(value, (list, tuple)):
            return any(has_nonfinite(item) for item in value)
        return isinstance(value, float) and not math.isfinite(value)

    def preserve_nonfinite(original, serialized):
        if not has_nonfinite(original):
            return serialized
        if isinstance(original, Mapping):
            # Use the existing JSON-mode key policy, including collisions;
            # witness keys need not be strings in a directly built report.
            adapter = TypeAdapter(Any)
            original_by_key = {
                next(iter(adapter.dump_python({key: None}, mode="json"))): value
                for key, value in original.items()
            }
            return {
                key: preserve_nonfinite(original_by_key[key], value)
                for key, value in serialized.items()
            }
        if isinstance(original, (list, tuple)):
            return [
                preserve_nonfinite(value, item)
                for value, item in zip(original, serialized, strict=True)
            ]
        if isinstance(original, float) and not math.isfinite(original):
            return original
        return serialized

    def retain(rows, documents):
        for row, document in zip(rows, documents, strict=True):
            document["offending_facts"] = preserve_nonfinite(
                row.offending_facts, document["offending_facts"]
            )

    retain(report.pre_snapshot.verdicts, dumped["pre_snapshot"]["verdicts"])
    retain(report.pre_snapshot_verdicts, dumped["pre_snapshot_verdicts"])
    retain(report.frame_verdicts, dumped["frame_verdicts"])
    retain(report.post_snapshot.verdicts, dumped["post_snapshot"]["verdicts"])
    for step, document in zip(report.steps, dumped["steps"], strict=True):
        retain(step.verdicts, document["verdicts"])
        retain(step.intermediate.verdicts, document["intermediate"]["verdicts"])
    return dumped


def build_transition_payload(
    exit_code: int,
    model_path: str,
    *,
    evaluated: bool,
    schema_version: ReportSchemaVersion = BASE_PAYLOAD_SCHEMA_VERSION,
    model_digest: str | None = None,
    assurance: AssuranceBlockV1 | None = None,
    structured: bool = False,
    supplied_digests: dict[str, Any] | None = None,
    transition_report: Any = None,
    report: CheckReport | None = None,
    issues: list[ValidationIssue] | None = None,
    warnings: list[ValidationIssue] | None = None,
    error: BaseException | None = None,
) -> dict[str, Any]:
    """The ``check`` payload for a TRANSITION run.

    ``population`` is null: a walk has a pre and a post and no single
    population, and putting one of them in a field named for the other would be
    a small lie that a consumer would eventually believe.

    A refused walk still gets a payload -- ``report.schema.json`` promises one on
    every exit path -- carrying ``evaluated: false``, the digests AS SUPPLIED,
    and the rejection in ``issues`` under its ``transition:*`` rule id.
    """
    payload = build_check_payload(
        exit_code,
        model_path,
        None,  # type: ignore[arg-type]
        schema_version=schema_version,
        model_digest=model_digest,
        assurance=assurance,
        structured=structured,
        _assurance_surface="transition",
        report=report,
        issues=issues,
        warnings=warnings,
        error=error,
    )
    projected_evaluated = transition_kernel.report_evaluated(evaluated)
    record_branch(
        "report:transition:n-a:evaluated"
        if projected_evaluated
        else "report:transition:n-a:not-evaluated"
    )
    digests = supplied_digests or {}
    block: dict[str, Any] = {
        "evaluated": projected_evaluated,
        "model_digest": digests.get("model_digest"),
        "operations_digest": digests.get("operations_digest"),
        "pre_digest": digests.get("pre_digest"),
        # Present and NULL when a walk was refused, rather than absent or
        # empty. A consumer reads `evaluated` to know whether these mean
        # anything, and never has to branch on a key's existence -- but an
        # empty array would read as "we looked and found none", which is a
        # different claim from "we did not look".
        "pre_snapshot": None,
        "pre_snapshot_verdicts": None,
        "steps": None,
        "frame_grading": None,
        "frame_verdicts": None,
        "post_snapshot": None,
    }
    has_families = transition_kernel.report_family_presence(
        projected_evaluated, transition_report is not None
    )
    has_steps = transition_kernel.report_steps_present(
        projected_evaluated, transition_report is not None
    )
    if has_families:
        dumped = _serializable_transition_document(transition_report)
        record_branch("report:transition:n-a:families")
        block.update(
            {
                key: dumped[key]
                for key in (
                    "pre_snapshot",
                    "pre_snapshot_verdicts",
                    "frame_grading",
                    "frame_verdicts",
                    "post_snapshot",
                )
            }
        )
        block["steps"] = dumped["steps"] if has_steps else None
    else:
        record_branch("report:transition:n-a:no-families")
        if has_steps:
            block["steps"] = []
    payload["transition"] = block
    return payload


def build_plan_transition_payload(
    exit_code: int,
    model_path: str | None,
    *,
    evaluated: bool,
    model_digest: str | None = None,
    structured: bool = False,
    supplied_digests: dict[str, Any] | None = None,
    transition_report: Any = None,
    computed_post: Mapping[str, Any] | None = None,
    post_snapshot_evaluated: bool = True,
    issues: list[ValidationIssue] | None = None,
    warnings: list[ValidationIssue] | None = None,
    error: BaseException | None = None,
) -> dict[str, Any]:
    """Project the v8 computed-post transition variant."""
    assurance = AssuranceBlockV1(
        semantic_decision_for_band(exit_code),
        uncovered_applicable_scope_ids=(
            "applicability:refusal:n-a:evidence-not-current",
        ),
    )
    record_branch("applicability:refusal:n-a:evidence-not-current")
    payload = build_transition_payload(
        exit_code,
        model_path,  # type: ignore[arg-type]
        evaluated=evaluated,
        schema_version=8,
        model_digest=model_digest,
        assurance=assurance,
        structured=structured,
        supplied_digests=supplied_digests,
        transition_report=transition_report,
        issues=issues,
        warnings=warnings,
        error=error,
    )
    # Keep the coordinate next to the inherited population coordinate without
    # changing any v7 insertion order or bytes.
    ordered: dict[str, Any] = {}
    for key, value in payload.items():
        ordered[key] = value
        if key == "population":
            ordered["post"] = "computed"
    block = ordered["transition"]
    block["frame_status"] = "not-applicable" if evaluated else "not-evaluated"
    block["frame_verdicts"] = None
    block["computed_post"] = None
    if computed_post is not None:
        block["computed_post"] = _plain_containers(computed_post)
    if evaluated and not post_snapshot_evaluated:
        block["post_snapshot"] = None
    return ordered


def build_validate_payload(
    exit_code: int,
    model_path: str,
    *,
    schema_version: ReportSchemaVersion = BASE_PAYLOAD_SCHEMA_VERSION,
    issues: list[ValidationIssue] | None = None,
    warnings: list[ValidationIssue] | None = None,
    error: BaseException | None = None,
) -> dict[str, Any]:
    """Assemble the ``validate`` payload. ``population`` is always ``null``.

    Stays on the frozen variants: r2 R1 named check and verify, and widening
    `validate` would move a payload nobody asked to move (IF-P3-5).
    """
    return _base_payload(
        "validate",
        exit_code,
        model_path,
        None,
        schema_version=schema_version,
        model_digest=None,
        issues=issues,
        warnings=warnings,
        error=error,
    )


class NonJsonValueError(ValueError):
    """A payload carried a value RFC 8259 cannot represent (CR-04).

    Raised instead of emitting it, because ``json.dumps``' default
    ``allow_nan=True`` writes the bare tokens ``NaN`` / ``Infinity`` /
    ``-Infinity``, which are not JSON: ``JSON.parse``, Go ``encoding/json``,
    ``serde_json``, ``jq`` and ``json.loads`` with a strict ``parse_constant``
    all reject them. The D-11/D-12 machine interface would therefore be
    unparseable exactly when the population is hostile — the case Phase 4's
    controller most needs it.

    ``gnd.cli`` catches this and emits a payload-shaped ``internal_error``
    record at exit 70 instead, so D-11's "a payload on every exit path" survives
    the failure. It is deliberately a ``ValueError`` subclass: that is what
    ``json.dumps(allow_nan=False)`` itself raises, so a caller need not know
    which of the two produced it.
    """


def render_json(payload: Mapping[str, Any]) -> str:
    """Return the one RFC-8259 rendering shared by API and CLI callers."""
    try:
        return json.dumps(payload, allow_nan=False)
    except ValueError as error:  # includes json's own "Out of range float value"
        raise NonJsonValueError(
            f"the payload carries a value RFC 8259 cannot represent (NaN/Infinity): {error}"
        ) from error


def emit(payload: dict[str, Any]) -> None:
    """Write one payload as a single JSON document to stdout.

    ``allow_nan=False`` (CR-04): RFC 8259 §6 — "Numeric values that cannot be
    represented … such as Infinity and NaN … are not permitted". Untrusted fact
    values reach ``verdicts[].offending_facts`` verbatim, and a NaN there made
    ``json.dumps`` write the bare token ``NaN``. The loader now rejects
    non-finite values (``population:type-mismatch``), so this is the residual
    guard for the D-05 path where a role's object type has no resolvable
    primitive and no type check ever runs.
    """
    rendered = render_json(payload)
    from gnd.assurance_transport import emit_receipt

    emit_receipt((rendered + "\n").encode("utf-8"))
    print(rendered)


def legacy_report_projection(
    payload: Mapping[str, Any], version: ReportSchemaVersion
) -> dict[str, Any]:
    """Project v7 to a frozen wire shape without authenticating any claims."""
    if payload.get("schema_version") != 7 or version not in (3, 4, 5, 6):
        raise ValueError("compatibility projection requires v7 and a frozen target")
    derived = payload.get("derivations")
    if (derived is not None) != (version in DERIVATION_PAYLOAD_SCHEMA_VERSIONS):
        raise ValueError("legacy target disagrees with the derivation class")
    result = {key: value for key, value in payload.items() if key != "assurance"}
    result["schema_version"] = version
    if version not in DERIVATION_PAYLOAD_SCHEMA_VERSIONS:
        result.pop("derivations", None)
    if version not in MODEL_BOUND_PAYLOAD_SCHEMA_VERSIONS:
        result.pop("model_digest", None)
    elif result.get("model_digest") is None:
        raise ValueError("model-bound legacy target requires admitted model identity")
    return result


class CurrentReportVersion(int):
    """Current model-selected wire plus its legacy class for retained reads.

    This declaration comes from the admitted model, never from report JSON.
    A bare current integer authorizes only that wire; this additional coordinate permits
    exact historical predecessor reads without letting the payload select one.
    """

    def __new__(cls, legacy_version: int, *, current_version: int = 7):
        if legacy_version not in (5, 6):
            raise ValueError("current report declaration requires an admitted model class")
        if current_version not in (7, 9, 10, 11):
            raise ValueError("current report version must be 7, 9, 10, or 11")
        value = int.__new__(cls, current_version)
        value.legacy_version = legacy_version
        return value


def current_payload_schema_version(model: Model) -> CurrentReportVersion:
    from gnd.redaction import RedactionPolicy
    from gnd.terms import uses_temporal

    return CurrentReportVersion(
        model_bound_payload_schema_version(model),
        current_version=11
        if uses_temporal(model)
        else 9
        if RedactionPolicy.from_model(model).active
        else 7,
    )


def requested_check_schema_version(
    model: Model | None,
    *,
    admission: bool,
) -> ReportSchemaVersion:
    """Select the check wire explicitly; admission uses v10 even before load."""
    if admission:
        from gnd.terms import uses_temporal

        if model is not None and uses_temporal(model):
            return 13
        return 10
    if model is None:
        return 7
    return current_payload_schema_version(model)
