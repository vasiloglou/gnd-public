"""The fidelity payload: per-fact-type rates, an honest census, and machine-readable
un-publishability (PANEL-1, R-11′, R-13′, D-22).

Four module contracts, re-aimed from ``measure/report.py:1-27`` at this lane:

**Raw evidence, always (D-22).** The payload quotes one VERBATIM extracted fact
from a named case, chosen deterministically and preferring a non-``tp`` outcome:
a bad-looking number is the one nobody audits, so the excerpt shows the most
load-bearing observation rather than a comfortable one.

**No timestamp, byte-reproducible.** Sorted keys, pre-sorted lists, no
``generated_at``. Two ``gnd fidelity`` runs over one case set are byte-identical,
which is what makes a published fidelity number re-derivable by a reader who has
only the committed cases.

**No aggregate figure (D-01).** Nothing here folds fact types together. Counts
are summed across the CASES that ran — that is one row's own evidence — and never
across rows. A single "extraction accuracy" would average the fact types the
extractor found easy over the ones it never attempted.

**Un-publishability is a schema fact (PANEL-1).** ``calibration.state`` is const
``"uncalibrated"``, ``publishable`` is const ``false``, and every object in
``fidelity.schema.json`` is closed so no interval field can exist. The reason
those are CONSTANTS rather than defaults is that **R-06 (cross-family delta) and
R-12 (the N=12 owner-labelled calibration set) are panel-confirmed deferrals**:
this lane has no instrument that could bound its own round-trip bias, because the
renderer authored the ground truth the extractor is scored against. A field a
future caller could flip would be a promise; a const is a refusal. The
uncalibrated/unpublishable pair IS the deferral's stand-in — when R-12 lands,
the schema version bumps and the constants become states.

**And no verdict channel (R-03″).** ``gnd verify`` emits verdicts and never a
rate; ``gnd fidelity`` emits rates and never a verdict, a band or an
``acceptance_ready`` claim. Both directions are pinned by named tests.
"""

from __future__ import annotations

import json  # noqa: F401 -- historical compatibility binding
from collections.abc import Mapping, Sequence
from importlib.resources import files
from typing import Any

from gnd import input_policy as _rf7_input
from gnd import verbalize
from gnd.artifacts import canonical_report_text as canonical  # noqa: F401 -- compatibility
from gnd.fidelity.match import FactTypeMatch
from gnd.model_identity import stable_model_identifier

__all__ = [
    "FIDELITY_SCHEMA_VERSION",
    "CaseOutcome",
    "MixedCaseCorpusError",
    "build_fidelity_payload",
    "load_fidelity_schema",
    "render_fidelity",
    "stable_model_identifier",
]

#: Fidelity payload key-set version. Bump ONLY on a breaking change to the key
#: set or a value's meaning (``report.py``'s ``PAYLOAD_SCHEMA_VERSION`` and
#: ``measure/report.py``'s ``MEASUREMENT_SCHEMA_VERSION`` precedent).
#: /1: the initial contract — per-fact-type rows, the R-13′ census, the PANEL-1
#: calibration block, and `publishable` const false. When R-12's calibration set
#: lands, `calibration.state` stops being a const and this version bumps.
FIDELITY_SCHEMA_VERSION = 2

#: PANEL-1. Structural properties of a round trip that renders from the very
#: population it is later scored against — each one is a reason the number may be
#: too kind, and none of them is quantified in this lane.
#:
#: * ``self-consistency`` — the extractor may agree with the renderer for reasons
#:   unrelated to reading the document.
#: * ``unmentioned-entity-recall`` — an entity the renderer never wrote down
#:   cannot be missed, so recall rises for free.
#: * ``relation-permutation`` — added 2026-08-13 (owner decision, UAT item 1).
#:   ``gnd doccheck``'s mention obligation checks that each role filler's
#:   reference VALUE appears; it cannot check that the document PAIRS those
#:   values as the population does. A renderer that permutes relationships passes
#:   the gate and then depresses fidelity for a reason belonging entirely to the
#:   renderer. Found live in plan 06 (deferred-items FINDING 3), where a draft
#:   document attributed every delivery to the wrong courier and `doccheck`
#:   exited 0.
#:
#: The schema requires each of these and permits more. It was a frozen `const`
#: pair until FINDING 3 produced a bias the payload physically could not name,
#: which pushed it into prose and undercut PANEL-1's own rule that
#: un-publishability is a schema fact. The `const` guarded against a bias being
#: quietly REMOVED to flatter the number; `contains` still guards that, while
#: allowing an addition — and an addition only ever makes the number look worse,
#: so it needs no protection from dishonesty.
UNQUANTIFIED_BIASES = (
    "self-consistency",
    "unmentioned-entity-recall",
    "relation-permutation",
)


class MixedCaseCorpusError(ValueError):
    """The case set spans more than one model (C4's analog). ``gnd fidelity`` is
    model-relative and one payload represents exactly one model; a mixed case
    set is a usage error (the CLI exits 64), never a silently-measured subset.
    """


class CaseOutcome:
    """One case's census state and its evidence row.

    ``state`` is R-13′'s vocabulary: ``ran`` (a valid, digest-bound handoff that
    was matched), ``skipped`` (the INTENTIONAL opt-out marker, with its reason),
    ``failed`` (anything else, with its reason). Absence of files is never
    ``skipped`` — a missing measurement must not look green.
    """

    def __init__(
        self,
        name: str,
        state: str,
        *,
        reason: str | None = None,
        matches: Sequence[FactTypeMatch] = (),
        source_sha256: str | None = None,
        extracted_sha256: str | None = None,
        document_sha256: str | None = None,
        source_facts: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
        extracted_facts: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
    ) -> None:
        self.name = name
        self.state = state
        self.reason = reason
        self.matches = list(matches)
        self.source_sha256 = source_sha256
        self.extracted_sha256 = extracted_sha256
        self.document_sha256 = document_sha256
        self.source_facts = dict(source_facts or {})
        self.extracted_facts = dict(extracted_facts or {})


def load_fidelity_schema() -> dict[str, Any]:
    """The Draft 2020-12 schema describing this payload, resolved through
    ``importlib.resources`` so the contract ships with the installed package
    (the ``report.schema.json`` / ``measurement.schema.json`` precedent).

    Vendored-only at the package root: it describes a runtime OUTPUT contract of
    the ``gnd`` CLI, not an interchange format the gnd-orm-core skill documents
    authoring rules for, so it has no canonical twin and stays out of
    ``SCHEMA_PAIRS`` (``tests/test_schema_sync.py:9-18``).
    """
    schema_text = files("gnd").joinpath("fidelity.schema.json").read_text(
        encoding="utf-8"
    )
    return _rf7_input.loads(schema_text)




# `stable_model_identifier` moved to `gnd.model_identity` in v5.1 Phase 1
# (D-P1.3). The copy that stood here was NOT "unchanged" from measure's, as its
# docstring claimed: it anchored on `Path(__file__).resolve().parents[3]`, the
# installed checkout, where measure anchored on the invocation root. r2 A4
# ruled the invocation root wins, so this is a behaviour change for a fidelity
# payload produced from a checkout other than the invocation directory -- the
# `eaa672a` detached-worktree shape. Re-exported above; one home now.


def _rate_entry(numerator: int, denominator: int) -> dict[str, Any]:
    """``{numerator, denominator, rate}`` — a rate never published alone
    (R-11′). ``rate`` is ``None`` exactly when the denominator is zero."""
    return {
        "numerator": numerator,
        "denominator": denominator,
        "rate": None if denominator == 0 else numerator / denominator,
    }


def _select_excerpt(cases: Sequence[CaseOutcome]) -> dict[str, Any] | None:
    """D-22's verbatim excerpt, chosen deterministically.

    The first RAN case in name order, preferring a fact type whose row carries a
    non-``tp`` outcome — ``measure/report.py:141-162``'s rule, same reasoning:
    the excerpt should show the observation a reader is most likely to want to
    check, and that is never the comfortable one.
    """
    for case in sorted(
        (case for case in cases if case.state == "ran"), key=lambda item: item.name
    ):
        evidence = [
            (match.fact_type_id, item)
            for match in case.matches
            if match.applicable
            for item in match.evidence
        ]
        chosen = next((item for item in evidence if item[1].outcome != "tp"), None)
        chosen = chosen or (evidence[0] if evidence else None)
        if chosen is not None:
            fact_type_id, item = chosen
            return {
                "case": case.name,
                "fact_type": fact_type_id,
                "outcome": item.outcome,
                "source": "extracted",
                "fact": dict(item.fact),
                "reason": None,
            }
        applicable_ids = {
            match.fact_type_id for match in case.matches if match.applicable
        }
        source = next(
            (
                (fact_type_id, facts[0])
                for fact_type_id, facts in sorted(case.source_facts.items())
                if fact_type_id in applicable_ids and facts
            ),
            None,
        )
        if source is not None:
            fact_type_id, fact = source
            return {
                "case": case.name,
                "fact_type": fact_type_id,
                "outcome": "missed",
                "source": "source",
                "fact": dict(fact),
                "reason": None,
            }
        return {
            "case": case.name,
            "fact_type": min(applicable_ids) if applicable_ids else "",
            "outcome": "evidence-unavailable",
            "source": "none",
            "fact": None,
            "reason": "the case ran but neither population contains an applicable fact",
        }
    return None


def build_fidelity_payload(
    model_path: str,
    cases: Sequence[CaseOutcome],
    applicable: Mapping[str, Any],
    *,
    model_sha256: str,
    applicable_sha256: str,
    projection_sha256: str,
    gnd_version: str,
) -> dict[str, Any]:
    """Assemble the fidelity payload from matched cases.

    Counts are summed over the cases that RAN. Skipped and failed cases enter
    the census and nothing else — folding a failed extraction in as "found
    nothing" would lower every rate and hide the failure INSIDE the number,
    which is the same move as dropping it entirely, differently disguised.

    Emits no timestamp and pre-sorted lists so two runs reproduce byte-for-byte.
    """
    ran = [case for case in cases if case.state == "ran"]

    rows_by_id: dict[str, dict[str, Any]] = {}
    for row in applicable["fact_types"]:
        fact_type_id = str(row["id"])
        rows_by_id[fact_type_id] = {
            "id": fact_type_id,
            "applicable": bool(row["applicable"]),
            "reason": row["reason"],
            "matched": {
                "source_total": 0,
                "extracted_total": 0,
                "tp": 0,
                "missed": 0,
                "unmatched": 0,
                "unresolved": 0,
                "ambiguous": 0,
            },
        }

    for case in ran:
        for match in case.matches:
            counters = rows_by_id[match.fact_type_id]["matched"]
            counters["source_total"] += match.source_total
            counters["extracted_total"] += match.extracted_total
            counters["tp"] += match.tp
            counters["missed"] += match.missed
            counters["unmatched"] += match.unmatched
            counters["unresolved"] += match.unresolved
            counters["ambiguous"] += match.ambiguous

    per_fact_type: list[dict[str, Any]] = []
    for fact_type_id in sorted(rows_by_id):
        row = rows_by_id[fact_type_id]
        counters = row["matched"]
        # INCLUSIVE precision (PANEL-5): the denominator is every extracted
        # fact, unresolved and ambiguous ones included.
        row["precision"] = _rate_entry(counters["tp"], counters["extracted_total"])
        row["recall"] = _rate_entry(counters["tp"], counters["source_total"])
        row["unresolved"] = _rate_entry(
            counters["unresolved"], counters["extracted_total"]
        )
        per_fact_type.append(row)

    reasons = sorted(
        (
            {
                "case": case.name,
                "state": case.state,
                "reason": case.reason or "",
            }
            for case in cases
            if case.state in ("skipped", "failed")
        ),
        key=lambda entry: entry["case"],
    )

    return {
        "schema_version": FIDELITY_SCHEMA_VERSION,
        "tool": "gnd",
        "command": "fidelity",
        "gnd_version": gnd_version,
        "model": {
            "id": stable_model_identifier(model_path),
            "sha256": model_sha256,
        },
        "artifacts": {
            "applicable_sha256": applicable_sha256,
            "projection_sha256": projection_sha256,
        },
        "cases": {
            "ran": len(ran),
            "skipped": sum(1 for case in cases if case.state == "skipped"),
            "failed": sum(1 for case in cases if case.state == "failed"),
            "reasons": reasons,
        },
        "per_fact_type": per_fact_type,
        "calibration": {
            "state": "uncalibrated",
            "unquantified_biases": list(UNQUANTIFIED_BIASES),
        },
        "publishable": False,
        "evidence": {
            "cases": [
                {
                    "case": case.name,
                    "state": case.state,
                    "source_population_sha256": case.source_sha256,
                    "extracted_population_sha256": case.extracted_sha256,
                    "document_sha256": case.document_sha256,
                }
                for case in sorted(cases, key=lambda item: item.name)
            ],
            "excerpt": _select_excerpt(cases),
        },
    }


def _format_rate(entry: Mapping[str, Any]) -> str:
    rate = entry["rate"]
    shown = "n/a" if rate is None else f"{rate:.4f}"
    return f"{shown} ({entry['numerator']}/{entry['denominator']})"


def render_fidelity(payload: Mapping[str, Any]) -> str:
    """The text rendering: the census FIRST, then one line per fact type.

    The census leads because a rate whose case set half failed is not the same
    number as one whose case set ran, and the reader must see which before
    reading any rate at all. The un-publishability line closes the report for
    the same reason.
    """
    census = payload["cases"]
    lines = [
        (
            f"fidelity for {verbalize.path_segment(payload['model']['id'])} "
            f"(sha256 {verbalize.path_segment(payload['model']['sha256'][:12])})"
        ),
        (
            f"cases: ran={census['ran']} skipped={census['skipped']} "
            f"failed={census['failed']}"
        ),
    ]
    for entry in census["reasons"]:
        lines.append(
            f"  {entry['state']}: {verbalize.path_segment(entry['case'])} — "
            f"{verbalize.path_segment(entry['reason'])}"
        )
    lines.append("")
    for row in payload["per_fact_type"]:
        if not row["applicable"]:
            lines.append(
                f"{verbalize.path_segment(row['id'])}: not-applicable — "
                f"{verbalize.path_segment(row['reason'])}"
            )
            continue
        matched = row["matched"]
        lines.append(
            f"{verbalize.path_segment(row['id'])}: "
            f"precision={_format_rate(row['precision'])} "
            f"recall={_format_rate(row['recall'])} "
            f"unresolved={_format_rate(row['unresolved'])} "
            f"[tp={matched['tp']} missed={matched['missed']} "
            f"unmatched={matched['unmatched']} ambiguous={matched['ambiguous']}]"
        )
    lines.append("")
    lines.append(
        f"calibration: {payload['calibration']['state']}; unquantified biases: "
        f"{', '.join(payload['calibration']['unquantified_biases'])}"
    )
    lines.append(
        f"publishable: {str(payload['publishable']).lower()} — the round trip "
        f"measures the round trip; R-06/R-12 are deferred, so no bound on that "
        f"bias exists"
    )
    return "\n".join(lines)
