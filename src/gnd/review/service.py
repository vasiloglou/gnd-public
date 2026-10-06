from __future__ import annotations

import argparse
import asyncio
import hashlib
import os
import stat
from pathlib import Path, PurePosixPath

from gnd import resolve_version
from gnd.commands._output import _canonical_payload
from gnd.exits import (
    EXIT_COLLISION,
    EXIT_INTERNAL,
    EXIT_IO,
    EXIT_NO_INPUT,
    EXIT_REVIEW_INCONCLUSIVE,
)
from gnd.review.constants import REVIEW_QUORUM

REVIEW_ATTEMPTED_REVIEWERS = 6

REVIEW_TERMINATE_GRACE_SECONDS = 0.5

def _review_outcome(attempted: int, successful: int) -> int:
    """The semantic exit for one structurally completed panel run.

    Written as a pure function of two counts so the whole 0-through-6 table can
    be asserted without spawning anything, and so ``16`` is produced in exactly
    one place. The ``attempted`` guard is load-bearing rather than defensive:
    16 means a run that FINISHED all six attempts and came up short, so a
    partial run must never be able to reach this function and be graded.
    """
    if attempted != REVIEW_ATTEMPTED_REVIEWERS:
        raise ValueError("a panel outcome requires all six reviewer attempts to have completed")
    if not 0 <= successful <= attempted:
        raise ValueError("successful reviewers must be a subset of the attempted reviewers")
    return 0 if successful >= REVIEW_QUORUM else EXIT_REVIEW_INCONCLUSIVE

def _repository_relative_path(value: str) -> str:
    """Argparse converter for one normalized, portable repository-relative path.

    The review request and every artifact it names are resolved against the
    directory the user is standing in, so an absolute, drive-qualified, or
    ``..``-bearing argument is a malformed INVOCATION (64) rather than a
    malformed document (3). The request loader enforces the same shape again on
    the bytes it reads; this converter is the argv half, and neither may be
    dropped in favour of the other.
    """
    if not value or "\x00" in value or "\\" in value:
        raise argparse.ArgumentTypeError(
            "must be a normalized repository-relative POSIX path (no NUL, no backslash)"
        )
    posix = PurePosixPath(value)
    if (
        posix.is_absolute()
        or value != posix.as_posix()
        or any(part in {"", ".", ".."} for part in posix.parts)
    ):
        raise argparse.ArgumentTypeError(
            "must be a normalized repository-relative POSIX path resolved against the "
            "current directory (no leading '/', no '.', no '..' component)"
        )
    return value

def _cmd_review_panel(
    request_path: str,
    out_dir: str,
    reviewer_timeout: float,
    overall_timeout: float,
    max_output_bytes: int,
    reviewer_effort: str = "xhigh",
    command_name: str = "review panel",
) -> int:
    """Bridge one validated review request into the bounded panel exactly once."""

    from gnd.review.adapters import REVIEWER_IDS
    from gnd.review.request import (
        ReviewArtifactMissingError,
        ReviewRequestError,
        load_review_request,
    )
    from gnd.review.runner import (
        MAX_REVIEW_PROMPT_BYTES,
        ReviewLimits,
        ReviewRunError,
        canonical_panel_run,
        run_review_panel,
    )

    output_directory = Path(out_dir)
    try:
        output_directory.lstat()
    except FileNotFoundError:
        pass
    except OSError as error:
        print(f"IO ERROR: review output {output_directory} could not be inspected: {error}")
        return EXIT_IO
    else:
        print(
            f"COLLISION: review output {output_directory} already exists; nothing was "
            f"written and no reviewer was invoked"
        )
        return EXIT_COLLISION

    root = Path.cwd()
    request_file = root / request_path
    try:
        request_info = request_file.lstat()
    except FileNotFoundError:
        print(f"MISSING: review request {request_path} does not exist")
        return EXIT_NO_INPUT
    except OSError as error:
        print(f"IO ERROR: review request {request_path} could not be inspected: {error}")
        return EXIT_IO
    if stat.S_ISLNK(request_info.st_mode) or not stat.S_ISREG(request_info.st_mode):
        print(f"IO ERROR: review request {request_path} has a refused file type")
        return EXIT_IO

    try:
        loaded = load_review_request(root, request_path)
    except ReviewArtifactMissingError as error:
        print(f"MISSING: reviewed artifact {error.artifact_path} does not exist")
        return EXIT_NO_INPUT
    except ReviewRequestError as error:
        print(f"ERROR: {error}")
        return 3

    limits = ReviewLimits(
        reviewer_timeout_seconds=reviewer_timeout,
        overall_timeout_seconds=overall_timeout,
        terminate_grace_seconds=REVIEW_TERMINATE_GRACE_SECONDS,
        max_prompt_bytes=MAX_REVIEW_PROMPT_BYTES,
        max_stdout_bytes=max_output_bytes,
        max_stderr_bytes=max_output_bytes,
        max_total_output_bytes=max_output_bytes * 2,
    )
    try:
        run = asyncio.run(
            run_review_panel(
                loaded,
                repository_root=root,
                output_directory=output_directory,
                limits=limits,
                reviewer_effort=reviewer_effort,
            )
        )
    except ReviewRunError as error:
        print(f"IO ERROR: the review panel could not run or publish its evidence: {error}")
        return EXIT_IO
    except (OSError, ValueError) as error:
        print(f"IO ERROR: review evidence could not be published: {error}")
        return EXIT_IO
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"INTERNAL ERROR: {type(error).__name__}: {error}")
        return EXIT_INTERNAL

    try:
        outcome = _review_outcome(len(run.envelopes), len(run.successful_reviewer_ids))
    except ValueError as error:
        print(f"INTERNAL ERROR: {error}")
        return EXIT_INTERNAL

    print(
        _canonical_payload(
            {
                "schema_version": 1,
                "tool": "gnd",
                "command": command_name,
                "gnd_version": resolve_version(),
                "advisory": True,
                "request_kind": run.request.kind,
                "request_sha256": run.request_sha256,
                "run_directory": str(output_directory),
                "run_sha256": hashlib.sha256(canonical_panel_run(run)).hexdigest(),
                "required_successes": REVIEW_QUORUM,
                "reviewer_effort": run.reviewer_effort.value,
                "attempted_reviewer_ids": [reviewer.value for reviewer in REVIEWER_IDS],
                "reviewer_statuses": [
                    {
                        "reviewer_id": envelope.reviewer_id.value,
                        "status": envelope.status.value,
                    }
                    for envelope in run.envelopes
                ],
                "successful_reviewer_ids": [
                    reviewer.value for reviewer in run.successful_reviewer_ids
                ],
                "quorum_met": run.quorum_met,
                "outcome": (
                    "quorum-established" if run.quorum_met else "inconclusive-below-quorum"
                ),
                "reviewed_artifacts_unchanged": (
                    run.reviewed_artifacts_before_sha256 == run.reviewed_artifacts_after_sha256
                ),
            }
        )
    )
    return outcome

def _cmd_review_finalize(run_dir: str, synthesis_path: str, out_path: str) -> int:
    """Validate one semantic synthesis against immutable run evidence and render it."""

    from gnd.review.report import (
        PanelSynthesis,
        ReviewReportError,
        canonical_panel_synthesis,
        finalize_panel_synthesis,
        render_panel_markdown,
    )
    from gnd.review.runner import (
        MAX_RUN_MARKER_BYTES,
        ReviewRunError,
        canonical_panel_run,
        load_panel_run,
    )

    report_path = Path(out_path)
    run_root = Path(run_dir)
    synthesis_file = Path(synthesis_path)

    for required, description in ((run_root, "panel run directory"), (synthesis_file, "synthesis")):
        try:
            info = required.lstat()
        except FileNotFoundError:
            print(f"MISSING: {description} {required} does not exist")
            return EXIT_NO_INPUT
        except OSError as error:
            print(f"IO ERROR: {description} {required} could not be inspected: {error}")
            return EXIT_IO
        expects_directory = required is run_root
        wrong_kind = (
            not stat.S_ISDIR(info.st_mode) if expects_directory else not stat.S_ISREG(info.st_mode)
        )
        if stat.S_ISLNK(info.st_mode) or wrong_kind:
            print(f"IO ERROR: {description} {required} has a refused file type")
            return EXIT_IO
        if not expects_directory and info.st_size > MAX_RUN_MARKER_BYTES:
            print(f"ERROR: synthesis {required} exceeds the {MAX_RUN_MARKER_BYTES}-byte cap")
            return 3

    try:
        run = load_panel_run(run_root)
    except ReviewRunError as error:
        print(f"ERROR: {error}")
        return 3

    try:
        synthesis = PanelSynthesis.model_validate_json(synthesis_file.read_bytes(), strict=True)
    except OSError as error:
        print(f"IO ERROR: synthesis {synthesis_file} could not be read: {error}")
        return EXIT_IO
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"ERROR: panel synthesis failed closed validation: {error}")
        return 3

    # Checked on the RUN's own derived quorum rather than on a message from the
    # finalizer: 16 is a structural claim about the panel, and reading it out of
    # an exception string would make the band depend on prose.
    if not run.quorum_met:
        print(
            _canonical_payload(
                {
                    "schema_version": 1,
                    "tool": "gnd",
                    "command": "review finalize",
                    "gnd_version": resolve_version(),
                    "advisory": True,
                    "required_successes": REVIEW_QUORUM,
                    "successful_reviewer_ids": [
                        reviewer.value for reviewer in run.successful_reviewer_ids
                    ],
                    "quorum_met": False,
                    "outcome": "inconclusive-below-quorum",
                    "report_path": None,
                }
            )
        )
        return _review_outcome(len(run.envelopes), len(run.successful_reviewer_ids))

    try:
        result = finalize_panel_synthesis(run, synthesis)
        rendered = render_panel_markdown(run, synthesis, result)
    except ReviewReportError as error:
        print(f"ERROR: {error}")
        return 3

    try:
        descriptor = os.open(report_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        print(f"COLLISION: {report_path} already exists; nothing was written")
        return EXIT_COLLISION
    except OSError as error:
        print(f"IO ERROR: could not write {report_path}: {error}")
        return EXIT_IO
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    except OSError as error:
        print(f"IO ERROR: could not write {report_path}: {error}")
        return EXIT_IO

    print(
        _canonical_payload(
            {
                "schema_version": 1,
                "tool": "gnd",
                "command": "review finalize",
                "gnd_version": resolve_version(),
                "advisory": True,
                "required_successes": REVIEW_QUORUM,
                "run_sha256": hashlib.sha256(canonical_panel_run(run)).hexdigest(),
                "synthesis_sha256": hashlib.sha256(
                    canonical_panel_synthesis(synthesis)
                ).hexdigest(),
                "successful_reviewer_ids": [
                    reviewer.value for reviewer in run.successful_reviewer_ids
                ],
                "quorum_met": True,
                "outcome": "quorum-established",
                "agreed_concern_count": result.agreed_concern_count,
                "divergent_concern_count": result.divergent_concern_count,
                "prioritized_fix_count": result.prioritized_fix_count,
                "report_path": str(report_path),
            }
        )
    )
    return 0

_review_outcome.__module__ = "gnd.cli"
_repository_relative_path.__module__ = "gnd.cli"
_cmd_review_panel.__module__ = "gnd.cli"
_cmd_review_finalize.__module__ = "gnd.cli"
