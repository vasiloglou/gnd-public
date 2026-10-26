from __future__ import annotations

import copy
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML
from support.cli_runner import run_gnd_text as _run_cli
from support.repository import REPO_ROOT

from gnd import cli
from gnd.checker import check
from gnd.extract.vocabulary import render_verbalization
from gnd.model import Model, ModelValidationError, load_model
from gnd.model_verbalization import render_model_verbalization
from gnd.population import load_population

MODELS = REPO_ROOT / 'tests' / 'fixtures' / 'models'
OPERATIONS_MODEL = MODELS / 'v2_operations.orm.yaml'
FULL_VOCABULARY = MODELS / 'full_vocabulary.orm.yaml'

def _load(path: Path) -> Any:
    yaml = YAML(typ='rt')
    with open(path, encoding='utf-8') as handle:
        return yaml.load(handle)

def _dump(document: Any, path: Path) -> Path:
    yaml = YAML(typ='rt')
    with open(path, 'w', encoding='utf-8') as handle:
        yaml.dump(document, handle)
    return path

def _rule_ids(error: ModelValidationError) -> set[str]:
    return {issue.rule_id for issue in error.issues}

def _operations_doc() -> Any:
    return _load(OPERATIONS_MODEL)

def _first(document: Any) -> Any:
    return document['operations'][0]

def test_two_operation_fixture_validates_clean() -> None:
    model = load_model(OPERATIONS_MODEL)
    assert [operation['id'] for operation in model.operations] == ['attach_review_note', 'flag_work_item']
    assert model.warnings == []
    assert _run_cli('validate', str(OPERATIONS_MODEL)).returncode == 0

def test_operations_without_version_two_is_rejected(tmp_path) -> None:
    document = _operations_doc()
    document['version'] = 1
    with pytest.raises(ModelValidationError) as excinfo:
        load_model(_dump(document, tmp_path / 'v1_with_operations.orm.yaml'))
    assert any(issue.rule_id.startswith('jsonschema:') for issue in excinfo.value.issues)

@pytest.mark.parametrize(('name', 'edit'), [('omitted-frame', lambda document: _first(document).pop('frame')), ('omitted-frame-modality', lambda document: _first(document)['frame'].pop('modality')), ('omitted-precondition-modality', lambda document: _first(document)['preconditions'][0].pop('modality')), ('omitted-dynamic-modality', lambda document: _first(document)['dynamic_rules'][0].pop('modality'))])
def test_modality_is_never_defaulted_anywhere_in_an_operation(name, edit, tmp_path) -> None:
    document = _operations_doc()
    edit(document)
    path = _dump(document, tmp_path / f'{name}.orm.yaml')
    with pytest.raises(ModelValidationError) as excinfo:
        load_model(path)
    assert any(issue.rule_id.startswith('jsonschema:') for issue in excinfo.value.issues)
    assert _run_cli('validate', str(path)).returncode == 3

def test_non_functional_dynamic_subject_warns_and_still_loads(tmp_path) -> None:
    document = _operations_doc()
    subject = next(fact for fact in document['fact_types'] if fact['id'] == 'work_item_has_state')
    del subject['constraints']
    path = _dump(document, tmp_path / 'non_functional_subject.orm.yaml')
    model = load_model(path)
    assert [issue.rule_id for issue in model.warnings] == ['semantic:op-dynamic-functional']
    assert 'unchecked' in model.warnings[0].message
    assert _run_cli('validate', str(path)).returncode == 0

def test_unconfirmed_inferred_obligation_claiming_alethic_warns(tmp_path) -> None:
    document = _operations_doc()
    _first(document)['preconditions'][0].update({'source': 'llm-inferred', 'status': 'proposed', 'modality': 'alethic', 'rationale': 'A review note presupposes a review.', 'provenance': {'rationale_world_fact': 'Notes attributed to a reviewer presuppose a review.'}})
    path = _dump(document, tmp_path / 'op_modality_policy.orm.yaml')
    model = load_model(path)
    assert [issue.rule_id for issue in model.warnings] == ['semantic:op-modality-policy']
    assert _run_cli('validate', str(path)).returncode == 0

def test_version_two_without_operations_is_behaviourally_version_one(tmp_path) -> None:
    document = _load(FULL_VOCABULARY)
    document['version'] = 2
    promoted = _dump(document, tmp_path / 'full_vocabulary_v2.orm.yaml')
    baseline = load_model(FULL_VOCABULARY)
    upgraded = load_model(promoted)
    assert upgraded.operations == []
    assert upgraded.model_dump(exclude={'version'}) == baseline.model_dump(exclude={'version'})
    assert render_model_verbalization(upgraded) == render_model_verbalization(baseline).replace('version=1', 'version=2', 1)
    assert render_verbalization(upgraded) == render_verbalization(baseline)
    assert _run_cli('validate', str(promoted)).returncode == 0

def _population(model: Model, path: Path) -> Any:
    path.write_text("population:\n  model: v2_operations.orm.yaml\n  source: fixture\n  covers: [work_item_has_state, work_item_has_priority]\nfacts:\n  work_item_has_state:\n    - { item: 'W-1', state: 'open' }\n    - { item: 'W-1', state: 'noted' }\n    - { item: 'W-2', state: 'open' }\n  work_item_has_priority:\n    - { item: 'W-1', priority: 3 }\n", encoding='utf-8')
    return load_population(path, model=model)

def test_operations_are_invisible_to_snapshot_checking(tmp_path) -> None:
    stripped_document = _operations_doc()
    del stripped_document['operations']
    stripped_document['version'] = 1
    stripped = load_model(_dump(stripped_document, tmp_path / 'stripped.orm.yaml'))
    with_operations = load_model(OPERATIONS_MODEL)
    assert with_operations.operations, 'the fixture must actually declare operations'
    left = check(with_operations, _population(with_operations, tmp_path / 'a.population.yaml'))
    right = check(stripped, _population(stripped, tmp_path / 'b.population.yaml'))
    assert left.model_dump_json() == right.model_dump_json()
    assert left.verdicts, 'an empty report would make this comparison vacuous'

def test_the_model_digest_excludes_operations_and_nothing_else_new(tmp_path) -> None:
    from gnd.population import MODEL_DIGEST_EXCLUDED_FIELDS, _model_digest
    assert MODEL_DIGEST_EXCLUDED_FIELDS == {'warnings', 'operations'}
    document = _operations_doc()
    baseline = _model_digest(load_model(OPERATIONS_MODEL))
    _first(document)['frame']['modality'] = 'deontic'
    edited = _model_digest(load_model(_dump(document, tmp_path / 'reframed.orm.yaml')))
    assert baseline == edited
    document = _operations_doc()
    document['fact_types'][0]['reading'] = '{WorkItem} is in state {WorkState}'
    moved = _model_digest(load_model(_dump(document, tmp_path / 'reread.orm.yaml')))
    assert baseline != moved, 'the digest must still cover everything the checker reads'

def test_review_verbalization_addresses_every_operation_part_once() -> None:
    rendered = render_model_verbalization(load_model(OPERATIONS_MODEL))
    assert '=== Operations ===' in rendered
    for locator in ('[operation:attach_review_note]', '[operation-precondition:attach_review_note:pre_reviewed]', '[operation-dynamic-rule:attach_review_note:state_must_change]', '[operation-effect:attach_review_note:0]', '[operation-effect:attach_review_note:3]', '[operation-frame:attach_review_note]', '[operation:flag_work_item]', '[operation-frame:flag_work_item]'):
        assert rendered.count(locator) == 1, f'{locator} is not emitted exactly once'

def test_extraction_vocabulary_renders_readings_and_parameters_only() -> None:
    rendered = render_verbalization(load_model(OPERATIONS_MODEL))
    assert '=== Operations ===' in rendered
    assert 'WorkItem gains review note Note from Reviewer' in rendered
    assert '  - reviewer: Reviewer (String)' in rendered
    for withheld in ('pre_reviewed', 'state_must_change', 'alethic', 'deontic', 'retract'):
        assert withheld not in rendered, f'the constraint-blind vocabulary leaked {withheld!r} — a seed that recites the rules teaches the extractor to emit the population the checker wants rather than the one the document contains'

def test_vocabulary_is_blind_to_injected_obligations(tmp_path) -> None:
    baseline = render_verbalization(load_model(OPERATIONS_MODEL))
    document = _operations_doc()
    _first(document)['preconditions'].append({'id': 'pre_open', 'require': [{'fact_type': 'work_item_has_state', 'bind': {'item': '$item', 'state': 'open'}}], 'modality': 'alethic', 'source': 'explicit', 'status': 'confirmed', 'provenance': {'csdp_step': 7, 'user_quote': 'Only open items take notes.'}})
    _first(document)['dynamic_rules'].append({'id': 'priority_also_rises', 'subject': {'fact_type': 'work_item_has_priority', 'value_role': 'priority', 'bind': {'item': '$item'}}, 'op': '>', 'modality': 'alethic', 'source': 'explicit', 'status': 'confirmed', 'provenance': {'csdp_step': 7, 'user_quote': 'Priority rises.'}})
    document['operations'][1]['frame']['modality'] = 'alethic'
    injected = load_model(_dump(document, tmp_path / 'injected.orm.yaml'))
    assert render_verbalization(injected) == baseline
    assert render_model_verbalization(injected) != render_model_verbalization(load_model(OPERATIONS_MODEL))

def _service(tmp_path: Path, before_text: str):
    from gnd.evolve import EvolutionService
    tmp_path.mkdir(parents=True, exist_ok=True)
    model_path = tmp_path / 'model.orm.yaml'
    model_path.write_text(before_text, encoding='utf-8')
    (tmp_path / 'model.verbalization.txt').write_text('pre-existing\n', encoding='utf-8')
    return EvolutionService(model_path=model_path, evidence_root=tmp_path / 'evolution-evidence', verbalization_path=tmp_path / 'model.verbalization.txt', allowed_project_root=tmp_path)

def _proposal(before_text: str, candidate_document: Any, operations: tuple[Any, ...]):
    from gnd.evolve import CommittedText, EvolutionOperationAudit, EvolutionProposal
    buffer = __import__('io').StringIO()
    YAML(typ='rt').dump(candidate_document, buffer)
    candidate_text = buffer.getvalue()
    return (EvolutionProposal(proposal_id='proposal-v2', expected_model_sha256=hashlib.sha256(before_text.encode('utf-8')).hexdigest(), candidate_model=CommittedText.from_text(candidate_text, media_type='application/yaml'), operations=operations, rationale='ORM+ v2 gate fixture.', audit=EvolutionOperationAudit(actor_id='owner:fixture', origin='test_model_v2', requested_at=datetime(2026, 8, 19, 12, 0, tzinfo=UTC))), candidate_text)
NEW_OPERATION = {'id': 'close_work_item', 'reading': '{WorkItem} is closed', 'parameters': [{'name': 'item', 'object_type': 'work_item'}], 'effects': [{'assert': {'fact_type': 'work_item_has_state', 'bind': {'item': '$item', 'state': 'closed'}}}], 'frame': {'modality': 'deontic'}, 'source': 'user-supplied', 'status': 'confirmed', 'provenance': {'added_at_step': '7d'}}

def test_an_additive_operation_delta_proceeds(tmp_path) -> None:
    from gnd.evolve import ElementLocator, EvolutionOperation, EvolutionOperationKind
    before_text = OPERATIONS_MODEL.read_text(encoding='utf-8')
    candidate = _operations_doc()
    candidate['operations'].append(copy.deepcopy(NEW_OPERATION))
    proposal, candidate_text = _proposal(before_text, candidate, (EvolutionOperation(operation_id='add-close-operation', kind=EvolutionOperationKind.ADD, locator=ElementLocator(collection='operations', element_id='close_work_item'), before=None, after=copy.deepcopy(NEW_OPERATION)),))
    preview = _service(tmp_path / 'ws', before_text).preview(proposal)
    assert preview.breaking is False
    assert preview.validation.valid is True
    published = YAML(typ='safe').load(preview.candidate_model.text)
    assert [operation['id'] for operation in published['operations']] == ['attach_review_note', 'flag_work_item', 'close_work_item']
    assert any(entry.reference == 'operations[close_work_item]' and entry.change == 'added' for entry in preview.blast_radius.entries), 'an added operation must be visible in the blast radius'
    assert candidate_text == preview.candidate_model.text

def test_a_delta_outside_the_reference_set_still_proceeds(tmp_path) -> None:
    from gnd.evolve import ElementLocator, EvolutionOperation, EvolutionOperationKind
    before_text = OPERATIONS_MODEL.read_text(encoding='utf-8')
    added = {'id': 'tag', 'name': 'Tag', 'kind': 'value', 'primitive': 'String'}
    candidate = _operations_doc()
    candidate['object_types'].append(copy.deepcopy(added))
    proposal, _ = _proposal(before_text, candidate, (EvolutionOperation(operation_id='add-tag', kind=EvolutionOperationKind.ADD, locator=ElementLocator(collection='object_types', element_id='tag'), before=None, after=copy.deepcopy(added)),))
    preview = _service(tmp_path / 'ws', before_text).preview(proposal)
    published = YAML(typ='safe').load(preview.candidate_model.text)
    assert [operation['id'] for operation in published['operations']] == ['attach_review_note', 'flag_work_item'], 'operations must be carried through verbatim'

def _gated(tmp_path: Path, build) -> str:
    from gnd.evolve import EvolutionOperationsGatedError
    before_text = OPERATIONS_MODEL.read_text(encoding='utf-8')
    candidate, operations = build(_operations_doc())
    proposal, _ = _proposal(before_text, candidate, operations)
    service = _service(tmp_path, before_text)
    with pytest.raises(EvolutionOperationsGatedError) as excinfo:
        service.preview(proposal)
    return str(excinfo.value)

def test_deleting_an_operation_is_gated(tmp_path) -> None:
    from gnd.evolve import ElementLocator, EvolutionOperation, EvolutionOperationKind

    def build(document):
        removed = document['operations'].pop(1)
        return (document, (EvolutionOperation(operation_id='drop-flag', kind=EvolutionOperationKind.DELETE, locator=ElementLocator(collection='operations', element_id='flag_work_item'), before=json.loads(json.dumps(removed)), after=None),))
    message = _gated(tmp_path / 'ws', build)
    assert 'flag_work_item' in message
    assert 'hand-edit the model' in message

def test_modifying_an_operation_is_gated(tmp_path) -> None:
    from gnd.evolve import ElementLocator, EvolutionOperation, EvolutionOperationKind

    def build(document):
        before = json.loads(json.dumps(document['operations'][1]))
        document['operations'][1]['frame']['modality'] = 'alethic'
        after = json.loads(json.dumps(document['operations'][1]))
        return (document, (EvolutionOperation(operation_id='reframe-flag', kind=EvolutionOperationKind.MODIFY, locator=ElementLocator(collection='operations', element_id='flag_work_item'), before=before, after=after),))
    assert 'flag_work_item' in _gated(tmp_path / 'ws', build)

def test_renaming_a_fact_type_an_operation_references_is_gated(tmp_path) -> None:
    from gnd.evolve import ElementLocator, EvolutionOperation, EvolutionOperationKind

    def build(document):
        fact = next(item for item in document['fact_types'] if item['id'] == 'work_item_reviewed_by')
        before = json.loads(json.dumps(fact))
        fact['id'] = 'work_item_review_by'
        after = json.loads(json.dumps(fact))
        return (document, (EvolutionOperation(operation_id='rename-reviewed-by', kind=EvolutionOperationKind.RENAME, locator=ElementLocator(collection='fact_types', element_id='work_item_reviewed_by'), before=before, after=after),))
    message = _gated(tmp_path / 'ws', build)
    assert 'work_item_reviewed_by' in message

def test_the_gate_names_the_intersecting_ids_rather_than_the_whole_model(tmp_path) -> None:
    from gnd.evolve import ElementLocator, EvolutionOperation, EvolutionOperationKind

    def build(document):
        fact = next(item for item in document['fact_types'] if item['id'] == 'work_item_has_note')
        before = json.loads(json.dumps(fact))
        return (document, (EvolutionOperation(operation_id='drop-note-fact', kind=EvolutionOperationKind.DELETE, locator=ElementLocator(collection='fact_types', element_id='work_item_has_note'), before=before, after=None),))
    message = _gated(tmp_path / 'ws', build)
    assert 'work_item_has_note' in message
    assert 'work_item_has_priority' not in message

def test_a_v1_model_is_untouched_by_the_gate() -> None:
    from gnd.evolve.service import _operations_reference_set
    assert _operations_reference_set(YAML(typ='safe').load(FULL_VOCABULARY.read_text())) == frozenset()

def test_the_reference_set_is_flat_and_not_transitive() -> None:
    from gnd.evolve.service import _operations_reference_set
    references = _operations_reference_set(YAML(typ='safe').load(OPERATIONS_MODEL.read_text()))
    assert references == {'work_item', 'note', 'reviewer', 'work_item_reviewed_by', 'work_item_has_note', 'work_item_has_state'}
    assert 'work_item_id' not in references

def test_the_gate_returns_exit_eighteen() -> None:
    from gnd.evolve import EvolutionOperationsGatedError
    assert cli.EXIT_EVOLUTION_OPERATIONS_GATED == 18
    assert cli._evolve_error_exit(EvolutionOperationsGatedError('evolution operations gated: stale ')) == 18

def test_a_creatable_subtype_inheriting_its_reference_is_accepted(tmp_path) -> None:
    document = _operations_doc()
    document['object_types'].append({'id': 'urgent_item', 'name': 'UrgentItem', 'kind': 'entity', 'subtype_of': ['work_item'], 'inherits_reference': True})
    operation = _first(document)
    operation['parameters'].append({'name': 'urgent', 'object_type': 'urgent_item'})
    operation['effects'].append({'create': {'object_type': 'urgent_item', 'param': 'urgent'}})
    model = load_model(_dump(document, tmp_path / 'creatable_subtype.orm.yaml'))
    assert model.warnings == []

def test_a_subtype_that_inherits_nothing_is_still_refused(tmp_path) -> None:
    document = _operations_doc()
    document['object_types'].append({'id': 'urgent_item', 'name': 'UrgentItem', 'kind': 'entity', 'subtype_of': ['work_item'], 'inherits_reference': False})
    operation = _first(document)
    operation['parameters'].append({'name': 'urgent', 'object_type': 'urgent_item'})
    operation['effects'].append({'create': {'object_type': 'urgent_item', 'param': 'urgent'}})
    with pytest.raises(ModelValidationError) as excinfo:
        load_model(_dump(document, tmp_path / 'uninheriting_subtype.orm.yaml'))
    assert 'semantic:op-create-ref-mode' in _rule_ids(excinfo.value)

def test_a_subtype_cycle_under_create_terminates(tmp_path) -> None:
    document = _operations_doc()
    document['object_types'].extend([{'id': 'a_type', 'name': 'AType', 'kind': 'entity', 'subtype_of': ['b_type'], 'inherits_reference': True}, {'id': 'b_type', 'name': 'BType', 'kind': 'entity', 'subtype_of': ['a_type'], 'inherits_reference': True}])
    operation = _first(document)
    operation['parameters'].append({'name': 'cyclic', 'object_type': 'a_type'})
    operation['effects'].append({'create': {'object_type': 'a_type', 'param': 'cyclic'}})
    with pytest.raises(ModelValidationError) as excinfo:
        load_model(_dump(document, tmp_path / 'subtype_cycle.orm.yaml'))
    assert 'semantic:op-create-ref-mode' in _rule_ids(excinfo.value)

def test_reading_validation_is_not_quadratic_in_the_parameter_count(tmp_path) -> None:
    from gnd.model import semantic_validate
    size = 4000
    document = {'version': 2, 'object_types': [{'id': f't_{index}', 'name': f'T{index}', 'kind': 'value', 'primitive': 'String'} for index in range(size)], 'fact_types': [{'id': 'f', 'reading': '{T0}', 'roles': [{'object_type': 't_0', 'role_name': 'r'}]}], 'operations': [{'id': 'op', 'reading': ' '.join(f'{{t_{index}}}' for index in range(size)), 'parameters': [{'name': f'p_{index}', 'object_type': f't_{index}'} for index in range(size)], 'effects': [{'assert': {'fact_type': 'f', 'bind': {'r': 'x'}}}], 'frame': {'modality': 'alethic'}, 'source': 'user-supplied', 'status': 'confirmed', 'provenance': {'added_at_step': 'x'}}]}
    import time
    started = time.perf_counter()
    issues = semantic_validate(document)
    elapsed = time.perf_counter() - started
    assert [issue for issue in issues if issue.severity == 'error'] == []
    assert elapsed < 2.0, f'semantic validation of {size} parameters took {elapsed:.2f}s — the placeholder rule is scanning the parameter list again'

def test_the_reference_set_is_total_over_arbitrary_json() -> None:
    from gnd.evolve.service import _operations_reference_set
    for hostile in (1, None, 'text', {'x': 1}, [], [1, 2], [{'object_type': 'kept'}]):
        assert _operations_reference_set({'operations': [{'parameters': hostile}]}) <= {'kept'}
    for hostile in (1, None, 'text', {'x': 1}):
        assert _operations_reference_set({'operations': hostile}) == frozenset()
        assert _operations_reference_set({'operations': [hostile]}) == frozenset()
        assert _operations_reference_set({'operations': [{'effects': [{'assert': hostile}]}]}) == frozenset()
        assert _operations_reference_set({'operations': [{'dynamic_rules': [{'subject': hostile}]}]}) == frozenset()

def test_a_hostile_after_value_is_refused_rather_than_raising(tmp_path) -> None:
    from gnd.evolve import (
        ElementLocator,
        EvolutionError,
        EvolutionOperation,
        EvolutionOperationKind,
    )
    before_text = OPERATIONS_MODEL.read_text(encoding='utf-8')
    hostile = {'id': 'hostile', 'parameters': 1}
    candidate = _operations_doc()
    candidate['operations'].append(copy.deepcopy(hostile))
    removed = copy.deepcopy(next(item for item in _operations_doc()['object_types'] if item['id'] == 'effort'))
    candidate['object_types'] = [item for item in candidate['object_types'] if item['id'] != 'effort']
    proposal, _ = _proposal(before_text, candidate, (EvolutionOperation(operation_id='add-hostile', kind=EvolutionOperationKind.ADD, locator=ElementLocator(collection='operations', element_id='hostile'), before=None, after=copy.deepcopy(hostile)), EvolutionOperation(operation_id='drop-effort', kind=EvolutionOperationKind.DELETE, locator=ElementLocator(collection='object_types', element_id='effort'), before=json.loads(json.dumps(removed)), after=None)))
    with pytest.raises(EvolutionError) as excinfo:
        _service(tmp_path / 'ws', before_text).preview(proposal)
    assert not isinstance(excinfo.value, TypeError)
    assert cli._evolve_error_exit(excinfo.value) == 3, 'a malformed proposal must land in the malformed band, not the internal one'

def test_the_current_model_is_validated_before_it_is_traversed() -> None:
    import inspect

    from gnd.evolve.service import EvolutionService
    source = inspect.getsource(EvolutionService.preview)
    validated = source.index('label="current model"')
    parsed = source.index('before_document = _parse_model_text(before_text)')
    gated = source.index('_enforce_operations_gate(before_document, proposal)')
    assert validated < parsed < gated, 'the current model must be validated before it is parsed or traversed'
    assert gated < source.index('self._validated_candidate(\n            proposal.candidate_model,')

def test_an_alias_bearing_current_model_is_refused(tmp_path) -> None:
    from gnd.evolve import (
        ElementLocator,
        EvolutionError,
        EvolutionOperation,
        EvolutionOperationKind,
    )
    before_text = 'version: 1\nobject_types:\n  - &anchor {id: a, name: A, kind: value, primitive: String}\n  - *anchor\nfact_types: []\n'
    added = {'id': 'b', 'name': 'B', 'kind': 'value', 'primitive': 'String'}
    candidate = {'version': 1, 'object_types': [{'id': 'a', 'name': 'A', 'kind': 'value', 'primitive': 'String'}, {'id': 'a', 'name': 'A', 'kind': 'value', 'primitive': 'String'}, copy.deepcopy(added)], 'fact_types': []}
    proposal, _ = _proposal(before_text, candidate, (EvolutionOperation(operation_id='add-b', kind=EvolutionOperationKind.ADD, locator=ElementLocator(collection='object_types', element_id='b'), before=None, after=copy.deepcopy(added)),))
    with pytest.raises(EvolutionError) as excinfo:
        _service(tmp_path / 'ws', before_text).preview(proposal)
    assert str(excinfo.value) == 'current model validation failed: model YAML alias/event guard refused input'

def test_an_archived_proposal_may_carry_both_a_type_and_an_id(tmp_path) -> None:
    document = _operations_doc()
    document['rejected_proposals'] = [{'type': 'ring', 'id': 'archived_ring', 'status': 'rejected'}, {'id': 'archived_operation', 'status': 'rejected'}, {'type': 'uniqueness', 'status': 'rejected'}]
    assert len(load_model(_dump(document, tmp_path / 'archived.orm.yaml')).rejected_proposals) == 3

def test_an_archived_proposal_identified_by_nothing_is_refused(tmp_path) -> None:
    document = _operations_doc()
    document['rejected_proposals'] = [{'status': 'rejected'}]
    with pytest.raises(ModelValidationError):
        load_model(_dump(document, tmp_path / 'anonymous_archive.orm.yaml'))

WORKED_EXAMPLE = MODELS / 'v2_worked_example.orm.yaml'
CANONICAL_SCHEMA = REPO_ROOT / 'src' / 'gnd' / 'skills' / 'gnd-orm-core' / 'references' / 'orm-meta.schema.json'
VENDORED_SCHEMA = REPO_ROOT / 'src' / 'gnd' / 'schema' / 'orm-meta.schema.json'
REPRESENTATION_FORMAT = REPO_ROOT / 'src' / 'gnd' / 'skills' / 'gnd-orm-core' / 'references' / 'representation-format.md'

def test_worked_example_validates_clean() -> None:
    model = load_model(WORKED_EXAMPLE)
    assert model.warnings == []
    assert _run_cli('validate', str(WORKED_EXAMPLE)).returncode == 0

def test_worked_example_bytes_are_the_specification_bytes() -> None:
    fenced = re.findall('^```yaml\\n(operations:\\n.*?)^```$', REPRESENTATION_FORMAT.read_text(encoding='utf-8'), flags=re.MULTILINE | re.DOTALL)
    assert len(fenced) == 1, f'representation-format.md must carry exactly one fenced block starting at `operations:`; found {len(fenced)}'
    fixture_text = WORKED_EXAMPLE.read_text(encoding='utf-8')
    marker = '\noperations:\n'
    assert marker in fixture_text
    assert fenced[0] == fixture_text[fixture_text.index(marker) + 1:], "the specification's worked example and tests/fixtures/models/v2_worked_example.orm.yaml have drifted apart. Edit the fixture, confirm `gnd validate` exits 0 on it, then copy its `operations:` section into the document — never the other way around."

def test_schema_copies_stay_byte_identical_and_carry_the_v2_keys() -> None:
    assert CANONICAL_SCHEMA.read_bytes() == VENDORED_SCHEMA.read_bytes()
    schema = json.loads(VENDORED_SCHEMA.read_text(encoding='utf-8'))
    assert schema['properties']['version'] == {'enum': [1, 2, 3, 4]}
    assert schema['properties']['operations']['items'] == {'$ref': '#/$defs/operation'}
    defs = schema['$defs']
    for name in ('operation', 'obligation', 'effect', 'dynamic_rule', 'frame', 'atom', 'bindings', 'term', 'source_kind', 'provenance_policy'):
        assert name in defs, f'$defs/{name} is missing from the shipped schema'
    assert 'imported' in defs['source_kind']['enum']
    assert defs['constraint_common']['properties']['id'] == {'$ref': '#/$defs/identifier'}
    assert defs['frame']['required'] == ['modality']
    assert 'postconditions' not in json.dumps(schema), 'M3 keeps postconditions out of the v2 language; effects state the claims'

def test_imported_confirmed_without_reviewed_in_is_rejected(tmp_path) -> None:
    document = _operations_doc()
    _first(document)['preconditions'][0].update({'source': 'imported', 'provenance': {'framework': 'gsd', 'artifact': '.planning/REQUIREMENTS.md', 'commit': '0000000', 'sha256': '0' * 64, 'anchor': 'Only a reviewer of the item may leave a review note.'}})
    path = _dump(document, tmp_path / 'imported_unreviewed.orm.yaml')
    with pytest.raises(ModelValidationError):
        load_model(path)
    assert _run_cli('validate', str(path)).returncode == 3

def test_imported_proposed_needs_no_reviewed_in(tmp_path) -> None:
    document = _operations_doc()
    _first(document)['preconditions'][0].update({'source': 'imported', 'status': 'proposed', 'modality': 'deontic', 'provenance': {'framework': 'gsd', 'artifact': '.planning/REQUIREMENTS.md', 'commit': '0000000', 'sha256': '0' * 64, 'anchor': 'Only a reviewer of the item may leave a review note.'}})
    model = load_model(_dump(document, tmp_path / 'imported_proposed.orm.yaml'))
    assert model.operations[0]['preconditions'][0]['source'] == 'imported'

def _reject_op_param_ref(document: Any) -> None:
    _first(document)['parameters'][2]['object_type'] = 'auditor'

def _reject_op_param_names_distinct(document: Any) -> None:
    _first(document)['parameters'].append({'name': 'item', 'object_type': 'work_item'})

def _reject_op_reading_placeholders(document: Any) -> None:
    _first(document)['reading'] = '{Auditor} gains review note {Note} from {Reviewer}'

def _reject_op_reading_qualifier_label(document: Any) -> None:
    _first(document)['reading'] = '{WorkItem:note} gains a review note'

def _reject_op_atom_ref(document: Any) -> None:
    _first(document)['effects'][1]['assert']['fact_type'] = 'work_item_has_owner'

def _reject_op_term_ref(document: Any) -> None:
    _first(document)['effects'][1]['assert']['bind']['note'] = '$memo'

def _reject_op_term_type_compat(document: Any) -> None:
    _first(document)['effects'][1]['assert']['bind']['item'] = '$reviewer'

def _reject_op_effect_ground(document: Any) -> None:
    del _first(document)['effects'][1]['assert']['bind']['note']

def _reject_op_create_param(document: Any) -> None:
    _first(document)['effects'][0]['create']['param'] = 'memo'

def _reject_op_create_ref_mode(document: Any) -> None:
    operation = _first(document)
    operation['parameters'].append({'name': 'spent', 'object_type': 'effort'})
    operation['effects'].append({'create': {'object_type': 'effort', 'param': 'spent'}})

def _reject_op_status_source(document: Any) -> None:
    _first(document)['status'] = 'proposed'

def _reject_obligation_status_source(document: Any) -> None:
    _first(document)['preconditions'][0]['status'] = 'proposed'

def _reject_op_obligation_ids_distinct(document: Any) -> None:
    _first(document)['dynamic_rules'][0]['id'] = 'pre_reviewed'

def _reject_imported_provenance(document: Any) -> None:
    _first(document)['preconditions'][0].update({'source': 'imported', 'provenance': {'framework': 'gsd', 'artifact': '.planning/REQUIREMENTS.md', 'commit': '0000000', 'sha256': '0' * 64, 'anchor': '   ', 'reviewed_in': 'review/fixture.md'}})

def _reject_imported_confirmed_reviewed(document: Any) -> None:
    _first(document)['preconditions'][0].update({'source': 'imported', 'provenance': {'framework': 'gsd', 'artifact': '.planning/REQUIREMENTS.md', 'commit': '0000000', 'sha256': '0' * 64, 'anchor': 'Only a reviewer of the item may leave a review note.', 'reviewed_in': '  '}})

def _reject_id_unique_operation(document: Any) -> None:
    _first(document)['id'] = 'work_item_has_state'

def _reject_id_unique_constraint(document: Any) -> None:
    priority = next(fact for fact in document['fact_types'] if fact['id'] == 'work_item_has_priority')
    priority['constraints'][0]['id'] = 'work_item_has_state'
REJECTING_CASES = [('op-param-ref', _reject_op_param_ref, 'semantic:op-param-ref'), ('op-param-names-distinct', _reject_op_param_names_distinct, 'semantic:op-param-names-distinct'), ('op-reading-placeholders', _reject_op_reading_placeholders, 'semantic:op-reading-placeholders'), ('op-reading-qualifier-label', _reject_op_reading_qualifier_label, 'semantic:op-reading-placeholders'), ('op-atom-ref', _reject_op_atom_ref, 'semantic:op-atom-ref'), ('op-term-ref', _reject_op_term_ref, 'semantic:op-term-ref'), ('op-term-type-compat', _reject_op_term_type_compat, 'semantic:op-term-type-compat'), ('op-effect-ground', _reject_op_effect_ground, 'semantic:op-effect-ground'), ('op-create-param', _reject_op_create_param, 'semantic:op-create-param'), ('op-create-ref-mode', _reject_op_create_ref_mode, 'semantic:op-create-ref-mode'), ('op-status-source', _reject_op_status_source, 'semantic:status-source'), ('obligation-status-source', _reject_obligation_status_source, 'semantic:status-source'), ('op-obligation-ids-distinct', _reject_op_obligation_ids_distinct, 'semantic:op-obligation-ids-distinct'), ('imported-provenance', _reject_imported_provenance, 'semantic:imported-provenance'), ('imported-confirmed-reviewed', _reject_imported_confirmed_reviewed, 'semantic:imported-confirmed-reviewed'), ('id-unique-operation', _reject_id_unique_operation, 'semantic:id-unique'), ('id-unique-constraint-id', _reject_id_unique_constraint, 'semantic:id-unique')]

@pytest.mark.parametrize(('name', 'edit', 'rule_id'), REJECTING_CASES, ids=[case[0] for case in REJECTING_CASES])
def test_each_new_rule_rejects_a_document(name, edit, rule_id, tmp_path) -> None:
    document = _operations_doc()
    edit(document)
    path = _dump(document, tmp_path / f'{name}.orm.yaml')
    with pytest.raises(ModelValidationError) as excinfo:
        load_model(path)
    assert rule_id in _rule_ids(excinfo.value), f'expected {rule_id}, got {sorted(_rule_ids(excinfo.value))}'
    assert _run_cli('validate', str(path)).returncode == 3

def test_every_error_rule_added_by_this_phase_has_a_rejecting_case() -> None:
    from gnd import model as model_module
    covered = {rule_id for _, _, rule_id in REJECTING_CASES}
    import inspect
    registered = {}
    for rule in model_module._SEMANTIC_RULES:
        source = inspect.getsource(rule)
        rule_id = re.findall('rule_id="([^"]+)"', source).pop()
        registered[rule_id] = 'severity="warning"' in source
    v2_error_rules = {rule_id for rule_id, is_warning in registered.items() if not is_warning and rule_id.startswith(('semantic:op-', 'semantic:imported-'))}
    assert v2_error_rules <= covered, f'no rejecting case for {sorted(v2_error_rules - covered)}'

def test_every_v1_fixture_loads_with_an_empty_operations_list():
    paths = [FULL_VOCABULARY, MODELS.parent / 'checker/setfam.orm.yaml', MODELS.parent / 'checker/ring.orm.yaml', OPERATIONS_MODEL, MODELS.parent / 'v70-phase4/positive.orm.yaml']
    loadable = [(path, load_model(path)) for path in paths]
    v1_models = [(path, model) for path, model in loadable if model.version == 1]
    v2_paths = {path.relative_to(MODELS.parent) for path, model in loadable if model.version == 2}
    assert Path('v70-phase4/positive.orm.yaml') in v2_paths
    stems = {path.name.removesuffix('.orm.yaml') for path, _ in v1_models}
    assert {'full_vocabulary', 'setfam', 'ring'} <= stems
    for path, model in v1_models:
        assert model.operations == [], path
