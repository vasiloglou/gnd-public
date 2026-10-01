"""Public ``gnd exp run`` coverage for the one-attempt session bridge.

The agent executable is a sanitized local fixture and every verifier is GND's
real machine channel.  No provider login or network access is involved.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
import shlex
import shutil
import stat
import time
from pathlib import Path
from typing import Any

import pytest
from support.digests import sha256_bytes as _sha256

from gnd import cli
from gnd.agent_cli import (
    AgentAdapterId,
    InvocationResult,
    InvocationStatus,
    build_agent_argv,
    invoke_agent,
)
from gnd.cli import main
from gnd.exp.session import case_payload_versions, run_session
from gnd.exp.session_contract import read_session_contract

REPO_ROOT = Path(__file__).resolve().parent.parent
SESSION_CORPUS = REPO_ROOT / "tests" / "fixtures" / "phase4_reference" / "session.json"
SKELETON = REPO_ROOT / "tests" / "fixtures" / "skeleton"
CHECKER = REPO_ROOT / "tests" / "fixtures" / "checker"


def _canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def _bound(path: str, data: bytes, media_type: str) -> dict[str, Any]:
    return {
        "path": path,
        "media_type": media_type,
        "encoding": "utf-8",
        "sha256": _sha256(data),
        "size_bytes": len(data),
    }


def _write_fake_agent(bin_dir: Path, adapter: str, *, exit_code: int = 0) -> None:
    executable = bin_dir / adapter
    executable.write_text(
        f"""#!/usr/bin/env python3
import sys

if "--version" in sys.argv:
    print("sanitized-session-agent 1.0")
    raise SystemExit(0)
print("agent stdout")
print("agent stderr", file=sys.stderr)
raise SystemExit({exit_code})
""",
        encoding="utf-8",
    )
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)


def _session_case(
    case_id: str = "session-exact-all-required-acceptance",
) -> dict[str, Any]:
    cases = json.loads(SESSION_CORPUS.read_text(encoding="utf-8"))
    exact = next(case for case in cases if case["case_id"] == case_id)
    blob = exact["input_blobs"][0]
    raw = blob["bytes"].encode(blob["encoding"])
    assert len(raw) == blob["size_bytes"]
    assert _sha256(raw) == blob["sha256"]
    return exact


def _contracted_expectation(
    case_id: str = "session-declared-output-differs-from-expectation",
) -> bytes:
    """The committed expectation bytes, recomputed from the corpus blob.

    A model-conforming population that no seeded candidate already holds, so
    an agent has to actually produce it.
    """

    blob = _session_case(case_id)["expected_output_blobs"][0]
    raw = blob["bytes"].encode(blob["encoding"])
    assert len(raw) == blob["size_bytes"]
    assert _sha256(raw) == blob["sha256"]
    return raw


def _accepted_population() -> bytes:
    return (SKELETON / "population.good.yaml").read_bytes()


def _make_experiment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    adapter: str = "codex",
    model_fixture: Path | None = None,
    subject_fixture: Path | None = None,
    subject_bytes: bytes | None = None,
    agent_exit: int = 0,
    max_attempts: int = 1,
    wall_seconds: float = 5.0,
    case_id: str = "session-exact-all-required-acceptance",
    expected_bytes: bytes | None = None,
    expected_candidate_path: str = "population.yaml",
) -> Path:
    experiment_id = "EXP-401-session"
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
                "Q1=Did the bounded session establish the contract?",
            ]
        )
        == 0
    )
    root = tmp_path / experiment_id
    candidate = root / "candidate"
    candidate.mkdir()

    model_source = model_fixture or SKELETON / "model.orm.yaml"
    subject_source = subject_fixture or SKELETON / "population.good.yaml"
    model_bytes = model_source.read_bytes()
    population_bytes = subject_bytes if subject_bytes is not None else subject_source.read_bytes()
    (root / "model.orm.yaml").write_bytes(model_bytes)
    (candidate / "population.yaml").write_bytes(population_bytes)

    exact = _session_case(case_id)
    input_blob = exact["input_blobs"][0]
    input_bytes = input_blob["bytes"].encode(input_blob["encoding"])
    input_path = root / input_blob["path"]
    input_path.parent.mkdir(parents=True)
    input_path.write_bytes(input_bytes)
    # The seeded candidate and the declared expectation are independent inputs.
    # The default expectation is deliberately NOT the seeded candidate: making
    # them equal by construction is what let R-01 stand, because agreement was
    # then structural rather than earned.  A test wanting the accepted path
    # passes the expectation explicitly or uses an agent that produces it.
    contracted_bytes = _contracted_expectation() if expected_bytes is None else expected_bytes
    expected_path = root / "expected" / "population.yaml"
    expected_path.parent.mkdir()
    expected_path.write_bytes(contracted_bytes)

    contract = {
        "schema_version": 1,
        "experiment_id": experiment_id,
        "max_attempts": max_attempts,
        "wall_seconds": wall_seconds,
        "cases": [
            {
                "case_id": exact["case_id"],
                "role": "required",
                "inputs": [
                    {
                        key: input_blob[key]
                        for key in (
                            "path",
                            "media_type",
                            "encoding",
                            "sha256",
                            "size_bytes",
                        )
                    }
                ],
                "expected_outputs": [
                    {
                        **_bound(
                            "expected/population.yaml",
                            contracted_bytes,
                            "application/yaml",
                        ),
                        "output_id": "population",
                        "candidate_path": expected_candidate_path,
                        "comparison": "exact-bytes",
                    }
                ],
                "verify": {
                    "command": "check",
                    "model": _bound("model.orm.yaml", model_bytes, "application/yaml"),
                    "subject": "population.yaml",
                },
            }
        ],
    }
    (root / "session.contract.json").write_text(
        json.dumps(contract, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _write_fake_agent(bin_dir, adapter, exit_code=agent_exit)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")
    return root


def _write_exact_feedback_retry_agent(
    executable: Path,
    *,
    accepted_population: bytes,
) -> None:
    encoded_population = base64.b64encode(accepted_population).decode("ascii")
    executable.write_text(
        f"""#!/usr/bin/env python3
import base64
import hashlib
import json
import pathlib
import re
import sys

if "--version" in sys.argv:
    print("exact-feedback-agent 1.0")
    raise SystemExit(0)

counter = pathlib.Path(".attempt-count")
attempt = int(counter.read_text()) + 1 if counter.exists() else 1
counter.write_text(str(attempt))
feedback = sys.stdin.buffer.read()
if attempt == 1:
    if feedback:
        raise SystemExit(31)
    raise SystemExit(0)

prompt = sys.argv[-1]
match = re.search(r"Current attempt feedback SHA-256: ([0-9a-f]{{64}})", prompt)
if match is None or hashlib.sha256(feedback).hexdigest() != match.group(1):
    raise SystemExit(32)
published = list(pathlib.Path("..").glob("runs/*/attempts/0001/feedback.json"))
if len(published) != 1 or feedback != published[0].read_bytes():
    raise SystemExit(36)
if "source_attempt_index" in prompt or "normalized_verifier_signature" in prompt:
    raise SystemExit(35)
document = json.loads(feedback)
if document["source_attempt_index"] != 1 or document["disposition"] != "retry":
    raise SystemExit(33)
for forbidden in ("prose", "timing", "absolute_path", "stderr", "best_attempt",
                  "cumulative_attempts", "prior_attempt"):
    if forbidden in document:
        raise SystemExit(34)
pathlib.Path("received-feedback.bin").write_bytes(feedback)
pathlib.Path("population.yaml").write_bytes(base64.b64decode({encoded_population!r}))
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)


def _write_producing_agent(
    executable: Path,
    *,
    produced: bytes,
    candidate_path: str,
) -> None:
    """A sanitized local agent that writes exactly `produced` and exits zero."""

    encoded = base64.b64encode(produced).decode("ascii")
    executable.write_text(
        f"""#!/usr/bin/env python3
import base64
import pathlib
import sys

if "--version" in sys.argv:
    print("producing-agent 1.0")
    raise SystemExit(0)

sys.stdin.buffer.read()
print("agent stdout")
print("agent stderr", file=sys.stderr)
target = pathlib.Path({candidate_path!r})
target.parent.mkdir(parents=True, exist_ok=True)
target.write_bytes(base64.b64decode({encoded!r}))
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)


def _write_corpus_agent(
    executable: Path,
    *,
    scenario: str,
    good_population: bytes,
    bad_population: bytes,
    marker: Path,
) -> None:
    good = base64.b64encode(good_population).decode("ascii")
    bad = base64.b64encode(bad_population).decode("ascii")
    if scenario == "wall":
        # Test main-process descendant cleanup without spending this half-second
        # deadline importing a cold Python interpreter during version preflight.
        # The separate adapter deadline test owns version-probe exhaustion.
        executable.write_text(
            "#!/bin/sh\n"
            'if [ "$1" = "--version" ]; then echo "corpus-agent 1.0"; exit 0; fi\n'
            "(\n"
            f"  : > {shlex.quote(str(marker.with_suffix('.started')))}\n"
            "  /bin/sleep 0.7\n"
            f"  printf survived > {shlex.quote(str(marker))}\n"
            ") &\n"
            "wait\n",
            encoding="utf-8",
        )
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
        return
    executable.write_text(
        f"""#!/usr/bin/env python3
import base64
import os
import pathlib
import subprocess
import sys
import time

if "--version" in sys.argv:
    print("corpus-agent 1.0")
    raise SystemExit(0)

sys.stdin.buffer.read()
scenario = {scenario!r}
counter = pathlib.Path(__file__).with_suffix(".count")
attempt = int(counter.read_text()) + 1 if counter.exists() else 1
counter.write_text(str(attempt))
good = base64.b64decode({good!r})
bad = base64.b64decode({bad!r})
if scenario == "accepted":
    pathlib.Path("population.yaml").write_bytes(good)
elif scenario == "same-score":
    pathlib.Path("population.yaml").write_bytes(bad + f"# variant {{attempt}}\\n".encode())
elif scenario == "oscillation":
    variant = "A" if attempt in (1, 3) else "B"
    pathlib.Path("population.yaml").write_bytes(bad + f"# variant {{variant}}\\n".encode())
elif scenario == "flood":
    for descriptor, value in ((1, b"o"), (2, b"e")):
        payload = value * (2 * 1024 * 1024)
        view = memoryview(payload)
        while view:
            view = view[os.write(descriptor, view):]
    raise SystemExit(23)
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)


def _assert_exact_run_evidence(
    root: Path,
    rendered: dict[str, Any],
    *,
    corpus_row: dict[str, Any] | None = None,
) -> None:
    """Resolve and recompute every digest edge actually indexed by a run."""

    run = root / "runs" / rendered["run_id"]
    attempts = sorted((run / "attempts").iterdir())
    launches = sorted((run / "launches").iterdir())
    assert len(attempts) == rendered["attempt_count"]
    assert [path.name for path in launches] == [
        f"{index:04d}.json" for index in range(1, rendered["attempt_count"] + 1)
    ]
    contract_bytes = (root / "session.contract.json").read_bytes()
    contract = json.loads(contract_bytes)
    for bound in contract["cases"][0]["inputs"]:
        data = (root / bound["path"]).read_bytes()
        assert len(data) == bound["size_bytes"]
        assert _sha256(data) == bound["sha256"]

    if corpus_row is not None:
        evidence = corpus_row["expected_evidence"]
        assert evidence["session_contract_path"] == "session.contract.json"
        assert len(evidence["attempts"]) == rendered["attempt_count"]
        expected_run_files = {
            evidence["result_path"],
            *(
                [evidence["best_path"]]
                if evidence["best_path"] is not None
                else []
            ),
        }
        for expected_attempt in evidence["attempts"]:
            expected_run_files.update(
                {
                    expected_attempt["launch_intent_path"],
                    expected_attempt["attempt_manifest_path"],
                    expected_attempt["candidate_inventory_path"],
                    expected_attempt["agent_stdout_path"],
                    expected_attempt["agent_stderr_path"],
                    expected_attempt["feedback_path"],
                    *expected_attempt["candidate_snapshot_paths"],
                    *expected_attempt["verifier_payload_paths"],
                }
            )
        actual_run_files = {
            path.relative_to(run).as_posix() for path in run.rglob("*") if path.is_file()
        }
        assert actual_run_files == expected_run_files
        assert (rendered["best_attempt"] is None) is (evidence["best_path"] is None)

    attempt_digests: dict[int, str] = {}
    candidate_digests: dict[int, str] = {}
    for expected_index, attempt in enumerate(attempts, start=1):
        assert attempt.name == f"{expected_index:04d}"
        manifest_path = attempt / "attempt.json"
        manifest_bytes = manifest_path.read_bytes()
        manifest = json.loads(manifest_bytes)
        attempt_digests[expected_index] = _sha256(manifest_bytes)
        assert manifest["attempt_index"] == expected_index
        assert manifest["evaluation"]["contract_sha256"] == _sha256(contract_bytes)
        launch_bytes = (run / manifest["launch_intent"]["path"]).read_bytes()
        assert len(launch_bytes) == manifest["launch_intent"]["size_bytes"]
        assert _sha256(launch_bytes) == manifest["launch_intent"]["sha256"]
        launch = json.loads(launch_bytes)
        assert launch["attempt_index"] == expected_index
        assert launch["contract_sha256"] == _sha256(contract_bytes)

        inventory_bytes = (attempt / "candidate.inventory.json").read_bytes()
        assert _sha256(inventory_bytes) == manifest["candidate_inventory_sha256"]
        inventory = json.loads(inventory_bytes)
        assert inventory["file_count"] == len(inventory["files"])
        assert inventory["total_bytes"] == sum(row["size_bytes"] for row in inventory["files"])
        for row in inventory["files"]:
            data = (attempt / "candidate" / row["path"]).read_bytes()
            assert len(data) == row["size_bytes"]
            assert _sha256(data) == row["sha256"]
        candidate_digests[expected_index] = inventory["tree_sha256"]
        assert inventory["tree_sha256"] == manifest["evaluation"]["candidate_sha256"]

        for leaf_name, field in (
            ("agent.stdout", "agent_stdout"),
            ("agent.stderr", "agent_stderr"),
        ):
            data = (attempt / leaf_name).read_bytes()
            assert len(data) == manifest[field]["size_bytes"]
            assert _sha256(data) == manifest[field]["sha256"]
        feedback = (attempt / "feedback.json").read_bytes()
        assert len(feedback) == manifest["feedback"]["size_bytes"]
        assert _sha256(feedback) == manifest["feedback"]["sha256"]
        expected_files = {
            "attempt.json",
            "candidate.inventory.json",
            "feedback.json",
            "agent.stdout",
            "agent.stderr",
            *(f"candidate/{row['path']}" for row in inventory["files"]),
        }
        for row in manifest["raw_verifier_payloads"]:
            data = (run / row["path"]).read_bytes()
            assert len(data) == row["size_bytes"]
            assert _sha256(data) == row["sha256"]
            expected_files.add(f"verifier/{row['case_id']}.json")
        observed_files = {
            path.relative_to(attempt).as_posix() for path in attempt.rglob("*") if path.is_file()
        }
        assert observed_files == expected_files
        expected_digest_index = {
            "launch_intent_sha256": _sha256(launch_bytes),
            "candidate_inventory_sha256": _sha256(inventory_bytes),
            "candidate_tree_sha256": inventory["tree_sha256"],
            "agent_stdout_sha256": manifest["agent_stdout"]["sha256"],
            "agent_stderr_sha256": manifest["agent_stderr"]["sha256"],
            "evaluation_sha256": _sha256(_canonical_json_bytes(manifest["evaluation"])),
            "feedback_sha256": _sha256(feedback),
            **{
                f"verifier.{row['case_id']}.sha256": row["sha256"]
                for row in manifest["raw_verifier_payloads"]
            },
        }
        assert manifest["evidence_digests"] == expected_digest_index

    result_bytes = (run / "result.json").read_bytes()
    assert json.loads(result_bytes) == rendered
    terminal = rendered["attempt_count"]
    assert (
        rendered["referenced_evidence_digests"]["attempt_manifest_sha256"]
        == attempt_digests[terminal]
    )
    assert set(rendered["referenced_evidence_digests"]) == {"attempt_manifest_sha256"}
    best_path = run / "best.json"
    if rendered["best_attempt"] is None:
        assert not best_path.exists()
    else:
        best = json.loads(best_path.read_bytes())
        best_index = rendered["best_attempt"]
        assert best["attempt"] == best_index
        assert best["attempt_manifest_sha256"] == attempt_digests[best_index]
        assert best["candidate_sha256"] == candidate_digests[best_index]
        assert rendered["best_attempt_manifest_sha256"] == attempt_digests[best_index]
        assert rendered["best_candidate_sha256"] == candidate_digests[best_index]


def _successful_invocation(
    *,
    prompt: str,
    feedback_sha256: str | None = None,
) -> InvocationResult:
    started = 10.0
    effective_prompt = prompt
    if feedback_sha256 is not None:
        effective_prompt = (
            f"{prompt}\n\nCurrent attempt feedback SHA-256: {feedback_sha256}\n"
            "Canonical current-attempt feedback is supplied byte-for-byte on stdin."
        )
    prompt_token = (
        f"<prompt:sha256={hashlib.sha256(effective_prompt.encode('utf-8')).hexdigest()}>"
    )
    return InvocationResult(
        adapter=AgentAdapterId.codex,
        status=InvocationStatus.succeeded,
        executable="codex",
        version="test-agent 1.0",
        argv=(*build_agent_argv(AgentAdapterId.codex, effective_prompt)[:-1], prompt_token),
        cwd="<candidate-root>",
        termination="exited",
        exit_code=0,
        started_monotonic=started,
        ended_monotonic=started + 0.01,
        stdout_observed_bytes=0,
        stdout_retained_bytes=0,
        stdout_truncated=False,
        stderr_observed_bytes=0,
        stderr_retained_bytes=0,
        stderr_truncated=False,
        environment=(),
        prompt_sha256=hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        stdout=b"",
        stderr=b"",
        feedback_sha256=feedback_sha256,
    )


def _run(root: Path, adapter: str, capsys: pytest.CaptureFixture[str]) -> tuple[int, dict]:
    exit_code = main(["exp", "run", str(root), "--adapter", adapter])
    output = capsys.readouterr().out.splitlines()
    return exit_code, json.loads(output[-1])


@pytest.mark.parametrize("adapter", ["claude", "codex"])
def test_public_single_attempt_accepts_and_recomputes_every_persisted_digest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    adapter: str,
) -> None:
    # The seeded candidate already holds what this contract declares, stated
    # explicitly rather than assumed by the fixture.
    root = _make_experiment(
        tmp_path,
        monkeypatch,
        adapter=adapter,
        expected_bytes=_accepted_population(),
    )

    exit_code, rendered = _run(root, adapter, capsys)

    assert exit_code == 0
    assert rendered["disposition"] == "accepted"
    run = root / "runs" / rendered["run_id"]
    attempt = run / "attempts" / "0001"
    attempt_path = attempt / "attempt.json"
    best_path = run / "best.json"
    result_path = run / "result.json"
    for path in (attempt_path, best_path, result_path):
        assert path.is_file()

    attempt_doc = json.loads(attempt_path.read_text(encoding="utf-8"))
    inventory_path = attempt / "candidate.inventory.json"
    inventory_bytes = inventory_path.read_bytes()
    assert _sha256(inventory_bytes) == attempt_doc["candidate_inventory_sha256"]

    snapshot = attempt / "candidate"
    inventory = json.loads(inventory_bytes)
    assert inventory["file_count"] == len(inventory["files"]) == 1
    candidate_row = inventory["files"][0]
    candidate_bytes = (snapshot / candidate_row["path"]).read_bytes()
    assert len(candidate_bytes) == candidate_row["size_bytes"]
    assert _sha256(candidate_bytes) == candidate_row["sha256"]
    assert inventory["tree_sha256"] == attempt_doc["evaluation"]["candidate_sha256"]

    stdout = (attempt / "agent.stdout").read_bytes()
    stderr = (attempt / "agent.stderr").read_bytes()
    assert stdout == b"agent stdout\n"
    assert stderr == b"agent stderr\n"
    assert _sha256(stdout) == attempt_doc["agent_stdout"]["sha256"]
    assert _sha256(stderr) == attempt_doc["agent_stderr"]["sha256"]
    assert attempt_doc["invocation"]["adapter"] == adapter
    assert "stdout" not in attempt_doc["invocation"]
    assert "stderr" not in attempt_doc["invocation"]

    verifier_row = attempt_doc["raw_verifier_payloads"][0]
    verifier_path = run / verifier_row["path"]
    verifier_bytes = verifier_path.read_bytes()
    verifier = json.loads(verifier_bytes)
    assert verifier["command"] == "check"
    assert verifier["model"] == "model.orm.yaml"
    assert verifier["population"] == "population.yaml"
    assert verifier["exit_code"] == 0
    assert verifier["acceptance_ready"] is True
    assert _sha256(verifier_bytes) == verifier_row["sha256"]

    contract_bytes = (root / "session.contract.json").read_bytes()
    contract = json.loads(contract_bytes)
    input_bound = contract["cases"][0]["inputs"][0]
    input_bytes = (root / input_bound["path"]).read_bytes()
    assert _sha256(input_bytes) == input_bound["sha256"]
    assert _sha256(contract_bytes) == attempt_doc["evaluation"]["contract_sha256"]

    attempt_bytes = attempt_path.read_bytes()
    best = json.loads(best_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert best["attempt_manifest_sha256"] == _sha256(attempt_bytes)
    assert best["candidate_sha256"] == inventory["tree_sha256"]
    assert result == rendered
    assert result["best_attempt_manifest_sha256"] == _sha256(attempt_bytes)
    assert result["referenced_evidence_digests"]["attempt_manifest_sha256"] == _sha256(
        attempt_bytes
    )


def test_second_attempt_receives_only_the_exact_current_feedback_bytes_and_digest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    accepted_population = _accepted_population()
    root = _make_experiment(
        tmp_path,
        monkeypatch,
        subject_fixture=SKELETON / "population.bad.yaml",
        max_attempts=2,
        expected_bytes=accepted_population,
    )
    _write_exact_feedback_retry_agent(
        tmp_path / "bin" / "codex",
        accepted_population=accepted_population,
    )

    exit_code, rendered = _run(root, "codex", capsys)

    assert exit_code == 0
    assert rendered["disposition"] == "accepted"
    assert rendered["attempt_count"] == 2
    run = root / "runs" / rendered["run_id"]
    feedback = (run / "attempts" / "0001" / "feedback.json").read_bytes()
    received = (run / "attempts" / "0002" / "candidate" / "received-feedback.bin").read_bytes()
    assert received == feedback
    feedback_sha256 = _sha256(feedback)
    first = json.loads((run / "attempts" / "0001" / "attempt.json").read_bytes())
    second = json.loads((run / "attempts" / "0002" / "attempt.json").read_bytes())
    assert first["feedback"]["sha256"] == feedback_sha256
    assert second["invocation"]["feedback_sha256"] == feedback_sha256

    document = json.loads(feedback)
    mutations: list[dict[str, Any]] = []
    for field in document:
        mutated = json.loads(feedback)
        value = mutated[field]
        if isinstance(value, bool):
            mutated[field] = not value
        elif isinstance(value, int):
            mutated[field] = value + 1
        elif isinstance(value, str):
            mutated[field] = value + "-stale"
        elif isinstance(value, list):
            mutated[field] = [*value, "stale"]
        elif value is None:
            mutated[field] = 0
        else:  # pragma: no cover - closed feedback has no other JSON kind
            raise AssertionError(type(value))
        mutations.append(mutated)
    for forbidden in (
        "prose",
        "timing",
        "absolute_path",
        "stderr",
        "best_attempt",
        "cumulative_attempts",
        "prior_attempt",
    ):
        mutated = json.loads(feedback)
        mutated[forbidden] = "forbidden"
        mutations.append(mutated)
    nested = json.loads(feedback)
    nested["required"][0]["counts"]["pass"] += 1
    mutations.append(nested)

    for mutated in mutations:
        mutated_bytes = (json.dumps(mutated, sort_keys=True, separators=(",", ":")) + "\n").encode()
        refused = asyncio.run(
            invoke_agent(
                AgentAdapterId.codex,
                prompt="repair the candidate",
                cwd=root / "candidate",
                timeout_seconds=2.0,
                feedback_bytes=mutated_bytes,
                feedback_sha256=_sha256(mutated_bytes),
            )
        )
        assert refused.status is InvocationStatus.failed


def test_cancellation_after_staging_discards_private_bytes_and_publishes_no_attempt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _make_experiment(
        tmp_path,
        monkeypatch,
        subject_fixture=SKELETON / "population.bad.yaml",
        max_attempts=2,
    )
    contract_path = root / "session.contract.json"
    contract_bytes = contract_path.read_bytes()
    contract = read_session_contract(
        contract_path,
        experiment_root=root,
        experiment_id="EXP-401-session",
    )
    run = root / "runs" / "run-cancelled"
    verifier_entered = asyncio.Event()

    async def invoker(*args: Any, **kwargs: Any) -> InvocationResult:
        return _successful_invocation(
            prompt=kwargs["prompt"],
            feedback_sha256=kwargs["feedback_sha256"],
        )

    async def verifier(*args: Any, **kwargs: Any) -> tuple[int, bytes]:
        verifier_entered.set()
        await asyncio.Future()
        raise AssertionError("unreachable")

    async def scenario() -> None:
        task = asyncio.create_task(
            run_session(
                contract,
                contract_sha256=_sha256(contract_bytes),
                adapter_id=AgentAdapterId.codex,
                prompt="repair the candidate",
                candidate_root=root / "candidate",
                run_root=run,
                verifier=verifier,
                invoker=invoker,
            )
        )
        await asyncio.wait_for(verifier_entered.wait(), timeout=1.0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(scenario())

    assert list((run / ".staging").iterdir()) == []
    assert list((run / "attempts").iterdir()) == []
    assert not (run / "result.json").exists()
    assert (run / "launches" / "0001.json").is_file()
    with pytest.raises(ValueError, match="uncommitted launch intent"):
        asyncio.run(
            run_session(
                contract,
                contract_sha256=_sha256(contract_bytes),
                adapter_id=AgentAdapterId.codex,
                prompt="repair the candidate",
                candidate_root=root / "candidate",
                run_root=run,
                verifier=verifier,
                invoker=invoker,
            )
        )


def test_malformed_verifier_return_is_closed_without_stranded_staging(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _make_experiment(
        tmp_path,
        monkeypatch,
        subject_fixture=SKELETON / "population.bad.yaml",
    )
    contract_path = root / "session.contract.json"
    contract_bytes = contract_path.read_bytes()
    contract = read_session_contract(
        contract_path,
        experiment_root=root,
        experiment_id="EXP-401-session",
    )
    run = root / "runs" / "run-malformed-verifier"

    async def invoker(*args: Any, **kwargs: Any) -> InvocationResult:
        return _successful_invocation(
            prompt=kwargs["prompt"],
            feedback_sha256=kwargs["feedback_sha256"],
        )

    async def malformed(*args: Any, **kwargs: Any):
        return 0, "not-bytes"

    result = asyncio.run(
        run_session(
            contract,
            contract_sha256=_sha256(contract_bytes),
            adapter_id=AgentAdapterId.codex,
            prompt="repair the candidate",
            candidate_root=root / "candidate",
            run_root=run,
            verifier=malformed,
            invoker=invoker,
        )
    )

    assert result.disposition == "verifier-failure"
    assert list((run / ".staging").iterdir()) == []


@pytest.mark.parametrize(
    ("update", "message"),
    [
        ({"process_group_cleaned": False}, "process-group cleanup"),
        ({"adapter": AgentAdapterId.claude}, "different agent adapter"),
        ({"prompt_sha256": None}, "lacks agent instruction identity"),
        ({"prompt_sha256": "0" * 64}, "different agent instructions"),
        ({"feedback_sha256": "0" * 64}, "stale retry feedback"),
        (
            {"argv": ("codex", "exec", f"<prompt:sha256={'0' * 64}>")},
            "stale fixed adapter arguments",
        ),
        (
            {"termination": "killed"},
            "successful invocation must exit normally",
        ),
        (
            {"exit_code": 9},
            "successful invocation must exit normally",
        ),
        (
            {"status": InvocationStatus.failed},
            "failed invocation cannot claim exit zero",
        ),
        (
            {"status": InvocationStatus.timed_out},
            "timed-out invocation requires termination provenance",
        ),
        (
                {
                    "status": InvocationStatus.failed,
                    "spawned": False,
                    "termination": "not-started",
                    "spawn_error": "InjectedNotStarted",
                    "exit_code": None,
                "stdout": b"impossible main output",
                "stdout_observed_bytes": 22,
                "stdout_retained_bytes": 22,
            },
            "unstarted invocation cannot contain main-process streams",
        ),
    ],
)
def test_custom_invocation_proof_mismatch_refuses_before_staging(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    update: dict[str, Any],
    message: str,
) -> None:
    root = _make_experiment(tmp_path, monkeypatch)
    contract_path = root / "session.contract.json"
    contract_bytes = contract_path.read_bytes()
    contract = read_session_contract(
        contract_path,
        experiment_root=root,
        experiment_id="EXP-401-session",
    )
    run = root / "runs" / "run-unproven-invocation"

    async def invoker(*args: Any, **kwargs: Any) -> InvocationResult:
        return _successful_invocation(
            prompt=kwargs["prompt"],
            feedback_sha256=kwargs["feedback_sha256"],
        ).model_copy(update=update)

    async def verifier(*args: Any, **kwargs: Any) -> tuple[int, bytes]:
        raise AssertionError("unproven invocation reached the verifier")

    with pytest.raises(ValueError, match=message):
        asyncio.run(
            run_session(
                contract,
                contract_sha256=_sha256(contract_bytes),
                adapter_id=AgentAdapterId.codex,
                prompt="repair the candidate",
                candidate_root=root / "candidate",
                run_root=run,
                verifier=verifier,
                invoker=invoker,
            )
        )

    assert list((run / ".staging").iterdir()) == []
    assert list((run / "attempts").iterdir()) == []


@pytest.mark.skipif(os.name != "posix", reason="symlink containment is POSIX-specific")
def test_symlinked_run_parent_cannot_place_evidence_inside_mutable_candidate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _make_experiment(tmp_path, monkeypatch)
    contract_path = root / "session.contract.json"
    contract_bytes = contract_path.read_bytes()
    contract = read_session_contract(
        contract_path,
        experiment_root=root,
        experiment_id="EXP-401-session",
    )
    alias = tmp_path / "candidate-alias"
    alias.symlink_to(root / "candidate", target_is_directory=True)
    escaped_run = alias / "evidence-run"

    async def verifier(*args: Any, **kwargs: Any) -> tuple[int, bytes]:
        raise AssertionError("contained evidence path reached the verifier")

    with pytest.raises(ValueError, match="outside the mutable candidate"):
        asyncio.run(
            run_session(
                contract,
                contract_sha256=_sha256(contract_bytes),
                adapter_id=AgentAdapterId.codex,
                prompt="repair the candidate",
                candidate_root=root / "candidate",
                run_root=escaped_run,
                verifier=verifier,
            )
        )

    assert not (root / "candidate" / "evidence-run").exists()


def test_verifier_owned_timeout_replays_as_verifier_failure_without_an_extra_launch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import gnd.exp.session as session_module

    root = _make_experiment(
        tmp_path,
        monkeypatch,
        subject_fixture=SKELETON / "population.bad.yaml",
    )
    contract_path = root / "session.contract.json"
    contract_bytes = contract_path.read_bytes()
    contract = read_session_contract(
        contract_path,
        experiment_root=root,
        experiment_id="EXP-401-session",
    )
    run = root / "runs" / "run-verifier-timeout"
    launches = 0

    async def invoker(*args: Any, **kwargs: Any) -> InvocationResult:
        nonlocal launches
        launches += 1
        return _successful_invocation(
            prompt=kwargs["prompt"],
            feedback_sha256=kwargs["feedback_sha256"],
        )

    async def verifier_timeout(*args: Any, **kwargs: Any):
        raise TimeoutError("verifier-owned timeout")

    original_publish_result = session_module.SessionStore.publish_result

    def crash_before_result(self, result):
        raise RuntimeError("crash before timeout result")

    monkeypatch.setattr(
        session_module.SessionStore,
        "publish_result",
        crash_before_result,
    )
    with pytest.raises(RuntimeError, match="crash before timeout result"):
        asyncio.run(
            run_session(
                contract,
                contract_sha256=_sha256(contract_bytes),
                adapter_id=AgentAdapterId.codex,
                prompt="repair the candidate",
                candidate_root=root / "candidate",
                run_root=run,
                verifier=verifier_timeout,
                invoker=invoker,
            )
        )
    monkeypatch.setattr(
        session_module.SessionStore,
        "publish_result",
        original_publish_result,
    )

    result = asyncio.run(
        run_session(
            contract,
            contract_sha256=_sha256(contract_bytes),
            adapter_id=AgentAdapterId.codex,
            prompt="repair the candidate",
            candidate_root=root / "candidate",
            run_root=run,
            verifier=verifier_timeout,
            invoker=invoker,
        )
    )

    assert result.disposition == "verifier-failure"
    assert launches == 1
    assert list((run / ".staging").iterdir()) == []


def test_resume_binds_contract_policy_adapter_and_prompt_before_launch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    import gnd.exp.session as session_module

    root = _make_experiment(
        tmp_path,
        monkeypatch,
        subject_fixture=SKELETON / "population.bad.yaml",
        max_attempts=2,
    )
    contract_path = root / "session.contract.json"
    contract_bytes = contract_path.read_bytes()
    contract_sha256 = _sha256(contract_bytes)
    contract = read_session_contract(
        contract_path,
        experiment_root=root,
        experiment_id="EXP-401-session",
    )
    run = root / "runs" / "run-bound-resume"

    # Capture the real current machine wire once in-process. This test owns
    # resume identity, not subprocess startup performance, so replay the exact
    # bytes rather than letting cold package authentication spend its old
    # one-second verifier fixture bound.
    bound_versions = case_payload_versions(contract, root)
    candidate = root / "candidate"
    model_copy = candidate / "model.orm.yaml"
    model_copy.write_bytes((root / "model.orm.yaml").read_bytes())
    previous = Path.cwd()
    capsys.readouterr()
    monkeypatch.chdir(candidate)
    verifier_exit = main(["check", "model.orm.yaml", "population.yaml", "--format", "json"])
    verifier_bytes = capsys.readouterr().out.encode("utf-8")
    monkeypatch.chdir(previous)
    model_copy.unlink()

    async def trusted_verifier(*_args: Any, **_kwargs: Any) -> tuple[int, bytes]:
        return verifier_exit, verifier_bytes

    original_publish_best = session_module.SessionStore.publish_best

    def crash_after_best_publication(self, record):
        original_publish_best(self, record)
        raise RuntimeError("crash after first completed attempt")

    monkeypatch.setattr(
        session_module.SessionStore,
        "publish_best",
        crash_after_best_publication,
    )
    with pytest.raises(RuntimeError, match="first completed attempt"):
        asyncio.run(
            run_session(
                contract,
                contract_sha256=contract_sha256,
                adapter_id=AgentAdapterId.codex,
                prompt="repair the candidate",
                candidate_root=root / "candidate",
                run_root=run,
                verifier=trusted_verifier,
                expected_payload_versions=bound_versions,
            )
        )
    monkeypatch.setattr(
        session_module.SessionStore,
        "publish_best",
        original_publish_best,
    )
    assert (run / "attempts" / "0001" / "attempt.json").is_file()
    assert (run / "launches" / "0001.json").is_file()
    assert not (run / "launches" / "0002.json").exists()

    launches = 0

    async def must_not_launch(*args: Any, **kwargs: Any) -> InvocationResult:
        nonlocal launches
        launches += 1
        raise AssertionError("resume mismatch reached the agent")

    with pytest.raises(ValueError, match="different agent adapter"):
        asyncio.run(
            run_session(
                contract,
                contract_sha256=contract_sha256,
                adapter_id=AgentAdapterId.claude,
                prompt="repair the candidate",
                candidate_root=root / "candidate",
                run_root=run,
                verifier=trusted_verifier,
                invoker=must_not_launch,
                expected_payload_versions=bound_versions,
            )
        )
    with pytest.raises(ValueError, match="different agent instructions"):
        asyncio.run(
            run_session(
                contract,
                contract_sha256=contract_sha256,
                adapter_id=AgentAdapterId.codex,
                prompt="changed repair instructions",
                candidate_root=root / "candidate",
                run_root=run,
                verifier=trusted_verifier,
                invoker=must_not_launch,
                expected_payload_versions=bound_versions,
            )
        )
    for changed_policy in (
        contract.model_copy(update={"max_attempts": 3}),
        contract.model_copy(update={"wall_seconds": 1.0}),
    ):
        with pytest.raises(ValueError, match="different agent instructions"):
            asyncio.run(
                run_session(
                    changed_policy,
                    contract_sha256=contract_sha256,
                    adapter_id=AgentAdapterId.codex,
                    prompt="repair the candidate",
                    candidate_root=root / "candidate",
                    run_root=run,
                    verifier=trusted_verifier,
                    invoker=must_not_launch,
                    expected_payload_versions=bound_versions,
                )
            )
    population = root / "candidate" / "population.yaml"
    population.write_bytes(population.read_bytes() + b"# uncommitted mutation\n")
    with pytest.raises(ValueError, match="mutable candidate differs"):
        asyncio.run(
            run_session(
                contract,
                contract_sha256=contract_sha256,
                adapter_id=AgentAdapterId.codex,
                prompt="repair the candidate",
                candidate_root=root / "candidate",
                run_root=run,
                verifier=trusted_verifier,
                invoker=must_not_launch,
                expected_payload_versions=bound_versions,
            )
        )
    assert launches == 0


def test_crashing_invoker_consumes_one_durable_launch_and_restart_never_reuses_it(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _make_experiment(tmp_path, monkeypatch, max_attempts=1)
    contract_path = root / "session.contract.json"
    contract_bytes = contract_path.read_bytes()
    contract = read_session_contract(
        contract_path,
        experiment_root=root,
        experiment_id="EXP-401-session",
    )
    run = root / "runs" / "run-crashed-launch"
    launches = 0

    async def crashing_invoker(*args: Any, **kwargs: Any) -> InvocationResult:
        nonlocal launches
        launches += 1
        raise RuntimeError("injected invoker crash")

    async def verifier(*args: Any, **kwargs: Any) -> tuple[int, bytes]:
        raise AssertionError("crashed invocation reached verifier")

    with pytest.raises(RuntimeError, match="injected invoker crash"):
        asyncio.run(
            run_session(
                contract,
                contract_sha256=_sha256(contract_bytes),
                adapter_id=AgentAdapterId.codex,
                prompt="repair the candidate",
                candidate_root=root / "candidate",
                run_root=run,
                verifier=verifier,
                invoker=crashing_invoker,
            )
        )
    for _ in range(2):
        with pytest.raises(ValueError, match="uncommitted launch intent"):
            asyncio.run(
                run_session(
                    contract,
                    contract_sha256=_sha256(contract_bytes),
                    adapter_id=AgentAdapterId.codex,
                    prompt="repair the candidate",
                    candidate_root=root / "candidate",
                    run_root=run,
                    verifier=verifier,
                    invoker=crashing_invoker,
                )
            )

    assert launches == 1
    assert (run / "launches" / "0001.json").is_file()
    assert list((run / "attempts").iterdir()) == []


@pytest.mark.parametrize(
    ("case_id", "scenario", "expected", "attempts"),
    [
        ("session-exact-all-required-acceptance", "accepted", "accepted", 1),
        ("session-missing-required-output", "missing", "verifier-failure", 1),
        ("session-malformed-exit-mismatch", "mismatch", "verifier-failure", 1),
        (
            "session-alethic-indeterminate-deontic-warning",
            "modality",
            "budget-exhausted",
            1,
        ),
        (
            "session-same-score-different-candidate",
            "same-score",
            "budget-exhausted",
            2,
        ),
        ("session-a-b-a-oscillation", "oscillation", "oscillation", 3),
        (
            "session-attempt-wall-exhaustion-descendant-cleanup",
            "wall",
            "budget-exhausted",
            1,
        ),
        ("session-stdout-stderr-flood", "flood", "agent-failure", 1),
    ],
)
def test_every_reference_corpus_case_runs_through_the_public_entrypoint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    case_id: str,
    scenario: str,
    expected: str,
    attempts: int,
) -> None:
    import gnd.exp.session as session_module

    model = CHECKER / "misc.orm.yaml" if scenario == "modality" else None
    subject = (
        CHECKER / "population.misc_pass.yaml"
        if scenario == "modality"
        else SKELETON / "population.bad.yaml"
    )
    # Version and main process retain one shared deadline. The wall fixture
    # uses a shell builtin probe and must prove its child actually started.
    wall_seconds = 0.5 if scenario == "wall" else 5.0
    root = _make_experiment(
        tmp_path,
        monkeypatch,
        model_fixture=model,
        subject_fixture=subject,
        max_attempts=attempts,
        wall_seconds=wall_seconds,
        case_id=case_id,
        # Only the accepted row's agent produces the contracted bytes.
        expected_bytes=_accepted_population() if scenario == "accepted" else None,
    )
    marker = tmp_path / "descendant-survived"
    _write_corpus_agent(
        tmp_path / "bin" / "codex",
        scenario=scenario,
        good_population=_accepted_population(),
        bad_population=(SKELETON / "population.bad.yaml").read_bytes(),
        marker=marker,
    )

    real_verifier = session_module.run_gnd_verifier
    if scenario == "missing":

        async def missing(*args: Any, **kwargs: Any) -> tuple[int, bytes]:
            raise RuntimeError("sanitized verifier absence")

        monkeypatch.setattr(session_module, "run_gnd_verifier", missing)
    elif scenario == "mismatch":

        async def mismatch(case, snapshot, *, experiment_root, timeout_seconds):
            process_exit, raw = await real_verifier(
                case,
                snapshot,
                experiment_root=experiment_root,
                timeout_seconds=timeout_seconds,
            )
            return process_exit + 1, raw

        monkeypatch.setattr(session_module, "run_gnd_verifier", mismatch)

    exit_code, rendered = _run(root, "codex", capsys)

    assert exit_code == (0 if expected == "accepted" else cli.EXIT_SESSION_NOT_ACCEPTED)
    assert rendered["disposition"] == expected
    assert rendered["attempt_count"] == attempts
    corpus_row = _session_case(case_id)
    assert rendered["disposition"] == corpus_row["machine_label"]["disposition"]
    _assert_exact_run_evidence(root, rendered, corpus_row=corpus_row)

    run = root / "runs" / rendered["run_id"]
    if scenario == "same-score":
        assert corpus_row["assertions"] == [
            "distinct-candidate-digests-are-not-recurrence"
        ]
        assert rendered["disposition"] not in {"stagnation", "oscillation"}
        digests = [
            json.loads((path / "candidate.inventory.json").read_bytes())["tree_sha256"]
            for path in sorted((run / "attempts").iterdir())
        ]
        assert len(set(digests)) == 2
    if scenario == "wall":
        time.sleep(0.9)
        assert marker.with_suffix(".started").is_file()
        assert not marker.exists()
        assert "wall budget" in rendered["terminal_reason"]
        invocation = json.loads((run / "attempts" / "0001" / "attempt.json").read_bytes())[
            "invocation"
        ]
        assert invocation["version"].startswith("<version:sha256=")
        assert invocation["status"] == "timed-out"
        assert invocation["spawned"] is True
        assert invocation["process_group_cleaned"] is True
    if scenario == "flood":
        invocation = json.loads((run / "attempts" / "0001" / "attempt.json").read_bytes())[
            "invocation"
        ]
        assert invocation["stdout_observed_bytes"] >= 2 * 1024 * 1024
        assert invocation["stderr_observed_bytes"] >= 2 * 1024 * 1024
        assert invocation["stdout_truncated"] is invocation["stderr_truncated"] is True


@pytest.mark.parametrize(
    ("model_fixture", "subject_fixture", "subject_bytes", "child_exit"),
    [
        pytest.param(SKELETON / "model.orm.yaml", SKELETON / "population.bad.yaml", None, 1),
        pytest.param(CHECKER / "setfam.orm.yaml", CHECKER / "population.empty.yaml", None, 2),
        pytest.param(SKELETON / "model.orm.yaml", None, b"not: [valid", 3),
        pytest.param(CHECKER / "misc.orm.yaml", CHECKER / "population.misc_pass.yaml", None, 4),
    ],
)
def test_verifier_bands_never_escape_as_the_parent_session_exit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    model_fixture: Path,
    subject_fixture: Path | None,
    subject_bytes: bytes | None,
    child_exit: int,
) -> None:
    root = _make_experiment(
        tmp_path,
        monkeypatch,
        model_fixture=model_fixture,
        subject_fixture=subject_fixture,
        subject_bytes=subject_bytes,
    )

    exit_code, rendered = _run(root, "codex", capsys)

    assert exit_code == cli.EXIT_SESSION_NOT_ACCEPTED == 15
    assert exit_code != child_exit
    assert rendered["disposition"] == "budget-exhausted"
    raw_path = (
        root
        / "runs"
        / rendered["run_id"]
        / "attempts"
        / "0001"
        / "verifier"
        / "session-exact-all-required-acceptance.json"
    )
    assert json.loads(raw_path.read_bytes())["exit_code"] == child_exit
    run = root / "runs" / rendered["run_id"]
    best = json.loads((run / "best.json").read_text(encoding="utf-8"))
    attempt_bytes = (run / "attempts" / "0001" / "attempt.json").read_bytes()
    assert best["attempt"] == 1
    assert best["attempt_manifest_sha256"] == hashlib.sha256(attempt_bytes).hexdigest()


def _sole_verifier_payload(root: Path, rendered: dict[str, Any], case_id: str) -> dict[str, Any]:
    path = (
        root / "runs" / rendered["run_id"] / "attempts" / "0001" / "verifier" / f"{case_id}.json"
    )
    return json.loads(path.read_bytes())


def _sole_expected_output_feedback(root: Path, rendered: dict[str, Any]) -> dict[str, Any]:
    feedback_bytes = (
        root / "runs" / rendered["run_id"] / "attempts" / "0001" / "feedback.json"
    ).read_bytes()
    feedback = json.loads(feedback_bytes)
    assert len(feedback["required"]) == 1
    acceptance = feedback["required"][0]["acceptance"]
    assert acceptance["mode"] == "exact-bytes"
    declared = acceptance["outputs"]
    assert len(declared) == 1
    rendered_feedback = feedback_bytes.decode("utf-8")
    for forbidden in ("expected_sha256", "observed_sha256", "size_bytes", "expected/"):
        assert forbidden not in rendered_feedback
    return declared[0]


def test_do_nothing_agent_reds_against_a_contract_it_never_satisfied(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """R-01's second reproduction: the declared output is never produced."""

    case_id = "session-declared-output-never-produced"
    root = _make_experiment(
        tmp_path,
        monkeypatch,
        case_id=case_id,
        expected_bytes=_contracted_expectation(case_id),
        expected_candidate_path="answer.json",
    )

    exit_code, rendered = _run(root, "codex", capsys)

    assert exit_code == cli.EXIT_SESSION_NOT_ACCEPTED
    assert rendered["disposition"] == "budget-exhausted"
    assert rendered["terminal_reason"] != "all required cases accepted"
    # Attribution: every other conjunct of acceptance held.  The candidate is a
    # model-conforming population, so the verifier itself was ready to accept.
    assert _sole_verifier_payload(root, rendered, case_id)["acceptance_ready"] is True
    observation = _sole_expected_output_feedback(root, rendered)
    assert observation["state"] == "absent"
    assert not (root / "candidate" / "answer.json").exists()
    _assert_exact_run_evidence(root, rendered, corpus_row=_session_case(case_id))


def test_produced_output_differing_from_the_expectation_reds(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """R-01's first reproduction: produced bytes differ from the expectation."""

    case_id = "session-declared-output-differs-from-expectation"
    contracted = _contracted_expectation(case_id)
    # A different, still model-conforming population.  Attribution depends on
    # this: a non-conforming candidate would red through the verifier whether
    # or not the expected-output conjunct exists.
    differing = _accepted_population() + b"# a population the contract did not ask for\n"
    assert differing != contracted
    root = _make_experiment(
        tmp_path,
        monkeypatch,
        subject_fixture=SKELETON / "population.bad.yaml",
        case_id=case_id,
        expected_bytes=contracted,
    )
    _write_producing_agent(
        tmp_path / "bin" / "codex",
        produced=differing,
        candidate_path="population.yaml",
    )

    exit_code, rendered = _run(root, "codex", capsys)

    assert exit_code == cli.EXIT_SESSION_NOT_ACCEPTED
    assert rendered["disposition"] == "budget-exhausted"
    assert rendered["terminal_reason"] != "all required cases accepted"
    assert _sole_verifier_payload(root, rendered, case_id)["acceptance_ready"] is True
    observation = _sole_expected_output_feedback(root, rendered)
    assert observation["state"] == "differs"
    produced_path = (
        root / "runs" / rendered["run_id"] / "attempts" / "0001" / "candidate" / "population.yaml"
    )
    assert produced_path.read_bytes() == differing
    _assert_exact_run_evidence(root, rendered, corpus_row=_session_case(case_id))


def test_agent_producing_the_contracted_output_is_accepted(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The over-correction control: the repaired gate is still passable."""

    contracted = _contracted_expectation()
    root = _make_experiment(
        tmp_path,
        monkeypatch,
        subject_fixture=SKELETON / "population.bad.yaml",
        expected_bytes=contracted,
    )
    _write_producing_agent(
        tmp_path / "bin" / "codex",
        produced=contracted,
        candidate_path="population.yaml",
    )

    exit_code, rendered = _run(root, "codex", capsys)

    assert exit_code == 0
    assert rendered["disposition"] == "accepted"
    assert rendered["terminal_reason"] == "all required cases accepted"
    observation = _sole_expected_output_feedback(root, rendered)
    assert observation["state"] == "matched"


def test_agent_failure_is_a_well_formed_nonacceptance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = _make_experiment(tmp_path, monkeypatch, agent_exit=23)

    exit_code, rendered = _run(root, "codex", capsys)

    assert exit_code == cli.EXIT_SESSION_NOT_ACCEPTED
    assert rendered["disposition"] == "agent-failure"
    assert rendered["attempt_count"] == 1


def test_process_payload_mismatch_cannot_spoof_public_acceptance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    import gnd.exp.session as session_module

    root = _make_experiment(tmp_path, monkeypatch)
    real_verifier = session_module.run_gnd_verifier

    async def mismatched(case, snapshot, *, experiment_root, timeout_seconds):
        _process_exit, raw = await real_verifier(
            case,
            snapshot,
            experiment_root=experiment_root,
            timeout_seconds=timeout_seconds,
        )
        assert json.loads(raw)["exit_code"] == 0
        return 1, raw

    monkeypatch.setattr(session_module, "run_gnd_verifier", mismatched)
    exit_code, rendered = _run(root, "codex", capsys)

    assert exit_code == cli.EXIT_SESSION_NOT_ACCEPTED
    assert rendered["disposition"] == "verifier-failure"
    assert rendered["terminal_reason"] == (
        "one or more declared verifier cases did not produce valid evidence"
    )
    assert not (root / "runs" / rendered["run_id"] / "best.json").exists()


def test_candidate_cannot_shadow_the_fixed_gnd_verifier_module(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = _make_experiment(tmp_path, monkeypatch, expected_bytes=_accepted_population())
    marker = tmp_path / "candidate-module-ran"
    hostile_package = root / "candidate" / "gnd"
    hostile_package.mkdir()
    (hostile_package / "__main__.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('ran')\n",
        encoding="utf-8",
    )

    exit_code, rendered = _run(root, "codex", capsys)

    assert exit_code == 0
    assert rendered["disposition"] == "accepted"
    assert not marker.exists(), "candidate bytes replaced the trusted verifier module"


def test_run_distinguishes_missing_malformed_and_path_refusal(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = _make_experiment(tmp_path, monkeypatch)
    contract = root / "session.contract.json"
    contract.unlink()
    assert main(["exp", "run", str(root), "--adapter", "codex"]) == cli.EXIT_NO_INPUT
    capsys.readouterr()

    contract.write_text("{}\n", encoding="utf-8")
    assert main(["exp", "run", str(root), "--adapter", "codex"]) == 3
    capsys.readouterr()

    candidate = root / "candidate"
    shutil.rmtree(candidate)
    candidate.symlink_to(tmp_path, target_is_directory=True)
    # Restore a valid contract before exercising the candidate trust boundary.
    other = tmp_path / "other"
    other.mkdir()
    valid_root = _make_experiment(other, monkeypatch)
    shutil.rmtree(valid_root / "candidate")
    (valid_root / "candidate").symlink_to(tmp_path, target_is_directory=True)
    assert main(["exp", "run", str(valid_root), "--adapter", "codex"]) == cli.EXIT_IO


def test_spec_kind_and_contract_identity_must_match_before_agent_spawn(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = _make_experiment(tmp_path, monkeypatch)
    marker = tmp_path / "agent-ran"
    executable = tmp_path / "bin" / "codex"
    executable.write_text(
        executable.read_text(encoding="utf-8").replace(
            'print("agent stdout")', f'open({str(marker)!r}, "w").write("ran")'
        ),
        encoding="utf-8",
    )
    spec = root / "SPEC.md"
    spec.write_text(
        spec.read_text(encoding="utf-8").replace("kind: data-driven", "kind: analysis"),
        encoding="utf-8",
    )
    assert main(["exp", "run", str(root), "--adapter", "codex"]) == 3
    assert not marker.exists()
    capsys.readouterr()

    spec.write_text(
        spec.read_text(encoding="utf-8").replace("kind: analysis", "kind: data-driven"),
        encoding="utf-8",
    )
    contract_path = root / "session.contract.json"
    document = json.loads(contract_path.read_text(encoding="utf-8"))
    document["experiment_id"] = "EXP-999-spoofed"
    contract_path.write_text(json.dumps(document) + "\n", encoding="utf-8")
    assert main(["exp", "run", str(root), "--adapter", "codex"]) == 3
    assert not marker.exists()


def test_cli_can_tighten_but_not_loosen_or_inject_process_configuration(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = _make_experiment(tmp_path, monkeypatch, expected_bytes=_accepted_population())
    assert (
        main(
            [
                "exp",
                "run",
                str(root),
                "--adapter",
                "codex",
                "--wall-seconds",
                "6",
            ]
        )
        == cli.EXIT_USAGE
    )
    capsys.readouterr()

    exit_code = main(
        [
            "exp",
            "run",
            str(root),
            "--adapter",
            "codex",
            "--wall-seconds",
            "4",
        ]
    )
    assert exit_code == 0
    capsys.readouterr()

    for forbidden in ("--executable", "--model", "--provider", "--argv"):
        with pytest.raises(SystemExit) as caught:
            main(["exp", "run", str(root), "--adapter", "codex", forbidden, "injected"])
        assert caught.value.code == cli.EXIT_USAGE
        capsys.readouterr()


def test_unexpected_controller_defect_maps_to_internal_without_traceback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    import gnd.exp.session as session_module

    root = _make_experiment(tmp_path, monkeypatch)

    async def broken_controller(*args, **kwargs):
        raise RuntimeError("simulated controller defect")

    monkeypatch.setattr(session_module, "run_session", broken_controller)
    assert main(["exp", "run", str(root), "--adapter", "codex"]) == cli.EXIT_INTERNAL
    output = capsys.readouterr()
    assert "RuntimeError: simulated controller defect" in output.out
    assert "Traceback" not in output.out + output.err


@pytest.mark.parametrize("accepted", [True, False])
def test_session_outcome_never_controls_experiment_closure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    accepted: bool,
) -> None:
    root = _make_experiment(
        tmp_path,
        monkeypatch,
        subject_fixture=(SKELETON / "population.good.yaml") if accepted else None,
        subject_bytes=None if accepted else b"not: [valid",
        expected_bytes=_accepted_population() if accepted else None,
    )
    run_exit, rendered = _run(root, "codex", capsys)
    assert run_exit == (0 if accepted else cli.EXIT_SESSION_NOT_ACCEPTED)
    evidence = f"runs/{rendered['run_id']}/result.json"
    reason = (
        "  reason: the one bounded attempt did not satisfy the contract\n" if not accepted else ""
    )
    (root / "CONCLUSIONS.md").write_text(
        "---\n"
        + "id: EXP-401-session\n"
        + "resolves:\n"
        + "- id: Q1\n"
        + f"  outcome: {'answered' if accepted else 'unanswered'}\n"
        + f"  evidence: {evidence}\n"
        + reason
        + "---\n\n# Conclusions\n",
        encoding="utf-8",
    )
    assert main(["exp", "close", str(root)]) == 0
    capsys.readouterr()

    (root / "CONCLUSIONS.md").unlink()
    assert main(["exp", "close", str(root)]) == cli.EXIT_EXPERIMENT_OPEN
