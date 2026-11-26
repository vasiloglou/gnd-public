"""Successor contracts for refactoring follow-ups #299, #303 and #304."""
import hashlib
import json

import pytest
from pydantic import ValidationError
from test_rf1_session_pins import BUILDERS, _fresh, build_v6, owner, run_main

from gnd.assurance.core import _sorted_set
from gnd.exp.session_eval import AttemptFeedback
from gnd.exp.session_judgments import entry
from gnd.exp.session_records import AttemptRecord, SessionResult
from gnd.exp.session_replay import _entry
from gnd.fidelity.match import _rate as fidelity_rate
from gnd.measure.score import _rate as measure_rate
from gnd.proof_bridge import _canonical


@pytest.mark.parametrize("rate", [fidelity_rate, measure_rate])
def test_independent_rate_contract(rate):
    assert rate(1, 0) is None
    assert rate(3, 2) == 1.5


@pytest.mark.parametrize("sorter", [_sorted_set, _canonical])
def test_independent_identity_order(sorter):
    assert sorter(("z", "a", "z")) == ("a", "z")
    with pytest.raises(TypeError):
        sorter(([],))


@pytest.mark.parametrize("builder", [_entry, entry])
def test_evidence_entry_wrappers(builder):
    assert builder("x", b"a") == {
        "path": "x", "size_bytes": 1, "sha256": hashlib.sha256(b"a").hexdigest()
    }
    with pytest.raises(TypeError):
        builder("x", None)


@pytest.mark.parametrize("reader", [AttemptFeedback, AttemptRecord, SessionResult])
def test_versioned_json_entries(reader):
    with pytest.raises(ValidationError):
        reader.model_validate_json(b'{"schema_version":0}')

    class Probe(reader):
        @classmethod
        def model_validate(cls, obj, **kwargs):
            return obj, kwargs

    assert Probe.model_validate_json(bytearray(b'{"x":1}'), strict=True) == ({"x": 1}, {"strict": True})


def tree(run):
    return {p.relative_to(run): p.read_bytes() if p.is_file() else None for p in run.rglob("*")}


@pytest.mark.parametrize("version", [2, 3, 7, 8])
def test_existing_terminal_evidence(version, tmp_path, monkeypatch):
    built, run, _ = _fresh(version, tmp_path, monkeypatch)
    monkeypatch.setattr(owner("_next_session_run_root"), "_next_session_run_root", lambda root: run)
    result_path = run / "result.json"
    for present in (True, False):
        if not present:
            result_path.unlink()
        before = tree(built.root)
        result = run_main(built.argv, cwd=tmp_path)
        assert result.returncode == 74, result.stdout
        assert tree(built.root) == before


@pytest.mark.parametrize("version", [6, 7, 8])
def test_portable_session_prompt_identity(version, tmp_path, monkeypatch):
    receipts = []
    for label, padding in (("one", ""), ("two", ""), ("three", " ")):
        directory = tmp_path / label
        directory.mkdir()
        built = BUILDERS[version](directory, monkeypatch)
        contract = built.root / "session.contract.json"
        document = json.loads(contract.read_bytes())
        document["prompt_format"] = "portable-v1"
        contract.write_text(json.dumps(document, sort_keys=True) + padding)
        result = run_main(built.argv, cwd=directory)
        assert result.returncode in (0, 15), result.stdout
        launch = json.loads((built.root / "runs/run-0001/launches/0001.json").read_bytes())
        digest = hashlib.sha256(contract.read_bytes()).hexdigest()
        assert launch["contract_sha256"] == digest
        prompt = (
            "Modify only the current candidate directory so it satisfies every "
            f"required case in the caller-validated contract at ../session.contract.json (sha256:{digest})."
        )
        expected = hashlib.sha256(prompt.encode()).hexdigest()
        assert launch["base_prompt_sha256"] == expected
        receipts.append((expected, launch["controller_prompt_sha256"], launch["effective_prompt_sha256"]))
    assert receipts[0] == receipts[1]
    assert all(a != b for a, b in zip(receipts[0], receipts[2], strict=True))


@pytest.mark.parametrize("version", range(1, 9))
def test_portable_selector_wire_versions(version, tmp_path, monkeypatch):
    from gnd.exp.session_contract import DataDrivenContract

    built = BUILDERS[version](tmp_path, monkeypatch)
    path = built.root / "session.contract.json"
    document = json.loads(path.read_bytes())
    assert "prompt_format" not in DataDrivenContract.model_validate(document).model_dump()
    document["prompt_format"] = "portable-v1"
    if version < 6:
        with pytest.raises(ValidationError):
            DataDrivenContract.model_validate(document)
    else:
        contract = DataDrivenContract.model_validate(document)
        assert contract.model_dump()["prompt_format"] == "portable-v1"
        document["prompt_format"] = "unknown"
        with pytest.raises(ValidationError):
            DataDrivenContract.model_validate(document)


def test_contract_digest_survives_path_replacement(tmp_path, monkeypatch):
    from gnd.exp import session_contract

    built = build_v6(tmp_path, monkeypatch)
    path = built.root / "session.contract.json"
    original = path.read_bytes()
    verify = session_contract._verify_bound_file

    def replace_after_read(*args, **kwargs):
        path.write_bytes(b"{}")
        return verify(*args, **kwargs)

    monkeypatch.setattr(session_contract, "_verify_bound_file", replace_after_read)
    contract, digest = session_contract.read_session_contract_with_digest(
        path, experiment_root=built.root, experiment_id=built.experiment_id
    )
    assert contract.schema_version == 6 and path.read_bytes() == b"{}"
    assert digest == hashlib.sha256(original).hexdigest()


def test_portable_v6_terminal_evidence(tmp_path, monkeypatch):
    built = BUILDERS[6](tmp_path, monkeypatch)
    path = built.root / "session.contract.json"
    contract = json.loads(path.read_bytes())
    contract["prompt_format"] = "portable-v1"
    path.write_text(json.dumps(contract))
    assert run_main(built.argv, cwd=tmp_path).returncode in (0, 15)
    run = built.root / "runs/run-0001"
    monkeypatch.setattr(owner("_next_session_run_root"), "_next_session_run_root", lambda root: run)
    before = tree(built.root)
    assert run_main(built.argv, cwd=tmp_path).returncode == 74
    assert tree(built.root) == before
