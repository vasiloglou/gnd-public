"""Corpus-first contract-v6 closure."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from gnd.exp.session_contract import DataDrivenContract

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/v61-phase6-exact-contract"
COMMAND = json.loads((FIXTURE / "contracts/command.json").read_text(encoding="utf-8"))
OPENAI = json.loads((FIXTURE / "contracts/openai.json").read_text(encoding="utf-8"))


def test_a01_a02_contract_v6_is_closed_and_version_dispatched() -> None:
    command = DataDrivenContract.model_validate(COMMAND)
    openai = DataDrivenContract.model_validate(OPENAI)
    assert command.schema_version == openai.schema_version == 6
    assert command.adapter.policy_id == "local-command"
    assert openai.adapter.parameters.model == "stub-model-1"
    assert command.model_dump(mode="json") == COMMAND


@pytest.mark.parametrize("field", ["executable", "argv", "base_url", "credential_env"])
def test_contract_never_accepts_process_policy(field: str) -> None:
    dirty = copy.deepcopy(COMMAND)
    dirty["adapter"][field] = "forbidden"
    with pytest.raises(ValidationError):
        DataDrivenContract.model_validate(dirty)


def test_v5_relabel_and_v6_injection_both_refuse() -> None:
    dirty = copy.deepcopy(COMMAND)
    dirty["schema_version"] = 5
    with pytest.raises(ValidationError):
        DataDrivenContract.model_validate(dirty)
