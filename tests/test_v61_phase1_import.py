from __future__ import annotations

import io
import os
import random
import subprocess
import sys
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from gnd import artifacts as artifact_module
from gnd.artifacts import ArtifactError
from gnd.rai_import import (
    RaiImportCollision,
    RaiImportError,
    RaiImportIO,
    RaiImportRequest,
    RaiImportResult,
    _default_modality,
    _snake,
    parse_rai_model_bytes,
    plan_rai_import,
    publish_rai_import,
)

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / 'tests/fixtures/v61-phase1'
IMPORT = CORPUS / 'import'
POSITIVE = [{'expected_aliases': 'identity.expected.aliases.json', 'expected_exit': 0, 'expected_model': 'identity.expected.model.orm.yaml', 'id': 'I-IDENTITY', 'input': 'identity.source.orm.yaml', 'source_artifact': 'identity.source.orm.yaml', 'source_commit': None}]
NEGATIVE = [{'expected_exit': 3, 'expected_rule': 'rai-import:modality', 'id': 'N-MODALITY', 'input': 'mutations/modality-no-default.orm.yaml', 'source_artifact': 'modality-no-default.orm.yaml', 'source_commit': None}, {'expected_exit': 3, 'expected_rule': 'rai-import:role-name', 'id': 'N-ROLE-COLLISION', 'input': 'mutations/role-collision.orm.yaml', 'source_artifact': 'role-collision.orm.yaml', 'source_commit': None}, {'expected_exit': 3, 'expected_rule': 'rai-import:ring-placement', 'id': 'N-RING-MISSING', 'input': 'mutations/ring-missing-target.orm.yaml', 'source_artifact': 'ring-missing-target.orm.yaml', 'source_commit': None}, {'expected_exit': 3, 'expected_rule': 'rai-import:provenance', 'id': 'N-PROVENANCE-NO-COMMIT', 'input': 'provenance.source.orm.yaml', 'source_artifact': 'provenance.source.orm.yaml', 'source_commit': None}, {'expected_exit': 3, 'expected_rule': 'rai-import:unsupported', 'id': 'N-OUTSIDE', 'input': 'mutations/outside-four-classes.orm.yaml', 'source_artifact': 'outside-four-classes.orm.yaml', 'source_commit': None}]
HOSTILE = [{'expected_exit': 3, 'expected_rule': 'rai-import:parse', 'generator': {'kind': 'hex', 'value': 'ff'}, 'id': 'H-INVALID-UTF8', 'input_bytes': 1, 'input_sha256': 'a8100ae6aa1940d0b663bb31cd466142ebbdbd5187131b92d93818987832eb89'}, {'expected_exit': 3, 'expected_rule': 'rai-import:parse', 'generator': {'kind': 'utf8', 'value': 'version: [\n'}, 'id': 'H-MALFORMED-YAML', 'input_bytes': 11, 'input_sha256': '5e7e04f69773587ef05800714cc633797c5c9b093962b225f7f0030548935d21'}, {'expected_exit': 3, 'expected_rule': 'rai-import:parse', 'generator': {'kind': 'utf8', 'value': 'version: 1\na: &a {}\nb: *a\n'}, 'id': 'H-YAML-ALIAS', 'input_bytes': 26, 'input_sha256': 'cd834de7d6efc3a78f18e04d034b3a0d1a9256d41a18fab2471d703627718d6e'}, {'expected_exit': 3, 'expected_rule': 'rai-import:parse', 'generator': {'kind': 'utf8', 'value': 'version: 1\n---\nversion: 1\n'}, 'id': 'H-MULTI-DOC', 'input_bytes': 26, 'input_sha256': 'ebe69e0e230b9e69797896ef66b6c8b3a84d5fbcb94f249893a77465b8df0071'}, {'expected_exit': 3, 'expected_rule': 'rai-import:parse', 'generator': {'kind': 'utf8', 'value': '- version\n- 1\n'}, 'id': 'H-NONMAPPING', 'input_bytes': 14, 'input_sha256': '7aaa111a26468c4f0e35aa0757bd9ad8ee4603227a9a4c37913306d5d7160330'}, {'expected_exit': 3, 'expected_rule': 'rai-import:parse', 'generator': {'kind': 'utf8', 'value': 'version: 1\nvalue: .nan\n'}, 'id': 'H-NONFINITE', 'input_bytes': 23, 'input_sha256': 'caacf8f28a231c5cbbbcc77a1a4081a870a62b786dc6a9ee1a12dcb930d9e16e'}, {'expected_exit': 3, 'expected_rule': 'rai-import:parse', 'generator': {'digits': 10001, 'kind': 'huge-integer'}, 'id': 'H-HUGE-INTEGER', 'input_bytes': 10020, 'input_sha256': 'ba986a465f2859558a8adc51daa63980511c77f1362722620d193b2afd277fa8'}, {'expected_exit': 3, 'expected_rule': 'rai-import:parse', 'generator': {'depth': 200, 'kind': 'deep-list'}, 'id': 'H-DEEP-NESTING', 'input_bytes': 420, 'input_sha256': '6e433d5d5011c908f2c42fe86674eb208f517187f1fe13e0d43a0e0f8c622f90'}, {'expected_exit': 3, 'expected_rule': 'rai-import:unsupported', 'generator': {'bytes': 10485760, 'kind': 'padded-unsupported'}, 'id': 'H-EXACT-CAP', 'input_bytes': 10485760, 'input_sha256': 'e3e4016a930b8a556d6fb4459ce7188aa6e68bed194bd13ac86c5b72524b6b4c'}, {'expected_exit': 74, 'expected_rule': 'rai-import:size', 'generator': {'bytes': 10485761, 'kind': 'padded-unsupported'}, 'id': 'H-OVER-CAP', 'input_bytes': 10485761, 'input_sha256': '708af4fa7362f03b98e2cc295836e5236c4a5ab8069b261557c024d20cd235bd'}]

def _run(case: dict[str, object], output: Path) -> subprocess.CompletedProcess[str]:
    argv = [sys.executable, '-m', 'gnd', 'import', 'rai-orm', str(IMPORT / str(case['input'])), '--out', str(output), '--source-artifact', str(case['source_artifact'])]
    if case['source_commit'] is not None:
        argv.extend(['--source-commit', str(case['source_commit'])])
    return subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, check=False)

def _assert_lane_exists(result: subprocess.CompletedProcess[str]) -> None:
    parser_refusal = "invalid choice: 'import'" in result.stderr
    assert not parser_refusal, 'expected corpus-first RED: the approved `gnd import rai-orm` production surface is still absent'

def _assert_exact(actual: bytes, expected: bytes) -> None:
    assert actual == expected

def _hostile_bytes(case: dict[str, object]) -> bytes:
    generator = case['generator']
    kind = generator['kind']
    if kind == 'hex':
        return bytes.fromhex(generator['value'])
    if kind == 'utf8':
        return generator['value'].encode()
    if kind == 'huge-integer':
        return ('version: 1\nvalue: ' + '9' * generator['digits'] + '\n').encode()
    if kind == 'deep-list':
        depth = generator['depth']
        return ('version: 1\nvalue: ' + '[' * depth + '0' + ']' * depth + '\n').encode()
    if kind == 'padded-unsupported':
        prefix = b'version: 1\nunsupported: true\n'
        return prefix + b'#' * (generator['bytes'] - len(prefix))
    raise AssertionError(f'unknown hostile generator: {kind}')

def test_import_harness_negative_control_rejects_one_dirty_byte() -> None:
    expected = (IMPORT / 'identity.expected.model.orm.yaml').read_bytes()
    with pytest.raises(AssertionError):
        _assert_exact(expected + b'# dirty\n', expected)

@pytest.mark.parametrize('case', NEGATIVE, ids=lambda row: row['id'])
def test_named_import_refusal(case: dict[str, object], tmp_path: Path) -> None:
    output = tmp_path / 'out'
    result = _run(case, output)
    _assert_lane_exists(result)
    assert result.returncode == case['expected_exit'], result.stderr
    assert case['expected_rule'] in result.stdout + result.stderr
    assert not output.exists()

@pytest.mark.parametrize('source', ['sample', 'common-sense', 'llm-inferred', 'imported'])
@pytest.mark.parametrize(('status', 'expected'), [('proposed', 'deontic'), ('confirmed', 'alethic')])
def test_every_d03_import_default_arm_is_reachable(source: str, status: str, expected: str) -> None:
    constraint: dict[str, object] = {'source': source, 'status': status}
    if source == 'imported' and status == 'confirmed':
        constraint['provenance'] = {'reviewed_in': 'owner-review'}
    assert _default_modality(constraint, '/constraint') == expected

def test_imported_confirmed_requires_reviewed_in() -> None:
    with pytest.raises(RaiImportError, match='reviewed_in'):
        _default_modality({'source': 'imported', 'status': 'confirmed', 'provenance': {}}, '/constraint')

@pytest.mark.parametrize('name', ['', 'rôle', 'bad-name'])
def test_invalid_role_names_refuse_by_name(name: str) -> None:
    with pytest.raises(RaiImportError, match='rai-import:role-name'):
        _snake(name, '/role')

@pytest.mark.parametrize('mutation', ['nonbinary', 'extra-key'])
def test_additional_ring_refusal_branches(mutation: str, tmp_path: Path) -> None:
    yaml = YAML(typ='rt')
    document = yaml.load((IMPORT / 'ring.source.orm.yaml').read_text(encoding='utf-8'))
    if mutation == 'nonbinary':
        document['fact_types'][0]['roles'].pop()
    else:
        document['constraints'][0]['dialect_extension'] = True
    stream = io.StringIO()
    yaml.dump(document, stream)
    source = tmp_path / 'ring.orm.yaml'
    source.write_text(stream.getvalue(), encoding='utf-8')
    request = RaiImportRequest(source, tmp_path / 'out', 'ring.orm.yaml', None)
    with pytest.raises(RaiImportError, match='rai-import:ring-placement'):
        plan_rai_import(request)

def test_deterministic_arbitrary_byte_prefixes_are_total() -> None:
    generator = random.Random(0)
    for size in range(1, 65):
        data = generator.randbytes(size) + b'\xff'
        with pytest.raises(RaiImportError):
            parse_rai_model_bytes(data, source='arbitrary.orm.yaml')

def test_import_command_level_exits_are_disjoint_and_publish_create_once(tmp_path: Path) -> None:
    source = IMPORT / 'identity.source.orm.yaml'
    output = tmp_path / 'out'
    output.mkdir()
    collision = subprocess.run([sys.executable, '-m', 'gnd', 'import', 'rai-orm', str(source), '--out', str(output), '--source-artifact', 'identity.source.orm.yaml'], cwd=ROOT, capture_output=True, text=True, check=False)
    assert collision.returncode == 11
    assert not tuple(output.iterdir())
    missing = subprocess.run([sys.executable, '-m', 'gnd', 'import', 'rai-orm', str(tmp_path / 'missing.yaml'), '--out', str(tmp_path / 'missing-out'), '--source-artifact', 'missing.yaml'], cwd=ROOT, capture_output=True, text=True, check=False)
    assert missing.returncode == 66
    usage = subprocess.run([sys.executable, '-m', 'gnd', 'import', 'rai-orm', str(source), '--out', str(tmp_path / 'x')], cwd=ROOT, capture_output=True, text=True, check=False)
    assert usage.returncode == 64
    assert '--source-artifact' in usage.stderr

@pytest.mark.parametrize('kind', ['file', 'symlink'])
def test_non_directory_output_leaf_is_io_not_collision(kind: str, tmp_path: Path) -> None:
    output = tmp_path / 'out'
    if kind == 'file':
        output.write_text('occupied\n', encoding='utf-8')
    else:
        os.symlink(tmp_path / 'missing-target', output)
    case = next(row for row in POSITIVE if row['id'] == 'I-IDENTITY')
    result = _run(case, output)
    assert result.returncode == 74
    assert 'rai-import:io' in result.stderr

def test_missing_output_parent_is_io_and_is_not_created(tmp_path: Path) -> None:
    output = tmp_path / 'missing-parent' / 'out'
    case = next(row for row in POSITIVE if row['id'] == 'I-IDENTITY')
    result = _run(case, output)
    assert result.returncode == 74
    assert 'rai-import:io' in result.stderr
    assert not output.parent.exists()

def test_empty_source_commit_is_a_named_input_refusal(tmp_path: Path) -> None:
    case = next(row for row in POSITIVE if row['id'] == 'I-IDENTITY')
    case_with_empty_commit = {**case, 'source_commit': ''}
    output = tmp_path / 'out'
    result = _run(case_with_empty_commit, output)
    assert result.returncode == 3
    assert 'rai-import:provenance' in result.stderr
    assert not output.exists()

def test_conflicting_existing_modality_is_a_named_refusal(tmp_path: Path) -> None:
    source = tmp_path / 'conflicting-modality.orm.yaml'
    source.write_bytes((IMPORT / 'role-name.source.orm.yaml').read_bytes().replace(b'modality: alethic', b'modality: deontic'))
    case = {'input': str(source), 'source_artifact': 'conflicting-modality.orm.yaml', 'source_commit': None}
    result = _run(case, tmp_path / 'out')
    assert result.returncode == 3
    assert 'rai-import:modality' in result.stderr

def test_repeated_unnamed_role_type_is_a_named_refusal(tmp_path: Path) -> None:
    source = tmp_path / 'ambiguous-roles.orm.yaml'
    source.write_text('version: 1\nsource: { kind: text-conversation, confidence: standard, mode: one-shot }\nobject_types:\n  - { id: item, name: Item, kind: value, primitive: String }\nfact_types:\n  - id: item_matches_item\n    reading: "{Item} matches {Item}"\n    roles:\n      - { object_type: item }\n      - { object_type: item }\n    constraints: []\nconstraints: []\nrejected_proposals: []\n', encoding='utf-8')
    case = {'input': str(source), 'source_artifact': 'ambiguous-roles.orm.yaml', 'source_commit': None}
    result = _run(case, tmp_path / 'out')
    assert result.returncode == 3
    assert 'rai-import:role-name' in result.stderr

def test_target_invalid_after_admitted_rewrite_is_named(tmp_path: Path) -> None:
    source = tmp_path / 'target-invalid.orm.yaml'
    source.write_bytes((IMPORT / 'role-name.source.orm.yaml').read_bytes().replace(b'version: 1\n', b'version: 1\nsurprise: true\n'))
    case = {'input': str(source), 'source_artifact': 'target-invalid.orm.yaml', 'source_commit': None}
    result = _run(case, tmp_path / 'out')
    assert result.returncode == 3
    assert 'rai-import:target-invalid' in result.stderr
    assert not (tmp_path / 'out').exists()

def test_publication_race_is_classified_as_collision(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    request = RaiImportRequest(tmp_path / 'input', tmp_path / 'out', 'input', None)
    result = RaiImportResult(b'model\n', b'{}\n', '0' * 64, '1' * 64, ())

    def collide(*_args: object, **_kwargs: object) -> object:
        raise ArtifactError('artifact publication collision: out already exists')
    monkeypatch.setattr('gnd.rai_import.publish_directory_once', collide)
    with pytest.raises(RaiImportCollision):
        publish_rai_import(request, result)

def test_unexpected_container_types_are_a_named_input_refusal(tmp_path: Path) -> None:
    source = tmp_path / 'hostile.orm.yaml'
    source.write_text('version: 1\nobject_types: []\nfact_types: [hostile]\nconstraints: []\n', encoding='utf-8')
    result = subprocess.run([sys.executable, '-m', 'gnd', 'import', 'rai-orm', str(source), '--out', str(tmp_path / 'out'), '--source-artifact', 'hostile.orm.yaml'], cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 3
    assert 'rai-import:unsupported' in result.stderr
    assert not (tmp_path / 'out').exists()

def test_ring_target_container_is_a_named_input_refusal(tmp_path: Path) -> None:
    source = tmp_path / 'hostile-ring.orm.yaml'
    source.write_text('version: 1\nobject_types: []\nfact_types: []\nconstraints:\n  - { type: ring, variant: acyclic, fact_type: { bad: shape } }\n', encoding='utf-8')
    result = subprocess.run([sys.executable, '-m', 'gnd', 'import', 'rai-orm', str(source), '--out', str(tmp_path / 'out'), '--source-artifact', 'hostile-ring.orm.yaml'], cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 3
    assert 'rai-import:ring-placement' in result.stderr
    assert not (tmp_path / 'out').exists()

def test_nested_role_reference_container_is_a_named_refusal(tmp_path: Path) -> None:
    source = tmp_path / 'hostile-role-ref.orm.yaml'
    source.write_text('version: 1\nobject_types:\n  - { id: item, name: Item, kind: value, primitive: String }\nfact_types:\n  - id: item_seen\n    reading: "{Item} is seen"\n    roles: [{ object_type: item, role_name: item }]\n    constraints:\n      - type: uniqueness\n        roles: [[hostile]]\n        source: explicit\n        status: confirmed\n        modality: alethic\n        provenance: { user_quote: Each item is seen once. }\nconstraints: []\nrejected_proposals: []\n', encoding='utf-8')
    result = subprocess.run([sys.executable, '-m', 'gnd', 'import', 'rai-orm', str(source), '--out', str(tmp_path / 'out'), '--source-artifact', 'hostile-role-ref.orm.yaml'], cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 3
    assert 'rai-import:unsupported' in result.stderr
    assert not (tmp_path / 'out').exists()

def test_provenance_anchor_must_identify_one_constraint(tmp_path: Path) -> None:
    source = tmp_path / 'ambiguous.orm.yaml'
    source.write_text('version: 1\nsource: { kind: text-conversation, confidence: standard, mode: one-shot }\nobject_types:\n  - { id: item, name: Item, kind: value, primitive: String }\n  - { id: code, name: Code, kind: value, primitive: String }\nfact_types:\n  - id: item_has_code\n    reading: "{Item} has {Code}"\n    roles:\n      - { object_type: item, role_name: item }\n      - { object_type: code, role_name: code }\n    constraints:\n      - { type: mandatory, role: item, source: explicit, status: confirmed, modality: alethic }\n      - { type: mandatory, role: code, source: explicit, status: confirmed, modality: alethic }\nconstraints: []\nrejected_proposals: []\n', encoding='utf-8')
    output = tmp_path / 'out'
    result = subprocess.run([sys.executable, '-m', 'gnd', 'import', 'rai-orm', str(source), '--out', str(output), '--source-artifact', 'ambiguous.orm.yaml', '--source-commit', 'abc123'], cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 3
    assert 'rai-import:provenance' in result.stderr
    assert not output.exists()

def test_provenance_walk_does_not_rescan_the_source_per_constraint() -> None:
    source = (ROOT / 'src/gnd/rai_import.py').read_text(encoding='utf-8')
    assert 'text.count(anchor)' not in source

@pytest.mark.parametrize('message', ['injected pre-manifest failure', 'artifact publication collision: injected raw I/O'])
def test_importer_pre_manifest_failure_leaves_no_partial_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, message: str) -> None:
    request = RaiImportRequest(tmp_path / 'input', tmp_path / 'out', 'input', None)
    result = RaiImportResult(b'model\n', b'{}\n', '0' * 64, '1' * 64, ())
    original = artifact_module._write_new_file_at
    calls = 0

    def fail_second(*args: object, **kwargs: object) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError(message)
        original(*args, **kwargs)
    monkeypatch.setattr(artifact_module, '_write_new_file_at', fail_second)
    with pytest.raises(RaiImportIO, match='injected'):
        publish_rai_import(request, result)
    assert not request.output_dir.exists()
    assert not tuple(tmp_path.glob('.gnd-staging-*'))

def test_cleanup_failure_still_leaves_no_completion_marker(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    request = RaiImportRequest(tmp_path / 'input', tmp_path / 'out', 'input', None)
    result = RaiImportResult(b'model\n', b'{}\n', '0' * 64, '1' * 64, ())
    original = artifact_module._write_new_file_at
    calls = 0

    def fail_manifest(*args: object, **kwargs: object) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError('injected manifest failure')
        original(*args, **kwargs)

    def fail_cleanup(*_args: object, **_kwargs: object) -> None:
        raise OSError('injected cleanup failure')
    monkeypatch.setattr(artifact_module, '_write_new_file_at', fail_manifest)
    monkeypatch.setattr(artifact_module, '_clear_directory_fd', fail_cleanup)
    with pytest.raises(RaiImportIO, match='manifest failure'):
        publish_rai_import(request, result)
    assert not (request.output_dir / 'aliases.json').exists()
