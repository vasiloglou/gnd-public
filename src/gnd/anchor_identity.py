"""RF3 shared dependency home; algorithms retain predecessor semantics."""
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


ANCHOR_TRANSLATION = _ANCHOR_TRANSLATION

anchor_normalize.__module__ = 'gnd.extract.identity'

lexical_normalize.__module__ = 'gnd.extract.identity'

identity_key.__module__ = 'gnd.extract.identity'
