"""The two skill-to-code handoff contracts: document manifest + extraction sidecar
(R-04‴, R-05″, D-15).

The adopted shape makes the skill-to-code handoff a FILE ON DISK: the
``gnd-render-doc`` skill writes a document plus a :class:`DocumentManifest`,
the ``gnd-extract`` skill writes a population plus an
:class:`ExtractionSidecar` (``<population>.extraction.json``), and the code
validators (``gnd verify``, ``gnd doccheck``) consume both fail-closed. Both
files are UNTRUSTED metadata naming paths and digests, so this module applies
``synth/provenance.py``'s sidecar discipline without importing it (the C6
analog): ``extra="forbid"`` (an unknown field is a load-time rejection — a
swapped-format or schema-drifted file can never read as valid), every sha256
digest REQUIRED (the digest IS the binding; WR-02: record the model ID STRING,
the digest is the identity), and RELATIVE paths only, resolved against the
file's own directory (``test_measure_corpus_root``'s untrusted-index rule: an
absolute or ``..``-escaping entry is refused, never resolved — T-02.1-07).

Reads are byte-capped (:data:`MAX_MANIFEST_BYTES`) in ``report.py``'s
``MAX_POPULATION_ISSUES`` posture: bound every untrusted-input-proportional
resource (T-02.1-08).

All failures raise :class:`ManifestError` carrying issue-style
:class:`~gnd.model.ValidationIssue` records so ``gnd verify`` can map them to
``extraction:sidecar-invalid`` payload issues without re-deriving messages.
"""

from __future__ import annotations

import json
import os
import stat
from collections.abc import Iterator
from contextlib import contextmanager
from io import BufferedReader
from pathlib import Path, PurePosixPath
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
    field_validator,
    model_validator,
)

from gnd import input_policy as _rf7_input
from gnd.errors import ValidationIssue
from gnd.errors import issues_from_validation_error as _validation_issues
from gnd.manifest_paths import manifest_path_issue

__all__ = [
    "MAX_MANIFEST_BYTES",
    "Distractor",
    "DocumentManifest",
    "ExtractionSidecar",
    "ExtractionSkipMarker",
    "ManifestError",
    "manifest_path_issue",
    "open_manifest_relative_path",
    "read_document_manifest",
    "read_extraction_sidecar",
    "read_extraction_skip_marker",
    "resolve_manifest_relative_path",
]

#: Byte cap on a manifest/sidecar read. These files carry a handful of paths,
#: digests and distractor sentences — 1 MB is generous headroom, and the cap is
#: what keeps a hostile 10 GB "sidecar" from being slurped before validation
#: (the MAX_POPULATION_BYTES posture, T-02.1-08).
MAX_MANIFEST_BYTES = 1 * 1024 * 1024

#: The CLOSED distractor vocabulary (R-05). doccheck demands at least one of
#: EACH kind; a kind outside this set is rejected at load, not at check time.
DistractorKind = Literal["out-of-model", "near-miss-entity", "absent-fact"]
NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ManifestError(Exception):
    """A manifest/sidecar failed to read, parse, validate, or named an unsafe
    path. Loud by design — a silently-skipped handoff file is an unrun
    extraction reading as green (T-02.1-11).

    Carries ``issues`` (:class:`~gnd.model.ValidationIssue` records) so
    ``gnd verify`` maps the failure into its payload verbatim.
    """

    def __init__(self, message: str, issues: list[ValidationIssue] | None = None):
        super().__init__(message)
        self.issues: list[ValidationIssue] = issues or [
            ValidationIssue(
                path="", message=message, rule_id="extraction:sidecar-invalid"
            )
        ]


class Distractor(BaseModel):
    """One planted distractor (R-05). ``fact_type``/``roles`` are REQUIRED when
    ``kind`` is ``absent-fact`` — doccheck's obligation 3 must be able to prove
    the fact is genuinely absent under ``identity_key``, so a distractor it
    cannot check fails closed at load."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    kind: DistractorKind
    text: str
    fact_type: str | None = Field(default=None, min_length=1)
    roles: dict[str, Any] | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def _absent_fact_is_checkable(self) -> Distractor:
        if self.kind == "absent-fact" and (self.fact_type is None or self.roles is None):
            raise ValueError(
                "an absent-fact distractor must carry fact_type AND roles so its "
                "genuine absence is checkable under identity_key (R-05)"
            )
        return self


class DocumentManifest(BaseModel):
    """What ``gnd-render-doc`` emitted, bound by digest to everything it
    consumed (R-05″). ``executing_model`` is the model ID STRING, never a
    family label (WR-02 — ``proposer_model``/``prompt_version`` are the exact
    precedent). ``applicable_sha256`` binds the applicable-set artifact the
    renderer honored, so doccheck enforces the rendering obligation over the
    SAME scope the renderer was given (R-10′/P-2)."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_version: Literal[1]
    #: Relative path to the rendered document, resolved against this file's dir.
    document: NonEmptyString
    document_sha256: str
    #: The model reference (opaque ID string; never dereferenced — T-01-05).
    model: str
    model_sha256: str
    #: Relative path to the source population the renderer verbalized.
    source_population: NonEmptyString
    source_population_sha256: str
    #: Digest of the applicable-set artifact (<stem>.applicable.json).
    applicable_sha256: str
    #: Renderer identity — expected "gnd-render-doc"; recorded, and doccheck's
    #: obligation 4 demands the fields non-empty.
    renderer_skill: Literal["gnd-render-doc"]
    renderer_skill_version: NonEmptyString
    executing_model: NonEmptyString
    distractors: list[Distractor]


class ExtractionSidecar(BaseModel):
    """What ``gnd-extract`` emitted beside its population
    (``<population>.extraction.json``), bound by digest to the population, the
    model, the projection it decoded against, and the document it read
    (R-04‴/T-02.1-10). The population file itself stays untouched — D-15 froze
    the interchange format, so provenance lives HERE."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_version: Literal[1]
    #: Relative path to the population this sidecar describes.
    population: NonEmptyString
    population_sha256: str
    #: The model reference (opaque ID string; never dereferenced).
    model: str
    model_sha256: str
    projection_sha256: str
    #: Relative path to the document the extraction was read from.
    document: NonEmptyString
    document_sha256: str
    #: Extractor identity — expected "gnd-extract"; recorded into the verify
    #: payload's extraction block verbatim.
    skill: Literal["gnd-extract"]
    skill_version: NonEmptyString
    executing_model: NonEmptyString


class ExtractionSkipMarker(BaseModel):
    """The intentional fidelity opt-out marker; malformed means failed."""

    model_config = ConfigDict(extra="forbid", strict=True)

    reason: str = Field(min_length=1)

    @field_validator("reason")
    @classmethod
    def _reason_is_stated(cls, value: str) -> str:
        reason = value.strip()
        if not reason:
            raise ValueError("reason must contain non-whitespace text")
        return reason


#: field name -> is it a path field that must stay relative and contained.
_MANIFEST_PATH_FIELDS = ("document", "source_population")
_SIDECAR_PATH_FIELDS = ("population", "document")


def resolve_manifest_relative_path(
    manifest_path: str | Path,
    value: str,
    *,
    field: str,
    rule_id: str,
) -> Path:
    """Resolve a manifest-relative path without following symlink components."""
    if (issue := manifest_path_issue(field, value, rule_id)) is not None:
        raise ManifestError(issue.message, [issue])
    try:
        manifest_dir = Path(manifest_path).resolve().parent
        candidate = manifest_dir / value
    except (OSError, ValueError) as error:
        message = f"{field} could not be constructed safely: {error}"
        raise ManifestError(
            message,
            [ValidationIssue(path=field, message=message, rule_id=rule_id)],
        ) from error
    current = manifest_dir
    for part in Path(value).parts:
        current /= part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            break
        except OSError as error:
            raise ManifestError(
                f"{field} could not be inspected safely: {error}",
                [
                    ValidationIssue(
                        path=field,
                        message=str(error),
                        rule_id=rule_id,
                    )
                ],
            ) from error
        if stat.S_ISLNK(mode):
            message = (
                f"{field} traverses symlink component {current}; manifest-relative "
                "reads refuse symlinks so they cannot escape their case directory"
            )
            raise ManifestError(
                message,
                [ValidationIssue(path=field, message=message, rule_id=rule_id)],
            )
    try:
        resolved = candidate.resolve(strict=False)
    except (OSError, RuntimeError, ValueError) as error:
        message = f"{field} could not be resolved safely: {error}"
        raise ManifestError(
            message,
            [ValidationIssue(path=field, message=message, rule_id=rule_id)],
        ) from error
    try:
        resolved.relative_to(manifest_dir)
    except ValueError as error:
        message = (
            f"{field} resolves outside the manifest directory ({resolved}); "
            "manifest-relative reads must remain contained"
        )
        raise ManifestError(
            message,
            [ValidationIssue(path=field, message=message, rule_id=rule_id)],
        ) from error
    return resolved


@contextmanager
def open_manifest_relative_path(
    manifest_path: str | Path,
    value: str,
    *,
    field: str,
    rule_id: str,
) -> Iterator[tuple[Path, BufferedReader]]:
    """Open a contained manifest-relative regular file without following links.

    Resolution supplies the diagnostic path and containment check. The actual
    open then walks from the manifest directory through directory descriptors
    with ``O_NOFOLLOW`` so a component cannot be swapped after validation.
    """
    resolved = resolve_manifest_relative_path(
        manifest_path, value, field=field, rule_id=rule_id
    )
    manifest_dir = Path(manifest_path).resolve().parent
    parts = PurePosixPath(value).parts
    directory_fd = os.open(
        manifest_dir,
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0),
    )
    try:
        for part in parts[:-1]:
            next_fd = os.open(
                part,
                os.O_RDONLY
                | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=directory_fd,
            )
            os.close(directory_fd)
            directory_fd = next_fd
        leaf_fd = os.open(
            parts[-1],
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=directory_fd,
        )
        info = os.fstat(leaf_fd)
        if not stat.S_ISREG(info.st_mode):
            os.close(leaf_fd)
            raise OSError(f"{field} is not a regular file")
    except (OSError, ValueError) as error:
        message = f"{field} could not be opened safely without following links: {error}"
        raise ManifestError(
            message,
            [ValidationIssue(path=field, message=message, rule_id=rule_id)],
        ) from error
    finally:
        os.close(directory_fd)

    stream = os.fdopen(leaf_fd, "rb")
    try:
        yield resolved, stream
    finally:
        stream.close()


def _read_document(path: Path, rule_id: str) -> Any:
    """Byte-capped read + JSON parse, every failure a :class:`ManifestError`."""
    try:
        size = path.stat().st_size
    except OSError as error:
        raise ManifestError(
            f"{path} could not be read: {error}",
            [ValidationIssue(path=str(path), message=str(error), rule_id=rule_id)],
        ) from error
    if size > MAX_MANIFEST_BYTES:
        message = (
            f"{path} is {size} bytes, over the {MAX_MANIFEST_BYTES}-byte cap for "
            f"untrusted manifest input (T-02.1-08)"
        )
        raise ManifestError(
            message,
            [ValidationIssue(path=str(path), message=message, rule_id=rule_id)],
        )
    try:
        return _rf7_input.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ManifestError(
            f"{path} is not parseable JSON: {error}",
            [ValidationIssue(path=str(path), message=str(error), rule_id=rule_id)],
        ) from error


def _load(
    path: str | Path,
    model_cls: type[BaseModel],
    path_fields: tuple[str, ...],
    rule_id: str,
) -> Any:
    file_path = Path(path)
    document = _read_document(file_path, rule_id)
    try:
        loaded = model_cls.model_validate(document)
    except ValidationError as error:
        raise ManifestError(
            f"{file_path} is not a valid {model_cls.__name__}:\n{error}",
            _validation_issues(error, rule_id),
        ) from error
    issues = [
        issue
        for field in path_fields
        if (issue := manifest_path_issue(field, getattr(loaded, field), rule_id))
        is not None
    ]
    if issues:
        raise ManifestError(
            f"{file_path} names unsafe paths: "
            + "; ".join(issue.message for issue in issues),
            issues,
        )
    return loaded


def read_document_manifest(path: str | Path) -> DocumentManifest:
    """Load a :class:`DocumentManifest` strictly, or raise :class:`ManifestError`.

    Paths inside resolve RELATIVE to ``path``'s own directory; absolute and
    parent-escaping entries are refused here so no caller ever resolves one.
    """
    return _load(
        path, DocumentManifest, _MANIFEST_PATH_FIELDS, "extraction:manifest-invalid"
    )


def read_extraction_sidecar(path: str | Path) -> ExtractionSidecar:
    """Load an :class:`ExtractionSidecar` strictly, or raise :class:`ManifestError`.

    Same containment rules as :func:`read_document_manifest`; the issue records
    carry ``extraction:sidecar-invalid`` so ``gnd verify`` maps them verbatim.
    """
    return _load(
        path, ExtractionSidecar, _SIDECAR_PATH_FIELDS, "extraction:sidecar-invalid"
    )


def read_extraction_skip_marker(path: str | Path) -> ExtractionSkipMarker:
    """Load a byte-capped, closed intentional-opt-out marker."""
    return _load(
        path,
        ExtractionSkipMarker,
        (),
        "extraction:skip-marker-invalid",
    )
