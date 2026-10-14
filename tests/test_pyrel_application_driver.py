"""Discriminating false-acceptance controls for the native corpus verifier."""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('pa_driver', ROOT / 'tools/measure_pyrel_applications.py')
DRIVER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DRIVER)


def test_target_only_false_acceptance_cannot_match(monkeypatch):
    matrix = json.loads((DRIVER.CORPUS / 'matrix.json').read_text())
    answers = json.loads((DRIVER.CORPUS / 'answers.json').read_text())

    def fake_run(argv, **kwargs):
        if '-c' in argv:
            return subprocess.CompletedProcess(argv, 0, json.dumps({'python': '3.13.12',
                'relationalai': '1.30.1', 'duckdb': '1.5.5'}), '')
        if '-m' in argv:
            Path(argv[argv.index('--out') + 1]).write_text('# trusted fake export')
            return subprocess.CompletedProcess(argv, 0, '', '')
        if '--out' in argv:
            output = Path(argv[argv.index('--out') + 1])
            name = output.stem
            case = matrix['cases'][name]
            expected = {'pass': 'satisfied', 'fail': 'violated', 'warning': 'warning'}
            row = {'constraint_ref': case['target'], 'status': expected[case['expected']]}
            report = {'schema_version': 1, 'profile': 'applications-v1', 'accepted': False,
                      'status': 'rejected', 'exit_code': 1,
                      'binding': {'model_sha256': '0' * 64, 'population_sha256': '0' * 64},
                      'verdicts': [], 'derivations': []}
            if case['target'].startswith('derivation:'):
                report['derivations'] = [{'derivation_ref': case['target'], 'status': row['status']}]
            else:
                report['verdicts'] = [row]
            output.write_text(json.dumps(report))
            return subprocess.CompletedProcess(argv, 1, '', '')
        raise AssertionError(argv)

    monkeypatch.setattr(DRIVER.subprocess, 'run', fake_run)
    result = DRIVER.measure('acceptance', ROOT / 'tutorials/runtimes/.venv/bin/python')
    assert result['matched'] == 0, 'correct target rows cannot launder wrong binding/overall result'
    assert result['denominator'] == len(answers)


def valid_report(name):
    matrix = json.loads((DRIVER.CORPUS / 'matrix.json').read_text())
    answer = json.loads((DRIVER.CORPUS / 'answers.json').read_text())[name]
    case = matrix['cases'][name]
    model = json.loads((ROOT / case['model']).read_text())
    entries = [(f"fact_types[{f['id']}].constraints[{i}]", c)
               for f in model['fact_types'] for i, c in enumerate(f.get('constraints', []))]
    entries += [(f'constraints[{i}]', c) for i, c in enumerate(model.get('constraints', []))]
    report = {'schema_version': 1, 'profile': 'applications-v1', 'backend': 'duckdb-local',
              **answer['expected_acceptance'],
              'binding': {'model_sha256': 'a' * 64, 'population_sha256': 'b' * 64},
              'verdicts': [{'constraint_ref': ref, 'modality': c.get('modality', 'alethic'),
                            'status': answer['expected_native_verdicts'][ref],
                            'id': c.get('id', ref), 'constraint_type': c['type'], 'reason': None,
                            'witnesses': answer['expected_native_guarded_witnesses'].get(ref, [])}
                           for ref, c in entries],
              'derivations': [{'derivation_ref': ref, 'status': answer['expected_native_verdicts'][ref],
                               **rows} for ref, rows in answer['expected_native_derivations'].items()]}
    population = json.loads((ROOT / case['population']).read_text())
    expected_computed = {}
    for row in report['derivations']:
        ref = row['derivation_ref']; name = ref.split(':', 1)[1]
        values = {json.dumps(value, sort_keys=True): value for value in population['facts'][name] + row['missing']}
        for value in row['extra']:
            values.pop(json.dumps(value, sort_keys=True), None)
        row.update(fact_type=name, computed=[values[key] for key in sorted(values)], reason=None)
        expected_computed[ref] = row['computed']
    answer = {**answer, 'expected_native_computed': expected_computed}
    return report, answer, model


def test_full_acceptance_checker_discriminates_each_boundary():
    import copy

    for name in ['m0-r0-positive', 'm0-r4-negative', 'm1-r4-negative', 'm2-book_is_eligible-extra']:
        report, answer, model = valid_report(name)
        code = answer['expected_acceptance']['exit_code']
        assert DRIVER.check_acceptance(report, code, answer, model, 'a' * 64, 'b' * 64) == []
        mutants = []
        for key, value in [('accepted', not report['accepted']), ('status', 'invented'),
                           ('exit_code', 70), ('schema_version', True), ('backend', 'remote')]:
            changed = copy.deepcopy(report)
            changed[key] = value
            mutants.append(changed)
        for change in ['binding', 'drop-row', 'duplicate', 'modality', 'other-verdict']:
            changed = copy.deepcopy(report)
            if change == 'binding':
                changed['binding']['population_sha256'] = 'c' * 64
            elif change == 'drop-row':
                changed['verdicts'].pop()
            elif change == 'duplicate':
                changed['verdicts'].append(changed['verdicts'][0])
            elif change == 'modality':
                changed['verdicts'][0]['modality'] = 'deontic'
            else:
                changed['verdicts'][0]['status'] = 'error'
            mutants.append(changed)
        changed = copy.deepcopy(report)
        changed['verdicts'][-1]['witnesses'] = [{'invented': 1}]
        mutants.append(changed)
        if report['derivations']:
            changed = copy.deepcopy(report)
            changed['derivations'][-1]['extra'] = []
            mutants.append(changed)
        for changed in mutants:
            assert DRIVER.check_acceptance(changed, code, answer, model, 'a' * 64, 'b' * 64)
        assert DRIVER.check_acceptance(report, 64, answer, model, 'a' * 64, 'b' * 64)


def test_wrong_row_placement_and_identity_cannot_pass():
    import copy

    report, answer, model = valid_report('m0-r4-negative')
    changed = copy.deepcopy(report)
    changed['derivations'] = [{**r, 'derivation_ref': r['constraint_ref']} for r in report['verdicts']]
    changed['verdicts'] = []
    assert DRIVER.check_acceptance(changed, 0, answer, model, 'a' * 64, 'b' * 64)
    for key in ['id', 'constraint_type', 'reason', 'witnesses']:
        changed = copy.deepcopy(report)
        del changed['verdicts'][0][key]
        assert DRIVER.check_acceptance(changed, 0, answer, model, 'a' * 64, 'b' * 64)


def test_nonobject_invalid_and_oversized_reports_are_recordable(tmp_path):
    _report, answer, model = valid_report('m0-r0-positive')
    path = tmp_path / 'report.json'
    for raw in ['null', '[]', '{', ' ' * (4 * 1024 * 1024 + 1)]:
        path.write_text(raw)
        value, diagnostics = DRIVER.read_native_report(path)
        assert DRIVER.check_acceptance(value, 0, answer, model, 'a' * 64, 'b' * 64) or diagnostics
    assert DRIVER.read_native_report(tmp_path / 'missing.json')[1]


def test_snapshot_hash_changes_refuse_before_native_execution(monkeypatch):
    original = DRIVER.read_bounded

    def changed(path, limit=1048576):
        raw = original(path, limit)
        return raw + b' ' if path.name == 'answers.json' else raw

    monkeypatch.setattr(DRIVER, 'read_bounded', changed)
    import pytest
    with pytest.raises(ValueError, match='approved snapshot'):
        DRIVER.approved_corpus()


def test_agreement_counts_actual_rows_and_exact_two_exclusions():
    import copy
    answers = json.loads((DRIVER.CORPUS / 'answers.json').read_text())
    approved = json.loads((DRIVER.CORPUS / 'approval.json').read_text())['intentional_disagreements']
    records = []
    for name, answer in answers.items():
        verdicts, derivations = [], []
        for ref, status in answer['expected_native_verdicts'].items():
            (derivations if ref.startswith('derivation:') else verdicts).append({
                'derivation_ref' if ref.startswith('derivation:') else 'constraint_ref': ref, 'status': status})
        records.append({'case': name, 'report': {'verdicts': verdicts, 'derivations': derivations},
                        'process_exit': answer['expected_acceptance']['exit_code'],
                        'population_sha256': 'a' * 64})
    function = getattr(DRIVER, 'agreement', None)
    assert callable(function), 'row agreement accounting is not implemented'
    result = function(records, answers, approved)
    assert result['native_obligation_rows'] == 2323
    assert result['comparable_rows'] == result['compared_rows'] == result['matches'] == 2321
    assert len(result['intentional_disagreements']) == 2
    assert result['business_rejections_agree'] is True
    for damage in ['unlisted', 'missing-exclusion', 'extra-exclusion', 'missing-row', 'duplicate-case', 'business-exit']:
        dirty = copy.deepcopy(records); exclusions = copy.deepcopy(approved)
        if damage == 'unlisted':
            dirty[0]['report']['verdicts'][0]['status'] = 'violated'
        elif damage == 'missing-exclusion':
            exclusions.pop('m2-eligible-joint-omission')
        elif damage == 'extra-exclusion':
            exclusions['m0-r0-positive'] = {'constraints[0]': 'unapproved'}
        elif damage == 'missing-row':
            dirty[0]['report']['verdicts'].pop()
        elif damage == 'business-exit':
            dirty[0]['process_exit'] = 1
        else:
            dirty.append(copy.deepcopy(dirty[0]))
        import pytest
        with pytest.raises(ValueError):
            function(dirty, answers, exclusions)


def test_computed_derivation_identity_and_values_cannot_be_laundered():
    import copy
    report, answer, model = valid_report('m2-book_is_eligible-extra')
    assert DRIVER.check_acceptance(report, 1, answer, model, 'a' * 64, 'b' * 64) == []
    for key, value in [('fact_type', 'invented'), ('computed', []), ('reason', 'invented')]:
        dirty = copy.deepcopy(report)
        dirty['derivations'][-1][key] = value
        assert DRIVER.check_acceptance(dirty, 1, answer, model, 'a' * 64, 'b' * 64), key


def test_missing_computed_expected_key_cannot_silently_skip_verification():
    report, answer, model = valid_report('m2-book_is_eligible-extra')
    del answer['expected_native_computed']
    assert DRIVER.check_acceptance(report, 1, answer, model, 'a' * 64, 'b' * 64)


def test_measurement_rejects_changed_runtime_snapshot(monkeypatch):
    import pytest
    matrix = json.loads((DRIVER.CORPUS / 'matrix.json').read_text())
    original = DRIVER.read_bounded
    reads = 0
    def changed(path, limit=1048576):
        nonlocal reads
        raw = original(path, limit)
        if path == ROOT / 'src/gnd/export/pyrel_runtime.py':
            reads += 1
            if reads > 1:
                return raw + b' '
        return raw
    def fake_run(argv, **_kwargs):
        if '-c' in argv:
            return subprocess.CompletedProcess(argv, 0, json.dumps({'python': '3.13.12', 'relationalai': '1.30.1', 'duckdb': '1.5.5'}), '')
        output = Path(argv[argv.index('--out') + 1])
        if '-m' in argv:
            output.write_text('# fake export')
            return subprocess.CompletedProcess(argv, 0, '', '')
        report, answer, _ = valid_report(output.stem)
        case = matrix['cases'][output.stem]
        report['binding'] = {'model_sha256': DRIVER.sha(original(ROOT / case['model'])),
                             'population_sha256': DRIVER.sha(original(ROOT / case['population']))}
        output.write_text(json.dumps(report))
        return subprocess.CompletedProcess(argv, answer['expected_acceptance']['exit_code'], '', '')
    monkeypatch.setattr(DRIVER, 'read_bounded', changed)
    monkeypatch.setattr(DRIVER.subprocess, 'run', fake_run)
    with pytest.raises(ValueError, match='changed during execution'):
        DRIVER.measure('acceptance', ROOT / 'tutorials/runtimes/.venv/bin/python', 'guarded')
