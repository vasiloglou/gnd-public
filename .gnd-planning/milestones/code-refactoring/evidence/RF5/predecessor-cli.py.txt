"""``gnd`` CLI: validate models and check populations.

The supported interface is the ``gnd`` console script installed from the
``get-nick-done`` distribution (PKG-01). ``python -m gnd`` keeps working and
``__main__.py`` is untouched (D-03), but it is a development convenience rather
than the documented entry point. Both reach ``main()``; the generated console
wrapper calls ``sys.exit(main())``, so the ``int`` return below IS the process
exit code and the bands are preserved on either path.

Exit-code bands (SKELETON.md, normative) — 0/1/2/3/4:
- 0: pass — accepted. Deontic warnings and *deontic* ``unchecked`` verdicts are
  allowed here; an ALETHIC ``unchecked`` verdict is NOT (see band 4).
- 1: any alethic ``fail`` — violated
- 2: no alethic fail, but any ``vacuous`` — inadequate
- 3: model or population failed to load/validate — ill-formed
- 4: any alethic constraint carries an ``unchecked`` verdict — indeterminate
  (D-07). The checker never mechanically evaluated a constraint that IS the
  acceptance contract, so acceptance cannot be claimed. Distinct from band 2:
  vacuous is a *decided* state (evaluated, no subjects), indeterminate means
  the machinery never ran.

Band precedence is 3 > 1 > 4 > 2 > 0 (D-08): a definite failure is the most
actionable signal, and indeterminate outranks vacuous. ``acceptance_ready`` is
true only at exit 0.

Non-band exit codes (WR-03 — never collide with the 0-4 band contract):
- 64 (EX_USAGE): malformed invocation (argparse usage error). argparse's
  default ``SystemExit(2)`` would masquerade as "vacuous population" to retry
  loops keying on the bands. Exit 64 deliberately emits NO ``--format json``
  payload: the format flag is not known until ``parse_args()`` returns, and a
  malformed invocation is a harness error rather than a verdict. Do not "fix"
  this.
- 66 (EX_NOINPUT): a REQUIRED input artifact is missing, so an obligation cannot
  be checked at all. Fail-closed (D-22): a check that cannot run is never
  skipped, because a skipped obligation reads as a discharged one. Returning 3
  would masquerade as "a document failed to load", sending the user to inspect a
  file that does not exist; returning 0 would publish coverage the run never had.
  Named as :data:`EXIT_NO_INPUT` since plan 03-01 — it shipped as five raw
  integer literals, which meant a disjointness proof performed by grepping
  ``EXIT_[A-Z_]* *=`` missed it entirely and could have re-allocated 66 to a new
  command.
- 70 (EX_SOFTWARE): internal checker error. An uncaught traceback's default
  exit 1 would masquerade as "alethic fail".

Lifecycle exit codes (``install``, and ``doctor``/``uninstall`` when they land).
**5 through 9 are left deliberately unallocated** as headroom for future verdict
bands, which is why the lifecycle vocabulary starts at 10 and can never be
mistaken for a verdict:

- 10 (EXIT_DRIFT): one or more placed assets are stale, missing, or modified.
  Returning 1 for "some skills are stale" would read as "alethic constraint
  violated" to any retry loop keying on the bands. Reported by ``doctor``, never
  by ``install`` — install *repairs* drift, so drift is not an install outcome.
  That invariant is load-bearing and used to be false for one whole drift state:
  a file a new version stopped shipping was skipped by ``install`` and carried
  into the rewritten receipt, so ``install`` said "already current" at exit 0
  while ``doctor`` said drift at exit 10, permanently. ``install`` now prunes
  such an orphan when its bytes still match what GND placed (CR-04), which is
  what makes this sentence true rather than aspirational. A ``modified`` asset
  is still never touched by ``install``; the repair for that one is the user's.
- 11 (EXIT_COLLISION): an unmanaged file blocked a write. **Nothing was
  destroyed**; re-run with ``--force`` to replace it. Returning 3 here would
  masquerade as "model or population failed to load", sending a user to inspect
  a YAML file over a filesystem conflict.
- 12 (EXIT_NO_INSTALL): no install manifest at any resolved target root. Distinct
  from 0: "nothing to do because everything is current" and "nothing to do
  because nothing was ever installed" are opposite diagnoses, and returning 0
  would let ``uv tool upgrade get-nick-done && gnd install --sync`` report
  success on a machine where the skills were never placed.
- 13 (EXIT_MODEL_CODE_DRIFT): a generated project no longer agrees with the
  model it was generated from — a derived file was edited, a derived file is
  gone, or the model moved and the code did not. Returning 1 would masquerade
  as "an alethic constraint was violated" to any retry loop keying on the
  bands, sending a harness to inspect a population over a stale file; returning
  10 would collide with ``doctor``'s ASSET drift, whose subject (skills placed
  in an agent's directory) and repair (re-install) are unrelated — one number
  meaning two different drifts is D-01's blending error arriving in the
  exit-code contract, and it would be discovered by whoever writes the first CI
  job branching on it. It belongs in the lifecycle register opened at 10 rather
  than in 5-9 because model-code drift is an outcome about ARTIFACTS, not a
  verdict about a population, and 5-9 stay reserved as verdict-band headroom.
  **ONE band for the whole command, not one per assertion.** Splitting into
  13/15/16 for integrity/currency/structure would put in the exit code what
  belongs in the payload, and a CI job branching on three drift codes is
  strictly worse than one branching on a code and reading `findings[].kind`.
  ``doctor``'s single code 10 covering five asset states is the shipped
  precedent.
- 14 (EXIT_EXPERIMENT_OPEN): an experiment's obligations are not discharged — a
  declared question left unresolved, an orphan answer to a question nobody
  asked, an unresolvable evidence pointer, an unresolved ``follows:`` reference,
  or a codegen experiment whose conformance did not pass. Returning 1 would
  masquerade as "alethic constraint violated" to any retry loop keying on the
  bands, sending a harness to inspect a population over an unwritten conclusion;
  returning 10 would collide with ``doctor``'s ASSET drift, whose repair
  (re-install) is unrelated. It belongs in the lifecycle register opened at 10
  rather than in 5-9, because a refused close is an outcome about ARTIFACTS, not
  a verdict about a population — and 5-9 stay reserved as verdict-band headroom.
- 15 (EXIT_SESSION_NOT_ACCEPTED): a data-driven experiment session completed
  its one bounded attempt without establishing exact required-case acceptance.
  Returning a child verifier's 1-4 would masquerade as a direct population
  verdict and hide the session lifecycle claim; returning 14 would conflate a
  run outcome with the separate completeness-based experiment close gate. It is
  one lifecycle result for agent failure, verifier failure, and exhausted
  acceptance alike; ``result.json`` carries the precise disposition.
- 16 (EXIT_REVIEW_INCONCLUSIVE): a structurally valid, fully completed
  six-reviewer panel established fewer than three DISTINCT schema-valid
  successes, so no panel result may be reported (D-20). It is a claim about the
  PANEL, never about a reviewed artifact. Returning 1 would masquerade as
  "alethic constraint violated" to any retry loop keying on the bands, sending a
  harness to inspect a population over an absent reviewer; returning 3 would
  masquerade as "the reviewed document failed to load", sending a reader to
  inspect a file that parsed perfectly and was never the problem; returning 0
  would publish consensus the run never had, which is precisely the quorum
  mirage the three-reviewer rule exists to forbid. It never covers a run that
  did not finish: a panel that could not spawn, publish, or read its evidence
  returns its own I/O or internal band, and 16 is reached only after all six
  attempts structurally completed and every failure envelope was retained.
  ONE band for the whole command — a below-quorum panel and a below-quorum
  finalization are the same fact about the same run, and ``run.json`` carries
  every per-reviewer status a consumer needs to branch on.
- 74 (EX_IOERR): the target could not be read or written as required — permission
  denied, an unwritable root, a partial write, an unreadable install receipt, or
  a path refused by the traversal guard. Returning 70 would masquerade as an
  internal checker bug and send the user to file an issue over a chmod.

Also avoided: 125-128 and 128+n, which are shell- and signal-reserved.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import os
import re
import shutil
import stat
import sys
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, get_args

from jsonschema import Draft202012Validator

from gnd import api as api_module
from gnd import exits as exits_module
from gnd import install as install_module
from gnd import report as report_module
from gnd import resolve_version, solve, transition, verbalize
from gnd.checker import CheckReport, check, check_with_anchors
from gnd.checker import band as checker_band
from gnd.exits import (
    EXIT_CHECKER_DEFECT,
    EXIT_COLLISION,
    EXIT_DRIFT,
    EXIT_EVOLUTION_OPERATIONS_GATED,
    EXIT_EXPERIMENT_OPEN,
    EXIT_GENERATOR,
    EXIT_INTERNAL,
    EXIT_IO,
    EXIT_MODEL_CODE_DRIFT,  # noqa: F401 -- compatibility
    EXIT_NO_INPUT,
    EXIT_NO_INSTALL,
    EXIT_QUARANTINE,
    EXIT_REVIEW_INCONCLUSIVE,
    EXIT_SESSION_NOT_ACCEPTED,
    EXIT_USAGE,
    EXIT_WALK_HALTED,  # noqa: F401 - retained as the historical cli-level re-export
)
from gnd.model import (
    Model,
    ModelValidationError,
    ValidationIssue,
    derivation_classifications,
    load_model,
    structured_derivation_ids,
)
from gnd.population import PopulationValidationError, load_population
from gnd.review.constants import REVIEW_QUORUM
from gnd.semantic_registry import capture_branches

_DEFAULT_CHECK = check

# EXIT_USAGE (64), EXIT_NO_INPUT (66) and EXIT_INTERNAL (70) are imported from
# gnd.exits at the top of this module: gnd/solve.py needs the same bands, and
# because cli imports solve the reverse import is circular. Their justification
# prose moved with them. See gnd/exits.py.

# Exit allocations and their rationale live in gnd.exits.


def _session_result_exit(result: Any) -> int:
    from gnd.exp.session_store import SessionOutcome

    return 0 if result.disposition is SessionOutcome.accepted else EXIT_SESSION_NOT_ACCEPTED


CLI_TEST_ARGV_REQUIRED_REASON = "cli:test-argv-required"
CLI_TEST_ARGV_FORBIDDEN_REASON = "cli:test-argv-forbidden"
CLI_WORK_COVERS_REQUIRED_REASON = "cli:work-covers-required"
KIND_AUTHOR_EXPECTATION_TESTS_REASON = "kind:author-expectation-tests"

#: Rendering formats. An invalid choice routes through _BandSafeParser.error()
#: to exit 64, which emits no payload — see the module docstring.
OUTPUT_FORMATS = ("text", "json")


class IndexValidationError(ValueError):
    """The synthesis corpus manifest is not a supported closed document."""


_INDEX_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["populations", "not_derivable"],
    "properties": {
        "populations": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "population",
                    "sidecar",
                    "seed",
                    "band",
                    "class",
                    "case_kind",
                ],
                "properties": {
                    "population": {"type": "string", "minLength": 1},
                    "sidecar": {"type": "string", "minLength": 1},
                    "seed": {"type": "integer"},
                    "band": {"type": "integer", "minimum": 0, "maximum": 4},
                    "class": {
                        "enum": [
                            "conforming",
                            "boundary",
                            "violating",
                            "no-subjects",
                            "unchecked",
                        ]
                    },
                    "case_kind": {
                        "enum": [
                            "conforming",
                            "boundary",
                            "violating",
                            "no-subjects",
                            "unchecked",
                        ]
                    },
                    "operator": {"type": "string", "minLength": 1},
                    "boundary_side": {"type": "string", "minLength": 1},
                    "epsilon": {"type": ["number", "string", "null"]},
                    "target": {"type": "string", "minLength": 1},
                    "predicted_verdict": {
                        "enum": ["pass", "warning", "fail", "vacuous", "unchecked"]
                    },
                    "violates_target": {"type": "string", "minLength": 1},
                    "violates": {
                        "type": "array",
                        "items": {"type": "string", "minLength": 1},
                        "uniqueItems": True,
                    },
                    "isolating": {"type": "boolean"},
                    "isolation_verified": {"type": "boolean"},
                    "baseline_seed": {"type": "integer"},
                },
            },
        },
        "not_derivable": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["constraint_ref", "family", "operator", "mechanism"],
                "properties": {
                    "constraint_ref": {"type": "string"},
                    "family": {"type": "string"},
                    "operator": {"type": ["string", "null"]},
                    "mechanism": {"type": "string"},
                    "case_kind": {"type": "string"},
                    "side": {"type": "string"},
                },
            },
        },
    },
}
_INDEX_VALIDATOR = Draft202012Validator(_INDEX_SCHEMA)


def _validate_index_document(document: Any) -> dict[str, Any]:
    """Validate and return one synthesis ``index.json`` document.

    The index is untrusted corpus input.  Keeping this schema closed prevents a
    malformed record from becoming an ``AttributeError``/``KeyError`` whose
    process exit 1 is indistinguishable from an alethic checker failure.
    """
    errors = sorted(_INDEX_VALIDATOR.iter_errors(document), key=lambda error: list(error.path))
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        raise IndexValidationError(f"index.json at {location}: {error.message}")
    return document


class _BandSafeParser(argparse.ArgumentParser):
    """Usage errors exit 64 (EX_USAGE), not argparse's default 2 — exit 2 is
    the normative "vacuous population" band (WR-03)."""

    def error(self, message: str) -> None:  # type: ignore[override]
        self.print_usage(sys.stderr)
        print(f"{self.prog}: error: {message}", file=sys.stderr)
        raise SystemExit(EXIT_USAGE)


class _StoreOnce(argparse.Action):
    """Refuse a second occurrence of a single-valued flag.

    argparse's default is last-wins, which lets a user believe a bound was set
    that never was. A second occurrence is a user error, never a silent
    overwrite -- and it reaches 64 through _BandSafeParser.error like every other
    usage refusal.
    """

    def __call__(self, parser, namespace, values, option_string=None):  # type: ignore[no-untyped-def]
        if getattr(namespace, f"_seen_{self.dest}", False):
            parser.error(f"{option_string} may be given at most once")
        setattr(namespace, f"_seen_{self.dest}", True)
        setattr(namespace, self.dest, values)


def _positive_int(value: str) -> int:
    """Argparse converter for counts that must be strictly positive."""
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def _positive_finite_float(value: str) -> float:
    """Argparse converter for positive finite wall-clock tightenings."""

    parsed = float(value)
    if parsed <= 0 or not math.isfinite(parsed):
        raise argparse.ArgumentTypeError("must be finite and greater than zero")
    return parsed


def _print_issues(issues: list[ValidationIssue]) -> None:
    """Render structured validation issues. Widened from ModelValidationError so
    the population loader's issues (D-04) reach the same renderer rather than
    being flattened into a summary string.

    Capped at ``report.MAX_POPULATION_ISSUES`` (WR-01). That bound used to apply
    only where issues were SERIALIZED, so the JSON payload for a systematically
    malformed 3.1 MB population was a correct 63 KB while this renderer wrote
    32 MB — a 10x amplification of the input, and ~100 MB of stdout at the 10 MB
    file cap. Bound every untrusted-input-proportional resource where it is
    PRODUCED, not only where it is serialized. The elision is reported, never
    silent, exactly as ``issues_truncated`` is in the payload."""
    shown = issues[: report_module.MAX_POPULATION_ISSUES]
    for issue in shown:
        print(f"ERROR at {issue.path}: {issue.message} [{issue.rule_id}]")
    if len(issues) > len(shown):
        print(
            f"... and {len(issues) - len(shown)} further issue(s) elided "
            f"(cap {report_module.MAX_POPULATION_ISSUES}); use --format json for "
            f"the machine-readable payload, which reports issues_total."
        )


def _print_trace(model: Model, model_path: str) -> None:
    """What a transition run WOULD evaluate. Reporting only (D6).

    It exists on `validate` and not on `check` because `check` returns a
    verdict, and a flag meaning "report instead of decide" does not belong on a
    command whose job is to decide. It cannot be dropped for size either: it is
    the only surface that emits `operations_digest`, and a required field no
    command produces is a format defect.
    """
    print("TRACE")
    print(f"  model_digest      {transition.transition_model_identity(model)}")
    print(f"  operations_digest {transition.operations_digest(model.operations)}")

    print("COMPILED OBLIGATIONS")
    any_compiled = False
    for operation in model.operations:
        op_id = str(operation.get("id"))
        for entry in model.compiled_obligations(op_id):
            if not entry.get("subset"):
                continue
            any_compiled = True
            subset = entry["subset"]
            print(
                f"  [{entry['modality']}] {verbalize.path_segment(op_id)}."
                f"{verbalize.path_segment(str(entry['obligation']))} -> "
                f"every {verbalize.path_segment(str(subset['of']))} fact has a "
                f"matching {verbalize.path_segment(str(subset['in']))} fact"
            )
            print(f"      {entry['locator']}")
    if not any_compiled:
        print("  (none)")

    print("RETAINED (transition-only)")
    any_retained = False
    for operation in model.operations:
        op_id = str(operation.get("id"))
        for entry in model.compiled_obligations(op_id):
            reason = entry.get("transition-only")
            if not reason:
                continue
            any_retained = True
            print(
                f"  {verbalize.path_segment(op_id)}."
                f"{verbalize.path_segment(str(entry['obligation']))}: "
                f"transition-only: {verbalize.line_text(str(reason))}"
            )
    if not any_retained:
        print("  (none)")

    print("DERIVATION STABILITY")
    classifications = derivation_classifications(model.model_dump())
    for classification in classifications:
        dependencies = ", ".join(
            verbalize.path_segment(dependency)
            for dependency in classification.asserted_dependencies
        )
        print(
            f"  {verbalize.path_segment(classification.fact_type)}: "
            f"{classification.stability} (dependencies: {dependencies})"
        )
    if not classifications:
        print("  (none)")

    print("FRAME MODALITY BY FACT TYPE")
    # Over EVERY operation, because no walk has been supplied: this is what the
    # model would produce, and a walk narrows it to the fact types it touches.
    grading = transition.frame_modalities(model)
    for fact_type_id in sorted(grading):
        modality, operations = grading[fact_type_id]
        names = ", ".join(verbalize.path_segment(name) for name in operations)
        print(f"  {verbalize.path_segment(fact_type_id)}: {modality} ({names})")
    if not grading:
        print("  (none)")


def _print_projected_text(payload: dict[str, Any]) -> None:
    """Render only the already-projected tree on declaration-bearing routes."""

    from gnd.redaction import render_text_header

    header = render_text_header(payload)
    if header is None:
        raise ValueError("projected text requires redaction metadata")
    print(header)
    transition_block = payload.get("transition")
    if isinstance(transition_block, dict):
        for step in transition_block.get("steps") or []:
            changes = step.get("derived_changes") if isinstance(step, dict) else None
            if not changes:
                continue
            print(
                f"STEP {step.get('index')} ({verbalize.path_segment(str(step.get('operation')))})"
            )
            _print_derived_change_summaries(changes)
    print(report_module.render_json(payload))


def _cmd_validate(
    model_path: str,
    output_format: str,
    *,
    trace: bool = False,
    unredacted: bool = False,
) -> int:
    result = api_module._run_validate(model_path, unredacted=unredacted)
    if output_format == "json":
        try:
            report_module.emit(result.payload)
        except report_module.NonJsonValueError as error:
            fallback = report_module.build_validate_payload(
                EXIT_INTERNAL,
                model_path,
                schema_version=result.payload["schema_version"],
                error=error,
            )
            report_module.emit(fallback)
            return EXIT_INTERNAL
        return result.exit_code
    mechanical_payload = result.payload.get("report", result.payload)
    if "redaction" in mechanical_payload:
        if trace and result.model is not None and not result.issues and result.error is None:
            _print_trace(result.model, model_path)
        _print_projected_text(mechanical_payload)
        return result.exit_code
    for warning in result.warnings:
        print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")
    if result.issues:
        _print_issues(list(result.issues))
        return result.exit_code
    if result.error is not None:
        prefix = "INTERNAL ERROR" if result.exit_code == EXIT_INTERNAL else "ERROR"
        print(f"{prefix}: {result.error}")
        return result.exit_code
    if trace:
        _print_trace(result.model, model_path)
    print(f"OK: {model_path} is a valid GND ORM model")
    return result.exit_code


def _cmd_coverage(
    model_path: str,
    experiments: list[str],
    check_sources: list[str],
    verify_sources: list[str],
    conformance_sources: list[str],
    transition_sources: list[str],
    output_format: str,
) -> int:
    """Compute the read-only element roadmap; never write an artifact."""

    from gnd.coverage import (
        CoverageInputError,
        CoverageMissingError,
        CoveragePathError,
        build_coverage,
        build_payload,
        canonical_payload,
        guard_named_source,
        render_coverage,
    )

    model_file = Path(model_path)
    try:
        guard_named_source(model_file, directory=False)
        model = load_model(model_file)
    except CoverageMissingError as error:
        print(f"MISSING: {error}")
        return EXIT_NO_INPUT
    except CoveragePathError as error:
        print(f"IO ERROR: {error}")
        return EXIT_IO
    except ModelValidationError as error:
        _print_issues(error.issues)
        return 3
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"ERROR: {error}")
        return 3

    try:
        result = build_coverage(
            model,
            model_path=model_path,
            experiments=[Path(path) for path in experiments],
            check=[Path(path) for path in check_sources],
            verify=[Path(path) for path in verify_sources],
            conformance=[Path(path) for path in conformance_sources],
            transition=[Path(path) for path in transition_sources],
        )
    except CoverageMissingError as error:
        print(f"MISSING: {error}")
        return EXIT_NO_INPUT
    except CoveragePathError as error:
        print(f"IO ERROR: {error}")
        return EXIT_IO
    except CoverageInputError as error:
        print(f"ERROR: {error}")
        return 3

    payload = build_payload(result, gnd_version=resolve_version())
    if output_format == "json":
        print(canonical_payload(payload))
    else:
        print(render_coverage(payload), end="")
    return 0


def _constraint_verdict_line(verdict: Any, indent: str = "  ") -> str:
    """ONE rendering of a constraint verdict, for every surface that prints one.

    Extracted by the phase-2 refactoring review (protocol section 8, step 5).
    There were two copies here -- the blocking and advisory arms below print the
    same three fields the same way -- and the transition arm was about to add a
    third. Three copies of a line is how a format drifts between the report a
    reader sees for a snapshot check and the one they see for a walk, over the
    same underlying verdict.
    """
    return (
        f"{indent}[{verdict.verdict}] {verbalize.path_segment(verdict.constraint_ref)}: "
        f"{verbalize.line_text(verdict.message)}"
    )


def _derivation_verdict_lines(
    verdict: Any,
    indent: str = "  ",
) -> list[str]:
    """Render one derivation obligation and its ordered findings."""

    lines = [
        (
            f"{indent}[{verdict.verdict}] "
            f"{verbalize.path_segment(verdict.derivation_ref)}: "
            f"{verbalize.line_text(verdict.message)}"
        )
    ]
    lines.extend(
        f"{indent}  [{finding.kind}] {verbalize.line_text(finding.message)}"
        for finding in verdict.findings
    )
    return lines


def _print_report(report: CheckReport) -> None:
    blocking = [
        verdict
        for verdict in report.verdicts
        if verdict.modality == "alethic" and verdict.verdict != "pass"
    ]
    advisory = [
        verdict
        for verdict in report.verdicts
        if verdict.modality == "deontic" and verdict.verdict != "pass"
    ]

    print("BLOCKING (alethic)")
    if blocking:
        for verdict in blocking:
            print(_constraint_verdict_line(verdict))
    else:
        print("  (none)")

    print("ADVISORY (deontic)")
    if advisory:
        for verdict in advisory:
            print(_constraint_verdict_line(verdict))
    else:
        print("  (none)")

    if report.derivations:
        print("DERIVATIONS (alethic)")
        for verdict in report.derivations:
            for line in _derivation_verdict_lines(verdict):
                print(line)

    counts = report.counts()
    print(
        f"pass={counts['pass']} fail={counts['fail']} warning={counts['warning']} "
        f"unchecked={counts['unchecked']} vacuous={counts['vacuous']}"
    )

    if report.coverage:
        print("COVERAGE")
        for fact_type_id, entry in report.coverage.items():
            print(
                f"  {verbalize.path_segment(fact_type_id)}: {entry.declared}, facts={entry.facts}"
            )


def _band(report: CheckReport) -> int:
    """Delegate to :func:`gnd.checker.band` — the ONE owner of the exit-band rule.

    Band 3 returns earlier from the load arms, so it never reaches here. The
    precedence 3 > 1 > 4 > 2 > 0 (D-08) lives in ``checker.band`` so the Phase 2/4
    measurement harness reads the same rule the CLI does — a second copy is how
    exit bands drift apart.
    """
    return checker_band(report)


def _print_transition(
    walk: Any, warnings: list[ValidationIssue], *, computed_post: dict[str, Any] | None = None
) -> None:
    """Text rendering: four families, printed as four sections and never merged.

    A reader who wants one number reads the exit code; a reader who wants to fix
    something needs to know WHICH family found it, because a pre-state defect
    and an undeclared side effect call for entirely different work.
    """
    for warning in warnings:
        print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")

    def render(verdicts: list[Any], indent: str = "  ") -> None:
        for verdict in verdicts:
            where = verbalize.path_segment(verdict.locator)
            print(f"{indent}[{verdict.verdict}] {where}: {verbalize.line_text(verdict.message)}")

    print("PRE-STATE")
    _print_check_verdicts(walk.pre_snapshot)
    render(walk.pre_snapshot_verdicts)
    for step in walk.steps:
        print(f"STEP {step.index} ({verbalize.path_segment(step.operation)})")
        _print_derived_change_summaries(step.derived_changes)
        render(step.verdicts)
        _print_check_verdicts(step.intermediate, label="  intermediate")
    if computed_post is None:
        print("FRAME")
        for grading in walk.frame_grading:
            print(
                f"  {verbalize.path_segment(grading.fact_type)}: {grading.modality} "
                f"({grading.reason}; {', '.join(map(verbalize.path_segment, grading.operations))})"
            )
        render(walk.frame_verdicts)
    else:
        print("COMPUTED POST")
        print(json.dumps(computed_post, allow_nan=False))
        print("FRAME COMPARISON: not applicable -- post is computed")
    print("POST-STATE")
    _print_check_verdicts(walk.post_snapshot)


def _print_derived_change_summaries(changes: Any) -> None:
    for change in changes or []:
        if isinstance(change, dict):
            fact_type = change.get("fact_type")
            added = change.get("added") or []
            removed = change.get("removed") or []
        else:
            fact_type = change.fact_type
            added = change.added
            removed = change.removed
        print(f"DERIVED {verbalize.path_segment(str(fact_type))}: +{len(added)} -{len(removed)}")


def _print_check_verdicts(report: CheckReport, label: str = "  snapshot") -> None:
    for verdict in report.verdicts:
        if verdict.verdict != "pass":
            print(_constraint_verdict_line(verdict, f"{label} "))


def _live_assurance(
    model, populations, result, band, trace, *, steps=None, extraction_route="not-applicable"
):
    from gnd.assurance_transport import prepare_execution

    block, execution = api_module._certify_assurance(
        model,
        populations,
        result,
        band,
        trace,
        steps=steps,
        extraction_route=extraction_route,
    )
    if execution is not None:
        prepare_execution(execution)
    return block


def _cmd_transition(
    model_path: str,
    pre_path: str,
    steps_path: str,
    post_path: str | None,
    output_format: str,
    *,
    unredacted: bool = False,
) -> int:
    result = api_module._run_transition(
        model_path,
        pre_path,
        steps_path,
        post_path,
        unredacted=unredacted,
    )
    if output_format == "json":
        if result.execution is not None:
            from gnd.assurance_transport import prepare_execution

            prepare_execution(result.execution)
        report_module.emit(result.payload)
        return result.exit_code
    mechanical_payload = result.payload.get("report", result.payload)
    if "redaction" in mechanical_payload:
        _print_projected_text(mechanical_payload)
        return result.exit_code
    if result.report is not None:
        _print_transition(
            result.report,
            list(result.warnings),
            computed_post=(
                result.payload["transition"]["computed_post"] if post_path is None else None
            ),
        )
        return result.exit_code
    for warning in result.warnings:
        print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")
    if result.issues:
        _print_issues(list(result.issues))
    elif result.error is not None:
        prefix = "INTERNAL ERROR" if result.exit_code == EXIT_INTERNAL else "ERROR"
        print(f"{prefix}: {result.error}")
    return result.exit_code


def _cmd_check(
    model_path: str,
    population_path: str,
    output_format: str,
    *,
    unredacted: bool = False,
    anchors_path: str | None = None,
    document_path: str | None = None,
    admission: bool = False,
) -> int:
    result = api_module._run_check(
        model_path,
        population_path,
        unredacted=unredacted,
        evaluator=check if check is not _DEFAULT_CHECK else None,
        anchors=anchors_path,
        document=document_path,
        admission=admission,
    )
    if output_format == "json":
        if result.execution is not None:
            from gnd.assurance_transport import prepare_execution

            prepare_execution(result.execution)
        report_module.emit(result.payload)
        return result.exit_code
    mechanical_payload = result.payload.get("report", result.payload)
    if "redaction" in mechanical_payload:
        _print_projected_text(mechanical_payload)
        if admission:
            _print_admission_text(result.payload.get("report", result.payload))
        return result.exit_code
    if result.report is not None:
        for warning in result.warnings:
            print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")
        _print_report(result.report)
        if admission:
            _print_admission_text(result.payload.get("report", result.payload))
        return result.exit_code
    for warning in result.warnings:
        print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")
    if result.issues:
        _print_issues(list(result.issues))
    elif result.error is not None:
        prefix = "INTERNAL ERROR" if result.exit_code == EXIT_INTERNAL else "ERROR"
        print(f"{prefix}: {result.error}")
    return result.exit_code


def _cmd_verbalize_population(
    model_path: str, population_path: str, output_format: str, *,
    anchors_path: str | None = None, document_path: str | None = None,
    unredacted: bool = False,
) -> int:
    emitter_id = f"cli-population-verbalization-{output_format}"
    result = api_module._run_verbalize(
        model_path, population_path, anchors=anchors_path, document=document_path,
        unredacted=unredacted, emitter_id=emitter_id,
    )
    if result["exit_code"]:
        print(result["error"]["message"], file=sys.stderr)
        return result["exit_code"]
    for row in result["rows"]:
        if output_format == "jsonl":
            print(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            continue
        ref = row["fact_ref"]
        suffix = f" | excerpt: {row['excerpt']}" if "excerpt" in row else ""
        print(f"FACT {verbalize.path_segment(ref['fact_type'])}[{ref['index']}]: {row['sentence']}{suffix}")
    return 0


def _cmd_diff(
    model_a: str, model_b: str, populations: str | None, output_format: str,
    unredacted: bool, seed: int,
) -> int:
    from gnd.diff import DiffError

    try:
        payload = api_module.diff(model_a, model_b, populations=populations,
                                  unredacted=unredacted, seed=seed)
    except (DiffError, ModelValidationError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 3
    except OSError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return EXIT_IO
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"INTERNAL ERROR: {error}", file=sys.stderr)
        return EXIT_INTERNAL
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    else:
        payload = payload["report"] if payload.get("schema_version") == 12 else payload
        print(f"DIFF {payload['model_a_digest']} {payload['model_b_digest']}")
        print(f"Entailment rows: {len(payload['entailment'])}")
        for row in payload["entailment"]:
            print(f"  {row['from_model']}->{row['to_model']} {row['left_ref']} {row['result']}")
        for row in payload["populations"]:
            print(f"POPULATION {row['population_ref']}: A={row['a'].get('band')} B={row['b'].get('band')}")
            for direction in ("a_to_b", "b_to_a"):
                for gap in row[direction]:
                    print(f"  {direction} {gap['target_ref']} {gap['verdict']} {gap['witness_sentence'] or ''}")
        for row in payload["not_derivable"]:
            print(f"NOT DERIVABLE {row['source']}: {row['reason']}")
    return 0


def _print_admission_text(payload: dict[str, Any]) -> None:
    section = payload["admission"]
    for row in section["admitted"]:
        ref = row["fact_ref"]
        print(f"ADMITTED {ref['fact_type']}[{ref['index']}]")
    for row in section["blocked"]:
        ref = row["fact_ref"]
        print(f"BLOCKED {ref['fact_type']}[{ref['index']}]: {', '.join(row['blocked_by'])}")


def _cmd_rai_import(
    model_path: str,
    output_dir: str,
    source_artifact: str,
    source_commit: str | None,
) -> int:
    """Import one admitted RAI ORM document and publish its evidence pair."""

    from gnd.rai_import import (
        RaiImportCollision,
        RaiImportError,
        RaiImportIO,
        RaiImportMissing,
        RaiImportRequest,
        plan_rai_import,
        publish_rai_import,
    )

    request = RaiImportRequest(Path(model_path), Path(output_dir), source_artifact, source_commit)
    try:
        result = plan_rai_import(request)
        publish_rai_import(request, result)
    except RaiImportCollision as error:
        print(error, file=sys.stderr)
        return EXIT_COLLISION
    except RaiImportMissing as error:
        print(error, file=sys.stderr)
        return EXIT_NO_INPUT
    except RaiImportIO as error:
        print(error, file=sys.stderr)
        return EXIT_IO
    except RaiImportError as error:
        print(error, file=sys.stderr)
        return 3
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"INTERNAL ERROR: {type(error).__name__}: {error}", file=sys.stderr)
        return EXIT_INTERNAL
    print(f"IMPORTED {model_path} -> {output_dir}")
    return 0


def _cmd_check_batch(model_path: str, populations_dir: str, *, unredacted: bool = False) -> int:
    """Emit the canonical one-model/many-population matrix."""

    from importlib.resources import files

    from gnd.batch import (
        BatchInternalError,
        BatchIOError,
        BatchMissingError,
        BatchUsageError,
        build_batch_payload,
        canonical_batch_bytes,
        check_population_directory,
    )

    try:
        result = check_population_directory(Path(model_path), Path(populations_dir))
        payload = build_batch_payload(result)
        try:
            batch_model = load_model(model_path)
        except Exception:  # noqa: BLE001 -- preserve predecessor refusal contract
            batch_model = None
        if batch_model is not None:
            from gnd.redaction import RedactionPolicy, project_output

            policy = RedactionPolicy.from_model(batch_model)
            payload = project_output(
                "batch",
                payload,
                policy=policy,
                mode="unredacted" if unredacted else "applied",
                emitter_id="cli-batch-json",
            )
        schema = json.loads(
            files("gnd").joinpath("batch-report.schema.json").read_text(encoding="utf-8")
        )
        Draft202012Validator(schema).validate(payload)
        sys.stdout.buffer.write(canonical_batch_bytes(payload))
        return result.aggregate_exit
    except BatchUsageError as error:
        print(f"gnd check: error: {error}", file=sys.stderr)
        return EXIT_USAGE
    except BatchMissingError as error:
        print(f"gnd check: error: {error}", file=sys.stderr)
        return EXIT_NO_INPUT
    except BatchIOError as error:
        print(f"gnd check: error: {error}", file=sys.stderr)
        return EXIT_IO
    except BatchInternalError as error:
        print(f"INTERNAL ERROR: {error}", file=sys.stderr)
        return EXIT_INTERNAL
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"INTERNAL ERROR: {type(error).__name__}: {error}", file=sys.stderr)
        return EXIT_INTERNAL


def _cmd_verify(
    model_path: str,
    population_path: str,
    sidecar_path: str | None,
    artifacts_dir: str | None,
    no_extraction: bool,
    out: str | None,
    output_format: str,
    *,
    unredacted: bool = False,
) -> int:
    """``gnd verify MODEL POPULATION`` — the full derived verifier (R-03″).

    Composes popvalidate → check over a PRE-EXTRACTED population file. This
    command never calls a model and never orchestrates extraction: the
    skill-to-code handoff is a file on disk plus its sidecar (R-04‴). Its value
    over ``gnd check``: provenance on every verdict plus the always-present
    ``extraction`` metadata block — the extraction state is its OWN channel,
    kept separate from the checker outcome so a checker pass over an
    uncalibrated extraction can never read as proof of faithfulness (PANEL-2),
    and no fidelity rate ever appears in a verify payload (R-03″ hard rule).

    The extraction-state machine (R-13′) runs BEFORE the composition: a failed
    handoff is an ill-formed extraction at exit 3. ``skipped`` is written ONLY
    by the intentional ``--no-extraction`` opt-out; a missing or invalid
    sidecar is ``failed``, never skipped, never silently green (T-02.1-11).
    """
    import hashlib as _hashlib

    schema_version = 7
    model = None
    semantic_trace = set()
    structured = False
    # v5.1 Phase 3: one identity, computed once, reused by every later payload
    # this invocation emits. `None` until a model loads -- a pre-load error has
    # no model identity to claim, so it stays on the frozen version 3 rather
    # than fabricating one (§6.1).
    model_digest: str | None = None

    from gnd.extract.manifest import (
        ManifestError,
        open_manifest_relative_path,
        read_extraction_sidecar,
    )
    from gnd.population import MAX_POPULATION_BYTES, load_population_bytes
    from gnd.synth import paths as _paths

    #: Every schema key present on every verify exit path (state + reason +
    #: sidecar fields or nulls) — check/validate payloads keep `{}` (plan 01).
    extraction: dict[str, Any] = {
        "state": "failed",
        "reason": None,
        "sidecar": None,
        "population_sha256": None,
        "model_sha256": None,
        "projection_sha256": None,
        "document": None,
        "document_sha256": None,
        "skill": None,
        "skill_version": None,
        "executing_model": None,
    }
    verified_population_bytes: bytes | None = None
    verified_document_bytes: bytes | None = None
    verified_population_source: Path | None = None

    def active_redaction() -> bool:
        if model is None:
            return False
        from gnd.redaction import RedactionPolicy

        return RedactionPolicy.from_model(model).active

    def emit(
        exit_code: int,
        *,
        report: CheckReport | None = None,
        issues: list[ValidationIssue] | None = None,
        warnings: list[ValidationIssue] | None = None,
        error: BaseException | None = None,
    ) -> int:
        with capture_branches() as projection_trace:
            payload = report_module.build_verify_payload(
                exit_code,
                model_path,
                population_path,
                extraction=extraction,
                schema_version=schema_version,
                model_digest=model_digest,
                structured=structured,
                report=report,
                issues=issues,
                warnings=warnings,
                error=error,
            )
        if report is not None and model is not None:
            payload["assurance"] = _live_assurance(
                model,
                [population],
                report,
                exit_code,
                semantic_trace | projection_trace,
                extraction_route=("authenticated" if extraction["state"] == "ran" else "skipped"),
            ).as_dict()
        policy = None
        if model is not None:
            from gnd.redaction import (
                RedactionPolicy,
                RedactionProjectionError,
                project_failure,
                project_output,
            )

            policy = RedactionPolicy.from_model(model)
            try:
                if output_format == "json":
                    payload = project_output(
                        "verify",
                        payload,
                        policy=policy,
                        mode="unredacted" if unredacted else "applied",
                        emitter_id="cli-verify-json",
                    )
                else:
                    payload = project_output(
                        "verify",
                        payload,
                        policy=policy,
                        mode="unredacted" if unredacted else "applied",
                        emitter_id="cli-verify-text",
                    )
            except RedactionProjectionError:
                payload = report_module.build_verify_payload(
                    EXIT_INTERNAL,
                    model_path,
                    population_path,
                    extraction=extraction,
                    schema_version=schema_version,
                    model_digest=model_digest,
                    structured=structured,
                    error=RuntimeError("redaction projection failed"),
                )
                payload = project_failure(
                    "verify",
                    payload,
                    policy=policy,
                    mode="unredacted" if unredacted else "applied",
                )
                exit_code = EXIT_INTERNAL
        try:
            rendered = report_module.render_json(payload)
        except report_module.NonJsonValueError as failure:
            # CR-04 — the twin of _cmd_check's fallback, with the extraction
            # block preserved: the fallback carries no verdicts and no issues,
            # so it cannot itself trip the guard.
            payload = report_module.build_verify_payload(
                EXIT_INTERNAL,
                model_path,
                population_path,
                extraction=extraction,
                schema_version=schema_version,
                model_digest=model_digest,
                structured=structured,
                error=failure,
            )
            if policy is not None and policy.active:
                from gnd.redaction import project_failure

                payload = project_failure(
                    "verify",
                    payload,
                    policy=policy,
                    mode="unredacted" if unredacted else "applied",
                )
            rendered = report_module.render_json(payload)
            exit_code = EXIT_INTERNAL
        from gnd.assurance_transport import emit_receipt

        emit_receipt((rendered + "\n").encode("utf-8"))
        if out is not None:
            # The output path comes from argv ONLY, never from any file
            # content, and routes through the one traversal guard.
            try:
                destination = _paths.safe_output_path(Path(out).parent, Path(out).name)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(rendered + "\n", encoding="utf-8")
            except install_module.InstallPathError as failure:
                print(f"ERROR: refused output path: {failure}")
                return EXIT_IO
            except OSError as failure:
                print(f"ERROR: could not write {out}: {failure}")
                return EXIT_IO
        if output_format == "json":
            print(rendered)
        elif "redaction" in payload:
            _print_projected_text(payload)
        return exit_code

    # --- the extraction-state machine (R-13′), before the composition ---
    if no_extraction:
        extraction["state"] = "skipped"
        extraction["reason"] = "extraction opted out (--no-extraction)"
    else:
        resolved_sidecar = (
            Path(sidecar_path)
            if sidecar_path is not None
            else Path(population_path).with_suffix(".extraction.json")
        )
        extraction["sidecar"] = str(resolved_sidecar)
        if not resolved_sidecar.is_file():
            # ABSENCE IS FAILED, never skipped (R-13′/T-02.1-11): a silently
            # lost handoff file must not read as a deliberate opt-out.
            extraction["reason"] = (
                f"no extraction sidecar at {resolved_sidecar} and --no-extraction "
                f"not given — a missing measurement must not look green"
            )
            issue = ValidationIssue(
                path=str(resolved_sidecar),
                message=str(extraction["reason"]),
                rule_id="extraction:sidecar-missing",
            )
            if output_format != "json" and not active_redaction():
                _print_issues([issue])
            return emit(3, issues=[issue])
        try:
            sidecar = read_extraction_sidecar(resolved_sidecar)
        except ManifestError as error:
            extraction["reason"] = f"extraction sidecar is invalid: {error}"
            if output_format != "json" and not active_redaction():
                _print_issues(error.issues)
            return emit(3, issues=error.issues)

        if artifacts_dir is None:
            issue = ValidationIssue(
                path="projection_sha256",
                message=(
                    "--artifacts is required for an extraction handoff so "
                    "projection_sha256 can be verified against actual bytes"
                ),
                rule_id="extraction:binding-mismatch",
            )
            extraction["reason"] = issue.message
            if output_format != "json" and not active_redaction():
                _print_issues([issue])
            return emit(3, issues=[issue])

        projection_rel = f"{_extract_stem(model_path)}.projection.schema.json"
        bundle_issue = _artifact_index_issue(model_path, artifacts_dir, (projection_rel,))
        if bundle_issue is not None:
            _code, message = bundle_issue
            issue = ValidationIssue(
                path="projection_sha256",
                message=message,
                rule_id="extraction:binding-mismatch",
            )
            extraction["reason"] = message
            if output_format != "json" and not active_redaction():
                _print_issues([issue])
            return emit(3, issues=[issue])
        projection_path = Path(artifacts_dir) / (projection_rel)
        try:
            with open_manifest_relative_path(
                resolved_sidecar,
                sidecar.population,
                field="population",
                rule_id="extraction:binding-mismatch",
            ) as (resolved_population, population_stream):
                verified_population_bytes = population_stream.read(MAX_POPULATION_BYTES + 1)
            with open_manifest_relative_path(
                resolved_sidecar,
                sidecar.document,
                field="document",
                rule_id="extraction:binding-mismatch",
            ) as (_document_path, document_stream):
                from gnd.extract.anchors import MAX_DOCUMENT_BYTES

                document_digest = _hashlib.sha256()
                retained_document = bytearray()
                while chunk := document_stream.read(64 * 1024):
                    document_digest.update(chunk)
                    if len(retained_document) <= MAX_DOCUMENT_BYTES:
                        retained_document.extend(chunk[:MAX_DOCUMENT_BYTES + 1 - len(retained_document)])
                verified_document_bytes = bytes(retained_document)
            verified_population_source = resolved_population
            if resolved_population != Path(population_path).resolve(strict=True):
                raise ManifestError(
                    "the sidecar population does not name the POPULATION argument",
                    [
                        ValidationIssue(
                            path="population",
                            message=(
                                f"sidecar resolves population to {resolved_population}, "
                                f"but argv names {Path(population_path).resolve(strict=True)}"
                            ),
                            rule_id="extraction:binding-mismatch",
                        )
                    ],
                )
        except (ManifestError, OSError, ValueError) as error:
            issues = (
                error.issues
                if isinstance(error, ManifestError)
                else [
                    ValidationIssue(
                        path="population",
                        message=f"sidecar paths could not be verified: {error}",
                        rule_id="extraction:binding-mismatch",
                    )
                ]
            )
            extraction["reason"] = "sidecar path binding failed: " + "; ".join(
                issue.message for issue in issues
            )
            if output_format != "json" and not active_redaction():
                _print_issues(issues)
            return emit(3, issues=issues)

        # C6 binding (the measure precedent, T-02.1-10): recompute and compare
        # every digest the sidecar publishes against the actual bytes on disk.
        binding_issues: list[ValidationIssue] = []
        digests: dict[str, str] = {}
        for field, path in (
            ("model_sha256", Path(model_path)),
            ("projection_sha256", projection_path),
        ):
            try:
                digests[field] = _hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError as error:
                binding_issues.append(
                    ValidationIssue(
                        path=field,
                        message=(
                            f"the sidecar's {field} cannot be verified: {path} "
                            f"could not be read ({error})"
                        ),
                        rule_id="extraction:binding-mismatch",
                    )
                )
        assert verified_population_bytes is not None
        digests["population_sha256"] = _hashlib.sha256(verified_population_bytes).hexdigest()
        digests["document_sha256"] = document_digest.hexdigest()
        for field in (
            "population_sha256",
            "model_sha256",
            "projection_sha256",
            "document_sha256",
        ):
            recorded = getattr(sidecar, field)
            actual = digests.get(field)
            if actual is not None and actual != recorded:
                binding_issues.append(
                    ValidationIssue(
                        path=field,
                        message=(
                            f"the sidecar records {field}={recorded} but the "
                            f"file's bytes hash to {actual} — the population "
                            f"is not the extraction this sidecar describes (C6)"
                        ),
                        rule_id="extraction:binding-mismatch",
                    )
                )
        if binding_issues:
            extraction["reason"] = "sidecar binding mismatch: " + "; ".join(
                issue.message for issue in binding_issues
            )
            if output_format != "json" and not active_redaction():
                _print_issues(binding_issues)
            return emit(3, issues=binding_issues)

        extraction.update(
            state="ran",
            reason=None,
            population_sha256=sidecar.population_sha256,
            model_sha256=sidecar.model_sha256,
            projection_sha256=sidecar.projection_sha256,
            document=sidecar.document,
            document_sha256=sidecar.document_sha256,
            skill=sidecar.skill,
            skill_version=sidecar.skill_version,
            executing_model=sidecar.executing_model,
        )

    # --- the existing composition: popvalidate → check → band (R-03″) ---
    try:
        model = load_model(model_path)
    except ModelValidationError as error:
        if output_format != "json" and not active_redaction():
            for warning in error.warnings:
                print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")
            _print_issues(error.issues)
        return emit(3, issues=error.issues, warnings=error.warnings)
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        if output_format != "json" and not active_redaction():
            print(f"ERROR: {error}")
        return emit(3, error=error)

    structured = bool(structured_derivation_ids(model))
    model_digest = transition.transition_model_identity(model)

    try:
        # model= runs layer-2 model-relative validation and stamps the marker
        # check() requires — no flag disables it (D-18), exactly as in check.
        if verified_population_bytes is None:
            population = load_population(population_path, model=model)
        else:
            assert verified_population_source is not None
            population = load_population_bytes(
                verified_population_bytes,
                source=verified_population_source,
                model=model,
            )
    except PopulationValidationError as error:
        warnings = [*model.warnings, *error.warnings]
        if output_format != "json" and not active_redaction():
            for warning in warnings:
                print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")
            _print_issues(error.issues)
        return emit(3, issues=error.issues, warnings=warnings)
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        if output_format != "json" and not active_redaction():
            print(f"ERROR: {error}")
        return emit(3, error=error)

    if extraction["state"] == "ran":
        # PANEL-6 header ownership: compare the complete header to the SAME
        # deterministic template owner used by `gnd extract`. General
        # population validation intentionally permits labels and treats an
        # omitted model_id as a warning, but neither is permitted on this
        # stricter agent-extraction handoff.
        expected_header = _extraction_header_template(model_path, model)
        actual_header: dict[str, Any] = {
            "model": population.model,
            "source": population.source,
            "covers": population.covers,
        }
        if population.model_id is not None:
            actual_header["model_id"] = population.model_id
        if population.label is not None:
            actual_header["label"] = population.label
        header_issues: list[ValidationIssue] = []
        if actual_header != expected_header:
            header_issues.append(
                ValidationIssue(
                    path="population",
                    message=(
                        "the extraction population header must equal the "
                        "deterministic header_template key for key; expected "
                        f"{expected_header!r}, got {actual_header!r}"
                    ),
                    rule_id="extraction:header-mismatch",
                )
            )
        if header_issues:
            extraction["state"] = "failed"
            extraction["reason"] = "header ownership violated (PANEL-6): " + "; ".join(
                issue.message for issue in header_issues
            )
            if output_format != "json" and not active_redaction():
                _print_issues(header_issues)
            return emit(
                3,
                issues=header_issues,
                warnings=[*model.warnings, *population.warnings],
            )

    try:
        with capture_branches() as semantic_trace:
            from gnd.extract.anchors import (
                AnchorError,
                bind_anchors,
                read_anchor_sidecar,
                read_regular_path,
            )
            anchor_path = Path(str(population_path) + ".anchors.json")
            if os.path.lexists(anchor_path):
                anchor_sidecar = read_anchor_sidecar(anchor_path)
                if extraction["state"] != "ran" or verified_document_bytes is None:
                    raise AnchorError("anchor:binding-mismatch: verified document bytes unavailable")
                document_raw = verified_document_bytes
                if verified_population_bytes is None:
                    population_file = Path(population_path)
                    verified_population_bytes = read_regular_path(
                        population_file, label="anchor population", max_bytes=MAX_POPULATION_BYTES,
                    )
                bind_anchors(anchor_sidecar, model, verified_population_bytes, document_raw, population)
                report = check_with_anchors(
                    model, population, anchors=anchor_sidecar, document_bytes=document_raw,
                )
            else:
                report = check(model, population)
            exit_code = _band(report)
    except AnchorError as error:
        return emit(3, error=error)
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        if output_format != "json" and not active_redaction():
            print(f"INTERNAL ERROR: {type(error).__name__}: {error}")
        return emit(EXIT_INTERNAL, error=error)

    # One band decision, delegated to the ONE owner — never re-derived here.
    warnings = [*model.warnings, *population.warnings]

    if output_format != "json" and not active_redaction():
        for warning in warnings:
            print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")
        state = extraction["state"]
        reason = f" ({extraction['reason']})" if extraction["reason"] else ""
        print(f"EXTRACTION: state={state}{reason}")
        _print_report(report)
    return emit(exit_code, report=report, warnings=warnings)


def _extract_stem(model_path: str) -> str:
    """The slugged filename stem the bundle's four files share.

    Thin alias over :func:`gnd.extract.bundle.bundle_stem`, kept because five
    call sites in this module read better with the local name. The RULE has one
    owner (plan 03-04): it used to live here and be re-implemented by hand in
    ``codegen/emit.py``, which is the third-copy outcome G-03′ names.
    """
    from gnd.extract.bundle import bundle_stem

    return bundle_stem(model_path)


def _extraction_header_template(model_path: str, model: Any) -> dict[str, Any]:
    """The extraction population header — see :func:`gnd.extract.bundle.header_template`.

    Alias, not a second implementation. ``codegen/emit.py`` used to import THIS
    private name from ``gnd.cli``, inverting the layering and pulling the whole
    package into the generation lane's offline-scan closure (measured: 21
    modules -> 45). It imports ``gnd.extract.bundle`` directly now.
    """
    from gnd.extract.bundle import header_template

    return header_template(model_path, model)


def _artifact_index_issue(
    model_path: str,
    artifacts_dir: str,
    required_artifacts: tuple[str, ...],
) -> tuple[int, str] | None:
    """Validate the bundle index and every artifact this consumer will read."""
    import hashlib as _hashlib

    root = Path(artifacts_dir)
    index_path = root / f"{_extract_stem(model_path)}.artifacts.json"
    if not index_path.is_file():
        return (
            EXIT_NO_INPUT,
            f"the extraction bundle index at {index_path} does not exist",
        )
    try:
        if index_path.stat().st_size > 1024 * 1024:
            return (3, f"the extraction bundle index at {index_path} exceeds 1 MiB")
        index = json.loads(index_path.read_text(encoding="utf-8"))
        model_actual = _hashlib.sha256(Path(model_path).read_bytes()).hexdigest()
        model_recorded = str(index["model"]["sha256"])
        if model_recorded != model_actual:
            return (
                3,
                (
                    f"the bundle index records model sha256 {model_recorded} but "
                    f"the model bytes hash to {model_actual}"
                ),
            )
        for rel in required_artifacts:
            artifact_path = root / rel
            if not artifact_path.is_file():
                return (
                    EXIT_NO_INPUT,
                    f"the indexed extraction artifact at {artifact_path} is missing",
                )
            recorded = str(index["artifacts"][rel]["sha256"])
            actual = _hashlib.sha256(artifact_path.read_bytes()).hexdigest()
            if recorded != actual:
                return (
                    3,
                    (
                        f"the bundle index records {rel} sha256 {recorded} but "
                        f"the artifact bytes hash to {actual}"
                    ),
                )
    except (OSError, UnicodeDecodeError, ValueError, KeyError, TypeError) as error:
        return (3, f"the extraction bundle index is not verifiable ({error})")
    return None


def _cmd_extract(model_path: str, out_dir: str) -> int:
    """``gnd extract MODEL --out DIR`` — the per-model artifact bundle.

    Everything here is a pure offline function of ``model.orm.yaml`` (R-04'''):
    the projection, the constraint-blind verbalization, the applicable set, and
    the digest index with the PANEL-6 ``header_template``. The executing agent
    (the gnd-extract skill) is the only place a model is ever called.
    """
    import hashlib as _hashlib
    import os
    import tempfile

    from gnd.extract.projection import ProjectionGateError, project
    from gnd.extract.refscheme import applicable_set
    from gnd.extract.vocabulary import render_verbalization
    from gnd.synth import paths as _paths

    try:
        model = load_model(model_path)
        from gnd.terms import require_non_temporal

        require_non_temporal(model, "extract")
    except ModelValidationError as error:
        for warning in error.warnings:
            print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")
        _print_issues(error.issues)
        return 3
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"ERROR: {error}")
        return 3

    try:
        projection = project(model)
    except ProjectionGateError as error:
        # A gate violation here is OUR emitter building a leaking schema — an
        # internal invariant breach in gnd's own derivation, never the caller's
        # input (their model already loaded clean). So EXIT_INTERNAL (70): band
        # 3 would send the user to fix a valid model, and 5 (EXIT_GENERATOR)
        # belongs to the synthesis lane's invariants, not this one.
        print(f"INTERNAL ERROR: {error}")
        return EXIT_INTERNAL

    stem = _extract_stem(model_path)

    def canonical(payload: dict[str, Any]) -> str:
        # Sorted keys + no NaN, so two extracts over one model agree to the
        # byte (measure/report.py:104-110's discipline).
        return (
            json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False)
            + "\n"
        )

    artifacts: dict[str, str] = {
        f"{stem}.projection.schema.json": canonical(projection),
        f"{stem}.verbalization.txt": render_verbalization(model),
        f"{stem}.applicable.json": canonical(applicable_set(model)),
    }

    out_root = Path(out_dir)
    index_rel = f"{stem}.artifacts.json"
    digests: dict[str, str] = {}
    try:
        model_bytes = Path(model_path).read_bytes()
        # Every write routes through the ONE traversal guard (cli.py's synth
        # precedent): output paths come from argv only, never from model or
        # response content (T-02.1-03).
        destinations: dict[str, Path] = {}
        for rel in [*artifacts, index_rel]:
            destinations[rel] = _paths.safe_output_path(out_root, rel)
        artifact_bytes = {rel: text.encode("utf-8") for rel, text in artifacts.items()}
        digests = {rel: _hashlib.sha256(data).hexdigest() for rel, data in artifact_bytes.items()}

        # PANEL-6 header ownership: `model`, `model_id`, `source` and `covers`
        # are set by deterministic code — the caller contract the gnd-extract
        # skill copies VERBATIM and `gnd verify` re-derives and enforces (plan
        # 03). The LLM never chooses header fields (vacuity gaming through
        # omitted coverage).
        header_template = _extraction_header_template(model_path, model)
        index_payload: dict[str, Any] = {
            "gnd_version": resolve_version(),
            "model": {
                "path": Path(model_path).as_posix(),
                "sha256": _hashlib.sha256(model_bytes).hexdigest(),
            },
            "artifacts": {rel: {"sha256": digest} for rel, digest in digests.items()},
            "header_template": header_template,
        }
        bundle_bytes = {
            **artifact_bytes,
            index_rel: canonical(index_payload).encode("utf-8"),
        }

        # Stage the complete bundle beside its destination. Only after every
        # file is durable do artifact replacements begin, with the index last.
        # Consumers require and validate that index, so an interruption during
        # replacement is rejected as a mixed bundle instead of being consumed.
        out_root.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix=f".{out_root.name}.staging-", dir=out_root.parent
        ) as staging_name:
            staging = Path(staging_name)
            for rel, data in bundle_bytes.items():
                staged = staging / rel
                with staged.open("wb") as handle:
                    handle.write(data)
                    handle.flush()
                    os.fsync(handle.fileno())
            staging_fd = os.open(staging, os.O_RDONLY)
            try:
                os.fsync(staging_fd)
            finally:
                os.close(staging_fd)

            out_root.mkdir(parents=True, exist_ok=True)
            for rel in artifacts:
                os.replace(staging / rel, destinations[rel])
            os.replace(staging / index_rel, destinations[index_rel])
            output_fd = os.open(out_root, os.O_RDONLY)
            try:
                os.fsync(output_fd)
            finally:
                os.close(output_fd)
    except install_module.InstallPathError as error:
        print(f"ERROR: refused output path: {error}")
        return EXIT_IO
    except OSError as error:
        print(f"ERROR: could not write the bundle under {out_dir}: {error}")
        return EXIT_IO

    print(f"extracted bundle for {model_path} -> {out_root}")
    for rel in [*digests, index_rel]:
        print(f"  {rel}")
    return 0


def _stale_smoke_modules(root_fd: int | None, project: object) -> frozenset[str]:
    """Smoke-pattern basenames in the project root that this model does not emit.

    One directory listing, no recursion: the emitted smoke module is always at
    the project root, so a match deeper in the tree belongs to the user's own
    layout and is none of codegen's business (v5.1 D-P1.8).
    """
    from fnmatch import fnmatch

    from gnd.codegen.emit import smoke_module_pattern

    if root_fd is None:
        return frozenset()
    emitted = {
        file.relpath
        for file in project.files  # type: ignore[attr-defined]
        if fnmatch(file.relpath, smoke_module_pattern())
    }
    try:
        present = os.listdir(root_fd)
    except OSError:
        return frozenset()
    return frozenset(
        name for name in present if fnmatch(name, smoke_module_pattern()) and name not in emitted
    )


def _cmd_export_pyrel(
    model_path: str, out_path: str, *, duckdb_path: str = ":memory:", connection: str | None = None
) -> int:
    from gnd.export.emit import render_pyrel
    from gnd.export.pyrel_runtime import ExportInputError, write_new

    try:
        source = render_pyrel(Path(model_path), duckdb_path=duckdb_path, connection=connection)
    except FileNotFoundError as error:
        print(f"missing input: {error}", file=sys.stderr)
        return EXIT_NO_INPUT
    except ExportInputError as error:
        print(f"invalid model: {error}", file=sys.stderr)
        return 3
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"export failed: {error}", file=sys.stderr)
        return EXIT_INTERNAL
    try:
        write_new(Path(out_path), source)
    except FileExistsError as error:
        print(f"output exists: {error}", file=sys.stderr)
        return EXIT_COLLISION
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"output failure: {error}", file=sys.stderr)
        return EXIT_INTERNAL
    print(f"Exported PyRel program to {out_path}")
    return 0


def _cmd_codegen(model_path: str, out_dir: str, *, force: bool = False) -> int:
    """``gnd codegen MODEL --out DIR [--force]`` — the model becomes a project.

    GEN-01's emitter. The generated project has the GND shape (G-01): tools
    derived from the model's fact types, a code-emitted ``SKILL.md`` the terminal
    agent runs, and the shipped ``gnd verify`` as its verifier half — so it is
    CI-runnable with zero network and no API key. Everything here is an offline
    function of ``model.orm.yaml``.

    **Two write paths, and the split is deliberate.** A FRESH target (absent or
    empty, with no codegen manifest) is published by ``write_project``: the whole
    tree is staged, fsynced, and swapped in with one ``os.replace``, so a crash
    leaves nothing at all — strictly stronger than ordering. An EXISTING codegen
    project goes through the six-state classifier in :mod:`gnd.codegen.plan`,
    which writes per file and the manifest LAST, because it must preserve the
    extension files a whole-tree replace would destroy.

    Bands, and why each is the one it is:

    * ``0`` — the tree was written, or was already current (a second run over an
      unchanged model performs zero writes — G-06).
    * ``3`` — the model failed to load, two of its ids sanitize to one Python
      symbol, or the existing manifest is unreadable. The second is the ONE case
      where codegen refuses a model ``gnd validate`` accepted, and 3 is right
      because the remedy is in the model: rename one id.
    * ``11`` — a write or adoption was REFUSED and nothing was destroyed: a
      hand-edited derived file; an unmanaged regular, symlink, or non-regular
      occupant at a derived path; an occupied directory without a codegen
      manifest; an unrecorded regular extension before explicit ``--force``
      adoption; or a recorded or unrecorded extension path occupied by a
      symlink, directory, FIFO, or over-cap leaf. Re-run with ``--force`` only
      for hand-edited or unmanaged regular/symlink derived paths and unrecorded
      regular-extension adoption; remove or move unsafe occupants by hand.
      Also: a smoke-pattern module at the project root that this model does not
      emit (v5.1 D-P1.8). That scan is provenance-blind and ``--force`` does not
      override it — the remedy is to delete the named file, because renaming a
      create-once module would overwrite bytes regeneration must never touch.
      This is not a new allocation or claim: 11 retains its refusal meaning,
      while recorded authored regular extension divergence is an informational
      create-once skip at exit 0, not band 11.
    * ``64`` — usage (argparse).
    * ``70`` — an emitter invariant broke: the projection gate refused GND's own
      schema, an emitted module did not parse, the default template imported a
      provider, or the generated skill's frontmatter would not read back. All
      four are breaches by GND's emitter over a model that already loaded clean,
      so they follow the ``ProjectionGateError`` precedent rather than band 3.
    * ``74`` — the output path was refused by the traversal guard, or unwritable.
    """
    from gnd.codegen.emit import (
        EmitGateError,
        ProjectExistsError,
        SkillNameError,
        emit_project,
        write_project,
    )
    from gnd.codegen.identifiers import IdentifierError
    from gnd.codegen.manifest import (
        CodegenManifestError,
        build_manifest,
        render_manifest,
    )
    from gnd.codegen.plan import (
        _assert_root_path_bound,
        _bind_codegen_parent,
        _open_codegen_root,
        _read_manifest_at,
        apply_codegen,
        plan_codegen,
    )
    from gnd.extract.projection import ProjectionGateError

    try:
        model = load_model(model_path)
        from gnd.terms import require_non_temporal

        require_non_temporal(model, "codegen")
        if model.reference_populations:
            raise ModelValidationError(
                [
                    ValidationIssue(
                        path="$",
                        message="codegen does not support reference populations",
                        rule_id="reference:consumer-unsupported",
                    )
                ]
            )
    except ModelValidationError as error:
        for warning in error.warnings:
            print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")
        _print_issues(error.issues)
        return 3
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"ERROR: {error}")
        return 3

    try:
        project = emit_project(
            model,
            model_path,
            skill_name=Path(out_dir).resolve(strict=False).name,
        )
    except SkillNameError as error:
        print(f"ERROR: invalid generated skill directory: {error}")
        return EXIT_IO
    except IdentifierError as error:
        print(f"ERROR: {error}")
        return 3
    except (EmitGateError, ProjectionGateError) as error:
        print(f"INTERNAL ERROR: {error}")
        return EXIT_INTERNAL

    root = Path(out_dir)
    manifest = None
    root_fd = None
    try:
        parent_path, root_parts, parent_fd = _bind_codegen_parent(root)
    except install_module.InstallPathError as error:
        print(f"ERROR: refused output path: {error}")
        return EXIT_IO
    try:
        root_fd = _open_codegen_root(root)
    except FileNotFoundError:
        occupied = False
    except install_module.InstallPathError as error:
        os.close(parent_fd)
        print(f"ERROR: refused output path: {error}")
        return EXIT_IO
    else:
        try:
            manifest, _manifest_identity = _read_manifest_at(root_fd, root)
            occupied = bool(os.listdir(root_fd))
        except CodegenManifestError as error:
            os.close(root_fd)
            os.close(parent_fd)
            print(f"ERROR: {error}")
            return 3
        except OSError as error:
            os.close(root_fd)
            os.close(parent_fd)
            print(f"ERROR: could not inspect output directory {root}: {error}")
            return EXIT_IO
    try:
        _assert_root_path_bound(parent_path, parent_fd)
    except install_module.InstallPathError as error:
        if root_fd is not None:
            os.close(root_fd)
        os.close(parent_fd)
        print(f"ERROR: refused output path: {error}")
        return EXIT_IO
    if manifest is None and not occupied:
        # The FRESH path — plan 03's atomic whole-tree publication, with the
        # manifest staged last and the tree renamed below the retained parent.
        try:
            write_project(
                project,
                out_dir,
                manifest_text=render_manifest(build_manifest(project, model_path)),
                parent_fd=parent_fd,
                parent_path=parent_path,
                root_parts=root_parts,
                root_fd=root_fd,
            )
        except ProjectExistsError as error:
            print(f"ERROR: {error}")
            return EXIT_COLLISION
        except SkillNameError as error:
            print(f"ERROR: invalid generated skill directory: {error}")
            return EXIT_IO
        except install_module.InstallPathError as error:
            print(f"ERROR: refused output path: {error}")
            return EXIT_IO
        except OSError as error:
            print(f"ERROR: could not write the project under {out_dir}: {error}")
            return EXIT_IO
        finally:
            if root_fd is not None:
                os.close(root_fd)
            os.close(parent_fd)
        print(f"generated project for {model_path} -> {root}")
        for file in project.files:
            print(f"  {file.relpath} [{file.ownership}] created")
        return 0

    if manifest is None and not force:
        # Plan 03's shipped refusal, preserved rather than quietly relaxed by
        # the arrival of the classifier: a directory holding work GND never
        # placed is not a codegen project, and merging into it is a bigger
        # promise than "regenerate". `--force` adopts it, and even then only the
        # PLANNED relpaths are ever touched.
        if root_fd is not None:
            os.close(root_fd)
        os.close(parent_fd)
        print(
            f"ERROR: {root} is not empty and carries no codegen manifest, so "
            f"gnd codegen refuses rather than writing into it. Nothing was "
            f"destroyed. Re-run with --force to adopt the occupied paths GND "
            f"would own; files at any other path are never touched."
        )
        return EXIT_COLLISION

    emitted_smoke = ", ".join(
        sorted(
            file.relpath
            for file in project.files
            if file.relpath.startswith("test_architecture_smoke_")
        )
    )
    stale_smoke = _stale_smoke_modules(root_fd, project)
    if stale_smoke:
        # v5.1 D-P1.8: detect, decide, THEN write (standing rule 3). The scan is
        # provenance-blind — a smoke-pattern basename that is not the one this
        # model emits is refused whether GND wrote it or a hand did, because
        # adopting it would claim a file codegen did not create and leaving it
        # puts an orphan beside a live module no reader can tell apart.
        if root_fd is not None:
            os.close(root_fd)
        os.close(parent_fd)
        listed = ", ".join(sorted(stale_smoke))
        print(
            f"ERROR: {root} carries a smoke module this model does not emit: "
            f"{listed}. This model's smoke module is {emitted_smoke}. Delete "
            f"the file(s) named above and re-run; gnd codegen refuses rather "
            f"than adopting or renaming a create-once file. Nothing was "
            f"destroyed, and --force does not override this."
        )
        return EXIT_COLLISION

    os.close(parent_fd)
    try:
        assert root_fd is not None
        plan = plan_codegen(project, out_dir, manifest, root_fd=root_fd)
        result = apply_codegen(project, out_dir, plan, force=force, root_fd=root_fd)
    except CodegenManifestError as error:
        print(f"ERROR: {error}")
        return 3
    except install_module.InstallPathError as error:
        print(f"ERROR: refused output path: {error}")
        return EXIT_IO
    except install_module.InstallError as error:
        print(f"ERROR: refused manifest update: {error}. Nothing was destroyed.")
        return EXIT_COLLISION
    except OSError as error:
        print(f"ERROR: could not write the project under {out_dir}: {error}")
        return EXIT_IO
    finally:
        if root_fd is not None:
            os.close(root_fd)

    states = plan.by_relpath()
    apply_states = {record.relpath: record for record in result.skipped}
    print(f"generated project for {model_path} -> {root}")
    for file in project.files:
        state = apply_states.get(file.relpath, states[file.relpath])
        verb = "written" if file.relpath in result.written else f"skipped ({state.state})"
        print(f"  {file.relpath} [{file.ownership}] {verb}")
    print(f"{result.writes} written, {len(result.skipped)} skipped")
    for orphan in result.orphans:
        print(f"  NOTE: {orphan} is recorded but no longer emitted; left in place")
    for relpath in result.extension_skips:
        print(f"NOTE: preserved authored extension {relpath}; left unchanged")
    if result.collisions:
        force_remediable = [
            detail for detail in result.collision_details if detail.remediation == "force"
        ]
        manual_removal = [
            detail for detail in result.collision_details if detail.remediation == "remove"
        ]
        if force_remediable:
            print("ERROR: force-remediable refusals:")
            for detail in force_remediable:
                print(f"  {detail.relpath} — {detail.detail}")
            print(
                "Re-run with --force to overwrite the derived paths or adopt the "
                "regular unmanaged extension paths listed above."
            )
        if manual_removal:
            print("ERROR: unsafe occupants requiring manual removal:")
            for detail in manual_removal:
                print(f"  {detail.relpath} — {detail.detail}")
            print(
                "Remove or move the unsafe occupants listed above by hand; --force "
                "will not replace them."
            )
        print("Nothing was destroyed.")
        return EXIT_COLLISION
    return 0


def _utf8_clean(value: str) -> bool:
    """Is this command-line string valid UTF-8?

    POSIX argv is decoded with surrogateescape, so bytes that were never valid
    UTF-8 survive as lone surrogates. They are refused at stage 1 rather than
    encoded: writing them with surrogatepass produces ill-formed UTF-8, which
    would make the harness emit a log its own reader must reject.
    """
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def _cmd_solve(args: argparse.Namespace) -> int:
    """``gnd solve MODEL --workspace DIR`` — stage 1, then the walk.

    Stage 1 of the validation matrix lives here because a repeated flag and a
    malformed NAME=SECONDS are only visible at the command line. Stages 2 through
    8 are decidable from the typed arguments and belong to run_walk, which is the
    one home for them.
    """
    strings = [args.model, args.workspace, args.experiment, args.from_station, args.until]
    strings += list(args.skip) + list(args.test_argv) + list(args.station_timeout)
    if args.adapter is not None:
        strings.append(args.adapter)
    if args.adapter_policy is not None:
        strings.append(args.adapter_policy)
    for value in strings:
        if value is not None and not _utf8_clean(value):
            print(
                "gnd solve: error: command-line arguments must be valid UTF-8",
                file=sys.stderr,
            )
            return EXIT_USAGE

    station_timeout: dict[str, int] = {}
    for item in args.station_timeout:
        name, separator, raw = item.partition("=")
        if not separator or not name:
            print(
                f"gnd solve: error: --station-timeout expects NAME=SECONDS, got {item!r}",
                file=sys.stderr,
            )
            return EXIT_USAGE
        if not raw.isascii() or not raw.isdecimal():
            print(
                "gnd solve: error: --station-timeout SECONDS must be a positive ASCII integer",
                file=sys.stderr,
            )
            return EXIT_USAGE
        normalized = raw.lstrip("0") or "0"
        ceiling = str(solve.MAX_STATION_TIMEOUT_S)
        if len(normalized) > len(ceiling) or (
            len(normalized) == len(ceiling) and normalized > ceiling
        ):
            print(
                "gnd solve: error: --station-timeout SECONDS must be between 1 and "
                f"{solve.MAX_STATION_TIMEOUT_S}",
                file=sys.stderr,
            )
            return EXIT_USAGE
        seconds = int(normalized)
        if seconds < 1 or seconds > solve.MAX_STATION_TIMEOUT_S:
            print(
                "gnd solve: error: --station-timeout SECONDS must be between 1 and "
                f"{solve.MAX_STATION_TIMEOUT_S}",
                file=sys.stderr,
            )
            return EXIT_USAGE
        if name in station_timeout:
            # Two values for one station is a contradiction, not a set. --skip
            # repeats are fine for exactly the opposite reason.
            print(
                f"gnd solve: error: --station-timeout given twice for {name!r}",
                file=sys.stderr,
            )
            return EXIT_USAGE
        station_timeout[name] = seconds

    return solve.run_walk(
        Path(args.model),
        workspace=Path(args.workspace),
        experiment=None if args.experiment is None else Path(args.experiment),
        start=args.from_station,
        until=args.until,
        skip=frozenset(args.skip),
        auto=args.auto,
        adapter=args.adapter,
        adapter_policy=(None if args.adapter_policy is None else Path(args.adapter_policy)),
        test_argv=tuple(args.test_argv),
        station_timeout=station_timeout,
    )


def _cmd_conformance(model_path: str, project_dir: str, output_format: str) -> int:
    """``gnd conformance MODEL DIR`` — does the generated code still match?

    GEN-02's headline. The reusable conformance service invokes all four
    standalone assertions; this controller only renders its raw payload. That
    keeps command and programmatic callers on one partial-run and exit-band
    contract without making the service import this controller.

    **What a green result means, and what it does not.** Exit 0 says every
    DERIVED file still hashes to what the manifest recorded, the model has not
    moved since generation, and the emitted surface names every fact type the
    model declares, and declared architecture agrees with static observations.
    Extension bytes are not integrity-digest-gated, and architecture may inspect
    explicit declarations. It says nothing about a
    derived file co-edited together with its manifest entry, and nothing about
    what a tool's BODY computes — assertion #3 binds names and signatures. All
    of those bounds travel in the payload's ``limits`` block and the
    ``unexamined`` list rather than only in this docstring, because the payload
    is what a CI job reads.

    **A model that will not LOAD is band 3, never 13.** The structural assertion
    needs the parsed model, and a model that fails validation means the
    obligations could not be EVALUATED — reporting drift there would claim the
    code disagrees with a model that does not exist in a checkable form. This is
    RESEARCH §2.2's case C0 arriving as a band rather than as a traceback, and it
    is why plan 06's mutation #3 has to be a CONSISTENT rename: the naive
    one-line version lands here and reds for a reason that has nothing to do with
    the gate.

    Bands, and why each is the one it is: see
    :func:`gnd.conformance.service.run_conformance`.
    """
    from gnd.conformance.report import canonical, render_conformance
    from gnd.conformance.service import run_conformance

    result = run_conformance(model_path, project_dir)

    if output_format == "json":
        print(canonical(result.payload))
    else:
        print(render_conformance(result.payload))

    return result.exit_code


class _RecoveryCLIError(Exception):
    """One classified refusal at the public recovery argv boundary."""

    def __init__(self, exit_code: int, message: str) -> None:
        super().__init__(message)
        self.exit_code = exit_code


def _recovery_root(value: str) -> tuple[Path, int]:
    """Descriptor-walk and retain one authoritative real repository root."""

    from gnd.recovery.inventory import RecoveryInventoryError, _open_real_directory

    try:
        _evolve_reject_unsafe_spelling(value, label="recovery repository root")
    except _EvolutionCLIError as error:
        raise _RecoveryCLIError(error.exit_code, str(error)) from error
    if "\\" in value:
        raise _RecoveryCLIError(EXIT_IO, "recovery repository root must use POSIX path separators")
    supplied = Path(value)
    candidate = supplied if supplied.is_absolute() else Path.cwd() / supplied
    try:
        root_fd, root = _open_real_directory(candidate)
    except RecoveryInventoryError as error:
        exit_code = EXIT_NO_INPUT if _recovery_cause_is(error, FileNotFoundError) else EXIT_IO
        raise _RecoveryCLIError(exit_code, str(error)) from error
    return root, root_fd


def _recovery_relative_argv(root: Path, value: str, *, label: str) -> str:
    """Normalize an argv path to one portable path beneath ``root``."""

    from pathlib import PurePosixPath, PureWindowsPath

    if not value or not value.strip() or "\x00" in value:
        raise _RecoveryCLIError(EXIT_IO, f"{label} must be a nonempty path")
    if value != value.strip() or "\\" in value:
        raise _RecoveryCLIError(EXIT_IO, f"{label} must use normalized POSIX path spelling")
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    if ".." in posix.parts or ".." in windows.parts:
        raise _RecoveryCLIError(EXIT_IO, f"{label} contains a refused '..' component")
    if windows.drive and not windows.is_absolute():
        raise _RecoveryCLIError(EXIT_IO, f"{label} is a refused drive-relative path")

    supplied = Path(value)
    candidate = supplied if supplied.is_absolute() else root.joinpath(*posix.parts)
    try:
        relative = candidate.relative_to(root)
    except ValueError as error:
        raise _RecoveryCLIError(EXIT_IO, f"{label} escapes recovery root {root}") from error
    relative_posix = PurePosixPath(*relative.parts)
    normalized = relative_posix.as_posix()
    if not relative.parts or normalized in {"", "."}:
        raise _RecoveryCLIError(EXIT_IO, f"{label} must name a leaf beneath {root}")
    if not supplied.is_absolute() and posix.as_posix() != value:
        raise _RecoveryCLIError(EXIT_IO, f"{label} is not in canonical POSIX form")
    return normalized


def _recovery_required_canonical_leaf(
    root: Path,
    root_fd: int,
    value: str,
    *,
    label: str,
    canonical_name: str,
) -> Path:
    """Require an explicit argv leaf to identify one canonical bundle sibling."""

    relative = _recovery_relative_argv(root, value, label=label)
    if relative != canonical_name:
        raise _RecoveryCLIError(
            EXIT_IO,
            f"{label} must be the canonical sibling {root / canonical_name}",
        )
    path = root / relative
    try:
        info = os.stat(canonical_name, dir_fd=root_fd, follow_symlinks=False)
    except FileNotFoundError as error:
        raise _RecoveryCLIError(EXIT_NO_INPUT, f"required {label} {path} is missing") from error
    except OSError as error:
        raise _RecoveryCLIError(
            EXIT_IO, f"{label} {path} could not be inspected: {error}"
        ) from error
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise _RecoveryCLIError(EXIT_IO, f"{label} {path} is not a real regular file")
    return path


def _recovery_cause_is(error: BaseException, kind: type[BaseException]) -> bool:
    """Whether one closed error chain contains ``kind`` (without prose parsing)."""

    seen: set[int] = set()
    current: BaseException | None = error
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if isinstance(current, kind):
            return True
        current = current.__cause__ or current.__context__
    return False


def _recovery_json(value: Any) -> str:
    """Canonical public JSON for frozen recovery records."""

    document = value.model_dump(mode="json")
    return json.dumps(
        document,
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
        allow_nan=False,
    )


def _recovery_open_output_parent(root_fd: int, relative: str) -> tuple[int, str]:
    """Return a descriptor-bound existing real output parent and leaf name."""

    from pathlib import PurePosixPath

    parts = PurePosixPath(relative).parts
    current = os.dup(root_fd)
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        for part in parts[:-1]:
            before = os.stat(part, dir_fd=current, follow_symlinks=False)
            if stat.S_ISLNK(before.st_mode) or not stat.S_ISDIR(before.st_mode):
                raise _RecoveryCLIError(
                    EXIT_IO, f"inventory output crosses non-directory component {part!r}"
                )
            child = os.open(part, flags, dir_fd=current)
            actual = os.fstat(child)
            if (before.st_dev, before.st_ino) != (actual.st_dev, actual.st_ino):
                os.close(child)
                raise _RecoveryCLIError(
                    EXIT_IO, f"inventory output component {part!r} changed before open"
                )
            os.close(current)
            current = child
        return current, parts[-1]
    except FileNotFoundError as error:
        os.close(current)
        raise _RecoveryCLIError(
            EXIT_IO, "inventory output parent must already exist beneath ROOT"
        ) from error
    except OSError as error:
        os.close(current)
        raise _RecoveryCLIError(
            EXIT_IO, f"inventory output parent could not be opened safely: {error}"
        ) from error
    except BaseException:
        os.close(current)
        raise


_RECOVERY_DIRECTORY_NAME_OBSERVATION_CAP = 10_000


def _recovery_canonical_directory_parts(
    root_fd: int,
    parts: tuple[str, ...],
) -> tuple[str, ...]:
    """Resolve existing directory components to their stored names by identity."""

    current = os.dup(root_fd)
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    canonical: list[str] = []
    try:
        for supplied in parts:
            before = os.stat(supplied, dir_fd=current, follow_symlinks=False)
            if stat.S_ISLNK(before.st_mode) or not stat.S_ISDIR(before.st_mode):
                raise _RecoveryCLIError(
                    EXIT_IO, f"directory component {supplied!r} is not a real directory"
                )
            child = os.open(supplied, flags, dir_fd=current)
            actual = os.fstat(child)
            if (before.st_dev, before.st_ino) != (actual.st_dev, actual.st_ino):
                os.close(child)
                raise _RecoveryCLIError(
                    EXIT_IO, f"directory component {supplied!r} changed before open"
                )
            stored_names: list[str] = []
            observations = 0
            with os.scandir(current) as entries:
                for entry in entries:
                    observations += 1
                    if observations > _RECOVERY_DIRECTORY_NAME_OBSERVATION_CAP:
                        os.close(child)
                        raise _RecoveryCLIError(
                            EXIT_IO,
                            f"directory contains too many entries to resolve {supplied!r} safely",
                        )
                    try:
                        observed = entry.stat(follow_symlinks=False)
                    except OSError:
                        continue
                    if (observed.st_dev, observed.st_ino) == (
                        actual.st_dev,
                        actual.st_ino,
                    ):
                        stored_names.append(entry.name)
            if len(stored_names) != 1:
                os.close(child)
                raise _RecoveryCLIError(
                    EXIT_IO,
                    f"directory component {supplied!r} has no unique stored identity",
                )
            canonical.append(stored_names[0])
            os.close(current)
            current = child
        return tuple(canonical)
    except FileNotFoundError as error:
        raise _RecoveryCLIError(
            EXIT_NO_INPUT, f"directory component is missing: {error}"
        ) from error
    except OSError as error:
        raise _RecoveryCLIError(
            EXIT_IO, f"directory component could not be resolved safely: {error}"
        ) from error
    finally:
        os.close(current)


def _recovery_require_absent_output(root_fd: int, relative: str) -> None:
    parent_fd, name = _recovery_open_output_parent(root_fd, relative)
    try:
        try:
            os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            return
        except OSError as error:
            raise _RecoveryCLIError(
                EXIT_IO, f"inventory output {relative} could not be inspected: {error}"
            ) from error
        raise _RecoveryCLIError(
            EXIT_IO, f"inventory output {relative} already exists; refusing to overwrite it"
        )
    finally:
        os.close(parent_fd)


def _recovery_require_existing_exclusion(root_fd: int, relative: str) -> None:
    """Require one user-declared exclusion to exist beneath the bound root."""

    parent_fd, name = _recovery_open_output_parent(root_fd, relative)
    try:
        try:
            os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError as error:
            raise _RecoveryCLIError(
                EXIT_NO_INPUT, f"explicit exclusion {relative} does not exist"
            ) from error
        except OSError as error:
            raise _RecoveryCLIError(
                EXIT_IO, f"explicit exclusion {relative} could not be inspected: {error}"
            ) from error
    finally:
        os.close(parent_fd)


def _recovery_root_still_bound(root: Path, root_fd: int) -> None:
    """Refuse publication if argv ROOT no longer names the scanned directory."""

    from gnd.recovery.inventory import RecoveryInventoryError, _open_real_directory

    expected = os.fstat(root_fd)
    try:
        check_fd, _ = _open_real_directory(root)
    except RecoveryInventoryError as error:
        raise _RecoveryCLIError(
            EXIT_IO, f"recovery repository root {root} changed during operation: {error}"
        ) from error
    try:
        actual = os.fstat(check_fd)
        if (actual.st_dev, actual.st_ino) != (expected.st_dev, expected.st_ino):
            raise _RecoveryCLIError(
                EXIT_IO, f"recovery repository root {root} changed during inventory"
            )
    finally:
        os.close(check_fd)


def _recovery_publish_absent(root_fd: int, relative: str, data: bytes) -> None:
    """Publish one absent leaf relative to the retained repository descriptor."""

    parent_fd, name = _recovery_open_output_parent(root_fd, relative)
    staging = f".gnd-recovery-{os.urandom(8).hex()}"
    staged = False
    try:
        handle_fd = os.open(
            staging,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o644,
            dir_fd=parent_fd,
        )
        staged = True
        with os.fdopen(handle_fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(
                staging,
                name,
                src_dir_fd=parent_fd,
                dst_dir_fd=parent_fd,
                follow_symlinks=False,
            )
        except FileExistsError as error:
            raise _RecoveryCLIError(
                EXIT_IO,
                f"inventory output {relative} changed before publication; refusing overwrite",
            ) from error
        os.unlink(staging, dir_fd=parent_fd)
        staged = False
    except _RecoveryCLIError:
        raise
    except OSError as error:
        raise _RecoveryCLIError(
            EXIT_IO, f"inventory output {relative} could not be published: {error}"
        ) from error
    finally:
        if staged:
            try:
                os.unlink(staging, dir_fd=parent_fd)
            except OSError:
                pass
        os.close(parent_fd)


def _parse_recovery_exclusion(value: str) -> Any:
    """Parse ``REASON=PATH`` into the closed public exclusion record."""

    from pydantic import ValidationError

    from gnd.recovery.report import ExcludedRoot, ExclusionReason

    if "=" not in value:
        raise _RecoveryCLIError(
            3,
            f"exclusion {value!r} must use REASON=PATH with a closed exclusion reason",
        )
    reason_value, path = value.split("=", 1)
    try:
        reason = ExclusionReason(reason_value)
    except ValueError as error:
        raise _RecoveryCLIError(3, f"invalid exclusion reason {reason_value!r}") from error
    try:
        return ExcludedRoot(
            exclusion_id=(
                "cli-exclusion-"
                + hashlib.sha256(f"{reason.value}\0{path}".encode()).hexdigest()[:16]
            ),
            path=path,
            reason=reason,
        )
    except ValidationError as error:
        raise _RecoveryCLIError(EXIT_IO, f"unsafe exclusion path in {value!r}: {error}") from error


def _cmd_recovery_inventory(
    root_value: str,
    sources: list[str],
    tests: list[str],
    docs: list[str],
    configs: list[str],
    schemas: list[str],
    exclusions: list[str],
    max_file_bytes: int,
    max_total_bytes: int,
    max_files: int,
    out_value: str,
) -> int:
    """Inventory explicit repository roots as inert, bounded static evidence."""

    from pydantic import ValidationError

    from gnd.recovery.inventory import (
        _CONTROLLER_BUNDLE_PATHS,
        RecoveryInventoryError,
        _controller_reserved_exclusion,
        _is_canonical_bundle_alias,
        scan_recovery_scope,
    )
    from gnd.recovery.report import (
        RootCategory,
        SelectedRoot,
    )

    try:
        root, root_fd = _recovery_root(root_value)
        try:
            output_relative = _recovery_relative_argv(root, out_value, label="inventory output")
            canonical_bundle_names = _CONTROLLER_BUNDLE_PATHS
            if _is_canonical_bundle_alias(output_relative):
                raise _RecoveryCLIError(
                    3,
                    "inventory --out cannot replace a canonical recovery bundle artifact",
                )
            output_path = root / output_relative
            _recovery_require_absent_output(root_fd, output_relative)
            from pathlib import PurePosixPath

            output_parts = PurePosixPath(output_relative).parts
            canonical_output_parent = _recovery_canonical_directory_parts(
                root_fd, output_parts[:-1]
            )

            categorized = (
                (RootCategory.source, sources),
                (RootCategory.test, tests),
                (RootCategory.docs, docs),
                (RootCategory.config, configs),
                (RootCategory.schema, schemas),
            )
            if not any(values for _, values in categorized):
                raise _RecoveryCLIError(3, "at least one categorized recovery root is required")
            try:
                selected = tuple(
                    sorted(
                        (
                            SelectedRoot(category=category, path=path)
                            for category, values in categorized
                            for path in values
                        ),
                        key=lambda item: (item.path, item.category.value),
                    )
                )
            except ValidationError as error:
                raise _RecoveryCLIError(
                    EXIT_IO, f"unsafe selected recovery root: {error}"
                ) from error
            selected_bindings = tuple(
                (
                    item,
                    () if item.path == "." else PurePosixPath(item.path).parts,
                    _recovery_canonical_directory_parts(
                        root_fd,
                        () if item.path == "." else PurePosixPath(item.path).parts,
                    ),
                )
                for item in selected
            )
            selected_parts = sorted(canonical for _item, _supplied, canonical in selected_bindings)
            if any(
                other[: len(parts)] == parts
                for index, parts in enumerate(selected_parts)
                for other in selected_parts[index + 1 :]
            ):
                raise _RecoveryCLIError(3, "selected recovery roots must not overlap")
            parsed_exclusions = tuple(
                sorted(
                    (_parse_recovery_exclusion(value) for value in exclusions),
                    key=lambda item: (item.path, item.reason.value),
                )
            )
            for item in parsed_exclusions:
                _recovery_require_existing_exclusion(root_fd, item.path)
            output_scope_matches = tuple(
                (item, supplied, canonical)
                for item, supplied, canonical in selected_bindings
                if canonical_output_parent[: len(canonical)] == canonical
            )
            if len(output_scope_matches) > 1:
                raise _RecoveryCLIError(
                    3, "inventory output resolves beneath overlapping selected roots"
                )
            controller_output_path: str | None = None
            if output_scope_matches:
                _selected, supplied, canonical = output_scope_matches[0]
                controller_output_path = PurePosixPath(
                    *supplied,
                    *canonical_output_parent[len(canonical) :],
                    output_parts[-1],
                ).as_posix()
            reserved_paths: list[tuple[str, str]] = []
            if controller_output_path is not None:
                reserved_paths.append(("output", controller_output_path))
            if any(not canonical for _item, _supplied, canonical in selected_bindings):
                reserved_paths.extend(("bundle", name) for name in canonical_bundle_names)
            reserved_path_names = {path for _role, path in reserved_paths}
            conflicting_user_exclusions = sorted(
                item.path for item in parsed_exclusions if item.path in reserved_path_names
            )
            if conflicting_user_exclusions:
                raise _RecoveryCLIError(
                    3,
                    "controller-generated recovery paths cannot also be user exclusions: "
                    f"{conflicting_user_exclusions}",
                )
            controller_exclusions = tuple(
                _controller_reserved_exclusion(role, path)
                for role, path in sorted(reserved_paths, key=lambda item: item[1])
            )
            scan_exclusions = tuple(
                sorted((*parsed_exclusions, *controller_exclusions), key=lambda item: item.path)
            )
            inventory = scan_recovery_scope(
                root,
                selected,
                excluded_roots=scan_exclusions,
                max_file_bytes=max_file_bytes,
                max_total_bytes=max_total_bytes,
                max_files=max_files,
                expected_root_identity=(
                    os.fstat(root_fd).st_dev,
                    os.fstat(root_fd).st_ino,
                ),
            )
            observed_exclusions = {item.path for item in inventory.scope.excluded_roots}
            blocking_output_exclusions = sorted(
                item.path
                for item in inventory.scope.excluded_roots
                if controller_output_path is not None
                and controller_output_path.startswith(f"{item.path}/")
            )
            if blocking_output_exclusions:
                raise _RecoveryCLIError(
                    3,
                    "inventory output cannot sit below an excluded tree: "
                    f"{blocking_output_exclusions}",
                )
            missing_exclusions = sorted(
                item.path for item in parsed_exclusions if item.path not in observed_exclusions
            )
            if missing_exclusions:
                raise _RecoveryCLIError(
                    EXIT_NO_INPUT,
                    f"explicit exclusions disappeared before inventory: {missing_exclusions}",
                )
            rendered = (_recovery_json(inventory) + "\n").encode("utf-8")
            _recovery_root_still_bound(root, root_fd)
            _recovery_publish_absent(root_fd, output_relative, rendered)
        finally:
            os.close(root_fd)
    except _RecoveryCLIError as error:
        print(f"RECOVERY INVENTORY REFUSED ({error.exit_code}): {error}")
        return error.exit_code
    except FileNotFoundError as error:
        print(f"RECOVERY INVENTORY REFUSED ({EXIT_NO_INPUT}): missing selected root: {error}")
        return EXIT_NO_INPUT
    except RecoveryInventoryError as error:
        if _recovery_cause_is(error, FileNotFoundError):
            exit_code = EXIT_NO_INPUT
        else:
            exit_code = EXIT_IO
        print(f"RECOVERY INVENTORY REFUSED ({exit_code}): {error}")
        return exit_code
    except ValidationError as error:
        print(f"RECOVERY INVENTORY REFUSED (3): {error}")
        return 3
    except (install_module.InstallError, install_module.InstallPathError, OSError) as error:
        print(f"RECOVERY INVENTORY REFUSED ({EXIT_IO}): {error}")
        return EXIT_IO
    except (TypeError, ValueError) as error:
        print(f"RECOVERY INVENTORY REFUSED (3): {error}")
        return 3

    print(f"recovery inventory wrote {output_path}")
    return 0


def _cmd_recovery_verify(
    root_value: str,
    report_value: str,
    model_value: str,
    verbalization_value: str,
) -> int:
    """Verify one canonical three-artifact recovery bundle without mutation."""

    from gnd.recovery.verify import verify_recovery_bundle

    try:
        root, root_fd = _recovery_root(root_value)
        try:
            _recovery_required_canonical_leaf(
                root,
                root_fd,
                report_value,
                label="recovery report",
                canonical_name="model.recovery.json",
            )
            _recovery_required_canonical_leaf(
                root,
                root_fd,
                model_value,
                label="recovered model",
                canonical_name="model.orm.yaml",
            )
            _recovery_required_canonical_leaf(
                root,
                root_fd,
                verbalization_value,
                label="model verbalization",
                canonical_name="model.verbalization.txt",
            )
            root_info = os.fstat(root_fd)
            result = verify_recovery_bundle(
                root,
                expected_root_identity=(root_info.st_dev, root_info.st_ino),
            )
            _recovery_root_still_bound(root, root_fd)
        finally:
            os.close(root_fd)
    except _RecoveryCLIError as error:
        print(f"RECOVERY VERIFY REFUSED ({error.exit_code}): {error}")
        return error.exit_code

    print(_recovery_json(result))
    if result.ok:
        return 0
    if any(error.startswith("missing-artifact:") for error in result.errors):
        return EXIT_NO_INPUT
    if any(error.startswith(("unsafe-artifact:", "parent-traversal:")) for error in result.errors):
        return EXIT_IO
    return 3


class _EvolutionCLIError(Exception):
    """One closed public evolution exit before a service stage can run."""

    def __init__(self, exit_code: int, message: str) -> None:
        super().__init__(message)
        self.exit_code = exit_code


_EVOLUTION_CLAIM_MAX_BYTES = 10 * 1024 * 1024


def _evolve_reject_unsafe_spelling(value: str, *, label: str) -> None:
    from pathlib import PurePosixPath, PureWindowsPath

    if not value or "\x00" in value:
        raise _EvolutionCLIError(EXIT_IO, f"{label} is empty or contains a NUL byte")
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    if ".." in posix.parts or ".." in windows.parts:
        raise _EvolutionCLIError(EXIT_IO, f"{label} contains a refused '..' component")
    if windows.drive and not windows.is_absolute():
        raise _EvolutionCLIError(EXIT_IO, f"{label} is a refused drive-relative path")


def _evolve_absolute_path(value: str, *, label: str) -> Path:
    _evolve_reject_unsafe_spelling(value, label=label)
    supplied = Path(value)
    return supplied if supplied.is_absolute() else Path.cwd() / supplied


def _evolve_reject_existing_symlinks(path: Path, *, label: str) -> None:
    """Reject every existing symlink component in one argv-supplied path."""

    current = Path(path.anchor)
    parts = path.parts[1:] if path.anchor else path.parts
    for part in parts:
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            return
        except OSError as error:
            raise _EvolutionCLIError(
                EXIT_IO, f"{label} could not be inspected at {current}: {error}"
            ) from error
        if stat.S_ISLNK(info.st_mode):
            raise _EvolutionCLIError(EXIT_IO, f"{label} crosses symlink {current}")


def _evolve_workspace(value: str) -> Path:
    workspace = _evolve_absolute_path(value, label="workspace")
    _evolve_reject_existing_symlinks(workspace, label="workspace")
    try:
        info = workspace.lstat()
    except FileNotFoundError as error:
        raise _EvolutionCLIError(EXIT_NO_INPUT, f"workspace {workspace} does not exist") from error
    except OSError as error:
        raise _EvolutionCLIError(
            EXIT_IO, f"workspace {workspace} could not be inspected: {error}"
        ) from error
    if not stat.S_ISDIR(info.st_mode):
        raise _EvolutionCLIError(EXIT_IO, f"workspace {workspace} is not a real directory")
    try:
        return workspace.resolve(strict=True)
    except OSError as error:
        raise _EvolutionCLIError(
            EXIT_IO, f"workspace {workspace} could not be resolved: {error}"
        ) from error


def _evolve_rooted_path(
    root: Path,
    value: str,
    *,
    root_label: str,
    label: str,
    required: bool,
    regular: bool = True,
) -> tuple[Path, str]:
    candidate = _evolve_absolute_path(value, label=label)
    try:
        relative = candidate.relative_to(root)
    except ValueError as error:
        raise _EvolutionCLIError(
            EXIT_IO, f"{label} {candidate} is outside {root_label} {root}"
        ) from error
    if not relative.parts:
        raise _EvolutionCLIError(EXIT_IO, f"{label} cannot be the {root_label}")

    current = root
    missing = False
    for part in relative.parts:
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            missing = True
            break
        except OSError as error:
            raise _EvolutionCLIError(
                EXIT_IO, f"{label} could not be inspected at {current}: {error}"
            ) from error
        if stat.S_ISLNK(info.st_mode):
            raise _EvolutionCLIError(EXIT_IO, f"{label} crosses symlink {current}")

    try:
        resolved = candidate.resolve(strict=False)
    except OSError as error:
        raise _EvolutionCLIError(
            EXIT_IO, f"{label} {candidate} could not be resolved: {error}"
        ) from error
    if not resolved.is_relative_to(root):
        raise _EvolutionCLIError(
            EXIT_IO, f"{label} {candidate} resolves outside {root_label} {root}"
        )
    if required and missing:
        raise _EvolutionCLIError(EXIT_NO_INPUT, f"required {label} {candidate} is missing")
    if required:
        try:
            info = candidate.lstat()
        except FileNotFoundError as error:
            raise _EvolutionCLIError(
                EXIT_NO_INPUT, f"required {label} {candidate} is missing"
            ) from error
        except OSError as error:
            raise _EvolutionCLIError(
                EXIT_IO, f"required {label} {candidate} could not be inspected: {error}"
            ) from error
        if regular and not stat.S_ISREG(info.st_mode):
            raise _EvolutionCLIError(EXIT_IO, f"required {label} {candidate} is not a regular file")
    return candidate, relative.as_posix()


def _evolve_workspace_path(
    workspace: Path,
    value: str,
    *,
    label: str,
    required: bool,
    regular: bool = True,
) -> tuple[Path, str]:
    return _evolve_rooted_path(
        workspace,
        value,
        root_label="workspace",
        label=label,
        required=required,
        regular=regular,
    )


def _evolve_records_root(value: str) -> Path:
    records = _evolve_absolute_path(value, label="records root")
    _evolve_reject_existing_symlinks(records, label="records root")
    try:
        info = records.lstat()
    except FileNotFoundError:
        pass
    except OSError as error:
        raise _EvolutionCLIError(
            EXIT_IO, f"records root {records} could not be inspected: {error}"
        ) from error
    else:
        if not stat.S_ISDIR(info.st_mode):
            raise _EvolutionCLIError(EXIT_IO, f"records root {records} is not a real directory")
    try:
        return records.resolve(strict=False)
    except OSError as error:
        raise _EvolutionCLIError(
            EXIT_IO, f"records root {records} could not be resolved: {error}"
        ) from error


def _evolve_read_claim(
    path: Path,
    model_type: Any,
    *,
    label: str,
    anchor: Path | None = None,
    relative: str | None = None,
) -> Any:
    from gnd.evolve import (
        EvolutionFinalizationState,
        EvolutionIntent,
        EvolutionPreview,
        EvolutionProposal,
        EvolutionRecord,
        read_evolution_finalization_state,
        read_evolution_intent,
        read_evolution_preview,
        read_evolution_proposal,
        read_evolution_record,
    )

    readers = {
        EvolutionFinalizationState: read_evolution_finalization_state,
        EvolutionIntent: read_evolution_intent,
        EvolutionPreview: read_evolution_preview,
        EvolutionProposal: read_evolution_proposal,
        EvolutionRecord: read_evolution_record,
    }
    reader = readers.get(model_type)
    if reader is None:
        raise _EvolutionCLIError(
            EXIT_INTERNAL,
            f"{label} has no claim-specific evolution reader",
        )
    try:
        return reader(path, anchor=anchor, relative=relative)
    except Exception as error:  # closed service refusal translation
        raise _EvolutionCLIError(
            _evolve_error_exit(error),
            f"{label} {path} is malformed: {error}",
        ) from error


def _evolve_validate_proposal_roots(proposal: Any) -> None:
    from pathlib import PurePosixPath, PureWindowsPath

    for project in proposal.linked_projects:
        raw = str(project.root)
        if "\x00" in raw or PurePosixPath(raw).is_absolute() or PureWindowsPath(raw).is_absolute():
            raise _EvolutionCLIError(
                3,
                f"linked project {project.project_id!r} must use a workspace-relative root",
            )


def _evolve_service_exit(error: Exception) -> int:
    """Translate the service's closed refusal vocabulary into public exits.

    The service predates typed refusal subclasses. Causes take precedence; the
    remaining exact message families are a compatibility adapter, and an
    unknown refusal fails as the internal-error band instead of being guessed.
    """

    from pydantic import ValidationError

    from gnd.safefs import InstallError, InstallPathError

    cause: BaseException | None = error
    while cause is not None:
        if isinstance(cause, FileNotFoundError):
            return EXIT_NO_INPUT
        if isinstance(cause, InstallPathError):
            return EXIT_IO
        if isinstance(cause, InstallError):
            return EXIT_COLLISION
        if isinstance(cause, OSError):
            return EXIT_IO
        if isinstance(
            cause,
            (
                json.JSONDecodeError,
                UnicodeDecodeError,
                ValidationError,
                ModelValidationError,
            ),
        ):
            return 3
        cause = cause.__cause__

    message = str(error)
    io_markers = (
        " is a symlink",
        " is not a regular file",
        "could not be inspected",
        "could not be read",
        "cannot be resolved",
        "escapes allowed root",
        "is not a directory",
        "unsupported special entry",
        "linked project exceeds ",
    )
    stale_markers = (
        "stale ",
        # An incomplete evolution refused a new one. 11 is reused rather than
        # newly allocated: "a write was refused, nothing was destroyed" is the
        # claim band 11 already makes (03-04 precedent), so no disjointness
        # obligation arises. D-11 forbids completing the state we found.
        "incomplete evolution ",
        "accepted blast radius",
        "breaking evolution requires explicit acceptance",
        "immutable evidence conflict",
        "changed before",
        "differs from immutable evidence",
        "does not match staged",
        "completed record differs",
        "live model bytes differ",
        "evidence changed",
        "verbalization changed",
        "blast radius changed",
        "identity differs",
        "identity changed",
        "inventory is incomplete",
        "do not match pending identities",
        "changed during",
    )
    malformed_markers = (
        "invalid ",
        "validation failed",
        "not UTF-8",
        "candidate model is not",
        "declared operations",
        "declared before value",
        "stable locator",
        "add target",
        "duplicate stable blast-radius reference",
        "candidate model media type",
        "operation audit actor/origin/time",
        "new llm-inferred constraints",
        "owner-approved user-supplied constraints",
        "new or changed constraints",
        "fact_types[",
        "evolution proposal exceeds ",
    )
    if any(marker in message for marker in io_markers):
        return EXIT_IO
    if any(marker in message for marker in stale_markers):
        return EXIT_COLLISION
    if any(marker in message for marker in malformed_markers):
        return 3
    return EXIT_INTERNAL


def _evolve_json_bytes(claim: Any) -> bytes:
    return (
        json.dumps(
            claim.model_dump(mode="json"),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _evolve_emit_claim(claim: Any, output_format: str, *, stage: str) -> None:
    if output_format == "json":
        sys.stdout.write(_evolve_json_bytes(claim).decode("utf-8"))
        return
    if stage == "preview":
        print(f"PREVIEW {claim.preview_sha256}")
        print(f"  proposal: {claim.proposal_sha256}")
        print(f"  before: {claim.before_model.sha256}")
        print(f"  candidate: {claim.candidate_model.sha256}")
        print(f"  blast-radius: {claim.blast_radius.report_sha256}")
        print(f"  breaking: {str(claim.breaking).lower()}")
        for reference in claim.affected_references:
            print(f"  affected: {reference}")
    elif stage == "apply":
        print(f"PENDING {claim.state_identity_sha256}")
        print(f"  proposal: {claim.proposal_id}")
        print(f"  preview: {claim.preview_sha256}")
        print(f"  model: {claim.old_model_sha256} -> {claim.new_model_sha256}")
    else:
        label = "PUBLISHED-WITH-DRIFT" if claim.published_with_drift else "RECORDED"
        print(f"{label} {claim.record_identity_sha256}")
        print(f"  model: {claim.old_model_sha256} -> {claim.new_model_sha256}")
        print(f"  conformance-exit: {claim.conformance_exit_code}")


def _evolve_publish_preview(
    workspace: Path,
    destination: Path,
    relative: str,
    data: bytes,
) -> None:
    from gnd.artifacts import ArtifactError, read_regular_file_bytes
    from gnd.safefs import InstallError, InstallPathError, LeafIdentity
    from gnd.safefs import atomic_write as _atomic_write

    try:
        existing = read_regular_file_bytes(
            workspace,
            relative,
            label="preview output",
        )
    except ArtifactError as error:
        cause: BaseException | None = error
        while cause is not None and not isinstance(cause, FileNotFoundError):
            cause = cause.__cause__
        if isinstance(cause, FileNotFoundError):
            existing = None
        else:
            raise _EvolutionCLIError(
                EXIT_IO,
                f"preview output could not be read through the workspace anchor: {error}",
            ) from error
    if existing is not None:
        if existing == data:
            return
        raise _EvolutionCLIError(
            EXIT_COLLISION,
            f"preview output {destination} already contains different owner bytes",
        )
    try:
        _atomic_write(
            workspace,
            relative,
            data,
            expected=LeafIdentity(kind="absent"),
        )
    except InstallPathError as error:
        raise _EvolutionCLIError(EXIT_IO, f"preview output path was refused: {error}") from error
    except InstallError as error:
        raise _EvolutionCLIError(
            EXIT_COLLISION, f"preview output changed before publication: {error}"
        ) from error
    except OSError as error:
        raise _EvolutionCLIError(
            EXIT_IO, f"preview output {destination} could not be published: {error}"
        ) from error


def _evolve_same_review_identity(reviewed: Any, staged: Any) -> bool:
    """Whether a staged accepted preview is the exact reviewed preview lineage."""

    excluded = {"accepted_blast_radius_sha256", "preview_sha256"}
    if reviewed.model_dump(mode="json", exclude=excluded) != staged.model_dump(
        mode="json", exclude=excluded
    ):
        return False
    return reviewed.accepted_blast_radius_sha256 in {
        None,
        staged.accepted_blast_radius_sha256,
    }


def _evolve_error_exit(error: Exception) -> int:
    from gnd.evolve import (
        EvolutionError,
        EvolutionOperationsGatedError,
        EvolutionReadOnlyCompatibilityError,
    )
    from gnd.safefs import InstallPathError

    if isinstance(error, _EvolutionCLIError):
        return error.exit_code
    # Before the generic EvolutionError arm, and by TYPE rather than by message
    # substring: the gate's refusal text names user-supplied element ids, and a
    # message-family match over those is how an id containing "stale " would
    # silently become exit 11.
    if isinstance(error, EvolutionOperationsGatedError):
        return EXIT_EVOLUTION_OPERATIONS_GATED
    # Before the generic arm, and by TYPE for the same reason: a pending state
    # this tool can read but cannot finish is a collision with existing
    # evidence, not a malformed input (D-P3.5).
    if isinstance(error, EvolutionReadOnlyCompatibilityError):
        return EXIT_COLLISION
    if isinstance(error, EvolutionError):
        return _evolve_service_exit(error)
    if isinstance(error, InstallPathError):
        return EXIT_IO
    if isinstance(error, FileNotFoundError):
        return EXIT_NO_INPUT
    if isinstance(error, OSError):
        return EXIT_IO
    return EXIT_INTERNAL


def _evolve_fail(error: Exception, *, stage: str) -> int:
    exit_code = _evolve_error_exit(error)
    print(f"EVOLUTION {stage.upper()} REFUSED ({exit_code}): {error}", file=sys.stderr)
    return exit_code


def _evolve_finish_apply(service: Any, pending: Any, output_format: str) -> int:
    """Complete the published evolution inside the same ``apply`` invocation.

    R-02 (MODEL-02): ``run_conformance`` is reachable only from
    ``EvolutionService.finalize``, and ``apply``/``finalize`` are separate
    user-facing subcommands, so "stopped after apply" was an ordinary user state
    in which a model change was published with no downstream recheck. The staged
    two-phase *service* protocol is deliberately unchanged (04-05…04-07 locked
    the model CAS as the explicit commit point, with conformance following it
    without rollback and the record published last); the gap closes here, at the
    command boundary.

    The two claims stay two payloads — D-24 forbids presenting the publication
    claim and the conformance claim as one verdict — and the command's exit is
    finalize's raw aggregate conformance exit, so drift is a published model
    with a reported problem rather than a failed apply.
    """

    _evolve_emit_claim(pending, output_format, stage="apply")
    try:
        record = service.finalize(pending)
    except Exception as error:  # closed public exit mapping
        raise _EvolutionCLIError(
            _evolve_error_exit(error),
            "model CAS committed, but the chained finalization was refused; the model "
            "is published and its downstream recheck is incomplete — complete it with "
            f"`gnd evolve finalize`: {error}",
        ) from error
    _evolve_emit_claim(record, output_format, stage="finalize")
    return record.conformance_exit_code


def _cmd_evolve_preview(
    model_path: str,
    proposal_path: str,
    workspace_path: str,
    records_path: str,
    preview_path: str,
    output_format: str,
) -> int:
    """Validate one proposal through ``EvolutionService.preview`` and publish its claim."""

    from gnd.evolve import EvolutionService, read_evolution_proposal

    try:
        workspace = _evolve_workspace(workspace_path)
        model, _model_relative = _evolve_workspace_path(
            workspace, model_path, label="model", required=True
        )
        proposal_file, proposal_relative = _evolve_workspace_path(
            workspace, proposal_path, label="proposal", required=True
        )
        preview_file, preview_relative = _evolve_workspace_path(
            workspace, preview_path, label="preview output", required=False
        )
        records = _evolve_records_root(records_path)
        proposal = read_evolution_proposal(
            proposal_file,
            anchor=workspace,
            relative=proposal_relative,
        )
        _evolve_validate_proposal_roots(proposal)
        service = EvolutionService(
            model_path=model,
            evidence_root=records,
            allowed_project_root=workspace,
        )
        preview = service.preview(proposal)
        rendered = _evolve_json_bytes(preview)
        _evolve_publish_preview(workspace, preview_file, preview_relative, rendered)
        _evolve_emit_claim(preview, output_format, stage="preview")
        return 0
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        return _evolve_fail(error, stage="preview")


def _cmd_evolve_apply(
    model_path: str,
    proposal_path: str,
    preview_path: str,
    workspace_path: str,
    records_path: str,
    output_format: str,
) -> int:
    """Revalidate an exact preview, publish the model CAS, and complete it.

    One command, one whole operation (R-02): ``EvolutionService.apply`` then
    ``EvolutionService.finalize`` in the same process, returning finalize's raw
    aggregate conformance exit.
    """

    from gnd.evolve import EvolutionPreview, EvolutionService, read_evolution_proposal

    try:
        workspace = _evolve_workspace(workspace_path)
        model, model_relative = _evolve_workspace_path(
            workspace, model_path, label="model", required=True
        )
        proposal_file, proposal_relative = _evolve_workspace_path(
            workspace, proposal_path, label="proposal", required=True
        )
        preview_file, preview_relative = _evolve_workspace_path(
            workspace, preview_path, label="preview", required=True
        )
        records = _evolve_records_root(records_path)
        proposal = read_evolution_proposal(
            proposal_file,
            anchor=workspace,
            relative=proposal_relative,
        )
        _evolve_validate_proposal_roots(proposal)
        reviewed = _evolve_read_claim(
            preview_file,
            EvolutionPreview,
            label="preview",
            anchor=workspace,
            relative=preview_relative,
        )
        if reviewed.proposal != proposal:
            raise _EvolutionCLIError(
                EXIT_COLLISION,
                "reviewed preview belongs to a different explicit proposal identity",
            )
        service = EvolutionService(
            model_path=model,
            evidence_root=records,
            allowed_project_root=workspace,
        )
        # Ahead of the branch split, not inside ``service.preview``: the
        # candidate-already-live retry branch below never calls ``preview``, and
        # it is exactly the branch a user reaches after an interrupted apply.
        # Installing the check only in ``preview`` would leave that branch
        # outside the guarantee. The proposal that owns the pending state is
        # exempt inside the service, so completing it stays possible.
        service.refuse_inherited_pending_finalization(proposal.proposal_id)
        try:
            from gnd.artifacts import read_regular_file_bytes

            live_model = read_regular_file_bytes(
                workspace,
                model_relative,
                label="model",
            )
        except Exception as error:
            raise _EvolutionCLIError(
                EXIT_IO, f"model {model} could not be read before apply: {error}"
            ) from error
        if live_model == reviewed.candidate_model.text.encode(reviewed.candidate_model.encoding):
            staged_path = records / reviewed.proposal.proposal_id / "preview.json"
            staged_file, staged_relative = _evolve_rooted_path(
                records,
                str(staged_path),
                root_label="records root",
                label="staged preview",
                required=True,
            )
            staged = _evolve_read_claim(
                staged_file,
                EvolutionPreview,
                label="staged preview",
                anchor=records,
                relative=staged_relative,
            )
            if not _evolve_same_review_identity(reviewed, staged):
                raise _EvolutionCLIError(
                    EXIT_COLLISION,
                    "staged accepted preview differs from the reviewed preview identity",
                )
            pending = service.apply(staged)
            return _evolve_finish_apply(service, pending, output_format)
        fresh = service.preview(proposal)
        if reviewed != fresh:
            raise _EvolutionCLIError(
                EXIT_COLLISION,
                "reviewed preview is stale or belongs to a different proposal/model identity",
            )
        accepted = fresh
        if fresh.breaking:
            print(
                "Enter the exact reviewed blast radius report_sha256 to apply:",
                file=sys.stderr,
            )
            try:
                accepted_digest = input().strip()
            except EOFError as error:
                raise _EvolutionCLIError(
                    EXIT_COLLISION, "breaking evolution requires exact blast radius acceptance"
                ) from error
            accepted = service.preview(
                proposal,
                accepted_blast_radius_sha256=accepted_digest,
            )
        pending = service.apply(accepted)
        return _evolve_finish_apply(service, pending, output_format)
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        return _evolve_fail(error, stage="apply")


def _cmd_evolve_finalize(
    model_path: str,
    pending_path: str,
    workspace_path: str,
    records_path: str,
    output_format: str,
) -> int:
    """Complete one pending identity through ``EvolutionService.finalize``."""

    from gnd.evolve import EvolutionFinalizationState, EvolutionService

    try:
        workspace = _evolve_workspace(workspace_path)
        model, _model_relative = _evolve_workspace_path(
            workspace, model_path, label="model", required=True
        )
        records = _evolve_records_root(records_path)
        pending_file, pending_relative = _evolve_rooted_path(
            records,
            pending_path,
            root_label="records root",
            label="pending state",
            required=True,
        )
        pending = _evolve_read_claim(
            pending_file,
            EvolutionFinalizationState,
            label="pending state",
            anchor=records,
            relative=pending_relative,
        )
        service = EvolutionService(
            model_path=model,
            evidence_root=records,
            allowed_project_root=workspace,
        )
        record = service.finalize(pending)
        _evolve_emit_claim(record, output_format, stage="finalize")
        return record.conformance_exit_code
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        return _evolve_fail(error, stage="finalize")


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
        applicable = json.loads(applicable_bytes.decode("utf-8"))
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


#: The case-directory convention `gnd fidelity` consumes (produced by the
#: gnd-render-doc / gnd-extract skills). Every file is REQUIRED for a case to
#: run; `extraction.skipped.json` is the one intentional opt-out marker.
_CASE_SOURCE = "source.population.json"
_CASE_DOCUMENT = "document.md"
_CASE_MANIFEST = "document.manifest.json"
_CASE_EXTRACTED = "extracted.population.json"
_CASE_SIDECAR = "extracted.population.extraction.json"
_CASE_SKIPPED = "extraction.skipped.json"


def _cmd_fidelity(
    model_path: str,
    cases_dir: str,
    artifacts_dir: str,
    out: str | None,
    output_format: str,
) -> int:
    """``gnd fidelity MODEL --cases DIR --artifacts DIR`` — extractor fidelity
    per fact type (SC3).

    **This command emits RATES and never a per-run verdict.** It is R-03″'s
    dual: ``gnd verify`` answers "does this population satisfy the model" and
    carries no rate; ``gnd fidelity`` answers "does this extraction reflect its
    document" and carries no verdict, no band and no ``acceptance_ready``. A
    single output carrying both invites reading either as the other, which is
    exactly the conflation PANEL-2 corrected.

    Fail-closed on its inputs. The applicable-set artifact DEFINES the row set
    and therefore every denominator, so its absence is exit 66 rather than a
    run over "whatever fact types happened to appear" — a missing artifact must
    never read as coverage. A case whose recorded digest does not describe the
    bytes on disk is exit 3: that is a tamper signal, not a census state.

    The census is R-13′'s: ``ran`` cases produce the rates, ``skipped`` (the
    intentional ``extraction.skipped.json`` marker) and ``failed`` (anything
    else, with its reason) are counted beside them and folded into no
    denominator anywhere.

    Exits 0 with the report, 3 on a binding mismatch inside a case, 64 on usage
    errors or a case set spanning more than one model, 66 when a required
    artifact is missing, 70 on an internal contract breach (a broken matcher
    partition or a payload its own schema rejects), 74 when the output path is
    refused or unwritable.
    """
    import hashlib as _hashlib

    from jsonschema import Draft202012Validator
    from jsonschema import ValidationError as SchemaValidationError

    from gnd.extract.manifest import (
        ManifestError,
        read_document_manifest,
        read_extraction_sidecar,
        read_extraction_skip_marker,
    )
    from gnd.extract.refscheme import applicable_set
    from gnd.fidelity.match import FidelityPartitionError, match_case
    from gnd.fidelity.report import (
        CaseOutcome,
        build_fidelity_payload,
        canonical,
        load_fidelity_schema,
        render_fidelity,
    )
    from gnd.synth import paths as _paths

    try:
        model = load_model(model_path)
    except ModelValidationError as error:
        for warning in error.warnings:
            print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")
        _print_issues(error.issues)
        return 3
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"ERROR: {error}")
        return 3

    stem = _extract_stem(model_path)
    artifacts_root = Path(artifacts_dir)
    applicable_path = artifacts_root / f"{stem}.applicable.json"
    projection_path = artifacts_root / f"{stem}.projection.schema.json"

    bundle_issue = _artifact_index_issue(
        model_path,
        artifacts_dir,
        (f"{stem}.applicable.json", f"{stem}.projection.schema.json"),
    )
    if bundle_issue is not None:
        code, message = bundle_issue
        print(f"VIOLATION artifact-index: {verbalize.line_text(message)}")
        return code

    # Fail closed (66, the D-22/doccheck EX_NOINPUT precedent): the applicable
    # set is the denominator's definition and the projection is what the
    # extraction decoded against. A missing one means the number cannot be
    # computed, never that it is 1.0.
    for label, required in (
        ("applicable-set artifact", applicable_path),
        ("projection artifact", projection_path),
    ):
        if not required.is_file():
            print(
                f"MISSING: the {label} at {required} does not exist — the "
                f"applicable set defines every denominator, so a run without "
                f"it would read as coverage it never had ({EXIT_NO_INPUT})"
            )
            return EXIT_NO_INPUT

    try:
        applicable_bytes = applicable_path.read_bytes()
        applicable = json.loads(applicable_bytes.decode("utf-8"))
        if applicable != applicable_set(model):
            print(
                "VIOLATION applicable-set: artifact does not match the "
                "canonical disposition derived from this model"
            )
            return 3
        declared_fact_types = {str(row["id"]) for row in applicable["fact_types"]}
        applicable_sha256 = _hashlib.sha256(applicable_bytes).hexdigest()
        projection_sha256 = _hashlib.sha256(projection_path.read_bytes()).hexdigest()
        model_sha256 = _hashlib.sha256(Path(model_path).read_bytes()).hexdigest()
    except (OSError, UnicodeDecodeError, ValueError, KeyError, TypeError) as error:
        print(f"ERROR: the extraction artifacts are not readable ({error})")
        return 3

    cases_root = Path(cases_dir)
    if not cases_root.is_dir():
        print(f"ERROR: --cases {cases_dir} is not a directory")
        return EXIT_USAGE
    case_dirs = sorted(path for path in cases_root.iterdir() if path.is_dir())
    if not case_dirs:
        print(
            f"ERROR: no case directories under {cases_dir} — an empty case set "
            f"produces no rates, and a payload over zero cases would read as a "
            f"measurement (64)"
        )
        return EXIT_USAGE

    # --- pass 1: classify every case; collect the model digests it claims ---
    outcomes: list[CaseOutcome] = []
    candidates: list[tuple[Path, Any, Any]] = []
    claimed_digests: set[str] = set()

    for case_dir in case_dirs:
        name = case_dir.name
        skipped_marker = case_dir / _CASE_SKIPPED
        extracted_path = case_dir / _CASE_EXTRACTED
        if skipped_marker.is_file():
            if extracted_path.is_file():
                outcomes.append(
                    CaseOutcome(
                        name,
                        "failed",
                        reason=(
                            f"{_CASE_SKIPPED} and {_CASE_EXTRACTED} are both "
                            f"present — an opt-out beside an extraction is a "
                            f"contradiction, not a skip"
                        ),
                    )
                )
                continue
            try:
                reason = read_extraction_skip_marker(skipped_marker).reason
            except ManifestError:
                outcomes.append(
                    CaseOutcome(
                        name,
                        "failed",
                        reason=(
                            f"{_CASE_SKIPPED} carries no readable 'reason' — a "
                            f"skip without a stated reason is indistinguishable "
                            f"from a lost file (R-13')"
                        ),
                    )
                )
                continue
            outcomes.append(CaseOutcome(name, "skipped", reason=reason))
            continue

        missing = [
            rel
            for rel in (
                _CASE_SOURCE,
                _CASE_DOCUMENT,
                _CASE_MANIFEST,
                _CASE_EXTRACTED,
                _CASE_SIDECAR,
            )
            if not (case_dir / rel).is_file()
        ]
        if missing:
            # ABSENCE IS FAILED, never skipped (R-13'/T-02.1-11).
            outcomes.append(
                CaseOutcome(
                    name,
                    "failed",
                    reason=(
                        f"the case is incomplete: {', '.join(missing)} missing "
                        f"and no {_CASE_SKIPPED} opt-out marker"
                    ),
                )
            )
            continue

        try:
            sidecar = read_extraction_sidecar(case_dir / _CASE_SIDECAR)
            manifest = read_document_manifest(case_dir / _CASE_MANIFEST)
        except ManifestError as error:
            outcomes.append(CaseOutcome(name, "failed", reason=f"handoff file invalid: {error}"))
            continue

        claimed_digests.add(sidecar.model_sha256)
        claimed_digests.add(manifest.model_sha256)
        candidates.append((case_dir, sidecar, manifest))

    # C4's analog, checked BEFORE any per-case binding: one payload represents
    # exactly one model, and "these cases are about different models" is a
    # usage error, not a tampered file.
    if len(claimed_digests) > 1:
        print(
            f"ERROR: the case set spans {len(claimed_digests)} model digest(s); "
            f"gnd fidelity is model-relative and one payload represents exactly "
            f"one model (C4). Split the cases and measure each model separately."
        )
        return EXIT_USAGE

    # --- pass 2: bind, load and match the candidate cases ---
    for case_dir, sidecar, manifest in candidates:
        name = case_dir.name
        source_path = case_dir / _CASE_SOURCE
        document_path = case_dir / _CASE_DOCUMENT
        extracted_path = case_dir / _CASE_EXTRACTED
        try:
            source_bytes = source_path.read_bytes()
            document_bytes = document_path.read_bytes()
            extracted_bytes = extracted_path.read_bytes()
        except OSError as error:
            outcomes.append(
                CaseOutcome(name, "failed", reason=f"a case file is unreadable: {error}")
            )
            continue

        source_sha256 = _hashlib.sha256(source_bytes).hexdigest()
        document_sha256 = _hashlib.sha256(document_bytes).hexdigest()
        extracted_sha256 = _hashlib.sha256(extracted_bytes).hexdigest()

        # C6 inside the case, in BOTH directions: the sidecar binds the
        # extraction to the model and the document it read, and the manifest
        # binds that document to the source population it was rendered from.
        # Without the second half a case could score an extraction of one
        # document against an unrelated source population and read clean.
        mismatches = [
            (field, recorded, actual)
            for field, recorded, actual in (
                ("sidecar.population_sha256", sidecar.population_sha256, extracted_sha256),
                ("sidecar.model_sha256", sidecar.model_sha256, model_sha256),
                ("sidecar.document_sha256", sidecar.document_sha256, document_sha256),
                (
                    "sidecar.projection_sha256",
                    sidecar.projection_sha256,
                    projection_sha256,
                ),
                ("manifest.document_sha256", manifest.document_sha256, document_sha256),
                (
                    "manifest.source_population_sha256",
                    manifest.source_population_sha256,
                    source_sha256,
                ),
                ("manifest.applicable_sha256", manifest.applicable_sha256, applicable_sha256),
            )
            if recorded != actual
        ]
        if mismatches:
            for field, recorded, actual in mismatches:
                print(
                    f"VIOLATION binding: {verbalize.path_segment(name)}/"
                    f"{verbalize.path_segment(field)} records "
                    f"{verbalize.path_segment(recorded)} but the bytes hash to "
                    f"{verbalize.path_segment(actual)} — this is not the artifact the "
                    f"handoff describes (C6)"
                )
            return 3

        try:
            source_population = load_population(source_path, model=model)
            extracted_population = load_population(extracted_path, model=model)
        except PopulationValidationError as error:
            outcomes.append(
                CaseOutcome(
                    name,
                    "failed",
                    reason=(
                        "a population failed model-relative validation: "
                        + "; ".join(issue.message for issue in error.issues[:3])
                    ),
                )
            )
            continue
        except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
            outcomes.append(
                CaseOutcome(name, "failed", reason=f"a population failed to load: {error}")
            )
            continue

        undeclared = sorted(
            (set(source_population.facts) | set(extracted_population.facts)) - declared_fact_types
        )
        if undeclared:
            outcomes.append(
                CaseOutcome(
                    name,
                    "failed",
                    reason=(
                        f"fact type(s) {undeclared} appear in a population but "
                        f"not in the applicable-set artifact, so no row could "
                        f"account for them"
                    ),
                )
            )
            continue

        try:
            matches = match_case(
                source_population.facts,
                extracted_population.facts,
                model=model,
                applicable=applicable,
            )
        except FidelityPartitionError as error:
            # The matcher's own invariant, breached over inputs that already
            # loaded clean: gnd's accounting, never the caller's data.
            print(f"INTERNAL ERROR: {error}")
            return EXIT_INTERNAL

        outcomes.append(
            CaseOutcome(
                name,
                "ran",
                matches=matches,
                source_sha256=source_sha256,
                extracted_sha256=extracted_sha256,
                document_sha256=document_sha256,
                source_facts=source_population.facts,
                extracted_facts=extracted_population.facts,
            )
        )

    payload = build_fidelity_payload(
        model_path,
        outcomes,
        applicable,
        model_sha256=model_sha256,
        applicable_sha256=applicable_sha256,
        projection_sha256=projection_sha256,
        gnd_version=resolve_version(),
    )

    # Validated before emission: a payload its own contract rejects is an
    # internal breach (70), not a report a consumer should have to police.
    try:
        Draft202012Validator(load_fidelity_schema()).validate(payload)
        rendered = canonical(payload)
    except (SchemaValidationError, ValueError) as error:
        print(f"INTERNAL ERROR: the fidelity payload violates its own schema: {error}")
        return EXIT_INTERNAL

    if out is not None:
        # The output path comes from argv ONLY, never from any case content,
        # and routes through the one traversal guard.
        try:
            destination = _paths.safe_output_path(Path(out).parent, Path(out).name)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(rendered + "\n", encoding="utf-8")
        except install_module.InstallPathError as error:
            print(f"ERROR: refused output path: {error}")
            return EXIT_IO
        except OSError as error:
            print(f"ERROR: could not write {out}: {error}")
            return EXIT_IO

    if output_format == "json":
        print(rendered)
    else:
        print(render_fidelity(payload))
    return 0


#: The fixed reviewer roster size. Pinned to ``gnd.review.adapters.REVIEWER_IDS``
#: by a test rather than derived here, because deriving it would require
#: importing the review stack at CLI import time for a number that must not move
#: silently anyway.
REVIEW_ATTEMPTED_REVIEWERS = 6

#: Python-owned, never argv-supplied: the grace a reviewer's process group gets
#: between SIGTERM and SIGKILL. A user-tunable grace is a way to make cleanup
#: unprovable, and cleanup provenance is what the failure envelopes assert.
REVIEW_TERMINATE_GRACE_SECONDS = 0.5


def _canonical_payload(payload: dict[str, Any]) -> str:
    """One deterministic JSON line. Two runs over one unchanged panel print the
    same bytes, so a recorded review summary is reproduced rather than trusted."""

    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _review_outcome(attempted: int, successful: int) -> int:
    """The semantic exit for one structurally completed panel run.

    Written as a pure function of two counts so the whole 0-through-6 table can
    be asserted without spawning anything, and so ``16`` is produced in exactly
    one place. The ``attempted`` guard is load-bearing rather than defensive:
    16 means a run that FINISHED all six attempts and came up short, so a
    partial run must never be able to reach this function and be graded.
    """
    if attempted != REVIEW_ATTEMPTED_REVIEWERS:
        raise ValueError("a panel outcome requires all six reviewer attempts to have completed")
    if not 0 <= successful <= attempted:
        raise ValueError("successful reviewers must be a subset of the attempted reviewers")
    return 0 if successful >= REVIEW_QUORUM else EXIT_REVIEW_INCONCLUSIVE


def _repository_relative_path(value: str) -> str:
    """Argparse converter for one normalized, portable repository-relative path.

    The review request and every artifact it names are resolved against the
    directory the user is standing in, so an absolute, drive-qualified, or
    ``..``-bearing argument is a malformed INVOCATION (64) rather than a
    malformed document (3). The request loader enforces the same shape again on
    the bytes it reads; this converter is the argv half, and neither may be
    dropped in favour of the other.
    """
    if not value or "\x00" in value or "\\" in value:
        raise argparse.ArgumentTypeError(
            "must be a normalized repository-relative POSIX path (no NUL, no backslash)"
        )
    posix = PurePosixPath(value)
    if (
        posix.is_absolute()
        or value != posix.as_posix()
        or any(part in {"", ".", ".."} for part in posix.parts)
    ):
        raise argparse.ArgumentTypeError(
            "must be a normalized repository-relative POSIX path resolved against the "
            "current directory (no leading '/', no '.', no '..' component)"
        )
    return value


def _add_review_panel_arguments(parser: argparse.ArgumentParser) -> None:
    """Attach the one shared request/output/bounds surface to a panel command."""

    parser.add_argument(
        "request",
        type=_repository_relative_path,
        help=(
            "repository-relative path to the review request JSON (kind plan, "
            "experiment-outcome, or spec-results-delta), resolved against the "
            "current directory"
        ),
    )
    parser.add_argument(
        "--out",
        required=True,
        help="directory to publish immutable panel evidence into; it must not exist",
    )
    parser.add_argument(
        "--reviewer-timeout",
        type=_positive_finite_float,
        default=600.0,
        help="positive finite per-reviewer wall-clock bound in seconds (default: 600)",
    )
    parser.add_argument(
        "--overall-timeout",
        type=_positive_finite_float,
        default=900.0,
        help="positive finite whole-panel wall-clock bound in seconds (default: 900)",
    )
    parser.add_argument(
        "--max-output-bytes",
        type=_positive_int,
        default=536_870_912,
        help=(
            "positive retained byte cap per reviewer stream; the whole-panel "
            "aggregate is twice this value (default: 536870912 -- effectively "
            "uncapped; pass a smaller value to bound a run)"
        ),
    )


def _cmd_review_panel(
    request_path: str,
    out_dir: str,
    reviewer_timeout: float,
    overall_timeout: float,
    max_output_bytes: int,
    reviewer_effort: str = "xhigh",
    command_name: str = "review panel",
) -> int:
    """Bridge one validated review request into the bounded panel exactly once."""

    from gnd.review.adapters import REVIEWER_IDS
    from gnd.review.request import (
        ReviewArtifactMissingError,
        ReviewRequestError,
        load_review_request,
    )
    from gnd.review.runner import (
        MAX_REVIEW_PROMPT_BYTES,
        ReviewLimits,
        ReviewRunError,
        canonical_panel_run,
        run_review_panel,
    )

    output_directory = Path(out_dir)
    try:
        output_directory.lstat()
    except FileNotFoundError:
        pass
    except OSError as error:
        print(f"IO ERROR: review output {output_directory} could not be inspected: {error}")
        return EXIT_IO
    else:
        print(
            f"COLLISION: review output {output_directory} already exists; nothing was "
            f"written and no reviewer was invoked"
        )
        return EXIT_COLLISION

    root = Path.cwd()
    request_file = root / request_path
    try:
        request_info = request_file.lstat()
    except FileNotFoundError:
        print(f"MISSING: review request {request_path} does not exist")
        return EXIT_NO_INPUT
    except OSError as error:
        print(f"IO ERROR: review request {request_path} could not be inspected: {error}")
        return EXIT_IO
    if stat.S_ISLNK(request_info.st_mode) or not stat.S_ISREG(request_info.st_mode):
        print(f"IO ERROR: review request {request_path} has a refused file type")
        return EXIT_IO

    try:
        loaded = load_review_request(root, request_path)
    except ReviewArtifactMissingError as error:
        print(f"MISSING: reviewed artifact {error.artifact_path} does not exist")
        return EXIT_NO_INPUT
    except ReviewRequestError as error:
        print(f"ERROR: {error}")
        return 3

    limits = ReviewLimits(
        reviewer_timeout_seconds=reviewer_timeout,
        overall_timeout_seconds=overall_timeout,
        terminate_grace_seconds=REVIEW_TERMINATE_GRACE_SECONDS,
        max_prompt_bytes=MAX_REVIEW_PROMPT_BYTES,
        max_stdout_bytes=max_output_bytes,
        max_stderr_bytes=max_output_bytes,
        max_total_output_bytes=max_output_bytes * 2,
    )
    try:
        run = asyncio.run(
            run_review_panel(
                loaded,
                repository_root=root,
                output_directory=output_directory,
                limits=limits,
                reviewer_effort=reviewer_effort,
            )
        )
    except ReviewRunError as error:
        print(f"IO ERROR: the review panel could not run or publish its evidence: {error}")
        return EXIT_IO
    except (OSError, ValueError) as error:
        print(f"IO ERROR: review evidence could not be published: {error}")
        return EXIT_IO
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"INTERNAL ERROR: {type(error).__name__}: {error}")
        return EXIT_INTERNAL

    try:
        outcome = _review_outcome(len(run.envelopes), len(run.successful_reviewer_ids))
    except ValueError as error:
        print(f"INTERNAL ERROR: {error}")
        return EXIT_INTERNAL

    print(
        _canonical_payload(
            {
                "schema_version": 1,
                "tool": "gnd",
                "command": command_name,
                "gnd_version": resolve_version(),
                "advisory": True,
                "request_kind": run.request.kind,
                "request_sha256": run.request_sha256,
                "run_directory": str(output_directory),
                "run_sha256": hashlib.sha256(canonical_panel_run(run)).hexdigest(),
                "required_successes": REVIEW_QUORUM,
                "reviewer_effort": run.reviewer_effort.value,
                "attempted_reviewer_ids": [reviewer.value for reviewer in REVIEWER_IDS],
                "reviewer_statuses": [
                    {
                        "reviewer_id": envelope.reviewer_id.value,
                        "status": envelope.status.value,
                    }
                    for envelope in run.envelopes
                ],
                "successful_reviewer_ids": [
                    reviewer.value for reviewer in run.successful_reviewer_ids
                ],
                "quorum_met": run.quorum_met,
                "outcome": (
                    "quorum-established" if run.quorum_met else "inconclusive-below-quorum"
                ),
                "reviewed_artifacts_unchanged": (
                    run.reviewed_artifacts_before_sha256 == run.reviewed_artifacts_after_sha256
                ),
            }
        )
    )
    return outcome


def _cmd_review_finalize(run_dir: str, synthesis_path: str, out_path: str) -> int:
    """Validate one semantic synthesis against immutable run evidence and render it."""

    from gnd.review.report import (
        PanelSynthesis,
        ReviewReportError,
        canonical_panel_synthesis,
        finalize_panel_synthesis,
        render_panel_markdown,
    )
    from gnd.review.runner import (
        MAX_RUN_MARKER_BYTES,
        ReviewRunError,
        canonical_panel_run,
        load_panel_run,
    )

    report_path = Path(out_path)
    run_root = Path(run_dir)
    synthesis_file = Path(synthesis_path)

    for required, description in ((run_root, "panel run directory"), (synthesis_file, "synthesis")):
        try:
            info = required.lstat()
        except FileNotFoundError:
            print(f"MISSING: {description} {required} does not exist")
            return EXIT_NO_INPUT
        except OSError as error:
            print(f"IO ERROR: {description} {required} could not be inspected: {error}")
            return EXIT_IO
        expects_directory = required is run_root
        wrong_kind = (
            not stat.S_ISDIR(info.st_mode) if expects_directory else not stat.S_ISREG(info.st_mode)
        )
        if stat.S_ISLNK(info.st_mode) or wrong_kind:
            print(f"IO ERROR: {description} {required} has a refused file type")
            return EXIT_IO
        if not expects_directory and info.st_size > MAX_RUN_MARKER_BYTES:
            print(f"ERROR: synthesis {required} exceeds the {MAX_RUN_MARKER_BYTES}-byte cap")
            return 3

    try:
        run = load_panel_run(run_root)
    except ReviewRunError as error:
        print(f"ERROR: {error}")
        return 3

    try:
        synthesis = PanelSynthesis.model_validate_json(synthesis_file.read_bytes(), strict=True)
    except OSError as error:
        print(f"IO ERROR: synthesis {synthesis_file} could not be read: {error}")
        return EXIT_IO
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"ERROR: panel synthesis failed closed validation: {error}")
        return 3

    # Checked on the RUN's own derived quorum rather than on a message from the
    # finalizer: 16 is a structural claim about the panel, and reading it out of
    # an exception string would make the band depend on prose.
    if not run.quorum_met:
        print(
            _canonical_payload(
                {
                    "schema_version": 1,
                    "tool": "gnd",
                    "command": "review finalize",
                    "gnd_version": resolve_version(),
                    "advisory": True,
                    "required_successes": REVIEW_QUORUM,
                    "successful_reviewer_ids": [
                        reviewer.value for reviewer in run.successful_reviewer_ids
                    ],
                    "quorum_met": False,
                    "outcome": "inconclusive-below-quorum",
                    "report_path": None,
                }
            )
        )
        return _review_outcome(len(run.envelopes), len(run.successful_reviewer_ids))

    try:
        result = finalize_panel_synthesis(run, synthesis)
        rendered = render_panel_markdown(run, synthesis, result)
    except ReviewReportError as error:
        print(f"ERROR: {error}")
        return 3

    try:
        descriptor = os.open(report_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        print(f"COLLISION: {report_path} already exists; nothing was written")
        return EXIT_COLLISION
    except OSError as error:
        print(f"IO ERROR: could not write {report_path}: {error}")
        return EXIT_IO
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    except OSError as error:
        print(f"IO ERROR: could not write {report_path}: {error}")
        return EXIT_IO

    print(
        _canonical_payload(
            {
                "schema_version": 1,
                "tool": "gnd",
                "command": "review finalize",
                "gnd_version": resolve_version(),
                "advisory": True,
                "required_successes": REVIEW_QUORUM,
                "run_sha256": hashlib.sha256(canonical_panel_run(run)).hexdigest(),
                "synthesis_sha256": hashlib.sha256(
                    canonical_panel_synthesis(synthesis)
                ).hexdigest(),
                "successful_reviewer_ids": [
                    reviewer.value for reviewer in run.successful_reviewer_ids
                ],
                "quorum_met": True,
                "outcome": "quorum-established",
                "agreed_concern_count": result.agreed_concern_count,
                "divergent_concern_count": result.divergent_concern_count,
                "prioritized_fix_count": result.prioritized_fix_count,
                "report_path": str(report_path),
            }
        )
    )
    return 0


def _add_format_argument(parser: argparse.ArgumentParser) -> None:
    """--format on BOTH subcommands (D-10). An invalid choice is an argparse
    usage error, so _BandSafeParser routes it to exit 64 with no payload."""
    parser.add_argument(
        "--format",
        choices=OUTPUT_FORMATS,
        default="text",
        help="output rendering: human-readable text (default) or one JSON payload",
    )


def _add_unredacted_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--unredacted",
        action="store_true",
        help=argparse.SUPPRESS,
    )


def _experiment_outcome(
    io_failures: list[str],
    missing_artifacts: list[str],
    ill_formed: list[str],
    open_obligations: list[str],
) -> int:
    """Experiment-lifecycle outcomes -> exit code. One decision function, like
    :func:`_install_outcome` and :func:`_doctor_outcome`.

    Precedence **74 > 66 > 3 > 14 > 0**, and every step of it is a claim about
    what the run is entitled to say:

    - **74** first: a target that could not be read or written says nothing at
      all about what is in it, so no other diagnosis is available. The
      ``_install_outcome`` precedent, for the same reason.
    - **66** next: a required artifact is absent, so there is nothing to parse.
      Reporting 3 would send the user to inspect a document that does not exist,
      and reporting 0 would let a missing SPEC.md read as an experiment with
      nothing wrong. Fail closed (D-22).
    - **3** next: the artifact is present and will not parse or will not
      validate. Its obligations cannot be *evaluated*, so 14 would assert "this
      experiment is still open" when the truth is "this experiment is
      unreadable". 3 is the shipped meaning of ill-formed — the same claim
      ``load_model`` makes.
    - **14** last before success: the spec parsed, was evaluated, and an
      obligation is genuinely undischarged. This is the only code here that
      reports a fact about the EXPERIMENT rather than about the files.
    - **0**: every obligation discharged.

    Ordering 66 above 3 (rather than folding "missing" into "ill-formed") is what
    keeps this function's 3 falsifiable: if both mapped to 3, no input could ever
    distinguish them and one of the two diagnoses would be unreachable.
    """
    if io_failures:
        return EXIT_IO
    if missing_artifacts:
        return EXIT_NO_INPUT
    if ill_formed:
        return 3
    if open_obligations:
        return EXIT_EXPERIMENT_OPEN
    return 0


def _cmd_exp_init(
    experiment_id: str,
    out_dir: str,
    kind: str,
    title: str,
    questions: list[tuple[str, str]],
    covers: list[Any],
    session_contract: str | None,
) -> int:
    """``gnd exp init ID --out DIR`` — scaffold ``DIR/ID/SPEC.md``.

    Every write goes through :func:`gnd.synth.paths.safe_output_path`, the
    shipped traversal guard. The output root comes from argv only — never from
    document content — and ``ID`` is constrained to
    :data:`~gnd.exp.spec.EXPERIMENT_DIR_PATTERN` before it is used to build a
    path, so a separator or a ``..`` cannot reach the guard in the first place.
    """
    from pydantic import ValidationError

    from gnd.exp.frontmatter import render_frontmatter
    from gnd.exp.session_contract import (
        SessionContractError,
        TestsAcceptance,
        read_session_contract,
    )
    from gnd.exp.spec import ExperimentSpec
    from gnd.safefs import InstallPathError
    from gnd.synth.paths import safe_output_path

    frontmatter: dict[str, Any] = {
        "id": experiment_id,
        "kind": kind,
        "title": title,
        "questions": [{"id": qid, "text": text} for qid, text in questions],
        "follows": [],
    }
    contract = None
    if session_contract is not None:
        contract_path = Path(session_contract)
        try:
            contract = read_session_contract(
                contract_path,
                experiment_root=contract_path.parent,
                experiment_id=experiment_id,
            )
        except SessionContractError as error:
            _print_issues(error.issues)
            return 3
    if kind == "work" and not covers:
        all_tests = contract is not None and all(
            isinstance(case.acceptance, TestsAcceptance) for case in contract.cases
        )
        if not all_tests:
            print(
                "USAGE ERROR: work experiments require at least one --covers entry "
                "unless every contract case uses tests mode "
                f"[{CLI_WORK_COVERS_REQUIRED_REASON}]"
            )
            return EXIT_USAGE
        frontmatter["covers_exemption"] = "tests-only"
    if covers:
        frontmatter["covers"] = [entry.model_dump(exclude_none=True) for entry in covers]
    try:
        # Validate BEFORE writing: `gnd exp init` must never emit a SPEC.md that
        # `gnd exp validate` would then refuse.
        ExperimentSpec.model_validate(frontmatter)
    except ValidationError as error:
        _print_issues(
            [
                ValidationIssue(
                    path=".".join(str(part) for part in entry["loc"]),
                    message=entry["msg"],
                    rule_id="experiment:spec-invalid",
                )
                for entry in error.errors()
            ]
        )
        return _experiment_outcome([], [], [str(error)], [])

    try:
        spec_path = safe_output_path(out_dir, f"{experiment_id}/SPEC.md")
    except InstallPathError as error:
        print(f"REFUSED: {error}")
        return _experiment_outcome([str(error)], [], [], [])

    if spec_path.parent.exists():
        # EXIT_COLLISION's shipped meaning: an existing path blocked a write and
        # NOTHING was destroyed. There is deliberately no --force here; an
        # experiment directory holds recorded conclusions and evidence, and a
        # flag that overwrites them is a flag that loses them.
        print(
            f"COLLISION: {spec_path.parent} already exists — nothing was written. "
            f"An experiment directory is never overwritten; move it aside or "
            f"choose another id."
        )
        return EXIT_COLLISION

    body = (
        f"# {experiment_id}\n\n"
        f"{title}\n\n"
        f"## Questions\n\n"
        + "".join(f"- **{qid}** — {text}\n" for qid, text in questions)
        + "\nRecord answers in CONCLUSIONS.md beside this file. Every declared "
        "question id must appear there, and every evidence pointer must name a "
        "file inside this directory.\n"
    )
    staging: Path | None = None
    try:
        output_root = spec_path.parent.parent
        output_root.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=f".{experiment_id}.staging-", dir=output_root))
        staged_spec = safe_output_path(staging, "SPEC.md")
        with staged_spec.open("xb") as handle:
            handle.write(render_frontmatter(frontmatter, body).encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
        directory_fd = os.open(staging, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        os.replace(staging, spec_path.parent)
        staging = None
    except OSError as error:
        if spec_path.parent.exists():
            print(
                f"COLLISION: {spec_path.parent} appeared while initialization "
                "was staged — nothing was overwritten."
            )
            return EXIT_COLLISION
        print(f"IO ERROR: {spec_path} could not be published: {error}")
        return _experiment_outcome([str(error)], [], [], [])
    finally:
        if staging is not None:
            shutil.rmtree(staging, ignore_errors=True)

    print(f"CREATED {spec_path}")
    for qid, text in questions:
        print(f"  declares {qid}: {text}")
    return 0


def _cmd_exp_validate(experiment_dir: str) -> int:
    """``gnd exp validate DIR`` — is this a well-formed experiment?

    Structure only. Whether the questions are GOOD questions is language, and
    language belongs to the skill (G-10); what is checked here is what can be
    checked mechanically.
    """
    from gnd.exp.spec import SpecError, read_spec

    root = Path(experiment_dir)
    spec_path = root / "SPEC.md"
    if not spec_path.is_file():
        print(
            f"MISSING: {spec_path} does not exist — an experiment is its SPEC.md, "
            f"and a directory without one is not an experiment with nothing wrong"
        )
        return _experiment_outcome([], [str(spec_path)], [], [])

    try:
        spec = read_spec(spec_path)
    except SpecError as error:
        _print_issues(error.issues)
        return _experiment_outcome([], [], [str(error)], [])

    # The id IS the directory name (EXPERIMENT_DIR_PATTERN's whole reason). A
    # mismatch is ill-formed rather than cosmetic: `follows:` references resolve
    # by directory name, so a spec whose id disagrees with its location is
    # unreachable by every reference that names it.
    actual = root.resolve().name
    if actual != spec.id:
        message = (
            f"the spec declares id {spec.id!r} but sits in directory {actual!r}; "
            f"follows: references resolve by directory name, so this experiment "
            f"cannot be referenced by the id it claims"
        )
        _print_issues(
            [ValidationIssue(path="id", message=message, rule_id="experiment:spec-invalid")]
        )
        return _experiment_outcome([], [], [message], [])

    print(f"VALID {spec_path}")
    print(f"  id: {spec.id}")
    print(f"  kind: {spec.kind}")
    print(f"  title: {spec.title}")
    print(
        f"  declares {len(spec.questions)} question(s): " + ", ".join(q.id for q in spec.questions)
    )
    if spec.follows:
        print("  follows: " + ", ".join(spec.follows))
    return _experiment_outcome([], [], [], [])


def _cmd_exp_author_expectation(
    experiment_dir: str,
    case_id: str,
    output_id: str,
    candidate_path: str,
    source: str,
    media_type: str,
    encoding: str,
) -> int:
    """Author one pathless exact expectation, then prove its bytes are gone."""

    from gnd.artifacts import ArtifactError
    from gnd.exp.expectation_author import (
        ExpectationAuthorError,
        SurvivingAnswerError,
        author_expectation,
    )
    from gnd.exp.session_contract import (
        SessionContractError,
        TestsAcceptance,
        read_session_contract,
    )
    from gnd.exp.spec import KIND_POLICY, SpecError, read_spec

    root = Path(experiment_dir)
    spec_path = root / "SPEC.md"
    try:
        spec_info = spec_path.lstat()
    except FileNotFoundError:
        print(f"MISSING: required experiment artifact {spec_path} does not exist")
        return EXIT_NO_INPUT
    except OSError as error:
        print(f"IO ERROR: required experiment artifact {spec_path} is unreadable: {error}")
        return EXIT_IO
    if stat.S_ISLNK(spec_info.st_mode) or not stat.S_ISREG(spec_info.st_mode):
        print(f"IO ERROR: required experiment artifact {spec_path} has a refused file type")
        return EXIT_IO
    try:
        spec = read_spec(spec_path)
    except SpecError as error:
        _print_issues(error.issues)
        return 3
    if spec.id != root.name:
        print(f"ERROR: SPEC.md id {spec.id!r} does not match directory {root.name!r}")
        return 3
    if not KIND_POLICY[spec.kind].expectation_authorable:
        print(
            "ERROR: this experiment kind does not allow gnd exp author-expectation: "
            f"not {spec.kind!r}"
        )
        return 3

    try:
        contract = read_session_contract(
            root / "session.contract.json",
            experiment_root=root,
            experiment_id=spec.id,
        )
    except SessionContractError:
        # Authoring is allowed to repair a temporarily incomplete exact-bytes
        # contract. The production author below performs its own staged load;
        # this preflight exists only for the tests-mode kind gate.
        contract = None
    selected_case = (
        next((case for case in contract.cases if case.case_id == case_id), None)
        if contract is not None
        else None
    )
    if selected_case is not None and isinstance(selected_case.acceptance, TestsAcceptance):
        print(
            "USAGE ERROR: author-expectation cannot author bytes for a tests-mode case "
            f"[{KIND_AUTHOR_EXPECTATION_TESTS_REASON}]"
        )
        return EXIT_USAGE

    try:
        authored = author_expectation(
            root,
            experiment_id=spec.id,
            case_id=case_id,
            output_id=output_id,
            candidate_path=candidate_path,
            source=source,
            media_type=media_type,
            encoding=encoding,
        )
    except SurvivingAnswerError as error:
        print("REFUSED: produced answer bytes still exist under the experiment root:")
        for path in error.paths:
            print(f"  {path}")
        return 3
    except ExpectationAuthorError as error:
        print(f"REFUSED: {error}")
        return 3
    except SessionContractError as error:
        _print_issues(error.issues)
        return 3
    except ArtifactError as error:
        print(f"IO ERROR: expectation could not be authored safely: {error}")
        return EXIT_IO
    except OSError as error:
        print(f"IO ERROR: expectation could not be authored: {error}")
        return EXIT_IO

    print(f"AUTHORED {authored.contract_path}")
    print(f"  case: {authored.case_id}")
    print(f"  output: {authored.output_id} -> candidate/{authored.candidate_path}")
    print(f"  sha256: {authored.sha256}")
    print(f"  deleted: {authored.deleted_source}")
    print("  answer copies under experiment root: 0")
    return 0


def _cmd_exp_close(experiment_dir: str) -> int:
    """``gnd exp close DIR`` — has this experiment discharged what it declared?

    A VALIDATOR returning an exit code, never a state machine (G-11): nothing is
    written, no status is recorded, and running it twice over an unchanged
    directory answers the same way both times.

    The verdict itself lives in :func:`gnd.exp.close.evaluate_close` and
    :func:`gnd.exp.close.close_outcome`. What lives HERE is the ordering of the
    file-level bands around it, which :func:`_experiment_outcome` decides on the
    shipped precedence 74 > 66 > 3 > 14 > 0:

    - a missing ``SPEC.md`` is **66**. Without it there is no ``declared`` set,
      so the gate's subtraction has no left operand and 14 would assert
      something about an experiment that is not there.
    - a missing ``CONCLUSIONS.md`` is **14**, and that difference from the line
      above is deliberate. 66 would say "a required input is missing" and send a
      reader hunting for a file; the truth is narrower and more useful — this
      experiment has not concluded, which is exactly what band 14 means. It is
      the gate's own verdict, not a complaint about the filesystem.
    - an unparseable or schema-invalid document is **3**: the obligations could
      not be EVALUATED, and 14 would claim they were and found wanting.

    A ``kind: codegen`` experiment carries one obligation more than the others
    (G-17 = SC4): a ``conformance.json`` recorded beside its documents, whose
    ``findings`` array is empty and whose assertions all ran. That branch lives in
    :func:`gnd.exp.close._conformance_findings` and reaches this function as an
    ordinary finding, so the band stays **14** — the experiment did not discharge
    what it declared. It is deliberately not 13: 13 is a claim about a generated
    project whose repair is ``gnd codegen``, and this is a claim about an
    experiment whose repair is to re-measure and re-conclude.
    """
    from gnd.exp.close import CONCLUSIONS_FILENAME, close_outcome, evaluate_close
    from gnd.exp.conclusions import ConclusionsError, read_conclusions
    from gnd.exp.spec import SpecError, read_spec

    root = Path(experiment_dir)
    spec_path = root / "SPEC.md"
    if not spec_path.is_file():
        print(
            f"MISSING: {spec_path} does not exist — there is no declared question "
            f"set to close against, so nothing can be said about this directory"
        )
        return _experiment_outcome([], [str(spec_path)], [], [])

    try:
        spec = read_spec(spec_path)
    except SpecError as error:
        _print_issues(error.issues)
        return _experiment_outcome([], [], [str(error)], [])

    actual = root.resolve().name
    if actual != spec.id:
        message = (
            f"the spec declares id {spec.id!r} but sits in directory {actual!r}; "
            f"follows: references resolve by directory name, so this experiment "
            f"cannot be closed under a location it does not declare"
        )
        _print_issues(
            [ValidationIssue(path="id", message=message, rule_id="experiment:spec-invalid")]
        )
        return _experiment_outcome([], [], [message], [])

    conclusions_path = root / CONCLUSIONS_FILENAME
    if not conclusions_path.is_file():
        message = (
            f"{conclusions_path} does not exist; this experiment declared "
            f"{len(spec.questions)} question(s) and has recorded no conclusions, "
            f"so it is OPEN. Every declared id must be resolved — an honest "
            f"'unanswered' with a reason closes it, a silence does not."
        )
        print(f"OPEN: {message}")
        return _experiment_outcome([], [], [], [message])

    try:
        conclusions = read_conclusions(conclusions_path)
    except ConclusionsError as error:
        _print_issues(error.issues)
        return _experiment_outcome([], [], [str(error)], [])

    # The conclusions declare which experiment they belong to, so that claim is
    # checked rather than decorative — otherwise a CONCLUSIONS.md copied from a
    # sibling resolves THIS experiment's ids against THAT one's work. Ill-formed
    # (3) rather than open (14): the document is not this experiment's
    # conclusions at all, so its obligations were never evaluated. Same band and
    # same reasoning as `gnd exp validate`'s id/directory refusal.
    if conclusions.id != spec.id:
        message = (
            f"{CONCLUSIONS_FILENAME} declares id {conclusions.id!r} but sits beside "
            f"a SPEC.md declaring {spec.id!r}; these are not this experiment's "
            f"conclusions"
        )
        _print_issues(
            [ValidationIssue(path="id", message=message, rule_id="experiment:conclusions-invalid")]
        )
        return _experiment_outcome([], [], [message], [])

    try:
        result = evaluate_close(spec, conclusions, spec_path)
    except OSError as error:
        print(f"IO ERROR: {root} could not be inspected: {error}")
        return _experiment_outcome([str(error)], [], [], [])

    print(f"  declared: {', '.join(result.declared)}")
    print(f"  resolved: {', '.join(result.resolved) or '(none)'}")
    for finding in result.findings:
        print(f"  [{finding.kind}] {finding.id}: {finding.message}")

    if result.findings:
        print(
            f"OPEN {root} — {len(result.findings)} obligation(s) undischarged "
            f"({EXIT_EXPERIMENT_OPEN})"
        )
        return close_outcome(result)

    # The outcomes are reported AFTER the verdict was computed, and reporting
    # them is all that was ever done with them: the gate enforces completeness
    # and honesty, never a positive result (G-12), so an all-'unanswered'
    # experiment prints here exactly like an all-'answered' one.
    print(f"CLOSED {root}")
    for resolution in conclusions.resolves:
        print(f"  {resolution.id}: {resolution.outcome} — cites {resolution.evidence}")
    return close_outcome(result)


def _next_session_run_root(experiment_root: Path) -> Path:
    """Return the next run directory, above every index already present.

    **The index is chronology, and allocation is what makes that true.** This
    used to return the first unused slot, which refilled holes: delete an old
    ``run-0001`` from a history that still held ``run-0002``, and the NEXT run
    — the newest one — was allocated ``run-0001``, below a run that preceded
    it. ``gnd exp close``'s work obligation reads the highest-indexed run as
    the latest launch (O-18), so under hole-refilling an older acceptance could
    answer for a newer refusal, and a genuinely latest acceptance could be
    refused by a stale higher number. The allocator and the gate held
    incompatible notions of "latest", and the gate was reading a fact the
    allocator did not provide.

    Allocating strictly above the maximum present index makes the gate's
    premise true by construction. Numbers are still not reused while their
    directory exists, and the sequence remains gap-free for every history this
    allocator produces on its own; a hole left by a hand-deleted run stays a
    hole rather than being backfilled under a newer run's identity.
    """

    # The gate that READS these names owns their shape, so the allocator
    # imports it rather than restating a second pattern that could drift from
    # the first — the two disagreeing about what a run is called is precisely
    # the class of defect this function was just repaired for.
    from gnd.exp.close import MAX_SESSION_RUN_INDEX, SESSION_RUN_PATTERN

    runs = experiment_root / "runs"
    try:
        info = runs.lstat()
    except FileNotFoundError:
        runs.mkdir(mode=0o755)
    else:
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise OSError(f"session runs root {runs} must be a real directory")

    highest = 0
    for entry in runs.iterdir():
        matched = SESSION_RUN_PATTERN.match(entry.name)
        if matched:
            highest = max(highest, int(entry.name.removeprefix("run-")))
    if highest >= MAX_SESSION_RUN_INDEX:
        raise OSError(f"session runs root {runs} has no available numbered run id")
    return runs / f"run-{highest + 1:04d}"


def _run_tests_mode_bridge(
    contract: Any,
    *,
    test_argv: list[str],
    candidate_root: Path,
    experiment_root: Path,
    run_root: Path,
    contract_sha256: str,
) -> Any:
    """Keep the tests lane behind one programmatic CLI bridge call."""

    from gnd.exp.tests_runner import run_tests_mode

    return asyncio.run(
        run_tests_mode(
            contract,
            argv=test_argv,
            candidate_root=candidate_root,
            experiment_root=experiment_root,
            run_root=run_root,
            contract_sha256=contract_sha256,
        )
    )


def _cmd_exp_run(
    experiment_dir: str,
    adapter: str | None,
    adapter_policy: str | None,
    wall_seconds: float | None,
    test_argv: list[str],
) -> int:
    """Bridge one validated data-driven experiment into ``run_session`` once."""

    from gnd.agents import AgentAdapterId, AgentCLIError
    from gnd.artifacts import canonical_json_bytes
    from gnd.declared_adapter import invoke_declared_adapter
    from gnd.exp.adapter_policy import AdapterPolicyError, read_adapter_policy
    from gnd.exp.session import (
        case_payload_versions,
        case_redaction,
        run_gnd_verifier,
        run_session,
    )
    from gnd.exp.session_contract import (
        DECLARED_ADAPTER_SESSION_CONTRACT_VERSION,
        TESTS_ARGV_ECHO_MISMATCH_REASON,
        SessionContractError,
        TestsAcceptance,
        read_session_contract,
    )
    from gnd.exp.session_store import SessionResult
    from gnd.exp.spec import KIND_POLICY, SpecError, read_spec

    root = Path(experiment_dir)
    try:
        root_info = root.lstat()
    except FileNotFoundError:
        print(f"MISSING: experiment directory {root} does not exist")
        return EXIT_NO_INPUT
    except OSError as error:
        print(f"IO ERROR: experiment directory {root} could not be inspected: {error}")
        return EXIT_IO
    if stat.S_ISLNK(root_info.st_mode) or not stat.S_ISDIR(root_info.st_mode):
        print(f"IO ERROR: experiment directory {root} must be a real directory")
        return EXIT_IO

    spec_path = root / "SPEC.md"
    contract_path = root / "session.contract.json"
    candidate_root = root / "candidate"
    for required in (spec_path, contract_path, candidate_root):
        try:
            required_info = required.lstat()
        except FileNotFoundError:
            print(f"MISSING: required session artifact {required} does not exist")
            return EXIT_NO_INPUT
        except OSError as error:
            print(f"IO ERROR: required session artifact {required} is unreadable: {error}")
            return EXIT_IO
        expected_directory = required == candidate_root
        wrong_kind = (expected_directory and not stat.S_ISDIR(required_info.st_mode)) or (
            not expected_directory and not stat.S_ISREG(required_info.st_mode)
        )
        if stat.S_ISLNK(required_info.st_mode) or wrong_kind:
            print(f"IO ERROR: required session artifact {required} has a refused file type")
            return EXIT_IO

    try:
        spec = read_spec(spec_path)
    except SpecError as error:
        _print_issues(error.issues)
        return 3
    if spec.id != root.name:
        print(f"ERROR: SPEC.md id {spec.id!r} does not match directory {root.name!r}")
        return 3
    if not KIND_POLICY[spec.kind].session_runnable:
        print(f"ERROR: experiment kind {spec.kind!r} is not session-runnable")
        return 3

    try:
        contract = read_session_contract(
            contract_path,
            experiment_root=root,
            experiment_id=spec.id,
        )
    except SessionContractError as error:
        _print_issues(error.issues)
        return 3

    declared_session = contract.schema_version in {DECLARED_ADAPTER_SESSION_CONTRACT_VERSION, 7, 8}
    if declared_session:
        if adapter is not None or adapter_policy is None:
            print(
                "USAGE ERROR: schema-v6/v7 contracts require --adapter-policy and forbid --adapter"
            )
            return EXIT_USAGE
    elif adapter is None or adapter_policy is not None:
        print(
            "USAGE ERROR: legacy contracts require --adapter claude|codex and forbid "
            "--adapter-policy"
        )
        return EXIT_USAGE

    resolved_policy = None
    if declared_session:
        assert contract.adapter is not None
        try:
            resolved_policy = read_adapter_policy(
                adapter_policy,
                declaration=contract.adapter,
            )
        except AdapterPolicyError as error:
            if error.kind == "missing":
                print(f"MISSING: {error}")
                return EXIT_NO_INPUT
            if error.kind == "io":
                print(f"IO ERROR: {error}")
                return EXIT_IO
            print(f"REFUSED: {error}")
            return 3

    tests_acceptances = [
        case.acceptance for case in contract.cases if isinstance(case.acceptance, TestsAcceptance)
    ]
    if tests_acceptances and not test_argv:
        print(
            "USAGE ERROR: a tests-mode contract requires at least one --test-argv word "
            f"[{CLI_TEST_ARGV_REQUIRED_REASON}]"
        )
        return EXIT_USAGE
    if not tests_acceptances and test_argv:
        print(
            "USAGE ERROR: --test-argv is forbidden when the contract has no tests case "
            f"[{CLI_TEST_ARGV_FORBIDDEN_REASON}]"
        )
        return EXIT_USAGE
    tests_only = len(tests_acceptances) == len(contract.cases)
    if tests_acceptances:
        encoded_argv = json.dumps(
            test_argv,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        actual_echo = hashlib.sha256(encoded_argv).hexdigest()
        if actual_echo != tests_acceptances[0].test_argv_sha256:
            print(
                "REFUSED: --test-argv does not match the contract's common echo "
                f"[{TESTS_ARGV_ECHO_MISMATCH_REASON}]"
            )
            return 3

    if wall_seconds is not None:
        if contract.wall_seconds is None or wall_seconds > contract.wall_seconds:
            print(
                "USAGE ERROR: --wall-seconds may only tighten the contract's "
                "declared finite wall_seconds bound"
            )
            return EXIT_USAGE
        contract = contract.model_copy(update={"wall_seconds": wall_seconds})

    if tests_only:
        try:
            run_root = _next_session_run_root(root)
            contract_sha256 = hashlib.sha256(contract_path.read_bytes()).hexdigest()
            outcome = _run_tests_mode_bridge(
                contract,
                test_argv=test_argv,
                candidate_root=candidate_root,
                experiment_root=root,
                run_root=run_root,
                contract_sha256=contract_sha256,
            )
            print(outcome.result_bytes.decode("utf-8"), end="")
            return outcome.exit_code
        except (OSError, ValueError) as error:
            print(f"IO ERROR: tests-mode session could not be published: {error}")
            return EXIT_IO
        except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
            print(f"INTERNAL ERROR: {type(error).__name__}: {error}")
            return EXIT_INTERNAL

    try:
        run_root = _next_session_run_root(root)
        contract_sha256 = hashlib.sha256(contract_path.read_bytes()).hexdigest()
        selected_adapter = None if adapter is None else AgentAdapterId(adapter)
        # D-P3.4: each case's digest-bound model selects the payload version
        # its verifier evidence must carry; a structured case promotes the feedback
        # wire to schema version 3 inside run_session.
        expected_versions = case_payload_versions(contract, root)
        session_redaction = case_redaction(contract, root)

        tests_rows: dict[str, Any] | None = None
        tests_verifier_failed = False

        async def verifier(case: Any, snapshot: Path) -> tuple[int, bytes]:
            nonlocal tests_rows, tests_verifier_failed
            if isinstance(case.acceptance, TestsAcceptance):
                if tests_rows is None:
                    from gnd.exp.tests_runner import TestsSessionResult, run_tests_mode

                    tests_outcome = await run_tests_mode(
                        contract,
                        argv=test_argv,
                        candidate_root=snapshot,
                        experiment_root=root,
                        run_root=run_root / "tests-verifier",
                        contract_sha256=contract_sha256,
                    )
                    parsed = TestsSessionResult.model_validate_json(tests_outcome.result_bytes)
                    tests_rows = {row.case_id: row for row in parsed.feedback}
                    tests_verifier_failed = parsed.disposition == "verifier-failure"
                row = tests_rows.get(case.case_id)
                if row is None:
                    raise ValueError(f"tests runner omitted case {case.case_id!r}")
                feedback = row.model_dump(mode="json", exclude={"case_id", "role"})
                accepted = row.reason is None and set(row.required) <= set(row.passing)
                process_exit = 70 if tests_verifier_failed else 0 if accepted else 1
                return process_exit, canonical_json_bytes(feedback)
            return await run_gnd_verifier(
                case,
                snapshot,
                experiment_root=root,
                timeout_seconds=contract.wall_seconds or 300.0,
            )

        prompt = (
            "Modify only the current candidate directory so it satisfies every "
            f"required case in the caller-validated contract at {contract_path.absolute()}."
        )
        result = asyncio.run(
            run_session(
                contract,
                contract_sha256=contract_sha256,
                adapter_id=selected_adapter,
                adapter_policy=resolved_policy,
                prompt=prompt,
                candidate_root=candidate_root,
                run_root=run_root,
                verifier=verifier,
                declared_invoker=(invoke_declared_adapter if declared_session else None),
                expected_payload_versions=expected_versions,
                redaction=session_redaction,
            )
        )
        result_bytes = (run_root / "result.json").read_bytes()
        persisted = SessionResult.model_validate_json(result_bytes)
        if persisted != result:
            print("INTERNAL ERROR: persisted session result disagrees with controller result")
            return EXIT_INTERNAL
        print(result_bytes.decode("utf-8"), end="")
        return _session_result_exit(persisted)
    except AgentCLIError as error:
        print(f"MISSING: {error}")
        return EXIT_NO_INPUT
    except (OSError, ValueError) as error:
        print(f"IO ERROR: data-driven session could not be published: {error}")
        return EXIT_IO
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"INTERNAL ERROR: {type(error).__name__}: {error}")
        return EXIT_INTERNAL


def _parse_question(value: str) -> tuple[str, str]:
    """Argparse converter for ``--question ID=TEXT``."""
    identifier, separator, text = value.partition("=")
    if not separator or not identifier.strip() or not text.strip():
        raise argparse.ArgumentTypeError(
            f"expected ID=TEXT, got {value!r} — a question needs both an id the "
            f"conclusions can resolve and the text it is asking"
        )
    return identifier.strip(), text.strip()


def _parse_covers(value: str) -> Any:
    """Argparse converter for one compact JSON CoversEntry."""

    from pydantic import ValidationError

    from gnd.exp.spec import CoversEntry

    try:
        document = json.loads(value)
        return CoversEntry.model_validate(document)
    except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError(
            f"expected a closed JSON covers entry with exactly one of operation, "
            f"constraint, fact_type, or derivation: {error}"
        ) from error


def _add_target_arguments(parser: argparse.ArgumentParser) -> None:
    """D-08's target flag surface, defined once.

    ``install`` uses it now; ``doctor`` and ``uninstall`` (plan 01.2-04) use the
    same helper, so three commands cannot drift in how they resolve a target —
    the sibling of ``_add_format_argument``'s reason for existing.

    ``--global`` cannot use argparse's derived attribute name: ``global`` is a
    Python keyword, so ``args.global`` is a syntax error. Both scope flags
    therefore store a constant into an explicitly named ``scope`` destination.
    """
    parser.add_argument(
        "--claude",
        action="store_true",
        help="target Claude Code's skills directory (default: both runtimes)",
    )
    parser.add_argument(
        "--codex",
        action="store_true",
        help="target Codex CLI's skills directory (default: both runtimes)",
    )
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument(
        "--global",
        dest="scope",
        action="store_const",
        const="global",
        help="user level (DEFAULT): ~/.claude/skills and $CODEX_HOME/skills (~/.codex/skills)",
    )
    scope.add_argument(
        "--project",
        dest="scope",
        action="store_const",
        const="project",
        help="this project: ./.claude/skills and ./.codex/skills",
    )
    parser.set_defaults(scope="global")


def _install_outcome(io_failures: list[str], collisions: list[str]) -> int:
    """Lifecycle outcomes -> exit code. One decision function, like ``_band()``.

    Precedence: an I/O failure outranks a collision, because a target that could
    not be read or written says nothing at all about what is in it, while a
    collision is a complete and accurate report.

    ``install`` never returns :data:`EXIT_DRIFT`: drift is what install *repairs*,
    and reporting it is ``doctor``'s job (plan 01.2-04).
    """
    if io_failures:
        return EXIT_IO
    if collisions:
        return EXIT_COLLISION
    return 0


def _doctor_outcome(report: install_module.DoctorReport) -> int:
    """Diagnosis -> exit code. One decision function, like ``_band()``.

    Precedence **12 > 11 > 10 > 0**:

    - 12 first, because "nothing is installed anywhere" makes every other
      question moot; reporting drift over an install that does not exist sends
      the user to repair a directory they never wrote.
    - 11 next: a collision means a file GND does not own is sitting where GND
      would place one. Nothing was destroyed, and the repair (``--force``, or
      moving the file aside) differs from the repair for drift (``install``).
    - 10 last: stale, missing, modified — and an untrusted receipt, which is
      folded in here rather than given a code of its own, because the user's
      next action is the same either way: look, then re-install.

    :data:`EXIT_DRIFT` is declared in this module by plan 01.2-02 and returned
    by nothing until here — install *repairs* drift, so drift was never an
    install outcome.
    """
    if not report.installed_anywhere():
        return EXIT_NO_INSTALL
    if report.has_collision():
        return EXIT_COLLISION
    if report.has_drift():
        return EXIT_DRIFT
    return 0


def _render_states(states: list[install_module.SkillFileState]) -> None:
    """Per-file detail, capped exactly as the population loader caps its issue
    summary: a five-target run over 29 files each would otherwise bury the
    headline, and a report nobody can read is not a report."""
    interesting = [record for record in states if record.state != "current"]
    shown = interesting[: install_module.MAX_REPORTED_STATES]
    for record in shown:
        detail = f": {record.detail}" if record.detail else ""
        print(f"  [{record.state}] {record.relpath}{detail}")
    if len(interesting) > len(shown):
        print(
            f"  ... and {len(interesting) - len(shown)} further record(s) elided "
            f"(cap {install_module.MAX_REPORTED_STATES})"
        )


def _render_diagnosis(diagnosis: install_module.TargetDiagnosis) -> None:
    print(f"{diagnosis.target.label()} -> {diagnosis.target.root}")
    if diagnosis.problem:
        print(f"  REFUSED: {diagnosis.problem}")
        print("  Nothing was inferred from it. No state is reported for this root.")
    elif not diagnosis.installed:
        print("  not installed")
    else:
        counts = diagnosis.counts()
        summary = ", ".join(f"{state}={counts[state]}" for state in sorted(counts)) or "no assets"
        provenance = f"{diagnosis.mode} mode" if diagnosis.mode else "no receipt (partial install)"
        version = (
            f", {install_module.DISTRIBUTION} {diagnosis.version}" if diagnosis.version else ""
        )
        stamp = f", placed {diagnosis.installed_at}" if diagnosis.installed_at else ""
        print(f"  installed ({provenance}{version}{stamp}): {summary}")
        _render_states(diagnosis.states)
    if diagnosis.alternative_root is not None:
        print(
            f"  note: {diagnosis.alternative_root} is a known alternative Codex skills "
            f"location that GND does not write (the published docs and the shipped "
            f"binary disagree; both roots were observed live)"
        )


def _cmd_doctor(*, claude: bool, codex: bool) -> int:
    """Report the state of every placed asset, at BOTH scopes (PKG-07).

    The scope flags are accepted through the shared helper and deliberately not
    honoured for resolution: runtime skill precedence puts the user level ahead
    of the project level, so a user who installs into a project and sees no
    effect is usually being shadowed by an earlier user-level install. A doctor
    that inspected only the scope it was pointed at could not see that.

    Text-only by D-25.
    """
    project = Path.cwd()
    runtimes = [name for name, on in (("claude", claude), ("codex", codex)) if on]
    runtimes = runtimes or list(install_module.RUNTIMES)

    try:
        skills_root = install_module.packaged_skills_root()
    except install_module.InstallError as error:
        print(f"ERROR: {error}")
        return EXIT_IO

    targets = [
        target
        for scope in install_module.SCOPES
        for target in install_module.resolve_targets(runtimes, scope, project)
    ]
    report = install_module.diagnose(skills_root, targets)

    verdict = "on PATH" if report.executable_on_path else "NOT on PATH"
    print(f"executable directory: {report.executable_dir} ({verdict})")
    if not report.executable_on_path:
        print(
            "  a successful install whose bin directory is not on PATH presents as "
            "`gnd: command not found`. Fix it with `uv tool update-shell`, then open "
            "a new shell."
        )
    print(
        "checking both scopes regardless of the flags given (skill precedence is "
        "user level over project level)"
    )

    for diagnosis in report.targets:
        _render_diagnosis(diagnosis)

    for row in report.shadowing:
        print(
            f"SHADOWING: the {row.runtime} user-scope install of '{row.skill}' at "
            f"{row.shadowing_root} takes precedence over the project-scope one at "
            f"{row.shadowed_root} — edits to the project copy will appear to do nothing."
        )

    outcome = _doctor_outcome(report)
    if outcome == EXIT_NO_INSTALL:
        print("no GND install manifest found at any resolved target root (listed above).")
    return outcome


def _uninstall_outcome(io_failures: list[str], retained: list[str], installed: bool) -> int:
    """Removal outcome -> exit code. Sibling of ``_doctor_outcome``.

    Precedence: an I/O-class refusal outranks everything, then "nothing was
    installed", then "something GND-owned was left behind".

    A receipt this build could not trust — an unrecognised schema, or an entry
    the traversal guard refused — returns :data:`EXIT_IO` rather than
    :data:`EXIT_DRIFT`. 74 already means "an unreadable install receipt, or a path
    refused by the traversal guard" in this module's own docstring, and the
    distinction is load-bearing: 10 says "files were retained after a removal ran",
    while a refusal means no removal was attempted at all. Reporting the first as
    the second would tell a script that the uninstall happened.
    """
    if io_failures:
        return EXIT_IO
    if not installed:
        return EXIT_NO_INSTALL
    if retained:
        return EXIT_DRIFT
    return 0


def _cmd_uninstall(*, claude: bool, codex: bool, scope: str) -> int:
    """Remove GND's placed skills from every requested target root (PKG-07).

    Unlike ``doctor``, this honours the scope flags exactly as given: ``doctor``
    inspects both scopes because it only reports, and a command that DELETES must
    touch nothing the user did not point it at.

    Text-only by D-25.
    """
    project = Path.cwd()
    runtimes = [name for name, on in (("claude", claude), ("codex", codex)) if on]

    try:
        skills_root = install_module.packaged_skills_root()
    except install_module.InstallError as error:
        print(f"ERROR: {error}")
        return EXIT_IO

    candidates = install_module.resolve_targets(
        runtimes or list(install_module.RUNTIMES), scope, project
    )

    io_failures: list[str] = []
    retained: list[str] = []
    installed = False
    for target in candidates:
        try:
            manifest = install_module.read_manifest(target.root)
        except install_module.InstallPathError as error:
            print(f"REFUSED at {target.root}: {error}")
            print("  Nothing was deleted at this root, or anywhere else.")
            io_failures.append(str(target.root))
            continue
        except install_module.InstallError as error:
            print(f"REFUSED at {target.root}: {error}")
            io_failures.append(str(target.root))
            continue
        if manifest is None:
            print(f"{target.label()} -> {target.root}\n  not installed")
            continue
        installed = True

        try:
            result = install_module.remove(skills_root, target, manifest)
        except install_module.InstallPathError as error:
            print(f"REFUSED at {target.root}: {error}")
            print("  The refusal is total: nothing was deleted at this root.")
            io_failures.append(str(target.root))
            continue
        except (install_module.InstallError, OSError) as error:
            print(f"ERROR at {target.root}: {error}")
            io_failures.append(str(target.root))
            continue

        print(f"{target.label()} -> {target.root}")
        print(
            f"  removed {len(result.removed)} artifact(s), pruned "
            f"{len(result.pruned)} director(y/ies)"
            + (", removed the install receipt" if result.manifest_removed else "")
        )
        if result.retained:
            retained.extend(f"{target.root}/{record.relpath}" for record in result.retained)
            _render_states(result.retained)
            print(
                f"  {len(result.retained)} file(s) were kept: GND only deletes files whose "
                f"bytes still match what it placed. Remove them yourself if you want them "
                f"gone. The install receipt was kept with them."
            )

    if not installed and not io_failures:
        print("no GND install manifest found at any resolved target root:")
        for target in candidates:
            print(f"  {target.label()}: {target.root}")

    return _uninstall_outcome(io_failures, retained, installed)


def _render_target_result(
    target: install_module.InstallTarget,
    result: install_module.ApplyResult,
) -> None:
    print(f"{target.label()} -> {target.root}")
    # WR-05: the headline used to be chosen on `writes` alone, so "already
    # current (0 writes)" fired for runs that wrote nothing BECAUSE everything
    # collided or was modified — a success line two rows above its own
    # contradiction. Currency is a claim about the tree, not about the counter.
    if result.writes:
        print(f"  placed {result.writes} file(s)")
    elif result.skipped or result.collisions:
        print(f"  nothing placed ({len(result.skipped)} record(s) not acted on, see below)")
    else:
        print("  already current (0 writes)")
    if result.pruned:
        print(
            f"  removed {len(result.pruned)} file(s) this version no longer ships "
            f"(bytes still matched what GND placed): {', '.join(result.pruned)}"
        )
    if not result.skipped:
        return
    shown = result.skipped[: install_module.MAX_REPORTED_STATES]
    for record in shown:
        print(f"  [{record.state}] {record.relpath}: {record.detail}")
    if len(result.skipped) > len(shown):
        print(
            f"  ... and {len(result.skipped) - len(shown)} further record(s) elided "
            f"(cap {install_module.MAX_REPORTED_STATES})"
        )


def _cmd_install(
    *,
    claude: bool,
    codex: bool,
    scope: str,
    force: bool,
    symlink: bool,
    sync: bool,
) -> int:
    """Place every packaged skill into every requested target root (PKG-02).

    Text-only by D-25 — see the subcommand's help text for why that is a decision
    rather than an omission.
    """
    project = Path.cwd()
    mode = "symlink" if symlink else "copy"

    try:
        skills_root = install_module.packaged_skills_root()
    except install_module.InstallError as error:
        print(f"ERROR: {error}")
        return EXIT_IO

    if sync:
        candidates = install_module.standard_targets(project)
    else:
        runtimes = [name for name, on in (("claude", claude), ("codex", codex)) if on]
        candidates = install_module.resolve_targets(
            runtimes or list(install_module.RUNTIMES), scope, project
        )

    io_failures: list[str] = []
    collisions: list[str] = []
    # This pass answers ONE question — which candidate roots `--sync` has
    # anything to sync — and reports a root whose receipt cannot be read. The
    # manifest it reads is deliberately discarded: see the re-read below.
    targets: list[install_module.InstallTarget] = []
    for target in candidates:
        try:
            manifest = install_module.read_manifest(target.root)
        except install_module.InstallError as error:
            print(f"ERROR at {target.root}: {error}")
            io_failures.append(str(target.root))
            continue
        if sync and manifest is None:
            continue
        targets.append(target)

    if sync and not targets and not io_failures:
        # D-10's self-locating property has nothing to locate. Saying WHICH roots
        # were examined is the difference between a diagnosable answer and a
        # mystery, since there is deliberately no central registry to inspect.
        print("no GND install manifest found at any standard target root:")
        for target in candidates:
            print(f"  {target.label()}: {target.root}")
        return EXIT_NO_INSTALL

    for target in targets:
        # F-01: read the receipt HERE, immediately before this target is planned
        # and applied — never once for every target up front. Two requested
        # targets can resolve to ONE physical directory (a user symlinking
        # `.codex/skills -> ../.claude/skills` is a reasonable response to D-21's
        # unresolved Codex-root question), in which case the first target's apply
        # writes the very receipt the second target must read. Carrying a stale
        # `manifest=None` across that write made the second pass plan all 29
        # files as `collided`, report "GND did not place it" about files GND had
        # placed milliseconds earlier in the same command, and overwrite a
        # receipt owning 29 real files with an empty one.
        #
        # Re-reading was chosen over detecting the aliasing (comparing each
        # resolved root's st_dev/st_ino) because it fixes the general defect
        # rather than one instance of it: apply()'s contract is that `manifest`
        # describes the root as it is NOW, and any writer between the two reads —
        # a sibling target, a concurrent `gnd install`, the user — falsifies a
        # value cached before the write. An st_dev/st_ino check would make these
        # two targets agree while leaving that contract broken everywhere else.
        try:
            manifest = install_module.read_manifest(target.root)
        except install_module.InstallError as error:
            print(f"ERROR at {target.root}: {error}")
            io_failures.append(str(target.root))
            continue
        effective_mode = manifest.mode if (sync and manifest is not None) else mode
        if manifest is not None and manifest.mode != effective_mode:
            # Two shapes at one root is not a state this installer will produce:
            # copy files sitting beneath a symlinked skill directory would be
            # written THROUGH the link, into the distribution itself.
            print(
                f"{target.label()} -> {target.root}\n"
                f"  BLOCKED: this root was installed in {manifest.mode!r} mode and you "
                f"asked for {effective_mode!r}. Nothing was changed. Re-run in "
                f"{manifest.mode!r} mode, or remove the root and install again."
            )
            collisions.append(str(target.root))
            continue
        try:
            records = install_module.plan(skills_root, target, manifest, mode=effective_mode)
            result = install_module.apply(
                skills_root,
                target,
                records,
                mode=effective_mode,
                force=force,
                manifest=manifest,
            )
        except install_module.InstallPathError as error:
            print(f"REFUSED at {target.root}: {error}")
            io_failures.append(str(target.root))
            continue
        except (install_module.InstallError, OSError) as error:
            print(f"ERROR at {target.root}: {error}")
            io_failures.append(str(target.root))
            continue

        _render_target_result(target, result)
        if result.collisions:
            collisions.extend(f"{target.root}/{rel}" for rel in result.collisions)
            print(
                f"  {len(result.collisions)} unmanaged file(s) blocked a write. Nothing "
                f"was destroyed — re-run with --force to replace them."
            )

    return _install_outcome(io_failures, collisions)


def _emit_boundary_corpus(
    *,
    model: Any,
    baseline: Any,
    baseline_seed_value: int,
    baseline_expectations: dict[str, Any],
    out_root: Path,
    build_sidecar: Any,
    written: list[dict[str, Any]],
    not_derivable: list[dict[str, Any]],
    output_format: str,
    fail: Any,
    abort_quarantine: Any,
    filename_suffix: str = "",
) -> int | None:
    """Derive, admit and write the boundary class (D-06). ``None`` on success.

    Every case carries its PREDICTED verdict, derived at the same time as the
    data; a case the real checker disagrees with is QUARANTINED at exit 6 with a
    typed discrepancy and its sidecar keeps the prediction (C1) — the derivation
    is authoritative, the checker observational.
    """
    import hashlib as _hashlib
    from random import Random

    from gnd.checker import band as _cb
    from gnd.synth import assemble as _assemble
    from gnd.synth import boundary as _boundary
    from gnd.synth import frontier as _frontier
    from gnd.synth import paths as _paths
    from gnd.synth import provenance as _prov

    cases, downs = _boundary.enumerate_boundary(model, baseline.doc, Random(baseline_seed_value))
    # The two case kinds D-10's three labels do not name. `no-subjects` is the
    # (no-subjects, pass) row F-02 and F-05 both lived in; `unchecked` pins the
    # band-4 frontier the undecided rate is measured over. Both carry
    # `label: boundary`, so no schema copy moves (D-15).
    frontier_cases, frontier_downs = _frontier.enumerate_frontier(
        model, baseline.doc, Random(baseline_seed_value)
    )
    cases = cases + frontier_cases
    downs = downs + frontier_downs
    for down in downs:
        record = down.as_record()
        not_derivable.append(record)
    bound_not_derivable = [down.as_record() for down in downs]

    for case in cases:
        # A stable per-case seed derived from (baseline_seed, ref, case name), so
        # a case regenerates without replaying the whole enumeration.
        digest = _hashlib.sha256(
            f"{baseline_seed_value}:{case.constraint_ref}:{case.name}".encode()
        ).digest()
        case_seed = int.from_bytes(digest[:8], "big")
        label = _prov.CASE_KIND_TO_LABEL[case.case_kind]
        pop_rel = (
            f"{label}/{_paths.slug(case.constraint_ref)}.{_paths.slug(case.name)}"
            f"{filename_suffix}.json"
        )
        try:
            pop_abs = _paths.safe_output_path(out_root, pop_rel)
        except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
            return fail(EXIT_IO, f"refused output path for {case.constraint_ref}: {error}")

        try:
            admitted = _boundary.emit_boundary(model, case, pop_abs)
        except _boundary.BoundaryPredictionMismatch as mismatch:
            # C1: RETAIN under quarantine at exit 6 with the PREDICTION intact.
            try:
                q_rel = (
                    f"quarantine/{_paths.slug(case.constraint_ref)}."
                    f"{_paths.slug(case.name)}{filename_suffix}.json"
                )
                q_abs = _paths.safe_output_path(out_root, q_rel)
                q_abs.parent.mkdir(parents=True, exist_ok=True)
                q_abs.write_text(
                    json.dumps(mismatch.doc, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
                q_sidecar = build_sidecar(
                    q_abs.name,
                    label,
                    case_seed,
                    baseline.pool_size,
                    {**baseline_expectations, **mismatch.predicted},
                    case_kind=case.case_kind,
                    operator=case.name,
                    target=case.constraint_ref,
                    predicted_verdict=(
                        mismatch.predicted[case.constraint_ref].expected_verdict
                        if case.constraint_ref in mismatch.predicted
                        else None
                    ),
                    boundary_side=case.side,
                    epsilon=case.epsilon,
                    not_derivable=bound_not_derivable or None,
                    baseline_seed=baseline_seed_value,
                )
                _prov.write_sidecar(q_sidecar, q_abs)
                (q_abs.with_suffix(".discrepancy.json")).write_text(
                    json.dumps(mismatch.discrepancies, indent=2) + "\n", encoding="utf-8"
                )
                pop_abs.unlink(missing_ok=True)
            except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
                return fail(EXIT_IO, f"could not write quarantine: {error}")
            try:
                quarantine_path = abort_quarantine(q_abs)
            except OSError as error:
                return fail(EXIT_IO, f"could not publish quarantine: {error}")
            if output_format == "json":
                report_module.emit(
                    {
                        "command": "synth",
                        "exit_code": EXIT_QUARANTINE,
                        "quarantine": str(quarantine_path),
                        "discrepancies": mismatch.discrepancies,
                    }
                )
            else:
                print(
                    f"QUARANTINED (boundary prediction/observation mismatch, C1): {quarantine_path}"
                )
                print(f"  {mismatch}")
            return EXIT_QUARANTINE
        except _assemble.GeneratorError as error:
            return fail(
                EXIT_GENERATOR,
                f"generator invariant failed for boundary case {case.name} on "
                f"{case.constraint_ref}: {error}",
            )

        try:
            sidecar = build_sidecar(
                pop_abs.name,
                label,
                case_seed,
                baseline.pool_size,
                {**baseline_expectations, **admitted.predicted},
                case_kind=case.case_kind,
                operator=case.name,
                target=case.constraint_ref,
                predicted_verdict=admitted.predicted_verdict,
                boundary_side=case.side,
                epsilon=case.epsilon,
                not_derivable=bound_not_derivable or None,
                baseline_seed=baseline_seed_value,
            )
            sidecar_abs = _prov.write_sidecar(sidecar, pop_abs)
        except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
            return fail(EXIT_IO, f"could not write sidecar for {pop_abs}: {error}")
        written.append(
            {
                "population": str(pop_abs),
                "sidecar": str(sidecar_abs),
                "seed": case_seed,
                "band": _cb(admitted.report),
                "class": label,
                "case_kind": case.case_kind,
                "operator": case.name,
                "boundary_side": case.side,
                "epsilon": case.epsilon,
                "target": case.constraint_ref,
                "predicted_verdict": admitted.predicted_verdict,
                "baseline_seed": baseline_seed_value,
            }
        )
    return None


class _SynthCorpusTransaction:
    """Build a corpus off-tree and publish it only as one directory swap."""

    def __init__(self, final_root: Path) -> None:
        import shutil
        import tempfile

        self.final_root = final_root
        self.final_root.parent.mkdir(parents=True, exist_ok=True)
        self.stage_root = Path(
            tempfile.mkdtemp(prefix=f".{final_root.name}.synth-", dir=final_root.parent)
        )
        self._active = True
        try:
            if final_root.exists():
                if not final_root.is_dir():
                    raise OSError(f"corpus root {final_root} is not a directory")
                shutil.copytree(final_root, self.stage_root, dirs_exist_ok=True)
        except Exception:
            shutil.rmtree(self.stage_root, ignore_errors=True)
            self._active = False
            raise

    def abort(self, *, publish_quarantine: bool = False) -> None:
        import shutil

        if not self._active:
            return
        try:
            if publish_quarantine:
                staged_quarantine = self.stage_root / "quarantine"
                if staged_quarantine.exists():
                    final_quarantine = self.final_root / "quarantine"
                    final_quarantine.mkdir(parents=True, exist_ok=True)
                    for source in staged_quarantine.rglob("*"):
                        if not source.is_file():
                            continue
                        relative = source.relative_to(staged_quarantine)
                        destination = final_quarantine / relative
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        if (
                            not destination.exists()
                            or destination.read_bytes() != source.read_bytes()
                        ):
                            shutil.copy2(source, destination)
        finally:
            shutil.rmtree(self.stage_root, ignore_errors=True)
            self._active = False

    def commit(self) -> None:
        import os
        import shutil

        if not self._active:
            raise OSError("synthesis transaction is no longer active")
        backup = self.stage_root.with_name(self.stage_root.name + ".backup")
        moved_existing = False
        try:
            if self.final_root.exists():
                os.replace(self.final_root, backup)
                moved_existing = True
            os.replace(self.stage_root, self.final_root)
            self._active = False
        except Exception:
            if moved_existing and backup.exists() and not self.final_root.exists():
                os.replace(backup, self.final_root)
            raise
        finally:
            if not self._active and backup.exists():
                shutil.rmtree(backup, ignore_errors=True)


def _validate_existing_synth_index(out_root: Path) -> None:
    """Fail closed on the old manifest before the transaction writes anything."""
    index_path = out_root / "index.json"
    if not index_path.exists():
        return
    try:
        document = _validate_index_document(json.loads(index_path.read_text(encoding="utf-8")))
        _resolve_unique_index_entries(out_root, document)
    except json.JSONDecodeError as error:
        raise IndexValidationError(f"index.json is not valid JSON: {error}") from error
    except CorpusPathError as error:
        raise IndexValidationError(str(error)) from error


def _bind_synth_not_derivable(
    out_root: Path, not_derivable: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Bind the complete stand-down manifest into every current v4 sidecar."""
    from gnd.synth import provenance as _prov

    records: dict[tuple[str, str], dict[str, Any]] = {}
    index_path = out_root / "index.json"
    if index_path.exists():
        document = _validate_index_document(json.loads(index_path.read_text(encoding="utf-8")))
        for record in document["not_derivable"]:
            records[(str(record.get("constraint_ref")), str(record.get("operator")))] = record
    for record in not_derivable:
        records[(str(record.get("constraint_ref")), str(record.get("operator")))] = record
    manifest = [records[key] for key in sorted(records)]

    for sidecar_path in out_root.rglob("*.meta.json"):
        if "quarantine" in sidecar_path.relative_to(out_root).parts:
            continue
        sidecar = _prov.read_sidecar(sidecar_path)
        if sidecar.schema_version not in {"gnd-sidecar/4", "gnd-sidecar/5"}:
            continue
        population_path = sidecar_path.parent / sidecar.population
        updated = sidecar.model_copy(update={"not_derivable": manifest or None})
        _prov.write_sidecar(updated, population_path)
    return manifest


def _cmd_synth(
    model_path: str,
    out: str,
    class_: str,
    pool_path: str | None,
    seed: int | None,
    seeds: int,
    output_format: str,
    baseline_seed: int | None = None,
) -> int:
    """Generate labelled synthetic populations for a model (DATA-01).

    The development lane is probabilistic by DEFAULT (owner correction): ``--seed``
    omitted draws OS entropy per population and RECORDS it in the sidecar, so the
    data is fresh yet regenerable; ``--seed N`` is the deterministic
    variant-regeneration path (D-07′). ``--pool`` consumes an admitted pool; an
    omitted ``--pool`` builds a Faker pool and MATERIALISES it beside the corpus,
    so every run's ``pool_sha256`` is a real hashed file (D-19). ``index.json``
    MERGES across ``--class`` invocations (Gemini), never overwrites.

    ``--class violating`` (plan 05) mutates a conforming baseline — named by
    ``--baseline-seed`` so every case is traceable to what it mutated — one
    population per (constraint, applicable operator) pair, each admitted ONLY
    after the real checker confirms the model-derived typed prediction. A
    prediction/observation mismatch QUARANTINES the case (retained, typed
    discrepancy, exit 6, C1) — it is never discarded and its sidecar is never
    relabelled to match observation, because the disagreement may be a checker
    defect and a discarded case is how that defect vanishes from its own
    evaluation corpus.
    """
    import hashlib as _hashlib
    import os
    import tempfile
    from random import Random

    from gnd.checker import band as _cb
    from gnd.synth import assemble as _assemble
    from gnd.synth import mutate as _mutate
    from gnd.synth import paths as _paths
    from gnd.synth import poolfile as _poolfile
    from gnd.synth import provenance as _prov

    transaction: _SynthCorpusTransaction | None = None

    def fail(code: int, message: str) -> int:
        if transaction is not None:
            transaction.abort()
        if output_format == "json":
            report_module.emit({"command": "synth", "exit_code": code, "error": message})
        else:
            print(f"ERROR: {message}")
        return code

    try:
        model = load_model(model_path)
        from gnd.terms import require_non_temporal

        require_non_temporal(model, "synth")
        if model.reference_populations:
            raise ModelValidationError(
                [
                    ValidationIssue(
                        path="$",
                        message="synth does not support reference populations",
                        rule_id="reference:consumer-unsupported",
                    )
                ]
            )
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        return fail(3, f"{model_path}: {error}")

    structured = structured_derivation_ids(model)
    if structured:
        from gnd.checker import _model_uses_exact_derivations

        if any(
            isinstance(rule := fact_type.get("derivation_rule"), dict)
            and "clauses" in rule
            for fact_type in model.fact_types
        ) or not _model_uses_exact_derivations(model):
            return fail(
                EXIT_GENERATOR,
                "synth-derivation-unsupported: model declares structured "
                f"derivation rules ({', '.join(structured)}); generating a "
                "claimed derived extension is the forward-chaining constructor "
                "OQ-P2-2 names, and synth refuses rather than emitting facts it "
                "cannot warrant",
            )

    final_out_root = Path(out)
    try:
        _validate_existing_synth_index(final_out_root)
        transaction = _SynthCorpusTransaction(final_out_root)
    except IndexValidationError as error:
        return fail(3, f"could not prepare {final_out_root / 'index.json'}: {error}")
    except OSError as error:
        return fail(EXIT_IO, f"could not stage corpus {final_out_root}: {error}")
    out_root = transaction.stage_root
    model_ref = Path(model_path).name
    model_stem = _paths.slug(Path(model_path).stem)
    primary_dir = {"violating": "violating", "boundary": "boundary"}.get(class_, "conforming")

    # Resolve the pool: an admitted --pool, or a freshly built Faker pool. Either
    # way it is MATERIALISED into the corpus so pool_sha256 is never empty.
    pool_seed = seed if seed is not None else int.from_bytes(os.urandom(8), "big")
    try:
        if pool_path is not None:
            pool = _poolfile.load_pool(pool_path, model)
        else:
            pool = _poolfile.build_faker_pool(model, Random(pool_seed), size_per_type=8)
    except _poolfile.PoolValidationError as error:
        return fail(EXIT_GENERATOR, f"pool rejected:\n{error}")
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        return fail(EXIT_GENERATOR, f"pool could not be prepared: {error}")

    try:
        pool_rel = f"{primary_dir}/pool.{pool.sha256[:16]}.pool.json"
        pool_abs = _paths.safe_output_path(out_root, pool_rel)
        pool_abs.parent.mkdir(parents=True, exist_ok=True)
        _poolfile.write_pool(pool, pool_abs)
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        return fail(EXIT_IO, f"could not materialise the pool: {error}")

    provenance = pool.provenance or {}
    derivation_rules = {
        str(fact_type.get("id")): fact_type.get("derivation_rule") for fact_type in model.fact_types
    }
    unmutated_derivations = [
        {
            "derivation_ref": f"derivation:{fact_type_id}",
            "reason": (
                f"aggregate:{derivation_rules[fact_type_id]['aggregate']['fn']}-mutation-unsupported"
                if isinstance(derivation_rules[fact_type_id], dict)
                and isinstance(derivation_rules[fact_type_id].get("aggregate"), dict)
                else "structured-derivation-mutation-unsupported"
            ),
        }
        for fact_type_id in structured
    ]

    def abort_quarantine(staged_path: Path) -> Path:
        if transaction is None:
            return staged_path
        relative = staged_path.relative_to(transaction.stage_root)
        published_path = transaction.final_root / relative
        transaction.abort(publish_quarantine=True)
        return published_path

    def typed_expectations(assembly: _assemble.Assembly) -> dict[str, _prov.ExpectedState]:
        return {
            ref: _prov.ExpectedState(
                ground_truth=state.ground_truth,
                expected_verdict=state.expected_verdict,
                reason=state.reason,
            )
            for ref, state in assembly.expectations.items()
        }

    def build_sidecar(
        pop_name: str,
        class_label: str,
        pop_seed: int,
        pool_size: int,
        expectations: dict[str, _prov.ExpectedState],
        **extra: Any,
    ) -> _prov.Sidecar:
        return _prov.Sidecar(
            population=pop_name,
            population_sha256="",  # write_sidecar computes it over the written file
            **{"class": class_label},
            seed=pop_seed,
            gnd_version=resolve_version(),
            model=model_ref,
            model_id=str(model.model_id) if model.model_id else None,
            model_digest=_prov.validated_model_sha256(model),
            pool_source=str(provenance.get("source", "unknown")),
            pool_path=pool_rel,
            pool_sha256=pool.sha256,
            proposer_model=provenance.get("proposer_model"),
            prompt_version=provenance.get("prompt_version"),
            pool_size=pool_size,
            expectations=expectations,
            unmutated_derivations=unmutated_derivations,
            **extra,
        )

    def write_witness_quarantine(disc: _assemble.CheckerWitnessDiscrepancy, pop_seed: int) -> int:
        # C1: RETAIN the case under quarantine, never discard or relabel.
        try:
            q_rel = f"quarantine/{model_stem}.conforming.seed{pop_seed}.json"
            q_abs = _paths.safe_output_path(out_root, q_rel)
            q_abs.parent.mkdir(parents=True, exist_ok=True)
            q_abs.write_text(
                json.dumps(disc.doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            (q_abs.with_suffix(".discrepancy.json")).write_text(
                json.dumps(disc.discrepancies, indent=2) + "\n", encoding="utf-8"
            )
        except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
            return fail(EXIT_IO, f"could not write quarantine: {error}")
        try:
            quarantine_path = abort_quarantine(q_abs)
        except OSError as error:
            return fail(EXIT_IO, f"could not publish quarantine: {error}")
        if output_format == "json":
            report_module.emit(
                {
                    "command": "synth",
                    "exit_code": EXIT_QUARANTINE,
                    "quarantine": str(quarantine_path),
                    "discrepancies": disc.discrepancies,
                }
            )
        else:
            # Both directions land here (CR-04); the kinds name which one, and a
            # candidate false PASS is the one a reader must not skim past.
            kinds = sorted({str(record.get("kind", "candidate")) for record in disc.discrepancies})
            print(f"QUARANTINED ({', '.join(kinds)}, C1): {quarantine_path}")
            for record in disc.discrepancies:
                print(
                    f"  {record['constraint_ref']}: witness={record['witness']} "
                    f"observed={record['observed']}"
                )
        return EXIT_QUARANTINE

    written: list[dict[str, Any]] = []
    not_derivable: list[dict[str, Any]] = []

    if class_ in ("conforming", "all"):
        seed_values = (
            [seed + i for i in range(seeds)]
            if seed is not None
            else [int.from_bytes(os.urandom(8), "big") for _ in range(seeds)]
        )
        for pop_seed in seed_values:
            try:
                assembly = _assemble.assemble_conforming(
                    model, pop_seed, pool=pool, model_ref=model_ref
                )
            except _assemble.CheckerWitnessDiscrepancy as disc:
                return write_witness_quarantine(disc, pop_seed)
            except _assemble.GeneratorError as error:
                return fail(
                    EXIT_GENERATOR, f"generator invariant failed at seed {pop_seed}: {error}"
                )

            try:
                pop_rel = f"conforming/{model_stem}.conforming.seed{pop_seed}.json"
                pop_abs = _paths.safe_output_path(out_root, pop_rel)
                pop_abs.parent.mkdir(parents=True, exist_ok=True)
                pop_abs.write_text(
                    json.dumps(assembly.doc, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
            except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
                return fail(EXIT_IO, f"could not write population: {error}")

            # Re-admit the EMITTED file (exit 5 on rejection) — a structurally
            # invalid population contributes zero verdicts and must be loud.
            try:
                population = load_population(str(pop_abs), model=model)
            except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
                return fail(EXIT_GENERATOR, f"emitted population failed re-admission: {error}")
            report = check(model, population)

            try:
                sidecar = build_sidecar(
                    pop_abs.name,
                    "conforming",
                    pop_seed,
                    assembly.pool_size,
                    typed_expectations(assembly),
                    case_kind="conforming",
                )
                sidecar_abs = _prov.write_sidecar(sidecar, pop_abs)
            except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
                return fail(EXIT_IO, f"could not write sidecar for {pop_abs}: {error}")
            written.append(
                {
                    "population": str(pop_abs),
                    "sidecar": str(sidecar_abs),
                    "seed": pop_seed,
                    "band": _cb(report),
                    "class": "conforming",
                    "case_kind": "conforming",
                }
            )

    class _BaselineFailure(Exception):
        def __init__(self, code: int) -> None:
            self.code = code

    baseline_cache: dict[int, tuple[int, Any, Any, dict[str, _prov.ExpectedState]]] = {}

    def resolve_baseline(b_seed: int) -> tuple[int, Any, Any, dict[str, _prov.ExpectedState]]:
        """The conforming baseline the boundary and violating classes build on.

        Cached by seed so ``--class all`` assembles each variant ONCE: two classes
        derived from different baselines would not be comparable, and the
        sidecar's ``baseline_seed`` would name different populations for cases
        the report shows side by side.
        """
        if b_seed in baseline_cache:
            return baseline_cache[b_seed]
        try:
            baseline = _assemble.assemble_conforming(model, b_seed, pool=pool, model_ref=model_ref)
        except _assemble.CheckerWitnessDiscrepancy as disc:
            raise _BaselineFailure(write_witness_quarantine(disc, b_seed)) from None
        except _assemble.GeneratorError as error:
            raise _BaselineFailure(
                fail(EXIT_GENERATOR, f"baseline assembly failed at seed {b_seed}: {error}")
            ) from None
        try:
            with tempfile.NamedTemporaryFile(
                "w", suffix=".json", delete=False, encoding="utf-8"
            ) as handle:
                json.dump(baseline.doc, handle)
                temp_path = handle.name
            try:
                baseline_report = check(model, load_population(temp_path, model=model))
            finally:
                Path(temp_path).unlink(missing_ok=True)
        except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
            raise _BaselineFailure(
                fail(EXIT_GENERATOR, f"baseline failed re-admission: {error}")
            ) from None
        baseline_cache[b_seed] = (b_seed, baseline, baseline_report, typed_expectations(baseline))
        return baseline_cache[b_seed]

    def emit_violating_corpus(
        b_seed: int,
        baseline: Any,
        baseline_report: Any,
        baseline_expectations: dict[str, _prov.ExpectedState],
        filename_suffix: str,
    ) -> int | None:
        cases, stand_downs = _mutate.enumerate_violating(model, baseline.doc)
        not_derivable.extend(stand_downs)
        for ref, mutation in cases:
            # A stable per-case seed derived from (baseline_seed, ref, operator),
            # so a case regenerates without replaying the whole enumeration.
            digest = _hashlib.sha256(f"{b_seed}:{ref}:{mutation.name}".encode()).digest()
            case_seed = int.from_bytes(digest[:8], "big")
            pop_rel = (
                f"violating/{_paths.slug(ref)}.{_paths.slug(mutation.name)}{filename_suffix}.json"
            )
            try:
                pop_abs = _paths.safe_output_path(out_root, pop_rel)
            except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
                return fail(EXIT_IO, f"refused output path for {ref}: {error}")
            try:
                case = _mutate.emit_violating(
                    model,
                    baseline.doc,
                    baseline_report,
                    mutation,
                    ref,
                    pop_abs,
                    Random(case_seed),
                )
            except _mutate.PredictionMismatch as mismatch:
                # QUARANTINE, never discard (C1): the prediction is authoritative
                # ground truth; the checker's disagreement is an observation and a
                # candidate checker defect, adjudicated later. The sidecar keeps
                # the PREDICTION — relabelling it to match observation is the
                # oracle circularity that lets a present-day checker defect
                # vanish from its own evaluation corpus. Exit 5 stays reserved
                # for structural GeneratorError; a disagreement is exit 6.
                try:
                    q_rel = (
                        f"quarantine/{_paths.slug(ref)}.{_paths.slug(mutation.name)}"
                        f"{filename_suffix}.json"
                    )
                    q_abs = _paths.safe_output_path(out_root, q_rel)
                    q_abs.parent.mkdir(parents=True, exist_ok=True)
                    q_abs.write_text(
                        json.dumps(mismatch.doc, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8",
                    )
                    q_sidecar = build_sidecar(
                        q_abs.name,
                        "violating",
                        case_seed,
                        baseline.pool_size,
                        {**baseline_expectations, **mismatch.predicted},
                        violates=sorted(mismatch.predicted),
                        operator=mutation.name,
                        violates_target=ref,
                        isolating=len(mismatch.predicted) == 1,
                        isolation_verified=False,  # the checker did NOT confirm it
                        baseline_seed=b_seed,
                        not_derivable=stand_downs or None,
                    )
                    _prov.write_sidecar(q_sidecar, q_abs)
                    (q_abs.with_suffix(".discrepancy.json")).write_text(
                        json.dumps(mismatch.discrepancies, indent=2) + "\n", encoding="utf-8"
                    )
                    pop_abs.unlink(missing_ok=True)  # retained under quarantine/, not corpus
                except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
                    return fail(EXIT_IO, f"could not write quarantine: {error}")
                try:
                    quarantine_path = abort_quarantine(q_abs)
                except OSError as error:
                    return fail(EXIT_IO, f"could not publish quarantine: {error}")
                if output_format == "json":
                    report_module.emit(
                        {
                            "command": "synth",
                            "exit_code": EXIT_QUARANTINE,
                            "quarantine": str(quarantine_path),
                            "discrepancies": mismatch.discrepancies,
                        }
                    )
                else:
                    print(f"QUARANTINED (prediction/observation mismatch, C1): {quarantine_path}")
                    print(f"  {mismatch}")
                return EXIT_QUARANTINE
            except _assemble.GeneratorError as error:
                return fail(
                    EXIT_GENERATOR,
                    f"generator invariant failed for {mutation.name} on {ref}: {error}",
                )

            try:
                sidecar = build_sidecar(
                    pop_abs.name,
                    "violating",
                    case_seed,
                    baseline.pool_size,
                    {**baseline_expectations, **case.predicted},
                    violates=sorted(case.predicted),
                    operator=mutation.name,
                    violates_target=ref,
                    isolating=case.isolating,
                    isolation_verified=True,
                    baseline_seed=b_seed,
                    case_kind="violating",
                    target=ref,
                    not_derivable=stand_downs or None,
                )
                sidecar_abs = _prov.write_sidecar(sidecar, pop_abs)
            except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
                return fail(EXIT_IO, f"could not write sidecar for {pop_abs}: {error}")
            written.append(
                {
                    "population": str(pop_abs),
                    "sidecar": str(sidecar_abs),
                    "seed": case_seed,
                    "band": _cb(case.report),
                    "class": "violating",
                    "case_kind": "violating",
                    "operator": mutation.name,
                    "target": ref,
                    "violates_target": ref,
                    "violates": sorted(case.predicted),
                    "isolating": case.isolating,
                    "isolation_verified": True,
                    "baseline_seed": b_seed,
                }
            )
        return None

    if class_ in ("boundary", "violating", "all"):
        baseline_start = baseline_seed if baseline_seed is not None else seed
        baseline_seeds = (
            [baseline_start + i for i in range(seeds)]
            if baseline_start is not None
            else [int.from_bytes(os.urandom(8), "big") for _ in range(seeds)]
        )
        for b_seed_value in baseline_seeds:
            try:
                b_seed, baseline, baseline_report, baseline_expectations = resolve_baseline(
                    b_seed_value
                )
            except _BaselineFailure as failure:
                return failure.code

            # A multi-seed run emits the same operator names for each baseline;
            # include the baseline seed so later variants cannot overwrite the
            # first one.  Preserve the historical single-seed names.
            filename_suffix = f".baseline{b_seed}" if seeds > 1 else ""
            if class_ in ("boundary", "all"):
                outcome = _emit_boundary_corpus(
                    model=model,
                    baseline=baseline,
                    baseline_seed_value=b_seed,
                    baseline_expectations=baseline_expectations,
                    out_root=out_root,
                    build_sidecar=build_sidecar,
                    written=written,
                    not_derivable=not_derivable,
                    output_format=output_format,
                    fail=fail,
                    abort_quarantine=abort_quarantine,
                    filename_suffix=filename_suffix,
                )
                if outcome is not None:
                    return outcome

            if class_ in ("violating", "all"):
                outcome = emit_violating_corpus(
                    b_seed,
                    baseline,
                    baseline_report,
                    baseline_expectations,
                    filename_suffix,
                )
                if outcome is not None:
                    return outcome

    try:
        not_derivable = _bind_synth_not_derivable(out_root, not_derivable)
        _merge_index(out_root, written, not_derivable)
    except (_prov.SidecarError, json.JSONDecodeError) as error:
        return fail(EXIT_IO, f"could not bind generator manifest: {error}")
    except IndexValidationError as error:
        return fail(3, f"could not merge {out_root / 'index.json'}: {error}")
    except OSError as error:
        return fail(EXIT_IO, f"could not write {out_root / 'index.json'}: {error}")

    stage_root = out_root
    try:
        transaction.commit()
    except OSError as error:
        return fail(EXIT_IO, f"could not publish corpus {final_out_root}: {error}")
    for entry in written:
        for field in ("population", "sidecar"):
            entry[field] = str(final_out_root / Path(entry[field]).relative_to(stage_root))
    out_root = final_out_root

    violating_entries = [entry for entry in written if entry["class"] == "violating"]
    isolating_count = sum(1 for entry in violating_entries if entry.get("isolating"))
    isolating_fraction = isolating_count / len(violating_entries) if violating_entries else None

    if output_format == "json":
        report_module.emit(
            {
                "command": "synth",
                "exit_code": 0,
                "out": str(out_root),
                "class": class_,
                "pool": pool_rel,
                "pool_sha256": pool.sha256,
                "populations": written,
                "not_derivable": not_derivable,
                "isolating_cases": isolating_count,
                "set_attributed_cases": len(violating_entries) - isolating_count,
                "isolating_fraction": isolating_fraction,
            }
        )
    else:
        print(f"OK: wrote {len(written)} {class_} population(s) under {out_root}")
        for entry in written:
            label = entry.get("operator") or "conforming"
            print(f"  seed {entry['seed']}: {entry['population']} (band {entry['band']}, {label})")
        if violating_entries:
            print(
                f"  isolating: {isolating_count}/{len(violating_entries)} "
                f"({isolating_fraction:.3f}) — set-attributed: "
                f"{len(violating_entries) - isolating_count}"
            )
        for record in not_derivable:
            print(
                f"  not-derivable: {record['constraint_ref']} "
                f"[{record['operator'] or record['family']}]: {record['mechanism']}"
            )
        print(f"  pool: {pool_rel} ({pool.sha256[:16]})")
    return 0


class CorpusPathError(Exception):
    """An ``index.json`` entry does not resolve to a file inside the corpus root.

    ``--populations DIR`` is a promise that DIR is what gets measured, so a
    stored path that is absolute, escapes the root, or names a file that is not
    there is a REFUSAL rather than a fallback. The resolver this replaces tried
    ``Path(stored)`` first — against the process working directory — and took the
    first candidate that existed: since every committed index stored repo-root-
    relative paths, a run from the repo root read the repo-root copies whatever
    ``--populations`` said. An emptied corpus directory reproduced the committed
    payload byte-for-byte, digest and all, and a corrupted population inside the
    named directory was never opened. Mapped to exit 3 (ill-formed input), the
    same band as the other C6 binding failures.
    """


def _resolve_corpus_path(populations_dir: Path, stored: str) -> Path:
    """Resolve an ``index.json`` / sidecar path STRICTLY under the corpus root.

    Three rules, in order, and none of them may be relaxed into a fallback:

    1. ``index.json`` is UNTRUSTED input — an absolute path or one containing
       ``..`` is refused outright, before it can reach the filesystem;
    2. the path is joined under ``populations_dir`` through
       :func:`gnd.synth.paths.safe_output_path`, the same containment guard the
       write side uses, so a symlinked escape is refused too;
    3. the resolved file must EXIST. A population named in the index and absent
       under the root means the corpus is incomplete, and an incomplete corpus
       publishes a rate over a denominator its reader cannot see. Skipping the
       entry and falling back to a copy elsewhere on disk are the same defect
       wearing different clothes.
    """
    from gnd.synth import paths as _paths

    rel = Path(stored)
    if rel.is_absolute() or ".." in rel.parts:
        raise CorpusPathError(
            f"index.json entry {stored!r} is absolute or escapes its directory — "
            f"refused. A measurement reads the corpus it was pointed at "
            f"({populations_dir}), and index.json is untrusted input (C6)."
        )
    try:
        resolved = _paths.safe_output_path(populations_dir, rel.as_posix())
    except Exception as error:
        # The traversal guard's own refusal type is an implementation detail of
        # gnd.install; re-raised as the corpus-level error the CLI maps to 3.
        raise CorpusPathError(
            f"index.json entry {stored!r} resolves outside {populations_dir}: {error}"
        ) from error
    if not resolved.exists():
        raise CorpusPathError(
            f"index.json entry {stored!r} does not resolve to an existing file "
            f"under {populations_dir} — the corpus is incomplete, and a "
            f"measurement must read the corpus it was pointed at (C6). Falling "
            f"back to a copy elsewhere on disk is how an EMPTY directory once "
            f"reproduced the committed payload byte-for-byte."
        )
    return resolved


def _resolve_unique_index_entries(
    populations_dir: Path, index: dict[str, Any]
) -> list[tuple[dict[str, Any], Path, Path]]:
    """Resolve index paths once and reject aliases before any case is loaded.

    Reporting preserves the manifest's order, but denominators must describe
    physical artifacts rather than records.  Two spellings or symlinks that
    resolve to the same population/sidecar are therefore duplicates, and the
    error names both record positions so the corpus can be repaired directly.
    """
    resolved_entries: list[tuple[dict[str, Any], Path, Path]] = []
    seen: dict[str, dict[Path, int]] = {"population": {}, "sidecar": {}}
    for position, entry in enumerate(index["populations"]):
        resolved: dict[str, Path] = {}
        for field in ("population", "sidecar"):
            path = _resolve_corpus_path(populations_dir, entry[field])
            if path in seen[field]:
                first = seen[field][path]
                raise CorpusPathError(
                    f"index.json populations[{position}].{field} duplicates "
                    f"populations[{first}].{field} after normalization: "
                    f"{entry[field]!r} resolves to {path}"
                )
            seen[field][path] = position
            resolved[field] = path
        expected_sidecar = resolved["population"].with_suffix(".meta.json")
        if resolved["sidecar"] != expected_sidecar:
            raise CorpusPathError(
                f"index.json populations[{position}].sidecar resolves to "
                f"{resolved['sidecar']}, but population {resolved['population']} "
                f"is bound to {expected_sidecar}"
            )
        resolved_entries.append((entry, resolved["population"], resolved["sidecar"]))
    return resolved_entries


def _cmd_measure(
    model_path: str,
    populations: str,
    output_format: str,
    out: str | None,
    promote: str | None = None,
    *,
    unredacted: bool = False,
) -> int:
    """Measure the checker's per-constraint rates over labelled populations (VER-03).

    Computed OFFLINE from committed artifacts (owner's two-lane rule): this arm
    imports no provider or network module, and the payload carries no timestamp
    so two runs over one corpus reproduce byte-for-byte. Exit codes: 3 on a C6
    sidecar-binding mismatch (recomputed population/model/pool digest disagrees
    with the sidecar) or a missing/ill-formed expectation, 5 on a population that
    fails re-admission, 6 when checker_defects[] is non-empty (C9), 64 on a mixed
    (model, pool_source) corpus (C4).
    """
    from gnd import redaction as _redaction
    from gnd.measure import report as measure_report
    from gnd.measure.score import (
        CellLookupError,
        InconsistentExpectationError,
        PartitionError,
    )
    from gnd.measure.truth import ConstraintRefError, ExpectationMissingError
    from gnd.synth import poolfile as _poolfile
    from gnd.synth import provenance as _prov

    policy = None

    def fail(code: int, message: str) -> int:
        payload = {"command": "measure", "exit_code": code, "error": message}
        if policy is not None and policy.active:
            payload["error"] = message if unredacted else _redaction.INSTANCE_DETAIL
            payload = _redaction.project_output(
                "measure",
                payload,
                policy=policy,
                mode="unredacted" if unredacted else "applied",
                emitter_id=f"cli-measure-{output_format}",
            )
        if output_format == "json":
            report_module.emit(payload)
        else:
            if policy is not None and policy.active:
                print(_redaction.render_text_header(payload))
            print(f"ERROR: {payload['error']}")
        return code

    try:
        model = load_model(model_path)
        from gnd.terms import require_non_temporal

        require_non_temporal(model, "measure")
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        return fail(3, f"{model_path}: {error}")
    policy = _redaction.RedactionPolicy.from_model(model)

    populations_dir = Path(populations)
    index_path = populations_dir / "index.json"
    if not index_path.exists():
        return fail(3, f"no index.json under {populations_dir} — nothing to measure.")
    try:
        index = _validate_index_document(json.loads(index_path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as error:
        return fail(3, f"could not read {index_path}: {error}")
    except IndexValidationError as error:
        return fail(3, str(error))

    expected_model_digest = _prov.validated_model_sha256(model)
    expected_aggregate_disclosures = sorted(
        (
            f"derivation:{fact_type['id']}",
            f"aggregate:{fact_type['derivation_rule']['aggregate']['fn']}-mutation-unsupported",
        )
        for fact_type in model.fact_types
        if isinstance(fact_type.get("derivation_rule"), dict)
        and isinstance(fact_type["derivation_rule"].get("aggregate"), dict)
    )
    expected_aggregate_refs = {ref for ref, _reason in expected_aggregate_disclosures}
    pool_sha_cache: dict[str, str] = {}
    measured: list[measure_report.MeasuredPopulation] = []
    validated_entries: list[dict[str, Any]] = []
    loaded_sidecars: list[_prov.Sidecar] = []

    # F-05: every path the payload publishes is CORPUS-ROOT-RELATIVE, so the
    # payload is a function of the corpus and not of how the corpus was named on
    # the command line. Storing `str(pop_path)` inherited the form of
    # `--populations`: measuring with an absolute path baked machine paths into
    # `corpus[].path`, `corpus[].sidecar_path` and
    # `per_constraint[].evidence.population` — 157 differing values, all path
    # strings, no number among them — so the sha256 receipt in 02-MEASUREMENT.md
    # held for the documented relative invocation from the repo root and for no
    # other. This is the same class CR-01 closed on the write side of
    # `index.json`; the payload retained it.
    try:
        corpus_root = populations_dir.resolve()
    except OSError as error:
        return fail(3, f"could not resolve {populations_dir}: {error}")

    def _corpus_relative(path: Path) -> str:
        return path.resolve().relative_to(corpus_root).as_posix()

    try:
        resolved_entries = _resolve_unique_index_entries(populations_dir, index)
    except CorpusPathError as error:
        return fail(3, str(error))

    for index_entry, pop_path, sidecar_path in resolved_entries:
        # C6: verify the sidecar binding BEFORE scoring. read_sidecar recomputes
        # population_sha256 (a stale/edited population) and rejects a swapped
        # sidecar by name; a SidecarError is a binding failure -> exit 3.
        try:
            sidecar = _prov.read_sidecar(sidecar_path)
        except _prov.SidecarError as error:
            return fail(3, f"C6 sidecar binding failed for {pop_path}: {error}")
        except OSError as error:
            return fail(3, f"could not read sidecar {sidecar_path}: {error}")
        if expected_aggregate_disclosures:
            actual_aggregate_disclosures = sorted(
                (row.get("derivation_ref", ""), row.get("reason", ""))
                for row in sidecar.unmutated_derivations
                if row.get("derivation_ref") in expected_aggregate_refs
                or row.get("reason", "").startswith("aggregate:")
            )
            if (
                sidecar.schema_version != "gnd-sidecar/5"
                or actual_aggregate_disclosures != expected_aggregate_disclosures
            ):
                return fail(
                    3,
                    f"unmutated_derivations in {sidecar_path} do not disclose every "
                    "aggregate derivation declared by the model",
                )

        # C6 (continued): recompute model_digest and pool_sha256 — the two digests
        # read_sidecar cannot check without the model and pool objects.
        if sidecar.model_digest != expected_model_digest:
            return fail(
                3,
                f"C6 sidecar binding failed for {pop_path}: model_digest "
                f"{sidecar.model_digest!r} does not match this model "
                f"({expected_model_digest!r}) — a wrong-model sidecar.",
            )
        try:
            pool_abs = _resolve_corpus_path(populations_dir, sidecar.pool_path)
        except CorpusPathError as error:
            return fail(3, f"C6 pool binding failed for {pop_path}: {error}")
        try:
            if str(pool_abs) not in pool_sha_cache:
                pool_sha_cache[str(pool_abs)] = _poolfile.load_pool(pool_abs, model).sha256
            recomputed_pool_sha = pool_sha_cache[str(pool_abs)]
        except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
            return fail(3, f"C6 pool binding failed for {pop_path}: {error}")
        if recomputed_pool_sha != sidecar.pool_sha256:
            return fail(
                3,
                f"C6 sidecar binding failed for {pop_path}: pool_sha256 "
                f"{sidecar.pool_sha256!r} does not match {pool_abs} "
                f"({recomputed_pool_sha!r}).",
            )

        # A population that fails to load is never counted — exit 5. A skipped
        # population contributes zero verdicts, hence zero errors, hence a better
        # score (T-02-19).
        try:
            population = load_population(str(pop_path), model=model)
        except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
            return fail(EXIT_GENERATOR, f"population {pop_path} failed to load: {error}")
        report = check(model, population)
        observed_by_ref = {verdict.constraint_ref: verdict.verdict for verdict in report.verdicts}
        checker_disagrees_with_oracle = any(
            observed_by_ref.get(ref) != state.expected_verdict
            for ref, state in sidecar.expectations.items()
        )

        # Every index label is a redundant cache.  The sidecar is bound to the
        # population bytes and the checker owns the observed band, so a cache
        # mismatch is malformed corpus input rather than coverage evidence.
        authoritative: dict[str, Any] = {
            "seed": sidecar.seed,
            "band": checker_band(report),
            "class": sidecar.class_,
            "case_kind": sidecar.case_kind or sidecar.class_,
            "operator": sidecar.operator,
            "boundary_side": sidecar.boundary_side,
            "epsilon": sidecar.epsilon,
            "target": sidecar.target,
            "predicted_verdict": sidecar.predicted_verdict,
            "violates_target": sidecar.violates_target,
            "violates": sorted(sidecar.violates) if sidecar.violates is not None else None,
            "isolating": sidecar.isolating,
            "isolation_verified": sidecar.isolation_verified,
            "baseline_seed": sidecar.baseline_seed,
        }
        for field in ("seed", "band", "class", "case_kind"):
            if index_entry[field] != authoritative[field]:
                # The checker is the system UNDER measurement.  When its live
                # observations disagree with the bound oracle, a changed band is
                # defect evidence, not proof the historical index was forged.
                # On an oracle-consistent corpus the same mismatch remains a
                # hard metadata failure, which is what catches index tampering.
                if field == "band" and checker_disagrees_with_oracle:
                    authoritative["band"] = index_entry[field]
                    continue
                return fail(
                    3,
                    f"index.json metadata for {pop_path} disagrees with its "
                    f"sidecar/checker: {field}={index_entry[field]!r}, expected "
                    f"{authoritative[field]!r}",
                )
        for field, expected in authoritative.items():
            if field in ("seed", "band", "class", "case_kind") or field not in index_entry:
                continue
            actual = index_entry[field]
            if field == "epsilon" and actual is not None and expected is not None:
                actual, expected = str(actual), str(expected)
            if field == "violates" and actual is not None:
                actual = sorted(actual)
            # v1-v3 sidecars predate bound operator provenance. Preserve their
            # readability, but never feed that legacy index-only operator into
            # a v4 coverage summary.
            if (
                field == "operator"
                and expected is None
                and sidecar.schema_version not in {"gnd-sidecar/4", "gnd-sidecar/5"}
            ):
                continue
            if actual != expected:
                return fail(
                    3,
                    f"index.json metadata for {pop_path} disagrees with its "
                    f"sidecar: {field}={actual!r}, expected {expected!r}",
                )

        validated_entry = {
            "population": index_entry["population"],
            "sidecar": index_entry["sidecar"],
            **{field: value for field, value in authoritative.items() if value is not None},
        }
        if (
            sidecar.schema_version not in {"gnd-sidecar/4", "gnd-sidecar/5"}
            and sidecar.operator is None
            and index_entry.get("operator") is not None
        ):
            validated_entry["operator"] = index_entry["operator"]
        validated_entries.append(validated_entry)
        loaded_sidecars.append(sidecar)

        measured.append(
            measure_report.MeasuredPopulation(
                population_path=_corpus_relative(pop_path),
                population_sha256=sidecar.population_sha256,
                sidecar_path=_corpus_relative(sidecar_path),
                sidecar_sha256=_prov._sha256_file(sidecar_path),
                sidecar=sidecar,
                report=report,
            )
        )

    # WR-02: the measured set is whatever index.json lists, and index.json is
    # covered by no digest — so a PRUNED index quietly narrows every denominator
    # while the run still exits 0 (deleting the 51 violating entries from a
    # committed index still published `false_pass_rate 0.0`). Reconcile the index
    # against the TREE: a population/sidecar pair sitting on disk but absent from
    # the scored set is an unexplained file, which is exactly what `corpus[]` is
    # supposed to make visible. `quarantine/` is excluded deliberately — a
    # quarantined case is RETAINED outside the corpus by design (C1), not
    # measured.
    # Both sides of this comparison are corpus-root-relative POSIX strings
    # (F-05), so the reconciliation is over the same identity the payload
    # publishes rather than over resolved absolutes.
    # A fresh v4 corpus binds the complete generator stand-down manifest into
    # its sidecars.  Reconcile the top-level index cache against that union so a
    # fabricated record cannot inflate boundary_not_derivable.  All-legacy and
    # mixed corpora retain read compatibility; their index-only values are not
    # treated as v4 sidecar-derived coverage provenance.
    validated_not_derivable = list(index.get("not_derivable") or [])
    if loaded_sidecars and all(
        sidecar.schema_version in {"gnd-sidecar/4", "gnd-sidecar/5"} for sidecar in loaded_sidecars
    ):
        by_record: dict[tuple[str, str], dict[str, Any]] = {}
        for sidecar in loaded_sidecars:
            for record in sidecar.not_derivable or []:
                key = (
                    str(record.get("constraint_ref")),
                    str(record.get("operator")),
                )
                by_record[key] = record
        indexed = {
            (str(record.get("constraint_ref")), str(record.get("operator"))): record
            for record in validated_not_derivable
        }
        if indexed != by_record:
            return fail(
                3,
                "index.json not_derivable metadata disagrees with the v4 "
                "sidecar-bound generator manifest",
            )
        validated_not_derivable = [by_record[key] for key in sorted(by_record)]

    validated_index = {
        "populations": validated_entries,
        "not_derivable": validated_not_derivable,
    }

    try:
        scored_sidecars = {mp.sidecar_path for mp in measured}
        on_disk = {
            _corpus_relative(candidate)
            for candidate in populations_dir.rglob("*.meta.json")
            if "quarantine" not in Path(_corpus_relative(candidate)).parts
        }
    except (OSError, ValueError) as error:
        return fail(3, f"could not enumerate {populations_dir}: {error}")
    unlisted = sorted(on_disk - scored_sidecars)
    if unlisted:
        return fail(
            3,
            f"{unlisted} sit under {populations_dir} but are not in index.json — "
            f"the measured set is whatever the index lists and the index is bound "
            f"by no digest, so an unlisted population narrows every denominator "
            f"silently. Re-run `gnd synth` to merge them, or remove them.",
        )

    try:
        payload = measure_report.build_measurement_report(
            model,
            measure_report.stable_model_identifier(model_path),
            measured,
            gnd_version=resolve_version(),
            index=validated_index,
            index_sha256=_prov._sha256_file(index_path),
        )
    except measure_report.MixedCorpusError as error:
        return fail(EXIT_USAGE, str(error))
    except (ExpectationMissingError, ConstraintRefError, InconsistentExpectationError) as error:
        # A sidecar whose (ground_truth, expected_verdict) pair the cell table
        # calls an error is ill-formed INPUT, same band as the C6 binding
        # failures — not an internal fault (CR-03). Listed before CellLookupError
        # because it subclasses it.
        return fail(3, f"sidecar/model inconsistency: {error}")
    except (CellLookupError, PartitionError) as error:
        # A verdict/ground-truth state the table does not know, or a broken
        # partition, is an INTERNAL accounting fault. Exit 70 rather than an
        # uncaught traceback's exit 1, which would masquerade as band 1
        # ("alethic fail") to any harness keying on the bands.
        return fail(EXIT_INTERNAL, f"measurement accounting failed: {error}")

    semantic_payload = payload
    from gnd.redaction import RedactionPolicy, project_output

    policy = RedactionPolicy.from_model(model)
    if output_format == "json":
        payload = project_output(
            "measure",
            semantic_payload,
            policy=policy,
            mode="unredacted" if unredacted else "applied",
            emitter_id="cli-measure-json",
        )
    else:
        payload = project_output(
            "measure",
            semantic_payload,
            policy=policy,
            mode="unredacted" if unredacted else "applied",
            emitter_id="cli-measure-text",
        )

    rendered = measure_report._canonical(payload)
    if out is not None:
        try:
            Path(out).write_text(rendered + "\n", encoding="utf-8")
        except OSError as error:
            return fail(EXIT_IO, f"could not write {out}: {error}")

    if output_format == "json":
        if out is None:
            print(rendered)
    else:
        print(measure_report.render_measurement(payload))
        if out is not None:
            print(f"  (json written to {out})")

    if promote is not None:
        outcome = _promote_defects(
            model=model,
            model_path=model_path,
            payload=semantic_payload,
            measured=measured,
            corpus_dir=Path(promote),
            populations_root=corpus_root,
            output_format=output_format,
            fail=fail,
        )
        if outcome is not None:
            return outcome

    # C9: a non-empty checker_defects[] is exit 6, direction-agnostic.
    if semantic_payload["checker_defects"]:
        return EXIT_CHECKER_DEFECT
    return 0


def _promote_defects(
    *,
    model: Any,
    model_path: str,
    payload: dict[str, Any],
    measured: list[Any],
    corpus_dir: Path,
    populations_root: Path,
    output_format: str,
    fail: Any,
) -> int | None:
    """D-14: copy each defect-revealing input into the corpus and PRINT the rows.

    The append stays a REVIEWED act — the corpus's value is that every case
    earned its place — so nothing here edits ``manifest.yaml`` and nothing
    touches ``tests/test_adversarial_corpus.py``. The mechanical part is
    producing rows that are correct by construction.
    """
    from gnd.measure import promote as _promote
    from gnd.synth import GENERATOR_VERSION

    defects = payload["checker_defects"]
    if not defects:
        if output_format != "json":
            print(
                "  --promote: no checker defects to promote. An empty promotion is a "
                "FINDING, not an omission (D-14)."
            )
        return None
    sidecars = {mp.population_path: mp.sidecar for mp in measured}
    try:
        rows = _promote.manifest_rows(
            defects,
            model,
            model_path,
            sidecars,
            corpus_dir,
            generator_version=GENERATOR_VERSION,
            populations_root=populations_root,
        )
        rendered = _promote.render_manifest_rows(rows)
    except _promote.PromotionError as error:
        return fail(EXIT_GENERATOR, f"promotion failed: {error}")
    except OSError as error:
        return fail(EXIT_IO, f"could not write promoted inputs: {error}")

    if output_format == "json":
        report_module.emit(
            {
                "command": "measure",
                "exit_code": EXIT_CHECKER_DEFECT,
                "promoted": rows,
                "corpus_dir": str(corpus_dir),
                "manifest_yaml": rendered,
            }
        )
    else:
        print(
            f"  --promote: {len(rows)} row(s) written into {corpus_dir}. APPEND THEM BY "
            f"REVIEW — this command never edits manifest.yaml:"
        )
        print(rendered)
    return None


def _corpus_relative(out_root: Path, path: str) -> str:
    """``path`` expressed relative to the corpus root, in POSIX form (CR-01).

    Every path written by ``gnd synth`` came from
    :func:`gnd.synth.paths.safe_output_path` and is therefore inside
    ``out_root``; the ``ValueError`` branch exists so a future caller that breaks
    that invariant is visible in the index rather than silently absolutised.
    """
    candidate = Path(path)
    try:
        return candidate.resolve().relative_to(out_root.resolve()).as_posix()
    except ValueError:
        return candidate.as_posix()


def _merge_index(
    out_root: Path,
    written: list[dict[str, Any]],
    not_derivable: list[dict[str, Any]] | None = None,
) -> None:
    """MERGE new entries into ``index.json`` (Gemini), union by population path,
    emitted in stable sorted order so the file is byte-reproducible (which also
    makes plan 04's D-22 'first contributing population in corpus order'
    deterministic — Claude-LOW). ``not_derivable`` records merge by
    (constraint_ref, operator) — a stand-down is an ANSWER and must survive
    re-invocation, never a silent skip.

    Paths are stored RELATIVE TO ``out_root`` (CR-01), the same rule the sidecar
    already applies to ``population`` and ``pool_path``. Storing them as written
    (cwd-relative, or absolute when ``--out`` was) is what let ``gnd measure
    --populations DIR`` resolve them against the process working directory and
    read a corpus the operator never named — and it bakes a machine path into a
    committed artifact besides.
    """
    import os
    import tempfile

    index_path = out_root / "index.json"
    existing: dict[str, dict[str, Any]] = {}
    existing_downs: dict[tuple[str, str], dict[str, Any]] = {}
    if index_path.exists():
        try:
            document = _validate_index_document(json.loads(index_path.read_text(encoding="utf-8")))
            _resolve_unique_index_entries(out_root, document)
            for entry in document["populations"]:
                existing[entry["population"]] = entry
            for record in document["not_derivable"]:
                existing_downs[(record["constraint_ref"], str(record.get("operator")))] = record
        except json.JSONDecodeError as error:
            raise IndexValidationError(f"index.json is not valid JSON: {error}") from error
        except CorpusPathError as error:
            raise IndexValidationError(str(error)) from error
    for entry in written:
        relative = dict(entry)
        for key in ("population", "sidecar"):
            if relative.get(key):
                relative[key] = _corpus_relative(out_root, relative[key])
        existing[relative["population"]] = relative
    for record in not_derivable or []:
        existing_downs[(record["constraint_ref"], str(record.get("operator")))] = record
    merged = sorted(existing.values(), key=lambda e: e["population"])
    merged_downs = sorted(
        existing_downs.values(), key=lambda r: (r["constraint_ref"], str(r.get("operator")))
    )
    document = {"populations": merged, "not_derivable": merged_downs}
    _validate_index_document(document)
    rendered = json.dumps(document, indent=2, ensure_ascii=False, sort_keys=True) + "\n"

    out_root.mkdir(parents=True, exist_ok=True)
    staged_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            dir=out_root,
            prefix=".index.",
            suffix=".tmp",
            delete=False,
            encoding="utf-8",
        ) as handle:
            staged_path = Path(handle.name)
            handle.write(rendered)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(staged_path, index_path)
        staged_path = None
        directory_fd = os.open(out_root, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if staged_path is not None:
            staged_path.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = _BandSafeParser(
        prog="gnd",
        description="GND ORM runtime: validate conceptual models, check populations",
    )
    # argparse's version action raises SystemExit(0). That is INSIDE the
    # normative band contract and correct — reporting the version is a success.
    # Do not "fix" it into a return; the action fires during parse_args(), before
    # main() has anything to return.
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {resolve_version()}",
        help="print the installed version and exit",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    from gnd.witness.cli import add_parsers as add_witness_parsers

    add_witness_parsers(subparsers)

    import_parser = subparsers.add_parser(
        "import", help="import a supported foreign ORM dialect create-once"
    )
    import_subparsers = import_parser.add_subparsers(dest="import_command", required=True)
    rai_import_parser = import_subparsers.add_parser(
        "rai-orm",
        help="import the bounded rai-orm-from-schema dialect",
    )
    rai_import_parser.add_argument("model", help="path to the source RAI ORM YAML file")
    rai_import_parser.add_argument(
        "--out", required=True, help="new directory for model.orm.yaml and aliases.json"
    )
    rai_import_parser.add_argument(
        "--source-artifact",
        help="stable relative POSIX source path recorded in provenance",
    )
    rai_import_parser.add_argument(
        "--source-commit",
        help="source repository commit required when provenance must be synthesized",
    )

    validate_parser = subparsers.add_parser(
        "validate",
        help="validate a model and bind declared fixed reference populations",
        description="Validate the model; version-4 references bind beneath its parent with disjoint fixed ownership and exact raw hashes.",
    )
    validate_parser.add_argument("model", help="path to the model file")
    validate_parser.add_argument(
        "--trace",
        action="store_true",
        help=(
            "report what a transition run would evaluate, WITHOUT evaluating "
            "anything: the two digests every steps.json must carry, which "
            "preconditions compile to standing obligations and which are "
            "retained per-step and why, and the frame modality each fact type "
            "would be graded with. Reports; never decides, never reads a "
            "population. This is the only shipped producer of "
            "operations_digest, which every steps.json is required to carry"
        ),
    )
    _add_format_argument(validate_parser)
    _add_unredacted_argument(validate_parser)

    diff_parser = subparsers.add_parser("diff", help="compare two models over one vocabulary")
    diff_parser.add_argument("model_a")
    diff_parser.add_argument("model_b")
    diff_parser.add_argument("--populations", metavar="DIR")
    diff_parser.add_argument("--seed", type=int, default=0)
    _add_format_argument(diff_parser)
    _add_unredacted_argument(diff_parser)

    coverage_parser = subparsers.add_parser(
        "coverage",
        help="report claims and cited evidence for every addressable model element",
    )
    coverage_parser.add_argument("model", help="path to the model file")
    coverage_parser.add_argument("--experiments", action="append", default=[], metavar="DIR")
    coverage_parser.add_argument("--check", action="append", default=[], metavar="PATH")
    coverage_parser.add_argument("--verify", action="append", default=[], metavar="PATH")
    coverage_parser.add_argument("--conformance", action="append", default=[], metavar="PATH")
    coverage_parser.add_argument("--transition", action="append", default=[], metavar="PATH")
    _add_format_argument(coverage_parser)

    check_parser = subparsers.add_parser(
        "check",
        help="check a population against a model, or a walk between two populations",
        description=(
            "Two arms, and exactly one runs. SNAPSHOT: a positional population is "
            "checked against the model's constraints. TRANSITION: --pre, --steps "
            "and --post audit a WALK -- the operation invocations claimed to have "
            "carried the pre-population to the post-population -- reporting failed "
            "preconditions, undeclared side effects and illegal intermediate "
            "states. Mixing the two, or supplying part of the transition triple, "
            "is a usage error at 64: they answer different questions, and "
            "silently preferring one would make the other's arguments decorative. "
            "Model version 3 supports guarded Date plus/minus Duration calendar-day "
            "terms (date_add/date_sub), selecting report v11; --admission selects temporal report v13."
        ),
    )
    check_parser.add_argument(
        "model",
        help="path to the model file",
    )
    # nargs="?" so the transition arm can omit it. The parser therefore cannot
    # enforce "one arm or the other" itself -- that check lives in the dispatch,
    # routed back through parser.error so it exits 64 with no payload like every
    # other malformed invocation.
    check_parser.add_argument(
        "population",
        nargs="?",
        help="path to the population file (YAML or JSON) -- the snapshot arm",
    )
    check_parser.add_argument(
        "--populations",
        help="batch arm: directory of sorted .json/.yaml/.yml population projections",
    )
    check_parser.add_argument(
        "--pre",
        help="transition arm: the population the walk starts from",
    )
    check_parser.add_argument(
        "--steps",
        help="transition arm: the steps.json document describing the walk",
    )
    check_parser.add_argument(
        "--post",
        help="transition arm: the population the walk is claimed to end in",
    )
    check_parser.add_argument("--anchors", help="bound source anchor sidecar for snapshot checks")
    check_parser.add_argument("--document", help="source document for anchor spans")
    check_parser.add_argument(
        "--admission",
        action="store_true",
        help="include the occurrence admission partition in the check report",
    )
    _add_format_argument(check_parser)
    _add_unredacted_argument(check_parser)

    verbalize_parser = subparsers.add_parser(
        "verbalize",
        help="render supplied facts as deterministic sentences",
    )
    verbalize_targets = verbalize_parser.add_subparsers(dest="verbalize_target", required=True)
    verbalize_population_parser = verbalize_targets.add_parser(
        "population",
        help="render one population in text or JSONL",
    )
    verbalize_population_parser.add_argument("model")
    verbalize_population_parser.add_argument("population")
    verbalize_population_parser.add_argument("--anchors")
    verbalize_population_parser.add_argument("--document")
    verbalize_population_parser.add_argument("--format", choices=("text", "jsonl"), default="text")
    _add_unredacted_argument(verbalize_population_parser)

    verify_parser = subparsers.add_parser(
        "verify",
        help="run the full derived verifier over a pre-extracted population (VER-01, VER-02)",
        description=(
            "Run the full derived verifier: popvalidate then check over a "
            "PRE-EXTRACTED population file. This command never calls a model "
            "and never orchestrates extraction (R-03''): the executing agent "
            "running the gnd-extract skill writes the population and its "
            "<population>.extraction.json sidecar, and verify validates the "
            "handoff before composing the checker. Exit bands are REUSED "
            "unchanged with precedence 3 > 1 > 4 > 2 > 0: 3 ill-formed "
            "(including an ill-formed extraction handoff), 1 alethic fail, 4 "
            "indeterminate, 2 vacuous, 0 pass. The payload's extraction block "
            "carries the machine-readable state (ran | skipped | failed + "
            "reason); a missing sidecar is extraction:sidecar-missing, a "
            "malformed one extraction:sidecar-invalid, and a digest that does "
            "not match the file bytes extraction:binding-mismatch — all exit "
            "3, state failed. skipped is written ONLY by --no-extraction. "
            "Never a fidelity rate in this payload: a checker pass over an "
            "uncalibrated extraction is checker acceptance, not proof of "
            "faithfulness."
        ),
    )
    verify_parser.add_argument("model", help="path to the model file")
    verify_parser.add_argument(
        "population", help="path to the PRE-EXTRACTED population file (YAML or JSON)"
    )
    verify_parser.add_argument(
        "--sidecar",
        default=None,
        help=(
            "path to the extraction sidecar (default: the population path with "
            "an .extraction.json suffix, beside the population)"
        ),
    )
    verify_parser.add_argument(
        "--artifacts",
        default=None,
        help=(
            "directory containing the model's extraction bundle; required on "
            "the extraction path so projection_sha256 is verified"
        ),
    )
    verify_parser.add_argument(
        "--no-extraction",
        dest="no_extraction",
        action="store_true",
        help=(
            "the INTENTIONAL opt-out: check a population that was not produced "
            "by an extraction; records extraction.state=skipped with the reason"
        ),
    )
    verify_parser.add_argument(
        "--out",
        default=None,
        help="also write the JSON payload to this path (from argv only)",
    )
    _add_format_argument(verify_parser)
    _add_unredacted_argument(verify_parser)

    synth_parser = subparsers.add_parser(
        "synth",
        help="generate labelled synthetic populations from a model (DATA-01)",
        description=(
            "Generate labelled synthetic populations, each with a provenance "
            "SIDECAR. --class conforming builds populations the checker accepts; "
            "--class violating mutates a conforming baseline, one population per "
            "(constraint, operator) pair, each admitted only after the real checker "
            "confirms the model-derived typed prediction (D-05'); --class all does "
            "both. The development lane is probabilistic by default: --seed omitted "
            "draws OS entropy per population and records it, so data is fresh yet "
            "regenerable; --seed N is the deterministic variant-regeneration path. "
            "--pool consumes an admitted pool artifact; an omitted --pool builds "
            "and materialises a Faker pool beside the corpus. Exits 5 on a "
            "generator invariant failure, 6 on a quarantined checker/witness or "
            "prediction/observation disagreement (C1)."
        ),
    )
    synth_parser.add_argument("model", help="path to the model file")
    synth_parser.add_argument(
        "--out", default=".gnd/synth", help="output root for populations (default: .gnd/synth)"
    )
    synth_parser.add_argument(
        "--class",
        dest="synth_class",
        choices=("conforming", "boundary", "violating", "all"),
        default="conforming",
        help=(
            "the population class to generate: conforming, boundary, violating, or "
            "all. `boundary` derives cases from the constraints' own declared bounds "
            "(D-06) and includes the `no-subjects` and `unchecked` frontier kinds"
        ),
    )
    synth_parser.add_argument(
        "--pool",
        default=None,
        help="path to an admitted pool artifact (default: build a Faker pool)",
    )
    synth_parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="RNG seed (omitted: draw OS entropy, the probabilistic development default)",
    )
    synth_parser.add_argument(
        "--baseline-seed",
        type=int,
        default=None,
        help=(
            "seed of the conforming baseline a violating run mutates (recorded in "
            "every violating sidecar so each case is traceable to what it mutated; "
            "default: --seed, else OS entropy)"
        ),
    )
    synth_parser.add_argument(
        "--seeds",
        type=_positive_int,
        default=1,
        help=(
            "number of independent seed variants to generate for every requested "
            "class (default 1, the lightweight dev lane). --seeds 30 is the "
            "publication/degeneracy invocation: 30 clean seeds give 95%% confidence "
            "(rule of three) that fewer than 10%% of the GENERATOR's runs are "
            "degenerate"
        ),
    )
    _add_format_argument(synth_parser)

    measure_parser = subparsers.add_parser(
        "measure",
        help="measure per-constraint false-pass/false-fail/undecided rates (VER-03)",
        description=(
            "Measure the checker's per-constraint false-pass, false-fail and "
            "undecided rates over labelled synthetic populations. Reads the "
            "populations `gnd synth` wrote and their provenance sidecars, verifies "
            "the C6 sidecar binding before scoring, and emits a per-constraint "
            "report — three rates, each with its numerator AND its conditional "
            "denominator (C2), never a blended accuracy number (D-01). Computed "
            "OFFLINE from committed artifacts: no timestamp, so two runs over one "
            "corpus reproduce byte-for-byte. Exits 3 on a sidecar-binding "
            "mismatch, 5 on a population that fails to load, 6 on a checker defect "
            "(C9), 64 on a corpus mixing models or pool sources (C4)."
        ),
    )
    measure_parser.add_argument("model", help="path to the model file")
    measure_parser.add_argument(
        "--promote",
        default=None,
        metavar="DIR",
        help=(
            "D-14: copy each defect-revealing population and its model into DIR (the "
            "adversarial corpus root) and PRINT manifest rows in the locked record "
            "shape. The append itself stays a reviewed act — this never edits "
            "manifest.yaml"
        ),
    )
    measure_parser.add_argument(
        "--populations",
        required=True,
        help="output root of a `gnd synth` run (the directory holding index.json)",
    )
    measure_parser.add_argument(
        "--out", default=None, help="write the JSON payload to this path (default: stdout)"
    )
    _add_format_argument(measure_parser)
    _add_unredacted_argument(measure_parser)

    extract_parser = subparsers.add_parser(
        "extract",
        help="emit the per-model extraction artifact bundle (VER-01, DATA-02)",
        description=(
            "Derive the per-model extraction artifacts OFFLINE from "
            "model.orm.yaml: <stem>.projection.schema.json (the closed, "
            "shape-only structured-output projection, gated by a recursive "
            "allowlist that fails closed on unlisted keywords), "
            "<stem>.verbalization.txt (the constraint-blind rendering seed), "
            "<stem>.applicable.json (the three-path reference-scheme "
            "applicable set) and <stem>.artifacts.json (sha256 digests plus "
            "the header_template the executing skill copies verbatim). No "
            "provider is called and no network is touched — the executing "
            "agent running the gnd-extract skill is the only place a model "
            "is ever called. Exits 0 when the bundle is emitted, 3 when the "
            "model is invalid, 64 on usage errors, 70 when the projection "
            "gate refuses gnd's own emitter (an internal invariant breach), "
            "74 when the output path is refused or unwritable."
        ),
    )
    extract_parser.add_argument("model", help="path to the model file")
    extract_parser.add_argument(
        "--out", required=True, help="output directory for the four-file bundle"
    )

    export_parser = subparsers.add_parser("export", help="export an optional standalone artifact")
    export_targets = export_parser.add_subparsers(dest="export_target", required=True)
    from gnd.export.souffle_cli import add_parsers
    add_parsers(export_targets)
    from gnd.export.lean_cli import add_parsers as add_lean_parsers

    add_lean_parsers(export_targets)
    pyrel_parser = export_targets.add_parser("pyrel", help="export a standalone PyRel program")
    pyrel_parser.add_argument("model", help="path to the model file")
    pyrel_parser.add_argument("--out", required=True, help="new Python program path")
    connection_group = pyrel_parser.add_mutually_exclusive_group()
    connection_group.add_argument("--duckdb-path", default=":memory:")
    connection_group.add_argument("--connection", help="reserved named Snowflake connection")

    codegen_parser = subparsers.add_parser(
        "codegen",
        help="emit a plain-Python agent project derived from the model (GEN-01)",
        description=(
            "Turn model.orm.yaml into a plain-Python project with the GND "
            "shape: <package>/tools.py (one derived function per fact type, "
            "named and parameterized through the published model-id to "
            "Python-symbol mapping, with docstrings derived from the model's "
            "readings), the four-file extraction artifact bundle under "
            "artifacts/, a code-emitted SKILL.md the terminal agent runs, and "
            "create-once extension files (pyproject.toml, references/) that "
            "regeneration never rewrites. No provider SDK and no network "
            "library is emitted, so the generated project is CI-runnable with "
            "zero network and no API key — the agent running the generated "
            "SKILL.md is the only place a model is ever called. Every emitted "
            "Python module is parsed before any byte reaches disk. "
            "Re-running over an existing generated project is idempotent: an "
            "unchanged model performs ZERO writes and leaves every hash "
            "identical. A derived file you hand-edited, and an unmanaged file "
            "sitting at a derived path, are REFUSED rather than overwritten; "
            "--force overwrites them and still never touches an extension "
            "file. Exits 0 when the tree is written or already current, 3 when "
            "the model is invalid, two of its ids sanitize to one Python "
            "symbol (rename one), or the existing manifest is unreadable, 11 "
            "when a write was refused and nothing was destroyed, 64 on usage "
            "errors, 70 when an emitter invariant breaks over an already-valid "
            "model, 74 when the output path is refused or unwritable."
        ),
    )
    codegen_parser.add_argument("model", help="path to the model file")
    codegen_parser.add_argument(
        "--out",
        required=True,
        help="output directory for the generated project",
    )
    codegen_parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "overwrite hand-edited derived files and adopt unmanaged files at "
            "derived paths. Extension files (pyproject.toml, references/) are "
            "NEVER overwritten, with or without this flag, and no path outside "
            "the generated layout is ever touched."
        ),
    )

    conformance_parser = subparsers.add_parser(
        "conformance",
        help="check that a generated project still matches its model (GEN-02); temporal models refused",
        description=(
            "Ask whether a project `gnd codegen` generated still agrees with "
            "the model it came from. FOUR assertions run. Two are exact and "
            "corroborating: INTEGRITY — every code-emitted file still hashes "
            "to what the codegen manifest recorded — and CURRENCY, the "
            "manifest's model digest against the model's digest now, which IS "
            "model-code drift: the model moved and the code did not. Both are "
            "importable functions rather than CLI-only paths, so a downstream "
            "tool can invoke them without going through argv. The third is "
            "STRUCTURAL, and it is the assertion that makes a green result "
            "mean anything: the emitted surface is checked against the fact "
            "types the MODEL declares, computed from the model and the "
            "filesystem and never from the manifest or a previous generation. "
            "Without it the other two establish only that the generator agrees "
            "with itself — a project that is well-formed and empty, with every "
            "digest re-signed, passes both. The fourth is ARCHITECTURE: authored "
            "module, symbol, artifact and entry-point declarations are compared "
            "with static filesystem and AST observations without executing the "
            "project. Fully offline "
            "over committed artifacts, and the generated project is NEVER "
            "imported — this command reads bytes and hashes them, because "
            "importing a module to inspect it would execute the project's own "
            "code on every CI run. What a GREEN result does not say travels in "
            "the payload, not only in this text: every file the manifest "
            "records appears in either `examined` or `unexamined` by integrity, "
            "and extension files (pyproject.toml, references/) are not digest-gated because "
            "human- and LLM-authored text is not byte-reproducible and cannot "
            "be digest-gated, and the required `limits` block names the "
            "manifest co-edit blind spot — a manifest cannot record its own "
            "digest, so a derived file edited TOGETHER with its manifest entry "
            "is undetectable by digest comparison, exactly as in `gnd doctor`. "
            "Two runs over one unchanged project print byte-identical JSON. "
            "Exits 0 when all four assertions ran and found nothing, 13 when the "
            "generated code no longer matches its model (one band for the "
            "whole command — the payload names which assertion and which "
            "file), 3 when the codegen manifest will not parse, 64 on usage "
            "errors, 66 when the manifest or the model is missing so nothing "
            "could be compared at all (fail closed — a check that could not "
            "run must not read as one that passed), 74 when the project tree "
            "could not be read."
        ),
    )
    conformance_parser.add_argument("model", help="path to the model file")
    conformance_parser.add_argument(
        "directory", help="the generated project's root (the directory `gnd codegen --out` wrote)"
    )
    _add_format_argument(conformance_parser)

    recovery_parser = subparsers.add_parser(
        "recovery",
        help="inventory static code evidence and verify one recovered model bundle",
        description=(
            "Run the one-time, execution-free recovery boundary. Inventory reads only "
            "explicit categorized roots under ROOT with closed byte/file limits and "
            "writes one immutable JSON census. Verify re-resolves the canonical model, "
            "full verbalization, report, evidence digests, typed locators, and exact "
            "selected-path census. Neither command imports or executes repository code, "
            "launches an agent, invokes conformance, or generates code. Exits 3 for an "
            "ill-formed inventory/report or failed digest/locator claim, 66 when a "
            "required input is missing, and 74 for refused or unreadable paths and I/O."
        ),
    )
    recovery_subparsers = recovery_parser.add_subparsers(
        dest="recovery_command",
        required=True,
    )
    recovery_inventory_parser = recovery_subparsers.add_parser(
        "inventory",
        help="write one bounded closed census of explicit static repository roots",
        description=(
            "Read explicitly selected source, test, documentation, configuration, and "
            "schema roots as inert bytes. Every selected path is classified as parsed, "
            "excluded, ambiguous, or frontier; source text is never copied into the "
            "inventory. --exclude uses REASON=PATH where REASON is dependency, vendored, "
            "generated, cache, build, or sensitive-tree. The output is write-once. "
            "Exits 3 for an empty/malformed scope, 66 for a missing root, and 74 for an "
            "unsafe/unreadable path or refused output."
        ),
    )
    recovery_inventory_parser.add_argument(
        "root",
        metavar="ROOT",
        help="authoritative existing repository root",
    )
    for option, destination, label in (
        ("--source", "sources", "source"),
        ("--tests", "tests", "test"),
        ("--docs", "docs", "documentation"),
        ("--config", "configs", "configuration"),
        ("--schema", "schemas", "schema"),
    ):
        recovery_inventory_parser.add_argument(
            option,
            dest=destination,
            action="append",
            default=[],
            metavar="PATH",
            help=f"repository-relative {label} root (repeatable)",
        )
    recovery_inventory_parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="REASON=PATH",
        help="closed exclusion reason and repository-relative path (repeatable)",
    )
    recovery_inventory_parser.add_argument(
        "--max-file-bytes",
        type=_positive_int,
        default=2 * 1024 * 1024,
        help="maximum bytes read from one selected file (default: 2097152)",
    )
    recovery_inventory_parser.add_argument(
        "--max-total-bytes",
        type=_positive_int,
        default=32 * 1024 * 1024,
        help="maximum aggregate bytes read from selected files (default: 33554432)",
    )
    recovery_inventory_parser.add_argument(
        "--max-files",
        type=_positive_int,
        default=10_000,
        help="maximum selected file observations (default: 10000)",
    )
    recovery_inventory_parser.add_argument(
        "--out",
        required=True,
        metavar="INVENTORY.json",
        help="write-once inventory JSON destination beneath ROOT",
    )

    recovery_verify_parser = recovery_subparsers.add_parser(
        "verify",
        help="verify the canonical three-artifact recovery bundle and every claim",
        description=(
            "Verify REPORT beneath authoritative ROOT, together with its explicit "
            "canonical sibling model and full verbalization. All leaves are no-follow "
            "regular files; the runtime reloads the model, reproduces the complete "
            "verbalization, resolves every evidence locator, and re-inventories the "
            "selected roots. Exits 3 for malformed/stale evidence, 66 for a missing "
            "artifact, and 74 for unsafe/unreadable paths or I/O."
        ),
    )
    recovery_verify_parser.add_argument(
        "root",
        metavar="ROOT",
        help="authoritative existing recovery bundle/repository root",
    )
    recovery_verify_parser.add_argument(
        "report",
        metavar="REPORT",
        help="explicit canonical model.recovery.json beneath ROOT",
    )
    recovery_verify_parser.add_argument(
        "--model",
        default="model.orm.yaml",
        metavar="MODEL",
        help="explicit recovered model sibling (default: model.orm.yaml)",
    )
    recovery_verify_parser.add_argument(
        "--verbalization",
        default="model.verbalization.txt",
        metavar="VERBALIZATION",
        help="explicit full verbalization sibling (default: model.verbalization.txt)",
    )

    evolve_parser = subparsers.add_parser(
        "evolve",
        help="preview, apply, and finalize one digest-bound model evolution",
        description=(
            "Run the staged offline evolution protocol over explicit files. "
            "Preview validates without mutation; apply revalidates the exact "
            "reviewed preview, performs the model CAS, and completes the live "
            "conformance recheck in one invocation; finalize completes a "
            "pending state left behind by an interrupted apply. The CLI does "
            "not propose changes, repair projects, or select a runtime."
        ),
    )
    evolve_subparsers = evolve_parser.add_subparsers(
        dest="evolve_command",
        required=True,
    )
    evolve_preview_parser = evolve_subparsers.add_parser(
        "preview",
        help="validate a proposal and publish one immutable review claim",
        description=(
            "Read MODEL and PROPOSAL beneath the authoritative workspace, "
            "validate the candidate and blast radius, and write the complete "
            "digest-bound preview to PREVIEW without changing the model, "
            "verbalization, records, or linked projects."
        ),
    )
    evolve_preview_parser.add_argument("model", help="current model file beneath ROOT")
    evolve_preview_parser.add_argument(
        "proposal", help="closed evolution proposal JSON beneath ROOT"
    )
    evolve_preview_parser.add_argument(
        "--workspace",
        required=True,
        help="authoritative existing workspace ROOT",
    )
    evolve_preview_parser.add_argument(
        "--records",
        required=True,
        help="authoritative immutable evidence DIR",
    )
    evolve_preview_parser.add_argument(
        "--out",
        required=True,
        help="write-once PREVIEW JSON path beneath ROOT",
    )
    _add_format_argument(evolve_preview_parser)

    evolve_apply_parser = evolve_subparsers.add_parser(
        "apply",
        help="revalidate an exact preview and complete the whole evolution",
        description=(
            "Require PROPOSAL and PREVIEW to reproduce the current exact "
            "preview, obtain the exact blast-radius digest for a breaking "
            "proposal, publish the candidate model CAS and durable "
            "pending-finalization evidence, then complete the verbalization, "
            "live linked-project conformance, and final record in the same "
            "invocation. The exit is the raw aggregate conformance exit, so "
            "linked drift returns 13 with the model published and no rollback."
        ),
    )
    evolve_apply_parser.add_argument("model", help="current model file beneath ROOT")
    evolve_apply_parser.add_argument("proposal", help="closed evolution proposal JSON beneath ROOT")
    evolve_apply_parser.add_argument(
        "--preview",
        required=True,
        help="exact reviewed PREVIEW JSON beneath ROOT",
    )
    evolve_apply_parser.add_argument(
        "--workspace",
        required=True,
        help="authoritative existing workspace ROOT",
    )
    evolve_apply_parser.add_argument(
        "--records",
        required=True,
        help="authoritative immutable evidence DIR",
    )
    _add_format_argument(evolve_apply_parser)

    evolve_finalize_parser = evolve_subparsers.add_parser(
        "finalize",
        help="complete exact pending leaves and publish the final record last",
        description=(
            "Load one immutable PENDING identity, finish its exact "
            "verbalization and linked-project conformance leaves, and publish "
            "the final evolution record last. Linked drift remains exit 13 "
            "with its raw evidence; no rollback or regeneration occurs."
        ),
    )
    evolve_finalize_parser.add_argument("model", help="published model file beneath ROOT")
    evolve_finalize_parser.add_argument(
        "pending", help="immutable pending-finalization JSON beneath ROOT"
    )
    evolve_finalize_parser.add_argument(
        "--workspace",
        required=True,
        help="authoritative existing workspace ROOT",
    )
    evolve_finalize_parser.add_argument(
        "--records",
        required=True,
        help="authoritative immutable evidence DIR",
    )
    _add_format_argument(evolve_finalize_parser)

    doccheck_parser = subparsers.add_parser(
        "doccheck",
        help="validate a rendered document's manifest against its renderer obligations (DATA-02)",
        description=(
            "Discharge the gnd-render-doc skill's obligations by CODE over the "
            "document manifest (skill prose explains, validators discharge). "
            "Four obligations: (1) binding — document_sha256, "
            "source_population_sha256 and applicable_sha256 match the actual "
            "file bytes; (2) rendering — every role filler of every APPLICABLE "
            "fact type in the source population is mentioned in the document "
            "under lexical normalization, direct fillers as their value and "
            "composite fillers via their identifying component values; "
            "inapplicable fact types are exempt BY the published "
            "applicable-set artifact, never by leniency; (3) distractors — at "
            "least one of each kind (out-of-model, near-miss-entity, "
            "absent-fact), every distractor text present in the document, and "
            "every absent-fact distractor genuinely absent from the source "
            "population; (4) renderer identity fields non-empty. Exits 0 when "
            "every obligation holds, 3 on any violation (one line each), 64 on "
            "usage errors, 66 when the applicable-set artifact or any "
            "manifest-named file is missing (fail closed — an obligation that "
            "cannot be checked is never skipped)."
        ),
    )
    doccheck_parser.add_argument("model", help="path to the model file")
    doccheck_parser.add_argument(
        "manifest", help="path to the document manifest (paths resolve beside it)"
    )
    doccheck_parser.add_argument(
        "--artifacts",
        required=True,
        help="the gnd extract bundle directory holding <stem>.applicable.json",
    )

    fidelity_parser = subparsers.add_parser(
        "fidelity",
        help="measure extractor fidelity per fact type over committed cases (DATA-02)",
        description=(
            "Measure the EXTRACTOR, per fact type, over committed case "
            "directories. This command emits RATES and never a per-run verdict "
            "— it is the dual of `gnd verify`, which emits verdicts and never a "
            "rate: a checker pass over an uncalibrated extraction is not "
            "evidence of faithfulness. Matching is by the model's own reference "
            "scheme under a LEXICAL-only normalization, multiset (tp per "
            "identity key is min(source_count, extracted_count)), with INCLUSIVE "
            "precision (unresolved and ambiguous extractions stay in the "
            "denominator) and `ambiguous` as an explicit outcome for "
            "normalization collisions and broken composite identities — never "
            "an arbitrary match. Every rate ships with its numerator AND "
            "denominator, no figure blends fact types, and the payload is "
            "schema-REQUIRED to report calibration.state 'uncalibrated' and "
            "publishable false: the round trip measures the round trip, and "
            "while the calibration set is deferred no interval field may exist "
            "at all. Fully offline over committed artifacts. Exits 0 with the "
            "report, 3 on a digest binding mismatch inside a case, 64 on usage "
            "errors or a case set spanning more than one model, 66 when a "
            "required extraction artifact is missing (fail closed — a missing "
            "applicable set must not read as coverage), 70 on an internal "
            "contract breach, 74 when the output path is refused."
        ),
    )
    fidelity_parser.add_argument("model", help="path to the model file")
    fidelity_parser.add_argument(
        "--cases",
        required=True,
        help=(
            "directory of case directories, each carrying source.population.json, "
            "document.md, document.manifest.json, extracted.population.json and "
            "extracted.population.extraction.json (or extraction.skipped.json)"
        ),
    )
    fidelity_parser.add_argument(
        "--artifacts",
        required=True,
        help="the gnd extract bundle directory holding <stem>.applicable.json",
    )
    fidelity_parser.add_argument("--out", help="write the payload to this path")
    _add_format_argument(fidelity_parser)

    review_parser = subparsers.add_parser(
        "review",
        help="run the bounded six-reviewer advisory panel and finalize its synthesis (REV-01)",
        description=(
            "Advisory multi-CLI review over ONE of exactly three input classes — "
            "a plan, an experiment outcome, or a spec/results/delta bundle. GND "
            "attempts six reviewer seats over five installed terminal-agent CLIs "
            "(claude, codex, qwen, gemini, kimi, plus a glm seat that runs the "
            "claude CLI against Z.AI's Anthropic-compatible endpoint) through "
            "fixed Python-owned invocation argv and bounded "
            "prompt transport (stdin for five, one --prompt argv element for Kimi), "
            "keeps one closed envelope "
            "per reviewer including "
            "every timeout, authentication failure, missing executable and "
            "unparseable response, and requires three DISTINCT schema-valid "
            "successes before any panel result may be reported. Every reviewer "
            "must first return substantive help that documents every long flag in "
            "the invocation GND is about to send; an incompatible reviewer is never "
            "invoked. GND does not sandbox reviewer CLIs or enforce read-only "
            "execution. It verifies the reviewed artifacts are unchanged before "
            "publishing a run. The panel ships no provider SDK and sources no "
            "credentials."
        ),
    )
    review_subparsers = review_parser.add_subparsers(dest="review_command", required=True)

    review_panel_parser = review_subparsers.add_parser(
        "panel",
        help="attempt all six reviewers and publish one immutable evidence directory",
        description=(
            "Load and digest-bind a review request, attempt all six reviewers "
            "concurrently under one shared deadline, and publish the normalized "
            "request, four raw streams and one closed envelope per reviewer, "
            "every validated response, and a manifest-last run.json into a "
            "directory that must not already exist. REQUEST and every artifact "
            "it names are repository-relative paths resolved against the "
            "directory you are standing in. Every bound must be strictly "
            "positive and is validated BEFORE any process is spawned; each "
            "reviewer's deadline is the earlier of --reviewer-timeout and the "
            "remaining --overall-timeout. Prints one closed JSON summary and "
            "never a verdict, a rate, or a conformance result. Exits 0 when at "
            "least three distinct reviewers returned schema-valid responses, 16 "
            "when all six attempts completed and fewer than three did, 3 when "
            "the request or a reviewer-cited artifact is ill-formed, 11 when the "
            "output directory already exists (nothing was written and no "
            "reviewer was invoked), 64 on usage errors including a non-positive "
            "bound, 66 when the request or a reviewed artifact is missing, 70 on "
            "an internal defect, 74 on refused or failed path/IO."
        ),
    )
    _add_review_panel_arguments(review_panel_parser)

    review_panel_light_parser = review_subparsers.add_parser(
        "panel-light",
        help="run the same panel at high or medium supported per-run effort",
        description=(
            "Run the same bounded six-reviewer advisory panel and publish the "
            "same immutable evidence as `gnd review panel`, but request a lighter "
            "supported per-run effort from Claude and Codex. The default is high; "
            "--effort medium is the only alternative. Qwen uses persistent effort "
            "configuration, and Gemini, Kimi, and the GLM seat expose no per-run "
            "effort flag, so "
            "their invocation policies and models are unchanged. All request, "
            "quorum, deadline, evidence, exit-band, and no-sandbox rules are "
            "identical to the quality-first panel."
        ),
    )
    _add_review_panel_arguments(review_panel_light_parser)
    review_panel_light_parser.add_argument(
        "--effort",
        choices=("high", "medium"),
        default="high",
        help="supported per-run effort for Claude and Codex (default: high)",
    )

    review_finalize_parser = review_subparsers.add_parser(
        "finalize",
        help="validate a semantic synthesis against immutable run evidence and render it",
        description=(
            "Take one immutable panel RUN directory and one closed SYNTHESIS "
            "document — the semantic grouping an agent authored over the "
            "successful responses — and prove it before rendering: the synthesis "
            "must bind the run by digest, account for every retained concern "
            "exactly once, give every agreed concern at least two DISTINCT "
            "successful supporting reviewers, keep every evidence-backed "
            "singleton under divergent views, and trace every prioritized fix to "
            "the complete supporter and evidence set of each group it touches. "
            "Reviewer quorum (three) and concern agreement (two) are different "
            "thresholds and neither substitutes for the other. Nothing in a "
            "reviewed artifact is ever written, no fix is applied, and an "
            "existing report is never replaced. Exits 0 when the report is "
            "rendered, 16 when the run itself is below quorum, 3 when the run "
            "evidence or the synthesis fails closed validation, 11 when the "
            "report path already exists, 64 on usage errors, 66 when the run "
            "directory or the synthesis is missing, 74 on refused or failed "
            "path/IO."
        ),
    )
    review_finalize_parser.add_argument(
        "run", help="the immutable panel run directory published by gnd review panel"
    )
    review_finalize_parser.add_argument(
        "synthesis", help="the closed semantic synthesis JSON authored over that run"
    )
    review_finalize_parser.add_argument(
        "--out",
        required=True,
        help="path to write PANEL-REVIEW.md; an existing file is never replaced",
    )

    exp_parser = subparsers.add_parser(
        "exp",
        help="scaffold, author, run, validate, and close experiments",
        description=(
            "Work with experiments — the unit that carries a question, the run "
            "that answered it, and the evidence for the answer. This lane owns "
            "the structural INVARIANTS (does the spec parse, does every declared "
            "question id resolve, does every evidence pointer name a file inside "
            "the experiment); the language — what makes a good question or a good "
            "conclusion — belongs to the skill. Fully offline: an experiment's "
            "recorded conclusion is only worth something if a reviewer can "
            "recompute it from the committed tree."
        ),
    )
    exp_subparsers = exp_parser.add_subparsers(dest="exp_command", required=True)
    from gnd.exp.spec import ExperimentKind

    exp_init_parser = exp_subparsers.add_parser(
        "init",
        help="scaffold a new experiment directory with its SPEC.md",
        description=(
            "Create <out>/<ID>/SPEC.md declaring the questions this experiment "
            "will have to answer. ID must match ^EXP-\\d{3}-[a-z0-9][a-z0-9-]*$ "
            "because the id IS the directory name, and every write goes through "
            "the shipped traversal guard. An existing experiment directory is "
            "REFUSED, never overwritten, and there is deliberately no --force: "
            "an experiment directory holds recorded conclusions and evidence. "
            "Exits 0 when the spec is written, 3 when the requested declaration "
            "is not a valid ExperimentSpec, 11 when the experiment directory "
            "already exists (nothing was written), 64 on usage errors including "
            "a malformed ID or a --question that is not ID=TEXT, 74 when the "
            "output path is refused by the guard or is unwritable."
        ),
    )
    exp_init_parser.add_argument("id", help="the experiment id, e.g. EXP-001-codegen-drift")
    exp_init_parser.add_argument(
        "--out", required=True, help="directory the experiment directory is created in"
    )
    exp_init_parser.add_argument(
        "--kind",
        choices=get_args(ExperimentKind),
        default="codegen",
        help="the closed experiment kind (default: codegen)",
    )
    exp_init_parser.add_argument(
        "--title", default=None, help="one line saying what this experiment is for"
    )
    exp_init_parser.add_argument(
        "--question",
        dest="questions",
        action="append",
        type=_parse_question,
        default=None,
        metavar="ID=TEXT",
        help="a declared question; repeatable. Every id must be answered to close.",
    )
    exp_init_parser.add_argument(
        "--covers",
        action="append",
        type=_parse_covers,
        default=None,
        metavar="ENTRY",
        help=(
            "compact JSON model-element cover with exactly one of operation, "
            "constraint, fact_type, or derivation (which addresses "
            "derivation:<id>); repeatable"
        ),
    )
    exp_init_parser.add_argument(
        "--session-contract",
        default=None,
        metavar="PATH",
        help="contract inspected only to establish the work tests-only covers exemption",
    )

    exp_validate_parser = exp_subparsers.add_parser(
        "validate",
        help="check that an experiment directory is structurally well-formed",
        description=(
            "Read <DIR>/SPEC.md and report its structure: id, kind, title, the "
            "declared question ids in declared order, and any follows: "
            "references. The spec is UNTRUSTED committed metadata, so the read "
            "is byte-capped before it happens, anchors/aliases are refused, "
            "unknown keys are rejected (extra=forbid), the experiment kind is a "
            "closed vocabulary, and duplicate or empty question ids are refused "
            "— a duplicate declaration makes the close gate's declared-vs-"
            "resolved set difference ambiguous. Exits 0 when the experiment is "
            "well-formed, 3 when SPEC.md is unparseable, schema-invalid, or "
            "declares an id that disagrees with its own directory name, 64 on "
            "usage errors, 66 when SPEC.md is missing entirely (fail closed — a "
            "directory without a spec is not an experiment with nothing wrong)."
        ),
    )
    exp_validate_parser.add_argument("directory", help="the experiment directory")

    exp_author_expectation_parser = exp_subparsers.add_parser(
        "author-expectation",
        help="hash an exact answer, remove its source, and reject any surviving copy",
        description=(
            "Author one answer-free exact-bytes expectation in "
            "<DIR>/session.contract.json. --from must be an experiment-relative "
            "regular file (an absolute path is accepted only when it remains "
            "inside DIR). The source is read through descriptor-anchored, "
            "no-follow traversal and the 10 MiB session-input cap, the updated "
            "contract is production-validated before publication, the source is "
            "deleted, and every regular file under the experiment root is scanned "
            "for equal bytes. The contract entry contains sha256, output_id, "
            "candidate_path, comparison, media_type, and encoding, but no path or "
            "size_bytes. Exits 0 only after the published contract loads and no "
            "answer copy remains; 3 when the spec, contract, case, output, source, "
            "or answer-copy state is refused; 64 on usage errors; 66 when SPEC.md "
            "is missing; 74 on refused or failed path/I/O."
        ),
    )
    exp_author_expectation_parser.add_argument(
        "directory", help="the data-driven experiment directory"
    )
    exp_author_expectation_parser.add_argument(
        "--case", dest="case_id", required=True, help="case_id to update"
    )
    exp_author_expectation_parser.add_argument(
        "--output-id", required=True, help="expected output id to insert or replace"
    )
    exp_author_expectation_parser.add_argument(
        "--candidate-path",
        required=True,
        help="output path relative to candidate/",
    )
    exp_author_expectation_parser.add_argument(
        "--from",
        dest="source",
        required=True,
        help="produced answer file inside the experiment root",
    )
    exp_author_expectation_parser.add_argument(
        "--media-type",
        default="application/json",
        help="declared media type (default: application/json)",
    )
    exp_author_expectation_parser.add_argument(
        "--encoding",
        default="utf-8",
        help="declared encoding (default: utf-8)",
    )

    exp_run_parser = exp_subparsers.add_parser(
        "run",
        help="run one bounded attempt for a data-driven experiment",
        description=(
            "Load a kind: data-driven SPEC.md and its conventional "
            "session.contract.json, invoke exactly one trusted terminal-agent "
            "adapter, run GND's machine verifier over every declared case, and "
            "publish immutable evidence under runs/. The adapter vocabulary is "
            "closed; no executable, provider, model, argv, attempt increase, or "
            "contract-bound loosening is accepted. This does not close the "
            "experiment: gnd exp close remains the separate completeness gate. "
            "Exits 0 on exact required-case acceptance, 15 on a well-formed "
            "nonaccepted session, 3 on malformed or mismatched committed input, "
            "64 on usage errors or a wall-bound loosening, 66 when a required "
            "artifact or selected adapter is missing, 70 on an internal defect, "
            "74 on refused or failed path/I/O. Child verifier exits 1 through 4 "
            "are retained as case evidence and never become this parent exit."
        ),
    )
    exp_run_parser.add_argument("directory", help="the data-driven experiment directory")
    exp_run_parser.add_argument(
        "--adapter",
        choices=("claude", "codex"),
        help="legacy trusted terminal-agent adapter (contracts v1-v5)",
    )
    exp_run_parser.add_argument(
        "--adapter-policy",
        help="trusted local declared-adapter policy path (contracts v6/v7; v7 supports bounded patches and ranking)",
    )
    exp_run_parser.add_argument(
        "--wall-seconds",
        type=_positive_finite_float,
        default=None,
        help="optional positive finite tightening of the contract wall bound",
    )
    exp_run_parser.add_argument(
        "--test-argv",
        action="append",
        default=None,
        metavar="WORD",
        help="one exact tests-mode child argv word; repeatable and never shell-parsed",
    )

    exp_close_parser = exp_subparsers.add_parser(
        "close",
        help="has this experiment discharged every question it declared?",
        description=(
            "Refuse to close an experiment that did not finish what it declared. "
            "The verdict is a difference of two SETS — the question ids in "
            "SPEC.md and the resolution ids in CONCLUSIONS.md — and it fails "
            "when EITHER difference is non-empty: a declared question left "
            "unresolved, or an orphan answer to a question nobody asked. It also "
            "fails when a resolution's evidence pointer does not name a file "
            "inside the experiment directory, or when a follows: reference names "
            "an experiment that does not exist or has not concluded. "
            "The OUTCOME VALUES never affect the verdict. An experiment whose "
            "every question honestly resolves to 'unanswered' with a reason and "
            "a citation CLOSES at exit 0 — a gate that demanded success would pay "
            "for lying, and the gate's job is that a question cannot be quietly "
            "forgotten, not that experiments succeed. "
            "This is a validator, not a state machine: nothing is written and no "
            "status is recorded. Exits 0 when every obligation is discharged, 3 "
            "when SPEC.md or CONCLUSIONS.md is unparseable, schema-invalid, or "
            "declares another experiment's id, 14 when an obligation is "
            "undischarged INCLUDING a missing CONCLUSIONS.md (the gate's own "
            "verdict — the experiment is open, not the input missing), 64 on "
            "usage errors, 66 when SPEC.md is missing entirely, 74 when the "
            "directory cannot be read."
        ),
    )
    exp_close_parser.add_argument("directory", help="the experiment directory")

    solve_station_order = ", ".join(station.name for station in solve.STATIONS)
    solve_exit_map = ", ".join(
        f"{code} {meaning}" for code, meaning in exits_module.SOLVE_CONTROL_PLANE_EXITS
    )
    solve_parser = subparsers.add_parser(
        "solve",
        help="walk the CLI-pure GND stations in order, gating each, and log the walk",
        description=(
            f"Walk the CLI-pure GND stations in locked order -- {solve_station_order} "
            "-- blocking for an authorization "
            "before each one and appending an authorization record to a walk log "
            "before the station is spawned.\n"
            "\n"
            "WHAT THIS GUARANTEES: sequence, gating and logging FOR WALKS THAT GO "
            "THROUGH IT. Nothing more.\n"
            "\n"
            "WHAT IT DOES NOT GUARANTEE: the process in general. Running the "
            "stations a la carte stays legal and is not a violation of anything -- "
            "a harness that could not be bypassed would be routed around, and a "
            "bypassed harness is worse than none, because its log's existence "
            "would falsely imply the walk is where work happens.\n"
            "\n"
            "IT DOES NOT JUDGE STATION-INTERNAL AGENT WORK. The guarantee's "
            "perimeter is the walk log's perimeter.\n"
            "\n"
            "A STATION'S OWN EXIT IS IN THE LOG, NOT IN THIS COMMAND'S EXIT CODE. "
            f"The exit code is a control plane: {solve_exit_map}. "
            "A caller scripting this command reads the code "
            "and then reads the log; a station exiting 11 does not make gnd solve "
            "claim a collision about itself.\n"
            "\n"
            "THE BROWNFIELD PROFILE ASSUMES RECOVERY ALREADY COMPLETED. "
            "--skip synth --skip codegen --skip conformance leaves gnd validate; a "
            "recovered model's gate is gnd recovery verify, which runs BEFORE this "
            "harness is entered, not inside it.\n"
            "\n"
            "THE WALK LOG RECORDS WHAT THIS HARNESS DID; IT IS NOT PROOF THAT IT "
            "DID IT. A log that satisfies the walk predicate is a self-consistent "
            "document, and a file authored by hand can be self-consistent too. It "
            "attests no spawn, no executed argv, no existing artifact and no human "
            "presence.\n"
            "\n"
            "THE OUTER STATION TIMEOUT IS NOT THE CONTRACT'S INNER --wall-seconds "
            "BOUND. --station-timeout bounds the child process; this harness passes "
            "no --wall-seconds to gnd exp run, because a contract's own wall bound "
            "is the contract's business."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    solve_parser.add_argument("model", help="path to the model file")
    solve_parser.add_argument(
        "--workspace",
        required=True,
        action=_StoreOnce,
        help=(
            "the directory every station writes into. Required: a walk that wrote "
            "five artifacts into whatever directory the caller happened to be "
            "standing in is the accident this argument exists to prevent"
        ),
    )
    solve_parser.add_argument(
        "--experiment",
        action=_StoreOnce,
        help=(
            "the data-driven experiment directory for the exp-run station, which "
            "must resolve strictly inside --workspace. Mandatory when exp-run is "
            "selected and refused when it is not"
        ),
    )
    solve_parser.add_argument(
        "--from",
        dest="from_station",
        action=_StoreOnce,
        help="first station to run, inclusive",
    )
    solve_parser.add_argument("--until", action=_StoreOnce, help="last station to run, inclusive")
    solve_parser.add_argument(
        "--skip",
        action="append",
        default=[],
        metavar="NAME",
        help="omit a station; repeatable, and repeating one name is not an error",
    )
    solve_parser.add_argument(
        "--auto",
        action="store_true",
        help=(
            "authorize every gate without blocking. The log is NOT byte-identical "
            "to a gated walk: flags.auto is true and every authorization carries "
            "the auto source token"
        ),
    )
    solve_parser.add_argument(
        "--adapter",
        action=_StoreOnce,
        choices=("claude", "codex"),
        help="terminal-agent adapter for the exp-run station; resolves to claude",
    )
    solve_parser.add_argument(
        "--adapter-policy",
        action=_StoreOnce,
        help="trusted local declared-adapter policy for a schema-v6 exp-run station",
    )
    solve_parser.add_argument(
        "--test-argv",
        dest="test_argv",
        action="append",
        default=[],
        metavar="WORD",
        help="forwarded to the exp-run station verbatim, in the order given",
    )
    solve_parser.add_argument(
        "--station-timeout",
        dest="station_timeout",
        action="append",
        default=[],
        metavar="NAME=SECONDS",
        help=(
            "override one station's outer timeout. SECONDS is a positive integer "
            f"no greater than {solve.MAX_STATION_TIMEOUT_S}: an unbounded override "
            "is an unbounded child wearing a flag"
        ),
    )

    install_parser = subparsers.add_parser(
        "install",
        help="place every packaged GND skill into your agent runtime's skills directory",
        description=(
            "Place every packaged GND skill into your agent runtime's skills "
            "directory. Copies by default; a second run with no intervening change "
            "performs zero writes, and a file GND did not place is never overwritten "
            "without --force. Text output only: --format json exists so a retry loop "
            "can consume VERIFIER output, and this is a human-operated setup command "
            "with no programmatic consumer, so a machine-readable install report is "
            "deliberately not offered (D-25)."
        ),
    )
    _add_target_arguments(install_parser)
    install_parser.add_argument(
        "--symlink",
        action="store_true",
        help=(
            "link skill directories instead of copying — DEVELOPMENT INSTALLS ONLY. "
            "A tool environment is rebuilt on upgrade and removed on uninstall, so a "
            "link into one is silently swapped after a same-interpreter reinstall and "
            "dangles outright after an interpreter-version change or an uninstall"
        ),
    )
    install_parser.add_argument(
        "--force",
        action="store_true",
        help="replace unmanaged files that block a write (never touches files you edited)",
    )
    install_parser.add_argument(
        "--sync",
        action="store_true",
        help=(
            "ignore the runtime and scope flags; refresh every standard root that "
            "already carries an install manifest. This is the second half of "
            "`uv tool upgrade get-nick-done && gnd install --sync`"
        ),
    )

    doctor_parser = subparsers.add_parser(
        "doctor",
        help="report the state of every GND skill this machine has placed",
        description=(
            "Report every placed asset as current, stale, missing, modified or "
            "collided, and print the two environment facts that explain most "
            "'it did not work' reports: the directory the running executable lives "
            "in with an on-PATH verdict, and every target root inspected. BOTH "
            "scopes are always inspected, whichever scope flag is given, because "
            "skill precedence puts the user level ahead of the project level and a "
            "shadowed project install is the most common confusing outcome. Exits 0 "
            "when everything is current, 10 on drift, 11 on a collision, 12 when "
            "nothing is installed anywhere. Text output only, for the reason "
            "`gnd install --help` gives (D-25). "
            "Scope: installed-asset state ONLY. A green doctor says nothing about "
            "your model or its conformance state — in particular it does not report "
            "a pending evolution finalization, which `gnd evolve` reports and "
            "refuses. Reading exit 0 here as 'my model is fine' is the one "
            "misreading this command cannot make for you."
        ),
    )
    _add_target_arguments(doctor_parser)

    uninstall_parser = subparsers.add_parser(
        "uninstall",
        help="remove the GND skills this machine placed, leaving your own edits alone",
        description=(
            "Remove every skill file GND placed at the requested target roots. A file "
            "is deleted only when its bytes still hash to what the install receipt "
            "recorded, so anything you edited is KEPT and named in the report — there "
            "is deliberately no flag that overrides this. Files GND never placed are "
            "never touched. The directories emptied by the removal are pruned and the "
            "receipt is removed last. Unlike `doctor`, this acts on exactly the scope "
            "you name. Exits 0 on a clean removal, 10 when something was kept, 12 when "
            "nothing is installed, 74 when a receipt could not be trusted (in which "
            "case nothing at all was deleted). Text output only (D-25)."
        ),
    )
    _add_target_arguments(uninstall_parser)

    judgment_parser = subparsers.add_parser("judgments", help="evaluate saved external opinions")
    judgment_sub = judgment_parser.add_subparsers(dest="judgment_command", required=True)
    judgment_check = judgment_sub.add_parser(
        "check", help="check saved receipts and confidence floors"
    )
    judgment_check.add_argument("model")
    judgment_check.add_argument("population")
    for name in ("policy", "receipts", "trusted-root"):
        judgment_check.add_argument("--" + name, required=True)
    judgment_check.add_argument("--reference-root")
    judgment_check.add_argument("--unredacted", action="store_true")
    judgment_check.add_argument("--format", choices=("json", "text"), default="text")

    args = parser.parse_args(argv)
    if args.command == "judgments":
        from gnd.api import judgments
        from gnd.artifacts import canonical_json_bytes

        result = judgments(
            args.model,
            args.population,
            args.policy,
            args.receipts,
            trusted_root=args.trusted_root,
            reference_root=args.reference_root,
            unredacted=args.unredacted,
        )
        print(
            canonical_json_bytes(result, exact_numbers=True).decode()
            if args.format == "json"
            else "saved judgment outcome: " + str(result["outcome"])
        )
        return result["outcome"]

    if args.command in {"witness", "replay", "witness-view"}:
        from gnd.witness.cli import run as run_witness

        return run_witness(args)
    if args.command == "diff":
        return _cmd_diff(
            args.model_a, args.model_b, args.populations, args.format, args.unredacted, args.seed
        )
    if args.command == "import":
        source_artifact = args.source_artifact
        if source_artifact is None:
            supplied = args.model
            candidate = PurePosixPath(supplied)
            if (
                Path(supplied).is_absolute()
                or PureWindowsPath(supplied).is_absolute()
                or "\\" in supplied
                or any(part in {"", ".", ".."} for part in supplied.split("/"))
            ):
                rai_import_parser.error(
                    "an absolute or unstable MODEL path requires --source-artifact"
                )
            source_artifact = candidate.as_posix()
        return _cmd_rai_import(args.model, args.out, source_artifact, args.source_commit)
    if args.command == "verbalize":
        if (args.anchors is None) != (args.document is None):
            verbalize_population_parser.error("--anchors and --document must be supplied together")
        return _cmd_verbalize_population(
            args.model,
            args.population,
            args.format,
            anchors_path=args.anchors,
            document_path=args.document,
            unredacted=args.unredacted,
        )
    if args.command == "check":
        if (args.anchors is None) != (args.document is None):
            check_parser.error("--anchors and --document must be supplied together")
        if (args.anchors is not None or args.document is not None) and (
            args.populations is not None
            or args.pre is not None
            or args.steps is not None
            or args.post is not None
        ):
            check_parser.error("--anchors and --document apply only to snapshot checks")
        transition_arm = {"--pre": args.pre, "--steps": args.steps, "--post": args.post}
        supplied = {flag for flag, value in transition_arm.items() if value is not None}
        if args.populations is not None:
            if args.admission:
                check_parser.error("--admission applies only to snapshot checks")
            if args.population is not None or supplied:
                check_parser.error(
                    "--populations is a distinct batch arm; do not combine it with "
                    "a positional population or --pre/--steps/--post"
                )
            if args.format != "json":
                check_parser.error("--populations requires --format json")
            return _cmd_check_batch(args.model, args.populations, unredacted=args.unredacted)
        if supplied and args.population is not None:
            # Not a precedence question. A caller who wrote both asked two
            # questions in one command and is owed the error, not a guess.
            check_parser.error(
                "a positional population and the transition arm (--pre/--steps/--post) "
                "are different questions; supply one or the other"
            )
        plan_arm = supplied == {"--pre", "--steps"}
        if supplied and len(supplied) != len(transition_arm) and not plan_arm:
            missing = sorted(set(transition_arm) - supplied)
            check_parser.error(
                f"the transition arm needs --pre, --steps and --post; missing "
                f"{', '.join(missing)}. A partial triple is a typo, not a mode"
            )
        if not supplied and args.population is None:
            check_parser.error(
                "supply a population to check, or --pre/--steps/--post to audit a walk"
            )
        if supplied:
            if args.admission:
                check_parser.error("--admission applies only to snapshot checks")
            return _cmd_transition(
                args.model,
                args.pre,
                args.steps,
                args.post,
                args.format,
                unredacted=args.unredacted,
            )
    if args.command == "validate":
        return _cmd_validate(
            args.model,
            args.format,
            trace=args.trace,
            unredacted=args.unredacted,
        )
    if args.command == "coverage":
        return _cmd_coverage(
            args.model,
            args.experiments,
            args.check,
            args.verify,
            args.conformance,
            args.transition,
            args.format,
        )
    if args.command == "verify":
        if args.no_extraction and args.sidecar is not None:
            # A usage contradiction, not a verdict: --sidecar names a handoff
            # to validate while --no-extraction opts out of extraction
            # entirely. Routed through the parser so it exits 64 with no
            # payload, exactly like every other malformed invocation (WR-03).
            verify_parser.error(
                "--sidecar and --no-extraction are contradictory: --sidecar "
                "names an extraction handoff to validate, --no-extraction "
                "declares there was none"
            )
        return _cmd_verify(
            args.model,
            args.population,
            args.sidecar,
            args.artifacts,
            args.no_extraction,
            args.out,
            args.format,
            unredacted=args.unredacted,
        )
    if args.command == "synth":
        return _cmd_synth(
            args.model,
            args.out,
            args.synth_class,
            args.pool,
            args.seed,
            args.seeds,
            args.format,
            args.baseline_seed,
        )
    if args.command == "measure":
        return _cmd_measure(
            args.model,
            args.populations,
            args.format,
            args.out,
            args.promote,
            unredacted=args.unredacted,
        )
    if args.command == "extract":
        return _cmd_extract(args.model, args.out)
    if args.command == "export":
        if args.export_target.startswith("lean"):
            from gnd.export.lean_cli import dispatch as lean_dispatch

            return lean_dispatch(args)
        if args.export_target != "pyrel":
            from gnd.export.souffle_cli import dispatch
            return dispatch(args)
        return _cmd_export_pyrel(
            args.model, args.out, duckdb_path=args.duckdb_path, connection=args.connection
        )
    if args.command == "codegen":
        return _cmd_codegen(args.model, args.out, force=args.force)
    if args.command == "conformance":
        return _cmd_conformance(args.model, args.directory, args.format)
    if args.command == "solve":
        return _cmd_solve(args)
    if args.command == "recovery":
        if args.recovery_command == "inventory":
            return _cmd_recovery_inventory(
                args.root,
                args.sources,
                args.tests,
                args.docs,
                args.configs,
                args.schemas,
                args.exclude,
                args.max_file_bytes,
                args.max_total_bytes,
                args.max_files,
                args.out,
            )
        return _cmd_recovery_verify(
            args.root,
            args.report,
            args.model,
            args.verbalization,
        )
    if args.command == "evolve":
        if args.evolve_command == "preview":
            return _cmd_evolve_preview(
                args.model,
                args.proposal,
                args.workspace,
                args.records,
                args.out,
                args.format,
            )
        if args.evolve_command == "apply":
            return _cmd_evolve_apply(
                args.model,
                args.proposal,
                args.preview,
                args.workspace,
                args.records,
                args.format,
            )
        return _cmd_evolve_finalize(
            args.model,
            args.pending,
            args.workspace,
            args.records,
            args.format,
        )
    if args.command == "doccheck":
        return _cmd_doccheck(args.model, args.manifest, args.artifacts)
    if args.command == "fidelity":
        return _cmd_fidelity(args.model, args.cases, args.artifacts, args.out, args.format)
    if args.command == "review":
        if args.review_command in {"panel", "panel-light"}:
            # The aggregate is twice the per-stream cap, so a per-stream request
            # above half the module's hard ceiling is a malformed INVOCATION
            # (64) rather than a runtime failure after five processes have run.
            from gnd.review.runner import MAX_REVIEW_STREAM_BYTES

            if args.max_output_bytes * 2 > MAX_REVIEW_STREAM_BYTES:
                panel_parser = (
                    review_panel_parser
                    if args.review_command == "panel"
                    else review_panel_light_parser
                )
                panel_parser.error(
                    f"--max-output-bytes must be at most "
                    f"{MAX_REVIEW_STREAM_BYTES // 2}; the whole-panel aggregate "
                    f"is twice the per-stream cap and may not exceed "
                    f"{MAX_REVIEW_STREAM_BYTES} bytes"
                )
            return _cmd_review_panel(
                args.request,
                args.out,
                args.reviewer_timeout,
                args.overall_timeout,
                args.max_output_bytes,
                reviewer_effort=("xhigh" if args.review_command == "panel" else args.effort),
                command_name=f"review {args.review_command}",
            )
        return _cmd_review_finalize(args.run, args.synthesis, args.out)
    if args.command == "exp":
        from gnd.exp.spec import EXPERIMENT_DIR_PATTERN

        if args.exp_command == "init":
            if not EXPERIMENT_DIR_PATTERN.match(args.id):
                # A malformed id from argv is a USAGE error, not a verdict about
                # a document: routed through the parser so it exits 64 like every
                # other malformed invocation (WR-03).
                exp_init_parser.error(
                    f"{args.id!r} is not a legal experiment id; it must match "
                    f"{EXPERIMENT_DIR_PATTERN.pattern} — the id IS the directory "
                    f"name, so a separator or a '..' in it would be a path"
                )
            return _cmd_exp_init(
                args.id,
                args.out,
                args.kind,
                args.title or args.id,
                args.questions
                or [("Q1", "What did this experiment establish, and by what evidence?")],
                args.covers or [],
                args.session_contract,
            )
        if args.exp_command == "validate":
            return _cmd_exp_validate(args.directory)
        if args.exp_command == "author-expectation":
            return _cmd_exp_author_expectation(
                args.directory,
                args.case_id,
                args.output_id,
                args.candidate_path,
                args.source,
                args.media_type,
                args.encoding,
            )
        if args.exp_command == "run":
            return _cmd_exp_run(
                args.directory,
                args.adapter,
                args.adapter_policy,
                args.wall_seconds,
                args.test_argv or [],
            )
        return _cmd_exp_close(args.directory)
    if args.command == "doctor":
        return _cmd_doctor(claude=args.claude, codex=args.codex)
    if args.command == "uninstall":
        return _cmd_uninstall(claude=args.claude, codex=args.codex, scope=args.scope)
    if args.command == "install":
        return _cmd_install(
            claude=args.claude,
            codex=args.codex,
            scope=args.scope,
            force=args.force,
            symlink=args.symlink,
            sync=args.sync,
        )
    return _cmd_check(
        args.model,
        args.population,
        args.format,
        unredacted=args.unredacted,
        anchors_path=args.anchors,
        document_path=args.document,
        admission=args.admission,
    )
