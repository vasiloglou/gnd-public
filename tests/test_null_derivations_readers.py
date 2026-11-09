"""Readers of a ``derivations`` collection treat a present ``null`` as absent.

``dict.get("derivations", [])`` returns ``None`` when the key is present but
null, so each reader below once iterated ``None``. The report-level case is
covered by ``test_coverage_cli``; these pin the transition-snapshot reader in
the session evaluator and the diff projection in redaction.
"""

from __future__ import annotations

import copy
import json

from support.cli_runner import run_main
from support.repository import REPO_ROOT

from gnd.exp import session_eval
from gnd.model import Model, parse_model_document
from gnd.redaction import RedactionPolicy, project_output

APPROVALS = REPO_ROOT / "src/gnd/examples/approvals"
MODEL = "src/gnd/examples/approvals/model.orm.yaml"


def _transition_report() -> dict:
    result = run_main(
        [
            "check",
            MODEL,
            "--pre",
            str(APPROVALS / "state.pop.yaml"),
            "--steps",
            str(APPROVALS / "approve-41.steps.json"),
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def _validate(payload: dict) -> session_eval.CaseEvaluation:
    digest = "0" * 64
    return session_eval.validate_transition_payload(
        json.dumps(payload).encode("utf-8"),
        case_id="null-derivations",
        role="required",
        process_exit=payload["exit_code"],
        expected_schema_version=payload["schema_version"],
        expected_model=payload["model"],
        expected_post=None,
        candidate_sha256=digest,
        contract_sha256=digest,
        evidence_candidate_sha256=digest,
        evidence_contract_sha256=digest,
    )


def test_transition_snapshot_null_derivations_read_as_absent() -> None:
    report = _transition_report()
    block = report["transition"]
    assert block["evaluated"] and block["steps"]
    assert "derivations" not in block["pre_snapshot"]
    baseline = _validate(report)

    nulled = copy.deepcopy(report)
    nulled["transition"]["pre_snapshot"]["derivations"] = None
    nulled["transition"]["post_snapshot"]["derivations"] = None
    for step in nulled["transition"]["steps"]:
        step["intermediate"]["derivations"] = None
    evaluation = _validate(nulled)
    # Only the payload digest may move: the bytes differ, the reading must not.
    assert evaluation.raw_payload_sha256 != baseline.raw_payload_sha256
    assert evaluation.model_copy(
        update={"raw_payload_sha256": baseline.raw_payload_sha256}
    ) == baseline


def test_diff_projection_null_derivations_read_as_absent() -> None:
    path = APPROVALS / "model.orm.yaml"
    document = parse_model_document(path.read_bytes(), source=path)
    document["fact_types"][0]["roles"][0]["redact"] = True
    policy = RedactionPolicy.from_model(Model.model_validate(document))
    assert policy.active
    payload = {"populations": [{"a_to_b": [], "b_to_a": [], "derivations": None}]}
    projected = project_output("diff", payload, policy=policy, mode="applied")
    assert projected == payload
