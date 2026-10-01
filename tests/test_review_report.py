from __future__ import annotations

import builtins
import hashlib
import inspect
import os
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from gnd.agent_cli import EnvironmentFact
from gnd.review.adapters import REVIEWER_IDS, ReviewerId, reviewer_policies

# The executable each reviewer identity runs (the GLM seat runs claude, so an
# envelope's executable_name is not always its reviewer id).
_EXECUTABLES = {policy.reviewer_id: policy.executable_name for policy in reviewer_policies()}
from gnd.review.report import (
    ConcernEvidenceRef,
    ConcernGroup,
    ConcernRef,
    PanelResult,
    PanelSynthesis,
    PrioritizedFix,
    ReviewReportError,
    canonical_panel_synthesis,
    finalize_panel_synthesis,
    render_panel_markdown,
)
from gnd.review.request import (
    MVP_TRIAGE_CRITERION,
    PlanReviewRequest,
    ResponseSalvage,
    ReviewArtifact,
    ReviewConcern,
    ReviewerResponse,
    ReviewEvidence,
    ReviewRubric,
    canonical_review_request,
)
from gnd.review.runner import (
    PanelRun,
    ProcessEvidence,
    ReviewerEnvelope,
    ReviewerStatus,
    ReviewIssue,
    StreamEvidence,
    canonical_panel_run,
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _request() -> PlanReviewRequest:
    return PlanReviewRequest(
        plan=ReviewArtifact(
            path="plan.md",
            sha256="1" * 64,
            media_type="text/markdown",
        ),
        rubric=ReviewRubric(name="correctness", criteria=("Cite concrete evidence.",MVP_TRIAGE_CRITERION,)),
    )


def _response(
    reviewer: ReviewerId,
    concern_ids: tuple[str, ...] = (),
    *,
    injected_text: str | None = None,
) -> ReviewerResponse:
    concerns = tuple(
        ReviewConcern(
            concern_id=concern_id,
            severity="high" if concern_id == "shared" else "medium",
            # Relevance tracks the concern id, so a run can carry a mixed
            # triage without a second fixture builder.
            relevance="blocking" if concern_id == "shared" else "completeness",
            title=(
                injected_text
                if injected_text is not None
                else f"Concern {concern_id} needs attention"
            ),
            evidence=(
                ReviewEvidence(
                    artifact_path="plan.md",
                    location="line 12",
                    observation=(
                        injected_text
                        if injected_text is not None
                        else f"Evidence for {concern_id} is present here."
                    ),
                ),
            ),
            recommendation=f"Fix {concern_id} without changing review evidence.",
        )
        for concern_id in concern_ids
    )
    return ReviewerResponse(
        schema_version=1,
        reviewer_id=reviewer.value,
        disposition="revise" if concerns else "approve",
        summary="Evidence-backed response.",
        concerns=concerns,
    )


def _stream(reviewer: ReviewerId, name: str, data: bytes) -> StreamEvidence:
    return StreamEvidence(
        path=f"reviewers/{reviewer.value}/{name}",
        sha256=_sha(data),
        observed_bytes=len(data),
        retained_bytes=len(data),
        truncated=False,
    )


def _process(
    reviewer: ReviewerId,
    *,
    phase: str,
    stdout: bytes,
) -> ProcessEvidence:
    if phase == "capability":
        started, ended = 1.0, 1.25
        argv_sha256, argv_count = "2" * 64, 2
        stdin_sha256 = None
        stderr = b"capability probe stderr\n"
        stdout_name, stderr_name = "capability.stdout", "capability.stderr"
    elif phase == "invocation":
        started, ended = 2.0, 3.0
        argv_sha256, argv_count = "4" * 64, 5
        stdin_sha256 = "5" * 64
        stderr = b""
        stdout_name, stderr_name = "stdout", "stderr"
    else:  # pragma: no cover - fixture guard
        raise AssertionError(phase)
    return ProcessEvidence(
        status="succeeded",
        spawned=True,
        timed_out=False,
        termination="exited",
        return_code=0,
        signal=None,
        spawn_error=None,
        started_monotonic=started,
        ended_monotonic=ended,
        elapsed_seconds=ended - started,
        argv_sha256=argv_sha256,
        argv_count=argv_count,
        stdin_sha256=stdin_sha256,
        stdout=_stream(reviewer, stdout_name, stdout),
        stderr=_stream(reviewer, stderr_name, stderr),
        environment=(EnvironmentFact(name="PATH", provenance="supplied"),),
        termination_steps=(),
        process_group_cleaned=True,
    )


def _envelope(
    reviewer: ReviewerId,
    response: ReviewerResponse | None,
) -> ReviewerEnvelope:
    if response is not None:
        capability = _process(
            reviewer,
            phase="capability",
            stdout=b"read-only mode supported\n",
        )
        invocation = _process(
            reviewer,
            phase="invocation",
            stdout=response.model_dump_json().encode(),
        )
        return ReviewerEnvelope(
            schema_version=1,
            reviewer_id=reviewer,
            status=ReviewerStatus.success,
            executable_name=_EXECUTABLES[reviewer],
            capability=capability,
            invocation=invocation,
            response=response,
            issues=(),
        )
    return ReviewerEnvelope(
        schema_version=1,
        reviewer_id=reviewer,
        status=ReviewerStatus.missing,
        executable_name=_EXECUTABLES[reviewer],
        capability=None,
        invocation=None,
        response=None,
        issues=(ReviewIssue(code="missing", message="reviewer executable is missing"),),
    )


def _run(
    successful: tuple[ReviewerId, ...],
    concern_ids: dict[ReviewerId, tuple[str, ...]] | None = None,
    *,
    injected_text: str | None = None,
) -> PanelRun:
    request = _request()
    concerns = concern_ids or {}
    envelopes = tuple(
        _envelope(
            reviewer,
            (
                _response(
                    reviewer,
                    concerns.get(reviewer, ()),
                    injected_text=injected_text,
                )
                if reviewer in successful
                else None
            ),
        )
        for reviewer in REVIEWER_IDS
    )
    artifact_digest = _sha(b"plan.md\x001" + b"1" * 63)
    return PanelRun(
        schema_version=1,
        request=request,
        request_sha256=_sha(canonical_review_request(request)),
        envelopes=envelopes,
        successful_reviewer_ids=successful,
        quorum_met=len(successful) >= 3,
        reviewed_artifacts_before_sha256=artifact_digest,
        reviewed_artifacts_after_sha256=artifact_digest,
    )


def _run_sha(run: PanelRun) -> str:
    return _sha(canonical_panel_run(run))


def _empty_synthesis(run: PanelRun) -> PanelSynthesis:
    return PanelSynthesis(
        schema_version=1,
        run_sha256=_run_sha(run),
        summary="The successful reviewers raised no concerns.",
        agreed_concerns=(),
        divergent_concerns=(),
        prioritized_fixes=(),
    )


def _ref(reviewer: ReviewerId, concern_id: str) -> ConcernRef:
    return ConcernRef(reviewer_id=reviewer, concern_id=concern_id)


@pytest.mark.parametrize("success_count", range(5))
def test_finalization_quorum_is_exactly_three_distinct_successful_reviewers(
    success_count: int,
) -> None:
    run = _run(REVIEWER_IDS[:success_count])
    synthesis = _empty_synthesis(run)

    if success_count < 3:
        with pytest.raises(ReviewReportError, match="quorum|three"):
            finalize_panel_synthesis(run, synthesis)
    else:
        result = finalize_panel_synthesis(run, synthesis)
        assert isinstance(result, PanelResult)
        assert result.successful_reviewer_ids == REVIEWER_IDS[:success_count]
        assert result.advisory is True


@pytest.mark.parametrize("supporter_count", range(5))
def test_agreement_requires_two_distinct_successful_supporters(
    supporter_count: int,
) -> None:
    successful = REVIEWER_IDS
    supporting = REVIEWER_IDS[:supporter_count]
    run = _run(
        successful,
        {reviewer: ("shared",) for reviewer in supporting},
    )
    refs = tuple(_ref(reviewer, "shared") for reviewer in supporting)
    group = ConcernGroup(
        group_id="shared-bound",
        severity="high",
        title="Bound external output",
        summary="Independent reviewers identified the same missing bound.",
        concerns=refs,
        supporting_reviewers=supporting,
    )
    synthesis = PanelSynthesis(
        schema_version=1,
        run_sha256=_run_sha(run),
        summary="Review synthesis.",
        agreed_concerns=(group,),
        divergent_concerns=(),
        prioritized_fixes=(),
    )

    if supporter_count < 2:
        with pytest.raises((ValidationError, ReviewReportError), match="two|support"):
            finalize_panel_synthesis(run, synthesis)
    else:
        result = finalize_panel_synthesis(run, synthesis)
        assert result.agreed_concern_count == 1
        assert result.divergent_concern_count == 0


def test_two_concerns_from_one_reviewer_are_not_agreement() -> None:
    run = _run(REVIEWER_IDS[:3], {ReviewerId.claude: ("one", "two")})
    group = ConcernGroup(
        group_id="forged",
        severity="medium",
        title="Not independent",
        summary="Two concern IDs came from one reviewer.",
        concerns=(
            _ref(ReviewerId.claude, "one"),
            _ref(ReviewerId.claude, "two"),
        ),
        supporting_reviewers=(ReviewerId.claude,),
    )
    synthesis = PanelSynthesis(
        run_sha256=_run_sha(run),
        summary="Invalid grouping.",
        agreed_concerns=(group,),
        divergent_concerns=(),
        prioritized_fixes=(),
    )

    with pytest.raises((ValidationError, ReviewReportError), match="distinct|two|support"):
        finalize_panel_synthesis(run, synthesis)


def test_singleton_concern_is_retained_under_divergent_views() -> None:
    run = _run(REVIEWER_IDS[:3], {ReviewerId.claude: ("singleton",)})
    singleton = _ref(ReviewerId.claude, "singleton")
    synthesis = PanelSynthesis(
        run_sha256=_run_sha(run),
        summary="One reviewer found a distinct issue.",
        agreed_concerns=(),
        divergent_concerns=(singleton,),
        prioritized_fixes=(),
    )

    result = finalize_panel_synthesis(run, synthesis)
    rendered = render_panel_markdown(run, synthesis, result)

    assert result.divergent_concern_count == 1
    assert "Divergent Views" in rendered
    assert "claude" in rendered
    assert "singleton" in rendered
    assert "line 12" in rendered


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("omit", "missing|account"),
        ("duplicate-divergent", "duplicate|once"),
        ("group-and-divergent", "duplicate|once"),
        ("unknown-concern", "unknown|concern"),
        ("failed-reviewer", "successful|reviewer"),
        ("forged-supporters", "support"),
    ],
)
def test_complete_concern_accounting_rejects_omission_duplication_and_forgery(
    mutation: str,
    message: str,
) -> None:
    run = _run(
        REVIEWER_IDS[:3],
        {
            ReviewerId.claude: ("shared", "solo"),
            ReviewerId.codex: ("shared",),
        },
    )
    shared = (
        _ref(ReviewerId.claude, "shared"),
        _ref(ReviewerId.codex, "shared"),
    )
    group = ConcernGroup(
        group_id="shared",
        severity="high",
        title="Shared issue",
        summary="Two reviewers found it.",
        concerns=shared,
        supporting_reviewers=(ReviewerId.claude, ReviewerId.codex),
    )
    divergent: tuple[ConcernRef, ...] = (_ref(ReviewerId.claude, "solo"),)
    if mutation == "omit":
        divergent = ()
    elif mutation == "duplicate-divergent":
        divergent = divergent * 2
    elif mutation == "group-and-divergent":
        divergent = divergent + (shared[0],)
    elif mutation == "unknown-concern":
        divergent = (_ref(ReviewerId.claude, "invented"),)
    elif mutation == "failed-reviewer":
        divergent = (_ref(ReviewerId.gemini, "invented"),)
    elif mutation == "forged-supporters":
        group = group.model_copy(
            update={"supporting_reviewers": (ReviewerId.claude, ReviewerId.qwen)}
        )
    synthesis = PanelSynthesis(
        run_sha256=_run_sha(run),
        summary="Mutation target.",
        agreed_concerns=(group,),
        divergent_concerns=divergent,
        prioritized_fixes=(),
    )

    with pytest.raises(ReviewReportError, match=message):
        finalize_panel_synthesis(run, synthesis)


def _valid_group_and_fix(run: PanelRun) -> tuple[ConcernGroup, PrioritizedFix]:
    concerns = (
        _ref(ReviewerId.claude, "shared"),
        _ref(ReviewerId.codex, "shared"),
    )
    supporters = (ReviewerId.claude, ReviewerId.codex)
    group = ConcernGroup(
        group_id="shared",
        severity="high",
        title="Bound subprocess output",
        summary="Both reviewers cite the same missing bound.",
        concerns=concerns,
        supporting_reviewers=supporters,
    )
    fix = PrioritizedFix(
        fix_id="fix-output-bound",
        rank=1,
        title="Add the missing output cap",
        action="Update the process step and its test to enforce the declared byte cap.",
        concerns=concerns,
        evidence=(
            ConcernEvidenceRef(
                reviewer_id=ReviewerId.claude,
                concern_id="shared",
                evidence_index=0,
            ),
            ConcernEvidenceRef(
                reviewer_id=ReviewerId.codex,
                concern_id="shared",
                evidence_index=0,
            ),
        ),
        supporting_reviewers=supporters,
    )
    assert run.quorum_met
    return group, fix


def test_prioritized_fix_resolves_every_supporter_to_requested_artifact_evidence() -> None:
    run = _run(
        REVIEWER_IDS[:3],
        {
            ReviewerId.claude: ("shared",),
            ReviewerId.codex: ("shared",),
        },
    )
    group, fix = _valid_group_and_fix(run)
    synthesis = PanelSynthesis(
        run_sha256=_run_sha(run),
        summary="Two reviewers agree on one located fix.",
        agreed_concerns=(group,),
        divergent_concerns=(),
        prioritized_fixes=(fix,),
    )

    result = finalize_panel_synthesis(run, synthesis)
    rendered = render_panel_markdown(run, synthesis, result)

    assert result.prioritized_fix_count == 1
    assert "plan.md" in rendered
    assert "line 12" in rendered
    assert "claude" in rendered and "codex" in rendered


def test_prioritized_fix_cannot_omit_one_supporter_from_addressed_agreement() -> None:
    run = _run(
        REVIEWER_IDS[:3],
        {
            ReviewerId.claude: ("shared",),
            ReviewerId.codex: ("shared",),
        },
    )
    group, fix = _valid_group_and_fix(run)
    forged = fix.model_copy(
        update={
            "concerns": (_ref(ReviewerId.claude, "shared"),),
            "evidence": (
                ConcernEvidenceRef(
                    reviewer_id=ReviewerId.claude,
                    concern_id="shared",
                    evidence_index=0,
                ),
            ),
            "supporting_reviewers": (ReviewerId.claude,),
        }
    )
    synthesis = PanelSynthesis(
        run_sha256=_run_sha(run),
        summary="A forged fix drops one member of an established agreement.",
        agreed_concerns=(group,),
        divergent_concerns=(),
        prioritized_fixes=(forged,),
    )

    with pytest.raises(ReviewReportError, match="every supporter|agreed group"):
        finalize_panel_synthesis(run, synthesis)


def test_prioritized_fix_rejects_one_missing_supporter_evidence_reference() -> None:
    run = _run(
        REVIEWER_IDS[:3],
        {
            ReviewerId.claude: ("shared",),
            ReviewerId.codex: ("shared",),
        },
    )
    group, fix = _valid_group_and_fix(run)
    missing_codex_evidence = fix.model_copy(update={"evidence": fix.evidence[:1]})
    assert missing_codex_evidence.concerns == fix.concerns
    assert missing_codex_evidence.supporting_reviewers == fix.supporting_reviewers
    synthesis = PanelSynthesis(
        run_sha256=_run_sha(run),
        summary="Both supporters remain, but one evidence reference was removed.",
        agreed_concerns=(group,),
        divergent_concerns=(),
        prioritized_fixes=(missing_codex_evidence,),
    )

    with pytest.raises(ReviewReportError, match="evidence.*every.*supporter"):
        finalize_panel_synthesis(run, synthesis)


@pytest.mark.parametrize(
    ("update", "message"),
    [
        ({"concerns": ()}, "concern"),
        ({"evidence": ()}, "evidence"),
        (
            {
                "evidence": (
                    ConcernEvidenceRef(
                        reviewer_id=ReviewerId.claude,
                        concern_id="shared",
                        evidence_index=99,
                    ),
                )
            },
            "evidence|index",
        ),
        ({"supporting_reviewers": (ReviewerId.qwen,)}, "support"),
        (
            {"concerns": (_ref(ReviewerId.claude, "invented"),)},
            "unknown|concern",
        ),
    ],
)
def test_prioritized_fix_cannot_lose_evidence_invent_concerns_or_forge_supporters(
    update: dict[str, Any],
    message: str,
) -> None:
    run = _run(
        REVIEWER_IDS[:3],
        {
            ReviewerId.claude: ("shared",),
            ReviewerId.codex: ("shared",),
        },
    )
    group, fix = _valid_group_and_fix(run)
    forged = fix.model_copy(update=update)
    synthesis = PanelSynthesis(
        run_sha256=_run_sha(run),
        summary="Forged fix target.",
        agreed_concerns=(group,),
        divergent_concerns=(),
        prioritized_fixes=(forged,),
    )

    with pytest.raises((ValidationError, ReviewReportError), match=message):
        finalize_panel_synthesis(run, synthesis)


def test_run_digest_and_stored_quorum_are_revalidated_during_finalization() -> None:
    run = _run(REVIEWER_IDS[:3])
    wrong_digest = _empty_synthesis(run).model_copy(update={"run_sha256": "f" * 64})
    with pytest.raises(ReviewReportError, match="run.*digest"):
        finalize_panel_synthesis(run, wrong_digest)

    forged = run.model_copy(update={"quorum_met": False})
    with pytest.raises(ReviewReportError, match="quorum|run"):
        finalize_panel_synthesis(forged, _empty_synthesis(forged))


def _assert_closed_and_frozen(model: Any) -> None:
    assert model.model_config["extra"] == "forbid"
    assert model.model_config["frozen"] is True
    with pytest.raises(ValidationError):
        model.__class__.model_validate(
            {**model.model_dump(mode="python"), "unknown": True},
            strict=True,
        )
    field_name = next(iter(model.__class__.model_fields))
    with pytest.raises(ValidationError):
        setattr(model, field_name, getattr(model, field_name))


def test_synthesis_records_are_recursively_closed_frozen_and_canonical() -> None:
    run = _run(
        REVIEWER_IDS[:3],
        {
            ReviewerId.claude: ("shared",),
            ReviewerId.codex: ("shared",),
        },
    )
    group, fix = _valid_group_and_fix(run)
    synthesis = PanelSynthesis(
        run_sha256=_run_sha(run),
        summary="Two reviewers agree on a closed evidence-bound fix.",
        agreed_concerns=(group,),
        divergent_concerns=(),
        prioritized_fixes=(fix,),
    )
    result = finalize_panel_synthesis(run, synthesis)
    first = canonical_panel_synthesis(synthesis)

    assert first == canonical_panel_synthesis(synthesis)
    assert first.endswith(b"\n") and not first.endswith(b"\n\n")
    success = run.envelopes[0]
    missing = run.envelopes[-1]
    assert success.capability is not None
    assert success.invocation is not None
    capability = success.capability
    invocation = success.invocation
    assert capability.stdout.path != invocation.stdout.path
    assert capability.stderr.path != invocation.stderr.path
    assert capability.argv_sha256 != invocation.argv_sha256
    assert capability.argv_count != invocation.argv_count
    assert capability.started_monotonic != invocation.started_monotonic
    assert capability.ended_monotonic != invocation.ended_monotonic
    assert capability.stdout.sha256 != invocation.stdout.sha256
    assert capability.stdout.retained_bytes != invocation.stdout.retained_bytes

    for model in (
        synthesis,
        group,
        fix,
        group.concerns[0],
        fix.evidence[0],
        result,
        run,
        success,
        capability,
        invocation,
        invocation.stdout,
        invocation.stderr,
        missing,
        missing.issues[0],
    ):
        _assert_closed_and_frozen(model)


def test_markdown_rendering_is_deterministic_and_neutralizes_heading_control_injection() -> None:
    injection = (
        "# Forged Heading\n```md\n## Consensus\n```\n"
        "<script>alert(1)</script> | [link](file:///tmp/x)\n"
        "\u202eREVERSED\u202c\u2028NEXT"
    )
    run = _run(
        REVIEWER_IDS[:3],
        {ReviewerId.claude: ("singleton",)},
        injected_text=injection,
    )
    synthesis = PanelSynthesis(
        run_sha256=_run_sha(run),
        summary=injection,
        agreed_concerns=(),
        divergent_concerns=(_ref(ReviewerId.claude, "singleton"),),
        prioritized_fixes=(),
    )
    result = finalize_panel_synthesis(run, synthesis)

    first = render_panel_markdown(run, synthesis, result)
    second = render_panel_markdown(run, synthesis, result)

    assert first == second
    assert first.endswith("\n") and not first.endswith("\n\n")
    assert "<script>" not in first
    assert "file:///tmp/x" not in first
    assert "\u202e" not in first and "\u2028" not in first
    headings = [line for line in first.splitlines() if line.startswith("#")]
    assert headings == [
        "# Panel Review",
        "## Summary",
        "## MVP Triage",
        "## Agreed Concerns",
        "## Divergent Views",
        "## Prioritized Fix Plan",
        "## Response Completeness",
        "## Advisory Boundary",
    ]
    assert "no changes were applied" in first.lower()


def test_the_rendered_report_states_what_each_response_cost_to_read() -> None:
    """A dropped concern no reader is told about is worse than the parse failure
    per-concern salvage exists to remove.
    """

    successful = (ReviewerId.claude, ReviewerId.codex, ReviewerId.qwen)
    run = _run(
        successful,
        {
            ReviewerId.claude: ("one",),
            ReviewerId.codex: ("two",),
            ReviewerId.qwen: ("three",),
        },
    )
    def _with_salvage(envelope: ReviewerEnvelope, salvage: ResponseSalvage) -> ReviewerEnvelope:
        return ReviewerEnvelope.model_validate(
            envelope.model_dump(mode="python") | {"response_salvage": salvage}
        )

    complete = ResponseSalvage(
        transport="jsonl",
        preamble_lines=0,
        trailing_lines=0,
        declared_concern_count=1,
        retained_concern_count=1,
        dropped=(),
        complete=True,
    )
    salvaged = _with_salvage(
        run.envelopes[0],
        ResponseSalvage(
            transport="jsonl",
            preamble_lines=1,
            trailing_lines=0,
            declared_concern_count=2,
            retained_concern_count=1,
            dropped=(
                {
                    "position": 3,
                    "reason": "concern cites an artifact outside the request: src/x.py",
                    "byte_count": 220,
                },
            ),
            complete=False,
        ),
    )
    envelopes = (
        salvaged,
        _with_salvage(run.envelopes[1], complete),
        _with_salvage(run.envelopes[2], complete),
    ) + run.envelopes[3:]
    run = PanelRun.model_validate(
        run.model_dump(mode="python") | {"schema_version": 3, "envelopes": envelopes}
    )
    synthesis = PanelSynthesis(
        schema_version=1,
        run_sha256=_run_sha(run),
        summary="Three reviewers disagreed on everything.",
        agreed_concerns=(),
        divergent_concerns=(
            _ref(ReviewerId.claude, "one"),
            _ref(ReviewerId.codex, "two"),
            _ref(ReviewerId.qwen, "three"),
        ),
        prioritized_fixes=(),
    )

    rendered = render_panel_markdown(run, synthesis, finalize_panel_synthesis(run, synthesis))

    completeness = rendered.split("## Response Completeness\n")[1].split("## Advisory Boundary")[0]
    assert "claude: 1 concerns retained, 1 dropped" in completeness
    assert "1 preamble and 0 trailing lines ignored, 2 declared" in completeness
    assert "position 3" in completeness and "220 bytes" in completeness
    assert "src/x.py" in completeness
    assert "codex: 1 concerns, response read complete." in completeness
    assert "gemini" not in completeness


def test_a_legacy_run_says_its_completeness_was_never_recorded() -> None:
    """Pre-salvage evidence must not read as though it had been read completely."""

    from gnd.review.report import _completeness_lines

    legacy = _run(
        (ReviewerId.claude, ReviewerId.codex, ReviewerId.qwen),
        {ReviewerId.claude: ("one",)},
    )

    assert legacy.schema_version == 1
    lines = _completeness_lines(legacy)
    assert "- claude: 1 concerns; completeness not recorded." in lines
    assert all("read complete" not in line for line in lines)


def _tree_snapshot(root: Path) -> tuple[tuple[str, str, int, bytes], ...]:
    rows: list[tuple[str, str, int, bytes]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        mode = path.lstat().st_mode
        if path.is_dir():
            rows.append((relative, "directory", mode, b""))
        elif path.is_file():
            with builtins.open(path, "rb") as stream:
                rows.append((relative, "file", mode, stream.read()))
        else:
            rows.append((relative, "other", mode, b""))
    return tuple(rows)


def test_finalization_and_rendering_have_no_reviewed_artifact_writer_surface(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    reviewed_root = tmp_path / "reviewed"
    reviewed_root.mkdir()
    reviewed = reviewed_root / "plan.md"
    reviewed.write_bytes(b"immutable reviewed bytes")
    nested = reviewed_root / "evidence"
    nested.mkdir()
    (nested / "context.md").write_bytes(b"retained context bytes")
    before = _tree_snapshot(reviewed_root)
    run = _run(REVIEWER_IDS[:3])
    synthesis = _empty_synthesis(run)

    def forbidden(*_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError("advisory finalization must not write files")

    real_open = builtins.open

    def guarded_open(
        file: Any,
        mode: str = "r",
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if any(flag in mode for flag in "wax+"):
            raise AssertionError(
                f"advisory finalization attempted builtins.open({file!r}, {mode!r})"
            )
        return real_open(file, mode, *args, **kwargs)

    real_os_open = os.open
    write_flags = os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC

    def guarded_os_open(path: Any, flags: int, *args: Any, **kwargs: Any) -> int:
        if flags & write_flags:
            raise AssertionError(
                f"advisory finalization attempted os.open({path!r}, flags={flags})"
            )
        return real_os_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(Path, "write_bytes", forbidden)
    monkeypatch.setattr(builtins, "open", guarded_open)
    monkeypatch.setattr(os, "open", guarded_os_open)
    result = finalize_panel_synthesis(run, synthesis)
    rendered = render_panel_markdown(run, synthesis, result)

    assert rendered
    descriptor = os.open(reviewed, os.O_RDONLY)
    os.close(descriptor)
    assert _tree_snapshot(reviewed_root) == before
    for function in (finalize_panel_synthesis, render_panel_markdown):
        parameters = inspect.signature(function).parameters
        assert not {
            "repository_root",
            "artifact_path",
            "writer",
            "callback",
            "apply",
        } & set(parameters)


def test_the_report_counts_retained_concerns_by_relevance() -> None:
    """The MVP triage is computed from retained concerns, not reviewer prose.

    Three reviewers, one shared blocking concern each and one completeness
    concern each: the section must report 3 of 6 blocking. The count comes from
    the run's own retained concerns, so a reviewer summary claiming otherwise
    cannot move it.
    """

    reviewers = REVIEWER_IDS[:3]
    run = _run(reviewers, {reviewer: ("shared", "solo") for reviewer in reviewers})
    synthesis = PanelSynthesis(
        run_sha256=_run_sha(run),
        summary="Three seats returned.",
        agreed_concerns=(),
        divergent_concerns=tuple(
            _ref(reviewer, concern_id)
            for reviewer in reviewers
            for concern_id in ("shared", "solo")
        ),
        prioritized_fixes=(),
    )
    rendered = render_panel_markdown(run, synthesis, finalize_panel_synthesis(run, synthesis))

    assert "**3 of 6 retained concerns are blocking** (0 hardening, 3 completeness)." in rendered
    assert "No blocking concern was reported." not in rendered


def test_a_round_with_no_blocking_concern_says_the_next_instrument_is_code() -> None:
    """The measurement that decides whether a round paid, stated in the report."""

    reviewers = REVIEWER_IDS[:3]
    run = _run(reviewers, {reviewer: ("solo",) for reviewer in reviewers})
    synthesis = PanelSynthesis(
        run_sha256=_run_sha(run),
        summary="Three seats returned.",
        agreed_concerns=(),
        divergent_concerns=tuple(_ref(reviewer, "solo") for reviewer in reviewers),
        prioritized_fixes=(),
    )
    rendered = render_panel_markdown(run, synthesis, finalize_panel_synthesis(run, synthesis))

    assert "**0 of 3 retained concerns are blocking** (0 hardening, 3 completeness)." in rendered
    assert "the next instrument is implementation rather than another round" in rendered
