"""Fresh conformance over a complete reviewed synthetic expense project."""
from __future__ import annotations

import base64
import gzip
import hashlib
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator

from gnd.conformance.report import load_conformance_schema

JsonObject = dict[str, Any]
CONFORMANCE_VALIDATOR = Draft202012Validator(load_conformance_schema())
def _public_expense_workspace():
    path = Path(__file__).parent / "fixtures/public-expense-current/workspace.json.gz"
    assert path.is_file() and not path.is_symlink()
    with path.open("rb") as stream: packed = stream.read(128 * 1024 + 1)
    assert len(packed) <= 128 * 1024 and hashlib.sha256(packed).hexdigest() == '438a305a97f476a266c5c94a3953fd667ee6e892b2a1a49ca6bbad767e5366de'
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream: expanded = stream.read(256 * 1024 + 1)
    assert len(expanded) <= 256 * 1024
    doc = json.loads(expanded)
    assert doc["schema_version"] == 1 and len(doc["members"]) == 18
    holder = tempfile.TemporaryDirectory(prefix="gnd-public-expense-current-")
    root = Path(holder.name)
    members = {}
    for name, member in doc["members"].items():
        rel = PurePosixPath(name)
        assert rel.parts and not rel.is_absolute() and ".." not in rel.parts and name == rel.as_posix()
        raw = base64.b64decode(member["data"], validate=True)
        assert len(raw) <= 64 * 1024 and hashlib.sha256(raw).hexdigest() == member["sha256"]
        destination = root.joinpath(*rel.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        members[name] = raw
    return holder, root, members
_HOLDER, REPO_ROOT, _MEMBERS = _public_expense_workspace()
EXPENSE = REPO_ROOT / "examples/expense-tracker"
MODEL_PATH = EXPENSE / "model.orm.yaml"
BASELINE_COMMIT = "9c7a464"
def _git_blob(commit: str, relative: str) -> bytes:
    assert commit == BASELINE_COMMIT and relative in {'examples/expense-tracker/conformance/baseline.json': {'commit': '9c7a464168a74cbbaa0713842bef098c65a9f3b8', 'sha256': '9fca97d1e10fae6a2735f625836a9dcaec75b9f40393660f168bdd94ac4d3add', 'bytes': 6642}, 'examples/expense-tracker/conformance/post-evolution.json': {'commit': '9c7a464168a74cbbaa0713842bef098c65a9f3b8', 'sha256': '03422d1780adbb8c0150827ec002b33b36c2d3cb2cf5c69a5bdadd00e3428d01', 'bytes': 6805}}
    data = _MEMBERS[relative]
    assert hashlib.sha256(data).hexdigest() == {'examples/expense-tracker/conformance/baseline.json': {'commit': '9c7a464168a74cbbaa0713842bef098c65a9f3b8', 'sha256': '9fca97d1e10fae6a2735f625836a9dcaec75b9f40393660f168bdd94ac4d3add', 'bytes': 6642}, 'examples/expense-tracker/conformance/post-evolution.json': {'commit': '9c7a464168a74cbbaa0713842bef098c65a9f3b8', 'sha256': '03422d1780adbb8c0150827ec002b33b36c2d3cb2cf5c69a5bdadd00e3428d01', 'bytes': 6805}}[relative]["sha256"]
    return data

def _read_json(path: Path) -> JsonObject:
    """Read one committed JSON object."""
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), path
    return value


def _run_gnd_json(*args: str) -> tuple[int, JsonObject]:
    """Run GND through its subprocess interface and parse its JSON payload."""
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


def test_expense_generated_project_is_current_after_conversion() -> None:
    """Exclude a recorded green payload that is stale, partial, or schema-invalid."""
    committed = _read_json(EXPENSE / "conformance" / "post-conversion.json")
    CONFORMANCE_VALIDATOR.validate(committed)

    assert committed["assertions"]
    assert all(assertion["ran"] is True for assertion in committed["assertions"])
    assert {row["id"] for row in committed["assertions"]} == {
        "integrity",
        "currency",
        "structural",
        "architecture",
    }
    assert committed["findings"] == []
    code, live = _run_gnd_json(
        "conformance",
        str(MODEL_PATH),
        str(EXPENSE / "project"),
    )
    CONFORMANCE_VALIDATOR.validate(live)
    assert code == 0
    assert live == committed

    for name in ("baseline.json", "post-evolution.json"):
        relative = f"examples/expense-tracker/conformance/{name}"
        assert (REPO_ROOT / relative).read_bytes() == _git_blob(BASELINE_COMMIT, relative)

