"""Generated report authority controls; expected answers do not drive materialization."""

from __future__ import annotations

import atexit
import copy
import gzip
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from gnd import api
from gnd.admission_validation import (
    AdmissionValidationError,
    validate_admission_payload,
    validate_reference_transport,
)
from gnd.artifacts import canonical_json_bytes, sha256_hex
from gnd.exp.session_contract import read_session_contract
from gnd.exp.session_eval import (
    AttemptEvaluation,
    VerifierPayloadError,
    case_decision,
    ranking_observations,
)
from gnd.exp.session_v7 import _evaluate
from gnd.model import load_model
from gnd.population import load_population
from gnd.references import bind_references


def _materialize_public_fixture():
    packed = (Path(__file__).parent / "fixtures/public-v72-status/closure.json.gz").read_bytes()
    assert len(packed) <= 8192
    assert hashlib.sha256(packed).hexdigest() == "87ac9325be0f9103469d19ea93a401e8305543d4879f14a4120521acc70b82cd"
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(65537)
    assert len(raw) <= 65536
    assert hashlib.sha256(raw).hexdigest() == "712de4b83f93eed036d25c18b32ef948d41abd12b3b7e0b21f526de6782f76e3"
    documents = json.loads(raw)
    assert set(documents) == {'tests/fixtures/v71/phase2/release/model.orm.yaml', 'tests/fixtures/v71/phase2/dispatch/model.orm.yaml', 'tests/fixtures/v71/phase2/dispatch/candidate.pop.json', 'tests/fixtures/v72/phase2/inputs.json', 'tests/fixtures/v72/phase2/answers.json', 'tests/fixtures/v71/phase2/release/candidate.pop.json', 'tests/fixtures/v71/phase2/release/references/catalog.pop.json', 'tests/fixtures/v71/phase2/dispatch/references/catalog.pop.json'}
    temporary = tempfile.TemporaryDirectory(prefix="gnd-public-v72-status-")
    root = Path(temporary.name).resolve()
    for name, text in documents.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return temporary, root

_TEMPORARY, ROOT = _materialize_public_fixture()
atexit.register(_TEMPORARY.cleanup)

CORPUS = ROOT / "tests/fixtures/v72/phase2"
INPUT_BYTES = (CORPUS / "inputs.json").read_bytes()
ANSWER_BYTES = (CORPUS / "answers.json").read_bytes()
assert sha256_hex(INPUT_BYTES) == "33ed815fdefa3144107730669239d1f882de2a14b2dee6a41b824d43454415f6"
assert (
    sha256_hex(ANSWER_BYTES) == "e889a42a92676a61aeeb36260a44f0a29a42ec786c9e1a9a666adefaa4770bff"
)
CASES = json.loads(INPUT_BYTES)["cases"]
ANSWERS = {row["id"]: row["expected"] for row in json.loads(ANSWER_BYTES)["cases"]}
ALTERED = {"command": "validate", "outcome": "violated", "exit_code": 1}

def write(path, doc):
    path.write_bytes(canonical_json_bytes(doc))

def materialize(row, root, monkeypatch):
    root = root.resolve()
    shutil.copytree(ROOT / f"tests/fixtures/v71/phase2/{row['domain']}", root, dirs_exist_ok=True)
    doc = YAML(typ="safe").load((root / "model.orm.yaml").read_text())
    pop = json.loads((root / "candidate.pop.json").read_text())
    if row["version"] == 14:
        doc["object_types"].append(
            {"id": "interval", "name": "Interval", "kind": "value", "primitive": "Duration"}
        )
        doc["fact_types"].append(
            {
                "id": "interval_fits",
                "reading": "{Interval} fits {Interval}",
                "roles": [{"role_name": n, "object_type": "interval"} for n in ("a", "b")],
                "constraints": [
                    {
                        "type": "value-comparison",
                        "role_a": "a",
                        "role_b": "b",
                        "operator": "<=",
                        "source": "user-supplied",
                        "status": "confirmed",
                        "modality": "alethic",
                        "provenance": {"user_quote": "First duration cannot exceed second."},
                    }
                ],
            }
        )
        pop["population"]["covers"].append("interval_fits")
        pop["facts"]["interval_fits"] = [{"a": 1, "b": 2}]
    if row["variant"].startswith("failure"):
        ft, role = (
            ("dispatch_subject_product", "product")
            if row["domain"] == "dispatch"
            else ("release_subject_environment", "environment")
        )
        pop["facts"][ft][0][role] = "NOT-IN-CATALOG"
    write(root / "model.orm.yaml", doc)
    write(root / "candidate.pop.json", pop)
    model_raw = (root / "model.orm.yaml").read_bytes()
    contract = {
        "schema_version": 7,
        "experiment_id": "EXP-72-status",
        "max_attempts": 1,
        "wall_seconds": 60,
        "adapter": {"policy_id": "local-command", "parameters": {}},
        "ranking": [{"metric": "candidate_admitted_unique", "direction": "max"}],
        "cases": [
            {
                "case_id": "status",
                "role": "required",
                "inputs": [],
                "reference_root": ".",
                "acceptance": {
                    "mode": "constraint-satisfaction",
                    "coverage": [
                        {"fact_type": ft, "min_facts": 1} for ft in pop["population"]["covers"]
                    ],
                },
                "verify": {
                    "command": "check",
                    "model": {
                        "path": "model.orm.yaml",
                        "sha256": sha256_hex(model_raw),
                        "size_bytes": len(model_raw),
                        "media_type": "application/yaml",
                        "encoding": "utf-8",
                    },
                    "subject": "candidate.pop.json",
                },
            }
        ],
    }
    write(root / "contract.json", contract)
    selected = read_session_contract(
        root / "contract.json", experiment_root=root, experiment_id="EXP-72-status"
    )
    snapshot = root / "snapshot"
    snapshot.mkdir()
    shutil.copy(root / "candidate.pop.json", snapshot / "candidate.pop.json")
    monkeypatch.chdir(root)
    payload = (
        api.diff("model.orm.yaml", "model.orm.yaml")
        if row["variant"] == "diff"
        else api.check("model.orm.yaml", "candidate.pop.json", admission=True)
    )
    assert payload["schema_version"] == row["version"]
    if row["variant"] != "diff":
        for field in ALTERED:
            assert payload[field] == payload["report"][field]
        failed = row["variant"].startswith("failure")
        assert (payload["outcome"] == "accepted") is not failed
        assert (payload["exit_code"] == 0) is not failed
    model = load_model(root / "model.orm.yaml")
    refs = bind_references(model, root=root)
    model._references = refs
    population = load_population(root / "candidate.pop.json", model=model)
    return root, snapshot, selected, payload, model, refs, population

def mutate(row, payload):
    dirty = copy.deepcopy(payload)
    variant = row["variant"]
    field = row.get("field")
    if variant in {"outer", "both"}:
        dirty[field] = ALTERED[field]
    if variant in {"inner", "both"}:
        dirty["report"][field] = ALTERED[field]
    if variant in {"structure", "binding", "correlation", "failure-outer"}:
        dirty["command"] = "validate"
    if variant == "structure":
        del dirty["exit_code"]
    if variant == "binding":
        dirty["model_digest"] = "sha256:" + "0" * 64
    if variant == "unknown":
        dirty["schema_version"] = 99
    return dirty

def session(selected, payload, process_exit, root, snapshot):
    result = _evaluate(
        selected.cases[0],
        canonical_json_bytes(payload),
        process_exit,
        snapshot,
        root,
        "a" * 64,
        "b" * 64,
    )
    attempt = AttemptEvaluation(
        attempt_index=1, candidate_sha256="a" * 64, contract_sha256="b" * 64, results=(result,)
    )
    return result, case_decision(selected.cases[0], result), ranking_observations(selected, attempt)

@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_status_authority(case, tmp_path, monkeypatch):
    root, snapshot, selected, clean, model, refs, population = materialize(
        case, tmp_path, monkeypatch
    )
    dirty = mutate(case, clean)
    expected = ANSWERS[case["id"]]
    consumer = case["consumer"]
    if consumer == "transport":
        call = lambda: validate_reference_transport(
            dirty, model=model, references=refs, expected_version=case["version"]
        )
        if expected in {"accepted", "valid-failure"}:
            assert call() is None
        else:
            with pytest.raises(AdmissionValidationError, match=expected):
                call()
    elif consumer == "admission":
        if expected == "correlation":
            with pytest.raises(AdmissionValidationError, match="correlation"):
                validate_admission_payload(
                    dirty, model=model, candidate=population, references=refs
                )
        else:
            metrics = validate_admission_payload(
                dirty, model=model, candidate=population, references=refs
            )
            if expected == "accepted":
                assert metrics["candidate_blocked_occurrences"] == 0
                assert metrics["candidate_admitted_unique"] == (3 if case["version"] == 14 else 2)
            else:
                assert metrics["candidate_blocked_occurrences"] > 0
    else:
        process_exit = 1 if case["variant"] == "process" else clean["exit_code"]
        if expected == "correlation":
            # Prove refusal before either acceptance or ranking sees an evaluation.
            with pytest.raises(AdmissionValidationError, match="correlation"):
                session(selected, dirty, process_exit, root, snapshot)
        elif expected == "structural":
            with pytest.raises(AdmissionValidationError, match="structural"):
                session(selected, dirty, process_exit, root, snapshot)
        elif expected == "inner-refusal":
            reason = (
                "outcome 'violated' does not match exit 0"
                if case.get("field") == "outcome"
                else "process exit 0 does not match payload exit 1"
                if case.get("field") == "exit_code"
                else "process exit 1 does not match payload exit 0"
            )
            with pytest.raises(VerifierPayloadError, match=reason):
                session(selected, dirty, process_exit, root, snapshot)
        else:
            result, decision, rank = session(selected, dirty, process_exit, root, snapshot)
            assert result.payload_valid
            assert not result.validation_errors
            assert decision.accepted is (expected == "accepted")
            assert rank[0]["available"]
            if expected == "accepted":
                assert rank[0]["value"] == (3 if case["version"] == 14 else 2)

@pytest.mark.parametrize("domain", ["dispatch", "release"])
@pytest.mark.parametrize("temporal", [False, True], ids=["snapshot", "temporal"])
@pytest.mark.parametrize("command", ["validate", "check"])
def test_generated_non_admission_compatibility(domain, temporal, command, tmp_path, monkeypatch):
    row = {"domain": domain, "version": 14 if temporal else 12, "variant": "clean"}
    _root, _snapshot, _selected, _clean, model, refs, _population = materialize(
        row, tmp_path, monkeypatch
    )
    payload = (
        api.validate("model.orm.yaml")
        if command == "validate"
        else api.check("model.orm.yaml", "candidate.pop.json")
    )
    assert payload["outcome"] == "accepted"
    assert payload["exit_code"] == 0
    inner = payload["report"]
    assert inner.get("admission") is None
    assert all(payload[field] == inner[field] for field in ALTERED)
    assert payload["schema_version"] == (14 if inner["schema_version"] == 13 else 12)
    validate_reference_transport(
        payload, model=model, references=refs, expected_version=payload["schema_version"]
    )

@pytest.mark.parametrize("domain", ["dispatch", "release"])
@pytest.mark.parametrize("temporal", [False, True], ids=["snapshot", "temporal"])
def test_actual_process_failure_preserves_status(domain, temporal, tmp_path, monkeypatch):
    row = {"domain": domain, "version": 14 if temporal else 12, "variant": "failure"}
    root, snapshot, selected, expected, model, refs, _population = materialize(
        row, tmp_path, monkeypatch
    )
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "gnd",
            "check",
            "model.orm.yaml",
            "candidate.pop.json",
            "--admission",
            "--format",
            "json",
        ],
        cwd=root,
        capture_output=True,
        timeout=20,
        check=False,
    )
    payload = json.loads(completed.stdout)
    assert completed.returncode == payload["exit_code"] == expected["exit_code"] != 0
    assert payload["outcome"] == expected["outcome"] != "accepted"
    assert all(payload[field] == payload["report"][field] for field in ALTERED)
    validate_reference_transport(
        payload, model=model, references=refs, expected_version=row["version"]
    )
    result, decision, _rank = session(selected, payload, completed.returncode, root, snapshot)
    assert result.payload_valid
    assert not result.validation_errors
    assert not decision.accepted

@pytest.mark.parametrize(
    "suffix", ["both-outcome-session", "both-exit_code-session", "process-mismatch"]
)
@pytest.mark.parametrize("fault", ["wrong-owner", "wrong-reason"])
def test_review_inner_refusal_boundary(suffix, fault, tmp_path, monkeypatch):
    case = next(row for row in CASES if row["id"] == "dispatch-12-" + suffix)

    def unrelated(*args, **kwargs):
        if fault == "wrong-owner":
            raise AdmissionValidationError("seeded unrelated admission error")
        raise VerifierPayloadError(["seeded unrelated verifier error"])

    monkeypatch.setattr(sys.modules[__name__], "_evaluate", unrelated)
    error = AdmissionValidationError if fault == "wrong-owner" else AssertionError
    with pytest.raises(error):
        test_status_authority(case, tmp_path, monkeypatch)
