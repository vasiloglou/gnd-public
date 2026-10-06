"""Executable cache and roster-order cases from the v6.3 Phase 2 corpus."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import FrozenInstanceError, replace
from functools import partial
from pathlib import Path
from typing import Any

import pytest
from support.public_release_fixture import publish
from support.public_release_fixture import synthetic_release as _fixture_release

from gnd import checking_service

synthetic_release = partial(_fixture_release, source=Path(__file__).resolve().parents[1] / "src/gnd")

from gnd.assurance import _wire as wire_reader
from gnd.assurance import evidence as reader

CORPUS = Path(__file__).parent / "fixtures/v63-phase2"
ANSWERS = json.loads((CORPUS / "answers.json").read_text())
CASES = {row["case_id"]: row for row in ANSWERS["cases"]}


def _prime(package: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[dict[str, int], Any]:
    """Prove a real accepted hit before each dirty second-call mutation."""
    calls = {"full": 0}
    real = reader._load

    def counted(root: Any) -> Any:
        calls["full"] += 1
        return real(root)

    monkeypatch.setattr(reader, "_load", counted)
    monkeypatch.setattr(reader.resources, "files", lambda _name: package)
    first = reader.load_assurance_evidence()
    second = reader.load_assurance_evidence()
    assert first.available and second.available
    assert first is second
    assert calls["full"] == 1, "the accepting control must prove a cache hit"
    return calls, second


def _bundle(package: Path) -> Path:
    return package / "_assurance_evidence"


def _address_target(package: Path, address: str) -> Path:
    parts = Path(address).parts
    return package.joinpath(*parts[2:]) if parts[:2] == ("src", "gnd") else _bundle(package) / address


def _flip_first(path: Path) -> None:
    raw = path.read_bytes()
    assert raw and raw[:1] != b"["
    path.write_bytes(b"[" + raw[1:])


def _expect(case_id: str, value: Any, calls: dict[str, int]) -> None:
    answer = CASES[case_id]
    assert value.available is answer["available_after"]
    assert calls["full"] == answer["full_loads"]


class _WrappedPackage:
    """A Traversable-like tree whose descendants also are not pathlib Paths."""

    def __init__(self, root: Path) -> None:
        self.root = root

    @property
    def name(self) -> str:
        return self.root.name

    def joinpath(self, *parts: str) -> _WrappedPackage:
        return _WrappedPackage(self.root.joinpath(*parts))

    def iterdir(self):
        return (_WrappedPackage(path) for path in self.root.iterdir())

    def open(self, *args: Any, **kwargs: Any):
        return self.root.open(*args, **kwargs)

    def is_dir(self) -> bool:
        return self.root.is_dir()

    def is_file(self) -> bool:
        return self.root.is_file()


@pytest.mark.parametrize("case_id", sorted(CASES))
def test_phase2_branch(case_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # The corpus is committed red before the lane exists. Once the cache lands,
    # every branch below still has an outcome assertion independent of this guard.
    if case_id not in {"C18", "C19", "C20"}:
        assert hasattr(reader, "_assurance_cache"), "Phase 2 cache lane is not implemented"
        reader._assurance_cache.clear()
    package, manifest = synthetic_release(tmp_path)
    bundle = _bundle(package)

    if case_id == "C01":
        calls = {"full": 0}
        real = reader._load

        def counted(root: Any) -> Any:
            calls["full"] += 1
            return real(root)

        monkeypatch.setattr(reader, "_load", counted)
        monkeypatch.setattr(reader.resources, "files", lambda _name: package)
        _expect(case_id, reader.load_assurance_evidence(), calls)
        return

    if case_id == "C03":
        second_package, _ = synthetic_release(tmp_path / "second")
        current = [package]
        calls = {"full": 0}
        real = reader._load

        def counted(root: Any) -> Any:
            calls["full"] += 1
            return real(root)

        monkeypatch.setattr(reader, "_load", counted)
        monkeypatch.setattr(reader.resources, "files", lambda _name: current[0])
        first = reader.load_assurance_evidence()
        current[0] = second_package
        second = reader.load_assurance_evidence()
        assert first.available and first is not second
        _expect(case_id, second, calls)
        return

    if case_id == "C15":
        (bundle / "anchor.json").write_text('{"schema_version":1}')
        calls = {"full": 0}
        real = reader._load

        def counted(root: Any) -> Any:
            calls["full"] += 1
            return real(root)

        monkeypatch.setattr(reader, "_load", counted)
        monkeypatch.setattr(reader.resources, "files", lambda _name: package)
        assert not reader.load_assurance_evidence().available
        publish(package, manifest)
        _expect(case_id, reader.load_assurance_evidence(), calls)
        return

    if case_id == "C16":
        wrapped = _WrappedPackage(package)
        calls = {"full": 0}
        real = reader._load

        def counted(root: Any) -> Any:
            calls["full"] += 1
            return real(root)

        monkeypatch.setattr(reader, "_load", counted)
        monkeypatch.setattr(reader.resources, "files", lambda _name: wrapped)
        assert reader.load_assurance_evidence().available
        _expect(case_id, reader.load_assurance_evidence(), calls)
        return

    if case_id == "C17":
        calls = {"full": 0}
        real = reader._load

        def mutate_after_authentication(root: Any) -> Any:
            calls["full"] += 1
            value = real(root)
            if calls["full"] == 1:
                _flip_first(bundle / "result.json")
            return value

        monkeypatch.setattr(reader, "_load", mutate_after_authentication)
        monkeypatch.setattr(reader.resources, "files", lambda _name: package)
        _expect(case_id, reader.load_assurance_evidence(), calls)
        return

    if case_id in {"C18", "C19", "C20"}:
        if case_id != "C19":
            with (package / "assurance/core.py").open("ab") as stream:
                stream.write(b"\n# phase 2 roster change\n")
        if case_id == "C20":
            _flip_first(bundle / "result.json")
        calls = {"full": 0}
        proof_reads = {"count": 0}
        real_load, real_read = reader._load, reader._read

        def counted(root: Any) -> Any:
            calls["full"] += 1
            return real_load(root)

        def read_counted(path: Any, limit: int = reader.MAX_DOCUMENT_BYTES) -> bytes:
            if Path(str(path)).name == "result.json":
                proof_reads["count"] += 1
            return real_read(path, limit)

        monkeypatch.setattr(reader, "_load", counted)
        monkeypatch.setattr(reader, "_read", read_counted)
        if case_id == "C19":
            _expect(case_id, reader._load(package), calls)
        else:
            with pytest.raises(ValueError, match="stale or incomplete production roster"):
                reader._load(package)
            assert proof_reads["count"] == 0
            assert calls["full"] == CASES[case_id]["full_loads"]
        return

    if case_id == "C22":
        calls, _ = _prime(package, monkeypatch)
        real_identity = reader.runtime_identity

        def changed_identity(names: list[str]) -> dict[str, Any]:
            value = real_identity(names)
            value["interpreter_sha256"] = "0" * 64
            return value

        monkeypatch.setattr(reader, "runtime_identity", changed_identity)
        _expect(case_id, reader.load_assurance_evidence(), calls)
        return

    if case_id == "C23":
        roles = ("source", "schema", "proof-result", "scope", "semantics", "toolchain")
        original_load = reader._load
        for index, role in enumerate(roles):
            if index:
                reader._assurance_cache.clear()
                package, manifest = synthetic_release(tmp_path / role)
                monkeypatch.setattr(reader.resources, "files", lambda _name, root=package: root)
            monkeypatch.setattr(reader, "_load", original_load)
            calls, _ = _prime(package, monkeypatch)
            address = next(row["address"]["path"] for row in manifest["files"] if row["role"] == role)
            target = _address_target(package, address)
            with target.open("ab") as stream:
                stream.write(b"x")
            _expect(case_id, reader.load_assurance_evidence(), calls)
        return

    if case_id in {"C24", "C25", "C26", "C27"}:
        calls, first = _prime(package, monkeypatch)
        real_stat = reader._stat_identity
        field = {"C24": 0, "C25": 1, "C26": 2, "C27": 3}[case_id]

        def one_field_changed(path: Path) -> tuple[int, int, int, int]:
            values = list(real_stat(path))
            if path.name == "result.json":
                values[field] += 1
            return tuple(values)

        monkeypatch.setattr(reader, "_stat_identity", one_field_changed)
        second = reader.load_assurance_evidence()
        assert second is not first
        _expect(case_id, second, calls)
        assert reader.load_assurance_evidence() is second
        assert calls["full"] == 2
        return

    if case_id == "C28":
        calls, _ = _prime(package, monkeypatch)
        original_roster = reader.production_roster(package)
        addressed = package / "exp/session_eval.py"
        before = addressed.lstat()
        moved = tmp_path / "relocated-exp"
        (package / "exp").rename(moved)
        (package / "exp").symlink_to(moved, target_is_directory=True)
        assert addressed.lstat().st_ino == before.st_ino
        monkeypatch.setattr(reader, "production_roster", lambda _root: original_roster)
        _expect(case_id, reader.load_assurance_evidence(), calls)
        return

    if case_id == "C29":
        calls = {"full": 0}
        real_load, real_fingerprint = reader._load, reader._fingerprint
        first = {"pending": True}

        def counted(root: Any) -> Any:
            calls["full"] += 1
            return real_load(root)

        def fail_pre_once(root: Path) -> Any:
            if first["pending"]:
                first["pending"] = False
                raise OSError("injected pre-fingerprint failure")
            return real_fingerprint(root)

        monkeypatch.setattr(reader, "_load", counted)
        monkeypatch.setattr(reader, "_fingerprint", fail_pre_once)
        monkeypatch.setattr(reader.resources, "files", lambda _name: package)
        assert reader.load_assurance_evidence().available
        _expect(case_id, reader.load_assurance_evidence(), calls)
        return

    if case_id in {"C30", "C31"}:
        calls = {"full": 0}
        real_load = reader._load

        def republish_after_auth(root: Any) -> Any:
            calls["full"] += 1
            value = real_load(root)
            if calls["full"] == 1 or case_id == "C31":
                manifest["assumptions"].append(f"valid-refresh-{calls['full']}")
                publish(package, manifest)
            return value

        monkeypatch.setattr(reader, "_load", republish_after_auth)
        monkeypatch.setattr(reader.resources, "files", lambda _name: package)
        value = reader.load_assurance_evidence()
        _expect(case_id, value, calls)
        if case_id == "C30":
            assert value.assumptions == ("synthetic-release-test", "valid-refresh-1")
            assert reader.load_assurance_evidence() is value
            assert calls["full"] == 2
        else:
            assert not reader._assurance_cache
        return

    if case_id == "C32":
        calls = {"full": 0}
        real = reader._load

        def counted(root: Any) -> Any:
            calls["full"] += 1
            return real(root)

        monkeypatch.setattr(reader, "_load", counted)
        monkeypatch.setattr(reader.resources, "files", lambda _name: package)
        existing_dirs = sum(
            1
            for path in package.rglob("*")
            if path.is_dir() and "_assurance_evidence" not in path.parts
        )
        monkeypatch.setattr(wire_reader, "MAX_ROSTER_DIRECTORIES", existing_dirs + 2)
        assert reader.production_roster(package)
        for number in range(3):
            (package / f"empty-{number}").mkdir()
        started = time.perf_counter()
        value = reader.load_assurance_evidence()
        assert time.perf_counter() - started < 5.0
        _expect(case_id, value, calls)
        return

    if case_id == "C33":
        calls, value = _prime(package, monkeypatch)
        with pytest.raises(FrozenInstanceError):
            value.available = False
        with pytest.raises(FrozenInstanceError):
            value.digests.scope_digest = "0" * 64
        _expect(case_id, reader.load_assurance_evidence(), calls)
        return

    if case_id == "C34":
        calls, _ = _prime(package, monkeypatch)
        path = bundle / "result.json"
        path.unlink()
        os.mkfifo(path)
        _expect(case_id, reader.load_assurance_evidence(), calls)
        return

    if case_id == "C35":
        calls, first = _prime(package, monkeypatch)
        manifest["assumptions"].append("valid-refresh")
        publish(package, manifest)
        second = reader.load_assurance_evidence()
        assert second is not first
        assert second.assumptions == ("synthetic-release-test", "valid-refresh")
        _expect(case_id, second, calls)
        assert reader.load_assurance_evidence() is second
        assert calls["full"] == 2
        return

    if case_id == "C36":
        calls, first = _prime(package, monkeypatch)
        path = bundle / "result.json"
        before = path.stat()
        raw = path.read_bytes()
        os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns + 1_000_000_000))
        assert path.read_bytes() == raw
        second = reader.load_assurance_evidence()
        assert second is not first
        _expect(case_id, second, calls)
        assert reader.load_assurance_evidence() is second
        assert calls["full"] == 2
        return

    if case_id == "C37":
        calls, first = _prime(package, monkeypatch)
        real_census = reader._bundle_census

        def changed_census(root: Path) -> tuple[tuple[str, str], ...]:
            return (*real_census(root), ("injected-phantom", "file"))

        monkeypatch.setattr(reader, "_bundle_census", changed_census)
        second = reader.load_assurance_evidence()
        assert second is not first
        _expect(case_id, second, calls)
        assert reader.load_assurance_evidence() is second
        assert calls["full"] == 2
        return

    calls, first = _prime(package, monkeypatch)
    if case_id == "C02":
        _expect(case_id, first, calls)
        return
    if case_id == "C04":
        anchor = json.loads((bundle / "anchor.json").read_text())
        digest = anchor["manifest_sha256"]
        anchor["manifest_sha256"] = ("0" if digest[0] != "0" else "1") + digest[1:]
        (bundle / "anchor.json").write_text(json.dumps(anchor))
    elif case_id == "C05":
        with (bundle / "manifest.json").open("ab") as stream:
            stream.write(b" ")
    elif case_id == "C06":
        (package / "new_module.py").write_bytes(b"phase_2_added = True\n")
    elif case_id == "C07":
        (bundle / "extra.bin").write_bytes(b"x")
    elif case_id == "C08":
        (bundle / "extra").mkdir()
    elif case_id == "C09":
        (bundle / "result.json").unlink()
    elif case_id == "C10":
        (bundle / "result.json").unlink()
        (bundle / "result.json").symlink_to("scope.json")
    elif case_id == "C11":
        with (bundle / "result.json").open("ab") as stream:
            stream.write(b"\n")
    elif case_id in {"C12", "C13", "C14"}:
        path = bundle / "result.json"
        before = path.stat()
        if case_id == "C14":
            sibling = bundle / "replacement.tmp"
            sibling.write_bytes(b"[" + path.read_bytes()[1:])
            os.utime(sibling, ns=(before.st_atime_ns, before.st_mtime_ns))
            os.replace(sibling, path)
            assert path.stat().st_ino != before.st_ino
        else:
            _flip_first(path)
            target_mtime = before.st_mtime_ns if case_id == "C13" else before.st_mtime_ns + 1_000_000_000
            os.utime(path, ns=(before.st_atime_ns, target_mtime))
            now = path.stat()
            if case_id == "C12":
                assert now.st_size == before.st_size and now.st_mtime_ns != before.st_mtime_ns
            else:
                assert now.st_size == before.st_size and now.st_mtime_ns == before.st_mtime_ns
                assert now.st_ctime_ns != before.st_ctime_ns
    elif case_id == "C21":
        original_limit = reader.MAX_FILES
        limit = max(len(manifest["files"]), len(list(bundle.iterdir()))) + 2
        monkeypatch.setattr(reader, "MAX_FILES", limit)
        monkeypatch.setattr(wire_reader, "MAX_FILES", limit)
        for number in range(limit + 1):
            (bundle / f"extra-{number:03d}").write_bytes(b"x")
        started = time.perf_counter()
        value = reader.load_assurance_evidence()
        assert time.perf_counter() - started < 5.0
        _expect(case_id, value, calls)
        # A separate dirty sibling exercises the symlink-directory refusal.
        monkeypatch.setattr(reader, "MAX_FILES", original_limit)
        monkeypatch.setattr(wire_reader, "MAX_FILES", original_limit)
        sibling, _ = synthetic_release(tmp_path / "symlink-dir")
        (_bundle(sibling) / "linked").symlink_to(_bundle(sibling), target_is_directory=True)
        with pytest.raises(ValueError, match="symlink"):
            reader._load(sibling)
        return
    else:
        raise AssertionError(f"unhandled corpus case: {case_id}")
    _expect(case_id, reader.load_assurance_evidence(), calls)


def test_stale_roster_report_boundary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A stale bundle changes only the exact unavailable assurance projection."""
    from gnd import api, report

    package, _ = synthetic_release(tmp_path)
    reader._assurance_cache.clear()
    monkeypatch.setattr(reader.resources, "files", lambda _name: package)
    fixtures = Path(__file__).parent / "fixtures/checker"
    model = fixtures / "misc.orm.yaml"
    population = fixtures / "population.misc_pass.yaml"
    current = api.check(model, population, unredacted=True)
    assert current["assurance"]["scope_digest"] is not None
    assert current["assurance"]["assumptions"] == ["synthetic-release-test"]

    (package / "new_module.py").write_bytes(b"phase_2_added = True\n")
    stale = api.check(model, population, unredacted=True)
    expected = dict(current)
    expected["assurance"] = {
        "schema_version": 1,
        "semantic_decision": current["assurance"]["semantic_decision"],
        "assurance_level": "none",
        "scope_digest": None,
        "semantics_digest": None,
        "production_roster_digest": None,
        "proof_digest": None,
        "toolchain_digest": None,
        "uncovered_applicable_scope_ids": current["assurance"]["uncovered_applicable_scope_ids"],
        "assumptions": [],
    }
    assert report.render_json(stale) == report.render_json(expected)


def test_unavailable_projection_after_positive_coverage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Exercise the level and uncovered-ID transition with a test-only capability."""
    from gnd import api, report

    _, manifest = synthetic_release(tmp_path)
    for row in manifest["rows"]:
        row["status"] = "proved"
    positive_evidence = reader._capability(manifest=manifest)
    unavailable_evidence = reader._capability(reason="unavailable-or-invalid-evidence")
    scopes = []
    real_scope = api.derive_assurance_scope

    def capture_scope(*args: Any, **kwargs: Any) -> Any:
        value = real_scope(*args, **kwargs)
        scopes.append(value)
        return value

    monkeypatch.setattr(checking_service, "derive_assurance_scope", capture_scope)
    fixtures = Path(__file__).parent / "fixtures/checker"
    model = fixtures / "misc.orm.yaml"
    population = fixtures / "population.misc_pass.yaml"
    monkeypatch.setattr(checking_service, "load_assurance_evidence", lambda: positive_evidence)
    positive = api.check(model, population, unredacted=True)
    assert positive["assurance"]["assurance_level"] == "proof-backed"
    assert positive["assurance"]["uncovered_applicable_scope_ids"] == []

    monkeypatch.setattr(checking_service, "load_assurance_evidence", lambda: unavailable_evidence)
    unavailable = api.check(model, population, unredacted=True)
    assert len(scopes) == 2
    assert scopes[0].applicable_scope_ids == scopes[1].applicable_scope_ids
    expected = dict(positive)
    expected["assurance"] = {
        "schema_version": 1,
        "semantic_decision": positive["assurance"]["semantic_decision"],
        "assurance_level": "none",
        "scope_digest": None,
        "semantics_digest": None,
        "production_roster_digest": None,
        "proof_digest": None,
        "toolchain_digest": None,
        "uncovered_applicable_scope_ids": sorted(scopes[1].applicable_scope_ids),
        "assumptions": [],
    }
    assert expected["assurance"]["uncovered_applicable_scope_ids"]
    assert report.render_json(unavailable) == report.render_json(expected)


@pytest.mark.parametrize("stage", ["first-post", "retry-pre", "retry-post"])
def test_fingerprint_failure_retry_branch(
    stage: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each post-authentication snapshot error has a separate outcome control."""
    package, _ = synthetic_release(tmp_path)
    reader._assurance_cache.clear()
    monkeypatch.setattr(reader.resources, "files", lambda _name: package)
    real_fingerprint, real_load = reader._fingerprint, reader._load
    calls = {"fingerprint": 0, "full": 0}

    def fingerprint(root: Path) -> Any:
        calls["fingerprint"] += 1
        number = calls["fingerprint"]
        if (stage == "first-post" and number == 2) or (
            stage == "retry-pre" and number == 3
        ) or (stage == "retry-post" and number == 4):
            raise OSError(f"injected {stage} fingerprint failure")
        value = real_fingerprint(root)
        if number == 2:
            return replace(value, anchor_sha256="0" * 64)
        return value

    def full_load(root: Any) -> Any:
        calls["full"] += 1
        return real_load(root)

    monkeypatch.setattr(reader, "_fingerprint", fingerprint)
    monkeypatch.setattr(reader, "_load", full_load)
    value = reader.load_assurance_evidence()
    assert calls == {"fingerprint": 4, "full": 2}
    if stage == "first-post":
        assert value.available
        assert reader.load_assurance_evidence() is value
        assert calls["full"] == 2
    else:
        assert not value.available
        assert not reader._assurance_cache


@pytest.mark.parametrize("entry", ["anchor.json", "assurance-anchor.schema.json"])
def test_public_loader_refuses_special_entry_without_blocking(entry: str, tmp_path: Path) -> None:
    """A special entry encountered before census must not hold a public call open."""
    package, _ = synthetic_release(tmp_path)
    assert reader._load(package).available
    path = _bundle(package) / entry if entry == "anchor.json" else package / entry
    path.unlink()
    os.mkfifo(path)
    script = (
        "import sys; from pathlib import Path; from gnd.assurance import evidence as r; "
        "r.resources.files = lambda _name: Path(sys.argv[1]); "
        "print(r.load_assurance_evidence().available)"
    )
    try:
        observed = subprocess.run(
            [sys.executable, "-c", script, str(package)],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
    except subprocess.TimeoutExpired:
        pytest.fail(f"public loader blocked on {entry}")
    assert observed.returncode == 0, observed.stderr
    assert observed.stdout.strip() == "False"


def test_nonpath_public_loader_refuses_special_entry_without_blocking(tmp_path: Path) -> None:
    """The non-Path Traversable route has the same early FIFO refusal."""
    package, _ = synthetic_release(tmp_path)
    assert reader._load(_WrappedPackage(package)).available
    path = _bundle(package) / "anchor.json"
    path.unlink()
    os.mkfifo(path)
    script = (
        "import sys; from pathlib import Path; "
        "sys.path.insert(0, sys.argv[2]); "
        "from test_v63_phase2_cache import _WrappedPackage; "
        "from gnd.assurance import evidence as r; "
        "r.resources.files = lambda _name: _WrappedPackage(Path(sys.argv[1])); "
        "print(r.load_assurance_evidence().available)"
    )
    try:
        observed = subprocess.run(
            [sys.executable, "-c", script, str(package), str(Path(__file__).parent)],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
    except subprocess.TimeoutExpired:
        pytest.fail("non-Path public loader blocked on anchor.json")
    assert observed.returncode == 0, observed.stderr
    assert observed.stdout.strip() == "False"


def test_roster_entry_cap_counts_ignored_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A source directory's unselected entries still consume the walk cap."""
    package = tmp_path / "gnd"
    package.mkdir()
    (package / "one.py").write_bytes(b"x = 1\n")
    for number in range(5):
        (package / f"ignored-{number}.txt").write_bytes(b"x")
    monkeypatch.setattr(reader, "MAX_FILES", 2)
    monkeypatch.setattr(wire_reader, "MAX_FILES", 2)
    with pytest.raises(ValueError, match="production roster entry limit"):
        reader.production_roster(package)


def test_roster_refuses_unaddressed_symlink(tmp_path: Path) -> None:
    """Symlink refusal does not depend on the addressed-component hit guard."""
    package = tmp_path / "gnd"
    package.mkdir()
    (package / "one.py").write_bytes(b"x = 1\n")
    (package / "ignored.txt").symlink_to("one.py")
    with pytest.raises(ValueError, match="production roster entry is a symlink"):
        reader.production_roster(package)
