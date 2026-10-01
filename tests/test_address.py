"""The derivation address: produced since Phase 2, parsed since Phase 3.

Phase 2 pinned ``parse_address`` returning ``None`` for the derivation class
as its deliberate downstream boundary ("global parsing and gnd coverage
consumption intentionally remain Phase 3 work"). Phase 3 T3.6 moved that
boundary, so the old pin's subject moved out from under it and it is RETIRED
here rather than left as a test about nothing (the 005 correction-record
rule); the positive contract replaces it.
"""

from gnd.address import derivation_address, fact_type_address, parse_address


def test_derivation_address_is_coherent_and_distinct() -> None:
    assert derivation_address("book_is_eligible") == "derivation:book_is_eligible"
    assert derivation_address("book_is_eligible") != fact_type_address("book_is_eligible")


def test_derivation_address_round_trips_through_the_global_parser() -> None:
    parsed = parse_address(derivation_address("book_is_eligible"))
    assert parsed is not None
    assert parsed.element_class == "derivation"
    assert parsed.identifier == "book_is_eligible"
    assert parsed.addressing == "declared-id"
