"""P3-XR (r2 A8): the LIVE ``gnd exp run`` path consumes derivation feedback.

Offline fake adapters, the REAL ``gnd check`` verifier subprocess, the real
store. Attempt one leaves the seeded incomplete claim in place and reds
``derived-extension-incomplete`` at band 1; the current schema-version-4 feedback
delivers the obligation's address and witness; attempt two claims the exact
extension and the session exits 0. Retained payloads, the attempt record's v4
binding, replay revalidation and the feedback digest round-trip are asserted
over the published evidence.

Committed red: before the session lane, ``validate_verifier_payload`` refused
every v4 payload ("must be current version 3") and no feedback shape carried a
derivation row, so the first attempt terminated as verifier-failure.
"""


from __future__ import annotations

import base64
import contextlib
import hashlib
import io
import json
import os
import stat
from pathlib import Path
from typing import Any

import pytest
from support.digests import sha256_bytes as _sha256

from gnd import cli
from gnd.cli import main
from gnd.exp.session import case_payload_versions
from gnd.exp.session_contract import read_session_contract
from gnd.exp.session_eval import (
    ASSURANCE_FEEDBACK_SCHEMA_VERSION,
    build_attempt_feedback,
    canonical_feedback,
)
from gnd.exp.session_store import SessionStore, _retained_wire
from gnd.report import MODEL_BOUND_DERIVATION_PAYLOAD_SCHEMA_VERSION

REPO_ROOT = Path(__file__).resolve().parent.parent


CORPUS = REPO_ROOT / "tests" / "fixtures" / "phase3-consumers"


FEEDBACK_ANSWER = json.loads(
    (CORPUS / "answers" / "feedback-derivation-rows.json").read_text(encoding="utf-8")
)


EXPERIMENT_ID = "EXP-801-derivation-session"


CASE_ID = "eligibility-derivation"


def _bound(path: str, data: bytes, media_type: str) -> dict[str, Any]:
    return {
        "path": path,
        "media_type": media_type,
        "encoding": "utf-8",
        "sha256": _sha256(data),
        "size_bytes": len(data),
    }


def _write_derivation_retry_agent(executable: Path, *, exact: bytes) -> None:
    encoded = base64.b64encode(exact).decode("ascii")
    executable.write_text(
        f"""#!/usr/bin/env python3
import base64
import json
import pathlib
import sys

if "--version" in sys.argv:
    print("derivation-agent 1.0")
    raise SystemExit(0)

counter = pathlib.Path(".attempt-count")
attempt = int(counter.read_text()) + 1 if counter.exists() else 1
counter.write_text(str(attempt))
feedback = sys.stdin.buffer.read()
if attempt == 1:
    if feedback:
        raise SystemExit(41)
    raise SystemExit(0)

document = json.loads(feedback)
if document["schema_version"] != 4:
    raise SystemExit(42)
rows = document["required"][0]["derivations"]
if len(rows) != 1:
    raise SystemExit(43)
row = rows[0]
if row["derivation_ref"] != "derivation:book_is_eligible":
    raise SystemExit(44)
if row["kind"] != "derived-extension-incomplete" or row["reason_code"] is not None:
    raise SystemExit(45)
if row["witness"] != {{"book": "alpha"}}:
    raise SystemExit(46)
if b'"beta"' in feedback:
    raise SystemExit(47)  # only the published counterexample may cross the wire
pathlib.Path("population.yaml").write_bytes(base64.b64decode({encoded!r}))
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)


def _make_experiment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        assert (
            main(
                [
                    "exp",
                    "init",
                    EXPERIMENT_ID,
                    "--out",
                    str(tmp_path),
                    "--kind",
                    "data-driven",
                    "--question",
                    "Q1=Can the live session hold an agent to a derivation obligation?",
                ]
            )
            == 0
        )
    root = tmp_path / EXPERIMENT_ID
    candidate = root / "candidate"
    candidate.mkdir()

    model_bytes = (CORPUS / "eligibility.orm.yaml").read_bytes()
    incomplete = (CORPUS / "eligibility.incomplete.population.yaml").read_bytes()
    exact = (CORPUS / "eligibility.exact.population.yaml").read_bytes()
    (root / "model.orm.yaml").write_bytes(model_bytes)
    (candidate / "population.yaml").write_bytes(incomplete)

    task = b'{"task": "claim the exact derived extension"}\n'
    input_path = root / "input" / "task.json"
    input_path.parent.mkdir()
    input_path.write_bytes(task)

    contract = {
        "schema_version": 2,
        "experiment_id": EXPERIMENT_ID,
        "max_attempts": 2,
        "wall_seconds": 30.0,
        "cases": [
            {
                "case_id": CASE_ID,
                "role": "required",
                "inputs": [_bound("input/task.json", task, "application/json")],
                "acceptance": {
                    "mode": "constraint-satisfaction",
                    "coverage": [{"fact_type": "book_listed", "min_facts": 1}],
                },
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
    for adapter_id in ("claude", "codex"):
        _write_derivation_retry_agent(bin_dir / adapter_id, exact=exact)
    for name in (
        "CODEX_HOME",
        "CLAUDE_CONFIG_DIR",
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_AUTH_TOKEN",
        "CLAUDE_CODE_OAUTH_TOKEN",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")
    return root


def test_the_live_session_delivers_the_derivation_witness_and_accepts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _make_experiment(tmp_path, monkeypatch)

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exit_code = main(["exp", "run", str(root), "--adapter", "codex"])
    assert exit_code == 0, stdout.getvalue()
    result = json.loads(stdout.getvalue().splitlines()[-1])
    assert result["disposition"] == "accepted"
    assert result["attempt_count"] == 2

    run_root = root / "runs" / "run-0001"

    # The version map the CLI computed is reproducible from the contract.
    contract = read_session_contract(
        root / "session.contract.json",
        experiment_root=root,
        experiment_id=EXPERIMENT_ID,
    )
    versions = case_payload_versions(contract, root)
    # v5.1 Phase 3: the session verifier runs `gnd check`/`gnd verify`, so the
    # version it expects is the MODEL-BOUND structured variant. The claim is
    # unchanged -- the model, not a constant, decides the case's evidence wire.
    assert versions == {CASE_ID: 7}
    assert versions[CASE_ID].legacy_version == MODEL_BOUND_DERIVATION_PAYLOAD_SCHEMA_VERSION

    # Attempt 1: retained raw payload is the derivation red, feedback is v4
    # carrying exactly the corpus answer rows.
    raw_payload = json.loads(
        (run_root / "attempts" / "0001" / "verifier" / f"{CASE_ID}.json").read_bytes()
    )
    assert raw_payload["schema_version"] == 7
    assert raw_payload["model_digest"].startswith("sha256:")
    assert raw_payload["exit_code"] == 1
    (verdict,) = raw_payload["derivations"]
    assert verdict["verdict"] == "fail"

    feedback_one = json.loads((run_root / "attempts" / "0001" / "feedback.json").read_bytes())
    assert feedback_one["schema_version"] == ASSURANCE_FEEDBACK_SCHEMA_VERSION == 4
    assert feedback_one["disposition"] == "retry"
    assert feedback_one["required"][0]["derivations"] == FEEDBACK_ANSWER["incomplete"]

    attempt_one = json.loads((run_root / "attempts" / "0001" / "attempt.json").read_bytes())
    assert attempt_one["schema_version"] == 4
    assert attempt_one["feedback_schema_version"] == 4

    # Attempt 2: the exact claim is accepted and its v4 row carries the
    # REQUIRED empty derivations tuple, never an absent key.
    feedback_two = json.loads((run_root / "attempts" / "0002" / "feedback.json").read_bytes())
    assert feedback_two["schema_version"] == 4
    assert feedback_two["disposition"] == "accepted"
    assert feedback_two["required"][0]["derivations"] == FEEDBACK_ANSWER["exact"] == []


def test_replay_revalidates_and_rebuilds_identical_v3_feedback_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Retained v4 bytes keep their claim; replay cannot recreate live authority."""

    root = _make_experiment(tmp_path, monkeypatch)
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        assert main(["exp", "run", str(root), "--adapter", "codex"]) == 0

    run_root = root / "runs" / "run-0001"
    contract = read_session_contract(
        root / "session.contract.json",
        experiment_root=root,
        experiment_id=EXPERIMENT_ID,
    )
    contract_sha256 = hashlib.sha256((root / "session.contract.json").read_bytes()).hexdigest()
    versions = case_payload_versions(contract, root)
    store = SessionStore(
        run_root, run_id=run_root.name, contract_id=contract.experiment_id
    )
    for attempt_index in (1, 2):
        record, _, feedback, persisted = store._load_attempt_for_resume(
            attempt_index,
            contract=contract,
            expected_payload_versions=versions,
        )
        assert record.schema_version == 4
        rebuilt = build_attempt_feedback(
            run_id=run_root.name,
            contract=contract,
            contract_sha256=contract_sha256,
            invocation=record.invocation,
            evaluation=record.evaluation,
            disposition=feedback.disposition,
            schema_version=feedback.schema_version,
        )
        # v4 replay preserves the archived wire but cannot recreate a live
        # process capability from JSON. The normalized business signal is
        # unchanged; a fresh projection conservatively withholds assurance.
        assert record.evaluation.results[0]._assurance_execution is None
        rebuilt_wire = json.loads(canonical_feedback(rebuilt)[0])
        archived_wire = json.loads(persisted)
        for document in (rebuilt_wire, archived_wire):
            for row in document["required"] + document["diagnostic"]:
                row.pop("assurance")
        assert rebuilt_wire == archived_wire


def test_replay_refuses_the_wrong_expected_version(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """D-P3.4 at the store: a v4 attempt cannot replay under a v3 expectation."""

    root = _make_experiment(tmp_path, monkeypatch)
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        assert main(["exp", "run", str(root), "--adapter", "codex"]) == 0

    run_root = root / "runs" / "run-0001"
    contract = read_session_contract(
        root / "session.contract.json",
        experiment_root=root,
        experiment_id=EXPERIMENT_ID,
    )
    store = SessionStore(
        run_root, run_id=run_root.name, contract_id=contract.experiment_id
    )
    with pytest.raises(ValueError, match="must be current version 3"):
        store._load_attempt_for_resume(1, contract=contract)


def test_the_derivation_experiment_closes_at_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """T3.7's tail: the close gate carries the v4 evidence chain."""

    root = _make_experiment(tmp_path, monkeypatch)
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        assert main(["exp", "run", str(root), "--adapter", "codex"]) == 0

    (root / "CONCLUSIONS.md").write_text(
        "---\n"
        f"id: {EXPERIMENT_ID}\n"
        "resolves:\n"
        "- id: Q1\n"
        "  outcome: answered\n"
        "  reason: >-\n"
        "    Yes. Attempt one redded derived-extension-incomplete at band 1,\n"
        "    the schema-version-4 feedback delivered the obligation's address\n"
        "    and witness, and attempt two's exact claim was accepted at 0.\n"
        "  evidence: runs/run-0001/result.json\n"
        "---\n\n"
        f"# {EXPERIMENT_ID} conclusions\n",
        encoding="utf-8",
    )
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        code = main(["exp", "close", str(root)])
    assert code == 0, stdout.getvalue()


def test_cli_exit_registries_are_unchanged() -> None:
    """No new exit band anywhere in this phase (plan section 2)."""

    assert cli.EXIT_GENERATOR == 5
    assert not hasattr(cli, "EXIT_DERIVATION")


@pytest.mark.parametrize("retained", [3, 5, 4.0])
def test_a_declared_case_never_lets_a_retained_payload_pick_its_own_wire(retained: Any) -> None:
    """P3R-2: declared wire 6 remains the independent replay anchor."""
    wire = MODEL_BOUND_DERIVATION_PAYLOAD_SCHEMA_VERSION
    raw = json.dumps({"schema_version": retained}).encode("utf-8")
    assert _retained_wire(raw, {CASE_ID: wire}, CASE_ID) == wire

