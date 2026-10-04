"""Trusted local adapter-policy parsing and separation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gnd.exp.adapter_policy import AdapterPolicyError, read_adapter_policy
from gnd.exp.session_contract import DataDrivenContract

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/public-local-adapter-policy"


def _contract(name: str) -> DataDrivenContract:
    return DataDrivenContract.model_validate_json((FIXTURE / f"contracts/{name}.json").read_bytes())


def test_a03_policy_id_must_match_contract(tmp_path: Path) -> None:
    document = json.loads((FIXTURE / "policies/command-argv.json").read_text())
    document["policy_id"] = "wrong"
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(AdapterPolicyError, match="policy id"):
        read_adapter_policy(path, declaration=_contract("command").adapter)


def test_command_and_openai_policies_resolve(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PHASE6_API_KEY", "canary-value")
    command = read_adapter_policy(
        FIXTURE / "policies/command-argv.json",
        declaration=_contract("command").adapter,
    )
    openai = read_adapter_policy(
        FIXTURE / "policies/openai-loopback.json",
        declaration=_contract("openai").adapter,
    )
    assert command.policy.kind == "command"
    assert openai.policy.kind == "openai-compatible"
    assert openai.model == "stub-model-1"


def test_credential_environment_name_is_refused_for_command(tmp_path: Path) -> None:
    document = json.loads((FIXTURE / "policies/command-argv.json").read_text())
    document["environment_allowlist"].append("OPENAI_API_KEY")
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(AdapterPolicyError, match="credential"):
        read_adapter_policy(path, declaration=_contract("command").adapter)


@pytest.mark.parametrize(
    "mutation,match",
    [
        (lambda row: row.update(argv=["Bearer literal", "{prompt}"]), "credential"),
        (lambda row: row.update(argv=["OPENAI_API_KEY=value", "{prompt}"]), "credential"),
        (lambda row: row.update(argv=["prefix-{prompt}"]), "whole"),
        (lambda row: row.update(unexpected=True), "extra"),
    ],
)
def test_c08_c11_command_policy_refusals(tmp_path: Path, mutation, match: str) -> None:
    document = json.loads((FIXTURE / "policies/command-argv.json").read_text())
    mutation(document)
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(AdapterPolicyError, match=match):
        read_adapter_policy(path, declaration=_contract("command").adapter)


def test_a11_a14_missing_nonregular_and_hostile_policy_inputs(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    with pytest.raises(AdapterPolicyError) as absent:
        read_adapter_policy(missing, declaration=_contract("command").adapter)
    assert absent.value.kind == "missing"

    directory = tmp_path / "directory"
    directory.mkdir()
    with pytest.raises(AdapterPolicyError) as nonregular:
        read_adapter_policy(directory, declaration=_contract("command").adapter)
    assert nonregular.value.kind == "io"

    hostile = tmp_path / "hostile.json"
    hostile.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
    with pytest.raises(AdapterPolicyError, match="duplicate JSON key"):
        read_adapter_policy(hostile, declaration=_contract("command").adapter)

    document = json.loads((FIXTURE / "policies/command-argv.json").read_text())
    document["executable"] = "phase6-definitely-missing-executable"
    hostile.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(AdapterPolicyError) as executable:
        read_adapter_policy(hostile, declaration=_contract("command").adapter)
    assert executable.value.kind == "missing"


def test_a04_a06_openai_model_and_url_rules(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("PHASE6_API_KEY", "canary-value")
    document = json.loads((FIXTURE / "policies/openai-loopback.json").read_text())
    document["base_url"] = "http://example.com/v1"
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(AdapterPolicyError, match="loopback"):
        read_adapter_policy(path, declaration=_contract("openai").adapter)

    command = json.loads((FIXTURE / "policies/command-argv.json").read_text())
    command["argv"].append("{model}")
    path.write_text(json.dumps(command), encoding="utf-8")
    with pytest.raises(AdapterPolicyError, match="agree"):
        read_adapter_policy(path, declaration=_contract("command").adapter)
