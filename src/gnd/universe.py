"""RF3 shared dependency home; algorithms retain predecessor semantics."""
from __future__ import annotations

from collections.abc import Mapping
from contextvars import ContextVar
from typing import Any, Literal

from gnd.atoms import atom_has_bind


def _fact_type_roles(doc: dict[str, Any]) -> dict[str, set[str]]:
    """fact_type id -> set of role_names."""
    return {
        str(ft.get("id")): {
            str(role.get("role_name"))
            for role in ft.get("roles") or []
            if isinstance(role, dict) and role.get("role_name")
        }
        for ft in doc.get("fact_types") or []
        if isinstance(ft, dict) and ft.get("id") is not None
    }


def _resolved_primitive(
    object_type_id: str,
    object_types: dict[str, dict[str, Any]],
    seen: set[str] | None = None,
) -> str | None:
    """Resolve a primitive without importing popvalidate (which imports Model)."""
    seen = set(seen or ())
    if object_type_id in seen:
        return None
    seen.add(object_type_id)
    object_type = object_types.get(object_type_id)
    if object_type is None:
        return None
    if object_type.get("kind") == "value":
        primitive = object_type.get("primitive")
        return str(primitive) if primitive is not None else None
    reference = object_type.get("reference") or {}
    if reference.get("mode") in ("popular", "general") and reference.get("value_type"):
        return _resolved_primitive(str(reference["value_type"]), object_types, seen)
    if object_type.get("inherits_reference"):
        inherited = {
            primitive
            for parent in object_type.get("subtype_of") or []
            if (primitive := _resolved_primitive(str(parent), object_types, seen)) is not None
        }
        if len(inherited) == 1:
            return inherited.pop()
    return None


def _supertype_parents(doc: dict[str, Any]) -> dict[str, list[str]]:
    """object-type id -> declared direct supertypes (``subtype_of``)."""
    return {
        str(ot.get("id")): [str(s) for s in ot.get("subtype_of") or []]
        for ot in doc.get("object_types") or []
        # `isinstance` BEFORE `.get`: a non-mapping entry is layer 1's finding,
        # and this helper raising would deny every layer-2 rule the chance to
        # report its own. Surfaced by v5.0 Phase 1's hostile-shape sweep.
        if isinstance(ot, dict) and ot.get("id") is not None
    }


_DERIVATION_TERM_CACHE: ContextVar[dict | None] = ContextVar("gnd_intake_term_issues", default=None)


DERIVATION_TERM_CACHE = _DERIVATION_TERM_CACHE
fact_type_roles = _fact_type_roles
def resolved_primitive(
    object_type_id: str,
    object_types: dict[str, dict[str, Any]],
    seen: set[str] | None = None,
) -> str | None:
    """Historical model-intake signature, explicitly choosing truthy resolution."""
    return primitive_for(object_type_id, object_types, variant="truthy", seen=seen)


resolved_primitive.__module__ = "gnd.model"
resolved_primitive.__name__ = "_resolved_primitive"
resolved_primitive.__qualname__ = "_resolved_primitive"
supertype_parents = _supertype_parents


from collections.abc import Callable


def _object_types_by_id(model: Model) -> dict[str, dict[str, Any]]:
    return {
        str(ot.get("id")): ot for ot in model.object_types or [] if ot.get("id") is not None
    }


def _identifying_primitive(_object_type_id: str, object_type: dict[str, Any]) -> str | None:
    """Extractor: the primitive an identifying value type carries."""
    # The meta-schema guarantees `primitive` is present when kind is value
    # (`$defs/object_type.allOf[1]`).
    primitive = object_type.get("primitive")
    return str(primitive) if primitive is not None else None


def _identifying_id(object_type_id: str, _object_type: dict[str, Any]) -> str | None:
    """Extractor: the id of the identifying value type itself."""
    return str(object_type_id)


def _resolve_reference(
    object_type_id: str,
    by_id: dict[str, dict[str, Any]],
    parents: dict[str, list[str]],
    seen: set[str],
    extract: Callable[[str, dict[str, Any]], str | None],
) -> str | None:
    """Walk an object type to the value type that IDENTIFIES its instances.

    One walk, two extractions (the ``_instance_values_of`` /``_instances_of``
    posture applied to reference resolution). ``extract`` is applied to the value
    type the walk lands on: :func:`_identifying_primitive` yields the primitive
    for layer-2 type checking, :func:`_identifying_id` yields the value type's own
    id for the checker's universe walk. Both answers therefore come from ONE
    notion of "which value type denotes this entity" — the F-01 fix would
    otherwise have been a second, drift-prone copy of this traversal.

    The disjunction at the ``inherits_reference`` branch is over the EXTRACTED
    value, not over the id, which is what preserves the pre-existing primitive
    semantics exactly: two supertypes identified by two distinct value types that
    share one primitive still resolve that primitive, while the id extraction
    correctly declines to pick one of the two.
    """
    if object_type_id in seen:
        # A subtype cycle is NOT rejected by model validation today — a model
        # with `a subtype_of [b]` and `b subtype_of [a]` validates at exit 0 —
        # so the walk cannot assume acyclicity (T-01.1-07).
        return None
    seen.add(object_type_id)

    object_type = by_id.get(object_type_id)
    if object_type is None:
        return None

    if object_type.get("kind") == "value":
        return extract(object_type_id, object_type)

    reference = object_type.get("reference") or {}
    value_type = reference.get("value_type")
    if reference.get("mode") in ("popular", "general") and value_type is not None:
        # `semantic:reference-value-type` (model.py) guarantees this names a
        # value-kind object type, which in turn carries a `primitive`.
        target = by_id.get(str(value_type))
        if target is None:
            return None
        return extract(str(value_type), target)

    if parents.get(object_type_id) and object_type.get("inherits_reference") is True:
        # Only when the subtype declares that it INHERITS its supertype's
        # identification scheme. `inherits_reference: false` with no reference of
        # its own is unresolvable, and reading through anyway would be a guess.
        resolved = {
            _resolve_reference(parent, by_id, parents, seen, extract)
            for parent in parents[object_type_id]
        }
        resolved.discard(None)
        return next(iter(resolved)) if len(resolved) == 1 else None

    return None


def resolve_reference_value_type(object_type_id: str, model: Model) -> str | None:
    """The id of the value type whose values DENOTE this object type's instances.

    A ``kind: value`` object type denotes itself. An entity type resolves through
    ``reference.value_type``; an entity subtype declaring
    ``inherits_reference: true`` walks its supertypes and yields an id only when
    every resolvable ancestor agrees on exactly one. ``None`` means not
    resolvable, on the same five routes :func:`resolve_primitive` documents.

    This is the *typing* inference of :func:`resolve_primitive` stopped one step
    earlier, and it is what lets the checker populate a value type's universe
    with the identifying values that appear in facts (F-01):
    ``population-format.md`` — *"Entity values in facts use the entity's
    reference-scheme value … ``movie: 1`` means the Movie whose MovieId is 1"*.
    Having asserted here that ``999999`` IS a MovieId in order to type-check it,
    the tool cannot coherently decline to range-check it as one.
    """
    return _resolve_reference(
        str(object_type_id),
        _object_types_by_id(model),
        _supertype_parents({"object_types": model.object_types}),
        set(),
        _identifying_id,
    )


def resolve_primitive(object_type_id: str, model: Model) -> str | None:
    """The primitive an object type's values carry, or ``None`` (D-05).

    A ``kind: value`` object type yields its ``primitive`` directly. An entity
    type resolves through ``reference.value_type``. An entity SUBTYPE that
    declares ``inherits_reference: true`` walks its supertypes and yields a
    primitive only when every resolvable ancestor agrees on exactly one.

    ``None`` means **not resolvable**, and every caller must then skip the type
    check *silently* — no issue, no warning. A skipped check is honest; an
    invented one is not. The five ways resolution legitimately fails are
    unit-based reference mode, external reference mode, an entity subtype with
    ``inherits_reference: false`` and no reference of its own, multiple
    inheritance resolving to two distinct primitives, and a subtype cycle.

    The upward walk carries a ``seen`` set because subtype cycles are not
    rejected by model validation today (T-01.1-07). It reuses
    :func:`gnd.model._supertype_parents` for the edge map rather than
    re-deriving one. It deliberately does NOT call
    :func:`gnd.model._ancestor_closure`: that closure walks ``subtype_of``
    unconditionally, while resolution must stop at any ancestor that does not
    declare ``inherits_reference: true`` — reading past one would be exactly the
    guess D-05 forbids.
    """
    return primitive_for(str(object_type_id), _object_types_by_id(model), variant="strict")


def primitive_for(
    object_type_id: str,
    object_types: dict[str, dict[str, Any]],
    *,
    variant: Literal["truthy", "strict"],
    seen: set[str] | None = None,
) -> str | None:
    """Resolve with an explicit predecessor policy; the two walks remain distinct."""
    if variant == "truthy":
        return _resolved_primitive(object_type_id, object_types, seen)
    if variant == "strict":
        return _resolve_reference(
            str(object_type_id), object_types,
            _supertype_parents({"object_types": list(object_types.values())}),
            set() if seen is None else seen, _identifying_primitive,
        )
    raise ValueError(f"unknown primitive resolver variant: {variant!r}")


identifying_id = _identifying_id
identifying_primitive = _identifying_primitive
object_types_by_id = _object_types_by_id
resolve_reference = _resolve_reference


from gnd.values import IdentitySet as _IdentitySet

IMPLEMENTED_FAMILIES = {
    "anchored",
    "uniqueness",
    "mandatory",
    "mandatory-disjunctive",
    "value",
    "frequency",
    "ring",
    "subset",
    "equality",
    "exclusion",
    "exclusive-or",
    "value-comparison",
    "cardinality",
    "subtype-partition",
    "guarded",
}


_RING_COMPONENTS = {
    "asymmetric-intransitive": ("asymmetric", "intransitive"),
    "acyclic-intransitive": ("acyclic", "intransitive"),
    "symmetric-irreflexive": ("symmetric", "irreflexive"),
    "symmetric-intransitive": ("symmetric", "intransitive"),
}

RING_COMPONENTS = _RING_COMPONENTS

_RING_VARIANTS = {
    "irreflexive",
    "asymmetric",
    "intransitive",
    "antisymmetric",
    "acyclic",
    "symmetric",
    "purely-reflexive",
    "reflexive",
    "transitive",
} | set(_RING_COMPONENTS)


def _is_implemented(constraint: dict[str, Any], fact_type: dict[str, Any] | None) -> bool:
    constraint_type = constraint.get("type")
    if constraint_type not in IMPLEMENTED_FAMILIES:
        return False
    if constraint_type == "anchored":
        return fact_type is not None
    if constraint_type == "uniqueness":
        if fact_type is not None:
            return isinstance(constraint.get("roles"), list)
        return constraint.get("scope") == "external" and bool(constraint.get("role_refs"))
    if constraint_type == "mandatory":
        return fact_type is not None and constraint.get("role") is not None
    if constraint_type == "value":
        forms = [key for key in ("allowed", "range", "ranges") if constraint.get(key) is not None]
        return constraint.get("object_type") is not None and len(forms) == 1
    if constraint_type == "mandatory-disjunctive":
        return bool(constraint.get("role_refs"))
    if constraint_type == "frequency":
        return bool(constraint.get("bound")) and (
            bool(constraint.get("roles")) or bool(constraint.get("role_refs"))
        )
    if constraint_type == "subset":
        return bool(constraint.get("subset_role_seq")) and bool(constraint.get("superset_role_seq"))
    if constraint_type in ("equality", "exclusion"):
        return bool(constraint.get("role_seq_a")) and bool(constraint.get("role_seq_b"))
    if constraint_type == "exclusive-or":
        return bool(constraint.get("role_seqs"))
    if constraint_type == "ring":
        return fact_type is not None and constraint.get("variant") in _RING_VARIANTS
    if constraint_type == "value-comparison":
        return (
            constraint.get("operator") is not None
            and constraint.get("role_a") is not None
            and constraint.get("role_b") is not None
        )
    if constraint_type == "guarded":
        antecedent = constraint.get("antecedent")
        consequent = constraint.get("consequent")
        exists = consequent.get("exists") if isinstance(consequent, Mapping) else None
        exists_atoms = exists.get("atoms") if isinstance(exists, Mapping) else None
        return (
            isinstance(antecedent, list)
            and bool(antecedent)
            and all(atom_has_bind(atom) for atom in antecedent)
            and isinstance(consequent, dict)
            and sum(key in consequent for key in ("comparison", "atom", "absence", "exists")) == 1
            and all(
                isinstance(consequent.get(key), dict)
                for key in ("comparison", "atom", "absence", "exists")
                if key in consequent
            )
            and (
                "exists" not in consequent
                or (
                    isinstance(exists_atoms, list)
                    and bool(exists_atoms)
                    and all(atom_has_bind(atom) for atom in exists_atoms)
                )
            )
        )
    if constraint_type == "subtype-partition":
        return constraint.get("supertype") is not None and bool(constraint.get("subtypes"))
    # cardinality
    if not constraint.get("bound"):
        return False
    if constraint.get("scope") == "object":
        return constraint.get("object_type") is not None and constraint.get("role_ref") is None
    if constraint.get("scope") == "role":
        return constraint.get("role_ref") is not None and constraint.get("object_type") is None
    return False


def _constraint_role_refs(constraint: dict[str, Any]):
    """Yield every ``{fact_type, role}`` reference a constraint carries."""
    for reference_field in (
        "role_refs",
        "subset_role_seq",
        "superset_role_seq",
        "role_seq_a",
        "role_seq_b",
    ):
        for ref in constraint.get(reference_field) or []:
            if isinstance(ref, dict):
                yield ref
    for sequence in constraint.get("role_seqs") or []:
        for ref in sequence or []:
            if isinstance(ref, dict):
                yield ref
    for reference_field in ("role_ref", "role_a", "role_b"):
        ref = constraint.get(reference_field)
        if isinstance(ref, dict):
            yield ref


def _scope_fact_types(
    constraint: dict[str, Any],
    constraint_type: str,
    model: Model,
    fact_type: dict[str, Any] | None,
) -> list[str]:
    """The fact types a constraint ranges over (for vacuity detection)."""
    if fact_type is not None:
        return [str(fact_type.get("id"))]
    if constraint_type == "guarded":
        antecedent = constraint.get("antecedent")
        if not isinstance(antecedent, list):
            return []
        referenced = [
            str(atom.get("fact_type"))
            for atom in antecedent
            if isinstance(atom, dict) and atom.get("fact_type") is not None
        ]
        return list(dict.fromkeys(referenced))
    referenced = [str(ref.get("fact_type")) for ref in _constraint_role_refs(constraint)]
    if referenced:
        return list(dict.fromkeys(referenced))
    if constraint_type in ("value", "cardinality"):
        target = constraint.get("object_type")
        return [
            str(ft.get("id"))
            for ft in model.fact_types
            if any(role.get("object_type") == target for role in ft.get("roles") or [])
        ]
    if constraint_type == "subtype-partition":
        targets = {constraint.get("supertype"), *(constraint.get("subtypes") or [])}
        return [
            str(ft.get("id"))
            for ft in model.fact_types
            if any(role.get("object_type") in targets for role in ft.get("roles") or [])
        ]
    return []


def _fact_type_by_id(model: Model, fact_type_id: str) -> dict[str, Any] | None:
    for fact_type in model.fact_types:
        if str(fact_type.get("id")) == fact_type_id:
            return fact_type
    return None


def _role_object_type(model: Model, fact_type_id: str, role_name: str) -> str | None:
    fact_type = _fact_type_by_id(model, fact_type_id)
    for role in (fact_type or {}).get("roles") or []:
        if role.get("role_name") == role_name:
            return str(role.get("object_type"))
    return None


def _descendant_closure(object_type_id: str, model: Model) -> set[str]:
    """``object_type_id`` plus every transitive SUBTYPE of it (cycle-safe).

    Direction is upward-propagating membership. In ORM 2 subtypehood IS
    population subsethood — ``pop(S) subset-of pop(A)`` whenever
    ``S subtype_of A`` — so a value playing an S-typed role is an instance of A,
    transitively. The reverse does NOT hold: a vehicle is not thereby a car,
    which is why this walk collects descendants and never ancestors.

    Multiple inheritance falls out of the fixpoint rather than needing a case:
    ``subtype_of`` is a list, so a type joins the closure as soon as ANY of its
    declared supertypes is already in it.

    Cycle safety is load-bearing here, not defensive. No ``semantic:`` rule
    forbids subtype cycles today (verified: ``a subtype_of [b]`` plus
    ``b subtype_of [a]`` validates at exit 0; the missing rule is recorded in
    the phase's ``deferred-items.md``). The fixpoint terminates because it only
    ever adds to a subset of a finite set of declared ids.

    Kept as its own helper rather than parameterising ``model._ancestor_closure``
    (the same shape walking the opposite edge direction): both directions are
    live in this phase, and one function taking a direction argument is one call
    site away from being handed the wrong one.
    """
    parents = {
        str(object_type.get("id")): [str(s) for s in object_type.get("subtype_of") or []]
        for object_type in model.object_types
        if object_type.get("id") is not None
    }
    members = {object_type_id}
    changed = True
    while changed:
        changed = False
        for declared_id, supertypes in parents.items():
            if declared_id not in members and members.intersection(supertypes):
                members.add(declared_id)
                changed = True
    return members


def _denoting_types(covered: set[str], model: Model) -> set[str]:
    """Object types whose instances are DENOTED by values of ``covered`` (F-01).

    An ORM reference scheme means an entity type's instances are denoted by
    values of its reference value type: ``population-format.md`` — *"Entity
    values in facts use the entity's reference-scheme value … ``movie: 1`` means
    the Movie whose MovieId is 1"*. So ``movie: 999999`` IS an occurrence of
    MovieId in the population, and the universe of MovieId must contain it.

    The loader already draws exactly this inference. ``popvalidate`` walks
    ``entity -> reference.value_type`` (following ``inherits_reference`` up
    ``subtype_of``) in order to TYPE-CHECK ``999999`` as a MovieId, and rejects
    the population at exit 3 when it is not one. Having asserted that the value
    IS a MovieId, declining to range-check the same value as a MovieId is
    incoherent — one value cannot be a MovieId for typing and not a MovieId for
    constraints. Before this closure, an alethic ``value``/``cardinality``
    constraint on a reference value type reported ``pass`` — *"— satisfied"* —
    at exit 0 over a population that visibly contained violating values, and the
    ``cardinality`` message stated its own blindness out loud (*"at most 2 —
    satisfied (0 observed)"* over four). That is the affirmative false
    certification this phase exists to eliminate, one relation over from the
    subtype direction CORE-06 named.

    The resolution walk is :func:`popvalidate.resolve_reference_value_type` —
    the loader's own traversal, not a second notion of it, because two
    inferences about "which value type denotes this entity" is how the typing
    answer and the constraint answer drift apart again.

    Types already in ``covered`` are excluded so a role can contribute at most
    once, which keeps ``offending`` one entry per OCCURRENCE rather than per
    occurrence per route.
    """
    return {
        str(object_type.get("id"))
        for object_type in model.object_types
        if object_type.get("id") is not None
        and str(object_type.get("id")) not in covered
        and resolve_reference_value_type(str(object_type.get("id")), model) in covered
    }


def _instance_values_of(object_type_id: str, model: Model, population: Population) -> list[Any]:
    """Closed-world instance values of an object type, DUPLICATES PRESERVED.

    The one closed-world walk (SKELETON.md semantics), extended by CORE-06 to
    every transitive subtype: the ``instances:`` roster of the type or any of
    its subtypes, plus every value playing a role typed to the type or any of
    its subtypes. Both routes are required because subtype membership is
    observable both ways (``population-format.md``: "via ``instances:`` rosters
    for the subtype or via subtype-typed roles played in facts").

    For a ``kind: value`` object type the walk additionally collects the values
    that DENOTE instances of every entity type whose reference scheme resolves
    to it (:func:`_denoting_types`, F-01) — by both routes again, since an
    entity's roster holds its identifying values just as its facts do. The
    widening is confined to value types: it says what an identifying value IS,
    and an entity type is never one.

    Returns a LIST because ``_check_value`` reports one offending entry per
    OCCURRENCE, while :func:`_instances_of` needs a set — one traversal, two
    shapes. The exact-match blind spot this closure fixes was previously written
    out twice, in two functions, which is precisely how two copies of one rule
    drift apart (RESEARCH Pitfall 8).

    The target type's own roster is emitted first and the others' in sorted id
    order, so the offending list is deterministic and unchanged for every object
    type that has neither subtypes nor entity types referencing it.
    """
    covered = _descendant_closure(object_type_id, model)
    if _kind_of(object_type_id, model) == "value":
        collected = covered | _denoting_types(covered, model)
    else:
        collected = covered
    values: list[Any] = []
    for collected_id in [object_type_id, *sorted(collected - {object_type_id})]:
        values.extend(population.instances.get(collected_id, []))
    for fact_type in model.fact_types:
        typed_roles = [
            role.get("role_name")
            for role in fact_type.get("roles") or []
            if str(role.get("object_type")) in collected
        ]
        if not typed_roles:
            continue
        for fact in population.facts.get(str(fact_type.get("id")), []):
            for role_name in typed_roles:
                if role_name in fact:
                    values.append(fact[role_name])
    return values


def _kind_of(object_type_id: str, model: Model) -> str | None:
    for object_type in model.object_types:
        if str(object_type.get("id")) == object_type_id:
            kind = object_type.get("kind")
            return str(kind) if kind is not None else None
    return None


def _instances_of(object_type_id: str, model: Model, population: Population) -> _IdentitySet:
    """Closed-world instance SET of an object type (SKELETON.md semantics),
    including every instance of its transitive subtypes (CORE-06).

    Before the closure, a car with no plate satisfied ``mandatory(vehicle)`` —
    affirmatively, with a "satisfied" message — because the universe was derived
    by matching ``role.object_type`` exactly (CONTEXT.md probe #5).
    """
    return _IdentitySet(_instance_values_of(object_type_id, model, population))


RING_VARIANTS = _RING_VARIANTS
constraint_role_refs = _constraint_role_refs
denoting_types = _denoting_types
descendant_closure = _descendant_closure
fact_type_by_id = _fact_type_by_id
instance_values_of = _instance_values_of
instances_of = _instances_of
is_implemented = _is_implemented
kind_of = _kind_of
role_object_type = _role_object_type
scope_fact_types = _scope_fact_types

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gnd.documents import Model
    from gnd.population import Population

_fact_type_roles.__module__ = 'gnd.model'

_resolved_primitive.__module__ = 'gnd.model'

_supertype_parents.__module__ = 'gnd.model'

_object_types_by_id.__module__ = 'gnd.popvalidate'

_identifying_primitive.__module__ = 'gnd.popvalidate'

_identifying_id.__module__ = 'gnd.popvalidate'

_resolve_reference.__module__ = 'gnd.popvalidate'

resolve_reference_value_type.__module__ = 'gnd.popvalidate'

resolve_primitive.__module__ = 'gnd.popvalidate'

_is_implemented.__module__ = 'gnd.checker'

_constraint_role_refs.__module__ = 'gnd.checker'

_scope_fact_types.__module__ = 'gnd.checker'

_fact_type_by_id.__module__ = 'gnd.checker'

_role_object_type.__module__ = 'gnd.checker'

_descendant_closure.__module__ = 'gnd.checker'

_denoting_types.__module__ = 'gnd.checker'

_instance_values_of.__module__ = 'gnd.checker'

_kind_of.__module__ = 'gnd.checker'

_instances_of.__module__ = 'gnd.checker'
