

from __future__ import annotations

from support.v62_phase3_corpus import FIXTURE

from gnd.address import derivation_address, parse_address
from gnd.model import load_model
from gnd.model_verbalization import render_model_verbalization


def test_v01_v02_nested_head_and_where_terms_have_canonical_text() -> None:
    rendered = render_model_verbalization(load_model(FIXTURE / "models/exact-terms.orm.yaml"))

    assert "residue = mod($value, $divisor)" in rendered
    assert "neg(neg($value)) = $value" in rendered
    assert "abs(mod($value, $divisor)) is less than abs($divisor)" in rendered


def test_v03_v04_terms_reuse_one_derivation_address_without_subterm_ids() -> None:
    address = derivation_address("residue")

    assert address == "derivation:residue"
    assert parse_address(address).identifier == "residue"
    assert "mod" not in address
    assert "where" not in address
