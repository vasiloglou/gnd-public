"""Bounded test-only migration coverage validation; no assurance claim."""
from __future__ import annotations

import gzip
import json
import os
import re
import stat
import zlib
from pathlib import Path, PurePosixPath

ROW_KEYS = frozenset({"source_node", "source_sha256", "disposition", "claim", "target_nodes", "changed_boundary", "archive_limit", "selection"})
PACKET_KEYS = frozenset({"originals", "collected", "rows", "expected_surfaces", "surfaces", "private_dependencies", "source_delta_accounted", "acceptance_passed", "handoff_requested"})
DISPOSITIONS = frozenset({"current", "successor", "consolidated", "historical", "fixture-only", "retained-private"})
SELECTIONS = frozenset({"default", "distribution", "optional-unverified", "unselected"})
HEX = re.compile(r"[0-9a-f]{64}\Z")


class MigrationRefusal(ValueError):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise MigrationRefusal(reason)


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _node(value: object) -> bool:
    if not _text(value):
        return False
    path = value.split("::", 1)[0]
    parts = PurePosixPath(path)
    return not parts.is_absolute() and ".." not in parts.parts and "\\" not in path


def _strings(value: object, *, nodes: bool = False) -> bool:
    return isinstance(value, list) and len(value) <= 50_000 and all(
        _node(item) if nodes else _text(item) for item in value
    ) and len(value) == len(set(value))


def _pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        _require(key not in result, "duplicate-key")
        result[key] = value
    return result


def _constant(value: str) -> None:
    raise MigrationRefusal("non-json-constant")


def strict_json(text: str) -> object:
    try:
        return json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)
    except (ValueError, RecursionError) as error:
        if isinstance(error, MigrationRefusal):
            raise
        raise MigrationRefusal("invalid-json") from error


def load_case_map(path: Path, *, max_bytes: int = 8_388_608) -> tuple[dict, ...]:
    _require(type(max_bytes) is int and 0 < max_bytes <= 8_388_608, "invalid-cap")
    try:
        _require(not path.is_symlink(), "symlink-map")
        _require(".." not in path.parts, "traversal-map")
        _require(not any(parent.is_symlink() for parent in path.parents), "symlink-map")
        descriptor = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
        with os.fdopen(descriptor, "rb") as raw:
            info = os.fstat(raw.fileno())
            _require(stat.S_ISREG(info.st_mode), "nonregular-map")
            _require(info.st_size <= max_bytes, "oversize-map")
            magic = raw.read(2)
            raw.seek(0)
            if magic == b"\x1f\x8b":
                with gzip.GzipFile(fileobj=raw) as stream:
                    data = stream.read(max_bytes + 1)
            else:
                data = raw.read(max_bytes + 1)
        _require(len(data) <= max_bytes, "oversize-map")
        lines = data.decode("utf-8").splitlines()
        _require(len(lines) <= 10_000, "too-many-rows")
        rows = tuple(strict_json(line) for line in lines)
        _require(all(isinstance(row, dict) for row in rows), "invalid-row-shape")
        return rows
    except (OSError, EOFError, UnicodeError, RecursionError, ValueError, zlib.error) as error:
        if isinstance(error, MigrationRefusal):
            raise
        raise MigrationRefusal("unreadable-map") from error


def validate_case_map(rows: tuple[dict, ...], *, originals: dict[str, str], collected: set[str], retained_private: dict[str, str] | None = None) -> None:
    _require(isinstance(originals, dict) and len(originals) <= 10_000, "invalid-originals")
    _require(all(_node(k) and isinstance(v, str) and HEX.fullmatch(v) for k, v in originals.items()), "invalid-originals")
    _require(isinstance(collected, set) and len(collected) <= 50_000 and all(_node(x) for x in collected), "invalid-collection")
    _require(isinstance(rows, tuple) and len(rows) <= 10_000, "invalid-rows")
    private = {} if retained_private is None else retained_private
    _require(isinstance(private, dict) and len(private) <= 10_000, "invalid-private-policy")
    _require(all(_node(k) and isinstance(v, str) and HEX.fullmatch(v) for k, v in private.items()), "invalid-private-policy")
    seen = set()
    for row in rows:
        _require(isinstance(row, dict) and set(row) == ROW_KEYS, "invalid-row-shape")
        source = row["source_node"]
        _require(_node(source), "invalid-source-node")
        _require(source not in seen, "duplicate-original")
        seen.add(source)
        _require(source in originals, "unknown-original")
        _require(row["source_sha256"] == originals[source], "source-digest-mismatch")
        kind = row["disposition"]
        _require(isinstance(kind, str) and kind in DISPOSITIONS, "unknown-disposition")
        selection = row["selection"]
        _require(isinstance(selection, str) and selection in SELECTIONS, "unknown-selection")
        _require(_text(row["claim"]) and _text(row["changed_boundary"]), "missing-claim")
        targets = row["target_nodes"]
        _require(_strings(targets, nodes=True), "invalid-targets")
        if kind == "retained-private":
            _require(source in private and private[source] == originals[source], "unapproved-private-original")
            _require(selection == "unselected" and not targets, "private-selected")
            _require(_text(row["archive_limit"]), "missing-private-limit")
            _require(row["changed_boundary"] != "none", "missing-private-boundary")
        elif kind == "historical":
            _require(_text(row["archive_limit"]), "missing-archive-limit")
            _require(selection == "unselected", "historical-selected")
        else:
            _require(row["archive_limit"] is None, "unexpected-archive-limit")
            if kind == "fixture-only":
                _require(bool(targets), "missing-fixture-consumer")
            else:
                _require(bool(targets), "missing-target")
                _require(selection != "unselected", "current-unselected")
            if kind == "successor":
                _require(row["changed_boundary"] != "none", "missing-successor-boundary")
            if kind == "consolidated":
                _require(row["changed_boundary"] != "none", "unsupported-consolidation")
        _require(set(targets) <= collected, "missing-target")
    _require(seen == set(originals), "missing-original")


def validate_progress_counts(progress: dict, rows: tuple[dict, ...], *, original_count: int) -> None:
    """Private retention satisfies accounting only, never public coverage."""
    expected = {
        "original_definitions": original_count,
        "reviewed_dispositions": len(rows),
        "unresolved_definitions": original_count - len(rows),
        "current_or_successor_definitions": sum(row["disposition"] in {"current", "successor", "consolidated"} for row in rows),
        "historical_definitions": sum(row["disposition"] == "historical" for row in rows),
        "retained_private_definitions": sum(row["disposition"] == "retained-private" for row in rows),
        "fixture_only_definitions": sum(row["disposition"] == "fixture-only" for row in rows),
    }
    _require(isinstance(progress, dict), "invalid-progress")
    _require(all(type(progress.get(key)) is int and progress[key] == value for key, value in expected.items()), "incorrect-coverage-counts")


def validate_surface_map(document: dict, *, surfaces: set[str], collected: set[str]) -> None:
    _require(isinstance(document, dict) and set(document) == {"surfaces"}, "invalid-surface-shape")
    _require(isinstance(collected, set) and len(collected) <= 50_000 and all(_node(x) for x in collected), "invalid-collection")
    rows = document["surfaces"]
    _require(isinstance(rows, list) and len(rows) <= 10_000, "invalid-surface-shape")
    _require(isinstance(surfaces, set) and all(_text(x) for x in surfaces), "invalid-surfaces")
    seen = set()
    for row in rows:
        _require(isinstance(row, dict) and set(row) == {"id", "target_nodes", "execution", "limitations"}, "invalid-surface-shape")
        identity = row["id"]
        _require(_text(identity), "invalid-surface-id")
        _require(identity not in seen, "duplicate-surface")
        seen.add(identity)
        _require(_strings(row["target_nodes"], nodes=True) and bool(row["target_nodes"]), "invalid-surface-targets")
        _require(set(row["target_nodes"]) <= collected, "missing-target")
        _require(_strings(row["limitations"]), "invalid-limitations")
        _require(isinstance(row["execution"], str) and row["execution"] in {"current", "optional-unverified"}, "invalid-execution")
        if row["execution"] == "optional-unverified":
            _require(bool(row["limitations"]), "unsupported-optional-claim")
    _require(seen == surfaces, "missing-surface")


def validate_acceptance_packet(packet: dict, *, retained_private: dict[str, str] | None = None) -> None:
    _require(isinstance(packet, dict) and set(packet) == PACKET_KEYS, "invalid-packet-shape")
    _require(isinstance(packet["rows"], list), "invalid-rows")
    _require(_strings(packet["collected"], nodes=True), "invalid-collection")
    _require(_strings(packet["expected_surfaces"]), "invalid-surfaces")
    _require(_strings(packet["private_dependencies"]), "invalid-private-dependencies")
    for name in ("source_delta_accounted", "acceptance_passed", "handoff_requested"):
        _require(type(packet[name]) is bool, "invalid-handoff-shape")
    collected = set(packet["collected"])
    validate_case_map(tuple(packet["rows"]), originals=packet["originals"], collected=collected, retained_private=retained_private)
    _require(not packet["private_dependencies"], "private-dependency")
    validate_surface_map({"surfaces": packet["surfaces"]}, surfaces=set(packet["expected_surfaces"]), collected=collected)
    if packet["handoff_requested"]:
        _require(packet["source_delta_accounted"], "unaccounted-source-delta")
        _require(packet["acceptance_passed"], "failed-acceptance")
