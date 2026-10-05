"""Live command declared-adapter behavior."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import shutil
import stat
import sys
from pathlib import Path

from gnd.cli import main
from gnd.declared_adapter import invoke_declared_adapter
from gnd.exp.adapter_policy import read_adapter_policy
from gnd.exp.session_contract import DataDrivenContract

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/public-local-adapter-policy"
SKELETON = ROOT / "tests/fixtures/skeleton"


def _bound(path: str, data: bytes, media_type: str) -> dict[str, object]:
    return {
        "path": path,
        "media_type": media_type,
        "encoding": "utf-8",
        "sha256": hashlib.sha256(data).hexdigest(),
        "size_bytes": len(data),
    }


def test_c01_argv_command_runs_without_shell(tmp_path: Path) -> None:
    shutil.copy2(FIXTURE / "agents/fake_agent.py", tmp_path / "agent.py")
    contract = DataDrivenContract.model_validate_json(
        (FIXTURE / "contracts/command.json").read_bytes()
    )
    policy = read_adapter_policy(
        FIXTURE / "policies/command-argv.json", declaration=contract.adapter
    )
    result = asyncio.run(
        invoke_declared_adapter(
            policy,
            prompt="literal ; $(no-shell)",
            cwd=tmp_path,
            timeout_seconds=5.0,
        )
    )
    assert result.status == "succeeded"


def test_c02_live_command_session_is_accepted(tmp_path: Path) -> None:
    experiment_id = "EXP-061-command-live"
    assert (
        main(
            [
                "exp",
                "init",
                experiment_id,
                "--out",
                str(tmp_path),
                "--kind",
                "data-driven",
                "--question",
                "Q1=Can a declared command produce the required candidate?",
            ]
        )
        == 0
    )
    root = tmp_path / experiment_id
    candidate = root / "candidate"
    candidate.mkdir()
    model = (SKELETON / "model.orm.yaml").read_bytes()
    accepted = (SKELETON / "population.good.yaml").read_bytes()
    rejected = (SKELETON / "population.bad.yaml").read_bytes()
    (root / "model.orm.yaml").write_bytes(model)
    (root / "input").mkdir()
    (root / "input/reference.yaml").write_bytes(accepted)
    (root / "expected").mkdir()
    (root / "expected/population.yaml").write_bytes(accepted)
    (candidate / "population.yaml").write_bytes(rejected)
    contract = {
        "schema_version": 6,
        "experiment_id": experiment_id,
        "max_attempts": 1,
        "wall_seconds": 15.0,
        "adapter": {"policy_id": "local-command", "parameters": {"model": None}},
        "cases": [
            {
                "case_id": "exact-population",
                "role": "required",
                "inputs": [_bound("input/reference.yaml", accepted, "application/yaml")],
                "acceptance": {
                    "mode": "exact-bytes",
                    "expected_outputs": [
                        {
                            **_bound("expected/population.yaml", accepted, "application/yaml"),
                            "output_id": "population",
                            "candidate_path": "population.yaml",
                            "comparison": "exact-bytes",
                        }
                    ],
                },
                "verify": {
                    "command": "check",
                    "model": _bound("model.orm.yaml", model, "application/yaml"),
                    "subject": "population.yaml",
                },
            }
        ],
    }
    (root / "session.contract.json").write_text(
        json.dumps(contract, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    encoded = base64.b64encode(accepted).decode("ascii")
    agent = tmp_path / "declared-agent.py"
    agent.write_text(
        "import base64, pathlib, sys\n"
        "if sys.argv[1:] == ['--version']:\n"
        " print('declared-agent 1'); raise SystemExit(0)\n"
        f"pathlib.Path('population.yaml').write_bytes(base64.b64decode('{encoded}'))\n",
        encoding="utf-8",
    )
    agent.chmod(agent.stat().st_mode | stat.S_IXUSR)
    policy = tmp_path / "command.policy.json"
    policy.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "policy_id": "local-command",
                "kind": "command",
                "executable": sys.executable,
                "argv": [str(agent), "{prompt}"],
                "version_argv": ["--version"],
                "prompt_transport": "argv",
                "environment_allowlist": ["PATH", "HOME", "TMPDIR", "LANG", "LC_ALL"],
            }
        ),
        encoding="utf-8",
    )

    assert main(["exp", "run", str(root), "--adapter-policy", str(policy)]) == 0
    result = json.loads((root / "runs/run-0001/result.json").read_text(encoding="utf-8"))
    attempt = json.loads(
        (root / "runs/run-0001/attempts/0001/attempt.json").read_text(encoding="utf-8")
    )
    assert result["disposition"] == "accepted"
    assert attempt["schema_version"] == 8
    assert attempt["invocation"]["policy_id"] == "local-command"

    before = sorted((root / "runs").iterdir())
    assert main(["exp", "run", str(root)]) == 64
    assert main(["exp", "run", str(root), "--adapter", "codex"]) == 64
    assert (
        main(
            [
                "exp",
                "run",
                str(root),
                "--adapter",
                "codex",
                "--adapter-policy",
                str(policy),
            ]
        )
        == 64
    )
    assert (
        main(
            [
                "exp",
                "run",
                str(root),
                "--adapter-policy",
                str(tmp_path / "missing.policy.json"),
            ]
        )
        == 66
    )
    assert sorted((root / "runs").iterdir()) == before


def test_c04_c05_stdin_transport_frames_null_and_retry_feedback(tmp_path: Path) -> None:
    agent = tmp_path / "agent.py"
    agent.write_text(
        "import pathlib,sys\npathlib.Path('stdin.bin').write_bytes(sys.stdin.buffer.read())\n",
        encoding="utf-8",
    )
    document = json.loads((FIXTURE / "policies/command-stdin.json").read_text(encoding="utf-8"))
    document["executable"] = sys.executable
    document["argv"] = [str(agent)]
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(json.dumps(document), encoding="utf-8")
    contract = DataDrivenContract.model_validate_json(
        (FIXTURE / "contracts/command.json").read_bytes()
    )
    policy = read_adapter_policy(policy_path, declaration=contract.adapter)

    first = asyncio.run(
        invoke_declared_adapter(policy, prompt="first", cwd=tmp_path, timeout_seconds=5.0)
    )
    assert first.status == "succeeded"
    envelope = json.loads((tmp_path / "stdin.bin").read_bytes())
    assert envelope == {"schema_version": 1, "prompt": "first", "feedback_base64": None}

    feedback = b'{"disposition":"retry"}\n'
    digest = hashlib.sha256(feedback).hexdigest()
    second = asyncio.run(
        invoke_declared_adapter(
            policy,
            prompt="second",
            cwd=tmp_path,
            timeout_seconds=5.0,
            feedback_bytes=feedback,
            feedback_sha256=digest,
        )
    )
    assert second.status == "succeeded"
    envelope = json.loads((tmp_path / "stdin.bin").read_bytes())
    assert envelope["feedback_base64"] == base64.b64encode(feedback).decode()
    assert digest in envelope["prompt"]


def test_c12_nonzero_command_is_closed_failure(tmp_path: Path) -> None:
    agent = tmp_path / "fail.py"
    agent.write_text("raise SystemExit(23)\n", encoding="utf-8")
    document = json.loads((FIXTURE / "policies/command-argv.json").read_text(encoding="utf-8"))
    document["executable"] = sys.executable
    document["argv"] = [str(agent), "{prompt}"]
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(json.dumps(document), encoding="utf-8")
    contract = DataDrivenContract.model_validate_json(
        (FIXTURE / "contracts/command.json").read_bytes()
    )
    result = asyncio.run(
        invoke_declared_adapter(
            read_adapter_policy(policy_path, declaration=contract.adapter),
            prompt="fail",
            cwd=tmp_path,
            timeout_seconds=5.0,
        )
    )
    assert result.status == "failed"
    assert result.exit_code == 23
