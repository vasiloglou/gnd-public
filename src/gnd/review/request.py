"""Closed, digest-bound review requests and reviewer responses.

Review request bytes are untrusted repository data.  This module validates a
small three-variant schema, binds every reviewed artifact by SHA-256, and reads
all bytes through the repository's descriptor-bound artifact primitive before
anything can reach a reviewer prompt.
"""

from __future__ import annotations

import hashlib
import json
import stat
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Annotated, Any, Literal, Self

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    SerializerFunctionWrapHandler,
    StringConstraints,
    TypeAdapter,
    ValidationError,
    model_serializer,
    model_validator,
)

from gnd import input_policy as _rf7_input
from gnd.artifacts import ArtifactError, read_regular_bounded
from gnd.artifacts import reject_json_duplicate_pairs as _reject_duplicate_object_pairs

__all__ = [
    "MVP_TRIAGE_CRITERION",
    "ArtifactReadClaim",
    "DroppedConcern",
    "ExperimentOutcomeReviewRequest",
    "LoadedReviewArtifact",
    "LoadedReviewRequest",
    "ParsedReviewerResponse",
    "PlanReviewRequest",
    "ResponseSalvage",
    "ReviewArtifact",
    "ReviewArtifactMissingError",
    "ReviewConcern",
    "ReviewEvidence",
    "ReviewRequest",
    "ReviewRequestError",
    "ReviewRubric",
    "ReviewerId",
    "ReviewerResponse",
    "ReviewerResponseHead",
    "SpecResultsDeltaReviewRequest",
    "canonical_review_request",
    "load_review_request",
    "parse_reviewer_response",
    "parse_reviewer_response_with_salvage",
    "validate_review_request",
]

SCHEMA_VERSION = 2
DEFAULT_MAX_REQUEST_BYTES = 1024 * 1024
DEFAULT_MAX_ARTIFACT_BYTES = 10 * 1024 * 1024
DEFAULT_MAX_TOTAL_ARTIFACT_BYTES = 30 * 1024 * 1024
DEFAULT_MAX_RESPONSE_BYTES = 1024 * 1024
MAX_RESPONSE_PREAMBLE_LINES = 32
MAX_RETAINED_DROPS = 64
MAX_DROP_REASON_CHARS = 480

_CLOSED_MODEL = ConfigDict(extra="forbid", frozen=True, strict=True)

NonEmptyString = Annotated[
    str,
    StringConstraints(strip_whitespace=True, strict=True, min_length=1),
]
StableId = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        strict=True,
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$",
    ),
]
DropReason = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        strict=True,
        min_length=1,
        max_length=MAX_DROP_REASON_CHARS,
    ),
]
MediaType = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        strict=True,
        min_length=3,
        max_length=128,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9!#$&^_.+-]*/[A-Za-z0-9][A-Za-z0-9!#$&^_.+-]*$",
    ),
]
Sha256 = Annotated[
    str,
    StringConstraints(strict=True, pattern=r"^[0-9a-f]{64}$"),
]
ReviewerId = Literal["claude", "codex", "qwen", "gemini", "kimi", "glm"]
ReviewDisposition = Literal["approve", "revise", "block"]
ConcernSeverity = Literal["low", "medium", "high", "critical"]
ConcernRelevance = Literal["blocking", "hardening", "completeness"]
"""How a concern bears on a demonstrable MVP -- a different axis from severity.

``severity`` rates how bad the flaw is.  ``relevance`` rates whether repairing
it moves the product toward doing something it demonstrably could not do
before.  They are independent: a ``critical`` naming a documentation
inconsistency and a ``critical`` meaning the command exits 0 on invalid input
arrive identically on the severity axis, and the panel had no way to tell them
apart.

- ``blocking``     -- unfixed, the software does not demonstrably do what it
  claims: it crashes, computes a wrong answer, silently accepts bad input, or
  the claim cannot be run at all.
- ``hardening``    -- a real defect with a real consequence, but the
  demonstration still stands.
- ``completeness`` -- the artifact becomes more complete or consistent and no
  user-observable behaviour changes.

This is the REVIEWER's claim about its own concern, carrying exactly the
authority ``severity`` carries: none over the disposition.  Whoever dispositions
the panel assigns the class that governs the repair.
"""


class ReviewRequestError(Exception):
    """A request, artifact, or reviewer response violated its closed contract."""


class ReviewArtifactMissingError(ReviewRequestError):
    """A validated in-repository artifact descriptor names a missing input."""

    def __init__(self, artifact_path: str) -> None:
        self.artifact_path = artifact_path
        super().__init__(f"review artifact {artifact_path} is missing")


def _safe_repository_path(value: str) -> str:
    """Require one already-normalized portable repository-relative path."""

    if "\x00" in value:
        raise ValueError("repository-relative path contains a NUL byte")
    if value != value.strip() or "\\" in value:
        raise ValueError("repository-relative path is not normalized")
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
        raise ValueError("repository-relative path must not be absolute or drive-qualified")
    if not posix.parts or any(part in {"", ".", ".."} for part in posix.parts):
        raise ValueError("repository-relative path contains a non-normal component")
    if posix.as_posix() != value:
        raise ValueError("repository-relative path must use normalized POSIX spelling")
    return value


RepositoryRelativePath = Annotated[
    str,
    StringConstraints(strict=True, min_length=1),
    AfterValidator(_safe_repository_path),
]


class ReviewArtifact(BaseModel):
    """One repository artifact named and bound by its exact bytes."""

    model_config = _CLOSED_MODEL

    path: RepositoryRelativePath
    sha256: Sha256
    media_type: MediaType


MVP_TRIAGE_CRITERION = (
    "MVP first: classify every concern as blocking, hardening, or completeness, "
    "and report blocking concerns first. A concern is blocking only if, left "
    "unfixed, the software does not demonstrably do what it claims. Do not "
    "manufacture completeness concerns to avoid an empty return -- "
    "\"no concerns, and here is what I checked\" is a valid answer."
)
"""The one criterion every GND panel carries, whatever else its rubric says.

Two measured pressures make this structural rather than advisory.  A non-approve
verdict is refused unless it carries a concern (see :class:`ReviewerResponse`),
and across nineteen seat-runs of one milestone no seat ever returned empty --
so a reviewer with nothing blocking to say must still produce something, and
completeness concerns are the cheapest thing to produce.  Requiring the
criterion in the rubric does not repeal that pressure; it makes the reviewer
name the class, so the panel can count how much of a round was worth running.
"""


class ReviewRubric(BaseModel):
    """Closed reviewer instructions shared by every member of a panel."""

    model_config = _CLOSED_MODEL

    name: NonEmptyString
    criteria: tuple[NonEmptyString, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _criteria_are_unique(self) -> Self:
        if len(self.criteria) != len(set(self.criteria)):
            raise ValueError("review rubric criteria must be unique")
        return self



def _require_standing_criterion(rubric: ReviewRubric, schema_version: int) -> None:
    """Refuse a current-version request whose rubric omits the standing criterion.

    Version-conditioned for one reason only: committed panel evidence carries
    rubrics authored before the criterion existed, and a retained run that stops
    parsing is evidence destroyed.  Every request GND builds today is version 2.
    """

    if schema_version < 2:
        return
    if MVP_TRIAGE_CRITERION not in rubric.criteria:
        raise ValueError("review rubric must carry the standing MVP triage criterion")


class PlanReviewRequest(BaseModel):
    """Review one implementation plan."""

    model_config = _CLOSED_MODEL

    schema_version: Literal[1, 2] = SCHEMA_VERSION
    kind: Literal["plan"] = "plan"
    plan: ReviewArtifact
    rubric: ReviewRubric

    @model_validator(mode="after")
    def _rubric_carries_the_standing_criterion(self) -> Self:
        _require_standing_criterion(self.rubric, self.schema_version)
        return self


class ExperimentOutcomeReviewRequest(BaseModel):
    """Review one immutable experiment outcome."""

    model_config = _CLOSED_MODEL

    schema_version: Literal[1, 2] = SCHEMA_VERSION
    kind: Literal["experiment-outcome"] = "experiment-outcome"
    outcome: ReviewArtifact
    rubric: ReviewRubric

    @model_validator(mode="after")
    def _rubric_carries_the_standing_criterion(self) -> Self:
        _require_standing_criterion(self.rubric, self.schema_version)
        return self


class SpecResultsDeltaReviewRequest(BaseModel):
    """Review a specification, measured results, and their stated delta."""

    model_config = _CLOSED_MODEL

    schema_version: Literal[1, 2] = SCHEMA_VERSION
    kind: Literal["spec-results-delta"] = "spec-results-delta"
    spec: ReviewArtifact
    results: ReviewArtifact
    delta: ReviewArtifact
    rubric: ReviewRubric

    @model_validator(mode="after")
    def _rubric_carries_the_standing_criterion(self) -> Self:
        _require_standing_criterion(self.rubric, self.schema_version)
        return self

    @model_validator(mode="after")
    def _roles_are_distinct(self) -> Self:
        paths = (self.spec.path, self.results.path, self.delta.path)
        portable_paths = tuple(unicodedata.normalize("NFKC", path).casefold() for path in paths)
        if len(portable_paths) != len(set(portable_paths)):
            raise ValueError("spec, results, and delta must name distinct artifact paths")
        return self


ReviewRequest = Annotated[
    PlanReviewRequest | ExperimentOutcomeReviewRequest | SpecResultsDeltaReviewRequest,
    Field(discriminator="kind"),
]
_REVIEW_REQUEST_ADAPTER = TypeAdapter(ReviewRequest)


class ReviewEvidence(BaseModel):
    """One concrete source observation supporting a reviewer concern."""

    model_config = _CLOSED_MODEL

    artifact_path: RepositoryRelativePath
    location: NonEmptyString
    observation: NonEmptyString


class ReviewConcern(BaseModel):
    """One evidence-backed issue reported by a reviewer."""

    model_config = _CLOSED_MODEL

    concern_id: StableId
    severity: ConcernSeverity
    relevance: ConcernRelevance | None = None
    title: NonEmptyString
    evidence: tuple[ReviewEvidence, ...] = Field(min_length=1)
    recommendation: NonEmptyString

    @model_serializer(mode="wrap")
    def _absent_relevance_is_not_serialized(
        self,
        handler: SerializerFunctionWrapHandler,
    ) -> dict[str, Any]:
        """Keep every committed response.json byte-identical.

        A concern retained before the relevance axis existed carries ``None``,
        and emitting ``"relevance":null`` for it would change the bytes of runs
        the panel promises to reserialize exactly.  Same precedent as
        ``artifact_reads`` on the response.
        """

        document = handler(self)
        if self.relevance is None:
            document.pop("relevance", None)
        return document

    @model_validator(mode="after")
    def _evidence_is_unique(self) -> Self:
        identities = tuple(
            (entry.artifact_path, entry.location, entry.observation) for entry in self.evidence
        )
        if len(identities) != len(set(identities)):
            raise ValueError("review concern contains duplicate evidence")
        return self


class ArtifactReadClaim(BaseModel):
    """One reviewer-reported read of one referenced artifact.

    This is the design's proof-of-read, restored to a structured home after the
    round that suppressed it: in `panel-run-by-reference` a reviewer verified
    the digest itself and reported it in prose, the next prompt told reviewers
    not to, and `panel-run-by-reference-r2` then had two seats with no
    observable evidence of reading at all.  It is a self-report -- the panel
    can measure engagement (see the envelope's evidence resolution) but cannot
    force a read -- and ``digest_matched: false`` is an integrity signal, not a
    critique of the reviewed artifact.
    """

    model_config = _CLOSED_MODEL

    path: RepositoryRelativePath
    digest_matched: bool


MAX_ARTIFACT_READ_CLAIMS = 64


class ReviewerResponse(BaseModel):
    """Complete closed JSON returned by one expected panel reviewer."""

    model_config = _CLOSED_MODEL

    schema_version: Literal[1, 2] = SCHEMA_VERSION
    reviewer_id: ReviewerId
    disposition: ReviewDisposition
    summary: NonEmptyString
    concerns: tuple[ReviewConcern, ...]
    artifact_reads: tuple[ArtifactReadClaim, ...] = Field(
        default=(), max_length=MAX_ARTIFACT_READ_CLAIMS
    )

    @model_validator(mode="after")
    def _relevance_is_required_at_this_schema_version(self) -> Self:
        """Classification is mandatory for every response the panel asks for.

        ``relevance`` is optional on the TYPE and required at schema version 2,
        which is the only version the prompt requests.  The split exists so
        committed panel evidence from before the axis existed stays loadable --
        ``test_committed_panel_evidence_stays_loadable`` is the guard, and a
        retained run that stops parsing is evidence destroyed, not a schema
        tightened.  Nothing produces a version-1 response any more.
        """

        if self.schema_version < 2:
            return self
        unclassified = tuple(
            concern.concern_id for concern in self.concerns if concern.relevance is None
        )
        if unclassified:
            raise ValueError(
                "every concern must carry a relevance: " + ", ".join(unclassified)
            )
        return self

    @model_serializer(mode="wrap")
    def _absent_reads_are_not_serialized(
        self,
        handler: SerializerFunctionWrapHandler,
    ) -> dict[str, Any]:
        """Keep every committed response.json byte-identical."""

        document = handler(self)
        if not self.artifact_reads:
            document.pop("artifact_reads", None)
        return document

    @model_validator(mode="after")
    def _disposition_and_concerns_agree(self) -> Self:
        identifiers = tuple(concern.concern_id for concern in self.concerns)
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("review response contains duplicate concern identifiers")
        if self.disposition == "approve" and self.concerns:
            raise ValueError("an approve response cannot contain concerns")
        if self.disposition == "approve" and any(
            not claim.digest_matched for claim in self.artifact_reads
        ):
            raise ValueError("an approve response cannot carry a digest mismatch")
        read_paths = tuple(claim.path for claim in self.artifact_reads)
        if len(read_paths) != len(set(read_paths)):
            raise ValueError("artifact read claims must name distinct paths")
        if self.disposition != "approve" and not self.concerns:
            raise ValueError(f"a {self.disposition} response must contain a concern")
        return self


class ReviewerResponseHead(BaseModel):
    """Identity and verdict for one reviewer, validated apart from its concerns.

    The head is never salvaged.  A review whose author or disposition is in
    doubt is not a partial opinion, so a head that fails here fails the seat.

    ``concern_count`` is the exception, and it is deliberate.  It carries no
    authority -- it is a cross-check on a number the panel counts for itself --
    so it is read best-effort and never fails the seat.  Measured: a live Kimi
    seat returned ``"4"`` for it and lost a complete review backed by eleven
    file reads, which is the exact failure this whole design exists to remove.
    """

    model_config = _CLOSED_MODEL

    schema_version: Literal[1, 2] = SCHEMA_VERSION
    reviewer_id: ReviewerId
    disposition: ReviewDisposition
    summary: NonEmptyString
    concern_count: int | None = Field(default=None, ge=0, le=4096)
    artifact_reads: tuple[ArtifactReadClaim, ...] = Field(
        default=(), max_length=MAX_ARTIFACT_READ_CLAIMS
    )


class DroppedConcern(BaseModel):
    """One concern the panel could not retain, and exactly why."""

    model_config = _CLOSED_MODEL

    position: int = Field(ge=1)
    reason: DropReason
    byte_count: int = Field(ge=0)


class ResponseSalvage(BaseModel):
    """What a retained response cost to read, so nothing is dropped in silence.

    ``byte_count`` on a dropped concern is transport-relative and says so here
    rather than overstating its precision: for ``jsonl`` it is the exact source
    line, for ``object`` it is the compact re-serialization of an element whose
    original spelling the whole-document parse did not preserve.

    Only the first ``MAX_RETAINED_DROPS`` drops are recorded individually; the
    rest are counted in ``dropped_overflow``, which keeps a flood of junk lines
    from costing memory proportional to the reviewer's output.
    """

    model_config = _CLOSED_MODEL

    transport: Literal["object", "jsonl"]
    preamble_lines: int = Field(ge=0)
    trailing_lines: int = Field(ge=0)
    declared_concern_count: int | None = Field(default=None, ge=0)
    retained_concern_count: int = Field(ge=0)
    dropped: tuple[DroppedConcern, ...] = Field(default=(), max_length=MAX_RETAINED_DROPS)
    dropped_overflow: int = Field(default=0, ge=0)
    declared_concern_count_unreadable: bool = False
    artifact_reads_dropped: int = Field(default=0, ge=0)
    artifact_reads_unreadable: bool = False
    complete: bool

    @model_serializer(mode="wrap")
    def _default_fields_are_not_serialized(
        self,
        handler: SerializerFunctionWrapHandler,
    ) -> dict[str, Any]:
        """Keep already-published salvage records byte-identical."""

        document = handler(self)
        if not self.declared_concern_count_unreadable:
            document.pop("declared_concern_count_unreadable", None)
        if not self.artifact_reads_dropped:
            document.pop("artifact_reads_dropped", None)
        if not self.artifact_reads_unreadable:
            document.pop("artifact_reads_unreadable", None)
        return document

    @model_validator(mode="after")
    def _completeness_is_derived(self) -> Self:
        positions = tuple(entry.position for entry in self.dropped)
        if len(positions) != len(set(positions)) or positions != tuple(sorted(positions)):
            raise ValueError("dropped concerns must carry unique ascending positions")
        if self.dropped_overflow and len(self.dropped) != MAX_RETAINED_DROPS:
            raise ValueError("unrecorded drops require a full retained drop record")
        if self.declared_concern_count_unreadable and self.declared_concern_count is not None:
            raise ValueError("an unreadable declared count cannot also carry a value")
        derived = (
            self.preamble_lines == 0
            and self.trailing_lines == 0
            and not self.dropped
            and self.dropped_overflow == 0
            and not self.declared_concern_count_unreadable
            and self.artifact_reads_dropped == 0
            and not self.artifact_reads_unreadable
            and self.declared_concern_count in {None, self.retained_concern_count}
        )
        if self.complete is not derived:
            raise ValueError("response salvage completeness must be derived, never asserted")
        return self


class ParsedReviewerResponse(BaseModel):
    """One retained reviewer response together with the record of its reading."""

    model_config = _CLOSED_MODEL

    response: ReviewerResponse
    salvage: ResponseSalvage

    @model_validator(mode="after")
    def _retained_count_matches(self) -> Self:
        if self.salvage.retained_concern_count != len(self.response.concerns):
            raise ValueError("salvage retained count must equal the retained concerns")
        return self


class LoadedReviewArtifact(BaseModel):
    """One validated artifact descriptor paired with its retained exact bytes."""

    model_config = _CLOSED_MODEL

    artifact: ReviewArtifact
    data: bytes

    @model_validator(mode="after")
    def _digest_matches_data(self) -> Self:
        if hashlib.sha256(self.data).hexdigest() != self.artifact.sha256:
            raise ValueError("loaded artifact bytes do not match their SHA-256")
        return self


class LoadedReviewRequest(BaseModel):
    """A normalized request whose complete artifact bytes have been retained."""

    model_config = _CLOSED_MODEL

    request: ReviewRequest
    artifacts: tuple[LoadedReviewArtifact, ...]
    request_sha256: Sha256

    @model_validator(mode="after")
    def _request_and_loaded_artifacts_are_exact(self) -> Self:
        expected = _request_artifacts(self.request)
        if tuple(item.artifact for item in self.artifacts) != expected:
            raise ValueError("loaded artifacts do not exactly match the review request")
        expected_request_sha256 = hashlib.sha256(canonical_review_request(self.request)).hexdigest()
        if self.request_sha256 != expected_request_sha256:
            raise ValueError("loaded request SHA-256 is stale")
        return self


def _canonical_json(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def canonical_review_request(request: ReviewRequest) -> bytes:
    """Return the deterministic JSON identity of one validated request."""

    if not isinstance(
        request,
        (
            PlanReviewRequest,
            ExperimentOutcomeReviewRequest,
            SpecResultsDeltaReviewRequest,
        ),
    ):
        raise TypeError("canonical review request requires a validated request model")
    return _canonical_json(request.model_dump(mode="json"))




def _reject_nonfinite_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant {value!r} is not allowed")


def _unfence(text: str) -> str:
    """Strip one surrounding markdown code fence, if the whole payload is fenced.

    Frontier reviewer CLIs routinely wrap a JSON response in ```json ... ```.
    Measured: claude returned a schema-valid review in panel-run-04 that failed
    at `char 0` on the opening backticks. Refusing that is a GND parsing defect,
    not a reviewer failure -- the response was correct.

    This is deliberately narrow. It unwraps only when the *entire* stripped
    payload is one fenced block, so a fence appearing inside a string value, or
    any trailing prose after the closing fence, still fails closed as before.
    """

    stripped = text.strip()
    if not stripped.startswith("```") or not stripped.endswith("```"):
        return text
    body = stripped[3:-3]
    newline = body.find("\n")
    if newline == -1:
        return text
    info = body[:newline].strip()
    # Only an empty or bare-language info string may be discarded.
    if info and not info.isalnum():
        return text
    return body[newline + 1 :]


def _strict_json_object(raw: bytes, *, label: str) -> dict[str, Any]:
    try:
        text = _unfence(raw.decode("utf-8"))
        document = _rf7_input.loads(
            text,
            object_pairs_hook=_reject_duplicate_object_pairs,
            parse_constant=_reject_nonfinite_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise ReviewRequestError(f"invalid {label} JSON: {error}") from error
    if not isinstance(document, dict):
        raise ReviewRequestError(f"invalid {label} JSON: top level must be an object")
    return document


def _validation_json(value: Mapping[str, Any], *, label: str) -> bytes:
    try:
        return _canonical_json(dict(value))
    except (TypeError, ValueError, UnicodeError) as error:
        raise ReviewRequestError(f"invalid {label}: value is not finite JSON") from error


def validate_review_request(value: Any) -> ReviewRequest:
    """Validate one mapping as exactly one of the three closed request kinds."""

    if not isinstance(value, Mapping):
        raise ReviewRequestError("invalid review request: top level must be an object")
    try:
        return _REVIEW_REQUEST_ADAPTER.validate_json(
            _validation_json(value, label="review request"),
            strict=True,
        )
    except ValidationError as error:
        raise ReviewRequestError(f"invalid review request: {error}") from error


def _request_artifacts(request: ReviewRequest) -> tuple[ReviewArtifact, ...]:
    if isinstance(request, PlanReviewRequest):
        return (request.plan,)
    if isinstance(request, ExperimentOutcomeReviewRequest):
        return (request.outcome,)
    if isinstance(request, SpecResultsDeltaReviewRequest):
        return (request.spec, request.results, request.delta)
    raise TypeError("unknown validated review request type")


def _repository_root_identity(root: Path) -> tuple[int, int]:
    try:
        info = root.lstat()
    except OSError as error:
        raise ReviewRequestError(
            f"review repository root could not be inspected: {error}"
        ) from error
    if stat.S_ISLNK(info.st_mode):
        raise ReviewRequestError("review repository root is a symlink")
    if not stat.S_ISDIR(info.st_mode):
        raise ReviewRequestError("review repository root is not a directory")
    return info.st_dev, info.st_ino


def _assert_repository_root_identity(root: Path, expected: tuple[int, int]) -> None:
    try:
        current = root.lstat()
    except OSError as error:
        raise ReviewRequestError(f"review repository root changed: {error}") from error
    if stat.S_ISLNK(current.st_mode) or not stat.S_ISDIR(current.st_mode):
        raise ReviewRequestError("review repository root changed type")
    if (current.st_dev, current.st_ino) != expected:
        raise ReviewRequestError("review repository root changed identity")


def _validate_bound(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ReviewRequestError(f"{name} must be a nonnegative integer byte cap")


def load_review_request(
    repository_root: str | Path,
    request_path: str,
    *,
    max_request_bytes: int = DEFAULT_MAX_REQUEST_BYTES,
    max_artifact_bytes: int = DEFAULT_MAX_ARTIFACT_BYTES,
    max_total_artifact_bytes: int = DEFAULT_MAX_TOTAL_ARTIFACT_BYTES,
) -> LoadedReviewRequest:
    """Load a request and all referenced artifacts from one retained root identity."""

    _validate_bound("request byte cap", max_request_bytes)
    _validate_bound("artifact per-file byte cap", max_artifact_bytes)
    _validate_bound("artifact aggregate byte cap", max_total_artifact_bytes)
    try:
        normalized_request_path = _safe_repository_path(request_path)
    except (TypeError, ValueError) as error:
        raise ReviewRequestError(f"review request path is invalid: {error}") from error

    root = Path(repository_root)
    root_identity = _repository_root_identity(root)
    try:
        request_bytes, _ = read_regular_bounded(
            root,
            normalized_request_path,
            max_bytes=max_request_bytes,
            expected_root=root_identity,
        )
    except ArtifactError as error:
        raise ReviewRequestError(
            f"review request could not be read within its cap: {error}"
        ) from error

    document = _strict_json_object(request_bytes, label="review request")
    request = validate_review_request(document)
    loaded: list[LoadedReviewArtifact] = []
    total_bytes = 0
    for artifact in _request_artifacts(request):
        try:
            data, snapshot = read_regular_bounded(
                root,
                artifact.path,
                max_bytes=max_artifact_bytes,
                expected_root=root_identity,
            )
        except ArtifactError as error:
            if isinstance(error.__cause__, FileNotFoundError):
                raise ReviewArtifactMissingError(artifact.path) from error
            raise ReviewRequestError(
                f"review artifact {artifact.path} failed its regular per-file byte check: {error}"
            ) from error
        if snapshot.sha256 != artifact.sha256:
            raise ReviewRequestError(
                f"review artifact {artifact.path} sha256 does not match the request"
            )
        total_bytes += len(data)
        if total_bytes > max_total_artifact_bytes:
            raise ReviewRequestError(
                f"review artifact aggregate total exceeds the {max_total_artifact_bytes}-byte cap"
            )
        loaded.append(LoadedReviewArtifact(artifact=artifact, data=data))

    _assert_repository_root_identity(root, root_identity)
    canonical = canonical_review_request(request)
    return LoadedReviewRequest(
        request=request,
        artifacts=tuple(loaded),
        request_sha256=hashlib.sha256(canonical).hexdigest(),
    )


def _validate_expected_reviewer(value: str) -> ReviewerId:
    allowed = {"claude", "codex", "qwen", "gemini", "kimi", "glm"}
    if value not in allowed:
        raise ReviewRequestError(f"expected reviewer {value!r} is not a closed reviewer ID")
    return value  # type: ignore[return-value]


def _validate_allowed_artifact_paths(
    paths: Sequence[str] | None,
) -> frozenset[str] | None:
    if paths is None:
        return None
    normalized: set[str] = set()
    for path in paths:
        try:
            normalized.add(_safe_repository_path(path))
        except (TypeError, ValueError) as error:
            raise ReviewRequestError(f"allowed review artifact path is invalid: {error}") from error
    return frozenset(normalized)


_UNPARSABLE = object()


def _drop_reason(text: object) -> str:
    collapsed = " ".join(str(text).split())
    return collapsed[:MAX_DROP_REASON_CHARS] if collapsed else "unstated"


def _looks_like_json(text: str, *, before_head: bool) -> bool:
    """Whether a line claims to be JSON, whether or not it parses.

    This is a heuristic and cannot be anything else: prose and broken JSON are
    not separable by inspection, and the panel review of this very change found
    both of its edges -- a garbled head that omits its opening brace reads as
    prose, and prose that opens with a bracket read as broken JSON.  What makes
    the heuristic safe is not its accuracy but the invariant beside it: an
    ``approve`` response must be a clean document, so no misclassification can
    turn a verdict into a more permissive one.

    It is deliberately asymmetric.  Before the head a match is fatal, so only
    ``{`` counts -- prose opening with ``[`` is ordinary, and the measured qwen
    preamble proves prose mentioning braces is too.  After the head a match
    only means "dropped concern rather than epilogue", where the stricter
    reading costs an accurate record and nothing else.
    """

    return text.startswith("{") if before_head else text.startswith(("{", "["))


def _json_object_or_none(text: str) -> dict[str, Any] | None:
    """Return one strict JSON object, or None for anything else at all.

    ``RecursionError`` is caught with the parse errors deliberately: deeply
    nested reviewer output is malformed input, not an internal defect, and
    letting it escape would abort the other four seats.
    """

    try:
        document = _rf7_input.loads(
            text,
            object_pairs_hook=_reject_duplicate_object_pairs,
            parse_constant=_reject_nonfinite_constant,
        )
    except (json.JSONDecodeError, ValueError, RecursionError):
        return None
    return document if isinstance(document, dict) else None


def _compact_bytes(value: Any) -> int:
    try:
        return len(
            json.dumps(
                value,
                ensure_ascii=False,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        )
    except (TypeError, ValueError, RecursionError):
        return 0


def _readable_concern_count(value: Any) -> int | None:
    """Read an advisory count generously, because it may never cost a seat.

    A bare integer, an integral float, and a decimal string all name the same
    number unambiguously.  Anything else is unreadable, and unreadable is
    recorded rather than fatal.
    """

    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        candidate = value
    elif isinstance(value, float):
        if not value.is_integer():
            return None
        candidate = int(value)
    elif isinstance(value, str):
        text = value.strip()
        if not text.isdigit():
            return None
        candidate = int(text)
    else:
        return None
    return candidate if 0 <= candidate <= 4096 else None


def _readable_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "false"}:
            return lowered == "true"
    return None


@dataclass(frozen=True)
class _ParsedHead:
    """One strictly validated head plus the record of its lenient fields."""

    head: ReviewerResponseHead
    declared_count_unreadable: bool
    reads_dropped: int
    reads_unreadable: bool


def _readable_artifact_reads(
    value: Any,
    allowed_paths: frozenset[str] | None,
) -> tuple[tuple[ArtifactReadClaim, ...], int, bool]:
    """Read the reviewer's read report generously, because it is a self-report.

    Like ``concern_count``, this field carries no authority -- the panel
    measures engagement itself against the bytes it holds -- so nothing here
    may cost a seat.  Well-formed entries are kept, entries that are garbage,
    duplicated, or name a path outside the request are counted as dropped, and
    a field that is not a list at all is recorded as unreadable.
    """

    if not isinstance(value, list):
        return (), 0, True
    claims: list[ArtifactReadClaim] = []
    seen: set[str] = set()
    dropped = 0
    for entry in value[:MAX_ARTIFACT_READ_CLAIMS]:
        if not isinstance(entry, Mapping):
            dropped += 1
            continue
        path_value = entry.get("path")
        matched = _readable_bool(entry.get("digest_matched"))
        if not isinstance(path_value, str) or matched is None:
            dropped += 1
            continue
        try:
            path = _safe_repository_path(path_value.strip())
        except (TypeError, ValueError):
            dropped += 1
            continue
        if path in seen or (allowed_paths is not None and path not in allowed_paths):
            dropped += 1
            continue
        seen.add(path)
        claims.append(ArtifactReadClaim(path=path, digest_matched=matched))
    dropped += max(0, len(value) - MAX_ARTIFACT_READ_CLAIMS)
    return tuple(claims), dropped, False


def _validated_head(
    document: Mapping[str, Any],
    reviewer_id: ReviewerId,
    allowed_paths: frozenset[str] | None = None,
) -> _ParsedHead:
    """Validate the authoritative head strictly and its lenient fields gently.

    Identity, disposition, and summary are authoritative and strict.  The two
    self-report fields -- ``concern_count`` and ``artifact_reads`` -- are read
    best-effort and recorded rather than refused, because a cross-check that
    can cost a seat becomes the exact trivial-loss failure this parser exists
    to remove.  Measured twice: a live seat lost a complete review to the
    string ``"4"``.
    """

    declared = document.get("concern_count")
    readable = _readable_concern_count(declared) if declared is not None else None
    count_unreadable = declared is not None and readable is None
    reads_value = document.get("artifact_reads")
    if reads_value is None:
        reads, reads_dropped, reads_unreadable = (), 0, False
    else:
        reads, reads_dropped, reads_unreadable = _readable_artifact_reads(
            reads_value, allowed_paths
        )
    authoritative = {
        key: value
        for key, value in document.items()
        if key not in {"concern_count", "artifact_reads"}
    }
    if readable is not None:
        authoritative["concern_count"] = readable
    try:
        head = ReviewerResponseHead.model_validate_json(
            _validation_json(authoritative, label="reviewer response head"),
            strict=True,
        )
    except ValidationError as error:
        raise ReviewRequestError(f"invalid reviewer response: {error}") from error
    if head.reviewer_id != reviewer_id:
        raise ReviewRequestError(
            f"reviewer identity mismatch: expected {reviewer_id}, got {head.reviewer_id}"
        )
    return _ParsedHead(
        head=head.model_copy(update={"artifact_reads": reads}),
        declared_count_unreadable=count_unreadable,
        reads_dropped=reads_dropped,
        reads_unreadable=reads_unreadable,
    )


class _ConcernCollector:
    """Validate concerns as they are scanned, retaining nothing unbounded.

    Every candidate is validated and then released, so a reviewer cannot make
    the panel hold memory proportional to its own output: what survives is the
    retained concerns, which the response byte cap already bounds, and at most
    ``MAX_RETAINED_DROPS`` drop records.
    """

    def __init__(self, allowed_paths: frozenset[str] | None) -> None:
        self._allowed_paths = allowed_paths
        self._seen_ids: set[str] = set()
        self.retained: list[ReviewConcern] = []
        self.dropped: list[DroppedConcern] = []
        self.dropped_overflow = 0
        self.candidate_count = 0

    def _drop(self, position: int, byte_count: int, reason: str) -> None:
        if len(self.dropped) < MAX_RETAINED_DROPS:
            self.dropped.append(
                DroppedConcern(
                    position=position,
                    reason=_drop_reason(reason),
                    byte_count=byte_count,
                )
            )
        else:
            self.dropped_overflow += 1

    def offer(self, position: int, byte_count: int, candidate: Any) -> None:
        """Take one concern candidate, or record exactly why it was dropped."""

        self.candidate_count += 1
        if candidate is _UNPARSABLE:
            self._drop(position, byte_count, "line is not a JSON object")
            return
        if not isinstance(candidate, Mapping):
            self._drop(position, byte_count, "concern is not a JSON object")
            return
        try:
            concern = ReviewConcern.model_validate_json(
                _validation_json(candidate, label="reviewer concern"),
                strict=True,
            )
        except (ValidationError, ReviewRequestError, RecursionError) as error:
            self._drop(position, byte_count, f"concern failed closed validation: {error}")
            return
        if concern.concern_id in self._seen_ids:
            self._drop(position, byte_count, f"duplicate concern identifier {concern.concern_id}")
            return
        if self._allowed_paths is not None:
            outside = sorted(
                {
                    evidence.artifact_path
                    for evidence in concern.evidence
                    if evidence.artifact_path not in self._allowed_paths
                }
            )
            if outside:
                self._drop(
                    position,
                    byte_count,
                    "concern cites an artifact outside the request: " + ", ".join(outside),
                )
                return
        self._seen_ids.add(concern.concern_id)
        self.retained.append(concern)


def _with_drops(error: object, collector: _ConcernCollector) -> str:
    message = " ".join(str(error).split())
    total = len(collector.dropped) + collector.dropped_overflow
    if not total:
        return message
    reasons = "; ".join(entry.reason for entry in collector.dropped[:8])
    return f"{message}; {total} concern(s) dropped: {reasons}"


def _require_clean_approval(
    head: ReviewerResponseHead,
    *,
    candidate_count: int,
    preamble_lines: int,
    trailing_lines: int,
) -> None:
    """An approving response must be a clean document, or it is not approval.

    Approval is the one disposition where anything the panel could not read
    makes the verdict MORE permissive than what the reviewer wrote.  This rule
    is what actually closes verdict laundering, and unlike the prose heuristic
    it holds no matter how an unreadable line was classified.
    """

    if head.disposition != "approve":
        return
    if candidate_count:
        raise ReviewRequestError(
            "invalid reviewer response: an approve response cannot carry concerns"
        )
    if preamble_lines or trailing_lines:
        raise ReviewRequestError(
            "invalid reviewer response: an approve response cannot carry unread lines"
        )


def _assemble_response(
    parsed_head: _ParsedHead,
    collector: _ConcernCollector,
    *,
    transport: Literal["object", "jsonl"],
    preamble_lines: int,
    trailing_lines: int,
) -> ParsedReviewerResponse:
    """Build the response from a strictly validated head and what survived."""

    head = parsed_head.head
    _require_clean_approval(
        head,
        candidate_count=collector.candidate_count,
        preamble_lines=preamble_lines,
        trailing_lines=trailing_lines,
    )
    try:
        response = ReviewerResponse(
            schema_version=head.schema_version,
            reviewer_id=head.reviewer_id,
            disposition=head.disposition,
            summary=head.summary,
            concerns=tuple(collector.retained),
            artifact_reads=head.artifact_reads,
        )
    except ValidationError as error:
        raise ReviewRequestError(
            f"invalid reviewer response: {_with_drops(error, collector)}"
        ) from error
    retained = len(collector.retained)
    try:
        salvage = ResponseSalvage(
            transport=transport,
            preamble_lines=preamble_lines,
            trailing_lines=trailing_lines,
            declared_concern_count=head.concern_count,
            retained_concern_count=retained,
            dropped=tuple(collector.dropped),
            dropped_overflow=collector.dropped_overflow,
            declared_concern_count_unreadable=parsed_head.declared_count_unreadable,
            artifact_reads_dropped=parsed_head.reads_dropped,
            artifact_reads_unreadable=parsed_head.reads_unreadable,
            complete=(
                preamble_lines == 0
                and trailing_lines == 0
                and not collector.dropped
                and collector.dropped_overflow == 0
                and not parsed_head.declared_count_unreadable
                and parsed_head.reads_dropped == 0
                and not parsed_head.reads_unreadable
                and head.concern_count in {None, retained}
            ),
        )
        return ParsedReviewerResponse(response=response, salvage=salvage)
    except ValidationError as error:
        raise ReviewRequestError(f"invalid reviewer response record: {error}") from error


def _object_transport(
    document: Mapping[str, Any],
    *,
    reviewer_id: ReviewerId,
    allowed_paths: frozenset[str] | None,
    preamble_lines: int,
    trailing_lines: int,
) -> ParsedReviewerResponse:
    """Read the whole-response-as-one-object transport, salvaging per element."""

    concerns_value = document["concerns"]
    if not isinstance(concerns_value, list):
        raise ReviewRequestError("invalid reviewer response: concerns must be a JSON array")
    parsed_head = _validated_head(
        {key: value for key, value in document.items() if key != "concerns"},
        reviewer_id,
        allowed_paths,
    )
    collector = _ConcernCollector(allowed_paths)
    for index, element in enumerate(concerns_value, start=1):
        collector.offer(index, _compact_bytes(element), element)
    return _assemble_response(
        parsed_head,
        collector,
        transport="object",
        preamble_lines=preamble_lines,
        trailing_lines=trailing_lines,
    )


def parse_reviewer_response_with_salvage(
    raw: bytes,
    *,
    expected_reviewer: str,
    allowed_artifact_paths: Sequence[str] | None = None,
    max_response_bytes: int = DEFAULT_MAX_RESPONSE_BYTES,
) -> ParsedReviewerResponse:
    """Read one reviewer response so a single bad concern costs only itself.

    Measured across the twelve committed panel runs: four of the five
    ``malformed`` envelopes carried a usable review that a whole-document parse
    threw away with the one fault in it.  The head -- identity and disposition
    -- is still validated strictly and is never salvaged; every concern is
    validated alone, and anything dropped is recorded rather than forgotten.

    This function is total over its input: every reachable failure, including
    hostile nesting and unencodable text, leaves as ``ReviewRequestError``.
    """

    _validate_bound("reviewer response byte cap", max_response_bytes)
    if not isinstance(raw, bytes):
        raise ReviewRequestError("invalid reviewer response: raw output must be bytes")
    if len(raw) > max_response_bytes:
        raise ReviewRequestError(
            f"invalid reviewer response: output exceeds the {max_response_bytes}-byte cap"
        )
    reviewer_id = _validate_expected_reviewer(expected_reviewer)
    allowed_paths = _validate_allowed_artifact_paths(allowed_artifact_paths)
    try:
        text = _unfence(raw.decode("utf-8"))
    except UnicodeDecodeError as error:
        raise ReviewRequestError("invalid reviewer response: output is not UTF-8") from error

    stripped = text.strip()
    whole = _json_object_or_none(stripped) if stripped else None
    if whole is not None and "concerns" in whole:
        return _object_transport(
            whole,
            reviewer_id=reviewer_id,
            allowed_paths=allowed_paths,
            preamble_lines=0,
            trailing_lines=0,
        )

    head_document: dict[str, Any] | None = None
    parsed_head: _ParsedHead | None = None
    preamble_lines = 0
    collector = _ConcernCollector(allowed_paths)
    # Non-JSON lines are held only as (position, size) until the next object
    # line proves them interior, or end of input proves them a trailing run.
    pending: list[tuple[int, int]] = []
    pending_overflow = 0

    for number, line in enumerate(text.splitlines(), start=1):
        candidate = line.strip()
        if not candidate:
            continue
        parsed = _json_object_or_none(candidate)
        if head_document is None:
            if parsed is None:
                if _looks_like_json(candidate, before_head=True):
                    raise ReviewRequestError(
                        "invalid reviewer response: malformed JSON precedes the response head"
                    )
                preamble_lines += 1
                if preamble_lines > MAX_RESPONSE_PREAMBLE_LINES:
                    raise ReviewRequestError(
                        "invalid reviewer response: more than "
                        f"{MAX_RESPONSE_PREAMBLE_LINES} lines precede the response"
                    )
                continue
            head_document = parsed
            if "concerns" in head_document:
                # A whole-object response that only line scanning could reach,
                # because prose or a fence surrounds it.
                return _object_transport(
                    head_document,
                    reviewer_id=reviewer_id,
                    allowed_paths=allowed_paths,
                    preamble_lines=preamble_lines,
                    trailing_lines=_trailing_prose_lines(text, number),
                )
            parsed_head = _validated_head(head_document, reviewer_id, allowed_paths)
            continue
        if parsed is None and not _looks_like_json(candidate, before_head=False):
            if len(pending) < MAX_RETAINED_DROPS:
                pending.append((number, len(line.encode("utf-8"))))
            else:
                pending_overflow += 1
            continue
        for position, byte_count in pending:
            collector.offer(position, byte_count, _UNPARSABLE)
        for _ in range(pending_overflow):
            collector.offer(number, 0, _UNPARSABLE)
        pending, pending_overflow = [], 0
        collector.offer(
            number,
            len(line.encode("utf-8")),
            _UNPARSABLE if parsed is None else parsed,
        )

    if parsed_head is None:
        raise ReviewRequestError("invalid reviewer response: output contains no JSON object")
    return _assemble_response(
        parsed_head,
        collector,
        transport="jsonl",
        preamble_lines=preamble_lines,
        trailing_lines=len(pending) + pending_overflow,
    )


def _trailing_prose_lines(text: str, after_line: int) -> int:
    """Count prose after a whole-object response, refusing a second document.

    Prose after a complete response is an epilogue.  Another JSON line is a
    second opinion the panel has no way to attribute, and is refused rather
    than counted as prose.
    """

    count = 0
    for number, line in enumerate(text.splitlines(), start=1):
        candidate = line.strip() if number > after_line else ""
        if not candidate:
            continue
        if _looks_like_json(candidate, before_head=False):
            raise ReviewRequestError(
                "invalid reviewer response: output contains more than one JSON document"
            )
        count += 1
    return count


def parse_reviewer_response(
    raw: bytes,
    *,
    expected_reviewer: str,
    allowed_artifact_paths: Sequence[str] | None = None,
    max_response_bytes: int = DEFAULT_MAX_RESPONSE_BYTES,
) -> ReviewerResponse:
    """Parse one reviewer response that must have been read completely.

    This keeps the pre-salvage contract exactly: a response that could not be
    read whole is an error here, not a quietly shortened opinion.  Callers that
    want the salvaged form must ask for it, and must then carry its record.
    """

    parsed = parse_reviewer_response_with_salvage(
        raw,
        expected_reviewer=expected_reviewer,
        allowed_artifact_paths=allowed_artifact_paths,
        max_response_bytes=max_response_bytes,
    )
    if not parsed.salvage.complete:
        raise ReviewRequestError(
            "invalid reviewer response: it could not be read completely -- "
            "use parse_reviewer_response_with_salvage to accept and record the loss"
        )
    return parsed.response
