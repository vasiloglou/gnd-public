"""Ground atom evaluation over a fact list. Stdlib only, by construction.

An operation's preconditions, effects and dynamic-rule subjects are all ATOMS:
a fact type plus a binding of role names to terms. At evaluation time a walk has
already supplied a value for every declared parameter, so every term is either a
``$var`` with a binding or a literal. There is no unification, no search and no
join to do -- which is the whole reason this module is small enough to be
obviously correct.

Value identity is INJECTED, never imported. ``1``, ``1.0`` and ``True`` have to
compare the way the checker compares them, or a fact this module says is present
is a fact the checker counts twice; but importing the checker's private key
function here would make the module's isolation a fiction. So the two entry
points that compare take ``identity`` as a keyword-only argument, and
``transition.py`` owns the single import and passes it in. The two that only
substitute or reshape take nothing: they never compare anything.

The module is therefore unit-testable with a toy identity function, and exactly
one identity semantics exists in the process.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

#: A parameter name to its bound value. Supplied by the walk, one per step.
Bindings = dict[str, Any]

#: A value to its comparison key. ``checker._identity_key`` in production.
Identity = Callable[[Any], Any]


class UnboundTermError(KeyError):
    """A ``$var`` term named no bound parameter.

    Deliberately unreachable at evaluation time, and left as an exception rather
    than a silent ``None`` so that "unreachable" is a claim something can break.
    Two guards stand in front of it: an atom naming an undeclared parameter is
    refused at authoring time by ``semantic:op-term-ref`` (Phase 1), and a walk
    whose bindings are not exactly the declared parameter set is refused at load
    time by ``transition:bindings-mismatch``. A structural test asserts both.
    """


def resolve_term(term: Any, bindings: Bindings) -> Any:
    """``'$expense'`` -> ``bindings['expense']``; anything else is a literal.

    No ``identity`` parameter: substitution compares nothing.
    """
    if isinstance(term, str) and term.startswith("$"):
        name = term[1:]
        if name not in bindings:
            raise UnboundTermError(name)
        return bindings[name]
    return term


def ground_atom(atom: dict[str, Any], bindings: Bindings) -> tuple[str, dict[str, Any]]:
    """``(fact_type_id, {role: value})``, with omitted roles left omitted.

    The omission is load-bearing: a ``retract`` may bind a subset of the roles,
    and the roles it does not bind are wildcards that select every value. An
    ``assert`` binds all of them, which layer 2 already enforces
    (``semantic:op-effect-ground``), so a partially bound atom here is always a
    selector and never a fact.
    """
    # The ONE raw bind read left in src/gnd (v5.1 D-P1.4 ruled 28 sites; this
    # is the 28th). It stays raw because this module imports NOTHING from gnd
    # -- a boundary two reviewers enforced against an earlier draft, and one
    # `test_patterns_imports_nothing_but_the_standard_library` makes literal.
    # It is also not a consumer of untrusted shapes: every atom reaching here
    # comes from `transition.py` walking an already-loaded model, so the
    # meta-schema has already accepted `bind` as a mapping (IF-P1-9).
    bound = atom.get("bind") or {}
    return str(atom.get("fact_type")), {
        str(role): resolve_term(term, bindings) for role, term in bound.items()
    }


def matches(fact: dict[str, Any], roles: dict[str, Any], *, identity: Identity) -> bool:
    """True if ``fact`` agrees on every role in ``roles``. Unbound roles are free."""
    return all(
        role in fact and identity(fact[role]) == identity(value)
        for role, value in roles.items()
    )


def holds(
    atom: dict[str, Any],
    facts: list[dict[str, Any]],
    bindings: Bindings,
    *,
    identity: Identity,
) -> bool:
    """True if some fact agrees on every bound role. Ground membership, nothing more."""
    _, roles = ground_atom(atom, bindings)
    return any(matches(fact, roles, identity=identity) for fact in facts)


def select(
    atom: dict[str, Any],
    facts: list[dict[str, Any]],
    bindings: Bindings,
    *,
    identity: Identity,
) -> list[int]:
    """Indices of every fact agreeing on the bound roles -- the retract selector.

    Indices rather than facts so a caller can remove them without relying on
    value equality a second time, which is where a wildcard retract of two
    identical-looking facts would otherwise go wrong.
    """
    _, roles = ground_atom(atom, bindings)
    return [
        index for index, fact in enumerate(facts) if matches(fact, roles, identity=identity)
    ]
