"""MC2 corpus-first consumers; retained controls are identified separately."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest
from support.cli_runner import run_main

from gnd import api, disclosure
from gnd.documents import Model
from gnd.errors import ModelValidationError
from gnd.model import load_model
from gnd.model_verbalization import render_model_verbalization

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / '.gnd-planning/milestones/model-composition/evidence/MC2/corpus'
ANSWERS = {r['id']: r for r in json.loads((CORPUS / 'answers.json').read_text())['cases']}


@pytest.fixture
def corpus(tmp_path):
    target = tmp_path / 'corpus'
    shutil.copytree(CORPUS, target)
    return target


def read(path):
    return json.loads(path.read_text())


def cli(*args):
    return run_main(['verbalize', 'model', *map(str, args)])


@pytest.mark.parametrize('form', ['path', 'str', 'Model'])
def test_C01_new_api_preserves_plain_text(corpus, form):
    path = corpus / 'anchored/model.orm.yaml'
    value = load_model(path) if form == 'Model' else str(path) if form == 'str' else path
    assert api.verbalize_model(value) == (corpus / 'include-free-verbalization.expected.txt').read_text()


@pytest.mark.parametrize('form', ['path', 'Model'])
def test_C02_composed_review(corpus, form):
    path = corpus / 'anchored/project.orm.json'
    value = load_model(path) if form == 'Model' else path
    assert render_model_verbalization(value) == (corpus / 'include-verbalization.expected.txt').read_text()


def test_C03_rooted_compose_and_replay(corpus):
    a = corpus / 'anchored'
    result = api.compose(a / 'project.orm.json', a / 'composition')
    assert result['exit_code'] == ANSWERS[3]['compose_exit'], result
    assert result['population'] == read(a / 'include-composed.population.json')
    assert result['record'] == read(a / 'include-composition.record.json')
    replay = api.check(a / 'project.orm.json', a / 'include-composed.population.json',
                       composition=a / 'include-composition.record.json', sources=a / 'composition')
    assert replay['exit_code'] == ANSWERS[3]['replay_exit'], replay
    plain = api.check(a / 'model.orm.yaml', a / 'composed.population.json',
                      composition=a / 'composition.record.json', sources=a / 'composition')
    allowed = {'model', 'model_identity', 'model_sha256', 'model_version', 'population', 'population_sha256'}
    assert {k: v for k, v in replay.items() if k not in allowed} == {
        k: v for k, v in plain.items() if k not in allowed}
    assert result['record']['model_sha256'] == hashlib.sha256((a / 'project.orm.json').read_bytes()).hexdigest()


@pytest.mark.parametrize('route', ['compose', 'replay'])
def test_C04_tampered_pin_precedes_derivation(corpus, monkeypatch, route):
    import gnd.composition as composition
    a = corpus / 'anchored'
    (a / 'contracts-v1.orm.json').write_bytes((a / 'contracts-v1.orm.json').read_bytes() + b' ')
    monkeypatch.setattr(composition, 'compose', lambda *a, **k: pytest.fail('population derivation reached'))
    if route == 'compose':
        result = api.compose(a / 'project.orm.json', a / 'composition')
        assert result['exit_code'] == 3 and result['error']['message'] == ANSWERS[4]['reason'], result
    else:
        result = api.check(a / 'project.orm.json', a / 'include-composed.population.json',
                           composition=a / 'include-composition.record.json', sources=a / 'composition')
        assert result['exit_code'] == 3
        assert any(i['rule_id'] == ANSWERS[4]['reason'] for i in result['issues']), result


def test_C05_authored_snapshot_race_refuses(corpus, monkeypatch):
    import gnd.checking_service as service
    import gnd.composition as composition
    a = corpus / 'anchored'
    original = service._resolve_model
    seen = []

    def replace_after_load(value, **kwargs):
        result = original(value, **kwargs)
        seen.append(result[0])
        (a / 'project.orm.json').write_bytes((a / 'project.orm.json').read_bytes() + b' ')
        return result

    monkeypatch.setattr(service, '_resolve_model', replace_after_load)
    monkeypatch.setattr(composition, 'verify_composition', lambda *a, **k: pytest.fail('record verification reached'))
    result = api.check(a / 'project.orm.json', a / 'include-composed.population.json',
                       composition=a / 'include-composition.record.json', sources=a / 'composition')
    assert result['exit_code'] == ANSWERS[5]['exit'] and len(seen) == 1, result
    assert 'include:unsupported-route' not in json.dumps(result)


def test_C06_retained_codegen_currency_refusal(corpus, tmp_path):
    """An unchanged retained guard control, already green before MC2."""
    path = corpus / 'anchored/project.orm.json'
    out = tmp_path / 'generated'
    result = run_main(['codegen', str(path), '--out', str(out)])
    assert result.returncode == ANSWERS[6]['exit']
    assert ANSWERS[6]['reason'].encode() in result.stdout + result.stderr
    assert not out.exists()


def test_C07_declaration_order(corpus):
    text = render_model_verbalization(corpus / 'multiple/project.orm.json')
    headers = [s for s in text.splitlines() if s.startswith('Includes ')]
    assert headers == ANSWERS[7]['headers']


def test_C08_unresolved_constructed_model(corpus):
    model = Model.model_validate(read(corpus / 'unresolved-model.json'))
    with pytest.raises(ModelValidationError) as caught:
        render_model_verbalization(model)
    assert caught.value.issues[0].rule_id == ANSWERS[8]['rule_id']


def test_C09_missing_model_cli(corpus):
    result = cli(corpus / 'absent.orm.json')
    assert result.returncode == ANSWERS[9]['cli_exit']
    assert not result.stdout


@pytest.mark.parametrize('raw', [b'{', b'NaN', b'[]', b'9' * 5000], ids=['syntax', 'nonfinite', 'array', 'long-integer'])
def test_C10_malformed_model_cli(corpus, raw):
    path = corpus / 'bad.orm.json'
    path.write_bytes(raw)
    result = cli(path)
    assert result.returncode == ANSWERS[10]['cli_exit']
    assert not result.stdout


def test_C11_controls_do_not_forge_headers(corpus):
    path = corpus / 'anchored/project.orm.json'
    doc = read(path)
    declaration = doc['includes'][0]
    declaration['id'] = 'contracts\nFORGED\x1b[31m'
    old = path.parent / declaration['path']
    declaration['path'] = 'contracts\nline.orm.json'
    old.rename(path.parent / declaration['path'])
    path.write_text(json.dumps(doc))
    text = render_model_verbalization(path)
    headers = [s for s in text.splitlines() if s.startswith('Includes ')]
    assert len(headers) == 1
    assert '\\nFORGED' in headers[0] and '\\x1b' in headers[0]
    assert not any(s.startswith('FORGED') for s in text.splitlines())


def test_C12_retained_in_memory_replay_refusal(corpus):
    """An unchanged retained guard control, already green before MC2."""
    a = corpus / 'anchored'
    result = api.check(load_model(a / 'project.orm.json'), a / 'include-composed.population.json',
                       composition=a / 'include-composition.record.json', sources=a / 'composition')
    assert result['exit_code'] == ANSWERS[12]['exit']
    assert ANSWERS[12]['reason'] in json.dumps(result)


def test_C13_owned_rules_render_once(corpus):
    text = render_model_verbalization(corpus / 'owned-inline/project.orm.yaml')
    assert len([s for s in text.splitlines() if s.startswith('Includes ')]) == 1
    for identifier in ANSWERS[13]['owned_constraints']:
        assert text.count(f'"id":"{identifier}"') == 1


@pytest.mark.parametrize('mode', [None, 'customer', 'internal'])
def test_new_review_surface_modes(corpus, mode):
    path = corpus / 'anchored/project.orm.json'
    with disclosure.invocation(mode):
        assert api.verbalize_model(path) == (corpus / 'include-verbalization.expected.txt').read_text()
    args = ['--disclosure', mode] if mode else []
    result = run_main([*args, 'verbalize', 'model', str(path)])
    assert result.returncode == 0
    assert result.stdout.decode() == (corpus / 'include-verbalization.expected.txt').read_text()
