"""The constraint-blind model verbalization — the rendering seed (R-08″).

``render_verbalization`` is constraint-blind BY CONSTRUCTION, not by review:
the builder reads ONLY ``object_types[]`` (id, name, kind, ``reference``,
``subtype_of``, ``inherits_reference``), ``fact_types[]`` (id, ``reading``,
``roles``), primitive shapes via ``popvalidate.resolve_primitive``, and —
solely for the external-mode identification phrase — the composite identity
:func:`gnd.extract.refscheme.reference_identity` derives from top-level
external ``uniqueness`` constraints' ``role_refs``. No other constraint access
exists anywhere in this module: no constraint sentences, no modality words, no
provenance prefixes. The panel's reason is Codex's finding that constraint
verbalizations bias the extractor toward REPAIRING violations — a document
seed that recites "each employee has exactly one salary" teaches the extractor
to emit the population the checker wants rather than the one the document
contains. ``tests/test_extract_vocabulary.py::test_vocabulary_is_constraint_blind``
pins this as byte-identity under constraint injection.

The header is a THIRD header form — mechanical derivation by ``gnd extract`` —
not the CSDP header (which claims a dialogue that never happened) and not the
Phase-4 introspection header ``verbalization-patterns.md:51`` reserves; that
reservation is the precedent for adding a derivation-flavoured form.

Sentence patterns follow ``verbalization-patterns.md`` (object-type modes at
:55-117, the external/composite phrase at :81-89). ``verbalize.py``'s ~55
``*_message`` functions are violation-voice and deliberately NOT imported —
only the neutralization boundary (``_neutralize``/``line_text``) is reused,
because model text (names, readings, units) includes user-supplied fields and
must not forge lines or escape quotes (T-02.1-06).
"""

from __future__ import annotations

import re
from typing import Any

from gnd.extract.refscheme import reference_identity
from gnd.popvalidate import resolve_primitive
from gnd.verbalize import _neutralize, line_text

__all__ = ["reading_text", "render_verbalization"]

#: ``{Employee}`` and ``{Employee:manager}`` reading placeholders.
_PLACEHOLDER = re.compile(r"\{([^{}:]+)(?::([^{}]+))?\}")


def reading_text(reading: Any) -> str:
    """A reading with placeholders instantiated as type names — ``{X}`` becomes
    ``X`` and ``{X:role}`` becomes ``X (role)``.

    Public since plan 03-03: ``gnd.codegen.docstrings`` derives each emitted
    tool's docstring from the same instantiated reading this module renders
    into the verbalization. That is a change of VISIBILITY, not of behaviour —
    a second copy next door would fork the one place a reading turns into
    prose, and the fork would show up as two different sentences for one fact
    type (G-03). Note what it does NOT do: neutralization is the caller's, at
    the caller's emission site, exactly as ``_object_type_sentence`` does it
    here."""

    def replace(match: re.Match[str]) -> str:
        name, role = match.group(1), match.group(2)
        return f"{name} ({role})" if role else name

    return _PLACEHOLDER.sub(replace, str(reading or ""))


def _display(by_id: dict[str, dict[str, Any]], oid: Any) -> str:
    object_type = by_id.get(str(oid)) or {}
    return _neutralize(object_type.get("name") or oid)


def _object_type_sentence(
    object_type: dict[str, Any], by_id: dict[str, dict[str, Any]], model: Any
) -> str:
    oid = str(object_type.get("id"))
    name = _neutralize(object_type.get("name") or oid)

    if object_type.get("kind") == "value":
        primitive = resolve_primitive(oid, model)
        if primitive is not None:
            return f"{name} is a value of type {_neutralize(primitive)}."
        return f"{name} is a value type."

    reference = object_type.get("reference") or {}
    mode = reference.get("mode")
    subtype_of = object_type.get("subtype_of") or []

    if subtype_of and not reference:
        supertypes = " and ".join(_display(by_id, parent) for parent in subtype_of)
        if object_type.get("inherits_reference") is True:
            return (
                f"{name} is a kind of {supertypes}, inheriting the reference "
                f"of {supertypes}."
            )
        return f"{name} is a kind of {supertypes}."

    if mode in ("popular", "general"):
        return f"{name} is identified by {_display(by_id, reference.get('value_type'))}."

    if mode == "unit-based":
        unit = _neutralize(reference.get("unit"))
        measure_type = _neutralize(reference.get("measure_type"))
        return f"{name} is identified by a value in {unit} ({measure_type})."

    if mode == "external":
        # The one sanctioned constraint read (R-08″ scoping): the composite
        # identification phrase derives from external uniqueness role_refs
        # (verbalization-patterns.md:81-89).
        kind, payload = reference_identity(oid, model)
        if kind == "composite":
            parts = " and ".join(
                f"{_neutralize(entry['role'])} (in fact type "
                f"{_neutralize(entry['fact_type'])})"
                for entry in payload
            )
            return f"{name} is identified by the combination of {parts}."
        return (
            f"{name} has an external reference scheme with no anchoring "
            f"external uniqueness constraint."
        )

    return f"{name} is an entity type with no declared reference scheme."


def render_verbalization(model: Any) -> str:
    """The constraint-blind verbalization document for ``model``.

    Sections per ``verbalization-patterns.md``'s document shape, minus every
    constraint-bearing section: a derivation header (the third header form),
    ``=== Object Types ===`` (one reference-scheme sentence per object type),
    and ``=== Fact Types ===`` (each reading with its roles' primitive
    shapes). Every emitted line passes through ``verbalize.line_text`` so
    model-supplied control characters cannot forge line structure.
    """
    by_id = {str(entry.get("id")): entry for entry in model.object_types}

    lines: list[str] = [
        "=== Header ===",
        "Derived mechanically from the ORM model by `gnd extract` (R-08\").",
        "Constraint-blind by specification: object types, reference schemes,",
        "fact-type readings and primitive shapes only — no constraint",
        "sentences, no modality, no provenance. Hand-authoring this file is",
        "banned; regenerate it with `gnd extract MODEL --out DIR`.",
        "",
        "=== Object Types ===",
    ]
    for object_type in model.object_types:
        lines.append(_object_type_sentence(object_type, by_id, model))
    lines.append("")
    lines.append("=== Fact Types ===")
    for fact_type in model.fact_types:
        lines.append(reading_text(fact_type.get("reading")))
        for role in fact_type.get("roles") or []:
            oid = str(role.get("object_type"))
            primitive = resolve_primitive(oid, model)
            suffix = f" ({_neutralize(primitive)})" if primitive is not None else ""
            lines.append(
                f"  - {_neutralize(role.get('role_name'))}: "
                f"{_display(by_id, oid)}{suffix}"
            )
        lines.append("")

    # ORM+ v2 operations, under the SAME blindness rule as everything above:
    # the reading and the parameter phrases, and nothing else. Preconditions,
    # dynamic rules, effects and every frame or obligation modality are
    # withheld, for the reason the module docstring gives — a seed that recites
    # the rules teaches the extractor to emit the population the checker wants
    # rather than the one the document contains, and an operation's obligations
    # are exactly such rules. Emitted only when the model declares operations,
    # so a v1 model renders byte-identically to what it rendered before v2.
    operations = getattr(model, "operations", None) or []
    if operations:
        lines.append("=== Operations ===")
        for operation in operations:
            lines.append(reading_text(operation.get("reading")))
            for parameter in operation.get("parameters") or []:
                oid = str(parameter.get("object_type"))
                primitive = resolve_primitive(oid, model)
                suffix = f" ({_neutralize(primitive)})" if primitive is not None else ""
                lines.append(
                    f"  - {_neutralize(parameter.get('name'))}: "
                    f"{_display(by_id, oid)}{suffix}"
                )
            lines.append("")

    return "\n".join(line_text(line) for line in lines).rstrip("\n") + "\n"
