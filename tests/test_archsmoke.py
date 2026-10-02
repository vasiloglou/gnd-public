"""Owner-approved corpus for dynamic architecture smoke (v4 Phase 3).

The corpus preceded the implementation (D-P3.1, corpus-first). At its commit
the shape tests below were green and every evaluator row was red for exactly
one reason: ``gnd.archsmoke`` did not yet exist.

The two negative controls are why the corpus is worth its cost. S-08 mutates
``run_row`` into a runner that never spawns and requires S-03, S-06 and S-11 to
go red; S-14 empties the parametrization and requires the non-vacuity guard to
go red. A corpus that cannot fail under those mutations would credit a runner
that runs nothing.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

CORPUS = Path(__file__).parent / "fixtures" / "architecture" / "smoke"
BASE = CORPUS / "base"
ANSWER_KEY = json.loads((CORPUS / "expected.json").read_text(encoding="utf-8"))
CASE_DIRS = tuple(sorted(p for p in (CORPUS / "cases").iterdir() if p.is_dir()))

EVALUATOR_CASES = tuple(
    p for p in CASE_DIRS if ANSWER_KEY["cases"][p.name].get("kind") != "negative-control"
)
CONTROL_CASES = tuple(
    p for p in CASE_DIRS if ANSWER_KEY["cases"][p.name].get("kind") == "negative-control"
)

SMOKE_STATUSES = (
    "matched",
    "band-mismatch",
    "did-not-start",
    "timed-out",
    "output-cap-exceeded",
)


def _story(case_dir: Path) -> dict:
    return json.loads((case_dir / "case.json").read_text(encoding="utf-8"))


def _materialize(case_dir: Path, tmp_path: Path) -> Path:
    """Copy the shared base project, then the case's own files over it."""
    root = tmp_path / "project"
    shutil.copytree(BASE, root)
    for source in case_dir.iterdir():
        if source.name == "case.json":
            continue
        shutil.copy2(source, root / source.name)
    return root


# ---------------------------------------------------------------------------
# Shape -- green at the corpus commit, and they guard the corpus itself
# ---------------------------------------------------------------------------


def test_the_answer_key_covers_exactly_the_committed_cases() -> None:
    assert set(ANSWER_KEY["cases"]) == {p.name for p in CASE_DIRS}
    assert ANSWER_KEY["case_count"] == len(CASE_DIRS)


def test_every_case_tells_a_story() -> None:
    for case_dir in CASE_DIRS:
        story = _story(case_dir)["story"]
        assert len(story) > 40, f"{case_dir.name} has no readable story"


def test_every_evaluator_case_ships_a_contract() -> None:
    for case_dir in EVALUATOR_CASES:
        assert (case_dir / "architecture.contract.yaml").is_file(), case_dir.name


def test_every_expected_status_is_in_the_closed_vocabulary() -> None:
    for name, expected in ANSWER_KEY["cases"].items():
        for row in expected.get("rows", ()):
            assert row["status"] in SMOKE_STATUSES, (name, row["status"])


def test_the_answer_key_uses_every_status_at_least_once() -> None:
    """A vocabulary with an unexercised member is a declared branch with no case."""
    used = {
        row["status"]
        for expected in ANSWER_KEY["cases"].values()
        for row in expected.get("rows", ())
    }
    assert used == set(SMOKE_STATUSES), f"never exercised: {set(SMOKE_STATUSES) - used}"


def test_each_negative_control_names_the_cases_it_must_red() -> None:
    for case_dir in CONTROL_CASES:
        expected = ANSWER_KEY["cases"][case_dir.name]
        assert expected["mutation"], case_dir.name
        assert expected["must_red"], case_dir.name
        for target in expected["must_red"]:
            assert target in ANSWER_KEY["cases"], target


def test_the_base_entry_point_is_the_only_behaviour_a_case_needs() -> None:
    source = (BASE / "app.py").read_text(encoding="utf-8")
    for command in (
        "ok",
        "refuse",
        "boom",
        "write",
        "readfile",
        "spawn-and-sleep",
        "flood",
        "badbytes",
    ):
        assert f'"{command}"' in source, command


# ---------------------------------------------------------------------------
# Evaluator -- RED until src/gnd/archsmoke.py exists
# ---------------------------------------------------------------------------


def _evaluate(case_dir: Path, tmp_path: Path, run_row: Any = None) -> None:
    """Compare one case against the answer key, optionally under a mutated
    ``run_row``. The negative controls drive the SAME comparison the real
    evaluator uses; a control that took a private path would prove nothing."""
    from gnd.archsmoke import run_row as real_run_row
    from gnd.archsmoke import smoke_rows, uncited_exits

    run_row = run_row or real_run_row

    expected = ANSWER_KEY["cases"][case_dir.name]
    root = _materialize(case_dir, tmp_path)
    rows = smoke_rows(root)

    assert [row.id for row in rows] == [r["id"] for r in expected["rows"]], (
        f"{case_dir.name}: the contract's rows are not the answer key's rows"
    )

    timeout = expected.get("timeout_seconds", 30)
    tmp_dirs: list[Path] = []
    for row, want in zip(rows, expected["rows"]):
        row_tmp = tmp_path / "row" / row.id
        row_tmp.mkdir(parents=True)
        tmp_dirs.append(row_tmp)
        outcome = run_row(row, project_root=root, tmp=row_tmp, timeout=timeout)

        assert outcome.status == want["status"], (
            f"{case_dir.name}/{row.id}: expected {want['status']}, got {outcome.status}"
        )
        assert outcome.actual_exit == want["actual_exit"], (
            f"{case_dir.name}/{row.id}: exit {outcome.actual_exit} != {want['actual_exit']}"
        )
        for fragment in want.get("stdout_contains", ()):
            assert fragment in outcome.stdout, (row.id, fragment)
        for fragment in want.get("message_contains", ()):
            assert fragment in outcome.message, (row.id, fragment)
        cap = expected.get("assertions", {}).get("capture_at_most_bytes_per_stream")
        if cap is not None:
            assert len(outcome.stdout.encode("utf-8", "surrogatepass")) <= cap * 4

    assertions = expected.get("assertions", {})
    if assertions.get("tmp_dirs_distinct"):
        assert len({str(d) for d in tmp_dirs}) == len(tmp_dirs)
    if assertions.get("no_surviving_descendants"):
        survivors = subprocess.run(
            ["pgrep", "-f", "time.sleep(45)"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.split()
        assert not survivors, f"{case_dir.name} leaked {len(survivors)} descendants"
    if "uncited_exits" in assertions:
        from gnd.architecture import load_architecture_contract

        actual = [list(pair) for pair in uncited_exits(load_architecture_contract(root))]
        assert actual == assertions["uncited_exits"]


def test_the_empty_contract_case_announces_itself(tmp_path: Path) -> None:
    """S-07: nothing runs, and the vacuity is SAID rather than silently green."""
    from gnd.archsmoke import smoke_rows

    case_dir = CORPUS / "cases" / "S-07-no-smoke-rows"
    root = _materialize(case_dir, tmp_path)
    assert smoke_rows(root) == ()


def test_substitute_refuses_a_substitution_outside_the_closed_set() -> None:
    """The branch the loader makes unreachable from a contract is still reachable
    from the public function, so it ships with a case that can fail it."""
    from gnd.archsmoke import substitute

    with pytest.raises(ValueError, match="tmp"):
        substitute(["--out", "{scratch}/x.json"], tmp=Path("/tmp"))


def test_the_emitted_module_is_three_lines_and_delegates() -> None:
    from gnd.codegen.emit import render_smoke_module

    text = render_smoke_module()
    lines = text.splitlines()
    # Four since v5.1 Phase 1: OQ-V5-P4-2's blank line separates the import
    # block from the executable assignment. The `ruff` I001 falsifier for that
    # separator lives with the rest of the naming work, in
    # `test_codegen_smoke_naming.py`.
    assert len(lines) == 4, lines
    assert lines[1] == "from gnd.archsmoke import build_smoke_module"
    assert lines[2] == ""
    assert "build_smoke_module(__file__)" in lines[3]


def test_conformance_never_reaches_the_smoke_runner() -> None:
    """T3.5. archsmoke is the first module in the package that deliberately
    executes project code; conformance must not be able to reach it."""
    probe = (
        "import sys, json;"
        "import gnd.conformance.service;"
        "print(json.dumps('gnd.archsmoke' in sys.modules))"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout.strip()) is False, (
        "importing conformance pulled in the execution primitive"
    )

    # Negative control: the SAME probe, with the import planted. If this does not
    # report True the probe cannot see the thing it exists to forbid, and the
    # assertion above is green for the wrong reason.
    planted = subprocess.run(
        [
            sys.executable,
            "-c",
            probe.replace("import gnd.conformance.service;", "import gnd.archsmoke;"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert planted.returncode == 0, planted.stderr
    assert json.loads(planted.stdout.strip()) is True, (
        "the never-imports probe cannot detect a planted import"
    )


# ---------------------------------------------------------------------------
# The negative controls -- the corpus proving it can tell a runner from a stub
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case_dir", EVALUATOR_CASES, ids=[p.name for p in EVALUATOR_CASES])
def test_corpus_case(case_dir: Path, tmp_path: Path) -> None:
    _evaluate(case_dir, tmp_path)


def test_negative_control_a_runner_that_never_spawns_reds_its_named_cases(
    tmp_path: Path,
) -> None:
    """S-08. Mutation: return the declared band without ever spawning. Every
    case the answer key names must go red. If any stayed green, the corpus
    would credit a runner that runs nothing."""
    from gnd import archsmoke

    def never_spawns(row, *, project_root, tmp, timeout=archsmoke.DEFAULT_TIMEOUT_SECONDS):
        return archsmoke.SmokeOutcome(
            id=row.id,
            entry_point=row.entry_point,
            argv=tuple(row.argv),
            expect_exit=row.expect_exit,
            status=archsmoke.SmokeStatus.MATCHED,
            actual_exit=row.expect_exit,
            stdout="",
            stderr="",
            truncated=False,
        )

    control = ANSWER_KEY["cases"]["S-08-negative-control-never-spawns"]
    assert control["must_red"], "the control names no cases"
    for target in control["must_red"]:
        with pytest.raises(AssertionError):
            _evaluate(CORPUS / "cases" / target, tmp_path / target, run_row=never_spawns)


def test_negative_control_an_empty_parametrization_reds_the_non_vacuity_guard(
    tmp_path: Path,
) -> None:
    """S-14. Mutation: parametrize over nothing while the contract still
    declares rows. ``test_smoke_declares_rows`` must go red -- otherwise a
    silently empty smoke suite passes and the guard is itself vacuous."""
    from gnd import archsmoke

    case_dir = CORPUS / "cases" / "S-01-accepting-row"
    root = _materialize(case_dir, tmp_path)
    module_file = str(root / "test_architecture_smoke_corpus.py")
    Path(module_file).write_text("# placeholder\n", encoding="utf-8")

    real_rows = archsmoke.smoke_rows
    calls = {"n": 0}

    def drop_rows_at_build(project_root):
        calls["n"] += 1
        return () if calls["n"] == 1 else real_rows(project_root)

    archsmoke.smoke_rows = drop_rows_at_build
    try:
        _, declares_rows, _floor = archsmoke.build_smoke_module(module_file)
    finally:
        archsmoke.smoke_rows = real_rows

    with pytest.raises(AssertionError, match="does not carry every declared row"):
        declares_rows()


# ---------------------------------------------------------------------------
# Totality regressions -- each reproduced against the pre-fix runner
# ---------------------------------------------------------------------------


def test_a_project_root_that_does_not_exist_is_an_outcome_not_an_exception(
    tmp_path: Path,
) -> None:
    """run_row's docstring claims totality. A missing project root made Popen
    raise FileNotFoundError straight through it -- reproduced before the fix."""
    from gnd.architecture import ArchitectureSmoke
    from gnd.archsmoke import SmokeStatus, run_row

    row = ArchitectureSmoke(id="p", entry_point="app", argv=(), expect_exit=0)
    outcome = run_row(row, project_root=tmp_path / "absent", tmp=tmp_path / "t")
    assert outcome.status is SmokeStatus.DID_NOT_START
    assert outcome.actual_exit is None


def test_a_missing_tmp_directory_does_not_forge_a_did_not_start(
    tmp_path: Path,
) -> None:
    """The marker mechanism must report that the ENTRY POINT did not resolve,
    never that its own scratch directory was absent. Before the fix a module
    that resolved perfectly was reported did-not-start because the marker write
    failed."""
    from gnd.archsmoke import SmokeStatus, run_row, smoke_rows

    case_dir = CORPUS / "cases" / "S-01-accepting-row"
    root = _materialize(case_dir, tmp_path)
    (row,) = smoke_rows(root)
    outcome = run_row(row, project_root=root, tmp=tmp_path / "never" / "created")
    assert outcome.status is SmokeStatus.MATCHED, outcome.message


# ---------------------------------------------------------------------------
# Adversarial diff review regressions (v4 Phase 3, codex). Each was REPRODUCED
# against the pre-fix runner before the repair was written.
# ---------------------------------------------------------------------------


def _project(tmp_path: Path, **modules: str) -> Path:
    root = tmp_path / "proj"
    root.mkdir(parents=True, exist_ok=True)
    for name, source in modules.items():
        (root / f"{name}.py").write_text(source, encoding="utf-8")
    return root


def _row(entry_point: str, expect: int, *argv: str):
    from gnd.architecture import ArchitectureSmoke

    return ArchitectureSmoke(
        id="probe", entry_point=entry_point, argv=tuple(argv), expect_exit=expect
    )


def test_a_package_that_cannot_be_executed_never_reports_matched(tmp_path: Path) -> None:
    """F1. find_spec proves something RESOLVES; it does not prove python -m can
    execute it. A package without __main__ resolved, wrote the start marker and
    exited 1, so a row declaring 1 reported MATCHED while no entry-point code
    ran -- the defining defect class, one layer under S-11."""
    from gnd.archsmoke import SmokeStatus, run_row

    root = tmp_path / "proj"
    (root / "pkg").mkdir(parents=True)
    (root / "pkg" / "__init__.py").write_text("", encoding="utf-8")

    outcome = run_row(_row("pkg", 1), project_root=root, tmp=tmp_path / "t")
    assert outcome.status is SmokeStatus.DID_NOT_START, outcome.message


def test_an_over_cap_child_that_exits_immediately_is_not_matched(tmp_path: Path) -> None:
    """F2. Overflow lost to exit: a child writing past the cap and exiting 0
    reported MATCHED and truncated=True at the same time."""
    from gnd.archsmoke import MAX_CAPTURE_BYTES, SmokeStatus, run_row

    root = _project(
        tmp_path,
        fastflood=(
            "import sys\n"
            f"sys.stdout.buffer.write(b'x' * {MAX_CAPTURE_BYTES + 1})\n"
            "sys.stdout.buffer.flush()\n"
            "raise SystemExit(0)\n"
        ),
    )
    outcome = run_row(_row("fastflood", 0), project_root=root, tmp=tmp_path / "t")
    assert outcome.status is SmokeStatus.OUTPUT_CAP_EXCEEDED, outcome.message
    assert outcome.truncated
    assert len(outcome.stdout.encode("utf-8")) <= MAX_CAPTURE_BYTES


def test_an_over_cap_stderr_child_that_exits_immediately_is_not_matched(
    tmp_path: Path,
) -> None:
    """F2, the stderr half -- S-12 exercised neither fast exit nor stderr."""
    from gnd.archsmoke import MAX_CAPTURE_BYTES, SmokeStatus, run_row

    root = _project(
        tmp_path,
        fasterr=(
            "import sys\n"
            f"sys.stderr.buffer.write(b'e' * {MAX_CAPTURE_BYTES + 1})\n"
            "sys.stderr.buffer.flush()\n"
            "raise SystemExit(0)\n"
        ),
    )
    outcome = run_row(_row("fasterr", 0), project_root=root, tmp=tmp_path / "t")
    assert outcome.status is SmokeStatus.OUTPUT_CAP_EXCEEDED, outcome.message
    assert outcome.truncated


def test_the_deadline_covers_a_descendant_that_holds_the_pipes(tmp_path: Path) -> None:
    """F3. The leader exited 0 while a descendant held stdout/stderr open. The
    runner broke out of its poll loop on the leader's exit and then blocked in
    the reader join and pipe close -- 8.04s measured against a 1s deadline."""
    import time

    from gnd.archsmoke import run_row

    root = _project(
        tmp_path,
        leader_exits=(
            "import subprocess, sys\n"
            "subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'])\n"
            "raise SystemExit(0)\n"
        ),
    )
    started = time.monotonic()
    run_row(_row("leader_exits", 0), project_root=root, tmp=tmp_path / "t", timeout=1)
    elapsed = time.monotonic() - started
    assert elapsed < 8, f"run_row took {elapsed:.2f}s against a 1s deadline"


# ---------------------------------------------------------------------------
# F5 -- the REAL seam. These drive the emitted three-line module under pytest
# rather than comparing statuses behind its back.
# ---------------------------------------------------------------------------


def _emitted_project(tmp_path: Path, case: str) -> Path:
    from gnd.codegen.emit import render_smoke_module

    root = _materialize(CORPUS / "cases" / case, tmp_path)
    (root / "test_architecture_smoke_corpus.py").write_text(
        render_smoke_module(), encoding="utf-8"
    )
    return root


def _pytest_over(root: Path, *args: str, mutation: str = "") -> subprocess.CompletedProcess:
    plugin = ""
    if mutation:
        (root / "_mutant.py").write_text(mutation, encoding="utf-8")
        plugin = "_mutant"
    argv = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:randomly",
        "-p",
        "no:cacheprovider",
        *(["-p", plugin] if plugin else []),
        "test_architecture_smoke_corpus.py",
        *args,
    ]
    return subprocess.run(argv, cwd=root, capture_output=True, text=True, check=False)


def test_the_emitted_module_greens_and_names_its_rows(tmp_path: Path) -> None:
    """The real bridge, collected and run, with the contract's own row ids."""
    root = _emitted_project(tmp_path, "S-01-accepting-row")
    collected = _pytest_over(root, "--collect-only")
    assert "test_architecture_smoke_corpus.py::test_smoke[accepts]" in collected.stdout
    assert _pytest_over(root).returncode == 0


def test_the_emitted_module_reds_on_a_failing_row(tmp_path: Path) -> None:
    """The seam the corpus was comparing around: a band mismatch must fail the
    MODULE, not merely produce a status object the harness inspects."""
    root = _emitted_project(tmp_path, "S-03-band-mismatch")
    result = _pytest_over(root)
    assert result.returncode != 0
    assert "band mismatch" in result.stdout


def test_the_emitted_module_announces_an_empty_contract(tmp_path: Path) -> None:
    """S-07 through the real module: a skip with a message, not silence."""
    root = _emitted_project(tmp_path, "S-07-no-smoke-rows")
    result = _pytest_over(root, "-rs")
    assert result.returncode == 0
    assert "no smoke rows" in result.stdout
    assert "architecture.contract.yaml" in result.stdout


def test_negative_control_a_pass_that_always_passes_greens_a_failing_row(
    tmp_path: Path,
) -> None:
    """Mutation: SmokeOutcome.passed returns True unconditionally. The failing
    row must go GREEN -- proving the assertion in the emitted module is
    load-bearing. Before this test, mutating `passed` left the whole corpus
    green because every case compared `outcome.status` directly."""
    root = _emitted_project(tmp_path, "S-03-band-mismatch")
    assert _pytest_over(root).returncode != 0, "the unmutated run must red"
    mutated = _pytest_over(
        root,
        mutation=(
            "import gnd.archsmoke as a\na.SmokeOutcome.passed = property(lambda self: True)\n"
        ),
    )
    assert mutated.returncode == 0, (
        "the pass/fail seam is not load-bearing: mutating `passed` changed nothing"
    )


def test_the_floor_reds_when_a_declared_row_is_deselected(tmp_path: Path) -> None:
    """The floor's real branch, through the real module: deselect one declared
    row and the module must fail naming it."""
    root = _emitted_project(tmp_path, "S-04-tmp-substitution")
    assert _pytest_over(root).returncode == 0
    partial = _pytest_over(
        root, "--deselect", "test_architecture_smoke_corpus.py::test_smoke[writes-b]"
    )
    assert partial.returncode != 0
    assert "writes-b" in partial.stdout


def test_negative_control_a_floor_that_asserts_nothing_greens_a_partial_run(
    tmp_path: Path,
) -> None:
    """Mutation: replace the floor with one that asserts nothing. The partial
    run must go GREEN, proving the floor -- not something else -- is what reds
    a smoke suite that ran only some of its declared rows."""
    root = _emitted_project(tmp_path, "S-04-tmp-substitution")
    mutation = (
        "import pytest\n"
        "import gnd.archsmoke as a\n"
        "_real = a.build_smoke_module\n"
        "def _patched(module_file):\n"
        "    smoke, declares, _floor = _real(module_file)\n"
        "    @pytest.fixture(scope='module', autouse=True)\n"
        "    def _noop():\n"
        "        yield\n"
        "    return smoke, declares, _noop\n"
        "a.build_smoke_module = _patched\n"
    )
    mutated = _pytest_over(
        root,
        "--deselect",
        "test_architecture_smoke_corpus.py::test_smoke[writes-b]",
        mutation=mutation,
    )
    assert mutated.returncode == 0, "the non-vacuity floor is not what reds a partial run"
