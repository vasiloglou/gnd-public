

from __future__ import annotations

import subprocess
import sys

from support.v62_phase1_corpus import ANSWERS, FIXTURE


def test_trace_case_v06() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "gnd",
            "validate",
            str(FIXTURE / "models/static.orm.yaml"),
            "--trace",
        ],
        capture_output=True,
        check=False,
        text=True,
    )
    assert completed.returncode == ANSWERS["V06"]["exit"]
    assert ANSWERS["V06"]["trace_heading"] in completed.stdout
    assert "eligible: static (dependencies: blocked, evidence)" in completed.stdout
    assert "final_eligible: static (dependencies: blocked, evidence)" in completed.stdout
    assert "SECRET-ITEM-314159" not in completed.stdout
