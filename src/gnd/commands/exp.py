from __future__ import annotations

import argparse
import json
from typing import Any

from gnd import input_policy as _rf7_input


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
        document = _rf7_input.loads(value)
        return CoversEntry.model_validate(document)
    except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError(
            f"expected a closed JSON covers entry with exactly one of operation, "
            f"constraint, fact_type, or derivation: {error}"
        ) from error

_parse_question.__module__ = "gnd.cli"
_parse_covers.__module__ = "gnd.cli"

import asyncio
import hashlib
import stat
from pathlib import Path

from gnd.commands._output import _print_issues
from gnd.exits import EXIT_INTERNAL, EXIT_IO, EXIT_NO_INPUT, EXIT_SESSION_NOT_ACCEPTED, EXIT_USAGE
from gnd.exp.cli_service import CLI_TEST_ARGV_FORBIDDEN_REASON, CLI_TEST_ARGV_REQUIRED_REASON


def _session_result_exit(result: Any) -> int:
    from gnd.exp.session_store import SessionOutcome

    return 0 if result.disposition is SessionOutcome.accepted else EXIT_SESSION_NOT_ACCEPTED


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

_cmd_exp_run.__module__ = "gnd.cli"
_next_session_run_root.__module__ = "gnd.cli"
_run_tests_mode_bridge.__module__ = "gnd.cli"
_session_result_exit.__module__ = "gnd.cli"

from typing import get_args

import gnd.exp.cli_service as _handler_exp_cli_service
from gnd.commands._arguments import _positive_finite_float


def _register_exp(subparsers):
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


    return {'exp_author_expectation_parser': exp_author_expectation_parser, 'exp_close_parser': exp_close_parser, 'exp_init_parser': exp_init_parser, 'exp_parser': exp_parser, 'exp_run_parser': exp_run_parser, 'exp_validate_parser': exp_validate_parser}


def add_parsers(subparsers, *, command: str | None = None):
    parsers = {}
    if command is None or command == 'exp':
        selected = _register_exp(subparsers)
        parsers.update(selected)
        selected['exp_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if not parsers:
        raise ValueError(f"unsupported command: {command}")
    return parsers


def handle(args, parsers) -> int:
    exp_init_parser = parsers.get('exp_init_parser')
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
            return _handler_exp_cli_service._cmd_exp_init(
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
            return _handler_exp_cli_service._cmd_exp_validate(args.directory)
        if args.exp_command == "author-expectation":
            return _handler_exp_cli_service._cmd_exp_author_expectation(
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
        return _handler_exp_cli_service._cmd_exp_close(args.directory)

    raise ValueError(f"unsupported command: {args.command}")

