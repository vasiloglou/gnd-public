"""Cross-validate retained GND verifier bytes and gate exact acceptance."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Annotated, Any, Literal, Self

from jsonschema import Draft202012Validator
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    StringConstraints,
    ValidationError,
    model_serializer,
    model_validator,
)

from gnd import checker
from gnd import input_policy as _rf7_input
from gnd.agents import InvocationResult
from gnd.artifacts import (
    Sha256,
    canonical_json_text,
    reject_json_constant,
    reject_json_duplicate_pairs_result,
)
from gnd.checker import CheckReport
from gnd.exp.session_contract import (
    ConstraintSatisfactionAcceptance,
    DataDrivenContract,
    PatchArtifact,
    SessionCase,
    TestsAcceptance,
    TransitionAcceptance,
    WalkAcceptance,
)
from gnd.exp.tests_runner import TestsAcceptanceFeedback
from gnd.payloads import (
    DERIVATION_PAYLOAD_SCHEMA_VERSIONS,
    MAX_POPULATION_ISSUES,
    PAYLOAD_SCHEMA_VERSION,
    load_report_schema,
)
from gnd.semantic_registry import record_branch

__all__ = [
    "DERIVATION_FEEDBACK_SCHEMA_VERSION",
    "FEEDBACK_SCHEMA_VERSION",
    "LEGACY_FEEDBACK_SCHEMA_VERSION",
    "REDACTION_FEEDBACK_SCHEMA_VERSION",
    "WALK_FLOOR_FEEDBACK_SCHEMA_VERSION",
    "AttemptEvaluation",
    "AttemptFeedback",
    "CaseDecision",
    "CaseEvaluation",
    "CaseFeedback",
    "CaseFeedbackV3",
    "ConstraintAcceptanceFeedback",
    "ConstraintViolationFeedback",
    "CoverageGap",
    "DerivationFeedback",
    "ExactAcceptanceFeedback",
    "ExactOutputFeedback",
    "ExpectedOutputObservation",
    "PopulationIssueFeedback",
    "UncheckedAlethicFeedback",
    "VacuityFindingFeedback",
    "VerifierPayloadError",
    "WalkFloorGap",
    "attach_walk_floor_steps",
    "best_key",
    "build_attempt_feedback",
    "canonical_feedback",
    "case_decision",
    "contract_accepts",
    "derivation_feedback_rows",
    "normalized_verifier_signature",
    "observe_expected_outputs",
    "validate_tests_payload",
    "validate_verifier_payload",
    "walk_floor_gaps",
]

OUTCOME_BY_EXIT = {
    0: "accepted",
    1: "violated",
    2: "inadequate",
    3: "ill_formed",
    4: "indeterminate",
    70: "internal_error",
}
MAX_VERIFIER_PAYLOAD_BYTES = 10 * 1024 * 1024
_REPORT_VALIDATOR = Draft202012Validator(load_report_schema())
LEGACY_FEEDBACK_SCHEMA_VERSION = 1
FEEDBACK_SCHEMA_VERSION = 2
#: v5.0 Phase 3 (r2 A8, D-P3.2): the feedback wire that carries derivation
#: repair rows. Selection is SESSION-WIDE: when ANY case's model selects
#: report schema version 4, the whole attempt document promotes to feedback
#: v3 — one wire version per document, so a mixed contract's v3-model cases
#: ride v3 rows whose required ``derivations`` tuple is simply empty. Every
#: session with no v4 case keeps its schema-v2 bytes and digests untouched.
#: No optional-key middle ground, per the r2 R2 versioning rule.
DERIVATION_FEEDBACK_SCHEMA_VERSION = 3
ASSURANCE_FEEDBACK_SCHEMA_VERSION = 4
TRANSITION_FEEDBACK_SCHEMA_VERSION = 5
REDACTION_FEEDBACK_SCHEMA_VERSION = 6
WALK_FLOOR_FEEDBACK_SCHEMA_VERSION = 7


NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
MachineToken = Annotated[str, StringConstraints(pattern=r"^[a-z][a-z0-9-]{0,127}$")]
MachineIdentifier = Annotated[
    str,
    StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$"),
]
ConstraintReference = Annotated[
    str,
    StringConstraints(
        pattern=(
            r"^[A-Za-z_][A-Za-z0-9_-]*(?:\[[A-Za-z0-9_.:-]+\])?"
            r"(?:\.[A-Za-z_][A-Za-z0-9_-]*"
            r"(?:\[[A-Za-z0-9_.:-]+\])?)*$"
        )
    ),
]
FeedbackDisposition = Literal[
    "accepted",
    "retry",
    "agent-failure",
    "verifier-failure",
    "stagnation",
    "oscillation",
    "budget-exhausted",
]
VerifierExit = Literal[0, 1, 2, 3, 4, 70]
VerifierOutcome = Literal[
    "accepted",
    "violated",
    "inadequate",
    "ill_formed",
    "indeterminate",
    "internal_error",
]


class VerifierPayloadError(Exception):
    """Retained verifier bytes do not support a current evaluation claim."""

    def __init__(self, issues: list[str]):
        self.issues = list(issues)
        super().__init__("verifier payload invalid: " + "; ".join(self.issues))


class VerifierVerdict(BaseModel):
    """Machine-semantic verdict fields retained in immutable evaluations."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    constraint_ref: ConstraintReference
    constraint_type: MachineToken
    modality: Literal["alethic", "deontic"]
    source: Literal[
        "explicit",
        "sample",
        "common-sense",
        "llm-inferred",
        "user-supplied",
        # ORM+ v2's sixth source. Carried verbatim from the constraint, like the
        # five above: this literal is the MODEL's vocabulary, not this schema's,
        # and omitting a member would turn "the model declares an imported
        # constraint" into a payload construction failure. Adding a member is
        # backward compatible in the direction that matters — every document
        # that validated before still validates.
        "imported",
        # IK2's seventh source, carried verbatim for the same reason.
        "induced",
    ]
    status: Literal["proposed", "confirmed"]
    verdict: Literal["pass", "fail", "warning", "unchecked", "vacuous"]
    reason_code: MachineToken | None


class _VerifierFeedbackDetail(BaseModel):
    """Validated payload values projected only into schema-v2 retry feedback."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    constraint_ref: ConstraintReference
    message: str
    offending_facts: tuple[Any, ...]


class DerivationFeedback(BaseModel):
    """Schema-v3 repair row for one derivation finding or refusal.

    One row per FAIL finding (``kind`` set, ``reason_code`` null) or per
    UNCHECKED verdict (``kind`` null, ``reason_code`` set); a pass verdict
    contributes no row. ``witness`` and ``message`` are the checker's own
    published COUNTEREXAMPLE — one missing binding or one offending fact,
    the r1 plan's mandated boundary crossing — and nothing beyond it. Stated
    honestly rather than as "answer-free": for a small extension the missing
    binding IS most of the remedy, which is the transition-checking posture
    the plan chose and r2 R3 recorded ("EXP-008 measures roster
    transcription"); what never crosses is anything the payload did not
    already publish.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    derivation_ref: Annotated[str, StringConstraints(pattern=r"^derivation:\S+$")]
    kind: Literal["derived-extension-incomplete", "derived-extension-unsound"] | None = None
    reason_code: Literal["derivation-not-covered", "derivation-rule-opaque"] | None = None
    message: str
    witness: dict[str, Any] | None = None

    @model_validator(mode="after")
    def _finding_or_refusal(self) -> Self:
        if (self.kind is None) == (self.reason_code is None):
            raise ValueError(
                "a derivation feedback row carries exactly one of kind (a fail "
                "finding) or reason_code (an unchecked refusal)"
            )
        if (self.witness is not None) != (self.kind is not None):
            raise ValueError("a witness accompanies exactly the fail findings")
        return self


def derivation_feedback_rows(
    derivations: Sequence[Mapping[str, Any]],
) -> tuple[DerivationFeedback, ...]:
    """Project a payload's ``derivations[]`` block into schema-v3 repair rows.

    Total over malformed rows: a missing key, a null witness on a finding, or
    a wrong-typed value raises :class:`ValueError` with one message, never a
    raw ``KeyError``/``TypeError`` (standing rule 1 — this function is
    exported, so its callers are not only ``validate_verifier_payload``).
    """

    try:
        return _derivation_feedback_rows(derivations)
    except (KeyError, TypeError, AttributeError, ValidationError) as error:
        raise ValueError(f"derivation rows are not closed repair rows: {error}") from error


def _derivation_feedback_rows(
    derivations: Sequence[Mapping[str, Any]],
) -> tuple[DerivationFeedback, ...]:
    rows: list[DerivationFeedback] = []
    for verdict in derivations:
        if verdict["verdict"] == "fail":
            for finding in verdict["findings"]:
                rows.append(
                    DerivationFeedback(
                        derivation_ref=str(verdict["derivation_ref"]),
                        kind=finding["kind"],
                        reason_code=None,
                        message=str(finding["message"]),
                        witness=dict(finding["witness"]),
                    )
                )
        elif verdict["verdict"] == "unchecked":
            rows.append(
                DerivationFeedback(
                    derivation_ref=str(verdict["derivation_ref"]),
                    kind=None,
                    reason_code=verdict["reason_code"],
                    message=str(verdict["message"]),
                    witness=None,
                )
            )
    return tuple(sorted(rows, key=_canonical_model_key))


class ExtractionFeedback(BaseModel):
    """Extraction state/content identity without paths, reasons, or model prose."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    state: Literal["ran", "skipped", "failed"] | None = None
    population_sha256: Sha256 | None = None
    model_sha256: Sha256 | None = None
    projection_sha256: Sha256 | None = None
    document_sha256: Sha256 | None = None


ExpectedOutputState = Literal["matched", "differs", "absent"]


class ExpectedOutputObservation(BaseModel):
    """What one declared expected output was observed to be for one attempt.

    This is contract-acceptance evidence, not a verifier verdict: it never
    enters counts, verdicts, outcome, or ``acceptance_ready``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    output_id: MachineIdentifier
    expected_sha256: Sha256
    observed_sha256: Sha256 | None = None
    state: ExpectedOutputState

    @model_validator(mode="after")
    def _state_and_observed_digest_agree(self) -> Self:
        if self.state == "absent":
            if self.observed_sha256 is not None:
                raise ValueError("an absent expected output cannot carry an observed digest")
        elif self.observed_sha256 is None:
            raise ValueError("a produced expected output must carry an observed digest")
        elif (self.observed_sha256 == self.expected_sha256) != (self.state == "matched"):
            raise ValueError("expected-output state does not match its digest comparison")
        return self


def observe_expected_outputs(
    case: SessionCase,
    candidate_files: Mapping[str, str],
) -> tuple[ExpectedOutputObservation, ...]:
    """Compare one case's declared expected outputs against staged identity.

    ``candidate_files`` maps candidate-relative path to content digest and is
    the attempt's immutable staged inventory.  No filesystem path is read here:
    re-reading the candidate tree after staging would reopen the very
    time-of-check gap the staging boundary exists to close.
    """

    observations: list[ExpectedOutputObservation] = []
    for declared in case.expected_outputs:
        if declared.comparison != "exact-bytes":  # pragma: no cover - closed literal
            raise ValueError(
                f"expected output {declared.output_id!r} declares unsupported comparison "
                f"{declared.comparison!r}"
            )
        observed = candidate_files.get(declared.candidate_path)
        if observed is None:
            state: ExpectedOutputState = "absent"
        elif observed == declared.sha256:
            state = "matched"
        else:
            state = "differs"
        observations.append(
            ExpectedOutputObservation(
                output_id=declared.output_id,
                expected_sha256=declared.sha256,
                observed_sha256=observed,
                state=state,
            )
        )
    return tuple(observations)


class CaseEvaluation(BaseModel):
    """A schema-valid verifier result bound to one current candidate and contract."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    payload_valid: bool
    case_id: str = Field(min_length=1)
    role: Literal["required", "diagnostic"]
    candidate_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    contract_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    raw_payload_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    command: Literal["check", "verify", "transition"] = "check"
    process_exit: VerifierExit
    payload_exit: VerifierExit
    outcome: VerifierOutcome
    acceptance_ready: bool
    counts: dict[str, int]
    coverage: dict[str, Any]
    verdicts: tuple[VerifierVerdict, ...] = ()
    issues: tuple[dict[str, Any], ...] = ()
    issues_total: int = Field(default=0, ge=0)
    issues_truncated: bool = False
    extraction: ExtractionFeedback = Field(default_factory=ExtractionFeedback)
    # The empty default is deliberate and fail-closed: acceptance compares this
    # tuple against the contract's declared outputs, so a result carrying none
    # cannot satisfy a case that declares at least one.
    expected_outputs: tuple[ExpectedOutputObservation, ...] = ()
    alethic_failure_count: int = Field(ge=0)
    alethic_indeterminate_count: int = Field(ge=0)
    validation_errors: tuple[str, ...] = ()
    _judgment_report: Any = PrivateAttr(default=None)
    _judgment_files: Any = PrivateAttr(default=None)
    _admission_metrics: dict[str, int] | None = PrivateAttr(default=None)
    _verdict_feedback: tuple[_VerifierFeedbackDetail, ...] = PrivateAttr(default=())
    # v5.0 Phase 3: derivation repair rows ride a PrivateAttr like the verdict
    # details above, so the serialized evaluation — whose canonical digest is
    # retained evidence — keeps its exact pre-phase bytes for every session.
    _derivation_feedback: tuple[DerivationFeedback, ...] = PrivateAttr(default=())
    _assurance_execution: Any = PrivateAttr(default=None)
    _assurance_receipt: Any = PrivateAttr(default=None)
    _assurance_binding: tuple[str, str, str, str, int] | None = PrivateAttr(default=None)
    _transition_steps: tuple[TransitionStepFeedback, ...] = PrivateAttr(default=())
    # Candidate step bindings are needed to grade walk floors, but are never
    # evidence-wire data.  ``None`` is distinct from an observed empty walk so
    # a missing immutable-snapshot observation cannot accidentally discharge a
    # forbidden-only declaration.
    _walk_floor_steps: tuple[dict[str, Any], ...] | None = PrivateAttr(default=None)
    _tests_feedback: TestsAcceptanceFeedback | None = PrivateAttr(default=None)

    @property
    def verdict_feedback(self) -> tuple[_VerifierFeedbackDetail, ...]:
        return self._verdict_feedback

    @property
    def derivation_feedback(self) -> tuple[DerivationFeedback, ...]:
        return self._derivation_feedback

    @property
    def transition_steps(self) -> tuple[TransitionStepFeedback, ...]:
        return self._transition_steps


def attach_walk_floor_steps(
    result: CaseEvaluation,
    submitted_steps: Sequence[Mapping[str, Any]],
) -> CaseEvaluation:
    """Attach an immutable private observation of candidate transition steps.

    The public ``CaseEvaluation`` model and its serialized bytes stay frozen.
    Only the operation and bindings needed by the floor matcher are copied;
    callers cannot mutate the retained observation through their source
    objects after validation.
    """

    observed: list[dict[str, Any]] = []
    for index, step in enumerate(submitted_steps):
        if not isinstance(step, Mapping):
            raise TypeError(f"submitted steps[{index}] must be an object")
        operation = step.get("op")
        bindings = step.get("bindings")
        if not isinstance(operation, str) or not operation:
            raise ValueError(f"submitted steps[{index}].op must be a nonempty string")
        if not isinstance(bindings, Mapping):
            raise TypeError(f"submitted steps[{index}].bindings must be an object")
        observed.append({"op": operation, "bindings": dict(bindings)})
    attached = result.model_copy(deep=True)
    attached.__pydantic_private__["_walk_floor_steps"] = tuple(observed)
    return attached


class AttemptEvaluation(BaseModel):
    """All verifier results attributed to one immutable attempt."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    attempt_index: int = Field(gt=0)
    candidate_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    contract_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    results: tuple[CaseEvaluation, ...]

    @model_validator(mode="after")
    def _case_ids_are_unique(self) -> AttemptEvaluation:
        ids = [result.case_id for result in self.results]
        duplicates = sorted({case_id for case_id in ids if ids.count(case_id) > 1})
        if duplicates:
            raise ValueError(f"duplicate case result(s): {', '.join(duplicates)}")
        return self


class CoverageGap(BaseModel):
    """One contract floor not met by checker-reported population counts."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    fact_type: MachineIdentifier
    required: int = Field(ge=1)
    observed: int = Field(ge=0)
    checker_declared: bool


class WalkFloorGap(BaseModel):
    """Answer-free identity of one unmet transition-walk floor."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: Literal["required-op-missing", "forbidden-op-present"]
    operation_id: MachineIdentifier


def _walk_scalar_key(value: Any) -> tuple[str, Any]:
    """Return type-aware canonical identity for one admitted JSON scalar."""

    if isinstance(value, bool):
        kind = "boolean"
    elif isinstance(value, (int, float)):
        kind = "number"
    elif isinstance(value, str):
        kind = "string"
    else:
        raise TypeError("walk-floor bindings must be JSON string/number/boolean scalars")
    try:
        encoded = canonical_json_text(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"walk-floor binding is not a finite JSON scalar: {error}") from error
    return kind, value if kind == "number" else encoded


def walk_floor_gaps(
    declaration: WalkAcceptance,
    submitted_steps: Sequence[Mapping[str, Any]],
) -> tuple[WalkFloorGap, ...]:
    """Evaluate required/forbidden operation floors over submitted steps.

    One operation and binding-posting index is built for the whole walk.  A
    required subset is discharged only when the same step id survives every
    posting-list intersection; bindings from different steps never pool.
    """

    operation_steps: dict[str, set[int]] = {}
    binding_steps: dict[tuple[str, str, str, Any], set[int]] = {}
    for step_id, step in enumerate(submitted_steps):
        if not isinstance(step, Mapping):
            raise TypeError(f"submitted steps[{step_id}] must be an object")
        operation = step.get("op")
        bindings = step.get("bindings")
        if not isinstance(operation, str) or not operation:
            raise ValueError(f"submitted steps[{step_id}].op must be a nonempty string")
        if not isinstance(bindings, Mapping):
            raise TypeError(f"submitted steps[{step_id}].bindings must be an object")
        operation_steps.setdefault(operation, set()).add(step_id)
        for parameter, value in bindings.items():
            if not isinstance(parameter, str) or not parameter:
                raise ValueError(
                    f"submitted steps[{step_id}].bindings keys must be nonempty strings"
                )
            scalar_kind, scalar_value = _walk_scalar_key(value)
            binding_steps.setdefault((operation, parameter, scalar_kind, scalar_value), set()).add(
                step_id
            )

    gaps: set[tuple[str, str]] = set()
    for required in declaration.required_ops:
        candidates = operation_steps.get(required.op)
        if candidates:
            postings = []
            for parameter, value in required.bindings_subset.items():
                scalar_kind, scalar_value = _walk_scalar_key(value)
                postings.append(
                    binding_steps.get((required.op, parameter, scalar_kind, scalar_value), set())
                )
            if postings:
                smallest, *others = sorted(postings, key=len)
                matched = any(all(step_id in posting for posting in others) for step_id in smallest)
            else:
                matched = True
        else:
            matched = False
        if not matched:
            gaps.add(("required-op-missing", required.op))

    for operation in declaration.forbidden_ops:
        if operation_steps.get(operation):
            gaps.add(("forbidden-op-present", operation))

    return tuple(
        WalkFloorGap(kind=kind, operation_id=operation) for kind, operation in sorted(gaps)
    )


class CaseDecision(BaseModel):
    """One normalized mode-aware decision over validated verifier evidence."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    accepted: bool
    raw_band: VerifierExit
    coverage_gaps: tuple[CoverageGap, ...] = ()
    walk_floor_gaps: tuple[WalkFloorGap, ...] = ()

    @model_serializer(mode="wrap")
    def _serialize_predecessor_shape(self, handler):
        document = handler(self)
        if not self.walk_floor_gaps:
            document.pop("walk_floor_gaps")
        return document

    @model_validator(mode="after")
    def _decision_is_canonical(self) -> Self:
        fact_types = [gap.fact_type for gap in self.coverage_gaps]
        if fact_types != sorted(fact_types) or len(fact_types) != len(set(fact_types)):
            raise ValueError("coverage gaps must be uniquely sorted by fact type")
        walk_keys = [(gap.kind, gap.operation_id) for gap in self.walk_floor_gaps]
        if walk_keys != sorted(walk_keys) or len(walk_keys) != len(set(walk_keys)):
            raise ValueError("walk-floor gaps must be uniquely sorted by kind and operation")
        if self.raw_band != 0 and (self.coverage_gaps or self.walk_floor_gaps):
            raise ValueError("acceptance floors are evaluated only after raw verifier band zero")
        if self.accepted and (self.raw_band != 0 or self.coverage_gaps or self.walk_floor_gaps):
            raise ValueError("an accepted decision requires raw band zero and no acceptance gap")
        return self


class VerdictCounts(BaseModel):
    """Closed verifier tally retained in feedback and recurrence signatures."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    passed: int = Field(alias="pass", ge=0)
    fail: int = Field(ge=0)
    warning: int = Field(ge=0)
    unchecked: int = Field(ge=0)
    vacuous: int = Field(ge=0)


class CoverageFeedback(BaseModel):
    """One sorted, machine-semantic coverage entry."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    fact_type: MachineIdentifier
    declared: Literal["declared", "undeclared"]
    facts: int = Field(ge=0)


class _VerifierVerdictV1(BaseModel):
    """Frozen schema-v1 feedback verdict row."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    constraint_ref: ConstraintReference
    constraint_type: MachineToken
    modality: Literal["alethic", "deontic"]
    source: Literal[
        "explicit",
        "sample",
        "common-sense",
        "llm-inferred",
        "user-supplied",
        # ORM+ v2's sixth source. Carried verbatim from the constraint, like the
        # five above: this literal is the MODEL's vocabulary, not this schema's,
        # and omitting a member would turn "the model declares an imported
        # constraint" into a payload construction failure. Adding a member is
        # backward compatible in the direction that matters — every document
        # that validated before still validates.
        "imported",
        # IK2's seventh source, carried verbatim for the same reason.
        "induced",
    ]
    status: Literal["proposed", "confirmed"]
    verdict: Literal["pass", "fail", "warning", "unchecked", "vacuous"]
    reason_code: MachineToken | None


class _IssueFeedbackV1(BaseModel):
    """Frozen schema-v1 issue identity."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    rule_id: MachineIdentifier
    severity: Literal["error", "warning"]


class _ExpectedOutputFeedbackV1(BaseModel):
    """Frozen schema-v1 answer-bearing expected-output feedback."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    output_id: MachineIdentifier
    expected_sha256: Sha256
    observed_sha256: Sha256 | None
    state: ExpectedOutputState


class _CaseFeedbackV1(BaseModel):
    """Frozen schema-v1 case feedback reader; never widened with v2 fields."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: NonEmptyString
    role: Literal["required", "diagnostic"]
    command: Literal["check", "verify"]
    process_exit: VerifierExit
    payload_exit: VerifierExit
    outcome: VerifierOutcome
    acceptance_ready: bool
    counts: VerdictCounts
    coverage: tuple[CoverageFeedback, ...]
    verdicts: tuple[_VerifierVerdictV1, ...]
    issues: tuple[_IssueFeedbackV1, ...]
    issues_total: int = Field(ge=0)
    issues_truncated: bool
    extraction: ExtractionFeedback
    # Declared order, not sorted: the agent is told which declared output it
    # missed, and the contract's order is the only order it can act on.
    expected_outputs: tuple[_ExpectedOutputFeedbackV1, ...] = ()
    alethic_failure_count: int = Field(ge=0)
    alethic_indeterminate_count: int = Field(ge=0)

    @model_validator(mode="after")
    def _nested_records_are_canonical(self) -> Self:
        coverage_keys = [entry.fact_type for entry in self.coverage]
        if coverage_keys != sorted(coverage_keys) or len(coverage_keys) != len(set(coverage_keys)):
            raise ValueError("feedback coverage entries must be uniquely sorted")
        issue_keys = [(entry.rule_id, entry.severity) for entry in self.issues]
        if issue_keys != sorted(issue_keys):
            raise ValueError("feedback issues must be sorted")
        verdict_keys = [
            (
                entry.constraint_ref,
                entry.constraint_type,
                entry.modality,
                entry.source,
                entry.status,
                entry.verdict,
                entry.reason_code or "",
            )
            for entry in self.verdicts
        ]
        if verdict_keys != sorted(verdict_keys):
            raise ValueError("feedback verdicts must be sorted")
        if self.issues_total < len(self.issues):
            raise ValueError("feedback issues_total cannot be smaller than retained issues")
        output_ids = [entry.output_id for entry in self.expected_outputs]
        if len(output_ids) != len(set(output_ids)):
            raise ValueError("feedback expected outputs must be uniquely identified")
        return self


class ExactOutputFeedback(BaseModel):
    """Answer-free exact-mode status for one declared output."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    output_id: MachineIdentifier
    state: ExpectedOutputState


class ConstraintViolationFeedback(BaseModel):
    """Validated band-1 repair data for one violated constraint."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    constraint_ref: ConstraintReference
    constraint_type: MachineToken
    modality: Literal["alethic", "deontic"]
    reason_code: MachineToken
    message: str
    offending_facts: tuple[Any, ...]


PopulationPath = Annotated[
    str,
    StringConstraints(
        pattern=(
            r"^\$(?:\.[A-Za-z_][A-Za-z0-9_:-]*"
            r"|\[(?:[A-Za-z0-9_.:-]+|[0-9]+)\])*$"
        )
    ),
]


class PopulationIssueFeedback(BaseModel):
    """Validated band-3 population issue with a normalized data coordinate."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    rule_id: MachineIdentifier
    severity: Literal["error", "warning"]
    path: PopulationPath
    message: str


class VacuityFindingFeedback(BaseModel):
    """Validated band-2 vacuity finding."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    constraint_ref: ConstraintReference
    constraint_type: MachineToken
    message: str
    offending_facts: tuple[Any, ...]


class UncheckedAlethicFeedback(BaseModel):
    """Validated band-4 unchecked alethic identity."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    constraint_ref: ConstraintReference
    reason_code: MachineToken


class ExactAcceptanceFeedback(BaseModel):
    """Closed schema-v2 exact-mode feedback branch."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    mode: Literal["exact-bytes"]
    outputs: tuple[ExactOutputFeedback, ...]

    @model_validator(mode="after")
    def _outputs_are_uniquely_sorted(self) -> Self:
        ids = [entry.output_id for entry in self.outputs]
        if ids != sorted(ids) or len(ids) != len(set(ids)):
            raise ValueError("exact feedback outputs must be uniquely sorted")
        return self


class ConstraintAcceptanceFeedback(BaseModel):
    """Closed schema-v2 constraint-mode feedback branch."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    mode: Literal["constraint-satisfaction"]
    violations: tuple[ConstraintViolationFeedback, ...] = ()
    population_issues: tuple[PopulationIssueFeedback, ...] = ()
    vacuity_findings: tuple[VacuityFindingFeedback, ...] = ()
    unchecked_alethic: tuple[UncheckedAlethicFeedback, ...] = ()
    coverage_gaps: tuple[CoverageGap, ...] = ()

    @model_validator(mode="after")
    def _repair_rows_are_canonical(self) -> Self:
        collections = (
            ("violations", self.violations),
            ("population issues", self.population_issues),
            ("vacuity findings", self.vacuity_findings),
            ("unchecked alethic", self.unchecked_alethic),
            ("coverage gaps", self.coverage_gaps),
        )
        for label, rows in collections:
            keys = [_canonical_model_key(row) for row in rows]
            if keys != sorted(keys) or len(keys) != len(set(keys)):
                raise ValueError(f"{label} must be uniquely sorted")
        return self


CaseAcceptanceFeedback = Annotated[
    ExactAcceptanceFeedback | ConstraintAcceptanceFeedback | TestsAcceptanceFeedback,
    Field(discriminator="mode"),
]


class CaseFeedback(BaseModel):
    """Closed schema-v2 current-attempt decision fields for one case."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: NonEmptyString
    role: Literal["required", "diagnostic"]
    command: Literal["check", "verify"]
    process_exit: VerifierExit
    payload_exit: VerifierExit
    outcome: VerifierOutcome
    acceptance_ready: bool
    counts: VerdictCounts
    coverage: tuple[CoverageFeedback, ...]
    issues_total: int = Field(ge=0)
    issues_truncated: bool
    extraction: ExtractionFeedback
    acceptance: CaseAcceptanceFeedback
    alethic_failure_count: int = Field(ge=0)
    alethic_indeterminate_count: int = Field(ge=0)

    @model_validator(mode="after")
    def _nested_records_are_canonical(self) -> Self:
        coverage_keys = [entry.fact_type for entry in self.coverage]
        if coverage_keys != sorted(coverage_keys) or len(coverage_keys) != len(set(coverage_keys)):
            raise ValueError("feedback coverage entries must be uniquely sorted")
        return self


class CaseFeedbackV3(CaseFeedback):
    """Closed schema-v3 case row: schema-v2 fields plus REQUIRED derivations.

    ``derivations`` has no default on purpose: every v3 row carries the key —
    empty for a case whose payload decided all obligations pass — so a v2 row
    can never validate as a v3 row by accident, and the two wire shapes stay
    disjoint (r2 R2's no-optional-key rule).
    """

    derivations: tuple[DerivationFeedback, ...]

    @model_validator(mode="after")
    def _derivation_rows_are_canonical(self) -> Self:
        keys = [_canonical_model_key(row) for row in self.derivations]
        if keys != sorted(keys) or len(keys) != len(set(keys)):
            raise ValueError("derivation feedback rows must be uniquely sorted")
        return self


class AssuranceFeedback(BaseModel):
    """Closed imported wire value; parsing it confers no evidence authority."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal[1]
    semantic_decision: Literal["accept", "refuse", "indeterminate"] | None
    assurance_level: Literal["none", "partial", "proof-backed"]
    scope_digest: Sha256 | None
    semantics_digest: Sha256 | None
    production_roster_digest: Sha256 | None
    proof_digest: Sha256 | None
    toolchain_digest: Sha256 | None
    uncovered_applicable_scope_ids: tuple[str, ...]
    assumptions: tuple[str, ...]

    @model_validator(mode="after")
    def _wire_relations(self) -> Self:
        from gnd.assurance import AssuranceBlockV1

        AssuranceBlockV1(**self.model_dump(exclude={"schema_version"}))
        return self


class CaseFeedbackV4(CaseFeedbackV3):
    assurance: AssuranceFeedback | None


class TransitionStepFeedback(BaseModel):
    """Answer-free outcome for one transition step."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    index: int = Field(gt=0)
    operation_id: MachineIdentifier
    outcome: Literal["accepted", "violated", "inadequate", "indeterminate"]


class TransitionCaseFeedback(BaseModel):
    """Closed schema-v5 case row; no bindings, witnesses, or messages."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: NonEmptyString
    role: Literal["required", "diagnostic"]
    command: Literal["transition"]
    band: VerifierExit
    steps: tuple[TransitionStepFeedback, ...]


class TransitionCaseFeedbackV7(TransitionCaseFeedback):
    """Transition feedback plus answer-free unmet walk-floor identities."""

    unmet_walk_floors: tuple[WalkFloorGap, ...]

    @model_validator(mode="after")
    def _floor_rows_are_unique_and_sorted(self) -> Self:
        keys = [(row.kind, row.operation_id) for row in self.unmet_walk_floors]
        if keys != sorted(keys) or len(keys) != len(set(keys)):
            raise ValueError("unmet walk floors must be uniquely sorted by kind and operation")
        return self


class SessionRedactionDeclaration(BaseModel):
    """One case-scoped declaration carried by answer-free session wires."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: NonEmptyString
    source: Literal["role", "fact-type"]
    fact_type: MachineIdentifier
    roles: tuple[MachineIdentifier, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _roles_are_unique_and_sorted(self) -> Self:
        if self.roles != tuple(sorted(set(self.roles))):
            raise ValueError("redaction roles must be uniquely sorted")
        return self


class SessionRedaction(BaseModel):
    """Required applied-mode marker for session successor wires."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    mode: Literal["applied"]
    declarations: tuple[SessionRedactionDeclaration, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _declarations_are_unique_and_sorted(self) -> Self:
        keys = [(row.case_id, row.fact_type, row.source, row.roles) for row in self.declarations]
        if keys != sorted(set(keys)):
            raise ValueError("session redaction declarations must be uniquely sorted")
        return self


class _AttemptFeedbackV1(BaseModel):
    """Frozen schema-v1 feedback reader."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[LEGACY_FEEDBACK_SCHEMA_VERSION]
    run_id: NonEmptyString
    contract_id: NonEmptyString
    contract_sha256: Sha256
    source_attempt_index: int = Field(gt=0)
    candidate_sha256: Sha256
    case_payload_sha256s: tuple[tuple[NonEmptyString, Sha256], ...]
    normalized_verifier_signature: Sha256
    process_exit: int | None
    payload_exit: tuple[tuple[NonEmptyString, VerifierExit], ...]
    acceptance_ready: bool
    required: tuple[_CaseFeedbackV1, ...]
    diagnostic: tuple[_CaseFeedbackV1, ...]
    disposition: FeedbackDisposition


class _AttemptFeedbackV2(BaseModel):
    """Strict schema-v2 feedback reader."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[FEEDBACK_SCHEMA_VERSION]
    run_id: NonEmptyString
    contract_id: NonEmptyString
    contract_sha256: Sha256
    source_attempt_index: int = Field(gt=0)
    candidate_sha256: Sha256
    case_payload_sha256s: tuple[tuple[NonEmptyString, Sha256], ...]
    normalized_verifier_signature: Sha256
    process_exit: int | None
    payload_exit: tuple[tuple[NonEmptyString, VerifierExit], ...]
    acceptance_ready: bool
    required: tuple[CaseFeedback, ...]
    diagnostic: tuple[CaseFeedback, ...]
    disposition: FeedbackDisposition


class _AttemptFeedbackV3(BaseModel):
    """Strict schema-v3 feedback reader: v2 shape with derivation-bearing rows."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[DERIVATION_FEEDBACK_SCHEMA_VERSION]
    run_id: NonEmptyString
    contract_id: NonEmptyString
    contract_sha256: Sha256
    source_attempt_index: int = Field(gt=0)
    candidate_sha256: Sha256
    case_payload_sha256s: tuple[tuple[NonEmptyString, Sha256], ...]
    normalized_verifier_signature: Sha256
    process_exit: int | None
    payload_exit: tuple[tuple[NonEmptyString, VerifierExit], ...]
    acceptance_ready: bool
    required: tuple[CaseFeedbackV3, ...]
    diagnostic: tuple[CaseFeedbackV3, ...]
    disposition: FeedbackDisposition


class _AttemptFeedbackV4(_AttemptFeedbackV3):
    schema_version: Literal[ASSURANCE_FEEDBACK_SCHEMA_VERSION]
    required: tuple[CaseFeedbackV4, ...]
    diagnostic: tuple[CaseFeedbackV4, ...]


class _AttemptFeedbackV5(BaseModel):
    """Strict transition feedback reader."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[TRANSITION_FEEDBACK_SCHEMA_VERSION]
    run_id: NonEmptyString
    contract_id: NonEmptyString
    contract_sha256: Sha256
    source_attempt_index: int = Field(gt=0)
    candidate_sha256: Sha256
    case_payload_sha256s: tuple[tuple[NonEmptyString, Sha256], ...]
    normalized_verifier_signature: Sha256
    process_exit: int | None
    payload_exit: tuple[tuple[NonEmptyString, VerifierExit], ...]
    acceptance_ready: bool
    required: tuple[CaseFeedbackV4 | TransitionCaseFeedback, ...]
    diagnostic: tuple[CaseFeedbackV4 | TransitionCaseFeedback, ...]
    disposition: FeedbackDisposition

    @model_validator(mode="after")
    def _version_five_is_transition_disjoint(self) -> Self:
        rows = (*self.required, *self.diagnostic)
        # An attempt that produced no candidate (agent-failure) never reaches the
        # verifier and so has no rows at all; any non-empty row set must still
        # carry a transition row.
        if rows and not any(isinstance(row, TransitionCaseFeedback) for row in rows):
            raise ValueError("schema_version 5 requires at least one transition feedback row")
        return self


class _AttemptFeedbackV6(_AttemptFeedbackV5):
    """All current case unions plus required case-scoped redaction metadata."""

    schema_version: Literal[REDACTION_FEEDBACK_SCHEMA_VERSION]
    redaction: SessionRedaction

    @model_validator(mode="after")
    def _version_five_is_transition_disjoint(self) -> Self:
        # v6 is selected by policy, not by acceptance mode. It therefore also
        # admits snapshot-only sessions while retaining v5's case-row union.
        return self


class _AttemptFeedbackV7(BaseModel):
    """Walk-floor feedback with required nullable redaction metadata."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[WALK_FLOOR_FEEDBACK_SCHEMA_VERSION]
    run_id: NonEmptyString
    contract_id: NonEmptyString
    contract_sha256: Sha256
    source_attempt_index: int = Field(gt=0)
    candidate_sha256: Sha256
    case_payload_sha256s: tuple[tuple[NonEmptyString, Sha256], ...]
    normalized_verifier_signature: Sha256
    process_exit: int | None
    payload_exit: tuple[tuple[NonEmptyString, VerifierExit], ...]
    acceptance_ready: bool
    required: tuple[CaseFeedbackV4 | TransitionCaseFeedbackV7, ...]
    diagnostic: tuple[CaseFeedbackV4 | TransitionCaseFeedbackV7, ...]
    disposition: FeedbackDisposition
    redaction: SessionRedaction | None

    @model_validator(mode="after")
    def _version_seven_has_walk_floor_row(self) -> Self:
        rows = (*self.required, *self.diagnostic)
        if rows and not any(isinstance(row, TransitionCaseFeedbackV7) for row in rows):
            raise ValueError("schema_version 7 requires at least one walk-floor feedback row")
        return self


class RepairFinding(VerifierVerdict):
    reason_code: MachineToken | None = None
    owner: Literal["candidate", "reference", "host"]
    allowed_fixes: tuple[
        Literal["add-fact", "replace-fact", "delete-fact", "replace-artifact"], ...
    ] = Field(max_length=4)
    message: str
    offending_facts: tuple[dict[str, Any], ...]


class PatchFeedbackContext(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    base_candidate_sha256: Sha256
    artifacts: tuple[PatchArtifact, ...] = Field(max_length=256)
    allowed_fixes: tuple[
        Literal["add-fact", "replace-fact", "delete-fact", "replace-artifact"], ...
    ] = Field(max_length=4)


class _AttemptFeedbackV8(_AttemptFeedbackV7):
    schema_version: Literal[8]
    required: tuple[dict[str, Any], ...]
    diagnostic: tuple[dict[str, Any], ...]
    audience: Literal["candidate", "operator"]
    candidate_edit_context: dict[str, Any]

    @model_validator(mode="after")
    def _version_seven_has_walk_floor_row(self):
        PatchFeedbackContext.model_validate(self.candidate_edit_context)
        all_ids = []
        for role, rows in (("required", self.required), ("diagnostic", self.diagnostic)):
            for row in rows:
                fields = dict(row)
                findings = fields.pop("constraint_findings", None)
                if not isinstance(findings, list):
                    raise TypeError("constraint findings must be an array")
                for finding in findings:
                    parsed = RepairFinding.model_validate(finding)
                    if len(set(parsed.allowed_fixes)) != len(parsed.allowed_fixes):
                        raise ValueError("duplicate repair fixes")
                reader = (
                    TransitionCaseFeedbackV7
                    if fields.get("command") == "transition"
                    else CaseFeedbackV4
                )
                parsed = reader.model_validate(fields)
                if parsed.role != role:
                    raise ValueError("feedback case role differs")
                all_ids.append(parsed.case_id)
        if len(set(all_ids)) != len(all_ids) or sorted(all_ids) != sorted(
            case_id for case_id, _ in self.case_payload_sha256s
        ):
            raise ValueError("feedback cases and payload bindings differ")
        if sorted(all_ids) != sorted(case_id for case_id, _ in self.payload_exit):
            raise ValueError("feedback cases and payload exits differ")
        return self


class _AttemptFeedbackV9(_AttemptFeedbackV8):
    schema_version: Literal[9]
    judgments: tuple[dict[str, Any], ...]


class AttemptFeedback(BaseModel):
    """Version-dispatched feedback normalized without rewriting its wire shape."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[
        LEGACY_FEEDBACK_SCHEMA_VERSION,
        FEEDBACK_SCHEMA_VERSION,
        DERIVATION_FEEDBACK_SCHEMA_VERSION,
        ASSURANCE_FEEDBACK_SCHEMA_VERSION,
        TRANSITION_FEEDBACK_SCHEMA_VERSION,
        REDACTION_FEEDBACK_SCHEMA_VERSION,
        WALK_FLOOR_FEEDBACK_SCHEMA_VERSION,
        8,
        9,
    ] = FEEDBACK_SCHEMA_VERSION
    run_id: NonEmptyString
    contract_id: NonEmptyString
    contract_sha256: Sha256
    source_attempt_index: int = Field(gt=0)
    candidate_sha256: Sha256
    case_payload_sha256s: tuple[tuple[NonEmptyString, Sha256], ...]
    normalized_verifier_signature: Sha256
    process_exit: int | None
    payload_exit: tuple[tuple[NonEmptyString, VerifierExit], ...]
    acceptance_ready: bool
    required: tuple[
        dict[str, Any]
        | _CaseFeedbackV1
        | CaseFeedbackV4
        | CaseFeedbackV3
        | CaseFeedback
        | TransitionCaseFeedbackV7
        | TransitionCaseFeedback,
        ...,
    ]
    diagnostic: tuple[
        dict[str, Any]
        | _CaseFeedbackV1
        | CaseFeedbackV4
        | CaseFeedbackV3
        | CaseFeedback
        | TransitionCaseFeedbackV7
        | TransitionCaseFeedback,
        ...,
    ]
    disposition: FeedbackDisposition
    redaction: SessionRedaction | None = None
    audience: Literal["candidate", "operator"] | None = None
    candidate_edit_context: dict[str, Any] | None = None
    judgments: tuple[dict[str, Any], ...] = ()

    @classmethod
    def model_validate(cls, obj: Any, *args: Any, **kwargs: Any) -> Self:
        if isinstance(obj, cls):
            return obj
        version = obj.get("schema_version") if isinstance(obj, dict) else None
        if version == LEGACY_FEEDBACK_SCHEMA_VERSION:
            reader: type[
                _AttemptFeedbackV1
                | _AttemptFeedbackV2
                | _AttemptFeedbackV3
                | _AttemptFeedbackV4
                | _AttemptFeedbackV5
                | _AttemptFeedbackV6
                | _AttemptFeedbackV7
            ] = _AttemptFeedbackV1
        elif version == FEEDBACK_SCHEMA_VERSION:
            reader = _AttemptFeedbackV2
        elif version == DERIVATION_FEEDBACK_SCHEMA_VERSION:
            reader = _AttemptFeedbackV3
        elif version == ASSURANCE_FEEDBACK_SCHEMA_VERSION:
            reader = _AttemptFeedbackV4
        elif version == TRANSITION_FEEDBACK_SCHEMA_VERSION:
            reader = _AttemptFeedbackV5
        elif version == REDACTION_FEEDBACK_SCHEMA_VERSION:
            reader = _AttemptFeedbackV6
        elif version == WALK_FLOOR_FEEDBACK_SCHEMA_VERSION:
            reader = _AttemptFeedbackV7
        elif version == 9:
            reader = _AttemptFeedbackV9
        elif version == 8:
            reader = _AttemptFeedbackV8
        else:
            raise ValidationError.from_exception_data(
                cls.__name__,
                [
                    {
                        "type": "literal_error",
                        "loc": ("schema_version",),
                        "input": version,
                        "ctx": {
                            "expected": (
                                f"{LEGACY_FEEDBACK_SCHEMA_VERSION}, "
                                f"{FEEDBACK_SCHEMA_VERSION} or "
                                f"{DERIVATION_FEEDBACK_SCHEMA_VERSION}, "
                                f"{ASSURANCE_FEEDBACK_SCHEMA_VERSION}, "
                                f"{TRANSITION_FEEDBACK_SCHEMA_VERSION}, "
                                f"{REDACTION_FEEDBACK_SCHEMA_VERSION}, or "
                                f"{WALK_FLOOR_FEEDBACK_SCHEMA_VERSION}"
                            )
                        },
                    }
                ],
            )
        parsed = reader.model_validate(obj, *args, **kwargs)
        return super().model_validate(dict(parsed.__dict__))

    @model_serializer(mode="wrap")
    def _serialize_wire_version(self, handler):
        document = handler(self)
        if self.schema_version != 9:
            document.pop("judgments")
        if self.schema_version not in {8, 9}:
            document.pop("audience")
            document.pop("candidate_edit_context")
        if self.schema_version not in {
            REDACTION_FEEDBACK_SCHEMA_VERSION,
            WALK_FLOOR_FEEDBACK_SCHEMA_VERSION,
            8,
            9,
        }:
            document.pop("redaction")
        return document

    @classmethod
    def model_validate_json(
        cls, json_data: str | bytes | bytearray, *args: Any, **kwargs: Any
    ) -> Self:
        """Route JSON through the version dispatcher above.

        ``model_validate_json`` is a SEPARATE pydantic entry point, not a
        decode in front of ``model_validate``, so overriding only the latter
        leaves the dispatcher bypassable by any caller holding bytes — and the
        bypass does not merely lose compatibility, it can ADMIT what dictionary
        dispatch refuses. ``gnd.evolve.models`` pairs every dispatcher with
        this override for the same reason.
        """
        if isinstance(json_data, bytearray):
            json_data = bytes(json_data)
        return cls.model_validate(_rf7_input.loads(json_data), *args, **kwargs)

    @model_validator(mode="after")
    def _ordered_current_case_sets(self) -> Self:
        if self.schema_version in {8, 9}:
            for rows in (self.required, self.diagnostic):
                ids = [r["case_id"] for r in rows]
                if ids != sorted(set(ids)):
                    raise ValueError("v8 case rows must be uniquely sorted")
            return self
        if self.schema_version == REDACTION_FEEDBACK_SCHEMA_VERSION:
            if self.redaction is None:
                raise ValueError("schema_version 6 requires session redaction metadata")
        elif (
            self.schema_version not in {WALK_FLOOR_FEEDBACK_SCHEMA_VERSION, 8, 9}
            and self.redaction is not None
        ):
            raise ValueError("only schema versions 6 and 7 carry redaction metadata")
        payload_ids = [case_id for case_id, _ in self.case_payload_sha256s]
        exit_ids = [case_id for case_id, _ in self.payload_exit]
        required_ids = [entry.case_id for entry in self.required]
        diagnostic_ids = [entry.case_id for entry in self.diagnostic]
        all_ids = required_ids + diagnostic_ids
        for label, ids in (
            ("case payload digests", payload_ids),
            ("payload exits", exit_ids),
            ("required feedback", required_ids),
            ("diagnostic feedback", diagnostic_ids),
        ):
            if ids != sorted(ids) or len(ids) != len(set(ids)):
                raise ValueError(f"{label} must be uniquely sorted by case id")
        if payload_ids != sorted(all_ids) or exit_ids != sorted(all_ids):
            raise ValueError("feedback case digest/exit sets must exactly match case feedback")
        expected_exits = tuple(
            sorted(
                (
                    entry.case_id,
                    entry.band if isinstance(entry, TransitionCaseFeedback) else entry.payload_exit,
                )
                for entry in (*self.required, *self.diagnostic)
            )
        )
        if self.payload_exit != expected_exits:
            raise ValueError("feedback payload exits must match nested case feedback")
        if self.acceptance_ready != (self.disposition == "accepted"):
            raise ValueError("accepted disposition and acceptance_ready must agree")
        return self


def _strict_object(raw: bytes) -> dict[str, Any]:
    if len(raw) > MAX_VERIFIER_PAYLOAD_BYTES:
        raise VerifierPayloadError(
            [
                (
                    f"payload is {len(raw)} bytes, over the "
                    f"{MAX_VERIFIER_PAYLOAD_BYTES}-byte verifier cap"
                )
            ]
        )
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise VerifierPayloadError([f"payload is not UTF-8: {error}"]) from error



    decoder = _rf7_input.JSONDecoder(
        parse_constant=reject_json_constant,
        object_pairs_hook=reject_json_duplicate_pairs_result,
    )
    try:
        payload, end = decoder.raw_decode(text.lstrip())
    except (json.JSONDecodeError, ValueError, RecursionError) as error:
        raise VerifierPayloadError([f"payload is not one strict JSON document: {error}"]) from error
    if text.lstrip()[end:].strip():
        raise VerifierPayloadError(["payload contains trailing bytes after its JSON document"])
    if not isinstance(payload, dict):
        raise VerifierPayloadError(["payload JSON root must be an object"])
    return payload


def _schema_issues(payload: dict[str, Any]) -> list[str]:
    try:
        return [
            f"schema {error.json_path}: {error.message}"
            for error in sorted(
                _REPORT_VALIDATOR.iter_errors(payload), key=lambda item: item.json_path
            )
        ]
    except RecursionError:
        return ["schema: payload nesting exceeds the validation depth"]


def _zero_counts() -> dict[str, int]:
    return {"pass": 0, "fail": 0, "warning": 0, "unchecked": 0, "vacuous": 0}


def _wire_band(*collections: Sequence[Mapping[str, Any]]) -> int:
    rows = [row for collection in collections for row in collection]
    if any(row.get("verdict") == "fail" for row in rows):
        return 1
    if any(row.get("verdict") == "unchecked" and row.get("modality") == "alethic" for row in rows):
        return 4
    if any(row.get("verdict") == "vacuous" for row in rows):
        return 2
    return 0


def validate_transition_payload(
    raw: bytes,
    *,
    case_id: str,
    role: Literal["required", "diagnostic"],
    process_exit: int,
    expected_schema_version: int,
    expected_model: str,
    expected_post: str | None,
    candidate_sha256: str,
    contract_sha256: str,
    evidence_candidate_sha256: str,
    evidence_contract_sha256: str,
    submitted_steps: Mapping[str, Any] | None = None,
) -> CaseEvaluation:
    """Validate one v7/v8 transition report and derive answer-free step rows."""
    payload = _strict_object(raw)
    problems = _schema_issues(payload)
    if payload.get("schema_version") != expected_schema_version:
        problems.append(
            f"schema_version must be current version {expected_schema_version}, "
            f"not {payload.get('schema_version')!r}"
        )
    if (
        expected_schema_version in {9, 11}
        and (payload.get("redaction") or {}).get("mode") != "applied"
    ):
        problems.append("redaction mode must be applied for session verifier evidence")
    if payload.get("tool") != "gnd" or payload.get("command") != "check":
        problems.append("transition verifier must emit a gnd check payload")
    if payload.get("model") != expected_model:
        problems.append("transition verifier model coordinate does not match the contract")
    if payload.get("population") is not None:
        problems.append("transition verifier population coordinate must be null")
    if (payload.get("post") == "computed") != (expected_post is None):
        problems.append("transition report plan/full mode does not match the contract")
    if payload.get("exit_code") != process_exit:
        problems.append("transition process exit does not match payload exit")
    if evidence_candidate_sha256 != candidate_sha256:
        problems.append("candidate evidence digest does not bind the current candidate")
    if evidence_contract_sha256 != contract_sha256:
        problems.append("contract evidence digest does not bind the current contract")
    if problems:
        raise VerifierPayloadError(problems)

    exit_code = payload["exit_code"]
    if payload["outcome"] != OUTCOME_BY_EXIT.get(exit_code):
        problems.append("transition outcome does not match exit code")
    if payload["acceptance_ready"] is not (exit_code == 0):
        problems.append("transition acceptance_ready does not match exit code")
    block = payload["transition"]
    step_rows: list[TransitionStepFeedback] = []
    if block["evaluated"]:
        collections: list[Sequence[Mapping[str, Any]]] = [
            block["pre_snapshot"]["verdicts"],
            block["pre_snapshot"].get("derivations", ()),
            block["pre_snapshot_verdicts"],
        ]
        for step in block["steps"]:
            step_collections = [
                step["verdicts"],
                step["intermediate"]["verdicts"],
                step["intermediate"].get("derivations", ()),
            ]
            step_band = _wire_band(*step_collections)
            step_rows.append(
                TransitionStepFeedback(
                    index=step["index"],
                    operation_id=step["operation"],
                    outcome=OUTCOME_BY_EXIT[step_band],
                )
            )
            collections.extend(step_collections)
        if block["frame_verdicts"] is not None:
            collections.append(block["frame_verdicts"])
        if block["post_snapshot"] is not None:
            collections.extend(
                [
                    block["post_snapshot"]["verdicts"],
                    block["post_snapshot"].get("derivations", ()),
                ]
            )
        computed_band = _wire_band(*collections)
        if computed_band != exit_code:
            problems.append(
                f"transition band {computed_band} does not match payload exit {exit_code}"
            )
    elif exit_code not in {3, 70}:
        problems.append("an unevaluated transition must exit 3 or 70")

    observed_steps: Sequence[Mapping[str, Any]] | None = None
    if submitted_steps is not None:
        candidate_rows = submitted_steps.get("steps")
        if not isinstance(candidate_rows, list):
            problems.append("submitted transition steps must carry a steps array")
        elif any(not isinstance(row, Mapping) for row in candidate_rows):
            problems.append("submitted transition steps must contain only objects")
        else:
            observed_steps = candidate_rows
            if block["evaluated"]:
                candidate_operations = [row.get("op") for row in candidate_rows]
                report_operations = [row["operation"] for row in block["steps"]]
                if candidate_operations != report_operations:
                    problems.append(
                        "submitted step operations do not match the transition report order"
                    )
    if problems:
        raise VerifierPayloadError(problems)

    evaluation = CaseEvaluation(
        payload_valid=True,
        case_id=case_id,
        role=role,
        candidate_sha256=candidate_sha256,
        contract_sha256=contract_sha256,
        raw_payload_sha256=hashlib.sha256(raw).hexdigest(),
        command="transition",
        process_exit=process_exit,
        payload_exit=exit_code,
        outcome=payload["outcome"],
        acceptance_ready=payload["acceptance_ready"],
        counts=_zero_counts(),
        coverage={},
        issues=tuple(payload["issues"]),
        issues_total=payload["issues_total"],
        issues_truncated=payload["issues_truncated"],
        alethic_failure_count=int(exit_code == 1),
        alethic_indeterminate_count=int(exit_code == 4),
    )
    evaluation.__pydantic_private__["_transition_steps"] = tuple(step_rows)
    if observed_steps is not None:
        try:
            evaluation = attach_walk_floor_steps(evaluation, observed_steps)
        except (TypeError, ValueError) as error:
            raise VerifierPayloadError([str(error)]) from error
    return evaluation


def validate_verifier_payload(
    raw: bytes,
    *,
    case_id: str,
    role: Literal["required", "diagnostic"],
    process_exit: int,
    expected_command: Literal["check", "verify"],
    expected_subject: str,
    candidate_sha256: str,
    contract_sha256: str,
    evidence_candidate_sha256: str,
    evidence_contract_sha256: str,
    require_extraction: bool = False,
    expected_model: str | None = None,
    expected_outputs: tuple[ExpectedOutputObservation, ...] = (),
    expected_schema_version: int = PAYLOAD_SCHEMA_VERSION,
) -> CaseEvaluation:
    """Validate exact raw verifier bytes before they may enter acceptance.

    JSON Schema closes shape.  The checks below close the relations that JSON
    Schema cannot express: version currency, process/payload exit identity,
    outcome algebra, recomputed counts and checker band, extraction state, and
    current evidence bindings.

    ``expected_schema_version`` is the report version the case's MODEL selects
    (v5.0 Phase 3, D-P3.4): a v4 payload for a model that declares no
    structured derivation is refused exactly like a v3 payload for one that
    does. The VALIDATION ORDER is deliberate and pinned (standing rule 3): the
    version gate reports first, digest bindings second, reconstruction
    cross-checks third — a wrong-version payload names its version, not a
    digest mismatch.
    """

    payload = _strict_object(raw)
    schema_problems = _schema_issues(payload)
    problems = list(schema_problems)

    if payload.get("schema_version") != expected_schema_version:
        problems.append(
            f"schema_version must be current version {expected_schema_version}, "
            f"not {payload.get('schema_version')!r}"
        )
    if (
        expected_schema_version in {9, 11}
        and (payload.get("redaction") or {}).get("mode") != "applied"
    ):
        problems.append("redaction mode must be applied for session verifier evidence")
    if payload.get("tool") != "gnd":
        problems.append(f"tool must be 'gnd', not {payload.get('tool')!r}")
    if payload.get("command") != expected_command:
        problems.append(
            f"command {payload.get('command')!r} does not match expected {expected_command!r}"
        )
    if payload.get("population") != expected_subject:
        problems.append(
            f"subject {payload.get('population')!r} does not match expected {expected_subject!r}"
        )
    if expected_model is not None and payload.get("model") != expected_model:
        problems.append(
            f"model {payload.get('model')!r} does not match expected {expected_model!r}"
        )
    if payload.get("exit_code") != process_exit:
        problems.append(
            f"process exit {process_exit} does not match payload exit {payload.get('exit_code')!r}"
        )

    # Shape errors stop before any required-field indexing.  The identity
    # checks above still run so a schema-valid field mutation is diagnosed by
    # its semantic name as well as by a conditional-schema side effect.
    if schema_problems:
        raise VerifierPayloadError(problems)

    if payload.get("schema_version") in {7, 9, 11}:
        from gnd.assurance import AssuranceBlockV1, semantic_decision_for_band

        try:
            imported = dict(payload["assurance"])
            imported.pop("schema_version")
            imported["uncovered_applicable_scope_ids"] = tuple(
                imported["uncovered_applicable_scope_ids"]
            )
            imported["assumptions"] = tuple(imported["assumptions"])
            block = AssuranceBlockV1(**imported)
            if block.semantic_decision != semantic_decision_for_band(payload["exit_code"]):
                problems.append("assurance semantic decision does not match the report band")
        except (ValueError, TypeError):
            problems.append("assurance is not a closed canonical wire value")

    expected_outcome = OUTCOME_BY_EXIT.get(payload["exit_code"])
    if expected_outcome is None:
        problems.append(f"payload exit {payload['exit_code']} has no session outcome mapping")
    elif payload["outcome"] != expected_outcome:
        problems.append(
            f"outcome {payload['outcome']!r} does not match exit "
            f"{payload['exit_code']} ({expected_outcome!r})"
        )
    expected_acceptance = payload["exit_code"] == 0
    if payload["acceptance_ready"] is not expected_acceptance:
        problems.append("acceptance_ready does not match the exact verifier exit algebra")

    if evidence_candidate_sha256 != candidate_sha256:
        problems.append("candidate evidence digest does not bind the current candidate")
    if evidence_contract_sha256 != contract_sha256:
        problems.append("contract evidence digest does not bind the current contract")

    # v4 payloads publish only the canonical derivation_ref on the wire; the
    # internal DerivationVerdict still requires fact_type, so it is recovered
    # from the address. Reconstructing WITHOUT the derivations block was the
    # false-fail this parameterization exists to kill (P3-XR-5): counts and
    # band fold derivation verdicts in, so a dropped block cannot agree with a
    # derivation-bearing payload's own numbers.
    derivation_rows = payload.get("derivations") or []
    report: CheckReport | None = None
    try:
        report = CheckReport.model_validate(
            {
                # Public bytes have no producer scope metadata. Tag imported
                # outcomes at this consumer boundary; never guess which
                # snapshot branch produced them from family/outcome alone.
                "verdicts": [
                    {**row, "scope_id": f"composition:verifier-verdict:n-a:{row['verdict']}"}
                    for row in payload["verdicts"]
                ],
                "coverage": payload["coverage"],
                "derivations": [
                    {
                        **row,
                        "fact_type": str(row["derivation_ref"])[len("derivation:") :],
                        "scope_id": "experiment-feedback:verifier-derivation:"
                        f"{row['derivation']}:{row.get('reason_code') or row['verdict']}",
                    }
                    for row in derivation_rows
                ],
            }
        )
    except (ValidationError, KeyError, TypeError) as error:
        # schema already passed; retain a deterministic diagnostic
        problems.append(f"report could not be reconstructed: {error}")
    if report is not None:
        if payload["counts"] != report.counts():
            problems.append("counts do not equal counts recomputed from verdicts")
        if payload["exit_code"] in {0, 1, 2, 4} and checker.band(report) != payload["exit_code"]:
            problems.append(
                f"checker band {checker.band(report)} does not match payload exit "
                f"{payload['exit_code']}"
            )

    for index, verdict in enumerate(payload["verdicts"]):
        has_reason = isinstance(verdict["reason_code"], str) and bool(
            verdict["reason_code"].strip()
        )
        if has_reason != (verdict["verdict"] == "unchecked"):
            problems.append(f"verdicts[{index}].reason_code must be nonempty exactly for unchecked")

    if payload["issues_total"] < len(payload["issues"]):
        problems.append("issues_total cannot be smaller than retained issues")
    if not payload["issues_truncated"] and payload["issues_total"] != len(payload["issues"]):
        problems.append("issues_total must equal retained issues when not truncated")
    if payload["issues_truncated"] and (
        len(payload["issues"]) != MAX_POPULATION_ISSUES
        or payload["issues_total"] <= MAX_POPULATION_ISSUES
    ):
        problems.append(
            "truncated issues must retain the fixed cap and report a larger issues_total"
        )
    for index, issue in enumerate(payload["issues"]):
        if issue["severity"] != "error":
            problems.append(f"issues[{index}] must have error severity")
    for index, warning in enumerate(payload["warnings"]):
        if warning["severity"] != "warning":
            problems.append(f"warnings[{index}] must have warning severity")
    try:
        for fact_type, entry in payload["coverage"].items():
            CoverageFeedback(
                fact_type=fact_type,
                declared=entry["declared"],
                facts=entry["facts"],
            )
        for issue in payload["issues"]:
            _IssueFeedbackV1(rule_id=issue["rule_id"], severity=issue["severity"])
    except ValidationError as error:
        problems.append(f"feedback machine identifiers are not closed: {error}")

    if payload["exit_code"] in {3, 70} and (
        payload["verdicts"] or payload["counts"] != _zero_counts() or payload["coverage"]
    ):
        problems.append("exit 3/70 must not carry checker verdicts, counts, or coverage")
    if payload["exit_code"] in {3, 70} and derivation_rows:
        problems.append("exit 3/70 must not carry derivation obligations")
    # A structured model ALWAYS yields one obligation row per structured fact
    # type, so a structured checker result with an empty derivations block
    # cannot have come from the shipped checker — a forged payload could erase
    # every obligation and ride the zeroed counts to band 0 (adversarial
    # review finding 1). Renamed-but-well-formed refs remain out of reach
    # here by design: this function validates bytes against the contract's
    # expectations and never re-derives the obligation set from the model.
    if (
        getattr(expected_schema_version, "legacy_version", expected_schema_version)
        in DERIVATION_PAYLOAD_SCHEMA_VERSIONS
        and payload["exit_code"] in {0, 1, 2, 4}
        and not derivation_rows
    ):
        problems.append(
            "a structured (v4/v6) checker result must carry at least one derivation obligation"
        )
    if payload["exit_code"] in {0, 1, 2, 4} and (payload["issues"] or payload["error"] is not None):
        problems.append("checker result bands must not carry load issues or internal errors")
    if payload["exit_code"] == 70 and payload["error"] is None:
        problems.append("internal_error exit 70 requires an error object")

    extraction = payload["extraction"]
    if expected_command == "check" and extraction != {}:
        problems.append("check requires an empty extraction channel")
    if require_extraction and (
        not isinstance(extraction, dict) or extraction.get("state") != "ran"
    ):
        problems.append("extraction must have state 'ran' for this verifier case")

    if problems:
        raise VerifierPayloadError(problems)

    verdicts = payload["verdicts"]
    try:
        normalized_verdicts = tuple(
            VerifierVerdict(
                constraint_ref=row["constraint_ref"],
                constraint_type=row["constraint_type"],
                modality=row["modality"],
                source=row["source"],
                status=row["status"],
                verdict=row["verdict"],
                reason_code=row["reason_code"],
            )
            for row in verdicts
        )
    except ValidationError as error:
        raise VerifierPayloadError(
            [f"verdict machine identifiers are not closed: {error}"]
        ) from error
    evaluation = CaseEvaluation(
        payload_valid=True,
        case_id=case_id,
        role=role,
        candidate_sha256=candidate_sha256,
        contract_sha256=contract_sha256,
        raw_payload_sha256=hashlib.sha256(raw).hexdigest(),
        command=payload["command"],
        process_exit=process_exit,
        payload_exit=payload["exit_code"],
        outcome=payload["outcome"],
        acceptance_ready=payload["acceptance_ready"],
        counts=payload["counts"],
        coverage=payload["coverage"],
        verdicts=normalized_verdicts,
        issues=tuple(payload["issues"]),
        issues_total=payload["issues_total"],
        issues_truncated=payload["issues_truncated"],
        extraction=ExtractionFeedback(
            state=extraction.get("state"),
            population_sha256=extraction.get("population_sha256"),
            model_sha256=extraction.get("model_sha256"),
            projection_sha256=extraction.get("projection_sha256"),
            document_sha256=extraction.get("document_sha256"),
        ),
        expected_outputs=expected_outputs,
        alethic_failure_count=sum(
            row["modality"] == "alethic" and row["verdict"] == "fail" for row in verdicts
        ),
        alethic_indeterminate_count=sum(
            row["modality"] == "alethic" and row["verdict"] == "unchecked" for row in verdicts
        ),
        validation_errors=(),
    )
    evaluation.__pydantic_private__["_verdict_feedback"] = tuple(
        _VerifierFeedbackDetail(
            constraint_ref=row["constraint_ref"],
            message=row["message"],
            offending_facts=tuple(row["offending_facts"]),
        )
        for row in verdicts
    )
    try:
        evaluation.__pydantic_private__["_derivation_feedback"] = derivation_feedback_rows(
            derivation_rows
        )
    except (ValidationError, KeyError, TypeError, ValueError) as error:
        raise VerifierPayloadError(
            [f"derivation rows are not closed repair rows: {error}"]
        ) from error
    return evaluation


def _declared_outputs_were_produced(case: SessionCase, result: CaseEvaluation) -> bool:
    """Whether the case's declared expected outputs were all observed matched.

    The declared set is the denominator, so a result carrying no observation,
    too few, or an identity the contract never declared cannot satisfy it.
    """

    declared = {output.output_id: output.sha256 for output in case.expected_outputs}
    observations = result.expected_outputs
    if len(observations) != len(declared):
        return False
    if {entry.output_id for entry in observations} != set(declared):
        return False
    return all(
        entry.state == "matched" and entry.expected_sha256 == declared[entry.output_id]
        for entry in observations
    )


def validate_tests_payload(
    raw: bytes,
    *,
    case_id: str,
    role: str,
    process_exit: int,
    required_tests: tuple[str, ...],
    candidate_sha256: str,
    contract_sha256: str,
) -> CaseEvaluation:
    """Bind one tests-runner row to the current immutable candidate attempt."""

    try:
        feedback = TestsAcceptanceFeedback.model_validate_json(raw)
    except ValidationError as error:
        raise VerifierPayloadError([f"tests feedback is invalid: {error}"]) from error
    if feedback.required != required_tests:
        raise VerifierPayloadError(["tests feedback required ids differ from the contract"])
    accepted = (
        process_exit == 0
        and feedback.reason is None
        and set(feedback.required) <= set(feedback.passing)
    )
    band = 0 if accepted else 70 if process_exit == 70 else 1
    evaluation = CaseEvaluation(
        payload_valid=True,
        case_id=case_id,
        role=role,
        candidate_sha256=candidate_sha256,
        contract_sha256=contract_sha256,
        raw_payload_sha256=hashlib.sha256(raw).hexdigest(),
        command="check",
        process_exit=band,
        payload_exit=band,
        outcome=OUTCOME_BY_EXIT[band],
        acceptance_ready=accepted,
        counts={
            "pass": int(accepted),
            "fail": int(not accepted and band == 1),
            "warning": 0,
            "unchecked": int(band == 70),
            "vacuous": 0,
        },
        coverage={},
        alethic_failure_count=int(band == 1),
        alethic_indeterminate_count=int(band == 70),
    )
    evaluation.__pydantic_private__["_tests_feedback"] = feedback
    return evaluation


def _post_verdict_walk_decision(
    case: SessionCase,
    result: CaseEvaluation,
) -> CaseDecision:
    """Apply walk floors only after the transition verdict is trusted band 0.

    Keeping this as a separate seam makes the normative ordering executable:
    neither a refused walk nor a nonzero transition band can call the floor
    matcher, and a floor can therefore never rescue or replace that verdict.
    """

    if result.payload_exit != 0:  # pragma: no cover - caller invariant
        raise ValueError("walk floors may be evaluated only after transition band zero")
    declaration = getattr(case.acceptance, "walk", None)
    if declaration is None:
        return CaseDecision(accepted=True, raw_band=0)
    if result._walk_floor_steps is None:
        raise ValueError("walk-floor acceptance lacks immutable submitted-step evidence")
    gaps = walk_floor_gaps(declaration, result._walk_floor_steps)
    return CaseDecision(
        accepted=not gaps,
        raw_band=0,
        walk_floor_gaps=gaps,
    )


def case_decision(case: SessionCase, result: CaseEvaluation) -> CaseDecision:
    """Decide one case from its validated checker evidence and acceptance branch.

    ``validate_verifier_payload`` is the checker-oracle boundary: it validates
    payload shape, current evidence bindings, exit algebra, counts, and the
    recomputed checker band before constructing ``CaseEvaluation``.  This
    helper consumes that immutable result and does not inspect candidate files
    or duplicate checker semantics.
    """

    raw_band = result.payload_exit
    trusted_band_zero = (
        result.payload_valid
        and not result.validation_errors
        and result.case_id == case.case_id
        and result.role == case.role.value
        and result.command
        == ("check" if isinstance(case.acceptance, TestsAcceptance) else case.verify.command)
        and result.process_exit == result.payload_exit == 0
        and result.acceptance_ready
        and result.outcome == OUTCOME_BY_EXIT[0]
    )
    if not trusted_band_zero:
        record_branch("experiment-feedback:case:n-a:untrusted")
        return CaseDecision(accepted=False, raw_band=raw_band)

    if isinstance(case.acceptance, TransitionAcceptance):
        return _post_verdict_walk_decision(case, result)

    if isinstance(case.acceptance, TestsAcceptance):
        feedback = result._tests_feedback
        accepted = (
            feedback is not None
            and feedback.required == case.acceptance.required_tests
            and feedback.reason is None
            and set(feedback.required) <= set(feedback.passing)
        )
        return CaseDecision(accepted=accepted, raw_band=raw_band)

    if not isinstance(case.acceptance, ConstraintSatisfactionAcceptance):
        accepted = _declared_outputs_were_produced(case, result)
        record_branch(
            "experiment-feedback:case:exact-bytes:accept"
            if accepted
            else "experiment-feedback:case:exact-bytes:refuse"
        )
        return CaseDecision(accepted=accepted, raw_band=raw_band)

    gaps: list[CoverageGap] = []
    for floor in sorted(case.acceptance.coverage, key=lambda entry: entry.fact_type):
        coverage = result.coverage.get(floor.fact_type)
        observed = 0 if coverage is None else coverage["facts"]
        if observed < floor.min_facts:
            gaps.append(
                CoverageGap(
                    fact_type=floor.fact_type,
                    required=floor.min_facts,
                    observed=observed,
                    checker_declared=(coverage is not None and coverage["declared"] == "declared"),
                )
            )
    record_branch(
        "experiment-feedback:case:constraint-satisfaction:refuse"
        if gaps
        else "experiment-feedback:case:constraint-satisfaction:accept"
    )
    return CaseDecision(
        accepted=not gaps,
        raw_band=raw_band,
        coverage_gaps=tuple(gaps),
    )


def contract_accepts(contract: DataDrivenContract, attempt: AttemptEvaluation) -> bool:
    """Whether every and only required case has one current accepted result."""

    required_cases = contract.required_cases
    if not required_cases:
        record_branch("experiment-feedback:contract:n-a:no-required-cases")
        return False
    by_id = {result.case_id: result for result in attempt.results}
    for case in required_cases:
        result = by_id.get(case.case_id)
        if result is None:
            record_branch("experiment-feedback:contract:n-a:missing-case")
            return False
        if result.candidate_sha256 != attempt.candidate_sha256:
            record_branch("experiment-feedback:contract:n-a:stale-candidate")
            return False
        if result.contract_sha256 != attempt.contract_sha256:
            record_branch("experiment-feedback:contract:n-a:stale-contract")
            return False
        if case.judgment_gate is not None and (
            result._judgment_report is None
            or result._judgment_report["judgment_policy"] is None
            or not result._judgment_report["judgment_policy"]["admission"]
        ):
            return False
        if not case_decision(case, result).accepted:
            record_branch("experiment-feedback:contract:n-a:rejected-case")
            return False
    record_branch("experiment-feedback:contract:n-a:accept")
    return True


def ranking_observations(contract, attempt):
    by_id = {result.case_id: result for result in attempt.results}
    values = []
    for requested in contract.ranking or ():
        observations = []
        for case in contract.required_cases:
            result = by_id.get(case.case_id)
            if (
                result is None
                or not result.payload_valid
                or result.role != "required"
                or result.candidate_sha256 != attempt.candidate_sha256
                or result.contract_sha256 != attempt.contract_sha256
            ):
                break
            decision = case_decision(case, result)
            metric = requested.metric
            if metric == "candidate_admitted_unique":
                if (
                    not isinstance(case.acceptance, ConstraintSatisfactionAcceptance)
                    or result._admission_metrics is None
                ):
                    break
                value = result._admission_metrics[metric]
            elif metric == "accepted_required_cases":
                value = int(decision.accepted)
            elif metric == "alethic_failures":
                value = result.alethic_failure_count
            elif metric == "alethic_indeterminate":
                value = result.alethic_indeterminate_count
            else:
                value = sum(g.required - g.observed for g in decision.coverage_gaps)
            observations.append(value)
        available = len(observations) == len(contract.required_cases)
        value = (
            (
                min(observations)
                if requested.metric == "candidate_admitted_unique"
                else sum(observations)
            )
            if available
            else None
        )
        values.append(
            {
                "metric": requested.metric,
                "direction": requested.direction,
                "available": available,
                "value": value,
            }
        )
    return values


def best_key(
    contract: DataDrivenContract,
    attempt: AttemptEvaluation,
) -> tuple[int, ...]:
    """Return the locked ascending rank from the shared case decision seam."""

    if contract.profile.patch and contract.ranking:
        pairs = tuple(
            item
            for row in ranking_observations(contract, attempt)
            for item in (
                (0, -row["value"] if row["direction"] == "max" else row["value"])
                if row["available"]
                else (1, 0)
            )
        )
        return (*pairs, attempt.attempt_index)
    by_id = {result.case_id: result for result in attempt.results}
    rows: list[tuple[CaseEvaluation, CaseDecision, bool]] = []
    for case in contract.required_cases:
        result = by_id.get(case.case_id)
        if result is None:
            continue
        bound = (
            result.role == "required"
            and result.candidate_sha256 == attempt.candidate_sha256
            and result.contract_sha256 == attempt.contract_sha256
        )
        rows.append((result, case_decision(case, result), bound))

    accepted = sum(bound and decision.accepted for _, decision, bound in rows)
    if all(
        not isinstance(case.acceptance, ConstraintSatisfactionAcceptance)
        for case in contract.required_cases
    ):
        return (
            -accepted,
            sum(result.alethic_failure_count for result, _, _ in rows),
            sum(result.alethic_indeterminate_count for result, _, _ in rows),
            attempt.attempt_index,
        )

    band_counts = {
        band: sum(decision.raw_band == band for _, decision, _ in rows) for band in (3, 1, 4, 2)
    }
    coverage_shortfall = sum(
        gap.required - gap.observed for _, decision, _ in rows for gap in decision.coverage_gaps
    )
    return (
        -accepted,
        band_counts[3],
        band_counts[1],
        band_counts[4],
        band_counts[2],
        coverage_shortfall,
        attempt.attempt_index,
    )


def _canonical_model_key(value: BaseModel) -> str:
    return canonical_json_text(value.model_dump(mode="json", by_alias=True))


def _sorted_untrusted_facts(facts: tuple[Any, ...]) -> tuple[Any, ...]:
    try:
        return tuple(sorted(facts, key=canonical_json_text))
    except (TypeError, ValueError) as error:
        raise ValueError(f"offending facts are not canonical JSON data: {error}") from error


def _normalized_population_path(raw: Any) -> str:
    if not isinstance(raw, str) or not raw:
        raise ValueError("population issue path must be a nonempty string")
    if raw.startswith("/") or "\\" in raw or ".." in raw or "\x00" in raw:
        raise ValueError("population issue path is not a normalized data coordinate")
    candidate = raw if raw.startswith("$") else f"$.{raw}"
    try:
        return PopulationIssueFeedback(
            rule_id="population:path",
            severity="error",
            path=candidate,
            message="path validation",
        ).path
    except ValidationError as error:
        raise ValueError("population issue path is not a normalized data coordinate") from error


def _common_case_feedback(result: CaseEvaluation) -> dict[str, Any]:
    try:
        coverage = tuple(
            CoverageFeedback(
                fact_type=fact_type,
                declared=entry["declared"],
                facts=entry["facts"],
            )
            for fact_type, entry in sorted(result.coverage.items())
        )
        counts = VerdictCounts.model_validate(result.counts)
    except (KeyError, TypeError, ValidationError) as error:
        raise ValueError(
            f"case {result.case_id!r} has noncanonical decision fields: {error}"
        ) from error
    return {
        "case_id": result.case_id,
        "role": result.role,
        "command": result.command,
        "process_exit": result.process_exit,
        "payload_exit": result.payload_exit,
        "outcome": result.outcome,
        "acceptance_ready": result.acceptance_ready,
        "counts": counts,
        "coverage": coverage,
        "issues_total": result.issues_total,
        "issues_truncated": result.issues_truncated,
        "extraction": result.extraction,
        "alethic_failure_count": result.alethic_failure_count,
        "alethic_indeterminate_count": result.alethic_indeterminate_count,
    }


def _case_feedback_v1(result: CaseEvaluation) -> _CaseFeedbackV1:
    common = _common_case_feedback(result)
    try:
        issues = tuple(
            sorted(
                (
                    _IssueFeedbackV1(
                        rule_id=issue["rule_id"],
                        severity=issue["severity"],
                    )
                    for issue in result.issues
                ),
                key=lambda entry: (entry.rule_id, entry.severity),
            )
        )
    except (KeyError, TypeError, ValidationError) as error:
        raise ValueError(
            f"case {result.case_id!r} has noncanonical schema-v1 issues: {error}"
        ) from error
    return _CaseFeedbackV1(
        **common,
        verdicts=tuple(
            _VerifierVerdictV1(
                constraint_ref=entry.constraint_ref,
                constraint_type=entry.constraint_type,
                modality=entry.modality,
                source=entry.source,
                status=entry.status,
                verdict=entry.verdict,
                reason_code=entry.reason_code,
            )
            for entry in sorted(
                result.verdicts,
                key=lambda entry: (
                    entry.constraint_ref,
                    entry.constraint_type,
                    entry.modality,
                    entry.source,
                    entry.status,
                    entry.verdict,
                    entry.reason_code or "",
                ),
            )
        ),
        issues=issues,
        expected_outputs=tuple(
            _ExpectedOutputFeedbackV1(
                output_id=entry.output_id,
                expected_sha256=entry.expected_sha256,
                observed_sha256=entry.observed_sha256,
                state=entry.state,
            )
            for entry in result.expected_outputs
        ),
    )


def _case_feedback_v2(case: SessionCase, result: CaseEvaluation) -> CaseFeedback:
    common = _common_case_feedback(result)
    decision = case_decision(case, result)
    details = {entry.constraint_ref: entry for entry in result.verdict_feedback}
    if set(details) != {entry.constraint_ref for entry in result.verdicts}:
        raise ValueError(f"case {result.case_id!r} lacks validated verifier feedback details")
    if isinstance(case.acceptance, TestsAcceptance):
        if result._tests_feedback is None:
            raise ValueError(f"case {result.case_id!r} lacks retained tests feedback")
        acceptance = result._tests_feedback
    elif isinstance(case.acceptance, ConstraintSatisfactionAcceptance):
        violations = tuple(
            sorted(
                (
                    ConstraintViolationFeedback(
                        constraint_ref=row.constraint_ref,
                        constraint_type=row.constraint_type,
                        modality=row.modality,
                        reason_code=row.reason_code or "violated",
                        message=details[row.constraint_ref].message,
                        offending_facts=_sorted_untrusted_facts(
                            details[row.constraint_ref].offending_facts
                        ),
                    )
                    for row in result.verdicts
                    if result.payload_exit == 1 and row.verdict in {"fail", "warning"}
                ),
                key=_canonical_model_key,
            )
        )
        try:
            population_issues = tuple(
                sorted(
                    (
                        PopulationIssueFeedback(
                            rule_id=issue["rule_id"],
                            severity=issue["severity"],
                            path=_normalized_population_path(issue["path"]),
                            message=issue["message"],
                        )
                        for issue in result.issues
                        if result.payload_exit == 3
                    ),
                    key=_canonical_model_key,
                )
            )
        except (KeyError, TypeError, ValidationError) as error:
            raise ValueError(
                f"case {result.case_id!r} has noncanonical population issues: {error}"
            ) from error
        vacuity_findings = tuple(
            sorted(
                (
                    VacuityFindingFeedback(
                        constraint_ref=row.constraint_ref,
                        constraint_type=row.constraint_type,
                        message=details[row.constraint_ref].message,
                        offending_facts=_sorted_untrusted_facts(
                            details[row.constraint_ref].offending_facts
                        ),
                    )
                    for row in result.verdicts
                    if result.payload_exit == 2 and row.verdict == "vacuous"
                ),
                key=_canonical_model_key,
            )
        )
        unchecked_alethic = tuple(
            sorted(
                (
                    UncheckedAlethicFeedback(
                        constraint_ref=row.constraint_ref,
                        reason_code=row.reason_code or "unchecked",
                    )
                    for row in result.verdicts
                    if result.payload_exit == 4
                    and row.verdict == "unchecked"
                    and row.modality == "alethic"
                ),
                key=_canonical_model_key,
            )
        )
        record_branch("experiment-feedback:projection:constraint-satisfaction:repair-details")
        acceptance: CaseAcceptanceFeedback = ConstraintAcceptanceFeedback(
            mode="constraint-satisfaction",
            violations=violations,
            population_issues=population_issues,
            vacuity_findings=vacuity_findings,
            unchecked_alethic=unchecked_alethic,
            coverage_gaps=tuple(sorted(decision.coverage_gaps, key=_canonical_model_key)),
        )
    else:
        record_branch("experiment-feedback:projection:exact-bytes:output-details")
        acceptance = ExactAcceptanceFeedback(
            mode="exact-bytes",
            outputs=tuple(
                sorted(
                    (
                        ExactOutputFeedback(output_id=row.output_id, state=row.state)
                        for row in result.expected_outputs
                    ),
                    key=lambda row: row.output_id,
                )
            ),
        )
    return CaseFeedback(**common, acceptance=acceptance)


def _case_feedback_v3(case: SessionCase, result: CaseEvaluation) -> CaseFeedbackV3:
    """The v2 row plus the case's derivation repair rows, always present."""

    base = _case_feedback_v2(case, result)
    return CaseFeedbackV3(
        **{name: getattr(base, name) for name in CaseFeedback.model_fields},
        derivations=result.derivation_feedback,
    )


def project_assurance_feedback(execution):
    """Shared live projection for snapshot, derivation and direct walk consumers."""
    from gnd.assurance import certify_result, derive_assurance_scope
    from gnd.assurance_evidence import load_assurance_evidence

    scope = derive_assurance_scope(execution, consumer="feedback")
    block = certify_result(execution, scope=scope, evidence=load_assurance_evidence())
    record_branch(f"experiment-feedback:assurance:{execution.surface}:projected")
    return block


def _case_feedback_v4(case: SessionCase, result: CaseEvaluation) -> CaseFeedbackV4:
    from gnd.assurance import AssuranceBlockV1, semantic_decision_for_band

    base = _case_feedback_v3(case, result)
    block = None
    if isinstance(case.acceptance, ConstraintSatisfactionAcceptance):
        expected_binding = (
            result.case_id,
            result.candidate_sha256,
            result.contract_sha256,
            result.raw_payload_sha256,
            result.payload_exit,
        )
        execution = (
            result._assurance_execution if result._assurance_binding == expected_binding else None
        )
        block = (
            project_assurance_feedback(execution)
            if execution is not None
            else AssuranceBlockV1(semantic_decision_for_band(result.payload_exit))
        )
    return CaseFeedbackV4(
        **{name: getattr(base, name) for name in CaseFeedbackV3.model_fields},
        assurance=AssuranceFeedback.model_validate(block.as_dict()) if block is not None else None,
    )


def _case_feedback_v5(result: CaseEvaluation) -> TransitionCaseFeedback:
    return TransitionCaseFeedback(
        case_id=result.case_id,
        role=result.role,
        command="transition",
        band=result.payload_exit,
        steps=result.transition_steps,
    )


def _case_feedback_v7(
    case: SessionCase,
    result: CaseEvaluation,
) -> TransitionCaseFeedbackV7:
    decision = case_decision(case, result)
    return TransitionCaseFeedbackV7(
        case_id=result.case_id,
        role=result.role,
        command="transition",
        band=result.payload_exit,
        steps=result.transition_steps,
        unmet_walk_floors=decision.walk_floor_gaps,
    )


def _case_feedback(
    result: CaseEvaluation,
    *,
    case: SessionCase | None = None,
    schema_version: int,
) -> _CaseFeedbackV1 | CaseFeedback | TransitionCaseFeedback | TransitionCaseFeedbackV7:
    if schema_version == LEGACY_FEEDBACK_SCHEMA_VERSION:
        record_branch("experiment-feedback:projection:n-a:legacy-v1")
        return _case_feedback_v1(result)
    if schema_version == FEEDBACK_SCHEMA_VERSION and case is not None:
        record_branch("experiment-feedback:projection:n-a:current-v2")
        return _case_feedback_v2(case, result)
    if schema_version == DERIVATION_FEEDBACK_SCHEMA_VERSION and case is not None:
        record_branch("experiment-feedback:projection:n-a:derivation-v3")
        return _case_feedback_v3(case, result)
    if schema_version == ASSURANCE_FEEDBACK_SCHEMA_VERSION and case is not None:
        return _case_feedback_v4(case, result)
    if (
        schema_version
        in {
            TRANSITION_FEEDBACK_SCHEMA_VERSION,
            REDACTION_FEEDBACK_SCHEMA_VERSION,
        }
        and case is not None
    ):
        return (
            _case_feedback_v5(result)
            if isinstance(case.acceptance, TransitionAcceptance)
            else _case_feedback_v4(case, result)
        )
    if schema_version == WALK_FLOOR_FEEDBACK_SCHEMA_VERSION and case is not None:
        return (
            _case_feedback_v7(case, result)
            if isinstance(case.acceptance, TransitionAcceptance)
            else _case_feedback_v4(case, result)
        )
    record_branch("experiment-feedback:projection:n-a:unsupported-version")
    raise ValueError(f"unsupported feedback schema version {schema_version!r}")


def _signature_document(
    attempt: AttemptEvaluation,
    *,
    contract: DataDrivenContract | None,
    schema_version: int,
) -> dict[str, Any]:
    cases_by_id = {} if contract is None else {case.case_id: case for case in contract.cases}
    rows = [
        _case_feedback(
            result,
            case=cases_by_id.get(result.case_id),
            schema_version=schema_version,
        )
        for result in attempt.results
    ]
    rows.sort(key=lambda row: row.case_id)
    # Assurance is orthogonal to retry/recurrence policy. A change in proof
    # availability must not alter the normalized business-verifier signal.
    return {
        "schema_version": schema_version,
        "cases": [
            row.model_dump(
                mode="json",
                by_alias=True,
                exclude={"assurance"} if schema_version in {4, 5, 6, 7} else set(),
            )
            for row in rows
        ],
    }


def normalized_verifier_signature(
    contract: DataDrivenContract,
    attempt: AttemptEvaluation,
    *,
    schema_version: int = LEGACY_FEEDBACK_SCHEMA_VERSION,
) -> str:
    """Hash closed verifier decision semantics for one explicit wire version."""

    document = _signature_document(
        attempt,
        contract=contract,
        schema_version=schema_version,
    )
    encoded = json.dumps(
        document,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_attempt_feedback(
    *,
    run_id: str,
    contract: DataDrivenContract,
    contract_id: str | None = None,
    contract_sha256: str,
    invocation: InvocationResult,
    evaluation: AttemptEvaluation,
    disposition: FeedbackDisposition,
    acceptance_ready: bool | None = None,
    schema_version: int = FEEDBACK_SCHEMA_VERSION,
    redaction: SessionRedaction | None = None,
) -> AttemptFeedback:
    """Build feedback solely from one immutable attempt and its fixed contract."""

    if evaluation.contract_sha256 != contract_sha256:
        record_branch("experiment-feedback:attempt:n-a:evaluation-contract-mismatch")
        raise ValueError("evaluation contract digest does not match feedback contract")
    if contract is None:
        record_branch("experiment-feedback:attempt:n-a:missing-contract")
        raise ValueError("feedback reconstruction requires the normalized contract")
    if contract_id is not None and contract_id != contract.experiment_id:
        record_branch("experiment-feedback:attempt:n-a:contract-id-mismatch")
        raise ValueError("contract_id disagrees with the supplied contract")
    contract_id = contract.experiment_id
    declared = {case.case_id: case.role.value for case in contract.cases}
    cases_by_id = {case.case_id: case for case in contract.cases}
    rows: list[
        _CaseFeedbackV1 | CaseFeedback | TransitionCaseFeedback | TransitionCaseFeedbackV7
    ] = []
    for result in evaluation.results:
        role = declared.get(result.case_id)
        if role is None:
            record_branch("experiment-feedback:attempt:n-a:undeclared-case")
            raise ValueError(f"feedback result {result.case_id!r} is not declared by the contract")
        if result.role != role:
            record_branch("experiment-feedback:attempt:n-a:case-role-mismatch")
            raise ValueError(f"feedback result {result.case_id!r} has the wrong case role")
        if result.candidate_sha256 != evaluation.candidate_sha256:
            record_branch("experiment-feedback:attempt:n-a:case-candidate-mismatch")
            raise ValueError(f"feedback result {result.case_id!r} is bound to a stale candidate")
        if result.contract_sha256 != evaluation.contract_sha256:
            record_branch("experiment-feedback:attempt:n-a:case-contract-mismatch")
            raise ValueError(f"feedback result {result.case_id!r} is bound to a stale contract")
        rows.append(
            _case_feedback(
                result,
                case=cases_by_id.get(result.case_id),
                schema_version=schema_version,
            )
        )
    rows.sort(key=lambda row: row.case_id)
    required = tuple(row for row in rows if row.role == "required")
    diagnostic = tuple(row for row in rows if row.role == "diagnostic")
    by_id = {result.case_id: result for result in evaluation.results}
    ordered_ids = sorted(by_id)
    feedback = AttemptFeedback(
        schema_version=schema_version,
        run_id=run_id,
        contract_id=contract_id,
        contract_sha256=contract_sha256,
        source_attempt_index=evaluation.attempt_index,
        candidate_sha256=evaluation.candidate_sha256,
        case_payload_sha256s=tuple(
            (case_id, by_id[case_id].raw_payload_sha256) for case_id in ordered_ids
        ),
        normalized_verifier_signature=normalized_verifier_signature(
            contract,
            evaluation,
            schema_version=schema_version,
        ),
        process_exit=invocation.exit_code,
        payload_exit=tuple((case_id, by_id[case_id].payload_exit) for case_id in ordered_ids),
        acceptance_ready=(
            contract_accepts(contract, evaluation)
            if contract is not None
            else bool(acceptance_ready)
        ),
        required=required,
        diagnostic=diagnostic,
        disposition=disposition,
        redaction=redaction,
    )
    record_branch("experiment-feedback:attempt:n-a:built")
    return feedback


def canonical_feedback(feedback: AttemptFeedback) -> tuple[bytes, str]:
    """Return feedback's sole accepted JSON encoding and its SHA-256."""

    if not isinstance(feedback, AttemptFeedback):
        raise TypeError("feedback must be an AttemptFeedback instance")
    _assert_model_instance_closed(feedback, path="feedback")
    validated = AttemptFeedback.model_validate(feedback.model_dump(mode="python", by_alias=True))
    encoded = (
        json.dumps(
            validated.model_dump(mode="json", by_alias=True),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    return encoded, hashlib.sha256(encoded).hexdigest()


def _assert_model_instance_closed(value: Any, *, path: str) -> None:
    """Reject hidden ``model_copy(update=...)`` extras before serialization."""

    if isinstance(value, BaseModel):
        declared = set(type(value).model_fields)
        observed = set(value.__dict__)
        if observed != declared:
            unexpected = sorted(observed - declared)
            missing = sorted(declared - observed)
            raise ValueError(
                f"{path} has hidden or missing model fields: "
                f"unexpected={unexpected}, missing={missing}"
            )
        for name in sorted(declared):
            _assert_model_instance_closed(getattr(value, name), path=f"{path}.{name}")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _assert_model_instance_closed(item, path=f"{path}[{key!r}]")
        return
    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _assert_model_instance_closed(item, path=f"{path}[{index}]")
