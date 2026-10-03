"""Run a generated project's smoke module in a venv that cannot see GND's tree.

v5.1 Phase 1 §6.2. The milestone's headline claim is that an OUTSIDER can run
what `gnd codegen` produced. Every softer arrangement -- running the module
under this suite's interpreter, or with the checkout on `PYTHONPATH` -- proves
only that the module works for someone who already has GND importable, which
is precisely the person the claim is not about.

Three isolation levers, each closing a different leak:

* the venv is built OUTSIDE the checkout and installs the distribution as a
  BUILT WHEEL, so nothing resolves through the source tree;
* the child clears ``PYTHONPATH`` and sets ``PYTHONNOUSERSITE=1``, closing the
  two ambient paths a developer machine adds;
* the child's cwd is the project root, never the checkout, so a relative import
  or a stray `conftest.py` above cannot reach GND either.

Building the wheel is the slow part, so it happens once per session and is
reused (D-P1.7 put this lane in the default gate, which makes its cost a
standing cost rather than an opt-in one).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from support.generated_project import (
    REPO_ROOT,
    GeneratedProject,
    declared_test_dependencies,
)


class IsolationUnavailable(RuntimeError):
    """`uv` is missing, so the isolated lane cannot run at all.

    Raised rather than skipped: D-P1.7 put this lane in the DEFAULT gate, and a
    lane that quietly degrades to a skip is a lane nobody measures -- the
    `review_runner` quarantine this phase's ruling refuses to repeat.
    """


def build_wheelhouse(destination: Path) -> Path:
    """Build the get-nick-done wheel into ``destination`` and return it."""
    if not _uv():
        raise IsolationUnavailable(
            "`uv` is not on PATH; the isolated-venv lane builds the "
            "distribution wheel with it (pyproject declares uv_build)"
        )
    destination.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [_uv(), "build", "--wheel", "--out-dir", str(destination)],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"building the distribution wheel failed\n--- stdout ---\n"
            f"{result.stdout}\n--- stderr ---\n{result.stderr}"
        )
    wheels = sorted(destination.glob("*.whl"))
    if not wheels:
        raise AssertionError(f"no wheel landed in {destination}")
    return wheels[-1]


def create_isolated_venv(
    project: GeneratedProject, *, venv_root: Path, wheelhouse: Path
) -> Path:
    """Create a venv outside the checkout carrying ONLY the project's own deps.

    The dependency list is read from the generated `pyproject.toml`, never
    restated here: the claim is that what the project DECLARES is sufficient,
    so a runner that installed a hand-written list would be marking its own
    homework.
    """
    declared = declared_test_dependencies(project)
    if not declared:
        raise AssertionError(
            "the generated pyproject declares no test-time dependencies, so "
            "there is nothing to install and the smoke module cannot import "
            "gnd.archsmoke (this is exactly what D-P1.2 repaired)"
        )
    subprocess.run(
        [_uv(), "venv", str(venv_root)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    python = _venv_python(venv_root)
    install = subprocess.run(
        [
            _uv(),
            "pip",
            "install",
            "--python",
            str(python),
            "--find-links",
            str(wheelhouse),
            *declared,
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if install.returncode != 0:
        raise AssertionError(
            f"installing {declared} into the isolated venv failed\n"
            f"--- stdout ---\n{install.stdout}\n--- stderr ---\n{install.stderr}"
        )
    return python


def run_in_isolation(
    project: GeneratedProject, *, python: Path, argv: list[str] | None = None
) -> subprocess.CompletedProcess[str]:
    """Run the project's smoke module under ``python``, from the project root."""
    command = argv or [
        str(python),
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:randomly",
        project.smoke_module.name,
    ]
    return subprocess.run(
        command,
        cwd=project.root,
        check=False,
        capture_output=True,
        text=True,
        env=_isolated_environment(),
    )


def import_origin(python: Path, module: str, *, cwd: Path) -> str:
    """Where ``module`` resolves from inside the venv -- empty when it does not.

    T1.2b's instrument: the assertion is not "gnd is importable" but "the file
    it imports is NOT in the checkout".
    """
    probe = (
        f"import importlib.util, sys;"
        f"spec = importlib.util.find_spec({module!r});"
        f"sys.stdout.write(spec.origin or '' if spec else '')"
    )
    result = subprocess.run(
        [str(python), "-c", probe],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        env=_isolated_environment(),
    )
    return result.stdout.strip()


def _isolated_environment() -> dict[str, str]:
    """The child environment, with both ambient import paths closed."""
    environment = {
        key: value
        for key, value in os.environ.items()
        if key not in {"PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV"}
    }
    environment["PYTHONNOUSERSITE"] = "1"
    return environment


def _venv_python(venv_root: Path) -> Path:
    candidate = venv_root / ("Scripts" if sys.platform == "win32" else "bin") / "python"
    if not candidate.exists():
        raise AssertionError(f"no interpreter at {candidate} after `uv venv`")
    return candidate


def _uv() -> str | None:
    from shutil import which

    return which("uv")
