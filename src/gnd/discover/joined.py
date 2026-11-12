"""Bounded discovery of guards over a binary relation and classifier."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass
from itertools import islice, permutations, product
from typing import Any

from gnd import input_policy
from gnd.atoms import atom_bind
from gnd.discover.candidates import Candidate
from gnd.discover.support import Identity, PopulationView, Role, _subjects, identity, json_native
from gnd.popvalidate import _PRIMITIVE_PREDICATES

FAMILY = "guarded-join"
MAX_WORK = 1_000_000
DEFAULT_PAIRS = 256
Coordinates = tuple[str, str, str]


@dataclass(frozen=True, slots=True)
class Settings:
    relation: Coordinates
    classifier: Coordinates
    marker: Coordinates | None
    marker_value: Any
    max_pairs: int


class Refused(ValueError):
    """An unavailable joined family with a closed report reason."""


@dataclass(slots=True)
class Work:
    visits: int = 0

    def charge(self, count: int = 1) -> None:
        if self.visits + count > MAX_WORK:
            raise Refused("work-limit")
        self.visits += count


def require_family(families: tuple[str, ...], settings: Settings | None) -> None:
    """The joined family and its explicit selectors must travel together."""
    if (FAMILY in families) != (settings is not None):
        raise ValueError("guarded-join needs both family selection and joined selectors")


def matches_counterexamples(view, settings, counterexamples, offending):
    """Check the reported row IDs against independently produced checker bindings."""
    fact, source_name, target_name = settings.relation
    roles = {role.name: role for role in view.roles[fact]}
    source, target = roles[source_name], roles[target_name]
    witnessed = {
        (identity(binding["$a"], source.primitive), identity(binding["$b"], target.primitive))
        for binding in offending
        if isinstance(binding, dict) and "$a" in binding and "$b" in binding
    }
    rows = view.population.facts[fact]
    for ref in counterexamples:
        position = int(ref.rsplit("#", 1)[1])
        row = rows[position]
        key = (
            identity(row[source_name], source.primitive),
            identity(row[target_name], target.primitive),
        )
        if key not in witnessed:
            return False
    return True


def _coordinates(value: str) -> Coordinates:
    parts = value.split(":")
    if len(parts) != 3 or not all(parts):
        raise ValueError("joined coordinates need FACT:ROLE:ROLE")
    return parts[0], parts[1], parts[2]


def _literal(value: Any) -> bool:
    return json_native(value) and not (isinstance(value, str) and value.startswith("$"))


def configure(
    relation: str, classifier: str, marker: str | None, max_pairs: int | None
) -> Settings:
    coordinates, value = None, None
    if marker is not None:
        marker_roles, separator, raw = marker.partition("=")
        if not separator or len(raw) > 4096:
            raise ValueError("--joined-marker needs FACT:ENTITY:VALUE=JSON with a bounded scalar")
        coordinates = _coordinates(marker_roles)
        try:
            value = input_policy.loads(raw)
        except (ValueError, RecursionError):
            raise ValueError("--joined-marker needs a JSON scalar") from None
        if not _literal(value):
            raise ValueError("--joined-marker needs a JSON scalar without a reserved dollar prefix")
    return Settings(
        _coordinates(relation),
        _coordinates(classifier),
        coordinates,
        value,
        DEFAULT_PAIRS if max_pairs is None else max_pairs,
    )


def _roles(view: PopulationView, coordinates: Coordinates, eligible, redacted):
    fact, first, second = coordinates
    if fact not in eligible:
        raise Refused("ineligible-fact-type")
    if fact not in view.population.covers:
        raise Refused("uncovered-fact-type")
    roles = {role.name: role for role in view.roles.get(fact, ())}
    if len(roles) != 2 or first == second or first not in roles or second not in roles:
        raise Refused("invalid-binary-roles")
    if (fact, first) in redacted or (fact, second) in redacted:
        raise Refused("redacted-role")
    return roles[first], roles[second]


def _rows(view: PopulationView, roles: tuple[Role, Role], work: Work):
    first, second = roles
    # Charge before copying or inspecting the rows.
    rows = view.population.facts.get(first.fact_type, ())
    work.charge(len(rows))
    for position, row in enumerate(rows):
        left, right = row[first.name], row[second.name]
        a, b = identity(left, first.primitive), identity(right, second.primitive)
        if a is None or b is None:
            raise Refused("opaque-or-unrepresentable-row")
        yield view.fact_id(first.fact_type, position), a, b, right


def _atom(roles: tuple[Role, Role], first: Any, second: Any) -> dict[str, Any]:
    a, b = roles
    return {"fact_type": a.fact_type, "bind": {a.name: first, b.name: second}}


def guard_key(core: dict[str, Any]) -> str | None:
    """Identity of a joined candidate shape, modulo variable names and atom order."""
    antecedent = core.get("antecedent") or ()
    consequent = core.get("consequent") or {}
    kind = next(iter(consequent), "")
    if len(antecedent) not in (2, 3) or kind not in {"atom", "absence"}:
        return None

    def signature(order):
        names: dict[str, int] = {}

        def term_key(term):
            if isinstance(term, str) and term.startswith("$"):
                return ("var", names.setdefault(term, len(names)))
            return ("literal", identity(term, None))

        def atom_key(atom):
            return atom["fact_type"], [
                (role, term_key(term)) for role, term in sorted(atom_bind(atom).items())
            ]

        canonical = [[atom_key(atom) for atom in order], kind, atom_key(consequent[kind])]
        return json.dumps(canonical, ensure_ascii=False, separators=(",", ":"))

    return min(signature(order) for order in permutations(antecedent))


def _candidate(antecedent, consequent, order):
    core = {"type": "guarded", "antecedent": antecedent, "consequent": consequent}
    key = guard_key(core)
    assert key is not None
    core["id"] = "gj_" + hashlib.sha256(key.encode()).hexdigest()[:24]
    return Candidate(FAMILY, None, core, _subjects(order))


def _generate(view, settings, eligible, redacted, work, metadata):
    relation = _roles(view, settings.relation, eligible, redacted)
    classifier = _roles(view, settings.classifier, eligible, redacted)
    marker = None if settings.marker is None else _roles(view, settings.marker, eligible, redacted)
    if (
        relation[0].fact_type == classifier[0].fact_type
        or relation[0].object_type != classifier[0].object_type
        or relation[1].object_type != classifier[0].object_type
        or (marker and marker[0].object_type != classifier[0].object_type)
    ):
        raise Refused("incompatible-join-roles")

    class_values: dict[Identity, Any] = {}
    memberships: dict[Identity, set[Identity]] = defaultdict(set)
    for _, member, category, raw in _rows(view, classifier, work):
        if not _literal(raw):
            raise Refused("unrepresentable-class-literal")
        class_values.setdefault(category, raw)
        memberships[member].add(category)

    marked = set()
    if marker is not None:
        primitive = marker[1].primitive
        predicate = _PRIMITIVE_PREDICATES.get(primitive)
        if predicate is None or not predicate(settings.marker_value):
            raise Refused("invalid-marker-value")
        marker_key = identity(settings.marker_value, primitive)
        if marker_key is None:
            raise Refused("invalid-marker-value")
        marked = {
            member for _, member, value, _ in _rows(view, marker, work) if value == marker_key
        }

    def classify(entity):
        categories = memberships.get(entity)
        if not categories:
            raise Refused("missing-classification")
        if len(categories) != 1:
            raise Refused("ambiguous-classification")
        return next(iter(categories))

    outgoing = defaultdict(list)
    same = []
    seen = set()
    for ref, source, target, _ in _rows(view, relation, work):
        if (source, target) in seen:
            continue
        seen.add((source, target))
        origin, destination = classify(source), classify(target)
        outgoing[origin].append((ref, destination))
        if marker is None or target in marked:
            same.append((ref, origin != destination))

    edge = _atom(relation, "$a", "$b")
    classes = sorted(class_values)
    pairs = product(sorted(outgoing), classes)
    total_pairs = len(outgoing) * len(classes)
    compared = min(settings.max_pairs, total_pairs)
    metadata.update(omitted=total_pairs, first_omitted_ordinal=0 if total_pairs else None)
    candidates = []
    for origin, destination in islice(pairs, compared):
        rows = outgoing[origin]
        work.charge(1 + len(rows))
        candidates.append(
            _candidate(
                [edge, _atom(classifier, "$a", class_values[origin])],
                {"absence": _atom(classifier, "$b", class_values[destination])},
                [(ref, category == destination) for ref, category in rows],
            )
        )
        metadata["compared"] += 1
        metadata["omitted"] -= 1
        metadata["first_omitted_ordinal"] = metadata["compared"] if metadata["omitted"] else None
    if same:
        work.charge(1 + len(same))
        antecedent = [edge, _atom(classifier, "$b", "$k")]
        if marker is not None:
            antecedent.append(_atom(marker, "$b", settings.marker_value))
        candidates.append(_candidate(antecedent, {"atom": _atom(classifier, "$a", "$k")}, same))
    return candidates


def generate(view, settings: Settings, *, eligible, redacted):
    """Compute candidates and independent support before the discovery checker."""
    work = Work()
    metadata = {
        "reason": None,
        "compared": 0,
        "omitted": 0,
        "first_omitted_ordinal": None,
        "max_directed_pairs": settings.max_pairs,
    }
    try:
        candidates = _generate(view, settings, set(eligible), redacted, work, metadata)
    except Refused as error:
        candidates = []
        metadata["reason"] = str(error)
    return candidates, {**metadata, "work": {"visits": work.visits, "ceiling": MAX_WORK}}
