from __future__ import annotations

from support.v62_phase6_corpus import assert_answer, loaded_case

from gnd.coverage import _element_universe


def test_exists_uses_one_constraint_address(tmp_path):
    model, *_ = loaded_case(tmp_path)
    elements, _ = _element_universe(model)
    addresses = [address for address, element_class, _ in elements if element_class == 'constraint']
    assert addresses.count('constraint:neighbor_residue') == 1
    assert not any('exists' in address or 'where' in address for address in addresses)
    assert_answer('E15', exit=0, addresses=['constraint:neighbor_residue'], exists_subaddresses=0)
