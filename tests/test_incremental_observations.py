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
    with owner._state.transaction(m):
        with pytest.raises(ValueError, match='active|busy'):
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
