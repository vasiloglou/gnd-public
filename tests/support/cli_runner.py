"""Shared execution boundaries for test-controlled commands and GND main calls."""

from __future__ import annotations

import contextlib
import io
import locale
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from support.repository import REPO_ROOT

from gnd import cli


@dataclass(frozen=True)
class RunResult:
    argv: tuple[str, ...]
    returncode: int
    stdout: bytes
    stderr: bytes


def completed_text(result: RunResult) -> subprocess.CompletedProcess[str]:
    """Project raw streams as subprocess.run(text=True) would on this runtime."""
    encoding = "utf-8" if sys.flags.utf8_mode else locale.getencoding()

    def decode(raw: bytes) -> str:
        with io.TextIOWrapper(io.BytesIO(raw), encoding=encoding, newline=None) as stream:
            return stream.read()

    return subprocess.CompletedProcess(
        list(result.argv), result.returncode, decode(result.stdout), decode(result.stderr)
    )


def run_gnd_text(*args: str, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    """Run this checkout's GND CLI with the standard text-mode projection."""
    return completed_text(run_process([sys.executable, "-m", "gnd", *args], cwd=cwd))


def run_process(
    argv: Sequence[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    stdin: bytes | None = None,
    timeout: float | None = None,
) -> RunResult:
    """Run without shell expansion and retain exact streams and exit status."""
    arguments = tuple(argv)
    completed = subprocess.run(
        arguments,
        cwd=cwd,
        env=None if env is None else dict(env),
        input=stdin,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    return RunResult(arguments, completed.returncode, completed.stdout, completed.stderr)


def run_main(
    argv: Sequence[str], *, cwd: Path | None = None, capture_stderr: bool = True
) -> RunResult:
    """Call the CLI in process while restoring cwd and stream redirection."""
    arguments = tuple(argv)
    stdout = io.StringIO()
    stderr = io.StringIO()
    directory = contextlib.nullcontext() if cwd is None else contextlib.chdir(cwd)
    error_stream = contextlib.redirect_stderr(stderr) if capture_stderr else contextlib.nullcontext()
    with directory, contextlib.redirect_stdout(stdout), error_stream:
        try:
            code = cli.main(list(arguments))
        except SystemExit as error:
            code = int(error.code or 0)
    return RunResult(
        arguments,
        int(code),
        stdout.getvalue().encode("utf-8", errors="surrogatepass"),
        stderr.getvalue().encode("utf-8", errors="surrogatepass"),
    )
