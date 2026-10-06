"""Internal v6 snapshot correspondence coverage and assurance decisions.

This module deliberately does not read files or import repository proof tools.
The repository-only publisher authenticates bytes first and constructs
:class:`CorrespondenceEvidence`; the pure walk below then validates the closed
registry/currency relation before certification.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from gnd import semantic_spec
from gnd.artifacts import is_sha256_hex
from gnd.assurance._wire import (
    CorrespondenceDigests as CorrespondenceDigests,  # noqa: PLC0414 -- compatibility surface
)
from gnd.correspondence import AdaptedSnapshot, SnapshotDecision
from gnd.semantic_registry import REGISTRY, Branch, is_registered, record_branch

SemanticDecision = Literal["accept", "refuse", "indeterminate"]
AssuranceLevel = Literal["proof-backed", "partial", "none"]
ExtractionRoute = Literal["authenticated", "skipped"]

PHASE2_TRUST_ASSUMPTIONS = (
    "phase2-ast-recognizer",
    "phase2-emitter",
    "phase2-theory-mapping",
    "phase2-isabelle-kernel",
    "phase2-nagini-viper-silicon",
    "phase2-runtime-tests",
    "phase2-frozen-expected-answers",
)




@dataclass(frozen=True, slots=True, init=False)
class CorrespondenceEvidence:
    """Authenticated evidence capability produced only by the repository reader."""

    covered_scope_ids: tuple[str, ...]
    declared_scope_ids: tuple[str, ...]
    digests: CorrespondenceDigests
    assumptions: tuple[str, ...] = ()
    authenticated: bool = False

    def __init__(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("CorrespondenceEvidence requires the authenticated evidence loader")

    @classmethod
    def _from_authenticated(
        cls,
        covered_scope_ids: tuple[str, ...],
        declared_scope_ids: tuple[str, ...],
        digests: CorrespondenceDigests,
        assumptions: tuple[str, ...],
    ) -> CorrespondenceEvidence:
        value = object.__new__(cls)
        object.__setattr__(value, "covered_scope_ids", covered_scope_ids)
        object.__setattr__(value, "declared_scope_ids", declared_scope_ids)
        object.__setattr__(value, "digests", digests)
        object.__setattr__(value, "assumptions", assumptions)
        object.__setattr__(value, "authenticated", True)
        return value


@dataclass(frozen=True, slots=True)
class ValidatedScopeWalk:
    applicable_scope_ids: tuple[str, ...]
    current_covered_scope_ids: tuple[str, ...]
    digests: CorrespondenceDigests
    assumptions: tuple[str, ...]
    admitted: bool
    currency_valid: bool


@dataclass(frozen=True, slots=True)
class AssuranceBlock:
    semantic_decision: SemanticDecision
    assurance_level: AssuranceLevel
    scope_digest: str
    semantics_digest: str
    production_roster_digest: str
    proof_digest: str
    toolchain_digest: str
    uncovered_applicable_scope_ids: tuple[str, ...]
    assumptions: tuple[str, ...]


def _unique_sorted(values: tuple[str, ...]) -> tuple[str, ...]:
    result = tuple(sorted(set(values)))
    if len(result) != len(values):
        raise ValueError("scope IDs must be unique")
    return result


def _sorted_set(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted(set(values)))


def _currency_valid(evidence: CorrespondenceEvidence) -> bool:
    return evidence.authenticated


def _phase3_target(row: Branch) -> bool:
    # This denominator is the published v6.0 Phase 3 roster, not a live census.
    # Phase 4 aggregate branches remain registered but cannot enlarge its proof.
    if row.reason_code == "derived-unknown" or ":aggregate:" in row.scope_id:
        return False
    # Phase 6 existential consequents likewise stay outside the frozen denominator.
    if row.surface == "snapshot" and row.family == "guarded" and row.variant == "exists":
        return False
    if (
        row.reason_code
        in {
            "term:mod-zero",
            "term:exact-value-too-wide",
            "term:dependency-unavailable",
            "term:div-zero",
            "term:sqrt-negative",
            "term:haversine-coordinate-range",
            "term:float-overflow",
        }
        or row.scope_id == "snapshot:guarded:comparison:exact-success"
    ):
        return False
    if row.family == "assurance" and row.variant in {"snapshot", "transition", "derivation"}:
        return False
    if row.surface in {"snapshot", "applicability", "certification"}:
        return True
    if row.surface == "composition":
        return row.variant != "transition" and row.family not in {
            "oracle-verdict",
            "derivation-view",
            "dynamic-refresh",
        }
    if row.surface == "report":
        return row.family == "check" and row.scope_id != "report:check:n-a:derivation-row"
    if row.surface == "experiment-feedback":
        return row.scope_id in {
            "experiment-feedback:projection:constraint-satisfaction:repair-details",
            "experiment-feedback:projection:n-a:current-v2",
        }
    return False


def phase3_scope_ids() -> tuple[str, ...]:
    """The owner-approved 230-row correspondence denominator."""
    return tuple(sorted(row.scope_id for row in REGISTRY if _phase3_target(row)))


def walk_snapshot_scope(
    adapted: AdaptedSnapshot,
    decision: SnapshotDecision,
    evidence: CorrespondenceEvidence,
) -> ValidatedScopeWalk:
    """Validate exact applicable/current sets; reject forged registry rows."""
    declared = _unique_sorted(evidence.declared_scope_ids)
    covered = _unique_sorted(evidence.covered_scope_ids)
    if any(not is_registered(scope_id) for scope_id in (*declared, *covered)):
        raise ValueError("evidence names an unregistered scope ID")
    if not set(covered) <= set(declared):
        raise ValueError("covered scope IDs are not a subset of the declaration")
    expected_declaration = phase3_scope_ids()
    if declared != expected_declaration:
        missing = sorted(set(expected_declaration) - set(declared))
        extra = sorted(set(declared) - set(expected_declaration))
        raise ValueError(f"Phase 3 declaration mismatch: missing={missing}, extra={extra}")

    finding_ids = {
        scope_id for finding in decision.findings for scope_id in finding.applicable_scope_ids
    }
    applicable = _sorted_set(
        tuple(
            {
                *(
                    scope_id
                    for scope_id in adapted.observation.applicable_scope_ids
                    if scope_id in set(expected_declaration)
                ),
                *finding_ids,
            }
        )
    )
    if not finding_ids <= set(applicable):
        raise ValueError("an executed finding is absent from the applicable scope walk")
    if any(scope_id not in declared for scope_id in applicable):
        raise ValueError("the evidence declaration omits an applicable scope ID")
    current = tuple(scope_id for scope_id in applicable if scope_id in set(covered))
    assumptions = _unique_sorted(evidence.assumptions)
    assumptions_complete = set(PHASE2_TRUST_ASSUMPTIONS) <= set(assumptions)
    return ValidatedScopeWalk(
        applicable_scope_ids=applicable,
        current_covered_scope_ids=current,
        digests=evidence.digests,
        assumptions=assumptions,
        admitted=not adapted.observation.refusals,
        currency_valid=_currency_valid(evidence) and assumptions_complete,
    )


def certify_snapshot(
    decision: SnapshotDecision,
    *,
    scope: ValidatedScopeWalk,
    extraction_route: ExtractionRoute,
) -> AssuranceBlock:
    """Compute internal assurance by delegating to the proved policy helpers."""
    semantic_decision = semantic_spec.decision_of(decision.band)
    if semantic_decision not in {"accept", "refuse", "indeterminate"}:
        raise ValueError("snapshot band has no semantic decision")
    level = semantic_spec.assurance_for_route(
        len(scope.applicable_scope_ids),
        len(scope.current_covered_scope_ids),
        True,
        scope.admitted,
        scope.currency_valid,
        True,
        extraction_route == "authenticated",
    )
    if level not in {"proof-backed", "partial", "none"}:
        raise ValueError("semantic assurance helper returned an unknown level")
    record_branch(f"certification:decision:phase1:{semantic_decision}")
    record_branch(f"certification:assurance:phase1:{level}")
    uncovered = tuple(
        scope_id
        for scope_id in scope.applicable_scope_ids
        if scope_id not in set(scope.current_covered_scope_ids)
    )
    digests = scope.digests
    return AssuranceBlock(
        semantic_decision=semantic_decision,
        assurance_level=level,
        scope_digest=digests.scope_digest,
        semantics_digest=digests.semantics_digest,
        production_roster_digest=digests.production_roster_digest,
        proof_digest=digests.proof_digest,
        toolchain_digest=digests.toolchain_digest,
        uncovered_applicable_scope_ids=uncovered,
        assumptions=scope.assumptions,
    )


# Phase 6's result policy excludes its own infrastructure from A and C. These
# pure kernels do not mint an authenticated execution or evidence capability.
AssuranceSurface = Literal["snapshot", "transition", "derivation"]
AssuranceConsumer = Literal["report", "feedback"]


def assurance_prerequisites(
    surface: AssuranceSurface,
    consumer: AssuranceConsumer,
) -> tuple[str, ...]:
    """Derive every prerequisite before choosing an assurance outcome."""
    if surface not in ("snapshot", "transition", "derivation"):
        raise ValueError("unknown assurance surface")
    if consumer not in ("report", "feedback"):
        raise ValueError("unknown assurance consumer")
    required = [
        f"applicability:assurance:{surface}:derived",
        *(
            f"certification:assurance:{surface}:{level}"
            for level in ("none", "partial", "proof-backed")
        ),
        f"report:assurance:{surface}:projected",
    ]
    if consumer == "feedback":
        required.append(f"experiment-feedback:assurance:{surface}:projected")
    return tuple(sorted(required))


def _assurance_outcome(applicable: int, covered: int, guards_valid: bool) -> AssuranceLevel:
    """The scalar refinement of the finite-set rule; no coverage inference."""
    if not guards_valid or applicable <= 0 or covered <= 0 or covered > applicable:
        return "none"
    if covered == applicable:
        return "proof-backed"
    return "partial"


def _assurance_policy(
    applicable: frozenset[str],
    covered: frozenset[str],
    *,
    required: frozenset[str],
    proved_infrastructure: frozenset[str],
    guards_valid: bool,
) -> AssuranceLevel:
    """Check the finite-set premises before invoking the scalar refinement."""
    valid = (
        guards_valid
        and covered <= applicable
        and required <= proved_infrastructure
        and not (applicable & required)
        and not (applicable & proved_infrastructure)
    )
    return _assurance_outcome(len(applicable), len(covered), valid)


@dataclass(frozen=True, slots=True)
class AssuranceBlockV1:
    """Wire projection; only certification may confer evidence authority.

    Deserializing or constructing this value never authenticates an execution.
    Readers must not use it as an evidence or execution capability.
    """

    semantic_decision: SemanticDecision | None
    assurance_level: AssuranceLevel = "none"
    scope_digest: str | None = None
    semantics_digest: str | None = None
    production_roster_digest: str | None = None
    proof_digest: str | None = None
    toolchain_digest: str | None = None
    uncovered_applicable_scope_ids: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.semantic_decision not in {None, "accept", "refuse", "indeterminate"}:
            raise ValueError("unknown semantic decision")
        if self.assurance_level not in {"none", "partial", "proof-backed"}:
            raise ValueError("unknown assurance level")
        identities = (
            self.scope_digest,
            self.semantics_digest,
            self.production_roster_digest,
            self.proof_digest,
            self.toolchain_digest,
        )
        for value in identities:
            if value is not None and not is_sha256_hex(value):
                raise ValueError("invalid assurance identity")
        if self.assurance_level != "none" and (
            self.semantic_decision is None or any(value is None for value in identities)
        ):
            raise ValueError("positive assurance requires a semantic result and all identities")
        if self.assurance_level == "proof-backed" and self.uncovered_applicable_scope_ids:
            raise ValueError("proof-backed assurance cannot have uncovered obligations")
        for values in (self.uncovered_applicable_scope_ids, self.assumptions):
            if not isinstance(values, tuple) or any(not isinstance(v, str) for v in values):
                raise ValueError("assurance arrays must be immutable strings")
            if tuple(sorted(set(values))) != values:
                raise ValueError("assurance arrays must be sorted and unique")

    def as_dict(self) -> dict[str, object]:
        from dataclasses import asdict

        result = {"schema_version": 1, **asdict(self)}
        result["uncovered_applicable_scope_ids"] = list(self.uncovered_applicable_scope_ids)
        result["assumptions"] = list(self.assumptions)
        return result


def semantic_decision_for_band(band: int) -> SemanticDecision | None:
    if band == 0:
        return "accept"
    if band == 1:
        return "refuse"
    if band in (2, 4):
        return "indeterminate"
    if band in (3, 70):
        return None
    raise ValueError("band has no report envelope")


@dataclass(frozen=True, slots=True, init=False)
class AuthenticatedExecution:
    identity: str
    production_roster_digest: str | None
    surface: AssuranceSurface
    band: int
    input_scope_ids: frozenset[str]
    trace: frozenset[str]
    complete: bool
    extraction_route: str

    def __init__(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("execution requires the live evaluation boundary")


@dataclass(frozen=True, slots=True, init=False)
class AssuranceScope:
    execution_identity: str
    production_roster_digest: str | None
    surface: AssuranceSurface
    consumer: AssuranceConsumer
    applicable_scope_ids: frozenset[str]
    required_infrastructure_ids: frozenset[str]
    valid: bool

    def __init__(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("scope requires derive_assurance_scope")


def _internal_value(cls, **fields):
    value = object.__new__(cls)
    for key, item in fields.items():
        object.__setattr__(value, key, item)
    return value


def _mint_execution(
    model, populations, result, band, trace, *, steps=None, extraction_route="not-applicable"
):
    """Called at live CLI evaluation boundaries, never by a JSON reader.

    Keep complete immutable input/result identities; do not retain the mutable
    report as the capability. Application code inside this process is trusted.
    """
    import hashlib

    from gnd import artifacts, checker, transition
    from gnd.assurance._wire import production_identity
    from gnd.model import structured_derivation_ids

    snapshots = result.embedded_reports() if steps is not None else [result]
    expected = {row.scope_id for report in snapshots for row in report.verdicts}
    expected.update(row.scope_id for report in snapshots for row in report.derivations)
    if steps is not None:
        expected.update(row.scope_id for row in result.all_verdicts())
    expected.discard(None)
    if steps is not None:
        expected.update({"report:check:n-a:envelope-only", "report:transition:n-a:evaluated"})
        actual_band = transition.band(result)
        expected.add(
            "composition:band:transition:"
            + {0: "clean", 1: "fail", 2: "vacuous", 4: "unchecked"}[actual_band]
        )
    else:
        variant = "phase1" if result.phase1_trace is not None else "n-a"
        expected.update(
            f"report:check:{variant}:{name}" for name in ("counts", "verdict-row", "coverage")
        )
        actual_band = checker.band(result)
        expected.add(
            "composition:band:n-a:"
            + {0: "clean", 1: "alethic-fail", 2: "vacuous", 4: "alethic-unchecked"}[actual_band]
        )
    input_scope = frozenset(
        scope_id for report in snapshots for scope_id in report.assurance_input_scope_ids
    )
    surface = (
        "transition"
        if steps is not None
        else "derivation"
        if structured_derivation_ids(model)
        else "snapshot"
    )
    complete = (
        bool(snapshots)
        and band == actual_band
        and all(pop.matches_validation_marker(model) for pop in populations)
        and all(report.snapshot_projection is not None for report in snapshots)
        and bool(input_scope)
        and expected <= set(trace)
        and all(is_registered(scope_id) for scope_id in trace)
        and extraction_route in {"not-applicable", "authenticated", "skipped"}
    )
    try:
        producer = production_identity()
    except (OSError, ValueError):
        producer = None
    identity = {
        "production_roster_digest": producer,
        "model": transition.transition_model_identity(model),
        "populations": [pop.model_dump(mode="json") for pop in populations],
        "steps": steps,
        "result": result.model_dump(mode="json"),
        "snapshots": [
            {
                "report": report.model_dump(mode="json"),
                "derivations": [row.model_dump(mode="json") for row in report.derivations],
                "scope": list(report.assurance_input_scope_ids),
            }
            for report in snapshots
        ],
        "band": band,
        "trace": sorted(trace),
        "extraction_route": extraction_route,
    }
    return _internal_value(
        AuthenticatedExecution,
        identity=hashlib.sha256(artifacts.canonical_json_bytes(identity)).hexdigest(),
        surface=surface,
        production_roster_digest=producer,
        band=band,
        input_scope_ids=input_scope,
        trace=frozenset(trace),
        complete=complete,
        extraction_route=extraction_route,
    )


def _result_obligation(row: Branch, surface: AssuranceSurface, consumer: AssuranceConsumer) -> bool:
    # Phase 4 branches have no certificate in the historical evidence roster.
    # Keep that prior roster's applicable set stable for opaque-free reports.
    if row.reason_code == "derived-unknown" or row.scope_id.endswith(":unresolved"):
        return False
    if row.family in {"assurance", "oracle-verdict"} or row.surface == "certification":
        return False
    if row.surface == "experiment-feedback":
        return consumer == "feedback" and row.family in {"projection", "verifier-derivation"}
    if (
        row.surface == "transition"
        or row.variant == "transition"
        or (row.surface == "report" and row.family == "transition")
    ):
        return surface == "transition"
    if row.surface == "derivation" or row.semantic_branch == "derivation-row":
        return surface in {"transition", "derivation"}
    return True


def derive_assurance_scope(
    execution: AuthenticatedExecution, *, consumer: AssuranceConsumer
) -> AssuranceScope:
    if type(execution) is not AuthenticatedExecution:
        raise TypeError("scope requires an authenticated execution")
    required = frozenset(assurance_prerequisites(execution.surface, consumer))
    applicable = frozenset(
        row.scope_id
        for row in REGISTRY
        if (
            row.scope_id in execution.input_scope_ids
            and _result_obligation(row, execution.surface, consumer)
        )
    )
    # A trace event must be either an input obligation or a declared consumer /
    # infrastructure event. Unknown and unexplained events invalidate the walk.
    explained = applicable | required
    valid = execution.complete and execution.trace <= explained
    record_branch(f"applicability:assurance:{execution.surface}:derived")
    return _internal_value(
        AssuranceScope,
        execution_identity=execution.identity,
        production_roster_digest=execution.production_roster_digest,
        surface=execution.surface,
        consumer=consumer,
        applicable_scope_ids=applicable,
        required_infrastructure_ids=required,
        valid=valid,
    )


def certify_result(
    execution: AuthenticatedExecution, *, scope: AssuranceScope, evidence
) -> AssuranceBlockV1:
    from gnd.assurance._wire import AuthenticatedAssuranceEvidence

    if type(execution) is not AuthenticatedExecution or type(scope) is not AssuranceScope:
        raise TypeError("certification requires execution and scope capabilities")
    if type(evidence) is not AuthenticatedAssuranceEvidence:
        raise TypeError("certification requires release evidence")
    same = scope.execution_identity == execution.identity and scope.surface == execution.surface
    available = (
        evidence.available
        and evidence.digests is not None
        and execution.production_roster_digest is not None
        and evidence.digests.production_roster_digest == execution.production_roster_digest
    )
    covered = scope.applicable_scope_ids & evidence.covered_scope_ids if available else frozenset()
    infrastructure = frozenset(row.scope_id for row in REGISTRY if row.family == "assurance")
    proved_infrastructure = (
        evidence.covered_scope_ids & infrastructure if available else frozenset()
    )
    level = _assurance_policy(
        scope.applicable_scope_ids,
        covered,
        required=scope.required_infrastructure_ids,
        proved_infrastructure=proved_infrastructure,
        guards_valid=(
            same and scope.valid and available and execution.extraction_route != "skipped"
        ),
    )
    decision = semantic_decision_for_band(execution.band)
    if decision is None:
        level = "none"
    record_branch(f"certification:assurance:{execution.surface}:{level}")
    identities = evidence.digests if available else None
    return AssuranceBlockV1(
        semantic_decision=decision,
        assurance_level=level,
        scope_digest=identities.scope_digest if identities else None,
        semantics_digest=identities.semantics_digest if identities else None,
        production_roster_digest=identities.production_roster_digest if identities else None,
        proof_digest=identities.proof_digest if identities else None,
        toolchain_digest=identities.toolchain_digest if identities else None,
        uncovered_applicable_scope_ids=tuple(sorted(scope.applicable_scope_ids - covered)),
        assumptions=evidence.assumptions if available else (),
    )


CorrespondenceEvidence.__module__ = 'gnd.assurance'
ValidatedScopeWalk.__module__ = 'gnd.assurance'
AssuranceBlock.__module__ = 'gnd.assurance'
_unique_sorted.__module__ = 'gnd.assurance'
_sorted_set.__module__ = 'gnd.assurance'
_currency_valid.__module__ = 'gnd.assurance'
_phase3_target.__module__ = 'gnd.assurance'
phase3_scope_ids.__module__ = 'gnd.assurance'
walk_snapshot_scope.__module__ = 'gnd.assurance'
certify_snapshot.__module__ = 'gnd.assurance'
assurance_prerequisites.__module__ = 'gnd.assurance'
_assurance_outcome.__module__ = 'gnd.assurance'
_assurance_policy.__module__ = 'gnd.assurance'
AssuranceBlockV1.__module__ = 'gnd.assurance'
semantic_decision_for_band.__module__ = 'gnd.assurance'
AuthenticatedExecution.__module__ = 'gnd.assurance'
AssuranceScope.__module__ = 'gnd.assurance'
_internal_value.__module__ = 'gnd.assurance'
_mint_execution.__module__ = 'gnd.assurance'
_result_obligation.__module__ = 'gnd.assurance'
derive_assurance_scope.__module__ = 'gnd.assurance'
certify_result.__module__ = 'gnd.assurance'

# Public dependency and compatibility spellings; same predecessor objects.
assurance_outcome = _assurance_outcome
assurance_policy = _assurance_policy
currency_valid = _currency_valid
internal_value = _internal_value
mint_execution = _mint_execution
phase3_target = _phase3_target
result_obligation = _result_obligation
sorted_set = _sorted_set
unique_sorted = _unique_sorted
