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
from pathlib import (
    Path,
    PurePosixPath,
    PureWindowsPath,
)
from typing import Any, get_args  # noqa: F401 -- historical CLI binding

from jsonschema import Draft202012Validator  # noqa: F401 -- historical CLI binding

from gnd import api as api_module  # noqa: F401 -- historical CLI binding
from gnd import exits as exits_module
from gnd import install as install_module  # noqa: F401 -- historical CLI binding
from gnd import report as report_module  # noqa: F401 -- historical CLI binding
from gnd import (
    resolve_version,
    solve,
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
