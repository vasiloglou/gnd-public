from __future__ import annotations

import itertools

from proof.v6.derivation import proof_kernel


def test_obligation_kernel_exhaustively_matches_the_normative_partition():
    for covered, structured, semiderived, missing, surplus in itertools.product(
        (False, True), repeat=5
    ):
        expected = (
            4
            if not covered or not structured
            else 1
            if missing or (surplus and not semiderived)
            else 0
        )
        assert (
            proof_kernel.obligation_verdict(covered, structured, semiderived, missing, surplus)
            == expected
        )
        assert proof_kernel.finding_mask(semiderived, missing, surplus) == (
            int(missing) + 2 * int(surplus and not semiderived)
        )


def test_coverage_precedes_opaque_and_lower_rules_use_computed_rows():
    assert proof_kernel.coverage_reason(False, False) == 1
    assert proof_kernel.coverage_reason(True, False) == 2
    assert proof_kernel.visible_in_upper(0, computed=False, claimed=True)
    assert proof_kernel.visible_in_upper(1, computed=True, claimed=False)
    assert proof_kernel.visible_in_upper(2, computed=True, claimed=False)


def test_band_precedence_is_fail_then_unchecked_then_vacuous_then_clean():
    assert proof_kernel.composed_band(True, True, True) == 1
    assert proof_kernel.composed_band(False, True, True) == 4
    assert proof_kernel.composed_band(False, False, True) == 2
    assert proof_kernel.composed_band(False, False, False) == 0

