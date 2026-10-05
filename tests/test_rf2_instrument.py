"""Negative controls for the owner-approved RF2 successor instrument."""
from __future__ import annotations

import copy
import hashlib
import json

import pytest
import test_rf1_session_pins as sessions
import test_rf2_helpers as helpers
from support import rf2_session_pins as successor

from gnd import exits


@pytest.fixture(scope="module")
def live_case(tmp_path_factory):
    root = tmp_path_factory.mktemp("rf2-successor-controls")
    with pytest.MonkeyPatch.context() as patch:
        records = successor.install_capture(patch)
        built, run, observed = sessions._fresh(1, root, patch)
    tokens = {**sessions._tokens(root), **built.tokens}
    expected = json.loads(successor.ANSWERS.read_text())[successor.minor_tag()]["v1-fresh"]
    expected.pop("original_golden_sha256")
    return observed, records, built, run, root, tokens, expected


def assert_case(observed, records, built, run, root, tokens, expected):
    assert successor.prepare(observed, records, built, run, root, tokens) == expected


def test_successor_current_case_is_green(live_case):
    assert_case(*live_case)


@pytest.mark.parametrize("damage", ["digest", "stale-producer", "mint-semantics",
                                    "occurrence", "unbound", "declared-input"])
def test_successor_refuses_damage(live_case, damage, monkeypatch):
    observed, records, built, run, root, tokens, expected = live_case
    observed, records = copy.deepcopy(observed), copy.deepcopy(records)
    leaf = "attempts/0001/attempt.json"
    data = json.loads(observed["evidence"][leaf]["text"])
    digest = data["assurance_receipts"][0]["process_receipt"]["execution"]["identity"]
    row = next(row for row in records if row["identity"] == digest)
    if damage == "digest":
        row["identity"] = "0" * 64
    elif damage == "stale-producer":
        row["input"]["production_roster_digest"] = "0" * 64
    elif damage == "mint-semantics":
        row["input"]["band"] = 70
        altered = hashlib.sha256(successor.independent_bytes(row["input"])).hexdigest()
        row["identity"] = altered
        observed["evidence"][leaf]["text"] = observed["evidence"][leaf]["text"].replace(digest, altered)
    elif damage == "occurrence":
        observed["evidence"]["attempts/0003/attempt.json"] = observed["evidence"].pop(leaf)
    elif damage == "unbound":
        observed["evidence"][leaf]["text"] = observed["evidence"][leaf]["text"].replace(digest, "0" * 64)
    else:
        original = type(built).inputs
        def changed(self, selected_run=None):
            values = original(self, selected_run)
            values["prompt"] += b"changed input"
            return values
        monkeypatch.setattr(type(built), "inputs", changed)
    with pytest.raises(AssertionError):
        assert_case(observed, records, built, run, root, tokens, expected)


@pytest.mark.parametrize("damage", ["changed-value", "extra-name"])
def test_exit_union_refuses_damage(monkeypatch, damage):
    if damage == "changed-value":
        monkeypatch.setattr(exits, "EXIT_DRIFT", 9)
    else:
        monkeypatch.setattr(exits, "EXIT_EXTRA", 19, raising=False)
    with pytest.raises(AssertionError):
        helpers.test_all_exit_allocations_have_one_home_and_old_aliases()


def test_historical_golden_bytes_are_bound(live_case, monkeypatch, tmp_path):
    observed, records, built, run, root, tokens, _expected = live_case
    path = tmp_path / "golden.json"
    path.write_bytes(successor.golden_path("session", "v1-fresh").read_bytes() + b" ")
    monkeypatch.setattr(successor, "golden_path", lambda *_: path)
    with pytest.raises(AssertionError):
        successor.assert_successor("v1-fresh", observed, records, built, run, root, tokens)


def test_all_original_rf1_interpreters_have_successors():
    from support.rf1_pins import MINORS
    answers = json.loads(successor.ANSWERS.read_text())
    assert set(answers) == set(MINORS)
    for rows in answers.values():
        assert set(rows) == {"v1-fresh", "v2-fresh", "v1-resume", "v2-resume"}


def test_dual_capture_cannot_bypass_historical_answer(live_case, monkeypatch, tmp_path):
    observed, records, built, run, root, tokens, _expected = live_case
    monkeypatch.setenv("GND_RF1_CAPTURE", str(tmp_path / "old-capture"))
    monkeypatch.setenv("GND_RF2_SUCCESSOR_CAPTURE", str(tmp_path / "new-capture"))
    with pytest.raises(AssertionError):
        successor.assert_successor("v1-fresh", observed, records, built, run, root, tokens)
    assert not (tmp_path / "new-capture").exists()


def test_declared_json_input_whitespace_remains_bound():
    assert successor.project_input(b'{"a":1}', {}) != successor.project_input(b'{"a": 1}', {})


def test_declared_input_escaped_path_placeholder_preserves_bytes():
    path = '/tmp/root"with\\slash'
    raw = json.dumps({"path": path}, ensure_ascii=False).encode()
    answer = successor.project_input(raw, {path: "<root>"})
    assert answer == {"text": '{"path": "<root>"}'}
    changed = json.dumps({"path": path, "extra": True}, ensure_ascii=False).encode()
    assert successor.project_input(changed, {path: "<root>"}) != answer
