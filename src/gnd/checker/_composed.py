"""CT2 composed-anchor checking (composition-and-type-induction milestone).

A separate home inside the ``gnd.checker`` package so ``_core`` stays under its
RF6 size ceiling; ``gnd.checker`` re-exports the function. The dispatch and
the per-source anchor evaluation are looked up on ``_core`` at call time, so a
patch of the defining home still takes effect here.
"""
from __future__ import annotations

from typing import Any

import gnd.checker._core as _core_home
from gnd.address import positional_constraint_ref
from gnd.checker._reports import CheckReport, ConstraintVerdict
from gnd.documents import Model
from gnd.model_index import ModelIndex
from gnd.population import Population


def check_with_composed_anchors(
    model: Model,
    population: Population,
    *,
    sources: Any,
    lineage: dict[Any, Any],
) -> CheckReport:
    """Check a composed population, each anchored value against its own source (CT2).

    Every source is evaluated once by ``_anchored_verdicts`` over its own
    population, sidecar and document, so a value is matched before renaming
    against the span its own sidecar names. A composed fact fails when any of
    its lineage source facts fails.
    """
    report = _core_home._check_dispatch(model, population)
    per_source = {
        source.id: _core_home._anchored_verdicts(model, source.population, source.sidecar, source.document_bytes)
        for source in sources
    }
    order = [source.id for source in sources]
    replacements = {}
    obligations = [
        (declared, position, item)
        for declared in ModelIndex.for_model(model).iter_fact_types_shared()
        for position, item in enumerate(declared.get("constraints") or [])
        if item.get("type") == "anchored"
    ]
    for fact_type, index, constraint in obligations:
        fact_id = str(fact_type["id"])
        reference = positional_constraint_ref(fact_id, index)
        variant = "role" if constraint.get("role") is not None else "all"
        failing = {
            (source_id, fact_id, ref["index"])
            for source_id, verdicts in per_source.items()
            if reference in verdicts and verdicts[reference].verdict in {"fail", "warning"}
            for ref in verdicts[reference].fact_refs
        }
        rows = population.facts.get(fact_id, [])
        # A row with no lineage has no source to bind it, so it fails.
        failed_refs = [
            row_index for row_index in range(len(rows))
            if not lineage.get((fact_id, row_index))
            or any((entry["source"], entry["fact_type"], entry["fact_index"]) in failing
                   for entry in lineage.get((fact_id, row_index), ()))
        ]
        unchecked = next((
            per_source[source_id][reference] for source_id in order
            if reference in per_source[source_id] and per_source[source_id][reference].verdict == "unchecked"
        ), None)
        if failed_refs:
            verdict = "warning" if constraint.get("modality") == "deontic" else "fail"
            scope = f"snapshot:anchored:{variant}:violated:{constraint.get('modality', 'alethic')}"
            reason = None
        elif unchecked is not None:
            verdict, scope, reason = "unchecked", unchecked.scope_id, unchecked.reason_code
        elif not rows:
            verdict, scope, reason = "vacuous", f"snapshot:anchored:{variant}:vacuous", None
        else:
            verdict, scope, reason = "pass", f"snapshot:anchored:{variant}:clean", None
        replacements[reference] = ConstraintVerdict(
            scope_id=scope, constraint_ref=reference, constraint_type="anchored",
            modality=str(constraint.get("modality", "alethic")),
            source=str(constraint["source"]), status=str(constraint["status"]),
            verdict=verdict, reason_code=reason,
            message=f"Source anchor {verdict} for {fact_id}.",
            offending_facts=[{"fact_type": fact_id, "roles": rows[row_index]} for row_index in failed_refs],
            fact_refs=[{"fact_type": fact_id, "index": row_index} for row_index in failed_refs],
        )
    if not replacements:
        return report
    return report.model_copy(update={
        "verdicts": [replacements.get(row.constraint_ref, row) for row in report.verdicts],
        "snapshot_projection": None,
        "admission_projection": report.snapshot_projection,
    })
