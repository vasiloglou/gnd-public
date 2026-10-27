from __future__ import annotations

import json
import stat
import sys
from pathlib import Path
from typing import Any

from gnd.exits import (
    EXIT_COLLISION,
    EXIT_EVOLUTION_OPERATIONS_GATED,
    EXIT_INTERNAL,
    EXIT_IO,
    EXIT_NO_INPUT,
)
from gnd.model import ModelValidationError


class _EvolutionCLIError(Exception):
    """One closed public evolution exit before a service stage can run."""

    def __init__(self, exit_code: int, message: str) -> None:
        super().__init__(message)
        self.exit_code = exit_code

_EVOLUTION_CLAIM_MAX_BYTES = 10 * 1024 * 1024

def _evolve_reject_unsafe_spelling(value: str, *, label: str) -> None:
    from pathlib import PurePosixPath, PureWindowsPath

    if not value or "\x00" in value:
        raise _EvolutionCLIError(EXIT_IO, f"{label} is empty or contains a NUL byte")
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    if ".." in posix.parts or ".." in windows.parts:
        raise _EvolutionCLIError(EXIT_IO, f"{label} contains a refused '..' component")
    if windows.drive and not windows.is_absolute():
        raise _EvolutionCLIError(EXIT_IO, f"{label} is a refused drive-relative path")

def _evolve_absolute_path(value: str, *, label: str) -> Path:
    _evolve_reject_unsafe_spelling(value, label=label)
    supplied = Path(value)
    return supplied if supplied.is_absolute() else Path.cwd() / supplied

def _evolve_reject_existing_symlinks(path: Path, *, label: str) -> None:
    """Reject every existing symlink component in one argv-supplied path."""

    current = Path(path.anchor)
    parts = path.parts[1:] if path.anchor else path.parts
    for part in parts:
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            return
        except OSError as error:
            raise _EvolutionCLIError(
                EXIT_IO, f"{label} could not be inspected at {current}: {error}"
            ) from error
        if stat.S_ISLNK(info.st_mode):
            raise _EvolutionCLIError(EXIT_IO, f"{label} crosses symlink {current}")

def _evolve_workspace(value: str) -> Path:
    workspace = _evolve_absolute_path(value, label="workspace")
    _evolve_reject_existing_symlinks(workspace, label="workspace")
    try:
        info = workspace.lstat()
    except FileNotFoundError as error:
        raise _EvolutionCLIError(EXIT_NO_INPUT, f"workspace {workspace} does not exist") from error
    except OSError as error:
        raise _EvolutionCLIError(
            EXIT_IO, f"workspace {workspace} could not be inspected: {error}"
        ) from error
    if not stat.S_ISDIR(info.st_mode):
        raise _EvolutionCLIError(EXIT_IO, f"workspace {workspace} is not a real directory")
    try:
        return workspace.resolve(strict=True)
    except OSError as error:
        raise _EvolutionCLIError(
            EXIT_IO, f"workspace {workspace} could not be resolved: {error}"
        ) from error

def _evolve_rooted_path(
    root: Path,
    value: str,
    *,
    root_label: str,
    label: str,
    required: bool,
    regular: bool = True,
) -> tuple[Path, str]:
    candidate = _evolve_absolute_path(value, label=label)
    try:
        relative = candidate.relative_to(root)
    except ValueError as error:
        raise _EvolutionCLIError(
            EXIT_IO, f"{label} {candidate} is outside {root_label} {root}"
        ) from error
    if not relative.parts:
        raise _EvolutionCLIError(EXIT_IO, f"{label} cannot be the {root_label}")

    current = root
    missing = False
    for part in relative.parts:
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            missing = True
            break
        except OSError as error:
            raise _EvolutionCLIError(
                EXIT_IO, f"{label} could not be inspected at {current}: {error}"
            ) from error
        if stat.S_ISLNK(info.st_mode):
            raise _EvolutionCLIError(EXIT_IO, f"{label} crosses symlink {current}")

    try:
        resolved = candidate.resolve(strict=False)
    except OSError as error:
        raise _EvolutionCLIError(
            EXIT_IO, f"{label} {candidate} could not be resolved: {error}"
        ) from error
    if not resolved.is_relative_to(root):
        raise _EvolutionCLIError(
            EXIT_IO, f"{label} {candidate} resolves outside {root_label} {root}"
        )
    if required and missing:
        raise _EvolutionCLIError(EXIT_NO_INPUT, f"required {label} {candidate} is missing")
    if required:
        try:
            info = candidate.lstat()
        except FileNotFoundError as error:
            raise _EvolutionCLIError(
                EXIT_NO_INPUT, f"required {label} {candidate} is missing"
            ) from error
        except OSError as error:
            raise _EvolutionCLIError(
                EXIT_IO, f"required {label} {candidate} could not be inspected: {error}"
            ) from error
        if regular and not stat.S_ISREG(info.st_mode):
            raise _EvolutionCLIError(EXIT_IO, f"required {label} {candidate} is not a regular file")
    return candidate, relative.as_posix()

def _evolve_workspace_path(
    workspace: Path,
    value: str,
    *,
    label: str,
    required: bool,
    regular: bool = True,
) -> tuple[Path, str]:
    return _evolve_rooted_path(
        workspace,
        value,
        root_label="workspace",
        label=label,
        required=required,
        regular=regular,
    )

def _evolve_records_root(value: str) -> Path:
    records = _evolve_absolute_path(value, label="records root")
    _evolve_reject_existing_symlinks(records, label="records root")
    try:
        info = records.lstat()
    except FileNotFoundError:
        pass
    except OSError as error:
        raise _EvolutionCLIError(
            EXIT_IO, f"records root {records} could not be inspected: {error}"
        ) from error
    else:
        if not stat.S_ISDIR(info.st_mode):
            raise _EvolutionCLIError(EXIT_IO, f"records root {records} is not a real directory")
    try:
        return records.resolve(strict=False)
    except OSError as error:
        raise _EvolutionCLIError(
            EXIT_IO, f"records root {records} could not be resolved: {error}"
        ) from error

def _evolve_read_claim(
    path: Path,
    model_type: Any,
    *,
    label: str,
    anchor: Path | None = None,
    relative: str | None = None,
) -> Any:
    from gnd.evolve import (
        EvolutionFinalizationState,
        EvolutionIntent,
        EvolutionPreview,
        EvolutionProposal,
        EvolutionRecord,
        read_evolution_finalization_state,
        read_evolution_intent,
        read_evolution_preview,
        read_evolution_proposal,
        read_evolution_record,
    )

    readers = {
        EvolutionFinalizationState: read_evolution_finalization_state,
        EvolutionIntent: read_evolution_intent,
        EvolutionPreview: read_evolution_preview,
        EvolutionProposal: read_evolution_proposal,
        EvolutionRecord: read_evolution_record,
    }
    reader = readers.get(model_type)
    if reader is None:
        raise _EvolutionCLIError(
            EXIT_INTERNAL,
            f"{label} has no claim-specific evolution reader",
        )
    try:
        return reader(path, anchor=anchor, relative=relative)
    except Exception as error:  # closed service refusal translation
        raise _EvolutionCLIError(
            _evolve_error_exit(error),
            f"{label} {path} is malformed: {error}",
        ) from error

def _evolve_validate_proposal_roots(proposal: Any) -> None:
    from pathlib import PurePosixPath, PureWindowsPath

    for project in proposal.linked_projects:
        raw = str(project.root)
        if "\x00" in raw or PurePosixPath(raw).is_absolute() or PureWindowsPath(raw).is_absolute():
            raise _EvolutionCLIError(
                3,
                f"linked project {project.project_id!r} must use a workspace-relative root",
            )

def _evolve_service_exit(error: Exception) -> int:
    """Translate the service's closed refusal vocabulary into public exits.

    The service predates typed refusal subclasses. Causes take precedence; the
    remaining exact message families are a compatibility adapter, and an
    unknown refusal fails as the internal-error band instead of being guessed.
    """

    from pydantic import ValidationError

    from gnd.safefs import InstallError, InstallPathError

    cause: BaseException | None = error
    while cause is not None:
        if isinstance(cause, FileNotFoundError):
            return EXIT_NO_INPUT
        if isinstance(cause, InstallPathError):
            return EXIT_IO
        if isinstance(cause, InstallError):
            return EXIT_COLLISION
        if isinstance(cause, OSError):
            return EXIT_IO
        if isinstance(
            cause,
            (
                json.JSONDecodeError,
                UnicodeDecodeError,
                ValidationError,
                ModelValidationError,
            ),
        ):
            return 3
        cause = cause.__cause__

    message = str(error)
    io_markers = (
        " is a symlink",
        " is not a regular file",
        "could not be inspected",
        "could not be read",
        "cannot be resolved",
        "escapes allowed root",
        "is not a directory",
        "unsupported special entry",
        "linked project exceeds ",
    )
    stale_markers = (
        "stale ",
        # An incomplete evolution refused a new one. 11 is reused rather than
        # newly allocated: "a write was refused, nothing was destroyed" is the
        # claim band 11 already makes (03-04 precedent), so no disjointness
        # obligation arises. D-11 forbids completing the state we found.
        "incomplete evolution ",
        "accepted blast radius",
        "breaking evolution requires explicit acceptance",
        "immutable evidence conflict",
        "changed before",
        "differs from immutable evidence",
        "does not match staged",
        "completed record differs",
        "live model bytes differ",
        "evidence changed",
        "verbalization changed",
        "blast radius changed",
        "identity differs",
        "identity changed",
        "inventory is incomplete",
        "do not match pending identities",
        "changed during",
    )
    malformed_markers = (
        "invalid ",
        "validation failed",
        "not UTF-8",
        "candidate model is not",
        # Any model's YAML refusal, current or staged, is input (review H1).
        "is not valid YAML",
        "declared operations",
        "declared before value",
        "stable locator",
        "add target",
        "duplicate stable blast-radius reference",
        "candidate model media type",
        "operation audit actor/origin/time",
        "new llm-inferred constraints",
        "owner-approved user-supplied constraints",
        "new or changed constraints",
        # IK2 D-12 refusals for induced provenance (spec R-I1..R-I4).
        "provenance.induction",
        "new induced constraints",
        "induced constraints become confirmed",
        "fact_types[",
        "evolution proposal exceeds ",
    )
    if any(marker in message for marker in io_markers):
        return EXIT_IO
    if any(marker in message for marker in stale_markers):
        return EXIT_COLLISION
    if any(marker in message for marker in malformed_markers):
        return 3
    return EXIT_INTERNAL

def _evolve_json_bytes(claim: Any) -> bytes:
    return (
        json.dumps(
            claim.model_dump(mode="json"),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")

def _evolve_emit_claim(claim: Any, output_format: str, *, stage: str) -> None:
    if output_format == "json":
        sys.stdout.write(_evolve_json_bytes(claim).decode("utf-8"))
        return
    if stage == "preview":
        print(f"PREVIEW {claim.preview_sha256}")
        print(f"  proposal: {claim.proposal_sha256}")
        print(f"  before: {claim.before_model.sha256}")
        print(f"  candidate: {claim.candidate_model.sha256}")
        print(f"  blast-radius: {claim.blast_radius.report_sha256}")
        print(f"  breaking: {str(claim.breaking).lower()}")
        for reference in claim.affected_references:
            print(f"  affected: {reference}")
    elif stage == "apply":
        print(f"PENDING {claim.state_identity_sha256}")
        print(f"  proposal: {claim.proposal_id}")
        print(f"  preview: {claim.preview_sha256}")
        print(f"  model: {claim.old_model_sha256} -> {claim.new_model_sha256}")
    else:
        label = "PUBLISHED-WITH-DRIFT" if claim.published_with_drift else "RECORDED"
        print(f"{label} {claim.record_identity_sha256}")
        print(f"  model: {claim.old_model_sha256} -> {claim.new_model_sha256}")
        print(f"  conformance-exit: {claim.conformance_exit_code}")

def _evolve_publish_preview(
    workspace: Path,
    destination: Path,
    relative: str,
    data: bytes,
) -> None:
    from gnd.artifacts import ArtifactError, read_regular_file_bytes
    from gnd.safefs import InstallError, InstallPathError, LeafIdentity
    from gnd.safefs import atomic_write as _atomic_write

    try:
        existing = read_regular_file_bytes(
            workspace,
            relative,
            label="preview output",
        )
    except ArtifactError as error:
        cause: BaseException | None = error
        while cause is not None and not isinstance(cause, FileNotFoundError):
            cause = cause.__cause__
        if isinstance(cause, FileNotFoundError):
            existing = None
        else:
            raise _EvolutionCLIError(
                EXIT_IO,
                f"preview output could not be read through the workspace anchor: {error}",
            ) from error
    if existing is not None:
        if existing == data:
            return
        raise _EvolutionCLIError(
            EXIT_COLLISION,
            f"preview output {destination} already contains different owner bytes",
        )
    try:
        _atomic_write(
            workspace,
            relative,
            data,
            expected=LeafIdentity(kind="absent"),
        )
    except InstallPathError as error:
        raise _EvolutionCLIError(EXIT_IO, f"preview output path was refused: {error}") from error
    except InstallError as error:
        raise _EvolutionCLIError(
            EXIT_COLLISION, f"preview output changed before publication: {error}"
        ) from error
    except OSError as error:
        raise _EvolutionCLIError(
            EXIT_IO, f"preview output {destination} could not be published: {error}"
        ) from error

def _evolve_same_review_identity(reviewed: Any, staged: Any) -> bool:
    """Whether a staged accepted preview is the exact reviewed preview lineage."""

    excluded = {"accepted_blast_radius_sha256", "preview_sha256"}
    if reviewed.model_dump(mode="json", exclude=excluded) != staged.model_dump(
        mode="json", exclude=excluded
    ):
        return False
    return reviewed.accepted_blast_radius_sha256 in {
        None,
        staged.accepted_blast_radius_sha256,
    }

def _evolve_error_exit(error: Exception) -> int:
    from gnd.evolve import (
        EvolutionError,
        EvolutionOperationsGatedError,
        EvolutionReadOnlyCompatibilityError,
    )
    from gnd.safefs import InstallPathError

    if isinstance(error, _EvolutionCLIError):
        return error.exit_code
    # Before the generic EvolutionError arm, and by TYPE rather than by message
    # substring: the gate's refusal text names user-supplied element ids, and a
    # message-family match over those is how an id containing "stale " would
    # silently become exit 11.
    if isinstance(error, EvolutionOperationsGatedError):
        return EXIT_EVOLUTION_OPERATIONS_GATED
    # Before the generic arm, and by TYPE for the same reason: a pending state
    # this tool can read but cannot finish is a collision with existing
    # evidence, not a malformed input (D-P3.5).
    if isinstance(error, EvolutionReadOnlyCompatibilityError):
        return EXIT_COLLISION
    if isinstance(error, EvolutionError):
        return _evolve_service_exit(error)
    if isinstance(error, InstallPathError):
        return EXIT_IO
    if isinstance(error, FileNotFoundError):
        return EXIT_NO_INPUT
    if isinstance(error, OSError):
        return EXIT_IO
    return EXIT_INTERNAL

def _evolve_fail(error: Exception, *, stage: str) -> int:
    exit_code = _evolve_error_exit(error)
    print(f"EVOLUTION {stage.upper()} REFUSED ({exit_code}): {error}", file=sys.stderr)
    return exit_code

def _evolve_finish_apply(service: Any, pending: Any, output_format: str) -> int:
    """Complete the published evolution inside the same ``apply`` invocation.

    R-02 (MODEL-02): ``run_conformance`` is reachable only from
    ``EvolutionService.finalize``, and ``apply``/``finalize`` are separate
    user-facing subcommands, so "stopped after apply" was an ordinary user state
    in which a model change was published with no downstream recheck. The staged
    two-phase *service* protocol is deliberately unchanged (04-05…04-07 locked
    the model CAS as the explicit commit point, with conformance following it
    without rollback and the record published last); the gap closes here, at the
    command boundary.

    The two claims stay two payloads — D-24 forbids presenting the publication
    claim and the conformance claim as one verdict — and the command's exit is
    finalize's raw aggregate conformance exit, so drift is a published model
    with a reported problem rather than a failed apply.
    """

    _evolve_emit_claim(pending, output_format, stage="apply")
    try:
        record = service.finalize(pending)
    except Exception as error:  # closed public exit mapping
        raise _EvolutionCLIError(
            _evolve_error_exit(error),
            "model CAS committed, but the chained finalization was refused; the model "
            "is published and its downstream recheck is incomplete — complete it with "
            f"`gnd evolve finalize`: {error}",
        ) from error
    _evolve_emit_claim(record, output_format, stage="finalize")
    return record.conformance_exit_code

def _cmd_evolve_preview(
    model_path: str,
    proposal_path: str,
    workspace_path: str,
    records_path: str,
    preview_path: str,
    output_format: str,
) -> int:
    """Validate one proposal through ``EvolutionService.preview`` and publish its claim."""

    from gnd.evolve import EvolutionService, read_evolution_proposal

    try:
        workspace = _evolve_workspace(workspace_path)
        model, _model_relative = _evolve_workspace_path(
            workspace, model_path, label="model", required=True
        )
        proposal_file, proposal_relative = _evolve_workspace_path(
            workspace, proposal_path, label="proposal", required=True
        )
        preview_file, preview_relative = _evolve_workspace_path(
            workspace, preview_path, label="preview output", required=False
        )
        records = _evolve_records_root(records_path)
        proposal = read_evolution_proposal(
            proposal_file,
            anchor=workspace,
            relative=proposal_relative,
        )
        _evolve_validate_proposal_roots(proposal)
        service = EvolutionService(
            model_path=model,
            evidence_root=records,
            allowed_project_root=workspace,
        )
        preview = service.preview(proposal)
        rendered = _evolve_json_bytes(preview)
        _evolve_publish_preview(workspace, preview_file, preview_relative, rendered)
        _evolve_emit_claim(preview, output_format, stage="preview")
        return 0
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        return _evolve_fail(error, stage="preview")

def _cmd_evolve_apply(
    model_path: str,
    proposal_path: str,
    preview_path: str,
    workspace_path: str,
    records_path: str,
    output_format: str,
) -> int:
    """Revalidate an exact preview, publish the model CAS, and complete it.

    One command, one whole operation (R-02): ``EvolutionService.apply`` then
    ``EvolutionService.finalize`` in the same process, returning finalize's raw
    aggregate conformance exit.
    """

    from gnd.evolve import EvolutionPreview, EvolutionService, read_evolution_proposal

    try:
        workspace = _evolve_workspace(workspace_path)
        model, model_relative = _evolve_workspace_path(
            workspace, model_path, label="model", required=True
        )
        proposal_file, proposal_relative = _evolve_workspace_path(
            workspace, proposal_path, label="proposal", required=True
        )
        preview_file, preview_relative = _evolve_workspace_path(
            workspace, preview_path, label="preview", required=True
        )
        records = _evolve_records_root(records_path)
        proposal = read_evolution_proposal(
            proposal_file,
            anchor=workspace,
            relative=proposal_relative,
        )
        _evolve_validate_proposal_roots(proposal)
        reviewed = _evolve_read_claim(
            preview_file,
            EvolutionPreview,
            label="preview",
            anchor=workspace,
            relative=preview_relative,
        )
        if reviewed.proposal != proposal:
            raise _EvolutionCLIError(
                EXIT_COLLISION,
                "reviewed preview belongs to a different explicit proposal identity",
            )
        service = EvolutionService(
            model_path=model,
            evidence_root=records,
            allowed_project_root=workspace,
        )
        # Ahead of the branch split, not inside ``service.preview``: the
        # candidate-already-live retry branch below never calls ``preview``, and
        # it is exactly the branch a user reaches after an interrupted apply.
        # Installing the check only in ``preview`` would leave that branch
        # outside the guarantee. The proposal that owns the pending state is
        # exempt inside the service, so completing it stays possible.
        service.refuse_inherited_pending_finalization(proposal.proposal_id)
        try:
            from gnd.artifacts import read_regular_file_bytes

            live_model = read_regular_file_bytes(
                workspace,
                model_relative,
                label="model",
            )
        except Exception as error:
            raise _EvolutionCLIError(
                EXIT_IO, f"model {model} could not be read before apply: {error}"
            ) from error
        if live_model == reviewed.candidate_model.text.encode(reviewed.candidate_model.encoding):
            staged_path = records / reviewed.proposal.proposal_id / "preview.json"
            staged_file, staged_relative = _evolve_rooted_path(
                records,
                str(staged_path),
                root_label="records root",
                label="staged preview",
                required=True,
            )
            staged = _evolve_read_claim(
                staged_file,
                EvolutionPreview,
                label="staged preview",
                anchor=records,
                relative=staged_relative,
            )
            if not _evolve_same_review_identity(reviewed, staged):
                raise _EvolutionCLIError(
                    EXIT_COLLISION,
                    "staged accepted preview differs from the reviewed preview identity",
                )
            pending = service.apply(staged)
            return _evolve_finish_apply(service, pending, output_format)
        fresh = service.preview(proposal)
        if reviewed != fresh:
            raise _EvolutionCLIError(
                EXIT_COLLISION,
                "reviewed preview is stale or belongs to a different proposal/model identity",
            )
        accepted = fresh
        if fresh.breaking:
            print(
                "Enter the exact reviewed blast radius report_sha256 to apply:",
                file=sys.stderr,
            )
            try:
                accepted_digest = input().strip()
            except EOFError as error:
                raise _EvolutionCLIError(
                    EXIT_COLLISION, "breaking evolution requires exact blast radius acceptance"
                ) from error
            accepted = service.preview(
                proposal,
                accepted_blast_radius_sha256=accepted_digest,
            )
        pending = service.apply(accepted)
        return _evolve_finish_apply(service, pending, output_format)
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        return _evolve_fail(error, stage="apply")

def _cmd_evolve_finalize(
    model_path: str,
    pending_path: str,
    workspace_path: str,
    records_path: str,
    output_format: str,
) -> int:
    """Complete one pending identity through ``EvolutionService.finalize``."""

    from gnd.evolve import EvolutionFinalizationState, EvolutionService

    try:
        workspace = _evolve_workspace(workspace_path)
        model, _model_relative = _evolve_workspace_path(
            workspace, model_path, label="model", required=True
        )
        records = _evolve_records_root(records_path)
        pending_file, pending_relative = _evolve_rooted_path(
            records,
            pending_path,
            root_label="records root",
            label="pending state",
            required=True,
        )
        pending = _evolve_read_claim(
            pending_file,
            EvolutionFinalizationState,
            label="pending state",
            anchor=records,
            relative=pending_relative,
        )
        service = EvolutionService(
            model_path=model,
            evidence_root=records,
            allowed_project_root=workspace,
        )
        record = service.finalize(pending)
        _evolve_emit_claim(record, output_format, stage="finalize")
        return record.conformance_exit_code
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        return _evolve_fail(error, stage="finalize")

_EvolutionCLIError.__module__ = "gnd.cli"
_evolve_reject_unsafe_spelling.__module__ = "gnd.cli"
_evolve_absolute_path.__module__ = "gnd.cli"
_evolve_reject_existing_symlinks.__module__ = "gnd.cli"
_evolve_workspace.__module__ = "gnd.cli"
_evolve_rooted_path.__module__ = "gnd.cli"
_evolve_workspace_path.__module__ = "gnd.cli"
_evolve_records_root.__module__ = "gnd.cli"
_evolve_read_claim.__module__ = "gnd.cli"
_evolve_validate_proposal_roots.__module__ = "gnd.cli"
_evolve_service_exit.__module__ = "gnd.cli"
_evolve_json_bytes.__module__ = "gnd.cli"
_evolve_emit_claim.__module__ = "gnd.cli"
_evolve_publish_preview.__module__ = "gnd.cli"
_evolve_same_review_identity.__module__ = "gnd.cli"
_evolve_error_exit.__module__ = "gnd.cli"
_evolve_fail.__module__ = "gnd.cli"
_evolve_finish_apply.__module__ = "gnd.cli"
_cmd_evolve_preview.__module__ = "gnd.cli"
_cmd_evolve_apply.__module__ = "gnd.cli"
_cmd_evolve_finalize.__module__ = "gnd.cli"
