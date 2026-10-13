"""Averaging includes every observation and never hides a slow individual check."""
from types import SimpleNamespace

import pytest
import test_guarded_corpus as corpus


def install_fake_work(monkeypatch, durations):
    elapsed = [0.0]
    calls = [0]
    clock_calls = [0]

    def clock():
        if clock_calls[0] % 2:
            elapsed[0] += durations[calls[0] - 1]
        clock_calls[0] += 1
        return elapsed[0]

    def check(*_args):
        calls[0] += 1
        return SimpleNamespace(verdicts=[SimpleNamespace(
            constraint_ref='constraints[0]', verdict='pass', message='bindings=1')])

    monkeypatch.setattr(corpus, '_performance_population', lambda _n: (None, None, 1))
    monkeypatch.setattr(corpus, 'check', check)
    monkeypatch.setattr(corpus.time, 'perf_counter', clock)
    return calls


def test_batches_include_all_observations(monkeypatch):
    calls = install_fake_work(monkeypatch, [.1, .1, .1, .1, .9] * 20)
    samples = corpus._guarded_timing_samples()
    assert all(row == pytest.approx([.26] * 9) for row in samples)
    assert calls[0] == 100


def test_batch_average_cannot_hide_one_slow_check(monkeypatch):
    install_fake_work(monkeypatch, [2.1] + [.1] * 99)
    with pytest.raises(AssertionError, match='individual check exceeded two seconds'):
        corpus._guarded_timing_samples()
