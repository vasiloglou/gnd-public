from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from gnd import payloads as report_module
from gnd import safefs as install_module
from gnd import transition
from gnd.checker import CheckReport, check, check_with_anchors
from gnd.commands._output import (
    _band,
    _live_assurance,
    _print_issues,
    _print_projected_text,
    _print_report,
)
from gnd.exits import EXIT_INTERNAL, EXIT_IO
from gnd.extract.service import _artifact_index_issue, _extract_stem, _extraction_header_template
from gnd.model import ModelValidationError, ValidationIssue, load_model, structured_derivation_ids
from gnd.population import PopulationValidationError, load_population
from gnd.semantic_registry import capture_branches


def _cmd_verify(
    model_path: str,
    population_path: str,
    sidecar_path: str | None,
    artifacts_dir: str | None,
    no_extraction: bool,
    out: str | None,
    output_format: str,
    *,
    unredacted: bool = False,
) -> int:
    """``gnd verify MODEL POPULATION`` — the full derived verifier (R-03″).

    Composes popvalidate → check over a PRE-EXTRACTED population file. This
    command never calls a model and never orchestrates extraction: the
    skill-to-code handoff is a file on disk plus its sidecar (R-04‴). Its value
    over ``gnd check``: provenance on every verdict plus the always-present
    ``extraction`` metadata block — the extraction state is its OWN channel,
    kept separate from the checker outcome so a checker pass over an
    uncalibrated extraction can never read as proof of faithfulness (PANEL-2),
    and no fidelity rate ever appears in a verify payload (R-03″ hard rule).

    The extraction-state machine (R-13′) runs BEFORE the composition: a failed
    handoff is an ill-formed extraction at exit 3. ``skipped`` is written ONLY
    by the intentional ``--no-extraction`` opt-out; a missing or invalid
    sidecar is ``failed``, never skipped, never silently green (T-02.1-11).
    """
    import hashlib as _hashlib

    schema_version = 7
    model = None
    semantic_trace = set()
    structured = False
    # v5.1 Phase 3: one identity, computed once, reused by every later payload
    # this invocation emits. `None` until a model loads -- a pre-load error has
    # no model identity to claim, so it stays on the frozen version 3 rather
    # than fabricating one (§6.1).
    model_digest: str | None = None

    from gnd.extract.manifest import (
        ManifestError,
        open_manifest_relative_path,
        read_extraction_sidecar,
    )
    from gnd.population import MAX_POPULATION_BYTES, load_population_bytes
    from gnd.synth import paths as _paths

    #: Every schema key present on every verify exit path (state + reason +
    #: sidecar fields or nulls) — check/validate payloads keep `{}` (plan 01).
    extraction: dict[str, Any] = {
        "state": "failed",
        "reason": None,
        "sidecar": None,
        "population_sha256": None,
        "model_sha256": None,
        "projection_sha256": None,
        "document": None,
        "document_sha256": None,
        "skill": None,
        "skill_version": None,
        "executing_model": None,
    }
    verified_population_bytes: bytes | None = None
    verified_document_bytes: bytes | None = None
    verified_population_source: Path | None = None

    def active_redaction() -> bool:
        if model is None:
            return False
        from gnd.redaction import RedactionPolicy

        return RedactionPolicy.from_model(model).active

    def emit(
        exit_code: int,
        *,
        report: CheckReport | None = None,
        issues: list[ValidationIssue] | None = None,
        warnings: list[ValidationIssue] | None = None,
        error: BaseException | None = None,
    ) -> int:
        with capture_branches() as projection_trace:
            payload = report_module.build_verify_payload(
                exit_code,
                model_path,
                population_path,
                extraction=extraction,
                schema_version=schema_version,
                model_digest=model_digest,
                structured=structured,
                report=report,
                issues=issues,
                warnings=warnings,
                error=error,
            )
        if report is not None and model is not None:
            payload["assurance"] = _live_assurance(
                model,
                [population],
                report,
                exit_code,
                semantic_trace | projection_trace,
                extraction_route=("authenticated" if extraction["state"] == "ran" else "skipped"),
            ).as_dict()
        policy = None
        if model is not None:
            from gnd.redaction import (
                RedactionPolicy,
                RedactionProjectionError,
                project_failure,
                project_output,
            )

            policy = RedactionPolicy.from_model(model)
            try:
                if output_format == "json":
                    payload = project_output(
                        "verify",
                        payload,
                        policy=policy,
                        mode="unredacted" if unredacted else "applied",
                        emitter_id="cli-verify-json",
                    )
                else:
                    payload = project_output(
                        "verify",
                        payload,
                        policy=policy,
                        mode="unredacted" if unredacted else "applied",
                        emitter_id="cli-verify-text",
                    )
            except RedactionProjectionError:
                payload = report_module.build_verify_payload(
                    EXIT_INTERNAL,
                    model_path,
                    population_path,
                    extraction=extraction,
                    schema_version=schema_version,
                    model_digest=model_digest,
                    structured=structured,
                    error=RuntimeError("redaction projection failed"),
                )
                payload = project_failure(
                    "verify",
                    payload,
                    policy=policy,
                    mode="unredacted" if unredacted else "applied",
                )
                exit_code = EXIT_INTERNAL
        try:
            rendered = report_module.render_json(payload)
        except report_module.NonJsonValueError as failure:
            # CR-04 — the twin of _cmd_check's fallback, with the extraction
            # block preserved: the fallback carries no verdicts and no issues,
            # so it cannot itself trip the guard.
            payload = report_module.build_verify_payload(
                EXIT_INTERNAL,
                model_path,
                population_path,
                extraction=extraction,
                schema_version=schema_version,
                model_digest=model_digest,
                structured=structured,
                error=failure,
            )
            if policy is not None and policy.active:
                from gnd.redaction import project_failure

                payload = project_failure(
                    "verify",
                    payload,
                    policy=policy,
                    mode="unredacted" if unredacted else "applied",
                )
            rendered = report_module.render_json(payload)
            exit_code = EXIT_INTERNAL
        from gnd.assurance_transport import emit_receipt

        emit_receipt((rendered + "\n").encode("utf-8"))
        if out is not None:
            # The output path comes from argv ONLY, never from any file
            # content, and routes through the one traversal guard.
            try:
                destination = _paths.safe_output_path(Path(out).parent, Path(out).name)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(rendered + "\n", encoding="utf-8")
            except install_module.InstallPathError as failure:
                print(f"ERROR: refused output path: {failure}")
                return EXIT_IO
            except OSError as failure:
                print(f"ERROR: could not write {out}: {failure}")
                return EXIT_IO
        if output_format == "json":
            print(rendered)
        elif "redaction" in payload:
            _print_projected_text(payload)
        return exit_code

    # --- the extraction-state machine (R-13′), before the composition ---
    if no_extraction:
        extraction["state"] = "skipped"
        extraction["reason"] = "extraction opted out (--no-extraction)"
    else:
        resolved_sidecar = (
            Path(sidecar_path)
            if sidecar_path is not None
            else Path(population_path).with_suffix(".extraction.json")
        )
        extraction["sidecar"] = str(resolved_sidecar)
        if not resolved_sidecar.is_file():
            # ABSENCE IS FAILED, never skipped (R-13′/T-02.1-11): a silently
            # lost handoff file must not read as a deliberate opt-out.
            extraction["reason"] = (
                f"no extraction sidecar at {resolved_sidecar} and --no-extraction "
                f"not given — a missing measurement must not look green"
            )
            issue = ValidationIssue(
                path=str(resolved_sidecar),
                message=str(extraction["reason"]),
                rule_id="extraction:sidecar-missing",
            )
            if output_format != "json" and not active_redaction():
                _print_issues([issue])
            return emit(3, issues=[issue])
        try:
            sidecar = read_extraction_sidecar(resolved_sidecar)
        except ManifestError as error:
            extraction["reason"] = f"extraction sidecar is invalid: {error}"
            if output_format != "json" and not active_redaction():
                _print_issues(error.issues)
            return emit(3, issues=error.issues)

        if artifacts_dir is None:
            issue = ValidationIssue(
                path="projection_sha256",
                message=(
                    "--artifacts is required for an extraction handoff so "
                    "projection_sha256 can be verified against actual bytes"
                ),
                rule_id="extraction:binding-mismatch",
            )
            extraction["reason"] = issue.message
            if output_format != "json" and not active_redaction():
                _print_issues([issue])
            return emit(3, issues=[issue])

        projection_rel = f"{_extract_stem(model_path)}.projection.schema.json"
        bundle_issue = _artifact_index_issue(model_path, artifacts_dir, (projection_rel,))
        if bundle_issue is not None:
            _code, message = bundle_issue
            issue = ValidationIssue(
                path="projection_sha256",
                message=message,
                rule_id="extraction:binding-mismatch",
            )
            extraction["reason"] = message
            if output_format != "json" and not active_redaction():
                _print_issues([issue])
            return emit(3, issues=[issue])
        projection_path = Path(artifacts_dir) / (projection_rel)
        try:
            with open_manifest_relative_path(
                resolved_sidecar,
                sidecar.population,
                field="population",
                rule_id="extraction:binding-mismatch",
            ) as (resolved_population, population_stream):
                verified_population_bytes = population_stream.read(MAX_POPULATION_BYTES + 1)
            with open_manifest_relative_path(
                resolved_sidecar,
                sidecar.document,
                field="document",
                rule_id="extraction:binding-mismatch",
            ) as (_document_path, document_stream):
                from gnd.extract.anchors import MAX_DOCUMENT_BYTES

                document_digest = _hashlib.sha256()
                retained_document = bytearray()
                while chunk := document_stream.read(64 * 1024):
                    document_digest.update(chunk)
                    if len(retained_document) <= MAX_DOCUMENT_BYTES:
                        retained_document.extend(chunk[:MAX_DOCUMENT_BYTES + 1 - len(retained_document)])
                verified_document_bytes = bytes(retained_document)
            verified_population_source = resolved_population
            if resolved_population != Path(population_path).resolve(strict=True):
                raise ManifestError(
                    "the sidecar population does not name the POPULATION argument",
                    [
                        ValidationIssue(
                            path="population",
                            message=(
                                f"sidecar resolves population to {resolved_population}, "
                                f"but argv names {Path(population_path).resolve(strict=True)}"
                            ),
                            rule_id="extraction:binding-mismatch",
                        )
                    ],
                )
        except (ManifestError, OSError, ValueError) as error:
            issues = (
                error.issues
                if isinstance(error, ManifestError)
                else [
                    ValidationIssue(
                        path="population",
                        message=f"sidecar paths could not be verified: {error}",
                        rule_id="extraction:binding-mismatch",
                    )
                ]
            )
            extraction["reason"] = "sidecar path binding failed: " + "; ".join(
                issue.message for issue in issues
            )
            if output_format != "json" and not active_redaction():
                _print_issues(issues)
            return emit(3, issues=issues)

        # C6 binding (the measure precedent, T-02.1-10): recompute and compare
        # every digest the sidecar publishes against the actual bytes on disk.
        binding_issues: list[ValidationIssue] = []
        digests: dict[str, str] = {}
        for field, path in (
            ("model_sha256", Path(model_path)),
            ("projection_sha256", projection_path),
        ):
            try:
                digests[field] = _hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError as error:
                binding_issues.append(
                    ValidationIssue(
                        path=field,
                        message=(
                            f"the sidecar's {field} cannot be verified: {path} "
                            f"could not be read ({error})"
                        ),
                        rule_id="extraction:binding-mismatch",
                    )
                )
        assert verified_population_bytes is not None
        digests["population_sha256"] = _hashlib.sha256(verified_population_bytes).hexdigest()
        digests["document_sha256"] = document_digest.hexdigest()
        for field in (
            "population_sha256",
            "model_sha256",
            "projection_sha256",
            "document_sha256",
        ):
            recorded = getattr(sidecar, field)
            actual = digests.get(field)
            if actual is not None and actual != recorded:
                binding_issues.append(
                    ValidationIssue(
                        path=field,
                        message=(
                            f"the sidecar records {field}={recorded} but the "
                            f"file's bytes hash to {actual} — the population "
                            f"is not the extraction this sidecar describes (C6)"
                        ),
                        rule_id="extraction:binding-mismatch",
                    )
                )
        if binding_issues:
            extraction["reason"] = "sidecar binding mismatch: " + "; ".join(
                issue.message for issue in binding_issues
            )
            if output_format != "json" and not active_redaction():
                _print_issues(binding_issues)
            return emit(3, issues=binding_issues)

        extraction.update(
            state="ran",
            reason=None,
            population_sha256=sidecar.population_sha256,
            model_sha256=sidecar.model_sha256,
            projection_sha256=sidecar.projection_sha256,
            document=sidecar.document,
            document_sha256=sidecar.document_sha256,
            skill=sidecar.skill,
            skill_version=sidecar.skill_version,
            executing_model=sidecar.executing_model,
        )

    # --- the existing composition: popvalidate → check → band (R-03″) ---
    try:
        model = load_model(model_path)
    except ModelValidationError as error:
        if output_format != "json" and not active_redaction():
            for warning in error.warnings:
                print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")
            _print_issues(error.issues)
        return emit(3, issues=error.issues, warnings=error.warnings)
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        if output_format != "json" and not active_redaction():
            print(f"ERROR: {error}")
        return emit(3, error=error)

    structured = bool(structured_derivation_ids(model))
    model_digest = transition.transition_model_identity(model)

    try:
        # model= runs layer-2 model-relative validation and stamps the marker
        # check() requires — no flag disables it (D-18), exactly as in check.
        if verified_population_bytes is None:
            population = load_population(population_path, model=model)
        else:
            assert verified_population_source is not None
            population = load_population_bytes(
                verified_population_bytes,
                source=verified_population_source,
                model=model,
            )
    except PopulationValidationError as error:
        warnings = [*model.warnings, *error.warnings]
        if output_format != "json" and not active_redaction():
            for warning in warnings:
                print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")
            _print_issues(error.issues)
        return emit(3, issues=error.issues, warnings=warnings)
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        if output_format != "json" and not active_redaction():
            print(f"ERROR: {error}")
        return emit(3, error=error)

    if extraction["state"] == "ran":
        # PANEL-6 header ownership: compare the complete header to the SAME
        # deterministic template owner used by `gnd extract`. General
        # population validation intentionally permits labels and treats an
        # omitted model_id as a warning, but neither is permitted on this
        # stricter agent-extraction handoff.
        expected_header = _extraction_header_template(model_path, model)
        actual_header: dict[str, Any] = {
            "model": population.model,
            "source": population.source,
            "covers": population.covers,
        }
        if population.model_id is not None:
            actual_header["model_id"] = population.model_id
        if population.label is not None:
            actual_header["label"] = population.label
        header_issues: list[ValidationIssue] = []
        if actual_header != expected_header:
            header_issues.append(
                ValidationIssue(
                    path="population",
                    message=(
                        "the extraction population header must equal the "
                        "deterministic header_template key for key; expected "
                        f"{expected_header!r}, got {actual_header!r}"
                    ),
                    rule_id="extraction:header-mismatch",
                )
            )
        if header_issues:
            extraction["state"] = "failed"
            extraction["reason"] = "header ownership violated (PANEL-6): " + "; ".join(
                issue.message for issue in header_issues
            )
            if output_format != "json" and not active_redaction():
                _print_issues(header_issues)
            return emit(
                3,
                issues=header_issues,
                warnings=[*model.warnings, *population.warnings],
            )

    try:
        with capture_branches() as semantic_trace:
            from gnd.extract.anchors import (
                AnchorError,
                bind_anchors,
                read_anchor_sidecar,
                read_regular_path,
            )
            anchor_path = Path(str(population_path) + ".anchors.json")
            if os.path.lexists(anchor_path):
                anchor_sidecar = read_anchor_sidecar(anchor_path)
                if extraction["state"] != "ran" or verified_document_bytes is None:
                    raise AnchorError("anchor:binding-mismatch: verified document bytes unavailable")
                document_raw = verified_document_bytes
                if verified_population_bytes is None:
                    population_file = Path(population_path)
                    verified_population_bytes = read_regular_path(
                        population_file, label="anchor population", max_bytes=MAX_POPULATION_BYTES,
                    )
                bind_anchors(anchor_sidecar, model, verified_population_bytes, document_raw, population)
                report = check_with_anchors(
                    model, population, anchors=anchor_sidecar, document_bytes=document_raw,
                )
            else:
                report = check(model, population)
            exit_code = _band(report)
    except AnchorError as error:
        return emit(3, error=error)
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        if output_format != "json" and not active_redaction():
            print(f"INTERNAL ERROR: {type(error).__name__}: {error}")
        return emit(EXIT_INTERNAL, error=error)

    # One band decision, delegated to the ONE owner — never re-derived here.
    warnings = [*model.warnings, *population.warnings]

    if output_format != "json" and not active_redaction():
        for warning in warnings:
            print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")
        state = extraction["state"]
        reason = f" ({extraction['reason']})" if extraction["reason"] else ""
        print(f"EXTRACTION: state={state}{reason}")
        _print_report(report)
    return emit(exit_code, report=report, warnings=warnings)

_cmd_verify.__module__ = "gnd.cli"
