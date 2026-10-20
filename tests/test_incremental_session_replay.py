"""IE3 paired public replay, with complete typed calculation observations."""
import hashlib
import json
import sys
from contextlib import contextmanager

from gnd import api, extensions
from gnd.branches import capture_branches
from gnd.extension_preparation import fingerprint
from tests.test_incremental_baseline import tool
from tests.test_incremental_extensions import envelope


def digest(value):
    key = fingerprint(value)
    assert key is not None, 'refused diagnostic key cannot establish parity'
    return hashlib.sha256(tool.canonical_json_bytes(key)).hexdigest()


def complete_calculation(result):
    return hashlib.sha256(tool.canonical_json_bytes(envelope(result))).hexdigest()


@contextmanager
def observe_calculations():
    reached = []
    assembly = extensions._incremental_components.__code__
    calculators = {extensions._python_extension_calculator.__code__,
                   extensions._exact_extension_calculator.__code__,
                   extensions._evaluate_stratified_extensions.__wrapped__.__code__}
    depth = 0
    previous = sys.getprofile()

    def profile(frame, event, result):
        nonlocal depth
        if previous is not None:
            previous(frame, event, result)
        if frame.f_code is assembly:
            if event == 'call':
                depth += 1
            elif event == 'return':
                depth -= 1
                if result is not None:
                    reached.append(complete_calculation(result))
        elif event == 'return' and frame.f_code in calculators and depth == 0 and result is not None:
            reached.append(complete_calculation(result))

    sys.setprofile(profile)
    try:
        yield reached
    finally:
        sys.setprofile(previous)


def reporter_replay(*, incremental):
    model = tool.load_model(tool.previous.REPORTER / 'steps.orm.json')
    owner = api.EvaluationSession(model) if incremental else None
    receipt = None
    calls = []
    with tool.count_work() as counts:
        for row in tool.previous.reporter_calls():
            population = tool.load_population(tool.previous.REPORTER / row['population'], model=model)
            with capture_branches() as branches, observe_calculations() as calculations:
                if row['call'] == 'check':
                    payload, receipt = (owner.check_with_receipt(population) if owner else
                                        api.check_with_receipt(model, population))
                else:
                    steps = json.loads((tool.previous.REPORTER / row['steps']).read_text())
                    payload = (owner.transition(population, steps, pre_receipt=receipt) if owner else
                               api.transition(model, population, steps, pre_receipt=receipt))
            calls.append({'payload': digest(payload), 'exit': payload['exit_code'],
                          'branches': sorted(branches), 'calculations': sorted(set(calculations))})
    return calls, dict(counts), owner.stats() if owner else None


def test_reporter_complete_trace_and_actual_work_reduction():
    full, full_counts, _ = reporter_replay(incremental=False)
    reused, reused_counts, state = reporter_replay(incremental=True)
    assert len(full) == len(reused) == 13
    assert [row['exit'] for row in full] == [2] * 13
    assert all(row['calculations'] and row['branches'] for row in full)
    assert full == reused
    assert full_counts['derivation_body_evaluations'] == 4878
    assert reused_counts['derivation_body_evaluations'] < 4878
    assert state['hits'] > 0 and state['entries'] > 0
    assert state['rows'] <= 100_000 and state['bytes'] <= 32 * 1024 * 1024
