









from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from gnd.review.adapters import ReviewerId
from gnd.review.request import (
    MAX_RESPONSE_PREAMBLE_LINES,
    MAX_RETAINED_DROPS,
    MVP_TRIAGE_CRITERION,
    ReviewRequestError,
    parse_reviewer_response,
    parse_reviewer_response_with_salvage,
)
from gnd.review.runner import (
    MAX_REVIEWER_CONCERNS,
    _build_prompt,
    _response_payload,
)

ARTIFACT = "plan.md"


def _concern(concern_id: str, *, path: str = ARTIFACT) -> dict[str, Any]:
    return {
        "concern_id": concern_id,
        "severity": "high",
        "relevance": "blocking",
        "title": f"Concern {concern_id}",
        "evidence": [
            {
                "artifact_path": path,
                "location": "line 12",
                "observation": f"What {concern_id} shows.",
            }
        ],
        "recommendation": f"Address {concern_id}.",
    }


def _head(
    *,
    disposition: str = "revise",
    concern_count: int | None = None,
    reviewer: str = "claude",
) -> dict[str, Any]:
    head: dict[str, Any] = {
        "schema_version": 1,
        "reviewer_id": reviewer,
        "disposition": disposition,
        "summary": "Evidence-backed response.",
    }
    if concern_count is not None:
        head["concern_count"] = concern_count
    return head


def _jsonl(head: dict[str, Any], *concerns: Any) -> bytes:
    lines = [json.dumps(head, separators=(",", ":"))]
    for concern in concerns:
        lines.append(
            concern if isinstance(concern, str) else json.dumps(concern, separators=(",", ":"))
        )
    return ("\n".join(lines) + "\n").encode("utf-8")


def _parse(raw: bytes, *, allowed: tuple[str, ...] | None = (ARTIFACT,)) -> Any:
    return parse_reviewer_response_with_salvage(
        raw,
        expected_reviewer="claude",
        allowed_artifact_paths=allowed,
    )


                                                                               


def test_json_lines_head_and_concerns_parse_complete() -> None:
    parsed = _parse(_jsonl(_head(concern_count=2), _concern("one"), _concern("two")))

    assert parsed.salvage.transport == "jsonl"
    assert parsed.salvage.complete is True
    assert parsed.salvage.declared_concern_count == 2
    assert tuple(concern.concern_id for concern in parsed.response.concerns) == ("one", "two")
    assert parsed.salvage.dropped == ()


def test_an_unparseable_concern_line_costs_only_itself() -> None:


    truncated = '{"concern_id":"two","severity":"high",'
    raw = _jsonl(_head(concern_count=3), _concern("one"), truncated, _concern("three"))

    parsed = _parse(raw)

    assert tuple(c.concern_id for c in parsed.response.concerns) == ("one", "three")
    assert [entry.position for entry in parsed.salvage.dropped] == [3]
    assert parsed.salvage.dropped[0].reason == "line is not a JSON object"
    assert parsed.salvage.dropped[0].byte_count == len(truncated)
    assert parsed.salvage.complete is False


def test_a_schema_invalid_concern_line_is_dropped_with_its_reason() -> None:


    invalid = _concern("two") | {"verdict": "CONFIRMED"}
    parsed = _parse(_jsonl(_head(), _concern("one"), invalid, _concern("three")))

    assert tuple(c.concern_id for c in parsed.response.concerns) == ("one", "three")
    assert [entry.position for entry in parsed.salvage.dropped] == [3]
    assert "Extra inputs are not permitted" in parsed.salvage.dropped[0].reason


def test_a_concern_citing_an_unrequested_path_is_dropped_not_fatal() -> None:


    raw = _jsonl(_head(), _concern("one"), _concern("two", path="src/elsewhere.py"))
    parsed = _parse(raw)

    assert tuple(c.concern_id for c in parsed.response.concerns) == ("one",)
    assert "outside the request" in parsed.salvage.dropped[0].reason
    assert "src/elsewhere.py" in parsed.salvage.dropped[0].reason


def test_a_trailing_epilogue_is_recorded_rather_than_fatal() -> None:
    raw = _jsonl(_head(), _concern("one")) + b"\nThat concludes my review.\n"
    parsed = _parse(raw)

    assert len(parsed.response.concerns) == 1
    assert parsed.salvage.trailing_lines == 1
    assert parsed.salvage.dropped == ()
    assert parsed.salvage.complete is False


def test_declared_count_disagreeing_with_retained_marks_the_response_incomplete() -> None:
    parsed = _parse(_jsonl(_head(concern_count=4), _concern("one")))

    assert parsed.salvage.declared_concern_count == 4
    assert parsed.salvage.retained_concern_count == 1
    assert parsed.salvage.complete is False


                                                                               


def test_a_garbled_head_fails_the_whole_seat() -> None:
    raw = b'{"schema_version":1,"reviewer_id":"claude","disposition":"maybe","summary":"x"}\n'

    with pytest.raises(ReviewRequestError, match="invalid"):
        _parse(raw + json.dumps(_concern("one")).encode())


def test_a_verdict_whose_every_concern_dropped_is_not_an_opinion() -> None:
    raw = _jsonl(_head(disposition="block"), _concern("one", path="src/elsewhere.py"))

    with pytest.raises(ReviewRequestError, match="artifact|concern"):
        _parse(raw)


def test_an_approve_head_carrying_any_concern_line_is_malformed() -> None:


    raw = _jsonl(_head(disposition="approve"), _concern("one") | {"verdict": "x"})

    with pytest.raises(ReviewRequestError, match="approve"):
        _parse(raw)


def test_an_approve_head_alone_is_a_complete_response() -> None:
    parsed = _parse(_jsonl(_head(disposition="approve", concern_count=0)))

    assert parsed.response.disposition == "approve"
    assert parsed.salvage.complete is True


def test_a_preamble_longer_than_the_cap_is_refused() -> None:
    noise = b"thinking out loud\n" * (MAX_RESPONSE_PREAMBLE_LINES + 1)

    with pytest.raises(ReviewRequestError, match="precede"):
        _parse(noise + _jsonl(_head(), _concern("one")))


def test_a_second_json_document_after_an_object_response_is_refused() -> None:
    whole = _head() | {"concerns": [_concern("one")]}
    raw = json.dumps(whole, separators=(",", ":")).encode() + b"\n{}\n"

    with pytest.raises(ReviewRequestError, match="more than one"):
        _parse(raw)


                                                                               


def test_the_single_object_transport_is_unchanged_for_a_valid_response() -> None:
    whole = _head() | {"concerns": [_concern("one"), _concern("two")]}
    parsed = _parse(json.dumps(whole).encode())

    assert parsed.salvage.transport == "object"
    assert parsed.salvage.complete is True
    assert len(parsed.response.concerns) == 2


def test_the_single_object_transport_drops_one_bad_element() -> None:
    whole = _head() | {
        "concerns": [_concern("one"), _concern("two") | {"verdict": "x"}, _concern("three")]
    }
    parsed = _parse(json.dumps(whole).encode())

    assert tuple(c.concern_id for c in parsed.response.concerns) == ("one", "three")
    assert [entry.position for entry in parsed.salvage.dropped] == [2]
    assert parsed.salvage.dropped[0].byte_count > 0


                                                                               








































































































                                                                               





































def test_the_prompt_states_the_json_lines_contract_and_the_advisory_cap(
    tmp_path: Path,
) -> None:
    from gnd.review.request import load_review_request

    (tmp_path / "plan.md").write_text("# Plan\n\nOne step.\n")
    digest = __import__("hashlib").sha256((tmp_path / "plan.md").read_bytes()).hexdigest()
    (tmp_path / "request.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "kind": "plan",
                "plan": {"path": "plan.md", "sha256": digest, "media_type": "text/markdown"},
                "rubric": {"name": "correctness", "criteria": ["Cite concrete evidence.", MVP_TRIAGE_CRITERION]},
            }
        )
    )
    loaded = load_review_request(tmp_path, "request.json")

    prompt = _build_prompt(loaded, ReviewerId.claude).decode("utf-8")

    assert "Return JSON Lines: one complete JSON object per line" in prompt
    assert "Line 1 is the head, and carries no concerns:" in prompt
    assert (
        f"Report at most {MAX_REVIEWER_CONCERNS} concerns, blocking first and "
        "most severe within each class."
    ) in prompt
    assert "costs that concern alone" in prompt
                                                                           
                                                                       
                                                 
    assert '"relevance":"blocking | hardening | completeness"' in prompt
    assert "relevance is a separate axis from severity and both are required." in prompt
    assert '"concern_count"' in prompt
    assert "exactly one JSON object" not in prompt
                                                                               
                                                                               
                                                                               
                                                                            
                                                     
    assert "the disposition must be revise or block" in prompt
    assert "an approving response is refused if anything surrounds it" in prompt
    assert '"artifact_reads"' in prompt


def test_a_json_lines_response_reaches_the_parser_through_the_kimi_projection() -> None:
    raw = _jsonl(_head(reviewer="kimi"), _concern("one"))

    assert _response_payload(ReviewerId.kimi, raw) == raw


                                                                               


def test_an_approve_head_cannot_hide_a_concern_in_the_trailing_run() -> None:







    raw = _jsonl(_head(disposition="approve")) + b'{"concern_id":"hidden","severity":"critical"\n'

    with pytest.raises(ReviewRequestError, match="approve"):
        _parse(raw)


def test_a_garbled_head_cannot_hide_in_the_preamble() -> None:





    raw = (
        b'{"schema_version":1,"reviewer_id":"claude","disposition":"block","summary":"must fix"\n'
        + _jsonl(_head(disposition="approve", concern_count=0))
    )

    with pytest.raises(ReviewRequestError, match="malformed JSON precedes"):
        _parse(raw)


def test_prose_around_the_response_is_still_tolerated() -> None:




    raw = (
        b"Here is my review.\n\n"
        + _jsonl(_head(), _concern("one"))
        + b"That concludes my review.\n"
    )
    parsed = _parse(raw)

    assert parsed.salvage.preamble_lines == 1
    assert parsed.salvage.trailing_lines == 1
    assert len(parsed.response.concerns) == 1


@pytest.mark.parametrize(
    ("label", "payload"),
    [
        ("deep nesting", b'{"a":' + b"[" * 10_000 + b"]" * 10_000 + b"}"),
        ("lone surrogate", b'{"concern_id":"x","title":"\\ud800"}'),
        ("bare array", b"[1,2,3]"),
        ("empty object", b"{}"),
        ("nan", b'{"concern_id":NaN}'),
        ("duplicate keys", b'{"concern_id":"a","concern_id":"b"}'),
    ],
)
def test_hostile_concern_lines_are_drops_and_never_escape_as_python_errors(
    label: str,
    payload: bytes,
) -> None:





    parsed = _parse(_jsonl(_head(), _concern("one")) + payload + b"\n")

    assert len(parsed.response.concerns) == 1, label
    assert len(parsed.salvage.dropped) == 1, label


def test_a_lone_surrogate_in_the_object_transport_is_refused_not_raised() -> None:
    raw = (
        b'{"schema_version":1,"reviewer_id":"claude","disposition":"revise",'
        b'"summary":"s","concerns":[{"title":"\\ud800"}]}'
    )

    with pytest.raises(ReviewRequestError):
        _parse(raw)


def test_a_flood_of_junk_lines_costs_a_bounded_record_not_the_seat() -> None:





    junk = b'{"x":1}\n' * 5_000
    raw = _jsonl(_head(concern_count=1), _concern("one")) + junk

    parsed = _parse(raw)

    assert len(parsed.response.concerns) == 1
    assert len(parsed.salvage.dropped) == MAX_RETAINED_DROPS
    assert parsed.salvage.dropped_overflow == 5_000 - MAX_RETAINED_DROPS
    assert parsed.salvage.complete is False


def test_the_compatibility_parser_refuses_what_it_could_not_read_whole() -> None:




    raw = _jsonl(_head(), _concern("one"), _concern("two", path="src/elsewhere.py"))

    with pytest.raises(ReviewRequestError, match="completely"):
        parse_reviewer_response(
            raw,
            expected_reviewer="claude",
            allowed_artifact_paths=(ARTIFACT,),
        )

    whole = _head() | {"concerns": [_concern("one")]}
    assert parse_reviewer_response(
        json.dumps(whole).encode(),
        expected_reviewer="claude",
        allowed_artifact_paths=(ARTIFACT,),
    ).concerns






















                                                                               


def test_an_approve_response_must_be_a_clean_document() -> None:








    approve = _jsonl(_head(disposition="approve", concern_count=0))

    with pytest.raises(ReviewRequestError, match="unread lines"):
        _parse(b'"disposition":"block","summary":"must fix"}\n' + approve)

    with pytest.raises(ReviewRequestError, match="unread lines"):
        _parse(approve + b"Thanks for reading.\n")

    assert _parse(approve).salvage.complete is True


def test_a_garbled_head_without_an_opening_brace_is_a_stated_residual_limit() -> None:







    parsed = _parse(
        b'"disposition":"block","summary":"must fix"}\n' + _jsonl(_head(), _concern("one"))
    )

    assert parsed.response.disposition == "revise"
    assert parsed.salvage.preamble_lines == 1
    assert parsed.salvage.complete is False

















def test_a_pretty_printed_json_lines_response_is_a_refusal_not_a_salvage() -> None:






    with pytest.raises(ReviewRequestError):
        _parse(b'{\n "schema_version":1,\n "reviewer_id":"claude",\n "disposition":"approve"\n}\n')

    whole = json.dumps(_head() | {"concerns": [_concern("one")]}, indent=2).encode()
    assert _parse(whole).salvage.complete is True


def test_the_advisory_concern_cap_is_not_enforced_at_parse() -> None:




    concerns = [_concern(f"c{index}") for index in range(MAX_REVIEWER_CONCERNS + 6)]
    parsed = _parse(_jsonl(_head(concern_count=len(concerns)), *concerns))

    assert len(parsed.response.concerns) == MAX_REVIEWER_CONCERNS + 6
    assert parsed.salvage.complete is True








































def test_an_object_transport_drop_records_its_normalized_length() -> None:




    element = _concern("two") | {"verdict": "x"}
    padded = json.dumps(_head() | {"concerns": [_concern("one"), element]}, indent=4)
    parsed = _parse(padded.encode())

    dropped = parsed.salvage.dropped[0]
    assert dropped.byte_count == len(json.dumps(element, separators=(",", ":")).encode())
    assert dropped.byte_count < len(json.dumps(element, indent=4).encode())


                                                                                


def test_an_unreadable_declared_count_is_recorded_and_never_costs_the_seat() -> None:






    head = _head() | {"concern_count": "not a number"}
    parsed = _parse(_jsonl(head, _concern("one")))

    assert len(parsed.response.concerns) == 1
    assert parsed.salvage.declared_concern_count is None
    assert parsed.salvage.declared_concern_count_unreadable is True
    assert parsed.salvage.complete is False


@pytest.mark.parametrize(
    ("declared", "expected"),
    [("4", 4), (4, 4), (4.0, 4), (" 7 ", 7), ("four", None), (-1, None), (True, None)],
)
def test_a_declared_count_is_read_generously_but_never_invented(
    declared: object,
    expected: int | None,
) -> None:
    concerns = [_concern(f"c{index}") for index in range(4)]
    parsed = _parse(_jsonl(_head() | {"concern_count": declared}, *concerns))

    assert parsed.salvage.declared_concern_count == expected
    assert parsed.salvage.declared_concern_count_unreadable is (expected is None)

















































                                                                                


def test_the_head_read_report_reaches_the_response_and_may_never_cost_the_seat() -> None:







    head = _head() | {"artifact_reads": [{"path": ARTIFACT, "digest_matched": True}]}
    parsed = _parse(_jsonl(head, _concern("one")))

    assert [(c.path, c.digest_matched) for c in parsed.response.artifact_reads] == [
        (ARTIFACT, True)
    ]
    assert parsed.salvage.complete is True


def test_garbage_read_entries_are_counted_and_never_fatal() -> None:
    head = _head() | {
        "artifact_reads": [
            {"path": ARTIFACT, "digest_matched": "true"},
            {"path": "../escape.md", "digest_matched": True},
            {"path": "outside-the-request.md", "digest_matched": True},
            "not an object",
            {"path": ARTIFACT, "digest_matched": True},
        ]
    }
    parsed = _parse(_jsonl(head, _concern("one")))

    assert [(c.path, c.digest_matched) for c in parsed.response.artifact_reads] == [
        (ARTIFACT, True)
    ]
    assert parsed.salvage.artifact_reads_dropped == 4
    assert parsed.salvage.complete is False


def test_a_read_report_that_is_not_a_list_is_recorded_as_unreadable() -> None:
    parsed = _parse(_jsonl(_head() | {"artifact_reads": "plan.md"}, _concern("one")))

    assert parsed.response.artifact_reads == ()
    assert parsed.salvage.artifact_reads_unreadable is True
    assert parsed.salvage.complete is False


def test_an_approval_carrying_a_digest_mismatch_is_self_contradictory() -> None:




    head = _head(disposition="approve") | {
        "artifact_reads": [{"path": ARTIFACT, "digest_matched": False}]
    }

    with pytest.raises(ReviewRequestError, match="digest mismatch"):
        _parse(_jsonl(head))


def test_a_reported_mismatch_survives_as_a_structured_signal() -> None:




    head = _head(disposition="block") | {
        "artifact_reads": [{"path": ARTIFACT, "digest_matched": False}]
    }
    parsed = _parse(_jsonl(head, _concern("one")))

    assert parsed.response.artifact_reads[0].digest_matched is False
    assert parsed.response.disposition == "block"




















def test_evidence_resolution_measures_quotes_against_the_bytes_the_panel_holds() -> None:






    from gnd.review.request import parse_reviewer_response_with_salvage as parse
    from gnd.review.runner import _resolve_evidence

    artifact_text = "The verifier runs before the agent and its exit code is the gate."
    texts = {ARTIFACT: " ".join(artifact_text.split())}

    quoting = _concern("anchored")
    quoting["evidence"][0]["observation"] = (
        "The spec says 'its exit code is the gate' which is unimplemented."
    )
    fabricated = _concern("fabricated")
    fabricated["evidence"][0]["observation"] = (
        "The spec says 'the agent runs before the verifier' which is backwards."
    )
    parsed = parse(
        _jsonl(_head(), quoting, fabricated),
        expected_reviewer="claude",
        allowed_artifact_paths=(ARTIFACT,),
    )

    resolution = _resolve_evidence(parsed.response, texts)

    assert resolution.anchored_concerns == 1
    assert resolution.total_concerns == 2
    assert resolution.unanchored_concern_ids == ("fabricated",)



















