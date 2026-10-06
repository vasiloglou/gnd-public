"""Existing model operations section; historical facade retained."""
from __future__ import annotations

from typing import Any

from gnd.atoms import atom_bind
from gnd.documents import Model
from gnd.model._validation import _derivation_bind


def _effect_index(operations: list[dict[str, Any]]) -> dict[str, Any]:
    """How many operations assert each fact type, and which retract it.

    Both halves are needed to decide whether a precondition can be lifted into a
    standing claim -- see :func:`compile_operation`.
    """
    counts: dict[str, int] = {}
    retracted: set[str] = set()
    for operation in operations:
        asserted: set[str] = set()
        for effect in operation.get("effects") or []:
            if not isinstance(effect, dict):
                continue
            if isinstance(effect.get("assert"), dict) and effect["assert"].get("fact_type"):
                asserted.add(str(effect["assert"]["fact_type"]))
            if isinstance(effect.get("retract"), dict) and effect["retract"].get("fact_type"):
                retracted.add(str(effect["retract"]["fact_type"]))
        for fact_type_id in asserted:
            counts[fact_type_id] = counts.get(fact_type_id, 0) + 1
    return {"asserters": counts, "retracted": retracted}


def _variables_in(atom: dict[str, Any]) -> set[str]:
    return {
        str(term)[1:]
        for term in _derivation_bind(atom).values()
        if isinstance(term, str) and term.startswith("$")
    }


def _roles_by_variable(atom: dict[str, Any]) -> dict[str, list[str]]:
    """``{parameter name: [role names]}`` for the atom's variable bindings.

    A MULTIMAP, because one parameter may occupy two roles: `A(left: $x, right:
    $x)` is a legal atom, and a plain dict kept only the last role -- so a
    compiled obligation over such an atom compared one role pair and called
    `B(1,1)` matched by `A(2,1)`. Found by adversarial review.
    """
    roles: dict[str, list[str]] = {}
    for role, term in atom_bind(atom).items():
        if isinstance(term, str) and term.startswith("$"):
            roles.setdefault(str(term)[1:], []).append(str(role))
    return roles


def _has_literal(atom: dict[str, Any]) -> bool:
    return any(
        not (isinstance(term, str) and term.startswith("$"))
        for term in _derivation_bind(atom).values()
    )


def compile_operation(operation: dict[str, Any], effects: dict[str, Any]) -> list[dict[str, Any]]:
    """Standing obligations derivable from one operation's preconditions.

    A precondition is a claim about the instant a step runs. Some of them imply
    something DURABLE: `reimburse_expense` requires the expense to have reached
    Workday and records that it was reimbursed, so every reimbursed expense in
    any population, walk or no walk, was submitted. That second sentence is
    checkable against data at rest, and deriving it is what compilation means.

    Only one shape compiles: a literal-free, single-atom precondition sharing at
    least one parameter with an asserted fact type. The quantifier is
    EXISTENTIAL and was measured rather than preferred -- under the universal
    reading nothing at all compiles in the 13-operation corpus model, because
    every all-shared precondition is disqualified for carrying a literal or for
    being one atom of a conjunction, so the whole feature would ship with no
    case that could observe it. Unshared parameters are quantified away, which
    makes the result a role-projection subset: standard ORM.

    TWO guards make that lift sound, and one of them was missing until an
    adversarial review supplied the counterexample.

    The SOLE-ASSERTER guard: the derived claim generalizes over facts of the
    ASSERTED type, so it only follows if this operation is the only way such
    facts arise.

    The NO-RETRACT guard: the claim also depends on the REQUIRED fact still
    being there. An operation that requires A, asserts B and retracts A in the
    same step is entirely legal -- and the state it produces breaks "every B has
    an A", so running the same walk twice reports an alethic failure against a
    state its own operation produced. If any operation in the model retracts the
    required fact type, the obligation is retained instead.

    Both guards make an assumption mechanical instead of promised. Neither makes
    the lift unconditionally valid: a population may contain facts with no
    operational provenance at all, which is why these obligations are evaluated
    inside a walk and never published as model constraints.

    Everything else is retained with a ``transition-only`` reason. Retained is
    not skipped: the transition evaluator checks it at the step, it simply
    cannot be lifted into a claim about data at rest.
    """
    parameters = {str(p.get("name")) for p in operation.get("parameters") or []}
    asserted: list[dict[str, Any]] = [
        effect["assert"]
        for effect in operation.get("effects") or []
        if isinstance(effect, dict) and isinstance(effect.get("assert"), dict)
    ]
    compiled: list[dict[str, Any]] = []
    for index, obligation in enumerate(operation.get("preconditions") or []):
        atoms = obligation.get("require") or []
        entry: dict[str, Any] = {
            "obligation": str(obligation.get("id")),
            "modality": str(obligation.get("modality", "")),
            "source_index": index,
        }
        if len(atoms) != 1:
            entry["transition-only"] = f"conjunctive precondition of {len(atoms)} atoms"
            compiled.append(entry)
            continue
        atom = atoms[0]
        if _has_literal(atom):
            entry["transition-only"] = "atom carries a literal"
            compiled.append(entry)
            continue
        required_type = str(atom.get("fact_type"))
        if required_type in effects["retracted"]:
            entry["transition-only"] = (
                f"'{required_type}' is retracted by some operation, so the derived "
                f"claim would not stay true of a state this model can produce"
            )
            compiled.append(entry)
            continue
        atom_roles = _roles_by_variable(atom)
        sharing = [
            (effect, sorted(set(atom_roles) & set(_roles_by_variable(effect)) & parameters))
            for effect in asserted
        ]
        sharing = [(effect, shared) for effect, shared in sharing if shared]
        if not sharing:
            entry["transition-only"] = "no parameter is bound by any asserted fact type"
            compiled.append(entry)
            continue
        sole = [
            (effect, shared)
            for effect, shared in sharing
            if effects["asserters"].get(str(effect["fact_type"]), 0) == 1
        ]
        if not sole:
            crowded = sorted({str(effect["fact_type"]) for effect, _ in sharing})
            entry["transition-only"] = (
                f"asserted fact type(s) {crowded} are asserted by more than one "
                f"operation, so the derived claim would not follow"
            )
            compiled.append(entry)
            continue
        # EVERY eligible asserted fact type, not the first one sorted: an
        # operation asserting both B and C from one precondition licenses two
        # claims, and taking `sole[0]` silently dropped the other -- so a
        # pre-state violating it was never checked. Found by adversarial review.
        for effect, shared in sole:
            effect_roles = _roles_by_variable(effect)
            # Role PAIRS, not parameter names: the evaluator compares a role of
            # the asserted fact type against a role of the required one, and the
            # parameter is only the link between them. One parameter may occupy
            # several roles on either side, so every combination is a pair the
            # comparison must hold for.
            pairs = [
                (of_role, in_role)
                for name in shared
                for of_role in effect_roles[name]
                for in_role in atom_roles[name]
            ]
            compiled.append(
                {
                    **entry,
                    "subset": {"of": str(effect["fact_type"]), "in": required_type},
                    "role_pairs": pairs,
                    "atom": atom,
                    "locator": (
                        f"$.operations[id={operation.get('id')}].compiled[{len(compiled)}]"
                    ),
                }
            )
    return compiled


def _attach_compiled_obligations(model: Model) -> None:
    """Attach ``operation["compiled"]`` IN MEMORY, after semantic validation.

    Never on ``Model.constraints``, never serialized, never in YAML, and -- after
    a reproduced defect -- never on the operation dicts either. See
    :attr:`Model._compiled`: writing into them moved ``operations_digest``,
    because that digest is taken over exactly the section being written to. The
    side table leaves the loaded document byte-for-byte as authored, so both
    digests are stable by construction rather than by careful stripping.

    Runs only when the model declares operations, so a v1 document's load path
    is byte-identical to what it was before v2 existed.
    """
    if not model.operations:
        return
    effects = _effect_index(model.operations)
    for operation in model.operations:
        model._compiled[str(operation.get("id"))] = compile_operation(operation, effects)



_effect_index.__module__ = 'gnd.model'
_variables_in.__module__ = 'gnd.model'
_roles_by_variable.__module__ = 'gnd.model'
_has_literal.__module__ = 'gnd.model'
compile_operation.__module__ = 'gnd.model'
_attach_compiled_obligations.__module__ = 'gnd.model'
