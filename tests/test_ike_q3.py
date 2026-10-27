"""IKE-Q3: an unbindable reference file is a named refusal in discover and judgments.

Spec: .gnd-planning/milestones/induced-knowledge/notes/followup-ike-q3-spec.md
(§7: Q1-Q5; rulings D1-A, D2-A). The fixture is a scratch copy of the dispatch
reference corpus, damaged by tests/support/reference_homes.py.
"""

from __future__ import annotations

import pytest
from support import reference_homes
from support.cli_runner import run_main


def _text(result) -> str:
    return (result.stdout + result.stderr).decode("utf-8", errors="replace")


def _discover(work):
    return run_main([
        "discover", str(work / "model.orm.yaml"), str(work / "candidate.pop.json"),
        "--out", str(work / "d.json"), "--report", str(work / "r.json"),
        "--actor", "h", "--requested-at", "2026-10-27T00:00:00+00:00"])


@pytest.mark.parametrize(("damage", "exit_code", "words"), [
    ("missing", 66, "could not be inspected"),  # Q1
    ("linked", 74, "is a symlink"),  # Q2
])
def test_q1_q2_discover_names_an_unbindable_reference(tmp_path, damage, exit_code, words):
    work = reference_homes.workspace(tmp_path, damage)
    result = _discover(work)
    assert result.returncode == exit_code, _text(result)
    text = _text(result)
    assert "reference population: artifact references/catalog.pop.json" in text
    assert words in text and "Traceback" not in text
    assert not (work / "d.json").exists() and not (work / "r.json").exists()


def test_q3_discover_refuses_a_directory_at_the_reference_path(tmp_path):
    work = reference_homes.workspace(tmp_path, "missing")
    (work / reference_homes.REFERENCE).mkdir()
    result = _discover(work)
    assert result.returncode == 74, _text(result)
    assert "reference population:" in _text(result)


@pytest.mark.parametrize("damage", ["missing", "linked"])
def test_q4_the_judgments_api_returns_a_binding_refusal(tmp_path, monkeypatch, damage):
    work = reference_homes.workspace(tmp_path, damage)
    result = reference_homes._judgments(work, tmp_path, monkeypatch)
    assert result["outcome"] == 3
    assert result["error"] == {"reason": "binding", "message": "invalid bound judgment input"}


@pytest.mark.parametrize("damage", ["missing", "linked"])
def test_q5_judgments_check_exits_3(tmp_path, monkeypatch, damage):
    import gnd.judgments

    work = reference_homes.workspace(tmp_path, damage)
    for name in ("policy.json", "receipts.json"):
        (tmp_path / name).write_text("{}")
    monkeypatch.setattr(gnd.judgments, "read_judgment_policy", lambda raw: {"probe": True})
    monkeypatch.setattr(gnd.judgments, "read_judgment_receipts", lambda raw: [])
    result = run_main([
        "judgments", "check", str(work / "model.orm.yaml"), str(work / "candidate.pop.json"),
        "--policy", str(tmp_path / "policy.json"), "--receipts", str(tmp_path / "receipts.json"),
        "--trusted-root", str(tmp_path)])
    assert result.returncode == 3, _text(result)
    assert "Traceback" not in _text(result)
