from __future__ import annotations

from support.v62_phase5_corpus import document

from gnd.model import Model
from gnd.redaction import RedactionPolicy


def _policy() -> RedactionPolicy:
    return RedactionPolicy.from_model(Model.model_validate(document()))

def test_r01_a_redacted_input_taints_the_float_head_that_reads_it() -> None:
    policy = _policy()
    assert ('margin_sample', 'margin') in policy.derivation_roles('sample_margin_sqrt')

def test_r02_taint_propagates_across_a_second_purely_derived_stratum() -> None:
    policy = _policy()
    roles = policy.derivation_roles('sample_margin_sqrt_doubled')
    assert ('margin_sample', 'margin') in roles
    assert ('sample_margin_sqrt', 'margin_sqrt') in roles

def test_r03_an_unrelated_public_derivation_stays_untainted() -> None:
    policy = _policy()
    assert policy.derivation_roles('sample_serving_distance_km') == frozenset()
    assert policy.derivation_roles('sample_rate_kbps') == frozenset()
