from __future__ import annotations

import json  # noqa: F401 -- historical compatibility binding
from pathlib import Path
from typing import Any

from gnd import input_policy as _rf7_input
from gnd import resolve_version, verbalize
from gnd import safefs as install_module
from gnd.exits import EXIT_INTERNAL, EXIT_IO, EXIT_NO_INPUT, EXIT_USAGE
from gnd.extract.service import _artifact_index_issue, _extract_stem
from gnd.model import ModelValidationError, load_model
from gnd.output import _print_issues
from gnd.population import PopulationValidationError, load_population

_CASE_SOURCE = "source.population.json"

_CASE_DOCUMENT = "document.md"

_CASE_MANIFEST = "document.manifest.json"

_CASE_EXTRACTED = "extracted.population.json"

_CASE_SIDECAR = "extracted.population.extraction.json"

_CASE_SKIPPED = "extraction.skipped.json"

def _cmd_fidelity(
    model_path: str,
    cases_dir: str,
    artifacts_dir: str,
    out: str | None,
    output_format: str,
) -> int:
    """``gnd fidelity MODEL --cases DIR --artifacts DIR`` — extractor fidelity
    per fact type (SC3).

    **This command emits RATES and never a per-run verdict.** It is R-03″'s
    dual: ``gnd verify`` answers "does this population satisfy the model" and
    carries no rate; ``gnd fidelity`` answers "does this extraction reflect its
    document" and carries no verdict, no band and no ``acceptance_ready``. A
    single output carrying both invites reading either as the other, which is
    exactly the conflation PANEL-2 corrected.

    Fail-closed on its inputs. The applicable-set artifact DEFINES the row set
    and therefore every denominator, so its absence is exit 66 rather than a
    run over "whatever fact types happened to appear" — a missing artifact must
    never read as coverage. A case whose recorded digest does not describe the
    bytes on disk is exit 3: that is a tamper signal, not a census state.

    The census is R-13′'s: ``ran`` cases produce the rates, ``skipped`` (the
    intentional ``extraction.skipped.json`` marker) and ``failed`` (anything
    else, with its reason) are counted beside them and folded into no
    denominator anywhere.

    Exits 0 with the report, 3 on a binding mismatch inside a case, 64 on usage
    errors or a case set spanning more than one model, 66 when a required
    artifact is missing, 70 on an internal contract breach (a broken matcher
    partition or a payload its own schema rejects), 74 when the output path is
    refused or unwritable.
    """
    import hashlib as _hashlib

    from jsonschema import Draft202012Validator
    from jsonschema import ValidationError as SchemaValidationError

    from gnd.extract.manifest import (
        ManifestError,
        read_document_manifest,
        read_extraction_sidecar,
        read_extraction_skip_marker,
    )
    from gnd.extract.refscheme import applicable_set
    from gnd.fidelity.match import FidelityPartitionError, match_case
    from gnd.fidelity.report import (
        CaseOutcome,
        build_fidelity_payload,
        canonical,
        load_fidelity_schema,
        render_fidelity,
    )
    from gnd.synth import paths as _paths

    try:
        model = load_model(model_path)
    except ModelValidationError as error:
        for warning in error.warnings:
            print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")
        _print_issues(error.issues)
        return 3
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"ERROR: {error}")
        return 3

    stem = _extract_stem(model_path)
    artifacts_root = Path(artifacts_dir)
    applicable_path = artifacts_root / f"{stem}.applicable.json"
    projection_path = artifacts_root / f"{stem}.projection.schema.json"

    bundle_issue = _artifact_index_issue(
        model_path,
        artifacts_dir,
        (f"{stem}.applicable.json", f"{stem}.projection.schema.json"),
    )
    if bundle_issue is not None:
        code, message = bundle_issue
        print(f"VIOLATION artifact-index: {verbalize.line_text(message)}")
        return code

    # Fail closed (66, the D-22/doccheck EX_NOINPUT precedent): the applicable
    # set is the denominator's definition and the projection is what the
    # extraction decoded against. A missing one means the number cannot be
    # computed, never that it is 1.0.
    for label, required in (
        ("applicable-set artifact", applicable_path),
        ("projection artifact", projection_path),
    ):
        if not required.is_file():
            print(
                f"MISSING: the {label} at {required} does not exist — the "
                f"applicable set defines every denominator, so a run without "
                f"it would read as coverage it never had ({EXIT_NO_INPUT})"
            )
            return EXIT_NO_INPUT

    try:
        applicable_bytes = applicable_path.read_bytes()
        applicable = _rf7_input.loads(applicable_bytes.decode("utf-8"))
        if applicable != applicable_set(model):
            print(
                "VIOLATION applicable-set: artifact does not match the "
                "canonical disposition derived from this model"
            )
            return 3
        declared_fact_types = {str(row["id"]) for row in applicable["fact_types"]}
        applicable_sha256 = _hashlib.sha256(applicable_bytes).hexdigest()
        projection_sha256 = _hashlib.sha256(projection_path.read_bytes()).hexdigest()
        model_sha256 = _hashlib.sha256(Path(model_path).read_bytes()).hexdigest()
    except (OSError, UnicodeDecodeError, ValueError, KeyError, TypeError) as error:
        print(f"ERROR: the extraction artifacts are not readable ({error})")
        return 3

    cases_root = Path(cases_dir)
    if not cases_root.is_dir():
        print(f"ERROR: --cases {cases_dir} is not a directory")
        return EXIT_USAGE
    case_dirs = sorted(path for path in cases_root.iterdir() if path.is_dir())
    if not case_dirs:
        print(
            f"ERROR: no case directories under {cases_dir} — an empty case set "
            f"produces no rates, and a payload over zero cases would read as a "
            f"measurement (64)"
        )
        return EXIT_USAGE

    # --- pass 1: classify every case; collect the model digests it claims ---
    outcomes: list[CaseOutcome] = []
    candidates: list[tuple[Path, Any, Any]] = []
    claimed_digests: set[str] = set()

    for case_dir in case_dirs:
        name = case_dir.name
        skipped_marker = case_dir / _CASE_SKIPPED
        extracted_path = case_dir / _CASE_EXTRACTED
        if skipped_marker.is_file():
            if extracted_path.is_file():
                outcomes.append(
                    CaseOutcome(
                        name,
                        "failed",
                        reason=(
                            f"{_CASE_SKIPPED} and {_CASE_EXTRACTED} are both "
                            f"present — an opt-out beside an extraction is a "
                            f"contradiction, not a skip"
                        ),
                    )
                )
                continue
            try:
                reason = read_extraction_skip_marker(skipped_marker).reason
            except ManifestError:
                outcomes.append(
                    CaseOutcome(
                        name,
                        "failed",
                        reason=(
                            f"{_CASE_SKIPPED} carries no readable 'reason' — a "
                            f"skip without a stated reason is indistinguishable "
                            f"from a lost file (R-13')"
                        ),
                    )
                )
                continue
            outcomes.append(CaseOutcome(name, "skipped", reason=reason))
            continue

        missing = [
            rel
            for rel in (
                _CASE_SOURCE,
                _CASE_DOCUMENT,
                _CASE_MANIFEST,
                _CASE_EXTRACTED,
                _CASE_SIDECAR,
            )
            if not (case_dir / rel).is_file()
        ]
        if missing:
            # ABSENCE IS FAILED, never skipped (R-13'/T-02.1-11).
            outcomes.append(
                CaseOutcome(
                    name,
                    "failed",
                    reason=(
                        f"the case is incomplete: {', '.join(missing)} missing "
                        f"and no {_CASE_SKIPPED} opt-out marker"
                    ),
                )
            )
            continue

        try:
            sidecar = read_extraction_sidecar(case_dir / _CASE_SIDECAR)
            manifest = read_document_manifest(case_dir / _CASE_MANIFEST)
        except ManifestError as error:
            outcomes.append(CaseOutcome(name, "failed", reason=f"handoff file invalid: {error}"))
            continue

        claimed_digests.add(sidecar.model_sha256)
        claimed_digests.add(manifest.model_sha256)
        candidates.append((case_dir, sidecar, manifest))

    # C4's analog, checked BEFORE any per-case binding: one payload represents
    # exactly one model, and "these cases are about different models" is a
    # usage error, not a tampered file.
    if len(claimed_digests) > 1:
        print(
            f"ERROR: the case set spans {len(claimed_digests)} model digest(s); "
            f"gnd fidelity is model-relative and one payload represents exactly "
            f"one model (C4). Split the cases and measure each model separately."
        )
        return EXIT_USAGE

    # --- pass 2: bind, load and match the candidate cases ---
    for case_dir, sidecar, manifest in candidates:
        name = case_dir.name
        source_path = case_dir / _CASE_SOURCE
        document_path = case_dir / _CASE_DOCUMENT
        extracted_path = case_dir / _CASE_EXTRACTED
        try:
            source_bytes = source_path.read_bytes()
            document_bytes = document_path.read_bytes()
            extracted_bytes = extracted_path.read_bytes()
        except OSError as error:
            outcomes.append(
                CaseOutcome(name, "failed", reason=f"a case file is unreadable: {error}")
            )
            continue

        source_sha256 = _hashlib.sha256(source_bytes).hexdigest()
        document_sha256 = _hashlib.sha256(document_bytes).hexdigest()
        extracted_sha256 = _hashlib.sha256(extracted_bytes).hexdigest()

        # C6 inside the case, in BOTH directions: the sidecar binds the
        # extraction to the model and the document it read, and the manifest
        # binds that document to the source population it was rendered from.
        # Without the second half a case could score an extraction of one
        # document against an unrelated source population and read clean.
        mismatches = [
            (field, recorded, actual)
            for field, recorded, actual in (
                ("sidecar.population_sha256", sidecar.population_sha256, extracted_sha256),
                ("sidecar.model_sha256", sidecar.model_sha256, model_sha256),
                ("sidecar.document_sha256", sidecar.document_sha256, document_sha256),
                (
                    "sidecar.projection_sha256",
                    sidecar.projection_sha256,
                    projection_sha256,
                ),
                ("manifest.document_sha256", manifest.document_sha256, document_sha256),
                (
                    "manifest.source_population_sha256",
                    manifest.source_population_sha256,
                    source_sha256,
                ),
                ("manifest.applicable_sha256", manifest.applicable_sha256, applicable_sha256),
            )
            if recorded != actual
        ]
        if mismatches:
            for field, recorded, actual in mismatches:
                print(
                    f"VIOLATION binding: {verbalize.path_segment(name)}/"
                    f"{verbalize.path_segment(field)} records "
                    f"{verbalize.path_segment(recorded)} but the bytes hash to "
                    f"{verbalize.path_segment(actual)} — this is not the artifact the "
                    f"handoff describes (C6)"
                )
            return 3

        try:
            source_population = load_population(source_path, model=model)
            extracted_population = load_population(extracted_path, model=model)
        except PopulationValidationError as error:
            outcomes.append(
                CaseOutcome(
                    name,
                    "failed",
                    reason=(
                        "a population failed model-relative validation: "
                        + "; ".join(issue.message for issue in error.issues[:3])
                    ),
                )
            )
            continue
        except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
            outcomes.append(
                CaseOutcome(name, "failed", reason=f"a population failed to load: {error}")
            )
            continue

        undeclared = sorted(
            (set(source_population.facts) | set(extracted_population.facts)) - declared_fact_types
        )
        if undeclared:
            outcomes.append(
                CaseOutcome(
                    name,
                    "failed",
                    reason=(
                        f"fact type(s) {undeclared} appear in a population but "
                        f"not in the applicable-set artifact, so no row could "
                        f"account for them"
                    ),
                )
            )
            continue

        try:
            matches = match_case(
                source_population.facts,
                extracted_population.facts,
                model=model,
                applicable=applicable,
            )
        except FidelityPartitionError as error:
            # The matcher's own invariant, breached over inputs that already
            # loaded clean: gnd's accounting, never the caller's data.
            print(f"INTERNAL ERROR: {error}")
            return EXIT_INTERNAL

        outcomes.append(
            CaseOutcome(
                name,
                "ran",
                matches=matches,
                source_sha256=source_sha256,
                extracted_sha256=extracted_sha256,
                document_sha256=document_sha256,
                source_facts=source_population.facts,
                extracted_facts=extracted_population.facts,
            )
        )

    payload = build_fidelity_payload(
        model_path,
        outcomes,
        applicable,
        model_sha256=model_sha256,
        applicable_sha256=applicable_sha256,
        projection_sha256=projection_sha256,
        gnd_version=resolve_version(),
    )

    # Validated before emission: a payload its own contract rejects is an
    # internal breach (70), not a report a consumer should have to police.
    try:
        Draft202012Validator(load_fidelity_schema()).validate(payload)
        rendered = canonical(payload)
    except (SchemaValidationError, ValueError) as error:
        print(f"INTERNAL ERROR: the fidelity payload violates its own schema: {error}")
        return EXIT_INTERNAL

    if out is not None:
        # The output path comes from argv ONLY, never from any case content,
        # and routes through the one traversal guard.
        try:
            destination = _paths.safe_output_path(Path(out).parent, Path(out).name)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(rendered + "\n", encoding="utf-8")
        except install_module.InstallPathError as error:
            print(f"ERROR: refused output path: {error}")
            return EXIT_IO
        except OSError as error:
            print(f"ERROR: could not write {out}: {error}")
            return EXIT_IO

    if output_format == "json":
        print(rendered)
    else:
        print(render_fidelity(payload))
    return 0

_cmd_fidelity.__module__ = "gnd.cli"
