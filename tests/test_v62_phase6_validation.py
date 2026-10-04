from __future__ import annotations

import pytest
from support.v62_phase6_corpus import assert_answer, document, loaded_case

from gnd.model import ModelValidationError


def test_exists_positive_range_restriction(tmp_path):
    model, *_ = loaded_case(tmp_path)
    assert model.constraints[0]['consequent']['exists']['atoms']
    assert_answer('E09', exit=0, validation='accepted')

def test_exists_unsafe_variables_rejected(tmp_path):
    model = document()
    exists = model['constraints'][0]['consequent']['exists']
    exists['where'][0]['left'] = {'fn': 'mod', 'args': ['$only_where', 30]}
    with pytest.raises(ModelValidationError) as excinfo:
        loaded_case(tmp_path / 'nested', model)
    assert 'semantic:guarded-exists-range' in {issue.rule_id for issue in excinfo.value.issues}
    assert_answer('E10A', exit=3, rule_id='semantic:guarded-exists-range')
    model = document()
    model['constraints'][0]['consequent']['exists']['where'][0]['left'] = '$unbound'
    with pytest.raises(ModelValidationError) as excinfo:
        loaded_case(tmp_path / 'direct', model)
    assert 'semantic:guarded-exists-where-bound' in {issue.rule_id for issue in excinfo.value.issues}
    assert_answer('E10B', exit=3, rule_id='semantic:guarded-exists-where-bound')

def test_exists_where_primitive_mismatch_is_rejected(tmp_path):
    model = document()
    model['constraints'][0]['consequent']['exists']['where'][0] = {'operator': '=', 'left': '$pci', 'right': 'text'}
    with pytest.raises(ModelValidationError) as excinfo:
        loaded_case(tmp_path, model)
    assert 'semantic:guarded-exists-where-type' in {issue.rule_id for issue in excinfo.value.issues}
