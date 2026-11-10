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
    expected_model = Model.model_validate(read(corpus / 'unresolved-model.json'))
    expected_dump = expected_model.model_dump(exclude={'warnings', 'operations', 'reference_populations'})
    assert replay['model_digest'] == 'sha256:' + hashlib.sha256(
        repr(expected_dump).encode('utf-8', 'surrogatepass')).hexdigest()
    assert plain['model_digest'] == read(corpus / 'include-free-replay.expected.json')['model_digest']
    for payload, model_name, population_name, record_name in (
        (replay, 'project.orm.json', 'include-composed.population.json', 'include-composition.record.json'),
        (plain, 'model.orm.yaml', 'composed.population.json', 'composition.record.json'),
    ):
        assert payload['model'] == str(a / model_name)
        assert payload['population'] == str(a / population_name)
        record_bytes = (json.dumps(read(a / record_name), sort_keys=True, separators=(',', ':'),
                                   ensure_ascii=False, allow_nan=False) + '\n').encode()
        assert payload['composition']['record_sha256'] == hashlib.sha256(record_bytes).hexdigest()
    assert replay['composition']['lineage'] == plain['composition']['lineage']
    allowed = {'model', 'population', 'model_digest'}
    left, right = ({k: v for k, v in payload.items() if k not in allowed}
                   for payload in (replay, plain))
    left['composition'] = {k: v for k, v in left['composition'].items() if k != 'record_sha256'}
    right['composition'] = {k: v for k, v in right['composition'].items() if k != 'record_sha256'}
    assert left == right
    assert result['record']['model_sha256'] == hashlib.sha256((a / 'project.orm.json').read_bytes()).hexdigest()


@pytest.mark.parametrize('route', ['compose', 'replay'])
def test_C04_tampered_pin_precedes_derivation(corpus, monkeypatch, route):
    from gnd import composition
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
    from gnd import composition
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
    assert '=== Header ===' not in result.stdout.decode()
    assert 'ERROR' in (result.stdout + result.stderr).decode()


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


@pytest.mark.parametrize('damage', ['no-metadata', 'id', 'path', 'sha256', 'missing-fields', 'extra', 'orphan'])
def test_unresolved_header_variants(corpus, damage):
    model = load_model(corpus / 'anchored/project.orm.json')
    if damage == 'no-metadata':
        model._included = ()
    elif damage == 'missing-fields':
        model.includes[0].clear()
    elif damage == 'extra':
        model.includes.append(dict(model.includes[0]))
    elif damage == 'orphan':
        model.includes.clear()
        model.fact_type_constraints.append({'fact_type': 'missing', 'constraints': [{}]})
    else:
        model.includes[0][damage] = ['hostile', {'shape': None}]
    with pytest.raises(ModelValidationError) as caught:
        render_model_verbalization(model)
    assert caught.value.issues[0].rule_id == 'include:unresolved'


@pytest.mark.parametrize('name,expected', [
    ('FileNotFoundError', 66), ('ModelLoadError', 3), ('YAMLError', 3),
    ('OSError', 3), ('ValueError', 3), ('TypeError', 3), ('RecursionError', 3), ('RuntimeError', 70),
])
def test_model_cli_exception_bands(monkeypatch, capsys, name, expected):
    import builtins

    from ruamel.yaml.error import YAMLError

    from gnd.commands.checking import _cmd_verbalize_model
    from gnd.errors import ModelLoadError

    kind = {'YAMLError': YAMLError, 'ModelLoadError': ModelLoadError}.get(name, getattr(builtins, name, None))

    def fail(_):
        raise kind('bad\nFORGED\x1b')

    monkeypatch.setattr(api, 'verbalize_model', fail)
    assert _cmd_verbalize_model('model.orm.json') == expected
    out = capsys.readouterr()
    assert not out.out and '\\nFORGED' in out.err and '\\x1b' in out.err
    assert not any(line.startswith('FORGED') for line in out.err.splitlines())


def test_plain_cli_preserves_text(corpus):
    result = cli(corpus / 'anchored/model.orm.yaml')
    assert result.returncode == 0
    assert result.stdout.decode() == (corpus / 'include-free-verbalization.expected.txt').read_text()


def test_private_authored_binding_is_not_serialized(corpus):
    from gnd.model import load_model_bytes_composed

    path = corpus / 'anchored/project.orm.json'
    model = load_model(path)
    expected = read(corpus / 'unresolved-model.json')
    assert model._authored_sha256 == hashlib.sha256(path.read_bytes()).hexdigest()
    assert load_model_bytes_composed(path.read_bytes(), source=path, root=path.parent)._authored_sha256 == model._authored_sha256
    assert model.model_dump() == expected
    assert model.model_dump_json() == Model.model_validate(expected).model_dump_json()
    assert load_model(path.parent / 'model.orm.yaml')._authored_sha256 is None


def test_header_layer_bounded_latency(monkeypatch):
    import time

    from gnd import model_verbalization as renderer
    from gnd.documents import IncludedFile

    declarations = [{'id': f'{i:0128d}', 'path': ('x' * 127 + '/') * 31 + 'x' * 128,
                     'sha256': 'a' * 64} for i in range(8)]
    model = Model(version=5, object_types=[], fact_types=[], includes=declarations)
    model._included = tuple(IncludedFile(d['id'], d['path'], d['sha256'], 1, None, None) for d in declarations)
    monkeypatch.setattr(renderer, 'load_model', lambda *a, **k: pytest.fail('header layer loaded a file'))
    start = time.monotonic()
    for _ in range(1000):
        lines = renderer._include_lines(model)
    elapsed = time.monotonic() - start
    assert len(lines) == 8 and elapsed < 3, elapsed


def test_legacy_malformed_compose_loader_lookup(corpus, monkeypatch):
    from gnd.errors import ModelLoadError

    path = corpus / 'bad.orm.json'
    path.write_bytes(b'{')
    seen = []

    def legacy(raw, *, source):
        seen.append((raw, source))
        raise ModelLoadError('legacy refusal')

    monkeypatch.setattr(api.model_module, 'load_model_bytes', legacy)
    monkeypatch.setattr(api.model_module, 'load_model_bytes_composed', lambda *a, **k: pytest.fail('rooted loader reached'))
    result = api.compose(path, corpus)
    assert seen == [(b'{', path)] and result['exit_code'] == 3
    assert result['error']['message'] == 'invalid model'


def test_plain_snapshot_cannot_pair_with_new_include(corpus, monkeypatch):
    from gnd import checking_service as service
    from gnd import composition

    a = corpus / 'anchored'
    original = service._resolve_model

    def replace(value, **kwargs):
        result = original(value, **kwargs)
        (a / 'model.orm.yaml').write_bytes((a / 'project.orm.json').read_bytes())
        return result

    monkeypatch.setattr(service, '_resolve_model', replace)
    monkeypatch.setattr(composition, 'verify_composition', lambda *a, **k: pytest.fail('record verify reached'))
    result = api.check(a / 'model.orm.yaml', a / 'composed.population.json',
                       composition=a / 'composition.record.json', sources=a / 'composition')
    assert result['exit_code'] == 3 and 'include:unsupported-route' in json.dumps(result)


def test_reference_composition_remains_refused(tmp_path):
    from test_mc1_model_includes import split_existing

    source = ROOT / 'tests/fixtures/reference-corpus/dispatch'
    shutil.copytree(source / 'references', tmp_path / 'references')
    path, _, _ = split_existing(tmp_path, source / 'model.orm.yaml')
    assert load_model(path).reference_populations
    result = api.compose(path, tmp_path / 'absent-composition')
    assert result['exit_code'] == 3
    assert result['error']['message'] == 'composition:invalid: composition with reference populations is unsupported'
    assert result['error'] == api.compose(source / 'model.orm.yaml', tmp_path / 'absent-composition')['error']


def test_authored_model_examples_remain_visible_in_customer_mode(corpus):
    path = corpus / 'anchored/project.orm.json'
    vocabulary = path.parent / 'contracts-v1.orm.json'
    shared = read(vocabulary)
    shared['fact_types'][0]['sample_population'] = [
        {role['role_name']: 'AUTHORED_SAMPLE_CANARY' for role in shared['fact_types'][0]['roles']}]
    vocabulary.write_text(json.dumps(shared))
    own = read(path)
    own['includes'][0]['sha256'] = hashlib.sha256(vocabulary.read_bytes()).hexdigest()
    path.write_text(json.dumps(own))
    ordinary = api.verbalize_model(path)
    assert 'AUTHORED_SAMPLE_CANARY' in ordinary
    with disclosure.invocation('customer'):
        assert api.verbalize_model(path) == ordinary
    result = run_main(['--disclosure', 'customer', 'verbalize', 'model', str(path)])
    assert result.returncode == 0 and result.stdout.decode() == ordinary


@pytest.mark.parametrize('missing', [False, True])
def test_model_cli_include_refusals_do_not_render(corpus, missing):
    path = corpus / 'anchored/project.orm.json'
    vocabulary = path.parent / 'contracts-v1.orm.json'
    if missing:
        vocabulary.unlink()
    else:
        vocabulary.write_bytes(vocabulary.read_bytes() + b' ')
    result = cli(path)
    assert result.returncode == 3 and b'=== Header ===' not in result.stdout
    expected = b'include:unreadable' if missing else b'include:hash-mismatch'
    assert expected in result.stdout + result.stderr


def test_rooted_composition_cli_writes_only_after_success(corpus, tmp_path):
    a = corpus / 'anchored'
    out, record = tmp_path / 'population.json', tmp_path / 'record.json'
    args = ['compose', str(a / 'project.orm.json'), str(a / 'composition')]
    result = run_main([*args, '--out', str(out), '--record', str(record)])
    assert result.returncode == 0, result.stdout + result.stderr
    assert read(out) == read(a / 'include-composed.population.json')
    assert read(record) == read(a / 'include-composition.record.json')
    checked = run_main(['check', str(a / 'project.orm.json'), str(out), '--composition',
                        str(record), '--sources', str(a / 'composition'), '--format', 'json'])
    assert checked.returncode == 0, checked.stdout + checked.stderr
    (a / 'contracts-v1.orm.json').unlink()
    refused_out, refused_record = tmp_path / 'refused.json', tmp_path / 'refused-record.json'
    refused = run_main([*args, '--out', str(refused_out), '--record', str(refused_record)])
    assert refused.returncode == 3 and b'include:unreadable' in refused.stdout + refused.stderr
    assert not refused_out.exists() and not refused_record.exists()


def test_T11_capped_authored_byte_binding_latency(corpus, monkeypatch):
    import time

    from gnd import anchors
    from gnd.checking_service import _composition_view
    from gnd.composition import CompositionError

    a = corpus / 'anchored'
    path = a / 'project.orm.json'
    raw = path.read_bytes().ljust(anchors.MAX_DOCUMENT_BYTES, b' ')
    path.write_bytes(raw)
    model = load_model(path)
    assert model._authored_sha256 == hashlib.sha256(raw).hexdigest()
    record = read(a / 'include-composition.record.json')
    record['model_sha256'] = model._authored_sha256
    captured = [raw]
    calls = []

    def read_snapshot(_path, *, label, max_bytes):
        assert label == 'model' and max_bytes == anchors.MAX_DOCUMENT_BYTES
        return captured[0]

    def verify(*args):
        calls.append(args)
        return 'verified-sentinel'

    monkeypatch.setattr(anchors, 'read_regular_path', read_snapshot)
    start = time.monotonic()
    for _ in range(20):
        derived, _ = _composition_view(model, path, 'pop.json', b'{}', record, a / 'composition', verify)
        assert derived == 'verified-sentinel'
    elapsed = time.monotonic() - start
    assert len(calls) == 20 and elapsed < 3, elapsed
    captured[0] = raw[:-1] + b'\t'
    with pytest.raises(CompositionError, match='model changed'):
        _composition_view(model, path, 'pop.json', b'{}', record, a / 'composition', verify)
    assert len(calls) == 20
    print(f'20 capped authored-byte comparisons: {elapsed:.6f}s < 3s')


@pytest.mark.parametrize('route', ['codegen', 'conformance'])
def test_T8_changed_vocabulary_never_claims_currency(corpus, tmp_path, route):
    path = corpus / 'anchored/project.orm.json'
    before = path.read_bytes()
    vocabulary = path.parent / 'contracts-v1.orm.json'
    vocabulary.write_bytes(vocabulary.read_bytes() + b' ')
    out = tmp_path / 'output'
    args = ([route, str(path), '--out', str(out)] if route == 'codegen'
            else [route, str(path), str(out), '--format', 'json'])
    result = run_main(args)
    assert result.returncode == 3 and b'include:unsupported-route' in result.stdout + result.stderr
    assert not out.exists() and path.read_bytes() == before
