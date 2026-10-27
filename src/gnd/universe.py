"""RF3 shared dependency home; algorithms retain predecessor semantics."""
from __future__ import annotations

from collections.abc import Mapping
from contextvars import ContextVar
from typing import Any, Literal  # noqa: F401 -- compatibility export

from gnd.atoms import atom_has_bind
from gnd.constraint_families import FAMILIES, resolve_hook
from gnd.documents import Model
from gnd.model_index import ModelIndex
from gnd.model_queries import _identifying_id, _identifying_primitive, _resolve_reference


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


from gnd.model_queries import (
    _resolved_primitive,
    _supertype_parents,
)

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


from collections.abc import Callable  # noqa: F401 -- compatibility export


def _object_types_by_id(model: Model) -> dict[str, dict[str, Any]]:
    return ModelIndex.object_map(model)


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


from gnd.model_queries import primitive_for

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
    entry = FAMILIES.get(constraint.get("type"))
    if entry is None or not entry.implemented:
        return False
    return resolve_hook(entry.shape, globals())(constraint, fact_type)


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
    constraint: dict[str, Any], constraint_type: str, model: Model,
    fact_type: dict[str, Any] | None,
) -> list[str]:
    """Shared host/reference precedence followed by a registered scope hook."""
    if fact_type is not None:
        return [str(fact_type.get("id"))]
    entry = FAMILIES.get(constraint_type)
    if entry is not None and entry.scope_before_refs:
        return resolve_hook(entry.scope, globals())(constraint, constraint_type, model, fact_type)
    referenced = [str(ref.get("fact_type")) for ref in _constraint_role_refs(constraint)]
    if referenced:
        return list(dict.fromkeys(referenced))
    if entry is None:
        return []
    return resolve_hook(entry.scope, globals())(constraint, constraint_type, model, fact_type)


def _fact_type_by_id(model: Model, fact_type_id: str) -> dict[str, Any] | None:
    return ModelIndex.legacy_fact_type(model, fact_type_id)


def _role_object_type(model: Model, fact_type_id: str, role_name: str) -> str | None:
    return ModelIndex.legacy_role_type(model, fact_type_id, role_name)


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


def _universe_types(object_type_id: str, model: Model) -> set[str]:
    """The object types whose rosters and roles feed ``object_type_id``'s universe.

    Every transitive subtype, plus, for a value type, every entity type its
    values denote. :func:`_instance_values_of` walks exactly these, and a
    witness drawn from that universe takes its spelling from them too.
    """
    covered = _descendant_closure(object_type_id, model)
    if _kind_of(object_type_id, model) == "value":
        return covered | _denoting_types(covered, model)
    return covered


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
    collected = _universe_types(object_type_id, model)
    values: list[Any] = []
    for collected_id in [object_type_id, *sorted(collected - {object_type_id})]:
        values.extend(population.instances.get(collected_id, []))
    for fact_type in ModelIndex.for_model(model).iter_fact_types_shared():
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
universe_types = _universe_types

from typing import TYPE_CHECKING

if TYPE_CHECKING:
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

def _family_implemented_anchored(constraint, fact_type):
    return fact_type is not None


def _family_implemented_uniqueness(constraint, fact_type):
    if fact_type is not None:
        return isinstance(constraint.get("roles"), list)
    return constraint.get("scope") == "external" and bool(constraint.get("role_refs"))


def _family_implemented_mandatory(constraint, fact_type):
    return fact_type is not None and constraint.get("role") is not None


def _family_implemented_value(constraint, fact_type):
    forms = [key for key in ("allowed", "range", "ranges") if constraint.get(key) is not None]
    return constraint.get("object_type") is not None and len(forms) == 1


def _family_implemented_mandatory_disjunctive(constraint, fact_type):
    return bool(constraint.get("role_refs"))


def _family_implemented_frequency(constraint, fact_type):
    return bool(constraint.get("bound")) and (
        bool(constraint.get("roles")) or bool(constraint.get("role_refs"))
    )


def _family_implemented_subset(constraint, fact_type):
    return bool(constraint.get("subset_role_seq")) and bool(constraint.get("superset_role_seq"))


def _family_implemented_equality(constraint, fact_type):
    return bool(constraint.get("role_seq_a")) and bool(constraint.get("role_seq_b"))


def _family_implemented_exclusive_or(constraint, fact_type):
    return bool(constraint.get("role_seqs"))


def _family_implemented_ring(constraint, fact_type):
    return fact_type is not None and constraint.get("variant") in _RING_VARIANTS


def _family_implemented_value_comparison(constraint, fact_type):
    return (
        constraint.get("operator") is not None
        and constraint.get("role_a") is not None
        and constraint.get("role_b") is not None
    )


def _family_implemented_guarded(constraint, fact_type):
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


def _family_implemented_subtype_partition(constraint, fact_type):
    return constraint.get("supertype") is not None and bool(constraint.get("subtypes"))


def _family_implemented_cardinality(constraint, fact_type):
    if not constraint.get("bound"):
        return False
    if constraint.get("scope") == "object":
        return constraint.get("object_type") is not None and constraint.get("role_ref") is None
    if constraint.get("scope") == "role":
        return constraint.get("role_ref") is not None and constraint.get("object_type") is None
    return False


def _family_scope_guarded(constraint, constraint_type, model, fact_type):
    antecedent = constraint.get("antecedent")
    if not isinstance(antecedent, list):
        return []
    referenced = [
        str(atom.get("fact_type"))
        for atom in antecedent
        if isinstance(atom, dict) and atom.get("fact_type") is not None
    ]
    return list(dict.fromkeys(referenced))


def _family_scope_value(constraint, constraint_type, model, fact_type):
    target = constraint.get("object_type")
    return ModelIndex.scope_facts(model, (target,))


def _family_scope_subtype_partition(constraint, constraint_type, model, fact_type):
    targets = {constraint.get("supertype"), *(constraint.get("subtypes") or [])}
    return ModelIndex.scope_facts(model, targets)


def _family_scope_empty(constraint, constraint_type, model, fact_type):
    return []


def _family_shape_false(constraint, fact_type):
    return False


def _family_shape_true(constraint, fact_type):
    return True
