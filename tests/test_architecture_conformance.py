from __future__ import annotations

import copy
import inspect
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path, PurePosixPath
from typing import Any

import pytest
from support.digests import sha256_bytes as _sha256

from gnd.codegen.manifest import read_manifest
from gnd.model import load_model

CORPUS = Path(__file__).parent / 'fixtures' / 'architecture' / 'static'
CASE_PATHS = tuple(sorted((CORPUS / 'cases').glob('*/case.json')))
ANSWER_KEY = json.loads((CORPUS / 'expected.json').read_text(encoding='utf-8'))
CONTRACT_RELPATH = 'architecture.contract.yaml'
CONTRACT_CAP = 1 * 1024 * 1024
ARCHITECTURE_FINDING_KINDS = ('contract-unreadable', 'contract-missing', 'declared-module-missing', 'declared-symbol-missing', 'symbol-shape-mismatch', 'declared-artifact-missing', 'artifact-path-mismatch', 'artifact-reference-unfound', 'entry-point-module-missing', 'entry-point-flag-unfound', 'contract-fact-type-unknown')

def _canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')

def _safe_recipe_path(root: Path, relpath: str) -> Path:
    pure = PurePosixPath(relpath)
    assert relpath and (not pure.is_absolute()) and ('..' not in pure.parts)
    return root.joinpath(*pure.parts)

def _remove_occupant(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)

def _apply_patch(document: object, patch: dict[str, Any]) -> None:
    parts = [part.replace('~1', '/').replace('~0', '~') for part in patch['path'].split('/')[1:]]
    assert parts
    parent: Any = document
    for part in parts[:-1]:
        parent = parent[int(part)] if isinstance(parent, list) else parent[part]
    leaf = parts[-1]
    if patch['op'] == 'remove':
        if isinstance(parent, list):
            parent.pop(int(leaf))
        else:
            del parent[leaf]
    else:
        value = copy.deepcopy(patch['value'])
        if isinstance(parent, list):
            index = int(leaf)
            if patch['op'] == 'add':
                parent.insert(index, value)
            else:
                parent[index] = value
        else:
            parent[leaf] = value

def _contract_document(recipe: dict[str, Any]) -> dict[str, Any]:
    document = json.loads((CORPUS / 'base' / 'contract.json').read_text(encoding='utf-8'))
    kind = recipe['kind']
    if kind == 'generated-source-count':
        document.update(modules=[{'path': f'sources/m{index:04d}.py', 'symbols': []} for index in range(recipe['count'])], artifacts=[], entry_points=[], smoke=[])
    elif kind == 'generated-source-bytes':
        document.update(modules=[{'path': f'sources/b{index:03d}.py', 'symbols': []} for index in range(recipe['count'])], artifacts=[], entry_points=[], smoke=[])
    else:
        for mutation in recipe.get('patches', []):
            _apply_patch(document, mutation)
    return document

def _materialize_contract(root: Path, recipe: dict[str, Any]) -> bytes | None:
    kind = recipe['kind']
    destination = root / CONTRACT_RELPATH
    if kind == 'absent':
        return None
    if kind == 'malformed':
        data = b'{broken\n'
        destination.write_bytes(data)
        return data
    if kind == 'oversized':
        with destination.open('wb') as stream:
            stream.truncate(CONTRACT_CAP + 1)
        return None
    document = _contract_document(recipe)
    data = _canonical(document)
    if kind == 'symlink':
        target = root / 'contract-target.json'
        target.write_bytes(data)
        destination.symlink_to(target.name)
        return None
    if kind == 'directory':
        destination.mkdir()
        return None
    destination.write_bytes(data)
    return data

def _materialize_generated_sources(root: Path, recipe: dict[str, Any]) -> None:
    if recipe['kind'] != 'generated-source-bytes':
        return
    for index in range(recipe['count']):
        path = root / 'sources' / f'b{index:03d}.py'
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('wb') as stream:
            stream.truncate(recipe['size'])

def _apply_project_mutations(root: Path, mutations: list[dict[str, Any]]) -> None:
    for mutation in mutations:
        destination = _safe_recipe_path(root, mutation['path'])
        _remove_occupant(destination)
        kind = mutation['kind']
        if kind == 'absent':
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        if kind == 'text':
            destination.write_text(mutation['text'], encoding='utf-8')
        elif kind == 'hex':
            destination.write_bytes(bytes.fromhex(mutation['hex']))
        elif kind == 'sparse':
            with destination.open('wb') as stream:
                stream.truncate(mutation['size'])
        elif kind == 'directory':
            destination.mkdir()
        elif kind == 'symlink':
            destination.symlink_to(mutation['target'])
        else:
            raise AssertionError(f'unknown project mutation kind: {kind}')

def _write_manifest(root: Path, model_path: Path, *, lists_contract: bool, contract_bytes: bytes | None) -> None:
    files: list[dict[str, str]] = []
    if lists_contract:
        files.append({'ownership': 'extension', 'relpath': CONTRACT_RELPATH, 'sha256': _sha256(contract_bytes) if contract_bytes is not None else '0' * 64})
    document = {'files': files, 'gnd_version': 'architecture-corpus', 'manifest_version': 1, 'model': {'path': '../model.orm.yaml', 'sha256': _sha256(model_path.read_bytes())}}
    (root / '.gnd-codegen.json').write_bytes(_canonical(document))

def _materialize(case: dict[str, Any], tmp_path: Path) -> tuple[Path, Path]:
    model_path = tmp_path / 'model.orm.yaml'
    shutil.copyfile(CORPUS / 'model.orm.yaml', model_path)
    root = tmp_path / 'project'
    shutil.copytree(CORPUS / 'base' / 'project', root)
    contract_bytes = _materialize_contract(root, case['contract'])
    _materialize_generated_sources(root, case['contract'])
    _apply_project_mutations(root, case['project'])
    _write_manifest(root, model_path, lists_contract=case['manifest_contract'], contract_bytes=contract_bytes)
    return (model_path, root)

def _plain(value: object | None) -> object | None:
    return None if value is None else asdict(value)

def _declared_counts(document: dict[str, Any]) -> dict[str, int]:
    return {'modules': len(document['modules']), 'symbols': sum(len(module['symbols']) for module in document['modules']), 'artifacts': len(document['artifacts']), 'artifact_requirements': sum(len(artifact['required_by']) for artifact in document['artifacts']), 'entry_points': len(document['entry_points']), 'smoke_rows': len(document['smoke'])}

def _observe_real(case: dict[str, Any], model_path: Path, root: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    from gnd.conformance import architecture as architecture_module
    from gnd.conformance.integrity import open_project_root
    seam = case.get('seam')
    if isinstance(seam, str) and seam.startswith('source-read-refusal:'):
        from gnd.artifacts import ArtifactError
        target = seam.split(':', 1)[1]
        real_reader = architecture_module.read_regular_bounded_at

        def refuse_one(root_fd: int, relative: str, **kwargs: Any) -> Any:
            if relative == target:
                raise ArtifactError(f'deterministic corpus read refusal for {target}')
            return real_reader(root_fd, relative, **kwargs)
        monkeypatch.setattr(architecture_module, 'read_regular_bounded_at', refuse_one)
    if case['id'] in {'C-05-source-count-budget', 'C-06-source-byte-budget'}:

        def forbid_source_read(root_fd: int, relative: str, **kwargs: Any) -> Any:
            raise AssertionError(f'budget refusal read forbidden source {relative}')
        monkeypatch.setattr(architecture_module, 'read_regular_bounded_at', forbid_source_read)
    manifest = read_manifest(root / '.gnd-codegen.json')
    root_fd = open_project_root(root)
    try:
        result = architecture_module.check_architecture(load_model(model_path), root, manifest, model_path=model_path, root_fd=root_fd)
    finally:
        os.close(root_fd)
    observation: dict[str, Any] = {'ran': True, 'contract': _plain(result.contract), 'declared': _plain(result.declared), 'scanned': list(result.scanned), 'contract_absent': result.contract_absent, 'findings': [{'kind': finding.kind, 'target': finding.target, 'message': finding.message} for finding in result.findings], 'exit': 13 if result.findings else 0}
    if seam == 'root-race':
        from gnd.conformance import service as service_module
        real_bind = service_module.bind_project_root
        displaced = root.with_name('project-before-root-race')
        injected = False

        def replace_before_rebind(*args: Any, **kwargs: Any) -> tuple[int, int]:
            nonlocal injected
            if not injected:
                injected = True
                root.rename(displaced)
                root.mkdir()
            return real_bind(*args, **kwargs)
        monkeypatch.setattr(service_module, 'bind_project_root', replace_before_rebind)
        service_result = service_module.run_conformance(model_path, root)
        assertions = {row['id']: row['ran'] for row in service_result.payload['assertions']}
        observation.update(exit=service_result.exit_code, service_error=service_result.payload['error'], service_architecture_ran=assertions.get('architecture'))
        assert injected
    return observation

def _assert_observation(expected: dict[str, Any], actual: dict[str, Any]) -> None:
    for key in ('ran', 'contract', 'declared', 'scanned', 'contract_absent', 'exit'):
        assert actual[key] == expected[key], f'{key}: {actual[key]!r} != {expected[key]!r}'
    expected_findings = expected['findings']
    actual_findings = actual['findings']
    assert len(actual_findings) == len(expected_findings)
    for index, (wanted, found) in enumerate(zip(expected_findings, actual_findings, strict=True)):
        assert found['kind'] == wanted['kind'], f'finding {index} kind'
        assert found['target'] == wanted['target'], f'finding {index} target'
        for fragment in wanted['message_contains']:
            assert fragment in found['message'], f"finding {index} lacks {fragment!r}: {found['message']!r}"
    if 'service_error_contains' in expected:
        assert all(part in actual['service_error'] for part in expected['service_error_contains'])
        assert actual['service_architecture_ran'] is expected['service_architecture_ran']

def _synthetic_observation(expected: dict[str, Any]) -> dict[str, Any]:
    observation = copy.deepcopy(expected)
    observation['findings'] = [{'kind': row['kind'], 'target': row['target'], 'message': ' | '.join(row['message_contains'])} for row in expected['findings']]
    if 'service_error_contains' in expected:
        observation['service_error'] = ' | '.join(expected['service_error_contains'])
    return observation

def test_static_corpus_and_answer_key_are_closed_and_bijective() -> None:
    assert ANSWER_KEY['schema_version'] == 1
    assert ANSWER_KEY['case_count'] == 48
    assert len(CASE_PATHS) == 48
    cases = [json.loads(path.read_text(encoding='utf-8')) for path in CASE_PATHS]
    case_ids = [case['id'] for case in cases]
    assert len(case_ids) == len(set(case_ids))
    assert set(case_ids) == set(ANSWER_KEY['cases'])
    assert all((path.parent.name == case['id'] for path, case in zip(CASE_PATHS, cases, strict=True)))
    contract_kinds = {'absent', 'base', 'directory', 'generated-source-bytes', 'generated-source-count', 'malformed', 'oversized', 'symlink'}
    project_kinds = {'absent', 'directory', 'hex', 'sparse', 'symlink', 'text'}
    for case in cases:
        assert set(case) in ({'schema_version', 'id', 'story', 'manifest_contract', 'contract', 'project'}, {'schema_version', 'id', 'story', 'manifest_contract', 'contract', 'project', 'seam'})
        assert case['schema_version'] == 1 and case['story']
        contract = case['contract']
        assert contract['kind'] in contract_kinds
        expected_contract_keys = {'base': {'kind', 'patches'}, 'generated-source-count': {'kind', 'count'}, 'generated-source-bytes': {'kind', 'count', 'size'}}.get(contract['kind'], {'kind'})
        assert set(contract) == expected_contract_keys
        for patch in contract.get('patches', []):
            assert set(patch) == {'op', 'path', 'value'}
            assert patch['op'] in {'add', 'replace'}
            assert patch['path'].startswith('/')
        for row in case['project']:
            assert row['kind'] in project_kinds
            expected_project_keys = {'absent': {'path', 'kind'}, 'directory': {'path', 'kind'}, 'hex': {'path', 'kind', 'hex'}, 'sparse': {'path', 'kind', 'size'}, 'symlink': {'path', 'kind', 'target'}, 'text': {'path', 'kind', 'text'}}[row['kind']]
            assert set(row) == expected_project_keys
            _safe_recipe_path(Path('portable-root'), row['path'])
        if 'seam' in case:
            assert case['seam'] == 'root-race' or case['seam'].startswith('source-read-refusal:')
        answer = ANSWER_KEY['cases'][case['id']]
        required = {'ran', 'contract', 'declared', 'scanned', 'contract_absent', 'findings', 'exit'}
        assert required <= set(answer)
        assert set(answer) in (required, required | {'service_error_contains', 'service_architecture_ran'})
        assert answer['scanned'] == sorted(set(answer['scanned']))
        for finding in answer['findings']:
            assert set(finding) == {'kind', 'target', 'message_contains'}
            assert finding['message_contains']

def test_answer_key_binds_contract_bytes_and_declared_counts() -> None:
    for case_path in CASE_PATHS:
        case = json.loads(case_path.read_text(encoding='utf-8'))
        expected = ANSWER_KEY['cases'][case['id']]
        kind = case['contract']['kind']
        if kind == 'malformed':
            assert expected['contract'] == {'relpath': CONTRACT_RELPATH, 'sha256': _sha256(b'{broken\n')}
            assert expected['declared'] is None
        elif kind in {'base', 'generated-source-count', 'generated-source-bytes'}:
            document = _contract_document(case['contract'])
            assert expected['contract'] == {'relpath': CONTRACT_RELPATH, 'sha256': _sha256(_canonical(document))}
            assert expected['declared'] == _declared_counts(document)
        else:
            assert expected['contract'] is None
            assert expected['declared'] is None

def test_always_clean_evaluator_fails_a_known_red_story() -> None:
    expected = ANSWER_KEY['cases']['C-29-pathlib-path-mismatch']
    observed = _synthetic_observation(expected)
    observed.update(findings=[], exit=0)
    with pytest.raises(AssertionError):
        _assert_observation(expected, observed)

def test_always_finding_evaluator_fails_the_clean_control() -> None:
    expected = ANSWER_KEY['cases']['C-48-full-conforming-control']
    observed = _synthetic_observation(expected)
    observed.update(findings=[{'kind': 'contract-unreadable', 'target': CONTRACT_RELPATH, 'message': 'forced'}], exit=13)
    with pytest.raises(AssertionError):
        _assert_observation(expected, observed)

def test_architecture_validation_and_suppression_order_is_literal() -> None:
    from gnd.conformance.architecture import check_architecture
    source = inspect.getsource(check_architecture)
    ordered_markers = ('loaded = _read_contract(', 'declared = _declared_counts(contract)', 'roster, entry_paths = _source_roster(contract)', 'if len(roster) > MAX_ARCHITECTURE_SOURCES:', 'states = {relpath: _stat_source(', 'if aggregate_bytes > MAX_ARCHITECTURE_SOURCE_BYTES:', 'fact_ids = {', 'observations: dict[str, SourceObservation] = {}', 'for module in contract.modules:', 'for artifact in contract.artifacts:', 'basename = PurePosixPath(artifact.path).name', 'relpath = entry_paths[entry.module]')
    positions = [source.index(marker) for marker in ordered_markers]
    assert positions == sorted(positions)
    assert source.count('observations.get(') == 3
    assert 'observations[required_by]' not in source
    assert 'observations[relpath]' not in source[source.index('for module in contract.modules:'):]
    planted = source + '\nobservation = observations[required_by]\n'
    assert 'observations[required_by]' in planted

@pytest.mark.slow
def test_legal_near_budget_roster_completes_in_a_fresh_process_under_five_seconds(tmp_path: Path) -> None:
    model_path = tmp_path / 'model.orm.yaml'
    shutil.copyfile(CORPUS / 'model.orm.yaml', model_path)
    root = tmp_path / 'project'
    sources = root / 'sources'
    sources.mkdir(parents=True)
    source_size = 65535
    seed = sources / 'm0000.py'
    source_prefix = b"from pathlib import Path\nDATA = Path(__file__).parent.parent / 'artifacts' / 'data.json'\n"
    seed.write_bytes(source_prefix + b' ' * (source_size - len(source_prefix)))
    modules = [{'path': 'sources/m0000.py', 'symbols': []}]
    for index in range(1, 1024):
        relpath = f'sources/m{index:04d}.py'
        os.link(seed, root / relpath)
        modules.append({'path': relpath, 'symbols': []})
    assert source_size * len(modules) == 64 * 1024 * 1024 - 1024
    contract = {'contract_version': 1, 'modules': modules, 'artifacts': [{'path': 'artifacts/data.json', 'required_by': [module['path'] for module in modules]}], 'entry_points': [], 'smoke': []}
    contract_bytes = _canonical(contract)
    (root / CONTRACT_RELPATH).write_bytes(contract_bytes)
    (root / 'artifacts').mkdir()
    (root / 'artifacts' / 'data.json').write_text('{}\n', encoding='utf-8')
    _write_manifest(root, model_path, lists_contract=True, contract_bytes=contract_bytes)
    probe = "import json, sys, time\nfrom pathlib import Path\nfrom gnd.codegen.manifest import read_manifest\nfrom gnd.conformance.architecture import check_architecture\nfrom gnd.model import load_model\nmodel_path, root = Path(sys.argv[1]), Path(sys.argv[2])\nstarted = time.perf_counter()\nresult = check_architecture(load_model(model_path), root, read_manifest(root / '.gnd-codegen.json'), model_path=model_path)\nprint(json.dumps({'elapsed': time.perf_counter() - started, 'findings': len(result.findings), 'scanned': len(result.scanned)}))\n"
    started = time.perf_counter()
    completed = subprocess.run([sys.executable, '-c', probe, str(model_path), str(root)], capture_output=True, text=True, check=False, timeout=10)
    wall_elapsed = time.perf_counter() - started
    assert completed.returncode == 0, completed.stderr
    measured = json.loads(completed.stdout)
    assert measured['findings'] == 0
    assert measured['scanned'] == 1025
    assert measured['elapsed'] < 5.0
    assert wall_elapsed < 5.0

def test_aggregate_budget_binds_every_read_to_the_initial_source_stat(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from gnd.conformance import ConformanceError
    from gnd.conformance import architecture as architecture_module
    model_path = tmp_path / 'model.orm.yaml'
    shutil.copyfile(CORPUS / 'model.orm.yaml', model_path)
    root = tmp_path / 'project'
    sources = root / 'sources'
    sources.mkdir(parents=True)
    seed = sources / 'm0000.py'
    seed.write_bytes(b' ')
    modules = [{'path': 'sources/m0000.py', 'symbols': []}]
    for index in range(1, 1024):
        relpath = f'sources/m{index:04d}.py'
        os.link(seed, root / relpath)
        modules.append({'path': relpath, 'symbols': []})
    contract = {'contract_version': 1, 'modules': modules, 'artifacts': [], 'entry_points': [], 'smoke': []}
    contract_bytes = _canonical(contract)
    (root / CONTRACT_RELPATH).write_bytes(contract_bytes)
    _write_manifest(root, model_path, lists_contract=True, contract_bytes=contract_bytes)
    real_reader = architecture_module.read_regular_bounded_at
    source_reads = 0

    def grow_after_budget(root_fd: int, relative: str, **kwargs: Any) -> Any:
        nonlocal source_reads
        source_reads += 1
        if source_reads == 1:
            seed.write_bytes(b' ' * (10 * 1024 * 1024))
        else:
            raise AssertionError('a second source read escaped the aggregate-race abort')
        return real_reader(root_fd, relative, **kwargs)
    monkeypatch.setattr(architecture_module, 'read_regular_bounded_at', grow_after_budget)
    with pytest.raises(ConformanceError, match='architecture-source-race'):
        architecture_module.check_architecture(load_model(model_path), root, read_manifest(root / '.gnd-codegen.json'), model_path=model_path)
    assert source_reads == 1

def test_artifact_indexes_are_built_once_for_duplicate_requirements(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from gnd.conformance import architecture as architecture_module
    model_path = tmp_path / 'model.orm.yaml'
    shutil.copyfile(CORPUS / 'model.orm.yaml', model_path)
    root = tmp_path / 'project'
    root.mkdir()
    source_text = "from pathlib import Path\nGOOD = Path(__file__).parent / 'artifacts' / 'data.json'\nBAD = Path(__file__).parent / 'wrong' / 'data.json'\n"
    (root / 'app.py').write_text(source_text, encoding='utf-8')
    (root / 'artifacts').mkdir()
    (root / 'artifacts' / 'data.json').write_text('{}\n', encoding='utf-8')
    contract = {'contract_version': 1, 'modules': [{'path': 'app.py', 'symbols': []}], 'artifacts': [{'path': 'artifacts/data.json', 'required_by': ['app.py', 'app.py', 'app.py']}], 'entry_points': [], 'smoke': []}
    contract_bytes = _canonical(contract)
    (root / CONTRACT_RELPATH).write_bytes(contract_bytes)
    _write_manifest(root, model_path, lists_contract=True, contract_bytes=contract_bytes)
    real_resolver = architecture_module._resolved_expression
    resolver_calls = 0

    def count_resolution(node: Any, source_relpath: str) -> str | None:
        nonlocal resolver_calls
        resolver_calls += 1
        return real_resolver(node, source_relpath)
    monkeypatch.setattr(architecture_module, '_resolved_expression', count_resolution)
    expected_resolver_calls = len(architecture_module.observe_source_bytes(source_text.encode('utf-8'), 'app.py').path_candidates)
    result = architecture_module.check_architecture(load_model(model_path), root, read_manifest(root / '.gnd-codegen.json'), model_path=model_path)
    mismatches = [finding for finding in result.findings if finding.kind == 'artifact-path-mismatch']
    assert resolver_calls == expected_resolver_calls
    assert len(mismatches) == 1

def test_closed_retained_root_descriptor_is_assertion_io(tmp_path: Path) -> None:
    from gnd.conformance import ConformanceError
    from gnd.conformance.architecture import check_architecture
    from gnd.conformance.integrity import open_project_root
    case = json.loads((CORPUS / 'cases' / 'C-48-full-conforming-control' / 'case.json').read_text(encoding='utf-8'))
    model_path, root = _materialize(case, tmp_path)
    root_fd = open_project_root(root)
    os.close(root_fd)
    with pytest.raises(ConformanceError, match='architecture-descriptor'):
        check_architecture(load_model(model_path), root, read_manifest(root / '.gnd-codegen.json'), model_path=model_path, root_fd=root_fd)

@pytest.mark.parametrize('target', ['app.py', 'artifacts/data.json'])
def test_unknown_architecture_stat_refusal_is_io_not_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, target: str) -> None:
    from gnd.artifacts import ArtifactError
    from gnd.conformance import ConformanceError
    from gnd.conformance import architecture as architecture_module
    case = json.loads((CORPUS / 'cases' / 'C-48-full-conforming-control' / 'case.json').read_text(encoding='utf-8'))
    model_path, root = _materialize(case, tmp_path)
    real_stat = architecture_module.stat_leaf_at

    def refuse(root_fd: int, relative: str) -> os.stat_result:
        if relative == target:
            try:
                raise PermissionError(13, 'deterministic stat refusal')
            except PermissionError as error:
                raise ArtifactError('deterministic stat refusal') from error
        return real_stat(root_fd, relative)
    monkeypatch.setattr(architecture_module, 'stat_leaf_at', refuse)
    with pytest.raises(ConformanceError, match='architecture-stat-io'):
        architecture_module.check_architecture(load_model(model_path), root, read_manifest(root / '.gnd-codegen.json'), model_path=model_path)

@pytest.mark.parametrize(('source', 'expected_kinds'), [('def main():\n    pass\nmain: object\n', []), ('def main():\n    pass\nmain, other = (1, 2)\n', ['declared-symbol-missing'])])
def test_architecture_symbols_follow_effective_python_assignment_bindings(tmp_path: Path, source: str, expected_kinds: list[str]) -> None:
    from gnd.conformance.architecture import check_architecture
    model_path = tmp_path / 'model.orm.yaml'
    shutil.copyfile(CORPUS / 'model.orm.yaml', model_path)
    root = tmp_path / 'project'
    root.mkdir()
    (root / 'app.py').write_text(source, encoding='utf-8')
    contract = {'contract_version': 1, 'modules': [{'path': 'app.py', 'symbols': [{'name': 'main', 'parameters': []}]}], 'artifacts': [], 'entry_points': [], 'smoke': []}
    contract_bytes = _canonical(contract)
    (root / CONTRACT_RELPATH).write_bytes(contract_bytes)
    _write_manifest(root, model_path, lists_contract=True, contract_bytes=contract_bytes)
    result = check_architecture(load_model(model_path), root, read_manifest(root / '.gnd-codegen.json'), model_path=model_path)
    assert [finding.kind for finding in result.findings] == expected_kinds

def test_fresh_interpreter_does_not_import_cli_or_execute_hostile_source(tmp_path: Path) -> None:
    model_path = tmp_path / 'model.orm.yaml'
    shutil.copyfile(CORPUS / 'model.orm.yaml', model_path)
    root = tmp_path / 'project'
    root.mkdir()
    sentinel = tmp_path / 'hostile-source-executed'
    (root / 'hostile.py').write_text(f"from pathlib import Path\nPath({sentinel.as_posix()!r}).write_text('executed')\ndef declared():\n    return None\n", encoding='utf-8')
    contract = {'contract_version': 1, 'modules': [{'path': 'hostile.py', 'symbols': [{'name': 'declared', 'parameters': []}]}], 'artifacts': [], 'entry_points': [], 'smoke': []}
    contract_bytes = _canonical(contract)
    (root / CONTRACT_RELPATH).write_bytes(contract_bytes)
    _write_manifest(root, model_path, lists_contract=True, contract_bytes=contract_bytes)
    probe = "import json, sys\nfrom pathlib import Path\nbefore = 'gnd.cli' in sys.modules\nfrom gnd.codegen.manifest import read_manifest\nfrom gnd.conformance.architecture import check_architecture\nfrom gnd.model import load_model\nmodel_path, root, sentinel = map(Path, sys.argv[1:])\nafter_import = 'gnd.cli' in sys.modules\nresult = check_architecture(load_model(model_path), root, read_manifest(root / '.gnd-codegen.json'), model_path=model_path)\nprint(json.dumps({'before': before, 'after_import': after_import, 'after_check': 'gnd.cli' in sys.modules, 'executed': sentinel.exists(), 'findings': len(result.findings)}))\n"
    completed = subprocess.run([sys.executable, '-c', probe, str(model_path), str(root), str(sentinel)], capture_output=True, text=True, check=False, timeout=10)
    assert completed.returncode == 0, completed.stderr
    measured = json.loads(completed.stdout)
    assert measured == {'before': False, 'after_import': False, 'after_check': False, 'executed': False, 'findings': 0}
    assert not sentinel.exists()

@pytest.mark.parametrize('case_path', CASE_PATHS, ids=lambda path: path.parent.name)
def test_every_static_corpus_case(case_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert len(CASE_PATHS) >= 48, 'the measured branch floor belongs inside the proof body'
    case = json.loads(case_path.read_text(encoding='utf-8'))
    model_path, root = _materialize(case, tmp_path)
    actual = _observe_real(case, model_path, root, monkeypatch)
    _assert_observation(ANSWER_KEY['cases'][case['id']], actual)
