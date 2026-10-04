from __future__ import annotations

import json
import subprocess
import sys

from support.v62_phase2_corpus import ANSWERS, FIXTURE, population, steps

from gnd.api import transition

MODEL = FIXTURE / 'models/dynamic.orm.yaml'
COMPUTED_ONLY = {'ready', 'ticket_score'}

def _plan() -> dict:
    return transition(MODEL, population('pre_open'), steps(), post=None, unredacted=True)

def test_m03_plan_is_asserted_only_but_keeps_consequences() -> None:
    payload = _plan()
    assert payload['exit_code'] == ANSWERS['M03']['exit']
    facts = payload['transition']['computed_post']['facts']
    assert not COMPUTED_ONLY.intersection(facts)
    assert facts['resolvable'] == [{'ticket': 'authored-surplus'}]
    assert payload['transition']['steps'][0]['derived_changes']

def test_g02_authored_semiderived_surplus_survives_durably() -> None:
    payload = _plan()
    rows = payload['transition']['computed_post']['facts']['resolvable']
    assert rows == [{'ticket': 'authored-surplus'}]

def test_plan_api_and_cli_json_are_equal() -> None:
    api_payload = _plan()
    completed = subprocess.run([sys.executable, '-m', 'gnd', 'check', str(MODEL), '--pre', str(population('pre_open')), '--steps', str(steps()), '--format', 'json', '--unredacted'], capture_output=True, check=False, text=True)
    assert completed.returncode == 0, completed.stderr
    cli_payload = json.loads(completed.stdout)
    assert cli_payload['transition'] == api_payload['transition']
