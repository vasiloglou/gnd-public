"""Bounded data-only candidate proposals; pure application returns full bytes."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from gnd import json_input
from gnd.artifacts import ArtifactError, canonical_json_bytes, is_sha256_hex
from gnd.exp.session_contract import DataDrivenContract
from gnd.extract.manifest import manifest_path_issue

MAX_PATCH_BYTES = 10 * 1024 * 1024


class PatchRefusal(ValueError):
    def __init__(self, reason: str, message: str):
        self.reason = reason
        super().__init__(message[:256])


def _refuse(reason, message):
    raise PatchRefusal(reason, message)


def bounded_json(raw: bytes, *, max_bytes=MAX_PATCH_BYTES):
    try:
        return json_input.bounded_json(raw, max_bytes=max_bytes)
    except json_input.JsonInputRefusal as error:
        raise PatchRefusal(error.reason, str(error)) from error


def read_patch_document(raw: bytes) -> dict:
    doc = bounded_json(raw)
    _shape(doc)
    return doc


def validate_json_value(doc):
    try:
        return json_input.validate_json_value(doc)
    except json_input.JsonInputRefusal as error:
        raise PatchRefusal(error.reason, str(error)) from error


def _shape(doc):
    validate_json_value(doc)
    if not isinstance(doc, dict) or set(doc) != {
        "schema_version",
        "base_candidate_sha256",
        "operations",
    }:
        _refuse("shape", "closed proposal object required")
    if type(doc["schema_version"]) is not int or doc["schema_version"] != 1:
        _refuse("shape", "proposal version must be 1")
    digest = doc["base_candidate_sha256"]
    if digest is not None and not is_sha256_hex(digest):
        _refuse("shape", "invalid base digest")
    ops = doc["operations"]
    if not isinstance(ops, list):
        _refuse("shape", "operations must be an array")
    if len(ops) > 1024:
        _refuse("limit", "operation count exceeds cap")
    for op in ops:
        if not isinstance(op, dict):
            _refuse("shape", "operation must be an object")
        kind = op.get("op")
        fields = (
            {"op", "artifact", "value"}
            if kind == "replace-artifact"
            else {"op", "artifact", "collection", "key"}
            | ({"value"} if kind == "upsert" else set())
        )
        if kind not in {"replace-artifact", "upsert", "delete"} or set(op) != fields:
            _refuse("shape", "invalid closed operation")
        if not isinstance(op["artifact"], str):
            _refuse("shape", "artifact must be a path")
        if kind != "replace-artifact" and (
            not isinstance(op["collection"], list) or not isinstance(op["key"], list)
        ):
            _refuse("shape", "collection and key must be arrays")
        if kind != "replace-artifact" and any(
            not isinstance(segment, str) for segment in op["collection"]
        ):
            _refuse("shape", "collection selector segments must be strings")


def _key(values):
    answer = []
    for value in values:
        if type(value) is bool:
            answer.append(("boolean", value))
        elif isinstance(value, str):
            if len(value.encode()) > 4096:
                _refuse("limit", "key scalar exceeds cap")
            answer.append(("string", value))
        elif type(value) in (int, float, Decimal) and Decimal(str(value)).is_finite():
            token = Decimal(str(value))
            answer.append(("number", token))
        else:
            _refuse("keys", "key must be a non-null finite scalar")
    return tuple(answer)


def proposal_mode(doc, contract):
    return (
        "complete"
        if all(op["op"] == "replace-artifact" for op in doc["operations"])
        and {op["artifact"] for op in doc["operations"]}
        == {a.path for a in contract.candidate_edits.artifacts}
        else "patch"
    )


def apply_candidate_patch(
    doc,
    *,
    contract: DataDrivenContract,
    base_root: Path | None,
    base_sha256: str | None,
    allow_initial_seed: bool = False,
) -> dict[str, bytes]:
    _shape(doc)
    doc = bounded_json(canonical_json_bytes(doc, exact_numbers=True))
    seed = allow_initial_seed and doc["base_candidate_sha256"] is None
    if allow_initial_seed and not seed:
        _refuse("stale-base", "first proposal must be a complete null-base seed")
    if not seed and (
        doc["base_candidate_sha256"] is None or doc["base_candidate_sha256"] != base_sha256
    ):
        _refuse("stale-base", "proposal does not name the current base")
    edits = contract.candidate_edits
    if edits is None:
        _refuse("protected", "contract does not permit proposals")
    declared = {a.path: a for a in edits.artifacts}
    for op in doc["operations"]:
        path = op["artifact"]
        if len(path.encode()) > 4096 or manifest_path_issue("artifact", path, "patch"):
            _refuse("path", "unsafe artifact path")
        if path not in declared:
            _refuse("protected", "undeclared artifact")
    files = {}
    if base_root is not None:
        try:
            from gnd.exp.session_store import _collect_candidate

            inventory, collected = _collect_candidate(base_root)
            if inventory.tree_sha256 != base_sha256:
                _refuse("stale-base", "base bytes differ from bound identity")
            files = {leaf.entry.path: leaf.data for leaf in collected}
        except (ArtifactError, ValueError) as error:
            if isinstance(error, PatchRefusal):
                raise
            _refuse(
                "limit"
                if "cap" in str(error) or "exceed" in str(error) or "limit" in str(error)
                else "path",
                str(error),
            )
    if seed and (
        len(doc["operations"]) != len(declared)
        or {op["artifact"] for op in doc["operations"]} != set(declared)
        or any(op["op"] != "replace-artifact" for op in doc["operations"])
    ):
        _refuse("shape", "initial seed must replace every declared artifact")
    documents, indexes = {}, {}
    visited = 0
    touched = {
        (op["artifact"], tuple(op.get("collection", [])))
        for op in doc["operations"]
        if op["op"] != "replace-artifact"
    }
    # A no-op still validates the declared base's key uniqueness and row bound.
    if not doc["operations"]:
        touched = {(a.path, c.path) for a in edits.artifacts for c in a.collections}
    for path, selector in sorted(touched):
        collection = next((c for c in declared[path].collections if c.path == selector), None)
        if collection is None:
            _refuse("keys", "undeclared collection")
        if path not in documents:
            try:
                documents[path] = bounded_json(files[path])
            except (KeyError, ValueError):
                _refuse("keys", "collection artifact is not valid JSON")
        rows = documents[path]
        try:
            for segment in selector:
                rows = rows[segment]
        except (TypeError, KeyError):
            _refuse("keys", "collection selector does not resolve")
        if not isinstance(rows, list):
            _refuse("keys", "collection must resolve to an array")
        visited += len(rows)
        if visited > 100000:
            _refuse("limit", "visited row count exceeds cap")
        index = {}
        for position, row in enumerate(rows):
            try:
                key = _key([row[k] for k in collection.key])
            except (KeyError, TypeError):
                _refuse("keys", "missing row key")
            if key in index:
                _refuse("keys", "duplicate base key")
            index[key] = position
        indexes[(path, selector)] = (collection, rows, index)
    seen, whole = set(), set()
    for op in doc["operations"]:
        path = op["artifact"]
        if op["op"] == "replace-artifact":
            if path in whole or any(k[0] == path for k in seen):
                _refuse("conflict", "whole and collection edits conflict")
            whole.add(path)
        else:
            selector = tuple(op["collection"])
            collection, rows, index = indexes[(path, selector)]
            if len(op["key"]) != len(collection.key):
                _refuse("keys", "key arity differs")
            key = _key(op["key"])
            if op["op"] == "upsert":
                try:
                    value_key = _key([op["value"][k] for k in collection.key])
                except (KeyError, TypeError):
                    _refuse("keys", "upsert value has no valid key")
                if key != value_key:
                    _refuse("keys", "upsert key differs from value")
            identity = (path, selector, key)
            if identity in seen or path in whole:
                _refuse("conflict", "duplicate or conflicting operation")
            seen.add(identity)
            if op["op"] == "delete" and key not in index:
                _refuse("missing-delete", "delete names no existing key")
    changed = set()
    for op in doc["operations"]:
        path = op["artifact"]
        if op["op"] == "replace-artifact":
            files[path] = canonical_json_bytes(op["value"], exact_numbers=True)
            continue
        collection, rows, index = indexes[(path, tuple(op["collection"]))]
        key = _key(op["key"])
        if op["op"] == "delete":
            rows[index[key]] = None
            changed.add(path)
        elif key not in index:
            rows.append(op["value"])
            changed.add(path)
        elif rows[index[key]] != op["value"]:
            rows[index[key]] = op["value"]
            changed.add(path)
    for _collection, rows, _index in indexes.values():
        rows[:] = [row for row in rows if row is not None]
    for path in changed:
        files[path] = canonical_json_bytes(documents[path], exact_numbers=True)
    if (
        len(files) > 10000
        or sum(map(len, files.values())) > 100 * 1024 * 1024
        or any(len(v) > MAX_PATCH_BYTES for v in files.values())
    ):
        _refuse("limit", "result inventory exceeds cap")
    return files
