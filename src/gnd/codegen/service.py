from __future__ import annotations

import os
from pathlib import Path

from gnd import safefs as install_module
from gnd.exits import EXIT_COLLISION, EXIT_INTERNAL, EXIT_IO
from gnd.model import ModelValidationError, ValidationIssue, load_model
from gnd.output import _print_issues


def _stale_smoke_modules(root_fd: int | None, project: object) -> frozenset[str]:
    """Smoke-pattern basenames in the project root that this model does not emit.

    One directory listing, no recursion: the emitted smoke module is always at
    the project root, so a match deeper in the tree belongs to the user's own
    layout and is none of codegen's business (v5.1 D-P1.8).
    """
    from fnmatch import fnmatch

    from gnd.codegen.emit import smoke_module_pattern

    if root_fd is None:
        return frozenset()
    emitted = {
        file.relpath
        for file in project.files  # type: ignore[attr-defined]
        if fnmatch(file.relpath, smoke_module_pattern())
    }
    try:
        present = os.listdir(root_fd)
    except OSError:
        return frozenset()
    return frozenset(
        name for name in present if fnmatch(name, smoke_module_pattern()) and name not in emitted
    )

def _cmd_codegen(model_path: str, out_dir: str, *, force: bool = False) -> int:
    """``gnd codegen MODEL --out DIR [--force]`` — the model becomes a project.

    GEN-01's emitter. The generated project has the GND shape (G-01): tools
    derived from the model's fact types, a code-emitted ``SKILL.md`` the terminal
    agent runs, and the shipped ``gnd verify`` as its verifier half — so it is
    CI-runnable with zero network and no API key. Everything here is an offline
    function of ``model.orm.yaml``.

    **Two write paths, and the split is deliberate.** A FRESH target (absent or
    empty, with no codegen manifest) is published by ``write_project``: the whole
    tree is staged, fsynced, and swapped in with one ``os.replace``, so a crash
    leaves nothing at all — strictly stronger than ordering. An EXISTING codegen
    project goes through the six-state classifier in :mod:`gnd.codegen.plan`,
    which writes per file and the manifest LAST, because it must preserve the
    extension files a whole-tree replace would destroy.

    Bands, and why each is the one it is:

    * ``0`` — the tree was written, or was already current (a second run over an
      unchanged model performs zero writes — G-06).
    * ``3`` — the model failed to load, two of its ids sanitize to one Python
      symbol, or the existing manifest is unreadable. The second is the ONE case
      where codegen refuses a model ``gnd validate`` accepted, and 3 is right
      because the remedy is in the model: rename one id.
    * ``11`` — a write or adoption was REFUSED and nothing was destroyed: a
      hand-edited derived file; an unmanaged regular, symlink, or non-regular
      occupant at a derived path; an occupied directory without a codegen
      manifest; an unrecorded regular extension before explicit ``--force``
      adoption; or a recorded or unrecorded extension path occupied by a
      symlink, directory, FIFO, or over-cap leaf. Re-run with ``--force`` only
      for hand-edited or unmanaged regular/symlink derived paths and unrecorded
      regular-extension adoption; remove or move unsafe occupants by hand.
      Also: a smoke-pattern module at the project root that this model does not
      emit (v5.1 D-P1.8). That scan is provenance-blind and ``--force`` does not
      override it — the remedy is to delete the named file, because renaming a
      create-once module would overwrite bytes regeneration must never touch.
      This is not a new allocation or claim: 11 retains its refusal meaning,
      while recorded authored regular extension divergence is an informational
      create-once skip at exit 0, not band 11.
    * ``64`` — usage (argparse).
    * ``70`` — an emitter invariant broke: the projection gate refused GND's own
      schema, an emitted module did not parse, the default template imported a
      provider, or the generated skill's frontmatter would not read back. All
      four are breaches by GND's emitter over a model that already loaded clean,
      so they follow the ``ProjectionGateError`` precedent rather than band 3.
    * ``74`` — the output path was refused by the traversal guard, or unwritable.
    """
    from gnd.codegen.emit import (
        EmitGateError,
        ProjectExistsError,
        SkillNameError,
        emit_project,
        write_project,
    )
    from gnd.codegen.identifiers import IdentifierError
    from gnd.codegen.manifest import (
        CodegenManifestError,
        build_manifest,
        render_manifest,
    )
    from gnd.codegen.plan import (
        _assert_root_path_bound,
        _bind_codegen_parent,
        _open_codegen_root,
        _read_manifest_at,
        apply_codegen,
        plan_codegen,
    )
    from gnd.extract.projection import ProjectionGateError

    try:
        model = load_model(model_path)
        from gnd.terms import require_non_temporal

        require_non_temporal(model, "codegen")
        if model.reference_populations:
            raise ModelValidationError(
                [
                    ValidationIssue(
                        path="$",
                        message="codegen does not support reference populations",
                        rule_id="reference:consumer-unsupported",
                    )
                ]
            )
    except ModelValidationError as error:
        for warning in error.warnings:
            print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")
        _print_issues(error.issues)
        return 3
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"ERROR: {error}")
        return 3

    try:
        project = emit_project(
            model,
            model_path,
            skill_name=Path(out_dir).resolve(strict=False).name,
        )
    except SkillNameError as error:
        print(f"ERROR: invalid generated skill directory: {error}")
        return EXIT_IO
    except IdentifierError as error:
        print(f"ERROR: {error}")
        return 3
    except (EmitGateError, ProjectionGateError) as error:
        print(f"INTERNAL ERROR: {error}")
        return EXIT_INTERNAL

    root = Path(out_dir)
    manifest = None
    root_fd = None
    try:
        parent_path, root_parts, parent_fd = _bind_codegen_parent(root)
    except install_module.InstallPathError as error:
        print(f"ERROR: refused output path: {error}")
        return EXIT_IO
    try:
        root_fd = _open_codegen_root(root)
    except FileNotFoundError:
        occupied = False
    except install_module.InstallPathError as error:
        os.close(parent_fd)
        print(f"ERROR: refused output path: {error}")
        return EXIT_IO
    else:
        try:
            manifest, _manifest_identity = _read_manifest_at(root_fd, root)
            occupied = bool(os.listdir(root_fd))
        except CodegenManifestError as error:
            os.close(root_fd)
            os.close(parent_fd)
            print(f"ERROR: {error}")
            return 3
        except OSError as error:
            os.close(root_fd)
            os.close(parent_fd)
            print(f"ERROR: could not inspect output directory {root}: {error}")
            return EXIT_IO
    try:
        _assert_root_path_bound(parent_path, parent_fd)
    except install_module.InstallPathError as error:
        if root_fd is not None:
            os.close(root_fd)
        os.close(parent_fd)
        print(f"ERROR: refused output path: {error}")
        return EXIT_IO
    if manifest is None and not occupied:
        # The FRESH path — plan 03's atomic whole-tree publication, with the
        # manifest staged last and the tree renamed below the retained parent.
        try:
            write_project(
                project,
                out_dir,
                manifest_text=render_manifest(build_manifest(project, model_path)),
                parent_fd=parent_fd,
                parent_path=parent_path,
                root_parts=root_parts,
                root_fd=root_fd,
            )
        except ProjectExistsError as error:
            print(f"ERROR: {error}")
            return EXIT_COLLISION
        except SkillNameError as error:
            print(f"ERROR: invalid generated skill directory: {error}")
            return EXIT_IO
        except install_module.InstallPathError as error:
            print(f"ERROR: refused output path: {error}")
            return EXIT_IO
        except OSError as error:
            print(f"ERROR: could not write the project under {out_dir}: {error}")
            return EXIT_IO
        finally:
            if root_fd is not None:
                os.close(root_fd)
            os.close(parent_fd)
        print(f"generated project for {model_path} -> {root}")
        for file in project.files:
            print(f"  {file.relpath} [{file.ownership}] created")
        return 0

    if manifest is None and not force:
        # Plan 03's shipped refusal, preserved rather than quietly relaxed by
        # the arrival of the classifier: a directory holding work GND never
        # placed is not a codegen project, and merging into it is a bigger
        # promise than "regenerate". `--force` adopts it, and even then only the
        # PLANNED relpaths are ever touched.
        if root_fd is not None:
            os.close(root_fd)
        os.close(parent_fd)
        print(
            f"ERROR: {root} is not empty and carries no codegen manifest, so "
            f"gnd codegen refuses rather than writing into it. Nothing was "
            f"destroyed. Re-run with --force to adopt the occupied paths GND "
            f"would own; files at any other path are never touched."
        )
        return EXIT_COLLISION

    emitted_smoke = ", ".join(
        sorted(
            file.relpath
            for file in project.files
            if file.relpath.startswith("test_architecture_smoke_")
        )
    )
    stale_smoke = _stale_smoke_modules(root_fd, project)
    if stale_smoke:
        # v5.1 D-P1.8: detect, decide, THEN write (standing rule 3). The scan is
        # provenance-blind — a smoke-pattern basename that is not the one this
        # model emits is refused whether GND wrote it or a hand did, because
        # adopting it would claim a file codegen did not create and leaving it
        # puts an orphan beside a live module no reader can tell apart.
        if root_fd is not None:
            os.close(root_fd)
        os.close(parent_fd)
        listed = ", ".join(sorted(stale_smoke))
        print(
            f"ERROR: {root} carries a smoke module this model does not emit: "
            f"{listed}. This model's smoke module is {emitted_smoke}. Delete "
            f"the file(s) named above and re-run; gnd codegen refuses rather "
            f"than adopting or renaming a create-once file. Nothing was "
            f"destroyed, and --force does not override this."
        )
        return EXIT_COLLISION

    os.close(parent_fd)
    try:
        assert root_fd is not None
        plan = plan_codegen(project, out_dir, manifest, root_fd=root_fd)
        result = apply_codegen(project, out_dir, plan, force=force, root_fd=root_fd)
    except CodegenManifestError as error:
        print(f"ERROR: {error}")
        return 3
    except install_module.InstallPathError as error:
        print(f"ERROR: refused output path: {error}")
        return EXIT_IO
    except install_module.InstallError as error:
        print(f"ERROR: refused manifest update: {error}. Nothing was destroyed.")
        return EXIT_COLLISION
    except OSError as error:
        print(f"ERROR: could not write the project under {out_dir}: {error}")
        return EXIT_IO
    finally:
        if root_fd is not None:
            os.close(root_fd)

    states = plan.by_relpath()
    apply_states = {record.relpath: record for record in result.skipped}
    print(f"generated project for {model_path} -> {root}")
    for file in project.files:
        state = apply_states.get(file.relpath, states[file.relpath])
        verb = "written" if file.relpath in result.written else f"skipped ({state.state})"
        print(f"  {file.relpath} [{file.ownership}] {verb}")
    print(f"{result.writes} written, {len(result.skipped)} skipped")
    for orphan in result.orphans:
        print(f"  NOTE: {orphan} is recorded but no longer emitted; left in place")
    for relpath in result.extension_skips:
        print(f"NOTE: preserved authored extension {relpath}; left unchanged")
    if result.collisions:
        force_remediable = [
            detail for detail in result.collision_details if detail.remediation == "force"
        ]
        manual_removal = [
            detail for detail in result.collision_details if detail.remediation == "remove"
        ]
        if force_remediable:
            print("ERROR: force-remediable refusals:")
            for detail in force_remediable:
                print(f"  {detail.relpath} — {detail.detail}")
            print(
                "Re-run with --force to overwrite the derived paths or adopt the "
                "regular unmanaged extension paths listed above."
            )
        if manual_removal:
            print("ERROR: unsafe occupants requiring manual removal:")
            for detail in manual_removal:
                print(f"  {detail.relpath} — {detail.detail}")
            print(
                "Remove or move the unsafe occupants listed above by hand; --force "
                "will not replace them."
            )
        print("Nothing was destroyed.")
        return EXIT_COLLISION
    return 0

_stale_smoke_modules.__module__ = "gnd.cli"
_cmd_codegen.__module__ = "gnd.cli"
