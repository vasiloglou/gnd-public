from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from support.v70_phase4 import _unknown_positive, _write

from gnd import api
from gnd.report import load_report_schema


def test_unresolved_witness_obeys_redaction_and_schema(tmp_path: Path) -> None:
    model, population = _unknown_positive()
    model["fact_types"][1]["roles"][1]["redact"] = True
    population["facts"]["inferred"].append({"record": "R1", "item": "SECRET-314159"})
    paths = _write(tmp_path, model, population)
    redacted = api.check(*paths, admission=True)
    assert redacted["exit_code"] == 4
    assert "SECRET-314159" not in json.dumps(redacted)
    assert redacted["derivations"][0]["findings"][0]["witness"] == {
        "redacted": True, "roles": ["inferred.item"]
    }
    assert not list(Draft202012Validator(load_report_schema()).iter_errors(redacted))
    open_payload = api.check(*paths, admission=True, unredacted=True)
    assert open_payload["derivations"][0]["findings"][0]["witness"]["item"] == "SECRET-314159"

def test_anchored_admission_uses_partial_derivation_path(tmp_path: Path) -> None:
    model, population = _unknown_positive()
    model["fact_types"][1]["constraints"] = [{
        "type": "anchored", "role": "record", "modality": "alethic",
        "source": "explicit", "status": "confirmed",
        "provenance": {"user_quote": "R1"},
    }]
    population["facts"]["inferred"].append({"record": "R1", "item": "B"})
    paths = _write(tmp_path, model, population)
    payload = api.check(*paths, admission=True)
    assert payload["exit_code"] == 4
    assert payload["derivations"][0]["reason_code"] == "derived-unknown"
    assert not list(Draft202012Validator(load_report_schema()).iter_errors(payload))
