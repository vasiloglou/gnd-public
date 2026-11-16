"""Bind a release to an independently selected, bounded dependency policy."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from gnd.artifacts import ArtifactError, canonical_json_bytes, publish_directory_once, sha256_hex

from .depth import ExampleError, _decode, _read

POLICY = Path(__file__).with_name("revision_fixture") / "release-policy.json"
POLICY_SHA256 = "af44dfee16ca94f20c560c5e82bb00e59bb86f53c53c7219b30fb6da3ad8bc65"
MAX_ARTIFACTS = 96
MAX_DEPENDENCIES = 32
SNAPSHOTS = ("before", "after")
MARKER = "manifest.json"
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_PATH = re.compile(r"(?:[a-z0-9_-]+/){0,4}[a-z0-9_-][a-z0-9_.-]*\Z")


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ExampleError(reason)


def _digest(value) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def _path(value) -> bool:
    return isinstance(value, str) and len(value) <= 120 and _PATH.fullmatch(value) is not None


@dataclass(frozen=True)
class Policy:
    sha256: str
    entries: dict[str, dict[str, tuple[str, ...]]]

    @classmethod
    def load(cls, path: Path = POLICY, pin: str = POLICY_SHA256) -> Policy:
        require(_digest(pin), "invalid release policy digest")
        raw = _read(path.parent, path.name)
        require(sha256_hex(raw) == pin, "release policy digest differs")
        policy = _decode(raw)
        snapshots = policy.get("snapshots")
        require(set(policy) == {"format", "snapshots"} and policy["format"] == "literature-release-policy/1"
                and isinstance(snapshots, dict) and set(snapshots) == set(SNAPSHOTS),
                "invalid release policy")
        entries = {}
        for snapshot in SNAPSHOTS:
            rows = snapshots[snapshot]
            require(isinstance(rows, list) and 0 < len(rows) <= MAX_ARTIFACTS, "invalid policy roster")
            indexed = {}
            preceding = {f"before/{name}" for name in entries.get("before", {})}
            for row in rows:
                require(isinstance(row, dict) and set(row) == {"path", "kind", "requires"},
                        "invalid release policy row")
                name, kind, parents = row["path"], row["kind"], row["requires"]
                require(_path(name) and name not in indexed and name != MARKER and not name.startswith("before/")
                        and _path(kind)
                        and isinstance(parents, list) and len(parents) <= MAX_DEPENDENCIES
                        and all(_path(parent) and (parent in indexed or parent in preceding) for parent in parents)
                        and len(set(parents)) == len(parents), "invalid release policy dependency or path")
                indexed[name] = tuple(parents)
            entries[snapshot] = indexed
        return cls(pin, entries)

    def capture(self, root: Path, snapshot: str) -> dict[str, bytes]:
        files = {path: _read(root, path) for path in self.entries[snapshot]}
        files[MARKER] = canonical_json_bytes({
            "format": "literature-release/1",
            "policy_sha256": self.sha256,
            "snapshot": snapshot,
            "artifacts": [{"path": name, "sha256": sha256_hex(raw)} for name, raw in files.items()],
            "prior_artifacts": {name: sha256_hex(_read(root.parent, name))
                                for name in sorted(self._primary_dependencies(snapshot))},
        })
        return files

    def _primary_dependencies(self, snapshot: str) -> set[str]:
        return {parent for parents in self.entries[snapshot].values() for parent in parents
                if parent.startswith("before/")}

    def affected(self, snapshot: str, changed: set[str]) -> set[str]:
        stale = set(changed)
        for name, parents in self.entries[snapshot].items():
            if name in changed or stale.intersection(parents):
                stale.add(name)
        return stale.intersection(self.entries[snapshot])

    def inspect(self, root: Path, snapshot: str) -> tuple[dict, dict[str, bytes]]:
        require(snapshot in SNAPSHOTS, "select the before or after release snapshot")
        raw = _read(root, MARKER)
        manifest = _decode(raw)
        rows = manifest.get("artifacts")
        require(set(manifest) == {"format", "policy_sha256", "snapshot", "artifacts", "prior_artifacts"}
                and manifest["format"] == "literature-release/1"
                and manifest["policy_sha256"] == self.sha256 and manifest["snapshot"] == snapshot,
                "invalid release manifest identity")
        paths = self.entries[snapshot]
        require(isinstance(rows, list) and len(rows) == len(paths), "release artifact roster differs")
        pins = {}
        for row in rows:
            require(isinstance(row, dict) and set(row) == {"path", "sha256"}, "invalid release artifact roster")
            name, digest = row["path"], row["sha256"]
            require(_path(name) and name in paths and name not in pins and _digest(digest),
                    "invalid release artifact roster")
            pins[name] = digest
        prior = manifest["prior_artifacts"]
        require(isinstance(prior, dict) and prior.keys() == self._primary_dependencies(snapshot)
                and all(_digest(digest) for digest in prior.values()), "invalid prior artifact roster")
        upstream_stale = set()
        if prior:
            try:
                previous, prior_files = self.inspect(root.parent / "before", "before")
            except (ArtifactError, ExampleError, OSError):
                upstream_stale.update(prior)
            else:
                prior_current = set(previous["current"])
                for name, digest in prior.items():
                    relative = name.removeprefix("before/")
                    if relative not in prior_current or sha256_hex(prior_files[relative]) != digest:
                        upstream_stale.add(name)
        files, changed = {}, set()
        for name in paths:
            try:
                actual = _read(root, name)
            except (ArtifactError, OSError):
                changed.add(name)
            else:
                if sha256_hex(actual) == pins[name]:
                    files[name] = actual
                else:
                    changed.add(name)
        stale = self.affected(snapshot, changed | upstream_stale)
        state = {"snapshot": snapshot, "status": "stale" if stale else "current",
                 "changed": sorted(changed), "prior_stale": sorted(upstream_stale),
                 "stale": sorted(stale), "current": sorted(paths.keys() - stale)}
        files[MARKER] = raw
        return state, files


def status(root: Path, *, policy: Path = POLICY, policy_sha256: str = POLICY_SHA256) -> dict:
    """Check a candidate against the consumer's exact policy and propagate staleness."""
    try:
        state, _ = Policy.load(policy, policy_sha256).inspect(root, root.name)
    except (ArtifactError, OSError) as error:
        raise ExampleError(str(error)) from error
    return state


def publish(root: Path, files: dict[str, bytes]) -> None:
    publish_directory_once(root.parent, root.name, files, manifest_name="release.json")
