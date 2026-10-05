"""Append-only, digest-linked evidence for programmatic experiment sessions.

The mutable candidate directory crosses a trust boundary here.  It is walked
through directory descriptors without following links, bounded before it is
retained, and copied into a private staging directory for verifier execution.
Complete attempt evidence is then copied through a descriptor-bound,
append-only destination, with ``attempt.json`` written last as its commit
marker.

``best.json`` and ``result.json`` are deliberately different claims.  The
former is a replaceable pointer to one immutable attempt; the latter is an
append-once terminal statement.  Neither substitutes for the candidate or raw
bytes to which the attempt manifest points.
"""

from __future__ import annotations

import json
import math
import mimetypes
import os
import secrets
import shutil
import stat
from collections.abc import Mapping
from contextlib import suppress
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Annotated, Any, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
    field_validator,
    model_serializer,
    model_validator,
)

from gnd.agent_cli import AgentAdapterId, InvocationResult
from gnd.artifacts import (
    ArtifactError,
    LeafSnapshot,
    _clear_directory_fd,
    _exchange_paths_atomic,
    _read_regular_bounded_fd,
    canonical_json_bytes,
    publish_directory_once,
    publish_leaf_atomic,
    read_regular_bounded,
    sha256_hex,
    tree_sha256_from_inventory,
)
from gnd.assurance_transport import ArchivedAssuranceReceipt
from gnd.exp.declared_invocation import DeclaredInvocationResult
from gnd.exp.session_contract import (
    DataDrivenContract,
    RankingMetric,
    TestsAcceptance,
    TransitionAcceptance,
)
from gnd.exp.session_eval import (
    AttemptEvaluation,
    AttemptFeedback,
    SessionRedaction,
    VerifierPayloadError,
    attach_walk_floor_steps,
    best_key,
    canonical_feedback,
    normalized_verifier_signature,
    validate_tests_payload,
    validate_transition_payload,
    validate_verifier_payload,
)
from gnd.report import MODEL_BOUND_PAYLOAD_SCHEMA_VERSIONS, PAYLOAD_SCHEMA_VERSION

__all__ = [
    "MAX_SESSION_RESULT_BYTES",
    "AttemptRecord",
    "CandidateFile",
    "CandidateInventory",
    "DeclaredLaunchIntent",
    "LaunchIntent",
    "ResumeState",
    "SessionOutcome",
    "SessionResult",
    "SessionStore",
    "StagedCandidate",
    "WalkFloorResult",
]

FIXED_STORE_SCHEMA_VERSION = 1
LEGACY_EVIDENCE_SCHEMA_VERSION = 1
EVIDENCE_SCHEMA_VERSION = 2
#: v5.0 Phase 3 (r2 A8): the evidence version whose feedback carries the
#: derivation repair rows. Selected exactly when a case's model selects
#: report schema version 4; every other session keeps version 2 bytes.
DERIVATION_EVIDENCE_SCHEMA_VERSION = 3
ASSURANCE_EVIDENCE_SCHEMA_VERSION = 4
TRANSITION_EVIDENCE_SCHEMA_VERSION = 5
REDACTION_EVIDENCE_SCHEMA_VERSION = 6
WALK_FLOOR_EVIDENCE_SCHEMA_VERSION = 7
DECLARED_ADAPTER_EVIDENCE_SCHEMA_VERSION = 8
DECLARED_LAUNCH_SCHEMA_VERSION = 2
TRANSITION_RESULT_SCHEMA_VERSION = 3
REDACTION_RESULT_SCHEMA_VERSION = 4
WALK_FLOOR_RESULT_SCHEMA_VERSION = 5
MAX_CANDIDATE_FILES = 10_000
MAX_CANDIDATE_FILE_BYTES = 10 * 1024 * 1024
MAX_CANDIDATE_TOTAL_BYTES = 100 * 1024 * 1024
MAX_CANDIDATE_DEPTH = 64

MAX_RETAINED_STREAM_BYTES = 10 * 1024 * 1024
MAX_VERIFIER_PAYLOAD_BYTES = 10 * 1024 * 1024
#: Read cap for a committed ``result.json`` consumed as UNTRUSTED metadata
#: (the close gate reads it long after the run that wrote it). Sized to the
#: retained-evidence caps above: a terminal result that outgrew the payload
#: cap could not have been written by this store's own lane.
MAX_SESSION_RESULT_BYTES = 10 * 1024 * 1024
FILE_MODE = 0o644
SNAPSHOT_FILE_MODE = 0o444


def _evidence_entry(path: str, raw: bytes) -> dict[str, object]:
    """Declare producer bytes at the caller's version-specific coordinate."""
    return {"path": path, "sha256": sha256_hex(raw), "size_bytes": len(raw)}


def _version_validation_error(model_name: str, version: Any) -> ValidationError:
    return ValidationError.from_exception_data(
        model_name,
        [
            {
                "type": "literal_error",
                "loc": ("schema_version",),
                "input": version,
                "ctx": {
                    "expected": (
                        f"{LEGACY_EVIDENCE_SCHEMA_VERSION}, {EVIDENCE_SCHEMA_VERSION}, "
                        f"{DERIVATION_EVIDENCE_SCHEMA_VERSION}, "
                        f"{ASSURANCE_EVIDENCE_SCHEMA_VERSION}, "
                        f"{TRANSITION_EVIDENCE_SCHEMA_VERSION}, "
                        f"{REDACTION_EVIDENCE_SCHEMA_VERSION}, or "
                            f"{WALK_FLOOR_EVIDENCE_SCHEMA_VERSION}, or "
                            f"{DECLARED_ADAPTER_EVIDENCE_SCHEMA_VERSION}"
                    )
                },
            }
        ],
    )


SNAPSHOT_EXECUTABLE_FILE_MODE = 0o555
DIRECTORY_MODE = 0o755

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]


def _strict_object_bytes(data: bytes, *, label: str) -> dict[str, Any]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"{label} is not UTF-8: {error}") from error

    def reject_constant(token: str) -> None:
        raise ValueError(f"non-finite JSON number {token!r} is forbidden")

    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        document: dict[str, Any] = {}
        for key, value in pairs:
            if key in document:
                raise ValueError(f"duplicate JSON key {key!r}")
            document[key] = value
        return document

    decoder = json.JSONDecoder(
        parse_constant=reject_constant,
        object_pairs_hook=reject_duplicates,
    )
    try:
        document, end = decoder.raw_decode(text.lstrip())
    except (json.JSONDecodeError, ValueError, RecursionError) as error:
        raise ValueError(f"{label} is not strict JSON: {error}") from error
    if text.lstrip()[end:].strip():
        raise ValueError(f"{label} contains trailing bytes")
    if not isinstance(document, dict):
        raise ValueError(f"{label} must contain a JSON object")  # noqa: TRY004
    return document


def _create_evidence_parent(
    root: Path,
    parts: tuple[str, ...],
    *,
    expected_identity: tuple[int, int] | None = None,
) -> int:
    """Open/create a contained real directory chain through descriptors."""

    try:
        before = root.lstat()
    except OSError as error:
        raise ValueError(f"evidence root {root} could not be inspected") from error
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISDIR(before.st_mode):
        raise ValueError(f"evidence root {root} must be a real directory")
    flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    current = os.open(root, flags)
    opened = os.fstat(current)
    if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
        os.close(current)
        raise ValueError(f"evidence root {root} changed before it opened")
    if expected_identity is not None and (
        opened.st_dev,
        opened.st_ino,
    ) != expected_identity:
        os.close(current)
        raise ValueError(f"evidence root {root} changed from its expected identity")
    try:
        for part in parts:
            try:
                os.mkdir(part, DIRECTORY_MODE, dir_fd=current)
            except FileExistsError:
                pass
            else:
                os.fsync(current)
            info = os.stat(part, dir_fd=current, follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
                raise ValueError(f"evidence directory component {part!r} is not real")
            child = os.open(part, flags, dir_fd=current)
            child_opened = os.fstat(child)
            if (child_opened.st_dev, child_opened.st_ino) != (
                info.st_dev,
                info.st_ino,
            ):
                os.close(child)
                raise ValueError(
                    f"evidence directory component {part!r} changed before it opened"
                )
            os.close(current)
            current = child
    except BaseException:
        os.close(current)
        raise
    return current


def _write_new_file(
    path: Path,
    data: bytes,
    *,
    root: Path | None = None,
    mode: int = FILE_MODE,
    expected_root: tuple[int, int] | None = None,
) -> None:
    """Create one regular evidence leaf, refusing every existing leaf.

    Parent directories are private store-owned directories.  The leaf itself is
    opened with ``O_EXCL`` and ``O_NOFOLLOW`` so an existing file or symlink can
    never be overwritten or traversed.
    """

    evidence_root = path.parent if root is None else root
    try:
        relative = path.absolute().relative_to(evidence_root.absolute())
    except ValueError as error:
        raise ValueError(f"evidence leaf {path} escapes its staging root") from error
    parts = PurePosixPath(relative.as_posix()).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ValueError("evidence leaf path is not a normalized relative path")
    parent_fd = _create_evidence_parent(
        evidence_root,
        parts[:-1],
        expected_identity=expected_root,
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(parts[-1], flags, mode, dir_fd=parent_fd)
    except BaseException:
        os.close(parent_fd)
        raise
    try:
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = -1
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.fsync(parent_fd)
    finally:
        if descriptor >= 0:  # pragma: no cover - fdopen normally owns it
            os.close(descriptor)
        os.close(parent_fd)


class CandidateFile(BaseModel):
    """One regular file in an immutable candidate tree."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    path: NonEmptyString
    media_type: NonEmptyString
    encoding: NonEmptyString | None
    size_bytes: int = Field(ge=0)
    sha256: Sha256
    executable: bool = False

    @field_validator("path")
    @classmethod
    def _path_is_relative(cls, value: str) -> str:
        posix = PurePosixPath(value)
        if (
            posix.is_absolute()
            or not posix.parts
            or any(part in {"", ".", ".."} for part in posix.parts)
        ):
            raise ValueError("candidate file path must be a normalized relative path")
        return posix.as_posix()


class CandidateInventory(BaseModel):
    """Canonical identity of all regular bytes in one candidate snapshot."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[1] = FIXED_STORE_SCHEMA_VERSION
    files: tuple[CandidateFile, ...]
    file_count: int = Field(ge=0)
    total_bytes: int = Field(ge=0)
    tree_sha256: Sha256

    @model_validator(mode="after")
    def _totals_and_order_are_exact(self) -> Self:
        paths = [entry.path for entry in self.files]
        if paths != sorted(paths):
            raise ValueError("candidate inventory files must be sorted by path")
        if len(paths) != len(set(paths)):
            raise ValueError("candidate inventory contains a duplicate path")
        if self.file_count != len(self.files):
            raise ValueError("candidate file_count does not match files")
        if self.total_bytes != sum(entry.size_bytes for entry in self.files):
            raise ValueError("candidate total_bytes does not match files")
        expected = tree_sha256_from_inventory(self.files)
        if self.tree_sha256 != expected:
            raise ValueError("candidate tree_sha256 does not match files")
        return self


class EvidenceFile(BaseModel):
    """Identity of one raw evidence leaf retained under an attempt."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    path: NonEmptyString
    size_bytes: int = Field(ge=0)
    sha256: Sha256


class VerifierPayloadEvidence(EvidenceFile):
    case_id: NonEmptyString


class LaunchIntent(BaseModel):
    """Append-once proof that one bounded launch index was consumed."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[1] = FIXED_STORE_SCHEMA_VERSION
    run_id: NonEmptyString
    attempt_index: int = Field(gt=0)
    contract_sha256: Sha256
    policy_sha256: Sha256
    adapter: AgentAdapterId
    base_prompt_sha256: Sha256
    controller_prompt_sha256: Sha256
    effective_prompt_sha256: Sha256
    feedback_sha256: Sha256 | None = None
    candidate_inventory: CandidateInventory
    candidate_inventory_sha256: Sha256
    candidate_sha256: Sha256

    @model_validator(mode="after")
    def _candidate_identity_is_exact(self) -> Self:
        if self.candidate_inventory_sha256 != sha256_hex(
            canonical_json_bytes(self.candidate_inventory)
        ):
            raise ValueError("launch candidate inventory digest is stale")
        if self.candidate_sha256 != self.candidate_inventory.tree_sha256:
            raise ValueError("launch candidate tree digest is stale")
        return self


class DeclaredLaunchIntent(BaseModel):
    """Append-once launch identity for one schema-v6 declared adapter."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[DECLARED_LAUNCH_SCHEMA_VERSION] = DECLARED_LAUNCH_SCHEMA_VERSION
    run_id: NonEmptyString
    attempt_index: int = Field(gt=0)
    contract_sha256: Sha256
    policy_id: NonEmptyString
    policy_kind: Literal["command", "openai-compatible"]
    policy_sha256: Sha256
    model_sha256: Sha256 | None = None
    base_prompt_sha256: Sha256
    controller_prompt_sha256: Sha256
    effective_prompt_sha256: Sha256
    feedback_sha256: Sha256 | None = None
    candidate_inventory: CandidateInventory
    candidate_inventory_sha256: Sha256
    candidate_sha256: Sha256

    @model_validator(mode="after")
    def _candidate_identity_is_exact(self) -> Self:
        if self.candidate_inventory_sha256 != sha256_hex(
            canonical_json_bytes(self.candidate_inventory)
        ):
            raise ValueError("launch candidate inventory digest is stale")
        if self.candidate_sha256 != self.candidate_inventory.tree_sha256:
            raise ValueError("launch candidate tree digest is stale")
        return self


_DeclaredLaunchIntentV2 = DeclaredLaunchIntent


class _DeclaredLaunchIntentV3(_DeclaredLaunchIntentV2):
    schema_version: Literal[3] = 3


class _DeclaredLaunchIntentV4(_DeclaredLaunchIntentV3):
    schema_version: Literal[4]
    judgment_policy_sha256: dict[str, Sha256]


class DeclaredLaunchIntent(_DeclaredLaunchIntentV2):
    schema_version: Literal[2, 3, 4] = 2
    judgment_policy_sha256: dict[str, Sha256] = Field(default_factory=dict)

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        if isinstance(obj, cls):
            return obj
        reader = (
            _DeclaredLaunchIntentV4
            if isinstance(obj, dict) and obj.get("schema_version") == 4
            else _DeclaredLaunchIntentV3
            if isinstance(obj, dict) and obj.get("schema_version") == 3
            else _DeclaredLaunchIntentV2
        )
        return super().model_validate(
            reader.model_validate(obj, *args, **kwargs).model_dump(mode="python")
        )

    @classmethod
    def model_validate_json(cls, raw, *args, **kwargs):
        return cls.model_validate(json.loads(raw), *args, **kwargs)

    @model_serializer(mode="wrap")
    def _wire(self, handler):
        doc = handler(self)
        if self.schema_version != 4:
            doc.pop("judgment_policy_sha256")
        return doc


class CandidateEdit(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    mode: Literal["complete", "patch"]
    patch_path: str
    patch_raw_sha256: Sha256 | None
    base_candidate_sha256: Sha256 | None
    result_candidate_sha256: Sha256 | None
    refusal: (
        Literal[
            "shape",
            "limit",
            "stale-base",
            "protected",
            "path",
            "keys",
            "conflict",
            "missing-delete",
            "publication",
        ]
        | None
    )

    @model_validator(mode="after")
    def _proposal_evidence_is_complete(self):
        if self.refusal is None and (
            self.patch_raw_sha256 is None or self.result_candidate_sha256 is None
        ):
            raise ValueError("successful proposal requires replay evidence and result identity")
        if self.refusal is not None and self.result_candidate_sha256 is not None:
            raise ValueError("refused proposal cannot claim a result identity")
        return self


class RankingObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    metric: Literal[
        "accepted_required_cases",
        "candidate_admitted_unique",
        "alethic_failures",
        "alethic_indeterminate",
        "coverage_shortfall",
    ]
    direction: Literal["min", "max"]
    available: bool
    value: int | None

    @model_validator(mode="after")
    def _availability(self):
        if self.available != (self.value is not None):
            raise ValueError("metric availability and value differ")
        return self


class _AttemptRecordBase(BaseModel):
    """Fields shared by the two immutable attempt wire readers."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: NonEmptyString
    attempt_index: int = Field(gt=0)
    elapsed_seconds: float = Field(ge=0, allow_inf_nan=False)
    launch_intent: EvidenceFile
    invocation: InvocationResult
    candidate_inventory: CandidateInventory
    candidate_inventory_sha256: Sha256
    candidate_snapshot: NonEmptyString
    agent_stdout: EvidenceFile
    agent_stderr: EvidenceFile
    raw_verifier_payloads: tuple[VerifierPayloadEvidence, ...]
    evaluation: AttemptEvaluation
    feedback: EvidenceFile
    best_eligible: bool
    evidence_digests: dict[str, Sha256]

    @model_validator(mode="after")
    def _bindings_are_current(self) -> Self:
        if self.evaluation.attempt_index != self.attempt_index:
            raise ValueError("evaluation attempt_index does not match attempt record")
        if self.evaluation.candidate_sha256 != self.candidate_inventory.tree_sha256:
            raise ValueError("evaluation candidate digest does not match candidate inventory")
        case_ids = [entry.case_id for entry in self.raw_verifier_payloads]
        if case_ids != sorted(case_ids) or len(case_ids) != len(set(case_ids)):
            raise ValueError("raw verifier payloads must be uniquely sorted by case id")
        return self


class _AttemptRecordV1(_AttemptRecordBase):
    """Frozen schema-v1 attempt reader."""

    schema_version: Literal[LEGACY_EVIDENCE_SCHEMA_VERSION]


class _AttemptRecordV2(_AttemptRecordBase):
    """Strict schema-v2 attempt reader with an explicit feedback binding."""

    schema_version: Literal[EVIDENCE_SCHEMA_VERSION]
    feedback_schema_version: Literal[2]


class _AttemptRecordV3(_AttemptRecordBase):
    """Strict schema-v3 attempt reader: the v2 shape binding v3 feedback.

    v5.0 Phase 3 (r2 A8): an attempt whose feedback carries derivation repair
    rows takes the next evidence version, exactly as the feedback wire does,
    so a v2 consumer can never half-read one.
    """

    schema_version: Literal[DERIVATION_EVIDENCE_SCHEMA_VERSION]
    feedback_schema_version: Literal[3]


class _AttemptRecordV4(_AttemptRecordBase):
    """Version 4 preserves the explicit assurance feedback binding."""

    schema_version: Literal[ASSURANCE_EVIDENCE_SCHEMA_VERSION]
    feedback_schema_version: Literal[4]
    assurance_receipts: tuple[ArchivedAssuranceReceipt, ...]


class _AttemptRecordV5(_AttemptRecordV4):
    """Version 5 binds the answer-free transition feedback wire."""

    schema_version: Literal[TRANSITION_EVIDENCE_SCHEMA_VERSION]
    feedback_schema_version: Literal[TRANSITION_EVIDENCE_SCHEMA_VERSION]


class _AttemptRecordV6(_AttemptRecordV5):
    """Version 6 binds projected feedback and case-scoped declarations."""

    schema_version: Literal[REDACTION_EVIDENCE_SCHEMA_VERSION]
    feedback_schema_version: Literal[REDACTION_EVIDENCE_SCHEMA_VERSION]
    redaction: SessionRedaction


class _AttemptRecordV7(_AttemptRecordV5):
    """Version 7 binds walk-floor feedback and nullable redaction metadata."""

    schema_version: Literal[WALK_FLOOR_EVIDENCE_SCHEMA_VERSION]
    feedback_schema_version: Literal[WALK_FLOOR_EVIDENCE_SCHEMA_VERSION]
    redaction: SessionRedaction | None


class _AttemptRecordV8(_AttemptRecordBase):
    """Version 8 binds declared-adapter identity without widening v1-v7."""

    schema_version: Literal[DECLARED_ADAPTER_EVIDENCE_SCHEMA_VERSION]
    feedback_schema_version: Literal[2, 3, 4, 5, 6, 7]
    invocation: DeclaredInvocationResult
    assurance_receipts: tuple[ArchivedAssuranceReceipt, ...] = ()
    redaction: SessionRedaction | None = None


class _AttemptRecordV9(_AttemptRecordV8):
    schema_version: Literal[9]
    feedback_schema_version: Literal[8]
    candidate_edit: CandidateEdit | None
    operator_feedback: EvidenceFile
    ranking: tuple[RankingObservation, ...]


class JudgmentEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    policy: EvidenceFile
    receipts: EvidenceFile
    report: EvidenceFile
    sources: tuple[EvidenceFile, ...]


class _AttemptRecordV10(_AttemptRecordV9):
    schema_version: Literal[10]
    feedback_schema_version: Literal[9]
    judgment_evidence: dict[str, JudgmentEvidence]


class AttemptRecord(_AttemptRecordBase):
    """Version-dispatched immutable attempt normalized only in memory."""

    schema_version: Literal[
        LEGACY_EVIDENCE_SCHEMA_VERSION,
        EVIDENCE_SCHEMA_VERSION,
        DERIVATION_EVIDENCE_SCHEMA_VERSION,
        ASSURANCE_EVIDENCE_SCHEMA_VERSION,
        TRANSITION_EVIDENCE_SCHEMA_VERSION,
        REDACTION_EVIDENCE_SCHEMA_VERSION,
        WALK_FLOOR_EVIDENCE_SCHEMA_VERSION,
        DECLARED_ADAPTER_EVIDENCE_SCHEMA_VERSION,
        9,
        10,
    ] = EVIDENCE_SCHEMA_VERSION
    feedback_schema_version: Literal[2, 3, 4, 5, 6, 7, 8, 9] | None = EVIDENCE_SCHEMA_VERSION
    assurance_receipts: tuple[ArchivedAssuranceReceipt, ...] = ()
    redaction: SessionRedaction | None = None
    candidate_edit: CandidateEdit | None = None
    operator_feedback: EvidenceFile | None = None
    ranking: tuple[RankingObservation, ...] = ()
    judgment_evidence: dict[str, JudgmentEvidence] = {}
    invocation: InvocationResult | DeclaredInvocationResult

    @classmethod
    def model_validate(cls, obj: Any, *args: Any, **kwargs: Any) -> Self:
        if isinstance(obj, cls):
            return obj
        version = obj.get("schema_version") if isinstance(obj, dict) else None
        if version == LEGACY_EVIDENCE_SCHEMA_VERSION:
            reader: type[
                _AttemptRecordV1
                | _AttemptRecordV2
                | _AttemptRecordV3
                | _AttemptRecordV4
                | _AttemptRecordV5
                | _AttemptRecordV6
                | _AttemptRecordV7
                | _AttemptRecordV8
            ] = _AttemptRecordV1
        elif version == EVIDENCE_SCHEMA_VERSION:
            reader = _AttemptRecordV2
        elif version == DERIVATION_EVIDENCE_SCHEMA_VERSION:
            reader = _AttemptRecordV3
        elif version == ASSURANCE_EVIDENCE_SCHEMA_VERSION:
            reader = _AttemptRecordV4
        elif version == TRANSITION_EVIDENCE_SCHEMA_VERSION:
            reader = _AttemptRecordV5
        elif version == REDACTION_EVIDENCE_SCHEMA_VERSION:
            reader = _AttemptRecordV6
        elif version == WALK_FLOOR_EVIDENCE_SCHEMA_VERSION:
            reader = _AttemptRecordV7
        elif version == DECLARED_ADAPTER_EVIDENCE_SCHEMA_VERSION:
            reader = _AttemptRecordV8
        elif version == 10:
            reader = _AttemptRecordV10
        elif version == 9:
            reader = _AttemptRecordV9
        else:
            raise _version_validation_error(cls.__name__, version)
        normalized = dict(reader.model_validate(obj, *args, **kwargs).__dict__)
        if version == LEGACY_EVIDENCE_SCHEMA_VERSION:
            normalized["feedback_schema_version"] = None
        return super().model_validate(normalized)

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
        return cls.model_validate(json.loads(json_data), *args, **kwargs)

    @model_serializer(mode="wrap")
    def _serialize_wire_version(self, handler):
        document = handler(self)
        if self.schema_version != 10:
            document.pop("judgment_evidence")
        if self.schema_version not in {9, 10}:
            for key in ("candidate_edit", "operator_feedback", "ranking"):
                document.pop(key)
        if self.schema_version not in {
            ASSURANCE_EVIDENCE_SCHEMA_VERSION,
            TRANSITION_EVIDENCE_SCHEMA_VERSION,
            REDACTION_EVIDENCE_SCHEMA_VERSION,
            WALK_FLOOR_EVIDENCE_SCHEMA_VERSION,
            DECLARED_ADAPTER_EVIDENCE_SCHEMA_VERSION,
            9,
            10,
        }:
            document.pop("assurance_receipts")
        if self.schema_version not in {
            REDACTION_EVIDENCE_SCHEMA_VERSION,
            WALK_FLOOR_EVIDENCE_SCHEMA_VERSION,
            DECLARED_ADAPTER_EVIDENCE_SCHEMA_VERSION,
            9,
            10,
        }:
            document.pop("redaction")
        if self.schema_version == LEGACY_EVIDENCE_SCHEMA_VERSION:
            document.pop("feedback_schema_version")
        return document

    @model_validator(mode="after")
    def _feedback_version_matches_attempt_version(self) -> Self:
        if (
            self.schema_version
            not in {
                ASSURANCE_EVIDENCE_SCHEMA_VERSION,
                TRANSITION_EVIDENCE_SCHEMA_VERSION,
                REDACTION_EVIDENCE_SCHEMA_VERSION,
                WALK_FLOOR_EVIDENCE_SCHEMA_VERSION,
                DECLARED_ADAPTER_EVIDENCE_SCHEMA_VERSION,
                9,
                10,
            }
            and self.assurance_receipts
        ):
            raise ValueError("legacy attempt cannot carry assurance receipts")
        ids = [receipt.case_id for receipt in self.assurance_receipts]
        if ids != sorted(set(ids)):
            raise ValueError("assurance receipts must be uniquely sorted")
        by_case = {row.case_id: row for row in self.evaluation.results}
        for receipt in self.assurance_receipts:
            result = by_case.get(receipt.case_id)
            if result is None or (
                receipt.candidate_sha256 != result.candidate_sha256
                or receipt.contract_sha256 != result.contract_sha256
                or receipt.process_receipt.report_sha256 != result.raw_payload_sha256
                or receipt.process_receipt.execution.band != result.payload_exit
            ):
                raise ValueError("archived assurance receipt has different result bindings")
        if self.schema_version == LEGACY_EVIDENCE_SCHEMA_VERSION:
            if self.feedback_schema_version is not None:
                raise ValueError("schema-v1 attempts cannot carry a v2 feedback binding")
        elif (
            self.schema_version not in {DECLARED_ADAPTER_EVIDENCE_SCHEMA_VERSION, 9, 10}
            and self.feedback_schema_version != self.schema_version
        ):
            raise ValueError(
                "attempt and feedback schema versions must agree (versions 2-4 bind the same feedback version)"
            )
        if self.schema_version == REDACTION_EVIDENCE_SCHEMA_VERSION:
            if self.redaction is None:
                raise ValueError("schema-v6 attempts require session redaction metadata")
        elif (
            self.schema_version
            not in {
                WALK_FLOOR_EVIDENCE_SCHEMA_VERSION,
                DECLARED_ADAPTER_EVIDENCE_SCHEMA_VERSION,
                9,
                10,
            }
            and self.redaction is not None
        ):
            raise ValueError("only schema-v6/v7/v8 attempts carry session redaction metadata")
        return self


class SessionOutcome(StrEnum):
    accepted = "accepted"
    agent_failure = "agent-failure"
    verifier_failure = "verifier-failure"
    budget_exhausted = "budget-exhausted"
    stagnation = "stagnation"
    oscillation = "oscillation"


LegacyAcceptanceMode = Literal["exact-bytes", "constraint-satisfaction", "tests"]
AcceptanceMode = Literal["exact-bytes", "constraint-satisfaction", "tests", "transition"]


class _SessionResultBase(BaseModel):
    """Fields shared by both terminal-result wire readers."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: NonEmptyString
    disposition: SessionOutcome
    terminal_reason: NonEmptyString
    attempt_count: int = Field(gt=0)
    best_attempt: int | None = Field(default=None, gt=0)
    best_attempt_manifest_sha256: Sha256 | None = None
    best_candidate_sha256: Sha256 | None = None
    referenced_evidence_digests: dict[str, Sha256]

    @model_validator(mode="after")
    def _best_identity_is_all_or_nothing(self) -> Self:
        fields = (
            self.best_attempt,
            self.best_attempt_manifest_sha256,
            self.best_candidate_sha256,
        )
        if any(value is None for value in fields) != all(value is None for value in fields):
            raise ValueError(
                "best attempt number, manifest digest, and candidate digest are paired"
            )
        if self.disposition is SessionOutcome.accepted and self.best_attempt is None:
            raise ValueError("an accepted result must identify its best immutable attempt")
        if self.best_attempt is not None and self.best_attempt > self.attempt_count:
            raise ValueError("best_attempt cannot exceed attempt_count")
        return self


class _SessionResultV1(_SessionResultBase):
    """Frozen schema-v1 terminal-result reader."""

    schema_version: Literal[LEGACY_EVIDENCE_SCHEMA_VERSION]


class _SessionResultV2(_SessionResultBase):
    """Strict schema-v2 result reader naming its acceptance semantics."""

    schema_version: Literal[EVIDENCE_SCHEMA_VERSION]
    acceptance_modes: tuple[LegacyAcceptanceMode, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _acceptance_modes_are_unique_and_sorted(self) -> Self:
        if self.acceptance_modes != tuple(sorted(set(self.acceptance_modes))):
            raise ValueError("result acceptance modes must be uniquely sorted")
        return self


class _SessionResultV3(_SessionResultBase):
    """Result wire that can name transition acceptance."""

    schema_version: Literal[TRANSITION_RESULT_SCHEMA_VERSION]
    acceptance_modes: tuple[AcceptanceMode, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _acceptance_modes_are_unique_and_sorted(self) -> Self:
        if self.acceptance_modes != tuple(sorted(set(self.acceptance_modes))):
            raise ValueError("result acceptance modes must be uniquely sorted")
        if "transition" not in self.acceptance_modes:
            raise ValueError("schema_version 3 requires transition acceptance")
        return self


class _SessionResultV4(_SessionResultBase):
    """Current terminal result with required applied redaction metadata."""

    schema_version: Literal[REDACTION_RESULT_SCHEMA_VERSION]
    acceptance_modes: tuple[AcceptanceMode, ...] = Field(min_length=1)
    redaction: SessionRedaction

    @model_validator(mode="after")
    def _acceptance_modes_are_unique_and_sorted(self) -> Self:
        if self.acceptance_modes != tuple(sorted(set(self.acceptance_modes))):
            raise ValueError("result acceptance modes must be uniquely sorted")
        return self


class WalkFloorResult(BaseModel):
    """Canonical declaration/discharge summary for one transition walk floor."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: NonEmptyString
    role: Literal["required", "diagnostic"]
    required_ops: int = Field(ge=0)
    forbidden_ops: int = Field(ge=0)
    discharged: bool

    @model_validator(mode="after")
    def _declaration_is_nonempty(self) -> Self:
        if self.required_ops == 0 and self.forbidden_ops == 0:
            raise ValueError("a walk-floor result must account for at least one declaration")
        return self


class _SessionResultV5(_SessionResultBase):
    """Walk-floor terminal result bound to the exact contract bytes."""

    schema_version: Literal[WALK_FLOOR_RESULT_SCHEMA_VERSION]
    acceptance_modes: tuple[AcceptanceMode, ...] = Field(min_length=1)
    redaction: SessionRedaction | None
    contract_sha256: Sha256
    walk_floors: tuple[WalkFloorResult, ...]

    @model_validator(mode="after")
    def _walk_floor_rows_are_canonical(self) -> Self:
        if self.acceptance_modes != tuple(sorted(set(self.acceptance_modes))):
            raise ValueError("result acceptance modes must be uniquely sorted")
        case_ids = [row.case_id for row in self.walk_floors]
        if case_ids != sorted(case_ids) or len(case_ids) != len(set(case_ids)):
            raise ValueError("walk-floor result rows must be uniquely sorted by case id")
        return self


class _SessionResultV6(_SessionResultV5):
    schema_version: Literal[6]
    ranking_policy: tuple[RankingMetric, ...] | None
    best_ranking: tuple[RankingObservation, ...] | None


class _SessionResultV7(_SessionResultV6):
    schema_version: Literal[7]
    judgment_admission: dict[str, bool] | None


class SessionResult(_SessionResultBase):
    """Version-dispatched append-once terminal claim."""

    schema_version: Literal[
        LEGACY_EVIDENCE_SCHEMA_VERSION,
        EVIDENCE_SCHEMA_VERSION,
        TRANSITION_RESULT_SCHEMA_VERSION,
        REDACTION_RESULT_SCHEMA_VERSION,
        WALK_FLOOR_RESULT_SCHEMA_VERSION,
        6,
        7,
    ] = EVIDENCE_SCHEMA_VERSION
    acceptance_modes: tuple[AcceptanceMode, ...] = ("exact-bytes",)
    redaction: SessionRedaction | None = None
    contract_sha256: Sha256 | None = None
    walk_floors: tuple[WalkFloorResult, ...] = ()
    judgment_admission: dict[str, bool] | None = None
    ranking_policy: tuple[RankingMetric, ...] | None = None
    best_ranking: tuple[RankingObservation, ...] | None = None

    @classmethod
    def model_validate(cls, obj: Any, *args: Any, **kwargs: Any) -> Self:
        if isinstance(obj, cls):
            return obj
        version = obj.get("schema_version") if isinstance(obj, dict) else None
        if version == LEGACY_EVIDENCE_SCHEMA_VERSION:
            reader: type[
                _SessionResultV1
                | _SessionResultV2
                | _SessionResultV3
                | _SessionResultV4
                | _SessionResultV5
            ] = _SessionResultV1
        elif version == EVIDENCE_SCHEMA_VERSION:
            reader = _SessionResultV2
        elif version == TRANSITION_RESULT_SCHEMA_VERSION:
            reader = _SessionResultV3
        elif version == REDACTION_RESULT_SCHEMA_VERSION:
            reader = _SessionResultV4
        elif version == WALK_FLOOR_RESULT_SCHEMA_VERSION:
            reader = _SessionResultV5
        elif version == 7:
            reader = _SessionResultV7
        elif version == 6:
            reader = _SessionResultV6
        else:
            raise _version_validation_error(cls.__name__, version)
        normalized = dict(reader.model_validate(obj, *args, **kwargs).__dict__)
        if version == LEGACY_EVIDENCE_SCHEMA_VERSION:
            normalized["acceptance_modes"] = ()
        return super().model_validate(normalized)

    @classmethod
    def model_validate_json(
        cls, json_data: str | bytes | bytearray, *args: Any, **kwargs: Any
    ) -> Self:
        """Route JSON through the version dispatcher above.

        Pydantic's ``model_validate_json`` is a SEPARATE entry point, not a
        decode in front of ``model_validate``, so overriding only the latter
        leaves the dispatcher bypassable by any caller that happens to hold
        bytes. That bypass is not academic: parsed directly against this class,
        a schema-v1 document takes the v2 ``acceptance_modes`` default and then
        reds on the canonical-wire validator, so the frozen reader that exists
        to keep v1 evidence readable never runs. ``gnd.evolve.models`` pairs
        every dispatcher with this override for the same reason; the exp lane
        did not, and a v1 ``result.json`` committed under ``examples/`` is what
        surfaced it.
        """
        if isinstance(json_data, bytearray):
            json_data = bytes(json_data)
        return cls.model_validate(json.loads(json_data), *args, **kwargs)

    @model_serializer(mode="wrap")
    def _serialize_wire_version(self, handler):
        document = handler(self)
        if self.schema_version != 7:
            document.pop("judgment_admission")
        if self.schema_version not in {6, 7}:
            document.pop("ranking_policy")
            document.pop("best_ranking")
        if self.schema_version == LEGACY_EVIDENCE_SCHEMA_VERSION:
            document.pop("acceptance_modes")
        if self.schema_version not in {
            REDACTION_RESULT_SCHEMA_VERSION,
            WALK_FLOOR_RESULT_SCHEMA_VERSION,
            6,
            7,
        }:
            document.pop("redaction")
        if self.schema_version not in {WALK_FLOOR_RESULT_SCHEMA_VERSION, 6, 7}:
            document.pop("contract_sha256")
            document.pop("walk_floors")
        return document

    @model_validator(mode="after")
    def _wire_acceptance_modes_are_canonical(self) -> Self:
        if self.schema_version == REDACTION_RESULT_SCHEMA_VERSION:
            if self.redaction is None:
                raise ValueError("schema-v4 results require session redaction metadata")
        elif (
            self.schema_version not in {WALK_FLOOR_RESULT_SCHEMA_VERSION, 6, 7}
            and self.redaction is not None
        ):
            raise ValueError("only schema-v4/v5 results carry session redaction metadata")
        if self.schema_version == LEGACY_EVIDENCE_SCHEMA_VERSION:
            if self.acceptance_modes:
                raise ValueError("schema-v1 results cannot carry acceptance modes")
        elif not self.acceptance_modes or self.acceptance_modes != tuple(
            sorted(set(self.acceptance_modes))
        ):
            raise ValueError("result acceptance modes must be nonempty, unique, and sorted")
        if self.schema_version in {WALK_FLOOR_RESULT_SCHEMA_VERSION, 6, 7}:
            if self.contract_sha256 is None:
                raise ValueError("schema-v5 results require a contract digest")
            case_ids = [row.case_id for row in self.walk_floors]
            if case_ids != sorted(case_ids) or len(case_ids) != len(set(case_ids)):
                raise ValueError("walk-floor result rows must be uniquely sorted")
        elif self.contract_sha256 is not None or self.walk_floors:
            raise ValueError("only schema-v5 results carry walk-floor accounting")
        return self


class BestAttemptIdentity(BaseModel):
    """Exact immutable attempt named by the replaceable best pointer."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    attempt_index: int = Field(gt=0)
    attempt_manifest_sha256: Sha256
    candidate_sha256: Sha256


class RecurrencePair(BaseModel):
    """First occurrence of one exact candidate/signature pair."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    candidate_sha256: Sha256
    normalized_verifier_signature: Sha256
    first_attempt_index: int = Field(gt=0)


@dataclass(frozen=True, slots=True)
class ResumeState:
    """State reconstructed only from complete, validated local evidence."""

    next_attempt_index: int
    best_attempt_identity: BestAttemptIdentity | None
    seen_recurrence_pairs: tuple[RecurrencePair, ...]
    accounted_wall_seconds: float
    prior_feedback_bytes: bytes | None
    prior_feedback_sha256: str | None


@dataclass(frozen=True, slots=True)
class StagedCandidate:
    """Private immutable snapshot made available to verifier execution."""

    attempt_index: int
    snapshot_path: Path
    inventory: CandidateInventory
    _staging_path: Path = field(repr=False)
    _source_root: Path = field(repr=False)
    _staging_identity: tuple[int, int] = field(repr=False)
    _snapshot_identity: tuple[int, int] = field(repr=False)
    _patch_source_identity: tuple[int, int] | None = field(default=None, repr=False)


@dataclass(frozen=True, slots=True)
class _CollectedFile:
    entry: CandidateFile
    data: bytes = field(repr=False)


def _classify(path: str, data: bytes) -> tuple[str, str | None]:
    media_type = mimetypes.guess_type(path, strict=False)[0] or "application/octet-stream"
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        encoding = None
    else:
        encoding = "utf-8"
    return media_type, encoding


def _collect_candidate(
    root: Path,
    *,
    expected_identity: tuple[int, int] | None = None,
    bound_fd: int | None = None,
) -> tuple[CandidateInventory, tuple[_CollectedFile, ...]]:
    """Read a candidate tree through no-follow descriptors into bounded memory."""

    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    path_bound = bound_fd is None
    if bound_fd is None:
        try:
            root_info = root.lstat()
        except OSError as error:
            raise ValueError(f"candidate root {root} could not be inspected: {error}") from error
        if stat.S_ISLNK(root_info.st_mode):
            raise ValueError(f"candidate root {root} is a symlink")
        if not stat.S_ISDIR(root_info.st_mode):
            raise ValueError(f"candidate root {root} is not a directory")
        root_fd = os.open(root, flags)
    else:
        root_fd = os.dup(bound_fd)
        root_info = os.fstat(root_fd)
    root_before = os.fstat(root_fd)
    if (root_before.st_dev, root_before.st_ino) != (root_info.st_dev, root_info.st_ino):
        os.close(root_fd)
        raise ValueError(f"candidate root {root} changed before it opened")
    if expected_identity is not None and (
        root_before.st_dev,
        root_before.st_ino,
    ) != expected_identity:
        os.close(root_fd)
        raise ValueError(f"candidate root {root} changed from its expected identity")
    collected: list[_CollectedFile] = []
    total_bytes = 0

    def descend(directory_fd: int, prefix: tuple[str, ...]) -> None:
        nonlocal total_bytes
        try:
            names = sorted(os.listdir(directory_fd))
        except OSError as error:
            raise ValueError(
                f"candidate directory {'/'.join(prefix) or '.'} changed: {error}"
            ) from error
        for name in names:
            relative_parts = (*prefix, name)
            relative = PurePosixPath(*relative_parts).as_posix()
            try:
                info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            except OSError as error:
                raise ValueError(
                    f"candidate entry {relative} could not be inspected: {error}"
                ) from error
            if stat.S_ISLNK(info.st_mode):
                raise ValueError(f"candidate entry {relative} is a symlink")
            if stat.S_ISDIR(info.st_mode):
                if len(relative_parts) > MAX_CANDIDATE_DEPTH:
                    raise ValueError(
                        f"candidate directory {relative} exceeds the "
                        f"{MAX_CANDIDATE_DEPTH}-component depth cap"
                    )
                child_fd = os.open(name, flags, dir_fd=directory_fd)
                opened_directory = os.fstat(child_fd)
                if (
                    not stat.S_ISDIR(opened_directory.st_mode)
                    or (opened_directory.st_dev, opened_directory.st_ino)
                    != (info.st_dev, info.st_ino)
                ):
                    os.close(child_fd)
                    raise ValueError(
                        f"candidate directory {relative} changed before it opened"
                    )
                try:
                    descend(child_fd, relative_parts)
                    final_directory = os.fstat(child_fd)
                    if (
                        final_directory.st_dev,
                        final_directory.st_ino,
                        final_directory.st_size,
                        final_directory.st_mtime_ns,
                    ) != (
                        opened_directory.st_dev,
                        opened_directory.st_ino,
                        opened_directory.st_size,
                        opened_directory.st_mtime_ns,
                    ):
                        raise ValueError(
                            f"candidate directory {relative} changed while being read"
                        )
                finally:
                    os.close(child_fd)
                continue
            if not stat.S_ISREG(info.st_mode):
                raise ValueError(f"candidate entry {relative} is not a regular file")
            if len(collected) >= MAX_CANDIDATE_FILES:
                raise ValueError(f"candidate has more than the {MAX_CANDIDATE_FILES}-file cap")
            if info.st_size > MAX_CANDIDATE_FILE_BYTES:
                raise ValueError(
                    f"candidate file {relative} is {info.st_size} bytes, over the "
                    f"{MAX_CANDIDATE_FILE_BYTES}-byte per-file cap"
                )
            if total_bytes + info.st_size > MAX_CANDIDATE_TOTAL_BYTES:
                raise ValueError(
                    f"candidate is over the {MAX_CANDIDATE_TOTAL_BYTES}-byte total cap"
                )
            file_flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
            file_fd = os.open(name, file_flags, dir_fd=directory_fd)
            try:
                opened = os.fstat(file_fd)
                if not stat.S_ISREG(opened.st_mode) or (
                    opened.st_dev,
                    opened.st_ino,
                ) != (info.st_dev, info.st_ino):
                    raise ValueError(f"candidate file {relative} changed before it opened")
                with os.fdopen(file_fd, "rb") as stream:
                    file_fd = -1
                    data = stream.read(MAX_CANDIDATE_FILE_BYTES + 1)
                    final = os.fstat(stream.fileno())
            finally:
                if file_fd >= 0:
                    os.close(file_fd)
            if len(data) > MAX_CANDIDATE_FILE_BYTES:
                raise ValueError(f"candidate file {relative} grew over its byte cap")
            if len(data) != opened.st_size or (
                final.st_dev,
                final.st_ino,
                final.st_mode,
                final.st_size,
                final.st_mtime_ns,
            ) != (
                opened.st_dev,
                opened.st_ino,
                opened.st_mode,
                opened.st_size,
                opened.st_mtime_ns,
            ):
                raise ValueError(f"candidate file {relative} changed while being read")
            total_bytes += len(data)
            media_type, encoding = _classify(relative, data)
            entry = CandidateFile(
                path=relative,
                media_type=media_type,
                encoding=encoding,
                size_bytes=len(data),
                sha256=sha256_hex(data),
                executable=bool(opened.st_mode & 0o111),
            )
            collected.append(_CollectedFile(entry=entry, data=data))

    try:
        descend(root_fd, ())
        root_after = os.fstat(root_fd)
        if (
            root_after.st_dev,
            root_after.st_ino,
            root_after.st_size,
            root_after.st_mtime_ns,
        ) != (
            root_before.st_dev,
            root_before.st_ino,
            root_before.st_size,
            root_before.st_mtime_ns,
        ):
            raise ValueError("candidate root changed while being read")
        if path_bound:
            root_current = root.lstat()
            if (root_current.st_dev, root_current.st_ino) != (
                root_after.st_dev,
                root_after.st_ino,
            ):
                raise ValueError("candidate root changed identity while being read")
    finally:
        os.close(root_fd)
    collected.sort(key=lambda item: item.entry.path)
    files = tuple(item.entry for item in collected)
    inventory = CandidateInventory(
        files=files,
        file_count=len(files),
        total_bytes=total_bytes,
        tree_sha256=tree_sha256_from_inventory(files),
    )
    return inventory, tuple(collected)


def _retained_wire(raw: bytes, declared: Mapping[str, int], case_id: str) -> int:
    """The wire an IMMUTABLE retained payload may replay under (IF-P3-17).

    ONLY where the caller declared one, and only that wire or its FROZEN
    PREDECESSOR two versions back, as an EXACT int -- never bool or float.
    A payload's own version can never select itself: `raw_payload_sha256`
    pins these bytes but NOT their version, and `CaseEvaluation` records
    none, so the declared wire is the only anchor; without it the check
    downstream is self-referential and the derivation guard is skippable.
    An absent id never made the claim, so the frozen fallback still refuses.
    """

    if case_id not in declared:
        return PAYLOAD_SCHEMA_VERSION
    wire = declared[case_id]
    try:
        payload = json.loads(raw)
    except ValueError:
        return wire
    version = payload.get("schema_version") if isinstance(payload, dict) else None
    admitted = {wire, wire - 2} if wire in MODEL_BOUND_PAYLOAD_SCHEMA_VERSIONS else {wire}
    legacy = getattr(wire, "legacy_version", None)
    if wire == 7 and legacy in {5, 6}:
        admitted.update({legacy, legacy - 2})
    return version if type(version) is int and version in admitted else wire


class SessionStore:
    """Publish the immutable evidence tree for one trusted session run."""

    def __init__(
        self,
        root: str | Path,
        *,
        run_id: str,
        contract_id: str | None = None,
    ):
        if not run_id.strip():
            raise ValueError("run_id cannot be empty")
        if contract_id is not None and not contract_id.strip():
            raise ValueError("contract_id cannot be empty")
        self.root = Path(root)
        self.run_id = run_id.strip()
        self.contract_id = contract_id.strip() if contract_id is not None else self.run_id
        self.root.mkdir(parents=True, exist_ok=True, mode=DIRECTORY_MODE)
        if stat.S_ISLNK(self.root.lstat().st_mode) or not self.root.is_dir():
            raise ValueError(f"session store root {self.root} must be a real directory")
        self._attempts_root = self.root / "attempts"
        self._launches_root = self.root / "launches"
        self._staging_root = self.root / ".staging"
        for directory in (self._attempts_root, self._launches_root, self._staging_root):
            directory.mkdir(exist_ok=True, mode=DIRECTORY_MODE)
            info = directory.lstat()
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
                raise ValueError(f"session store directory {directory} must be real")
        self._directory_identities = {
            directory: self._directory_identity(directory)
            for directory in (
                self.root,
                self._attempts_root,
                self._launches_root,
                self._staging_root,
            )
        }
        self._staged: dict[int, StagedCandidate] = {}
        self._feedback: dict[int, tuple[AttemptFeedback, EvidenceFile, bytes]] = {}
        self._best_loaded = False
        self._best_expected_present = False
        self._best_leaf_snapshot: LeafSnapshot | None = None

    @staticmethod
    def _directory_identity(path: Path) -> tuple[int, int]:
        try:
            info = path.lstat()
        except OSError as error:
            raise ValueError(f"session store directory {path} could not be inspected") from error
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise ValueError(f"session store directory {path} must be real")
        return info.st_dev, info.st_ino

    def _open_owned_directory(self, path: Path) -> int:
        expected = self._directory_identities[path]
        flags = (
            os.O_RDONLY
            | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0)
        )
        try:
            descriptor = os.open(path, flags)
        except OSError as error:
            raise ValueError(f"session store directory {path} could not be opened safely") from error
        opened = os.fstat(descriptor)
        if not stat.S_ISDIR(opened.st_mode) or (opened.st_dev, opened.st_ino) != expected:
            os.close(descriptor)
            raise ValueError(f"session store directory {path} changed identity")
        return descriptor

    def _assert_store_layout(self) -> None:
        for path in self._directory_identities:
            descriptor = self._open_owned_directory(path)
            os.close(descriptor)

    @staticmethod
    def _open_directory_below(
        anchor_fd: int,
        parts: tuple[str, ...],
        *,
        expected_identity: tuple[int, int] | None = None,
    ) -> int:
        """Resolve a real directory through one retained descriptor ancestry."""

        current = os.dup(anchor_fd)
        flags = (
            os.O_RDONLY
            | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0)
        )
        try:
            for part in parts:
                info = os.stat(part, dir_fd=current, follow_symlinks=False)
                if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
                    raise ValueError(
                        f"session evidence directory {part!r} is not real"
                    )
                child = os.open(part, flags, dir_fd=current)
                opened = os.fstat(child)
                if (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
                    os.close(child)
                    raise ValueError(
                        f"session evidence directory {part!r} changed before it opened"
                    )
                os.close(current)
                current = child
            opened = os.fstat(current)
            if expected_identity is not None and (
                opened.st_dev,
                opened.st_ino,
            ) != expected_identity:
                raise ValueError(
                    "session evidence directory changed from its enumerated identity"
                )
            result = current
            current = -1
            return result
        finally:
            if current >= 0:
                os.close(current)

    def attempt_path(self, attempt_index: int) -> Path:
        if attempt_index <= 0:
            raise ValueError("attempt_index must be greater than zero")
        return self._attempts_root / f"{attempt_index:04d}"

    def launch_path(self, attempt_index: int) -> Path:
        if attempt_index <= 0:
            raise ValueError("attempt_index must be greater than zero")
        return self._launches_root / f"{attempt_index:04d}.json"

    def inventory_candidate(self, candidate_root: str | Path) -> CandidateInventory:
        inventory, _ = _collect_candidate(Path(candidate_root))
        return inventory

    def publish_launch_intent(
        self,
        *,
        attempt_index: int,
        contract_sha256: str,
        policy_sha256: str,
        adapter: AgentAdapterId,
        base_prompt_sha256: str,
        controller_prompt_sha256: str,
        effective_prompt_sha256: str,
        feedback_sha256: str | None,
        candidate_root: str | Path,
    ) -> LaunchIntent:
        """Durably consume an attempt index immediately before agent launch."""

        self._assert_store_layout()
        if self.attempt_path(attempt_index).exists():
            raise FileExistsError(self.attempt_path(attempt_index))
        inventory = self.inventory_candidate(candidate_root)
        intent = LaunchIntent(
            run_id=self.run_id,
            attempt_index=attempt_index,
            contract_sha256=contract_sha256,
            policy_sha256=policy_sha256,
            adapter=adapter,
            base_prompt_sha256=base_prompt_sha256,
            controller_prompt_sha256=controller_prompt_sha256,
            effective_prompt_sha256=effective_prompt_sha256,
            feedback_sha256=feedback_sha256,
            candidate_inventory=inventory,
            candidate_inventory_sha256=sha256_hex(canonical_json_bytes(inventory)),
            candidate_sha256=inventory.tree_sha256,
        )
        destination = self.launch_path(attempt_index)
        try:
            publish_leaf_atomic(
                self._launches_root,
                destination.name,
                canonical_json_bytes(intent),
                expected_root=self._directory_identities[self._launches_root],
            )
        except ArtifactError as error:
            raise FileExistsError(destination) from error
        return intent

    def publish_declared_launch_intent(
        self,
        *,
        attempt_index: int,
        contract_sha256: str,
        policy_id: str,
        policy_kind: Literal["command", "openai-compatible"],
        policy_sha256: str,
        model_sha256: str | None,
        base_prompt_sha256: str,
        controller_prompt_sha256: str,
        effective_prompt_sha256: str,
        feedback_sha256: str | None,
        candidate_root: str | Path,
        schema_version: int = 2,
        judgment_policy_sha256: dict[str, str] | None = None,
    ) -> DeclaredLaunchIntent:
        """Durably consume an attempt index for a declared adapter."""

        self._assert_store_layout()
        if self.attempt_path(attempt_index).exists():
            raise FileExistsError(self.attempt_path(attempt_index))
        inventory = self.inventory_candidate(candidate_root)
        intent = DeclaredLaunchIntent(
            judgment_policy_sha256=judgment_policy_sha256 or {},
            schema_version=schema_version,
            run_id=self.run_id,
            attempt_index=attempt_index,
            contract_sha256=contract_sha256,
            policy_id=policy_id,
            policy_kind=policy_kind,
            policy_sha256=policy_sha256,
            model_sha256=model_sha256,
            base_prompt_sha256=base_prompt_sha256,
            controller_prompt_sha256=controller_prompt_sha256,
            effective_prompt_sha256=effective_prompt_sha256,
            feedback_sha256=feedback_sha256,
            candidate_inventory=inventory,
            candidate_inventory_sha256=sha256_hex(canonical_json_bytes(inventory)),
            candidate_sha256=inventory.tree_sha256,
        )
        destination = self.launch_path(attempt_index)
        try:
            publish_leaf_atomic(
                self._launches_root,
                destination.name,
                canonical_json_bytes(intent),
                expected_root=self._directory_identities[self._launches_root],
            )
        except ArtifactError as error:
            raise FileExistsError(destination) from error
        return intent

    def _load_launch_intent(
        self,
        attempt_index: int,
    ) -> tuple[LaunchIntent | DeclaredLaunchIntent, bytes, EvidenceFile]:
        relative = f"launches/{attempt_index:04d}.json"
        data = self._read_evidence_leaf(relative, cap=MAX_CANDIDATE_FILE_BYTES)
        document = _strict_object_bytes(data, label=relative)
        try:
            version = document.get("schema_version")
            if version == FIXED_STORE_SCHEMA_VERSION:
                intent: LaunchIntent | DeclaredLaunchIntent = LaunchIntent.model_validate(document)
            elif version in {DECLARED_LAUNCH_SCHEMA_VERSION, 3, 4}:
                intent = DeclaredLaunchIntent.model_validate(document)
            else:
                raise ValueError(f"unsupported launch-intent schema version {version!r}")
        except ValidationError as error:
            raise ValueError(f"{relative} is not a valid launch intent: {error}") from error
        if canonical_json_bytes(intent) != data:
            raise ValueError(f"{relative} is not canonically encoded")
        if intent.run_id != self.run_id or intent.attempt_index != attempt_index:
            raise ValueError(f"{relative} has a stale run or attempt identity")
        return (
            intent,
            data,
            EvidenceFile(path=relative, size_bytes=len(data), sha256=sha256_hex(data)),
        )

    def stage_patch_candidate(
        self, *, attempt_index, base_root, base_sha256, proposal_raw, contract
    ):
        from gnd.exp.session_patch import apply_candidate_patch, read_patch_document

        document = read_patch_document(proposal_raw)
        files = apply_candidate_patch(
            document,
            contract=contract,
            base_root=base_root,
            base_sha256=base_sha256,
            allow_initial_seed=attempt_index == 1,
        )
        name = "patch-input-" + secrets.token_hex(8)
        executable = set()
        if base_root is not None:
            inventory, _ = _collect_candidate(Path(base_root))
            executable = {f.path for f in inventory.files if f.executable}
        published_identity = []
        publish_directory_once(
            self._staging_root,
            name,
            files,
            manifest_name=max(files),
            executable_paths=executable,
            expected_root=self._directory_identities[self._staging_root],
            _published_identity=published_identity,
        )
        source = self._staging_root / name
        if len(published_identity) != 1:
            raise ValueError("patch source publication did not bind one directory identity")
        identity = published_identity[0]
        try:
            return self.stage_candidate(
                attempt_index=attempt_index,
                candidate_root=source,
                _patch_source_identity=identity,
            )
        except BaseException:
            self._discard_owned_staging_directory(source, identity)
            raise

    def stage_candidate(
        self,
        *,
        attempt_index: int,
        candidate_root: str | Path,
        _patch_source_identity: tuple[int, int] | None = None,
    ) -> StagedCandidate:
        """Freeze a candidate after agent cleanup and expose that snapshot to verifiers."""

        if attempt_index <= 0:
            raise ValueError("attempt_index must be greater than zero")
        self._assert_store_layout()
        if self.attempt_path(attempt_index).exists():
            raise FileExistsError(self.attempt_path(attempt_index))
        source = Path(candidate_root).absolute()
        cached = self._staged.get(attempt_index)
        if cached is not None:
            if cached._source_root != source:
                raise ValueError("attempt already staged from a different candidate root")
            self._validate_staged_candidate(cached)
            return cached

        inventory, files = _collect_candidate(source, expected_identity=_patch_source_identity)
        staging = self._staging_root / f"{attempt_index:04d}-{secrets.token_hex(8)}"
        staging_root_fd = self._open_owned_directory(self._staging_root)
        staging_fd = -1
        snapshot_fd = -1
        staging_identity: tuple[int, int] | None = None
        snapshot_identity: tuple[int, int] | None = None
        try:
            os.mkdir(staging.name, DIRECTORY_MODE, dir_fd=staging_root_fd)
            os.fsync(staging_root_fd)
            staging_info = os.stat(
                staging.name,
                dir_fd=staging_root_fd,
                follow_symlinks=False,
            )
            staging_identity = (staging_info.st_dev, staging_info.st_ino)
            staging_fd = os.open(
                staging.name,
                os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=staging_root_fd,
            )
            staging_opened = os.fstat(staging_fd)
            if (staging_opened.st_dev, staging_opened.st_ino) != staging_identity:
                raise ValueError("attempt staging directory changed before it opened")
            os.mkdir("candidate", DIRECTORY_MODE, dir_fd=staging_fd)
            snapshot_info = os.stat("candidate", dir_fd=staging_fd, follow_symlinks=False)
            snapshot_fd = os.open(
                "candidate",
                os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=staging_fd,
            )
            snapshot_opened = os.fstat(snapshot_fd)
            snapshot_identity = (snapshot_opened.st_dev, snapshot_opened.st_ino)
            if snapshot_identity != (snapshot_info.st_dev, snapshot_info.st_ino):
                raise ValueError("candidate snapshot changed before it opened")
            os.fsync(staging_fd)
            snapshot = staging / "candidate"
            for collected in files:
                destination = snapshot.joinpath(*PurePosixPath(collected.entry.path).parts)
                _write_new_file(
                    destination,
                    collected.data,
                    root=staging,
                    expected_root=staging_identity,
                    mode=(
                        SNAPSHOT_EXECUTABLE_FILE_MODE
                        if collected.entry.executable
                        else SNAPSHOT_FILE_MODE
                    ),
                )
            _write_new_file(
                staging / "candidate.inventory.json",
                canonical_json_bytes(inventory),
                root=staging,
                expected_root=staging_identity,
            )
            if self.inventory_candidate(snapshot) != inventory:
                raise ValueError("candidate snapshot differs from its source inventory")
        except BaseException:
            try:
                current = staging.lstat()
            except OSError:
                pass
            else:
                if staging_identity == (current.st_dev, current.st_ino):
                    shutil.rmtree(staging, ignore_errors=True)
            raise
        finally:
            if snapshot_fd >= 0:
                os.close(snapshot_fd)
            if staging_fd >= 0:
                os.close(staging_fd)
            os.close(staging_root_fd)
        self._assert_store_layout()
        if staging_identity is None or snapshot_identity is None:  # pragma: no cover
            raise RuntimeError("attempt staging identities were not captured")
        staged = StagedCandidate(
            attempt_index=attempt_index,
            snapshot_path=snapshot,
            inventory=inventory,
            _staging_path=staging,
            _source_root=source,
            _staging_identity=staging_identity,
            _snapshot_identity=snapshot_identity,
            _patch_source_identity=_patch_source_identity,
        )
        self._staged[attempt_index] = staged
        return staged

    def _validate_staged_candidate(self, staged: StagedCandidate) -> None:
        staging_root_fd = self._open_owned_directory(self._staging_root)
        staging_fd = -1
        snapshot_fd = -1
        try:
            staging_info = os.stat(
                staged._staging_path.name,
                dir_fd=staging_root_fd,
                follow_symlinks=False,
            )
            if (
                stat.S_ISLNK(staging_info.st_mode)
                or not stat.S_ISDIR(staging_info.st_mode)
                or (staging_info.st_dev, staging_info.st_ino)
                != staged._staging_identity
            ):
                raise ValueError("attempt staging directory changed identity")
            staging_fd = os.open(
                staged._staging_path.name,
                os.O_RDONLY
                | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=staging_root_fd,
            )
            if (
                (opened := os.fstat(staging_fd)).st_dev,
                opened.st_ino,
            ) != staged._staging_identity:
                raise ValueError("attempt staging directory changed before it opened")
            snapshot_info = os.stat("candidate", dir_fd=staging_fd, follow_symlinks=False)
            if (
                stat.S_ISLNK(snapshot_info.st_mode)
                or not stat.S_ISDIR(snapshot_info.st_mode)
                or (snapshot_info.st_dev, snapshot_info.st_ino)
                != staged._snapshot_identity
            ):
                raise ValueError("candidate snapshot changed identity")
            snapshot_fd = os.open(
                "candidate",
                os.O_RDONLY
                | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=staging_fd,
            )
            if (
                (snapshot_opened := os.fstat(snapshot_fd)).st_dev,
                snapshot_opened.st_ino,
            ) != staged._snapshot_identity:
                raise ValueError("candidate snapshot changed before it opened")
        finally:
            if snapshot_fd >= 0:
                os.close(snapshot_fd)
            if staging_fd >= 0:
                os.close(staging_fd)
            os.close(staging_root_fd)

    def _discard_owned_staging_directory(self, path: Path, identity: tuple[int, int]) -> None:
        """Clear only the captured direct child of this owned staging root."""
        if path.parent != self._staging_root:
            return
        root_fd = child_fd = -1
        cleanup_name = "cleanup-" + secrets.token_hex(16)
        placeholder_identity = None
        claimed = False
        try:
            root_fd = self._open_owned_directory(self._staging_root)
            current = os.stat(path.name, dir_fd=root_fd, follow_symlinks=False)
            if (current.st_dev, current.st_ino) != identity:
                return
            os.mkdir(cleanup_name, 0o700, dir_fd=root_fd)
            placeholder = os.stat(cleanup_name, dir_fd=root_fd, follow_symlinks=False)
            placeholder_identity = (placeholder.st_dev, placeholder.st_ino)
            _exchange_paths_atomic(root_fd, path.name, root_fd, cleanup_name)
            claimed = True
            child_fd = os.open(
                cleanup_name,
                os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=root_fd,
            )
            opened = os.fstat(child_fd)
            if (opened.st_dev, opened.st_ino) != identity:
                return
            current = os.stat(cleanup_name, dir_fd=root_fd, follow_symlinks=False)
            if (current.st_dev, current.st_ino) != identity:
                return
            _clear_directory_fd(child_fd)
            current = os.stat(cleanup_name, dir_fd=root_fd, follow_symlinks=False)
            if (current.st_dev, current.st_ino) == identity:
                os.rmdir(cleanup_name, dir_fd=root_fd)
                claimed = False
        except (OSError, ValueError, ArtifactError):
            pass
        finally:
            if child_fd >= 0:
                os.close(child_fd)
            if root_fd >= 0:
                if placeholder_identity is not None:
                    with suppress(OSError, ArtifactError):
                        current = os.stat(path.name, dir_fd=root_fd, follow_symlinks=False)
                        if claimed and (current.st_dev, current.st_ino) == placeholder_identity:
                            _exchange_paths_atomic(root_fd, path.name, root_fd, cleanup_name)
                            claimed = False
                    # Never clear a replacement to remove an empty reservation.
                    for name in (path.name, cleanup_name):
                        with suppress(OSError):
                            current = os.stat(name, dir_fd=root_fd, follow_symlinks=False)
                            if (current.st_dev, current.st_ino) == placeholder_identity:
                                os.rmdir(name, dir_fd=root_fd)
                os.close(root_fd)

    def _discard_staged(self, attempt_index: int, staged: StagedCandidate) -> None:
        self._discard_owned_staging_directory(staged._staging_path, staged._staging_identity)
        if staged._patch_source_identity is not None:
            self._discard_owned_staging_directory(
                staged._source_root, staged._patch_source_identity
            )
        self._staged.pop(attempt_index, None)
        self._feedback.pop(attempt_index, None)

    def publish_feedback(
        self,
        *,
        attempt_index: int,
        feedback: AttemptFeedback,
        staged_candidate: StagedCandidate | None = None,
    ) -> EvidenceFile:
        """Stage canonical current-attempt feedback before ``attempt.json``."""

        self._assert_store_layout()
        staged = staged_candidate or self._staged.get(attempt_index)
        if staged is None or self._staged.get(attempt_index) is not staged:
            raise ValueError("feedback requires a candidate staged by this session store")
        self._validate_staged_candidate(staged)
        if feedback.run_id != self.run_id:
            raise ValueError("feedback belongs to a different run")
        if feedback.contract_id != self.contract_id:
            raise ValueError("feedback belongs to a different contract")
        if feedback.source_attempt_index != attempt_index:
            raise ValueError("feedback source attempt does not match its staging directory")
        if feedback.candidate_sha256 != staged.inventory.tree_sha256:
            raise ValueError("feedback candidate digest does not match the staged snapshot")
        if attempt_index in self._feedback or (staged._staging_path / "feedback.json").exists():
            raise FileExistsError(staged._staging_path / "feedback.json")
        encoded, digest = canonical_feedback(feedback)
        relative = f"attempts/{attempt_index:04d}/feedback.json"
        evidence = EvidenceFile(path=relative, size_bytes=len(encoded), sha256=digest)
        try:
            _write_new_file(
                staged._staging_path / "feedback.json",
                encoded,
                root=staged._staging_path,
                expected_root=staged._staging_identity,
            )
        except BaseException:
            self._discard_staged(attempt_index, staged)
            raise
        self._feedback[attempt_index] = (feedback, evidence, encoded)
        return evidence

    def publish_attempt(
        self,
        *,
        attempt_index: int,
        candidate_root: str | Path | None,
        invocation: InvocationResult | DeclaredInvocationResult,
        verifier_payloads: dict[str, bytes],
        evaluation: AttemptEvaluation,
        contract: DataDrivenContract,
        best_eligible: bool,
        staged_candidate: StagedCandidate | None = None,
        elapsed_seconds: float | None = None,
    ) -> AttemptRecord:
        """Publish raw evidence followed by the canonical immutable attempt index."""

        self._assert_store_layout()
        final = self.attempt_path(attempt_index)
        if final.exists():
            raise FileExistsError(final)
        staged = staged_candidate or self._staged.get(attempt_index)
        if staged is None:
            if candidate_root is None:
                raise ValueError("candidate_root is required until an attempt is staged")
            staged = self.stage_candidate(
                attempt_index=attempt_index,
                candidate_root=candidate_root,
            )
        try:
            launch_intent, _, launch_evidence = self._load_launch_intent(attempt_index)
            if launch_intent.contract_sha256 != evaluation.contract_sha256:
                raise ValueError("launch intent contract digest does not match the evaluation")
            if isinstance(launch_intent, LaunchIntent):
                if not isinstance(invocation, InvocationResult):
                    raise TypeError("legacy launch intent requires a legacy invocation")
                if launch_intent.adapter is not invocation.adapter:
                    raise ValueError("launch intent adapter does not match the invocation")
            else:
                if not isinstance(invocation, DeclaredInvocationResult):
                    raise TypeError("declared launch intent requires a declared invocation")
                if (
                    launch_intent.policy_id != invocation.policy_id
                    or launch_intent.policy_kind != invocation.policy_kind
                    or launch_intent.policy_sha256 != invocation.policy_sha256
                ):
                    raise ValueError("launch intent policy does not match the invocation")
            if launch_intent.controller_prompt_sha256 != invocation.prompt_sha256:
                raise ValueError("launch intent prompt identity does not match the invocation")
            if launch_intent.feedback_sha256 != invocation.feedback_sha256:
                raise ValueError("launch intent feedback identity does not match the invocation")
            if isinstance(invocation, InvocationResult):
                expected_prompt_token = f"<prompt:sha256={launch_intent.effective_prompt_sha256}>"
                if not invocation.argv or invocation.argv[-1] != expected_prompt_token:
                    raise ValueError("launch intent effective prompt does not match the invocation")
            elif launch_intent.effective_prompt_sha256 != invocation.effective_prompt_sha256:
                raise ValueError("launch intent effective prompt does not match the invocation")
            if staged.attempt_index != attempt_index:
                raise ValueError("staged candidate belongs to a different attempt")
            if self._staged.get(attempt_index) is not staged:
                raise ValueError("staged candidate does not belong to this session store")
            self._validate_staged_candidate(staged)
            if (
                candidate_root is not None
                and staged._source_root != Path(candidate_root).absolute()
            ):
                raise ValueError("candidate_root differs from the staged candidate source")
            if evaluation.attempt_index != attempt_index:
                raise ValueError("evaluation belongs to a different attempt")
            if evaluation.candidate_sha256 != staged.inventory.tree_sha256:
                raise ValueError(
                    "evaluation candidate digest does not match the immutable candidate snapshot"
                )
            observed_inventory, candidate_files = _collect_candidate(
                staged.snapshot_path,
                expected_identity=staged._snapshot_identity,
            )
            if observed_inventory != staged.inventory:
                raise ValueError("immutable candidate snapshot changed during verifier execution")
            if len(invocation.stdout) > MAX_RETAINED_STREAM_BYTES:
                raise ValueError("retained agent stdout is over the evidence-store byte cap")
            if len(invocation.stderr) > MAX_RETAINED_STREAM_BYTES:
                raise ValueError("retained agent stderr is over the evidence-store byte cap")
            if elapsed_seconds is None:
                elapsed_seconds = invocation.ended_monotonic - invocation.started_monotonic
            if not math.isfinite(elapsed_seconds) or elapsed_seconds < 0:
                raise ValueError("attempt elapsed time is negative or non-finite")

            evaluation_by_case = {result.case_id: result for result in evaluation.results}
            for case_id, result in evaluation_by_case.items():
                raw = verifier_payloads.get(case_id)
                if raw is None:
                    raise ValueError(f"evaluation for {case_id!r} has no raw verifier payload")
                if sha256_hex(raw) != result.raw_payload_sha256:
                    raise ValueError(
                        f"raw verifier digest for {case_id!r} does not match evaluation"
                    )

            feedback_entry = self._feedback.get(attempt_index)
            if feedback_entry is None:
                raise ValueError(
                    "canonical current-attempt feedback must be published before the attempt"
                )
            feedback, feedback_evidence, feedback_bytes = feedback_entry
            if feedback.contract_sha256 != evaluation.contract_sha256:
                raise ValueError("feedback contract digest does not match the evaluation")
            if feedback.process_exit != invocation.exit_code:
                raise ValueError("feedback process exit does not match the invocation")
            expected_payloads = tuple(
                (case_id, evaluation_by_case[case_id].raw_payload_sha256)
                for case_id in sorted(evaluation_by_case)
            )
            expected_exits = tuple(
                (case_id, evaluation_by_case[case_id].payload_exit)
                for case_id in sorted(evaluation_by_case)
            )
            if feedback.case_payload_sha256s != expected_payloads:
                raise ValueError("feedback payload digests do not match the evaluation")
            if feedback.payload_exit != expected_exits:
                raise ValueError("feedback payload exits do not match the evaluation")
            if feedback.normalized_verifier_signature != normalized_verifier_signature(
                contract,
                evaluation,
                schema_version=feedback.schema_version,
            ):
                raise ValueError("feedback verifier signature does not match the evaluation")
            if canonical_feedback(feedback)[0] != feedback_bytes:
                raise ValueError("staged feedback bytes are not canonical")

            raw_evidence: list[VerifierPayloadEvidence] = []
            for case_id, raw in sorted(verifier_payloads.items()):
                if not case_id or any(
                    character
                    not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
                    for character in case_id
                ):
                    raise ValueError(f"unsafe verifier case id {case_id!r}")
                if len(raw) > MAX_VERIFIER_PAYLOAD_BYTES:
                    raise ValueError(f"verifier payload for {case_id!r} is over the byte cap")
                relative = f"attempts/{attempt_index:04d}/verifier/{case_id}.json"
                raw_evidence.append(
                    VerifierPayloadEvidence(
                        case_id=case_id,
                        **_evidence_entry(relative, raw),
                    )
                )

            inventory_bytes = canonical_json_bytes(staged.inventory)
            evaluation_bytes = canonical_json_bytes(evaluation)
            stdout = EvidenceFile(
                **_evidence_entry(f"attempts/{attempt_index:04d}/agent.stdout", invocation.stdout),
            )
            stderr = EvidenceFile(
                **_evidence_entry(f"attempts/{attempt_index:04d}/agent.stderr", invocation.stderr),
            )
            evidence_digests: dict[str, str] = {
                "launch_intent_sha256": launch_evidence.sha256,
                "candidate_inventory_sha256": sha256_hex(inventory_bytes),
                "candidate_tree_sha256": staged.inventory.tree_sha256,
                "agent_stdout_sha256": stdout.sha256,
                "agent_stderr_sha256": stderr.sha256,
                "evaluation_sha256": sha256_hex(evaluation_bytes),
                "feedback_sha256": feedback_evidence.sha256,
            }
            evidence_digests.update(
                {f"verifier.{entry.case_id}.sha256": entry.sha256 for entry in raw_evidence}
            )
            record = AttemptRecord(
                assurance_receipts=tuple(
                    sorted(
                        (
                            result._assurance_receipt
                            for result in evaluation.results
                            if result._assurance_receipt is not None
                        ),
                        key=lambda row: row.case_id,
                    )
                )
                if feedback.schema_version in {4, 5, 6, 7}
                else (),
                schema_version=(
                    DECLARED_ADAPTER_EVIDENCE_SCHEMA_VERSION
                    if isinstance(invocation, DeclaredInvocationResult)
                    else feedback.schema_version
                ),
                feedback_schema_version=(
                    feedback.schema_version
                    if feedback.schema_version != LEGACY_EVIDENCE_SCHEMA_VERSION
                    else None
                ),
                run_id=self.run_id,
                attempt_index=attempt_index,
                elapsed_seconds=elapsed_seconds,
                launch_intent=launch_evidence,
                invocation=invocation,
                candidate_inventory=staged.inventory,
                candidate_inventory_sha256=sha256_hex(inventory_bytes),
                candidate_snapshot=f"attempts/{attempt_index:04d}/candidate",
                agent_stdout=stdout,
                agent_stderr=stderr,
                raw_verifier_payloads=tuple(raw_evidence),
                evaluation=evaluation,
                feedback=feedback_evidence,
                best_eligible=best_eligible,
                evidence_digests=evidence_digests,
                redaction=feedback.redaction,
            )
            publication_files = {
                **{
                    f"candidate/{collected.entry.path}": collected.data
                    for collected in candidate_files
                },
                "candidate.inventory.json": inventory_bytes,
                "feedback.json": feedback_bytes,
                "agent.stdout": invocation.stdout,
                "agent.stderr": invocation.stderr,
                **{f"verifier/{case_id}.json": raw for case_id, raw in verifier_payloads.items()},
                # Load-bearing ordering is enforced by the shared primitive:
                # this manifest is the final durable leaf.
                "attempt.json": canonical_json_bytes(record),
            }
            executable_paths = {
                f"candidate/{collected.entry.path}"
                for collected in candidate_files
                if collected.entry.executable
            }
            self._validate_staged_candidate(staged)
            try:
                publish_directory_once(
                    self._attempts_root,
                    final.name,
                    publication_files,
                    manifest_name="attempt.json",
                    max_files=len(publication_files),
                    max_file_bytes=max(
                        MAX_CANDIDATE_FILE_BYTES,
                        MAX_RETAINED_STREAM_BYTES,
                        MAX_VERIFIER_PAYLOAD_BYTES,
                    ),
                    max_total_bytes=sum(len(data) for data in publication_files.values()),
                    max_depth=MAX_CANDIDATE_DEPTH + 1,
                    expected_root=self._directory_identities[self._attempts_root],
                    executable_paths=executable_paths,
                    # An agent that left no candidate bytes (agent-failure) still
                    # has a snapshot: an empty directory the readers expect.
                    empty_directories=(
                        ("candidate",) if staged.inventory.file_count == 0 else ()
                    ),
                )
            except ArtifactError as error:
                if "collision" in str(error):
                    raise FileExistsError(final) from error
                raise ValueError(f"attempt publication failed: {error}") from error
        except BaseException:
            # A failed attempt never leaves a manifest at its published path.
            self._discard_staged(attempt_index, staged)
            raise
        self._discard_staged(attempt_index, staged)
        return record

    def publish_best(self, record: AttemptRecord) -> Path:
        """Atomically point ``best.json`` at the exact immutable attempt manifest."""

        self._assert_store_layout()
        if record.run_id != self.run_id:
            raise ValueError("attempt record belongs to a different run")
        if not record.best_eligible:
            raise ValueError("an incomplete verifier attempt cannot become best")
        attempt_bytes = self._read_evidence_leaf(
            f"attempts/{record.attempt_index:04d}/attempt.json",
            cap=MAX_CANDIDATE_FILE_BYTES,
        )
        expected = canonical_json_bytes(record)
        if attempt_bytes != expected:
            raise ValueError("published attempt manifest does not match the supplied record")
        document = {
            "schema_version": FIXED_STORE_SCHEMA_VERSION,
            "run_id": self.run_id,
            "attempt": record.attempt_index,
            "attempt_manifest_sha256": sha256_hex(attempt_bytes),
            "candidate_sha256": record.candidate_inventory.tree_sha256,
        }
        destination = self.root / "best.json"
        expected_leaf: LeafSnapshot | None = None
        root_fd = self._open_owned_directory(self.root)
        try:
            destination_info = os.stat(
                "best.json",
                dir_fd=root_fd,
                follow_symlinks=False,
            )
        except FileNotFoundError:
            if self._best_loaded and self._best_expected_present:
                raise ValueError("best pointer disappeared after it was validated")
        else:
            if stat.S_ISLNK(destination_info.st_mode):
                raise ValueError("best pointer is a symlink")
            if self._best_loaded and not self._best_expected_present:
                raise ValueError("best pointer appeared after its absence was validated")
            if not self._best_loaded:
                raise ValueError(
                    "an existing best pointer must be validated before it can be replaced"
                )
            try:
                _, expected_leaf = read_regular_bounded(
                    self.root,
                    "best.json",
                    max_bytes=MAX_CANDIDATE_FILE_BYTES,
                    expected_root=self._directory_identities[self.root],
                )
            except ArtifactError as error:
                raise ValueError(f"best pointer could not be read safely: {error}") from error
            if self._best_leaf_snapshot is not None and expected_leaf != self._best_leaf_snapshot:
                raise ValueError("best pointer changed after it was validated")
        finally:
            os.close(root_fd)
        try:
            published = publish_leaf_atomic(
                self.root,
                "best.json",
                canonical_json_bytes(document),
                expected=expected_leaf,
                expected_root=self._directory_identities[self.root],
            )
        except ArtifactError as error:
            raise ValueError(f"best pointer publication failed: {error}") from error
        self._best_loaded = True
        self._best_expected_present = True
        self._best_leaf_snapshot = published
        return destination

    def _read_evidence_leaf(
        self,
        relative: str,
        *,
        cap: int,
        expected: EvidenceFile | None = None,
        attempt_fd: int | None = None,
        root_fd: int | None = None,
    ) -> bytes:
        if attempt_fd is not None and root_fd is not None:
            raise ValueError("an evidence read cannot have two descriptor roots")
        if attempt_fd is not None:
            parts = PurePosixPath(relative).parts
            if len(parts) < 3 or parts[0] != "attempts":
                raise ValueError("attempt evidence path lacks its attempt prefix")
            contained = PurePosixPath(*parts[2:]).as_posix()
            try:
                data, _ = _read_regular_bounded_fd(
                    attempt_fd,
                    contained,
                    max_bytes=cap,
                )
            except ArtifactError as error:
                raise ValueError(
                    f"evidence {relative!r} could not be read safely: {error}"
                ) from error
        elif root_fd is not None:
            try:
                data, _ = _read_regular_bounded_fd(
                    root_fd,
                    relative,
                    max_bytes=cap,
                )
            except ArtifactError as error:
                raise ValueError(
                    f"evidence {relative!r} could not be read safely: {error}"
                ) from error
        elif relative.startswith("attempts/"):
            read_root = self._attempts_root
            contained = relative.removeprefix("attempts/")
            try:
                data, _ = read_regular_bounded(
                    read_root,
                    contained,
                    max_bytes=cap,
                    expected_root=self._directory_identities[read_root],
                )
            except ArtifactError as error:
                raise ValueError(
                    f"evidence {relative!r} could not be read safely: {error}"
                ) from error
        else:
            try:
                data, _ = read_regular_bounded(
                    self.root,
                    relative,
                    max_bytes=cap,
                    expected_root=self._directory_identities[self.root],
                )
            except ArtifactError as error:
                raise ValueError(
                    f"evidence {relative!r} could not be read safely: {error}"
                ) from error
        if expected is not None:
            if expected.path != relative:
                raise ValueError(f"evidence path {expected.path!r} does not match {relative!r}")
            if len(data) != expected.size_bytes or sha256_hex(data) != expected.sha256:
                raise ValueError(f"evidence digest or size mismatch at {relative!r}")
        return data

    def _load_attempt_for_resume(
        self,
        attempt_index: int,
        *,
        contract: DataDrivenContract | None = None,
        expected_payload_versions: Mapping[str, int] | None = None,
    ) -> tuple[AttemptRecord, bytes, AttemptFeedback, bytes]:
        """Load one attempt while binding the recorded attempts directory."""

        attempts_fd = self._open_owned_directory(self._attempts_root)
        try:
            return self._load_attempt_for_resume_bound(
                attempt_index,
                attempts_fd=attempts_fd,
                contract=contract,
                expected_payload_versions=expected_payload_versions,
            )
        finally:
            os.close(attempts_fd)

    def _load_attempt_for_resume_bound(
        self,
        attempt_index: int,
        *,
        attempts_fd: int,
        contract: DataDrivenContract | None = None,
        expected_identity: tuple[int, int] | None = None,
        expected_payload_versions: Mapping[str, int] | None = None,
    ) -> tuple[AttemptRecord, bytes, AttemptFeedback, bytes]:
        attempt_fd = self._open_directory_below(
            attempts_fd,
            (f"{attempt_index:04d}",),
            expected_identity=expected_identity,
        )
        try:
            return self._load_attempt_from_fd(
                attempt_index,
                attempt_fd=attempt_fd,
                contract=contract,
                expected_payload_versions=expected_payload_versions,
            )
        finally:
            os.close(attempt_fd)

    def _load_attempt_from_fd(
        self,
        attempt_index: int,
        *,
        attempt_fd: int,
        contract: DataDrivenContract | None = None,
        expected_payload_versions: Mapping[str, int] | None = None,
    ) -> tuple[AttemptRecord, bytes, AttemptFeedback, bytes]:
        prefix = f"attempts/{attempt_index:04d}"
        attempt_relative = f"{prefix}/attempt.json"
        attempt_bytes = self._read_evidence_leaf(
            attempt_relative,
            cap=MAX_CANDIDATE_FILE_BYTES,
            attempt_fd=attempt_fd,
        )
        document = _strict_object_bytes(attempt_bytes, label=attempt_relative)
        try:
            stdout_document = document["agent_stdout"]
            stderr_document = document["agent_stderr"]
            invocation_document = document["invocation"]
            stdout_path = stdout_document["path"]
            stderr_path = stderr_document["path"]
        except (KeyError, TypeError) as error:
            raise ValueError(f"{attempt_relative} lacks its stream evidence index") from error
        if not isinstance(invocation_document, dict):
            raise ValueError(  # noqa: TRY004
                f"{attempt_relative} invocation must be an object"
            )
        stdout_bytes = self._read_evidence_leaf(
            stdout_path,
            cap=MAX_RETAINED_STREAM_BYTES,
            attempt_fd=attempt_fd,
        )
        stderr_bytes = self._read_evidence_leaf(
            stderr_path,
            cap=MAX_RETAINED_STREAM_BYTES,
            attempt_fd=attempt_fd,
        )
        invocation_document["stdout"] = stdout_bytes
        invocation_document["stderr"] = stderr_bytes
        try:
            record = AttemptRecord.model_validate(document)
        except (ValidationError, ValueError) as error:
            raise ValueError(
                f"{attempt_relative} is not a valid attempt record: {error}"
            ) from error
        if canonical_json_bytes(record) != attempt_bytes:
            raise ValueError(f"{attempt_relative} is not canonically encoded")
        if record.run_id != self.run_id or record.attempt_index != attempt_index:
            raise ValueError(f"{attempt_relative} has a stale run or attempt identity")
        if record.candidate_snapshot != f"{prefix}/candidate":
            raise ValueError(f"{attempt_relative} names a stale candidate snapshot")
        launch_intent, _, launch_evidence = self._load_launch_intent(attempt_index)
        if record.launch_intent != launch_evidence:
            raise ValueError("attempt launch-intent digest or path is stale")
        if launch_intent.contract_sha256 != record.evaluation.contract_sha256:
            raise ValueError("attempt launch intent binds a different contract digest")
        if isinstance(launch_intent, LaunchIntent):
            if not isinstance(record.invocation, InvocationResult):
                raise TypeError("legacy launch intent binds a declared invocation")
            if launch_intent.adapter is not record.invocation.adapter:
                raise ValueError("attempt launch intent binds a different adapter")
        else:
            if not isinstance(record.invocation, DeclaredInvocationResult):
                raise TypeError("declared launch intent binds a legacy invocation")
            if (
                launch_intent.policy_id != record.invocation.policy_id
                or launch_intent.policy_kind != record.invocation.policy_kind
                or launch_intent.policy_sha256 != record.invocation.policy_sha256
            ):
                raise ValueError("attempt launch intent binds a different policy")
            if contract is not None:
                declaration = contract.adapter
                expected_model_sha256 = (
                    None
                    if declaration is None or declaration.parameters.model is None
                    else sha256_hex(declaration.parameters.model.encode())
                )
                if launch_intent.model_sha256 != expected_model_sha256:
                    raise ValueError("attempt launch intent binds a different model")
        if launch_intent.controller_prompt_sha256 != record.invocation.prompt_sha256:
            raise ValueError("attempt launch intent binds different agent instructions")
        if launch_intent.feedback_sha256 != record.invocation.feedback_sha256:
            raise ValueError("attempt launch intent binds different retry feedback")
        if isinstance(record.invocation, InvocationResult):
            if (
                not record.invocation.argv
                or record.invocation.argv[-1]
                != f"<prompt:sha256={launch_intent.effective_prompt_sha256}>"
            ):
                raise ValueError("attempt launch intent binds a different effective prompt")
        elif (
            record.invocation.effective_prompt_sha256
            != launch_intent.effective_prompt_sha256
        ):
            raise ValueError("attempt launch intent binds a different effective prompt")

        inventory_relative = f"{prefix}/candidate.inventory.json"
        inventory_bytes = self._read_evidence_leaf(
            inventory_relative,
            cap=MAX_CANDIDATE_FILE_BYTES,
            attempt_fd=attempt_fd,
        )
        inventory_document = _strict_object_bytes(
            inventory_bytes,
            label=inventory_relative,
        )
        try:
            inventory = CandidateInventory.model_validate(inventory_document)
        except ValidationError as error:
            raise ValueError(f"{inventory_relative} is invalid: {error}") from error
        if canonical_json_bytes(inventory) != inventory_bytes:
            raise ValueError(f"{inventory_relative} is not canonically encoded")
        if inventory != record.candidate_inventory:
            raise ValueError("attempt candidate inventory differs from its retained inventory")
        if sha256_hex(inventory_bytes) != record.candidate_inventory_sha256:
            raise ValueError("attempt candidate inventory digest is stale")
        candidate_fd = -1
        try:
            candidate_fd = self._open_directory_below(
                attempt_fd,
                ("candidate",),
            )
            observed_inventory, _ = _collect_candidate(
                self.root / record.candidate_snapshot,
                bound_fd=candidate_fd,
            )
        except (OSError, ValueError) as error:
            raise ValueError(f"candidate snapshot could not be inventoried: {error}") from error
        finally:
            if candidate_fd >= 0:
                os.close(candidate_fd)
        if observed_inventory != inventory:
            raise ValueError("candidate snapshot bytes do not match the attempt inventory")

        self._read_evidence_leaf(
            f"{prefix}/agent.stdout",
            cap=MAX_RETAINED_STREAM_BYTES,
            expected=record.agent_stdout,
            attempt_fd=attempt_fd,
        )
        self._read_evidence_leaf(
            f"{prefix}/agent.stderr",
            cap=MAX_RETAINED_STREAM_BYTES,
            expected=record.agent_stderr,
            attempt_fd=attempt_fd,
        )
        raw_by_case: dict[str, bytes] = {}
        for entry in record.raw_verifier_payloads:
            expected_path = f"{prefix}/verifier/{entry.case_id}.json"
            raw_by_case[entry.case_id] = self._read_evidence_leaf(
                expected_path,
                cap=MAX_VERIFIER_PAYLOAD_BYTES,
                expected=entry,
                attempt_fd=attempt_fd,
            )
        for result in record.evaluation.results:
            raw = raw_by_case.get(result.case_id)
            if raw is None or sha256_hex(raw) != result.raw_payload_sha256:
                raise ValueError(f"evaluation case {result.case_id!r} lacks its exact raw payload")

        feedback_relative = f"{prefix}/feedback.json"
        feedback_bytes = self._read_evidence_leaf(
            feedback_relative,
            cap=MAX_VERIFIER_PAYLOAD_BYTES,
            expected=record.feedback,
            attempt_fd=attempt_fd,
        )
        feedback_document = _strict_object_bytes(
            feedback_bytes,
            label=feedback_relative,
        )
        try:
            feedback = AttemptFeedback.model_validate(feedback_document)
        except ValidationError as error:
            raise ValueError(f"{feedback_relative} is invalid: {error}") from error
        if canonical_feedback(feedback)[0] != feedback_bytes:
            raise ValueError(f"{feedback_relative} is not canonically encoded")
        if (
            feedback.run_id != self.run_id
            or feedback.contract_id != self.contract_id
            or feedback.source_attempt_index != attempt_index
            or feedback.candidate_sha256 != inventory.tree_sha256
            or feedback.contract_sha256 != record.evaluation.contract_sha256
        ):
            raise ValueError("feedback identity does not bind the current immutable attempt")
        if feedback.process_exit != record.invocation.exit_code:
            raise ValueError("feedback process exit does not match the retained invocation")
        evaluation_by_case = {result.case_id: result for result in record.evaluation.results}
        expected_payloads = tuple(
            (case_id, evaluation_by_case[case_id].raw_payload_sha256)
            for case_id in sorted(evaluation_by_case)
        )
        expected_exits = tuple(
            (case_id, evaluation_by_case[case_id].payload_exit)
            for case_id in sorted(evaluation_by_case)
        )
        if feedback.case_payload_sha256s != expected_payloads:
            raise ValueError("feedback payload digests do not match the attempt evaluation")
        if feedback.payload_exit != expected_exits:
            raise ValueError("feedback payload exits do not match the attempt evaluation")
        if (
            record.schema_version != DECLARED_ADAPTER_EVIDENCE_SCHEMA_VERSION
            and record.schema_version != feedback.schema_version
        ):
            raise ValueError("attempt and feedback schema versions do not agree")
        if record.redaction != feedback.redaction:
            raise ValueError("attempt and feedback redaction metadata do not agree")
        if feedback.schema_version in (
            EVIDENCE_SCHEMA_VERSION,
            DERIVATION_EVIDENCE_SCHEMA_VERSION,
            ASSURANCE_EVIDENCE_SCHEMA_VERSION,
            TRANSITION_EVIDENCE_SCHEMA_VERSION,
            REDACTION_EVIDENCE_SCHEMA_VERSION,
            WALK_FLOOR_EVIDENCE_SCHEMA_VERSION,
        ):
            if contract is None:
                raise ValueError("schema-v2 attempt replay requires the normalized contract")
            if contract.experiment_id != self.contract_id:
                raise ValueError("replay contract identity does not match the session store")
            contract_cases = {case.case_id: case for case in contract.cases}
            revalidated_results = []
            for result in record.evaluation.results:
                case = contract_cases.get(result.case_id)
                raw = raw_by_case.get(result.case_id)
                if case is None or raw is None:
                    raise ValueError(
                        f"schema-v2 evaluation case {result.case_id!r} is not contract-bound"
                    )
                try:
                    if isinstance(case.acceptance, TestsAcceptance):
                        revalidated = validate_tests_payload(
                            raw,
                            case_id=case.case_id,
                            role=case.role.value,
                            process_exit=result.process_exit,
                            required_tests=case.acceptance.required_tests,
                            candidate_sha256=record.evaluation.candidate_sha256,
                            contract_sha256=record.evaluation.contract_sha256,
                        )
                    elif isinstance(case.acceptance, TransitionAcceptance):
                        revalidated = validate_transition_payload(
                            raw,
                            case_id=case.case_id,
                            role=case.role.value,
                            expected_schema_version=_retained_wire(
                                raw, expected_payload_versions or {}, case.case_id
                            ),
                            process_exit=result.process_exit,
                            expected_model=case.verify.model.path,
                            expected_post=case.verify.post,
                            candidate_sha256=record.evaluation.candidate_sha256,
                            contract_sha256=record.evaluation.contract_sha256,
                            evidence_candidate_sha256=record.evaluation.candidate_sha256,
                            evidence_contract_sha256=record.evaluation.contract_sha256,
                        )
                        if case.acceptance.walk is not None and revalidated.payload_exit == 0:
                            from gnd.transition import (
                                TransitionLoadError,
                                read_steps_document,
                            )

                            steps_path = (
                                self.root / record.candidate_snapshot / case.verify.steps
                            )
                            try:
                                steps_document = read_steps_document(steps_path)
                            except TransitionLoadError as error:
                                raise ValueError(
                                    f"schema-v7 evaluation case {result.case_id!r} "
                                    f"has invalid retained steps: {error}"
                                ) from error
                            submitted_steps = steps_document["steps"]
                            submitted_operations = [
                                step["op"] for step in submitted_steps
                            ]
                            report_operations = [
                                step.operation_id for step in revalidated.transition_steps
                            ]
                            if submitted_operations != report_operations:
                                raise ValueError(
                                    f"schema-v7 evaluation case {result.case_id!r} "
                                    "retained step operations differ from raw evidence"
                                )
                            revalidated = attach_walk_floor_steps(
                                revalidated, submitted_steps
                            )
                    else:
                        revalidated = validate_verifier_payload(
                            raw,
                            case_id=case.case_id,
                            role=case.role.value,
                            expected_schema_version=_retained_wire(
                                raw, expected_payload_versions or {}, case.case_id
                            ),
                            process_exit=result.process_exit,
                            expected_command=case.verify.command,
                            expected_model=case.verify.model.path,
                            expected_subject=case.verify.subject,
                            candidate_sha256=record.evaluation.candidate_sha256,
                            contract_sha256=record.evaluation.contract_sha256,
                            evidence_candidate_sha256=record.evaluation.candidate_sha256,
                            evidence_contract_sha256=record.evaluation.contract_sha256,
                            require_extraction=case.verify.command == "verify",
                            expected_outputs=result.expected_outputs,
                        )
                except VerifierPayloadError as error:
                    raise ValueError(
                        f"schema-v2 evaluation case {result.case_id!r} failed replay: "
                        f"{'; '.join(error.issues)}"
                    ) from error
                if revalidated.model_dump(mode="json") != result.model_dump(mode="json"):
                    raise ValueError(
                        f"schema-v2 evaluation case {result.case_id!r} differs from raw evidence"
                    )
                revalidated_results.append(revalidated)
            evaluation = AttemptEvaluation(
                attempt_index=record.evaluation.attempt_index,
                candidate_sha256=record.evaluation.candidate_sha256,
                contract_sha256=record.evaluation.contract_sha256,
                results=tuple(revalidated_results),
            )
            record = record.model_copy(update={"evaluation": evaluation})
        if feedback.normalized_verifier_signature != normalized_verifier_signature(
            contract,
            record.evaluation,
            schema_version=feedback.schema_version,
        ):
            raise ValueError("feedback signature does not match the attempt evaluation")

        inventory_canonical = canonical_json_bytes(record.candidate_inventory)
        evaluation_canonical = canonical_json_bytes(record.evaluation)
        expected_digests = {
            "launch_intent_sha256": record.launch_intent.sha256,
            "candidate_inventory_sha256": sha256_hex(inventory_canonical),
            "candidate_tree_sha256": record.candidate_inventory.tree_sha256,
            "agent_stdout_sha256": record.agent_stdout.sha256,
            "agent_stderr_sha256": record.agent_stderr.sha256,
            "evaluation_sha256": sha256_hex(evaluation_canonical),
            "feedback_sha256": record.feedback.sha256,
            **{
                f"verifier.{entry.case_id}.sha256": entry.sha256
                for entry in record.raw_verifier_payloads
            },
        }
        if record.evidence_digests != expected_digests:
            raise ValueError("attempt evidence digest index is incomplete or stale")
        return record, attempt_bytes, feedback, feedback_bytes

    def read_resume_state(
        self,
        contract: DataDrivenContract,
        *,
        expected_payload_versions: Mapping[str, int] | None = None,
    ) -> ResumeState:
        """Validate all immutable records and reconstruct the next controller state.

        This method is intentionally read-only.  A gap, partial staging tree,
        stale digest, bad pointer, or terminal result is refused rather than
        repaired, renamed, or silently skipped.
        """

        if contract.schema_version in {7, 8}:
            from gnd.exp.session_v7 import reconstruct

            return reconstruct(self, contract)
        self._assert_store_layout()
        root_fd = self._open_owned_directory(self.root)
        attempts_fd = self._open_owned_directory(self._attempts_root)
        launches_fd = self._open_owned_directory(self._launches_root)
        staging_fd = self._open_owned_directory(self._staging_root)
        try:
            return self._read_resume_state_bound(
                root_fd=root_fd,
                attempts_fd=attempts_fd,
                launches_fd=launches_fd,
                staging_fd=staging_fd,
                contract=contract,
                expected_payload_versions=expected_payload_versions,
            )
        finally:
            os.close(staging_fd)
            os.close(launches_fd)
            os.close(attempts_fd)
            os.close(root_fd)

    def _read_resume_state_bound(
        self,
        *,
        root_fd: int,
        attempts_fd: int,
        launches_fd: int,
        staging_fd: int,
        contract: DataDrivenContract,
        expected_payload_versions: Mapping[str, int] | None = None,
    ) -> ResumeState:
        """Reconstruct state while all store-owned directory identities stay open."""

        try:
            os.stat("result.json", dir_fd=root_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise ValueError("a terminal session result exists; terminal runs cannot resume")
        try:
            staging_entries = os.listdir(staging_fd)
        except OSError as error:
            raise ValueError(f"session staging root could not be inspected: {error}") from error
        if staging_entries:
            raise ValueError("unpublished staging state exists; resume refuses partial attempts")

        try:
            launch_entries = sorted(os.listdir(launches_fd))
        except OSError as error:
            raise ValueError(f"launch-intent directory could not be inspected: {error}") from error
        launch_indices: list[int] = []
        launch_identities: dict[int, tuple[int, int]] = {}
        for entry in launch_entries:
            try:
                info = os.stat(entry, dir_fd=launches_fd, follow_symlinks=False)
            except OSError as error:
                raise ValueError(
                    f"launch-intent entry {entry} could not be inspected: {error}"
                ) from error
            stem, suffix = os.path.splitext(entry)
            if (
                stat.S_ISLNK(info.st_mode)
                or not stat.S_ISREG(info.st_mode)
                or suffix != ".json"
                or len(stem) != 4
                or not stem.isdigit()
                or int(stem) <= 0
            ):
                raise ValueError(
                    f"launch-intent entry {entry!r} is not a numeric regular JSON leaf"
                )
            index = int(stem)
            launch_indices.append(index)
            launch_identities[index] = (info.st_dev, info.st_ino)
        expected_launch_indices = list(range(1, len(launch_indices) + 1))
        if launch_indices != expected_launch_indices:
            raise ValueError(
                "launch intents are not contiguous: "
                f"observed {launch_indices}, expected {expected_launch_indices}"
            )

        try:
            entries = sorted(os.listdir(attempts_fd))
        except OSError as error:
            raise ValueError(f"attempt directory could not be inspected: {error}") from error
        indices: list[int] = []
        attempt_identities: dict[int, tuple[int, int]] = {}
        for entry in entries:
            try:
                info = os.stat(entry, dir_fd=attempts_fd, follow_symlinks=False)
            except OSError as error:
                raise ValueError(f"attempt entry {entry} could not be inspected: {error}") from error
            if (
                stat.S_ISLNK(info.st_mode)
                or not stat.S_ISDIR(info.st_mode)
                or len(entry) != 4
                or not entry.isdigit()
                or int(entry) <= 0
            ):
                raise ValueError(f"attempt entry {entry!r} is not a numeric real directory")
            index = int(entry)
            indices.append(index)
            attempt_identities[index] = (info.st_dev, info.st_ino)
        expected_indices = list(range(1, len(indices) + 1))
        if indices != expected_indices:
            raise ValueError(
                f"attempt records are not contiguous: observed {indices}, expected {expected_indices}"
            )
        if len(launch_indices) < len(indices):
            raise ValueError("a completed attempt lacks its pre-spawn launch intent")
        if len(launch_indices) > len(indices):
            raise ValueError(
                "an uncommitted launch intent exists; resume refuses a hidden retry"
            )
        if launch_indices != indices:
            raise ValueError("launch intents and completed attempts are not one-to-one")

        records: dict[int, tuple[AttemptRecord, bytes, AttemptFeedback, bytes]] = {}
        seen: dict[tuple[str, str], int] = {}
        recurrence: list[RecurrencePair] = []
        accounted = 0.0
        contract_sha256: str | None = None
        for index in indices:
            loaded = self._load_attempt_for_resume_bound(
                index,
                attempts_fd=attempts_fd,
                contract=contract,
                expected_identity=attempt_identities[index],
                expected_payload_versions=expected_payload_versions,
            )
            record, _, feedback, _ = loaded
            if contract_sha256 is None:
                contract_sha256 = record.evaluation.contract_sha256
            elif record.evaluation.contract_sha256 != contract_sha256:
                raise ValueError("attempt records bind more than one contract digest")
            accounted += record.elapsed_seconds
            pair = (
                record.candidate_inventory.tree_sha256,
                feedback.normalized_verifier_signature,
            )
            if pair not in seen:
                seen[pair] = index
                recurrence.append(
                    RecurrencePair(
                        candidate_sha256=pair[0],
                        normalized_verifier_signature=pair[1],
                        first_attempt_index=index,
                    )
                )
            records[index] = loaded

        best_identity: BestAttemptIdentity | None = None
        try:
            os.stat("best.json", dir_fd=root_fd, follow_symlinks=False)
        except FileNotFoundError:
            self._best_loaded = True
            self._best_expected_present = False
            self._best_leaf_snapshot = None
        else:
            try:
                best_bytes, best_snapshot = _read_regular_bounded_fd(
                    root_fd,
                    "best.json",
                    max_bytes=MAX_CANDIDATE_FILE_BYTES,
                )
            except ArtifactError as error:
                raise ValueError(f"best pointer could not be read safely: {error}") from error
            self._best_loaded = True
            self._best_expected_present = True
            self._best_leaf_snapshot = best_snapshot
            best_document = _strict_object_bytes(best_bytes, label="best.json")
            if set(best_document) != {
                "schema_version",
                "run_id",
                "attempt",
                "attempt_manifest_sha256",
                "candidate_sha256",
            }:
                raise ValueError("best pointer has an unknown or missing field")
            if canonical_json_bytes(best_document) != best_bytes:
                raise ValueError("best pointer is not canonically encoded")
            if not isinstance(best_document["schema_version"], int) or isinstance(
                best_document["schema_version"], bool
            ):
                raise ValueError(  # noqa: TRY004 - persisted evidence is invalid
                    "best pointer schema version must be an integer"
                )
            if not isinstance(best_document["attempt"], int) or isinstance(
                best_document["attempt"], bool
            ):
                raise ValueError(  # noqa: TRY004 - persisted evidence is invalid
                    "best pointer attempt must be an integer"
                )
            try:
                attempt_index = best_document["attempt"]
                best_identity = BestAttemptIdentity(
                    attempt_index=attempt_index,
                    attempt_manifest_sha256=best_document["attempt_manifest_sha256"],
                    candidate_sha256=best_document["candidate_sha256"],
                )
            except (KeyError, TypeError, ValueError, ValidationError) as error:
                raise ValueError(f"best pointer is invalid: {error}") from error
            if best_document["schema_version"] != FIXED_STORE_SCHEMA_VERSION:
                raise ValueError("best pointer schema version is unsupported")
            if best_document["run_id"] != self.run_id:
                raise ValueError("best pointer belongs to a different run")
            selected = records.get(attempt_index)
            if selected is None:
                raise ValueError("best pointer names a missing attempt")
            record, attempt_bytes, _, _ = selected
            if (
                sha256_hex(attempt_bytes) != best_identity.attempt_manifest_sha256
                or record.candidate_inventory.tree_sha256 != best_identity.candidate_sha256
            ):
                raise ValueError("best pointer does not match its immutable attempt evidence")

        eligible = [loaded[0] for loaded in records.values() if loaded[0].best_eligible]
        expected_best = min(
            eligible,
            key=lambda record: best_key(contract, record.evaluation),
            default=None,
        )
        if expected_best is None:
            if best_identity is not None:
                raise ValueError("best pointer names an attempt that is not eligible")
        else:
            if best_identity is None:
                raise ValueError("eligible attempts exist without a complete best pointer")
            expected_attempt_bytes = records[expected_best.attempt_index][1]
            if (
                best_identity.attempt_index != expected_best.attempt_index
                or best_identity.attempt_manifest_sha256 != sha256_hex(expected_attempt_bytes)
                or best_identity.candidate_sha256
                != expected_best.candidate_inventory.tree_sha256
            ):
                raise ValueError("best pointer does not name the deterministic best attempt")

        prior_feedback_bytes: bytes | None = None
        prior_feedback_sha256: str | None = None
        if indices:
            _, _, _, prior_feedback_bytes = records[indices[-1]]
            prior_feedback_sha256 = sha256_hex(prior_feedback_bytes)
        for index, expected_identity in attempt_identities.items():
            current = os.stat(
                f"{index:04d}",
                dir_fd=attempts_fd,
                follow_symlinks=False,
            )
            if (current.st_dev, current.st_ino) != expected_identity:
                raise ValueError(
                    f"attempt {index:04d} changed from its enumerated identity"
                )
        for index, expected_identity in launch_identities.items():
            current = os.stat(
                f"{index:04d}.json",
                dir_fd=launches_fd,
                follow_symlinks=False,
            )
            if (current.st_dev, current.st_ino) != expected_identity:
                raise ValueError(
                    f"launch intent {index:04d} changed from its enumerated identity"
                )
        self._assert_store_layout()
        return ResumeState(
            next_attempt_index=len(indices) + 1,
            best_attempt_identity=best_identity,
            seen_recurrence_pairs=tuple(recurrence),
            accounted_wall_seconds=accounted,
            prior_feedback_bytes=prior_feedback_bytes,
            prior_feedback_sha256=prior_feedback_sha256,
        )

    def publish_result(self, result: SessionResult) -> Path:
        """Append the terminal session claim without changing an attempt or pointer."""

        self._assert_store_layout()
        validated = SessionResult.model_validate(result.model_dump(mode="python"))
        if validated.run_id != self.run_id:
            raise ValueError("session result belongs to a different run")
        destination = self.root / "result.json"
        try:
            publish_leaf_atomic(
                self.root,
                "result.json",
                canonical_json_bytes(validated),
                expected_root=self._directory_identities[self.root],
            )
        except ArtifactError as error:
            raise FileExistsError(destination) from error
        return destination
