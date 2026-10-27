"""Tool docstrings DERIVED from the model — the escape from the mixed file.

**The decision this module discharges.** G-05's consequence list puts "tool
docstrings" among the things the codegen *skill* authors. Taken literally that
makes ``tools.py`` a MIXED file: signatures that must be digest-gated and
AST-checked sitting beside prose that is user-owned and, being LLM-authored, not
byte-reproducible. File-level ownership (G-04) then fails on the one file that
matters most, and the documented fallback — in-file sentinel merge regions — is
the on-ramp to the round-trip engineering ``REQUIREMENTS.md`` line 70 puts
permanently out of scope.

The escape was already in the tree. ``gnd.extract.vocabulary.reading_text``
instantiates a fact type's ``reading`` into prose, and that prose is a perfectly
good docstring. So docstrings are DERIVED, the skill does not author them,
``tools.py`` stays 100% derived, and no sentinel is needed. This corrects
G-05's consequence LIST; G-05 itself stands unchanged.

**Neutralization happens HERE, at the emission site.** ``vocabulary.py:38``
imports ``verbalize._neutralize`` for the same reason and this module follows
it: model text (names, readings, units) includes user-supplied fields, and a
crafted ``reading`` reaching rendered prose is a named threat (T-02.1-06, and
T-03-13 in this phase's register). Neutralization is never assumed of the model
— ``gnd validate`` types ``reading`` as a plain string and deliberately does not
interpret it.

**The delimiter choice IS half the mitigation, so it is stated rather than
left to the emitter.** Emitted docstrings use ``'''``. ``_neutralize`` escapes
every backslash and every single quote and turns newlines, carriage returns,
C0/C1 controls and the Unicode line/paragraph separators into escape sequences —
so no ``'''`` run and no forged line can survive it. It does NOT escape the
double quote, which is harmless inside a ``'''`` literal and would be an escape
hatch inside a ``\"\"\"`` one. Emitting with ``\"\"\"`` while neutralizing with
the shipped function would be a boundary that cannot hold; emitting with
``'''`` makes the shipped function sufficient, with nothing added on top and
therefore nothing to drift.
"""

from __future__ import annotations

from typing import Any

from gnd.extract.vocabulary import reading_text
from gnd.popvalidate import resolve_primitive
from gnd.verbalize import _neutralize, neutralize_text

__all__ = ["DOCSTRING_DELIMITER", "docstring_open", "tool_docstring"]

#: The delimiter emitted tool docstrings are written with. Published as DATA
#: because it is load-bearing security, not formatting: see the module
#: docstring — ``_neutralize`` escapes ``'`` and not ``"``, so this delimiter is
#: what makes the shipped neutralizer a sufficient boundary. Changing it to
#: ``\"\"\"`` reopens the injection this module exists to close.
DOCSTRING_DELIMITER = "'''"


def docstring_open(body: str) -> str:
    """The opening of an emitted docstring whose neutralized body is ``body``.

    Raw exactly when the body holds an escape other than ``\\\\`` and ``\\'``.
    A non-raw literal would decode the neutralizer's ``\\n`` back into a
    newline, so the runtime ``__doc__`` could carry a forged line that the
    source text does not (IK1-Q4). The two escapes the neutralizer writes for a
    backslash and a quote decode to those characters and cannot change a line,
    so a reading such as "Employee's" keeps its bytes and its runtime text.
    Inside the raw literal ``\\'`` stays two characters and cannot close it.
    """
    index = 0
    while index < len(body):
        if body[index] == "\\":
            if body[index + 1:index + 2] not in ("\\", "'"):
                return "r" + DOCSTRING_DELIMITER
            index += 1
        index += 1
    return DOCSTRING_DELIMITER


def _display_name(model: Any, object_type_id: Any) -> str:
    """The object type's display name, neutralized."""
    oid = str(object_type_id)
    for entry in model.object_types:
        if str(entry.get("id")) == oid:
            return _neutralize(entry.get("name") or oid)
    return _neutralize(oid)


def _summary_suffix(model: Any, object_type_id: Any) -> str:
    """`` — <summary>`` for an object type whose description has one, else empty.

    Only ``summary`` is rendered, so a docstring keeps one line per role; the
    other core keys and every extra stay out of code (IK1). The summary is
    escaped by ``neutralize_text`` and never truncated -- it escapes ``'``
    exactly as ``_neutralize`` does, so the delimiter rule above still holds.
    """
    oid = str(object_type_id)
    for entry in model.object_types:
        if str(entry.get("id")) == oid:
            description = entry.get("description")
            if isinstance(description, dict) and "summary" in description:
                return f" — {neutralize_text(description['summary'])}"
            return ""
    return ""


def tool_docstring(model: Any, fact_type: dict[str, Any]) -> str:
    """The derived docstring body for ``fact_type``'s emitted tool.

    Four structural parts, in this order — the instantiated reading, a blank
    line, the derivation provenance, and one line per role in DECLARED order
    carrying its object type and primitive shape:

    .. code-block:: text

        Employee has EmployeeName

        Derived from fact type 'employee_has_name'. Roles, in declared order:
          - employee: Employee
          - name: EmployeeName (String)

    Every model-supplied fragment passes through ``_neutralize`` first, so the
    line structure above is the emitter's and can never be the model's. The
    returned text carries no trailing newline and no indentation: the emitter
    owns layout, this function owns content.

    A fact type with no ``reading`` gets its id as the first line rather than an
    empty one — an undocumented tool would make the emitted surface less
    reviewable exactly where the model was already thinnest.
    """
    fact_id = str(fact_type.get("id"))
    headline = _neutralize(reading_text(fact_type.get("reading"))).strip()
    if not headline:
        headline = f"Fact type {_neutralize(fact_id)}."

    lines = [
        headline,
        "",
        (
            f"Derived from fact type '{_neutralize(fact_id)}'. Roles, in "
            f"declared order:"
        ),
    ]
    for role in fact_type.get("roles") or []:
        oid = role.get("object_type")
        primitive = resolve_primitive(str(oid), model)
        suffix = f" ({_neutralize(primitive)})" if primitive is not None else ""
        lines.append(
            f"  - {_neutralize(role.get('role_name'))}: "
            f"{_display_name(model, oid)}{suffix}{_summary_suffix(model, oid)}"
        )
    return "\n".join(lines)
