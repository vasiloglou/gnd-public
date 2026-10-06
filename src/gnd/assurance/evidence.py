"""Read release-bound assurance evidence without repository or proof tools.

The installed package and release anchor are trusted release inputs. Hashes
check currency relative to that anchor; they do not authenticate a publisher.
Any unavailable or malformed evidence withholds assurance, not the verdict.
"""

from __future__ import annotations

import stat
from dataclasses import dataclass
from importlib import metadata, resources
from pathlib import Path
from typing import Any

import jsonschema

from gnd.artifacts import sha256_hex as _sha
from gnd.assurance._wire import (
    MAX_BUNDLE_BYTES as MAX_BUNDLE_BYTES,  # noqa: PLC0414 -- compatibility surface
)
from gnd.assurance._wire import (
    MAX_DEPTH as MAX_DEPTH,  # noqa: PLC0414 -- compatibility surface
)
from gnd.assurance._wire import (
    MAX_DOCUMENT_BYTES as MAX_DOCUMENT_BYTES,  # noqa: PLC0414 -- compatibility surface
)
from gnd.assurance._wire import (
    MAX_FILES as MAX_FILES,  # noqa: PLC0414 -- compatibility surface
)
from gnd.assurance._wire import (
    MAX_ROSTER_DIRECTORIES as MAX_ROSTER_DIRECTORIES,  # noqa: PLC0414 -- compatibility surface
)
from gnd.assurance._wire import (
    RUNTIME_DEPENDENCIES as RUNTIME_DEPENDENCIES,  # noqa: PLC0414 -- compatibility surface
)
from gnd.assurance._wire import (
    AuthenticatedAssuranceEvidence as AuthenticatedAssuranceEvidence,  # noqa: PLC0414 -- compatibility surface
)
from gnd.assurance._wire import (
    capability as _capability,
)
from gnd.assurance._wire import (
    children as _children,
)
from gnd.assurance._wire import (
    decode_json as _json,
)
from gnd.assurance._wire import (
    dependency_identity as dependency_identity,  # noqa: PLC0414 -- compatibility surface
)
from gnd.assurance._wire import (
    enforce_bundle_limits as enforce_bundle_limits,  # noqa: PLC0414 -- compatibility surface
)
from gnd.assurance._wire import (
    production_identity as production_identity,  # noqa: PLC0414 -- compatibility surface
)
from gnd.assurance._wire import (
    production_roster as production_roster,  # noqa: PLC0414 -- compatibility surface
)
from gnd.assurance._wire import (
    read as _read,
)
from gnd.assurance._wire import (
    relative as _relative,
)
from gnd.assurance._wire import (
    roster_digest as roster_digest,  # noqa: PLC0414 -- compatibility surface
)
from gnd.assurance._wire import (
    runtime_identity as runtime_identity,  # noqa: PLC0414 -- compatibility surface
)
from gnd.assurance._wire import (
    sorted_strings as _sorted_strings,
)
from gnd.semantic_registry import REGISTRY


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
    from gnd.assurance.claims import validate_claim_graph

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


_load.__module__ = 'gnd.assurance_evidence'
_CacheFingerprint.__module__ = 'gnd.assurance_evidence'
_CacheEntry.__module__ = 'gnd.assurance_evidence'
_stat_identity.__module__ = 'gnd.assurance_evidence'
_bundle_census.__module__ = 'gnd.assurance_evidence'
_fingerprint.__module__ = 'gnd.assurance_evidence'
_try_fingerprint.__module__ = 'gnd.assurance_evidence'
_preflight_read_inputs.__module__ = 'gnd.assurance_evidence'
_cached_load.__module__ = 'gnd.assurance_evidence'
load_assurance_evidence.__module__ = 'gnd.assurance_evidence'

# Public dependency and compatibility spellings; same predecessor objects.
CacheEntry = _CacheEntry
CacheFingerprint = _CacheFingerprint
FINGERPRINT_ERRORS = _FINGERPRINT_ERRORS
assurance_cache = _assurance_cache
bundle_census = _bundle_census
cached_load = _cached_load
fingerprint = _fingerprint
load = _load
preflight_read_inputs = _preflight_read_inputs
stat_identity = _stat_identity
try_fingerprint = _try_fingerprint

sha = _sha
