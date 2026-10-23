"""Deterministic, complete stakeholder verbalization of an ORM model.

Unlike :mod:`gnd.extract.vocabulary`, this renderer is deliberately
constraint-aware.  It is the review artifact for model evolution: every model
element is emitted once under a stable locator, every active constraint keeps
its complete lifecycle metadata, and rejected proposals remain visibly
archived rather than being mistaken for active rules.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from gnd.atoms import atom_bind
from gnd.documents import Model
from gnd.model import analyze_declared_aggregate, iter_derivation_clauses, load_model
from gnd.refscheme import reference_identity
from gnd.terms import term_variables
from gnd.universe import resolve_primitive
from gnd.verbalize import line_text
from gnd.vocabulary import reading_text

__all__ = ["VerbalizationError", "render_model_verbalization"]


class VerbalizationError(ValueError):
    """The caller supplied a value that is not a validated ORM model."""


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _display(object_types: dict[str, dict[str, Any]], identifier: Any) -> str:
    item = object_types.get(str(identifier), {})
    return str(item.get("name") or identifier)


def _object_type_cnl(
    item: dict[str, Any],
    *,
    object_types: dict[str, dict[str, Any]],
    model: Model,
) -> str:
    identifier = str(item["id"])
    name = str(item.get("name") or identifier)
    parents = item.get("subtype_of") or []
    if parents:
        parent_names = " and ".join(_display(object_types, parent) for parent in parents)
        if item.get("inherits_reference") is True:
            sentence = (
                f"{name} is a kind of {parent_names}, inheriting the reference of {parent_names}."
            )
        else:
            sentence = f"{name} is a kind of {parent_names}."
    elif item.get("kind") == "value":
        primitive = resolve_primitive(identifier, model)
        sentence = (
            f"{name} is a value of type {primitive}."
            if primitive is not None
            else f"{name} is a value type."
        )
    else:
        reference = item.get("reference") or {}
        mode = reference.get("mode")
        if mode in {"popular", "general"}:
            sentence = (
                f"{name} is identified by {_display(object_types, reference.get('value_type'))}."
            )
        elif mode == "unit-based":
            sentence = (
                f"{name} is identified by a value in {reference.get('unit')} "
                f"({reference.get('measure_type')})."
            )
        elif mode == "external":
            kind, payload = reference_identity(identifier, model)
            if kind == "composite":
                roles = " and ".join(
                    f"{entry['role']} in {entry['fact_type']}" for entry in payload
                )
                sentence = f"{name} is identified by the combination of {roles}."
            else:
                sentence = f"{name} has an external reference scheme."
        else:
            sentence = f"{name} is an entity type with no declared reference scheme."

    if item.get("derivation_rule"):
        sentence += f" Derivation rule: {item['derivation_rule']}"
    if item.get("independent") is True:
        sentence += " Independent instances may exist without playing a fact role."
    return sentence


def _fact_type_cnl(item: dict[str, Any], model: Model) -> str:
    sentence = reading_text(item.get("reading")).strip()
    if sentence and not sentence.endswith("."):
        sentence += "."
    roles = item.get("roles") or []
    object_ids = [str(role.get("object_type")) for role in roles]
    if len(roles) > 1 and len(set(object_ids)) < len(object_ids):
        role_names = " and ".join(str(role.get("role_name")) for role in roles)
        sentence += f" Repeated object-type roles are named {role_names}."
    objectification = item.get("objectification") or item.get("objectified_as")
    if objectification:
        sentence += f" This fact type is objectified as {objectification}."
    if item.get("derivation_rule"):
        rule = item["derivation_rule"]
        sentence += (
            f" This fact type is derived: {_derivation_cnl(rule, model)}"
            if isinstance(rule, dict)
            else f" This fact type is derived: {rule}"
        )
    if item.get("depends_on"):
        sentence += " Admission depends on " + ", ".join(item["depends_on"]) + "."
    return sentence or "This fact type has no declared reading."


def _role_ref(ref: Any) -> str:
    if not isinstance(ref, dict):
        return str(ref)
    return f"{ref.get('fact_type')}:{ref.get('role')}"


def _bound_text(bound: Any) -> str:
    if not isinstance(bound, dict):
        return str(bound)
    minimum = bound.get("min")
    maximum = bound.get("max")
    if minimum is not None and maximum is not None and minimum == maximum:
        return f"exactly {minimum}"
    if minimum is not None and maximum is not None:
        return f"at least {minimum} and at most {maximum}"
    if minimum is not None:
        return f"at least {minimum}"
    return f"at most {maximum}"


def _guarded_term(term: Any) -> str:
    if isinstance(term, dict) and set(term) == {"duration_days"}:
        return f"{term['duration_days']} calendar days"
    if isinstance(term, dict) and set(term) == {"date"}:
        return f"date {term['date']}"
    if isinstance(term, dict) and set(term) == {"fn", "args"}:
        if term["fn"] in {"date_add", "date_sub"}:
            day, duration = term["args"]
            direction = "after" if term["fn"] == "date_add" else "before"
            return f"({_guarded_term(duration)} {direction} {_guarded_term(day)})"
        arguments = ", ".join(_guarded_term(argument) for argument in term["args"])
        return f"{term['fn']}({arguments})"
    return term if isinstance(term, str) and term.startswith("$") else _canonical(term)


def _guarded_atom(atom: Any) -> str:
    if not isinstance(atom, dict):
        return _canonical(atom)
    binds = atom_bind(atom)
    if not isinstance(binds, dict):
        return str(atom.get("fact_type"))
    arguments = ", ".join(f"{role} = {_guarded_term(term)}" for role, term in binds.items())
    return f"{atom.get('fact_type')}({arguments})"


def _derivation_cnl(rule: dict[str, Any], model: Model) -> str:
    if "clauses" in rule:
        return "; or ".join(
            _derivation_cnl(clause, model) for clause in iter_derivation_clauses(rule)
        )
    body = " and ".join(_guarded_atom(atom) for atom in rule.get("body") or [])
    negated = " and ".join(
        f"no {_guarded_atom(atom)} fact holds" for atom in rule.get("negate") or []
    )
    comparisons = " and ".join(
        f"{_guarded_term(item.get('left'))} {item.get('operator')} "
        f"{_guarded_term(item.get('right'))}"
        for item in rule.get("where") or []
    )
    conditions = " and ".join(item for item in (body, negated, comparisons) if item)
    head = ", ".join(
        f"{role} = {_guarded_term(term)}" for role, term in (rule.get("head") or {}).items()
    )
    aggregate = rule.get("aggregate")
    if isinstance(aggregate, dict):
        analysis = analyze_declared_aggregate(model, rule)
        if analysis is not None and analysis.issue is None:
            result = f"${analysis.result_variable}"
            group = [f"${variable}" for variable in analysis.group_variables]
            over = ", ".join(f"${variable}" for variable in analysis.over_variables)
            function = analysis.function
            value_term = analysis.value_term
        else:
            result = str(aggregate.get("as", ""))
            group = sorted(
                {
                    f"${variable}"
                    for term in (rule.get("head") or {}).values()
                    for variable in term_variables(term)
                    if f"${variable}" != result
                }
            )
            over = ", ".join(str(item) for item in aggregate.get("over") or [])
            function = aggregate.get("fn")
            value_term = aggregate.get("of")
        clause = (
            f"group by {', '.join(group) if group else '()'}; "
            f"aggregate {function} of {_guarded_term(value_term)} "
            f"distinctly over ({over}) as {result}"
        )
        prefix = " and ".join(item for item in (body, negated) if item)
        sentence = f"when {prefix}; {clause}"
        if comparisons:
            sentence += f"; where {comparisons}"
        return f"{sentence}, derive ({head})"
    return f"when {conditions}, derive ({head})"


def _guarded_cnl(item: dict[str, Any]) -> str:
    antecedent = " and ".join(_guarded_atom(atom) for atom in item.get("antecedent") or [])
    consequent = item.get("consequent") or {}
    if "comparison" in consequent:
        comparison = consequent.get("comparison") or {}
        operators = {
            "<": "is less than",
            "<=": "is at most",
            "=": "equals",
            ">=": "is at least",
            ">": "is greater than",
            "!=": "is not equal to",
        }
        operator = operators.get(str(comparison.get("operator")), str(comparison.get("operator")))
        conclusion = (
            f"{_guarded_term(comparison.get('left'))} {operator} "
            f"{_guarded_term(comparison.get('right'))}"
        )
    elif "atom" in consequent:
        conclusion = f"{_guarded_atom(consequent.get('atom'))} holds"
    elif "exists" in consequent:
        exists = consequent.get("exists") or {}
        atoms = " and ".join(
            f"{_guarded_atom(atom)} holds" for atom in exists.get("atoms") or []
        )
        comparisons = []
        for comparison in exists.get("where") or []:
            operators = {
                "<": "is less than",
                "<=": "is at most",
                "=": "equals",
                ">=": "is at least",
                ">": "is greater than",
                "!=": "is not equal to",
            }
            operator = operators.get(
                str(comparison.get("operator")), str(comparison.get("operator"))
            )
            comparisons.append(
                f"{_guarded_term(comparison.get('left'))} {operator} "
                f"{_guarded_term(comparison.get('right'))}"
            )
        conditions = [atoms, *comparisons]
        conclusion = "there exists a joint assignment such that " + " and ".join(
            value for value in conditions if value
        )
    else:
        conclusion = f"no {_guarded_atom(consequent.get('absence'))} fact holds"
    return f"If {antecedent}, then {conclusion}."


def _constraint_cnl(item: dict[str, Any], host: str) -> str:
    family = str(item.get("type", "unknown"))
    if family == "anchored":
        role = item.get("role")
        subject = f"role {role} of {host}" if role is not None else f"every role of {host}"
        return f"Each populated value of {subject} must have a bound source anchor."
    if family == "uniqueness":
        roles = item.get("roles") or [_role_ref(ref) for ref in item.get("role_refs", [])]
        return f"Each combination of {', '.join(map(str, roles))} occurs at most once."
    if family == "mandatory":
        return f"Each instance must play role {item.get('role')}."
    if family == "mandatory-disjunctive":
        refs = ", ".join(_role_ref(ref) for ref in item.get("role_refs", []))
        return f"Each subject must play at least one of the roles {refs}."
    if family == "value":
        subject = item.get("object_type") or "Each value"
        if item.get("role_ref") is not None:
            subject = f"{subject} playing role {_role_ref(item['role_ref'])}"
        if "allowed" in item:
            return f"{subject} must take one of: {', '.join(map(str, item['allowed']))}."
        ranges = item.get("ranges") or ([item["range"]] if "range" in item else [])
        return f"{subject} must lie in the declared range set {_canonical(ranges)}."
    if family == "frequency":
        roles = item.get("roles") or [_role_ref(ref) for ref in item.get("role_refs", [])]
        return f"Each combination of {', '.join(map(str, roles))} occurs {_bound_text(item.get('bound'))}."
    if family == "ring":
        variant = item.get("variant")
        return f"The relation on {host} satisfies the {variant} ring property."
    if family in {"subset", "equality", "exclusion", "exclusive-or"}:
        return f"The declared role sequences on {host} satisfy {family}."
    if family == "value-comparison":
        left = _role_ref(item.get("role_a"))
        right = _role_ref(item.get("role_b"))
        comparisons = {
            "<": "less than",
            "<=": "less than or equal to",
            "=": "equal to",
            ">=": "greater than or equal to",
            ">": "greater than",
            "!=": "not equal to",
        }
        comparison = comparisons.get(str(item.get("operator")), str(item.get("operator")))
        return f"For each subject, {left} is {comparison} {right}."
    if family == "cardinality":
        subject = item.get("object_type") or _role_ref(item.get("role_ref"))
        return f"The population of {subject} has {_bound_text(item.get('bound'))} instances."
    if family == "subtype-partition":
        qualifier = "exactly one" if item.get("exclusive") and item.get("exhaustive") else "one"
        return (
            f"Each {item.get('supertype')} is {qualifier} of: "
            f"{', '.join(map(str, item.get('subtypes', [])))}."
        )
    if family == "guarded":
        return _guarded_cnl(item)
    if family == "textual":
        return f"[textual constraint] {item.get('expression')}"
    return f"Constraint {family} applies on {host}."


def _constraint_lines(constraints: list[dict[str, Any]], host: str) -> list[str]:
    keyed: list[tuple[str, str, dict[str, Any]]] = []
    for item in constraints:
        canonical = _canonical(item)
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        keyed.append((str(item.get("type", "unknown")), digest, item))
    keyed.sort(key=lambda value: (value[0], value[1], _canonical(value[2])))

    occurrences: Counter[tuple[str, str]] = Counter()
    lines: list[str] = []
    for family, digest, item in keyed:
        occurrence_key = (family, digest)
        occurrence = occurrences[occurrence_key]
        occurrences[occurrence_key] += 1
        source = item.get("source")
        status = item.get("status")
        modality = item.get("modality")
        prefix = f"[from {source}, {status}; modality={modality}]"
        rationale = (
            f" rationale={json.dumps(item['rationale'], ensure_ascii=False)}"
            if item.get("rationale")
            else ""
        )
        provenance = f" provenance={_canonical(item.get('provenance', {}))}"
        locator = f"[constraint:{host}:{family}:{digest}:{occurrence}]"
        lines.append(
            line_text(
                f"{locator} {prefix} {_constraint_cnl(item, host)} "
                f"source={source} status={status} modality={modality}"
                f"{rationale}{provenance} canonical={_canonical(item)}"
            )
        )
    return lines


def _term_text(term: Any) -> str:
    """A bound term as review prose: ``$expense`` reads as the parameter name,
    a literal reads as its JSON spelling so a string ``"7"`` stays visibly a
    string next to an integer ``7``."""
    if isinstance(term, str) and term.startswith("$"):
        return term[1:]
    return json.dumps(term, ensure_ascii=False)


def _atom_cnl(atom: dict[str, Any]) -> str:
    bind = atom_bind(atom)
    parts = ", ".join(f"{role}={_term_text(term)}" for role, term in bind.items())
    return f"{atom.get('fact_type')}({parts})"


def _effect_cnl(effect: dict[str, Any]) -> str:
    if "create" in effect:
        create = effect["create"] or {}
        return f"create a new {create.get('object_type')} bound to {create.get('param')}"
    if "assert" in effect:
        return f"assert {_atom_cnl(effect['assert'] or {})}"
    return f"retract {_atom_cnl(effect['retract'] or {})}"


def _obligation_lines(operation: dict[str, Any], operation_id: str) -> list[str]:
    """One line per obligation, each carrying its OWN modality, source and
    status — the operation has none of the three, because a verdict attaches to
    an obligation and never to the operation as a whole."""
    lines: list[str] = []
    for index, obligation in enumerate(operation.get("preconditions") or []):
        conjunction = " and ".join(_atom_cnl(atom) for atom in obligation.get("require") or [])
        lines.append(
            line_text(
                f"[operation-precondition:{operation_id}:{obligation.get('id')}] "
                f"Before this operation may fire, {conjunction} must hold. "
                f"[from {obligation.get('source')}, {obligation.get('status')}; "
                f"modality={obligation.get('modality')}] "
                f"index={index} canonical={_canonical(obligation)}"
            )
        )
    for index, rule in enumerate(operation.get("dynamic_rules") or []):
        subject = rule.get("subject") or {}
        lines.append(
            line_text(
                f"[operation-dynamic-rule:{operation_id}:{rule.get('id')}] "
                f"The new {subject.get('value_role')} of "
                f"{_atom_cnl(subject)} is {rule.get('op')} the old one. "
                f"[from {rule.get('source')}, {rule.get('status')}; "
                f"modality={rule.get('modality')}] "
                f"index={index} canonical={_canonical(rule)}"
            )
        )
    return lines


def _operation_lines(operations: list[dict[str, Any]]) -> list[str]:
    """Every operation rendered once, in stable id order, with each obligation,
    each effect and the frame on its own addressable line — the same
    "represented exactly once under a stable locator" rule the rest of this
    renderer follows."""
    lines: list[str] = []
    for operation in sorted(operations, key=lambda value: str(value.get("id"))):
        operation_id = str(operation.get("id"))
        header = {
            key: value
            for key, value in operation.items()
            if key not in {"preconditions", "effects", "dynamic_rules", "frame"}
        }
        parameters = ", ".join(
            f"{parameter.get('name')}: {parameter.get('object_type')}"
            for parameter in operation.get("parameters") or []
        )
        lines.append(
            line_text(
                f"[operation:{operation_id}] "
                f"{reading_text(operation.get('reading')).strip()}. "
                f"Parameters: {parameters}. "
                f"source={operation.get('source')} status={operation.get('status')} "
                f"canonical={_canonical(header)}"
            )
        )
        lines.extend(_obligation_lines(operation, operation_id))
        for index, effect in enumerate(operation.get("effects") or []):
            lines.append(
                line_text(
                    f"[operation-effect:{operation_id}:{index}] "
                    f"{_effect_cnl(effect)}. canonical={_canonical(effect)}"
                )
            )
        frame = operation.get("frame") or {}
        lines.append(
            line_text(
                f"[operation-frame:{operation_id}] Deltas to the fact types this "
                f"operation touches are graded {frame.get('modality')}. "
                f"modality={frame.get('modality')} canonical={_canonical(frame)}"
            )
        )
    return lines


def _coerce_model(model: Model | str | Path) -> Model:
    if isinstance(model, Model):
        return model
    if isinstance(model, (str, Path)):
        return load_model(str(model))
    raise VerbalizationError("render_model_verbalization requires a validated Model or model path")


def render_model_verbalization(model: Model | str | Path) -> str:
    """Render all model semantics in stable-id order with one final newline."""

    loaded = _coerce_model(model)
    object_types = {
        str(item["id"]): item for item in loaded.object_types if item.get("id") is not None
    }
    lines = [
        "=== Header ===",
        line_text(
            "Complete deterministic ORM review; "
            f"version={loaded.version} model_id={json.dumps(loaded.model_id)} "
            f"source={_canonical(loaded.source)}"
        ),
        "",
        "=== Object Types ===",
    ]

    for declaration in sorted(loaded.reference_populations, key=lambda d: d["id"]):
        lines.append(
            line_text(
                f"Reference {declaration['id']} owns {', '.join(declaration['fact_types'])}; fixed supplied facts."
            )
        )

    for item in sorted(loaded.object_types, key=lambda value: str(value.get("id"))):
        identifier = str(item["id"])
        details: list[str] = []
        for field in (
            "reference",
            "subtype_of",
            "inherits_reference",
            "derivation",
            "derivation_rule",
            "storage",
            "independent",
            "sample_population",
            "population",
        ):
            if field in item:
                details.append(f"{field}={_canonical(item[field])}")
        suffix = " " + " ".join(details) if details else ""
        lines.append(
            line_text(
                f"[object-type:{identifier}] "
                f"{_object_type_cnl(item, object_types=object_types, model=loaded)}"
                f"{suffix} canonical={_canonical(item)}"
            )
        )

    lines.extend(["", "=== Fact Types ==="])
    for item in sorted(loaded.fact_types, key=lambda value: str(value.get("id"))):
        fact_id = str(item["id"])
        # Roles and constraints are independently addressable model elements and
        # receive their own lines below.  Excluding them from the fact header is
        # what makes "represented exactly once" true rather than merely making
        # every stable tag unique.
        fact_header = {
            key: value for key, value in item.items() if key not in {"roles", "constraints"}
        }
        details = [f"reading={json.dumps(item.get('reading'), ensure_ascii=False)}"]
        for field in (
            "objectification",
            "objectified_as",
            "derivation",
            "derivation_rule",
            "storage",
            "sample_population",
            "population",
            "provenance",
        ):
            if field in item:
                details.append(f"{field}={_canonical(item[field])}")
        lines.append(
            line_text(
                f"[fact-type:{fact_id}] {_fact_type_cnl(item, model)} "
                f"{'Values of every role are redacted from reports. ' if item.get('redact') is True else ''}"
                f"{' '.join(details)} canonical={_canonical(fact_header)}"
            )
        )
        for role in item.get("roles") or []:
            role_name = str(role.get("role_name"))
            object_type = str(role.get("object_type"))
            lines.append(
                line_text(
                    f"[role:{fact_id}:{role_name}] {role_name} is played by "
                    f"{_display(object_types, object_type)}. "
                    f"{'Values of this role are redacted from reports. ' if role.get('redact') is True else ''}"
                    f"canonical={_canonical(role)}"
                )
            )
        lines.extend(_constraint_lines(item.get("constraints") or [], f"fact_types[{fact_id}]"))

    if loaded.constraints:
        lines.extend(["", "=== Top-level Constraints ==="])
        lines.extend(_constraint_lines(loaded.constraints, "model"))

    # Emitted only when the model declares operations. A v1 model — and a
    # `version: 2` model that declares none — renders byte-identically to what
    # it rendered before v2 existed, which is what makes every committed
    # verbalization digest in this repository still correct.
    operations = getattr(loaded, "operations", None) or []
    if operations:
        lines.extend(["", "=== Operations ==="])
        lines.extend(_operation_lines(operations))

    if loaded.deontic_notes:
        lines.extend(["", "=== Deontic Notes ==="])
        for index, note in enumerate(loaded.deontic_notes):
            lines.append(
                line_text(
                    f"[deontic-note:{index}] {note.text} "
                    f"rationale={json.dumps(note.rationale, ensure_ascii=False)}"
                )
            )

    if loaded.rejected_proposals:
        lines.extend(["", "=== Appendix: Rejected Proposals ==="])
        archived = sorted(loaded.rejected_proposals, key=_canonical)
        for index, item in enumerate(archived):
            lines.append(
                line_text(
                    f"[archived-proposal:{index}] archived=true status=rejected "
                    f"canonical={_canonical(item)}"
                )
            )

    return "\n".join(lines).rstrip("\n") + "\n"
