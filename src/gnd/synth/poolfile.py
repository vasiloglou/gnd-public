"""The pool artifact: load / validate / write / build, with one notion of validity.

A POOL ARTIFACT is the single seam between any proposer and deterministic
assembly (D-19). An LLM-proposed pool and a Faker-built pool are the same shape,
validated against ``pool.schema.json``, content-addressed by sha256 over the
canonical JSON encoding, and carrying provenance. Nothing downstream can tell
which source produced a pool except by reading ``provenance.source``.

Two gates run on load, in order (:func:`load_pool`):

1. **Schema** — the strict closed contract ``pool.schema.json``. Any failure
   rejects; a malformed pool is never coherence-checked.
2. **Coherence, model-relative** — every object type covered, every sample
   satisfying ``popvalidate``'s OWN primitive predicate (resolve-or-skip where the
   primitive is unresolvable, C10/D-05), every value-constrained sample in range,
   and enough DISTINCT identifiers per type for the largest lower-bound demand the
   model makes (uniqueness / frequency / cardinality / mandatory, plus
   cross-fact-type join recurrence — the degeneracy that made Polyfactory's
   all-distinct pools produce zero-row joins across the F-05 frontier).

An agent-composed pool is UNTRUSTED input (T-02-28): rejection is whole-pool,
loud, and carries the FULL enumerated failure list — the caller may be a
proposer's bounded repair loop, and a truncated list starves the repair. There is
no partial-acceptance mode.

The Faker builder (:func:`build_faker_pool`) draws every value through
``values.make_value`` — the same dispatch the loader validates against — so
builder and validator can never disagree about what a valid value is, and its
output round-trips its own gate (asserted in the tests).
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from random import Random
from typing import Any

from gnd import popvalidate
from gnd.model import Model
from gnd.synth.identity import scalar_identity
from gnd.synth.value_domain import (
    EmptyValueDomain,
    constraint_accepts,
    draw_value_for_constraints,
    object_value_constraints,
    value_satisfies_all,
)

try:
    from importlib.resources import files as _resource_files
except ImportError:  # pragma: no cover - importlib.resources.files is stdlib on 3.11+
    _resource_files = None  # type: ignore[assignment]

from jsonschema import Draft202012Validator

__all__ = [
    "Pool",
    "PoolValidationError",
    "build_faker_pool",
    "load_pool",
    "write_pool",
]

#: Families whose evaluation JOINS two or more fact types. An object type that
#: fills a role in ≥2 of the fact types a single join-scoped constraint
#: references is a join key: its identifiers must recur across those fact types
#: for the join to have rows, so the coherence gate demands enough of them.
_JOIN_SCOPED_TYPES = frozenset(
    {"subset", "equality", "exclusion", "exclusive-or", "mandatory-disjunctive"}
)


class PoolValidationError(Exception):
    """A pool failed the schema or coherence gate.

    Carries the FULL enumerated failure list (``.failures``); ``str`` renders it
    as one message per line so a proposer's repair loop sees every defect at once.
    """

    def __init__(self, failures: list[str]) -> None:
        self.failures = list(failures)
        joined = "\n  ".join(self.failures)
        super().__init__(f"pool rejected with {len(self.failures)} failure(s):\n  {joined}")


@dataclass(frozen=True)
class Pool:
    """A loaded, gate-passed pool artifact.

    ``sha256`` is the pool's identity — computed over the canonical JSON encoding
    of the document, excluding nothing (D-07′). Two writers producing the same
    logical pool in different key orders yield the same hash.
    """

    object_types: dict[str, list[Any]]
    value_types: dict[str, list[Any]]
    provenance: dict[str, Any]
    sha256: str
    domain_narrative: str | None = None


# --------------------------------------------------------------------------- #
# canonical encoding + hashing
# --------------------------------------------------------------------------- #


def _payload_of(
    object_types: dict[str, list[Any]],
    value_types: dict[str, list[Any]],
    provenance: dict[str, Any],
    domain_narrative: str | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "object_types": object_types,
        "value_types": value_types,
        "provenance": provenance,
    }
    if domain_narrative is not None:
        payload["domain_narrative"] = domain_narrative
    return payload


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    """Deterministic, key-sorted, whitespace-free JSON — the hash input.

    ``sort_keys`` makes the hash independent of key order; compact separators and
    ``ensure_ascii=False`` make it independent of the writer's formatting choices.
    """
    try:
        rendered = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except ValueError as error:
        raise PoolValidationError(
            [f"pool contains a non-finite number that strict JSON cannot encode: {error}"]
        ) from error
    return rendered.encode("utf-8")


def _sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _non_finite_failures(value: Any, path: str = "$") -> list[str]:
    """Recursively locate numbers that are not interchange JSON scalars."""
    failures: list[str] = []
    if isinstance(value, float) and not math.isfinite(value):
        failures.append(f"{path} contains non-finite number {value!r}")
    elif isinstance(value, dict):
        for key, member in value.items():
            failures.extend(_non_finite_failures(member, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, member in enumerate(value):
            failures.extend(_non_finite_failures(member, f"{path}[{index}]"))
    return failures


def _load_pool_schema() -> dict[str, Any]:
    text = _resource_files("gnd").joinpath("pool.schema.json").read_text(encoding="utf-8")
    return json.loads(text)


# --------------------------------------------------------------------------- #
# model introspection — one notion of validity, borrowed from popvalidate
# --------------------------------------------------------------------------- #


def _object_types_by_id(model: Model) -> dict[str, dict[str, Any]]:
    return {
        str(ot.get("id")): ot
        for ot in model.object_types or []
        if ot.get("id") is not None
    }


def _iter_all_constraints(model: Model):
    """Yield ``(fact_type_id | None, constraint)`` for every active constraint."""
    for fact_type in model.fact_types or []:
        ftid = fact_type.get("id")
        for constraint in fact_type.get("constraints") or []:
            yield ftid, constraint
    for constraint in model.constraints or []:
        yield None, constraint


def _object_scope_value_constraints(model: Model) -> dict[str, list[dict[str, Any]]]:
    """Object-type-scoped ``value`` constraints (``allowed`` / ``range``).

    Only the OBJECT-scope ones (no ``role_ref``): a role-scoped value constraint
    narrows one role's population and is an assembly-layer concern, not a property
    of every sample of the type.
    """
    return object_value_constraints(model)


def _ref_object_type(role_obj: dict[str, dict[str, str]], ref: Any) -> str | None:
    if not isinstance(ref, dict):
        return None
    return role_obj.get(str(ref.get("fact_type")), {}).get(str(ref.get("role")))


def _join_key_types(model: Model) -> set[str]:
    """Object types that recur across ≥2 fact types within one join-scoped constraint."""
    role_obj = popvalidate._role_object_types(model)
    keys: set[str] = set()
    for _ftid, constraint in _iter_all_constraints(model):
        ctype = constraint.get("type")
        refs: list[tuple[str | None, str | None]] = []
        if ctype in _JOIN_SCOPED_TYPES:
            for field in ("subset_role_seq", "superset_role_seq", "role_seq_a", "role_seq_b"):
                for ref in constraint.get(field) or []:
                    refs.append((str(ref.get("fact_type")), _ref_object_type(role_obj, ref)))
            for seq in constraint.get("role_seqs") or []:
                for ref in seq or []:
                    refs.append((str(ref.get("fact_type")), _ref_object_type(role_obj, ref)))
            for ref in constraint.get("role_refs") or []:
                refs.append((str(ref.get("fact_type")), _ref_object_type(role_obj, ref)))
        elif ctype in ("uniqueness", "frequency") and constraint.get("scope") == "external":
            for ref in constraint.get("role_refs") or []:
                refs.append((str(ref.get("fact_type")), _ref_object_type(role_obj, ref)))
        elif ctype == "value-comparison":
            ra, rb = constraint.get("role_a"), constraint.get("role_b")
            if isinstance(ra, dict) and isinstance(rb, dict):
                for ref in (ra, rb):
                    refs.append((str(ref.get("fact_type")), _ref_object_type(role_obj, ref)))
        else:
            continue
        by_object: dict[str, set[str]] = {}
        for ftid, oid in refs:
            if oid is None or ftid is None:
                continue
            by_object.setdefault(oid, set()).add(ftid)
        for oid, fact_types in by_object.items():
            if len(fact_types) >= 2:
                keys.add(oid)
    return keys


def _distinctness_demand(model: Model) -> dict[str, tuple[int, str]]:
    """Per object type: ``(minimum distinct values, reason)``.

    The reason names the constraint family that drove the demand, so a rejection
    can tell a proposer WHY more identifiers are needed rather than only that they
    are. Contributors: role participation (1), uniqueness (2), frequency ``{min}``,
    cardinality ``{min}``, and join recurrence (2). ``mandatory`` folds into the
    role-participation baseline (every instance must be able to play the role).
    """
    role_obj = popvalidate._role_object_types(model)
    demand: dict[str, tuple[int, str]] = {}

    def bump(oid: str | None, n: int, reason: str) -> None:
        if oid is None:
            return
        current = demand.get(oid, (0, ""))
        if n > current[0]:
            demand[oid] = (n, reason)

    # Baseline: every object type that fills a role needs at least one identifier.
    for roles in role_obj.values():
        for oid in roles.values():
            bump(oid, 1, "role participation")

    for ftid, constraint in _iter_all_constraints(model):
        ctype = constraint.get("type")
        if ctype == "uniqueness":
            if constraint.get("scope") == "external":
                for ref in constraint.get("role_refs") or []:
                    bump(_ref_object_type(role_obj, ref), 2, "external uniqueness")
            else:
                for role_name in constraint.get("roles") or []:
                    bump(role_obj.get(str(ftid), {}).get(str(role_name)), 2, "uniqueness")
        elif ctype == "frequency":
            bound = constraint.get("bound") or {}
            minimum = bound.get("min")
            if minimum is None:
                continue
            if constraint.get("scope") == "external":
                targets = [
                    _ref_object_type(role_obj, ref) for ref in constraint.get("role_refs") or []
                ]
            else:
                targets = [
                    role_obj.get(str(ftid), {}).get(str(rn))
                    for rn in constraint.get("roles") or []
                ]
            for oid in targets:
                bump(oid, int(minimum), f"frequency {{min: {int(minimum)}}}")
        elif ctype == "cardinality":
            bound = constraint.get("bound") or {}
            minimum = bound.get("min")
            if minimum is None:
                continue
            if constraint.get("scope") == "object":
                bump(constraint.get("object_type"), int(minimum), f"cardinality {{min: {int(minimum)}}}")
            else:
                bump(
                    _ref_object_type(role_obj, constraint.get("role_ref")),
                    int(minimum),
                    f"cardinality {{min: {int(minimum)}}}",
                )

    for oid in _join_key_types(model):
        bump(oid, 2, "join recurrence")

    return demand


# --------------------------------------------------------------------------- #
# value-constraint satisfaction (borrowing the loader's primitive predicates)
# --------------------------------------------------------------------------- #


def _satisfies_value_constraint(value: Any, spec: dict[str, Any]) -> tuple[bool, str]:
    if constraint_accepts(value, spec):
        return True, ""
    if "allowed" in spec:
        return False, f"is outside the allowed enum {spec['allowed']}"
    declared = spec.get("ranges") if spec.get("ranges") is not None else spec.get("range")
    return False, f"is outside the declared range domain {declared}"


def _distinct_count(values: list[Any]) -> int:
    return len({scalar_identity(value) for value in values})


# --------------------------------------------------------------------------- #
# load / write
# --------------------------------------------------------------------------- #


def _coherence_failures(payload: dict[str, Any], model: Model) -> list[str]:
    failures: list[str] = []
    object_bucket: dict[str, Any] = payload.get("object_types", {})
    value_bucket: dict[str, Any] = payload.get("value_types", {})
    value_constraints = _object_scope_value_constraints(model)
    demand = _distinctness_demand(model)

    for object_type in model.object_types or []:
        oid = str(object_type.get("id"))
        kind = object_type.get("kind")
        bucket = object_bucket if kind == "entity" else value_bucket
        bucket_name = "object_types" if kind == "entity" else "value_types"
        if oid not in bucket:
            failures.append(
                f"object type '{oid}' ({kind}) has no entry under {bucket_name}"
            )
            continue
        values = bucket[oid]

        # Resolve-or-skip primitive check (C10/D-05).
        primitive = popvalidate.resolve_primitive(oid, model)
        predicate = popvalidate._PRIMITIVE_PREDICATES.get(str(primitive)) if primitive else None
        if primitive is not None and predicate is not None:
            for index, value in enumerate(values):
                if not predicate(value):
                    failures.append(
                        f"'{oid}'[{index}] = {value!r} is not a valid {primitive}"
                    )
        # When primitive is None (unit-based / external reference, e.g. salary or
        # assignment) NO invented type check is performed — the loader itself
        # skips it silently (D-05), so the pool gate must too.

        # Value-constraint conformance.
        governed_oid = (
            str(popvalidate.resolve_reference_value_type(oid, model) or oid)
            if kind == "entity"
            else oid
        )
        declared_specs = value_constraints.get(governed_oid, [])
        # An unresolved primitive cannot be ordered against range bounds without
        # inventing a type interpretation. Enum membership remains mechanically
        # decidable through normative scalar identity, even for opaque values.
        specs = (
            declared_specs
            if primitive is not None
            else [spec for spec in declared_specs if spec.get("allowed") is not None]
        )
        if specs:
            for index, value in enumerate(values):
                for spec in specs:
                    ok, why = _satisfies_value_constraint(value, spec)
                    if not ok:
                        failures.append(f"'{oid}'[{index}] = {value!r} {why}")

        # Distinctness demand.
        needed, reason = demand.get(oid, (0, ""))
        have = _distinct_count(values)
        if have < needed:
            failures.append(
                f"'{oid}' supplies {have} distinct value(s) but needs >= {needed} "
                f"({reason})"
            )

    return failures


def load_pool(path: str | Path, model: Model) -> Pool:
    """Load, schema-gate, then coherence-gate a pool against ``model``.

    Raises :class:`PoolValidationError` carrying every failure. The two gates run
    in order; a schema failure short-circuits, because a malformed document cannot
    be coherence-checked meaningfully.
    """
    text = Path(path).read_text(encoding="utf-8")
    document = json.loads(text)

    finite_failures = _non_finite_failures(document)
    if finite_failures:
        raise PoolValidationError(finite_failures)

    schema = _load_pool_schema()
    validator = Draft202012Validator(schema)
    schema_failures = [
        f"schema: {error.json_path} — {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda e: e.json_path)
    ]
    if schema_failures:
        raise PoolValidationError(schema_failures)

    coherence_failures = _coherence_failures(document, model)
    if coherence_failures:
        raise PoolValidationError(coherence_failures)

    object_types = document["object_types"]
    value_types = document["value_types"]
    provenance = document["provenance"]
    domain_narrative = document.get("domain_narrative")
    payload = _payload_of(object_types, value_types, provenance, domain_narrative)
    return Pool(
        object_types=object_types,
        value_types=value_types,
        provenance=provenance,
        sha256=_sha256(payload),
        domain_narrative=domain_narrative,
    )


def write_pool(pool: Pool, path: str | Path) -> None:
    """Write ``pool`` as canonical (key-sorted) JSON, so any writer's bytes hash
    identically to any other's for the same logical pool."""
    payload = _payload_of(
        pool.object_types, pool.value_types, pool.provenance, pool.domain_narrative
    )
    try:
        canonical = json.dumps(
            payload,
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
    except ValueError as error:
        raise PoolValidationError(
            [f"pool contains a non-finite number that strict JSON cannot encode: {error}"]
        ) from error
    Path(path).write_text(canonical + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- #
# the offline Faker builder
# --------------------------------------------------------------------------- #


def _distinct_identifiers(
    primitive: str | None,
    count: int,
    rng: Random,
    oid: str,
    constraints: list[dict[str, Any]] | None = None,
) -> list[Any]:
    """``count`` DISTINCT identifier values for an entity type.

    When the primitive is unresolvable (unit-based / external reference — the
    resolve-or-skip cases), emit deterministic opaque tokens rather than
    attempting a primitive-typed draw, matching the read-side contract.

    ``spec`` is the ``value`` constraint governing the entity's REFERENCE VALUE
    TYPE (F-01). An entity value in a fact IS its reference-scheme value, so a
    ``value`` constraint on ``movie_id`` governs every ``movie:`` occurrence;
    drawing identifiers outside it produces a pool from which no conforming
    population can be assembled. The read-side (``_denoting_types`` in the
    assembler's universe walk) and this draw are the two halves of the same rule.
    """
    constraints = constraints or []
    enum_values = _enum_identifier_values(constraints)
    if enum_values is not None:
        unique: list[Any] = []
        seen: set[tuple[str, Any]] = set()
        for value in enum_values:
            key = scalar_identity(value)
            if key not in seen:
                seen.add(key)
                unique.append(value)
        if not unique:
            raise PoolValidationError(
                [f"value constraints for '{oid}' have an empty intersection"]
            )
        if len(unique) < count:
            raise PoolValidationError(
                [
                    (
                        f"value enum for '{oid}' supplies only {len(unique)} distinct "
                        f"identifier value(s), but the pool requires {count}; the declared "
                        f"domain cannot satisfy the identifier demand"
                    )
                ]
            )
        return unique[:count]

    if primitive is None:
        if constraints:
            raise PoolValidationError(
                [f"cannot generate constrained identifiers for unresolved type '{oid}'"]
            )
        # Stable, seeded, distinct opaque identifiers.
        out: list[str] = []
        seen: set[str] = set()
        while len(out) < count:
            token = f"{oid}-{rng.getrandbits(32):08x}"
            if token not in seen:
                seen.add(token)
                out.append(token)
        return out

    out_values: list[Any] = []
    seen_keys: set[tuple[str, Any]] = set()
    attempts = 0
    limit = count * 50 + 50
    while len(out_values) < count and attempts < limit:
        try:
            value = draw_value_for_constraints(primitive, rng, constraints)
        except EmptyValueDomain as error:
            raise PoolValidationError([f"value domain for '{oid}' is empty: {error}"]) from error
        attempts += 1
        key = scalar_identity(value)
        if key not in seen_keys:
            seen_keys.add(key)
            out_values.append(value)
    if len(out_values) < count:
        raise PoolValidationError(
            [
                (
                    f"could not draw {count} distinct {primitive} identifiers for "
                    f"'{oid}' — the primitive's value space is too small for the demand"
                )
            ]
        )
    return out_values


def _enum_identifier_values(constraints: list[dict[str, Any]]) -> list[Any] | None:
    """Return the enum intersection for an identifier domain, when declared."""
    enum_constraints = [
        constraint for constraint in constraints if constraint.get("allowed") is not None
    ]
    if not enum_constraints:
        return None
    return [
        value
        for value in enum_constraints[0]["allowed"]
        if value_satisfies_all(value, constraints)
    ]


def _value_samples(
    primitive: str, count: int, rng: Random, constraints: list[dict[str, Any]]
) -> list[Any]:
    """``count`` sample values for a value type, honouring any value constraint.

    Distinctness is not forced for samples (the demand baseline of 1 is met by any
    non-empty list); an enum with fewer members than ``count`` simply repeats.
    """
    try:
        return [
            draw_value_for_constraints(primitive, rng, constraints)
            for _ in range(count)
        ]
    except EmptyValueDomain as error:
        raise PoolValidationError(
            [f"value domain for primitive {primitive!r} is empty: {error}"]
        ) from error


def build_faker_pool(
    model: Model, rng: int | Random, *, size_per_type: int = 8
) -> Pool:
    """Draw a Faker-backed pool that passes ``load_pool`` for ``model`` by
    construction.

    ``rng`` may be an int seed (recorded as ``provenance.rng_seed`` and used to
    build a :class:`random.Random`) or a Random instance (no seed recorded).
    Every list is sized to satisfy the same coherence demands ``load_pool``
    checks, and every value is drawn through :func:`values.make_value`, so the
    builder and the validator agree on validity by sharing one dispatch.
    """
    seed: int | None = None
    if isinstance(rng, int):
        seed = rng
        rng = Random(rng)

    value_constraints = _object_scope_value_constraints(model)
    demand = _distinctness_demand(model)

    object_types: dict[str, list[Any]] = {}
    value_types: dict[str, list[Any]] = {}

    for object_type in model.object_types or []:
        oid = str(object_type.get("id"))
        kind = object_type.get("kind")
        model_demand = max(1, demand.get(oid, (1, ""))[0])
        needed = max(size_per_type, model_demand)
        primitive = popvalidate.resolve_primitive(oid, model)
        if kind == "entity":
            # F-01: the entity's identifiers ARE values of its reference value
            # type, so a `value` constraint on that type governs them.
            reference_value_type = popvalidate.resolve_reference_value_type(oid, model)
            constraints = (
                value_constraints.get(str(reference_value_type), [])
                if reference_value_type
                else []
            )
            enum_values = _enum_identifier_values(constraints)
            if enum_values is not None:
                # ``size_per_type`` is a diversity target, not a model demand.
                # A finite enum may cap it, but may never cap the minimum number
                # of distinct identifiers required by model constraints.
                enum_capacity = _distinct_count(enum_values)
                needed = (
                    model_demand
                    if enum_capacity < model_demand
                    else min(needed, enum_capacity)
                )
            object_types[oid] = _distinct_identifiers(
                primitive,
                needed,
                rng,
                oid,
                constraints,
            )
        else:
            # A value-kind object type always carries a primitive.
            primitive_name = str(primitive) if primitive else str(object_type.get("primitive"))
            value_types[oid] = _value_samples(
                primitive_name, needed, rng, value_constraints.get(oid, [])
            )

    provenance: dict[str, Any] = {"source": "faker"}
    if seed is not None:
        provenance["rng_seed"] = seed
    if model.model_id:
        provenance["model_id"] = str(model.model_id)

    payload = _payload_of(object_types, value_types, provenance, None)
    coherence_failures = _coherence_failures(payload, model)
    if coherence_failures:
        raise PoolValidationError(coherence_failures)
    return Pool(
        object_types=object_types,
        value_types=value_types,
        provenance=provenance,
        sha256=_sha256(payload),
        domain_narrative=None,
    )
