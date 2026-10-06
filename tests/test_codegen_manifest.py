"""The codegen manifest: a closed, digest-bound, path-safe record with a real
WRITER — the half the extraction lane never had as a function.

RESEARCH §1.3 item 6 found the ``artifacts.json`` writer and its
recorded-vs-actual digest loop INLINE in ``cli.py:829-877``, not as reusable
functions. This suite pins the writer/reader pair, the path safety applied at
READ time (the manifest is untrusted committed metadata whose entries are
paths), the manifest-last ordering, and the published integrity blind spot.

Two things in here are deliberately not what they look like:

* The determinism test's non-vacuity floor is derived from the LOADED MODEL and
  the emitter, never hardcoded. "Two runs produce byte-identical manifests" is
  trivially satisfied by a manifest with zero files — plan 03's M-E2 proved
  exactly that shape passes a digest comparison.
* The closure test asserts ``src/gnd/cli.py`` is NOT reachable from the
  generation lane. That is the receipt for this plan's layering decision, not
  decoration: measured, the ``gnd.cli`` reach-in grew scan 5's closure from 21
  modules to 45.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import stat
from pathlib import Path
from typing import Any, get_args

import pytest
from support.rf5_sources import cli_sources

from gnd.codegen.emit import emit_project, write_project
from gnd.codegen.manifest import (
    CODEGEN_MANIFEST_VERSION,
    INTEGRITY_LIMITS,
    MANIFEST_FILENAME,
    MAX_CODEGEN_MANIFEST_BYTES,
    CodegenManifest,
    CodegenManifestError,
    ManagedFile,
    Ownership,
    build_manifest,
    manifest_path,
    read_manifest,
    render_manifest,
    write_manifest,
)
from gnd.model import load_model

REPO_ROOT = Path(__file__).resolve().parent.parent
FULL_VOCABULARY = REPO_ROOT / "tests" / "fixtures" / "models" / "full_vocabulary.orm.yaml"
KEYWORDS = REPO_ROOT / "tests" / "fixtures" / "models" / "keywords.orm.yaml"


def _generate(out_root: Path, model_path: Path = FULL_VOCABULARY) -> Any:
    """Emit + publish a whole project with its manifest, the way the CLI does."""
    model = load_model(str(model_path))
    project = emit_project(model, str(model_path), skill_name=out_root.resolve().name)
    manifest = build_manifest(project, str(model_path))
    write_project(project, out_root, manifest_text=render_manifest(manifest))
    return model, project, manifest


# --------------------------------------------------------------------------
# the published surface
# --------------------------------------------------------------------------


def test_write_manifest_and_read_manifest_are_module_level_functions() -> None:
    """Both halves exist as FUNCTIONS. The writer is the one that did not."""
    from gnd.codegen import manifest as module

    for name in ("read_manifest", "write_manifest", "build_manifest", "render_manifest"):
        assert callable(getattr(module, name, None)), (
            f"{name} is not a module-level function of gnd.codegen.manifest; the "
            f"whole point of this module is that the digest loop stops being "
            f"inline in cli.py"
        )
        assert name in module.__all__, f"{name} is not exported"


def test_ownership_is_a_module_level_literal_with_exactly_two_members() -> None:
    """G-05: derived means CODE-EMITTED; everything an LLM wrote is extension."""
    assert set(get_args(Ownership)) == {"derived", "extension"}


def test_the_manifest_version_is_published_with_a_bump_rule() -> None:
    from gnd.codegen import manifest as module

    assert isinstance(CODEGEN_MANIFEST_VERSION, int)
    lines = Path(module.__file__).read_text(encoding="utf-8").splitlines()
    assignment = next(
        index
        for index, line in enumerate(lines)
        if line.startswith("CODEGEN_MANIFEST_VERSION =")
    )
    preceding = []
    cursor = assignment - 1
    while cursor >= 0 and lines[cursor].startswith("#:"):
        preceding.append(lines[cursor])
        cursor -= 1
    assert preceding, (
        "CODEGEN_MANIFEST_VERSION carries no `#:` comment block; the bump rule "
        "must travel with the constant (the fidelity/report.py:64 precedent)"
    )
    assert "bump" in " ".join(preceding).lower() or "refus" in " ".join(preceding).lower()


def test_the_integrity_limits_are_published_as_data_not_only_as_prose() -> None:
    """RESEARCH §2.5 requires the blind spot be PUBLISHED, and plan 05's payload
    consumes exactly this tuple. A limitation stated only in a docstring is one
    skim away from not existing (the G-08 posture, applied one plan early)."""
    assert isinstance(INTEGRITY_LIMITS, tuple)
    assert INTEGRITY_LIMITS, "the limits tuple is empty"
    joined = " ".join(INTEGRITY_LIMITS).lower()
    assert "own digest" in joined, (
        "the co-edit blind spot — a manifest cannot record its own digest — is "
        f"not stated in INTEGRITY_LIMITS: {INTEGRITY_LIMITS}"
    )
    assert "extension" in joined, (
        "the extension files are never digest-gated bound (G-05) is not stated"
    )


def test_the_module_docstring_states_the_blind_spot_and_the_non_refactor() -> None:
    from gnd.codegen import manifest as module

    doc = (module.__doc__ or "").lower()
    assert "own digest" in doc, "the co-edit blind spot is missing from the docstring"
    assert "cli.py" in doc, (
        "the deliberate non-refactor of cli.py's extraction bundle index is not "
        "recorded, so the duplication reads as an oversight rather than a choice"
    )


# --------------------------------------------------------------------------
# determinism, with a model-derived non-vacuity floor
# --------------------------------------------------------------------------


def test_two_runs_produce_byte_identical_manifests_with_a_model_derived_floor(
    tmp_path: Path,
) -> None:
    """The determinism claim, floored so it cannot pass over an empty manifest.

    The floor is computed from the LOADED MODEL and the emitter — never written
    as a literal — in three layers:

    1. ``files`` is non-empty;
    2. its relpaths equal the emitted project's relpaths exactly (so a manifest
       that recorded three of nine files is a failure, not a pass);
    3. the derived surface is model-relative: the emitted ``tools.py`` defines
       one tool per fact type, and its digest is recorded.

    Layer 3 is what stops "well-formed nothing" from satisfying layers 1-2 — the
    M-E2 shape from plan 03, where a zero-tool emitter produced two byte-identical
    outputs and the digest comparison PASSED.
    """
    model, project, manifest = _generate(tmp_path / "first" / "project")
    _model2, project2, manifest2 = _generate(tmp_path / "second" / "project")

    left = render_manifest(manifest)
    right = render_manifest(manifest2)

    # Floor first, so a vacuous manifest can never reach the comparison.
    assert manifest.files, "the manifest recorded zero files"
    assert {entry.relpath for entry in manifest.files} == set(project.relpaths), (
        "the manifest does not cover exactly the emitted project"
    )
    derived = {entry.relpath for entry in manifest.files if entry.ownership == "derived"}
    assert derived == {file.relpath for file in project.derived}

    tools_rel = f"{project.package}/tools.py"
    tools_source = next(f.text for f in project.files if f.relpath == tools_rel)
    emitted_tools = [
        node.name
        for node in ast.parse(tools_source).body
        if isinstance(node, ast.FunctionDef)
    ]
    assert len(emitted_tools) == len(model.fact_types), (
        f"the emitted tool count {len(emitted_tools)} is not one per fact type "
        f"({len(model.fact_types)}); a manifest over well-formed nothing would "
        f"still compare byte-identical"
    )
    recorded = {entry.relpath: entry.sha256 for entry in manifest.files}
    assert recorded[tools_rel] == hashlib.sha256(
        tools_source.encode("utf-8")
    ).hexdigest()

    assert left == right, "two runs over one model produced different manifests"
    assert project.relpaths == project2.relpaths


def test_the_manifest_records_the_model_path_and_digest(tmp_path: Path) -> None:
    _model, _project, manifest = _generate(tmp_path / "project")
    assert manifest.model.sha256 == hashlib.sha256(
        FULL_VOCABULARY.read_bytes()
    ).hexdigest()
    assert manifest.model.path.endswith("full_vocabulary.orm.yaml")


def test_the_manifest_never_records_itself(tmp_path: Path) -> None:
    """The blind spot, asserted structurally rather than only documented.

    ``artifacts`` in the extraction bundle index does not include itself either
    (``cli.py:968-976``); this is the same bound, and stating it as a test is
    what keeps a later "let's also record the manifest" change honest about
    being impossible rather than merely omitted.
    """
    _model, _project, manifest = _generate(tmp_path / "project")
    assert MANIFEST_FILENAME not in {entry.relpath for entry in manifest.files}


# --------------------------------------------------------------------------
# read-time refusals — the manifest is untrusted committed metadata
# --------------------------------------------------------------------------


def _tamper(root: Path, mutate) -> Path:
    path = manifest_path(root)
    document = json.loads(path.read_text(encoding="utf-8"))
    mutate(document)
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return path


@pytest.mark.parametrize(
    "relpath",
    [
        "/etc/passwd",
        "../escape.py",
        "sub/../../escape.py",
        "C:\\evil.py",
        "\\\\server\\share\\evil.py",
    ],
)
def test_an_unsafe_relpath_is_refused_at_read_time(tmp_path: Path, relpath: str) -> None:
    """Absolute (POSIX **and** Windows), drive-lettered, and escaping entries.

    Checked under both path flavours because a manifest is a committed artifact
    that crosses machines — ``C:\\evil`` is an ordinary relative name to POSIX
    ``Path`` and would otherwise resolve INSIDE the project and be accepted.
    """
    root = tmp_path / "project"
    _generate(root)
    path = _tamper(root, lambda doc: doc["files"].append(
        {"relpath": relpath, "sha256": "0" * 64, "ownership": "derived"}
    ))
    with pytest.raises(CodegenManifestError) as caught:
        read_manifest(path)
    message = str(caught.value)
    assert relpath in message or repr(relpath) in message, (
        "the refusal does not name the offending value, so a mutation check "
        "cannot tell a test that reds for the right reason from one that reds "
        f"for any reason: {message}"
    )


def test_a_planted_symlink_does_not_deny_the_whole_manifest(tmp_path: Path) -> None:
    """The read/write division, asserted as behaviour.

    ``install.safe_destination``'s docstring is the shipped rule: it *"gates
    every write and every delete; never a read"*, and *"a symlink standing AT a
    destination is a classification verdict (``collided``), not a path error"*.

    MEASURED during plan 03-04: applying the filesystem-resolution half at read
    time made ONE planted symlink refuse the entire manifest at band 3 — a
    denial of regeneration for every other file in the project, strictly worse
    than the per-file refusal at band 11 the classifier already produces. So the
    read keeps the LEXICAL half, and the containment half runs at the write.
    """
    root = tmp_path / "project"
    _generate(root)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "tools.py").write_text("x = 1\n", encoding="utf-8")
    (root / "link").symlink_to(outside)

    path = _tamper(root, lambda doc: doc["files"].append(
        {"relpath": "link/tools.py", "sha256": "0" * 64, "ownership": "derived"}
    ))
    # The record still READS — one planted link cannot deny the project.
    manifest = read_manifest(path)
    assert "link/tools.py" in {entry.relpath for entry in manifest.files}


def test_a_write_through_a_symlinked_ancestor_is_refused_by_the_shipped_guard(
    tmp_path: Path,
) -> None:
    """The other half of the division: the WRITE gate refuses the escape.

    ``os.lstat`` does not follow the FINAL component but does follow every
    ancestor, so a symlinked directory in the middle of a relpath is invisible
    to the classifier and must be caught where the bytes land.
    """
    from gnd.install import InstallPathError
    from gnd.synth.paths import safe_output_path

    root = tmp_path / "project"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (root / "link").symlink_to(outside)

    with pytest.raises(InstallPathError):
        safe_output_path(root, "link/tools.py")


def test_an_unknown_top_level_key_is_refused(tmp_path: Path) -> None:
    root = tmp_path / "project"
    _generate(root)
    path = _tamper(root, lambda doc: doc.__setitem__("surprise", True))
    with pytest.raises(CodegenManifestError):
        read_manifest(path)


def test_an_unknown_ownership_value_is_refused(tmp_path: Path) -> None:
    root = tmp_path / "project"
    _generate(root)
    path = _tamper(
        root, lambda doc: doc["files"][0].__setitem__("ownership", "partly-derived")
    )
    with pytest.raises(CodegenManifestError):
        read_manifest(path)


def test_a_manifest_declaring_a_newer_version_is_refused(tmp_path: Path) -> None:
    """Refused, never guessed at — install.py's MANIFEST_SCHEMA posture."""
    root = tmp_path / "project"
    _generate(root)
    path = _tamper(
        root,
        lambda doc: doc.__setitem__("manifest_version", CODEGEN_MANIFEST_VERSION + 1),
    )
    with pytest.raises(CodegenManifestError):
        read_manifest(path)


def test_a_manifest_over_the_byte_cap_is_refused_before_it_is_parsed(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    _generate(root)
    path = manifest_path(root)
    path.write_bytes(b"{" + b" " * (MAX_CODEGEN_MANIFEST_BYTES + 1) + b"}")
    with pytest.raises(CodegenManifestError) as caught:
        read_manifest(path)
    assert "cap" in str(caught.value).lower()


def test_a_manifest_that_is_not_json_is_refused(tmp_path: Path) -> None:
    root = tmp_path / "project"
    _generate(root)
    path = manifest_path(root)
    path.write_text("not json at all", encoding="utf-8")
    with pytest.raises(CodegenManifestError):
        read_manifest(path)


def test_a_written_manifest_reads_back_equal(tmp_path: Path) -> None:
    root = tmp_path / "project"
    _model, _project, manifest = _generate(root)
    assert read_manifest(manifest_path(root)) == manifest


def test_write_manifest_returns_the_path_it_wrote(tmp_path: Path) -> None:
    root = tmp_path / "fresh"
    root.mkdir()
    manifest = CodegenManifest(
        manifest_version=CODEGEN_MANIFEST_VERSION,
        gnd_version="0.0.0",
        model={"path": "m.orm.yaml", "sha256": "0" * 64},
        files=[ManagedFile(relpath="a.py", sha256="1" * 64, ownership="derived")],
    )
    written = write_manifest(root, manifest)
    assert written == manifest_path(root)
    assert written.is_file()


def test_write_manifest_does_not_follow_a_planted_staging_symlink(
    tmp_path: Path,
) -> None:
    root = tmp_path / "fresh"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("keep me\n", encoding="utf-8")
    planted = root / ".gnd-codegen.json.tmp"
    planted.symlink_to(outside)
    manifest = CodegenManifest(
        manifest_version=CODEGEN_MANIFEST_VERSION,
        gnd_version="0.0.0",
        model={"path": "m.orm.yaml", "sha256": "0" * 64},
        files=[ManagedFile(relpath="a.py", sha256="1" * 64, ownership="derived")],
    )

    written = write_manifest(root, manifest)

    assert outside.read_text(encoding="utf-8") == "keep me\n"
    assert planted.is_symlink()
    assert read_manifest(written) == manifest


# --------------------------------------------------------------------------
# the manifest is written LAST
# --------------------------------------------------------------------------


def test_a_crashed_run_leaves_no_manifest(tmp_path: Path, monkeypatch) -> None:
    """A crash mid-publication must never leave a manifest describing files that
    do not exist — ``_cmd_extract``'s load-bearing index-last ordering.

    The failure is injected into the LAST artifact write, so the manifest is the
    only thing that could still have landed. The assertion is on the target root
    itself: nothing was published at all.
    """
    model = load_model(str(FULL_VOCABULARY))
    root = tmp_path / "project"
    project = emit_project(
        model, str(FULL_VOCABULARY), skill_name=root.resolve().name
    )
    manifest = build_manifest(project, str(FULL_VOCABULARY))

    import gnd.codegen.emit as emit_module

    real = emit_module._write_staged_file
    calls: list[str] = []

    def exploding(root_fd, rel, text):
        calls.append(str(rel))
        if len(calls) == len(project.files):  # the last artifact, before the manifest
            raise OSError("disk full")
        return real(root_fd, rel, text)

    monkeypatch.setattr(emit_module, "_write_staged_file", exploding)

    with pytest.raises(OSError):
        write_project(project, root, manifest_text=render_manifest(manifest))

    assert not root.exists(), f"a crashed run published {sorted(root.rglob('*'))}"
    assert not manifest_path(root).exists()


@pytest.mark.parametrize("failure_kind", ["write", "fsync"])
@pytest.mark.parametrize("failure_index", [1, 3], ids=["first-leaf", "later-leaf"])
@pytest.mark.parametrize("nested", [False, True], ids=["direct", "multi-component"])
def test_failed_staged_leaf_cleans_private_tree_and_created_ancestors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_kind: str,
    failure_index: int,
    nested: bool,
) -> None:
    """CR-03: every partial leaf and call-created output component is private."""
    from gnd.codegen import emit as emit_module

    root = (
        tmp_path / "new-a" / "new-b" / "project"
        if nested
        else tmp_path / "project"
    )
    model = load_model(str(FULL_VOCABULARY))
    project = emit_project(model, str(FULL_VOCABULARY), skill_name=root.name)
    manifest = build_manifest(project, str(FULL_VOCABULARY))

    if failure_kind == "write":
        real_fdopen = emit_module.os.fdopen
        opened = 0

        class FailingWriter:
            def __init__(self, handle):
                self.handle = handle

            def __enter__(self):
                self.handle.__enter__()
                return self

            def __exit__(self, *args):
                return self.handle.__exit__(*args)

            def write(self, _data):
                raise OSError("injected staged write failure")

            def flush(self):
                self.handle.flush()

            def fileno(self):
                return self.handle.fileno()

        def failing_fdopen(fd, mode):
            nonlocal opened
            opened += 1
            handle = real_fdopen(fd, mode)
            return FailingWriter(handle) if opened == failure_index else handle

        monkeypatch.setattr(emit_module.os, "fdopen", failing_fdopen)
    else:
        real_fsync = emit_module.os.fsync
        synced_files = 0

        def failing_fsync(fd):
            nonlocal synced_files
            if stat.S_ISREG(os.fstat(fd).st_mode):
                synced_files += 1
                if synced_files == failure_index:
                    raise OSError("injected staged fsync failure")
            return real_fsync(fd)

        monkeypatch.setattr(emit_module.os, "fsync", failing_fsync)

    with pytest.raises(OSError, match=f"injected staged {failure_kind} failure"):
        write_project(project, root, manifest_text=render_manifest(manifest))

    assert not root.exists()
    assert not (tmp_path / "new-a").exists()
    assert list(tmp_path.glob(".project.staging-*")) == []


def test_staged_writer_closes_the_raw_descriptor_when_fdopen_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """WR-01: fdopen failure unlinks the partial leaf and closes its raw fd."""
    from gnd.codegen import emit as emit_module

    root = tmp_path / "staging"
    root.mkdir()
    root_fd = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    captured: list[int] = []
    real_open = emit_module.os.open

    def recording_open(path, flags, *args, **kwargs):
        fd = real_open(path, flags, *args, **kwargs)
        if flags & os.O_CREAT:
            captured.append(fd)
        return fd

    def failing_fdopen(_fd, _mode):
        raise OSError("injected codegen fdopen failure")

    monkeypatch.setattr(emit_module.os, "open", recording_open)
    monkeypatch.setattr(emit_module.os, "fdopen", failing_fdopen)
    try:
        with pytest.raises(OSError, match="injected codegen fdopen failure"):
            emit_module._write_staged_file(root_fd, "nested/leaf.txt", "bytes\n")
    finally:
        os.close(root_fd)

    assert len(captured) == 1
    with pytest.raises(OSError):
        os.fstat(captured[0])
    assert not (root / "nested" / "leaf.txt").exists()


@pytest.mark.parametrize("failure_point", ["binding-validation", "dup"])
def test_internal_publisher_descriptors_close_on_early_setup_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_point: str,
) -> None:
    """WR-01: internally owned parent/root fds acquire immediate cleanup guards."""
    from gnd.codegen import emit as emit_module
    from gnd.codegen import plan as plan_module
    from gnd.install import InstallPathError

    root = tmp_path / "project"
    root.mkdir()
    model = load_model(str(FULL_VOCABULARY))
    project = emit_project(model, str(FULL_VOCABULARY), skill_name=root.name)
    captured: list[int] = []
    real_bind = plan_module._bind_codegen_parent
    real_open_root = plan_module._open_codegen_root

    def recording_bind(candidate):
        parent_path, parts, fd = real_bind(candidate)
        captured.append(fd)
        if failure_point == "binding-validation":
            parts = ("different-root",)
        return parent_path, parts, fd

    def recording_open_root(candidate):
        fd = real_open_root(candidate)
        captured.append(fd)
        return fd

    monkeypatch.setattr(plan_module, "_bind_codegen_parent", recording_bind)
    monkeypatch.setattr(plan_module, "_open_codegen_root", recording_open_root)
    if failure_point == "dup":
        monkeypatch.setattr(
            emit_module.os,
            "dup",
            lambda _fd: (_ for _ in ()).throw(OSError("injected dup failure")),
        )

    with pytest.raises((OSError, InstallPathError)):
        write_project(project, root)

    owned_fds = set(captured)
    assert len(owned_fds) == 2
    for fd in owned_fds:
        with pytest.raises(OSError):
            os.fstat(fd)


def test_directory_durability_barriers_are_bottom_up_and_finish_at_parents(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CR-04: leaf fsyncs are followed by every required directory barrier."""
    from gnd.codegen import emit as emit_module

    root = tmp_path / "new-a" / "new-b" / "project"
    model = load_model(str(FULL_VOCABULARY))
    project = emit_project(model, str(FULL_VOCABULARY), skill_name=root.name)
    manifest = build_manifest(project, str(FULL_VOCABULARY))
    events: list[str] = []
    real_fsync_directory = emit_module._fsync_directory

    def recording_fsync(fd, label):
        events.append(label)
        real_fsync_directory(fd, label)

    monkeypatch.setattr(emit_module, "_fsync_directory", recording_fsync)

    write_project(project, root, manifest_text=render_manifest(manifest))

    staging_events = [event for event in events if event.startswith("staging:")]
    assert staging_events[-1] == "staging:."
    assert set(staging_events[:-1]) == {
        "staging:artifacts",
        "staging:full_vocabulary",
        "staging:references",
    }
    assert events[len(staging_events) :] == [
        "publication-parent",
        "output-parent:new-a",
        "output-parent:.",
    ]


@pytest.mark.parametrize("failed_barrier", ["staging:.", "publication-parent"])
def test_required_directory_barrier_failure_is_reported_before_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failed_barrier: str,
) -> None:
    """CR-04: no required durability failure can return a successful write."""
    from gnd.codegen import emit as emit_module

    root = tmp_path / "project"
    model = load_model(str(FULL_VOCABULARY))
    project = emit_project(model, str(FULL_VOCABULARY), skill_name=root.name)
    manifest = build_manifest(project, str(FULL_VOCABULARY))
    real_fsync_directory = emit_module._fsync_directory

    def failing_fsync(fd, label):
        if label == failed_barrier:
            raise OSError(5, "injected directory barrier failure")
        real_fsync_directory(fd, label)

    monkeypatch.setattr(emit_module, "_fsync_directory", failing_fsync)

    with pytest.raises(OSError, match="injected directory barrier failure"):
        write_project(project, root, manifest_text=render_manifest(manifest))

    if failed_barrier == "staging:.":
        assert not root.exists()
    else:
        assert manifest_path(root).is_file()


def test_the_manifest_is_the_last_staged_path(tmp_path: Path) -> None:
    """Ordering asserted on the write SEQUENCE, not only on the outcome."""
    model = load_model(str(FULL_VOCABULARY))
    root = tmp_path / "project"
    project = emit_project(
        model, str(FULL_VOCABULARY), skill_name=root.resolve().name
    )
    manifest = build_manifest(project, str(FULL_VOCABULARY))

    import gnd.codegen.emit as emit_module

    real = emit_module._write_staged_file
    order: list[str] = []

    def recording(root_fd, rel, text):
        order.append(str(rel))
        return real(root_fd, rel, text)

    original = emit_module._write_staged_file
    emit_module._write_staged_file = recording
    try:
        write_project(project, root, manifest_text=render_manifest(manifest))
    finally:
        emit_module._write_staged_file = original

    assert order[-1] == MANIFEST_FILENAME, (
        f"the manifest was not the last path staged: {order}"
    )
    assert len(order) == len(project.files) + 1


# --------------------------------------------------------------------------
# the layering receipt for this plan's gnd.cli decision
# --------------------------------------------------------------------------


def _closure(*roots: Path) -> set[Path]:
    """Scan 5's walk, recomputed here so this test owns its own measurement."""
    src = REPO_ROOT / "src"

    def imported(source: str) -> set[str]:
        names: set[str] = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                names.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                names.add(node.module)
                names.update(f"{node.module}.{a.name}" for a in node.names)
        return names

    def module_path(dotted: str) -> Path | None:
        parts = dotted.split(".")
        if parts[0] != "gnd":
            return None
        base = src.joinpath(*parts)
        if (base / "__init__.py").is_file():
            return base / "__init__.py"
        candidate = base.with_suffix(".py")
        return candidate if candidate.is_file() else None

    seen: set[Path] = set()
    queue = [path for root in roots for path in root.rglob("*.py")]
    assert queue, "the closure roots hold no modules — the roots are wrong"
    while queue:
        path = queue.pop()
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        for dotted in imported(path.read_text(encoding="utf-8")):
            target = module_path(dotted)
            if target is not None and target not in seen:
                queue.append(target)
    return seen


def test_the_codegen_lane_does_not_reach_into_the_cli() -> None:
    """The receipt for this plan's layering call, pinned so it cannot regress.

    Plan 03 imported ``cli._extraction_header_template`` from ``codegen/emit.py``
    through a function-local import and flagged it for this plan. MEASURED at
    plan-04 start and after, over ``src/gnd/codegen/``'s transitive import
    closure:

    ==============================  =========  =====================
    closure rooted at codegen/      modules    ``src/gnd/cli.py`` in?
    ==============================  =========  =====================
    before (the reach-in)                  44  yes
    after (``gnd.extract.bundle``)         18  no
    ==============================  =========  =====================

    That one edge pulled the whole checker / measure / fidelity / synth stack
    into the offline scan's closure, so a network import anywhere reachable from
    ``cli.py`` would have red the codegen guard for a reason with nothing to do
    with codegen.

    This plan extracted the shared owner into :mod:`gnd.extract.bundle` instead
    of copying it (G-03′ forbids the copy) and instead of leaving the inversion
    (a library module importing a CLI's private function). This test keeps the
    edge out.

    **Scoped to codegen deliberately, and the reason is a finding.** The wider
    ``GENERATION_LANE_ROOTS`` closure still reaches ``cli.py`` — through
    ``exp/close.py``'s ``from gnd.cli import EXIT_EXPERIMENT_OPEN``, the same
    defect shape in plan 03-02's lane. Extracting the exit-band register is out
    of this plan's scope (G-16′'s disjointness proof is defined as a grep over
    ``EXIT_[A-Z_]* *=`` assignments in ``cli.py``, so moving them is a decision
    that register's owner has to make), and it is recorded in
    ``deferred-items.md`` rather than fixed here or left unsaid.
    """
    closure = _closure(REPO_ROOT / "src" / "gnd" / "codegen")
    relative = sorted(str(p.relative_to(REPO_ROOT)) for p in closure)
    assert "src/gnd/cli.py" not in relative, (
        "the codegen lane reaches src/gnd/cli.py again. A library module "
        "importing a CLI's private function inverts the layering and pulls the "
        f"whole package into the offline closure ({len(relative)} modules): "
        f"{relative}"
    )
    assert "src/gnd/codegen/emit.py" in relative, (
        "the closure walk did not even reach the emitter — the roots are wrong "
        "and this guard is checking nothing"
    )
    assert "src/gnd/model.py" in relative, (
        "the closure walk never left src/gnd/codegen/ — a walk that stays inside "
        "its root is a directory listing wearing a closure's name, and it would "
        "keep passing after the reach-in came back one module deeper"
    )


def test_the_bundle_owner_is_one_module_with_two_callers() -> None:
    """``extract_stem`` / ``header_template`` have ONE owner, not three copies."""
    from gnd.extract import bundle

    assert callable(bundle.bundle_stem)
    assert callable(bundle.header_template)

    emit_source = (REPO_ROOT / "src" / "gnd" / "codegen" / "emit.py").read_text(
        encoding="utf-8"
    )
    cli_source = cli_sources()
    assert "from gnd.extract.bundle import" in emit_source
    assert "gnd.extract.bundle" in cli_source
    assert "from gnd.cli import" not in emit_source, (
        "codegen reaches into the CLI again"
    )


def test_the_keyword_model_also_produces_a_readable_manifest(tmp_path: Path) -> None:
    """The G-21 hazard fixture, through the manifest lane."""
    root = tmp_path / "kw"
    _model, project, manifest = _generate(root, KEYWORDS)
    reread = read_manifest(manifest_path(root))
    assert reread == manifest
    assert {e.relpath for e in reread.files} == set(project.relpaths)
