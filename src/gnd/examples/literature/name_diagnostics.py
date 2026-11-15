"""Generate reviewable name candidates from original literature occurrences."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any

from gnd.anchors import read_regular_path, strict_json
from gnd.artifacts import ArtifactError

from .assurance_report import DOCUMENT_CAP, Refusal

INPUT_SCHEMA = "literature-name-occurrences/1"
OUTPUT_SCHEMA = "literature-name-diagnostics/1"
THRESHOLD = 0.8
FAMILY_MINIMUM = 4
MAX_OCCURRENCES = 500
MAX_CANDIDATES = 8_000
SCORES = {"homonym": 1.0, "family": 0.9, "synonym": 0.85}
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
DIGEST = re.compile(r"[0-9a-f]{64}")
COMPACT = re.compile(r"[A-Za-z0-9]+")
ADJACENT_CAPITALS = re.compile(r"[A-Z]{2}")
GENERIC_TOKENS = frozenset({"family", "method", "variant"})


def _require(condition: bool) -> None:
    if not condition:
        raise Refusal("input:schema")


def _shape(value: Any, required: set[str], optional: frozenset[str] = frozenset()) -> None:
    _require(isinstance(value, dict) and required <= value.keys() <= required | optional)


def _id(value: Any) -> bool:
    return isinstance(value, str) and ID.fullmatch(value) is not None


def _id_set(values: Any) -> frozenset[str]:
    _require(isinstance(values, list) and len(values) <= 8 and all(map(_id, values)))
    result = frozenset(values)
    _require(len(result) == len(values))
    return result


@dataclass(frozen=True)
class Occurrence:
    id: str
    work: str
    contexts: frozenset[str]
    origins: frozenset[str]
    source: str
    object_type: str
    spelling: str
    evidence: dict
    digest: str
    folded: str
    tokens: frozenset[str]
    acronym: bool

    @property
    def key(self) -> tuple[str, str, str]:
        return self.source, self.object_type, self.spelling

    def resolution_key(self) -> dict:
        return {"source": self.source, "object_type": self.object_type, "value": self.spelling}


def _natural(value: Any) -> bool:
    return type(value) is int and value >= 0


def _tokenize(folded: str) -> frozenset[str]:
    words = re.findall(r"[^\W_]+", folded)
    return frozenset(
        "family" if word == "families" else word[:-1] if len(word) >= 5 and word.endswith("s") else word
        for word in words if len(word) >= 4
    ) - GENERIC_TOKENS


def _occurrence(row: Any) -> Occurrence:
    _shape(row, {"id", "work", "contexts", "introducing_works", "key", "evidence", "population_sha256"})
    _require(_id(row["id"]) and _id(row["work"]))
    contexts, origins = _id_set(row["contexts"]), _id_set(row["introducing_works"])
    _require(bool(contexts))
    key = row["key"]
    _shape(key, {"source", "object_type", "value"})
    _require(_id(key["source"]) and _id(key["object_type"]))
    spelling = key["value"]
    _require(isinstance(spelling, str) and 0 < len(spelling) <= 96 and spelling.strip() == spelling
             and spelling.isprintable())
    evidence = row["evidence"]
    _shape(evidence, {"source", "fact_type", "fact_index", "role"}, frozenset({"span"}))
    _require(evidence["source"] == key["source"] and _id(evidence["fact_type"])
             and _natural(evidence["fact_index"]) and _id(evidence["role"]))
    if "span" in evidence:
        span = evidence["span"]
        _shape(span, {"start", "end"})
        _require(_natural(span["start"]) and _natural(span["end"]) and span["start"] < span["end"])
    digest = row["population_sha256"]
    _require(isinstance(digest, str) and DIGEST.fullmatch(digest) is not None)
    folded = unicodedata.normalize("NFC", spelling).casefold()
    return Occurrence(row["id"], row["work"], contexts, origins, key["source"], key["object_type"], spelling,
                      evidence, digest, folded, _tokenize(folded),
                      COMPACT.fullmatch(spelling) is not None and ADJACENT_CAPITALS.search(spelling) is not None)


def _occurrences(data: Any) -> list[Occurrence]:
    _shape(data, {"schema", "occurrences"})
    _require(data["schema"] == INPUT_SCHEMA and isinstance(data["occurrences"], list))
    if len(data["occurrences"]) > MAX_OCCURRENCES:
        raise Refusal("input:occurrence-limit")
    rows = sorted(map(_occurrence, data["occurrences"]), key=lambda row: row.id)
    _require(len({row.id for row in rows}) == len(rows))
    sources = {}
    for row in rows:
        _require(sources.setdefault(row.source, row.digest) == row.digest)
    return rows


def _one_edit(left: str, right: str) -> bool:
    if abs(len(left) - len(right)) > 1 or left == right:
        return False
    if len(left) == len(right):
        return sum(a != b for a, b in zip(left, right, strict=True)) == 1
    if len(left) > len(right):
        left, right = right, left
    for index, (a, b) in enumerate(zip(left, right, strict=False)):
        if a != b:
            return left[index:] == right[index + 1:]
    return True


def _families(rows: list[Occurrence]) -> dict[str, frozenset[str]]:
    works = defaultdict(set)
    introduced = set()
    for row in rows:
        for token in row.tokens:
            family = row.object_type, token
            works[family].add(row.work)
            if row.origins:
                introduced.add(family)
    result = defaultdict(set)
    for (object_type, token), sources in works.items():
        if len(sources) >= FAMILY_MINIMUM and (object_type, token) not in introduced:
            result[object_type].add(token)
    return {key: frozenset(tokens) for key, tokens in result.items()}


def _classify(left: Occurrence, right: Occurrence, families: frozenset[str]) -> str | None:
    context_overlap = not left.contexts.isdisjoint(right.contexts)
    if (left.folded == right.folded and left.origins.isdisjoint(right.origins)
            and (not context_overlap or left.spelling != right.spelling and (left.acronym or right.acronym))):
        return "homonym"
    if left.work != right.work and left.tokens & right.tokens & families:
        return "family"
    if context_overlap and _one_edit(left.folded, right.folded):
        return "synonym"
    return None


def _placeholders(rows: list[Occurrence]) -> dict[tuple[str, str, str], str]:
    used = {(row.object_type, row.spelling) for row in rows}
    output = {}
    for row in rows:
        if row.key in output:
            continue
        digest = hashlib.sha256(json.dumps(row.key, separators=(",", ":")).encode()).hexdigest()
        value = f"@unresolved:{digest}"
        while (row.object_type, value) in used:
            value += "_"
        output[row.key] = value
        used.add((row.object_type, value))
    return output


def diagnose(data: Any) -> list[dict]:
    """Return candidate kinds and unresolved proposals in occurrence order."""
    rows = _occurrences(data)
    families = _families(rows)
    selected = {}
    for left, right in combinations(rows, 2):
        if left.source == right.source or left.object_type != right.object_type:
            continue
        kind = _classify(left, right, families.get(left.object_type, frozenset()))
        if kind is None or SCORES[kind] < THRESHOLD:
            continue
        pair = frozenset((left.key, right.key))
        earlier = selected.get(pair)
        if earlier is None or SCORES[kind] > SCORES[earlier[2]]:
            selected[pair] = (left, right, kind)
            if len(selected) > MAX_CANDIDATES:
                raise Refusal("input:candidate-limit")
    placeholders = _placeholders(rows)
    output = []
    for left, right, kind in sorted(selected.values(), key=lambda item: (item[0].id, item[1].id)):
        output.append({
            "occurrences": [left.id, right.id],
            "kind": kind,
            "score": SCORES[kind],
            "resolution": {
                "decision": "unresolved",
                "keys": [left.resolution_key(), right.resolution_key()],
                "evidence": [left.evidence | {"key": 0}, right.evidence | {"key": 1}],
                "producer": {"kind": "tool", "id": "literature-name-diagnostics"},
                "input_sha256": {left.source: left.digest, right.source: right.digest},
                "placeholders": [placeholders[left.key], placeholders[right.key]],
            },
        })
    return output


def read_diagnostic_input(path: Path) -> tuple[object, str]:
    """Read one regular local input and bind its exact bytes."""
    try:
        raw = read_regular_path(path, label="diagnostic input", max_bytes=DOCUMENT_CAP)
    except (ArtifactError, OSError) as error:
        raise Refusal("input:unreadable") from error
    data = strict_json(raw, max_bytes=DOCUMENT_CAP, too_large="input:too-large")
    return data, hashlib.sha256(raw).hexdigest()


def main(argv: list[str] | None = None) -> int:
    """Read a capped input and print one diagnostic report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args(argv)
    output = {"schema": OUTPUT_SCHEMA, "exit_code": 0, "input_sha256": None, "threshold": THRESHOLD,
              "family_minimum_works": FAMILY_MINIMUM, "candidates": [], "reason": None}
    try:
        data, output["input_sha256"] = read_diagnostic_input(args.input)
        output["candidates"] = diagnose(data)
    except Refusal as error:
        output.update(exit_code=3, reason=error.reason)
    except (ValueError, UnicodeError, RecursionError):
        output.update(exit_code=3, reason="input:not-json")
    print(json.dumps(output, sort_keys=True))
    return output["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
