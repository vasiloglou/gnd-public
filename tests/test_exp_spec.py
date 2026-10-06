












from __future__ import annotations

from pathlib import Path

import pytest
from support.rf5_sources import cli_sources

from gnd.exp.spec import (
    EXPERIMENT_DIR_PATTERN,
    ExperimentSpec,
    SpecError,
    read_spec,
)

VALID = """---
id: EXP-001-probe
kind: codegen
title: Does the emitter agree with the model
questions:
  - id: Q1
    text: Does fresh generation conform to the model?
  - id: Q2
    text: Does a stale rename get caught?
---

# EXP-001-probe
"""


def _spec(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "SPEC.md"
    path.write_text(text, encoding="utf-8")
    return path


def test_a_valid_spec_yields_its_question_ids_in_declared_order(tmp_path: Path) -> None:
    spec = read_spec(_spec(tmp_path, VALID))

    assert isinstance(spec, ExperimentSpec)
    assert spec.id == "EXP-001-probe"
    assert spec.kind == "codegen"
    assert [q.id for q in spec.questions] == ["Q1", "Q2"], (
        "declared order is not incidental — the close gate reports the FIRST "
        "unresolved question, and a reordered list renames the failure"
    )
    assert spec.follows == []


def test_a_duplicate_question_id_is_refused(tmp_path: Path) -> None:





    text = VALID.replace("  - id: Q2", "  - id: Q1")

    with pytest.raises(SpecError) as caught:
        read_spec(_spec(tmp_path, text))
    message = str(caught.value)
    assert "Q1" in message
    assert "duplicate" in message.lower()


def test_an_unknown_top_level_key_is_refused(tmp_path: Path) -> None:

    text = VALID.replace("kind: codegen", "kind: codegen\nconclusion: shipped")

    with pytest.raises(SpecError) as caught:
        read_spec(_spec(tmp_path, text))
    assert "conclusion" in str(caught.value)


def test_an_unknown_question_key_is_refused(tmp_path: Path) -> None:

    text = VALID.replace(
        "    text: Does a stale rename get caught?",
        "    text: Does a stale rename get caught?\n    answer: yes",
    )

    with pytest.raises(SpecError) as caught:
        read_spec(_spec(tmp_path, text))
    assert "answer" in str(caught.value)


def test_an_empty_question_id_is_refused(tmp_path: Path) -> None:
    text = VALID.replace("  - id: Q2", '  - id: ""')

    with pytest.raises(SpecError) as caught:
        read_spec(_spec(tmp_path, text))
    assert "questions" in str(caught.value)


def test_a_whitespace_only_question_id_is_refused(tmp_path: Path) -> None:

    text = VALID.replace("  - id: Q2", '  - id: "   "')

    with pytest.raises(SpecError) as caught:
        read_spec(_spec(tmp_path, text))
    assert "questions" in str(caught.value)


def test_a_whitespace_only_question_text_is_refused(tmp_path: Path) -> None:
    text = VALID.replace("    text: Does a stale rename get caught?", '    text: "  "')

    with pytest.raises(SpecError) as caught:
        read_spec(_spec(tmp_path, text))
    assert "questions" in str(caught.value)


def test_a_spec_declaring_no_questions_is_refused(tmp_path: Path) -> None:







    text = """---
id: EXP-001-probe
kind: codegen
title: Nothing asked
questions: []
---

body
"""

    with pytest.raises(SpecError) as caught:
        read_spec(_spec(tmp_path, text))
    assert "questions" in str(caught.value)


def test_an_unknown_kind_is_refused(tmp_path: Path) -> None:

    text = VALID.replace("kind: codegen", "kind: vibes")

    with pytest.raises(SpecError) as caught:
        read_spec(_spec(tmp_path, text))
    assert "kind" in str(caught.value)


def test_an_id_that_is_not_a_legal_experiment_directory_name_is_refused(
    tmp_path: Path,
) -> None:

    text = VALID.replace("id: EXP-001-probe", "id: ../escape")

    with pytest.raises(SpecError) as caught:
        read_spec(_spec(tmp_path, text))
    assert "id" in str(caught.value)


def test_the_experiment_dir_pattern_accepts_and_rejects_the_documented_forms() -> None:
    for good in ("EXP-001-probe", "EXP-042-codegen-drift", "EXP-999-a"):
        assert EXPERIMENT_DIR_PATTERN.match(good), good
    for bad in ("EXP-1-probe", "exp-001-probe", "EXP-001-", "EXP-001-Probe", "EXP-001", "../x"):
        assert not EXPERIMENT_DIR_PATTERN.match(bad), bad


def test_an_unparseable_spec_raises_spec_error_not_a_frontmatter_error(
    tmp_path: Path,
) -> None:






    with pytest.raises(SpecError):
        read_spec(_spec(tmp_path, "no fence at all\n"))


def test_spec_error_carries_validation_issues(tmp_path: Path) -> None:

    text = VALID.replace("kind: codegen", "kind: vibes")

    with pytest.raises(SpecError) as caught:
        read_spec(_spec(tmp_path, text))
    issues = caught.value.issues
    assert issues, "SpecError carried no ValidationIssue records"
    assert all(issue.rule_id.startswith("experiment:") for issue in issues)


def test_a_follows_reference_list_is_read(tmp_path: Path) -> None:

    text = VALID.replace(
        "questions:", "follows: [EXP-000-seed]\nquestions:"
    )
    spec = read_spec(_spec(tmp_path, text))
    assert spec.follows == ["EXP-000-seed"]







def test_the_three_replaced_kind_literals_are_gone_from_their_call_sites() -> None:


















    import inspect

    from gnd.exp import close

    cli_source = cli_sources()
    for guard in ('spec.kind != "data-driven"', "spec.kind != 'data-driven'"):
        assert guard not in cli_source, (
            f"{guard} survives in gnd/cli.py; KIND_POLICY is no longer the one "
            f"home for that decision"
        )

    close_source = inspect.getsource(close)
    assert 'CONFORMANCE_GATED_KIND: ExperimentKind = "codegen"' not in close_source, (
        "the conformance-gated kind is hard-coded again beside the table"
    )


def test_kind_policy_is_total_over_the_closed_experiment_vocabulary() -> None:






    from typing import get_args

    from gnd.exp.spec import KIND_POLICY, ExperimentKind

    declared = set(get_args(ExperimentKind))
    assert set(KIND_POLICY) == declared


def test_every_kind_policy_consumer_indexes_the_table() -> None:






    import inspect

    from gnd.exp import close

    cli_source = cli_sources()
    assert "KIND_POLICY[spec.kind].expectation_authorable" in cli_source
    assert "KIND_POLICY[spec.kind].session_runnable" in cli_source
    assert "KIND_POLICY[spec.kind].close_obligations" in inspect.getsource(close)
