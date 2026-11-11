"""Compare outputs recorded at one package version with outputs written at another.

Issue 172. Many committed outputs carry ``gnd_version``, and some carry a
digest of a file that does. Each release used to re-record all of them (30
files for 0.3.0). The functions here let a test compare what the product writes
today with bytes that were recorded at an earlier version, so a version bump
moves no recorded byte.

The rule is narrow on purpose. Moving a tree from version ``old`` to ``new``
changes exactly two things:

- the value of a version field that equals ``old`` becomes ``new``;
- a 64-digit hexadecimal digest that equals the digest of a file of the same
  tree, where that file changed in the move, becomes the digest of the moved
  file. The link is checked: a digest that matches no file of the tree is left
  alone, so it still has to equal the recorded one.

Everything else is compared as before, byte for byte. When ``old == new`` the
move is the identity, so at the recorded version these tests compare exactly
what they always compared. A file that was recorded at a still older version
and is kept that way on purpose (the 0.1.0 inputs) names neither version and
is not touched.

A test states the version its fixture was recorded at as ``RECORDED_AT``. A new
fixture states the version it is recorded at; nothing here needs to change.

``structure`` is for the one case the rule above does not reach: a file in
which the version feeds digests of parts of the file itself, which only the
product can re-derive. It keeps every byte except the version values and the
digests, and it keeps which digests are equal to which. ``unordered_structure``
is its form for a document that also orders its parts by such a digest.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping

from gnd import resolve_version

#: A version field in JSON text, plain or escaped inside a JSON string.
_GND_VERSION = re.compile(rb'(\\?"gnd_version\\?"\s*:\s*\\?")([^"\\]*)')
#: The inducer block that ``gnd discover`` writes into provenance, in a JSON document, in
#: JSON text held in a string of one, or in a verbalization:
#: ``"inducer": {"name": "gnd-discover", "version": ...}``.
_INDUCER_VERSION = re.compile(
    rb'(\\*"inducer\\*"\s*:\s*\{\s*\\*"name\\*"\s*:\s*\\*"gnd-discover\\*"\s*,'
    rb'\s*\\*"version\\*"\s*:\s*\\*")([^"\\]*)')
_HEX64 = re.compile(rb"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")
_HEX16 = re.compile(rb"(?<![0-9a-f])[0-9a-f]{16}(?![0-9a-f])")


def live_version() -> str:
    """The version the product under test writes."""
    return resolve_version()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def move_version(data: bytes, old: str, new: str) -> bytes:
    """Return ``data`` with every version field that equals ``old`` set to ``new``."""
    if old == new:
        return data
    source = old.encode("utf-8")
    target = new.encode("utf-8")

    def moved(match: re.Match[bytes]) -> bytes:
        return match.group(1) + target if match.group(2) == source else match.group(0)

    return _INDUCER_VERSION.sub(moved, _GND_VERSION.sub(moved, data))


def as_recorded(data: bytes, recorded_at: str) -> bytes:
    """One fresh output, as the product would have written it at ``recorded_at``."""
    return move_version(data, live_version(), recorded_at)


def move_tree(files: Mapping[str, bytes], old: str, new: str) -> dict[str, bytes]:
    """Move a tree of files from version ``old`` to ``new``, re-deriving the digests that follow.

    A cited digest is replaced only when it equals the SHA-256 of a file of the
    tree before the move, and it is replaced by the SHA-256 of that file after it.
    """
    if old == new:
        return dict(files)
    moved = {name: move_version(data, old, new) for name, data in files.items()}
    current = dict(moved)
    for _ in range(len(files) + 2):
        mapping: dict[bytes, bytes] = {}
        for name, data in files.items():
            if current[name] != data:
                before, after = sha256_hex(data).encode("ascii"), sha256_hex(current[name]).encode("ascii")
                assert mapping.setdefault(before, after) == after, f"{name}: one digest maps to two values"
        following = {name: _cite(data, mapping) for name, data in moved.items()}
        if following == current:
            return current
        current = following
    raise AssertionError("the digests of the moved tree do not settle; the files cite each other in a cycle")


def _cite(data: bytes, mapping: Mapping[bytes, bytes]) -> bytes:
    return _HEX64.sub(lambda m: mapping.get(m.group(0), m.group(0)), data)


def tree_as_recorded(files: Mapping[str, bytes], recorded_at: str) -> dict[str, bytes]:
    """A fresh output tree, as the product would have written it at ``recorded_at``."""
    return move_tree(files, live_version(), recorded_at)


def tree_at_live_version(files: Mapping[str, bytes], recorded_at: str) -> dict[str, bytes]:
    """A recorded tree, as the product writes it today.

    For a recorded project the product is run over: it reads the version and
    the digests it wrote, so they have to be the ones it would write now.
    """
    return move_tree(files, recorded_at, live_version())


def _named_digests(data: bytes) -> bytes:
    for pattern, label in ((_HEX64, b"sha256"), (_HEX16, b"hex16")):
        names: dict[bytes, bytes] = {}

        def named(match: re.Match[bytes], names=names, label=label) -> bytes:
            return names.setdefault(match.group(0), b"<" + label + b":" + str(len(names)).encode() + b">")

        data = pattern.sub(named, data)
    return data


def _versions_masked(data: bytes) -> bytes:
    return _INDUCER_VERSION.sub(rb"\1<V>", _GND_VERSION.sub(rb"\1<V>", data))


def structure(data: bytes) -> bytes:
    """``data`` with its version values and its digests replaced by names.

    Every version field becomes ``<V>``. Each distinct run of 64 hexadecimal
    digits becomes ``<sha256:N>`` and each distinct run of 16 becomes
    ``<hex16:N>``, numbered in order of first appearance, so two places that
    held one digest still hold one name and two that differed still differ.
    """
    return _named_digests(_versions_masked(data))


def unordered_structure(data: bytes) -> bytes:
    """The structural form of a JSON document whose order follows its digests.

    Some documents list their parts in the order of a digest, so a new version
    reorders them. This form is the sorted lines of the document, printed with
    sorted keys and with each text it embeds split into that text's own lines.
    Version values are masked first; digests are then named within each line.
    It keeps every line and how often it occurs, and gives up their order.
    """
    text = json.dumps(json.loads(data), indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8")
    lines = [part for line in _versions_masked(text).split(b"\n") for part in line.split(b"\\n")]
    return b"\n".join(sorted(_named_digests(line) for line in lines)) + b"\n"
