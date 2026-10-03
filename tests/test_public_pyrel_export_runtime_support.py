from __future__ import annotations

import functools
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CORPUS = REPO / "tests/fixtures/pyrel-export"
ANSWERS = CORPUS / "answers"
BASICS = REPO / "tests/fixtures/pyrel-oracle/basics.orm.yaml"
POPULATION = REPO / "tests/fixtures/pyrel-oracle/population.basics_pass.yaml"
RUNTIME = REPO / "src/gnd/export/pyrel_runtime.py"

def cli(*args: str, cwd: Path, timeout: int = 30) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO / "src")
    return subprocess.run([sys.executable, "-m", "gnd", "export", "pyrel", *args],
                          cwd=cwd, env=env, capture_output=True, text=True,
                          timeout=timeout, check=False)


@functools.cache
def require_export() -> None:
    result = cli("--help", cwd=REPO)
    assert result.returncode == 0, (
        "EXPORT_NOT_IMPLEMENTED: gnd export pyrel --help must exit 0; "
        f"got {result.returncode}: {result.stderr[-1000:]}"
    )


def export(tmp_path: Path, model: Path = BASICS, *options: str) -> Path:
    require_export()
    program = tmp_path / "program.py"
    result = cli(str(model), "--out", str(program), *options, cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert program.is_file(), "successful export did not produce an artifact"
    return program


def normalize(report: dict) -> dict:
    result = dict(report)
    result["model"], result["population"] = "MODEL", "POPULATION"
    return result


def assert_report(actual: dict, expected: dict) -> None:
    rows = actual["verdicts"]
    refs = [row["constraint_ref"] for row in rows]
    assert len(refs) == len(set(refs)), "duplicate constraint reference"
    assert rows, "empty report"
    assert all(row["status"] != "error" for row in rows), "evaluation error"
    assert "acceptance_ready" not in actual
    assert normalize(actual) == expected


def execute(program: Path, population: Path, out: Path, *options: str,
            python: str | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env["RAI_BUILD_DIR"] = str(program.parent / "scratch-build")
    command = ([python, str(program)] if python else
               ["uv", "run", "--script", str(program)])
    return subprocess.run([*command, str(population), "--out", str(out), *options],
                          cwd=program.parent, env=env, capture_output=True, text=True,
                          timeout=600, check=False)

