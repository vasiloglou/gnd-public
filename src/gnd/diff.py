"""Conservative, read-only comparison of two models over one vocabulary."""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Mapping, Sequence
from random import Random
from typing import Any

from gnd.address import positional_constraint_ref
from gnd.artifacts import canonical_json_bytes
from gnd.artifacts import sha256_hex as _digest
from gnd.checker import _compare, _identity_token, _partial_compatible, structured_extension_view
from gnd.extract.anchors import vocabulary_digest
from gnd.model import Model
from gnd.population import PopulationLoadError, load_population_bytes
from gnd.verbalize_population import (
    PopulationVerbalizationError,
    render_witness,
    validate_model_object,
)


class DiffError(ValueError):
    """A diff input violates its contract."""




def _constraints(model: Model) -> list[tuple[str, str, dict[str, Any]]]:
    rows = []
    for fact in model.fact_types:
        for index, constraint in enumerate(fact.get("constraints") or []):
            rows.append((positional_constraint_ref(str(fact["id"]), index), str(fact["id"]), constraint))
    for index, constraint in enumerate(model.constraints):
        rows.append((positional_constraint_ref(None, index), "", constraint))
    return rows


def _range_contains(left: Mapping[str, Any], right: Mapping[str, Any], primitive: str) -> bool:
    for key, inclusive in (("min", "min_inclusive"), ("max", "max_inclusive")):
        a, b = left.get(key), right.get(key)
        if b is None:
            continue
        if a is None:
            return False
        outside = _compare(a, "<" if key == "min" else ">", b, primitive, primitive)
        equal = _compare(a, "=", b, primitive, primitive)
        if outside is None or equal is None or outside:
            return False
        if equal and left.get(inclusive, True) and not right.get(inclusive, True):
            return False
    return True


def _guard_parts(constraint: Mapping[str, Any]) -> tuple[Any, Any]:
    names: dict[str, str] = {}

    def normalize(value: Any) -> Any:
        if isinstance(value, str) and re.fullmatch(r"\$[A-Za-z_][A-Za-z0-9_]*", value):
            return names.setdefault(value, f"$v{len(names)}")
        if isinstance(value, Mapping):
            return {key: normalize(value[key]) for key in sorted(value)}
        if isinstance(value, list):
            return [normalize(item) for item in value]
        return value

    return normalize(constraint.get("antecedent")), normalize(constraint.get("consequent"))


def _implies(family: str, left: Mapping[str, Any], right: Mapping[str, Any], primitive: str | None) -> tuple[bool, str]:
    if left.get("modality") != right.get("modality"):
        return False, "different-modality"
    if family not in {"uniqueness", "mandatory", "mandatory-disjunctive", "subset", "exclusion", "value", "guarded"}:
        return False, "no-catalogue-rule"
    if family == "uniqueness":
        lroles, rroles = left.get("roles"), right.get("roles")
        if isinstance(lroles, list) and isinstance(rroles, list) and set(lroles) <= set(rroles):
            return True, ""
        lrefs, rrefs = left.get("role_refs"), right.get("role_refs")
        if (isinstance(lrefs, list) and isinstance(rrefs, list)
                and {canonical_json_bytes(ref) for ref in lrefs} <= {canonical_json_bytes(ref) for ref in rrefs}):
            return True, ""
    elif family == "mandatory":
        if left.get("role") == right.get("role") and left.get("role") is not None:
            return True, ""
    elif family == "mandatory-disjunctive":
        lrefs, rrefs = left.get("role_refs"), right.get("role_refs")
        if isinstance(lrefs, list) and isinstance(rrefs, list) and {canonical_json_bytes(ref) for ref in lrefs} == {canonical_json_bytes(ref) for ref in rrefs}:
            return True, ""
    elif family in {"subset", "exclusion"}:
        keys = ("subset_role_seq", "superset_role_seq") if family == "subset" else ("role_seq_a", "role_seq_b")
        if all(left.get(key) is not None and left.get(key) == right.get(key) for key in keys):
            return True, ""
    elif family == "value":
        same_subject = left.get("object_type") == right.get("object_type") and left.get("role_ref") == right.get("role_ref")
        if same_subject:
            if (isinstance(left.get("allowed"), list) and isinstance(right.get("allowed"), list)
                    and {canonical_json_bytes(x) for x in left["allowed"]} <= {canonical_json_bytes(x) for x in right["allowed"]}):
                return True, ""
            l_ranges = left.get("ranges") or ([left["range"]] if isinstance(left.get("range"), Mapping) else [])
            r_ranges = right.get("ranges") or ([right["range"]] if isinstance(right.get("range"), Mapping) else [])
            if primitive is not None and l_ranges and r_ranges and all(
                any(_range_contains(lrange, rrange, primitive) for rrange in r_ranges)
                for lrange in l_ranges
            ):
                return True, ""
    elif family == "guarded":
        lantecedent, lconsequent = _guard_parts(left)
        rantecedent, rconsequent = _guard_parts(right)
        if lantecedent == rantecedent and lconsequent == rconsequent:
            return True, ""
        if lantecedent == rantecedent:
            lcmp = (lconsequent or {}).get("comparison")
            rcmp = (rconsequent or {}).get("comparison")
            if (isinstance(lcmp, Mapping) and isinstance(rcmp, Mapping)
                    and lcmp.get("left") == rcmp.get("left")
                    and lcmp.get("operator") == rcmp.get("operator")):
                try:
                    lv, rv = lcmp["right"], rcmp["right"]
                    if (type(lv) is type(rv) and isinstance(lv, (int, float))
                            and not isinstance(lv, bool)
                            and ((lcmp["operator"] in {"<", "<="} and lv <= rv)
                                 or (lcmp["operator"] in {">", ">="} and lv >= rv))):
                        return True, ""
                except (KeyError, TypeError):
                    pass
    return False, "no-catalogue-rule"


def compare_constraints(model_a: Model, model_b: Model) -> list[dict[str, Any]]:
    """Compare ordered constraint pairs within their family and subject."""
    out = []
    for from_id, to_id, left_model, right_model in (("a", "b", model_a, model_b), ("b", "a", model_b, model_a)):
        index: dict[tuple[str, str, str], list[tuple[str, dict[str, Any]]]] = defaultdict(list)
        for ref, scope, constraint in _constraints(right_model):
            family = str(constraint.get("type"))
            subject = str((constraint.get("object_type"), constraint.get("role_ref"))) if family == "value" else ""
            index[(family, scope, subject)].append((ref, constraint))
        for left_ref, scope, left in _constraints(left_model):
            family = str(left.get("type"))
            subject = str((left.get("object_type"), left.get("role_ref"))) if family == "value" else ""
            primitive = next((str(obj.get("primitive")) for obj in left_model.object_types if obj.get("id") == left.get("object_type")), None)
            for right_ref, right in index.get((family, scope, subject), ()):
                implies, reason = _implies(family, left, right, primitive)
                out.append({"from_model": from_id, "to_model": to_id, "left_ref": left_ref,
                            "right_ref": right_ref, "family": family,
                            "result": "implies" if implies else "undecided", "reason": None if implies else reason})
    return sorted(out, key=lambda row: (row["family"], row["from_model"], row["left_ref"], row["right_ref"]))


def _summary(report: dict[str, Any]) -> dict[str, Any]:
    return {"state": "checked", "band": report["exit_code"],
            "has_vacuous": any(v["verdict"] == "vacuous" for v in report.get("verdicts", ())),
            "verdicts": [{"ref": v["constraint_ref"], "verdict": v["verdict"]} for v in report.get("verdicts", ())],
            "derivation_verdicts": [{"ref": v["derivation_ref"], "verdict": v["verdict"]} for v in report.get("derivations") or ()]}


def _tuple_status(view: Any, population: Any, derived: bool, head: str, binding: Mapping[str, Any], roles: tuple[str, ...]) -> str:
    if any(isinstance(binding.get(role), Mapping) and "$opaque" in binding[role] for role in roles):
        return "unknown"
    def same(row: Mapping[str, Any]) -> bool:
        return all(_identity_token(row[role]) == _identity_token(binding[role]) for role in roles)

    if not derived:
        return "in" if any(same(row) for row in population.facts.get(head, ())) else "out"
    if any(same(row) for row in view.facts.get(head, ())):
        return "in"
    if head in view.unavailable:
        return "unknown"
    values = tuple(binding[role] for role in roles)
    if any(all(_partial_compatible(a, b) for a, b in zip(values, pattern, strict=True)) for pattern in view.possible.get(head, ())):
        return "unknown"
    return "out"


def _derivation_rows(model_a: Model, model_b: Model, pop_a: Any, pop_b: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    view_a, view_b = structured_extension_view(model_a, pop_a), structured_extension_view(model_b, pop_b)
    rows: list[dict[str, Any]] = []
    a_to_b: list[dict[str, Any]] = []
    b_to_a: list[dict[str, Any]] = []
    facts_b = {str(fact["id"]): fact for fact in model_b.fact_types}
    for fact in model_a.fact_types:
        head = str(fact["id"])
        derived_a = fact.get("derivation") == "derived"
        derived_b = facts_b[head].get("derivation") == "derived"
        if not (derived_a or derived_b):
            continue
        roles = tuple(str(role["role_name"]) for role in fact["roles"])
        candidates = {canonical_json_bytes(dict(row)): dict(row) for row in (*pop_a.facts.get(head, ()), *pop_b.facts.get(head, ()), *view_a.facts.get(head, ()), *view_b.facts.get(head, ()))}
        for binding in (candidates[key] for key in sorted(candidates)):
            if any(isinstance(binding.get(role), Mapping) and "$opaque" in binding[role] for role in roles):
                continue
            opaque_a = derived_a and not isinstance(fact.get("derivation_rule"), Mapping)
            opaque_b = derived_b and not isinstance(facts_b[head].get("derivation_rule"), Mapping)
            a_status = "unknown" if opaque_a else _tuple_status(view_a, pop_a, derived_a, head, binding, roles)
            b_status = "unknown" if opaque_b else _tuple_status(view_b, pop_b, derived_b, head, binding, roles)
            if a_status == b_status:
                continue
            if "unknown" in (a_status, b_status):
                outcome = "unresolved"
            else:
                out_population = pop_a if a_status == "out" else pop_b
                claimed = any(all(_identity_token(row[role]) == _identity_token(binding[role]) for role in roles)
                              for row in out_population.facts.get(head, ())
                              if all(not isinstance(row.get(role), Mapping) for role in roles))
                outcome = "unsound" if claimed else "incomplete"
            rows.append({"fact_type": head, "tuple": binding, "a_status": a_status,
                         "b_status": b_status, "outcome": outcome, "offending_facts": [binding]})
            try:
                sentence = render_witness(model_a, head, binding, unredacted=True)
            except PopulationVerbalizationError:
                sentence = None
            for source, target, dest in ((a_status, b_status, a_to_b), (b_status, a_status, b_to_a)):
                if source == "in" and target != "in":
                    dest.append({"target_ref": f"derivation:{head}",
                                 "verdict": "unchecked" if target == "unknown" else "fail",
                                 "offending_facts": [binding], "witness_sentence": sentence})
    return rows, a_to_b, b_to_a


def compare_population(model_a: Model, model_b: Model, population_bytes: bytes, *, source: str, population_ref: str, origin: str = "provided") -> dict[str, Any]:
    """Load the same bytes independently under both models and compare results."""
    from gnd import checker, checking_service

    populations = []
    reports = []
    for model in (model_a, model_b):
        try:
            population = load_population_bytes(population_bytes, source=source, model=model)
        except PopulationLoadError as error:
            populations.append(None)
            reports.append({"state": "not_comparable", "rule": type(error).__name__})
            continue
        populations.append(population)
        payload = checking_service.check_report(
            model, population, evaluator=checker.check_partial, admission=True, unredacted=True
        ).payload
        reports.append(payload.get("report", payload))
    summary = [_summary(r) if pop is not None else r for pop, r in zip(populations, reports, strict=True)]
    a_to_b: list[dict[str, Any]] = []
    b_to_a: list[dict[str, Any]] = []
    derivations: list[dict[str, Any]] = []
    if all(pop is not None for pop in populations):
        for source_report, target_report, dest in ((reports[0], reports[1], a_to_b), (reports[1], reports[0], b_to_a)):
            if source_report["exit_code"] == 0:
                for verdict in target_report.get("verdicts", ()):
                    if verdict["verdict"] == "fail":
                        dest.append({"target_ref": verdict["constraint_ref"], "verdict": "fail",
                                     "offending_facts": verdict.get("witnesses") or [], "witness_sentence": None})
        derivations, derived_ab, derived_ba = _derivation_rows(model_a, model_b, *populations)
        a_to_b.extend(derived_ab)
        b_to_a.extend(derived_ba)
    return {"population_ref": population_ref, "population_sha256": _digest(population_bytes),
            "origin": origin, "a": summary[0], "b": summary[1], "a_to_b": a_to_b,
            "b_to_a": b_to_a, "derivations": derivations}


def _structured(model: Model) -> bool:
    return any(fact.get("derivation_rule") for fact in model.fact_types)


def diff_models(
    model_a: Model,
    model_b: Model,
    *,
    populations: Sequence[tuple[str, bytes]] = (),
    synthesize: bool = True,
    seed: int = 0,
) -> dict[str, Any]:
    """Produce a bounded differential report without mutating either model."""
    for model in (model_a, model_b):
        from gnd.terms import require_non_temporal

        require_non_temporal(model, "diff")
        validate_model_object(model)
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        raise DiffError("diff:invalid-seed")
    vocab_a, vocab_b = vocabulary_digest(model_a), vocabulary_digest(model_b)
    if vocab_a != vocab_b:
        raise DiffError("diff:vocabulary-mismatch")
    rows = []
    for name, raw in populations:
        if not isinstance(name, str) or not isinstance(raw, bytes):
            raise DiffError("diff:invalid-population-input")
        try:
            load_population_bytes(raw, source=name)
        except (PopulationLoadError, UnicodeError, RecursionError, ValueError, TypeError) as error:
            raise DiffError(f"diff:invalid-population:{name}:{type(error).__name__}") from error
        except Exception as error:  # untrusted YAML/JSON parser boundary
            raise DiffError(f"diff:invalid-population:{name}:{type(error).__name__}") from error
        rows.append(compare_population(model_a, model_b, raw, source=name, population_ref=name))
    not_derivable: list[dict[str, str]] = []
    if synthesize:
        from gnd.synth.assemble import GeneratorError, assemble_conforming
        from gnd.synth.boundary import derive_boundary_cases

        for source_id, model in (("a", model_a), ("b", model_b)):
            if model.reference_populations:
                not_derivable.append(
                    {
                        "source": source_id,
                        "kind": "synthesis",
                        "subject": "model",
                        "reason": "fixed reference synthesis unavailable",
                    }
                )
                continue
            if _structured(model):
                not_derivable.append({"source": source_id, "kind": "synthesis", "subject": "model",
                                      "reason": "structured derivation synthesis unavailable"})
                continue
            try:
                assembly = assemble_conforming(model, seed, model_ref=f"model-{source_id}.orm.yaml")
            except GeneratorError as error:
                not_derivable.append({"source": source_id, "kind": "synthesis", "subject": "model", "reason": str(error)})
                continue
            raw = canonical_json_bytes(assembly.doc)
            rows.append(compare_population(model_a, model_b, raw, source=f"synth-{source_id}.pop.json",
                                           population_ref=f"synth-{source_id}-conforming", origin=f"synth-{source_id}-conforming"))
            other = model_b if source_id == "a" else model_a
            for boundary_model, origin in ((other, "other-model-boundary"),
                                           (model, f"synth-{source_id}-boundary")):
                for ref, _, _ in _constraints(boundary_model):
                    cases, refusals = derive_boundary_cases(boundary_model, ref, assembly.doc, Random(seed))
                    for refusal in refusals:
                        not_derivable.append({"source": source_id, "kind": "boundary",
                                              "subject": ref, "reason": refusal.reason})
                    for candidate in cases:
                        boundary_raw = canonical_json_bytes(candidate.doc)
                        row = compare_population(model_a, model_b, boundary_raw,
                                                 source=f"boundary-{source_id}.pop.json",
                                                 population_ref=f"{origin}:{source_id}:{ref}:{candidate.name}",
                                                 origin=origin)
                        source_summary = row[source_id]
                        target_summary = row["b" if source_id == "a" else "a"]
                        if source_summary.get("band") == 0 and target_summary.get("band") in {1, 4}:
                            rows.append(row)
    from gnd.references import reference_model_digest

    return {
        "schema_version": "gnd-diff/1",
        "command": "diff",
        "model_a_digest": reference_model_digest(model_a)
        if model_a.reference_populations
        else "sha256:" + _digest(canonical_json_bytes(model_a.model_dump(exclude={"warnings"}))),
        "model_b_digest": reference_model_digest(model_b)
        if model_b.reference_populations
        else "sha256:" + _digest(canonical_json_bytes(model_b.model_dump(exclude={"warnings"}))),
        "vocabulary_digest": vocab_a,
        "seed": seed,
        "assurance": "none",
        "entailment": compare_constraints(model_a, model_b),
        "populations": rows,
        "not_derivable": not_derivable,
    }
