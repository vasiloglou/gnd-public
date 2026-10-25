"""Candidate generation and the suppression catalogue (IK4 spec §6).

Generation order is the emission order: families in ``FAMILIES`` order, then
fact types and roles in model declaration order. Set-comparison pairs are
enumerated by object type in declaration order, then ``(fact type, role)`` in
declaration order (corpus finding C-F5). ``--max-pairs`` counts unordered pairs,
each yielding both subsets, one equality and one exclusion (C-F3).
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any

from gnd.discover.support import (
    PopulationView,
    Role,
    Subjects,
    cell_key,
    equality_subjects,
    exclusion_subjects,
    subset_subjects,
)
from gnd.model_index import ModelIndex

FAMILIES = ("uniqueness", "mandatory", "value", "frequency", "subset", "equality", "exclusion")
SET_FAMILIES = ("subset", "equality", "exclusion")
FULL_KEY_ARITY = 4  # IK4-D4

#: Catalogue rule ids, in precedence order: a candidate matching several rows is
#: counted under the first (C-F4).
CATALOGUE = (
    "declared",
    "equality-implies-subset",
    "frequency-max-1-is-uniqueness",
    "unscoped-value-implies-scoped",
    "reference-scheme-implies-uniqueness",
    "spanning-uniqueness",
    "superkey",
)
#: Candidate-against-candidate counters (spec §6; C-F2 names the frequency one).
REDUNDANCY = ("redundant-subset", "redundant-frequency", "redundant-superkey")


@dataclass
class Candidate:
    family: str
    host: str | None  # fact-type id for inline families; None at top level
    core: dict[str, Any]
    subjects: Subjects | None = None
    spanning: bool = False

    @property
    def key(self) -> tuple[Any, ...]:
        return canonical_key(self.family, self.host, self.core)


def _seq(seq: Any) -> tuple[tuple[str, str], ...]:
    if not isinstance(seq, list):
        return ()
    return tuple(
        (str(ref.get("fact_type")), str(ref.get("role"))) for ref in seq if isinstance(ref, dict)
    )


def _bound(core: dict[str, Any]) -> tuple[Any, Any]:
    bound = core.get("bound") if isinstance(core.get("bound"), dict) else {}
    return bound.get("min"), bound.get("max")


def canonical_key(family: str, host: str | None, core: dict[str, Any]) -> tuple[Any, ...]:
    """Identity for the ``declared`` row: same family, roles, sides, bound or values."""
    if family == "uniqueness":
        return ("uniqueness", host, frozenset(ModelIndex.constraint_roles(core)))
    if family == "mandatory":
        return ("mandatory", host, core.get("role"))
    if family == "value":
        ref = core.get("role_ref") if isinstance(core.get("role_ref"), dict) else None
        allowed = core.get("allowed") if isinstance(core.get("allowed"), list) else []
        scope = (ref.get("fact_type"), ref.get("role")) if ref else None
        return ("value", core.get("object_type"), scope, frozenset(cell_key(v) for v in allowed))
    if family == "frequency":
        return ("frequency", host, frozenset(ModelIndex.constraint_roles(core)), *_bound(core))
    if family == "subset":
        return ("subset", _seq(core.get("subset_role_seq")), _seq(core.get("superset_role_seq")))
    if family in ("equality", "exclusion"):
        sides = frozenset((_seq(core.get("role_seq_a")), _seq(core.get("role_seq_b"))))
        return (family, sides)
    return (family, host, repr(sorted(core.items())))


def _ref(role: Role) -> dict[str, str]:
    return {"fact_type": role.fact_type, "role": role.name}


@dataclass
class Generated:
    candidates: list[Candidate]
    skipped_value_roles: int
    skipped_key_subsets: int
    skipped_pairs: dict[str, int]
    redundant_frequency: int


def generate(
    view: PopulationView,
    *,
    families: tuple[str, ...],
    fact_types: list[str],
    max_values: int,
    max_pairs: int,
) -> Generated:
    """Every candidate core, in emission order. ``fact_types`` are the eligible ones."""
    out: list[Candidate] = []
    skipped_value_roles = skipped_key_subsets = redundant_frequency = 0
    if "uniqueness" in families:
        for ft in fact_types:
            names = [role.name for role in view.roles[ft]]
            arity = len(names)
            sizes = range(1, arity) if arity <= FULL_KEY_ARITY else range(1, 3)
            for size in sizes:
                for roles in combinations(names, size):
                    out.append(Candidate("uniqueness", ft, {"type": "uniqueness", "roles": list(roles)}))
            if arity > FULL_KEY_ARITY:
                skipped_key_subsets += 2**arity - 2 - arity - arity * (arity - 1) // 2
            if arity:
                out.append(
                    Candidate("uniqueness", ft, {"type": "uniqueness", "roles": names}, spanning=True)
                )
    if "mandatory" in families:
        for ft in fact_types:
            for role in view.roles[ft]:
                out.append(Candidate("mandatory", ft, {"type": "mandatory", "role": role.name}))
    if "value" in families:
        for ft in fact_types:
            for role in view.roles[ft]:
                allowed, occurrences = view.value_domain(role)
                if not allowed:
                    continue
                if len(allowed) > max_values:
                    skipped_value_roles += 1
                    continue
                core = {
                    "type": "value",
                    "object_type": role.object_type,
                    "role_ref": _ref(role),
                    "allowed": allowed,
                }
                ids = [view.fact_id(ft, index) for index in occurrences]
                out.append(
                    Candidate(
                        "value", ft, core,
                        Subjects(len(ids), 0, tuple(ids[:256]), ()),
                    )
                )
    if "frequency" in families:
        for ft in fact_types:
            for role in view.roles[ft]:
                counts, first = view.groups(role)
                if not counts:
                    continue
                lo, hi = min(counts.values()), max(counts.values())
                if hi == 1:
                    redundant_frequency += 1  # the uniqueness, never a frequency
                    continue
                bound = {"max": hi} if lo == 1 else {"min": lo, "max": hi}
                core = {"type": "frequency", "scope": "internal", "roles": [role.name], "bound": bound}
                ids = [view.fact_id(ft, index) for index in first.values()]
                out.append(
                    Candidate("frequency", ft, core, Subjects(len(ids), 0, tuple(ids[:256]), ()))
                )
    skipped_pairs: dict[str, int] = {}
    wanted = [family for family in SET_FAMILIES if family in families]
    if wanted:
        pairs: list[tuple[Role, Role]] = []
        for object_type in view.object_type_ids:
            played = [
                role for ft in fact_types for role in view.roles[ft]
                if role.object_type == object_type
            ]
            for a, b in combinations(played, 2):
                if a.fact_type == b.fact_type:
                    continue
                if len(pairs) < max_pairs:
                    pairs.append((a, b))
                else:
                    skipped_pairs[object_type] = skipped_pairs.get(object_type, 0) + 1
        subsets: list[Candidate] = []
        equalities: list[Candidate] = []
        exclusions: list[Candidate] = []
        for a, b in pairs:
            view.charge_pair(a, b)
            side_a, side_b = view.side(a), view.side(b)
            if "subset" in wanted:
                for sub, sup, s_sub, s_sup in ((a, b, side_a, side_b), (b, a, side_b, side_a)):
                    core = {
                        "type": "subset",
                        "subset_role_seq": [_ref(sub)],
                        "superset_role_seq": [_ref(sup)],
                    }
                    subsets.append(Candidate("subset", None, core, subset_subjects(s_sub, s_sup)))
            pair_core = {"role_seq_a": [_ref(a)], "role_seq_b": [_ref(b)]}
            if "equality" in wanted:
                equalities.append(
                    Candidate("equality", None, {"type": "equality", **pair_core},
                              equality_subjects(side_a, side_b))
                )
            if "exclusion" in wanted:
                exclusions.append(
                    Candidate("exclusion", None, {"type": "exclusion", **pair_core},
                              exclusion_subjects(side_a, side_b))
                )
        out.extend(subsets + equalities + exclusions)
    return Generated(out, skipped_value_roles, skipped_key_subsets, skipped_pairs, redundant_frequency)


class Catalogue:
    """The closed, modality-blind suppression catalogue over declared constraints."""

    def __init__(self, view: PopulationView, model: Any) -> None:
        index = ModelIndex.for_model(model)
        self.declared: set[tuple[Any, ...]] = set()
        self.equalities: set[frozenset[tuple[tuple[str, str], ...]]] = set()
        self.frequency_max_1: set[tuple[str | None, frozenset[str]]] = set()
        self.unscoped_values: list[tuple[Any, frozenset[str]]] = []
        self.uniqueness: list[tuple[str | None, frozenset[str]]] = []
        for _, constraint, fact_type in index.iter_constraints():
            if not isinstance(constraint, dict):
                continue
            family = str(constraint.get("type"))
            host = str(fact_type.get("id")) if isinstance(fact_type, dict) else None
            self.declared.add(canonical_key(family, host, constraint))
            roles = frozenset(ModelIndex.constraint_roles(constraint))
            if family == "equality":
                self.equalities.add(
                    frozenset((_seq(constraint.get("role_seq_a")), _seq(constraint.get("role_seq_b"))))
                )
            elif family == "frequency" and _bound(constraint)[1] == 1:
                self.frequency_max_1.add((host, roles))
            elif family == "uniqueness":
                self.uniqueness.append((host, roles))
            elif family == "value" and constraint.get("role_ref") is None:
                allowed = constraint.get("allowed")
                if isinstance(allowed, list):
                    self.unscoped_values.append(
                        (constraint.get("object_type"), frozenset(cell_key(v) for v in allowed))
                    )
        objects = index.object_types_by_id()
        self.reference_keys: set[tuple[Any, ...]] = set()
        for ft, roles in view.roles.items():
            if len(roles) != 2:
                continue
            for entity, value in ((roles[0], roles[1]), (roles[1], roles[0])):
                reference = (objects.get(entity.object_type) or {}).get("reference")
                if isinstance(reference, dict) and reference.get("value_type") == value.object_type:
                    self.reference_keys.update({
                        ("uniqueness", ft, frozenset({entity.name})),
                        ("uniqueness", ft, frozenset({value.name})),
                        ("mandatory", ft, entity.name),
                    })

    def rule(self, candidate: Candidate) -> str | None:
        """The first catalogue row that suppresses ``candidate``, or None."""
        key = candidate.key
        roles = frozenset(ModelIndex.constraint_roles(candidate.core))
        if key in self.declared:
            return "declared"
        if candidate.family == "subset":
            sides = frozenset(
                (_seq(candidate.core["subset_role_seq"]), _seq(candidate.core["superset_role_seq"]))
            )
            if sides in self.equalities:
                return "equality-implies-subset"
        if candidate.family == "uniqueness" and (candidate.host, roles) in self.frequency_max_1:
            return "frequency-max-1-is-uniqueness"
        if candidate.family == "value":
            allowed = frozenset(cell_key(v) for v in candidate.core["allowed"])
            for object_type, declared in self.unscoped_values:
                if object_type == candidate.core["object_type"] and allowed >= declared:
                    return "unscoped-value-implies-scoped"
        if key in self.reference_keys:
            return "reference-scheme-implies-uniqueness"
        if candidate.spanning:
            return "spanning-uniqueness"
        if candidate.family == "uniqueness":
            for host, declared in self.uniqueness:
                if host == candidate.host and declared < roles:
                    return "superkey"
        return None


def redundancy(emitted: list[Candidate]) -> tuple[list[Candidate], dict[str, int]]:
    """Candidate-against-candidate rules, applied after admission, in spec order."""
    counts = {"redundant-subset": 0, "redundant-superkey": 0}
    equal_sides = {
        frozenset((_seq(c.core["role_seq_a"]), _seq(c.core["role_seq_b"])))
        for c in emitted if c.family == "equality"
    }
    keys: dict[str | None, list[frozenset[str]]] = {}
    for c in emitted:
        if c.family == "uniqueness":
            keys.setdefault(c.host, []).append(frozenset(ModelIndex.constraint_roles(c.core)))
    kept: list[Candidate] = []
    for c in emitted:
        if c.family == "subset":
            sides = frozenset((_seq(c.core["subset_role_seq"]), _seq(c.core["superset_role_seq"])))
            if sides in equal_sides:
                counts["redundant-subset"] += 1
                continue
        if c.family == "uniqueness":
            roles = frozenset(ModelIndex.constraint_roles(c.core))
            if any(other < roles for other in keys.get(c.host, [])):
                counts["redundant-superkey"] += 1
                continue
        kept.append(c)
    return kept, counts
