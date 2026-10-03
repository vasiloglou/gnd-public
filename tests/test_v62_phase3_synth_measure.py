from __future__ import annotations

import contextlib
import copy
import io
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from ruamel.yaml import YAML
from support.v62_phase3_corpus import FIXTURE, population_document

from gnd.checker import DynamicRefreshWork, RelationUnavailable, StructuredExtensionView
from gnd.cli import main
from gnd.measure.report import load_measurement_schema, render_measurement
from gnd.model import load_model
from gnd.synth import assemble as assemble_module
from gnd.synth.assemble import GeneratorError, _materialize_structured_claims, assemble_conforming


def _synth_model(tmp_path: Path, *, redacted: bool=True) -> Path:
    yaml = YAML(typ='safe')
    document = yaml.load((FIXTURE / 'models/exact-terms.orm.yaml').read_text(encoding='utf-8'))
    document['constraints'] = []
    document['operations'] = []
    if not redacted:
        for fact_type in document['fact_types']:
            for role in fact_type.get('roles', []):
                role.pop('redact', None)
    path = tmp_path / 'exact-synth.orm.yaml'
    writer = YAML()
    with path.open('w', encoding='utf-8') as stream:
        writer.dump(document, stream)
    return path

def _run_synth(model: Path, out: Path) -> None:
    assert main(['synth', str(model), '--class', 'conforming', '--seed', '7', '--out', str(out), '--format', 'json']) == 0

def test_s01_s02_exact_synth_converges_reproducibly(tmp_path: Path) -> None:
    model = _synth_model(tmp_path)
    left, right = (tmp_path / 'left', tmp_path / 'right')
    with contextlib.redirect_stdout(io.StringIO()):
        _run_synth(model, left)
        _run_synth(model, right)
    left_population = next(path for path in (left / 'conforming').glob('*.conforming.seed*.json') if not path.name.endswith('.meta.json'))
    right_population = next(path for path in (right / 'conforming').glob('*.conforming.seed*.json') if not path.name.endswith('.meta.json'))
    assert left_population.read_bytes() == right_population.read_bytes()
    facts = json.loads(left_population.read_text(encoding='utf-8'))['facts']
    assert facts['residue']
    assert facts['doubled_residue']

def test_s03_zero_divisor_synth_has_named_bounded_failure() -> None:
    model = load_model(FIXTURE / 'models/exact-terms.orm.yaml')
    with pytest.raises(GeneratorError, match='term-generation-did-not-converge.*term:mod-zero') as failure:
        _materialize_structured_claims(population_document(), model)
    assert 'residue' in str(failure.value)

def test_s03_assemble_retries_after_an_unavailable_exact_candidate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    model = load_model(_synth_model(tmp_path))
    production_view = assemble_module.structured_extension_view
    calls = 0

    def unavailable_once(model_arg, population_arg):
        nonlocal calls
        calls += 1
        if calls == 1:
            return StructuredExtensionView(facts={}, recomputed=('residue',), work=DynamicRefreshWork(selected_heads=1, strata_evaluated=1), unavailable={'residue': RelationUnavailable('residue', 'term:mod-zero', {'value': 7, 'divisor': 0})})
        return production_view(model_arg, population_arg)
    monkeypatch.setattr(assemble_module, 'structured_extension_view', unavailable_once)
    assembly = assemble_conforming(model, 7, max_rounds=3)
    assert calls == 2
    assert assembly.rounds == 2
    assert assembly.doc['facts']['residue']

def test_s03_assemble_exhausts_the_explicit_unavailable_candidate_budget(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    model = load_model(_synth_model(tmp_path))
    calls = 0

    def always_unavailable(_model_arg, _population_arg):
        nonlocal calls
        calls += 1
        return StructuredExtensionView(facts={}, recomputed=('residue',), work=DynamicRefreshWork(selected_heads=1, strata_evaluated=1), unavailable={'residue': RelationUnavailable('residue', 'term:mod-zero', {'value': 7, 'divisor': 0})})
    monkeypatch.setattr(assemble_module, 'structured_extension_view', always_unavailable)
    with pytest.raises(GeneratorError, match='term-generation-did-not-converge.*term:mod-zero.*attempts=3'):
        assemble_conforming(model, 7, max_rounds=3)
    assert calls == 3

def test_m01_m04_measurement_names_unmutated_derivations(tmp_path: Path) -> None:
    model = _synth_model(tmp_path)
    corpus = tmp_path / 'corpus'
    with contextlib.redirect_stdout(io.StringIO()):
        _run_synth(model, corpus)
    measurement = tmp_path / 'measurement.json'
    assert main(['measure', str(model), '--populations', str(corpus), '--format', 'json', '--out', str(measurement)]) == 0
    payload = json.loads(measurement.read_text(encoding='utf-8'))
    rows = payload['coverage_summary']['unmutated_derivations']
    assert rows == [{'derivation_ref': 'derivation:doubled_residue', 'reason': 'structured-derivation-mutation-unsupported'}, {'derivation_ref': 'derivation:permitted', 'reason': 'structured-derivation-mutation-unsupported'}, {'derivation_ref': 'derivation:residue', 'reason': 'structured-derivation-mutation-unsupported'}]
    rendered = render_measurement(payload)
    assert rendered.count('UNMUTATED derivation:') == 3
    assert payload['coverage_summary']['constraint_count'] == len(payload['per_constraint'])
    assert payload['coverage_summary']['constraint_count'] == 1
    measured = payload['per_constraint'][0]
    assert measured['n'] == sum(measured['cells'].values())
    assert measured['false_pass_rate'] == (measured['false_pass'] / measured['expected_nonpass'] if measured['expected_nonpass'] else None)
    assert measured['false_fail_rate'] == (measured['false_fail'] / measured['satisfied'] if measured['satisfied'] else None)
    for row in rows:
        assert row['derivation_ref'] in rendered
        assert row['reason'] in rendered
    validator = Draft202012Validator(load_measurement_schema())
    assert not list(validator.iter_errors(payload))
    missing = copy.deepcopy(payload)
    del missing['coverage_summary']['unmutated_derivations']
    extra = copy.deepcopy(payload)
    extra['coverage_summary']['unmutated_derivations'][0]['unexpected'] = True
    assert list(validator.iter_errors(missing))
    assert list(validator.iter_errors(extra))

def test_measurement_v3_summary_is_required_without_redaction(tmp_path: Path) -> None:
    model = _synth_model(tmp_path, redacted=False)
    corpus = tmp_path / 'corpus'
    with contextlib.redirect_stdout(io.StringIO()):
        _run_synth(model, corpus)
    measurement = tmp_path / 'measurement.json'
    assert main(['measure', str(model), '--populations', str(corpus), '--format', 'json', '--out', str(measurement)]) == 0
    payload = json.loads(measurement.read_text(encoding='utf-8'))
    assert payload['schema_version'] == 3
    assert payload['redaction'] == {'mode': 'applied', 'declarations': []}
    assert payload['coverage_summary']['unmutated_derivations']
    missing = copy.deepcopy(payload)
    del missing['coverage_summary']['unmutated_derivations']
    validator = Draft202012Validator(load_measurement_schema())
    assert not list(validator.iter_errors(payload))
    assert list(validator.iter_errors(missing))
