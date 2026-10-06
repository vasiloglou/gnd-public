"""RF9 CI repair corpus: compatibility state and strict pool refusals."""
import json

import pytest

from gnd import model
from gnd.model import _validation
from gnd.synth.poolfile import PoolValidationError, load_pool


@pytest.mark.parametrize('name', ['_DERIVATION_WORK', '_DERIVATION_ATOM_VISITS', '_DERIVATION_CLASSIFICATION_WORK'])
def test_model_counter_lookup_is_live(monkeypatch, name):
    before = getattr(_validation, name)
    monkeypatch.setattr(_validation, name, before + 173)
    assert getattr(model, name) == before + 173


def test_unknown_model_lookup_refuses():
    with pytest.raises(AttributeError):
        getattr(model, '_rf9_unknown_counter')


@pytest.mark.parametrize('raw', ['{"x": NaN}', '{"x": 1e999}', '{"x": 1, "x": 2}'])
def test_pool_shared_policy_refusal_keeps_boundary(tmp_path, raw):
    path = tmp_path / 'pool.json'
    path.write_text(raw)
    with pytest.raises(PoolValidationError):
        load_pool(path, None)


def test_pool_malformed_json_keeps_decoder_exception(tmp_path):
    path = tmp_path / 'pool.json'
    path.write_text('{')
    with pytest.raises(json.JSONDecodeError):
        load_pool(path, None)
