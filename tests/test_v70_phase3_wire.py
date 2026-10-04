import json
from pathlib import Path

import pytest
from support.cli_runner import run_gnd_text
from test_v70_phase3_opaque import run_case

FIXTURE = Path(__file__).parent / "fixtures/v70-phase3"

@pytest.mark.parametrize(
    "case_id",
    ["W01-redacted-legacy-version", "W02-redacted-admission-version",
     "W03-admission-population-refusal", "W04-admission-model-refusal"],
)
def test_requested_and_legacy_report_versions(case_id: str, tmp_path: Path) -> None:
    run_case(case_id, tmp_path)

def test_admission_flag_refuses_batch_arm_without_report() -> None:
    result = run_gnd_text(
        "check", str(FIXTURE / "model.orm.yaml"),
        "--populations", str(FIXTURE), "--admission", "--format", "json",
    )
    assert result.returncode == 64
    assert result.stdout == ""

def test_admission_flag_accepts_snapshot_arm() -> None:
    result = run_gnd_text(
        "check", str(FIXTURE / "model.orm.yaml"),
        str(FIXTURE / "population.pop.json"), "--admission", "--format", "json",
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["schema_version"] == 10
