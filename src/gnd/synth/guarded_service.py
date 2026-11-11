"""Admission, checker confirmation and publication for guarded case corpora."""

from __future__ import annotations

import json
from pathlib import Path
from random import Random
from shutil import move, rmtree

from ruamel.yaml.error import YAMLError

from gnd.address import positional_constraint_ref
from gnd.checker import check
from gnd.errors import ModelLoadError, ModelValidationError, ReferenceInputError
from gnd.exits import EXIT_GENERATOR, EXIT_ILL_FORMED, EXIT_IO, EXIT_QUARANTINE
from gnd.model import load_model, load_model_bytes
from gnd.model_index import ModelIndex, scoped
from gnd.payloads import emit
from gnd.population import PopulationLoadError, load_population_bytes
from gnd.safefs import InstallPathError
from gnd.synth import guarded_cases
from gnd.synth.corpus_service import _SynthCorpusTransaction
from gnd.synth.guarded import _WorkBudget
from gnd.synth.paths import safe_output_path
from gnd.synth.provenance import validated_model_sha256


def _digest(model):
    return "sha256:" + validated_model_sha256(model)


def _write(root, relative, value):
    path = safe_output_path(root, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    return path


def _confirm(model, model_path, facts, covers, ref, verdict, count):
    header = {"model": Path(model_path).name, "source": "synthetic", "covers": covers}
    if model.model_id:
        header["model_id"] = model.model_id
    population_doc = {"population": header, "facts": facts}
    population = load_population_bytes(
        json.dumps(population_doc, allow_nan=False).encode(), source="case.json", model=model
    )
    report = check(model, population)
    observed = next((row for row in report.verdicts if row.constraint_ref == ref), None)
    findings = [
        {
            "constraint_ref": row.constraint_ref,
            "verdict": row.verdict,
            "reason_code": row.reason_code,
        }
        for row in report.verdicts
        if row.constraint_ref != ref and row.verdict != "pass"
    ]
    target = (
        None
        if observed is None
        else {"verdict": observed.verdict, "binding_count": observed.binding_count}
    )
    expected = {"verdict": verdict, "binding_count": count}
    return population_doc, findings, expected, target


def _ordinary_corpus(model, constraints, root, seed, synth):
    scoped_document = model.model_dump(exclude={"warnings"}, exclude_unset=True)
    scoped_constraints = []
    refs = {}
    for ref, constraint, fact_type in constraints:
        if constraint["type"] == "guarded":
            continue
        if fact_type is None:
            refs[ref] = positional_constraint_ref(None, len(scoped_constraints))
            scoped_constraints.append(constraint)
        else:
            refs[ref] = ref
    scoped_document["constraints"] = scoped_constraints
    relative_model = "ordinary/scoped.orm.yaml"
    relative_corpus = "ordinary/corpus"
    path = _write(root, relative_model, scoped_document)
    record = {
        "model": relative_model,
        "source_model_digest": _digest(model),
        "constraint_refs": refs,
    }
    try:
        scoped_model = load_model_bytes(path.read_bytes(), source=path)
    except (ModelLoadError, ModelValidationError, YAMLError) as error:
        return {
            **record,
            "reason": "scoped-model-invalid",
            "detail": str(error).replace(str(root) + "/", ""),
        }, EXIT_ILL_FORMED
    record["model_digest"] = _digest(scoped_model)
    response = {}
    code = synth(
        str(path),
        str(root / relative_corpus),
        "all",
        None,
        seed,
        1,
        "json",
        emit_payload=response.update,
    )
    if code:
        return {
            **record,
            "reason": "ordinary-synth-failed",
            "exit_code": code,
            "detail": (response.get("error") or "See ordinary synthesis quarantine.").replace(
                str(root) + "/", ""
            ),
        }, code
    return {**record, "corpus": relative_corpus, "reason": None}, 0


def _quarantine(transaction, relative, evidence):
    root = transaction.stage_root
    for path in root.iterdir():
        if path.name != "quarantine":
            rmtree(path) if path.is_dir() else path.unlink()
    _write(root, relative, evidence)
    transaction.commit()


@scoped
def run_guarded_cases(model_path, out, seed, output_format, synth):
    def result(code, *, error=None, manifest=None, quarantine=None):
        if output_format == "json":
            payload = {"command": "synth", "exit_code": code}
            if error is not None:
                payload["error"] = error
            if manifest is not None:
                payload["manifest"] = str(Path(out) / manifest)
            if quarantine is not None:
                payload["quarantine"] = str(Path(out) / quarantine)
            emit(payload)
        elif error is not None:
            print(f"ERROR: {error}")
        else:
            print(f"OK: wrote {Path(out) / manifest}")
        return code

    try:
        model = load_model(model_path)
    except (OSError, ModelLoadError, ModelValidationError, ReferenceInputError, UnicodeDecodeError, YAMLError) as error:
        return result(EXIT_ILL_FORMED, error=str(error))
    index = ModelIndex.for_model(model)
    covers = list(index.role_object_types())
    constraints = list(index.iter_constraints_shared())
    if len(covers) > 256 or len(constraints) > 128:
        return result(
            EXIT_GENERATOR, error="guarded case model exceeds 256 fact types or 128 constraints"
        )
    try:
        transaction = _SynthCorpusTransaction(Path(out), fresh=True)
    except OSError as error:
        return result(EXIT_IO, error=str(error))
    seed = 0 if seed is None else seed
    rng = Random(seed)
    remaining = guarded_cases.RUN_WORK
    root = transaction.stage_root
    rules = []
    try:
        for ref, rule, fact_type in constraints:
            if rule["type"] != "guarded":
                continue
            cases = []
            row = {"rule_id": rule.get("id"), "constraint_ref": ref, "cases": cases, "reason": None}
            position = len(rules)
            rules.append(row)
            pair = None
            if row["rule_id"] is None:
                row["reason"] = "missing-id"
            elif remaining <= 0:
                row["reason"] = "search-limit"
            elif model.reference_populations or fact_type is not None:
                row["reason"] = "unsupported-shape"
            else:
                budget = _WorkBudget(limit=min(remaining, guarded_cases.GUARD_WORK))
                pair, row["reason"] = guarded_cases.build_pair(model, index, rule, rng, budget)
                remaining -= budget.used
            if pair is None:
                continue
            failing = "warning" if rule["modality"] == "deontic" else "fail"
            for case, kind, verdict, suffix in zip(
                pair, ("failing", "passing"), (failing, "pass"), ("fail", "pass"), strict=True
            ):
                relative = f"cases/{position:04d}.{suffix}.json"
                population, findings, expected, target = _confirm(
                    model, model_path, case.facts, covers, ref, verdict, case.binding_count
                )
                if expected != target:
                    quarantine = f"quarantine/{position:04d}.{suffix}.json"
                    _quarantine(
                        transaction,
                        quarantine,
                        {
                            "rule_id": row["rule_id"],
                            "constraint_ref": ref,
                            "model_digest": _digest(model),
                            "kind": kind,
                            "expected": expected,
                            "observed": target,
                            "population": population,
                        },
                    )
                    return result(
                        EXIT_QUARANTINE,
                        error="checker disagrees with guarded case",
                        quarantine=quarantine,
                    )
                _write(root, relative, population)
                cases.append(
                    {"kind": kind, "population": relative, **expected, "other_findings": findings}
                )

        if model.reference_populations:
            ordinary, code = {"reason": "reference-populations-unsupported"}, 0
        else:
            ordinary, code = _ordinary_corpus(model, constraints, root, seed, synth)
        if code == EXIT_QUARANTINE:
            move(root / "ordinary/corpus/quarantine", root / "quarantine")
            relative = "quarantine/ordinary.json"
            _quarantine(transaction, relative, ordinary)
            return result(
                code, error="ordinary synthesis disagrees with the checker", quarantine=relative
            )
        manifest = "guarded-cases.json"
        _write(
            root,
            manifest,
            {
                "schema_version": "gnd-guarded-cases/1",
                "model_digest": _digest(model),
                "seed": seed,
                "rules": rules,
                "ordinary": ordinary,
            },
        )
        transaction.commit()
    except PopulationLoadError as error:
        return result(
            EXIT_GENERATOR, error=f"generated guarded population did not validate: {error}"
        )
    except (InstallPathError, OSError) as error:
        return result(EXIT_IO, error=str(error))
    finally:
        transaction.abort()
    return result(0, manifest=manifest)
