from __future__ import annotations

import copy
import importlib
import json
import time
from pathlib import Path

import pytest
from test_public_transition_walks import CORPUS

from gnd.model import MAX_MODEL_BYTES, load_model
from gnd.population import MAX_POPULATION_BYTES, load_population
from gnd.transition import MAX_STEPS_BYTES

ROOT = Path(__file__).resolve().parents[1]
TRANSITION_MODEL = str(CORPUS / "v2_expense.orm.yaml")
WALKS = str(CORPUS / "walks")


def _api():
    try:
        return importlib.import_module('gnd.api')
    except ModuleNotFoundError as error:
        pytest.fail('expected corpus-first RED: gnd.api does not exist yet; approve tests/fixtures/v61-phase2 before production implementation', pytrace=False)
        raise AssertionError from error

def _walk(name: str) -> tuple[str, str, str]:
    root = f'{WALKS}/{name}'
    return (f'{root}/pre.pop.yaml', f'{root}/steps.json', f'{root}/post.pop.yaml')

@pytest.mark.parametrize(('walk', 'band'), [('clean-walk', 0), ('broken-pre', 1), ('open-new-chain', 2), ('empty-steps', 3), ('tag-unchecked', 4)])
def test_transition_paths_reach_every_existing_band(walk: str, band: int) -> None:
    pre, steps, post = _walk(walk)
    payload = _api().transition(TRANSITION_MODEL, pre, steps, post)
    assert payload['exit_code'] == band

def test_transition_reuses_one_model_for_path_and_loaded_inputs() -> None:
    api = _api()
    model = load_model(TRANSITION_MODEL)
    pre_path, steps_path, post_path = _walk('clean-walk')
    by_path = api.transition(model, pre_path, steps_path, post_path)
    pre = load_population(pre_path, model=model)
    post = load_population(post_path, model=model)
    steps = json.loads((ROOT / steps_path).read_text(encoding='utf-8'))
    by_object = api.transition(model, pre, steps, post)
    assert by_path['exit_code'] == by_object['exit_code'] == 0
    assert by_object['model'] is None

def test_transition_path_model_plus_loaded_population_fails_closed() -> None:
    api = _api()
    model = load_model(TRANSITION_MODEL)
    pre_path, steps_path, post_path = _walk('clean-walk')
    post = load_population(post_path, model=model)
    payload = api.transition(TRANSITION_MODEL, pre_path, steps_path, post)
    assert payload['exit_code'] == 70
    assert payload['error']['type'] == 'UnvalidatedPopulationError'

def test_loaded_pre_digest_omission_accepts_and_claim_refuses() -> None:
    api = _api()
    model = load_model(TRANSITION_MODEL)
    pre_path, steps_path, post_path = _walk('clean-walk')
    pre = load_population(pre_path, model=model)
    post = load_population(post_path, model=model)
    steps = json.loads((ROOT / steps_path).read_text(encoding='utf-8'))
    accepted = api.transition(model, pre, steps, post)
    assert accepted['exit_code'] == 0
    claimed = copy.deepcopy(steps)
    claimed['pre_digest'] = 'sha256:' + '0' * 64
    refused = api.transition(model, pre, claimed, post)
    assert refused['exit_code'] == 3
    assert any(issue['rule_id'] == 'transition:pre-digest-unverifiable' for issue in refused['issues'])

def test_transition_internal_fault_returns_70(monkeypatch: pytest.MonkeyPatch) -> None:
    api = _api()
    transition_module = importlib.import_module('gnd.transition')
    monkeypatch.setattr(transition_module, 'evaluate', lambda *_: (_ for _ in ()).throw(RuntimeError('pin')))
    pre, steps, post = _walk('clean-walk')
    payload = api.transition(TRANSITION_MODEL, pre, steps, post)
    assert payload['exit_code'] == 70
    assert payload['error']['type'] == 'RuntimeError'

@pytest.mark.parametrize('kind', ['malformed', 'non-json-number', 'deep', 'over-cap'])
def test_hostile_steps_paths_return_reports_without_tracebacks(tmp_path: Path, kind: str) -> None:
    _api_module = _api()
    path = tmp_path / 'steps.json'
    if kind == 'malformed':
        path.write_text('{', encoding='utf-8')
    elif kind == 'non-json-number':
        path.write_text('{"steps_schema":1,"steps":[{"value":NaN}]}', encoding='utf-8')
    elif kind == 'deep':
        path.write_text('[' * 1200 + ']' * 1200, encoding='utf-8')
    else:
        path.write_bytes(b'x' * (MAX_STEPS_BYTES + 1))
    pre, _, post = _walk('clean-walk')
    payload = _api_module.transition(TRANSITION_MODEL, pre, path, post)
    assert payload['exit_code'] == 3

def test_deep_loaded_steps_return_a_report_without_recursion_error() -> None:
    document: dict[str, object] = {}
    cursor = document
    for _ in range(2000):
        nested: dict[str, object] = {}
        cursor['x'] = nested
        cursor = nested
    pre, _, post = _walk('clean-walk')
    payload = _api().transition(TRANSITION_MODEL, pre, document, post)
    assert payload['exit_code'] == 3
    assert payload['issues'][0]['rule_id'] == 'transition:steps-shape'


MODEL = "tests/fixtures/v61-phase1/batch/model.orm.yaml"
POPULATIONS = "tests/fixtures/v61-phase1/batch/populations"
CASES = {'hostile_families': [{'ids': 'H-01-H-03', 'kind': 'model', 'controls': ['malformed', 'alias', 'over-cap']}, {'ids': 'H-04-H-08', 'kind': 'population', 'controls': ['malformed', 'alias', 'non-json-number', 'deep', 'over-cap']}, {'ids': 'H-09-H-12', 'kind': 'steps', 'controls': ['malformed', 'non-json-number', 'deep', 'over-cap']}, {'id': 'H-13', 'kind': 'overhead', 'ceiling': {'ratio': 1.25, 'fixed_seconds': 0.05}}]}

def test_legal_near_cap_inputs_stay_within_approved_api_overhead(tmp_path: Path) -> None:
    ceiling = CASES['hostile_families'][-1]['ceiling']
    api = _api()

    def padded(source: Path, target: Path, cap: int, prefix: bytes) -> Path:
        raw = source.read_bytes()
        target.write_bytes(raw + prefix + b' ' * (cap - len(raw) - len(prefix) - 1))
        return target
    model = padded(ROOT / MODEL, tmp_path / 'model.yaml', MAX_MODEL_BYTES, b'\n#')
    population = padded(ROOT / POPULATIONS / '00-band-0.yaml', tmp_path / 'population.yaml', MAX_POPULATION_BYTES, b'\n#')
    pre, steps, post = _walk('clean-walk')
    step_path = padded(ROOT / steps, tmp_path / 'steps.json', MAX_STEPS_BYTES, b'\n')
    pairs = ((api._run_validate, api.validate, (model,)), (api._run_check, api.check, (model, population)), (api._run_transition, api.transition, (ROOT / TRANSITION_MODEL, ROOT / pre, step_path, ROOT / post)))
    for service, public, arguments in pairs:
        started = time.perf_counter()
        service(*arguments)
        baseline = time.perf_counter() - started
        started = time.perf_counter()
        public(*arguments)
        added = time.perf_counter() - started
        assert added <= baseline * ceiling['ratio'] + ceiling['fixed_seconds']
