"""The PROC-01 station harness behind ``gnd solve``.

One walk over the five CLI-pure GND stations, with a blocking authorization gate
before each spawn and an append-only JSON Lines log of what happened. The spec is
``.gnd-planning/milestones/v2.0/notes/phase-4-spec.md`` at revision 10; section
numbers in the comments below refer to it.

Two properties are load-bearing and easy to erode, so they are stated here:

* **The log carries no verdict.** There is no ``passed``, ``ok``, ``verdict``,
  ``result`` or ``status`` key at any depth in any record kind. A station's own
  exit is recorded verbatim and interpreted by nobody. The harness's process exit
  is a separate control-plane code (:func:`run_walk`'s return value) and never
  becomes a claim about the work.
* **``authorized_by`` is written by code at gate time**, never narrated
  afterwards, which is what keeps an ``--auto`` walk's log from being
  byte-identical to a gated one.

``STATIONS`` is the one home for station policy: order, argv shape, accepted
exits, timeout and evidence path. Nothing outside it may name a station, an
accepted exit or an evidence path.
"""

from __future__ import annotations

import contextlib
import dataclasses
import errno
import hashlib
import json
import os
import re
import signal
import stat
import subprocess
import sys
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import BinaryIO, Literal

from gnd import input_policy as _rf7_input
from gnd.exits import (
    EXIT_INTERNAL,
    EXIT_IO,
    EXIT_NO_INPUT,
    EXIT_OK,
    EXIT_USAGE,
    EXIT_WALK_HALTED,
)

__all__ = [
    "MAX_GATE_REPLY_BYTES",
    "MAX_STATION_TIMEOUT_S",
    "SCHEMA_VERSION",
    "STATIONS",
    "Station",
    "StationOutcome",
    "StationSpawn",
    "WalkPaths",
    "encode_record",
    "run_walk",
    "station_by_name",
]


# --------------------------------------------------------------------------- #
# Constants the spec pins by value
# --------------------------------------------------------------------------- #

#: The walk log's schema version (spec 5.1). An integer, pinned: a future format
#: change increments it, and this module owns version 1 and nothing else.
SCHEMA_VERSION = 1

#: The largest gate reply admitted, in bytes, before its terminating newline
#: (spec 5.4). One more byte than this is read, to detect the overrun.
MAX_GATE_REPLY_BYTES = 257

#: Ceiling on ``--station-timeout SECONDS`` (spec 6.1 stage 1, D-22). An
#: unbounded override is an unbounded child wearing a flag.
MAX_STATION_TIMEOUT_S = 86400

#: Grace period between SIGTERM and SIGKILL when reaping a timed-out child.
_REAP_GRACE_S = 10

#: Directory scans are bounded (spec 6.3). Over the cap, walk-file allocation
#: refuses with 74 and run discovery records ``evidence-ambiguous``.
_MAX_DIR_ENTRIES = 10_000

#: A session result is a small closed document. Bound the exp-run stdout read so
#: evidence attribution cannot turn a child-controlled capture into an unbounded
#: in-process read.
_MAX_RESULT_STDOUT_BYTES = 8 * 1024 * 1024
_MAX_ADAPTER_POLICY_BYTES = 256 * 1024

_WALK_STEM = re.compile(r"^walk-(\d{4,})$")
_RUN_DIR = re.compile(r"^run-(\d{4,})$")


class _InternalDefect(Exception):
    """The harness wrote a record it does not have a contract for.

    Raised by :func:`encode_record` and by nothing else in this module, which is
    what bounds exit 70 to a named instance instead of a catch-all (spec 6.2).
    """


def _adapter_policy_token(path: Path) -> str:
    """Return the exact bounded policy-byte token or raise ``OSError``."""

    before = path.lstat()
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise OSError("adapter policy must be a real regular file")
    if before.st_size > _MAX_ADAPTER_POLICY_BYTES:
        raise OSError("adapter policy exceeds the byte cap")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        opened = os.fstat(descriptor)
        if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            raise OSError("adapter policy changed before it opened")
        chunks: list[bytes] = []
        remaining = _MAX_ADAPTER_POLICY_BYTES + 1
        while remaining:
            chunk = os.read(descriptor, min(64 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
        after = path.lstat()
        if len(raw) > _MAX_ADAPTER_POLICY_BYTES or (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        ) != (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns):
            raise OSError("adapter policy changed while it was read")
    finally:
        os.close(descriptor)
    return "<adapter-policy:sha256=" + hashlib.sha256(raw).hexdigest() + ">"


class _GateIOError(OSError):
    """The default authorization gate could not read its controlling stream."""


# --------------------------------------------------------------------------- #
# Section 3 — the station table
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class WalkPaths:
    """Everything a station's argv or evidence path is built from.

    Frozen, and rebuilt with :func:`dataclasses.replace` when the exp-run
    station's discovered ``run_index`` becomes known — the run directory does
    not exist until the child has written it.
    """

    model: Path
    workspace: Path
    experiment: Path | None
    walk_id: str
    adapter: str | None
    test_argv: tuple[str, ...]
    adapter_policy: Path | None = None
    adapter_policy_token: str | None = None
    run_index: int | None = None

    @property
    def model_arg(self) -> str:
        """The model as it is handed to a child whose cwd is the workspace."""
        return _relative_or_absolute(self.model, self.workspace)

    @property
    def experiment_arg(self) -> str:
        if self.experiment is None:  # pragma: no cover - guarded by stage 8
            raise _InternalDefect("experiment-arg-without-experiment")
        return _relative_or_absolute(self.experiment, self.workspace)


@dataclass(frozen=True)
class Station:
    name: str
    argv: Callable[[WalkPaths], tuple[str, ...]]
    accepted_exits: frozenset[int]
    timeout: int
    evidence: Callable[[WalkPaths], str] | None


def _gnd_argv(*words: str) -> tuple[str, ...]:
    """Invoke this installed package without depending on ``PATH``.

    The console script and ``python -m gnd`` both enter :func:`gnd.cli.main`.
    Using the current interpreter for child stations keeps that equivalence true
    even when the interpreter's bin directory is absent from ``PATH``.
    """
    return (sys.executable, "-m", "gnd", *words)


def _argv_validate(paths: WalkPaths) -> tuple[str, ...]:
    return _gnd_argv("validate", paths.model_arg)


def _argv_synth(paths: WalkPaths) -> tuple[str, ...]:
    return _gnd_argv("synth", paths.model_arg, "--out", "corpus", "--class", "all")


def _argv_codegen(paths: WalkPaths) -> tuple[str, ...]:
    return _gnd_argv("codegen", paths.model_arg, "--out", "project")


def _argv_exp_run(paths: WalkPaths) -> tuple[str, ...]:
    # The harness passes no --wall-seconds: a contract's own wall bound is the
    # contract's business, and retiming it silently would be a claim about work
    # this harness does not own (spec 6.3).
    argv = list(_gnd_argv("exp", "run", paths.experiment_arg))
    if paths.adapter is not None:
        argv += ["--adapter", paths.adapter]
    if paths.adapter_policy is not None:
        argv += ["--adapter-policy", str(paths.adapter_policy)]
    for word in paths.test_argv:
        argv += ["--test-argv", word]
    return tuple(argv)


def _argv_conformance(paths: WalkPaths) -> tuple[str, ...]:
    return _gnd_argv("conformance", paths.model_arg, "project")


def _capture_stdout(paths: WalkPaths, station: str) -> str:
    return f"walks/{paths.walk_id}.{station}.out"


def _capture_stderr(paths: WalkPaths, station: str) -> str:
    return f"walks/{paths.walk_id}.{station}.err"


def _evidence_validate(paths: WalkPaths) -> str:
    return _capture_stdout(paths, "validate")


def _evidence_synth(paths: WalkPaths) -> str:
    return "corpus/"


def _evidence_codegen(paths: WalkPaths) -> str:
    return "project/.gnd-codegen.json"


def _evidence_exp_run(paths: WalkPaths) -> str:
    if paths.run_index is None:  # pragma: no cover - guarded by the caller
        raise _InternalDefect("exp-run-evidence-without-run-index")
    return f"{paths.experiment_arg.rstrip('/')}/runs/run-{paths.run_index:04d}/result.json"


def _evidence_conformance(paths: WalkPaths) -> str:
    return _capture_stdout(paths, "conformance")


#: The locked order. This literal is the one home for station policy: order,
#: argv shape, accepted exits, timeout, evidence path. `conformance` accepts 13
#: (EXIT_MODEL_CODE_DRIFT) because drift is a finding the station is built to
#: report, not a failure of the walk (D-2). `codegen` excludes 11
#: (EXIT_COLLISION) because PROC-01 names precisely that refusal as the --auto
#: backstop; `exp-run` excludes 15, 3 and 64 for the same kind of reason.
STATIONS: tuple[Station, ...] = (
    Station("validate", _argv_validate, frozenset({0}), 300, _evidence_validate),
    Station("synth", _argv_synth, frozenset({0}), 300, _evidence_synth),
    Station("codegen", _argv_codegen, frozenset({0}), 300, _evidence_codegen),
    Station("exp-run", _argv_exp_run, frozenset({0}), 3600, _evidence_exp_run),
    Station("conformance", _argv_conformance, frozenset({0, 13}), 300, _evidence_conformance),
)

_STATION_NAMES: tuple[str, ...] = tuple(station.name for station in STATIONS)
_STATION_POSITION: Mapping[str, int] = MappingProxyType(
    {station.name: index for index, station in enumerate(STATIONS)}
)


def station_by_name(name: str) -> Station:
    for station in STATIONS:
        if station.name == name:
            return station
    raise KeyError(name)


# --------------------------------------------------------------------------- #
# Section 5.1.1 — the record encoder
# --------------------------------------------------------------------------- #

_KEYS: Mapping[str, tuple[str, ...]] = MappingProxyType(
    {
        "walk": ("record", "walk_id", "schema_version", "model", "selected", "flags", "started"),
        "gate": ("record", "walk_id", "station", "argv", "authorized_by"),
        "station": ("record", "walk_id", "station", "exit", "evidence", "halt"),
    }
)

_FLAG_KEYS: tuple[str, ...] = (
    "from",
    "until",
    "skip",
    "auto",
    "adapter",
    "adapter_explicit",
    "experiment",
    "test_argv",
    "station_timeout",
)

_HALT_CAUSES = ("timeout", "spawn-error", "signal", "evidence-ambiguous")


def _stamp(now: datetime) -> str:
    """RFC 3339 UTC, seconds precision. Records carry STRINGS, never datetimes."""
    return now.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def encode_record(record: Mapping[str, object]) -> bytes:
    """The one encoder for every record. This is its whole contract.

    The ``try`` block is part of the contract, not a wrapper around it:
    ``_InternalDefect`` is the only exception this function raises, which is what
    keeps exit 70 a named instance rather than an uncaught traceback outside the
    band section 6.2 calls total.
    """
    try:
        kind = record["record"]
        if tuple(record) != _KEYS[kind]:  # membership AND order, one check
            raise _InternalDefect(f"keys:{kind}")
        if kind == "walk" and tuple(record["flags"]) != _FLAG_KEYS:  # type: ignore[arg-type]
            raise _InternalDefect("flags")
        return (
            json.dumps(
                record,
                ensure_ascii=False,  # UTF-8 is the file encoding; no \uXXXX escaping
                separators=(",", ":"),  # no insignificant whitespace
                allow_nan=False,  # ValueError on a non-finite float
                sort_keys=False,  # key order is the literal order above
            ).encode("utf-8")
            + b"\n"
        )
    except _InternalDefect:
        raise
    except (KeyError, ValueError, TypeError) as exc:
        raise _InternalDefect(repr(exc)) from exc


# --------------------------------------------------------------------------- #
# Section 5.4 — the authorization gate
# --------------------------------------------------------------------------- #


def _authorized_by(source: str, reply: str, now: datetime) -> str:
    return f"{source} {json.dumps(reply, ensure_ascii=False)} {_stamp(now)}"


def _blocking_stdin_gate(station: Station) -> str | None:
    """Block on stdin for an authorization; return the reply, or None to decline.

    Bytes, not a line: ``input()`` decodes an unbounded line before any cap can
    see it, so the cap would be applied after the damage. At most
    ``MAX_GATE_REPLY_BYTES + 1`` bytes are read — one beyond the limit, purely to
    detect the overrun.

    Declines, exhaustively: EOF before any byte; more than the cap with no
    newline inside it; bytes that are not valid UTF-8 (never replacement-decoded);
    and SIGINT, because abandoning a walk at a gate with Ctrl-C is the ordinary
    way a human does it and a traceback is not an answer (D-41).

    A reply of 1..cap bytes that ends at EOF with no newline is ACCEPTED: the
    rule follows the cap, not the terminator (D-62).
    """
    try:
        print(
            f"gnd solve: authorize station {station.name}? ",
            end="",
            file=sys.stderr,
            flush=True,
        )
        raw = _read_gate_bytes(sys.stdin)
    except KeyboardInterrupt:
        return None
    except (OSError, TypeError, ValueError) as error:
        raise _GateIOError(f"authorization gate I/O failed: {error}") from error
    if raw is None:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _read_gate_bytes(stream: object) -> bytes | None:
    """Read one bounded gate reply. None is a decline; bytes are a reply."""
    buffer = getattr(stream, "buffer", stream)
    chunks = bytearray()
    while len(chunks) <= MAX_GATE_REPLY_BYTES:
        byte = buffer.read(1)
        if not byte:  # EOF
            if not chunks:
                return None  # EOF before any byte
            return bytes(chunks)  # 1..cap bytes ending at EOF: accepted (D-62)
        if byte == b"\n":
            return bytes(chunks)
        chunks += byte
    return None  # over the cap with no newline inside it


# --------------------------------------------------------------------------- #
# Section 6.3 — bounded children
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class StationSpawn:
    argv: tuple[str, ...]
    cwd: Path
    timeout_s: int
    stdout_path: Path
    stderr_path: Path
    # Runtime-only binding to the already-open, no-symlink walks directory. It
    # is deliberately private and excluded from equality/repr: the five public
    # fields above remain the spawn contract, while this descriptor closes the
    # pathname race between log allocation and capture creation.
    _walks_fd: int | None = field(default=None, repr=False, compare=False)


@dataclass(frozen=True)
class StationOutcome:
    exit_code: int | None
    halt: str | None


def _spawn_station(spawn: StationSpawn) -> StationOutcome:
    """Run one station to completion, bounded, with its streams never merged.

    Both capture files are opened before the child is spawned; a capture file
    that cannot be opened is an I/O refusal, surfaced as ``spawn-error`` so the
    caller can map it to 74 without inspecting an exception.
    """
    owned_walks_fd: int | None = None
    walks_fd = spawn._walks_fd
    try:
        if walks_fd is None:
            owned_walks_fd = _open_walks_directory(spawn.cwd, create=False)
            walks_fd = owned_walks_fd
        out = _open_capture(spawn, spawn.stdout_path, walks_fd)
    except OSError:
        if owned_walks_fd is not None:
            with contextlib.suppress(OSError):
                os.close(owned_walks_fd)
        return StationOutcome(None, "spawn-error")

    try:
        try:
            err = _open_capture(spawn, spawn.stderr_path, walks_fd)
        except OSError:
            return StationOutcome(None, "spawn-error")
        try:
            outcome = _run_child(spawn, out, err)
        finally:
            close_failed = False
            for handle in (err, out):
                try:
                    handle.close()
                except OSError:
                    close_failed = True
        return StationOutcome(None, "spawn-error") if close_failed else outcome
    finally:
        if not out.closed:
            with contextlib.suppress(OSError):
                out.close()
        if owned_walks_fd is not None:
            with contextlib.suppress(OSError):
                os.close(owned_walks_fd)


def _open_capture(spawn: StationSpawn, path: Path, walks_fd: int) -> BinaryIO:
    """Create one capture leaf exclusively under the bound walks directory."""
    leaf = _capture_leaf_name(spawn, path)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    descriptor = os.open(leaf, flags, 0o644, dir_fd=walks_fd)
    try:
        return os.fdopen(descriptor, "wb")
    except BaseException:
        with contextlib.suppress(OSError):
            os.close(descriptor)
        raise


def _capture_leaf_name(spawn: StationSpawn, path: Path) -> str:
    expected_parent = os.path.abspath(spawn.cwd / "walks")
    if os.path.abspath(path.parent) != expected_parent or path.name in {"", ".", ".."}:
        raise OSError(errno.EPERM, "capture path is not a direct child of workspace/walks")
    return path.name


def _run_child(spawn: StationSpawn, out: object, err: object) -> StationOutcome:
    try:
        child = subprocess.Popen(
            # A list, not the frozen tuple: the spec asks for a list argv, and a
            # sequence of separate words is the whole point -- never a string a
            # shell could reinterpret.
            list(spawn.argv),
            cwd=str(spawn.cwd),
            stdin=subprocess.DEVNULL,
            stdout=out,
            stderr=err,
            start_new_session=True,  # its own process group, so a timeout reaps the tree
        )
    except OSError:
        return StationOutcome(None, "spawn-error")

    try:
        code = child.wait(timeout=spawn.timeout_s)
    except subprocess.TimeoutExpired:
        _reap(child)
        return StationOutcome(None, "timeout")
    except KeyboardInterrupt:
        # The child is in its own process group and got the signal too; reap it
        # and record a signal halt rather than letting the exception escape.
        _reap(child)
        return StationOutcome(None, "signal")

    if code < 0:
        return StationOutcome(None, "signal")
    return StationOutcome(code, None)


def _reap(child: subprocess.Popen[bytes]) -> None:
    """SIGTERM the child's process group, wait the grace period, then SIGKILL."""
    for sig in (signal.SIGTERM, signal.SIGKILL):
        with contextlib.suppress(ProcessLookupError, PermissionError, OSError):
            os.killpg(os.getpgid(child.pid), sig)
        try:
            child.wait(timeout=_REAP_GRACE_S)
            return
        except subprocess.TimeoutExpired:
            continue
    with contextlib.suppress(Exception):  # pragma: no cover - SIGKILL does not fail
        child.wait(timeout=_REAP_GRACE_S)


# --------------------------------------------------------------------------- #
# Paths, allocation and discovery
# --------------------------------------------------------------------------- #


def _relative_or_absolute(target: Path, workspace: Path) -> str:
    """Workspace-relative with POSIX separators, or absolute when outside it.

    The absolute case is the one exception to workspace-relativity (spec 5.1.1).
    """
    try:
        return target.resolve().relative_to(workspace.resolve()).as_posix()
    except ValueError:
        return target.resolve().as_posix()


def _open_walks_directory(workspace: Path, *, create: bool) -> int:
    """Open the physical workspace's real ``walks`` directory without symlinks.

    The returned descriptor is the authority for every log and capture write in
    one walk. Resolving the caller-supplied workspace once permits a workspace
    symlink while refusing a symlink below that physical root.
    """
    workspace_real = Path(os.path.realpath(workspace))
    directory_flags = os.O_RDONLY
    directory_flags |= getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory_flags |= getattr(os, "O_CLOEXEC", 0)
    root_fd = os.open(workspace_real, directory_flags)
    try:
        if create:
            try:
                os.mkdir("walks", mode=0o755, dir_fd=root_fd)
            except FileExistsError:
                pass
        info = os.stat("walks", dir_fd=root_fd, follow_symlinks=False)
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise OSError(errno.ENOTDIR, "workspace/walks must be a real directory")
        return os.open("walks", directory_flags, dir_fd=root_fd)
    finally:
        os.close(root_fd)


def _scan_indices(
    directory: Path | int,
    pattern: re.Pattern[str],
    *,
    entry_type: Literal["file", "directory"],
) -> set[int] | None:
    """Indices matching *pattern* under *directory*; None if the cap is exceeded.

    A name that does not match is skipped, not parsed, and never raises. The cap
    is part of the contract: an unbounded scan is an unbounded read.
    """
    found: set[int] = set()
    seen = 0
    # ``scandir(fd)`` owns and closes the descriptor on some supported Python/
    # platform combinations. Duplicate a borrowed descriptor so the walk keeps
    # its directory authority through every later capture.
    borrowed_copy: int | None = os.dup(directory) if isinstance(directory, int) else None
    scan_target: Path | int = borrowed_copy if borrowed_copy is not None else directory
    try:
        with os.scandir(scan_target) as entries:
            for entry in entries:
                seen += 1
                if seen > _MAX_DIR_ENTRIES:
                    return None
                if entry_type == "file":
                    expected_type = entry.is_file(follow_symlinks=False)
                else:
                    expected_type = entry.is_dir(follow_symlinks=False)
                if not expected_type:
                    continue
                stem = entry.name.removesuffix(".jsonl")
                match = pattern.match(stem)
                if match is not None:
                    found.add(int(match.group(1)))
    finally:
        if borrowed_copy is not None:
            with contextlib.suppress(OSError):
                os.close(borrowed_copy)
    return found


def _allocate_walk_file(
    walks_dir: Path, *, directory_fd: int | None = None
) -> tuple[Path, str, BinaryIO]:
    """Open ``walk-NNNN.jsonl`` O_EXCL, strictly above the greatest index present.

    Holes are never refilled: an allocator that fills holes makes "highest index
    is the latest" false, which is the Lane D false premise taken as policy
    rather than rediscovered. The first walk in an empty workspace is
    ``walk-0001`` — indices start at 1.
    """
    owned_fd: int | None = None
    if directory_fd is None:
        directory_flags = os.O_RDONLY
        directory_flags |= getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
        directory_flags |= getattr(os, "O_CLOEXEC", 0)
        owned_fd = os.open(walks_dir, directory_flags)
        directory_fd = owned_fd
    try:
        present = _scan_indices(directory_fd, _WALK_STEM, entry_type="file")
        if present is None:
            raise OSError(errno.ENFILE, "walks directory over the scan cap")
        index = (max(present) + 1) if present else 1
        while True:
            leaf = f"walk-{index:04d}.jsonl"
            path = walks_dir / leaf
            flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
            flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
            try:
                descriptor = os.open(leaf, flags, 0o644, dir_fd=directory_fd)
            except FileExistsError:
                index += 1  # lost a race; never append to a file we did not create
                continue
            try:
                handle = os.fdopen(descriptor, "ab")
            except BaseException:
                with contextlib.suppress(OSError):
                    os.close(descriptor)
                with contextlib.suppress(OSError):
                    os.unlink(leaf, dir_fd=directory_fd)
                raise

            # O_EXCL protects this pathname, but a concurrent allocator can
            # publish a much higher index after the first scan. Re-scan while
            # retaining the descriptor; if our index is no longer above every
            # present walk, remove only our own candidate and retry.
            try:
                present_after = _scan_indices(directory_fd, _WALK_STEM, entry_type="file")
            except BaseException:
                handle.close()
                with contextlib.suppress(OSError):
                    os.unlink(leaf, dir_fd=directory_fd)
                raise
            if present_after is None:
                handle.close()
                with contextlib.suppress(OSError):
                    os.unlink(leaf, dir_fd=directory_fd)
                raise OSError(errno.ENFILE, "walks directory over the scan cap")
            greater = [
                present_index for present_index in present_after if present_index > index
            ]
            if greater:
                handle.close()
                os.unlink(leaf, dir_fd=directory_fd)
                index = max(greater) + 1
                continue
            return path, path.stem, handle
    finally:
        if owned_fd is not None:
            os.close(owned_fd)


# --------------------------------------------------------------------------- #
# The log writer
# --------------------------------------------------------------------------- #


class _WalkLog:
    """Append-only writer. No line is ever rewritten."""

    def __init__(self, path: Path, handle: BinaryIO) -> None:
        self._path = path
        self._handle = handle
        self.records = 0

    def append(self, record: Mapping[str, object]) -> None:
        """Encode and append one record, then flush. Raises OSError on failure.

        A flush failure after every byte already reached the file is the one I/O
        refusal that can leave a complete, B5-passing log; the harness still
        exits 74, because "the bytes are durable" is a different claim from "the
        log is well formed", and only the second one is true.
        """
        self._handle.write(encode_record(record))
        self._handle.flush()
        os.fsync(self._handle.fileno())
        self.records += 1

    def close(self) -> None:
        self._handle.close()


# --------------------------------------------------------------------------- #
# Section 6.1 — the validation matrix, and the walk
# --------------------------------------------------------------------------- #

# The bands come from gnd.exits, which exists precisely so this module and
# gnd/cli.py cannot drift: cli imports solve, so solve importing cli back would
# be circular, and restating the literals here was two unguarded homes for one
# normative value. 0 is not a named band -- a completed walk is not an
# allocation, it is the absence of one.
_EXIT_OK = EXIT_OK
_EXIT_HALTED = EXIT_WALK_HALTED
_EXIT_USAGE = EXIT_USAGE
_EXIT_NOINPUT = EXIT_NO_INPUT
_EXIT_INTERNAL = EXIT_INTERNAL
_EXIT_IO = EXIT_IO


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _select(
    *, start: str | None, until: str | None, skip: frozenset[str]
) -> tuple[str, ...]:
    lo = _STATION_POSITION[start] if start is not None else 0
    hi = _STATION_POSITION[until] if until is not None else len(STATIONS) - 1
    return tuple(
        name
        for index, name in enumerate(_STATION_NAMES)
        if lo <= index <= hi and name not in skip
    )


def _in_locked_order(names: Iterable[str]) -> list[str]:
    return sorted(names, key=lambda name: _STATION_POSITION[name])


def _validate(
    *,
    model: Path,
    workspace: Path,
    experiment: Path | None,
    start: str | None,
    until: str | None,
    skip: frozenset[str],
    adapter: str | None,
    adapter_policy: Path | None,
    test_argv: tuple[str, ...],
    station_timeout: Mapping[str, int],
) -> tuple[int, tuple[str, ...]] | tuple[int, None]:
    """Resolved-value stage 1 plus stages 2 through 8, first-refusal-wins.

    Stage 1's raw argument grammar belongs to the CLI parser, which is where a
    repeated flag or a malformed ``NAME=SECONDS`` is still visible. Its typed
    range and vocabulary rules are repeated here as API invariants so direct
    callers cannot bypass the command's total exit band.

    Returns ``(exit_code, None)`` on a refusal, ``(0, selected)`` otherwise.
    Nothing is spawned and no log is written on any refusal.
    """
    # Stage 1 — typed range and vocabulary rules shared by CLI and API callers.
    if adapter is not None and adapter not in {"claude", "codex"}:
        return _EXIT_USAGE, None
    if adapter is not None and adapter_policy is not None:
        return _EXIT_USAGE, None
    if any(
        type(seconds) is not int or not 1 <= seconds <= MAX_STATION_TIMEOUT_S
        for seconds in station_timeout.values()
    ):
        return _EXIT_USAGE, None

    # Stage 2 — name resolution.
    for name in (start, until):
        if name is not None and name not in _STATION_POSITION:
            return _EXIT_USAGE, None
    for name in sorted(skip) + sorted(station_timeout):
        if name not in _STATION_POSITION:
            return _EXIT_USAGE, None

    # Stage 3 — selection algebra.
    if (
        start is not None
        and until is not None
        and _STATION_POSITION[start] > _STATION_POSITION[until]
    ):
        return _EXIT_USAGE, None
    if (start is not None and start in skip) or (until is not None and until in skip):
        return _EXIT_USAGE, None
    lo = _STATION_POSITION[start] if start is not None else 0
    hi = _STATION_POSITION[until] if until is not None else len(STATIONS) - 1
    for name in skip:
        if not (lo <= _STATION_POSITION[name] <= hi):
            # Silently ignoring an inapplicable --skip lets a user believe a
            # bound was set that never was (D-63) — the same principle stage 4
            # applies to --station-timeout.
            return _EXIT_USAGE, None
    selected = _select(start=start, until=until, skip=skip)
    if not selected:
        return _EXIT_USAGE, None

    # Stage 4 — flag relevance.
    for name in station_timeout:
        if name not in selected:
            return _EXIT_USAGE, None
    if "exp-run" not in selected and (
        experiment is not None
        or test_argv
        or adapter is not None
        or adapter_policy is not None
    ):
        # `adapter is not None` means EXPLICITLY supplied: the default is
        # resolved later, which is the whole reason the parameter is
        # `str | None` rather than `str = "claude"` (D-29).
        return _EXIT_USAGE, None

    # Stage 5 — path shape.
    if experiment is not None:
        workspace_real = _real(workspace)
        experiment_real = _real(experiment)
        if experiment_real == workspace_real or workspace_real not in experiment_real.parents:
            return _EXIT_USAGE, None

    # Stage 6 — path existence.
    if not workspace.exists():
        return _EXIT_NOINPUT, None
    if not model.exists():
        return _EXIT_NOINPUT, None
    if experiment is not None and not experiment.exists():
        return _EXIT_NOINPUT, None
    if adapter_policy is not None and not adapter_policy.exists():
        return _EXIT_NOINPUT, None

    # Stage 7 — path type and access.
    if not workspace.is_dir():
        return _EXIT_IO, None
    if experiment is not None and not experiment.is_dir():
        return _EXIT_IO, None
    if not model.is_file():
        return _EXIT_IO, None
    if adapter_policy is not None:
        try:
            policy_info = adapter_policy.lstat()
        except OSError:
            return _EXIT_IO, None
        if stat.S_ISLNK(policy_info.st_mode) or not stat.S_ISREG(policy_info.st_mode):
            return _EXIT_IO, None
    if not os.access(workspace, os.W_OK):
        return _EXIT_IO, None
    try:
        walks_fd = _open_walks_directory(workspace, create=True)
        os.close(walks_fd)
    except OSError:
        return _EXIT_IO, None

    # Stage 8 — station preconditions. These are about the CONTENTS of paths, so
    # they run after those paths are known to exist and to be usable (D-40).
    if "exp-run" in selected and experiment is None:
        return _EXIT_USAGE, None
    if (
        "conformance" in selected
        and "codegen" not in selected
        and not (workspace / "project").is_dir()
    ):
        return _EXIT_USAGE, None

    return _EXIT_OK, selected


def _real(path: Path) -> Path:
    """Resolve symlinks without requiring the path to exist."""
    return Path(os.path.realpath(path))


def _build_flags(
    *,
    start: str | None,
    until: str | None,
    skip: frozenset[str],
    auto: bool,
    adapter: str | None,
    adapter_explicit: bool,
    experiment: Path | None,
    workspace: Path,
    test_argv: tuple[str, ...],
    station_timeout: Mapping[str, int],
) -> dict[str, object]:
    """The ``flags`` object, in ``_FLAG_KEYS`` order, all values JSON primitives.

    ``from``/``until`` are ``null`` when the flag was not given: the log records
    what the user supplied, and ``selected`` already records what it resolved to.
    Recording the resolved boundary instead would write different bytes for the
    same walk, which is how r3's "reproducible digest" was not one (D-30).
    """
    return {
        "from": start,
        "until": until,
        "skip": _in_locked_order(skip),
        "auto": auto,
        "adapter": adapter,
        "adapter_explicit": adapter_explicit,
        "experiment": (
            None if experiment is None else _relative_or_absolute(experiment, workspace)
        ),
        "test_argv": list(test_argv),
        "station_timeout": {
            name: station_timeout[name] for name in _in_locked_order(station_timeout)
        },
    }


def run_walk(
    model: Path,
    *,
    workspace: Path,
    experiment: Path | None = None,
    start: str | None = None,
    until: str | None = None,
    skip: frozenset[str] = frozenset(),
    auto: bool = False,
    adapter: str | None = None,
    adapter_policy: Path | None = None,
    test_argv: tuple[str, ...] = (),
    station_timeout: Mapping[str, int] = MappingProxyType({}),
    gate: Callable[[Station], str | None] = _blocking_stdin_gate,
    clock: Callable[[], datetime] = _utc_now,
    spawn: Callable[[StationSpawn], StationOutcome] = _spawn_station,
) -> int:
    """Walk the selected stations, gating each, and return the harness's exit code.

    The returned code is the harness's own control plane (spec 6.2). It is never
    a station's exit, and it is never a verdict about the work: a station exiting
    11 must not make ``gnd solve`` claim ``EXIT_COLLISION`` about itself.
    """
    code, selected = _validate(
        model=model,
        workspace=workspace,
        experiment=experiment,
        start=start,
        until=until,
        skip=skip,
        adapter=adapter,
        adapter_policy=adapter_policy,
        test_argv=test_argv,
        station_timeout=station_timeout,
    )
    if selected is None:
        return code

    adapter_explicit = adapter is not None or adapter_policy is not None
    resolved_adapter = (
        (adapter or (None if adapter_policy is not None else "claude"))
        if "exp-run" in selected
        else None
    )
    adapter_policy_token: str | None = None
    if adapter_policy is not None:
        try:
            adapter_policy_token = _adapter_policy_token(adapter_policy)
        except OSError:
            return _EXIT_IO

    walks_fd: int | None = None
    try:
        walks_fd = _open_walks_directory(workspace, create=False)
        walk_path, walk_id, walk_handle = _allocate_walk_file(
            workspace / "walks", directory_fd=walks_fd
        )
    except OSError:
        if walks_fd is not None:
            with contextlib.suppress(OSError):
                os.close(walks_fd)
        return _EXIT_IO
    assert walks_fd is not None  # narrowed after the successful allocation path

    paths = WalkPaths(
        model=model,
        workspace=workspace,
        experiment=experiment,
        walk_id=walk_id,
        adapter=resolved_adapter,
        test_argv=test_argv,
        adapter_policy=adapter_policy,
        adapter_policy_token=adapter_policy_token,
    )

    try:
        log = _WalkLog(walk_path, walk_handle)
    except OSError:
        with contextlib.suppress(OSError):
            walk_handle.close()
        with contextlib.suppress(OSError):
            os.close(walks_fd)
        return _EXIT_IO

    result: int = _EXIT_IO
    try:
        try:
            result = _walk(
                log=log,
                paths=paths,
                selected=selected,
                flags=_build_flags(
                    start=start,
                    until=until,
                    skip=skip,
                    auto=auto,
                    adapter=(adapter_policy_token or resolved_adapter),
                    adapter_explicit=adapter_explicit,
                    experiment=experiment,
                    workspace=workspace,
                    test_argv=test_argv,
                    station_timeout=station_timeout,
                ),
                station_timeout=station_timeout,
                auto=auto,
                gate=gate,
                clock=clock,
                spawn=spawn,
                walks_fd=walks_fd,
            )
        except _InternalDefect:
            result = _EXIT_INTERNAL
    finally:
        try:
            log.close()
        except OSError:
            result = _EXIT_IO
        try:
            os.close(walks_fd)
        except OSError:
            result = _EXIT_IO
    return result


def _walk(
    *,
    log: _WalkLog,
    paths: WalkPaths,
    selected: tuple[str, ...],
    flags: Mapping[str, object],
    station_timeout: Mapping[str, int],
    auto: bool,
    gate: Callable[[Station], str | None],
    clock: Callable[[], datetime],
    spawn: Callable[[StationSpawn], StationOutcome],
    walks_fd: int,
) -> int:
    try:
        log.append(
            {
                "record": "walk",
                "walk_id": paths.walk_id,
                "schema_version": SCHEMA_VERSION,
                "model": _relative_or_absolute(paths.model, paths.workspace),
                "selected": list(selected),
                "flags": dict(flags),
                "started": _stamp(clock()),
            }
        )
    except OSError:
        return _EXIT_IO

    for name in selected:
        station = station_by_name(name)
        station_paths = paths
        argv = station.argv(station_paths)
        recorded_argv = list(argv)
        if name == "exp-run" and paths.adapter_policy is not None:
            index = recorded_argv.index("--adapter-policy") + 1
            recorded_argv[index] = paths.adapter_policy_token

        # The gate record is appended when the gate OPENS, before the spawn, so a
        # station that crashes still leaves the authorization that permitted it.
        if auto:
            authorized_by: str | None = _authorized_by("auto", "auto", clock())
            gate_io_failed = False
        else:
            # SIGINT at a gate is a DECLINE, and the guard belongs HERE rather
            # than inside any one gate: "an interrupt at a gate halts the walk"
            # is a property of the walk, so a gate that does not catch it must
            # not be able to make KeyboardInterrupt escape (D-41). The default
            # gate catches it too, and that is defence in depth, not the
            # contract.
            try:
                reply = gate(station)
            except KeyboardInterrupt:
                reply = None
                gate_io_failed = False
            except (OSError, TypeError, ValueError):
                reply = None
                gate_io_failed = True
            else:
                gate_io_failed = False
            authorized_by = (
                None if reply is None else _authorized_by("stdin", reply, clock())
            )
        try:
            log.append(
                {
                    "record": "gate",
                    "walk_id": paths.walk_id,
                    "station": name,
                    "argv": recorded_argv,
                    "authorized_by": authorized_by,
                }
            )
        except OSError:
            return _EXIT_IO
        if gate_io_failed:
            return _EXIT_IO
        if authorized_by is None:
            # A declined gate writes no `station` record: nothing was attempted.
            return _EXIT_HALTED

        if name == "exp-run" and paths.adapter_policy is not None:
            try:
                current_policy_token = _adapter_policy_token(paths.adapter_policy)
            except OSError:
                return _EXIT_IO
            if current_policy_token != paths.adapter_policy_token:
                return _EXIT_IO

        # The pre-spawn run-index set, for exp-run only. The harness never
        # creates `runs/` — writing into the experiment to make its own discovery
        # convenient would be the harness making a claim about work it does not
        # own — so a missing directory is simply an empty set.
        before = (
            _scan_indices_safe(paths.experiment / "runs")
            if name == "exp-run" and paths.experiment is not None
            else None
        )

        spawn_request = StationSpawn(
            argv=argv,
            cwd=paths.workspace,
            timeout_s=station_timeout.get(name, station.timeout),
            stdout_path=paths.workspace / _capture_stdout(paths, name),
            stderr_path=paths.workspace / _capture_stderr(paths, name),
            _walks_fd=walks_fd,
        )
        outcome = spawn(spawn_request)

        evidence: str | None
        halt = outcome.halt
        if halt is not None:
            evidence = None
        elif name == "exp-run" and paths.experiment is not None:
            after = _scan_indices_safe(paths.experiment / "runs")
            appeared = None if (after is None or before is None) else after - before
            claimed_index = _exp_run_index_from_stdout(spawn_request)
            if (
                claimed_index is not None
                and appeared is not None
                and appeared == {claimed_index}
            ):
                station_paths = dataclasses.replace(paths, run_index=claimed_index)
                evidence = station.evidence(station_paths) if station.evidence else None
            else:
                # The child must claim the same sole new run id in its bounded
                # result document. Cardinality alone cannot distinguish this
                # child from one concurrent `gnd exp run` (D-78).
                evidence = None
                halt = "evidence-ambiguous"
        else:
            evidence = station.evidence(station_paths) if station.evidence else None

        # An evidence path that escapes the workspace is not recorded, not even
        # to say it was rejected: the whole point of one workspace-relative
        # evidence type is that nothing outside the workspace can be named. The
        # escaping value never reaches the log.
        if evidence is not None and not _inside_workspace(evidence, paths.workspace):
            evidence = None
            halt = "evidence-ambiguous"

        try:
            log.append(
                {
                    "record": "station",
                    "walk_id": paths.walk_id,
                    "station": name,
                    "exit": outcome.exit_code,
                    "evidence": evidence,
                    "halt": halt,
                }
            )
        except OSError:
            return _EXIT_IO

        if halt == "spawn-error":
            return _EXIT_IO
        if halt is not None:
            return _EXIT_HALTED
        if outcome.exit_code not in station.accepted_exits:
            return _EXIT_HALTED

    return _EXIT_OK


def _inside_workspace(relpath: str, workspace: Path) -> bool:
    """Is *relpath* a workspace-relative path that stays inside the workspace?

    Three escapes are refused by name because each is a different mechanism: an
    absolute path, a ``..`` segment, and a symlink whose target leaves the tree.
    The last is why this resolves rather than only inspecting the string.
    """
    if relpath.startswith("/") or PurePosixPath(relpath).is_absolute():
        return False
    if any(part == ".." for part in PurePosixPath(relpath).parts):
        return False
    workspace_real = _real(workspace)
    target_real = _real(workspace / relpath)
    return target_real == workspace_real or workspace_real in target_real.parents


def _exp_run_index_from_stdout(spawn: StationSpawn) -> int | None:
    """Read the bounded exp-run result and return its claimed run index.

    ``gnd exp run`` emits the exact terminal ``result.json`` bytes on stdout;
    both result schemas carry ``run_id``. Reading that child-authored identity
    closes the attribution gap left by a directory set difference alone.
    """
    owned_walks_fd: int | None = None
    walks_fd = spawn._walks_fd
    descriptor: int | None = None
    try:
        if walks_fd is None:
            owned_walks_fd = _open_walks_directory(spawn.cwd, create=False)
            walks_fd = owned_walks_fd
        leaf = _capture_leaf_name(spawn, spawn.stdout_path)
        flags = os.O_RDONLY
        flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
        descriptor = os.open(leaf, flags, dir_fd=walks_fd)
        chunks = bytearray()
        while len(chunks) <= _MAX_RESULT_STDOUT_BYTES:
            block = os.read(
                descriptor,
                min(64 * 1024, _MAX_RESULT_STDOUT_BYTES + 1 - len(chunks)),
            )
            if not block:
                break
            chunks.extend(block)
        if len(chunks) > _MAX_RESULT_STDOUT_BYTES:
            return None
        document = _rf7_input.loads(bytes(chunks))
        if not isinstance(document, dict):
            return None
        run_id = document.get("run_id")
        if not isinstance(run_id, str):
            return None
        matched = _RUN_DIR.fullmatch(run_id)
        return None if matched is None else int(matched.group(1))
    except (OSError, TypeError, ValueError):
        return None
    finally:
        if descriptor is not None:
            with contextlib.suppress(OSError):
                os.close(descriptor)
        if owned_walks_fd is not None:
            with contextlib.suppress(OSError):
                os.close(owned_walks_fd)


def _scan_indices_safe(directory: Path) -> set[int] | None:
    """Run-index discovery that never raises.

    Once a child has been spawned, every failure of the harness's own discovery
    is ``evidence-ambiguous``, never an I/O refusal (D-59): the station ran, and
    what the harness cannot do is say what it produced. That is a halt, not a 74.
    """
    if not directory.is_dir():
        return set()
    try:
        return _scan_indices(directory, _RUN_DIR, entry_type="directory")
    except OSError:
        return None
