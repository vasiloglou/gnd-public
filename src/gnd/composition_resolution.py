"""Bind source evidence and verify an explicit composition identity policy."""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from gnd.anchors import strict_json
from gnd.model_index import ModelIndex

if TYPE_CHECKING:
    from gnd.composition import Source

MAX_RESOLUTION_BYTES = 4 << 20
_SHA256 = re.compile(r"[0-9a-f]{64}")


class CompositionError(ValueError):
    """A bounded, value-free composition refusal (exit 3)."""

    def __init__(self, message: str) -> None:
        super().__init__(f"composition:invalid: {message}")


# Resolves old serialized exception references through the public alias.
CompositionError.__module__ = "gnd.composition"


def scalar(value: Any) -> bool:
    return isinstance(value, (str, bool, int)) or (isinstance(value, float) and math.isfinite(value))


def exact_fields(value: Any, fields: set[str], what: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise CompositionError(f"{what} has missing or unexpected fields")
    return value


def read_json(raw: bytes, *, max_bytes: int, what: str) -> Any:
    try:
        return strict_json(raw, max_bytes=max_bytes, too_large=f"{what} exceeds its size cap")
    except (ValueError, TypeError, UnicodeError, RecursionError) as error:
        raise CompositionError(f"{what}: {error}") from error


def scalar_key(value: Any) -> tuple[str, str]:
    return type(value).__name__, repr(value)


def row_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return tuple((name, *scalar_key(value)) for name, value in sorted(row.items()))


def _identity(key: dict) -> tuple:
    return key["source"], key["object_type"], *scalar_key(key["value"])


def _natural(value: Any) -> bool:
    return type(value) is int and value >= 0


def _parse_coordinate(coordinate: Any, what: str) -> int:
    fields = {"key", "source", "fact_type", "fact_index", "role"}
    if isinstance(coordinate, dict) and "span" in coordinate:
        fields.add("span")
    exact_fields(coordinate, fields, what)
    if (type(coordinate["key"]) is not int or coordinate["key"] not in (0, 1)
            or not _natural(coordinate["fact_index"])
            or not all(isinstance(coordinate[field], str) and coordinate[field]
                       for field in ("source", "fact_type", "role"))):
        raise CompositionError(f"{what} has an invalid coordinate")
    if "span" in fields:
        span = exact_fields(coordinate["span"], {"start", "end"}, f"{what} span")
        if not (_natural(span["start"]) and _natural(span["end"]) and span["start"] < span["end"]):
            raise CompositionError(f"{what} has an invalid span")
    return coordinate["key"]


@dataclass(frozen=True)
class Resolution:
    object_types: frozenset[str]
    decisions: list[dict]

    def check_renaming(self, number: int, renaming: dict, object_type: str | None) -> None:
        citation = renaming["decision"]
        if citation >= len(self.decisions):
            raise CompositionError(f"renaming {number} cites unknown decision {citation}")
        identity = renaming["source"], object_type, *scalar_key(renaming["from"])
        if not any(_identity(key) == identity for key in self.decisions[citation]["keys"]):
            raise CompositionError(f"renaming {number} cites decision {citation}, which does not name its key")


def parse_resolution(raw: bytes, index: ModelIndex, sources: tuple[str, ...]) -> Resolution:
    """Parse bounded resolution JSON and validate its model and manifest references."""
    data = exact_fields(read_json(raw, max_bytes=MAX_RESOLUTION_BYTES, what="resolution"),
                        {"schema", "object_types", "decisions"}, "resolution")
    if data["schema"] != "gnd-resolution/1":
        raise CompositionError("resolution schema is not gnd-resolution/1")
    types = data["object_types"]
    if (not isinstance(types, list)
            or not all(isinstance(item, str) and index.object_type(item) is not None for item in types)
            or len(set(types)) != len(types)):
        raise CompositionError("resolution object_types must be distinct declared object types")
    if not isinstance(data["decisions"], list):
        raise CompositionError("resolution decisions must be a list")
    known_sources, known_types = set(sources), frozenset(types)
    for number, decision in enumerate(data["decisions"]):
        what = f"resolution decision {number}"
        exact_fields(decision, {"decision", "keys", "evidence", "producer", "input_sha256", "placeholders"}, what)
        kind = decision["decision"]
        if kind not in ("same", "different", "unresolved"):
            raise CompositionError(f"{what} has an invalid decision kind")
        keys = decision["keys"]
        if not isinstance(keys, list) or len(keys) != 2:
            raise CompositionError(f"{what} requires two keys")
        for position, key in enumerate(keys):
            exact_fields(key, {"source", "object_type", "value"}, f"{what} key {position}")
            if (not isinstance(key["source"], str) or key["source"] not in known_sources
                    or not isinstance(key["object_type"], str) or key["object_type"] not in known_types
                    or not scalar(key["value"])):
                raise CompositionError(f"{what} key {position} is invalid")
        if keys[0]["source"] == keys[1]["source"] or keys[0]["object_type"] != keys[1]["object_type"]:
            raise CompositionError(f"{what} needs keys of one object type from distinct sources")
        producer = exact_fields(decision["producer"], {"kind", "id"}, f"{what} producer")
        if (producer["kind"] not in ("reviewer", "tool") or not isinstance(producer["id"], str)
                or not 1 <= len(producer["id"]) <= 128):
            raise CompositionError(f"{what} has an invalid producer")
        digests = exact_fields(decision["input_sha256"], {key["source"] for key in keys}, f"{what} input_sha256")
        if not all(isinstance(digest, str) and _SHA256.fullmatch(digest) for digest in digests.values()):
            raise CompositionError(f"{what} has an invalid input digest")
        coordinates = decision["evidence"]
        if not isinstance(coordinates, list):
            raise CompositionError(f"{what} evidence must be a list")
        if {_parse_coordinate(item, f"{what} evidence {position}")
                for position, item in enumerate(coordinates)} != {0, 1}:
            raise CompositionError(f"{what} requires evidence for both keys")
        placeholders = decision["placeholders"]
        if kind == "unresolved":
            if (not isinstance(placeholders, list) or len(placeholders) != 2
                    or not all(scalar(value) and type(value) is type(key["value"])
                               for value, key in zip(placeholders, keys, strict=True))
                    or scalar_key(placeholders[0]) == scalar_key(placeholders[1])):
                raise CompositionError(f"{what} has invalid placeholders")
        elif placeholders is not None:
            raise CompositionError(f"{what} requires null placeholders")
    return Resolution(known_types, data["decisions"])


class ResolutionEvidence:
    """Index asserted roles and the anchors bound to each cited source."""

    def __init__(self, index: ModelIndex, sources: tuple[Source, ...], resolution: Resolution):
        self.resolution = resolution
        self.sources = {source.id: source for source in sources}
        self.roles = {}
        self.anchored = set()
        model_roles = index.role_object_types()
        for fact in index.iter_fact_types_shared():
            if fact.get("derivation") in ("derived", "semiderived"):
                continue
            fact_type = fact["id"]
            self.roles[fact_type] = {
                role: object_type for role, object_type in model_roles[fact_type].items()
                if object_type in resolution.object_types
            }
            for rule in fact.get("constraints") or ():
                if rule.get("type") == "anchored":
                    role = rule.get("role")
                    anchored = model_roles[fact_type] if role is None else (role,)
                    self.anchored.update((fact_type, name) for name in anchored)
        self.anchors = {
            (source.id, anchor["fact_key"]["fact_type"], row_key(anchor["fact_key"]["roles"]),
             anchor["role"], anchor["span"]["start"], anchor["span"]["end"])
            for source in sources for anchor in source.sidecar.anchors
        }

    def bind(self) -> None:
        """Verify each decision's population digests and asserted evidence."""
        for number, decision in enumerate(self.resolution.decisions):
            for source, digest in sorted(decision["input_sha256"].items()):
                if self.sources[source].digests["population_sha256"] != digest:
                    raise CompositionError(f"decision {number} input digest for source {source} differs from its population")
            for position, coordinate in enumerate(decision["evidence"]):
                key_index = coordinate["key"]
                key = decision["keys"][key_index]
                source, fact, row_index, role = (coordinate[field] for field in
                                                ("source", "fact_type", "fact_index", "role"))
                label = f"decision {number} evidence {position}"
                # Only echo model-declared identifiers and manifest source ids.
                if source not in self.sources or role not in self.roles.get(fact, {}):
                    raise CompositionError(f"{label} does not name an asserted source role")
                label += f" (source {source}, {fact}#{row_index}.{role})"
                rows = self.sources[source].population.facts.get(fact, ())
                if (source != key["source"] or self.roles[fact][role] != key["object_type"]
                        or row_index >= len(rows) or role not in rows[row_index]
                        or scalar_key(rows[row_index][role]) != scalar_key(key["value"])):
                    raise CompositionError(f"{label} does not hold key {key_index}")
                span = coordinate.get("span")
                if (fact, role) in self.anchored:
                    if span is None or (source, fact, row_key(rows[row_index]), role,
                                        span["start"], span["end"]) not in self.anchors:
                        raise CompositionError(f"{label} has no anchor at its span")
                elif span is not None:
                    raise CompositionError(f"{label} names a span for an unanchored role")

    def collect_keys(self, renamings: dict) -> dict:
        """Collect the first asserted coordinate and outcome of each key."""
        keys = {}
        for source in self.sources.values():
            for fact in sorted(source.population.facts):
                roles = self.roles.get(fact)
                if not roles:
                    continue
                for row_index, row in enumerate(source.population.facts[fact]):
                    for role, object_type in roles.items():
                        if role not in row:
                            continue
                        value = row[role]
                        identity = source.id, object_type, *scalar_key(value)
                        if identity not in keys:
                            keys[identity] = {
                                "source": source.id, "object_type": object_type, "value": value,
                                "outcome": renamings.get(identity, (None, value))[1],
                                "coordinate": f"{source.id} {fact}#{row_index}.{role}",
                            }
        return keys

    def other_outcomes(self, keys: dict, kept: dict, renamings: dict) -> Iterable[tuple]:
        """Yield outcomes of other entities, including instance-only values."""
        def outcome(identity):
            _, object_type, *original = identity
            if object_type in self.resolution.object_types and identity not in keys:
                renamed = renamings.get(identity)
                return object_type, scalar_key(renamed[1]) if renamed is not None else tuple(original)
            return None

        for identities in (kept, renamings):
            for identity in identities:
                result = outcome(identity)
                if result is not None:
                    yield result
        for source in self.sources.values():
            for object_type, values in source.population.instances.items():
                if object_type in self.resolution.object_types:
                    for value in values:
                        result = outcome((source.id, object_type, *scalar_key(value)))
                        if result is not None:
                            yield result

    def stamp_lineage(self, facts: list[dict], max_bytes: int) -> None:
        """Attach decision indexes, checking expansion before storing each list."""
        by_key = defaultdict(set)
        for number, decision in enumerate(self.resolution.decisions):
            for key in decision["keys"]:
                by_key[_identity(key)].add(number)
        index_bytes = [len(str(number)) + 1 for number in range(len(self.resolution.decisions))]
        spent = 0
        for fact in facts:
            citations = set()
            for origin in fact["sources"]:
                source, kind, row_index = origin["source"], origin["fact_type"], origin["fact_index"]
                roles = self.roles.get(kind)
                if roles:
                    row = self.sources[source].population.facts[kind][row_index]
                    for role, object_type in roles.items():
                        if role in row:
                            citations.update(by_key.get((source, object_type, *scalar_key(row[role])), ()))
            # The canonical writer also includes indentation and field names.
            spent += sum(index_bytes[citation] for citation in citations)
            if spent > max_bytes:
                raise CompositionError("the composition record would exceed its 16 MiB cap")
            fact["decisions"] = sorted(citations)


def _roots(pairs: list[tuple[int, int]], size: int) -> list[int]:
    parent = list(range(size))
    weights = [1] * size

    def root(item: int) -> int:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    for left, right in pairs:
        a, b = root(left), root(right)
        if a != b:
            if weights[a] < weights[b]:
                a, b = b, a
            parent[b] = a
            weights[a] += weights[b]
    return [root(item) for item in range(size)]


def _pair_refusal(left: dict, right: dict, reason: str) -> CompositionError:
    return CompositionError(f"keys at {left['coordinate']} and {right['coordinate']} "
                            f"(object type {left['object_type']}) {reason}")


def check_coverage(keys: list[dict], decisions: list[dict], *, other_outcomes: Iterable[tuple] = ()) -> None:
    """Verify indexed decisions and all required joins and separations."""
    positions = {_identity(key): position for position, key in enumerate(keys)}
    outcomes = [scalar_key(key["outcome"]) for key in keys]
    pairs = [tuple(positions[_identity(key)] for key in decision["keys"]) for decision in decisions]
    roots = _roots([pair for pair, decision in zip(pairs, decisions, strict=True)
                    if decision["decision"] == "same"], len(keys))
    joined, spelling = defaultdict(list), defaultdict(list)
    for position, key in enumerate(keys):
        joined[key["object_type"], outcomes[position]].append(position)
        spelling[key["object_type"], scalar_key(key["value"])].append(position)
    placeholders = {
        (keys[key]["object_type"], outcomes[key])
        for pair, decision in zip(pairs, decisions, strict=True) if decision["decision"] == "unresolved"
        for key in pair
    }
    shared = placeholders.intersection(other_outcomes) if placeholders else set()
    separated = defaultdict(set)
    for number, ((left, right), decision) in enumerate(zip(pairs, decisions, strict=True)):
        kind = decision["decision"]
        label = f"decision {number} ({kind})"
        if kind == "same":
            if outcomes[left] != outcomes[right]:
                raise CompositionError(f"{label} keys are not joined")
            continue
        if roots[left] == roots[right]:
            raise CompositionError(f"{label} keys are connected through same decisions")
        if kind == "different":
            if outcomes[left] == outcomes[right]:
                raise CompositionError(f"{label} keys end joined")
        else:
            for position, key in enumerate((left, right)):
                if outcomes[key] != scalar_key(decision["placeholders"][position]):
                    raise CompositionError(f"{label} key {position} does not take its placeholder")
                outcome = keys[key]["object_type"], outcomes[key]
                if outcome in shared or len(joined[outcome]) != 1:
                    raise CompositionError(f"{label} key {position} has a shared placeholder")
        if scalar_key(keys[left]["value"]) == scalar_key(keys[right]["value"]):
            separated[left].add(right)
            separated[right].add(left)

    # Sorting is stable, so each type keeps manifest/fact/row/role order.
    for _, group in sorted(joined.items(), key=lambda item: (item[0][0], item[1][0])):
        first = group[0]
        if all(keys[i]["source"] == keys[first]["source"] for i in group):
            continue
        for second in group[1:]:
            if roots[first] != roots[second]:
                raise _pair_refusal(keys[first], keys[second], "are joined without a same decision")
    for _, group in sorted(spelling.items(), key=lambda item: (item[0][0], item[1][0])):
        counts = Counter(outcomes[i] for i in group)
        if len(counts) == 1:
            continue
        for first in group:
            # Each spelling appears at most once per source/type. A count
            # identifies an incomplete group without enumerating its pairs.
            if len(separated[first]) < len(group) - counts[outcomes[first]]:
                second = next(i for i in group if outcomes[i] != outcomes[first] and i not in separated[first])
                raise _pair_refusal(keys[first], keys[second], "end apart without a different or unresolved decision")
