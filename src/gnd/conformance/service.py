"""Reusable orchestration for one live conformance run.

The command-line controller renders the raw payload returned here; evolution and
other programmatic callers consume the same payload directly.  Keeping the run
in this module gives every entry point identical partial-run and exit-precedence
semantics without making a service import :mod:`gnd.cli` or parse rendered prose.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from gnd import resolve_version
from gnd.artifacts import ArtifactError, read_regular_bounded_at
from gnd.codegen.manifest import (
    MAX_CODEGEN_MANIFEST_BYTES,
    CodegenManifestError,
    read_manifest_bytes,
)
from gnd.conformance import ConformanceError
from gnd.conformance.architecture import check_architecture
from gnd.conformance.currency import check_currency, model_file_sha256
from gnd.conformance.integrity import bind_project_root, check_integrity, open_project_root
from gnd.conformance.report import build_conformance_payload
from gnd.conformance.structural import check_structural
from gnd.exits import EXIT_ILL_FORMED, EXIT_IO, EXIT_MODEL_CODE_DRIFT, EXIT_NO_INPUT
from gnd.model import ModelLoadError, ModelValidationError, load_model

__all__ = ["ConformanceServiceResult", "run_conformance"]

_EXIT_ILL_FORMED = EXIT_ILL_FORMED
_EXIT_MODEL_CODE_DRIFT = EXIT_MODEL_CODE_DRIFT
_EXIT_NO_INPUT = EXIT_NO_INPUT
_EXIT_IO = EXIT_IO


@dataclass(frozen=True, slots=True)
class ConformanceServiceResult:
    """The raw conformance claim and its command-wide process exit code."""

    payload: dict[str, Any]
    exit_code: int


def _conformance_outcome(
    io_failures: list[str],
    missing_artifacts: list[str],
    unreadable_records: list[str],
    findings: list[str],
) -> int:
    """Select the one run-wide band with precedence ``74 > 66 > 3 > 13 > 0``."""
    if io_failures:
        return _EXIT_IO
    if missing_artifacts:
        return _EXIT_NO_INPUT
    if unreadable_records:
        return _EXIT_ILL_FORMED
    if findings:
        return _EXIT_MODEL_CODE_DRIFT
    return 0


def run_conformance(model_path: str | Path, project_root: str | Path) -> ConformanceServiceResult:
    """Run all four conformance assertions without rendering.

    Assertions retain their partial results when a later assertion cannot run.
    The payload's per-assertion ``ran`` fields say exactly which work completed;
    ``exit_code`` applies the published precedence to the run as a whole.
    """
    root = Path(project_root)
    from gnd.terms import uses_temporal

    try:
        temporal_model = load_model(model_path)
    except (OSError, ModelLoadError, ModelValidationError):
        temporal_model = None  # Preserve the existing missing/invalid-input precedence.
    if temporal_model is not None and uses_temporal(temporal_model):
        payload = build_conformance_payload(
            model_path,
            None,
            None,
            None,
            actual_model_sha256=None,
            gnd_version=resolve_version(),
            error="conformance does not support temporal models in Phase 1",
        )
        return ConformanceServiceResult(payload, _EXIT_ILL_FORMED)
    model_coordinate = Path(model_path).name
    manifest_coordinate = ".gnd-codegen.json"
    project_coordinate = "generated project"

    io_failures: list[str] = []
    missing_artifacts: list[str] = []
    unreadable_records: list[str] = []
    errors_by_band: dict[int, list[str]] = {
        _EXIT_IO: [],
        _EXIT_NO_INPUT: [],
        _EXIT_ILL_FORMED: [],
    }

    def record_error(band: int, message: str) -> None:
        errors_by_band[band].append(message)

    manifest = None
    integrity = None
    currency = None
    structural = None
    architecture = None
    actual_model_sha256 = None
    loaded_model = None
    root_identity: tuple[int, int] | None = None
    root_fd = -1

    try:
        root_fd = open_project_root(root)
        opened_root = os.fstat(root_fd)
        root_identity = opened_root.st_dev, opened_root.st_ino
    except ConformanceError:
        io_failures.append(project_coordinate)
        record_error(
            _EXIT_IO,
            f"the {project_coordinate} root could not be bound (cause: root-open)",
        )

    try:
        if root_fd >= 0:
            try:
                manifest_bytes, _manifest_snapshot = read_regular_bounded_at(
                    root_fd,
                    manifest_coordinate,
                    max_bytes=MAX_CODEGEN_MANIFEST_BYTES,
                )
            except ArtifactError as artifact_error:
                cause: BaseException | None = artifact_error
                while cause is not None and not isinstance(cause, FileNotFoundError):
                    cause = cause.__cause__
                if isinstance(cause, FileNotFoundError):
                    missing_artifacts.append(manifest_coordinate)
                    record_error(
                        _EXIT_NO_INPUT,
                        f"{manifest_coordinate} is missing from the {project_coordinate}, "
                        f"so no comparison was performed at all (cause: missing-manifest). "
                        f"Run `gnd codegen {model_coordinate} --out <project-root>` first",
                    )
                else:
                    io_failures.append(manifest_coordinate)
                    record_error(
                        _EXIT_IO,
                        f"{manifest_coordinate} could not be read without following links "
                        f"(cause: manifest-io)",
                    )
            else:
                try:
                    manifest = read_manifest_bytes(
                        manifest_bytes,
                        source=manifest_coordinate,
                    )
                except CodegenManifestError:
                    unreadable_records.append(manifest_coordinate)
                    record_error(
                        _EXIT_ILL_FORMED,
                        f"{manifest_coordinate} is not a valid codegen manifest, so no "
                        f"comparison was performed at all (cause: invalid-manifest)",
                    )

        if manifest is not None and root_fd >= 0:
            integrity_ran = False
            try:
                integrity = check_integrity(
                    root,
                    manifest,
                    expected_root=root_identity,
                    root_fd=root_fd,
                )
                integrity_ran = True
            except ConformanceError:
                io_failures.append(project_coordinate)
                record_error(
                    _EXIT_IO,
                    f"the {project_coordinate} integrity assertion could not run (cause: file-io)",
                )

            if not Path(model_path).is_file():
                missing_artifacts.append(model_coordinate)
                record_error(
                    _EXIT_NO_INPUT,
                    f"{model_coordinate} is missing, so currency, structural and architecture "
                    f"checks could not run (cause: missing-model). A model that is "
                    f"gone is not a model that moved",
                )
            else:
                try:
                    actual_model_sha256 = model_file_sha256(model_path)
                    currency = check_currency(model_path, manifest)
                except ConformanceError:
                    io_failures.append(model_coordinate)
                    record_error(
                        _EXIT_IO,
                        f"{model_coordinate} could not be read for the currency "
                        f"assertion (cause: model-io)",
                    )

                try:
                    loaded_model = (
                        temporal_model if temporal_model is not None else load_model(model_path)
                    )
                    structural = check_structural(
                        loaded_model,
                        root,
                        manifest,
                        model_path=model_path,
                        root_fd=root_fd,
                    )
                except (ModelLoadError, ModelValidationError):
                    unreadable_records.append(model_coordinate)
                    record_error(
                        _EXIT_ILL_FORMED,
                        f"{model_coordinate} did not load (cause: invalid-model), "
                        f"so the structural assertion could not run — this is NOT "
                        f"a conformance finding, and nothing was established about "
                        f"the {project_coordinate} in either direction",
                    )
                except ConformanceError:
                    io_failures.append(project_coordinate)
                    record_error(
                        _EXIT_IO,
                        f"the {project_coordinate} structural assertion could not "
                        f"run (cause: structural-io)",
                    )

                if loaded_model is not None:
                    try:
                        architecture = check_architecture(
                            loaded_model,
                            root,
                            manifest,
                            model_path=model_path,
                            root_fd=root_fd,
                        )
                    except ConformanceError:
                        io_failures.append(project_coordinate)
                        record_error(
                            _EXIT_IO,
                            f"the {project_coordinate} architecture assertion "
                            f"could not run (cause: architecture-io)",
                        )

            try:
                bind_project_root(root, expected=root_identity)
            except ConformanceError:
                io_failures.append(project_coordinate)
                record_error(
                    _EXIT_IO,
                    f"the {project_coordinate} root changed during conformance (cause: root-race)",
                )

            # The lexical rebind is not itself a commit point: it proves only
            # the root inode.  Re-run the complete descriptor-bound structural
            # walk after it (including every directory identity) and finish
            # with every derived leaf digest.  A mutation performed at the
            # rebind seam therefore becomes drift or IO, never a green payload.
            if structural is not None and loaded_model is not None:
                try:
                    reconciled_structural = check_structural(
                        loaded_model,
                        root,
                        manifest,
                        model_path=model_path,
                        root_fd=root_fd,
                    )
                    retained_findings = tuple(
                        dict.fromkeys((*structural.findings, *reconciled_structural.findings))
                    )
                    structural = replace(
                        reconciled_structural,
                        findings=retained_findings,
                    )
                except ConformanceError:
                    io_failures.append(project_coordinate)
                    record_error(
                        _EXIT_IO,
                        f"the {project_coordinate} final structural reconciliation "
                        f"could not run (cause: structural-io)",
                    )

            if architecture is not None and loaded_model is not None:
                try:
                    reconciled_architecture = check_architecture(
                        loaded_model,
                        root,
                        manifest,
                        model_path=model_path,
                        root_fd=root_fd,
                    )
                    retained_findings = tuple(
                        dict.fromkeys((*architecture.findings, *reconciled_architecture.findings))
                    )
                    architecture = replace(
                        reconciled_architecture,
                        findings=retained_findings,
                    )
                except ConformanceError:
                    io_failures.append(project_coordinate)
                    record_error(
                        _EXIT_IO,
                        f"the {project_coordinate} final architecture reconciliation "
                        f"could not run (cause: architecture-io)",
                    )

            if integrity_ran:
                try:
                    integrity = check_integrity(
                        root,
                        manifest,
                        expected_root=root_identity,
                        root_fd=root_fd,
                    )
                except ConformanceError:
                    io_failures.append(project_coordinate)
                    record_error(
                        _EXIT_IO,
                        f"the {project_coordinate} final derived-leaf reconciliation "
                        f"could not run (cause: file-io)",
                    )
    finally:
        if root_fd >= 0:
            os.close(root_fd)

    findings = [
        *(finding.target for finding in (integrity.findings if integrity else ())),
        *(finding.target for finding in (currency or ())),
        *(finding.target for finding in (structural.findings if structural else ())),
        *(finding.target for finding in (architecture.findings if architecture else ())),
    ]

    exit_code = _conformance_outcome(
        io_failures,
        missing_artifacts,
        unreadable_records,
        findings,
    )
    selected_errors = errors_by_band.get(exit_code, [])
    error = " | ".join(selected_errors) if selected_errors else None
    payload = build_conformance_payload(
        model_path,
        manifest,
        integrity,
        currency,
        structural=structural,
        architecture=architecture,
        actual_model_sha256=actual_model_sha256,
        gnd_version=resolve_version(),
        error=error,
    )
    return ConformanceServiceResult(payload=payload, exit_code=exit_code)


model_digest = model_file_sha256  # RF2 compatibility alias.
