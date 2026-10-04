"""Transition walk guards over bounded, independently owned public test data."""
from __future__ import annotations

import atexit
import gzip
import hashlib
import io
import json
import re
import tempfile
from pathlib import Path
from typing import Any

import pytest
from test_public_transition_trace import _run


def _materialize() -> tuple[tempfile.TemporaryDirectory, Path]:
    packed = (Path(__file__).parent / "fixtures/public-transition-trace/walks.json.gz").read_bytes()
    assert len(packed) <= 65536
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(262145)
    assert len(raw) <= 262144
    assert hashlib.sha256(raw).hexdigest() == "61ddba2324f726bae13bf14f72f79ac2cab559ebf3d00111ce8dba583ae12795"
    files = json.loads(raw)
    assert isinstance(files, dict) and len(files) == 197
    allowed = {"expected.json", "pre.pop.yaml", "post.pop.yaml", "steps.json"}
    for name, text in files.items():
        parts = name.split("/")
        assert name == "v2_expense.orm.yaml" or (
            len(parts) == 3 and parts[0] == "walks"
            and re.fullmatch(r"[a-z][a-z0-9-]*", parts[1])
            and parts[2] in allowed
        )
        assert isinstance(text, str)
    temporary = tempfile.TemporaryDirectory(prefix="gnd-public-transition-walks-")
    root = Path(temporary.name)
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    return temporary, root


_TEMPORARY, CORPUS = _materialize()
atexit.register(_TEMPORARY.cleanup)
MODEL = CORPUS / "v2_expense.orm.yaml"
WALKS = CORPUS / "walks"

_SNAPSHOT_FAMILIES = {"pre_snapshot", "post_snapshot"}


_REF_FACT_TYPE = re.compile(r"fact_types\[([^\]]+)\]")



def _walks() -> list[str]:
    return sorted(d.name for d in WALKS.iterdir() if (d / "expected.json").is_file())


WALK_NAMES = _walks()



def _expected(name: str) -> dict[str, Any]:
    return json.loads((WALKS / name / "expected.json").read_text(encoding="utf-8"))



def _walk_argv(name: str) -> list[str]:
    walk = WALKS / name
    return ["check", str(MODEL),
            "--pre", str(walk / "pre.pop.yaml"),
            "--steps", str(walk / "steps.json"),
            "--post", str(walk / "post.pop.yaml")]



def _transition(payload: Any) -> dict[str, Any]:
    assert isinstance(payload, dict), "no JSON payload on stdout"
    block = payload.get("transition")
    assert isinstance(block, dict), (
        "payload carries no transition block -- report.schema.json promises a "
        "payload on every exit path, and a transition run must fill it")
    return block



def _candidates(block: dict[str, Any], expectation: dict[str, Any]) -> list[dict[str, Any]]:
    """Every verdict object an expectation could legitimately match."""
    family, kind = expectation.get("family"), expectation.get("kind")
    steps = block.get("steps") or []
    index = expectation.get("step")
    if family in _SNAPSHOT_FAMILIES and kind is None:
        report = block.get("pre_snapshot" if family == "pre_snapshot" else "post_snapshot")
        return list((report or {}).get("verdicts") or [])
    if family == "pre_snapshot":
        return list(block.get("pre_snapshot_verdicts") or [])
    if family == "frame":
        return list(block.get("frame_verdicts") or [])
    if family == "step" and kind == "intermediate":
        chosen = steps if index is None else steps[index - 1: index]
        return [v for s in chosen for v in ((s.get("intermediate") or {}).get("verdicts") or [])]
    if family == "step":
        chosen = steps if index is None else steps[index - 1: index]
        return [v for s in chosen for v in (s.get("verdicts") or [])]
    return [v for s in steps for v in (s.get("verdicts") or [])] \
        + list(block.get("frame_verdicts") or []) \
        + list(block.get("pre_snapshot_verdicts") or [])



def _matches(verdict: dict[str, Any], expectation: dict[str, Any]) -> bool:
    constraint_verdict = "constraint_ref" in verdict
    for key, wanted in expectation.items():
        if key in {"family", "step"}:
            continue
        if key == "kind" and constraint_verdict:
            # `kind: intermediate` names WHERE the finding lives -- the step's
            # embedded CheckReport -- not a field on a ConstraintVerdict, which
            # has no kind. _candidates has already narrowed to that report.
            continue
        if key == "fact_type" and not constraint_verdict:
            if verdict.get(key) != wanted:
                return False
            continue
        if key == "fact_type":
            # ConstraintVerdict: the fact type lives inside constraint_ref.
            found = _REF_FACT_TYPE.search(str(verdict.get("constraint_ref", "")))
            if not found or found.group(1) != wanted:
                return False
            continue
        if verdict.get(key) != wanted:
            return False
    return True



def _describe(block: dict[str, Any]) -> str:
    return json.dumps(block, indent=2, sort_keys=True)[:4000]



@pytest.mark.parametrize("name", WALK_NAMES)
def test_walk_exits_as_the_corpus_says(name: str, capsys: pytest.CaptureFixture[str]) -> None:
    expected = _expected(name)
    code, _ = _run(_walk_argv(name), capsys)
    assert code == expected["exit"], (
        f"{name}: expected exit {expected['exit']}, got {code}.\n"
        f"Why this walk exists: {expected['story']}")



@pytest.mark.parametrize(
    "name", [n for n in WALK_NAMES if _expected(n).get("must")])
def test_walk_reports_every_required_verdict(
    name: str, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = _expected(name)
    _, payload = _run(_walk_argv(name), capsys)
    assert isinstance(payload, dict), f"{name}: no JSON payload on stdout"
    for wanted in expected["must"]:
        if "issue" in wanted:
            ids = [i.get("rule_id") for i in payload.get("issues") or []]
            assert wanted["issue"] in ids, (
                f"{name}: expected issue {wanted['issue']}, got {ids}.\n"
                f"Why: {expected['story']}")
            continue
        if "frame_grading" in wanted:
            grading = _transition(payload).get("frame_grading") or []
            assert any(all(g.get(k) == v for k, v in wanted["frame_grading"].items())
                       for g in grading), (
                f"{name}: no frame_grading entry matching {wanted['frame_grading']}.\n"
                f"Got: {json.dumps(grading, indent=2)}")
            continue
        block = _transition(payload)
        assert any(_matches(v, wanted) for v in _candidates(block, wanted)), (
            f"{name}: no verdict matching {wanted}.\n"
            f"Why this walk exists: {expected['story']}\n"
            f"transition block:\n{_describe(block)}")



@pytest.mark.parametrize(
    "name", [n for n in WALK_NAMES if _expected(n).get("must_not")])
def test_walk_reports_no_forbidden_verdict(
    name: str, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = _expected(name)
    _, payload = _run(_walk_argv(name), capsys)
    assert isinstance(payload, dict), f"{name}: no JSON payload on stdout"
    block = _transition(payload)
    for forbidden in expected["must_not"]:
        offenders = [v for v in _candidates(block, forbidden) if _matches(v, forbidden)]
        assert not offenders, (
            f"{name}: forbidden verdict {forbidden} appeared: "
            f"{json.dumps(offenders, indent=2)}\n"
            f"Why this walk exists: {expected['story']}")



@pytest.mark.parametrize(
    "name", [n for n in WALK_NAMES if _expected(n).get("payload")])
def test_walk_payload_block(name: str, capsys: pytest.CaptureFixture[str]) -> None:
    """The evaluated flag distinguishes 'not a transition run' (transition null)
    from 'refused before evaluation' (evaluated false) without reading exit_code."""
    expected = _expected(name)
    _, payload = _run(_walk_argv(name), capsys)
    assert isinstance(payload, dict), f"{name}: no JSON payload on stdout"
    steps_doc = json.loads((WALKS / name / "steps.json").read_text(encoding="utf-8"))
    for key, wanted in expected["payload"].items():
        got = payload.get(key)
        assert isinstance(got, dict), f"{name}: payload has no {key} block"
        for field, value in wanted.items():
            if value == "<as supplied>":
                # The fixture's sentinel for "whatever the steps document said",
                # written so an expectation never duplicates a digest it would
                # then have to be kept in sync with. A refused walk must echo
                # the caller's own digests back: being told a digest mismatched
                # is not much use without being shown which one you sent.
                value = steps_doc.get(field) if isinstance(steps_doc, dict) else None
            assert got.get(field) == value, (
                f"{name}: payload.{key}.{field} is {got.get(field)!r}, "
                f"expected {value!r}")

