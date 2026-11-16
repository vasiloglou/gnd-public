from __future__ import annotations

import hashlib
import json
import shutil
import time
from pathlib import Path

import pytest

from gnd.examples.literature import reading

EXPECTED = json.loads((Path(__file__).parent / "fixtures/ld4-revision/expected.json").read_bytes())


def _read(path):
    return json.loads(path.read_bytes())


def _write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def _pin(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def release(tmp_path_factory):
    from gnd.examples.literature import revision

    root = tmp_path_factory.mktemp("ld4")
    read_run = root / "reading"
    reading.run(read_run)
    out = root / "release"
    return revision, out, revision.run(read_run, out)


def test_release_replays_prior_and_current_relations(release):
    revision, out, report = release
    assert report["queries"] == EXPECTED["queries"]
    assert report["occurrences"] == EXPECTED["occurrences"]
    assert report["ambiguous"] == EXPECTED["ambiguous"]
    assert report["coverage"] == EXPECTED["coverage"]
    assert report["evolution"] == EXPECTED["evolution"]
    assert report["rule_comparison"] == EXPECTED["rule_comparison"]
    before = out / "before" / "witness.json"
    digest = _pin(before)
    assert revision.replay(out) == report
    assert _pin(before) == digest == report["before_witness_sha256"]
    prior = revision.replay(out, snapshot="before")
    assert prior["witness_sha256"] == digest
    assert prior["queries"] == [row[:3] for row in EXPECTED["queries"]]
    assert report["resolution_edition"] != report["rule_edition"]


def test_both_current_supports_are_individually_replayable(release):
    revision, out, report = release
    assert [row["source"] for row in report["supports"]] == EXPECTED["independent_support_sources"]
    assert len({row["review_sha256"] for row in report["supports"]}) == 2
    assert len({row["witness_sha256"] for row in report["supports"]}) == 2
    for row in report["supports"]:
        assert revision.replay_support(out, row["source"]) == row


def test_every_required_kind_and_transitive_staleness(release, tmp_path):
    revision, out, _ = release
    candidate = tmp_path / "after"
    shutil.copytree(out / "after", candidate)
    policy = revision.POLICY
    pin = _pin(policy)
    rows = _read(policy)["snapshots"]["after"]
    assert set(EXPECTED["required_kinds"]) <= {row["kind"] for row in rows}
    for kind in EXPECTED["required_kinds"]:
        row = next(row for row in rows if row["kind"] == kind)
        path = row["path"]
        artifact = candidate / path
        raw = artifact.read_bytes()
        artifact.write_bytes(raw + b" ")
        try:
            state = revision.status(candidate, policy=policy, policy_sha256=pin)
            assert path in state["changed"], kind
            assert path in state["stale"], kind
            if path in {"reading/coverage.json", "definition.json"}:
                assert "claims.json" in state["stale"]
                assert "sources/whale-a/document.txt" in state["current"]
        finally:
            artifact.write_bytes(raw)


def test_policy_precedes_candidate_and_requires_exact_roster(release, tmp_path):
    revision, out, _ = release
    policy = revision.POLICY
    with pytest.raises(ValueError, match="policy digest"):
        revision.status(tmp_path / "missing", policy=policy, policy_sha256="0" * 64)
    candidate = tmp_path / "after"
    shutil.copytree(out / "after", candidate)
    marker = candidate / "manifest.json"
    original = _read(marker)
    (candidate / "reading/coverage.json").unlink()
    missing_coverage = [row for row in original["artifacts"] if row["path"] != "reading/coverage.json"]
    for rows in ([], original["artifacts"] + original["artifacts"][:1], missing_coverage):
        _write(marker, {**original, "artifacts": rows})
        with pytest.raises(ValueError, match="roster"):
            revision.status(candidate)


def test_rehashed_migration_still_requires_actual_occurrences(release, tmp_path):
    revision, out, _ = release
    candidate = tmp_path / "release"
    shutil.copytree(out, candidate)
    artifact = candidate / "after/migration.json"
    migration = _read(artifact)
    migration["occurrences"][0][-1] = 99
    _write(artifact, migration)
    marker = candidate / "after/manifest.json"
    manifest = _read(marker)
    next(row for row in manifest["artifacts"] if row["path"] == "migration.json")["sha256"] = _pin(artifact)
    _write(marker, manifest)
    with pytest.raises(ValueError, match="migration"):
        revision.replay(candidate)


def test_bounded_candidate_roster_refuses_before_payload_read(release, tmp_path):
    revision, out, _ = release
    candidate = tmp_path / "after"
    candidate.mkdir()
    marker = candidate / "manifest.json"
    manifest = _read(out / "after/manifest.json")
    started = time.monotonic()
    for payload in (
        b'{"artifacts":[NaN]}',
        b"[" * 3000 + b"]" * 3000,
        ("9" * 6000).encode(),
        b" " * (1 << 20),
        json.dumps({**manifest, "artifacts": manifest["artifacts"] * 1000}).encode(),
    ):
        marker.write_bytes(payload)
        with pytest.raises(ValueError):
            revision.status(candidate)
    assert time.monotonic() - started < 3
