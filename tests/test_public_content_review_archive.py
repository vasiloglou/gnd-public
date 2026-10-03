"""Bounded lossless review storage preserves independent map and artifact bindings."""
from __future__ import annotations

import base64
import copy
import gzip
import hashlib
import io
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


def bounded_gzip(raw):
    assert len(raw) <= 1048576
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        expanded = stream.read(2097153)
    assert len(expanded) <= 2097152
    return expanded


def validate_review(raw, name, migration, root):
    assert Path(name).name == name
    suffix = "-content-review.json.gz" if name.endswith(".gz") else "-content-review.json"
    assert name.endswith(suffix)
    review = strict_json((bounded_gzip(raw) if name.endswith(".gz") else raw).decode("utf-8"))
    map_path = migration / (name.removesuffix(suffix) + "-case-map.jsonl.gz")
    assert review["case_map_file_sha256"] == hashlib.sha256(map_path.read_bytes()).hexdigest()
    rows = load_case_map(map_path)
    assert type(review["definitions"]) is int and review["definitions"] == len(rows)
    assert isinstance(review["files"], list)
    for item in review["files"]:
        path = Path(item["target"])
        assert not path.is_absolute() and ".." not in path.parts
        resolved = (root / path).resolve(strict=True)
        assert resolved.is_relative_to(root.resolve())
        assert item["target_sha256"] == hashlib.sha256(resolved.read_bytes()).hexdigest()
    return review


def validate_archive(document, migration, root):
    assert set(document) == {"format", "entries"}
    assert document["format"] == "lossless-content-reviews-v1"
    assert isinstance(document["entries"], list) and document["entries"]
    seen = set()
    for entry in document["entries"]:
        assert set(entry) == {"path", "sha256", "raw_base64"}
        name = entry["path"]
        assert isinstance(name, str) and name not in seen
        seen.add(name)
        raw = base64.b64decode(entry["raw_base64"], validate=True)
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"]
        validate_review(raw, name, migration, root)
    return seen


def archive():
    with (MIGRATION / "content-reviews.json.gz").open("rb") as stream:
        raw = stream.read(1048577)
    return strict_json(bounded_gzip(raw).decode("utf-8"))


def test_archive_preserves_281_review_files_and_their_independent_bindings():
    assert len(validate_archive(archive(), MIGRATION, ROOT)) == 281


def test_review_owners_are_unique_and_exhaust_case_map_shards():
    names = validate_archive(archive(), MIGRATION, ROOT)
    owned = {name.split("-content-review.", 1)[0] for name in names}
    assert len(owned) == len(names)
    for path in sorted(MIGRATION.glob("*-content-review.json*")):
        prefix = path.name.split("-content-review.", 1)[0]
        assert prefix not in owned
        validate_review(path.read_bytes(), path.name, MIGRATION, ROOT)
        owned.add(prefix)
    assert owned == {p.name.removesuffix("-case-map.jsonl.gz") for p in MIGRATION.glob("*-case-map.jsonl.gz")}


@pytest.mark.parametrize("mutation", ["digest", "map", "artifact", "duplicate", "traversal", "artifact_traversal", "count"])
def test_archive_rejects_broken_bytes_maps_artifacts_and_owners(mutation, tmp_path):
    import json
    (tmp_path / "sample.txt").write_bytes(b"approved\n")
    row = {"source_node": "source-case-00000", "source_sha256": "a" * 64}
    map_path = tmp_path / "sample-case-map.jsonl.gz"
    map_path.write_bytes(gzip.compress(json.dumps(row).encode(), mtime=0))
    review = {"definitions": 1, "case_map_file_sha256": hashlib.sha256(map_path.read_bytes()).hexdigest(),
              "files": [{"target": "sample.txt", "target_sha256": hashlib.sha256(b"approved\n").hexdigest()}]}
    raw = json.dumps(review).encode()
    entry = {"path": "sample-content-review.json", "sha256": hashlib.sha256(raw).hexdigest(),
             "raw_base64": base64.b64encode(raw).decode()}
    document = {"format": "lossless-content-reviews-v1", "entries": [entry]}
    assert validate_archive(document, tmp_path, tmp_path) == {entry["path"]}
    damaged = copy.deepcopy(document)
    item = damaged["entries"][0]
    if mutation == "digest": item["sha256"] = "0" * 64
    elif mutation == "map": map_path.write_bytes(map_path.read_bytes() + b"x")
    elif mutation == "artifact": (tmp_path / "sample.txt").write_bytes(b"changed\n")
    elif mutation == "duplicate": damaged["entries"].append(dict(item))
    elif mutation == "traversal": item["path"] = "../sample-content-review.json"
    else:
        if mutation == "count": review["definitions"] = 2
        else: review["files"][0]["target"] = "../sample.txt"
        raw = json.dumps(review).encode()
        item.update(sha256=hashlib.sha256(raw).hexdigest(), raw_base64=base64.b64encode(raw).decode())
    with pytest.raises(AssertionError): validate_archive(damaged, tmp_path, tmp_path)


@pytest.mark.parametrize("kind", ["compressed", "expanded"])
def test_review_archive_keeps_original_size_caps(kind):
    raw = b"x" * 1048577 if kind == "compressed" else gzip.compress(b"x" * 2097153, mtime=0)
    with pytest.raises(AssertionError): bounded_gzip(raw)
