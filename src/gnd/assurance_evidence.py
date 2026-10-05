"""Read release-bound assurance evidence without repository or proof tools.

The installed package and release anchor are trusted release inputs. Hashes
check currency relative to that anchor; they do not authenticate a publisher.
Any unavailable or malformed evidence withholds assurance, not the verdict.
"""

from __future__ import annotations

import json
import math
import os
import platform
import stat
import sys
from dataclasses import dataclass
from importlib import metadata, resources
from pathlib import Path, PurePosixPath
from typing import Any

import jsonschema

from gnd.artifacts import sha256_hex as _sha
from gnd.assurance import CorrespondenceDigests
from gnd.semantic_registry import REGISTRY

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


def _load(package: Any) -> AuthenticatedAssuranceEvidence:
    bundle = package.joinpath("_assurance_evidence")
    anchor = _json(_read(bundle.joinpath("anchor.json")))
    jsonschema.validate(anchor, _json(_read(package.joinpath("assurance-anchor.schema.json"))))
    raw = _read(bundle.joinpath("manifest.json"))
    if _sha(raw) != anchor["manifest_sha256"]:
        raise ValueError("stale release manifest")
    manifest = _json(raw)
    jsonschema.validate(manifest, _json(_read(package.joinpath("assurance-evidence.schema.json"))))
    enforce_bundle_limits(len(raw), max(len(manifest["files"]), len(manifest["rows"])))
    names = [entry["name"] for entry in manifest["runtime_domain"]["dependencies"]]
    if _sorted_strings(names) != RUNTIME_DEPENDENCIES:
        raise ValueError("incomplete runtime dependency roster")
    if manifest["runtime_domain"] != runtime_identity(names):
        raise ValueError("stale runtime identity")
    _sorted_strings(manifest["assumptions"])
    declared = [row["scope_id"] for row in manifest["rows"]]
    _sorted_strings(declared)
    if set(declared) != {row.scope_id for row in REGISTRY}:
        raise ValueError("evidence registry mismatch")
    excluded = _sorted_strings(manifest["excluded_policy_scope_ids"])
    expected_excluded = tuple(
        sorted(
            row.scope_id
            for row in REGISTRY
            if (
                row.family == "oracle-verdict"
                or (
                    row.surface == "experiment-feedback"
                    and row.family in {"attempt", "case", "contract"}
                )
            )
        )
    )
    if excluded != expected_excluded:
        raise ValueError("evidence policy exclusion mismatch")
    actual_roster = production_roster(package)
    supplied_roster = sorted(
        (row["address"] for row in manifest["files"] if row["role"] in {"source", "schema"}),
        key=lambda row: row["path"],
    )
    if (
        actual_roster != supplied_roster
        or roster_digest(actual_roster) != manifest["production_roster_digest"]
    ):
        raise ValueError("stale or incomplete production roster")
    # Publication outputs are an explicit finite census, not a path exemption.
    expected_bundle = {"anchor.json", "manifest.json"}
    for row in manifest["files"]:
        parts = _relative(row["address"]["path"])
        if parts[:3] == ("src", "gnd", "_assurance_evidence"):
            raise ValueError("bundle input must use its canonical bundle-relative address")
        if parts[:2] != ("src", "gnd"):
            expected_bundle.add(row["address"]["path"])
    observed_bundle = set()
    expected_directories = {
        "/".join(parts[:index])
        for name in expected_bundle
        for parts in [name.split("/")]
        for index in range(1, len(parts))
    }
    pending = [(bundle, "")]
    while pending:
        directory, prefix = pending.pop()
        if isinstance(directory, Path) and directory.is_symlink():
            raise ValueError("bundle directory is a symlink")
        for item in _children(directory):
            if isinstance(item, Path) and item.is_symlink():
                raise ValueError("bundle entry is a symlink")
            name = prefix + item.name
            if item.is_dir():
                if name not in expected_directories:
                    raise ValueError("unlisted bundle directory")
                pending.append((item, name + "/"))
            elif item.is_file():
                if name not in expected_bundle:
                    raise ValueError("unlisted bundle file")
                observed_bundle.add(name)
            else:
                raise ValueError("bundle entry is not a regular file or directory")
    if observed_bundle != expected_bundle:
        raise ValueError("bundle file census differs from the publication manifest")
    addresses = {}
    proof_documents = {}
    total = len(raw)
    for row in manifest["files"]:
        address = row["address"]
        path = address["path"]
        parts = _relative(path)
        if path in addresses or path in {
            "src/gnd/_assurance_evidence/manifest.json",
            "src/gnd/_assurance_evidence/anchor.json",
        }:
            raise ValueError("duplicate or circular evidence input")
        target = (
            package.joinpath(*parts[2:]) if parts[:2] == ("src", "gnd") else bundle.joinpath(*parts)
        )
        if isinstance(target, Path):
            anchor = package if parts[:2] == ("src", "gnd") else bundle
            relative_parts = parts[2:] if parts[:2] == ("src", "gnd") else parts
            cursor = anchor
            for part in relative_parts:
                cursor = cursor.joinpath(part)
                if cursor.is_symlink():
                    raise ValueError("evidence input is a symlink")
        data = _read(target, min(MAX_DOCUMENT_BYTES, MAX_BUNDLE_BYTES - total))
        total += len(data)
        enforce_bundle_limits(total, len(addresses) + 1)
        if len(data) != address["bytes"] or _sha(data) != address["sha256"]:
            raise ValueError("stale evidence input")
        addresses[path] = address
        if row["role"] not in {"source", "schema"}:
            proof_documents[path] = data
    for role, field in (
        ("scope", "scope_digest"),
        ("semantics", "semantics_digest"),
        ("toolchain", "toolchain_digest"),
    ):
        matching = [row["address"] for row in manifest["files"] if row["role"] == role]
        if len(matching) != 1 or matching[0]["sha256"] != manifest[field]:
            raise ValueError("unbound evidence role identity")
    proof_results = sorted(
        (row["address"] for row in manifest["files"] if row["role"] == "proof-result"),
        key=lambda row: row["path"],
    )
    if not proof_results or roster_digest(proof_results) != manifest["proof_digest"]:
        raise ValueError("unbound proof result identity")
    result_digests = {item["sha256"] for item in proof_results}
    input_digests = {
        row["address"]["sha256"] for row in manifest["files"] if row["role"] == "proof-source"
    }
    owners = {row.scope_id: row.production_owner for row in REGISTRY}
    for row in manifest["rows"]:
        _sorted_strings(row["theorems"])
        _sorted_strings(row["production_owners"])
        _sorted_strings(row["assumptions"])
        if not set(row["assumptions"]) <= set(manifest["assumptions"]):
            raise ValueError("undeclared proof assumption")
        if row["normative"] != addresses.get(row["normative"]["path"]):
            raise ValueError("unbound normative input")
        if row["scope_id"] in excluded and row["status"] != "excluded":
            raise ValueError("excluded policy row claims evidence")
        if row["status"] == "proved" and (
            row["result_digest"] not in result_digests
            or row["proof_inputs_digest"] not in input_digests
            or owners[row["scope_id"]] not in row["production_owners"]
        ):
            raise ValueError("proved row is not bound to its owner and proof artifacts")
        if row["status"] != "proved" and (
            row["provider"] is not None
            or row["result_digest"] is not None
            or row["proof_inputs_digest"] is not None
            or row["theorems"]
        ):
            raise ValueError("unproved row carries a proof claim")
        if row["status"] == "proved" and (
            not row["theorems"]
            or not row["production_owners"]
            or row["provider"] is None
            or row["proof_inputs_digest"] is None
            or row["result_digest"] is None
        ):
            raise ValueError("incomplete proved row")
    from gnd.assurance_claims import validate_claim_graph

    validate_claim_graph(manifest, addresses, proof_documents)
    return _capability(manifest=manifest)


@dataclass(frozen=True, slots=True)
class _CacheFingerprint:
    package_root: str
    anchor_sha256: str
    manifest_sha256: str
    production_roster_digest: str
    runtime_identity: dict[str, Any]
    bundle_entries: tuple[tuple[str, str], ...]
    addressed_files: tuple[tuple[str, int, int, int, int], ...]


@dataclass(frozen=True, slots=True)
class _CacheEntry:
    fingerprint: _CacheFingerprint
    capability: AuthenticatedAssuranceEvidence


_assurance_cache: dict[str, _CacheEntry] = {}
_FINGERPRINT_ERRORS = (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError, RecursionError)


def _stat_identity(path: Path) -> tuple[int, int, int, int]:
    found = path.lstat()
    if not stat.S_ISREG(found.st_mode):
        raise ValueError("evidence input is not a regular file")
    return found.st_size, found.st_mtime_ns, found.st_ctime_ns, found.st_ino


def _bundle_census(bundle: Path) -> tuple[tuple[str, str], ...]:
    """Bounded lstat-only view of every bundle entry, including directories."""
    if not stat.S_ISDIR(bundle.lstat().st_mode):
        raise ValueError("bundle root is not a directory")
    pending = [(bundle, "", 0)]
    rows: list[tuple[str, str]] = []
    total_bytes = 0
    while pending:
        directory, prefix, depth = pending.pop()
        if depth > MAX_DEPTH:
            raise ValueError("evidence depth limit")
        for item in _children(directory):
            found = item.lstat()
            name = prefix + item.name
            if stat.S_ISDIR(found.st_mode):
                kind = "directory"
                pending.append((item, name + "/", depth + 1))
            elif stat.S_ISREG(found.st_mode):
                kind = "file"
                total_bytes += found.st_size
            else:
                raise ValueError("bundle entry is not a regular file or directory")
            rows.append((name, kind))
            enforce_bundle_limits(total_bytes, len(rows))
    return tuple(sorted(rows))


def _fingerprint(package: Path) -> _CacheFingerprint:
    bundle = package / "_assurance_evidence"
    anchor_raw = _read(bundle / "anchor.json")
    manifest_raw = _read(bundle / "manifest.json")
    manifest = _json(manifest_raw)
    names = [row["name"] for row in manifest["runtime_domain"]["dependencies"]]
    addressed: list[tuple[str, int, int, int, int]] = []
    seen: set[str] = set()
    for row in manifest["files"]:
        address = row["address"]["path"]
        parts = _relative(address)
        if address in seen:
            raise ValueError("duplicate evidence input")
        seen.add(address)
        source_address = parts[:2] == ("src", "gnd")
        base = package if source_address else bundle
        relative = parts[2:] if source_address else parts
        target = base
        for part in relative:
            target = target / part
            if target.is_symlink():
                raise ValueError("evidence input is a symlink")
        addressed.append((address, *_stat_identity(target)))
        enforce_bundle_limits(0, len(addressed))
    return _CacheFingerprint(
        package_root=str(package.resolve()),
        anchor_sha256=_sha(anchor_raw),
        manifest_sha256=_sha(manifest_raw),
        production_roster_digest=roster_digest(production_roster(package)),
        runtime_identity=runtime_identity(names),
        bundle_entries=_bundle_census(bundle),
        addressed_files=tuple(sorted(addressed)),
    )


def _try_fingerprint(package: Path) -> _CacheFingerprint | None:
    try:
        return _fingerprint(package)
    except _FINGERPRINT_ERRORS:
        return None


def _preflight_read_inputs(package: Any) -> None:
    """Refuse special entries that the authenticating loader reads before census."""
    bundle = package.joinpath("_assurance_evidence")
    if not bundle.is_dir() or (isinstance(bundle, Path) and not stat.S_ISDIR(bundle.lstat().st_mode)):
        raise ValueError("bundle root is not a directory")
    for path in (
        bundle.joinpath("anchor.json"),
        bundle.joinpath("manifest.json"),
        package.joinpath("assurance-anchor.schema.json"),
        package.joinpath("assurance-evidence.schema.json"),
    ):
        if not path.is_file():
            raise ValueError("early evidence input is not a regular file")
        if isinstance(path, Path):
            _stat_identity(path)


def _cached_load(package: Path) -> AuthenticatedAssuranceEvidence:
    root = str(package.resolve())
    entry = _assurance_cache.get(root)
    if entry is not None:
        current = _try_fingerprint(package)
        if current == entry.fingerprint:
            return entry.capability
        _assurance_cache.pop(root, None)

    before = _try_fingerprint(package)
    value = _load(package)
    if before is None:
        return value  # Authentication succeeded, but no pre-snapshot can authorize a cache entry.
    after = _try_fingerprint(package)
    if before != after:
        retry_before = _try_fingerprint(package)
        value = _load(package)
        retry_after = _try_fingerprint(package)
        if retry_before is None or retry_before != retry_after:
            return _capability(reason="unavailable-or-invalid-evidence")
        after = retry_after
    if after is not None:
        _assurance_cache[root] = _CacheEntry(after, value)
    return value


def load_assurance_evidence() -> AuthenticatedAssuranceEvidence:
    """Load only this installed package's release evidence; fail closed."""
    try:
        package = resources.files("gnd")
        _preflight_read_inputs(package)
        return _cached_load(package) if isinstance(package, Path) else _load(package)
    except (
        OSError,
        ValueError,
        TypeError,
        KeyError,
        RecursionError,
        jsonschema.ValidationError,
        jsonschema.SchemaError,
        metadata.PackageNotFoundError,
        RuntimeError,
    ):
        return _capability(reason="unavailable-or-invalid-evidence")
