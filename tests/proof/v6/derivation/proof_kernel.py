"""Pure decision kernels mirrored from the production derivation semantics."""

from __future__ import annotations


def obligation_verdict(
    covered: bool,
    structured: bool,
    semiderived: bool,
    missing: bool,
    surplus: bool,
) -> int:
    """Encode pass=0, fail=1 and unchecked=4 for the admitted rule fragment."""
    if not covered:
        return 4
    if not structured:
        return 4
    if missing or (surplus and not semiderived):
        return 1
    return 0


def finding_mask(semiderived: bool, missing: bool, surplus: bool) -> int:
    """Encode incomplete=1 and unsound=2 in normative finding order."""
    result = 0
    if missing:
        result += 1
    if surplus and not semiderived:
        result += 2
    return result


def composed_band(has_fail: bool, has_unchecked: bool, has_vacuous: bool) -> int:
    if has_fail:
        return 1
    if has_unchecked:
        return 4
    if has_vacuous:
        return 2
    return 0


def visible_in_upper(kind: int, computed: bool, claimed: bool) -> bool:
    """kind: 0 base, 1 derived, 2 semiderived."""
    if kind == 0:
        return claimed
    return computed


def coverage_reason(covered: bool, structured: bool) -> int:
    """Encode none=0, not-covered=1 and opaque=2 with coverage first."""
    if not covered:
        return 1
    if not structured:
        return 2
    return 0
