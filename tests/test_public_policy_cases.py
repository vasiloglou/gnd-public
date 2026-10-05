from __future__ import annotations

import gzip
import json
from pathlib import Path

import pytest

from gnd.assurance import _assurance_policy, assurance_prerequisites
from gnd.semantic_spec import decision_of

DATA = json.loads(gzip.decompress((Path(__file__).parent / "fixtures/public-policy-cases.json.gz").read_bytes()))
ROWS = DATA["rows"]
ANSWERS = DATA["cases"]

@pytest.mark.parametrize("row", ROWS, ids=lambda row: row["case_id"])
def test_approved_policy_case(row):
    recipe = row["recipe"]
    required = frozenset(assurance_prerequisites(row["surface"], row["consumer"]))
    assert required == set(recipe["required_infrastructure"])
    applicable, covered = frozenset(recipe["applicable"]), frozenset(recipe["covered"])
    level = _assurance_policy(
        applicable,
        covered,
        required=required,
        proved_infrastructure=required - set(recipe["missing_infrastructure"]),
        guards_valid=recipe["guard_failure"] is None,
    )
    actual = {
        "band": recipe["band"],
        "decision": decision_of(recipe["band"]) or None,
        "level": level,
        "uncovered": sorted(applicable - covered),
    }
    assert actual == ANSWERS[row["case_id"]]


