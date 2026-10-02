

















from __future__ import annotations

import inspect
import os
import re
import stat
from pathlib import Path

import pytest

from gnd import cli
from gnd.cli import main

CLI_SOURCE = Path(cli.__file__).read_text(encoding="utf-8")


EXITS_SOURCE = (Path(cli.__file__).parent / "exits.py").read_text(encoding="utf-8")






PRE_EXISTING_ALLOCATION = {0, 1, 2, 3, 4, 5, 6, 10, 11, 12, 64, 66, 70, 74}







def test_band_fourteen_is_disjoint_from_the_literal_allocation_set() -> None:

    assert cli.EXIT_EXPERIMENT_OPEN == 14
    for allocated in sorted(PRE_EXISTING_ALLOCATION):
        assert cli.EXIT_EXPERIMENT_OPEN != allocated, (
            f"band 14 collides with the already-allocated {allocated}"
        )
    assert cli.EXIT_EXPERIMENT_OPEN not in PRE_EXISTING_ALLOCATION


def test_naming_sixty_six_did_not_move_it() -> None:






    assert cli.EXIT_NO_INPUT == 66
    assert cli.EXIT_NO_INPUT in PRE_EXISTING_ALLOCATION








ALLOCATION_BEFORE_CONFORMANCE = PRE_EXISTING_ALLOCATION | {14}




ALLOCATION_BEFORE_SESSION = PRE_EXISTING_ALLOCATION | {13, 14}







ALLOCATION_BEFORE_REVIEW = PRE_EXISTING_ALLOCATION | {13, 14, 15}


def test_band_fifteen_is_disjoint_from_every_shipped_exit() -> None:
    assert cli.EXIT_SESSION_NOT_ACCEPTED == 15
    for allocated in sorted(ALLOCATION_BEFORE_SESSION):
        assert cli.EXIT_SESSION_NOT_ACCEPTED != allocated
    assert cli.EXIT_SESSION_NOT_ACCEPTED not in ALLOCATION_BEFORE_SESSION












ALLOCATION_BEFORE_OPERATIONS_GATE = PRE_EXISTING_ALLOCATION | {13, 14, 15, 16}


def test_band_eighteen_is_disjoint_from_every_shipped_exit() -> None:







    assert cli.EXIT_EVOLUTION_OPERATIONS_GATED == 18
    for allocated in sorted(ALLOCATION_BEFORE_OPERATIONS_GATE):
        assert cli.EXIT_EVOLUTION_OPERATIONS_GATED != allocated, (
            f"band 18 collides with the already-allocated {allocated}"
        )
    assert cli.EXIT_EVOLUTION_OPERATIONS_GATED not in ALLOCATION_BEFORE_OPERATIONS_GATE


def test_seventeen_is_the_walk_halt_and_nothing_else() -> None:











    by_value: dict[int, list[str]] = {}
    for name, value in vars(cli).items():
        if name.startswith("EXIT_") and isinstance(value, int):
            by_value.setdefault(value, []).append(name)

    assert cli.EXIT_WALK_HALTED == 17
    assert by_value[17] == ["EXIT_WALK_HALTED"], (
        f"17 must have exactly one owner, found {by_value[17]}"
    )
    
    assert 17 not in ALLOCATION_BEFORE_OPERATIONS_GATE


def test_band_eighteen_is_one_meaning_and_not_one_per_gated_shape() -> None:









    named = {
        name
        for name, value in vars(cli).items()
        if name.startswith("EXIT_") and isinstance(value, int) and value == 18
    }
    assert named == {"EXIT_EVOLUTION_OPERATIONS_GATED"}
    assert cli.EXIT_EVOLUTION_OPERATIONS_GATED != cli.EXIT_COLLISION, (
        "a policy refusal and a stale-identity collision are unlike claims; one "
        "number for both would make 'refresh and retry' the wrong advice for "
        "half of it (D-24)"
    )


def test_band_sixteen_is_disjoint_from_every_shipped_exit() -> None:







    assert cli.EXIT_REVIEW_INCONCLUSIVE == 16
    for allocated in sorted(ALLOCATION_BEFORE_REVIEW):
        assert cli.EXIT_REVIEW_INCONCLUSIVE != allocated, (
            f"band 16 collides with the already-allocated {allocated}"
        )
    assert cli.EXIT_REVIEW_INCONCLUSIVE not in ALLOCATION_BEFORE_REVIEW
    assert 15 in ALLOCATION_BEFORE_REVIEW, (
        "the set this proof runs against does not include the band the previous "
        "plan allocated, so it is proving disjointness from a stale universe"
    )


def test_band_sixteen_is_one_meaning_and_not_one_per_review_failure_mode() -> None:









    named = {
        name
        for name, value in vars(cli).items()
        if name.startswith("EXIT_") and isinstance(value, int) and value == 16
    }
    assert named == {"EXIT_REVIEW_INCONCLUSIVE"}
    assert cli.REVIEW_QUORUM == 3
    assert cli.EXIT_REVIEW_INCONCLUSIVE != cli.EXIT_SESSION_NOT_ACCEPTED, (
        "a below-quorum PANEL and a non-accepted SESSION are unlike claims; one "
        "number for both would blend two lifecycles (D-24)"
    )


def test_band_thirteen_is_disjoint_from_the_literal_allocation_set() -> None:





    assert cli.EXIT_MODEL_CODE_DRIFT == 13
    for allocated in sorted(ALLOCATION_BEFORE_CONFORMANCE):
        assert cli.EXIT_MODEL_CODE_DRIFT != allocated, (
            f"band 13 collides with the already-allocated {allocated}"
        )
    assert cli.EXIT_MODEL_CODE_DRIFT not in ALLOCATION_BEFORE_CONFORMANCE
    assert 14 in ALLOCATION_BEFORE_CONFORMANCE, (
        "the set this proof runs against does not include the band the previous "
        "plan allocated, so it is proving disjointness from a stale universe"
    )


def test_band_thirteen_does_not_reuse_doctors_asset_drift() -> None:






    assert cli.EXIT_MODEL_CODE_DRIFT != cli.EXIT_DRIFT
    assert cli.EXIT_DRIFT == 10


def test_five_through_nine_headroom_is_only_partly_spent() -> None:






    named = {
        value
        for name, value in vars(cli).items()
        if name.startswith("EXIT_") and isinstance(value, int)
    }
    for headroom in (7, 8, 9):
        assert headroom not in PRE_EXISTING_ALLOCATION
        assert headroom not in named, f"{headroom} must remain verdict-band headroom"


def test_every_named_exit_constant_carries_exactly_one_meaning() -> None:







    meanings = {
        "EXIT_GENERATOR": "generator invariant failed",
        "EXIT_QUARANTINE": "checker disagreed with ground truth",
        "EXIT_CHECKER_DEFECT": "checker disagreed with ground truth",
        "EXIT_DRIFT": "assets drift",
        "EXIT_COLLISION": "unmanaged file blocked a write",
        "EXIT_NO_INSTALL": "no install manifest",
        "EXIT_MODEL_CODE_DRIFT": "generated code no longer matches its model",
        "EXIT_EXPERIMENT_OPEN": "an experiment obligation is undischarged",
        "EXIT_SESSION_NOT_ACCEPTED": "a session terminated without acceptance",
        "EXIT_REVIEW_INCONCLUSIVE": "a completed panel had fewer than three successes",
        "EXIT_WALK_HALTED": "a gated station walk halted before completing its selection",
        "EXIT_EVOLUTION_OPERATIONS_GATED": (
            "a well-formed v2 operation delta gnd evolve does not own"
        ),
        "EXIT_USAGE": "usage error",
        "EXIT_NO_INPUT": "a required input artifact is missing",
        "EXIT_INTERNAL": "internal error",
        "EXIT_IO": "IO error",
    }
    by_value: dict[int, set[str]] = {}
    for name, meaning in meanings.items():
        by_value.setdefault(getattr(cli, name), set()).add(meaning)
    for value, distinct in by_value.items():
        assert len(distinct) == 1, f"exit {value} carries two meanings: {distinct}"
    
    
    named = {
        name
        for name, value in vars(cli).items()
        if name.startswith("EXIT_") and isinstance(value, int)
    }
    assert named == set(meanings), f"unaccounted exit constants: {named ^ set(meanings)}"








_RETURNED_66 = re.compile(r"^(?!\s*#).*\breturn\s+\(?\s*66\b", re.MULTILINE)
_ASSIGNED_66 = re.compile(r"^(\w+)\s*=\s*66\b", re.MULTILINE)


def test_no_bare_sixty_six_literal_remains_in_the_cli() -> None:












    assert _RETURNED_66.search("        return 66\n"), (
        "the bare-literal pattern does not match a bare literal; this guard "
        "cannot fail and proves nothing"
    )
    assert _RETURNED_66.search("        return (66, 'missing')\n")

    
    
    
    
    
    for source, label in ((CLI_SOURCE, "cli.py"), (EXITS_SOURCE, "exits.py")):
        offenders = _RETURNED_66.findall(source)
        assert not offenders, f"a bare 66 literal is back in {label}: {offenders}"

    assigned = _ASSIGNED_66.findall(CLI_SOURCE) + _ASSIGNED_66.findall(EXITS_SOURCE)
    assert assigned == ["EXIT_NO_INPUT"], (
        f"66 is assigned to {assigned}; exactly one name may hold it, in exactly "
        "one home"
    )


def test_the_module_docstring_justifies_both_new_names() -> None:





    docstring = cli.__doc__ or ""
    assert "14 (EXIT_EXPERIMENT_OPEN)" in docstring
    assert "masquerade" in docstring.split("14 (EXIT_EXPERIMENT_OPEN)")[1][:900]
    assert "66 (EX_NOINPUT)" in docstring
    assert "masquerade" in docstring.split("66 (EX_NOINPUT)")[1][:900]
    
    assert "13 (EXIT_MODEL_CODE_DRIFT)" in docstring
    assert "masquerade" in docstring.split("13 (EXIT_MODEL_CODE_DRIFT)")[1][:900]
    assert "15 (EXIT_SESSION_NOT_ACCEPTED)" in docstring
    assert "masquerade" in docstring.split("15 (EXIT_SESSION_NOT_ACCEPTED)")[1][:900]
    
    assert "16 (EXIT_REVIEW_INCONCLUSIVE)" in docstring
    assert "masquerade" in docstring.split("16 (EXIT_REVIEW_INCONCLUSIVE)")[1][:900]







def test_the_experiment_outcome_precedence_is_seventy_four_over_everything() -> None:

    assert (
        cli._experiment_outcome(["io"], ["missing"], ["ill"], ["open"]) == cli.EXIT_IO
    )


def test_a_missing_artifact_outranks_an_ill_formed_one() -> None:

    assert (
        cli._experiment_outcome([], ["missing"], ["ill"], ["open"]) == cli.EXIT_NO_INPUT
    )


def test_an_ill_formed_spec_outranks_an_open_obligation() -> None:

    assert cli._experiment_outcome([], [], ["ill"], ["open"]) == 3


def test_an_undischarged_obligation_is_band_fourteen() -> None:

    assert (
        cli._experiment_outcome([], [], [], ["open"]) == cli.EXIT_EXPERIMENT_OPEN
    )


def test_everything_discharged_is_zero() -> None:
    assert cli._experiment_outcome([], [], [], []) == 0







def test_init_then_validate_round_trips_at_exit_zero(tmp_path: Path) -> None:
    assert main(["exp", "init", "EXP-001-probe", "--out", str(tmp_path)]) == 0
    spec = tmp_path / "EXP-001-probe" / "SPEC.md"
    assert spec.is_file()
    assert main(["exp", "validate", str(tmp_path / "EXP-001-probe")]) == 0


def test_init_records_the_questions_it_was_given(tmp_path: Path) -> None:
    assert (
        main(
            [
                "exp",
                "init",
                "EXP-002-two",
                "--out",
                str(tmp_path),
                "--question",
                "Q1=Does fresh generation conform?",
                "--question",
                "Q2=Does a stale rename get caught?",
            ]
        )
        == 0
    )
    from gnd.exp.spec import read_spec

    spec = read_spec(tmp_path / "EXP-002-two" / "SPEC.md")
    assert [q.id for q in spec.questions] == ["Q1", "Q2"]


def test_re_initialising_an_existing_experiment_exits_eleven_and_destroys_nothing(
    tmp_path: Path,
) -> None:

    assert main(["exp", "init", "EXP-001-probe", "--out", str(tmp_path)]) == 0
    spec = tmp_path / "EXP-001-probe" / "SPEC.md"
    before = spec.read_bytes()
    (tmp_path / "EXP-001-probe" / "evidence.txt").write_text("kept\n", encoding="utf-8")

    assert main(["exp", "init", "EXP-001-probe", "--out", str(tmp_path)]) == (
        cli.EXIT_COLLISION
    )
    assert spec.read_bytes() == before
    assert (tmp_path / "EXP-001-probe" / "evidence.txt").is_file(), (
        "re-init destroyed recorded evidence — there is deliberately no --force "
        "here for exactly this reason"
    )


def test_two_inits_of_one_declaration_write_identical_bytes(tmp_path: Path) -> None:


    for index in ("EXP-001-probe", "EXP-002-probe"):
        assert main(["exp", "init", index, "--out", str(tmp_path)]) == 0
    first = (tmp_path / "EXP-001-probe" / "SPEC.md").read_text(encoding="utf-8")
    second = (tmp_path / "EXP-002-probe" / "SPEC.md").read_text(encoding="utf-8")
    assert first.replace("EXP-001", "EXP-002") == second


def test_failed_init_removes_its_staging_directory_and_can_be_retried(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    real_replace = cli.os.replace

    def fail_publication(source: str | Path, destination: str | Path) -> None:
        if Path(destination).name == "EXP-001-probe":
            raise OSError("simulated publication failure")
        real_replace(source, destination)

    monkeypatch.setattr(cli.os, "replace", fail_publication)
    assert main(["exp", "init", "EXP-001-probe", "--out", str(tmp_path)]) == cli.EXIT_IO
    assert not (tmp_path / "EXP-001-probe").exists()
    assert not list(tmp_path.glob(".EXP-001-probe.staging-*"))

    monkeypatch.setattr(cli.os, "replace", real_replace)
    assert main(["exp", "init", "EXP-001-probe", "--out", str(tmp_path)]) == 0
    assert (tmp_path / "EXP-001-probe" / "SPEC.md").is_file()


def test_validate_over_a_directory_with_no_spec_exits_sixty_six(tmp_path: Path) -> None:

    assert main(["exp", "validate", str(tmp_path)]) == cli.EXIT_NO_INPUT


def test_validate_over_an_unknown_frontmatter_key_exits_three(tmp_path: Path) -> None:
    assert main(["exp", "init", "EXP-001-probe", "--out", str(tmp_path)]) == 0
    spec = tmp_path / "EXP-001-probe" / "SPEC.md"
    spec.write_text(
        spec.read_text(encoding="utf-8").replace("kind: codegen", "kind: codegen\nverdict: pass"),
        encoding="utf-8",
    )
    assert main(["exp", "validate", str(tmp_path / "EXP-001-probe")]) == 3


def test_validate_over_an_unfenced_spec_exits_three(tmp_path: Path) -> None:
    root = tmp_path / "EXP-001-probe"
    root.mkdir()
    (root / "SPEC.md").write_text("# not a spec\n", encoding="utf-8")
    assert main(["exp", "validate", str(root)]) == 3


def test_validate_refuses_a_spec_whose_id_disagrees_with_its_directory(
    tmp_path: Path,
) -> None:

    assert main(["exp", "init", "EXP-001-probe", "--out", str(tmp_path)]) == 0
    (tmp_path / "EXP-001-probe").rename(tmp_path / "EXP-009-elsewhere")
    assert main(["exp", "validate", str(tmp_path / "EXP-009-elsewhere")]) == 3


def test_close_refuses_a_spec_whose_id_disagrees_with_its_directory(
    tmp_path: Path,
) -> None:
    assert (
        main(
            [
                "exp",
                "init",
                "EXP-001-probe",
                "--out",
                str(tmp_path),
                "--kind",
                "analysis",
            ]
        )
        == 0
    )
    root = tmp_path / "EXP-001-probe"
    (root / "CONCLUSIONS.md").write_text(
        "---\nid: EXP-001-probe\nresolves:\n"
        "- id: Q1\n  outcome: answered\n  evidence: SPEC.md\n"
        "---\n\n# Conclusions\n",
        encoding="utf-8",
    )
    moved = tmp_path / "EXP-009-elsewhere"
    root.rename(moved)

    assert main(["exp", "close", str(moved)]) == 3


def test_a_malformed_experiment_id_is_a_usage_error(tmp_path: Path) -> None:

    with pytest.raises(SystemExit) as caught:
        main(["exp", "init", "../escape", "--out", str(tmp_path)])
    assert caught.value.code == cli.EXIT_USAGE
    assert not list(tmp_path.iterdir()), "a refused id still wrote something"


def test_a_malformed_question_argument_is_a_usage_error(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as caught:
        main(
            ["exp", "init", "EXP-001-probe", "--out", str(tmp_path), "--question", "no-equals"]
        )
    assert caught.value.code == cli.EXIT_USAGE


def test_exp_without_a_subcommand_is_a_usage_error() -> None:
    with pytest.raises(SystemExit) as caught:
        main(["exp"])
    assert caught.value.code == cli.EXIT_USAGE


@pytest.mark.skipif(os.getuid() == 0, reason="root ignores directory permissions")
def test_an_unwritable_output_root_exits_seventy_four(tmp_path: Path) -> None:

    root = tmp_path / "readonly"
    root.mkdir()
    root.chmod(stat.S_IRUSR | stat.S_IXUSR)
    try:
        assert main(["exp", "init", "EXP-001-probe", "--out", str(root)]) == cli.EXIT_IO
    finally:
        root.chmod(stat.S_IRWXU)







def _help_text(capsys: pytest.CaptureFixture[str], argv: list[str]) -> str:
    with pytest.raises(SystemExit):
        main(argv)
    return " ".join(capsys.readouterr().out.split())


def test_the_exp_init_description_enumerates_every_exit_path(
    capsys: pytest.CaptureFixture[str],
) -> None:
    text = _help_text(capsys, ["exp", "init", "--help"])
    for code in ("Exits 0", " 3 ", " 11 ", " 64 ", " 74 "):
        assert code in text, f"gnd exp init --help does not mention {code.strip()}"


def test_the_exp_validate_description_enumerates_every_exit_path(
    capsys: pytest.CaptureFixture[str],
) -> None:
    text = _help_text(capsys, ["exp", "validate", "--help"])
    for code in ("Exits 0", " 3 ", " 64 ", " 66 "):
        assert code in text, f"gnd exp validate --help does not mention {code.strip()}"


def test_the_exp_run_help_exposes_only_closed_adapter_and_tightening_controls(
    capsys: pytest.CaptureFixture[str],
) -> None:
    text = _help_text(capsys, ["exp", "run", "--help"])
    assert "--adapter {claude,codex}" in text
    assert "--wall-seconds" in text
    for forbidden in ("--executable", "--provider", "--model", "--argv", "--max-attempts"):
        assert forbidden not in text
    for code in ("Exits 0", " 3 ", " 15 ", " 64 ", " 66 ", " 70 ", " 74 "):
        assert code in text, f"gnd exp run --help does not mention {code.strip()}"


def test_the_exp_run_handler_is_one_thin_programmatic_bridge() -> None:
    source = inspect.getsource(cli._cmd_exp_run)
    assert source.count("asyncio.run(") == 1
    assert source.count("run_session(") == 1
    assert "_cmd_exp_close" not in source

    main_source = inspect.getsource(main)
    assert "_BandSafeParser(" in main_source
