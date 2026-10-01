"""Normative ORM scalar identity for synthesis-side code.

This is deliberately independent of :mod:`gnd.checker`: the synthesis oracle
must not call the implementation it evaluates.  It nevertheless implements the
same specified domains: booleans are separate, all JSON numeric renderings
share one domain, strings are separate, and tuples are keyed component-wise.
"""

from __future__ import annotations

from typing import Any


def scalar_identity(value: Any) -> tuple[str, Any]:
    """Return the synthesis identity key for one interchange scalar."""
    if isinstance(value, bool):
        return ("boolean", value)
    if isinstance(value, (int, float)):
        return ("number", value)
    if isinstance(value, str):
        return ("string", value)
    if value is None:
        return ("null", None)
    return (f"python:{type(value).__qualname__}", repr(value))


def tuple_identity(values: tuple[Any, ...]) -> tuple[tuple[str, Any], ...]:
    """Return component-wise ORM identity for a projected tuple."""
    return tuple(scalar_identity(value) for value in values)
