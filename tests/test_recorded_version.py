"""Issue 172: the rule that lets a recorded output outlive a version bump, held to its limits.

``tests/support/recorded_version.py`` moves a tree of outputs from one package
version to another. These tests show what the move changes, and that it
changes nothing else: a difference in any other byte, or a digest that cites
nothing in the tree, still reaches the comparison a test makes.
"""
from __future__ import annotations

import json

import pytest
from support import recorded_version
from support.recorded_version import move_tree, move_version, sha256_hex


def _artifacts(version: str, extra: str = "") -> bytes:
    return json.dumps({"gnd_version": version, "model": "m" + extra}, indent=2).encode()


def _tree(version: str, extra: str = "") -> dict[str, bytes]:
    """A project as the product writes it: a file with the version, a manifest that cites
    it and carries the version too, a payload that cites both, and a page that cites the payload."""
    artifacts = _artifacts(version, extra)
    manifest = json.dumps({"gnd_version": version, "files": [{"path": "a.json", "sha256": sha256_hex(artifacts)}]}).encode()
    payload = json.dumps({"gnd_version": version, "examined": [sha256_hex(artifacts), sha256_hex(manifest)],
                          "input_sha256": "f" * 64}).encode()
    page = f"[payload](sha256:{sha256_hex(payload)}) and [frozen](sha256:{'e' * 64})".encode()
    frozen = json.dumps({"gnd_version": "0.1.0"}).encode()
    return {"a.json": artifacts, "manifest.json": manifest, "payload.json": payload, "PAGE.md": page, "old.json": frozen}


@pytest.mark.parametrize(("old", "new"), [("0.3.0", "0.3.1"), ("0.3.0", "0.10.0"), ("1.0.0rc1", "0.3.0")])
def test_a_moved_tree_is_the_tree_the_product_writes_at_the_other_version(old, new):
    assert move_tree(_tree(old), old, new) == _tree(new)
    assert move_tree(_tree(new), new, old) == _tree(old)


def test_the_move_is_the_identity_at_the_recorded_version():
    tree = _tree("0.3.0")
    assert move_tree(tree, "0.3.0", "0.3.0") == tree
    assert move_version(tree["a.json"], "0.3.0", "0.3.0") is tree["a.json"]


def test_a_file_kept_at_an_older_version_and_a_digest_of_nothing_in_the_tree_do_not_move():
    moved = move_tree(_tree("0.3.0"), "0.3.0", "0.3.1")
    assert json.loads(moved["old.json"]) == {"gnd_version": "0.1.0"}
    assert b"f" * 64 in moved["payload.json"] and b"e" * 64 in moved["PAGE.md"]


def test_any_other_difference_still_shows_after_the_move():
    recorded = _tree("0.3.0")
    fresh = _tree("0.3.1", extra="-changed")          # the product now writes another model name
    moved = move_tree(fresh, "0.3.1", "0.3.0")
    # The changed file differs, and so does every file that cites it, down the chain.
    assert {name for name in recorded if moved[name] != recorded[name]} == {
        "a.json", "manifest.json", "payload.json", "PAGE.md"}


def test_a_product_that_writes_the_wrong_version_is_not_moved_into_agreement():
    recorded = _tree("0.3.0")
    wrong = _tree("9.9.9")                             # neither the live version nor the recorded one
    assert move_tree(wrong, "0.3.1", "0.3.0") == wrong != recorded


def test_a_broken_citation_is_not_repaired():
    fresh = _tree("0.3.1")
    manifest = json.loads(fresh["manifest.json"])
    manifest["files"][0]["sha256"] = "0" * 64        # the manifest no longer cites the real file
    fresh["manifest.json"] = json.dumps(manifest).encode()
    moved = move_tree(fresh, "0.3.1", "0.3.0")
    assert b"0" * 64 in moved["manifest.json"]
    assert moved["manifest.json"] != _tree("0.3.0")["manifest.json"]


def test_the_version_field_forms_that_move():
    assert move_version(b'{"gnd_version": "0.3.1"}', "0.3.1", "0.3.0") == b'{"gnd_version": "0.3.0"}'
    escaped = rb'{"text": "{\"gnd_version\":\"0.3.1\"}"}'
    assert move_version(escaped, "0.3.1", "0.3.0") == rb'{"text": "{\"gnd_version\":\"0.3.0\"}"}'
    inducer = b'"inducer": {\n  "name": "gnd-discover",\n  "version": "0.3.1"\n}'
    assert move_version(inducer, "0.3.1", "0.3.0") == inducer.replace(b"0.3.1", b"0.3.0")
    nested = rb'\"inducer\":{\"name\":\"gnd-discover\",\"version\":\"0.3.1\"}'
    assert move_version(nested, "0.3.1", "0.3.0") == nested.replace(b"0.3.1", b"0.3.0")
    # Not a version field of the product: another key, another inducer, a bare mention.
    for other in (b'{"prior_gnd_version": "0.3.1"}', b'{"version": "0.3.1"}',
                  b'"inducer": {"name": "popper", "version": "0.3.1"}', b"gnd 0.3.1 was installed"):
        assert move_version(other, "0.3.1", "0.3.0") == other


def test_fresh_output_is_taken_from_the_live_version(monkeypatch):
    monkeypatch.setattr(recorded_version, "resolve_version", lambda: "0.4.0")
    assert recorded_version.as_recorded(_artifacts("0.4.0"), "0.3.0") == _artifacts("0.3.0")
    assert recorded_version.tree_as_recorded(_tree("0.4.0"), "0.3.0") == _tree("0.3.0")
    assert recorded_version.tree_at_live_version(_tree("0.3.0"), "0.3.0") == _tree("0.4.0")
    monkeypatch.setattr(recorded_version, "resolve_version", lambda: "0.3.0")
    assert recorded_version.as_recorded(_artifacts("0.3.0"), "0.3.0") == _artifacts("0.3.0")
