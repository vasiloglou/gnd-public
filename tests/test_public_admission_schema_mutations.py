import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from gnd.report import load_report_schema

FIXTURE = Path(__file__).parent / "fixtures/v70-phase3"

def test_v10_schema_accepts_exact_example_and_rejects_mutations() -> None:
    validator = Draft202012Validator(load_report_schema())
    good = json.loads((FIXTURE / "wire-v10-example.json").read_text())
    assert not list(validator.iter_errors(good))
    missing = copy.deepcopy(good)
    missing.pop("admission")
    assert list(validator.iter_errors(missing))
    wrong_ref = copy.deepcopy(good)
    wrong_ref["admission"]["admitted"][0]["fact_ref"]["index"] = "zero"
    assert list(validator.iter_errors(wrong_ref))
    unknown = copy.deepcopy(good)
    unknown["admission"]["surprise"] = []
    assert list(validator.iter_errors(unknown))
