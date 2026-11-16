from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from gnd.artifacts import canonical_json_bytes
from gnd.examples.literature import reading, revision

EXPECTED = json.loads((Path(__file__).parent / "fixtures/ld5-verdict/expected.json").read_bytes())


@pytest.fixture(scope="module")
def release(tmp_path_factory):
    from gnd.examples.literature import verdict

    root = tmp_path_factory.mktemp("ld5")
    read_run = root / "reading"
    reading.run(read_run)
    out = root / "release"
    revision.run(read_run, out)
    return verdict, out


def _read(path):
    return json.loads(path.read_bytes())


def _digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _rebind(root, paths):
    manifest = root / "after/manifest.json"
    value = _read(manifest)
    replacements = {name: _digest((root / "after" / name).read_bytes()) for name in paths}
    for row in value["artifacts"]:
        if row["path"] in replacements:
            row["sha256"] = replacements[row["path"]]
    manifest.write_bytes(canonical_json_bytes(value))


def _result(report):
    return {"decision": report["decision"], "effective": report["effective"],
            "states": [item["state"] for item in report["supports"]]}


def test_fixture_replays_both_then_one_then_zero_supports_and_explicit_review_renewal(release, tmp_path):
    verdict, root = release
    report = verdict.run(root, tmp_path / "verdict-run")
    assert {key: _result(value) for key, value in report.items()} == EXPECTED
    assert verdict.replay(root, tmp_path / "verdict-run") == report


@pytest.mark.parametrize(("path", "key"), (
    ("claims.json", "claim"),
    ("decisions.json", "decision"),
    ("rule.json", "rule"),
    ("definition.json", "definition"),
))
def test_rehashed_global_semantic_artifact_requires_revalidation(release, tmp_path, path, key):
    verdict, root = release
    candidate = tmp_path / "release"
    shutil.copytree(root, candidate)
    artifact = candidate / "after" / path
    value = _read(artifact)
    value["change-control"] = "proposed by the snapshot"
    artifact.write_bytes(canonical_json_bytes(value))
    _rebind(candidate, [path])
    observed = verdict.evaluate(candidate, "both-approved")
    assert observed["decision"] == "revalidation-required" and observed["effective"] == []
    assert key in observed["stale_bindings"]


@pytest.mark.parametrize(("leaf", "field", "reason"), (
    ("support.json", "occurrence", "occurrence"),
    ("support.json", "resolution_edition", "resolution_edition"),
    ("review.json", "policy_sha256", "review"),
))
def test_rehashed_one_support_keeps_the_other_certificate(release, tmp_path, leaf, field, reason):
    verdict, root = release
    candidate = tmp_path / "release"
    shutil.copytree(root, candidate)
    path = f"supports/whale-a/{leaf}"
    artifact = candidate / "after" / path
    value = _read(artifact)
    if field == "occurrence":
        value[field] = {**value[field], "index": 99}
    else:
        value[field] = "0" * 64
    artifact.write_bytes(canonical_json_bytes(value))
    _rebind(candidate, [path])
    observed = verdict.evaluate(candidate, "both-approved")
    assert observed["effective"] == ["corroboration"]
    assert observed["supports"][0] == {"source": "whale-a", "state": "stale", "reason": reason}


def test_a_candidate_cannot_repin_its_own_opinions(release, tmp_path):
    verdict, root = release
    altered = tmp_path / "verdicts.json"
    doc = _read(verdict.OPINIONS)
    first = doc["cases"][0]["source_opinions"][0]
    first["verdict"] = "reject"
    altered.write_bytes(canonical_json_bytes(doc))
    with pytest.raises(ValueError, match="verdict digest"):
        verdict.evaluate(root, "both-approved", opinions=altered, opinions_sha256=verdict.OPINIONS_SHA256)


def test_invalid_pinned_opinion_shapes_fail_before_release_reads(tmp_path):
    from time import monotonic

    from gnd.examples.literature import verdict

    fixture = tmp_path / "opinions.json"
    release = tmp_path / "missing-release"
    document = _read(verdict.OPINIONS)
    first = document["cases"][0]
    empty = {**document, "cases": [{**first, "source_opinions": []}, *document["cases"][1:]]}
    duplicate = {**document, "cases": [first] * len(document["cases"])}
    started = monotonic()
    for raw in (b" " * (1 << 20), b"[" * 3000 + b"]" * 3000, b'{"value":NaN}',
                canonical_json_bytes(empty), canonical_json_bytes(duplicate)):
        fixture.write_bytes(raw)
        with pytest.raises((ValueError, verdict.ArtifactError)):
            verdict.evaluate(release, "both-approved", opinions=fixture, opinions_sha256=_digest(raw))
    assert monotonic() - started < 3
