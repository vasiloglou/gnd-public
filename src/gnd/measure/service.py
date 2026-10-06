from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gnd import payloads as report_module
from gnd import resolve_version
from gnd.checker import band as checker_band
from gnd.checker import check
from gnd.exits import EXIT_CHECKER_DEFECT, EXIT_GENERATOR, EXIT_INTERNAL, EXIT_IO, EXIT_USAGE
from gnd.model import load_model
from gnd.population import load_population
from gnd.synth.corpus_service import (
    CorpusPathError,
    IndexValidationError,
    _resolve_corpus_path,
    _resolve_unique_index_entries,
    _validate_index_document,
)


def _cmd_measure(
    model_path: str,
    populations: str,
    output_format: str,
    out: str | None,
    promote: str | None = None,
    *,
    unredacted: bool = False,
) -> int:
    """Measure the checker's per-constraint rates over labelled populations (VER-03).

    Computed OFFLINE from committed artifacts (owner's two-lane rule): this arm
    imports no provider or network module, and the payload carries no timestamp
    so two runs over one corpus reproduce byte-for-byte. Exit codes: 3 on a C6
    sidecar-binding mismatch (recomputed population/model/pool digest disagrees
    with the sidecar) or a missing/ill-formed expectation, 5 on a population that
    fails re-admission, 6 when checker_defects[] is non-empty (C9), 64 on a mixed
    (model, pool_source) corpus (C4).
    """
    from gnd import redaction as _redaction
    from gnd.measure import report as measure_report
    from gnd.measure.score import (
        CellLookupError,
        InconsistentExpectationError,
        PartitionError,
    )
    from gnd.measure.truth import ConstraintRefError, ExpectationMissingError
    from gnd.synth import poolfile as _poolfile
    from gnd.synth import provenance as _prov

    policy = None

    def fail(code: int, message: str) -> int:
        payload = {"command": "measure", "exit_code": code, "error": message}
        if policy is not None and policy.active:
            payload["error"] = message if unredacted else _redaction.INSTANCE_DETAIL
            payload = _redaction.project_output(
                "measure",
                payload,
                policy=policy,
                mode="unredacted" if unredacted else "applied",
                emitter_id=f"cli-measure-{output_format}",
            )
        if output_format == "json":
            report_module.emit(payload)
        else:
            if policy is not None and policy.active:
                print(_redaction.render_text_header(payload))
            print(f"ERROR: {payload['error']}")
        return code

    try:
        model = load_model(model_path)
        from gnd.terms import require_non_temporal

        require_non_temporal(model, "measure")
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        return fail(3, f"{model_path}: {error}")
    policy = _redaction.RedactionPolicy.from_model(model)

    populations_dir = Path(populations)
    index_path = populations_dir / "index.json"
    if not index_path.exists():
        return fail(3, f"no index.json under {populations_dir} — nothing to measure.")
    try:
        index = _validate_index_document(json.loads(index_path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as error:
        return fail(3, f"could not read {index_path}: {error}")
    except IndexValidationError as error:
        return fail(3, str(error))

    expected_model_digest = _prov.validated_model_sha256(model)
    expected_aggregate_disclosures = sorted(
        (
            f"derivation:{fact_type['id']}",
            f"aggregate:{fact_type['derivation_rule']['aggregate']['fn']}-mutation-unsupported",
        )
        for fact_type in model.fact_types
        if isinstance(fact_type.get("derivation_rule"), dict)
        and isinstance(fact_type["derivation_rule"].get("aggregate"), dict)
    )
    expected_aggregate_refs = {ref for ref, _reason in expected_aggregate_disclosures}
    pool_sha_cache: dict[str, str] = {}
    measured: list[measure_report.MeasuredPopulation] = []
    validated_entries: list[dict[str, Any]] = []
    loaded_sidecars: list[_prov.Sidecar] = []

    # F-05: every path the payload publishes is CORPUS-ROOT-RELATIVE, so the
    # payload is a function of the corpus and not of how the corpus was named on
    # the command line. Storing `str(pop_path)` inherited the form of
    # `--populations`: measuring with an absolute path baked machine paths into
    # `corpus[].path`, `corpus[].sidecar_path` and
    # `per_constraint[].evidence.population` — 157 differing values, all path
    # strings, no number among them — so the sha256 receipt in 02-MEASUREMENT.md
    # held for the documented relative invocation from the repo root and for no
    # other. This is the same class CR-01 closed on the write side of
    # `index.json`; the payload retained it.
    try:
        corpus_root = populations_dir.resolve()
    except OSError as error:
        return fail(3, f"could not resolve {populations_dir}: {error}")

    def _corpus_relative(path: Path) -> str:
        return path.resolve().relative_to(corpus_root).as_posix()

    try:
        resolved_entries = _resolve_unique_index_entries(populations_dir, index)
    except CorpusPathError as error:
        return fail(3, str(error))

    for index_entry, pop_path, sidecar_path in resolved_entries:
        # C6: verify the sidecar binding BEFORE scoring. read_sidecar recomputes
        # population_sha256 (a stale/edited population) and rejects a swapped
        # sidecar by name; a SidecarError is a binding failure -> exit 3.
        try:
            sidecar = _prov.read_sidecar(sidecar_path)
        except _prov.SidecarError as error:
            return fail(3, f"C6 sidecar binding failed for {pop_path}: {error}")
        except OSError as error:
            return fail(3, f"could not read sidecar {sidecar_path}: {error}")
        if expected_aggregate_disclosures:
            actual_aggregate_disclosures = sorted(
                (row.get("derivation_ref", ""), row.get("reason", ""))
                for row in sidecar.unmutated_derivations
                if row.get("derivation_ref") in expected_aggregate_refs
                or row.get("reason", "").startswith("aggregate:")
            )
            if (
                sidecar.schema_version != "gnd-sidecar/5"
                or actual_aggregate_disclosures != expected_aggregate_disclosures
            ):
                return fail(
                    3,
                    f"unmutated_derivations in {sidecar_path} do not disclose every "
                    "aggregate derivation declared by the model",
                )

        # C6 (continued): recompute model_digest and pool_sha256 — the two digests
        # read_sidecar cannot check without the model and pool objects.
        if sidecar.model_digest != expected_model_digest:
            return fail(
                3,
                f"C6 sidecar binding failed for {pop_path}: model_digest "
                f"{sidecar.model_digest!r} does not match this model "
                f"({expected_model_digest!r}) — a wrong-model sidecar.",
            )
        try:
            pool_abs = _resolve_corpus_path(populations_dir, sidecar.pool_path)
        except CorpusPathError as error:
            return fail(3, f"C6 pool binding failed for {pop_path}: {error}")
        try:
            if str(pool_abs) not in pool_sha_cache:
                pool_sha_cache[str(pool_abs)] = _poolfile.load_pool(pool_abs, model).sha256
            recomputed_pool_sha = pool_sha_cache[str(pool_abs)]
        except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
            return fail(3, f"C6 pool binding failed for {pop_path}: {error}")
        if recomputed_pool_sha != sidecar.pool_sha256:
            return fail(
                3,
                f"C6 sidecar binding failed for {pop_path}: pool_sha256 "
                f"{sidecar.pool_sha256!r} does not match {pool_abs} "
                f"({recomputed_pool_sha!r}).",
            )

        # A population that fails to load is never counted — exit 5. A skipped
        # population contributes zero verdicts, hence zero errors, hence a better
        # score (T-02-19).
        try:
            population = load_population(str(pop_path), model=model)
        except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
            return fail(EXIT_GENERATOR, f"population {pop_path} failed to load: {error}")
        report = check(model, population)
        observed_by_ref = {verdict.constraint_ref: verdict.verdict for verdict in report.verdicts}
        checker_disagrees_with_oracle = any(
            observed_by_ref.get(ref) != state.expected_verdict
            for ref, state in sidecar.expectations.items()
        )

        # Every index label is a redundant cache.  The sidecar is bound to the
        # population bytes and the checker owns the observed band, so a cache
        # mismatch is malformed corpus input rather than coverage evidence.
        authoritative: dict[str, Any] = {
            "seed": sidecar.seed,
            "band": checker_band(report),
            "class": sidecar.class_,
            "case_kind": sidecar.case_kind or sidecar.class_,
            "operator": sidecar.operator,
            "boundary_side": sidecar.boundary_side,
            "epsilon": sidecar.epsilon,
            "target": sidecar.target,
            "predicted_verdict": sidecar.predicted_verdict,
            "violates_target": sidecar.violates_target,
            "violates": sorted(sidecar.violates) if sidecar.violates is not None else None,
            "isolating": sidecar.isolating,
            "isolation_verified": sidecar.isolation_verified,
            "baseline_seed": sidecar.baseline_seed,
        }
        for field in ("seed", "band", "class", "case_kind"):
            if index_entry[field] != authoritative[field]:
                # The checker is the system UNDER measurement.  When its live
                # observations disagree with the bound oracle, a changed band is
                # defect evidence, not proof the historical index was forged.
                # On an oracle-consistent corpus the same mismatch remains a
                # hard metadata failure, which is what catches index tampering.
                if field == "band" and checker_disagrees_with_oracle:
                    authoritative["band"] = index_entry[field]
                    continue
                return fail(
                    3,
                    f"index.json metadata for {pop_path} disagrees with its "
                    f"sidecar/checker: {field}={index_entry[field]!r}, expected "
                    f"{authoritative[field]!r}",
                )
        for field, expected in authoritative.items():
            if field in ("seed", "band", "class", "case_kind") or field not in index_entry:
                continue
            actual = index_entry[field]
            if field == "epsilon" and actual is not None and expected is not None:
                actual, expected = str(actual), str(expected)
            if field == "violates" and actual is not None:
                actual = sorted(actual)
            # v1-v3 sidecars predate bound operator provenance. Preserve their
            # readability, but never feed that legacy index-only operator into
            # a v4 coverage summary.
            if (
                field == "operator"
                and expected is None
                and sidecar.schema_version not in {"gnd-sidecar/4", "gnd-sidecar/5"}
            ):
                continue
            if actual != expected:
                return fail(
                    3,
                    f"index.json metadata for {pop_path} disagrees with its "
                    f"sidecar: {field}={actual!r}, expected {expected!r}",
                )

        validated_entry = {
            "population": index_entry["population"],
            "sidecar": index_entry["sidecar"],
            **{field: value for field, value in authoritative.items() if value is not None},
        }
        if (
            sidecar.schema_version not in {"gnd-sidecar/4", "gnd-sidecar/5"}
            and sidecar.operator is None
            and index_entry.get("operator") is not None
        ):
            validated_entry["operator"] = index_entry["operator"]
        validated_entries.append(validated_entry)
        loaded_sidecars.append(sidecar)

        measured.append(
            measure_report.MeasuredPopulation(
                population_path=_corpus_relative(pop_path),
                population_sha256=sidecar.population_sha256,
                sidecar_path=_corpus_relative(sidecar_path),
                sidecar_sha256=_prov._sha256_file(sidecar_path),
                sidecar=sidecar,
                report=report,
            )
        )

    # WR-02: the measured set is whatever index.json lists, and index.json is
    # covered by no digest — so a PRUNED index quietly narrows every denominator
    # while the run still exits 0 (deleting the 51 violating entries from a
    # committed index still published `false_pass_rate 0.0`). Reconcile the index
    # against the TREE: a population/sidecar pair sitting on disk but absent from
    # the scored set is an unexplained file, which is exactly what `corpus[]` is
    # supposed to make visible. `quarantine/` is excluded deliberately — a
    # quarantined case is RETAINED outside the corpus by design (C1), not
    # measured.
    # Both sides of this comparison are corpus-root-relative POSIX strings
    # (F-05), so the reconciliation is over the same identity the payload
    # publishes rather than over resolved absolutes.
    # A fresh v4 corpus binds the complete generator stand-down manifest into
    # its sidecars.  Reconcile the top-level index cache against that union so a
    # fabricated record cannot inflate boundary_not_derivable.  All-legacy and
    # mixed corpora retain read compatibility; their index-only values are not
    # treated as v4 sidecar-derived coverage provenance.
    validated_not_derivable = list(index.get("not_derivable") or [])
    if loaded_sidecars and all(
        sidecar.schema_version in {"gnd-sidecar/4", "gnd-sidecar/5"} for sidecar in loaded_sidecars
    ):
        by_record: dict[tuple[str, str], dict[str, Any]] = {}
        for sidecar in loaded_sidecars:
            for record in sidecar.not_derivable or []:
                key = (
                    str(record.get("constraint_ref")),
                    str(record.get("operator")),
                )
                by_record[key] = record
        indexed = {
            (str(record.get("constraint_ref")), str(record.get("operator"))): record
            for record in validated_not_derivable
        }
        if indexed != by_record:
            return fail(
                3,
                "index.json not_derivable metadata disagrees with the v4 "
                "sidecar-bound generator manifest",
            )
        validated_not_derivable = [by_record[key] for key in sorted(by_record)]

    validated_index = {
        "populations": validated_entries,
        "not_derivable": validated_not_derivable,
    }

    try:
        scored_sidecars = {mp.sidecar_path for mp in measured}
        on_disk = {
            _corpus_relative(candidate)
            for candidate in populations_dir.rglob("*.meta.json")
            if "quarantine" not in Path(_corpus_relative(candidate)).parts
        }
    except (OSError, ValueError) as error:
        return fail(3, f"could not enumerate {populations_dir}: {error}")
    unlisted = sorted(on_disk - scored_sidecars)
    if unlisted:
        return fail(
            3,
            f"{unlisted} sit under {populations_dir} but are not in index.json — "
            f"the measured set is whatever the index lists and the index is bound "
            f"by no digest, so an unlisted population narrows every denominator "
            f"silently. Re-run `gnd synth` to merge them, or remove them.",
        )

    try:
        payload = measure_report.build_measurement_report(
            model,
            measure_report.stable_model_identifier(model_path),
            measured,
            gnd_version=resolve_version(),
            index=validated_index,
            index_sha256=_prov._sha256_file(index_path),
        )
    except measure_report.MixedCorpusError as error:
        return fail(EXIT_USAGE, str(error))
    except (ExpectationMissingError, ConstraintRefError, InconsistentExpectationError) as error:
        # A sidecar whose (ground_truth, expected_verdict) pair the cell table
        # calls an error is ill-formed INPUT, same band as the C6 binding
        # failures — not an internal fault (CR-03). Listed before CellLookupError
        # because it subclasses it.
        return fail(3, f"sidecar/model inconsistency: {error}")
    except (CellLookupError, PartitionError) as error:
        # A verdict/ground-truth state the table does not know, or a broken
        # partition, is an INTERNAL accounting fault. Exit 70 rather than an
        # uncaught traceback's exit 1, which would masquerade as band 1
        # ("alethic fail") to any harness keying on the bands.
        return fail(EXIT_INTERNAL, f"measurement accounting failed: {error}")

    semantic_payload = payload
    from gnd.redaction import RedactionPolicy, project_output

    policy = RedactionPolicy.from_model(model)
    if output_format == "json":
        payload = project_output(
            "measure",
            semantic_payload,
            policy=policy,
            mode="unredacted" if unredacted else "applied",
            emitter_id="cli-measure-json",
        )
    else:
        payload = project_output(
            "measure",
            semantic_payload,
            policy=policy,
            mode="unredacted" if unredacted else "applied",
            emitter_id="cli-measure-text",
        )

    rendered = measure_report._canonical(payload)
    if out is not None:
        try:
            Path(out).write_text(rendered + "\n", encoding="utf-8")
        except OSError as error:
            return fail(EXIT_IO, f"could not write {out}: {error}")

    if output_format == "json":
        if out is None:
            print(rendered)
    else:
        print(measure_report.render_measurement(payload))
        if out is not None:
            print(f"  (json written to {out})")

    if promote is not None:
        outcome = _promote_defects(
            model=model,
            model_path=model_path,
            payload=semantic_payload,
            measured=measured,
            corpus_dir=Path(promote),
            populations_root=corpus_root,
            output_format=output_format,
            fail=fail,
        )
        if outcome is not None:
            return outcome

    # C9: a non-empty checker_defects[] is exit 6, direction-agnostic.
    if semantic_payload["checker_defects"]:
        return EXIT_CHECKER_DEFECT
    return 0

def _promote_defects(
    *,
    model: Any,
    model_path: str,
    payload: dict[str, Any],
    measured: list[Any],
    corpus_dir: Path,
    populations_root: Path,
    output_format: str,
    fail: Any,
) -> int | None:
    """D-14: copy each defect-revealing input into the corpus and PRINT the rows.

    The append stays a REVIEWED act — the corpus's value is that every case
    earned its place — so nothing here edits ``manifest.yaml`` and nothing
    touches ``tests/test_adversarial_corpus.py``. The mechanical part is
    producing rows that are correct by construction.
    """
    from gnd.measure import promote as _promote
    from gnd.synth import GENERATOR_VERSION

    defects = payload["checker_defects"]
    if not defects:
        if output_format != "json":
            print(
                "  --promote: no checker defects to promote. An empty promotion is a "
                "FINDING, not an omission (D-14)."
            )
        return None
    sidecars = {mp.population_path: mp.sidecar for mp in measured}
    try:
        rows = _promote.manifest_rows(
            defects,
            model,
            model_path,
            sidecars,
            corpus_dir,
            generator_version=GENERATOR_VERSION,
            populations_root=populations_root,
        )
        rendered = _promote.render_manifest_rows(rows)
    except _promote.PromotionError as error:
        return fail(EXIT_GENERATOR, f"promotion failed: {error}")
    except OSError as error:
        return fail(EXIT_IO, f"could not write promoted inputs: {error}")

    if output_format == "json":
        report_module.emit(
            {
                "command": "measure",
                "exit_code": EXIT_CHECKER_DEFECT,
                "promoted": rows,
                "corpus_dir": str(corpus_dir),
                "manifest_yaml": rendered,
            }
        )
    else:
        print(
            f"  --promote: {len(rows)} row(s) written into {corpus_dir}. APPEND THEM BY "
            f"REVIEW — this command never edits manifest.yaml:"
        )
        print(rendered)
    return None

_cmd_measure.__module__ = "gnd.cli"
_promote_defects.__module__ = "gnd.cli"
