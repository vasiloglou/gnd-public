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

import argparse  # noqa: F401 -- historical CLI binding
import asyncio  # noqa: F401 -- historical CLI binding
import hashlib  # noqa: F401 -- historical CLI binding
import json  # noqa: F401 -- historical CLI binding
import math  # noqa: F401 -- historical CLI binding
import os  # noqa: F401 -- historical CLI binding
import re  # noqa: F401 -- historical CLI binding
import shutil  # noqa: F401 -- historical CLI binding
import stat  # noqa: F401 -- historical CLI binding
import sys  # noqa: F401 -- historical CLI binding
import tempfile  # noqa: F401 -- historical CLI binding
from pathlib import Path, PurePosixPath, PureWindowsPath  # noqa: F401 -- historical CLI binding
from typing import Any, get_args  # noqa: F401 -- historical CLI binding

from jsonschema import Draft202012Validator  # noqa: F401 -- historical CLI binding

from gnd import api as api_module  # noqa: F401 -- historical CLI binding
from gnd import exits as exits_module  # noqa: F401 -- historical CLI binding
from gnd import install as install_module  # noqa: F401 -- historical CLI binding
from gnd import report as report_module  # noqa: F401 -- historical CLI binding
from gnd import (
    resolve_version,
    solve,  # noqa: F401 -- historical CLI binding
    transition,  # noqa: F401 -- historical CLI binding
    verbalize,  # noqa: F401 -- historical CLI binding
)
from gnd.checker import (
    CheckReport,  # noqa: F401 -- historical CLI binding
    check,  # noqa: F401 -- historical CLI binding
    check_with_anchors,  # noqa: F401 -- historical CLI binding
)
from gnd.checker import band as checker_band  # noqa: F401 -- historical CLI binding
from gnd.codegen.service import (
    _cmd_codegen as _cmd_codegen,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.codegen.service import (
    _stale_smoke_modules as _stale_smoke_modules,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands import checking as _group_checking
from gnd.commands import codegen as _group_codegen
from gnd.commands import conformance as _group_conformance
from gnd.commands import doccheck as _group_doccheck
from gnd.commands import evolve as _group_evolve
from gnd.commands import exp as _group_exp
from gnd.commands import export as _group_export
from gnd.commands import extract as _group_extract
from gnd.commands import fidelity as _group_fidelity
from gnd.commands import judgments as _group_judgments
from gnd.commands import lifecycle as _group_lifecycle
from gnd.commands import measure as _group_measure
from gnd.commands import recovery as _group_recovery
from gnd.commands import review as _group_review
from gnd.commands import solve as _group_solve
from gnd.commands import synth as _group_synth
from gnd.commands import verify as _group_verify
from gnd.commands import witness as _group_witness
from gnd.commands._arguments import (
    OUTPUT_FORMATS as OUTPUT_FORMATS,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands._arguments import (
    _add_format_argument as _add_format_argument,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands._arguments import (
    _add_unredacted_argument as _add_unredacted_argument,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands._arguments import (
    _BandSafeParser as _BandSafeParser,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands._arguments import (
    _positive_finite_float as _positive_finite_float,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands._arguments import (
    _positive_int as _positive_int,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands._arguments import (
    _StoreOnce as _StoreOnce,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands._output import _band as _band  # noqa: PLC0414 -- historical CLI binding
from gnd.commands._output import (
    _canonical_payload as _canonical_payload,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands._output import (
    _constraint_verdict_line as _constraint_verdict_line,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands._output import (
    _derivation_verdict_lines as _derivation_verdict_lines,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands._output import (
    _live_assurance as _live_assurance,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands._output import (
    _print_admission_text as _print_admission_text,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands._output import (
    _print_check_verdicts as _print_check_verdicts,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands._output import (
    _print_derived_change_summaries as _print_derived_change_summaries,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands._output import (
    _print_issues as _print_issues,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands._output import (
    _print_projected_text as _print_projected_text,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands._output import (
    _print_report as _print_report,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands._output import (
    _print_trace as _print_trace,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands._output import (
    _print_transition as _print_transition,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.checking import (
    _DEFAULT_CHECK as _DEFAULT_CHECK,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.checking import (
    _cmd_check as _cmd_check,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.checking import (
    _cmd_check_batch as _cmd_check_batch,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.checking import (
    _cmd_coverage as _cmd_coverage,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.checking import _cmd_diff as _cmd_diff  # noqa: PLC0414 -- historical CLI binding
from gnd.commands.checking import (
    _cmd_rai_import as _cmd_rai_import,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.checking import (
    _cmd_transition as _cmd_transition,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.checking import (
    _cmd_validate as _cmd_validate,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.checking import (
    _cmd_verbalize_population as _cmd_verbalize_population,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.exp import _cmd_exp_run as _cmd_exp_run  # noqa: PLC0414 -- historical CLI binding
from gnd.commands.exp import (
    _next_session_run_root as _next_session_run_root,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.exp import (
    _parse_covers as _parse_covers,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.exp import (
    _parse_question as _parse_question,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.exp import (
    _run_tests_mode_bridge as _run_tests_mode_bridge,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.exp import (
    _session_result_exit as _session_result_exit,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.export import (
    _cmd_export_pyrel as _cmd_export_pyrel,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.lifecycle import (
    _add_target_arguments as _add_target_arguments,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.lifecycle import (
    _cmd_doctor as _cmd_doctor,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.lifecycle import (
    _cmd_install as _cmd_install,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.lifecycle import (
    _cmd_uninstall as _cmd_uninstall,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.lifecycle import (
    _doctor_outcome as _doctor_outcome,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.lifecycle import (
    _install_outcome as _install_outcome,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.lifecycle import (
    _render_diagnosis as _render_diagnosis,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.lifecycle import (
    _render_states as _render_states,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.lifecycle import (
    _render_target_result as _render_target_result,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.lifecycle import (
    _uninstall_outcome as _uninstall_outcome,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.review import (
    _add_review_panel_arguments as _add_review_panel_arguments,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.commands.solve import _cmd_solve as _cmd_solve  # noqa: PLC0414 -- historical CLI binding
from gnd.commands.solve import _utf8_clean as _utf8_clean  # noqa: PLC0414 -- historical CLI binding
from gnd.conformance.cli_service import (
    _cmd_conformance as _cmd_conformance,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.evolve.cli_service import (
    _EVOLUTION_CLAIM_MAX_BYTES as _EVOLUTION_CLAIM_MAX_BYTES,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.evolve.cli_service import (
    _cmd_evolve_apply as _cmd_evolve_apply,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.evolve.cli_service import (
    _cmd_evolve_finalize as _cmd_evolve_finalize,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.evolve.cli_service import (
    _cmd_evolve_preview as _cmd_evolve_preview,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.evolve.cli_service import (
    _EvolutionCLIError as _EvolutionCLIError,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.evolve.cli_service import (
    _evolve_absolute_path as _evolve_absolute_path,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.evolve.cli_service import (
    _evolve_emit_claim as _evolve_emit_claim,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.evolve.cli_service import (
    _evolve_error_exit as _evolve_error_exit,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.evolve.cli_service import (
    _evolve_fail as _evolve_fail,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.evolve.cli_service import (
    _evolve_finish_apply as _evolve_finish_apply,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.evolve.cli_service import (
    _evolve_json_bytes as _evolve_json_bytes,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.evolve.cli_service import (
    _evolve_publish_preview as _evolve_publish_preview,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.evolve.cli_service import (
    _evolve_read_claim as _evolve_read_claim,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.evolve.cli_service import (
    _evolve_records_root as _evolve_records_root,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.evolve.cli_service import (
    _evolve_reject_existing_symlinks as _evolve_reject_existing_symlinks,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.evolve.cli_service import (
    _evolve_reject_unsafe_spelling as _evolve_reject_unsafe_spelling,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.evolve.cli_service import (
    _evolve_rooted_path as _evolve_rooted_path,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.evolve.cli_service import (
    _evolve_same_review_identity as _evolve_same_review_identity,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.evolve.cli_service import (
    _evolve_service_exit as _evolve_service_exit,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.evolve.cli_service import (
    _evolve_validate_proposal_roots as _evolve_validate_proposal_roots,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.evolve.cli_service import (
    _evolve_workspace as _evolve_workspace,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.evolve.cli_service import (
    _evolve_workspace_path as _evolve_workspace_path,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.exits import (
    EXIT_CHECKER_DEFECT,  # noqa: F401 -- historical CLI binding
    EXIT_COLLISION,  # noqa: F401 -- historical CLI binding
    EXIT_DRIFT,  # noqa: F401 -- historical CLI binding
    EXIT_EVOLUTION_OPERATIONS_GATED,  # noqa: F401 -- historical CLI binding
    EXIT_EXPERIMENT_OPEN,  # noqa: F401 -- historical CLI binding
    EXIT_GENERATOR,  # noqa: F401 -- historical CLI binding
    EXIT_INTERNAL,  # noqa: F401 -- historical CLI binding
    EXIT_IO,  # noqa: F401 -- historical CLI binding
    EXIT_MODEL_CODE_DRIFT,  # noqa: F401 -- historical CLI binding
    EXIT_NO_INPUT,  # noqa: F401 -- historical CLI binding
    EXIT_NO_INSTALL,  # noqa: F401 -- historical CLI binding
    EXIT_QUARANTINE,  # noqa: F401 -- historical CLI binding
    EXIT_REVIEW_INCONCLUSIVE,  # noqa: F401 -- historical CLI binding
    EXIT_SESSION_NOT_ACCEPTED,  # noqa: F401 -- historical CLI binding
    EXIT_USAGE,  # noqa: F401 -- historical CLI binding
    EXIT_WALK_HALTED,  # noqa: F401 -- historical CLI binding
)

# EXIT_USAGE (64), EXIT_NO_INPUT (66) and EXIT_INTERNAL (70) are imported from
# gnd.exits at the top of this module: gnd/solve.py needs the same bands, and
# because cli imports solve the reverse import is circular. Their justification
# prose moved with them. See gnd/exits.py.
# Exit allocations and their rationale live in gnd.exits.
#: Rendering formats. An invalid choice routes through _BandSafeParser.error()
#: to exit 64, which emits no payload — see the module docstring.
#: The case-directory convention `gnd fidelity` consumes (produced by the
#: gnd-render-doc / gnd-extract skills). Every file is REQUIRED for a case to
#: run; `extraction.skipped.json` is the one intentional opt-out marker.
#: The fixed reviewer roster size. Pinned to ``gnd.review.adapters.REVIEWER_IDS``
#: by a test rather than derived here, because deriving it would require
#: importing the review stack at CLI import time for a number that must not move
#: silently anyway.
#: Python-owned, never argv-supplied: the grace a reviewer's process group gets
#: between SIGTERM and SIGKILL. A user-tunable grace is a way to make cleanup
#: unprovable, and cleanup provenance is what the failure envelopes assert.
from gnd.exp.cli_service import (
    CLI_TEST_ARGV_FORBIDDEN_REASON as CLI_TEST_ARGV_FORBIDDEN_REASON,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.exp.cli_service import (
    CLI_TEST_ARGV_REQUIRED_REASON as CLI_TEST_ARGV_REQUIRED_REASON,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.exp.cli_service import (
    CLI_WORK_COVERS_REQUIRED_REASON as CLI_WORK_COVERS_REQUIRED_REASON,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.exp.cli_service import (
    KIND_AUTHOR_EXPECTATION_TESTS_REASON as KIND_AUTHOR_EXPECTATION_TESTS_REASON,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.exp.cli_service import (
    _cmd_exp_author_expectation as _cmd_exp_author_expectation,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.exp.cli_service import (
    _cmd_exp_close as _cmd_exp_close,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.exp.cli_service import (
    _cmd_exp_init as _cmd_exp_init,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.exp.cli_service import (
    _cmd_exp_validate as _cmd_exp_validate,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.exp.cli_service import (
    _experiment_outcome as _experiment_outcome,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.export.verification_service import (
    _cmd_verify as _cmd_verify,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.extract.service import (
    _artifact_index_issue as _artifact_index_issue,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.extract.service import (
    _cmd_extract as _cmd_extract,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.extract.service import (
    _extract_stem as _extract_stem,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.extract.service import (
    _extraction_header_template as _extraction_header_template,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.fidelity.doccheck_service import (
    _cmd_doccheck as _cmd_doccheck,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.fidelity.service import (
    _CASE_DOCUMENT as _CASE_DOCUMENT,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.fidelity.service import (
    _CASE_EXTRACTED as _CASE_EXTRACTED,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.fidelity.service import (
    _CASE_MANIFEST as _CASE_MANIFEST,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.fidelity.service import (
    _CASE_SIDECAR as _CASE_SIDECAR,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.fidelity.service import (
    _CASE_SKIPPED as _CASE_SKIPPED,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.fidelity.service import (
    _CASE_SOURCE as _CASE_SOURCE,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.fidelity.service import (
    _cmd_fidelity as _cmd_fidelity,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.measure.service import (
    _cmd_measure as _cmd_measure,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.measure.service import (
    _promote_defects as _promote_defects,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.model import (
    Model,  # noqa: F401 -- historical CLI binding
    ModelValidationError,  # noqa: F401 -- historical CLI binding
    ValidationIssue,  # noqa: F401 -- historical CLI binding
    derivation_classifications,  # noqa: F401 -- historical CLI binding
    load_model,  # noqa: F401 -- historical CLI binding
    structured_derivation_ids,  # noqa: F401 -- historical CLI binding
)
from gnd.population import (
    PopulationValidationError,  # noqa: F401 -- historical CLI binding
    load_population,  # noqa: F401 -- historical CLI binding
)
from gnd.recovery.service import (
    _RECOVERY_DIRECTORY_NAME_OBSERVATION_CAP as _RECOVERY_DIRECTORY_NAME_OBSERVATION_CAP,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.recovery.service import (
    _cmd_recovery_inventory as _cmd_recovery_inventory,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.recovery.service import (
    _cmd_recovery_verify as _cmd_recovery_verify,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.recovery.service import (
    _parse_recovery_exclusion as _parse_recovery_exclusion,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.recovery.service import (
    _recovery_canonical_directory_parts as _recovery_canonical_directory_parts,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.recovery.service import (
    _recovery_cause_is as _recovery_cause_is,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.recovery.service import (
    _recovery_json as _recovery_json,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.recovery.service import (
    _recovery_open_output_parent as _recovery_open_output_parent,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.recovery.service import (
    _recovery_publish_absent as _recovery_publish_absent,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.recovery.service import (
    _recovery_relative_argv as _recovery_relative_argv,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.recovery.service import (
    _recovery_require_absent_output as _recovery_require_absent_output,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.recovery.service import (
    _recovery_require_existing_exclusion as _recovery_require_existing_exclusion,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.recovery.service import (
    _recovery_required_canonical_leaf as _recovery_required_canonical_leaf,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.recovery.service import (
    _recovery_root as _recovery_root,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.recovery.service import (
    _recovery_root_still_bound as _recovery_root_still_bound,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.recovery.service import (
    _RecoveryCLIError as _RecoveryCLIError,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.review.constants import REVIEW_QUORUM  # noqa: F401 -- historical CLI binding
from gnd.review.service import (
    REVIEW_ATTEMPTED_REVIEWERS as REVIEW_ATTEMPTED_REVIEWERS,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.review.service import (
    REVIEW_TERMINATE_GRACE_SECONDS as REVIEW_TERMINATE_GRACE_SECONDS,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.review.service import (
    _cmd_review_finalize as _cmd_review_finalize,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.review.service import (
    _cmd_review_panel as _cmd_review_panel,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.review.service import (
    _repository_relative_path as _repository_relative_path,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.review.service import (
    _review_outcome as _review_outcome,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.semantic_registry import capture_branches  # noqa: F401 -- historical CLI binding
from gnd.synth.corpus_service import (
    _INDEX_SCHEMA as _INDEX_SCHEMA,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.synth.corpus_service import (
    _INDEX_VALIDATOR as _INDEX_VALIDATOR,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.synth.corpus_service import (
    CorpusPathError as CorpusPathError,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.synth.corpus_service import (
    IndexValidationError as IndexValidationError,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.synth.corpus_service import (
    _corpus_relative as _corpus_relative,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.synth.corpus_service import (
    _merge_index as _merge_index,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.synth.corpus_service import (
    _resolve_corpus_path as _resolve_corpus_path,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.synth.corpus_service import (
    _resolve_unique_index_entries as _resolve_unique_index_entries,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.synth.corpus_service import (
    _SynthCorpusTransaction as _SynthCorpusTransaction,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.synth.corpus_service import (
    _validate_existing_synth_index as _validate_existing_synth_index,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.synth.corpus_service import (
    _validate_index_document as _validate_index_document,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.synth.service import (
    _bind_synth_not_derivable as _bind_synth_not_derivable,  # noqa: PLC0414 -- historical CLI binding
)
from gnd.synth.service import _cmd_synth as _cmd_synth  # noqa: PLC0414 -- historical CLI binding
from gnd.synth.service import (
    _emit_boundary_corpus as _emit_boundary_corpus,  # noqa: PLC0414 -- historical CLI binding
)


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

    _group_witness.add_parsers(subparsers, command='witness')
    _group_checking.add_parsers(subparsers, command='import')
    _group_checking.add_parsers(subparsers, command='validate')
    _group_checking.add_parsers(subparsers, command='diff')
    _group_checking.add_parsers(subparsers, command='coverage')
    _group_checking.add_parsers(subparsers, command='check')
    _group_checking.add_parsers(subparsers, command='verbalize')
    _group_verify.add_parsers(subparsers, command='verify')
    _group_synth.add_parsers(subparsers, command='synth')
    _group_measure.add_parsers(subparsers, command='measure')
    _group_extract.add_parsers(subparsers, command='extract')
    _group_export.add_parsers(subparsers, command='export')
    _group_codegen.add_parsers(subparsers, command='codegen')
    _group_conformance.add_parsers(subparsers, command='conformance')
    _group_recovery.add_parsers(subparsers, command='recovery')
    _group_evolve.add_parsers(subparsers, command='evolve')
    _group_doccheck.add_parsers(subparsers, command='doccheck')
    _group_fidelity.add_parsers(subparsers, command='fidelity')
    _group_review.add_parsers(subparsers, command='review')
    _group_exp.add_parsers(subparsers, command='exp')
    _group_solve.add_parsers(subparsers, command='solve')
    _group_lifecycle.add_parsers(subparsers, command='install')
    _group_lifecycle.add_parsers(subparsers, command='doctor')
    _group_lifecycle.add_parsers(subparsers, command='uninstall')
    _group_judgments.add_parsers(subparsers, command='judgments')

    args = parser.parse_args(argv)
    return args.handler(args)
