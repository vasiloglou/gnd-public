from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError
from support.digests import sha256_bytes as _digest

from gnd.review.request import (
    MVP_TRIAGE_CRITERION,
    ExperimentOutcomeReviewRequest,
    LoadedReviewRequest,
    PlanReviewRequest,
    ReviewArtifact,
    ReviewConcern,
    ReviewerResponse,
    ReviewEvidence,
    ReviewRequestError,
    ReviewRubric,
    SpecResultsDeltaReviewRequest,
    canonical_review_request,
    load_review_request,
    parse_reviewer_response,
    validate_review_request,
)


def _artifact(path: str, data: bytes) -> dict[str, str]:
    return {
        "path": path,
        "sha256": _digest(data),
        "media_type": "text/markdown",
    }


def _request_payload(kind: str, artifacts: dict[str, bytes]) -> dict[str, Any]:
    common: dict[str, Any] = {
        "schema_version": 2,
        "kind": kind,
        "rubric": {
            "name": "implementation safety",
            "criteria": [
                "Identify concrete correctness failures.",
                "Cite each concern to reviewed evidence.",
                MVP_TRIAGE_CRITERION,
            ],
        },
    }
    if kind == "plan":
        common["plan"] = _artifact("plan.md", artifacts["plan.md"])
    elif kind == "experiment-outcome":
        common["outcome"] = _artifact("outcome.json", artifacts["outcome.json"])
    elif kind == "spec-results-delta":
        common.update(
            {
                "spec": _artifact("SPEC.md", artifacts["SPEC.md"]),
                "results": _artifact("results.json", artifacts["results.json"]),
                "delta": _artifact("delta.md", artifacts["delta.md"]),
            }
        )
    else:  # pragma: no cover - helper guard
        raise AssertionError(kind)
    return common


def _materialize_request(
    root: Path,
    kind: str,
) -> tuple[Path, dict[str, Any], dict[str, bytes]]:
    artifacts = {
        "plan.md": b"# Plan\nDo the bounded thing.\n",
        "outcome.json": b'{"outcome":"accepted"}\n',
        "SPEC.md": b"# Contract\nThe result is exact.\n",
        "results.json": b'{"score":1}\n',
        "delta.md": b"# Delta\nNo discrepancy.\n",
    }
    payload = _request_payload(kind, artifacts)
    for relative in {
        value["path"] for value in payload.values() if isinstance(value, dict) and "path" in value
    }:
        (root / relative).write_bytes(artifacts[relative])
    request_path = root / "review-request.json"
    request_path.write_text(json.dumps(payload), encoding="utf-8")
    return request_path, payload, artifacts


@pytest.mark.parametrize(
    ("kind", "expected_type", "paths"),
    [
        ("plan", PlanReviewRequest, ("plan.md",)),
        ("experiment-outcome", ExperimentOutcomeReviewRequest, ("outcome.json",)),
        (
            "spec-results-delta",
            SpecResultsDeltaReviewRequest,
            ("SPEC.md", "results.json", "delta.md"),
        ),
    ],
)
def test_load_review_request_accepts_exactly_three_digest_bound_variants(
    tmp_path: Path,
    kind: str,
    expected_type: type[BaseModel],
    paths: tuple[str, ...],
) -> None:
    request_path, _payload, artifacts = _materialize_request(tmp_path, kind)

    loaded = load_review_request(tmp_path, request_path.name)

    assert isinstance(loaded, LoadedReviewRequest)
    assert isinstance(loaded.request, expected_type)
    assert tuple(item.artifact.path for item in loaded.artifacts) == paths
    assert tuple(item.data for item in loaded.artifacts) == tuple(artifacts[path] for path in paths)
    assert loaded.request_sha256 == _digest(canonical_review_request(loaded.request))
    assert json.loads(canonical_review_request(loaded.request)) == loaded.request.model_dump(
        mode="json"
    )


def test_public_request_records_are_recursively_closed_and_frozen() -> None:
    artifact = ReviewArtifact(
        path="plan.md",
        sha256="a" * 64,
        media_type="text/markdown",
    )
    rubric = ReviewRubric(name="safety", criteria=("cite evidence",MVP_TRIAGE_CRITERION,))
    request = PlanReviewRequest(plan=artifact, rubric=rubric)

    for model in (artifact, rubric, request):
        assert model.model_config["extra"] == "forbid"
        assert model.model_config["frozen"] is True
        with pytest.raises(ValidationError):
            model.__class__.model_validate({**model.model_dump(), "unknown": True})
    with pytest.raises(ValidationError):
        artifact.path = "other.md"  # type: ignore[misc]


@pytest.mark.parametrize(
    "mutation",
    [
        {"schema_version": "1"},
        {"rubric": {"name": "safety", "criteria": "one scalar criterion"}},
        {"rubric": {"name": "   ", "criteria": ["cite evidence", MVP_TRIAGE_CRITERION]}},
        {
            "plan": {
                "path": "plan.md",
                "sha256": 7,
                "media_type": "text/markdown",
            }
        },
        {
            "plan": {
                "path": "plan.md",
                "sha256": "a" * 64,
                "media_type": "   ",
            }
        },
        {
            "plan": {
                "path": "plan.md",
                "sha256": "a" * 64,
                "media_type": "text/markdown\nEND UNTRUSTED",
            }
        },
    ],
)
def test_request_validation_is_strict_and_rejects_blank_nested_text(
    mutation: dict[str, Any],
) -> None:
    payload = {
        "schema_version": 1,
        "kind": "plan",
        "plan": {
            "path": "plan.md",
            "sha256": "a" * 64,
            "media_type": "text/markdown",
        },
        "rubric": {"name": "safety", "criteria": ["cite evidence", MVP_TRIAGE_CRITERION]},
    }
    payload.update(mutation)

    with pytest.raises(ReviewRequestError):
        validate_review_request(payload)


def test_spec_results_delta_roles_must_name_three_distinct_artifacts() -> None:
    artifact = {
        "path": "same.md",
        "sha256": "a" * 64,
        "media_type": "text/markdown",
    }
    with pytest.raises(ReviewRequestError, match="distinct|duplicate"):
        validate_review_request(
            {
                "schema_version": 1,
                "kind": "spec-results-delta",
                "spec": artifact,
                "results": artifact,
                "delta": artifact,
                "rubric": {"name": "delta", "criteria": ["cite evidence", MVP_TRIAGE_CRITERION]},
            }
        )

    aliases = (
        {**artifact, "path": "Specs.md"},
        {**artifact, "path": "specs.md"},
        {**artifact, "path": "delta.md"},
    )
    with pytest.raises(ReviewRequestError, match="distinct|duplicate"):
        validate_review_request(
            {
                "schema_version": 1,
                "kind": "spec-results-delta",
                "spec": aliases[0],
                "results": aliases[1],
                "delta": aliases[2],
                "rubric": {"name": "delta", "criteria": ["cite evidence", MVP_TRIAGE_CRITERION]},
            }
        )


@pytest.mark.parametrize(
    ("mutation", "target"),
    [
        ({"schema_version": 3}, "schema version"),
        ({"kind": "repository"}, "closed kind"),
        ({"provider": "claude"}, "top-level unknown field"),
        ({"command": ["sh", "-c", "oops"]}, "command injection field"),
        (
            {"plan": {"path": "plan.md", "sha256": "0" * 64, "media_type": "text/markdown"}},
            "mixed-kind member",
        ),
    ],
)
def test_request_union_rejects_schema_drift_and_mixed_kind_members(
    tmp_path: Path,
    mutation: dict[str, Any],
    target: str,
) -> None:
    request_path, payload, _artifacts = _materialize_request(tmp_path, "experiment-outcome")
    payload.update(mutation)
    request_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ReviewRequestError, match="invalid review request"):
        load_review_request(tmp_path, request_path.name)
    assert target


def test_unknown_fields_are_rejected_at_every_nested_request_depth(tmp_path: Path) -> None:
    request_path, payload, _artifacts = _materialize_request(tmp_path, "plan")
    mutations = (
        lambda value: value.update({"unexpected": 1}),
        lambda value: value["plan"].update({"model": "opus"}),
        lambda value: value["rubric"].update({"provider": "codex"}),
    )
    for mutate in mutations:
        candidate = json.loads(json.dumps(payload))
        mutate(candidate)
        request_path.write_text(json.dumps(candidate), encoding="utf-8")
        with pytest.raises(ReviewRequestError, match="invalid review request"):
            load_review_request(tmp_path, request_path.name)


@pytest.mark.parametrize(
    "criteria",
    [[], ["   "], ["same", "same"], ["same", " same "]],
)
def test_rubric_requires_nonempty_unique_criteria(
    tmp_path: Path,
    criteria: list[str],
) -> None:
    request_path, payload, _artifacts = _materialize_request(tmp_path, "plan")
    payload["rubric"]["criteria"] = criteria
    request_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ReviewRequestError, match="invalid review request"):
        load_review_request(tmp_path, request_path.name)


@pytest.mark.parametrize(
    "unsafe",
    [
        "/etc/passwd",
        "../outside.md",
        "nested/../../outside.md",
        r"C:\\Windows\\system.ini",
        r"C:drive-relative.md",
        r"nested\\escape.md",
        "./plan.md",
        "plan.md/",
        "plan\x00.md",
    ],
)
def test_artifact_paths_are_normalized_repository_relative_only(
    unsafe: str,
) -> None:
    with pytest.raises(ValidationError):
        ReviewArtifact(
            path=unsafe,
            sha256="a" * 64,
            media_type="text/markdown",
        )


@pytest.mark.parametrize("unsafe", ["../request.json", "/tmp/request.json", r"C:\\x"])
def test_request_file_path_is_repository_relative(tmp_path: Path, unsafe: str) -> None:
    with pytest.raises(ReviewRequestError, match="path"):
        load_review_request(tmp_path, unsafe)


def test_loader_rejects_missing_stale_symlink_and_nonregular_artifacts(
    tmp_path: Path,
) -> None:
    from gnd.review.request import ReviewArtifactMissingError

    request_path, payload, _artifacts = _materialize_request(tmp_path, "plan")

    (tmp_path / "plan.md").unlink()
    with pytest.raises(ReviewArtifactMissingError, match="plan.md"):
        load_review_request(tmp_path, request_path.name)

    (tmp_path / "plan.md").write_bytes(b"different")
    with pytest.raises(ReviewRequestError, match="sha256"):
        load_review_request(tmp_path, request_path.name)

    target = tmp_path / "target.md"
    target.write_bytes(b"# Plan\nDo the bounded thing.\n")
    (tmp_path / "plan.md").unlink()
    (tmp_path / "plan.md").symlink_to(target)
    with pytest.raises(ReviewRequestError, match="symlink|regular"):
        load_review_request(tmp_path, request_path.name)

    if hasattr(os, "mkfifo"):
        (tmp_path / "plan.md").unlink()
        os.mkfifo(tmp_path / "plan.md")
        with pytest.raises(ReviewRequestError, match="regular"):
            load_review_request(tmp_path, request_path.name)

    assert payload["plan"]["sha256"] == _digest(b"# Plan\nDo the bounded thing.\n")


def test_loader_rejects_symlinked_request_and_repository_root(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    request_path, _payload, _artifacts = _materialize_request(real, "plan")
    (real / "request-link.json").symlink_to(request_path)
    root_link = tmp_path / "root-link"
    root_link.symlink_to(real, target_is_directory=True)

    with pytest.raises(ReviewRequestError, match="symlink|regular"):
        load_review_request(real, "request-link.json")
    with pytest.raises(ReviewRequestError, match="root"):
        load_review_request(root_link, request_path.name)


def test_loader_rejects_intermediate_symlink_for_request_or_artifact(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    plan = b"# Plan\nOutside bytes must not be reviewed through an alias.\n"
    (outside / "plan.md").write_bytes(plan)
    (outside / "request.json").write_text(
        json.dumps(_request_payload("plan", {"plan.md": plan})),
        encoding="utf-8",
    )
    repository = tmp_path / "repository"
    repository.mkdir()
    (repository / "alias").symlink_to(outside, target_is_directory=True)

    with pytest.raises(ReviewRequestError, match="symlink|unsafe|regular"):
        load_review_request(repository, "alias/request.json")

    request = _request_payload("plan", {"plan.md": plan})
    request["plan"]["path"] = "alias/plan.md"
    (repository / "request.json").write_text(json.dumps(request), encoding="utf-8")
    with pytest.raises(ReviewRequestError, match="symlink|unsafe|regular"):
        load_review_request(repository, "request.json")


def test_loader_enforces_request_per_file_and_aggregate_caps(tmp_path: Path) -> None:
    request_path, _payload, _artifacts = _materialize_request(tmp_path, "spec-results-delta")
    request_size = request_path.stat().st_size

    with pytest.raises(ReviewRequestError, match="request.*cap|byte"):
        load_review_request(tmp_path, request_path.name, max_request_bytes=request_size - 1)
    with pytest.raises(ReviewRequestError, match="per-file|byte"):
        load_review_request(tmp_path, request_path.name, max_artifact_bytes=5)
    with pytest.raises(ReviewRequestError, match="aggregate|total"):
        load_review_request(tmp_path, request_path.name, max_total_artifact_bytes=20)


def test_loader_rejects_duplicate_keys_trailing_json_and_nonfinite_constants(
    tmp_path: Path,
) -> None:
    _request_path, payload, _artifacts = _materialize_request(tmp_path, "plan")
    candidates = (
        b'{"schema_version":2,"schema_version":2}',
        json.dumps(payload).encode() + b" trailing",
        json.dumps(payload).replace('"schema_version": 2', '"schema_version": NaN').encode(),
    )
    for index, raw in enumerate(candidates):
        path = tmp_path / f"bad-{index}.json"
        path.write_bytes(raw)
        with pytest.raises(ReviewRequestError, match="JSON|duplicate|finite|invalid"):
            load_review_request(tmp_path, path.name)


def _valid_response(reviewer_id: str = "claude") -> dict[str, Any]:
    return {
        "schema_version": 2,
        "reviewer_id": reviewer_id,
        "disposition": "revise",
        "summary": "One concrete issue remains.",
        "concerns": [
            {
                "concern_id": "missing-bound",
                "severity": "high",
                "relevance": "blocking",
                "title": "The output bound is absent",
                "evidence": [
                    {
                        "artifact_path": "plan.md",
                        "location": "line 12",
                        "observation": "The step invokes a process without a byte cap.",
                    }
                ],
                "recommendation": "Add a closed byte limit before process launch.",
            }
        ],
    }


def test_reviewer_response_validates_complete_closed_json_and_expected_identity() -> None:
    response = parse_reviewer_response(
        json.dumps(_valid_response(), separators=(",", ":")).encode(),
        expected_reviewer="claude",
    )

    assert isinstance(response, ReviewerResponse)
    assert response.reviewer_id == "claude"
    assert isinstance(response.concerns[0], ReviewConcern)
    assert isinstance(response.concerns[0].evidence[0], ReviewEvidence)
    assert response.model_config["extra"] == "forbid"
    assert response.model_config["frozen"] is True


def test_reviewer_response_evidence_must_name_a_requested_artifact() -> None:
    raw = json.dumps(_valid_response()).encode()

    assert parse_reviewer_response(
        raw,
        expected_reviewer="claude",
        allowed_artifact_paths=("plan.md",),
    )
    with pytest.raises(ReviewRequestError, match="artifact"):
        parse_reviewer_response(
            raw,
            expected_reviewer="claude",
            allowed_artifact_paths=("other.md",),
        )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.update({"schema_version": "1"}),
        lambda value: value.update({"disposition": "maybe"}),
        lambda value: value["concerns"][0].update({"severity": "urgent"}),
        lambda value: value["concerns"][0]["evidence"][0].update({"location": "   "}),
        lambda value: value["concerns"][0]["evidence"][0].update({"observation": "   "}),
        lambda value: value.update({"disposition": "approve"}),
    ],
)
def test_reviewer_response_rejects_coercion_unknown_enums_blank_evidence_and_approval_with_concerns(
    mutation: Any,
) -> None:
    payload = _valid_response()
    mutation(payload)

    with pytest.raises(ReviewRequestError):
        parse_reviewer_response(
            json.dumps(payload).encode(),
            expected_reviewer="claude",
        )


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda value: value.update({"reviewer_id": "codex"}), "reviewer"),
        (lambda value: value.update({"unknown": True}), "invalid"),
        (lambda value: value["concerns"][0].update({"unknown": True}), "invalid"),
        (lambda value: value["concerns"][0].update({"evidence": []}), "invalid"),
        (
            lambda value: value.update({"disposition": "block", "concerns": []}),
            "concern",
        ),
    ],
)
def test_reviewer_response_rejects_wrong_identity_and_nested_schema_drift(
    mutate: Any,
    message: str,
) -> None:
    payload = _valid_response()
    mutate(payload)

    with pytest.raises(ReviewRequestError, match=message):
        parse_reviewer_response(
            json.dumps(payload).encode(),
            expected_reviewer="claude",
        )


def test_a_repeated_concern_identifier_is_dropped_rather_than_fatal() -> None:
    """This case used to kill the seat. Under per-concern salvage it costs the
    repeat and nothing else; the full behavior is pinned in test_review_salvage.
    """

    from gnd.review.request import parse_reviewer_response_with_salvage

    payload = _valid_response()
    payload["concerns"].append(payload["concerns"][0].copy())

    parsed = parse_reviewer_response_with_salvage(
        json.dumps(payload).encode(),
        expected_reviewer="claude",
    )

    assert len(parsed.response.concerns) == 1
    assert [entry.position for entry in parsed.salvage.dropped] == [2]
    assert "duplicate concern identifier" in parsed.salvage.dropped[0].reason
    assert parsed.salvage.complete is False


def test_reviewer_response_parser_rejects_duplicate_keys_trailing_nan_and_nonobject() -> None:
    valid = json.dumps(_valid_response(), separators=(",", ":")).encode()
    samples = (
        valid[:-1] + b',"summary":"duplicate"}',
        valid + b"\n{}",
        valid.replace(b'"schema_version":2', b'"schema_version":NaN'),
        b"[]",
        b"",
        b"\xff",
    )
    for raw in samples:
        with pytest.raises(ReviewRequestError):
            parse_reviewer_response(raw, expected_reviewer="claude")


def test_validate_review_request_rejects_nonmapping_and_unknown_kind() -> None:
    for value in ([], "plan", {"schema_version": 1, "kind": "general"}):
        with pytest.raises(ReviewRequestError):
            validate_review_request(value)


def test_a_fenced_reviewer_response_parses_because_refusing_it_was_our_defect() -> None:
    """Measured in `panel-run-04`: claude returned a schema-valid review wrapped
    in ```json ... ``` and GND rejected it at `char 0`. The reviewer was right and
    the parser was wrong. Unwrapping is narrow -- only a wholly-fenced payload --
    so everything that failed closed before still does.
    """

    from gnd.review.request import _strict_json_object

    body = b'{"a": 1}'
    assert _strict_json_object(b"```json\n" + body + b"\n```", label="t") == {"a": 1}
    assert _strict_json_object(b"```\n" + body + b"\n```", label="t") == {"a": 1}
    assert _strict_json_object(body, label="t") == {"a": 1}

    for still_invalid in (
        b"```json\n" + body + b"\n```\nand here is my reasoning",
        b"I'm sorry, I cannot review this.",
        b"```json\n[1, 2, 3]\n```",
    ):
        with pytest.raises(ReviewRequestError):
            _strict_json_object(still_invalid, label="t")


# Historical saved-provider response stays in the private source archive.


def test_a_current_version_response_must_classify_every_concern() -> None:
    """The MVP axis is required where it is asked for, and only there.

    Both halves matter.  Refusing an unclassified concern at schema version 2 is
    what makes ``relevance`` a measurement rather than a suggestion; accepting
    the identical bytes at version 1 is what keeps committed panel evidence --
    authored before the axis existed -- loadable.  A guard that did the first
    without the second would destroy retained evidence to tighten a schema.
    """

    payload = _valid_response()
    del payload["concerns"][0]["relevance"]

    with pytest.raises(ReviewRequestError, match="relevance"):
        parse_reviewer_response(
            json.dumps(payload, separators=(",", ":")).encode(),
            expected_reviewer="claude",
        )

    payload["schema_version"] = 1
    legacy = parse_reviewer_response(
        json.dumps(payload, separators=(",", ":")).encode(),
        expected_reviewer="claude",
    )
    assert legacy.concerns[0].relevance is None
    # ...and it round-trips without inventing a key the committed bytes lack.
    assert "relevance" not in legacy.concerns[0].model_dump(mode="json")


def test_a_current_version_request_must_carry_the_standing_mvp_criterion() -> None:
    """A panel cannot be run without telling reviewers to triage."""

    payload: dict[str, Any] = {
        "schema_version": 2,
        "kind": "plan",
        "plan": {"path": "plan.md", "sha256": "a" * 64, "media_type": "text/markdown"},
        "rubric": {"name": "safety", "criteria": ["cite evidence"]},
    }

    with pytest.raises(ReviewRequestError, match="MVP triage criterion"):
        validate_review_request(payload)

    payload["rubric"]["criteria"] = ["cite evidence", MVP_TRIAGE_CRITERION]
    assert validate_review_request(payload).rubric.criteria[-1] == MVP_TRIAGE_CRITERION

    # The negative control for the version condition: a retained request from
    # before the criterion existed still loads.
    stale = {**payload, "schema_version": 1}
    stale["rubric"] = {"name": "safety", "criteria": ["cite evidence"]}
    assert validate_review_request(stale).schema_version == 1
