"""Read-only consolidation signals for one validated conceptual model."""

import re
import unicodedata
from collections import defaultdict
from itertools import combinations

from gnd.artifacts import canonical_json_bytes, sha256_hex
from gnd.model._validation import _PLACEHOLDER
from gnd.model_index import ModelIndex
from gnd.refscheme import role_player_signature
from gnd.values import identity_key


def _digest(value):
    return sha256_hex(canonical_json_bytes(value, exact_numbers=True))


def _tokens(name):
    """Lexical tokens with Unicode case and word boundaries for model names."""
    name = unicodedata.normalize("NFC", name)
    pieces = []
    for i, ch in enumerate(name):
        if (
            i
            and ch.isupper()
            and (
                name[i - 1].islower()
                or name[i - 1].isdigit()
                or (name[i - 1].isupper() and name[i + 1 : i + 2].islower())
            )
        ):
            pieces.append(" ")
        pieces.append(ch)
    separated = "".join(pieces)
    return re.findall(r"[^\W_]+", separated.casefold())


_UNITS = frozenset(
    [
        "ms",
        "sec",
        "seconds",
        "minutes",
        "hours",
        "days",
        "km",
        "cm",
        "mm",
        "meters",
        "metres",
        "miles",
        "kg",
        "mg",
        "grams",
        "kilograms",
        "bytes",
        "kb",
        "mb",
        "gb",
        "tb",
        "kelvin",
        "celsius",
        "fahrenheit",
        "percent",
        "percentage",
        "usd",
        "eur",
        "gbp",
        "liters",
        "litres",
        "ml",
        "hz",
        "khz",
        "mhz",
        "ghz",
    ]
)


class _Limit(Exception):
    """A discovery ceiling has been reached."""


def _locations(provenance, charge):
    """Collect only locations from arbitrary authored provenance metadata."""
    if not isinstance(provenance, dict):
        return [], {}

    def located(span):
        if not isinstance(span, dict):
            return None
        keys = ("document_sha256", "start", "end", "excerpt_sha256")
        if not (
            all(
                isinstance(span.get(key), str) and re.fullmatch(r"[a-f0-9]{64}", span[key])
                for key in (keys[0], keys[3])
            )
            and type(span.get("start")) is int
            and type(span.get("end")) is int
            and 0 <= span["start"] < span["end"]
        ):
            return None
        return {key: span[key] for key in keys}

    spans = provenance.get("spans")
    rows = provenance.get("sample_spans")
    charge(
        "items",
        (len(spans) if isinstance(spans, list) else 0)
        + (len(rows) if isinstance(rows, list) else 0),
    )
    return (
        sorted((s for v in spans if (s := located(v))), key=canonical_json_bytes)
        if isinstance(spans, list)
        else [],
        {
            entry["row"]: s
            for entry in rows
            if isinstance(entry, dict)
            and type(entry.get("row")) is int
            and (s := located(entry.get("span")))
        }
        if isinstance(rows, list)
        else {},
    )


def _reading_shape(reading, players, spans_by_object):
    slots = iter(players)

    def replace(_match):
        player = next(slots)
        return "{}" if len(spans_by_object.get(player, ())) == 1 else "{" + player + "}"

    return " ".join(
        unicodedata.normalize("NFC", _PLACEHOLDER.sub(replace, reading)).casefold().split()
    )


def discover_candidates(model, *, max_items=100_000, max_pairs=25_000):
    """Return deterministic groups, provenance and explicit charged work."""
    if min(max_items, max_pairs) < 0:
        raise ValueError("discovery budgets must be nonnegative")
    work = {"items": 0, "pairs": 0}
    limits = {"items": max_items, "pairs": max_pairs}
    groups = []

    def charge(kind, amount=1):
        if amount > limits[kind] - work[kind]:
            raise _Limit(kind)
        work[kind] += amount

    evidence = {}
    spans_by_object = {}
    object_locations = {}
    observed = defaultdict(set)
    observations = defaultdict(list)
    buckets = defaultdict(list)
    name_index = defaultdict(list)
    labels = {}

    def emit(signal, kind, ids, score):
        members = sorted(ids)
        items = []
        for identifier in members:
            item = evidence[kind, identifier]
            charge(
                "items",
                1
                + sum(len(item.get(field, ())) for field in ("spans", "samples", "observations"))
                + sum(map(len, item.get("player_spans", {}).values())),
            )
            items.append(item)
        groups.append(
            {
                "signal": signal,
                "kind": kind,
                "members": members,
                "score": score,
                "group_id": _digest([signal, kind, members]),
                "evidence_sha256": _digest(items),
                "evidence": items,
            }
        )

    def name_entry(kind, identifier, tokens):
        label = "".join(tokens)
        if not label:
            return
        charge("items", len(label))
        grams = {label[i : i + 3] for i in range(max(1, len(label) - 2))}
        labels[kind, identifier] = grams
        for gram in sorted(grams):
            charge("items")
            name_index[kind, gram].append(identifier)

    try:
        charge("items")
        index = ModelIndex.for_model(model)
        objects = index.object_types_by_id()
        role_maps = index.role_object_types()
        facts = {fact["id"]: fact for fact in index.iter_fact_types_shared()}
        foreign = {
            row.element_id for row in model._provenance if row.origin != "model" and row.element_id
        }
        for kind, elements in (("object", objects), ("fact", facts)):
            for identifier, element in sorted(elements.items()):
                charge("items")
                provenance = element.get("provenance") or {}
                spans, sample_spans = _locations(provenance, charge)
                if kind == "object":
                    object_locations[identifier] = spans
                    spans_by_object[identifier] = {
                        span["document_sha256"] for span in spans if "document_sha256" in span
                    }
                else:
                    roles = role_maps[identifier]
                    sample_evidence = []
                    for i, row in enumerate(element.get("sample_population") or []):
                        charge("items", 1 + len(roles))
                        row_evidence = {"row": i, "span": sample_spans.get(i)}
                        sample_evidence.append(row_evidence)
                        for key, player in roles.items():
                            if key in row and objects.get(player, {}).get("kind") == "entity":
                                observed[player].add(identity_key(row[key]))
                                observations[player].append(
                                    {"fact": identifier, "role": key, **row_evidence}
                                )
                if identifier in foreign:
                    continue
                name = element.get("name") or identifier
                tokens = _tokens(name)
                item = {"id": identifier, "name": name, "spans": spans}
                evidence[kind, identifier] = item
                name_entry(kind, identifier, tokens)
                if kind == "object":
                    reference = element.get("reference") or {}
                    if (
                        element.get("kind") == "value" or reference.get("mode") == "unit-based"
                    ) and tokens:
                        primitive = index.primitive(identifier, variant="strict")
                        item["primitive"] = primitive
                        if reference.get("mode") == "unit-based":
                            item["unit"] = reference["unit"]
                            item["measure_type"] = reference["measure_type"]
                            buckets["unit", kind, (primitive, reference["measure_type"])].append(
                                identifier
                            )
                        elif len(tokens) > 1 and tokens[-1] in _UNITS:
                            item["unit"] = tokens[-1]
                            buckets["unit", kind, (primitive, tuple(tokens[:-1]))].append(
                                identifier
                            )
                        for marker in ("count", "counts"):
                            if marker in tokens and len(tokens) > 1:
                                position = tokens.index(marker)
                                noun = position - 1 if position else len(tokens) - 1
                                item["counted_noun"] = tokens[noun]
                                frame = tuple(tokens[:noun] + ["{}"] + tokens[noun + 1 :])
                                buckets["counted-noun", kind, (primitive, frame)].append(identifier)
                                break
                    continue
                roles = role_maps[identifier]
                players = tuple(roles.values())
                item["role_players"] = players
                charge(
                    "items", sum(len(object_locations.get(player, ())) for player in set(players))
                )
                item["player_spans"] = {
                    player: object_locations.get(player, []) for player in sorted(set(players))
                }
                item["reading"] = element["reading"]
                buckets["role-players", kind, role_player_signature(roles)].append(identifier)
                shape = _reading_shape(element["reading"], players, spans_by_object)
                buckets["reading-shape", kind, shape].append(identifier)
                item["samples"] = sorted(sample_evidence, key=canonical_json_bytes)
        for identifier, values in sorted(observed.items()):
            if len(values) == 1 and ("object", identifier) in evidence:
                evidence["object", identifier]["observations"] = sorted(
                    observations[identifier], key=canonical_json_bytes
                )
                emit("singleton", "object", [identifier], 100)
        for (signal, kind, _), ids in buckets.items():
            if len(ids) < 2:
                continue
            qualifier = {"unit": "unit", "counted-noun": "counted_noun"}.get(signal)
            if qualifier and len({evidence[kind, member][qualifier] for member in ids}) < 2:
                continue
            emit(signal, kind, ids, 90)
        compared = set()
        for (kind, _), ids in sorted(name_index.items()):
            for a, b in combinations(ids, 2):
                charge("items")
                pair = kind, a, b
                if pair in compared:
                    continue
                charge("pairs")
                compared.add(pair)
                left, right = labels[kind, a], labels[kind, b]
                charge("items", min(len(left), len(right)))
                ratio = 2 * len(left & right) / (len(left) + len(right))
                if ratio >= 0.85:
                    emit("near-name", kind, [a, b], round(100 * ratio))
    except _Limit as error:
        reason = str(error) + "-limit"
    else:
        reason = "complete"
    return {
        "schema_version": 1,
        "complete": reason == "complete",
        "reason": reason,
        "work": work,
        "groups": sorted(groups, key=lambda g: (-g["score"], g["group_id"])),
    }
