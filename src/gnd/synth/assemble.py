"""Constraint-directed conforming assembly, verified against the real checker.

``assemble_conforming`` builds a population a model's checker accepts as
conforming — every ALETHIC constraint satisfied (convergence is defined on
alethic ``fail`` only: an alethic ``textual`` holds the run at band 4 forever,
and that is correct). It does so on TWO oracles that must never be conflated:

**The checker is a SEARCH HEURISTIC, never the ground-truth oracle (C1).** The
repair fixpoint uses ``gnd.checker.check`` to find which constraints are not yet
satisfied and repairs them — but GROUND TRUTH is the assembler's own INDEPENDENT
constructive witness (:mod:`this module`'s ``_witness_*`` predicates, a separate
re-implementation of ORM population semantics, never a call into the checker).
Three outcomes at the budget edge:

- checker reports zero alethic ``fail`` AND every witness holds -> converged,
  ground truth ``satisfied`` by construction;
- a constraint's witness does not hold AND the checker fails it too -> the
  generator genuinely failed -> :class:`GeneratorError`, exit 5,
  ``not-derivable``, naming the constraint (this is also where the oscillation
  and budget branches land);
- the checker reports an alethic ``fail`` on a constraint whose witness DOES
  hold -> checker and independent oracle DISAGREE -> a candidate checker
  false-fail (D-01): :class:`CheckerWitnessDiscrepancy` carrying the population
  so the caller QUARANTINES it and exits 6. The case is retained and its ground
  truth is NEVER relabelled to match the observation — that relabelling is the
  oracle-circularity C1 exists to prevent;
- the checker reports NO alethic fail on a constraint whose witness proves it
  VIOLATED -> the same disagreement in the other direction, a candidate checker
  false-PASS -> the same :class:`CheckerWitnessDiscrepancy`, retention and exit
  6 (CR-04). Symmetry is the point: this direction used to exit 5 and DISCARD
  the document, so the one artifact reproducing the defect class D-01 calls a
  defect at any count was destroyed, and the event was labelled a generator
  limitation.

**Expectations come from the independent oracle, never from the report.**
``_build_expectations`` derives every constraint's ``(ground_truth,
expected_verdict, reason)`` from :func:`gnd.synth.mutate.expected_state`.
Copying ``expected_verdict`` off the verdict the checker just emitted (the shape
this module once had) makes the checker's own answer the standard it is measured
against — the same circularity, arriving through the sidecar.

**Every emitted population is re-admitted through ``load_population`` (exit 5 on
rejection).** A structurally-invalid population contributes zero verdicts, hence
zero errors, hence a perfect score, so it must be loud.

**The non-degeneracy gate is POSITIVE (Claude-HIGH).** Plan 01 excluded
``subset`` from the vacuity table, so a degenerate subset join never emits
``vacuous``; waiting for that verdict would sail a zero-row join through as clean.
:func:`assert_non_degenerate` instead asserts every join-scoped subject sequence
(spanning >1 fact type — ``subset``'s included) yields >=1 row, reusing the
checker's own ``_role_seq_tuples`` so the count is the checker's join, not a
re-implementation.
"""

from __future__ import annotations

import json
import math  # noqa: F401 -- historical compatibility binding
import tempfile
from collections.abc import Callable
from dataclasses import (
    dataclass,  # noqa: F401 -- historical compatibility binding
    field,  # noqa: F401 -- historical compatibility binding
)
from datetime import (
    date,  # noqa: F401 -- historical compatibility binding
    datetime,  # noqa: F401 -- historical compatibility binding
)
from itertools import product  # noqa: F401 -- historical compatibility binding
from pathlib import Path
from random import Random
from typing import Any

from gnd import checker as checker_module  # noqa: F401 -- historical compatibility binding
from gnd import input_policy as _rf7_input
from gnd import popvalidate
from gnd.address import positional_constraint_ref
from gnd.checker import check, structured_extension_view
from gnd.model import Model
from gnd.population import Population, PopulationValidationError, load_population
from gnd.synth.comparison import (
    normalize_operands as _normalize_comparison_operands,  # noqa: F401 -- historical compatibility binding
)
from gnd.synth.comparison import (
    role_literal_operands as _role_literal_operands,  # noqa: F401 -- historical compatibility binding
)
from gnd.synth.guarded import (
    antecedent_bindings as _exists_antecedent_bindings,
)
from gnd.synth.guarded import (
    exists_witness as _exists_witness,  # noqa: F401 -- historical compatibility binding
)
from gnd.synth.guarded import (
    has_private_exists_sources as _has_private_exists_sources,
)
from gnd.synth.guarded import (
    modular_repair_plan as _exists_modular_repair_plan,
)
from gnd.synth.identity import scalar_identity as _key
from gnd.synth.identity import tuple_identity as _tuple_key
from gnd.synth.oracle.constructive import (
    CHAIN_COMPATIBLE as _CHAIN_COMPATIBLE,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    EXTERNAL_UNIQUENESS_SEARCH_CAP as _EXTERNAL_UNIQUENESS_SEARCH_CAP,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    TEMPORAL_PRIMITIVES as _TEMPORAL_PRIMITIVES,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    Assembly as Assembly,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    Builder as _Builder,
)
from gnd.synth.oracle.constructive import (
    CheckerWitnessDiscrepancy as CheckerWitnessDiscrepancy,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    ExpectedStateData as ExpectedStateData,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    GeneratorError as GeneratorError,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    TermGenerationUnavailable as _TermGenerationUnavailable,
)
from gnd.synth.oracle.constructive import (
    acyclic as _acyclic,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    alethic_refs as _alethic_refs,
)
from gnd.synth.oracle.constructive import (
    assert_non_degenerate as assert_non_degenerate,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    compare_scalar as _compare_scalar,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    comparison_literal as _comparison_literal,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    constraint_iter_with_ref as _constraint_iter_with_ref,
)
from gnd.synth.oracle.constructive import (
    denoting_types as _denoting_types,  # noqa: F401 -- compatibility export
)
from gnd.synth.oracle.constructive import (
    descendants as _descendants,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    direct_subtypes as _direct_subtypes,
)
from gnd.synth.oracle.constructive import (
    fact_type_constraints as _fact_type_constraints,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    identity_unique as _identity_unique,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    in_range as _in_range,
)
from gnd.synth.oracle.constructive import (
    instant_pair as _instant_pair,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    is_external_entity as _is_external_entity,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    join as _join,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    join_scoped_sequences as _join_scoped_sequences,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    kind as _kind,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    measure_distinct_ratios as measure_distinct_ratios,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    object_types_by_id as _object_types_by_id,  # noqa: F401 -- compatibility export
)
from gnd.synth.oracle.constructive import (
    ordered_pair as _ordered_pair,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    project as _project,
)
from gnd.synth.oracle.constructive import (
    range_union_claim as _range_union_claim,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    ring_component_ok as _ring_component_ok,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    ring_satisfied as _ring_satisfied,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    role_object as _role_object,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    seq_tuples as _seq_tuples,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    universe as _universe,
)
from gnd.synth.oracle.constructive import (
    value_witness as _value_witness,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    witness as _witness,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.constructive import (
    witness_map as _witness_map,
)
from gnd.synth.pool import EntityPool  # noqa: F401 -- historical compatibility binding
from gnd.synth.poolfile import Pool, build_faker_pool
from gnd.synth.value_domain import (
    EmptyValueDomain,  # noqa: F401 -- historical compatibility binding
    draw_value_for_constraints,  # noqa: F401 -- historical compatibility binding
    governing_value_constraints,  # noqa: F401 -- historical compatibility binding
)

__all__ = [
    "Assembly",
    "CheckerWitnessDiscrepancy",
    "GeneratorError",
    "assemble_conforming",
    "assert_non_degenerate",
]












# --------------------------------------------------------------------------- #
# independent model introspection (no checker import for ground truth)
# --------------------------------------------------------------------------- #










# fmt: off










# --------------------------------------------------------------------------- #
# independent witnesses — the ground-truth oracle (C1)
# --------------------------------------------------------------------------- #










#: Primitives whose values are ISO-8601 TEXT but whose order is chronological.
#: Lexical order agrees with chronology for a well-formed ``Date``, but not for a
#: ``DateTime`` carrying a UTC offset — ``…T10:00:00+02:00`` sorts after
#: ``…T09:00:00Z`` as text and before it in time — so these are compared as
#: instants, not as strings.














# fmt: on




# --------------------------------------------------------------------------- #
# construction — a conforming population BY CONSTRUCTION, checker-verified later
# --------------------------------------------------------------------------- #












# --------------------------------------------------------------------------- #
# non-degeneracy — POSITIVE row-count gate (Claude-HIGH), reusing the checker join
# --------------------------------------------------------------------------- #








# --------------------------------------------------------------------------- #
# expectations (C3)
# --------------------------------------------------------------------------- #




def _build_expectations(
    model: Model, doc: dict[str, Any], children: dict[str, set[str]]
) -> dict[str, ExpectedStateData]:
    """Per-constraint :class:`ExpectedStateData` from the INDEPENDENT oracle (C1).

    BOTH fields come from :func:`gnd.synth.mutate.expected_state` — the same
    model-derived engine the violating, boundary and frontier classes already
    use — and neither is ever read off the report the checker just produced.

    The shape this replaces took ``ground_truth`` from the constructive witness
    (correct) but ``expected_verdict`` from ``obs_verdict``, the verdict the
    checker emitted for this very population. That made the checker's own answer
    the standard it is measured against, which is the oracle circularity C1
    exists to close, re-entering one relation over: a checker stubbed to answer
    ``vacuous`` for every ``value`` constraint over a fully-populated, satisfied
    universe scored ``correct`` on every observation and published
    ``undecided_rate 0.0`` — the one number D-02 exists to keep honest. Worse in
    the other direction: once an abstention became the expectation, a LATER,
    FIXED checker returning ``pass`` scored a ``false_pass`` and exited 6, so
    repairing a checker made the committed corpus report a defect.

    A divergence between the derived expectation and the observation is now a
    MEASURED cell (``undecided`` / ``false_pass`` / ``false_fail``) rather than
    being defined away — that is the channel D-02 promises, and the alethic-fail
    directions are additionally quarantined upstream at exit 6.

    A constraint the oracle cannot label (``expected_state`` returns ``None``) is
    NOT defaulted to the observation: it is ``not-derivable``, and a conforming
    population carrying one raises :class:`GeneratorError`. Naming it is the
    point — an unlabelled constraint scored ``correct`` keeps the applicability
    matrix reading 1.0000 over a cell whose ground truth is the checker's output.
    """
    # Local import: gnd.synth.mutate imports this module, so the shared oracle
    # cannot be bound at module scope. It is the SAME function the mutation,
    # boundary and frontier layers call — one oracle, four consumers.
    from gnd.synth.oracle.state import expected_state

    out: dict[str, ExpectedStateData] = {}
    unlabelled: list[str] = []
    for ref, constraint, ft in _constraint_iter_with_ref(model):
        state = expected_state(constraint, ft, doc, model, children)
        if state is None:
            unlabelled.append(f"{ref} [{constraint.get('type')}]")
            continue
        out[ref] = state
    if unlabelled:
        raise GeneratorError(
            f"no independent expected-state oracle for {sorted(unlabelled)} — the "
            f"conforming class cannot label them, so they are not-derivable "
            f"(exit 5). Copying the checker's own verdict in as the expectation "
            f"would score them `correct` forever and hide the gap behind a "
            f"coverage fraction of 1.0000."
        )
    return out


# --------------------------------------------------------------------------- #
# orchestration
# --------------------------------------------------------------------------- #


def _load_temp(doc: dict[str, Any], model: Model) -> Population:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
        json.dump(doc, handle)
        temp_path = handle.name
    try:
        return load_population(temp_path, model=model)
    finally:
        Path(temp_path).unlink(missing_ok=True)


def _alethic_fails(report) -> list[Any]:
    return [v for v in report.verdicts if v.verdict == "fail" and v.modality == "alethic"]




def _false_pass_discrepancies(broken: list[str], report) -> list[dict[str, Any]]:
    """Typed discrepancy records for the false-PASS direction (CR-04).

    Mirrors the false-FAIL records field for field so both directions travel the
    same quarantine path; only ``witness``/``observed``/``kind`` differ, which is
    what lets a reader tell the two apart in the retained
    ``*.discrepancy.json``.
    """
    observed = {v.constraint_ref: v.verdict for v in report.verdicts} if report else {}
    return [
        {
            "constraint_ref": ref,
            "witness": "violated",
            "observed": observed.get(ref, "pass"),
            "kind": "candidate-false-pass",
        }
        for ref in broken
    ]




def assemble_conforming(
    model: Model,
    seed: int,
    *,
    pool: Pool | None = None,
    pool_size: int = 8,
    rows_per_fact_type: int = 6,
    max_rounds: int = 20,
    model_ref: str = "model.orm.yaml",
    fault: Callable[[dict[str, Any]], None] | None = None,
) -> Assembly:
    """Assemble a checker-verified conforming population for ``model``.

    See the module docstring for the C1 oracle-independence contract. Raises
    :class:`GeneratorError` (exit 5) on a genuine generator limitation or a
    re-admission failure, and :class:`CheckerWitnessDiscrepancy` (exit 6) on a
    checker/witness disagreement.
    """
    from gnd.terms import require_non_temporal

    require_non_temporal(model, "synth")
    rng = Random(seed)
    if pool is None:
        pool = build_faker_pool(model, Random(rng.getrandbits(64)), size_per_type=pool_size)

    children = _direct_subtypes(model)
    alethic = _alethic_refs(model)
    builder = _Builder(model, pool, rng, rows_per_fact_type)
    builder.construct()
    _seed_guarded_exists(builder, model)

    rounds = 0
    prev_fail_count: int | None = None
    report = None
    doc: dict[str, Any] = {}
    for rounds in range(1, max_rounds + 1):
        try:
            doc = _materialize_structured_claims(builder.doc(model_ref), model)
        except _TermGenerationUnavailable as error:
            if rounds == max_rounds:
                raise GeneratorError(f"{error}; attempts={max_rounds}") from error
            # Candidate generation is deterministic for a seed, but a failed
            # exact extension does not certify the asserted rows. Consume the
            # next draws and build a fresh candidate within the shared round
            # budget instead of aborting on the first undefined term.
            builder = _Builder(model, pool, rng, rows_per_fact_type)
            builder.construct()
            prev_fail_count = None
            continue
        try:
            population = _load_temp(doc, model)
        except PopulationValidationError as error:
            raise GeneratorError(
                f"assembled population failed re-admission (load_population): "
                f"{error} — a structurally-invalid population contributes zero "
                f"verdicts and must be loud (exit 5)."
            ) from error
        report = check(model, population)
        witnesses = _witness_map(model, doc, children)
        fails = _alethic_fails(report)

        # C1: a checker alethic fail whose independent witness HOLDS is a candidate
        # checker false-fail — never repaired, routed to quarantine.
        discrepancies = [
            {
                "constraint_ref": v.constraint_ref,
                "witness": "satisfied",
                "observed": v.verdict,
                "kind": "candidate-false-fail",
            }
            for v in fails
            if witnesses.get(v.constraint_ref) is True
        ]
        repairable = [v for v in fails if witnesses.get(v.constraint_ref) is not True]
        failed_refs = {v.constraint_ref for v in fails}
        false_passes = [
            ref for ref in alethic if witnesses.get(ref) is False and ref not in failed_refs
        ]
        discrepancies.extend(_false_pass_discrepancies(false_passes, report))
        if discrepancies:
            raise CheckerWitnessDiscrepancy(doc, discrepancies)

        if not fails:
            # Converged only when every ALETHIC constructive witness also holds.
            # A deontic witness that does not hold is a WARNING, not a fail, and
            # does not block a conforming population (convergence is defined on
            # alethic fail only).
            break
        if prev_fail_count is not None and len(fails) >= prev_fail_count:
            broken = [
                v.constraint_ref for v in repairable if witnesses.get(v.constraint_ref) is False
            ]
            raise GeneratorError(
                f"repair oscillated (no net reduction in alethic failures at round "
                f"{rounds}); unresolved: {broken or [v.constraint_ref for v in repairable]} "
                f"(not-derivable, distinct from budget exhaustion)."
            )
        prev_fail_count = len(fails)
        _repair(builder, repairable, model, children)
    else:
        # Budget exhausted.
        fails = _alethic_fails(report) if report is not None else []
        witnesses = _witness_map(model, doc, children)
        discrepancies = [
            {
                "constraint_ref": v.constraint_ref,
                "witness": "satisfied",
                "observed": v.verdict,
                "kind": "candidate-false-fail",
            }
            for v in fails
            if witnesses.get(v.constraint_ref) is True
        ]
        if discrepancies:
            raise CheckerWitnessDiscrepancy(doc, discrepancies)
        raise GeneratorError(
            f"did not converge within {max_rounds} rounds; unresolved alethic "
            f"fails: {[v.constraint_ref for v in fails]} (not-derivable)."
        )

    # Final gate: optional test fault, then witnesses, then non-degeneracy.
    if fault is not None:
        fault(doc)
        population = _load_temp(doc, model)
        report = check(model, population)
        witnesses = _witness_map(model, doc, children)
        broken = [ref for ref, ok in witnesses.items() if ok is False and ref in alethic]
        if broken:
            # The twin of the convergence branch above, and it splits the same
            # way (CR-04). A broken witness the checker ALSO fails is a genuine
            # generator failure — the fault worked as designed — and stays exit 5.
            # A broken witness the checker waved through is a candidate false
            # pass, and is retained under quarantine at exit 6 like every other
            # checker/witness disagreement.
            failed = {v.constraint_ref for v in _alethic_fails(report)}
            undetected = [ref for ref in broken if ref not in failed]
            if undetected:
                raise CheckerWitnessDiscrepancy(doc, _false_pass_discrepancies(undetected, report))
            raise GeneratorError(
                f"alethic constructive witness does not hold for {broken} at "
                f"final verification (injected fault), and the checker agrees — "
                f"a generator failure, exit 5."
            )

    assert_non_degenerate(model, population)
    expectations = _build_expectations(model, doc, children)
    ratios = measure_distinct_ratios(model, doc)
    return Assembly(
        doc=doc,
        model=model,
        pool=pool,
        seed=seed,
        pool_size=pool_size,
        rounds=rounds,
        expectations=expectations,
        distinct_ratios=ratios,
        witnesses=_witness_map(model, doc, children),
    )


def _materialize_structured_claims(doc: dict[str, Any], model: Model) -> dict[str, Any]:
    """Evaluate complete structured extensions over an asserted candidate."""
    structured = {
        str(fact_type.get("id"))
        for fact_type in model.fact_types
        if isinstance(fact_type.get("derivation_rule"), dict)
    }
    if not structured:
        return doc
    asserted = {
        **doc,
        "facts": {
            fact_type: rows
            for fact_type, rows in doc.get("facts", {}).items()
            if fact_type not in structured
        },
    }
    population = _load_temp(asserted, model)
    view = structured_extension_view(model, population)
    if view.unavailable:
        first = next(iter(view.unavailable.values()))
        raise _TermGenerationUnavailable(
            "term-generation-did-not-converge: structured relation "
            f"'{first.relation}' is unavailable because {first.reason}; "
            f"binding={dict(first.binding)!r}"
        )
    materialized = _rf7_input.loads(json.dumps(asserted))
    for fact_type in structured:
        rows = view.facts.get(fact_type, ())
        if rows:
            materialized["facts"][fact_type] = [dict(row) for row in rows]
    return materialized


# --------------------------------------------------------------------------- #
# repair operations — the checker as a SEARCH HEURISTIC only (C1)
# --------------------------------------------------------------------------- #


def _repair(
    builder: _Builder, fails: list[Any], model: Model, children: dict[str, set[str]]
) -> None:
    """Apply a family-specific repair for each alethic fail whose witness fails.

    The checker told us WHICH constraint is unsatisfied (search heuristic); the
    repair re-establishes it constructively.
    """
    by_ref = {ref: (c, ft) for ref, c, ft in _constraint_iter_with_ref(model)}
    for verdict in fails:
        entry = by_ref.get(verdict.constraint_ref)
        if entry is None:
            continue
        constraint, ft = entry
        ctype = str(constraint.get("type"))
        if ctype == "uniqueness":
            _repair_uniqueness(builder, constraint, ft, model)
        elif ctype == "mandatory":
            builder._close_mandatory()
        elif ctype == "mandatory-disjunctive":
            _repair_disjunctive(builder, constraint, model, children)
        elif ctype == "frequency":
            _repair_frequency(builder, constraint, ft, model)
        elif ctype == "cardinality":
            _repair_cardinality(builder, constraint)
        elif ctype == "ring":
            builder._generate_ring(ft)
        elif ctype == "value":
            _repair_value(builder, constraint, ft)
        elif ctype in ("subset", "equality"):
            builder._coordinate_set_families()
        elif ctype == "exclusion":
            builder._coordinate_exclusion(constraint)
        elif ctype == "exclusive-or":
            builder._coordinate_exclusive_or(constraint)
        elif ctype == "guarded":
            _seed_guarded_exists(builder, model, only_ref=verdict.constraint_ref)
    # A uniqueness repair may delete the only row for a mandatory subject.
    # Close that hole in the same repair transaction so the outer progress
    # guard never mistakes a changed failure for an oscillation.
    builder._close_mandatory()
    builder._coordinate_external_uniqueness()


def _seed_guarded_exists(
    builder: _Builder, model: Model, *, only_ref: str | None = None
) -> None:
    """Construct exactly one defined modular witness per antecedent binding
    for Phase 6's deliberately narrow two-atom synth shape.

    This is a constructive baseline helper, not a general guarded repair
    engine. Shared relations, additional constraints, unsupported where terms,
    and non-modular guarded forms remain not-derivable.
    """
    for index, constraint in enumerate(model.constraints or []):
        ref = positional_constraint_ref(None, index)
        if only_ref is not None and ref != only_ref:
            continue
        if constraint.get("type") != "guarded":
            continue
        if not _has_private_exists_sources(model, constraint):
            continue
        plan = _exists_modular_repair_plan(constraint)
        if plan is None:
            continue
        atoms = plan["atoms"]
        facts = builder.facts
        antecedents = _exists_antecedent_bindings(constraint, facts)
        if not antecedents:
            continue
        relation_ids = list(dict.fromkeys(str(atom["fact_type"]) for atom in atoms))
        for fact_type_id in relation_ids:
            facts[fact_type_id] = []

        type_by_id = {str(ft.get("id")): ft for ft in model.fact_types or []}
        divisor = plan["divisor"]
        for antecedent in antecedents:
            source = antecedent.get(plan["antecedent_variable"])
            if not isinstance(source, int) or isinstance(source, bool):
                raise GeneratorError(
                    f"{ref}: modular exists synthesis requires an Integer antecedent operand"
                )
            values = dict(antecedent)
            values[plan["candidate_variable"]] = source % divisor
            values[plan["candidate_divisor"]] = divisor
            for atom in atoms:
                fact_type_id = str(atom["fact_type"])
                fact_type = type_by_id[fact_type_id]
                role_types = {
                    str(role.get("role_name")): str(role.get("object_type"))
                    for role in fact_type.get("roles") or []
                }
                row: dict[str, Any] = {}
                for role, raw_variable in atom["bind"].items():
                    variable = str(raw_variable)[1:]
                    if variable not in values:
                        values[variable] = builder._draw_value(
                            fact_type_id, str(role), role_types[str(role)]
                        )
                    row[str(role)] = values[variable]
                facts.setdefault(fact_type_id, []).append(row)


def _repair_uniqueness(builder: _Builder, constraint: dict[str, Any], ft, model: Model) -> None:
    if constraint.get("scope") == "external":
        builder._coordinate_external_uniqueness()
        return
    ftid = str(ft.get("id"))
    roles = [str(r) for r in constraint.get("roles") or []]
    seen: set[tuple] = set()
    kept: list[dict[str, Any]] = []
    for fact in builder.facts.get(ftid, []):
        if any(r not in fact for r in roles):
            kept.append(fact)
            continue
        key = _tuple_key(tuple(fact[r] for r in roles))
        if key in seen:
            continue
        seen.add(key)
        kept.append(fact)
    builder.facts[ftid] = kept


def _repair_frequency(builder: _Builder, constraint: dict[str, Any], ft, model: Model) -> None:
    if constraint.get("scope") == "external" or ft is None:
        return
    ftid = str(ft.get("id"))
    roles = [str(r) for r in constraint.get("roles") or []]
    bound = constraint.get("bound") or {}
    maximum = bound.get("max")
    if maximum is None:
        return
    groups: dict[tuple, int] = {}
    kept: list[dict[str, Any]] = []
    for fact in builder.facts.get(ftid, []):
        if any(r not in fact for r in roles):
            kept.append(fact)
            continue
        key = _tuple_key(tuple(fact[r] for r in roles))
        if groups.get(key, 0) >= maximum:
            continue
        groups[key] = groups.get(key, 0) + 1
        kept.append(fact)
    builder.facts[ftid] = kept


def _repair_cardinality(builder: _Builder, constraint: dict[str, Any]) -> None:
    bound = constraint.get("bound") or {}
    maximum = bound.get("max")
    if constraint.get("scope") != "role" or maximum is None:
        return
    role_ref = constraint.get("role_ref") or {}
    ftid = str(role_ref.get("fact_type"))
    role_name = str(role_ref.get("role"))
    seen: set[tuple[str, Any]] = set()
    kept: list[dict[str, Any]] = []
    for fact in builder.facts.get(ftid, []):
        if role_name not in fact:
            kept.append(fact)
            continue
        key = _key(fact[role_name])
        if key not in seen and len(seen) >= maximum:
            continue
        seen.add(key)
        kept.append(fact)
    builder.facts[ftid] = kept


def _repair_value(builder: _Builder, constraint: dict[str, Any], ft) -> None:
    role_ref = constraint.get("role_ref")
    if role_ref is None:
        return
    ftid = str(role_ref.get("fact_type"))
    role_name = str(role_ref.get("role"))
    rng = constraint.get("range")
    allowed = constraint.get("allowed")
    oid = builder.role_obj.get(ftid, {}).get(role_name)
    primitive = popvalidate.resolve_primitive(str(constraint.get("object_type")), builder.model)
    for fact in builder.facts.get(ftid, []):
        if role_name not in fact:
            continue
        value = fact[role_name]
        # `is False` deliberately, not `not …`: since F-2 `_in_range` has a third
        # answer, and `not None` is `True` — which would redraw exactly the values
        # no comparison could judge. Repair acts on a DECIDED violation only; a
        # value the oracle cannot order is left where it is, and the checker's
        # `unchecked` is the honest outcome for it.
        allowed_keys = {_key(member) for member in allowed or []}
        bad = (allowed is not None and _key(value) not in allowed_keys) or (
            rng is not None and _in_range(value, rng, primitive) is False
        )
        if bad and oid is not None:
            fact[role_name] = builder._draw_value(ftid, role_name, oid)


def _repair_disjunctive(
    builder: _Builder, constraint: dict[str, Any], model: Model, children
) -> None:
    refs = list(constraint.get("role_refs") or [])
    if not refs:
        return
    oids = {builder.role_obj.get(str(r.get("fact_type")), {}).get(str(r.get("role"))) for r in refs}
    if len(oids) != 1 or None in oids:
        return
    oid = next(iter(oids))
    doc = {"facts": builder.facts, "instances": {}}
    played: set[tuple[str, Any]] = set()
    for r in refs:
        for (v,) in _project(doc, str(r.get("fact_type")), [str(r.get("role"))]):
            played.add(_key(v))
    target = refs[0]
    tfid, trole = str(target.get("fact_type")), str(target.get("role"))
    tft = next((f for f in model.fact_types if str(f.get("id")) == tfid), None)
    if tft is None:
        return
    for value in _universe(doc, model, str(oid), children):
        if _key(value) in played:
            continue
        played.add(_key(value))
        builder.facts.setdefault(tfid, []).append(builder._complete_fact(tft, {trole: value}))








































