from __future__ import annotations

import argparse
import json
from typing import Any


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
