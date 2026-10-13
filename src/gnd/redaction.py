"""Post-verdict witness projection for model-declared sensitive roles.

The checker and transition evaluator never import this module.  They finish a
semantic result first; emitters then project a copy of the resulting payload.
That ordering is the boundary that keeps redaction from changing a verdict,
band, count, or obligation identity.
"""

from __future__ import annotations

import copy
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

from gnd.artifacts import canonical_json_text
from gnd.atoms import atom_bind
from gnd.branches import record_branch
from gnd.model import Model, analyze_declared_aggregate
from gnd.terms import is_function_term, term_variables

RedactionMode = Literal["applied", "unredacted"]
OutputKind = Literal[
    "validate",
    "check",
    "admission",
    "verify",
    "transition",
    "plan",
    "batch",
    "measure",
    "session-feedback",
    "session-attempt",
    "session-result",
    "population-verbalization",
    "diff",
]

INSTANCE_DETAIL = "[REDACTED INSTANCE DETAIL]"
_CONSTRAINT_FACT = re.compile(r"fact_types\[([^\]]+)\]")
_TOP_LEVEL_CONSTRAINT = re.compile(r"^constraints\[(\d+)\]")
_FACT_PATH = re.compile(r"(?:^|\.)facts\.([^\.\[]+)\[\d+\]\.([^\.\[]+)(?:$|\.)")
_STEP_BINDING_PATH = re.compile(r"(?:^|\.)steps\[\d+\]\.bindings\.([^\.\[]+)(?:$|\.)")
_STEP_BINDINGS_PATH = re.compile(r"(?:^|\.)steps\[\d+\]\.bindings(?:$|\.)")


class RedactionProjectionError(RuntimeError):
    """The output could not be copied or projected without guessing."""


@dataclass(frozen=True)
class RedactionDeclaration:
    case_id: str | None
    source: Literal["role", "fact-type"]
    fact_type: str
    roles: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "source": self.source,
            "fact_type": self.fact_type,
            "roles": list(self.roles),
        }


@dataclass(frozen=True)
class RedactionPolicy:
    declarations: tuple[RedactionDeclaration, ...]
    effective_roles: frozenset[tuple[str, str]]
    redacted_parameters: Mapping[str, frozenset[str]]
    _constraint_roles: Mapping[int, frozenset[tuple[str, str]]] = field(repr=False, compare=False)
    _compiled_roles: Mapping[str, frozenset[tuple[str, str]]] = field(
        default_factory=dict, repr=False, compare=False, kw_only=True
    )
    _constraint_variable_roles: Mapping[int, Mapping[str, frozenset[tuple[str, str]]]] = field(
        repr=False, compare=False
    )
    _exists_constraints: frozenset[int] = field(repr=False, compare=False)
    _parameter_roles: Mapping[str, Mapping[str, frozenset[tuple[str, str]]]] = field(
        repr=False,
        compare=False,
    )
    _derivation_roles: Mapping[str, frozenset[tuple[str, str]]] = field(
        repr=False,
        compare=False,
    )

    @classmethod
    def from_model(cls, model: Model, *, case_id: str | None = None) -> RedactionPolicy:
        declarations: list[RedactionDeclaration] = []
        effective: set[tuple[str, str]] = set()
        for fact_type in model.fact_types:
            fact_id = str(fact_type.get("id"))
            roles = tuple(str(role.get("role_name")) for role in fact_type.get("roles") or [])
            if fact_type.get("redact") is True:
                declarations.append(
                    RedactionDeclaration(case_id, "fact-type", fact_id, tuple(sorted(roles)))
                )
                effective.update((fact_id, role) for role in roles)
            for role in fact_type.get("roles") or []:
                if role.get("redact") is not True:
                    continue
                role_name = str(role.get("role_name"))
                declarations.append(RedactionDeclaration(case_id, "role", fact_id, (role_name,)))
                effective.add((fact_id, role_name))

        taint_edges: dict[tuple[str, str], set[tuple[str, str]]] = {}

        def connect(
            source: tuple[str, str],
            target: tuple[str, str],
            *,
            bidirectional: bool = False,
        ) -> None:
            taint_edges.setdefault(source, set()).add(target)
            if bidirectional:
                taint_edges.setdefault(target, set()).add(source)

        for fact_type in model.fact_types:
            fact_id = str(fact_type.get("id"))
            rule = fact_type.get("derivation_rule") or {}
            if not isinstance(rule, Mapping):
                continue
            variable_sources: dict[str, set[tuple[str, str]]] = {}
            for atom in [*(rule.get("body") or []), *(rule.get("negate") or [])]:
                if not isinstance(atom, Mapping):
                    continue
                source_id = atom.get("fact_type")
                bindings = atom_bind(dict(atom))
                if not isinstance(source_id, str) or not bindings:
                    continue
                for role_name, term in bindings.items():
                    if isinstance(term, str) and term.startswith("$"):
                        variable_sources.setdefault(term[1:], set()).add(
                            (source_id, str(role_name))
                        )
            head = rule.get("head")
            if isinstance(head, Mapping):
                aggregate = rule.get("aggregate")
                aggregate_variables: set[str] = set()
                aggregate_result: str | None = None
                if isinstance(aggregate, Mapping):
                    analysis = analyze_declared_aggregate(model, dict(rule))
                    if analysis is not None and analysis.issue is None:
                        aggregate_result = analysis.result_variable
                        aggregate_variables.update(analysis.variables)
                        aggregate_variables.update(analysis.over_variables)
                        aggregate_variables.update(analysis.group_variables)
                for role_name, term in head.items():
                    target = (fact_id, str(role_name))
                    used_variables = set(term_variables(term))
                    for variable in used_variables:
                        for source in variable_sources.get(variable, set()):
                            connect(source, target)
                    if aggregate_result in used_variables:
                        for variable in aggregate_variables:
                            for source in variable_sources.get(variable, set()):
                                connect(source, target)
                where_variables = {
                    variable
                    for comparison in rule.get("where") or []
                    if isinstance(comparison, Mapping)
                    for side in ("left", "right")
                    for variable in term_variables(comparison.get(side))
                }
                if aggregate_result in where_variables:
                    where_variables.update(aggregate_variables)
                for variable in where_variables:
                    for source in variable_sources.get(variable, set()):
                        for role_name in head:
                            connect(source, (fact_id, str(role_name)))

        # An operation parameter is one value flowing through preconditions and
        # effects.  If any binding site is tainted, every fact role populated
        # from that same parameter is tainted as well (including plan output).
        for operation in model.operations:
            sites: dict[str, set[tuple[str, str]]] = {}
            for node in _walk_mappings(operation):
                fact_id = node.get("fact_type")
                bindings = atom_bind(dict(node))
                if not isinstance(fact_id, str) or not bindings:
                    continue
                for role_name, value in bindings.items():
                    if isinstance(value, str) and value.startswith("$"):
                        sites.setdefault(value, set()).add((fact_id, str(role_name)))
            for coordinates in sites.values():
                for source in coordinates:
                    for target in coordinates:
                        if source != target:
                            connect(source, target, bidirectional=True)

        pending = list(effective)
        while pending:
            source = pending.pop()
            for target in taint_edges.get(source, set()):
                if target in effective:
                    continue
                effective.add(target)
                pending.append(target)

        declarations.sort(
            key=lambda item: (
                item.case_id or "",
                item.fact_type,
                item.source,
                item.roles,
            )
        )
        parameter_roles: dict[str, dict[str, set[tuple[str, str]]]] = {}
        for operation in model.operations:
            operation_id = str(operation.get("id"))
            by_parameter: dict[str, set[tuple[str, str]]] = {}
            for node in _walk_mappings(operation):
                fact_id = node.get("fact_type")
                bindings = atom_bind(dict(node))
                if not isinstance(fact_id, str) or not bindings:
                    continue
                for role_name, value in bindings.items():
                    coordinate = (fact_id, str(role_name))
                    if coordinate not in effective or not isinstance(value, str):
                        continue
                    if value.startswith("$") and len(value) > 1:
                        by_parameter.setdefault(value[1:], set()).add(coordinate)
            parameter_roles[operation_id] = by_parameter

        frozen_parameter_roles = {
            operation: {
                parameter: frozenset(coordinates)
                for parameter, coordinates in sorted(parameters.items())
            }
            for operation, parameters in sorted(parameter_roles.items())
        }
        redacted_parameters = {
            operation: frozenset(parameters)
            for operation, parameters in frozen_parameter_roles.items()
            if parameters
        }
        constraint_roles: dict[int, frozenset[tuple[str, str]]] = {}
        constraint_variable_roles: dict[int, Mapping[str, frozenset[tuple[str, str]]]] = {}
        exists_constraints: set[int] = set()
        for index, constraint in enumerate(model.constraints):
            coordinates = {
                (str(node["fact_type"]), str(node["role"]))
                for node in _walk_mappings(constraint)
                if isinstance(node.get("fact_type"), str)
                and isinstance(node.get("role"), str)
                and (str(node["fact_type"]), str(node["role"])) in effective
            }
            consequent = constraint.get("consequent")
            comparison = consequent.get("comparison") if isinstance(consequent, Mapping) else None
            if isinstance(comparison, Mapping):
                for atom in constraint.get("antecedent") or []:
                    if not isinstance(atom, Mapping) or not isinstance(atom.get("fact_type"), str):
                        continue
                    for role_name, term in atom_bind(dict(atom)).items():
                        coordinate = (str(atom["fact_type"]), str(role_name))
                        if coordinate in effective:
                            coordinates.add(coordinate)
            exists = consequent.get("exists") if isinstance(consequent, Mapping) else None
            if isinstance(exists, Mapping):
                exists_constraints.add(index)
                variables_by_role: dict[str, set[tuple[str, str]]] = {}
                for atom in [
                    *(constraint.get("antecedent") or []),
                    *(exists.get("atoms") or []),
                ]:
                    if not isinstance(atom, Mapping) or not isinstance(atom.get("fact_type"), str):
                        continue
                    for role_name, term in atom_bind(dict(atom)).items():
                        if isinstance(term, str) and term.startswith("$"):
                            coordinate = (str(atom["fact_type"]), str(role_name))
                            if coordinate in effective:
                                variables_by_role.setdefault(term, set()).add(coordinate)
                constraint_variable_roles[index] = {
                    variable: frozenset(roles)
                    for variable, roles in sorted(variables_by_role.items())
                }
                comparisons = [
                    comparison
                    for comparison in exists.get("where") or []
                    if isinstance(comparison, Mapping)
                ]
                term_bearing = any(
                    is_function_term(comparison.get(side))
                    for comparison in comparisons
                    for side in ("left", "right")
                )
                used = {
                    variable
                    for comparison in comparisons
                    for side in ("left", "right")
                    for variable in term_variables(comparison.get(side))
                }
                for atom in [
                    *(constraint.get("antecedent") or []),
                    *(exists.get("atoms") or []),
                ]:
                    if not isinstance(atom, Mapping) or not isinstance(atom.get("fact_type"), str):
                        continue
                    for role_name, term in atom_bind(dict(atom)).items():
                        variables = term_variables(term)
                        coordinate = (str(atom["fact_type"]), str(role_name))
                        if coordinate in effective and (
                            term_bearing or used.intersection(variables)
                        ):
                            coordinates.add(coordinate)
            constraint_roles[index] = frozenset(coordinates)
        derivation_roles: dict[str, frozenset[tuple[str, str]]] = {}
        for fact_type in model.fact_types:
            fact_id = str(fact_type.get("id"))
            coordinates = {coordinate for coordinate in effective if coordinate[0] == fact_id}
            rule = fact_type.get("derivation_rule")
            if isinstance(rule, Mapping):
                for atom in [*(rule.get("body") or []), *(rule.get("negate") or [])]:
                    if not isinstance(atom, Mapping) or not isinstance(atom.get("fact_type"), str):
                        continue
                    for role_name in atom_bind(dict(atom)):
                        coordinate = (str(atom["fact_type"]), str(role_name))
                        if coordinate in effective:
                            coordinates.add(coordinate)
            derivation_roles[fact_id] = frozenset(coordinates)
        changed = True
        while changed:
            changed = False
            for fact_type in model.fact_types:
                fact_id = str(fact_type.get("id"))
                rule = fact_type.get("derivation_rule")
                if not isinstance(rule, Mapping):
                    continue
                coordinates = set(derivation_roles.get(fact_id, frozenset()))
                for atom in [*(rule.get("body") or []), *(rule.get("negate") or [])]:
                    if isinstance(atom, Mapping):
                        coordinates.update(
                            derivation_roles.get(str(atom.get("fact_type")), frozenset())
                        )
                frozen = frozenset(coordinates)
                if frozen != derivation_roles.get(fact_id):
                    derivation_roles[fact_id] = frozen
                    changed = True
        from gnd.compiled_obligations import compiled_entries

        return cls(
            declarations=tuple(declarations),
            effective_roles=frozenset(effective),
            redacted_parameters=redacted_parameters,
            _constraint_roles=constraint_roles,
            _constraint_variable_roles=constraint_variable_roles,
            _exists_constraints=frozenset(exists_constraints),
            _parameter_roles=frozen_parameter_roles,
            _derivation_roles=derivation_roles,
            _compiled_roles={
                str(entry['locator']): frozenset(
                    coordinate for coordinate in effective
                    if coordinate[0] == str(entry['subset']['of'])
                ) | derivation_roles.get(str(entry['subset']['of']), frozenset())
                for _op, entry in compiled_entries(model)
            },
        )

    @property
    def active(self) -> bool:
        return bool(self.effective_roles)

    def marker(self, roles: set[tuple[str, str]] | frozenset[tuple[str, str]]) -> dict[str, Any]:
        selected = sorted(f"{fact_type}.{role}" for fact_type, role in roles)
        if not selected:
            raise RedactionProjectionError("a redaction marker requires an effective role")
        return {"redacted": True, "roles": selected}

    def fact_roles(self, fact_type: str) -> frozenset[tuple[str, str]]:
        return frozenset(
            coordinate for coordinate in self.effective_roles if coordinate[0] == fact_type
        )

    def parameter_roles(self, operation: str, parameter: str) -> frozenset[tuple[str, str]]:
        return self._parameter_roles.get(operation, {}).get(parameter, frozenset())

    def derivation_roles(self, fact_type: str) -> frozenset[tuple[str, str]]:
        return self._derivation_roles.get(fact_type, frozenset())

    def verdict_roles(self, row: Mapping[str, Any]) -> frozenset[tuple[str, str]]:
        fact_type = _fact_from_verdict(row)
        if fact_type is not None:
            return self.fact_roles(fact_type) | self.derivation_roles(fact_type)
        reference = row.get("constraint_ref")
        if isinstance(reference, str) and reference in self._compiled_roles:
            return self._compiled_roles[reference]
        match = _TOP_LEVEL_CONSTRAINT.fullmatch(reference) if isinstance(reference, str) else None
        return (
            self._constraint_roles.get(int(match.group(1)), frozenset()) if match else frozenset()
        )

    def metadata(self, mode: RedactionMode) -> dict[str, Any]:
        return {
            "mode": mode,
            "declarations": [declaration.as_dict() for declaration in self.declarations],
        }


@dataclass(frozen=True)
class EmitterSpec:
    id: str
    kind: str
    surface: str
    format: str
    capture: list[str]
    reachable_exits: list[int]


def emitter_specs() -> tuple[EmitterSpec, ...]:
    """The closed output census exercised by the Phase-4 leak matrix."""

    rows = (
        ("api-population-verbalization", "population-verbalization", "api", "object", ("return",), (0, 3, 70)),
        ("cli-population-verbalization-text", "population-verbalization", "cli", "text", ("stdout", "stderr"), (0, 3, 64, 70)),
        ("cli-population-verbalization-jsonl", "population-verbalization", "cli", "jsonl", ("stdout", "stderr"), (0, 3, 64, 70)),
        ("api-validate", "validate", "api", "object", ("return",), (0, 3, 70)),
        ("api-check", "check", "api", "object", ("return",), (0, 1, 2, 3, 4, 70)),
        ("api-diff", "diff", "api", "object", ("return",), (0, 3, 70, 74)),
        ("cli-diff-json", "diff", "cli", "json", ("stdout", "stderr"), (0, 3, 64, 70, 74)),
        ("cli-diff-text", "diff", "cli", "text", ("stdout", "stderr"), (0, 3, 64, 70, 74)),
        ("api-transition-full", "transition", "api", "object", ("return",), (0, 1, 2, 3, 4, 70)),
        ("api-transition-plan", "plan", "api", "object", ("return",), (0, 1, 2, 3, 4, 70)),
        ("cli-validate-json", "validate", "cli", "json", ("stdout", "stderr"), (0, 3, 64, 70)),
        ("cli-validate-text", "validate", "cli", "text", ("stdout", "stderr"), (0, 3, 64, 70)),
        ("cli-check-json", "check", "cli", "json", ("stdout", "stderr"), (0, 1, 2, 3, 4, 64, 70)),
        ("cli-check-text", "check", "cli", "text", ("stdout", "stderr"), (0, 1, 2, 3, 4, 64, 70)),
        (
            "cli-verify-json",
            "verify",
            "cli",
            "json",
            ("stdout", "stderr", "written-output"),
            (0, 1, 2, 3, 4, 64, 70, 74),
        ),
        (
            "cli-verify-text",
            "verify",
            "cli",
            "text",
            ("stdout", "stderr", "written-output"),
            (0, 1, 2, 3, 4, 64, 70, 74),
        ),
        (
            "cli-transition-full-json",
            "transition",
            "cli",
            "json",
            ("stdout", "stderr"),
            (0, 1, 2, 3, 4, 64, 70),
        ),
        (
            "cli-transition-full-text",
            "transition",
            "cli",
            "text",
            ("stdout", "stderr"),
            (0, 1, 2, 3, 4, 64, 70),
        ),
        (
            "cli-transition-plan-json",
            "plan",
            "cli",
            "json",
            ("stdout", "stderr"),
            (0, 1, 2, 3, 4, 64, 70),
        ),
        (
            "cli-transition-plan-text",
            "plan",
            "cli",
            "text",
            ("stdout", "stderr"),
            (0, 1, 2, 3, 4, 64, 70),
        ),
        (
            "cli-batch-json",
            "batch",
            "cli",
            "json",
            ("stdout", "stderr", "rows"),
            (0, 1, 2, 3, 4, 64, 66, 70, 74),
        ),
        (
            "cli-measure-json",
            "measure",
            "cli",
            "json",
            ("stdout", "stderr", "written-output"),
            (0, 3, 5, 6, 64, 70, 74),
        ),
        (
            "cli-measure-text",
            "measure",
            "cli",
            "text",
            ("stdout", "stderr", "written-output"),
            (0, 3, 5, 6, 64, 70, 74),
        ),
        (
            "session-feedback-json",
            "session-feedback",
            "session",
            "json",
            ("feedback",),
            (0, 1, 2, 3, 4, 70),
        ),
        (
            "session-attempt-json",
            "session-attempt",
            "session",
            "json",
            ("attempt-evidence",),
            (0, 1, 2, 3, 4, 70),
        ),
        (
            "session-result-json",
            "session-result",
            "session",
            "json",
            ("result",),
            (0, 1, 2, 3, 4, 70),
        ),
        (
            "session-retained-verifier-json",
            "session-feedback",
            "session",
            "json",
            ("retained-verifier-bytes",),
            (0, 1, 2, 3, 4, 70),
        ),
    )
    return tuple(
        EmitterSpec(identifier, kind, surface, format_, list(capture), list(exits))
        for identifier, kind, surface, format_, capture, exits in rows
    )


def _walk_mappings(value: Any):
    if isinstance(value, Mapping):
        yield value
        for child in value.values():
            yield from _walk_mappings(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from _walk_mappings(child)


def _fact_from_verdict(row: Mapping[str, Any]) -> str | None:
    fact_type = row.get("fact_type")
    if isinstance(fact_type, str):
        return fact_type
    reference = row.get("constraint_ref")
    if isinstance(reference, str) and (match := _CONSTRAINT_FACT.search(reference)):
        return match.group(1)
    derivation = row.get("derivation_ref")
    if isinstance(derivation, str) and derivation.startswith("derivation:"):
        return derivation.split(":", 1)[1]
    return None


def _project_fact(row: dict[str, Any], fact_type: str, policy: RedactionPolicy) -> None:
    selected = policy.fact_roles(fact_type)
    for selected_fact, role in selected:
        if selected_fact == fact_type and role in row:
            row[role] = policy.marker({(fact_type, role)})


def _project_issue(row: dict[str, Any], policy: RedactionPolicy) -> None:
    path = row.get("path")
    if not isinstance(path, str):
        return
    fact_match = _FACT_PATH.search(path)
    if fact_match and (fact_match.group(1), fact_match.group(2)) in policy.effective_roles:
        row["message"] = INSTANCE_DETAIL
        return
    if _STEP_BINDINGS_PATH.search(path) and policy.redacted_parameters:
        row["message"] = INSTANCE_DETAIL
        return
    binding_match = _STEP_BINDING_PATH.search(path)
    if binding_match:
        parameter = binding_match.group(1)
        if any(parameter in parameters for parameters in policy.redacted_parameters.values()):
            row["message"] = INSTANCE_DETAIL


def _project_verdict(
    row: dict[str, Any],
    policy: RedactionPolicy,
    *,
    operation: str | None = None,
) -> None:
    reference = row.get("constraint_ref")
    match = _TOP_LEVEL_CONSTRAINT.fullmatch(reference) if isinstance(reference, str) else None
    constraint_index = int(match.group(1)) if match else -1
    if constraint_index in policy._exists_constraints:
        variables = policy._constraint_variable_roles.get(constraint_index, {})
        # Dependency failures may carry a derivation binding in prose rather
        # than in offending_facts. The binding names come from the source
        # derivation and need not match the constraint's variable names, so
        # mask the whole detail message when it contains serialized values.
        message = row.get("message")
        redacted = isinstance(message, str) and "binding=" in message
        witnesses = row.get("offending_facts")
        if isinstance(witnesses, list):
            for witness in witnesses:
                if not isinstance(witness, dict):
                    continue
                for variable, roles in variables.items():
                    if variable in witness:
                        witness[variable] = policy.marker(set(roles))
                        redacted = True
        if redacted:
            row["message"] = INSTANCE_DETAIL
        return
    selected = set(policy.verdict_roles(row))
    locator = row.get("locator")
    binding_match = _STEP_BINDING_PATH.search(locator) if isinstance(locator, str) else None
    if operation is not None and binding_match:
        selected.update(policy.parameter_roles(operation, binding_match.group(1)))
    if operation is not None and row.get("kind") == "create-freshness":
        for parameter in policy.redacted_parameters.get(operation, frozenset()):
            selected.update(policy.parameter_roles(operation, parameter))
    if not selected:
        return
    row["message"] = INSTANCE_DETAIL
    witnesses = row.get("offending_facts")
    if isinstance(witnesses, list) and witnesses:
        row["offending_facts"] = [policy.marker(set(selected))]
    if row.get("value") is not None:
        row["value"] = policy.marker(set(selected))


def _project_derivation(row: dict[str, Any], policy: RedactionPolicy) -> None:
    fact_type = _fact_from_verdict(row)
    if fact_type is None:
        return
    selected = policy.derivation_roles(fact_type)
    if not selected:
        return
    if row.get("message") is not None:
        row["message"] = INSTANCE_DETAIL
    for finding in row.get("findings") or []:
        if not isinstance(finding, dict) or finding.get("witness") is None:
            continue
        finding["witness"] = policy.marker(set(selected))
        finding["message"] = INSTANCE_DETAIL


def _project_snapshot(snapshot: Any, policy: RedactionPolicy) -> None:
    if not isinstance(snapshot, dict):
        return
    for verdict in snapshot.get("verdicts") or []:
        if isinstance(verdict, dict):
            _project_verdict(verdict, policy)
    for derivation in snapshot.get("derivations") or []:
        if isinstance(derivation, dict):
            _project_derivation(derivation, policy)


def _project_transition(block: Any, policy: RedactionPolicy) -> None:
    if not isinstance(block, dict):
        return
    _project_snapshot(block.get("pre_snapshot"), policy)
    _project_snapshot(block.get("post_snapshot"), policy)
    for verdict in block.get("pre_snapshot_verdicts") or []:
        if isinstance(verdict, dict):
            _project_verdict(verdict, policy)
    for verdict in block.get("frame_verdicts") or []:
        if isinstance(verdict, dict):
            _project_verdict(verdict, policy)
    for step in block.get("steps") or []:
        if not isinstance(step, dict):
            continue
        operation = str(step.get("operation"))
        bindings = step.get("bindings")
        if isinstance(bindings, dict):
            for parameter in list(bindings):
                roles = policy.parameter_roles(operation, str(parameter))
                if roles:
                    bindings[parameter] = policy.marker(set(roles))
        for verdict in step.get("verdicts") or []:
            if isinstance(verdict, dict):
                _project_verdict(verdict, policy, operation=operation)
        for change in step.get("derived_changes") or []:
            if not isinstance(change, dict):
                continue
            fact_type = str(change.get("fact_type"))
            for direction in ("added", "removed"):
                rows = change.get(direction) or []
                for row in rows:
                    if isinstance(row, dict):
                        _project_fact(row, fact_type, policy)
                unique: dict[str, Any] = {}
                for row in rows:
                    unique.setdefault(canonical_json_text(row), row)
                change[direction] = list(unique.values())
            record_branch("report:transition-derived-changes:n-a:projected")
        _project_snapshot(step.get("intermediate"), policy)
    computed = block.get("computed_post")
    if isinstance(computed, dict):
        facts = computed.get("facts")
        if isinstance(facts, dict):
            for fact_type, rows in facts.items():
                if isinstance(rows, list):
                    for row in rows:
                        if isinstance(row, dict):
                            _project_fact(row, str(fact_type), policy)


def _empty_transition() -> dict[str, Any]:
    return {
        "evaluated": False,
        "model_digest": None,
        "operations_digest": None,
        "pre_digest": None,
        "pre_snapshot": None,
        "pre_snapshot_verdicts": None,
        "steps": None,
        "frame_grading": None,
        "frame_status": None,
        "frame_verdicts": None,
        "computed_post": None,
        "post_snapshot": None,
    }


def _select_successor(kind: OutputKind, payload: dict[str, Any]) -> None:
    if kind == "admission":
        payload["schema_version"] = 13 if payload.get("schema_version") == 13 else 10
        payload.setdefault("admission", {"admitted": [], "blocked": []})
        return
    if kind in {"validate", "check", "verify", "transition", "plan"}:
        payload["schema_version"] = 9
        payload["post"] = (
            "declared" if kind == "transition" else "computed" if kind == "plan" else None
        )
        if payload.get("transition") is None:
            payload["transition"] = _empty_transition()
        else:
            payload["transition"].setdefault("frame_status", None)
            payload["transition"].setdefault("computed_post", None)
        payload.setdefault("derivations", None)
        payload.setdefault("model_digest", None)
        payload.setdefault("assurance", None)
    elif kind == "batch":
        payload["schema_version"] = 2
    elif kind == "measure":
        payload["schema_version"] = 3
    elif kind in {"session-feedback", "session-attempt"}:
        payload["schema_version"] = 6
    elif kind == "session-result":
        payload["schema_version"] = 4


def project_output(
    kind: OutputKind,
    value: Mapping[str, Any],
    *,
    policy: RedactionPolicy,
    mode: RedactionMode,
    case_id: str | None = None,
    emitter_id: str | None = None,
) -> dict[str, Any]:
    """Return a projected copy of one completed output payload."""

    if mode not in {"applied", "unredacted"}:
        raise RedactionProjectionError(f"unsupported redaction mode: {mode!r}")
    if emitter_id is not None and emitter_id not in {row.id for row in emitter_specs()}:
        raise RedactionProjectionError(f"unregistered redaction emitter: {emitter_id!r}")
    try:
        payload = copy.deepcopy(dict(value))
        if kind == "diff":
            if mode == "applied" and policy.active:
                marker = policy.marker(policy.effective_roles)
                for row in payload.get("populations", ()):
                    for direction in ("a_to_b", "b_to_a"):
                        for gap in row.get(direction, ()):
                            gap["offending_facts"] = [marker for _ in gap.get("offending_facts", ())]
                            if gap.get("witness_sentence") is not None:
                                gap["witness_sentence"] = INSTANCE_DETAIL
                    for difference in row.get("derivations", ()):
                        difference["tuple"] = marker
                        difference["offending_facts"] = [marker for _ in difference.get("offending_facts", ())]
            return payload
        if kind == "population-verbalization":
            if mode == "applied" and policy.active:
                for row in payload.get("rows", ()):
                    if not isinstance(row, dict) or not isinstance(row.get("roles"), dict):
                        raise RedactionProjectionError("invalid population verbalization row")
                    fact_type = row["fact_ref"]["fact_type"]
                    for role in row["roles"]:
                        coordinate = (fact_type, role)
                        if coordinate in policy.effective_roles:
                            row["roles"][role] = policy.marker({coordinate})
                    # A source slice for another fact can overlap a secret.
                    row["excerpt_candidates"] = {}
            return payload
        if not policy.active:
            if kind == "measure" and payload.get("schema_version") == 3:
                payload["redaction"] = policy.metadata(mode)
            return payload
        if case_id is not None:
            policy = RedactionPolicy(
                declarations=tuple(
                    RedactionDeclaration(
                        case_id,
                        declaration.source,
                        declaration.fact_type,
                        declaration.roles,
                    )
                    for declaration in policy.declarations
                ),
                effective_roles=policy.effective_roles,
                redacted_parameters=policy.redacted_parameters,
                _constraint_roles=policy._constraint_roles,
                _constraint_variable_roles=policy._constraint_variable_roles,
                _exists_constraints=policy._exists_constraints,
                _parameter_roles=policy._parameter_roles,
                _derivation_roles=policy._derivation_roles,
                _compiled_roles=policy._compiled_roles,
            )
        _select_successor(kind, payload)
        if mode == "applied":
            for issue in payload.get("issues") or []:
                if isinstance(issue, dict):
                    _project_issue(issue, policy)
            for warning in payload.get("warnings") or []:
                if isinstance(warning, dict):
                    _project_issue(warning, policy)
            for verdict in payload.get("verdicts") or []:
                if isinstance(verdict, dict):
                    if kind == "admission":
                        typed = verdict["offending_facts"]
                        verdict["offending_facts"] = verdict["witnesses"]
                        _project_verdict(verdict, policy)
                        verdict["witnesses"] = verdict["offending_facts"]
                        verdict["offending_facts"] = typed
                    else:
                        _project_verdict(verdict, policy)
            for derivation in payload.get("derivations") or []:
                if isinstance(derivation, dict):
                    _project_derivation(derivation, policy)
            _project_transition(payload.get("transition"), policy)
            for row in payload.get("rows") or []:
                if not isinstance(row, dict):
                    continue
                for issue in row.get("issues") or []:
                    if isinstance(issue, dict):
                        _project_issue(issue, policy)
            for constraint in payload.get("per_constraint") or payload.get("constraints") or []:
                if not isinstance(constraint, dict):
                    continue
                evidence = constraint.get("evidence")
                if isinstance(evidence, dict) and isinstance(evidence.get("verdict"), dict):
                    _project_verdict(evidence["verdict"], policy)
            error = payload.get("error")
            if isinstance(error, dict) and error.get("message") is not None:
                error["message"] = INSTANCE_DETAIL
        payload["redaction"] = policy.metadata(mode)
        return payload
    except RedactionProjectionError:
        raise
    except Exception as error:
        raise RedactionProjectionError(str(error)) from error


def render_text_header(payload: Mapping[str, Any]) -> str | None:
    """Render the symmetric first text line for a successor payload."""

    metadata = payload.get("redaction")
    if not isinstance(metadata, Mapping):
        return None
    coordinates = sorted(
        {
            f"{row['fact_type']}.{role}"
            for row in metadata.get("declarations", ())
            if isinstance(row, Mapping) and isinstance(row.get("fact_type"), str)
            for role in row.get("roles", ())
            if isinstance(role, str)
        }
    )
    return f"REDACTION {metadata.get('mode')}: {', '.join(coordinates)}"


def project_failure(
    kind: OutputKind,
    value: Mapping[str, Any],
    *,
    policy: RedactionPolicy,
    mode: RedactionMode,
) -> dict[str, Any]:
    """Select the successor envelope after projection itself failed.

    ``value`` must be a newly built, witness-free exit-70 envelope.  This helper
    intentionally does not call :func:`project_output`, so a defect in that
    function cannot turn the fail-closed route into recursion.
    """

    try:
        payload = copy.deepcopy(dict(value))
        _select_successor(kind, payload)
        if mode == "applied" and isinstance(payload.get("error"), dict):
            payload["error"]["message"] = INSTANCE_DETAIL
        payload["redaction"] = policy.metadata(mode)
        return payload
    except Exception as error:
        raise RedactionProjectionError(str(error)) from error
