"""Fresh local completeness and fixture-owned smoke configuration controls."""
from __future__ import annotations

import base64
import gzip
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

import pytest
import test_public_book_boundaries as _boundaries
import test_public_book_runtime as _runtime

import gnd

JsonObject = dict[str, Any]

def _public_workflow_workspace():
    holder = tempfile.TemporaryDirectory(prefix="gnd-public-book-workflow-")
    root = Path(holder.name)
    reused = dict(_runtime._MEMBERS)
    reused.update({p: data for p, data in _boundaries._MEMBERS.items() if p.startswith("examples/bookrec/EXP-006-bookrec-layout/")})
    assert len(reused) == 52
    for name, data in reused.items():
        relative = PurePosixPath(name)
        assert relative.parts and not relative.is_absolute() and ".." not in relative.parts
        assert len(data) <= 64 * 1024
        destination = root.joinpath(*relative.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    archive = Path(__file__).parent / "fixtures/public-book-workflow/workspace.json.gz"
    assert archive.is_file() and not archive.is_symlink()
    with archive.open("rb") as stream:
        packed = stream.read(4097)
    assert len(packed) <= 4096 and hashlib.sha256(packed).hexdigest() == '1bda1f1244c10fc3507e33c268a73c60f3a13a3010796c4848cfbf7baba54058'
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        expanded = stream.read(8193)
    assert len(expanded) <= 8192
    document = json.loads(expanded)
    assert document["schema"] == 1 and len(document["members"]) == 4
    for name, member in document["members"].items():
        relative = PurePosixPath(name)
        assert relative.parts and not relative.is_absolute() and ".." not in relative.parts
        data = base64.b64decode(member["data"], validate=True)
        assert len(data) <= 4096 and hashlib.sha256(data).hexdigest() == member["sha256"]
        destination = root.joinpath(*relative.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    return holder, root
_HOLDER, REPO_ROOT = _public_workflow_workspace()
BOOKREC = REPO_ROOT / "examples/bookrec"
PROJECT = BOOKREC / "project"
EXP006 = BOOKREC / "EXP-006-bookrec-layout"
EXP007 = BOOKREC / "EXP-007-bookrec-layout-gate"
SMOKE_MODULE = "test_architecture_smoke_bookrec.py"
_sha256 = lambda raw: hashlib.sha256(raw).hexdigest()

@pytest.fixture(scope="module", autouse=True)
def _public_fresh_local_sessions():
    bin_dir = REPO_ROOT / "local-adapter"
    bin_dir.mkdir()
    adapter = bin_dir / "claude"
    adapter.write_text("#!/usr/bin/env python3\nimport sys\nif '--version' in sys.argv:\n print('local-synthetic-session 1.0')\nelse:\n sys.stdin.buffer.read()\n print('Synthetic candidate left unchanged.')\n", encoding="utf-8")
    adapter.chmod(0o755)
    home = REPO_ROOT / "local-home"
    home.mkdir()
    environment = {"PATH": str(bin_dir) + os.pathsep + str(Path(sys.executable).parent) + os.pathsep + "/usr/bin:/bin", "HOME": str(home), "LANG": "C", "LC_ALL": "C", "PYTHONPATH": str(Path(gnd.__file__).resolve().parent.parent)}
    generation_environment = dict(environment)
    generation_environment["PYTHONPATH"] = str(PROJECT) + os.pathsep + environment["PYTHONPATH"]
    generated = subprocess.run([sys.executable, "-m", "bookrec.cli", "recommend", "--model", str(EXP006 / "model.orm.yaml"), "--input", str(BOOKREC / "populations/seed.population.json"), "--output", str(EXP006 / "candidate/population.json"), "--user", "u-minor", "--limit", "3"], cwd=PROJECT, env=generation_environment, check=False, capture_output=True, text=True, timeout=60)
    assert generated.returncode == 0, generated.stdout + generated.stderr
    for experiment, argv in [(EXP006, []), (EXP007, ["python3", "-m", "pytest", "-p", "no:randomly", f"project/{SMOKE_MODULE}", "--junit-xml=results/junit.xml", "-q"])]:
        assert not (experiment / "runs").exists()
        completed = subprocess.run([sys.executable, "-m", "gnd", "exp", "run", str(experiment), "--adapter", "claude", *[f"--test-argv={word}" for word in argv]], cwd=REPO_ROOT, env=environment, check=False, capture_output=True, text=True, timeout=60)
        assert completed.returncode == 0, completed.stdout + completed.stderr
        result = _read_json(experiment / "runs/run-0001/result.json")
        assert result["disposition"] == "accepted"

def _read_json(path: Path) -> JsonObject:
    """Read one committed JSON object."""
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), path
    return value


def test_exp006_closes_at_zero() -> None:
    """P4-04. The separate completeness gate, discharged."""
    completed = subprocess.run(
        [sys.executable, "-m", "gnd", "exp", "close", str(EXP006)],
        cwd=REPO_ROOT, check=False, capture_output=True, text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_exp007_gate_accepts_and_closes() -> None:
    """P4-25. The row the round-1 panel found missing: the gate's GREEN case.

    Three seats independently found the spec had a red case for its headline
    gate and no green one -- this milestone's defining defect class, inside the
    document written to prevent it.
    """
    result = _read_json(EXP007 / "runs" / "run-0001" / "result.json")

    assert result["acceptance_modes"] == ["tests"]
    assert result["disposition"] == "accepted"

    (feedback,) = result["feedback"]
    assert feedback["role"] == "required"
    assert feedback["reason"] is None
    assert set(feedback["passing"]) == set(feedback["required"]) == set(feedback["present"])

    completed = subprocess.run(
        [sys.executable, "-m", "gnd", "exp", "close", str(EXP007)],
        cwd=REPO_ROOT, check=False, capture_output=True, text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_testpaths_names_both_example_smoke_modules() -> None:
    """P4-13. BookRec's rows join the repository suite, in the repair's commit.

    Measured at spec time: `testpaths` is asserted by no other test, so a module
    could be emitted, committed, and never collected by anything.
    """
    import tomllib

    config = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    testpaths = config["tool"]["pytest"]["ini_options"]["testpaths"]

    assert f"examples/bookrec/project/{SMOKE_MODULE}" in testpaths
    assert (
        "examples/expense-tracker/project/test_architecture_smoke_expense_tracker.py"
        in testpaths
    )
    for entry in testpaths:
        if entry != "tests":
            assert (REPO_ROOT / entry).is_file(), entry

    collected = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:randomly",
         f"examples/bookrec/project/{SMOKE_MODULE}"],
        cwd=REPO_ROOT, check=False, capture_output=True, text=True,
    )
    assert collected.returncode == 0, collected.stdout
    assert collected.stdout.count("::test_smoke") == 3, collected.stdout


def test_smoke_module_basename_has_one_home() -> None:
    """P4-35. D4 knowingly entrenches a second spelling; bound it to one string.

    Measured: `smoke_module_relpath` returns test_architecture_smoke_model.py for
    BOTH examples, because both models are named model.orm.yaml -- so the
    emitter's own collision-avoidance rationale is already false for the two
    projects this repository ships. The committed basenames were hand-chosen.
    This row stops that one divergence from spreading: the file, its manifest
    entry, testpaths and the gate contract must all say the same string.
    """
    import tomllib

    manifest = _read_json(PROJECT / ".gnd-codegen.json")
    entries = [row for row in manifest["files"] if row["relpath"] == SMOKE_MODULE]
    config = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    acceptance = _read_json(EXP007 / "session.contract.json")["cases"][0]["acceptance"]

    assert (PROJECT / SMOKE_MODULE).is_file()
    assert len(entries) == 1 and entries[0]["ownership"] == "extension"
    assert entries[0]["sha256"] == _sha256((PROJECT / SMOKE_MODULE).read_bytes())
    assert f"examples/bookrec/project/{SMOKE_MODULE}" in (
        config["tool"]["pytest"]["ini_options"]["testpaths"]
    )
    assert all(SMOKE_MODULE in rid for rid in acceptance["required_tests"])
    assert all(SMOKE_MODULE in row["path"] or "contract" in row["path"]
               or row["path"].endswith((".yaml", ".json")) for row in acceptance["protected"])

