"""Deterministic validation and rendering for advisory panel synthesis."""

from __future__ import annotations

import hashlib
import html
import json
import unicodedata
from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

from gnd.review.adapters import REVIEWER_IDS, ReviewerId
from gnd.review.constants import REVIEW_QUORUM
from gnd.review.request import ReviewerResponse
from gnd.review.runner import (
    ARTIFACTS_BY_REFERENCE_SCHEMA_VERSION,
    PanelRun,
    ReviewerStatus,
    canonical_panel_run,
)

__all__ = [
    "ConcernEvidenceRef",
    "ConcernGroup",
    "ConcernRef",
    "PanelResult",
    "PanelSynthesis",
    "PrioritizedFix",
    "ReviewReportError",
    "canonical_panel_synthesis",
    "finalize_panel_synthesis",
    "render_panel_markdown",
]


SHA256_PATTERN = r"^[0-9a-f]{64}$"
NonEmptyText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, strict=True, min_length=1, max_length=8_192),
]
StableId = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        strict=True,
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$",
    ),
]
Severity = Literal["critical", "high", "medium", "low"]
_CLOSED = ConfigDict(extra="forbid", frozen=True, strict=True)


class ReviewReportError(Exception):
    """A synthesis attempted to overclaim or lose immutable run evidence."""


class ConcernRef(BaseModel):
    """Exact concern identity; IDs are local to a reviewer."""

    model_config = _CLOSED

    reviewer_id: ReviewerId
    concern_id: StableId


class ConcernEvidenceRef(BaseModel):
    """One evidence entry from an exact retained concern."""

    model_config = _CLOSED

    reviewer_id: ReviewerId
    concern_id: StableId
    evidence_index: int = Field(ge=0)


class ConcernGroup(BaseModel):
    """A proposed semantic match; deterministic finalization proves support."""

    model_config = _CLOSED

    group_id: StableId
    severity: Severity
    title: NonEmptyText
    summary: NonEmptyText
    concerns: tuple[ConcernRef, ...]
    supporting_reviewers: tuple[ReviewerId, ...]


class PrioritizedFix(BaseModel):
    """One advisory action traced to retained concern evidence."""

    model_config = _CLOSED

    fix_id: StableId
    rank: int = Field(ge=1)
    title: NonEmptyText
    action: NonEmptyText
    concerns: tuple[ConcernRef, ...]
    evidence: tuple[ConcernEvidenceRef, ...]
    supporting_reviewers: tuple[ReviewerId, ...]


class PanelSynthesis(BaseModel):
    """Closed semantic proposal over one immutable :class:`PanelRun`."""

    model_config = _CLOSED

    schema_version: Literal[1] = 1
    run_sha256: str = Field(pattern=SHA256_PATTERN)
    summary: NonEmptyText
    agreed_concerns: tuple[ConcernGroup, ...]
    divergent_concerns: tuple[ConcernRef, ...]
    prioritized_fixes: tuple[PrioritizedFix, ...]

    @model_validator(mode="after")
    def _stable_ids_are_unique(self) -> Self:
        group_ids = tuple(group.group_id for group in self.agreed_concerns)
        if len(group_ids) != len(set(group_ids)):
            raise ValueError("agreed concern group IDs must be unique")
        fix_ids = tuple(fix.fix_id for fix in self.prioritized_fixes)
        if len(fix_ids) != len(set(fix_ids)):
            raise ValueError("prioritized fix IDs must be unique")
        ranks = tuple(fix.rank for fix in self.prioritized_fixes)
        if len(ranks) != len(set(ranks)):
            raise ValueError("prioritized fix ranks must be unique")
        return self


class PanelResult(BaseModel):
    """The separate advisory claim derived by deterministic finalization."""

    model_config = _CLOSED

    schema_version: Literal[1] = 1
    run_sha256: str = Field(pattern=SHA256_PATTERN)
    synthesis_sha256: str = Field(pattern=SHA256_PATTERN)
    advisory: Literal[True] = True
    successful_reviewer_ids: tuple[ReviewerId, ...]
    agreed_concern_count: int = Field(ge=0)
    divergent_concern_count: int = Field(ge=0)
    prioritized_fix_count: int = Field(ge=0)


def _canonical_model(model: BaseModel) -> bytes:
    return (
        json.dumps(
            model.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def canonical_panel_synthesis(synthesis: PanelSynthesis) -> bytes:
    """Return the exact digest identity of a validated semantic proposal."""

    return _canonical_model(synthesis)


def _ref_key(reference: ConcernRef | ConcernEvidenceRef) -> tuple[ReviewerId, str]:
    return reference.reviewer_id, reference.concern_id


def _ordered_reviewers(keys: set[ReviewerId]) -> tuple[ReviewerId, ...]:
    return tuple(reviewer for reviewer in REVIEWER_IDS if reviewer in keys)


def _validated_run(run: PanelRun) -> PanelRun:
    try:
        return PanelRun.model_validate(run.model_dump(mode="python"), strict=True)
    except Exception as error:
        raise ReviewReportError(f"panel run failed closed revalidation: {error}") from error


def _validated_synthesis(synthesis: PanelSynthesis) -> PanelSynthesis:
    try:
        return PanelSynthesis.model_validate(
            synthesis.model_dump(mode="python"),
            strict=True,
        )
    except Exception as error:
        raise ReviewReportError(f"panel synthesis failed closed validation: {error}") from error


def _successful_responses(
    run: PanelRun,
) -> dict[ReviewerId, ReviewerResponse]:
    responses: dict[ReviewerId, ReviewerResponse] = {}
    for envelope in run.envelopes:
        if envelope.status != ReviewerStatus.success:
            continue
        if envelope.response is None:
            raise ReviewReportError("successful envelope is missing its reviewer response")
        responses[envelope.reviewer_id] = envelope.response
    expected_ids = tuple(reviewer for reviewer in REVIEWER_IDS if reviewer in responses)
    if run.successful_reviewer_ids != expected_ids:
        raise ReviewReportError("panel run successful reviewer membership is inconsistent")
    if run.quorum_met is not (len(expected_ids) >= REVIEW_QUORUM):
        raise ReviewReportError("panel run quorum claim is inconsistent with its envelopes")
    return responses


def _concern_index(
    responses: dict[ReviewerId, ReviewerResponse],
) -> dict[tuple[ReviewerId, str], object]:
    return {
        (reviewer, concern.concern_id): concern
        for reviewer, response in responses.items()
        for concern in response.concerns
    }


def finalize_panel_synthesis(
    run: PanelRun,
    synthesis: PanelSynthesis,
) -> PanelResult:
    """Prove quorum, exact accounting, support, and fix traceability."""

    run = _validated_run(run)
    synthesis = _validated_synthesis(synthesis)
    run_sha256 = hashlib.sha256(canonical_panel_run(run)).hexdigest()
    if synthesis.run_sha256 != run_sha256:
        raise ReviewReportError("synthesis run digest does not match immutable panel evidence")
    responses = _successful_responses(run)
    if len(responses) < REVIEW_QUORUM:
        raise ReviewReportError("panel finalization requires a quorum of three reviewers")
    concerns = _concern_index(responses)
    all_keys = set(concerns)

    seen: set[tuple[ReviewerId, str]] = set()
    agreed_membership: dict[
        tuple[ReviewerId, str],
        frozenset[tuple[ReviewerId, str]],
    ] = {}
    for group in synthesis.agreed_concerns:
        keys = tuple(_ref_key(reference) for reference in group.concerns)
        if len(keys) != len(set(keys)):
            raise ReviewReportError("an agreed concern contains duplicate membership")
        unknown = set(keys) - all_keys
        if unknown:
            raise ReviewReportError("an agreed concern references an unknown concern")
        supporters = {reviewer for reviewer, _ in keys}
        if len(supporters) < 2:
            raise ReviewReportError(
                "agreement requires two distinct successful supporting reviewers"
            )
        if group.supporting_reviewers != _ordered_reviewers(supporters):
            raise ReviewReportError("agreed concern supporting reviewers are forged or incomplete")
        overlap = seen.intersection(keys)
        if overlap:
            raise ReviewReportError("a concern may appear exactly once across synthesis groups")
        group_members = frozenset(keys)
        for key in keys:
            agreed_membership[key] = group_members
        seen.update(keys)

    divergent_keys = tuple(_ref_key(reference) for reference in synthesis.divergent_concerns)
    if len(divergent_keys) != len(set(divergent_keys)):
        raise ReviewReportError("divergent concern membership contains a duplicate")
    if set(divergent_keys) - all_keys:
        failed = {reviewer for reviewer, _ in divergent_keys if reviewer not in responses}
        if failed:
            raise ReviewReportError("divergent concerns must come from successful reviewers")
        raise ReviewReportError("divergent views reference an unknown concern")
    if seen.intersection(divergent_keys):
        raise ReviewReportError("a concern cannot be both agreed and divergent")
    seen.update(divergent_keys)
    if seen != all_keys:
        raise ReviewReportError("synthesis concern accounting is missing retained concerns")

    ranks = tuple(fix.rank for fix in synthesis.prioritized_fixes)
    if ranks and set(ranks) != set(range(1, len(ranks) + 1)):
        raise ReviewReportError("prioritized fix ranks must be contiguous from one")
    for fix in synthesis.prioritized_fixes:
        fix_keys = tuple(_ref_key(reference) for reference in fix.concerns)
        if not fix_keys:
            raise ReviewReportError("a prioritized fix must address a retained concern")
        if len(fix_keys) != len(set(fix_keys)):
            raise ReviewReportError("a prioritized fix contains duplicate concerns")
        if set(fix_keys) - all_keys:
            raise ReviewReportError("a prioritized fix references an unknown concern")
        required_group_keys: set[tuple[ReviewerId, str]] = set()
        for key in fix_keys:
            required_group_keys.update(agreed_membership.get(key, frozenset((key,))))
        if set(fix_keys) != required_group_keys:
            raise ReviewReportError(
                "a prioritized fix must retain every supporter from an addressed agreed group"
            )
        supporters = {reviewer for reviewer, _ in fix_keys}
        if fix.supporting_reviewers != _ordered_reviewers(supporters):
            raise ReviewReportError("prioritized fix supporting reviewers are forged or incomplete")
        if not fix.evidence:
            raise ReviewReportError("a prioritized fix must cite retained evidence")
        evidence_keys = tuple(_ref_key(reference) for reference in fix.evidence)
        if set(evidence_keys) != set(fix_keys):
            raise ReviewReportError(
                "a prioritized fix must cite evidence for every addressed concern and supporter"
            )
        seen_evidence: set[tuple[ReviewerId, str, int]] = set()
        for evidence_ref in fix.evidence:
            identity = (
                evidence_ref.reviewer_id,
                evidence_ref.concern_id,
                evidence_ref.evidence_index,
            )
            if identity in seen_evidence:
                raise ReviewReportError("a prioritized fix contains duplicate evidence")
            seen_evidence.add(identity)
            concern = concerns[_ref_key(evidence_ref)]
            if evidence_ref.evidence_index >= len(concern.evidence):  # type: ignore[attr-defined]
                raise ReviewReportError("prioritized fix evidence index is out of range")
            evidence = concern.evidence[evidence_ref.evidence_index]  # type: ignore[attr-defined]
            requested_paths = {
                artifact.path
                for artifact in (
                    (run.request.plan,)
                    if run.request.kind == "plan"
                    else (
                        (run.request.outcome,)
                        if run.request.kind == "experiment-outcome"
                        else (run.request.spec, run.request.results, run.request.delta)
                    )
                )
            }
            if evidence.artifact_path not in requested_paths:
                raise ReviewReportError("prioritized fix evidence is outside requested artifacts")

    synthesis_sha256 = hashlib.sha256(canonical_panel_synthesis(synthesis)).hexdigest()
    return PanelResult(
        run_sha256=run_sha256,
        synthesis_sha256=synthesis_sha256,
        successful_reviewer_ids=run.successful_reviewer_ids,
        agreed_concern_count=len(synthesis.agreed_concerns),
        divergent_concern_count=len(synthesis.divergent_concerns),
        prioritized_fix_count=len(synthesis.prioritized_fixes),
    )


_MARKDOWN_PUNCTUATION = frozenset("\\`*_{}[]()#+!|>")


def _safe_text(value: str) -> str:
    visible: list[str] = []
    for character in value:
        category = unicodedata.category(character)
        if character in {"\n", "\r", "\t"} or category in {"Cc", "Cf", "Zl", "Zp"}:
            visible.append(f"\\u{ord(character):04x}")
        else:
            visible.append(character)
    escaped_html = html.escape("".join(visible), quote=True).replace("://", ":\\/\\/")
    return "".join(
        f"\\{character}" if character in _MARKDOWN_PUNCTUATION else character
        for character in escaped_html
    )


def _concerns_by_key(run: PanelRun) -> dict[tuple[ReviewerId, str], object]:
    return _concern_index(_successful_responses(run))


def _render_reference(
    reference: ConcernRef,
    concerns: dict[tuple[ReviewerId, str], object],
) -> str:
    concern = concerns[_ref_key(reference)]
    evidence = concern.evidence[0]  # type: ignore[attr-defined]
    return (
        f"{reference.reviewer_id.value}:{_safe_text(reference.concern_id)} — "
        f"{_safe_text(evidence.artifact_path)} at {_safe_text(evidence.location)} — "
        f"{_safe_text(evidence.observation)}"
    )


def _delivery_boundary(run: PanelRun) -> str:
    """State what the panel can prove about what each reviewer actually read.

    Under by-reference delivery the prompt names paths instead of carrying
    bytes, so "reviewer X saw exactly these bytes" stops being provable. The
    run proves what was OFFERED, and that the files did not change during the
    window. A reviewer that read half an artifact is indistinguishable from one
    that read all of it, and the report must say so in its own words rather
    than keep implying the older, stronger claim.
    """

    if run.schema_version < ARTIFACTS_BY_REFERENCE_SCHEMA_VERSION:
        return (
            "Every reviewer was handed the complete artifact bytes in its prompt, "
            "and those bytes were verified unchanged across the run."
        )
    if run.schema_version >= 6 and run.artifact_transport == "qwen-inline":
        return (
            "Qwen was handed the complete digest-checked artifact bytes in its prompt. "
            "The other reviewers were given artifact paths and digests and read the "
            "files themselves. For those reference-delivered seats, this run establishes "
            "what was offered and that the files did not change while it ran; it does not "
            "establish what each reviewer read. Cited evidence is evidence of engagement, "
            "never of complete reading."
        )
    return (
        "Reviewers were given artifact paths and digests, not bytes, and read the files "
        "themselves. This run establishes what was offered and that the files did not "
        "change while it ran; it does not establish what any reviewer read. Cited "
        "evidence is evidence of engagement, never of complete reading, and two "
        "reviewers may have read different things."
    )


def _completeness_lines(run: PanelRun) -> list[str]:
    """State what each retained response cost to read.

    A dropped concern that no reader is told about is worse than the parse
    failure this section exists because of.
    """

    lines: list[str] = []
    for envelope in run.envelopes:
        if envelope.status != ReviewerStatus.success or envelope.response is None:
            continue
        name = envelope.reviewer_id.value
        salvage = envelope.response_salvage
        retained = len(envelope.response.concerns)
        if salvage is None:
            lines.append(f"- {name}: {retained} concerns; completeness not recorded.")
            continue
        if salvage.complete:
            lines.append(f"- {name}: {retained} concerns, response read complete.")
            continue
        declared = (
            "none declared"
            if salvage.declared_concern_count is None
            else f"{salvage.declared_concern_count} declared"
        )
        lines.append(
            f"- {name}: {retained} concerns retained, {len(salvage.dropped)} dropped, "
            f"{salvage.preamble_lines} preamble and {salvage.trailing_lines} trailing "
            f"lines ignored, {declared}."
        )
        for entry in salvage.dropped:
            lines.append(
                f"  - position {entry.position} "
                rf"\({entry.byte_count} bytes\): {_safe_text(entry.reason)}"
            )
    for envelope in run.envelopes:
        if envelope.status != ReviewerStatus.success or envelope.response is None:
            continue
        name = envelope.reviewer_id.value
        for claim in envelope.response.artifact_reads:
            if claim.digest_matched:
                lines.append(f"- {name} reported reading {_safe_text(claim.path)}.")
            else:
                lines.append(
                    f"- **{name} reported a DIGEST MISMATCH on {_safe_text(claim.path)}** — "
                    "an integrity signal about the review itself, not a finding about "
                    "the artifact. The panel's own on-disk verification is the arbiter."
                )
        resolution = envelope.evidence_resolution
        if resolution is not None and resolution.total_concerns:
            lines.append(
                f"- {name}: {resolution.anchored_concerns} of {resolution.total_concerns} "
                "concerns anchor a verbatim quotation in the artifact bytes."
            )
            if resolution.unanchored_concern_ids:
                unanchored = ", ".join(
                    _safe_text(concern_id)
                    for concern_id in resolution.unanchored_concern_ids
                )
                lines.append(f"  - unanchored: {unanchored}")
    if not lines:
        lines.append("None.")
    return lines


def _render_mvp_triage(run: PanelRun) -> list[str]:
    """Count retained concerns by relevance -- the panel's own worth, measured.

    Computed from the retained concerns, never from a reviewer's summary or the
    synthesis prose.  The number that decides whether a round paid is
    ``blocking`` over the total: a round returning many concerns and no blocking
    ones measured the artifact's prose, not the product.  It is a measurement,
    never a gate -- nothing is dropped or refused over it.
    """

    counts = {"blocking": 0, "hardening": 0, "completeness": 0, "unclassified": 0}
    total = 0
    for concern in _concern_index(_successful_responses(run)).values():
        relevance = getattr(concern, "relevance", None) or "unclassified"
        counts[relevance] += 1
        total += 1
    if not total:
        return ["No concern was retained, so there is nothing to triage."]
    if counts["unclassified"] == total:
        # A run retained from before the relevance axis existed. Say so rather
        # than reporting zero blocking concerns, which would read as a measured
        # result instead of an absent measurement.
        return [
            (
                f"Not measured: this run predates the relevance axis, and all "
                f"{total} retained concerns are unclassified."
            )
        ]
    lines = [
        f"**{counts['blocking']} of {total} retained concerns are blocking** "
        f"({counts['hardening']} hardening, {counts['completeness']} completeness"
        + (f", {counts['unclassified']} unclassified" if counts["unclassified"] else "")
        + ").",
    ]
    if not counts["blocking"]:
        lines.append(
            "No blocking concern was reported. Every retained concern leaves the "
            "reviewed work demonstrably doing what it claims, so the next "
            "instrument is implementation rather than another round."
        )
    return lines


def render_panel_markdown(
    run: PanelRun,
    synthesis: PanelSynthesis,
    result: PanelResult,
) -> str:
    """Render fixed-heading Markdown without raw streams or writable authority."""

    expected_result = finalize_panel_synthesis(run, synthesis)
    try:
        supplied_result = PanelResult.model_validate(result.model_dump(mode="python"), strict=True)
    except Exception as error:
        raise ReviewReportError(f"panel result failed closed validation: {error}") from error
    if supplied_result != expected_result:
        raise ReviewReportError("panel result does not match deterministic finalization")
    concerns = _concerns_by_key(run)
    order = {reviewer: index for index, reviewer in enumerate(REVIEWER_IDS)}

    lines = [
        "# Panel Review",
        "## Summary",
        _safe_text(synthesis.summary),
        "## MVP Triage",
        *_render_mvp_triage(run),
        "## Agreed Concerns",
    ]
    if not synthesis.agreed_concerns:
        lines.append("None.")
    for group in sorted(synthesis.agreed_concerns, key=lambda item: item.group_id):
        lines.append(
            f"- **{_safe_text(group.severity.upper())} — {_safe_text(group.title)}**: "
            f"{_safe_text(group.summary)}"
        )
        refs = sorted(
            group.concerns,
            key=lambda ref: (order[ref.reviewer_id], ref.concern_id),
        )
        for reference in refs:
            lines.append(f"  - {_render_reference(reference, concerns)}")

    lines.append("## Divergent Views")
    if not synthesis.divergent_concerns:
        lines.append("None.")
    for reference in sorted(
        synthesis.divergent_concerns,
        key=lambda ref: (order[ref.reviewer_id], ref.concern_id),
    ):
        lines.append(f"- {_render_reference(reference, concerns)}")

    lines.append("## Prioritized Fix Plan")
    if not synthesis.prioritized_fixes:
        lines.append("None.")
    for fix in sorted(synthesis.prioritized_fixes, key=lambda item: (item.rank, item.fix_id)):
        supporters = ", ".join(reviewer.value for reviewer in fix.supporting_reviewers)
        lines.append(
            f"{fix.rank}. **{_safe_text(fix.title)}** — {_safe_text(fix.action)} "
            rf"\(supporters: {_safe_text(supporters)}\)"
        )
        for evidence_ref in fix.evidence:
            concern = concerns[_ref_key(evidence_ref)]
            evidence = concern.evidence[evidence_ref.evidence_index]  # type: ignore[attr-defined]
            lines.append(
                f"   - {_safe_text(evidence.artifact_path)} at "
                f"{_safe_text(evidence.location)} — {_safe_text(evidence.observation)}"
            )

    lines.append("## Response Completeness")
    lines.extend(_completeness_lines(run))

    lines.extend(
        (
            "## Advisory Boundary",
            "This panel is advisory only; no changes were applied to reviewed artifacts.",
            _delivery_boundary(run),
        )
    )
    return "\n".join(lines) + "\n"
