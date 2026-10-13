"""Keep inherited reference validation outside the added-layer timing gate."""
from support import public_v71_witness_corpus as corpus

from gnd import model


def test_defining_reference_intake_is_counted(tmp_path, monkeypatch):
    ticks = [0.0]
    original = model.validate_declarations

    def counted_validation(*args, **kwargs):
        ticks[0] += 1.0
        return original(*args, **kwargs)

    monkeypatch.setattr(model, 'validate_declarations', counted_validation)
    monkeypatch.setattr(corpus.time, 'monotonic', lambda: ticks[0])
    measurement = {}
    row = next(row for row in corpus.INPUTS['cases'] if row['id'] == 'dispatch-B01-direct')
    result = corpus.execute(row, tmp_path, monkeypatch, measurement=measurement)
    corpus.assert_answer(result, corpus.ANSWERS[row['id']])
    assert measurement['inherited_intake_seconds'] > 0
    assert ticks[0] == sum(measurement.values()), (
        'defining-module validation escaped the inherited timing accounting', measurement)
