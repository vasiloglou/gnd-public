"""The two admitted-value bridges, and the verified gates they submit to.

`gnd.proof_kernel` is the whole verified slice and holds nothing this file
needs; this file holds everything the pinned verifier cannot translate. Both
bridges take or return a type the rest of GND uses and Nagini 1.3.1 does not:
`adapt_phase1_slice` reads an admitted pydantic `Model` and `Population` plus
raw `dict[str, Any]` constraint fragments, and `project_phase1_result` returns
the report's `dict[str, Any]`.

**Neither bridge decides anything.** The adapter proposes a canonicalization and
`admit_phase1_slice` -- proved -- decides whether it preserves what was
observed; the projector asks `project_one_verdict`, `phase1_counts`,
`compose_phase1_band`'s band and `phase1_acceptance_ready` for every semantic
field and then only builds containers around the answers. What remains here is
extraction and assembly, and the phase record states that residual instead of
calling it proved.
"""

from __future__ import annotations

from typing import Any

from gnd.documents import Model
from gnd.population import Population
from gnd.proof_kernel import (
    SLICE_VERDICT_NAMES,
    ProjectedVerdict,
    SliceGroup,
    SliceInput,
    SliceVerdict,
    admit_phase1_slice,
    decide_phase1_assurance,
    phase1_acceptance_ready,
    phase1_counts,
    project_one_verdict,
)


def adapt_phase1_slice(
    model: Model,
    population: Population,
    constraint: dict[str, Any],
    fact_type: dict[str, Any] | None,
    constraint_ref: str,
) -> SliceInput | None:
    """Admitted values to the bounded slice value, or None (never an exception).

    Every value this returns came back from `admit_phase1_slice`, so a
    canonicalization that lost, invented, deduplicated or miscounted an observed
    identity is refused by a proof rather than by this function's own care.
    """
    proposed = _candidate_slice(model, population, constraint, fact_type, constraint_ref)
    if proposed is None:
        return None
    candidate, universe_values, player_values, role_values = proposed
    return admit_phase1_slice(candidate, universe_values, player_values, role_values)


def phase1_refusal_reason(
    model: Model,
    population: Population,
    constraint: dict[str, Any],
    fact_type: dict[str, Any] | None,
    constraint_ref: str,
) -> str | None:
    """Which A14.4 refusal token a refused constraint earned, or None.

    Review finding R12: the ratified refusal vocabulary had no reader -- a
    refusal was recorded nowhere, against section 5.2's own words. The
    classification runs the SAME pipeline the adapter runs (never a second
    copy of either rule): a constraint the candidate builder cannot shape is
    out-of-scope-family; one whose candidate the verified admission gate then
    refuses is out-of-scope-cardinality. A constraint the pipeline admits
    earns no refusal row. The evidence-not-current token has no seam here:
    currency is decided by the evidence runner, not at check time.
    """
    proposed = _candidate_slice(model, population, constraint, fact_type, constraint_ref)
    if proposed is None:
        return "out-of-scope-family"
    candidate, universe_values, player_values, role_values = proposed
    if admit_phase1_slice(candidate, universe_values, player_values, role_values) is None:
        return "out-of-scope-cardinality"
    return None


def project_phase1_result(
    verdicts: tuple[SliceVerdict, ...],
    *,
    band: int,
    coverage: tuple[tuple[str, str, int], ...],
    applicable: int,
    current: int,
    in_scope: bool,
) -> dict[str, Any]:
    """N8. Containers around values the verified kernel already decided."""
    decision, assurance = decide_phase1_assurance(
        band=band, applicable=applicable, current=current, in_scope=in_scope
    )
    counts = phase1_counts(verdicts)
    return {
        # N8's counts keys are SLICE_VERDICT_NAMES itself -- the kernel owns both
        # the numbers and their order, and restating the tuple here was the
        # two-homes drift standing rule 4 forbids (refactoring review, phase 1).
        "counts": dict(zip(SLICE_VERDICT_NAMES, counts, strict=True)),
        "verdicts": [_public_row(project_one_verdict(verdict)) for verdict in verdicts],
        "coverage": {
            fact_type_id: {"declared": declared, "facts": facts}
            for fact_type_id, declared, facts in coverage
        },
        "exit_code": band,
        "acceptance_ready": phase1_acceptance_ready(band),
        "phase1_assurance": {
            "semantic_decision": decision,
            "assurance_level": assurance,
            "applicable": applicable,
            "current": current,
            "in_scope": in_scope,
        },
    }


def _public_row(row: ProjectedVerdict) -> dict[str, Any]:
    """One projected verdict as a dict. Every value is `row`'s, unchanged."""
    return {
        "constraint_ref": row.constraint_ref,
        "constraint_type": row.constraint_type,
        "modality": row.modality,
        "verdict": row.verdict,
        "reason_code": row.reason_code,
        "offending_facts": public_witness(row),
        "phase1_reason_code": row.reason_code,
    }


def public_witness(row: ProjectedVerdict) -> list[Any]:
    """A14.3. Today's family-specific public witness shape, byte for byte.

    Whether to flatten is `row.flatten_witness`, decided by the verified
    `project_one_verdict`; applying it is the only thing left here.
    """
    if row.flatten_witness:
        return [values[0] for values in row.witness]
    return [list(values) for values in row.witness]


def _candidate_slice(
    model: Model,
    population: Population,
    constraint: dict[str, Any],
    fact_type: dict[str, Any] | None,
    constraint_ref: str,
) -> tuple[SliceInput, tuple[str, ...], tuple[str, ...], tuple[str, ...]] | None:
    """The raw extraction: a candidate, plus the observations it must preserve.

    The three tuples beside the candidate are what was actually seen, in the
    order it was seen, duplicates intact. They exist so `admit_phase1_slice` has
    something to check the candidate AGAINST; a bridge that returned only the
    candidate would be asking to be trusted.
    """
    constraint_type = constraint.get("type")
    modality = constraint.get("modality")
    if modality not in ("alethic", "deontic"):
        return None

    if constraint_type == "textual" and fact_type is None:
        if not isinstance(constraint.get("expression"), str):
            return None
        return (
            SliceInput(
                constraint_ref, "textual-refusal", modality, True, True, (), (), (), None, None
            ),
            (),
            (),
            (),
        )

    if fact_type is None:
        return None
    fact_type_id = str(fact_type.get("id"))
    facts = population.facts.get(fact_type_id) or []
    covered = fact_type_id in population.covers

    if constraint_type == "mandatory":
        role_name = constraint.get("role")
        if not isinstance(role_name, str):
            return None
        object_type_id = _role_object_type(fact_type, role_name)
        if object_type_id is None:
            return None
        if _universe_is_widened(object_type_id, model):
            return None
        raw_universe = _observed(_universe_values(object_type_id, model, population))
        raw_players = _observed(fact[role_name] for fact in facts if role_name in fact)
        if raw_universe is None or raw_players is None:
            return None
        return (
            SliceInput(
                constraint_ref,
                "mandatory",
                modality,
                covered,
                bool(facts),
                _canonical(raw_universe),
                _canonical(raw_players),
                (),
                None,
                None,
            ),
            raw_universe,
            raw_players,
            (),
        )

    if constraint_type != "frequency" or constraint.get("scope") != "internal":
        return None
    roles = constraint.get("roles")
    bound = constraint.get("bound")
    if not isinstance(roles, list) or len(roles) != 1 or not isinstance(roles[0], str):
        return None
    if not isinstance(bound, dict):
        return None
    raw_roles = _observed(fact[roles[0]] for fact in facts if roles[0] in fact)
    if raw_roles is None:
        return None
    return (
        SliceInput(
            constraint_ref,
            "frequency",
            modality,
            covered,
            bool(facts),
            (),
            (),
            _frequency_groups(raw_roles),
            bound.get("min"),
            bound.get("max"),
        ),
        (),
        (),
        raw_roles,
    )


def _role_object_type(fact_type: dict[str, Any], role_name: str) -> str | None:
    for role in fact_type.get("roles") or []:
        if isinstance(role, dict) and role.get("role_name") == role_name:
            object_type = role.get("object_type")
            return str(object_type) if object_type is not None else None
    return None


def _universe_is_widened(object_type_id: str, model: Model) -> bool:
    """Whether the production universe walk reaches beyond N2's own words.

    N2 excludes subtypes and entity-reference closure from the slice, and the
    production walk deliberately includes both (CORE-06, F-01). A model where
    the two walks could differ is therefore OUTSIDE the slice, and the bridge
    refuses it so the legacy path decides -- same bytes, no slice-coverage
    claim (review finding R8: a subtype-widened universe shipped a phase1
    trace before this refusal existed). The closure questions are answered by
    the checker's own helpers rather than by a second copy of either rule.
    """
    from gnd.universe import denoting_types as _denoting_types
    from gnd.universe import descendant_closure as _descendant_closure

    if _descendant_closure(object_type_id, model) != {object_type_id}:
        return True
    kinds = {
        str(object_type.get("id")): object_type.get("kind") for object_type in model.object_types
    }
    return bool(kinds.get(object_type_id) == "value" and _denoting_types({object_type_id}, model))


def _universe_values(object_type_id: str, model: Model, population: Population) -> list[Any]:
    """N2's universe, taken from the ONE production walk that defines it.

    Imported inside the function because `gnd.checker` imports this module: the
    seam runs the other way. The duplicate-derivation alternative is what
    standing rule 4 forbids, so the cycle is broken here rather than by writing
    the universe rule down twice.
    """
    from gnd.universe import instance_values_of as _instance_values_of

    return list(_instance_values_of(object_type_id, model, population))


def _observed(values: Any) -> tuple[str, ...] | None:
    """What was seen, in the order it was seen, or a refusal.

    A non-String primitive refuses the whole slice rather than being coerced --
    coercion is the mutation M15 exists to catch, and it dies here because the
    refusal happens before anything is canonicalized.
    """
    seen: list[str] = []
    for value in values:
        if not isinstance(value, str):
            return None
        seen.append(value)
    return tuple(seen)


def _canonical(values: tuple[str, ...]) -> tuple[str, ...]:
    """N1's canonical identities: sorted and unique.

    The ASCENDING order is this function's alone. `admit_phase1_slice` proves
    distinctness and set equality, and cannot prove the order because Nagini
    1.3.1 defines no comparison on strings; `tests/test_v6_phase1_adapter.py`
    holds the order and M12 reds when it moves.
    """
    return tuple(sorted(set(values)))


def _frequency_groups(values: tuple[str, ...]) -> tuple[SliceGroup, ...]:
    """N4's occurring groups. Multiplicity survives only in the count."""
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return tuple(SliceGroup((key,), counts[key]) for key in sorted(counts))
