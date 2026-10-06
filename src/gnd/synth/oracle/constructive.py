"""Constructive witnesses and search primitives, unchanged from assemble."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, datetime
from itertools import product
from random import Random
from typing import Any

from gnd import checker as checker_module
from gnd import popvalidate
from gnd.address import positional_constraint_ref
from gnd.model import Model
from gnd.population import Population
from gnd.synth.comparison import (
    normalize_operands as _normalize_comparison_operands,
)
from gnd.synth.comparison import role_literal_operands as _role_literal_operands
from gnd.synth.guarded import (
    exists_witness as _exists_witness,
)
from gnd.synth.identity import scalar_identity as _key
from gnd.synth.identity import tuple_identity as _tuple_key
from gnd.synth.pool import EntityPool
from gnd.synth.poolfile import Pool
from gnd.synth.value_domain import (
    EmptyValueDomain,
    draw_value_for_constraints,
    governing_value_constraints,
)


class GeneratorError(Exception):
    """A generator invariant failed and could not be repaired within budget.

    Either a constructive witness does not hold after the repair budget (the
    family is ``not-derivable`` from this generator), a re-admission
    ``PopulationValidationError``, or an oscillating repair. Exit 5 at the CLI.
    """


class _TermGenerationUnavailable(GeneratorError):
    """One generated asserted candidate made an exact derivation unavailable."""


class CheckerWitnessDiscrepancy(Exception):
    """The checker and the independent constructive witness disagree (C1).

    BOTH directions travel this one path (CR-04), distinguished by each record's
    ``kind``:

    - ``candidate-false-fail`` — the checker reported an alethic ``fail`` on a
      constraint the witness proves satisfied;
    - ``candidate-false-pass`` — the checker reported no alethic fail while the
      witness proves the constraint violated. This direction used to be a bare
      :class:`GeneratorError`: exit 5, no document, labelled ``not-derivable``.
      It is the more dangerous of the two — a checker that fails to fail — and
      destroying its only reproduction is the "defect vanishes from its own
      evaluation corpus" circularity C1 exists to close.

    Carries the population document and the typed discrepancies so the caller can
    QUARANTINE the case (retain it, never discard or relabel) and exit 6.
    """

    def __init__(self, doc: dict[str, Any], discrepancies: list[dict[str, Any]]) -> None:
        self.doc = doc
        self.discrepancies = discrepancies
        joined = "; ".join(
            f"{d['constraint_ref']} witness={d['witness']} observed={d['observed']}"
            for d in discrepancies
        )
        super().__init__(f"candidate checker false-fail(s): {joined}")


@dataclass
class Assembly:
    """A converged conforming population and its provenance for the sidecar."""

    doc: dict[str, Any]
    model: Model
    pool: Pool
    seed: int
    pool_size: int
    rounds: int
    expectations: dict[str, ExpectedStateData]
    distinct_ratios: dict[str, tuple[int, int]]
    witnesses: dict[str, bool | None] = field(default_factory=dict)


@dataclass
class ExpectedStateData:
    """Plain per-constraint expectation the CLI lifts into a typed ExpectedState."""

    ground_truth: str
    expected_verdict: str
    reason: str | None


def _object_types_by_id(model: Model) -> dict[str, dict[str, Any]]:
    return {str(ot.get("id")): ot for ot in model.object_types or [] if ot.get("id") is not None}


def _role_object(model: Model) -> dict[str, dict[str, str]]:
    return {
        str(ft.get("id")): {
            str(role.get("role_name")): str(role.get("object_type"))
            for role in ft.get("roles") or []
            if role.get("role_name") is not None and role.get("object_type") is not None
        }
        for ft in model.fact_types or []
        if ft.get("id") is not None
    }


def _direct_subtypes(model: Model) -> dict[str, set[str]]:
    children: dict[str, set[str]] = {}
    for ot in model.object_types or []:
        oid = str(ot.get("id"))
        for parent in ot.get("subtype_of") or []:
            children.setdefault(str(parent), set()).add(oid)
    return children


def _descendants(model: Model, ot_id: str, children: dict[str, set[str]]) -> set[str]:
    seen: set[str] = set()
    stack = [ot_id]
    while stack:
        node = stack.pop()
        for child in children.get(node, set()):
            if child not in seen:
                seen.add(child)
                stack.append(child)
    return seen


def _denoting_types(covered: set[str], model: Model) -> set[str]:
    """Object types whose instances are DENOTED by values of ``covered`` (F-01).

    An ORM reference scheme means an entity type's instances are denoted by
    values of its reference value type: ``population-format.md`` — *"Entity
    values in facts use the entity's reference-scheme value … ``movie: 1`` means
    the Movie whose MovieId is 1"*. So ``movie: 999999`` IS an occurrence of
    MovieId, and the closed-world universe of MovieId must contain it.

    Phase 1 closed exactly this hole in the CHECKER (F-01). The independent
    witness carried the pre-F-01 walk until plan 06 ran the generator over
    ``reference_value_type.orm.yaml`` for the first time: the witness saw ZERO
    MovieId values, returned a vacuous ``all([]) == True``, and claimed SATISFIED
    over a population whose only fact carried an out-of-range identifier. The
    checker — correctly — said ``fail``. An oracle that claims satisfaction over
    a violated ground truth publishes the checker's correct verdict as a
    FALSE FAIL: a fabricated checker defect in the report. The semantics are
    shared with the checker; this walk is written independently of it (C1).
    """
    return {
        str(object_type.get("id"))
        for object_type in model.object_types or []
        if object_type.get("id") is not None
        and str(object_type.get("id")) not in covered
        and popvalidate.resolve_reference_value_type(str(object_type.get("id")), model)
        in covered
    }


def _universe(doc: dict[str, Any], model: Model, ot_id: str, children: dict[str, set[str]]) -> list[Any]:
    """Independent closed-world instance values of ``ot_id`` (+ subtypes).

    A deliberately separate re-implementation of the checker's closed-world walk
    (C1): rosters of the type or a subtype, plus every value playing a role typed
    to the type or a subtype — AND, when ``ot_id`` is a value type, every value
    playing a role typed to an entity that value type DENOTES (F-01, see
    :func:`_denoting_types`). Duplicates preserved.
    """
    covered = {str(ot_id)} | _descendants(model, str(ot_id), children)
    covered |= _denoting_types(covered, model)
    values: list[Any] = []
    for cid in sorted(covered):
        values.extend(doc.get("instances", {}).get(cid, []))
    role_obj = _role_object(model)
    for ft in model.fact_types or []:
        ftid = str(ft.get("id"))
        typed = [rn for rn, oid in role_obj.get(ftid, {}).items() if oid in covered]
        if not typed:
            continue
        for fact in doc.get("facts", {}).get(ftid, []):
            for rn in typed:
                if rn in fact:
                    values.append(fact[rn])
    return values


def _project(doc: dict[str, Any], ft_id: str, role_names: list[str]) -> list[tuple[Any, ...]]:
    rows = []
    for fact in doc.get("facts", {}).get(str(ft_id), []):
        if all(rn in fact for rn in role_names):
            rows.append(tuple(fact[rn] for rn in role_names))
    return rows


def _join(doc: dict[str, Any], model: Model, role_refs: list[dict[str, Any]]) -> list[tuple[Any, ...]]:
    """Independent shared-anchor join over ``role_refs`` (C1 re-implementation).

    Mirrors the checker's semantics — join fact types on non-referenced roles of
    shared object type — but is written here, so a checker join bug cannot hide
    in the ground truth it is measured against.
    """
    role_obj = _role_object(model)
    by_ft: dict[str, list[tuple[int, str]]] = {}
    order: list[str] = []
    for slot, ref in enumerate(role_refs):
        ftid = str(ref.get("fact_type"))
        if ftid not in by_ft:
            by_ft[ftid] = []
            order.append(ftid)
        by_ft[ftid].append((slot, str(ref.get("role"))))

    rows: list[tuple[dict[str, Any], dict[int, Any]]] = [({}, {})]
    for ftid in order:
        ref_roles = {role for _, role in by_ft[ftid]}
        anchors = [
            (rn, oid) for rn, oid in role_obj.get(ftid, {}).items() if rn not in ref_roles
        ]
        new_rows: list[tuple[dict[str, Any], dict[int, Any]]] = []
        for anchor_vals, outputs in rows:
            for fact in doc.get("facts", {}).get(ftid, []):
                if any(rn not in fact for rn, _ in anchors):
                    continue
                if any(role not in fact for _, role in by_ft[ftid]):
                    continue
                merged = dict(anchor_vals)
                ok = True
                for rn, oid in anchors:
                    identity = _key(fact[rn])
                    if oid in merged and merged[oid] != identity:
                        ok = False
                        break
                    merged[oid] = identity
                if not ok:
                    continue
                new_out = dict(outputs)
                for slot, rn in by_ft[ftid]:
                    new_out[slot] = fact[rn]
                new_rows.append((merged, new_out))
        rows = new_rows
    return [tuple(out[slot] for slot in range(len(role_refs))) for _, out in rows]


def _seq_tuples(doc: dict[str, Any], model: Model, seq: list[dict[str, Any]]) -> list[tuple[Any, ...]]:
    ftids = {str(ref.get("fact_type")) for ref in seq}
    if len(ftids) == 1:
        ftid = next(iter(ftids))
        return _project(doc, ftid, [str(ref.get("role")) for ref in seq])
    return _join(doc, model, seq)


_CHAIN_COMPATIBLE = {
    "irreflexive",
    "asymmetric",
    "acyclic",
    "intransitive",
    "antisymmetric",
    "asymmetric-intransitive",
    "acyclic-intransitive",
}


_EXTERNAL_UNIQUENESS_SEARCH_CAP = 10_000


def _ring_satisfied(variant: str, pairs: set[tuple[Any, Any]]) -> bool:
    """Ring semantics over KEYED pairs (IN-01).

    ``pairs`` carries :func:`_tuple_key` elements, not raw values, so ``True``
    and ``1`` stay distinct here exactly as they do in ``_acyclic`` and every
    other identity in this module. Building the pair set from raw values
    collapsed them into one element, which is the inconsistency ``_key`` exists
    to prevent — and since CR-02 made this witness the SOLE source of every
    published expectation, an identity that disagrees with itself between two
    ring components is no longer a curiosity.
    """
    elements = {a for a, _ in pairs} | {b for _, b in pairs}
    components = {
        "asymmetric-intransitive": ("asymmetric", "intransitive"),
        "acyclic-intransitive": ("acyclic", "intransitive"),
        "symmetric-irreflexive": ("symmetric", "irreflexive"),
        "symmetric-intransitive": ("symmetric", "intransitive"),
    }.get(variant, (variant,))
    for component in components:
        if not _ring_component_ok(component, pairs, elements):
            return False
    return True


def _ring_component_ok(component: str, pairs: set[tuple[Any, Any]], elements: set[Any]) -> bool:
    if component == "irreflexive":
        return not any(a == b for a, b in pairs)
    if component == "asymmetric":
        return not any((b, a) in pairs for a, b in pairs)
    if component == "antisymmetric":
        return not any(a != b and (b, a) in pairs for a, b in pairs)
    if component == "symmetric":
        return all((b, a) in pairs for a, b in pairs)
    if component == "intransitive":
        return not any(
            (a, c) in pairs for a, b in pairs for b2, c in pairs if b2 == b
        )
    if component == "transitive":
        return all(
            (a, c) in pairs for a, b in pairs for b2, c in pairs if b2 == b
        )
    if component == "purely-reflexive":
        return all(a == b for a, b in pairs)
    if component == "reflexive":
        return all((a, a) in pairs for a in elements)
    if component == "acyclic":
        return _acyclic(pairs)
    return True


def _acyclic(pairs: set[tuple[Any, Any]]) -> bool:
    """``pairs`` is already KEYED by :func:`_ring_satisfied`'s caller (IN-01), so
    this walks the keys directly rather than re-keying them."""
    graph: dict[Any, set[Any]] = {}
    for a, b in pairs:
        graph.setdefault(a, set()).add(b)
        graph.setdefault(b, set())
    visiting: set[Any] = set()
    visited: set[Any] = set()

    def dfs(node: Any) -> bool:
        visiting.add(node)
        for nxt in graph.get(node, set()):
            if nxt in visiting:
                return False
            if nxt not in visited and not dfs(nxt):
                return False
        visiting.discard(node)
        visited.add(node)
        return True

    return all(node in visited or dfs(node) for node in list(graph))


_TEMPORAL_PRIMITIVES = ("Date", "DateTime")


def _ordered_pair(value: Any, bound: Any, primitive: str | None) -> tuple[Any, Any] | None:
    """``(value, bound)`` in a common ORDERED domain, or ``None`` if none exists.

    constraint-reference.md gives the family as *"one or more numeric /
    character ranges"* and ``orm-meta.schema.json`` types a bound
    ``["string", "number"]``, so exactly two domains carry a total order here:
    two numbers, and two strings (lexically — which is what makes ISO-8601 dates
    order correctly by construction). Everything else — a string against a
    numeric bound, a value against a bound of the other kind — has no order, and
    the honest answer is no claim rather than a plausible one.

    Two exclusions, each for a value that would otherwise order and order WRONGLY:

    * ``bool``. ``isinstance(True, int)`` is ``True`` in Python and ``True == 1``,
      so a boolean lands silently INSIDE a ``1..100`` range. Whether a boolean is
      a valid Integer is the loader's question, not this one's.
    * ``NaN``. Every ordered comparison involving NaN is unordered (IEEE 754-2019
      §5.11), so both ``nan < min`` and ``nan > max`` are ``False`` and a NaN
      comes out inside every range — the one unorderable value Python does not
      raise on, hence the one that needs naming.

    ``inf`` is NOT excluded: it orders totally and correctly against finite
    bounds, so declining it would trade a false claim for a needless abstention.
    """
    if isinstance(value, bool) or isinstance(bound, bool):
        return None
    if isinstance(value, (int, float)) and isinstance(bound, (int, float)):
        if any(isinstance(x, float) and math.isnan(x) for x in (value, bound)):
            return None
        return value, bound
    if isinstance(value, str) and isinstance(bound, str):
        if primitive in _TEMPORAL_PRIMITIVES:
            return _instant_pair(value, bound, primitive)
        return value, bound
    return None


def _instant_pair(value: str, bound: str, primitive: str | None) -> tuple[Any, Any] | None:
    """Two ISO-8601 strings as instants, or ``None`` when they do not compare.

    A malformed operand and a naive/aware mix both yield no claim: Python raises
    on the second rather than inventing an offset for the naive one, and an
    oracle that guessed would decide a constraint on a fiction.
    """
    parser = date.fromisoformat if primitive == "Date" else datetime.fromisoformat
    parsed: list[Any] = []
    for text in (value, bound):
        try:
            parsed.append(parser(text))
        except (TypeError, ValueError):
            return None
    if primitive == "DateTime":
        aware = [instant.utcoffset() is not None for instant in parsed]
        if aware[0] != aware[1]:
            return None
    return parsed[0], parsed[1]


def _in_range(value: Any, rng: dict[str, Any], primitive: str | None = None) -> bool | None:
    """Whether ``value`` lies within ``rng`` — or ``None`` when no claim is possible.

    ``None`` is the third answer, and its absence was F-2: this returned
    ``False`` — VIOLATED — for every value that was not an ``int`` or ``float``,
    though ``orm-meta.schema.json`` types range bounds ``["string", "number"]``
    and the family is normatively *"numeric / character"*. Over a String- or
    Date-domain range the oracle therefore labelled a CONFORMING population
    violated; and on ``unresolvable_bound.orm.yaml`` — a shipped fixture whose
    ``mass`` type has a unit-based reference and hence no resolvable primitive,
    so its String values reach the constraint untyped — the run quarantined at
    exit 6 as ``candidate-false-pass``, naming the CHECKER for the one normative
    answer available to it (``bound-type-mismatch``, band 4).

    The correct pattern was already two functions away: ``_literal_operand``
    returns ``_UNTYPEABLE`` and ``_comparison_literal`` turns it into ``None``
    for exactly this situation. This is the same rule at the range family.

    A range with neither bound constrains nothing and is satisfied — the
    open-ended form of constraint-reference.md with both ends open. The
    meta-schema's ``anyOf`` requires one, so it does not arise from a model.
    """
    minimum, maximum = rng.get("min"), rng.get("max")
    if minimum is not None:
        pair = _ordered_pair(value, minimum, primitive)
        if pair is None:
            return None
        left, right = pair
        below = left < right if rng.get("min_inclusive", True) else left <= right
        if below:
            return False
    if maximum is not None:
        pair = _ordered_pair(value, maximum, primitive)
        if pair is None:
            return None
        left, right = pair
        above = left > right if rng.get("max_inclusive", True) else left >= right
        if above:
            return False
    return True


def _range_union_claim(
    value: Any, ranges: list[dict[str, Any]], primitive: str | None
) -> bool | None:
    """Whether ``value`` conforms to a DISJUNCTION of ranges, or ``None``.

    A single ``range`` is the union of one, so both meta-schema forms take this
    path. A value conforms when any interval admits it; it violates only when
    EVERY interval decided against it — one undecidable interval leaves the whole
    disjunction open, because that interval might have been the satisfied one.
    """
    outcomes = [_in_range(value, bounds, primitive) for bounds in ranges]
    if any(outcome is True for outcome in outcomes):
        return True
    if any(outcome is None for outcome in outcomes):
        return None
    return False


def _value_witness(
    constraint: dict[str, Any], values: list[Any], primitive: str | None = None
) -> bool | None:
    """Ground truth for one ``value`` constraint over the values it governs.

    The meta-schema makes the three spec forms a ``oneOf`` — ``allowed`` (a
    finite enumeration), ``range`` (one interval), ``ranges`` (a list of
    intervals) — and constraint-reference.md gives the plural form as *"one or
    more numeric / character ranges"*: a **disjunction**, so a value conforms
    when it lies inside ANY of them and violates only when it lies outside every
    one. Written from that reading, not from the checker (C1).

    ``ranges`` had no branch here at all, so the loop body never ran and the
    witness returned SATISFIED over a population violating every interval — and
    since the expectations are derived solely from this oracle, that published
    the checker's correct ``fail`` as a false-fail (F-1). The tell was the
    asymmetry: :mod:`gnd.synth.boundary` and :mod:`gnd.synth.mutate` both stand
    down on ``ranges``, and only the ground-truth witness answered anyway.

    They stand down for a reason that does NOT apply here, which is why this
    implements the family rather than abstaining with them: their job is
    SYNTHESIS — placing a case exactly on the frontier, or minting one value
    outside the spec — and a union of intervals has no single min/max pair to
    aim at. This function's job is EVALUATION, and a disjunction of membership
    tests is completely determined by the normative text. Abstaining where the
    spec is explicit would forfeit oracle coverage for no gain; the abstention
    rule is for shapes the reference genuinely leaves open.

    ``None`` means no claim, and it is returned in two situations:

    * a ``value`` constraint carrying none of the three forms — a shape the
      ``oneOf`` forbids, so unreachable for a loaded model, and guessing
      "satisfied" for an unrecognised spec form is precisely the defect above;
    * any governed value that cannot be ORDERED against the bounds (F-2). One
      undecidable member withdraws the claim for the whole constraint, even when
      another member decided against the bound. The reference does not settle
      that precedence, and claiming "violated" would be worse than silent: the
      checker answers ``unchecked`` for this population by an explicitly
      deliberate rule, so a witness saying "violated" would quarantine that
      correct abstention as a ``candidate-false-pass`` — F-2's exact shape, one
      population over.

    ``allowed`` never abstains: enumeration membership is a total test across
    types, so it has no undecidable case to withdraw on.
    """
    allowed = constraint.get("allowed")
    if allowed is not None:
        # F-7: membership is by IDENTITY, not `==`. Plain `in` collapses `True`
        # with `1` and `False` with `0` (bool <: int), so a population carrying
        # `1` would read as satisfied against `allowed: [true]` while the checker
        # correctly fails it — the witness contradicting the spec in the one
        # branch F-01 left unkeyed, now that this function is the sole oracle for
        # all three `value` forms. `_key` is this module's own independent
        # identity (C1), deliberately not `checker._identity_key`.
        allowed_keys = {_key(a) for a in allowed}
        return all(_key(value) in allowed_keys for value in values)
    ranges = constraint.get("ranges")
    if ranges is None:
        rng = constraint.get("range")
        if rng is None:
            return None
        ranges = [rng]
    claims = [_range_union_claim(value, list(ranges), primitive) for value in values]
    if any(claim is None for claim in claims):
        return None
    return all(claims)


def _comparison_literal(
    constraint: dict[str, Any], fact_type: dict[str, Any], model: Model
) -> tuple[str, Any, str] | None:
    """``(role, typed_literal, oriented_operator)`` for either operand order.

    ``None`` covers every shape over which the witness makes NO CLAIM: a
    role-vs-role comparison (handled by the projection path), a reference-clock
    operand, and a literal that cannot be typed in the role's primitive domain.
    """
    pair = _role_literal_operands(model, constraint, fact_type)
    if pair is None:
        return None
    role, literal, operator = pair
    assert role.role is not None
    return role.role, literal.value, operator


def _witness(
    constraint: dict[str, Any],
    fact_type: dict[str, Any] | None,
    doc: dict[str, Any],
    model: Model,
    children: dict[str, set[str]],
) -> bool | None:
    """Independent ground-truth predicate for one constraint, or ``None``.

    ``None`` means "no independent witness for this family/shape" — the assembler
    then treats the constraint as satisfied-or-abstained by construction and does
    NOT participate it in the C1 quarantine test. Every predicate here is written
    from ORM semantics directly, never by calling the checker (C1).
    """
    ctype = str(constraint.get("type"))
    role_obj = _role_object(model)

    if ctype == "guarded":
        consequent = constraint.get("consequent")
        if isinstance(consequent, dict) and isinstance(consequent.get("exists"), dict):
            return _exists_witness(constraint, doc.get("facts") or {})

    if ctype == "uniqueness":
        if constraint.get("scope") == "external":
            tuples = _join(doc, model, list(constraint.get("role_refs") or []))
        else:
            assert fact_type is not None
            tuples = _project(doc, str(fact_type.get("id")), [str(r) for r in constraint.get("roles") or []])
        keys = [_tuple_key(t) for t in tuples]
        return len(keys) == len(set(keys))

    if ctype == "mandatory":
        assert fact_type is not None
        role_name = str(constraint.get("role"))
        oid = role_obj.get(str(fact_type.get("id")), {}).get(role_name)
        if oid is None:
            return None
        universe = {_key(v) for v in _universe(doc, model, oid, children)}
        present = {
            _key(fact[role_name])
            for fact in doc.get("facts", {}).get(str(fact_type.get("id")), [])
            if role_name in fact
        }
        return universe <= present

    if ctype == "mandatory-disjunctive":
        refs = list(constraint.get("role_refs") or [])
        oids = {role_obj.get(str(r.get("fact_type")), {}).get(str(r.get("role"))) for r in refs}
        if len(oids) != 1 or None in oids:
            return None
        oid = next(iter(oids))
        universe = {_key(v) for v in _universe(doc, model, oid, children)}
        played: set[tuple[str, Any]] = set()
        for r in refs:
            for (v,) in _project(doc, str(r.get("fact_type")), [str(r.get("role"))]):
                played.add(_key(v))
        return universe <= played

    if ctype == "frequency":
        bound = constraint.get("bound") or {}
        lo, hi = bound.get("min"), bound.get("max")
        if constraint.get("scope") == "external":
            tuples = _join(doc, model, list(constraint.get("role_refs") or []))
        else:
            assert fact_type is not None
            tuples = _project(doc, str(fact_type.get("id")), [str(r) for r in constraint.get("roles") or []])
        counts: dict[Any, int] = {}
        for t in tuples:
            counts[_tuple_key(t)] = counts.get(_tuple_key(t), 0) + 1
        for c in counts.values():
            if (lo is not None and c < lo) or (hi is not None and c > hi):
                return False
        return True

    if ctype == "ring":
        assert fact_type is not None
        roles = [str(role.get("role_name")) for role in fact_type.get("roles") or []]
        if len(roles) != 2:
            return None
        # KEYED, not raw (IN-01): `_tuple_key` keeps `True` and `1` apart, the
        # way `_acyclic` and every other identity in this module already do.
        pairs = {_tuple_key(tuple(t)) for t in _project(doc, str(fact_type.get("id")), roles)}
        return _ring_satisfied(str(constraint.get("variant")), pairs)

    if ctype == "value":
        oid = str(constraint.get("object_type"))
        role_ref = constraint.get("role_ref")
        if role_ref is not None:
            values = [v for (v,) in _project(doc, str(role_ref.get("fact_type")), [str(role_ref.get("role"))])]
        else:
            values = _universe(doc, model, oid, children)
        # The primitive comes from `object_type` in BOTH forms: the role-scope
        # hybrid names a primitive there and narrows the scope with `role_ref`
        # (constraint-reference.md). It is `None` for a type with no resolvable
        # primitive — a unit-based reference mode — which is the residual path
        # that made F-2 reachable from a shipped fixture.
        return _value_witness(constraint, values, popvalidate.resolve_primitive(oid, model))

    if ctype == "subset":
        sub = {_tuple_key(t) for t in _seq_tuples(doc, model, list(constraint.get("subset_role_seq") or []))}
        sup = {_tuple_key(t) for t in _seq_tuples(doc, model, list(constraint.get("superset_role_seq") or []))}
        return sub <= sup

    if ctype == "equality":
        a = {_tuple_key(t) for t in _seq_tuples(doc, model, list(constraint.get("role_seq_a") or []))}
        b = {_tuple_key(t) for t in _seq_tuples(doc, model, list(constraint.get("role_seq_b") or []))}
        return a == b

    if ctype == "exclusion":
        a = {_tuple_key(t) for t in _seq_tuples(doc, model, list(constraint.get("role_seq_a") or []))}
        b = {_tuple_key(t) for t in _seq_tuples(doc, model, list(constraint.get("role_seq_b") or []))}
        return not (a & b)

    if ctype == "exclusive-or":
        seqs = [list(s or []) for s in constraint.get("role_seqs") or []]
        if not all(len(s) == 1 for s in seqs):
            return None  # multi-role disjunctive half is undecidable (matches checker)
        value_sets = [
            {_key(t[0]) for t in _seq_tuples(doc, model, s)} for s in seqs
        ]
        refs = [s[0] for s in seqs]
        oids = {role_obj.get(str(r.get("fact_type")), {}).get(str(r.get("role"))) for r in refs}
        if len(oids) != 1 or None in oids:
            return None
        universe = {_key(v) for v in _universe(doc, model, next(iter(oids)), children)}
        union = set().union(*value_sets) if value_sets else set()
        both = any(sum(v in s for s in value_sets) > 1 for v in union)
        neither = bool(universe - union)
        return not (both or neither)

    if ctype == "cardinality":
        bound = constraint.get("bound") or {}
        lo, hi = bound.get("min"), bound.get("max")
        if constraint.get("scope") == "object":
            members = {_key(v) for v in _universe(doc, model, str(constraint.get("object_type")), children)}
        else:
            role_ref = constraint.get("role_ref") or {}
            members = {_key(v) for (v,) in _project(doc, str(role_ref.get("fact_type")), [str(role_ref.get("role"))])}
        count = len(members)
        return not ((lo is not None and count < lo) or (hi is not None and count > hi))

    if ctype == "value-comparison":
        # Intra-fact form only (the fixtures' shape); cross-fact is None here.
        if fact_type is None:
            return None
        op = str(constraint.get("operator"))
        ftid = str(fact_type.get("id"))
        operand_a, operand_b = _normalize_comparison_operands(model, constraint, fact_type)
        if operand_a.kind == operand_b.kind == "role":
            assert operand_a.role is not None and operand_b.role is not None
            rows = _project(doc, ftid, [operand_a.role, operand_b.role])
            claims = [
                _compare_scalar(
                    a,
                    op,
                    b,
                    operand_a.primitive,
                    operand_b.primitive,
                )
                for a, b in rows
            ]
            if any(claim is None for claim in claims):
                return None
            return all(claims)
        # A literal may appear on either side; orient the operator to the role.
        pair = _comparison_literal(constraint, fact_type, model)
        if pair is None:
            return None
        role, literal, oriented_operator = pair
        role_primitive = next(
            (
                operand.primitive
                for operand in (operand_a, operand_b)
                if operand.kind == "role" and operand.role == role
            ),
            None,
        )
        claims = [
            _compare_scalar(
                value,
                oriented_operator,
                literal,
                role_primitive,
                role_primitive,
            )
            for (value,) in _project(doc, ftid, [role])
        ]
        if any(claim is None for claim in claims):
            return None
        return all(claims)

    return None


def _compare_scalar(
    a: Any,
    op: str,
    b: Any,
    primitive_a: str | None = None,
    primitive_b: str | None = None,
) -> bool | None:
    """Compare two scalars in their declared ORM domains, independently.

    Equality is total and uses ORM scalar identity (so booleans never collapse
    into integers). Ordered comparisons require compatible declared domains:
    numeric primitives share one domain, Date/DateTime are parsed as ISO instants,
    and incompatible role primitives yield ``None`` rather than a fabricated
    violation. ``None`` is an abstention and must never drive convergence repair.
    """
    if op not in ("<", "<=", "=", ">=", ">", "!="):
        return None
    if op in ("=", "!="):
        equal = _key(a) == _key(b)
        return equal if op == "=" else not equal

    numeric_primitives = {"Integer", "Float", "Number"}
    if primitive_a is not None and primitive_b is not None:
        if {primitive_a, primitive_b} <= numeric_primitives:
            pair = _ordered_pair(a, b, None)
        elif primitive_a != primitive_b:
            return None
        elif primitive_a in _TEMPORAL_PRIMITIVES:
            if not isinstance(a, str) or not isinstance(b, str):
                return None
            pair = _instant_pair(a, b, primitive_a)
        else:
            pair = _ordered_pair(a, b, primitive_a)
    else:
        # Unresolvable reference modes have no declared primitive. Preserve the
        # checker-independent resolve-or-skip posture while allowing two runtime
        # scalars that demonstrably share a total numeric or lexical order.
        pair = _ordered_pair(a, b, None)
    if pair is None:
        return None
    left, right = pair
    return bool(
        {
            "<": left < right,
            "<=": left <= right,
            ">=": left >= right,
            ">": left > right,
        }[op]
    )


def _kind(model: Model, oid: str) -> str | None:
    ot = _object_types_by_id(model).get(str(oid))
    return str(ot.get("kind")) if ot and ot.get("kind") is not None else None


def _identity_unique(values) -> list[Any]:
    unique: list[Any] = []
    seen: set[tuple[str, Any]] = set()
    for value in values:
        if _key(value) not in seen:
            seen.add(_key(value))
            unique.append(value)
    return unique


def _is_external_entity(model: Model, oid: str) -> bool:
    ot = _object_types_by_id(model).get(str(oid))
    return bool(ot) and (ot.get("reference") or {}).get("mode") == "external"


def _fact_type_constraints(ft: dict[str, Any]) -> list[dict[str, Any]]:
    return list(ft.get("constraints") or [])


class _Builder:
    """Constructs a conforming population confined to small per-type working sets.

    All entity draws come from ``self.work[type]`` (a fixed few distinct pool
    identifiers), NEVER the full pool universe — confinement is what keeps the
    closed-world universe equal to the working sets, so set-family coordination
    (exclusive-or, exclusion, subset) is tractable and joins recur.
    """

    def __init__(self, model: Model, pool: Pool, rng: Random, rows_per_fact_type: int) -> None:
        self.model = model
        self.pool = pool
        self.rng = rng
        self.rows = max(1, rows_per_fact_type)
        self.epool = EntityPool(model, pool, rng)
        self.role_obj = _role_object(model)
        self.children = _direct_subtypes(model)
        self.facts: dict[str, list[dict[str, Any]]] = {}
        self._role_value_specs = self._collect_role_value_specs()
        self._type_max = self._collect_object_cardinality_max()
        self._role_max = self._collect_role_cardinality_max()
        self.work: dict[str, list[Any]] = {}
        self._build_work_sets()

    # -- setup ----------------------------------------------------------------

    def _collect_role_value_specs(self) -> dict[tuple[str, str], list[dict[str, Any]]]:
        specs: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for fact_type in self.model.fact_types or []:
            ftid = str(fact_type.get("id"))
            for role in fact_type.get("roles") or []:
                role_name = str(role.get("role_name"))
                oid = str(role.get("object_type"))
                constraints = governing_value_constraints(
                    self.model, oid, ftid=ftid, role_name=role_name
                )
                if constraints:
                    specs[(ftid, role_name)] = constraints
        return specs

    def _collect_object_cardinality_max(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for _ft, constraint in self._iter_constraints():
            if constraint.get("type") == "cardinality" and constraint.get("scope") == "object":
                bound = constraint.get("bound") or {}
                if bound.get("max") is not None:
                    out[str(constraint.get("object_type"))] = int(bound["max"])
        return out

    def _collect_role_cardinality_max(self) -> dict[tuple[str, str], int]:
        out: dict[tuple[str, str], int] = {}
        for _ft, constraint in self._iter_constraints():
            if constraint.get("type") == "cardinality" and constraint.get("scope") == "role":
                bound = constraint.get("bound") or {}
                role_ref = constraint.get("role_ref") or {}
                if bound.get("max") is not None:
                    out[(str(role_ref.get("fact_type")), str(role_ref.get("role")))] = int(
                        bound["max"]
                    )
        return out

    def _iter_constraints(self):
        for ft in self.model.fact_types or []:
            for constraint in _fact_type_constraints(ft):
                yield ft, constraint
        for constraint in self.model.constraints or []:
            yield None, constraint

    def _build_work_sets(self) -> None:
        for ot in self.model.object_types or []:
            oid = str(ot.get("id"))
            if ot.get("kind") != "entity":
                continue
            universe = self.epool.universe(oid)
            cap = min(len(universe), self._type_max.get(oid, 3), 3)
            cap = max(cap, 1) if universe else 0
            self.work[oid] = universe[:cap]

    # -- value drawing --------------------------------------------------------

    def _draw_value(self, ftid: str, role_name: str, oid: str) -> Any:
        constraints = self._role_value_specs.get((ftid, role_name))
        if constraints is not None:
            primitive = popvalidate.resolve_primitive(oid, self.model)
            if primitive is None:
                raise GeneratorError(f"no primitive resolvable for constrained value type {oid!r}")
            try:
                return draw_value_for_constraints(str(primitive), self.rng, constraints)
            except EmptyValueDomain as error:
                raise GeneratorError(
                    f"value constraints for role {ftid}.{role_name} have an empty "
                    f"intersection: {error}"
                ) from error
        return self.epool.draw_value(oid)

    def _draw_entity(self, oid: str) -> Any:
        work = self.work.get(str(oid))
        if not work:
            raise GeneratorError(
                f"no working entities for object type {oid!r}; the pool supplies "
                f"no identifiers for it (not-derivable)."
            )
        return self.rng.choice(work)

    # -- category detection ---------------------------------------------------

    def _claimed_fact_types(self) -> set[str]:
        claimed: set[str] = set()
        for ft in self.model.fact_types or []:
            ftid = str(ft.get("id"))
            roles = ft.get("roles") or []
            if any(_is_external_entity(self.model, r.get("object_type")) for r in roles):
                claimed.add(ftid)
            if self._ring_variants(ft):
                claimed.add(ftid)
        for _ft, constraint in self._iter_constraints():
            ctype = constraint.get("type")
            if ctype == "subset":
                for ref in constraint.get("subset_role_seq") or []:
                    claimed.add(str(ref.get("fact_type")))
            elif ctype == "exclusion":
                for ref in constraint.get("role_seq_b") or []:
                    claimed.add(str(ref.get("fact_type")))
            elif ctype == "exclusive-or":
                for seq in constraint.get("role_seqs") or []:
                    for ref in seq or []:
                        claimed.add(str(ref.get("fact_type")))
        return claimed

    def _ring_variants(self, ft: dict[str, Any]) -> list[str]:
        return [
            str(c.get("variant")) for c in _fact_type_constraints(ft) if c.get("type") == "ring"
        ]

    # -- construction passes --------------------------------------------------

    def construct(self) -> None:
        claimed = self._claimed_fact_types()
        for ft in self.model.fact_types or []:
            ftid = str(ft.get("id"))
            self.facts.setdefault(ftid, [])
            if ftid not in claimed and not isinstance(ft.get("derivation_rule"), dict):
                self._generate_plain(ft)
        for ft in self.model.fact_types or []:
            if self._ring_variants(ft):
                self._generate_ring(ft)
        self._generate_externals()
        self._coordinate_set_families()
        self._coordinate_value_comparisons()
        self._seed_joins()
        self._close_mandatory()
        self._coordinate_external_uniqueness()

    def _entity_roles(self, ft: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            r for r in ft.get("roles") or [] if _kind(self.model, r.get("object_type")) == "entity"
        ]

    def _value_roles(self, ft: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            r for r in ft.get("roles") or [] if _kind(self.model, r.get("object_type")) == "value"
        ]

    def _generate_plain(self, ft: dict[str, Any]) -> None:
        ftid = str(ft.get("id"))
        entity_roles = self._entity_roles(ft)
        value_roles = self._value_roles(ft)
        singleton_uc = [
            str(rn)
            for c in _fact_type_constraints(ft)
            if c.get("type") == "uniqueness" and c.get("scope") != "external"
            for rn in (c.get("roles") or [])
            if len(c.get("roles") or []) == 1
        ]
        driver = None
        for r in entity_roles:
            if str(r.get("role_name")) in singleton_uc:
                driver = r
                break
        if driver is None and entity_roles:
            driver = entity_roles[0]

        rows_out: list[dict[str, Any]] = []
        if driver is not None:
            drv_type = str(driver.get("object_type"))
            drv_role = str(driver.get("role_name"))
            drivers = list(self.work.get(drv_type, []))
            rmax = self._role_max.get((ftid, drv_role))
            if rmax is not None:
                drivers = drivers[:rmax]
            for entity in drivers:
                row: dict[str, Any] = {drv_role: entity}
                for r in entity_roles:
                    if r is driver:
                        continue
                    row[str(r.get("role_name"))] = self._draw_entity(str(r.get("object_type")))
                for r in value_roles:
                    row[str(r.get("role_name"))] = self._draw_value(
                        ftid, str(r.get("role_name")), str(r.get("object_type"))
                    )
                rows_out.append(row)
        elif value_roles:
            row = {}
            for r in value_roles:
                row[str(r.get("role_name"))] = self._draw_value(
                    ftid, str(r.get("role_name")), str(r.get("object_type"))
                )
            rows_out.append(row)
        self.facts[ftid] = rows_out

    def _generate_ring(self, ft: dict[str, Any]) -> None:
        ftid = str(ft.get("id"))
        roles = ft.get("roles") or []
        if len(roles) != 2:
            raise GeneratorError(f"ring host {ftid!r} is not binary (not-derivable).")
        from_role, to_role = str(roles[0].get("role_name")), str(roles[1].get("role_name"))
        etype = str(roles[0].get("object_type"))
        nodes = list(self.work.get(etype, []))
        if len(nodes) < 2:
            raise GeneratorError(f"ring host {ftid!r} needs >=2 nodes (not-derivable).")
        variants = set(self._ring_variants(ft))
        edges = self._ring_edges(variants, nodes)
        self.facts[ftid] = [{from_role: a, to_role: b} for a, b in edges]

    def _ring_edges(self, variants: set[str], nodes: list[Any]) -> list[tuple[Any, Any]]:
        n = nodes
        if variants <= _CHAIN_COMPATIBLE:
            if len(n) >= 3:
                return [(n[0], n[1]), (n[1], n[2])]
            return [(n[0], n[1])]
        if "transitive" in variants:
            if len(n) >= 3:
                return [(n[0], n[1]), (n[1], n[2]), (n[0], n[2])]
            return [(n[0], n[1])]
        if variants & {"symmetric", "symmetric-irreflexive", "symmetric-intransitive"}:
            return [(n[0], n[1]), (n[1], n[0])]
        if "purely-reflexive" in variants:
            return [(node, node) for node in n]
        if "reflexive" in variants:
            return [(node, node) for node in n] + [(n[0], n[1])]
        # single primitive fallback
        return [(n[0], n[1])]

    def _generate_externals(self) -> None:
        for ot in self.model.object_types or []:
            if ot.get("kind") != "entity" or (ot.get("reference") or {}).get("mode") != "external":
                continue
            etid = str(ot.get("id"))
            instances = list(self.work.get(etid, []))
            hosts = [
                ft
                for ft in self.model.fact_types or []
                if any(str(r.get("object_type")) == etid for r in ft.get("roles") or [])
            ]
            for i, inst in enumerate(instances):
                for ft in hosts:
                    ftid = str(ft.get("id"))
                    row: dict[str, Any] = {}
                    for r in ft.get("roles") or []:
                        rn = str(r.get("role_name"))
                        roid = str(r.get("object_type"))
                        if roid == etid:
                            row[rn] = inst
                        elif _kind(self.model, roid) == "entity":
                            work = self.work.get(roid, [])
                            row[rn] = work[i % len(work)] if work else self._draw_entity(roid)
                        else:
                            row[rn] = self._draw_value(ftid, rn, roid)
                    self.facts.setdefault(ftid, []).append(row)

    def _external_uniqueness_components(
        self,
    ) -> list[list[tuple[str, dict[str, Any]]]]:
        """Connected alethic external uniqueness constraints in source order."""
        fact_types = {str(ft.get("id")): ft for ft in self.model.fact_types or []}
        items: list[tuple[str, dict[str, Any], set[tuple[str, ...]]]] = []
        for index, constraint in enumerate(self.model.constraints or []):
            if not (
                constraint.get("type") == "uniqueness"
                and constraint.get("scope") == "external"
                and constraint.get("modality") == "alethic"
            ):
                continue
            refs = list(constraint.get("role_refs") or [])
            referenced = {(str(ref.get("fact_type")), str(ref.get("role"))) for ref in refs}
            signatures = {("role", *role_ref) for role_ref in referenced}
            for ftid in {ftid for ftid, _role in referenced}:
                signatures.update(
                    ("anchor", str(role.get("object_type")))
                    for role in (fact_types.get(ftid) or {}).get("roles") or []
                    if (ftid, str(role.get("role_name"))) not in referenced
                )
            items.append((positional_constraint_ref(None, index), constraint, signatures))

        components: list[list[tuple[str, dict[str, Any]]]] = []
        remaining = list(items)
        while remaining:
            ref, constraint, signatures = remaining.pop(0)
            component = [(ref, constraint)]
            while connected := [item for item in remaining if signatures & item[2]]:
                for candidate_ref, candidate, candidate_signatures in connected:
                    remaining.remove((candidate_ref, candidate, candidate_signatures))
                    component.append((candidate_ref, candidate))
                    signatures |= candidate_signatures
            components.append(component)
        return components

    def _external_join_groups(
        self, role_refs: list[dict[str, Any]]
    ) -> list[list[tuple[str, int, str]]]:
        """Referenced cells for the exact anchor groups materialized by ``_join``."""
        by_ft: dict[str, list[tuple[int, str]]] = {}
        order: list[str] = []
        for slot, ref in enumerate(role_refs):
            ftid = str(ref.get("fact_type"))
            if ftid not in by_ft:
                by_ft[ftid] = []
                order.append(ftid)
            by_ft[ftid].append((slot, str(ref.get("role"))))
        joined: list[tuple[dict[str, Any], dict[int, tuple[str, int, str]]]] = [({}, {})]
        for ftid in order:
            ref_roles = {role for _slot, role in by_ft[ftid]}
            anchors = [
                (role, oid)
                for role, oid in self.role_obj.get(ftid, {}).items()
                if role not in ref_roles
            ]
            next_joined = []
            for anchor_values, outputs in joined:
                for row_index, fact in enumerate(self.facts.get(ftid, [])):
                    if any(role not in fact for role, _oid in anchors) or any(
                        role not in fact for _slot, role in by_ft[ftid]
                    ):
                        continue
                    merged = dict(anchor_values)
                    if any(
                        oid in merged and merged[oid] != _key(fact[role]) for role, oid in anchors
                    ):
                        continue
                    merged.update({oid: _key(fact[role]) for role, oid in anchors})
                    selected = dict(outputs)
                    selected.update({slot: (ftid, row_index, role) for slot, role in by_ft[ftid]})
                    next_joined.append((merged, selected))
            joined = next_joined
        return [[selected[slot] for slot in range(len(role_refs))] for _anchors, selected in joined]

    def _coordinate_external_uniqueness(self) -> None:
        for component in self._external_uniqueness_components():
            self._coordinate_external_component(component)

    def _coordinate_external_component(self, component: list[tuple[str, dict[str, Any]]]) -> None:
        """Atomically search a bounded assignment for one external component."""
        original_doc = {"facts": self.facts, "instances": {}}
        if all(
            _witness(constraint, None, original_doc, self.model, self.children) is True
            for _ref, constraint in component
        ):
            return

        groups = [
            group
            for _ref, constraint in component
            for group in self._external_join_groups(list(constraint.get("role_refs") or []))
        ]
        cells: list[tuple[str, int, str]] = []
        seen_cells: set[tuple[str, int, str]] = set()
        for cell in (cell for group in groups for cell in group):
            if cell not in seen_cells:
                seen_cells.add(cell)
                cells.append(cell)

        trial = {ftid: [dict(row) for row in rows] for ftid, rows in self.facts.items()}
        domain_cache: dict[tuple[str, str], list[Any]] = {}

        def domain(ftid: str, role_name: str) -> list[Any]:
            cache_key = (ftid, role_name)
            if cache_key in domain_cache:
                return domain_cache[cache_key]
            oid = self.role_obj.get(ftid, {}).get(role_name)
            values = [row[role_name] for row in self.facts.get(ftid, []) if role_name in row]
            if oid is not None and _kind(self.model, oid) == "entity":
                values.extend(self.work.get(oid, []))
            elif oid is not None:
                draw_count = max(1, 2 * len(groups))
                values.extend(self._draw_value(ftid, role_name, oid) for _ in range(draw_count))
            domain_cache[cache_key] = _identity_unique(values)
            return domain_cache[cache_key]

        baseline = _witness_map(self.model, original_doc, self.children)
        alethic = _alethic_refs(self.model)
        preserved = {ref for ref, result in baseline.items() if result is True and ref in alethic}
        member_refs = {ref for ref, _constraint in component}
        attempts = 0
        cap_reached = False

        def solve(position: int) -> bool:
            nonlocal attempts, cap_reached
            if position == len(cells):
                witnesses = _witness_map(
                    self.model, {"facts": trial, "instances": {}}, self.children
                )
                return all(witnesses.get(ref) is True for ref in member_refs) and all(
                    witnesses.get(ref) is True for ref in preserved
                )
            ftid, row_index, role_name = cells[position]
            for value in domain(ftid, role_name):
                if attempts >= _EXTERNAL_UNIQUENESS_SEARCH_CAP:
                    cap_reached = True
                    return False
                attempts += 1
                trial[ftid][row_index][role_name] = value
                if solve(position + 1):
                    return True
                if cap_reached:
                    return False
            return False

        refs = ", ".join(ref for ref, _constraint in component)
        if not solve(0):
            reason = (
                "external-uniqueness-search-cap"
                if cap_reached
                else "external-uniqueness-domain-exhausted"
            )
            raise GeneratorError(
                f"external uniqueness component [{refs}]: {reason} after "
                f"{attempts} candidate assignments (not-derivable)."
            )
        self.facts = trial

    def _coordinate_set_families(self) -> None:
        for _ft, constraint in self._iter_constraints():
            ctype = constraint.get("type")
            if ctype == "subset":
                self._coordinate_subset(constraint)
            elif ctype == "exclusion":
                self._coordinate_exclusion(constraint)
            elif ctype == "exclusive-or":
                self._coordinate_exclusive_or(constraint)

    def _coordinate_subset(self, constraint: dict[str, Any]) -> None:
        sub_seq = list(constraint.get("subset_role_seq") or [])
        sup_seq = list(constraint.get("superset_role_seq") or [])
        sup_tuples = _seq_tuples({"facts": self.facts, "instances": {}}, self.model, sup_seq)
        if not sup_tuples:
            return
        # Copy ONE superset tuple into the subset side (subset side is a single
        # fact type when it is claimed — the fixtures' shape).
        sub_ftids = {str(ref.get("fact_type")) for ref in sub_seq}
        if len(sub_ftids) != 1:
            return
        sub_ftid = next(iter(sub_ftids))
        chosen = sup_tuples[0]
        row = {str(ref.get("role")): value for ref, value in zip(sub_seq, chosen, strict=False)}
        self.facts.setdefault(sub_ftid, [])
        if row not in self.facts[sub_ftid]:
            self.facts[sub_ftid].append(row)

    def _coordinate_exclusion(self, constraint: dict[str, Any]) -> None:
        # Leave the seq_b side empty: seq_a carries rows (non-vacuous), seq_b is
        # disjoint by being empty. seq_b fact types were claimed (not plainly
        # generated), so they are already empty here.
        for ref in constraint.get("role_seq_b") or []:
            self.facts.setdefault(str(ref.get("fact_type")), [])

    def _coordinate_exclusive_or(self, constraint: dict[str, Any]) -> None:
        seqs = [list(s or []) for s in constraint.get("role_seqs") or []]
        if not all(len(s) == 1 for s in seqs):
            return
        refs = [s[0] for s in seqs]
        oids = {
            self.role_obj.get(str(r.get("fact_type")), {}).get(str(r.get("role"))) for r in refs
        }
        if len(oids) != 1 or None in oids:
            return
        oid = next(iter(oids))
        doc = {"facts": self.facts, "instances": {}}
        universe = []
        seen: set[tuple[str, Any]] = set()
        for v in _universe(doc, self.model, str(oid), self.children):
            if _key(v) not in seen:
                seen.add(_key(v))
                universe.append(v)
        for ref in refs:
            self.facts.setdefault(str(ref.get("fact_type")), [])
            self.facts[str(ref.get("fact_type"))] = []
        for i, member in enumerate(universe):
            ref = refs[i % len(refs)]
            self.facts[str(ref.get("fact_type"))].append({str(ref.get("role")): member})

    def _coordinate_value_comparisons(self) -> None:
        """Order intra-fact value-comparison operands so the constraint holds.

        Deontic in some fixtures and ALETHIC in others (``misc.orm.yaml`` caps
        points at 100 alethically), so this is a convergence requirement wherever
        the modality is alethic — and a clean conforming population should not
        carry a gratuitous ``start > end`` warning either.

        Two shapes: role-vs-role (order the two operands) and role-vs-LITERAL
        (clamp the role's value to the literal side). The literal shape was
        invisible before, because ``role_b`` was assumed to name a role.
        """
        for ft in self.model.fact_types or []:
            ftid = str(ft.get("id"))
            for constraint in _fact_type_constraints(ft):
                if constraint.get("type") != "value-comparison":
                    continue
                op = str(constraint.get("operator"))
                pair = _comparison_literal(constraint, ft, self.model)
                if pair is not None:
                    self._clamp_to_literal(ftid, pair[0], pair[2], pair[1])
                    continue
                operand_a, operand_b = _normalize_comparison_operands(self.model, constraint, ft)
                if operand_a.kind != "role" or operand_b.kind != "role":
                    continue
                role_a, role_b = operand_a.role, operand_b.role
                assert role_a is not None and role_b is not None
                for fact in self.facts.get(ftid, []):
                    if role_a not in fact or role_b not in fact:
                        continue
                    a, b = fact[role_a], fact[role_b]
                    claim = _compare_scalar(
                        a,
                        op,
                        b,
                        operand_a.primitive,
                        operand_b.primitive,
                    )
                    if claim is not False:
                        continue
                    ordered = _compare_scalar(
                        a,
                        "<=",
                        b,
                        operand_a.primitive,
                        operand_b.primitive,
                    )
                    if ordered is None:
                        continue
                    lo, hi = (a, b) if ordered else (b, a)
                    if op in ("<=", "<", "=", ">="):
                        fact[role_a], fact[role_b] = (
                            (lo, hi) if op in ("<=", "<", "=") else (hi, lo)
                        )
                        if op in ("=",):
                            fact[role_b] = fact[role_a]
                    elif op in (">",):
                        fact[role_a], fact[role_b] = hi, lo

    def _clamp_to_literal(self, ftid: str, role: str, op: str, literal: Any) -> None:
        """Move ``role``'s values to the satisfying side of a literal operand.

        Only the ordered operators have a satisfying side reachable by a single
        assignment; ``!=`` is left alone (any distinct value already satisfies it
        and forcing one would fight the value generator's own spec awareness).
        """
        step = 1 if isinstance(literal, int) and not isinstance(literal, bool) else None
        for fact in self.facts.get(ftid, []):
            if role not in fact:
                continue
            oid = self.role_obj.get(ftid, {}).get(role)
            primitive = (
                popvalidate.resolve_primitive(str(oid), self.model) if oid is not None else None
            )
            if _compare_scalar(fact[role], op, literal, primitive, primitive) is not False:
                continue
            if op in ("<=", ">=", "="):
                fact[role] = literal
            elif op == "<" and step is not None:
                fact[role] = literal - step
            elif op == ">" and step is not None:
                fact[role] = literal + step

    def _seed_joins(self) -> None:
        doc = {"facts": self.facts, "instances": {}}
        for _ref, _label, seq in _join_scoped_sequences(self.model):
            if _seq_tuples(doc, self.model, seq):
                continue
            self._seed_one_join(seq)

    def _seed_one_join(self, seq: list[dict[str, Any]]) -> None:
        # Make every referenced fact type carry a fact whose anchor roles all take
        # the index-0 working identifier of their object type — so shared anchors
        # match and the join yields >=1 row.
        for ref in seq:
            ftid = str(ref.get("fact_type"))
            ft = next((f for f in self.model.fact_types if str(f.get("id")) == ftid), None)
            if ft is None:
                continue
            row: dict[str, Any] = {}
            for r in ft.get("roles") or []:
                rn = str(r.get("role_name"))
                roid = str(r.get("object_type"))
                if _kind(self.model, roid) == "entity":
                    work = self.work.get(roid, [])
                    row[rn] = work[0] if work else self._draw_entity(roid)
                else:
                    row[rn] = self._draw_value(ftid, rn, roid)
            self.facts.setdefault(ftid, [])
            if row not in self.facts[ftid]:
                self.facts[ftid].append(row)

    def _close_mandatory(self) -> None:
        doc = {"facts": self.facts, "instances": {}}
        for ft in self.model.fact_types or []:
            ftid = str(ft.get("id"))
            for constraint_index, constraint in enumerate(_fact_type_constraints(ft)):
                if constraint.get("type") != "mandatory":
                    continue
                role_name = str(constraint.get("role"))
                oid = self.role_obj.get(ftid, {}).get(role_name)
                if oid is None:
                    continue
                present = {_key(f[role_name]) for f in self.facts.get(ftid, []) if role_name in f}
                for value in _universe(doc, self.model, oid, self.children):
                    if _key(value) in present:
                        continue
                    present.add(_key(value))
                    constraint_ref = positional_constraint_ref(ftid, constraint_index)
                    self.facts.setdefault(ftid, []).append(
                        self._mandatory_completion(ft, {role_name: value}, constraint_ref)
                    )

    def _mandatory_completion(
        self,
        ft: dict[str, Any],
        fixed: dict[str, Any],
        constraint_ref: str,
    ) -> dict[str, Any]:
        """Complete a missing mandatory subject without reopening uniqueness."""
        ftid = str(ft.get("id"))
        singleton_roles = {
            str(role)
            for constraint in _fact_type_constraints(ft)
            if constraint.get("type") == "uniqueness"
            and constraint.get("scope") != "external"
            and constraint.get("modality") == "alethic"
            and len(constraint.get("roles") or []) == 1
            for role in constraint.get("roles") or []
        }
        restricted = singleton_roles - set(fixed)
        if not restricted:
            return self._complete_fact(ft, fixed)

        roles = [role for role in ft.get("roles") or [] if str(role.get("role_name")) in restricted]
        domains: list[list[Any]] = []
        for role in roles:
            role_name = str(role.get("role_name"))
            oid = str(role.get("object_type"))
            if _kind(self.model, oid) == "entity":
                candidates = list(self.work.get(oid, []))
            else:
                candidates = [
                    self._draw_value(ftid, role_name, oid)
                    for _ in range(max(1, 2 * max(1, len(self.facts.get(ftid, [])))))
                ]
            used = {_key(row[role_name]) for row in self.facts.get(ftid, []) if role_name in row}
            domains.append(
                [
                    candidate
                    for candidate in _identity_unique(candidates)
                    if _key(candidate) not in used
                ]
            )

        original_doc = {"facts": self.facts, "instances": {}}
        baseline = _witness_map(self.model, original_doc, self.children)
        alethic = _alethic_refs(self.model)
        preserved = {ref for ref, result in baseline.items() if result is True and ref in alethic}
        for values in product(*domains):
            candidate = dict(fixed)
            candidate.update(
                {
                    str(role.get("role_name")): value
                    for role, value in zip(roles, values, strict=True)
                }
            )
            candidate = self._complete_fact(ft, candidate)
            trial = {key: [dict(row) for row in rows] for key, rows in self.facts.items()}
            trial.setdefault(ftid, []).append(candidate)
            witnesses = _witness_map(self.model, {"facts": trial, "instances": {}}, self.children)
            if all(witnesses.get(ref) is True for ref in preserved):
                return candidate
        raise GeneratorError(
            f"{constraint_ref}: mandatory-uniqueness-domain-exhausted (not-derivable)."
        )

    def _complete_fact(self, ft: dict[str, Any], fixed: dict[str, Any]) -> dict[str, Any]:
        ftid = str(ft.get("id"))
        row = dict(fixed)
        for r in ft.get("roles") or []:
            rn = str(r.get("role_name"))
            if rn in row:
                continue
            roid = str(r.get("object_type"))
            if _kind(self.model, roid) == "entity":
                row[rn] = self._draw_entity(roid)
            else:
                row[rn] = self._draw_value(ftid, rn, roid)
        return row

    # -- output ---------------------------------------------------------------

    def doc(self, model_ref: str) -> dict[str, Any]:
        covers = [str(ft.get("id")) for ft in self.model.fact_types or []]
        header: dict[str, Any] = {
            "model": model_ref,
            "source": "synthetic",
            "label": "conforming",
            "covers": covers,
        }
        if self.model.model_id:
            header["model_id"] = str(self.model.model_id)
        facts = {ftid: rows for ftid, rows in self.facts.items() if rows}
        return {"population": header, "instances": {}, "facts": facts}


def _join_scoped_sequences(model: Model):
    """Yield ``(constraint_ref, label, sequence)`` for every SUBJECT role sequence
    that spans >1 fact type — the checker's ``_JOIN_SUBJECT_SEQS`` families PLUS
    ``subset`` (which plan 01 omits from the vacuity table, so its degenerate join
    never emits ``vacuous`` — Claude-HIGH)."""

    def emit(constraint, ref):
        ctype = str(constraint.get("type"))
        seqs: list[list[dict[str, Any]]] = []
        if ctype in ("uniqueness", "frequency") and constraint.get("scope") == "external":
            seqs.append(list(constraint.get("role_refs") or []))
        elif ctype == "value-comparison":
            refs = [
                operand
                for operand in (constraint.get("role_a"), constraint.get("role_b"))
                if isinstance(operand, dict) and "fact_type" in operand and "role" in operand
            ]
            if len(refs) == 2:
                seqs.append(refs)
        elif ctype in ("equality", "exclusion"):
            seqs.append(list(constraint.get("role_seq_a") or []))
            seqs.append(list(constraint.get("role_seq_b") or []))
        elif ctype == "subset":
            seqs.append(list(constraint.get("subset_role_seq") or []))
            seqs.append(list(constraint.get("superset_role_seq") or []))
        for seq in seqs:
            fts = {str(r.get("fact_type")) for r in seq if isinstance(r, dict)}
            if len(fts) > 1:
                label = ", ".join(f"{r.get('fact_type')}.{r.get('role')}" for r in seq)
                yield ref, label, [r for r in seq if isinstance(r, dict)]

    for ft in model.fact_types or []:
        for i, constraint in enumerate(_fact_type_constraints(ft)):
            ref = positional_constraint_ref(ft.get("id"), i)
            yield from emit(constraint, ref)
    for i, constraint in enumerate(model.constraints or []):
        yield from emit(constraint, positional_constraint_ref(None, i))


def assert_non_degenerate(model: Model, population: Population) -> None:
    """Assert every join-scoped subject sequence yields >=1 row on ``population``.

    POSITIVE gate (Claude-HIGH): it does NOT wait for a ``vacuous`` verdict —
    ``subset`` never emits one — but asserts row-count directly, reusing the
    checker's OWN ``_role_seq_tuples`` so the count is the checker's join. A zero
    row on any join-scoped sequence is a generator defect (:class:`GeneratorError`),
    not a model property.
    """
    for ref, label, seq in _join_scoped_sequences(model):
        rows = checker_module._role_seq_tuples(model, population, seq)
        if not rows:
            raise GeneratorError(
                f"non-degeneracy gate: join-scoped subject sequence [{label}] "
                f"({ref}) yielded ZERO rows on the conforming population — a "
                f"degenerate join tests nothing (Claude-HIGH positive gate)."
            )


def measure_distinct_ratios(model: Model, doc: dict[str, Any]) -> dict[str, tuple[int, int]]:
    """Per entity object type: ``(distinct identifiers, total draws)`` across all
    facts — the entity-recurrence figure stated against Polyfactory's 8-of-8."""
    role_obj = _role_object(model)
    counts: dict[str, tuple[set[tuple[str, Any]], int]] = {}
    entity_ids = {
        str(ot.get("id")) for ot in model.object_types or [] if ot.get("kind") == "entity"
    }
    for ft in model.fact_types or []:
        ftid = str(ft.get("id"))
        for rn, oid in role_obj.get(ftid, {}).items():
            if oid not in entity_ids:
                continue
            seen, total = counts.get(oid, (set(), 0))
            for fact in doc.get("facts", {}).get(ftid, []):
                if rn in fact:
                    seen.add(_key(fact[rn]))
                    total += 1
            counts[oid] = (seen, total)
    return {oid: (len(seen), total) for oid, (seen, total) in counts.items() if total}


def _constraint_iter_with_ref(model: Model):
    for ft in model.fact_types or []:
        for i, constraint in enumerate(_fact_type_constraints(ft)):
            yield positional_constraint_ref(ft.get("id"), i), constraint, ft
    for i, constraint in enumerate(model.constraints or []):
        yield positional_constraint_ref(None, i), constraint, None



# Historical qualifications are serialized by existing callers.
GeneratorError.__module__ = 'gnd.synth.assemble'
_TermGenerationUnavailable.__module__ = 'gnd.synth.assemble'
CheckerWitnessDiscrepancy.__module__ = 'gnd.synth.assemble'
Assembly.__module__ = 'gnd.synth.assemble'
ExpectedStateData.__module__ = 'gnd.synth.assemble'
_object_types_by_id.__module__ = 'gnd.synth.assemble'
_role_object.__module__ = 'gnd.synth.assemble'
_direct_subtypes.__module__ = 'gnd.synth.assemble'
_descendants.__module__ = 'gnd.synth.assemble'
_denoting_types.__module__ = 'gnd.synth.assemble'
_universe.__module__ = 'gnd.synth.assemble'
_project.__module__ = 'gnd.synth.assemble'
_join.__module__ = 'gnd.synth.assemble'
_seq_tuples.__module__ = 'gnd.synth.assemble'
_ring_satisfied.__module__ = 'gnd.synth.assemble'
_ring_component_ok.__module__ = 'gnd.synth.assemble'
_acyclic.__module__ = 'gnd.synth.assemble'
_ordered_pair.__module__ = 'gnd.synth.assemble'
_instant_pair.__module__ = 'gnd.synth.assemble'
_in_range.__module__ = 'gnd.synth.assemble'
_range_union_claim.__module__ = 'gnd.synth.assemble'
_value_witness.__module__ = 'gnd.synth.assemble'
_comparison_literal.__module__ = 'gnd.synth.assemble'
_witness.__module__ = 'gnd.synth.assemble'
_compare_scalar.__module__ = 'gnd.synth.assemble'
_kind.__module__ = 'gnd.synth.assemble'
_identity_unique.__module__ = 'gnd.synth.assemble'
_is_external_entity.__module__ = 'gnd.synth.assemble'
_fact_type_constraints.__module__ = 'gnd.synth.assemble'
_Builder.__module__ = 'gnd.synth.assemble'
_join_scoped_sequences.__module__ = 'gnd.synth.assemble'
assert_non_degenerate.__module__ = 'gnd.synth.assemble'
measure_distinct_ratios.__module__ = 'gnd.synth.assemble'
_constraint_iter_with_ref.__module__ = 'gnd.synth.assemble'

# Public dependency and compatibility spellings; same predecessor objects.
Builder = _Builder
CHAIN_COMPATIBLE = _CHAIN_COMPATIBLE
EXTERNAL_UNIQUENESS_SEARCH_CAP = _EXTERNAL_UNIQUENESS_SEARCH_CAP
TEMPORAL_PRIMITIVES = _TEMPORAL_PRIMITIVES
TermGenerationUnavailable = _TermGenerationUnavailable
acyclic = _acyclic
compare_scalar = _compare_scalar
comparison_literal = _comparison_literal
constraint_iter_with_ref = _constraint_iter_with_ref
denoting_types = _denoting_types
descendants = _descendants
direct_subtypes = _direct_subtypes
fact_type_constraints = _fact_type_constraints
identity_unique = _identity_unique
in_range = _in_range
instant_pair = _instant_pair
is_external_entity = _is_external_entity
join = _join
join_scoped_sequences = _join_scoped_sequences
key = _key
kind = _kind
object_types_by_id = _object_types_by_id
ordered_pair = _ordered_pair
project = _project
range_union_claim = _range_union_claim
ring_component_ok = _ring_component_ok
ring_satisfied = _ring_satisfied
role_object = _role_object
seq_tuples = _seq_tuples
tuple_key = _tuple_key
universe = _universe
value_witness = _value_witness
witness = _witness

def _witness_map(
    model: Model, doc: dict[str, Any], children: dict[str, set[str]]
) -> dict[str, bool | None]:
    out: dict[str, bool | None] = {}
    for ref, constraint, ft in _constraint_iter_with_ref(model):
        out[ref] = _witness(constraint, ft, doc, model, children)
    return out

_witness_map.__module__ = 'gnd.synth.assemble'
witness_map = _witness_map

def _alethic_refs(model: Model) -> set[str]:
    """Constraint refs whose modality is alethic — convergence is defined on
    these only (a deontic violation is a WARNING, never a fail, and does not
    block a conforming population; a deontic witness that does not hold is
    therefore not a convergence failure)."""
    return {
        ref
        for ref, constraint, _ft in _constraint_iter_with_ref(model)
        if str(constraint.get("modality", "")) == "alethic"
    }

_alethic_refs.__module__ = 'gnd.synth.assemble'
alethic_refs = _alethic_refs
