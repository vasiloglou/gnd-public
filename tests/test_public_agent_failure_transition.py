"""An agent process that fails in a transition session is recorded, not a crash.

Regression for a failure found while recording live sessions: when the agent
exited before writing any candidate, ``gnd exp run`` died with an I/O error
(exit 74) because the transition feedback required a verifier row that an
agent-failure attempt can never have, and the attempt evidence was lost.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import sys
from pathlib import Path

import pytest

from gnd.cli import main

SESSION = Path(__file__).resolve().parent / "fixtures/public-walk-floor/session"
EXPERIMENT = "EXP-900-agent-fails"


def _bound(root: Path, relative: str, media_type: str) -> dict[str, object]:
    data = (root / relative).read_bytes()
    return {"path": relative, "media_type": media_type, "encoding": "utf-8",
            "sha256": hashlib.sha256(data).hexdigest(), "size_bytes": len(data)}


def _experiment(tmp_path: Path, *, schema_version: int) -> Path:
    assert main(["exp", "init", EXPERIMENT, "--out", str(tmp_path), "--kind", "data-driven",
                 "--question", "Q1=Is a failing agent recorded?"]) == 0
    root = tmp_path / EXPERIMENT
    (root / "input").mkdir()
    (root / "candidate").mkdir()
    (root / "model.orm.yaml").write_bytes((SESSION / "model.orm.yaml").read_bytes())
    (root / "input/state.pop.yaml").write_bytes((SESSION / "input/pre.pop.yaml").read_bytes())
    case = {
        "case_id": "walk", "role": "required",
        "inputs": [_bound(root, "input/state.pop.yaml", "application/yaml")],
        "acceptance": {"mode": "transition", **({"walk": None} if schema_version == 6 else {})},
        "verify": {"command": "transition", "model": _bound(root, "model.orm.yaml", "application/yaml"),
                   "pre": "input/state.pop.yaml", "steps": "steps.json", "post": None},
    }
    contract = {"schema_version": schema_version, "experiment_id": EXPERIMENT, "max_attempts": 2,
                "wall_seconds": 60.0, "cases": [case]}
    if schema_version == 6:
        contract["adapter"] = {"policy_id": "failing-agent", "parameters": {"model": None}}
    (root / "session.contract.json").write_text(json.dumps(contract, indent=2))
    return root


def _assert_recorded(root: Path) -> None:
    result = json.loads((root / "runs/run-0001/result.json").read_text())
    assert result["disposition"] == "agent-failure"
    attempt = root / "runs/run-0001/attempts/0001"
    assert (attempt / "attempt.json").is_file(), "the attempt evidence must be retained"
    feedback = json.loads((attempt / "feedback.json").read_text())
    assert feedback["disposition"] == "agent-failure"
    assert feedback["required"] == [] or all(row["band"] is not None for row in feedback["required"])
    assert main(["exp", "validate", str(root)]) == 0


def test_a_failing_command_agent_is_recorded_as_agent_failure(tmp_path):
    root = _experiment(tmp_path, schema_version=6)
    policy = tmp_path / "failing.policy.json"
    policy.write_text(json.dumps({
        "schema_version": 1, "policy_id": "failing-agent", "kind": "command",
        "executable": sys.executable, "argv": ["-c", "import sys; sys.exit(1)"],
        "version_argv": ["--version"], "prompt_transport": "stdin",
        "environment_allowlist": ["PATH", "HOME"]}))
    assert main(["exp", "run", str(root), "--adapter-policy", str(policy)]) == 15
    _assert_recorded(root)


def test_a_failing_legacy_adapter_is_recorded_as_agent_failure(tmp_path, monkeypatch):
    root = _experiment(tmp_path, schema_version=4)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "claude"
    fake.write_text("#!/bin/sh\n[ \"$1\" = \"--version\" ] && echo 'fake-claude 1' && exit 0\nexit 1\n")
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    assert main(["exp", "run", str(root), "--adapter", "claude"]) == 15
    _assert_recorded(root)


@pytest.mark.parametrize("schema_version", [4, 6])
def test_a_failed_attempt_leaves_no_partial_run_state(tmp_path, schema_version, monkeypatch):
    root = _experiment(tmp_path, schema_version=schema_version)
    if schema_version == 4:
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        fake = bin_dir / "claude"
        fake.write_text("#!/bin/sh\nexit 1\n")
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
        argv = ["exp", "run", str(root), "--adapter", "claude"]
    else:
        policy = tmp_path / "p.json"
        policy.write_text(json.dumps({
            "schema_version": 1, "policy_id": "failing-agent", "kind": "command",
            "executable": sys.executable, "argv": ["-c", "raise SystemExit(3)"],
            "version_argv": ["--version"], "prompt_transport": "stdin",
            "environment_allowlist": ["PATH", "HOME"]}))
        argv = ["exp", "run", str(root), "--adapter-policy", str(policy)]
    assert main(argv) == 15
    assert not any(p.name.startswith(".staging") and any(p.iterdir()) for p in (root / "runs/run-0001").glob(".staging*"))


def test_a_failing_agent_in_an_exact_bytes_session_is_recorded(tmp_path):
    skeleton = Path(__file__).resolve().parent / "fixtures/skeleton"
    assert main(["exp", "init", "EXP-901-exact", "--out", str(tmp_path), "--kind", "data-driven",
                 "--question", "Q1=Is a failing agent recorded?"]) == 0
    root = tmp_path / "EXP-901-exact"
    for name in ("candidate", "input", "expected"):
        (root / name).mkdir()
    (root / "model.orm.yaml").write_bytes((skeleton / "model.orm.yaml").read_bytes())
    good = (skeleton / "population.good.yaml").read_bytes()
    (root / "input/reference.yaml").write_bytes(good)
    (root / "expected/population.yaml").write_bytes(good)
    contract = {
        "schema_version": 6, "experiment_id": "EXP-901-exact", "max_attempts": 1, "wall_seconds": 15.0,
        "adapter": {"policy_id": "failing-agent", "parameters": {"model": None}},
        "cases": [{
            "case_id": "exact", "role": "required",
            "inputs": [_bound(root, "input/reference.yaml", "application/yaml")],
            "acceptance": {"mode": "exact-bytes", "expected_outputs": [{
                **_bound(root, "expected/population.yaml", "application/yaml"),
                "output_id": "population", "candidate_path": "population.yaml", "comparison": "exact-bytes"}]},
            "verify": {"command": "check", "model": _bound(root, "model.orm.yaml", "application/yaml"),
                       "subject": "population.yaml"}}]}
    (root / "session.contract.json").write_text(json.dumps(contract))
    policy = tmp_path / "failing.policy.json"
    policy.write_text(json.dumps({
        "schema_version": 1, "policy_id": "failing-agent", "kind": "command",
        "executable": sys.executable, "argv": ["-c", "import sys; sys.exit(1)"],
        "version_argv": ["--version"], "prompt_transport": "stdin",
        "environment_allowlist": ["PATH", "HOME"]}))
    assert main(["exp", "run", str(root), "--adapter-policy", str(policy)]) == 15
    _assert_recorded(root)


def _reload_attempt(root: Path, run: str = "run-0001", versions=None):
    from gnd.exp.session_contract import DataDrivenContract
    from gnd.exp.session_store import SessionStore

    contract = DataDrivenContract.model_validate_json((root / "session.contract.json").read_bytes())
    store = SessionStore(root / "runs" / run, run_id=run, contract_id=EXPERIMENT)
    return store._load_attempt_for_resume(1, contract=contract, expected_payload_versions=versions)


def test_a_published_agent_failure_attempt_reloads(tmp_path):
    root = _experiment(tmp_path, schema_version=6)
    policy = tmp_path / "failing.policy.json"
    policy.write_text(json.dumps({
        "schema_version": 1, "policy_id": "failing-agent", "kind": "command",
        "executable": sys.executable, "argv": ["-c", "import sys; sys.exit(1)"],
        "version_argv": ["--version"], "prompt_transport": "stdin",
        "environment_allowlist": ["PATH", "HOME"]}))
    assert main(["exp", "run", str(root), "--adapter-policy", str(policy)]) == 15
    snapshot = root / "runs/run-0001/attempts/0001/candidate"
    assert snapshot.is_dir() and not any(snapshot.iterdir()), "an empty snapshot is still published"
    record, *_ = _reload_attempt(root)
    assert record.candidate_inventory.file_count == 0


def test_a_deleted_snapshot_is_still_refused(tmp_path):
    """Readers stay strict: a published snapshot that disappears is evidence tampering."""
    import shutil

    root = _experiment(tmp_path, schema_version=6)
    policy = tmp_path / "writer.policy.json"
    policy.write_text(json.dumps({
        "schema_version": 1, "policy_id": "failing-agent", "kind": "command",
        "executable": sys.executable,
        "argv": ["-c", "open('steps.json', 'w').write('not json')"],
        "version_argv": ["--version"], "prompt_transport": "stdin",
        "environment_allowlist": ["PATH", "HOME"]}))
    assert main(["exp", "run", str(root), "--adapter-policy", str(policy)]) == 15
    versions = {"walk": 8}  # the transition payload version this session published
    record, *_ = _reload_attempt(root, versions=versions)
    assert record.candidate_inventory.file_count == 1
    shutil.rmtree(root / "runs/run-0001/attempts/0001/candidate")
    with pytest.raises(ValueError, match="could not be inventoried"):
        _reload_attempt(root, versions=versions)
