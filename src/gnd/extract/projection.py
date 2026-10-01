"""The closed, shape-only per-model projection and its recursive allowlist gate.

``project(model)`` turns ``population.schema.json``'s three open maps
(``instances``, ``facts``, and the per-fact role map) into enumerated property
sets derived from the model, and drops every keyword outside the published
allowlist below. The result is what an extractor is handed as a structured-
output schema: it must be able to carry a VIOLATING population faithfully, so
it encodes shape — arity, enumerated ids, scalar-ness — and never a constraint
(D-16, SC4). An extractor structurally unable to emit a violation would make
the round trip score perfectly while measuring nothing.

**The gate is an ALLOWLIST that fails closed, in production code (PANEL-4,
G-2).** A denylist catches the keywords somebody enumerated; the failure mode
this phase is named after is the construct nobody did. ``audit_allowlist``
refuses any keyword outside :data:`_ALLOWED_KEYWORDS` — including vendor
extensions and keywords invented after this file was written — and
``project()`` runs the audit before returning, raising
:class:`ProjectionGateError`. The corpus sweep in
``tests/test_extract_projection.py`` is corroboration, never the gate: P-1
measured a ``uniqueItems`` leak caught by 4 of 451 corpus populations (0.9%),
while the allowlist catches it on every emission.

**Assertions run against the returned dict or the emitted ``.schema.json``
file, never a live API response (P-3).** Anthropic's SDKs document client-side
stripping of unsupported constraints, so a live call succeeding proves nothing
about closure — a leak would be silently removed in flight and reappear in the
committed artifact.
"""

from __future__ import annotations

from typing import Any

__all__ = ["ProjectionGateError", "audit_allowlist", "project"]

#: The published keyword table (PANEL-4, verbatim) — module-level DATA a
#: reviewer diffs against the panel's list, never literals buried in the walk
#: (measure/score.py:187-193's publish-the-table discipline). Everything else
#: fails closed. Value rules enforced by the walk, beyond mere membership:
#: ``additionalProperties`` only literal ``False``; every ``type: object`` node
#: carries it explicitly; ``$schema`` at the root only; ``enum`` only at the
#: two population-header paths (P-7); ``required`` role-arity only.
_ALLOWED_KEYWORDS = frozenset(
    {
        "type",
        "properties",
        "items",
        "$defs",
        "$ref",
        "additionalProperties",
        "required",
        "anyOf",
    }
)

#: The two paths where ``enum`` is interchange-format SHAPE, not a constraint
#: (P-7): the population header's ``source`` and ``label``. Everything below
#: the header is field territory and ``enum`` there is constraint vocabulary.
_ENUM_ALLOWED_SEGS = frozenset(
    {
        ("properties", "population", "properties", "source"),
        ("properties", "population", "properties", "label"),
    }
)

_MISSING = object()


class ProjectionGateError(ValueError):
    """The built projection failed the allowlist audit.

    Raised by :func:`project` itself — in PRODUCTION code, not only a test
    (G-2) — because a leak filed under some existing outcome would flatter
    every downstream number: a constraint keyword that reaches the emitted
    schema silently narrows what the extractor can emit, and every fidelity
    rate computed over its output improves without anyone deciding it should
    (the refuse-never-default register of measure/score.py's CellLookupError).
    """


def _render(segs: tuple[str, ...]) -> str:
    return "$" + "".join(f".{seg}" for seg in segs)


def _expected_required(
    segs: tuple[str, ...], node: dict[str, Any]
) -> list[str] | None:
    """The exact ``required`` list a node at ``segs`` may carry, or ``None``
    when ``required`` is not permitted there at all.

    ``required`` encodes ARITY and nothing else (PANEL-4's scoping): the root
    names its two document sections, the header names its two mandatory
    metadata fields, and a fact-items node names exactly its enclosing role
    set — a binary fact type has two role slots the way a tuple has two slots.
    """
    if segs == ():
        return ["population", "facts"]
    if segs == ("properties", "population"):
        return ["model", "source"]
    if (
        len(segs) == 5
        and segs[:3] == ("properties", "facts", "properties")
        and segs[4] == "items"
    ):
        return [str(name) for name in (node.get("properties") or {})]
    return None


def _audit(
    node: Any, segs: tuple[str, ...], out: list[tuple[str, str, str]]
) -> None:
    if not isinstance(node, dict):
        return
    path = _render(segs)

    for key in node:
        if key == "$schema":
            if segs:
                out.append(
                    (path, "$schema", "'$schema' is permitted at the root path only")
                )
            continue
        if key == "enum":
            if segs not in _ENUM_ALLOWED_SEGS:
                out.append(
                    (
                        path,
                        "enum",
                        (
                            "'enum' below the population header is constraint "
                            "vocabulary; it is permitted ONLY at "
                            "$.properties.population.properties.source and "
                            ".label, where it is interchange-format shape (P-7)"
                        ),
                    )
                )
            continue
        if key not in _ALLOWED_KEYWORDS:
            out.append(
                (
                    path,
                    str(key),
                    (
                        "not on the published _ALLOWED_KEYWORDS table — the "
                        "allowlist fails closed on keywords nobody enumerated "
                        "(PANEL-4)"
                    ),
                )
            )

    additional = node.get("additionalProperties", _MISSING)
    if additional is not _MISSING and additional is not False:
        out.append(
            (
                path,
                "additionalProperties",
                (
                    "must be the literal false — a schema-valued or true "
                    "additionalProperties re-opens the map the projection "
                    "exists to close (D-16)"
                ),
            )
        )
    if node.get("type") == "object" and additional is _MISSING:
        out.append(
            (
                path,
                "additionalProperties",
                (
                    "absent on a type:object node — closure demands an "
                    "explicit false on every object"
                ),
            )
        )

    required = node.get("required")
    if required is not None:
        expected = _expected_required(segs, node)
        if expected is None:
            out.append(
                (
                    path,
                    "required",
                    (
                        "'required' is permitted only at the root, the "
                        "population header, and fact-items nodes (role-arity); "
                        "anywhere else it is a constraint"
                    ),
                )
            )
        elif not isinstance(required, list) or sorted(
            str(name) for name in required
        ) != sorted(expected):
            out.append(
                (
                    path,
                    "required",
                    (
                        f"must be exactly {sorted(expected)} (order-"
                        f"insensitive; role-arity only, PANEL-4) — got "
                        f"{required!r}"
                    ),
                )
            )

    for key, value in node.items():
        if key in ("properties", "$defs") and isinstance(value, dict):
            for name, sub in value.items():
                _audit(sub, (*segs, key, str(name)), out)
        elif key == "items":
            _audit(value, (*segs, "items"), out)
        elif key == "anyOf" and isinstance(value, list):
            for index, sub in enumerate(value):
                _audit(sub, (*segs, f"anyOf[{index}]"), out)


def audit_allowlist(schema: dict[str, Any]) -> list[tuple[str, str, str]]:
    """Every allowlist violation in ``schema`` as ``(json_path, keyword, reason)``.

    A structure-aware walk: the children of ``properties`` and ``$defs`` are
    NAMES (object-type ids, fact-type ids, role names — arbitrary model text),
    not keywords, so only genuine schema nodes are audited. An empty list means
    the schema is inside the published allowlist and its value rules.
    """
    out: list[tuple[str, str, str]] = []
    _audit(schema, (), out)
    return out


def _build_projection(model: Any) -> dict[str, Any]:
    """The closed projection of ``population.schema.json`` for ONE model.

    From the corpus-validated RESEARCH prototype (451/451 violating + boundary
    populations accepted). Closure notes:

    * the three open maps (``instances``, ``facts``, the per-fact role map)
      become enumerated property sets derived from the model;
    * ``$defs/scalar`` is ``anyOf`` of single types, not ``type: [...]`` (A1 —
      the structured-output docs enumerate supported *types* but do not settle
      type-arrays; ``anyOf`` is explicitly supported);
    * the population header keeps its ``source``/``label`` enums — header, not
      field (P-7) — and ``minLength`` from the source schema is dropped;
    * fact items carry ``additionalProperties: false`` plus full-role
      ``required`` (arity, validated to reject none of the 451).
    """
    instance_properties = {
        str(object_type["id"]): {"type": "array", "items": {"$ref": "#/$defs/scalar"}}
        for object_type in model.object_types
    }
    fact_properties: dict[str, Any] = {}
    owned = {ft for declaration in model.reference_populations for ft in declaration["fact_types"]}
    for fact_type in model.fact_types:
        if fact_type["id"] in owned:
            continue
        roles = [str(role["role_name"]) for role in (fact_type.get("roles") or [])]
        fact_properties[str(fact_type["id"])] = {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": roles,
                "properties": {name: {"$ref": "#/$defs/scalar"} for name in roles},
            },
        }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": ["population", "facts"],
        "properties": {
            "population": {
                "type": "object",
                "additionalProperties": False,
                "required": ["model", "source"],
                "properties": {
                    "model": {"type": "string"},
                    "model_id": {"type": "string"},
                    "source": {"enum": ["agent-output", "synthetic", "fixture"]},
                    "label": {"enum": ["conforming", "boundary", "violating"]},
                    "covers": {"type": "array", "items": {"type": "string"}},
                },
            },
            "instances": {
                "type": "object",
                "additionalProperties": False,
                "properties": instance_properties,
            },
            "facts": {
                "type": "object",
                "additionalProperties": False,
                "properties": fact_properties,
            },
        },
        "$defs": {
            "scalar": {
                "anyOf": [
                    {"type": "string"},
                    {"type": "number"},
                    {"type": "boolean"},
                ]
            }
        },
    }


def project(model: Any) -> dict[str, Any]:
    """The audited, closed, shape-only projection for ``model``.

    Builds the projection and runs :func:`audit_allowlist` over it BEFORE
    returning — the gate is this function, not a test. A violation raises
    :class:`ProjectionGateError` naming every offending ``(path, keyword)``,
    because refusing loudly is the only honest option: a default would file
    the leak under "emitted fine" and flatter every downstream fidelity rate.
    """
    from gnd.terms import require_non_temporal

    require_non_temporal(model, "extract")
    schema = _build_projection(model)
    violations = audit_allowlist(schema)
    if violations:
        rendered = "; ".join(
            f"{path}: {keyword} ({reason})" for path, keyword, reason in violations
        )
        raise ProjectionGateError(
            f"the built projection failed the allowlist audit with "
            f"{len(violations)} violation(s) — refusing to emit it (a leaked "
            f"keyword narrows what the extractor can emit and silently "
            f"improves every downstream rate): {rendered}"
        )
    return schema
