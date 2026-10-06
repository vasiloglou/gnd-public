from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from gnd import input_policy as _rf7_input
from gnd import verbalize
from gnd.commands._output import _print_issues
from gnd.exits import EXIT_NO_INPUT
from gnd.extract.service import _artifact_index_issue, _extract_stem
from gnd.model import ModelValidationError, load_model
from gnd.population import PopulationValidationError, load_population


def _cmd_doccheck(model_path: str, manifest_path: str, artifacts_dir: str) -> int:
    """``gnd doccheck MODEL MANIFEST --artifacts DIR`` — the renderer-obligation
    validator (R-05″), scoped by the applicable set (R-10′/P-2).

    Skill prose explains, validators discharge: every obligation the
    gnd-render-doc skill takes on is checked HERE by code over the document
    manifest. Four obligations: (1) digest binding — document, source
    population and applicable-set bytes hash to what the manifest records;
    (2) rendering — every role filler of every APPLICABLE fact type is
    mentioned in the document under lexical_normalize (direct fillers as their
    value, composite fillers via their component values; inapplicable fact
    types are exempt BY THE ARTIFACT, never by leniency); (3) distractors —
    at least one of each kind, every text present, every absent-fact genuinely
    absent under identity_key; (4) renderer identity fields non-empty.

    Text output only, one line per violation: the consumer is the render-doc
    skill's loop reading exit codes — this is a GATE, not a report, so no JSON
    format exists in v1 (one composing payload per lane).
    """
    import hashlib as _hashlib

    from gnd.extract.identity import identity_key, lexical_normalize
    from gnd.extract.manifest import (
        ManifestError,
        read_document_manifest,
        resolve_manifest_relative_path,
    )
    from gnd.extract.refscheme import applicable_set
    from gnd.fidelity.match import match_fact_type

    try:
        model = load_model(model_path)
        from gnd.terms import require_non_temporal

        require_non_temporal(model, "doccheck")
    except ModelValidationError as error:
        for warning in error.warnings:
            print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")
        _print_issues(error.issues)
        return 3
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"ERROR: {error}")
        return 3

    try:
        manifest = read_document_manifest(manifest_path)
    except ManifestError as error:
        _print_issues(error.issues)
        return 3

    applicable_rel = f"{_extract_stem(model_path)}.applicable.json"
    bundle_issue = _artifact_index_issue(model_path, artifacts_dir, (applicable_rel,))
    if bundle_issue is not None:
        code, message = bundle_issue
        print(f"VIOLATION artifact-index: {verbalize.line_text(message)}")
        return code

    # Manifest-relative resolution (the contract manifest.py enforces: the
    # paths are relative and contained, so this join cannot escape).
    try:
        document_path = resolve_manifest_relative_path(
            manifest_path,
            manifest.document,
            field="document",
            rule_id="document:unsafe-path",
        )
        population_path = resolve_manifest_relative_path(
            manifest_path,
            manifest.source_population,
            field="source_population",
            rule_id="document:unsafe-path",
        )
    except ManifestError as error:
        _print_issues(error.issues)
        return 3
    applicable_path = Path(artifacts_dir) / applicable_rel

    # Fail closed (66, the 01.2/D-22 EX_NOINPUT precedent): a missing required
    # artifact means an obligation CANNOT be checked — never skip it.
    for label, required in (
        ("document", document_path),
        ("source population", population_path),
        ("applicable-set artifact", applicable_path),
    ):
        if not required.is_file():
            print(
                f"MISSING: the {label} at {required} does not exist — every "
                f"obligation is checked or the check refuses to run "
                f"({EXIT_NO_INPUT})"
            )
            return EXIT_NO_INPUT

    try:
        document_bytes = document_path.read_bytes()
        population_bytes = population_path.read_bytes()
        applicable_bytes = applicable_path.read_bytes()
    except OSError as error:
        print(f"MISSING: a manifest-named file could not be read: {error}")
        return EXIT_NO_INPUT

    violations: list[str] = []

    # --- Obligation 1: digest binding (T-02.1-10) ---
    for field, recorded, data in (
        ("document_sha256", manifest.document_sha256, document_bytes),
        (
            "source_population_sha256",
            manifest.source_population_sha256,
            population_bytes,
        ),
        ("applicable_sha256", manifest.applicable_sha256, applicable_bytes),
        ("model_sha256", manifest.model_sha256, Path(model_path).read_bytes()),
    ):
        actual = _hashlib.sha256(data).hexdigest()
        if actual != recorded:
            violations.append(
                f"binding: {field} records {recorded} but the file's bytes "
                f"hash to {actual} — the manifest does not describe this file"
            )

    try:
        applicable = _rf7_input.loads(applicable_bytes.decode("utf-8"))
        if applicable != applicable_set(model):
            print(
                "VIOLATION applicable-set: artifact does not match the "
                "canonical disposition derived from this model"
            )
            return 3
        applicable_ids = {str(row["id"]) for row in applicable["fact_types"] if row["applicable"]}
        object_rows = {str(row["id"]): row for row in applicable["object_types"]}
    except (UnicodeDecodeError, ValueError, KeyError, TypeError) as error:
        print(
            f"VIOLATION applicable-set: {applicable_path} is not a readable "
            f"applicable-set artifact ({error})"
        )
        return 3

    try:
        population = load_population(population_path, model=model)
    except PopulationValidationError as error:
        _print_issues(error.issues)
        return 3
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"ERROR: {error}")
        return 3

    try:
        document_text = document_bytes.decode("utf-8")
    except UnicodeDecodeError as error:
        print(f"VIOLATION document: {document_path} is not UTF-8 text ({error})")
        return 3
    normalized_document = lexical_normalize(document_text)

    def mentioned(value: Any) -> bool:
        rendered = value if isinstance(value, str) else json.dumps(value)
        needle = str(lexical_normalize(rendered))
        if not needle:
            return False
        return re.search(rf"(?<!\w){re.escape(needle)}(?!\w)", normalized_document) is not None

    def distractor_text_present(value: str) -> bool:
        needle = str(lexical_normalize(value))
        return bool(needle) and needle in normalized_document

    def role_object_types(fact_type_id: str) -> dict[str, str]:
        for fact_type in model.fact_types:
            if str(fact_type.get("id")) == fact_type_id:
                return {
                    str(role.get("role_name")): str(role.get("object_type"))
                    for role in fact_type.get("roles") or []
                }
        return {}

    def composite_components(object_type_id: str, value: Any) -> list[tuple[str, Any]] | None:
        """The component values identifying a composite filler (R-10′ path 2),
        looked up through the external UC's role_refs in the SOURCE population.
        ``None`` when the identity is underivable — fail closed, a filler whose
        mention cannot be checked is a violation, not an exemption."""
        row = object_rows.get(object_type_id) or {}
        components: list[tuple[str, Any]] = []
        for role_ref in row.get("role_refs") or []:
            ref_ft = str(role_ref["fact_type"])
            ref_role = str(role_ref["role"])
            anchor_roles = [
                name
                for name, oid in role_object_types(ref_ft).items()
                if oid == object_type_id and name != ref_role
            ]
            matches = [
                fact[ref_role]
                for fact in population.facts.get(ref_ft, [])
                for anchor in anchor_roles
                if anchor in fact
                and ref_role in fact
                and identity_key(fact[anchor]) == identity_key(value)
            ]
            if not matches:
                return None
            components.extend((ref_ft, match) for match in matches)
        return components or None

    # --- Obligation 2: the rendering obligation, over the APPLICABLE set ---
    for fact_type_id, facts in sorted(population.facts.items()):
        if fact_type_id not in applicable_ids:
            continue  # exempt BY THE ARTIFACT (R-10'/P-2), never by leniency
        roles = role_object_types(fact_type_id)
        for fact in facts:
            for role_name, value in fact.items():
                object_type_id = roles.get(str(role_name), "")
                row = object_rows.get(object_type_id) or {}
                if row.get("path") == "composite":
                    components = composite_components(object_type_id, value)
                    if components is None:
                        violations.append(
                            f"rendering: {fact_type_id}.{role_name} filler "
                            f"{value!r} is a composite {object_type_id!r} whose "
                            f"identifying components cannot be derived from the "
                            f"source population — its mention cannot be checked"
                        )
                        continue
                    for component_ft, component in components:
                        if not mentioned(component):
                            violations.append(
                                f"rendering: {fact_type_id}.{role_name} filler "
                                f"{value!r} resolves through component "
                                f"{component!r} (via {component_ft}), which is "
                                f"not mentioned in the document"
                            )
                elif not mentioned(value):
                    violations.append(
                        f"rendering: {fact_type_id}.{role_name} reference value "
                        f"{value!r} is not mentioned in the document"
                    )

    # --- Obligation 3: distractors (R-05) ---
    present_kinds = {distractor.kind for distractor in manifest.distractors}
    for kind in ("out-of-model", "near-miss-entity", "absent-fact"):
        if kind not in present_kinds:
            violations.append(
                f"distractors: no distractor of kind {kind} — all three kinds are mandatory (R-05)"
            )
    for distractor in manifest.distractors:
        if not distractor_text_present(distractor.text):
            violations.append(
                f"distractors: the {distractor.kind} distractor text "
                f"{distractor.text!r} does not appear in the document"
            )
        if distractor.kind == "absent-fact":
            fact_type_id = str(distractor.fact_type)
            declared_roles = set(role_object_types(fact_type_id))
            supplied_roles = set(distractor.roles or {})
            if not declared_roles:
                violations.append(
                    f"distractors: absent-fact names unknown fact type {fact_type_id!r}"
                )
                continue
            if supplied_roles != declared_roles:
                violations.append(
                    f"distractors: absent-fact {fact_type_id!r} must supply exactly "
                    f"the declared roles {sorted(declared_roles)}; got "
                    f"{sorted(supplied_roles)}"
                )
                continue
            candidate_facts = dict(population.facts)
            candidate_facts[fact_type_id] = [dict(distractor.roles or {})]
            candidate = match_fact_type(
                fact_type_id,
                population.facts,
                candidate_facts,
                model=model,
                applicable=applicable,
            )
            if not candidate.applicable:
                violations.append(
                    f"distractors: absent-fact {fact_type_id!r} cannot be proved "
                    f"absent because the fact type is not applicable"
                )
            elif candidate.tp:
                violations.append(
                    f"distractors: the absent-fact distractor "
                    f"({fact_type_id} {distractor.roles!r}) matches an EXISTING "
                    f"source fact under the model's reference schemes — it is a "
                    f"fact, not a planted lie"
                )
            elif candidate.unresolved or candidate.ambiguous:
                violations.append(
                    f"distractors: absent-fact {fact_type_id!r} has role fillers "
                    f"that cannot be resolved unambiguously through the model's "
                    f"reference schemes"
                )

    # --- Obligation 4: renderer identity (WR-02) ---
    for field in ("renderer_skill", "renderer_skill_version", "executing_model"):
        if not str(getattr(manifest, field)).strip():
            violations.append(
                f"identity: {field} is empty — an anonymous rendering is not "
                f"attributable provenance"
            )

    for violation in violations:
        print(f"VIOLATION {violation}")
    print(
        f"doccheck: {len(violations)} violation(s) over "
        f"{len(applicable_ids)} applicable fact type(s), "
        f"{len(manifest.distractors)} distractor(s)"
    )
    return 3 if violations else 0

_cmd_doccheck.__module__ = "gnd.cli"
