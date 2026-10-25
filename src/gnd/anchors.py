"""RF3 shared dependency home; algorithms retain predecessor semantics."""
from __future__ import annotations

import json
import math
import re
import unicodedata
from array import array
from collections import deque
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from gnd import input_policy as _rf7_input
from gnd.anchor_identity import ANCHOR_TRANSLATION as _ANCHOR_TRANSLATION
from gnd.artifacts import canonical_json_bytes, read_regular_file_bytes, sha256_hex

MAX_SIDECAR_BYTES = 1 << 20


MAX_DOCUMENT_BYTES = 10 << 20


_HEX = re.compile(r"[0-9a-f]{64}\Z")


_NUMBER = re.compile(r"[+-]?(?:[0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)(?:\.[0-9]+)?|[+-]?\.[0-9]+")


_INTEGER = re.compile(r"[+-]?(?:[0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)\Z")


_DECIMAL = re.compile(r"[+-]?(?:[0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)?\.[0-9]+")


_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


_NUMERIC_TOKEN = re.compile(r"[+-]?(?:[0-9][0-9,.]*|\.[0-9]+)(?:\s*%)?")


class AnchorError(ValueError):
    """A bounded, named layer-three anchor refusal."""


@dataclass(frozen=True)
class AnchorSidecar:
    schema_version: int
    population_sha256: str
    vocabulary_digest: str
    document_sha256: str
    anchors: tuple[dict[str, Any], ...]


def _pairs(rows: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in rows:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-JSON constant {value}")


def _parse(raw: bytes) -> Any:
    if len(raw) > MAX_SIDECAR_BYTES:
        raise ValueError("sidecar exceeds 1 MiB")
    def _integer(value: str) -> int:
        if len(value) > 18:
            raise ValueError("oversized integer")
        return int(value)
    value = _rf7_input.loads(raw.decode("utf-8", "strict"), object_pairs_hook=_pairs,
                       parse_constant=_reject_constant, parse_int=_integer)
    def depth(node: Any, level: int = 0) -> None:
        if level > 32:
            raise ValueError("JSON nesting too deep")
        if isinstance(node, dict):
            for child in node.values():
                depth(child, level + 1)
        elif isinstance(node, list):
            for child in node:
                depth(child, level + 1)
    depth(value)
    return value


def _exact_keys(value: Any, required: set[str], optional: set[str] = frozenset()) -> None:
    if not isinstance(value, dict) or not required <= value.keys() or value.keys() - required - optional:
        raise ValueError("anchor record has missing or unexpected fields")


def _digest(value: Any) -> bool:
    return isinstance(value, str) and _HEX.fullmatch(value) is not None


def _scalar(value: Any) -> bool:
    return value is None or isinstance(value, (str, bool, int)) or (isinstance(value, float) and math.isfinite(value))


def parse_anchor_sidecar(raw: bytes) -> AnchorSidecar:
    try:
        data = _parse(raw)
        _exact_keys(data, {"schema_version", "population_sha256", "vocabulary_digest", "document_sha256", "anchors"})
        if type(data["schema_version"]) is not int or data["schema_version"] != 1:
            raise ValueError("unsupported sidecar version")
        if not all(_digest(data[key]) for key in ("population_sha256", "vocabulary_digest", "document_sha256")):
            raise ValueError("invalid digest")
        if not isinstance(data["anchors"], list):
            raise TypeError("anchors must be a list")
        seen = set()
        for anchor in data["anchors"]:
            _exact_keys(anchor, {"fact_key", "role", "span", "occurrence", "excerpt_sha256"}, {"block_id", "unit_id"})
            _exact_keys(anchor["fact_key"], {"fact_type", "roles"})
            fact_key = anchor["fact_key"]
            if not isinstance(fact_key["fact_type"], str) or not isinstance(fact_key["roles"], dict) or not all(isinstance(k, str) and _scalar(v) for k, v in fact_key["roles"].items()):
                raise ValueError("invalid fact key")
            if not isinstance(anchor["role"], str) or not anchor["role"]:
                raise ValueError("invalid anchor role")
            for metadata in ("block_id", "unit_id"):
                if metadata in anchor and (not isinstance(anchor[metadata], str) or not anchor[metadata]):
                    raise ValueError("invalid anchor metadata")
            _exact_keys(anchor["span"], {"start", "end"})
            span = anchor["span"]
            if any(type(span[k]) is not int for k in ("start", "end")) or not 0 <= span["start"] < span["end"]:
                raise ValueError("invalid anchor span")
            if type(anchor["occurrence"]) is not int or anchor["occurrence"] < 0 or not _digest(anchor["excerpt_sha256"]):
                raise ValueError("invalid anchor occurrence or excerpt digest")
            identity = (fact_key["fact_type"], json.dumps(fact_key["roles"], sort_keys=True, ensure_ascii=False, allow_nan=False), anchor["role"])
            if identity in seen:
                raise ValueError("duplicate fact-role anchor")
            seen.add(identity)
        return AnchorSidecar(data["schema_version"], data["population_sha256"], data["vocabulary_digest"], data["document_sha256"], tuple(data["anchors"]))
    except (ValueError, TypeError, UnicodeError, RecursionError) as error:
        raise AnchorError(f"anchor:sidecar-invalid: {error}") from error


def read_anchor_sidecar(path: str | Path) -> AnchorSidecar:
    try:
        raw = read_regular_path(path, label="anchor sidecar", max_bytes=MAX_SIDECAR_BYTES)
    except Exception as error:
        raise AnchorError(f"anchor:sidecar-invalid: {error}") from error
    return parse_anchor_sidecar(raw)


def read_regular_path(path: str | Path, *, label: str, max_bytes: int) -> bytes:
    """Read a caller path from a trusted root, refusing symlinks at every step."""
    candidate = Path(path)
    if candidate.is_absolute():
        root = Path(candidate.anchor)
        relative = candidate.relative_to(root).as_posix()
    else:
        root = Path.cwd()
        relative = candidate.as_posix()
    return read_regular_file_bytes(root, relative, label=label, max_bytes=max_bytes)


def validate_anchor_sidecar(sidecar: AnchorSidecar) -> AnchorSidecar:
    """Apply the same strict wire validation to an in-memory sidecar."""
    try:
        payload = {
            "schema_version": sidecar.schema_version,
            "population_sha256": sidecar.population_sha256,
            "vocabulary_digest": sidecar.vocabulary_digest,
            "document_sha256": sidecar.document_sha256,
            "anchors": list(sidecar.anchors),
        }
        return parse_anchor_sidecar(_canonical(payload))
    except (ValueError, TypeError, AttributeError) as error:
        raise AnchorError(f"anchor:sidecar-invalid: {error}") from error


def _canonical(value: Any) -> bytes:
    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if not all(isinstance(key, str) for key in node):
                raise ValueError("non-string vocabulary key")
            for item in node.values():
                walk(item)
        elif isinstance(node, (list, tuple)):
            for item in node:
                walk(item)
        elif not _scalar(node):
            raise ValueError("non-finite or unsupported vocabulary scalar")
    walk(value)
    return canonical_json_bytes(value).removesuffix(b"\n")


def vocabulary_digest(model: Any) -> str:
    facts = model.fact_types if hasattr(model, "fact_types") else model["fact_types"]
    objects = model.object_types if hasattr(model, "object_types") else model["object_types"]
    # The description is excluded, extras included (D11): an extraction sidecar
    # stays bound when only a description changes, so this digest does not
    # identify the rendered vocabulary text.
    projection = {"object_types": [
        {key: value for key, value in item.items() if key != "description"}
        for item in objects
    ], "fact_types": [
        {key: value for key, value in fact.items() if key not in {"derivation_rule", "constraints", "sample_population", "depends_on"}}
        for fact in facts
    ]}
    return sha256_hex(_canonical(projection))


def canonical_document_text(raw: bytes) -> str:
    if len(raw) > MAX_DOCUMENT_BYTES:
        raise AnchorError("anchor:sidecar-invalid: document exceeds 10 MiB")
    try:
        return unicodedata.normalize("NFC", raw.decode("utf-8", "strict"))
    except UnicodeError as error:
        raise AnchorError(f"anchor:sidecar-invalid: {error}") from error


def bind_anchors(
    sidecar: AnchorSidecar,
    model: Any,
    population_bytes: bytes | None,
    document_bytes: bytes | None,
    population: Any = None,
) -> str:
    if population_bytes is None or document_bytes is None:
        raise AnchorError("anchor:binding-mismatch: raw population and document bytes required")
    source = canonical_document_text(document_bytes)
    if (sidecar.population_sha256 != sha256_hex(population_bytes) or sidecar.document_sha256 != sha256_hex(document_bytes) or sidecar.vocabulary_digest != vocabulary_digest(model)):
        raise AnchorError("anchor:binding-mismatch: digest differs")
    declared = {
        str(fact_type["id"]): {str(role["role_name"]) for role in fact_type.get("roles") or []}
        for fact_type in model.fact_types
    }
    admitted = {}
    if population is not None:
        for fact_type, rows in population.facts.items():
            admitted[fact_type] = {
                tuple((name, type(value).__name__, repr(value)) for name, value in sorted(row.items()))
                for row in rows
            }
    for anchor in sidecar.anchors:
        fact_key = anchor["fact_key"]
        fact_type = fact_key["fact_type"]
        roles = fact_key["roles"]
        identity = tuple((name, type(value).__name__, repr(value)) for name, value in sorted(roles.items()))
        if fact_type not in declared or set(roles) != declared[fact_type] or anchor["role"] not in roles or (population is not None and identity not in admitted.get(fact_type, set())):
            raise AnchorError("anchor:sidecar-invalid: fact key or role is not an admitted population row")
        span = anchor["span"]
        if span["end"] > len(source) or sha256_hex(source[span["start"]:span["end"]].encode("utf-8")) != anchor["excerpt_sha256"]:
            raise AnchorError("anchor:binding-mismatch: source span or excerpt differs")
    return source


def write_anchor_sidecar(sidecar: AnchorSidecar, population_path: str | Path) -> Path:
    """Atomically publish an adjacent sidecar and read it back."""
    import os
    import tempfile
    read_regular_path(population_path, label="anchor population", max_bytes=MAX_DOCUMENT_BYTES)
    target = Path(str(population_path) + ".anchors.json")
    payload = {"schema_version": sidecar.schema_version, "population_sha256": sidecar.population_sha256,
               "vocabulary_digest": sidecar.vocabulary_digest, "document_sha256": sidecar.document_sha256,
               "anchors": list(sidecar.anchors)}
    raw = _canonical(payload) + b"\n"
    if len(raw) > MAX_SIDECAR_BYTES:
        raise AnchorError("anchor:sidecar-invalid: sidecar exceeds 1 MiB")
    fd, temporary = tempfile.mkstemp(prefix=".anchors-", dir=target.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
        read_anchor_sidecar(target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return target


def _word(char: str) -> bool:
    return bool(re.match(r"\w", char))


def lexical_ranges(
    source: str,
    values: set[str],
    *,
    wanted_occurrences: dict[str, set[int]] | None = None,
) -> dict[str, Any]:
    """Index requested values with one trie walk over the projected document."""
    # Normalization is projected per code point so a source span can be checked
    # against the complete selected match after case folding and substitutions.
    chars: list[str] = []
    starts = array("I")
    ends = array("I")
    for index, char in enumerate(source):
        projected = unicodedata.normalize("NFC", char.translate(_ANCHOR_TRANSLATION).casefold())
        for part in projected:
            if part.isspace():
                if chars and chars[-1] == " ":
                    ends[-1] = index + 1
                    continue
                part = " "
            chars.append(part)
            starts.append(index)
            ends.append(index + 1)
    normalized = "".join(chars)
    selected = wanted_occurrences is not None
    if selected:
        values = values & set(wanted_occurrences)
    result: dict[str, Any] = {value: {} if selected else [] for value in values}
    counts = dict.fromkeys(values, 0)
    transitions: list[dict[str, int]] = [{}]
    failure = [0]
    outputs: list[list[str]] = [[]]
    for value in values:
        if not value:
            continue
        state = 0
        for char in value:
            following = transitions[state].get(char)
            if following is None:
                following = len(transitions)
                transitions[state][char] = following
                transitions.append({})
                failure.append(0)
                outputs.append([])
            state = following
        outputs[state].append(value)
    queue = deque(transitions[0].values())
    while queue:
        state = queue.popleft()
        for char, following in transitions[state].items():
            queue.append(following)
            ancestor = failure[state]
            while ancestor and char not in transitions[ancestor]:
                ancestor = failure[ancestor]
            failure[following] = transitions[ancestor].get(char, 0)
            outputs[following].extend(outputs[failure[following]])
    state = 0
    for index, char in enumerate(normalized):
        while state and char not in transitions[state]:
            state = failure[state]
        state = transitions[state].get(char, 0)
        for value in outputs[state]:
            start = index + 1 - len(value)
            end = index + 1
            if (start == 0 or not _word(normalized[start - 1])) and (end == len(normalized) or not _word(normalized[end])):
                if selected:
                    occurrence = counts[value]
                    if occurrence in wanted_occurrences[value]:
                        result[value][occurrence] = (starts[start], ends[index])
                    counts[value] += 1
                else:
                    result[value].append((starts[start], ends[index]))
    return result


def recognition_target(kind: str, expected: Any) -> Any:
    """Canonical comparison key for one admitted recogniser value."""
    return date.fromisoformat(str(expected)) if kind == "iso-8601-date" else Decimal(str(expected))


def recognition_index(
    source: str,
    kinds: set[str],
    *,
    limits: dict[str, dict[Any, int]] | None = None,
) -> dict[str, dict[Any, list[tuple[int, int]]]]:
    """Scan each declared numeric/date grammar once, independent of fact count."""
    result: dict[str, dict[Any, list[tuple[int, int]]]] = {}
    for kind in kinds:
        values: dict[Any, list[tuple[int, int]]] = {}
        requested = None if limits is None else limits.get(kind, {})
        pattern = _DATE if kind == "iso-8601-date" else _NUMERIC_TOKEN
        for match in pattern.finditer(source):
            start, end = match.span()
            if kind == "iso-8601-date":
                forbidden_before = start and (_word(source[start - 1]) or source[start - 1] in "+-")
                forbidden_after = end < len(source) and (_word(source[end]) or source[end] in "+-")
            else:
                forbidden_before = start and (_word(source[start - 1]) or source[start - 1] in "+-")
                forbidden_after = end < len(source) and (_word(source[end]) or source[end] == "%")
            if forbidden_before or forbidden_after:
                continue
            token = match.group()
            if kind != "iso-8601-date":
                percent = token.endswith("%")
                numeric = token.rstrip("%").rstrip()
                if kind == "percent":
                    if not percent or _NUMBER.fullmatch(numeric) is None:
                        continue
                elif percent or (kind == "integer" and _INTEGER.fullmatch(numeric) is None) or (kind == "decimal" and _DECIMAL.fullmatch(numeric) is None):
                    continue
            try:
                found = date.fromisoformat(token) if kind == "iso-8601-date" else Decimal(numeric.replace(",", ""))
            except (ValueError, InvalidOperation):
                continue
            if requested is not None and found not in requested:
                continue
            bucket = values.setdefault(found, [])
            if requested is None or len(bucket) <= requested[found]:
                bucket.append((start, end))
        result[kind] = values
    return result


def recognised_ranges(index: dict[str, dict[Any, list[tuple[int, int]]]], kind: str, expected: Any) -> list[tuple[int, int]]:
    try:
        target = recognition_target(kind, expected)
    except (ValueError, InvalidOperation):
        return []
    return index.get(kind, {}).get(target, [])


DATE = _DATE
DECIMAL = _DECIMAL
HEX = _HEX
INTEGER = _INTEGER
NUMBER = _NUMBER
NUMERIC_TOKEN = _NUMERIC_TOKEN
canonical = _canonical
digest = _digest
exact_keys = _exact_keys
pairs = _pairs
parse = _parse
reject_constant = _reject_constant
scalar = _scalar
word = _word

AnchorError.__module__ = 'gnd.extract.anchors'

AnchorSidecar.__module__ = 'gnd.extract.anchors'

_pairs.__module__ = 'gnd.extract.anchors'

_reject_constant.__module__ = 'gnd.extract.anchors'

_parse.__module__ = 'gnd.extract.anchors'

_exact_keys.__module__ = 'gnd.extract.anchors'

_digest.__module__ = 'gnd.extract.anchors'

_scalar.__module__ = 'gnd.extract.anchors'

parse_anchor_sidecar.__module__ = 'gnd.extract.anchors'

read_anchor_sidecar.__module__ = 'gnd.extract.anchors'

read_regular_path.__module__ = 'gnd.extract.anchors'

validate_anchor_sidecar.__module__ = 'gnd.extract.anchors'

_canonical.__module__ = 'gnd.extract.anchors'

vocabulary_digest.__module__ = 'gnd.extract.anchors'

canonical_document_text.__module__ = 'gnd.extract.anchors'

bind_anchors.__module__ = 'gnd.extract.anchors'

write_anchor_sidecar.__module__ = 'gnd.extract.anchors'

_word.__module__ = 'gnd.extract.anchors'

lexical_ranges.__module__ = 'gnd.extract.anchors'

recognition_target.__module__ = 'gnd.extract.anchors'

recognition_index.__module__ = 'gnd.extract.anchors'

recognised_ranges.__module__ = 'gnd.extract.anchors'
