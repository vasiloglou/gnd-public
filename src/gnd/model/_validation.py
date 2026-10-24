# ruff: noqa: F401 -- historical namespace imports retained for compatibility facade
"""Model loading with two-layer validation.

Layer 1: jsonschema Draft 2020-12 meta-schema (structure, enums, discriminated
per-type constraint shapes, per-source provenance rules) — errors addressed via
``json_path``.
Layer 2: plain-Python semantic rules for what JSON Schema cannot express —
identifier integrity, cross-references, reading/role agreement, reference
modes, and status/source consistency. Each rule is a small pure function over
the parsed document returning :class:`ValidationIssue` records with a stable
``semantic:`` rule_id.

Both layers emit the same unified error record: :class:`ValidationIssue`.
Issues carry a ``severity``: ``error`` issues abort the load
(:class:`ModelValidationError`); ``warning`` issues are attached to the loaded
:class:`Model` as ``Model.warnings`` — the D-03 modality-policy warning uses
this channel.

Threat note (T-01-07): the only pattern applied to document content is the
fixed, linear-time placeholder regex below; no regex is ever taken FROM the
document and evaluated.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from gnd import input_policy as _rf7_input

if TYPE_CHECKING:
    from gnd.population import Population
import json
import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime
from importlib.resources import files
from pathlib import Path
from typing import Any, Literal

from jsonschema import Draft202012Validator
from ruamel.yaml import YAML
from ruamel.yaml.scalarbool import ScalarBoolean

# Message wording for the layer-2 rules lives with every other CNL template
# (gnd.verbalize imports nothing from gnd, so this cannot cycle).
from gnd import verbalize
from gnd.atoms import atom_bind, atom_has_bind
from gnd.documents import (
    DeonticNote,  # historical compatibility export
    Model,
)
from gnd.errors import (
    ModelLoadError,
    ModelValidationError,
    ValidationIssue,
    issues_from_validation_error,  # historical compatibility export
)
from gnd.model._induction import (
    _induction_strings,
    _rule_induced_confirmed_reviewed,
    _rule_induced_provenance,
)
from gnd.terms import (
    DEFAULT_LIMITS,
    FLOAT_FUNCTION_ARITY,
    NUMERIC_PRIMITIVES,
    analyze_term,
    is_function_term,
    term_variables,
)
from gnd.universe import (
    DERIVATION_TERM_CACHE as _DERIVATION_TERM_CACHE,
)
from gnd.universe import (
    fact_type_roles as _fact_type_roles,
)
from gnd.universe import (
    resolved_primitive as _resolved_primitive,
)
from gnd.universe import (
    supertype_parents as _supertype_parents,
)
from gnd.yaml_comments import configure_comment_scanner

#: Fixed pattern counting {Type} / {Type:role} placeholders in readings.
_PLACEHOLDER = re.compile(r"\{[^{}]+\}")

MAX_MODEL_BYTES = 10 * 1024 * 1024  # 10 MB — same cap as population input
from gnd.documents import MAX_YAML_EVENTS


def yaml_stream_guard_error(path: str | Path) -> str | None:
    """Pre-load guard for untrusted YAML input (T-01-02), or None when safe.

    The byte-size cap alone does not bound expansion: ruamel's safe/rt loaders
    expand anchors/aliases without limits, so a well-under-cap billion-laughs
    document exhausts memory during ``yaml.load``. This guard walks the parser
    EVENT stream (no node construction, no alias expansion) and rejects:

    - any alias usage — GND models and populations are plain data documents,
      and the JSON rendering (D-11 parity) has no alias construct either;
    - documents exceeding the ``MAX_YAML_EVENTS`` parse-event budget.
    """
    from ruamel.yaml.events import AliasEvent

    yaml = YAML(typ="safe")
    with open(path, encoding="utf-8") as handle:
        for count, event in enumerate(yaml.parse(handle), start=1):
            if count > MAX_YAML_EVENTS:
                return (
                    f"YAML document '{path}' exceeds the {MAX_YAML_EVENTS} "
                    f"parse-event budget for untrusted input"
                )
            if isinstance(event, AliasEvent):
                return (
                    f"YAML document '{path}' uses an anchor/alias "
                    f"('*{event.anchor}') — aliases are rejected for untrusted "
                    f"input (alias-amplification defense, T-01-02)"
                )
    return None


from gnd.documents import structured_derivation_ids  # historical compatibility export


def _load_meta_schema() -> dict[str, Any]:
    schema_text = files("gnd").joinpath("schema/orm-meta.schema.json").read_text(encoding="utf-8")
    return _rf7_input.loads(schema_text)


#: The keys the structured derivation arm admits. Named here as well as in the
#: meta-schema because the hint below has to say WHICH key was wrong, and a
#: `oneOf` failure cannot: it can only report that the value matched neither
#: arm. The schema is authoritative; this is the vocabulary the message needs.
_DERIVATION_ARM_KEYS = ("aggregate", "body", "negate", "where", "head", "clauses")


def _derivation_rule_hint(error: Any, doc: Any = None) -> str | None:
    """A pointed reason for a `oneOf` failure on a `derivation_rule`.

    The published meta-schema refuses an unknown key -- a third party
    validating against that file must get the same answer GND gives -- but a
    `oneOf` message names no key, and "matched neither arm" sends an author
    hunting. This recovers the naming without weakening the schema, which is
    what made the approved criterion (refuse at the schema AND name the
    construct) look impossible.
    """
    if error.validator != "oneOf" or not str(error.json_path).endswith("derivation_rule"):
        return None
    instance = error.instance
    site = ""
    path = list(error.absolute_path)
    if (
        isinstance(doc, dict)
        and len(path) >= 3
        and path[0] == "fact_types"
        and isinstance(path[1], int)
    ):
        rows = doc.get("fact_types")
        if isinstance(rows, list) and path[1] < len(rows) and isinstance(rows[path[1]], dict):
            site = f"{rows[path[1]].get('id')}.derivation_rule"
    if not isinstance(instance, dict):
        return (
            f"{site}: a derivation rule is either an opaque string or a structured object "
            f"with keys {list(_DERIVATION_ARM_KEYS)}, not "
            f"{type(instance).__name__}"
        )
    unknown = [_safe_key(key) for key in instance if _safe_key(key) not in _DERIVATION_ARM_KEYS]
    if unknown:
        return (
            f"{site}: structured derivation rule has no {sorted(unknown)} construct; the "
            f"admitted keys are {list(_DERIVATION_ARM_KEYS)} -- disjunction, "
            "window functions and unconstrained value invention have no syntax, and a "
            "rule needing one stays an opaque string"
        )
    clauses = instance.get("clauses")
    if isinstance(clauses, list):
        if not clauses:
            return f"{site}.clauses: derivation clauses must be nonempty"
        for index, clause in enumerate(clauses):
            if not isinstance(clause, dict) or (
                not isinstance(clause.get("body"), list)
                or not clause["body"]
                or any(key not in {"body", "negate", "where", "head"} for key in clause)
            ):
                return f"{site}.clauses[{index}]: malformed derivation clause"
        if "body" in instance or "negate" in instance:
            return f"{site}: root body/negate cannot accompany clauses"
        heads = ["head" in clause for clause in clauses]
        if ("head" in instance and any(heads)) or ("head" not in instance and not all(heads)):
            return f"{site}: clauses must use exactly one head placement"
    missing = [key for key in ("body", "head") if key not in instance and "clauses" not in instance]
    if missing:
        return f"{site}: structured derivation rule declares no {sorted(missing)}"
    return site or None


_OBJECT_TYPE_DESCRIPTION_PATH = re.compile(r"\$\.object_types\[\d+\]\.description(?:[.\[]|$)")
#: Subtrees whose values must have a JSON form: object-type descriptions
#: (IK1-D6) and induction blocks (IK2), whose schema bounds NaN would satisfy.
_JSON_FORM_SCREENED_PATHS = (
    _OBJECT_TYPE_DESCRIPTION_PATH,
    re.compile(
        r"\$\.(?:fact_types\[\d+\]\.)?constraints\[\d+\]\.provenance\.induction(?:[.\[]|$)"
    ),
)
_LONE_SURROGATE = re.compile("[\ud800-\udfff]")


def _value_without_json_form(value: Any) -> str | None:
    """Why a screened value cannot be carried unchanged as JSON (IK1-D6, IK2).

    The schema's JSON types cannot refuse these: NaN and infinity are numbers,
    a lone surrogate is a string, and an anchored YAML boolean loads as an
    ``int`` subclass that would serialize as ``1``.
    """
    if isinstance(value, float) and not math.isfinite(value):
        return f"{value!r} is a non-finite number, which has no JSON form"
    if isinstance(value, str) and _LONE_SURROGATE.search(value):
        return "string contains a lone surrogate, which has no UTF-8 JSON form"
    if isinstance(value, ScalarBoolean):
        return "anchored YAML boolean would not be carried unchanged; remove the anchor"
    return None


#: IK1's name, kept as an identity alias after IK2 widened the screen.
_description_value_without_json_form = _value_without_json_form


def _layer1_structural(doc: Any) -> list[ValidationIssue]:
    # jsonschema formats invalid instances in errors. CPython refuses to
    # stringify an integer of more than 4300 decimal digits, so screen hostile
    # in-process JSON before asking it to render a diagnostic.
    pending = [("$", doc)]
    while pending:
        path, value = pending.pop()
        if isinstance(value, dict):
            for key, child in value.items():
                if not isinstance(key, str):
                    derivation = ".derivation_rule" in path
                    return [ValidationIssue(
                        path=path,
                        message=f"object key {_safe_key(key)!r} is not a JSON string",
                        rule_id="jsonschema:oneOf" if derivation else "jsonschema:propertyNames",
                    )]
                pending.append((f"{path}.{key}", child))
        elif isinstance(value, list):
            pending.extend((f"{path}[{index}]", child) for index, child in enumerate(value))
        elif type(value) is int and value.bit_length() > 14_000:
            return [ValidationIssue(
                path=path,
                message="integer literal exceeds the in-process diagnostic limit",
                rule_id="jsonschema:type",
            )]
        elif any(pattern.match(path) for pattern in _JSON_FORM_SCREENED_PATHS) and (
            reason := _value_without_json_form(value)
        ):
            return [ValidationIssue(path=path, message=reason, rule_id="jsonschema:type")]
    validator = Draft202012Validator(_load_meta_schema())
    issues = []
    for error in sorted(validator.iter_errors(doc), key=lambda e: e.json_path):
        message = error.message
        hint = _derivation_rule_hint(error, doc)
        if hint:
            message = f"{hint} [{message}]"
        issues.append(
            ValidationIssue(
                path=error.json_path,
                message=message,
                rule_id=f"jsonschema:{error.validator}",
            )
        )
    return issues


# --- layer-2 helpers ---


def _iter_constraints(doc: dict[str, Any]):
    """Yield (path, constraint) for every ACTIVE constraint, inline then top-level."""
    for fact_type in doc.get("fact_types") or []:
        if not isinstance(fact_type, dict):
            continue
        fact_type_id = fact_type.get("id", "?")
        for index, constraint in enumerate(fact_type.get("constraints") or []):
            if isinstance(constraint, dict):
                yield f"$.fact_types[id={fact_type_id}].constraints[{index}]", constraint
    for index, constraint in enumerate(doc.get("constraints") or []):
        if isinstance(constraint, dict):
            yield f"$.constraints[{index}]", constraint


def _iter_role_refs(constraint: dict[str, Any]):
    """Yield every ``{fact_type, role}`` cross-reference a constraint carries."""
    for field in ("role_refs", "subset_role_seq", "superset_role_seq", "role_seq_a", "role_seq_b"):
        for ref in constraint.get(field) or []:
            if isinstance(ref, dict):
                yield ref
    for sequence in constraint.get("role_seqs") or []:
        for ref in sequence or []:
            if isinstance(ref, dict):
                yield ref
    for field in ("role_ref", "role_a", "role_b"):
        ref = constraint.get(field)
        if isinstance(ref, dict) and "fact_type" in ref:
            yield ref


# --- layer-2 rules (each: pure function doc -> list[ValidationIssue]) ---


def _rule_id_unique(doc: dict[str, Any]) -> list[ValidationIssue]:
    """ONE id namespace, shared by object types, fact types, operations, and
    the optional stable ids constraints may carry (A4).

    A parallel namespace per section was rejected: ``covers:`` entries, blast
    radius references and coverage rows all address model elements by bare id,
    so two elements sharing one id make those addresses ambiguous whatever
    section each lives in. Constraint ids are OPTIONAL — a constraint without
    one is still addressed positionally, and coverage reports a positional
    address as unstable — but a constraint that declares one joins the same
    set as everything else."""
    issues: list[ValidationIssue] = []
    declared_ids: set[str] = set()

    def declare(path: str, element_id: Any, scope: str) -> None:
        if element_id is None:
            return
        if element_id in declared_ids:
            issues.append(
                ValidationIssue(
                    path=path,
                    message=f"duplicate id '{element_id}' across {scope}",
                    rule_id="semantic:id-unique",
                )
            )
        declared_ids.add(element_id)

    scope = "object_types/fact_types/operations/constraint ids"
    for section in ("object_types", "fact_types", "operations"):
        for element in doc.get(section) or []:
            # `isinstance` BEFORE `.get`: a non-mapping element is layer 1's
            # finding, and this rule raising would deny EVERY later rule the
            # chance to report its own. Found by v5.0 Phase 1's hostile-shape
            # sweep; pre-existing since v1 and reachable from any parsed
            # document, because layer 2 runs on documents that survived
            # PARSING, not documents that passed layer 1.
            if not isinstance(element, dict):
                continue
            declare(f"$.{section}[id={element.get('id')}]", element.get("id"), scope)
    for path, constraint in _iter_constraints(doc):
        declare(f"{path}.id", constraint.get("id"), scope)
    return issues


def _rule_role_ref(doc: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    object_type_ids = {
        ot.get("id")
        for ot in doc.get("object_types") or []
        if isinstance(ot, dict) and ot.get("id") is not None
    }
    for fact_type in doc.get("fact_types") or []:
        if not isinstance(fact_type, dict):
            continue
        fact_type_id = fact_type.get("id", "?")
        for role in fact_type.get("roles") or []:
            # Same guard, same reason as `_rule_id_unique` above.
            if not isinstance(role, dict):
                continue
            referenced = role.get("object_type")
            if referenced is not None and referenced not in object_type_ids:
                issues.append(
                    ValidationIssue(
                        path=f"$.fact_types[id={fact_type_id}].roles[{role.get('role_name')}]",
                        message=(
                            f"role '{role.get('role_name')}' references undeclared "
                            f"object type '{referenced}'"
                        ),
                        rule_id="semantic:role-ref",
                    )
                )
    return issues


def _rule_cross_ref(doc: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    roles_by_fact_type = _fact_type_roles(doc)
    for path, constraint in _iter_constraints(doc):
        for ref in _iter_role_refs(constraint):
            fact_type_id = ref.get("fact_type")
            role_name = ref.get("role")
            if fact_type_id not in roles_by_fact_type:
                issues.append(
                    ValidationIssue(
                        path=path,
                        message=(f"role reference names undeclared fact type '{fact_type_id}'"),
                        rule_id="semantic:cross-ref",
                    )
                )
            elif role_name not in roles_by_fact_type[fact_type_id]:
                issues.append(
                    ValidationIssue(
                        path=path,
                        message=(
                            f"role reference names role '{role_name}', which does not exist "
                            f"on fact type '{fact_type_id}'"
                        ),
                        rule_id="semantic:cross-ref",
                    )
                )
    return issues


def _rule_depends_on(doc: dict[str, Any]) -> list[ValidationIssue]:
    """An admission dependency names a declared fact type; cycles are legal."""
    declared = {ft.get("id") for ft in doc.get("fact_types") or [] if isinstance(ft, dict)}
    issues: list[ValidationIssue] = []
    for index, fact_type in enumerate(doc.get("fact_types") or []):
        if not isinstance(fact_type, dict):
            continue
        for dep_index, dependency in enumerate(fact_type.get("depends_on") or []):
            if dependency not in declared:
                issues.append(ValidationIssue(
                    path=f"$.fact_types[{index}].depends_on[{dep_index}]",
                    message=f"dependency names undeclared fact type '{dependency}'",
                    rule_id="semantic:depends-on-ref",
                ))
    return issues


def _rule_reading_placeholders(doc: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    object_types = {
        str(object_type.get("id")): object_type
        for object_type in doc.get("object_types") or []
        if object_type.get("id") is not None
    }

    def normalize(label: str) -> str:
        return "".join(character for character in label.casefold() if character.isalnum())

    for fact_type in doc.get("fact_types") or []:
        fact_type_id = fact_type.get("id", "?")
        reading = str(fact_type.get("reading", ""))
        placeholders = _PLACEHOLDER.findall(reading)
        roles = fact_type.get("roles") or []
        if len(placeholders) != len(roles):
            issues.append(
                ValidationIssue(
                    path=f"$.fact_types[id={fact_type_id}].reading",
                    message=(
                        f"reading of '{fact_type_id}' has {len(placeholders)} placeholder(s) "
                        f"but {len(roles)} role(s)"
                    ),
                    rule_id="semantic:reading-placeholders",
                )
            )
            continue
        for index, (placeholder, role) in enumerate(zip(placeholders, roles, strict=True)):
            object_type_id = str(role.get("object_type"))
            object_type = object_types.get(object_type_id)
            if object_type is None:
                continue  # semantic:role-ref owns undeclared object types
            label = placeholder[1:-1].partition(":")[0].strip()
            expected = {
                normalize(object_type_id),
                normalize(str(object_type.get("name", object_type_id))),
            }
            if normalize(label) not in expected:
                issues.append(
                    ValidationIssue(
                        path=f"$.fact_types[id={fact_type_id}].reading",
                        message=(
                            f"reading placeholder {placeholder!r} at position {index} does "
                            f"not name role {index}'s object type '{object_type_id}'"
                        ),
                        rule_id="semantic:reading-placeholders",
                    )
                )
                break
    return issues


def _rule_fact_type_arity(doc: dict[str, Any]) -> list[ValidationIssue]:
    """An explicit fact-type arity is a cross-check against its role count."""
    issues: list[ValidationIssue] = []
    for fact_type in doc.get("fact_types") or []:
        arity = fact_type.get("arity")
        if arity is None:
            continue
        role_count = len(fact_type.get("roles") or [])
        if arity != role_count:
            fact_type_id = fact_type.get("id", "?")
            issues.append(
                ValidationIssue(
                    path=f"$.fact_types[id={fact_type_id}].arity",
                    message=(
                        f"fact type '{fact_type_id}' declares arity {arity}, but has "
                        f"{role_count} role(s)"
                    ),
                    rule_id="semantic:fact-type-arity",
                )
            )
    return issues


def _rule_role_names_distinct(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Role names are distinct within a fact type, full stop (CR-03).

    This rule used to bucket roles **by object_type** and flag a duplicate name
    only inside one bucket, so two roles of DIFFERENT object types could share a
    name and the model validated clean at exit 0. That is not a cosmetic
    laxness, because ``role_name`` is how everything downstream ADDRESSES a role:

    - ``_fact_type_roles`` returns a SET of role names, so such a fact type's
      "declared role set" has n−1 members for n roles. ``popvalidate``'s R5
      (``population:missing-role``) compares the supplied key set against that
      shrunken set, so a fact filling only one of two roles is structurally
      conformant — and CONTEXT.md probe #1 returns verbatim: a population of
      facts each supplying only ``x`` reported ``pass=1 fail=0 warning=0
      unchecked=0 vacuous=0`` at exit 0 against an alethic ``mandatory`` on that
      role. With an ``instances:`` roster the same model produced a SPURIOUS
      alethic fail instead — wrong in the other direction.
    - ``checker._check_mandatory`` resolves a role's object type with
      ``next(...)``, silently taking whichever duplicate is declared first.

    D-03's premise — "``role_name`` is already ``required`` in the meta-schema,
    so 'the model's role set' is always well defined" — holds only once names are
    unique per fact type. Establishing source: this repo's own
    ``representation-format.md`` ("``role_name``: **required on every role** …
    cross-references and the checker key on it", and "``{ fact_type: <id>, role:
    <role_name> }`` … must resolve"), which is unsatisfiable when one name
    addresses two roles. Halpin's ORM 2 role names are likewise unique per
    predicate.

    The same-object-type case the old rule caught is subsumed: it is the special
    case where the two colliding roles happen to share a type.
    """
    issues: list[ValidationIssue] = []
    for fact_type in doc.get("fact_types") or []:
        fact_type_id = fact_type.get("id", "?")
        role_names = [str(role.get("role_name")) for role in fact_type.get("roles") or []]
        duplicates = sorted({name for name in role_names if role_names.count(name) > 1})
        if duplicates:
            issues.append(
                ValidationIssue(
                    path=f"$.fact_types[id={fact_type_id}].roles",
                    message=(
                        f"fact type '{fact_type_id}' declares role_name(s) "
                        f"{duplicates} more than once (roles: {role_names}); role "
                        f"names address roles in constraints and in populations, "
                        f"so they must be distinct within a fact type — a shared "
                        f"name shrinks the fact type's declared role set and makes "
                        f"a fact that fills only one of the two structurally "
                        f"conformant"
                    ),
                    rule_id="semantic:role-names-distinct",
                )
            )
    return issues


def _rule_subtype_ref(doc: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    object_type_ids = {
        ot.get("id") for ot in doc.get("object_types") or [] if ot.get("id") is not None
    }
    for object_type in doc.get("object_types") or []:
        object_type_id = object_type.get("id", "?")
        for supertype in object_type.get("subtype_of") or []:
            if supertype not in object_type_ids:
                issues.append(
                    ValidationIssue(
                        path=f"$.object_types[id={object_type_id}].subtype_of",
                        message=(f"'{object_type_id}' declares undeclared supertype '{supertype}'"),
                        rule_id="semantic:subtype-ref",
                    )
                )
    return issues


def _rule_external_ref_uc(doc: dict[str, Any]) -> list[ValidationIssue]:
    """reference.mode external requires a top-level external UC over the entity's
    identifying fact types (each referenced fact type plays a role of the entity)."""
    issues: list[ValidationIssue] = []
    fact_types_by_id = {
        str(ft.get("id")): ft
        for ft in doc.get("fact_types") or []
        if isinstance(ft, dict) and ft.get("id") is not None
    }
    external_ucs = [
        constraint
        for constraint in doc.get("constraints") or []
        if isinstance(constraint, dict)
        and constraint.get("type") == "uniqueness"
        and constraint.get("scope") == "external"
    ]

    def _identifies(constraint: dict[str, Any], object_type_id: str) -> bool:
        referenced = [ref.get("fact_type") for ref in constraint.get("role_refs") or []]
        if not referenced:
            return False
        for fact_type_id in referenced:
            fact_type = fact_types_by_id.get(str(fact_type_id))
            if fact_type is None or not any(
                role.get("object_type") == object_type_id for role in fact_type.get("roles") or []
            ):
                return False
        return True

    for object_type in doc.get("object_types") or []:
        if (object_type.get("reference") or {}).get("mode") != "external":
            continue
        object_type_id = object_type.get("id", "?")
        if not any(_identifies(uc, object_type_id) for uc in external_ucs):
            issues.append(
                ValidationIssue(
                    path=f"$.object_types[id={object_type_id}].reference",
                    message=(
                        f"'{object_type_id}' has reference mode 'external' but no top-level "
                        f"external uniqueness constraint identifies it"
                    ),
                    rule_id="semantic:external-ref-uc",
                )
            )
    return issues


def _rule_reference_value_type(doc: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    object_types_by_id = {
        str(ot.get("id")): ot for ot in doc.get("object_types") or [] if ot.get("id") is not None
    }
    for object_type in doc.get("object_types") or []:
        object_type_id = object_type.get("id", "?")
        value_type = (object_type.get("reference") or {}).get("value_type")
        if value_type is None:
            continue
        target = object_types_by_id.get(str(value_type))
        if target is None or target.get("kind") != "value":
            issues.append(
                ValidationIssue(
                    path=f"$.object_types[id={object_type_id}].reference.value_type",
                    message=(
                        f"reference of '{object_type_id}' names '{value_type}', which is not "
                        f"declared as a value-kind object type"
                    ),
                    rule_id="semantic:reference-value-type",
                )
            )
    return issues


def _temporal_literal_valid(value: str, primitive: str) -> bool:
    try:
        if primitive == "Date":
            return re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is not None and bool(
                date.fromisoformat(value)
            )
        if primitive == "DateTime":
            if (
                re.fullmatch(
                    r"\d{4}-\d{2}-\d{2}[Tt ]\d{2}:\d{2}"
                    r"(:\d{2}(\.\d+)?)?([Zz]|[+-]\d{2}:?\d{2})?",
                    value,
                )
                is None
            ):
                return False
            return bool(_rf7_input.parse_datetime(value))
    except ValueError:
        return False
    return False


_NUMERIC_PRIMITIVES = {"Integer", "Float", "Number"}


def _range_endpoints_valid(endpoints: list[Any], primitive: str) -> bool:
    if primitive == "Duration":
        from gnd.terms import valid_duration

        return all(valid_duration(endpoint) for endpoint in endpoints)
    if primitive in _NUMERIC_PRIMITIVES:
        return all(
            isinstance(endpoint, (int, float)) and not isinstance(endpoint, bool)
            for endpoint in endpoints
        )
    if primitive == "String":
        return all(isinstance(endpoint, str) for endpoint in endpoints)
    if primitive in ("Date", "DateTime"):
        return all(
            isinstance(endpoint, str) and _temporal_literal_valid(endpoint, primitive)
            for endpoint in endpoints
        )
    return False


def _rule_value_range_type(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Range endpoints must inhabit the constrained object's primitive domain."""
    issues: list[ValidationIssue] = []
    object_types = {
        str(object_type.get("id")): object_type
        for object_type in doc.get("object_types") or []
        if object_type.get("id") is not None
    }
    for path, constraint in _iter_constraints(doc):
        if constraint.get("type") != "value":
            continue
        range_specs = []
        if constraint.get("range") is not None:
            range_specs.append(constraint["range"])
        range_specs.extend(constraint.get("ranges") or [])
        if not range_specs:
            continue
        target = str(constraint.get("object_type"))
        primitive = _resolved_primitive(target, object_types)
        if primitive is None:
            # D-05: unit-based/external references deliberately have no
            # primitive. Their bounds remain checker-time undecidable rather
            # than becoming a model error through an invented type.
            continue
        for range_index, bounds in enumerate(range_specs):
            endpoints = [bounds[key] for key in ("min", "max") if key in bounds]
            endpoint_path = f"{path}.ranges[{range_index}]" if len(range_specs) > 1 else path
            if not _range_endpoints_valid(endpoints, primitive):
                issues.append(
                    ValidationIssue(
                        path=endpoint_path,
                        message=(
                            f"value range endpoints for '{target}' must match its resolved "
                            f"primitive '{primitive}' and each other"
                        ),
                        rule_id="semantic:value-range-type",
                    )
                )
    return issues


def _rule_value_range_order(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Every fully bounded value range is ordered in its primitive domain."""
    issues: list[ValidationIssue] = []
    object_types = {
        str(object_type.get("id")): object_type
        for object_type in doc.get("object_types") or []
        if object_type.get("id") is not None
    }
    for path, constraint in _iter_constraints(doc):
        if constraint.get("type") != "value":
            continue
        target = str(constraint.get("object_type"))
        primitive = _resolved_primitive(target, object_types)
        if primitive is None:
            continue
        range_specs: list[tuple[str, dict[str, Any]]] = []
        if constraint.get("range") is not None:
            range_specs.append((f"{path}.range", constraint["range"]))
        range_specs.extend(
            (f"{path}.ranges[{index}]", bounds)
            for index, bounds in enumerate(constraint.get("ranges") or [])
        )
        for endpoint_path, bounds in range_specs:
            if "min" not in bounds or "max" not in bounds:
                continue
            minimum = bounds["min"]
            maximum = bounds["max"]
            if not _range_endpoints_valid([minimum, maximum], primitive):
                continue  # semantic:value-range-type owns malformed endpoints
            ordered_min: Any = minimum
            ordered_max: Any = maximum
            if primitive == "Date":
                ordered_min = date.fromisoformat(minimum)
                ordered_max = date.fromisoformat(maximum)
            elif primitive == "DateTime":
                ordered_min, ordered_max = map(_rf7_input.parse_datetime, (minimum, maximum))
                awareness = (
                    ordered_min.utcoffset() is not None,
                    ordered_max.utcoffset() is not None,
                )
                if awareness[0] != awareness[1]:
                    issues.append(
                        ValidationIssue(
                            path=endpoint_path,
                            message=(
                                f"DateTime range for '{target}' mixes an offset-aware "
                                "endpoint with an offset-naive endpoint"
                            ),
                            rule_id="semantic:value-range-order",
                        )
                    )
                    continue
                if awareness[0]:
                    ordered_min = ordered_min.astimezone(UTC)
                    ordered_max = ordered_max.astimezone(UTC)
            if ordered_min > ordered_max:
                issues.append(
                    ValidationIssue(
                        path=endpoint_path,
                        message=(
                            f"value range minimum {minimum!r} exceeds maximum "
                            f"{maximum!r} for '{target}'"
                        ),
                        rule_id="semantic:value-range-order",
                    )
                )
    return issues


def _rule_count_bound_order(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Frequency/cardinality count intervals cannot be inverted."""
    issues: list[ValidationIssue] = []
    for path, constraint in _iter_constraints(doc):
        if constraint.get("type") not in ("frequency", "cardinality"):
            continue
        bound = constraint.get("bound") or {}
        minimum = bound.get("min")
        maximum = bound.get("max")
        if minimum is not None and maximum is not None and minimum > maximum:
            issues.append(
                ValidationIssue(
                    path=f"{path}.bound",
                    message=(f"count bound minimum {minimum} exceeds maximum {maximum}"),
                    rule_id="semantic:count-bound-order",
                )
            )
    return issues


def _rule_status_source(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Status/source consistency: explicit and user-supplied claims are
    confirmed; status 'rejected' lives only in rejected_proposals.

    Applied to every provenance-bearing element, not only to constraints:
    an ORM+ v2 operation and each of its obligations carry the same
    ``source``/``status`` pair under the same policy, which
    ``provenance-and-modality.md`` states once for all of them. Leaving
    operations out would have let ``source: explicit`` sit next to
    ``status: proposed`` — the user's own words filed as a proposal — in exactly
    the place the D-03 defaulting table then reads to pick a modality."""
    issues: list[ValidationIssue] = []
    for path, constraint in _iter_provenance_bearing(doc):
        source = constraint.get("source")
        status = constraint.get("status")
        if status == "rejected":
            issues.append(
                ValidationIssue(
                    path=path,
                    message=(
                        f"active {_provenance_bearing_label(constraint)} has status "
                        f"'rejected' — rejected claims live only in rejected_proposals"
                    ),
                    rule_id="semantic:status-source",
                )
            )
        elif source in ("explicit", "user-supplied") and status != "confirmed":
            issues.append(
                ValidationIssue(
                    path=path,
                    message=(
                        f"{_provenance_bearing_label(constraint)} with source '{source}' "
                        f"must have status 'confirmed', not '{status}'"
                    ),
                    rule_id="semantic:status-source",
                )
            )
    return issues


def _rule_string_ref(doc: dict[str, Any]) -> list[ValidationIssue]:
    """WR-01: resolve every plain-string reference that the dict-shape
    ``semantic:cross-ref`` rule does not cover — inline ``roles``/``role``
    against the host fact type's role_names, ``object_type``/``supertype``/
    ``subtypes[]``/``objectified_as`` against declared object-type ids, and
    inline value-comparison operands (at least one must name a host role;
    the other may be a literal or a time function). Typos in these references
    previously produced silent passes or spurious alethic fails at check time."""
    issues: list[ValidationIssue] = []
    object_type_ids = {
        str(ot.get("id")) for ot in doc.get("object_types") or [] if ot.get("id") is not None
    }
    roles_by_fact_type = _fact_type_roles(doc)

    def unresolved(path: str, message: str) -> None:
        issues.append(ValidationIssue(path=path, message=message, rule_id="semantic:string-ref"))

    for fact_type in doc.get("fact_types") or []:
        fact_type_id = str(fact_type.get("id", "?"))
        objectified = fact_type.get("objectified_as")
        if objectified is not None and str(objectified) not in object_type_ids:
            unresolved(
                f"$.fact_types[id={fact_type_id}].objectified_as",
                f"objectified_as names undeclared object type '{objectified}'",
            )
        role_names = roles_by_fact_type.get(fact_type_id, set())
        for index, constraint in enumerate(fact_type.get("constraints") or []):
            path = f"$.fact_types[id={fact_type_id}].constraints[{index}]"
            for role in constraint.get("roles") or []:
                if isinstance(role, str) and role not in role_names:
                    unresolved(
                        path,
                        f"constraint references role '{role}', which does not exist "
                        f"on fact type '{fact_type_id}'",
                    )
            role = constraint.get("role")
            if isinstance(role, str) and role not in role_names:
                unresolved(
                    path,
                    f"constraint references role '{role}', which does not exist "
                    f"on fact type '{fact_type_id}'",
                )
            if constraint.get("type") == "value-comparison":
                operands = [constraint.get("role_a"), constraint.get("role_b")]
                named_roles = [
                    str(operand["role"])
                    for operand in operands
                    if isinstance(operand, dict) and "role" in operand
                ]
                named_roles.extend(
                    operand
                    for operand in operands
                    if isinstance(operand, str) and operand in role_names
                )
                invalid_roles = [role for role in named_roles if role not in role_names]
                if invalid_roles:
                    unresolved(
                        path,
                        f"value-comparison references roles not declared by "
                        f"'{fact_type_id}': {sorted(invalid_roles)}",
                    )
                if not named_roles:
                    legacy = sorted(
                        str(operand) for operand in operands if isinstance(operand, str)
                    )
                    unresolved(
                        path,
                        f"value-comparison on '{fact_type_id}' has no operand naming a "
                        f"role of the fact type ({legacy}) — a typo'd operand "
                        f"would silently compare as a string literal",
                    )

    for path, constraint in _iter_constraints(doc):
        for field in ("object_type", "supertype"):
            target = constraint.get(field)
            if target is not None and str(target) not in object_type_ids:
                unresolved(path, f"{field} names undeclared object type '{target}'")
        for subtype in constraint.get("subtypes") or []:
            if str(subtype) not in object_type_ids:
                unresolved(path, f"subtypes entry names undeclared object type '{subtype}'")
    return issues


def _ancestor_closure(object_type_id: str, parents: dict[str, list[str]]) -> set[str]:
    """The object type plus all transitive supertypes (cycle-safe BFS)."""
    seen = {object_type_id}
    frontier = [object_type_id]
    while frontier:
        current = frontier.pop()
        for parent in parents.get(current, []):
            if parent not in seen:
                seen.add(parent)
                frontier.append(parent)
    return seen


def _rule_ring_binary(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Halpin's ring precondition (constraint-reference.md): a ring constraint's
    host fact type must be a binary whose two roles are played by compatible
    object types (the same type, or types sharing a common supertype). Without
    this rule the checker would receive an unevaluable constraint (CR-01)."""
    issues: list[ValidationIssue] = []
    parents = _supertype_parents(doc)
    for fact_type in doc.get("fact_types") or []:
        roles = fact_type.get("roles") or []
        for index, constraint in enumerate(fact_type.get("constraints") or []):
            if constraint.get("type") != "ring":
                continue
            object_types = [str(role.get("object_type")) for role in roles]
            compatible = len(roles) == 2 and bool(
                _ancestor_closure(object_types[0], parents)
                & _ancestor_closure(object_types[1], parents)
            )
            if not compatible:
                issues.append(
                    ValidationIssue(
                        path=f"$.fact_types[id={fact_type.get('id')}].constraints[{index}]",
                        message=(
                            f"ring constraint requires a binary fact type with both roles "
                            f"played by compatible object types; '{fact_type.get('id')}' "
                            f"has {len(roles)} role(s) over {sorted(set(object_types))}"
                        ),
                        rule_id="semantic:ring-binary",
                    )
                )
    return issues


#: Set-comparison families and the sequence-valued fields each one declares.
#: ``exclusive-or`` instead carries a LIST of sequences (``role_seqs``,
#: minItems 2) and is handled separately in :func:`_constraint_role_seqs`.
_ROLE_SEQ_FIELDS: dict[str, tuple[str, ...]] = {
    "subset": ("subset_role_seq", "superset_role_seq"),
    "equality": ("role_seq_a", "role_seq_b"),
    "exclusion": ("role_seq_a", "role_seq_b"),
}


def _constraint_role_seqs(constraint: dict[str, Any]) -> list[tuple[str, list[dict]]]:
    """``(label, sequence)`` for every role sequence a set-comparison constraint
    carries, in declaration order. Empty for every other family."""
    constraint_type = str(constraint.get("type"))
    if constraint_type == "exclusive-or":
        return [
            (f"role_seqs[{index}]", [r for r in (seq or []) if isinstance(r, dict)])
            for index, seq in enumerate(constraint.get("role_seqs") or [])
        ]
    return [
        (field, [r for r in (constraint.get(field) or []) if isinstance(r, dict)])
        for field in _ROLE_SEQ_FIELDS.get(constraint_type, ())
        if constraint.get(field) is not None
    ]


def _joining_sequences(constraint: dict[str, Any]) -> list[list[dict[str, Any]]]:
    """Role sequences whose evaluation invokes a cross-fact shared-anchor join."""
    constraint_type = constraint.get("type")
    if constraint_type in ("uniqueness", "frequency") and constraint.get("scope") == "external":
        return [list(constraint.get("role_refs") or [])]
    if constraint_type == "value-comparison" and isinstance(constraint.get("role_a"), dict):
        return [[constraint["role_a"], constraint["role_b"]]]
    return [sequence for _, sequence in _constraint_role_seqs(constraint)]


def _rule_join_anchor_unambiguous(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Reject inferred joins with multiple same-type anchors on one fact type."""
    issues: list[ValidationIssue] = []
    fact_types = {
        str(fact_type.get("id")): fact_type
        for fact_type in doc.get("fact_types") or []
        if fact_type.get("id") is not None
    }
    for path, constraint in _iter_constraints(doc):
        for sequence in _joining_sequences(constraint):
            fact_type_ids = {str(ref.get("fact_type")) for ref in sequence}
            if len(fact_type_ids) <= 1:
                continue
            referenced: dict[str, set[str]] = {}
            for ref in sequence:
                referenced.setdefault(str(ref.get("fact_type")), set()).add(str(ref.get("role")))
            for fact_type_id in sorted(fact_type_ids):
                anchors: dict[str, list[str]] = {}
                for role in (fact_types.get(fact_type_id) or {}).get("roles") or []:
                    role_name = str(role.get("role_name"))
                    if role_name in referenced.get(fact_type_id, set()):
                        continue
                    anchors.setdefault(str(role.get("object_type")), []).append(role_name)
                ambiguous = {
                    object_type: role_names
                    for object_type, role_names in anchors.items()
                    if len(role_names) > 1
                }
                if ambiguous:
                    issues.append(
                        ValidationIssue(
                            path=path,
                            message=(
                                f"cross-fact join on '{fact_type_id}' has multiple candidate "
                                f"anchor roles for one object type: {ambiguous}; declare an "
                                "explicit join mapping before this constraint can be checked"
                            ),
                            rule_id="semantic:join-anchor-ambiguous",
                        )
                    )
    return issues


def _role_object_types(doc: dict[str, Any]) -> dict[str, dict[str, str]]:
    """fact_type id -> role_name -> object_type id."""
    return {
        str(ft.get("id")): {
            str(role.get("role_name")): str(role.get("object_type"))
            for role in ft.get("roles") or []
            if isinstance(role, dict) and role.get("role_name") is not None
        }
        for ft in doc.get("fact_types") or []
        if isinstance(ft, dict) and ft.get("id") is not None
    }


def _rule_role_seq_arity(doc: dict[str, Any]) -> list[ValidationIssue]:
    """ORM 2's set-comparison precondition, first half (D-13 clause 3): subset,
    equality, exclusion and exclusive-or are defined over COMPATIBLE role
    sequences, and compatibility presupposes equal arity — a (person, course)
    pair has no defined containment relation to a bare (person) (Halpin, ORM 2
    TechReport §2.8). Enforced at model load for the same reason
    ``semantic:ring-binary`` is: it is a defect of the MODEL, so it must fail
    at ``gnd validate`` before any population exists, rather than reaching the
    checker as a constraint evaluated over mismatched projections."""
    issues: list[ValidationIssue] = []
    for path, constraint in _iter_constraints(doc):
        seqs = _constraint_role_seqs(constraint)
        if len(seqs) < 2:
            continue
        if len({len(sequence) for _, sequence in seqs}) > 1:
            issues.append(
                ValidationIssue(
                    path=path,
                    message=verbalize.role_seq_arity_message(
                        str(constraint.get("type")),
                        [(label, len(sequence)) for label, sequence in seqs],
                    ),
                    rule_id="semantic:role-seq-arity",
                )
            )
    return issues


def _rule_role_seq_type_compat(doc: dict[str, Any]) -> list[ValidationIssue]:
    """ORM 2's set-comparison precondition, second half (D-13 clause 3): at each
    position the compared roles must be played by COMPATIBLE object types.
    Equal length is necessary but not sufficient — the constraint asserts the
    same tuple appears in both projections, which is meaningless when the values
    at a position are drawn from disjoint populations.

    "Compatible" is deliberately the SAME predicate ``_rule_ring_binary`` uses —
    a non-empty intersection of the two ancestor closures, i.e. the same object
    type or types sharing a common supertype. One notion of type compatibility
    that disagrees with another is a latent bug in exactly the family this rule
    exists to repair, and reusing ``_ancestor_closure`` inherits its cycle
    safety (subtype cycles are NOT rejected by validation today)."""
    issues: list[ValidationIssue] = []
    parents = _supertype_parents(doc)
    role_types = _role_object_types(doc)
    for path, constraint in _iter_constraints(doc):
        seqs = _constraint_role_seqs(constraint)
        # Unequal lengths belong to semantic:role-seq-arity; reporting both
        # would give one defect two names.
        if len(seqs) < 2 or len({len(sequence) for _, sequence in seqs}) != 1:
            continue
        for position in range(len(seqs[0][1])):
            resolved: list[tuple[str, str, str]] = []
            for _, sequence in seqs:
                ref = sequence[position]
                fact_type_id = str(ref.get("fact_type"))
                role_name = str(ref.get("role"))
                object_type = role_types.get(fact_type_id, {}).get(role_name)
                # An unresolvable reference is semantic:cross-ref's finding;
                # naming it here too would produce a confusing second error.
                if object_type is not None:
                    resolved.append((fact_type_id, role_name, object_type))
            mismatch = next(
                (
                    other
                    for other in resolved[1:]
                    if not (
                        _ancestor_closure(resolved[0][2], parents)
                        & _ancestor_closure(other[2], parents)
                    )
                ),
                None,
            )
            if mismatch is not None:
                issues.append(
                    ValidationIssue(
                        path=path,
                        message=verbalize.role_seq_type_compat_message(
                            str(constraint.get("type")),
                            position,
                            resolved[0],
                            mismatch,
                        ),
                        rule_id="semantic:role-seq-type-compat",
                    )
                )
    return issues


def _rule_disjunctive_subject_type(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Single-role disjunctions require one declaration-order-neutral subject."""
    issues: list[ValidationIssue] = []
    role_types = _role_object_types(doc)
    for path, constraint in _iter_constraints(doc):
        role_refs: list[dict[str, Any]] = []
        if constraint.get("type") == "mandatory-disjunctive":
            role_refs = list(constraint.get("role_refs") or [])
        elif constraint.get("type") == "exclusive-or":
            sequences = list(constraint.get("role_seqs") or [])
            if sequences and all(len(sequence or []) == 1 for sequence in sequences):
                role_refs = [sequence[0] for sequence in sequences]
        if not role_refs:
            continue
        declared = {
            role_types.get(str(ref.get("fact_type")), {}).get(str(ref.get("role")))
            for ref in role_refs
        }
        declared.discard(None)
        if len(declared) != 1 or len(declared) < len(
            {
                role_types.get(str(ref.get("fact_type")), {}).get(str(ref.get("role")))
                for ref in role_refs
            }
        ):
            issues.append(
                ValidationIssue(
                    path=path,
                    message=(
                        "single-role disjunctive constraints require every referenced "
                        f"role to declare the same subject object type, got {sorted(declared)}"
                    ),
                    rule_id="semantic:disjunctive-subject-type",
                )
            )
    return issues


def _rule_partition_asserts_something(doc: dict[str, Any]) -> list[ValidationIssue]:
    """CR-02: a ``subtype-partition`` declaring neither ``exclusive`` nor
    ``exhaustive`` asserts nothing, and must not be authorable.

    In ORM 2 a subtype *partition* IS the conjunction of subtype exclusion (⊗)
    and subtype totality (⊍) — Halpin, *Information Modeling and Relational
    Databases* 2e §6.5. This repo's own normative reference agrees:
    ``src/gnd/skills/gnd-orm-core/references/constraint-reference.md`` enumerates exactly
    three verbalizations ("full partition", "exclusive only", "exhaustive
    only"). There is no "neither" reading, so the shape has no meaning to check
    and ``pass`` was never a defined outcome for it — yet the checker computed
    ``both = []`` and ``neither = []`` and reported "Every {supertype} is
    partitioned over: … — satisfied", structurally identical to the withdrawn
    ``neither = []`` hardcode that CONTEXT.md lists as verified defect #3.

    Enforced HERE rather than in the meta-schema on purpose. An ``anyOf`` inside
    ``$defs/subtype_partition`` would make the shape unrepresentable too, but
    that ``$def`` sits inside ``top_level_constraint``'s ``oneOf``: a flagless
    partition would then match zero branches and the author would receive
    ``jsonschema:oneOf`` "is not valid under any of the given schemas" instead of
    a sentence naming the repair — the opposite of D-04's actionable-feedback
    posture. ``semantic:ring-binary``, ``semantic:role-seq-arity`` and
    ``semantic:role-seq-type-compat`` are the precedent: a Halpin precondition
    the ``oneOf`` shape cannot express well belongs in layer 2, which rejects it
    at ``gnd validate`` just as hard (exit 3). ``checker._check_subtype_partition``
    keeps a matching ``unchecked`` branch as defense in depth, for a ``Model``
    built in process rather than loaded.

    ``exclusive: false`` / ``exhaustive: false`` are treated as absent: an
    explicitly-false flag asserts exactly as much as a missing one (nothing),
    and accepting it would leave the undefined state representable behind a
    presence check.
    """
    issues: list[ValidationIssue] = []
    for path, constraint in _iter_constraints(doc):
        if constraint.get("type") != "subtype-partition":
            continue
        if constraint.get("exclusive") or constraint.get("exhaustive"):
            continue
        issues.append(
            ValidationIssue(
                path=path,
                message=verbalize.partition_asserts_nothing_message(
                    str(constraint.get("supertype")),
                    [str(s) for s in constraint.get("subtypes") or []],
                ),
                rule_id="semantic:partition-asserts-nothing",
            )
        )
    return issues


#: Constraint families the checker can NEVER mechanically evaluate — not "not
#: yet implemented" but unimplementable in principle. A ``textual`` constraint
#: holds a natural-language expression that is stored as quoted data and never
#: parsed (T-01-08), so no future phase can decide it. Families merely absent
#: from ``checker.IMPLEMENTED_FAMILIES`` are deliberately NOT listed here: they
#: are unchecked today and decidable tomorrow, which is a different claim.
NEVER_MECHANICAL_FAMILIES = frozenset({"textual"})


def _rule_anchored_role_and_recogniser(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Resolve each inline anchor selector against its declared role primitive."""
    issues: list[ValidationIssue] = []
    objects = {
        str(value.get("id")): value
        for value in doc.get("object_types") or []
        if isinstance(value, dict) and value.get("id") is not None
    }
    compatible = {
        "integer": {"Integer"},
        "decimal": {"Float", "Number"},
        "percent": {"Integer", "Float", "Number"},
        "iso-8601-date": {"Date"},
    }
    for fact_type in doc.get("fact_types") or []:
        if not isinstance(fact_type, dict):
            continue
        roles = {
            str(role.get("role_name")): str(role.get("object_type"))
            for role in fact_type.get("roles") or []
            if isinstance(role, dict) and role.get("role_name") is not None
        }
        for index, constraint in enumerate(fact_type.get("constraints") or []):
            if not isinstance(constraint, dict) or constraint.get("type") != "anchored":
                continue
            path = f"$.fact_types[id={fact_type.get('id')}].constraints[{index}]"
            selected = constraint.get("role")
            if selected is not None and str(selected) not in roles:
                issues.append(ValidationIssue(
                    path=f"{path}.role",
                    message=f"anchored role {selected!r} is not declared by fact type {fact_type.get('id')!r}",
                    rule_id="semantic:anchored-invalid",
                ))
                continue
            if selected is None:
                continue
            primitive = _resolved_primitive(roles[str(selected)], objects)
            for recogniser in constraint.get("recognise") or []:
                if primitive not in compatible.get(str(recogniser), set()):
                    issues.append(ValidationIssue(
                        path=f"{path}.recognise",
                        message=f"recogniser {recogniser!r} is incompatible with {selected!r} ({primitive})",
                        rule_id="semantic:anchored-invalid",
                    ))
    return issues


def _rule_textual_alethic(doc: dict[str, Any]) -> list[ValidationIssue]:
    """D-20: an alethic constraint in a never-mechanically-checkable family
    makes its model PERMANENTLY indeterminate — no population can ever reach
    exit 0, because an unverifiable hard constraint means acceptance cannot be
    mechanically claimed. That is accepted as correct; this rule only moves the
    discovery from check time to AUTHORING time, where it can still be fixed.

    Severity is WARNING and must stay warning: promoting it to an error would
    reject every existing model carrying one, and ``gnd validate`` must keep
    exiting 0. Exempting ``textual`` from band 4 instead was rejected — that is
    exactly the "we decided not to look, so we will call it fine" reasoning
    phase 01.1 exists to remove."""
    issues: list[ValidationIssue] = []
    for path, constraint in _iter_constraints(doc):
        if (
            constraint.get("type") in NEVER_MECHANICAL_FAMILIES
            and constraint.get("modality") == "alethic"
        ):
            issues.append(
                ValidationIssue(
                    path=path,
                    message=verbalize.textual_alethic_message(
                        str(constraint.get("type")), constraint.get("expression")
                    ),
                    rule_id="semantic:textual-alethic",
                    severity="warning",
                )
            )
    return issues


def _rule_modality_policy(doc: dict[str, Any]) -> list[ValidationIssue]:
    """D-03 over-modeling defense, made structural: an UNCONFIRMED llm-inferred,
    common-sense or induced constraint claiming alethic modality gets a WARNING."""
    issues: list[ValidationIssue] = []
    for path, constraint in _iter_constraints(doc):
        if (
            constraint.get("source") == "induced"
            and constraint.get("status") == "proposed"
            and constraint.get("modality") == "alethic"
        ):
            # IK2: its own sentence, so the llm-inferred/common-sense message
            # below stays byte-identical for every model that already gets it.
            issues.append(
                ValidationIssue(
                    path=path,
                    message=(
                        f"unconfirmed induced {constraint.get('type')} constraint carries "
                        f"modality 'alethic' — induced constraints default to deontic until "
                        f"reviewed (D-03)"
                    ),
                    rule_id="semantic:modality-policy",
                    severity="warning",
                )
            )
        elif (
            constraint.get("source") in ("llm-inferred", "common-sense")
            and constraint.get("status") == "proposed"
            and constraint.get("modality") == "alethic"
        ):
            issues.append(
                ValidationIssue(
                    path=path,
                    message=(
                        f"unconfirmed {constraint.get('source')} {constraint.get('type')} "
                        f"constraint carries modality 'alethic' — unconfirmed llm-inferred/"
                        f"common-sense constraints default to deontic until user-confirmed "
                        f"(D-03)"
                    ),
                    rule_id="semantic:modality-policy",
                    severity="warning",
                )
            )
    return issues


# --- layer-2 helpers for ORM+ v2 operations ---
#
# Every rule below reads ``doc["operations"]``, which a v1 document simply does
# not have — each one is a no-op on every model authored before v2, which is
# what makes "v1 loads byte-identically" true by construction rather than by
# regression testing.


def _iter_operations(doc: dict[str, Any]):
    """Yield ``(path, operation)`` for every declared operation."""
    for index, operation in enumerate(doc.get("operations") or []):
        identifier = operation.get("id")
        locator = f"id={identifier}" if identifier is not None else str(index)
        yield f"$.operations[{locator}]", operation


def _operation_parameters(operation: dict[str, Any]) -> dict[str, str]:
    """parameter name -> declared object type, first declaration winning.

    First-wins rather than last-wins so that a duplicate name (which
    ``semantic:op-param-names-distinct`` rejects on its own) cannot also change
    which type every other rule resolves — one defect, one message."""
    resolved: dict[str, str] = {}
    for parameter in operation.get("parameters") or []:
        name = parameter.get("name")
        if name is None or str(name) in resolved:
            continue
        resolved[str(name)] = str(parameter.get("object_type"))
    return resolved


def _iter_operation_obligations(operation: dict[str, Any]):
    """Yield ``(kind, index, obligation)`` for every modality-bearing rule an
    operation carries — preconditions and dynamic rules alike."""
    for index, obligation in enumerate(operation.get("preconditions") or []):
        yield "preconditions", index, obligation
    for index, rule in enumerate(operation.get("dynamic_rules") or []):
        yield "dynamic_rules", index, rule


def _iter_operation_atoms(operation: dict[str, Any]):
    """Yield ``(suffix, atom_like)`` for every ``{fact_type, bind}`` site.

    Covers precondition atoms, ``assert``/``retract`` effects, and dynamic-rule
    subjects: the subject is an atom carrying one extra key (``value_role``),
    and treating it as anything else would exempt it from reference checking."""
    for index, obligation in enumerate(operation.get("preconditions") or []):
        for atom_index, atom in enumerate(obligation.get("require") or []):
            if isinstance(atom, dict):
                yield f".preconditions[{index}].require[{atom_index}]", atom
    for index, effect in enumerate(operation.get("effects") or []):
        if not isinstance(effect, dict):
            continue
        for verb in ("assert", "retract"):
            atom = effect.get(verb)
            if isinstance(atom, dict):
                yield f".effects[{index}].{verb}", atom
    for index, rule in enumerate(operation.get("dynamic_rules") or []):
        subject = rule.get("subject")
        if isinstance(subject, dict):
            yield f".dynamic_rules[{index}].subject", subject


def _iter_operation_terms(operation: dict[str, Any]):
    """Yield ``(suffix, role_name, term)`` for every bound term in an operation."""
    for suffix, atom in _iter_operation_atoms(operation):
        bind = atom_bind(atom)
        if not isinstance(bind, dict):
            continue
        for role_name, term in bind.items():
            yield f"{suffix}.bind[{role_name}]", str(role_name), term


def _variable_name(term: Any) -> str | None:
    """The parameter a term references, or None when the term is a literal."""
    if isinstance(term, str) and term.startswith("$"):
        return term[1:]
    return None


def _rule_op_param_ref(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Every operation parameter names a declared object type."""
    issues: list[ValidationIssue] = []
    object_type_ids = {
        str(ot.get("id")) for ot in doc.get("object_types") or [] if ot.get("id") is not None
    }
    for path, operation in _iter_operations(doc):
        for index, parameter in enumerate(operation.get("parameters") or []):
            referenced = parameter.get("object_type")
            if referenced is not None and str(referenced) not in object_type_ids:
                issues.append(
                    ValidationIssue(
                        path=f"{path}.parameters[{index}]",
                        message=(
                            f"parameter '{parameter.get('name')}' references undeclared "
                            f"object type '{referenced}'"
                        ),
                        rule_id="semantic:op-param-ref",
                    )
                )
    return issues


def _rule_op_param_names_distinct(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Two parameters of one operation may not share a name — every ``$var``
    in that operation would otherwise resolve to whichever the loader happened
    to index last."""
    issues: list[ValidationIssue] = []
    for path, operation in _iter_operations(doc):
        seen: set[str] = set()
        for parameter in operation.get("parameters") or []:
            name = parameter.get("name")
            if name is None:
                continue
            if str(name) in seen:
                issues.append(
                    ValidationIssue(
                        path=f"{path}.parameters",
                        message=(
                            f"operation '{operation.get('id')}' declares parameter "
                            f"'{name}' more than once"
                        ),
                        rule_id="semantic:op-param-names-distinct",
                    )
                )
            seen.add(str(name))
    return issues


#: How many parameter names a placeholder-resolution failure prints. The
#: message names the candidates so the author can fix the reading; a model may
#: legally declare thousands of parameters, and a message that printed all of
#: them would be a second denial of service, on the reader.
_REPORTED_PARAMETER_LIMIT = 8


def _rule_op_reading_placeholders(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Every ``{...}`` placeholder in an operation reading names exactly one
    declared parameter, and no parameter is claimed twice.

    This is deliberately NOT the fact-type rule's bijection. A fact type's
    reading verbalizes its complete role tuple, so placeholder count must equal
    role count; an operation reading is a sentence a stakeholder reads, and an
    operation legitimately takes parameters the sentence does not mention (a
    binding used only by a dynamic rule, for instance). What must hold is that
    every placeholder resolves: a reading naming something that is not a
    parameter is a reading about a different operation.

    Resolution reuses the fact-type matcher's normalization and accepts three
    spellings: the parameter's own name, its object type's id, or that object
    type's ``name``. ``{Type:param}`` disambiguates when two parameters share
    one object type -- and the ``Type`` half is still checked, so
    ``{Wrong:note}`` is a defect rather than a comment.

    Resolution goes through an INDEX built once per operation, never a scan per
    placeholder. The scan was quadratic in the parameter count, and an untrusted
    model under the 10 MB cap can declare tens of thousands of parameters and as
    many placeholders: a 463 KB document with 4,000 of each took 4.4 seconds to
    load, and the cap admits documents an order of magnitude larger (T-01)."""
    issues: list[ValidationIssue] = []
    object_types = {
        str(object_type.get("id")): object_type
        for object_type in doc.get("object_types") or []
        if object_type.get("id") is not None
    }

    def normalize(label: str) -> str:
        return "".join(character for character in label.casefold() if character.isalnum())

    for path, operation in _iter_operations(doc):
        parameters = _operation_parameters(operation)
        identifier = operation.get("id")
        # normalized spelling -> the parameters it could name. Built ONCE.
        by_spelling: dict[str, set[str]] = {}
        own_spellings: dict[str, set[str]] = {}
        for name, object_type_id in parameters.items():
            object_type = object_types.get(object_type_id) or {}
            spellings = {
                normalize(name),
                normalize(object_type_id),
                normalize(str(object_type.get("name", object_type_id))),
            }
            own_spellings[name] = spellings
            for spelling in spellings:
                by_spelling.setdefault(spelling, set()).add(name)

        def refuse(
            placeholder: str,
            reason: str,
            *,
            # Bound as defaults, not captured: a closure over the loop
            # variables would report every operation's failure against the
            # LAST operation's path (B023).
            where: str = path,
            named: Any = identifier,
            declared: dict[str, str] = parameters,
        ) -> None:
            shown = sorted(declared)[:_REPORTED_PARAMETER_LIMIT]
            elided = len(declared) - len(shown)
            listing = f"{shown}" + (f" and {elided} more" if elided > 0 else "")
            issues.append(
                ValidationIssue(
                    path=f"{where}.reading",
                    message=(
                        f"reading placeholder {placeholder!r} of operation "
                        f"'{named}' {reason}; declared parameters: {listing}"
                    ),
                    rule_id="semantic:op-reading-placeholders",
                )
            )

        claimed: set[str] = set()
        for placeholder in _PLACEHOLDER.findall(str(operation.get("reading", ""))):
            label, _, qualifier = placeholder[1:-1].partition(":")
            label = label.strip()
            qualifier = qualifier.strip()
            if qualifier:
                if qualifier not in parameters:
                    refuse(placeholder, f"names no parameter {qualifier!r}")
                    break
                if normalize(label) not in own_spellings[qualifier]:
                    refuse(
                        placeholder,
                        f"qualifies parameter {qualifier!r}, whose object type is "
                        f"'{parameters[qualifier]}' and not {label!r}",
                    )
                    break
                matched = qualifier
            else:
                candidates = by_spelling.get(normalize(label), set())
                if len(candidates) != 1:
                    refuse(
                        placeholder,
                        "names no parameter"
                        if not candidates
                        else (
                            f"is ambiguous between {sorted(candidates)} -- qualify it "
                            f"as {{{label}:<parameter>}}"
                        ),
                    )
                    break
                matched = next(iter(candidates))
            if matched in claimed:
                refuse(placeholder, f"claims parameter {matched!r} a second time")
                break
            claimed.add(matched)
    return issues


def _atom_reference_issues(
    path: str,
    atom: Any,
    roles_by_fact_type: dict[str, set[str]],
    rule_id: str,
    *,
    extra_role_names: tuple[Any, ...] = (),
) -> list[ValidationIssue]:
    """Check one atom's fact-type and role references for any rule family."""
    if not isinstance(atom, dict):
        return []

    issues: list[ValidationIssue] = []
    fact_type_id = atom.get("fact_type")
    if str(fact_type_id) not in roles_by_fact_type:
        return [
            ValidationIssue(
                path=path,
                message=f"atom names undeclared fact type '{fact_type_id}'",
                rule_id=rule_id,
            )
        ]

    declared = roles_by_fact_type[str(fact_type_id)]
    bind = atom_bind(atom)
    named = list(bind) if isinstance(bind, dict) else []
    named.extend(extra_role_names)
    for role_name in named:
        if str(role_name) not in declared:
            issues.append(
                ValidationIssue(
                    path=path,
                    message=(
                        f"atom binds role '{role_name}', which does not exist on "
                        f"fact type '{fact_type_id}'"
                    ),
                    rule_id=rule_id,
                )
            )
    return issues


def _rule_op_atom_ref(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Every atom names a declared fact type, and every bind key — plus a
    dynamic rule's ``value_role`` — names a role of that fact type."""
    issues: list[ValidationIssue] = []
    roles_by_fact_type = _fact_type_roles(doc)
    for path, operation in _iter_operations(doc):
        for suffix, atom in _iter_operation_atoms(operation):
            extra = (atom.get("value_role"),) if atom.get("value_role") is not None else ()
            issues.extend(
                _atom_reference_issues(
                    f"{path}{suffix}",
                    atom,
                    roles_by_fact_type,
                    rule_id="semantic:op-atom-ref",
                    extra_role_names=extra,
                )
            )
    return issues


def _rule_op_term_ref(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Every ``$var`` — in a precondition, an effect, or a dynamic subject —
    names a declared parameter of its own operation. A parameter minted by a
    ``create`` effect is a declared parameter like any other, so this rule is
    also what makes "every effect variable is bound" true."""
    issues: list[ValidationIssue] = []
    for path, operation in _iter_operations(doc):
        parameters = _operation_parameters(operation)
        for suffix, _role_name, term in _iter_operation_terms(operation):
            variable = _variable_name(term)
            if variable is not None and variable not in parameters:
                issues.append(
                    ValidationIssue(
                        path=f"{path}{suffix}",
                        message=(
                            f"term '{term}' names no declared parameter of operation "
                            f"'{operation.get('id')}' (declared: {sorted(parameters)})"
                        ),
                        rule_id="semantic:op-term-ref",
                    )
                )
    return issues


def _rule_op_term_type_compat(doc: dict[str, Any]) -> list[ValidationIssue]:
    """A parameter bound to a role must be able to play it: the parameter's
    object type and the role's object type share an ancestor closure.

    "Compatible" is the SAME predicate ``semantic:ring-binary`` and
    ``semantic:role-seq-type-compat`` use — one notion of type compatibility,
    because a second one that disagrees is a latent bug in exactly the family
    this rule exists to repair."""
    issues: list[ValidationIssue] = []
    parents = _supertype_parents(doc)
    role_types = _role_object_types(doc)
    declared_object_types = {
        str(ot.get("id")) for ot in doc.get("object_types") or [] if ot.get("id") is not None
    }
    for path, operation in _iter_operations(doc):
        parameters = _operation_parameters(operation)
        for suffix, atom in _iter_operation_atoms(operation):
            fact_type_id = str(atom.get("fact_type"))
            bind = atom_bind(atom)
            if not isinstance(bind, dict):
                continue
            for role_name, term in bind.items():
                variable = _variable_name(term)
                # An unresolvable variable, role, or parameter type is another
                # rule's finding; naming it here too would give one defect two
                # names — and an undeclared type has an ancestor closure of
                # itself, so it would fail this test for the wrong reason.
                if variable is None or variable not in parameters:
                    continue
                if parameters[variable] not in declared_object_types:
                    continue
                role_object_type = role_types.get(fact_type_id, {}).get(str(role_name))
                if role_object_type is None:
                    continue
                parameter_object_type = parameters[variable]
                if not (
                    _ancestor_closure(parameter_object_type, parents)
                    & _ancestor_closure(role_object_type, parents)
                ):
                    issues.append(
                        ValidationIssue(
                            path=f"{path}{suffix}.bind[{role_name}]",
                            message=(
                                f"parameter '{variable}' of type "
                                f"'{parameter_object_type}' cannot play role "
                                f"'{role_name}' of '{fact_type_id}', which is played by "
                                f"'{role_object_type}'"
                            ),
                            rule_id="semantic:op-term-type-compat",
                        )
                    )
    return issues


def _rule_op_effect_ground(doc: dict[str, Any]) -> list[ValidationIssue]:
    """An ``assert`` effect binds EVERY declared role of its fact type.

    ``retract`` deliberately admits wildcards — an omitted role means "every
    value" — but an ``assert`` with an unbound role does not name a fact, it
    names a fact shape, and there is nothing to add to the population. Unbound
    VARIABLES are ``semantic:op-term-ref``'s finding at every site including
    this one, so a term naming no parameter is reported once, there."""
    issues: list[ValidationIssue] = []
    roles_by_fact_type = _fact_type_roles(doc)
    for path, operation in _iter_operations(doc):
        for index, effect in enumerate(operation.get("effects") or []):
            atom = effect.get("assert") if isinstance(effect, dict) else None
            if not isinstance(atom, dict):
                continue
            fact_type_id = str(atom.get("fact_type"))
            declared = roles_by_fact_type.get(fact_type_id)
            # An undeclared fact type is semantic:op-atom-ref's finding.
            if declared is None:
                continue
            bind = atom_bind(atom)
            bound = set(map(str, bind)) if isinstance(bind, dict) else set()
            missing = declared - bound
            if missing:
                issues.append(
                    ValidationIssue(
                        path=f"{path}.effects[{index}].assert",
                        message=(
                            f"assert on '{fact_type_id}' leaves role(s) "
                            f"{sorted(missing)} unbound — an asserted fact must be ground"
                        ),
                        rule_id="semantic:op-effect-ground",
                    )
                )
    return issues


def _rule_op_create_param(doc: dict[str, Any]) -> list[ValidationIssue]:
    """A ``create`` mints exactly one declared parameter, of that parameter's
    own declared type, and that parameter is not referenced by any
    precondition.

    The precondition clause is the substantive one: preconditions are evaluated
    in the state BEFORE the step, where a created instance does not exist, so a
    precondition mentioning it can never hold and the operation could never
    fire. Two ``create`` effects on one parameter are refused for the same
    reason a name is a name."""
    issues: list[ValidationIssue] = []
    for path, operation in _iter_operations(doc):
        parameters = _operation_parameters(operation)
        created: set[str] = set()
        for index, effect in enumerate(operation.get("effects") or []):
            create = effect.get("create") if isinstance(effect, dict) else None
            if not isinstance(create, dict):
                continue
            param = str(create.get("param"))
            location = f"{path}.effects[{index}].create"

            def refuse(message: str, where: str = location) -> None:
                issues.append(
                    ValidationIssue(
                        path=where,
                        message=message,
                        rule_id="semantic:op-create-param",
                    )
                )

            if param not in parameters:
                refuse(
                    f"create mints '{param}', which is not a declared parameter of "
                    f"operation '{operation.get('id')}' (declared: {sorted(parameters)})"
                )
                continue
            if param in created:
                refuse(f"parameter '{param}' is created more than once")
            created.add(param)
            declared_type = parameters[param]
            if str(create.get("object_type")) != declared_type:
                refuse(
                    f"create mints '{param}' as '{create.get('object_type')}' but the "
                    f"parameter is declared '{declared_type}'"
                )
        if not created:
            continue
        for index, obligation in enumerate(operation.get("preconditions") or []):
            for atom_index, atom in enumerate(obligation.get("require") or []):
                bind = atom_bind(atom)
                if not isinstance(bind, dict):
                    continue
                for role_name, term in bind.items():
                    variable = _variable_name(term)
                    if variable in created:
                        issues.append(
                            ValidationIssue(
                                path=(
                                    f"{path}.preconditions[{index}].require[{atom_index}]"
                                    f".bind[{role_name}]"
                                ),
                                message=(
                                    f"precondition binds '{variable}', which this operation "
                                    f"creates — a created instance does not exist in the "
                                    f"pre-state, so the precondition can never hold"
                                ),
                                rule_id="semantic:op-create-param",
                            )
                        )
    return issues


def _rule_op_create_ref_mode(doc: dict[str, Any]) -> list[ValidationIssue]:
    """A ``create`` targets an entity type identified by a value the caller can
    supply — reference mode ``popular`` or ``general``, **inherited or its own**.

    A ``unit-based`` type is identified by a measured quantity, an ``external``
    type by the fact roles it plays, and a value type is not created at all. For
    each of those, "mint a fresh instance and let the caller supply its
    identifier" has no meaning: there is no identifier to supply.

    The test is "does an identifying value type resolve", not "does this entry
    carry a ``reference`` block". A subtype declaring ``inherits_reference:
    true`` has no local ``reference`` and IS creatable — it is identified by the
    value type its supertype names, which is what the format says such a subtype
    inherits. Reading the local block only would refuse every creatable subtype
    in the language.

    Resolution goes through ``popvalidate._resolve_reference``, the ONE
    reference-scheme walk this repository has (``synth/pool.py`` states the
    rule) — including its ``seen`` set, so a subtype cycle resolves to None
    rather than recursing forever. The import is deferred because
    ``popvalidate`` imports this module at module scope."""
    from gnd.universe import identifying_id as _identifying_id
    from gnd.universe import resolve_reference as _resolve_reference

    issues: list[ValidationIssue] = []
    object_types = {
        str(ot.get("id")): ot for ot in doc.get("object_types") or [] if ot.get("id") is not None
    }
    parents = _supertype_parents(doc)
    for path, operation in _iter_operations(doc):
        for index, effect in enumerate(operation.get("effects") or []):
            create = effect.get("create") if isinstance(effect, dict) else None
            if not isinstance(create, dict):
                continue
            object_type_id = str(create.get("object_type"))
            object_type = object_types.get(object_type_id)
            # An undeclared type is semantic:op-create-param's finding via the
            # parameter it must agree with.
            if object_type is None:
                continue
            identified_by = (
                None
                if object_type.get("kind") == "value"
                else _resolve_reference(
                    object_type_id, object_types, parents, set(), _identifying_id
                )
            )
            if identified_by is None:
                declared = (object_type.get("reference") or {}).get("mode")
                inherited = " (nor through any supertype)" if object_type.get("subtype_of") else ""
                issues.append(
                    ValidationIssue(
                        path=f"{path}.effects[{index}].create",
                        message=(
                            f"create targets '{object_type_id}', which resolves to no "
                            f"identifying value type{inherited} — its declared reference "
                            f"mode is {declared!r}, and only 'popular' and 'general' "
                            f"entity types can be minted with a caller-supplied identifier"
                        ),
                        rule_id="semantic:op-create-ref-mode",
                    )
                )
    return issues


def _rule_op_obligation_ids_distinct(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Precondition and dynamic-rule ids are distinct WITHIN one operation.

    They are operation-scoped on purpose and do not join the model-wide id
    namespace: an obligation is addressed as ``operation.obligation``, so two
    operations may each carry a ``pre_approved`` without ambiguity, and
    requiring globally unique obligation ids would make every operation's
    internal naming depend on every other operation's."""
    issues: list[ValidationIssue] = []
    for path, operation in _iter_operations(doc):
        seen: set[str] = set()
        for kind, index, obligation in _iter_operation_obligations(operation):
            obligation_id = obligation.get("id")
            if obligation_id is None:
                continue
            if str(obligation_id) in seen:
                issues.append(
                    ValidationIssue(
                        path=f"{path}.{kind}[{index}]",
                        message=(
                            f"operation '{operation.get('id')}' declares obligation id "
                            f"'{obligation_id}' more than once across preconditions and "
                            f"dynamic_rules"
                        ),
                        rule_id="semantic:op-obligation-ids-distinct",
                    )
                )
            seen.add(str(obligation_id))
    return issues


#: The ``imported`` provenance block's required fields. The meta-schema
#: requires their PRESENCE and a nonzero length; this list is what the semantic
#: rule re-reads to reject a value that is present, string-typed, and blank —
#: which the schema's ``minLength: 1`` accepts and no reader can act on.
IMPORTED_PROVENANCE_FIELDS = ("framework", "artifact", "commit", "sha256", "anchor")


def _iter_provenance_bearing(doc: dict[str, Any]):
    """Yield ``(path, element)`` for everything carrying source/status/provenance
    — every active constraint, every operation, and every operation obligation.

    One iteration for one policy. ``provenance-and-modality.md`` states the
    source taxonomy, the per-source provenance shapes and the source/status
    consistency rule once, for all of them; a rule that walked only constraints
    would enforce that single statement in one of the three places it governs.
    """
    yield from _iter_constraints(doc)
    for path, operation in _iter_operations(doc):
        yield path, operation
        for kind, index, obligation in _iter_operation_obligations(operation):
            yield f"{path}.{kind}[{index}]", obligation


def _provenance_bearing_label(element: dict[str, Any]) -> str:
    """How to name a provenance-bearing element in a message.

    A constraint is named by its ``type`` (``uniqueness constraint``); an
    operation and an obligation have no ``type`` key and are named by their
    ``id``. Falling back to ``None constraint`` would have reported an
    operation's defect as a constraint's."""
    family = element.get("type")
    if family is not None:
        return f"{family} constraint"
    identifier = element.get("id")
    return f"operation claim '{identifier}'" if identifier is not None else "operation claim"


def _rule_imported_provenance(doc: dict[str, Any]) -> list[ValidationIssue]:
    """An ``imported`` claim carries a complete, non-blank verbatim anchor.

    ``imported`` is the one source whose evidence lives OUTSIDE this repository's
    model: it names another framework's artifact, the commit it was read at, that
    artifact's digest, and the verbatim text the claim was taken from. A blank
    anchor makes the import unverifiable while still looking sourced, which is
    strictly worse than an honest ``llm-inferred``."""
    issues: list[ValidationIssue] = []
    for path, element in _iter_provenance_bearing(doc):
        if element.get("source") != "imported":
            continue
        provenance = element.get("provenance")
        if not isinstance(provenance, dict):
            continue  # absent provenance is layer 1's rejection
        for field in IMPORTED_PROVENANCE_FIELDS:
            value = provenance.get(field)
            if not isinstance(value, str) or not value.strip():
                issues.append(
                    ValidationIssue(
                        path=f"{path}.provenance.{field}",
                        message=(
                            f"imported claim has a missing or blank '{field}' — an "
                            f"import that cannot be resolved back to verbatim artifact "
                            f"bytes is not evidence"
                        ),
                        rule_id="semantic:imported-provenance",
                    )
                )
    return issues


def _rule_imported_confirmed_reviewed(doc: dict[str, Any]) -> list[ValidationIssue]:
    """A9: an ``imported`` claim may not present itself as ``confirmed`` without
    naming the review that confirmed it.

    Confirmation is what flips the D-03 default from deontic to alethic, i.e.
    what turns an imported claim into a hard gate. Requiring ``reviewed_in``
    keeps that flip attributable to a review a reader can go and find."""
    issues: list[ValidationIssue] = []
    for path, element in _iter_provenance_bearing(doc):
        if element.get("source") != "imported" or element.get("status") != "confirmed":
            continue
        provenance = element.get("provenance")
        reviewed_in = provenance.get("reviewed_in") if isinstance(provenance, dict) else None
        if not isinstance(reviewed_in, str) or not reviewed_in.strip():
            issues.append(
                ValidationIssue(
                    path=f"{path}.provenance.reviewed_in",
                    message=(
                        "imported claim is 'confirmed' without a 'reviewed_in' record — "
                        "an unreviewed import may not present itself as confirmed (A9)"
                    ),
                    rule_id="semantic:imported-confirmed-reviewed",
                )
            )
    return issues


def _internal_uniqueness_keys(fact_type: dict[str, Any]) -> list[set[str]]:
    return [
        {str(role) for role in constraint.get("roles") or []}
        for constraint in fact_type.get("constraints") or []
        if constraint.get("type") == "uniqueness"
        and constraint.get("scope", "internal") == "internal"
    ]


def dynamic_subject_is_functional(
    subject: dict[str, Any], fact_types: list[dict[str, Any]]
) -> bool | None:
    """Do the roles the SUBJECT BINDS determine at most one value?

    "Old versus new" presupposes a single old value, and an internal uniqueness
    constraint is what proves there is one -- but only if the subject actually
    binds that constraint's roles. A key over (a, b) proves the FACT TYPE
    functional in (a, b); it proves nothing about a subject that binds only `a`,
    which can match two facts carrying two different values.

    An earlier version asked whether some key existed among the fact type's
    non-value roles and never looked at the binding, so such a subject was
    called functional and the evaluator compared against whichever fact came
    first -- the same fact SET producing a finding in one order and none in the
    other. Found by adversarial review with exactly that reproduction.

    ``None`` means the question does not arise: an undeclared fact type or value
    role is ``semantic:op-atom-ref``'s finding, not this one's.

    Extracted so the authoring-time WARNING and the evaluation-time ``unchecked``
    verdict cannot disagree: they are the same question asked at two moments,
    and two copies of the answer is how they would drift.
    """
    fact_type_id = str(subject.get("fact_type"))
    value_role = str(subject.get("value_role"))
    bound = {str(role) for role in atom_bind(subject)} - {value_role}
    for fact_type in fact_types:
        if str(fact_type.get("id")) != fact_type_id:
            continue
        declared = {str(role.get("role_name")) for role in fact_type.get("roles") or []}
        if value_role not in declared:
            return None
        return any(key <= bound for key in _internal_uniqueness_keys(fact_type))
    return None


def _rule_op_dynamic_functional(doc: dict[str, Any]) -> list[ValidationIssue]:
    """WARNING: a dynamic rule's subject is not PROVABLY functional.

    "Old versus new value" presupposes that the bound roles determine at most
    one value — otherwise there is no single old value to compare against. The
    model proves this with an internal uniqueness constraint over exactly the
    non-value roles. Severity is warning, not error: the evaluator (Phase 2)
    reports such a rule ``unchecked`` rather than guessing, so the model still
    loads and the author learns at authoring time what the checker will refuse
    to decide at check time."""
    issues: list[ValidationIssue] = []
    roles_by_fact_type = _fact_type_roles(doc)
    uniqueness_by_fact_type: dict[str, list[set[str]]] = {}
    for fact_type in doc.get("fact_types") or []:
        keys = [
            {str(role) for role in constraint.get("roles") or []}
            for constraint in fact_type.get("constraints") or []
            if constraint.get("type") == "uniqueness"
            and constraint.get("scope", "internal") == "internal"
        ]
        uniqueness_by_fact_type[str(fact_type.get("id"))] = keys
    for path, operation in _iter_operations(doc):
        for index, rule in enumerate(operation.get("dynamic_rules") or []):
            subject = rule.get("subject")
            if not isinstance(subject, dict):
                continue
            fact_type_id = str(subject.get("fact_type"))
            declared = roles_by_fact_type.get(fact_type_id)
            # An undeclared fact type or role is semantic:op-atom-ref's finding.
            if declared is None or str(subject.get("value_role")) not in declared:
                continue
            determinant = declared - {str(subject.get("value_role"))}
            if dynamic_subject_is_functional(subject, doc.get("fact_types") or []) is False:
                issues.append(
                    ValidationIssue(
                        path=f"{path}.dynamic_rules[{index}].subject",
                        message=(
                            f"dynamic rule '{rule.get('id')}' compares old and new values of "
                            f"'{subject.get('value_role')}' on '{fact_type_id}', which no "
                            f"internal uniqueness constraint over {sorted(determinant)} "
                            f"proves functional — the rule will evaluate 'unchecked'"
                        ),
                        rule_id="semantic:op-dynamic-functional",
                        severity="warning",
                    )
                )
    return issues


def _rule_op_dynamic_untouched(doc: dict[str, Any]) -> list[ValidationIssue]:
    """WARNING: a dynamic rule whose subject its own operation never touches.

    A dynamic rule constrains a transition the operation MAKES. If none of the
    operation's effects touch the rule's subject fact type, the rule can never
    fire -- the evaluator judges only transitions the step actually made, so it
    reports nothing, forever.

    The corpus model carries the case this rule exists for: an operation that
    submits an expense to Workday declares that the approval chain's spending
    threshold must strictly increase, and its effects never mention that
    threshold. Read literally, every submission would warn that it failed to
    raise a limit it never went near; read correctly, nothing is reported and
    the author never learns their rule is decorative. Hence a warning at
    authoring time, where it can still be fixed or deleted.

    Warning, never an error: it refuses no model that loads today, and an
    operation may legitimately be mid-authoring.
    """
    issues: list[ValidationIssue] = []
    classifications = {row.fact_type: row for row in derivation_classifications(doc)}
    for path, operation in _iter_operations(doc):
        touched: set[str] = set()
        for effect in operation.get("effects") or []:
            if not isinstance(effect, dict):
                continue
            for verb in ("assert", "retract"):
                atom = effect.get(verb)
                if isinstance(atom, dict) and atom.get("fact_type"):
                    touched.add(str(atom["fact_type"]))
        for index, rule in enumerate(operation.get("dynamic_rules") or []):
            subject = rule.get("subject")
            if not isinstance(subject, dict):
                continue
            fact_type_id = str(subject.get("fact_type"))
            if fact_type_id in touched:
                continue
            classification = classifications.get(fact_type_id)
            if classification is not None and touched.intersection(
                classification.asserted_dependencies
            ):
                continue
            issues.append(
                ValidationIssue(
                    path=f"{path}.dynamic_rules[{index}].subject",
                    message=(
                        f"dynamic rule '{rule.get('id')}' takes '{fact_type_id}' as its "
                        f"subject, which no effect of '{operation.get('id')}' touches, so "
                        f"the rule can never fire and the evaluator will report nothing"
                    ),
                    rule_id="semantic:op-dynamic-untouched",
                    severity="warning",
                )
            )
    return issues


def _rule_op_modality_policy(doc: dict[str, Any]) -> list[ValidationIssue]:
    """WARNING: D-03 extended to operation obligations — an UNCONFIRMED
    llm-inferred or common-sense precondition or dynamic rule claiming alethic
    modality gets the same warning its constraint counterpart gets.

    A separate rule rather than a widened ``semantic:modality-policy`` because
    the two iterate different documents' shapes and each rule in this loader
    emits exactly one stable rule id; a caller filtering on the constraint rule
    would otherwise silently start receiving operation findings."""
    issues: list[ValidationIssue] = []
    for path, operation in _iter_operations(doc):
        for kind, index, obligation in _iter_operation_obligations(operation):
            if (
                obligation.get("source") in ("llm-inferred", "common-sense")
                and obligation.get("status") == "proposed"
                and obligation.get("modality") == "alethic"
            ):
                issues.append(
                    ValidationIssue(
                        path=f"{path}.{kind}[{index}]",
                        message=(
                            f"unconfirmed {obligation.get('source')} obligation "
                            f"'{obligation.get('id')}' carries modality 'alethic' — "
                            f"unconfirmed llm-inferred/common-sense claims default to "
                            f"deontic until user-confirmed (D-03)"
                        ),
                        rule_id="semantic:op-modality-policy",
                        severity="warning",
                    )
                )
    return issues


# --- layer-2 helpers and rules for guarded constraints ---


def _iter_guarded_constraints(doc: Any):
    """Yield ``(path, constraint)`` for every active top-level guarded constraint."""
    if not isinstance(doc, dict):
        return
    constraints = doc.get("constraints")
    if not isinstance(constraints, list):
        return
    for index, constraint in enumerate(constraints):
        if isinstance(constraint, dict) and constraint.get("type") == "guarded":
            yield f"$.constraints[{index}]", constraint


def _iter_guarded_atoms(constraint: Any):
    """Yield every atom in a guarded antecedent or consequent."""
    if not isinstance(constraint, dict):
        return
    antecedent = constraint.get("antecedent")
    if isinstance(antecedent, list):
        for index, atom in enumerate(antecedent):
            yield f".antecedent[{index}]", atom
    consequent = constraint.get("consequent")
    if not isinstance(consequent, dict):
        return
    for kind in ("atom", "absence"):
        if kind in consequent:
            yield f".consequent.{kind}", consequent.get(kind)
    exists = consequent.get("exists")
    if isinstance(exists, dict) and isinstance(exists.get("atoms"), list):
        for index, atom in enumerate(exists["atoms"]):
            yield f".consequent.exists.atoms[{index}]", atom


def _iter_guarded_consequent_terms(constraint: Any):
    """Yield ``(suffix, term)`` for every term used by a guarded consequent."""
    if not isinstance(constraint, dict):
        return
    consequent = constraint.get("consequent")
    if not isinstance(consequent, dict):
        return
    for kind in ("atom", "absence"):
        atom = consequent.get(kind)
        if not isinstance(atom, dict):
            continue
        bind = atom_bind(atom)
        if not isinstance(bind, dict):
            continue
        for role_name, term in bind.items():
            yield f".consequent.{kind}.bind[{role_name}]", term
    comparison = consequent.get("comparison")
    if isinstance(comparison, dict):
        for side in ("left", "right"):
            if side in comparison:
                yield f".consequent.comparison.{side}", comparison.get(side)


def _rule_guarded_term_ref(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Every guarded atom names a declared fact type and only its declared roles."""
    issues: list[ValidationIssue] = []
    roles_by_fact_type = _fact_type_roles(doc) if isinstance(doc, dict) else {}
    for path, constraint in _iter_guarded_constraints(doc):
        for suffix, atom in _iter_guarded_atoms(constraint):
            issues.extend(
                _atom_reference_issues(
                    f"{path}{suffix}",
                    atom,
                    roles_by_fact_type,
                    rule_id="semantic:guarded-term-ref",
                )
            )
    return issues


def _rule_guarded_role_claim(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Every guarded atom binds every role declared by its fact type."""
    issues: list[ValidationIssue] = []
    roles_by_fact_type = _fact_type_roles(doc) if isinstance(doc, dict) else {}
    for path, constraint in _iter_guarded_constraints(doc):
        for suffix, atom in _iter_guarded_atoms(constraint):
            if not isinstance(atom, dict):
                continue
            fact_type_id = str(atom.get("fact_type"))
            declared = roles_by_fact_type.get(fact_type_id)
            if declared is None:
                continue
            bind = atom_bind(atom)
            named = {str(name) for name in bind} if isinstance(bind, dict) else set()
            missing = declared - named
            if missing:
                issues.append(
                    ValidationIssue(
                        path=f"{path}{suffix}",
                        message=(
                            f"atom for fact type '{fact_type_id}' omits declared roles "
                            f"{sorted(missing)}"
                        ),
                        rule_id="semantic:guarded-role-claim",
                    )
                )
    return issues


def _rule_guarded_consequent_ground(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Every guarded consequent variable is bound by its antecedent or exists atom."""
    issues: list[ValidationIssue] = []
    for path, constraint in _iter_guarded_constraints(doc):
        bound: set[str] = set()
        antecedent = constraint.get("antecedent")
        if isinstance(antecedent, list):
            for atom in antecedent:
                bind = atom_bind(atom)
                if not isinstance(bind, dict):
                    continue
                bound.update(
                    variable
                    for term in bind.values()
                    if (variable := _variable_name(term)) is not None
                )
        consequent = constraint.get("consequent")
        exists = consequent.get("exists") if isinstance(consequent, dict) else None
        exists_bound: set[str] = set()
        if isinstance(exists, dict):
            for atom in exists.get("atoms") or []:
                bind = atom_bind(atom)
                if isinstance(bind, dict):
                    exists_bound.update(
                        variable
                        for term in bind.values()
                        if (variable := _variable_name(term)) is not None
                    )
        allowed = bound | exists_bound
        grounding_message = (
            "are not bound by an antecedent or positive exists atom"
            if isinstance(exists, dict)
            else "are not introduced by an antecedent bind"
        )
        for suffix, term in _iter_guarded_consequent_terms(constraint):
            unbound = set(term_variables(term)) - allowed
            if unbound:
                issues.append(
                    ValidationIssue(
                        path=f"{path}{suffix}",
                        message=(
                            f"consequent variables {sorted('$' + item for item in unbound)} "
                            f"{grounding_message}"
                        ),
                        rule_id="semantic:guarded-consequent-ground",
                    )
                )
    return issues


def _guarded_nested_function_variables(term: Any) -> set[str]:
    """Variables occurring below an exact-term function node."""
    found: set[str] = set()
    stack: list[tuple[Any, bool]] = [(term, False)]
    seen = 0
    while stack and seen < DEFAULT_LIMITS.max_nodes:
        value, nested = stack.pop()
        seen += 1
        if isinstance(value, str) and value.startswith("$") and nested:
            found.add(value[1:])
        elif is_function_term(value):
            arguments = value.get("args")
            if isinstance(arguments, list):
                stack.extend((child, True) for child in reversed(arguments))
    return found


def _rule_guarded_exists_range(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Exact-function variables must be positively range-restricted."""
    issues: list[ValidationIssue] = []
    for path, constraint in _iter_guarded_constraints(doc):
        consequent = constraint.get("consequent")
        exists = consequent.get("exists") if isinstance(consequent, dict) else None
        if not isinstance(exists, dict):
            continue
        bound: set[str] = set()
        for atom in [*(constraint.get("antecedent") or []), *(exists.get("atoms") or [])]:
            bind = atom_bind(atom)
            if isinstance(bind, dict):
                bound.update(
                    variable
                    for term in bind.values()
                    if (variable := _variable_name(term)) is not None
                )
        unsafe = {
            variable
            for comparison in exists.get("where") or []
            if isinstance(comparison, dict)
            for side in ("left", "right")
            for variable in _guarded_nested_function_variables(comparison.get(side))
            if variable not in bound
        }
        if unsafe:
            issues.append(
                ValidationIssue(
                    path=f"{path}.consequent.exists",
                    message=(
                        "exact where-term variables must occur in an antecedent or positive "
                        f"exists atom: {sorted('$' + item for item in unsafe)}"
                    ),
                    rule_id="semantic:guarded-exists-range",
                )
            )
    return issues


def _rule_guarded_exists_where_bound(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Every exists.where variable is antecedent-bound or positively exists-bound."""
    issues: list[ValidationIssue] = []
    for path, constraint in _iter_guarded_constraints(doc):
        consequent = constraint.get("consequent")
        exists = consequent.get("exists") if isinstance(consequent, dict) else None
        if not isinstance(exists, dict):
            continue
        bound: set[str] = set()
        for atom in [*(constraint.get("antecedent") or []), *(exists.get("atoms") or [])]:
            bind = atom_bind(atom)
            if isinstance(bind, dict):
                bound.update(
                    variable
                    for term in bind.values()
                    if (variable := _variable_name(term)) is not None
                )
        for index, comparison in enumerate(exists.get("where") or []):
            if not isinstance(comparison, dict):
                continue
            variables = set(term_variables(comparison.get("left"))) | set(term_variables(comparison.get("right")))
            nested = _guarded_nested_function_variables(comparison.get("left")) | _guarded_nested_function_variables(comparison.get("right"))
            variables -= nested
            unbound = variables - bound
            if unbound:
                issues.append(
                    ValidationIssue(
                        path=f"{path}.consequent.exists.where[{index}]",
                        message=(
                            "where variables must be introduced by an antecedent or positive "
                            f"exists atom: {sorted('$' + item for item in unbound)}"
                        ),
                        rule_id="semantic:guarded-exists-where-bound",
                    )
                )
    return issues


def _guarded_primitives_compatible(left: str, right: str) -> bool:
    """Whether two resolved primitive domains admit one comparison."""
    numeric = {"Integer", "Float", "Number"}
    return left == right or (left in numeric and right in numeric)


def _guarded_literal_matches_primitive(primitive: str, literal: Any) -> bool:
    """Kind-level compatibility between a resolved primitive and a literal.

    Deliberately NOT a format check: the checker accepts any string for the
    string-serialized primitives (Date, DateTime, Binary) and compares
    lexically, so layer 2 refusing a non-ISO date literal would reject a
    model whose comparison the checker evaluates -- the divergence the spec's
    relation table forbids. Content validation of literals stays out of scope
    (003-1, carried)."""
    if isinstance(literal, bool):
        return primitive == "Boolean"
    if isinstance(literal, (int, float)):
        return primitive in ("Integer", "Float", "Number")
    if isinstance(literal, str):
        return primitive in ("String", "Date", "DateTime", "Binary")
    return False


def _guarded_literal_kinds_compatible(left: Any, right: Any) -> bool:
    """Whether two schema scalar literals inhabit compatible scalar kinds."""
    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool)
    if isinstance(left, (int, float)) or isinstance(right, (int, float)):
        return (
            isinstance(left, (int, float))
            and not isinstance(left, bool)
            and isinstance(right, (int, float))
            and not isinstance(right, bool)
        )
    return isinstance(left, str) and isinstance(right, str)


def _rule_guarded_comparison_type(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Every guarded comparison has compatible resolved operand types."""
    # Local import avoids the module-import cycle: popvalidate imports Model and
    # the shared semantic helpers from this module. Resolution still has exactly
    # one implementation, in gnd.popvalidate.
    from gnd.universe import resolve_primitive

    issues: list[ValidationIssue] = []
    role_types = _role_object_types(doc) if isinstance(doc, dict) else {}
    object_types = (
        [item for item in doc.get("object_types") or [] if isinstance(item, dict)]
        if isinstance(doc, dict)
        else []
    )
    primitive_model = Model.model_construct(object_types=object_types)
    primitive_cache: dict[str, str | None] = {}

    def primitive_for(object_type_id: str) -> str | None:
        if object_type_id not in primitive_cache:
            primitive_cache[object_type_id] = resolve_primitive(object_type_id, primitive_model)
        return primitive_cache[object_type_id]

    for path, constraint in _iter_guarded_constraints(doc):
        consequent = constraint.get("consequent")
        comparison = consequent.get("comparison") if isinstance(consequent, dict) else None
        if not isinstance(comparison, dict) or not {"left", "right"} <= comparison.keys():
            continue

        variable_primitives: dict[str, list[str]] = {}
        antecedent = constraint.get("antecedent")
        if isinstance(antecedent, list):
            for atom in antecedent:
                if not isinstance(atom, dict):
                    continue
                fact_type_id = str(atom.get("fact_type"))
                bind = atom_bind(atom)
                if not isinstance(bind, dict):
                    continue
                for role_name, term in bind.items():
                    variable = _variable_name(term)
                    object_type_id = role_types.get(fact_type_id, {}).get(str(role_name))
                    if variable is None or object_type_id is None:
                        continue
                    primitive = primitive_for(object_type_id)
                    if primitive is not None:
                        variable_primitives.setdefault(variable, []).append(primitive)

        left = comparison.get("left")
        right = comparison.get("right")
        collapsed_primitives = {
            variable: (
                next(iter(set(values)))
                if len(set(values)) == 1
                else "Number"
                if set(values) <= NUMERIC_PRIMITIVES
                else ""
            )
            for variable, values in variable_primitives.items()
        }
        if isinstance(left, dict) or isinstance(right, dict):
            left_analysis = analyze_term(left, collapsed_primitives, limits=DEFAULT_LIMITS)
            right_analysis = analyze_term(right, collapsed_primitives, limits=DEFAULT_LIMITS)
            for side, analysis in (("left", left_analysis), ("right", right_analysis)):
                if analysis.issue is not None:
                    issues.append(
                        ValidationIssue(
                            path=f"{path}.consequent.comparison.{side}",
                            message=f"guarded term is invalid: {analysis.issue}",
                            rule_id=analysis.issue,
                        )
                    )
            if (
                left_analysis.issue is None
                and right_analysis.issue is None
                and left_analysis.primitive is not None
                and right_analysis.primitive is not None
                and not _guarded_primitives_compatible(
                    left_analysis.primitive, right_analysis.primitive
                )
            ):
                issues.append(
                    ValidationIssue(
                        path=f"{path}.consequent.comparison",
                        message=(
                            "guarded comparison operands have incompatible resolved "
                            f"types: {left_analysis.primitive!r} and "
                            f"{right_analysis.primitive!r}"
                        ),
                        rule_id="semantic:guarded-comparison-type",
                    )
                )
            continue
        if any(
            isinstance(operand, float) and not math.isfinite(operand) for operand in (left, right)
        ):
            continue
        left_variable = _variable_name(left)
        right_variable = _variable_name(right)
        left_primitives = variable_primitives.get(left_variable, []) if left_variable else []
        right_primitives = variable_primitives.get(right_variable, []) if right_variable else []

        compatible: bool | None
        if left_variable is not None and right_variable is not None:
            if not left_primitives or not right_primitives:
                compatible = None
            else:
                compatible = all(
                    any(_guarded_primitives_compatible(item, other) for other in right_primitives)
                    for item in left_primitives
                ) and all(
                    any(_guarded_primitives_compatible(item, other) for other in left_primitives)
                    for item in right_primitives
                )
        elif left_variable is not None:
            compatible = (
                all(
                    _guarded_literal_matches_primitive(primitive, right)
                    for primitive in left_primitives
                )
                if left_primitives
                else None
            )
        elif right_variable is not None:
            compatible = (
                all(
                    _guarded_literal_matches_primitive(primitive, left)
                    for primitive in right_primitives
                )
                if right_primitives
                else None
            )
        else:
            compatible = _guarded_literal_kinds_compatible(left, right)

        if compatible is False:
            issues.append(
                ValidationIssue(
                    path=f"{path}.consequent.comparison",
                    message=(
                        "guarded comparison operands have incompatible resolved "
                        f"types: {left!r} and {right!r}"
                    ),
                    rule_id="semantic:guarded-comparison-type",
                )
            )
    return issues


def _rule_guarded_exists_where_type(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Every exists.where comparison has compatible resolved term types."""
    from gnd.universe import resolve_primitive

    issues: list[ValidationIssue] = []
    role_types = _role_object_types(doc) if isinstance(doc, dict) else {}
    object_types = (
        [item for item in doc.get("object_types") or [] if isinstance(item, dict)]
        if isinstance(doc, dict)
        else []
    )
    primitive_model = Model.model_construct(object_types=object_types)
    primitive_cache: dict[str, str | None] = {}

    def primitive_for(object_type_id: str) -> str | None:
        if object_type_id not in primitive_cache:
            primitive_cache[object_type_id] = resolve_primitive(object_type_id, primitive_model)
        return primitive_cache[object_type_id]

    for path, constraint in _iter_guarded_constraints(doc):
        consequent = constraint.get("consequent")
        exists = consequent.get("exists") if isinstance(consequent, dict) else None
        if not isinstance(exists, dict):
            continue
        variable_primitives: dict[str, list[str]] = {}
        for atom in [*(constraint.get("antecedent") or []), *(exists.get("atoms") or [])]:
            if not isinstance(atom, dict):
                continue
            fact_type_id = str(atom.get("fact_type"))
            bind = atom_bind(atom)
            if not isinstance(bind, dict):
                continue
            for role_name, term in bind.items():
                variable = _variable_name(term)
                object_type_id = role_types.get(fact_type_id, {}).get(str(role_name))
                if variable is None or object_type_id is None:
                    continue
                primitive = primitive_for(object_type_id)
                if primitive is not None:
                    variable_primitives.setdefault(variable, []).append(primitive)
        collapsed = {
            variable: (
                next(iter(set(values)))
                if len(set(values)) == 1
                else "Number"
                if set(values) <= NUMERIC_PRIMITIVES
                else ""
            )
            for variable, values in variable_primitives.items()
        }
        for index, comparison in enumerate(exists.get("where") or []):
            if not isinstance(comparison, dict) or not {"left", "right"} <= comparison.keys():
                continue
            left, right = comparison.get("left"), comparison.get("right")
            analyses = (
                analyze_term(left, collapsed, limits=DEFAULT_LIMITS),
                analyze_term(right, collapsed, limits=DEFAULT_LIMITS),
            )
            for side, analysis in zip(("left", "right"), analyses, strict=True):
                if analysis.issue is not None:
                    issues.append(
                        ValidationIssue(
                            path=f"{path}.consequent.exists.where[{index}].{side}",
                            message=f"guarded exists term is invalid: {analysis.issue}",
                            rule_id=analysis.issue,
                        )
                    )
            if any(analysis.issue is not None for analysis in analyses):
                continue
            left_primitive, right_primitive = analyses[0].primitive, analyses[1].primitive
            if (
                left_primitive is not None
                and right_primitive is not None
                and not _guarded_primitives_compatible(left_primitive, right_primitive)
            ):
                issues.append(
                    ValidationIssue(
                        path=f"{path}.consequent.exists.where[{index}]",
                        message=(
                            "guarded exists comparison operands have incompatible resolved "
                            f"types: {left_primitive!r} and {right_primitive!r}"
                        ),
                        rule_id="semantic:guarded-exists-where-type",
                    )
                )
    return issues


# --- layer-2 helpers and rules for ORM++ structured derivation rules ---------
#
# Normative semantics has ONE home: gnd-orm-core/references/representation-format.md,
# "Derived fact types". Nothing here restates it; these functions implement it.
#
# The registration order at the bottom of this block IS the refusal precedence
# r2 A11 fixes -- reference errors, then shape errors, then graph errors -- so a
# document carrying two defects reports the one that explains the other first.
# One walk over both element kinds (standing rule 4): fact types get the full
# policy, object types get `_rule_derivation_structured_on_object_type`, which
# refuses them by decision (D-P1.1) rather than by omission.

#: The keys the structured arm admits. Aggregation, arithmetic, disjunction and
#: value invention are refused by not existing here -- the refusal names the key
#: it found, which a layer-1 `oneOf` failure could not do.
_DERIVATION_RULE_KEYS = frozenset({"body", "negate", "aggregate", "where", "head"})


def iter_derivation_clauses(rule: Any) -> tuple[dict[str, Any], ...]:
    """Present legacy sugar and every explicit clause without changing model bytes.

    Malformed input is deliberately total; the schema and shape rule own its
    refusal. A clause-local where list follows the root comparisons.
    """
    if not isinstance(rule, dict):
        return ()
    if "clauses" not in rule:
        return (rule,)
    clauses = rule.get("clauses")
    if not isinstance(clauses, list):
        return ()
    shared = {key: value for key, value in rule.items() if key != "clauses"}
    result = []
    for clause in clauses:
        if not isinstance(clause, dict):
            result.append(dict(shared))
            continue
        effective = {**shared, **clause}
        if isinstance(shared.get("where"), list) and isinstance(clause.get("where"), list):
            effective["where"] = [*shared["where"], *clause["where"]]
        result.append(effective)
    return tuple(result)


def _is_structured_rule(rule: Any) -> bool:
    """Whether a declared rule takes the object arm. A string stays opaque."""
    return isinstance(rule, dict)


def _iter_structured_fact_derivations(doc: Any):
    """Yield ``(path, fact_type, clause)`` for every structured clause."""
    if not isinstance(doc, dict):
        return
    fact_types = doc.get("fact_types")
    if not isinstance(fact_types, list):
        return
    for index, fact_type in enumerate(fact_types):
        if not isinstance(fact_type, dict):
            continue
        rule = fact_type.get("derivation_rule")
        if _is_structured_rule(rule):
            path = (
                f"$.fact_types.{_derivation_id(fact_type.get('id'))}.derivation_rule"
                if "clauses" in rule else f"$.fact_types[{index}].derivation_rule"
            )
            for clause_index, clause in enumerate(iter_derivation_clauses(rule)):
                suffix = f".clauses[{clause_index}]" if "clauses" in rule else ""
                yield path + suffix, fact_type, clause


#: Atoms yielded by :func:`_derivation_atoms` since interpreter start.
_DERIVATION_ATOM_VISITS = 0

#: The operations whose complexity T1.18 actually bounds: every component
#: comparison in :func:`body_components` and every candidate check in the
#: topological walk. Counting ITERATOR YIELDS instead (the first attempt) made
#: that row unfalsifiable -- an implementation could rescan its groups
#: quadratically while yielding each atom exactly once, and the bound would not
#: move. A reviewer measured 19,900 inner scans behind a published count of 200.
_DERIVATION_WORK = 0

#: Primitive work performed by :func:`derivation_classifications`. Tests reset
#: this counter immediately before one call and bound it by the admitted input
#: plus the identifiers the classifier actually emits. Keeping this separate
#: from ``_DERIVATION_WORK`` prevents validation's join/strata accounting from
#: hiding a classification rescan.
_DERIVATION_CLASSIFICATION_WORK = 0


def _derivation_atoms(rule: Any):
    """Yield ``(suffix, atom, polarity)`` over a structured rule's atoms.

    Total by construction: a non-list body, a non-mapping atom and a missing
    section all yield nothing rather than raising. The shape rule is what
    reports them, so this helper never needs to.
    """
    global _DERIVATION_ATOM_VISITS
    if not isinstance(rule, dict):
        return
    for key, polarity in (("body", "positive"), ("negate", "negated")):
        section = rule.get(key)
        if not isinstance(section, list):
            continue
        for index, atom in enumerate(section):
            _DERIVATION_ATOM_VISITS += 1
            if isinstance(atom, dict):
                yield f".{key}[{index}]", atom, polarity


def _safe_key(key: Any) -> str:
    """A bounded, exception-safe rendering of a mapping key for a message.

    ``str()`` on an integer with more than 4300 digits raises ``ValueError``
    under CPython's integer-conversion limit, so a rule whose key is such a
    literal would crash the validator that exists to refuse it.
    """
    try:
        text = str(key)
    except Exception:  # noqa: BLE001 - any rendering failure is still a key
        text = f"<unrenderable {type(key).__name__}>"
    return text if len(text) <= 120 else text[:117] + "..."


def _derivation_id(value: Any) -> str:
    """Preserve valid identifiers and render hostile non-strings without raising."""
    if isinstance(value, str):
        return value
    try:
        return str(value)
    except (ValueError, OverflowError):
        return f"<unrenderable {type(value).__name__}>"


def _derivation_bind(atom: Any) -> dict[Any, Any]:
    """An atom's bind mapping, or an empty one when it is not a mapping.

    A non-mapping ``bind`` is the shape rule's finding; every other rule reads
    through this helper so a hostile document produces issues rather than an
    ``AttributeError`` (standing rule 1).
    """
    bind = atom_bind(atom)
    return bind if isinstance(bind, dict) else {}


def _derivation_variable(term: Any) -> str | None:
    """The variable a term references, or None when it is not one.

    A bare ``"$"`` is NOT a variable: ``_variable_name`` would return the empty
    string, and an empty name silently unifies with nothing. Refusing it here
    keeps `head:malformed-variable` a decidable branch.
    """
    name = _variable_name(term)
    return name if name else None


def _derivation_positive_variables(rule: Any) -> set[str]:
    """Variables a POSITIVE body atom binds -- the range-restriction basis."""
    return {
        variable
        for suffix, atom, polarity in _derivation_atoms(rule)
        if polarity == "positive"
        for term in _derivation_bind(atom).values()
        if (variable := _derivation_variable(term)) is not None
    }


def _aggregate_variables(rule: Any) -> tuple[set[str], str | None]:
    """Return aggregate contribution variables and its local result name."""
    if not isinstance(rule, dict) or not isinstance(rule.get("aggregate"), dict):
        return set(), None
    aggregate = rule["aggregate"]
    over = {
        variable
        for value in aggregate.get("over", ())
        if (variable := _derivation_variable(value)) is not None
    }
    return over, _derivation_variable(aggregate.get("as"))


@dataclass(frozen=True, slots=True)
class AggregateAnalysis:
    """The one shared, total interpretation of a structured aggregate."""

    function: Literal["count", "sum", "min", "max", "avg"] | None
    value_term: object | None
    over_variables: tuple[str, ...]
    result_variable: str | None
    group_variables: tuple[str, ...]
    value_primitive: str | None
    result_primitive: Literal["Integer", "ExactRational"] | None
    variables: tuple[str, ...]
    issue: str | None = None


def analyze_aggregate(
    rule: object,
    variable_primitives: Mapping[str, str],
    *,
    limits=DEFAULT_LIMITS,
) -> AggregateAnalysis | None:
    """Analyze an aggregate without assuming schema-valid input.

    The returned first issue is intentionally deterministic.  Semantic
    validation turns it into the public diagnostic; checker and redaction use
    the same group/scope interpretation once it is valid.
    """
    if not isinstance(rule, dict) or "aggregate" not in rule:
        return None
    aggregate = rule.get("aggregate")
    empty = AggregateAnalysis(None, None, (), None, (), None, None, (), "semantic:aggregate-shape")
    if not isinstance(aggregate, dict) or not isinstance(variable_primitives, Mapping):
        return empty
    function = aggregate.get("fn")
    if not isinstance(function, str) or function not in {"count", "sum", "min", "max", "avg"}:
        return AggregateAnalysis(
            None, aggregate.get("of"), (), None, (), None, None, (), "semantic:aggregate-function"
        )
    over_raw = aggregate.get("over")
    if not isinstance(over_raw, list) or not over_raw:
        return empty
    over: list[str] = []
    for item in over_raw:
        variable = _derivation_variable(item)
        if variable is None:
            return empty
        if variable in over:
            return AggregateAnalysis(
                function,
                aggregate.get("of"),
                tuple(over),
                None,
                (),
                None,
                None,
                (),
                "semantic:aggregate-over-duplicate",
            )
        if variable not in variable_primitives:
            return AggregateAnalysis(
                function,
                aggregate.get("of"),
                tuple(over),
                None,
                (),
                None,
                None,
                (),
                "semantic:aggregate-over-unbound",
            )
        over.append(variable)
    result = _derivation_variable(aggregate.get("as"))
    if result is None:
        return empty
    value = analyze_term(aggregate.get("of"), variable_primitives, limits=limits)
    if value.issue is not None or set(value.variables) - set(variable_primitives):
        return AggregateAnalysis(
            function,
            aggregate.get("of"),
            tuple(over),
            result,
            (),
            value.primitive,
            None,
            value.variables,
            "semantic:aggregate-of-unbound",
        )
    if result in variable_primitives or result in over or result in value.variables:
        return AggregateAnalysis(
            function,
            aggregate.get("of"),
            tuple(over),
            result,
            (),
            value.primitive,
            None,
            value.variables,
            "semantic:aggregate-as-not-fresh",
        )
    head = rule.get("head")
    group = (
        tuple(
            sorted(
                {
                    variable
                    for term in head.values()
                    for variable in term_variables(term)
                    if variable != result
                }
            )
        )
        if isinstance(head, dict)
        else ()
    )
    if set(group) - set(variable_primitives):
        return AggregateAnalysis(
            function,
            aggregate.get("of"),
            tuple(over),
            result,
            group,
            value.primitive,
            None,
            value.variables,
            "semantic:aggregate-head-scope",
        )
    scope = set(group) | {result}
    for term in head.values() if isinstance(head, dict) else ():
        if set(term_variables(term)) - scope:
            return AggregateAnalysis(
                function,
                aggregate.get("of"),
                tuple(over),
                result,
                group,
                value.primitive,
                None,
                value.variables,
                "semantic:aggregate-head-scope",
            )
    where = rule.get("where", [])
    if not isinstance(where, list) or any(not isinstance(item, dict) for item in where):
        return AggregateAnalysis(
            function,
            aggregate.get("of"),
            tuple(over),
            result,
            group,
            value.primitive,
            None,
            value.variables,
            "semantic:aggregate-where-scope",
        )
    for comparison in where:
        if any(set(term_variables(comparison.get(side))) - scope for side in ("left", "right")):
            return AggregateAnalysis(
                function,
                aggregate.get("of"),
                tuple(over),
                result,
                group,
                value.primitive,
                None,
                value.variables,
                "semantic:aggregate-where-scope",
            )
    if function != "count" and value.primitive != "Integer":
        return AggregateAnalysis(
            function,
            aggregate.get("of"),
            tuple(over),
            result,
            group,
            value.primitive,
            None,
            value.variables,
            "semantic:aggregate-input-type",
        )
    avg_head_terms_needing_round = [
        term
        for term in (head.values() if isinstance(head, dict) else ())
        if result in term_variables(term)
        and not (is_function_term(term) and term.get("fn") == "round")
    ]
    if function == "avg" and avg_head_terms_needing_round:
        return AggregateAnalysis(
            function,
            aggregate.get("of"),
            tuple(over),
            result,
            group,
            value.primitive,
            "ExactRational",
            value.variables,
            "semantic:aggregate-head-needs-round",
        )
    return AggregateAnalysis(
        function,
        aggregate.get("of"),
        tuple(over),
        result,
        group,
        value.primitive,
        "Integer" if function != "avg" else "ExactRational",
        value.variables,
    )


def _derivation_scope_variables(rule: Any) -> set[str]:
    """Variables available after grouping, for aggregate head and where sites."""
    _over, result = _aggregate_variables(rule)
    if result is None:
        return _derivation_positive_variables(rule)
    head = rule.get("head") if isinstance(rule, dict) else None
    group = {
        variable
        for term in (head.values() if isinstance(head, dict) else ())
        for variable in term_variables(term)
        if variable != result
    }
    return group | {result}


def _primitive_maps(doc: dict[str, Any]) -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    role_types = _role_object_types(doc)
    object_types = {
        str(item.get("id")): item
        for item in doc.get("object_types") or []
        if isinstance(item, dict) and item.get("id") is not None
    }
    primitives = {
        object_type_id: primitive
        for object_type_id in object_types
        if (primitive := _resolved_primitive(object_type_id, object_types)) is not None
    }
    return role_types, primitives


def _derivation_variable_primitives(
    doc: dict[str, Any], rule: dict[str, Any], *, include_aggregate_result: bool = True
) -> dict[str, str]:
    role_types, primitives = _primitive_maps(doc)
    observed: dict[str, set[str]] = {}
    for suffix, atom, polarity in _derivation_atoms(rule):
        if not isinstance(atom, dict):
            continue
        fact_type_id = str(atom.get("fact_type"))
        for role_name, term in _derivation_bind(atom).items():
            variable = _derivation_variable(term)
            object_type_id = role_types.get(fact_type_id, {}).get(str(role_name))
            primitive = primitives.get(object_type_id or "")
            if variable is not None and primitive is not None:
                observed.setdefault(variable, set()).add(primitive)
    resolved: dict[str, str] = {}
    for variable, choices in observed.items():
        if len(choices) == 1:
            resolved[variable] = next(iter(choices))
        elif choices <= NUMERIC_PRIMITIVES:
            resolved[variable] = "Number"
    aggregate = rule.get("aggregate")
    if include_aggregate_result and isinstance(aggregate, dict):
        result = _derivation_variable(aggregate.get("as"))
        if result is not None:
            function = aggregate.get("fn")
            if function == "count":
                resolved[result] = "Integer"
            elif function == "avg":
                resolved[result] = "Number"
            else:
                analysis = analyze_term(aggregate.get("of"), resolved, limits=DEFAULT_LIMITS)
                if analysis.primitive is not None:
                    resolved[result] = analysis.primitive
    return resolved


def analyze_declared_aggregate(
    model: Model | dict[str, Any], rule: dict[str, Any]
) -> AggregateAnalysis | None:
    """Use the one aggregate policy walk with declared body-role primitives."""
    document = (
        {"object_types": model.object_types, "fact_types": model.fact_types}
        if isinstance(model, Model)
        else model
    )
    return analyze_aggregate(
        rule,
        _derivation_variable_primitives(document, rule, include_aggregate_result=False),
    )


def body_components(rule: Any) -> list[frozenset[str]]:
    """The connected components of a rule body's join graph, canonically ordered.

    Union-find, not a scan of every existing group per atom. The scanning
    version was quadratic in the number of atoms -- 19,900 comparisons for a
    200-atom body -- which the counted-operations bound (T1.18) exposed once it
    counted comparisons instead of iterator yields.

    Ordered by each component's sorted variable tuple, so the partition is a
    function of the model bytes and not of dict iteration order (T1.7).
    """
    # The nested `find`/`union` below own the counter; this frame only reads it
    # through them, so no `global` declaration belongs here.
    parent: dict[str, str] = {}

    def find(item: str) -> str:
        global _DERIVATION_WORK
        root = item
        while parent[root] != root:
            _DERIVATION_WORK += 1
            root = parent[root]
        while parent[item] != root:  # path compression
            parent[item], item = root, parent[item]
        return root

    def union(left: str, right: str) -> None:
        global _DERIVATION_WORK
        _DERIVATION_WORK += 1
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for suffix, atom, polarity in _derivation_atoms(rule):
        if polarity != "positive":
            continue
        variables = sorted(
            {
                variable
                for term in _derivation_bind(atom).values()
                if (variable := _derivation_variable(term)) is not None
            }
        )
        if not variables:
            # A fully GROUNDED atom -- every term a literal -- binds nothing and
            # so joins nothing. It is its own component, and because it can
            # never share a variable with the head it is exactly the existence
            # guard `derivation-body-component-unused` refuses. Dropping it here
            # (the first implementation did) let that guard through silently.
            variables = [f"\u0000grounded:{suffix}"]
        for variable in variables:
            parent.setdefault(variable, variable)
        for variable in variables[1:]:
            union(variables[0], variable)

    grouped: dict[str, set[str]] = {}
    for variable in parent:
        grouped.setdefault(find(variable), set()).add(variable)
    return sorted((frozenset(g) for g in grouped.values()), key=lambda g: sorted(g))


def derivation_dependencies(doc: Any) -> dict[str, set[str]]:
    """Fact type -> the fact types its rule reads.

    The edge direction is ``body/negate -> head`` (r2 A7): the head DEPENDS ON
    every fact type its atoms name, negated ones included, so a topological walk
    over this mapping evaluates a dependency before its dependent.
    """
    dependencies: dict[str, set[str]] = {}
    for path, fact_type, rule in _iter_structured_fact_derivations(doc):
        head_id = _derivation_id(fact_type.get("id"))
        dependencies.setdefault(head_id, set()).update({
            _derivation_id(atom.get("fact_type"))
            for suffix, atom, polarity in _derivation_atoms(rule)
            if atom.get("fact_type") is not None
        })
    return dependencies


@dataclass(frozen=True, slots=True)
class DerivationEdge:
    head: str
    dependency: str
    polarity: Literal["positive", "negative", "aggregate"]
    clause_index: int
    atom_path: str


def derivation_dependency_edges(doc: Any) -> tuple[DerivationEdge, ...]:
    """Keep every labelled atom edge, including duplicate and mixed edges."""
    edges: list[DerivationEdge] = []
    for path, fact_type, clause in _iter_structured_fact_derivations(doc):
        clause_match = re.search(r"\.clauses\[(\d+)\]$", path)
        clause_index = int(clause_match.group(1)) if clause_match else 0
        for suffix, atom, polarity in _derivation_atoms(clause):
            dependency = atom.get("fact_type")
            if dependency is None:
                continue
            label = "aggregate" if polarity == "positive" and "aggregate" in clause else (
                "negative" if polarity == "negated" else "positive"
            )
            edges.append(DerivationEdge(
                _derivation_id(fact_type.get("id")), _derivation_id(dependency), label,
                clause_index, path + suffix,
            ))
    return tuple(edges)


DerivationStability = Literal["static", "dynamic"]


@dataclass(frozen=True, slots=True)
class DerivationClassification:
    """One structured fact type's stability under the declared operations."""

    fact_type: str
    derivation: Literal["derived", "semiderived"]
    stability: DerivationStability
    asserted_dependencies: tuple[str, ...]
    touching_operations: tuple[str, ...]
    shared_dependencies: tuple[str, ...]
    complete: bool
    reason: str | None


def derivation_dependency_closure(
    doc: Any,
    fact_type_id: str,
) -> tuple[frozenset[str], bool, str | None]:
    """Return asserted leaves beneath one structured head, failing closed.

    The walk is memoized per invocation. Unknown dependencies,
    malformed atoms and cycles make the result incomplete; callers classify an
    incomplete result as dynamic rather than silently assuming independence.
    """
    if not isinstance(doc, dict):
        return frozenset(), False, "model document is not an object"
    closures = _derivation_dependency_closures(doc)
    return closures.get(
        fact_type_id,
        (frozenset(), False, f"'{fact_type_id}' has no structured derivation rule"),
    )


def _derivation_dependency_closures(
    doc: dict[str, Any],
) -> dict[str, tuple[frozenset[str], bool, str | None]]:
    """Compute asserted leaves once per SCC, then publish to each member."""
    global _DERIVATION_CLASSIFICATION_WORK
    fact_rows = doc.get("fact_types")
    if not isinstance(fact_rows, list):
        return {}
    fact_types = {_derivation_id(row.get("id")): row for row in fact_rows if isinstance(row, dict)}
    dependencies = derivation_dependencies(doc)
    memo: dict[str, tuple[frozenset[str], bool, str | None]] = {}
    for component in derivation_strata(doc):
        members = set(component)
        leaves: set[str] = set()
        complete = all(
            isinstance(fact_types[current].get("id"), str) for current in component
        )
        reason: str | None = None
        for current in component:
            _DERIVATION_CLASSIFICATION_WORK += 1
            for dependency in sorted(dependencies.get(current, set()) - members):
                _DERIVATION_CLASSIFICATION_WORK += 1
                if dependency not in fact_types:
                    complete = False
                    reason = reason or f"dependency '{dependency}' is not declared"
                    leaves.add(dependency)
                elif dependency in memo:
                    child_leaves, child_complete, child_reason = memo[dependency]
                    _DERIVATION_CLASSIFICATION_WORK += len(child_leaves)
                    leaves.update(child_leaves)
                    if not child_complete:
                        complete = False
                        reason = reason or child_reason
                elif dependency in dependencies:
                    complete = False
                    reason = reason or f"dependency order omits '{dependency}'"
                else:
                    leaves.add(dependency)
            rule = fact_types[current].get("derivation_rule", {})
            clauses = iter_derivation_clauses(rule)
            if (
                not isinstance(rule, dict)
                or any(_safe_key(key) not in _DERIVATION_RULE_KEYS | {"clauses"} for key in rule)
                or ("clauses" in rule and ("body" in rule or "negate" in rule))
                or not clauses
                or any(
                    any(_safe_key(key) not in _DERIVATION_RULE_KEYS for key in clause)
                    for clause in clauses
                )
                or any(
                not isinstance(clause.get("body"), list)
                or not clause["body"]
                or not isinstance(clause.get("negate", []), list)
                or not isinstance(clause.get("head"), dict)
                or not clause["head"]
                or any(
                    not isinstance(atom, dict)
                    or not isinstance(atom.get("fact_type"), str)
                    or not atom_has_bind(atom)
                    for section in (clause["body"], clause.get("negate", []))
                    for atom in section
                )
                for clause in clauses
                )
            ):
                complete = False
                reason = reason or "structured derivation rule shape is incomplete"
        for current in component:
            memo[current] = frozenset(leaves), complete, reason
    return memo


def derivation_classifications(doc: Any) -> tuple[DerivationClassification, ...]:
    """Classify every structured fact type against every operation touch."""
    global _DERIVATION_CLASSIFICATION_WORK
    if not isinstance(doc, dict):
        return ()
    operation_rows = doc.get("operations")
    operations_complete = operation_rows is None or isinstance(operation_rows, list)
    operations_reason = None if operations_complete else "operations collection is not a list"
    operations = (
        [row for row in operation_rows if isinstance(row, dict)]
        if isinstance(operation_rows, list)
        else []
    )
    if isinstance(operation_rows, list) and len(operations) != len(operation_rows):
        operations_complete = False
        operations_reason = operations_reason or "operations collection has a malformed entry"
    fact_rows = doc.get("fact_types")
    if not isinstance(fact_rows, list):
        return ()
    closures = _derivation_dependency_closures(doc)
    touches: dict[str, set[str]] = {}
    touched_by_fact: dict[str, set[str]] = {}
    for operation in operations:
        operation_id = _derivation_id(operation.get("id"))
        if not isinstance(operation.get("id"), str):
            operations_complete = False
            operations_reason = operations_reason or "an operation id is not a string"
        effect_rows = operation.get("effects")
        if effect_rows is None:
            operations_complete = False
            operations_reason = operations_reason or (
                f"operation '{operation_id}' declares no effects collection"
            )
            continue
        if not isinstance(effect_rows, list):
            operations_complete = False
            operations_reason = operations_reason or (
                f"operation '{operation_id}' effects collection is not a list"
            )
            continue
        for effect in effect_rows:
            _DERIVATION_CLASSIFICATION_WORK += 1
            if not isinstance(effect, dict):
                operations_complete = False
                operations_reason = operations_reason or (
                    f"operation '{operation_id}' has a malformed effect"
                )
                continue
            effect_kinds = set(effect) & {"create", "assert", "retract"}
            if len(effect_kinds) != 1 or set(effect) - {"create", "assert", "retract"}:
                operations_complete = False
                operations_reason = operations_reason or (
                    f"operation '{operation_id}' has an unknown effect shape"
                )
                continue
            if "create" in effect and not isinstance(effect.get("create"), dict):
                operations_complete = False
                operations_reason = operations_reason or (
                    f"operation '{operation_id}' has a malformed create effect"
                )
                continue
            for verb in ("assert", "retract"):
                atom = effect.get(verb)
                if isinstance(atom, dict) and isinstance(atom.get("fact_type"), str):
                    touched = atom["fact_type"]
                    touches.setdefault(operation_id, set()).add(touched)
                    touched_by_fact.setdefault(touched, set()).add(operation_id)
                elif verb in effect:
                    operations_complete = False
                    operations_reason = operations_reason or (
                        f"operation '{operation_id}' has a malformed {verb} effect"
                    )

    rows: list[DerivationClassification] = []
    for fact_type in fact_rows:
        if not isinstance(fact_type, dict) or not _is_structured_rule(
            fact_type.get("derivation_rule")
        ):
            continue
        fact_type_id = str(fact_type.get("id"))
        derivation = str(fact_type.get("derivation"))
        leaves, complete, reason = closures.get(
            fact_type_id,
            (frozenset(), False, f"'{fact_type_id}' has no classifiable dependency closure"),
        )
        if not operations_complete:
            complete = False
            reason = reason or operations_reason
        witnesses: set[str] = set()
        touching: list[str] = []
        leaf_set = set(leaves)
        candidate_operations: set[str] = set()
        for dependency in (*leaf_set, fact_type_id):
            _DERIVATION_CLASSIFICATION_WORK += 1
            candidate_operations.update(touched_by_fact.get(dependency, set()))
        for operation_id in sorted(candidate_operations):
            _DERIVATION_CLASSIFICATION_WORK += 1
            shared = leaf_set & touches[operation_id]
            if fact_type_id in touches[operation_id]:
                shared.add(fact_type_id)
            if shared:
                touching.append(operation_id)
                witnesses.update(shared)
                _DERIVATION_CLASSIFICATION_WORK += len(shared)
        stability: DerivationStability = "static" if complete and not touching else "dynamic"
        rows.append(
            DerivationClassification(
                fact_type=fact_type_id,
                derivation=("semiderived" if derivation == "semiderived" else "derived"),
                stability=stability,
                asserted_dependencies=tuple(sorted(leaves)),
                touching_operations=tuple(touching),
                shared_dependencies=tuple(sorted(witnesses)),
                complete=complete,
                reason=reason,
            )
        )
    return tuple(rows)


def _derivation_components(dependencies: dict[str, set[str]]) -> tuple[tuple[str, ...], ...]:
    """All SCCs in a total, iterative graph walk."""
    nodes = set(dependencies)
    outgoing = {node: sorted(dependencies[node] & nodes) for node in nodes}
    incoming: dict[str, list[str]] = {node: [] for node in nodes}
    for node, children in outgoing.items():
        for child in children:
            incoming[child].append(node)
    seen: set[str] = set()
    finish: list[str] = []
    for root in sorted(nodes):
        if root in seen:
            continue
        seen.add(root)
        stack = [(root, iter(outgoing[root]))]
        while stack:
            node, children = stack[-1]
            child = next(children, None)
            if child is None:
                finish.append(node)
                stack.pop()
            elif child not in seen:
                seen.add(child)
                stack.append((child, iter(outgoing[child])))
    seen.clear()
    result = []
    for root in reversed(finish):
        if root in seen:
            continue
        component = []
        pending = [root]
        seen.add(root)
        while pending:
            node = pending.pop()
            component.append(node)
            for parent in incoming[node]:
                if parent not in seen:
                    seen.add(parent)
                    pending.append(parent)
        result.append(tuple(sorted(component)))
    return tuple(result)


def derivation_strata(doc: Any) -> list[tuple[str, ...]]:
    """SCC-condensed, dependency-first deterministic structured strata."""
    global _DERIVATION_WORK
    dependencies = derivation_dependencies(doc)
    components = _derivation_components(dependencies)
    component_of = {member: index for index, component in enumerate(components) for member in component}
    prerequisites: dict[int, set[int]] = {index: set() for index in range(len(components))}
    dependents: dict[int, set[int]] = {index: set() for index in range(len(components))}
    for head, children in dependencies.items():
        head_index = component_of[head]
        for dependency in children:
            child_index = component_of.get(dependency)
            if child_index is not None and child_index != head_index:
                prerequisites[head_index].add(child_index)
                dependents[child_index].add(head_index)
                _DERIVATION_WORK += 1
    ready = sorted((index for index, needs in prerequisites.items() if not needs), key=lambda i: components[i])
    ordered: list[tuple[str, ...]] = []
    while ready:
        index = ready.pop(0)
        ordered.append(components[index])
        for dependent in sorted(dependents[index]):
            prerequisites[dependent].discard(index)
            if not prerequisites[dependent]:
                ready.append(dependent)
        ready.sort(key=lambda i: components[i])
    return ordered


def _rule_derivation_term_ref(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Every derivation atom names a declared fact type and only its roles.

    FIRST in the derivation block, and deliberately: a rule naming a fact type
    that does not exist must say so, rather than reporting the shape error that
    is a consequence of it.
    """
    issues: list[ValidationIssue] = []
    roles_by_fact_type = _fact_type_roles(doc)
    for path, fact_type, rule in _iter_structured_fact_derivations(doc):
        for suffix, atom, polarity in _derivation_atoms(rule):
            fact_type_id = str(atom.get("fact_type"))
            declared = roles_by_fact_type.get(fact_type_id)
            if declared is None:
                issues.append(
                    ValidationIssue(
                        path=f"{path}{suffix}",
                        message=(
                            f"derivation atom names fact type '{fact_type_id}', "
                            "which the model does not declare"
                        ),
                        rule_id="semantic:derivation-term-ref",
                    )
                )
                continue
            bind = atom_bind(atom)
            if not isinstance(bind, dict):
                continue
            for role_name in bind:
                if str(role_name) not in declared:
                    issues.append(
                        ValidationIssue(
                            path=f"{path}{suffix}.bind[{role_name}]",
                            message=(f"fact type '{fact_type_id}' declares no role '{role_name}'"),
                            rule_id="semantic:derivation-term-ref",
                        )
                    )
        head = rule.get("head")
        own_roles = roles_by_fact_type.get(str(fact_type.get("id")))
        if isinstance(head, dict) and own_roles is not None:
            for role_name in head:
                if str(role_name) not in own_roles:
                    issues.append(
                        ValidationIssue(
                            path=f"{path}.head[{role_name}]",
                            message=(
                                f"head names role '{role_name}', which fact type "
                                f"'{fact_type.get('id')}' does not declare"
                            ),
                            rule_id="semantic:derivation-term-ref",
                        )
                    )
    return issues


def _rule_derivation_rule_shape(doc: dict[str, Any]) -> list[ValidationIssue]:
    """The structured arm's keys, sections and declaration consistency.

    The meta-schema types this arm as a bare object on purpose: a `oneOf`
    failure at layer 1 can only say the value matched neither arm, while this
    rule can name the key it refused -- which is what makes `aggregate`, `sum`,
    `or` and arithmetic *refused by name* rather than merely absent.
    """
    issues: list[ValidationIssue] = []
    roles_by_fact_type = _fact_type_roles(doc)

    def add(path: str, message: str) -> None:
        issues.append(
            ValidationIssue(path=path, message=message, rule_id="semantic:derivation-rule-shape")
        )

    # Defense in depth for in-process callers, mirroring
    # `_check_guarded_structural_refusal`: layer 1's `oneOf` catches a rule that
    # is neither string nor object, but layer 2 promises a finding for any
    # malformed rule, and returning silence for a `null` rule broke that promise.
    for index, fact_type in enumerate(doc.get("fact_types") or []):
        if not isinstance(fact_type, dict):
            continue
        declared = fact_type.get("derivation_rule")
        if declared is None and str(fact_type.get("derivation") or "asserted") in {
            "derived",
            "semiderived",
        }:
            add(
                f"$.fact_types[{index}].derivation_rule",
                "a derived or semiderived fact type declares no derivation rule",
            )
        elif declared is not None and not isinstance(declared, (str, dict)):
            add(
                f"$.fact_types[{index}].derivation_rule",
                "a derivation rule is either an opaque string or a structured "
                f"object, not {type(declared).__name__}",
            )

    for path, fact_type, rule in _iter_structured_fact_derivations(doc):
        fact_type_id = str(fact_type.get("id"))
        for key in sorted(_safe_key(key) for key in rule):
            if key not in _DERIVATION_RULE_KEYS:
                add(
                    f"{path}.{key}",
                    f"structured derivation rule has no '{key}' construct; the "
                    f"admitted keys are {sorted(_DERIVATION_RULE_KEYS)} -- "
                    "disjunction, window functions and unconstrained value invention "
                    "have no syntax, and a rule needing one stays a string",
                )
        if "body" not in rule:
            add(f"{path}.body", "structured derivation rule declares no body")
        else:
            body = rule.get("body")
            if not isinstance(body, list):
                add(f"{path}.body", "derivation body is not a list of atoms")
            elif not body:
                add(f"{path}.body", "derivation body is empty")
            else:
                for index, atom in enumerate(body):
                    if not isinstance(atom, dict):
                        add(f"{path}.body[{index}]", "derivation atom is not a mapping")
        if "negate" in rule and not isinstance(rule.get("negate"), list):
            add(f"{path}.negate", "derivation negate is not a list of atoms")
        elif isinstance(rule.get("negate"), list):
            for index, atom in enumerate(rule["negate"]):
                if not isinstance(atom, dict):
                    add(f"{path}.negate[{index}]", "derivation atom is not a mapping")
        if "where" in rule and not isinstance(rule.get("where"), list):
            add(f"{path}.where", "derivation where is not a list of comparisons")
        elif isinstance(rule.get("where"), list):
            if not rule["where"]:
                add(f"{path}.where", "derivation where is empty")
            for index, comparison in enumerate(rule["where"]):
                if not isinstance(comparison, dict):
                    add(f"{path}.where[{index}]", "where comparison is not a mapping")
        head = rule.get("head")
        if head is None:
            add(f"{path}.head", "structured derivation rule declares no head")
        elif not isinstance(head, dict):
            add(f"{path}.head", "derivation head is not a mapping of role to variable")
        elif not head:
            add(f"{path}.head", "derivation head binds no role")
        derivation = str(fact_type.get("derivation") or "asserted")
        if derivation not in {"derived", "semiderived"}:
            add(
                f"$.fact_types[id={fact_type_id}].derivation",
                f"a structured derivation rule requires derivation 'derived' or "
                f"'semiderived', not '{derivation}'",
            )
        if str(fact_type.get("storage") or "computed") != "computed":
            add(
                f"$.fact_types[id={fact_type_id}].storage",
                "a structured derivation rule computes its extension, so storage "
                f"'{fact_type.get('storage')}' contradicts it",
            )
        if not roles_by_fact_type.get(fact_type_id):
            add(
                f"$.fact_types[id={fact_type_id}]",
                "a structured derivation rule needs the fact type's own roles as "
                "its head, and this fact type declares none",
            )
    return issues


def _aggregate_issues(doc: dict[str, Any], *, rule_id: str) -> list[ValidationIssue]:
    """Project one named result from the shared aggregate analysis."""
    issues: list[ValidationIssue] = []
    for path, _fact_type, rule in _iter_structured_fact_derivations(doc):
        analysis = analyze_declared_aggregate(doc, rule)
        if analysis is None or analysis.issue != rule_id:
            continue
        issues.append(
            ValidationIssue(
                path=f"{path}.aggregate",
                message=f"aggregate is invalid: {analysis.issue}",
                rule_id=rule_id,
            )
        )
    return issues


def _rule_aggregate_shape(doc: dict[str, Any]) -> list[ValidationIssue]:
    return _aggregate_issues(doc, rule_id="semantic:aggregate-shape")


def _rule_aggregate_function(doc: dict[str, Any]) -> list[ValidationIssue]:
    return _aggregate_issues(doc, rule_id="semantic:aggregate-function")


def _rule_aggregate_of_unbound(doc: dict[str, Any]) -> list[ValidationIssue]:
    return _aggregate_issues(doc, rule_id="semantic:aggregate-of-unbound")


def _rule_aggregate_over_unbound(doc: dict[str, Any]) -> list[ValidationIssue]:
    return _aggregate_issues(doc, rule_id="semantic:aggregate-over-unbound")


def _rule_aggregate_over_duplicate(doc: dict[str, Any]) -> list[ValidationIssue]:
    return _aggregate_issues(doc, rule_id="semantic:aggregate-over-duplicate")


def _rule_aggregate_as_not_fresh(doc: dict[str, Any]) -> list[ValidationIssue]:
    return _aggregate_issues(doc, rule_id="semantic:aggregate-as-not-fresh")


def _rule_aggregate_input_type(doc: dict[str, Any]) -> list[ValidationIssue]:
    return _aggregate_issues(doc, rule_id="semantic:aggregate-input-type")


def _rule_aggregate_where_scope(doc: dict[str, Any]) -> list[ValidationIssue]:
    return _aggregate_issues(doc, rule_id="semantic:aggregate-where-scope")


def _rule_aggregate_head_scope(doc: dict[str, Any]) -> list[ValidationIssue]:
    return _aggregate_issues(doc, rule_id="semantic:aggregate-head-scope")


def _rule_aggregate_head_needs_round(doc: dict[str, Any]) -> list[ValidationIssue]:
    return _aggregate_issues(doc, rule_id="semantic:aggregate-head-needs-round")


def _rule_derivation_structured_on_object_type(doc: dict[str, Any]) -> list[ValidationIssue]:
    """A structured rule on an OBJECT type is refused by name (D-P1.1).

    D6 puts derived subtypes and computed rosters out of v5.0's scope. The
    meta-schema carries `derivation_rule` on object types as well as fact types,
    so without this rule an author writing a computed roster would get silence
    and a rule nothing evaluates -- a declared branch with no case that can fail
    it, arriving through the schema.
    """
    issues: list[ValidationIssue] = []
    if not isinstance(doc, dict):
        return issues
    for index, object_type in enumerate(doc.get("object_types") or []):
        if not isinstance(object_type, dict):
            continue
        if _is_structured_rule(object_type.get("derivation_rule")):
            issues.append(
                ValidationIssue(
                    path=f"$.object_types[{index}].derivation_rule",
                    message=(
                        f"object type '{object_type.get('id')}' declares a structured "
                        "derivation rule; derived subtypes and computed rosters are "
                        "out of scope in this version (D6), and only fact types "
                        "carry a machine-shaped rule. A string rule stays legal and "
                        "stays opaque"
                    ),
                    rule_id="semantic:derivation-structured-on-object-type",
                )
            )
    return issues


def _rule_derivation_effect_on_derived(doc: dict[str, Any]) -> list[ValidationIssue]:
    """An operation may not persist into a computed derived view."""
    if not isinstance(doc, dict):
        return []
    modes = {
        str(row.get("id")): str(row.get("derivation"))
        for row in doc.get("fact_types") or []
        if isinstance(row, dict) and _is_structured_rule(row.get("derivation_rule"))
    }
    issues: list[ValidationIssue] = []
    for operation_index, operation in enumerate(doc.get("operations") or []):
        if not isinstance(operation, dict):
            continue
        operation_id = str(operation.get("id"))
        for effect_index, effect in enumerate(operation.get("effects") or []):
            if not isinstance(effect, dict):
                continue
            for verb in ("assert", "retract"):
                atom = effect.get(verb)
                if not isinstance(atom, dict):
                    continue
                fact_type_id = str(atom.get("fact_type"))
                if modes.get(fact_type_id) != "derived":
                    continue
                issues.append(
                    ValidationIssue(
                        path=(f"$.operations[{operation_index}].effects[{effect_index}].{verb}"),
                        message=(
                            f"operation '{operation_id}' {verb}s structured derived "
                            f"fact type '{fact_type_id}'; derived facts are computed "
                            "views and cannot be operation effects"
                        ),
                        rule_id="semantic:derivation-effect-on-derived",
                    )
                )
    return issues


def _rule_derivation_effect_on_semiderived(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Phase 2 refuses writes into the authored half of a structured view."""
    if not isinstance(doc, dict):
        return []
    semiderived = {
        str(row.get("id"))
        for row in doc.get("fact_types") or []
        if isinstance(row, dict)
        and row.get("derivation") == "semiderived"
        and _is_structured_rule(row.get("derivation_rule"))
    }
    issues: list[ValidationIssue] = []
    for operation_index, operation in enumerate(doc.get("operations") or []):
        if not isinstance(operation, dict):
            continue
        operation_id = str(operation.get("id"))
        for effect_index, effect in enumerate(operation.get("effects") or []):
            if not isinstance(effect, dict):
                continue
            for verb in ("assert", "retract"):
                atom = effect.get(verb)
                if not isinstance(atom, dict):
                    continue
                fact_type_id = str(atom.get("fact_type"))
                if fact_type_id not in semiderived:
                    continue
                issues.append(
                    ValidationIssue(
                        path=(f"$.operations[{operation_index}].effects[{effect_index}].{verb}"),
                        message=(
                            f"operation '{operation_id}' {verb}s structured semiderived "
                            f"fact type '{fact_type_id}'; Phase 2 computes that view for "
                            "reads while preserving only pre-existing authored surplus, "
                            "so operations may not write it"
                        ),
                        rule_id="semantic:derivation-effect-on-semiderived",
                    )
                )
    return issues


def _rule_derivation_dynamic_dependency_incomplete(
    doc: dict[str, Any],
) -> list[ValidationIssue]:
    """Admit proved dynamic closures and refuse only unclassifiable ones."""
    if not isinstance(doc, dict) or not doc.get("operations"):
        return []
    issues: list[ValidationIssue] = []
    for row in derivation_classifications(doc):
        if row.complete:
            continue
        issues.append(
            ValidationIssue(
                path=f"$.fact_types[id={row.fact_type}].derivation_rule",
                message=(
                    f"structured {row.derivation} fact type '{row.fact_type}' has an "
                    "incomplete dependency closure: "
                    f"{row.reason or 'the dependency graph could not be classified'}; "
                    "selective dynamic refresh fails closed"
                ),
                rule_id="semantic:derivation-dynamic-dependency-incomplete",
            )
        )
    return issues


def _rule_derivation_role_claim(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Every derivation atom binds every role its fact type declares."""
    issues: list[ValidationIssue] = []
    roles_by_fact_type = _fact_type_roles(doc)
    for path, fact_type, rule in _iter_structured_fact_derivations(doc):
        for suffix, atom, polarity in _derivation_atoms(rule):
            declared = roles_by_fact_type.get(str(atom.get("fact_type")))
            if declared is None:
                continue
            bind = atom_bind(atom)
            named = {str(name) for name in bind} if isinstance(bind, dict) else set()
            missing = declared - named
            if missing:
                issues.append(
                    ValidationIssue(
                        path=f"{path}{suffix}",
                        message=(
                            f"atom for fact type '{atom.get('fact_type')}' omits "
                            f"declared roles {sorted(missing)}"
                        ),
                        rule_id="semantic:derivation-role-claim",
                    )
                )
    return issues


def _rule_derivation_head_role_claim(doc: dict[str, Any]) -> list[ValidationIssue]:
    """The head binds EVERY role of the fact type it derives."""
    issues: list[ValidationIssue] = []
    roles_by_fact_type = _fact_type_roles(doc)
    for path, fact_type, rule in _iter_structured_fact_derivations(doc):
        declared = roles_by_fact_type.get(str(fact_type.get("id")))
        head = rule.get("head")
        if declared is None or not isinstance(head, dict):
            continue
        missing = declared - {str(name) for name in head}
        if missing:
            issues.append(
                ValidationIssue(
                    path=f"{path}.head",
                    message=(
                        f"head omits declared roles {sorted(missing)} of fact type "
                        f"'{fact_type.get('id')}'"
                    ),
                    rule_id="semantic:derivation-head-role-claim",
                )
            )
    return issues


def _derivation_head_term_issues(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Analyze exact head/where terms and enforce their Phase-3 type boundary."""
    issues: list[ValidationIssue] = []
    role_types, primitives = _primitive_maps(doc)
    for path, fact_type, rule in _iter_structured_fact_derivations(doc):
        variable_primitives = _derivation_variable_primitives(doc, rule)
        head = rule.get("head")
        if not isinstance(head, dict):
            continue
        for role_name, term in head.items():
            legacy_variable = _derivation_variable(term)
            if legacy_variable is not None and legacy_variable not in variable_primitives:
                # Preserve the admitted pre-Phase-3 case where primitive
                # metadata is unresolved; the legacy evaluator still carries
                # and compares the runtime scalar by identity.
                continue
            analysis = analyze_term(term, variable_primitives, limits=DEFAULT_LIMITS)
            if analysis.issue is not None:
                issues.append(
                    ValidationIssue(
                        path=f"{path}.head[{role_name}]",
                        message=f"head term for role '{role_name}' is invalid: {analysis.issue}",
                        rule_id=analysis.issue,
                    )
                )
                continue
            own_id = str(fact_type.get("id"))
            object_type_id = role_types.get(own_id, {}).get(str(role_name))
            role_primitive = primitives.get(object_type_id or "")
            compatible = (
                role_primitive == analysis.primitive
                or (
                    role_primitive in NUMERIC_PRIMITIVES
                    and analysis.primitive in NUMERIC_PRIMITIVES
                )
                or (
                    not is_function_term(term)
                    and isinstance(term, str)
                    and role_primitive in {"String", "Date", "DateTime", "Binary"}
                )
            )
            if role_primitive is not None and not compatible:
                issues.append(
                    ValidationIssue(
                        path=f"{path}.head[{role_name}]",
                        message=(
                            f"head term has primitive {analysis.primitive!r}, incompatible "
                            f"with role primitive {role_primitive!r}"
                        ),
                        rule_id="semantic:derivation-head-term-type",
                    )
                )
            if (
                is_function_term(term)
                and term.get("fn") != "round"
                and analysis.primitive != "Integer"
            ):
                # Two rule ids, not one: an exact-tier function (Phase 3/4 --
                # add/sub/mul/neg/abs/mod) keeps the id Phase 3's closed,
                # digest-cited fixture already pins
                # (tests/fixtures/v62-phase3/answers.json); a float-tier
                # function (div/sqrt/floor/ceil/haversine) gets the plan's
                # own literal T5.2 name. Neither closed evidence nor the
                # plan's wording is sacrificed.
                float_headed = term.get("fn") in FLOAT_FUNCTION_ARITY
                issues.append(
                    ValidationIssue(
                        path=f"{path}.head[{role_name}]",
                        message="a non-Integer computed head requires round",
                        rule_id=(
                            "semantic:derivation-float-head-unquantized"
                            if float_headed
                            else "semantic:derivation-head-needs-round"
                        ),
                    )
                )
        where = rule.get("where")
        if not isinstance(where, list):
            continue
        positive = _derivation_scope_variables(rule)
        for index, comparison in enumerate(where):
            if not isinstance(comparison, dict):
                continue
            analyses = {
                side: analyze_term(comparison.get(side), variable_primitives, limits=DEFAULT_LIMITS)
                for side in ("left", "right")
            }
            for side, analysis in analyses.items():
                unbound = set(analysis.variables) - positive
                issue = analysis.issue
                if unbound:
                    issue = "semantic:derivation-term-unbound"
                if issue is not None:
                    issues.append(
                        ValidationIssue(
                            path=f"{path}.where[{index}].{side}",
                            message=f"where term is invalid: {issue}",
                            rule_id=issue,
                        )
                    )
            left = analyses["left"].primitive
            right = analyses["right"].primitive
            if (
                analyses["left"].issue is None
                and analyses["right"].issue is None
                and left is not None
                and right is not None
                and not _guarded_primitives_compatible(left, right)
            ):
                issues.append(
                    ValidationIssue(
                        path=f"{path}.where[{index}]",
                        message=f"where operands have incompatible types {left!r} and {right!r}",
                        rule_id="semantic:term-comparison-type",
                    )
                )
    return issues


def _filter_derivation_term_issues(doc: dict[str, Any], *, rule_id: str) -> list[ValidationIssue]:
    cache = _DERIVATION_TERM_CACHE.get()
    if cache is None or cache["document"] is not doc:
        issues = _derivation_head_term_issues(doc)
    else:
        if "issues" not in cache:
            cache["issues"] = _derivation_head_term_issues(doc)
        issues = cache["issues"]
    return [issue for issue in issues if issue.rule_id == rule_id]


def _rule_term_function_name(doc: dict[str, Any]) -> list[ValidationIssue]:
    return _filter_derivation_term_issues(doc, rule_id="semantic:term-function-name")


def _rule_term_function_arity(doc: dict[str, Any]) -> list[ValidationIssue]:
    return _filter_derivation_term_issues(doc, rule_id="semantic:term-function-arity")


def _rule_term_argument_type(doc: dict[str, Any]) -> list[ValidationIssue]:
    return _filter_derivation_term_issues(doc, rule_id="semantic:term-argument-type")


def _rule_term_non_finite_number(doc: dict[str, Any]) -> list[ValidationIssue]:
    issues = _filter_derivation_term_issues(doc, rule_id="semantic:term-non-finite-number")
    for path, constraint in _iter_guarded_constraints(doc):
        consequent = constraint.get("consequent")
        comparison = consequent.get("comparison") if isinstance(consequent, dict) else None
        if not isinstance(comparison, dict):
            continue
        for side in ("left", "right"):
            operand = comparison.get(side)
            if isinstance(operand, float) and not math.isfinite(operand):
                issues.append(
                    ValidationIssue(
                        path=f"{path}.consequent.comparison.{side}",
                        message="guarded term is invalid: semantic:term-non-finite-number",
                        rule_id="semantic:term-non-finite-number",
                    )
                )
    return issues


def _rule_term_node_budget(doc: dict[str, Any]) -> list[ValidationIssue]:
    return _filter_derivation_term_issues(doc, rule_id="semantic:term-node-budget")


def _rule_term_depth_budget(doc: dict[str, Any]) -> list[ValidationIssue]:
    return _filter_derivation_term_issues(doc, rule_id="semantic:term-depth-budget")


def _rule_term_shape(doc: dict[str, Any]) -> list[ValidationIssue]:
    return _filter_derivation_term_issues(doc, rule_id="semantic:term-shape")


def _rule_term_unbound(doc: dict[str, Any]) -> list[ValidationIssue]:
    return _filter_derivation_term_issues(doc, rule_id="semantic:term-unbound")


def _rule_derivation_head_term_type(doc: dict[str, Any]) -> list[ValidationIssue]:
    return _filter_derivation_term_issues(doc, rule_id="semantic:derivation-head-term-type")


def _rule_derivation_head_needs_round(doc: dict[str, Any]) -> list[ValidationIssue]:
    return _filter_derivation_term_issues(doc, rule_id="semantic:derivation-head-needs-round")


def _rule_derivation_float_head_unquantized(doc: dict[str, Any]) -> list[ValidationIssue]:
    return _filter_derivation_term_issues(
        doc, rule_id="semantic:derivation-float-head-unquantized"
    )


def _rule_derivation_term_unbound(doc: dict[str, Any]) -> list[ValidationIssue]:
    return _filter_derivation_term_issues(doc, rule_id="semantic:derivation-term-unbound")


def _rule_term_comparison_type(doc: dict[str, Any]) -> list[ValidationIssue]:
    return _filter_derivation_term_issues(doc, rule_id="semantic:term-comparison-type")


def _rule_derivation_head_unbound(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Range restriction: every head variable is bound by a POSITIVE body atom."""
    issues: list[ValidationIssue] = []
    for path, fact_type, rule in _iter_structured_fact_derivations(doc):
        head = rule.get("head")
        if not isinstance(head, dict):
            continue
        positive = _derivation_scope_variables(rule)
        for role_name, term in head.items():
            unbound = set(term_variables(term)) - positive
            if unbound:
                issues.append(
                    ValidationIssue(
                        path=f"{path}.head[{role_name}]",
                        message=(
                            f"head variables {sorted('$' + item for item in unbound)} are not bound by any positive "
                            "body atom, so the derived extension would be unbounded"
                        ),
                        rule_id="semantic:derivation-head-unbound",
                    )
                )
    return issues


def _rule_derivation_negate_unbound(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Safety: every negated variable is bound by a POSITIVE body atom."""
    issues: list[ValidationIssue] = []
    for path, fact_type, rule in _iter_structured_fact_derivations(doc):
        positive = _derivation_positive_variables(rule)
        for suffix, atom, polarity in _derivation_atoms(rule):
            if polarity != "negated":
                continue
            for role_name, term in _derivation_bind(atom).items():
                variable = _derivation_variable(term)
                if variable is not None and variable not in positive:
                    issues.append(
                        ValidationIssue(
                            path=f"{path}{suffix}.bind[{role_name}]",
                            message=(
                                f"negated variable '${variable}' is not bound by any "
                                "positive body atom; negation as failure needs a "
                                "finite range to fail over"
                            ),
                            rule_id="semantic:derivation-negate-unbound",
                        )
                    )
    return issues


def _rule_derivation_body_component_unused(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Every connected component of the body feeds the head.

    A DISCONNECTED body is legal here, unlike the guarded family's antecedent:
    "a minor user and an adult-rated book" is a genuine cross product and a
    genuine business rule. What is refused is weaker and more precise -- a
    component binding no head variable is an "if anything exists anywhere"
    guard whose truth does not depend on the fact being derived.
    """
    issues: list[ValidationIssue] = []
    for path, fact_type, rule in _iter_structured_fact_derivations(doc):
        head = rule.get("head")
        if not isinstance(head, dict):
            continue
        head_variables = {variable for term in head.values() for variable in term_variables(term)}
        over, result = _aggregate_variables(rule)
        if result is not None:
            head_variables.update(_derivation_scope_variables(rule) - {result})
            head_variables.update(over)
            head_variables.update(term_variables(rule["aggregate"].get("of")))
        for component in body_components(rule):
            if not (component & head_variables):
                issues.append(
                    ValidationIssue(
                        path=f"{path}.body",
                        message=(
                            "body component binding "
                            f"{sorted('$' + v for v in component)} feeds no head role; "
                            "a component whose variables never reach the head is an "
                            "existence guard, not part of the derived fact"
                        ),
                        rule_id="semantic:derivation-body-component-unused",
                    )
                )
    return issues


def _rule_derivation_term_type(doc: dict[str, Any]) -> list[ValidationIssue]:
    """A variable may not join roles whose object types are incompatible.

    "Compatible" is the SAME ancestor-closure predicate `semantic:op-term-type-compat`
    and `semantic:role-seq-type-compat` use -- one notion of type compatibility,
    because a second one that disagrees is a latent bug in exactly the family
    this rule exists to prevent.
    """
    issues: list[ValidationIssue] = []
    parents = _supertype_parents(doc)
    role_types = _role_object_types(doc)
    for path, fact_type, rule in _iter_structured_fact_derivations(doc):
        seen: dict[str, list[tuple[str, str]]] = {}
        seen_types: dict[str, set[str]] = {}
        closures: dict[str, set[str]] = {}
        sites: list[tuple[str, str, Any]] = []
        for suffix, atom, polarity in _derivation_atoms(rule):
            fact_type_id = str(atom.get("fact_type"))
            for role_name, term in _derivation_bind(atom).items():
                sites.append((f"{path}{suffix}.bind[{role_name}]", fact_type_id, (role_name, term)))
        head = rule.get("head")
        if isinstance(head, dict):
            own_id = str(fact_type.get("id"))
            for role_name, term in head.items():
                sites.append((f"{path}.head[{role_name}]", own_id, (role_name, term)))
        for site_path, fact_type_id, (role_name, term) in sites:
            variable = _derivation_variable(term)
            if variable is None:
                continue
            object_type = role_types.get(fact_type_id, {}).get(str(role_name))
            if object_type is None:
                continue
            # EVERY prior site, not just the first. Keeping only the first
            # made validity depend on bind ORDER: with `bridge <: p,q`,
            # `left <: p` and `right <: q`, the order (bridge, left, right)
            # found nothing because each pair met the bridge, while
            # (left, bridge, right) reported the real `left`/`right` conflict.
            # Semantic validity may not depend on mapping order.
            if object_type not in closures:
                closures[object_type] = _ancestor_closure(object_type, parents)
            closure = closures[object_type]
            incompatible = {
                previous
                for previous in seen_types.get(variable, ())
                if not closure & closures[previous]
            }
            # Compatible repeated types require no pairwise site walk. When
            # conflicts exist retain every prior site and diagnostic order.
            prior_sites = seen.get(variable, []) if incompatible else ()
            for previous_type, previous_path in prior_sites:
                if previous_type not in incompatible:
                    continue
                issues.append(
                    ValidationIssue(
                        path=site_path,
                        message=(
                            f"variable '${variable}' plays a role of type "
                            f"'{object_type}' here and a role of type "
                            f"'{previous_type}' at {previous_path}; the two object "
                            "types share no ancestor, so the join is empty by "
                            "construction"
                        ),
                        rule_id="semantic:derivation-term-type",
                    )
                )
            seen.setdefault(variable, []).append((object_type, site_path))
            seen_types.setdefault(variable, set()).add(object_type)
    return issues


def _rule_derivation_opaque_dependency(doc: dict[str, Any]) -> list[ValidationIssue]:
    """A structured rule may not depend on an opaque (string-rule) derivation.

    The string arm is never interpreted, so its extension does not exist for a
    structured rule to read. Refusing is distinct from an undeclared reference
    (the fact type IS declared) and from recursion (there is no cycle).
    """
    issues: list[ValidationIssue] = []
    opaque = {
        str(fact_type.get("id"))
        for fact_type in (doc.get("fact_types") or [])
        if isinstance(fact_type, dict)
        and str(fact_type.get("derivation") or "asserted") in {"derived", "semiderived"}
        and isinstance(fact_type.get("derivation_rule"), str)
    }
    for path, fact_type, rule in _iter_structured_fact_derivations(doc):
        for suffix, atom, polarity in _derivation_atoms(rule):
            fact_type_id = str(atom.get("fact_type"))
            if fact_type_id in opaque:
                issues.append(
                    ValidationIssue(
                        path=f"{path}{suffix}",
                        message=(
                            f"structured rule depends on '{fact_type_id}', whose "
                            "derivation is an opaque string this tool never "
                            "interprets, so its extension cannot be computed"
                        ),
                        rule_id="semantic:derivation-opaque-dependency",
                    )
                )
    return issues


def _derivation_cycles(doc: Any) -> list[list[str]]:
    """Every genuine cycle among structured derived fact types.

    Tarjan's SCC over the ``body/negate -> head`` graph, restricted to derived
    heads. Returns each strongly connected component of size > 1, plus every
    self-looping singleton -- and NOT the merely-downstream nodes an
    acyclic-prefix subtraction reports, which named innocent fact types as
    cyclic and misstated the members of the real cycles.
    """
    dependencies = derivation_dependencies(doc)
    derived = set(dependencies)
    edges = {head: sorted(dependencies[head] & derived) for head in sorted(derived)}
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    components: list[list[str]] = []
    counter = 0

    def strongconnect(node: str) -> None:
        nonlocal counter
        # Iterative: a deep chain must not blow the Python stack in a validator
        # that promises totality.
        work: list[tuple[str, int]] = [(node, 0)]
        while work:
            current, child_index = work[-1]
            if child_index == 0:
                index[current] = low[current] = counter
                counter += 1
                stack.append(current)
                on_stack.add(current)
            recursed = False
            for position in range(child_index, len(edges.get(current, []))):
                child = edges[current][position]
                if child not in index:
                    work[-1] = (current, position + 1)
                    work.append((child, 0))
                    recursed = True
                    break
                if child in on_stack:
                    low[current] = min(low[current], index[child])
            if recursed:
                continue
            if low[current] == index[current]:
                component: list[str] = []
                while True:
                    member = stack.pop()
                    on_stack.discard(member)
                    component.append(member)
                    if member == current:
                        break
                if len(component) > 1 or current in edges.get(current, []):
                    components.append(sorted(component))
            work.pop()
            if work:
                parent, _ = work[-1]
                low[parent] = min(low[parent], low[current])

    for node in sorted(edges):
        if node not in index:
            strongconnect(node)
    return sorted(components)


def _rule_derivation_unstratified(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Refuse negative and aggregate internal edges, and recursive functions."""
    issues: list[ValidationIssue] = []
    dependencies = derivation_dependencies(doc)
    components = _derivation_components(dependencies)
    component_of = {head: component for component in components for head in component}
    recursive = {
        head for component in components
        if len(component) > 1 or any(head in dependencies[head] for head in component)
        for head in component
    }
    for edge in derivation_dependency_edges(doc):
        component = component_of.get(edge.head)
        if component is not None and edge.dependency in component and edge.polarity != "positive":
            issues.append(
                ValidationIssue(
                    path=edge.atom_path,
                    message=(
                        f"{edge.polarity} edge {edge.dependency!r} -> {edge.head!r} "
                        f"lies inside dependency cycle {list(component)}"
                    ),
                    rule_id="semantic:derivation-unstratified",
                )
            )
    for path, fact_type, clause in _iter_structured_fact_derivations(doc):
        head_id = str(fact_type.get("id"))
        if head_id not in recursive or not isinstance(clause.get("head"), dict):
            continue
        for role_name, term in clause["head"].items():
            if is_function_term(term):
                issues.append(ValidationIssue(
                    path=f"{path}.head[{role_name}]",
                    message=f"recursive head '{head_id}' computes a new value for '{role_name}'",
                    rule_id="semantic:derivation-recursive-value-invention",
                ))
    return issues


def _rule_temporal_language(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Temporal syntax is v3-only and confined to guarded comparison operands."""
    from gnd.terms import is_temporal_node, temporal_nodes

    allowed: set[int] = set()
    for _, constraint in _iter_guarded_constraints(doc):
        consequent = constraint.get("consequent")
        comparison = consequent.get("comparison") if isinstance(consequent, dict) else None
        if isinstance(comparison, dict):
            for side in ("left", "right"):
                allowed.update(id(node) for _, node in temporal_nodes(comparison.get(side)))
    issues = []
    role_types, primitives = _primitive_maps(doc)
    hosts = {
        id(constraint): str(ft.get("id"))
        for ft in doc.get("fact_types") or []
        if isinstance(ft, dict)
        for constraint in ft.get("constraints") or []
    }
    for path, constraint in _iter_constraints(doc):
        if constraint.get("type") != "value-comparison":
            continue
        domains = []
        for side in ("role_a", "role_b"):
            operand = constraint.get(side)
            host = hosts.get(id(constraint), "")
            if isinstance(operand, dict):
                host = str(operand.get("fact_type", host))
                role = operand.get("role")
            else:
                role = operand
            object_type = role_types.get(host, {}).get(role) if isinstance(role, str) else None
            domains.append(primitives.get(object_type or ""))
        if "Duration" in domains and domains != ["Duration", "Duration"]:
            issues.append(
                ValidationIssue(
                    path=path,
                    message="Duration comparisons require two Duration roles.",
                    rule_id="semantic:temporal-comparison-type",
                )
            )
    for path, constraint in _iter_guarded_constraints(doc):
        observed: dict[str, set[str]] = {}
        for _, atom in _iter_guarded_atoms(constraint):
            if not isinstance(atom, dict):
                continue
            bindings = atom_bind(atom)
            if not isinstance(bindings, dict):
                continue
            for role, term in bindings.items():
                variable = _variable_name(term)
                object_type = role_types.get(str(atom.get("fact_type")), {}).get(str(role))
                primitive = primitives.get(object_type or "")
                if variable is not None and primitive is not None:
                    observed.setdefault(variable, set()).add(primitive)
        for variable, choices in observed.items():
            if "Duration" in choices and len(choices) > 1:
                issues.append(
                    ValidationIssue(
                        path=path,
                        message=f"Variable ${variable} mixes Duration and another primitive.",
                        rule_id="semantic:guarded-binding-type",
                    )
                )
    for path, node in temporal_nodes(doc):
        if node.get("primitive") == "Duration" or is_temporal_node(node):
            reason = None
            if doc.get("version") not in {3, 4}:
                reason = "temporal syntax requires model version 3"
            elif is_temporal_node(node) and id(node) not in allowed:
                reason = "temporal terms are supported only in guarded comparison operands"
            if reason:
                issues.append(
                    ValidationIssue(path=path, message=reason, rule_id="semantic:temporal-site")
                )
    return issues


_SEMANTIC_RULES = (
    _rule_temporal_language,
    _rule_id_unique,
    _rule_role_ref,
    _rule_cross_ref,
    _rule_depends_on,
    # After _rule_cross_ref: a sequence naming an undeclared fact type or role
    # must produce the cross-ref error first, not a confusing arity error.
    _rule_role_seq_arity,
    _rule_role_seq_type_compat,
    _rule_disjunctive_subject_type,
    _rule_join_anchor_unambiguous,
    _rule_reading_placeholders,
    _rule_fact_type_arity,
    _rule_role_names_distinct,
    _rule_subtype_ref,
    _rule_external_ref_uc,
    _rule_reference_value_type,
    _rule_value_range_type,
    _rule_value_range_order,
    _rule_count_bound_order,
    _rule_status_source,
    _rule_string_ref,
    _rule_ring_binary,
    _rule_partition_asserts_something,
    _rule_modality_policy,
    _rule_textual_alethic,
    # --- ORM+ v2 (operations). Appended, never interleaved: the table in
    # representation-format.md lists this tuple in registration order, and a
    # v1 model reaches every rule below with an empty operations list.
    _rule_op_param_ref,
    _rule_op_param_names_distinct,
    _rule_op_reading_placeholders,
    _rule_op_atom_ref,
    # After _rule_op_atom_ref: a term bound to a role that does not exist must
    # produce the atom-reference error, not a confusing type-compatibility one.
    _rule_op_term_ref,
    _rule_op_term_type_compat,
    _rule_op_effect_ground,
    _rule_op_create_param,
    _rule_op_create_ref_mode,
    _rule_op_obligation_ids_distinct,
    _rule_imported_provenance,
    _rule_imported_confirmed_reviewed,
    _rule_op_dynamic_functional,
    _rule_op_dynamic_untouched,
    _rule_op_modality_policy,
    # --- GND v3 guarded constraints. Appended after the complete v2 block,
    # never interleaved; the normative table follows this registration order.
    _rule_guarded_term_ref,
    _rule_guarded_role_claim,
    _rule_guarded_consequent_ground,
    _rule_guarded_comparison_type,
    _rule_guarded_exists_range,
    _rule_guarded_exists_where_bound,
    _rule_guarded_exists_where_type,
    # --- GND v5 ORM++ structured derivation rules. Appended after the guarded
    # block, never interleaved. THIS ORDER IS THE REFUSAL PRECEDENCE (r2 A11):
    # reference errors, then shape errors, then graph errors -- so a document
    # carrying two defects reports the one that explains the other first, and
    # the corpus pins a decided order rather than an incidental one.
    _rule_derivation_term_ref,
    _rule_derivation_rule_shape,
    _rule_aggregate_shape,
    _rule_aggregate_function,
    _rule_aggregate_of_unbound,
    _rule_aggregate_over_unbound,
    _rule_aggregate_over_duplicate,
    _rule_aggregate_as_not_fresh,
    _rule_aggregate_input_type,
    _rule_aggregate_where_scope,
    _rule_aggregate_head_scope,
    _rule_aggregate_head_needs_round,
    _rule_derivation_structured_on_object_type,
    _rule_derivation_role_claim,
    _rule_derivation_head_role_claim,
    _rule_term_function_name,
    _rule_term_function_arity,
    _rule_term_argument_type,
    _rule_term_non_finite_number,
    _rule_term_node_budget,
    _rule_term_depth_budget,
    _rule_term_shape,
    _rule_term_unbound,
    _rule_derivation_head_term_type,
    _rule_derivation_head_needs_round,
    _rule_derivation_float_head_unquantized,
    _rule_derivation_term_unbound,
    _rule_term_comparison_type,
    _rule_derivation_head_unbound,
    _rule_derivation_negate_unbound,
    _rule_derivation_body_component_unused,
    _rule_derivation_term_type,
    _rule_derivation_opaque_dependency,
    _rule_derivation_unstratified,
    _rule_derivation_effect_on_derived,
    _rule_derivation_effect_on_semiderived,
    _rule_derivation_dynamic_dependency_incomplete,
    _rule_anchored_role_and_recogniser,
    # --- IK2 induced provenance. Appended after every earlier block, never
    # interleaved, so no existing model's issue order changes.
    _rule_induced_provenance,
    _rule_induced_confirmed_reviewed,
)


def semantic_validate(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Run every layer-2 semantic rule over a parsed model document.

    **Total by construction.** Layer 2 runs on documents that survived
    PARSING, not documents that passed layer 1, so a rule can be handed a
    ``None`` where it expects a mapping. Individual rules guard what they
    reasonably can; this loop is what makes the guarantee whole, because a
    guarantee spread across forty rules is a guarantee nobody holds.

    An escaped exception becomes a NAMED issue rather than a traceback, and
    never a silent pass: ``internal:rule-raised`` identifies the rule, so a
    defect surfaces as a loud finding in the band-3 output instead of a
    stack trace out of a validator whose docstring promises totality.
    Discovered by v5.0 Phase 1's hostile-shape sweep, which found rules from
    v1, v2 and v3 raising on the same shapes.
    """
    token = _DERIVATION_TERM_CACHE.set({"document": doc})
    try:
        issues: list[ValidationIssue] = []
        for rule in _SEMANTIC_RULES:
            try:
                issues.extend(rule(doc))
            except Exception as error:  # noqa: BLE001 - totality is the contract
                issues.append(
                    ValidationIssue(
                        path="$",
                        message=(
                            f"semantic rule '{rule.__name__}' raised "
                            f"{type(error).__name__} on this document; the document is "
                            "refused and the rule is defective"
                        ),
                        rule_id="internal:rule-raised",
                    )
                )
        return issues
    finally:
        _DERIVATION_TERM_CACHE.reset(token)



yaml_stream_guard_error.__module__ = 'gnd.model'
_load_meta_schema.__module__ = 'gnd.model'
_derivation_rule_hint.__module__ = 'gnd.model'
_layer1_structural.__module__ = 'gnd.model'
_iter_constraints.__module__ = 'gnd.model'
_iter_role_refs.__module__ = 'gnd.model'
_rule_id_unique.__module__ = 'gnd.model'
_rule_role_ref.__module__ = 'gnd.model'
_rule_cross_ref.__module__ = 'gnd.model'
_rule_depends_on.__module__ = 'gnd.model'
_rule_reading_placeholders.__module__ = 'gnd.model'
_rule_fact_type_arity.__module__ = 'gnd.model'
_rule_role_names_distinct.__module__ = 'gnd.model'
_rule_subtype_ref.__module__ = 'gnd.model'
_rule_external_ref_uc.__module__ = 'gnd.model'
_rule_reference_value_type.__module__ = 'gnd.model'
_temporal_literal_valid.__module__ = 'gnd.model'
_range_endpoints_valid.__module__ = 'gnd.model'
_rule_value_range_type.__module__ = 'gnd.model'
_rule_value_range_order.__module__ = 'gnd.model'
_rule_count_bound_order.__module__ = 'gnd.model'
_rule_status_source.__module__ = 'gnd.model'
_rule_string_ref.__module__ = 'gnd.model'
_ancestor_closure.__module__ = 'gnd.model'
_rule_ring_binary.__module__ = 'gnd.model'
_constraint_role_seqs.__module__ = 'gnd.model'
_joining_sequences.__module__ = 'gnd.model'
_rule_join_anchor_unambiguous.__module__ = 'gnd.model'
_role_object_types.__module__ = 'gnd.model'
_rule_role_seq_arity.__module__ = 'gnd.model'
_rule_role_seq_type_compat.__module__ = 'gnd.model'
_rule_disjunctive_subject_type.__module__ = 'gnd.model'
_rule_partition_asserts_something.__module__ = 'gnd.model'
_rule_anchored_role_and_recogniser.__module__ = 'gnd.model'
_rule_textual_alethic.__module__ = 'gnd.model'
_rule_modality_policy.__module__ = 'gnd.model'
_iter_operations.__module__ = 'gnd.model'
_operation_parameters.__module__ = 'gnd.model'
_iter_operation_obligations.__module__ = 'gnd.model'
_iter_operation_atoms.__module__ = 'gnd.model'
_iter_operation_terms.__module__ = 'gnd.model'
_variable_name.__module__ = 'gnd.model'
_rule_op_param_ref.__module__ = 'gnd.model'
_rule_op_param_names_distinct.__module__ = 'gnd.model'
_rule_op_reading_placeholders.__module__ = 'gnd.model'
_atom_reference_issues.__module__ = 'gnd.model'
_rule_op_atom_ref.__module__ = 'gnd.model'
_rule_op_term_ref.__module__ = 'gnd.model'
_rule_op_term_type_compat.__module__ = 'gnd.model'
_rule_op_effect_ground.__module__ = 'gnd.model'
_rule_op_create_param.__module__ = 'gnd.model'
_rule_op_create_ref_mode.__module__ = 'gnd.model'
_rule_op_obligation_ids_distinct.__module__ = 'gnd.model'
_iter_provenance_bearing.__module__ = 'gnd.model'
_provenance_bearing_label.__module__ = 'gnd.model'
_rule_imported_provenance.__module__ = 'gnd.model'
_rule_imported_confirmed_reviewed.__module__ = 'gnd.model'
_induction_strings.__module__ = 'gnd.model'
_rule_induced_provenance.__module__ = 'gnd.model'
_rule_induced_confirmed_reviewed.__module__ = 'gnd.model'
_internal_uniqueness_keys.__module__ = 'gnd.model'
dynamic_subject_is_functional.__module__ = 'gnd.model'
_rule_op_dynamic_functional.__module__ = 'gnd.model'
_rule_op_dynamic_untouched.__module__ = 'gnd.model'
_rule_op_modality_policy.__module__ = 'gnd.model'
_iter_guarded_constraints.__module__ = 'gnd.model'
_iter_guarded_atoms.__module__ = 'gnd.model'
_iter_guarded_consequent_terms.__module__ = 'gnd.model'
_rule_guarded_term_ref.__module__ = 'gnd.model'
_rule_guarded_role_claim.__module__ = 'gnd.model'
_rule_guarded_consequent_ground.__module__ = 'gnd.model'
_guarded_nested_function_variables.__module__ = 'gnd.model'
_rule_guarded_exists_range.__module__ = 'gnd.model'
_rule_guarded_exists_where_bound.__module__ = 'gnd.model'
_guarded_primitives_compatible.__module__ = 'gnd.model'
_guarded_literal_matches_primitive.__module__ = 'gnd.model'
_guarded_literal_kinds_compatible.__module__ = 'gnd.model'
_rule_guarded_comparison_type.__module__ = 'gnd.model'
_rule_guarded_exists_where_type.__module__ = 'gnd.model'
iter_derivation_clauses.__module__ = 'gnd.model'
_is_structured_rule.__module__ = 'gnd.model'
_iter_structured_fact_derivations.__module__ = 'gnd.model'
_derivation_atoms.__module__ = 'gnd.model'
_safe_key.__module__ = 'gnd.model'
_derivation_id.__module__ = 'gnd.model'
_derivation_bind.__module__ = 'gnd.model'
_derivation_variable.__module__ = 'gnd.model'
_derivation_positive_variables.__module__ = 'gnd.model'
_aggregate_variables.__module__ = 'gnd.model'
AggregateAnalysis.__module__ = 'gnd.model'
analyze_aggregate.__module__ = 'gnd.model'
_derivation_scope_variables.__module__ = 'gnd.model'
_primitive_maps.__module__ = 'gnd.model'
_derivation_variable_primitives.__module__ = 'gnd.model'
analyze_declared_aggregate.__module__ = 'gnd.model'
body_components.__module__ = 'gnd.model'
derivation_dependencies.__module__ = 'gnd.model'
DerivationEdge.__module__ = 'gnd.model'
derivation_dependency_edges.__module__ = 'gnd.model'
DerivationClassification.__module__ = 'gnd.model'
derivation_dependency_closure.__module__ = 'gnd.model'
_derivation_dependency_closures.__module__ = 'gnd.model'
derivation_classifications.__module__ = 'gnd.model'
_derivation_components.__module__ = 'gnd.model'
derivation_strata.__module__ = 'gnd.model'
_rule_derivation_term_ref.__module__ = 'gnd.model'
_rule_derivation_rule_shape.__module__ = 'gnd.model'
_aggregate_issues.__module__ = 'gnd.model'
_rule_aggregate_shape.__module__ = 'gnd.model'
_rule_aggregate_function.__module__ = 'gnd.model'
_rule_aggregate_of_unbound.__module__ = 'gnd.model'
_rule_aggregate_over_unbound.__module__ = 'gnd.model'
_rule_aggregate_over_duplicate.__module__ = 'gnd.model'
_rule_aggregate_as_not_fresh.__module__ = 'gnd.model'
_rule_aggregate_input_type.__module__ = 'gnd.model'
_rule_aggregate_where_scope.__module__ = 'gnd.model'
_rule_aggregate_head_scope.__module__ = 'gnd.model'
_rule_aggregate_head_needs_round.__module__ = 'gnd.model'
_rule_derivation_structured_on_object_type.__module__ = 'gnd.model'
_rule_derivation_effect_on_derived.__module__ = 'gnd.model'
_rule_derivation_effect_on_semiderived.__module__ = 'gnd.model'
_rule_derivation_dynamic_dependency_incomplete.__module__ = 'gnd.model'
_rule_derivation_role_claim.__module__ = 'gnd.model'
_rule_derivation_head_role_claim.__module__ = 'gnd.model'
_derivation_head_term_issues.__module__ = 'gnd.model'
_filter_derivation_term_issues.__module__ = 'gnd.model'
_rule_term_function_name.__module__ = 'gnd.model'
_rule_term_function_arity.__module__ = 'gnd.model'
_rule_term_argument_type.__module__ = 'gnd.model'
_rule_term_non_finite_number.__module__ = 'gnd.model'
_rule_term_node_budget.__module__ = 'gnd.model'
_rule_term_depth_budget.__module__ = 'gnd.model'
_rule_term_shape.__module__ = 'gnd.model'
_rule_term_unbound.__module__ = 'gnd.model'
_rule_derivation_head_term_type.__module__ = 'gnd.model'
_rule_derivation_head_needs_round.__module__ = 'gnd.model'
_rule_derivation_float_head_unquantized.__module__ = 'gnd.model'
_rule_derivation_term_unbound.__module__ = 'gnd.model'
_rule_term_comparison_type.__module__ = 'gnd.model'
_rule_derivation_head_unbound.__module__ = 'gnd.model'
_rule_derivation_negate_unbound.__module__ = 'gnd.model'
_rule_derivation_body_component_unused.__module__ = 'gnd.model'
_rule_derivation_term_type.__module__ = 'gnd.model'
_rule_derivation_opaque_dependency.__module__ = 'gnd.model'
_derivation_cycles.__module__ = 'gnd.model'
_rule_derivation_unstratified.__module__ = 'gnd.model'
_rule_temporal_language.__module__ = 'gnd.model'
semantic_validate.__module__ = 'gnd.model'
AggregateAnalysis.__dict__['__hash__'].__module__ = 'gnd.model'
AggregateAnalysis.__dict__['__init__'].__module__ = 'gnd.model'
AggregateAnalysis.__dict__['__repr__'].__module__ = 'gnd.model'
AggregateAnalysis.__dict__['__eq__'].__module__ = 'gnd.model'
AggregateAnalysis.__dict__['__setattr__'].__module__ = 'gnd.model'
AggregateAnalysis.__dict__['__delattr__'].__module__ = 'gnd.model'
DerivationEdge.__dict__['__hash__'].__module__ = 'gnd.model'
DerivationEdge.__dict__['__init__'].__module__ = 'gnd.model'
DerivationEdge.__dict__['__repr__'].__module__ = 'gnd.model'
DerivationEdge.__dict__['__eq__'].__module__ = 'gnd.model'
DerivationEdge.__dict__['__setattr__'].__module__ = 'gnd.model'
DerivationEdge.__dict__['__delattr__'].__module__ = 'gnd.model'
DerivationClassification.__dict__['__hash__'].__module__ = 'gnd.model'
DerivationClassification.__dict__['__init__'].__module__ = 'gnd.model'
DerivationClassification.__dict__['__repr__'].__module__ = 'gnd.model'
DerivationClassification.__dict__['__eq__'].__module__ = 'gnd.model'
DerivationClassification.__dict__['__setattr__'].__module__ = 'gnd.model'
DerivationClassification.__dict__['__delattr__'].__module__ = 'gnd.model'
