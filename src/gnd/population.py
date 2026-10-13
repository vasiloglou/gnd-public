"""Population loading — the ONE shared code path (D-11).

Agent outputs, synthetic data, and eval fixtures all load through
:func:`load_population`. A ``.json`` suffix parses via stdlib ``json``; anything
else parses via ruamel ``YAML(typ="safe")``. Both frontends feed the same
dict-to-:class:`Population` construction path, so YAML and JSON renderings of
the same content load identically — and, since WR-04, are REJECTED identically
too: ``json.load``'s defaults silently kept the last of two duplicate keys and
accepted the non-standard literals ``NaN``/``Infinity``/``-Infinity``, so
documents ruamel rejected at exit 3 loaded at exit 0 as JSON. Parity is a
property of the exit code, not of the exception type; the two front ends reject
through different mechanisms and that is fine.

Validation has the same two layers as the model loader (D-01):

Layer 1: the D-10 population schema (``src/gnd/schema/population.schema.json``),
checked BEFORE Pydantic construction using the same
``Draft202012Validator``/``json_path`` idiom as the model loader and the same
unified :class:`~gnd.model.ValidationIssue` record shape. Syntax only — it
cannot know which fact types or roles a model declares.
Layer 2 (CORE-04): model-relative structural conformance, run only when a
``model`` is supplied — see :func:`load_population` and :mod:`gnd.popvalidate`.

Security notes:
- 10 MB file-size cap before parsing (agent-output populations are untrusted;
  mitigates T-01-02).
- YAML anchors/aliases are rejected via a parse-event pre-scan before any node
  construction: the byte cap alone does not bound alias amplification (a
  well-under-cap billion-laughs document expands to memory exhaustion during
  load). Aliases are a YAML-only construct, so rejecting them also preserves
  D-11 YAML/JSON parity.
- The ``population.model`` header field is declarative metadata only — this
  loader never opens the referenced path (mitigates T-01-05); the checker takes
  the model object from the caller.
"""

from __future__ import annotations

import hashlib  # noqa: F401 -- compatibility export
import io
import json  # noqa: F401 -- historical compatibility binding
from importlib.resources import files
from pathlib import Path
from typing import Any, Literal

from jsonschema import Draft202012Validator
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr
from ruamel.yaml import YAML

from gnd import input_policy as _rf7_input
from gnd.documents import MAX_YAML_EVENTS, Model
from gnd.errors import (
    MAX_SUMMARY_ISSUES,  # noqa: F401 -- compatibility export
    PopulationLoadError,
    PopulationValidationError,
    ValidationIssue,
)
from gnd.popvalidate import population_validate
from gnd.values import MODEL_DIGEST_EXCLUDED_FIELDS  # noqa: F401 -- compatibility export
from gnd.values import (
    content_digest as _content_digest,
)
from gnd.values import model_digest as _model_digest
from gnd.yaml_comments import configure_comment_scanner

_ORIGINAL_DRAFT_VALIDATOR = Draft202012Validator

MAX_POPULATION_BYTES = 10 * 1024 * 1024  # 10 MB


#: How many issues the exception's SUMMARY STRING names (WR-01). Deliberately
#: much smaller than ``report.MAX_POPULATION_ISSUES``: the structured
#: ``issues`` list is what every caller in this repo reads, and the summary is a
#: human-readable fallback for a stray ``str(error)``. Building an unbounded one
#: was ~100 MB of throwaway work per hostile population, since neither
#: ``_cmd_check`` arm ever reads it.


class Population(BaseModel):
    """A loaded population: facts keyed by fact-type id, facts keyed by role_name.

    Carries the D-02 proof that model-relative (layer-2) validation ran — against
    WHICH model (:attr:`validated_against`) and over WHICH CONTENT
    (``_validated_digest``). Both halves are private attributes, so they are
    invisible to ``model_dump()`` (they never round-trip into a serialized
    population file) and cannot be supplied through the public constructor (a
    ``_validated_against=`` kwarg is silently ignored). They are set on exactly
    one code path: the success path of ``load_population(..., model=...)``.

    **The marker attests to content, not merely to an object (CR-01).** An
    earlier version stored only the model reference, so a population could be
    loaded cleanly and then mutated — ``population.facts = {...}``,
    ``population.facts["ft"].append(...)`` or
    ``model_copy(update={"facts": ...})`` — and the mutated object still
    satisfied ``validated_against is model``. Dropping a covered role that way
    restored CONTEXT.md probe #1 verbatim: ``pass=2 fail=0 warning=0 unchecked=0
    vacuous=0`` at exit 0, with "— satisfied" over facts layer 2 never saw. That
    is exactly the workflow Phase 2 DATA-01 (load conforming, inject violation,
    re-check) performs, which is why a guard that only runs when a caller
    remembers to re-validate is not enough.

    Two mechanisms, in this order:

    1. ``model_config = ConfigDict(frozen=True)`` makes the *common* mutation —
       plain attribute assignment — an immediate ``ValidationError`` rather than
       a silent pass.
    2. ``_validated_digest`` is the load-bearing half, because ``frozen=True``
       leaves the nested containers mutable (``facts["ft"].append(...)``) and
       ``model_copy(update=...)`` preserves private attributes while replacing
       fields. :meth:`matches_validation_marker` re-derives the digest from the
       CURRENT content, so any mutation by any route invalidates it.

    ``model_copy()`` preserves the marker (identical content ⇒ identical
    digest); ``model_copy(deep=True)`` deep-copies the referenced
    :class:`~gnd.model.Model`, so ``is`` no longer holds and
    :func:`gnd.checker.check` refuses the copy. That fails **closed**, which is
    the desired direction — re-load or re-validate rather than trying to defeat
    it.
    """

    model_config = ConfigDict(frozen=True)

    format_version: Literal[1, 2] = Field(default=1, exclude=True)
    model: str
    #: D-06: the ``model_id`` the population's author believed they were writing
    #: against, restated from the model's own top-level field. Optional, opaque,
    #: never dereferenced — see :func:`gnd.popvalidate._rule_model_id`.
    model_id: str | None = None
    source: Literal["agent-output", "synthetic", "fixture"]
    label: Literal["conforming", "boundary", "violating"] | None = None
    covers: list[str] = Field(default_factory=list)
    instances: dict[str, list[Any]] = Field(default_factory=dict)
    facts: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)
    #: Warning-severity layer-2 issues. Public and user-facing (unlike the
    #: marker): they belong in the JSON payload, exactly as ``Model.warnings``
    #: does for the model loader.
    warnings: list[ValidationIssue] = Field(default_factory=list)

    #: Deliberately NOT named with a ``model_`` prefix — that collides with
    #: Pydantic's protected namespace and emits a UserWarning.
    _reference_combined: bool = PrivateAttr(default=False)
    _reference_context: object = PrivateAttr(default=None)
    _validated_against: Model | None = PrivateAttr(default=None)
    #: The content digest at the moment layer 2 passed (CR-01). ``None`` when
    #: layer 2 never ran, so an unstamped population fails the check on both
    #: halves rather than on a digest that happens to compare equal.
    _validated_digest: str | None = PrivateAttr(default=None)
    #: Digest of the validation-relevant model content at the moment layer 2
    #: passed. Model identity alone cannot detect mutations to nested fields.
    _validated_model_digest: str | None = PrivateAttr(default=None)

    @property
    def validated_against(self) -> Model | None:
        """The :class:`~gnd.model.Model` OBJECT this population passed layer-2
        validation against, or ``None`` when layer 2 never ran.

        The object, not an id string: the meta-schema has no top-level identity
        field today, so a string marker would be ``None`` for every existing
        model and the guarantee would evaporate exactly where it is needed.
        Object identity needs no schema support.

        This answers "which model", NOT "is this population still the one that
        was validated" — the second question is :meth:`matches_validation_marker`,
        and it is the one :func:`gnd.checker.check` must ask (CR-01).
        """
        return self._validated_against

    def matches_validation_marker(self, model: Model) -> bool:
        """Whether THIS content passed layer 2 against THIS model object (D-02).

        The complete precondition :func:`gnd.checker.check` enforces. Both
        halves are required and neither is sufficient:

        - ``validated_against is model`` — identity, never equality (two
          independent ``load_model()`` calls on one file compare equal, and
          accepting that would let a population validated against one model be
          checked against a different-but-identical one).
        - the digest re-derived from the current field values equals the one
          recorded when layer 2 passed — so any mutation after the load, by any
          route, invalidates the marker (CR-01).
        """
        if (
            self._validated_against is not model
            or self._validated_digest is None
            or self._validated_model_digest is None
        ):
            return False
        return (
            self._validated_digest == _content_digest(self)
            and self._validated_model_digest == _model_digest(model)
        )


#: Model fields this digest deliberately does NOT cover, each for its own
#: reason. Named rather than inlined because ``representation-format.md`` states
#: the coverage normatively and a reader has to be able to find the code that
#: implements it.
#:
#: ``warnings`` — validation OUTPUT, written onto the model after layer 2 ran;
#: no checker verdict depends on it.
#:
#: ``operations`` — ORM+ v2 state transitions, which default snapshot checking ignores
#: (representation-format.md, "Default snapshot mode ignores operations"). This
#: digest's contract is "everything layer 2 validated and THE CHECKER READS", so
#: a section outside default checking does not belong in it. Explicit compiled
#: snapshot checking reads operations separately without changing this digest. Two
#: consequences, both intended: a v1 model's digest is byte-identical to what it
#: was before v2 existed, and editing an operation does not invalidate a
#: population that was never checked against it. The claim a TRANSITION run
#: needs — that the steps were authored against these operations — is a
#: different claim over different bytes, and Phase 2's ``steps.json`` carries its
#: own ``operations_digest`` for it rather than overloading this one.


def _stamp_validated_against(population: Population, model: Model) -> None:
    """Record that ``population`` passed layer 2 against ``model`` (D-02).

    The ONE setter. ``load_population`` calls it on its success path, and
    ``tests/conftest.py::make_population`` calls the same function so that
    directly-constructed test populations travel one code path rather than
    two. Private by name because it is not a supported bypass: it stamps the
    marker without running layer 2, which is only ever correct for a checker
    test that deliberately constructs a shape layer 2 would reject.

    Stamps BOTH halves. Setting only ``_validated_against`` is the CR-01 defect:
    it attests to a model, not to the content that was validated.
    """
    population._validated_against = model
    population._validated_digest = _content_digest(population)
    population._validated_model_digest = _model_digest(model)


def _load_population_schema() -> dict[str, Any]:
    schema_text = (
        files("gnd").joinpath("schema/population.schema.json").read_text(encoding="utf-8")
    )
    return _rf7_input.loads(schema_text)


def _prepared_population_schema(schema: Any) -> Any:
    """Expand the bundled schema's finite local refs, or retain the original.

    Only schema positions are traversed; enum/const/annotation values remain
    literals. Unknown resource/ref structures use the ordinary resolver. This
    prepares the same validator, never a population or validation marker.
    """
    if not isinstance(schema, dict):
        return schema
    definitions = schema.get("$defs")
    if (
        schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("$id") != "https://gnd.dev/schema/population.schema.json"
        or not isinstance(definitions, dict)
        or set(definitions) != {"scalar", "opaque_marker", "fact_value"}
    ):
        return schema
    work = [0]
    maps = {"properties", "$defs"}
    sequences = {"anyOf", "allOf"}
    children = {"items", "additionalProperties", "if", "else"}
    literals = {"type", "required", "enum", "const", "title", "description", "minLength"}

    def expand(node: Any, active: tuple[str, ...], depth: int) -> Any:
        work[0] += 1
        if depth > 48 or work[0] > 4096:
            raise ValueError("population schema preparation bound")
        if isinstance(node, bool):
            return node
        if not isinstance(node, dict):
            raise TypeError("unsupported schema node")
        if "$ref" in node:
            reference = node["$ref"]
            if (
                len(node) != 1
                or not isinstance(reference, str)
                or not reference.startswith("#/$defs/")
            ):
                raise ValueError("unsupported schema reference")
            name = reference.removeprefix("#/$defs/")
            if name not in definitions or name in active:
                raise ValueError("unknown or recursive schema reference")
            return expand(definitions[name], (*active, name), depth + 1)
        result = {}
        for key, value in node.items():
            if depth == 0 and key in {"$schema", "$id"}:
                result[key] = value
            elif key in maps:
                if not isinstance(value, dict):
                    raise ValueError("unsupported schema map")
                result[key] = {name: expand(child, active, depth + 1)
                               for name, child in value.items()}
            elif key in sequences:
                if not isinstance(value, list):
                    raise ValueError("unsupported schema sequence")
                result[key] = [expand(child, active, depth + 1) for child in value]
            elif key in children:
                result[key] = expand(value, active, depth + 1)
            elif key in literals:
                result[key] = value
            else:
                raise ValueError("unsupported schema keyword or nested resource")
        return result

    try:
        return expand(schema, (), 0)
    except (TypeError, ValueError):
        return schema


def _schema_issues(doc: Any) -> list[ValidationIssue]:
    schema = _prepared_population_schema(_load_population_schema())
    if Draft202012Validator is _ORIGINAL_DRAFT_VALIDATOR:
        from gnd.population_shape import accepts_shape

        if accepts_shape(doc, schema):
            return []
    validator = Draft202012Validator(schema)
    return [
        ValidationIssue(
            path=error.json_path,
            message=error.message,
            rule_id=f"jsonschema:{error.validator}",
        )
        for error in sorted(validator.iter_errors(doc), key=lambda e: e.json_path)
    ]


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """WR-04: ``json.load`` keeps the LAST of two duplicate keys, silently.

    ruamel rejects a duplicate mapping key outright, so without this hook the two
    front ends produced OPPOSITE outcomes for logically identical documents:

    ``{"movie": 1, "title": "A", "movie": 2}`` in a ``.json`` population loaded
    as ``{"movie": 2, "title": "A"}`` and exited 0, while the same fact written
    in YAML exited 3 with "found duplicate key". An agent emitting a duplicated
    role in JSON had one of its two values silently discarded, with no issue and
    no warning — and was told its output was accepted.

    That falsifies the module docstring's claim that "YAML and JSON renderings of
    the same content load identically", which ``popvalidate._is_number``'s
    comment also invokes as a design constraint ("D-11 YAML/JSON parity"). Parity
    is checked here rather than in layer 2 because by the time a dict exists the
    duplicate is already gone: only the parser sees both values.
    """
    seen: dict[str, Any] = {}
    for key, value in pairs:
        if key in seen:
            raise PopulationLoadError(
                f"duplicate key {key!r} in population JSON — a fact fills each of "
                f"its roles exactly once, and the YAML front end rejects the same "
                f"document (D-11 parity). Keeping the last occurrence, as "
                f"json.load does by default, would silently discard the other "
                f"value."
            )
        seen[key] = value
    return seen


def _reject_json_constant(name: str) -> Any:
    """WR-04 / CR-04: ``json.load``'s default ``parse_constant`` accepts the
    non-standard literals ``NaN``, ``Infinity`` and ``-Infinity``.

    RFC 8259 §6 permits none of them, and a NaN that got through satisfied every
    alethic range constraint (``nan < min`` and ``nan > max`` are both false) and
    then poisoned the ``--format json`` payload with a token no strict reader
    accepts. Rejected at the front end so the document never enters the shared
    dict-to-``Population`` path.
    """
    raise PopulationLoadError(
        f"population JSON contains the non-standard literal {name} — RFC 8259 "
        f"§6 permits no NaN or Infinity, and IEEE 754 makes every ordered "
        f"comparison involving NaN unordered, so such a value cannot be checked "
        f"against any range constraint."
    )


def _parse_document_bytes(data: bytes, *, suffix: str, source: str) -> Any:
    text = data.decode("utf-8")
    if suffix == ".json":
        with io.StringIO(text) as handle:
            # WR-04 / CR-04: both hooks exist to keep the JSON front end from
            # ACCEPTING what the YAML front end rejects. D-11 parity is a design
            # constraint, not an aspiration — the two renderings of one document
            # must produce the same exit code.
            #
            # The third divergence WR-04 names — the YAML arm's MAX_YAML_EVENTS
            # budget, which the JSON arm lacks — is deliberately NOT mirrored.
            # MAX_YAML_EVENTS exists because YAML aliases amplify: a well-under-
            # cap document expands to memory exhaustion during load. JSON has no
            # alias construct, so its only unbounded shape is nesting depth, and
            # CPython's decoder already fails that closed: 200 000 nested arrays
            # raise RecursionError, which the CLI's load arm maps to exit 3 with
            # a message. Adding a second counter would be a disagreeing cap for
            # a hazard that is already bounded.
            try:
                return _rf7_input.load(
                    handle,
                    object_pairs_hook=_reject_duplicate_json_keys,
                    parse_constant=_reject_json_constant,
                )
            except ValueError as error:
                # CPython refuses overlong integer tokens before schema validation.
                raise PopulationLoadError("population JSON contains an invalid number") from error
    # WR-05 (T-01-02): the size cap does not bound YAML alias amplification —
    # pre-scan the event stream and reject aliases before any node is built.
    from ruamel.yaml.events import AliasEvent

    yaml = configure_comment_scanner(YAML(typ="safe"))
    for count, event in enumerate(yaml.parse(text), start=1):
        if count > MAX_YAML_EVENTS:
            raise PopulationLoadError(
                f"YAML document '{source}' exceeds the {MAX_YAML_EVENTS} "
                "parse-event budget for untrusted input"
            )
        if isinstance(event, AliasEvent):
            raise PopulationLoadError(
                f"YAML document '{source}' uses an anchor/alias ('*{event.anchor}') "
                "— aliases are rejected for untrusted input"
            )
    return yaml.load(text)


def _build_population(
    doc: Any, *, model: Model | None, deduplicate_shape_rows: bool = False
) -> Population:
    shape = doc
    if deduplicate_shape_rows and isinstance(doc, dict) and isinstance(doc.get("facts"), dict):
        facts = {}
        for fact_type, rows in doc["facts"].items():
            if not isinstance(rows, list):
                facts[fact_type] = rows
                continue
            unique = {}
            for row in rows:
                unique.setdefault(repr(row), row)
            facts[fact_type] = list(unique.values())
        shape = {**doc, "facts": facts}
    issues = _schema_issues(shape)
    if issues:
        raise PopulationValidationError(issues)

    warnings: list[ValidationIssue] = []
    if model is not None:
        issues = population_validate(doc, model)
        warnings = [issue for issue in issues if issue.severity == "warning"]
        errors = [issue for issue in issues if issue.severity == "error"]
        if errors:
            raise PopulationValidationError(errors, warnings)

    header = doc["population"]
    population = Population(
        format_version=doc.get("format_version", 1),
        model=header["model"],
        model_id=header.get("model_id"),
        source=header["source"],
        label=header.get("label"),
        covers=list(header.get("covers") or []),
        instances={k: list(v) for k, v in (doc.get("instances") or {}).items()},
        facts={k: [dict(f) for f in v] for k, v in (doc.get("facts") or {}).items()},
        warnings=warnings,
    )
    if model is not None:
        _stamp_validated_against(population, model)
    return population


def _combine_validated_populations(
    model: Model, inputs: tuple[Population, ...], document: dict[str, Any]
) -> Population:
    """Validate the union of already shape-validated, model-bound inputs.

    The reference binder constructs the document from these validated values;
    model-relative validation still runs on the complete combined universe.
    """
    if not inputs or any(not pop.matches_validation_marker(model) for pop in inputs):
        raise PopulationLoadError("combined input is not validated against this model")
    issues = population_validate(document, model)
    errors = [issue for issue in issues if issue.severity == "error"]
    warnings = [issue for issue in issues if issue.severity == "warning"]
    if errors:
        raise PopulationValidationError(errors, warnings)
    header = document["population"]
    result = Population(
        format_version=document["format_version"],
        model=header["model"],
        model_id=header.get("model_id"),
        source=header["source"],
        covers=header["covers"],
        instances=document["instances"],
        facts=document["facts"],
        warnings=warnings,
    )
    _stamp_validated_against(result, model)
    return result


def load_population_bytes(
    data: bytes,
    *,
    source: str | Path,
    model: Model | None = None,
) -> Population:
    """Load already-opened population bytes through the normal validation path."""
    if len(data) > MAX_POPULATION_BYTES:
        raise PopulationLoadError(
            f"population file '{source}' is {len(data)} bytes, exceeding the "
            f"{MAX_POPULATION_BYTES}-byte cap for untrusted population input"
        )
    source_path = Path(source)
    doc = _parse_document_bytes(data, suffix=source_path.suffix, source=str(source))
    return _build_population(doc, model=model)


def load_population(path: str | Path, *, model: Model | None = None) -> Population:
    """Load a population file (YAML or JSON) through the single shared code path.

    Raises :class:`PopulationValidationError` (a :class:`PopulationLoadError`)
    with pointed ``json_path`` issues when the document violates the D-10 schema
    (layer 1) or, when ``model`` is supplied, when it does not conform
    structurally to that model (layer 2, CORE-04 — see :mod:`gnd.popvalidate`).
    Raises :class:`PopulationLoadError` when the file exceeds the size cap or
    trips the YAML alias/event guard (WR-05, T-01-02).
    Warning-severity layer-2 issues never abort the load; they are returned on
    ``Population.warnings``, mirroring ``Model.warnings``.

    ``model`` is optional by design (D-02 explicitly rejected making it
    required): loading a population before a model is resolved is legitimate.
    Skipping layer 2 is nonetheless not a way to skip the *check*: the success
    path stamps the population with the model object it was validated against,
    and :func:`gnd.checker.check` refuses any population that is not stamped for
    the very model it is being checked with. There is deliberately no bypass
    (D-18).

    Layer ordering is load-bearing (T-01.1-05): the 10 MB size cap and the YAML
    alias pre-scan run FIRST, layer 1 next, layer 2 last. Layer 2 must never be
    the reason a billion-laughs document gets parsed. The ``population.model``
    header remains declarative metadata that this loader never opens (T-01-05);
    layer 2 reads it as opaque data and the model object comes from the caller.
    """
    path = Path(path)

    size = path.stat().st_size
    if size > MAX_POPULATION_BYTES:
        raise PopulationLoadError(
            f"population file '{path}' is {size} bytes, exceeding the "
            f"{MAX_POPULATION_BYTES}-byte cap for untrusted population input"
        )

    with path.open("rb") as stream:
        data = stream.read(MAX_POPULATION_BYTES + 1)
    return load_population_bytes(data, source=path, model=model)
