from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gnd import payloads as report_module
from gnd import resolve_version
from gnd.checker import check
from gnd.exits import EXIT_GENERATOR, EXIT_IO, EXIT_QUARANTINE
from gnd.model import ModelValidationError, ValidationIssue, load_model, structured_derivation_ids
from gnd.population import load_population
from gnd.synth.corpus_service import (
    IndexValidationError,
    _merge_index,
    _SynthCorpusTransaction,
    _validate_existing_synth_index,
    _validate_index_document,
)


def _emit_boundary_corpus(
    *,
    model: Any,
    baseline: Any,
    baseline_seed_value: int,
    baseline_expectations: dict[str, Any],
    out_root: Path,
    build_sidecar: Any,
    written: list[dict[str, Any]],
    not_derivable: list[dict[str, Any]],
    output_format: str,
    fail: Any,
    abort_quarantine: Any,
    filename_suffix: str = "",
) -> int | None:
    """Derive, admit and write the boundary class (D-06). ``None`` on success.

    Every case carries its PREDICTED verdict, derived at the same time as the
    data; a case the real checker disagrees with is QUARANTINED at exit 6 with a
    typed discrepancy and its sidecar keeps the prediction (C1) — the derivation
    is authoritative, the checker observational.
    """
    import hashlib as _hashlib
    from random import Random

    from gnd.checker import band as _cb
    from gnd.synth import assemble as _assemble
    from gnd.synth import boundary as _boundary
    from gnd.synth import frontier as _frontier
    from gnd.synth import paths as _paths
    from gnd.synth import provenance as _prov

    cases, downs = _boundary.enumerate_boundary(model, baseline.doc, Random(baseline_seed_value))
    # The two case kinds D-10's three labels do not name. `no-subjects` is the
    # (no-subjects, pass) row F-02 and F-05 both lived in; `unchecked` pins the
    # band-4 frontier the undecided rate is measured over. Both carry
    # `label: boundary`, so no schema copy moves (D-15).
    frontier_cases, frontier_downs = _frontier.enumerate_frontier(
        model, baseline.doc, Random(baseline_seed_value)
    )
    cases = cases + frontier_cases
    downs = downs + frontier_downs
    for down in downs:
        record = down.as_record()
        not_derivable.append(record)
    bound_not_derivable = [down.as_record() for down in downs]

    for case in cases:
        # A stable per-case seed derived from (baseline_seed, ref, case name), so
        # a case regenerates without replaying the whole enumeration.
        digest = _hashlib.sha256(
            f"{baseline_seed_value}:{case.constraint_ref}:{case.name}".encode()
        ).digest()
        case_seed = int.from_bytes(digest[:8], "big")
        label = _prov.CASE_KIND_TO_LABEL[case.case_kind]
        pop_rel = (
            f"{label}/{_paths.slug(case.constraint_ref)}.{_paths.slug(case.name)}"
            f"{filename_suffix}.json"
        )
        try:
            pop_abs = _paths.safe_output_path(out_root, pop_rel)
        except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
            return fail(EXIT_IO, f"refused output path for {case.constraint_ref}: {error}")

        try:
            admitted = _boundary.emit_boundary(model, case, pop_abs)
        except _boundary.BoundaryPredictionMismatch as mismatch:
            # C1: RETAIN under quarantine at exit 6 with the PREDICTION intact.
            try:
                q_rel = (
                    f"quarantine/{_paths.slug(case.constraint_ref)}."
                    f"{_paths.slug(case.name)}{filename_suffix}.json"
                )
                q_abs = _paths.safe_output_path(out_root, q_rel)
                q_abs.parent.mkdir(parents=True, exist_ok=True)
                q_abs.write_text(
                    json.dumps(mismatch.doc, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
                q_sidecar = build_sidecar(
                    q_abs.name,
                    label,
                    case_seed,
                    baseline.pool_size,
                    {**baseline_expectations, **mismatch.predicted},
                    case_kind=case.case_kind,
                    operator=case.name,
                    target=case.constraint_ref,
                    predicted_verdict=(
                        mismatch.predicted[case.constraint_ref].expected_verdict
                        if case.constraint_ref in mismatch.predicted
                        else None
                    ),
                    boundary_side=case.side,
                    epsilon=case.epsilon,
                    not_derivable=bound_not_derivable or None,
                    baseline_seed=baseline_seed_value,
                )
                _prov.write_sidecar(q_sidecar, q_abs)
                (q_abs.with_suffix(".discrepancy.json")).write_text(
                    json.dumps(mismatch.discrepancies, indent=2) + "\n", encoding="utf-8"
                )
                pop_abs.unlink(missing_ok=True)
            except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
                return fail(EXIT_IO, f"could not write quarantine: {error}")
            try:
                quarantine_path = abort_quarantine(q_abs)
            except OSError as error:
                return fail(EXIT_IO, f"could not publish quarantine: {error}")
            if output_format == "json":
                report_module.emit(
                    {
                        "command": "synth",
                        "exit_code": EXIT_QUARANTINE,
                        "quarantine": str(quarantine_path),
                        "discrepancies": mismatch.discrepancies,
                    }
                )
            else:
                print(
                    f"QUARANTINED (boundary prediction/observation mismatch, C1): {quarantine_path}"
                )
                print(f"  {mismatch}")
            return EXIT_QUARANTINE
        except _assemble.GeneratorError as error:
            return fail(
                EXIT_GENERATOR,
                f"generator invariant failed for boundary case {case.name} on "
                f"{case.constraint_ref}: {error}",
            )

        try:
            sidecar = build_sidecar(
                pop_abs.name,
                label,
                case_seed,
                baseline.pool_size,
                {**baseline_expectations, **admitted.predicted},
                case_kind=case.case_kind,
                operator=case.name,
                target=case.constraint_ref,
                predicted_verdict=admitted.predicted_verdict,
                boundary_side=case.side,
                epsilon=case.epsilon,
                not_derivable=bound_not_derivable or None,
                baseline_seed=baseline_seed_value,
            )
            sidecar_abs = _prov.write_sidecar(sidecar, pop_abs)
        except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
            return fail(EXIT_IO, f"could not write sidecar for {pop_abs}: {error}")
        written.append(
            {
                "population": str(pop_abs),
                "sidecar": str(sidecar_abs),
                "seed": case_seed,
                "band": _cb(admitted.report),
                "class": label,
                "case_kind": case.case_kind,
                "operator": case.name,
                "boundary_side": case.side,
                "epsilon": case.epsilon,
                "target": case.constraint_ref,
                "predicted_verdict": admitted.predicted_verdict,
                "baseline_seed": baseline_seed_value,
            }
        )
    return None

def _bind_synth_not_derivable(
    out_root: Path, not_derivable: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Bind the complete stand-down manifest into every current v4 sidecar."""
    from gnd.synth import provenance as _prov

    records: dict[tuple[str, str], dict[str, Any]] = {}
    index_path = out_root / "index.json"
    if index_path.exists():
        document = _validate_index_document(json.loads(index_path.read_text(encoding="utf-8")))
        for record in document["not_derivable"]:
            records[(str(record.get("constraint_ref")), str(record.get("operator")))] = record
    for record in not_derivable:
        records[(str(record.get("constraint_ref")), str(record.get("operator")))] = record
    manifest = [records[key] for key in sorted(records)]

    for sidecar_path in out_root.rglob("*.meta.json"):
        if "quarantine" in sidecar_path.relative_to(out_root).parts:
            continue
        sidecar = _prov.read_sidecar(sidecar_path)
        if sidecar.schema_version not in {"gnd-sidecar/4", "gnd-sidecar/5"}:
            continue
        population_path = sidecar_path.parent / sidecar.population
        updated = sidecar.model_copy(update={"not_derivable": manifest or None})
        _prov.write_sidecar(updated, population_path)
    return manifest

def _cmd_synth(
    model_path: str,
    out: str,
    class_: str,
    pool_path: str | None,
    seed: int | None,
    seeds: int,
    output_format: str,
    baseline_seed: int | None = None,
) -> int:
    """Generate labelled synthetic populations for a model (DATA-01).

    The development lane is probabilistic by DEFAULT (owner correction): ``--seed``
    omitted draws OS entropy per population and RECORDS it in the sidecar, so the
    data is fresh yet regenerable; ``--seed N`` is the deterministic
    variant-regeneration path (D-07′). ``--pool`` consumes an admitted pool; an
    omitted ``--pool`` builds a Faker pool and MATERIALISES it beside the corpus,
    so every run's ``pool_sha256`` is a real hashed file (D-19). ``index.json``
    MERGES across ``--class`` invocations (Gemini), never overwrites.

    ``--class violating`` (plan 05) mutates a conforming baseline — named by
    ``--baseline-seed`` so every case is traceable to what it mutated — one
    population per (constraint, applicable operator) pair, each admitted ONLY
    after the real checker confirms the model-derived typed prediction. A
    prediction/observation mismatch QUARANTINES the case (retained, typed
    discrepancy, exit 6, C1) — it is never discarded and its sidecar is never
    relabelled to match observation, because the disagreement may be a checker
    defect and a discarded case is how that defect vanishes from its own
    evaluation corpus.
    """
    import hashlib as _hashlib
    import os
    import tempfile
    from random import Random

    from gnd.checker import band as _cb
    from gnd.synth import assemble as _assemble
    from gnd.synth import mutate as _mutate
    from gnd.synth import paths as _paths
    from gnd.synth import poolfile as _poolfile
    from gnd.synth import provenance as _prov

    transaction: _SynthCorpusTransaction | None = None

    def fail(code: int, message: str) -> int:
        if transaction is not None:
            transaction.abort()
        if output_format == "json":
            report_module.emit({"command": "synth", "exit_code": code, "error": message})
        else:
            print(f"ERROR: {message}")
        return code

    try:
        model = load_model(model_path)
        from gnd.terms import require_non_temporal

        require_non_temporal(model, "synth")
        if model.reference_populations:
            raise ModelValidationError(
                [
                    ValidationIssue(
                        path="$",
                        message="synth does not support reference populations",
                        rule_id="reference:consumer-unsupported",
                    )
                ]
            )
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        return fail(3, f"{model_path}: {error}")

    structured = structured_derivation_ids(model)
    if structured:
        from gnd.checker import _model_uses_exact_derivations

        if any(
            isinstance(rule := fact_type.get("derivation_rule"), dict)
            and "clauses" in rule
            for fact_type in model.fact_types
        ) or not _model_uses_exact_derivations(model):
            return fail(
                EXIT_GENERATOR,
                "synth-derivation-unsupported: model declares structured "
                f"derivation rules ({', '.join(structured)}); generating a "
                "claimed derived extension is the forward-chaining constructor "
                "OQ-P2-2 names, and synth refuses rather than emitting facts it "
                "cannot warrant",
            )

    final_out_root = Path(out)
    try:
        _validate_existing_synth_index(final_out_root)
        transaction = _SynthCorpusTransaction(final_out_root)
    except IndexValidationError as error:
        return fail(3, f"could not prepare {final_out_root / 'index.json'}: {error}")
    except OSError as error:
        return fail(EXIT_IO, f"could not stage corpus {final_out_root}: {error}")
    out_root = transaction.stage_root
    model_ref = Path(model_path).name
    model_stem = _paths.slug(Path(model_path).stem)
    primary_dir = {"violating": "violating", "boundary": "boundary"}.get(class_, "conforming")

    # Resolve the pool: an admitted --pool, or a freshly built Faker pool. Either
    # way it is MATERIALISED into the corpus so pool_sha256 is never empty.
    pool_seed = seed if seed is not None else int.from_bytes(os.urandom(8), "big")
    try:
        if pool_path is not None:
            pool = _poolfile.load_pool(pool_path, model)
        else:
            pool = _poolfile.build_faker_pool(model, Random(pool_seed), size_per_type=8)
    except _poolfile.PoolValidationError as error:
        return fail(EXIT_GENERATOR, f"pool rejected:\n{error}")
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        return fail(EXIT_GENERATOR, f"pool could not be prepared: {error}")

    try:
        pool_rel = f"{primary_dir}/pool.{pool.sha256[:16]}.pool.json"
        pool_abs = _paths.safe_output_path(out_root, pool_rel)
        pool_abs.parent.mkdir(parents=True, exist_ok=True)
        _poolfile.write_pool(pool, pool_abs)
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        return fail(EXIT_IO, f"could not materialise the pool: {error}")

    provenance = pool.provenance or {}
    derivation_rules = {
        str(fact_type.get("id")): fact_type.get("derivation_rule") for fact_type in model.fact_types
    }
    unmutated_derivations = [
        {
            "derivation_ref": f"derivation:{fact_type_id}",
            "reason": (
                f"aggregate:{derivation_rules[fact_type_id]['aggregate']['fn']}-mutation-unsupported"
                if isinstance(derivation_rules[fact_type_id], dict)
                and isinstance(derivation_rules[fact_type_id].get("aggregate"), dict)
                else "structured-derivation-mutation-unsupported"
            ),
        }
        for fact_type_id in structured
    ]

    def abort_quarantine(staged_path: Path) -> Path:
        if transaction is None:
            return staged_path
        relative = staged_path.relative_to(transaction.stage_root)
        published_path = transaction.final_root / relative
        transaction.abort(publish_quarantine=True)
        return published_path

    def typed_expectations(assembly: _assemble.Assembly) -> dict[str, _prov.ExpectedState]:
        return {
            ref: _prov.ExpectedState(
                ground_truth=state.ground_truth,
                expected_verdict=state.expected_verdict,
                reason=state.reason,
            )
            for ref, state in assembly.expectations.items()
        }

    def build_sidecar(
        pop_name: str,
        class_label: str,
        pop_seed: int,
        pool_size: int,
        expectations: dict[str, _prov.ExpectedState],
        **extra: Any,
    ) -> _prov.Sidecar:
        return _prov.Sidecar(
            population=pop_name,
            population_sha256="",  # write_sidecar computes it over the written file
            **{"class": class_label},
            seed=pop_seed,
            gnd_version=resolve_version(),
            model=model_ref,
            model_id=str(model.model_id) if model.model_id else None,
            model_digest=_prov.validated_model_sha256(model),
            pool_source=str(provenance.get("source", "unknown")),
            pool_path=pool_rel,
            pool_sha256=pool.sha256,
            proposer_model=provenance.get("proposer_model"),
            prompt_version=provenance.get("prompt_version"),
            pool_size=pool_size,
            expectations=expectations,
            unmutated_derivations=unmutated_derivations,
            **extra,
        )

    def write_witness_quarantine(disc: _assemble.CheckerWitnessDiscrepancy, pop_seed: int) -> int:
        # C1: RETAIN the case under quarantine, never discard or relabel.
        try:
            q_rel = f"quarantine/{model_stem}.conforming.seed{pop_seed}.json"
            q_abs = _paths.safe_output_path(out_root, q_rel)
            q_abs.parent.mkdir(parents=True, exist_ok=True)
            q_abs.write_text(
                json.dumps(disc.doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            (q_abs.with_suffix(".discrepancy.json")).write_text(
                json.dumps(disc.discrepancies, indent=2) + "\n", encoding="utf-8"
            )
        except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
            return fail(EXIT_IO, f"could not write quarantine: {error}")
        try:
            quarantine_path = abort_quarantine(q_abs)
        except OSError as error:
            return fail(EXIT_IO, f"could not publish quarantine: {error}")
        if output_format == "json":
            report_module.emit(
                {
                    "command": "synth",
                    "exit_code": EXIT_QUARANTINE,
                    "quarantine": str(quarantine_path),
                    "discrepancies": disc.discrepancies,
                }
            )
        else:
            # Both directions land here (CR-04); the kinds name which one, and a
            # candidate false PASS is the one a reader must not skim past.
            kinds = sorted({str(record.get("kind", "candidate")) for record in disc.discrepancies})
            print(f"QUARANTINED ({', '.join(kinds)}, C1): {quarantine_path}")
            for record in disc.discrepancies:
                print(
                    f"  {record['constraint_ref']}: witness={record['witness']} "
                    f"observed={record['observed']}"
                )
        return EXIT_QUARANTINE

    written: list[dict[str, Any]] = []
    not_derivable: list[dict[str, Any]] = []

    if class_ in ("conforming", "all"):
        seed_values = (
            [seed + i for i in range(seeds)]
            if seed is not None
            else [int.from_bytes(os.urandom(8), "big") for _ in range(seeds)]
        )
        for pop_seed in seed_values:
            try:
                assembly = _assemble.assemble_conforming(
                    model, pop_seed, pool=pool, model_ref=model_ref
                )
            except _assemble.CheckerWitnessDiscrepancy as disc:
                return write_witness_quarantine(disc, pop_seed)
            except _assemble.GeneratorError as error:
                return fail(
                    EXIT_GENERATOR, f"generator invariant failed at seed {pop_seed}: {error}"
                )

            try:
                pop_rel = f"conforming/{model_stem}.conforming.seed{pop_seed}.json"
                pop_abs = _paths.safe_output_path(out_root, pop_rel)
                pop_abs.parent.mkdir(parents=True, exist_ok=True)
                pop_abs.write_text(
                    json.dumps(assembly.doc, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
            except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
                return fail(EXIT_IO, f"could not write population: {error}")

            # Re-admit the EMITTED file (exit 5 on rejection) — a structurally
            # invalid population contributes zero verdicts and must be loud.
            try:
                population = load_population(str(pop_abs), model=model)
            except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
                return fail(EXIT_GENERATOR, f"emitted population failed re-admission: {error}")
            report = check(model, population)

            try:
                sidecar = build_sidecar(
                    pop_abs.name,
                    "conforming",
                    pop_seed,
                    assembly.pool_size,
                    typed_expectations(assembly),
                    case_kind="conforming",
                )
                sidecar_abs = _prov.write_sidecar(sidecar, pop_abs)
            except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
                return fail(EXIT_IO, f"could not write sidecar for {pop_abs}: {error}")
            written.append(
                {
                    "population": str(pop_abs),
                    "sidecar": str(sidecar_abs),
                    "seed": pop_seed,
                    "band": _cb(report),
                    "class": "conforming",
                    "case_kind": "conforming",
                }
            )

    class _BaselineFailure(Exception):
        def __init__(self, code: int) -> None:
            self.code = code

    baseline_cache: dict[int, tuple[int, Any, Any, dict[str, _prov.ExpectedState]]] = {}

    def resolve_baseline(b_seed: int) -> tuple[int, Any, Any, dict[str, _prov.ExpectedState]]:
        """The conforming baseline the boundary and violating classes build on.

        Cached by seed so ``--class all`` assembles each variant ONCE: two classes
        derived from different baselines would not be comparable, and the
        sidecar's ``baseline_seed`` would name different populations for cases
        the report shows side by side.
        """
        if b_seed in baseline_cache:
            return baseline_cache[b_seed]
        try:
            baseline = _assemble.assemble_conforming(model, b_seed, pool=pool, model_ref=model_ref)
        except _assemble.CheckerWitnessDiscrepancy as disc:
            raise _BaselineFailure(write_witness_quarantine(disc, b_seed)) from None
        except _assemble.GeneratorError as error:
            raise _BaselineFailure(
                fail(EXIT_GENERATOR, f"baseline assembly failed at seed {b_seed}: {error}")
            ) from None
        try:
            with tempfile.NamedTemporaryFile(
                "w", suffix=".json", delete=False, encoding="utf-8"
            ) as handle:
                json.dump(baseline.doc, handle)
                temp_path = handle.name
            try:
                baseline_report = check(model, load_population(temp_path, model=model))
            finally:
                Path(temp_path).unlink(missing_ok=True)
        except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
            raise _BaselineFailure(
                fail(EXIT_GENERATOR, f"baseline failed re-admission: {error}")
            ) from None
        baseline_cache[b_seed] = (b_seed, baseline, baseline_report, typed_expectations(baseline))
        return baseline_cache[b_seed]

    def emit_violating_corpus(
        b_seed: int,
        baseline: Any,
        baseline_report: Any,
        baseline_expectations: dict[str, _prov.ExpectedState],
        filename_suffix: str,
    ) -> int | None:
        cases, stand_downs = _mutate.enumerate_violating(model, baseline.doc)
        not_derivable.extend(stand_downs)
        for ref, mutation in cases:
            # A stable per-case seed derived from (baseline_seed, ref, operator),
            # so a case regenerates without replaying the whole enumeration.
            digest = _hashlib.sha256(f"{b_seed}:{ref}:{mutation.name}".encode()).digest()
            case_seed = int.from_bytes(digest[:8], "big")
            pop_rel = (
                f"violating/{_paths.slug(ref)}.{_paths.slug(mutation.name)}{filename_suffix}.json"
            )
            try:
                pop_abs = _paths.safe_output_path(out_root, pop_rel)
            except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
                return fail(EXIT_IO, f"refused output path for {ref}: {error}")
            try:
                case = _mutate.emit_violating(
                    model,
                    baseline.doc,
                    baseline_report,
                    mutation,
                    ref,
                    pop_abs,
                    Random(case_seed),
                )
            except _mutate.PredictionMismatch as mismatch:
                # QUARANTINE, never discard (C1): the prediction is authoritative
                # ground truth; the checker's disagreement is an observation and a
                # candidate checker defect, adjudicated later. The sidecar keeps
                # the PREDICTION — relabelling it to match observation is the
                # oracle circularity that lets a present-day checker defect
                # vanish from its own evaluation corpus. Exit 5 stays reserved
                # for structural GeneratorError; a disagreement is exit 6.
                try:
                    q_rel = (
                        f"quarantine/{_paths.slug(ref)}.{_paths.slug(mutation.name)}"
                        f"{filename_suffix}.json"
                    )
                    q_abs = _paths.safe_output_path(out_root, q_rel)
                    q_abs.parent.mkdir(parents=True, exist_ok=True)
                    q_abs.write_text(
                        json.dumps(mismatch.doc, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8",
                    )
                    q_sidecar = build_sidecar(
                        q_abs.name,
                        "violating",
                        case_seed,
                        baseline.pool_size,
                        {**baseline_expectations, **mismatch.predicted},
                        violates=sorted(mismatch.predicted),
                        operator=mutation.name,
                        violates_target=ref,
                        isolating=len(mismatch.predicted) == 1,
                        isolation_verified=False,  # the checker did NOT confirm it
                        baseline_seed=b_seed,
                        not_derivable=stand_downs or None,
                    )
                    _prov.write_sidecar(q_sidecar, q_abs)
                    (q_abs.with_suffix(".discrepancy.json")).write_text(
                        json.dumps(mismatch.discrepancies, indent=2) + "\n", encoding="utf-8"
                    )
                    pop_abs.unlink(missing_ok=True)  # retained under quarantine/, not corpus
                except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
                    return fail(EXIT_IO, f"could not write quarantine: {error}")
                try:
                    quarantine_path = abort_quarantine(q_abs)
                except OSError as error:
                    return fail(EXIT_IO, f"could not publish quarantine: {error}")
                if output_format == "json":
                    report_module.emit(
                        {
                            "command": "synth",
                            "exit_code": EXIT_QUARANTINE,
                            "quarantine": str(quarantine_path),
                            "discrepancies": mismatch.discrepancies,
                        }
                    )
                else:
                    print(f"QUARANTINED (prediction/observation mismatch, C1): {quarantine_path}")
                    print(f"  {mismatch}")
                return EXIT_QUARANTINE
            except _assemble.GeneratorError as error:
                return fail(
                    EXIT_GENERATOR,
                    f"generator invariant failed for {mutation.name} on {ref}: {error}",
                )

            try:
                sidecar = build_sidecar(
                    pop_abs.name,
                    "violating",
                    case_seed,
                    baseline.pool_size,
                    {**baseline_expectations, **case.predicted},
                    violates=sorted(case.predicted),
                    operator=mutation.name,
                    violates_target=ref,
                    isolating=case.isolating,
                    isolation_verified=True,
                    baseline_seed=b_seed,
                    case_kind="violating",
                    target=ref,
                    not_derivable=stand_downs or None,
                )
                sidecar_abs = _prov.write_sidecar(sidecar, pop_abs)
            except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
                return fail(EXIT_IO, f"could not write sidecar for {pop_abs}: {error}")
            written.append(
                {
                    "population": str(pop_abs),
                    "sidecar": str(sidecar_abs),
                    "seed": case_seed,
                    "band": _cb(case.report),
                    "class": "violating",
                    "case_kind": "violating",
                    "operator": mutation.name,
                    "target": ref,
                    "violates_target": ref,
                    "violates": sorted(case.predicted),
                    "isolating": case.isolating,
                    "isolation_verified": True,
                    "baseline_seed": b_seed,
                }
            )
        return None

    if class_ in ("boundary", "violating", "all"):
        baseline_start = baseline_seed if baseline_seed is not None else seed
        baseline_seeds = (
            [baseline_start + i for i in range(seeds)]
            if baseline_start is not None
            else [int.from_bytes(os.urandom(8), "big") for _ in range(seeds)]
        )
        for b_seed_value in baseline_seeds:
            try:
                b_seed, baseline, baseline_report, baseline_expectations = resolve_baseline(
                    b_seed_value
                )
            except _BaselineFailure as failure:
                return failure.code

            # A multi-seed run emits the same operator names for each baseline;
            # include the baseline seed so later variants cannot overwrite the
            # first one.  Preserve the historical single-seed names.
            filename_suffix = f".baseline{b_seed}" if seeds > 1 else ""
            if class_ in ("boundary", "all"):
                outcome = _emit_boundary_corpus(
                    model=model,
                    baseline=baseline,
                    baseline_seed_value=b_seed,
                    baseline_expectations=baseline_expectations,
                    out_root=out_root,
                    build_sidecar=build_sidecar,
                    written=written,
                    not_derivable=not_derivable,
                    output_format=output_format,
                    fail=fail,
                    abort_quarantine=abort_quarantine,
                    filename_suffix=filename_suffix,
                )
                if outcome is not None:
                    return outcome

            if class_ in ("violating", "all"):
                outcome = emit_violating_corpus(
                    b_seed,
                    baseline,
                    baseline_report,
                    baseline_expectations,
                    filename_suffix,
                )
                if outcome is not None:
                    return outcome

    try:
        not_derivable = _bind_synth_not_derivable(out_root, not_derivable)
        _merge_index(out_root, written, not_derivable)
    except (_prov.SidecarError, json.JSONDecodeError) as error:
        return fail(EXIT_IO, f"could not bind generator manifest: {error}")
    except IndexValidationError as error:
        return fail(3, f"could not merge {out_root / 'index.json'}: {error}")
    except OSError as error:
        return fail(EXIT_IO, f"could not write {out_root / 'index.json'}: {error}")

    stage_root = out_root
    try:
        transaction.commit()
    except OSError as error:
        return fail(EXIT_IO, f"could not publish corpus {final_out_root}: {error}")
    for entry in written:
        for field in ("population", "sidecar"):
            entry[field] = str(final_out_root / Path(entry[field]).relative_to(stage_root))
    out_root = final_out_root

    violating_entries = [entry for entry in written if entry["class"] == "violating"]
    isolating_count = sum(1 for entry in violating_entries if entry.get("isolating"))
    isolating_fraction = isolating_count / len(violating_entries) if violating_entries else None

    if output_format == "json":
        report_module.emit(
            {
                "command": "synth",
                "exit_code": 0,
                "out": str(out_root),
                "class": class_,
                "pool": pool_rel,
                "pool_sha256": pool.sha256,
                "populations": written,
                "not_derivable": not_derivable,
                "isolating_cases": isolating_count,
                "set_attributed_cases": len(violating_entries) - isolating_count,
                "isolating_fraction": isolating_fraction,
            }
        )
    else:
        print(f"OK: wrote {len(written)} {class_} population(s) under {out_root}")
        for entry in written:
            label = entry.get("operator") or "conforming"
            print(f"  seed {entry['seed']}: {entry['population']} (band {entry['band']}, {label})")
        if violating_entries:
            print(
                f"  isolating: {isolating_count}/{len(violating_entries)} "
                f"({isolating_fraction:.3f}) — set-attributed: "
                f"{len(violating_entries) - isolating_count}"
            )
        for record in not_derivable:
            print(
                f"  not-derivable: {record['constraint_ref']} "
                f"[{record['operator'] or record['family']}]: {record['mechanism']}"
            )
        print(f"  pool: {pool_rel} ({pool.sha256[:16]})")
    return 0

_emit_boundary_corpus.__module__ = "gnd.cli"
_bind_synth_not_derivable.__module__ = "gnd.cli"
_cmd_synth.__module__ = "gnd.cli"
