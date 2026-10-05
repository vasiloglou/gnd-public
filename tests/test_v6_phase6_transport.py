"""Only a live supervised fixed verifier can provide a session capability."""

import asyncio
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from gnd.assurance_transport import VerifiedPayload, consume_receipt
from gnd.exp.session import run_gnd_verifier
from gnd.exp.session_contract import SessionCase
from gnd.exp.session_eval import validate_verifier_payload
from gnd.report import CurrentReportVersion

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests/fixtures/v6-assurance"


def run_live(tmp_path):
    case = SessionCase.model_validate_json((CORPUS / "legacy-feedback/case.json").read_bytes())
    snapshot = tmp_path / "candidate"
    snapshot.mkdir()
    shutil.copy2(
        CORPUS / "cases/expense-approval/conforming/population.json", snapshot / "population.json"
    )
    code, raw = asyncio.run(run_gnd_verifier(case, snapshot, experiment_root=ROOT))
    assert code == 0
    return case, raw


def test_live_process_transports_an_exact_report_and_receipt(tmp_path):
    case, raw = run_live(tmp_path)
    assert type(raw) is VerifiedPayload
    assert raw.execution.complete and raw.execution.surface == "snapshot"
    assert raw.receipt["report_sha256"] == hashlib.sha256(raw).hexdigest()
    assert raw.case_id == case.case_id
    assert json.loads(raw)["schema_version"] == 7
    assert not (tmp_path / "candidate" / "execution-receipt.json").exists()


def test_public_reader_never_mints_an_execution_from_even_verified_bytes(tmp_path):
    case, raw = run_live(tmp_path)
    result = validate_verifier_payload(
        raw,
        case_id=case.case_id,
        role="required",
        process_exit=0,
        expected_command="check",
        expected_subject="population.json",
        expected_model=case.verify.model.path,
        expected_schema_version=CurrentReportVersion(5),
        candidate_sha256="a" * 64,
        contract_sha256="b" * 64,
        evidence_candidate_sha256="a" * 64,
        evidence_contract_sha256="b" * 64,
    )
    assert result._assurance_execution is None


@pytest.mark.parametrize("mutation", ["nonce", "report", "producer", "extra", "missing"])
def test_a_modified_receipt_cannot_recreate_the_live_capability(tmp_path, mutation):
    case, raw = run_live(tmp_path)
    document = json.loads(json.dumps(raw.receipt))
    nonce, producer = document["nonce"], document["producer_identity"]
    if mutation == "nonce":
        document["nonce"] = "a" * 64
    elif mutation == "report":
        document["report_sha256"] = "a" * 64
    elif mutation == "producer":
        document["producer_identity"] = "a" * 64
    elif mutation == "extra":
        document["trusted"] = True
    else:
        document.pop("execution")
    path = tmp_path / "archived.json"
    path.write_text(json.dumps(document))
    observed = consume_receipt(path, nonce=nonce, producer=producer, raw=raw, case_id=case.case_id)
    assert type(observed) is bytes and observed == raw


def test_raw_json_cannot_construct_a_verified_payload():
    with pytest.raises(TypeError):
        VerifiedPayload(b'{"assurance":"proof-backed"}')
