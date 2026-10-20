"""IE0 discriminator controls for the measurement instrument, not an optimizer."""
from __future__ import annotations

import copy
import importlib.util
import signal
import sys
from pathlib import Path

import pytest

from gnd import api, checker, extensions
from gnd.errors import UnvalidatedPopulationError
from gnd.extension_preparation import fingerprint

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('measure_incremental_evaluation', ROOT / 'tools/measure_incremental_evaluation.py')
tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tool)


@pytest.fixture(autouse=True)
def hang_guard():
    if not hasattr(signal, 'SIGALRM'):
        yield
        return
    old = signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError('IE0 600s guard')))
    signal.alarm(600)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)


def test_fixture_identity_and_public_provenance():
    import hashlib
    import re
    provenance = (tool.previous.REPORTER / 'PROVENANCE.md').read_text()
    for name, digest in re.findall(r'^\| `([^`]+)` \| `[0-9a-f]{64}` \| `([0-9a-f]{64})` \|$', provenance, re.MULTILINE):
        assert hashlib.sha256((tool.previous.REPORTER / name).read_bytes()).hexdigest() == digest
    pairs = list(tool.localized_inputs())
    assert len(pairs) == 6
    assert all(p.matches_validation_marker(m) for m, p in pairs)


def test_full_replay_parity_and_denominators():
    all_payloads = []
    for receipts, count in [(False, 25), (True, 19)]:
        with tool.count_work() as counts:
            payloads = tool.replay_full('reporter', receipts=receipts)
        assert len(payloads) == 13 and counts['checker_runs'] == count
        assert counts['derivation_body_evaluations'] > 0
        assert counts['constraint_evaluations'] > 0
        all_payloads.append([tool.previous.normalized_digest(p) for p in payloads])
    assert all_payloads[0] == all_payloads[1]
    assert [p['exit_code'] for p in tool.replay_full('course', receipts=False)] == [1, 1, 0]


def assert_live(counter):
    m, p = next(tool.localized_inputs())
    with tool.count_work() as counts:
        api.check(m, p)
    assert counts[counter] > 0


def test_derivation_counter_liveness(monkeypatch):
    assert_live('derivation_body_evaluations')
    mapping = dict(tool.CODE_COUNTERS)
    mapping.pop(extensions._clause_bindings.__code__)
    monkeypatch.setattr(tool, 'CODE_COUNTERS', mapping)
    with pytest.raises((AssertionError, KeyError)):
        assert_live('derivation_body_evaluations')
    with tool.count_work() as counts:
        fingerprint({'x': [1]})
    assert counts.get('derivation_body_evaluations', 0) == 0
    assert counts['fingerprint_nodes'] > 0


def test_constraint_and_alias_counter_liveness(monkeypatch):
    from gnd.checker import _clause_bindings as clause_bindings
    assert clause_bindings is extensions._clause_bindings
    m, p = next(tool.localized_inputs())
    facts = extensions.base_relations(m, p)
    rule = m.fact_types[2]['derivation_rule']
    with tool.count_work() as counts:
        clause_bindings(rule, extensions._relation_facts(facts), extensions.JoinWork())
    assert counts['derivation_body_evaluations'] == 1
    assert_live('constraint_evaluations')
    monkeypatch.setattr(tool, 'EVALUATOR_CODES', set())
    with pytest.raises((AssertionError, KeyError)):
        assert_live('constraint_evaluations')


def test_census_has_discriminating_stories():
    rows = {name: tool.observation(m, p) for name, m, p in tool.extra_controls()}
    assert rows['recursive']['extensions'] != rows['recursive-delete']['extensions']
    assert rows['negative-absent']['extensions'] != rows['negative-present']['extensions']
    assert rows['aggregate']['unavailable'] != rows['unavailable']['unavailable']
    assert rows['roster-empty']['payload'] != rows['roster-added']['payload']
    assert 'partial' in rows
    pairs = list(tool.localized_inputs())
    before, after = [tool.semantic_envelope(*pairs[i]) for i in (0, 5)]
    assert before['extensions'] == after['extensions']
    assert before['lineage'] != after['lineage']
    for family in tool.FAMILIES:
        assert f'| {family} |' in tool.census()
    m, p = pairs[0]
    p.facts['left'].append({'item': 'unvalidated'})
    with pytest.raises(UnvalidatedPopulationError):
        checker.check(m, p)


@pytest.mark.parametrize('surface', tool.SURFACES)
def test_oracle_rejects_corruption(surface):
    m, p = next(tool.localized_inputs())
    original = tool.observation(m, p)
    changed = copy.deepcopy(original)
    changed[surface] = ['deliberate wrong semantic value']
    assert tool.compare_results(original, changed) == [surface]
    del changed[surface]
    assert surface in tool.compare_results(original, changed)


def test_instrument_cleanup_and_timing_order(monkeypatch, tmp_path):
    calls = []
    def replay(workload, *, receipts):
        assert sys.getprofile() is None
        calls.append('B' if receipts else 'F')
        return []
    monkeypatch.setattr(tool, 'replay_full', replay)
    for repeat in range(1, 8):
        calls.clear()
        result = tool.measure_modes('localized', repeat=repeat)
        assert result['order'] == [('ABC', 'BCA', 'CAB')[i % 3] for i in range(repeat)]
        assert all(len(samples) == repeat for samples in result['samples'].values())
        assert calls[3:] == ['B' if a == 'B' else 'F' for order in result['order'] for a in order]
    old = sys.getprofile()
    original = tool.previous.Model.model_dump if hasattr(tool.previous, 'Model') else None
    with pytest.raises(RuntimeError), tool.count_work():
        raise RuntimeError('rollback profiler')
    assert sys.getprofile() is old
    if original:
        assert tool.previous.Model.model_dump is original
    for args in (['--repeat', '0'], ['--repeat', '8'], ['--workload', 'wrong']):
        with pytest.raises(SystemExit) as exc:
            tool.main([*args, '--out', str(tmp_path)])
        assert exc.value.code == 2


def test_receipt_report_mutation_probe():
    assert tool.receipt_probe()['report_mutable']


def test_baseline_evidence_completeness():
    from test_incremental_baseline_review import accepted_document
    sample = accepted_document()
    assert tool.validate_evidence(sample)
    empty = copy.deepcopy(sample)
    empty['work'] = {}
    assert not tool.validate_evidence(empty)
    for key in ('identities', 'parity', 'source_head'):
        changed = copy.deepcopy(sample)
        del changed[key]
        assert not tool.validate_evidence(changed)
    changed = copy.deepcopy(sample)
    changed['parity'][0]['mismatches'] = ['lineage']
    assert not tool.validate_evidence(changed)
