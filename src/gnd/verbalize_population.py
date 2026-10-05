"""Deterministic, projected sentences for population facts and complete witnesses."""

from __future__ import annotations

import json
import math
import re
from collections.abc import Mapping
from typing import Any

from gnd.anchors import AnchorSidecar, bind_anchors
from gnd.documents import Model
from gnd.errors import PopulationLoadError
from gnd.extensions import identity_token as _identity_token
from gnd.model import _layer1_structural, semantic_validate
from gnd.population import Population, load_population_bytes
from gnd.redaction import INSTANCE_DETAIL, RedactionPolicy, RedactionProjectionError, project_output
from gnd.values import content_digest as _content_digest
from gnd.verbalize import _quote, line_text

_PLACEHOLDER = re.compile(r"\{[^{}]+\}")


class PopulationVerbalizationError(ValueError):
    """An input cannot be represented without inventing a role or reading."""


def validate_model_object(model: Model) -> None:
    """Recheck both loader layers for a possibly mutated in-memory model."""
    if not isinstance(model, Model):
        raise PopulationVerbalizationError("invalid model")
    try:
        if model.version == 1 and model.operations:
            raise PopulationVerbalizationError("invalid model")
        # Pydantic supplies v2-only default fields on a loaded v1 model; they
        # were absent from its valid source document and must not invalidate it.
        excluded = {"warnings", "operations"} if model.version == 1 else {"warnings"}
        if not model.reference_populations:
            excluded.add("reference_populations")
        document = model.model_dump(exclude=excluded, exclude_none=True)
        if _layer1_structural(document) or any(
            issue.severity == "error" for issue in semantic_validate(document)
        ):
            raise PopulationVerbalizationError("invalid model")
    except PopulationVerbalizationError:
        raise
    except Exception as error:
        raise PopulationVerbalizationError("invalid model") from error


def _opaque(value: object) -> bool:
    return isinstance(value, dict) and set(value) == {"$opaque"} and isinstance(value["$opaque"], str)


def _reject_surrogates(value: str) -> None:
    if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
        raise PopulationVerbalizationError("surrogate code point cannot be verbalized")


def _token(value: object) -> bytes:
    if _opaque(value):
        return json.dumps(["opaque-label", value["$opaque"]], ensure_ascii=False, separators=(",", ":")).encode()
    return _identity_token(value)


def _display(value: object) -> str:
    if isinstance(value, dict) and value.get("redacted") is True:
        return _quote(INSTANCE_DETAIL)
    if _opaque(value):
        return _quote(f"[opaque: {value['$opaque']}]")
    return _quote(value)


def _complete_binding(
    fact_type: Mapping[str, Any], binding: Mapping[str, object], *, allow_marker: bool = False,
) -> tuple[str, ...]:
    names = tuple(str(role["role_name"]) for role in fact_type["roles"])
    if set(binding) != set(names):
        raise PopulationVerbalizationError("incomplete binding or unknown role")
    for value in binding.values():
        if isinstance(value, str):
            _reject_surrogates(value)
        elif _opaque(value):
            _reject_surrogates(value["$opaque"])
        if _opaque(value) or (allow_marker and isinstance(value, dict) and value.get("redacted") is True):
            continue
        if type(value) not in (str, bool, int, float) or (isinstance(value, float) and not math.isfinite(value)):
            raise PopulationVerbalizationError("unsupported role value")
    return names


def _sentence(reading: str, fact_type: Mapping[str, Any], binding: Mapping[str, object], *, inverse: bool = False) -> str:
    names = _complete_binding(fact_type, binding, allow_marker=True)
    matches = tuple(_PLACEHOLDER.finditer(reading))
    if inverse and not matches:
        if len(names) != 2:
            raise PopulationVerbalizationError("inverse reading needs a full role template")
        rendered = f"{_display(binding[names[1]])} {line_text(reading)} {_display(binding[names[0]])}"
    else:
        if len(matches) != len(names):
            raise PopulationVerbalizationError("reading does not cover every role")
        parts: list[str] = []
        offset = 0
        used: set[str] = set()
        for index, match in enumerate(matches):
            label, separator, qualifier = match.group()[1:-1].partition(":")
            if inverse and not separator:
                raise PopulationVerbalizationError("inverse template needs explicit role names")
            role = qualifier.strip() if inverse and separator else names[index]
            if role not in binding or role in used or not label.strip():
                raise PopulationVerbalizationError("reading role is ambiguous")
            used.add(role)
            parts.extend((line_text(reading[offset:match.start()]), _display(binding[role])))
            offset = match.end()
        if used != set(names):
            raise PopulationVerbalizationError("reading does not cover every role")
        parts.append(line_text(reading[offset:]))
        rendered = "".join(parts)
    return rendered if rendered.endswith((".", "!", "?")) else rendered + "."


def _anchor_key(fact_type: str, binding: Mapping[str, object]) -> tuple[object, ...]:
    # Match the validated sidecar's complete fact-key identity, retaining types.
    return (fact_type, tuple((name, type(value).__name__, repr(value)) for name, value in sorted(binding.items())))


def _excerpts(sidecar: AnchorSidecar, source: str) -> dict[tuple[object, ...], dict[str, list[str]]]:
    index: dict[tuple[object, ...], dict[str, list[str]]] = {}
    for anchor in sidecar.anchors:
        key = _anchor_key(anchor["fact_key"]["fact_type"], anchor["fact_key"]["roles"])
        role = anchor["role"]
        span = anchor["span"]
        value = source[span["start"]:span["end"]]
        bucket = index.setdefault(key, {}).setdefault(role, [])
        if value not in bucket:
            bucket.append(value)
    return index


def _matches_population_bytes(model: Model, population: Population, raw: bytes | None) -> bool:
    if raw is None:
        return False
    for suffix in (".json", ".yaml"):
        try:
            decoded = load_population_bytes(raw, source=f"bound-population{suffix}", model=model)
        except (PopulationLoadError, ValueError, TypeError, UnicodeError):
            continue
        # Python equality equates 1 with 1.0, yet verbalization prints them
        # differently. The loader's typed content digest preserves that form.
        if _content_digest(decoded) == _content_digest(population):
            return True
    return False


def _project_rows(
    model: Model,
    raw: list[dict[str, Any]],
    *,
    unredacted: bool,
    emitter_id: str,
) -> tuple[dict[str, Any], ...]:
    policy = RedactionPolicy.from_model(model)
    try:
        projected = project_output(
            "population-verbalization", {"rows": raw}, policy=policy,
            mode="unredacted" if unredacted else "applied", emitter_id=emitter_id,
        )
    except RedactionProjectionError:
        raise
    except Exception as error:
        raise RedactionProjectionError("population projection failed") from error
    result: list[dict[str, Any]] = []
    by_id = {str(fact_type["id"]): fact_type for fact_type in model.fact_types}
    for item in projected["rows"]:
        fact_type = by_id[item["fact_ref"]["fact_type"]]
        sentence = _sentence(item["reading"], fact_type, item["roles"], inverse=item["inverse"])
        row = {"fact_ref": item["fact_ref"], "sentence": sentence}
        candidates = item.get("excerpt_candidates") or {}
        labels = [f"{name}: {_quote(value)}" for name in item["role_names"] for value in candidates.get(name, ())]
        if labels:
            row["excerpt"] = "; ".join(labels)
        result.append(row)
    return tuple(result)


def verbalize_population(
    model: Model,
    population: Population,
    *,
    anchors: AnchorSidecar | None = None,
    population_bytes: bytes | None = None,
    document_bytes: bytes | None = None,
    unredacted: bool = False,
    emitter_id: str = "api-population-verbalization",
) -> tuple[dict[str, Any], ...]:
    """Render every occurrence, with source indices preserved after sorting."""
    validate_model_object(model)
    if model.reference_populations:
        from gnd.model import bind_population, resolve_context

        bind_population(model, population, references=resolve_context(model))
    if not population.matches_validation_marker(model):
        raise PopulationVerbalizationError("population is not validated against this model")
    if anchors and not _matches_population_bytes(model, population, population_bytes):
        raise PopulationVerbalizationError("sidecar population bytes differ from the rendered population")
    source = bind_anchors(anchors, model, population_bytes, document_bytes, population) if anchors else None
    anchor_index = _excerpts(anchors, source) if anchors and source is not None else {}
    raw: list[dict[str, Any]] = []
    for fact_type in sorted(model.fact_types, key=lambda fact: str(fact["id"])):
        fact_id = str(fact_type["id"])
        role_names = tuple(str(role["role_name"]) for role in fact_type["roles"])
        for output_label in (fact_id, *role_names, str(fact_type["reading"]), str(fact_type.get("inverse_reading") or "")):
            _reject_surrogates(output_label)
        indexed = list(enumerate(population.facts.get(fact_id, ())))
        for _, binding in indexed:
            _complete_binding(fact_type, binding)
        indexed.sort(key=lambda item: (tuple(_token(item[1][name]) for name in role_names), item[0]))
        inverse = fact_type.get("inverse_reading")
        if inverse and len(role_names) > 2 and not _PLACEHOLDER.search(str(inverse)) and indexed:
            raise PopulationVerbalizationError("inverse reading needs a full role template")
        for index, binding in indexed:
            common = {
                "fact_ref": {"fact_type": fact_id, "index": index},
                "roles": dict(binding),
                "role_names": role_names,
                "excerpt_candidates": anchor_index.get(_anchor_key(fact_id, binding), {}),
            }
            raw.append({**common, "reading": str(fact_type["reading"]), "inverse": False})
            if inverse:
                raw.append({**common, "reading": str(inverse), "inverse": True})
    return _project_rows(model, raw, unredacted=unredacted, emitter_id=emitter_id)


def render_witness(
    model: Model, fact_type_id: str, binding: Mapping[str, object], *, unredacted: bool = False,
) -> str:
    """Render one complete offending-fact binding as a forward sentence."""
    validate_model_object(model)
    fact_type = next((fact for fact in model.fact_types if fact["id"] == fact_type_id), None)
    if fact_type is None or not isinstance(binding, Mapping):
        raise PopulationVerbalizationError("unknown fact type or invalid binding")
    _complete_binding(fact_type, binding)
    from gnd.popvalidate import _PRIMITIVE_PREDICATES
    from gnd.universe import resolve_primitive

    for role in fact_type["roles"]:
        name = str(role["role_name"])
        value = binding[name]
        if _opaque(value):
            if model.version < 2 or not value["$opaque"]:
                raise PopulationVerbalizationError("invalid opaque witness value")
            continue
        primitive = resolve_primitive(str(role["object_type"]), model)
        predicate = _PRIMITIVE_PREDICATES.get(str(primitive))
        if predicate is not None and not predicate(value):
            raise PopulationVerbalizationError("witness role has wrong primitive")
    raw = [{
        "fact_ref": {"fact_type": fact_type_id, "index": 0},
        "roles": dict(binding),
        "role_names": tuple(str(role["role_name"]) for role in fact_type["roles"]),
        "excerpt_candidates": {},
        "reading": str(fact_type["reading"]),
        "inverse": False,
    }]
    return _project_rows(model, raw, unredacted=unredacted, emitter_id="api-population-verbalization")[0]["sentence"]
