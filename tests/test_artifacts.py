"""Adversarial contracts for shared, policy-neutral artifact primitives."""

from __future__ import annotations

import ast
import hashlib
import json
import os
import stat
from collections.abc import Callable
from pathlib import Path, PurePosixPath
from typing import Any

import pytest
from pydantic import BaseModel

import gnd.artifacts as artifact_module
from gnd.artifacts import (
    ArtifactError,
    TreeFile,
    canonical_json_bytes,
    canonical_json_text,
    inventory_tree,
    publish_directory_once,
    publish_leaf_atomic,
    read_regular_bounded,
    read_regular_file_bytes,
    sha256_hex,
    tree_sha256_from_directory,
    tree_sha256_from_inventory,
)


def test_regular_leaf_read_is_bounded_no_follow_and_identity_checked(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    leaf = root / "evidence.json"
    leaf.write_bytes(b"evidence\n")

    data, snapshot = read_regular_bounded(root, "evidence.json", max_bytes=32)

    assert data == b"evidence\n"
    assert snapshot.path == "evidence.json"
    assert snapshot.file_type == "regular"
    assert snapshot.size_bytes == len(data)

    leaf.write_bytes(b"replacement\n")
    with pytest.raises(ArtifactError, match="changed|identity|expected"):
        read_regular_bounded(root, "evidence.json", max_bytes=32, expected=snapshot)


@pytest.mark.parametrize(
    "relative",
    ["../escape", "/absolute", "nested/../../escape", "C:/drive", "nul\x00name"],
)
def test_artifact_paths_refuse_escape_absolute_drive_and_nul(
    tmp_path: Path, relative: str
) -> None:
    root = tmp_path / "root"
    root.mkdir()

    with pytest.raises(ArtifactError):
        read_regular_bounded(root, relative, max_bytes=32)
    with pytest.raises(ArtifactError):
        publish_leaf_atomic(root, relative, b"x")


def test_reads_and_inventories_refuse_symlinks_and_nonregular_files(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.write_bytes(b"outside")
    (root / "linked").symlink_to(outside)

    with pytest.raises(ArtifactError, match="symlink"):
        read_regular_bounded(root, "linked", max_bytes=32)
    with pytest.raises(ArtifactError, match="symlink"):
        inventory_tree(root)

    if hasattr(os, "mkfifo"):
        (root / "linked").unlink()
        os.mkfifo(root / "pipe")
        with pytest.raises(ArtifactError, match="regular"):
            inventory_tree(root)


def test_tree_inventory_is_sorted_stable_complete_and_digest_sensitive(tmp_path: Path) -> None:
    root = tmp_path / "tree"
    (root / "z").mkdir(parents=True)
    (root / "z" / "last.txt").write_bytes(b"last")
    (root / "a.txt").write_bytes(b"first")

    first = inventory_tree(root)
    second = inventory_tree(root)

    assert first == second
    assert [entry.path for entry in first.files] == ["a.txt", "z/last.txt"]
    assert first.file_count == 2
    assert first.total_bytes == 9

    (root / "z" / "last.txt").write_bytes(b"changed")
    changed = inventory_tree(root)
    assert changed.tree_sha256 != first.tree_sha256


def test_directory_tree_digest_uses_filesystem_bytes_for_names_and_symlink_targets(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "tree"
    root.mkdir()
    file_name = b"file-\xff"
    link_name = b"link-\xfe"
    file_bytes = b"filesystem bytes\n"
    (root / "file").write_bytes(file_bytes)
    (root / "link").symlink_to("file")
    real_fsencode = os.fsencode

    def injected_fsencode(value: str | bytes | os.PathLike[str]) -> bytes:
        if value == "file":
            return file_name
        if value == "link":
            return link_name
        return real_fsencode(value)

    monkeypatch.setattr(artifact_module.os, "fsencode", injected_fsencode)

    expected = hashlib.sha256()
    for name in sorted((file_name, link_name)):
        if name == file_name:
            expected.update(b"F\0" + file_name + b"\0" + file_bytes)
        else:
            expected.update(b"L\0" + link_name + b"\0" + file_name)

    assert tree_sha256_from_directory(
        root,
        label="filesystem-byte tree",
        max_entries=2,
        max_bytes=len(file_bytes),
    ) == expected.hexdigest()


def test_tree_inventory_enforces_per_file_total_count_and_depth_bounds(tmp_path: Path) -> None:
    root = tmp_path / "tree"
    (root / "one" / "two").mkdir(parents=True)
    (root / "a").write_bytes(b"1234")
    (root / "b").write_bytes(b"5678")
    (root / "one" / "two" / "c").write_bytes(b"9")

    with pytest.raises(ArtifactError, match="per-file"):
        inventory_tree(root, max_file_bytes=3)
    with pytest.raises(ArtifactError, match="total"):
        inventory_tree(root, max_total_bytes=8)
    with pytest.raises(ArtifactError, match="file cap|files"):
        inventory_tree(root, max_files=2)
    with pytest.raises(ArtifactError, match="depth"):
        inventory_tree(root, max_depth=1)


def test_leaf_publication_is_atomic_compare_and_swap_and_never_overwrites_collision(
    tmp_path: Path,
) -> None:
    root = tmp_path / "root"
    root.mkdir()

    first = publish_leaf_atomic(root, "best.json", b"one\n")
    with pytest.raises(ArtifactError, match="exists|collision"):
        publish_leaf_atomic(root, "best.json", b"unexpected\n")
    assert (root / "best.json").read_bytes() == b"one\n"

    second = publish_leaf_atomic(root, "best.json", b"two\n", expected=first)
    assert (root / "best.json").read_bytes() == b"two\n"
    assert second.sha256 != first.sha256

    (root / "best.json").write_bytes(b"raced\n")
    with pytest.raises(ArtifactError, match="changed|identity|expected"):
        publish_leaf_atomic(root, "best.json", b"three\n", expected=second)
    assert (root / "best.json").read_bytes() == b"raced\n"


def test_leaf_compare_and_swap_never_overwrites_a_gap_racer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    expected = publish_leaf_atomic(root, "best.json", b"expected\n")
    original_exchange = artifact_module._exchange_paths_atomic
    injected = False

    def racing_exchange(first_fd, first_name, second_fd, second_name):
        nonlocal injected
        if not injected and second_name == "best.json":
            injected = True
            os.unlink(second_name, dir_fd=second_fd)
            descriptor = os.open(
                second_name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o644,
                dir_fd=second_fd,
            )
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(b"racer\n")
        original_exchange(first_fd, first_name, second_fd, second_name)

    monkeypatch.setattr(artifact_module, "_exchange_paths_atomic", racing_exchange)
    with pytest.raises(ArtifactError, match="compare-and-swap"):
        publish_leaf_atomic(root, "best.json", b"replacement\n", expected=expected)

    assert injected is True
    assert (root / "best.json").read_bytes() == b"racer\n"
    assert not list(root.glob(".gnd-staging-*"))


def test_append_once_directory_writes_manifest_last_and_refuses_duplicates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    order: list[str] = []
    original = artifact_module._write_new_file_at

    def recording_write(root_fd, parts, data, **kwargs) -> None:
        order.append(PurePosixPath(*parts).as_posix())
        original(root_fd, parts, data, **kwargs)

    monkeypatch.setattr(artifact_module, "_write_new_file_at", recording_write)
    inventory = publish_directory_once(
        root,
        "attempts/0001",
        {
            "candidate/main.py": b"print('ok')\n",
            "attempt.json": b'{"complete":true}\n',
            "agent.stdout": b"done\n",
        },
        manifest_name="attempt.json",
    )

    assert order[-1] == "attempt.json"
    assert inventory.file_count == 3
    assert (root / "attempts" / "0001" / "attempt.json").is_file()

    with pytest.raises(ArtifactError, match="exists|collision"):
        publish_directory_once(
            root,
            "attempts/0001",
            {"attempt.json": b"replacement\n"},
            manifest_name="attempt.json",
        )
    assert (root / "attempts" / "0001" / "attempt.json").read_bytes() == (
        b'{"complete":true}\n'
    )


@pytest.mark.parametrize(
    "alias",
    ["a//b", "a/./b", "a/b/", " a/b", "a/b ", r"a\b"],
)
def test_append_once_directory_rejects_noncanonical_member_aliases(
    tmp_path: Path,
    alias: str,
) -> None:
    root = tmp_path / "root"
    root.mkdir()

    with pytest.raises(ArtifactError, match="normalized POSIX"):
        publish_directory_once(
            root,
            "bundles/one",
            {
                alias: b"first",
                "a/b": b"second",
                "manifest.json": b"{}\n",
            },
            manifest_name="manifest.json",
        )

    assert not (root / "bundles" / "one").exists()


def test_append_once_directory_rejects_noncanonical_executable_aliases(
    tmp_path: Path,
) -> None:
    root = tmp_path / "root"
    root.mkdir()

    with pytest.raises(ArtifactError, match="normalized POSIX"):
        publish_directory_once(
            root,
            "bundles/one",
            {"bin/tool": b"#!/bin/sh\n", "manifest.json": b"{}\n"},
            manifest_name="manifest.json",
            executable_paths={"bin//tool", "bin/tool"},
        )

    assert not (root / "bundles" / "one").exists()


def test_append_once_directory_never_replaces_a_publication_racer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    original_mkdir = artifact_module._mkdir_directory_once

    def racing_mkdir(parent_fd, name):
        os.mkdir(name, dir_fd=parent_fd)
        original_mkdir(parent_fd, name)

    monkeypatch.setattr(
        artifact_module,
        "_mkdir_directory_once",
        racing_mkdir,
    )
    with pytest.raises(ArtifactError, match="collision"):
        publish_directory_once(
            root,
            "attempts/0001",
            {"attempt.json": b'{"complete":true}\n'},
            manifest_name="attempt.json",
        )

    destination = root / "attempts" / "0001"
    assert destination.is_dir()
    assert not list(destination.iterdir())
    assert not list(root.rglob(".gnd-staging-*"))


def test_append_once_directory_refuses_a_swapped_bound_destination(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    original_write = artifact_module._write_new_file_at
    injected = False

    def swap_destination(root_fd, parts, data, **kwargs):
        nonlocal injected
        original_write(root_fd, parts, data, **kwargs)
        if not injected:
            injected = True
            destination = root / "attempts" / "0001"
            destination.rename(destination.with_name("0001-preserved"))
            destination.mkdir()

    monkeypatch.setattr(
        artifact_module,
        "_write_new_file_at",
        swap_destination,
    )
    with pytest.raises(ArtifactError, match="destination.*changed"):
        publish_directory_once(
            root,
            "attempts/0001",
            {
                "data.txt": b"bound bytes\n",
                "attempt.json": b'{"complete":true}\n',
            },
            manifest_name="attempt.json",
        )

    assert injected is True
    assert not (root / "attempts" / "0001" / "attempt.json").exists()
    assert not (root / "attempts" / "0001-preserved" / "attempt.json").exists()


def test_append_once_directory_verifies_every_member_after_manifest_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    original_write = artifact_module._write_new_file_at
    injected = False

    def remove_member_before_manifest(root_fd, parts, data, **kwargs):
        nonlocal injected
        if parts == ("attempt.json",) and not injected:
            injected = True
            os.unlink("data.txt", dir_fd=root_fd)
        original_write(root_fd, parts, data, **kwargs)

    monkeypatch.setattr(
        artifact_module,
        "_write_new_file_at",
        remove_member_before_manifest,
    )
    with pytest.raises(ArtifactError, match="complete tree"):
        publish_directory_once(
            root,
            "attempts/0001",
            {
                "data.txt": b"required evidence\n",
                "attempt.json": b'{"complete":true}\n',
            },
            manifest_name="attempt.json",
        )

    assert injected is True
    assert not (root / "attempts" / "0001").exists()


def test_failed_directory_publication_leaves_no_partial_destination_or_staging(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    original = artifact_module._write_new_file_at
    calls = 0

    def fail_second(root_fd, parts, data, **kwargs) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected write failure")
        original(root_fd, parts, data, **kwargs)

    monkeypatch.setattr(artifact_module, "_write_new_file_at", fail_second)
    with pytest.raises(OSError, match="injected"):
        publish_directory_once(
            root,
            "bundles/one",
            {"data.txt": b"data", "manifest.json": b"{}\n"},
            manifest_name="manifest.json",
        )

    assert not (root / "bundles" / "one").exists()
    assert not list(root.rglob(".gnd-staging-*"))


# ---------------------------------------------------------------------------
# Promoted primitives (plan 04-18 / review finding R-04).
#
# The functions below are verbatim transcriptions of the private helpers that
# `exp/session_store.py`, `evolve/service.py`, `recovery/inventory.py`, and
# `review/runner.py` each carried before the consolidation.  They are pinned
# here, not imported, precisely because the originals are being deleted: an
# equivalence assertion against a helper that no longer exists is a tautology,
# and one against the promoted function itself is worse.  These are the frozen
# pre-consolidation bodies, and they are what "no digest moved" is measured
# against.
# ---------------------------------------------------------------------------


def _legacy_digest(data: bytes) -> str:
    """artifacts.py `_digest`, session_store/evolve/recovery `_sha256`."""

    return hashlib.sha256(data).hexdigest()


def _legacy_canonical_bytes(value: object) -> bytes:
    """artifacts.py `_canonical_bytes`."""

    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _legacy_session_canonical_bytes(value: BaseModel | dict[str, Any]) -> bytes:
    """exp/session_store.py `_canonical_bytes`."""

    document = value.model_dump(mode="json") if isinstance(value, BaseModel) else value
    return (
        json.dumps(
            document,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _legacy_canonical_model(model: BaseModel) -> bytes:
    """review/runner.py `_canonical_model`."""

    return (
        json.dumps(
            model.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _legacy_canonical(value: Any) -> str:
    """evolve/service.py `_canonical` — the str-returning variant."""

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _legacy_record_bytes(value: Any) -> bytes:
    """evolve/service.py `_record_bytes`."""

    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    return (_legacy_canonical(value) + "\n").encode("utf-8")


def _legacy_canonical_fragment(value: Any) -> bytes:
    """recovery/inventory.py `_canonical_fragment` — bytes, no trailing newline."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _legacy_tree_sha256(files: Any) -> str:
    """artifacts.py `_tree_sha256` / session_store `_candidate_tree_sha256`."""

    return _legacy_digest(
        _legacy_canonical_bytes({"files": [entry.model_dump(mode="json") for entry in files]})
    )


def _legacy_regular_bytes(path: Path, *, label: str) -> bytes:
    """evolve/service.py `_regular_bytes`, with its exact refusal wording."""

    try:
        info = path.lstat()
    except OSError as error:
        raise ValueError(f"{label} could not be inspected at {path}: {error}") from error
    if stat.S_ISLNK(info.st_mode):
        raise ValueError(f"{label} at {path} is a symlink; refusing to follow it")
    if not stat.S_ISREG(info.st_mode):
        raise ValueError(f"{label} at {path} is not a regular file")
    try:
        return path.read_bytes()
    except OSError as error:
        raise ValueError(f"{label} could not be read at {path}: {error}") from error


def _legacy_directory_tree_sha256(root: Path, *, max_entries: int, max_bytes: int) -> str:
    """evolve/service.py `_tree_sha256` — the directory-walking variant."""

    digest = hashlib.sha256()
    entries = 0
    total_bytes = 0

    def visit(directory: Path) -> None:
        nonlocal entries, total_bytes
        children = sorted(os.scandir(directory), key=lambda entry: entry.name)
        for entry in children:
            entries += 1
            if entries > max_entries:
                raise ValueError("too many entries")
            path = Path(entry.path)
            relpath = path.relative_to(root).as_posix().encode("utf-8")
            info = entry.stat(follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode):
                target = os.readlink(path).encode("utf-8")
                digest.update(b"L\0" + relpath + b"\0" + target)
            elif stat.S_ISDIR(info.st_mode):
                digest.update(b"D\0" + relpath + b"\0")
                visit(path)
            elif stat.S_ISREG(info.st_mode):
                total_bytes += info.st_size
                if total_bytes > max_bytes:
                    raise ValueError("over the byte cap")
                digest.update(b"F\0" + relpath + b"\0")
                digest.update(_legacy_regular_bytes(path, label="linked project file"))
            else:
                raise ValueError("unsupported special entry")

    visit(root)
    return digest.hexdigest()


class _EquivalenceModel(BaseModel):
    """A model whose dump exercises ordering, unicode, and nesting at once."""

    zeta: str
    alpha: int
    nested: dict[str, Any]


_EQUIVALENCE_VALUES: tuple[Any, ...] = (
    {},
    {"b": 1, "a": 2},
    {"unicode": "naïve — Ω 漢字", "escape": 'quote " backslash \\ newline \n'},
    {"nested": {"z": [1, 2, {"y": None, "x": True}], "a": 3.5}},
    [1, "two", None, False],
    {"empty_list": [], "empty_object": {}, "zero": 0, "negative": -17},
)


@pytest.mark.parametrize("value", _EQUIVALENCE_VALUES)
def test_canonical_json_bytes_matches_every_private_helper_it_replaces(value: Any) -> None:
    """One canonical-JSON implementation, byte-identical to all four originals."""

    promoted = canonical_json_bytes(value)

    assert promoted == _legacy_canonical_bytes(value)
    assert promoted == _legacy_session_canonical_bytes(value)
    assert promoted == _legacy_record_bytes(value)
    assert canonical_json_text(value) == _legacy_canonical(value)
    assert canonical_json_text(value).encode("utf-8") == _legacy_canonical_fragment(value)


def test_canonical_json_bytes_matches_the_model_dumping_helpers() -> None:
    """The BaseModel front-end agrees with session_store, runner, and evolve."""

    model = _EquivalenceModel(
        zeta="ω",
        alpha=1,
        nested={"b": [1, 2], "a": None},
    )
    promoted = canonical_json_bytes(model)

    assert promoted == _legacy_session_canonical_bytes(model)
    assert promoted == _legacy_canonical_model(model)
    assert promoted == _legacy_record_bytes(model)


def test_canonical_json_pins_separators_key_order_ascii_and_trailing_newline() -> None:
    """Pinned by assertion, not inherited by inspection.

    Every stored digest in the repository is a digest of these exact bytes, so
    a one-character drift in separators, ordering, escaping, or the trailing
    newline would silently invalidate all of them at once.
    """

    value = {"b": "ü", "a": {"d": 1, "c": [2, 3]}}

    assert canonical_json_bytes(value) == b'{"a":{"c":[2,3],"d":1},"b":"\xc3\xbc"}\n'

    rendered = canonical_json_text(value)
    assert rendered == '{"a":{"c":[2,3],"d":1},"b":"ü"}'
    # separators: no space after ',' or ':'
    assert ", " not in rendered
    assert ": " not in rendered
    # key ordering: sorted, not insertion order
    assert rendered.index('"a"') < rendered.index('"b"')
    assert rendered.index('"c"') < rendered.index('"d"')
    # ascii handling: non-ASCII stays literal (ensure_ascii=False), UTF-8 encoded
    assert "\\u" not in rendered
    assert "ü" in rendered
    # trailing newline: on the bytes form only, exactly one
    assert canonical_json_bytes(value).endswith(b"}\n")
    assert not canonical_json_bytes(value).endswith(b"}\n\n")
    assert not rendered.endswith("\n")
    assert canonical_json_bytes(value) == (rendered + "\n").encode("utf-8")


def test_canonical_json_refuses_non_finite_numbers() -> None:
    """`allow_nan=False` is part of the canonical form, not an accident."""

    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ValueError):
            canonical_json_bytes({"value": bad})
        with pytest.raises(ValueError):
            canonical_json_text({"value": bad})


@pytest.mark.parametrize(
    "data",
    [b"", b"evidence\n", b"\x00\xff\xfe", "naïve — Ω".encode()],
)
def test_sha256_hex_matches_the_private_digest_helpers(data: bytes) -> None:
    """One content digest, byte-identical to all four `_sha256`/`_digest` copies."""

    assert sha256_hex(data) == _legacy_digest(data)


def test_tree_sha256_from_inventory_matches_the_legacy_inventory_digest() -> None:
    """The declared-inventory tree identity is unchanged by the promotion."""

    files = (
        TreeFile(path="a.txt", size_bytes=5, sha256="0" * 64),
        TreeFile(path="z/last.txt", size_bytes=4, sha256="1" * 64, executable=True),
    )

    assert tree_sha256_from_inventory(files) == _legacy_tree_sha256(files)
    assert tree_sha256_from_inventory(list(files)) == _legacy_tree_sha256(files)
    # It is sensitive to the inventory it is given, not merely stable.
    changed = (files[0], files[1].model_copy(update={"executable": False}))
    assert tree_sha256_from_inventory(changed) != tree_sha256_from_inventory(files)


def test_tree_sha256_from_directory_matches_the_legacy_directory_walk(tmp_path: Path) -> None:
    """The directory-walking tree identity is a different function, also unchanged."""

    root = tmp_path / "project"
    (root / "pkg" / "sub").mkdir(parents=True)
    (root / "pkg" / "sub" / "deep.py").write_bytes(b"deep\n")
    (root / "pkg" / "mod.py").write_bytes(b"mod\n")
    (root / "top.txt").write_bytes(b"top\n")
    (root / "link").symlink_to("top.txt")

    promoted = tree_sha256_from_directory(
        root,
        label="linked project",
        max_entries=1000,
        max_bytes=1_000_000,
    )

    assert promoted == _legacy_directory_tree_sha256(root, max_entries=1000, max_bytes=1_000_000)

    (root / "pkg" / "mod.py").write_bytes(b"changed\n")
    assert (
        tree_sha256_from_directory(
            root,
            label="linked project",
            max_entries=1000,
            max_bytes=1_000_000,
        )
        != promoted
    )


def test_the_two_tree_identities_are_distinct_functions_over_distinct_inputs(
    tmp_path: Path,
) -> None:
    """They share a name in the old tree and nothing else; the promotion says so."""

    root = tmp_path / "project"
    root.mkdir()
    (root / "a.txt").write_bytes(b"aaaaa")

    inventory = inventory_tree(root)

    # The inventory identity hashes a declared file list ...
    assert tree_sha256_from_inventory(inventory.files) == inventory.tree_sha256
    # ... the directory identity walks a real root, and the two never agree.
    walked = tree_sha256_from_directory(
        root, label="project", max_entries=100, max_bytes=1000
    )
    assert walked != inventory.tree_sha256

    with pytest.raises((AttributeError, TypeError)):
        tree_sha256_from_inventory(root)  # type: ignore[arg-type]


def test_tree_sha256_from_directory_enforces_its_entry_and_byte_caps(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    (root / "a.txt").write_bytes(b"aaaaa")
    (root / "b.txt").write_bytes(b"bbbbb")

    with pytest.raises(ArtifactError, match="tree entries"):
        tree_sha256_from_directory(root, label="linked project", max_entries=1, max_bytes=1000)
    with pytest.raises(ArtifactError, match="snapshot cap"):
        tree_sha256_from_directory(root, label="linked project", max_entries=100, max_bytes=6)


@pytest.mark.parametrize("mutation", ["add", "remove"])
def test_tree_sha256_refuses_root_entry_set_changes_after_enumeration(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
) -> None:
    root = tmp_path / "project"
    root.mkdir()
    existing = root / "existing.txt"
    existing.write_bytes(b"existing\n")
    root_inode = root.stat().st_ino
    real_listdir = artifact_module.os.listdir
    injected = False

    def mutate_after_listdir(directory: Any) -> list[str]:
        nonlocal injected
        names = real_listdir(directory)
        if not injected and os.fstat(directory).st_ino == root_inode:
            injected = True
            if mutation == "add":
                (root / "late.txt").write_bytes(b"late\n")
            else:
                existing.unlink()
        return names

    monkeypatch.setattr(artifact_module.os, "listdir", mutate_after_listdir)

    with pytest.raises(ArtifactError, match="changed while enumerated"):
        tree_sha256_from_directory(
            root,
            label="linked project",
            max_entries=100,
            max_bytes=10_000,
        )


def test_tree_sha256_refuses_nested_directory_mutation_after_enumeration(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "project"
    nested = root / "nested"
    nested.mkdir(parents=True)
    nested_inode = nested.stat().st_ino
    real_listdir = artifact_module.os.listdir
    injected = False

    def mutate_nested(directory: Any) -> list[str]:
        nonlocal injected
        names = real_listdir(directory)
        if not injected and os.fstat(directory).st_ino == nested_inode:
            injected = True
            (nested / "late.py").write_bytes(b"pass\n")
        return names

    monkeypatch.setattr(artifact_module.os, "listdir", mutate_nested)

    with pytest.raises(ArtifactError, match="changed while enumerated"):
        tree_sha256_from_directory(
            root,
            label="linked project",
            max_entries=100,
            max_bytes=10_000,
        )


def test_tree_sha256_rebinds_the_lexical_anchor_before_return(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "project"
    root.mkdir()
    displaced = tmp_path / "displaced-project"
    root_inode = root.stat().st_ino
    real_listdir = artifact_module.os.listdir
    injected = False

    def replace_anchor(directory: Any) -> list[str]:
        nonlocal injected
        names = real_listdir(directory)
        if not injected and os.fstat(directory).st_ino == root_inode:
            injected = True
            root.rename(displaced)
            root.mkdir()
        return names

    monkeypatch.setattr(artifact_module.os, "listdir", replace_anchor)

    with pytest.raises(ArtifactError, match="expected identity|changed before"):
        tree_sha256_from_directory(
            root,
            label="linked project",
            max_entries=100,
            max_bytes=10_000,
        )


def test_tree_sha256_rebinds_the_selected_locator_before_return(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    anchor = tmp_path / "workspace"
    selected = anchor / "project"
    selected.mkdir(parents=True)
    displaced = anchor / "displaced-project"
    selected_inode = selected.stat().st_ino
    real_listdir = artifact_module.os.listdir
    injected = False

    def replace_locator(directory: Any) -> list[str]:
        nonlocal injected
        names = real_listdir(directory)
        if not injected and os.fstat(directory).st_ino == selected_inode:
            injected = True
            selected.rename(displaced)
            selected.mkdir()
        return names

    monkeypatch.setattr(artifact_module.os, "listdir", replace_locator)

    with pytest.raises(ArtifactError, match="root changed"):
        tree_sha256_from_directory(
            anchor,
            relative="project",
            label="linked project",
            max_entries=100,
            max_bytes=10_000,
        )


def test_tree_sha256_rejects_an_invalid_locator_before_opening_the_anchor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    anchor = tmp_path / "workspace"
    anchor.mkdir()
    open_calls = 0
    real_open_root = artifact_module._open_root

    def tracked_open_root(*args: Any, **kwargs: Any) -> int:
        nonlocal open_calls
        open_calls += 1
        return real_open_root(*args, **kwargs)

    monkeypatch.setattr(artifact_module, "_open_root", tracked_open_root)

    with pytest.raises(ArtifactError, match="parent or non-normal component"):
        tree_sha256_from_directory(
            anchor,
            relative="../escape",
            label="linked project",
            max_entries=100,
            max_bytes=10_000,
        )

    assert open_calls == 0


def test_read_regular_file_bytes_matches_the_legacy_reader_and_its_refusals(
    tmp_path: Path,
) -> None:
    """Whole-file reads are rooted, no-follow, and preserve leaf bytes."""

    good = tmp_path / "model.orm.yaml"
    good.write_bytes(b"name: demo\n")
    assert read_regular_file_bytes(tmp_path, good.name, label="model") == _legacy_regular_bytes(
        good, label="model"
    )

    missing = tmp_path / "absent"
    with pytest.raises(ArtifactError) as inspected:
        read_regular_file_bytes(tmp_path, missing.name, label="model")
    assert "model could not be read safely" in str(inspected.value)

    link = tmp_path / "link"
    link.symlink_to(good)
    with pytest.raises(ArtifactError) as symlinked:
        read_regular_file_bytes(tmp_path, link.name, label="publication leaf")
    assert "publication leaf could not be read safely" in str(symlinked.value)
    assert "is a symlink" in str(symlinked.value)

    with pytest.raises(ArtifactError) as directory:
        read_regular_file_bytes(tmp_path.parent, tmp_path.name, label="model")
    assert "is not a regular file" in str(directory.value)


@pytest.mark.parametrize(
    "seam",
    ["root", "descend", "inventory", "create-parent"],
)
def test_descriptor_readers_close_new_descriptors_when_fstat_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    seam: str,
) -> None:
    root = tmp_path / "root"
    child = root / "child"
    child.mkdir(parents=True)
    root_fd = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    real_open = artifact_module.os.open
    real_fstat = artifact_module.os.fstat
    real_close = artifact_module.os.close
    target_fd = -1
    closed: list[int] = []

    def tracked_open(path: Any, flags: int, *args: Any, **kwargs: Any) -> int:
        nonlocal target_fd
        descriptor = real_open(path, flags, *args, **kwargs)
        if (seam == "root" and Path(path) == root) or (
            seam != "root" and path == "child"
        ):
            target_fd = descriptor
        return descriptor

    def failing_fstat(descriptor: int) -> os.stat_result:
        if descriptor == target_fd:
            raise OSError("injected fstat failure")
        return real_fstat(descriptor)

    def tracked_close(descriptor: int) -> None:
        closed.append(descriptor)
        real_close(descriptor)

    monkeypatch.setattr(artifact_module.os, "open", tracked_open)
    monkeypatch.setattr(artifact_module.os, "fstat", failing_fstat)
    monkeypatch.setattr(artifact_module.os, "close", tracked_close)

    try:
        with pytest.raises(ArtifactError, match="opened safely|could not be opened"):
            if seam == "root":
                artifact_module._open_root(root)
            elif seam == "descend":
                artifact_module._descend(root_fd, ("child",))
            elif seam == "inventory":
                artifact_module._inventory_tree_fd(root_fd)
            else:
                artifact_module._create_parent_at(root_fd, ("child",))
    finally:
        real_close(root_fd)

    assert target_fd >= 0
    assert closed.count(target_fd) == 1


PROMOTED_ARTIFACT_PRIMITIVES = frozenset(
    {
        "canonical_json_bytes",
        "canonical_json_text",
        "read_regular_file_bytes",
        "sha256_hex",
        "tree_sha256_from_directory",
        "tree_sha256_from_inventory",
    }
)


def _module_level_redefinitions(
    package_root: Path,
    *,
    exclude: frozenset[str] = frozenset(),
) -> list[str]:
    """Report module-level bindings of a promoted primitive name.

    Scoped by location rather than by substring: only top-level ``def`` and
    assignment nodes are considered, so an import of the promoted name, a
    nested helper, an attribute, and a differently-named lookalike are all
    outside the scan by construction.
    """

    findings: list[str] = []
    for path in sorted(package_root.rglob("*.py")):
        if path.name in exclude:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            bound: list[str] = []
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                bound = [node.name]
            elif isinstance(node, ast.Assign):
                bound = [t.id for t in node.targets if isinstance(t, ast.Name)]
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                bound = [node.target.id]
            for name in bound:
                if name in PROMOTED_ARTIFACT_PRIMITIVES:
                    findings.append(
                        f"{path.name}:{node.lineno} redefines promoted primitive {name!r}"
                    )
    return findings


def test_no_module_redefines_a_promoted_artifact_primitive() -> None:
    """A local copy of a promoted primitive cannot silently return.

    R-04 was four modules each carrying private copies of `artifacts.py`'s
    digest, canonical-JSON, read, and tree-identity logic.  This gate is what
    stops the consolidation from unwinding one helper at a time.
    """

    package_root = Path(artifact_module.__file__).parent
    findings = _module_level_redefinitions(package_root, exclude=frozenset({"artifacts.py"}))

    assert findings == [], (
        "promoted artifact primitives are redefined outside gnd/artifacts.py:\n"
        + "\n".join(findings)
        + "\nImport them from gnd.artifacts instead of reimplementing them."
    )


def test_the_duplication_gate_fires_on_a_planted_redefinition(tmp_path: Path) -> None:
    """Negative control: the gate above must be able to fail.

    Without this, a scan that silently matched nothing — a renamed primitive, a
    changed exclusion, a broken walk — would read exactly like a clean tree.
    """

    planted = tmp_path / "gnd"
    (planted / "sub").mkdir(parents=True)

    # The primitive's own home is excluded and must not be reported.
    (planted / "artifacts.py").write_text(
        "def sha256_hex(data):\n    return ''\n", encoding="utf-8"
    )
    # None of these are module-level redefinitions of a promoted name.
    (planted / "innocent.py").write_text(
        "from gnd.artifacts import canonical_json_bytes, sha256_hex\n"
        "\n"
        "def _sha256_hex_lookalike(data):\n"
        "    return sha256_hex(data)\n"
        "\n"
        "def factory():\n"
        "    def sha256_hex(data):\n"
        "        return 'nested, not module level'\n"
        "    return sha256_hex\n"
        "\n"
        "class Holder:\n"
        "    def canonical_json_bytes(self):\n"
        "        return b''\n",
        encoding="utf-8",
    )
    # This one is.
    (planted / "sub" / "offender.py").write_text(
        "import hashlib\n"
        "\n"
        "def sha256_hex(data):\n"
        "    return hashlib.sha256(data).hexdigest()\n",
        encoding="utf-8",
    )

    findings = _module_level_redefinitions(planted, exclude=frozenset({"artifacts.py"}))

    assert len(findings) == 1, findings
    assert "offender.py" in findings[0]
    assert "sha256_hex" in findings[0]
    assert "innocent.py" not in "".join(findings)
    assert "artifacts.py" not in "".join(findings)

    # A rebinding assignment is caught too, not only a `def`.
    (planted / "aliased.py").write_text(
        "import hashlib\n\ncanonical_json_text = repr\n", encoding="utf-8"
    )
    aliased = _module_level_redefinitions(planted, exclude=frozenset({"artifacts.py"}))
    assert len(aliased) == 2, aliased
    assert any("aliased.py" in finding and "canonical_json_text" in finding for finding in aliased)


# The four modules R-04 named.  The gate below is scoped to exactly these,
# because a package-wide sweep would red on twelve modules this plan does not
# touch -- that inventory is recorded in 04-18-SUMMARY.md as measured, named,
# deferred work rather than silently absorbed here.
CONSOLIDATED_MODULES = (
    "exp/session_store.py",
    "evolve/service.py",
    "recovery/inventory.py",
    "review/runner.py",
)

# A canonical-form site that is deliberately NOT routed onto the promoted
# primitive, recorded by name so the exception is reviewable rather than an
# invisible hole in the predicate.
CANONICAL_JSON_ALLOWLIST = {
    (
        "review/runner.py",
        "_build_prompt",
    ): (
        "renders the reviewer prompt schema with ensure_ascii at its default True, "
        "not the canonical False; it feeds prompt_sha256, so routing it onto "
        "canonical_json_text would change the escaping policy on recorded review "
        "evidence. Different function, not a copy."
    ),
}


CANONICAL_SEPARATOR_SPELLINGS = frozenset({'(",", ":")', "(',', ':')"})


def _reimplemented_primitive_bodies(module_path: Path, relative: str) -> list[str]:
    """Report bodies that reimplement a promoted primitive under any name.

    The name gate (`_module_level_redefinitions`) catches a copy that reuses a
    promoted name.  This catches the copy that does not -- a fresh ``_sha256``
    or a fresh canonical ``json.dumps`` -- which is the shape R-04 actually
    found four times.  Analysis is `ast.parse` over file text throughout; this
    gate never imports, `exec`s, or `compile`-and-runs the module it inspects,
    because importing a module to inspect it executes its module-level code and
    would turn a lint gate into an execution surface.

    **Recognised shapes.**  A module-level ``def``/``async def`` whose body
    (docstring excluded) is either

    1. exactly one ``return`` of ``<sha256 call>.hexdigest()``; or
    2. exactly one ``return`` of ``<sha256 call>.digest().hex()``; or
    3. exactly two statements -- an assignment of ``<sha256 call>`` to a plain
       ``Name``, then a ``return`` of that same name's ``.hexdigest()`` or
       ``.digest().hex()``

    where ``<sha256 call>`` is a call of ``hashlib.sha256`` or of any local name
    bound by ``from hashlib import sha256`` (an ``as`` alias included), resolved
    from ``ast.ImportFrom`` nodes rather than by importing anything.

    Plus, anywhere in the module, a ``json.dumps`` call with ``sort_keys=True``
    whose ``separators`` argument is the canonical two-character tuple, given
    either as an inline literal or as a module-level constant resolved through
    this module's own top-level assignments.  ``CANONICAL_JSON_ALLOWLIST``
    exempts named ``(relative, owner)`` pairs.

    **What this assertion cannot see -- it is deliberately partial and makes no
    claim to the name gate's package-wide coverage.**

    - a digest assembled across three or more statements, or inside a loop
      (`review/runner.py::_artifact_set_sha256` is exactly this, and is a
      legitimate incremental accumulator rather than a duplicate)
    - a copy that is not a module-level ``def``: a nested function, a method, a
      class body, a lambda, a comprehension
    - a canonical form built without ``json.dumps`` at all
    - a ``json.dumps`` whose ``separators`` are computed at runtime rather than
      being an inline literal or a module-level constant
    - a copy reached by ``importlib`` or ``getattr`` indirection
    - anything outside ``src/gnd``

    The region outside `CONSOLIDATED_MODULES` is not swept by the four-module
    gate; it is held as an exact recorded set by
    `KNOWN_OUT_OF_SCOPE_DUPLICATES` and reconciled both ways, so a fifth module
    reimplementing cannot pass unmentioned.
    """

    findings: list[str] = []
    tree = ast.parse(module_path.read_text(encoding="utf-8"), filename=str(module_path))

    # `from hashlib import sha256 [as alias]` -- resolved from the import nodes,
    # never by importing the module under inspection.
    digest_aliases: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "hashlib":
            for imported in node.names:
                if imported.name == "sha256":
                    digest_aliases.add(imported.asname or imported.name)

    # Module-level constants, so a `separators` argument given by name resolves.
    module_constants: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    module_constants[target.id] = ast.unparse(node.value)
        elif (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.value is not None
        ):
            module_constants[node.target.id] = ast.unparse(node.value)

    def _is_digest_construction(node: ast.expr) -> bool:
        """True for `hashlib.sha256(...)` or `<from-imported alias>(...)`."""

        if not isinstance(node, ast.Call):
            return False
        func = node.func
        if (
            isinstance(func, ast.Attribute)
            and func.attr == "sha256"
            and isinstance(func.value, ast.Name)
            and func.value.id == "hashlib"
        ):
            return True
        return isinstance(func, ast.Name) and func.id in digest_aliases

    def _is_hex_readout(node: ast.expr, base: Callable[[ast.expr], bool]) -> bool:
        """True for `<base>.hexdigest()` and for `<base>.digest().hex()`."""

        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            return False
        attribute = node.func
        if attribute.attr == "hexdigest":
            return base(attribute.value)
        if attribute.attr == "hex":
            inner = attribute.value
            return (
                isinstance(inner, ast.Call)
                and isinstance(inner.func, ast.Attribute)
                and inner.func.attr == "digest"
                and base(inner.func.value)
            )
        return False

    def _is_local(local: str) -> Callable[[ast.expr], bool]:
        """Predicate for `<local>` -- a factory, so no loop variable is captured."""

        def bound(candidate: ast.expr) -> bool:
            return isinstance(candidate, ast.Name) and candidate.id == local

        return bound

    for node in tree.body:
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        body = [
            item
            for item in node.body
            if not (isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant))
        ]
        reimplements = False
        if len(body) == 1 and isinstance(body[0], ast.Return) and body[0].value is not None:
            reimplements = _is_hex_readout(body[0].value, _is_digest_construction)
        elif (
            len(body) == 2
            and isinstance(body[0], ast.Assign)
            and len(body[0].targets) == 1
            and isinstance(body[0].targets[0], ast.Name)
            and _is_digest_construction(body[0].value)
            and isinstance(body[1], ast.Return)
            and body[1].value is not None
        ):
            reimplements = _is_hex_readout(body[1].value, _is_local(body[0].targets[0].id))
        if reimplements:
            findings.append(f"{relative}:{node.lineno} {node.name}() reimplements sha256_hex")

    enclosing: dict[int, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            for child in ast.walk(node):
                enclosing.setdefault(id(child), node.name)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not ast.unparse(node.func).endswith("json.dumps"):
            continue
        keywords = {kw.arg: ast.unparse(kw.value) for kw in node.keywords}
        if keywords.get("sort_keys") != "True":
            continue
        separators = keywords.get("separators")
        if separators is None:
            continue
        separators = module_constants.get(separators, separators)
        if separators not in CANONICAL_SEPARATOR_SPELLINGS:
            continue
        owner = enclosing.get(id(node), "<module>")
        if (relative, owner) in CANONICAL_JSON_ALLOWLIST:
            continue
        findings.append(
            f"{relative}:{node.lineno} {owner}() reimplements the canonical JSON form"
        )
    return findings


def test_consolidated_modules_do_not_reimplement_a_promoted_primitive_body() -> None:
    """The consolidation cannot unwind under a fresh private name.

    R-04's four duplicate implementations were never named `sha256_hex` or
    `canonical_json_bytes` -- they were `_sha256`, `_canonical_bytes`,
    `_canonical`, `_canonical_fragment`, and `_canonical_model`.  A gate keyed
    only on the promoted names would have stayed green through every one of
    them, which is this project's recurring defect class.
    """

    package_root = Path(artifact_module.__file__).parent
    findings: list[str] = []
    for relative in CONSOLIDATED_MODULES:
        findings.extend(_reimplemented_primitive_bodies(package_root / relative, relative))

    assert findings == [], (
        "consolidated modules reimplement a promoted artifact primitive:\n"
        + "\n".join(findings)
        + "\nImport sha256_hex / canonical_json_bytes / canonical_json_text "
        "from gnd.artifacts instead."
    )


def test_the_body_gate_fires_on_a_planted_reimplementation(tmp_path: Path) -> None:
    """Negative control for the body gate, over every shape it claims to see.

    Widened by 04-22.  Verification planted two unrouted copies of `sha256_hex`
    -- one of them in the two-statement spelling, inside the gate's own declared
    scope -- and both shipped green through this file.  Every shape below is
    asserted *by symbol name*, not only by count: a count alone passes when one
    planted shape stops being detected and another is double-counted, which is
    the failure mode 04-12 M2 and 04-13 M2 both recorded.
    """

    offender = tmp_path / "offender.py"
    offender.write_text(
        "import hashlib\n"
        "import json\n"
        "from hashlib import sha256\n"
        "from hashlib import sha256 as _sha\n"
        "\n"
        "_SEPARATORS = (',', ':')\n"
        "\n"
        "def _sha256(data):\n"
        "    return hashlib.sha256(data).hexdigest()\n"
        "\n"
        "def _sha256_digest_hex(data):\n"
        "    return hashlib.sha256(data).digest().hex()\n"
        "\n"
        "def _sha256_two_statement(data):\n"
        "    '''Assign then return -- exactly two statements.'''\n"
        "    digest = hashlib.sha256(data)\n"
        "    return digest.hexdigest()\n"
        "\n"
        "def _sha256_imported(data):\n"
        "    return sha256(data).hexdigest()\n"
        "\n"
        "def _sha256_aliased(data):\n"
        "    return _sha(data).digest().hex()\n"
        "\n"
        "def _canonical(value):\n"
        "    return json.dumps(value, sort_keys=True, separators=(',', ':'))\n"
        "\n"
        "def _canonical_via_constant(value):\n"
        "    return json.dumps(value, sort_keys=True, separators=_SEPARATORS)\n",
        encoding="utf-8",
    )
    findings = _reimplemented_primitive_bodies(offender, "offender.py")

    digest_offenders = (
        "_sha256",
        "_sha256_digest_hex",
        "_sha256_two_statement",
        "_sha256_imported",
        "_sha256_aliased",
    )
    for symbol in digest_offenders:
        assert any(f"{symbol}() reimplements sha256_hex" in finding for finding in findings), (
            f"{symbol} went undetected: {findings}"
        )
    json_offenders = ("_canonical", "_canonical_via_constant")
    for symbol in json_offenders:
        assert any(
            f"{symbol}() reimplements the canonical JSON form" in finding for finding in findings
        ), f"{symbol} went undetected: {findings}"
    assert len(findings) == len(digest_offenders) + len(json_offenders), findings

    innocent = tmp_path / "innocent.py"
    innocent.write_text(
        "import hashlib\n"
        "import json\n"
        "from gnd.artifacts import canonical_json_bytes, sha256_hex\n"
        "\n"
        "_WIDE_SEPARATORS = (', ', ': ')\n"
        "\n"
        "def rolling_digest(items):\n"
        "    digest = hashlib.sha256()\n"
        "    for item in items:\n"
        "        digest.update(item)\n"
        "    return digest.hexdigest()\n"
        "\n"
        "def pretty(value):\n"
        "    return json.dumps(value, indent=2)\n"
        "\n"
        "def unsorted(value):\n"
        "    return json.dumps(value, separators=(',', ':'))\n"
        "\n"
        "def spaced(value):\n"
        "    return json.dumps(value, sort_keys=True, separators=_WIDE_SEPARATORS)\n"
        "\n"
        "def routed(value):\n"
        "    return sha256_hex(canonical_json_bytes(value))\n"
        "\n"
        "def factory():\n"
        "    def _nested(data):\n"
        "        return hashlib.sha256(data).hexdigest()\n"
        "    return _nested\n"
        "\n"
        "class Holder:\n"
        "    def _method(self, data):\n"
        "        return hashlib.sha256(data).hexdigest()\n",
        encoding="utf-8",
    )
    assert _reimplemented_primitive_bodies(innocent, "innocent.py") == []


def test_the_body_gate_does_not_report_the_live_incremental_accumulator() -> None:
    """`review/runner.py::_artifact_set_sha256` is an accumulator, not a copy.

    It is a module-level `def` that assigns `hashlib.sha256()` to a plain name
    and returns that same name's `hexdigest()`, so it satisfies the widened
    two-statement shape's target and return conditions *verbatim*; only the
    exactly-two-statement requirement excludes it.  It lives inside
    `CONSOLIDATED_MODULES`, so a widening that reports it would red the
    four-module gate on an innocent function.  Asserted here over the real
    module path, by symbol name, so a future widening cannot re-break it in
    silence.
    """

    package_root = Path(artifact_module.__file__).parent
    relative = "review/runner.py"
    findings = _reimplemented_primitive_bodies(package_root / relative, relative)

    assert not any("_artifact_set_sha256" in finding for finding in findings), findings
    assert findings == [], findings


def test_the_canonical_json_allowlist_names_only_live_sites() -> None:
    """An allowlist entry that no longer matches anything is a stale exemption."""

    package_root = Path(artifact_module.__file__).parent
    for (relative, owner), rationale in CANONICAL_JSON_ALLOWLIST.items():
        assert rationale.strip(), f"{relative}:{owner} is exempted without a reason"
        source = (package_root / relative).read_text(encoding="utf-8")
        tree = ast.parse(source)
        owners = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        }
        assert owner in owners, f"allowlisted {owner}() no longer exists in {relative}"


