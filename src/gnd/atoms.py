"""The ONE reader for an atom's role bindings.

v5.1 Phase 1 §6.7 (O10, D-P1.4). Twenty-eight raw ``atom.get("bind")`` sites
existed across four modules and only five guarded the shape at the site, so the
same malformed document was tolerated in one place and raised in another.
Standing rule 1: totality belongs to the FUNCTION, not to twenty-eight callers
who each have to remember.

**Why the values are kept as they are.** The spec sketched
``_atom_bind(atom) -> dict[str, str]``, discarding a bind "with non-string
values". Measured against the meta-schema, that would be wrong:
``$defs/term`` is ``$defs/scalar``, typed ``["string", "number", "boolean"]``,
so ``bind: {quantity: 3}`` and ``bind: {urgent: true}`` are VALID models. A
str-only reader would silently return ``{}`` for them -- every role in such an
atom would vanish from role-name validation, guarded matching and
verbalization at once. Values are therefore returned unchanged; ``$``-variable
resolution stays where it already lives, in the caller.

The guarantee here is narrow and total: whatever the document contains, the
result is a mapping with string keys, and nothing raises.
"""

from __future__ import annotations

from typing import Any

__all__ = ["atom_bind", "atom_has_bind"]


def atom_bind(atom: object) -> dict[str, Any]:
    """The atom's role bindings as ``{role_name: term}`` -- total, never raises.

    A non-mapping atom, a missing ``bind``, or a ``bind`` that is not itself a
    mapping all yield ``{}``. Keys are coerced with ``str`` because a YAML
    document can present ``1:`` as an integer key, and every caller compares
    role names as strings.
    """
    if not isinstance(atom, dict):
        return {}
    bind = atom.get("bind")
    if not isinstance(bind, dict):
        return {}
    return {str(role_name): term for role_name, term in bind.items()}


def atom_has_bind(atom: object) -> bool:
    """Whether the atom carries a well-formed ``bind`` MAPPING at all.

    Distinct from ``atom_bind(atom) != {}``: this answers the structural
    question two validation predicates ask -- is the key present and of the
    right kind -- for which an empty mapping is present-but-empty rather than
    absent, and the meta-schema's ``minProperties: 1`` makes that a defect
    worth reporting rather than skipping.
    """
    return isinstance(atom, dict) and isinstance(atom.get("bind"), dict)
