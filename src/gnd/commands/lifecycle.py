from __future__ import annotations

import argparse
from pathlib import Path

from gnd import install as install_module
from gnd.exits import EXIT_COLLISION, EXIT_DRIFT, EXIT_IO, EXIT_NO_INSTALL


def _add_target_arguments(parser: argparse.ArgumentParser) -> None:
    """D-08's target flag surface, defined once.

    ``install`` uses it now; ``doctor`` and ``uninstall`` (plan 01.2-04) use the
    same helper, so three commands cannot drift in how they resolve a target —
    the sibling of ``_add_format_argument``'s reason for existing.

    ``--global`` cannot use argparse's derived attribute name: ``global`` is a
    Python keyword, so ``args.global`` is a syntax error. Both scope flags
    therefore store a constant into an explicitly named ``scope`` destination.
    """
    parser.add_argument(
        "--claude",
        action="store_true",
        help="target Claude Code's skills directory (default: both runtimes)",
    )
    parser.add_argument(
        "--codex",
        action="store_true",
        help="target Codex CLI's skills directory (default: both runtimes)",
    )
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument(
        "--global",
        dest="scope",
        action="store_const",
        const="global",
        help="user level (DEFAULT): ~/.claude/skills and $CODEX_HOME/skills (~/.codex/skills)",
    )
    scope.add_argument(
        "--project",
        dest="scope",
        action="store_const",
        const="project",
        help="this project: ./.claude/skills and ./.codex/skills",
    )
    parser.set_defaults(scope="global")

def _install_outcome(io_failures: list[str], collisions: list[str]) -> int:
    """Lifecycle outcomes -> exit code. One decision function, like ``_band()``.

    Precedence: an I/O failure outranks a collision, because a target that could
    not be read or written says nothing at all about what is in it, while a
    collision is a complete and accurate report.

    ``install`` never returns :data:`EXIT_DRIFT`: drift is what install *repairs*,
    and reporting it is ``doctor``'s job (plan 01.2-04).
    """
    if io_failures:
        return EXIT_IO
    if collisions:
        return EXIT_COLLISION
    return 0

def _doctor_outcome(report: install_module.DoctorReport) -> int:
    """Diagnosis -> exit code. One decision function, like ``_band()``.

    Precedence **12 > 11 > 10 > 0**:

    - 12 first, because "nothing is installed anywhere" makes every other
      question moot; reporting drift over an install that does not exist sends
      the user to repair a directory they never wrote.
    - 11 next: a collision means a file GND does not own is sitting where GND
      would place one. Nothing was destroyed, and the repair (``--force``, or
      moving the file aside) differs from the repair for drift (``install``).
    - 10 last: stale, missing, modified — and an untrusted receipt, which is
      folded in here rather than given a code of its own, because the user's
      next action is the same either way: look, then re-install.

    :data:`EXIT_DRIFT` is declared in this module by plan 01.2-02 and returned
    by nothing until here — install *repairs* drift, so drift was never an
    install outcome.
    """
    if not report.installed_anywhere():
        return EXIT_NO_INSTALL
    if report.has_collision():
        return EXIT_COLLISION
    if report.has_drift():
        return EXIT_DRIFT
    return 0

def _render_states(states: list[install_module.SkillFileState]) -> None:
    """Per-file detail, capped exactly as the population loader caps its issue
    summary: a five-target run over 29 files each would otherwise bury the
    headline, and a report nobody can read is not a report."""
    interesting = [record for record in states if record.state != "current"]
    shown = interesting[: install_module.MAX_REPORTED_STATES]
    for record in shown:
        detail = f": {record.detail}" if record.detail else ""
        print(f"  [{record.state}] {record.relpath}{detail}")
    if len(interesting) > len(shown):
        print(
            f"  ... and {len(interesting) - len(shown)} further record(s) elided "
            f"(cap {install_module.MAX_REPORTED_STATES})"
        )

def _render_diagnosis(diagnosis: install_module.TargetDiagnosis) -> None:
    print(f"{diagnosis.target.label()} -> {diagnosis.target.root}")
    if diagnosis.problem:
        print(f"  REFUSED: {diagnosis.problem}")
        print("  Nothing was inferred from it. No state is reported for this root.")
    elif not diagnosis.installed:
        print("  not installed")
    else:
        counts = diagnosis.counts()
        summary = ", ".join(f"{state}={counts[state]}" for state in sorted(counts)) or "no assets"
        provenance = f"{diagnosis.mode} mode" if diagnosis.mode else "no receipt (partial install)"
        version = (
            f", {install_module.DISTRIBUTION} {diagnosis.version}" if diagnosis.version else ""
        )
        stamp = f", placed {diagnosis.installed_at}" if diagnosis.installed_at else ""
        print(f"  installed ({provenance}{version}{stamp}): {summary}")
        _render_states(diagnosis.states)
    if diagnosis.alternative_root is not None:
        print(
            f"  note: {diagnosis.alternative_root} is a known alternative Codex skills "
            f"location that GND does not write (the published docs and the shipped "
            f"binary disagree; both roots were observed live)"
        )

def _cmd_doctor(*, claude: bool, codex: bool) -> int:
    """Report the state of every placed asset, at BOTH scopes (PKG-07).

    The scope flags are accepted through the shared helper and deliberately not
    honoured for resolution: runtime skill precedence puts the user level ahead
    of the project level, so a user who installs into a project and sees no
    effect is usually being shadowed by an earlier user-level install. A doctor
    that inspected only the scope it was pointed at could not see that.

    Text-only by D-25.
    """
    project = Path.cwd()
    runtimes = [name for name, on in (("claude", claude), ("codex", codex)) if on]
    runtimes = runtimes or list(install_module.RUNTIMES)

    try:
        skills_root = install_module.packaged_skills_root()
    except install_module.InstallError as error:
        print(f"ERROR: {error}")
        return EXIT_IO

    targets = [
        target
        for scope in install_module.SCOPES
        for target in install_module.resolve_targets(runtimes, scope, project)
    ]
    report = install_module.diagnose(skills_root, targets)

    verdict = "on PATH" if report.executable_on_path else "NOT on PATH"
    print(f"executable directory: {report.executable_dir} ({verdict})")
    if not report.executable_on_path:
        print(
            "  a successful install whose bin directory is not on PATH presents as "
            "`gnd: command not found`. Fix it with `uv tool update-shell`, then open "
            "a new shell."
        )
    print(
        "checking both scopes regardless of the flags given (skill precedence is "
        "user level over project level)"
    )

    for diagnosis in report.targets:
        _render_diagnosis(diagnosis)

    for row in report.shadowing:
        print(
            f"SHADOWING: the {row.runtime} user-scope install of '{row.skill}' at "
            f"{row.shadowing_root} takes precedence over the project-scope one at "
            f"{row.shadowed_root} — edits to the project copy will appear to do nothing."
        )

    outcome = _doctor_outcome(report)
    if outcome == EXIT_NO_INSTALL:
        print("no GND install manifest found at any resolved target root (listed above).")
    return outcome

def _uninstall_outcome(io_failures: list[str], retained: list[str], installed: bool) -> int:
    """Removal outcome -> exit code. Sibling of ``_doctor_outcome``.

    Precedence: an I/O-class refusal outranks everything, then "nothing was
    installed", then "something GND-owned was left behind".

    A receipt this build could not trust — an unrecognised schema, or an entry
    the traversal guard refused — returns :data:`EXIT_IO` rather than
    :data:`EXIT_DRIFT`. 74 already means "an unreadable install receipt, or a path
    refused by the traversal guard" in this module's own docstring, and the
    distinction is load-bearing: 10 says "files were retained after a removal ran",
    while a refusal means no removal was attempted at all. Reporting the first as
    the second would tell a script that the uninstall happened.
    """
    if io_failures:
        return EXIT_IO
    if not installed:
        return EXIT_NO_INSTALL
    if retained:
        return EXIT_DRIFT
    return 0

def _cmd_uninstall(*, claude: bool, codex: bool, scope: str) -> int:
    """Remove GND's placed skills from every requested target root (PKG-07).

    Unlike ``doctor``, this honours the scope flags exactly as given: ``doctor``
    inspects both scopes because it only reports, and a command that DELETES must
    touch nothing the user did not point it at.

    Text-only by D-25.
    """
    project = Path.cwd()
    runtimes = [name for name, on in (("claude", claude), ("codex", codex)) if on]

    try:
        skills_root = install_module.packaged_skills_root()
    except install_module.InstallError as error:
        print(f"ERROR: {error}")
        return EXIT_IO

    candidates = install_module.resolve_targets(
        runtimes or list(install_module.RUNTIMES), scope, project
    )

    io_failures: list[str] = []
    retained: list[str] = []
    installed = False
    for target in candidates:
        try:
            manifest = install_module.read_manifest(target.root)
        except install_module.InstallPathError as error:
            print(f"REFUSED at {target.root}: {error}")
            print("  Nothing was deleted at this root, or anywhere else.")
            io_failures.append(str(target.root))
            continue
        except install_module.InstallError as error:
            print(f"REFUSED at {target.root}: {error}")
            io_failures.append(str(target.root))
            continue
        if manifest is None:
            print(f"{target.label()} -> {target.root}\n  not installed")
            continue
        installed = True

        try:
            result = install_module.remove(skills_root, target, manifest)
        except install_module.InstallPathError as error:
            print(f"REFUSED at {target.root}: {error}")
            print("  The refusal is total: nothing was deleted at this root.")
            io_failures.append(str(target.root))
            continue
        except (install_module.InstallError, OSError) as error:
            print(f"ERROR at {target.root}: {error}")
            io_failures.append(str(target.root))
            continue

        print(f"{target.label()} -> {target.root}")
        print(
            f"  removed {len(result.removed)} artifact(s), pruned "
            f"{len(result.pruned)} director(y/ies)"
            + (", removed the install receipt" if result.manifest_removed else "")
        )
        if result.retained:
            retained.extend(f"{target.root}/{record.relpath}" for record in result.retained)
            _render_states(result.retained)
            print(
                f"  {len(result.retained)} file(s) were kept: GND only deletes files whose "
                f"bytes still match what it placed. Remove them yourself if you want them "
                f"gone. The install receipt was kept with them."
            )

    if not installed and not io_failures:
        print("no GND install manifest found at any resolved target root:")
        for target in candidates:
            print(f"  {target.label()}: {target.root}")

    return _uninstall_outcome(io_failures, retained, installed)

def _render_target_result(
    target: install_module.InstallTarget,
    result: install_module.ApplyResult,
) -> None:
    print(f"{target.label()} -> {target.root}")
    # WR-05: the headline used to be chosen on `writes` alone, so "already
    # current (0 writes)" fired for runs that wrote nothing BECAUSE everything
    # collided or was modified — a success line two rows above its own
    # contradiction. Currency is a claim about the tree, not about the counter.
    if result.writes:
        print(f"  placed {result.writes} file(s)")
    elif result.skipped or result.collisions:
        print(f"  nothing placed ({len(result.skipped)} record(s) not acted on, see below)")
    else:
        print("  already current (0 writes)")
    if result.pruned:
        print(
            f"  removed {len(result.pruned)} file(s) this version no longer ships "
            f"(bytes still matched what GND placed): {', '.join(result.pruned)}"
        )
    if not result.skipped:
        return
    shown = result.skipped[: install_module.MAX_REPORTED_STATES]
    for record in shown:
        print(f"  [{record.state}] {record.relpath}: {record.detail}")
    if len(result.skipped) > len(shown):
        print(
            f"  ... and {len(result.skipped) - len(shown)} further record(s) elided "
            f"(cap {install_module.MAX_REPORTED_STATES})"
        )

def _cmd_install(
    *,
    claude: bool,
    codex: bool,
    scope: str,
    force: bool,
    symlink: bool,
    sync: bool,
) -> int:
    """Place every packaged skill into every requested target root (PKG-02).

    Text-only by D-25 — see the subcommand's help text for why that is a decision
    rather than an omission.
    """
    project = Path.cwd()
    mode = "symlink" if symlink else "copy"

    try:
        skills_root = install_module.packaged_skills_root()
    except install_module.InstallError as error:
        print(f"ERROR: {error}")
        return EXIT_IO

    if sync:
        candidates = install_module.standard_targets(project)
    else:
        runtimes = [name for name, on in (("claude", claude), ("codex", codex)) if on]
        candidates = install_module.resolve_targets(
            runtimes or list(install_module.RUNTIMES), scope, project
        )

    io_failures: list[str] = []
    collisions: list[str] = []
    # This pass answers ONE question — which candidate roots `--sync` has
    # anything to sync — and reports a root whose receipt cannot be read. The
    # manifest it reads is deliberately discarded: see the re-read below.
    targets: list[install_module.InstallTarget] = []
    for target in candidates:
        try:
            manifest = install_module.read_manifest(target.root)
        except install_module.InstallError as error:
            print(f"ERROR at {target.root}: {error}")
            io_failures.append(str(target.root))
            continue
        if sync and manifest is None:
            continue
        targets.append(target)

    if sync and not targets and not io_failures:
        # D-10's self-locating property has nothing to locate. Saying WHICH roots
        # were examined is the difference between a diagnosable answer and a
        # mystery, since there is deliberately no central registry to inspect.
        print("no GND install manifest found at any standard target root:")
        for target in candidates:
            print(f"  {target.label()}: {target.root}")
        return EXIT_NO_INSTALL

    for target in targets:
        # F-01: read the receipt HERE, immediately before this target is planned
        # and applied — never once for every target up front. Two requested
        # targets can resolve to ONE physical directory (a user symlinking
        # `.codex/skills -> ../.claude/skills` is a reasonable response to D-21's
        # unresolved Codex-root question), in which case the first target's apply
        # writes the very receipt the second target must read. Carrying a stale
        # `manifest=None` across that write made the second pass plan all 29
        # files as `collided`, report "GND did not place it" about files GND had
        # placed milliseconds earlier in the same command, and overwrite a
        # receipt owning 29 real files with an empty one.
        #
        # Re-reading was chosen over detecting the aliasing (comparing each
        # resolved root's st_dev/st_ino) because it fixes the general defect
        # rather than one instance of it: apply()'s contract is that `manifest`
        # describes the root as it is NOW, and any writer between the two reads —
        # a sibling target, a concurrent `gnd install`, the user — falsifies a
        # value cached before the write. An st_dev/st_ino check would make these
        # two targets agree while leaving that contract broken everywhere else.
        try:
            manifest = install_module.read_manifest(target.root)
        except install_module.InstallError as error:
            print(f"ERROR at {target.root}: {error}")
            io_failures.append(str(target.root))
            continue
        effective_mode = manifest.mode if (sync and manifest is not None) else mode
        if manifest is not None and manifest.mode != effective_mode:
            # Two shapes at one root is not a state this installer will produce:
            # copy files sitting beneath a symlinked skill directory would be
            # written THROUGH the link, into the distribution itself.
            print(
                f"{target.label()} -> {target.root}\n"
                f"  BLOCKED: this root was installed in {manifest.mode!r} mode and you "
                f"asked for {effective_mode!r}. Nothing was changed. Re-run in "
                f"{manifest.mode!r} mode, or remove the root and install again."
            )
            collisions.append(str(target.root))
            continue
        try:
            records = install_module.plan(skills_root, target, manifest, mode=effective_mode)
            result = install_module.apply(
                skills_root,
                target,
                records,
                mode=effective_mode,
                force=force,
                manifest=manifest,
            )
        except install_module.InstallPathError as error:
            print(f"REFUSED at {target.root}: {error}")
            io_failures.append(str(target.root))
            continue
        except (install_module.InstallError, OSError) as error:
            print(f"ERROR at {target.root}: {error}")
            io_failures.append(str(target.root))
            continue

        _render_target_result(target, result)
        if result.collisions:
            collisions.extend(f"{target.root}/{rel}" for rel in result.collisions)
            print(
                f"  {len(result.collisions)} unmanaged file(s) blocked a write. Nothing "
                f"was destroyed — re-run with --force to replace them."
            )

    return _install_outcome(io_failures, collisions)

_add_target_arguments.__module__ = "gnd.cli"
_install_outcome.__module__ = "gnd.cli"
_doctor_outcome.__module__ = "gnd.cli"
_render_states.__module__ = "gnd.cli"
_render_diagnosis.__module__ = "gnd.cli"
_cmd_doctor.__module__ = "gnd.cli"
_uninstall_outcome.__module__ = "gnd.cli"
_cmd_uninstall.__module__ = "gnd.cli"
_render_target_result.__module__ = "gnd.cli"
_cmd_install.__module__ = "gnd.cli"




def _register_install(subparsers):
    install_parser = subparsers.add_parser(
        "install",
        help="place every packaged GND skill into your agent runtime's skills directory",
        description=(
            "Place every packaged GND skill into your agent runtime's skills "
            "directory. Copies by default; a second run with no intervening change "
            "performs zero writes, and a file GND did not place is never overwritten "
            "without --force. Text output only: --format json exists so a retry loop "
            "can consume VERIFIER output, and this is a human-operated setup command "
            "with no programmatic consumer, so a machine-readable install report is "
            "deliberately not offered (D-25)."
        ),
    )
    _add_target_arguments(install_parser)
    install_parser.add_argument(
        "--symlink",
        action="store_true",
        help=(
            "link skill directories instead of copying — DEVELOPMENT INSTALLS ONLY. "
            "A tool environment is rebuilt on upgrade and removed on uninstall, so a "
            "link into one is silently swapped after a same-interpreter reinstall and "
            "dangles outright after an interpreter-version change or an uninstall"
        ),
    )
    install_parser.add_argument(
        "--force",
        action="store_true",
        help="replace unmanaged files that block a write (never touches files you edited)",
    )
    install_parser.add_argument(
        "--sync",
        action="store_true",
        help=(
            "ignore the runtime and scope flags; refresh every standard root that "
            "already carries an install manifest. This is the second half of "
            "`uv tool upgrade get-nick-done && gnd install --sync`"
        ),
    )

    return {'install_parser': install_parser}


def _register_doctor(subparsers):
    doctor_parser = subparsers.add_parser(
        "doctor",
        help="report the state of every GND skill this machine has placed",
        description=(
            "Report every placed asset as current, stale, missing, modified or "
            "collided, and print the two environment facts that explain most "
            "'it did not work' reports: the directory the running executable lives "
            "in with an on-PATH verdict, and every target root inspected. BOTH "
            "scopes are always inspected, whichever scope flag is given, because "
            "skill precedence puts the user level ahead of the project level and a "
            "shadowed project install is the most common confusing outcome. Exits 0 "
            "when everything is current, 10 on drift, 11 on a collision, 12 when "
            "nothing is installed anywhere. Text output only, for the reason "
            "`gnd install --help` gives (D-25). "
            "Scope: installed-asset state ONLY. A green doctor says nothing about "
            "your model or its conformance state — in particular it does not report "
            "a pending evolution finalization, which `gnd evolve` reports and "
            "refuses. Reading exit 0 here as 'my model is fine' is the one "
            "misreading this command cannot make for you."
        ),
    )
    _add_target_arguments(doctor_parser)

    return {'doctor_parser': doctor_parser}


def _register_uninstall(subparsers):
    uninstall_parser = subparsers.add_parser(
        "uninstall",
        help="remove the GND skills this machine placed, leaving your own edits alone",
        description=(
            "Remove every skill file GND placed at the requested target roots. A file "
            "is deleted only when its bytes still hash to what the install receipt "
            "recorded, so anything you edited is KEPT and named in the report — there "
            "is deliberately no flag that overrides this. Files GND never placed are "
            "never touched. The directories emptied by the removal are pruned and the "
            "receipt is removed last. Unlike `doctor`, this acts on exactly the scope "
            "you name. Exits 0 on a clean removal, 10 when something was kept, 12 when "
            "nothing is installed, 74 when a receipt could not be trusted (in which "
            "case nothing at all was deleted). Text output only (D-25)."
        ),
    )
    _add_target_arguments(uninstall_parser)

    return {'uninstall_parser': uninstall_parser}


def add_parsers(subparsers, *, command: str | None = None):
    parsers = {}
    if command is None or command == 'install':
        selected = _register_install(subparsers)
        parsers.update(selected)
        selected['install_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if command is None or command == 'doctor':
        selected = _register_doctor(subparsers)
        parsers.update(selected)
        selected['doctor_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if command is None or command == 'uninstall':
        selected = _register_uninstall(subparsers)
        parsers.update(selected)
        selected['uninstall_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if not parsers:
        raise ValueError(f"unsupported command: {command}")
    return parsers


def handle(args, parsers) -> int:
    if args.command == "doctor":
        return _cmd_doctor(claude=args.claude, codex=args.codex)

    if args.command == "uninstall":
        return _cmd_uninstall(claude=args.claude, codex=args.codex, scope=args.scope)

    if args.command == "install":
        return _cmd_install(
            claude=args.claude,
            codex=args.codex,
            scope=args.scope,
            force=args.force,
            symlink=args.symlink,
            sync=args.sync,
        )

    raise ValueError(f"unsupported command: {args.command}")

