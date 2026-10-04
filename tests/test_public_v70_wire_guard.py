"""Original unresolved wire order/reason/shape and legacy schema rejection guard."""
from __future__ import annotations

import copy
from pathlib import Path

from jsonschema import Draft202012Validator
from test_v70_phase4_runtime import _stage

from gnd import api
from gnd.report import load_report_schema


def test_v10_unresolved_wire_is_closed_and_legacy_rejects_it(tmp_path: Path) -> None:
    model, population, _ = _stage("P04-three-findings", tmp_path)
    payload = api.check(model, population, admission=True)
    validator = Draft202012Validator(load_report_schema())
    assert not list(validator.iter_errors(payload))
    wrong_order = copy.deepcopy(payload)
    wrong_order["derivations"][0]["findings"].reverse()
    assert list(validator.iter_errors(wrong_order))
    wrong_reason = copy.deepcopy(payload)
    wrong_reason["derivations"][0]["reason_code"] = "derived-unknown"
    assert list(validator.iter_errors(wrong_reason))
    extra = copy.deepcopy(payload)
    extra["derivations"][0]["findings"][0]["surprise"] = True
    assert list(validator.iter_errors(extra))
    legacy = copy.deepcopy(payload)
    legacy["schema_version"] = 7
    legacy.pop("admission")
    assert list(validator.iter_errors(legacy))
