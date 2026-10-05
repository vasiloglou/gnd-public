import shutil
from pathlib import Path

from gnd import api
from gnd.model import load_model_bytes

ROOT = Path(__file__).resolve().parents[1]

def test_byte_loader_preserves_trailing_literal_block_text():
    raw = b'version: 1\nobject_types: []\nfact_types: []\nsource:\n  note: |+\n    hi  \n     '
    model = load_model_bytes(raw, source='literal-model.yaml')
    assert model.source['note'] == 'hi  \n '

def test_asserted_origin_roster_has_canonical_order(tmp_path):
    root = tmp_path / 'dispatch'
    shutil.copytree(ROOT / 'tests/fixtures/v71/phase2/dispatch', root)
    report = api.check(root / 'model.orm.yaml', root / 'candidate.pop.json')
    assert report['exit_code'] == 0
    rows = report['occurrence_origins']
    keys = [(row['origin']['kind'], row['origin']['reference_id'] or '', row['fact_type'], row['index']) for row in rows]
    assert keys == sorted(keys)

def test_known_reference_binding_failure_uses_empty_successor_wrapper(tmp_path):
    root = tmp_path / 'dispatch'
    shutil.copytree(ROOT / 'tests/fixtures/v71/phase2/dispatch', root)
    (root / 'references/catalog.pop.json').write_bytes(b'{}\n')
    report = api.validate(root / 'model.orm.yaml')
    assert report['exit_code'] == 3
    assert report['schema_version'] == 12
    assert report['model_digest'] is None
    assert report['reference_binding']['references'] == []
    assert report['occurrence_origins'] == []

def test_mutated_nonfinite_reference_identity_refuses_as_input(tmp_path):
    from gnd.model import load_model
    from gnd.population import load_population
    root = tmp_path / 'dispatch'
    shutil.copytree(ROOT / 'tests/fixtures/v71/phase2/dispatch', root)
    model = load_model(root / 'model.orm.yaml')
    population = load_population(root / 'candidate.pop.json', model=model)
    model.source['cost'] = float('nan')
    assert api.check(model, population)['exit_code'] == 3

def test_transition_candidate_cannot_repeat_fixed_relation(tmp_path):
    from support.reference_cases import _bundle, _operation, _save

    from gnd.model import load_model
    from gnd.transition import model_digest, operations_digest
    bundle = _bundle('dispatch', tmp_path / 'dispatch')
    bundle['model']['operations'] = [_operation(bundle)]
    bundle['candidate']['facts'][bundle['ids']['catalog']] = []
    _save(bundle)
    model = load_model(bundle['root'] / 'model.orm.yaml')
    steps = {'steps_schema': 1, 'model': 'model.orm.yaml', 'model_digest': model_digest(model), 'operations_digest': operations_digest(model.operations), 'steps': [{'op': 'read_catalog', 'bindings': {'subject': bundle['ids']['subject_value'], 'left': bundle['ids']['left_value'], 'right': bundle['ids']['right_value']}}]}
    report = api.transition(model, bundle['root'] / 'candidate.pop.json', steps)
    assert report['exit_code'] == 3
    assert report['occurrence_origins'] == []

def test_mutable_combined_flag_cannot_bypass_reference_binding(tmp_path):
    from gnd import checker
    from gnd.model import load_model
    from gnd.population import load_population
    root = tmp_path / 'dispatch'
    shutil.copytree(ROOT / 'tests/fixtures/v71/phase2/dispatch', root)
    model = load_model(root / 'model.orm.yaml')
    candidate = load_population(root / 'candidate.pop.json', model=model)
    normal = checker.band(checker.check(model, candidate))
    candidate._reference_combined = True
    assert checker.band(checker.check(model, candidate)) == normal == 0

def test_deontic_dirty_presentation_producer_cannot_return_clean(tmp_path, monkeypatch):
    from support.reference_cases import _bundle, _save

    from gnd import checker
    bundle = _bundle('dispatch', tmp_path / 'dispatch')
    bundle['model']['constraints'][0]['modality'] = 'deontic'
    _save(bundle)
    original = checker._guarded_bindings

    def dirty_bindings(*args, **kwargs):
        return original(*args, **kwargs) * 100001
    monkeypatch.setattr(checker, '_guarded_bindings', dirty_bindings)
    report = api.check(bundle['root'] / 'model.orm.yaml', bundle['root'] / 'candidate.pop.json')
    assert report['exit_code'] == 4

def test_reference_diff_default_text_cli_uses_embedded_report():
    import subprocess
    import sys
    model = ROOT / 'tests/fixtures/v71/phase2/dispatch/model.orm.yaml'
    result = subprocess.run([sys.executable, '-m', 'gnd', 'diff', str(model), str(model)], capture_output=True, text=True, check=False, timeout=30)
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith('DIFF sha256:')

def test_deontic_dirty_presentation_admission_retains_provenance(tmp_path, monkeypatch):
    from support.reference_cases import _bundle, _save

    from gnd import checker
    bundle = _bundle('dispatch', tmp_path / 'dispatch')
    bundle['model']['constraints'][0]['modality'] = 'deontic'
    _save(bundle)
    original = checker._guarded_bindings

    def dirty_bindings(*args, **kwargs):
        return original(*args, **kwargs) * 100001
    monkeypatch.setattr(checker, '_guarded_bindings', dirty_bindings)
    report = api.check(bundle['root'] / 'model.orm.yaml', bundle['root'] / 'candidate.pop.json', admission=True)
    assert report['exit_code'] == 4
    assert len(report['report']['admission']['blocked']) == 2

def test_legacy_model_file_symlink_keeps_historical_loading(tmp_path):
    from gnd.model import load_model
    target = tmp_path / 'model.yaml'
    target.write_text('version: 3\nobject_types: []\nfact_types: []\n')
    link = tmp_path / 'linked.yaml'
    link.symlink_to(target.name)
    assert load_model(link).version == 3

def test_legacy_model_parent_symlink_keeps_historical_loading(tmp_path):
    from gnd.model import load_model
    root = tmp_path / 'real'
    root.mkdir()
    (root / 'model.yaml').write_text('version: 3\nobject_types: []\nfact_types: []\n')
    link = tmp_path / 'linked'
    link.symlink_to(root.name, target_is_directory=True)
    assert load_model(link / 'model.yaml').version == 3

def test_reference_resource_scope_does_not_enlarge_legacy_assurance():
    base = ROOT / 'tests/fixtures/v62-phase3'
    report = api.check(base / 'models/exact-terms.orm.yaml', base / 'populations/term-clean.pop.yaml')
    assert report['exit_code'] == 0
    assert 'snapshot:guarded:n-a:unchecked-reference-join-work-limit' not in report['assurance']['uncovered_applicable_scope_ids']

def test_combined_flag_cannot_hide_candidate_owned_reference_assertions(tmp_path):
    import pytest
    from support.reference_cases import _bundle, _save

    from gnd import checker
    from gnd.model import load_model
    from gnd.population import load_population
    from gnd.references import ReferenceInputError
    bundle = _bundle('dispatch', tmp_path / 'dispatch')
    ids = bundle['ids']
    bundle['candidate']['facts'][ids['catalog']] = bundle['catalog']['facts'][ids['catalog']]
    bundle['candidate']['population']['covers'].append(ids['catalog'])
    _save(bundle)
    model = load_model(bundle['root'] / 'model.orm.yaml')
    candidate = load_population(bundle['root'] / 'candidate.pop.json', model=model)
    candidate._reference_combined = True
    with pytest.raises(ReferenceInputError, match='candidate'):
        checker.check(model, candidate)

def test_computed_post_origins_cover_new_candidate_rows_without_fixed_output(tmp_path):
    from support.reference_cases import _bundle, _operation, _save

    from gnd.model import load_model
    from gnd.transition import model_digest, operations_digest
    bundle = _bundle('dispatch', tmp_path / 'dispatch')
    bundle['model']['operations'] = [_operation(bundle)]
    _save(bundle)
    model = load_model(bundle['root'] / 'model.orm.yaml')
    steps = {'steps_schema': 1, 'model': 'model.orm.yaml', 'model_digest': model_digest(model), 'operations_digest': operations_digest(model.operations), 'steps': [{'op': 'read_catalog', 'bindings': {'subject': 'new-shipment', 'left': bundle['ids']['left_value'], 'right': bundle['ids']['right_value']}}]}
    report = api.transition(model, bundle['root'] / 'candidate.pop.json', steps)
    assert report['exit_code'] == 0
    facts = report['report']['transition']['computed_post']['facts']
    assert bundle['ids']['catalog'] not in facts
    assert len(facts[bundle['ids']['a']]) == 2
    actual = {(row['fact_type'], row['index']) for row in report['occurrence_origins'] if row['origin']['kind'] == 'candidate'}
    assert actual == {(ft, index) for ft, rows in facts.items() for index in range(len(rows))}

def test_diff_legacy_path_replacement_cannot_bypass_no_follow(tmp_path, monkeypatch):
    import pytest
    from support.reference_cases import _bundle, _save

    from gnd.diff import DiffError
    from gnd.model import load_model
    bundle = _bundle('dispatch', tmp_path / 'dispatch')
    bundle['model'].pop('reference_populations')
    bundle['model']['version'] = 3
    _save(bundle)
    path = bundle['root'] / 'model.orm.yaml'
    other = load_model(path)
    target = bundle['root'] / 'replacement.yaml'
    target.write_bytes(path.read_bytes())
    original = Path.is_symlink
    replaced = False

    def replace_after_inspection(self):
        nonlocal replaced
        result = original(self)
        if self == path and (not replaced):
            replaced = True
            self.unlink()
            self.symlink_to(target.name)
        return result
    monkeypatch.setattr(Path, 'is_symlink', replace_after_inspection)
    with pytest.raises(DiffError, match='diff:invalid-model'):
        api.diff(path, other)
    assert replaced

def test_diff_path_refuses_when_safe_descriptor_capability_is_missing(tmp_path, monkeypatch):
    import os

    import pytest
    from support.reference_cases import _bundle, _save

    from gnd.diff import DiffError
    from gnd.model import load_model
    bundle = _bundle('dispatch', tmp_path / 'dispatch')
    bundle['model'].pop('reference_populations')
    bundle['model']['version'] = 3
    _save(bundle)
    path = bundle['root'] / 'model.orm.yaml'
    other = load_model(path)
    monkeypatch.delattr(os, 'O_NOFOLLOW')
    with pytest.raises(DiffError, match='diff:invalid-model'):
        api.diff(path, other)
