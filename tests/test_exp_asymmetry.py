



















































from __future__ import annotations

import difflib
import json
from collections.abc import Sequence
from pathlib import Path

import pytest

from gnd.cli import EXIT_EXPERIMENT_OPEN, main
from gnd.exp.conclusions import read_conclusions
from gnd.exp.frontmatter import render_frontmatter
from gnd.exp.session_store import SessionOutcome, SessionResult
from gnd.exp.spec import SpecError, read_spec

DECLARED: tuple[str, ...] = ("Q1", "Q2", "Q3")

                                                                              
                                                                               
                                                                               
                                                                             
                         
FORGOTTEN: str = "Q2"


def _experiment(
    parent: Path,
    *,
    resolved: Sequence[str],
    outcomes: Sequence[str] | None = None,
) -> Path:







    root = parent / "EXP-001-probe"
    (root / "results").mkdir(parents=True)
    (root / "results" / "run.json").write_text('{"cases": 0}\n', encoding="utf-8")

    (root / "SPEC.md").write_text(
        render_frontmatter(
            {
                "id": "EXP-001-probe",
                                                                               
                                                                              
                                                                             
                                                                              
                                                                                
                                                                                
                                           
                "kind": "analysis",
                "title": "does the emitter agree with the model",
                "questions": [{"id": q, "text": f"what does {q} establish?"} for q in DECLARED],
                "follows": [],
            },
            "# EXP-001-probe\n",
        ),
        encoding="utf-8",
    )

    chosen = list(outcomes) if outcomes is not None else ["unanswered"] * len(resolved)
    resolutions = []
    for question, outcome in zip(resolved, chosen, strict=True):
        entry = {"id": question, "outcome": outcome, "evidence": "results/run.json"}
        if outcome != "answered":
            entry["reason"] = "the run was stopped before this case, so nothing was measured"
        resolutions.append(entry)

    (root / "CONCLUSIONS.md").write_text(
        render_frontmatter(
            {"id": "EXP-001-probe", "resolves": resolutions},
            "# EXP-001-probe conclusions\n",
        ),
        encoding="utf-8",
    )
    return root


                                                                               
                              
                                                                               


def test_an_experiment_whose_every_question_is_unanswered_closes_at_exit_zero(
    tmp_path: Path, capsys
) -> None:







    root = _experiment(tmp_path, resolved=DECLARED)

    assert main(["exp", "close", str(root)]) == 0, (
        "an experiment that answered every declared question with an honest, "
        "reasoned, cited 'unanswered' must CLOSE — the gate enforces "
        "completeness and honesty, never a positive result (G-12)"
    )
    out = capsys.readouterr().out
    assert "CLOSED" in out
    assert out.count("unanswered") >= len(DECLARED), (
        "the fixture must actually be all-unanswered, or this test passes over "
        "an experiment that is not the one it names"
    )


def test_the_same_experiment_missing_exactly_one_declared_id_is_refused_at_fourteen(
    tmp_path: Path, capsys
) -> None:

    root = _experiment(tmp_path, resolved=[q for q in DECLARED if q != FORGOTTEN])

    assert main(["exp", "close", str(root)]) == EXIT_EXPERIMENT_OPEN, (
        "an experiment that quietly dropped a question it set out to answer "
        "must be REFUSED; the gate's job is exactly this"
    )
    assert FORGOTTEN in capsys.readouterr().out


def test_the_two_halves_differ_only_in_the_presence_of_that_one_id(
    tmp_path: Path,
) -> None:









    closing = _experiment(tmp_path / "closing", resolved=DECLARED)
    refused = _experiment(tmp_path / "refused", resolved=[q for q in DECLARED if q != FORGOTTEN])

    assert (closing / "SPEC.md").read_bytes() == (refused / "SPEC.md").read_bytes(), (
        "the two halves must declare the SAME questions; a differing spec would "
        "make the failing half fail for a reason the test does not name"
    )

                                                                          
    closing_resolutions = read_conclusions(closing / "CONCLUSIONS.md").resolves
    refused_resolutions = read_conclusions(refused / "CONCLUSIONS.md").resolves
    assert [r.id for r in closing_resolutions] == list(DECLARED)
    assert [r.model_dump() for r in closing_resolutions if r.id != FORGOTTEN] == [
        r.model_dump() for r in refused_resolutions
    ], "the surviving resolutions must be identical between the halves"

                                                                              
                                                                          
    diff = list(
        difflib.ndiff(
            (closing / "CONCLUSIONS.md").read_text(encoding="utf-8").splitlines(),
            (refused / "CONCLUSIONS.md").read_text(encoding="utf-8").splitlines(),
        )
    )
    added = [line[2:] for line in diff if line.startswith("+ ")]
    removed = [line[2:] for line in diff if line.startswith("- ")]

    assert added == [], f"the failing half gained lines it should not have: {added}"
    assert len(removed) == 4, (
        f"exactly one resolution block (its four keys) should be gone, got {removed}"
    )
    assert sum(FORGOTTEN in line for line in removed) == 1, (
        f"the removed block must be {FORGOTTEN}'s, got {removed}"
    )


def test_a_mixed_outcome_experiment_closes_at_exit_zero(tmp_path: Path) -> None:






    root = _experiment(
        tmp_path,
        resolved=DECLARED,
        outcomes=("answered", "unanswered", "invalidated"),
    )

    assert main(["exp", "close", str(root)]) == 0


@pytest.mark.parametrize("disposition", list(SessionOutcome))
def test_every_terminal_session_outcome_is_evidence_not_a_closure_verdict(
    tmp_path: Path,
    disposition: SessionOutcome,
) -> None:


    root = _experiment(tmp_path, resolved=DECLARED)
    accepted = disposition is SessionOutcome.accepted
    result = SessionResult(
        run_id="run-closure-separation",
        disposition=disposition,
        terminal_reason=f"sanitized {disposition.value} terminal reason",
        attempt_count=1,
        best_attempt=1 if accepted else None,
        best_attempt_manifest_sha256="a" * 64 if accepted else None,
        best_candidate_sha256="b" * 64 if accepted else None,
        referenced_evidence_digests={"attempt_manifest_sha256": "c" * 64},
    )
    (root / "results" / "run.json").write_text(
        json.dumps(result.model_dump(mode="json"), sort_keys=True) + "\n",
        encoding="utf-8",
    )

    assert main(["exp", "close", str(root)]) == 0


                                                                               
                   
                                                                               


def test_the_passing_half_is_not_satisfiable_by_a_zero_question_experiment(
    tmp_path: Path,
) -> None:














    root = _experiment(tmp_path, resolved=DECLARED)
    spec = read_spec(root / "SPEC.md")

    assert len(spec.questions) >= 1, "the pin's own fixture declares nothing"
    assert len(spec.questions) == len(DECLARED)
    assert {q.id for q in spec.questions} == set(DECLARED), (
        "the passing verdict must come from resolving REAL declared questions"
    )

    vacuous = tmp_path / "vacuous"
    vacuous.mkdir()
    (vacuous / "SPEC.md").write_text(
        render_frontmatter(
            {
                "id": "EXP-002-vacuous",
                "kind": "analysis",
                "title": "asks nothing",
                "questions": [],
                "follows": [],
            },
            "# EXP-002-vacuous\n",
        ),
        encoding="utf-8",
    )

    with pytest.raises(SpecError) as caught:
        read_spec(vacuous / "SPEC.md")
    assert "at least 1" in str(caught.value) or "min_length" in str(caught.value), (
        "a zero-question spec must be refused at LOAD; if it ever loads, the "
        "close gate becomes a gate that cannot fail and this pin becomes "
        "satisfiable by an experiment that asked nothing"
    )
