"""MC1 include contract: refusals, provenance, identity, compatibility and order."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from gnd.model import ModelValidationError, load_model, load_model_bytes

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / 'src/gnd/examples/rule_check/model.orm.yaml'


def vocabulary():
    from ruamel.yaml import YAML
    doc = YAML(typ='safe').load(EXAMPLE.read_text())
    doc.pop('rejected_proposals')
    doc['fact_types'][0]['constraints'] = []
    return doc


def write_case(tmp_path, doc=None, *, suffix='.orm.json'):
    raw = json.dumps(vocabulary() if doc is None else doc).encode()
    included = tmp_path / ('vocab' + suffix)
    included.write_bytes(raw)
    own = {'version': 5, 'includes': [{'id': 'vocab', 'path': included.name,
            'sha256': hashlib.sha256(raw).hexdigest()}]}
    path = tmp_path / 'project.orm.json'
    path.write_text(json.dumps(own))
    return path, own, included


def save(path, doc):
    path.write_text(json.dumps(doc))


def reason(path, expected):
    with pytest.raises(ModelValidationError) as caught:
        load_model(path)
    assert caught.value.issues[0].rule_id == 'include:' + expected
    return caught.value.issues[0]


@pytest.mark.parametrize('bad', [None, True, 1, 'x', {}, [], [None], [{}],
                                [{'id': [], 'path': 'v', 'sha256': '0'*64}]])
def test_T5_declaration(tmp_path, bad):
    path, own, _ = write_case(tmp_path)
    own['includes'] = bad
    save(path, own)
    reason(path, 'declaration')


@pytest.mark.parametrize('bad', ['A'*64, '0'*63, 'g'*64])
def test_T6_hash_declaration(tmp_path, bad):
    path, own, _ = write_case(tmp_path)
    own['includes'][0]['sha256'] = bad
    save(path, own)
    reason(path, 'declaration')


@pytest.mark.parametrize('bad', ['../x', '/tmp/x', 'a//b', 'a\\b', 'C:x'])
def test_T8_path(tmp_path, bad):
    path, own, _ = write_case(tmp_path)
    own['includes'][0]['path'] = bad
    save(path, own)
    reason(path, 'path')


def test_T10_hash_mismatch(tmp_path):
    path, _, included = write_case(tmp_path)
    included.write_bytes(included.read_bytes() + b'\n')
    reason(path, 'hash-mismatch')


@pytest.mark.parametrize('section', ['includes', 'operations', 'reference_populations',
                                    'rejected_proposals', 'fact_type_constraints'])
def test_T13_forbidden(tmp_path, section):
    doc = vocabulary()
    doc[section] = []
    path, _, _ = write_case(tmp_path, doc)
    reason(path, 'forbidden-section')


def test_T15_collision(tmp_path):
    path, own, _ = write_case(tmp_path)
    own['object_types'] = [copy.deepcopy(vocabulary()['object_types'][0])]
    save(path, own)
    reason(path, 'collision')


def test_T18_unknown_target(tmp_path):
    path, own, _ = write_case(tmp_path)
    own['fact_type_constraints'] = [{'fact_type': 'missing', 'constraints': [{
        'type': 'mandatory', 'role': 'x', 'source': 'user-supplied',
        'status': 'confirmed', 'modality': 'alethic',
        'provenance': {'user_quote': 'required'}}]}]
    save(path, own)
    reason(path, 'unknown-target')


def test_T25_unresolved_and_orphan(tmp_path):
    path, own, _ = write_case(tmp_path)
    for includes in (own['includes'], None):
        own['includes'] = includes
        with pytest.raises(ModelValidationError) as caught:
            load_model_bytes(json.dumps(own).encode(), source=path)
        assert caught.value.issues[0].rule_id == 'include:unresolved'
    own = {'version': 5, 'fact_type_constraints': []}
    with pytest.raises(ModelValidationError) as caught:
        load_model_bytes(json.dumps(own).encode(), source=path)
    assert caught.value.issues[0].rule_id == 'include:declaration'


def test_T1_composed_content(tmp_path):
    path, own, included = write_case(tmp_path)
    composed = load_model(path)
    flat = load_model(included).model_dump()
    flat.update(version=5, includes=own['includes'], model_id=None, source={})
    assert composed.model_dump() == flat


@pytest.mark.parametrize('kind', ['missing', 'directory', 'leaf-link', 'ancestor-link'])
def test_T9_unreadable(tmp_path, kind):
    path, own, included = write_case(tmp_path)
    if kind == 'missing':
        included.unlink()
    elif kind == 'directory':
        included.unlink()
        included.mkdir()
    elif kind == 'leaf-link':
        target = included.with_name('target.orm.json')
        included.rename(target)
        included.symlink_to(target.name)
    else:
        (tmp_path / 'real').mkdir()
        included.rename(tmp_path / 'real' / included.name)
        (tmp_path / 'link').symlink_to('real', target_is_directory=True)
        own['includes'][0]['path'] = 'link/' + included.name
        save(path, own)
    reason(path, 'unreadable')


def test_T11_size(tmp_path):
    path, _, included = write_case(tmp_path)
    with included.open('wb') as handle:
        handle.truncate(10*1024*1024+1)
    reason(path, 'size')


@pytest.mark.parametrize('raw', [b'\xff', b'[:', b'[]', b'x: &a [1]\ny: *a\n',
                                b'version: 1\nobject_types: []\nfact_types: []\n'])
def test_T12_parse(tmp_path, raw):
    path, own, included = write_case(tmp_path)
    included.write_bytes(raw)
    own['includes'][0]['sha256'] = hashlib.sha256(raw).hexdigest()
    save(path, own)
    reason(path, 'parse')


def test_T14_unattended(tmp_path):
    doc = vocabulary()
    doc['source']['mode'] = 'unattended'
    path, _, _ = write_case(tmp_path, doc)
    reason(path, 'forbidden-section')


def test_T17_invalid_standalone(tmp_path):
    doc = vocabulary()
    doc['fact_types'][0]['roles'][0]['object_type'] = 'missing'
    path, _, _ = write_case(tmp_path, doc)
    reason(path, 'invalid-included-model')


@pytest.mark.parametrize('bad', [None, [], {}, [None], [{'fact_type': 'x'}]])
def test_T7_attachments(tmp_path, bad):
    path, own, _ = write_case(tmp_path)
    own['fact_type_constraints'] = bad
    save(path, own)
    reason(path, 'declaration')


def test_T21_all_paths_before_any_hash(tmp_path, monkeypatch):
    path, own, _ = write_case(tmp_path)
    own['includes'][0]['sha256'] = '0'*64
    own['includes'].append({'id': 'second', 'path': '../bad', 'sha256': '0'*64})
    save(path, own)
    from gnd import artifacts
    original = artifacts.read_regular_bounded_at
    def no_include_read(fd, relative, **kwargs):
        if relative != path.name:
            pytest.fail('include read ran before every path was checked')
        return original(fd, relative, **kwargs)
    monkeypatch.setattr(artifacts, 'read_regular_bounded_at', no_include_read)
    reason(path, 'path')


def attached_rule():
    return {'id': 'project_no_loops', 'type': 'ring', 'variant': 'acyclic',
            'source': 'user-supplied', 'status': 'confirmed', 'modality': 'alethic',
            'rationale': 'Project imports must form a DAG', 'remedy': 'Break the import loop.',
            'provenance': {'user_quote': 'No import loops.'}}


def attach(path, own, constraint=None):
    own['fact_type_constraints'] = [{'fact_type': 'component_imports_component',
                                     'constraints': [attached_rule() if constraint is None else constraint]}]
    save(path, own)


def test_T30_T31_T32_twin_check(tmp_path):
    from support.cli_runner import run_main
    path, own, _ = write_case(tmp_path)
    attach(path, own)
    flat = vocabulary()
    flat['version'] = 4
    flat.pop('model_id')
    flat['source'] = {}
    flat['fact_types'][0]['constraints'] = [attached_rule()]
    twin = tmp_path / 'flat.orm.json'
    save(twin, flat)
    for name in ('head', 'fixed'):
        population = ROOT / f'src/gnd/examples/rule_check/{name}.population.yaml'
        if name == 'fixed':
            from ruamel.yaml import YAML
            clean = YAML(typ='safe').load(population.read_text())
            facts = clean['facts']
            facts['component_imports_component'] = [r for r in facts['component_imports_component']
                if not (r['importer'] == 'auth' and r['imported'] == 'api')]
            for row in facts['component_is_in_area']:
                row['area'] = 'core'
            facts['component_has_owner'].append({'component': 'metrics', 'owner': 'platform'})
            facts['component_ships_in_release'] = [
                {'component': r['component'], 'release': '1.0'}
                for r in facts['component_is_in_area']]
            population = tmp_path / 'clean.population.json'
            save(population, clean)
        actual = run_main(['check', str(path), str(population), '--format', 'json'])
        expected = run_main(['check', str(twin), str(population), '--format', 'json'])
        assert actual.returncode == expected.returncode, (actual.stdout, expected.stdout)
        a, b = json.loads(actual.stdout), json.loads(expected.stdout)
        def normalized(value):
            if isinstance(value, dict):
                return {k: normalized(v) for k, v in value.items()
                        if k not in {'model', 'model_digest', 'model_identity', 'model_sha256', 'version'}}
            if isinstance(value, list):
                return [normalized(v) for v in value]
            return value
        assert normalized(a) == normalized(b)
        assert actual.returncode == (1 if name == 'head' else 0)


def test_T26_composed_bytes(tmp_path):
    from gnd.model import load_model_bytes_composed
    path, _, _ = write_case(tmp_path)
    assert load_model_bytes_composed(path.read_bytes(), source=path, root=tmp_path).model_dump() == load_model(path).model_dump()


def test_T44_T45b_deepest_provenance(tmp_path):
    path, own, _ = write_case(tmp_path)
    constraint = {'type': 'mandatory', 'role': 'absent', 'source': 'user-supplied',
                  'status': 'confirmed', 'modality': 'alethic',
                  'provenance': {'user_quote': 'Required'}}
    attach(path, own, constraint)
    with pytest.raises(ModelValidationError) as caught:
        load_model(path)
    assert any(i.path.startswith('$.fact_type_constraints[0].constraints[0]')
               for i in caught.value.issues)


def test_T39_metadata_and_origins(tmp_path):
    path, _, _ = write_case(tmp_path)
    model = load_model(path)
    assert model.model_id is None and model.source == {}
    assert model._included[0].model_id == vocabulary()['model_id']
    assert model._included[0].source == vocabulary()['source']
    assert any(o.origin == 'includes[vocab]' for o in model._provenance)


def test_T19_hostile_direct_calls(tmp_path):
    from gnd.model import retained_root
    from gnd.model._includes import compose, declares_includes, parse_declarations, parse_included
    shapes = [None, False, 3, 'x', [], {}, {'version': 5, 'includes': None}]
    for document in shapes:
        assert isinstance(declares_includes(document), bool)
        with pytest.raises(ModelValidationError):
            parse_declarations(document)
        with retained_root(tmp_path) as fd, pytest.raises(ModelValidationError):
            compose(document, descriptor=fd, source='model.orm.json')
    for raw in [b'\xff', b'NaN', b'['*200+b']'*200, b'{"n":'+b'9'*5000+b'}']:
        with pytest.raises(ModelValidationError):
            parse_included(raw, include_id='v', path='v.orm.json')


def test_T21_hash_before_parse(tmp_path, monkeypatch):
    import gnd.model._includes as includes
    path, _own, included = write_case(tmp_path)
    included.write_bytes(b'not json')
    def forbidden(*args, **kwargs):
        pytest.fail('parse stage ran after a bad hash')
    monkeypatch.setattr(includes, 'parse_included', forbidden)
    reason(path, 'hash-mismatch')


def test_T42_T43_identity_envelopes(tmp_path):
    from gnd.documents import Model
    from gnd.values import _model_digest, model_identity, reference_model_digest
    path, own, included = write_case(tmp_path)
    actual = load_model(path)
    independent = load_model(included).model_dump()
    independent.update(version=5, model_id=None, source={}, includes=own['includes'])
    expected = Model.model_validate(independent)
    for identity in (_model_digest, model_identity, reference_model_digest):
        assert identity(actual) == identity(expected)
    moved = included.with_name('moved.orm.json')
    moved.write_bytes(included.read_bytes())
    own['includes'][0]['path'] = moved.name
    save(path, own)
    assert model_identity(actual) != model_identity(load_model(path))


def test_T40_T47_v5_plain_temporal():
    path = ROOT / 'tests/fixtures/rc1-rule-ids/models/temporal.orm.yaml'
    original = load_model(path)
    doc = original.model_dump(exclude={'warnings'})
    doc['version'] = 5
    upgraded = load_model_bytes(json.dumps(doc).encode(), source='model.orm.json')
    assert upgraded.model_dump(exclude={'version'}) == original.model_dump(exclude={'version'})


def split_existing(tmp_path, original):
    from ruamel.yaml import YAML
    document = YAML(typ='safe').load(original.read_text())
    included = copy.deepcopy(document)
    own = {'version': 5, 'source': document.get('source', {}), 'model_id': document.get('model_id')}
    for section in ('operations', 'reference_populations', 'rejected_proposals'):
        if section in included:
            own[section] = included.pop(section)
    path, declaration, shared = write_case(tmp_path, included)
    own['includes'] = declaration['includes']
    save(path, own)
    return path, own, shared


def test_T34_own_operations_compile_against_included_types(tmp_path):
    original = ROOT / 'tests/fixtures/models/v2_operations.orm.yaml'
    path, _, _ = split_existing(tmp_path, original)
    actual, expected = load_model(path), load_model(original)
    assert actual.operations == expected.operations
    assert actual._compiled == expected._compiled
    assert actual._compiled


def test_T27_T28_reference_ownership(tmp_path):
    import shutil

    from gnd.model import load_model_bytes_composed
    source = ROOT / 'tests/fixtures/reference-corpus/dispatch'
    shutil.copytree(source / 'references', tmp_path / 'references')
    path, _, _ = split_existing(tmp_path, source / 'model.orm.yaml')
    baseline = load_model(source / 'model.orm.yaml')
    actual = load_model(path)
    buffered = load_model_bytes_composed(path.read_bytes(), source=path, root=tmp_path)
    for model in (actual, buffered):
        assert model._references is not None
        assert model._references._owners == baseline._references._owners
        assert [p.model_dump() for p in model._references._populations] == [
            p.model_dump() for p in baseline._references._populations]


def test_T36_subtype_and_T37_rejected_history(tmp_path):
    path, own, _ = write_case(tmp_path)
    own['object_types'] = [{'id': 'service', 'name': 'Service', 'kind': 'entity',
                            'subtype_of': ['component'], 'inherits_reference': True}]
    own['rejected_proposals'] = [{'id': 'old', 'type': 'textual', 'status': 'rejected',
                                  'rationale': 'Do not propose another component rule',
                                  'expression': 'component'}]
    save(path, own)
    model = load_model(path)
    assert model.object_types[0]['subtype_of'] == ['component']
    assert model.rejected_proposals == own['rejected_proposals']


def test_T38_notes_order(tmp_path):
    first = vocabulary()
    first['deontic_notes'] = [{'text': 'shared'}]
    path, own, _ = write_case(tmp_path, first)
    own['deontic_notes'] = [{'text': 'project'}]
    second = {'version': 1, 'object_types': [], 'fact_types': [], 'deontic_notes': [{'text': 'second'}]}
    raw = json.dumps(second).encode()
    (tmp_path / 'second.orm.json').write_bytes(raw)
    own['includes'].append({'id': 'second', 'path': 'second.orm.json', 'sha256': hashlib.sha256(raw).hexdigest()})
    save(path, own)
    assert [n.text for n in load_model(path).deontic_notes] == ['project', 'shared', 'second']


def test_T16_second_include_collision(tmp_path):
    path, own, _ = write_case(tmp_path)
    raw = json.dumps({'version': 1, 'object_types': [], 'fact_types': [], 'constraints': [{
        'id': 'same', 'type': 'textual', 'expression': 'A rule', 'modality': 'deontic',
        'source': 'user-supplied', 'status': 'confirmed', 'provenance': {'user_quote': 'A rule'}}]}).encode()
    (tmp_path / 'second.orm.json').write_bytes(raw)
    own['includes'].append({'id': 'second', 'path': 'second.orm.json', 'sha256': hashlib.sha256(raw).hexdigest()})
    own['constraints'] = json.loads(raw)['constraints']
    save(path, own)
    issue = reason(path, 'collision')
    assert 'second' in issue.message and 'model' in issue.message


def test_T11_growth_and_set_cap(tmp_path, monkeypatch):
    from gnd import artifacts
    path, own, _ = write_case(tmp_path)
    def grew(descriptor, relative, **kwargs):
        raise artifacts.ArtifactError(f'artifact {relative} grew over the {10*1024*1024}-byte cap')
    with monkeypatch.context() as patch:
        patch.setattr(artifacts, 'read_regular_bounded_at', grew)
        # Call compose directly: the includer's own read is a different boundary.
        from gnd.model import retained_root
        from gnd.model._includes import compose
        with retained_root(tmp_path) as fd, pytest.raises(ModelValidationError) as caught:
            compose(own, descriptor=fd, source=path)
        assert caught.value.issues[0].rule_id == 'include:size'
    own['includes'] = []
    for i in range(4):
        raw = b' '*(9*1024*1024) + b'{}'
        name = f'big{i}.orm.json'
        (tmp_path / name).write_bytes(raw)
        own['includes'].append({'id': f'v{i}', 'path': name, 'sha256': hashlib.sha256(raw).hexdigest()})
    save(path, own)
    reason(path, 'size')


def test_T50_runtime_frozen_T46_aliases():
    import subprocess

    import gnd.model._paths as paths
    import gnd.model._validation as validation
    from gnd import errors, model
    assert model._relative is paths._relative
    assert model.retained_root is paths.retained_root
    assert model.parse_model_document is validation.parse_model_document
    assert model.ReferenceInputError is errors.ReferenceInputError
    runtime = 'src/gnd/export/pyrel_runtime.py'
    assert (ROOT / runtime).read_bytes() == subprocess.check_output(['git', 'show', f'459ca8d2:{runtime}'], cwd=ROOT)


def test_T49_legacy_exception_spelling(tmp_path):
    from gnd.api import diff
    path = tmp_path / 'large.orm.yaml'
    with path.open('wb') as handle:
        handle.truncate(10*1024*1024+1)
    with pytest.raises(Exception, match='diff:invalid-model:ArtifactError'):
        diff(path, path)


def test_T22_scaling_and_quadratic_mutant():
    import statistics
    import time

    from gnd.model._includes import _merge
    def document(n):
        return {'version': 5, 'object_types': [{'id': f'o{i}'} for i in range(n)], 'fact_types': []}
    def measured(n, mutant):
        doc = document(n)
        def run():
            _merge(doc, [], [])
            if mutant:
                ids = [r['id'] for r in doc['object_types']]
                assert not any(a == b for i, a in enumerate(ids) for b in ids[i+1:])
        run()
        samples = []
        for _ in range(3):
            start = time.perf_counter()
            run()
            samples.append(time.perf_counter() - start)
        return statistics.median(samples)
    # Gate tests the new merge/index layer, independent of old semantic rules.
    linear = [measured(n, False) for n in (1000, 4000, 16000)]
    assert linear[2] <= 6*linear[1], linear
    quadratic = [measured(n, True) for n in (4000, 16000)]
    assert quadratic[1] > 6*quadratic[0], quadratic
    print(json.dumps({"linear_seconds":linear,"linear_ratio":linear[2]/linear[1],
                      "quadratic_seconds":quadratic,"quadratic_ratio":quadratic[1]/quadratic[0]}))


@pytest.mark.parametrize('command', ['validate', 'check'])
@pytest.mark.parametrize('format_', ['text', 'json'])
@pytest.mark.parametrize('case,expected_exit', [('clean', 0), ('cycle', 1), ('self', 1)])
def test_T2_T4_T32_T33_committed_twins(command, format_, case, expected_exit):
    from support.cli_runner import run_main
    fixture = ROOT / 'tests/fixtures/mc1-includes'
    paths = [fixture / 'project.orm.yaml', fixture / 'flattened.orm.yaml']
    results = [run_main([command, str(path), *(
        [str(fixture / f'{case}.pop.json')] if command == 'check' else []), '--format', format_])
        for path in paths]
    assert all(r.returncode == (0 if command == 'validate' else expected_exit) for r in results)
    # Normalize only model coordinates/digests and model-format version.
    if format_ == 'text':
        outputs = [r.stdout.replace(str(p).encode(), b'<MODEL>') for r,p in zip(results, paths, strict=True)]
        assert outputs[0] == outputs[1]
    else:
        def without_coordinates(node):
            if isinstance(node, dict):
                return {k: without_coordinates(v) for k,v in node.items() if k not in {
                    'model', 'model_identity', 'model_digest', 'model_sha256', 'version'}}
            return [without_coordinates(v) for v in node] if isinstance(node, list) else node
        assert without_coordinates(json.loads(results[0].stdout)) == without_coordinates(json.loads(results[1].stdout))
    if command == 'check' and case == 'self':
        assert b'fact_types[component_uses_component].constraints[1]' in results[0].stdout
        assert b'fact_types[component_uses_component].constraints[0]' in results[0].stdout


@pytest.mark.parametrize('format_', ['text', 'json'])
@pytest.mark.parametrize('command', ['validate', 'check'])
@pytest.mark.parametrize('fault,expected', [('hash', 'hash-mismatch'), ('path', 'path'), ('declaration', 'declaration'),
    ('parse','parse'),('forbidden','forbidden-section'),('collision','collision'),('invalid','invalid-included-model'),
    ('unknown','unknown-target'),('missing','unreadable'),('size','size')])
def test_refusal_cli_matrix(tmp_path, format_, command, fault, expected):
    from support.cli_runner import run_main
    path, own, included = write_case(tmp_path)
    if fault == 'hash':
        included.write_bytes(included.read_bytes()+b'\n')
    elif fault == 'path':
        own['includes'][0]['path'] = '../escape'
    elif fault == 'declaration':
        own['includes'] = []
    elif fault in ('parse', 'forbidden', 'invalid'):
        doc = vocabulary()
        if fault == 'forbidden': doc['operations'] = []
        if fault == 'invalid': doc['fact_types'][0]['roles'][0]['object_type'] = 'missing'
        raw = b'not-json' if fault == 'parse' else json.dumps(doc).encode()
        included.write_bytes(raw)
        own['includes'][0]['sha256'] = hashlib.sha256(raw).hexdigest()
    elif fault == 'collision':
        own['object_types'] = [copy.deepcopy(vocabulary()['object_types'][0])]
    elif fault == 'unknown':
        own['fact_type_constraints'] = [{'fact_type':'absent','constraints':[attached_rule()]}]
    elif fault == 'missing': included.unlink()
    elif fault == 'size':
        with included.open('wb') as handle: handle.truncate(10*1024*1024+1)
    save(path,own)
    population = ROOT / 'tests/fixtures/mc1-includes/clean.pop.json'
    result = run_main([command,str(path),*([str(population)] if command=='check' else []),'--format',format_])
    assert result.returncode == 3
    assert f'include:{expected}'.encode() in result.stdout+result.stderr


def proposed_ring(identifier):
    rule = attached_rule()
    rule.update(id=identifier, source='common-sense', status='proposed',
                provenance={'library_entry': 'acyclic-imports', 'rationale_world_fact': 'Loops should be avoided.'})
    return rule


def test_T45b_mixed_host_warning_paths(tmp_path):
    doc = vocabulary()
    doc['fact_types'][0]['constraints'] = [proposed_ring('included_warning')]
    path, own, _ = write_case(tmp_path, doc)
    attach(path, own, proposed_ring('owned_warning'))
    model = load_model(path)
    warnings = [w for w in model.warnings if w.rule_id == 'semantic:modality-policy']
    assert len(warnings) == 2
    assert warnings[0].path == 'includes[vocab]:$.fact_types[id=component_imports_component].constraints[0]'
    assert warnings[1].path == '$.fact_type_constraints[0].constraints[0]'


def test_T44_anonymous_origin_and_source_direction(tmp_path):
    doc = vocabulary()
    doc['constraints'][0].pop('id')
    path, own, _ = write_case(tmp_path, doc)
    own['source'] = {'kind':'prose','mode':'unattended','reviewer':'none',
                     'documents':[{'sha256':'0'*64,'label':'source.txt'}]}
    save(path, own)
    with pytest.raises(ModelValidationError) as caught:
        load_model(path)
    assert any(i.path.startswith('includes[vocab]:$.constraints[0]') for i in caught.value.issues)
    assert any(i.rule_id.startswith('semantic:unattended-') for i in caught.value.issues)


@pytest.mark.parametrize('version',[3,4])
def test_T48_temporal_vocabulary(tmp_path,version):
    from ruamel.yaml import YAML
    doc = YAML(typ='safe').load((ROOT/'tests/fixtures/rc1-rule-ids/models/temporal.orm.yaml').read_text())
    doc['version'] = version
    doc.pop('rejected_proposals', None)
    path, _, _ = write_case(tmp_path,doc)
    actual = load_model(path)
    assert actual.object_types == doc['object_types']
    assert actual.fact_types == doc['fact_types']


def test_T42b_included_content_mutation(tmp_path):
    from gnd.values import model_identity
    path, own, included = write_case(tmp_path)
    before = model_identity(load_model(path))
    doc = json.loads(included.read_bytes())
    doc['fact_types'][0]['reading'] = '{Component} imports another {Component}'
    raw = json.dumps(doc).encode()
    included.write_bytes(raw)
    own['includes'][0]['sha256'] = hashlib.sha256(raw).hexdigest()
    save(path,own)
    assert model_identity(load_model(path)) != before


def test_T12b_yaml_vocabulary(tmp_path):
    import io

    from ruamel.yaml import YAML
    stream=io.StringIO()
    YAML().dump(vocabulary(),stream)
    path,own,included=write_case(tmp_path,suffix='.orm.yaml')
    raw=stream.getvalue().encode()
    included.write_bytes(raw)
    own['includes'][0]['sha256']=hashlib.sha256(raw).hexdigest()
    save(path,own)
    assert load_model(path).fact_types == vocabulary()['fact_types']


def test_T20_schema_envelope_parity(tmp_path):
    from jsonschema import Draft202012Validator

    from gnd.model._includes import parse_declarations
    from gnd.model._validation import _load_meta_schema
    _, own, _ = write_case(tmp_path)
    validator=Draft202012Validator(_load_meta_schema())
    for bad in (None, True, [], [{}], [None], 'x'):
        doc=copy.deepcopy(own)
        doc['includes']=bad
        assert not validator.is_valid(doc)
        with pytest.raises(ModelValidationError): parse_declarations(doc)
    duplicate=copy.deepcopy(own)
    duplicate['includes']*=2
    assert validator.is_valid(duplicate)
    with pytest.raises(ModelValidationError): parse_declarations(duplicate)


def test_T18_own_target_refuses(tmp_path):
    path,own,_=write_case(tmp_path)
    ft=copy.deepcopy(vocabulary()['fact_types'][0])
    ft['id']='own_uses'
    own['fact_types']=[ft]
    own['fact_type_constraints']=[{'fact_type':'own_uses','constraints':[attached_rule()]}]
    save(path,own)
    reason(path,'unknown-target')


def test_T35_derived_own_fact_type(tmp_path):
    from gnd.api import check
    path,own,_=write_case(tmp_path)
    own['fact_types']=[{'id':'own_imports','reading':'{Component} also imports {Component}',
        'roles':[{'object_type':'component','role_name':'from_component'},
                 {'object_type':'component','role_name':'to_component'}],
        'derivation':'derived','derivation_rule':{
            'body':[{'fact_type':'component_imports_component','bind':{'importer':'$a','imported':'$b'}}],
            'head':{'from_component':'$a','to_component':'$b'}}}]
    save(path,own)
    model=load_model(path)
    assert model.fact_types[0]['id']=='own_imports'
    result=check(path,ROOT/'src/gnd/examples/rule_check/head.population.yaml')
    assert result['exit_code'] in (0,1,2)
    assert 'own_imports' in str(result['derivations'])


def test_T21_forbidden_before_validation(tmp_path, monkeypatch):
    import gnd.model._includes as includes
    doc=vocabulary()
    doc['operations']=[]
    doc['fact_types'][0]['roles'][0]['object_type']='missing'
    path,_,_=write_case(tmp_path,doc)
    structural = includes._structural
    def no_standalone_shape(document):
        if document.get('version') != 5:
            pytest.fail('standalone structural validation ran before forbidden-section refusal')
        return structural(document)
    monkeypatch.setattr(includes,'_structural',no_standalone_shape)
    def forbidden(*args,**kwargs): pytest.fail('standalone validation ran before forbidden-section refusal')
    monkeypatch.setattr(includes,'semantic_validate',forbidden)
    reason(path,'forbidden-section')


def test_T51_export_program_identity():
    from gnd.export.emit import render_pyrel
    row=json.loads((ROOT/'.gnd-planning/milestones/model-composition/evidence/MC1/baseline-export.json').read_text())
    path=Path(row['source_model'])
    assert hashlib.sha256(path.read_bytes()).hexdigest()==row['model_sha256']
    actual=render_pyrel(path,duckdb_path=row['duckdb_path'],connection=row['connection'])
    assert hashlib.sha256(actual.encode()).hexdigest()==row['program_sha256']


def test_T29_reference_write_refuses(tmp_path):
    import shutil

    from gnd.model import ReferenceInputError
    source=ROOT/'tests/fixtures/reference-corpus/dispatch'
    shutil.copytree(source/'references',tmp_path/'references')
    path,own,_=split_existing(tmp_path,source/'model.orm.yaml')
    own['operations']=[{'id':'write_catalog','reading':'{Warehouse} allows {Product}',
        'source':'user-supplied','status':'confirmed','provenance':{'user_quote':'Write the catalog.'},'parameters':[
        {'name':'w','object_type':'dispatch_warehouse'},{'name':'p','object_type':'dispatch_product'}],
        'effects':[{'assert':{'fact_type':'dispatch_catalog_allows','bind':{'warehouse':'$w','product':'$p'}}}],
        'frame':{'modality':'alethic'}}]
    save(path,own)
    with pytest.raises(ReferenceInputError,match='reference-owned'):
        load_model(path)


def test_T21_collision_before_composed_semantics(tmp_path,monkeypatch):
    from gnd import model
    path,own,_=write_case(tmp_path)
    own['object_types']=[copy.deepcopy(vocabulary()['object_types'][0])]
    save(path,own)
    def forbidden(*args,**kwargs): pytest.fail('composed validation ran before collision refusal')
    monkeypatch.setattr(model,'semantic_validate',forbidden)
    reason(path,'collision')


def test_root_symlink_refuses(tmp_path):
    real=tmp_path/'real'
    real.mkdir()
    path,_,_=write_case(real)
    alias=tmp_path/'alias'
    alias.symlink_to(real,target_is_directory=True)
    reason(alias/path.name,'unreadable')


@pytest.mark.parametrize('section,bad', [('object_types',None),('object_types',[None]),
    ('object_types',[{'id':[]}]),('fact_types',[{'id':{}}]),('constraints',[None])])
def test_T19_hostile_own_shapes(tmp_path,section,bad):
    from gnd.model import retained_root
    from gnd.model._includes import compose
    path,own,_=write_case(tmp_path)
    own[section]=bad
    with retained_root(tmp_path) as fd,pytest.raises(ModelValidationError):
        compose(own,descriptor=fd,source=path)


def test_T17_yaml_nonfinite_description(tmp_path):
    import io

    from ruamel.yaml import YAML
    doc=vocabulary()
    doc['object_types'][0]['description']={'summary':'Component','sample':float('nan')}
    stream=io.StringIO()
    YAML().dump(doc,stream)
    path,own,included=write_case(tmp_path,suffix='.orm.yaml')
    raw=stream.getvalue().encode()
    included.write_bytes(raw)
    own['includes'][0]['sha256']=hashlib.sha256(raw).hexdigest()
    save(path,own)
    reason(path,'invalid-included-model')
