

from __future__ import annotations

import base64
import json
import sys
import time
from pathlib import Path

from gnd.declared_adapter import (
    MAX_BUNDLE_FILES,
    MAX_BUNDLE_TOTAL_BYTES,
    MAX_HTTP_HEADER_BYTES,
    MAX_HTTP_RESPONSE_BYTES,
    apply_candidate_bundle,
)
from gnd.exp.adapter_policy import MAX_ADAPTER_POLICY_BYTES, read_adapter_policy
from gnd.exp.session_contract import DataDrivenContract

ROOT = Path(__file__).resolve().parents[1]


def test_t01_t03_phase6_caps_are_fixed() -> None:
    assert MAX_ADAPTER_POLICY_BYTES == 256 * 1024
    assert MAX_HTTP_HEADER_BYTES == 64 * 1024
    assert MAX_HTTP_RESPONSE_BYTES == 1024 * 1024
    assert MAX_BUNDLE_TOTAL_BYTES == 1024 * 1024
    assert MAX_BUNDLE_FILES == 256


def test_t01_maximum_argv_cardinality_validates_under_five_seconds(tmp_path: Path) -> None:
    contract = DataDrivenContract.model_validate_json(
        (ROOT / "tests/fixtures/v61-phase6/contracts/command.json").read_bytes()
    )
    document = {
        "schema_version": 1,
        "policy_id": "local-command",
        "kind": "command",
        "executable": sys.executable,
        "argv": [*[f"word-{index}" for index in range(4095)], "{prompt}"],
        "version_argv": ["--version"],
        "prompt_transport": "argv",
        "environment_allowlist": [],
    }
    policy = tmp_path / "policy.json"
    encoded = json.dumps(document).encode()
    assert len(encoded) < MAX_ADAPTER_POLICY_BYTES
    policy.write_bytes(encoded)
    started = time.monotonic()
    resolved = read_adapter_policy(policy, declaration=contract.adapter)
    assert time.monotonic() - started < 5.0
    assert len(resolved.policy.argv) == 4096


def test_t02_maximum_bundle_applies_under_five_seconds(tmp_path: Path) -> None:
    chunks = [b"x" * 4096 for _ in range(MAX_BUNDLE_FILES)]
    assert sum(map(len, chunks)) == MAX_BUNDLE_TOTAL_BYTES
    content = json.dumps(
        {
            "schema_version": 1,
            "files": [
                {
                    "path": f"rows/{index:03d}.bin",
                    "content_base64": base64.b64encode(chunk).decode(),
                }
                for index, chunk in enumerate(chunks)
            ],
        },
        separators=(",", ":"),
    )
    started = time.monotonic()
    apply_candidate_bundle(content, candidate_root=tmp_path)
    assert time.monotonic() - started < 5.0
    assert len(tuple((tmp_path / "rows").iterdir())) == MAX_BUNDLE_FILES
