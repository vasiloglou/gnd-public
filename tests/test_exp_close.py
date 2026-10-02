


































from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pytest

from gnd import cli
from gnd.cli import EXIT_EXPERIMENT_OPEN, EXIT_NO_INPUT, main
from gnd.exp.close import (
    CloseFinding,
    CloseFindingKind,
    CloseResult,
    close_outcome,
    evaluate_close,
)
from gnd.exp.conclusions import (
    ConclusionsError,
    ExperimentConclusions,
    Outcome,
    Resolution,
    read_conclusions,
)
from gnd.exp.frontmatter import render_frontmatter
from gnd.exp.spec import read_spec

VALID = """---
id: EXP-001-probe
resolves:
  - id: Q1
    outcome: answered
    evidence: results/run.json
  - id: Q2
    outcome: unanswered
    evidence: results/run.json
    reason: the generator never reached the rename case, so nothing was measured
---

# EXP-001-probe conclusions
"""


def _conclusions(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "CONCLUSIONS.md"
    path.write_text(text, encoding="utf-8")
    return path







def test_the_outcome_vocabulary_is_closed_at_exactly_three_members() -> None:






    from typing import get_args

    assert set(get_args(Outcome)) == {"answered", "unanswered", "invalidated"}
    assert len(get_args(Outcome)) == 3


def test_an_answered_resolution_with_a_pointer_validates(tmp_path: Path) -> None:
    conclusions = read_conclusions(_conclusions(tmp_path, VALID))

    assert isinstance(conclusions, ExperimentConclusions)
    assert conclusions.id == "EXP-001-probe"
    assert [r.id for r in conclusions.resolves] == ["Q1", "Q2"]
    assert conclusions.resolves[0].outcome == "answered"
    assert conclusions.resolves[0].evidence == "results/run.json"


def test_an_unanswered_resolution_with_a_reason_is_a_valid_record(
    tmp_path: Path,
) -> None:







    text = VALID.replace("outcome: answered", "outcome: unanswered").replace(
        "    evidence: results/run.json\n  - id: Q2",
        "    evidence: results/run.json\n    reason: the run was aborted before "
        "any measurement was taken\n  - id: Q2",
    )

    conclusions = read_conclusions(_conclusions(tmp_path, text))

    assert [r.outcome for r in conclusions.resolves] == ["unanswered", "unanswered"]
    assert all(r.reason for r in conclusions.resolves), (
        "an unanswered resolution must carry its reason through the load"
    )


def test_an_unanswered_resolution_without_a_reason_is_refused(tmp_path: Path) -> None:

    text = VALID.replace(
        "    reason: the generator never reached the rename case, so nothing was "
        "measured\n",
        "",
    )

    with pytest.raises(ConclusionsError) as caught:
        read_conclusions(_conclusions(tmp_path, text))
    assert "reason" in str(caught.value).lower()


def test_an_invalidated_resolution_without_a_reason_is_refused(tmp_path: Path) -> None:
    text = VALID.replace("outcome: answered", "outcome: invalidated")

    with pytest.raises(ConclusionsError) as caught:
        read_conclusions(_conclusions(tmp_path, text))
    assert "reason" in str(caught.value).lower()


def test_an_invalidated_resolution_with_a_reason_validates(tmp_path: Path) -> None:

    text = VALID.replace(
        "    outcome: answered\n    evidence: results/run.json\n",
        "    outcome: invalidated\n    evidence: results/run.json\n"
        "    reason: the fixture model changed under the run, so the measurement "
        "is not about the declared question\n",
    )

    conclusions = read_conclusions(_conclusions(tmp_path, text))

    assert conclusions.resolves[0].outcome == "invalidated"


def test_an_outcome_outside_the_closed_set_is_refused(tmp_path: Path) -> None:
    text = VALID.replace("outcome: answered", "outcome: succeeded")

    with pytest.raises(ConclusionsError) as caught:
        read_conclusions(_conclusions(tmp_path, text))
    assert "succeeded" in str(caught.value)


def test_an_empty_evidence_pointer_is_unrepresentable(tmp_path: Path) -> None:







    text = VALID.replace("    evidence: results/run.json\n    reason:", '    evidence: ""\n    reason:')

    with pytest.raises(ConclusionsError) as caught:
        read_conclusions(_conclusions(tmp_path, text))
    assert "evidence" in str(caught.value)


def test_a_whitespace_only_evidence_pointer_is_unrepresentable(tmp_path: Path) -> None:

    text = VALID.replace(
        "    evidence: results/run.json\n    reason:", '    evidence: "   "\n    reason:'
    )

    with pytest.raises(ConclusionsError) as caught:
        read_conclusions(_conclusions(tmp_path, text))
    assert "evidence" in str(caught.value)


def test_a_resolution_without_an_evidence_pointer_is_refused(tmp_path: Path) -> None:

    text = VALID.replace("    evidence: results/run.json\n    reason:", "    reason:")

    with pytest.raises(ConclusionsError) as caught:
        read_conclusions(_conclusions(tmp_path, text))
    assert "evidence" in str(caught.value)


def test_duplicate_resolution_ids_are_refused(tmp_path: Path) -> None:





    text = VALID.replace("  - id: Q2", "  - id: Q1")

    with pytest.raises(ConclusionsError) as caught:
        read_conclusions(_conclusions(tmp_path, text))
    message = str(caught.value)
    assert "Q1" in message
    assert "duplicate" in message.lower()


def test_an_unknown_key_in_a_resolution_is_refused(tmp_path: Path) -> None:






    text = VALID.replace(
        "    outcome: answered\n", "    outcome: answered\n    passed: true\n"
    )

    with pytest.raises(ConclusionsError) as caught:
        read_conclusions(_conclusions(tmp_path, text))
    assert "passed" in str(caught.value)


def test_an_unknown_top_level_key_is_refused(tmp_path: Path) -> None:
    text = VALID.replace("id: EXP-001-probe", "id: EXP-001-probe\nverdict: green")

    with pytest.raises(ConclusionsError) as caught:
        read_conclusions(_conclusions(tmp_path, text))
    assert "verdict" in str(caught.value)


def test_every_non_answering_outcome_is_obligated_to_explain_itself() -> None:








    from typing import get_args

    import pydantic

    for outcome in get_args(Outcome):
        if outcome == "answered":
            assert Resolution(id="Q1", outcome=outcome, evidence="run.json")
            continue
        with pytest.raises(pydantic.ValidationError):
            Resolution(id="Q1", outcome=outcome, evidence="run.json")
        assert Resolution(
            id="Q1", outcome=outcome, evidence="run.json", reason="measured nothing"
        )


def test_no_field_in_the_record_expresses_success_or_failure() -> None:








    forbidden = {"succeeded", "success", "passed", "failed", "ok", "result", "verdict"}
    fields = set(Resolution.model_fields) | set(ExperimentConclusions.model_fields)

    assert not (fields & forbidden), (
        f"the conclusions record grew a success field {sorted(fields & forbidden)}; "
        f"the gate enforces completeness and honesty, never a positive result"
    )


def test_a_missing_conclusions_file_raises_rather_than_reading_as_empty(
    tmp_path: Path,
) -> None:

    with pytest.raises(ConclusionsError):
        read_conclusions(tmp_path / "CONCLUSIONS.md")


def test_an_unfenced_conclusions_document_is_refused(tmp_path: Path) -> None:
    with pytest.raises(ConclusionsError):
        read_conclusions(_conclusions(tmp_path, "# just prose, no frontmatter\n"))


def test_an_anchor_alias_conclusions_block_is_refused(tmp_path: Path) -> None:

    text = """---
id: &anchor EXP-001-probe
resolves:
  - id: Q1
    outcome: answered
    evidence: *anchor
---

# body
"""

    with pytest.raises(ConclusionsError):
        read_conclusions(_conclusions(tmp_path, text))












def _experiment(
    parent: Path,
    experiment_id: str = "EXP-001-probe",
    *,
    kind: str = "analysis",
    declared: Sequence[str] = ("Q1", "Q2"),
    resolved: Sequence[str] | None = None,
    outcome: str = "answered",
    evidence: str = "results/run.json",
    follows: Sequence[str] = (),
    write_conclusions: bool = True,
) -> Path:






















    root = parent / experiment_id
    (root / "results").mkdir(parents=True)
    (root / "results" / "run.json").write_text("{}\n", encoding="utf-8")

    spec = {
        "id": experiment_id,
        "kind": kind,
        "title": "does the emitter agree with the model",
        "questions": [{"id": q, "text": f"what does {q} establish?"} for q in declared],
        "follows": list(follows),
    }
    (root / "SPEC.md").write_text(
        render_frontmatter(spec, f"# {experiment_id}\n"), encoding="utf-8"
    )

    if write_conclusions:
        ids = list(declared) if resolved is None else list(resolved)
        resolutions: list[dict[str, str]] = []
        for question in ids:
            entry = {"id": question, "outcome": outcome, "evidence": evidence}
            if outcome != "answered":
                entry["reason"] = "the run did not reach this case, so nothing was measured"
            resolutions.append(entry)
        (root / "CONCLUSIONS.md").write_text(
            render_frontmatter(
                {"id": experiment_id, "resolves": resolutions},
                f"# {experiment_id} conclusions\n",
            ),
            encoding="utf-8",
        )
    return root


def test_a_complete_experiment_closes_at_exit_zero(tmp_path: Path, capsys) -> None:
    root = _experiment(tmp_path)

    assert main(["exp", "close", str(root)]) == 0
    assert "CLOSED" in capsys.readouterr().out


def test_an_experiment_with_no_conclusions_is_refused_at_fourteen(
    tmp_path: Path, capsys
) -> None:








    root = _experiment(tmp_path, write_conclusions=False)

    assert main(["exp", "close", str(root)]) == EXIT_EXPERIMENT_OPEN
    assert "CONCLUSIONS.md" in capsys.readouterr().out


def test_a_forgotten_question_id_is_refused_and_named(tmp_path: Path, capsys) -> None:

    root = _experiment(tmp_path, declared=("Q1", "Q2"), resolved=("Q1",))

    assert main(["exp", "close", str(root)]) == EXIT_EXPERIMENT_OPEN
    assert "Q2" in capsys.readouterr().out, (
        "the forgotten id must be NAMED, not merely counted — an author cannot "
        "fix 'one question is unresolved'"
    )


def test_the_forgotten_id_is_carried_in_a_structured_finding(tmp_path: Path) -> None:








    root = _experiment(tmp_path, declared=("Q1", "Q2"), resolved=("Q1",))
    result = evaluate_close(
        read_spec(root / "SPEC.md"),
        read_conclusions(root / "CONCLUSIONS.md"),
        root / "SPEC.md",
    )

    assert [(f.kind, f.id) for f in result.findings] == [("forgotten-question", "Q2")]


def test_an_orphan_resolution_is_refused_and_named(tmp_path: Path, capsys) -> None:






    root = _experiment(tmp_path, declared=("Q1",), resolved=("Q1", "Q9"))

    assert main(["exp", "close", str(root)]) == EXIT_EXPERIMENT_OPEN
    assert "Q9" in capsys.readouterr().out


def test_the_orphan_id_is_carried_in_a_structured_finding(tmp_path: Path) -> None:
    root = _experiment(tmp_path, declared=("Q1",), resolved=("Q1", "Q9"))
    result = evaluate_close(
        read_spec(root / "SPEC.md"),
        read_conclusions(root / "CONCLUSIONS.md"),
        root / "SPEC.md",
    )

    assert [(f.kind, f.id) for f in result.findings] == [("orphan-resolution", "Q9")]


def test_both_set_differences_are_reported_together(tmp_path: Path) -> None:






    root = _experiment(tmp_path, declared=("Q1", "Q2"), resolved=("Q1", "Q9"))
    result = evaluate_close(
        read_spec(root / "SPEC.md"),
        read_conclusions(root / "CONCLUSIONS.md"),
        root / "SPEC.md",
    )

    assert {(f.kind, f.id) for f in result.findings} == {
        ("forgotten-question", "Q2"),
        ("orphan-resolution", "Q9"),
    }


def test_an_evidence_pointer_naming_a_directory_is_refused(
    tmp_path: Path, capsys
) -> None:





    root = _experiment(tmp_path, evidence="results")

    assert main(["exp", "close", str(root)]) == EXIT_EXPERIMENT_OPEN
    assert "results" in capsys.readouterr().out


def test_an_evidence_pointer_naming_a_missing_file_is_refused(
    tmp_path: Path, capsys
) -> None:
    root = _experiment(tmp_path, evidence="results/never-written.json")

    assert main(["exp", "close", str(root)]) == EXIT_EXPERIMENT_OPEN
    assert "never-written.json" in capsys.readouterr().out


def test_an_escaping_evidence_pointer_is_refused(tmp_path: Path) -> None:

    root = _experiment(tmp_path, evidence="../../etc/passwd")
    result = evaluate_close(
        read_spec(root / "SPEC.md"),
        read_conclusions(root / "CONCLUSIONS.md"),
        root / "SPEC.md",
    )

    assert {f.kind for f in result.findings} == {"unresolvable-evidence"}


def test_a_follows_reference_to_a_concluded_experiment_closes_at_zero(
    tmp_path: Path,
) -> None:

    _experiment(tmp_path, "EXP-000-seed", declared=("Q1",))
    root = _experiment(tmp_path, follows=("EXP-000-seed",))

    assert main(["exp", "close", str(root)]) == 0


def test_a_follows_reference_to_an_absent_experiment_is_refused(
    tmp_path: Path, capsys
) -> None:
    root = _experiment(tmp_path, follows=("EXP-999-absent",))

    assert main(["exp", "close", str(root)]) == EXIT_EXPERIMENT_OPEN
    assert "EXP-999-absent" in capsys.readouterr().out


def test_a_follows_reference_to_an_unconcluded_experiment_is_refused(
    tmp_path: Path, capsys
) -> None:






    _experiment(tmp_path, "EXP-000-seed", declared=("Q1",), write_conclusions=False)
    root = _experiment(tmp_path, follows=("EXP-000-seed",))

    assert main(["exp", "close", str(root)]) == EXIT_EXPERIMENT_OPEN
    assert "EXP-000-seed" in capsys.readouterr().out


def test_a_traversing_follows_reference_is_refused_without_touching_the_disk(
    tmp_path: Path,
) -> None:







    hostile_references = ("../../../etc", "C:\\evil", "/etc/passwd", "EXP-001-probe/..")
    for index, hostile in enumerate(hostile_references):
        
        
        
        root = _experiment(tmp_path / f"case{index}", follows=(hostile,))
        result = evaluate_close(
            read_spec(root / "SPEC.md"),
            read_conclusions(root / "CONCLUSIONS.md"),
            root / "SPEC.md",
        )
        assert {f.kind for f in result.findings} == {"unresolved-reference"}, (
            f"{hostile!r} was not refused as a reference"
        )


def test_a_missing_spec_exits_sixty_six(tmp_path: Path) -> None:






    root = _experiment(tmp_path)
    (root / "SPEC.md").unlink()

    assert main(["exp", "close", str(root)]) == EXIT_NO_INPUT


def test_an_unparseable_conclusions_document_exits_three(tmp_path: Path) -> None:
    root = _experiment(tmp_path)
    (root / "CONCLUSIONS.md").write_text("# no frontmatter here\n", encoding="utf-8")

    assert main(["exp", "close", str(root)]) == 3


def test_an_unparseable_spec_exits_three(tmp_path: Path) -> None:
    root = _experiment(tmp_path)
    (root / "SPEC.md").write_text("# no frontmatter here\n", encoding="utf-8")

    assert main(["exp", "close", str(root)]) == 3


def test_conclusions_declaring_another_experiments_id_exits_three(
    tmp_path: Path, capsys
) -> None:








    root = _experiment(tmp_path)
    text = (root / "CONCLUSIONS.md").read_text(encoding="utf-8")
    (root / "CONCLUSIONS.md").write_text(
        text.replace("id: EXP-001-probe", "id: EXP-002-elsewhere", 1), encoding="utf-8"
    )

    assert main(["exp", "close", str(root)]) == 3
    assert "EXP-002-elsewhere" in capsys.readouterr().out







def test_the_finding_kinds_are_a_closed_published_set() -> None:









    from typing import get_args

    assert set(get_args(CloseFindingKind)) == {
        "forgotten-question",
        "orphan-resolution",
        "unresolvable-evidence",
        "unresolved-reference",
        "unmet-conformance",
        "unrecorded-launch",
        "unaccepted-session",
    }


def test_every_published_finding_kind_is_named_by_a_construction_in_close_py() -> None:

















    import inspect
    from typing import get_args

    from gnd.exp import close as close_module

    source = inspect.getsource(close_module)
    for kind in get_args(CloseFindingKind):
        assert f'kind="{kind}"' in source, (
            f"{kind!r} is published in CloseFindingKind but no branch in "
            f"close.py constructs a finding with it"
        )


def test_close_outcome_returns_the_shipped_band_constant_not_a_local_literal() -> None:

    clean = CloseResult(findings=[], declared=("Q1",), resolved=("Q1",))
    assert close_outcome(clean) == 0

    finding = CloseFinding(
        kind="forgotten-question", id="Q1", message="Q1 was never resolved"
    )
    open_result = CloseResult(findings=[finding], declared=("Q1",), resolved=())
    assert close_outcome(open_result) == cli.EXIT_EXPERIMENT_OPEN
    assert cli.EXIT_EXPERIMENT_OPEN == 14


def test_close_outcome_states_its_precedence_and_why_band_ten_is_not_reused() -> None:

    doc = close_outcome.__doc__ or ""

    assert "precedence" in doc.lower()
    assert "10" in doc
    assert "drift" in doc.lower()


def test_no_parameter_in_close_defaults_a_gate_input_to_a_passing_value() -> None:
















    import inspect

    from gnd.exp import close as close_module

    inspected: list[str] = []
    for name, function in vars(close_module).items():
        if not inspect.isfunction(function) or name.startswith("_"):
            continue
        if function.__module__ != close_module.__name__:
            continue
        inspected.append(name)
        for parameter in inspect.signature(function).parameters.values():
            assert parameter.default is not True, (
                f"{name}({parameter.name}=True) defaults a gate input to a passing "
                f"value — the G-17 seam must be empty, not permissive"
            )

    assert {"evaluate_close", "close_outcome"} <= set(inspected), (
        f"the scan inspected {inspected} — a guard that examines no function "
        f"reports green over nothing"
    )


def test_evaluate_close_takes_no_conformance_argument() -> None:

    import inspect

    from gnd.exp import close as close_module

    names = set(inspect.signature(evaluate_close).parameters)
    assert not any("conform" in name for name in names), (
        "conformance arrives in plan 03-06 with no default; it is not this "
        "plan's to wire, and a defaulted stub would pre-answer it"
    )
    source = Path(close_module.__file__).read_text(encoding="utf-8")
    assert "03-06" in source, (
        "the empty seam must NAME its owner, or an absent branch is "
        "indistinguishable from a forgotten one"
    )


def test_the_gate_never_reads_an_outcome_value_to_decide_the_verdict(
    tmp_path: Path,
) -> None:






    for outcome in ("answered", "unanswered", "invalidated"):
        root = _experiment(tmp_path / outcome, outcome=outcome)
        assert main(["exp", "close", str(root)]) == 0, (
            f"outcome {outcome!r} changed the verdict; the gate enforces "
            f"completeness and honesty, never a positive result (G-12)"
        )
