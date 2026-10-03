from __future__ import annotations

import pytest
from support.v62_phase2_corpus import CASES, FIXTURE

from gnd.model import ModelValidationError, derivation_classifications, load_model


def test_complete_dynamic_model_is_admitted() -> None:
    model = load_model(FIXTURE / 'models/dynamic.orm.yaml')
    rows = {row.fact_type: row for row in derivation_classifications(model.model_dump())}
    assert set(rows) == {'resolvable', 'ready', 'ticket_score'}
    assert all(row.complete and row.stability == 'dynamic' for row in rows.values())
    assert rows['ready'].asserted_dependencies == ('blocked', 'evidence')
    assert not [warning for warning in model.warnings if warning.rule_id == 'semantic:op-dynamic-untouched']

@pytest.mark.parametrize('case_id', sorted(CASES))
def test_each_product_case_reaches_the_dynamic_lane(case_id: str) -> None:
    try:
        load_model(FIXTURE / 'models/dynamic.orm.yaml')
    except ModelValidationError as error:
        unsupported = [issue for issue in error.issues if issue.rule_id == 'semantic:derivation-dynamic-operations-unsupported']
        pytest.fail(f'{case_id} is RED only because the approved dynamic-composition lane is absent: {len(unsupported)} blanket refusal(s)')
