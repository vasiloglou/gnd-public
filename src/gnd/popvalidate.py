"""Layer-2 population validation: model-relative structural conformance (CORE-04).

The population loader has the same two-layer shape as the model loader (D-01):

Layer 1: the Draft 2020-12 population schema (``src/gnd/schema/population.schema.json``)
— syntax only, and *model-independent*. It cannot know whether ``movie_has_title``
is a fact type, nor which roles it declares.
Layer 2 (this module): **strict structural conformance against a specific model**
(D-03). Every key in ``facts:``, every key in ``instances:`` and every entry in
``covers:`` must resolve to an id the model declares, and a fact must supply
*exactly* the ``role_name`` set its fact type declares — a missing role is an
error and an extra role is an error. In ORM an instance of an n-ary fact type
fills all n roles; a fact missing a role is not a partial fact, it is not a fact.

Why this layer has to exist at all: ``checker._project`` filters out facts that
do not supply a covered role, so an omitted role makes uniqueness see an empty
projection and mandatory see an empty universe — and the checker then
*affirmatively states* that both constraints are satisfied. A population whose
two facts both omitted a mandatory role reported ``pass=2 fail=0 warning=0
unchecked=0 vacuous=0`` and exited 0. Documentation cannot fix that; only a
structural precondition can.

Rules **collect**; none aborts. D-04 makes exit 3 an *actionable* outcome, and a
retry loop that gets one issue per round trip needs N rounds. (The emitted list
is bounded downstream by ``report.MAX_POPULATION_ISSUES``; this module
deliberately adds no second, disagreeing cap.)

``rule_id`` namespace: ``population:``, deliberately NOT ``semantic:``.
``semantic:`` is owned by ``model.py``'s 12 model-document rules, and a consumer
grepping a log must be able to tell "your model is wrong" from "your population
does not match the model" without a lookup table — which is exactly the D-04
distinction between exit 3 (ill-formed shape) and exit 1 (broken rule).

Every issue message is rendered by ``gnd.verbalize``; no message string is
constructed here. Population-supplied data is untrusted agent output and reaches
a message only through ``verbalize._quote`` (WR-06 / T-01-04).

The same applies to ``ValidationIssue.path``, which is the OTHER channel this
module writes and the one that had no escaping at all (CR-05). ``path`` is
structural and carries no quotes of its own, so a raw ``path=f"$.facts.{key}"``
let a fact-type key containing newlines forge extra lines into
``cli._print_issues``' output — including the tool's own ``OK:`` line and
verdict-tally line. Every untrusted segment now goes through
``verbalize.path_segment``. Index segments (``covers[{index}]``) are integers we
computed and need none.

Deliberate, reversible call: ``covers`` duplicate detection (R4) lives here even
though it needs no model — ``population.schema.json`` could express it as
``uniqueItems``. It stays in layer 2 because (a) D-01 keeps layer 1's current
syntactic behaviour, (b) a schema edit would force a canonical-plus-vendored
byte-identical change and a ``test_schema_sync.py`` round trip, and (c) a
layer-2 message can name the duplicated id, where ``jsonschema:uniqueItems``
produces a generic array message.

Threat note (T-01-07, inherited from :mod:`gnd.model`): the only patterns
applied to document content are the two fixed, anchored, linear-time ISO-8601
literals below. No pattern is ever taken FROM a model or a population and
evaluated.
"""

from __future__ import annotations

import math
import re
from collections.abc import Callable
from datetime import date, datetime
from typing import Any

from gnd import verbalize
from gnd.documents import Model
from gnd.errors import ValidationIssue
from gnd.extraction_scope import fact_type_scope
from gnd.model_index import ModelIndex
from gnd.terms import valid_duration
from gnd.universe import (
    identifying_id as _identifying_id,  # noqa: F401 -- compatibility export
)
from gnd.universe import (
    identifying_primitive as _identifying_primitive,  # noqa: F401 -- compatibility export
)
from gnd.universe import (
    object_types_by_id as _object_types_by_id,  # noqa: F401 -- compatibility export
)
from gnd.universe import (
    resolve_primitive,
    resolve_reference_value_type,  # noqa: F401 -- compatibility export
)
from gnd.universe import (
    resolve_reference as _resolve_reference,  # noqa: F401 -- compatibility export
)

# --- layer-2 helpers ---


def _declared_fact_type_roles(model: Model) -> dict[str, set[str]]:
    """fact_type id -> declared role_names, reusing the model loader's helper."""
    return ModelIndex.for_model(model).fact_type_roles()


def _declared_object_type_ids(model: Model) -> set[str]:
    return {
        str(ot.get("id")) for ot in model.object_types or [] if ot.get("id") is not None
    }


def _role_object_types(model: Model) -> dict[str, dict[str, str]]:
    """Historical role-map shape from the shared read-only query index."""
    return ModelIndex.role_map(model)


def _covers(doc: dict[str, Any]) -> list[Any]:
    return list((doc.get("population") or {}).get("covers") or [])


# --- primitive resolution and predicates (D-05, R7/R8) ---

#: Fixed ISO-8601 calendar date (YYYY-MM-DD). Anchored by ``fullmatch``, with no
#: nested quantifier, so matching is linear in the value's length (T-01-07).
#: A literal in this source file — never derived from a model or a population.
_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")

#: Fixed ISO-8601 datetime: a date, a ``T`` (or space) separator, hh:mm with
#: optional seconds and fractional seconds, and an optional ``Z``/±hh:mm offset.
#: Same anchoring and linearity posture as ``_ISO_DATE`` (T-01-07).
_ISO_DATETIME = re.compile(
    r"\d{4}-\d{2}-\d{2}[Tt ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?([Zz]|[+-]\d{2}:?\d{2})?"
)


def _is_string(value: Any) -> bool:
    return isinstance(value, str)


def _is_integer(value: Any) -> bool:
    # `bool` SUBCLASSES `int` in Python, so isinstance(True, int) is True. Without
    # this exclusion `true` passes as an Integer, and because True == 1 it then
    # lands inside any range containing 1 — accepted silently, with no crash to
    # notice (01.1-RESEARCH.md Pitfall 1).
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    # A3: `Float`/`Number` roles ACCEPT `int`. YAML `1` and JSON `1` both load as
    # int while `1.0` loads as float, so rejecting int here would make a
    # population's validity depend on a rendering accident and break D-11
    # YAML/JSON parity.
    #
    # CR-04: `math.isfinite` excludes NaN and ±inf, and the NaN half is the one
    # that was silently ACCEPTED downstream. IEEE 754-2019 §5.11 makes every
    # ordered comparison involving NaN *unordered*, so `checker._in_range`
    # computed `below = nan < min -> False`, `above = nan > max -> False` and
    # returned `not (below or above) -> True`: it conflated "not proven outside"
    # with "inside", and reported "Each celsius value must be between '-50' and
    # '60' — satisfied" at exit 0. A NaN is not a number of the role's type, so
    # rejecting it here at exit 3 (D-03) is both the honest verdict and the one
    # that keeps it out of the comparison entirely. ±inf is rejected with it:
    # RFC 8259 §6 permits neither in JSON, so accepting them would also break
    # D-11 YAML/JSON parity (WR-04 rejects both at the JSON front end).
    # `_is_integer` needs no such guard: a Python `int` is always finite.
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _is_boolean(value: Any) -> bool:
    return isinstance(value, bool)


def _is_date(value: Any) -> bool:
    # A2: format-checked, not merely isinstance(str). checker._compare relies on
    # ISO-8601 dates ordering correctly under LEXICAL string comparison, so a
    # Date role holding "01/02/2026" compares wrongly and silently — and type
    # checking is the only place that can catch it.
    if not isinstance(value, str) or _ISO_DATE.fullmatch(value) is None:
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _is_datetime(value: Any) -> bool:
    if not isinstance(value, str) or _ISO_DATETIME.fullmatch(value) is None:
        return False
    normalized = value[:-1] + "+00:00" if value[-1:] in ("Z", "z") else value
    try:
        datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return True


def _is_binary(value: Any) -> bool:
    # No format check: inventing a base64 rule would be a guess, and D-05 says
    # resolve or skip, never guess.
    return isinstance(value, str)


#: The meta-schema's `primitive` enum, one predicate each. A MAPPING rather than
#: an if/elif chain on purpose: dispatch is by exact primitive name, so there is
#: no "check Boolean before the numeric branch" ordering hazard to get wrong —
#: the bool exclusion lives inside each numeric predicate instead.
#:
#: Every predicate uses `isinstance`, never `type(v) is ...`: ruamel's
#: round-trip loader yields int/float SUBCLASSES (ScalarInt, HexInt,
#: ScalarFloat) on the model side, so an identity test would reject them.
_PRIMITIVE_PREDICATES: dict[str, Callable[[Any], bool]] = {
    "String": _is_string,
    "Integer": _is_integer,
    "Float": _is_number,
    "Number": _is_number,
    "Date": _is_date,
    "DateTime": _is_datetime,
    "Boolean": _is_boolean,
    "Binary": _is_binary,
    "Duration": valid_duration,
}


# --- layer-2 rules (each: pure function (doc, model) -> list[ValidationIssue]) ---


def _rule_unknown_fact_type(doc: dict[str, Any], model: Model) -> list[ValidationIssue]:
    """Every key of ``facts:`` names a fact type the model declares (D-03).

    Runs FIRST: when it fires for a key, the missing-role and extra-role rules
    skip that key, because no declared role set exists to compare against.
    """
    issues: list[ValidationIssue] = []
    declared = _declared_fact_type_roles(model)
    for key in doc.get("facts") or {}:
        if str(key) not in declared:
            issues.append(
                ValidationIssue(
                    path=f"$.facts.{verbalize.path_segment(key)}",
                    message=verbalize.population_unknown_fact_type_message(
                        key, sorted(declared)
                    ),
                    rule_id="population:unknown-fact-type",
                )
            )
    return issues


def _rule_unknown_object_type(doc: dict[str, Any], model: Model) -> list[ValidationIssue]:
    """Every key of ``instances:`` names an object type the model declares (D-03)."""
    issues: list[ValidationIssue] = []
    declared = _declared_object_type_ids(model)
    for key in doc.get("instances") or {}:
        if str(key) not in declared:
            issues.append(
                ValidationIssue(
                    path=f"$.instances.{verbalize.path_segment(key)}",
                    message=verbalize.population_unknown_object_type_message(key),
                    rule_id="population:unknown-object-type",
                )
            )
    return issues


def _rule_unknown_covers(doc: dict[str, Any], model: Model) -> list[ValidationIssue]:
    """Every ``covers`` entry names a fact type the model declares (D-03).

    Coverage is the population's completeness claim (D-12): claiming coverage of
    something the model does not declare makes the claim unverifiable.
    """
    issues: list[ValidationIssue] = []
    declared = _declared_fact_type_roles(model)
    for index, fact_type_id in enumerate(_covers(doc)):
        if str(fact_type_id) not in declared:
            issues.append(
                ValidationIssue(
                    path=f"$.population.covers[{index}]",
                    message=verbalize.population_unknown_covers_message(fact_type_id),
                    rule_id="population:unknown-covers",
                )
            )
    return issues


def _rule_duplicate_covers(doc: dict[str, Any], model: Model) -> list[ValidationIssue]:
    """``covers`` holds each fact type at most once (D-03).

    Model-independent, and kept here rather than in the layer-1 schema — see the
    module docstring. The SECOND and later occurrences are reported, so the path
    names the entry to delete rather than the one to keep.
    """
    issues: list[ValidationIssue] = []
    first_seen: dict[str, int] = {}
    for index, fact_type_id in enumerate(_covers(doc)):
        key = str(fact_type_id)
        if key in first_seen:
            issues.append(
                ValidationIssue(
                    path=f"$.population.covers[{index}]",
                    message=verbalize.population_duplicate_covers_message(
                        fact_type_id, first_seen[key]
                    ),
                    rule_id="population:duplicate-covers",
                )
            )
        else:
            first_seen[key] = index
    return issues


def _rule_uncovered_structured_derived_facts(
    doc: Any, model: Model
) -> list[ValidationIssue]:
    """Refuse a non-empty structured claim that denies its own coverage.

    The production loader calls this after layer-1 shape validation, but the
    rule remains total for direct callers: malformed roots, headers, facts and
    values simply provide no eligible claim for this model-relative rule.
    """
    if not isinstance(doc, dict):
        return []
    population = doc.get("population")
    raw_covers = population.get("covers") if isinstance(population, dict) else None
    covered = (
        {str(fact_type_id) for fact_type_id in raw_covers}
        if isinstance(raw_covers, list)
        else set()
    )
    facts = doc.get("facts")
    if not isinstance(facts, dict):
        return []

    issues: list[ValidationIssue] = []
    for fact_type_id, inapplicable_reason in fact_type_scope(model).items():
        if inapplicable_reason is None or fact_type_id in covered:
            continue
        rows = facts.get(fact_type_id)
        if not isinstance(rows, list) or not rows:
            continue
        issues.append(
            ValidationIssue(
                path=f"$.facts.{verbalize.path_segment(fact_type_id)}",
                message=verbalize.population_uncovered_structured_derived_facts_message(
                    fact_type_id, len(rows)
                ),
                rule_id="population:uncovered-structured-derived-facts",
            )
        )
    return issues


def _rule_missing_role(doc: dict[str, Any], model: Model) -> list[ValidationIssue]:
    """A fact supplies every ``role_name`` its fact type declares (D-03).

    THE rule this phase exists for. In ORM an instance of an n-ary fact type
    fills all n roles, so an omission is not a partial fact — and it is exit 3
    (ill-formed shape), never exit 1 (mandatory violation): shape is not a rule,
    and the two are different feedback for a retry loop (D-04).

    Requires ``population:unknown-fact-type`` to be clean for the key.
    """
    issues: list[ValidationIssue] = []
    declared = _declared_fact_type_roles(model)
    for key, facts in (doc.get("facts") or {}).items():
        role_names = declared.get(str(key))
        if role_names is None:
            continue
        for index, fact in enumerate(facts or []):
            supplied = set(fact or {})
            for role_name in sorted(role_names - supplied, key=repr):
                issues.append(
                    ValidationIssue(
                        path=f"$.facts.{verbalize.path_segment(key)}[{index}]",
                        message=verbalize.population_missing_role_message(
                            key, index, role_name, sorted(role_names)
                        ),
                        rule_id="population:missing-role",
                    )
                )
    return issues


def _rule_extra_role(doc: dict[str, Any], model: Model) -> list[ValidationIssue]:
    """A fact supplies NO role beyond the ones its fact type declares (D-03).

    The mirror of the omission attack: an undeclared role name is either a typo
    (so some declared role is silently unfilled) or output written against a
    different model. Tolerating it would let the checker report on a subset of
    what the agent believed it had said.

    Requires ``population:unknown-fact-type`` to be clean for the key.

    ``key=repr`` is load-bearing, not cosmetic (WR-02). YAML mapping keys need
    not be strings, so ``set(fact) - role_names`` can hold both a ``bool``/``int``
    and a ``str`` — and a bare ``sorted()`` over that raises
    ``TypeError: '<' not supported between instances of 'str' and 'bool'``. The
    TypeError escaped ``population_validate``, was caught by ``_cmd_check``'s
    generic arm, and produced exit 3 with ``issues: []`` and an opaque
    ``{"type": "TypeError"}``: the band was right, but D-04 makes exit 3 the
    outcome where a retry loop most needs actionable feedback, and the loop was
    told the TOOL was broken rather than "fact 0 supplies an undeclared role".
    That is the same TypeError-as-tool-bug shape this phase closed one band over
    (the exit-70 ordering crash). ``repr`` is a total order over any two objects
    and is already this codebase's ordering key for heterogeneous values.
    """
    issues: list[ValidationIssue] = []
    declared = _declared_fact_type_roles(model)
    for key, facts in (doc.get("facts") or {}).items():
        role_names = declared.get(str(key))
        if role_names is None:
            continue
        for index, fact in enumerate(facts or []):
            for role_name in sorted(set(fact or {}) - role_names, key=repr):
                issues.append(
                    ValidationIssue(
                        path=(
                            f"$.facts.{verbalize.path_segment(key)}[{index}]"
                            f".{verbalize.path_segment(role_name)}"
                        ),
                        message=verbalize.population_extra_role_message(
                            key, index, role_name, sorted(role_names)
                        ),
                        rule_id="population:extra-role",
                    )
                )
    return issues


def _rule_fact_type_mismatch(doc: dict[str, Any], model: Model) -> list[ValidationIssue]:
    """Every fact value matches the primitive its role's object type resolves to.

    The rule that closes the exit-70 path: before CORE-04 a String in an
    Integer-typed role reached ``checker._in_range``, which evaluated
    ``"not-a-number" < 1`` and raised ``TypeError`` — so bad DATA was reported
    to the caller as a checker BUG (exit 70) and a retry loop was told the tool
    was broken. Rejecting it here at exit 3 means the value never reaches the
    comparison (D-03; CORE-06's "type-validated before ordering comparisons"
    clause, satisfied upstream).

    Requires ``population:unknown-fact-type`` clean for the key and
    ``population:extra-role`` clean for the role: an undeclared role has no
    object type and therefore no primitive.

    Skips SILENTLY whenever :func:`resolve_primitive` returns ``None`` (D-05).
    """
    issues: list[ValidationIssue] = []
    declared = _declared_fact_type_roles(model)
    role_object_types = _role_object_types(model)
    for key, facts in (doc.get("facts") or {}).items():
        role_names = declared.get(str(key))
        if role_names is None:
            continue
        typed = role_object_types.get(str(key), {})
        for index, fact in enumerate(facts or []):
            for role_name in sorted(set(fact or {}) & role_names, key=repr):
                object_type_id = typed.get(role_name)
                if object_type_id is None:
                    continue
                primitive = resolve_primitive(object_type_id, model)
                predicate = _PRIMITIVE_PREDICATES.get(str(primitive))
                if primitive is None or predicate is None:
                    continue
                value = fact[role_name]
                if (
                    doc.get("format_version") == 2
                    and isinstance(value, dict)
                    and set(value) == {"$opaque"}
                    and isinstance(value["$opaque"], str)
                    and value["$opaque"]
                ):
                    continue
                if not predicate(value):
                    issues.append(
                        ValidationIssue(
                            path=(
                                f"$.facts.{verbalize.path_segment(key)}[{index}]"
                                f".{verbalize.path_segment(role_name)}"
                            ),
                            message=verbalize.population_type_mismatch_message(
                                key, index, role_name, object_type_id, primitive, value
                            ),
                            rule_id="population:type-mismatch",
                        )
                    )
    return issues


def _rule_roster_type_mismatch(doc: dict[str, Any], model: Model) -> list[ValidationIssue]:
    """Every ``instances:`` roster entry matches its object type's primitive.

    The roster is a closed-world extension of the object type (WR-04): the
    checker draws value-constraint subjects and mandatory universes from it, so
    a type-invalid roster entry reaches the same comparisons a fact value does.

    Requires ``population:unknown-object-type`` clean for the key, and skips
    silently on an unresolvable primitive (D-05) exactly as R7 does.
    """
    issues: list[ValidationIssue] = []
    declared = _declared_object_type_ids(model)
    for key, values in (doc.get("instances") or {}).items():
        if str(key) not in declared:
            continue
        primitive = resolve_primitive(str(key), model)
        predicate = _PRIMITIVE_PREDICATES.get(str(primitive))
        if primitive is None or predicate is None:
            continue
        for index, value in enumerate(values or []):
            if not predicate(value):
                issues.append(
                    ValidationIssue(
                        path=f"$.instances.{verbalize.path_segment(key)}[{index}]",
                        message=verbalize.population_roster_type_mismatch_message(
                            key, index, primitive, value
                        ),
                        rule_id="population:type-mismatch",
                    )
                )
    return issues


def _rule_anchored_empty_string(doc: dict[str, Any], model: Model) -> list[ValidationIssue]:
    """Reject empty strings only when a declared anchor covers that role."""
    issues: list[ValidationIssue] = []
    for fact_type in model.fact_types:
        fact_type_id = str(fact_type.get("id"))
        declared = {
            str(role.get("role_name"))
            for role in fact_type.get("roles") or []
            if isinstance(role, dict) and role.get("role_name") is not None
        }
        anchored_roles: set[str] = set()
        for constraint in fact_type.get("constraints") or []:
            if constraint.get("type") == "anchored":
                role = constraint.get("role")
                anchored_roles.update(declared if role is None else {str(role)})
        for index, fact in enumerate((doc.get("facts") or {}).get(fact_type_id) or []):
            for role in sorted(anchored_roles & set(fact)):
                value = fact[role]
                if isinstance(value, str) and not value.strip():
                    issues.append(ValidationIssue(
                        path=f"$.facts.{verbalize.path_segment(fact_type_id)}[{index}].{verbalize.path_segment(role)}",
                        message=f"anchored role {role!r} cannot contain an empty or whitespace-only string",
                        rule_id="population:anchored-empty-string",
                    ))
    return issues


def _rule_model_id(doc: dict[str, Any], model: Model) -> list[ValidationIssue]:
    """The optional ``model_id`` header cross-check — D-06's three-way table.

    ================================  ==========================================
    model / population                outcome
    ================================  ==========================================
    both declared, DIFFERENT          error ``population:model-id-mismatch``
    model declares, population omits  **warning** ``population:model-id-absent``
    neither declares                  no check at all
    ================================  ==========================================

    The warning branch must never withhold acceptance: ``model_id`` is optional
    for backward compatibility, so every population written before the field
    existed lands there, and promoting the warning to an error would reject all
    of them.

    A fourth combination — the population declares an id and the model does not
    — is deliberately NO CHECK rather than a third rule id: the model has no
    identity for the population's claim to disagree with, so there is nothing to
    verify, and inventing a verdict there would be a guess.

    Both values are compared as OPAQUE STRINGS. Nothing is resolved to a path,
    nothing is opened, and ``population.model`` remains free-form metadata this
    loader never dereferences (T-01-05 / T-01.1-01). This is belt-and-braces on
    top of the unforgeable runtime marker (D-02, ``validated_against``), not a
    replacement for it: an attacker who controls the population can also set a
    matching ``model_id`` (T-01.1-14, accepted).
    """
    declared = model.model_id
    if declared is None:
        return []

    supplied = (doc.get("population") or {}).get("model_id")
    if supplied is None:
        return [
            ValidationIssue(
                path="$.population.model_id",
                message=verbalize.population_model_id_absent_message(declared),
                rule_id="population:model-id-absent",
                severity="warning",
            )
        ]

    if str(supplied) != str(declared):
        return [
            ValidationIssue(
                path="$.population.model_id",
                message=verbalize.population_model_id_mismatch_message(
                    supplied, declared
                ),
                rule_id="population:model-id-mismatch",
            )
        ]
    return []


#: Evaluation order. ``unknown-fact-type`` and ``unknown-object-type`` come
#: first: later rules skip the keys they reject, because no declared role set
#: (or object type) exists to compare those keys against. The two
#: type-conformance rules come last, after ``extra-role`` has claimed the role
#: names that have no declared object type and therefore no primitive.
_POPULATION_RULES = (
    _rule_unknown_fact_type,
    _rule_unknown_object_type,
    _rule_unknown_covers,
    _rule_duplicate_covers,
    _rule_uncovered_structured_derived_facts,
    _rule_missing_role,
    _rule_extra_role,
    _rule_fact_type_mismatch,
    _rule_anchored_empty_string,
    _rule_roster_type_mismatch,
    _rule_model_id,
)


def population_validate(doc: dict[str, Any], model: Model) -> list[ValidationIssue]:
    """Run every layer-2 rule over a parsed population document, given a model."""
    issues: list[ValidationIssue] = []
    for rule in _POPULATION_RULES:
        issues.extend(rule(doc, model))
    return issues
