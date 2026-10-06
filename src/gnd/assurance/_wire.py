"""Shared assurance wire/identity primitives."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CorrespondenceDigests:
    scope_digest: str
    semantics_digest: str
    production_roster_digest: str
    proof_digest: str
    toolchain_digest: str



# Historical qualifications are serialized by existing callers.
CorrespondenceDigests.__module__ = 'gnd.assurance.core'
CorrespondenceDigests.__module__ = 'gnd.assurance'

import json
import math
import os
import platform
import sys
from dataclasses import dataclass
from importlib import metadata, resources
from pathlib import Path, PurePosixPath
from typing import Any

from gnd.artifacts import sha256_hex as _sha

MAX_DOCUMENT_BYTES = 10 * 1024 * 1024


MAX_BUNDLE_BYTES = 64 * 1024 * 1024


MAX_FILES = 10_000


MAX_DEPTH = 64


MAX_ROSTER_DIRECTORIES = 10_000


RUNTIME_DEPENDENCIES = (
    "annotated-types",
    "attrs",
    "jsonschema",
    "jsonschema-specifications",
    "pydantic",
    "pydantic-core",
    "referencing",
    "rpds-py",
    "ruamel-yaml",
    "typing-extensions",
    "typing-inspection",
)


def enforce_bundle_limits(total_bytes: int, file_count: int) -> None:
    """One production owner for aggregate evidence size and file-count caps."""
    if total_bytes > MAX_BUNDLE_BYTES:
        raise ValueError("evidence aggregate byte limit")
    if file_count > MAX_FILES:
        raise ValueError("evidence file count limit")


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate evidence key")
        result[key] = value
    return result


def _finite(value: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("nonfinite evidence number")
    return result


def _constant(value: str) -> None:
    raise ValueError("nonfinite evidence constant")


def _integer(value: str) -> int:
    if len(value.lstrip("-")) > 4300:
        raise ValueError("evidence integer digit limit")
    return int(value)


def _json(data: bytes) -> Any:
    if len(data) > MAX_DOCUMENT_BYTES:
        raise ValueError("evidence document limit")
    text = data.decode("utf-8", errors="strict")
    # Limit container depth before the recursive JSON decoder gets the input.
    depth = 0
    quoted = escaped = False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            if depth > MAX_DEPTH:
                raise ValueError("evidence depth limit")
        elif char in "]}":
            depth -= 1
    return json.loads(
        text,
        object_pairs_hook=_pairs,
        parse_float=_finite,
        parse_constant=_constant,
        parse_int=_integer,
    )


def _read(path: Any, limit: int = MAX_DOCUMENT_BYTES) -> bytes:
    if limit < 0:
        raise ValueError("evidence aggregate byte limit")
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError("evidence byte limit")
    return data


def _children(directory: Any):
    """Stream local directory entries so caps apply before a full listing exists."""
    if isinstance(directory, Path):
        with os.scandir(directory) as entries:
            for entry in entries:
                yield Path(entry.path)
    else:
        yield from directory.iterdir()


def _relative(value: str) -> tuple[str, ...]:
    path = PurePosixPath(value)
    if (
        not value
        or path.is_absolute()
        or "\\" in value
        or any(item in {"", ".", ".."} for item in value.split("/"))
    ):
        raise ValueError("unsafe evidence path")
    return path.parts


def _sorted_strings(values: list[str]) -> tuple[str, ...]:
    if values != sorted(set(values)):
        raise ValueError("evidence strings are not unique and sorted")
    return tuple(values)


def dependency_identity(name: str) -> tuple[str, str]:
    """Hash imported distribution files and metadata, not installer outputs.

    RECORD is the installation's generated index. Declared console/gui launchers
    outside site-packages embed their environment's interpreter path; GND's
    semantic consumers import the dependency and never execute those launchers.
    Both are excluded by exact structural rules. Actual module/native-library
    bytes, METADATA and entry_points.txt remain independently hashed.
    """
    distribution = metadata.distribution(name)
    if distribution.files is None:
        raise ValueError("dependency has no installed file inventory")
    rows = []
    total = 0
    launchers = {
        f"../../../bin/{point.name}"
        for point in distribution.entry_points
        if point.group in {"console_scripts", "gui_scripts"}
    }
    for entry in sorted(distribution.files, key=str):
        if str(entry).endswith(".pyc") or "__pycache__" in entry.parts:
            continue
        if str(entry) in launchers or (
            len(entry.parts) == 2
            and entry.parts[0].endswith(".dist-info")
            and entry.parts[1] == "RECORD"
        ):
            continue
        data = _read(distribution.locate_file(entry), MAX_BUNDLE_BYTES - total)
        total += len(data)
        rows.append([str(entry), _sha(data)])
        enforce_bundle_limits(total, len(rows))
    return distribution.version, _sha(json.dumps(rows, separators=(",", ":")).encode())


def production_roster(package=None) -> list[dict[str, Any]]:
    """Inventory installed runtime code/schema inputs, independently of claims.

    Bundle resources have a separate exact file census validated by _load;
    they are data, not imported production modules. Its only un-hashed output
    nodes are the manifest and release anchor themselves.
    """
    package = resources.files("gnd") if package is None else package
    rows = []
    pending = [(package, "src/gnd/")]
    total = 0
    visited_directories = 0
    visited_entries = 0
    while pending:
        directory, prefix = pending.pop()
        visited_directories += 1
        if visited_directories > MAX_ROSTER_DIRECTORIES:
            raise ValueError("production roster directory limit")
        for item in _children(directory):
            visited_entries += 1
            if visited_entries > MAX_FILES:
                raise ValueError("production roster entry limit")
            if isinstance(item, Path) and item.is_symlink():
                raise ValueError("production roster entry is a symlink")
            if item.is_dir() and item.name not in {"__pycache__", "_assurance_evidence"}:
                pending.append((item, prefix + item.name + "/"))
            elif item.is_file() and item.name.endswith((".py", ".schema.json")):
                data = _read(item, min(MAX_DOCUMENT_BYTES, MAX_BUNDLE_BYTES - total))
                total += len(data)
                rows.append({"path": prefix + item.name, "bytes": len(data), "sha256": _sha(data)})
                enforce_bundle_limits(total, len(rows))
    return sorted(rows, key=lambda row: row["path"])


def roster_digest(rows: list[dict[str, Any]]) -> str:
    return _sha(
        json.dumps(rows, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    )


def production_identity() -> str:
    return roster_digest(production_roster())


def runtime_identity(dependencies: list[str]) -> dict[str, Any]:
    return {
        "implementation": sys.implementation.name,
        "version": platform.python_version(),
        "platform": sys.platform,
        "machine": platform.machine(),
        "interpreter_sha256": _sha(_read(Path(sys.executable), MAX_BUNDLE_BYTES)),
        "dependencies": [
            {"name": name, "version": version, "artifact_sha256": digest}
            for name in sorted(dependencies)
            for version, digest in [dependency_identity(name)]
        ],
    }


@dataclass(frozen=True, slots=True, init=False)
class AuthenticatedAssuranceEvidence:
    available: bool
    covered_scope_ids: frozenset[str]
    declared_scope_ids: frozenset[str]
    digests: CorrespondenceDigests | None
    assumptions: tuple[str, ...]
    reason: str | None

    def __init__(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("assurance evidence requires the installed release loader")


def _capability(
    *, manifest: dict | None = None, reason: str | None = None
) -> AuthenticatedAssuranceEvidence:
    value = object.__new__(AuthenticatedAssuranceEvidence)
    rows = manifest["rows"] if manifest is not None else []
    for name, item in {
        "available": manifest is not None,
        "covered_scope_ids": frozenset(
            row["scope_id"] for row in rows if row["status"] == "proved"
        ),
        "declared_scope_ids": frozenset(row["scope_id"] for row in rows),
        "digests": CorrespondenceDigests(
            **{
                key: manifest[key]
                for key in (
                    "scope_digest",
                    "semantics_digest",
                    "production_roster_digest",
                    "proof_digest",
                    "toolchain_digest",
                )
            }
        )
        if manifest is not None
        else None,
        "assumptions": tuple(manifest["assumptions"]) if manifest is not None else (),
        "reason": reason,
    }.items():
        object.__setattr__(value, name, item)
    return value



# Historical qualifications are serialized by existing callers.
enforce_bundle_limits.__module__ = 'gnd.assurance_evidence'
_pairs.__module__ = 'gnd.assurance_evidence'
_finite.__module__ = 'gnd.assurance_evidence'
_constant.__module__ = 'gnd.assurance_evidence'
_integer.__module__ = 'gnd.assurance_evidence'
_json.__module__ = 'gnd.assurance_evidence'
_read.__module__ = 'gnd.assurance_evidence'
_children.__module__ = 'gnd.assurance_evidence'
_relative.__module__ = 'gnd.assurance_evidence'
_sorted_strings.__module__ = 'gnd.assurance_evidence'
dependency_identity.__module__ = 'gnd.assurance_evidence'
production_roster.__module__ = 'gnd.assurance_evidence'
roster_digest.__module__ = 'gnd.assurance_evidence'
production_identity.__module__ = 'gnd.assurance_evidence'
runtime_identity.__module__ = 'gnd.assurance_evidence'
AuthenticatedAssuranceEvidence.__module__ = 'gnd.assurance_evidence'
_capability.__module__ = 'gnd.assurance_evidence'


def _closed(document, fields, label):
    if not isinstance(document, dict) or set(document) != fields:
        raise ValueError(f"proof {label} has an invalid field census")


def _strings(value, label):
    if (
        not isinstance(value, list)
        or any(not isinstance(item, str) for item in value)
        or value != sorted(set(value))
    ):
        raise ValueError(f"proof {label} is not sorted unique strings")
    return set(value)



# Historical qualifications are serialized by existing callers.
_closed.__module__ = 'gnd.assurance_claims'
_strings.__module__ = 'gnd.assurance_claims'

# Public dependency and compatibility spellings; same predecessor objects.
capability = _capability
children = _children
closed = _closed
constant = _constant
finite = _finite
integer = _integer
decode_json = _json
pairs = _pairs
read = _read
relative = _relative
sorted_strings = _sorted_strings
strings = _strings
