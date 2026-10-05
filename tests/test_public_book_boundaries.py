"""Current advisory-modality and input-seal boundaries over reviewed synthetic fixtures."""
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
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any

import pytest
from jsonschema import Draft202012Validator
from public_example_helpers import ref_to_id
from ruamel.yaml import YAML

from gnd.report import load_report_schema


def _public_boundary_workspace():
    archive = Path(__file__).parent / "fixtures/public-book-boundaries/workspace.json.gz"
    assert archive.is_file() and not archive.is_symlink()
    with archive.open("rb") as stream:
        packed = stream.read(32 * 1024 + 1)
    assert len(packed) <= 32 * 1024
    assert hashlib.sha256(packed).hexdigest() == '70ec73c1a3ccc56a1e3c91bbcbce0e3e18f7828f91ffc17bab245df9089108e8'
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        expanded = stream.read(128 * 1024 + 1)
    assert len(expanded) <= 128 * 1024
    document = json.loads(expanded)
    assert document["schema"] == 1 and len(document["members"]) == 8
    holder = tempfile.TemporaryDirectory(prefix="gnd-public-book-boundaries-")
    root = Path(holder.name)
    values = {}
    for name, bound in document["members"].items():
        relative = PurePosixPath(name)
        assert relative.parts and not relative.is_absolute() and ".." not in relative.parts
        assert relative.as_posix() == name
        data = base64.b64decode(bound["data"], validate=True)
        assert len(data) <= 64 * 1024 and hashlib.sha256(data).hexdigest() == bound["sha256"]
        destination = root.joinpath(*relative.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        values[name] = data
    return holder, root, values
_HOLDER, REPO_ROOT, _MEMBERS = _public_boundary_workspace()
BOOKREC = REPO_ROOT / "examples/bookrec"
MODEL_PATH = BOOKREC / "EXP-006-bookrec-layout/model.orm.yaml"
PRE_PROMOTION_MODEL_PATH = BOOKREC / "records/p001-promote-genre/before.orm.yaml"
EXP006 = BOOKREC / "EXP-006-bookrec-layout"
P001_HISTORY_COMMIT = "8caad962ba6c2d613a1a9ed295f912aecfb7fc98"
GENRE_GUARD = "recommendation_matches_preferred_genre"
BOOKREC_GUARDS = {"recommendation_excludes_rated_books", "recommendation_excludes_adult_books_for_minors", GENRE_GUARD}
JsonObject = dict[str, Any]
REPORT_VALIDATOR = Draft202012Validator(load_report_schema())
def _git_blob(commit: str, relative: str) -> bytes:
    assert commit == P001_HISTORY_COMMIT
    assert relative == "examples/bookrec/populations/genre-only.population.json"
    return _MEMBERS[relative]

@pytest.fixture(autouse=True)
def _public_local_adapter_sentinel(tmp_path, monkeypatch):
    """Keep the original negative branch local even if its seal regresses."""
    directory = tmp_path / "local-provider-sentinel"
    directory.mkdir()
    executable = directory / "claude"
    executable.write_text("#!/usr/bin/env python3\nimport sys\nif '--version' in sys.argv:\n print('local-seal-sentinel 1.0')\nelse:\n sys.stdin.buffer.read()\nraise SystemExit(97)\n", encoding="utf-8")
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(directory) + os.pathsep + os.environ.get("PATH", ""))

def _read_json(path: Path) -> JsonObject:
    """Read one committed JSON object."""
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), path
    return value


def _read_model(path: Path = MODEL_PATH) -> JsonObject:
    """Read a model as the YAML mapping used by the independent helper."""
    value = YAML(typ="safe").load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), path
    return value


def _run_gnd_json(*args: str) -> tuple[int, JsonObject]:
    """Run GND through the required subprocess interface and parse stdout."""
    completed = subprocess.run(
        [sys.executable, "-m", "gnd", *args, "--format", "json"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert completed.stdout, completed.stderr
    payload = json.loads(completed.stdout)
    assert isinstance(payload, dict)
    return completed.returncode, payload


def _run_check(model_path: Path, population_path: Path) -> tuple[int, JsonObject]:
    """Run ``gnd check`` and require a schema-valid report."""
    code, report = _run_gnd_json("check", str(model_path), str(population_path))
    REPORT_VALIDATOR.validate(report)
    return code, report


def _guard_verdicts(
    model: Mapping[str, Any],
    report: Mapping[str, Any],
    expected_ids: set[str] = BOOKREC_GUARDS,
) -> JsonObject:
    """Resolve positional verdict references to stable guarded IDs."""
    ids = ref_to_id(model)
    resolved = {
        ids[str(verdict["constraint_ref"])]: verdict
        for verdict in report["verdicts"]
        if str(verdict["constraint_ref"]) in ids
        and ids[str(verdict["constraint_ref"])] in expected_ids
    }
    assert set(resolved) == expected_ids
    return resolved


def test_genre_only_drift_is_advisory(tmp_path: Path) -> None:
    """Exclude checking the promoted model or attributing its old warning elsewhere."""
    model = _read_model(PRE_PROMOTION_MODEL_PATH)
    population_relative = "examples/bookrec/populations/genre-only.population.json"
    population_bytes = _git_blob(P001_HISTORY_COMMIT, population_relative)
    population_path = tmp_path / "genre-only.population.json"
    population_path.write_bytes(population_bytes)
    code, report = _run_check(PRE_PROMOTION_MODEL_PATH, population_path)
    verdicts = _guard_verdicts(model, report)
    warning_ids = {
        constraint_id
        for constraint_id, verdict in verdicts.items()
        if verdict["verdict"] == "warning"
    }

    assert code == report["exit_code"] == 0
    assert warning_ids == {GENRE_GUARD}
    assert verdicts[GENRE_GUARD]["modality"] == "deontic"
    assert verdicts[GENRE_GUARD]["offending_facts"] == [
        {"$u": "u-cy", "$b": "b-dune", "$g": "science-fiction"}
    ]


def test_pinned_architecture_contract_refuses_a_flipped_byte(tmp_path: Path) -> None:
    """P4-05. OQ-P4-1's one executable claim, asserting the CAUSE not the band.

    Exit 3 is emitted by five unrelated causes, so a row asserting only the
    number can pass while the digest check is dead.
    """
    scratch = tmp_path / "EXP-006-bookrec-layout"
    # A scratch COPY, so the committed experiment is never mutated by a test.
    # (This is the one copytree in the module and it copies an experiment, not
    # the project -- P4-11 asserts the project is never copied.)
    import shutil as _shutil

    _shutil.copytree(EXP006, scratch, ignore=_shutil.ignore_patterns("runs"))

    pinned = scratch / "input" / "architecture.contract.yaml"
    original = pinned.read_bytes()
    # ONE byte, same length: this isolates the digest check from the size check,
    # so the row cannot pass on a length mismatch the digest never had to catch.
    flipped = original.replace(b"known-user-recommend", b"known-user-recommenD")
    assert len(flipped) == len(original) and flipped != original
    pinned.write_bytes(flipped)

    completed = subprocess.run(
        [sys.executable, "-m", "gnd", "exp", "run", str(scratch), "--adapter", "claude"],
        cwd=REPO_ROOT, check=False, capture_output=True, text=True,
    )

    assert completed.returncode == 3, completed.stdout + completed.stderr
    combined = completed.stdout + completed.stderr
    # The CAUSE, not the band: exit 3 is emitted by five unrelated causes.
    contract = _read_json(EXP006 / "session.contract.json")
    index = [row["path"] for row in contract["cases"][0]["inputs"]].index(
        "input/architecture.contract.yaml"
    )
    assert f"cases.0.inputs.{index}.sha256" in combined, combined
    assert "experiment:session-contract-invalid" in combined
    assert not (scratch / "runs").exists(), "an agent must not start on unpinned bytes"

    # The control: unflipped, the same scratch copy gets past contract reading.
    pinned.write_bytes(original)
    clean = subprocess.run(
        [sys.executable, "-m", "gnd", "exp", "run", str(scratch), "--adapter", "no-such-adapter"],
        cwd=REPO_ROOT, check=False, capture_output=True, text=True,
    )
    assert clean.returncode != 3, "the contract is refused even unflipped -- P4-05 proves nothing"

