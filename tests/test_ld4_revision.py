from __future__ import annotations

import hashlib
import json
import shutil
import time
from pathlib import Path

import pytest

from gnd.artifacts import canonical_json_bytes
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
    assert report["changed_occurrences"] == [{
        "occurrence": ["whale-b", "method_builds_on_method", 0],
        "before": {"method": "WHAM", "base_method": "VampNet"},
        "after": {"method": "WhAM [whale]", "base_method": "VampNet [music]"},
    }]
    assert {"population.json", "reviews.json", "witness.json", "scoped-absence.json", "claims.json"} <= set(
        report["affected_artifacts"],
    )
    assert "reading/coverage.json" not in report["affected_artifacts"]
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
    assert len({row["occurrence"]["document_sha256"] for row in report["supports"]}) == 2
    for row in report["supports"]:
        occurrence = row["occurrence"]
        span = occurrence["span"]
        document = (out / f"after/sources/{row['source']}/document.txt").read_bytes()
        assert hashlib.sha256(document[span["start"]:span["end"]]).hexdigest() == span["sha256"]
        assert revision.replay_support(out, row["source"]) == row


@pytest.mark.parametrize(("removed", "surviving"), (("whale-a", "corroboration"), ("corroboration", "whale-a")))
def test_another_missing_support_does_not_change_an_independent_certificate(release, tmp_path, removed, surviving):
    revision, out, report = release
    candidate = tmp_path / "release"
    shutil.copytree(out, candidate)
    (candidate / f"after/sources/{removed}/document.txt").unlink()
    expected = next(row for row in report["supports"] if row["source"] == surviving)
    assert revision.replay_support(candidate, surviving) == expected
    with pytest.raises(ValueError, match="support evidence is stale"):
        revision.replay_support(candidate, removed)


def test_every_required_kind_and_transitive_staleness(release, tmp_path):
    revision, out, _ = release
    candidate = tmp_path / "after"
    shutil.copytree(out / "after", candidate)
    shutil.copytree(out / "before", tmp_path / "before")
    policy = revision.POLICY
    pin = _pin(policy)
    rows = _read(policy)["snapshots"]["after"]
    all_paths = {row["path"] for row in rows}
    assert set(EXPECTED["required_kinds"]) <= {row["kind"] for row in rows}
    for kind in EXPECTED["required_kinds"]:
        row = next(row for row in rows if row["kind"] == kind)
        path = row["path"]
        artifact = candidate / path
        raw = artifact.read_bytes()
        artifact.write_bytes(raw + b" ")
        try:
            state = revision.status(candidate, policy=policy, policy_sha256=pin)
            expected_stale = {path}
            while True:
                expanded = {row["path"] for row in rows if expected_stale.intersection(row["requires"])}
                if expanded <= expected_stale:
                    break
                expected_stale |= expanded
            assert state["changed"] == [path], kind
            assert set(state["stale"]) == expected_stale, kind
            assert set(state["current"]) == all_paths - expected_stale, kind
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


def test_policy_rejects_escape_and_forward_dependencies_before_candidate_read(release, tmp_path):
    revision, _, _ = release
    policy = tmp_path / "policy.json"
    for changed in ({"path": "../outside.json"}, {"path": "x" * 121}, {"requires": ["claims.json"]}):
        document = _read(revision.POLICY)
        document["snapshots"]["after"][0].update(changed)
        _write(policy, document)
        with pytest.raises(ValueError, match="invalid release policy dependency or path"):
            revision.status(tmp_path / "after", policy=policy, policy_sha256=_pin(policy))


def test_snapshot_identity_and_symlink_cannot_supply_required_artifact(release, tmp_path):
    revision, out, _ = release
    candidate = tmp_path / "after"
    shutil.copytree(out / "before", candidate)
    with pytest.raises(ValueError, match="release manifest identity"):
        revision.status(candidate)
    shutil.copytree(out / "after", candidate, dirs_exist_ok=True)
    evidence = candidate / "reading/coverage.json"
    evidence.unlink()
    evidence.symlink_to(out / "after/reading/coverage.json")
    state = revision.status(candidate)
    assert "reading/coverage.json" in state["changed"] and "claims.json" in state["stale"]


def test_dependencies_follow_actual_producers_and_prior_snapshot(release, tmp_path):
    revision, out, _ = release
    candidate = tmp_path / "release"
    shutil.copytree(out, candidate)
    after = candidate / "after"
    cases = (
        ("after/sources/resolution.json", {"decisions.json", "witness.json"}, {"sources/whale-a/document.txt"}),
        ("after/decisions.json", {"reviews.json"}, {"sources/resolution.json", "witness.json"}),
        ("after/evolution/proposal.json", {"evolution/model.orm.yaml", "evolution/reviews.json"}, {"witness.json"}),
        ("before/composition.json", {"migration.json", "claims.json"}, {"supports/corroboration/support.json"}),
    )
    for path, stale, current in cases:
        artifact = candidate / path
        original = artifact.read_bytes()
        artifact.write_bytes(original + b" ")
        state = revision.status(after)
        assert stale <= set(state["stale"]), path
        assert current <= set(state["current"]), path
        artifact.write_bytes(original)
    shutil.rmtree(candidate / "before")
    state = revision.status(after)
    assert set(state["prior_stale"]) == {"before/composition.json", "before/population.json"}
    assert "migration.json" in state["stale"]


def test_prior_replay_uses_retained_reading_source(release, monkeypatch):
    revision, out, report = release
    original = reading._read

    def retained_only(root, name):
        if root == reading.FIXTURE and name == "study.txt":
            raise FileNotFoundError("the packaged reader no longer has this source")
        return original(root, name)

    monkeypatch.setattr(reading, "_read", retained_only)
    assert revision.replay(out, snapshot="before")["witness_sha256"] == report["before_witness_sha256"]


def test_rehashed_interpretation_cannot_reuse_saved_source_approval(release, tmp_path):
    revision, out, _ = release
    candidate = tmp_path / "release"
    shutil.copytree(out, candidate)
    snapshot = candidate / "after"
    policy_path = snapshot / "interpretation.json"
    review_path = snapshot / "supports/whale-a/review.json"
    support_path = snapshot / "supports/whale-a/support.json"
    policy = {**_read(policy_path), "policy": "Require evidence that each source disputes the named ancestry."}
    policy_path.write_bytes(canonical_json_bytes(policy))
    review_path.write_bytes(canonical_json_bytes({**_read(review_path), "policy_sha256": _pin(policy_path)}))
    support_path.write_bytes(canonical_json_bytes({**_read(support_path), "review_sha256": _pin(review_path)}))
    manifest_path = snapshot / "manifest.json"
    manifest = _read(manifest_path)
    replacements = {path.relative_to(snapshot).as_posix(): _pin(path)
                    for path in (policy_path, review_path, support_path)}
    for row in manifest["artifacts"]:
        if row["path"] in replacements:
            row["sha256"] = replacements[row["path"]]
    _write(manifest_path, manifest)
    assert revision.status(snapshot)["status"] == "current"
    with pytest.raises(ValueError, match="interpretation policy"):
        revision.replay_support(candidate, "whale-a")


def test_no_covered_occurrence_change_keeps_absence_current(release):
    revision, out, _ = release
    after = out / "after"
    roster = _read(after / "reading/coverage.json")
    prior = {"coverage": roster["rows"], "revisit": EXPECTED["coverage"]["revisit"]}
    change = {"occurrence": ["other-source", "unrelated_fact", 0]}
    result = revision._coverage_impact(after, prior, [change])
    assert result == {"affected": {}, "revisit": [], "unrelated": {"denial": "current"}}


def test_public_rule_comparison_refuses_changed_vocabulary(release, tmp_path):
    revision, out, _ = release
    shutil.copytree(out / "after/comparison", tmp_path / "comparison")
    model_path = tmp_path / "comparison/head.orm.json"
    model = _read(model_path)
    model["object_types"].append({"id": "extra", "name": "Extra", "kind": "value", "primitive": "String"})
    _write(model_path, model)
    with pytest.raises(ValueError, match="check exited 3"):
        revision._rule_comparison(tmp_path)


def test_additive_refusal_must_identify_the_predicate_edit(release, tmp_path, monkeypatch):
    revision, out, _ = release
    after = tmp_path / "after"
    shutil.copytree(out / "after", after)
    command = revision._command

    def unrelated_refusal(root, *arguments):
        observed = command(root, *arguments)
        if arguments[:2] == ("evolve", "preview") and "--policy" in arguments:
            report = root / "additive.json"
            body = _read(report)
            body["policy_issues"][0]["operation_id"] = "different-edit"
            _write(report, body)
        return observed

    monkeypatch.setattr(revision, "_command", unrelated_refusal)
    with pytest.raises(ValueError, match="must reject the predicate edit"):
        revision._transition(after, _read(after / "review-inputs.json"))
