"""Runtime-only exact consumed Phase1 helpers; no original test disposition."""
from __future__ import annotations

from typing import Any

from test_public_slice_runtime import CASES, CORPUS
from test_public_slice_runtime import EXPECTED as SLICE_EXPECTED

from gnd.checker import band, check
from gnd.model import load_model
from gnd.population import load_population
from gnd.report import build_check_payload

EXPECTED=SLICE_EXPECTED["cases"]
CASE_BY_ID={row["id"]:row for row in CASES["cases"]}

IN_SCOPE_IDS = tuple(
    case_id for case_id in sorted(EXPECTED) if EXPECTED[case_id]["whole_result_in_scope"]
)

DIGEST = "sha256:" + "0" * 64

def _load(case_id: str):
    row = CASE_BY_ID[case_id]
    model = load_model(CORPUS / row["model"])
    return model, load_population(CORPUS / row["population"], model=model)

def _public(case_id: str) -> dict[str, Any]:
    model, population = _load(case_id)
    report = check(model, population)
    exit_code = band(report)
    return build_check_payload(
        exit_code,
        str(CORPUS / CASE_BY_ID[case_id]["model"]),
        str(CORPUS / CASE_BY_ID[case_id]["population"]),
        schema_version=5,
        model_digest=DIGEST,
        report=report,
    )
