"""IE0: full-evaluation differential baseline; no runtime optimization.

Counters observe code objects, so imported identity aliases are counted without
patching runtime algorithms. Timing uses separate, uninstrumented fresh inputs.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import dataclasses
import hashlib
import json
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from collections.abc import Mapping
from contextvars import ContextVar
from enum import Enum
from pathlib import Path
from typing import Any

from gnd import (
    api,
    extension_preparation,
    extensions,
    semantic_rows,
    semantic_spec,
    temporal_guarded,
)
from gnd import correspondence as correspondence_module
from gnd.artifacts import canonical_json_bytes
from gnd.branches import capture_branches
from gnd.constraint_families import FAMILIES
from gnd.model import derivation_dependencies, derivation_strata, load_model
from gnd.population import load_population, load_population_bytes

# Script invocation and import from tests use the same, explicit tool directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import measure_transition_cost as previous

ROOT = previous.ROOT
FIXTURE = ROOT / 'tests/fixtures/incremental_evaluation'
SURFACES = ('payload', 'exit', 'branches', 'extensions', 'lineage', 'unavailable', 'possible')
CALL_SINK = ContextVar('incremental_measurement_calls', default=None)
TIME_SINK = ContextVar('incremental_measurement_timing', default=None)
CODE_COUNTERS = {
    api.check.__code__: 'public_check_calls',
    api.check_with_receipt.__code__: 'receipt_mints',
    api.transition.__code__: 'public_transition_calls',
    extensions._clause_bindings.__code__: 'derivation_body_evaluations',
    extensions._partial_clause_rows.__code__: 'partial_body_evaluations',
    extension_preparation._Fingerprint.freeze.__code__: 'fingerprint_nodes',
}

# Successful verdict primitives plus guarded antecedent evaluation: actual
# work entries, never finding labels. Non-applicable indexed probes (None) do
# not count; nested primitive calls are intentionally distinct executed work.
EVALUATOR_CODES = {f.__code__ for f in (
    correspondence_module._inline_uniqueness_result,
    correspondence_module._indexed_mandatory_result,
    correspondence_module._indexed_guarded_bindings,
    correspondence_module._indexed_guarded_verdict,
    correspondence_module._indexed_guarded_exists_verdict,
    correspondence_module._legacy_string_order_result,
    semantic_rows.indexed_subset_verdict, semantic_spec.verdict_of,
    temporal_guarded.evaluate_temporal_guard,
)}
CALCULATOR_CODES = {extensions._evaluate_stratified_extensions.__wrapped__.__code__,
                    extensions._python_extension_calculator.__code__,
                    extensions._exact_extension_calculator.__code__}
SEMANTIC_SINK = ContextVar('incremental_measurement_semantics', default=None)


COMPLETE_CALL_SINK = ContextVar('session_complete_calls', default=None)
SESSION_STATS_SINK = ContextVar('session_stats_sink', default=None)
DIAGNOSTIC_WORK = ContextVar('session_diagnostic_work', default=False)


def complete_calculation_key(result):
    values = result.extensions
    complete = {
        'relations': {name: (relation.fact_type, relation.roles, relation.rows,
                             relation.row_lineage, relation.identity_codec_version)
                      for name, relation in values.items()},
        'unavailable': packed(getattr(values, 'unavailable', {})),
        'possible': packed(getattr(values, 'possible', {})),
        'logical_work': packed(result.counted_operations),
    }
    key = extension_preparation.fingerprint(complete)
    if key is None:
        raise ValueError('refused complete diagnostic projection')
    return key


@contextlib.contextmanager
def capture_complete():
    reached = []
    boundaries = CALCULATOR_CODES | {
        extensions._incremental_components.__code__,
        extensions._evaluate_stratified_extensions.__code__,
    }
    depth = 0
    old = sys.getprofile()

    def profile(frame, event, result):
        nonlocal depth
        if old is not None:
            old(frame, event, result)
        if frame.f_code in boundaries:
            if event == 'call':
                depth += 1
            elif event == 'return':
                depth -= 1
                if depth == 0 and result is not None:
                    reached.append(hashlib.sha256(canonical_json_bytes(
                        complete_calculation_key(result))).hexdigest())

    sys.setprofile(profile)
    try:
        yield reached
    finally:
        sys.setprofile(old)


def _session_stats(owner):
    sink = SESSION_STATS_SINK.get()
    if owner is not None and sink is not None:
        sink.append(owner.stats())


def calculation_envelope(calculated):
    return {
        'extensions': packed({name: relation.rows for name, relation in calculated.items()}),
        'lineage': packed({name: relation.row_lineage for name, relation in calculated.items()}),
        'unavailable': packed(getattr(calculated, 'unavailable', {})),
        'possible': packed(getattr(calculated, 'possible', {})),
    }


def capture_return(frame, event, result):
    sink = SEMANTIC_SINK.get()
    if sink is not None and event == 'return' and frame.f_code in CALCULATOR_CODES and result is not None:
        envelope = calculation_envelope(result.extensions)
        for key, value in envelope.items():
            sink[key].append(hashlib.sha256(canonical_json_bytes(value)).hexdigest())


@contextlib.contextmanager
def capture_semantics():
    sink = {key: [] for key in SURFACES}
    token = SEMANTIC_SINK.set(sink)
    old = sys.getprofile()
    def profile(frame, event, arg):
        if old:
            old(frame, event, arg)
        capture_return(frame, event, arg)
    sys.setprofile(profile)
    try:
        with capture_branches() as branches:
            yield sink
        sink['branches'] = sorted(branches)
    finally:
        sys.setprofile(old)
        SEMANTIC_SINK.reset(token)


def packed(value):
    """Lossless typed diagnostic projection, rejecting unknown object types."""
    if isinstance(value, Enum):
        return {'enum': type(value).__qualname__, 'value': packed(value.value)}
    if dataclasses.is_dataclass(value):
        return {f.name: packed(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, Mapping):
        if any(not isinstance(k, str) for k in value):
            raise TypeError('diagnostic mapping keys must be strings')
        return {k: packed(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [packed(v) for v in value]
    if isinstance(value, (set, frozenset)):
        return sorted((packed(v) for v in value), key=lambda v: canonical_json_bytes(v))
    if value is None or type(value) in (str, bool, int, float):
        return value
    if hasattr(value, 'model_dump'):
        return packed(value.model_dump(mode='json'))
    raise TypeError(f'unsupported diagnostic scalar: {type(value).__name__}')


def compare_results(expected: dict[str, Any], actual: dict[str, Any]) -> list[str]:
    return sorted(key for key in SURFACES if key not in expected or key not in actual
                  or canonical_json_bytes(packed(expected[key])) != canonical_json_bytes(packed(actual[key])))


@contextlib.contextmanager
def count_work():
    with previous.counting() as counts:
        old = sys.getprofile()
        for name in CODE_COUNTERS.values():
            counts[name] = 0
        counts['join_candidates'] = 0
        counts['partial_join_candidates'] = 0
        counts['constraint_evaluations'] = 0
        starts = {}

        def profile(frame, event, arg):
            if old:
                old(frame, event, arg)
            if DIAGNOSTIC_WORK.get():
                return
            if event == 'call':
                name = CODE_COUNTERS.get(frame.f_code)
                if name:
                    counts[name] += 1
                if frame.f_code in (extensions._clause_bindings.__code__, extensions._partial_bindings.__code__):
                    work = frame.f_locals['work']
                    starts[id(frame)] = work.join_candidates_indexed
            elif event == 'return' and id(frame) in starts:
                key = 'partial_join_candidates' if frame.f_code is extensions._partial_bindings.__code__ else 'join_candidates'
                counts[key] += frame.f_locals['work'].join_candidates_indexed - starts.pop(id(frame))
            if event == 'return' and frame.f_code in EVALUATOR_CODES and arg is not None:
                counts['constraint_evaluations'] += 1
        sys.setprofile(profile)
        try:
            yield counts
        finally:
            sys.setprofile(old)


def semantic_envelope(model, population):
    calculated, _ = extensions.evaluate_derivations(model, population)
    return calculation_envelope(calculated)


def observation(model, population, *, compiled=False):
    token = extensions.PARTIAL_OPAQUE.set(True) if compiled else None
    try:
        with capture_branches() as branches:
            payload = api.check(model, population, compiled_operations=compiled)
        envelope = semantic_envelope(model, population)
    finally:
        if token is not None:
            extensions.PARTIAL_OPAQUE.reset(token)
    return {'payload': payload, 'exit': payload['exit_code'], 'branches': sorted(branches), **envelope}


def localized_inputs():
    model = load_model(FIXTURE / 'model.orm.json')
    for name in ('initial', 'noop', 'insert', 'delete', 'replace', 'reorder'):
        yield model, load_population(FIXTURE / f'{name}.pop.json', model=model)


def public_call(function):
    sink = CALL_SINK.get()
    before = dict(sink[0]) if sink else {}
    semantic = SEMANTIC_SINK.get()
    positions = {key: len(semantic[key]) for key in ('extensions', 'lineage', 'unavailable', 'possible')} if semantic is not None else {}
    started = time.perf_counter()
    complete = COMPLETE_CALL_SINK.get()
    if complete is None:
        result = function()
    else:
        with capture_branches() as branches, capture_complete() as calculations:
            result = function()
        diagnostic_token = DIAGNOSTIC_WORK.set(True)
        try:
            payload_key = extension_preparation.fingerprint(result)
            if payload_key is None:
                raise ValueError('refused public payload projection')
            complete.append({'payload': hashlib.sha256(canonical_json_bytes(payload_key)).hexdigest(),
                             'exit': result['exit_code'], 'branches': sorted(branches),
                             'calculations': list(calculations)})
        finally:
            DIAGNOSTIC_WORK.reset(diagnostic_token)
    elapsed = time.perf_counter() - started
    if TIME_SINK.get() is not None:
        TIME_SINK.get().append(elapsed)
    if sink:
        counts, rows = sink
        rows.append({'index': len(rows), 'exit': result['exit_code'],
                     'totals': {k: v - before.get(k, 0) for k, v in counts.items()},
                     'instrumented_seconds': elapsed,
                     'semantics': {key: semantic[key][position:] for key, position in positions.items()}})
    return result


def replay_full(workload: str, *, receipts: bool, incremental: bool = False) -> list[dict[str, Any]]:
    if workload == 'localized':
        result, owner = [], None
        for model, population in localized_inputs():
            if incremental and owner is None:
                owner = api.EvaluationSession(model)
            def checked(m=model, p=population, owner=owner):
                if owner:
                    return owner.check_with_receipt(p)[0] if receipts else owner.check(p)
                return api.check_with_receipt(m, p)[0] if receipts else api.check(m, p)
            result.append(public_call(checked))
        _session_stats(owner)
        return result
    course = workload == 'course'
    model = load_model(previous.COURSE / 'model.orm.json' if course else previous.REPORTER / 'steps.orm.json')
    owner = api.EvaluationSession(model) if incremental else None
    checking = owner.check if owner else lambda p: api.check(model, p)
    minting = owner.check_with_receipt if owner else lambda p: api.check_with_receipt(model, p)
    walking = owner.transition if owner else lambda p, steps, **kwargs: api.transition(model, p, steps, **kwargs)
    result, receipt = [], None
    if course:
        for attempt in ('attempt-1', 'attempt-2', 'attempt-3'):
            population = load_population(previous.COURSE / 'state.pop.json', model=model)
            steps = previous._course_steps(f'{attempt}.steps.json')
            def walk(p=population, steps=steps):
                checked, current = minting(p) if receipts else (checking(p), None)
                if checked['exit_code'] not in (0, 2):
                    raise RuntimeError('course precheck unexpectedly refused')
                return walking(p, steps, pre_receipt=current)
            result.append(public_call(walk))
    else:
        for row in previous.reporter_calls():
            population = load_population(previous.REPORTER / row['population'], model=model)
            if row['call'] == 'check':
                if receipts:
                    held = []
                    def checked(p=population, held=held):
                        payload, minted = minting(p)
                        held.append(minted)
                        return payload
                    result.append(public_call(checked))
                    receipt = held[0]
                else:
                    result.append(public_call(lambda p=population: checking(p)))
            else:
                steps = json.loads((previous.REPORTER / row['steps']).read_text())
                result.append(public_call(lambda p=population, steps=steps, receipt=receipt:
                                          walking(p, steps, pre_receipt=receipt)))
    _session_stats(owner)
    return result


def schedule(repeat):
    return [('ABC', 'BCA', 'CAB')[i % 3] for i in range(repeat)]


def _measure_modes(workload: str, *, repeat: int, session_arm: bool) -> dict[str, Any]:
    samples = {arm: [] for arm in 'ABC'}
    evaluation = {arm: [] for arm in 'ABC'}
    preparation = {arm: [] for arm in 'ABC'}
    def replay(arm):
        if session_arm and arm == 'C':
            return replay_full(workload, receipts=True, incremental=True)
        return replay_full(workload, receipts=arm == 'B')

    for arm in 'ABC':
        replay(arm)
    for order in schedule(repeat):
        for arm in order:
            public_times = []
            token = TIME_SINK.set(public_times)
            start = time.perf_counter()
            try:
                replay(arm)
            finally:
                TIME_SINK.reset(token)
            total = time.perf_counter() - start
            samples[arm].append(total)
            evaluation[arm].append(sum(public_times))
            preparation[arm].append(total - sum(public_times))
    return {'order': schedule(repeat), 'samples': samples,
            'public_evaluation_samples': evaluation, 'loading_and_driver_samples': preparation,
            'medians': {arm: statistics.median(rows) for arm, rows in samples.items()},
            'range_s': {arm: max(rows) - min(rows) for arm, rows in samples.items()},
            'positionally_balanced': repeat % 3 == 0,
            'boundary': 'complete public replay including input loading; uninstrumented'}


def measure_modes(workload: str, *, repeat: int) -> dict[str, Any]:
    return _measure_modes(workload, repeat=repeat, session_arm=False)


def measure_session_modes(workload: str, *, repeat: int) -> dict[str, Any]:
    import tracemalloc

    if sys.getprofile() is not None or tracemalloc.is_tracing():
        raise ValueError('timing must be uninstrumented')
    return _measure_modes(workload, repeat=repeat, session_arm=True)


def extra_controls():
    """Existing public syntax, with explicit mutations and fresh admission."""
    from ruamel.yaml import YAML

    from gnd.model import Model
    yaml = YAML(typ='safe')
    recursive = ROOT / 'tests/fixtures/v70-phase4'
    model = load_model(recursive / 'recursive.orm.yaml')
    document = json.loads((recursive / 'recursive.pop.json').read_text())
    for name, edges in [('recursive', document['facts']['edge']),
                        ('recursive-delete', [{'source': 'A', 'target': 'B'}]),
                        ('recursive-alternate-delete', [{'source': 'A', 'target': 'B'}, {'source': 'A', 'target': 'C'}]),
                        ('recursive-alternate', [{'source': 'A', 'target': 'B'},
                         {'source': 'B', 'target': 'C'}, {'source': 'A', 'target': 'C'}]),
                        ('partial', [{'source': 'A', 'target': 'B'}, {'source': 'B', 'target': 'C'}, {'source': 'B', 'target': {'$opaque': 'unknown'}}])]:
        changed = copy.deepcopy(document)
        changed['facts']['edge'] = edges
        yield name, model, load_population_bytes(json.dumps(changed).encode(), source='control.json', model=model)
    aggregate = ROOT / 'tests/fixtures/v62-phase4'
    manifest = json.loads((aggregate / 'cases.json').read_text())
    model_doc = yaml.load((aggregate / manifest['model']).read_text())
    population_doc = yaml.load((aggregate / manifest['population']).read_text())
    for name in ('aggregate', 'unavailable'):
        changed_model = copy.deepcopy(model_doc)
        if name == 'unavailable':
            changed_model['fact_types'][1]['derivation_rule']['aggregate']['of'] = {'fn': 'mod', 'args': [1, 0]}
        model = Model.model_validate(changed_model)
        yield name, model, load_population_bytes(json.dumps(population_doc).encode(), source='control.json', model=model)
    model_doc = json.loads((FIXTURE / 'model.orm.json').read_text())
    population_doc = json.loads((FIXTURE / 'initial.pop.json').read_text())
    model_doc['fact_types'][2]['derivation_rule']['negate'] = [{'fact_type': 'right', 'bind': {'item': '$i'}}]
    for name, right in [('negative-absent', 'other'), ('negative-present', 'alpha')]:
        model = Model.model_validate(copy.deepcopy(model_doc))
        changed = copy.deepcopy(population_doc)
        changed['facts']['right'] = [{'item': right}]
        yield name, model, load_population_bytes(json.dumps(changed).encode(), source='control.json', model=model)
    model_doc['fact_types'][2]['constraints'].append({'type': 'mandatory', 'role': 'item', 'modality': 'alethic', 'source': 'explicit', 'status': 'confirmed', 'provenance': {'user_quote': 'Each item participates.'}})
    model = Model.model_validate(copy.deepcopy(model_doc))
    for name, roster in [('roster-empty', []), ('roster-added', ['unseen'])]:
        changed = copy.deepcopy(population_doc)
        changed['instances']['item'] = roster
        yield name, model, load_population_bytes(json.dumps(changed).encode(), source='control.json', model=model)


def parity_checks():
    # Each side owns its model/population; second observation never consumes a
    # first-side cached result, and required internal surfaces cannot be absent.
    results = []
    first_inputs = [(str(i), m, p) for i, (m, p) in enumerate(localized_inputs())] + list(extra_controls())
    second_inputs = [(str(i), m, p) for i, (m, p) in enumerate(localized_inputs())] + list(extra_controls())
    for (name, m, p), (_, other_m, other_p) in zip(first_inputs, second_inputs, strict=True):
        first, second = observation(m, p, compiled=name == 'partial'), observation(other_m, other_p, compiled=name == 'partial')
        results.append({'case': name, 'surfaces': list(SURFACES),
                        'mismatches': compare_results(first, second),
                        'digest': hashlib.sha256(canonical_json_bytes(first)).hexdigest(),
                        'exit': first['exit'], 'expected_exit': {'recursive': 0, 'recursive-alternate': 0, 'partial': 4, 'aggregate': 0, 'unavailable': 4}.get(name, 1)})
    return results


def reference_and_option_controls():
    from ruamel.yaml import YAML
    yaml = YAML(typ='safe')
    results = []
    with tempfile.TemporaryDirectory(prefix='gnd-ie0-reference-') as temp:
        directory = Path(temp).resolve() / 'dispatch'
        shutil.copytree(ROOT / 'tests/fixtures/reference-corpus/dispatch', directory)
        model_path, population_path = directory / 'model.orm.yaml', directory / 'candidate.pop.json'
        model_doc = yaml.load(model_path.read_text())
        for label, expected in [('reference-initial', 0), ('reference-changed', 1)]:
            if label.endswith('changed'):
                reference_path = directory / 'references/catalog.pop.json'
                ref_doc = json.loads(reference_path.read_text())
                ref_doc['facts']['dispatch_catalog_allows'] = []
                raw = (json.dumps(ref_doc) + '\n').encode()
                reference_path.write_bytes(raw)
                model_doc['reference_populations'][0]['sha256'] = hashlib.sha256(raw).hexdigest()
                with model_path.open('w') as stream:
                    yaml.dump(model_doc, stream)
            with capture_semantics() as first:
                payload = api.check(model_path, population_path)
            with capture_semantics() as second:
                control = api.check(model_path, population_path)
            for semantics, outcome in [(first, payload), (second, control)]:
                semantics['payload'] = previous.normalized_digest(outcome)
                semantics['exit'] = outcome['exit_code']
            results.append({'case': label, 'exit': payload['exit_code'], 'expected_exit': expected,
                            'mismatches': compare_results(first, second)})
    _, model, population = next(row for row in extra_controls() if row[0] == 'partial')
    default = observation(model, population)
    compiled = observation(model, population, compiled=True)
    if default['possible'] or not compiled['possible']:
        raise RuntimeError('check-option discriminator did not expose possible patterns')
    results.append({'case': 'option-compiled', 'exit': compiled['exit'], 'expected_exit': 4,
                    'mismatches': compare_results(compiled, observation(model, population, compiled=True))})
    return results


def receipt_probe():
    model = load_model(previous.COURSE / 'model.orm.json')
    population = load_population(previous.COURSE / 'state.pop.json', model=model)
    steps = previous._course_steps('attempt-3.steps.json')
    _, receipt = api.check_with_receipt(model, population)
    if not receipt.reusable or not receipt.report.verdicts:
        raise RuntimeError('receipt probe lacks reusable checked constraint report')
    control = api.transition(model, population, steps, pre_receipt=receipt)
    original = copy.deepcopy(receipt.report)
    receipt.report.verdicts[0].message = 'IE0 mutation probe'
    actual = api.transition(model, population, steps, pre_receipt=receipt)
    return {'report_mutable': receipt.report != original, 'reusable': receipt.reusable,
            'transition_changed': actual != control}


def identities():
    paths = [ROOT / 'pyproject.toml', ROOT / 'uv.lock', Path(__file__), Path(previous.__file__),
             ROOT / 'tests/test_incremental_baseline.py', ROOT / 'tests/test_incremental_baseline_review.py']
    paths += sorted((ROOT / 'src/gnd').rglob('*.py'))
    paths += sorted(FIXTURE.glob('*.json')) + sorted(previous.REPORTER.glob('*.json'))
    for directory in [ROOT / 'src/gnd/schema', previous.COURSE,
                      ROOT / 'tests/fixtures/v70-phase4', ROOT / 'tests/fixtures/v62-phase4',
                      ROOT / 'tests/fixtures/reference-corpus/dispatch']:
        paths += sorted(p for p in directory.rglob('*') if p.suffix in ('.json', '.yaml'))
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def census():
    model, _ = next(localized_inputs())
    lines = ['# IE0 eligibility census', '', 'Proposed, not implemented reuse eligibility.', '',
             '| Family | Eligibility | Invalidation |', '|---|---|---|']
    for name in FAMILIES:
        lines.append(f'| {name} | unresolved; evaluate fresh until classified | facts, rosters, covers, model, options, references |')
    lines += ['', '## Localized dependencies', '', json.dumps({
        k: sorted(v) for k, v in derivation_dependencies(model.model_dump()).items()}, sort_keys=True),
        '', 'Strata: ' + repr(derivation_strata(model.model_dump())), '',
        'Unchanged independent component must have zero executed bodies/evaluators.',
        'Reorder invalidates origin coordinates. Recursive SCC, negation, aggregates,',
        'partial/exact unavailability and reference/observer routes require explicit',
        'cases before eligibility; default is fresh. See stories.json for source controls.']
    return '\n'.join(lines) + '\n'


def validate_evidence(document):
    required = {'source_head', 'identities', 'work', 'parity', 'receipt_probe', 'new_workload'}
    if not required <= document.keys() or document['identities'] != identities() or not document['work']:
        return False
    if not document['parity'] or any(row['mismatches'] or row['exit'] != row['expected_exit'] for row in document['parity']):
        return False
    for name, workload in document['work'].items():
        if not {'full', 'receipts', 'fresh_full'} <= workload.keys():
            return False
        expected_calls = {'reporter': 13, 'course': 3, 'localized': 6}.get(name)
        for mode, row in workload.items():
            totals = row['totals']
            public_calls = sum(totals.get(k, 0) for k in ('public_check_calls', 'receipt_mints', 'public_transition_calls'))
            if public_calls != (6 if name == 'course' else expected_calls):
                return False
            if row['calls'] != expected_calls or len(row['payload_digests']) != expected_calls:
                return False
            if any(totals.get(k, 0) <= 0 for k in ('checker_runs', 'derivation_body_evaluations', 'constraint_evaluations')):
                return False
            if name == 'reporter' and totals['checker_runs'] != (19 if mode == 'receipts' else 25):
                return False
        if workload['full']['payload_digests'] != workload['receipts']['payload_digests']:
            return False
        if workload['full']['branches'] != workload['receipts']['branches']:
            return False
        expected_exits = {'reporter': [2]*13, 'course': [1, 1, 0], 'localized': [1]*6}[name]
        for row in workload.values():
            semantics = row['semantic_replay']
            if not set(SURFACES) <= semantics.keys() or semantics['exit'] != expected_exits:
                return False
            if any(not semantics[key] for key in ('extensions', 'lineage', 'unavailable', 'possible')):
                return False
            if len(row.get('per_call', [])) != expected_calls:
                return False
        for key in ('extensions', 'lineage', 'unavailable', 'possible'):
            # A/B can differ in duplicate calls because an explicit receipt skips
            # the precheck. Their actually computed semantic values must agree.
            if set(workload['full']['semantic_replay'][key]) != set(workload['receipts']['semantic_replay'][key]):
                return False
            for full_call, receipt_call in zip(workload['full']['per_call'], workload['receipts']['per_call'], strict=True):
                if key not in full_call['semantics'] or key not in receipt_call['semantics']:
                    return False
                if set(full_call['semantics'][key]) != set(receipt_call['semantics'][key]):
                    return False
        if compare_results(workload['full']['semantic_replay'], workload['fresh_full']['semantic_replay']):
            return False
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workload', choices=('all', 'reporter', 'course', 'localized'), default='all')
    parser.add_argument('--repeat', type=int, choices=range(1, 8), default=3)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    try:
        work = {}
        workloads = ('reporter', 'course', 'localized') if args.workload == 'all' else (args.workload,)
        for workload in workloads:
            work[workload] = {}
            for mode in ('full', 'receipts', 'fresh_full'):
                rows = []
                with count_work() as counts:
                    token = CALL_SINK.set((counts, rows))
                    try:
                        with capture_semantics() as semantics:
                            payloads = replay_full(workload, receipts=mode == 'receipts')
                    finally:
                        CALL_SINK.reset(token)
                semantics['payload'] = [previous.normalized_digest(p) for p in payloads]
                semantics['exit'] = [p['exit_code'] for p in payloads]
                work[workload][mode] = {'calls': len(payloads), 'per_call': rows,
                    'branches': semantics['branches'], 'semantic_replay': semantics, 'totals': dict(counts),
                    'payload_digests': [previous.normalized_digest(p) for p in payloads]}
        document = {'source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                    'identities': identities(), 'python': platform.python_version(),
                    'platform': platform.platform(),
                    'uv': subprocess.check_output(['uv', '--version'], text=True).strip(),
                    'dirty_paths': subprocess.check_output(['git', 'status', '--porcelain', '--', 'src/gnd', 'tools/measure_incremental_evaluation.py', 'tests/test_incremental_baseline.py', 'tests/fixtures/incremental_evaluation', 'pyproject.toml', 'uv.lock'], cwd=ROOT, text=True).splitlines(),
                    'counter_owners': {v: f'{k.co_filename.removeprefix(str(ROOT))}:{k.co_firstlineno}' for k, v in CODE_COUNTERS.items()},
                    'constraint_evaluator_owners': sorted(f'{c.co_filename.removeprefix(str(ROOT))}:{c.co_firstlineno}' for c in EVALUATOR_CODES), 'work': work, 'parity': parity_checks() + reference_and_option_controls(),
                    'receipt_probe': receipt_probe(), 'new_workload': 'not supplied',
                    'receipt_arm_meanings': {'reporter': 'mint and consume', 'course': 'mint and consume within each complete walk', 'localized': 'mint only; check-only workload, no reuse claim'}}
        outputs = {'environment.json': {k: v for k, v in document.items() if k not in ('work', 'parity')},
                   'work.json': work, 'parity.json': document['parity'],
                   'timings.json': {w: measure_modes(w, repeat=args.repeat) for w in workloads}}
        for name, value in outputs.items():
            (args.out / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
        (args.out / 'eligibility.md').write_text(census())
        return 0 if validate_evidence(document) else 1
    except Exception as exc:  # noqa: BLE001 -- diagnostic CLI, preserves failure as nonzero
        (args.out / 'failure.json').write_text(json.dumps({'type': type(exc).__name__, 'message': str(exc)}) + '\n')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
