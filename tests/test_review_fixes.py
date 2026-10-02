










from __future__ import annotations

import os
import re
import signal
import subprocess
import sys
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest

from gnd import cli, install

SAMPLE_SKILL = "gnd-orm-core"
FIRST_SKILL = "gnd-model-from-text"                                                     

                                                                              
                                                                          
                                                                          
                                                                               
                           
                                                                              
                                                                            
                                                                               
                                                                           
                                                                  
  
                                                                              
                                                                           
                                                            
                                                                               
                                                                   
                                                                               
                                            
  
                                                                                
                                                                              
                                                                         
                                                             
                                                                        
                                                                        
                                                                               
                                                                                
                                                                               
                                                                         
  
                                                                               
                                                                               
                                                                           
                                                                                
                                                              
                                                                             
            



def _target(root: Path, *, scope: str = "project") -> install.InstallTarget:
    return install.InstallTarget(runtime="claude", scope=scope, root=root)


def _install(root: Path, *, mode: str = "copy", force: bool = False) -> install.ApplyResult:
    skills = install.packaged_skills_root()
    target = _target(root)
    manifest = install.read_manifest(root)
    records = install.plan(skills, target, manifest, mode=mode)
    return install.apply(skills, target, records, mode=mode, force=force, manifest=manifest)


def _plant_on_first_call(real: Callable[..., Any], plant: Callable[[], None]) -> Callable[..., Any]:






    state = {"fired": False}

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not state["fired"]:
            state["fired"] = True
            plant()
        return real(*args, **kwargs)

    return wrapper


                                                                             
                                                            
                                                                             


                                                                                 
                                                                              
                                                                               
                      
VICTIM_LEAF = "SKILL.md"


def _toctou_fixture(tmp_path: Path) -> tuple[Path, Path, Callable[[], None]]:







    root = tmp_path / "root"
    outside = tmp_path / "outside"
    outside.mkdir(parents=True)
    victim = outside / VICTIM_LEAF
    victim.write_bytes(b"PRIVATE KEY\n")

    def swap() -> None:
        planted = root / SAMPLE_SKILL
        if planted.is_dir() and not planted.is_symlink():
            for child in sorted(planted.rglob("*"), reverse=True):
                child.unlink() if child.is_file() or child.is_symlink() else child.rmdir()
            planted.rmdir()
        if not planted.exists():
            planted.symlink_to(outside, target_is_directory=True)

    return root, victim, swap


def test_cr01_a_symlink_planted_after_validation_cannot_redirect_a_delete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:








    root, victim, swap = _toctou_fixture(tmp_path)
    _install(root)
    assert (root / SAMPLE_SKILL / VICTIM_LEAF).is_file()

    monkeypatch.setattr(install, "_unlink", _plant_on_first_call(install._unlink, swap))

    raised: BaseException | None = None
    try:
        install.remove(install.packaged_skills_root(), _target(root), install.read_manifest(root))
    except BaseException as error:  # noqa: BLE001 -- the test asserts the refused cleanup error type                                             
        raised = error

    assert victim.is_file() and victim.read_bytes() == b"PRIVATE KEY\n", (
        "a file OUTSIDE the target root was deleted. safe_destination validated "
        "<root>/gnd-orm-core as a real directory in Phase 1; the unlink in Phase 2 "
        "followed a symlink planted at that same path afterwards (CWE-367)."
    )
    assert isinstance(raised, install.InstallPathError | OSError), (
        f"the redirected delete must be refused, not silently skipped; got {raised!r}"
    )


def test_cr01_a_symlink_planted_after_validation_cannot_redirect_a_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:





    root, _victim, swap = _toctou_fixture(tmp_path)
    outside = tmp_path / "outside"
    before = {entry.name for entry in outside.iterdir()}

    monkeypatch.setattr(install, "_atomic_write", _plant_on_first_call(install._atomic_write, swap))

    with pytest.raises((install.InstallPathError, OSError)):
        _install(root)

    after = {entry.name for entry in outside.iterdir()}
    assert after == before, (
        f"files were written OUTSIDE the target root: {sorted(after - before)}. The "
        "write must be anchored to a directory file descriptor opened O_NOFOLLOW, "
        "so a symlink planted after validation raises rather than redirects."
    )


def test_cr01_mutations_are_anchored_to_a_directory_descriptor_on_this_platform() -> None:






    assert install.ANCHORED_MUTATION is True


                                                                             
                                                                            
                                                                        
                                                                    
                                                                             
 
                                                                  
                                                                           
                                                                               
                                                                          
                                                                              
                                                                              
                                                                       
                                                                            
                                                                          
                             


def _depth_changing_root(tmp_path: Path) -> Path:







    deep = tmp_path / "real" / "a" / "b" / "c"
    (deep / "proj").mkdir(parents=True)
    (tmp_path / "alias").symlink_to(deep, target_is_directory=True)
    return tmp_path / "alias" / "proj" / ".claude" / "skills"






































def test_cr02_a_placement_that_lands_nowhere_is_refused_not_reported(
    tmp_path: Path,
) -> None:







    root = tmp_path / "root"
    root.mkdir()
    with pytest.raises(install.InstallError, match="does not resolve"):
        install._place_symlink(root, "gnd-orm-core", tmp_path / "gone", relative=True)


                                                                             
                                                                               
                                                                               
                                                                             

                                                                           
                                                                              
                                                                         
                                                                       
               
VERDICT_BANDS = {0, 1, 2, 3, 4}

FALLBACK = (
    Path(install.__file__).parent
    / "skills"
    / "gnd-model-from-text"
    / "scripts"
    / "validate_model.py"
)
CI_WORKFLOW = Path(__file__).parent.parent / ".github" / "workflows" / "development.yml"


def _run_fallback(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
                                                                            
                                                                             
                                                                              
                                                                              
                                                                            
                                                             
    return subprocess.run(
        [sys.executable, str(FALLBACK), *args], cwd=cwd, capture_output=True, text=True, check=False
    )


@pytest.mark.parametrize(
    ("case", "args"),
    [
        ("no arguments at all", []),
        ("an unknown flag", ["--bogus", "m.orm.yaml"]),
        ("a model file that does not exist", ["does-not-exist.orm.yaml"]),
        ("a model that is not parseable YAML", ["malformed.orm.yaml"]),
        ("a --schema file that is not JSON", ["valid.orm.yaml", "--schema", "notjson.json"]),
    ],
)
def test_cr03_fallback_non_verdict_exits_are_outside_the_bands(
    tmp_path: Path, case: str, args: list[str]
) -> None:
    (tmp_path / "malformed.orm.yaml").write_text("a: [1, 2\n  b: {{{\n")
    (tmp_path / "valid.orm.yaml").write_text("orm: 1\n")
    (tmp_path / "notjson.json").write_text("this is not json at all\n")

    result = _run_fallback(args, tmp_path)

    assert result.returncode not in VERDICT_BANDS, (
        f"{case}: the fallback exited {result.returncode}, which is inside the "
        f"normative verdict bands {sorted(VERDICT_BANDS)}. It is not a verdict; a "
        f"consumer keying on the bands cannot tell it from one (D-22)."
    )
    assert "Traceback" not in result.stderr, (
        f"{case}: the fallback died with a raw traceback rather than a diagnosed "
        f"error.\n{result.stderr}"
    )


def test_cr03_fallback_still_uses_the_bands_for_real_verdicts(tmp_path: Path) -> None:


    (tmp_path / "invalid.orm.yaml").write_text("orm: 1\n")
    assert _run_fallback(["invalid.orm.yaml"], tmp_path).returncode == 1


def test_cr06_fallback_rejects_yaml_aliases_before_loading(tmp_path: Path) -> None:
    model = tmp_path / "aliased.orm.yaml"
    model.write_text(
        "version: 1\nobject_types: &types []\nfact_types: *types\n",
        encoding="utf-8",
    )

    result = _run_fallback([model.name], tmp_path)

    assert result.returncode == 65
    assert "alias" in result.stdout.lower()
    assert "Traceback" not in result.stderr


def test_cr06_fallback_rejects_an_over_budget_yaml_event_stream(tmp_path: Path) -> None:
    model = tmp_path / "event-heavy.orm.yaml"
    model.write_text("- 0\n" * 1_000_001, encoding="utf-8")

    result = _run_fallback([model.name], tmp_path)

    assert result.returncode == 65
    assert "parse-event budget" in result.stdout
    assert "Traceback" not in result.stderr


def test_wr06_ci_actions_are_immutable_and_token_permissions_are_minimal() -> None:
    workflow = CI_WORKFLOW.read_text(encoding="utf-8")
    action_refs = re.findall(r"^\s*-?\s*uses:\s*[^@\s]+@([^\s#]+)", workflow, re.MULTILINE)

    assert action_refs
    assert all(re.fullmatch(r"[0-9a-f]{40}", ref) for ref in action_refs)
    assert re.search(r"^permissions:\n  contents: read$", workflow, re.MULTILINE)


                                                                             
                                                                              
                                                                         
                                                                             

WITHDRAWN = "gnd-orm-core/examples/withdrawn.md"


def _versioned_source(tmp_path: Path, name: str, *, with_withdrawn: bool) -> Path:
    source = tmp_path / name
    (source / "gnd-orm-core").mkdir(parents=True)
    (source / "gnd-orm-core" / "SKILL.md").write_bytes(b"---\nname: gnd-orm-core\n---\n")
    if with_withdrawn:
        (source / "gnd-orm-core" / "examples").mkdir()
        (source / "gnd-orm-core" / "examples" / "withdrawn.md").write_bytes(b"withdrawn\n")
    return source


def _install_from(source: Path, root: Path, *, force: bool = False) -> install.ApplyResult:
    target = _target(root)
    manifest = install.read_manifest(root)
    records = install.plan(source, target, manifest, mode="copy")
    return install.apply(source, target, records, mode="copy", force=force, manifest=manifest)


def test_cr01_install_retains_a_manifest_only_file(tmp_path: Path) -> None:

    v1 = _versioned_source(tmp_path, "v1", with_withdrawn=True)
    v2 = _versioned_source(tmp_path, "v2", with_withdrawn=False)
    root = tmp_path / "root"

    assert _install_from(v1, root).writes == 2
    orphan = root / "gnd-orm-core" / "examples" / "withdrawn.md"
    assert orphan.is_file()

    result = _install_from(v2, root)

    assert orphan.read_bytes() == b"withdrawn\n"
    assert result.pruned == []
    retained = next(record for record in result.skipped if record.relpath == WITHDRAWN)
    assert retained.state == "modified"
    assert "receipt alone cannot prove" in retained.detail


def test_cr04_a_withdrawn_file_the_user_edited_is_never_pruned(tmp_path: Path) -> None:






    v1 = _versioned_source(tmp_path, "v1", with_withdrawn=True)
    v2 = _versioned_source(tmp_path, "v2", with_withdrawn=False)
    root = tmp_path / "root"
    _install_from(v1, root)

    orphan = root / "gnd-orm-core" / "examples" / "withdrawn.md"
    orphan.write_bytes(b"my own notes\n")

    result = _install_from(v2, root)

    assert orphan.read_bytes() == b"my own notes\n", "a user edit was destroyed (D-11)"
    assert result.pruned == []
    assert [record.relpath for record in result.skipped] == [WITHDRAWN]


def test_cr01_forged_receipt_cannot_authorize_deleting_an_unrelated_file(
    tmp_path: Path,
) -> None:
    root = tmp_path / "root"
    _install(root)
    unrelated = root / "my-private-skill" / "notes.md"
    unrelated.parent.mkdir()
    payload = b"these notes were never placed by GND\n"
    unrelated.write_bytes(payload)

    manifest = install.read_manifest(root)
    assert manifest is not None
    manifest.skills["my-private-skill"] = install.ManifestSkill(
        files={"notes.md": install.ManifestFile(sha256=install._sha256(payload), size=len(payload))}
    )

    result = install.remove(install.packaged_skills_root(), _target(root), manifest)

    assert unrelated.read_bytes() == payload
    retained = next(record for record in result.retained if record.relpath == "my-private-skill/notes.md")
    assert retained.state == "modified"
    assert "receipt alone cannot prove" in retained.detail
    assert not result.manifest_removed


                                                                             
                                                                             
                                                                              
                                                                             


@contextmanager
def _deadline(seconds: float, what: str) -> Iterator[None]:


    def _fire(signum: int, frame: object) -> None:
        raise TimeoutError(f"{what} did not return within {seconds}s — it is hanging")

    previous = signal.signal(signal.SIGALRM, _fire)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def test_wr03_a_fifo_at_a_gnd_relpath_is_classified_not_opened(tmp_path: Path) -> None:





    root = tmp_path / "root"
    (root / SAMPLE_SKILL).mkdir(parents=True)
    os.mkfifo(root / SAMPLE_SKILL / "SKILL.md")

    with _deadline(10, "plan() over a FIFO at a GND relpath"):
        records = install.plan(install.packaged_skills_root(), _target(root), None)

    by_relpath = {record.relpath: record for record in records}
    fifo = by_relpath[f"{SAMPLE_SKILL}/SKILL.md"]
    assert fifo.state == "collided"
    assert "non-regular" in fifo.detail


def test_wr03_an_oversized_file_at_a_gnd_relpath_is_capped_not_slurped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:



    monkeypatch.setattr(install, "MAX_CLASSIFY_BYTES", 64)
    root = tmp_path / "root"
    (root / SAMPLE_SKILL).mkdir(parents=True)
    (root / SAMPLE_SKILL / "SKILL.md").write_bytes(b"x" * 4096)

    records = install.plan(install.packaged_skills_root(), _target(root), None)
    oversized = {record.relpath: record for record in records}[f"{SAMPLE_SKILL}/SKILL.md"]
    assert oversized.state == "collided"
    assert "cap" in oversized.detail


                                                                             
                                                                
                                                                             


def test_wr04_an_oversized_receipt_is_refused_before_it_is_parsed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:






    monkeypatch.setattr(install, "MAX_MANIFEST_BYTES", 256)
    tmp_path.mkdir(exist_ok=True)
    (tmp_path / install.MANIFEST_NAME).write_text("[" * 4096)

    with pytest.raises(install.ManifestError, match="cap"):
        install.read_manifest(tmp_path)


def test_wr04_a_normal_receipt_is_far_below_the_cap(tmp_path: Path) -> None:


    _install(tmp_path)
    size = (tmp_path / install.MANIFEST_NAME).stat().st_size
    assert size < install.MAX_MANIFEST_BYTES / 10, (
        f"a real receipt is {size} bytes against a {install.MAX_MANIFEST_BYTES}-byte "
        f"cap; less than 10x headroom is a cap that will fire on a legitimate install"
    )


                                                                             
                                                                              
                                        
                                                                             


def _two_file_source(tmp_path: Path, name: str, body: bytes) -> Path:
    source = tmp_path / name
    (source / "gnd-orm-core").mkdir(parents=True)
    (source / "gnd-orm-core" / "SKILL.md").write_bytes(b"---\nname: gnd-orm-core\n---\n" + body)
    (source / "gnd-orm-core" / "notes.md").write_bytes(b"notes " + body)
    return source


def _crash_upgrading(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:








    v1 = _two_file_source(tmp_path, "v1", b"one\n")
    v2 = _two_file_source(tmp_path, "v2", b"two\n")
    root = tmp_path / "root"
    assert _install_from(v1, root).writes == 2

    real = install._atomic_write

    def _crash(
        root_arg: Path,
        relpath: str,
        data: bytes,
        *,
        expected: install.LeafIdentity | None = None,
    ) -> None:
        if relpath.endswith("notes.md"):
            raise OSError("simulated crash part-way through an upgrade")
        real(root_arg, relpath, data, expected=expected)

    monkeypatch.setattr(install, "_atomic_write", _crash)
    with pytest.raises(OSError):
        _install_from(v2, root)
    monkeypatch.undo()
    return v2, root


def test_wr02_a_crashed_upgrade_is_repairable_by_re_running_install(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    v2, root = _crash_upgrading(tmp_path, monkeypatch)

    receipt = install.read_manifest(root)
    assert receipt is not None and receipt.status != install.STATUS_COMPLETE, (
        "the crash left a receipt claiming a COMPLETE install. The status field "
        "already exists and was write-once; making the crash distinguishable is "
        "what separates GND's own half-written file from a user edit."
    )

    repair = _install_from(v2, root)
    assert repair.writes >= 1, "`gnd install` exited 0 over a half-upgraded tree"

    report = install.diagnose(v2, [_target(root)])
    assert report.targets[0].counts() == {"current": 2}
    assert cli._doctor_outcome(report) == 0
    assert install.read_manifest(root).status == install.STATUS_COMPLETE


def test_wr02_a_crashed_upgrade_is_also_removable_by_uninstall(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:


    v2, root = _crash_upgrading(tmp_path, monkeypatch)

    result = install.remove(v2, _target(root), install.read_manifest(root))

    assert result.retained == [], (
        "uninstall kept GND's own half-written files as though they were user edits"
    )
    assert result.manifest_removed


def test_cr02_interrupted_install_does_not_overwrite_a_third_digest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    v2, root = _crash_upgrading(tmp_path, monkeypatch)
    edited = root / "gnd-orm-core" / "notes.md"
    edited.write_bytes(b"my edit after the interrupted install\n")

    records = install.plan(v2, _target(root), install.read_manifest(root))
    assert {record.relpath: record.state for record in records}[
        "gnd-orm-core/notes.md"
    ] == "modified"

    result = _install_from(v2, root)

    assert edited.read_bytes() == b"my edit after the interrupted install\n"
    assert [record.relpath for record in result.skipped] == ["gnd-orm-core/notes.md"]


def test_cr02_interrupted_uninstall_does_not_delete_a_third_digest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    v2, root = _crash_upgrading(tmp_path, monkeypatch)
    edited = root / "gnd-orm-core" / "notes.md"
    edited.write_bytes(b"my edit after the interrupted install\n")

    result = install.remove(v2, _target(root), install.read_manifest(root))

    assert edited.read_bytes() == b"my edit after the interrupted install\n"
    assert [record.relpath for record in result.retained] == ["gnd-orm-core/notes.md"]
    assert not result.manifest_removed


def _retarget_installed_link(root: Path, tmp_path: Path) -> Path:
    _install(root, mode="symlink")
    link = root / SAMPLE_SKILL
    custom = tmp_path / "custom-skill"
    custom.mkdir()
    (custom / "SKILL.md").write_text("custom\n", encoding="utf-8")
    link.unlink()
    link.symlink_to(custom, target_is_directory=True)
    return link


def test_cr03_install_does_not_replace_a_retargeted_skill_link(tmp_path: Path) -> None:
    root = tmp_path / "root"
    link = _retarget_installed_link(root, tmp_path)
    retargeted_value = os.readlink(link)
    manifest = install.read_manifest(root)
    assert manifest is not None

    records = install.plan(
        install.packaged_skills_root(), _target(root), manifest, mode="symlink"
    )
    result = install.apply(
        install.packaged_skills_root(),
        _target(root),
        records,
        mode="symlink",
        manifest=manifest,
    )

    assert os.readlink(link) == retargeted_value
    retained = next(record for record in result.skipped if record.relpath == SAMPLE_SKILL)
    assert retained.state == "modified"


def test_cr03_uninstall_does_not_remove_a_retargeted_skill_link(tmp_path: Path) -> None:
    root = tmp_path / "root"
    link = _retarget_installed_link(root, tmp_path)
    retargeted_value = os.readlink(link)

    result = install.remove(
        install.packaged_skills_root(), _target(root), install.read_manifest(root)
    )

    assert link.is_symlink()
    assert os.readlink(link) == retargeted_value
    retained = next(record for record in result.retained if record.relpath == SAMPLE_SKILL)
    assert retained.state == "modified"
    assert not result.manifest_removed


def test_cr04_apply_revalidates_a_leaf_immediately_before_replacement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    v1 = _two_file_source(tmp_path, "v1", b"one\n")
    v2 = _two_file_source(tmp_path, "v2", b"two\n")
    root = tmp_path / "root"
    _install_from(v1, root)
    manifest = install.read_manifest(root)
    records = install.plan(v2, _target(root), manifest)
    victim = root / "gnd-orm-core" / "SKILL.md"
    edit = b"user edit after plan\n"

    real = install._atomic_write
    monkeypatch.setattr(
        install,
        "_atomic_write",
        _plant_on_first_call(real, lambda: victim.write_bytes(edit)),
    )

    with pytest.raises(install.InstallError, match="changed after planning"):
        install.apply(v2, _target(root), records, manifest=manifest)

    assert victim.read_bytes() == edit


def test_cr04_remove_restores_a_leaf_changed_after_planning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = _two_file_source(tmp_path, "source", b"one\n")
    root = tmp_path / "root"
    _install_from(source, root)
    victim = root / "gnd-orm-core" / "SKILL.md"
    edit = b"user edit after plan\n"

    real = install._unlink
    monkeypatch.setattr(
        install,
        "_unlink",
        _plant_on_first_call(real, lambda: victim.write_bytes(edit)),
    )

    with pytest.raises(install.InstallError, match="restored it instead of deleting"):
        install.remove(source, _target(root), install.read_manifest(root))

    assert victim.read_bytes() == edit


def test_wr02_a_genuine_user_edit_is_still_untouchable(tmp_path: Path) -> None:






    v1 = _two_file_source(tmp_path, "v1", b"one\n")
    root = tmp_path / "root"
    _install_from(v1, root)
    edited = root / "gnd-orm-core" / "notes.md"
    edited.write_bytes(b"my own notes\n")

    records = install.plan(v1, _target(root), install.read_manifest(root))
    assert {r.relpath: r.state for r in records}["gnd-orm-core/notes.md"] == "modified"

    _install_from(v1, root)
    assert edited.read_bytes() == b"my own notes\n"
    assert install.remove(v1, _target(root), install.read_manifest(root)).retained != []
    assert edited.read_bytes() == b"my own notes\n"


def test_wr02_a_clean_no_op_run_writes_no_in_progress_receipt(tmp_path: Path) -> None:


    v1 = _two_file_source(tmp_path, "v1", b"one\n")
    root = tmp_path / "root"
    _install_from(v1, root)
    before = (root / install.MANIFEST_NAME).read_bytes()

    second = _install_from(v1, root)

    assert (second.writes, second.manifest_written) == (0, False)
    assert (root / install.MANIFEST_NAME).read_bytes() == before


                                                                             
                                                                           
                                                                             


def test_wr05_a_run_that_placed_nothing_is_not_headlined_as_current(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:





    source = _two_file_source(tmp_path, "v1", b"one\n")
    root = tmp_path / "root"
    (root / SAMPLE_SKILL).mkdir(parents=True)
    for name in ("SKILL.md", "notes.md"):
        (root / SAMPLE_SKILL / name).write_bytes(b"not mine\n")

    result = _install_from(source, root)
    assert result.writes == 0
    cli._render_target_result(_target(root), result)
    headline = capsys.readouterr().out.splitlines()[1]

    assert result.collisions
    assert "already current" not in headline, (
        f"headline {headline!r} claims currency over a run that placed nothing "
        f"because {len(result.collisions)} path(s) collided"
    )
    assert "nothing placed" in headline


def test_wr05_a_genuine_no_op_still_says_already_current(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:

    _install(tmp_path)
    result = _install(tmp_path)
    cli._render_target_result(_target(tmp_path), result)
    assert "already current (0 writes)" in capsys.readouterr().out


                                                                             
                                                                            
                                            
                                                                             


def test_wr06_placed_files_are_readable_like_the_files_they_copy(tmp_path: Path) -> None:




    _install(tmp_path)
    expected = 0o644 & ~_umask()
    for path in (tmp_path / SAMPLE_SKILL / "SKILL.md", tmp_path / install.MANIFEST_NAME):
        mode = path.stat().st_mode & 0o777
        assert mode == expected, (
            f"{path.name} is mode {mode:#o}, expected {expected:#o} — the packaged "
            f"file it copies is 0o644 and the directories around it are 0o755"
        )


def _umask() -> int:
    current = os.umask(0o022)
    os.umask(current)
    return current


                                                                             
                                                                         
                          
                                                                             


def test_wr07_a_version_bump_rewrites_the_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:



    _install(tmp_path)
    placed_at = install.read_manifest(tmp_path).installed_at

    monkeypatch.setattr(install, "resolve_version", lambda: "9.9.9")
    result = _install(tmp_path)

    assert result.writes == 0, "a version bump must not rewrite any skill file"
    assert result.manifest_written, "the receipt still claims the previous version"
    receipt = install.read_manifest(tmp_path)
    assert receipt.version == "9.9.9"
    assert receipt.installed_at == placed_at, (
        "installed_at means 'when the recorded CONTENT was last placed' — the "
        "content did not move, so restamping it would make that docstring false"
    )


def test_wr07_an_unchanged_version_still_leaves_the_receipt_alone(tmp_path: Path) -> None:

    _install(tmp_path)
    before = (tmp_path / install.MANIFEST_NAME).read_bytes()
    assert _install(tmp_path).manifest_written is False
    assert (tmp_path / install.MANIFEST_NAME).read_bytes() == before


                                                                             
                                                                               
                                                                             
                                                                             


def test_wr01_a_receiptless_symlink_root_is_diagnosed_at_link_granularity(
    tmp_path: Path,
) -> None:













    source = _versioned_source(tmp_path, "src", with_withdrawn=True)
    root = tmp_path / "root"
    root.mkdir()
    (root / "gnd-orm-core").symlink_to(source / "gnd-orm-core", target_is_directory=True)

    report = install.diagnose(source, [_target(root)])
    diagnosis = report.targets[0]

    assert diagnosis.counts() == {"collided": 1}, (
        f"a receipt-less root placed as symlinks reported {diagnosis.counts()}; the "
        f"artifact placed there is ONE link, not two files behind it"
    )
    assert diagnosis.states[0].relpath == "gnd-orm-core"
    assert "symlink" in diagnosis.states[0].detail


def test_wr01_a_receiptless_copy_root_is_still_diagnosed_per_file(tmp_path: Path) -> None:


    source = _versioned_source(tmp_path, "src", with_withdrawn=True)
    root = tmp_path / "root"
    (root / "gnd-orm-core" / "examples").mkdir(parents=True)
    (root / "gnd-orm-core" / "SKILL.md").write_bytes(b"---\nname: gnd-orm-core\n---\n")
    (root / "gnd-orm-core" / "examples" / "withdrawn.md").write_bytes(b"withdrawn\n")

    report = install.diagnose(source, [_target(root)])
    assert report.targets[0].counts() == {"collided": 2}
