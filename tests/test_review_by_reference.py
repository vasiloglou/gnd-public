










from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from gnd.review.adapters import ReviewerId
from gnd.review.request import (
    MVP_TRIAGE_CRITERION,
    ReviewArtifactMissingError,
    load_review_request,
)
from gnd.review.runner import ARTIFACTS_BY_REFERENCE_SCHEMA_VERSION, _build_prompt

SENTINEL = "SENTINEL-CONTENT-THAT-MUST-NEVER-REACH-A-PROMPT"


def _request(root: Path, *, body: str, name: str = "plan.md") -> object:
    (root / name).write_text(body)
    digest = hashlib.sha256((root / name).read_bytes()).hexdigest()
    (root / "request.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "kind": "plan",
                "plan": {"path": name, "sha256": digest, "media_type": "text/markdown"},
                "rubric": {
                    "name": "correctness",
                    "criteria": ["Cite concrete evidence from the artifact.", MVP_TRIAGE_CRITERION],
                },
            }
        )
    )
    return load_review_request(root, "request.json")


def _prompt(root: Path, *, body: str) -> str:
    return _build_prompt(_request(root, body=body), ReviewerId.claude).decode("utf-8")


def test_no_artifact_content_reaches_the_prompt(tmp_path: Path) -> None:


    prompt = _prompt(tmp_path, body=f"# Plan\n\n{SENTINEL}\n")

    assert SENTINEL not in prompt
    assert "kind=artifact-reference" in prompt
    assert "kind=artifact\n" not in prompt


def test_the_prompt_names_path_size_and_digest_for_every_artifact(tmp_path: Path) -> None:
    body = "# Plan\n\nOne step.\n"
    digest = hashlib.sha256(body.encode()).hexdigest()

    prompt = _prompt(tmp_path, body=body)

    assert prompt.count("path=plan.md media_type=text/markdown") == 1
    assert f"bytes={len(body.encode())} sha256={digest}" in prompt


def test_the_rubric_is_still_inlined(tmp_path: Path) -> None:




    prompt = _prompt(tmp_path, body="# Plan\n\nOne step.\n")

    assert "kind=rubric" in prompt
    assert "Cite concrete evidence from the artifact." in prompt


def test_the_prompt_instructs_the_reviewer_to_read_and_to_report_a_mismatch(
    tmp_path: Path,
) -> None:
    prompt = _prompt(tmp_path, body="# Plan\n\nOne step.\n")

    assert "Read each referenced path from the repository before judging it" in prompt
    assert "set the disposition to block" in prompt
    assert "Analyze only the evidence" not in prompt
                                                                             
                                                                              
                                                                         
                                                                
    assert "must name one of the artifacts listed above" in prompt
    assert "Context from elsewhere belongs in the observation text" in prompt
    assert "Cite evidence by real repository path" not in prompt
                                                                              
                                                                             
                                                                               
                                                                          
                                                      
    assert '"artifact_reads"' in prompt
    assert "report every referenced artifact you read" in prompt
    assert "set digest_matched to false" in prompt
    assert "Do not report a match" not in prompt


def test_prompt_size_is_bounded_by_artifact_count_not_artifact_size(tmp_path: Path) -> None:





    small = tmp_path / "small"
    large = tmp_path / "large"
    small.mkdir()
    large.mkdir()

    tiny = _prompt(small, body="x\n")
    huge = _prompt(large, body="x" * 1_000_000 + "\n")

    assert abs(len(huge) - len(tiny)) < 64


def test_a_thirty_mebibyte_artifact_load_fits_kimi_s_argv_headroom(tmp_path: Path) -> None:





    prompt = _prompt(tmp_path, body="y" * (10 * 1024 * 1024))

    assert len(prompt.encode("utf-8")) < 64 * 1024


def test_a_referenced_artifact_that_is_missing_still_fails_before_any_reviewer(
    tmp_path: Path,
) -> None:





    (tmp_path / "plan.md").write_text("# Plan\n")
    (tmp_path / "request.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "kind": "plan",
                "plan": {"path": "gone.md", "sha256": "0" * 64, "media_type": "text/markdown"},
                "rubric": {"name": "correctness", "criteria": ["Cite evidence.", MVP_TRIAGE_CRITERION]},
            }
        )
    )

    with pytest.raises(ReviewArtifactMissingError):
        load_review_request(tmp_path, "request.json")


def test_the_run_version_is_bound_to_the_prompt_it_describes(tmp_path: Path) -> None:










    from gnd.review.runner import PANEL_RUN_SCHEMA_VERSION

    loaded = _request(tmp_path, body=f"# Plan\n\n{SENTINEL}\n")
    prompt = _build_prompt(loaded, ReviewerId.claude).decode("utf-8")
    qwen_prompt = _build_prompt(loaded, ReviewerId.qwen).decode("utf-8")

    referenced = SENTINEL not in prompt and "kind=artifact-reference" in prompt
    assert referenced, "the writer no longer references; the version below is now a lie"
    assert SENTINEL in qwen_prompt and "kind=artifact-inline" in qwen_prompt
    assert PANEL_RUN_SCHEMA_VERSION >= ARTIFACTS_BY_REFERENCE_SCHEMA_VERSION


def test_the_thirty_mebibyte_aggregate_cap_holds_across_a_multi_artifact_request(
    tmp_path: Path,
) -> None:




    names = ("spec.md", "results.md", "delta.md")
    body = "z" * (10 * 1024 * 1024)
    document: dict[str, object] = {"schema_version": 1, "kind": "spec-results-delta"}
    for role, name in zip(("spec", "results", "delta"), names, strict=True):
        (tmp_path / name).write_text(body)
        document[role] = {
            "path": name,
            "sha256": hashlib.sha256(body.encode()).hexdigest(),
            "media_type": "text/markdown",
        }
    document["rubric"] = {"name": "correctness", "criteria": ["Cite evidence.", MVP_TRIAGE_CRITERION]}
    (tmp_path / "request.json").write_text(json.dumps(document))

    loaded = load_review_request(tmp_path, "request.json")
    prompt = _build_prompt(loaded, ReviewerId.kimi)

    assert len(loaded.artifacts) == 3
    assert len(prompt) < 64 * 1024


def test_the_report_stops_claiming_it_knows_what_a_reviewer_read() -> None:




    from gnd.review.report import _delivery_boundary

    class _Run:
        schema_version = ARTIFACTS_BY_REFERENCE_SCHEMA_VERSION

    class _Legacy:
        schema_version = 2

    class _Mixed:
        schema_version = 6
        artifact_transport = "qwen-inline"

    referenced = _delivery_boundary(_Run())
    inlined = _delivery_boundary(_Legacy())
    mixed = _delivery_boundary(_Mixed())

    assert "does not establish what any reviewer read" in referenced
    assert "evidence of engagement, never of complete reading" in referenced
    assert "complete artifact bytes in its prompt" in inlined
    assert "Qwen was handed the complete digest-checked artifact bytes" in mixed
    assert "other reviewers were given artifact paths" in mixed
