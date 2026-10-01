"""The reference-scheme multiset matcher and its four-outcome partition (PANEL-5).

An extracted population and its source population share no identifiers: the
extractor invents its own tokens, so ``person_1`` and ``p_alice`` are the same
person or not and nothing in the JSON says which. ORM already answers it — every
entity type has a reference scheme, and that is exactly what makes an entity
nameable in prose. This module matches by that scheme and by nothing else.

**Four outcomes on the extracted side, and they PARTITION.**

* ``tp`` — a fact whose identity key is present in the source multiset.
* ``unmatched`` — a WELL-RESOLVED key with no source counterpart. The false
  positive proper.
* ``unresolved`` — a role filler that resolves to no source entity (R-10's third
  outcome). Reported as its own number, never folded into precision's numerator
  and never dropped from its denominator: "we could not place it" is not the
  same claim as "it is wrong", and collapsing the two is the reporting error
  this project keeps correcting (D-02, one layer up).
* ``ambiguous`` — a normalization collision (two source entities whose reference
  values collide under ``lexical_normalize``) or a broken composite identity (a
  token appearing in only one of its external-UC join fact types). Never an
  arbitrary assignment: a matcher that picks the first colliding candidate is
  right half the time by construction and reports certainty either way.

``tp + unmatched + unresolved + ambiguous == extracted_total`` and
``tp + missed == source_total``, both raised as :class:`FidelityPartitionError`
**in production code** (``measure/score.py:341-401``'s posture) — a rate over a
broken partition reads exactly like a rate over a sound one.

**Multiset, not set.** ``tp`` per identity key is ``min(source_count,
extracted_count)``. A source stating a fact twice against an extraction finding
it once is recall 1/2, not 1/1; deduplicating first silently deletes half the
evidence from the denominator.

**Inclusive precision.** The precision denominator is every extracted fact —
matched, unmatched, unresolved and ambiguous alike. Every exclusion available
here flatters, which is why none is taken.

**No aggregation across fact types (D-01).** There is deliberately no function
in this module that folds rows together, exactly as
``measure/score.py:420-433`` refuses to fold constraints. Every number belongs
to one fact type and travels with its denominator.

**Identity is this lane's own (C1).** Keys come from
``gnd.extract.identity.identity_key`` after ``lexical_normalize`` — never from
``gnd.checker._identity_key``. The matcher is composed with the checker and
evaluated against the synthesis oracle, so it may borrow the identity of
neither.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from gnd.extract.identity import identity_key, lexical_normalize

__all__ = [
    "FactEvidence",
    "FactTypeMatch",
    "FidelityPartitionError",
    "match_case",
    "match_fact_type",
]

#: The three non-``tp`` extracted outcomes, in canonical order.
EXTRACTED_OUTCOMES = ("unmatched", "unresolved", "ambiguous")


class FidelityPartitionError(RuntimeError):
    """A matcher invariant broke: the four extracted outcomes do not sum to the
    extracted total, ``tp + missed`` does not sum to the source total, or a
    population carries a fact type the applicable-set artifact never listed.

    Raised in the production path, never merely asserted in a test. The failure
    it guards is silent by nature — dropped facts leave every rate looking
    exactly as trustworthy as before.
    """


def _rate(numerator: int, denominator: int) -> float | None:
    """A rate, or ``None`` when the denominator is zero.

    ``measure/score.py:294-303``'s rule, unchanged: a zero denominator is "no
    data", not a division error. A fact type absent from a case reports ``None``
    rather than crashing or, worse, reading as 0.0.
    """
    if denominator == 0:
        return None
    return numerator / denominator


@dataclass(frozen=True)
class FactEvidence:
    """One extracted fact paired with its actual matcher outcome."""

    outcome: str
    fact: Mapping[str, Any]


@dataclass(frozen=True)
class FactTypeMatch:
    """One fact type's matched counts for one case.

    Carries the raw counters (the partition audit trail) and exposes every rate
    beside its own numerator and denominator (R-11′) — a rate can never be read
    off this object without its base.

    ``applicable`` and ``reason`` come from the applicable-set ARTIFACT, never
    from a matcher opinion: an unmeasurable fact type gets a row carrying its
    mechanism and contributes nothing to any count (C5), so it leaves the
    denominator visibly rather than by vanishing.
    """

    fact_type_id: str
    applicable: bool
    reason: str | None
    source_total: int
    extracted_total: int
    tp: int
    missed: int
    unmatched: int
    unresolved: int
    ambiguous: int
    evidence: tuple[FactEvidence, ...] = ()

    @property
    def precision_numerator(self) -> int:
        return self.tp

    @property
    def precision_denominator(self) -> int:
        """INCLUSIVE: every extracted fact, unresolved and ambiguous ones
        included (PANEL-5)."""
        return self.extracted_total

    @property
    def recall_numerator(self) -> int:
        return self.tp

    @property
    def recall_denominator(self) -> int:
        return self.source_total

    @property
    def unresolved_numerator(self) -> int:
        return self.unresolved

    @property
    def unresolved_denominator(self) -> int:
        return self.extracted_total

    @property
    def precision(self) -> float | None:
        return _rate(self.precision_numerator, self.precision_denominator)

    @property
    def recall(self) -> float | None:
        return _rate(self.recall_numerator, self.recall_denominator)

    @property
    def unresolved_rate(self) -> float | None:
        return _rate(self.unresolved_numerator, self.unresolved_denominator)


def _multiset_true_positives(
    source_keys: Counter[Any], extracted_keys: Counter[Any]
) -> int:
    """``Σ min(source_count, extracted_count)`` over the shared keys (PANEL-5).

    The whole multiset rule lives in this one function so the set-based
    shortcut has exactly one place to be introduced — and exactly one named
    test guarding it.
    """
    return sum(
        min(count, extracted_keys[key]) for key, count in source_keys.items()
    )


class _Resolver:
    """Per-model identity resolution driven BY THE ARTIFACT's recorded path.

    Holds the model's role map (role -> object type, which the applicable-set
    artifact does not carry) and the artifact's per-object-type disposition.
    Nothing here re-derives a reference scheme: ``refscheme.applicable_set``
    already did that once, and the artifact is what the renderer, doccheck and
    this matcher were all given.
    """

    def __init__(self, model: Any, applicable: Mapping[str, Any]) -> None:
        self.object_rows: dict[str, dict[str, Any]] = {
            str(row["id"]): dict(row) for row in applicable["object_types"]
        }
        self.fact_rows: dict[str, dict[str, Any]] = {
            str(row["id"]): dict(row) for row in applicable["fact_types"]
        }
        self.roles: dict[str, list[tuple[str, str]]] = {}
        for fact_type in model.fact_types:
            self.roles[str(fact_type.get("id"))] = [
                (str(role.get("role_name")), str(role.get("object_type")))
                for role in fact_type.get("roles") or []
            ]
        self.kinds: dict[str, str] = {
            str(object_type.get("id")): str(object_type.get("kind"))
            for object_type in model.object_types
        }

    # -- source-side indices ------------------------------------------------ #

    def index(self, facts: Mapping[str, Sequence[Mapping[str, Any]]]) -> _SourceIndex:
        """The identity index of a SOURCE population: which entity identities
        exist, and which of them are indistinguishable from each other."""
        direct: dict[str, dict[Any, set[str]]] = {}
        composite: dict[str, dict[Any, set[str]]] = {}

        for fact_type_id, fact_list in facts.items():
            for role_name, object_type_id in self.roles.get(fact_type_id, []):
                row = self.object_rows.get(object_type_id) or {}
                if self.kinds.get(object_type_id) != "entity":
                    continue
                for fact in fact_list:
                    if role_name not in fact:
                        continue
                    filler = fact[role_name]
                    if row.get("path") == "direct":
                        bucket = direct.setdefault(object_type_id, {})
                        bucket.setdefault(identity_key(filler), set()).add(repr(filler))
                    elif row.get("path") == "composite":
                        joined = self._join_composite(object_type_id, filler, facts)
                        if joined is None:
                            continue
                        bucket = composite.setdefault(object_type_id, {})
                        bucket.setdefault(joined, set()).add(repr(filler))
        return _SourceIndex(direct=direct, composite=composite)

    # -- per-role resolution ------------------------------------------------ #

    def _join_composite(
        self,
        object_type_id: str,
        filler: Any,
        facts: Mapping[str, Sequence[Mapping[str, Any]]],
    ) -> tuple[Any, ...] | None:
        """The component tuple identifying a composite token, joined WITHIN one
        population through the external UC's ``role_refs`` (PANEL-5).

        The surrogate token itself is meaningless across populations —
        RESEARCH verified ``assignment-64ac5db9`` joins to ``(140891,
        "glass")``, and that tuple is the identity. ``None`` when the token
        cannot complete its tuple: it appears in only one of its join fact
        types, or in none, or its component is itself not directly
        referenceable. Every such case is ``ambiguous`` at the call site — a
        fallback to the raw token would match the extractor's own invented
        identifier against the generator's.
        """
        row = self.object_rows.get(object_type_id) or {}
        anchor = identity_key(filler)
        components: list[Any] = []
        for role_ref in row.get("role_refs") or []:
            if role_ref.get("path") != "direct":
                # A composite whose component is itself composite: no ground
                # identity is derivable in one join, so refuse rather than
                # guess (the recursion is out of scope until a model needs it).
                return None
            ref_fact_type = str(role_ref["fact_type"])
            ref_role = str(role_ref["role"])
            anchor_roles = [
                name
                for name, oid in self.roles.get(ref_fact_type, [])
                if oid == object_type_id and name != ref_role
            ]
            found = {
                identity_key(fact[ref_role])
                for fact in facts.get(ref_fact_type, [])
                for anchor_role in anchor_roles
                if anchor_role in fact
                and ref_role in fact
                and identity_key(fact[anchor_role]) == anchor
            }
            if len(found) != 1:
                return None
            components.append(next(iter(found)))
        if not components:
            return None
        return ("composite", tuple(components))

    def role_component(
        self,
        object_type_id: str,
        filler: Any,
        facts: Mapping[str, Sequence[Mapping[str, Any]]],
        index: _SourceIndex,
        *,
        resolve_against_source: bool,
    ) -> tuple[str, Any]:
        """``("ok", component) | ("unresolved", None) | ("ambiguous", None)``.

        ``resolve_against_source`` is False for source facts themselves: the
        source IS the reference set, so its own fillers are keyed, never
        classified. Classifying them would make ``tp + missed ==
        source_total`` unsatisfiable for the very populations that define the
        ground truth.
        """
        row = self.object_rows.get(object_type_id) or {}
        path = row.get("path")
        is_entity = self.kinds.get(object_type_id) == "entity"

        if path == "composite":
            joined = self._join_composite(object_type_id, filler, facts)
            if joined is None:
                return ("ambiguous", None)
            if resolve_against_source:
                bucket = index.composite.get(object_type_id, {})
                tokens = bucket.get(joined)
                if tokens is None:
                    return ("unresolved", None)
                if len(tokens) > 1:
                    return ("ambiguous", None)
            return ("ok", joined)

        key = identity_key(filler)
        if path == "unmatchable":
            # Reached only through a fact type the artifact marks applicable,
            # which cannot happen: applicability requires EVERY role's object
            # type to resolve. Refuse rather than key on an identity the
            # artifact declared underivable.
            return ("ambiguous", None)
        if resolve_against_source and is_entity:
            bucket = index.direct.get(object_type_id, {})
            raw = bucket.get(key)
            if raw is None:
                return ("unresolved", None)
            if len(raw) > 1:
                # Two DISTINCT source entities collide under lexical_normalize
                # ("Ann B" / "ann  b"): nothing in the document can say which
                # one an extraction meant (R-10 forbids anything semantic).
                return ("ambiguous", None)
        return ("ok", key)

    def fact_key(
        self,
        fact_type_id: str,
        fact: Mapping[str, Any],
        facts: Mapping[str, Sequence[Mapping[str, Any]]],
        index: _SourceIndex,
        *,
        resolve_against_source: bool,
    ) -> tuple[str, Any]:
        """``("ok", key) | ("unresolved", None) | ("ambiguous", None)`` for a
        whole fact.

        The fact identity is ``(fact_type_id, ((role, component), ...))`` over
        the roles the MODEL declares — an extracted fact missing a declared
        role has no identity to compare and is ``ambiguous``, not a partial
        match. Precedence: any ambiguous role makes the fact ambiguous, then
        any unresolved role makes it unresolved. Ambiguity outranks because
        "we cannot tell which entity" is a stronger refusal than "we found no
        entity".
        """
        components: list[tuple[str, Any]] = []
        outcome = "ok"
        for role_name, object_type_id in self.roles.get(fact_type_id, []):
            if role_name not in fact:
                return ("ambiguous", None)
            state, component = self.role_component(
                object_type_id,
                fact[role_name],
                facts,
                index,
                resolve_against_source=resolve_against_source,
            )
            if state == "ambiguous":
                return ("ambiguous", None)
            if state == "unresolved":
                outcome = "unresolved"
            components.append((role_name, component))
        if outcome != "ok":
            return (outcome, None)
        return ("ok", (fact_type_id, tuple(sorted(components, key=lambda item: item[0]))))


@dataclass(frozen=True)
class _SourceIndex:
    """Which identities the SOURCE population contains, and which of them are
    indistinguishable. ``{object_type: {identity: {raw fillers}}}`` — a bucket
    with two raw fillers is a normalization collision."""

    direct: dict[str, dict[Any, set[str]]]
    composite: dict[str, dict[Any, set[str]]]


def _assert_declared(
    label: str,
    facts: Mapping[str, Sequence[Mapping[str, Any]]],
    declared: set[str],
) -> None:
    unknown = sorted(set(facts) - declared)
    if unknown:
        raise FidelityPartitionError(
            f"the {label} population carries fact type(s) {unknown} that the "
            f"applicable-set artifact never lists, so no row can account for "
            f"them — dropping them silently would remove extractions from "
            f"every denominator while every rate kept its shape."
        )


def match_fact_type(
    fact_type_id: str,
    source_facts: Mapping[str, Sequence[Mapping[str, Any]]],
    extracted_facts: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    model: Any,
    applicable: Mapping[str, Any],
    resolver: _Resolver | None = None,
    index: _SourceIndex | None = None,
) -> FactTypeMatch:
    """Match one fact type's facts and return its counts.

    The partition is checked here, in the production path, on every row: a
    dropped or double-counted fact is invisible in the published rate, so it is
    refused at the moment it happens (:class:`FidelityPartitionError`).
    """
    resolver = resolver if resolver is not None else _Resolver(model, applicable)
    index = index if index is not None else resolver.index(source_facts)

    row = resolver.fact_rows.get(fact_type_id)
    if row is None:
        raise FidelityPartitionError(
            f"fact type {fact_type_id!r} is not listed in the applicable-set "
            f"artifact — the artifact defines the row set, and a row the "
            f"artifact never declared is unaccountable."
        )
    if not row.get("applicable"):
        # C5: out of the denominator, visible in the table, mechanism attached.
        return FactTypeMatch(
            fact_type_id=fact_type_id,
            applicable=False,
            reason=row.get("reason"),
            source_total=0,
            extracted_total=0,
            tp=0,
            missed=0,
            unmatched=0,
            unresolved=0,
            ambiguous=0,
        )

    source_list = list(source_facts.get(fact_type_id, []))
    extracted_list = list(extracted_facts.get(fact_type_id, []))

    source_keys: Counter[Any] = Counter()
    for position, fact in enumerate(source_list):
        state, key = resolver.fact_key(
            fact_type_id, fact, source_facts, index, resolve_against_source=False
        )
        # A source fact whose own identity cannot be formed still counts in the
        # source total — it simply cannot be matched, so it lands in `missed`
        # under a key nothing can collide with. Dropping it would shrink recall's
        # denominator, which is the one direction that flatters.
        source_keys[key if state == "ok" else ("unkeyable-source", position)] += 1

    extracted_keys: Counter[Any] = Counter()
    unresolved = 0
    ambiguous = 0
    classified: list[tuple[str, Any, Mapping[str, Any]]] = []
    for fact in extracted_list:
        state, key = resolver.fact_key(
            fact_type_id, fact, extracted_facts, index, resolve_against_source=True
        )
        if state == "ambiguous":
            ambiguous += 1
        elif state == "unresolved":
            unresolved += 1
        else:
            extracted_keys[key] += 1
        classified.append((state, key, fact))

    tp = _multiset_true_positives(source_keys, extracted_keys)
    source_total = len(source_list)
    extracted_total = len(extracted_list)
    # `missed` and `unmatched` are computed INDEPENDENTLY of `tp` — per-key
    # surpluses, not `total - tp`. Deriving them by subtraction would make the
    # partition an arithmetic identity that holds for ANY value of `tp`,
    # including a wrong one: the invariant would be a gate that cannot fail
    # (02-01's lesson, and the reason this phase exists). Computed this way, the
    # two checks below genuinely reconcile two routes to the same number.
    missed = sum(
        max(0, count - extracted_keys[key]) for key, count in source_keys.items()
    )
    unmatched = sum(
        max(0, count - source_keys[key]) for key, count in extracted_keys.items()
    )

    partition = tp + unmatched + unresolved + ambiguous
    if partition != extracted_total:
        raise FidelityPartitionError(
            f"{fact_type_id}: the extracted partition sums to {partition} "
            f"(tp={tp}, unmatched={unmatched}, unresolved={unresolved}, "
            f"ambiguous={ambiguous}) but {extracted_total} fact(s) were "
            f"extracted — a fact was double-counted or dropped, so precision "
            f"is computed on a denominator its reader cannot see."
        )
    if tp + missed != source_total:
        raise FidelityPartitionError(
            f"{fact_type_id}: the source partition sums to {tp + missed} "
            f"(tp={tp}, missed={missed}) but the source states {source_total} "
            f"fact(s) — recall's denominator no longer describes the evidence."
        )

    remaining_source = source_keys.copy()
    evidence: list[FactEvidence] = []
    for state, key, fact in classified:
        if state in ("unresolved", "ambiguous"):
            outcome = state
        elif remaining_source[key] > 0:
            outcome = "tp"
            remaining_source[key] -= 1
        else:
            outcome = "unmatched"
        evidence.append(FactEvidence(outcome=outcome, fact=dict(fact)))

    return FactTypeMatch(
        fact_type_id=fact_type_id,
        applicable=True,
        reason=None,
        source_total=source_total,
        extracted_total=extracted_total,
        tp=tp,
        missed=missed,
        unmatched=unmatched,
        unresolved=unresolved,
        ambiguous=ambiguous,
        evidence=tuple(evidence),
    )


def match_case(
    source_facts: Mapping[str, Sequence[Mapping[str, Any]]],
    extracted_facts: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    model: Any,
    applicable: Mapping[str, Any],
) -> list[FactTypeMatch]:
    """Every fact type the artifact declares, for one case, sorted by id.

    EVERY declared fact type contributes a row — applicable or not, populated
    or not (the census half of ``measure/score.py:393-401``): a fact type that
    simply vanishes from the table is indistinguishable from one that scored
    perfectly, and the row is where the reader sees which.

    Returns a list, not an aggregate. Nothing here folds rows together (D-01).
    """
    resolver = _Resolver(model, applicable)
    declared = set(resolver.fact_rows)
    _assert_declared("source", source_facts, declared)
    _assert_declared("extracted", extracted_facts, declared)
    index = resolver.index(source_facts)
    return [
        match_fact_type(
            fact_type_id,
            source_facts,
            extracted_facts,
            model=model,
            applicable=applicable,
            resolver=resolver,
            index=index,
        )
        for fact_type_id in sorted(declared)
    ]


# ``lexical_normalize`` is imported for the identity contract it defines with
# ``identity_key`` (normalize, THEN tag the domain) and re-exported nowhere: the
# matcher must never grow a second normalization rule beside R-10's lexical one.
_ = lexical_normalize
