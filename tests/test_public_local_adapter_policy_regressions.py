"""Regressions reproduced from the Phase-6 adversarial diff review."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import pytest

import gnd.declared_adapter as declared
from gnd.agent_cli import BoundedProcessResult
from gnd.exp.adapter_policy import (
    MAX_POLICY_STRING_BYTES,
    AdapterPolicyError,
    read_adapter_policy,
)
from gnd.exp.session_contract import DataDrivenContract

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/public-local-adapter-policy"


def test_review_invalid_url_port_is_refused_during_policy_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    document = json.loads((FIXTURE / "policies/openai-loopback.json").read_text())
    document["base_url"] = "https://example.com:notaport/v1"
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps(document), encoding="utf-8")
    monkeypatch.setenv("PHASE6_API_KEY", "secret")
    contract = DataDrivenContract.model_validate_json(
        (FIXTURE / "contracts/openai.json").read_bytes()
    )
    with pytest.raises(AdapterPolicyError, match="port"):
        read_adapter_policy(policy, declaration=contract.adapter)


def test_review_credential_header_is_bounded_before_connect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PHASE6_API_KEY", "x" * MAX_POLICY_STRING_BYTES)
    contract = DataDrivenContract.model_validate_json(
        (FIXTURE / "contracts/openai.json").read_bytes()
    )
    with pytest.raises(AdapterPolicyError, match="credential.*cap"):
        read_adapter_policy(
            FIXTURE / "policies/openai-loopback.json",
            declaration=contract.adapter,
        )


def test_review_command_cleanup_failure_is_closed_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract = DataDrivenContract.model_validate_json(
        (FIXTURE / "contracts/command.json").read_bytes()
    )
    document = json.loads((FIXTURE / "policies/command-argv.json").read_text())
    document["executable"] = sys.executable
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(json.dumps(document), encoding="utf-8")
    policy = read_adapter_policy(policy_path, declaration=contract.adapter)
    cleanup = BoundedProcessResult(
        status="cleanup-failed",
        spawned=True,
        timed_out=False,
        termination="killed",
        return_code=-9,
        signal=9,
        spawn_error=None,
        started_monotonic=1.0,
        ended_monotonic=2.0,
        elapsed_seconds=1.0,
        argv_sha256="0" * 64,
        argv_count=1,
        stdout_observed_bytes=0,
        stdout_retained_bytes=0,
        stdout_truncated=False,
        stderr_observed_bytes=0,
        stderr_retained_bytes=0,
        stderr_truncated=False,
        environment=(),
        termination_steps=("sigterm", "sigkill"),
        process_group_cleaned=False,
        stdout=b"",
        stderr=b"",
    )

    async def failed_cleanup(*_args, **_kwargs):
        return cleanup

    monkeypatch.setattr(declared, "run_bounded_process", failed_cleanup)
    result = asyncio.run(
        declared.invoke_declared_adapter(policy, prompt="p", cwd=tmp_path, timeout_seconds=1)
    )
    assert result.status == "failed"
    assert result.process_group_cleaned is False
