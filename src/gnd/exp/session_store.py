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

import json  # noqa: F401 -- historical compatibility binding
import math
import mimetypes  # noqa: F401 -- historical compatibility binding
import os
import secrets
import shutil
import stat
from collections.abc import Mapping
from contextlib import suppress
from dataclasses import dataclass, field  # noqa: F401 -- historical compatibility binding
from enum import StrEnum  # noqa: F401 -- historical compatibility binding
from pathlib import Path, PurePosixPath
from typing import Annotated, Any, Literal, Self  # noqa: F401 -- historical compatibility binding

from pydantic import (
    BaseModel,  # noqa: F401 -- historical compatibility binding
    ConfigDict,  # noqa: F401 -- historical compatibility binding
    Field,  # noqa: F401 -- historical compatibility binding
    StringConstraints,  # noqa: F401 -- historical compatibility binding
    ValidationError,
    field_validator,  # noqa: F401 -- historical compatibility binding
    model_serializer,  # noqa: F401 -- historical compatibility binding
    model_validator,  # noqa: F401 -- historical compatibility binding
)

from gnd import input_policy as _rf7_input  # noqa: F401 -- historical compatibility binding
from gnd.agents import AgentAdapterId, InvocationResult
from gnd.artifacts import (
    ArtifactError,
    LeafSnapshot,
    Sha256,  # noqa: F401 -- historical compatibility binding
    _clear_directory_fd,
    _exchange_paths_atomic,
    _read_regular_bounded_fd,
    canonical_json_bytes,
    publish_directory_once,
    publish_leaf_atomic,
    read_regular_bounded,
    reject_json_constant,  # noqa: F401 -- historical compatibility binding
    reject_json_duplicate_pairs,  # noqa: F401 -- historical compatibility binding
    sha256_hex,
    tree_sha256_from_inventory,  # noqa: F401 -- historical compatibility binding
)
from gnd.assurance_transport import (
    ArchivedAssuranceReceipt,  # noqa: F401 -- historical compatibility binding
)
from gnd.exp.declared_invocation import DeclaredInvocationResult
from gnd.exp.session_contract import (
    DataDrivenContract,
    RankingMetric,  # noqa: F401 -- historical compatibility binding
    TestsAcceptance,
    TransitionAcceptance,
)
from gnd.exp.session_eval import (
    AttemptEvaluation,
    AttemptFeedback,
    SessionRedaction,  # noqa: F401 -- historical compatibility binding
    VerifierPayloadError,
    attach_walk_floor_steps,
    best_key,
    canonical_feedback,
    normalized_verifier_signature,
    validate_tests_payload,
    validate_transition_payload,
    validate_verifier_payload,
)
from gnd.exp.session_records import (
    ASSURANCE_EVIDENCE_SCHEMA_VERSION as ASSURANCE_EVIDENCE_SCHEMA_VERSION,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    DECLARED_ADAPTER_EVIDENCE_SCHEMA_VERSION as DECLARED_ADAPTER_EVIDENCE_SCHEMA_VERSION,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    DECLARED_LAUNCH_SCHEMA_VERSION as DECLARED_LAUNCH_SCHEMA_VERSION,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    DERIVATION_EVIDENCE_SCHEMA_VERSION as DERIVATION_EVIDENCE_SCHEMA_VERSION,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    DIRECTORY_MODE as DIRECTORY_MODE,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    EVIDENCE_SCHEMA_VERSION as EVIDENCE_SCHEMA_VERSION,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    FILE_MODE as FILE_MODE,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    FIXED_STORE_SCHEMA_VERSION as FIXED_STORE_SCHEMA_VERSION,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    LEGACY_EVIDENCE_SCHEMA_VERSION as LEGACY_EVIDENCE_SCHEMA_VERSION,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    MAX_CANDIDATE_DEPTH as MAX_CANDIDATE_DEPTH,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    MAX_CANDIDATE_FILE_BYTES as MAX_CANDIDATE_FILE_BYTES,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    MAX_CANDIDATE_FILES as MAX_CANDIDATE_FILES,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    MAX_CANDIDATE_TOTAL_BYTES as MAX_CANDIDATE_TOTAL_BYTES,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    MAX_RETAINED_STREAM_BYTES as MAX_RETAINED_STREAM_BYTES,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    MAX_SESSION_RESULT_BYTES as MAX_SESSION_RESULT_BYTES,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    MAX_VERIFIER_PAYLOAD_BYTES as MAX_VERIFIER_PAYLOAD_BYTES,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    REDACTION_EVIDENCE_SCHEMA_VERSION as REDACTION_EVIDENCE_SCHEMA_VERSION,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    REDACTION_RESULT_SCHEMA_VERSION as REDACTION_RESULT_SCHEMA_VERSION,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    SNAPSHOT_EXECUTABLE_FILE_MODE as SNAPSHOT_EXECUTABLE_FILE_MODE,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    SNAPSHOT_FILE_MODE as SNAPSHOT_FILE_MODE,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    TRANSITION_EVIDENCE_SCHEMA_VERSION as TRANSITION_EVIDENCE_SCHEMA_VERSION,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    TRANSITION_RESULT_SCHEMA_VERSION as TRANSITION_RESULT_SCHEMA_VERSION,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    WALK_FLOOR_EVIDENCE_SCHEMA_VERSION as WALK_FLOOR_EVIDENCE_SCHEMA_VERSION,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    WALK_FLOOR_RESULT_SCHEMA_VERSION as WALK_FLOOR_RESULT_SCHEMA_VERSION,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    AcceptanceMode as AcceptanceMode,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    AttemptRecord as AttemptRecord,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    BestAttemptIdentity as BestAttemptIdentity,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    CandidateEdit as CandidateEdit,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    CandidateFile as CandidateFile,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    CandidateInventory as CandidateInventory,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    DeclaredLaunchIntent as DeclaredLaunchIntent,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    EvidenceFile as EvidenceFile,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    JudgmentEvidence as JudgmentEvidence,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    LaunchIntent as LaunchIntent,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    LegacyAcceptanceMode as LegacyAcceptanceMode,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    NonEmptyString as NonEmptyString,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    RankingObservation as RankingObservation,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    RecurrencePair as RecurrencePair,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    ResumeState as ResumeState,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    SessionOutcome as SessionOutcome,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    SessionResult as SessionResult,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    StagedCandidate as StagedCandidate,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    VerifierPayloadEvidence as VerifierPayloadEvidence,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    WalkFloorResult as WalkFloorResult,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _AttemptRecordBase as _AttemptRecordBase,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _AttemptRecordV1 as _AttemptRecordV1,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _AttemptRecordV2 as _AttemptRecordV2,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _AttemptRecordV3 as _AttemptRecordV3,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _AttemptRecordV4 as _AttemptRecordV4,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _AttemptRecordV5 as _AttemptRecordV5,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _AttemptRecordV6 as _AttemptRecordV6,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _AttemptRecordV7 as _AttemptRecordV7,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _AttemptRecordV8 as _AttemptRecordV8,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _AttemptRecordV9 as _AttemptRecordV9,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _AttemptRecordV10 as _AttemptRecordV10,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _classify as _classify,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _collect_candidate as _collect_candidate,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _CollectedFile as _CollectedFile,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _create_evidence_parent as _create_evidence_parent,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _DeclaredLaunchIntentV2 as _DeclaredLaunchIntentV2,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _DeclaredLaunchIntentV3 as _DeclaredLaunchIntentV3,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _DeclaredLaunchIntentV4 as _DeclaredLaunchIntentV4,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _evidence_entry as _evidence_entry,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _retained_wire as _retained_wire,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _SessionResultBase as _SessionResultBase,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _SessionResultV1 as _SessionResultV1,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _SessionResultV2 as _SessionResultV2,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _SessionResultV3 as _SessionResultV3,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _SessionResultV4 as _SessionResultV4,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _SessionResultV5 as _SessionResultV5,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _SessionResultV6 as _SessionResultV6,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _SessionResultV7 as _SessionResultV7,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _strict_object_bytes as _strict_object_bytes,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _version_validation_error as _version_validation_error,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.exp.session_records import (
    _write_new_file as _write_new_file,  # noqa: PLC0414 -- compatibility re-export
)
from gnd.payloads import (
    MODEL_BOUND_PAYLOAD_SCHEMA_VERSIONS,  # noqa: F401 -- historical compatibility binding
    PAYLOAD_SCHEMA_VERSION,  # noqa: F401 -- historical compatibility binding
)

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
            raise ValueError(  # noqa: TRY004 -- preserve predecessor refusal contract
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

    def best_identity(self) -> BestAttemptIdentity | None:
        """Identity selected by the most recent validated reconstruction."""
        return getattr(self, "_best_identity", None)

    def best_record(self) -> AttemptRecord | None:
        """Selected patch-session attempt, after validated reconstruction."""
        best = getattr(self, "_v7_best", None)
        return None if best is None else best[0]

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

        if contract.profile.patch:
            from gnd.exp.session_replay import reconstruct

            return reconstruct(self, contract)
        self._assert_store_layout()
        root_fd = self._open_owned_directory(self.root)
        attempts_fd = self._open_owned_directory(self._attempts_root)
        launches_fd = self._open_owned_directory(self._launches_root)
        staging_fd = self._open_owned_directory(self._staging_root)
        try:
            state = self._read_resume_state_bound(
                root_fd=root_fd,
                attempts_fd=attempts_fd,
                launches_fd=launches_fd,
                staging_fd=staging_fd,
                contract=contract,
                expected_payload_versions=expected_payload_versions,
            )
            self._best_identity = state.best_attempt_identity
            return state
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
                raise ValueError(  # noqa: TRY004 -- preserve predecessor refusal contract
                    "best pointer schema version must be an integer"
                )
            if not isinstance(best_document["attempt"], int) or isinstance(
                best_document["attempt"], bool
            ):
                raise ValueError(  # noqa: TRY004 -- preserve predecessor refusal contract
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
