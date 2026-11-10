"""MC3 corpus-first evolution boundaries; source controls are labelled separately."""
from __future__ import annotations

import copy
import hashlib
import json
import shutil
from pathlib import Path
from unittest.mock import patch

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


def apply_cli(work, *, accepted=False):
    answer = read(work / 'preview.json')['blast_radius']['report_sha256'] if accepted else None
    with patch('builtins.input', return_value=answer, side_effect=None if accepted else EOFError):
        return run_main(['evolve', 'apply', str(work / 'project.orm.json'), str(work / 'combined.proposal.json'),
                     '--preview', str(work / 'preview.json'), '--workspace', str(work),
                     '--records', str(work / 'records'), '--format', 'json'])


def accept(work):
    from gnd.evolve.cli_service import _evolve_json_bytes

    current = service(work).preview(proposal(work))
    accepted = service(work).preview(proposal(work),
                                     accepted_blast_radius_sha256=current.blast_radius.report_sha256)
    (work / 'preview.json').write_bytes(_evolve_json_bytes(current))
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
    assert apply_cli(work, accepted=True).returncode == ANSWERS['C04']['accepted_apply_finalize_exit']
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
    assert apply_cli(work, accepted=True).returncode == 0


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


def test_publication_rechecks_after_staging_before_cas(work):
    import gnd.evolve.service as runtime
    from gnd.evolve import EvolutionIncludeError

    accepted = accept(work)
    exact = (work / 'project.orm.json').read_bytes()
    original = runtime.safe_destination

    def mutate(root, relative):
        destination = original(root, relative)
        if Path(root) == work and relative == 'project.orm.json':
            vocabulary = work / 'vocabulary-v2.orm.json'
            vocabulary.write_bytes(vocabulary.read_bytes() + b' ')
        return destination

    with (patch.object(runtime, 'safe_destination', side_effect=mutate),
          pytest.raises(EvolutionIncludeError)):
        service(work).apply(accepted)
    assert (work / 'project.orm.json').read_bytes() == exact


def test_already_live_retry_requires_live_candidate(work):
    from gnd.evolve import EvolutionIncludeError

    accepted = accept(work)
    current = service(work)
    pending = current.apply(accepted)
    vocabulary = work / 'vocabulary-v2.orm.json'
    original = vocabulary.read_bytes()
    vocabulary.write_bytes(original + b' ')
    with pytest.raises(EvolutionIncludeError):
        current.apply(accepted)
    vocabulary.write_bytes(original)
    assert current.apply(accepted) == pending


def test_verbalization_destination_cannot_replace_old_included_input(work):
    from gnd.evolve import EvolutionIncludeError, EvolutionService

    accepted = accept(work)
    source = work / 'vocabulary-v1.orm.json'
    exact = source.read_bytes()
    current = EvolutionService(model_path=work / 'project.orm.json', evidence_root=work / 'records',
                               allowed_project_root=work, verbalization_path=source)
    with pytest.raises(EvolutionIncludeError):
        current.apply(accepted)
    assert source.read_bytes() == exact
    assert not (work / 'records').exists()


def test_additive_repin_is_an_explicit_policy_refusal(work):
    reviewed = service(work).preview(proposal(work), policy='additive')
    assert reviewed.policy_issues
    assert any(issue.cell == 'include.repin-include' for issue in reviewed.policy_issues)


def test_discovery_preserves_authored_root_and_attaches_to_included_host(tmp_path):
    from gnd.discover.service import _proposal_bytes, discover
    from gnd.evolve import read_evolution_proposal_document
    from gnd.model import load_model, parse_model_document

    corpus = ROOT / 'tests/fixtures/induced_knowledge/ik4-corpus'
    vocabulary = tmp_path / 'staff-shared.orm.yaml'
    shutil.copyfile(corpus / 'staff.orm.yaml', vocabulary)
    model = tmp_path / 'staff.orm.yaml'
    authored = {'version': 5, 'model_id': 'ik4-staff', 'includes': [
        {'id': 'staff', 'path': vocabulary.name, 'sha256': sha(vocabulary.read_bytes())}]}
    write(model, authored)
    population = tmp_path / 'staff.population.yaml'
    shutil.copyfile(corpus / population.name, population)
    result = discover(model, population, families=('mandatory', 'uniqueness'),
                      max_values=10, max_pairs=10)
    raw, fits = _proposal_bytes(result, 'fixture', '2026-11-10T00:00:00Z', population)
    assert fits
    built = read_evolution_proposal_document(json.loads(raw))
    candidate = parse_model_document(built.candidate_model.text.encode(), source=model)
    assert candidate['includes'] == authored['includes']
    assert not candidate.get('fact_types')
    assert candidate['fact_type_constraints']
    assert all(op.locator.host == 'included_fact_type' for op in built.operations)
    before = vocabulary.read_bytes()
    current = service_for_paths(model, tmp_path)
    reviewed = current.preview(built)
    record = current.finalize(current.apply(reviewed))
    assert record.new_model_sha256 == sha(model.read_bytes())
    assert load_model(model).includes
    assert vocabulary.read_bytes() == before


def service_for_paths(model, root):
    from gnd.evolve import EvolutionService

    return EvolutionService(model_path=model, evidence_root=root / 'records', allowed_project_root=root)


@pytest.mark.parametrize('remove', [False, True])
def test_owned_population_positions_include_vocabulary_prefix(work, remove):
    from gnd.evolve import ConstraintLocator, EvolutionOperation, EvolutionOperationKind
    from gnd.evolve.models import canonical_sha256
    from gnd.evolve.population_check import constraint_placements
    from gnd.evolve.service import _apply_declared_operations, _final_constraint_host
    from gnd.model import load_model_bytes_composed

    rule = copy.deepcopy(read(work / 'project.orm.json')['fact_type_constraints'][0]['constraints'][0])
    rule['id'] = 'new_owned_rule'
    locator = ConstraintLocator(host='included_fact_type', host_id='component_uses_component', family=rule['type'])
    operations = [EvolutionOperation(operation_id='new', kind=EvolutionOperationKind.ADD, locator=locator, after=rule)]
    if remove:
        deletion = locator.model_copy(update={'canonical_before_sha256': canonical_sha256(rule),
                                              'duplicate_occurrence': 0})
        operations.append(EvolutionOperation(operation_id='remove', kind=EvolutionOperationKind.DELETE,
                                             locator=deletion, before=rule))
    placed = []
    document = _apply_declared_operations(read(work / 'project.orm.json'), operations, placed=placed)
    candidate = load_model_bytes_composed(json.dumps(document).encode(), source=work / 'project.orm.json', root=work)
    positions = constraint_placements(placed, _final_constraint_host(document, candidate))
    assert positions == ({} if remove else {0: ('component_uses_component', 2)})


@pytest.mark.parametrize('document', [None, 0, [], 'x', {'fact_types': 1},
                                     {'fact_types': [None]}, {'fact_type_constraints': [{'constraints': 1}]}])
def test_owned_dependency_walk_refuses_hostile_json(document):
    from gnd.evolve._includes import IncludeInputError, owned_impact

    with pytest.raises(IncludeInputError):
        owned_impact(document, frozenset({'component'}))


@pytest.mark.parametrize('values', [[], 0, 'x', {'unknown': b'x'}, {'components': 'not bytes'}])
def test_previous_api_inputs_are_typed_refusals(work, values):
    from gnd.evolve import EvolutionIncludeError

    with pytest.raises(EvolutionIncludeError):
        service(work).preview(proposal(work), previous_includes=values)


@pytest.mark.parametrize('alias', ['hardlink', 'symlink'])
def test_output_alias_cannot_target_vocabulary(work, alias):
    from gnd.evolve import EvolutionIncludeError, EvolutionService

    accepted = accept(work)
    source = work / 'vocabulary-v1.orm.json'
    output = work / 'vocabulary-output.json'
    if alias == 'hardlink':
        output.hardlink_to(source)
    else:
        output.symlink_to(source)
    current = EvolutionService(model_path=work / 'project.orm.json', evidence_root=work / 'records',
                               allowed_project_root=work, verbalization_path=output)
    with pytest.raises(EvolutionIncludeError):
        current.apply(accepted)
    assert not (work / 'records').exists()


def test_last_verification_order_is_literal():
    import inspect

    from gnd.evolve import EvolutionService

    source = inspect.getsource(EvolutionService.apply)
    tail = source[source.rindex('safe_destination(self.allowed_project_root, self._model_relative)'):]
    assert tail.index('_verified_include_preview(') < tail.index('_atomic_write(')


def test_twenty_thousand_element_ownership_and_dependencies_are_bounded(work):
    import time

    from gnd.evolve import ElementLocator, EvolutionOperation, EvolutionOperationKind
    from gnd.evolve._includes import enforce_ownership, owned_impact
    from gnd.model import load_model

    vocabulary = read(work / 'vocabulary-v1.orm.json')
    vocabulary['object_types'].extend({'id': f'value_{i}', 'name': f'Value{i}', 'kind': 'value',
                                      'primitive': 'String'} for i in range(20_000))
    write(work / 'vocabulary-v1.orm.json', vocabulary)
    document = read(work / 'project.orm.json')
    document['includes'][0]['sha256'] = sha((work / 'vocabulary-v1.orm.json').read_bytes())
    write(work / 'project.orm.json', document)
    model = load_model(work / 'project.orm.json')
    operations = tuple(EvolutionOperation(operation_id=f'add-{i}', kind=EvolutionOperationKind.ADD,
                       locator=ElementLocator(collection='object_types', element_id=f'own_{i}'),
                       after={'id': f'own_{i}', 'name': f'Own{i}', 'kind': 'value', 'primitive': 'String'})
                       for i in range(20_000))
    owned = {'operations': [{'id': f'op_{i}', 'input': f'value_{i}'} for i in range(20_000)]}
    started = time.perf_counter()
    enforce_ownership(model, document, operations)
    affected = owned_impact(owned, frozenset(f'value_{i}' for i in range(20_000)))
    duration = time.perf_counter() - started
    assert len(affected) == 20_000
    assert duration < 3, duration


def padded_proposal(work, padding):
    from gnd.evolve import read_evolution_proposal_document
    from gnd.evolve.models import CommittedText

    for name in ('vocabulary-v1.orm.json', 'vocabulary-v2.orm.json'):
        path = work / name
        path.write_bytes(path.read_bytes() + b' ' * padding)
    root = read(work / 'project.orm.json')
    candidate = read(work / 'combined.orm.json')
    root['includes'][0]['sha256'] = sha((work / 'vocabulary-v1.orm.json').read_bytes())
    candidate['includes'][0]['sha256'] = sha((work / 'vocabulary-v2.orm.json').read_bytes())
    write(work / 'project.orm.json', root)
    value = read(work / 'combined.proposal.json')
    value['expected_model_sha256'] = sha((work / 'project.orm.json').read_bytes())
    value['operations'][0]['before'] = root['includes'][0]
    value['operations'][0]['after'] = candidate['includes'][0]
    value['candidate_model'] = CommittedText.from_text(json.dumps(candidate), media_type='application/yaml').model_dump(mode='json')
    return read_evolution_proposal_document(value)


@pytest.mark.parametrize('padding, admitted', [(5 * 1024 * 1024 - 65536, True),
                                               (5 * 1024 * 1024 + 65536, False)])
def test_snapshot_bundle_uses_existing_claim_cap(work, padding, admitted):
    from gnd.evolve import EvolutionIncludeError

    current = padded_proposal(work, padding)
    if admitted:
        reviewed = service(work).preview(current)
        assert reviewed.before_includes and reviewed.candidate_includes
        from gnd.evolve import EvolutionPreview
        from gnd.evolve.cli_service import _evolve_json_bytes, _evolve_read_claim

        claim = work / 'near-cap-preview.json'
        claim.write_bytes(_evolve_json_bytes(reviewed))
        assert _evolve_read_claim(claim, EvolutionPreview, label='near-cap preview',
                                  anchor=work, relative=claim.name) == reviewed
    else:
        with pytest.raises(EvolutionIncludeError, match='cap'):
            service(work).preview(current)
    assert not (work / 'records').exists()


def test_ilp_prepare_import_and_mined_inputs_keep_authored_includer(tmp_path):
    from gnd.evolve import read_evolution_proposal_document
    from gnd.export.ilp_service import _load_candidate, _prepare, load_mined_inputs
    from gnd.model import parse_model_document

    source = ROOT / 'src/gnd/examples/refunds'
    shutil.copytree(source, tmp_path / 'refunds')
    root = tmp_path / 'refunds'
    model = root / 'model.orm.yaml'
    vocabulary = root / 'shared.orm.yaml'
    model.rename(vocabulary)
    write(model, {'version': 5, 'model_id': 'refunds', 'includes': [
        {'id': 'refunds', 'path': vocabulary.name, 'sha256': sha(vocabulary.read_bytes())}]})
    labels = read(root / 'labels.json')
    labels['model_sha256'] = sha(model.read_bytes())
    write(root / 'labels.json', labels)
    exact = vocabulary.read_bytes()
    prepared = _prepare(model, root / 'labels.json', 'rules')
    assert prepared.model.includes
    assert not prepared.document.get('fact_types')
    assert _load_candidate(prepared, [], model).includes
    mined = load_mined_inputs(model, root / 'batches/north.yaml')
    assert mined.model.includes and not mined.document.get('fact_types')
    out = root / 'export'
    result = run_main(['export', 'ilp', str(model), '--labels', str(root / 'labels.json'),
                       '--target', 'rules', '--out', str(out)])
    assert result.returncode == 0, result.stderr
    run = read(root / 'learners/rules/run.json')
    run['export_sha256'] = sha((out / 'export.json').read_bytes())
    write(root / 'run.json', run)
    proposal_path = root / 'proposal.json'
    result = run_main(['import', 'ilp-rules', str(model), str(root / 'learners/rules/ruleset.txt'),
                       '--labels', str(root / 'labels.json'), '--reported-coverage', str(root / 'run.json'),
                       '--target', 'rules', '--out', str(proposal_path), '--format', 'json'])
    assert result.returncode == 0, result.stdout + result.stderr
    built = read_evolution_proposal_document(read(proposal_path))
    candidate = parse_model_document(built.candidate_model.text.encode(), source=model)
    assert candidate['includes'] == read(model)['includes']
    assert not candidate.get('fact_types')
    assert candidate['constraints']
    assert service_for_paths(model, root).preview(built).validation.valid
    assert vocabulary.read_bytes() == exact


@pytest.mark.parametrize('proposal_name', ['combined.proposal.json', 'repin-only.proposal.json'])
def test_preview_output_cannot_create_missing_historical_input(work, proposal_name):
    old = work / 'vocabulary-v1.orm.json'
    shutil.copyfile(old, work / 'backup.json')
    old.unlink()
    result = preview(work, proposal_name, '--previous-include', 'components=backup.json',
                     '--out', str(old))
    assert result.returncode == 3, result.stdout + result.stderr
    assert not old.exists()


@pytest.mark.parametrize('host', ['fact_type', 'included_fact_type'])
def test_anonymous_duplicates_bind_owned_occurrences_only(work, host):
    from gnd.evolve import EvolutionIncludeError, read_evolution_proposal_document
    from gnd.evolve.models import CommittedText, canonical_sha256
    from gnd.model import load_model

    vocabulary = read(work / 'vocabulary-v1.orm.json')
    rule = vocabulary['fact_types'][0]['constraints'][0]
    rule.pop('id')
    write(work / 'vocabulary-v1.orm.json', vocabulary)
    document = read(work / 'project.orm.json')
    document['includes'][0]['sha256'] = sha((work / 'vocabulary-v1.orm.json').read_bytes())
    document['fact_type_constraints'][0]['constraints'] = [copy.deepcopy(rule), copy.deepcopy(rule)]
    write(work / 'project.orm.json', document)
    candidate = copy.deepcopy(document)
    candidate['fact_type_constraints'][0]['constraints'].pop()
    value = read(work / 'combined.proposal.json')
    value['expected_model_sha256'] = sha((work / 'project.orm.json').read_bytes())
    value['operations'] = [{'operation_id': 'delete-second-owned', 'kind': 'delete', 'before': rule,
        'locator': {'locator_kind': 'constraint', 'host': host, 'host_id': 'component_uses_component',
                    'family': rule['type'], 'canonical_before_sha256': canonical_sha256(rule),
                    'duplicate_occurrence': 1}}]
    value['candidate_model'] = CommittedText.from_text(json.dumps(candidate), media_type='application/yaml').model_dump(mode='json')
    built = read_evolution_proposal_document(value)
    current = service(work)
    if host == 'fact_type':
        with pytest.raises(EvolutionIncludeError, match='included-element'):
            current.preview(built)
    else:
        reviewed = current.preview(built)
        accepted = current.preview(built, accepted_blast_radius_sha256=reviewed.blast_radius.report_sha256)
        current.finalize(current.apply(accepted))
        assert len(read(work / 'project.orm.json')['fact_type_constraints'][0]['constraints']) == 1
        assert len(load_model(work / 'project.orm.json').fact_types[0]['constraints']) == 2


def test_reference_mutation_refuses_before_candidate_dependency_io(work):
    import gnd.model as loader
    from gnd.evolve import EvolutionIncludeError, read_evolution_proposal_document
    from gnd.evolve.models import CommittedText

    value = read(work / 'combined.proposal.json')
    candidate = read(work / 'combined.orm.json')
    candidate['reference_populations'] = [None]
    value['candidate_model'] = CommittedText.from_text(json.dumps(candidate), media_type='application/yaml').model_dump(mode='json')
    with (patch.object(loader, '_composed_view', wraps=loader._composed_view) as composed,
          pytest.raises(EvolutionIncludeError, match='reference populations')):
        service(work).preview(read_evolution_proposal_document(value))
    assert composed.call_count == 1  # Verified current input only.


def test_historical_snapshot_refuses_existing_symlink(work):
    from gnd.evolve import EvolutionIncludeError

    accepted = accept(work)
    old = work / 'vocabulary-v1.orm.json'
    old.unlink()
    old.symlink_to(work / 'vocabulary-v2.orm.json')
    with pytest.raises(EvolutionIncludeError, match='include:unreadable'):
        service(work).apply(accepted)
    assert not (work / 'records').exists()


@pytest.mark.parametrize('mode', ['related', 'unrelated', 'ownership', 'ordinary'])
def test_C09_operation_priorities_and_unrelated_control(work, mode):
    import gnd.model as loader
    from gnd.evolve import (
        EvolutionIncludeError,
        EvolutionOperationsGatedError,
        read_evolution_proposal_document,
    )
    from gnd.evolve.models import CommittedText

    related = mode != 'unrelated'
    fact = 'component_uses_component' if related else 'component_has_owner'
    bindings = {'using': '$a', 'used': '$b'} if related else {'component': '$a', 'owner': '$b'}
    operation = {'id': 'record_use', 'reading': 'record one relationship',
        'parameters': [{'name': 'a', 'object_type': 'component'},
                       {'name': 'b', 'object_type': 'component' if related else 'owner'}],
        'preconditions': [], 'effects': [{'assert': {'fact_type': fact, 'bind': bindings}}],
        'frame': {'modality': 'alethic'}, 'source': 'explicit', 'status': 'confirmed',
        'provenance': {'user_quote': 'Record the relationship.'}}
    document = read(work / 'project.orm.json')
    document['operations'] = [operation]
    write(work / 'project.orm.json', document)
    name = 'repin-only' if mode == 'related' else 'combined'
    value = read(work / f'{name}.proposal.json')
    candidate = read(work / f'{name}.orm.json')
    candidate['operations'] = [operation]
    value['expected_model_sha256'] = sha((work / 'project.orm.json').read_bytes())
    if mode == 'ownership':
        value['operations'] = [{'operation_id': 'readonly', 'kind': 'delete',
            'locator': {'locator_kind': 'element', 'collection': 'fact_types', 'element_id': fact},
            'before': read(work / 'vocabulary-v1.orm.json')['fact_types'][0]}]
    if mode == 'ordinary':
        value['operations'] = [{'operation_id': 'change-operation', 'kind': 'modify',
            'locator': {'locator_kind': 'element', 'collection': 'operations', 'element_id': operation['id']},
            'before': operation, 'after': {**operation, 'reading': 'new wording'}}]
    value['candidate_model'] = CommittedText.from_text(json.dumps(candidate), media_type='application/yaml').model_dump(mode='json')
    built = read_evolution_proposal_document(value)
    with patch.object(loader, '_composed_view', wraps=loader._composed_view) as composed:
        if mode == 'unrelated':
            assert service(work).preview(built).validation.valid
        else:
            error = EvolutionIncludeError if mode == 'ownership' else EvolutionOperationsGatedError
            with pytest.raises(error):
                service(work).preview(built)
            assert composed.call_count == (2 if mode == 'related' else 1)


def test_C12_linked_preview_forged_apply_and_finalize_refuse(work):
    from gnd.artifacts import canonical_json_bytes
    from gnd.evolve import (
        EvolutionIncludeError,
        read_evolution_finalization_state_document,
        read_evolution_preview_document,
        read_evolution_proposal_document,
    )
    from gnd.evolve.models import canonical_sha256

    current = service(work)
    reviewed = accept(work)
    value = reviewed.proposal.model_dump(mode='json')
    value['linked_projects'] = [{'project_id': 'linked',
        'locator': {'base': 'allowed-project-root', 'path': 'linked'},
        'tracked_roster': {'paths': ['project.txt']}, 'expected_tracked_tree_sha256': '0' * 64}]
    linked = read_evolution_proposal_document(value)
    with pytest.raises(EvolutionIncludeError, match='unsupported-route'):
        current.preview(linked)
    value = linked.model_dump(mode='json')
    forged = reviewed.model_dump(mode='json')
    forged['proposal'] = value
    forged['proposal_sha256'] = linked.proposal_sha256
    radius = forged['blast_radius']
    radius['proposal_sha256'] = linked.proposal_sha256
    radius['report_sha256'] = canonical_sha256({k: v for k, v in radius.items() if k != 'report_sha256'})
    forged['accepted_blast_radius_sha256'] = radius['report_sha256']
    forged['preview_sha256'] = canonical_sha256({k: v for k, v in forged.items() if k != 'preview_sha256'})
    forged = read_evolution_preview_document(forged)
    with pytest.raises(EvolutionIncludeError, match='unsupported-route'):
        current.apply(forged)
    assert not (work / 'records').exists()
    pending = current.apply(reviewed)
    stage = work / 'records' / linked.proposal_id
    (stage / 'proposal.json').write_bytes(canonical_json_bytes(linked))
    (stage / 'preview.json').write_bytes(canonical_json_bytes(forged))
    intent = read(stage / 'intent.json')
    intent.update(proposal_sha256=linked.proposal_sha256, preview_sha256=forged.preview_sha256,
                  blast_radius_sha256=radius['report_sha256'], accepted_blast_radius_sha256=radius['report_sha256'],
                  linked_projects=value['linked_projects'])
    (stage / 'intent.json').write_bytes(canonical_json_bytes(intent))
    state = pending.model_dump(mode='json')
    state.update(proposal_sha256=linked.proposal_sha256, preview_sha256=forged.preview_sha256,
                 intent_sha256=sha((stage / 'intent.json').read_bytes()), linked_projects=value['linked_projects'])
    state['state_identity_sha256'] = canonical_sha256({k: v for k, v in state.items() if k != 'state_identity_sha256'})
    state = read_evolution_finalization_state_document(state)
    (stage / 'pending.json').write_bytes(canonical_json_bytes(state))
    with pytest.raises(EvolutionIncludeError, match='unsupported-route'):
        current.finalize(state)
    assert not (stage / 'record.json').exists()


def test_C07_backup_suffix_never_selects_original_parser(work):
    import io

    from ruamel.yaml import YAML

    stream = io.StringIO()
    YAML().dump(read(work / 'vocabulary-v1.orm.json'), stream)
    raw = stream.getvalue().encode()
    backup = work / 'old-vocabulary.yaml'
    backup.write_bytes(raw)
    document = read(work / 'project.orm.json')
    document['includes'][0]['sha256'] = sha(raw)
    write(work / 'project.orm.json', document)
    value = read(work / 'combined.proposal.json')
    value['expected_model_sha256'] = sha((work / 'project.orm.json').read_bytes())
    value['operations'][0]['before'] = document['includes'][0]
    write(work / 'combined.proposal.json', value)
    (work / 'vocabulary-v1.orm.json').unlink()
    result = preview(work, 'combined.proposal.json', '--previous-include', f'components={backup.name}')
    assert result.returncode == 3, result.stdout + result.stderr
    assert not (work / 'preview.json').exists()


def test_C08_untouched_dependency_must_stay_live(work):
    from gnd.evolve import EvolutionIncludeError, read_evolution_proposal_document
    from gnd.evolve.models import CommittedText

    other = work / 'other.json'
    write(other, {'version': 1, 'object_types': [{'id': 'extra', 'name': 'Extra', 'kind': 'value', 'primitive': 'String'}],
                  'fact_types': []})
    declaration = {'id': 'other', 'path': other.name, 'sha256': sha(other.read_bytes())}
    document = read(work / 'project.orm.json')
    document['includes'].append(declaration)
    write(work / 'project.orm.json', document)
    value = read(work / 'combined.proposal.json')
    candidate = read(work / 'combined.orm.json')
    candidate['includes'].append(declaration)
    value['candidate_model'] = CommittedText.from_text(json.dumps(candidate), media_type='application/yaml').model_dump(mode='json')
    value['expected_model_sha256'] = sha((work / 'project.orm.json').read_bytes())
    built = read_evolution_proposal_document(value)
    current = service(work)
    reviewed = current.preview(built)
    accepted = current.preview(built, accepted_blast_radius_sha256=reviewed.blast_radius.report_sha256)
    (work / 'vocabulary-v1.orm.json').unlink()
    exact = other.read_bytes()
    other.write_bytes(exact + b' ')
    with pytest.raises(EvolutionIncludeError):
        current.apply(accepted)
    assert not (work / 'records').exists()
    other.write_bytes(exact)
    current.finalize(current.apply(accepted))


def test_C13_cli_pretty_claim_must_fit_existing_cap(work):
    from gnd.artifacts import canonical_json_bytes
    from gnd.evolve.cli_service import _evolve_json_bytes
    from gnd.evolve.service import MAX_EVOLUTION_PROPOSAL_BYTES

    baseline = service(work).preview(padded_proposal(work, 0))
    padding = (MAX_EVOLUTION_PROPOSAL_BYTES - len(canonical_json_bytes(baseline)) - 256) // 2
    built = padded_proposal(work, padding)
    reviewed = service(work).preview(built)
    assert len(canonical_json_bytes(reviewed)) <= MAX_EVOLUTION_PROPOSAL_BYTES < len(_evolve_json_bytes(reviewed))
    (work / 'combined.proposal.json').write_bytes(canonical_json_bytes(built))
    result = preview(work)
    assert result.returncode == 3, result.stdout + result.stderr
    assert not (work / 'preview.json').exists()


def test_C13_analysis_cap_refuses_before_output(work, monkeypatch):
    import gnd.evolve.service as runtime
    from gnd.artifacts import canonical_json_bytes
    from gnd.evolve import EvolutionIncludeAnalysis, EvolutionIncludeError

    with pytest.raises(EvolutionIncludeAnalysis) as caught:
        service(work).preview(proposal(work, 'repin-only.proposal.json'))
    cap = len(canonical_json_bytes(caught.value.radius)) - 1
    monkeypatch.setattr(runtime, 'MAX_EVOLUTION_PROPOSAL_BYTES', cap)
    with pytest.raises(EvolutionIncludeError, match='cap') as oversized:
        service(work).preview(proposal(work, 'repin-only.proposal.json'))
    assert not isinstance(oversized.value, EvolutionIncludeAnalysis)
    assert not (work / 'records').exists()


@pytest.mark.parametrize('version', [1, 2])
def test_C15_old_preview_and_record_graphs_refuse_include_fields(work, version):
    from gnd.evolve import read_evolution_preview_document, read_evolution_record_document

    reviewed = accept(work)
    preview_value = reviewed.model_dump(mode='json')
    preview_value['schema_version'] = version
    with pytest.raises(ValueError):
        read_evolution_preview_document(preview_value)
    current = service(work)
    record = current.finalize(current.apply(reviewed))
    record_value = record.model_dump(mode='json')
    record_value['schema_version'] = version
    with pytest.raises(ValueError):
        read_evolution_record_document(record_value)


def test_C14_mined_import_candidate_and_preview_keep_authored_root(tmp_path):
    from gnd.evolve import read_evolution_proposal_document
    from gnd.model import parse_model_document

    corpus = ROOT / 'tests/fixtures/ilp_learners/il4'
    vocabulary = tmp_path / 'shared.orm.yaml'
    shutil.copyfile(corpus / 'model.orm.yaml', vocabulary)
    model = tmp_path / 'model.orm.yaml'
    from gnd.model import load_model
    identifier = load_model(vocabulary).model_id
    write(model, {'version': 5, 'model_id': identifier, 'includes': [
        {'id': 'shared', 'path': vocabulary.name, 'sha256': sha(vocabulary.read_bytes())}]})
    population = tmp_path / 'population.yaml'
    shutil.copyfile(corpus / 'population.yaml', population)
    out = tmp_path / 'facts'
    exported = run_main(['export', 'ilp', str(model), '--population', str(population),
                         '--target', 'amie', '--out', str(out)])
    assert exported.returncode == 0, exported.stderr
    case = next(case for case in read(corpus / 'rules.json')['import'] if case['id'] == 'a2')
    rules = tmp_path / 'rules.txt'
    rules.write_text('\n'.join(case['rules']) + '\n')
    reported = tmp_path / 'reported.json'
    write(reported, {'schema_version': 'gnd-mined-run/1', 'learner': {'name': 'amie', 'version': '4.0.0'},
                     'rules_sha256': sha(rules.read_bytes()), 'population_sha256': sha(population.read_bytes()),
                     'facts_sha256': sha((out / 'amie/facts.tsv').read_bytes())})
    target = tmp_path / 'proposal.json'
    imported = run_main(['import', 'mined-rules', str(model), str(rules), '--population', str(population),
                         '--reported', str(reported), '--target', 'amie', '--out', str(target),
                         '--actor', 'mc3-test', '--requested-at', '2026-01-01T00:00:00Z', '--format', 'json'])
    assert imported.returncode == 0, imported.stdout + imported.stderr
    built = read_evolution_proposal_document(read(target))
    candidate = parse_model_document(built.candidate_model.text.encode(), source=model)
    assert not candidate.get('fact_types') and candidate['includes'] == read(model)['includes']
    assert service_for_paths(model, tmp_path).preview(built).validation.valid


def test_repeated_attachment_entries_use_global_owned_occurrences_and_prune(work):
    from gnd.evolve import ConstraintLocator, EvolutionOperation, EvolutionOperationKind
    from gnd.evolve.models import canonical_sha256
    from gnd.evolve.service import _apply_declared_operations

    document = read(work / 'project.orm.json')
    rule = document['fact_type_constraints'][0]['constraints'][0]
    rule.pop('id')
    document['fact_type_constraints'].append(copy.deepcopy(document['fact_type_constraints'][0]))
    locator = ConstraintLocator(host='included_fact_type', host_id='component_uses_component', family=rule['type'],
                                canonical_before_sha256=canonical_sha256(rule), duplicate_occurrence=1)
    deleted = EvolutionOperation(operation_id='delete-last', kind=EvolutionOperationKind.DELETE,
                                 locator=locator, before=rule)
    changed = {**rule, 'rationale': 'A distinct owned rule.'}
    added = EvolutionOperation(operation_id='append', kind=EvolutionOperationKind.ADD,
                               locator=ConstraintLocator(host='included_fact_type', host_id='component_uses_component',
                                                         family=rule['type']), after=changed)
    candidate = _apply_declared_operations(document, (deleted, added))
    entries = candidate['fact_type_constraints']
    assert [entry['fact_type'] for entry in entries] == ['component_uses_component', 'component_has_owner']
    assert entries[0]['constraints'] == [rule, changed]


def test_C12_reference_bearing_includer_keeps_reference_ownership(tmp_path):
    from datetime import UTC, datetime

    from gnd.discover import output
    from gnd.evolve import EvolutionIncludeError
    from gnd.model import parse_model_document

    source = ROOT / 'tests/fixtures/reference-corpus/dispatch'
    shutil.copytree(source, tmp_path / 'dispatch')
    root = tmp_path / 'dispatch'
    model = root / 'model.orm.yaml'
    authored = parse_model_document(model.read_bytes(), source=model)
    vocabulary = {key: authored.pop(key) for key in ('object_types', 'fact_types', 'constraints') if key in authored}
    vocabulary['version'] = 4
    write(root / 'shared.orm.json', vocabulary)
    authored['version'] = 5
    authored['includes'] = [{'id': 'dispatch', 'path': 'shared.orm.json',
                             'sha256': sha((root / 'shared.orm.json').read_bytes())}]
    write(model, authored)
    rule = {'type': 'mandatory', 'role': 'warehouse', 'source': 'user-supplied',
            'status': 'confirmed', 'modality': 'deontic',
            'provenance': {'user_quote': 'Every shipment names a warehouse.'}}
    operations = output.add_operations([('dispatch_subject_warehouse', rule)],
                                        included_hosts={'dispatch_subject_warehouse'})
    built = output.proposal(model_bytes=model.read_bytes(),
        document=output.candidate_document(authored, operations), ops=operations, actor='mc3-test',
        requested_at=datetime(2026, 11, 10, tzinfo=UTC), population_name='candidate.pop.json')
    current = service_for_paths(model, root)
    reviewed = current.preview(built)
    reference = root / 'references/catalog.pop.json'
    exact = reference.read_bytes()
    reference.write_bytes(exact + b' ')
    with pytest.raises(EvolutionIncludeError):
        current.apply(reviewed)
    reference.write_bytes(exact)
    record = current.finalize(current.apply(reviewed))
    assert record.new_model_sha256 == sha(model.read_bytes())


@pytest.mark.parametrize('target', ['element', 'role'])
@pytest.mark.parametrize('bad_id', [['name'], {'id': 'name'}])
def test_C16_malformed_rename_identity_is_input_refusal(work, target, bad_id):
    value = read(work / 'combined.proposal.json')
    vocabulary = read(work / 'vocabulary-v1.orm.json')
    before = copy.deepcopy(vocabulary['object_types'][0] if target == 'element' else
                           vocabulary['fact_types'][0]['roles'][0])
    locator = ({'locator_kind': 'element', 'collection': 'object_types', 'element_id': before['id']}
               if target == 'element' else {'locator_kind': 'role', 'fact_type_id': 'component_uses_component',
                                            'role_name': before['role_name']})
    after = {**before, 'id' if target == 'element' else 'role_name': bad_id}
    value['operations'] = [{'operation_id': 'hostile-rename', 'kind': 'rename',
                            'locator': locator, 'before': before, 'after': after}]
    write(work / 'combined.proposal.json', value)
    result = preview(work)
    assert result.returncode == 3, result.stdout + result.stderr
    assert not (work / 'preview.json').exists()


@pytest.mark.parametrize('state', ['parent-symlink', 'directory-leaf', 'missing-parent'])
def test_C07_historical_path_preflight_checks_existing_parts(work, state):
    from gnd.evolve import EvolutionIncludeError, read_evolution_proposal_document

    parent = work / 'old'
    parent.mkdir()
    old = parent / 'vocabulary.json'
    shutil.copyfile(work / 'vocabulary-v1.orm.json', old)
    authored = read(work / 'project.orm.json')
    authored['includes'][0]['path'] = 'old/vocabulary.json'
    write(work / 'project.orm.json', authored)
    value = read(work / 'combined.proposal.json')
    value['expected_model_sha256'] = sha((work / 'project.orm.json').read_bytes())
    value['operations'][0]['before'] = authored['includes'][0]
    built = read_evolution_proposal_document(value)
    current = service(work)
    reviewed = current.preview(built)
    accepted = current.preview(built, accepted_blast_radius_sha256=reviewed.blast_radius.report_sha256)
    old.unlink()
    if state == 'directory-leaf':
        old.mkdir()
    else:
        parent.rmdir()
        if state == 'parent-symlink':
            parent.symlink_to(work, target_is_directory=True)
    if state == 'missing-parent':
        current.finalize(current.apply(accepted))
    else:
        with pytest.raises(EvolutionIncludeError):
            current.apply(accepted)
        assert not (work / 'records').exists()


@pytest.mark.parametrize('alias', ['direct', 'hardlink', 'symlink'])
def test_review_discover_never_reports_into_included_input(work, alias):
    from gnd.discover import output

    vocabulary = work / 'vocabulary-v1.orm.json'
    target = vocabulary if alias == 'direct' else work / 'report-alias.json'
    if alias == 'hardlink':
        target.hardlink_to(vocabulary)
    elif alias == 'symlink':
        target.symlink_to(vocabulary)
    exact = vocabulary.read_bytes()
    with patch.object(output, 'write', side_effect=AssertionError('writer reached')):
        result = run_main(['discover', str(work / 'project.orm.json'), str(work / 'clean.pop.json'),
                           '--families', 'mandatory', '--out', str(work / 'discover-proposal.json'),
                           '--report', str(target), '--actor', 'mc3-review',
                           '--requested-at', '2026-11-10T00:00:00Z', '--format', 'json'])
    assert result.returncode == 3, result.stdout + result.stderr
    assert vocabulary.read_bytes() == exact
    assert not (work / 'discover-proposal.json').exists()


def test_review_model_cas_cannot_target_historical_include_path(work):
    import gnd.evolve.service as runtime
    from gnd.evolve import EvolutionIncludeError, read_evolution_proposal_document

    model = work / 'project.orm.json'
    old = (work / 'vocabulary-v1.orm.json').read_bytes()
    authored = read(model)
    authored['includes'][0]['path'] = model.name
    write(model, authored)
    value = read(work / 'combined.proposal.json')
    value['expected_model_sha256'] = sha(model.read_bytes())
    value['operations'][0]['before'] = authored['includes'][0]
    built = read_evolution_proposal_document(value)
    current = service(work)
    reviewed = current.preview(built, previous_includes={'components': old})
    accepted = current.preview(built, previous_includes={'components': old},
                               accepted_blast_radius_sha256=reviewed.blast_radius.report_sha256)
    exact = model.read_bytes()
    original = runtime._atomic_write
    def guarded(root, relative, *args, **kwargs):
        if root == work and relative == model.name:
            raise AssertionError('model CAS reached historical include input')
        return original(root, relative, *args, **kwargs)
    with patch.object(runtime, '_atomic_write', side_effect=guarded), pytest.raises(EvolutionIncludeError):
        current.apply(accepted)
    assert model.read_bytes() == exact
    assert not (work / 'records').exists()
