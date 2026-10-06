"""Matcher-side scalar identity: lexical normalization + domain-tagged keys (R-10, D-15).

This module MIRRORS the shape of ``gnd.synth.identity.scalar_identity`` —
booleans, numbers and strings as separate domains — and deliberately imports
neither it nor ``gnd.checker._identity_key`` (C1 independence in BOTH
directions: the matcher is composed with the checker and evaluated against the
synthesis oracle, so it may call neither). P-6/F-7 is the precedent bug this
guards: keying on plain equality lets Python's ``1 == True`` fold a boolean
filler into a numeric one, which is exactly the identity collapse F-7 closed in
the checker one layer down.

:func:`lexical_normalize` is R-10's LEXICAL-ONLY rule: casefold, collapse
internal whitespace runs to single spaces, strip — no aliases, nothing
semantic — and it applies to strings ONLY; every other type passes through
unchanged so a number is never coerced into a string domain by normalization.
"""

from __future__ import annotations

from gnd.anchor_identity import (
    ANCHOR_TRANSLATION as _ANCHOR_TRANSLATION,  # noqa: F401 -- compatibility export
)
from gnd.anchor_identity import (
    __all__,  # noqa: F401 -- compatibility export
    anchor_normalize,  # noqa: F401 -- compatibility export
    identity_key,  # noqa: F401 -- compatibility export
    lexical_normalize,  # noqa: F401 -- compatibility export
)
