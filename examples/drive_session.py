"""Drive GND experiment sessions -- one walk over all of them.

OQ-P4-3, absorbed by v4.0 Phase 4.  Five near-identical gated sessions differed
only in their brief, and the v3.0 record deferred collapsing them because doing
it then would have rewritten five committed evidence directories to save prose.
This driver collapses the *invocation* instead: the five directories stay
byte-unedited and a single parameterized walk runs whichever sessions you name.

Deliberately NOT a ``gnd`` subcommand.  The v4.0 plan's section 2 refuses a new
verb, and this is orchestration over the CLI rather than a claim of its own --
it decides nothing the CLI does not already decide, and it never edits a
contract.

    uv run examples/drive_session.py --root examples/bookrec --adapter claude \
        --timeout 1200 --only <experiment-id>

Deliberately NOT a PEP 723 script.  An inline-metadata block makes ``uv run``
build an isolated environment that does not contain this project, and the very
first real invocation then dies with ``FileNotFoundError: 'gnd'``.  GND is
invoked as ``sys.executable -m gnd`` for the same reason: the interpreter
running this file is the one known to have it.

Exit 0 only when every selected session both RAN and CLOSED at 0.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import signal
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

CONTRACT_NAME = "session.contract.json"
TESTS_MODE = "tests"


@dataclass(frozen=True)
class Session:
    """One experiment directory holding a session contract."""

    directory: Path
    experiment_id: str
    schema_version: int
    #: True when ANY case declares tests acceptance.  Read from the contract --
    #: never inferred from the directory name, because a name is not a mode and
    #: a walk that branched on ids would be N copies of this policy (rule 4).
    tests_mode: bool


@dataclass(frozen=True)
class DriveOutcome:
    """What the two child processes actually did.

    Both exit codes are carried verbatim.  Nothing here collapses a nonzero
    child into a success, and a timeout is its own outcome rather than a pass.
    """

    session: Session
    run_exit: int | None
    close_exit: int | None
    timed_out: bool
    argv: tuple[tuple[str, ...], ...]

    @property
    def ok(self) -> bool:
        return not self.timed_out and self.run_exit == 0 and self.close_exit == 0


def sessions(root: Path) -> tuple[Session, ...]:
    """Every experiment directory under ``root`` holding a session contract.

    Sorted by directory name so a walk is reproducible.  A contract that does
    not parse is surfaced as an error rather than skipped: a session silently
    dropped from a walk is a session nobody notices did not run.
    """
    found: list[Session] = []
    for contract_path in sorted(root.glob(f"*/{CONTRACT_NAME}")):
        document = json.loads(contract_path.read_text(encoding="utf-8"))
        cases = document.get("cases") or ()
        found.append(
            Session(
                directory=contract_path.parent,
                experiment_id=str(document.get("experiment_id", contract_path.parent.name)),
                schema_version=int(document.get("schema_version", 0)),
                tests_mode=any(
                    (case.get("acceptance") or {}).get("mode") == TESTS_MODE for case in cases
                ),
            )
        )
    return tuple(found)


#: GND is reached through THIS interpreter, never through a bare name on PATH.
GND = (sys.executable, "-m", "gnd")


def _run_argv(
    session: Session,
    *,
    adapter: str | None,
    adapter_policy: Path | None,
    test_argv: Sequence[str],
    wall_seconds: float | None,
) -> tuple[str, ...]:
    argv = [*GND, "exp", "run", str(session.directory)]
    if adapter is not None:
        argv += ["--adapter", adapter]
    if adapter_policy is not None:
        argv += ["--adapter-policy", str(adapter_policy)]
    if wall_seconds is not None:
        argv += ["--wall-seconds", str(wall_seconds)]
    for word in test_argv:
        # The JOINED form is mandatory.  argparse consumes a separated value
        # beginning with "-" as a flag, so `--test-argv -m` exits 64 and every
        # tests-mode invocation would fail on its second word.
        argv.append(f"--test-argv={word}")
    return tuple(argv)


def _run_bounded(argv: Sequence[str], *, timeout_seconds: float) -> int | None:
    """Run one child in its own process group and kill the GROUP on timeout.

    ``subprocess.run(timeout=...)`` kills only the leader, so a child that
    spawned its own children leaves them running after the bound expires --
    which makes the bound a report rather than a bound.  Returns None on
    timeout.
    """
    process = subprocess.Popen(list(argv), start_new_session=True)
    try:
        return process.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            process.kill()
        process.wait()
        return None


def _display_argv(argv: Sequence[str]) -> tuple[str, ...]:
    """Hide caller-local policy paths while preserving the executed argv."""

    displayed = list(argv)
    if "--adapter-policy" in displayed:
        displayed[displayed.index("--adapter-policy") + 1] = "<adapter-policy>"
    return tuple(displayed)


def drive(
    session: Session,
    *,
    adapter: str | None = None,
    adapter_policy: Path | None = None,
    test_argv: Sequence[str] = (),
    wall_seconds: float | None = None,
    timeout_seconds: float,
    dry_run: bool = False,
) -> DriveOutcome:
    """Run one session, then close it.  Never edits a contract.

    ``timeout_seconds`` has no default on purpose: an unbounded child is the
    failure mode this driver could most easily introduce, and a default would
    let a caller acquire one without choosing it.

    A tests-mode session REQUIRES at least one ``--test-argv`` word -- ``gnd exp
    run`` refuses without one -- and a non-tests session refuses to receive any.
    Both are checked here so the walk reports the mismatch rather than an
    opaque usage exit from the child.
    """
    if not (isinstance(timeout_seconds, (int, float)) and math.isfinite(timeout_seconds)
            and timeout_seconds > 0):
        raise ValueError(f"timeout_seconds must be positive and finite, not {timeout_seconds!r}")
    if session.tests_mode and not test_argv:
        raise ValueError(f"{session.experiment_id} is tests-mode and needs --test-argv")
    if not session.tests_mode and test_argv:
        raise ValueError(f"{session.experiment_id} is not tests-mode and forbids --test-argv")
    if session.schema_version == 6:
        if adapter is not None or adapter_policy is None:
            raise ValueError(
                f"{session.experiment_id} is schema v6 and requires adapter_policy only"
            )
    elif adapter is None or adapter_policy is not None:
        raise ValueError(
            f"{session.experiment_id} is legacy and requires adapter only"
        )

    run = _run_argv(
        session,
        adapter=adapter,
        adapter_policy=adapter_policy,
        test_argv=test_argv,
        wall_seconds=wall_seconds,
    )
    close = (*GND, "exp", "close", str(session.directory))

    if dry_run:
        return DriveOutcome(session, None, None, False, (run, close))

    run_exit = _run_bounded(run, timeout_seconds=timeout_seconds)
    if run_exit is None:
        return DriveOutcome(session, None, None, True, (run, close))
    if run_exit != 0:
        # Closing after a failed run would ask a completeness gate about an
        # experiment whose session never accepted.  Report the run's exit.
        return DriveOutcome(session, run_exit, None, False, (run, close))
    close_exit = _run_bounded(close, timeout_seconds=timeout_seconds)
    if close_exit is None:
        return DriveOutcome(session, run_exit, None, True, (run, close))
    return DriveOutcome(session, run_exit, close_exit, False, (run, close))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="drive GND experiment sessions")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--adapter", choices=("claude", "codex"))
    parser.add_argument("--adapter-policy", type=Path)
    parser.add_argument("--only", action="append", default=[], metavar="EXPERIMENT_ID")
    parser.add_argument("--test-argv", action="append", default=[], metavar="WORD")
    parser.add_argument("--wall-seconds", type=float, default=None)
    parser.add_argument("--timeout", type=float, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    discovered = sessions(args.root)
    selected = [s for s in discovered if not args.only or s.experiment_id in set(args.only)]
    unknown = set(args.only) - {s.experiment_id for s in discovered}
    if unknown:
        print(f"ERROR: no session named {sorted(unknown)} under {args.root}", file=sys.stderr)
        return 1
    if not selected:
        print(f"ERROR: no session contract found under {args.root}", file=sys.stderr)
        return 1

    failures = 0
    for session in selected:
        outcome = drive(
            session,
            adapter=args.adapter,
            adapter_policy=args.adapter_policy,
            test_argv=args.test_argv,
            wall_seconds=args.wall_seconds,
            timeout_seconds=args.timeout,
            dry_run=args.dry_run,
        )
        for one in outcome.argv:
            print(("DRY " if args.dry_run else "") + " ".join(_display_argv(one)))
        if not args.dry_run and not outcome.ok:
            failures += 1
            print(
                f"FAILED {session.experiment_id}: run={outcome.run_exit} "
                f"close={outcome.close_exit} timed_out={outcome.timed_out}",
                file=sys.stderr,
            )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
