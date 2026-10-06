"""Validate an admission partition against bound facts and supplied findings.

The mechanical judgments are trusted inputs; this module never reevaluates a
constraint. It reuses the occurrence/dependency projection used by emission.
"""

from __future__ import annotations

from collections import Counter
from types import SimpleNamespace

from jsonschema import Draft202012Validator

from gnd.address import positional_constraint_ref
from gnd.admission import build_admission
from gnd.artifacts import canonical_json_bytes
from gnd.documents import Model
from gnd.model import bind_population, resolve_context
from gnd.population import Population
from gnd.report_schema import load_report_schema
from gnd.semantic_adapter import canonical_scalar
from gnd.universe import resolve_primitive, resolve_reference_value_type
from gnd.values import reference_model_digest

_VALIDATOR = Draft202012Validator(load_report_schema())


class AdmissionValidationError(ValueError):
    pass


def constraint_annotations(model):
    return {
        **{
            positional_constraint_ref(str(ft["id"]), i): row
            for ft in model.fact_types
            for i, row in enumerate(ft.get("constraints", []))
        },
        **{positional_constraint_ref(None, i): row for i, row in enumerate(model.constraints)},
    }


def validate_reference_transport(payload, *, model, references, expected_version):
    if (
        not isinstance(payload, dict)
        or payload.get("schema_version") != expected_version
        or next(_VALIDATOR.iter_errors(payload), None) is not None
    ):
        raise AdmissionValidationError("reference wrapper structural validation failed")
    context = resolve_context(model, references)
    binding = {
        "identity_version": 1,
        "references": [
            {"id": origin.id, "sha256": origin.raw_sha256}
            for origin, _path, _raw in context._snapshots
        ],
    }
    if (
        payload["model_digest"] != reference_model_digest(model)
        or payload["reference_binding"] != binding
    ):
        raise AdmissionValidationError("reference wrapper binding differs")
    # Checker/transition wrappers copy these fields. Public diff reports have
    # no nested status; their independently authored outer status is preserved.
    inner = payload["report"]
    fields = ("command", "outcome", "exit_code")
    if all(field in inner for field in fields) and any(
        payload[field] != inner[field] for field in fields
    ):
        raise AdmissionValidationError("reference wrapper status correlation differs")


def validate_admission_payload(
    payload, *, model: Model, candidate: Population, references=None
) -> dict[str, int]:
    try:
        return _validate(payload, model, candidate, references)
    except (ValueError, TypeError, KeyError, AttributeError, IndexError) as error:
        if isinstance(error, AdmissionValidationError):
            raise
        raise AdmissionValidationError("admission input or partition is invalid") from error


def _validate(payload, model, candidate, references):
    if (
        not isinstance(model, Model)
        or not isinstance(candidate, Population)
        or not candidate.matches_validation_marker(model)
    ):
        raise AdmissionValidationError("validated model/candidate binding required")
    from gnd.json_input import validate_json_value

    validate_json_value(payload)
    if not isinstance(payload, dict) or len(canonical_json_bytes(payload)) > 10 * 1024 * 1024:
        raise AdmissionValidationError("bounded report object required")
    errors = list(_VALIDATOR.iter_errors(payload))
    if errors:
        raise AdmissionValidationError("report structural validation failed")
    combined = candidate
    owners = {}
    if model.reference_populations:
        context = resolve_context(model, references)
        view = bind_population(model, candidate, references=context)
        combined = view.combined
        owners = dict(context._owners)
        validate_reference_transport(
            payload,
            model=model,
            references=context,
            expected_version=14 if payload.get("report", {}).get("schema_version") == 13 else 12,
        )
        origins = sorted(
            view.occurrence_origins,
            key=lambda r: (
                r["origin"]["kind"],
                r["origin"]["reference_id"] or "",
                r["fact_type"],
                r["index"],
            ),
        )
        if payload["occurrence_origins"] != origins:
            raise AdmissionValidationError("reference origins or bytes differ")
        inner = payload["report"]
    else:
        if references is not None or payload.get("schema_version") not in {10, 13}:
            raise AdmissionValidationError("candidate admission report required")
        inner = payload
    from gnd.transition import transition_model_identity

    if inner["model_digest"] != transition_model_identity(model):
        raise AdmissionValidationError("model identity differs")
    universe = {(ft, i) for ft, rows in candidate.facts.items() for i in range(len(rows))}
    all_nodes = {(ft, i) for ft, rows in combined.facts.items() for i in range(len(rows))}
    roles = {ft["id"]: {r["role_name"] for r in ft["roles"]} for ft in model.fact_types}

    def coordinate(ref):
        if (
            not isinstance(ref, dict)
            or set(ref) != {"fact_type", "index"}
            or type(ref["index"]) is not int
        ):
            raise AdmissionValidationError("invalid exact occurrence coordinate")
        node = ref["fact_type"], ref["index"]
        if node not in all_nodes:
            raise AdmissionValidationError("coordinate outside bound facts")
        return node

    verdicts, findings = [], []
    counts = Counter()
    constraints = constraint_annotations(model)
    for row in inner["verdicts"]:
        if row["constraint_ref"] not in constraints:
            raise AdmissionValidationError("unknown constraint reference")
        counts[row["verdict"]] += 1
        refs = row["refused_facts"] if row["verdict"] == "unchecked" else row["offending_facts"]
        nodes = [coordinate(ref) for ref in refs]
        if len(set(nodes)) != len(nodes):
            raise AdmissionValidationError("duplicate finding coordinate")
        verdicts.append(SimpleNamespace(**{**row, "fact_refs": refs}))
        findings.append(SimpleNamespace(fact_refs=nodes))
    # Report totals include derivation claims; admission findings remain the
    # constraint projection used by build_admission.
    counts.update(row["verdict"] for row in (inner.get("derivations") or []))
    if dict(inner["counts"]) != {key: counts[key] for key in inner["counts"]}:
        raise AdmissionValidationError("verdict counts disagree")
    seen = set()
    partition = inner["admission"]
    for kind in ("admitted", "blocked"):
        for entry in partition[kind]:
            node = coordinate(entry["fact_ref"])
            if node not in universe or node in seen:
                raise AdmissionValidationError("partition repeats or invents a subject")
            seen.add(node)
            if kind == "admitted":
                deps = []
                for dep in entry["opaque_deps"]:
                    location = coordinate(dep["fact_ref"])
                    if dep["role"] not in roles[location[0]]:
                        raise AdmissionValidationError("unknown opaque role")
                    deps.append((*location, dep["role"]))
                if len(set(deps)) != len(deps):
                    raise AdmissionValidationError("duplicate opaque dependency")
            elif not entry["blocked_by"] or len(set(entry["blocked_by"])) != len(
                entry["blocked_by"]
            ):
                raise AdmissionValidationError("empty or duplicate blockers")
    if seen != universe:
        raise AdmissionValidationError("partition omits subjects")
    report = SimpleNamespace(
        verdicts=verdicts, snapshot_projection=SimpleNamespace(findings=findings)
    )
    expected = build_admission(model, combined, report, max_cells=1000000)
    for kind in expected:
        expected[kind] = [
            row for row in expected[kind] if row["fact_ref"]["fact_type"] not in owners
        ]
    if partition != expected:
        raise AdmissionValidationError(
            "partition disagrees with supplied findings and dependencies"
        )
    unique = set()
    for entry in partition["admitted"]:
        if not entry["opaque_deps"]:
            ft, index = coordinate(entry["fact_ref"])
            fact_type = next(row for row in model.fact_types if row["id"] == ft)
            identity = []
            for role in fact_type["roles"]:
                object_type = role["object_type"]
                primitive = resolve_primitive(
                    resolve_reference_value_type(object_type, model) or object_type, model
                )
                scalar = canonical_scalar(candidate.facts[ft][index][role["role_name"]], primitive)
                if scalar is None:
                    raise AdmissionValidationError("admitted role lacks a scalar identity")
                identity.append((object_type, scalar.identity_kind, scalar.token))
            unique.add((ft, tuple(identity)))
    return {
        "candidate_admitted_occurrences": len(partition["admitted"]),
        "candidate_blocked_occurrences": len(partition["blocked"]),
        "candidate_admitted_unique": len(unique),
    }
