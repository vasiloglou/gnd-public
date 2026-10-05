"""Lossless original projections stay bound to their independent case maps."""
from __future__ import annotations

import base64
import gzip
import hashlib
import io
import json
from pathlib import Path

import pytest
from support.public_migration import load_case_map, strict_json
from support.public_review_storage import migration_view

# Historical migration accounting/storage; current product assertions remain in default tests.
pytestmark = pytest.mark.evidence

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = None


@pytest.fixture(scope="module", autouse=True)
def historical_migration_view():
    # Historical archives must not be loaded by ordinary test collection.
    global MIGRATION
    with migration_view(ROOT / ".gnd-planning/milestones/public-launch/migration") as view:
        MIGRATION = view
        yield
    MIGRATION = None


def validate_archive(document, migration):
    assert set(document) == {"format", "entries"}
    assert document["format"] == "lossless-original-projections-v1"
    assert isinstance(document["entries"], list) and document["entries"]
    seen = set()
    for entry in document["entries"]:
        assert set(entry) == {"path", "sha256", "raw_base64"}
        name = entry["path"]
        assert isinstance(name, str) and Path(name).name == name
        assert name.endswith("-originals.json") and name not in seen
        seen.add(name)
        raw = base64.b64decode(entry["raw_base64"], validate=True)
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"]
        original = strict_json(raw.decode("utf-8"))
        rows = load_case_map(migration / name.replace("-originals.json", "-case-map.jsonl.gz"))
        expected = {row["source_node"]: row["source_sha256"] for row in rows}
        assert len(expected) == len(rows) and original == expected
    return seen


def archive():
    path = MIGRATION / "original-projections.json.gz"
    with path.open("rb") as stream:
        raw = stream.read(1048577)
    assert len(raw) <= 1048576
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        expanded = stream.read(2097153)
    assert len(expanded) <= 2097152
    return strict_json(expanded.decode("utf-8"))


def test_consolidated_projections_preserve_all_original_bytes_and_identities():
    assert len(validate_archive(archive(), MIGRATION)) == 230


@pytest.mark.parametrize("mutation", ["digest", "identity", "duplicate", "traversal"])
def test_projection_archive_rejects_changed_bytes_identity_duplicates_and_paths(mutation, tmp_path):
    raw = b'{"source-case-00000":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}\n'
    row = {"source_node": "source-case-00000", "source_sha256": "a" * 64}
    (tmp_path / "sample-case-map.jsonl.gz").write_bytes(gzip.compress(json.dumps(row).encode()))
    entry = {"path": "sample-originals.json", "sha256": hashlib.sha256(raw).hexdigest(), "raw_base64": base64.b64encode(raw).decode()}
    doc = {"format": "lossless-original-projections-v1", "entries": [entry]}
    assert validate_archive(doc, tmp_path) == {"sample-originals.json"}
    if mutation == "digest": entry["sha256"] = "0" * 64
    elif mutation == "identity":
        changed = raw.replace(b"aaaaaaaa", b"bbbbbbbb")
        entry.update(sha256=hashlib.sha256(changed).hexdigest(), raw_base64=base64.b64encode(changed).decode())
    elif mutation == "duplicate": doc["entries"].append(dict(entry))
    else: entry["path"] = "../sample-originals.json"
    with pytest.raises(AssertionError): validate_archive(doc, tmp_path)


def continuation_archive():
    path = MIGRATION / "original-projections-continuation.json.gz"
    with path.open("rb") as stream:
        raw = stream.read(1048577)
    assert len(raw) <= 1048576
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        expanded = stream.read(2097153)
    assert len(expanded) <= 2097152
    return strict_json(expanded.decode("utf-8"))


def test_continuation_projection_preserves_all_twenty_five_original_files():
    assert len(validate_archive(continuation_archive(), MIGRATION)) == 25


def test_all_projection_owners_are_unique_and_exhaust_case_map_shards():
    first = validate_archive(archive(), MIGRATION)
    second = validate_archive(continuation_archive(), MIGRATION)
    third = validate_archive(supplemental_archive(), MIGRATION)
    assert not first & second
    assert not third & (first | second)
    leaves = set()
    for path in MIGRATION.glob("*-originals.json"):
        assert path.name not in first | second | third
        rows = load_case_map(path.with_name(path.name.replace("-originals.json", "-case-map.jsonl.gz")))
        expected = {row["source_node"]: row["source_sha256"] for row in rows}
        assert len(expected) == len(rows)
        assert strict_json(path.read_text()) == expected
        leaves.add(path.name)
    wanted = {p.name.replace("-case-map.jsonl.gz", "-originals.json") for p in MIGRATION.glob("*-case-map.jsonl.gz")}
    assert first | second | third | leaves == wanted


def supplemental_archive():
    path = MIGRATION / "original-projections-supplemental.json.gz"
    with path.open("rb") as stream:
        raw = stream.read(1048577)
    assert len(raw) <= 1048576
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        expanded = stream.read(2097153)
    assert len(expanded) <= 2097152
    return strict_json(expanded.decode("utf-8"))


def test_supplemental_projection_preserves_all_twenty_original_files():
    assert len(validate_archive(supplemental_archive(), MIGRATION)) == 20
