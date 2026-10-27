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

from gnd.model._documents import ModelValueError as ModelValueError
from gnd.model._documents import json_document as json_document
from gnd.model._induction import _induction_strings as _induction_strings
from gnd.model._induction import (
    _rule_induced_confirmed_reviewed as _rule_induced_confirmed_reviewed,
)
from gnd.model._induction import _rule_induced_provenance as _rule_induced_provenance
from gnd.model._operations import _attach_compiled_obligations as _attach_compiled_obligations
from gnd.model._operations import _effect_index as _effect_index
from gnd.model._operations import _has_literal as _has_literal
from gnd.model._operations import _roles_by_variable as _roles_by_variable
from gnd.model._operations import _variables_in as _variables_in
from gnd.model._operations import compile_operation as compile_operation
from gnd.model._validation import _DERIVATION_ARM_KEYS as _DERIVATION_ARM_KEYS
from gnd.model._validation import _DERIVATION_RULE_KEYS as _DERIVATION_RULE_KEYS
from gnd.model._validation import _DERIVATION_TERM_CACHE as _DERIVATION_TERM_CACHE
from gnd.model._validation import _NUMERIC_PRIMITIVES as _NUMERIC_PRIMITIVES
from gnd.model._validation import _PLACEHOLDER as _PLACEHOLDER
from gnd.model._validation import _REPORTED_PARAMETER_LIMIT as _REPORTED_PARAMETER_LIMIT
from gnd.model._validation import _ROLE_SEQ_FIELDS as _ROLE_SEQ_FIELDS
from gnd.model._validation import _SEMANTIC_RULES as _SEMANTIC_RULES
from gnd.model._validation import DEFAULT_LIMITS as DEFAULT_LIMITS
from gnd.model._validation import FLOAT_FUNCTION_ARITY as FLOAT_FUNCTION_ARITY
from gnd.model._validation import IMPORTED_PROVENANCE_FIELDS as IMPORTED_PROVENANCE_FIELDS
from gnd.model._validation import MAX_MODEL_BYTES as MAX_MODEL_BYTES
from gnd.model._validation import MAX_YAML_EVENTS as MAX_YAML_EVENTS
from gnd.model._validation import NEVER_MECHANICAL_FAMILIES as NEVER_MECHANICAL_FAMILIES
from gnd.model._validation import NUMERIC_PRIMITIVES as NUMERIC_PRIMITIVES
from gnd.model._validation import UTC as UTC
from gnd.model._validation import YAML as YAML
from gnd.model._validation import AggregateAnalysis as AggregateAnalysis
from gnd.model._validation import Any as Any
from gnd.model._validation import DeonticNote as DeonticNote
from gnd.model._validation import DerivationClassification as DerivationClassification
from gnd.model._validation import DerivationEdge as DerivationEdge
from gnd.model._validation import DerivationStability as DerivationStability
from gnd.model._validation import Draft202012Validator as Draft202012Validator
from gnd.model._validation import Mapping as Mapping
from gnd.model._validation import Model as Model
from gnd.model._validation import ModelLoadError as ModelLoadError
from gnd.model._validation import ModelValidationError as ModelValidationError
from gnd.model._validation import Path as Path
from gnd.model._validation import ValidationIssue as ValidationIssue
from gnd.model._validation import _aggregate_issues as _aggregate_issues
from gnd.model._validation import _aggregate_variables as _aggregate_variables
from gnd.model._validation import _ancestor_closure as _ancestor_closure
from gnd.model._validation import _atom_reference_issues as _atom_reference_issues
from gnd.model._validation import _constraint_role_seqs as _constraint_role_seqs
from gnd.model._validation import _derivation_atoms as _derivation_atoms
from gnd.model._validation import _derivation_bind as _derivation_bind
from gnd.model._validation import _derivation_components as _derivation_components
from gnd.model._validation import _derivation_cycles as _derivation_cycles
from gnd.model._validation import _derivation_dependency_closures as _derivation_dependency_closures
from gnd.model._validation import _derivation_head_term_issues as _derivation_head_term_issues
from gnd.model._validation import _derivation_id as _derivation_id
from gnd.model._validation import _derivation_positive_variables as _derivation_positive_variables
from gnd.model._validation import _derivation_rule_hint as _derivation_rule_hint
from gnd.model._validation import _derivation_scope_variables as _derivation_scope_variables
from gnd.model._validation import _derivation_variable as _derivation_variable
from gnd.model._validation import _derivation_variable_primitives as _derivation_variable_primitives
from gnd.model._validation import _fact_type_roles as _fact_type_roles
from gnd.model._validation import _filter_derivation_term_issues as _filter_derivation_term_issues
from gnd.model._validation import (
    _guarded_literal_kinds_compatible as _guarded_literal_kinds_compatible,
)
from gnd.model._validation import (
    _guarded_literal_matches_primitive as _guarded_literal_matches_primitive,
)
from gnd.model._validation import (
    _guarded_nested_function_variables as _guarded_nested_function_variables,
)
from gnd.model._validation import _guarded_primitives_compatible as _guarded_primitives_compatible
from gnd.model._validation import _internal_uniqueness_keys as _internal_uniqueness_keys
from gnd.model._validation import _is_structured_rule as _is_structured_rule
from gnd.model._validation import _iter_constraints as _iter_constraints
from gnd.model._validation import _iter_guarded_atoms as _iter_guarded_atoms
from gnd.model._validation import _iter_guarded_consequent_terms as _iter_guarded_consequent_terms
from gnd.model._validation import _iter_guarded_constraints as _iter_guarded_constraints
from gnd.model._validation import _iter_operation_atoms as _iter_operation_atoms
from gnd.model._validation import _iter_operation_obligations as _iter_operation_obligations
from gnd.model._validation import _iter_operation_terms as _iter_operation_terms
from gnd.model._validation import _iter_operations as _iter_operations
from gnd.model._validation import _iter_provenance_bearing as _iter_provenance_bearing
from gnd.model._validation import _iter_role_refs as _iter_role_refs
from gnd.model._validation import (
    _iter_structured_fact_derivations as _iter_structured_fact_derivations,
)
from gnd.model._validation import _joining_sequences as _joining_sequences
from gnd.model._validation import _layer1_structural as _layer1_structural
from gnd.model._validation import _load_meta_schema as _load_meta_schema
from gnd.model._validation import _operation_parameters as _operation_parameters
from gnd.model._validation import _primitive_maps as _primitive_maps
from gnd.model._validation import _provenance_bearing_label as _provenance_bearing_label
from gnd.model._validation import _range_endpoints_valid as _range_endpoints_valid
from gnd.model._validation import _resolved_primitive as _resolved_primitive
from gnd.model._validation import _role_object_types as _role_object_types
from gnd.model._validation import _rule_aggregate_as_not_fresh as _rule_aggregate_as_not_fresh
from gnd.model._validation import _rule_aggregate_function as _rule_aggregate_function
from gnd.model._validation import (
    _rule_aggregate_head_needs_round as _rule_aggregate_head_needs_round,
)
from gnd.model._validation import _rule_aggregate_head_scope as _rule_aggregate_head_scope
from gnd.model._validation import _rule_aggregate_input_type as _rule_aggregate_input_type
from gnd.model._validation import _rule_aggregate_of_unbound as _rule_aggregate_of_unbound
from gnd.model._validation import _rule_aggregate_over_duplicate as _rule_aggregate_over_duplicate
from gnd.model._validation import _rule_aggregate_over_unbound as _rule_aggregate_over_unbound
from gnd.model._validation import _rule_aggregate_shape as _rule_aggregate_shape
from gnd.model._validation import _rule_aggregate_where_scope as _rule_aggregate_where_scope
from gnd.model._validation import (
    _rule_anchored_role_and_recogniser as _rule_anchored_role_and_recogniser,
)
from gnd.model._validation import _rule_count_bound_order as _rule_count_bound_order
from gnd.model._validation import _rule_cross_ref as _rule_cross_ref
from gnd.model._validation import _rule_depends_on as _rule_depends_on
from gnd.model._validation import (
    _rule_derivation_body_component_unused as _rule_derivation_body_component_unused,
)
from gnd.model._validation import (
    _rule_derivation_dynamic_dependency_incomplete as _rule_derivation_dynamic_dependency_incomplete,
)
from gnd.model._validation import (
    _rule_derivation_effect_on_derived as _rule_derivation_effect_on_derived,
)
from gnd.model._validation import (
    _rule_derivation_effect_on_semiderived as _rule_derivation_effect_on_semiderived,
)
from gnd.model._validation import (
    _rule_derivation_float_head_unquantized as _rule_derivation_float_head_unquantized,
)
from gnd.model._validation import (
    _rule_derivation_head_needs_round as _rule_derivation_head_needs_round,
)
from gnd.model._validation import (
    _rule_derivation_head_role_claim as _rule_derivation_head_role_claim,
)
from gnd.model._validation import _rule_derivation_head_term_type as _rule_derivation_head_term_type
from gnd.model._validation import _rule_derivation_head_unbound as _rule_derivation_head_unbound
from gnd.model._validation import _rule_derivation_negate_unbound as _rule_derivation_negate_unbound
from gnd.model._validation import (
    _rule_derivation_opaque_dependency as _rule_derivation_opaque_dependency,
)
from gnd.model._validation import _rule_derivation_role_claim as _rule_derivation_role_claim
from gnd.model._validation import _rule_derivation_rule_shape as _rule_derivation_rule_shape
from gnd.model._validation import (
    _rule_derivation_structured_on_object_type as _rule_derivation_structured_on_object_type,
)
from gnd.model._validation import _rule_derivation_term_ref as _rule_derivation_term_ref
from gnd.model._validation import _rule_derivation_term_type as _rule_derivation_term_type
from gnd.model._validation import _rule_derivation_term_unbound as _rule_derivation_term_unbound
from gnd.model._validation import _rule_derivation_unstratified as _rule_derivation_unstratified
from gnd.model._validation import _rule_disjunctive_subject_type as _rule_disjunctive_subject_type
from gnd.model._validation import _rule_external_ref_uc as _rule_external_ref_uc
from gnd.model._validation import _rule_fact_type_arity as _rule_fact_type_arity
from gnd.model._validation import _rule_guarded_comparison_type as _rule_guarded_comparison_type
from gnd.model._validation import _rule_guarded_consequent_ground as _rule_guarded_consequent_ground
from gnd.model._validation import _rule_guarded_exists_range as _rule_guarded_exists_range
from gnd.model._validation import (
    _rule_guarded_exists_where_bound as _rule_guarded_exists_where_bound,
)
from gnd.model._validation import _rule_guarded_exists_where_type as _rule_guarded_exists_where_type
from gnd.model._validation import _rule_guarded_role_claim as _rule_guarded_role_claim
from gnd.model._validation import _rule_guarded_term_ref as _rule_guarded_term_ref
from gnd.model._validation import _rule_id_unique as _rule_id_unique
from gnd.model._validation import (
    _rule_imported_confirmed_reviewed as _rule_imported_confirmed_reviewed,
)
from gnd.model._validation import _rule_imported_provenance as _rule_imported_provenance
from gnd.model._validation import _rule_join_anchor_unambiguous as _rule_join_anchor_unambiguous
from gnd.model._validation import _rule_modality_policy as _rule_modality_policy
from gnd.model._validation import _rule_op_atom_ref as _rule_op_atom_ref
from gnd.model._validation import _rule_op_create_param as _rule_op_create_param
from gnd.model._validation import _rule_op_create_ref_mode as _rule_op_create_ref_mode
from gnd.model._validation import _rule_op_dynamic_functional as _rule_op_dynamic_functional
from gnd.model._validation import _rule_op_dynamic_untouched as _rule_op_dynamic_untouched
from gnd.model._validation import _rule_op_effect_ground as _rule_op_effect_ground
from gnd.model._validation import _rule_op_modality_policy as _rule_op_modality_policy
from gnd.model._validation import (
    _rule_op_obligation_ids_distinct as _rule_op_obligation_ids_distinct,
)
from gnd.model._validation import _rule_op_param_names_distinct as _rule_op_param_names_distinct
from gnd.model._validation import _rule_op_param_ref as _rule_op_param_ref
from gnd.model._validation import _rule_op_reading_placeholders as _rule_op_reading_placeholders
from gnd.model._validation import _rule_op_term_ref as _rule_op_term_ref
from gnd.model._validation import _rule_op_term_type_compat as _rule_op_term_type_compat
from gnd.model._validation import (
    _rule_partition_asserts_something as _rule_partition_asserts_something,
)
from gnd.model._validation import _rule_reading_placeholders as _rule_reading_placeholders
from gnd.model._validation import _rule_reference_value_type as _rule_reference_value_type
from gnd.model._validation import _rule_ring_binary as _rule_ring_binary
from gnd.model._validation import _rule_role_names_distinct as _rule_role_names_distinct
from gnd.model._validation import _rule_role_ref as _rule_role_ref
from gnd.model._validation import _rule_role_seq_arity as _rule_role_seq_arity
from gnd.model._validation import _rule_role_seq_type_compat as _rule_role_seq_type_compat
from gnd.model._validation import _rule_status_source as _rule_status_source
from gnd.model._validation import _rule_string_ref as _rule_string_ref
from gnd.model._validation import _rule_subtype_ref as _rule_subtype_ref
from gnd.model._validation import _rule_temporal_language as _rule_temporal_language
from gnd.model._validation import _rule_term_argument_type as _rule_term_argument_type
from gnd.model._validation import _rule_term_comparison_type as _rule_term_comparison_type
from gnd.model._validation import _rule_term_depth_budget as _rule_term_depth_budget
from gnd.model._validation import _rule_term_function_arity as _rule_term_function_arity
from gnd.model._validation import _rule_term_function_name as _rule_term_function_name
from gnd.model._validation import _rule_term_node_budget as _rule_term_node_budget
from gnd.model._validation import _rule_term_non_finite_number as _rule_term_non_finite_number
from gnd.model._validation import _rule_term_shape as _rule_term_shape
from gnd.model._validation import _rule_term_unbound as _rule_term_unbound
from gnd.model._validation import _rule_textual_alethic as _rule_textual_alethic
from gnd.model._validation import _rule_value_range_order as _rule_value_range_order
from gnd.model._validation import _rule_value_range_type as _rule_value_range_type
from gnd.model._validation import _safe_key as _safe_key
from gnd.model._validation import _supertype_parents as _supertype_parents
from gnd.model._validation import _temporal_literal_valid as _temporal_literal_valid
from gnd.model._validation import _variable_name as _variable_name
from gnd.model._validation import analyze_aggregate as analyze_aggregate
from gnd.model._validation import analyze_declared_aggregate as analyze_declared_aggregate
from gnd.model._validation import analyze_term as analyze_term
from gnd.model._validation import atom_bind as atom_bind
from gnd.model._validation import atom_has_bind as atom_has_bind
from gnd.model._validation import body_components as body_components
from gnd.model._validation import configure_comment_scanner as configure_comment_scanner
from gnd.model._validation import dataclass as dataclass
from gnd.model._validation import date as date
from gnd.model._validation import datetime as datetime
from gnd.model._validation import derivation_classifications as derivation_classifications
from gnd.model._validation import derivation_dependencies as derivation_dependencies
from gnd.model._validation import derivation_dependency_closure as derivation_dependency_closure
from gnd.model._validation import derivation_dependency_edges as derivation_dependency_edges
from gnd.model._validation import derivation_strata as derivation_strata
from gnd.model._validation import dynamic_subject_is_functional as dynamic_subject_is_functional
from gnd.model._validation import files as files
from gnd.model._validation import is_function_term as is_function_term
from gnd.model._validation import issues_from_validation_error as issues_from_validation_error
from gnd.model._validation import iter_derivation_clauses as iter_derivation_clauses
from gnd.model._validation import json as json
from gnd.model._validation import math as math
from gnd.model._validation import re as re
from gnd.model._validation import semantic_validate as semantic_validate
from gnd.model._validation import structured_derivation_ids as structured_derivation_ids
from gnd.model._validation import term_variables as term_variables
from gnd.model._validation import verbalize as verbalize
from gnd.model._validation import yaml_stream_guard_error as yaml_stream_guard_error

if TYPE_CHECKING:
    from gnd.population import Population

import hashlib
import os
import weakref
from contextlib import contextmanager
from typing import Literal

from gnd import artifacts
from gnd.values import reference_model_digest


def parse_model_document(data: bytes, *, source: str | Path) -> Any:
    """Parse one bounded model buffer exactly as ``load_model_bytes`` does: strict
    JSON for a ``.json`` source, otherwise the alias/event guard and then the
    round-trip YAML reader. The document is returned unvalidated."""
    from ruamel.yaml.events import AliasEvent

    if len(data) > MAX_MODEL_BYTES:
        raise ModelLoadError("model exceeds the 10 MiB input cap")
    text = data.decode("utf-8")
    if re.search(r"(?m)[|>][-+0-9]{0,2}[ \t]*(?:#.*)?$", text) is None:
        text = text.rstrip()
    doc = None
    if Path(source).suffix == ".json" or text.lstrip().startswith("{"):
        from gnd.errors import PopulationLoadError
        from gnd.population import _parse_document_bytes

        try:
            doc = _parse_document_bytes(data, suffix=".json", source=str(source))
        except PopulationLoadError as error:
            from gnd.input_policy import InputRefusal

            if (Path(source).suffix == ".json"
                    or not isinstance(error.__cause__, json.JSONDecodeError)
                    or isinstance(error.__cause__, InputRefusal)):
                raise ModelLoadError("model JSON input refused") from error
            # A YAML flow mapping may start with an unquoted key.
    if doc is None:
        for count, event in enumerate(configure_comment_scanner(YAML(typ="safe")).parse(text), 1):
            if count > MAX_YAML_EVENTS or isinstance(event, AliasEvent):
                raise ModelLoadError("model YAML alias/event guard refused input")
        doc = configure_comment_scanner(YAML(typ="rt")).load(text)
    return doc


def load_model_bytes(data: bytes, *, source: str | Path) -> Model:
    """Validate one immutable bounded buffer; source is diagnostic metadata."""
    doc = parse_model_document(data, source=source)
    issues = _layer1_structural(doc)
    if issues:
        raise ModelValidationError(issues)
    issues = semantic_validate(dict(doc))
    errors = [issue for issue in issues if issue.severity == "error"]
    warnings = [issue for issue in issues if issue.severity == "warning"]
    if errors:
        raise ModelValidationError(errors, warnings)
    model = Model.model_validate({**dict(doc), "warnings": warnings})

    validate_declarations(model)
    _attach_compiled_obligations(model)
    return model


def _load_model_no_follow(path: Path) -> Model:
    """Strict path intake for consumers whose contract forbids symlink traversal."""
    from gnd import artifacts

    with retained_root(path.parent) as descriptor:
        data, _ = artifacts.read_regular_bounded_at(
            descriptor, path.name, max_bytes=MAX_MODEL_BYTES
        )
        model = load_model_bytes(data, source=path)
        if model.reference_populations:
            try:
                model._references = _bind_at(model, descriptor)
            except Exception as error:
                raise ReferenceInputError(str(error), model=model) from error
        return model


def load_model(path: str | Path) -> Model:
    """Read model and reference bytes beneath a single retained directory."""
    import os

    from gnd import artifacts

    path = Path(path)
    if hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY"):
        try:
            return _load_model_no_follow(path)
        except (OSError, artifacts.ArtifactError):
            # Only reference-free models retain the historical symlink route.
            pass
    import stat

    if not stat.S_ISREG(path.stat().st_mode):
        raise ModelLoadError("model path is not a regular file")
    with path.open("rb") as handle:
        data = handle.read(MAX_MODEL_BYTES + 1)
    model = load_model_bytes(data, source=path)
    if model.reference_populations:
        raise ReferenceInputError(
            "safe reference descriptor traversal is unavailable or refused the model path",
            model=model,
        )
    return model


# --------------------------------------------------------------------------- #
# Trace compilation (B2) -- in memory, per operation, never serialized
# --------------------------------------------------------------------------- #




MAX_BYTES = 10 * 1024 * 1024


MAX_SET_BYTES = 32 * 1024 * 1024


MAX_ENTRIES = 100_000


_TOKEN = object()


_BOUND = weakref.WeakValueDictionary()


_COMBINED = weakref.WeakValueDictionary()


class ReferenceInputError(ValueError):
    """A reference boundary refused its input before domain evaluation."""

    def __init__(self, message: str, *, model: Model | None = None):
        super().__init__(message)
        self.model = model


@dataclass(frozen=True)
class ReferenceOrigin:
    id: str
    raw_sha256: str


@dataclass(frozen=True)
class OccurrenceOrigin:
    kind: Literal["candidate", "reference"]
    reference_id: str | None


@dataclass(frozen=True)
class BoundReferenceContext:
    _model: Model
    _digest: str
    _snapshots: tuple[tuple[ReferenceOrigin, str, bytes], ...]
    _owners: tuple[tuple[str, str], ...]
    _populations: tuple[Population, ...]
    _token: object


@dataclass(frozen=True)
class BoundPopulationView:
    combined: Population
    candidate: Population
    occurrence_origins: tuple[dict[str, Any], ...]
    references: BoundReferenceContext


def validate_reference_structure(document: object) -> None:
    stack = [(document, 0)]
    while stack:
        node, parent_depth = stack.pop()
        if isinstance(node, (list, dict)):
            depth = parent_depth + 1
            if depth > 64:
                raise ReferenceInputError("reference container depth exceeds 64")
            stack.extend((v, depth) for v in (node.values() if isinstance(node, dict) else node))


def _relative(path: object) -> str:
    if not isinstance(path, str) or not path or len(path) > 4096:
        raise ReferenceInputError("reference path is empty or exceeds 4096 characters")
    parts = path.split("/")
    if len(parts) > 32 or any(p in {"", ".", ".."} for p in parts):
        raise ReferenceInputError(
            "reference path must have at most 32 nonempty relative components"
        )
    if "\\" in path or "\x00" in path or re.match(r"^[A-Za-z]:", path):
        raise ReferenceInputError("reference path is not a confined POSIX relative path")
    return path


@contextmanager
def retained_root(root: str | Path):
    """Open every lexical ancestor without following a symlink."""
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise ReferenceInputError("safe reference descriptor traversal is unavailable")
    absolute = Path(root)
    if not absolute.is_absolute():
        absolute = Path.cwd() / absolute
    descriptor = os.open(absolute.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in absolute.parts[1:]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_fd
        yield descriptor
    finally:
        os.close(descriptor)


def validate_declarations(model: Model) -> dict[str, str]:
    declarations = model.reference_populations
    if declarations:
        from gnd.model import _layer1_structural, semantic_validate

        document = model.model_dump(exclude={"warnings"})
        if _layer1_structural(document) or any(
            i.severity == "error" for i in semantic_validate(document)
        ):
            raise ReferenceInputError("reference-bearing model structure or semantics are invalid")
    if declarations and model.version != 4:
        raise ReferenceInputError("reference_populations requires model version 4")
    if len(declarations) > 32:
        raise ReferenceInputError("reference file count exceeds 32")
    ids: set[str] = set()
    owners: dict[str, str] = {}
    types = {ft["id"]: ft for ft in model.fact_types}
    for d in declarations:
        if set(d) != {"id", "path", "sha256", "fact_types"}:
            raise ReferenceInputError("reference declaration has missing or extra fields")
        identifier = d["id"]
        if not isinstance(identifier, str) or not 1 <= len(identifier) <= 128 or identifier in ids:
            raise ReferenceInputError("reference id must be unique and 1..128 characters")
        ids.add(identifier)
        _relative(d["path"])
        if not isinstance(d["sha256"], str) or not re.fullmatch("[0-9a-f]{64}", d["sha256"]):
            raise ReferenceInputError("reference sha256 must be 64 lowercase hexadecimal digits")
        claimed = d["fact_types"]
        if not isinstance(claimed, list) or not claimed:
            raise ReferenceInputError("reference fact_types must be a nonempty list")
        for ft in claimed:
            if not isinstance(ft, str) or ft not in types or ft in owners:
                raise ReferenceInputError(
                    "reference fact ownership is unknown, duplicated or overlapping"
                )
            if types[ft].get("derivation", "base") not in {"base", None}:
                raise ReferenceInputError("references may own only base fact types")
            owners[ft] = identifier
    for operation in model.operations:
        for effect in operation.get("effects", []):
            for action in ("assert", "retract"):
                if effect.get(action, {}).get("fact_type") in owners:
                    raise ReferenceInputError(
                        "operation effects cannot write a reference-owned fact type"
                    )
    return owners


def _bind_at(model: Model, descriptor: int) -> BoundReferenceContext:
    from gnd.population import PopulationLoadError, _build_population, _parse_document_bytes

    owners = validate_declarations(model)
    snapshots = []
    populations = []
    fact_entries = instance_entries = 0
    total = 0
    for d in sorted(model.reference_populations, key=lambda d: d["id"]):
        raw, _leaf = artifacts.read_regular_bounded_at(descriptor, d["path"], max_bytes=MAX_BYTES)
        total += len(raw)
        if total > MAX_SET_BYTES:
            raise ReferenceInputError("reference set exceeds 32 MiB")
        digest = hashlib.sha256(raw).hexdigest()
        if digest != d["sha256"]:
            raise ReferenceInputError("reference raw hash does not match declared sha256")
        doc = _parse_document_bytes(raw, suffix=Path(d["path"]).suffix, source=d["path"])
        validate_reference_structure(doc)
        if isinstance(doc, dict):
            for section in ("facts", "instances"):
                entries = doc.get(section, {})
                if (
                    isinstance(entries, dict)
                    and sum(len(rows) for rows in entries.values() if isinstance(rows, list))
                    > MAX_ENTRIES
                ):
                    raise ReferenceInputError("reference entries exceed 100000")
        try:
            pop = _build_population(doc, model=model, deduplicate_shape_rows=True)
        except PopulationLoadError as error:
            raise ReferenceInputError(
                "reference population structure or types are invalid"
            ) from error
        if any(ft not in d["fact_types"] for ft in pop.facts):
            raise ReferenceInputError("reference asserts an unowned fact type")
        fact_entries += sum(map(len, pop.facts.values()))
        instance_entries += sum(map(len, pop.instances.values()))
        if fact_entries > MAX_ENTRIES or instance_entries > MAX_ENTRIES:
            raise ReferenceInputError("reference fact or instance entry count exceeds 100000")
        snapshots.append((ReferenceOrigin(d["id"], digest), d["path"], raw))
        populations.append(pop)
    context = BoundReferenceContext(
        model,
        reference_model_digest(model),
        tuple(snapshots),
        tuple(sorted(owners.items())),
        tuple(populations),
        _TOKEN,
    )
    _BOUND[id(context)] = context
    return context


def bind_references(model: Model, *, root: str | Path) -> BoundReferenceContext:
    validate_declarations(model)
    with retained_root(root) as descriptor:
        return _bind_at(model, descriptor)


def bind_declared_references(
    model: Model, *, root: str | Path, attach: bool = False
) -> BoundReferenceContext | None:
    """Bind a model's declared reference populations at ``root``, or return None
    when it declares none. The binder's own exceptions pass through unwrapped,
    so every caller keeps its refusal mapping (IK4-Q2-R1). ``attach`` also sets
    the context on the model."""
    if not model.reference_populations:
        return None
    context = bind_references(model, root=root)
    if attach:
        model._references = context
    return context


def load_model_bytes_bound(
    data: bytes, *, source: str | Path, root: str | Path, attach: bool = False
) -> tuple[Model, BoundReferenceContext | None]:
    """``load_model_bytes``, then ``bind_declared_references`` at ``root``; neither
    step's exceptions are wrapped."""
    model = load_model_bytes(data, source=source)
    return model, bind_declared_references(model, root=root, attach=attach)


def resolve_context(
    model: Model, references: BoundReferenceContext | None = None
) -> BoundReferenceContext:
    context = references if references is not None else model._references
    if (
        not isinstance(context, BoundReferenceContext)
        or context._token is not _TOKEN
        or _BOUND.get(id(context)) is not context
    ):
        raise ReferenceInputError("reference-bearing model requires a bound reference context")
    if context._model is not model or context._digest != reference_model_digest(model):
        raise ReferenceInputError("reference context does not match this model's current identity")
    owners = validate_declarations(model)
    expected = {d["id"]: d for d in model.reference_populations}
    if tuple(sorted(owners.items())) != context._owners or len(expected) != len(context._snapshots):
        raise ReferenceInputError("reference context ownership or snapshot roster changed")
    if len(context._populations) != len(context._snapshots) or any(
        not pop.matches_validation_marker(model) for pop in context._populations
    ):
        raise ReferenceInputError("reference context validated population changed")
    for origin, path, raw in context._snapshots:
        declaration = expected.get(origin.id)
        if (
            declaration is None
            or path != declaration["path"]
            or origin.raw_sha256 != declaration["sha256"]
            or hashlib.sha256(raw).hexdigest() != origin.raw_sha256
        ):
            raise ReferenceInputError("reference context snapshot identity changed")
    return context


def bind_population(
    model: Model, candidate: Population, *, references: BoundReferenceContext
) -> BoundPopulationView:
    from gnd.population import _combine_validated_populations
    from gnd.values import identity_key as _identity_key

    context = resolve_context(model, references)
    owners = dict(context._owners)
    if any(ft in owners for ft in candidate.facts):
        raise ReferenceInputError("candidate cannot mention a reference-owned fact type")
    if not candidate.matches_validation_marker(model):
        raise ReferenceInputError("candidate population is not validated against the current model")
    facts = {ft: [dict(row) for row in rows] for ft, rows in candidate.facts.items()}
    instances = {ot: list(values) for ot, values in candidate.instances.items()}
    covers = list(candidate.covers)
    format_version = candidate.format_version
    origins = [
        {"origin": {"kind": "candidate", "reference_id": None}, "fact_type": ft, "index": i}
        for ft, rows in candidate.facts.items()
        for i in range(len(rows))
    ]
    for (origin, _path, _raw), pop in zip(context._snapshots, context._populations, strict=True):
        format_version = max(format_version, pop.format_version)
        for ot, values in pop.instances.items():
            instances.setdefault(ot, []).extend(values)
        for ft, rows in pop.facts.items():
            facts[ft] = [dict(row) for row in rows]
            origins.extend(
                {
                    "origin": {"kind": "reference", "reference_id": origin.id},
                    "fact_type": ft,
                    "index": i,
                }
                for i in range(len(rows))
            )
        covers.extend(ft for ft in pop.covers if ft not in covers)
    if (
        sum(map(len, facts.values())) > MAX_ENTRIES
        or sum(map(len, instances.values())) > MAX_ENTRIES
    ):
        raise ReferenceInputError("combined fact or instance entry count exceeds 100000")
    instances = {
        ot: list({_identity_key(value): value for value in values}.values())
        for ot, values in instances.items()
    }
    combined = _combine_validated_populations(
        model,
        (candidate, *context._populations),
        {
            "format_version": format_version,
            "population": {
                "model": candidate.model,
                "model_id": candidate.model_id,
                "source": candidate.source,
                "covers": covers,
            },
            "facts": facts,
            "instances": instances,
        },
    )
    combined._reference_combined = True
    combined._reference_context = context
    _COMBINED[id(combined)] = combined
    origins.sort(
        key=lambda row: (
            row["origin"]["kind"],
            row["origin"]["reference_id"] or "",
            row["fact_type"],
            row["index"],
        )
    )
    return BoundPopulationView(combined, candidate, tuple(origins), context)


def candidate_fact_count(view: BoundPopulationView) -> int:
    return sum(map(len, view.candidate.facts.values()))


def is_bound_population(
    model: Model, population: Population, context: BoundReferenceContext
) -> bool:
    """Recognize only a current combined population created by this binder."""
    return (
        _COMBINED.get(id(population)) is population
        and population._reference_context is context
        and population.matches_validation_marker(model)
    )


BOUND = _BOUND
COMBINED = _COMBINED
TOKEN = _TOKEN
bind_at = _bind_at
relative = _relative

ReferenceInputError.__module__ = 'gnd.references'
ReferenceOrigin.__module__ = 'gnd.references'
OccurrenceOrigin.__module__ = 'gnd.references'
BoundReferenceContext.__module__ = 'gnd.references'
BoundPopulationView.__module__ = 'gnd.references'
validate_reference_structure.__module__ = 'gnd.references'
_relative.__module__ = 'gnd.references'
retained_root.__module__ = 'gnd.references'
validate_declarations.__module__ = 'gnd.references'
_bind_at.__module__ = 'gnd.references'
bind_references.__module__ = 'gnd.references'
resolve_context.__module__ = 'gnd.references'
bind_population.__module__ = 'gnd.references'
candidate_fact_count.__module__ = 'gnd.references'
is_bound_population.__module__ = 'gnd.references'
load_model_bytes.__module__ = 'gnd.model'
_load_model_no_follow.__module__ = 'gnd.model'
load_model.__module__ = 'gnd.model'
ReferenceInputError.__module__ = 'gnd.references'
ReferenceOrigin.__module__ = 'gnd.references'
OccurrenceOrigin.__module__ = 'gnd.references'
BoundReferenceContext.__module__ = 'gnd.references'
BoundPopulationView.__module__ = 'gnd.references'
validate_reference_structure.__module__ = 'gnd.references'
_relative.__module__ = 'gnd.references'
retained_root.__module__ = 'gnd.references'
validate_declarations.__module__ = 'gnd.references'
_bind_at.__module__ = 'gnd.references'
bind_references.__module__ = 'gnd.references'
resolve_context.__module__ = 'gnd.references'
bind_population.__module__ = 'gnd.references'
candidate_fact_count.__module__ = 'gnd.references'
is_bound_population.__module__ = 'gnd.references'
ReferenceInputError.__dict__['__init__'].__module__ = 'gnd.model'
ReferenceOrigin.__dict__['__hash__'].__module__ = 'gnd.model'
ReferenceOrigin.__dict__['__init__'].__module__ = 'gnd.model'
ReferenceOrigin.__dict__['__repr__'].__module__ = 'gnd.model'
ReferenceOrigin.__dict__['__eq__'].__module__ = 'gnd.model'
ReferenceOrigin.__dict__['__setattr__'].__module__ = 'gnd.model'
ReferenceOrigin.__dict__['__delattr__'].__module__ = 'gnd.model'
OccurrenceOrigin.__dict__['__hash__'].__module__ = 'gnd.model'
OccurrenceOrigin.__dict__['__init__'].__module__ = 'gnd.model'
OccurrenceOrigin.__dict__['__repr__'].__module__ = 'gnd.model'
OccurrenceOrigin.__dict__['__eq__'].__module__ = 'gnd.model'
OccurrenceOrigin.__dict__['__setattr__'].__module__ = 'gnd.model'
OccurrenceOrigin.__dict__['__delattr__'].__module__ = 'gnd.model'
BoundReferenceContext.__dict__['__hash__'].__module__ = 'gnd.model'
BoundReferenceContext.__dict__['__init__'].__module__ = 'gnd.model'
BoundReferenceContext.__dict__['__repr__'].__module__ = 'gnd.model'
BoundReferenceContext.__dict__['__eq__'].__module__ = 'gnd.model'
BoundReferenceContext.__dict__['__setattr__'].__module__ = 'gnd.model'
BoundReferenceContext.__dict__['__delattr__'].__module__ = 'gnd.model'
BoundPopulationView.__dict__['__hash__'].__module__ = 'gnd.model'
BoundPopulationView.__dict__['__init__'].__module__ = 'gnd.model'
BoundPopulationView.__dict__['__repr__'].__module__ = 'gnd.model'
BoundPopulationView.__dict__['__eq__'].__module__ = 'gnd.model'
BoundPopulationView.__dict__['__setattr__'].__module__ = 'gnd.model'
BoundPopulationView.__dict__['__delattr__'].__module__ = 'gnd.model'


def __getattr__(name: str):
    """Expose mutable validation counters at their current defining state."""
    if name in {'_DERIVATION_WORK', '_DERIVATION_ATOM_VISITS', '_DERIVATION_CLASSIFICATION_WORK'}:
        from gnd.model import _validation

        return getattr(_validation, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
