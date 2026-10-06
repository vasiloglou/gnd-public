"""Shared session evidence types and bounded candidate intake."""
from __future__ import annotations

import json
import mimetypes
import os
import stat
from collections.abc import Mapping
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

from gnd import input_policy as _rf7_input
from gnd.agents import AgentAdapterId, InvocationResult
from gnd.artifacts import (
    Sha256,
    canonical_json_bytes,
    reject_json_constant,
    reject_json_duplicate_pairs,
    sha256_hex,
    tree_sha256_from_inventory,
)
from gnd.assurance_transport import ArchivedAssuranceReceipt
from gnd.exp.declared_invocation import DeclaredInvocationResult
from gnd.exp.session_contract import (
    RankingMetric,
)
from gnd.exp.session_eval import (
    AttemptEvaluation,
    SessionRedaction,
)
from gnd.payloads import (
    MODEL_BOUND_PAYLOAD_SCHEMA_VERSIONS,
    PAYLOAD_SCHEMA_VERSION,
)

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



def _strict_object_bytes(data: bytes, *, label: str) -> dict[str, Any]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"{label} is not UTF-8: {error}") from error



    decoder = _rf7_input.JSONDecoder(
        parse_constant=reject_json_constant,
        object_pairs_hook=reject_json_duplicate_pairs,
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
        return cls.model_validate(_rf7_input.loads(raw), *args, **kwargs)

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
        return cls.model_validate(_rf7_input.loads(json_data), *args, **kwargs)

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
        return cls.model_validate(_rf7_input.loads(json_data), *args, **kwargs)

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
        payload = _rf7_input.loads(raw)
    except ValueError:
        return wire
    version = payload.get("schema_version") if isinstance(payload, dict) else None
    admitted = {wire, wire - 2} if wire in MODEL_BOUND_PAYLOAD_SCHEMA_VERSIONS else {wire}
    legacy = getattr(wire, "legacy_version", None)
    if wire == 7 and legacy in {5, 6}:
        admitted.update({legacy, legacy - 2})
    return version if type(version) is int and version in admitted else wire




# Preserve the historical public qualification of moved objects.
_evidence_entry.__module__ = "gnd.exp.session_store"
_version_validation_error.__module__ = "gnd.exp.session_store"
_strict_object_bytes.__module__ = "gnd.exp.session_store"
_create_evidence_parent.__module__ = "gnd.exp.session_store"
_write_new_file.__module__ = "gnd.exp.session_store"
CandidateFile.__module__ = "gnd.exp.session_store"
CandidateInventory.__module__ = "gnd.exp.session_store"
EvidenceFile.__module__ = "gnd.exp.session_store"
VerifierPayloadEvidence.__module__ = "gnd.exp.session_store"
LaunchIntent.__module__ = "gnd.exp.session_store"
DeclaredLaunchIntent.__module__ = "gnd.exp.session_store"
_DeclaredLaunchIntentV3.__module__ = "gnd.exp.session_store"
_DeclaredLaunchIntentV4.__module__ = "gnd.exp.session_store"
DeclaredLaunchIntent.__module__ = "gnd.exp.session_store"
CandidateEdit.__module__ = "gnd.exp.session_store"
RankingObservation.__module__ = "gnd.exp.session_store"
_AttemptRecordBase.__module__ = "gnd.exp.session_store"
_AttemptRecordV1.__module__ = "gnd.exp.session_store"
_AttemptRecordV2.__module__ = "gnd.exp.session_store"
_AttemptRecordV3.__module__ = "gnd.exp.session_store"
_AttemptRecordV4.__module__ = "gnd.exp.session_store"
_AttemptRecordV5.__module__ = "gnd.exp.session_store"
_AttemptRecordV6.__module__ = "gnd.exp.session_store"
_AttemptRecordV7.__module__ = "gnd.exp.session_store"
_AttemptRecordV8.__module__ = "gnd.exp.session_store"
_AttemptRecordV9.__module__ = "gnd.exp.session_store"
JudgmentEvidence.__module__ = "gnd.exp.session_store"
_AttemptRecordV10.__module__ = "gnd.exp.session_store"
AttemptRecord.__module__ = "gnd.exp.session_store"
SessionOutcome.__module__ = "gnd.exp.session_store"
_SessionResultBase.__module__ = "gnd.exp.session_store"
_SessionResultV1.__module__ = "gnd.exp.session_store"
_SessionResultV2.__module__ = "gnd.exp.session_store"
_SessionResultV3.__module__ = "gnd.exp.session_store"
_SessionResultV4.__module__ = "gnd.exp.session_store"
WalkFloorResult.__module__ = "gnd.exp.session_store"
_SessionResultV5.__module__ = "gnd.exp.session_store"
_SessionResultV6.__module__ = "gnd.exp.session_store"
_SessionResultV7.__module__ = "gnd.exp.session_store"
SessionResult.__module__ = "gnd.exp.session_store"
BestAttemptIdentity.__module__ = "gnd.exp.session_store"
RecurrencePair.__module__ = "gnd.exp.session_store"
ResumeState.__module__ = "gnd.exp.session_store"
StagedCandidate.__module__ = "gnd.exp.session_store"
_CollectedFile.__module__ = "gnd.exp.session_store"
_classify.__module__ = "gnd.exp.session_store"
_collect_candidate.__module__ = "gnd.exp.session_store"
_retained_wire.__module__ = "gnd.exp.session_store"
_DeclaredLaunchIntentV2.__module__ = "gnd.exp.session_store"

# Preserve qualification on methods as well as their containing wire types.
for _wire_type in (
    CandidateFile, CandidateInventory, EvidenceFile, VerifierPayloadEvidence,
    LaunchIntent, _DeclaredLaunchIntentV2, _DeclaredLaunchIntentV3,
    _DeclaredLaunchIntentV4, DeclaredLaunchIntent, CandidateEdit, RankingObservation,
    _AttemptRecordBase, _AttemptRecordV1, _AttemptRecordV2, _AttemptRecordV3,
    _AttemptRecordV4, _AttemptRecordV5, _AttemptRecordV6, _AttemptRecordV7,
    _AttemptRecordV8, _AttemptRecordV9, JudgmentEvidence, _AttemptRecordV10,
    AttemptRecord, SessionOutcome, _SessionResultBase, _SessionResultV1,
    _SessionResultV2, _SessionResultV3, _SessionResultV4, WalkFloorResult,
    _SessionResultV5, _SessionResultV6, _SessionResultV7, SessionResult,
    BestAttemptIdentity, RecurrencePair, ResumeState, StagedCandidate, _CollectedFile,
):
    for _method in vars(_wire_type).values():
        if isinstance(_method, (classmethod, staticmethod)):
            _method = _method.__func__
        if getattr(_method, '__module__', None) == __name__:
            _method.__module__ = 'gnd.exp.session_store'
del _wire_type, _method
