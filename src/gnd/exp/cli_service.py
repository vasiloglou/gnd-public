from __future__ import annotations

import os
import shutil
import stat
import tempfile
from pathlib import Path
from typing import Any

from gnd.exits import EXIT_COLLISION, EXIT_EXPERIMENT_OPEN, EXIT_IO, EXIT_NO_INPUT, EXIT_USAGE
from gnd.model import ValidationIssue
from gnd.output import _print_issues

CLI_TEST_ARGV_REQUIRED_REASON = "cli:test-argv-required"

CLI_TEST_ARGV_FORBIDDEN_REASON = "cli:test-argv-forbidden"

CLI_WORK_COVERS_REQUIRED_REASON = "cli:work-covers-required"

KIND_AUTHOR_EXPECTATION_TESTS_REASON = "kind:author-expectation-tests"

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




_experiment_outcome.__module__ = "gnd.cli"
_cmd_exp_init.__module__ = "gnd.cli"
_cmd_exp_validate.__module__ = "gnd.cli"
_cmd_exp_author_expectation.__module__ = "gnd.cli"
_cmd_exp_close.__module__ = "gnd.cli"
