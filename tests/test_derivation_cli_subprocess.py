from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CASES = REPO_ROOT / 'tests' / 'fixtures' / 'derivation-evaluation' / 'cases'
COUNTS = re.compile('pass=(\\d+) fail=(\\d+) warning=(\\d+) unchecked=(\\d+) vacuous=(\\d+)')

def _run(case_id: str, *extra: str, seed: str='0') -> subprocess.CompletedProcess[bytes]:
    root = CASES / case_id
    environment = os.environ.copy()
    environment['PYTHONHASHSEED'] = seed
    return subprocess.run([sys.executable, '-m', 'gnd', 'check', str(root / 'model.orm.yaml'), str(root / 'population.yaml'), *extra], cwd=REPO_ROOT, env=environment, capture_output=True, check=False)

def test_report_bytes_across_hash_seeds() -> None:
    random_seed = str(int.from_bytes(os.urandom(4), 'big'))
    outputs = [_run('obligation-derived-both-differences', seed=seed) for seed in ('0', '1', '42', random_seed)]
    assert {result.returncode for result in outputs} == {1}
    assert len({result.stdout for result in outputs}) == 1
    assert len({result.stderr for result in outputs}) == 1
    assert b'derived-extension-incomplete' in outputs[0].stdout
    assert b'derived-extension-unsound' in outputs[0].stdout

def test_text_json_parity() -> None:
    text = _run('wire-text-json-parity')
    machine = _run('wire-text-json-parity', '--format', 'json')
    payload = json.loads(machine.stdout)
    match = COUNTS.search(text.stdout.decode())
    assert match is not None
    assert tuple(map(int, match.groups())) == tuple(payload['counts'][key] for key in ('pass', 'fail', 'warning', 'unchecked', 'vacuous'))
    assert text.returncode == machine.returncode == payload['exit_code']
    assert payload['schema_version'] == 7
    assert payload['assurance']['semantic_decision'] == 'accept'
    assert b'DERIVATIONS (alethic)' in text.stdout
