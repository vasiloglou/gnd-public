"""Exact current saved-judgment/session guards over full fixture closure."""
import json
import sys

import pytest

import tests.support
from gnd.exp.close import _declared_case_findings, _SessionRun
from gnd.exp.session_contract import read_session_contract
from gnd.exp.session_store import SessionStore
from gnd.judgments import JudgmentInputError, read_judgment_policy
from tests import test_public_v71_full_judgments as closure

bundle = closure._JUDGMENTS.bundle
encoded = closure._JUDGMENTS.encoded
session_case = closure._JUDGMENTS.session_case
write = closure._JUDGMENTS.write

@pytest.fixture(autouse=True)
def _exact_original_dependencies(monkeypatch):
    for name, module in (("v71_judgment_cases", closure._JUDGMENTS), ("v71_session_cases", closure._SESSIONS)):
        monkeypatch.setitem(sys.modules, "tests.support." + name, module)
        monkeypatch.setattr(tests.support, name, module, raising=False)

def test_floor_requires_metric_specific_semantics(tmp_path):
    b = bundle("dispatch", tmp_path)
    b["policy"]["admission"]["evidence_floor"] = {
        "metric": "verdict-probability",
        "semantics": "provider-defined",
        "minimum": 0.8,
    }
    with pytest.raises(JudgmentInputError):
        read_judgment_policy(encoded(b["policy"]))


def test_v8_closure_rebinds_judgment_sources(tmp_path):
    b = bundle("dispatch", tmp_path)
    session = session_case(
        {"domain": "dispatch", "mode": "session", "parameters": {"variant": "two-step"}}, b
    )
    run, root = session["_run"], session["_root"]
    source = next(iter(session["_attempts"][0]["judgment_evidence"].values()))["sources"][0]
    (run / "attempts/0001" / source["path"]).write_text("tampered")
    findings = _declared_case_findings(
        _SessionRun(1, run, run / "result.json", True),
        root,
        (run / "result.json").read_bytes(),
        experiment_id=root.name,
    )
    assert findings, "closure must not skip result7 judgment evidence"


def test_v8_reconstruction_checks_terminal_admission(tmp_path):
    b = bundle("dispatch", tmp_path)
    session = session_case(
        {"domain": "dispatch", "mode": "session", "parameters": {"variant": "two-step"}}, b
    )
    run, root = session["_run"], session["_root"]
    terminal = json.loads((run / "result.json").read_bytes())
    terminal["judgment_admission"] = {k: False for k in terminal["judgment_admission"]}
    write(run / "result.json", terminal)
    contract = read_session_contract(
        root / "session.contract.json", experiment_root=root, experiment_id=root.name
    )
    from gnd.exp.session_v7 import reconstruct

    with pytest.raises(ValueError, match="terminal judgment"):
        reconstruct(
            SessionStore(run, run_id=run.name, contract_id=root.name), contract, allow_terminal=True
        )


def test_source_replacement_between_stat_and_open_is_refused(tmp_path, monkeypatch):
    from gnd import artifacts
    from tests.support.v71_judgment_cases import public

    b = bundle("dispatch", tmp_path)
    original = artifacts.os.open
    events = []

    def replace_before_open(name, flags, *args, **kwargs):
        if name == "assessment.txt" and kwargs.get("dir_fd") is not None and not events:
            replacement = b["root"] / "sources/replacement.txt"
            replacement.write_text("replacement")
            replacement.replace(b["root"] / "sources/assessment.txt")
            events.append("replaced")
        return original(name, flags, *args, **kwargs)

    monkeypatch.setattr(artifacts.os, "open", replace_before_open)
    result = public(b)
    assert events == ["replaced"]
    assert result["outcome"] == 3 and result["judgment_policy"] is None


@pytest.mark.parametrize(
    "variant",
    [
        "binary-confidence",
        "verdict-null",
        "verdict-concentration",
        "choice-provider",
        "score-provider",
        "score-unordered",
    ],
)
def test_answer_kind_boundaries_are_closed(tmp_path, variant):
    from importlib.resources import files

    from jsonschema import Draft202012Validator

    from gnd.judgments import read_judgment_receipts
    from tests.support.v71_judgment_cases import attach_evidence

    b = bundle("dispatch", tmp_path)
    kind = (
        "binary-probability"
        if variant.startswith("binary")
        else "verdict-confidence"
        if variant.startswith("verdict")
        else "score"
        if variant.startswith("score")
        else "choice"
    )
    attach_evidence(b, kind)
    a = b["receipts"]["receipts"][0]["external_evidence"]["answer"]
    if variant == "binary-confidence":
        a.update(confidence=0.9, confidence_semantics="provider-defined")
    elif variant == "verdict-null":
        a.update(confidence=None, confidence_semantics=None)
    elif variant == "verdict-concentration":
        a["confidence_semantics"] = "distribution-concentration"
    elif variant == "score-unordered":
        a["legend"].reverse()
    else:
        a["confidence_semantics"] = "provider-defined"
    raw = encoded(b["receipts"])
    with pytest.raises(JudgmentInputError):
        read_judgment_receipts(raw)
    if variant != "score-unordered":
        schema = json.loads((files("gnd") / "judgment.schema.json").read_text())
        assert list(Draft202012Validator(schema).iter_errors(json.loads(raw)))


