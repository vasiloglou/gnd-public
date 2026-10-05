

from __future__ import annotations

import json
import subprocess
import sys

from support.v62_phase1_corpus import ANSWERS, FIXTURE, population, steps

from gnd.api import transition


def _plan() -> dict[str, object]:
    return transition(
        FIXTURE / "models/static.orm.yaml",
        population("pre_clean"),
        steps(),
        post=None,
        unredacted=True,
    )


def test_plan_case_l01_asserted_only() -> None:
    payload = _plan()
    assert payload["exit_code"] == ANSWERS["L01"]["exit"]
    facts = payload["transition"]["computed_post"]["facts"]
    assert "final_eligible" not in facts


def test_plan_case_l02_preserves_only_authored_semiderived_rows() -> None:
    payload = _plan()
    rows = payload["transition"]["computed_post"]["facts"]["eligible"]
    assert {row["item"] for row in rows} == {"SECRET-ITEM-314159", "supplied-poison"}


def test_plan_case_l04_api_cli_parity() -> None:
    api_payload = _plan()
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "gnd",
            "check",
            str(FIXTURE / "models/static.orm.yaml"),
            "--pre",
            str(population("pre_clean")),
            "--steps",
            str(steps()),
            "--format",
            "json",
            "--unredacted",
        ],
        capture_output=True,
        check=False,
        text=True,
    )
    assert completed.returncode == ANSWERS["L04"]["exit"]
    cli_payload = json.loads(completed.stdout)
    assert cli_payload["transition"]["computed_post"] == api_payload["transition"]["computed_post"]


def test_plan_case_l05_declared_post_stays_full_audit() -> None:
    payload = transition(
        FIXTURE / "models/static.orm.yaml",
        population("pre_clean"),
        steps(),
        population("post_exact"),
    )
    assert payload["exit_code"] == ANSWERS["L05"]["exit"]
    assert payload["transition"]["computed_post"] is None
