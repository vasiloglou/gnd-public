"""Read-only element coverage over models and previously emitted evidence."""

from __future__ import annotations

import json
import stat
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import files
from pathlib import Path
from typing import Any, Literal

from jsonschema import Draft202012Validator
from jsonschema.exceptions import best_match

from gnd.address import (
    Addressing,
    ElementClass,
    constraint_address,
    derivation_address,
    fact_type_address,
    operation_address,
    parse_address,
    positional_constraint_ref,
)
from gnd.artifacts import canonical_report_text as canonical_payload  # noqa: F401 -- compatibility
from gnd.conformance.report import CONFORMANCE_SCHEMA_VERSION
from gnd.exp.spec import EXPERIMENT_DIR_PATTERN, SpecError, read_spec
from gnd.model import Model, structured_derivation_ids
from gnd.report import (
    BASE_PAYLOAD_SCHEMA_VERSION,
    DERIVATION_PAYLOAD_SCHEMA_VERSION,
    MODEL_BOUND_BASE_PAYLOAD_SCHEMA_VERSION,
    MODEL_BOUND_DERIVATION_PAYLOAD_SCHEMA_VERSION,
    PAYLOAD_SCHEMA_VERSION,
    payload_schema_version,
)
from gnd.transition import transition_model_identity

MAX_EVIDENCE_BYTES = 10 * 1024 * 1024

EvidenceKind = Literal["check", "verify", "conformance", "transition"]
CoverageStatus = Literal["corroborated", "claimed", "unclaimed"]

#: How a check/verify source names -- or fails to name -- the model behind it.
#: A legacy source is still evidence; it simply never claimed a model, and the
#: view says so rather than letting a reader assume one.
ReportBinding = Literal["legacy-unbound", "model-bound"]

#: The stable name a wrong-producer refusal carries, so a consumer can branch
#: on the rule rather than on a message substring.
MODEL_DIGEST_MISMATCH = "coverage:model-digest-mismatch"

#: The one reason a check/verify source can be unbound: it predates the wire
#: that carries model identity. Anything else is a refusal, not a gap.
LEGACY_BINDING_GAP_REASON = "legacy-report-without-model-digest"

#: Each frozen check/verify report version and its model-bound successor. A
#: census model admits exactly the pair for ITS derivation class -- a v4 source
#: for a non-structured model is refused exactly as a v3 one for a structured
#: model is, and so is each of their successors.
MODEL_BOUND_REPORT_VERSION: dict[int, int] = {
    BASE_PAYLOAD_SCHEMA_VERSION: MODEL_BOUND_BASE_PAYLOAD_SCHEMA_VERSION,
    DERIVATION_PAYLOAD_SCHEMA_VERSION: MODEL_BOUND_DERIVATION_PAYLOAD_SCHEMA_VERSION,
}


@dataclass(frozen=True)
class SourceBindingGap:
    """One accepted check/verify source that never named its model."""

    kind: Literal["check", "verify"]
    path: str
    schema_version: Literal[3, 4]
    reason: Literal["legacy-report-without-model-digest"] = LEGACY_BINDING_GAP_REASON

    def row(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "path": self.path,
            "schema_version": self.schema_version,
            "reason": self.reason,
        }

    def order(self) -> tuple[str, str]:
        return (self.kind, self.path)


@dataclass(frozen=True)
class Claim:
    """One covers row from one experiment."""

    experiment_id: str
    source_path: str
    address: str
    addressing: Addressing
    conclusions: Literal["conclusions-present", "no-conclusions"]


@dataclass(frozen=True)
class Evidence:
    """One previously emitted payload row naming a model element."""

    source: EvidenceKind
    path: str
    quote: dict[str, Any]


@dataclass(frozen=True)
class ElementRow:
    address: str
    element_class: ElementClass
    addressing: Addressing
    claims: tuple[Claim, ...]
    evidence: tuple[Evidence, ...]
    status: CoverageStatus


@dataclass(frozen=True)
class CoverageResult:
    model_path: str
    model_version: int
    model_digest: str
    source_paths: dict[str, tuple[str, ...]]
    refused_sources: tuple[dict[str, str], ...]
    elements: tuple[ElementRow, ...]
    unmatched_covers: tuple[dict[str, str], ...]
    unstable_addresses: tuple[dict[str, str], ...]
    covers_exemptions: tuple[dict[str, str], ...]
    unbound_sources: tuple[SourceBindingGap, ...] = ()


def _census(rows: Sequence[ElementRow], element_class: ElementClass) -> dict[str, int]:
    selected = [row for row in rows if row.element_class == element_class]
    return {
        "in_model": len(selected),
        "claimed": sum(bool(row.claims) for row in selected),
        "corroborated": sum(row.status == "corroborated" for row in selected),
        "unclaimed": sum(not row.claims for row in selected),
        "unclaimed_with_evidence": sum(not row.claims and bool(row.evidence) for row in selected),
    }


def _census_classes(result_or_payload_elements: Sequence[Any]) -> tuple[str, ...]:
    """The census sections, in fixed order; ``derivation`` appears exactly when
    the element universe carries a derivation row (v5.0 Phase 3, T3.6).

    A model declaring no structured derivation keeps the three-section census
    and ``schema_version`` 1 byte-identically; a model declaring one selects
    the widened ``schema_version`` 2 variant with the fourth section always
    present — the r2 R2 no-optional-key rule, one payload over.
    """

    has_derivation = any(
        getattr(row, "element_class", None) == "derivation" for row in result_or_payload_elements
    )
    base: tuple[str, ...] = ("operation", "fact_type", "constraint")
    return base + (("derivation",) if has_derivation else ())


def build_payload(result: CoverageResult, *, gnd_version: str) -> dict[str, Any]:
    """Serialize a result into the closed coverage output contract."""

    census_classes = _census_classes(result.elements)
    # /3, /4 (v5.1 Phase 3, D-P3.2): the same derivation-class discriminator
    # that separated 1 from 2, on the output that now discloses which of its
    # check/verify sources never named a model. Versions 1 and 2 stay frozen
    # and readable; they forbid `sources.unbound`, so a consumer cannot mistake
    # an old census's silence for "there were no gaps". Byte identity of newly
    # emitted output and visible disclosure cannot both hold, and the later
    # ruling wins (IF-P3-2, OQ-V51-P3-PLAN-COVERAGE-1).
    return {
        "schema_version": 4 if "derivation" in census_classes else 3,
        "tool": "gnd",
        "command": "coverage",
        "gnd_version": gnd_version,
        "model": {
            "path": result.model_path,
            "version": result.model_version,
            "digest": result.model_digest,
        },
        "sources": {
            **{key: list(value) for key, value in result.source_paths.items()},
            "refused": [dict(row) for row in result.refused_sources],
            # Always present, possibly empty: "we looked and every source named
            # its model" and "we did not look" are different facts, and a key
            # that appears only when non-empty makes them indistinguishable.
            "unbound": [gap.row() for gap in result.unbound_sources],
        },
        "census": {
            element_class: _census(result.elements, element_class)
            for element_class in census_classes
        },
        "elements": [
            {
                "address": row.address,
                "class": row.element_class,
                "addressing": row.addressing,
                "status": row.status,
                "claims": [
                    {
                        "experiment": claim.experiment_id,
                        "path": claim.source_path,
                        "conclusions": claim.conclusions,
                    }
                    for claim in row.claims
                ],
                "evidence": [
                    {
                        "source": item.source,
                        "path": item.path,
                        "quote": item.quote,
                    }
                    for item in row.evidence
                ],
            }
            for row in result.elements
        ],
        "unmatched_covers": [dict(row) for row in result.unmatched_covers],
        "unstable_addresses": [dict(row) for row in result.unstable_addresses],
        "covers_exemptions": [dict(row) for row in result.covers_exemptions],
    }




def render_coverage(payload: Mapping[str, Any]) -> str:
    """Render the human element roadmap without an aggregate or grade."""

    lines = [
        "GND COVERAGE",
        f"MODEL {payload['model']['path']}",
        f"DIGEST {payload['model']['digest']}",
        "",
    ]
    labels = {
        "operation": "OPERATIONS",
        "fact_type": "FACT TYPES",
        "constraint": "CONSTRAINTS",
        "derivation": "DERIVATIONS",
    }
    rendered_classes = tuple(
        element_class
        for element_class in ("operation", "fact_type", "constraint", "derivation")
        if element_class in payload["census"]
    )
    for element_class in rendered_classes:
        counts = payload["census"][element_class]
        lines.append(f"{labels[element_class]} CENSUS")
        for key in (
            "in_model",
            "claimed",
            "corroborated",
            "unclaimed",
            "unclaimed_with_evidence",
        ):
            lines.append(f"  {key}: {counts[key]}")
        lines.append("")

    for element_class in rendered_classes:
        lines.append(labels[element_class])
        selected = [
            element for element in payload["elements"] if element["class"] == element_class
        ]
        if not selected:
            lines.append("  (none)")
        for element in selected:
            lines.append(
                f"  {element['address']} [{element['addressing']}] {element['status']}"
            )
            if element["addressing"] == "positional":
                lines.append("    unstable")
            for claim in element["claims"]:
                lines.append(
                    f"    claim {claim['experiment']} {claim['path']} "
                    f"{claim['conclusions']}"
                )
            for item in element["evidence"]:
                quote = json.dumps(
                    item["quote"], ensure_ascii=False, sort_keys=True, allow_nan=False
                )
                lines.append(f"    evidence {item['source']} {item['path']} {quote}")
        lines.append("")

    loud_sections = (
        ("UNMATCHED COVERS", "unmatched_covers"),
        ("UNSTABLE ADDRESSES", "unstable_addresses"),
        ("COVERS EXEMPTIONS", "covers_exemptions"),
    )
    for title, key in loud_sections:
        lines.append(title)
        rows = payload[key]
        if not rows:
            lines.append("  (none)")
        for row in rows:
            lines.append(
                "  "
                + " | ".join(
                    f"{field}={value}" for field, value in row.items()
                )
            )
        lines.append("")

    lines.append("UNBOUND SOURCES")
    unbound = payload["sources"].get("unbound", [])
    if not unbound:
        lines.append("  (none)")
    for row in unbound:
        lines.append(
            f"  kind={row['kind']} | path={row['path']} | "
            f"schema_version={row['schema_version']} | reason={row['reason']}"
        )
    lines.append("")

    lines.append("REFUSED SOURCES")
    refused = payload["sources"]["refused"]
    if not refused:
        lines.append("  (none)")
    for row in refused:
        lines.append(f"  path={row['path']} | reason={row['reason']}")
    return "\n".join(lines) + "\n"


class CoverageInputError(Exception):
    """A named source could not be consumed as the declared evidence kind."""


class CoverageMissingError(Exception):
    """A path explicitly named by the caller does not exist."""


class CoveragePathError(Exception):
    """A source path crossed a symlink or had a refused file type."""


def _refuse_symlink_components(path: Path) -> None:
    absolute = path if path.is_absolute() else Path.cwd() / path
    current = Path(absolute.anchor)
    for component in absolute.parts[1:]:
        current /= component
        try:
            info = current.lstat()
        except FileNotFoundError:
            return
        except OSError as error:
            raise CoveragePathError(
                f"{path} could not be inspected at {current}: {error}"
            ) from error
        if stat.S_ISLNK(info.st_mode):
            raise CoveragePathError(f"{path} crosses symlink component {current}")


def guard_named_source(path: Path, *, directory: bool) -> None:
    """Apply existence before the path guard for one argv-named source."""

    try:
        info = path.stat()
    except FileNotFoundError as error:
        raise CoverageMissingError(f"named source {path} does not exist") from error
    except OSError as error:
        raise CoveragePathError(f"named source {path} could not be inspected: {error}") from error
    _refuse_symlink_components(path)
    right_kind = stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)
    if not right_kind:
        expected = "directory" if directory else "regular file"
        raise CoveragePathError(f"named source {path} is not a {expected}")


def _guard_experiment_child(root: Path, child: Path) -> None:
    try:
        resolved_root = root.resolve(strict=True)
        resolved_child = child.resolve(strict=True)
        resolved_child.relative_to(resolved_root)
    except (OSError, ValueError) as error:
        raise CoveragePathError(
            f"experiment child {child} escapes or cannot be resolved beneath {root}"
        ) from error
    _refuse_symlink_components(child)
    try:
        info = child.lstat()
    except OSError as error:
        raise CoverageInputError(f"experiment child {child} is unreadable: {error}") from error
    if not stat.S_ISDIR(info.st_mode):
        raise CoverageInputError(f"experiment child {child} is not a directory")


def _guard_experiment_file(path: Path) -> None:
    try:
        info = path.lstat()
    except FileNotFoundError as error:
        raise CoverageInputError(f"required experiment document {path} is missing") from error
    except OSError as error:
        raise CoverageInputError(f"experiment document {path} is unreadable: {error}") from error
    _refuse_symlink_components(path)
    if not stat.S_ISREG(info.st_mode):
        raise CoveragePathError(f"experiment document {path} is not a regular file")


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-JSON numeric constant {value!r}")


def _accepted_schema_versions(kind: EvidenceKind, payload_version: int) -> tuple[int, ...]:
    """Every report version this evidence kind may present, for THIS model.

    Check and verify accept the model-appropriate PAIR: the frozen version the
    model's derivation class selects and its model-bound successor. A
    transition payload keeps the single frozen version -- v5.1 Phase 3 moved
    check and verify and deliberately left `gnd check --steps` alone -- and
    conformance has its own contract entirely.
    """

    if kind == "conformance":
        return (CONFORMANCE_SCHEMA_VERSION,)
    if kind == "transition":
        return (payload_version,)
    successor = MODEL_BOUND_REPORT_VERSION.get(payload_version)
    historical = (payload_version,) if successor is None else (payload_version, successor)
    if kind == "check":
        return (*historical, 7, 9, 10)
    return historical


def read_json_document(
    path: Path,
    *,
    kind: EvidenceKind,
    payload_version: int = PAYLOAD_SCHEMA_VERSION,
) -> dict[str, Any]:
    """Read one evidence object, or raise :class:`CoverageInputError`.

    Total over arbitrary bytes. ``stat()`` runs before ``read_bytes()`` so the
    cap bounds the read itself. Refuses over-cap and unreadable files, non-UTF-8,
    malformed JSON (including long-integer ``ValueError`` and deep-nesting
    ``RecursionError``), NaN/Infinity, non-object roots, and schema versions
    unsupported for the evidence kind named by the caller.

    ``payload_version`` is the FROZEN check/verify report version the MODEL
    selects (D-P3.4): a v4 payload for a model that declares no structured
    derivation is refused exactly like a v3 payload for one that does, so
    stale evidence can never stand for a model that now demands derivation
    obligations. Since v5.1 Phase 3 a check or verify source may also present
    that version's model-bound successor; the derivation-class family is what
    is checked here, never the binding.
    """

    try:
        size = path.stat().st_size
    except OSError as error:
        raise CoverageInputError(f"{path} could not be inspected: {error}") from error
    if size > MAX_EVIDENCE_BYTES:
        raise CoverageInputError(
            f"{path} is {size} bytes, over the {MAX_EVIDENCE_BYTES}-byte evidence cap"
        )
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise CoverageInputError(f"{path} could not be read: {error}") from error
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise CoverageInputError(f"{path} is not UTF-8: {error}") from error
    try:
        document = json.loads(text, parse_constant=_reject_json_constant)
    except (json.JSONDecodeError, ValueError, RecursionError) as error:
        raise CoverageInputError(f"{path} is not valid JSON: {error}") from error
    if not isinstance(document, dict):
        raise CoverageInputError(f"{path} has a {type(document).__name__} root, not an object")
    accepted = _accepted_schema_versions(kind, payload_version)
    if document.get("schema_version") not in accepted:
        wanted = " or ".join(str(version) for version in accepted)
        raise CoverageInputError(
            f"{path} has schema_version {document.get('schema_version')!r}; "
            f"{kind} evidence requires {wanted}"
        )
    return document


@lru_cache(maxsize=2)
def _schema(kind: Literal["report", "conformance"]) -> dict[str, Any]:
    name = "report.schema.json" if kind == "report" else "conformance.schema.json"
    return json.loads(files("gnd").joinpath(name).read_text(encoding="utf-8"))


def _declared_arm_errors(
    error: Any, schema: Mapping[str, Any], document: Mapping[str, Any]
) -> list[Any]:
    """The sub-errors of the ``oneOf`` arm this document CLAIMS to belong to.

    The report contract is a closed union tagged by ``schema_version``, and the
    bare top-level failure of ``oneOf`` says only "not valid under any of the
    given schemas" -- true, useless, and identical for a missing model digest,
    a malformed one and a stray derivations array. Every other arm fails on the
    tag, which is not news. So the reader reports the arm whose tag the
    document actually carries; if it carries none, no arm is more relevant than
    another and the caller falls back to the whole error set.
    """

    arms = error.schema.get("oneOf", ())
    declared = document.get("schema_version")
    selected: list[Any] = []
    for sub in error.context or ():
        index = next((step for step in sub.relative_schema_path if isinstance(step, int)), None)
        if index is None or index >= len(arms):
            continue
        arm = arms[index]
        reference = arm.get("$ref", "")
        if reference.startswith("#/$defs/"):
            arm = schema.get("$defs", {}).get(reference.removeprefix("#/$defs/"), arm)
        tag = arm.get("properties", {}).get("schema_version", {})
        allowed = [tag["const"]] if "const" in tag else tag.get("enum", ())
        if declared in allowed:
            nested = (
                _declared_arm_errors(sub, schema, sub.instance)
                if sub.validator == "oneOf" and isinstance(sub.instance, Mapping)
                else []
            )
            selected.extend(nested or [sub])
    return selected


def _validate_shape(
    document: dict[str, Any], path: Path, *, schema_kind: Literal["report", "conformance"]
) -> None:
    """Refuse a document whose shape the contract forbids, saying WHERE."""

    schema = _schema(schema_kind)
    try:
        raised = list(Draft202012Validator(schema).iter_errors(document))
    except (RecursionError, ValueError, TypeError) as caught:
        raise CoverageInputError(f"{path} could not be schema-validated: {caught}") from caught
    focused: list[Any] = []
    for candidate in raised:
        arm = (
            _declared_arm_errors(candidate, schema, document)
            if candidate.validator == "oneOf"
            else []
        )
        focused.extend(arm or [candidate])
    error = best_match(focused)
    if error is not None:
        location = error.json_path or "$"
        raise CoverageInputError(
            f"{path} has invalid {schema_kind} shape at {location}: {error.message}"
        )


_TRANSITION_REPORT_FIELDS: tuple[tuple[str, type[Any]], ...] = (
    ("pre_snapshot", dict),
    ("pre_snapshot_verdicts", list),
    ("steps", list),
    ("frame_grading", list),
    ("frame_verdicts", list),
    ("post_snapshot", dict),
)


def _validate_transition_evaluation_state(
    transition: dict[str, Any], path: Path
) -> None:
    """Enforce the evaluated/null partition the report schema only describes."""

    if transition["evaluated"]:
        malformed = [
            field
            for field, expected_type in _TRANSITION_REPORT_FIELDS
            if not isinstance(transition[field], expected_type)
        ]
        if malformed:
            raise CoverageInputError(
                f"{path} transition evaluated true requires populated report fields; "
                f"invalid: {', '.join(malformed)}"
            )
        for index, verdict in enumerate(transition["frame_verdicts"]):
            if "fact_type" not in verdict:
                raise CoverageInputError(
                    f"{path} transition frame_verdicts[{index}] is missing fact_type"
                )
        return

    populated = [
        field
        for field, _expected_type in _TRANSITION_REPORT_FIELDS
        if transition[field] is not None
    ]
    if populated:
        raise CoverageInputError(
            f"{path} transition evaluated false requires null report fields; "
            f"populated: {', '.join(populated)}"
        )


def read_evidence_document(
    path: Path,
    *,
    kind: EvidenceKind,
    payload_version: int = PAYLOAD_SCHEMA_VERSION,
    census_model_digest: str | None = None,
) -> tuple[dict[str, Any], ReportBinding | None]:
    """Read and validate one document as exactly the evidence kind declared.

    Returns the validated document and, for a check or verify source, how it
    names its model. The version logic lives HERE and nowhere else: an indexer
    that re-derived "is this legacy" from a version number would be a second
    home for the pairing, and the two would drift.

    The order is observable and pinned (§6.8): a capped no-follow read, then
    the JSON object and its version family, then the report schema, then the
    command kind the caller's flag declared, and only then the digest
    comparison. A malformed digest therefore fails its schema pattern before
    any comparison can look at it, and a source offered under the wrong flag
    fails before any evidence is indexed.

    ``census_model_digest`` is the identity of the model the view is being
    built for. When it is supplied and the source is model-bound, the two must
    be the same model; the refusal carries the stable name
    ``coverage:model-digest-mismatch``. Legacy sources skip the comparison --
    they never made the claim -- and are reported as unbound instead.
    """

    document = read_json_document(path, kind=kind, payload_version=payload_version)
    schema_kind: Literal["report", "conformance"] = (
        "conformance" if kind == "conformance" else "report"
    )
    _validate_shape(document, path, schema_kind=schema_kind)

    command = document.get("command")
    transition = document.get("transition")
    if kind in ("check", "verify"):
        if command != kind or transition is not None:
            raise CoverageInputError(f"{path} is not {kind} snapshot evidence as its flag declared")
        return document, _report_binding(document, path, census_model_digest)
    if kind == "transition":
        if command != "check" or not isinstance(transition, dict):
            raise CoverageInputError(f"{path} is not transition evidence as its flag declared")
        _validate_transition_evaluation_state(transition, path)
    elif command != "conformance":
        raise CoverageInputError(f"{path} is not conformance evidence as its flag declared")
    return document, None


def _report_binding(
    document: dict[str, Any], path: Path, census_model_digest: str | None
) -> ReportBinding:
    """Classify one schema-valid check/verify source, comparing if it claims.

    The schema has already proved that a model-bound version carries a
    well-formed digest and that a frozen version carries none, so this is a
    string comparison over two values that are both known to exist.
    """

    carried = document.get("model_digest")
    if carried is None:
        return "legacy-unbound"
    if census_model_digest is not None and carried != census_model_digest:
        raise CoverageInputError(
            f"{path} was produced by a different model [{MODEL_DIGEST_MISMATCH}]: "
            f"the report names {carried}, this census model is {census_model_digest}"
        )
    return "model-bound"


def _element_universe(
    model: Model,
) -> tuple[list[tuple[str, ElementClass, Addressing]], dict[str, str]]:
    elements: list[tuple[str, ElementClass, Addressing]] = []
    positional_to_address: dict[str, str] = {}
    for operation in model.operations:
        elements.append((operation_address(str(operation["id"])), "operation", "declared-id"))
    structured = set(structured_derivation_ids(model))
    for fact_type in model.fact_types:
        fact_type_id = str(fact_type["id"])
        elements.append((fact_type_address(fact_type_id), "fact_type", "declared-id"))
        if fact_type_id in structured:
            # T3.6 / r2 R2: the derivation obligation is a SECOND element with
            # its own distinct address, placed immediately after its fact
            # type's row and counted exactly once.
            elements.append(
                (derivation_address(fact_type_id), "derivation", "declared-id")
            )
        for index, constraint in enumerate(fact_type.get("constraints") or []):
            positional = positional_constraint_ref(fact_type_id, index)
            declared_id = constraint.get("id")
            address = (
                constraint_address(str(declared_id)) if declared_id is not None else positional
            )
            positional_to_address[positional] = address
            elements.append(
                (address, "constraint", "declared-id" if declared_id is not None else "positional")
            )
    for index, constraint in enumerate(model.constraints):
        positional = positional_constraint_ref(None, index)
        declared_id = constraint.get("id")
        address = constraint_address(str(declared_id)) if declared_id is not None else positional
        positional_to_address[positional] = address
        elements.append(
            (address, "constraint", "declared-id" if declared_id is not None else "positional")
        )
    return elements, positional_to_address


def _claim_address(entry: Any) -> tuple[str, Addressing]:
    if entry.operation is not None:
        return operation_address(str(entry.operation)), "declared-id"
    if entry.fact_type is not None:
        return fact_type_address(str(entry.fact_type)), "declared-id"
    if entry.derivation is not None:
        return derivation_address(str(entry.derivation)), "declared-id"
    value = str(entry.constraint)
    parsed = parse_address(value)
    if parsed is not None and parsed.addressing == "positional":
        return value, "positional"
    return constraint_address(value), "declared-id"


def _quote_fields(row: dict[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
    return {field: row.get(field) for field in fields}


def _index_snapshot(
    path: Path,
    *,
    kind: Literal["check", "verify"],
    positional_to_address: dict[str, str],
    evidence: dict[str, list[Evidence]],
    payload_version: int,
    census_model_digest: str,
    unbound: list[SourceBindingGap],
) -> None:
    document, binding = read_evidence_document(
        path,
        kind=kind,
        payload_version=payload_version,
        census_model_digest=census_model_digest,
    )
    if binding == "legacy-unbound":
        # A gap per SOURCE, keyed by the full path the caller named. Two
        # byte-identical sources at two paths are two rows: whatever a
        # consumer is told about one of them it must be told about the other,
        # and a basename is not a source identity.
        unbound.append(
            SourceBindingGap(
                kind=kind,
                path=str(path),
                schema_version=document["schema_version"],
            )
        )
    for row in document.get("derivations", []):
        evidence[str(row["derivation_ref"])].append(
            Evidence(
                kind,
                str(path),
                _quote_fields(
                    row,
                    (
                        "derivation_ref",
                        "derivation",
                        "modality",
                        "verdict",
                        "reason_code",
                    ),
                ),
            )
        )
    for verdict in document["verdicts"]:
        reference = str(verdict["constraint_ref"])
        address = positional_to_address.get(reference, reference)
        evidence[address].append(
            Evidence(
                kind,
                str(path),
                _quote_fields(
                    verdict,
                    (
                        "constraint_ref",
                        "constraint_type",
                        "modality",
                        "source",
                        "status",
                        "verdict",
                        "reason_code",
                    ),
                ),
            )
        )
    for fact_type_id, quote in document["coverage"].items():
        evidence[fact_type_address(str(fact_type_id))].append(
            Evidence(kind, str(path), _quote_fields(quote, ("declared", "facts")))
        )


def _index_conformance(path: Path, evidence: dict[str, list[Evidence]]) -> None:
    document, _binding = read_evidence_document(path, kind="conformance")
    unchecked = document["limits"]["unchecked"]
    for satisfied in document["satisfied"]:
        quote = _quote_fields(satisfied, ("fact_type_id", "symbol", "relpath", "ownership"))
        quote["unchecked"] = unchecked
        evidence[fact_type_address(str(satisfied["fact_type_id"]))].append(
            Evidence("conformance", str(path), quote)
        )


def _index_transition(
    path: Path,
    evidence: dict[str, list[Evidence]],
    refused: list[dict[str, str]],
    *,
    payload_version: int = PAYLOAD_SCHEMA_VERSION,
) -> None:
    document, _binding = read_evidence_document(
        path, kind="transition", payload_version=payload_version
    )
    transition = document["transition"]
    if not transition["evaluated"]:
        refused.append({"path": str(path), "reason": "the walk was refused before evaluation"})
        return
    verdict_fields = (
        "family",
        "locator",
        "kind",
        "modality",
        "verdict",
        "message",
        "reason_code",
        "direction",
        "fact_type",
    )
    for step in transition["steps"]:
        quote = _quote_fields(step, ("index", "operation"))
        quote["verdicts"] = [_quote_fields(verdict, verdict_fields) for verdict in step["verdicts"]]
        evidence[operation_address(str(step["operation"]))].append(
            Evidence("transition", str(path), quote)
        )
    for grading in transition["frame_grading"]:
        evidence[fact_type_address(str(grading["fact_type"]))].append(
            Evidence(
                "transition",
                str(path),
                _quote_fields(grading, ("fact_type", "modality", "reason", "operations")),
            )
        )
    for verdict in transition["frame_verdicts"]:
        if verdict["fact_type"] is not None:
            evidence[fact_type_address(str(verdict["fact_type"]))].append(
                Evidence("transition", str(path), _quote_fields(verdict, verdict_fields))
            )


def _status(claims: Sequence[Claim], evidence: Sequence[Evidence]) -> CoverageStatus:
    if claims and evidence:
        return "corroborated"
    if claims:
        return "claimed"
    return "unclaimed"


def build_coverage(
    model: Model,
    *,
    model_path: str,
    experiments: Sequence[Path],
    check: Sequence[Path],
    verify: Sequence[Path],
    conformance: Sequence[Path],
    transition: Sequence[Path],
) -> CoverageResult:
    """Build one coverage view by indexing sources, then walking elements once."""

    universe, positional_to_address = _element_universe(model)
    universe_addresses = {address for address, _, _ in universe}
    # D-P3.4: the model, not a constant, decides which report version counts
    # as evidence for it — refused in both mismatch directions.
    expected_payload_version = payload_schema_version(model)
    census_model_digest = transition_model_identity(model)
    unbound: list[SourceBindingGap] = []
    claims: dict[str, list[Claim]] = defaultdict(list)
    evidence: dict[str, list[Evidence]] = defaultdict(list)
    unmatched: list[dict[str, str]] = []
    unstable: list[dict[str, str]] = []
    exemptions: list[dict[str, str]] = []
    refused: list[dict[str, str]] = []

    for directory in experiments:
        guard_named_source(directory, directory=True)
        try:
            children = sorted(directory.iterdir(), key=lambda child: child.name)
        except OSError as error:
            raise CoverageInputError(f"{directory} could not be listed: {error}") from error
        for child in children:
            if EXPERIMENT_DIR_PATTERN.fullmatch(child.name) is None:
                continue
            _guard_experiment_child(directory, child)
            spec_path = child / "SPEC.md"
            _guard_experiment_file(spec_path)
            try:
                spec = read_spec(spec_path)
            except SpecError as error:
                raise CoverageInputError(str(error)) from error
            if spec.id != child.name:
                raise CoverageInputError(
                    f"{spec_path} declares id {spec.id!r}, not directory {child.name!r}"
                )
            if spec.covers_exemption is not None:
                exemptions.append(
                    {
                        "experiment": spec.id,
                        "path": str(spec_path),
                        "exemption": spec.covers_exemption,
                    }
                )
                continue
            conclusions_path = child / "CONCLUSIONS.md"
            try:
                conclusions_path.lstat()
            except FileNotFoundError:
                conclusions: Literal["conclusions-present", "no-conclusions"] = "no-conclusions"
            except OSError as error:
                raise CoverageInputError(
                    f"experiment conclusion {conclusions_path} is unreadable: {error}"
                ) from error
            else:
                _guard_experiment_file(conclusions_path)
                conclusions = "conclusions-present"
            for entry in spec.covers:
                written_address, addressing = _claim_address(entry)
                matched_address = positional_to_address.get(written_address, written_address)
                if addressing == "positional":
                    unstable.append(
                        {
                            "experiment": spec.id,
                            "path": str(spec_path),
                            "address": written_address,
                            "note": "positional; reordering the model's constraints silently retargets this row",
                        }
                    )
                if matched_address not in universe_addresses:
                    unmatched.append(
                        {
                            "experiment": spec.id,
                            "path": str(spec_path),
                            "address": written_address,
                            "reason": "the model declares no element with this id",
                        }
                    )
                    continue
                claims[matched_address].append(
                    Claim(spec.id, str(spec_path), matched_address, addressing, conclusions)
                )

    snapshot_sources: tuple[tuple[Literal["check", "verify"], Sequence[Path]], ...] = (
        ("check", check),
        ("verify", verify),
    )
    for kind, sources in snapshot_sources:
        for path in sources:
            guard_named_source(path, directory=False)
            _index_snapshot(
                path,
                kind=kind,
                positional_to_address=positional_to_address,
                evidence=evidence,
                payload_version=expected_payload_version,
                census_model_digest=census_model_digest,
                unbound=unbound,
            )
    for path in conformance:
        guard_named_source(path, directory=False)
        _index_conformance(path, evidence)
    for path in transition:
        guard_named_source(path, directory=False)
        _index_transition(path, evidence, refused, payload_version=expected_payload_version)

    rows = tuple(
        ElementRow(
            address,
            element_class,
            addressing,
            tuple(claims[address]),
            tuple(evidence[address]),
            _status(claims[address], evidence[address]),
        )
        for address, element_class, addressing in universe
    )
    return CoverageResult(
        model_path=model_path,
        model_version=model.version,
        model_digest=census_model_digest,
        source_paths={
            "experiments": tuple(str(path) for path in experiments),
            "check": tuple(str(path) for path in check),
            "verify": tuple(str(path) for path in verify),
            "conformance": tuple(str(path) for path in conformance),
            "transition": tuple(str(path) for path in transition),
        },
        refused_sources=tuple(refused),
        elements=rows,
        unmatched_covers=tuple(unmatched),
        unstable_addresses=tuple(unstable),
        covers_exemptions=tuple(exemptions),
        unbound_sources=tuple(sorted(unbound, key=SourceBindingGap.order)),
    )


model_digest = transition_model_identity  # RF2 compatibility alias.
