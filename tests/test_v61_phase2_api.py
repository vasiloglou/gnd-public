from __future__ import annotations

import importlib
import inspect
from pathlib import Path

import pytest

from gnd.model import MAX_MODEL_BYTES, load_model
from gnd.population import MAX_POPULATION_BYTES, Population, load_population

ROOT = Path(__file__).resolve().parents[1]
MODEL = 'tests/fixtures/v61-phase1/batch/model.orm.yaml'
POPULATIONS = 'tests/fixtures/v61-phase1/batch/populations'
ANSWERS = {'path_payloads': {'validate-valid': {'exit_code': 0, 'outcome': 'accepted', 'acceptance_ready': True}, 'validate-invalid': {'exit_code': 3, 'outcome': 'ill_formed', 'acceptance_ready': False}}, 'object_payloads': {'validate-loaded': {'exit_code': 0, 'model': None}}}

def _api():
    try:
        return importlib.import_module('gnd.api')
    except ModuleNotFoundError as error:
        pytest.fail('expected corpus-first RED: gnd.api does not exist yet; approve tests/fixtures/v61-phase2 before production implementation', pytrace=False)
        raise AssertionError from error

def _assert_subset(payload: dict[str, object], expected: dict[str, object]) -> None:
    for key, value in expected.items():
        if key == 'assurance_level':
            assert payload['assurance']['assurance_level'] == value
        elif key == 'evidence_not_current':
            assert ('applicability:refusal:n-a:evidence-not-current' in payload['assurance']['uncovered_applicable_scope_ids']) is value
        elif key == 'evaluated':
            assert payload['transition']['evaluated'] is value
        else:
            assert payload[key] == value

def test_public_all_is_exact() -> None:
    api = _api()
    assert api.__all__ == ('validate', 'check', 'transition', 'verbalize', 'diff', 'witness', 'replay', 'check_with_receipt', 'CheckReceipt', 'ReceiptRefused')
    assert {name for name in vars(api) if not name.startswith('_')} >= set(api.__all__)

def test_public_signatures_are_stable() -> None:
    api = _api()
    assert tuple(inspect.signature(api.validate).parameters) == ('model', 'unredacted', 'references')
    assert tuple(inspect.signature(api.check).parameters) == ('model', 'population', 'compiled_operations', 'unredacted', 'anchors', 'document', 'population_bytes', 'admission', 'references')
    compiled = inspect.signature(api.check).parameters['compiled_operations']
    assert compiled.kind is inspect.Parameter.KEYWORD_ONLY
    assert compiled.default is False
    assert tuple(inspect.signature(api.transition).parameters) == ('model', 'pre', 'steps', 'post', 'unredacted', 'references', 'pre_receipt')
    for function in (api.validate, api.check, api.transition):
        parameter = inspect.signature(function).parameters['unredacted']
        assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
        assert parameter.default is False
        assert inspect.signature(function).return_annotation != inspect.Signature.empty
        reference = inspect.signature(function).parameters['references']
        assert reference.kind is inspect.Parameter.KEYWORD_ONLY
        assert reference.default is None

@pytest.mark.parametrize(('model', 'answer'), [(MODEL, 'validate-valid'), ('tests/fixtures/derivation/cases/r24-head-malformed-variable.orm.yaml', 'validate-invalid')])
def test_validate_paths_return_existing_payloads(model: str, answer: str) -> None:
    payload = _api().validate(model)
    _assert_subset(payload, ANSWERS['path_payloads'][answer])

def test_validate_loaded_model_has_no_path_claim() -> None:
    payload = _api().validate(load_model(MODEL))
    _assert_subset(payload, ANSWERS['object_payloads']['validate-loaded'])

def test_validate_loaded_model_refuses_nested_mutation() -> None:
    model = load_model(MODEL)
    model.fact_types[0]['roles'][0]['object_type'] = 'undeclared-after-load'
    payload = _api().validate(model)
    assert payload['exit_code'] == 3
    assert any(issue['rule_id'] == 'semantic:role-ref' for issue in payload['issues'])

def test_unsupported_inputs_raise_type_error_before_evaluation() -> None:
    api = _api()
    with pytest.raises(TypeError):
        api.validate(41)
    with pytest.raises(TypeError):
        api.check(41, MODEL)
    with pytest.raises(TypeError):
        api.transition(MODEL, 41, {}, MODEL)

@pytest.mark.parametrize('band', range(5))
def test_snapshot_paths_reach_every_existing_band(band: int) -> None:
    payload = _api().check(MODEL, f'{POPULATIONS}/0{band}-band-{band}.yaml')
    assert payload['exit_code'] == band

def test_snapshot_reuses_one_loaded_model_with_path_or_object_population() -> None:
    api = _api()
    model = load_model(MODEL)
    path_payload = api.check(model, f'{POPULATIONS}/00-band-0.yaml')
    population = load_population(f'{POPULATIONS}/00-band-0.yaml', model=model)
    object_payload = api.check(model, population)
    assert path_payload['exit_code'] == object_payload['exit_code'] == 0
    assert object_payload['model'] is None
    assert object_payload['population'] is None
    assert object_payload['assurance']['assurance_level'] == 'none'
    assert object_payload['assurance']['uncovered_applicable_scope_ids']

@pytest.mark.parametrize('mutation', ['path-object', 'unstamped', 'nested-content', 'deep-copy', 'different-model-stamp'])
def test_loaded_population_marker_failures_are_payload_shaped_70(mutation: str) -> None:
    api = _api()
    model = load_model(MODEL)
    population = load_population(f'{POPULATIONS}/00-band-0.yaml', model=model)
    supplied_model: object = model
    if mutation == 'path-object':
        supplied_model = MODEL
    elif mutation == 'unstamped':
        population = Population.model_validate(population.model_dump())
    elif mutation == 'nested-content':
        population.facts['seed'].append({'item': 'changed-after-validation'})
    elif mutation == 'deep-copy':
        population = population.model_copy(deep=True)
    elif mutation == 'different-model-stamp':
        other = load_model(MODEL)
        population = load_population(f'{POPULATIONS}/00-band-0.yaml', model=other)
    payload = api.check(supplied_model, population)
    assert payload['exit_code'] == 70
    assert payload['error']['type'] == 'UnvalidatedPopulationError'

def test_snapshot_internal_fault_returns_70(monkeypatch: pytest.MonkeyPatch) -> None:
    api = _api()
    checker = importlib.import_module('gnd.checker')
    monkeypatch.setattr(checker, 'check', lambda *_: (_ for _ in ()).throw(RuntimeError('pin')))
    payload = api.check(MODEL, f'{POPULATIONS}/00-band-0.yaml')
    assert payload['exit_code'] == 70
    assert payload['error']['type'] == 'RuntimeError'

def test_direct_api_does_not_arm_a_later_receipt_emission(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    api = _api()
    report = importlib.import_module('gnd.report')
    receipt = tmp_path / 'unrelated-receipt.json'
    monkeypatch.setenv('GND_INTERNAL_ASSURANCE_RECEIPT', str(receipt))
    monkeypatch.setenv('GND_INTERNAL_ASSURANCE_NONCE', '0' * 64)
    payload = api.check(MODEL, f'{POPULATIONS}/00-band-0.yaml')
    report.emit(payload)
    assert not receipt.exists()

@pytest.mark.parametrize('kind', ['malformed', 'alias', 'over-cap'])
def test_hostile_model_paths_return_reports_without_tracebacks(tmp_path: Path, kind: str) -> None:
    _api_module = _api()
    path = tmp_path / 'hostile.orm.yaml'
    if kind == 'malformed':
        path.write_text('version: [', encoding='utf-8')
    elif kind == 'alias':
        path.write_text('version: &v 2\nmodel_id: *v\n', encoding='utf-8')
    else:
        path.write_bytes(b'x' * (MAX_MODEL_BYTES + 1))
    payload = _api_module.validate(path)
    assert payload['exit_code'] == 3

@pytest.mark.parametrize('kind', ['malformed', 'alias', 'non-json-number', 'deep', 'over-cap'])
def test_hostile_population_paths_return_reports_without_tracebacks(tmp_path: Path, kind: str) -> None:
    _api_module = _api()
    suffix = '.json' if kind in {'non-json-number', 'deep'} else '.yaml'
    path = tmp_path / f'hostile{suffix}'
    if kind == 'malformed':
        path.write_text('population: [', encoding='utf-8')
    elif kind == 'alias':
        path.write_text('population: &p {}\nfacts: *p\n', encoding='utf-8')
    elif kind == 'non-json-number':
        path.write_text('{"population":{},"facts":{"x":[{"v":NaN}]}}', encoding='utf-8')
    elif kind == 'deep':
        path.write_text('[' * 1200 + ']' * 1200, encoding='utf-8')
    else:
        path.write_bytes(b'x' * (MAX_POPULATION_BYTES + 1))
    payload = _api_module.check(MODEL, path)
    assert payload['exit_code'] == 3

def test_api_does_not_read_cwd_home_or_tmpdir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    forbidden = {tmp_path / name for name in ('cwd/.env', 'home/.gnd', 'tmp/config')}
    for path in forbidden:
        path.parent.mkdir(exist_ok=True)
        path.write_text('must not be read', encoding='utf-8')
    original = Path.open

    def guarded(path: Path, *args, **kwargs):
        assert path.resolve() not in forbidden
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, 'open', guarded)
    monkeypatch.setenv('HOME', str(tmp_path / 'home'))
    monkeypatch.setenv('TMPDIR', str(tmp_path / 'tmp'))
    monkeypatch.chdir(tmp_path / 'cwd')
    payload = _api().check(ROOT / MODEL, ROOT / POPULATIONS / '00-band-0.yaml')
    assert payload['exit_code'] == 0
