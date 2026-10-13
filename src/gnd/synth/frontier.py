"""The two case kinds the three population labels do not name.

**`no-subjects` is the ``(no-subjects, pass)`` row of the cell table** — the row
F-02 and F-05 both lived in, and the one a harness without it reports zero false
passes over regardless of what the checker does. A population whose subjects are
empty is not conforming (a consumer told "this should pass" would be misled: the
predicted verdict is ``vacuous``) and not violating (nothing in it violates
anything). It is the frontier of EVALUABILITY.

**`unchecked` pins every predecessor band-4 route in the measurement scope**,
which is what turns the undecided rate into a measurement of the frontier rather
than a residual. The route set is derived from the production semantic
registry's unchecked rows (:data:`BAND4_REASON_CODES`), with an explicit
Phase-6 guarded-exists exclusion to preserve the predecessor report contract.
Other routes added later without a case still appear as missing cells.

Neither kind needs a new population label. D-10's three values stay three and
D-15 keeps the format shut, so the five case kinds live in the sidecar under
``case_kind`` and map onto three labels through
:data:`gnd.synth.provenance.CASE_KIND_TO_LABEL`; ``no-subjects`` and
``unchecked`` both carry ``label: boundary``.

The routes are taken from ``01.1-VERIFICATION.md``'s residual-routes table, not
from imagination:

============================================  =========================================
route                                          construction
============================================  =========================================
inline families, host fact type empty          ``empty-host-fact-type``
``mandatory`` / ``mandatory-disjunctive``      ``coverage-omission``
object-scoped ``value`` / ``cardinality`` /    ``empty-object-scope`` (F-02)
``subtype-partition``
join-scoped families, zero-row join            ``zero-row-join-one-side-empty`` **and**
                                               ``zero-row-join-disjoint-anchors``
============================================  =========================================

The SECOND join construction is the one that matters. Nothing about it looks
empty: ``coverage`` reports facts on both sides, both anchor fact types are
populated, and before plan 01 the checker affirmed satisfaction over it at exit 0
with ``acceptance_ready: true``. That is F-05, and a corpus without the
disjoint-anchors construction cannot detect its return.
"""

from __future__ import annotations

from random import Random
from typing import Any

from gnd.checker import IMPLEMENTED_FAMILIES, check
from gnd.model import Model
from gnd.semantic_registry import REGISTRY, Branch
from gnd.synth.assemble import (
    _constraint_iter_with_ref,
    _role_object,
    _seq_tuples,
    _universe,
)
from gnd.synth.boundary import BoundaryCase, NotDerivable, _clone
from gnd.synth.mutate import (
    _direct_subtypes,
    _fresh_identifier,
    _resolve,
    _scope_fts,
    expected_state,
)

__all__ = [
    "BAND4_REASON_CODES",
    "JOIN_SCOPED_FAMILIES",
    "OBJECT_SCOPED_FAMILIES",
    "SHARED_REASON_CODES",
    "enumerate_frontier",
    "no_subjects_cases",
    "reason_codes_by_family",
    "unchecked_cases",
]

#: Families whose subjects are an object type's population — the F-02 route.
OBJECT_SCOPED_FAMILIES = {"value", "cardinality", "subtype-partition"}

#: Families evaluated over a JOIN of several fact types — the F-05 route.
JOIN_SCOPED_FAMILIES = {
    "uniqueness",
    "frequency",
    "subset",
    "equality",
    "exclusion",
    "value-comparison",
}


def _constraint_band4_rows() -> tuple[Branch, ...]:
    """Registered legacy constraint refusals used by the mutation frontier.

    Exact-term availability is reported separately as an unmutated derivation
    summary; folding those reasons into every constraint family's mutation
    frontier would inflate and misattribute the denominator.
    """
    return tuple(
        row
        for row in REGISTRY
        if row.outcome == "unchecked"
        and row.reason_code is not None
        and not row.reason_code.startswith("term:")
        and (
            row.surface == "snapshot"
            or row.surface == "applicability"
            and row.family in {"implemented", "join"}
        )
        # Phase 6's guarded-exists refusals remain registered snapshot routes,
        # but they are outside the frozen predecessor BAND4 report contract.
        # Phase 6 does not claim synth/frontier coverage for this new lane.
        and not (row.family == "guarded" and row.variant == "exists")
        # Compiled standing obligations require explicit caller activation;
        # the predecessor synth/measure lane uses ordinary snapshot checking.
        and row.family != "compiled-subset"
    )


def _scan_reason_codes() -> tuple[str, ...]:
    """Every predecessor constraint band-4 reason in measurement scope.

    Derived rather than re-typed (research assumption A4): a registered route
    added without a matching case must show up as a MISSING cell in the coverage
    matrix, except for the explicit guarded-exists and opt-in compiled
    standing-obligation boundaries above.
    """
    return tuple(sorted({
        row.reason_code for row in _constraint_band4_rows()
        if row.family != "anchored"
    }))


#: The band-4 frontier, derived from the semantic registry. The undecided rate is a
#: measurement OF this set.
#:
#: SCOPE (v5.0 Phase 3, D-P3.7): this frontier is CONSTRAINT-ONLY, by name.
#: The two derivation reason codes (``gnd.checker.DERIVATION_REASON_CODES``)
#: ride the report's ``derivations[]`` block, not constraint verdicts, and a
#: family-keyed map has no key to hang a fact-type obligation on — so their
#: absence here is a stated boundary, pinned by
#: ``tests/test_measure_derivation.py``, never a scan miss.
BAND4_REASON_CODES: tuple[str, ...] = _scan_reason_codes()


def frontier_codes_for(model: Model) -> tuple[str, ...]:
    """Add source-only reasons without widening the pinned legacy frontier."""
    anchored = any(
        constraint.get("type") == "anchored"
        for fact_type in model.fact_types
        for constraint in fact_type.get("constraints") or []
    )
    return tuple(sorted(set(BAND4_REASON_CODES) | (
        {"anchor-non-lexical", "anchor-sidecar-absent"} if anchored else set()
    )))


#: Band-4 codes emitted by shared applicability branches rather than by any
#: family's own branch. They are structural model faults (an unimplemented
#: family, a disconnected or ambiguous join) that any family's constraint can
#: reach, so attributing them to a family would make every family look as though
#: it owned an undecidability frontier it does not have.
SHARED_REASON_CODES: tuple[str, ...] = tuple(
    sorted(
        {
            row.reason_code
            for row in _constraint_band4_rows()
            if row.surface == "applicability" or row.family == "textual"
        }
    )
)


def reason_codes_by_family() -> dict[str, tuple[str, ...]]:
    """``family -> the band-4 reason codes the family's OWN branch can emit``.

    Attribution is by the registry row's family. Shared applicability codes are
    excluded and exposed separately as :data:`SHARED_REASON_CODES` — a family
    with no owned route has no undecidability frontier of its own, and that is
    what makes its ``unchecked`` cell not-applicable rather than missing.
    """
    out: dict[str, tuple[str, ...]] = {}
    for family in sorted(IMPLEMENTED_FAMILIES | {"textual"}):
        owned = {
            row.reason_code
            for row in _constraint_band4_rows()
            if row.surface == "snapshot"
            and row.family == family
            and row.reason_code != "family-unimplemented"
        }
        out[family] = tuple(sorted(owned))
    return out


# --------------------------------------------------------------------------- #
# no-subjects
# --------------------------------------------------------------------------- #


def _joining_sequences(constraint: dict[str, Any]) -> list[list[dict[str, Any]]]:
    """The constraint's role sequences that ACTUALLY join — span >1 fact type.

    A two-SIDED constraint is not a joining one. Flattening ``role_seq_a`` and
    ``role_seq_b`` into one list would make every ``subset`` / ``equality`` /
    ``exclusion`` look join-scoped, and emptying one side of a ``subset`` is a
    genuine VIOLATION (subset ⊄ superset), not vacuity — the case would be a
    violating population wearing a ``no-subjects`` label, which is precisely the
    mislabelling this kind exists to prevent.
    """
    sequences: list[list[dict[str, Any]]] = []
    for field_name in (
        "role_refs",
        "subset_role_seq",
        "superset_role_seq",
        "role_seq_a",
        "role_seq_b",
    ):
        seq = [r for r in constraint.get(field_name) or [] if isinstance(r, dict)]
        if seq:
            sequences.append(seq)
    for seq in constraint.get("role_seqs") or []:
        flat = [r for r in (seq or []) if isinstance(r, dict)]
        if flat:
            sequences.append(flat)
    return [seq for seq in sequences if len({str(r.get("fact_type")) for r in seq}) >= 2]


def _empty_one_anchor_side(doc, refs) -> str | None:
    """Empty the LAST distinct fact type of a join. Returns its id, or None."""
    ftids: list[str] = []
    for ref in refs:
        ftid = str(ref.get("fact_type"))
        if ftid not in ftids:
            ftids.append(ftid)
    if len(ftids) < 2:
        return None
    doc.setdefault("facts", {})[ftids[-1]] = []
    return ftids[-1]


def _make_anchors_disjoint(doc, model, refs, rng) -> str | None:
    """Rewrite the join ANCHOR values of the last fact type to fresh identifiers.

    The join is on the NON-referenced roles of shared object type (the assembler's
    own independent join semantics), so replacing those values with identifiers no
    other side carries drops the join to zero rows while leaving BOTH fact types
    populated. That is the construction nothing looks empty in.
    """
    role_obj = _role_object(model)
    by_ft: dict[str, set[str]] = {}
    order: list[str] = []
    for ref in refs:
        ftid = str(ref.get("fact_type"))
        if ftid not in by_ft:
            by_ft[ftid] = set()
            order.append(ftid)
        by_ft[ftid].add(str(ref.get("role")))
    if len(order) < 2:
        return None
    target_ft = order[-1]
    anchors = [
        (rn, oid) for rn, oid in role_obj.get(target_ft, {}).items() if rn not in by_ft[target_ft]
    ]
    if not anchors:
        return None
    rows = (doc.get("facts") or {}).get(target_ft, [])
    if not rows:
        return None
    touched = False
    for fact in rows:
        for role_name, oid in anchors:
            if role_name in fact:
                fact[role_name] = _fresh_identifier(doc, model, str(oid), rng)
                touched = True
    return target_ft if touched else None


def _subject_object_type(model: Model, constraint: dict[str, Any], family: str) -> str | None:
    """The object type a single-role disjunctive/exclusive family quantifies over.

    ``mandatory-disjunctive`` and single-role ``exclusive-or`` do not name an
    ``object_type``, but their subjects ARE an object type's universe — so
    emptying it is their route to the no-subjects row, and without it the
    families read as having no vacuity frontier at all.
    """
    if family not in ("mandatory-disjunctive", "exclusive-or"):
        return None
    refs: list[dict[str, Any]] = []
    for candidate in constraint.get("role_refs") or []:
        if isinstance(candidate, dict):
            refs.append(candidate)
    for seq in constraint.get("role_seqs") or []:
        flat = [r for r in (seq or []) if isinstance(r, dict)]
        if len(flat) != 1:
            return None
        refs.extend(flat)
    role_obj = _role_object(model)
    oids = {role_obj.get(str(r.get("fact_type")), {}).get(str(r.get("role"))) for r in refs}
    if len(oids) != 1 or None in oids:
        return None
    return str(next(iter(oids)))


def no_subjects_cases(
    model: Model, baseline_doc: dict[str, Any], rng: Random | None = None
) -> tuple[list[BoundaryCase], list[NotDerivable]]:
    """Populations that reach evaluation with an EMPTY subject set.

    Each route CONSTRUCTS a candidate population; the independent expected-state
    engine then decides whether the candidate really lands on the no-subjects row.
    A candidate whose ground truth comes back ``violated`` is a
    MASKED-BY-VACUITY case, not a no-subjects one, and shipping it under this
    label would put a violated ground truth in the row the measurement uses to
    detect exactly that confusion. Such candidates become ``NotDerivable``
    records naming what they actually are.

    ``cardinality {min >= 1}`` over an empty universe is a DECIDED FAILURE, not
    vacuity. It is therefore reported as not derivable for this row; the ordinary
    boundary generator owns that real below-minimum case.
    """
    rng = rng if rng is not None else Random(0)
    cases: list[BoundaryCase] = []
    downs: list[NotDerivable] = []
    children = _direct_subtypes(model)
    seen_empty_ft: set[tuple[str, str]] = set()

    def admit(
        ref: str,
        constraint: dict[str, Any],
        ft: dict[str, Any] | None,
        family: str,
        name: str,
        work: dict[str, Any],
        description: str,
    ) -> None:
        """Keep the candidate only if the INDEPENDENT oracle agrees it is one."""
        state = expected_state(constraint, ft, work, model, children)
        if state is None:
            downs.append(
                NotDerivable(
                    ref,
                    family,
                    f"no-subjects:{name}",
                    "the independent expected-state engine makes no claim over this "
                    "constraint shape, so the candidate carries no predicted verdict and "
                    "is not a measurement input",
                    case_kind="no-subjects",
                )
            )
            return
        if state.ground_truth != "no-subjects":
            downs.append(
                NotDerivable(
                    ref,
                    family,
                    f"no-subjects:{name}",
                    f"the construction leaves ground truth {state.ground_truth!r} "
                    f"(expected verdict {state.expected_verdict!r}, reason "
                    f"{state.reason!r}) — that is a "
                    f"{'masked-by-vacuity' if state.ground_truth == 'violated' else 'decided'} "
                    f"case, not a no-subjects one, and labelling it `no-subjects` would put "
                    f"a decided ground truth in the row the measurement uses to detect "
                    f"exactly that confusion",
                    case_kind="no-subjects",
                )
            )
            return
        cases.append(
            BoundaryCase(ref, family, name, "frontier", work, description, case_kind="no-subjects")
        )

    for ref, constraint, ft in _constraint_iter_with_ref(model):
        family = str(constraint.get("type"))
        if family == "anchored":
            downs.append(NotDerivable(
                ref, family, "no-subjects",
                "source anchoring is unmutated by the population-only synthesis lane",
                case_kind="no-subjects",
            ))
            continue
        if family not in IMPLEMENTED_FAMILIES:
            downs.append(
                NotDerivable(
                    ref,
                    family,
                    "no-subjects",
                    f"family {family!r} is not mechanically evaluated at all, so it never "
                    f"reaches the subject-set step — it returns `unchecked` at the verdict "
                    f"step and never reaches vacuity (01.1-VERIFICATION residual-routes "
                    f"table)",
                    case_kind="no-subjects",
                )
            )
            continue

        # ---- route: the inline host fact type is empty --------------------- #
        # Bound per (fact type, FAMILY) rather than per fact type: two inline
        # constraints of different families on one host are two different cells
        # of the matrix, and crediting only the first would leave the second
        # reading as an uncovered gap it is not.
        if ft is not None:
            ftid = str(ft.get("id"))
            if (ftid, family) not in seen_empty_ft:
                seen_empty_ft.add((ftid, family))
                if (baseline_doc.get("facts") or {}).get(ftid):
                    work = _clone(baseline_doc)
                    (work.get("facts") or {}).pop(ftid, None)
                    admit(
                        ref,
                        constraint,
                        ft,
                        family,
                        "empty-host-fact-type",
                        work,
                        f"the inline constraint's host fact type {ftid!r} is empty, so its "
                        f"subject set is empty and the constraint is not evaluated — the "
                        f"frontier of EVALUABILITY",
                    )
                else:
                    downs.append(
                        NotDerivable(
                            ref,
                            family,
                            "no-subjects",
                            f"host fact type {ftid!r} is already empty in the baseline; the "
                            f"case would be indistinguishable from the baseline",
                            case_kind="no-subjects",
                        )
                    )

        # ---- route: coverage omission (mandatory-relevant) ------------------ #
        if family == "mandatory" and ft is not None:
            target = str(ft.get("id"))
            covers = list((baseline_doc.get("population") or {}).get("covers") or [])
            if target in covers:
                work = _clone(baseline_doc)
                header = work.setdefault("population", {})
                header["covers"] = [c for c in header.get("covers") or [] if c != target]
                admit(
                    ref,
                    constraint,
                    ft,
                    family,
                    "coverage-omission",
                    work,
                    f"{target!r} dropped from `covers`: the population declares it does not "
                    f"cover the fact type, so the mandatory role has no observable subject "
                    f"set",
                )
            else:
                downs.append(
                    NotDerivable(
                        ref,
                        family,
                        "no-subjects",
                        "the subject fact type is not declared in `covers`; there is nothing "
                        "to omit",
                        case_kind="no-subjects",
                    )
                )

        # ---- route: empty object scope (F-02) ------------------------------ #
        role_scoped_value = family == "value" and isinstance(constraint.get("role_ref"), dict)
        if role_scoped_value:
            scope_oid = None
        elif family in OBJECT_SCOPED_FAMILIES:
            scope_oid = (
                constraint.get("object_type")
                or constraint.get("supertype")
                or _subject_object_type(model, constraint, family)
            )
        else:
            scope_oid = _subject_object_type(model, constraint, family)
        if scope_oid is not None:
            oid = str(scope_oid)
            if _universe(baseline_doc, model, oid, children):
                work = _clone(baseline_doc)
                _empty_object_universe(work, model, oid, children)
                admit(
                    ref,
                    constraint,
                    ft,
                    family,
                    "empty-object-scope",
                    work,
                    f"the {oid!r} universe is empty, so the constraint has no subjects. This "
                    f"is the F-02 row: before that fix the checker reported `pass` — an "
                    f"affirmative claim over an unevaluated scope",
                )
            else:
                downs.append(
                    NotDerivable(
                        ref,
                        family,
                        "no-subjects",
                        f"the {oid!r} universe is already empty in the baseline",
                        case_kind="no-subjects",
                    )
                )

        # ---- route: every scope fact type empty ---------------------------- #
        # The uniform route for the families whose subjects are neither an
        # inline host nor an object universe (the set families, xor). The oracle
        # filter above is what keeps a MASKED case from wearing this label.
        scope = _scope_fts(constraint, family, model, ft)
        if ft is None and scope and any((baseline_doc.get("facts") or {}).get(s) for s in scope):
            work = _clone(baseline_doc)
            for ftid in scope:
                (work.get("facts") or {}).pop(ftid, None)
            admit(
                ref,
                constraint,
                ft,
                family,
                "empty-all-scope-fact-types",
                work,
                f"every fact type the constraint ranges over ({', '.join(sorted(scope))}) is "
                f"empty, so it has no subjects at all",
            )

        # ---- route: zero-row join, in BOTH constructions -------------------- #
        sequences = _joining_sequences(constraint) if family in JOIN_SCOPED_FAMILIES else []
        for refs in sequences[:1]:
            if not _seq_tuples(baseline_doc, model, refs):
                downs.append(
                    NotDerivable(
                        ref,
                        family,
                        "no-subjects",
                        "the baseline's join already yields no rows, so neither zero-row "
                        "construction is distinguishable from it",
                        case_kind="no-subjects",
                    )
                )
                continue
            work = _clone(baseline_doc)
            emptied = _empty_one_anchor_side(work, refs)
            if emptied is not None:
                admit(
                    ref,
                    constraint,
                    ft,
                    family,
                    "zero-row-join-one-side-empty",
                    work,
                    f"one anchor fact type ({emptied!r}) is empty, so the join yields zero "
                    f"rows and the constraint has no subjects",
                )
            work = _clone(baseline_doc)
            disjoint = _make_anchors_disjoint(work, model, refs, rng)
            if disjoint is None:
                downs.append(
                    NotDerivable(
                        ref,
                        family,
                        "no-subjects-disjoint-anchors",
                        "the join carries no non-referenced anchor role whose values could "
                        "be made disjoint without emptying a side",
                        case_kind="no-subjects",
                    )
                )
            else:
                admit(
                    ref,
                    constraint,
                    ft,
                    family,
                    "zero-row-join-disjoint-anchors",
                    work,
                    f"BOTH anchor fact types stay populated and {disjoint!r} carries fresh "
                    f"anchor identifiers, so the join yields zero rows while NOTHING LOOKS "
                    f"EMPTY — `coverage` reports facts on both sides. This is the F-05 "
                    f"construction: before plan 01 the checker affirmed satisfaction over it "
                    f"at exit 0 with acceptance_ready true",
                )
    return cases, downs


def _empty_object_universe(doc, model, oid: str, children) -> None:
    """Remove every observable member of ``oid`` (rosters and role plays)."""
    from gnd.synth.boundary import _governed_object_types

    covered = _governed_object_types(model, str(oid), children)
    role_obj = _role_object(model)
    for ftid, rows in list((doc.get("facts") or {}).items()):
        governed = [rn for rn, rid in role_obj.get(ftid, {}).items() if str(rid) in covered]
        if not governed:
            continue
        doc["facts"][ftid] = [fact for fact in rows if all(rn not in fact for rn in governed)]
    for roster_id in list(doc.get("instances") or {}):
        if str(roster_id) in covered:
            doc["instances"][roster_id] = []


# --------------------------------------------------------------------------- #
# unchecked
# --------------------------------------------------------------------------- #


def _band4_verdicts(model: Model, doc: dict[str, Any]):
    """The checker's ``unchecked`` verdicts over one candidate document."""
    import json
    import tempfile
    from pathlib import Path

    from gnd.population import PopulationValidationError, load_population

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
        json.dump(doc, handle)
        temp_path = handle.name
    try:
        report = check(model, load_population(temp_path, model=model))
    except PopulationValidationError:
        return []
    finally:
        Path(temp_path).unlink(missing_ok=True)
    return [
        verdict
        for verdict in report.verdicts
        if verdict.verdict == "unchecked" and verdict.reason_code is not None
    ]


def unchecked_cases(
    model: Model, baseline_doc: dict[str, Any], rng: Random | None = None
) -> tuple[list[BoundaryCase], list[NotDerivable]]:
    """One population per band-4 route THIS model reaches, asserting its code.

    Routes are found by OBSERVING the checker over candidate populations — the
    baseline first, then the boundary class's own derived candidates — rather
    than by a hand list of model shapes. A route reachable only once a fact type
    is populated (the multi-role ``exclusive-or``'s clean exclusion half is the
    measured example) is invisible to a baseline-only probe, and a hand list is
    exactly the thing that silently stops covering a route added later.

    The DENOMINATOR — :data:`BAND4_REASON_CODES` — is scanned from the checker's
    own source. A code in the denominator with no case here is a route this model
    cannot reach, and it is REPORTED as such rather than dropped.
    """
    rng = rng if rng is not None else Random(0)
    cases: list[BoundaryCase] = []
    downs: list[NotDerivable] = []
    seen: set[str] = set()
    active_codes = frontier_codes_for(model)

    def harvest(doc: dict[str, Any], provenance: str) -> None:
        for verdict in _band4_verdicts(model, doc):
            if verdict.constraint_type == "anchored":
                continue  # no population-only source witness can discharge it
            if verdict.reason_code in seen:
                continue
            seen.add(str(verdict.reason_code))
            constraint, _ft = _resolve(model, verdict.constraint_ref)
            cases.append(
                BoundaryCase(
                    verdict.constraint_ref,
                    str(constraint.get("type")),
                    f"unchecked-{verdict.reason_code}",
                    "frontier",
                    _clone(doc),
                    f"pins the band-4 route `{verdict.reason_code}` ({provenance}): the "
                    f"checker declines to decide this constraint mechanically, and the "
                    f"undecided rate is a measurement OF that frontier rather than a "
                    f"residual",
                    case_kind="unchecked",
                )
            )

    harvest(baseline_doc, "over the conforming baseline")

    # Second pass over the boundary class's own candidates. Deterministic: the
    # candidates are enumerated in the same order every run, so which population
    # carries a given route is stable and the payload stays byte-reproducible.
    from gnd.synth.boundary import enumerate_boundary

    candidates, _ = enumerate_boundary(model, baseline_doc, Random(0))
    for candidate in candidates:
        if len(seen) == len(active_codes):
            break
        harvest(candidate.doc, f"reached through the boundary case `{candidate.name}`")

    del rng  # the routes are structural; nothing here draws a value
    for code in active_codes:
        if code not in seen:
            downs.append(
                NotDerivable(
                    "-",
                    "-",
                    f"unchecked:{code}",
                    f"band-4 route `{code}` is not reachable over this model: no constraint "
                    f"it declares has the shape that route guards, over the baseline or any "
                    f"derived boundary candidate",
                    case_kind="unchecked",
                )
            )
    return cases, downs


def enumerate_frontier(
    model: Model, baseline_doc: dict[str, Any], rng: Random | None = None
) -> tuple[list[BoundaryCase], list[NotDerivable]]:
    """Both frontier kinds for one model, in a stable order."""
    rng = rng if rng is not None else Random(0)
    ns_cases, ns_downs = no_subjects_cases(model, baseline_doc, rng)
    un_cases, un_downs = unchecked_cases(model, baseline_doc, rng)
    return ns_cases + un_cases, ns_downs + un_downs
