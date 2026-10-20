"""IE3 corpus-first public session and private receipt controls."""

import pytest

from gnd import api
from gnd.branches import capture_branches
from gnd.extension_preparation import fingerprint
from tests.test_incremental_baseline import tool


def session(model, **kwargs):
    return api.EvaluationSession(model, **kwargs)


def same_payload(actual, expected):
    actual_key, expected_key = fingerprint(actual), fingerprint(expected)
    assert actual_key is not None and expected_key is not None
    assert actual_key == expected_key


def test_explicit_facade_and_noop_evaluator_zero():
    m, p = next(tool.localized_inputs())
    owner = session(m)
    with capture_branches() as expected_branches:
        expected = api.check(m, p)
    with tool.count_work() as counts:
        for attempt in range(2):
            before = dict(counts)
            with capture_branches() as branches:
                actual = owner.check(p)
            same_payload(actual, expected)
            assert branches == expected_branches
            if attempt:
                assert counts['constraint_evaluations'] == before['constraint_evaluations']
                assert counts['derivation_body_evaluations'] == before['derivation_body_evaluations']
    assert owner.stats()['hits'] > 0
    owner.reset()
    assert owner.stats()['entries'] == 0
    owner.close()
    with pytest.raises(ValueError, match='closed'):
        owner.check(p)


def test_localized_full_payload_and_result_detachment():
    owner = None
    for m, p in tool.localized_inputs():
        if owner is None:
            owner = session(m)
        with capture_branches() as expected_branches:
            expected = api.check(m, p)
        with capture_branches() as branches:
            actual = owner.check(p)
        same_payload(actual, expected)
        assert branches == expected_branches
        actual.clear()
    assert owner.stats()['hits'] > 0


def test_session_bounds_preserve_full_fallback():
    m, p = next(tool.localized_inputs())
    owner = session(m, max_bytes=1)
    for _ in range(2):
        same_payload(owner.check(p), api.check(m, p))
        assert owner.stats()['entries'] == 0


def test_receipt_public_report_mutation_cannot_change_transition():
    from gnd.model import load_model
    from gnd.population import load_population
    root = tool.previous.COURSE
    m = load_model(root / 'model.orm.json')
    p = load_population(root / 'state.pop.json', model=m)
    steps = tool.previous._course_steps('attempt-3.steps.json')
    _, receipt = api.check_with_receipt(m, p)
    assert receipt.reusable
    expected = api.transition(m, p, steps, pre_receipt=receipt)
    assert receipt.report.verdicts
    receipt.report.verdicts[0].message = 'Public receipt mutation probe'
    same_payload(api.transition(m, p, steps, pre_receipt=receipt), expected)


def test_session_declared_and_computed_walks_preserve_payloads():
    from gnd.model import load_model
    from gnd.population import load_population
    root = tool.previous.COURSE
    m = load_model(root / 'model.orm.json')
    p = load_population(root / 'state.pop.json', model=m)
    owner = session(m)
    steps = tool.previous._course_steps('attempt-3.steps.json')
    for _ in range(2):
        expected = api.transition(m, p, steps)
        same_payload(owner.transition(p, steps), expected)


def test_mutation_error_does_not_advance_generation():
    m, p = next(tool.localized_inputs())
    owner = session(m)
    owner.check(p)
    before = owner.stats()['generation']
    p.facts['left'].append({'item': 'new'})
    same_payload(owner.check(p), api.check(m, p))
    assert owner.stats()['generation'] == before


def test_trusted_semantic_records_have_bounded_typed_keys(monkeypatch):
    from gnd import extension_preparation as preparation
    from gnd.semantic_ir import Scalar
    integer = Scalar('number', '', 1, 1, True, 'number')
    boolean = Scalar('boolean', 'true', 0, 1, False, 'boolean')
    assert preparation.fingerprint(integer) is not None
    assert preparation.fingerprint(integer) != preparation.fingerprint(boolean)
    monkeypatch.setattr(preparation, 'MAX_FINGERPRINT_NODES', 1)
    assert preparation.fingerprint(integer) is None


def test_independent_inline_constraint_executes_no_right_evaluator(monkeypatch):
    from gnd import correspondence
    from gnd.population import load_population
    m, p = next(tool.localized_inputs())
    current = session(m)
    calls = []
    original = correspondence._inline_uniqueness_result

    def observed(constraint, snapshot):
        result = original(constraint, snapshot)
        if result is not None:
            calls.append(constraint.fact_type)
        return result

    monkeypatch.setattr(correspondence, '_inline_uniqueness_result', observed)
    current.check(p)
    calls.clear()
    changed = load_population(tool.FIXTURE / 'insert.pop.json', model=m)
    expected = api.check(m, changed)
    calls.clear()
    same_payload(current.check(changed), expected)
    assert 'left_copy' in calls
    assert 'right_copy' not in calls


def test_session_signatures_and_no_serialized_handle():
    import inspect
    import pickle
    assert 'EvaluationSession' in api.__all__
    assert tuple(inspect.signature(api.EvaluationSession).parameters) == ('model', 'max_rows', 'max_bytes')
    assert tuple(inspect.signature(api.EvaluationSession.check).parameters) == (
        'self', 'population', 'compiled_operations', 'unredacted', 'anchors', 'document',
        'population_bytes', 'admission', 'references')
    assert tuple(inspect.signature(api.EvaluationSession.transition).parameters) == (
        'self', 'pre', 'steps', 'post', 'unredacted', 'references', 'pre_receipt')
    m, _ = next(tool.localized_inputs())
    with pytest.raises(TypeError, match='serialized'):
        pickle.dumps(session(m))


def test_direct_transition_result_cannot_expose_receipt_storage():
    from gnd.model import load_model
    from gnd.population import load_population
    from gnd.transition import _evaluate_to_state
    root = tool.previous.COURSE
    m = load_model(root / 'model.orm.json')
    p = load_population(root / 'state.pop.json', model=m)
    _, receipt = api.check_with_receipt(m, p)
    first, _, _ = _evaluate_to_state(m, p, [], pre_receipt=receipt)
    original = first.pre_snapshot.verdicts[0].message
    first.pre_snapshot.verdicts[0].message = 'mutated direct result'
    second, _, _ = _evaluate_to_state(m, p, [], pre_receipt=receipt)
    assert second.pre_snapshot.verdicts[0].message == original


def test_reference_mode_deliberately_falls_back(monkeypatch):
    from gnd.incremental_state import active_state
    m, p = next(tool.localized_inputs())
    current = session(m)
    seen = []
    original = api.check

    def watched(*args, **kwargs):
        seen.append(active_state()._disabled)
        kwargs.pop('references', None)
        return original(*args, **kwargs)

    monkeypatch.setattr(api, 'check', watched)
    result = current.check(p, references=object())
    same_payload(result, original(m, p))
    assert seen == [True]
    assert current.stats()['entries'] == 0


def test_receipt_copy_failure_is_nonreusable_without_payload_change(monkeypatch):
    from gnd.checker import CheckReport
    m, p = next(tool.localized_inputs())
    # This violating local fixture is not receipt eligible; use the course.
    from gnd.model import load_model
    from gnd.population import load_population
    m = load_model(tool.previous.COURSE / 'model.orm.json')
    p = load_population(tool.previous.COURSE / 'state.pop.json', model=m)
    expected = api.check(m, p)
    original = api.copy.deepcopy

    def fail_report(value, *args, **kwargs):
        if isinstance(value, CheckReport):
            raise TypeError('injected report clone failure')
        return original(value, *args, **kwargs)

    monkeypatch.setattr(api.copy, 'deepcopy', fail_report)
    payload, receipt = api.check_with_receipt(m, p)
    same_payload(payload, expected)
    assert not receipt.reusable


def test_failed_receipt_mint_does_not_repeat_checker(monkeypatch):
    from gnd.model import load_model
    from gnd.population import load_population
    m = load_model(tool.previous.COURSE / 'model.orm.json')
    p = load_population(tool.previous.COURSE / 'state.pop.json', model=m)
    calls = []

    def fail(*args, **kwargs):
        calls.append(1)
        raise RuntimeError('injected checker failure')

    monkeypatch.setattr(api.checker_module, 'check', fail)
    expected = api.check(m, p)
    assert len(calls) == 1
    calls.clear()
    payload, receipt = api.check_with_receipt(m, p)
    same_payload(payload, expected)
    assert not receipt.reusable
    assert len(calls) == 1


def test_fact_row_budget_charges_retained_witness_rows():
    import json

    from gnd.model import Model
    from gnd.population import load_population_bytes
    original, _ = next(tool.localized_inputs())
    document = original.model_dump()
    for fact in document['fact_types']:
        fact.pop('derivation', None)
        fact.pop('derivation_rule', None)
    m = Model.model_validate(document)
    data = json.loads((tool.FIXTURE / 'initial.pop.json').read_text())
    data['facts']['left_copy'] = [{'item': 'duplicate'}, {'item': 'duplicate'}]
    p = load_population_bytes(json.dumps(data).encode(), model=m, source="fixture:witness-rows")
    owner = session(m, max_rows=3)
    same_payload(owner.check(p), api.check(m, p))
    # Two input rows plus two retained witness rows exceed the cap.
    assert owner.stats()['entries'] == 0


def test_callable_family_default_change_invalidates(tmp_path, monkeypatch):
    from dataclasses import replace

    import test_public_branch_runtime as corpus

    from gnd.constraint_families import FAMILIES

    m, p = corpus._build('P2-039', tmp_path)

    def evaluator(constraint, snapshot, state=1):
        return state, []

    monkeypatch.setitem(FAMILIES, 'frequency', replace(FAMILIES['frequency'], evaluator=evaluator))
    owner = session(m)
    same_payload(owner.check(p), api.check(m, p))
    evaluator.__defaults__ = (0,)
    same_payload(owner.check(p), api.check(m, p))


def test_real_declared_post_is_forwarded():
    import test_public_transition_contract as corpus

    from gnd.model import load_model
    from gnd.population import load_population

    m = load_model(corpus.MODEL)
    root = corpus.CORPUS / 'walks' / 'clean-walk'
    pre = load_population(root / 'pre.pop.yaml', model=m)
    # The pre-state is deliberately the wrong declared post: dropping it must
    # not silently produce the successful computed-post result.
    steps = root / 'steps.json'
    expected = api.transition(m, pre, steps, pre)
    computed = api.transition(m, pre, steps)
    assert fingerprint(expected) != fingerprint(computed)
    same_payload(session(m).transition(pre, steps, pre), expected)


def test_real_bound_reference_context(tmp_path):
    import test_reference_population_corpus as corpus

    from gnd.model import load_model
    from gnd.population import load_population
    from gnd.references import bind_references

    domain = next(iter(corpus.INPUTS['domains']))
    bundle = corpus._bundle(domain, tmp_path / 'references')
    m = load_model(bundle['root'] / 'model.orm.yaml')
    p = load_population(bundle['root'] / 'candidate.pop.json', model=m)
    references = bind_references(m, root=bundle['root'])
    expected = api.check(m, p, references=references)
    assert expected['schema_version'] == 12
    assert expected['reference_binding']['references']
    current = session(m)
    same_payload(current.check(p, references=references), expected)
    assert current.stats()['entries'] == 0
    # Bound contexts carry a stamped alternate model; a foreign binding must
    # be refused rather than silently using the model's default root.
    from dataclasses import replace
    foreign = replace(references, _digest='sha256:' + '0' * 64)
    same_payload(current.check(p, references=foreign), api.check(m, p, references=foreign))
    assert fingerprint(current.check(p, references=foreign)) != fingerprint(expected)


def test_string_resolved_family_default_change_invalidates(tmp_path, monkeypatch):
    import test_public_branch_runtime as corpus

    from gnd import semantic_spec

    m, p = corpus._build('P2-039', tmp_path)

    def evaluator(constraint, snapshot, state=1):
        return state, []

    monkeypatch.setattr(semantic_spec, '_family_result_frequency', evaluator)
    owner = session(m)
    same_payload(owner.check(p), api.check(m, p))
    evaluator.__defaults__ = (0,)
    same_payload(owner.check(p), api.check(m, p))
