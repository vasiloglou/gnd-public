"""Closed, immutable records for conservative codebase recovery.

The recovery inventory is an evidence boundary, not a source-code transport.
It records byte identities and typed locators, while deliberately omitting raw
excerpts.  Every public record in this module is a frozen, ``extra=forbid``
Pydantic model so a report cannot acquire an unreviewed claim through schema
drift or mutation after validation.
"""

from __future__ import annotations

import re
from collections import defaultdict
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from typing import Annotated, Literal, Self

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    StrictStr,
    StringConstraints,
    model_validator,
)

__all__ = [
    "AmbiguousProposal",
    "CensusDisposition",
    "CensusEntry",
    "ClaimStatus",
    "ConstraintSource",
    "ElementKind",
    "EvidenceLocator",
    "EvidenceRecord",
    "ExcludedRoot",
    "ExclusionReason",
    "FrontierItem",
    "FrontierReason",
    "JsonPointerLocator",
    "LineLocator",
    "MediaType",
    "Modality",
    "ModeledElementEvidence",
    "OutputArtifact",
    "PythonSymbolLocator",
    "RecoveryInventory",
    "RecoveryReport",
    "RecoveryScope",
    "RecoveryVerificationResult",
    "RootCategory",
    "SelectedRoot",
    "YamlPathLocator",
]


NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
MAX_REPORT_RECORDS = 10_000


def _safe_relative_path(value: str) -> str:
    """Return one portable, normalized repository-relative path.

    Both POSIX and Windows interpretations are checked because reports are
    committed artifacts and may be verified on a different platform from the
    one that produced them.
    """

    if not value or not value.strip():
        raise ValueError("repository-relative paths must be nonempty")
    if value != value.strip():
        raise ValueError("repository-relative paths cannot have surrounding whitespace")
    if "\x00" in value:
        raise ValueError("repository-relative paths cannot contain NUL bytes")
    if "\\" in value:
        raise ValueError("repository-relative paths must use POSIX separators")
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    if (
        posix.is_absolute()
        or windows.is_absolute()
        or bool(posix.root)
        or bool(windows.root)
        or bool(windows.drive)
        or value.startswith(("/", "\\"))
    ):
        raise ValueError("repository paths must be relative")
    if ".." in posix.parts or ".." in windows.parts:
        raise ValueError("parent traversal is forbidden in repository paths")
    if value != "." and (not posix.parts or posix.as_posix() != value):
        raise ValueError("repository paths must be normalized POSIX paths")
    return value


RelativePath = Annotated[
    str,
    StringConstraints(min_length=1),
    AfterValidator(_safe_relative_path),
]


def _json_pointer(value: str) -> str:
    if not value.startswith("/"):
        raise ValueError("JSON pointers must be nonempty and start with '/'")
    if re.search(r"~(?:[^01]|$)", value):
        raise ValueError("JSON pointers may use only the ~0 and ~1 escapes")
    return value


JsonPointer = Annotated[
    str,
    StringConstraints(min_length=1),
    AfterValidator(_json_pointer),
]


class _ClosedFrozenModel(BaseModel):
    """Base configuration shared by every serialized recovery record."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class RootCategory(StrEnum):
    # Lower-case member names intentionally support the scanner's direct
    # ``RootCategory.source`` comparisons while values remain JSON literals.
    source = "source"
    test = "test"
    docs = "docs"
    config = "config"
    schema = "schema"


class MediaType(StrEnum):
    PYTHON = "text/x-python"
    MARKDOWN = "text/markdown"
    RESTRUCTURED_TEXT = "text/x-rst"
    PLAIN_TEXT = "text/plain"
    JSON = "application/json"
    JSON_SCHEMA = "application/schema+json"
    YAML = "application/yaml"
    SQL = "application/sql"
    OPAQUE = "application/octet-stream"


class ElementKind(StrEnum):
    OBJECT_TYPE = "object-type"
    FACT_TYPE = "fact-type"
    ROLE = "role"
    CONSTRAINT = "constraint"


class ConstraintSource(StrEnum):
    EXPLICIT = "explicit"
    SAMPLE = "sample"
    COMMON_SENSE = "common-sense"
    LLM_INFERRED = "llm-inferred"
    USER_SUPPLIED = "user-supplied"


class ClaimStatus(StrEnum):
    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class Modality(StrEnum):
    ALETHIC = "alethic"
    DEONTIC = "deontic"


class CensusDisposition(StrEnum):
    PARSED = "parsed"
    EXCLUDED = "excluded"
    AMBIGUOUS = "ambiguous"
    FRONTIER = "frontier"


class ExclusionReason(StrEnum):
    DEPENDENCY = "dependency"
    VENDORED = "vendored"
    GENERATED = "generated"
    CACHE = "cache"
    BUILD = "build"
    SENSITIVE_TREE = "sensitive-tree"


class FrontierReason(StrEnum):
    DYNAMIC_CONSTRUCT = "dynamic-construct"
    MIXED_LANGUAGE = "mixed-language"
    UNRESOLVED_IMPORT = "unresolved-import"
    UNSUPPORTED_LANGUAGE = "unsupported-language"
    SYMLINK = "symlink"
    SYMLINK_CYCLE = "symlink-cycle"
    BINARY = "binary"
    PARSE_ERROR = "parse-error"
    OVERSIZE = "oversize"
    FILE_LIMIT = "file-limit"
    AGGREGATE_LIMIT = "aggregate-limit"


class SelectedRoot(_ClosedFrozenModel):
    """One explicitly selected repository subtree and its evidence category."""

    category: RootCategory
    path: RelativePath


class ExcludedRoot(_ClosedFrozenModel):
    """One selected-scope entry deliberately excluded by a closed rule."""

    exclusion_id: NonEmptyString
    path: RelativePath
    reason: ExclusionReason


class RecoveryScope(_ClosedFrozenModel):
    """The explicit scan denominator and resource bounds."""

    # This is diagnostic run identity and may be absolute. All paths used to
    # open evidence remain repository-relative and are checked separately.
    repository_root: NonEmptyString
    selected_roots: tuple[SelectedRoot, ...] = Field(min_length=1, max_length=MAX_REPORT_RECORDS)
    excluded_roots: tuple[ExcludedRoot, ...] = Field(default=(), max_length=MAX_REPORT_RECORDS)
    max_file_bytes: int = Field(gt=0)
    max_total_bytes: int = Field(gt=0)
    max_files: int = Field(gt=0)

    @model_validator(mode="after")
    def _scope_is_unambiguous(self) -> Self:
        selected_paths = [entry.path for entry in self.selected_roots]
        if len(selected_paths) != len(set(selected_paths)):
            raise ValueError("selected root paths must be unique")
        excluded_ids = [entry.exclusion_id for entry in self.excluded_roots]
        excluded_paths = [entry.path for entry in self.excluded_roots]
        if len(excluded_ids) != len(set(excluded_ids)):
            raise ValueError("exclusion_id values must be unique")
        if len(excluded_paths) != len(set(excluded_paths)):
            raise ValueError("excluded paths must be unique")
        if excluded_paths != sorted(excluded_paths):
            raise ValueError("excluded paths must be sorted")
        if self.max_file_bytes > self.max_total_bytes:
            raise ValueError("max_file_bytes cannot exceed max_total_bytes")
        return self


class PythonSymbolLocator(_ClosedFrozenModel):
    kind: Literal["python-symbol"] = "python-symbol"
    symbol: NonEmptyString
    line_start: int = Field(gt=0)
    line_end: int = Field(gt=0)

    @model_validator(mode="after")
    def _ordered_span(self) -> Self:
        if self.line_end < self.line_start:
            raise ValueError("line_end cannot precede line_start")
        return self


class LineLocator(_ClosedFrozenModel):
    kind: Literal["line"] = "line"
    line_start: int = Field(gt=0)
    line_end: int = Field(gt=0)

    @model_validator(mode="after")
    def _ordered_span(self) -> Self:
        if self.line_end < self.line_start:
            raise ValueError("line_end cannot precede line_start")
        return self


class JsonPointerLocator(_ClosedFrozenModel):
    kind: Literal["json-pointer"] = "json-pointer"
    pointer: JsonPointer


class YamlPathLocator(_ClosedFrozenModel):
    kind: Literal["yaml-path"] = "yaml-path"
    path: tuple[StrictStr | StrictInt, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _segments_are_addressable(self) -> Self:
        for segment in self.path:
            if isinstance(segment, int) and segment < 0:
                raise ValueError("YAML path indexes cannot be negative")
            if isinstance(segment, str) and not segment:
                raise ValueError("YAML path keys cannot be empty")
        return self


EvidenceLocator = Annotated[
    PythonSymbolLocator | LineLocator | JsonPointerLocator | YamlPathLocator,
    Field(discriminator="kind"),
]


class EvidenceRecord(_ClosedFrozenModel):
    """Digest-bound evidence with a re-resolvable locator and no source text."""

    evidence_id: NonEmptyString
    path: RelativePath
    sha256: Sha256
    byte_length: int = Field(ge=0)
    media_type: MediaType
    encoding: Literal["utf-8"] = "utf-8"
    locator: EvidenceLocator
    excerpt_sha256: Sha256


class ModeledElementEvidence(_ClosedFrozenModel):
    """One model element and the concrete observations supporting it."""

    element_id: NonEmptyString
    element_kind: ElementKind
    model_pointer: JsonPointer
    evidence_ids: tuple[NonEmptyString, ...] = Field(min_length=1, max_length=MAX_REPORT_RECORDS)
    source: ConstraintSource | None = None
    status: ClaimStatus | None = None
    modality: Modality | None = None

    @model_validator(mode="after")
    def _claim_shape_is_closed(self) -> Self:
        if len(self.evidence_ids) != len(set(self.evidence_ids)):
            raise ValueError("modeled evidence_ids must be unique")
        provenance = (self.source, self.status, self.modality)
        if self.element_kind is ElementKind.CONSTRAINT:
            if any(value is None for value in provenance):
                raise ValueError("modeled constraints require source, status, and modality")
            if self.status is ClaimStatus.REJECTED:
                raise ValueError("rejected constraints cannot be modeled elements")
            if self.source in {
                ConstraintSource.SAMPLE,
                ConstraintSource.COMMON_SENSE,
                ConstraintSource.LLM_INFERRED,
            } and (
                self.status is not ClaimStatus.PROPOSED or self.modality is not Modality.DEONTIC
            ):
                raise ValueError(
                    "sample, common-sense, and llm-inferred recovery claims remain proposed/deontic"
                )
        elif any(value is not None for value in provenance):
            raise ValueError("only constraint elements carry constraint provenance")
        return self


class AmbiguousProposal(_ClosedFrozenModel):
    """A semantic interpretation retained for explicit owner review."""

    proposal_id: NonEmptyString
    element_id: NonEmptyString
    element_kind: ElementKind
    source: ConstraintSource
    status: ClaimStatus
    modality: Modality
    rationale: NonEmptyString
    evidence_ids: tuple[NonEmptyString, ...] = Field(min_length=1, max_length=MAX_REPORT_RECORDS)
    prior_proposal_id: NonEmptyString | None = None

    @model_validator(mode="after")
    def _proposal_policy(self) -> Self:
        if len(self.evidence_ids) != len(set(self.evidence_ids)):
            raise ValueError("proposal evidence_ids must be unique")
        if self.source in {
            ConstraintSource.SAMPLE,
            ConstraintSource.COMMON_SENSE,
            ConstraintSource.LLM_INFERRED,
        } and (self.status is ClaimStatus.CONFIRMED or self.modality is not Modality.DEONTIC):
            raise ValueError(
                "sample, common-sense, and llm-inferred proposals remain unconfirmed/deontic"
            )
        if self.status is ClaimStatus.PROPOSED and self.modality is not Modality.DEONTIC:
            raise ValueError("unconfirmed recovery proposals must be deontic")
        if self.status is ClaimStatus.CONFIRMED:
            if self.source is not ConstraintSource.USER_SUPPLIED:
                raise ValueError("owner confirmation must be recorded as user-supplied")
            if self.prior_proposal_id is None:
                raise ValueError("owner confirmation must reference the reviewed proposal")
        if self.prior_proposal_id == self.proposal_id:
            raise ValueError("a proposal cannot reference itself as its prior proposal")
        return self


class FrontierItem(_ClosedFrozenModel):
    """A selected path that static recovery could not safely interpret."""

    frontier_id: NonEmptyString
    path: RelativePath
    reason: FrontierReason
    # Aggregate/file caps can prevent a full byte read; in that fail-closed
    # state the census record remains, but no fabricated digest is emitted.
    sha256: Sha256 | None = None
    detail: NonEmptyString | None = None


class CensusEntry(_ClosedFrozenModel):
    """Exactly one disposition for one path in the selected denominator."""

    path: RelativePath
    disposition: CensusDisposition
    reference_ids: tuple[NonEmptyString, ...] = Field(min_length=1, max_length=MAX_REPORT_RECORDS)

    @model_validator(mode="after")
    def _references_are_canonical(self) -> Self:
        if tuple(sorted(set(self.reference_ids))) != self.reference_ids:
            raise ValueError("census reference_ids must be unique and sorted")
        return self


class RecoveryInventory(_ClosedFrozenModel):
    """Complete selected-path census plus evidence and conservative gaps."""

    scope: RecoveryScope
    evidence: tuple[EvidenceRecord, ...] = Field(default=(), max_length=MAX_REPORT_RECORDS)
    ambiguities: tuple[AmbiguousProposal, ...] = Field(default=(), max_length=MAX_REPORT_RECORDS)
    frontier: tuple[FrontierItem, ...] = Field(default=(), max_length=MAX_REPORT_RECORDS)
    census: tuple[CensusEntry, ...] = Field(default=(), max_length=MAX_REPORT_RECORDS)

    @model_validator(mode="after")
    def _inventory_is_referentially_closed(self) -> Self:
        evidence_by_id = {entry.evidence_id: entry for entry in self.evidence}
        ambiguity_by_id = {entry.proposal_id: entry for entry in self.ambiguities}
        frontier_by_id = {entry.frontier_id: entry for entry in self.frontier}
        exclusion_by_id = {entry.exclusion_id: entry for entry in self.scope.excluded_roots}
        collections = (
            ("evidence_id", self.evidence, evidence_by_id),
            ("proposal_id", self.ambiguities, ambiguity_by_id),
            ("frontier_id", self.frontier, frontier_by_id),
            ("exclusion_id", self.scope.excluded_roots, exclusion_by_id),
        )
        for label, records, indexed in collections:
            if len(records) != len(indexed):
                raise ValueError(f"{label} values must be unique")
        all_record_ids = [
            *(entry.evidence_id for entry in self.evidence),
            *(entry.proposal_id for entry in self.ambiguities),
            *(entry.frontier_id for entry in self.frontier),
            *(entry.exclusion_id for entry in self.scope.excluded_roots),
        ]
        if len(all_record_ids) != len(set(all_record_ids)):
            raise ValueError("inventory record identifiers must be globally unique")

        evidence_order = [(entry.path, entry.evidence_id) for entry in self.evidence]
        if evidence_order != sorted(evidence_order):
            raise ValueError("evidence must be sorted by path and evidence_id")
        ambiguity_ids = [entry.proposal_id for entry in self.ambiguities]
        if ambiguity_ids != sorted(ambiguity_ids):
            raise ValueError("ambiguities must be sorted by proposal_id")
        frontier_order = [(entry.path, entry.frontier_id) for entry in self.frontier]
        if frontier_order != sorted(frontier_order):
            raise ValueError("frontier items must be sorted by path and frontier_id")
        census_paths = [entry.path for entry in self.census]
        if census_paths != sorted(census_paths) or len(census_paths) != len(set(census_paths)):
            raise ValueError("census paths must be unique and sorted")

        evidence_ids = set(evidence_by_id)
        for proposal in self.ambiguities:
            if proposal.status is not ClaimStatus.PROPOSED:
                raise ValueError("inventory ambiguities must remain proposed")
            if not set(proposal.evidence_ids) <= evidence_ids:
                raise ValueError("inventory ambiguity references unknown evidence")

        evidence_by_path: dict[str, set[str]] = defaultdict(set)
        for entry in self.evidence:
            evidence_by_path[entry.path].add(entry.evidence_id)
        frontier_by_path: dict[str, set[str]] = defaultdict(set)
        for entry in self.frontier:
            frontier_by_path[entry.path].add(entry.frontier_id)
        exclusion_by_path: dict[str, set[str]] = defaultdict(set)
        for entry in self.scope.excluded_roots:
            exclusion_by_path[entry.path].add(entry.exclusion_id)
        ambiguity_by_path: dict[str, set[str]] = defaultdict(set)
        ambiguity_evidence_by_path: dict[str, set[str]] = defaultdict(set)
        for proposal in self.ambiguities:
            for evidence_id in proposal.evidence_ids:
                evidence_path = evidence_by_id[evidence_id].path
                ambiguity_by_path[evidence_path].add(proposal.proposal_id)
                ambiguity_evidence_by_path[evidence_path].add(evidence_id)

        expected_paths = {
            *evidence_by_path,
            *frontier_by_path,
            *exclusion_by_path,
        }
        if set(census_paths) != expected_paths:
            raise ValueError("census paths must exactly cover all inventory records")

        for row in self.census:
            parsed = evidence_by_path[row.path]
            frontiers = frontier_by_path[row.path]
            exclusions = exclusion_by_path[row.path]
            ambiguities = ambiguity_by_path[row.path]
            active_families = sum(bool(items) for items in (frontiers, exclusions, ambiguities))
            if active_families > 1 or (parsed and (frontiers or exclusions)):
                raise ValueError(f"inventory record families conflict for {row.path}")
            if ambiguities and parsed != ambiguity_evidence_by_path[row.path]:
                raise ValueError(
                    f"ambiguous census does not account for all evidence at {row.path}"
                )
            if exclusions:
                expected_disposition = CensusDisposition.EXCLUDED
                expected = exclusions
            elif frontiers:
                expected_disposition = CensusDisposition.FRONTIER
                expected = frontiers
            elif ambiguities:
                expected_disposition = CensusDisposition.AMBIGUOUS
                expected = ambiguities
            else:
                expected_disposition = CensusDisposition.PARSED
                expected = parsed
            if (
                row.disposition is not expected_disposition
                or not expected
                or set(row.reference_ids) != expected
            ):
                raise ValueError(
                    f"{row.disposition.value} census references do not exactly match {row.path}"
                )
        return self


class OutputArtifact(_ClosedFrozenModel):
    """One canonical recovery output and its non-recursive digest binding."""

    path: Literal[
        "model.orm.yaml",
        "model.verbalization.txt",
        "model.recovery.json",
    ]
    sha256: Sha256 | None


class RecoveryReport(_ClosedFrozenModel):
    """Evidence-complete model recovery report."""

    schema_version: Literal[1] = 1
    inventory: RecoveryInventory
    modeled_elements: tuple[ModeledElementEvidence, ...] = Field(max_length=MAX_REPORT_RECORDS)
    proposals: tuple[AmbiguousProposal, ...] = Field(max_length=MAX_REPORT_RECORDS)
    outputs: tuple[OutputArtifact, ...] = Field(min_length=3, max_length=3)

    @model_validator(mode="after")
    def _report_is_evidence_complete(self) -> Self:
        if not self.inventory.census:
            raise ValueError("a recovery report requires a nonempty selected-path census")

        evidence_ids = {entry.evidence_id for entry in self.inventory.evidence}
        modeled_ids = [entry.element_id for entry in self.modeled_elements]
        if len(modeled_ids) != len(set(modeled_ids)):
            raise ValueError("modeled element_id values must be unique")
        model_pointers = [entry.model_pointer for entry in self.modeled_elements]
        if len(model_pointers) != len(set(model_pointers)):
            raise ValueError("modeled model_pointer values must be unique")
        proposal_ids = [entry.proposal_id for entry in self.proposals]
        if len(proposal_ids) != len(set(proposal_ids)):
            raise ValueError("report proposal_id values must be unique")

        for claim in (*self.modeled_elements, *self.proposals):
            if not claim.evidence_ids or not set(claim.evidence_ids) <= evidence_ids:
                raise ValueError("every modeled or proposed claim requires known evidence")

        proposals_by_id = {entry.proposal_id: entry for entry in self.proposals}
        for observed in self.inventory.ambiguities:
            retained = proposals_by_id.get(observed.proposal_id)
            if retained is None:
                raise ValueError("every inventoried ambiguity must be retained for review")
            immutable_fields = (
                "proposal_id",
                "element_id",
                "element_kind",
                "source",
                "modality",
                "rationale",
                "evidence_ids",
                "prior_proposal_id",
            )
            if any(
                getattr(retained, field) != getattr(observed, field) for field in immutable_fields
            ):
                raise ValueError("inventoried proposal identity and evidence are immutable")
            if retained.status not in {ClaimStatus.PROPOSED, ClaimStatus.REJECTED}:
                raise ValueError("inventoried proposals may only remain proposed or be rejected")

        seen_proposals: set[str] = set()
        for proposal in self.proposals:
            if (
                proposal.prior_proposal_id is not None
                and proposal.prior_proposal_id not in seen_proposals
            ):
                raise ValueError("prior_proposal_id must reference an earlier retained proposal")
            seen_proposals.add(proposal.proposal_id)

        expected_outputs = (
            "model.orm.yaml",
            "model.verbalization.txt",
            "model.recovery.json",
        )
        if tuple(item.path for item in self.outputs) != expected_outputs:
            raise ValueError("recovery reports require exactly the three canonical outputs")
        if self.outputs[0].sha256 is None or self.outputs[1].sha256 is None:
            raise ValueError("model and verbalization outputs require SHA-256 bindings")
        if self.outputs[2].sha256 is not None:
            raise ValueError("model.recovery.json cannot recursively bind its own digest")
        return self


class RecoveryVerificationResult(_ClosedFrozenModel):
    """Closed outcome of verifying all three recovery artifacts."""

    ok: bool
    errors: tuple[NonEmptyString, ...] = ()
    model_sha256: Sha256 | None = None
    verbalization_sha256: Sha256 | None = None
    report_sha256: Sha256 | None = None
    verified_evidence_ids: tuple[NonEmptyString, ...] = Field(
        default=(), max_length=MAX_REPORT_RECORDS
    )
    verified_census_paths: tuple[RelativePath, ...] = Field(
        default=(), max_length=MAX_REPORT_RECORDS
    )

    @model_validator(mode="after")
    def _outcome_is_coherent(self) -> Self:
        if len(self.errors) != len(set(self.errors)):
            raise ValueError("verification errors must be unique")
        if tuple(sorted(set(self.verified_evidence_ids))) != self.verified_evidence_ids:
            raise ValueError("verified_evidence_ids must be unique and sorted")
        if tuple(sorted(set(self.verified_census_paths))) != self.verified_census_paths:
            raise ValueError("verified_census_paths must be unique and sorted")
        if self.ok:
            if self.errors:
                raise ValueError("successful verification cannot carry errors")
            if None in (
                self.model_sha256,
                self.verbalization_sha256,
                self.report_sha256,
            ):
                raise ValueError("successful verification requires all artifact digests")
        elif not self.errors:
            raise ValueError("failed verification requires at least one error")
        return self
