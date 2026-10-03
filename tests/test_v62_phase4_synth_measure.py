from __future__ import annotations

import contextlib
import copy
import io
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from ruamel.yaml import YAML
from support.v62_phase4_corpus import CASES_DOC, FIXTURE, document

from gnd.checker import CheckReport
from gnd.cli import main
from gnd.measure.report import load_measurement_schema, render_measurement
from gnd.model import Model, semantic_validate
from gnd.synth import assemble as assemble_module
from gnd.synth.assemble import CheckerWitnessDiscrepancy, GeneratorError, assemble_conforming


def test_s01_s02_s04_m01_m02_m03_m04_m05_aggregate_measurement_is_honest(tmp_path: Path) -> None:
    model_document = copy.deepcopy(document())
    model_document['constraints'] = []
    model_document['operations'] = []
    for fact_type in model_document['fact_types']:
        for role in fact_type.get('roles', []):
            role.pop('redact', None)
    model_path = tmp_path / 'aggregates.orm.yaml'
    with model_path.open('w', encoding='utf-8') as stream:
        YAML().dump(model_document, stream)
    corpus = tmp_path / 'corpus'
    original_model_bytes = model_path.read_bytes()
    with contextlib.redirect_stdout(io.StringIO()):
        assert main(['synth', str(model_path), '--class', 'conforming', '--seed', '7', '--out', str(corpus), '--format', 'json']) == 0
    assert model_path.read_bytes() == original_model_bytes
    generated = next(path for path in (corpus / 'conforming').glob('*.conforming.seed*.json') if not path.name.endswith('.meta.json'))
    generated_facts = json.loads(generated.read_text(encoding='utf-8'))['facts']
    assert generated_facts['scenario_count']
    assert generated_facts['scenario_sum']
    assert generated_facts['scenario_min']
    assert generated_facts['scenario_max']
    repeat = tmp_path / 'repeat'
    with contextlib.redirect_stdout(io.StringIO()):
        assert main(['synth', str(model_path), '--class', 'conforming', '--seed', '7', '--out', str(repeat), '--format', 'json']) == 0
    repeated = next(path for path in (repeat / 'conforming').glob('*.conforming.seed*.json') if not path.name.endswith('.meta.json'))
    assert generated.read_bytes() == repeated.read_bytes()
    report_path = tmp_path / 'measurement.json'
    with contextlib.redirect_stdout(io.StringIO()):
        assert main(['measure', str(model_path), '--populations', str(corpus), '--format', 'json', '--out', str(report_path)]) == 0
    payload = json.loads(report_path.read_text(encoding='utf-8'))
    assert payload['schema_version'] == 3
    rows = payload['coverage_summary']['unmutated_derivations']
    assert any(row['derivation_ref'] == 'derivation:scenario_count' for row in rows)
    assert {(row['derivation_ref'], row['reason']) for row in rows if row['derivation_ref'].startswith('derivation:scenario_')} >= {('derivation:scenario_count', 'aggregate:count-mutation-unsupported'), ('derivation:scenario_sum', 'aggregate:sum-mutation-unsupported'), ('derivation:scenario_mean_ok', 'aggregate:avg-mutation-unsupported')}
    assert {row['reason'] for row in rows if row['reason'].startswith('aggregate:')} == {'aggregate:count-mutation-unsupported', 'aggregate:sum-mutation-unsupported', 'aggregate:min-mutation-unsupported', 'aggregate:max-mutation-unsupported', 'aggregate:avg-mutation-unsupported'}
    assert all(not row['derivation_ref'].startswith('derivation:scenario_') for row in payload['per_constraint'])
    text = render_measurement(payload)
    for row in rows:
        assert row['derivation_ref'] in text
        assert row['reason'] in text
    assert not list(Draft202012Validator(load_measurement_schema()).iter_errors(payload))
    missing = copy.deepcopy(payload)
    del missing['coverage_summary']['unmutated_derivations']
    assert list(Draft202012Validator(load_measurement_schema()).iter_errors(missing))
    sidecar_path = generated.with_suffix('.meta.json')
    sidecar = json.loads(sidecar_path.read_text(encoding='utf-8'))
    sidecar['unmutated_derivations'] = [row for row in sidecar['unmutated_derivations'] if row['derivation_ref'] != 'derivation:scenario_count']
    sidecar_path.write_text(json.dumps(sidecar, sort_keys=True) + '\n', encoding='utf-8')
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exit_code = main(['measure', str(model_path), '--populations', str(corpus), '--format', 'json', '--out', str(tmp_path / 'omitted-measurement.json')])
    assert exit_code == 3
    assert 'unmutated_derivations' in output.getvalue()

def test_s03_s07_full_story_synth_refuses_missing_independent_guarded_oracle(tmp_path: Path) -> None:
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exit_code = main(['synth', str(FIXTURE / CASES_DOC['model']), '--class', 'conforming', '--seed', '7', '--out', str(tmp_path / 'corpus'), '--format', 'json'])
    assert exit_code == 5
    payload = json.loads(output.getvalue())
    assert payload['exit_code'] == 5
    assert 'no independent expected-state oracle' in payload['error']
    assert 'constraints[0] [guarded]' in payload['error']

def _aggregate_uniqueness_model(modality: str) -> Model:
    model_document = copy.deepcopy(document())
    model_document['constraints'] = []
    model_document['operations'] = []
    for fact_type in model_document['fact_types']:
        for role in fact_type.get('roles', []):
            role.pop('redact', None)
    model_document['fact_types'][0]['constraints'] = [{'type': 'uniqueness', 'roles': ['scenario'], 'source': 'explicit', 'status': 'confirmed', 'modality': modality, 'provenance': {'user_quote': 'A scenario has one observation.'}}]
    assert semantic_validate(model_document) == []
    return Model.model_validate(model_document)

def _duplicate_scenario(doc: dict) -> None:
    rows = doc['facts']['observation']
    assert rows
    duplicate = dict(rows[0])
    duplicate['sample'] = str(duplicate['sample']) + '-different'
    rows.append(duplicate)

def test_s05_alethic_aggregate_model_fault_is_synthesis_fatal() -> None:
    model = _aggregate_uniqueness_model('alethic')
    with pytest.raises(GeneratorError, match='alethic constructive witness'):
        assemble_conforming(model, 7, model_ref='aggregate.orm.yaml', fault=_duplicate_scenario)

def test_s06_deontic_aggregate_model_fault_is_advisory() -> None:
    model = _aggregate_uniqueness_model('deontic')
    assembly = assemble_conforming(model, 7, model_ref='aggregate.orm.yaml', fault=_duplicate_scenario)
    assert assembly.witnesses['fact_types[observation].constraints[0]'] is False

def test_s08_aggregate_model_checker_disagreement_is_quarantined(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    model = _aggregate_uniqueness_model('alethic')
    real_check = assemble_module.check
    target = 'fact_types[observation].constraints[0]'

    def lying_check(model_arg, population):
        report = real_check(model_arg, population)
        verdicts = [row.model_copy(update={'verdict': 'fail', 'scope_id': 'snapshot:uniqueness:inline:violated:alethic'}) if row.constraint_ref == target and row.verdict == 'pass' else row for row in report.verdicts]
        return CheckReport(verdicts=verdicts, coverage=report.coverage)
    monkeypatch.setattr(assemble_module, 'check', lying_check)
    with pytest.raises(CheckerWitnessDiscrepancy) as caught:
        assemble_conforming(model, 7, model_ref='aggregate.orm.yaml')
    assert caught.value.discrepancies[0]['constraint_ref'] == target
    model_path = tmp_path / 'aggregate.orm.yaml'
    with model_path.open('w', encoding='utf-8') as stream:
        YAML().dump(model.model_dump(exclude={'warnings'}), stream)
    corpus = tmp_path / 'corpus'
    with contextlib.redirect_stdout(io.StringIO()):
        assert main(['synth', str(model_path), '--class', 'conforming', '--seed', '7', '--out', str(corpus), '--format', 'json']) == 6
    assert list((corpus / 'quarantine').glob('*.discrepancy.json'))
