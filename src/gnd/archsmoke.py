"""Dynamic architecture smoke -- the half of the contract that RUNS.

The static assertion (``gnd.conformance.architecture``) never executes project
code; that invariant is its whole mechanism. This module is its opposite number
and the first place in the package that deliberately runs candidate code, so
the two must never meet: nothing under ``gnd.conformance`` may import this
module, and a test pins that.

**Smoke executes candidate code with the developer's identity -- an acceptance
convenience, never a security boundary.** GND does not sandbox it.

Three bounds exist because the child is user-controlled:

* a deadline, enforced over the child's whole **process group**, because
  ``subprocess.run(timeout=...)`` kills only the direct child and measured
  grandchildren survive it;
* ``MAX_CAPTURE_BYTES`` per stream, applied **at the read** -- truncating a
  failure message bounds the report, never the read;
* decoding with ``errors="replace"``, because strict decoding turns a child's
  invalid byte into an exception where an outcome belongs.

A row passes only when its status is ``MATCHED``. Every other status is a named
failure, and the one that matters most is ``DID_NOT_START``: ``python -m`` on a
missing module exits 1, and so does any uncaught traceback, so an exit-code
comparison alone would report a green row for a project whose entry point is
gone. Whether the entry point started is decided by a parent-owned pipe the
shim writes to only after resolving the target ``python -m`` will actually
execute -- one mechanism, not a sentinel exit code that could itself collide
with a declared band, and not a file the candidate could forge or delete.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading
import time
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Final

from gnd.architecture import (
    ArchitectureContract,
    ArchitectureSmoke,
    load_architecture_contract,
)

__all__ = [
    "DEFAULT_TIMEOUT_SECONDS",
    "MAX_CAPTURE_BYTES",
    "SmokeOutcome",
    "SmokeStatus",
    "build_smoke_module",
    "project_root_for",
    "run_row",
    "smoke_rows",
    "substitute",
    "uncited_exits",
]

DEFAULT_TIMEOUT_SECONDS: Final[int] = 120
MAX_CAPTURE_BYTES: Final[int] = 64 * 1024
TMP_TOKEN: Final[str] = "{tmp}"
#: Grace for readers to notice closed pipes after the group is killed.
_POST_KILL_JOIN_SECONDS: Final[float] = 2.0

#: Resolve what ``python -m`` will actually EXECUTE -- including a package's
#: ``__main__`` -- and only then signal down a parent-owned pipe before handing
#: control to ``runpy``. A pipe rather than a file because a file can be stale
#: from a previous run, absent because the scratch directory was unwritable, or
#: unlinked by the candidate code itself; none of those are questions about the
#: entry point. ``find_spec`` alone was not enough: a package without
#: ``__main__`` resolves, exits 1, and would match a row declaring 1.
_SHIM: Final[str] = (
    "import importlib.util as _u, os as _o, runpy as _r, sys as _s\n"
    "_mod, _fd = _s.argv[1], int(_s.argv[2])\n"
    "del _s.argv[1:3]\n"
    "_s.argv[0] = _mod\n"
    "def _fail(_m):\n"
    "    _s.stderr.write('gnd.archsmoke: %s\\n' % _m)\n"
    "    raise SystemExit(1)\n"
    "try:\n"
    "    _spec = _u.find_spec(_mod)\n"
    "except (ImportError, ValueError, TypeError) as _e:\n"
    "    _fail('entry point %r did not resolve: %s' % (_mod, _e))\n"
    "if _spec is None:\n"
    "    _fail('entry point %r did not resolve' % _mod)\n"
    "if _spec.submodule_search_locations is not None:\n"
    "    try:\n"
    "        _main = _u.find_spec(_mod + '.__main__')\n"
    "    except (ImportError, ValueError, TypeError):\n"
    "        _main = None\n"
    "    if _main is None:\n"
    "        _fail('entry point %r is a package with no __main__ and cannot be run '\n"
    "              'with python -m' % _mod)\n"
    "_o.write(_fd, b'1')\n"
    "_o.close(_fd)\n"
    "_r.run_module(_mod, run_name='__main__', alter_sys=True)\n"
)


class SmokeStatus(StrEnum):
    """The closed outcome vocabulary. Only ``MATCHED`` is a pass."""

    MATCHED = "matched"
    BAND_MISMATCH = "band-mismatch"
    DID_NOT_START = "did-not-start"
    TIMED_OUT = "timed-out"
    OUTPUT_CAP_EXCEEDED = "output-cap-exceeded"


@dataclass(frozen=True)
class SmokeOutcome:
    """One row's result. ``actual_exit`` is ``None`` when no exit code exists."""

    id: str
    entry_point: str
    argv: tuple[str, ...]
    expect_exit: int
    status: SmokeStatus
    actual_exit: int | None
    stdout: str
    stderr: str
    truncated: bool

    @property
    def passed(self) -> bool:
        return self.status is SmokeStatus.MATCHED

    @property
    def message(self) -> str:
        """The failure message, naming the row and both bands where they exist."""
        head = f"smoke row {self.id!r} ({self.entry_point} {' '.join(self.argv)})"
        if self.status is SmokeStatus.MATCHED:
            return f"{head}: exit {self.actual_exit} as declared"
        if self.status is SmokeStatus.BAND_MISMATCH:
            detail = (
                f"band mismatch: declared exit {self.expect_exit}, observed exit {self.actual_exit}"
            )
        elif self.status is SmokeStatus.DID_NOT_START:
            detail = (
                f"the entry point {self.entry_point!r} did not start, so its exit "
                f"code says nothing about the declared band {self.expect_exit}"
            )
        elif self.status is SmokeStatus.TIMED_OUT:
            detail = (
                "timed out; only its leader could be killed"
                if self.id in _GROUP_KILL_FAILED
                else "timed out; its process group was killed"
            )
        else:
            killed = (
                "only its leader could be killed"
                if self.id in _GROUP_KILL_FAILED
                else "its process group was killed"
            )
            detail = f"output cap of {MAX_CAPTURE_BYTES} bytes per stream exceeded; {killed}"
        tail = f"\n  stdout: {self.stdout[:2000]!r}\n  stderr: {self.stderr[:2000]!r}"
        return f"{head}: {detail}{tail}"


def project_root_for(module_file: str) -> Path:
    """The project root is the directory holding the emitted smoke module."""

    return Path(module_file).resolve().parent


def smoke_rows(project_root: str | Path) -> tuple[ArchitectureSmoke, ...]:
    """Re-read the contract's rows. Called at test time, never cached, so an
    authored row edit changes behaviour with no regeneration step."""

    return load_architecture_contract(project_root).smoke


def uncited_exits(contract: ArchitectureContract) -> tuple[tuple[str, int], ...]:
    """Declared exits no smoke row cites. A declared exit is documentation until
    a row arms it, and this is the channel that says which ones are unarmed."""

    cited: dict[str, set[int]] = {}
    for row in contract.smoke:
        cited.setdefault(row.entry_point, set()).add(row.expect_exit)
    unarmed = [
        (entry.module, exit_row.code)
        for entry in contract.entry_points
        for exit_row in entry.exits
        if exit_row.code not in cited.get(entry.module, frozenset())
    ]
    return tuple(sorted(unarmed))


def substitute(argv: Sequence[str], *, tmp: Path) -> tuple[str, ...]:
    """Expand the closed substitution set. The loader refuses any other token in
    a contract, but this function is public, so the branch stays reachable --
    and it RAISES rather than asserting, because ``python -O`` strips asserts."""

    out: list[str] = []
    for token in argv:
        expanded = token.replace(TMP_TOKEN, str(tmp))
        remainder = expanded.replace(str(tmp), "")
        if "{" in remainder or "}" in remainder:
            raise ValueError(
                f"argv token {token!r} uses a substitution other than literal "
                f"{TMP_TOKEN!r}; the substitution set is closed"
            )
        out.append(expanded)
    return tuple(out)


def _drain(stream: Any, sink: list[bytes], overflow: threading.Event) -> None:
    """Read one stream up to the cap, then signal overflow and stop reading."""

    total = 0
    while True:
        chunk = stream.read(min(4096, max(1, MAX_CAPTURE_BYTES - total + 1)))
        if not chunk:
            return
        remaining = MAX_CAPTURE_BYTES - total
        if remaining <= 0:
            overflow.set()
            return
        if len(chunk) > remaining:
            sink.append(chunk[:remaining])
            overflow.set()
            return
        sink.append(chunk)
        total += len(chunk)
        if total >= MAX_CAPTURE_BYTES:
            # Stop AT the declared constant rather than one chunk past it.
            overflow.set()
            return


#: Row ids whose group kill fell back to killing only the leader. The message
#: must not claim the group was killed when it was not.
_GROUP_KILL_FAILED: Final[set[str]] = set()


def _kill_group(proc: subprocess.Popen[bytes], pgid: int) -> bool:
    """Kill the child's whole process group; report whether that actually
    happened. A bare ``proc.kill()`` leaves grandchildren running -- measured --
    so the fallback is a weaker act and says so rather than claiming the group.

    ``pgid`` is captured at spawn, never looked up here: once the leader has
    exited and been reaped, ``os.getpgid`` raises and the kill would silently
    degrade to nothing while a descendant still held the pipes.
    """

    killed_group = True
    try:
        os.killpg(pgid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        killed_group = False
        try:
            proc.kill()
        except OSError:
            pass
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass
    return killed_group


def _started(read_fd: int) -> bool:
    """Did the shim hand control to the target? The signal arrives down a pipe
    the candidate cannot forge, unlink, or leave stale from a previous run."""

    try:
        return os.read(read_fd, 1) == b"1"
    except OSError:
        return False


def _unstarted(row: ArchitectureSmoke, argv: tuple[str, ...], reason: str) -> SmokeOutcome:
    """The outcome for a row nothing could start. Never compared to a band."""

    return SmokeOutcome(
        id=row.id,
        entry_point=row.entry_point,
        argv=argv,
        expect_exit=row.expect_exit,
        status=SmokeStatus.DID_NOT_START,
        actual_exit=None,
        stdout="",
        stderr=reason,
        truncated=False,
    )


def run_row(
    row: ArchitectureSmoke,
    *,
    project_root: str | Path,
    tmp: Path,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> SmokeOutcome:
    """Run one row and return an outcome for EVERY reachable result.

    Totality is this function's job, not its caller's: a hung child, a child
    that floods, a child whose bytes do not decode, and an entry point that
    never resolves each become a status rather than an exception.
    """

    root = Path(project_root)
    argv = substitute(row.argv, tmp=tmp)

    # The row's scratch is the runner's to own; a caller-shaped absence must not
    # become a statement about the entry point.
    try:
        tmp.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        return _unstarted(row, argv, f"the row's scratch directory {tmp} is unusable: {error}")

    read_fd, write_fd = os.pipe()
    os.set_inheritable(write_fd, True)
    try:
        # Fixed argv, no shell. Running candidate code IS the point of this module.
        try:
            proc = subprocess.Popen(
                [sys.executable, "-c", _SHIM, row.entry_point, str(write_fd), *argv],
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                start_new_session=True,
                pass_fds=(write_fd,),
            )
        except OSError as error:
            # A missing or unusable project root, an exhausted process table:
            # nothing ran, and totality is this function's job, not its caller's.
            return _unstarted(row, argv, f"the row could not be spawned in {root}: {error}")
    finally:
        os.close(write_fd)

    # start_new_session makes the child its own group leader, so the group id is
    # its pid. Captured NOW: after the leader is reaped it can no longer be
    # looked up, and a descendant would outlive every kill attempt.
    pgid = proc.pid

    out_chunks: list[bytes] = []
    err_chunks: list[bytes] = []
    overflow = threading.Event()
    readers = [
        threading.Thread(target=_drain, args=(proc.stdout, out_chunks, overflow), daemon=True),
        threading.Thread(target=_drain, args=(proc.stderr, err_chunks, overflow), daemon=True),
    ]
    for reader in readers:
        reader.start()

    # Poll rather than wait(timeout=...): once a reader stops at the cap the
    # child blocks writing into a full pipe and never exits, so a plain wait
    # would report every flood as a timeout -- the cap breach must win.
    status: SmokeStatus | None = None
    exit_code: int | None = None
    deadline = time.monotonic() + timeout
    while True:
        exit_code = proc.poll()
        if exit_code is not None:
            break
        if overflow.is_set():
            status = SmokeStatus.OUTPUT_CAP_EXCEEDED
            break
        if time.monotonic() >= deadline:
            status = SmokeStatus.TIMED_OUT
            break
        time.sleep(0.01)

    # The deadline covers reader completion too, not merely the leader's exit: a
    # descendant inheriting the pipes keeps a reader blocked long after the
    # leader is gone -- measured at 8s against a 1s deadline before this repair.
    for reader in readers:
        reader.join(timeout=max(0.0, deadline - time.monotonic()))
    if any(reader.is_alive() for reader in readers) or status is not None:
        # Kill the whole group whatever happened: it releases the pipes a
        # descendant is holding, and an unbounded smoke row is not a smoke row.
        killed = _kill_group(proc, pgid)
        if any(reader.is_alive() for reader in readers):
            for reader in readers:
                reader.join(timeout=_POST_KILL_JOIN_SECONDS)
            if status is None:
                status = SmokeStatus.TIMED_OUT
        if not killed and status is not None:
            _GROUP_KILL_FAILED.add(row.id)
        if status is not None:
            exit_code = None

    for stream in (proc.stdout, proc.stderr):
        # Never close a pipe whose reader is still alive: close() blocks on the
        # reader's I/O lock, which is the hang this repair exists to remove.
        if stream is not None and not any(reader.is_alive() for reader in readers):
            stream.close()

    started = _started(read_fd)
    os.close(read_fd)

    if status is None:
        # Overflow gets unconditional precedence over the band comparison. It
        # previously lost to a fast child's exit, so an over-cap row that exited
        # its declared code reported MATCHED with truncated=True at once.
        if overflow.is_set():
            status, exit_code = SmokeStatus.OUTPUT_CAP_EXCEEDED, None
        elif not started:
            status, exit_code = SmokeStatus.DID_NOT_START, None
        elif exit_code == row.expect_exit:
            status = SmokeStatus.MATCHED
        else:
            status = SmokeStatus.BAND_MISMATCH

    return SmokeOutcome(
        id=row.id,
        entry_point=row.entry_point,
        argv=argv,
        expect_exit=row.expect_exit,
        status=status,
        actual_exit=exit_code,
        stdout=b"".join(out_chunks).decode("utf-8", errors="replace"),
        stderr=b"".join(err_chunks).decode("utf-8", errors="replace"),
        truncated=overflow.is_set(),
    )


def build_smoke_module(module_file: str) -> tuple[Callable[..., None], Callable[[], None], Any]:
    """Build the three objects the emitted three-line module binds.

    Two non-vacuity guards, not one, because a single module-scoped fixture
    cannot cover both failures: with no rows nothing is collected, so the
    fixture never instantiates and the vacuity goes unannounced.

    * ``test_smoke`` -- one parametrized row per declared row.
    * ``test_smoke_declares_rows`` -- ALWAYS collected. It skips loudly when the
      contract declares nothing, and otherwise proves the parametrization did
      not silently drop a declared row.
    * ``_smoke_floor`` -- module-scoped autouse; on teardown, every declared row
      must actually have run.
    """

    import pytest

    root = project_root_for(module_file)
    rows = smoke_rows(root)
    declared = tuple(row.id for row in rows)
    ran: set[str] = set()

    @pytest.mark.parametrize("row", rows, ids=list(declared))
    def test_smoke(row: ArchitectureSmoke, tmp_path: Path) -> None:
        outcome = run_row(row, project_root=root, tmp=tmp_path)
        ran.add(row.id)
        assert outcome.passed, outcome.message

    def test_smoke_declares_rows() -> None:
        if not smoke_rows(root):
            pytest.skip(
                f"{root / 'architecture.contract.yaml'} declares no smoke rows; "
                f"nothing was executed and nothing is claimed"
            )
        # Re-read the contract rather than trusting the closure: comparing the
        # parametrization against the same tuple that built it would be vacuous.
        fresh = tuple(row.id for row in smoke_rows(root))
        marks = [
            mark for mark in getattr(test_smoke, "pytestmark", ()) if mark.name == "parametrize"
        ]
        assert marks, "test_smoke carries no parametrization"
        collected = tuple(marks[0].kwargs.get("ids") or ())
        assert collected == fresh, (
            f"the parametrization does not carry every declared row: "
            f"collected {collected}, contract declares {fresh}"
        )

    @pytest.fixture(scope="module", autouse=True)
    def _smoke_floor() -> Iterable[None]:
        ran.clear()
        yield
        missing = [row_id for row_id in declared if row_id not in ran]
        assert not missing, (
            f"declared smoke rows never ran: {missing}. A smoke suite that "
            f"silently runs nothing must not pass."
        )

    return test_smoke, test_smoke_declares_rows, _smoke_floor
