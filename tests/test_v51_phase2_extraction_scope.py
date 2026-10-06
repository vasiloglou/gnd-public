from __future__ import annotations

import copy
import statistics
import time
from pathlib import Path

import pytest

import gnd.extract.bundle as bundle_module
import gnd.extract.refscheme as refscheme_module
import gnd.popvalidate as popvalidate_module
from gnd.extract.bundle import header_template
from gnd.extract.projection import project
from gnd.extraction_scope import STRUCTURED_DERIVATION_INAPPLICABLE_REASON, fact_type_scope
from gnd.model import Model, load_model

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS = REPO_ROOT / 'tests' / 'fixtures' / 'v51-extraction-boundary'
MIXED_MODEL_PATH = CORPUS / 'models' / 'mixed.orm.yaml'

def _mixed_model() -> Model:
    return load_model(MIXED_MODEL_PATH)

def test_scope_classifies_asserted_structured_and_legacy_once() -> None:
    assert fact_type_scope(_mixed_model()) == {'book_listed': None, 'book_blocked': None, 'book_is_eligible': STRUCTURED_DERIVATION_INAPPLICABLE_REASON, 'book_ranked': None}

def test_structured_to_legacy_one_change_falsifier_reincludes_the_type() -> None:
    model = _mixed_model().model_copy(deep=True)
    structured = next(fact_type for fact_type in model.fact_types if fact_type['id'] == 'book_is_eligible')
    structured['derivation_rule'] = 'same policy, represented as legacy opaque text'
    assert fact_type_scope(model)['book_is_eligible'] is None

def test_header_contains_asserted_and_legacy_but_not_structured() -> None:
    assert header_template('tests/fixtures/v51-extraction-boundary/models/mixed.orm.yaml', _mixed_model()) == {'model': 'tests/fixtures/v51-extraction-boundary/models/mixed.orm.yaml', 'model_id': 'urn:gnd-fixture:v51-extraction-boundary:mixed@1', 'source': 'agent-output', 'covers': ['book_blocked', 'book_listed', 'book_ranked']}

def test_projection_deliberately_still_admits_the_structured_fact_type() -> None:
    facts = project(_mixed_model())['properties']['facts']['properties']
    assert 'book_is_eligible' in facts

def test_three_policy_consumers_call_the_one_scope_owner() -> None:
    consumers = [REPO_ROOT / 'src' / 'gnd' / 'extract' / 'bundle.py', REPO_ROOT / 'src' / 'gnd' / 'refscheme.py', REPO_ROOT / 'src' / 'gnd' / 'popvalidate.py']
    for path in consumers:
        source = path.read_text(encoding='utf-8')
        assert 'fact_type_scope(' in source, path
        assert 'structured_derivation_ids' not in source, path
        assert 'derivation_rule' not in source, path

def test_three_policy_consumers_obey_a_monkeypatched_scope_owner(monkeypatch: pytest.MonkeyPatch) -> None:
    sentinel = 'test-owned exclusion'
    altered = {'book_listed': sentinel, 'book_blocked': None, 'book_is_eligible': None, 'book_ranked': None}
    for module in (bundle_module, __import__('gnd.refscheme', fromlist=['refscheme']), popvalidate_module):
        monkeypatch.setattr(module, 'fact_type_scope', lambda _model: dict(altered))
    model = _mixed_model()
    header = bundle_module.header_template('mixed.orm.yaml', model)
    assert header['covers'] == ['book_blocked', 'book_is_eligible', 'book_ranked']
    applicability = {row['id']: row for row in refscheme_module.applicable_set(model)['fact_types']}
    assert applicability['book_listed'] == {'id': 'book_listed', 'applicable': False, 'reason': sentinel}
    assert applicability['book_is_eligible']['applicable'] is True
    issues = popvalidate_module._rule_uncovered_structured_derived_facts({'population': {'covers': []}, 'facts': {'book_listed': [{'book': 'dune'}], 'book_is_eligible': [{'book': 'dune'}]}}, model)
    assert [(issue.rule_id, issue.path) for issue in issues] == [('population:uncovered-structured-derived-facts', '$.facts.book_listed')]

def _timed_scope(model: Model) -> float:
    return statistics.median(time.perf_counter() - started for _ in range(7) for started in [time.perf_counter()] for _result in [fact_type_scope(model)])

def _scaling_model(size: int) -> Model:
    fact_types = []
    for index in range(size):
        fact_type = {'id': f'fact_{index}', 'roles': []}
        if index % 2:
            fact_type['derivation_rule'] = {'kind': 'structured'}
        fact_types.append(fact_type)
    return Model(version=1, object_types=[], fact_types=copy.deepcopy(fact_types))

def test_scope_walk_scales_linearly() -> None:
    small = _timed_scope(_scaling_model(5000))
    large = _timed_scope(_scaling_model(20000))
    assert large < 5.0
    assert large < 6 * small, {'small': small, 'large': large}
