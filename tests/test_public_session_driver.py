"""v4.0 Phase 4 -- T4.5 / OQ-P4-3: the parameterized session driver.

The v3.0 record deferred collapsing five near-identical gated sessions because
doing it then would have rewritten five committed evidence directories.  This
driver collapses the invocation instead, so `test_prior_experiments_are_byte_unedited`
in test_bookrec_phase4.py still holds.

Rows here are P4-15, P4-16, P4-30 and P4-31.  The round-1 panel found the r1
signature could not drive a tests-mode session at all and that only dry-run was
exercised; both are addressed below.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DRIVER_PATH = REPO_ROOT / "examples" / "drive_session.py"
BOOKREC = REPO_ROOT / "tests" / "fixtures" / "public-driver-sessions"


def _load_driver() -> Any:
    spec = importlib.util.spec_from_file_location("gnd_drive_session", DRIVER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Registered BEFORE exec: dataclasses resolves a field's type through
    # sys.modules[cls.__module__], and an unregistered module makes that None.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


driver = _load_driver()


def _contract(directory: Path, *, mode: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    if mode == "tests":
        acceptance: dict[str, Any] = {
            "mode": "tests",
            "protected": [],
            "required_tests": ["t.py::test_one"],
            "results_format": "junit-xml",
            "results_path": "results/junit.xml",
            "test_argv_sha256": "0" * 64,
        }
        case: dict[str, Any] = {"acceptance": acceptance, "case_id": "c", "role": "required"}
        version = 3
    else:
        acceptance = {"coverage": [{"fact_type": "f", "min_facts": 1}], "mode": mode}
        case = {
            "acceptance": acceptance,
            "case_id": "c",
            "role": "required",
            "inputs": [],
            "verify": {"command": "check", "subject": "population.json"},
        }
        version = 2
    (directory / "session.contract.json").write_text(
        json.dumps(
            {
                "cases": [case],
                "experiment_id": directory.name,
                "max_attempts": 1,
                "schema_version": version,
            }
        ),
        encoding="utf-8",
    )


def test_driver_discovers_every_committed_session() -> None:
    """P4-15, discovery half. The walk reaches all seven BookRec experiments."""
    found = driver.sessions(BOOKREC)

    ids = [session.experiment_id for session in found]
    assert len(ids) == len(set(ids)), ids
    assert len(ids) >= 7, ids
    # The mode comes from each CONTRACT, never from the directory name.
    by_id = {session.experiment_id: session for session in found}
    assert by_id["EXP-002-bookrec-v1-gate"].tests_mode is True
    assert by_id["EXP-001-bookrec-v1-development"].tests_mode is False


def test_driver_holds_no_experiment_literal() -> None:
    """P4-16, the source half. Necessary, and on its own not sufficient."""
    source = DRIVER_PATH.read_text(encoding="utf-8")

    assert "EXP-0" not in source
    assert "bookrec" not in source.lower().replace("examples/bookrec", "")


def test_g05_g08_schema_v6_driver_forwards_only_policy(tmp_path: Path) -> None:
    experiment = tmp_path / "EXP-999-declared"
    experiment.mkdir()
    (experiment / "session.contract.json").write_text(
        json.dumps(
            {
                "schema_version": 6,
                "experiment_id": experiment.name,
                "max_attempts": 1,
                "adapter": {"policy_id": "local", "parameters": {"model": None}},
                "cases": [],
            }
        ),
        encoding="utf-8",
    )
    (session,) = driver.sessions(tmp_path)
    policy = tmp_path / "adapter.policy.json"
    policy.write_text("{}\n", encoding="utf-8")
    outcome = driver.drive(
        session,
        adapter_policy=policy,
        timeout_seconds=5,
        dry_run=True,
    )
    assert outcome.argv[0][-2:] == ("--adapter-policy", str(policy))
    with pytest.raises(ValueError, match="requires adapter_policy only"):
        driver.drive(
            session,
            adapter="codex",
            adapter_policy=policy,
            timeout_seconds=5,
            dry_run=True,
        )


def test_g05_g08_driver_prints_no_policy_path(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    experiment = tmp_path / "EXP-999-declared"
    experiment.mkdir()
    (experiment / "session.contract.json").write_text(
        json.dumps(
            {
                "schema_version": 6,
                "experiment_id": experiment.name,
                "max_attempts": 1,
                "adapter": {"policy_id": "local", "parameters": {"model": None}},
                "cases": [],
            }
        ),
        encoding="utf-8",
    )
    secret_path = tmp_path / "private-operator-secret.policy.json"
    secret_path.write_text("{}\n", encoding="utf-8")
    assert (
        driver.main(
            [
                "--root",
                str(tmp_path),
                "--adapter-policy",
                str(secret_path),
                "--timeout",
                "5",
                "--dry-run",
            ]
        )
        == 0
    )
    assert str(secret_path) not in capsys.readouterr().out


@pytest.mark.parametrize("name", ["exp-alpha", "exp-omega-gate", "EXP-999-whatever"])
def test_driver_argv_depends_on_mode_alone_not_on_identity(tmp_path: Path, name: str) -> None:
    """P4-16, the BEHAVIOURAL half -- the source grep alone is bypassable.

    The adversarial reviewer added `if session.experiment_id.endswith("-gate")`
    and every driver row stayed green, because the only guard was a substring
    scan. This row drives differently-named fixtures, including one ending in
    `-gate`, and asserts the constructed argv differs ONLY where the directory
    name appears -- so control flow that consults an experiment's identity reds.
    """
    root = tmp_path / name
    _contract(root / name, mode="tests")
    (session,) = driver.sessions(root)

    outcome = driver.drive(
        session, adapter="claude", test_argv=("python3", "-m", "pytest"),
        timeout_seconds=5, dry_run=True,
    )
    run_argv, close_argv = outcome.argv
    normalized = tuple(
        "<DIR>" if word == str(session.directory) else word for word in run_argv
    )

    assert normalized == (
        *driver.GND, "exp", "run", "<DIR>", "--adapter", "claude",
        "--test-argv=python3", "--test-argv=-m", "--test-argv=pytest",
    ), normalized
    assert close_argv == (*driver.GND, "exp", "close", str(session.directory))


@pytest.mark.parametrize("mode", ["tests", "constraint-satisfaction"])
def test_driver_drives_either_mode_through_one_path(tmp_path: Path, mode: str) -> None:
    """P4-15. One code path serves both modes; the tests lane gets its --test-argv.

    The r1 signature could not pass one at all, and `gnd exp run` refuses a
    tests-mode contract without it -- so this row is what makes EXP-007
    drivable.
    """
    _contract(tmp_path / "exp-fixture", mode=mode)
    (session,) = driver.sessions(tmp_path)
    test_argv: Sequence[str] = ("python", "-m", "pytest") if mode == "tests" else ()

    outcome = driver.drive(
        session, adapter="claude", test_argv=test_argv, timeout_seconds=5, dry_run=True
    )

    run_argv, close_argv = outcome.argv
    assert run_argv[: len(driver.GND) + 2] == (*driver.GND, "exp", "run")
    assert close_argv[: len(driver.GND) + 2] == (*driver.GND, "exp", "close")
    joined = [word for word in run_argv if word.startswith("--test-argv=")]
    assert bool(joined) is (mode == "tests")
    if mode == "tests":
        # The JOINED form, not the separated one: argparse eats `--test-argv -m`
        # as a flag and the real CLI exits 64 on it.
        assert joined == [f"--test-argv={word}" for word in test_argv]
        assert "--test-argv" not in run_argv


@pytest.mark.parametrize("mode", ["tests", "constraint-satisfaction"])
def test_driver_refuses_a_test_argv_mismatch(tmp_path: Path, mode: str) -> None:
    """P4-15, the refusal half. Both directions of the mode/argv mismatch."""
    _contract(tmp_path / "exp-fixture", mode=mode)
    (session,) = driver.sessions(tmp_path)
    wrong: Sequence[str] = () if mode == "tests" else ("python",)

    with pytest.raises(ValueError):
        driver.drive(session, adapter="claude", test_argv=wrong, timeout_seconds=5, dry_run=True)


def test_driver_never_swallows_a_child_failure(tmp_path: Path, monkeypatch) -> None:
    """P4-30. A nonzero child exit reaches the driver's exit, verbatim."""
    _contract(tmp_path / "exp-fixture", mode="constraint-satisfaction")
    calls: list[tuple[str, ...]] = []

    def fake_bounded(argv, *, timeout_seconds):
        calls.append(tuple(argv))
        return 15

    monkeypatch.setattr(driver, "_run_bounded", fake_bounded)

    (session,) = driver.sessions(tmp_path)
    outcome = driver.drive(session, adapter="claude", timeout_seconds=5)

    assert outcome.run_exit == 15
    assert outcome.close_exit is None
    assert outcome.ok is False
    # close is NOT attempted after a failed run -- one child call, not two.
    assert len(calls) == 1

    code = driver.main(
        ["--root", str(tmp_path), "--adapter", "claude", "--timeout", "5"]
    )
    assert code == 1


def test_driver_reports_a_close_failure_after_a_green_run(tmp_path: Path, monkeypatch) -> None:
    """P4-30, second half. `gnd exp run` at 0 and `gnd exp close` at 14 is a failure.

    Without this, a driver that only inspected the run's exit would call an
    experiment driven successfully when its completeness gate refused it.
    """
    _contract(tmp_path / "exp-fixture", mode="constraint-satisfaction")
    exits = iter([0, 14])

    def fake_bounded(argv, *, timeout_seconds):
        return next(exits)

    monkeypatch.setattr(driver, "_run_bounded", fake_bounded)

    (session,) = driver.sessions(tmp_path)
    outcome = driver.drive(session, adapter="claude", timeout_seconds=5)

    assert (outcome.run_exit, outcome.close_exit) == (0, 14)
    assert outcome.ok is False


def test_driver_bounds_every_child(tmp_path: Path, monkeypatch) -> None:
    """P4-31. The bound is mandatory, is passed down, and a timeout is not a pass."""
    _contract(tmp_path / "exp-fixture", mode="constraint-satisfaction")
    (session,) = driver.sessions(tmp_path)

    # No default: a caller cannot acquire an unbounded child by omission.
    with pytest.raises(TypeError):
        driver.drive(session, adapter="claude")

    # And no infinite or nonpositive bound, which argparse would otherwise accept.
    for bad in (float("inf"), float("nan"), 0, -1):
        with pytest.raises(ValueError):
            driver.drive(session, adapter="claude", timeout_seconds=bad)

    seen: list[float] = []

    def fake_bounded(argv, *, timeout_seconds):
        """Report a timeout: _run_bounded returns None when the bound expires."""
        seen.append(timeout_seconds)

    monkeypatch.setattr(driver, "_run_bounded", fake_bounded)
    outcome = driver.drive(session, adapter="claude", timeout_seconds=7)

    assert seen == [7]
    assert outcome.timed_out is True
    assert outcome.ok is False
    assert outcome.run_exit is None


def test_driver_refuses_an_unknown_only_selector(tmp_path: Path) -> None:
    """A silent no-op walk is the failure this row exists to catch."""
    _contract(tmp_path / "exp-fixture", mode="constraint-satisfaction")

    assert driver.main(
        ["--root", str(tmp_path), "--adapter", "claude", "--timeout", "5",
         "--only", "no-such-experiment", "--dry-run"]
    ) == 1
    assert driver.main(
        ["--root", str(tmp_path), "--adapter", "claude", "--timeout", "5", "--dry-run"]
    ) == 0


def test_driver_reaches_a_real_gnd_and_reports_its_real_exit(tmp_path: Path) -> None:
    """The seam every other row mocks away.

    The adversarial reviewer reproduced `FileNotFoundError: 'gnd'` from the
    documented invocation: a PEP 723 header made `uv run` build an isolated
    environment without this project, and no row exercised the real executable
    because each one was either dry-run or monkeypatched.

    This drives a synthetic experiment that `gnd exp run` refuses fast -- no
    agent is launched -- so the row proves the executable resolves and its exit
    code is carried, without paying for a live session.
    """
    _contract(tmp_path / "exp-malformed", mode="constraint-satisfaction")
    (session,) = driver.sessions(tmp_path)

    outcome = driver.drive(session, adapter="claude", timeout_seconds=120)

    # A real child ran: a nonzero gnd band, not an exception and not None.
    assert outcome.timed_out is False
    assert isinstance(outcome.run_exit, int) and outcome.run_exit != 0
    assert outcome.close_exit is None
    assert outcome.ok is False
    assert driver.GND[0] == sys.executable


def test_driver_kills_the_whole_process_group_on_timeout(
    tmp_path: Path, monkeypatch
) -> None:
    """P4-31, the half a leader-only kill cannot make.

    subprocess.run(timeout=...) kills only the leader, so a child that spawned
    its own children leaves them running after the bound expires -- the bound
    becomes a report. The reviewer reproduced two surviving 30-second
    grandchildren. This spawns a real grandchild and asserts it is gone.
    """
    marker = tmp_path / "grandchild-alive"
    spawner = (
        "import subprocess,sys,time;"
        f"subprocess.Popen([sys.executable,'-c',\"import time,pathlib;"
        f"pathlib.Path(r'{marker}').write_text('x');time.sleep(30)\"]);"
        "time.sleep(30)"
    )
    monkeypatch.setattr(driver, "GND", (sys.executable, "-c", spawner))
    _contract(tmp_path / "exp-hang", mode="constraint-satisfaction")
    (session,) = driver.sessions(tmp_path)

    outcome = driver.drive(session, adapter="claude", timeout_seconds=3)

    assert outcome.timed_out is True
    assert outcome.run_exit is None
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and not marker.exists():
        time.sleep(0.05)
    assert marker.exists(), "the grandchild never started -- the row proves nothing"

    survivors = subprocess.run(
        ["pgrep", "-f", "pathlib.Path"], check=False, capture_output=True, text=True
    ).stdout.split()
    assert not survivors, f"descendants survived the bound: {survivors}"
