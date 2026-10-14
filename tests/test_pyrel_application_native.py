"""Scoped native profile branches, executed by the isolated runtime interpreter."""
from __future__ import annotations

import copy
import json
import os
import subprocess

import pytest
from test_pyrel_application_acceptance import RUNTIME, toy

pytestmark = pytest.mark.pyrel_oracle
NATIVE = RUNTIME.parents[3] / 'tutorials/runtimes/.venv/bin/python'
RUNNER = '''
import json, os, runpy, sys
api = runpy.run_path(sys.argv[1])['acceptance_document']
assert not any(name == 'gnd' or name.startswith('gnd.') for name in sys.modules)
results = []
for case in json.load(sys.stdin):
    results.append(api(case['model'], case['population'], model_sha256='a'*64, population_sha256='b'*64))
print('RESULTS:' + json.dumps(results, sort_keys=True))
'''


def execute_cases(tmp_path, cases):
    assert NATIVE.is_file(), 'selected native gate requires the locked optional runtime'
    runtime = tmp_path / 'runtime.py'
    runtime.write_bytes(RUNTIME.read_bytes())
    env = {k: v for k, v in os.environ.items() if k not in {'PYTHONPATH', 'PYTHONHOME'}}
    env['RAI_BUILD_DIR'] = str(tmp_path / 'native-build')
    completed = subprocess.run([str(NATIVE), '-I', '-c', RUNNER, str(runtime)],
                               input=json.dumps(cases), text=True, capture_output=True,
                               cwd=tmp_path, env=env, timeout=240, check=False)
    assert completed.returncode == 0, completed.stderr
    lines = [line for line in completed.stdout.splitlines() if line.startswith('RESULTS:')]
    assert len(lines) == 1, completed.stdout
    return json.loads(lines[0][8:])


def test_guarded_native_branch_table(tmp_path):
    cases, expected = [], []

    def add(model, pop, status, witnesses):
        cases.append({'model': copy.deepcopy(model), 'population': copy.deepcopy(pop)})
        expected.append((status, witnesses))

    # Every spelling is exercised on both sides of its actual native predicate.
    for operator, good, bad in [('=', 7, 8), ('==', 7, 8), ('!=', 8, 7), ('<>', 8, 7),
                                ('<', 6, 7), ('<=', 7, 8), ('>', 8, 7), ('>=', 7, 6)]:
        for value, status in [(good, 'satisfied'), (bad, 'violated')]:
            model, pop = toy()
            model['constraints'][0]['consequent'] = {'comparison': {'operator': operator, 'left': '$y', 'right': 7}}
            pop['facts']['r'][0]['y'] = value
            add(model, pop, status, [] if status == 'satisfied' else [{'$x': 'a', '$y': value}])
    for kind, present, status in [('atom', True, 'satisfied'), ('atom', False, 'violated'),
                                  ('absence', True, 'violated'), ('absence', False, 'satisfied')]:
        model, pop = toy()
        atom = model['constraints'][0]['consequent']['atom']
        model['constraints'][0]['consequent'] = {kind: atom}
        pop['facts']['s'] = pop['facts']['s'] if present else []
        add(model, pop, status, [] if status == 'satisfied' else [{'$x': 'a', '$y': 7}])
    # Partial consequent binding is existential, including a different unbound y.
    model, pop = toy()
    model['constraints'][0]['consequent']['atom']['bind'] = {'x': '$x'}
    pop['facts']['s'][0]['y'] = 99
    add(model, pop, 'satisfied', [])
    # Shared refs across atoms; nonempty relations with zero join are clean.
    model['constraints'][0]['antecedent'].append({'fact_type': 's', 'bind': {'x': '$x', 'y': '$y'}})
    add(model, pop, 'satisfied', [])
    # Known empty antecedent and unknown coverage differ, both withhold acceptance.
    pop['facts']['r'] = []
    add(model, pop, 'vacuous', [])
    pop['population']['covers'].remove('s')
    add(model, pop, 'incomplete', [])
    # Constants only have a native marker and an empty binding witness.
    model, pop = toy()
    model['constraints'][0]['antecedent'][0]['bind'] = {'x': 'a', 'y': 7}
    model['constraints'][0]['consequent'] = {'comparison': {'operator': '<', 'left': 7, 'right': 7}}
    add(model, pop, 'violated', [{}])
    # Repeated String ref filters a role pair; duplicates yield one logical witness.
    model, pop = toy()
    for fact in model['fact_types']:
        fact['roles'][1]['object_type'] = 's'
    model['constraints'][0]['antecedent'][0]['bind'] = {'x': '$x', 'y': '$x'}
    model['constraints'][0]['consequent'] = {'absence': {'fact_type': 's', 'bind': {'x': '$x'}}}
    pop['facts'] = {'r': [{'x': 'a', 'y': 'a'}, {'x': 'a', 'y': 'a'}, {'x': 'b', 'y': 'c'}],
                    's': [{'x': 'a', 'y': 'z'}]}
    add(model, pop, 'violated', [{'$x': 'a'}])
    # Boolean typed query and equality use a native predicate, not Python truth.
    model, pop = toy()
    model['object_types'][1]['primitive'] = 'Boolean'
    pop['facts'] = {'r': [{'x': 'a', 'y': False}], 's': []}
    model['constraints'][0]['consequent'] = {'comparison': {'operator': '=', 'left': '$y', 'right': True}}
    add(model, pop, 'violated', [{'$x': 'a', '$y': False}])
    reports = execute_cases(tmp_path, cases)
    assert len(reports) == len(expected)
    for i, (report, (status, witnesses)) in enumerate(zip(reports, expected, strict=True)):
        row = report['verdicts'][0]
        assert (row['status'], row['witnesses']) == (status, witnesses), (i, report)
        assert report['accepted'] is (status == 'satisfied'), (i, report)
        assert report['exit_code'] == {'satisfied': 0, 'violated': 1, 'vacuous': 2, 'incomplete': 2}[status]


def test_native_multiple_constant_rules_and_result_ceiling(tmp_path):
    model, pop = toy()
    model['constraints'] = []
    for left, right in [(7, 7), (8, 9)]:
        model['constraints'].append({'type': 'guarded', 'antecedent': [{'fact_type': 'r', 'bind': {'x': 'a', 'y': 7}}],
                                     'consequent': {'comparison': {'operator': '<', 'left': left, 'right': right}}})
    report = execute_cases(tmp_path, [{'model': model, 'population': pop}])[0]
    assert [r['status'] for r in report['verdicts']] == ['violated', 'satisfied'], report
    assert report['verdicts'][0]['witnesses'] == [{}]


def test_native_result_ceiling_on_real_join(tmp_path):
    model, pop = toy()
    model['constraints'][0]['antecedent'].append({'fact_type': 's', 'bind': {'x': '$a', 'y': '$b'}})
    model['constraints'][0]['consequent'] = {'comparison': {'operator': '=', 'left': '$y', 'right': 7}}
    pop['facts'] = {name: [{'x': f'x{i}', 'y': 7} for i in range(101)] for name in ['r', 's']}
    report = execute_cases(tmp_path, [{'model': model, 'population': pop}])[0]
    assert report['status'] == 'incomplete' and not report['accepted'], report
    assert report['verdicts'][0]['reason'] == 'native-result-tuple-limit'


@pytest.mark.parametrize('damage', ['clean', 'value', 'subset', 'mandatory', 'empty'])
def test_native_legacy_families_in_acceptance_profile(tmp_path, damage):
    model, pop = toy()
    model['fact_types'][0]['constraints'] = [{'type': 'uniqueness', 'roles': ['x']},
                                           {'type': 'mandatory', 'role': 'x'}]
    model['constraints'] = [{'type': 'value', 'object_type': 'n', 'allowed': [7]},
                            {'type': 'subset', 'subset_role_seq': [{'fact_type': 'r', 'role': 'x'}],
                             'superset_role_seq': [{'fact_type': 's', 'role': 'x'}]}]
    if damage == 'value':
        pop['facts']['r'][0]['y'] = 8
    elif damage == 'subset':
        pop['facts']['s'] = []
    elif damage == 'mandatory':
        pop['instances'] = {'s': ['missing']}
    elif damage == 'empty':
        pop['facts'] = {'r': [], 's': []}
    report = execute_cases(tmp_path, [{'model': model, 'population': pop}])[0]
    statuses = [row['status'] for row in report['verdicts']]
    if damage == 'clean':
        assert report['accepted'] and statuses == ['satisfied'] * 4, report
    elif damage == 'empty':
        assert report['status'] == 'incomplete' and statuses == ['vacuous'] * 4, report
    else:
        assert report['status'] == 'rejected' and 'violated' in statuses, report


@pytest.mark.parametrize('case', ['basics_pass', 'basics_fail'])
def test_native_default_report_retains_frozen_legacy_bytes(tmp_path, case):
    from test_public_pyrel_export_runtime_support import (
        ANSWERS,
        BASICS,
        REPO,
        assert_report,
        execute,
        export,
    )
    program = export(tmp_path, BASICS)
    out = tmp_path / 'report.json'
    result = execute(program, REPO / f'tests/fixtures/pyrel-oracle/population.{case}.yaml',
                     out, python=str(NATIVE))
    assert result.returncode == 0, result.stderr  # Legacy violations still complete the audit.
    assert_report(json.loads(out.read_text()), json.loads((ANSWERS / f'{case}.report.json').read_text()))
