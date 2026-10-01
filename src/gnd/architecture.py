"""Closed, bounded architecture contracts for generated agent projects.

The contract is authored project metadata.  Loading it is therefore total over
arbitrary bytes: the file is read through the shared bounded no-follow reader,
YAML aliases and excessive event streams are refused before construction, the
shape is closed by pydantic, and all semantic paths pass through one lexical
policy walk.

This module only loads declarations.  Static checking belongs to conformance
and smoke execution belongs to the later runner; neither happens here.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    StrictStr,
    ValidationError,
    field_validator,
)
from ruamel.yaml import YAML, YAMLError
from ruamel.yaml.events import AliasEvent, DocumentStartEvent

from gnd.artifacts import (
    ArtifactError,
    LeafSnapshot,
    _safe_parts,
    read_regular_bounded,
    read_regular_bounded_at,
)

__all__ = [
    "ARCHITECTURE_CONTRACT_FILENAME",
    "ARCHITECTURE_CONTRACT_VERSION",
    "MAX_ARCHITECTURE_CONTRACT_BYTES",
    "MAX_ARCHITECTURE_YAML_EVENTS",
    "ArchitectureArtifact",
    "ArchitectureContract",
    "ArchitectureContractError",
    "ArchitectureContractNotFoundError",
    "ArchitectureEntryPoint",
    "ArchitectureExit",
    "ArchitectureIssue",
    "ArchitectureModule",
    "ArchitectureSmoke",
    "ArchitectureSymbol",
    "load_architecture_contract",
    "parse_architecture_contract_bytes",
    "read_architecture_contract_bytes",
]

ARCHITECTURE_CONTRACT_FILENAME = "architecture.contract.yaml"
ARCHITECTURE_CONTRACT_VERSION = 1
MAX_ARCHITECTURE_CONTRACT_BYTES = 1 * 1024 * 1024
MAX_ARCHITECTURE_YAML_EVENTS = 100_000

_RULE_DECODE = "architecture:decode"
_RULE_DOCUMENT_TOO_LARGE = "architecture:document-too-large"
_RULE_YAML = "architecture:yaml"
_RULE_YAML_ALIAS = "architecture:yaml-alias"
_RULE_YAML_DOCUMENT_COUNT = "architecture:yaml-document-count"
_RULE_SHAPE = "architecture:shape"
_RULE_READ = "architecture:read"

_RULE_PATH = "architecture:path-invalid"
_RULE_ENTRY_POINT_DUPLICATE = "architecture:entry-point-duplicate"
#: Brackets delimit pytest's parametrize segment. Whitespace is refused by
#: PREDICATE rather than by an ASCII table: an adversarial review reproduced
#: that a no-break space (U+00A0) and an em space (U+2003) were accepted by the
#: six-character table while ``str.isspace()`` is true for both, and either one
#: splits a node id a selector must be able to name as one word.
_SMOKE_ID_BRACKETS = frozenset("[]")
_RULE_SMOKE_ID_CHARACTERS = "architecture:smoke-id-characters"
_RULE_SMOKE_ID_DUPLICATE = "architecture:smoke-id-duplicate"
_RULE_SMOKE_ENTRY_POINT_UNKNOWN = "architecture:smoke-entry-point-unknown"
_RULE_SMOKE_EXIT_UNDECLARED = "architecture:smoke-exit-undeclared"
_RULE_SMOKE_SUBSTITUTION = "architecture:smoke-substitution"


@dataclass(frozen=True)
class ArchitectureIssue:
    """One ordered architecture-contract diagnostic."""

    path: str
    message: str
    rule_id: str


class ArchitectureContractError(ValueError):
    """An architecture contract could not be safely loaded and validated."""

    def __init__(self, message: str, issues: tuple[ArchitectureIssue, ...]) -> None:
        self.issues = issues
        super().__init__(message)


class ArchitectureContractNotFoundError(ArchitectureContractError):
    """The project does not contain its architecture contract leaf."""


_CLOSED = ConfigDict(extra="forbid", frozen=True)
_ExitCode = Annotated[StrictInt, Field(ge=0, le=255)]


class ArchitectureSymbol(BaseModel):
    model_config = _CLOSED

    name: StrictStr
    parameters: tuple[StrictStr, ...]


class ArchitectureModule(BaseModel):
    model_config = _CLOSED

    path: StrictStr
    symbols: tuple[ArchitectureSymbol, ...]


class ArchitectureArtifact(BaseModel):
    model_config = _CLOSED

    path: StrictStr
    required_by: tuple[StrictStr, ...]


class ArchitectureExit(BaseModel):
    model_config = _CLOSED

    code: _ExitCode
    meaning: StrictStr


class ArchitectureEntryPoint(BaseModel):
    model_config = _CLOSED

    module: StrictStr
    subcommands: tuple[StrictStr, ...]
    flags: tuple[StrictStr, ...]
    consumes: tuple[StrictStr, ...]
    produces: tuple[StrictStr, ...]
    exits: tuple[ArchitectureExit, ...]


class ArchitectureSmoke(BaseModel):
    model_config = _CLOSED

    id: StrictStr
    entry_point: StrictStr
    argv: tuple[StrictStr, ...]
    expect_exit: _ExitCode


class ArchitectureContract(BaseModel):
    model_config = _CLOSED

    contract_version: Literal[ARCHITECTURE_CONTRACT_VERSION]
    modules: tuple[ArchitectureModule, ...]
    artifacts: tuple[ArchitectureArtifact, ...]
    entry_points: tuple[ArchitectureEntryPoint, ...]
    smoke: tuple[ArchitectureSmoke, ...]

    @field_validator("contract_version", mode="before")
    @classmethod
    def _contract_version_is_a_strict_integer(cls, value: object) -> object:
        if type(value) is not int:
            raise ValueError("contract_version must be the integer 1")
        return value


def _issue(path: str, message: str, rule_id: str) -> ArchitectureIssue:
    return ArchitectureIssue(path=path, message=message, rule_id=rule_id)


def _raise_one(source: str, message: str, rule_id: str) -> None:
    raise ArchitectureContractError(message, (_issue(source, message, rule_id),))


def _preflight_yaml(text: str, *, source: str) -> None:
    document_count = 0
    try:
        for count, event in enumerate(YAML(typ="safe").parse(text), start=1):
            if count > MAX_ARCHITECTURE_YAML_EVENTS:
                _raise_one(
                    source,
                    f"architecture contract exceeds the "
                    f"{MAX_ARCHITECTURE_YAML_EVENTS}-event YAML budget",
                    _RULE_YAML,
                )
            if isinstance(event, AliasEvent):
                _raise_one(
                    source,
                    f"architecture contract uses forbidden YAML alias '*{event.anchor}'",
                    _RULE_YAML_ALIAS,
                )
            if isinstance(event, DocumentStartEvent):
                document_count += 1
    except ArchitectureContractError:
        raise
    except (YAMLError, ValueError, RecursionError, TypeError, OverflowError) as error:
        _raise_one(source, f"architecture contract is not parseable YAML: {error}", _RULE_YAML)
    if document_count != 1:
        _raise_one(
            source,
            f"architecture contract contains {document_count} YAML documents; exactly one is required",
            _RULE_YAML_DOCUMENT_COUNT,
        )


def _load_yaml(text: str, *, source: str) -> object:
    try:
        return YAML(typ="safe").load(text)
    except (YAMLError, ValueError, RecursionError, TypeError, OverflowError) as error:
        _raise_one(source, f"architecture contract is not loadable YAML: {error}", _RULE_YAML)


def _shape_issues(error: ValidationError) -> tuple[ArchitectureIssue, ...]:
    return tuple(
        _issue(
            ".".join(str(part) for part in entry["loc"]),
            entry["msg"],
            _RULE_SHAPE,
        )
        for entry in error.errors()
    )


def _iter_contract_paths(contract: ArchitectureContract) -> Iterator[tuple[str, str]]:
    for module_index, module in enumerate(contract.modules):
        yield f"modules.{module_index}.path", module.path
    for artifact_index, artifact in enumerate(contract.artifacts):
        yield f"artifacts.{artifact_index}.path", artifact.path
        for required_index, required_by in enumerate(artifact.required_by):
            yield f"artifacts.{artifact_index}.required_by.{required_index}", required_by


def _duplicate_issues(
    values: tuple[str, ...], *, coordinate: str, noun: str, rule_id: str
) -> list[ArchitectureIssue]:
    counts = Counter(values)
    seen: set[str] = set()
    issues: list[ArchitectureIssue] = []
    for index, value in enumerate(values):
        if counts[value] > 1 and value not in seen:
            issues.append(
                _issue(
                    f"{coordinate}.{index}",
                    f"duplicate {noun} {value!r}",
                    rule_id,
                )
            )
        seen.add(value)
    return issues


def _semantic_issues(contract: ArchitectureContract) -> tuple[ArchitectureIssue, ...]:
    issues: list[ArchitectureIssue] = []

    for coordinate, value in _iter_contract_paths(contract):
        try:
            _safe_parts(value, field=coordinate)
        except ArtifactError as error:
            issues.append(_issue(coordinate, str(error), _RULE_PATH))

    entry_point_names = tuple(entry.module for entry in contract.entry_points)
    entry_point_counts = Counter(entry_point_names)
    issues.extend(
        _duplicate_issues(
            entry_point_names,
            coordinate="entry_points",
            noun="entry-point module",
            rule_id=_RULE_ENTRY_POINT_DUPLICATE,
        )
    )

    # v4.0 D5 (OQ-P3-IDS-1). A smoke id crosses one boundary this loader can see
    # and the loader is the only place that can refuse it: `gnd exp run`'s
    # tests-mode `required_tests` cites the pytest node id `test_smoke[<id>]`,
    # so a bracket closes the parametrize segment early and whitespace splits an
    # id no selector can name again. Refused at authoring time rather than
    # diagnosed at gate time, where the symptom is a required test that simply
    # never appears.
    for index, smoke in enumerate(contract.smoke):
        offending = sorted(
            {
                character
                for character in smoke.id
                if character in _SMOKE_ID_BRACKETS or character.isspace()
            }
        )
        if offending:
            issues.append(
                _issue(
                    f"smoke.{index}.id",
                    "smoke id "
                    + repr(smoke.id)
                    + " contains "
                    + ", ".join(repr(character) for character in offending)
                    + "; a smoke id becomes the pytest node id test_smoke[<id>] a "
                    "tests-mode gate cites, and brackets or whitespace make that "
                    "id unnameable",
                    _RULE_SMOKE_ID_CHARACTERS,
                )
            )

    smoke_ids = tuple(smoke.id for smoke in contract.smoke)
    issues.extend(
        _duplicate_issues(
            smoke_ids,
            coordinate="smoke",
            noun="smoke id",
            rule_id=_RULE_SMOKE_ID_DUPLICATE,
        )
    )

    unique_entry_points = {
        entry.module: entry
        for entry in contract.entry_points
        if entry_point_counts[entry.module] == 1
    }
    declared_exits_by_entry_point = {
        module: {exit_row.code for exit_row in entry.exits}
        for module, entry in unique_entry_points.items()
    }
    for index, smoke in enumerate(contract.smoke):
        if smoke.entry_point not in unique_entry_points:
            issues.append(
                _issue(
                    f"smoke.{index}.entry_point",
                    f"smoke names unknown or ambiguous entry point {smoke.entry_point!r}",
                    _RULE_SMOKE_ENTRY_POINT_UNKNOWN,
                )
            )

    for index, smoke in enumerate(contract.smoke):
        declared = declared_exits_by_entry_point.get(smoke.entry_point)
        if declared is None:
            continue
        if smoke.expect_exit not in declared:
            issues.append(
                _issue(
                    f"smoke.{index}.expect_exit",
                    f"exit {smoke.expect_exit} is not declared by {smoke.entry_point!r}",
                    _RULE_SMOKE_EXIT_UNDECLARED,
                )
            )

    for smoke_index, smoke in enumerate(contract.smoke):
        for argv_index, token in enumerate(smoke.argv):
            remainder = token.replace("{tmp}", "")
            if "{" in remainder or "}" in remainder:
                issues.append(
                    _issue(
                        f"smoke.{smoke_index}.argv.{argv_index}",
                        f"argv token {token!r} uses a substitution other than literal '{{tmp}}'",
                        _RULE_SMOKE_SUBSTITUTION,
                    )
                )

    return tuple(issues)


def parse_architecture_contract_bytes(data: bytes, *, source: str) -> ArchitectureContract:
    """Return one validated contract, or one closed error surface for any bytes."""

    if not isinstance(data, bytes):
        _raise_one(source, "architecture contract input must be bytes", _RULE_SHAPE)
    if len(data) > MAX_ARCHITECTURE_CONTRACT_BYTES:
        _raise_one(
            source,
            f"architecture contract is {len(data)} bytes, over the "
            f"{MAX_ARCHITECTURE_CONTRACT_BYTES}-byte cap",
            _RULE_DOCUMENT_TOO_LARGE,
        )
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        _raise_one(source, f"architecture contract is not UTF-8: {error}", _RULE_DECODE)

    _preflight_yaml(text, source=source)
    document = _load_yaml(text, source=source)
    try:
        contract = ArchitectureContract.model_validate(document)
    except ValidationError as error:
        issues = _shape_issues(error)
        raise ArchitectureContractError(
            f"architecture contract {source} has an invalid shape", issues
        ) from error
    except (ValueError, RecursionError, TypeError, OverflowError) as error:
        _raise_one(
            source, f"architecture contract shape could not be validated: {error}", _RULE_SHAPE
        )

    issues = _semantic_issues(contract)
    if issues:
        raise ArchitectureContractError(
            f"architecture contract {source} violates semantic rules", issues
        )
    return contract


def _missing_contract(error: ArtifactError) -> bool:
    cause: BaseException | None = error
    while cause is not None:
        if isinstance(cause, FileNotFoundError):
            return str(error).startswith(
                f"artifact {ARCHITECTURE_CONTRACT_FILENAME} could not be inspected"
            )
        cause = cause.__cause__
    return False


def read_architecture_contract_bytes(
    project_root: str | Path, *, root_fd: int | None = None
) -> tuple[bytes, LeafSnapshot]:
    """Read and bind the project-root contract without parsing it.

    The returned snapshot binds the exact bytes already read, so consumers that
    need both validation and an evidence digest never reopen the leaf.
    ``root_fd`` remains caller-owned.
    """
    try:
        if root_fd is None:
            data, snapshot = read_regular_bounded(
                project_root,
                ARCHITECTURE_CONTRACT_FILENAME,
                max_bytes=MAX_ARCHITECTURE_CONTRACT_BYTES,
            )
        else:
            data, snapshot = read_regular_bounded_at(
                root_fd,
                ARCHITECTURE_CONTRACT_FILENAME,
                max_bytes=MAX_ARCHITECTURE_CONTRACT_BYTES,
            )
    except (ArtifactError, OSError) as error:
        issue = _issue(ARCHITECTURE_CONTRACT_FILENAME, str(error), _RULE_READ)
        error_type = ArchitectureContractError
        if isinstance(error, ArtifactError) and _missing_contract(error):
            error_type = ArchitectureContractNotFoundError
        raise error_type(str(error), (issue,)) from error

    return data, snapshot


def load_architecture_contract(
    project_root: str | Path, *, root_fd: int | None = None
) -> ArchitectureContract:
    """Read and validate the project-root contract through no-follow descriptors.

    ``root_fd`` remains caller-owned.  Declared module and artifact paths are
    checked lexically only; this loader never opens them.
    """

    data, _snapshot = read_architecture_contract_bytes(project_root, root_fd=root_fd)

    return parse_architecture_contract_bytes(data, source=ARCHITECTURE_CONTRACT_FILENAME)
