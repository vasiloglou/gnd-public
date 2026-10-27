"""Validated, evidence-first model evolution with a raw-byte CAS commit point."""

from __future__ import annotations

import json
import stat
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

from pydantic import ValidationError
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from gnd import input_policy as _rf7_input
from gnd.artifacts import (
    ArtifactError,
    canonical_json_bytes,
    canonical_json_text,
    read_regular_file_bytes,
    sha256_hex,
    snapshot_tracked_roster,
    tree_sha256_from_directory,
)
from gnd.conformance.report import canonical as canonical_conformance
from gnd.conformance.service import run_conformance
from gnd.model import ModelLoadError, ModelValidationError
from gnd.model_verbalization import render_model_verbalization
from gnd.safefs import (
    InstallError,
    LeafIdentity,
    safe_destination,
)
from gnd.safefs import (
    atomic_write as _atomic_write,
)

from .models import (
    EVOLUTION_READ_ONLY_PENDING,
    EVOLUTION_SCHEMA_VERSION,
    AffectedCodeEvidence,
    BlastRadiusEntry,
    BlastRadiusReport,
    CASEvidence,
    CommittedText,
    ConstraintLocator,
    ElementLocator,
    EvolutionFinalizationState,
    EvolutionIntent,
    EvolutionOperation,
    EvolutionOperationKind,
    EvolutionPreview,
    EvolutionProposal,
    EvolutionRecord,
    LinkedProject,
    LinkedProjectConformance,
    ModelIdentityLocator,
    ProjectLocator,
    RoleLocator,
    ValidationEvidence,
    ValidationFinding,
    canonical_sha256,
    read_evolution_finalization_state_document,
    read_evolution_intent_document,
    read_evolution_preview_document,
    read_evolution_proposal_document,
    read_evolution_record_document,
    read_linked_project_conformance_document,
)

MAX_EVOLUTION_PROPOSAL_BYTES = 10 * 1024 * 1024
MAX_PROJECT_TREE_ENTRIES = 100_000
MAX_PROJECT_TREE_BYTES = 100 * 1024 * 1024
_AUDIT_KEYS = frozenset({"actor_id", "origin", "requested_at"})
_EXIT_PRECEDENCE = {0: 0, 13: 1, 3: 2, 66: 3, 74: 4}

__all__ = [
    "EvolutionError",
    "EvolutionService",
    "read_evolution_finalization_state",
    "read_evolution_intent",
    "read_evolution_preview",
    "read_evolution_proposal",
    "read_evolution_record",
    "read_linked_project_conformance",
]


class EvolutionError(Exception):
    """A proposal, stage, CAS, or immutable evidence write was refused."""


class EvolutionReadOnlyCompatibilityError(EvolutionError):
    """An old evidence document that may be READ but cannot be finished.

    Its own class rather than a message family, for the same reason the gated
    error below is: exit 11 is a distinct public band, and deriving it from a
    substring match on refusal text is how a band drifts into meaning something
    else. A version 1 or 2 pending finalization state is complete, valid,
    historical evidence -- it simply never recorded which project leaves the
    transaction covered, and no honest reading of it can supply them.
    """


class EvolutionOperationsGatedError(EvolutionError):
    """An ORM+ v2 operation delta this tool deliberately does not own.

    Its own class rather than a message family: exit 18 is a distinct public
    band ("the proposal is well formed and refused on policy"), and deriving it
    from a substring match on the refusal text is how an exit band drifts into
    meaning something else. Everything the caller needs to act — the gated
    element ids and the hand-edit protocol — is in the message."""


#: What a refused proposal is told to do instead. The full blast-radius walker
#: over operations is M3 work; until it exists the protocol is a human one, and
#: naming it in the refusal is what keeps the refusal actionable rather than
#: merely correct.
OPERATIONS_HAND_EDIT_PROTOCOL = (
    "hand-edit the model, confirm `gnd validate` exits 0, run a review panel "
    "over the diff, and append a record citing both"
)


def _relative_to_anchor(anchor: Path, path: Path, *, label: str) -> str:
    """Return one normalized lexical coordinate beneath an explicit anchor."""

    try:
        relative = path.absolute().relative_to(anchor.absolute())
    except ValueError as error:
        raise EvolutionError(f"{label} is outside its trusted anchor") from error
    if not relative.parts:
        raise EvolutionError(f"{label} must name a leaf beneath its trusted anchor")
    return relative.as_posix()


def _regular_bytes(
    anchor: Path,
    relative: str,
    *,
    label: str,
) -> bytes:
    """Translate the promoted read's refusals into this lane's error type.

    The read itself lives in ``gnd.artifacts``; only the exception type is local,
    because every caller here is inside an ``EvolutionError`` contract.  The
    message text is passed through unchanged.
    """

    try:
        return read_regular_file_bytes(
            anchor,
            relative,
            label=label,
            max_bytes=MAX_EVOLUTION_PROPOSAL_BYTES,
        )
    except ArtifactError as error:
        raise EvolutionError(str(error)) from error


def _missing_artifact(error: BaseException) -> bool:
    cause: BaseException | None = error
    while cause is not None:
        if isinstance(cause, FileNotFoundError):
            return True
        cause = cause.__cause__
    return False


def _leaf_identity(anchor: Path, relative: str, *, label: str) -> LeafIdentity:
    try:
        data = _regular_bytes(anchor, relative, label=label)
    except EvolutionError as error:
        if _missing_artifact(error):
            return LeafIdentity(kind="absent")
        raise
    return LeafIdentity(kind="file", sha256=sha256_hex(data))


def _load_model_bytes(
    data: bytes, *, label: str, model_path: Path, declared_references: Any = None
) -> Any:
    """Load model bytes, already admitted through a trusted descriptor, as if they
    sat at the workspace model's path ``model_path``.

    The bytes run the loader's guards and both validation layers. When the model
    declares reference populations, they are bound from the model's own
    directory through the no-follow ``bind_references``, exactly as ``gnd
    validate`` and ``gnd check`` bind them (IK4-Q2). Every load or binding
    refusal is a named EvolutionError, never an internal defect.

    ``declared_references``, when given, are the current model's declarations: a
    candidate that differs is refused before any of its files is read."""
    from gnd.model import bind_references, load_model_bytes
    from gnd.references import ReferenceInputError

    # The bytes are parsed as they were before IK4-Q2, when they sat in a
    # temporary model.orm.yaml: a .json name does not select the strict JSON
    # parser here (review R1; IK4-Q2-Q1 holds the question for the owner).
    source = model_path.with_suffix(".yaml") if model_path.suffix == ".json" else model_path
    try:
        model = load_model_bytes(data, source=source)
        if declared_references is not None and model.reference_populations != declared_references:
            raise EvolutionError(
                "declared operations do not equal the canonical candidate model: "
                "its reference populations differ from the current model's"
            )
        if model.reference_populations:
            try:
                model._references = bind_references(model, root=model_path.parent)
            except Exception as error:
                # load_model wraps every binding failure (a missing file, a link,
                # a digest mismatch) as ReferenceInputError; evolve does the same.
                raise ReferenceInputError(str(error), model=model) from error
        return model
    except YAMLError as error:
        raise _yaml_refusal(label, error) from None
    except (OSError, ModelLoadError, ModelValidationError, ReferenceInputError) as error:
        raise EvolutionError(f"{label} validation failed: {error}") from error


def _yaml_refusal(label: str, error: YAMLError) -> EvolutionError:
    """Malformed YAML is input, never an internal failure (IK4-Q2-Q2)."""
    mark = getattr(error, "problem_mark", None)
    where = f" at line {mark.line + 1}, column {mark.column + 1}" if mark else ""
    return EvolutionError(f"{label} is not valid YAML{where}")


def _parse_model_text(text: str) -> dict[str, Any]:
    try:
        _rf7_input.guard_yaml(text)
        parsed = YAML(typ="safe").load(text)
    except ValueError as error:
        raise EvolutionError(str(error)) from error
    except YAMLError as error:
        raise _yaml_refusal("candidate model", error) from None
    if not isinstance(parsed, dict):
        raise EvolutionError("candidate model is not a mapping")
    return dict(parsed)


def _constraints(document: dict[str, Any], *, hosted: bool = False) -> list[Any]:
    """Every constraint, fact-type lists first and then the top level.

    With ``hosted=True`` each is paired with its host: the fact-type id, or
    ``None`` for a top-level constraint (a non-string id by its ``repr``)."""
    result: list[Any] = []
    for fact_type in document.get("fact_types") or []:
        host = fact_type.get("id")
        key = host if isinstance(host, str) else repr(host)
        result.extend(
            (key, dict(item)) if hosted else dict(item)
            for item in fact_type.get("constraints") or []
        )
    result.extend(
        (None, dict(item)) if hosted else dict(item)
        for item in document.get("constraints") or []
    )
    return result


def _contains_audit_key(value: Any) -> bool:
    if isinstance(value, dict):
        return bool(_AUDIT_KEYS.intersection(value)) or any(
            _contains_audit_key(item) for item in value.values()
        )
    if isinstance(value, (list, tuple)):
        return any(_contains_audit_key(item) for item in value)
    return False


def _without_review(constraint: dict[str, Any]) -> dict[str, Any]:
    """A constraint as a reviewed status change may not alter it (IK2-D4).

    Confirmation may set ``status``, ``modality`` and ``provenance.reviewed_in``;
    everything else must equal the proposed predecessor."""
    stripped = {key: value for key, value in constraint.items() if key not in {"status", "modality"}}
    provenance = stripped.get("provenance")
    if isinstance(provenance, dict):
        stripped["provenance"] = {
            key: value for key, value in provenance.items() if key != "reviewed_in"
        }
    return stripped


def _enforce_d12(before: dict[str, Any], candidate: dict[str, Any]) -> None:
    before_hosted = [
        (host, canonical_json_text(item), item) for host, item in _constraints(before, hosted=True)
    ]
    before_counts = Counter(rendered for _, rendered, _ in before_hosted)
    candidates = [
        (host, canonical_json_text(item), item) for host, item in _constraints(candidate, hosted=True)
    ]
    # IK2: the proposed induced constraints a reviewed status change may claim
    # are those left over once every unchanged candidate copy has consumed its
    # exact match, so two candidates can never confirm one predecessor and an
    # unchanged copy can never be confirmed a second time. A claim is keyed by
    # the predecessor's host, so confirmation cannot also move the rule to
    # another fact type or the top level (review R3). Computed up front so the
    # single in-order pass below keeps every pre-IK2 refusal order.
    leftover = before_counts - Counter(rendered for _, rendered, _ in candidates)
    claimable: Counter[tuple[str | None, str]] = Counter()
    for host, rendered, item in before_hosted:
        if (
            leftover[rendered]
            and item.get("source") == "induced"
            and item.get("status") == "proposed"
        ):
            leftover[rendered] -= 1
            claimable[(host, canonical_json_text(_without_review(item)))] += 1

    for host, rendered, constraint in candidates:
        if _contains_audit_key(constraint.get("provenance", {})):
            raise EvolutionError(
                "operation audit actor/origin/time fields cannot enter constraint provenance"
            )
        if before_counts[rendered]:
            before_counts[rendered] -= 1
            continue

        source = constraint.get("source")
        status = constraint.get("status")
        modality = constraint.get("modality")
        provenance = constraint.get("provenance")
        if not isinstance(provenance, dict):
            provenance = {}
        if source != "induced" and "induction" in provenance:
            raise EvolutionError("provenance.induction is allowed only under source induced (D-12)")
        if source == "induced":
            if (status, modality) == ("proposed", "deontic"):
                if "reviewed_in" in provenance:
                    raise EvolutionError(
                        "new induced constraints cannot carry provenance.reviewed_in (D-12)"
                    )
                continue
            if status == "confirmed":
                reviewed_in = provenance.get("reviewed_in")
                predecessor = (host, canonical_json_text(_without_review(constraint)))
                if isinstance(reviewed_in, str) and reviewed_in.strip() and claimable[predecessor]:
                    claimable[predecessor] -= 1
                    continue
                raise EvolutionError(
                    "induced constraints become confirmed only as a reviewed status change "
                    "of an existing proposed induced constraint (D-12)"
                )
            raise EvolutionError("new induced constraints must be proposed/deontic (D-12)")
        if source == "llm-inferred":
            if (status, modality) != ("proposed", "deontic"):
                raise EvolutionError(
                    "new llm-inferred constraints must remain proposed/deontic (D-12)"
                )
        elif source == "user-supplied":
            if status != "confirmed":
                raise EvolutionError(
                    "owner-approved user-supplied constraints must be confirmed (D-12)"
                )
        else:
            raise EvolutionError(
                "new or changed constraints must be llm-inferred/proposed/deontic "
                "or user-supplied/confirmed (D-12)"
            )


def _json_ready(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def _surface_index(
    document: dict[str, Any],
    *,
    verbalization: str,
) -> dict[str, tuple[str, str]]:
    """Index every deterministic model surface by stable machine reference."""

    result: dict[str, tuple[str, str]] = {}

    def add(reference: str, surface: str, value: Any) -> None:
        if reference in result:
            raise EvolutionError(f"duplicate stable blast-radius reference {reference}")
        result[reference] = (surface, canonical_sha256(value))

    def add_constraints(host: str, constraints: list[dict[str, Any]]) -> None:
        occurrences: Counter[tuple[str, str]] = Counter()
        for constraint in constraints:
            family = str(constraint.get("type", "unknown"))
            digest = canonical_sha256(constraint)
            occurrence = occurrences[(family, digest)]
            occurrences[(family, digest)] += 1
            reference = f"{host}.constraints[{family}:{digest}:{occurrence}]"
            add(reference, "constraint", constraint)
            if "provenance" in constraint:
                add(f"{reference}.provenance", "provenance", constraint["provenance"])

    add("model", "model", document)
    add(
        "model.identity",
        "model",
        {"version": document.get("version"), "model_id": document.get("model_id")},
    )
    for object_type in document.get("object_types") or []:
        identifier = str(object_type["id"])
        reference = f"object_types[{identifier}]"
        add(reference, "object-type", object_type)
        if "reference" in object_type:
            add(
                f"{reference}.reference",
                "identifier-reference",
                object_type["reference"],
            )
        if "subtype_of" in object_type:
            add(
                f"{reference}.subtype_of",
                "identifier-reference",
                object_type["subtype_of"],
            )
        if "provenance" in object_type:
            add(f"{reference}.provenance", "provenance", object_type["provenance"])
        if "description" in object_type:
            add(f"{reference}.description", "annotation", object_type["description"])

    for fact_type in document.get("fact_types") or []:
        identifier = str(fact_type["id"])
        reference = f"fact_types[{identifier}]"
        add(reference, "fact-type", fact_type)
        raw_readings = fact_type.get("reading")
        readings = raw_readings if isinstance(raw_readings, list) else [raw_readings]
        reading_occurrences: Counter[str] = Counter()
        for reading in readings:
            if reading is None:
                continue
            digest = canonical_sha256(reading)
            occurrence = reading_occurrences[digest]
            reading_occurrences[digest] += 1
            add(
                f"{reference}.reading[{digest}:{occurrence}]",
                "reading",
                reading,
            )
        for role in fact_type.get("roles") or []:
            role_name = str(role["role_name"])
            add(f"{reference}.roles[{role_name}]", "role", role)
        add_constraints(reference, list(fact_type.get("constraints") or []))
        population_occurrences: Counter[str] = Counter()
        for population in fact_type.get("sample_population") or []:
            digest = canonical_sha256(population)
            occurrence = population_occurrences[digest]
            population_occurrences[digest] += 1
            add(
                f"{reference}.sample_population[{digest}:{occurrence}]",
                "population",
                population,
            )
        if "provenance" in fact_type:
            add(f"{reference}.provenance", "provenance", fact_type["provenance"])
        objectification = fact_type.get("objectification") or fact_type.get("objectified_as")
        if objectification is not None:
            add(
                f"{reference}.objectification",
                "identifier-reference",
                objectification,
            )

    for operation in document.get("operations") or []:
        identifier = str(operation["id"])
        reference = f"operations[{identifier}]"
        add(reference, "operation", operation)
        if "provenance" in operation:
            add(f"{reference}.provenance", "provenance", operation["provenance"])

    add_constraints("model", list(document.get("constraints") or []))
    add("model.verbalization", "verbalization", verbalization)
    return result


def _operations_reference_set(document: dict[str, Any]) -> frozenset[str]:
    """Every model element id the document's EXISTING operations depend on.

    Flat by design — parameter and ``create`` object types, plus the fact types
    named by precondition atoms, effects, and dynamic-rule subjects. It is NOT a
    transitive walk: a fact type's own roles' object types are reachable but are
    not added, because the gate this feeds is a refusal and a transitively
    widened refusal would swallow most of the model. The full blast-radius
    walker over operations is M3 work; this is the honest smaller claim.

    TOTAL over arbitrary JSON, not merely over schema-valid models. One caller
    passes the validated current model, but the other passes a proposal's
    ``after`` value, which is an arbitrary mapping that nothing schema-validates
    before it arrives here — an ``after`` of ``{"parameters": 1}`` must widen
    the set by nothing, never raise. Iterating a non-list is the specific shape
    that used to raise ``TypeError``, which the CLI then reported as an internal
    error (70) instead of a refusal."""

    def entries(value: Any) -> list[Any]:
        """A list's items; nothing at all for every other shape."""
        return value if isinstance(value, list) else []

    def named(value: Any, key: str) -> str | None:
        if isinstance(value, dict) and value.get(key) is not None:
            return str(value[key])
        return None

    references: set[str] = set()
    for operation in entries(document.get("operations")):
        if not isinstance(operation, dict):
            continue
        for parameter in entries(operation.get("parameters")):
            references.add(named(parameter, "object_type") or "")
        for obligation in entries(operation.get("preconditions")):
            if not isinstance(obligation, dict):
                continue
            for atom in entries(obligation.get("require")):
                references.add(named(atom, "fact_type") or "")
        for effect in entries(operation.get("effects")):
            if not isinstance(effect, dict):
                continue
            references.add(named(effect.get("create"), "object_type") or "")
            for verb in ("assert", "retract"):
                references.add(named(effect.get(verb), "fact_type") or "")
        for rule in entries(operation.get("dynamic_rules")):
            subject = rule.get("subject") if isinstance(rule, dict) else None
            references.add(named(subject, "fact_type") or "")
    references.discard("")
    return frozenset(references)


def _delta_element_ids(operation: EvolutionOperation) -> frozenset[str]:
    """The model element ids one proposal operation puts a delta on.

    A role or a fact-type-hosted constraint resolves to its HOST fact type: both
    live inside the ``fact_types[]`` entry, so a change to either is a change to
    that element as the reference set addresses it."""
    locator = operation.locator
    if isinstance(locator, ElementLocator):
        ids = {locator.element_id}
        if operation.kind is EvolutionOperationKind.RENAME and operation.after is not None:
            after_id = operation.after.get("id")
            if after_id is not None:
                ids.add(str(after_id))
        return frozenset(ids)
    if isinstance(locator, RoleLocator):
        return frozenset({locator.fact_type_id})
    if isinstance(locator, ModelIdentityLocator):
        return frozenset()
    if locator.host == "fact_type" and locator.host_id is not None:
        return frozenset({locator.host_id})
    return frozenset()


def _enforce_operations_gate(
    before_document: dict[str, Any],
    proposal: EvolutionProposal,
) -> None:
    """The ORM+ v2 evolve gate (A3).

    PROCEEDS on a purely additive operation delta — an ``add`` of a new
    operation whose reference set intersects nothing this same proposal renames
    or deletes. That is the shape of ordinary feature work after adoption, and
    refusing it would have left every post-adoption feature change with no tool
    owner at all.

    REFUSES with exit 18 on the narrower residue: modifying, renaming or
    deleting an operation, or putting any delta on an element that an EXISTING
    operation's reference set names. Those are the cases where the change's
    effect on the operations that depend on it is exactly what no shipped
    machinery computes yet, and publishing them on unchanged v1 machinery would
    be a silent claim that nothing downstream moved."""
    existing = _operations_reference_set(before_document)

    gated_operations = sorted(
        {
            operation.locator.element_id
            for operation in proposal.operations
            if isinstance(operation.locator, ElementLocator)
            and operation.locator.collection == "operations"
            and operation.kind is not EvolutionOperationKind.ADD
        }
    )
    if gated_operations:
        raise EvolutionOperationsGatedError(
            "evolution operations gated: this proposal modifies, renames or deletes "
            f"the operation(s) {gated_operations}. `gnd evolve` owns additive "
            "operation deltas only; for this one, "
            f"{OPERATIONS_HAND_EDIT_PROTOCOL}."
        )

    intersecting = sorted(
        {
            element_id
            for operation in proposal.operations
            # An ADD is gated too when it lands INSIDE an existing element —
            # a new role on, or a new constraint over, a fact type an operation
            # asserts changes what that operation must satisfy.
            if operation.kind is not EvolutionOperationKind.ADD
            or isinstance(operation.locator, (RoleLocator, ConstraintLocator))
            for element_id in _delta_element_ids(operation) & existing
        }
    )
    if intersecting:
        raise EvolutionOperationsGatedError(
            "evolution operations gated: this proposal puts a delta on "
            f"{intersecting}, which an existing operation's reference set names. "
            "Nothing shipped computes what that does to the operations depending "
            f"on it, so instead, {OPERATIONS_HAND_EDIT_PROTOCOL}."
        )

    removed = {
        element_id
        for operation in proposal.operations
        if operation.kind in {EvolutionOperationKind.RENAME, EvolutionOperationKind.DELETE}
        for element_id in _delta_element_ids(operation)
    }
    if not removed:
        return
    for operation in proposal.operations:
        locator = operation.locator
        if not (
            operation.kind is EvolutionOperationKind.ADD
            and isinstance(locator, ElementLocator)
            and locator.collection == "operations"
        ):
            continue
        added_references = _operations_reference_set({"operations": [operation.after or {}]})
        collision = sorted(added_references & removed)
        if collision:
            raise EvolutionOperationsGatedError(
                f"evolution operations gated: added operation "
                f"'{locator.element_id}' references {collision}, which this same "
                f"proposal renames or deletes. Split the two, or instead, "
                f"{OPERATIONS_HAND_EDIT_PROTOCOL}."
            )


def _operation_references(operation: EvolutionOperation) -> tuple[str, ...]:
    references = [operation.reference()]
    if operation.kind is EvolutionOperationKind.RENAME and operation.after is not None:
        if isinstance(operation.locator, ElementLocator):
            references.append(
                f"{operation.locator.collection}[{operation.after.get('id')}]"
            )
        elif isinstance(operation.locator, RoleLocator):
            references.append(
                f"fact_types[{operation.locator.fact_type_id}].roles["
                f"{operation.after.get('role_name')}]"
            )
    return tuple(references)


def _reference_matches(reference: str, root: str) -> bool:
    return reference == root or reference.startswith(f"{root}.")


def _matching_operation_ids(
    reference: str,
    operations: tuple[EvolutionOperation, ...],
) -> tuple[str, ...]:
    matched = {
        operation.operation_id
        for operation in operations
        if any(_reference_matches(reference, root) for root in _operation_references(operation))
    }
    if not matched:
        matched = {operation.operation_id for operation in operations}
    return tuple(sorted(matched))


def _build_blast_radius(
    proposal: EvolutionProposal,
    *,
    before_document: dict[str, Any],
    candidate_document: dict[str, Any],
    before_verbalization: str,
    candidate_verbalization: str,
) -> BlastRadiusReport:
    before_index = _surface_index(before_document, verbalization=before_verbalization)
    candidate_index = _surface_index(
        candidate_document,
        verbalization=candidate_verbalization,
    )
    entries: list[BlastRadiusEntry] = []
    for reference in sorted(set(before_index) | set(candidate_index)):
        before = before_index.get(reference)
        after = candidate_index.get(reference)
        if before == after:
            continue
        surface = before[0] if before is not None else after[0]  # type: ignore[index]
        before_sha256 = before[1] if before is not None else None
        after_sha256 = after[1] if after is not None else None
        if before is None:
            change = "added"
        elif after is None:
            change = "deleted"
        else:
            change = "modified"
        entries.append(
            BlastRadiusEntry(
                surface=surface,
                reference=reference,
                change=change,
                operation_ids=_matching_operation_ids(reference, proposal.operations),
                before_sha256=before_sha256,
                after_sha256=after_sha256,
            )
        )

    for artifact in proposal.artifacts:
        operation_ids = {
            operation.operation_id
            for operation in proposal.operations
            for supplied_reference in artifact.references
            if any(
                _reference_matches(supplied_reference, root)
                or _reference_matches(root, supplied_reference)
                for root in _operation_references(operation)
            )
        }
        if not operation_ids:
            continue
        surface = (
            artifact.artifact_kind
            if artifact.artifact_kind in {"population", "provenance"}
            else "supplied-artifact"
        )
        entries.append(
            BlastRadiusEntry(
                surface=surface,
                reference=artifact.reference(),
                change="affected",
                operation_ids=tuple(sorted(operation_ids)),
                before_sha256=artifact.sha256,
                after_sha256=artifact.sha256,
            )
        )

    entries.sort(key=lambda item: (item.reference, item.surface))
    body = {
        "schema_version": 1,
        "proposal_sha256": proposal.proposal_sha256,
        "before_model_sha256": proposal.expected_model_sha256,
        "candidate_model_sha256": proposal.candidate_model.sha256,
        "entries": [_json_ready(item) for item in entries],
    }
    return BlastRadiusReport(
        **body,
        report_sha256=canonical_sha256(body),
    )


def _find_element(document: dict[str, Any], locator: ElementLocator) -> tuple[list[Any], int]:
    collection = document.get(locator.collection)
    if not isinstance(collection, list):
        raise EvolutionError(f"stable locator collection {locator.collection} is absent")
    matches = [
        index for index, item in enumerate(collection) if item.get("id") == locator.element_id
    ]
    if len(matches) != 1:
        raise EvolutionError(
            f"stable locator {locator.reference()} resolved {len(matches)} elements, expected one"
        )
    return collection, matches[0]


def _find_fact(document: dict[str, Any], fact_type_id: str) -> dict[str, Any]:
    matches = [item for item in document.get("fact_types") or [] if item.get("id") == fact_type_id]
    if len(matches) != 1:
        raise EvolutionError(
            f"fact_types[{fact_type_id}] resolved {len(matches)} elements, expected one"
        )
    return matches[0]


def _find_role(document: dict[str, Any], locator: RoleLocator) -> tuple[list[Any], int]:
    roles = _find_fact(document, locator.fact_type_id).get("roles") or []
    matches = [
        index for index, item in enumerate(roles) if item.get("role_name") == locator.role_name
    ]
    if len(matches) != 1:
        raise EvolutionError(
            f"stable locator {locator.reference()} resolved {len(matches)} roles, expected one"
        )
    return roles, matches[0]


def _find_constraint(document: dict[str, Any], locator: ConstraintLocator) -> tuple[list[Any], int]:
    if locator.host == "model":
        constraints = document.get("constraints") or []
    else:
        constraints = _find_fact(document, str(locator.host_id)).get("constraints") or []
    matches = [
        index
        for index, item in enumerate(constraints)
        if item.get("type") == locator.family
        and canonical_sha256(item) == locator.canonical_before_sha256
    ]
    occurrence = locator.duplicate_occurrence
    if occurrence >= len(matches):
        raise EvolutionError(
            f"stable locator {locator.reference()} resolved no duplicate occurrence {occurrence}"
        )
    return constraints, matches[occurrence]


def _operation_target(
    document: dict[str, Any], operation: EvolutionOperation
) -> tuple[list[Any], int | None]:
    locator = operation.locator
    if isinstance(locator, ElementLocator):
        collection = document.get(locator.collection)
        # The FIRST operation added to a v1 document has no collection to join.
        # Created only for `operations`, and only on an add: every other absent
        # collection is a malformed locator, and silently materialising one
        # would turn a typo into a new top-level section.
        if (
            collection is None
            and locator.collection == "operations"
            and operation.kind is EvolutionOperationKind.ADD
        ):
            collection = document.setdefault("operations", [])
        if not isinstance(collection, list):
            raise EvolutionError(f"stable locator collection {locator.collection} is absent")
        if operation.kind is EvolutionOperationKind.ADD:
            if any(item.get("id") == locator.element_id for item in collection):
                raise EvolutionError(f"add target {locator.reference()} already exists")
            return collection, None
        return _find_element(document, locator)
    if isinstance(locator, RoleLocator):
        roles = _find_fact(document, locator.fact_type_id).get("roles") or []
        if operation.kind is EvolutionOperationKind.ADD:
            if any(item.get("role_name") == locator.role_name for item in roles):
                raise EvolutionError(f"add target {locator.reference()} already exists")
            return roles, None
        return _find_role(document, locator)
    if operation.kind is EvolutionOperationKind.ADD:
        if locator.host == "model":
            constraints = document.setdefault("constraints", [])
        else:
            fact_type = _find_fact(document, str(locator.host_id))
            constraints = fact_type.setdefault("constraints", [])
        dumped = operation.model_dump(mode="json")
        if any(item == dumped["after"] for item in constraints):
            raise EvolutionError(f"add target {locator.reference()} already exists")
        return constraints, None
    return _find_constraint(document, locator)


def _apply_declared_operations(
    before: dict[str, Any], operations: tuple[EvolutionOperation, ...]
) -> dict[str, Any]:
    document = deepcopy(before)
    for operation in operations:
        if isinstance(operation.locator, ModelIdentityLocator):
            dumped = operation.model_dump(mode="json")
            declared_before = dumped["before"]
            declared_after = dumped["after"]
            actual_before = {
                "version": document.get("version"),
                "model_id": document.get("model_id"),
            }
            if actual_before != declared_before:
                raise EvolutionError(
                    f"declared before value does not match {operation.reference()}"
                )
            assert declared_after is not None
            document.update(deepcopy(declared_after))
            continue
        collection, index = _operation_target(document, operation)
        dumped = operation.model_dump(mode="json")
        declared_before = dumped["before"]
        declared_after = dumped["after"]
        if operation.kind is EvolutionOperationKind.ADD:
            collection.append(deepcopy(declared_after))
            continue
        assert index is not None
        actual_before = collection[index]
        if actual_before != declared_before:
            raise EvolutionError(f"declared before value does not match {operation.reference()}")
        if operation.kind is EvolutionOperationKind.DELETE:
            del collection[index]
        else:
            collection[index] = deepcopy(declared_after)
    return document


def _tree_sha256(root: Path, *, relative: str | None = None) -> str:
    """Translate the promoted directory-walk identity into this lane's errors.

    Distinct from ``tree_sha256_from_inventory``: this one walks a real root and
    binds file, directory, and symlink-target bytes into the digest.  The two
    carried the same private name in different modules before 04-18.
    """

    try:
        return tree_sha256_from_directory(
            root,
            label="linked project",
            max_entries=MAX_PROJECT_TREE_ENTRIES,
            max_bytes=MAX_PROJECT_TREE_BYTES,
            relative=relative,
        )
    except ArtifactError as error:
        raise EvolutionError(str(error)) from error


def _declared_identity(project: Any) -> str:
    """The digest a linked project or conformance leaf claims for its tree."""

    if project.tracked_roster is not None:
        return project.expected_tracked_tree_sha256
    return project.expected_tree_sha256


def _observed_identity(leaf: Any) -> tuple[str, str, str]:
    """The expected/before/after triple a conformance leaf actually recorded."""

    if leaf.tracked_roster is not None:
        return (
            leaf.expected_tracked_tree_sha256,
            leaf.before_tracked_tree_sha256,
            leaf.after_tracked_tree_sha256,
        )
    return (leaf.expected_tree_sha256, leaf.before_tree_sha256, leaf.after_tree_sha256)


def _observation_fields(project: Any, before: str, after: str) -> dict[str, Any]:
    """The conformance-leaf fields for whichever identity this project uses."""

    if project.tracked_roster is not None:
        return {
            "tracked_roster": project.tracked_roster,
            "expected_tracked_tree_sha256": project.expected_tracked_tree_sha256,
            "before_tracked_tree_sha256": before,
            "after_tracked_tree_sha256": after,
        }
    return {
        "expected_tree_sha256": project.expected_tree_sha256,
        "before_tree_sha256": before,
        "after_tree_sha256": after,
    }


def _identity_fields(project: Any, observed: str) -> dict[str, Any]:
    """The linked-project fields to copy forward into intent and pending."""

    if project.tracked_roster is not None:
        return {
            "tracked_roster": project.tracked_roster,
            "expected_tracked_tree_sha256": observed,
        }
    return {"expected_tree_sha256": observed}


def _aggregate_exit_code(codes: list[int]) -> int:
    return max(codes or [0], key=lambda code: _EXIT_PRECEDENCE[code])


def _read_evolution_claim(
    path: str | Path,
    *,
    label: str,
    reader: Any,
    anchor: str | Path | None = None,
    relative: str | None = None,
) -> Any:
    claim_path = Path(path)
    trusted_anchor = claim_path.parent if anchor is None else Path(anchor)
    trusted_relative = (
        claim_path.name
        if relative is None
        else relative
    )
    raw = _regular_bytes(trusted_anchor, trusted_relative, label=label)
    if len(raw) > MAX_EVOLUTION_PROPOSAL_BYTES:
        raise EvolutionError(
            f"{label} exceeds the {MAX_EVOLUTION_PROPOSAL_BYTES}-byte cap"
        )
    try:
        value = _rf7_input.loads(raw)
        return reader(value)
    except (UnicodeDecodeError, json.JSONDecodeError, ValidationError, ValueError) as error:
        raise EvolutionError(f"invalid {label} at {claim_path}: {error}") from error


def read_evolution_proposal(
    path: str | Path,
    *,
    anchor: str | Path | None = None,
    relative: str | None = None,
) -> EvolutionProposal:
    """Read one bounded, closed JSON evolution proposal."""

    return _read_evolution_claim(
        path,
        label="evolution proposal",
        reader=read_evolution_proposal_document,
        anchor=anchor,
        relative=relative,
    )


def read_evolution_preview(
    path: str | Path,
    *,
    anchor: str | Path | None = None,
    relative: str | None = None,
) -> EvolutionPreview:
    """Read one bounded, version-selected preview claim."""

    return _read_evolution_claim(
        path,
        label="evolution preview",
        reader=read_evolution_preview_document,
        anchor=anchor,
        relative=relative,
    )


def read_evolution_intent(
    path: str | Path,
    *,
    anchor: str | Path | None = None,
    relative: str | None = None,
) -> EvolutionIntent:
    """Read one bounded, version-selected staged intent."""

    return _read_evolution_claim(
        path,
        label="evolution intent",
        reader=read_evolution_intent_document,
        anchor=anchor,
        relative=relative,
    )


def read_evolution_finalization_state(
    path: str | Path,
    *,
    anchor: str | Path | None = None,
    relative: str | None = None,
) -> EvolutionFinalizationState:
    """Read one bounded pending-finalization claim."""

    return _read_evolution_claim(
        path,
        label="evolution finalization state",
        reader=read_evolution_finalization_state_document,
        anchor=anchor,
        relative=relative,
    )


def read_evolution_record(
    path: str | Path,
    *,
    anchor: str | Path | None = None,
    relative: str | None = None,
) -> EvolutionRecord:
    """Read one bounded, version-selected immutable record."""

    return _read_evolution_claim(
        path,
        label="evolution record",
        reader=read_evolution_record_document,
        anchor=anchor,
        relative=relative,
    )


def read_linked_project_conformance(
    path: str | Path,
    *,
    envelope_version: int,
    anchor: str | Path | None = None,
    relative: str | None = None,
) -> LinkedProjectConformance:
    """Read one bounded standalone conformance leaf for an explicit envelope."""

    return _read_evolution_claim(
        path,
        label="linked project conformance",
        reader=lambda document: read_linked_project_conformance_document(
            document,
            envelope_version=envelope_version,
        ),
        anchor=anchor,
        relative=relative,
    )


class EvolutionService:
    """Preview, apply, and finalize one explicit model evolution proposal."""

    def __init__(
        self,
        *,
        model_path: str | Path,
        evidence_root: str | Path,
        verbalization_path: str | Path | None = None,
        allowed_project_root: str | Path | None = None,
    ) -> None:
        model = Path(model_path)
        if not model.is_absolute():
            model = Path.cwd() / model
        if model.is_symlink():
            raise EvolutionError(f"model path {model} is a symlink")
        self.model_path = model

        evidence = Path(evidence_root)
        if not evidence.is_absolute():
            evidence = Path.cwd() / evidence
        self.evidence_root = evidence

        if verbalization_path is None:
            verbalization = model.with_name("model.verbalization.txt")
        else:
            verbalization = Path(verbalization_path)
            if not verbalization.is_absolute():
                verbalization = Path.cwd() / verbalization
        self.verbalization_path = verbalization

        allowed = Path(allowed_project_root) if allowed_project_root is not None else model.parent
        if not allowed.is_absolute():
            allowed = Path.cwd() / allowed
        self.allowed_project_root = allowed.resolve()
        self._model_relative = _relative_to_anchor(
            self.allowed_project_root,
            self.model_path,
            label="model path",
        )
        self._verbalization_relative = _relative_to_anchor(
            self.allowed_project_root,
            self.verbalization_path,
            label="verbalization path",
        )

    def _proposal_relpath(self, proposal_id: str, leaf: str) -> str:
        return f"{proposal_id}/{leaf}"

    def _write_once(self, relpath: str, data: bytes) -> Path:
        destination = safe_destination(self.evidence_root, relpath)
        try:
            existing = _regular_bytes(
                self.evidence_root,
                relpath,
                label="immutable evidence",
            )
        except EvolutionError as error:
            if _missing_artifact(error):
                existing = None
            else:
                raise
        if existing is not None:
            if existing == data:
                return destination
            raise EvolutionError(f"immutable evidence conflict at {destination}")
        try:
            _atomic_write(
                self.evidence_root,
                relpath,
                data,
                expected=LeafIdentity(kind="absent"),
            )
        except InstallError as error:
            try:
                current = _regular_bytes(
                    self.evidence_root,
                    relpath,
                    label="immutable evidence",
                )
            except EvolutionError:
                current = None
            if current == data:
                return destination
            raise EvolutionError(
                f"immutable evidence write refused at {destination}: {error}"
            ) from error
        return destination

    @property
    def _model_path(self) -> Path:
        """The workspace model's path; evolve binds references from its directory."""
        return self.allowed_project_root / self._model_relative

    def _validated_candidate(
        self, candidate: CommittedText, *, declared_references: Any
    ) -> tuple[Any, ValidationEvidence]:
        if candidate.media_type not in {"application/yaml", "application/x-yaml"}:
            raise EvolutionError("candidate model media type must be application/yaml")
        model = _load_model_bytes(
            candidate.text.encode(candidate.encoding),
            label="candidate model",
            model_path=self._model_path,
            declared_references=declared_references,
        )
        warnings = tuple(
            ValidationFinding(
                path=item.path,
                message=item.message,
                rule_id=item.rule_id,
                severity=item.severity,
            )
            for item in model.warnings
        )
        return model, ValidationEvidence(
            valid=True,
            warnings=warnings,
            model_sha256=candidate.sha256,
        )

    def preview(
        self,
        proposal: EvolutionProposal,
        *,
        accepted_blast_radius_sha256: str | None = None,
    ) -> EvolutionPreview:
        """Validate and bind a proposal without changing any publication leaf."""

        try:
            proposal = read_evolution_proposal_document(proposal.model_dump(mode="json"))
        except (AttributeError, ValidationError, ValueError) as error:
            raise EvolutionError(f"invalid proposal identity: {error}") from error
        if proposal.schema_version != EVOLUTION_SCHEMA_VERSION:
            raise EvolutionError(
                "new evolution previews require the current schema version; "
                "versions 1 and 2 are read-only compatibility evidence"
            )

        # Checked before the model is read: an incomplete evolution is a
        # precondition failure of starting a new one, and reporting it must not
        # be masked by the stale-CAS refusal it will usually also cause.
        self.refuse_inherited_pending_finalization(proposal.proposal_id)

        before_bytes = _regular_bytes(
            self.allowed_project_root,
            self._model_relative,
            label="model",
        )
        before_sha256 = sha256_hex(before_bytes)
        if before_sha256 != proposal.expected_model_sha256:
            raise EvolutionError(
                "stale expected model identity before preview: "
                f"expected {proposal.expected_model_sha256}, observed {before_sha256}"
            )
        try:
            before_text = before_bytes.decode("utf-8")
        except UnicodeDecodeError as error:
            raise EvolutionError(f"model is not UTF-8: {error}") from error

        # The CURRENT model is validated first, and nothing reads its parsed
        # form before this line. `load_model` is what runs the alias/event guard
        # (T-01-02) and the two validation layers, so parsing the live bytes
        # ahead of it would both construct alias-bearing input the guard exists
        # to refuse and hand the gate below a document whose shapes nothing has
        # checked -- where `parameters: 1` raises TypeError instead of returning
        # a refusal.
        before_loaded_model = _load_model_bytes(
            before_bytes,
            label="current model",
            model_path=self._model_path,
        )
        before_document = _parse_model_text(before_text)

        # Before the CANDIDATE is validated, deliberately. The gate reads only
        # the current model and the proposal's declared locators, so its answer
        # never depends on the candidate -- and running it later would make its
        # commonest case unreachable. Renaming a fact type an operation
        # references cannot produce a VALID candidate without also editing that
        # operation, which is itself gated; checking the candidate's form first
        # would therefore answer "your candidate is invalid, go fix the
        # operations", sending the author straight into the other half of the
        # same gate.
        _enforce_operations_gate(before_document, proposal)

        candidate_model, validation = self._validated_candidate(
            proposal.candidate_model,
            declared_references=before_loaded_model.reference_populations,
        )
        candidate_document = _parse_model_text(proposal.candidate_model.text)
        declared_document = _apply_declared_operations(before_document, proposal.operations)
        if declared_document != candidate_document:
            raise EvolutionError("declared operations do not equal the canonical candidate model")
        _enforce_d12(before_document, candidate_document)

        verbalization_text = render_model_verbalization(candidate_model)
        before_verbalization_text = render_model_verbalization(before_loaded_model)
        before_blob = CommittedText.from_text(before_text, media_type="application/yaml")
        verbalization = CommittedText.from_text(
            verbalization_text,
            media_type="text/plain",
        )
        affected = tuple(sorted({operation.reference() for operation in proposal.operations}))
        blast_radius = _build_blast_radius(
            proposal,
            before_document=before_document,
            candidate_document=candidate_document,
            before_verbalization=before_verbalization_text,
            candidate_verbalization=verbalization_text,
        )
        breaking = any(
            operation.kind in {EvolutionOperationKind.RENAME, EvolutionOperationKind.DELETE}
            for operation in proposal.operations
        )
        if accepted_blast_radius_sha256 is not None and (
            not breaking or accepted_blast_radius_sha256 != blast_radius.report_sha256
        ):
            raise EvolutionError(
                "accepted blast radius does not match this proposal, current model, "
                "candidate model, and ordered report"
            )
        values: dict[str, Any] = {
            "proposal": proposal,
            "proposal_sha256": proposal.proposal_sha256,
            "before_model": before_blob,
            "candidate_model": proposal.candidate_model,
            "verbalization": verbalization,
            "validation": validation,
            "affected_references": affected,
            "breaking": breaking,
            "blast_radius": blast_radius,
            "accepted_blast_radius_sha256": accepted_blast_radius_sha256,
        }
        digest_body = {key: _json_ready(value) for key, value in values.items()}
        digest_body["schema_version"] = proposal.schema_version
        return EvolutionPreview(
            schema_version=proposal.schema_version,
            **values,
            preview_sha256=canonical_sha256(digest_body),
        )

    def _linked_snapshot(
        self,
        project: LinkedProject,
        *,
        expect_declared: bool = True,
    ) -> tuple[Path, str, ProjectLocator | None]:
        """Re-check the coordinate is safe and observe the identity behind it.

        ``expect_declared`` separates OBSERVING an identity from JUDGING it.
        Every caller wants the same path safety -- escape checks before and
        after resolution, a real directory, the roster-or-whole-tree dispatch --
        but not every caller is asking the same question. Before apply, a tree
        that no longer matches what the proposal declared is drift and must be
        refused here. After conformance has run, the declared identity is no
        longer the right comparand: the caller is asking whether the tree moved
        WHILE conformance ran, and answering that with a pre-apply refusal both
        names the wrong fault and makes the real one unreachable.
        """

        if project.locator is not None:
            supplied = Path(project.locator.path)
        else:
            assert project.root is not None
            supplied = project.root
        candidate = supplied if supplied.is_absolute() else self.allowed_project_root / supplied
        try:
            relative_path = candidate.relative_to(self.allowed_project_root)
        except ValueError as error:
            raise EvolutionError(
                f"linked project root {candidate} escapes allowed root "
                f"{self.allowed_project_root}"
            ) from error
        relative = None if relative_path == Path(".") else relative_path.as_posix()
        # A version 3 project is identified by the leaves the CALLER listed; a
        # version 1 or 2 project by its whole tree. One place decides which,
        # so preview, apply and finalize cannot observe it three ways.
        if project.tracked_roster is not None:
            try:
                _entries, tree = snapshot_tracked_roster(
                    self.allowed_project_root,
                    project.tracked_roster.paths,
                    label="linked project",
                    relative=relative,
                    max_total_bytes=MAX_PROJECT_TREE_BYTES,
                )
            except ArtifactError as error:
                raise EvolutionError(str(error)) from error
        else:
            tree = _tree_sha256(self.allowed_project_root, relative=relative)
        try:
            root = candidate.resolve(strict=True)
            root_info = root.stat()
        except (OSError, RuntimeError) as error:
            raise EvolutionError(
                f"linked project root {candidate} could not be resolved: {error}"
            ) from error
        try:
            root.relative_to(self.allowed_project_root)
        except ValueError as error:
            raise EvolutionError(
                f"linked project root {candidate} escapes allowed root after resolution "
                f"{self.allowed_project_root}"
            ) from error
        if not stat.S_ISDIR(root_info.st_mode):
            raise EvolutionError(f"linked project root {candidate} is not a directory")
        declared = _declared_identity(project)
        if expect_declared and tree != declared:
            raise EvolutionError(
                f"linked project {project.project_id} changed before apply: "
                f"expected {declared}, observed {tree}"
            )
        committed_locator = project.locator
        return root, tree, committed_locator

    def _read_staged_model(
        self,
        proposal_id: str,
        leaf: str,
        reader: Any,
        *,
        label: str,
    ) -> Any:
        relpath = self._proposal_relpath(proposal_id, leaf)
        try:
            value = _rf7_input.loads(
                _regular_bytes(
                    self.evidence_root,
                    relpath,
                    label=label,
                ).decode("utf-8")
            )
            return reader(value)
        except (UnicodeDecodeError, json.JSONDecodeError, ValidationError, ValueError) as error:
            raise EvolutionError(f"{label} is invalid: {error}") from error

    def _staged_proposal_ids(self) -> list[str]:
        try:
            entries = sorted(self.evidence_root.iterdir(), key=lambda item: item.name)
        except FileNotFoundError:
            return []
        except OSError as error:
            raise EvolutionError(
                f"evidence root could not be inspected at {self.evidence_root}: {error}"
            ) from error
        return [
            entry.name
            for entry in entries
            if not entry.is_symlink() and entry.is_dir() and not entry.name.startswith(".")
        ]

    def pending_finalization(
        self,
        proposal_id: str | None = None,
    ) -> EvolutionFinalizationState | None:
        """Report one staged pending finalization that has no completed record.

        MODEL-02 requires that every model change trigger a downstream
        conformance recheck. The recheck lives in :meth:`finalize`, and the
        pending state is written immediately before the model CAS, so an
        interrupted process can leave a *published* model whose recheck never
        ran. This inspection is what makes that state visible instead of silent.

        It is strictly read-only and it never completes, repairs, or rolls back
        what it finds: D-11's report-do-not-repair posture governs a pending
        state exactly as it governs drift.
        """

        for candidate in (
            [proposal_id] if proposal_id is not None else self._staged_proposal_ids()
        ):
            pending_path = safe_destination(
                self.evidence_root,
                self._proposal_relpath(candidate, "pending.json"),
            )
            try:
                pending_info = pending_path.lstat()
            except FileNotFoundError:
                continue
            except OSError as error:
                raise EvolutionError(
                    f"pending finalization state could not be inspected at "
                    f"{pending_path}: {error}"
                ) from error
            if not stat.S_ISREG(pending_info.st_mode):
                continue
            record = self.record_path(candidate)
            try:
                record.lstat()
            except FileNotFoundError:
                pass
            except OSError as error:
                raise EvolutionError(
                    f"final record could not be inspected at {record}: {error}"
                ) from error
            else:
                continue
            return self._read_staged_model(
                candidate,
                "pending.json",
                read_evolution_finalization_state_document,
                label="pending finalization state",
            )
        return None

    def refuse_inherited_pending_finalization(self, proposal_id: str | None = None) -> None:
        """Refuse to start a *new* evolution over an incomplete published one.

        Completing the pending state you found is not inheriting one, so the
        proposal that owns the pending state is exempt — otherwise the refusal
        would strand the very transaction it exists to surface.
        """

        pending = self.pending_finalization()
        if pending is None or pending.proposal_id == proposal_id:
            return
        pending_path = safe_destination(
            self.evidence_root,
            self._proposal_relpath(pending.proposal_id, "pending.json"),
        )
        raise EvolutionError(
            f"incomplete evolution {pending.proposal_id} has no final record, so its "
            "downstream conformance recheck may never have run; complete it with "
            f"`gnd evolve finalize <model> {pending_path}` before starting a new evolution"
        )

    def apply(self, preview: EvolutionPreview) -> EvolutionFinalizationState:
        """Stage immutable evidence and publish only the candidate model CAS."""

        try:
            preview = read_evolution_preview_document(preview.model_dump(mode="json"))
        except (AttributeError, ValidationError, ValueError) as error:
            raise EvolutionError(f"preview identity or proposal identity is invalid: {error}") from error
        if preview.schema_version != EVOLUTION_SCHEMA_VERSION:
            raise EvolutionError(
                "new evolution applies require the current schema version; "
                "versions 1 and 2 are read-only compatibility evidence"
            )
        if preview.breaking and preview.accepted_blast_radius_sha256 is None:
            raise EvolutionError(
                "breaking evolution requires explicit acceptance of this exact blast radius"
            )

        proposal = preview.proposal
        proposal_id = proposal.proposal_id
        # Re-run the gate here rather than trusting the preview that carried it:
        # `apply` accepts a preview document, and a hand-built one would
        # otherwise publish exactly the delta the gate exists to refuse.
        _enforce_operations_gate(
            _parse_model_text(preview.before_model.text),
            proposal,
        )
        live_bytes = _regular_bytes(
            self.allowed_project_root,
            self._model_relative,
            label="model",
        )
        live_sha256 = sha256_hex(live_bytes)
        if live_sha256 == preview.candidate_model.sha256:
            staged_preview = self._read_staged_model(
                proposal_id,
                "preview.json",
                read_evolution_preview_document,
                label="staged preview",
            )
            pending = self._read_staged_model(
                proposal_id,
                "pending.json",
                read_evolution_finalization_state_document,
                label="pending finalization state",
            )
            if staged_preview != preview or (
                pending.proposal_id != proposal_id
                or pending.proposal_sha256 != preview.proposal_sha256
                or pending.preview_sha256 != preview.preview_sha256
                or pending.old_model_sha256 != preview.before_model.sha256
                or pending.new_model_sha256 != preview.candidate_model.sha256
                or pending.verbalization_sha256 != preview.verbalization.sha256
            ):
                raise EvolutionError(
                    "stale model CAS: intended bytes exist under a different staged identity"
                )
            return pending
        if live_sha256 != preview.before_model.sha256:
            raise EvolutionError(
                "stale model CAS: model changed after preview; "
                f"expected {preview.before_model.sha256}, observed {live_sha256}"
            )
        if live_bytes != preview.before_model.text.encode("utf-8"):
            raise EvolutionError("live model bytes differ from the preview's committed bytes")

        before_document = _parse_model_text(preview.before_model.text)
        candidate_document = _parse_model_text(preview.candidate_model.text)
        declared_document = _apply_declared_operations(before_document, proposal.operations)
        if declared_document != candidate_document:
            raise EvolutionError(
                "declared operations do not equal the canonical candidate model at apply"
            )
        _enforce_d12(before_document, candidate_document)
        before_loaded_model = _load_model_bytes(
            live_bytes,
            label="current model at apply",
            model_path=self._model_path,
        )
        candidate_loaded_model, validation = self._validated_candidate(
            preview.candidate_model,
            declared_references=before_loaded_model.reference_populations,
        )
        candidate_verbalization = render_model_verbalization(candidate_loaded_model)
        recomputed_blast_radius = _build_blast_radius(
            proposal,
            before_document=before_document,
            candidate_document=candidate_document,
            before_verbalization=render_model_verbalization(before_loaded_model),
            candidate_verbalization=candidate_verbalization,
        )
        if validation != preview.validation:
            raise EvolutionError("candidate validation evidence changed before apply")
        if candidate_verbalization != preview.verbalization.text:
            raise EvolutionError("candidate verbalization changed before apply")
        if recomputed_blast_radius != preview.blast_radius:
            raise EvolutionError("blast radius changed before apply")

        snapshots = [self._linked_snapshot(project) for project in proposal.linked_projects]
        verbalization_identity = _leaf_identity(
            self.allowed_project_root,
            self._verbalization_relative,
            label="publication verbalization",
        )
        self._write_once(
            self._proposal_relpath(proposal_id, "proposal.json"),
            canonical_json_bytes(proposal),
        )
        self._write_once(
            self._proposal_relpath(proposal_id, "before.orm.yaml"),
            preview.before_model.text.encode("utf-8"),
        )
        self._write_once(
            self._proposal_relpath(proposal_id, "candidate.orm.yaml"),
            preview.candidate_model.text.encode("utf-8"),
        )
        self._write_once(
            self._proposal_relpath(proposal_id, "candidate.verbalization.txt"),
            preview.verbalization.text.encode("utf-8"),
        )
        self._write_once(
            self._proposal_relpath(proposal_id, "preview.json"),
            canonical_json_bytes(preview),
        )

        intent_projects: list[LinkedProject] = []
        for project, (root, tree, locator) in zip(
            proposal.linked_projects,
            snapshots,
            strict=True,
        ):
            if project.locator is not None:
                assert locator is not None
                coordinate: dict[str, Any] = {"locator": locator}
            else:
                coordinate = {"root": root}
            intent_projects.append(
                LinkedProject(
                    project_id=project.project_id,
                    **coordinate,
                    **_identity_fields(project, tree),
                )
            )
        intent = EvolutionIntent(
            schema_version=preview.schema_version,
            proposal_sha256=preview.proposal_sha256,
            preview_sha256=preview.preview_sha256,
            expected_model_sha256=preview.before_model.sha256,
            candidate_model_sha256=preview.candidate_model.sha256,
            verbalization_sha256=preview.verbalization.sha256,
            verbalization_before_kind=verbalization_identity.kind,
            verbalization_before_sha256=verbalization_identity.sha256,
            blast_radius_sha256=preview.blast_radius.report_sha256,
            accepted_blast_radius_sha256=preview.accepted_blast_radius_sha256,
            linked_projects=tuple(intent_projects),
        )
        intent_bytes = canonical_json_bytes(intent)
        intent_sha256 = sha256_hex(intent_bytes)
        self._write_once(self._proposal_relpath(proposal_id, "intent.json"), intent_bytes)
        # Version 3 records the projects INSIDE the state's own identity; an
        # older state never did and cannot recover them (IF-P3-6).
        state_body: dict[str, Any] = {
            "schema_version": preview.schema_version,
            "state": "pending-finalization",
            "proposal_id": proposal_id,
            "proposal_sha256": preview.proposal_sha256,
            "preview_sha256": preview.preview_sha256,
            "intent_sha256": intent_sha256,
            "old_model_sha256": preview.before_model.sha256,
            "new_model_sha256": preview.candidate_model.sha256,
            "verbalization_sha256": preview.verbalization.sha256,
            "verbalization_before_kind": verbalization_identity.kind,
            "verbalization_before_sha256": verbalization_identity.sha256,
        }
        if preview.schema_version == EVOLUTION_SCHEMA_VERSION:
            state_body["linked_projects"] = [
                project.model_dump(mode="json") for project in intent_projects
            ]
        pending = EvolutionFinalizationState(
            **state_body,
            state_identity_sha256=canonical_sha256(state_body),
        )
        self._write_once(
            self._proposal_relpath(proposal_id, "pending.json"),
            canonical_json_bytes(pending),
        )

        candidate_relative = self._proposal_relpath(proposal_id, "candidate.orm.yaml")
        staged_candidate_bytes = _regular_bytes(
            self.evidence_root,
            candidate_relative,
            label="staged candidate",
        )
        staged = _load_model_bytes(
            staged_candidate_bytes,
            label="staged candidate model",
            model_path=self._model_path,
        )
        if sha256_hex(staged_candidate_bytes) != preview.candidate_model.sha256:
            raise EvolutionError("staged candidate digest changed before publication")
        if render_model_verbalization(staged) != preview.verbalization.text:
            raise EvolutionError("staged candidate verbalization changed before publication")

        safe_destination(self.allowed_project_root, self._model_relative)
        try:
            _atomic_write(
                self.allowed_project_root,
                self._model_relative,
                preview.candidate_model.text.encode("utf-8"),
                expected=LeafIdentity(kind="file", sha256=preview.before_model.sha256),
            )
        except InstallError as error:
            raise EvolutionError(f"stale model CAS refused publication: {error}") from error
        return pending

    def record_path(self, proposal_id: str) -> Path:
        return safe_destination(
            self.evidence_root,
            self._proposal_relpath(proposal_id, "record.json"),
        )

    def final_record_file_sha256(self, record: EvolutionRecord) -> str:
        return sha256_hex(canonical_json_bytes(record))

    def finalize(self, state: EvolutionFinalizationState) -> EvolutionRecord:
        """Complete exact post-CAS leaves and publish the immutable D-13 record last."""

        # BEFORE anything is read from disk and before any recorded digest is
        # interpreted. A version 1 or 2 pending state does not record which
        # project leaves the transaction was about, and there is no honest way
        # to recover that: inferring it would mean discovering repository state,
        # and reinterpreting an old whole-tree digest under roster semantics
        # would silently change what the evidence claimed. So the state stays
        # readable and is refused by name (D-P3.5, IF-P3-6).
        if state.schema_version != EVOLUTION_SCHEMA_VERSION:
            raise EvolutionReadOnlyCompatibilityError(
                f"[{EVOLUTION_READ_ONLY_PENDING}] a version {state.schema_version} "
                "pending finalization state is read-only compatibility evidence: it "
                "does not declare the project roster this finalization would need"
            )
        try:
            state = read_evolution_finalization_state_document(state.model_dump(mode="json"))
        except (AttributeError, ValidationError, ValueError) as error:
            raise EvolutionError(f"pending finalization identity is invalid: {error}") from error
        proposal_id = state.proposal_id
        staged_state = self._read_staged_model(
            proposal_id,
            "pending.json",
            read_evolution_finalization_state_document,
            label="pending finalization state",
        )
        if staged_state != state:
            raise EvolutionError("pending finalization identity differs from immutable evidence")
        preview = self._read_staged_model(
            proposal_id,
            "preview.json",
            read_evolution_preview_document,
            label="staged preview",
        )
        proposal = self._read_staged_model(
            proposal_id,
            "proposal.json",
            read_evolution_proposal_document,
            label="staged proposal",
        )
        if proposal != preview.proposal or state.proposal_sha256 != preview.proposal_sha256:
            raise EvolutionError("pending proposal identity does not match staged preview")
        if not (
            state.schema_version
            == preview.schema_version
            == proposal.schema_version
        ):
            raise EvolutionError("pending evolution envelope versions do not match")
        if state.preview_sha256 != preview.preview_sha256:
            raise EvolutionError("pending preview identity does not match staged preview")
        if (
            state.old_model_sha256 != preview.before_model.sha256
            or state.new_model_sha256 != preview.candidate_model.sha256
            or state.verbalization_sha256 != preview.verbalization.sha256
        ):
            raise EvolutionError("pending publication identities do not match staged preview")

        intent_relative = self._proposal_relpath(proposal_id, "intent.json")
        intent_bytes = _regular_bytes(
            self.evidence_root,
            intent_relative,
            label="staged intent",
        )
        if sha256_hex(intent_bytes) != state.intent_sha256:
            raise EvolutionError("pending intent identity does not match staged intent")
        try:
            intent = read_evolution_intent_document(
                _rf7_input.loads(intent_bytes.decode("utf-8"))
            )
        except (UnicodeDecodeError, json.JSONDecodeError, ValidationError, ValueError) as error:
            raise EvolutionError(f"staged intent is unreadable: {error}") from error
        expected_intent = {
            "proposal_sha256": state.proposal_sha256,
            "preview_sha256": state.preview_sha256,
            "expected_model_sha256": state.old_model_sha256,
            "candidate_model_sha256": state.new_model_sha256,
            "verbalization_sha256": state.verbalization_sha256,
            "verbalization_before_kind": state.verbalization_before_kind,
            "verbalization_before_sha256": state.verbalization_before_sha256,
            "blast_radius_sha256": preview.blast_radius.report_sha256,
            "accepted_blast_radius_sha256": preview.accepted_blast_radius_sha256,
        }
        if any(getattr(intent, key) != value for key, value in expected_intent.items()):
            raise EvolutionError("staged intent fields do not match pending identities")
        if intent.schema_version != state.schema_version:
            raise EvolutionError("staged intent version does not match pending identity")
        # BEFORE any project leaf is opened. A pending state's identity digest is
        # a pure function of its own body, with no secret in it, so a rewritten
        # pending.json is perfectly self-consistent and the comparison against
        # the staged copy cannot catch it. At version 3 that body carries the
        # roster, and the published record enshrines the state by digest, so an
        # unchecked roster would let finalization publish evidence whose own
        # pending leaf describes a different transaction. The intent is already
        # bound to the preview and the proposal, so agreement with it is what
        # makes the declared roster this transaction's roster (§6.3, §6.5).
        if state.linked_projects != intent.linked_projects:
            raise EvolutionError("pending linked projects do not match staged intent")
        # Whole projects, not just coordinates: the intent copies the roster and
        # identity forward unchanged, so less would leave both smuggleable.
        if intent.linked_projects != proposal.linked_projects:
            raise EvolutionError("staged intent linked projects do not match the proposal")

        record_relative = self._proposal_relpath(proposal_id, "record.json")
        try:
            record_bytes = _regular_bytes(
                self.evidence_root,
                record_relative,
                label="final record",
            )
        except EvolutionError as error:
            if _missing_artifact(error):
                record_bytes = None
            else:
                raise
        completed: EvolutionRecord | None = None
        if record_bytes is not None:
            try:
                completed = read_evolution_record_document(
                    _rf7_input.loads(record_bytes.decode("utf-8"))
                )
            except (UnicodeDecodeError, json.JSONDecodeError, ValidationError, ValueError) as error:
                raise EvolutionError(f"final record is invalid: {error}") from error

        before_relative = self._proposal_relpath(proposal_id, "before.orm.yaml")
        candidate_relative = self._proposal_relpath(proposal_id, "candidate.orm.yaml")
        before_bytes = _regular_bytes(
            self.evidence_root,
            before_relative,
            label="staged before model",
        )
        candidate_bytes = _regular_bytes(
            self.evidence_root,
            candidate_relative,
            label="staged candidate",
        )
        if sha256_hex(before_bytes) != state.old_model_sha256:
            raise EvolutionError("staged before-model identity differs from pending state")
        if sha256_hex(candidate_bytes) != state.new_model_sha256:
            raise EvolutionError("staged candidate identity differs from pending state")
        live_bytes = _regular_bytes(
            self.allowed_project_root,
            self._model_relative,
            label="published model",
        )
        if sha256_hex(live_bytes) != state.new_model_sha256 or live_bytes != candidate_bytes:
            raise EvolutionError(
                "stale finalization: published model has divergent bytes; refusing overwrite or rollback"
            )

        before_loaded = _load_model_bytes(
            before_bytes,
            label="staged before model at finalize",
            model_path=self._model_path,
        )
        candidate_loaded = _load_model_bytes(
            candidate_bytes,
            label="staged candidate model at finalize",
            model_path=self._model_path,
        )
        try:
            before_text = before_bytes.decode("utf-8")
            candidate_text = candidate_bytes.decode("utf-8")
        except UnicodeDecodeError as error:
            raise EvolutionError(f"staged model is not UTF-8: {error}") from error
        before_document = _parse_model_text(before_text)
        candidate_document = _parse_model_text(candidate_text)
        if _apply_declared_operations(before_document, proposal.operations) != candidate_document:
            raise EvolutionError("declared operations changed before finalization")
        _enforce_d12(before_document, candidate_document)
        candidate_verbalization = render_model_verbalization(candidate_loaded)
        recomputed_blast_radius = _build_blast_radius(
            proposal,
            before_document=before_document,
            candidate_document=candidate_document,
            before_verbalization=render_model_verbalization(before_loaded),
            candidate_verbalization=candidate_verbalization,
        )
        if recomputed_blast_radius != preview.blast_radius:
            raise EvolutionError("blast radius changed before finalization")
        if candidate_verbalization != preview.verbalization.text:
            raise EvolutionError("candidate verbalization changed before finalization")

        desired_verbalization = preview.verbalization.text.encode("utf-8")
        current_verbalization = _leaf_identity(
            self.allowed_project_root,
            self._verbalization_relative,
            label="publication verbalization",
        )
        if not (
            current_verbalization.kind == "file"
            and current_verbalization.sha256 == state.verbalization_sha256
        ):
            if completed is not None:
                raise EvolutionError(
                    "completed record has divergent verbalization publication lineage"
                )
            if (
                current_verbalization.kind != state.verbalization_before_kind
                or current_verbalization.sha256 != state.verbalization_before_sha256
            ):
                raise EvolutionError(
                    "stale finalization: verbalization has divergent bytes; refusing overwrite"
                )
            safe_destination(
                self.allowed_project_root,
                self._verbalization_relative,
            )
            try:
                _atomic_write(
                    self.allowed_project_root,
                    self._verbalization_relative,
                    desired_verbalization,
                    expected=LeafIdentity(
                        kind=state.verbalization_before_kind,
                        sha256=state.verbalization_before_sha256,
                    ),
                )
            except InstallError as error:
                raise EvolutionError(
                    f"model CAS committed, but verbalization finalization was refused: {error}"
                ) from error

        intent_projects = intent.linked_projects
        if len(intent_projects) != len(
            proposal.linked_projects
        ):
            raise EvolutionError("staged intent linked-project inventory is incomplete")
        conformance: list[LinkedProjectConformance] = []
        for project, intent_project in zip(
            proposal.linked_projects,
            intent_projects,
            strict=True,
        ):
            root, before_tree, locator = self._linked_snapshot(project)
            if project.locator is not None:
                coordinate_matches = intent_project.locator == locator
            else:
                coordinate_matches = intent_project.root == root
            if (
                intent_project.project_id != project.project_id
                or not coordinate_matches
                or _declared_identity(intent_project) != before_tree
            ):
                raise EvolutionError(
                    f"staged intent identity changed for linked project {project.project_id}"
                )
            relpath = self._proposal_relpath(
                proposal_id,
                f"conformance/{project.project_id}.json",
            )
            try:
                evidence = self._read_staged_model(
                    proposal_id,
                    f"conformance/{project.project_id}.json",
                    lambda document: read_linked_project_conformance_document(
                        document,
                        envelope_version=state.schema_version,
                    ),
                    label=f"linked conformance evidence for {project.project_id}",
                )
            except EvolutionError as error:
                if _missing_artifact(error):
                    evidence = None
                else:
                    raise
            if evidence is not None:
                if project.locator is not None:
                    evidence_coordinate_matches = evidence.locator == locator
                else:
                    evidence_coordinate_matches = evidence.root == root
                if (
                    not evidence_coordinate_matches
                    or _observed_identity(evidence)
                    != (_declared_identity(project), before_tree, before_tree)
                ):
                    raise EvolutionError(
                        f"linked conformance identity changed for {project.project_id}"
                    )
            else:
                if completed is not None:
                    raise EvolutionError(
                        f"completed record is missing standalone conformance lineage for "
                        f"{project.project_id}"
                    )
                result = run_conformance(self.model_path, root)
                _root, after_tree, _locator = self._linked_snapshot(
                    project, expect_declared=False
                )
                if after_tree != before_tree:
                    raise EvolutionError(
                        f"linked project {project.project_id} changed during conformance; "
                        "automatic repair is forbidden"
                    )
                payload_text = canonical_conformance(result.payload)
                coordinate: dict[str, Any]
                if project.locator is not None:
                    assert locator is not None
                    coordinate = {"locator": locator}
                else:
                    coordinate = {"root": root}
                evidence = LinkedProjectConformance(
                    project_id=project.project_id,
                    **coordinate,
                    **_observation_fields(project, before_tree, after_tree),
                    payload=result.payload,
                    payload_sha256=sha256_hex(payload_text.encode("utf-8")),
                    exit_code=result.exit_code,
                )
                self._write_once(relpath, canonical_json_bytes(evidence))
            conformance.append(evidence)

        aggregate = _aggregate_exit_code([item.exit_code for item in conformance])
        cas = CASEvidence(
            expected_model_sha256=state.old_model_sha256,
            observed_model_sha256=state.new_model_sha256,
            published=True,
        )
        affected_code = AffectedCodeEvidence(
            ordered_references=preview.affected_references,
            generated_code_written=False,
            extension_code_written=False,
            blast_radius=tuple(item.reference for item in preview.blast_radius.entries),
        )
        values = {
            "proposal_id": proposal_id,
            "proposal_sha256": state.proposal_sha256,
            "preview_sha256": state.preview_sha256,
            "intent_sha256": state.intent_sha256,
            "old_model_sha256": state.old_model_sha256,
            "new_model_sha256": state.new_model_sha256,
            "blast_radius_sha256": preview.blast_radius.report_sha256,
            "accepted_blast_radius_sha256": preview.accepted_blast_radius_sha256,
            "finalization_state_sha256": state.state_identity_sha256,
            "operations": proposal.operations,
            "rationale": proposal.rationale,
            "audit": proposal.audit,
            "validation": preview.validation,
            "cas": cas,
            "linked_conformance": tuple(conformance),
            "affected_code": affected_code,
            "conformance_exit_code": aggregate,
            "published_with_drift": aggregate == 13,
        }
        digest_body = {key: _json_ready(value) for key, value in values.items()}
        digest_body.update(
            {
                "schema_version": state.schema_version,
                "model_commit_point": "model-cas",
                "transaction_scope": "single-leaf CAS; no multi-file atomicity",
            }
        )
        record = EvolutionRecord(
            schema_version=state.schema_version,
            **values,
            record_identity_sha256=canonical_sha256(digest_body),
        )
        if completed is not None:
            if completed != record:
                raise EvolutionError(
                    "completed record differs from reconstructed staged lineage"
                )
            return completed
        self._write_once(
            self._proposal_relpath(proposal_id, "record.json"),
            canonical_json_bytes(record),
        )
        return record
