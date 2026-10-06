"""Closed evidence models for staged ORM evolution."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from enum import StrEnum
from pathlib import Path, PurePosixPath, PureWindowsPath
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

LEGACY_EVOLUTION_SCHEMA_VERSION = 1
#: /2 the locator wire, /3 the tracked-roster wire (v5.1 Phase 3, D-P3.4). A
#: linked project is identified by the leaves the CALLER listed. Read
#: compatibility is total; only STARTING or FINISHING is version-restricted.
LOCATOR_EVOLUTION_SCHEMA_VERSION = 2
EVOLUTION_SCHEMA_VERSION = 3
EVOLUTION_SCHEMA_VERSIONS = (1, 2, 3)

#: The stable name a finalization refusal carries when the pending state
#: predates the roster wire, so a caller branches on the rule, not a substring.
EVOLUTION_READ_ONLY_PENDING = "evolution:old-pending-read-only"

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
StableId = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$",
    ),
]
Sha256String = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
_CONFORMANCE_EXIT_PRECEDENCE = {0: 0, 13: 1, 3: 2, 66: 3, 74: 4}


class _FrozenDict(dict[str, Any]):
    """A JSON mapping that serializes normally but rejects every mutation."""

    @staticmethod
    def _immutable(*_args: Any, **_kwargs: Any) -> None:
        raise TypeError("evolution evidence is recursively immutable")

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear = _immutable
    pop = _immutable
    popitem = _immutable
    setdefault = _immutable
    update = _immutable


def _freeze_json(value: Any) -> Any:
    if isinstance(value, dict):
        return _FrozenDict({str(key): _freeze_json(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json(item) for item in value)
    return value


def _canonical_json(value: Any) -> str:
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="json")
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def conformance_payload_sha256(value: Any) -> str:
    rendered = json.dumps(
        value,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
        allow_nan=False,
    )
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


class _ClosedFrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _version_validation_error(model_name: str, version: Any) -> ValidationError:
    return ValidationError.from_exception_data(
        model_name,
        [
            {
                "type": "literal_error",
                "loc": ("schema_version",),
                "input": version,
                "ctx": {
                    "expected": ", ".join(map(str, EVOLUTION_SCHEMA_VERSIONS))
                },
            }
        ],
    )


def _json_document(value: str | bytes | bytearray) -> Any:
    if isinstance(value, bytearray):
        value = bytes(value)
    return _rf7_input.loads(value)


def _relative_posix(value: Any, field: str) -> str:
    """The one spelling rule for every caller-supplied relative path here:
    shared by the project locator and by each roster leaf, so a path one would
    refuse cannot be admissible to the other; and decidable from the STRING
    with no filesystem access, which is what lets a hostile roster be rejected
    before anything is opened."""

    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a nonempty relative path")
    if "\x00" in value:
        raise ValueError(f"{field} contains a NUL byte")
    if value != value.strip() or "\\" in value:
        raise ValueError(f"{field} must use normalized POSIX spelling")
    posix, windows = PurePosixPath(value), PureWindowsPath(value)
    if (
        posix.is_absolute()
        or windows.is_absolute()
        or bool(posix.root)
        or bool(windows.root)
        or bool(windows.drive)
        or value.startswith(("/", "\\"))
    ):
        raise ValueError(f"{field} must be relative")
    if any(part in {"", ".", ".."} for part in posix.parts) or ".." in windows.parts:
        raise ValueError(f"{field} contains a parent or non-normal component")
    if not posix.parts or value != PurePosixPath(*posix.parts).as_posix():
        raise ValueError(f"{field} must use normalized POSIX spelling")
    return value


class ProjectLocator(_ClosedFrozenModel):
    """One lexical project coordinate relative to the trusted allowed root."""

    base: Literal["allowed-project-root"]
    path: str

    @field_validator("path")
    @classmethod
    def _normalized_relative_posix_path(cls, value: str) -> str:
        return _relative_posix(value, "project locator path")


class TrackedRoster(_ClosedFrozenModel):
    """The leaves a caller declares this project to consist of.

    ``gnd`` never derives these paths and never consults Git; it reads only what
    it is handed and has no opinion about anything absent from it (r2 R5). An
    EMPTY roster is legal and explicit -- a narrower claim than the whole tree,
    not a missing field.
    """

    schema_version: Literal[1] = 1
    paths: tuple[str, ...] = ()

    @field_validator("paths")
    @classmethod
    def _sorted_unique_leaves(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for path in value:
            _relative_posix(path, "tracked roster path")
        if len(set(value)) != len(value):
            raise ValueError("tracked roster paths must be unique")
        if list(value) != sorted(value):
            raise ValueError("tracked roster paths must be sorted")
        return value


class CommittedText(_ClosedFrozenModel):
    """Exact UTF-8 text bytes together with their media type and identity."""

    media_type: NonEmptyString
    encoding: Literal["utf-8"] = "utf-8"
    text: str
    sha256: Sha256String

    @classmethod
    def from_text(cls, text: str, *, media_type: str) -> CommittedText:
        return cls(
            media_type=media_type,
            encoding="utf-8",
            text=text,
            sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        )

    @model_validator(mode="after")
    def _digest_matches(self) -> CommittedText:
        actual = hashlib.sha256(self.text.encode(self.encoding)).hexdigest()
        if actual != self.sha256:
            raise ValueError(f"text digest mismatch: declared {self.sha256}, computed {actual}")
        return self


class EvolutionOperationKind(StrEnum):
    ADD = "add"
    MODIFY = "modify"
    RENAME = "rename"
    DELETE = "delete"


class ElementLocator(_ClosedFrozenModel):
    """One top-level, id-addressed model element.

    ``operations`` joins the collection literal for ORM+ v2. It is admitted so
    that a purely ADDITIVE operation delta — the shape of ordinary feature work
    after adoption — has a tool that owns it; every other operation delta is
    refused by the service's gate, not by this literal."""

    locator_kind: Literal["element"] = "element"
    collection: Literal["object_types", "fact_types", "operations"]
    element_id: NonEmptyString

    def reference(self) -> str:
        return f"{self.collection}[{self.element_id}]"


class RoleLocator(_ClosedFrozenModel):
    locator_kind: Literal["role"] = "role"
    fact_type_id: NonEmptyString
    role_name: NonEmptyString

    def reference(self) -> str:
        return f"fact_types[{self.fact_type_id}].roles[{self.role_name}]"


class ConstraintLocator(_ClosedFrozenModel):
    locator_kind: Literal["constraint"] = "constraint"
    host: Literal["model", "fact_type"]
    host_id: NonEmptyString | None = None
    family: NonEmptyString
    canonical_before_sha256: Sha256String | None = None
    duplicate_occurrence: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def _host_identity_is_complete(self) -> ConstraintLocator:
        if self.host == "fact_type" and self.host_id is None:
            raise ValueError("fact_type constraint locators require host_id")
        if self.host == "model" and self.host_id is not None:
            raise ValueError("model constraint locators cannot carry host_id")
        return self

    def reference(self) -> str:
        host = "model" if self.host == "model" else f"fact_types[{self.host_id}]"
        identity = self.canonical_before_sha256 or "new"
        return f"{host}.constraints[{self.family}:{identity}:{self.duplicate_occurrence}]"


class ModelIdentityLocator(_ClosedFrozenModel):
    """The atomic top-level ``version``/``model_id`` identity pair."""

    locator_kind: Literal["model-identity"] = "model-identity"

    def reference(self) -> str:
        return "model.identity"


StableLocator = ElementLocator | RoleLocator | ConstraintLocator | ModelIdentityLocator


class EvolutionOperation(_ClosedFrozenModel):
    operation_id: StableId
    kind: EvolutionOperationKind
    locator: StableLocator
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    before_sha256: Sha256String | None = None
    after_sha256: Sha256String | None = None

    @field_validator("before", "after")
    @classmethod
    def _freeze_values(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        return _freeze_json(value) if value is not None else None

    @model_validator(mode="after")
    def _shape_and_digests(self) -> EvolutionOperation:
        if self.kind is EvolutionOperationKind.ADD:
            if self.before is not None or self.after is None:
                raise ValueError("add operations require after and forbid before")
        elif self.kind is EvolutionOperationKind.DELETE:
            if self.before is None or self.after is not None:
                raise ValueError("delete operations require before and forbid after")
        elif self.before is None or self.after is None:
            raise ValueError(f"{self.kind.value} operations require before and after")

        actual_before = canonical_sha256(self.before) if self.before is not None else None
        actual_after = canonical_sha256(self.after) if self.after is not None else None
        if self.before_sha256 is not None and self.before_sha256 != actual_before:
            raise ValueError("before_sha256 does not identify before")
        if self.after_sha256 is not None and self.after_sha256 != actual_after:
            raise ValueError("after_sha256 does not identify after")
        object.__setattr__(self, "before_sha256", actual_before)
        object.__setattr__(self, "after_sha256", actual_after)

        if isinstance(self.locator, ElementLocator):
            if self.before is not None and self.before.get("id") != self.locator.element_id:
                raise ValueError("before id must match the stable element locator")
            if self.kind is EvolutionOperationKind.RENAME:
                if self.after.get("id") in {None, self.locator.element_id}:
                    raise ValueError("rename after must carry a distinct stable id")
            elif self.after is not None and self.after.get("id") != self.locator.element_id:
                raise ValueError("after id must match the stable element locator")
        elif isinstance(self.locator, RoleLocator):
            if self.before is not None and self.before.get("role_name") != self.locator.role_name:
                raise ValueError("before role_name must match the stable role locator")
            if self.kind is EvolutionOperationKind.RENAME:
                if self.after.get("role_name") in {None, self.locator.role_name}:
                    raise ValueError("rename after must carry a distinct role_name")
            elif self.after is not None and self.after.get("role_name") != self.locator.role_name:
                raise ValueError("after role_name must match the stable role locator")
        elif isinstance(self.locator, ModelIdentityLocator):
            if self.kind is not EvolutionOperationKind.MODIFY:
                raise ValueError("model identity operations must use modify")
            identity_keys = {"version", "model_id"}
            if set(self.before or {}) != identity_keys or set(self.after or {}) != identity_keys:
                raise ValueError(
                    "model identity before and after must contain exactly version and model_id"
                )
        else:
            if self.kind is EvolutionOperationKind.RENAME:
                raise ValueError("constraints cannot be renamed because they have no stable id")
            if self.before is None:
                if self.locator.canonical_before_sha256 is not None:
                    raise ValueError("new constraint locators cannot claim a before identity")
            elif self.locator.canonical_before_sha256 != actual_before:
                raise ValueError("constraint locator does not bind the canonical before value")
            value = self.after if self.after is not None else self.before
            if value is not None and value.get("type") != self.locator.family:
                raise ValueError("constraint family must match the stable locator")
        return self

    def reference(self) -> str:
        return self.locator.reference()


class EvolutionOperationAudit(_ClosedFrozenModel):
    """Who requested an operation; never a constraint provenance source."""

    actor_id: NonEmptyString
    origin: NonEmptyString
    requested_at: datetime

    @field_validator("requested_at")
    @classmethod
    def _timezone_required(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("requested_at must be timezone-aware")
        return value


def _unsafe_project_path(value: str) -> str | None:
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    if ".." in posix.parts or ".." in windows.parts:
        return "parent traversal is forbidden"
    if windows.drive and not windows.is_absolute():
        return "drive-relative paths are forbidden"
    if re.match(r"^[A-Za-z]:", value) and not windows.is_absolute():
        return "drive-relative paths are forbidden"
    return None


class ArtifactLocator(_ClosedFrozenModel):
    """A digest-bound, explicitly supplied downstream artifact reference."""

    locator_kind: Literal["artifact"] = "artifact"
    artifact_id: StableId
    artifact_kind: Literal[
        "population",
        "provenance",
        "verbalization",
        "generated-code",
        "extension-code",
        "documentation",
        "supplied-artifact",
    ]
    path: NonEmptyString
    sha256: Sha256String
    references: tuple[NonEmptyString, ...] = Field(min_length=1)

    @field_validator("path")
    @classmethod
    def _relative_path_only(cls, value: str) -> str:
        issue = _unsafe_project_path(value)
        if issue:
            raise ValueError(issue)
        if "\x00" in value:
            raise ValueError("NUL bytes are forbidden in artifact paths")
        if PurePosixPath(value).is_absolute() or PureWindowsPath(value).is_absolute():
            raise ValueError("artifact paths must be relative")
        return value

    @model_validator(mode="after")
    def _references_are_stable(self) -> ArtifactLocator:
        if tuple(sorted(set(self.references))) != self.references:
            raise ValueError("artifact references must be unique and sorted")
        return self

    def reference(self) -> str:
        return f"artifacts[{self.artifact_id}]"


class _LinkedProjectV1(_ClosedFrozenModel):
    project_id: StableId
    root: Path
    expected_tree_sha256: Sha256String

    @field_validator("root")
    @classmethod
    def _safe_root(cls, value: Path) -> Path:
        issue = _unsafe_project_path(str(value))
        if issue:
            raise ValueError(issue)
        return value


class _LinkedProjectV2(_ClosedFrozenModel):
    project_id: StableId
    locator: ProjectLocator
    expected_tree_sha256: Sha256String


class _LinkedProjectV3(_ClosedFrozenModel):
    project_id: StableId
    locator: ProjectLocator
    tracked_roster: TrackedRoster
    expected_tracked_tree_sha256: Sha256String


def _refuse_cross_version_project(project: Any, version: int, label: str) -> None:
    """A project must carry exactly the shape its ENVELOPE declares: one class
    reads three wires by holding either coordinate and either identity, and that
    must not become a way to smuggle a v3 roster into a v1 document."""

    if version == LEGACY_EVOLUTION_SCHEMA_VERSION:
        if project.root is None or project.locator is not None:
            raise ValueError(f"version 1 {label}s require root")
    elif project.locator is None or project.root is not None:
        raise ValueError(f"version {version} {label}s require locator")
    if (version == EVOLUTION_SCHEMA_VERSION) != (project.tracked_roster is not None):
        raise ValueError(f"version {version} {label}s carry the wrong tree identity")


def _refuse_foreign_keys(document: Any, carried: frozenset[str], label: str) -> None:
    """A key outside the SELECTED version's set is refused in the RAW document,
    NULL INCLUDED: a serializer drops a null before the self-binding identity is
    recomputed, so two byte-distinct documents would otherwise hash as one."""

    if isinstance(document, dict) and (stray := set(document) - carried):
        raise ValueError(f"{label} cannot carry {sorted(stray)}")


class LinkedProject(_ClosedFrozenModel):
    """Normalized linked-project view preserving its selected wire coordinate."""

    project_id: StableId
    expected_tree_sha256: Sha256String | None = None
    root: Path | None = None
    locator: ProjectLocator | None = None
    tracked_roster: TrackedRoster | None = None
    expected_tracked_tree_sha256: Sha256String | None = None

    @field_validator("root")
    @classmethod
    def _safe_root(cls, value: Path | None) -> Path | None:
        if value is not None and (issue := _unsafe_project_path(str(value))):
            raise ValueError(issue)
        return value

    @model_validator(mode="after")
    def _one_coordinate(self) -> LinkedProject:
        if (self.root is None) == (self.locator is None):
            raise ValueError("linked project requires exactly one coordinate")
        tracked = self.tracked_roster is not None
        if tracked != (self.expected_tracked_tree_sha256 is not None):
            raise ValueError("a tracked roster and its expected identity travel together")
        if tracked == (self.expected_tree_sha256 is not None):
            raise ValueError("linked project requires exactly one tree identity")
        return self

    @model_serializer(mode="wrap")
    def _serialize_selected_coordinate(self, handler):
        document = handler(self)
        document.pop("root" if self.root is None else "locator")
        for key in (
            ("tracked_roster", "expected_tracked_tree_sha256")
            if self.tracked_roster is None
            else ("expected_tree_sha256",)
        ):
            document.pop(key)
        return document


class _EvolutionProposalV1(_ClosedFrozenModel):
    schema_version: Literal[LEGACY_EVOLUTION_SCHEMA_VERSION] = (
        LEGACY_EVOLUTION_SCHEMA_VERSION
    )
    proposal_id: StableId
    expected_model_sha256: Sha256String
    candidate_model: CommittedText
    operations: tuple[EvolutionOperation, ...] = Field(min_length=1)
    rationale: NonEmptyString
    audit: EvolutionOperationAudit
    linked_projects: tuple[_LinkedProjectV1, ...] = ()
    artifacts: tuple[ArtifactLocator, ...] = ()


class _EvolutionProposalV2(_ClosedFrozenModel):
    schema_version: Literal[LOCATOR_EVOLUTION_SCHEMA_VERSION] = LOCATOR_EVOLUTION_SCHEMA_VERSION
    proposal_id: StableId
    expected_model_sha256: Sha256String
    candidate_model: CommittedText
    operations: tuple[EvolutionOperation, ...] = Field(min_length=1)
    rationale: NonEmptyString
    audit: EvolutionOperationAudit
    linked_projects: tuple[_LinkedProjectV2, ...] = ()
    artifacts: tuple[ArtifactLocator, ...] = ()


class _EvolutionProposalV3(_EvolutionProposalV2):
    schema_version: Literal[EVOLUTION_SCHEMA_VERSION] = EVOLUTION_SCHEMA_VERSION
    linked_projects: tuple[_LinkedProjectV3, ...] = ()


class EvolutionProposal(_ClosedFrozenModel):
    schema_version: Literal[1, 2, 3] = EVOLUTION_SCHEMA_VERSION
    proposal_id: StableId
    expected_model_sha256: Sha256String
    candidate_model: CommittedText
    operations: tuple[EvolutionOperation, ...] = Field(min_length=1)
    rationale: NonEmptyString
    audit: EvolutionOperationAudit
    linked_projects: tuple[LinkedProject, ...] = ()
    artifacts: tuple[ArtifactLocator, ...] = ()

    @classmethod
    def model_validate(cls, obj: Any, *args: Any, **kwargs: Any) -> Self:
        if isinstance(obj, cls):
            return obj
        version = obj.get("schema_version") if isinstance(obj, dict) else None
        if version == LEGACY_EVOLUTION_SCHEMA_VERSION:
            reader: type[_ClosedFrozenModel] = _EvolutionProposalV1
        elif version == LOCATOR_EVOLUTION_SCHEMA_VERSION:
            reader = _EvolutionProposalV2
        elif version == EVOLUTION_SCHEMA_VERSION:
            reader = _EvolutionProposalV3
        else:
            raise _version_validation_error(cls.__name__, version)
        parsed = reader.model_validate(obj, *args, **kwargs)
        return super().model_validate(parsed.model_dump(mode="python"))

    @classmethod
    def model_validate_json(
        cls, json_data: str | bytes | bytearray, *args: Any, **kwargs: Any
    ) -> Self:
        return cls.model_validate(_json_document(json_data), *args, **kwargs)

    @model_serializer(mode="wrap")
    def _serialize_wire_version(self, handler):
        document = handler(self)
        for project in document["linked_projects"]:
            if self.schema_version == LEGACY_EVOLUTION_SCHEMA_VERSION:
                project.pop("locator", None)
            else:
                project.pop("root", None)
        return document

    @model_validator(mode="after")
    def _identities_are_unique(self) -> EvolutionProposal:
        operation_ids = [item.operation_id for item in self.operations]
        if len(set(operation_ids)) != len(operation_ids):
            raise ValueError("operation_id values must be unique")
        project_ids = [item.project_id for item in self.linked_projects]
        if len(set(project_ids)) != len(project_ids):
            raise ValueError("linked project_id values must be unique")
        coordinates = [
            str(item.root) if item.root is not None else item.locator.path
            for item in self.linked_projects
        ]
        if len(set(coordinates)) != len(coordinates):
            raise ValueError("linked project coordinates must be unique")
        for project in self.linked_projects:
            _refuse_cross_version_project(project, self.schema_version, "linked project")
        artifact_ids = [item.artifact_id for item in self.artifacts]
        if len(set(artifact_ids)) != len(artifact_ids):
            raise ValueError("artifact_id values must be unique")
        artifact_paths = [item.path for item in self.artifacts]
        if len(set(artifact_paths)) != len(artifact_paths):
            raise ValueError("artifact paths must be unique")
        return self

    @property
    def proposal_sha256(self) -> str:
        return canonical_sha256(self)


class ValidationFinding(_ClosedFrozenModel):
    path: str
    message: str
    rule_id: str
    severity: Literal["error", "warning"]


class ValidationEvidence(_ClosedFrozenModel):
    valid: Literal[True] = True
    warnings: tuple[ValidationFinding, ...]
    model_sha256: Sha256String


class BlastRadiusEntry(_ClosedFrozenModel):
    surface: Literal[
        "model",
        "object-type",
        "fact-type",
        "reading",
        "role",
        "constraint",
        "identifier-reference",
        "population",
        "provenance",
        "verbalization",
        "supplied-artifact",
        # ORM+ v2. An added operation is a real, id-addressed model surface; it
        # would otherwise appear in the radius only as a change to the whole
        # `model` entry, which names nothing a reviewer can act on.
        "operation",
    ]
    reference: NonEmptyString
    change: Literal["added", "modified", "deleted", "affected"]
    operation_ids: tuple[StableId, ...] = Field(min_length=1)
    before_sha256: Sha256String | None = None
    after_sha256: Sha256String | None = None

    @model_validator(mode="after")
    def _identity_shape_matches_change(self) -> BlastRadiusEntry:
        if tuple(sorted(set(self.operation_ids))) != self.operation_ids:
            raise ValueError("blast-radius operation_ids must be unique and sorted")
        if self.change == "added" and (
            self.before_sha256 is not None or self.after_sha256 is None
        ):
            raise ValueError("added blast-radius entries require only an after identity")
        if self.change == "deleted" and (
            self.before_sha256 is None or self.after_sha256 is not None
        ):
            raise ValueError("deleted blast-radius entries require only a before identity")
        if self.change == "modified" and (
            self.before_sha256 is None
            or self.after_sha256 is None
            or self.before_sha256 == self.after_sha256
        ):
            raise ValueError("modified blast-radius entries require distinct identities")
        if self.change == "affected" and (
            self.before_sha256 is None or self.after_sha256 is None
        ):
            raise ValueError("affected blast-radius entries require both identities")
        return self


class BlastRadiusReport(_ClosedFrozenModel):
    schema_version: Literal[1] = 1
    proposal_sha256: Sha256String
    before_model_sha256: Sha256String
    candidate_model_sha256: Sha256String
    entries: tuple[BlastRadiusEntry, ...] = Field(min_length=1)
    report_sha256: Sha256String

    @model_validator(mode="after")
    def _report_is_ordered_and_bound(self) -> BlastRadiusReport:
        ordered = tuple(sorted(self.entries, key=lambda item: (item.reference, item.surface)))
        if ordered != self.entries:
            raise ValueError("blast-radius entries must be sorted by stable reference")
        references = [item.reference for item in self.entries]
        if len(set(references)) != len(references):
            raise ValueError("each blast-radius reference must appear exactly once")
        body = self.model_dump(mode="json", exclude={"report_sha256"})
        if canonical_sha256(body) != self.report_sha256:
            raise ValueError("report_sha256 does not bind the blast-radius report")
        return self


class _EvolutionPreviewV1(_ClosedFrozenModel):
    schema_version: Literal[LEGACY_EVOLUTION_SCHEMA_VERSION] = (
        LEGACY_EVOLUTION_SCHEMA_VERSION
    )
    proposal: _EvolutionProposalV1
    proposal_sha256: Sha256String
    before_model: CommittedText
    candidate_model: CommittedText
    verbalization: CommittedText
    validation: ValidationEvidence
    affected_references: tuple[NonEmptyString, ...]
    breaking: bool
    blast_radius: BlastRadiusReport
    accepted_blast_radius_sha256: Sha256String | None = None
    preview_sha256: Sha256String


class _EvolutionPreviewV2(_ClosedFrozenModel):
    schema_version: Literal[LOCATOR_EVOLUTION_SCHEMA_VERSION] = LOCATOR_EVOLUTION_SCHEMA_VERSION
    proposal: _EvolutionProposalV2
    proposal_sha256: Sha256String
    before_model: CommittedText
    candidate_model: CommittedText
    verbalization: CommittedText
    validation: ValidationEvidence
    affected_references: tuple[NonEmptyString, ...]
    breaking: bool
    blast_radius: BlastRadiusReport
    accepted_blast_radius_sha256: Sha256String | None = None
    preview_sha256: Sha256String


class _EvolutionPreviewV3(_EvolutionPreviewV2):
    schema_version: Literal[EVOLUTION_SCHEMA_VERSION] = EVOLUTION_SCHEMA_VERSION
    proposal: _EvolutionProposalV3


class EvolutionPreview(_ClosedFrozenModel):
    schema_version: Literal[1, 2, 3] = LEGACY_EVOLUTION_SCHEMA_VERSION
    proposal: EvolutionProposal
    proposal_sha256: Sha256String
    before_model: CommittedText
    candidate_model: CommittedText
    verbalization: CommittedText
    validation: ValidationEvidence
    affected_references: tuple[NonEmptyString, ...]
    breaking: bool
    blast_radius: BlastRadiusReport
    accepted_blast_radius_sha256: Sha256String | None = None
    preview_sha256: Sha256String

    @classmethod
    def model_validate(cls, obj: Any, *args: Any, **kwargs: Any) -> Self:
        if isinstance(obj, cls):
            return obj
        version = obj.get("schema_version") if isinstance(obj, dict) else None
        if version == LEGACY_EVOLUTION_SCHEMA_VERSION:
            reader: type[_ClosedFrozenModel] = _EvolutionPreviewV1
        elif version == LOCATOR_EVOLUTION_SCHEMA_VERSION:
            reader = _EvolutionPreviewV2
        elif version == EVOLUTION_SCHEMA_VERSION:
            reader = _EvolutionPreviewV3
        else:
            raise _version_validation_error(cls.__name__, version)
        parsed = reader.model_validate(obj, *args, **kwargs)
        normalized = parsed.model_dump(mode="python")
        normalized["proposal"] = EvolutionProposal.model_validate(normalized["proposal"])
        return super().model_validate(normalized)

    @classmethod
    def model_validate_json(
        cls, json_data: str | bytes | bytearray, *args: Any, **kwargs: Any
    ) -> Self:
        return cls.model_validate(_json_document(json_data), *args, **kwargs)

    @model_serializer(mode="wrap")
    def _serialize_wire_version(self, handler):
        document = handler(self)
        document["proposal"] = self.proposal.model_dump(mode="json")
        return document

    @model_validator(mode="after")
    def _bindings_match(self) -> EvolutionPreview:
        if self.proposal.schema_version != self.schema_version:
            raise ValueError("preview and proposal versions must match")
        if self.proposal_sha256 != self.proposal.proposal_sha256:
            raise ValueError("proposal_sha256 does not bind proposal")
        if self.candidate_model != self.proposal.candidate_model:
            raise ValueError("preview candidate differs from proposal candidate")
        if self.before_model.sha256 != self.proposal.expected_model_sha256:
            raise ValueError("preview before model differs from expected model identity")
        if tuple(sorted(set(self.affected_references))) != self.affected_references:
            raise ValueError("affected_references must be unique and sorted")
        expected_breaking = any(
            operation.kind in {EvolutionOperationKind.RENAME, EvolutionOperationKind.DELETE}
            for operation in self.proposal.operations
        )
        if self.breaking != expected_breaking:
            raise ValueError("breaking flag does not match proposal operations")
        if self.blast_radius.proposal_sha256 != self.proposal_sha256:
            raise ValueError("blast radius does not bind the proposal")
        if self.blast_radius.before_model_sha256 != self.before_model.sha256:
            raise ValueError("blast radius does not bind the before model")
        if self.blast_radius.candidate_model_sha256 != self.candidate_model.sha256:
            raise ValueError("blast radius does not bind the candidate model")
        if (
            self.accepted_blast_radius_sha256 is not None
            and self.accepted_blast_radius_sha256 != self.blast_radius.report_sha256
        ):
            raise ValueError("accepted blast radius does not match this preview")
        body = self.model_dump(mode="json", exclude={"preview_sha256"})
        if canonical_sha256(body) != self.preview_sha256:
            raise ValueError("preview_sha256 does not bind preview")
        return self


class _EvolutionIntentV1(_ClosedFrozenModel):
    schema_version: Literal[LEGACY_EVOLUTION_SCHEMA_VERSION] = (
        LEGACY_EVOLUTION_SCHEMA_VERSION
    )
    proposal_sha256: Sha256String
    preview_sha256: Sha256String
    expected_model_sha256: Sha256String
    candidate_model_sha256: Sha256String
    verbalization_sha256: Sha256String
    verbalization_before_kind: Literal["absent", "file"]
    verbalization_before_sha256: Sha256String | None = None
    blast_radius_sha256: Sha256String
    accepted_blast_radius_sha256: Sha256String | None = None
    linked_projects: tuple[_LinkedProjectV1, ...] = ()
    model_commit_point: Literal["model-cas"] = "model-cas"
    transaction_scope: Literal["single-leaf CAS; no multi-file atomicity"] = (
        "single-leaf CAS; no multi-file atomicity"
    )


class _EvolutionIntentV2(_ClosedFrozenModel):
    schema_version: Literal[LOCATOR_EVOLUTION_SCHEMA_VERSION] = LOCATOR_EVOLUTION_SCHEMA_VERSION
    proposal_sha256: Sha256String
    preview_sha256: Sha256String
    expected_model_sha256: Sha256String
    candidate_model_sha256: Sha256String
    verbalization_sha256: Sha256String
    verbalization_before_kind: Literal["absent", "file"]
    verbalization_before_sha256: Sha256String | None = None
    blast_radius_sha256: Sha256String
    accepted_blast_radius_sha256: Sha256String | None = None
    linked_projects: tuple[_LinkedProjectV2, ...] = ()
    model_commit_point: Literal["model-cas"] = "model-cas"
    transaction_scope: Literal["single-leaf CAS; no multi-file atomicity"] = (
        "single-leaf CAS; no multi-file atomicity"
    )


class _EvolutionIntentV3(_EvolutionIntentV2):
    schema_version: Literal[EVOLUTION_SCHEMA_VERSION] = EVOLUTION_SCHEMA_VERSION
    linked_projects: tuple[_LinkedProjectV3, ...] = ()


class EvolutionIntent(_ClosedFrozenModel):
    """Normalized staged intent selected by its enclosing schema version."""

    schema_version: Literal[1, 2, 3] = LEGACY_EVOLUTION_SCHEMA_VERSION
    proposal_sha256: Sha256String
    preview_sha256: Sha256String
    expected_model_sha256: Sha256String
    candidate_model_sha256: Sha256String
    verbalization_sha256: Sha256String
    verbalization_before_kind: Literal["absent", "file"]
    verbalization_before_sha256: Sha256String | None = None
    blast_radius_sha256: Sha256String
    accepted_blast_radius_sha256: Sha256String | None = None
    linked_projects: tuple[LinkedProject, ...] = ()
    model_commit_point: Literal["model-cas"] = "model-cas"
    transaction_scope: Literal["single-leaf CAS; no multi-file atomicity"] = (
        "single-leaf CAS; no multi-file atomicity"
    )

    @classmethod
    def model_validate(cls, obj: Any, *args: Any, **kwargs: Any) -> Self:
        if isinstance(obj, cls):
            return obj
        version = obj.get("schema_version") if isinstance(obj, dict) else None
        if version == LEGACY_EVOLUTION_SCHEMA_VERSION:
            reader: type[_ClosedFrozenModel] = _EvolutionIntentV1
        elif version == LOCATOR_EVOLUTION_SCHEMA_VERSION:
            reader = _EvolutionIntentV2
        elif version == EVOLUTION_SCHEMA_VERSION:
            reader = _EvolutionIntentV3
        else:
            raise _version_validation_error(cls.__name__, version)
        parsed = reader.model_validate(obj, *args, **kwargs)
        return super().model_validate(parsed.model_dump(mode="python"))

    @classmethod
    def model_validate_json(
        cls, json_data: str | bytes | bytearray, *args: Any, **kwargs: Any
    ) -> Self:
        return cls.model_validate(_json_document(json_data), *args, **kwargs)

    @model_serializer(mode="wrap")
    def _serialize_wire_version(self, handler):
        document = handler(self)
        for project in document["linked_projects"]:
            if self.schema_version == LEGACY_EVOLUTION_SCHEMA_VERSION:
                project.pop("locator", None)
            else:
                project.pop("root", None)
        return document

    @model_validator(mode="after")
    def _coordinate_version_matches(self) -> EvolutionIntent:
        for project in self.linked_projects:
            _refuse_cross_version_project(project, self.schema_version, "intent linked project")
        if self.verbalization_before_kind == "absent":
            if self.verbalization_before_sha256 is not None:
                raise ValueError("absent verbalization cannot have a digest")
        elif self.verbalization_before_sha256 is None:
            raise ValueError("existing verbalization requires a digest")
        return self


class EvolutionFinalizationState(_ClosedFrozenModel):
    """Durable identity required to finish exact post-CAS leaves."""

    schema_version: Literal[1, 2, 3] = LEGACY_EVOLUTION_SCHEMA_VERSION
    state: Literal["pending-finalization"] = "pending-finalization"
    proposal_id: StableId
    proposal_sha256: Sha256String
    preview_sha256: Sha256String
    intent_sha256: Sha256String
    old_model_sha256: Sha256String
    new_model_sha256: Sha256String
    verbalization_sha256: Sha256String
    verbalization_before_kind: Literal["absent", "file"]
    verbalization_before_sha256: Sha256String | None = None
    linked_projects: tuple[LinkedProject, ...] | None = None
    state_identity_sha256: Sha256String

    @model_serializer(mode="wrap")
    def _serialize_wire_version(self, handler):
        document = handler(self)
        if self.linked_projects is None:
            document.pop("linked_projects")
        return document

    @model_validator(mode="after")
    def _state_is_bound(self) -> EvolutionFinalizationState:
        # Only a version 3 state carries its projects, INSIDE its own identity:
        # that is what makes a clean clone finishable (IF-P3-6, D-P3.5).
        if (self.schema_version == EVOLUTION_SCHEMA_VERSION) != (
            self.linked_projects is not None
        ):
            raise ValueError("only a version 3 finalization state carries linked projects")
        for project in self.linked_projects or ():
            _refuse_cross_version_project(project, self.schema_version, "pending linked project")
        if self.verbalization_before_kind == "absent":
            if self.verbalization_before_sha256 is not None:
                raise ValueError("absent verbalization cannot have a digest")
        elif self.verbalization_before_sha256 is None:
            raise ValueError("existing verbalization requires a digest")
        body = self.model_dump(mode="json", exclude={"state_identity_sha256"})
        if canonical_sha256(body) != self.state_identity_sha256:
            raise ValueError("state_identity_sha256 does not bind finalization state")
        return self


class CASEvidence(_ClosedFrozenModel):
    expected_model_sha256: Sha256String
    observed_model_sha256: Sha256String
    commit_point: Literal["model-cas"] = "model-cas"
    published: bool
    conflict: str | None = None


class _LinkedProjectConformanceBase(_ClosedFrozenModel):
    project_id: NonEmptyString
    expected_tree_sha256: Sha256String | None = None
    before_tree_sha256: Sha256String | None = None
    after_tree_sha256: Sha256String | None = None
    tracked_roster: TrackedRoster | None = None
    expected_tracked_tree_sha256: Sha256String | None = None
    before_tracked_tree_sha256: Sha256String | None = None
    after_tracked_tree_sha256: Sha256String | None = None
    payload: dict[str, Any]
    payload_sha256: Sha256String
    exit_code: Literal[0, 3, 13, 66, 74]

    @field_validator("payload")
    @classmethod
    def _freeze_payload(cls, value: dict[str, Any]) -> dict[str, Any]:
        return _freeze_json(value)

    @model_validator(mode="after")
    def _payload_binding(self) -> LinkedProjectConformance:
        if conformance_payload_sha256(self.payload) != self.payload_sha256:
            raise ValueError("payload_sha256 does not bind raw conformance payload")
        whole = (self.expected_tree_sha256, self.before_tree_sha256, self.after_tree_sha256)
        tracked = (
            self.expected_tracked_tree_sha256,
            self.before_tracked_tree_sha256,
            self.after_tracked_tree_sha256,
        )
        chosen = tracked if self.tracked_roster is not None else whole
        other = whole if self.tracked_roster is not None else tracked
        if any(value is None for value in chosen) or any(
            value is not None for value in other
        ):
            raise ValueError("linked conformance requires exactly one observation triple")
        if len(set(chosen)) != 1:
            raise ValueError(
                "linked conformance requires expected, before, and after tree equality"
            )
        return self


class _LinkedProjectConformanceV1(_LinkedProjectConformanceBase):
    root: Path
    expected_tree_sha256: Sha256String
    before_tree_sha256: Sha256String
    after_tree_sha256: Sha256String


class _LinkedProjectConformanceV2(_LinkedProjectConformanceV1):
    root: None = None
    locator: ProjectLocator


class _LinkedProjectConformanceV3(_LinkedProjectConformanceBase):
    locator: ProjectLocator
    tracked_roster: TrackedRoster
    expected_tracked_tree_sha256: Sha256String
    before_tracked_tree_sha256: Sha256String
    after_tracked_tree_sha256: Sha256String


class LinkedProjectConformance(_LinkedProjectConformanceBase):
    """Normalized conformance leaf; its caller owns the wire-version choice."""

    root: Path | None = None
    locator: ProjectLocator | None = None

    @model_validator(mode="after")
    def _one_coordinate(self) -> LinkedProjectConformance:
        if (self.root is None) == (self.locator is None):
            raise ValueError("linked conformance requires exactly one coordinate")
        return self

    @model_serializer(mode="wrap")
    def _serialize_selected_coordinate(self, handler):
        document = handler(self)
        document.pop("root" if self.root is None else "locator")
        for key in (
            ("expected_", "before_", "after_")
            if self.tracked_roster is not None
            else ("expected_tracked_", "before_tracked_", "after_tracked_")
        ):
            document.pop(f"{key}tree_sha256")
        if self.tracked_roster is None:
            document.pop("tracked_roster")
        return document


class AffectedCodeEvidence(_ClosedFrozenModel):
    ordered_references: tuple[NonEmptyString, ...]
    generated_code_written: Literal[False] = False
    extension_code_written: Literal[False] = False
    blast_radius: tuple[NonEmptyString, ...] = ()


class _EvolutionRecordBase(_ClosedFrozenModel):
    proposal_id: StableId
    proposal_sha256: Sha256String
    preview_sha256: Sha256String
    intent_sha256: Sha256String
    old_model_sha256: Sha256String
    new_model_sha256: Sha256String
    blast_radius_sha256: Sha256String
    accepted_blast_radius_sha256: Sha256String | None
    finalization_state_sha256: Sha256String
    operations: tuple[EvolutionOperation, ...]
    rationale: NonEmptyString
    audit: EvolutionOperationAudit
    validation: ValidationEvidence
    cas: CASEvidence
    affected_code: AffectedCodeEvidence
    conformance_exit_code: Literal[0, 3, 13, 66, 74]
    published_with_drift: bool
    model_commit_point: Literal["model-cas"] = "model-cas"
    transaction_scope: Literal["single-leaf CAS; no multi-file atomicity"] = (
        "single-leaf CAS; no multi-file atomicity"
    )
    record_identity_sha256: Sha256String

    @model_validator(mode="after")
    def _derived_conformance_fields(self) -> Self:
        linked = tuple(getattr(self, "linked_conformance", ()))
        aggregate = max(
            (item.exit_code for item in linked),
            default=0,
            key=lambda code: _CONFORMANCE_EXIT_PRECEDENCE[code],
        )
        if self.conformance_exit_code != aggregate:
            raise ValueError(
                "conformance_exit_code does not match linked conformance precedence"
            )
        if self.published_with_drift is not (aggregate == 13):
            raise ValueError(
                "published_with_drift does not match the aggregate conformance exit"
            )
        return self


class _EvolutionRecordV1(_EvolutionRecordBase):
    schema_version: Literal[LEGACY_EVOLUTION_SCHEMA_VERSION] = (
        LEGACY_EVOLUTION_SCHEMA_VERSION
    )
    linked_conformance: tuple[_LinkedProjectConformanceV1, ...]


class _EvolutionRecordV2(_EvolutionRecordBase):
    schema_version: Literal[LOCATOR_EVOLUTION_SCHEMA_VERSION] = LOCATOR_EVOLUTION_SCHEMA_VERSION
    linked_conformance: tuple[_LinkedProjectConformanceV2, ...]


class _EvolutionRecordV3(_EvolutionRecordBase):
    schema_version: Literal[EVOLUTION_SCHEMA_VERSION] = EVOLUTION_SCHEMA_VERSION
    linked_conformance: tuple[_LinkedProjectConformanceV3, ...]


class EvolutionRecord(_EvolutionRecordBase):
    schema_version: Literal[1, 2, 3] = LEGACY_EVOLUTION_SCHEMA_VERSION
    linked_conformance: tuple[LinkedProjectConformance, ...]

    @classmethod
    def model_validate(cls, obj: Any, *args: Any, **kwargs: Any) -> Self:
        if isinstance(obj, cls):
            return obj
        version = obj.get("schema_version") if isinstance(obj, dict) else None
        if version == LEGACY_EVOLUTION_SCHEMA_VERSION:
            reader: type[_EvolutionRecordBase] = _EvolutionRecordV1
        elif version == LOCATOR_EVOLUTION_SCHEMA_VERSION:
            reader = _EvolutionRecordV2
        elif version == EVOLUTION_SCHEMA_VERSION:
            reader = _EvolutionRecordV3
        else:
            raise _version_validation_error(cls.__name__, version)
        parsed = reader.model_validate(obj, *args, **kwargs)
        for leaf in obj.get("linked_conformance") or ():
            read_linked_project_conformance_document(leaf, envelope_version=version)
        return super().model_validate(parsed.model_dump(mode="python"))

    @classmethod
    def model_validate_json(
        cls, json_data: str | bytes | bytearray, *args: Any, **kwargs: Any
    ) -> Self:
        return cls.model_validate(_json_document(json_data), *args, **kwargs)

    @model_serializer(mode="wrap")
    def _serialize_wire_version(self, handler):
        document = handler(self)
        for conformance in document["linked_conformance"]:
            if self.schema_version == LEGACY_EVOLUTION_SCHEMA_VERSION:
                conformance.pop("locator", None)
            else:
                conformance.pop("root", None)
        return document

    @model_validator(mode="after")
    def _record_binding(self) -> EvolutionRecord:
        for conformance in self.linked_conformance:
            _refuse_cross_version_project(conformance, self.schema_version, "conformance leaf")
        body = self.model_dump(mode="json", exclude={"record_identity_sha256"})
        if canonical_sha256(body) != self.record_identity_sha256:
            raise ValueError("record_identity_sha256 does not bind record")
        if self.old_model_sha256 != self.cas.expected_model_sha256:
            raise ValueError("CAS expected identity differs from old model identity")
        if self.new_model_sha256 != self.cas.observed_model_sha256:
            raise ValueError("CAS observed identity differs from new model identity")
        breaking = any(
            operation.kind in {EvolutionOperationKind.RENAME, EvolutionOperationKind.DELETE}
            for operation in self.operations
        )
        if breaking and self.accepted_blast_radius_sha256 != self.blast_radius_sha256:
            raise ValueError("breaking records require the exact accepted blast radius")
        if (
            self.accepted_blast_radius_sha256 is not None
            and self.accepted_blast_radius_sha256 != self.blast_radius_sha256
        ):
            raise ValueError("record acceptance differs from its blast-radius identity")
        return self


def read_evolution_proposal_document(document: Any) -> EvolutionProposal:
    """Read one proposal after selecting its closed wire graph by envelope version."""

    return EvolutionProposal.model_validate(document)


def read_evolution_preview_document(document: Any) -> EvolutionPreview:
    """Read one preview after selecting its closed wire graph by envelope version."""

    return EvolutionPreview.model_validate(document)


def read_evolution_intent_document(document: Any) -> EvolutionIntent:
    """Read one staged intent through its explicit enclosing version."""

    return EvolutionIntent.model_validate(document)


def read_evolution_finalization_state_document(
    document: Any,
) -> EvolutionFinalizationState:
    """Read one pending-finalization claim through its closed envelope."""

    version = document.get("schema_version") if isinstance(document, dict) else None
    if version not in EVOLUTION_SCHEMA_VERSIONS:
        raise _version_validation_error(EvolutionFinalizationState.__name__, version)
    fields = frozenset(EvolutionFinalizationState.model_fields)
    fields -= frozenset() if version == EVOLUTION_SCHEMA_VERSION else {"linked_projects"}
    _refuse_foreign_keys(document, fields, f"a version {version} pending state")
    for project in document.get("linked_projects") or ():
        _refuse_foreign_keys(project, frozenset(_LinkedProjectV3.model_fields), "a v3 project")
    return EvolutionFinalizationState.model_validate(document)


def read_evolution_record_document(document: Any) -> EvolutionRecord:
    """Read one record after selecting its nested conformance graph by version."""

    return EvolutionRecord.model_validate(document)


def read_linked_project_conformance_document(
    document: Any,
    *,
    envelope_version: int,
) -> LinkedProjectConformance:
    """Read a standalone leaf using only its caller-supplied envelope version."""

    if envelope_version == LEGACY_EVOLUTION_SCHEMA_VERSION:
        reader: type[_LinkedProjectConformanceBase] = _LinkedProjectConformanceV1
    elif envelope_version == LOCATOR_EVOLUTION_SCHEMA_VERSION:
        reader = _LinkedProjectConformanceV2
    elif envelope_version == EVOLUTION_SCHEMA_VERSION:
        reader = _LinkedProjectConformanceV3
    else:
        raise _version_validation_error(
            LinkedProjectConformance.__name__, envelope_version
        )
    required = frozenset(n for n, f in reader.model_fields.items() if f.is_required())
    parsed = reader.model_validate(document)
    _refuse_foreign_keys(document, required, f"a version {envelope_version} conformance leaf")
    return LinkedProjectConformance.model_validate(parsed.model_dump(mode="python"))


__all__ = [
    "EVOLUTION_READ_ONLY_PENDING",
    "EVOLUTION_SCHEMA_VERSION",
    "LEGACY_EVOLUTION_SCHEMA_VERSION",
    "LOCATOR_EVOLUTION_SCHEMA_VERSION",
    "AffectedCodeEvidence",
    "ArtifactLocator",
    "BlastRadiusEntry",
    "BlastRadiusReport",
    "CASEvidence",
    "CommittedText",
    "ConstraintLocator",
    "ElementLocator",
    "EvolutionFinalizationState",
    "EvolutionIntent",
    "EvolutionOperation",
    "EvolutionOperationAudit",
    "EvolutionOperationKind",
    "EvolutionPreview",
    "EvolutionProposal",
    "EvolutionRecord",
    "LinkedProject",
    "LinkedProjectConformance",
    "ModelIdentityLocator",
    "ProjectLocator",
    "RoleLocator",
    "StableLocator",
    "TrackedRoster",
    "ValidationEvidence",
    "ValidationFinding",
    "canonical_sha256",
    "conformance_payload_sha256",
    "read_evolution_finalization_state_document",
    "read_evolution_intent_document",
    "read_evolution_preview_document",
    "read_evolution_proposal_document",
    "read_evolution_record_document",
    "read_linked_project_conformance_document",
]
