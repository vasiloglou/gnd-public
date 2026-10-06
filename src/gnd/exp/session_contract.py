"""Closed, digest-bound contracts for data-driven experiment sessions.

The contract describes data and verifier subjects only.  Process selection,
arguments, prompts, and environment values remain trusted caller inputs in
``gnd.agent_cli`` and can never be supplied by committed contract bytes.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import stat
from collections import Counter
from enum import StrEnum
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Annotated, Any, Literal, Self

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PrivateAttr,
    StrictBool,
    StrictInt,
    StrictStr,
    StringConstraints,
    ValidationError,
    model_serializer,
    model_validator,
)
from pydantic_core import PydanticCustomError

from gnd import input_policy as _rf7_input
from gnd.artifacts import canonical_json_text
from gnd.exp.session_profile import (
    JUDGMENT_SESSION_CONTRACT_VERSION,
    SessionProfile,
    profile_for_version,
)
from gnd.extract.manifest import ManifestError, manifest_path_issue, open_manifest_relative_path
from gnd.model import ModelLoadError, ModelValidationError, ValidationIssue, load_model

__all__ = [
    "AdapterDeclaration",
    "AdapterParameters",
    "CaseAcceptance",
    "CaseRole",
    "ConstraintSatisfactionAcceptance",
    "CoverageFloor",
    "DataDrivenContract",
    "DigestBoundPath",
    "ExactBytesAcceptance",
    "ExpectedOutput",
    "ProtectedPath",
    "RequiredOperation",
    "SessionCase",
    "SessionContractError",
    "TestId",
    "TestsAcceptance",
    "TransitionAcceptance",
    "TransitionVerifyCase",
    "VerifyCase",
    "WalkAcceptance",
    "read_session_contract",
]

SESSION_CONTRACT_VERSION = 2
TESTS_SESSION_CONTRACT_VERSION = 3
TRANSITION_SESSION_CONTRACT_VERSION = 4
WALK_SESSION_CONTRACT_VERSION = 5
DECLARED_ADAPTER_SESSION_CONTRACT_VERSION = 6
LEGACY_SESSION_CONTRACT_VERSION = 1
MAX_SESSION_CONTRACT_BYTES = 1 * 1024 * 1024
MAX_SESSION_INPUT_BYTES = 10 * 1024 * 1024
MAX_SESSION_BOUND_BYTES = 100 * 1024 * 1024
MAX_SESSION_CASES = 1024
MAX_WALK_FLOOR_ROWS = 4096
MAX_REQUIRED_TESTS = 10_000
MAX_REQUIRED_TEST_ID_BYTES = 4_096
MAX_PROTECTED_PATHS = 10_000
SESSION_CONTRACT_RULE_ID = "experiment:session-contract-invalid"
CONTRACT_SHAPE_REASON = "contract:shape"
TESTS_REQUIRED_ID_REASON = "tests:required-id"
TESTS_REQUIRED_LIMIT_REASON = "tests:required-limit"
TESTS_PROTECTED_LIMIT_REASON = "tests:protected-limit"
TESTS_PROTECTED_UNCOVERED_REASON = "tests:protected-uncovered"
TESTS_PROTECTED_SYMLINK_REASON = "tests:protected-symlink"
TESTS_PROTECTED_DIGEST_REASON = "tests:protected-digest"
TESTS_ARGV_ECHO_MISMATCH_REASON = "tests:argv-echo-mismatch"
TESTS_ARGV_ECHO_DIVERGENT_REASON = "tests:argv-echo-divergent"
TESTS_RESULTS_PATH_REASON = "tests:results-path-relative"

_V3_ERROR_RULES = {
    "tests_required_id": TESTS_REQUIRED_ID_REASON,
    "tests_required_limit": TESTS_REQUIRED_LIMIT_REASON,
    "tests_protected_limit": TESTS_PROTECTED_LIMIT_REASON,
    "tests_protected_digest": TESTS_PROTECTED_DIGEST_REASON,
    "tests_argv_echo_divergent": TESTS_ARGV_ECHO_DIVERGENT_REASON,
    "tests_results_path_relative": TESTS_RESULTS_PATH_REASON,
}

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
CaseId = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$",
    ),
]
Sha256String = Annotated[
    str,
    StringConstraints(strip_whitespace=True, pattern=r"^[0-9a-f]{64}$"),
]


class AdapterParameters(BaseModel):
    """Non-secret model parameters committed by a schema-v6 contract."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    model: NonEmptyString | None = None


class AdapterDeclaration(BaseModel):
    """Contract selection of one trusted local adapter policy."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    policy_id: CaseId
    parameters: AdapterParameters


class CaseRole(StrEnum):
    required = "required"
    diagnostic = "diagnostic"


class SessionContractError(Exception):
    """A session contract could not be safely loaded and verified."""

    def __init__(self, message: str, issues: list[ValidationIssue] | None = None):
        self.issues = list(issues or [])
        if not self.issues:
            self.issues.append(
                ValidationIssue(
                    path="",
                    message=message,
                    rule_id=SESSION_CONTRACT_RULE_ID,
                )
            )
        super().__init__(message)


class DigestBoundPath(BaseModel):
    """One experiment-relative file whose exact bytes are committed."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    path: NonEmptyString
    media_type: NonEmptyString
    encoding: NonEmptyString
    sha256: Sha256String
    size_bytes: int = Field(ge=0, le=MAX_SESSION_INPUT_BYTES)


class ProtectedPath(BaseModel):
    """One compact path/digest seal for a protected candidate file."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    path: NonEmptyString
    sha256: Sha256String


class ExpectedOutput(DigestBoundPath):
    """One declared expected output, addressed by digest.

    ``candidate_path`` is the coordinate acceptance needs — where the agent
    must produce the bytes — and ``comparison`` states by which relation they
    are compared.  ``comparison`` has exactly one member on purpose: a declared
    equivalence must arrive as a new enum member with its own comparator and
    its own tests, never as an inferred default over an absent field.

    ``path`` is OPTIONAL, and omitting it is the answer-free way to declare an
    exact expectation.  Acceptance never reads the expected file: it compares
    the candidate's digest against ``sha256`` (``session_eval.py`` builds the
    observation, matching on digest alone).  A committed ``path`` only ever
    served ``_verify_bound_file``'s load-time proof that the declared digest
    matched bytes that demonstrably exist — a tamper-check on the contract, not
    an input to acceptance.  Paying for that proof with a plaintext answer
    sitting beside the agent's working directory is what made every exact
    experiment leakable, so the proof moves to authoring time: materialize the
    output, hash it, record the digest, discard the bytes.

    Both shapes stay legal, and behaviour selects on presence, so committed
    version-1 evidence that does declare ``path`` keeps validating unchanged.
    ``size_bytes`` follows ``path`` — it is a property of a bound file, and it
    is also an answer channel in its own right (an exact byte length plus a
    per-attempt matched/differs oracle narrows a search), so a pathless
    expectation declares neither.
    """

    path: NonEmptyString | None = None
    size_bytes: int | None = Field(default=None, ge=0, le=MAX_SESSION_INPUT_BYTES)
    output_id: CaseId
    candidate_path: NonEmptyString
    comparison: Literal["exact-bytes"]

    @model_validator(mode="after")
    def _path_and_size_agree(self) -> Self:
        """``size_bytes`` describes a bound file, so it may not outlive one."""
        if self.path is None and self.size_bytes is not None:
            raise ValueError(
                "size_bytes describes a committed file; a pathless expected output "
                "must declare neither"
            )
        if self.path is not None and self.size_bytes is None:
            raise ValueError("an expected output declaring path must also declare size_bytes")
        return self


class VerifyCase(BaseModel):
    """The fixed GND verifier operation for one candidate-relative subject."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    command: Literal["check", "verify"]
    model: DigestBoundPath
    subject: NonEmptyString


class TransitionVerifyCase(BaseModel):
    """A candidate-owned transition walk with one digest-bound pre-state."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    command: Literal["transition"]
    model: DigestBoundPath
    pre: NonEmptyString
    steps: NonEmptyString
    post: NonEmptyString | None

    @model_validator(mode="after")
    def _candidate_paths_are_safe(self) -> Self:
        for field in ("steps", "post"):
            value = getattr(self, field)
            if value is not None and not _results_path_is_safe(value):
                raise ValueError(f"{field} must be a normalized candidate-relative path")
        return self


class CoverageFloor(BaseModel):
    """Minimum checker-observed population for one declared model fact type."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    fact_type: CaseId
    min_facts: int = Field(ge=1)


class ExactBytesAcceptance(BaseModel):
    """Acceptance by verifier success and byte-exact declared outputs."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    mode: Literal["exact-bytes"]
    expected_outputs: tuple[ExpectedOutput, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _outputs_are_individually_addressable(self) -> Self:
        ids = [output.output_id for output in self.expected_outputs]
        duplicates = sorted({output_id for output_id in ids if ids.count(output_id) > 1})
        if duplicates:
            raise ValueError(f"duplicate expected output id(s): {', '.join(duplicates)}")
        return self


class ConstraintSatisfactionAcceptance(BaseModel):
    """Acceptance by checker band zero plus checker-reported coverage floors."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    mode: Literal["constraint-satisfaction"]
    coverage: tuple[CoverageFloor, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _coverage_fact_types_are_unique(self) -> Self:
        ids = [floor.fact_type for floor in self.coverage]
        duplicates = sorted({fact_type for fact_type in ids if ids.count(fact_type) > 1})
        if duplicates:
            raise ValueError(f"duplicate coverage fact type(s): {', '.join(duplicates)}")
        return self


class _TransitionAcceptanceV4(BaseModel):
    """Frozen schema-v4 transition shape; never widened with walk floors."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    mode: Literal["transition"]


def _closed_json_scalar(value: Any) -> Any:
    """Admit finite RFC-8259 scalars without coercion or huge-int crashes."""
    if not isinstance(value, (str, int, float, bool)):
        raise PydanticCustomError(
            "json_scalar_type",
            "binding values must be JSON string, integer, number, or boolean scalars",
        )
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"binding value is not a finite JSON scalar: {error}") from error
    return value


JsonScalar = Annotated[
    StrictStr | StrictInt | Annotated[float, Field(strict=True, allow_inf_nan=False)] | StrictBool,
    BeforeValidator(_closed_json_scalar),
]


class RequiredOperation(BaseModel):
    """One operation whose single submitted step must contain this subset."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    op: CaseId
    bindings_subset: dict[NonEmptyString, JsonScalar]


class WalkAcceptance(BaseModel):
    """Required and forbidden operation floors over an accepted walk."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    required_ops: tuple[RequiredOperation, ...] = Field(max_length=MAX_WALK_FLOOR_ROWS)
    forbidden_ops: tuple[CaseId, ...] = Field(max_length=MAX_WALK_FLOOR_ROWS)

    @model_validator(mode="after")
    def _declaration_is_closed(self) -> Self:
        if not self.required_ops and not self.forbidden_ops:
            raise ValueError("walk requires at least one required or forbidden operation")
        canonical = [
            (
                row.op,
                canonical_json_text(row.bindings_subset),
            )
            for row in self.required_ops
        ]
        duplicates = sorted(row for row, count in Counter(canonical).items() if count > 1)
        if duplicates:
            raise ValueError(
                "duplicate required operation declaration(s): "
                + ", ".join(operation for operation, _ in duplicates)
            )
        forbidden_duplicates = sorted(
            operation for operation, count in Counter(self.forbidden_ops).items() if count > 1
        )
        if forbidden_duplicates:
            raise ValueError(
                "duplicate forbidden operation id(s): " + ", ".join(forbidden_duplicates)
            )
        conflicts = sorted({row.op for row in self.required_ops} & set(self.forbidden_ops))
        if conflicts:
            raise ValueError(
                "operation(s) cannot be both required and forbidden: " + ", ".join(conflicts)
            )
        return self


class TransitionAcceptance(BaseModel):
    """Acceptance by the band of one transition verifier invocation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    mode: Literal["transition"]
    walk: WalkAcceptance | None = None


CaseAcceptance = Annotated[
    ExactBytesAcceptance | ConstraintSatisfactionAcceptance,
    Field(discriminator="mode"),
]


class JudgmentGate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    policy: DigestBoundPath
    receipts_path: NonEmptyString
    trusted_root: NonEmptyString

    @model_validator(mode="after")
    def _paths(self):
        for value in (self.receipts_path, self.trusted_root):
            if manifest_path_issue("judgment", value, SESSION_CONTRACT_RULE_ID):
                raise ValueError("unsafe judgment path")
        return self


class SessionCase(BaseModel):
    """Normalized required or diagnostic row in the fixed case denominator."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    judgment_gate: JudgmentGate | None = None
    _session_version: int = PrivateAttr(default=0)
    reference_root: str | None = None
    case_id: CaseId
    role: CaseRole
    inputs: tuple[DigestBoundPath, ...] = ()
    acceptance: ExpandedCaseAcceptance
    # Runtime compatibility view. It is populated from the selected acceptance
    # branch and omitted from v2 serialization; v1 serialization keeps this
    # original field and omits the normalized branch.
    expected_outputs: tuple[ExpectedOutput, ...] = ()
    verify: VerifyCase | TransitionVerifyCase | None = None


class _SessionCaseV1(BaseModel):
    """Frozen schema-v1 wire reader."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: CaseId
    role: CaseRole
    inputs: tuple[DigestBoundPath, ...] = Field(min_length=1)
    expected_outputs: tuple[ExpectedOutput, ...] = Field(min_length=1)
    verify: VerifyCase

    @model_validator(mode="after")
    def _expected_outputs_are_individually_addressable(self) -> Self:
        ExactBytesAcceptance(mode="exact-bytes", expected_outputs=self.expected_outputs)
        return self


class _SessionCaseV2(BaseModel):
    """Strict schema-v2 wire reader."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: CaseId
    role: CaseRole
    inputs: tuple[DigestBoundPath, ...] = Field(min_length=1)
    acceptance: CaseAcceptance
    verify: VerifyCase

    @model_validator(mode="after")
    def _constraint_mode_uses_the_checker(self) -> Self:
        if (
            isinstance(self.acceptance, ConstraintSatisfactionAcceptance)
            and self.verify.command != "check"
        ):
            raise ValueError("constraint-satisfaction acceptance requires verifier command 'check'")
        return self


class _DataDrivenContractV1(BaseModel):
    """Frozen schema-v1 contract reader; never widened with v2 fields."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[LEGACY_SESSION_CONTRACT_VERSION]
    experiment_id: NonEmptyString
    max_attempts: int = Field(gt=0)
    wall_seconds: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    cases: tuple[_SessionCaseV1, ...] = Field(min_length=1, max_length=MAX_SESSION_CASES)


class _DataDrivenContractV2(BaseModel):
    """Strict schema-v2 contract reader; legacy case fields are forbidden."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[SESSION_CONTRACT_VERSION]
    experiment_id: NonEmptyString
    max_attempts: int = Field(gt=0)
    wall_seconds: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    cases: tuple[_SessionCaseV2, ...] = Field(min_length=1, max_length=MAX_SESSION_CASES)


# Preserve the v2 value captured by the frozen reader above, then publish the
# current version for downstream consumers without changing that reader's bytes.
V2_SESSION_CONTRACT_VERSION = SESSION_CONTRACT_VERSION
SESSION_CONTRACT_VERSION = TESTS_SESSION_CONTRACT_VERSION


TestId = str


def _custom_error(error_type: str, message: str) -> PydanticCustomError:
    return PydanticCustomError(error_type, message)


def _test_path(identifier: str) -> str | None:
    """Return the named Python path when ``identifier`` has the TestId grammar."""

    if not isinstance(identifier, str):
        return None
    path, separator, selectors = identifier.partition("::")
    if not separator or not selectors:
        return None
    selector_parts = selectors.split("::")
    if any(not selector for selector in selector_parts):
        return None
    if (
        not path.endswith(".py")
        or "\\" in path
        or "\x00" in path
        or PurePosixPath(path).is_absolute()
        or PureWindowsPath(path).is_absolute()
        or bool(PureWindowsPath(path).drive)
    ):
        return None
    parts = path.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return None
    return path


def _results_path_is_safe(value: str) -> bool:
    if not value or "\\" in value or "\x00" in value:
        return False
    windows = PureWindowsPath(value)
    if PurePosixPath(value).is_absolute() or windows.is_absolute() or bool(windows.drive):
        return False
    return all(part not in {"", ".", ".."} for part in value.split("/"))


class TestsAcceptance(BaseModel):
    """Acceptance by a sealed, explicitly named JUnit test set."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    mode: Literal["tests"]
    required_tests: tuple[TestId, ...] = Field(min_length=1)
    results_path: str
    results_format: Literal["junit-xml"]
    protected: tuple[ProtectedPath | DigestBoundPath, ...] = Field(min_length=1)
    test_argv_sha256: Sha256String

    @model_validator(mode="before")
    @classmethod
    def _collection_caps_precede_element_work(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        required = value.get("required_tests")
        if isinstance(required, (list, tuple)):
            if len(required) > MAX_REQUIRED_TESTS:
                raise _custom_error(
                    "tests_required_limit",
                    f"required_tests has {len(required)} entries, over the "
                    f"{MAX_REQUIRED_TESTS}-entry cap",
                )
            for identifier in required:
                if (
                    isinstance(identifier, str)
                    and len(identifier.rsplit("::", 1)[-1].encode("utf-8"))
                    > MAX_REQUIRED_TEST_ID_BYTES
                ):
                    raise _custom_error(
                        "tests_required_limit",
                        f"final test selector exceeds {MAX_REQUIRED_TEST_ID_BYTES} UTF-8 bytes",
                    )
        protected = value.get("protected")
        if isinstance(protected, (list, tuple)) and len(protected) > MAX_PROTECTED_PATHS:
            raise _custom_error(
                "tests_protected_limit",
                f"protected has {len(protected)} entries, over the {MAX_PROTECTED_PATHS}-entry cap",
            )
        return value

    @model_validator(mode="after")
    def _declaration_is_closed(self) -> Self:
        invalid = [
            identifier for identifier in self.required_tests if _test_path(identifier) is None
        ]
        if invalid:
            raise _custom_error(
                "tests_required_id",
                f"invalid required test id(s): {', '.join(repr(item) for item in invalid)}",
            )
        if len(set(self.required_tests)) != len(self.required_tests):
            raise _custom_error("tests_required_id", "required test ids must be unique")
        paths = [entry.path for entry in self.protected]
        if len(set(paths)) != len(paths):
            raise _custom_error("tests_protected_digest", "protected paths must be unique")
        if not _results_path_is_safe(self.results_path):
            raise _custom_error(
                "tests_results_path_relative",
                "results_path must be a non-empty normalized relative path without . or ..",
            )
        return self


V3CaseAcceptance = Annotated[
    ExactBytesAcceptance | ConstraintSatisfactionAcceptance | TestsAcceptance,
    Field(discriminator="mode"),
]
ExpandedCaseAcceptance = Annotated[
    ExactBytesAcceptance
    | ConstraintSatisfactionAcceptance
    | TestsAcceptance
    | TransitionAcceptance,
    Field(discriminator="mode"),
]
V4CaseAcceptance = Annotated[
    ExactBytesAcceptance
    | ConstraintSatisfactionAcceptance
    | TestsAcceptance
    | _TransitionAcceptanceV4,
    Field(discriminator="mode"),
]
# Publicly, CaseAcceptance is the current union. _SessionCaseV2 captured the
# two-member definition above when its frozen class was created.
CaseAcceptance = ExpandedCaseAcceptance
SessionCase.model_rebuild()


class _SessionCaseV3(BaseModel):
    """Strict schema-v3 reader; tests cases omit verifier and input fields."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: CaseId
    role: CaseRole
    inputs: tuple[DigestBoundPath, ...] = ()
    acceptance: V3CaseAcceptance
    verify: VerifyCase | None = None

    @model_validator(mode="after")
    def _fields_match_acceptance_mode(self) -> Self:
        if isinstance(self.acceptance, TestsAcceptance):
            forbidden = self.model_fields_set & {"inputs", "verify"}
            if forbidden:
                raise ValueError(
                    "tests acceptance forbids case field(s): " + ", ".join(sorted(forbidden))
                )
            return self
        if "inputs" not in self.model_fields_set or not self.inputs:
            raise ValueError("non-tests v3 cases require non-empty inputs")
        if "verify" not in self.model_fields_set or self.verify is None:
            raise ValueError("non-tests v3 cases require verify")
        if (
            isinstance(self.acceptance, ConstraintSatisfactionAcceptance)
            and self.verify.command != "check"
        ):
            raise ValueError("constraint-satisfaction acceptance requires verifier command 'check'")
        return self


class _DataDrivenContractV3(BaseModel):
    """Strict schema-v3 contract reader."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[TESTS_SESSION_CONTRACT_VERSION]
    experiment_id: NonEmptyString
    max_attempts: int = Field(gt=0)
    wall_seconds: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    cases: tuple[_SessionCaseV3, ...] = Field(min_length=1, max_length=MAX_SESSION_CASES)

    @model_validator(mode="before")
    @classmethod
    def _legacy_cases_do_not_change_version_by_relabeling(cls, value: Any) -> Any:
        if (
            isinstance(value, dict)
            and isinstance(value.get("cases"), (list, tuple))
            and any(
                isinstance(case, dict) and "expected_outputs" in case for case in value["cases"]
            )
        ):
            raise ValueError("schema_version 3 requires the v3 case shape")
        return value

    @model_validator(mode="after")
    def _tests_cases_share_one_argv_echo(self) -> Self:
        echoes = {
            case.acceptance.test_argv_sha256
            for case in self.cases
            if isinstance(case.acceptance, TestsAcceptance)
        }
        if len(echoes) > 1:
            raise _custom_error(
                "tests_argv_echo_divergent",
                "all tests cases must declare the same test_argv_sha256",
            )
        return self


class _SessionCaseV4(BaseModel):
    """Strict schema-v4 reader adding transition acceptance."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: CaseId
    role: CaseRole
    inputs: tuple[DigestBoundPath, ...] = ()
    acceptance: V4CaseAcceptance
    verify: VerifyCase | TransitionVerifyCase | None = None

    @model_validator(mode="after")
    def _fields_match_acceptance_mode(self) -> Self:
        if isinstance(self.acceptance, TestsAcceptance):
            forbidden = self.model_fields_set & {"inputs", "verify"}
            if forbidden:
                raise ValueError(
                    "tests acceptance forbids case field(s): " + ", ".join(sorted(forbidden))
                )
            return self
        if not self.inputs or self.verify is None:
            raise ValueError("non-tests v4 cases require non-empty inputs and verify")
        if isinstance(self.acceptance, (_TransitionAcceptanceV4, TransitionAcceptance)):
            if not isinstance(self.verify, TransitionVerifyCase):
                raise TypeError("transition acceptance requires verifier command 'transition'")
            input_paths = [entry.path for entry in self.inputs]
            if input_paths.count(self.verify.pre) != 1:
                raise ValueError("transition pre must name exactly one digest-bound input")
            candidate_paths = [self.verify.steps]
            if self.verify.post is not None:
                candidate_paths.append(self.verify.post)
            overlap = sorted(set(input_paths) & set(candidate_paths))
            if overlap:
                raise ValueError(
                    "transition steps and post are candidate-owned, not bound inputs: "
                    + ", ".join(overlap)
                )
            return self
        if isinstance(self.verify, TransitionVerifyCase):
            raise TypeError("transition verifier requires transition acceptance")
        if (
            isinstance(self.acceptance, ConstraintSatisfactionAcceptance)
            and self.verify.command != "check"
        ):
            raise ValueError("constraint-satisfaction acceptance requires verifier command 'check'")
        return self


class _DataDrivenContractV4(BaseModel):
    """Strict schema-v4 contract reader."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[TRANSITION_SESSION_CONTRACT_VERSION]
    experiment_id: NonEmptyString
    max_attempts: int = Field(gt=0)
    wall_seconds: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    cases: tuple[_SessionCaseV4, ...] = Field(min_length=1, max_length=MAX_SESSION_CASES)

    @model_validator(mode="after")
    def _version_four_is_transition_disjoint(self) -> Self:
        if not any(
            isinstance(case.acceptance, (_TransitionAcceptanceV4, TransitionAcceptance))
            for case in self.cases
        ):
            raise ValueError("schema_version 4 requires at least one transition case")
        echoes = {
            case.acceptance.test_argv_sha256
            for case in self.cases
            if isinstance(case.acceptance, TestsAcceptance)
        }
        if len(echoes) > 1:
            raise _custom_error(
                "tests_argv_echo_divergent",
                "all tests cases must declare the same test_argv_sha256",
            )
        return self


class _SessionCaseV5(_SessionCaseV4):
    """Strict schema-v5 reader adding optional per-case walk floors."""

    acceptance: ExpandedCaseAcceptance

    @model_validator(mode="before")
    @classmethod
    def _transition_wire_declares_walk(cls, value: Any) -> Any:
        if isinstance(value, dict):
            acceptance = value.get("acceptance")
            if (
                isinstance(acceptance, dict)
                and acceptance.get("mode") == "transition"
                and "walk" not in acceptance
            ):
                raise ValueError("schema-version 5 transition acceptance must declare walk")
        return value

    @model_validator(mode="after")
    def _fields_match_acceptance_mode(self) -> Self:
        if isinstance(self.acceptance, TestsAcceptance):
            forbidden = self.model_fields_set & {"inputs", "verify"}
            if forbidden:
                raise ValueError(
                    "tests acceptance forbids case field(s): " + ", ".join(sorted(forbidden))
                )
            return self
        if not self.inputs or self.verify is None:
            raise ValueError("non-tests v5 cases require non-empty inputs and verify")
        if isinstance(self.acceptance, TransitionAcceptance):
            if not isinstance(self.verify, TransitionVerifyCase):
                raise _custom_error(
                    "contract_shape",
                    "transition acceptance requires verifier command 'transition'",
                )
            input_paths = [entry.path for entry in self.inputs]
            if input_paths.count(self.verify.pre) != 1:
                raise ValueError("transition pre must name exactly one digest-bound input")
            candidate_paths = [self.verify.steps]
            if self.verify.post is not None:
                candidate_paths.append(self.verify.post)
            overlap = sorted(set(input_paths) & set(candidate_paths))
            if overlap:
                raise ValueError(
                    "transition steps and post are candidate-owned, not bound inputs: "
                    + ", ".join(overlap)
                )
            return self
        if isinstance(self.verify, TransitionVerifyCase):
            raise _custom_error(
                "contract_shape",
                "transition verifier requires transition acceptance",
            )
        if (
            isinstance(self.acceptance, ConstraintSatisfactionAcceptance)
            and self.verify.command != "check"
        ):
            raise ValueError("constraint-satisfaction acceptance requires verifier command 'check'")
        return self


class _DataDrivenContractV5(_DataDrivenContractV4):
    """Strict schema-v5 reader; at least one transition case owns a walk."""

    schema_version: Literal[WALK_SESSION_CONTRACT_VERSION]
    cases: tuple[_SessionCaseV5, ...] = Field(min_length=1, max_length=MAX_SESSION_CASES)

    @model_validator(mode="after")
    def _version_five_is_walk_disjoint(self) -> Self:
        if not any(
            isinstance(case.acceptance, TransitionAcceptance) and case.acceptance.walk is not None
            for case in self.cases
        ):
            raise ValueError("schema_version 5 requires at least one transition walk declaration")
        return self


class _SessionCaseV6(_SessionCaseV5):
    """Strict schema-v6 case reader retaining the complete v5 case union."""


class _DataDrivenContractV6(BaseModel):
    """Strict schema-v6 reader adding declared adapter selection."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[DECLARED_ADAPTER_SESSION_CONTRACT_VERSION]
    experiment_id: NonEmptyString
    max_attempts: int = Field(gt=0)
    wall_seconds: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    adapter: AdapterDeclaration
    cases: tuple[_SessionCaseV6, ...] = Field(min_length=1, max_length=MAX_SESSION_CASES)

    @model_validator(mode="after")
    def _declared_adapter_requires_a_non_tests_case(self) -> Self:
        if not any(not isinstance(case.acceptance, TestsAcceptance) for case in self.cases):
            raise ValueError("schema_version 6 requires at least one non-tests case")
        return self


PATCH_SESSION_CONTRACT_VERSION = 7


class PatchCollection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    path: tuple[str, ...] = Field(min_length=1, max_length=16)
    key: tuple[str, ...] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def _selectors(self):
        if len(set(self.key)) != len(self.key) or any(
            not x or len(x.encode()) > 4096 for x in (*self.path, *self.key)
        ):
            raise ValueError("invalid collection selector")
        return self


class PatchArtifact(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    path: str
    collections: tuple[PatchCollection, ...] = Field(default=(), max_length=256)


class CandidateEdits(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    patch_path: str
    artifacts: tuple[PatchArtifact, ...] = Field(min_length=1, max_length=256)

    @model_validator(mode="after")
    def _declarations(self):
        paths = [self.patch_path, *(x.path for x in self.artifacts)]
        if sum(len(x.collections) for x in self.artifacts) > 256:
            raise ValueError("collection count exceeds cap")
        for path in paths:
            if len(path.encode()) > 4096 or manifest_path_issue(
                "path", path, SESSION_CONTRACT_RULE_ID
            ):
                raise ValueError("invalid artifact path")
        ordered = sorted(paths)
        if any(a == b or b.startswith(a + "/") for a, b in itertools.pairwise(ordered)):
            raise ValueError("overlapping artifact paths")
        for artifact in self.artifacts:
            selectors = [c.path for c in artifact.collections]
            if len(set(selectors)) != len(selectors):
                raise ValueError("duplicate collection")
        return self


class RankingMetric(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    metric: Literal[
        "accepted_required_cases",
        "candidate_admitted_unique",
        "alethic_failures",
        "alethic_indeterminate",
        "coverage_shortfall",
    ]
    direction: Literal["min", "max"]


class _SessionCaseV7(_SessionCaseV6):
    reference_root: str | None = None

    @model_validator(mode="after")
    def _fields_match_acceptance_mode(self):
        if not self.inputs and not isinstance(
            self.acceptance, (TestsAcceptance, TransitionAcceptance)
        ):
            if self.verify is None or isinstance(self.verify, TransitionVerifyCase):
                raise ValueError("snapshot case requires verify")
            if (
                isinstance(self.acceptance, ConstraintSatisfactionAcceptance)
                and self.verify.command != "check"
            ):
                raise ValueError("constraint acceptance requires check")
            return self
        return super()._fields_match_acceptance_mode()


class _DataDrivenContractV7(_DataDrivenContractV6):
    schema_version: Literal[7]
    max_attempts: int = Field(strict=True, ge=1, le=1024)
    cases: tuple[_SessionCaseV7, ...] = Field(min_length=1, max_length=MAX_SESSION_CASES)
    candidate_edits: CandidateEdits | None = None
    ranking: tuple[RankingMetric, ...] | None = Field(default=None, min_length=1, max_length=5)

    @model_validator(mode="after")
    def _new_paths(self):
        if self.ranking and len({x.metric for x in self.ranking}) != len(self.ranking):
            raise ValueError("duplicate ranking metric")
        if self.candidate_edits:
            protected = {
                "session.contract.json",
                *(bound.path for case in self.cases for bound in case.inputs),
            }
            protected.update(
                case.verify.model.path for case in self.cases if case.verify is not None
            )
            protected.update(
                bound.path
                for case in self.cases
                if isinstance(case.acceptance, TestsAcceptance)
                for bound in case.acceptance.protected
            )
            for target in [
                self.candidate_edits.patch_path,
                *(a.path for a in self.candidate_edits.artifacts),
            ]:
                if any(
                    target == path or target.startswith(path + "/") or path.startswith(target + "/")
                    for path in protected
                ):
                    raise ValueError("candidate declaration overlaps protected input")
        for case in self.cases:
            if (
                case.reference_root is not None
                and case.reference_root != "."
                and manifest_path_issue(
                    "reference_root", case.reference_root, SESSION_CONTRACT_RULE_ID
                )
            ):
                raise ValueError("unsafe reference root")
        return self


class _SessionCaseV8(_SessionCaseV7):
    judgment_gate: JudgmentGate | None

    @model_validator(mode="after")
    def _gate(self):
        if self.judgment_gate and (
            not isinstance(self.acceptance, ConstraintSatisfactionAcceptance)
            or self.verify is None
            or self.verify.command != "check"
        ):
            raise ValueError("judgment gate requires snapshot mechanical admission")
        return self


class _DataDrivenContractV8(_DataDrivenContractV7):
    schema_version: Literal[JUDGMENT_SESSION_CONTRACT_VERSION]
    cases: tuple[_SessionCaseV8, ...] = Field(min_length=1, max_length=MAX_SESSION_CASES)

    @model_validator(mode="after")
    def _protected_judgments(self):
        for case in self.cases:
            gate = case.judgment_gate
            if gate is None:
                continue
            paths = ["candidate", gate.receipts_path]
            if self.candidate_edits:
                paths += [
                    self.candidate_edits.patch_path,
                    *(a.path for a in self.candidate_edits.artifacts),
                ]
            for target in paths:
                for protected in (gate.trusted_root, gate.policy.path):
                    if (
                        target == protected
                        or target.startswith(protected + "/")
                        or protected.startswith(target + "/")
                    ):
                        raise ValueError("judgment authority overlaps candidate artifacts")
        return self


_CONTRACT_READERS = {
    LEGACY_SESSION_CONTRACT_VERSION: _DataDrivenContractV1,
    V2_SESSION_CONTRACT_VERSION: _DataDrivenContractV2,
    SESSION_CONTRACT_VERSION: _DataDrivenContractV3,
    TRANSITION_SESSION_CONTRACT_VERSION: _DataDrivenContractV4,
    WALK_SESSION_CONTRACT_VERSION: _DataDrivenContractV5,
    DECLARED_ADAPTER_SESSION_CONTRACT_VERSION: _DataDrivenContractV6,
    PATCH_SESSION_CONTRACT_VERSION: _DataDrivenContractV7,
    JUDGMENT_SESSION_CONTRACT_VERSION: _DataDrivenContractV8,
}


class DataDrivenContract(BaseModel):
    """Version-dispatched contract normalized for the session runtime."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[
        LEGACY_SESSION_CONTRACT_VERSION,
        V2_SESSION_CONTRACT_VERSION,
        SESSION_CONTRACT_VERSION,
        TRANSITION_SESSION_CONTRACT_VERSION,
        WALK_SESSION_CONTRACT_VERSION,
        DECLARED_ADAPTER_SESSION_CONTRACT_VERSION,
        PATCH_SESSION_CONTRACT_VERSION,
        JUDGMENT_SESSION_CONTRACT_VERSION,
    ]
    experiment_id: NonEmptyString
    max_attempts: int = Field(gt=0)
    wall_seconds: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    cases: tuple[SessionCase, ...] = Field(min_length=1, max_length=MAX_SESSION_CASES)
    adapter: AdapterDeclaration | None = None
    candidate_edits: CandidateEdits | None = None
    ranking: tuple[RankingMetric, ...] | None = None

    _profile: SessionProfile | None = PrivateAttr(default=None)

    @property
    def profile(self) -> SessionProfile:
        """Runtime-only capabilities; copies with another version cannot go stale."""
        if self._profile is not None and self._profile.contract_version == self.schema_version:
            return self._profile
        profile = profile_for_version(self.schema_version)
        if profile is None:
            raise ValueError("unsupported session profile")
        self._profile = profile
        return profile

    @classmethod
    def model_validate(cls, obj: Any, *args: Any, **kwargs: Any) -> Self:
        """Dispatch the closed wire version before parsing either schema."""

        if isinstance(obj, cls):
            return obj
        version = obj.get("schema_version") if isinstance(obj, dict) else None
        profile = profile_for_version(version)
        if profile is not None:
            reader = _CONTRACT_READERS[profile.contract_version]
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
                                f"{LEGACY_SESSION_CONTRACT_VERSION}, "
                                f"{V2_SESSION_CONTRACT_VERSION}, or "
                                f"{SESSION_CONTRACT_VERSION}, or "
                                f"{TRANSITION_SESSION_CONTRACT_VERSION}, or "
                                f"{WALK_SESSION_CONTRACT_VERSION}, or "
                                f"{DECLARED_ADAPTER_SESSION_CONTRACT_VERSION}, or "
                                f"{PATCH_SESSION_CONTRACT_VERSION}, or "
                                f"{JUDGMENT_SESSION_CONTRACT_VERSION}"
                            )
                        },
                    }
                ],
            )
        parsed = reader.model_validate(obj, *args, **kwargs)
        normalized = parsed.model_dump(mode="python")
        for case in normalized["cases"]:
            if version == LEGACY_SESSION_CONTRACT_VERSION:
                case["acceptance"] = {
                    "mode": "exact-bytes",
                    "expected_outputs": case["expected_outputs"],
                }
            else:
                acceptance = case["acceptance"]
                case["expected_outputs"] = (
                    acceptance["expected_outputs"] if acceptance["mode"] == "exact-bytes" else ()
                )
        result = super().model_validate(normalized)
        result._profile = profile
        for case in result.cases:
            case._session_version = version
        return result

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
        return cls.model_validate(_contract_json(json_data), *args, **kwargs)

    @model_serializer(mode="wrap")
    def _serialize_wire_version(self, handler):
        document = handler(self)
        if not self.profile.judgments:
            for case in document["cases"]:
                case.pop("judgment_gate", None)
        if not self.profile.patch:
            document.pop("candidate_edits", None)
            document.pop("ranking", None)
            for case in document["cases"]:
                case.pop("reference_root", None)
        else:
            for key in ("candidate_edits", "ranking"):
                if document[key] is None:
                    document.pop(key)
            for case in document["cases"]:
                if case["reference_root"] is None:
                    case.pop("reference_root")
        if not self.profile.declared_adapter:
            document.pop("adapter", None)
        if self.profile.legacy:
            for case in document["cases"]:
                case.pop("acceptance")
        else:
            for case in document["cases"]:
                case.pop("expected_outputs")
                if (
                    self.profile.tests
                    and case["acceptance"]["mode"] == "tests"
                ):
                    case.pop("inputs")
                    case.pop("verify")
                if (
                    not self.profile.walk
                    and case["acceptance"]["mode"] == "transition"
                ):
                    case["acceptance"].pop("walk", None)
        return document

    @model_validator(mode="after")
    def _case_denominator_is_closed(self) -> DataDrivenContract:
        ids = [case.case_id for case in self.cases]
        duplicates = sorted({case_id for case_id in ids if ids.count(case_id) > 1})
        if duplicates:
            raise ValueError(f"duplicate case id(s): {', '.join(duplicates)}")
        if not any(case.role is CaseRole.required for case in self.cases):
            raise ValueError("at least one required case is needed; zero would accept vacuously")
        # A pathless expected output binds no file, so it contributes no bytes
        # to the aggregate cap and declares no size to add.
        bound_fields = []
        for case in self.cases:
            bound_fields.extend((*case.inputs, *case.expected_outputs))
            if case.verify is not None:
                bound_fields.append(case.verify.model)
        total_bound_bytes = sum(
            bound.size_bytes for bound in bound_fields if bound.size_bytes is not None
        )
        if total_bound_bytes > MAX_SESSION_BOUND_BYTES:
            raise ValueError(
                f"contract declares {total_bound_bytes} bound bytes, over the "
                f"{MAX_SESSION_BOUND_BYTES}-byte aggregate cap"
            )
        return self

    @property
    def required_cases(self) -> tuple[SessionCase, ...]:
        """Required cases in their contract order."""

        return tuple(case for case in self.cases if case.role is CaseRole.required)


def _issue(path: str, message: str) -> ValidationIssue:
    return ValidationIssue(path=path, message=message, rule_id=SESSION_CONTRACT_RULE_ID)


def _reason_issue(path: str, message: str, rule_id: str) -> ValidationIssue:
    return ValidationIssue(path=path, message=message, rule_id=rule_id)


def _pydantic_issues(
    error: ValidationError,
    *,
    schema_version: object,
) -> list[ValidationIssue]:
    entries = error.errors()
    if schema_version == SESSION_CONTRACT_VERSION:
        custom = [entry for entry in entries if entry["type"] in _V3_ERROR_RULES]
        non_cascading_shape = [
            entry
            for entry in entries
            if entry["type"] not in _V3_ERROR_RULES
            and not (entry["loc"] == ("cases",) and entry["type"] == "too_short")
        ]
        entries = non_cascading_shape or custom
    return [
        _reason_issue(
            ".".join(str(part) for part in entry["loc"]),
            entry["msg"],
            (
                _V3_ERROR_RULES.get(entry["type"], CONTRACT_SHAPE_REASON)
                if schema_version
                not in (
                    LEGACY_SESSION_CONTRACT_VERSION,
                    V2_SESSION_CONTRACT_VERSION,
                )
                else SESSION_CONTRACT_RULE_ID
            ),
        )
        for entry in entries
    ]


def _contract_json(raw):
    document = _rf7_input.loads(raw)
    if isinstance(document, dict) and (profile := profile_for_version(document.get("schema_version"))) is not None and profile.patch:
        from gnd.json_input import bounded_json

        document = bounded_json(
            raw.encode() if isinstance(raw, str) else raw, max_bytes=MAX_SESSION_CONTRACT_BYTES
        )
    return document


def _read_contract_document(path: Path, root: Path) -> object:
    """Read the contract through a no-follow leaf descriptor under ``root``."""

    try:
        relative = path.absolute().relative_to(root.absolute()).as_posix()
    except (OSError, ValueError) as error:
        raise SessionContractError(
            f"session contract {path} is outside experiment root {root}",
            [_issue(str(path), "contract path must remain inside the experiment root")],
        ) from error

    anchor = root / ".session-contract-anchor"
    try:
        with open_manifest_relative_path(
            anchor,
            relative,
            field="session_contract",
            rule_id=SESSION_CONTRACT_RULE_ID,
        ) as (_, stream):
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise OSError("contract is not a regular file")
            if info.st_size > MAX_SESSION_CONTRACT_BYTES:
                raise SessionContractError(
                    f"session contract is over the {MAX_SESSION_CONTRACT_BYTES}-byte cap",
                    [
                        _issue(
                            str(path),
                            f"contract size {info.st_size} exceeds "
                            f"{MAX_SESSION_CONTRACT_BYTES} bytes",
                        )
                    ],
                )
            raw = stream.read(MAX_SESSION_CONTRACT_BYTES + 1)
    except SessionContractError:
        raise
    except ManifestError as error:
        raise SessionContractError(str(error), list(error.issues)) from error
    except OSError as error:
        raise SessionContractError(
            f"session contract {path} could not be read safely: {error}",
            [_issue(str(path), str(error))],
        ) from error

    text = ""
    try:
        text = raw.decode("utf-8")
        if (
            '"schema_version"' in text
            and isinstance(document := _rf7_input.loads(text), dict)
            and (profile := profile_for_version(document.get("schema_version"))) is not None and profile.patch
        ):
            return _contract_json(text)
        return _rf7_input.loads(
            text,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON number {token!r} is forbidden")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, RecursionError) as error:
        issue_path = "wall_seconds" if '"wall_seconds"' in text else str(path)
        raise SessionContractError(
            f"session contract {path} is not strict UTF-8 JSON: {error}",
            [_issue(issue_path, str(error))],
        ) from error


def _bound_fields(contract: DataDrivenContract):
    for case_index, case in enumerate(contract.cases):
        prefix = f"cases.{case_index}"
        for index, bound in enumerate(case.inputs):
            yield f"{prefix}.inputs.{index}", bound
        for index, bound in enumerate(case.expected_outputs):
            # A pathless expectation binds no file: there is nothing to open,
            # contain, or digest-recompute. Its sha256 is checked against the
            # candidate at acceptance time instead.
            if bound.path is None:
                continue
            outputs_field = (
                "expected_outputs"
                if contract.schema_version == LEGACY_SESSION_CONTRACT_VERSION
                else "acceptance.expected_outputs"
            )
            yield f"{prefix}.{outputs_field}.{index}", bound
        if case.verify is not None:
            yield f"{prefix}.verify.model", case.verify.model


def _protected_issue(field: str, message: str, rule_id: str) -> ValidationIssue:
    return _reason_issue(field, message, rule_id)


def _verify_protected_file(
    root_fd: int,
    field: str,
    bound: ProtectedPath | DigestBoundPath,
) -> ValidationIssue | None:
    """Check one candidate seal relative to the already-open candidate root."""

    if manifest_path_issue(f"{field}.path", bound.path, TESTS_PROTECTED_DIGEST_REASON):
        return _protected_issue(
            f"{field}.path",
            "protected path must be a normalized project-relative path",
            TESTS_PROTECTED_DIGEST_REASON,
        )

    parts = PurePosixPath(bound.path).parts
    current_fd = os.dup(root_fd)
    try:
        for index, part in enumerate(parts):
            try:
                info = os.stat(part, dir_fd=current_fd, follow_symlinks=False)
            except OSError as error:
                return _protected_issue(
                    f"{field}.path",
                    f"protected path could not be inspected: {error}",
                    TESTS_PROTECTED_DIGEST_REASON,
                )
            if stat.S_ISLNK(info.st_mode):
                return _protected_issue(
                    f"{field}.path",
                    f"protected path has symlink component {index}: {part}",
                    TESTS_PROTECTED_SYMLINK_REASON,
                )
            final = index == len(parts) - 1
            if not final and not stat.S_ISDIR(info.st_mode):
                return _protected_issue(
                    f"{field}.path",
                    f"protected intermediate component {index} is not a directory",
                    TESTS_PROTECTED_DIGEST_REASON,
                )
            if final and not stat.S_ISREG(info.st_mode):
                return _protected_issue(
                    f"{field}.path",
                    "protected final entry is not a regular file",
                    TESTS_PROTECTED_SYMLINK_REASON,
                )

            flags = os.O_RDONLY | os.O_NOFOLLOW
            if not final:
                flags |= os.O_DIRECTORY
            else:
                flags |= os.O_NONBLOCK
            try:
                next_fd = os.open(part, flags, dir_fd=current_fd)
            except OSError as error:
                return _protected_issue(
                    f"{field}.path",
                    f"protected path could not be opened safely: {error}",
                    TESTS_PROTECTED_DIGEST_REASON,
                )
            opened = os.fstat(next_fd)
            if (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
                os.close(next_fd)
                return _protected_issue(
                    f"{field}.path",
                    "protected path changed while it was being opened",
                    TESTS_PROTECTED_DIGEST_REASON,
                )
            os.close(current_fd)
            current_fd = next_fd

        digest = hashlib.sha256()
        while chunk := os.read(current_fd, 1024 * 1024):
            digest.update(chunk)
    except OSError as error:
        return _protected_issue(
            f"{field}.path",
            f"protected path could not be read safely: {error}",
            TESTS_PROTECTED_DIGEST_REASON,
        )
    finally:
        os.close(current_fd)

    actual = digest.hexdigest()
    if actual != bound.sha256:
        return _protected_issue(
            f"{field}.sha256",
            f"declared {bound.sha256} but observed {actual}",
            TESTS_PROTECTED_DIGEST_REASON,
        )
    return None


def _open_protected_root(candidate_root: Path) -> tuple[int | None, ValidationIssue | None]:
    """Open and pin the candidate root before inspecting protected entries."""

    field = "candidate"
    try:
        before = os.lstat(candidate_root)
        if stat.S_ISLNK(before.st_mode):
            return None, _protected_issue(
                field,
                "candidate root is a symlink",
                TESTS_PROTECTED_SYMLINK_REASON,
            )
        if not stat.S_ISDIR(before.st_mode):
            return None, _protected_issue(
                field,
                "candidate root is not a directory",
                TESTS_PROTECTED_DIGEST_REASON,
            )
        root_fd = os.open(
            candidate_root,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
        )
        opened = os.fstat(root_fd)
        if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            os.close(root_fd)
            return None, _protected_issue(
                field,
                "candidate root changed while it was being opened",
                TESTS_PROTECTED_DIGEST_REASON,
            )
    except OSError as error:
        return None, _protected_issue(
            field,
            f"candidate root could not be opened safely: {error}",
            TESTS_PROTECTED_DIGEST_REASON,
        )
    return root_fd, None


def _tests_declaration_issues(
    contract: DataDrivenContract,
    *,
    candidate_root: Path,
) -> list[ValidationIssue]:
    """Apply v3 cross-row and filesystem-backed rules in specified order."""

    issues: list[ValidationIssue] = []
    test_cases = [
        (case_index, case.acceptance)
        for case_index, case in enumerate(contract.cases)
        if isinstance(case.acceptance, TestsAcceptance)
    ]
    if not test_cases:
        return issues

    for case_index, acceptance in test_cases:
        protected_by_path = {entry.path: entry for entry in acceptance.protected}
        required_paths = {_test_path(identifier) for identifier in acceptance.required_tests}
        uncovered = sorted(path for path in required_paths if path not in protected_by_path)
        if uncovered:
            issues.append(
                _reason_issue(
                    f"cases.{case_index}.acceptance.protected",
                    "required test path(s) are not protected: " + ", ".join(uncovered),
                    TESTS_PROTECTED_UNCOVERED_REASON,
                )
            )

    # Coverage is a declaration check. Resolve every coverage fault before the
    # first filesystem lookup so shape/declaration ordering is deterministic.
    if issues:
        return issues

    root_fd, root_issue = _open_protected_root(candidate_root)
    if root_issue is not None:
        return [root_issue]
    assert root_fd is not None
    try:
        for case_index, acceptance in test_cases:
            for protected_index, protected in enumerate(acceptance.protected):
                issue = _verify_protected_file(
                    root_fd,
                    f"cases.{case_index}.acceptance.protected.{protected_index}",
                    protected,
                )
                if issue is not None:
                    issues.append(issue)
    finally:
        os.close(root_fd)
    return issues


def _verify_bound_file(root: Path, field: str, bound: DigestBoundPath) -> list[ValidationIssue]:
    anchor = root / ".session-contract-anchor"
    try:
        with open_manifest_relative_path(
            anchor,
            bound.path,
            field=f"{field}.path",
            rule_id=SESSION_CONTRACT_RULE_ID,
        ) as (_, stream):
            info = os.fstat(stream.fileno())
            if info.st_size > MAX_SESSION_INPUT_BYTES:
                return [
                    _issue(
                        f"{field}.size_bytes",
                        f"file is {info.st_size} bytes, over the "
                        f"{MAX_SESSION_INPUT_BYTES}-byte cap",
                    )
                ]
            digest = hashlib.sha256()
            observed = 0
            while chunk := stream.read(1024 * 1024):
                observed += len(chunk)
                digest.update(chunk)
    except ManifestError as error:
        return list(error.issues)
    except OSError as error:
        return [_issue(f"{field}.path", str(error))]

    issues: list[ValidationIssue] = []
    if observed != bound.size_bytes:
        issues.append(
            _issue(
                f"{field}.size_bytes",
                f"declared {bound.size_bytes} bytes but observed {observed}",
            )
        )
    actual = digest.hexdigest()
    if actual != bound.sha256:
        issues.append(
            _issue(
                f"{field}.sha256",
                f"declared {bound.sha256} but observed {actual}",
            )
        )
    return issues


def read_session_contract(
    path: str | Path,
    *,
    experiment_root: str | Path,
    experiment_id: str,
) -> DataDrivenContract:
    """Load, close, path-check, and recompute every contract byte binding."""

    file_path = Path(path)
    root = Path(experiment_root)
    document = _read_contract_document(file_path, root)
    schema_version = document.get("schema_version") if isinstance(document, dict) else None
    try:
        contract = DataDrivenContract.model_validate(document)
    except ValidationError as error:
        issues = _pydantic_issues(error, schema_version=schema_version)
        raise SessionContractError(
            f"{file_path} is not a valid data-driven session contract",
            issues,
        ) from error
    except Exception as error:
        rule_id = (
            CONTRACT_SHAPE_REASON
            if schema_version
            in {
                SESSION_CONTRACT_VERSION,
                WALK_SESSION_CONTRACT_VERSION,
                DECLARED_ADAPTER_SESSION_CONTRACT_VERSION,
            }
            else SESSION_CONTRACT_RULE_ID
        )
        raise SessionContractError(
            f"{file_path} is not a valid data-driven session contract",
            [_reason_issue(str(file_path), str(error), rule_id)],
        ) from error

    issues: list[ValidationIssue] = []
    if contract.experiment_id != experiment_id:
        issues.append(
            _reason_issue(
                "experiment_id",
                f"contract declares {contract.experiment_id!r}, but the trusted caller "
                f"selected {experiment_id!r}",
                (
                    CONTRACT_SHAPE_REASON
                    if contract.schema_version
                    in {
                        SESSION_CONTRACT_VERSION,
                        WALK_SESSION_CONTRACT_VERSION,
                        DECLARED_ADAPTER_SESSION_CONTRACT_VERSION,
                    }
                    else SESSION_CONTRACT_RULE_ID
                ),
            )
        )

    for field, bound in _bound_fields(contract):
        if path_issue := manifest_path_issue(
            f"{field}.path",
            bound.path,
            SESSION_CONTRACT_RULE_ID,
        ):
            issues.append(path_issue)
        else:
            issues.extend(_verify_bound_file(root, field, bound))
    loaded_models: dict[str, Any] = {}
    if not issues:
        from gnd.artifacts import read_regular_bounded
        from gnd.model import MAX_MODEL_BYTES, load_model_bytes

        for case in contract.cases:
            if case.verify is None:
                continue
            model_path = case.verify.model.path
            try:
                selected_model = loaded_models.get(model_path)
                if selected_model is None:
                    raw, _snapshot = read_regular_bounded(
                        root, model_path, max_bytes=MAX_MODEL_BYTES
                    )
                    selected_model = load_model_bytes(raw, source=model_path)
            except Exception as error:
                raise SessionContractError("session model input could not be validated") from error
            if selected_model.reference_populations:
                if (
                    not contract.profile.patch
                    or case.reference_root is None
                ):
                    raise SessionContractError(
                        "session contracts do not support unbound reference populations"
                    )
                from gnd.references import bind_references

                try:
                    selected_model._references = bind_references(
                        selected_model, root=root / case.reference_root
                    )
                except Exception as error:
                    raise SessionContractError("session references could not be bound") from error
                if contract.candidate_edits is not None:
                    targets = [
                        contract.candidate_edits.patch_path,
                        *(a.path for a in contract.candidate_edits.artifacts),
                    ]
                    protected = [
                        str(PurePosixPath(model_path).parent / path)
                        for _origin, path, _raw in selected_model._references._snapshots
                    ]
                    if any(
                        a == b or a.startswith(b + "/") or b.startswith(a + "/")
                        for a in targets
                        for b in protected
                    ):
                        raise SessionContractError("candidate declaration overlaps bound reference")
            elif (
                contract.schema_version == PATCH_SESSION_CONTRACT_VERSION
                and case.reference_root is not None
            ):
                raise SessionContractError("reference_root requires model references")
            loaded_models[model_path] = selected_model
    model_fact_types: dict[str, set[str]] = {}
    for index, case in enumerate(contract.cases):
        if isinstance(case.verify, VerifyCase) and (
            path_issue := manifest_path_issue(
                f"cases.{index}.verify.subject",
                case.verify.subject,
                SESSION_CONTRACT_RULE_ID,
            )
        ):
            issues.append(path_issue)
        # A candidate-relative path is a lexical claim, so it is checked at read
        # time beside verify.subject; containment is the write gate's business.
        for output_index, output in enumerate(case.expected_outputs):
            outputs_field = (
                "expected_outputs"
                if contract.schema_version == LEGACY_SESSION_CONTRACT_VERSION
                else "acceptance.expected_outputs"
            )
            if path_issue := manifest_path_issue(
                f"cases.{index}.{outputs_field}.{output_index}.candidate_path",
                output.candidate_path,
                SESSION_CONTRACT_RULE_ID,
            ):
                issues.append(path_issue)
        if isinstance(case.acceptance, ConstraintSatisfactionAcceptance):
            assert case.verify is not None
            model_path = case.verify.model.path
            if model_path not in model_fact_types:
                try:
                    model = load_model(root / model_path)
                    if model.reference_populations and not contract.profile.patch:
                        raise SessionContractError(
                            "session contracts do not support reference populations"
                        )
                except (OSError, ModelLoadError, ModelValidationError) as error:
                    issues.append(
                        _issue(
                            f"cases.{index}.verify.model.path",
                            f"coverage model could not be loaded: {error}",
                        )
                    )
                    continue
                model_fact_types[model_path] = {fact_type["id"] for fact_type in model.fact_types}
            known = model_fact_types[model_path]
            for floor_index, floor in enumerate(case.acceptance.coverage):
                if floor.fact_type not in known:
                    issues.append(
                        _issue(
                            f"cases.{index}.acceptance.coverage.{floor_index}.fact_type",
                            f"unknown model fact type {floor.fact_type!r}",
                        )
                    )
        if (
            contract.schema_version
            in {
                WALK_SESSION_CONTRACT_VERSION,
                DECLARED_ADAPTER_SESSION_CONTRACT_VERSION,
                PATCH_SESSION_CONTRACT_VERSION,
                8,
            }
            and isinstance(case.acceptance, TransitionAcceptance)
            and case.acceptance.walk is not None
        ):
            assert isinstance(case.verify, TransitionVerifyCase)
            model_path = case.verify.model.path
            if model_path not in loaded_models:
                try:
                    loaded_models[model_path] = load_model(root / model_path)
                    if loaded_models[
                        model_path
                    ].reference_populations and not contract.profile.patch:
                        raise SessionContractError(
                            "session contracts do not support reference populations"
                        )
                except (OSError, ModelLoadError, ModelValidationError) as error:
                    issues.append(
                        _issue(
                            f"cases.{index}.verify.model.path",
                            f"walk-floor model could not be loaded: {error}",
                        )
                    )
                    continue
            model = loaded_models[model_path]
            from gnd.transition import _operations_by_id, operation_binding_issues

            declared = _operations_by_id(model)
            for floor_index, floor in enumerate(case.acceptance.walk.required_ops):
                issues.extend(
                    operation_binding_issues(
                        model,
                        declared=declared,
                        operation_id=floor.op,
                        bindings=floor.bindings_subset,
                        operation_path=(
                            f"cases.{index}.acceptance.walk.required_ops.{floor_index}.op"
                        ),
                        bindings_path=(
                            "cases."
                            f"{index}.acceptance.walk.required_ops.{floor_index}.bindings_subset"
                        ),
                        subject=f"required operation {floor_index}",
                        require_exact=False,
                    )
                )
            for forbidden_index, operation_id in enumerate(case.acceptance.walk.forbidden_ops):
                issues.extend(
                    operation_binding_issues(
                        model,
                        declared=declared,
                        operation_id=operation_id,
                        bindings={},
                        operation_path=(
                            f"cases.{index}.acceptance.walk.forbidden_ops.{forbidden_index}"
                        ),
                        bindings_path=(
                            f"cases.{index}.acceptance.walk.forbidden_ops.{forbidden_index}"
                        ),
                        subject=f"forbidden operation {forbidden_index}",
                        require_exact=False,
                    )
                )

    if (
        contract.schema_version
        in {
            SESSION_CONTRACT_VERSION,
            TRANSITION_SESSION_CONTRACT_VERSION,
            WALK_SESSION_CONTRACT_VERSION,
            DECLARED_ADAPTER_SESSION_CONTRACT_VERSION,
        }
        and not issues
    ):
        issues.extend(_tests_declaration_issues(contract, candidate_root=root / "candidate"))

    if issues:
        raise SessionContractError(
            f"{file_path} failed session contract integrity validation",
            issues,
        )
    return contract
