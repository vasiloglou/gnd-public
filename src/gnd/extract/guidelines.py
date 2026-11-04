"""The optional extraction guideline file of ``gnd extract --guidelines`` (MG4).

Per fact type: its readings, the fact types that share its role players, and
per role the object type, its description core keys, how an entity is
identified and the primitive. Constraint-blind by construction, like
``gnd.vocabulary.render_verbalization``: no constraint is read except the
external uniqueness that IS an entity's composite reference scheme (through
``gnd.refscheme.entity_reference``), and value constraints are omitted
(MG-D6). The layout is normative in the gnd-extract extraction contract
("Guideline file").

Every model string passes through ``verbalize.neutralize_text`` inside quotes
or backticks, so no description, reading or name can start a line, and a
heading can only come from this generator (IK1-Q4). The file is plain text in
Markdown layout: raw HTML in a description is not escaped, so it is read as
text and never rendered (review R-F5). Model reads go through
``ModelIndex`` only (MG-R6).
"""

from __future__ import annotations

from typing import Any, Final

from gnd.documents import Model
from gnd.model_index import ModelIndex
from gnd.refscheme import entity_reference, fact_type_signatures
from gnd.verbalize import description_lines, line_text, neutralize_text

GUIDELINES_SUFFIX: Final = ".guidelines.md"

_IDENTITY_SENTENCES: Final = {
    "composite": "a combination of roles (composite reference)",
    "unmatchable": "no printable reference value",
}


def _code(value: Any) -> str:
    """An id or role name as inline code that cannot close its backticks."""
    return "`" + neutralize_text(value).replace("`", "\\x60") + "`"


def _quoted(value: Any) -> str:
    return f"'{neutralize_text(value)}'"


def _role_lines(index: ModelIndex, model: Model, role_name: str, object_type_id: str,
                identities: dict[str, tuple[str, str | None]]) -> list[str]:
    object_type = index.object_type(object_type_id) or {}
    kind = object_type.get("kind")
    name = object_type.get("name") or object_type_id
    lines = [
        f"### Role {_code(role_name)}",
        "",
        f"- Object type: {_quoted(name)} ({_code(object_type_id)}), {neutralize_text(kind)}",
    ]
    lines.extend(f"- {label}: '{text}'" for label, text in description_lines(object_type.get("description")))
    if kind == "entity":
        # Once per entity, not per role (review R-F6): reference_identity walks
        # the model's constraints, and a large model repeats its entities.
        if object_type_id not in identities:
            identities[object_type_id] = entity_reference(object_type_id, model)
        identity, value_type = identities[object_type_id]
        sentence = (
            f"the value of {_code(value_type)}" if identity == "direct" else _IDENTITY_SENTENCES[identity]
        )
        lines.append(f"- Identified by: {sentence}")
    primitive = index.primitive(object_type_id, variant="truthy")
    if primitive is not None:
        lines.append(f"- Primitive: {neutralize_text(primitive)}")
    lines.append("")
    return lines


def render_guidelines(model: Model) -> str:
    """The guideline file for one loaded model; deterministic bytes."""

    index = ModelIndex.for_model(model)
    signatures = fact_type_signatures(index)
    shared: dict[tuple[str, ...], list[str]] = {}
    for fact_type_id, signature in signatures.items():
        shared.setdefault(signature, []).append(fact_type_id)
    role_players = index.role_object_types()
    identities: dict[str, tuple[str, str | None]] = {}
    lines = [
        "# Extraction guidelines",
        "",
        "Derived mechanically from the ORM model by `gnd extract --guidelines`.",
        "Constraint-blind: readings, role players, object-type descriptions,",
        "reference modes and primitives only. A description is the modeller's",
        "prose and can restate a rule; it is guidance about meaning, never a rule",
        "to enforce. Extract what the document says, even when it breaks a rule.",
        "",
    ]
    for fact_type in index.iter_fact_types_shared():
        fact_type_id = str(fact_type.get("id"))
        lines.extend([f"## Fact type {_code(fact_type_id)}", ""])
        lines.append(f"- Reading: {_quoted(fact_type.get('reading'))}")
        inverse = fact_type.get("inverse_reading")
        if isinstance(inverse, str) and inverse:
            lines.append(f"- Inverse reading: {_quoted(inverse)}")
        others = [other for other in shared.get(signatures.get(fact_type_id, ()), []) if other != fact_type_id]
        if others:
            lines.append(f"- Same role players as: {', '.join(_code(other) for other in sorted(others))}")
        lines.append("")
        for role_name, object_type_id in role_players.get(fact_type_id, {}).items():
            lines.extend(_role_lines(index, model, role_name, object_type_id, identities))
    return "\n".join(line_text(line) for line in lines).rstrip("\n") + "\n"


__all__ = ["GUIDELINES_SUFFIX", "render_guidelines"]
