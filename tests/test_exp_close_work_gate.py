








































from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable, Sequence
from pathlib import Path

import pytest

from gnd import cli
from gnd.cli import main
from gnd.exp.close import (
    SESSION_RESULT_FILENAME,
    SESSION_RUNS_DIRNAME,
    _accepted_disposition,
    evaluate_close,
)
from gnd.exp.conclusions import read_conclusions
from gnd.exp.frontmatter import render_frontmatter
from gnd.exp.session_store import SessionOutcome, SessionResult
from gnd.exp.spec import read_spec
from gnd.exp.tests_runner import TestsAcceptanceFeedback as AcceptanceFeedback
from gnd.exp.tests_runner import _result_document

EXPERIMENT_ID = "EXP-001-work"







def _experiment(
    parent: Path,
    *,
    kind: str = "work",
    outcome: str = "answered",
    experiment_id: str = EXPERIMENT_ID,
    cases: tuple[str, ...] = ("gate",),
) -> Path:







    root = parent / experiment_id
    (root / "results").mkdir(parents=True)
    (root / "results" / "run.json").write_text("{}\n", encoding="utf-8")

    (root / "SPEC.md").write_text(
        render_frontmatter(
            {
                "id": experiment_id,
                "kind": kind,
                "title": "does the slice this experiment declared actually land",
                "questions": [{"id": "Q1", "text": "did the declared tests pass?"}],
                "follows": [],
            },
            f"# {experiment_id}\n",
        ),
        encoding="utf-8",
    )

    resolution = {"id": "Q1", "outcome": outcome, "evidence": "results/run.json"}
    if outcome != "answered":
        resolution["reason"] = "the run was stopped before this case, so nothing was measured"
    (root / "CONCLUSIONS.md").write_text(
        render_frontmatter(
            {"id": experiment_id, "resolves": [resolution]},
            f"# {experiment_id} conclusions\n",
        ),
        encoding="utf-8",
    )
    _write_contract(root, cases)
    return root


def _write_contract(root: Path, cases: tuple[str, ...] = ("gate",)) -> None:








    (root / "session.contract.json").write_text(
        json.dumps(
            {
                "schema_version": 3,
                "experiment_id": root.name,
                "max_attempts": 1,
                "cases": [
                    {
                        "case_id": case_id,
                        "role": "required",
                        "acceptance": {
                            "mode": "tests",
                            "required_tests": ["test_gate.py::test_pass"],
                            "protected": [],
                            "results_path": "results/results.xml",
                            "test_argv_sha256": "a" * 64,
                        },
                    }
                    for case_id in cases
                ],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def _tests_result(
    run_root: Path, *, disposition: str, launch_sha256: str = "a" * 64
) -> bytes:






    feedback = [
        (
            "gate",
            "required",
            AcceptanceFeedback(
                required=("test_gate.py::test_pass",),
                present=("test_gate.py::test_pass",),
                passing=("test_gate.py::test_pass",) if disposition == "accepted" else (),
                reason=None,
            ),
        )
    ]
    return _result_document(
        run_root,
        disposition=disposition,
        reason=None if disposition == "accepted" else "tests:required-not-passing",
        feedback=feedback,
        launch_sha256=launch_sha256,
    )


def _session_result(run_root: Path, *, disposition: SessionOutcome) -> bytes:

    accepted = disposition is SessionOutcome.accepted
    result = SessionResult.model_validate(
        {
            "schema_version": 2,
            "run_id": run_root.name,
            "disposition": disposition.value,
            "terminal_reason": "every required case met its declared acceptance mode"
            if accepted
            else "one or more required cases did not accept",
            "attempt_count": 1,
            "best_attempt": 1 if accepted else None,
            "best_attempt_manifest_sha256": "b" * 64 if accepted else None,
            "best_candidate_sha256": "c" * 64 if accepted else None,
            "referenced_evidence_digests": {"attempt_manifest_sha256": "b" * 64},
            "acceptance_modes": ["exact-bytes"],
        }
    )
    return json.dumps(result.model_dump(mode="json"), sort_keys=True).encode("utf-8")


def _run(
    root: Path,
    index: int,
    payload: bytes | Callable[[Path, str], bytes] | None,
    *,
    launched: bool = True,
) -> Path:











    run_root = root / SESSION_RUNS_DIRNAME / f"run-{index:04d}"
    run_root.mkdir(parents=True)
    digest = "a" * 64
    if launched:
        launches = run_root / "launches"
        launches.mkdir()
        record = json.dumps(
            {"run_id": run_root.name, "schema_version": 1}, sort_keys=True
        ).encode("utf-8")
        (launches / "0001.json").write_bytes(record)
        digest = hashlib.sha256(record).hexdigest()
    if payload is not None:
        resolved = payload(run_root, digest) if callable(payload) else payload
        (run_root / SESSION_RESULT_FILENAME).write_bytes(resolved)
    return run_root


def _accepted_run(root: Path, index: int = 1) -> Path:
    return _run(
        root,
        index,
        lambda run_root, digest: _tests_result(
            run_root, disposition="accepted", launch_sha256=digest
        ),
    )


def _refused_run(root: Path, index: int = 1) -> Path:
    return _run(
        root,
        index,
        lambda run_root, digest: _tests_result(
            run_root, disposition="not-accepted", launch_sha256=digest
        ),
    )


def _close(root: Path) -> Sequence:
    spec_path = root / "SPEC.md"
    return evaluate_close(
        read_spec(spec_path), read_conclusions(root / "CONCLUSIONS.md"), spec_path
    ).findings


def _kinds(findings: Sequence) -> set[str]:
    return {finding.kind for finding in findings}







def test_the_pair_differs_in_the_disposition_scalar_alone(tmp_path: Path) -> None:






    run_root = tmp_path / SESSION_RUNS_DIRNAME / "run-0001"
    accepting = json.loads(_tests_result(run_root, disposition="accepted"))
    refusing = json.loads(_tests_result(run_root, disposition="not-accepted"))

    differing = {
        key for key in accepting.keys() | refusing.keys()
        if accepting.get(key) != refusing.get(key)
    }
    
    
    assert differing == {"disposition", "reason", "feedback"}


def test_a_work_experiment_whose_latest_launch_accepted_closes_at_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _experiment(tmp_path)
    _accepted_run(root)

    capsys.readouterr()
    assert main(["exp", "close", str(root)]) == 0
    assert "CLOSED" in capsys.readouterr().out


def test_a_work_experiment_whose_latest_launch_did_not_accept_is_refused_at_fourteen(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _experiment(tmp_path)
    _refused_run(root)

    capsys.readouterr()
    assert main(["exp", "close", str(root)]) == cli.EXIT_EXPERIMENT_OPEN
    printed = capsys.readouterr().out

    assert "unaccepted-session" in printed
    assert "run-0001" in printed, (
        "the refusal does not name the run the author has to inspect or re-run; "
        "'one obligation is undischarged' is not something anyone can act on"
    )
    assert "not-accepted" in printed







def test_a_work_experiment_that_never_launched_cannot_close(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:

    root = _experiment(tmp_path)

    capsys.readouterr()
    assert main(["exp", "close", str(root)]) == cli.EXIT_EXPERIMENT_OPEN
    printed = capsys.readouterr().out

    assert "unrecorded-launch" in printed
    assert SESSION_RUNS_DIRNAME in printed
    assert "gnd exp run" in printed, (
        "the refusal must name the command that discharges it"
    )


def test_a_runs_directory_with_no_terminal_result_is_not_a_recorded_launch(
    tmp_path: Path,
) -> None:






    root = _experiment(tmp_path)
    _run(root, 1, None)

    findings = _close(root)
    assert "unrecorded-launch" in _kinds(findings)


def test_an_empty_runs_directory_is_not_a_recorded_launch(tmp_path: Path) -> None:
    root = _experiment(tmp_path)
    (root / SESSION_RUNS_DIRNAME).mkdir()

    assert "unrecorded-launch" in _kinds(_close(root))







def test_an_earlier_acceptance_cannot_speak_for_a_later_refusal(
    tmp_path: Path,
) -> None:








    root = _experiment(tmp_path)
    _accepted_run(root, 1)
    _refused_run(root, 2)

    findings = _close(root)
    assert _kinds(findings) == {"unaccepted-session"}
    assert [finding.id for finding in findings] == ["run-0002"]


def test_an_earlier_refusal_does_not_block_a_later_acceptance(tmp_path: Path) -> None:

    root = _experiment(tmp_path)
    _refused_run(root, 1)
    _accepted_run(root, 2)

    assert _close(root) == []


def test_the_latest_run_is_chosen_numerically_not_lexicographically(
    tmp_path: Path,
) -> None:






    root = _experiment(tmp_path)
    _accepted_run(root, 9999)
    _refused_run(root, 10000)

    findings = _close(root)
    assert [finding.id for finding in findings] == ["run-10000"]


def test_a_latest_run_without_a_terminal_result_is_not_an_acceptance(
    tmp_path: Path,
) -> None:

    root = _experiment(tmp_path)
    _accepted_run(root, 1)
    _run(root, 2, None)

    findings = _close(root)
    assert _kinds(findings) == {"unaccepted-session"}
    assert [finding.id for finding in findings] == ["run-0002"]


def test_an_accepted_result_copied_out_of_an_earlier_run_does_not_close_a_later_one(
    tmp_path: Path,
) -> None:













    root = _experiment(tmp_path)
    first = _accepted_run(root, 1)
    
    
    
    second = _run(root, 2, (first / SESSION_RESULT_FILENAME).read_bytes())
    assert (second / "launches" / "0001.json").is_file()

    findings = _close(root)
    assert _kinds(findings) == {"unaccepted-session"}
    assert [finding.id for finding in findings] == ["run-0002"]
    assert "run-0001" in findings[0].message, (
        "the refusal must name the run the result actually belongs to"
    )


def test_the_run_name_to_index_map_is_injective(tmp_path: Path) -> None:










    from gnd.exp.close import SESSION_RUN_PATTERN

    for index in (1, 2, 9999, 10000, 123456):
        assert SESSION_RUN_PATTERN.match(f"run-{index:04d}"), index

    seen: dict[int, str] = {}
    for name in (f"run-{i:04d}" for i in range(1, 200)):
        index = int(name.removeprefix("run-"))
        assert index not in seen, (name, seen.get(index))
        seen[index] = name

    for ambiguous in ("run-00001", "run-000001", "run-001"):
        assert not SESSION_RUN_PATTERN.match(ambiguous), ambiguous


def test_a_name_the_runner_cannot_mint_is_reported_rather_than_skipped(
    tmp_path: Path,
) -> None:









    root = _experiment(tmp_path)
    _accepted_run(root, 1)
    shadow = root / SESSION_RUNS_DIRNAME / "run-00001"
    shadow.mkdir(parents=True)
    (shadow / SESSION_RESULT_FILENAME).write_bytes(
        _tests_result(shadow, disposition="not-accepted")
    )

    findings = _close(root)
    assert [finding.id for finding in findings] == ["run-00001"]
    assert "mints" in findings[0].message


def test_an_object_standing_where_a_later_run_belongs_is_reported_not_skipped(
    tmp_path: Path,
) -> None:








    for shape in ("symlink", "file"):
        root = _experiment(tmp_path / shape)
        _accepted_run(root, 1)
        intruder = root / SESSION_RUNS_DIRNAME / "run-0002"
        if shape == "symlink":
            intruder.symlink_to(tmp_path / "nowhere", target_is_directory=True)
        else:
            intruder.write_text("not a run\n", encoding="utf-8")

        findings = _close(root)
        assert [finding.id for finding in findings] == ["run-0002"], shape
        assert "not a real directory" in findings[0].message, shape


@pytest.mark.parametrize("index", [0, 1_000_000])
def test_an_index_outside_the_allocator_range_is_not_evidence_of_a_launch(
    tmp_path: Path, index: int
) -> None:








    root = _experiment(tmp_path)
    stray = root / SESSION_RUNS_DIRNAME / f"run-{index:04d}"
    stray.mkdir(parents=True)
    (stray / SESSION_RESULT_FILENAME).write_bytes(
        _tests_result(stray, disposition="accepted")
    )

    findings = _close(root)
    kinds = _kinds(findings)
    assert "unaccepted-session" in kinds
    assert "unrecorded-launch" in kinds, (
        "an out-of-range directory must not discharge the launch obligation"
    )
    assert any("allocator's range" in finding.message for finding in findings)


def test_a_result_without_the_launch_record_it_describes_is_not_a_launch(
    tmp_path: Path,
) -> None:








    root = _experiment(tmp_path)
    run_root = root / SESSION_RUNS_DIRNAME / "run-0001"
    _run(root, 1, _tests_result(run_root, disposition="accepted"), launched=False)

    findings = _close(root)
    assert _kinds(findings) == {"unrecorded-launch", "unaccepted-session"}
    assert any("launches/" in finding.message for finding in findings)


def test_an_accepted_result_the_runner_could_not_have_written_is_refused(
    tmp_path: Path,
) -> None:








    root = _experiment(tmp_path)
    impossible = json.dumps(
        {
            "schema_version": 1,
            "run_id": "run-0001",
            "acceptance_modes": ["tests"],
            "disposition": "accepted",
            "reason": "tests:required-not-passing",
            "launch_sha256": None,
            "feedback": [],
        },
        sort_keys=True,
    ).encode("utf-8")
    _run(root, 1, impossible)

    findings = _close(root)
    assert _kinds(findings) == {"unaccepted-session"}
    assert "does not open this gate" in findings[0].message


@pytest.mark.parametrize(
    ("flaw", "mutate"),
    [
        ("no launch digest", lambda d: {**d, "launch_sha256": None}),
        (
            "refusal reason",
            lambda d: {**d, "reason": "tests:required-not-passing"},
        ),
        ("no feedback", lambda d: {**d, "feedback": []}),
        (
            "required test not passing",
            lambda d: {
                **d,
                "feedback": [{**d["feedback"][0], "passing": []}],
            },
        ),
    ],
)
def test_each_acceptance_consistency_rule_has_its_own_failing_document(
    tmp_path: Path, flaw: str, mutate
) -> None:







    from gnd.exp.tests_runner import TestsSessionResult

    run_root = tmp_path / SESSION_RUNS_DIRNAME / "run-0001"
    genuine = json.loads(_tests_result(run_root, disposition="accepted"))
    TestsSessionResult.model_validate(genuine)  

    with pytest.raises(ValueError):
        TestsSessionResult.model_validate(mutate(genuine))


def test_a_failing_diagnostic_row_does_not_block_an_accepted_result(
    tmp_path: Path,
) -> None:








    from gnd.exp.tests_runner import TestsSessionResult

    run_root = tmp_path / SESSION_RUNS_DIRNAME / "run-0001"
    document = _result_document(
        run_root,
        disposition="accepted",
        reason=None,
        feedback=[
            (
                "gate",
                "required",
                AcceptanceFeedback(
                    required=("test_gate.py::test_pass",),
                    present=("test_gate.py::test_pass",),
                    passing=("test_gate.py::test_pass",),
                    reason=None,
                ),
            ),
            (
                "probe",
                "diagnostic",
                AcceptanceFeedback(
                    required=("test_gate.py::test_probe",),
                    present=(),
                    passing=(),
                    reason=None,
                ),
            ),
        ],
        launch_sha256="a" * 64,
    )

    assert TestsSessionResult.model_validate_json(document).disposition == "accepted"


@pytest.mark.parametrize("shape", ["empty", "non-json", "symlinked-dir", "symlinked-file"])
def test_a_launch_directory_without_a_real_record_is_not_a_launch(
    tmp_path: Path, shape: str
) -> None:





    import shutil

    root = _experiment(tmp_path / shape)
    run_root = root / SESSION_RUNS_DIRNAME / "run-0001"
    _run(root, 1, _tests_result(run_root, disposition="accepted"))
    launches = run_root / "launches"
    for entry in launches.iterdir():
        entry.unlink()

    if shape == "non-json":
        (launches / "0001.txt").write_text("{}", encoding="utf-8")
    elif shape == "symlinked-dir":
        elsewhere = tmp_path / f"{shape}-elsewhere"
        elsewhere.mkdir()
        (elsewhere / "0001.json").write_text("{}", encoding="utf-8")
        shutil.rmtree(launches)
        launches.symlink_to(elsewhere, target_is_directory=True)
    elif shape == "symlinked-file":
        real = tmp_path / f"{shape}-real.json"
        real.write_text("{}", encoding="utf-8")
        (launches / "0001.json").symlink_to(real)

    assert "unrecorded-launch" in _kinds(_close(root)), shape


def test_an_arbitrary_json_file_is_not_a_launch_record(tmp_path: Path) -> None:








    root = _experiment(tmp_path)
    run_root = root / SESSION_RUNS_DIRNAME / "run-0001"
    _run(root, 1, None, launched=False)
    (run_root / "launches").mkdir()
    (run_root / "launches" / "forged.json").write_text("{}", encoding="utf-8")
    (run_root / SESSION_RESULT_FILENAME).write_bytes(
        _tests_result(run_root, disposition="accepted")
    )

    assert "unrecorded-launch" in _kinds(_close(root))


def test_a_result_naming_a_launch_record_this_run_does_not_hold_is_refused(
    tmp_path: Path,
) -> None:







    root = _experiment(tmp_path)
    _run(
        root,
        1,
        lambda run_root, _digest: _tests_result(
            run_root, disposition="accepted", launch_sha256="f" * 64
        ),
    )

    findings = _close(root)
    assert _kinds(findings) == {"unaccepted-session"}
    assert "does not hold" in findings[0].message


def test_an_accepted_result_missing_a_declared_case_is_refused(
    tmp_path: Path,
) -> None:









    root = _experiment(tmp_path, cases=("c1", "c2"))
    rows = [
        (
            case_id,
            "required",
            AcceptanceFeedback(
                required=(f"test_gate.py::{case_id}",),
                present=(f"test_gate.py::{case_id}",),
                passing=(f"test_gate.py::{case_id}",) if case_id == "c1" else (),
                reason=None,
            ),
        )
        for case_id in ("c1", "c2")
    ]

    def _truncated(run_root: Path, digest: str) -> bytes:
        genuine = json.loads(
            _result_document(
                run_root,
                disposition="not-accepted",
                reason="tests:required-not-passing",
                feedback=rows,
                launch_sha256=digest,
            )
        )
        forged = dict(genuine)
        forged["feedback"] = [
            row for row in genuine["feedback"] if row["case_id"] == "c1"
        ]
        forged["disposition"] = "accepted"
        forged["reason"] = None
        return json.dumps(forged, sort_keys=True).encode("utf-8")

    _run(root, 1, _truncated)

    findings = _close(root)
    assert _kinds(findings) == {"unaccepted-session"}
    assert "c2" in findings[0].message


def test_an_acceptance_whose_contract_cannot_be_read_is_not_a_checked_one(
    tmp_path: Path,
) -> None:

    root = _experiment(tmp_path)
    _accepted_run(root)
    (root / "session.contract.json").write_text("{ not json", encoding="utf-8")

    findings = _close(root)
    assert _kinds(findings) == {"unaccepted-session"}
    assert "could not be read" in findings[0].message


@pytest.mark.parametrize(
    "alias",
    ["run-٠٠٠١", "run-１２３４"],
    ids=["arabic-indic", "fullwidth"],
)
def test_a_unicode_digit_run_name_cannot_alias_a_real_run(
    tmp_path: Path, alias: str
) -> None:









    root = _experiment(tmp_path)
    _refused_run(root, 1)
    alias_root = root / SESSION_RUNS_DIRNAME / alias
    alias_root.mkdir(parents=True)
    (alias_root / "launches").mkdir()
    (alias_root / "launches" / "0001.json").write_text("{}", encoding="utf-8")
    (alias_root / SESSION_RESULT_FILENAME).write_bytes(
        _tests_result(alias_root, disposition="accepted")
    )

    findings = _close(root)
    ids = [finding.id for finding in findings]
    assert alias in ids, "the alias was silently ignored rather than reported"
    assert "run-0001" in ids, "the real refused run must still be judged"


def test_hostile_nested_json_is_a_refusal_rather_than_a_crash(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:









    root = _experiment(tmp_path)
    _run(root, 1, (b"[" * 10_000) + (b"]" * 10_000))

    capsys.readouterr()
    assert main(["exp", "close", str(root)]) == cli.EXIT_EXPERIMENT_OPEN
    assert "unaccepted-session" in capsys.readouterr().out







@pytest.mark.parametrize(
    ("name", "payload"),
    [
        ("hand-written", b'{"disposition": "accepted"}\n'),
        ("not-json", b"accepted\n"),
        ("empty", b""),
        (
            "extra-field",
            json.dumps(
                {
                    "schema_version": 1,
                    "run_id": "run-0001",
                    "acceptance_modes": ["tests"],
                    "disposition": "accepted",
                    "reason": None,
                    "launch_sha256": None,
                    "feedback": [],
                    "verdict": "pass",
                },
                sort_keys=True,
            ).encode("utf-8"),
        ),
    ],
)
def test_a_result_no_strict_reader_accepts_is_a_failure_not_an_unknown(
    tmp_path: Path, name: str, payload: bytes
) -> None:








    root = _experiment(tmp_path)
    _run(root, 1, payload)

    findings = _close(root)
    assert _kinds(findings) == {"unaccepted-session"}, name
    assert "does not open this gate" in findings[0].message


def test_a_result_that_cannot_be_read_is_a_refusal_not_a_crash(
    tmp_path: Path,
) -> None:






    root = _experiment(tmp_path)
    run_root = root / SESSION_RUNS_DIRNAME / "run-0001"
    _run(root, 1, _tests_result(run_root, disposition="accepted"))
    result = run_root / SESSION_RESULT_FILENAME
    result.chmod(0o000)
    try:
        if os.access(result, os.R_OK):  
            pytest.skip("this process can read a mode-000 file")
        findings = _close(root)
    finally:
        result.chmod(0o644)

    assert _kinds(findings) == {"unaccepted-session"}
    assert "could not be read" in findings[0].message


@pytest.mark.parametrize("shape", ["symlink", "directory"])
def test_the_bounded_read_refuses_non_regular_shapes(
    tmp_path: Path, shape: str
) -> None:

    from gnd.exp.close import _read_capped

    target = tmp_path / "result.json"
    if shape == "symlink":
        real = tmp_path / "real.json"
        real.write_text("{}", encoding="utf-8")
        target.symlink_to(real)
    else:
        target.mkdir()

    with pytest.raises(OSError):
        _read_capped(target, 1024)


def test_the_bounded_read_refuses_a_fifo_instead_of_blocking_on_it() -> None:

















    import subprocess
    import sys
    import tempfile

    workspace = Path(tempfile.mkdtemp())
    fifo = workspace / SESSION_RESULT_FILENAME
    os.mkfifo(fifo)

    program = (
        "import sys\n"
        f"sys.path.insert(0, {str(Path(cli.__file__).parents[2])!r})\n"
        "from gnd.exp.close import _read_capped\n"
        "try:\n"
        f"    _read_capped({str(fifo)!r}, 1024)\n"
        "    print('NOT-REFUSED')\n"
        "except OSError:\n"
        "    print('REFUSED')\n"
    )
    try:
        completed = subprocess.run(
            [sys.executable, "-c", program],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except subprocess.TimeoutExpired:  
        pytest.fail("_read_capped blocked on a FIFO instead of refusing it")

    assert completed.stdout.strip() == "REFUSED", completed.stderr[-500:]


def test_a_result_exactly_at_the_cap_is_read_rather_than_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:






    import gnd.exp.session_store as store_module

    root = _experiment(tmp_path)
    written: list[int] = []

    def _payload(run_root: Path, digest: str) -> bytes:
        document = _tests_result(
            run_root, disposition="accepted", launch_sha256=digest
        )
        written.append(len(document))
        return document

    _run(root, 1, _payload)
    monkeypatch.setattr(store_module, "MAX_SESSION_RESULT_BYTES", written[0])

    assert _close(root) == []


def test_an_oversized_result_is_refused_without_reading_past_the_cap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:















    import gnd.exp.session_store as store_module

    cap = 64
    monkeypatch.setattr(store_module, "MAX_SESSION_RESULT_BYTES", cap)
    root = _experiment(tmp_path)
    run_root = root / SESSION_RUNS_DIRNAME / "run-0001"
    _run(root, 1, b"{" + b"x" * 100_000)

    real_read = os.read
    observed: list[int] = []

    def counting_read(fd: int, length: int) -> bytes:
        chunk = real_read(fd, length)
        observed.append(len(chunk))
        return chunk

    monkeypatch.setattr(os, "read", counting_read)
    findings = _close(root)

    assert _kinds(findings) == {"unaccepted-session"}
    assert "cap" in findings[0].message
    assert observed, "the implementation never read through os.read"
    assert sum(observed) <= cap + 1, (
        f"read {sum(observed)} bytes from a {100_001}-byte file under a "
        f"{cap}-byte cap; the cap is bounding the verdict, not the read"
    )
    assert (run_root / SESSION_RESULT_FILENAME).stat().st_size > cap


def test_the_data_driven_lane_result_opens_the_same_gate(tmp_path: Path) -> None:

    root = _experiment(tmp_path)
    run_root = root / SESSION_RUNS_DIRNAME / "run-0001"
    _run(root, 1, _session_result(run_root, disposition=SessionOutcome.accepted))

    assert _close(root) == []


@pytest.mark.parametrize(
    "disposition",
    [
        SessionOutcome.agent_failure,
        SessionOutcome.verifier_failure,
        SessionOutcome.budget_exhausted,
        SessionOutcome.stagnation,
        SessionOutcome.oscillation,
    ],
)
def test_every_non_accepting_data_driven_disposition_refuses_the_close(
    tmp_path: Path, disposition: SessionOutcome
) -> None:





    root = _experiment(tmp_path)
    run_root = root / SESSION_RUNS_DIRNAME / "run-0001"
    _run(root, 1, _session_result(run_root, disposition=disposition))

    findings = _close(root)
    assert _kinds(findings) == {"unaccepted-session"}
    assert disposition.value in findings[0].message


def test_the_tests_lane_writer_and_reader_agree_on_every_field(
    tmp_path: Path,
) -> None:









    from gnd.exp.tests_runner import TestsSessionResult

    run_root = tmp_path / SESSION_RUNS_DIRNAME / "run-0001"
    for disposition in ("accepted", "not-accepted", "verifier-failure"):
        written = _result_document(
            run_root,
            disposition=disposition,
            reason=None if disposition == "accepted" else "tests:required-not-passing",
            feedback=[
                (
                    "gate",
                    "required",
                    AcceptanceFeedback(
                        required=("test_gate.py::test_pass",),
                        present=("test_gate.py::test_pass",),
                        
                        
                        
                        passing=(
                            ("test_gate.py::test_pass",)
                            if disposition == "accepted"
                            else ()
                        ),
                        reason=None,
                    ),
                )
            ],
            launch_sha256="a" * 64,
        )
        parsed = TestsSessionResult.model_validate_json(written)
        assert parsed.model_dump(mode="json") == json.loads(written), disposition


def test_the_reader_accepts_every_result_this_repository_has_committed() -> None:









    repo_root = Path(__file__).resolve().parent.parent
    committed = sorted(
        (repo_root / "tests/fixtures/public-session-results").glob("*/runs/run-*/result.json")
    )
    assert committed, "the committed session evidence this test reads is gone"

    versions = set()
    verdicts = set()
    for path in committed:
        payload = path.read_bytes()
        accepted, run_id, description = _accepted_disposition(payload)
        document = json.loads(payload)
        
        
        
        
        
        
        assert accepted == (document.get("disposition") == "accepted"), f"{path}: {description}"
        assert run_id == path.parent.name
        versions.add(document["schema_version"])
        verdicts.add(accepted)
    assert versions == {1, 2}, (
        "both evidence schema versions must stay represented, or this test "
        "silently stops covering the frozen reader"
    )
    assert verdicts == {True, False}, (
        "the reader must stay exercised against a real ACCEPTED and a real "
        "NONACCEPTED committed document; one verdict alone cannot fail on the "
        "other branch"
    )







def test_the_allocator_never_places_a_new_run_below_an_existing_one(
    tmp_path: Path,
) -> None:














    from gnd.cli import _next_session_run_root

    root = tmp_path / EXPERIMENT_ID
    runs = root / SESSION_RUNS_DIRNAME
    runs.mkdir(parents=True)
    for index in (1, 2, 3):
        (runs / f"run-{index:04d}").mkdir()

    (runs / "run-0001").rmdir()  
    assert _next_session_run_root(root).name == "run-0004", (
        "a new run took a number below runs that preceded it; 'the "
        "highest-indexed run is the latest' is then false"
    )


def test_the_allocator_only_mints_names_the_gate_counts(tmp_path: Path) -> None:







    from gnd.cli import _next_session_run_root
    from gnd.exp.close import (
        MAX_SESSION_RUN_INDEX,
        MIN_SESSION_RUN_INDEX,
        SESSION_RUN_PATTERN,
    )

    root = tmp_path / EXPERIMENT_ID
    root.mkdir(parents=True)
    for _ in range(5):
        minted = _next_session_run_root(root)
        assert SESSION_RUN_PATTERN.match(minted.name), minted.name
        index = int(minted.name.removeprefix("run-"))
        assert MIN_SESSION_RUN_INDEX <= index <= MAX_SESSION_RUN_INDEX
        minted.mkdir()







def test_no_kind_declares_latest_acceptance_without_also_declaring_a_launch() -> None:










    from gnd.exp.spec import CLOSE_OBLIGATIONS, KIND_POLICY

    for kind, policy in KIND_POLICY.items():
        if CLOSE_OBLIGATIONS.latest_sessions_accepted in policy.close_obligations:
            assert CLOSE_OBLIGATIONS.recorded_launch in policy.close_obligations, (
                f"kind {kind!r} would accept an experiment that never launched"
            )


@pytest.mark.parametrize("kind", ["analysis", "roundtrip", "data-driven"])
def test_a_kind_without_the_work_obligations_closes_with_no_runs_at_all(
    tmp_path: Path, kind: str
) -> None:






    root = _experiment(tmp_path, kind=kind)
    assert _close(root) == []







@pytest.mark.parametrize("outcome", ["unanswered", "invalidated"])
def test_an_honestly_unanswered_work_experiment_still_closes_once_its_session_accepted(
    tmp_path: Path, outcome: str
) -> None:








    root = _experiment(tmp_path, outcome=outcome)
    _accepted_run(root)

    assert _close(root) == []


def test_no_work_branch_reads_an_outcome_value(tmp_path: Path) -> None:






    verdicts = set()
    for index, outcome in enumerate(("answered", "unanswered", "invalidated")):
        root = _experiment(
            tmp_path / str(index), outcome=outcome, experiment_id=EXPERIMENT_ID
        )
        _refused_run(root)
        verdicts.add(tuple(sorted(_kinds(_close(root)))))
    assert verdicts == {("unaccepted-session",)}







def test_a_symlinked_runs_root_is_refused_rather_than_followed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _experiment(tmp_path)
    elsewhere = tmp_path / "elsewhere"
    (elsewhere / "run-0001").mkdir(parents=True)
    run_root = elsewhere / "run-0001"
    (run_root / SESSION_RESULT_FILENAME).write_bytes(
        _tests_result(run_root, disposition="accepted")
    )
    (root / SESSION_RUNS_DIRNAME).symlink_to(elsewhere, target_is_directory=True)

    capsys.readouterr()
    assert main(["exp", "close", str(root)]) == cli.EXIT_IO
    assert "must be a real directory" in capsys.readouterr().out


def test_a_symlinked_run_directory_is_not_counted_as_a_launch(tmp_path: Path) -> None:

    root = _experiment(tmp_path)
    elsewhere = tmp_path / "elsewhere" / "run-0001"
    elsewhere.mkdir(parents=True)
    (elsewhere / SESSION_RESULT_FILENAME).write_bytes(
        _tests_result(elsewhere, disposition="accepted")
    )
    (root / SESSION_RUNS_DIRNAME).mkdir()
    (root / SESSION_RUNS_DIRNAME / "run-0001").symlink_to(
        elsewhere, target_is_directory=True
    )

    assert "unrecorded-launch" in _kinds(_close(root))


def test_a_directory_outside_the_minted_shape_is_not_a_run(tmp_path: Path) -> None:






    root = _experiment(tmp_path)
    scratch = root / SESSION_RUNS_DIRNAME / "run-bound-resume"
    scratch.mkdir(parents=True)
    (scratch / SESSION_RESULT_FILENAME).write_bytes(
        _tests_result(scratch, disposition="accepted")
    )

    assert "unrecorded-launch" in _kinds(_close(root))


def test_a_stray_file_beside_the_runs_does_not_break_enumeration(
    tmp_path: Path,
) -> None:
    root = _experiment(tmp_path)
    _accepted_run(root)
    (root / SESSION_RUNS_DIRNAME / "NOTES.md").write_text("scratch\n", encoding="utf-8")

    assert _close(root) == []







def test_the_gate_reports_every_undischarged_obligation_not_the_first(
    tmp_path: Path,
) -> None:





    root = tmp_path / EXPERIMENT_ID
    (root / "results").mkdir(parents=True)
    (root / "results" / "run.json").write_text("{}\n", encoding="utf-8")
    (root / "SPEC.md").write_text(
        render_frontmatter(
            {
                "id": EXPERIMENT_ID,
                "kind": "work",
                "title": "a work experiment that discharged nothing",
                "questions": [
                    {"id": "Q1", "text": "did the declared tests pass?"},
                    {"id": "Q2", "text": "what did the smoke run show?"},
                ],
                "follows": [],
            },
            f"# {EXPERIMENT_ID}\n",
        ),
        encoding="utf-8",
    )
    (root / "CONCLUSIONS.md").write_text(
        render_frontmatter(
            {
                "id": EXPERIMENT_ID,
                "resolves": [
                    {"id": "Q1", "outcome": "answered", "evidence": "results/run.json"}
                ],
            },
            f"# {EXPERIMENT_ID} conclusions\n",
        ),
        encoding="utf-8",
    )

    assert _kinds(_close(root)) == {"forgotten-question", "unrecorded-launch"}
