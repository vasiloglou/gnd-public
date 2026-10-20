"""IE4 corpus-first observation and closed feedback acceptance controls."""
import json

import pytest

from gnd import api
from gnd.extension_preparation import fingerprint
from tests.test_incremental_baseline import tool
from tests.test_incremental_sessions import same_payload


def wire(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


@pytest.mark.parametrize('rows', [[], [{'item': 'replacement'}],
                                  [{'item': 'same'}, {'item': 'same'}]])
def test_observation_is_validated_relation_replacement(rows):
    m, p = next(tool.localized_inputs())
    owner = api.EvaluationSession(m)
    owner.check(p)
    before = owner.stats()['generation']
    observed = owner.observe(p, {'left': rows})
    assert observed.matches_validation_marker(m)
    assert observed.facts['left'] == rows
    assert observed.facts['right'] == p.facts['right']
    assert owner.stats()['generation'] == before
    same_payload(owner.check(observed), api.check(m, observed))
    rows.append({'item': 'external mutation'})
    assert observed.facts['left'] != rows
    assert observed.matches_validation_marker(m)


def test_observation_bad_unknown_and_stale_are_atomic():
    m, p = next(tool.localized_inputs())
    owner = api.EvaluationSession(m)
    owner.check(p)
    before = owner.stats().copy()
    for replacement in ({'unknown': []}, {'left': [{'missing_role': 'x'}]},
                        {'left': 'not rows'}):
        with pytest.raises((ValueError, TypeError)):
            owner.observe(p, replacement)
        assert owner.stats()['generation'] == before['generation']
        assert p.matches_validation_marker(m)
    p.facts['left'].append({'item': 'stale'})
    with pytest.raises(ValueError, match='validated'):
        owner.observe(p, {})


def test_observation_busy_closed_and_noop_ownership():
    m, p = next(tool.localized_inputs())
    owner = api.EvaluationSession(m)
    observed = owner.observe(p, {})
    assert fingerprint(observed.model_dump()) == fingerprint(p.model_dump())
    observed.facts['left'].clear()
    assert p.facts['left']
    with owner._state.transaction(m), pytest.raises(ValueError, match='active|busy'):
        owner.observe(p, {})
    owner.close()
    with pytest.raises(ValueError, match='closed'):
        owner.observe(p, {'unknown': 'bad'})


def test_two_attempt_feedback_full_parity_and_retry_order():
    from gnd.evaluation_feedback import build_feedback

    m, p = next(tool.localized_inputs())
    owner = api.EvaluationSession(m)
    first_payload, first = owner.check_with_feedback(p, attempt=1)
    same_payload(first_payload, api.check(m, p))
    assert first == build_feedback(m, p, first_payload, attempt=1)
    rows = {row['fact_type']: row for row in first['rows']}
    assert rows['left']['asserted_count'] == 2
    assert rows['left_copy']['asserted_count'] == 0
    assert rows['left_copy']['computed_count'] == 2
    assert rows['left_copy']['computed_status'] == 'available'
    original_bytes = wire(first)
    with pytest.raises(ValueError, match='attempt'):
        owner.check_with_feedback(p, attempt=1)
    with pytest.raises((ValueError, TypeError)):
        owner.observe(p, {'left': [{'bad': 'SECRET-cell'}]})
    observed = owner.observe(p, {'left': [{'item': 'SECRET-cell'}]})
    second_payload, second = owner.check_with_feedback(observed, attempt=2)
    same_payload(second_payload, api.check(m, observed))
    assert second == build_feedback(m, observed, second_payload, attempt=2)
    assert wire(first) == original_bytes
    assert b'SECRET-cell' not in wire(second)
    assert second['attempt'] == 2
    owner.reset()
    assert owner.check_with_feedback(observed, attempt=3)[1]['attempt'] == 3


def test_feedback_closed_version_strict_types_and_bounds():
    from gnd.evaluation_feedback import SessionFeedback

    m, p = next(tool.localized_inputs())
    _, feedback = api.EvaluationSession(m).check_with_feedback(p, attempt=1)
    assert feedback['kind'] == 'evaluation-session-feedback'
    assert feedback['schema_version'] == 1
    assert len(wire(feedback)) <= 16 * 1024
    assert len(feedback['rows']) <= 128
    assert SessionFeedback.model_validate_json(wire(feedback)).model_dump(mode='json') == feedback
    for changes in ({'schema_version': 2}, {'attempt': True}, {'cache_handle': 'x'},
                    {'attempt': 0}, {'attempt': 1000001}):
        with pytest.raises(ValueError):
            SessionFeedback.model_validate_json(wire({**feedback, **changes}))


def test_feedback_count_overflow_and_empty_are_distinct(monkeypatch):
    from gnd import evaluation_feedback as feedback

    m, p = next(tool.localized_inputs())
    monkeypatch.setattr(feedback, 'MAX_COUNT', 1)
    result = feedback.build_feedback(m, p, api.check(m, p), attempt=1)
    rows = {row['fact_type']: row for row in result['rows']}
    assert rows['left_copy']['computed_count'] is None
    assert rows['left_copy']['computed_status'] == 'overflow'
    observed = api.EvaluationSession(m).observe(p, {'left': []})
    result = feedback.build_feedback(m, observed, api.check(m, observed), attempt=1)
    rows = {row['fact_type']: row for row in result['rows']}
    assert rows['left_copy']['computed_count'] == 0
    assert rows['left_copy']['computed_status'] == 'available'


def test_asserted_overflow_is_explicit(monkeypatch):
    from gnd import evaluation_feedback as feedback

    m, p = next(tool.localized_inputs())
    monkeypatch.setattr(feedback, 'MAX_COUNT', 1)
    result = feedback.build_feedback(m, p, api.check(m, p), attempt=1)
    row = next(row for row in result['rows'] if row['fact_type'] == 'left')
    assert row['asserted_count'] is None
    assert row['asserted_status'] == 'overflow'


def test_failed_feedback_construction_keeps_attempt_and_generation(monkeypatch):
    from gnd import evaluation_feedback as feedback

    m, p = next(tool.localized_inputs())
    owner = api.EvaluationSession(m)
    owner.check(p)
    generation = owner.stats()['generation']
    original = feedback.build_feedback

    def fail(*args, **kwargs):
        raise RuntimeError('injected feedback construction failure')

    with monkeypatch.context() as patch:
        patch.setattr(feedback, 'build_feedback', fail)
        with pytest.raises(RuntimeError):
            owner.check_with_feedback(p, attempt=1)
    assert owner.stats()['generation'] == generation
    payload, result = owner.check_with_feedback(p, attempt=1)
    assert result == original(m, p, payload, attempt=1)


def test_error_feedback_not_evaluated_and_old_reader_refuses():
    from gnd.exp.session_eval import AttemptFeedback

    m, p = next(tool.localized_inputs())
    p.facts['left'].append({'item': 'invalid marker'})
    owner = api.EvaluationSession(m)
    payload, feedback = owner.check_with_feedback(p, attempt=1)
    assert payload['exit_code'] not in (0, 1, 2)
    assert owner.stats()['generation'] == 0
    assert all(row['computed_status'] == 'not-evaluated' for row in feedback['rows'])
    assert all(row['asserted_count'] is None for row in feedback['rows'])
    with pytest.raises(ValueError):
        AttemptFeedback.model_validate(feedback)


def test_multibyte_metadata_truncation_and_closed_byte_reader():
    from copy import deepcopy

    from gnd.evaluation_feedback import SessionFeedback, build_feedback
    from gnd.model import Model
    from gnd.population import load_population_bytes

    original, _ = next(tool.localized_inputs())
    doc = original.model_dump()
    base = deepcopy(doc['fact_types'][0])
    names = ['計' * 230 + str(i) for i in range(200)]
    doc['fact_types'] = [{**deepcopy(base), 'id': name} for name in names]
    m = Model.model_validate(doc)
    data = json.loads((tool.FIXTURE / 'initial.pop.json').read_text())
    data['population']['covers'] = names
    data['facts'] = {name: [] for name in names}
    p = load_population_bytes(wire(data), model=m, source='fixture:bounded-feedback.json')
    result = build_feedback(m, p, {'exit_code': 0, 'counts': {}}, attempt=1)
    assert 0 < len(result['rows']) < 128
    assert result['omitted_entries'] + len(result['rows']) == 200
    assert result['truncated']
    assert len(wire(result)) + 1 <= 16384
    oversized = {**result, 'rows': [result['rows'][0]] * 128}
    with pytest.raises(ValueError, match='byte limit'):
        SessionFeedback.model_validate_json(wire(oversized))


def test_current_unavailable_counts_are_not_empty():
    from gnd.evaluation_feedback import build_feedback
    from gnd.extensions import structured_extension_view
    from gnd.model import load_model
    from gnd.population import load_population

    root = tool.ROOT / 'tests/fixtures/v62-phase3'
    m = load_model(root / 'models/exact-terms.orm.yaml')
    p = load_population(root / 'populations/term-input.pop.yaml', model=m)
    view = structured_extension_view(m, p)
    assert view.unavailable
    result = build_feedback(m, p, api.check(m, p), attempt=1)
    rows = {row['fact_type']: row for row in result['rows']}
    for name in view.unavailable:
        assert rows[name]['computed_status'] == 'unavailable'
        assert rows[name]['computed_count'] is None


def test_noop_observation_reuses_all_work():
    m, p = next(tool.localized_inputs())
    owner = api.EvaluationSession(m)
    with tool.count_work() as counts:
        owner.check_with_feedback(p, attempt=1)
        observed = owner.observe(p, {'left': list(p.facts['left'])})
        before = dict(counts)
        owner.check_with_feedback(observed, attempt=2)
        assert counts['derivation_body_evaluations'] == before['derivation_body_evaluations']
        assert counts['constraint_evaluations'] == before['constraint_evaluations']


def test_two_attempt_public_course_host_loop_matches_full():
    from gnd.branches import capture_branches
    from gnd.evaluation_feedback import build_feedback
    from gnd.model import load_model
    from gnd.population import load_population

    m = load_model(tool.previous.COURSE / 'model.orm.json')
    pre = load_population(tool.previous.COURSE / 'state.pop.json', model=m)
    owner = api.EvaluationSession(m)
    steps = tool.previous._course_steps('attempt-3.steps.json')
    old_bytes = None
    for attempt in (1, 2):
        with capture_branches() as expected_branches:
            expected = api.check(m, pre)
            expected_feedback = build_feedback(m, pre, expected, attempt=attempt)
        with capture_branches() as actual_branches:
            payload, feedback = owner.check_with_feedback(pre, attempt=attempt)
        same_payload(payload, expected)
        assert feedback == expected_feedback
        assert actual_branches == expected_branches
        with capture_branches() as expected_branches:
            expected = api.transition(m, pre, steps)
        with capture_branches() as actual_branches:
            actual = owner.transition(pre, steps)
        same_payload(actual, expected)
        assert actual_branches == expected_branches
        if attempt == 1:
            old_bytes = wire(feedback)
            first = feedback
            pre = owner.observe(pre, {'passed': [*pre.facts['passed'],
                                                {'student': 'maya', 'course': 'STAT210'}]})
    assert wire(first) == old_bytes


@pytest.mark.parametrize('tag', ['kind', 'schema_version', 'operation'])
def test_feedback_reader_requires_explicit_discriminators(tag):
    from gnd.evaluation_feedback import SessionFeedback

    m, p = next(tool.localized_inputs())
    _, feedback = api.EvaluationSession(m).check_with_feedback(p, attempt=1)
    feedback.pop(tag)
    with pytest.raises(ValueError):
        SessionFeedback.model_validate_json(wire(feedback))


def test_feedback_reader_rejects_duplicate_version_before_collapse():
    from gnd.evaluation_feedback import SessionFeedback

    m, p = next(tool.localized_inputs())
    _, feedback = api.EvaluationSession(m).check_with_feedback(p, attempt=1)
    encoded = wire(feedback).replace(b'"schema_version":1',
                                    b'"schema_version":2,"schema_version":1')
    with pytest.raises(ValueError, match='duplicate'):
        SessionFeedback.model_validate_json(encoded)


def test_cancellation_after_feedback_computation_does_not_consume_attempt():
    import inspect
    import sys

    m, p = next(tool.localized_inputs())
    owner = api.EvaluationSession(m)
    owner.check(p)
    generation = owner.stats()['generation']
    lines, start = inspect.getsourcelines(api.EvaluationSession._call)
    target = start + next(i for i, line in enumerate(lines) if 'return payload' in line)
    armed = True

    def cancel(frame, event, arg):
        nonlocal armed
        if armed and event == 'line' and frame.f_code is api.EvaluationSession._call.__code__ and frame.f_lineno == target:
            armed = False
            raise KeyboardInterrupt('injected before transaction publication')
        return cancel

    previous = sys.gettrace()
    try:
        sys.settrace(cancel)
        with pytest.raises(KeyboardInterrupt):
            owner.check_with_feedback(p, attempt=1)
    finally:
        sys.settrace(previous)
    assert not armed
    assert owner.stats()['generation'] == generation
    assert owner.check_with_feedback(p, attempt=1)[1]['attempt'] == 1
