from pathlib import Path

import pytest
from test_v70_phase3_opaque import CASES, run_case


@pytest.mark.parametrize("case_id", [case_id for case_id in CASES if case_id.startswith("A")])
def test_exact_admission_partition(case_id: str, tmp_path: Path) -> None:
    run_case(case_id, tmp_path)
