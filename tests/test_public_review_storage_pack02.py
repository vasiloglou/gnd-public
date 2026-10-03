import base64
import gzip
import hashlib
import json
import os

import pytest
from support.public_review_storage import migration_view

# Historical migration accounting/storage; current product assertions remain in default tests.
pytestmark = pytest.mark.evidence


def _entry(name, text):
    raw = gzip.compress(text.encode(), compresslevel=9, mtime=0)
    return {"path": name, "sha256": hashlib.sha256(raw).hexdigest(), "gzip_utf8": text,
            "header_base64": base64.b64encode(raw[:10]).decode(),
            "trailer_base64": base64.b64encode(raw[-8:]).decode()}, raw


def _pack(entries):
    return gzip.compress(json.dumps({"format": "lossless-reviewed-gzip-leaves-v1", "entries": entries}).encode(), mtime=0)


def test_two_closed_pack_formats_preserve_raw_gzip_bytes_and_modes(tmp_path):
    root = tmp_path.resolve()
    item, raw = _entry("second-case-map.jsonl.gz", '{"source_node":"source-case-00001"}\n')
    first = gzip.compress(json.dumps({"format": "lossless-reviewed-leaves-v1", "entries": [
        {"path": "first-originals.json", "sha256": hashlib.sha256(b"original").hexdigest(), "raw_base64": base64.b64encode(b"original").decode()}]}).encode(), mtime=0)
    second = _pack([item])
    pins = {}
    for name, value in [("reviewed-leaves-01.json.gz", first), ("reviewed-leaves-02.json.gz", second)]:
        (root / name).write_bytes(value)
        pins[name] = (hashlib.sha256(value).hexdigest(), 1)
    previous = os.umask(0o077)
    try:
        with migration_view(root, expected_packs=pins) as logical:
            assert (logical / "first-originals.json").read_bytes() == b"original"
            assert (logical / "second-case-map.jsonl.gz").read_bytes() == raw
            assert {path.stat().st_mode & 0o777 for path in logical.iterdir()} == {0o644}
    finally:
        os.umask(previous)


@pytest.mark.parametrize("mutation", ["header", "flags", "trailer", "text", "digest", "member_cap", "duplicate", "entry_shape", "old_format_shape", "cross_pack_collision"])
def test_second_format_refuses_changed_gzip_members(mutation, tmp_path):
    root = tmp_path.resolve()
    item, _ = _entry("second-case-map.jsonl.gz", "original\n")
    entries = [item]
    if mutation == "header": item["header_base64"] = base64.b64encode(b"short").decode()
    elif mutation == "flags": item["header_base64"] = base64.b64encode(b"\x1f\x8b\x08\x08" + b"x" * 6).decode()
    elif mutation == "trailer": item["trailer_base64"] = base64.b64encode(b"x" * 8).decode()
    elif mutation == "text": item["gzip_utf8"] = 1
    elif mutation == "digest": item["sha256"] = "0" * 64
    elif mutation == "member_cap": item["gzip_utf8"] = "x" * 1048577
    elif mutation == "duplicate": entries.append(dict(item))
    elif mutation == "entry_shape": item["extra"] = True
    raw = _pack(entries)
    if mutation == "old_format_shape":
        raw = gzip.compress(json.dumps({"format": "lossless-reviewed-leaves-v1", "entries": entries}).encode(), mtime=0)
    (root / "reviewed-leaves-02.json.gz").write_bytes(raw)
    pins = {"reviewed-leaves-02.json.gz": (hashlib.sha256(raw).hexdigest(), len(entries))}
    if mutation == "cross_pack_collision":
        first = _pack([dict(item)])
        (root / "reviewed-leaves-01.json.gz").write_bytes(first)
        pins["reviewed-leaves-01.json.gz"] = (hashlib.sha256(first).hexdigest(), 1)
    with pytest.raises((ValueError, OSError)), migration_view(root, expected_packs=pins):
        pass


@pytest.mark.parametrize("mutation", ["none", "swap_members", "missing_pack", "pin"])
def test_default_two_pack_membership_is_closed(monkeypatch, mutation, tmp_path):
    from support import public_review_storage as storage

    root = tmp_path.resolve()
    a, a_raw = _entry("first-case-map.jsonl.gz", "first\n")
    b, b_raw = _entry("second-case-map.jsonl.gz", "second\n")
    names = ("reviewed-leaves-01.json.gz", "reviewed-leaves-02.json.gz")
    documents = [_pack([a]), _pack([b])]
    if mutation == "swap_members": documents.reverse()
    pins = {name: (hashlib.sha256(raw).hexdigest(), 1) for name, raw in zip(names, documents, strict=True)}
    for name, raw in zip(names, documents, strict=True): (root / name).write_bytes(raw)
    monkeypatch.setattr(storage, "PACK_PINS", pins)
    monkeypatch.setattr(storage, "LEAF_PINS", {a["path"]: a["sha256"], b["path"]: b["sha256"]})
    monkeypatch.setattr(storage, "PACK_LEAVES", {names[0]: (a["path"],), names[1]: (b["path"],)})
    if mutation == "missing_pack": (root / names[1]).unlink()
    elif mutation == "pin": pins[names[1]] = ("0" * 64, 1)
    if mutation == "none":
        with migration_view(root) as logical:
            assert (logical / a["path"]).read_bytes() == a_raw
            assert (logical / b["path"]).read_bytes() == b_raw
    else:
        with pytest.raises(ValueError), migration_view(root):
            pass
