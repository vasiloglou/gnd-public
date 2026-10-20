"""Bounded IE5 integrated parity/work/timing evidence; no provider or native lane."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import sys
import time
import tracemalloc
from pathlib import Path

import measure_incremental_evaluation as tool

from gnd import api
from gnd.artifacts import canonical_json_bytes

MODES = {'A': (False, False), 'B': (True, False), 'C': (True, True)}


def observed(workload, mode):
    receipts, incremental = MODES[mode]
    calls, states, work_calls = [], [], []
    call_token = tool.COMPLETE_CALL_SINK.set(calls)
    state_token = tool.SESSION_STATS_SINK.set(states)
    try:
        with tool.count_work() as counts:
            work_token = tool.CALL_SINK.set((counts, work_calls))
            try:
                tool.replay_full(workload, receipts=receipts, incremental=incremental)
            finally:
                tool.CALL_SINK.reset(work_token)
        state = states[-1] if states else None
        return {'calls': calls, 'actual_work': dict(counts), 'per_call_work': work_calls,
                'state': state, 'diagnostic_rates': diagnostic_rates(state) if state else None}
    finally:
        tool.COMPLETE_CALL_SINK.reset(call_token)
        tool.SESSION_STATS_SINK.reset(state_token)


def compare_modes(modes, *, workload):
    expected = {'reporter': [2] * 13, 'course': [1, 1, 0], 'localized': [1] * 6}
    if workload not in expected:
        raise ValueError('unknown frozen workload')
    for mode in 'ABC':
        if [row['exit'] for row in modes[mode]['calls']] != expected[workload]:
            raise ValueError(f'frozen {workload} census/exits failed in mode {mode}')
    a, b, c = (modes[mode]['calls'] for mode in 'ABC')
    if not a or len(a) != len(b) or len(b) != len(c):
        raise ValueError('mode call census mismatch')
    for index, (full, receipt, incremental) in enumerate(zip(a, b, c, strict=True)):
        for key in ('payload', 'exit', 'branches'):
            if full[key] != receipt[key] or receipt[key] != incremental[key]:
                raise ValueError(f'public semantic mismatch at call {index}: {key}')
        if receipt['calculations'] != incremental['calculations']:
            raise ValueError(f'complete receipt-route calculation mismatch at call {index}')
        if not receipt['calculations'] or not receipt['branches']:
            raise ValueError('empty semantic trace cannot establish parity')


def diagnostic_rates(state):
    pairs = {
        'unit_bypass_fraction': ('bypasses', 'lookups'),
        'explicit_fresh_session_fraction': ('session_fresh_calls', 'session_calls'),
        'extension_context_fallback_fraction': ('extension_context_fallbacks', 'extension_context_calls'),
        'constraint_fallback_fraction': ('constraint_fallbacks', 'constraint_calls'),
    }
    return {name: {'numerator': state[numerator], 'denominator': state[denominator],
                   'fraction': state[numerator] / state[denominator] if state[denominator] else None}
            for name, (numerator, denominator) in pairs.items()}


def measure_localized_cases(*, repeat):
    if sys.getprofile() is not None or tracemalloc.is_tracing():
        raise ValueError('case timing must be uninstrumented')
    names = ('cold', 'noop', 'insert', 'delete', 'replace', 'reorder')
    samples = {name: {mode: [] for mode in 'ABC'} for name in names}
    for mode in 'ABC':
        receipts, incremental = MODES[mode]
        tool.replay_full('localized', receipts=receipts, incremental=incremental)
    for order in tool.schedule(repeat):
        for mode in order:
            inputs = list(tool.localized_inputs())
            owner = api.EvaluationSession(inputs[0][0]) if mode == 'C' else None
            for name, (model, population) in zip(names, inputs, strict=True):
                started = time.perf_counter()
                if owner:
                    payload = owner.check_with_receipt(population)[0]
                elif mode == 'B':
                    payload = api.check_with_receipt(model, population)[0]
                else:
                    payload = api.check(model, population)
                elapsed = time.perf_counter() - started
                if payload['exit_code'] != 1:
                    raise ValueError('localized timing fixture unexpectedly changed exit')
                samples[name][mode].append(elapsed)
            if owner:
                owner.close()
    return {'order': tool.schedule(repeat), 'samples': samples,
            'medians': {name: {mode: statistics.median(values) for mode, values in modes.items()}
                        for name, modes in samples.items()},
            'boundary': 'separate uninstrumented public evaluation; preloaded inputs; cold/noop/dirty'}


def lifetime_probe():
    from gnd.incremental_state import ReuseState

    model, population = next(tool.localized_inputs())
    owner = api.EvaluationSession(model)
    bodies = []
    retained = []
    tracemalloc.start()
    try:
        with tool.count_work() as counts:
            for _ in range(32):
                before = counts['derivation_body_evaluations']
                owner.check(population)
                bodies.append(counts['derivation_body_evaluations'] - before)
                retained.append(owner.stats())
        current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    if any(bodies[1:]) or len({row['entries'] for row in retained}) != 1:
        raise ValueError('warm work or retained history grew')
    if max(row['bytes'] for row in retained) > 32 * 1024 * 1024:
        raise ValueError('retained cache exceeds approved bound')
    if max(row['rows'] for row in retained) > 100_000:
        raise ValueError('retained rows exceed approved bound')
    # Separate eligibility fallback from unit bypass: an admission refusal can
    # happen before any unit lookup even in an explicitly fresh session call.
    invalid = owner.observe(population, {})
    invalid.facts['left'].append({'item': 'lost-marker'})
    fallback_owner = api.EvaluationSession(model)
    refused = fallback_owner.check(invalid, references=object())
    if refused['exit_code'] in (0, 1, 2) or fallback_owner.stats()['bypasses']:
        raise ValueError('fallback diagnostic control was not discriminating')
    tiny = ReuseState(model, max_bytes=1)
    with tiny.transaction(model):
        if tiny.reuse('probe', 'capacity', (), lambda: 1) != 1:
            raise ValueError('capacity fallback changed value')
    owner.close()
    return {'calls': 32, 'body_deltas': bodies, 'retained_final': retained[-1],
            'projected_byte_peak': max(row['bytes'] for row in retained),
            'python_allocated_current': current, 'python_allocation_peak': peak,
            'after_close': owner.stats(), 'admission_fallback': fallback_owner.stats(),
            'capacity_fallback': tiny.stats(),
            'boundary': 'separate instrumented allocation probe; not RSS or uninstrumented wall time'}


def identities():
    paths = sorted(Path('src/gnd').rglob('*.py')) + [
        Path('tools/measure_evaluation_sessions.py'),
        Path('tools/measure_incremental_evaluation.py')]
    return {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths
            if 'examples' not in path.parts and 'skills' not in path.parts}


def run(*, repeat=3):
    source_identity, fixture_identity = identities(), tool.identities()
    workloads = {}
    for workload in ('reporter', 'course', 'localized'):
        modes = {mode: observed(workload, mode) for mode in 'ABC'}
        compare_modes(modes, workload=workload)
        if workload == 'reporter':
            full = modes['B']['actual_work']['derivation_body_evaluations']
            reused = modes['C']['actual_work']['derivation_body_evaluations']
            if full != 4878 or reused >= full or [r['exit'] for r in modes['C']['calls']] != [2] * 13:
                raise ValueError('frozen reporter counted gate failed')
        workloads[workload] = {'modes': modes,
                               'timing': tool.measure_session_modes(workload, repeat=repeat)}
        if workload == 'localized':
            workloads[workload]['case_timing'] = measure_localized_cases(repeat=repeat)
    lifetime = lifetime_probe()
    if identities() != source_identity or tool.identities() != fixture_identity:
        raise ValueError('source or fixture bytes changed during measurement')
    return {'kind': 'evaluation-session-measurement', 'schema_version': 1,
            'environment': {'python': sys.version.split()[0], 'platform': platform.platform(),
                            'architecture': platform.machine(), 'timing_isolated': False},
            'configuration': {'modes': {'A': 'full', 'B': 'receipts', 'C': 'session+receipts'},
                              'repeat': repeat, 'retained_rows': 100_000,
                              'retained_bytes': 32 * 1024 * 1024, 'retained_generations': 1},
            'workloads': workloads, 'lifetime': lifetime,
            'source_sha256': source_identity, 'fixture_sha256': fixture_identity,
            'limits': ['shared host; background work uncontrolled; timing informational',
                       'A/B compare complete public semantics; B/C also compare complete calculation traces',
                       'unreceipted A legitimately performs additional pre-state calculations',
                       'allocation peak is a separate instrumented localized probe, not RSS',
                       'diagnostic denominators: session calls, context attempts, constraint attempts, explicit lookups; misses/bypasses overlap',
                       'no new547 workload, downstream acceptance, certification, publication or merge']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--repeat', type=int, choices=(3, 6), default=3)
    args = parser.parse_args(argv)
    evidence = run(repeat=args.repeat)
    args.out.write_bytes(canonical_json_bytes(evidence))
    reporter = evidence['workloads']['reporter']['modes']
    print(json.dumps({'parity': True,
                      'reporter_full_bodies': reporter['B']['actual_work']['derivation_body_evaluations'],
                      'reporter_session_bodies': reporter['C']['actual_work']['derivation_body_evaluations'],
                      'reporter_timing_medians': evidence['workloads']['reporter']['timing']['medians']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
