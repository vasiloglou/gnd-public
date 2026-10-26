"""The aggregate measurement payload and its text rendering (VER-03, D-22).

``build_measurement_report`` folds a corpus of labelled populations into ONE
payload carrying, per constraint: the three published rates (each beside its
numerator and its conditional denominator — C2), the two selective rates, all
six partition counters, the D-12 provenance join (``source`` / ``status`` read
off the constraint the ref names), and a verbatim raw-evidence excerpt (D-22) —
an actual ``ConstraintVerdict`` from a named contributing population, so no
published number exists without a raw artifact a reader can open.

**Per-``(model, pool_source)`` (C4).** ``gnd measure`` is model-relative — it
loads every population against ONE model — so a single payload cannot span four
models. ``build_measurement_report`` refuses a corpus whose sidecars disagree on
``model_digest`` or ``pool_source``; the CLI maps that refusal to exit 64.

**No timestamp, byte-reproducible (owner's publication-pinning rule).** The
payload carries ``corpus[]`` with a sha256 per population and sidecar and NO
``generated_at`` — a timestamp is the one field that would break the
byte-for-byte re-measure the pinning rule promises, and ``report.schema.json``
already sets the no-timestamp precedent. Lists are emitted in a canonical
sorted order for the same reason.

**No aggregate accuracy (D-01).** There is deliberately no blended accuracy
number anywhere in the payload — a reviewer must be able to confirm its absence
by reading the schema, not by auditing the code. ``coverage_summary`` carries
counts, never a score.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.resources import files
from typing import Any

from gnd import input_policy as _rf7_input
from gnd import verbalize
from gnd.address import positional_constraint_ref
from gnd.checker import CheckReport
from gnd.measure.score import Observation, score_run
from gnd.measure.truth import expectation_for, resolve_constraint_ref
from gnd.model import Model
from gnd.model_identity import stable_model_identifier
from gnd.synth.provenance import Sidecar

__all__ = [
    "MEASUREMENT_SCHEMA_VERSION",
    "MeasuredPopulation",
    "MixedCorpusError",
    "build_labelled_report",
    "build_measurement_report",
    "load_measurement_schema",
    "render_measurement",
    "stable_model_identifier",
]

#: Measurement payload key-set version. Bump ONLY on a breaking change to the key
#: set or a value's meaning, matching ``report.py``'s ``PAYLOAD_SCHEMA_VERSION``
#: precedent.
#: /2: ``manifest`` (the ``index.json`` path and digest) became a required key —
#: WR-02/IN-02. The index decides which populations are measured and feeds three
#: published counters, so leaving it outside the pinning trail meant two payloads
#: could differ on those counters with identical corpus digests.
MEASUREMENT_SCHEMA_VERSION = 2

#: The six partition counters, in canonical order — mirrors score.OUTCOMES.
_CELL_KEYS = (
    "correct",
    "false_pass",
    "false_fail",
    "undecided",
    "masked_by_vacuity",
    "tool_defect",
)


class MixedCorpusError(ValueError):
    """The corpus mixes models or pool sources (C4). ``gnd measure`` is
    model-relative and one payload represents exactly one ``(model,
    pool_source)`` pair; a mixed corpus is a usage error (the CLI exits 64),
    never a silently-measured subset."""


@dataclass(frozen=True)
class MeasuredPopulation:
    """One scored population: its paths and hashes, the sidecar that labels it,
    and the checker's report over it. The CLI builds these after verifying the
    C6 sidecar binding; this module only reads them.

    ``population_path`` and ``sidecar_path`` are **corpus-root-relative POSIX
    strings**, never absolute and never CWD-relative (F-05). Every path the
    payload publishes comes from these two, so the payload — and therefore its
    sha256 — is a function of the corpus and not of how the corpus happened to
    be named on the command line. They are identifiers here, not file handles:
    nothing downstream of the CLI reopens them.
    """

    population_path: str
    population_sha256: str
    sidecar_path: str
    sidecar_sha256: str
    sidecar: Sidecar
    report: CheckReport


def load_measurement_schema() -> dict[str, Any]:
    """The Draft 2020-12 schema describing this payload, resolved through
    ``importlib.resources`` so it ships with the installed package (the
    ``report.schema.json`` / ``pool.schema.json`` precedent)."""
    schema_text = files("gnd").joinpath("measurement.schema.json").read_text(encoding="utf-8")
    return _rf7_input.loads(schema_text)


def _canonical(payload: dict[str, Any]) -> str:
    """The payload as canonical JSON: sorted keys, no NaN, stable separators.

    ``sort_keys`` fixes every object's key order; every list in the payload is
    pre-sorted by its builder, so two runs over one corpus are byte-identical.
    """
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False)


# `stable_model_identifier` moved to `gnd.model_identity` in v5.1 Phase 1
# (D-P1.3): fidelity carried a second copy anchored on a different root. It is
# re-exported above so existing imports keep working; the rule itself, and the
# reasoning for the invocation root, live in that module and nowhere else.


def _verdict_excerpt(report: CheckReport, ref: str) -> dict[str, Any] | None:
    for verdict in report.verdicts:
        if verdict.constraint_ref == ref:
            return {
                "constraint_ref": verdict.constraint_ref,
                "verdict": verdict.verdict,
                "message": verdict.message,
                "reason_code": verdict.reason_code,
                "offending_facts": verdict.offending_facts,
            }
    return None


def _select_evidence(
    ref: str,
    outcome_by_population: list[tuple[MeasuredPopulation, str, str, Any]],
) -> dict[str, Any] | None:
    """D-22: the verbatim excerpt for one row.

    Deterministic: the first contributing population in corpus order, PREFERRING
    an error-counting cell (``false_pass`` / ``false_fail`` / ``tool_defect`` /
    ``masked_by_vacuity``) over a ``correct`` one, so the excerpt shows the most
    load-bearing observation — the direction of the D-22 trap is that a
    bad-looking number is the one nobody audits.
    """
    error_cells = {"false_pass", "false_fail", "tool_defect", "masked_by_vacuity"}
    ordered = sorted(outcome_by_population, key=lambda item: item[0].population_path)
    preferred = next((mp for mp, outcome, _, _e in ordered if outcome in error_cells), None)
    chosen = preferred or (ordered[0][0] if ordered else None)
    if chosen is None:
        return None
    excerpt = _verdict_excerpt(chosen.report, ref)
    if excerpt is None:
        return None
    return {"population": chosen.population_path, "verdict": excerpt}


def _assert_every_declared_constraint_was_scored(
    model: Model, observations_by_ref: dict[str, list[Observation]]
) -> None:
    """Reconcile the scored row set against the constraints the model DECLARES (WR-01).

    Observations are collected by walking ``report.verdicts``, so a constraint
    the checker emits no verdict for produces no row and leaves the measurement
    with no signal at all — and nothing downstream can see the omission. The
    partition invariant cannot: it guards ``sum(cells) == n`` WITHIN a row, and a
    missing constraint has no row. The applicability matrix cannot either: it is
    computed from sidecars, not from verdicts. Dropping every verdict whose ref
    ended ``constraints[0]`` took 12 constraints and 1,920 observations out of a
    committed run while ``coverage_fraction`` still read 1.0 and the run exited 0.

    This is the same leak class the module docstrings are written against, one
    level up, so it is raised in production code rather than tested for.
    """
    from gnd.measure.score import PartitionError
    from gnd.synth.assemble import _constraint_iter_with_ref

    declared = {ref for ref, _constraint, _ft in _constraint_iter_with_ref(model)}
    unscored = sorted(declared - set(observations_by_ref))
    if unscored:
        raise PartitionError(
            f"{unscored} are declared in the model but produced no verdict on any "
            f"population in this corpus — those constraints left every rate "
            f"silently, and a coverage fraction computed from sidecars cannot see "
            f"the omission."
        )


def build_measurement_report(
    model: Model,
    model_path: str,
    populations: list[MeasuredPopulation],
    *,
    gnd_version: str,
    index: dict[str, Any] | None = None,
    index_sha256: str | None = None,
) -> dict[str, Any]:
    """Assemble the aggregate measurement payload from scored populations.

    Refuses a mixed corpus (:class:`MixedCorpusError`, C4). Emits no timestamp
    and canonical, sorted lists so two runs over one corpus reproduce
    byte-for-byte.
    """
    if not populations:
        raise MixedCorpusError(
            "no populations to measure — an empty corpus produces no rates. Point "
            "--populations at a directory with an index.json."
        )

    model_digests = {mp.sidecar.model_digest for mp in populations}
    pool_sources = {mp.sidecar.pool_source for mp in populations}
    # WR-02: `pool_source` is a LABEL ("faker", "llm-proposed"), so checking it
    # alone lets a payload span two distinct pools while reading as one — which
    # `_merge_index` makes easy, since it unions entries across invocations and a
    # second `gnd synth --seed M` leaves both pools in the corpus. The DIGEST is
    # the identity.
    pool_digests = {mp.sidecar.pool_sha256 for mp in populations}
    if len(model_digests) != 1 or len(pool_sources) != 1 or len(pool_digests) != 1:
        raise MixedCorpusError(
            f"the corpus spans {len(model_digests)} model digest(s), "
            f"{len(pool_sources)} pool source(s) and {len(pool_digests)} pool "
            f"digest(s); gnd measure is model-relative and one payload represents "
            f"exactly one (model, pool) pair (C4). Split the corpus and measure "
            f"each pair separately."
        )
    (pool_source,) = pool_sources

    scored = _score_rows(
        model, populations, lambda mp, ref: expectation_for(mp.sidecar, ref)
    )
    per_constraint = scored.per_constraint
    checker_defects = scored.checker_defects
    total_observations = scored.observations
    decided_observations = scored.decided
    total_wrong_attribution = scored.wrong_attribution

    violating_sidecars = [mp for mp in populations if mp.sidecar.class_ == "violating"]
    isolating_cases = sum(1 for mp in violating_sidecars if mp.sidecar.isolating is True)
    set_attributed_cases = sum(1 for mp in violating_sidecars if mp.sidecar.isolating is False)

    corpus = sorted(
        (
            {
                "path": mp.population_path,
                "sha256": mp.population_sha256,
                "sidecar_path": mp.sidecar_path,
                "sidecar_sha256": mp.sidecar_sha256,
            }
            for mp in populations
        ),
        key=lambda entry: entry["path"],
    )

    pools = sorted(
        {(mp.sidecar.pool_source, mp.sidecar.pool_sha256) for mp in populations},
    )
    pools_records = [{"source": source, "sha256": sha} for source, sha in pools]

    seeds = sorted({mp.sidecar.seed for mp in populations})
    generator_versions = sorted({mp.sidecar.generator_version for mp in populations})

    coverage_summary = {
        "constraint_count": len(per_constraint),
        "population_count": len(populations),
        "observation_count": total_observations,
        "decided_observations": decided_observations,
        "wrong_attribution": total_wrong_attribution,
        "isolating_cases": isolating_cases,
        "set_attributed_cases": set_attributed_cases,
        **_coverage_matrix_summary(model, populations, index),
    }
    exact_terms = any(
        "aggregate" in rule
        or any(
            isinstance(value, dict) and set(value) == {"fn", "args"}
            for value in [
                *(rule.get("head") or {}).values(),
                *(
                    operand
                    for comparison in rule.get("where") or []
                    for operand in (comparison.get("left"), comparison.get("right"))
                ),
            ]
        )
        for fact_type in model.fact_types
        for rule in [fact_type.get("derivation_rule")]
        if isinstance(rule, dict)
    )
    if exact_terms:
        coverage_summary.setdefault("unmutated_derivations", [])

    return {
        "schema_version": 3 if exact_terms else MEASUREMENT_SCHEMA_VERSION,
        "tool": "gnd",
        "command": "measure",
        "gnd_version": gnd_version,
        "generator_version": generator_versions[0] if len(generator_versions) == 1 else "mixed",
        "model": stable_model_identifier(model_path),
        "model_id": str(model.model_id) if model.model_id else None,
        "model_digest": next(iter(model_digests)),
        "pool_source": pool_source,
        "population_count": len(populations),
        "seeds": seeds,
        "pools": pools_records,
        # WR-02 / IN-02: `index.json` feeds `boundary_cases_derived`,
        # `boundary_not_derivable` and `operators_exercised`, and it decides WHICH
        # populations are measured at all — yet it appeared nowhere in `corpus[]`,
        # so two payloads could differ on those counters with identical corpus
        # digests and the byte-reproduction receipt covered none of it.
        "manifest": {"path": "index.json", "sha256": index_sha256},
        "corpus": corpus,
        "per_constraint": per_constraint,
        "coverage_summary": coverage_summary,
        "checker_defects": checker_defects,
        "lanes": {"deterministic": "run", "llm": "not-applicable-phase-2"},
    }


@dataclass(frozen=True)
class _ScoredRows:
    per_constraint: list[dict[str, Any]]
    checker_defects: list[dict[str, Any]]
    observations: int
    decided: int
    wrong_attribution: int


def _score_rows(
    model: Model, populations: list[Any], expectation_of: Any
) -> _ScoredRows:
    """The per-constraint rows and checker defects, shared by the synth path and
    IK3's expected-state labels path. ``expectation_of(population, ref)`` returns
    the :class:`ExpectedState` for one observation; a population whose
    ``sidecar`` is ``None`` (a host label) contributes no synth-only view."""
    # Collect observations per constraint ref, plus the per-population outcome so
    # the evidence excerpt can prefer an error-counting cell.
    from gnd.measure.score import classify

    observations_by_ref: dict[str, list[Observation]] = {}
    contributions: dict[str, list[tuple[MeasuredPopulation, str, str, Any]]] = {}
    ordered_pops = sorted(populations, key=lambda mp: mp.population_path)
    for mp in ordered_pops:
        for verdict in mp.report.verdicts:
            ref = verdict.constraint_ref
            expected = expectation_of(mp, ref)
            observation = Observation(expected, verdict.verdict, verdict.modality)
            outcome = classify(expected, verdict.verdict, verdict.modality)
            observations_by_ref.setdefault(ref, []).append(observation)
            contributions.setdefault(ref, []).append((mp, outcome, verdict.verdict, expected))

    _assert_every_declared_constraint_was_scored(model, observations_by_ref)

    # F-4: the census half of the same reconciliation. The check above is
    # set-based and sees a constraint that vanishes from EVERY population; this
    # sees one that vanishes from SOME, which leaves the row's rates intact over
    # half the evidence.
    scores = score_run(observations_by_ref, population_count=len(ordered_pops))

    per_constraint: list[dict[str, Any]] = []
    checker_defects: list[dict[str, Any]] = []
    decided_observations = 0
    total_observations = 0
    total_wrong_attribution = 0
    for ref in sorted(scores):
        score = scores[ref]
        constraint = resolve_constraint_ref(model, ref)
        # modality/type come from the constraint the ref names (D-12 join).
        modality = str(constraint.get("modality") or "")
        constraint_type = str(constraint.get("type") or "")
        evidence = _select_evidence(ref, contributions[ref])
        wrong_attribution = _wrong_attribution_count(ref, contributions[ref])
        total_wrong_attribution += wrong_attribution
        # Shared credit stays VISIBLE: a row whose evidence includes any
        # set-attributed violating case (isolating == False, this ref in the
        # predicted set) is marked, so a reader can see when per-constraint
        # credit is shared rather than clean (D-05').
        set_attributed_evidence = any(
            mp.sidecar is not None
            and mp.sidecar.class_ == "violating"
            and mp.sidecar.isolating is False
            and ref in (mp.sidecar.violates or [])
            for mp, _outcome, _observed, _expected in contributions[ref]
        )
        total_observations += score.n
        decided_observations += score.decided
        per_constraint.append(
            {
                "constraint_ref": ref,
                "constraint_type": constraint_type,
                "modality": modality,
                "source": constraint.get("source"),
                "status": constraint.get("status"),
                "n": score.n,
                "decided": score.decided,
                "coverage": score.coverage,
                "cells": dict(score.cells),
                "false_pass": score.cells["false_pass"],
                "expected_nonpass": score.expected_nonpass,
                "false_pass_rate": score.false_pass_rate,
                "false_fail": score.cells["false_fail"],
                "satisfied": score.satisfied,
                "false_fail_rate": score.false_fail_rate,
                "undecided_rate": score.undecided_rate,
                "selective_false_pass": score.selective_false_pass,
                "selective_false_fail": score.selective_false_fail,
                "ground_truth_states_seen": score.ground_truth_states_seen,
                "wrong_attribution": wrong_attribution,
                "set_attributed_evidence": set_attributed_evidence,
                "evidence": evidence,
            }
        )
        checker_defects.extend(_defects_for(ref, modality, contributions[ref]))

    checker_defects.sort(key=lambda d: (d["constraint_ref"], d["population"], d["kind"]))

    return _ScoredRows(
        per_constraint, checker_defects, total_observations, decided_observations,
        total_wrong_attribution,
    )


def build_labelled_report(
    model: Model,
    model_path: str,
    *,
    manifest_path: str,
    manifest_sha256: str,
    model_sha256: str,
    mode: str,
    populations: list[Any],
    work: dict[str, int],
    gnd_version: str,
    model_digest: str,
    rules: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """The IK3 labelled payload: schema 4 (expected-state) or 5 (class).

    Expected-state rows and defects come from :func:`_score_rows`, the synth
    path's own builder, so the two agree row for row (IK3-C2). The synth-only
    header (seeds, pools, generator version, sidecars) is replaced by the
    ``labels`` block (IK3-D2)."""
    corpus = []
    for population in populations:
        entry = {"id": population.id, "path": population.population_path,
                 "sha256": population.population_sha256}
        if population.class_ is not None:
            entry["class"] = population.class_
        corpus.append(entry)
    payload: dict[str, Any] = {
        "schema_version": 4 if mode == "expected-state" else 5,
        "tool": "gnd",
        "command": "measure",
        "gnd_version": gnd_version,
        "model": stable_model_identifier(model_path),
        "model_id": str(model.model_id) if model.model_id else None,
        "model_digest": model_digest,
        "population_count": len(populations),
        "labels": {
            "manifest": {"path": manifest_path, "sha256": manifest_sha256},
            "model_sha256": model_sha256,
            "mode": mode,
            "population_count": len(populations),
            "corpus": corpus,
            "work": dict(work),
        },
        "lanes": {"deterministic": "run", "llm": "not-applicable-phase-2"},
    }
    if mode == "class":
        payload["rules"] = list(rules or [])
        return payload
    scored = _score_rows(model, populations, lambda mp, ref: mp.expectations[ref])
    payload["per_constraint"] = scored.per_constraint
    payload["checker_defects"] = scored.checker_defects
    payload["coverage_summary"] = {
        "constraint_count": len(scored.per_constraint),
        "population_count": len(populations),
        "observation_count": scored.observations,
        "decided_observations": scored.decided,
        "wrong_attribution": scored.wrong_attribution,
    }
    return payload



def _coverage_matrix_summary(
    model: Model, populations: list[MeasuredPopulation], index: dict[str, Any] | None
) -> dict[str, Any]:
    """The C5 applicability matrix and every fraction derived from it.

    COVERAGE BEFORE RATES: a false-pass rate of 0.0 means one thing when the
    harness exercised every applicable cell and something entirely different when
    it exercised six families and quietly dropped the rest. Every numerator and
    denominator here is computed from the model document and the emitted
    sidecars — never a constant (A4).
    """
    from gnd.measure.coverage import (
        CASE_KINDS,
        applicability_matrix,
        coverage_fraction,
        families_in_model,
        observed_cells,
    )
    from gnd.synth.frontier import frontier_codes_for

    sidecars = [mp.sidecar for mp in populations]
    observed = observed_cells(sidecars, model)
    cells = applicability_matrix(model, observed)
    covered, applicable, fraction = coverage_fraction(cells)

    declared = families_in_model(model)
    frontier_codes = frontier_codes_for(model)
    families_covered = sorted({family for (family, _kind), count in observed.items() if count})
    kinds_present = sorted({kind for (_family, kind), count in observed.items() if count})

    # The band-4 frontier the undecided rate is measured OVER: which routes the
    # corpus actually pinned, and which the checker can emit but this model never
    # reaches. An unreached route is REPORTED, never dropped.
    measured_frontier = set(frontier_codes)
    exercised_codes = sorted(
        {
            verdict.reason_code
            for mp in populations
            for verdict in mp.report.verdicts
            if verdict.verdict == "unchecked"
            and verdict.reason_code in measured_frontier
        }
    )

    records = index or {}
    sidecar_bound = [
        sidecar
        for sidecar in sidecars
        if sidecar.schema_version in {"gnd-sidecar/4", "gnd-sidecar/5"}
    ]
    if sidecar_bound and len(sidecar_bound) == len(sidecars):
        unique_not_derivable = {
            json.dumps(record, sort_keys=True, separators=(",", ":"))
            for sidecar in sidecar_bound
            for record in sidecar.not_derivable or []
        }
        not_derivable = list(unique_not_derivable)
        unique_unmutated_derivations = {
            json.dumps(record, sort_keys=True, separators=(",", ":"))
            for sidecar in sidecar_bound
            if sidecar.schema_version == "gnd-sidecar/5"
            for record in sidecar.unmutated_derivations
        }
        unmutated_derivations = [
            _rf7_input.loads(record) for record in sorted(unique_unmutated_derivations)
        ]
        boundary_entries = [
            sidecar
            for sidecar in sidecar_bound
            if sidecar.case_kind in ("boundary", "no-subjects", "unchecked")
        ]
        operators_exercised = sorted(
            {sidecar.operator for sidecar in sidecar_bound if sidecar.operator}
        )
    else:
        # Backward-compatible read of v1-v3 corpora. New coverage claims are
        # always derived from the bound v4 sidecar fields above.
        not_derivable = list(records.get("not_derivable") or [])
        unmutated_derivations = list(records.get("unmutated_derivations") or [])
        boundary_entries = [
            entry
            for entry in (records.get("populations") or [])
            if entry.get("case_kind") in ("boundary", "no-subjects", "unchecked")
        ]
        operators_exercised = sorted(
            {
                entry["operator"]
                for entry in (records.get("populations") or [])
                if entry.get("operator")
            }
        )

    exists_refs = {
        positional_constraint_ref(None, index)
        for index, constraint in enumerate(model.constraints or [])
        if constraint.get("type") == "guarded"
        and isinstance(constraint.get("consequent"), dict)
        and isinstance(constraint["consequent"].get("exists"), dict)
    }
    unsupported_exists_rules_by_key: dict[str, dict[str, Any]] = {}
    for raw_record in not_derivable:
        record = _rf7_input.loads(raw_record) if isinstance(raw_record, str) else raw_record
        if not isinstance(record, dict) or record.get("constraint_ref") not in exists_refs:
            continue
        detail = {
            "constraint_ref": record["constraint_ref"],
            "family": record.get("family", "guarded"),
            "operator": record.get("operator"),
            "mechanism": str(record.get("mechanism", "unsupported guarded-exists form")),
        }
        key = json.dumps(detail, sort_keys=True, separators=(",", ":"))
        unsupported_exists_rules_by_key[key] = detail
    unsupported_exists_rules = [
        unsupported_exists_rules_by_key[key] for key in sorted(unsupported_exists_rules_by_key)
    ]

    return {
        "case_kinds": list(CASE_KINDS),
        "families_in_model": declared,
        "families_covered": families_covered,
        "case_kinds_present": kinds_present,
        "applicability_matrix": [cell.as_record() for cell in cells],
        "applicable_cells": applicable,
        "covered_applicable_cells": covered,
        "not_applicable_cells": sum(1 for c in cells if c.status == "not-applicable"),
        "missing_cells": sum(1 for c in cells if c.status == "missing"),
        "coverage_fraction": fraction,
        "band4_reason_codes": list(frontier_codes),
        "band4_reason_codes_exercised": exercised_codes,
        "boundary_cases_derived": len(boundary_entries),
        "boundary_not_derivable": len(not_derivable),
        **({"unmutated_derivations": unmutated_derivations} if unmutated_derivations else {}),
        **({"unsupported_exists_rules": unsupported_exists_rules} if unsupported_exists_rules else {}),
        "operators_exercised": operators_exercised,
    }


def _is_wrong_attribution(mp: MeasuredPopulation, outcome: str, expected: Any) -> bool:
    """D-21: detection credit for failing the WRONG constraint, pinned at 0.

    A ``fail``/``warning`` on a constraint whose sidecar ground truth is
    ``satisfied``, INSIDE a violating population, is a scoring failure, not a
    detection — without this pin a checker that fails constraints at random
    scores as a detector (text2lean pins the same property as
    ``wrong_detector_kills: Literal[0]``). It is a NAMED VIEW over the existing
    ``false_fail`` cells restricted to violating populations — never a seventh
    outcome, so plan 04's six-way partition invariant stands untouched; the
    observation lands in ``false_fail`` for the partition AND is counted a
    second time here under its own name.

    This looks redundant with generation-time verification (plan 05 task 2's
    predicted-set assertion makes it impossible for freshly emitted cases with
    the current checker) — it is NOT. The pin matters for exactly the runs
    where generation-time checking is absent: a COMMITTED corpus re-measured
    after a checker change, and the negative control. Do not delete it as dead.
    """
    return (
        mp.sidecar is not None
        and mp.sidecar.class_ == "violating"
        and outcome == "false_fail"
        and expected is not None
        and expected.ground_truth == "satisfied"
    )


def _wrong_attribution_count(
    ref: str, contributions: list[tuple[MeasuredPopulation, str, str, Any]]
) -> int:
    return sum(
        1
        for mp, outcome, _observed, expected in contributions
        if _is_wrong_attribution(mp, outcome, expected)
    )


def _defects_for(
    ref: str,
    modality: str,
    contributions: list[tuple[MeasuredPopulation, str, str, Any]],
) -> list[dict[str, Any]]:
    """checker_defects[] is direction-agnostic (C9, D-01) — four kinds.

    A deterministic checker error is a defect regardless of direction. Exit 6
    fires for an alethic false PASS, an alethic false FAIL, an impossible
    ``tool_defect`` cell, and a D-21 ``wrong_attribution`` — each promoted to a
    defect record with a ``kind`` discriminator so plan 05/06 can regenerate it.
    Deontic false passes/fails are measurement signal, not a checker defect (a
    deontic warning is feedback-only), so only alethic false-direction cells and
    tool defects are promoted — EXCEPT ``wrong_attribution`` (either modality):
    crediting the wrong constraint corrupts attribution whatever the modality,
    and by D-21 it is a scoring failure at any count. An alethic wrong
    attribution therefore produces TWO records for one observation — its
    ``false-fail`` and its ``wrong_attribution`` name — deliberately: the first
    is the partition's cell, the second the D-21 view.
    """
    defect_kinds = {
        "false_pass": "false-pass",
        "false_fail": "false-fail",
        "tool_defect": "tool-defect",
    }
    out: list[dict[str, Any]] = []
    for mp, outcome, observed, expected in contributions:
        if expected is None and mp.sidecar is not None:
            expected = mp.sidecar.expectations.get(ref)

        def record(kind: str, mp=mp, observed=observed, expected=expected) -> dict[str, Any]:
            row = {
                "kind": kind,
                "constraint_ref": ref,
                "modality": modality,
                "population": mp.population_path,
                "sidecar": mp.sidecar_path,
                "expected_verdict": expected.expected_verdict if expected else None,
                "observed_verdict": observed,
                "seed": mp.sidecar.seed if mp.sidecar is not None else None,
            }
            # IK3 C-F1: a host-labelled population has neither field.
            if mp.sidecar is None:
                del row["sidecar"], row["seed"]
            return row

        if _is_wrong_attribution(mp, outcome, expected):
            out.append(record("wrong_attribution"))
        if outcome not in defect_kinds:
            continue
        # Deontic false passes/fails are signal, not a checker defect; a tool
        # defect is a defect for either modality.
        if outcome in ("false_pass", "false_fail") and modality != "alethic":
            continue
        out.append(record(defect_kinds[outcome]))
    return out


def _fmt_rate(value: float | None, numerator: int, denominator: int) -> str:
    if value is None:
        return f"None ({numerator}/{denominator})"
    return f"{value:.4f} ({numerator}/{denominator})"


def render_measurement(payload: dict[str, Any]) -> str:
    """The text rendering: coverage before rates, ``n`` beside every rate.

    Every model-derived identifier is routed through ``verbalize.path_segment`` /
    ``verbalize.line_text`` — a fact-type key carrying a newline forged tool
    output once already (CR-05), and the report renderer is a new surface for the
    same defect.
    """
    lines: list[str] = []
    if "redaction" in payload:
        from gnd.redaction import render_text_header

        header = render_text_header(payload)
        if header is None:
            raise ValueError("measurement successor lacks redaction metadata")
        lines.append(header)
    source = (
        f"labels={payload['labels']['mode']}" if "labels" in payload
        else f"pool={verbalize.path_segment(payload['pool_source'])}"
    )
    lines.append(
        f"MEASUREMENT {verbalize.path_segment(payload['model'])} "
        f"[{source}] "
        f"populations={payload['population_count']}"
    )
    if "rules" in payload:
        work = payload["labels"]["work"]
        lines.append(f"WORK {work['total']} (ceiling {work['ceiling']})")
        for row in payload["rules"]:
            lines.append(
                f"  {verbalize.path_segment(row['ref'])} "
                f"[{verbalize.path_segment(row['constraint_type'])}/"
                f"{verbalize.path_segment(row['modality'])}] fires_on={row['fires_on']}"
            )
            lines.append(
                "      "
                + " ".join(
                    f"{key}={cell['numerator']}/{cell['denominator']}"
                    for key, cell in row["cells"].items()
                )
            )
        return "\n".join(lines)
    # COVERAGE BEFORE RATES: a rate over six families is not the same object as a
    # rate over fourteen, so the reader sees the denominator of the measurement
    # before any of its numbers.
    summary = payload["coverage_summary"]
    if "coverage_fraction" in summary:
        fraction = summary["coverage_fraction"]
        rendered = "None" if fraction is None else f"{fraction:.4f}"
        lines.append(
            f"COVERAGE {rendered} "
            f"({summary['covered_applicable_cells']}/{summary['applicable_cells']} applicable "
            f"(family, case_kind) cells; {summary['not_applicable_cells']} not-applicable, "
            f"{summary['missing_cells']} missing)"
        )
        for row in summary.get("unmutated_derivations", []):
            lines.append(
                "  UNMUTATED "
                f"{verbalize.path_segment(row['derivation_ref'])}: "
                f"{verbalize.line_text(row['reason'])}"
            )
        for row in summary.get("unsupported_exists_rules", []):
            operator = row["operator"] or "no operator"
            lines.append(
                "  NOT-DERIVABLE "
                f"{verbalize.path_segment(row['constraint_ref'])} "
                f"({verbalize.path_segment(operator)}): "
                f"{verbalize.line_text(row['mechanism'])}"
            )
        lines.append(
            f"  families {len(summary['families_covered'])}/{len(summary['families_in_model'])}"
            f" · case kinds present: {', '.join(summary['case_kinds_present']) or 'none'}"
            f" · boundary cases {summary['boundary_cases_derived']}"
            f" (not-derivable {summary['boundary_not_derivable']})"
        )
        unreached = [
            code
            for code in summary["band4_reason_codes"]
            if code not in summary["band4_reason_codes_exercised"]
        ]
        lines.append(
            f"  band-4 routes pinned "
            f"{len(summary['band4_reason_codes_exercised'])}/"
            f"{len(summary['band4_reason_codes'])}"
            + (f" · unreached over this model: {', '.join(unreached)}" if unreached else "")
        )
        for cell in summary["applicability_matrix"]:
            if cell["status"] == "not-applicable":
                lines.append(
                    f"  NOT-APPLICABLE {verbalize.path_segment(cell['family'])}/"
                    f"{cell['case_kind']}: {verbalize.line_text(str(cell['reason']))}"
                )
            elif cell["status"] == "missing":
                lines.append(
                    f"  MISSING {verbalize.path_segment(cell['family'])}/{cell['case_kind']}"
                )
    for row in payload["per_constraint"]:
        ref = verbalize.path_segment(row["constraint_ref"])
        lines.append(
            f"  {ref} [{verbalize.path_segment(row['constraint_type'])}/"
            f"{verbalize.path_segment(row['modality'])}] "
            f"source={verbalize.path_segment(row['source'])} "
            f"status={verbalize.path_segment(row['status'])}"
        )
        coverage = "None" if row["coverage"] is None else f"{row['coverage']:.4f}"
        lines.append(
            f"      n={row['n']} coverage={coverage} (decided={row['decided']}/{row['n']})"
        )
        lines.append(
            f"      false_pass={_fmt_rate(row['false_pass_rate'], row['false_pass'], row['expected_nonpass'])}"
        )
        lines.append(
            f"      false_fail={_fmt_rate(row['false_fail_rate'], row['false_fail'], row['satisfied'])}"
        )
        undecided_num = row["cells"]["undecided"] + row["cells"]["masked_by_vacuity"]
        lines.append(f"      undecided={_fmt_rate(row['undecided_rate'], undecided_num, row['n'])}")
        cells = row["cells"]
        lines.append("      cells: " + " ".join(f"{key}={cells[key]}" for key in _CELL_KEYS))
        markers = []
        if row.get("set_attributed_evidence"):
            markers.append("set-attributed evidence (shared credit, D-05')")
        if row.get("wrong_attribution"):
            markers.append(f"wrong_attribution={row['wrong_attribution']} (D-21 — must be 0)")
        if markers:
            lines.append("      " + "; ".join(markers))
        if "redaction" in payload and row.get("evidence") is not None:
            lines.append(
                "      evidence=" + json.dumps(row["evidence"], ensure_ascii=False, allow_nan=False)
            )
    if "isolating_cases" in summary:
        lines.append(
            f"VIOLATING CASES: isolating={summary['isolating_cases']} "
            f"set-attributed={summary['set_attributed_cases']} "
            f"wrong_attribution={summary['wrong_attribution']}"
        )
    defects = payload["checker_defects"]
    lines.append(f"CHECKER DEFECTS: {len(defects)}")
    for defect in defects:
        lines.append(
            f"  [{defect['kind']}] {verbalize.path_segment(defect['constraint_ref'])} "
            f"expected={defect['expected_verdict']} observed={defect['observed_verdict']}"
            + (f" seed={defect['seed']}" if "seed" in defect else f" population={verbalize.path_segment(defect['population'])}")
        )
    return "\n".join(lines)
