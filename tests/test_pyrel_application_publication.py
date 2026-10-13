"""Red-first parent acceptance/publication boundaries for PA3."""
import copy
import hashlib
import importlib
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / 'src/gnd/examples/bookrec/model.orm.yaml'
POP = ROOT / 'src/gnd/examples/bookrec/seed.population.json'


def application():
    assert importlib.util.find_spec('gnd.export.applications') is not None, 'native publication parent is absent'
    module = importlib.import_module('gnd.export.applications')
    assert callable(getattr(module, 'execute_application', None))
    assert callable(getattr(module, 'verify_policy_report', None))
    return module


def valid_policy():
    doc = json.loads(MODEL.read_text())
    entries = [(f"fact_types[{f['id']}].constraints[{i}]", c)
               for f in doc['fact_types'] for i, c in enumerate(f.get('constraints', []))]
    entries += [(f'constraints[{i}]', c) for i, c in enumerate(doc['constraints'])]
    policy = {'schema_version': 1, 'profile': 'applications-v1', 'backend': 'duckdb-local',
              'accepted': True, 'status': 'accepted', 'exit_code': 0,
              'binding': {'model_sha256': 'a' * 64, 'population_sha256': 'b' * 64},
              'verdicts': [{'constraint_ref': ref, 'id': c.get('id', ref), 'constraint_type': c['type'],
                            'modality': c.get('modality', 'alethic'), 'status': 'satisfied',
                            'witnesses': [], 'reason': None} for ref, c in entries], 'derivations': []}
    return doc, policy


def test_parent_requires_complete_explicit_accepted_report():
    module = application()
    doc, report = valid_policy()
    module.verify_policy_report(report, doc, 'a' * 64, 'b' * 64, 0)


@pytest.mark.parametrize('damage', ['empty', 'accepted', 'schema', 'backend', 'binding', 'missing-row',
                                   'duplicate-row', 'row-type', 'row-id', 'row-modality', 'incomplete',
                                   'error', 'vacuous', 'status', 'exit', 'reason-field', 'extra-head'])
def test_parent_rejects_each_false_publication_boundary(damage):
    module = application()
    doc, report = valid_policy(); report = copy.deepcopy(report)
    if damage == 'empty':
        report = {}
    elif damage in {'accepted', 'schema', 'backend', 'status', 'exit'}:
        key, value = {'accepted': ('accepted', False), 'schema': ('schema_version', True),
                      'backend': ('backend', 'remote'), 'status': ('status', 'rejected'),
                      'exit': ('exit_code', 70)}[damage]
        report[key] = value
    elif damage == 'binding':
        report['binding']['population_sha256'] = 'c' * 64
    elif damage == 'missing-row':
        report['verdicts'].pop()
    elif damage == 'duplicate-row':
        report['verdicts'].append(report['verdicts'][0])
    elif damage.startswith('row-'):
        key = {'row-type': 'constraint_type', 'row-id': 'id', 'row-modality': 'modality'}[damage]
        report['verdicts'][0][key] = 'invented'
    elif damage in {'incomplete', 'error', 'vacuous'}:
        report['verdicts'][0]['status'] = damage
    elif damage == 'reason-field':
        del report['verdicts'][0]['reason']
    else:
        report['derivations'] = [{'derivation_ref': 'derivation:invented', 'status': 'satisfied'}]
    with pytest.raises(ValueError):
        module.verify_policy_report(report, doc, 'a' * 64, 'b' * 64, 0)


def test_existing_output_and_input_remain_exact_on_refusal(tmp_path):
    module = application()
    source = tmp_path / 'input.json'; source.write_bytes(POP.read_bytes())
    output = tmp_path / 'output.json'; output.write_bytes(b'owner bytes')
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    result = module.execute_application(MODEL, source, output, native_python=Path('/absent/native/python'),
                                        query_script=tmp_path / 'query.py')
    assert not result['published'] and not result['accepted']
    assert source.read_bytes() == POP.read_bytes() and hashlib.sha256(source.read_bytes()).hexdigest() == before
    assert output.read_bytes() == b'owner bytes'


def simulated_child(module, monkeypatch, *, proposal_damage=None, report_damage=None, race=None):
    """Exercise publication against independently constructed child envelopes."""
    def child(argv, home):
        if Path(argv[2]).name == 'query.py':
            document = json.loads((home / 'seed.json').read_bytes())
            envelope = {'schema_version': 1, 'candidate': document, 'calculation': {'pairs': []},
                        'binding': {'model_sha256': hashlib.sha256((home / MODEL.name).read_bytes()).hexdigest(),
                                    'input_sha256': hashlib.sha256((home / 'seed.json').read_bytes()).hexdigest()}}
            raw = proposal_damage(envelope) if proposal_damage else json.dumps(envelope).encode()
            if raw is not None:
                (home / 'proposal.json').write_bytes(raw)
        else:
            _, report = valid_policy()
            report['binding'] = {'model_sha256': hashlib.sha256((home / MODEL.name).read_bytes()).hexdigest(),
                                 'population_sha256': hashlib.sha256((home / 'candidate.json').read_bytes()).hexdigest()}
            raw = report_damage(report) if report_damage else json.dumps(report).encode()
            if raw is not None:
                (home / 'policy.json').write_bytes(raw)
            if race:
                race(home)
        return SimpleNamespace(return_code=0, stderr=b'')
    monkeypatch.setattr(module, '_child', child)


def run_simulated(module, tmp_path, **options):
    source = tmp_path / 'source.json'; source.write_bytes(POP.read_bytes())
    query = tmp_path / 'query.py'; query.write_text('# owned query')
    output = tmp_path / 'result.json'
    result = module.execute_application(MODEL, source, output, native_python=Path(sys.executable),
                                        query_script=query, **options)
    return source, output, result


@pytest.mark.parametrize('boundary', ['proposal-missing', 'proposal-malformed', 'proposal-binding',
                                     'report-missing', 'report-malformed', 'report-binding',
                                     'report-partial', 'report-status'])
def test_child_artifact_refusals_withhold_output(monkeypatch, tmp_path, boundary):
    module = application()
    def damage(doc):
        if boundary.endswith('missing'):
            return None
        if boundary.endswith('malformed'):
            return b'{'
        if boundary.endswith('binding'):
            doc['binding'] = {}
        elif boundary.endswith('partial'):
            doc['verdicts'] = []
        else:
            doc['verdicts'][0]['status'] = 'incomplete'
        return json.dumps(doc).encode()
    simulated_child(module, monkeypatch, **{('proposal_damage' if boundary.startswith('proposal') else 'report_damage'): damage})
    source, output, result = run_simulated(module, tmp_path)
    assert not result['published'] and not result['accepted'] and result['exit_code'] != 0
    assert not output.exists() and source.read_bytes() == POP.read_bytes()


def test_checked_capture_is_published_despite_child_path_mutation(monkeypatch, tmp_path):
    module = application()
    simulated_child(module, monkeypatch, race=lambda home: (home / 'candidate.json').write_bytes(b'forged later bytes'))
    source, output, result = run_simulated(module, tmp_path)
    assert result['published'] and result['accepted'], result
    assert json.loads(output.read_bytes()) == json.loads(source.read_bytes())
    assert hashlib.sha256(output.read_bytes()).hexdigest() == result['policy']['binding']['population_sha256']


def test_no_clobber_race_preserves_owner_bytes(monkeypatch, tmp_path):
    module = application()
    simulated_child(module, monkeypatch, race=lambda home: (tmp_path / 'result.json').write_bytes(b'owner won'))
    source, output, result = run_simulated(module, tmp_path)
    assert not result['published'] and not result['accepted']
    assert output.read_bytes() == b'owner won' and source.read_bytes() == POP.read_bytes()


def test_changed_source_withholds_output(monkeypatch, tmp_path):
    module = application()
    simulated_child(module, monkeypatch, race=lambda home: (tmp_path / 'source.json').write_bytes(b'changed outside parent'))
    _, output, result = run_simulated(module, tmp_path)
    assert not result['published'] and not output.exists()
    assert 'source bytes changed' in result['reason']


def test_symlink_output_is_preserved(tmp_path):
    module = application()
    owner = tmp_path / 'owner'; owner.write_bytes(b'owner')
    output = tmp_path / 'result.json'; output.symlink_to(owner)
    result = module.execute_application(MODEL, POP, output, native_python=Path(sys.executable),
                                        query_script=tmp_path / 'absent')
    assert not result['published'] and output.is_symlink() and owner.read_bytes() == b'owner'


@pytest.mark.parametrize('mode', ['timeout', 'stdout', 'stderr', 'spawn'])
def test_actual_process_boundaries_refuse(monkeypatch, tmp_path, mode):
    module = application()
    limits = module.LIMITS.model_copy(update={'timeout_seconds': .15, 'stdout_limit_bytes': 32,
                                             'stderr_limit_bytes': 32, 'total_output_limit_bytes': 64})
    monkeypatch.setattr(module, 'LIMITS', limits)
    code = {'timeout': 'import time; time.sleep(3)', 'stdout': 'print("x" * 1000)',
            'stderr': 'import sys; print("x" * 1000, file=sys.stderr)', 'spawn': ''}[mode]
    argv = ['/absent/python'] if mode == 'spawn' else [sys.executable, '-I', '-c', code]
    with pytest.raises(RuntimeError, match='lifecycle refused'):
        module._child(argv, tmp_path)


def test_parent_refuses_malformed_computed_rows():
    module = application()
    doc, report = valid_policy()
    complete = json.loads(MODEL.with_name('complete.orm.yaml').read_bytes())
    # Attach the real shipped heads to the otherwise baseline obligations.
    doc['version'] = 2
    doc['fact_types'].extend(complete['fact_types'][-2:])
    report['derivations'] = [
        {'derivation_ref': 'derivation:' + name, 'fact_type': name, 'status': 'satisfied',
         'computed': [None], 'missing': [], 'extra': [], 'reason': None}
        for name in ['book_is_blocked_for', 'book_is_eligible']]
    with pytest.raises(ValueError):
        module.verify_policy_report(report, doc, 'a' * 64, 'b' * 64, 0)


def checker_attack(tmp_path):
    _, template = valid_policy()
    query = tmp_path / 'attack.py'
    # A developer query can write its own working directory. It must not be
    # able to replace the subsequently selected framework checker artifact.
    checker = ('import sys,json,hashlib\nfrom pathlib import Path\n'
               f'report={template!r}\n'
               'report["binding"]={"model_sha256":MODEL_SHA,"population_sha256":hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest()}\n'
               'Path(sys.argv[-1]).write_text(json.dumps(report))\n')
    query.write_text('import sys,json,hashlib,runpy\nfrom pathlib import Path\n'
                     'runtime,seed,out=map(Path,sys.argv[1:4])\n'
                     'r=runpy.run_path(str(runtime)); raw=seed.read_bytes(); doc=json.loads(raw)\n'
                     'doc["facts"]["recommendation"].append({"user":"ada","book":"night"})\n'
                     'sha=hashlib.sha256(r["MODEL_TEXT"].encode()).hexdigest()\n'
                     'out.write_text(json.dumps({"schema_version":1,"candidate":doc,"calculation":{},"binding":{"model_sha256":sha,"input_sha256":hashlib.sha256(raw).hexdigest()}}))\n'
                     f'runtime.write_text("MODEL_SHA="+repr(sha)+"\\n"+{checker!r})\n')
    return query


def test_query_cannot_replace_independent_checker(tmp_path):
    module = application()
    query = checker_attack(tmp_path)
    output = tmp_path / 'result.json'
    result = module.execute_application(MODEL, POP, output, native_python=Path(sys.executable), query_script=query, owned_relations=("recommendation",))
    assert not result['published'] and not output.exists(), result


def test_query_crash_is_operational_not_policy_rejection(tmp_path):
    module = application()
    query = tmp_path / 'crash.py'; query.write_text('raise RuntimeError("query crash")')
    result = module.execute_application(MODEL, POP, tmp_path / 'out.json',
                                        native_python=Path(sys.executable), query_script=query)
    assert result['exit_code'] == 70 and result['policy'] is None and not result['published'], result


def test_missing_interpreter_reaches_specific_refusal(tmp_path):
    module = application()
    result = module.execute_application(MODEL, POP, tmp_path / 'out.json',
                                        native_python=Path('/absent/python'), query_script=tmp_path / 'query.py')
    assert result['exit_code'] == 70 and 'explicit native interpreter is unavailable' in result['reason']
    assert not result['published']


def test_malformed_model_refuses_before_native_execution(monkeypatch, tmp_path):
    module = application()
    model = tmp_path / 'model.json'; doc = json.loads(MODEL.read_bytes())
    doc['fact_types'][0]['roles'][0]['object_type'] = 'unknown'
    model.write_text(json.dumps(doc))
    query = tmp_path / 'query.py'; query.write_text('# owned')
    called = []
    monkeypatch.setattr(module, '_child', lambda *args: called.append(args))
    result = module.execute_application(model, POP, tmp_path / 'out.json',
                                        native_python=Path(sys.executable), query_script=query)
    assert result['exit_code'] == 3 and 'model validation failed' in result['reason'] and called == []


def test_input_output_collision_preserves_checkpoint(tmp_path):
    module = application()
    source = tmp_path / 'source.json'; source.write_bytes(POP.read_bytes())
    result = module.execute_application(MODEL, source, source, native_python=Path(sys.executable),
                                        query_script=tmp_path / 'query.py')
    assert result['exit_code'] == 2 and not result['published'] and source.read_bytes() == POP.read_bytes()


def test_native_environment_has_no_ambient_credentials(monkeypatch, tmp_path):
    module = application()
    monkeypatch.setenv('PA3_TEST_SECRET', 'must-not-reach-child')
    monkeypatch.setenv('RAI_ENGINE', 'ambient-engine')
    result = module._child([sys.executable, '-I', '-c',
                           'import os; assert "PA3_TEST_SECRET" not in os.environ; assert "RAI_ENGINE" not in os.environ; print("isolated")'], tmp_path)
    assert result.return_code == 0 and result.stdout.strip() == b'isolated'


def test_metadata_scalar_type_change_cannot_publish(monkeypatch, tmp_path):
    module = application()
    source = tmp_path / 'source.json'; doc = json.loads(POP.read_bytes())
    doc['population']['revision'] = 1; source.write_text(json.dumps(doc))
    query = tmp_path / 'query.py'; query.write_text('# owned')
    simulated_child(module, monkeypatch)
    def damage(candidate):
        candidate['population']['revision'] = True
        return candidate
    output = tmp_path / 'out.json'
    result = module.execute_application(MODEL, source, output, native_python=Path(sys.executable),
                                        query_script=query, candidate_transform=damage)
    assert not result['published'] and not output.exists() and result['exit_code'] == 3, result


@pytest.mark.parametrize('boundary', ['coverage', 'instances', 'metadata', 'ownership', 'default-owned'])
def test_source_preservation_branches_refuse_publication(monkeypatch, tmp_path, boundary):
    module = application()
    simulated_child(module, monkeypatch)
    def damage(candidate):
        if boundary == 'coverage':
            candidate['population']['covers'].pop()
        elif boundary == 'instances':
            candidate['instances'] = {'user': ['ada']}
        elif boundary == 'metadata':
            candidate['population']['source'] = 'changed'
        elif boundary == 'default-owned':
            candidate['facts']['recommendation'].append({'user': 'ada', 'book': 'river'})
        return candidate
    _, output, result = run_simulated(module, tmp_path, candidate_transform=damage,
                                      owned_relations=('invented',) if boundary == 'ownership' else ())
    assert result['exit_code'] == 3 and not result['published'] and not output.exists(), result
    assert ('owned relations must name distinct asserted facts' if boundary == 'ownership' else 'candidate changed') in result['reason']
