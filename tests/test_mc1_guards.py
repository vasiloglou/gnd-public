"""Admission-point controls; each invokes the actual consumer before publication."""
from __future__ import annotations

import importlib
from pathlib import Path
from types import SimpleNamespace

import pytest
from test_mc1_model_includes import write_case

from gnd.errors import ModelValidationError


@pytest.mark.parametrize('module,name,args', [
    ('gnd.codegen.emit', 'emit_project', lambda p: (SimpleNamespace(), str(p))),
    ('gnd.codegen.manifest', 'build_manifest', lambda p: (SimpleNamespace(), str(p))),
    ('gnd.conformance.currency', 'model_file_sha256', lambda p: (p,)),
    ('gnd.evolve.service', '_parse_model_text', lambda p: (p.read_text(),)),
    ('gnd.export.pyrel_rules', 'render', lambda p: (p, 'duckdb')),
], ids=['R22-emit', 'R22-manifest', 'R23-currency', 'R19-parse', 'R13-pyrel-rules'])
def test_direct_refusals(tmp_path, module, name, args):
    path, _, _ = write_case(tmp_path)
    function = getattr(importlib.import_module(module), name)
    if module == 'gnd.evolve.service' and name == '_parse_model_text':
        # MC3 enables authored parsing only; canonical loading still authenticates includes.
        import json
        assert function(*args(path)) == json.loads(path.read_text())
        return
    with pytest.raises(Exception, match='include:unsupported-route'):
        function(*args(path))
    assert sorted(p.name for p in tmp_path.iterdir()) == ['project.orm.json', 'vocab.orm.json']


@pytest.mark.parametrize('route', ['codegen', 'extract', 'conformance', 'measure', 'pyrel'])
def test_cli_guards(tmp_path, route):
    from support.cli_runner import run_main
    path, _, _ = write_case(tmp_path)
    out = tmp_path / 'out'
    args = {
        'codegen': ['codegen', str(path), '--out', str(out)],
        'extract': ['extract', str(path), '--out', str(out)],
        'conformance': ['conformance', str(path), str(out), '--format', 'json'],
        'measure': ['measure', str(path), '--populations', str(tmp_path), '--format', 'json'],
        'pyrel': ['export', 'pyrel', str(path), '--out', str(out)],
    }[route]
    result = run_main(args)
    assert result.returncode == 3, (result.stdout, result.stderr)
    assert b'include:unsupported-route' in result.stdout + result.stderr
    assert not out.exists()


def test_R6_population_compose(tmp_path):
    from gnd.api import compose
    path, _, _ = write_case(tmp_path)
    # MC2 supports rooted composition; stale pins still precede population IO.
    vocabulary = tmp_path / 'vocab.orm.json'
    vocabulary.write_bytes(vocabulary.read_bytes() + b' ')
    result = compose(path, tmp_path / 'absent')
    assert result['exit_code'] == 3
    assert result['error']['message'] == 'include:hash-mismatch'


def test_R2_witness_inputs(tmp_path):
    from gnd.witness.service import _witness_inputs
    path, _, _ = write_case(tmp_path)
    population = tmp_path / 'candidate.json'
    population.write_text('{}')
    with pytest.raises(ModelValidationError, match='include:unsupported-route'):
        _witness_inputs(path, population, None)


def test_R3_witness_memory(tmp_path):
    import json

    from gnd.witness.io import intake
    path, _, _ = write_case(tmp_path)
    with pytest.raises(ModelValidationError, match='include:unsupported-route'):
        intake(json.loads(path.read_text()), {}, ())


def test_R19_evolve_loaded_bytes(tmp_path):
    from gnd.evolve.service import _load_model_document
    path, _, _ = write_case(tmp_path)
    import json

    from gnd.model import load_model_bytes

    model, authored = _load_model_document(path.read_bytes(), label='model', model_path=path)
    assert model.includes and authored == json.loads(path.read_text())
    with pytest.raises(ModelValidationError, match='include:unresolved'):
        load_model_bytes(path.read_bytes(), source=path)
    vocabulary = tmp_path / 'vocab.orm.json'
    vocabulary.write_bytes(vocabulary.read_bytes() + b' ')
    with pytest.raises(Exception, match='include:hash-mismatch'):
        _load_model_document(path.read_bytes(), label='model', model_path=path)


def test_R29_standalone_validate(tmp_path):
    import sys

    from support.cli_runner import run_process
    path, _, _ = write_case(tmp_path)
    script = Path(__file__).resolve().parents[1] / 'src/gnd/skills/gnd-model-from-text/scripts/validate_model.py'
    result = run_process([sys.executable, str(script), str(path)])
    assert result.returncode != 0
    assert b'include:unsupported-route' in result.stdout + result.stderr
    assert b'gnd validate' in result.stdout + result.stderr


def test_R29_standalone_migration(tmp_path, monkeypatch):
    import importlib.util
    path, _, _ = write_case(tmp_path)
    script = Path(__file__).resolve().parents[1] / 'src/gnd/skills/gnd-adopt/scripts/verify_migration.py'
    spec = importlib.util.spec_from_file_location('mc_migration', script)
    module = importlib.util.module_from_spec(spec)
    import sys
    # This source resource is also the installer's exact packaged inventory.
    # Import the standalone script without publishing a cache into that tree.
    before = set(script.parent.rglob('*'))
    monkeypatch.setattr(sys, 'dont_write_bytecode', True)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    assert set(script.parent.rglob('*')) == before
    with pytest.raises(module.Refusal, match='include:unsupported-route.*gnd validate'):
        module._load_model_surface(path.read_bytes(), path)


def test_R20_batch(tmp_path):
    from gnd.batch import check_population_directory
    path, _, _ = write_case(tmp_path)
    result = check_population_directory(path, tmp_path)
    assert result.aggregate_exit == 3
    assert 'include:unsupported-route' in str(result)


@pytest.mark.parametrize('module,name,kwargs', [
    ('gnd.fidelity.service', '_cmd_fidelity', {'cases_dir': '.', 'artifacts_dir': '.', 'out': None, 'output_format': 'json'}),
    ('gnd.fidelity.doccheck_service', '_cmd_doccheck', {'manifest_path': 'absent', 'artifacts_dir': '.'}),
], ids=['R25-fidelity', 'R25-doccheck'])
def test_R25_consumers(tmp_path, module, name, kwargs, capsys):
    path, _, _ = write_case(tmp_path)
    assert getattr(importlib.import_module(module), name)(str(path), **kwargs) == 3
    output = capsys.readouterr()
    assert 'include:unsupported-route' in output.out + output.err


def test_R28_rai_import_before_temp_copy(tmp_path, monkeypatch):
    import gnd.rai_import as rai
    path, _, _ = write_case(tmp_path)
    def forbidden(*args, **kwargs):
        pytest.fail('identity temp copy occurred before include refusal')
    monkeypatch.setattr(rai, '_valid_model_bytes', forbidden)
    request = rai.RaiImportRequest(path, tmp_path / 'out', 'model.orm.json', None)
    with pytest.raises(rai.RaiImportError, match='include:unsupported-route'):
        rai.plan_rai_import(request)
    assert not request.output_dir.exists()


@pytest.mark.parametrize('kind', ['lean', 'souffle'])
def test_R11_R12_exporters(tmp_path, kind):
    path, _, _ = write_case(tmp_path)
    population = tmp_path / 'candidate.json'
    population.write_text('{}')
    module = importlib.import_module(f'gnd.export.{kind}_io')
    out = tmp_path / 'out'
    kwargs = {'toolchain': {}} if kind == 'lean' else {}
    result = getattr(module, f'export_{kind}')(path, population, out=out, raw=True, **kwargs)
    assert result.exit_code == 3
    assert result.reason == 'include:unsupported-route'
    assert not out.exists()


def test_R18_discover(tmp_path):
    from gnd.discover.service import discover
    path, _, _ = write_case(tmp_path)
    population = tmp_path / 'candidate.json'
    population.write_text('{}')
    # MC3's rooted successor verifies dependencies before downstream admission.
    vocabulary = tmp_path / 'vocab.orm.json'
    vocabulary.write_bytes(vocabulary.read_bytes() + b' ')
    with pytest.raises(ModelValidationError, match='include:hash-mismatch'):
        discover(path, population, families=('mandatory',), max_values=10, max_pairs=10)


def test_R17_ilp_prepare(tmp_path):
    from gnd.export.ilp_service import _prepare
    path, _, _ = write_case(tmp_path)
    labels = Path(__file__).resolve().parents[1] / 'tests/fixtures/induced_knowledge/ik3-corpus/c1.labels.json'
    # MC3's rooted successor verifies dependencies before downstream admission.
    vocabulary = tmp_path / 'vocab.orm.json'
    vocabulary.write_bytes(vocabulary.read_bytes() + b' ')
    with pytest.raises(ModelValidationError, match='include:hash-mismatch'):
        _prepare(path, labels, 'popper')


def test_R9_session_replay(tmp_path):
    import hashlib

    from gnd.exp.session_replay import _model
    path, _, _ = write_case(tmp_path)
    raw = path.read_bytes()
    case = SimpleNamespace(verify=SimpleNamespace(model=SimpleNamespace(
        path=path.name, size_bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())))
    with pytest.raises(ModelValidationError, match='include:unsupported-route'):
        _model(case, tmp_path)


@pytest.mark.parametrize('operation', ['execute', 'proposal'])
def test_R16_applications(tmp_path, operation):
    import sys

    from gnd.export.applications import check_proposal, execute_application
    path, _, _ = write_case(tmp_path)
    input_ = tmp_path / 'input.json'
    input_.write_text('{}')
    out = tmp_path / 'out'
    if operation == 'execute':
        result = execute_application(path, input_, out, native_python=sys.executable, query_script=input_)
    else:
        result = check_proposal(path, input_, input_, out, native_python=sys.executable)
    assert result['exit_code'] == 3, result
    assert 'include:unsupported-route' in str(result)
    assert not out.exists()


def test_R15_runtime_side_calls(tmp_path):
    import json

    from gnd.export.applications import _preserve_source, verify_policy_report
    path, _, _ = write_case(tmp_path)
    document = json.loads(path.read_text())
    # Both entry helpers must guard before their independent runtime sees a model.
    report = {'schema_version': 1, 'profile': 'applications-v1', 'backend': 'duckdb-local',
              'accepted': True, 'exit_code': 0, 'binding': {'model_sha256': 'm', 'population_sha256': 'p'}}
    for function, args in [(verify_policy_report, (report, document, 'm', 'p', 0)),
                           (_preserve_source, (document, {}, {}, ()))]:
        with pytest.raises(ModelValidationError, match='include:unsupported-route'):
            function(*args)


def test_R4_judgments(tmp_path):
    from gnd.judgments import evaluate_judgments
    path, _, _ = write_case(tmp_path)
    with pytest.raises(ModelValidationError, match='include:unsupported-route'):
        evaluate_judgments(None, (), model=None, candidate=None, mechanical_report={},
                           model_bytes=path.read_bytes(), population_bytes=b'{}', trusted_root=tmp_path)


def test_R5_judgments_api(tmp_path):
    from gnd.api import judgments
    path, _, _ = write_case(tmp_path)
    result = judgments(path, 'absent', 'absent', 'absent', trusted_root=tmp_path)
    assert result['outcome'] == 3
    assert 'include:unsupported-route' in str(result)


def session_case(tmp_path):
    import hashlib

    import test_exp_session_contract as fixture

    from gnd.exp.session_contract import DataDrivenContract
    document = fixture._contract_document(tmp_path)
    path, _, _ = write_case(tmp_path)
    raw = path.read_bytes()
    for case in document['cases']:
        case['verify']['model'] = {'path': path.name, 'media_type': 'application/json',
            'encoding': 'utf-8', 'size_bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
    return path, document, DataDrivenContract.model_validate(document)


@pytest.mark.parametrize('route', ['case-models', 'copy-bound'])
def test_R7_session_copies(tmp_path, route):
    from gnd.exp.session import _case_models, _copy_bound_model
    _, _, contract = session_case(tmp_path)
    view = tmp_path / 'view'
    with pytest.raises(ModelValidationError, match='include:unsupported-route'):
        if route == 'case-models':
            _case_models(contract, tmp_path)
        else:
            _copy_bound_model(contract.cases[0], tmp_path, view)
    assert not view.exists()


def test_R8_session_contract(tmp_path):
    import test_exp_session_contract as fixture

    from gnd.exp.session_contract import SessionContractError
    _, document, _ = session_case(tmp_path)
    with pytest.raises(SessionContractError) as caught:
        fixture._read(tmp_path, document)
    assert any(i.rule_id == 'include:unsupported-route' for i in caught.value.issues)


def test_R10_session_judgments(tmp_path):
    from gnd.exp.session_judgments import evaluate
    path, _, _ = write_case(tmp_path)
    protected = tmp_path / 'judgment-authority'
    protected.mkdir()
    (protected / 'policy.json').write_text('{}')
    (tmp_path / 'receipts.json').write_text('{}')
    case = SimpleNamespace(judgment_gate=SimpleNamespace(
        policy=SimpleNamespace(path='policy.json'), receipts_path='receipts.json'),
        verify=SimpleNamespace(model=SimpleNamespace(path=path.name)))
    with pytest.raises(ModelValidationError, match='include:unsupported-route'):
        evaluate(case, {}, {}, None, None, tmp_path, tmp_path, tmp_path)


def test_R21_composition_verify(tmp_path):
    from gnd.checking_service import _composition_view
    path, _, _ = write_case(tmp_path)
    population = tmp_path / 'population.json'
    population.write_text('{}')
    def forbidden(*args, **kwargs):
        pytest.fail('composition verify ran on a partial model')
    with pytest.raises(ModelValidationError, match='include:unsupported-route'):
        _composition_view(None, path, population, None, None, tmp_path, forbidden)


def test_R27_recovery_before_copy(tmp_path, monkeypatch):
    import test_recovery_report as fixture

    from gnd.recovery import verify
    fixture._write_bundle(tmp_path)
    path, _, _ = write_case(tmp_path)
    (tmp_path / 'model.orm.yaml').write_bytes(path.read_bytes())
    def forbidden(*args, **kwargs):
        pytest.fail('recovery copied an includer before the guard')
    monkeypatch.setattr(verify.tempfile, 'TemporaryDirectory', forbidden)
    result = verify.verify_recovery_bundle(tmp_path)
    assert not result.ok
    assert 'include:unsupported-route' in str(result)


def test_R30_examples_do_not_declare_includes():
    from gnd.model import load_model, parse_model_document
    from gnd.model._includes import declares_includes
    examples = Path(__file__).resolve().parents[1] / 'src/gnd/examples'
    paths = sorted(examples.rglob('*.orm.yaml')) + sorted(examples.rglob('*.orm.json'))
    assert paths
    included = {path.relative_to(examples).as_posix() for path in paths
                if declares_includes(parse_model_document(path.read_bytes(), source=path))}
    expected = {'expense/teams/engineering.orm.json', 'expense/teams/sales.orm.json',
                'expense/teams/sales-v2.orm.json'}
    assert included == expected
    for relative in included:
        assert load_model(examples / relative)._included
