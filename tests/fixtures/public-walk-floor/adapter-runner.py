"""Standard-library installed-wheel probe for the Phase-6 adapter matrix."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _bound(path: str, data: bytes, media_type: str) -> dict[str, object]:
    return {
        "path": path,
        "media_type": media_type,
        "encoding": "utf-8",
        "sha256": _sha(data),
        "size_bytes": len(data),
    }


async def _run_session(
    repository: Path,
    scratch: Path,
    *,
    experiment_id: str,
    policy_id: str,
    model_name: str | None,
    policy_document: dict[str, object],
):
    from gnd.declared_adapter import invoke_declared_adapter
    from gnd.exp.adapter_policy import read_adapter_policy
    from gnd.exp.session import case_payload_versions, run_gnd_verifier, run_session
    from gnd.exp.session_contract import read_session_contract

    root = scratch / experiment_id
    root.mkdir()
    (root / "candidate").mkdir()
    (root / "input").mkdir()
    (root / "expected").mkdir()
    skeleton = repository / "tests/fixtures/skeleton"
    model = (skeleton / "model.orm.yaml").read_bytes()
    accepted = (skeleton / "population.good.yaml").read_bytes()
    rejected = (skeleton / "population.bad.yaml").read_bytes()
    (root / "model.orm.yaml").write_bytes(model)
    (root / "input/reference.yaml").write_bytes(accepted)
    (root / "expected/population.yaml").write_bytes(accepted)
    (root / "candidate/population.yaml").write_bytes(rejected)
    contract_document = {
        "schema_version": 6,
        "experiment_id": experiment_id,
        "max_attempts": 1,
        "wall_seconds": 20.0,
        "adapter": {"policy_id": policy_id, "parameters": {"model": model_name}},
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
    contract_path = root / "session.contract.json"
    contract_path.write_text(
        json.dumps(contract_document, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    policy_path = root / "adapter.policy.json"
    policy_path.write_text(json.dumps(policy_document), encoding="utf-8")
    contract = read_session_contract(
        contract_path, experiment_root=root, experiment_id=experiment_id
    )
    policy = read_adapter_policy(policy_path, declaration=contract.adapter)

    async def verifier(case, snapshot):
        return await run_gnd_verifier(case, snapshot, experiment_root=root, timeout_seconds=20.0)

    run_root = root / "runs/run-0001"
    result = await run_session(
        contract,
        contract_sha256=_sha(contract_path.read_bytes()),
        adapter_policy=policy,
        prompt="Installed Phase 6 matrix probe.",
        candidate_root=root / "candidate",
        run_root=run_root,
        verifier=verifier,
        declared_invoker=invoke_declared_adapter,
        expected_payload_versions=case_payload_versions(contract, root),
    )
    attempt = json.loads((run_root / "attempts/0001/attempt.json").read_text())
    launch = json.loads((run_root / "launches/0001.json").read_text())
    feedback = json.loads((run_root / "attempts/0001/feedback.json").read_text())
    return result, attempt, launch, feedback, run_root


def observe(repository: Path) -> dict[str, object]:
    from gnd.exp.adapter_policy import AdapterPolicyError, read_adapter_policy
    from gnd.exp.session_contract import DataDrivenContract

    with tempfile.TemporaryDirectory(prefix="gnd-phase6-installed-") as temporary:
        scratch = Path(temporary)
        accepted = (repository / "tests/fixtures/skeleton/population.good.yaml").read_bytes()
        encoded = base64.b64encode(accepted).decode("ascii")
        agent = scratch / "agent.py"
        agent.write_text(
            "import base64,json,pathlib,sys\n"
            f"data=base64.b64decode({encoded!r})\n"
            "if len(sys.argv)>1 and sys.argv[1]=='argv': assert len(sys.argv)==3\n"
            "else: doc=json.load(sys.stdin); assert doc['schema_version']==1\n"
            "pathlib.Path('population.yaml').write_bytes(data)\n",
            encoding="utf-8",
        )

        def command_policy(identifier: str, transport: str) -> dict[str, object]:
            argv = [str(agent), transport]
            if transport == "argv":
                argv.append("{prompt}")
            return {
                "schema_version": 1,
                "policy_id": identifier,
                "kind": "command",
                "executable": sys.executable,
                "argv": argv,
                "version_argv": ["--version"],
                "prompt_transport": transport,
                "environment_allowlist": ["PATH", "HOME", "TMPDIR", "LANG", "LC_ALL"],
            }

        argv_result, argv_attempt, argv_launch, argv_feedback, _ = asyncio.run(
            _run_session(
                repository,
                scratch,
                experiment_id="EXP-P6-argv",
                policy_id="installed-argv",
                model_name=None,
                policy_document=command_policy("installed-argv", "argv"),
            )
        )
        stdin_result, _, _, _, _ = asyncio.run(
            _run_session(
                repository,
                scratch,
                experiment_id="EXP-P6-stdin",
                policy_id="installed-stdin",
                model_name=None,
                policy_document=command_policy("installed-stdin", "stdin"),
            )
        )

        requests = 0
        scenario = "success"
        canary = "PHASE6_INSTALLED_CANARY"
        bundle = json.dumps(
            {
                "schema_version": 1,
                "files": [{"path": "population.yaml", "content_base64": encoded}],
            },
            separators=(",", ":"),
        )
        response = json.dumps({"choices": [{"message": {"content": bundle}}]}).encode()

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                nonlocal requests, scenario
                requests += 1
                self.rfile.read(int(self.headers["Content-Length"]))
                assert self.headers["Authorization"] == f"Bearer {canary}"
                if scenario == "redirect":
                    self.send_response(302)
                    self.send_header("Location", "/other")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                if scenario == "cap":
                    self.send_response(200)
                    self.send_header("Content-Length", str(1024 * 1024 + 1))
                    self.end_headers()
                    return
                self.send_response(200)
                self.send_header("Content-Length", str(len(response)))
                self.end_headers()
                self.wfile.write(response)

            def log_message(self, *_args):
                return

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        os.environ["PHASE6_API_KEY"] = canary
        try:
            http_result, _, _, _, http_run = asyncio.run(
                _run_session(
                    repository,
                    scratch,
                    experiment_id="EXP-P6-http",
                    policy_id="installed-http",
                    model_name="stub-model-1",
                    policy_document={
                        "schema_version": 1,
                        "policy_id": "installed-http",
                        "kind": "openai-compatible",
                        "base_url": f"http://127.0.0.1:{server.server_port}/v1",
                        "credential_env": "PHASE6_API_KEY",
                    },
                )
            )
            scenario = "redirect"
            redirect_result, _, _, _, _ = asyncio.run(
                _run_session(
                    repository,
                    scratch,
                    experiment_id="EXP-P6-http-redirect",
                    policy_id="installed-http-redirect",
                    model_name="stub-model-1",
                    policy_document={
                        "schema_version": 1,
                        "policy_id": "installed-http-redirect",
                        "kind": "openai-compatible",
                        "base_url": f"http://127.0.0.1:{server.server_port}/v1",
                        "credential_env": "PHASE6_API_KEY",
                    },
                )
            )
            scenario = "cap"
            cap_result, _, _, _, _ = asyncio.run(
                _run_session(
                    repository,
                    scratch,
                    experiment_id="EXP-P6-http-cap",
                    policy_id="installed-http-cap",
                    model_name="stub-model-1",
                    policy_document={
                        "schema_version": 1,
                        "policy_id": "installed-http-cap",
                        "kind": "openai-compatible",
                        "base_url": f"http://127.0.0.1:{server.server_port}/v1",
                        "credential_env": "PHASE6_API_KEY",
                    },
                )
            )
        finally:
            os.environ.pop("PHASE6_API_KEY", None)
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
        retained = b"".join(item.read_bytes() for item in http_run.rglob("*") if item.is_file())

        fixture_contract = DataDrivenContract.model_validate_json(
            (repository / "tests/fixtures/v61-phase6/contracts/command.json").read_bytes()
        )
        dirty = scratch / "dirty-policy.json"
        dirty.write_text(json.dumps(command_policy("wrong-id", "argv")), encoding="utf-8")
        refused = False
        try:
            read_adapter_policy(dirty, declaration=fixture_contract.adapter)
        except AdapterPolicyError:
            refused = True

        phase5_path = repository / "tests/fixtures/v61-phase5/installed/driver.py"
        spec = importlib.util.spec_from_file_location("phase5_installed", phase5_path)
        assert spec is not None and spec.loader is not None
        phase5 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(phase5)
        legacy = phase5.observe(repository)

    return {
        "contract-v6": 6,
        "launch-v2": argv_launch["schema_version"],
        "attempt-v8": argv_attempt["schema_version"],
        "feedback-v4": argv_feedback["schema_version"],
        "result-v2": argv_result.schema_version,
        "command-argv-accepted": argv_result.disposition.value == "accepted",
        "command-stdin-accepted": stdin_result.disposition.value == "accepted",
        "http-accepted": http_result.disposition.value == "accepted",
        "http-redirect-refused": redirect_result.disposition.value != "accepted",
        "http-cap-refused": cap_result.disposition.value != "accepted",
        "http-request-count": requests,
        "credential-absent": canary.encode() not in retained and b"PHASE6_API_KEY" not in retained,
        "policy-refusal": refused,
        "legacy-replay": legacy["attempt-v7"] and legacy["result-v5"],
        "evidence-not-current": {
            "assurance_level": "none",
            "scope_id": "applicability:refusal:n-a:evidence-not-current",
        },
    }


def main() -> int:
    print(json.dumps(observe(Path(sys.argv[1]).resolve()), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
