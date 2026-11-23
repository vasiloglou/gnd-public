"""LH2: replay of a caller run from its folder and the caller's root."""
from __future__ import annotations

import json
import shutil
import time

import pytest
from test_lh1_reading_host import (
    ANSWERS,
    CALLER,
    Empty,
    Producer,
    Reviewer,
    _edit,
    _files,
    _root,
    _wide_root,
)

from gnd.artifacts import ArtifactError, canonical_json_bytes, sha256_hex
from gnd.examples.literature import reading
from gnd.examples.literature.assurance_report import score_reading_coverage
from gnd.examples.literature.reading import ReadingLimits


def _same(report, replayed):
    assert replayed["producer_calls"] == {"broad-extraction": 0, "targeted-extraction": 0}
    assert {k: v for k, v in replayed.items() if k != "producer_calls"} == {
        k: v for k, v in report.items() if k != "producer_calls"}


def _rewrite(run, name, change):
    """Change one file of a run and re-pin it in the manifest, leaving the rest as it is."""
    path = run / name
    path.write_bytes(change(path.read_bytes()))
    manifest = json.loads((run / "run.json").read_bytes())
    manifest["artifacts"][name] = sha256_hex(path.read_bytes())
    (run / "run.json").write_bytes(canonical_json_bytes(manifest))


def _manifest(run, change):
    manifest = json.loads((run / "run.json").read_bytes())
    change(manifest)
    (run / "run.json").write_bytes(canonical_json_bytes(manifest))


@pytest.fixture(scope="module")
def plain(tmp_path_factory):
    out = tmp_path_factory.mktemp("lh2") / "run"
    return out, reading.run(out, fixture=CALLER, producer=Producer())


@pytest.fixture(scope="module")
def declared(tmp_path_factory):
    base = tmp_path_factory.mktemp("lh2-declared")
    root = _root(base, declared=True)
    out = base / "run"
    return root, out, reading.run(out, fixture=root, producer=Producer(), reviewer=Reviewer())


def _copy(run, tmp_path, name="copy"):
    target = tmp_path / name
    shutil.copytree(run, target)
    return target


def test_t1_a_caller_run_replays_with_no_calls(plain, declared):
    out, report = plain
    before = _files(out)
    _same(report, reading.replay(out, fixture=CALLER, expected_evidence_sha256=report["evidence_sha256"]))
    assert _files(out) == before
    root, run, report = declared
    _same(report, reading.replay(run, fixture=root))
    assert json.loads((run / "run.json").read_bytes())["settings"]["reviewer"] == "live"


@pytest.mark.parametrize(("name", "old", "new"), [
    ("producer-output-table.json", b"Graph sampling", b"Graph Sampling"),
    ("reviews.json", b"the excerpt states", b"the excerpt States"),
])
def test_t2_one_changed_byte_refuses(declared, tmp_path, name, old, new):
    root, run, _ = declared
    copy = _copy(run, tmp_path)
    _rewrite(copy, name, lambda raw: raw.replace(old, new, 1))
    with pytest.raises(reading.ExampleError):
        reading.replay(copy, fixture=root)


def test_t2_a_consistent_rewrite_needs_the_expected_digest(plain, tmp_path):
    _, report = plain
    answers = {**ANSWERS, "a-results": {"outcome": "empty", "facts": {}, "proposal_keys": []}}
    other = tmp_path / "other"
    reading.run(other, fixture=CALLER, producer=Producer(answers))
    reading.replay(other, fixture=CALLER)
    with pytest.raises(reading.ExampleError, match="expected digest"):
        reading.replay(other, fixture=CALLER, expected_evidence_sha256=report["evidence_sha256"])


def test_t3_non_default_limits_replay_with_them(tmp_path):
    limits = ReadingLimits(roster=64, input_bytes=1 << 20, response_bytes=64 * 1024)
    out = tmp_path / "run"
    report = reading.run(out, fixture=CALLER, producer=Producer(), limits=limits, document_budget=200)
    replayed = reading.replay(out, fixture=CALLER)
    _same(report, replayed)
    assert replayed["settings"]["limits"]["roster"] == 64
    assert replayed["settings"]["document_budget_bytes"] == 200


def test_t3_the_response_ceiling_run_replays_in_time(tmp_path):
    root = _wide_root(tmp_path, 9)
    padding = ["k" * 1000] * ((1 << 20) // 1003 - 2)

    class Padded:
        def produce(self, call):
            return {"outcome": "empty", "facts": {}, "proposal_keys": padding}

    out = tmp_path / "run"
    report = reading.run(out, fixture=root, producer=Padded(), limits=ReadingLimits(response_bytes=1 << 20))
    started = time.monotonic()
    replayed = reading.replay(out, fixture=root)
    assert time.monotonic() - started < 60
    assert replayed["evidence_sha256"] == report["evidence_sha256"]


def test_t3_a_setting_above_its_ceiling_refuses(plain, tmp_path):
    out, _ = plain
    copy = _copy(out, tmp_path)
    _manifest(copy, lambda manifest: manifest["settings"]["limits"].update(route_seconds=601))
    with pytest.raises(reading.ExampleError, match="route_seconds"):
        reading.replay(copy, fixture=CALLER)


def _repin_source(root):
    path = root / "survey-a.txt"
    path.write_bytes(path.read_bytes() + b"Appendix.\n")
    _edit(root, "roster.json", lambda roster: roster["sources"][0].update(sha256=sha256_hex(path.read_bytes())))


@pytest.mark.parametrize("change", ["source", "profile", "model", "include"])
def test_t4_a_changed_input_refuses(plain, tmp_path, change):
    out, _ = plain
    root = _root(tmp_path)
    if change == "source":
        _repin_source(root)
    elif change == "profile":
        _edit(root, "profile.json", lambda profile: profile.update(producer_label="host-extractor-2"))
    else:
        name = "survey.orm.json" if change == "model" else "terms.orm.json"
        (root / name).write_bytes((root / name).read_bytes() + b"\n")
    with pytest.raises(reading.ExampleError, match="stale reading input"):
        reading.replay(out, fixture=root)


def test_t6_the_scorer_scores_a_caller_run(plain):
    out, report = plain
    score = score_reading_coverage(out, report["coverage"], fixture=CALLER)
    assert score["status"] == "pass"
    assert score_reading_coverage(out, report["coverage"])["status"] != "pass"


def test_t7_steps_that_differ_from_the_profile_refuse(declared, tmp_path):
    root, run, _ = declared
    copy = _copy(run, tmp_path)

    def skip(manifest):
        manifest["steps"]["calibration"] = "skipped"
        manifest["steps"]["absence"] = "skipped"
        for name in ("fidelity-high.json", "fidelity-low.json", "scope.json", "closure.json"):
            del manifest["artifacts"][name]

    _manifest(copy, skip)
    with pytest.raises(reading.ExampleError, match="reading steps differ from the profile"):
        reading.replay(copy, fixture=root)


def test_t8_each_run_replays_only_against_its_own_kind_of_root(plain, tmp_path):
    out, _ = plain
    with pytest.raises(reading.ExampleError, match="a caller run replays against its own root"):
        reading.replay(out)
    packaged = tmp_path / "packaged"
    reading.run(packaged)
    with pytest.raises(reading.ExampleError, match="a packaged run replays against the packaged root"):
        reading.replay(packaged, fixture=CALLER)


MANIFEST_DEFECTS = {
    "settings-key-missing": lambda m: m["settings"].pop("unavailable"),
    "settings-extra-key": lambda m: m["settings"].update(stop="never"),
    "retained-null": lambda m: m["settings"]["limits"].update(retained_bytes=None),
    "limit-bool": lambda m: m["settings"]["limits"].update(roster=True),
    "step-maybe": lambda m: m["steps"].update(review="maybe"),
    "roster-without-reviews": lambda m: m["artifacts"].pop("reviews.json"),
}


@pytest.mark.parametrize("case", [*sorted(MANIFEST_DEFECTS), "not-canonical"])
def test_t9_a_malformed_manifest_refuses_before_any_run_file(declared, tmp_path, monkeypatch, case):
    root, run, _ = declared
    copy = _copy(run, tmp_path)
    if case == "not-canonical":
        (copy / "run.json").write_bytes((copy / "run.json").read_bytes() + b" ")
    else:
        _manifest(copy, MANIFEST_DEFECTS[case])
    monkeypatch.setattr(reading, "_read_run_file", lambda *_: pytest.fail("read a run file"))
    with pytest.raises((reading.ExampleError, ArtifactError)):
        reading.replay(copy, fixture=root)


def test_t9_the_run_files_are_read_under_the_recorded_cap(plain, tmp_path, monkeypatch):
    out, report = plain
    seen = []
    original = reading._read_run_file

    def recording(folder, name, max_bytes):
        seen.append(max_bytes)
        return original(folder, name, max_bytes)

    monkeypatch.setattr(reading, "_read_run_file", recording)
    reading.replay(out, fixture=CALLER)
    assert seen and set(seen) == {report["settings"]["limits"]["retained_bytes"]}


def test_t9_a_saved_run_replays(tmp_path):
    root = _root(tmp_path)
    raw = canonical_json_bytes(ANSWERS)
    (root / "responses.json").write_bytes(raw)
    (root / "producer-pin.json").write_bytes(canonical_json_bytes({"sha256": sha256_hex(raw)}))
    out = tmp_path / "run"
    report = reading.run(out, fixture=root)
    _same(report, reading.replay(out, fixture=root))


def test_t9_an_empty_live_run_replays(tmp_path):
    out = tmp_path / "run"
    report = reading.run(out, fixture=CALLER, producer=Empty())
    _same(report, reading.replay(out, fixture=CALLER))


def test_r1_a_receipt_at_the_response_cap_replays(tmp_path):
    root = _root(tmp_path, profile=_profile_review())
    filler = 512 - len(canonical_json_bytes({"basis": "", "decision": "supported"}))

    class Full:
        def review(self, call):
            return {"decision": "supported", "basis": "b" * filler}

    limits = ReadingLimits(response_bytes=512)
    answers = {name: {"outcome": "empty", "facts": {}, "proposal_keys": []} for name in ANSWERS}
    answers["a-opening"] = {"outcome": "accepted", "proposal_keys": [],
                            "facts": {"paper_title": [{"paper": "p", "title": "t"}]}}
    out = tmp_path / "run"
    try:
        report = reading.run(out, fixture=root, producer=Producer(answers), reviewer=Full(), limits=limits)
    except reading.ExampleError:
        assert not out.exists()
        return
    _same(report, reading.replay(out, fixture=root))


def _profile_review():
    value = json.loads((CALLER / "profile.json").read_bytes())
    value["review"] = True
    return value


@pytest.mark.parametrize("change", [{"budget_bytes": True}, {"scenario": "unavailable"}])
def test_r2_top_level_settings_refuse_before_any_run_file(plain, tmp_path, monkeypatch, change):
    out, _ = plain
    copy = _copy(out, tmp_path)
    _manifest(copy, lambda manifest: manifest.update(change))
    monkeypatch.setattr(reading, "_read_run_file", lambda *_: pytest.fail("read a run file"))
    with pytest.raises(reading.ExampleError):
        reading.replay(copy, fixture=CALLER)


def _rechain(run, name, raw):
    """Replace one payload and re-pin it through the stage chain and the manifest."""
    (run / name).write_bytes(raw)
    manifest = json.loads((run / "run.json").read_bytes())
    manifest["artifacts"][name] = sha256_hex(raw)
    predecessor = None
    for index in range(6):
        stage = json.loads((run / f"stage-{index}.json").read_bytes())
        stage["predecessor_sha256"] = predecessor
        stage["payload_sha256"] = manifest["artifacts"][f"payload-{index}.json"]
        stage_raw = canonical_json_bytes(stage)
        (run / f"stage-{index}.json").write_bytes(stage_raw)
        manifest["artifacts"][f"stage-{index}.json"] = predecessor = sha256_hex(stage_raw)
    (run / "run.json").write_bytes(canonical_json_bytes(manifest))


@pytest.mark.parametrize("payload", [{}, {"attempts": [1]}, {"attempts": [{"section": "a-opening"}]}])
def test_r3_a_malformed_retained_payload_refuses(plain, tmp_path, payload):
    out, _ = plain
    copy = _copy(out, tmp_path)
    _rechain(copy, "payload-1.json", canonical_json_bytes(payload))
    with pytest.raises((reading.ExampleError, ArtifactError)):
        reading.replay(copy, fixture=CALLER)
