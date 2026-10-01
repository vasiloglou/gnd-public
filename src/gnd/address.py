"""Canonical production and parsing of GND model-element addresses.

Declared model elements use a class-qualified identifier. Constraints that do
not declare an identifier retain the positional references emitted by the
checker since v1.0; those references are intentionally recognizable as the
legacy, unstable form.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

ElementClass = Literal["operation", "fact_type", "constraint", "derivation"]
Addressing = Literal["declared-id", "positional"]


@dataclass(frozen=True)
class Address:
    """One parsed element address."""

    text: str
    element_class: ElementClass
    addressing: Addressing
    identifier: str | None = None
    fact_type_id: str | None = None
    index: int | None = None


_INLINE_CONSTRAINT = re.compile(
    r"fact_types\[(?P<fact_type>[^\[\]]+)\]\.constraints\[(?P<index>[0-9]+)\]"
)
_TOP_LEVEL_CONSTRAINT = re.compile(r"constraints\[(?P<index>[0-9]+)\]")


def operation_address(op_id: str) -> str:
    """Return the declared-id address for an operation."""

    return f"operation:{op_id}"


def fact_type_address(ft_id: str) -> str:
    """Return the declared-id address for a fact type."""

    return f"fact_type:{ft_id}"


def constraint_address(constraint_id: str) -> str:
    """Return the declared-id address for a constraint."""

    return f"constraint:{constraint_id}"


def derivation_address(fact_type_id: str) -> str:
    """Return the address for one derivation obligation (v5.0 r2 R2).

    Deliberately DISTINCT from :func:`fact_type_address` over the same id: one
    fact type, two obligations, two addresses. Parsed by :func:`parse_address`
    and counted by ``gnd coverage`` since Phase 3 (T3.6).
    """

    return f"derivation:{fact_type_id}"


def positional_constraint_ref(fact_type_id: str | None, index: int) -> str:
    """Return the legacy positional constraint reference emitted since v1.0."""

    if fact_type_id is None:
        return f"constraints[{index}]"
    return f"fact_types[{fact_type_id}].constraints[{index}]"


def _parse_index(text: str) -> int | None:
    """Convert an ASCII digit run without leaking Python's integer cap error."""

    if len(text) > 32:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def parse_address(text: str) -> Address | None:
    """Parse ``text`` as an element address; return ``None`` for anything else.

    This function is total over arbitrary :class:`str`: malformed and hostile
    strings are ordinary non-addresses and never raise.
    """

    for prefix, element_class in (
        ("operation:", "operation"),
        ("fact_type:", "fact_type"),
        ("constraint:", "constraint"),
        ("derivation:", "derivation"),
    ):
        if text.startswith(prefix):
            identifier = text[len(prefix) :]
            if not identifier or identifier.strip() != identifier:
                return None
            return Address(text, element_class, "declared-id", identifier=identifier)

    inline = _INLINE_CONSTRAINT.fullmatch(text)
    if inline is not None:
        index = _parse_index(inline.group("index"))
        if index is None:
            return None
        return Address(
            text,
            "constraint",
            "positional",
            fact_type_id=inline.group("fact_type"),
            index=index,
        )

    top_level = _TOP_LEVEL_CONSTRAINT.fullmatch(text)
    if top_level is not None:
        index = _parse_index(top_level.group("index"))
        if index is None:
            return None
        return Address(text, "constraint", "positional", index=index)
    return None
