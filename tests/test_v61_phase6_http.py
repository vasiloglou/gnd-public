"""Single-turn OpenAI-compatible transport boundaries."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from gnd.cli import main
from gnd.declared_adapter import (
    MAX_HTTP_RESPONSE_BYTES,
    OpenAIResponseError,
    invoke_declared_adapter,
)
from gnd.exp.adapter_policy import read_adapter_policy
from gnd.exp.session_contract import DataDrivenContract

ROOT = Path(__file__).resolve().parents[1]
SKELETON = ROOT / "tests/fixtures/skeleton"


def _bound(path: str, data: bytes, media_type: str) -> dict[str, object]:
    return {
        "path": path,
        "media_type": media_type,
        "encoding": "utf-8",
        "sha256": hashlib.sha256(data).hexdigest(),
        "size_bytes": len(data),
    }


def _make_experiment(tmp_path: Path) -> tuple[Path, bytes]:
    experiment_id = "EXP-061-http-live"
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
                "Q1=Can one HTTP response produce the required candidate?",
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
        "adapter": {
            "policy_id": "local-openai",
            "parameters": {"model": "stub-model-1"},
        },
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
    return root, accepted


def test_http_response_cap_is_fixed() -> None:
    assert MAX_HTTP_RESPONSE_BYTES == 1024 * 1024
    assert issubclass(OpenAIResponseError, ValueError)


def test_h01_p01_live_http_session_is_accepted_and_secret_free(
    tmp_path: Path,
    monkeypatch,
) -> None:
    root, accepted = _make_experiment(tmp_path)
    observed: dict[str, object] = {"requests": 0}
    canary = "PHASE6_CANARY_314159265"

    bundle = json.dumps(
        {
            "schema_version": 1,
            "files": [
                {
                    "path": "population.yaml",
                    "content_base64": base64.b64encode(accepted).decode("ascii"),
                }
            ],
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    response = json.dumps(
        {"choices": [{"message": {"content": bundle, "role": "assistant"}}]},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            observed["requests"] = int(observed["requests"]) + 1
            observed["authorization"] = self.headers.get("Authorization")
            length = int(self.headers["Content-Length"])
            observed["body"] = json.loads(self.rfile.read(length))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

        def log_message(self, format: str, *args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        policy = tmp_path / "openai.policy.json"
        policy.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "policy_id": "local-openai",
                    "kind": "openai-compatible",
                    "base_url": f"http://127.0.0.1:{server.server_port}/v1",
                    "credential_env": "PHASE6_API_KEY",
                }
            ),
            encoding="utf-8",
        )
        monkeypatch.setenv("PHASE6_API_KEY", canary)
        assert main(["exp", "run", str(root), "--adapter-policy", str(policy)]) == 0
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert observed["requests"] == 1
    assert observed["authorization"] == f"Bearer {canary}"
    assert observed["body"]["model"] == "stub-model-1"
    run_root = root / "runs/run-0001"
    retained = b"".join(path.read_bytes() for path in run_root.rglob("*") if path.is_file())
    assert canary.encode() not in retained
    assert b"PHASE6_API_KEY" not in retained
    attempt = json.loads((run_root / "attempts/0001/attempt.json").read_text(encoding="utf-8"))
    assert attempt["invocation"]["policy_kind"] == "openai-compatible"
    assert attempt["invocation"]["response_body_bytes"] == len(response)


def _invoke_http_scenario(
    tmp_path: Path,
    monkeypatch,
    *,
    status: int,
    body: bytes,
    content_length: int | None = None,
    delay: float = 0.0,
    timeout: float = 2.0,
) -> tuple[object, int]:
    requests = 0

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            nonlocal requests
            requests += 1
            self.rfile.read(int(self.headers["Content-Length"]))
            if delay:
                time.sleep(delay)
            self.send_response(status)
            self.send_header(
                "Content-Length",
                str(len(body) if content_length is None else content_length),
            )
            self.end_headers()
            if body:
                try:
                    self.wfile.write(body)
                except BrokenPipeError:
                    pass

        def log_message(self, format: str, *args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        policy_path = tmp_path / f"policy-{status}.json"
        policy_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "policy_id": "local-openai",
                    "kind": "openai-compatible",
                    "base_url": f"http://127.0.0.1:{server.server_port}/v1",
                    "credential_env": "PHASE6_API_KEY",
                }
            ),
            encoding="utf-8",
        )
        contract = DataDrivenContract.model_validate_json(
            (ROOT / "tests/fixtures/v61-phase6/contracts/openai.json").read_bytes()
        )
        monkeypatch.setenv("PHASE6_API_KEY", "scenario-secret")
        resolved = read_adapter_policy(policy_path, declaration=contract.adapter)
        candidate = tmp_path / f"candidate-{status}"
        candidate.mkdir()
        result = asyncio.run(
            invoke_declared_adapter(
                resolved,
                prompt="produce candidate",
                cwd=candidate,
                timeout_seconds=timeout,
            )
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    return result, requests


def test_h03_h04_redirect_and_non_2xx_are_one_request(tmp_path: Path, monkeypatch) -> None:
    for status in (302, 503):
        scenario = tmp_path / str(status)
        scenario.mkdir()
        result, requests = _invoke_http_scenario(
            scenario,
            monkeypatch,
            status=status,
            body=b"{}",
        )
        assert result.status == "failed"
        assert requests == 1


def test_h05_h06_deadline_and_oversize_are_closed(tmp_path: Path, monkeypatch) -> None:
    slow = tmp_path / "slow"
    slow.mkdir()
    result, requests = _invoke_http_scenario(
        slow,
        monkeypatch,
        status=200,
        body=b"{}",
        delay=0.25,
        timeout=0.05,
    )
    assert result.status == "timed-out"
    assert requests == 1

    huge = tmp_path / "huge"
    huge.mkdir()
    result, requests = _invoke_http_scenario(
        huge,
        monkeypatch,
        status=200,
        body=b"",
        content_length=MAX_HTTP_RESPONSE_BYTES + 1,
    )
    assert result.status == "failed"
    assert requests == 1


def test_h10_h11_malformed_and_tool_call_responses_fail_once(tmp_path: Path, monkeypatch) -> None:
    bodies = [
        b"not-json",
        json.dumps(
            {
                "choices": [
                    {
                        "message": {
                            "content": "ignored",
                            "tool_calls": [{"id": "forbidden"}],
                        }
                    }
                ]
            }
        ).encode(),
        json.dumps({"choices": [{"message": {"content": "{}"}}]}).encode(),
    ]
    for index, body in enumerate(bodies):
        scenario = tmp_path / f"malformed-{index}"
        scenario.mkdir()
        result, requests = _invoke_http_scenario(
            scenario,
            monkeypatch,
            status=200,
            body=body,
        )
        assert result.status == "failed"
        assert requests == 1
