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

import unicodedata
from typing import Any

__all__ = ["anchor_normalize", "identity_key", "lexical_normalize"]


_ANCHOR_TRANSLATION = str.maketrans({
    0x2018: "'", 0x2019: "'", 0x201C: '"', 0x201D: '"',
    **{code: "-" for code in range(0x2010, 0x2016)}, 0x00A0: " ",
})


def anchor_normalize(value: str) -> str:
    """Project source text for anchor matching, independently of identity keys."""
    if not isinstance(value, str):
        raise TypeError("anchor normalization requires a string")
    mapped = unicodedata.normalize("NFC", value).translate(_ANCHOR_TRANSLATION)
    return unicodedata.normalize("NFC", " ".join(mapped.casefold().split()))


def lexical_normalize(value: Any) -> Any:
    """Casefold + collapse whitespace runs + strip — for ``str`` values only.

    ``str.split()`` with no argument splits on ANY whitespace run (spaces,
    tabs, newlines) and drops leading/trailing runs, so the join collapses and
    strips in one move. Non-strings are returned unchanged (R-10: lexical
    only — normalization must never move a value between identity domains).
    """
    if isinstance(value, str):
        return " ".join(value.casefold().split())
    return value


def identity_key(value: Any) -> tuple[str, Any]:
    """The matcher identity key: :func:`lexical_normalize` first, then the
    domain tuple.

    The domain tag is what keeps ``1``, ``True`` and ``"1"`` distinct — the
    bool check MUST precede the int/float check because ``bool`` subclasses
    ``int`` (the F-7 trap). The domains mirror
    ``synth/identity.scalar_identity``'s specification without importing it.
    """
    normalized = lexical_normalize(value)
    if isinstance(normalized, bool):
        return ("boolean", normalized)
    if isinstance(normalized, (int, float)):
        return ("number", normalized)
    if isinstance(normalized, str):
        return ("string", normalized)
    if normalized is None:
        return ("null", None)
    return (f"python:{type(normalized).__qualname__}", repr(normalized))
