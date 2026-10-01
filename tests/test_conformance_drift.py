"""Conformance assertions #1 (integrity) and #2 (currency), and band 13.

**The claim these tests defend is not "conformance detects drift".** It is that
conformance detects drift *and stays silent about everything it did not check* —
which is the harder half, and the half G-08 exists for. A check that reported an
edited ``pyproject.toml`` as model-code drift would be louder, more impressive,
and wrong: GND never wrote that file's contents, so it has no record to compare
against and no standing to call it drift.

Three shapes recur here and each is deliberate:

* **Every drift assertion names the FILE or the DIGEST PAIR**, never merely a
  count. Common Pitfall 1 is a mutation that reds for the wrong reason, and
  ``len(findings) == 1`` cannot tell a correct detection from an unrelated
  crash that happened to produce one finding.
* **The over-correction control runs first.** A freshly generated project must
  yield ZERO findings from both assertions. Without it, both mutations below
  could be satisfied by a check that always fires — and a check that always
  fires looks exactly like a working gate.
* **The partition is asserted structurally.** ``examined ∪ unexamined`` equals
  the manifest's whole file set and the two are disjoint, so a file cannot
  vanish from both lists and take its own unexaminedness with it.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, get_args

import pytest

from gnd import cli
from gnd.cli import main
from gnd.codegen.emit import GeneratedProject, emit_project, write_project
from gnd.codegen.manifest import (
    CodegenManifest,
    ManagedFile,
    ManifestModelRef,
    build_manifest,
    manifest_path,
    read_manifest,
    render_manifest,
)
from gnd.conformance import (
    UNEXAMINED_REASON,
    ConformanceError,
    Finding,
    FindingKind,
)
from gnd.conformance.currency import check_currency, model_digest
from gnd.conformance.integrity import MAX_CONFORMANCE_BYTES, check_integrity
from gnd.model import load_model

REPO_ROOT = Path(__file__).resolve().parent.parent
FULL_VOCABULARY = REPO_ROOT / "tests" / "fixtures" / "models" / "full_vocabulary.orm.yaml"


# --------------------------------------------------------------------------- #
# fixtures — a real generated project, from a model the test can edit
# --------------------------------------------------------------------------- #


def _model_copy(tmp_path: Path) -> Path:
    """A COPY of the fixture model, so currency's mutation can edit it.

    Editing the committed fixture would leak across tests and, worse, would make
    the mutation's restore a git operation rather than a filesystem one.
    """
    destination = tmp_path / "model.orm.yaml"
    shutil.copyfile(FULL_VOCABULARY, destination)
    return destination


def _generate(root: Path, model_path: Path) -> GeneratedProject:
    """A real generated project, written through the shipped emitter.

    Deliberately NOT through ``gnd codegen``: task 1's whole claim is that these
    assertions are callable with no CLI in the picture, and a fixture that
    reached for the CLI would quietly make that untestable.
    """
    model = load_model(str(model_path))
    project = emit_project(model, str(model_path), skill_name=root.resolve().name)
    write_project(
        project,
        str(root),
        manifest_text=render_manifest(build_manifest(project, str(model_path))),
    )
    return project


def _a_derived_relpath(project: GeneratedProject) -> str:
    return min(file.relpath for file in project.files if file.ownership == "derived")


def _an_extension_relpath(project: GeneratedProject) -> str:
    return min(file.relpath for file in project.files if file.ownership == "extension")


# --------------------------------------------------------------------------- #
# the over-correction control (SC3 clause 1, G-09)
# --------------------------------------------------------------------------- #


def test_a_fresh_project_yields_zero_findings_from_both_assertions(
    tmp_path: Path,
) -> None:
    """Neither assertion is a check that always fires.

    This runs FIRST because every mutation below is worthless without it: a
    check that reports drift unconditionally passes both mutation tests and
    fails only this one.
    """
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))

    integrity = check_integrity(root, manifest)
    currency = check_currency(model_path, manifest)

    assert integrity.findings == (), (
        f"a freshly generated project reported integrity drift: "
        f"{[finding.message for finding in integrity.findings]}"
    )
    assert currency == (), (
        f"an unedited model reported currency drift: "
        f"{[finding.message for finding in currency]}"
    )
    # Non-vacuity: the control is only a control if something was actually
    # checked. Zero findings over zero examined files is not a passing gate.
    assert integrity.examined, "the control examined nothing, so it proves nothing"


# --------------------------------------------------------------------------- #
# assertion #1 — integrity
# --------------------------------------------------------------------------- #


def test_one_edited_byte_in_a_derived_file_is_named_by_exactly_one_finding(
    tmp_path: Path,
) -> None:
    """G-09 mutation #1, at the library level. The finding NAMES the relpath and
    carries both digests, so a reader can check the claim rather than trust it."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    project = _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))
    target = _a_derived_relpath(project)

    recorded = manifest.entries()[target].sha256
    original = (root / target).read_text(encoding="utf-8")
    (root / target).write_text(original + " ", encoding="utf-8")
    actual = hashlib.sha256((original + " ").encode("utf-8")).hexdigest()

    result = check_integrity(root, manifest)

    assert len(result.findings) == 1, (
        f"one edited byte produced {len(result.findings)} findings: "
        f"{[finding.target for finding in result.findings]}"
    )
    finding = result.findings[0]
    assert finding.kind == "derived-file-modified"
    assert finding.target == target
    assert target in finding.message
    assert finding.recorded_sha256 == recorded
    assert finding.actual_sha256 == actual
    assert recorded[:12] in finding.message and actual[:12] in finding.message, (
        "the finding does not show the digest pair, so it cannot be "
        "distinguished from one that guessed"
    )


def test_a_deleted_derived_file_is_reported_missing_rather_than_crashing(
    tmp_path: Path,
) -> None:
    """A file the manifest records and disk does not is a FINDING, not an
    exception: an exception would abort the check over the other eight files."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    project = _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))
    target = _a_derived_relpath(project)
    (root / target).unlink()

    result = check_integrity(root, manifest)

    assert [finding.kind for finding in result.findings] == ["derived-file-missing"]
    finding = result.findings[0]
    assert finding.target == target
    assert target in finding.message
    assert finding.actual_sha256 is None
    assert finding.recorded_sha256 == manifest.entries()[target].sha256
    # The other derived files were still examined — the check did not stop.
    assert len(result.examined) == len(
        [file for file in project.files if file.ownership == "derived"]
    )


def test_an_edited_extension_file_produces_no_finding_and_is_reported_unexamined(
    tmp_path: Path,
) -> None:
    """G-08. Conformance says NOTHING about extension code — and it says so out
    loud, in the payload, rather than by omission."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    project = _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))
    target = _an_extension_relpath(project)

    (root / target).write_text("# the user's own work\n", encoding="utf-8")

    result = check_integrity(root, manifest)

    assert result.findings == (), (
        f"an extension edit was reported as drift: "
        f"{[finding.message for finding in result.findings]} — conformance has "
        f"no record to compare an LLM- or human-authored file against, so "
        f"calling this drift would be a false claim"
    )
    unexamined = {entry.relpath: entry for entry in result.unexamined}
    assert target in unexamined, (
        f"{target} was neither checked nor reported unexamined; a file that "
        f"falls out of both lists takes its own unexaminedness with it"
    )
    assert unexamined[target].ownership == "extension"
    assert unexamined[target].reason == UNEXAMINED_REASON
    assert target not in {entry.relpath for entry in result.examined}


def test_the_partition_covers_every_manifest_entry_exactly_once(
    tmp_path: Path,
) -> None:
    """``examined ∪ unexamined == the manifest``, and the two are disjoint.

    The structural form of G-08: the payload's honest scope is a partition, so
    a file cannot be silently dropped from the report by being in neither list,
    nor double-counted by being in both.
    """
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    project = _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))

    result = check_integrity(root, manifest)
    examined = {entry.relpath for entry in result.examined}
    unexamined = {entry.relpath for entry in result.unexamined}

    assert examined | unexamined == set(manifest.entries())
    assert not (examined & unexamined)
    # Non-vacuity: this fixture genuinely has both kinds, so a partition that
    # collapsed to one side would red here rather than pass trivially.
    assert examined and unexamined, (
        "the fixture project has no derived or no extension files, so the "
        "partition claim is untested"
    )
    assert unexamined == {
        file.relpath for file in project.files if file.ownership == "extension"
    }


# --------------------------------------------------------------------------- #
# assertion #2 — currency
# --------------------------------------------------------------------------- #


def test_an_edited_model_produces_one_finding_carrying_both_digests(
    tmp_path: Path,
) -> None:
    """G-09 mutation #2, at the library level. The PAIR is the point: a finding
    saying only "the model changed" cannot be told apart from one that guessed."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))
    recorded = manifest.model.sha256

    model_path.write_text(
        model_path.read_text(encoding="utf-8") + "\n# touched, not regenerated\n",
        encoding="utf-8",
    )
    actual = model_digest(model_path)
    assert actual != recorded, "the mutation did not change the model's digest"

    findings = check_currency(model_path, manifest)

    assert len(findings) == 1
    finding = findings[0]
    assert finding.kind == "model-digest-mismatch"
    assert finding.target == model_path.name
    assert finding.recorded_sha256 == recorded
    assert finding.actual_sha256 == actual
    assert recorded[:12] in finding.message and actual[:12] in finding.message, (
        f"the finding does not show the recorded/actual digest PAIR: "
        f"{finding.message}"
    )


def test_currency_target_is_operator_neutral_for_absolute_and_relative_models(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "operator-home-sentinel" / "operator-user-sentinel"
    workspace.mkdir(parents=True)
    model_path = _model_copy(workspace)
    root = workspace / "operator-project-sentinel"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))
    model_path.write_text(
        model_path.read_text(encoding="utf-8") + "\n# touched\n",
        encoding="utf-8",
    )

    absolute = check_currency(model_path, manifest)
    monkeypatch.chdir(workspace)
    relative = check_currency(Path("model.orm.yaml"), manifest)

    assert absolute == relative
    assert [finding.target for finding in absolute] == ["model.orm.yaml"]
    serialized = "\n".join(
        (finding.target + "\n" + finding.message) for finding in absolute
    )
    for forbidden in (
        workspace.as_posix(),
        "operator-home-sentinel",
        "operator-user-sentinel",
        "operator-project-sentinel",
    ):
        assert forbidden not in serialized


def test_integrity_stays_green_when_only_the_model_moved(tmp_path: Path) -> None:
    """The two assertions are INDEPENDENT and corroborating, not one check with
    two names: a model edit is invisible to integrity, whose files are all
    still exactly what the manifest recorded."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))

    model_path.write_text(
        model_path.read_text(encoding="utf-8") + "\n# touched\n", encoding="utf-8"
    )

    assert check_integrity(root, manifest).findings == ()
    assert len(check_currency(model_path, manifest)) == 1


def test_model_digest_over_an_unreadable_model_refuses_rather_than_guessing(
    tmp_path: Path,
) -> None:
    """Fail closed. Returning a sentinel digest would make an absent model
    read as drift, sending the user to regenerate over a file that is gone."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))
    model_path.unlink()

    with pytest.raises(ConformanceError) as caught:
        check_currency(model_path, manifest)
    assert str(model_path) in str(caught.value)


# --------------------------------------------------------------------------- #
# the standalone-callable claim (Phase 4's MODEL-02 depends on it)
# --------------------------------------------------------------------------- #


def test_currency_is_importable_with_no_cli_in_the_process() -> None:
    """Phase 4's MODEL-02 calls this from a third entry point entirely.

    Asserted in a FRESH interpreter, because ``gnd.cli`` is already imported in
    this test session and an in-process check would be a guard that cannot fail.
    The negative control below proves the probe can report ``True``.
    """
    probe = (
        "import sys\n"
        "from gnd.conformance.currency import check_currency, model_digest\n"
        "print('gnd.cli' in sys.modules)\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "False", (
        "importing the currency assertion dragged gnd.cli into the process; the "
        "assertion is then CLI-coupled in everything but name"
    )

    control = subprocess.run(
        [sys.executable, "-c", "import sys, gnd.cli; print('gnd.cli' in sys.modules)"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert control.stdout.strip() == "True", (
        "the probe cannot report True at all, so it proves nothing"
    )


# --------------------------------------------------------------------------- #
# the finding vocabulary is published DATA with no unreachable member
# --------------------------------------------------------------------------- #


def test_finding_kind_is_a_module_level_closed_literal_with_no_unemitted_member() -> None:
    """An unreachable enum member is indistinguishable from an unimplemented
    check — it reads as coverage that does not exist.

    Every declared kind must appear as a literal in one of the assertion
    modules that can emit it. Self-check below proves the search can fail.
    """
    from gnd.conformance import architecture as architecture_module
    from gnd.conformance import currency as currency_module
    from gnd.conformance import integrity as integrity_module
    from gnd.conformance import structural as structural_module

    sources = "".join(
        Path(module.__file__).read_text(encoding="utf-8")
        for module in (
            integrity_module,
            currency_module,
            structural_module,
            architecture_module,
        )
    )
    kinds = get_args(FindingKind)
    assert kinds, "FindingKind declares no members"
    for kind in kinds:
        assert f'"{kind}"' in sources, (
            f"FindingKind declares {kind!r} but no assertion module emits it; "
            f"an unreachable member reads as a check that exists"
        )
    assert '"model-code-structural-drift"' not in sources, (
        "the search cannot fail — it matches a kind nothing emits, so this "
        "guard would report green over an unreachable member"
    )


def test_a_finding_is_frozen_so_a_reader_cannot_edit_the_evidence() -> None:
    finding = Finding(
        kind="model-digest-mismatch",
        target="model.orm.yaml",
        message="…",
        recorded_sha256="0" * 64,
        actual_sha256="1" * 64,
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        finding.target = "elsewhere"  # type: ignore[misc]


# --------------------------------------------------------------------------- #
# hostile input: the tree under inspection is user-controlled (T-03-24/25/28)
# --------------------------------------------------------------------------- #


def test_a_manifest_relpath_is_re_checked_before_any_file_is_opened(
    tmp_path: Path,
) -> None:
    """T-03-25. ``read_manifest`` already refuses this — and conformance
    re-applies it anyway, because a caller can construct a ``CodegenManifest``
    directly and nothing about "our own reader would have caught it" survives
    that."""
    root = tmp_path / "project"
    root.mkdir()
    hostile = CodegenManifest(
        manifest_version=1,
        gnd_version="0.0.0",
        model=ManifestModelRef(path="model.orm.yaml", sha256="0" * 64),
        files=[
            ManagedFile(relpath="../escape.txt", sha256="0" * 64, ownership="derived")
        ],
    )

    with pytest.raises(ConformanceError) as caught:
        check_integrity(root, hostile)
    assert "../escape.txt" in str(caught.value)


def test_conformance_never_imports_the_project_under_inspection() -> None:
    """T-03-24 / T-03-30. Importing a generated module to inspect it would
    execute arbitrary user code on every CI run. Assertions #1 and #2 read BYTES
    and hash them; assertion #3 reads them and ``ast.parse``s them, which is why
    it is scanned here too — it is the assertion that most obviously *could*
    have been written with ``importlib`` + ``inspect``."""
    from gnd.conformance import architecture as architecture_module
    from gnd.conformance import currency as currency_module
    from gnd.conformance import integrity as integrity_module
    from gnd.conformance import structural as structural_module

    sources = "".join(
        Path(module.__file__).read_text(encoding="utf-8")
        for module in (
            integrity_module,
            currency_module,
            structural_module,
            architecture_module,
        )
    )
    forbidden_tokens = ("importlib.import_module", "exec(", "eval(", "runpy", "__import__")
    for forbidden in forbidden_tokens:
        assert forbidden not in sources, (
            f"{forbidden} is reachable in the conformance assertions; the tree "
            f"under inspection is user-controlled and must never be executed"
        )
    planted = sources + "\nexec(project_source)\n"
    assert any(token in planted for token in forbidden_tokens), (
        "the never-execute fence cannot catch a planted execution token"
    )


def test_an_oversized_derived_file_is_reported_from_stat_and_never_hashed(
    tmp_path: Path,
) -> None:
    """T-03-28: bound every untrusted-input-proportional resource."""

    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    project = _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))
    target = _a_derived_relpath(project)
    huge = root / target

    with huge.open("r+b") as handle:
        handle.truncate(MAX_CONFORMANCE_BYTES + 1)

    result = check_integrity(root, manifest)

    finding = next(f for f in result.findings if f.target == target)
    assert finding.kind == "derived-file-modified"
    assert finding.actual_sha256 is None
    assert str(MAX_CONFORMANCE_BYTES) in finding.message


def test_a_symlink_at_a_derived_path_is_reported_and_never_followed(
    tmp_path: Path,
) -> None:
    """A link standing at a recorded path is drift, not a path error — and the
    check reads the LINK's own stat rather than whatever it points at."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    project = _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))
    target = _a_derived_relpath(project)

    elsewhere = tmp_path / "elsewhere.py"
    elsewhere.write_text((root / target).read_text(encoding="utf-8"), encoding="utf-8")
    (root / target).unlink()
    (root / target).symlink_to(elsewhere)

    result = check_integrity(root, manifest)

    finding = next(f for f in result.findings if f.target == target)
    assert finding.kind == "derived-file-modified"
    assert finding.actual_sha256 is None, (
        "the symlink's TARGET was hashed; a link whose target happens to hold "
        "the recorded bytes would then read as conforming"
    )
    assert "symlink" in finding.message.lower()


def test_conformance_refuses_a_symlinked_manifest_even_when_outside_bytes_match(
    tmp_path: Path,
) -> None:
    from gnd.conformance.service import run_conformance

    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = manifest_path(root)
    outside = tmp_path / "outside-manifest.json"
    outside.write_bytes(manifest.read_bytes())
    manifest.unlink()
    manifest.symlink_to(outside)

    result = run_conformance(model_path, root)

    assert result.exit_code == 74
    assert "manifest-io" in result.payload["error"]
    assert result.payload["examined"] == []


def test_conformance_refuses_an_intermediate_symlink_without_hashing_outside_bytes(
    tmp_path: Path,
) -> None:
    from gnd.conformance.service import run_conformance

    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    project = _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))
    target = next(
        entry.relpath
        for entry in manifest.files
        if entry.ownership == "derived" and "/" in entry.relpath
    )
    first = target.split("/", 1)[0]
    outside_parent = tmp_path / "outside-tree"
    outside_parent.mkdir()
    (root / first).rename(outside_parent / first)
    (root / first).symlink_to(outside_parent / first, target_is_directory=True)
    outside_digest = manifest.entries()[target].sha256

    result = run_conformance(model_path, root)

    assert result.exit_code == 74
    assert "file-io" in result.payload["error"]
    assert outside_digest not in json.dumps(result.payload["examined"])
    expected = next(file.text.encode("utf-8") for file in project.files if file.relpath == target)
    assert (outside_parent / target).read_bytes() == expected


@pytest.mark.parametrize("swap", ["leaf", "intermediate"])
def test_structural_scan_does_not_follow_a_post_integrity_swap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    swap: str,
) -> None:
    from gnd.conformance import structural as structural_module
    from gnd.conformance.service import run_conformance

    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))
    target = next(
        entry.relpath
        for entry in manifest.files
        if entry.ownership == "derived" and entry.relpath.endswith("/tools.py")
    )
    outside_parent = tmp_path / f"outside-{swap}"
    outside_target = outside_parent / target
    outside_target.parent.mkdir(parents=True)
    outside_target.write_bytes((root / target).read_bytes())
    real_expected_surface = structural_module.expected_surface
    injected = False

    def swap_after_integrity(model: Any):
        nonlocal injected
        if not injected:
            injected = True
            if swap == "leaf":
                (root / target).unlink()
                (root / target).symlink_to(outside_target)
            else:
                first = target.split("/", 1)[0]
                displaced = root / f"displaced-{first}"
                (root / first).rename(displaced)
                (root / first).symlink_to(
                    outside_parent / first,
                    target_is_directory=True,
                )
        return real_expected_surface(model)

    monkeypatch.setattr(structural_module, "expected_surface", swap_after_integrity)

    result = run_conformance(model_path, root)

    assert injected is True
    assert result.exit_code != 0
    assert outside_target.read_bytes()
    assert all(outside_parent.as_posix() not in item["message"] for item in result.payload["findings"])
    if swap == "intermediate":
        assert result.exit_code == 74
        assert "file-io" in result.payload["error"]
    else:
        assert result.exit_code == 13
        finding = next(item for item in result.payload["findings"] if item["target"] == target)
        assert finding["kind"] == "derived-file-modified"


def test_final_reconciliation_catches_a_derived_mutation_at_the_root_rebind(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from gnd.conformance import service as service_module
    from gnd.conformance.service import run_conformance

    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))
    target = next(
        entry.relpath
        for entry in manifest.files
        if entry.ownership == "derived" and entry.relpath.endswith("/tools.py")
    )
    real_bind = service_module.bind_project_root
    injected = False

    def mutate_after_rebind(*args: Any, **kwargs: Any) -> tuple[int, int]:
        nonlocal injected
        identity = real_bind(*args, **kwargs)
        if not injected:
            injected = True
            leaf = root / target
            leaf.write_bytes(leaf.read_bytes() + b"\n# mutation at final rebind\n")
        return identity

    monkeypatch.setattr(service_module, "bind_project_root", mutate_after_rebind)

    result = run_conformance(model_path, root)

    assert injected is True
    assert result.exit_code in {13, 74}
    assert not (
        result.exit_code == 0
        and result.payload["error"] is None
        and result.payload["findings"] == []
    )
    if result.exit_code == 13:
        finding = next(item for item in result.payload["findings"] if item["target"] == target)
        assert finding["kind"] == "derived-file-modified"


@pytest.mark.parametrize("failure", ["stat", "read"])
def test_structural_source_failures_publish_only_relative_closed_causes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
) -> None:
    from gnd.artifacts import ArtifactError
    from gnd.conformance import structural as structural_module
    from gnd.conformance.service import run_conformance

    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))
    target = next(
        entry.relpath
        for entry in manifest.files
        if entry.ownership == "derived" and entry.relpath.endswith("/tools.py")
    )
    target_name = Path(target).name
    absolute_sentinel = (tmp_path / "operator-private" / target_name).as_posix()
    injected = False

    if failure == "stat":
        real_stat = structural_module._stat_at

        def fail_stat(name: str, directory_fd: int):
            nonlocal injected
            if not injected and name == target_name:
                injected = True
                raise PermissionError(absolute_sentinel)
            return real_stat(name, directory_fd)

        monkeypatch.setattr(structural_module, "_stat_at", fail_stat)
    else:
        real_read = structural_module.read_regular_bounded_at

        def fail_read(root_fd: int, relative: str, **kwargs: Any):
            nonlocal injected
            if not injected and relative == target:
                injected = True
                raise ArtifactError(absolute_sentinel)
            return real_read(root_fd, relative, **kwargs)

        monkeypatch.setattr(structural_module, "read_regular_bounded_at", fail_read)

    result = run_conformance(model_path, root)
    rendered = json.dumps(result.payload, sort_keys=True)

    assert injected is True
    assert result.exit_code == 13
    assert absolute_sentinel not in rendered
    finding = next(
        item
        for item in result.payload["findings"]
        if item["kind"] == "unparseable-source" and item["target"] == target
    )
    assert finding["message"] == (
        f"{target} could not be "
        + ("inspected (cause: source-stat)" if failure == "stat" else "read (cause: source-read)")
    )


# --------------------------------------------------------------------------- #
# scan 5 — the conformance package joins the generation lane's offline guard
# --------------------------------------------------------------------------- #


def test_the_conformance_package_is_covered_by_the_generation_lane_scan() -> None:
    """Scan 5's roots are a tuple precisely so a new generation package joins it
    in the commit that creates the package (plan 03-03's posture)."""
    from support.offline_roots import GENERATION_LANE_ROOTS

    roots = {root.name for root in GENERATION_LANE_ROOTS}
    assert "conformance" in roots, (
        "src/gnd/conformance/ is outside scan 5, so a network import reachable "
        "from it would be caught by no scan at all"
    )
    assert {"exp", "codegen"} <= roots, "scan 5 lost a root it already covered"


# --------------------------------------------------------------------------- #
# band 13 and the CLI (task 3)
# --------------------------------------------------------------------------- #


def test_the_cli_over_a_fresh_project_exits_zero(tmp_path: Path) -> None:
    """The over-correction control, through the real command."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    assert main(["codegen", str(model_path), "--out", str(root)]) == 0
    assert main(["conformance", str(model_path), str(root)]) == 0


def test_the_cli_exits_thirteen_and_names_the_edited_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """G-09 mutation #1, through the real command. This is SC3."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    assert main(["codegen", str(model_path), "--out", str(root)]) == 0
    capsys.readouterr()

    manifest = read_manifest(manifest_path(root))
    target = min(
        relpath
        for relpath, entry in manifest.entries().items()
        if entry.ownership == "derived"
    )
    edited = root / target
    edited.write_text(edited.read_text(encoding="utf-8") + " ", encoding="utf-8")

    assert main(["conformance", str(model_path), str(root)]) == cli.EXIT_MODEL_CODE_DRIFT
    out = capsys.readouterr().out
    assert target in out, f"the report does not name {target}:\n{out}"


def test_the_cli_exits_thirteen_and_shows_the_model_digest_pair(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """G-09 mutation #2, through the real command. Model-code drift IS this."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    assert main(["codegen", str(model_path), "--out", str(root)]) == 0
    capsys.readouterr()

    recorded = read_manifest(manifest_path(root)).model.sha256
    model_path.write_text(
        model_path.read_text(encoding="utf-8") + "\n# touched\n", encoding="utf-8"
    )
    actual = model_digest(model_path)

    assert main(["conformance", str(model_path), str(root)]) == cli.EXIT_MODEL_CODE_DRIFT
    out = capsys.readouterr().out
    assert recorded[:12] in out and actual[:12] in out, (
        f"the report does not show the recorded/actual digest pair:\n{out}"
    )


def test_the_cli_exits_zero_over_an_edited_extension_file_and_lists_it_unexamined(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    assert main(["codegen", str(model_path), "--out", str(root)]) == 0
    capsys.readouterr()

    manifest = read_manifest(manifest_path(root))
    target = min(
        relpath
        for relpath, entry in manifest.entries().items()
        if entry.ownership == "extension" and relpath != "architecture.contract.yaml"
    )
    (root / target).write_text("# mine\n", encoding="utf-8")

    assert main(["conformance", str(model_path), str(root)]) == 0
    out = capsys.readouterr().out
    assert target in out
    assert "unexamined" in out.lower()


def test_the_cli_over_a_directory_with_no_manifest_exits_sixty_six(
    tmp_path: Path,
) -> None:
    """66, not 13: a missing required artifact is not a drift verdict. Reporting
    13 would send a CI job to regenerate over a project that does not exist."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "not-a-project"
    root.mkdir()
    assert main(["conformance", str(model_path), str(root)]) == cli.EXIT_NO_INPUT


def test_the_cli_over_a_missing_model_exits_sixty_six(tmp_path: Path) -> None:
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    assert main(["codegen", str(model_path), "--out", str(root)]) == 0
    model_path.unlink()
    assert main(["conformance", str(model_path), str(root)]) == cli.EXIT_NO_INPUT


def test_the_cli_over_an_unreadable_manifest_exits_three(tmp_path: Path) -> None:
    """3, not 13: the record will not parse, so nothing can be compared at all."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    assert main(["codegen", str(model_path), "--out", str(root)]) == 0
    manifest_path(root).write_text("{ not json", encoding="utf-8")
    assert main(["conformance", str(model_path), str(root)]) == 3


def test_the_conformance_description_enumerates_every_exit_path(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A new band reaches a CI author through the subparser description, or it
    reaches them through a failed pipeline."""
    with pytest.raises(SystemExit):
        main(["conformance", "--help"])
    text = " ".join(capsys.readouterr().out.split())
    for code in ("Exits 0", " 3 ", " 13 ", " 64 ", " 66 ", " 74 "):
        assert code in text, f"gnd conformance --help does not mention {code.strip()}"
