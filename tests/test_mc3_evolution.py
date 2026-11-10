"""MC3 corpus-first evolution boundaries; source controls are labelled separately."""
from __future__ import annotations

import copy
import hashlib
import json
import shutil
from pathlib import Path

import pytest
from support.cli_runner import run_main

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / 'tests/fixtures/mc-vocabulary'
ANSWERS = {r['id']: r for r in json.loads((CORPUS / 'answers.json').read_text())['cases']}


def read(path):
    return json.loads(path.read_text())


def write(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def sha(data):
    return hashlib.sha256(data).hexdigest()


@pytest.fixture
def work(tmp_path):
    folder = tmp_path / 'workspace'
    shutil.copytree(CORPUS, folder)
    return folder


def preview(work, proposal='combined.proposal.json', *extra):
    return run_main(['evolve', 'preview', str(work / 'project.orm.json'), str(work / proposal),
                     '--workspace', str(work), '--records', str(work / 'records'),
                     '--out', str(work / 'preview.json'), '--format', 'json', *extra])


def service(work):
    from gnd.evolve import EvolutionService

    return EvolutionService(model_path=work / 'project.orm.json', evidence_root=work / 'records',
                            allowed_project_root=work)


def proposal(work, name='combined.proposal.json'):
    from gnd.evolve import read_evolution_proposal_document

    return read_evolution_proposal_document(read(work / name))


def apply_cli(work):
    return run_main(['evolve', 'apply', str(work / 'project.orm.json'), str(work / 'combined.proposal.json'),
                     '--preview', str(work / 'preview.json'), '--workspace', str(work),
                     '--records', str(work / 'records'), '--format', 'json'])


def accept(work):
    from gnd.evolve.cli_service import _evolve_json_bytes

    current = service(work).preview(proposal(work))
    accepted = service(work).preview(proposal(work),
                                     accepted_blast_radius_sha256=current.blast_radius.report_sha256)
    (work / 'preview.json').write_bytes(_evolve_json_bytes(accepted))
    return accepted


def test_C01_retained_source_states(work):
    """Existing loader/check controls, already green before MC3."""
    for population, code in [('clean.pop.json', 0), ('cycle.pop.json', 1)]:
        result = run_main(['check', str(work / 'project.orm.json'), str(work / population), '--rule-ids'])
        assert result.returncode == code
    assert (work / 'vocabulary-v2.orm.json').exists()


@pytest.mark.parametrize('kind', ['add', 'modify', 'rename', 'delete'])
@pytest.mark.parametrize('target', ['object', 'fact', 'role'])
def test_C02_included_definitions_refuse_before_candidate_validation(work, kind, target):
    from gnd.evolve import EvolutionIncludeError, read_evolution_proposal_document

    vocabulary = read(work / 'vocabulary-v1.orm.json')
    value = copy.deepcopy(vocabulary['object_types'][0] if target == 'object' else
                          vocabulary['fact_types'][0] if target == 'fact' else
                          vocabulary['fact_types'][0]['roles'][0])
    locator = ({'locator_kind': 'role', 'fact_type_id': 'component_uses_component',
                'role_name': value['role_name']} if target == 'role' else
               {'locator_kind': 'element', 'collection': 'object_types' if target == 'object' else 'fact_types',
                'element_id': value['id']})
    after = copy.deepcopy(value)
    if kind == 'rename':
        after['role_name' if target == 'role' else 'id'] = 'replacement'
    operation = {'operation_id': 'readonly-probe', 'kind': kind, 'locator': locator}
    if kind != 'add':
        operation['before'] = value
    if kind != 'delete':
        operation['after'] = after
    document = read(work / 'combined.proposal.json')
    document['operations'] = [operation]
    with pytest.raises(EvolutionIncludeError, match=ANSWERS['C02']['reason']):
        service(work).preview(read_evolution_proposal_document(document))
    assert not (work / 'records').exists()


def test_C03_analysis_names_broken_owned_rule_and_never_stages(work):
    result = preview(work, 'repin-only.proposal.json')
    assert result.returncode == ANSWERS['C03']['preview_exit'], result.stdout + result.stderr
    radius = read(work / 'preview.json')
    assert radius['schema_version'] == 1 and 'validation' not in radius
    references = '\n'.join(row['reference'] for row in radius['entries'])
    assert all(name in references for name in ANSWERS['C03']['broken_owned_rules'])
    assert all(name not in references for name in ANSWERS['C03']['not_broken'])
    assert not (work / 'records').exists()
    assert apply_cli(work).returncode == ANSWERS['C03']['diagnostic_apply_exit']


def test_C04_combined_preview_accept_publish_check(work):
    before = {p.name: p.read_bytes() for p in work.glob('vocabulary*.json')}
    assert preview(work).returncode == ANSWERS['C04']['preview_exit']
    current = read(work / 'preview.json')
    assert current['breaking'] is True
    assert apply_cli(work).returncode == ANSWERS['C04']['unaccepted_apply_exit']
    accepted = accept(work)
    assert accepted.before_includes and accepted.candidate_includes
    assert accepted.before_includes[0].content.sha256 == read(work / 'project.orm.json')['includes'][0]['sha256']
    assert apply_cli(work).returncode == ANSWERS['C04']['accepted_apply_finalize_exit']
    authored = read(work / 'project.orm.json')
    assert authored == read(work / 'combined.orm.json') and 'object_types' not in authored and 'fact_types' not in authored
    assert {p.name: p.read_bytes() for p in work.glob('vocabulary*.json')} == before
    result = run_main(['check', str(work / 'project.orm.json'), str(work / 'v2-clean.pop.json')])
    assert result.returncode == ANSWERS['C04']['check_exit']


def test_C04_analysis_acceptance_cannot_authorize_combined(work):
    from gnd.evolve import EvolutionError
    from gnd.evolve.cli_service import _evolve_error_exit

    assert preview(work, 'repin-only.proposal.json').returncode == 3
    analysis_hash = read(work / 'preview.json')['report_sha256']
    with pytest.raises(EvolutionError) as caught:
        service(work).preview(proposal(work), accepted_blast_radius_sha256=analysis_hash)
    assert _evolve_error_exit(caught.value) == ANSWERS['C04']['wrong_analysis_acceptance_exit']


def test_C05_valid_flattened_candidate_refuses_authored_replay(work):
    assert run_main(['validate', str(work / 'flattened-negative.orm.json')]).returncode == 0
    result = preview(work, 'flattened.proposal.json')
    assert result.returncode == ANSWERS['C05']['preview_exit']
    assert ANSWERS['C05']['reason_contains'].encode() in result.stdout + result.stderr
    assert not (work / 'records').exists() and not (work / 'preview.json').exists()


@pytest.mark.parametrize('state', ['absent', 'overwritten'])
def test_C06_explicit_authenticated_previous_bytes(work, state):
    old = work / 'vocabulary-v1.orm.json'
    backup = work / 'retained-v1.yaml'
    backup.write_bytes(old.read_bytes())
    if state == 'absent':
        old.unlink()
    else:
        old.write_bytes((work / 'vocabulary-v2.orm.json').read_bytes())
    result = preview(work, 'combined.proposal.json', '--previous-include', 'components=retained-v1.yaml')
    assert result.returncode == ANSWERS['C06']['valid_previous_exit'], result.stdout + result.stderr
    assert read(work / 'preview.json')['before_includes'][0]['content']['sha256'] == sha(backup.read_bytes())
    backup.unlink()
    accept_from_file = read(work / 'preview.json')
    from gnd.evolve import EvolutionPreview
    from gnd.evolve.cli_service import _evolve_json_bytes
    from gnd.evolve.models import canonical_sha256

    accept_from_file['accepted_blast_radius_sha256'] = accept_from_file['blast_radius']['report_sha256']
    accept_from_file['preview_sha256'] = canonical_sha256({k: v for k, v in accept_from_file.items()
                                                          if k != 'preview_sha256'})
    (work / 'preview.json').write_bytes(_evolve_json_bytes(EvolutionPreview.model_validate(accept_from_file)))
    assert apply_cli(work).returncode == 0


@pytest.mark.parametrize('bindings', [['unknown=not-opened'], ['components='],
                                      ['components=missing', 'components=missing'],
                                      ['components=missing'] * 9])
def test_C07_invalid_previous_bindings_refuse_before_reads(work, bindings):
    result = preview(work, 'combined.proposal.json', *[arg for value in bindings
                                                     for arg in ('--previous-include', value)])
    assert result.returncode == ANSWERS['C07']['invalid_exit'], result.stdout + result.stderr
    assert not (work / 'records').exists() and not (work / 'preview.json').exists()


@pytest.mark.parametrize('field', ['id', 'path', 'sha256', 'content'])
def test_C08_snapshot_tampering_refuses(work, field):
    from gnd.evolve import read_evolution_preview_document

    assert preview(work).returncode == 0
    document = read(work / 'preview.json')
    snapshot = document['before_includes'][0]
    if field == 'content':
        snapshot['content']['text'] += ' '
    else:
        snapshot[field] = 'tampered'
    with pytest.raises(ValueError):
        read_evolution_preview_document(document)


def test_C10_candidate_changed_after_preview_refuses(work):
    accept(work)
    before = (work / 'project.orm.json').read_bytes()
    vocabulary = work / 'vocabulary-v2.orm.json'
    vocabulary.write_bytes(vocabulary.read_bytes() + b' ')
    result = apply_cli(work)
    assert result.returncode == ANSWERS['C10']['exit'], result.stdout + result.stderr
    assert (work / 'project.orm.json').read_bytes() == before


def test_C11_finalize_uses_history_but_requires_live_candidate(work):
    from gnd.evolve import EvolutionIncludeError

    accepted = accept(work)
    current_service = service(work)
    pending = current_service.apply(accepted)
    (work / 'vocabulary-v1.orm.json').unlink()
    candidate = work / 'vocabulary-v2.orm.json'
    exact = candidate.read_bytes()
    candidate.write_bytes(exact + b' ')
    with pytest.raises(EvolutionIncludeError):
        current_service.finalize(pending)
    candidate.write_bytes(exact)
    record = current_service.finalize(pending)
    assert record == current_service.finalize(pending)
    assert 'fact_types' not in read(work / 'project.orm.json')


@pytest.mark.parametrize('version', [1, 2])
def test_C15_old_proposal_readers_refuse_new_graph_before_execution(work, version):
    """Expected parser refusal; existing closed graph already refuses the unknown kind."""
    from gnd.evolve import read_evolution_proposal_document

    document = read(work / 'combined.proposal.json')
    document['schema_version'] = version
    with pytest.raises(ValueError):
        read_evolution_proposal_document(document)


@pytest.mark.parametrize('identifier', ['model', ' stale ', 'a=b', 'line\n"[]', 'é'])
def test_C16_include_reference_is_unstripped_and_injective(identifier):
    from gnd.evolve import IncludeLocator

    locator = IncludeLocator(include_id=identifier)
    assert locator.include_id == identifier
    assert locator.reference() == 'includes[' + json.dumps(identifier, ensure_ascii=True) + ']'
