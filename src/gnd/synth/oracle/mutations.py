"""Model-directed mutation primitives."""
from __future__ import annotations

import copy
import itertools
import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from random import Random
from typing import Any

from gnd.address import positional_constraint_ref
from gnd.checker import (
    _RING_COMPONENTS,
    _RING_VARIANTS,
    IMPLEMENTED_FAMILIES,
    CheckReport,
    check,
)
from gnd.model import Model
from gnd.population import PopulationValidationError, load_population
from gnd.synth.comparison import normalize_operands as _normalize_comparison_operands
from gnd.synth.guarded import (
    antecedent_bindings as _guarded_antecedent_bindings,
)
from gnd.synth.guarded import (
    exists_witness as _guarded_exists_witness,
)
from gnd.synth.guarded import (
    has_private_exists_sources as _has_private_exists_sources,
)
from gnd.synth.guarded import (
    modular_repair_plan as _guarded_modular_repair_plan,
)
from gnd.synth.oracle.constructive import (
    ExpectedStateData as ExpectedStateData,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    GeneratorError as GeneratorError,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    compare_scalar as _compare_scalar,
)
from gnd.synth.oracle.constructive import (
    constraint_iter_with_ref as _constraint_iter_with_ref,
)
from gnd.synth.oracle.constructive import (
    key as _key,
)
from gnd.synth.oracle.constructive import (
    role_object as _role_object,
)
from gnd.synth.oracle.constructive import (
    seq_tuples as _seq_tuples,
)
from gnd.synth.oracle.state import (
    AMPLIFICATION_CEILING as _AMPLIFICATION_CEILING,
)
from gnd.synth.oracle.state import (
    MANDATORY_RELEVANT as _MANDATORY_RELEVANT,
)
from gnd.synth.oracle.state import (
    SKIP as _SKIP,
)
from gnd.synth.oracle.state import (
    complete_row as _complete_row,
)
from gnd.synth.oracle.state import (
    enforce_value_comparisons as _enforce_value_comparisons,
)
from gnd.synth.oracle.state import (
    existing_members as _existing_members,
)
from gnd.synth.oracle.state import (
    expected_state as expected_state,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle.state import (
    facts_of as _facts_of,
)
from gnd.synth.oracle.state import (
    fresh_identifier as _fresh_identifier,
)
from gnd.synth.oracle.state import (
    ft_by_id as _ft_by_id,
)
from gnd.synth.oracle.state import (
    is_entity as _is_entity,
)
from gnd.synth.oracle.state import (
    out_of_spec_value as _out_of_spec_value,
)
from gnd.synth.oracle.state import (
    predict_violations as predict_violations,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle.state import (
    resolve as _resolve,
)
from gnd.synth.oracle.state import (
    valid_value as _valid_value,
)
from gnd.synth.oracle.state import (
    xor_single_role as _xor_single_role,
)
from gnd.synth.provenance import ExpectedState

__all__ = [
    "OPERATORS",
    "ExpectedState",
    "Mutation",
    "PredictionMismatch",
    "ViolatingCase",
    "compare_observed",
    "emit_violating",
    "enumerate_violating",
    "expected_state",
    "family_coverage",
    "operators_for",
    "predict_violations",
]


@dataclass(frozen=True)
class Mutation:
    """One applicable (operator, constraint) binding.

    ``apply(doc, model, constraint_ref, rng)`` returns the mutated document
    (the caller deep-copies the baseline first). ``predict(model, baseline_doc,
    mutated_doc)`` returns the TYPED delta map (C3) — see
    :func:`predict_violations`, which every shipped operator uses; the shared
    engine is what makes each prediction "derived rather than hard-coded per
    operator".
    """

    name: str
    family: str
    target: str
    apply: Callable[[dict[str, Any], Model, str, Random], dict[str, Any]]
    predict: Callable[[Model, dict[str, Any], dict[str, Any]], dict[str, ExpectedState]]


@dataclass(frozen=True)
class _Template:
    name: str
    family: str
    applies: Callable[[Model, dict[str, Any], dict[str, Any] | None, dict[str, Any]], Any]
    apply: Callable[[dict[str, Any], Model, str, Random], dict[str, Any]]


def _applies_duplicate_covered(model, constraint, ft, doc):
    if ft is None or not isinstance(constraint.get("roles"), list):
        return _SKIP
    covered = [str(r) for r in constraint.get("roles") or []]
    all_roles = [str(r.get("role_name")) for r in ft.get("roles") or []]
    if set(covered) >= set(all_roles):
        return _SKIP  # spanning — exact-duplicate-row's shape
    rows = (doc.get("facts") or {}).get(str(ft.get("id")), [])
    if not any(all(c in row for c in covered) for row in rows):
        return "no baseline fact carries the covered roles; nothing to duplicate"
    return None


def _apply_duplicate_covered(doc, model, ref, rng):
    constraint, ft = _resolve(model, ref)
    ftid = str(ft.get("id"))
    covered = [str(r) for r in constraint.get("roles") or []]
    rows = _facts_of(doc, ftid)
    base = next(row for row in rows if all(c in row for c in covered))
    new: dict[str, Any] = {c: base[c] for c in covered}
    for role in ft.get("roles") or []:
        rn = str(role.get("role_name"))
        if rn in new:
            continue
        oid = str(role.get("object_type"))
        if _is_entity(model, oid):
            avoid = {_key(base.get(rn))} | {_key(v) for v in new.values()}
            members = [m for m in _existing_members(doc, model, oid) if _key(m) not in avoid]
            new[rn] = members[0] if members else _fresh_identifier(doc, model, oid, rng)
        else:
            new[rn] = _valid_value(model, ftid, rn, oid, rng, avoid=(base.get(rn),))
    _enforce_value_comparisons(model, ft, new)
    rows.append(new)
    return doc


def _applies_exact_duplicate(model, constraint, ft, doc):
    if ft is None or not isinstance(constraint.get("roles"), list):
        return _SKIP
    covered = [str(r) for r in constraint.get("roles") or []]
    all_roles = [str(r.get("role_name")) for r in ft.get("roles") or []]
    if set(covered) < set(all_roles):
        return _SKIP  # a proper subset — duplicate-covered-role-value's shape
    rows = (doc.get("facts") or {}).get(str(ft.get("id")), [])
    if not any(all(rn in row for rn in all_roles) for row in rows):
        return "no complete baseline fact to duplicate"
    return None


def _apply_exact_duplicate(doc, model, ref, rng):
    _constraint, ft = _resolve(model, ref)
    ftid = str(ft.get("id"))
    all_roles = [str(r.get("role_name")) for r in ft.get("roles") or []]
    rows = _facts_of(doc, ftid)
    base = next(row for row in rows if all(rn in row for rn in all_roles))
    rows.append(dict(base))
    return doc


def _applies_duplicate_joined(model, constraint, ft, doc):
    if ft is not None or constraint.get("scope") != "external" or not constraint.get("role_refs"):
        return _SKIP
    refs = [r for r in constraint.get("role_refs") or [] if isinstance(r, dict)]
    if len({str(r.get("fact_type")) for r in refs}) < 2:
        return _SKIP
    if not _seq_tuples(doc, model, refs):
        return "the baseline join yields zero rows; no joined tuple to duplicate"
    return None


def _apply_duplicate_joined(doc, model, ref, rng):
    constraint, _ft = _resolve(model, ref)
    refs = [r for r in constraint.get("role_refs") or [] if isinstance(r, dict)]
    first = _seq_tuples(doc, model, refs)[0]
    by_ft: dict[str, list[tuple[str, Any]]] = {}
    for one_ref, value in zip(refs, first, strict=True):
        by_ft.setdefault(str(one_ref.get("fact_type")), []).append(
            (str(one_ref.get("role")), value)
        )
    anchor_ids: dict[str, Any] = {}
    for ftid, referenced in by_ft.items():
        ft2 = _ft_by_id(model, ftid)
        row: dict[str, Any] = dict(referenced)
        for role in (ft2 or {}).get("roles") or []:
            rn = str(role.get("role_name"))
            if rn in row:
                continue
            oid = str(role.get("object_type"))
            if _is_entity(model, oid):
                if oid not in anchor_ids:
                    anchor_ids[oid] = _fresh_identifier(doc, model, oid, rng)
                row[rn] = anchor_ids[oid]
            else:
                row[rn] = _valid_value(model, ftid, rn, oid, rng)
        _enforce_value_comparisons(model, ft2 or {}, row)
        _facts_of(doc, ftid).append(row)
    return doc


def _mandatory_role_type(model, constraint, ft) -> str | None:
    role_name = str(constraint.get("role"))
    return _role_object(model).get(str(ft.get("id")), {}).get(role_name)


def _applies_roster_add(model, constraint, ft, doc):
    if ft is None or constraint.get("role") is None:
        return _SKIP
    oid = _mandatory_role_type(model, constraint, ft)
    if oid is None:
        return "the mandatory role's object type does not resolve"
    return None


def _apply_roster_add(doc, model, ref, rng):
    constraint, ft = _resolve(model, ref)
    oid = _mandatory_role_type(model, constraint, ft)
    fresh = _fresh_identifier(doc, model, str(oid), rng)
    doc.setdefault("instances", {}).setdefault(str(oid), []).append(fresh)
    return doc


def _other_ft_with_role(model, host_ftid: str, oid: str) -> tuple[dict[str, Any], str] | None:
    for ft in model.fact_types or []:
        if str(ft.get("id")) == host_ftid:
            continue
        for role in ft.get("roles") or []:
            if str(role.get("object_type")) == str(oid):
                return ft, str(role.get("role_name"))
    return None


def _applies_new_entity_plays(model, constraint, ft, doc):
    if ft is None or constraint.get("role") is None:
        return _SKIP
    oid = _mandatory_role_type(model, constraint, ft)
    if oid is None:
        return "the mandatory role's object type does not resolve"
    if _other_ft_with_role(model, str(ft.get("id")), oid) is None:
        return (
            f"no other fact type carries a role typed {oid!r}; a new instance "
            f"cannot be made observable outside the mandatory role"
        )
    return None


def _apply_new_entity_plays(doc, model, ref, rng):
    constraint, ft = _resolve(model, ref)
    oid = str(_mandatory_role_type(model, constraint, ft))
    other_ft, role_name = _other_ft_with_role(model, str(ft.get("id")), oid)
    fresh = _fresh_identifier(doc, model, oid, rng)
    row = _complete_row(doc, model, other_ft, {role_name: fresh}, rng)
    _facts_of(doc, str(other_ft.get("id"))).append(row)
    return doc


def _pick_disjunctive_member(model, constraint, doc):
    """A universe member playing >=1 disjunctive role that stays OBSERVABLE
    after its disjunctive plays are removed (Pitfall 4's precondition, checked
    against the population rather than assumed)."""
    refs = [r for r in constraint.get("role_refs") or [] if isinstance(r, dict)]
    role_obj = _role_object(model)
    oids = {role_obj.get(str(r.get("fact_type")), {}).get(str(r.get("role"))) for r in refs}
    if len(oids) != 1 or None in oids:
        return None, None
    oid = str(next(iter(oids)))
    ref_ftids = {str(r.get("fact_type")) for r in refs}
    facts = doc.get("facts") or {}
    for member in _existing_members(doc, model, oid):
        member_key = _key(member)
        plays = any(
            member_key == _key(fact.get(str(r.get("role"))))
            for r in refs
            for fact in facts.get(str(r.get("fact_type")), [])
            if str(r.get("role")) in fact
        )
        if not plays:
            continue
        observable = any(
            member_key == _key(value)
            for ftid, rows in facts.items()
            if ftid not in ref_ftids
            for fact in rows
            for value in fact.values()
        ) or any(
            member_key == _key(value)
            for values in (doc.get("instances") or {}).values()
            for value in values
        )
        if observable:
            return member, oid
    return None, oid


def _applies_remove_disjunctive(model, constraint, ft, doc):
    if not constraint.get("role_refs"):
        return _SKIP
    member, _oid = _pick_disjunctive_member(model, constraint, doc)
    if member is None:
        return (
            "no member both plays a disjunctive role and stays observable after "
            "removal — deleting the last observation self-cancels under the "
            "closed world (Pitfall 4)"
        )
    return None


def _apply_remove_disjunctive(doc, model, ref, rng):
    constraint, _ft = _resolve(model, ref)
    member, _oid = _pick_disjunctive_member(model, constraint, doc)
    member_key = _key(member)
    for one_ref in constraint.get("role_refs") or []:
        ftid = str(one_ref.get("fact_type"))
        role = str(one_ref.get("role"))
        rows = _facts_of(doc, ftid)
        doc["facts"][ftid] = [
            fact for fact in rows if not (role in fact and _key(fact[role]) == member_key)
        ]
    return doc


def _internal_frequency_groups(constraint, ft, doc):
    covered = [str(r) for r in constraint.get("roles") or []]
    groups: dict[tuple, tuple[tuple[Any, ...], int]] = {}
    for fact in (doc.get("facts") or {}).get(str(ft.get("id")), []):
        if any(rn not in fact for rn in covered):
            continue
        values = tuple(fact[rn] for rn in covered)
        key = tuple(_key(v) for v in values)
        original, count = groups.get(key, (values, 0))
        groups[key] = (original, count + 1)
    return covered, groups


def _frequency_min_gate(constraint) -> str | None:
    minimum = (constraint.get("bound") or {}).get("min")
    if minimum is None:
        return "no min bound declared; there is no lower boundary to fall below"
    if minimum <= 1:
        return (
            "occurring-groups semantics (constraint-reference.md:360): at min=1 the "
            "below-bound group does not occur, so the lower boundary is unreachable "
            "by deletion"
        )
    return None


def _applies_drop_from_group(model, constraint, ft, doc):
    if ft is None or not constraint.get("roles"):
        return _SKIP
    gate = _frequency_min_gate(constraint)
    if gate is not None:
        return gate
    minimum = (constraint.get("bound") or {}).get("min")
    _covered, groups = _internal_frequency_groups(constraint, ft, doc)
    if not any(count == minimum for _v, count in groups.values()):
        return f"no group sits exactly at min={minimum}; dropping one fact cannot cross it"
    return None


def _remove_one_from_min_group(doc, model, ref, *, last: bool):
    constraint, ft = _resolve(model, ref)
    minimum = (constraint.get("bound") or {}).get("min")
    covered, groups = _internal_frequency_groups(constraint, ft, doc)
    at_min = sorted(
        (key for key, (_v, count) in groups.items() if count == minimum), key=repr
    )
    target_key = at_min[-1] if last else at_min[0]
    rows = _facts_of(doc, str(ft.get("id")))
    for index, fact in enumerate(rows):
        if all(rn in fact for rn in covered) and (
            tuple(_key(fact[rn]) for rn in covered) == target_key
        ):
            del rows[index]
            break
    return doc


def _apply_drop_from_group(doc, model, ref, rng):
    return _remove_one_from_min_group(doc, model, ref, last=False)


def _apply_remove_last_covering(doc, model, ref, rng):
    return _remove_one_from_min_group(doc, model, ref, last=True)


def _applies_add_past_ceiling(model, constraint, ft, doc):
    if not constraint.get("roles") and constraint.get("scope") == "external":
        return (
            "external frequency ceiling amplification requires join-row growth that "
            "cascades through the anchor fact types' own constraints (not derivable)"
        )
    if ft is None or not constraint.get("roles"):
        return _SKIP
    maximum = (constraint.get("bound") or {}).get("max")
    if maximum is None:
        return "no max bound declared; there is no ceiling to exceed"
    _covered, groups = _internal_frequency_groups(constraint, ft, doc)
    largest = max((count for _v, count in groups.values()), default=0)
    needed = maximum + 1 - largest
    if needed > _AMPLIFICATION_CEILING:
        return (
            f"bound-beyond-generation-ceiling: exceeding max={maximum} needs {needed} "
            f"added facts, past the {_AMPLIFICATION_CEILING}-fact ceiling (T-02-19)"
        )
    return None


def _apply_add_past_ceiling(doc, model, ref, rng):
    constraint, ft = _resolve(model, ref)
    ftid = str(ft.get("id"))
    maximum = (constraint.get("bound") or {}).get("max")
    covered, groups = _internal_frequency_groups(constraint, ft, doc)
    ordered = sorted(groups.items(), key=lambda item: (-item[1][1], repr(item[0])))
    group_values = ordered[0][1][0]
    count = ordered[0][1][1]
    needed = maximum + 1 - count
    for _ in range(needed):
        fixed = dict(zip(covered, group_values, strict=True))
        row = _complete_row(doc, model, ft, fixed, rng, fresh_entities=True)
        _facts_of(doc, ftid).append(row)
    return doc


def _applies_drop_joined_below_min(model, constraint, ft, doc):
    if ft is not None or constraint.get("scope") != "external" or not constraint.get("role_refs"):
        return _SKIP
    return _frequency_min_gate(constraint)


def _apply_drop_joined_below_min(doc, model, ref, rng):
    constraint, _ft = _resolve(model, ref)
    minimum = (constraint.get("bound") or {}).get("min")
    refs = [r for r in constraint.get("role_refs") or [] if isinstance(r, dict)]
    tuples = _seq_tuples(doc, model, refs)
    counts: dict[tuple, tuple[tuple[Any, ...], int]] = {}
    for values in tuples:
        key = tuple(_key(v) for v in values)
        original, count = counts.get(key, (values, 0))
        counts[key] = (original, count + 1)
    at_min = sorted(
        (original for original, count in counts.values() if count == minimum), key=repr
    )
    if not at_min:
        raise GeneratorError(f"no joined group sits at min={minimum} to drop below")
    target = at_min[0]
    first_ref = refs[0]
    ftid = str(first_ref.get("fact_type"))
    role = str(first_ref.get("role"))
    rows = _facts_of(doc, ftid)
    for index, fact in enumerate(rows):
        if role in fact and _key(fact[role]) == _key(target[0]):
            del rows[index]
            break
    return doc


def _ring_components_of(constraint) -> tuple[str, ...]:
    variant = str(constraint.get("variant"))
    if variant not in _RING_VARIANTS:
        return ()
    return _RING_COMPONENTS.get(variant, (variant,))


def _ring_edges(doc, model, ft) -> tuple[str, str, list[tuple[Any, Any]]]:
    roles = [str(r.get("role_name")) for r in ft.get("roles") or []]
    from_role, to_role = roles[0], roles[1]
    edges = [
        (fact[from_role], fact[to_role])
        for fact in (doc.get("facts") or {}).get(str(ft.get("id")), [])
        if from_role in fact and to_role in fact
    ]
    return from_role, to_role, edges


def _ring_gate(ft) -> Any:
    roles = ft.get("roles") or []
    if len(roles) != 2:
        return "ring host is not binary"
    return None


def _applies_close_3_cycle(model, constraint, ft, doc):
    if ft is None or "acyclic" not in _ring_components_of(constraint):
        return _SKIP
    gate = _ring_gate(ft)
    if gate is not None:
        return gate
    _f, _t, edges = _ring_edges(doc, model, ft)
    keys = {(_key(a), _key(b)) for a, b in edges}
    for a, b in edges:
        for b2, c in edges:
            if (
                _key(b2) == _key(b)
                and len({_key(a), _key(b), _key(c)}) == 3
                and (_key(c), _key(a)) not in keys
            ):
                return None
    return "no open 2-edge path exists to close into a 3-cycle"


def _apply_close_3_cycle(doc, model, ref, rng):
    _constraint, ft = _resolve(model, ref)
    from_role, to_role, edges = _ring_edges(doc, model, ft)
    keys = {(_key(a), _key(b)) for a, b in edges}
    for a, b in edges:
        for b2, c in edges:
            if (
                _key(b2) == _key(b)
                and len({_key(a), _key(b), _key(c)}) == 3
                and (_key(c), _key(a)) not in keys
            ):
                _facts_of(doc, str(ft.get("id"))).append({from_role: c, to_role: a})
                return doc
    raise GeneratorError("close-3-cycle: no open path (applies() should have gated this)")


def _applies_close_2_cycle(model, constraint, ft, doc):
    components = set(_ring_components_of(constraint))
    if ft is None or not components & {"asymmetric", "acyclic", "antisymmetric"}:
        return _SKIP
    gate = _ring_gate(ft)
    if gate is not None:
        return gate
    _f, _t, edges = _ring_edges(doc, model, ft)
    keys = {(_key(a), _key(b)) for a, b in edges}
    for a, b in edges:
        if _key(a) != _key(b) and (_key(b), _key(a)) not in keys:
            return None
    return "no reversible edge exists to close into a 2-cycle"


def _apply_close_2_cycle(doc, model, ref, rng):
    _constraint, ft = _resolve(model, ref)
    from_role, to_role, edges = _ring_edges(doc, model, ft)
    keys = {(_key(a), _key(b)) for a, b in edges}
    sources = {_key(a) for a, _b in edges}
    candidates = [
        (a, b) for a, b in edges if _key(a) != _key(b) and (_key(b), _key(a)) not in keys
    ]
    # Prefer a reversal whose new source is not already a source, so a covered
    # uniqueness on the first role is not violated as a side effect.
    preferred = [(a, b) for a, b in candidates if _key(b) not in sources]
    a, b = (preferred or candidates)[0]
    _facts_of(doc, str(ft.get("id"))).append({from_role: b, to_role: a})
    return doc


def _applies_add_self_loop(model, constraint, ft, doc):
    components = set(_ring_components_of(constraint))
    if ft is None or not components & {"irreflexive", "acyclic", "asymmetric", "intransitive"}:
        return _SKIP
    gate = _ring_gate(ft)
    if gate is not None:
        return gate
    oid = str((ft.get("roles") or [{}])[0].get("object_type"))
    _f, _t, edges = _ring_edges(doc, model, ft)
    keys = {(_key(a), _key(b)) for a, b in edges}
    nodes = _existing_members(doc, model, oid)
    if not any((_key(n), _key(n)) not in keys for n in nodes):
        return "every node already carries a self-loop"
    return None


def _apply_add_self_loop(doc, model, ref, rng):
    _constraint, ft = _resolve(model, ref)
    from_role, to_role, edges = _ring_edges(doc, model, ft)
    keys = {(_key(a), _key(b)) for a, b in edges}
    sources = {_key(a) for a, _b in edges}
    oid = str((ft.get("roles") or [{}])[0].get("object_type"))
    nodes = [n for n in _existing_members(doc, model, oid) if (_key(n), _key(n)) not in keys]
    preferred = [n for n in nodes if _key(n) not in sources]
    node = (preferred or nodes)[0]
    _facts_of(doc, str(ft.get("id"))).append({from_role: node, to_role: node})
    return doc


def _value_occurrence(constraint, model, doc) -> tuple[str, str] | None:
    """(fact_type_id, role_name) of a fact occurrence the constraint governs."""
    role_ref = constraint.get("role_ref")
    if isinstance(role_ref, dict):
        ftid, role = str(role_ref.get("fact_type")), str(role_ref.get("role"))
        for fact in (doc.get("facts") or {}).get(ftid, []):
            if role in fact:
                return ftid, role
        return None
    target = str(constraint.get("object_type"))
    for ft in model.fact_types or []:
        ftid = str(ft.get("id"))
        for role in ft.get("roles") or []:
            if str(role.get("object_type")) != target:
                continue
            rn = str(role.get("role_name"))
            for fact in (doc.get("facts") or {}).get(ftid, []):
                if rn in fact:
                    return ftid, rn
    return None


def _applies_edit_out_of_range(model, constraint, ft, doc):
    if constraint.get("object_type") is None:
        return _SKIP
    if constraint.get("ranges") is not None:
        return "multi-range (`ranges`) out-of-spec synthesis is not implemented"
    if _out_of_spec_value(constraint) is None:
        return "no out-of-spec value derivable for this enum/range's value domain"
    if _value_occurrence(constraint, model, doc) is None:
        return "no governed fact occurrence exists in the baseline to edit"
    return None


def _apply_edit_out_of_range(doc, model, ref, rng):
    constraint, _ft = _resolve(model, ref)
    bad = _out_of_spec_value(constraint)
    ftid, role = _value_occurrence(constraint, model, doc)
    for fact in _facts_of(doc, ftid):
        if role in fact:
            fact[role] = bad
            break
    return doc


def _governed_ft_with_entity_role(constraint, model) -> tuple[dict[str, Any], str] | None:
    role_ref = constraint.get("role_ref")
    candidates: list[tuple[dict[str, Any], str]] = []
    if isinstance(role_ref, dict):
        ft = _ft_by_id(model, str(role_ref.get("fact_type")))
        if ft is not None:
            candidates.append((ft, str(role_ref.get("role"))))
    else:
        target = str(constraint.get("object_type"))
        for ft in model.fact_types or []:
            for role in ft.get("roles") or []:
                if str(role.get("object_type")) == target:
                    candidates.append((ft, str(role.get("role_name"))))
                    break
    for ft, role_name in candidates:
        if any(_is_entity(model, str(r.get("object_type"))) for r in ft.get("roles") or []):
            return ft, role_name
    return None


def _applies_add_out_of_range_new_entity(model, constraint, ft, doc):
    if constraint.get("object_type") is None:
        return _SKIP
    if constraint.get("ranges") is not None:
        return "multi-range (`ranges`) out-of-spec synthesis is not implemented"
    if _out_of_spec_value(constraint) is None:
        return "no out-of-spec value derivable for this enum/range's value domain"
    if _governed_ft_with_entity_role(constraint, model) is None:
        return "no governed fact type carries an entity role to mint a new instance in"
    return None


def _apply_add_out_of_range_new_entity(doc, model, ref, rng):
    constraint, _ft = _resolve(model, ref)
    bad = _out_of_spec_value(constraint)
    ft, role_name = _governed_ft_with_entity_role(constraint, model)
    row = _complete_row(doc, model, ft, {role_name: bad}, rng, fresh_entities=True)
    _facts_of(doc, str(ft.get("id"))).append(row)
    return doc


def _applies_introduce_distinct(model, constraint, ft, doc):
    maximum = (constraint.get("bound") or {}).get("max")
    if maximum is None:
        return "no max bound declared; a distinct instance cannot exceed anything"
    if constraint.get("scope") == "object":
        oid = str(constraint.get("object_type"))
        current = len(_existing_members(doc, model, oid))
    elif constraint.get("scope") == "role":
        role_ref = constraint.get("role_ref") or {}
        ftid, role = str(role_ref.get("fact_type")), str(role_ref.get("role"))
        players = {
            _key(fact[role])
            for fact in (doc.get("facts") or {}).get(ftid, [])
            if role in fact
        }
        current = len(players)
    else:
        return _SKIP
    needed = maximum + 1 - current
    if needed > _AMPLIFICATION_CEILING:
        return (
            f"bound-beyond-generation-ceiling: exceeding max={maximum} needs {needed} "
            f"new instances, past the {_AMPLIFICATION_CEILING}-instance ceiling (T-02-19)"
        )
    return None


def _apply_introduce_distinct(doc, model, ref, rng):
    constraint, _ft = _resolve(model, ref)
    maximum = (constraint.get("bound") or {}).get("max")
    if constraint.get("scope") == "object":
        oid = str(constraint.get("object_type"))
        needed = maximum + 1 - len(_existing_members(doc, model, oid))
        roster = doc.setdefault("instances", {}).setdefault(oid, [])
        for _ in range(max(needed, 1)):
            roster.append(_fresh_identifier(doc, model, oid, rng))
        return doc
    role_ref = constraint.get("role_ref") or {}
    ftid, role = str(role_ref.get("fact_type")), str(role_ref.get("role"))
    ft = _ft_by_id(model, ftid)
    oid = str(_role_object(model).get(ftid, {}).get(role))
    players = {
        _key(fact[role]) for fact in (doc.get("facts") or {}).get(ftid, []) if role in fact
    }
    needed = maximum + 1 - len(players)
    # Prefer EXISTING universe members that do not yet play the role — they add
    # no new-instance exposure; mint fresh only when the universe runs out.
    pool = [m for m in _existing_members(doc, model, oid) if _key(m) not in players]
    for index in range(max(needed, 1)):
        player = pool[index] if index < len(pool) else _fresh_identifier(doc, model, oid, rng)
        row = _complete_row(doc, model, ft, {role: player}, rng, fresh_entities=True)
        _facts_of(doc, ftid).append(row)
    return doc


def _uniqueness_conflict(model, ft, doc, row) -> bool:
    """Would appending ``row`` duplicate a covered internal-uniqueness projection?"""
    ftid = str(ft.get("id"))
    for constraint in ft.get("constraints") or []:
        if constraint.get("type") != "uniqueness" or not isinstance(constraint.get("roles"), list):
            continue
        covered = [str(r) for r in constraint.get("roles") or []]
        if any(rn not in row for rn in covered):
            continue
        key = tuple(_key(row[rn]) for rn in covered)
        for fact in (doc.get("facts") or {}).get(ftid, []):
            if all(rn in fact for rn in covered) and tuple(_key(fact[rn]) for rn in covered) == key:
                return True
    return False


def _subset_candidate(model, constraint, doc) -> tuple[str, dict[str, Any]] | None:
    sub_seq = [r for r in constraint.get("subset_role_seq") or [] if isinstance(r, dict)]
    sup_seq = [r for r in constraint.get("superset_role_seq") or [] if isinstance(r, dict)]
    sub_ftids = {str(r.get("fact_type")) for r in sub_seq}
    if len(sub_ftids) != 1:
        return None
    ftid = next(iter(sub_ftids))
    ft = _ft_by_id(model, ftid)
    if ft is None:
        return None
    roles = [str(r.get("role")) for r in sub_seq]
    role_obj = _role_object(model).get(ftid, {})
    if any(not _is_entity(model, str(role_obj.get(rn))) for rn in roles):
        return None
    sup_keys = {tuple(_key(v) for v in t) for t in _seq_tuples(doc, model, sup_seq)}
    sub_keys = {tuple(_key(v) for v in t) for t in _seq_tuples(doc, model, sub_seq)}
    pools = [_existing_members(doc, model, str(role_obj.get(rn)))[:8] for rn in roles]
    for combo in itertools.product(*pools):
        key = tuple(_key(v) for v in combo)
        if key in sup_keys or key in sub_keys:
            continue
        row = dict(zip(roles, combo, strict=True))
        if _uniqueness_conflict(model, ft, doc, row):
            continue
        return ftid, row
    return None


def _applies_add_missing_subset(model, constraint, ft, doc):
    if not constraint.get("subset_role_seq") or not constraint.get("superset_role_seq"):
        return _SKIP
    if _subset_candidate(model, constraint, doc) is None:
        return (
            "no subset-side tuple constructible from existing instances that is "
            "absent from the superset (or the subset side spans several fact types "
            "or value-typed roles)"
        )
    return None


def _apply_add_missing_subset(doc, model, ref, rng):
    constraint, _ft = _resolve(model, ref)
    ftid, fixed = _subset_candidate(model, constraint, doc)
    ft = _ft_by_id(model, ftid)
    row = _complete_row(doc, model, ft, fixed, rng)
    _facts_of(doc, ftid).append(row)
    return doc


def _equality_side_removal(model, constraint, doc) -> tuple[str, int] | None:
    """(fact_type_id, row_index) whose removal breaks the equality while keeping
    every removed entity value observable elsewhere."""
    facts = doc.get("facts") or {}
    for fld in ("role_seq_b", "role_seq_a"):
        seq = [r for r in constraint.get(fld) or [] if isinstance(r, dict)]
        ftids = {str(r.get("fact_type")) for r in seq}
        if len(ftids) != 1:
            continue
        ftid = next(iter(ftids))
        roles = [str(r.get("role")) for r in seq]
        rows = facts.get(ftid, [])
        for index in range(len(rows) - 1, -1, -1):
            fact = rows[index]
            if any(rn not in fact for rn in roles):
                continue
            observable = all(
                any(
                    _key(value) == _key(other_value)
                    for other_ftid, other_rows in facts.items()
                    for row_index, other in enumerate(other_rows)
                    if (other_ftid, row_index) != (ftid, index)
                    for other_value in other.values()
                )
                for value in fact.values()
            )
            if observable:
                return ftid, index
    return None


def _applies_remove_equality_side(model, constraint, ft, doc):
    if not constraint.get("role_seq_a") or not constraint.get("role_seq_b"):
        return _SKIP
    if str(constraint.get("type")) != "equality":
        return _SKIP
    if _equality_side_removal(model, constraint, doc) is None:
        return (
            "no single-fact-type side carries a removable tuple whose entity values "
            "stay observable (removal would self-cancel under the closed world)"
        )
    return None


def _apply_remove_equality_side(doc, model, ref, rng):
    constraint, _ft = _resolve(model, ref)
    ftid, index = _equality_side_removal(model, constraint, doc)
    del _facts_of(doc, ftid)[index]
    return doc


def _applies_add_overlap(model, constraint, ft, doc):
    if str(constraint.get("type")) != "exclusion":
        return _SKIP
    if not constraint.get("role_seq_a") or not constraint.get("role_seq_b"):
        return _SKIP
    seq_a = [r for r in constraint.get("role_seq_a") or [] if isinstance(r, dict)]
    seq_b = [r for r in constraint.get("role_seq_b") or [] if isinstance(r, dict)]
    if len({str(r.get("fact_type")) for r in seq_b}) != 1:
        return "the overlap side spans several fact types; no single row can create it"
    if not _seq_tuples(doc, model, seq_a):
        return "side A carries no tuples; there is nothing to overlap with"
    return None


def _apply_add_overlap(doc, model, ref, rng):
    constraint, _ft = _resolve(model, ref)
    seq_a = [r for r in constraint.get("role_seq_a") or [] if isinstance(r, dict)]
    seq_b = [r for r in constraint.get("role_seq_b") or [] if isinstance(r, dict)]
    first = _seq_tuples(doc, model, seq_a)[0]
    ftid = str(seq_b[0].get("fact_type"))
    ft = _ft_by_id(model, ftid)
    fixed = {str(r.get("role")): value for r, value in zip(seq_b, first, strict=True)}
    row = _complete_row(doc, model, ft, fixed, rng)
    _facts_of(doc, ftid).append(row)
    return doc




_XOR_MULTIROLE_MECHANISM = (
    "multi-role exclusive-or: the disjunctive half is undefined at arity > 1 "
    "(constraint-reference.md:319-331), so 'plays neither' has no tuple universe"
)


def _xor_player_sets(refs, doc) -> list[set[Any]]:
    facts = doc.get("facts") or {}
    return [
        {
            _key(fact[str(r.get("role"))])
            for fact in facts.get(str(r.get("fact_type")), [])
            if str(r.get("role")) in fact
        }
        for r in refs
    ]


def _applies_play_both(model, constraint, ft, doc):
    refs = _xor_single_role(constraint)
    if refs is None:
        return _XOR_MULTIROLE_MECHANISM
    sets = _xor_player_sets(refs, doc)
    if len(sets) < 2:
        return _SKIP
    if not (sets[0] - sets[1]):
        return "no member plays exactly the first sequence; nothing to double up"
    return None


def _apply_play_both(doc, model, ref, rng):
    constraint, _ft = _resolve(model, ref)
    refs = _xor_single_role(constraint)
    sets = _xor_player_sets(refs, doc)
    only_first = sets[0] - sets[1]
    role_obj = _role_object(model)
    oid = str(role_obj.get(str(refs[0].get("fact_type")), {}).get(str(refs[0].get("role"))))
    member = next(
        m for m in _existing_members(doc, model, oid) if _key(m) in only_first
    )
    target = refs[1]
    ftid = str(target.get("fact_type"))
    ft = _ft_by_id(model, ftid)
    row = _complete_row(doc, model, ft, {str(target.get("role")): member}, rng)
    _facts_of(doc, ftid).append(row)
    return doc


def _pick_xor_removable(model, constraint, doc):
    refs = _xor_single_role(constraint)
    role_obj = _role_object(model)
    oids = {role_obj.get(str(r.get("fact_type")), {}).get(str(r.get("role"))) for r in refs}
    if len(oids) != 1 or None in oids:
        return None, None
    oid = str(next(iter(oids)))
    ref_ftids = {str(r.get("fact_type")) for r in refs}
    facts = doc.get("facts") or {}
    sets = _xor_player_sets(refs, doc)
    played = set().union(*sets) if sets else set()
    for member in _existing_members(doc, model, oid):
        member_key = _key(member)
        if member_key not in played:
            continue
        observable = any(
            member_key == _key(value)
            for ftid, rows in facts.items()
            if ftid not in ref_ftids
            for fact in rows
            for value in fact.values()
        ) or any(
            member_key == _key(value)
            for values in (doc.get("instances") or {}).values()
            for value in values
        )
        if observable:
            return member, refs
    return None, refs


def _applies_play_neither(model, constraint, ft, doc):
    refs = _xor_single_role(constraint)
    if refs is None:
        return _XOR_MULTIROLE_MECHANISM
    member, _refs = _pick_xor_removable(model, constraint, doc)
    if member is None:
        return (
            "no member both plays an exclusive-or role and stays observable after "
            "removal — the closed world would self-cancel the mutation"
        )
    return None


def _apply_play_neither(doc, model, ref, rng):
    constraint, _ft = _resolve(model, ref)
    member, refs = _pick_xor_removable(model, constraint, doc)
    member_key = _key(member)
    for one_ref in refs:
        ftid = str(one_ref.get("fact_type"))
        role = str(one_ref.get("role"))
        rows = _facts_of(doc, ftid)
        doc["facts"][ftid] = [
            fact for fact in rows if not (role in fact and _key(fact[role]) == member_key)
        ]
    return doc


def _invertible_fact(model, constraint, ft, doc) -> int | None:
    operand_a, operand_b = _normalize_comparison_operands(model, constraint, ft)
    if operand_a.kind != "role" or operand_b.kind != "role":
        return None
    role_a, role_b = operand_a.role, operand_b.role
    assert role_a is not None and role_b is not None
    op = str(constraint.get("operator"))
    if op not in ("<", "<=", ">", ">="):
        return None
    for index, fact in enumerate((doc.get("facts") or {}).get(str(ft.get("id")), [])):
        if role_a not in fact or role_b not in fact:
            continue
        a, b = fact[role_a], fact[role_b]
        if _key(a) != _key(b) and _compare_scalar(a, op, b) and not _compare_scalar(b, op, a):
            return index
    return None


def _applies_invert_vc(model, constraint, ft, doc):
    if ft is None:
        return _SKIP
    op = str(constraint.get("operator"))
    if op not in ("<", "<=", ">", ">="):
        return f"operator {op!r} is symmetric under operand swap; inversion cannot violate it"
    operand_a, operand_b = _normalize_comparison_operands(model, constraint, ft)
    if operand_a.kind != "role" or operand_b.kind != "role":
        return "comparison does not carry two intra-fact roles to invert"
    if _invertible_fact(model, constraint, ft, doc) is None:
        return "no fact carries a strictly-ordered operand pair to invert"
    return None


def _apply_invert_vc(doc, model, ref, rng):
    constraint, ft = _resolve(model, ref)
    index = _invertible_fact(model, constraint, ft, doc)
    assert index is not None
    fact = _facts_of(doc, str(ft.get("id")))[index]
    operand_a, operand_b = _normalize_comparison_operands(model, constraint, ft)
    role_a, role_b = operand_a.role, operand_b.role
    assert role_a is not None and role_b is not None
    fact[role_a], fact[role_b] = fact[role_b], fact[role_a]
    return doc


def _applies_place_two_subtypes(model, constraint, ft, doc):
    if not constraint.get("supertype") or not constraint.get("subtypes"):
        return _SKIP
    if not constraint.get("exclusive"):
        return "the partition does not assert exclusivity; two memberships violate nothing"
    subtypes = [str(s) for s in constraint.get("subtypes") or []]
    if len(subtypes) < 2:
        return "fewer than two subtypes; no pair to place an instance into"
    if not _existing_members(doc, model, str(constraint.get("supertype"))):
        return "the supertype universe is empty; no instance to place"
    return None


def _apply_place_two_subtypes(doc, model, ref, rng):
    constraint, _ft = _resolve(model, ref)
    subtypes = [str(s) for s in constraint.get("subtypes") or []]
    member = _existing_members(doc, model, str(constraint.get("supertype")))[0]
    instances = doc.setdefault("instances", {})
    for subtype in subtypes[:2]:
        instances.setdefault(subtype, []).append(member)
    return doc


def _subtype_assertions(model, constraint, doc) -> list[tuple[str, Any]]:
    """(subtype, member) pairs asserted via rosters (the removable form)."""
    out = []
    for subtype in constraint.get("subtypes") or []:
        for value in (doc.get("instances") or {}).get(str(subtype), []):
            out.append((str(subtype), value))
    return out


def _applies_remove_all_subtypes(model, constraint, ft, doc):
    if not constraint.get("supertype") or not constraint.get("subtypes"):
        return _SKIP
    if not constraint.get("exhaustive"):
        return "the partition does not assert exhaustiveness; an uncovered instance violates nothing"
    if not _subtype_assertions(model, constraint, doc):
        return (
            "the baseline asserts no roster subtype membership (derivation-only); "
            "there is nothing to remove without first asserting one"
        )
    return None


def _apply_remove_all_subtypes(doc, model, ref, rng):
    constraint, _ft = _resolve(model, ref)
    assertions = _subtype_assertions(model, constraint, doc)
    _subtype, member = assertions[0]
    member_key = _key(member)
    instances = doc.setdefault("instances", {})
    for subtype in constraint.get("subtypes") or []:
        values = instances.get(str(subtype), [])
        instances[str(subtype)] = [v for v in values if _key(v) != member_key]
    return doc


def _coverage_target_ft(constraint, ft) -> str | None:
    if ft is not None:
        return str(ft.get("id"))
    refs = [r for r in constraint.get("role_refs") or [] if isinstance(r, dict)]
    if refs:
        return str(refs[0].get("fact_type"))
    return None


def _applies_drop_covers(model, constraint, ft, doc):
    if str(constraint.get("type")) not in _MANDATORY_RELEVANT:
        return _SKIP
    target = _coverage_target_ft(constraint, ft)
    covers = list((doc.get("population") or {}).get("covers") or [])
    if target is None or target not in covers:
        return "the subject fact type is not declared in covers; nothing to omit"
    return None


def _apply_drop_covers(doc, model, ref, rng):
    constraint, ft = _resolve(model, ref)
    target = _coverage_target_ft(constraint, ft)
    header = doc.setdefault("population", {})
    header["covers"] = [c for c in header.get("covers") or [] if c != target]
    return doc


def first_implemented_inline_ref(model: Model, ftid: str) -> str | None:
    """The ref `empty-fact-type` binds to: one case per fact type, not one per
    inline constraint, so the cross product does not emit duplicate populations."""
    ft = _ft_by_id(model, ftid)
    for index, constraint in enumerate((ft or {}).get("constraints") or []):
        if str(constraint.get("type")) in IMPLEMENTED_FAMILIES:
            return positional_constraint_ref(ftid, index)
    return None


def _applies_empty_ft(model, constraint, ft, doc):
    if ft is None:
        return _SKIP
    ftid = str(ft.get("id"))
    if not (doc.get("facts") or {}).get(ftid):
        return "the fact type is already empty; there is nothing to cascade"
    return None


def _apply_empty_ft(doc, model, ref, rng):
    _constraint, ft = _resolve(model, ref)
    (doc.get("facts") or {}).pop(str(ft.get("id")), None)
    return doc


def _exists_atom_safe_for_removal(model: Model, constraint: dict[str, Any]) -> bool:
    """Only remove witness rows from relations private to this exists rule."""
    return _has_private_exists_sources(model, constraint)


def _applies_remove_exists_witness(model, constraint, _ft, doc):
    def has_literal_binding(atoms: Any) -> bool:
        return isinstance(atoms, list) and any(
            isinstance(atom, Mapping)
            and isinstance(atom.get("bind"), Mapping)
            and any(
                not isinstance(value, str) or not value.startswith("$")
                for value in atom["bind"].values()
            )
            for atom in atoms
        )

    if has_literal_binding(constraint.get("antecedent")):
        return "literal role bindings are unsupported by the exists mutation planner"
    consequent = constraint.get("consequent")
    exists = consequent.get("exists") if isinstance(consequent, Mapping) else None
    exists_atoms = exists.get("atoms") if isinstance(exists, Mapping) else None
    if has_literal_binding(exists_atoms):
        return "literal role bindings are unsupported by the exists mutation planner"
    plan = _guarded_modular_repair_plan(constraint)
    if plan is None:
        return "only the bounded two-atom modular-residue exists shape is supported"
    if not _exists_atom_safe_for_removal(model, constraint):
        return "exists source relations are shared with another constraint or derivation"
    facts = doc.get("facts") or {}
    covers = set((doc.get("population") or {}).get("covers") or [])
    missing = sorted(
        str(atom.get("fact_type"))
        for atom in plan["atoms"]
        if str(atom.get("fact_type")) not in covers
    )
    if missing:
        return f"baseline does not cover exists source relations {missing}"
    antecedent_bindings = _guarded_antecedent_bindings(constraint, facts)
    if antecedent_bindings is None:
        return "baseline antecedent bindings exceed the guarded-oracle work limit"
    if not antecedent_bindings:
        return (
            "baseline has zero antecedent bindings; no witness can be selected "
            "for removal"
        )
    if _guarded_exists_witness(constraint, facts) is not True:
        return "baseline has no fully-defined witness for every antecedent binding"
    return None


def _apply_remove_exists_witness(doc, model, ref, rng):
    constraint, _ft = _resolve(model, ref)
    plan = _guarded_modular_repair_plan(constraint)
    if plan is None:
        raise GeneratorError(f"{ref}: unsupported guarded-exists mutation shape")
    bindings = _guarded_antecedent_bindings(constraint, doc.get("facts") or {})
    if not bindings:
        raise GeneratorError(f"{ref}: no antecedent binding can be selected for witness removal")
    ordered = sorted(bindings, key=lambda row: repr(sorted(row.items())))
    selected = rng.choice(ordered)
    first = plan["atoms"][0]
    ftid = str(first.get("fact_type"))
    role_bindings = first.get("bind") or {}
    anchors = {
        str(role): selected[str(variable)[1:]]
        for role, variable in role_bindings.items()
        if isinstance(variable, str)
        and variable.startswith("$")
        and str(variable)[1:] in selected
    }
    if not anchors:
        raise GeneratorError(f"{ref}: first exists atom has no antecedent anchor")
    rows = (doc.get("facts") or {}).get(ftid, [])
    kept = [
        row
        for row in rows
        if not all(
            role in row and _key(row[role]) == _key(value)
            for role, value in anchors.items()
        )
    ]
    if len(kept) == len(rows):
        raise GeneratorError(f"{ref}: selected antecedent binding had no removable witness rows")
    doc.setdefault("facts", {})[ftid] = kept
    return doc


OPERATORS: dict[str, tuple[_Template, ...]] = {
    "uniqueness": (
        _Template("duplicate-covered-role-value", "uniqueness", _applies_duplicate_covered, _apply_duplicate_covered),
        _Template("exact-duplicate-row", "uniqueness", _applies_exact_duplicate, _apply_exact_duplicate),
        _Template("duplicate-joined-tuple", "uniqueness", _applies_duplicate_joined, _apply_duplicate_joined),
    ),
    "mandatory": (
        _Template("roster-add-instance", "mandatory", _applies_roster_add, _apply_roster_add),
        _Template("new-entity-plays-role", "mandatory", _applies_new_entity_plays, _apply_new_entity_plays),
    ),
    "mandatory-disjunctive": (
        _Template("remove-all-disjunctive-role-plays", "mandatory-disjunctive", _applies_remove_disjunctive, _apply_remove_disjunctive),
    ),
    "frequency": (
        _Template("drop-fact-from-group", "frequency", _applies_drop_from_group, _apply_drop_from_group),
        _Template("add-facts-past-ceiling", "frequency", _applies_add_past_ceiling, _apply_add_past_ceiling),
        _Template("remove-fact-from-last-covering-group", "frequency", _applies_drop_from_group, _apply_remove_last_covering),
        _Template("drop-joined-group-below-min", "frequency", _applies_drop_joined_below_min, _apply_drop_joined_below_min),
    ),
    "ring": (
        _Template("close-3-cycle", "ring", _applies_close_3_cycle, _apply_close_3_cycle),
        _Template("close-2-cycle", "ring", _applies_close_2_cycle, _apply_close_2_cycle),
        _Template("add-self-loop", "ring", _applies_add_self_loop, _apply_add_self_loop),
    ),
    "value": (
        _Template("edit-value-out-of-range", "value", _applies_edit_out_of_range, _apply_edit_out_of_range),
        _Template("add-fact-with-out-of-range-new-entity", "value", _applies_add_out_of_range_new_entity, _apply_add_out_of_range_new_entity),
    ),
    "cardinality": (
        _Template("introduce-distinct-instance", "cardinality", _applies_introduce_distinct, _apply_introduce_distinct),
    ),
    "subset": (
        _Template("add-player-missing-subset-role", "subset", _applies_add_missing_subset, _apply_add_missing_subset),
    ),
    "equality": (
        _Template("remove-tuple-from-equality-side", "equality", _applies_remove_equality_side, _apply_remove_equality_side),
    ),
    "exclusion": (
        _Template("add-overlapping-tuple", "exclusion", _applies_add_overlap, _apply_add_overlap),
    ),
    "exclusive-or": (
        _Template("play-both-exclusive-or-roles", "exclusive-or", _applies_play_both, _apply_play_both),
        _Template("play-neither-exclusive-or-role", "exclusive-or", _applies_play_neither, _apply_play_neither),
    ),
    "value-comparison": (
        _Template("invert-value-comparison-operands", "value-comparison", _applies_invert_vc, _apply_invert_vc),
    ),
    "subtype-partition": (
        _Template("place-instance-in-two-subtypes", "subtype-partition", _applies_place_two_subtypes, _apply_place_two_subtypes),
        _Template("remove-instance-from-all-subtypes", "subtype-partition", _applies_remove_all_subtypes, _apply_remove_all_subtypes),
    ),
    "coverage-omission": (
        _Template("drop-fact-type-from-covers", "coverage-omission", _applies_drop_covers, _apply_drop_covers),
    ),
    "vacuity-cascade": (
        _Template("empty-fact-type", "vacuity-cascade", _applies_empty_ft, _apply_empty_ft),
    ),
}


def _templates_for(model: Model, ref: str, constraint: dict[str, Any], ft: dict[str, Any] | None):
    ctype = str(constraint.get("type"))
    templates = list(OPERATORS.get(ctype, ()))
    if ctype in _MANDATORY_RELEVANT:
        templates.extend(OPERATORS["coverage-omission"])
    if ft is not None and first_implemented_inline_ref(model, str(ft.get("id"))) == ref:
        templates.extend(OPERATORS["vacuity-cascade"])
    return templates


def operators_for(
    model: Model, constraint_ref: str, baseline_doc: dict[str, Any]
) -> tuple[list[Mutation], list[dict[str, Any]]]:
    """The applicable operators for ONE constraint, plus its not-derivable records.

    Applicability is decided against the model AND the baseline population —
    isolation and even applicability are properties of the (model, constraint,
    operator) triple (D-05'), so a static table cannot answer this. Every
    semantic stand-down is a RECORD with its mechanism named, never a silent
    skip; shape dispatch (internal vs external, single-role vs multi-role) is
    dispatch, not a stand-down.
    """
    constraint, ft = _resolve(model, constraint_ref)
    ctype = str(constraint.get("type"))
    if ctype == "anchored":
        return [], [{"constraint_ref": constraint_ref, "family": ctype, "operator": None,
                     "mechanism": "population mutation cannot supply a bound source anchor"}]
    if ctype not in IMPLEMENTED_FAMILIES:
        return [], []
    if ctype == "guarded":
        consequent = constraint.get("consequent")
        exists = consequent.get("exists") if isinstance(consequent, dict) else None
        if isinstance(exists, dict):
            operator = "remove-exists-witness-for-antecedent-binding"
            outcome = _applies_remove_exists_witness(model, constraint, ft, baseline_doc)
            if outcome is None:
                return [
                    Mutation(
                        name=operator,
                        family=ctype,
                        target=constraint_ref,
                        apply=_apply_remove_exists_witness,
                        predict=predict_violations,
                    )
                ], []
            return [], [
                {
                    "constraint_ref": constraint_ref,
                    "family": ctype,
                    "operator": operator,
                    "mechanism": outcome,
                }
            ]
        # Preserve the explicit post-MVP frontier for the guarded forms that
        # Phase 6 did not extend (atom, comparison, and absence consequents).
        return [], [
            {
                "constraint_ref": constraint_ref,
                "family": ctype,
                "operator": None,
                "mechanism": (
                    "guarded violating-witness synthesis is a post-MVP frontier; "
                    "no shipped operator claims coverage for this family"
                ),
            }
        ]
    mutations: list[Mutation] = []
    stand_downs: list[dict[str, Any]] = []
    family_native = 0
    for template in _templates_for(model, constraint_ref, constraint, ft):
        outcome = template.applies(model, constraint, ft, baseline_doc)
        if outcome is _SKIP:
            continue
        if outcome is None:
            if template.family == ctype:
                family_native += 1
            mutations.append(
                Mutation(
                    name=template.name,
                    family=template.family,
                    target=constraint_ref,
                    apply=template.apply,
                    predict=predict_violations,
                )
            )
        else:
            if template.family == ctype:
                family_native += 1  # a recorded stand-down is an answer, not a gap
            stand_downs.append(
                {
                    "constraint_ref": constraint_ref,
                    "family": ctype,
                    "operator": template.name,
                    "mechanism": str(outcome),
                }
            )
    # A constraint whose only cases are cross-cutting (vacuity cascade / coverage
    # omission) has NO family-native violating operator — record that rather than
    # letting the cascade case make the gap look covered.
    if family_native == 0:
        detail = (
            f"variant {constraint.get('variant')!r}" if ctype == "ring" else f"shape of {ctype!r}"
        )
        stand_downs.append(
            {
                "constraint_ref": constraint_ref,
                "family": ctype,
                "operator": None,
                "mechanism": (
                    f"no shipped operator violates this {detail}; the measured operator "
                    f"set does not cover it"
                ),
            }
        )
    return mutations, stand_downs


def enumerate_violating(
    model: Model, baseline_doc: dict[str, Any]
) -> tuple[list[tuple[str, Mutation]], list[dict[str, Any]]]:
    """The full (constraint x applicable operator) cross product for one model,
    plus every not-derivable record."""
    cases: list[tuple[str, Mutation]] = []
    stand_downs: list[dict[str, Any]] = []
    for ref, _constraint, _ft in _constraint_iter_with_ref(model):
        mutations, downs = operators_for(model, ref, baseline_doc)
        cases.extend((ref, mutation) for mutation in mutations)
        stand_downs.extend(downs)
    return cases, stand_downs


def family_coverage(model: Model, baseline_doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Per implemented family the model declares: the applicable operator names
    and the not-derivable records. Derived from ``checker.IMPLEMENTED_FAMILIES``
    — never a hand-typed list (research assumption A4)."""
    declared: dict[str, dict[str, Any]] = {}
    for ref, constraint, _ft in _constraint_iter_with_ref(model):
        family = str(constraint.get("type"))
        if family not in IMPLEMENTED_FAMILIES:
            continue
        entry = declared.setdefault(family, {"operators": set(), "not_derivable": []})
        mutations, downs = operators_for(model, ref, baseline_doc)
        entry["operators"].update(m.name for m in mutations)
        entry["not_derivable"].extend(downs)
    for entry in declared.values():
        entry["operators"] = sorted(entry["operators"])
    return declared


def compare_observed(
    predicted: dict[str, ExpectedState],
    baseline_report: CheckReport,
    report: CheckReport,
    *,
    target: str,
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    """The observed verdict delta and every typed prediction/observation
    discrepancy (empty list == the case is admissible).

    The observed set is the delta over ALL FIVE verdict states — the only
    condition is that the verdict CHANGED from the baseline. Collecting it as one
    expression is what stops the deletion trap (Qwen-MEDIUM): deletion operators
    predict ``no-subjects``/``vacuous``, and a two-step collection where a
    developer writes ``{fail, warning}`` and forgets to union the vacuous
    transitions makes every deletion operator spuriously mismatch.

    Restricting it to ``fail``/``warning``/``vacuous`` (WR-05) had the same shape
    one state over: :func:`expected_state` can predict a ``{satisfied, pass}`` or
    ``{satisfied, unchecked}`` transition — a mutation that incidentally repairs
    a deontic violation, or a ``vacuous -> pass`` transition when rows land in a
    previously-empty join (the baseline is only guaranteed free of ALETHIC
    fails). Any such prediction was unmatchable by construction: the ref landed
    in ``set(predicted) - set(observed)`` and the whole ``gnd synth`` run aborted
    at exit 6 as a prediction/observation mismatch, pointing at the checker when
    the cause was the filter — and a reader is instructed to treat that
    quarantine as a candidate checker defect to reproduce, fix and promote.

    An EMPTY observed set is a discrepancy through the same path: a silent no-op
    contributes a conforming datum labelled violating, inflating false-fail and
    depressing false-pass at once.
    """
    baseline = {v.constraint_ref: v.verdict for v in baseline_report.verdicts}
    observed = {
        v.constraint_ref: v.verdict
        for v in report.verdicts
        if v.verdict != baseline.get(v.constraint_ref)
    }

    discrepancies: list[dict[str, Any]] = []

    def record(ref: str, expectation: ExpectedState | None, observed_verdict: str | None) -> None:
        discrepancies.append(
            {
                "constraint_ref": ref,
                "predicted": expectation.model_dump() if expectation is not None else None,
                "observed_verdict": observed_verdict,
                "kind": "prediction-observation-mismatch",
            }
        )

    if not observed:
        if predicted:
            for ref, expectation in sorted(predicted.items()):
                record(ref, expectation, None)
        else:
            record(target, None, None)
        return observed, discrepancies

    for ref in sorted(set(predicted) - set(observed)):
        record(ref, predicted[ref], None)
    for ref in sorted(set(observed) - set(predicted)):
        record(ref, None, observed[ref])
    for ref in sorted(set(predicted) & set(observed)):
        if predicted[ref].expected_verdict != observed[ref]:
            record(ref, predicted[ref], observed[ref])
    return observed, discrepancies


class PredictionMismatch(Exception):
    """The observed violation set disagrees with the model-derived prediction.

    Deliberately ambiguous about cause, because the ambiguity is real: either
    the OPERATOR is wrong or the CHECKER is — reproduce before adjusting the
    prediction. The resolution is QUARANTINE-and-flag at exit 6 (C1), never
    discard: a discarded case is exactly how a present-day checker defect
    vanishes from its own evaluation corpus. The sidecar's prediction is the
    authoritative ground truth and is NEVER relabelled to match observation.
    """

    def __init__(
        self,
        doc: dict[str, Any],
        predicted: dict[str, ExpectedState],
        observed: dict[str, str],
        discrepancies: list[dict[str, Any]],
        mutation_name: str,
    ) -> None:
        self.doc = doc
        self.predicted = predicted
        self.observed = observed
        self.discrepancies = discrepancies
        self.mutation_name = mutation_name
        super().__init__(
            f"{mutation_name}: predicted {sorted(predicted)} but observed "
            f"{sorted(observed)} — either the operator is wrong or the CHECKER is; "
            f"reproduce before adjusting the prediction. The case is quarantined, "
            f"never discarded or relabelled (C1)."
        )


@dataclass
class ViolatingCase:
    """One admitted violating population: the mutated document, its typed
    prediction, the observed delta, and the per-case isolation verdict."""

    doc: dict[str, Any]
    predicted: dict[str, ExpectedState]
    observed: dict[str, str]
    isolating: bool
    report: CheckReport


def emit_violating(
    model: Model,
    baseline_doc: dict[str, Any],
    baseline_report: CheckReport,
    mutation: Mutation,
    constraint_ref: str,
    path: str | Path,
    rng: Random,
) -> ViolatingCase:
    """Apply one mutation, write the population, and admit it ONLY after the
    real checker confirms the model-derived prediction.

    1. Deep-copy the baseline DOCUMENT and apply the operator — never mutate a
       loaded ``Population`` (frozen, content-digested; a mutated one fails
       closed at ``check()`` by design).
    2. ``label: violating`` in the header (Phase 1 D-10 — the only
       population-file change this class needs).
    3. Write, then re-load through ``load_population``: a
       ``PopulationValidationError`` here is a GENERATOR bug (exit 5) — a
       structurally invalid population contributes zero verdicts and therefore
       zero errors.
    4-5. Check with the REAL checker and compare the observed delta (one
       expression, vacuous included) against the typed prediction; any
       difference raises :class:`PredictionMismatch` for the caller to
       QUARANTINE at exit 6 (C1). Exit 5 stays reserved for structural
       generator errors — never for a prediction/observation disagreement.
    """
    doc = copy.deepcopy(baseline_doc)
    doc = mutation.apply(doc, model, constraint_ref, rng)
    doc.setdefault("population", {})["label"] = "violating"

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    try:
        population = load_population(str(path), model=model)
    except PopulationValidationError as error:
        raise GeneratorError(
            f"{mutation.name} on {constraint_ref}: the mutated population failed "
            f"re-admission (a GENERATOR bug, exit 5 — it would contribute no "
            f"verdicts and therefore no errors): {error}"
        ) from error

    report = check(model, population)
    predicted = mutation.predict(model, baseline_doc, doc)
    observed, discrepancies = compare_observed(
        predicted, baseline_report, report, target=constraint_ref
    )
    if discrepancies:
        raise PredictionMismatch(doc, predicted, observed, discrepancies, mutation.name)
    return ViolatingCase(
        doc=doc,
        predicted=predicted,
        observed=observed,
        isolating=len(predicted) == 1,
        report=report,
    )



# Historical qualifications are serialized by existing callers.
Mutation.__module__ = 'gnd.synth.mutate'
_Template.__module__ = 'gnd.synth.mutate'
_applies_duplicate_covered.__module__ = 'gnd.synth.mutate'
_apply_duplicate_covered.__module__ = 'gnd.synth.mutate'
_applies_exact_duplicate.__module__ = 'gnd.synth.mutate'
_apply_exact_duplicate.__module__ = 'gnd.synth.mutate'
_applies_duplicate_joined.__module__ = 'gnd.synth.mutate'
_apply_duplicate_joined.__module__ = 'gnd.synth.mutate'
_mandatory_role_type.__module__ = 'gnd.synth.mutate'
_applies_roster_add.__module__ = 'gnd.synth.mutate'
_apply_roster_add.__module__ = 'gnd.synth.mutate'
_other_ft_with_role.__module__ = 'gnd.synth.mutate'
_applies_new_entity_plays.__module__ = 'gnd.synth.mutate'
_apply_new_entity_plays.__module__ = 'gnd.synth.mutate'
_pick_disjunctive_member.__module__ = 'gnd.synth.mutate'
_applies_remove_disjunctive.__module__ = 'gnd.synth.mutate'
_apply_remove_disjunctive.__module__ = 'gnd.synth.mutate'
_internal_frequency_groups.__module__ = 'gnd.synth.mutate'
_frequency_min_gate.__module__ = 'gnd.synth.mutate'
_applies_drop_from_group.__module__ = 'gnd.synth.mutate'
_remove_one_from_min_group.__module__ = 'gnd.synth.mutate'
_apply_drop_from_group.__module__ = 'gnd.synth.mutate'
_apply_remove_last_covering.__module__ = 'gnd.synth.mutate'
_applies_add_past_ceiling.__module__ = 'gnd.synth.mutate'
_apply_add_past_ceiling.__module__ = 'gnd.synth.mutate'
_applies_drop_joined_below_min.__module__ = 'gnd.synth.mutate'
_apply_drop_joined_below_min.__module__ = 'gnd.synth.mutate'
_ring_components_of.__module__ = 'gnd.synth.mutate'
_ring_edges.__module__ = 'gnd.synth.mutate'
_ring_gate.__module__ = 'gnd.synth.mutate'
_applies_close_3_cycle.__module__ = 'gnd.synth.mutate'
_apply_close_3_cycle.__module__ = 'gnd.synth.mutate'
_applies_close_2_cycle.__module__ = 'gnd.synth.mutate'
_apply_close_2_cycle.__module__ = 'gnd.synth.mutate'
_applies_add_self_loop.__module__ = 'gnd.synth.mutate'
_apply_add_self_loop.__module__ = 'gnd.synth.mutate'
_value_occurrence.__module__ = 'gnd.synth.mutate'
_applies_edit_out_of_range.__module__ = 'gnd.synth.mutate'
_apply_edit_out_of_range.__module__ = 'gnd.synth.mutate'
_governed_ft_with_entity_role.__module__ = 'gnd.synth.mutate'
_applies_add_out_of_range_new_entity.__module__ = 'gnd.synth.mutate'
_apply_add_out_of_range_new_entity.__module__ = 'gnd.synth.mutate'
_applies_introduce_distinct.__module__ = 'gnd.synth.mutate'
_apply_introduce_distinct.__module__ = 'gnd.synth.mutate'
_uniqueness_conflict.__module__ = 'gnd.synth.mutate'
_subset_candidate.__module__ = 'gnd.synth.mutate'
_applies_add_missing_subset.__module__ = 'gnd.synth.mutate'
_apply_add_missing_subset.__module__ = 'gnd.synth.mutate'
_equality_side_removal.__module__ = 'gnd.synth.mutate'
_applies_remove_equality_side.__module__ = 'gnd.synth.mutate'
_apply_remove_equality_side.__module__ = 'gnd.synth.mutate'
_applies_add_overlap.__module__ = 'gnd.synth.mutate'
_apply_add_overlap.__module__ = 'gnd.synth.mutate'

_xor_player_sets.__module__ = 'gnd.synth.mutate'
_applies_play_both.__module__ = 'gnd.synth.mutate'
_apply_play_both.__module__ = 'gnd.synth.mutate'
_pick_xor_removable.__module__ = 'gnd.synth.mutate'
_applies_play_neither.__module__ = 'gnd.synth.mutate'
_apply_play_neither.__module__ = 'gnd.synth.mutate'
_invertible_fact.__module__ = 'gnd.synth.mutate'
_applies_invert_vc.__module__ = 'gnd.synth.mutate'
_apply_invert_vc.__module__ = 'gnd.synth.mutate'
_applies_place_two_subtypes.__module__ = 'gnd.synth.mutate'
_apply_place_two_subtypes.__module__ = 'gnd.synth.mutate'
_subtype_assertions.__module__ = 'gnd.synth.mutate'
_applies_remove_all_subtypes.__module__ = 'gnd.synth.mutate'
_apply_remove_all_subtypes.__module__ = 'gnd.synth.mutate'
_coverage_target_ft.__module__ = 'gnd.synth.mutate'
_applies_drop_covers.__module__ = 'gnd.synth.mutate'
_apply_drop_covers.__module__ = 'gnd.synth.mutate'
first_implemented_inline_ref.__module__ = 'gnd.synth.mutate'
_applies_empty_ft.__module__ = 'gnd.synth.mutate'
_apply_empty_ft.__module__ = 'gnd.synth.mutate'
_exists_atom_safe_for_removal.__module__ = 'gnd.synth.mutate'
_applies_remove_exists_witness.__module__ = 'gnd.synth.mutate'
_apply_remove_exists_witness.__module__ = 'gnd.synth.mutate'
_templates_for.__module__ = 'gnd.synth.mutate'
operators_for.__module__ = 'gnd.synth.mutate'
enumerate_violating.__module__ = 'gnd.synth.mutate'
family_coverage.__module__ = 'gnd.synth.mutate'
compare_observed.__module__ = 'gnd.synth.mutate'
PredictionMismatch.__module__ = 'gnd.synth.mutate'
ViolatingCase.__module__ = 'gnd.synth.mutate'
emit_violating.__module__ = 'gnd.synth.mutate'


# Public dependency and compatibility spellings; same predecessor objects.
Template = _Template
XOR_MULTIROLE_MECHANISM = _XOR_MULTIROLE_MECHANISM
compat_all = __all__
applies_add_missing_subset = _applies_add_missing_subset
applies_add_out_of_range_new_entity = _applies_add_out_of_range_new_entity
applies_add_overlap = _applies_add_overlap
applies_add_past_ceiling = _applies_add_past_ceiling
applies_add_self_loop = _applies_add_self_loop
applies_close_2_cycle = _applies_close_2_cycle
applies_close_3_cycle = _applies_close_3_cycle
applies_drop_covers = _applies_drop_covers
applies_drop_from_group = _applies_drop_from_group
applies_drop_joined_below_min = _applies_drop_joined_below_min
applies_duplicate_covered = _applies_duplicate_covered
applies_duplicate_joined = _applies_duplicate_joined
applies_edit_out_of_range = _applies_edit_out_of_range
applies_empty_ft = _applies_empty_ft
applies_exact_duplicate = _applies_exact_duplicate
applies_introduce_distinct = _applies_introduce_distinct
applies_invert_vc = _applies_invert_vc
applies_new_entity_plays = _applies_new_entity_plays
applies_place_two_subtypes = _applies_place_two_subtypes
applies_play_both = _applies_play_both
applies_play_neither = _applies_play_neither
applies_remove_all_subtypes = _applies_remove_all_subtypes
applies_remove_disjunctive = _applies_remove_disjunctive
applies_remove_equality_side = _applies_remove_equality_side
applies_remove_exists_witness = _applies_remove_exists_witness
applies_roster_add = _applies_roster_add
apply_add_missing_subset = _apply_add_missing_subset
apply_add_out_of_range_new_entity = _apply_add_out_of_range_new_entity
apply_add_overlap = _apply_add_overlap
apply_add_past_ceiling = _apply_add_past_ceiling
apply_add_self_loop = _apply_add_self_loop
apply_close_2_cycle = _apply_close_2_cycle
apply_close_3_cycle = _apply_close_3_cycle
apply_drop_covers = _apply_drop_covers
apply_drop_from_group = _apply_drop_from_group
apply_drop_joined_below_min = _apply_drop_joined_below_min
apply_duplicate_covered = _apply_duplicate_covered
apply_duplicate_joined = _apply_duplicate_joined
apply_edit_out_of_range = _apply_edit_out_of_range
apply_empty_ft = _apply_empty_ft
apply_exact_duplicate = _apply_exact_duplicate
apply_introduce_distinct = _apply_introduce_distinct
apply_invert_vc = _apply_invert_vc
apply_new_entity_plays = _apply_new_entity_plays
apply_place_two_subtypes = _apply_place_two_subtypes
apply_play_both = _apply_play_both
apply_play_neither = _apply_play_neither
apply_remove_all_subtypes = _apply_remove_all_subtypes
apply_remove_disjunctive = _apply_remove_disjunctive
apply_remove_equality_side = _apply_remove_equality_side
apply_remove_exists_witness = _apply_remove_exists_witness
apply_remove_last_covering = _apply_remove_last_covering
apply_roster_add = _apply_roster_add
coverage_target_ft = _coverage_target_ft
equality_side_removal = _equality_side_removal
exists_atom_safe_for_removal = _exists_atom_safe_for_removal
frequency_min_gate = _frequency_min_gate
governed_ft_with_entity_role = _governed_ft_with_entity_role
internal_frequency_groups = _internal_frequency_groups
invertible_fact = _invertible_fact
mandatory_role_type = _mandatory_role_type
other_ft_with_role = _other_ft_with_role
pick_disjunctive_member = _pick_disjunctive_member
pick_xor_removable = _pick_xor_removable
remove_one_from_min_group = _remove_one_from_min_group
ring_components_of = _ring_components_of
ring_edges = _ring_edges
ring_gate = _ring_gate
subset_candidate = _subset_candidate
subtype_assertions = _subtype_assertions
templates_for = _templates_for
uniqueness_conflict = _uniqueness_conflict
value_occurrence = _value_occurrence
xor_player_sets = _xor_player_sets
xor_single_role = _xor_single_role

RING_COMPONENTS = _RING_COMPONENTS

RING_VARIANTS = _RING_VARIANTS

compare_scalar = _compare_scalar

constraint_iter_with_ref = _constraint_iter_with_ref

key = _key

role_object = _role_object

seq_tuples = _seq_tuples

normalize_comparison_operands = _normalize_comparison_operands

guarded_antecedent_bindings = _guarded_antecedent_bindings

guarded_exists_witness = _guarded_exists_witness

has_private_exists_sources = _has_private_exists_sources

guarded_modular_repair_plan = _guarded_modular_repair_plan
