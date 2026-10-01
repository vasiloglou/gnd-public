"""Production branch identities; no proof claim follows from registration.

This source-owned inventory describes decision branches, including branches whose
semantics are not formalized yet. It never reads a proof declaration or corpus.
Tracing is optional, context-local, and absent from public report serialization.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import TYPE_CHECKING

from gnd.semantic_ir import ADAPTER_REFUSALS

if TYPE_CHECKING:
    from gnd.model import Model
    from gnd.population import Population

SURFACES = (
    "snapshot",
    "applicability",
    "composition",
    "derivation",
    "transition",
    "report",
    "experiment-feedback",
    "certification",
)
OBLIGATION_KINDS = (
    "verdict",
    "applicability",
    "composition",
    "projection",
    "decision",
    "refusal",
    "execution",
)
OUTCOMES = (
    "pass",
    "fail",
    "warning",
    "unchecked",
    "vacuous",
    "refused",
    "projected",
    "accept",
    "refuse",
    "indeterminate",
    "proof-backed",
    "partial",
    "none",
    "applied",
    "filtered",
)
WITNESS_KINDS = ("none", "scalars", "tuples", "fact-rows", "bindings", "cycle", "derivation-row")
IR_DIMENSIONS = (
    "identity",
    "order",
    "role-order",
    "multiplicity",
    "primitive",
    "covers",
    "declared",
    "instances",
    "subtype-closure",
    "reference-widening",
    "modality",
    "bound",
    "operator",
    "literal",
    "variant",
    "consequent",
    "derivation-kind",
    "dependency-graph",
)


@dataclass(frozen=True)
class Branch:
    scope_id: str
    surface: str
    obligation_kind: str
    family: str
    variant: str
    arity: str
    modality: str
    semantic_branch: str
    outcome: str
    witness_kind: str
    reason_code: str | None
    applicability_inputs: tuple[str, ...]
    production_owner: str


class UnregisteredBranchError(LookupError):
    """An internal decision has no matching production branch contract."""


# A descriptor is (family, variants, arity, violating witness, owner, inputs).
# Variants follow the evaluator's input selectors, not the fixture labels.
_UNIVERSE = ("identity", "instances", "subtype-closure", "reference-widening")
_SNAPSHOT = (
    (
        "uniqueness",
        ("inline",),
        "sequence",
        "fact-rows",
        "_check_uniqueness",
        ("identity", "role-order", "multiplicity"),
    ),
    (
        "uniqueness",
        ("external",),
        "joined",
        "tuples",
        "_check_uniqueness_external",
        ("identity", "role-order", "multiplicity"),
    ),
    ("mandatory", ("inline",), "unary", "scalars", "_check_mandatory", _UNIVERSE),
    (
        "mandatory-disjunctive",
        ("n-a",),
        "sequence",
        "scalars",
        "_check_mandatory_disjunctive",
        _UNIVERSE,
    ),
    (
        "value",
        ("enum", "enum-role"),
        "unary",
        "scalars",
        "_check_value",
        (*_UNIVERSE, "multiplicity", "literal"),
    ),
    (
        "value",
        ("range", "range-role", "ranges", "ranges-role"),
        "unary",
        "scalars",
        "_check_value",
        (*_UNIVERSE, "multiplicity", "primitive", "order", "bound"),
    ),
    (
        "frequency",
        ("internal",),
        "sequence",
        "tuples",
        "_check_frequency",
        ("identity", "role-order", "multiplicity", "bound"),
    ),
    (
        "frequency",
        ("external",),
        "joined",
        "tuples",
        "_check_frequency",
        ("identity", "role-order", "multiplicity", "bound"),
    ),
    (
        "ring",
        (
            "irreflexive",
            "asymmetric",
            "intransitive",
            "antisymmetric",
            "acyclic",
            "symmetric",
            "purely-reflexive",
            "reflexive",
            "transitive",
            "acyclic-intransitive",
            "asymmetric-intransitive",
            "symmetric-intransitive",
            "symmetric-irreflexive",
        ),
        "binary",
        "tuples",
        "_check_ring",
        ("identity", "role-order", "variant"),
    ),
    *(
        (
            family,
            ("single", "joined"),
            "sequence",
            "tuples",
            "_check_set_comparison",
            ("identity", "role-order"),
        )
        for family in ("subset", "equality", "exclusion")
    ),
    ("exclusive-or", ("single-role",), "sequence", "scalars", "_check_exclusive_or", _UNIVERSE),
    (
        "exclusive-or",
        ("multi-role",),
        "sequence",
        "tuples",
        "_check_exclusive_or",
        ("identity", "role-order"),
    ),
    (
        "value-comparison",
        ("inline", "inline-literal", "cross-same", "cross-joined"),
        "binary",
        "tuples",
        "_check_value_comparison",
        ("identity", "primitive", "order", "operator", "literal", "role-order"),
    ),
    (
        "cardinality",
        ("object", "role"),
        "unary",
        "scalars",
        "_check_cardinality",
        (*_UNIVERSE, "bound"),
    ),
    (
        "subtype-partition",
        ("exclusive", "exhaustive", "both"),
        "n-ary",
        "scalars",
        "_check_subtype_partition",
        (*_UNIVERSE, "variant", "derivation-kind"),
    ),
    (
        "guarded",
        ("comparison", "atom", "absence", "exists"),
        "joined",
        "bindings",
        "_check_guarded",
        ("identity", "role-order", "primitive", "order", "operator", "literal", "consequent"),
    ),
)


def _row(
    surface: str,
    family: str,
    variant: str,
    event: str,
    outcome: str,
    *,
    owner: str,
    kind: str = "verdict",
    arity: str = "n/a",
    modality: str = "any",
    witness: str = "none",
    reason: str | None = None,
    inputs: tuple[str, ...] = (),
) -> Branch:
    suffix = f":{modality}" if event == "violated" else ""
    return Branch(
        f"{surface}:{family}:{variant}:{event}{suffix}",
        surface,
        kind,
        family,
        variant,
        arity,
        modality,
        event,
        outcome,
        witness,
        reason,
        inputs,
        owner,
    )


def _snapshot_rows() -> Iterator[Branch]:
    for variant in ("role", "all"):
        for event, outcome, reason, modality in (
            ("clean", "pass", None, "any"),
            ("violated", "fail", None, "alethic"),
            ("violated", "warning", None, "deontic"),
            ("sidecar-absent", "unchecked", "anchor-sidecar-absent", "any"),
            ("non-lexical", "unchecked", "anchor-non-lexical", "any"),
            ("vacuous", "vacuous", None, "any"),
        ):
            yield _row("snapshot", "anchored", variant, event, outcome,
                       owner="gnd.checker._anchored_verdict", modality=modality,
                       reason=reason, inputs=("identity", "role-order", "covers"))
        yield _row("snapshot", "anchored", variant, "unchecked-derived-unknown", "unchecked",
                   owner="gnd.checker._partial_constraint_report", reason="derived-unknown",
                   inputs=("identity", "role-order", "covers"))
    exact_unavailable: set[tuple[str, str]] = set()
    for family, variants, arity, witness, owner, inputs in _SNAPSHOT:
        for variant in variants:
            yield _row(
                "snapshot",
                family,
                variant,
                "unchecked-derived-unknown",
                "unchecked",
                owner="gnd.checker._partial_constraint_report",
                arity=arity,
                reason="derived-unknown",
                inputs=inputs,
            )
            actual_witness = "cycle" if family == "ring" and variant == "acyclic" else witness
            if not (family == "exclusive-or" and variant == "multi-role"):
                yield _row(
                    "snapshot",
                    family,
                    variant,
                    "clean",
                    "pass",
                    owner="gnd.correspondence.evaluate_snapshot",
                    arity=arity,
                    inputs=inputs,
                )
            for modality, outcome in (("alethic", "fail"), ("deontic", "warning")):
                yield _row(
                    "snapshot",
                    family,
                    variant,
                    "violated",
                    outcome,
                    owner="gnd.correspondence.evaluate_snapshot",
                    arity=arity,
                    witness=actual_witness,
                    modality=modality,
                    inputs=(*inputs, "modality"),
                )
            if (family, variant) not in exact_unavailable:
                exact_unavailable.add((family, variant))
                for event, reason in (
                    ("unchecked-mod-zero", "term:mod-zero"),
                    ("unchecked-exact-value-too-wide", "term:exact-value-too-wide"),
                    ("unchecked-dependency-unavailable", "term:dependency-unavailable"),
                    ("unchecked-div-zero", "term:div-zero"),
                    ("unchecked-sqrt-negative", "term:sqrt-negative"),
                    ("unchecked-haversine-coordinate-range", "term:haversine-coordinate-range"),
                    ("unchecked-float-overflow", "term:float-overflow"),
                    *(
                        (
                            ("unchecked-date-out-of-range", "term:date-out-of-range"),
                            ("unchecked-opaque-date-operand", "term:opaque-date-operand"),
                            ("unchecked-temporal-work-limit", "term:temporal-work-limit"),
                        )
                        if family == "guarded" and variant == "comparison"
                        else ()
                    ),
                ):
                    yield _row(
                        "snapshot",
                        family,
                        variant,
                        event,
                        "unchecked",
                        owner=(
                            "gnd.temporal_guarded.evaluate_temporal_guard"
                            if reason
                            in {
                                "term:date-out-of-range",
                                "term:opaque-date-operand",
                                "term:temporal-work-limit",
                            }
                            else "gnd.checker._check_dispatch"
                        ),
                        arity=arity,
                        modality="any",
                        reason=reason,
                        inputs=(*inputs, "dependency-graph"),
                    )

    yield _row(
        "snapshot",
        "guarded",
        "comparison",
        "exact-success",
        "pass",
        owner="gnd.checker._guarded_term_failure",
        inputs=("antecedent-atoms", "exact-term"),
    )
    yield _row(
        "snapshot",
        "guarded",
        "exists",
        "exact-success",
        "pass",
        owner="gnd.correspondence._indexed_guarded_exists_verdict",
        inputs=("antecedent-atoms", "exists-atoms", "exact-term"),
    )
    yield _row(
        "snapshot",
        "guarded",
        "exists",
        "clean-zero-bindings",
        "pass",
        owner="gnd.correspondence.evaluate_snapshot",
        inputs=("identity", "role-order"),
    )
    for event, reason in (
        ("unchecked-guarded-exists-coverage-missing", "guarded-exists-coverage-missing"),
        ("unchecked-guarded-exists-work-limit", "guarded-exists-work-limit"),
    ):
        yield _row(
            "snapshot",
            "guarded",
            "exists",
            event,
            "unchecked",
            owner="gnd.correspondence._indexed_guarded_exists_verdict",
            reason=reason,
            witness="none",
            inputs=("covers", "exists-atoms", "work-budget"),
        )
    yield _row(
        "snapshot",
        "guarded",
        "n-a",
        "unchecked-reference-join-work-limit",
        "unchecked",
        owner="gnd.correspondence._indexed_guarded_bindings",
        reason="reference-join-work-limit",
        witness="none",
        inputs=("antecedent-atoms", "work-budget"),
    )
    for event in ("pass", "fail", "unchecked"):
        yield _row(
            "snapshot",
            "guarded",
            "aggregate",
            event,
            event,
            owner="gnd.checker._check_dispatch",
            inputs=("antecedent-atoms", "derivation-kind", "dependency-graph"),
            witness="fact-rows" if event == "fail" else "none",
        )

    refusals = (
        ("mandatory", ("inline",), "role-unresolved", "_check_mandatory"),
        (
            "mandatory-disjunctive",
            ("n-a",),
            "subject-type-ambiguous",
            "_check_mandatory_disjunctive",
        ),
        (
            "value",
            ("range", "range-role", "ranges", "ranges-role"),
            "bound-type-mismatch",
            "_check_value",
        ),
        ("ring", ("n-a",), "ring-not-binary", "_check_ring"),
        ("exclusive-or", ("single-role",), "subject-type-ambiguous", "_check_exclusive_or"),
        ("exclusive-or", ("multi-role",), "xor-disjunctive-undefined", "_check_exclusive_or"),
        (
            "value-comparison",
            ("inline", "inline-literal", "cross-same", "cross-joined"),
            "values-not-comparable",
            "_check_value_comparison",
        ),
        (
            "value-comparison",
            ("inline-literal",),
            "literal-type-ambiguous",
            "_check_value_comparison",
        ),
        (
            "value-comparison",
            ("inline-time-literal",),
            "no-reference-clock",
            "_check_value_comparison",
        ),
        ("subtype-partition", ("n-a",), "partition-asserts-nothing", "_check_subtype_partition"),
        ("subtype-partition", ("n-a",), "subtype-derivation-only", "_check_subtype_partition"),
        ("guarded", ("n-a",), "family-unimplemented", "_check_guarded_structural_refusal"),
        ("guarded", ("comparison",), "literal-type-ambiguous", "_check_guarded"),
        ("guarded", ("comparison",), "values-not-comparable", "_check_guarded"),
        ("textual", ("n-a",), "textual-not-mechanical", "_verdict_for"),
    )
    for family, variants, reason, owner in refusals:
        for variant in variants:
            yield _row(
                "snapshot",
                family,
                variant,
                f"unchecked-{reason}",
                "unchecked",
                owner="gnd.correspondence.evaluate_snapshot",
                reason=reason,
                witness="bindings"
                if family == "guarded" and reason == "values-not-comparable"
                else "none",
                inputs=("variant", "primitive", "role-order"),
            )
    yield _row(
        "snapshot",
        "guarded",
        "n-a",
        "clean-zero-bindings",
        "pass",
        owner="gnd.correspondence.evaluate_snapshot",
        inputs=("identity", "role-order"),
    )

    # The verified execution route must never share a coverage row with the
    # legacy evaluator. These variants identify the kernel projection boundary.
    for family, variant in (("mandatory", "phase1-inline"), ("frequency", "phase1-internal")):
        for event, outcome, modality in (
            ("clean", "pass", "any"),
            ("violated", "fail", "alethic"),
            ("violated", "warning", "deontic"),
            ("vacuous-empty-subject", "vacuous", "any"),
        ):
            yield _row(
                "snapshot",
                family,
                variant,
                event,
                outcome,
                owner="gnd.correspondence.evaluate_snapshot",
                arity="unary",
                modality=modality,
                witness=("scalars" if family == "mandatory" else "tuples")
                if event == "violated"
                else "none",
                inputs=("identity", "covers", "declared", "bound", "modality"),
            )
    yield _row(
        "snapshot",
        "mandatory",
        "phase1-inline",
        "vacuous-coverage-omission",
        "vacuous",
        owner="gnd.correspondence.evaluate_snapshot",
        inputs=("covers", "declared"),
    )
    yield _row(
        "snapshot",
        "textual",
        "phase1",
        "unchecked-textual-not-mechanical",
        "unchecked",
        owner="gnd.correspondence.evaluate_snapshot",
        reason="textual-not-mechanical",
    )


def _applicability_rows() -> Iterator[Branch]:
    for variant, event, inputs in (
        ("n-a", "coverage-omission", ("covers", "declared")),
        ("n-a", "empty-subject-all", ("declared", "multiplicity")),
        ("guarded", "empty-subject-any", ("declared", "multiplicity")),
        *(
            (variant, "no-observable-subjects", _UNIVERSE)
            for variant in ("value", "cardinality-object", "subtype-partition")
        ),
        *(
            (variant, "zero-row-join", ("identity", "role-order"))
            for variant in (
                "uniqueness-external",
                "frequency-external",
                "value-comparison-cross",
                "equality",
                "exclusion",
            )
        ),
    ):
        yield _row(
            "applicability",
            "vacuity",
            variant,
            event,
            "vacuous",
            owner="gnd.correspondence.evaluate_snapshot",
            kind="applicability",
            inputs=inputs,
        )
    for variant, event, reason in (
        ("n-a", "disconnected", "join-disconnected"),
        ("guarded", "disconnected", "join-disconnected"),
        ("n-a", "anchor-ambiguous", "join-anchor-ambiguous"),
    ):
        yield _row(
            "applicability",
            "join",
            variant,
            event,
            "unchecked",
            owner="gnd.correspondence.evaluate_snapshot",
            kind="applicability",
            reason=reason,
            inputs=("identity", "role-order"),
        )
    yield _row(
        "applicability",
        "implemented",
        "n-a",
        "family-unimplemented",
        "unchecked",
        owner="gnd.correspondence.evaluate_snapshot",
        kind="applicability",
        reason="family-unimplemented",
        inputs=("variant",),
    )
    for reason in ("out-of-scope-family", "out-of-scope-cardinality", "evidence-not-current"):
        yield _row(
            "applicability",
            "refusal",
            "n-a",
            reason,
            "refused",
            owner=(
                "gnd.checker._observe_phase1_compatibility"
                if reason != "evidence-not-current"
                else "gnd.proof_currency.record_evidence_not_current"
            ),
            kind="refusal",
            reason=reason,
            inputs=("variant", "identity", "bound", "covers", "declared"),
        )

    for reason in ADAPTER_REFUSALS:
        yield _row(
            "applicability",
            "adapter",
            "n-a",
            reason,
            "refused",
            owner="gnd.semantic_adapter._refusal",
            kind="refusal",
            reason=reason,
            inputs=IR_DIMENSIONS,
        )
    yield _row(
        "applicability",
        "opaque",
        "n-a",
        "opaque-value",
        "unchecked",
        owner="gnd.correspondence.evaluate_snapshot",
        kind="applicability",
        reason="opaque-value",
        inputs=("identity", "role-order", "primitive"),
    )


def _composition_rows() -> Iterator[Branch]:
    yield _row(
        "composition",
        "derivation-view",
        "static",
        "applied",
        "projected",
        owner="gnd.transition._effective_static_state",
        kind="composition",
        inputs=("covers", "declared", "derivation-kind", "dependency-graph"),
    )
    yield _row(
        "composition",
        "derivation-view",
        "dynamic",
        "applied",
        "projected",
        owner="gnd.checker.structured_extension_view",
        kind="composition",
        inputs=("covers", "declared", "derivation-kind", "dependency-graph"),
    )
    yield _row(
        "composition",
        "dynamic-refresh",
        "selected",
        "projected",
        "projected",
        owner="gnd.transition._evaluate_to_state",
        kind="composition",
        inputs=("identity", "derivation-kind", "dependency-graph"),
    )
    yield _row(
        "composition",
        "dynamic-refresh",
        "no-touch",
        "refused",
        "refused",
        owner="gnd.transition._evaluate_to_state",
        kind="refusal",
        inputs=("derivation-kind", "dependency-graph"),
    )
    for variant in ("n-a", "phase1"):
        for event, outcome in (
            ("alethic-fail", "fail"),
            ("alethic-unchecked", "unchecked"),
            ("vacuous", "vacuous"),
            ("clean", "pass"),
            ("fail-over-unchecked-over-vacuous", "fail"),
            ("unchecked-over-vacuous", "unchecked"),
            ("vacuous-over-clean", "vacuous"),
            ("deontic-warning-keeps-band", "projected"),
            ("deontic-unchecked-keeps-band", "projected"),
        ):
            if variant == "phase1" and event == "deontic-unchecked-keeps-band":
                # in_scope admits textual refusal only with alethic modality;
                # mandatory/frequency have no unchecked outcome in that slice.
                continue
            yield _row(
                "composition",
                "band",
                variant,
                event,
                outcome,
                owner="gnd.checker.band",
                kind="composition",
                inputs=("modality",),
            )
    # Promotion composes authored oracle outcomes. Those inputs must not be
    # mistaken for observed snapshot decisions merely because they use the
    # same report carrier to call the band composer.
    for outcome in ("pass", "fail", "warning", "unchecked", "vacuous"):
        yield _row(
            "composition",
            "oracle-verdict",
            "n-a",
            outcome,
            outcome,
            owner="gnd.measure.promote.expected_exit_for",
            kind="composition",
            inputs=("modality",),
        )
        yield _row(
            "composition",
            "verifier-verdict",
            "n-a",
            outcome,
            outcome,
            owner="gnd.exp.session_eval.validate_verifier_payload",
            kind="composition",
            inputs=("modality",),
        )


def _derivation_rows() -> Iterator[Branch]:
    inputs = (
        "identity",
        "role-order",
        "primitive",
        "covers",
        "declared",
        "derivation-kind",
        "dependency-graph",
    )
    for variant in ("derived", "semiderived"):
        for event, outcome in (
            ("aggregate-applied", "applied"),
            ("aggregate-group-absent", "filtered"),
            ("aggregate-post-filter-false", "filtered"),
            ("aggregate-unavailable-origin", "unchecked"),
            ("aggregate-unavailable-propagated", "unchecked"),
        ):
            yield _row(
                "derivation",
                "extension",
                variant,
                event,
                outcome,
                owner="gnd.checker._exact_extension_calculator",
                kind="execution",
                modality="alethic",
                inputs=inputs,
            )
        for event, outcome in (
            ("exact-applied", "applied"),
            ("exact-where-false", "filtered"),
            ("exact-head-computed", "projected"),
            ("exact-origin-propagated", "unchecked"),
        ):
            yield _row(
                "derivation",
                "extension",
                variant,
                event,
                outcome,
                owner="gnd.checker._exact_extension_calculator",
                kind="execution",
                modality="alethic",
                inputs=inputs,
            )
        for event, outcome, reason in (
            ("clean", "pass", None),
            ("violated", "fail", None),
            ("unchecked-not-covered", "unchecked", "derivation-not-covered"),
            ("unchecked-rule-opaque", "unchecked", "derivation-rule-opaque"),
            ("unchecked-opaque-value", "unchecked", "opaque-value"),
            ("unchecked-derived-unknown", "unchecked", "derived-unknown"),
            ("unchecked-mod-zero", "unchecked", "term:mod-zero"),
            (
                "unchecked-exact-value-too-wide",
                "unchecked",
                "term:exact-value-too-wide",
            ),
            (
                "unchecked-dependency-unavailable",
                "unchecked",
                "term:dependency-unavailable",
            ),
            ("unchecked-div-zero", "unchecked", "term:div-zero"),
            ("unchecked-sqrt-negative", "unchecked", "term:sqrt-negative"),
            (
                "unchecked-haversine-coordinate-range",
                "unchecked",
                "term:haversine-coordinate-range",
            ),
            ("unchecked-float-overflow", "unchecked", "term:float-overflow"),
        ):
            yield _row(
                "derivation",
                "extension",
                variant,
                event,
                outcome,
                owner=(
                    "gnd.checker._exact_derivation_obligation"
                    if reason is not None and reason.startswith("term:")
                    else "gnd.checker._derivation_obligation"
                ),
                modality="alethic",
                reason=reason,
                inputs=inputs,
                witness="derivation-row" if event == "violated" else "none",
            )
        findings = ("incomplete", "unsound", "unresolved") if variant == "derived" else ("incomplete", "unresolved")
        for finding in findings:
            yield _row(
                "derivation",
                "finding",
                variant,
                finding,
                "fail",
                owner="gnd.checker._derivation_obligation",
                modality="alethic",
                inputs=inputs,
                witness="derivation-row",
            )


def _transition_rows() -> Iterator[Branch]:
    # (family, variant, event, outcome, modality, owner, reason, witness)
    rows = [
        ("precondition", "n-a", "clean", "pass", "any", "_evaluate_step", None, "none"),
        ("create-freshness", "n-a", "clean", "pass", "any", "_evaluate_step", None, "none"),
        ("retract-target", "n-a", "clean", "pass", "any", "_evaluate_step", None, "none"),
        ("assert-redundant", "n-a", "clean", "pass", "any", "_evaluate_step", None, "none"),
        ("assert-effect", "n-a", "inserted", "projected", "any", "_evaluate_step", None, "none"),
        (
            "assert-effect",
            "n-a",
            "duplicate-collapsed",
            "projected",
            "any",
            "_evaluate_step",
            None,
            "none",
        ),
        ("dynamic-rule", "n-a", "untouched", "refused", "any", "_evaluate_step", None, "none"),
        (
            "dynamic-rule",
            "n-a",
            "unchecked-nonfunctional",
            "unchecked",
            "any",
            "_evaluate_step",
            "transition:dynamic-subject-not-functional",
            "none",
        ),
        ("dynamic-rule", "no-old", "vacuous", "vacuous", "any", "_evaluate_step", None, "none"),
        ("dynamic-rule", "no-new", "vacuous", "vacuous", "any", "_evaluate_step", None, "none"),
        ("dynamic-rule", "comparison", "clean", "pass", "any", "_evaluate_step", None, "none"),
        (
            "intermediate-unloadable",
            "n-a",
            "unchecked",
            "unchecked",
            "alethic",
            "_load_intermediate",
            "transition:intermediate-state-unloadable",
            "none",
        ),
        (
            "intermediate-state",
            "n-a",
            "loaded",
            "projected",
            "any",
            "_load_intermediate",
            None,
            "none",
        ),
        (
            "compiled-subset",
            "n-a",
            "uncompiled",
            "refused",
            "any",
            "_compiled_verdicts",
            None,
            "none",
        ),
        (
            "compiled-subset",
            "n-a",
            "uncovered",
            "refused",
            "any",
            "_compiled_verdicts",
            None,
            "none",
        ),
        ("compiled-subset", "n-a", "clean", "pass", "any", "_compiled_verdicts", None, "none"),
    ]
    for family, variants, modalities, owner, witness in (
        ("precondition", ("n-a",), ("alethic", "deontic"), "_evaluate_step", "none"),
        (
            "create-freshness",
            ("preexisting", "same-step"),
            ("alethic",),
            "_evaluate_step",
            "scalars",
        ),
        ("retract-target", ("n-a",), ("alethic",), "_evaluate_step", "none"),
        ("assert-redundant", ("n-a",), ("deontic",), "_evaluate_step", "none"),
        ("dynamic-rule", ("comparison",), ("alethic", "deontic"), "_evaluate_step", "fact-rows"),
        (
            "frame-delta",
            ("undeclared-assert", "undeclared-retract"),
            ("alethic", "deontic"),
            "_frame_verdicts",
            "fact-rows",
        ),
        ("compiled-subset", ("n-a",), ("alethic", "deontic"), "_compiled_verdicts", "fact-rows"),
    ):
        for variant in variants:
            for modality in modalities:
                rows.append(
                    (
                        family,
                        variant,
                        "violated",
                        "fail" if modality == "alethic" else "warning",
                        modality,
                        owner,
                        None,
                        witness,
                    )
                )
    for direction in ("undeclared-assert", "undeclared-retract"):
        rows.append(
            ("frame-delta", direction, "clean", "pass", "any", "_frame_verdicts", None, "none")
        )
    for family, variant, event, outcome, modality, owner, reason, witness in rows:
        yield _row(
            "transition",
            family,
            variant,
            event,
            outcome,
            owner=f"gnd.transition.{owner}",
            modality=modality,
            reason=reason,
            witness=witness,
            kind="refusal" if outcome == "refused" else "verdict",
            inputs=("identity", "role-order", "modality", "operator", "covers", "declared"),
        )
    for reason, event in (
        ("term:mod-zero", "unchecked-mod-zero"),
        ("term:exact-value-too-wide", "unchecked-exact-value-too-wide"),
        ("term:dependency-unavailable", "unchecked-dependency-unavailable"),
        ("term:div-zero", "unchecked-div-zero"),
        ("term:sqrt-negative", "unchecked-sqrt-negative"),
        ("term:haversine-coordinate-range", "unchecked-haversine-coordinate-range"),
        ("term:float-overflow", "unchecked-float-overflow"),
        ("derived-unknown", "unchecked-derived-unknown"),
    ):
        yield _row(
            "transition",
            "precondition",
            "n-a",
            event,
            "unchecked",
            owner=("gnd.transition._unknown_precondition_verdicts"
                   if reason == "derived-unknown"
                   else "gnd.transition._unavailable_precondition_verdicts"),
            modality="any",
            reason=reason,
            inputs=("identity", "role-order", "modality", "dependency-graph"),
        )
    for event, outcome in (
        ("fail", "fail"),
        ("unchecked", "unchecked"),
        ("vacuous", "vacuous"),
        ("clean", "pass"),
    ):
        yield _row(
            "composition",
            "band",
            "transition",
            event,
            outcome,
            owner="gnd.transition.band",
            kind="composition",
            inputs=("modality",),
        )
    for variant, event, outcome, kind, reason in (
        ("derived-untouched", "refused", "refused", "refusal", None),
        ("derived-no-delta", "refused", "refused", "refusal", None),
        (
            "derived-nonfunctional",
            "unchecked",
            "unchecked",
            "verdict",
            "transition:dynamic-subject-not-functional",
        ),
        ("derived-no-old", "vacuous", "vacuous", "verdict", None),
        ("derived-unknown", "unchecked", "unchecked", "verdict", "derived-unknown"),
        ("derived-no-new", "vacuous", "vacuous", "verdict", None),
        ("derived-comparison", "clean", "pass", "composition", None),
    ):
        yield _row(
            "transition",
            "dynamic-rule",
            variant,
            event,
            outcome,
            owner="gnd.transition._evaluate_derived_dynamic_rules",
            kind=kind,
            reason=reason,
            inputs=("identity", "role-order", "modality", "operator", "dependency-graph"),
        )
    for reason, event in (
        ("term:mod-zero", "unchecked-mod-zero"),
        ("term:exact-value-too-wide", "unchecked-exact-value-too-wide"),
        ("term:dependency-unavailable", "unchecked-dependency-unavailable"),
        ("term:div-zero", "unchecked-div-zero"),
        ("term:sqrt-negative", "unchecked-sqrt-negative"),
        ("term:haversine-coordinate-range", "unchecked-haversine-coordinate-range"),
        ("term:float-overflow", "unchecked-float-overflow"),
    ):
        yield _row(
            "transition",
            "dynamic-rule",
            "derived-unavailable",
            event,
            "unchecked",
            owner="gnd.transition._unavailable_dynamic_rule_verdicts",
            reason=reason,
            inputs=("identity", "role-order", "modality", "dependency-graph"),
        )
    for modality in ("alethic", "deontic"):
        yield _row(
            "transition",
            "dynamic-rule",
            "derived-comparison",
            "violated",
            "fail" if modality == "alethic" else "warning",
            owner="gnd.transition._evaluate_derived_dynamic_rules",
            modality=modality,
            inputs=("identity", "role-order", "modality", "operator", "dependency-graph"),
        )
    for variant in ("added", "removed"):
        yield _row(
            "transition",
            "derived-change",
            variant,
            "projected",
            "projected",
            owner="gnd.transition._derived_changes",
            kind="projection",
            inputs=("identity", "role-order", "derivation-kind"),
        )


def _projection_rows() -> Iterator[Branch]:
    for variant, owner, events in (
        (
            "n-a",
            "gnd.report.build_check_payload",
            ("counts", "verdict-row", "coverage", "derivation-row", "envelope-only"),
        ),
        (
            "phase1",
            "gnd.report.build_check_payload",
            ("counts", "verdict-row", "coverage", "band", "acceptance"),
        ),
    ):
        for event in events:
            yield _row(
                "report",
                "check",
                variant,
                event,
                "projected",
                owner=owner,
                kind="projection",
                inputs=("identity", "role-order", "modality", "covers", "declared"),
            )
    yield _row(
        "report",
        "check",
        "n-a",
        "incompatible-schema",
        "refused",
        owner="gnd.report.build_check_payload",
        kind="refusal",
        inputs=("derivation-kind",),
    )
    for event in ("evaluated", "not-evaluated", "families", "no-families"):
        yield _row(
            "report",
            "transition",
            "n-a",
            event,
            "projected",
            owner="gnd.report.build_transition_payload",
            kind="projection",
            inputs=("identity", "modality"),
        )
    yield _row(
        "report",
        "transition-derived-changes",
        "n-a",
        "projected",
        "projected",
        owner="gnd.redaction._project_transition",
        kind="projection",
        inputs=("identity", "role-order", "derivation-kind"),
    )
    for family, outcomes in (
        ("decision", ("accept", "refuse", "indeterminate")),
        ("assurance", ("none", "partial", "proof-backed")),
    ):
        for outcome in outcomes:
            yield _row(
                "certification",
                family,
                "phase1",
                outcome,
                outcome,
                owner="gnd.assurance.certify_snapshot",
                kind="decision",
                inputs=("variant",),
            )


def _feedback_rows() -> Iterator[Branch]:
    # Imported report rows are inputs to cross-validation, never observations
    # that the current process executed the producer's derivation evaluator.
    for variant in ("derived", "semiderived"):
        for outcome, reason in (
            ("pass", None),
            ("fail", None),
            ("unchecked", "derivation-not-covered"),
            ("unchecked", "derivation-rule-opaque"),
        ):
            yield _row(
                "experiment-feedback",
                "verifier-derivation",
                variant,
                reason or outcome,
                outcome,
                owner="gnd.exp.session_eval.validate_verifier_payload",
                kind="projection",
                modality="alethic",
                reason=reason,
                inputs=("derivation-kind",),
            )
    for family, variant, events, owner, kind, outcome in (
        ("case", "n-a", ("untrusted",), "case_decision", "decision", "refuse"),
        (
            "contract",
            "n-a",
            (
                "no-required-cases",
                "missing-case",
                "stale-candidate",
                "stale-contract",
                "rejected-case",
            ),
            "contract_accepts",
            "decision",
            "refuse",
        ),
        ("contract", "n-a", ("accept",), "contract_accepts", "decision", "accept"),
        (
            "projection",
            "n-a",
            ("legacy-v1", "current-v2", "derivation-v3"),
            "_case_feedback",
            "projection",
            "projected",
        ),
        ("projection", "n-a", ("unsupported-version",), "_case_feedback", "refusal", "refused"),
        (
            "projection",
            "constraint-satisfaction",
            ("repair-details",),
            "_case_feedback_v2",
            "projection",
            "projected",
        ),
        (
            "projection",
            "exact-bytes",
            ("output-details",),
            "_case_feedback_v2",
            "projection",
            "projected",
        ),
        (
            "attempt",
            "n-a",
            (
                "evaluation-contract-mismatch",
                "missing-contract",
                "contract-id-mismatch",
                "undeclared-case",
                "case-role-mismatch",
                "case-candidate-mismatch",
                "case-contract-mismatch",
            ),
            "build_attempt_feedback",
            "refusal",
            "refused",
        ),
        ("attempt", "n-a", ("built",), "build_attempt_feedback", "projection", "projected"),
    ):
        for event in events:
            yield _row(
                "experiment-feedback",
                family,
                variant,
                event,
                outcome,
                owner=f"gnd.exp.session_eval.{owner}",
                kind=kind,
                inputs=("identity", "modality", "covers", "declared", "multiplicity"),
            )
    for variant in ("exact-bytes", "constraint-satisfaction"):
        for outcome in ("accept", "refuse"):
            yield _row(
                "experiment-feedback",
                "case",
                variant,
                outcome,
                outcome,
                owner="gnd.exp.session_eval.case_decision",
                kind="decision",
                inputs=("identity", "covers", "declared", "multiplicity"),
            )


def _assurance_rows() -> Iterator[Branch]:
    for variant in ("snapshot", "transition", "derivation"):
        yield _row(
            "applicability",
            "assurance",
            variant,
            "derived",
            "projected",
            owner="gnd.assurance.derive_assurance_scope",
            kind="projection",
            inputs=("identity", "variant", "covers", "declared"),
        )
        for level in ("none", "partial", "proof-backed"):
            yield _row(
                "certification",
                "assurance",
                variant,
                level,
                "projected",
                owner="gnd.assurance.certify_result",
                kind="decision",
                inputs=("identity", "variant"),
            )
        for surface, owner in (
            (
                "report",
                "gnd.report.build_transition_payload"
                if variant == "transition"
                else "gnd.report.build_check_payload",
            ),
            ("experiment-feedback", "gnd.exp.session_eval.project_assurance_feedback"),
        ):
            yield _row(
                surface,
                "assurance",
                variant,
                "projected",
                "projected",
                owner=owner,
                kind="projection",
                inputs=("identity", "variant"),
            )


REGISTRY: tuple[Branch, ...] = tuple(
    sorted(
        (
            *_snapshot_rows(),
            *_applicability_rows(),
            *_composition_rows(),
            *_derivation_rows(),
            *_transition_rows(),
            *_projection_rows(),
            *_feedback_rows(),
            *_assurance_rows(),
        ),
        key=lambda row: row.scope_id,
    )
)
_BY_ID = {row.scope_id: row for row in REGISTRY}
if len(_BY_ID) != len(REGISTRY):
    raise RuntimeError("duplicate production scope id")


def branch(scope_id: str) -> Branch:
    try:
        return _BY_ID[scope_id]
    except (KeyError, TypeError):
        raise UnregisteredBranchError(f"unregistered production branch: {scope_id!r}") from None


def is_registered(scope_id: str) -> bool:
    return isinstance(scope_id, str) and scope_id in _BY_ID


def snapshot_branch(family: str, variant: str, event: str) -> str:
    """Resolve a non-violation outcome; this lookup alone records no execution."""
    return branch(f"snapshot:{family}:{variant}:{event}").scope_id


def violated_branch(family: str, variant: str, modality: str) -> str:
    if modality not in ("alethic", "deontic"):
        raise UnregisteredBranchError(f"invalid violation modality: {modality!r}")
    return branch(f"snapshot:{family}:{variant}:violated:{modality}").scope_id


_TRACES: ContextVar[tuple[set[str], ...]] = ContextVar("gnd_semantic_branch_traces", default=())


@contextmanager
def capture_branches() -> Iterator[set[str]]:
    """Collect observed ids in this context, including nested observations."""
    reached: set[str] = set()
    token = _TRACES.set((*_TRACES.get(), reached))
    try:
        yield reached
    finally:
        _TRACES.reset(token)


def record_branch(scope_id: str, *, outcome: str | None = None) -> str:
    row = branch(scope_id)
    if outcome is not None and outcome != row.outcome:
        raise UnregisteredBranchError(
            f"branch {scope_id!r} describes {row.outcome!r}, not {outcome!r}"
        )
    for reached in _TRACES.get():
        reached.add(scope_id)
    return scope_id


_TIME_RELATIVE = re.compile(
    r"^(now|today|current_date|current_time|current_timestamp)(\(\))?$", re.IGNORECASE
)


def time_relative_operand(constraint: dict, fact_type: dict | None) -> str | None:
    """The first inline clock operand, preserving the evaluator's role precedence."""
    if fact_type is None:
        return None
    names = {str(role.get("role_name")) for role in fact_type.get("roles") or []}
    for operand in (constraint.get("role_a"), constraint.get("role_b")):
        if isinstance(operand, str) and operand not in names and _TIME_RELATIVE.match(operand):
            return operand
    return None


def constraint_variant(constraint: dict, fact_type: dict | None = None) -> str:
    """Classify the evaluator's representation variant, without evaluating it."""
    family = constraint.get("type")
    if family == "anchored":
        return "role" if constraint.get("role") is not None else "all"
    if family in ("uniqueness", "frequency"):
        return (
            ("inline" if family == "uniqueness" else "internal")
            if fact_type is not None
            else "external"
        )
    if family == "mandatory":
        return "inline"
    if family == "value":
        form = (
            "enum"
            if constraint.get("allowed") is not None
            else "ranges"
            if constraint.get("ranges") is not None
            else "range"
        )
        return form + ("-role" if isinstance(constraint.get("role_ref"), dict) else "")
    if family == "ring":
        return str(constraint.get("variant"))
    if family in ("subset", "equality", "exclusion"):
        fields = (
            ("subset_role_seq", "superset_role_seq")
            if family == "subset"
            else ("role_seq_a", "role_seq_b")
        )
        joined = any(
            len({ref.get("fact_type") for ref in constraint.get(field) or []}) > 1
            for field in fields
        )
        return "joined" if joined else "single"
    if family == "exclusive-or":
        return (
            "single-role"
            if all(len(seq or []) == 1 for seq in constraint.get("role_seqs") or [])
            else "multi-role"
        )
    if family == "cardinality":
        return str(constraint.get("scope"))
    if family == "subtype-partition":
        if constraint.get("exclusive") and constraint.get("exhaustive"):
            return "both"
        return (
            "exclusive"
            if constraint.get("exclusive")
            else "exhaustive"
            if constraint.get("exhaustive")
            else "n-a"
        )
    if family == "guarded":
        consequent = constraint.get("consequent")
        kinds = [
            kind
            for kind in ("comparison", "atom", "absence", "exists")
            if isinstance(consequent, dict) and kind in consequent
        ]
        return kinds[0] if len(kinds) == 1 else "n-a"
    if family == "value-comparison":
        if time_relative_operand(constraint, fact_type) is not None:
            return "inline-time-literal"
        left, right = constraint.get("role_a"), constraint.get("role_b")
        if fact_type is None:
            return (
                "cross-same" if left.get("fact_type") == right.get("fact_type") else "cross-joined"
            )
        names = {str(role.get("role_name")) for role in fact_type.get("roles") or []}

        def is_role(operand):
            return (isinstance(operand, dict) and "role" in operand) or (
                isinstance(operand, str) and operand in names
            )

        return "inline" if is_role(left) and is_role(right) else "inline-literal"
    return "n-a"


def applicable_scope_ids(model: Model, population: Population) -> tuple[str, ...]:
    """All outcomes owed by admitted input, independently of any proof declaration.

    This classifies the execution route without calling a verdict evaluator.
    Every outcome of each selected family/variant remains in the denominator,
    including the opposite result from the one the current data would produce.
    Shared applicability, composition and consumer obligations are unconditional.
    Structured semiderived extensions use the same effective fact view as check;
    otherwise a supplied surplus claim could change the selected proof route.
    """
    # Local imports keep the registry's descriptors usable during checker import.
    from gnd import checker
    from gnd.address import positional_constraint_ref
    from gnd.proof_bridge import adapt_phase1_slice

    if not population.matches_validation_marker(model):
        raise checker.UnvalidatedPopulationError(population, model)

    def carries_exact_term(value: object) -> bool:
        if isinstance(value, dict):
            if set(value) == {"fn", "args"}:
                return True
            return any(carries_exact_term(item) for item in value.values())
        if isinstance(value, list):
            return any(carries_exact_term(item) for item in value)
        return False

    def carries_float_term(value: object) -> bool:
        # A model using only Phase 3/4 exact functions (mod, add, ...) must
        # NOT mark Phase 5's float-only reasons applicable -- distinct from
        # carries_exact_term, which cannot tell the two families apart.
        from gnd.terms import FLOAT_FUNCTION_ARITY

        if isinstance(value, dict):
            if set(value) == {"fn", "args"} and value.get("fn") in FLOAT_FUNCTION_ARITY:
                return True
            return any(carries_float_term(item) for item in value.values())
        if isinstance(value, list):
            return any(carries_float_term(item) for item in value)
        return False

    from gnd.terms import TEMPORAL_REASONS, uses_temporal

    temporal_terms = uses_temporal(model)
    from gnd.popvalidate import resolve_primitive

    duration_facts = {
        str(ft.get("id"))
        for ft in model.fact_types
        if any(
            resolve_primitive(str(role.get("object_type")), model) == "Duration"
            for role in ft.get("roles") or []
        )
    }
    exact_terms = carries_exact_term(model.model_dump(exclude={"warnings"}))
    float_terms = carries_float_term(model.model_dump(exclude={"warnings"}))
    aggregate_heads = {
        str(fact_type.get("id"))
        for fact_type in model.fact_types
        if isinstance((rule := fact_type.get("derivation_rule")), dict)
        and isinstance(rule.get("aggregate"), dict)
    }
    exact_heads = {
        str(fact_type.get("id"))
        for fact_type in model.fact_types
        if isinstance((rule := fact_type.get("derivation_rule")), dict)
        and (
            carries_exact_term({"where": rule.get("where"), "head": rule.get("head")})
            or str(fact_type.get("id")) in aggregate_heads
        )
    }
    changed = True
    while changed:
        changed = False
        for fact_type in model.fact_types:
            fact_type_id = str(fact_type.get("id"))
            rule = fact_type.get("derivation_rule")
            if fact_type_id in exact_heads or not isinstance(rule, dict):
                continue
            dependencies = {
                str(atom.get("fact_type"))
                for key in ("body", "negate")
                for atom in rule.get(key) or []
                if isinstance(atom, dict)
            }
            if dependencies & exact_heads:
                exact_heads.add(fact_type_id)
                changed = True

    float_heads = {
        str(fact_type.get("id"))
        for fact_type in model.fact_types
        if isinstance((rule := fact_type.get("derivation_rule")), dict)
        and carries_float_term({"where": rule.get("where"), "head": rule.get("head")})
    }
    changed = True
    while changed:
        changed = False
        for fact_type in model.fact_types:
            fact_type_id = str(fact_type.get("id"))
            rule = fact_type.get("derivation_rule")
            if fact_type_id in float_heads or not isinstance(rule, dict):
                continue
            dependencies = {
                str(atom.get("fact_type"))
                for key in ("body", "negate")
                for atom in rule.get(key) or []
                if isinstance(atom, dict)
            }
            if dependencies & float_heads:
                float_heads.add(fact_type_id)
                changed = True

    #: The four Phase 5 float-only reasons. A model that is merely
    #: term-capable (e.g. Phase 3/4's `mod`) must not mark these applicable --
    #: `term_capable` alone cannot distinguish the function family a specific
    #: constraint or derivation actually reads.
    FLOAT_ONLY_REASON_CODES = frozenset(
        {
            "term:div-zero",
            "term:sqrt-negative",
            "term:haversine-coordinate-range",
            "term:float-overflow",
        }
    )

    def applicable_row(
        row: Branch,
        *,
        term_capable: bool = exact_terms,
        aggregate_capable: bool = bool(aggregate_heads),
        float_capable: bool = float_terms,
        temporal_capable: bool = temporal_terms,
    ) -> bool:
        if row.reason_code == "reference-join-work-limit" and not model.reference_populations:
            return False
        if row.reason_code in TEMPORAL_REASONS:
            return temporal_capable
        if row.reason_code in FLOAT_ONLY_REASON_CODES:
            return float_capable
        aggregate_only = (
            row.surface == "derivation"
            and row.family == "extension"
            and row.semantic_branch.startswith("aggregate-")
        ) or (row.surface == "snapshot" and row.family == "guarded" and row.variant == "aggregate")
        if aggregate_only:
            return aggregate_capable
        exact_only = (
            row.surface == "derivation"
            and row.family == "extension"
            and row.semantic_branch.startswith("exact-")
        ) or (
            row.surface == "snapshot"
            and row.family == "guarded"
            and row.semantic_branch == "exact-success"
        )
        if exact_only and not term_capable:
            return False
        return term_capable or row.reason_code is None or not row.reason_code.startswith("term:")

    static_view_scope = "composition:derivation-view:static:applied"
    dynamic_view_scope = "composition:derivation-view:dynamic:applied"

    def dynamic_composition_row(row: Branch) -> bool:
        # Owed only when a step can refresh a dynamic structured head.
        return (row.surface, row.family) in {
            ("composition", "dynamic-refresh"),
            ("transition", "derived-change"),
            ("report", "transition-derived-changes"),
        }

    has_opaque = any(
        isinstance(value, dict) and set(value) == {"$opaque"}
        for rows in population.facts.values() for fact in rows for value in fact.values()
    )
    selected = {
        row.scope_id
        for row in REGISTRY
        if row.surface
        in {"applicability", "composition", "report", "experiment-feedback", "certification"}
        and row.scope_id not in {static_view_scope, dynamic_view_scope}
        and (has_opaque or row.scope_id not in {
            "applicability:adapter:n-a:opaque-value",
            "applicability:opaque:n-a:opaque-value",
        })
        and not dynamic_composition_row(row)
        and applicable_row(row)
    }
    view = population
    structured = any(isinstance(ft.get("derivation_rule"), dict) for ft in model.fact_types)
    if structured:
        if has_opaque:
            extensions, _verdicts = checker._evaluate_derivations_dispatch(model, population)
            calculated = checker._ExtensionResult(extensions, 0)
        elif checker._model_uses_exact_derivations(model):
            calculated = checker._exact_extension_calculator(
                model, checker._base_relations(model, population)
            )
        else:
            calculated = checker._python_extension_calculator(
                model, checker._base_relations(model, population)
            )
        view = checker._constraint_view_dispatch(model, population, calculated.extensions)
        derivation_variants = {
            str(ft.get("derivation"))
            for ft in model.fact_types
            if ft.get("derivation") in {"derived", "semiderived"}
            and ft.get("derivation_rule") is not None
        }
        exact_derivation_variants = {
            str(ft.get("derivation")) for ft in model.fact_types if str(ft.get("id")) in exact_heads
        }
        aggregate_derivation_variants = {
            str(ft.get("derivation"))
            for ft in model.fact_types
            if str(ft.get("id")) in aggregate_heads
        }
        float_derivation_variants = {
            str(ft.get("derivation")) for ft in model.fact_types if str(ft.get("id")) in float_heads
        }
        selected.update(
            row.scope_id
            for row in REGISTRY
            if row.surface == "derivation"
            and row.variant in derivation_variants
            and applicable_row(
                row,
                term_capable=row.variant in exact_derivation_variants,
                aggregate_capable=row.variant in aggregate_derivation_variants,
                float_capable=row.variant in float_derivation_variants,
            )
        )
    if model.operations:
        has_preconditions = any(operation.get("preconditions") for operation in model.operations)
        has_dynamic_rules = any(operation.get("dynamic_rules") for operation in model.operations)
        exact_preconditions = any(
            str(atom.get("fact_type")) in exact_heads
            for operation in model.operations
            for obligation in operation.get("preconditions") or []
            for atom in obligation.get("require") or []
            if isinstance(atom, dict)
        )
        exact_dynamic_rules = any(
            isinstance((subject := rule.get("subject")), dict)
            and str(subject.get("fact_type")) in exact_heads
            for operation in model.operations
            for rule in operation.get("dynamic_rules") or []
            if isinstance(rule, dict)
        )
        float_preconditions = any(
            str(atom.get("fact_type")) in float_heads
            for operation in model.operations
            for obligation in operation.get("preconditions") or []
            for atom in obligation.get("require") or []
            if isinstance(atom, dict)
        )
        float_dynamic_rules = any(
            isinstance((subject := rule.get("subject")), dict)
            and str(subject.get("fact_type")) in float_heads
            for operation in model.operations
            for rule in operation.get("dynamic_rules") or []
            if isinstance(rule, dict)
        )
        structured_ids = {
            str(fact_type.get("id"))
            for fact_type in model.fact_types
            if isinstance(fact_type.get("derivation_rule"), dict)
        }
        derived_subject_rules = any(
            isinstance((subject := rule.get("subject")), dict)
            and str(subject.get("fact_type")) in structured_ids
            for operation in model.operations
            for rule in operation.get("dynamic_rules") or []
            if isinstance(rule, dict)
        )
        from gnd.model import derivation_classifications

        classifications = derivation_classifications(model.model_dump())
        dynamic_heads = any(row.stability == "dynamic" for row in classifications)

        def transition_row_is_applicable(row: Branch) -> bool:
            if row.family == "precondition" and not has_preconditions:
                return False
            if row.family == "dynamic-rule" and not has_dynamic_rules:
                return False
            if (
                row.family == "dynamic-rule"
                and row.variant.startswith("derived-")
                and not derived_subject_rules
            ):
                return False
            if dynamic_composition_row(row) and not dynamic_heads:
                return False
            term_capable = (
                exact_preconditions
                if row.family == "precondition"
                else exact_dynamic_rules
                if row.family == "dynamic-rule"
                else False
            )
            float_capable = (
                float_preconditions
                if row.family == "precondition"
                else float_dynamic_rules
                if row.family == "dynamic-rule"
                else False
            )
            return applicable_row(row, term_capable=term_capable, float_capable=float_capable)

        selected.update(
            row.scope_id
            for row in REGISTRY
            if row.surface == "transition" and transition_row_is_applicable(row)
        )
        if any(row.stability == "static" for row in classifications):
            selected.add(static_view_scope)
        if dynamic_heads:
            selected.add(dynamic_view_scope)
            selected.update(
                row.scope_id
                for row in REGISTRY
                if row.surface in {"composition", "report"}
                and dynamic_composition_row(row)
                and applicable_row(row)
            )
    constraints = [
        (constraint, ft, positional_constraint_ref(str(ft.get("id")), index))
        for ft in model.fact_types
        for index, constraint in enumerate(ft.get("constraints") or [])
    ] + [
        (constraint, None, positional_constraint_ref(None, index))
        for index, constraint in enumerate(model.constraints)
    ]
    for constraint, ft, reference in constraints:
        family = str(constraint.get("type"))
        modality = str(constraint.get("modality"))
        value = adapt_phase1_slice(model, view, constraint, ft, reference)
        if value is not None:
            variants = {
                "mandatory": {"phase1-inline"},
                "frequency": {"phase1-internal"},
                "textual": {"phase1"},
            }[family]
        else:
            variants = {constraint_variant(constraint, ft)}
            # These are shared family-level guards, not another representation.
            # In particular guarded zero-binding success is independent of the
            # consequent kind and must not disappear with a comparison variant.
            if family in {"ring", "subtype-partition", "guarded"} and not (
                family == "guarded" and constraint_variant(constraint) == "exists"
            ):
                variants.add("n-a")
            if family == "guarded" and any(
                isinstance(atom, dict) and str(atom.get("fact_type")) in aggregate_heads
                for atom in constraint.get("antecedent") or []
            ):
                variants.add("aggregate")
        constraint_term_capable = carries_exact_term(constraint) or bool(
            set(checker._scope_fact_types(constraint, family, model, ft)) & exact_heads
        )
        constraint_float_capable = carries_float_term(constraint) or bool(
            set(checker._scope_fact_types(constraint, family, model, ft)) & float_heads
        )
        selected.update(
            row.scope_id
            for row in REGISTRY
            if row.surface == "snapshot"
            and row.family == family
            and row.variant in variants
            and row.modality in {"any", modality}
            and applicable_row(
                row,
                temporal_capable=uses_temporal(constraint)
                or bool(
                    set(checker._scope_fact_types(constraint, family, model, ft)) & duration_facts
                ),
                term_capable=constraint_term_capable,
                float_capable=constraint_float_capable,
            )
        )
    return tuple(sorted(selected))
