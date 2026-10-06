"""Independent expected-state and prediction algorithms."""
from __future__ import annotations

from collections.abc import Mapping
from random import Random
from typing import Any

from gnd import popvalidate
from gnd.checker import (
    IMPLEMENTED_FAMILIES,
)
from gnd.model import Model, structured_derivation_ids
from gnd.synth.comparison import _UNTYPEABLE
from gnd.synth.comparison import normalize_operands as _normalize_comparison_operands
from gnd.synth.comparison import role_literal_operands as _role_literal_operands
from gnd.synth.guarded import (
    antecedent_bindings as _guarded_antecedent_bindings,
)
from gnd.synth.guarded import (
    exists_witness as _guarded_exists_witness,
)
from gnd.synth.guarded import (
    exists_witness_shape_supported as _guarded_exists_shape_supported,
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
    direct_subtypes as _direct_subtypes,
)
from gnd.synth.oracle.constructive import (
    key as _key,
)
from gnd.synth.oracle.constructive import (
    seq_tuples as _seq_tuples,
)
from gnd.synth.oracle.constructive import (
    tuple_key as _tuple_key,
)
from gnd.synth.oracle.constructive import (
    universe as _universe,
)
from gnd.synth.oracle.constructive import (
    witness as _witness,
)
from gnd.synth.provenance import ExpectedState
from gnd.synth.value_domain import (
    EmptyValueDomain,
    constraint_accepts,
    draw_value_for_constraints,
    governing_value_constraints,
)
from gnd.synth.values import make_value

_AMPLIFICATION_CEILING = 32


_OBJECT_SCOPED = {"value": "object_type", "cardinality": "object_type", "subtype-partition": "supertype"}


_MANDATORY_RELEVANT = {"mandatory", "mandatory-disjunctive"}


_SKIP = object()


def _resolve(model: Model, ref: str) -> tuple[dict[str, Any], dict[str, Any] | None]:
    for candidate_ref, constraint, ft in _constraint_iter_with_ref(model):
        if candidate_ref == ref:
            return constraint, ft
    raise GeneratorError(f"unknown constraint ref {ref!r} for this model")


def _ft_by_id(model: Model, ftid: str) -> dict[str, Any] | None:
    for ft in model.fact_types or []:
        if str(ft.get("id")) == str(ftid):
            return ft
    return None


def _facts_of(doc: dict[str, Any], ftid: str) -> list[dict[str, Any]]:
    return doc.setdefault("facts", {}).setdefault(str(ftid), [])


def _is_entity(model: Model, oid: str) -> bool:
    for ot in model.object_types or []:
        if str(ot.get("id")) == str(oid):
            return ot.get("kind") == "entity"
    return False


def _existing_members(doc: dict[str, Any], model: Model, oid: str) -> list[Any]:
    """Distinct closed-world members of ``oid``, deterministic order."""
    children = _direct_subtypes(model)
    seen: set[Any] = set()
    out: list[Any] = []
    for value in _universe(doc, model, str(oid), children):
        key = _key(value)
        if key not in seen:
            seen.add(key)
            out.append(value)
    return sorted(out, key=repr)


def _fresh_identifier(doc: dict[str, Any], model: Model, oid: str, rng: Random) -> Any:
    """A NEW identifier for ``oid`` that no closed-world walk already contains.

    Typed by the reference-scheme primitive where one resolves (an int for an
    Integer-referenced entity), and by the shape of the existing values where it
    does not (external / unit-based reference modes carry opaque scalars).
    """
    existing = _existing_members(doc, model, oid)
    keys = {_key(v) for v in existing}
    primitive = popvalidate.resolve_primitive(str(oid), model)
    ints = [v for v in existing if isinstance(v, int) and not isinstance(v, bool)]
    if primitive == "Integer" or (existing and len(ints) == len(existing)):
        candidate = (max(ints) + 1) if ints else 900001
        while _key(candidate) in keys:
            candidate += 1
        return candidate
    if primitive == "String" or (existing and all(isinstance(v, str) for v in existing)):
        index = 1
        candidate = f"znew-{oid}-{index}"
        while _key(candidate) in keys:
            index += 1
            candidate = f"znew-{oid}-{index}"
        return candidate
    if primitive is not None:
        for _ in range(100):
            candidate = make_value(str(primitive), rng)
            if _key(candidate) not in keys:
                return candidate
    raise GeneratorError(
        f"no fresh identifier derivable for object type {oid!r} "
        f"(primitive={primitive!r}, {len(existing)} existing values)"
    )


def _value_spec_for(
    model: Model, ftid: str, role_name: str, oid: str
) -> list[dict[str, Any]]:
    """Every object- and role-scoped value constraint governing this role."""
    return governing_value_constraints(
        model, oid, ftid=ftid, role_name=role_name
    )


def _valid_value(
    model: Model,
    ftid: str,
    role_name: str,
    oid: str,
    rng: Random,
    avoid: tuple[Any, ...] = (),
) -> Any:
    """An in-spec value for a value-typed role (honours enum / range specs)."""
    constraints = _value_spec_for(model, ftid, role_name, oid)
    avoid_keys = {_key(a) for a in avoid}
    primitive = popvalidate.resolve_primitive(str(oid), model)
    if primitive is None:
        raise GeneratorError(f"no primitive resolvable for value type {oid!r}")
    try:
        for _ in range(50):
            candidate = draw_value_for_constraints(
                str(primitive), rng, constraints
            )
            if _key(candidate) not in avoid_keys:
                return candidate
    except EmptyValueDomain as error:
        raise GeneratorError(
            f"value constraints for {ftid}.{role_name} have an empty intersection: {error}"
        ) from error
    return candidate


def _out_of_spec_value(constraint: dict[str, Any]) -> Any | None:
    """A value OUTSIDE the constraint's enum / range, or ``None`` (not derivable)."""
    allowed = constraint.get("allowed")
    if allowed is not None:
        if all(isinstance(a, str) for a in allowed):
            candidate = "znot-allowed"
            while candidate in allowed:
                candidate += "-x"
            return candidate
        numbers = [a for a in allowed if isinstance(a, (int, float)) and not isinstance(a, bool)]
        if len(numbers) == len(allowed) and numbers:
            return max(numbers) + 1
        return None
    ranges = constraint.get("ranges")
    if ranges is None and constraint.get("range") is not None:
        ranges = [constraint["range"]]
    for bounds in ranges or []:
        for edge, delta in (("max", 1), ("min", -1)):
            value = bounds.get(edge)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                candidate = value + delta
                if not constraint_accepts(candidate, constraint):
                    return candidate
    return None


def _enforce_value_comparisons(model: Model, ft: dict[str, Any], row: dict[str, Any]) -> None:
    """Order intra-fact value-comparison operands in a freshly built row so a
    mutation targeting constraint X does not smuggle in an accidental
    value-comparison violation (the assembler's coordination, mirrored)."""
    for constraint in ft.get("constraints") or []:
        if constraint.get("type") != "value-comparison":
            continue
        literal_pair = _role_literal_operands(model, constraint, ft)
        if literal_pair is not None:
            role_operand, literal_operand, op = literal_pair
            role = role_operand.role
            assert role is not None
            if role not in row or _compare_scalar(row[role], op, literal_operand.value):
                continue
            literal = literal_operand.value
            step = 1 if isinstance(literal, int) and not isinstance(literal, bool) else None
            if op in ("<=", ">=", "="):
                row[role] = literal
            elif op == "<" and step is not None:
                row[role] = literal - step
            elif op == ">" and step is not None:
                row[role] = literal + step
            continue
        operand_a, operand_b = _normalize_comparison_operands(model, constraint, ft)
        if operand_a.kind != "role" or operand_b.kind != "role":
            continue
        role_a, role_b = operand_a.role, operand_b.role
        assert role_a is not None and role_b is not None
        if role_a not in row or role_b not in row:
            continue
        op = str(constraint.get("operator"))
        a, b = row[role_a], row[role_b]
        if _compare_scalar(a, op, b):
            continue
        try:
            lo, hi = (a, b) if a <= b else (b, a)
        except TypeError:
            continue
        if op in ("<=", "<"):
            row[role_a], row[role_b] = lo, hi
        elif op in (">=", ">"):
            row[role_a], row[role_b] = hi, lo
        elif op == "=":
            row[role_b] = row[role_a]


def _complete_row(
    doc: dict[str, Any],
    model: Model,
    ft: dict[str, Any],
    fixed: dict[str, Any],
    rng: Random,
    *,
    fresh_entities: bool = False,
) -> dict[str, Any]:
    """A full fact row for ``ft``: ``fixed`` roles kept, entity roles drawn from
    the existing universe (or minted fresh), value roles drawn in-spec."""
    ftid = str(ft.get("id"))
    row = dict(fixed)
    for role in ft.get("roles") or []:
        rn = str(role.get("role_name"))
        if rn in row:
            continue
        oid = str(role.get("object_type"))
        if _is_entity(model, oid):
            if fresh_entities:
                row[rn] = _fresh_identifier(doc, model, oid, rng)
            else:
                members = _existing_members(doc, model, oid)
                row[rn] = members[0] if members else _fresh_identifier(doc, model, oid, rng)
        else:
            row[rn] = _valid_value(model, ftid, rn, oid, rng)
    _enforce_value_comparisons(model, ft, row)
    return row


def _scope_fts(
    constraint: dict[str, Any], ctype: str, model: Model, ft: dict[str, Any] | None
) -> list[str]:
    """Independent mirror of the normative scope rule (which fact types a
    constraint ranges over, for vacuity)."""
    if ft is not None:
        return [str(ft.get("id"))]
    if ctype == "guarded":
        antecedent = constraint.get("antecedent")
        if not isinstance(antecedent, list):
            return []
        return list(
            dict.fromkeys(
                str(atom.get("fact_type"))
                for atom in antecedent
                if isinstance(atom, dict) and atom.get("fact_type") is not None
            )
        )
    referenced: list[str] = []
    for fld in ("role_refs", "subset_role_seq", "superset_role_seq", "role_seq_a", "role_seq_b"):
        for ref in constraint.get(fld) or []:
            if isinstance(ref, dict):
                referenced.append(str(ref.get("fact_type")))
    for seq in constraint.get("role_seqs") or []:
        for ref in seq or []:
            if isinstance(ref, dict):
                referenced.append(str(ref.get("fact_type")))
    for fld in ("role_ref", "role_a", "role_b"):
        ref = constraint.get(fld)
        if isinstance(ref, dict):
            referenced.append(str(ref.get("fact_type")))
    if referenced:
        return list(dict.fromkeys(referenced))
    if ctype in ("value", "cardinality"):
        target = constraint.get("object_type")
        return [
            str(f.get("id"))
            for f in model.fact_types or []
            if any(r.get("object_type") == target for r in f.get("roles") or [])
        ]
    if ctype == "subtype-partition":
        targets = {constraint.get("supertype"), *(constraint.get("subtypes") or [])}
        return [
            str(f.get("id"))
            for f in model.fact_types or []
            if any(r.get("object_type") in targets for r in f.get("roles") or [])
        ]
    return []


_JOIN_QUANTIFIER = {
    "uniqueness": "any",
    "frequency": "any",
    "value-comparison": "any",
    "equality": "all",
    "exclusion": "all",
}


def _subject_sequences(constraint: dict[str, Any], ctype: str) -> list[list[dict[str, Any]]]:
    if ctype in ("uniqueness", "frequency"):
        refs = [r for r in constraint.get("role_refs") or [] if isinstance(r, dict)]
        return [refs] if refs else []
    if ctype == "value-comparison":
        refs = [
            r for r in (constraint.get("role_a"), constraint.get("role_b")) if isinstance(r, dict)
        ]
        return [refs] if refs else []
    if ctype in ("equality", "exclusion"):
        out = []
        for fld in ("role_seq_a", "role_seq_b"):
            seq = [r for r in constraint.get(fld) or [] if isinstance(r, dict)]
            if seq:
                out.append(seq)
        return out
    return []


def _join_vacuous(constraint: dict[str, Any], ctype: str, doc: dict[str, Any], model: Model) -> bool:
    quantifier = _JOIN_QUANTIFIER.get(ctype)
    if quantifier is None:
        return False
    sequences = _subject_sequences(constraint, ctype)
    spans = [len({str(r.get("fact_type")) for r in seq}) > 1 for seq in sequences]
    if not any(spans):
        return False
    empties = [not _seq_tuples(doc, model, seq) for seq in sequences]
    return any(empties) if quantifier == "any" else all(empties)


def _subtype_partition_witness(
    constraint: dict[str, Any], doc: dict[str, Any], model: Model, children: dict[str, set[str]]
) -> bool | None:
    """Independent subtype-partition predicate. ``None`` = membership exists
    only via an opaque derivation rule (expected ``unchecked``)."""
    supertype = str(constraint.get("supertype"))
    subtypes = [str(s) for s in constraint.get("subtypes") or []]
    exclusive = bool(constraint.get("exclusive"))
    exhaustive = bool(constraint.get("exhaustive"))
    if not exclusive and not exhaustive:
        return None
    declarations = {str(ot.get("id")): ot for ot in model.object_types or []}
    member_sets: dict[str, set[Any]] = {}
    for subtype in subtypes:
        members = {_key(v) for v in _universe(doc, model, subtype, children)}
        if not members and (declarations.get(subtype) or {}).get("derivation") == "derived":
            return None
        member_sets[subtype] = members
    universe = {_key(v) for v in _universe(doc, model, supertype, children)}
    for members in member_sets.values():
        universe |= members
    union: set[Any] = set().union(*member_sets.values()) if member_sets else set()
    both = exclusive and any(
        sum(v in s for s in member_sets.values()) > 1 for v in union
    )
    neither = exhaustive and bool(universe - union)
    return not (both or neither)


def _witness_ext(
    constraint: dict[str, Any],
    ft: dict[str, Any] | None,
    doc: dict[str, Any],
    model: Model,
    children: dict[str, set[str]],
) -> bool | None:
    if str(constraint.get("type")) == "subtype-partition":
        return _subtype_partition_witness(constraint, doc, model, children)
    return _witness(constraint, ft, doc, model, children)


def _guarded_atoms_have_derived_source(atoms: object, model: Model) -> bool:
    """Whether raw population rows omit a relation the oracle cannot derive."""
    if not isinstance(atoms, list) or not atoms:
        return False
    fact_types = {
        str(row.get("id")): row
        for row in model.fact_types or []
        if isinstance(row, Mapping) and row.get("id") is not None
    }
    for atom in atoms:
        fact_type = atom.get("fact_type") if isinstance(atom, Mapping) else None
        declaration = fact_types.get(str(fact_type)) if isinstance(fact_type, str) else None
        if declaration is None or declaration.get("derivation") in {
            "derived",
            "semiderived",
        } or declaration.get("derivation_rule") is not None:
            return True
    return False


def _guarded_exists_has_derived_source(
    constraint: dict[str, Any], model: Model
) -> bool:
    consequent = constraint.get("consequent")
    exists = consequent.get("exists") if isinstance(consequent, Mapping) else None
    atoms = exists.get("atoms") if isinstance(exists, Mapping) else None
    return _guarded_atoms_have_derived_source(atoms, model)


def expected_state(
    constraint: dict[str, Any],
    ft: dict[str, Any] | None,
    doc: dict[str, Any],
    model: Model,
    children: dict[str, set[str]],
) -> ExpectedStateData | None:
    """The independent (ground_truth, expected_verdict, reason) for one
    constraint over one document — or ``None`` when no independent oracle
    exists for the family/shape (the engine then makes NO claim, and an
    operator that changes such a constraint's verdict is a loud mismatch).

    Ordering mirrors the NORMATIVE verdict-resolution rules (D-12 clauses,
    the F-02 object-universe rule, the F-05 zero-row-join rule) — semantics
    shared with the checker, code independent of it (C1). The one deliberate
    divergence from a naive read: a family-emptied ``mandatory`` whose
    instances stay observable is ``{violated, vacuous}`` — the witness proves
    the violation, the correct checker still answers ``vacuous``, and plan 04
    scores the pair ``masked_by_vacuity`` instead of ``correct``.
    """
    ctype = str(constraint.get("type"))
    modality = str(constraint.get("modality", ""))
    violation = "fail" if modality == "alethic" else "warning"

    if ctype == "guarded":
        consequent = constraint.get("consequent")
        exists = consequent.get("exists") if isinstance(consequent, Mapping) else None
        if isinstance(exists, Mapping) and _guarded_atoms_have_derived_source(
            constraint.get("antecedent"), model
        ):
            return None

    if ctype == "textual":
        return ExpectedStateData("satisfied", "unchecked", "textual-not-mechanical")
    if ctype not in IMPLEMENTED_FAMILIES:
        return ExpectedStateData("satisfied", "unchecked", "family-unimplemented")
    if ctype == "value-comparison":
        operands = _normalize_comparison_operands(model, constraint, ft)
        if any(operand.kind == "clock" for operand in operands):
            return ExpectedStateData("satisfied", "unchecked", "no-reference-clock")
        if any(
            operand.kind == "literal" and operand.value is _UNTYPEABLE
            for operand in operands
        ):
            return ExpectedStateData("satisfied", "unchecked", "literal-type-ambiguous")
        if all(operand.kind in ("role", "cross-role") for operand in operands):
            primitive_a, primitive_b = (operand.primitive for operand in operands)
            numeric = {"Integer", "Float", "Number"}
            compatible = primitive_a == primitive_b or {primitive_a, primitive_b} <= numeric
            if constraint.get("operator") not in ("=", "!=") and not compatible:
                return ExpectedStateData("satisfied", "unchecked", "values-not-comparable")

    scope = _scope_fts(constraint, ctype, model, ft)
    subject_field = _OBJECT_SCOPED.get(ctype)
    object_scoped = (
        subject_field is not None
        and constraint.get(subject_field) is not None
        and not (ctype == "value" and isinstance(constraint.get("role_ref"), dict))
    )
    covers = list((doc.get("population") or {}).get("covers") or [])

    if not object_scoped and scope:
        if ctype in _MANDATORY_RELEVANT and any(s not in covers for s in scope):
            return ExpectedStateData("no-subjects", "vacuous", "coverage-omission")
        empty = [not (doc.get("facts") or {}).get(s) for s in scope]
        if (ctype == "guarded" and any(empty)) or all(empty):
            witness = _witness_ext(constraint, ft, doc, model, children)
            if witness is False:
                # The masked cell: ground truth VIOLATED, expected verdict
                # vacuous (D-12 clause 1 fires before evaluation).
                return ExpectedStateData("violated", "vacuous", "masked-by-fact-type-vacuity")
            return ExpectedStateData("no-subjects", "vacuous", "fact-types-empty")

    if ctype == "exclusive-or" and _xor_single_role(constraint) is None:
        # MULTI-ROLE exclusive-or. The disjunctive half has no tuple universe at
        # arity > 1 (constraint-reference.md:319-331), but the EXCLUSION half is
        # decidable over tuples, and a tuple found in two sequences PROVES the
        # constraint broken however the undecidable half would have gone
        # (violation outranks indeterminacy, D-08 precedence 1 > 4). Without this
        # branch the engine made NO claim, so the family's boundary cases carried
        # no predicted verdict and could not be measurement inputs at all.
        tuple_sets = [
            {_tuple_key(t) for t in _seq_tuples(doc, model, list(seq or []))}
            for seq in constraint.get("role_seqs") or []
        ]
        union = set().union(*tuple_sets) if tuple_sets else set()
        if any(sum(t in s for s in tuple_sets) > 1 for t in union):
            return ExpectedStateData("violated", violation, None)
        return ExpectedStateData("satisfied", "unchecked", "xor-disjunctive-undefined")

    if ctype == "guarded":
        consequent = constraint.get("consequent")
        exists = consequent.get("exists") if isinstance(consequent, dict) else None
        if isinstance(exists, dict):
            if not _guarded_exists_shape_supported(constraint):
                return None
            facts = doc.get("facts") or {}
            bindings = _guarded_antecedent_bindings(constraint, facts)
            if bindings is None:
                return None
            if not bindings:
                return ExpectedStateData("satisfied", "pass", None)
            # The standalone oracle sees only the document's asserted rows; it
            # does not materialize derived relations or prove their availability.
            if _guarded_exists_has_derived_source(constraint, model):
                return None
            witness = _guarded_exists_witness(
                constraint,
                facts,
                covered_fact_types=covers,
            )
            if witness is None:
                return None
            if witness is False:
                return ExpectedStateData("violated", violation, None)
            return ExpectedStateData("satisfied", "pass", None)

    if ctype == "subtype-partition":
        witness = _subtype_partition_witness(constraint, doc, model, children)
        if witness is None:
            return ExpectedStateData("satisfied", "unchecked", "subtype-derivation-only")
    else:
        witness = _witness_ext(constraint, ft, doc, model, children)
    if witness is None:
        return None
    if witness is False:
        return ExpectedStateData("violated", violation, None)

    if object_scoped:
        oid = str(constraint.get(subject_field))
        if not _universe(doc, model, oid, children):
            return ExpectedStateData("no-subjects", "vacuous", "no-observable-subjects")
    if _join_vacuous(constraint, ctype, doc, model):
        return ExpectedStateData("no-subjects", "vacuous", "zero-row-join")
    return ExpectedStateData("satisfied", "pass", None)


def predict_violations(
    model: Model, baseline_doc: dict[str, Any], mutated_doc: dict[str, Any]
) -> dict[str, ExpectedState]:
    """The typed verdict-delta prediction for one mutation (D-05', C3).

    For every constraint the model declares, the independent expected-state
    engine is evaluated over the baseline and the mutated document; every
    constraint whose expected state CHANGES enters the map with its mutated
    :class:`ExpectedState`. Computed per (model, constraint, operator) triple —
    the same operator predicts different sets on different models, which is the
    measured D-05' finding this function exists to honour.

    The ring implication lattice is not a constant: each co-declared ring
    constraint (every ``variant`` in the checker's ``_RING_VARIANTS``
    vocabulary, combined variants expanded through ``_RING_COMPONENTS``) is
    evaluated over the mutated pairs by its own witness, so a self-loop predicts
    ``irreflexive`` ∧ ``acyclic`` ∧ ``asymmetric`` exactly where those variants
    are co-declared and nothing where they are not.

    NOTE the signature deviates from the plan's ``predict(model, population,
    constraint_ref)``: a delta ("which refs CHANGE state") is a function of two
    documents, and a single-population signature cannot express it.
    """
    # v5.0 Phase 3 (T3.4, D-P3.6): mutating an asserted fact of a structured
    # model can flip a DERIVATION verdict this engine has no oracle for, and a
    # silently incomplete prediction is exactly the mislabelled-case leak the
    # sidecar contract forbids. `gnd synth` already refuses such models at the
    # generator band; this guard is the direct-API twin — a named stand-down
    # on the guarded-family pattern, never a silent no-claim.
    structured = structured_derivation_ids(model)
    if structured:
        raise GeneratorError(
            "the expectation engine makes no claim over a structured "
            f"derivation model ({', '.join(structured)}): a mutation can flip "
            "a derivation verdict no independent oracle here predicts, and "
            "synth refuses these models upstream at the generator band"
        )
    children = _direct_subtypes(model)
    predicted: dict[str, ExpectedState] = {}
    for ref, constraint, ft in _constraint_iter_with_ref(model):
        before = expected_state(constraint, ft, baseline_doc, model, children)
        after = expected_state(constraint, ft, mutated_doc, model, children)
        if after is None or before is None or before == after:
            continue
        predicted[ref] = ExpectedState(
            ground_truth=after.ground_truth,  # type: ignore[arg-type]
            expected_verdict=after.expected_verdict,  # type: ignore[arg-type]
            reason=after.reason,
        )
    return predicted



# Historical qualifications are serialized by existing callers.
_resolve.__module__ = 'gnd.synth.mutate'
_ft_by_id.__module__ = 'gnd.synth.mutate'
_facts_of.__module__ = 'gnd.synth.mutate'
_is_entity.__module__ = 'gnd.synth.mutate'
_existing_members.__module__ = 'gnd.synth.mutate'
_fresh_identifier.__module__ = 'gnd.synth.mutate'
_value_spec_for.__module__ = 'gnd.synth.mutate'
_valid_value.__module__ = 'gnd.synth.mutate'
_out_of_spec_value.__module__ = 'gnd.synth.mutate'
_enforce_value_comparisons.__module__ = 'gnd.synth.mutate'
_complete_row.__module__ = 'gnd.synth.mutate'
_scope_fts.__module__ = 'gnd.synth.mutate'
_subject_sequences.__module__ = 'gnd.synth.mutate'
_join_vacuous.__module__ = 'gnd.synth.mutate'
_subtype_partition_witness.__module__ = 'gnd.synth.mutate'
_witness_ext.__module__ = 'gnd.synth.mutate'
_guarded_atoms_have_derived_source.__module__ = 'gnd.synth.mutate'
_guarded_exists_has_derived_source.__module__ = 'gnd.synth.mutate'
expected_state.__module__ = 'gnd.synth.mutate'
predict_violations.__module__ = 'gnd.synth.mutate'

def _xor_single_role(constraint) -> list[dict[str, Any]] | None:
    seqs = [list(s or []) for s in constraint.get("role_seqs") or []]
    if not seqs or not all(len(s) == 1 and isinstance(s[0], dict) for s in seqs):
        return None
    return [s[0] for s in seqs]

_xor_single_role.__module__ = 'gnd.synth.mutate'

# Public dependency and compatibility spellings; same predecessor objects.
AMPLIFICATION_CEILING = _AMPLIFICATION_CEILING
JOIN_QUANTIFIER = _JOIN_QUANTIFIER
MANDATORY_RELEVANT = _MANDATORY_RELEVANT
OBJECT_SCOPED = _OBJECT_SCOPED
SKIP = _SKIP
complete_row = _complete_row
enforce_value_comparisons = _enforce_value_comparisons
existing_members = _existing_members
facts_of = _facts_of
fresh_identifier = _fresh_identifier
ft_by_id = _ft_by_id
guarded_atoms_have_derived_source = _guarded_atoms_have_derived_source
guarded_exists_has_derived_source = _guarded_exists_has_derived_source
is_entity = _is_entity
join_vacuous = _join_vacuous
out_of_spec_value = _out_of_spec_value
resolve = _resolve
scope_fts = _scope_fts
subject_sequences = _subject_sequences
subtype_partition_witness = _subtype_partition_witness
valid_value = _valid_value
value_spec_for = _value_spec_for
witness_ext = _witness_ext
xor_single_role = _xor_single_role

direct_subtypes = _direct_subtypes

tuple_key = _tuple_key

universe = _universe

witness = _witness

UNTYPEABLE = _UNTYPEABLE

role_literal_operands = _role_literal_operands

guarded_exists_shape_supported = _guarded_exists_shape_supported
