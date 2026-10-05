from __future__ import annotations

import pytest
from support.v62_phase2_corpus import FIXTURE, write_model

from gnd.model import ModelValidationError, load_model


@pytest.mark.parametrize('verb', ['assert', 'retract'], ids=['G03', 'G04'])
def test_semiderived_effects_are_refused(tmp_path, verb: str) -> None:

    def mutate(doc):
        doc['operations'][0]['effects'].append({verb: {'fact_type': 'resolvable', 'bind': {'ticket': '$ticket'}}})
    with pytest.raises(ModelValidationError) as caught:
        load_model(write_model(tmp_path, mutate))
    assert any(issue.rule_id == 'semantic:derivation-effect-on-semiderived' for issue in caught.value.issues)

def test_g01_authored_surplus_is_not_an_upper_stratum_input() -> None:
    model = load_model(FIXTURE / 'models/dynamic.orm.yaml')
    from gnd.checker import structured_extension_view
    from gnd.population import load_population
    pre = load_population(FIXTURE / 'populations/pre-open.pop.yaml', model=model)
    view = structured_extension_view(model, pre)
    assert {row['ticket'] for row in view.facts['ready']} == set()
