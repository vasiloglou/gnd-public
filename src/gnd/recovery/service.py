from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path
from typing import Any

from gnd import safefs as install_module
from gnd.evolve.cli_service import _EvolutionCLIError, _evolve_reject_unsafe_spelling
from gnd.exits import EXIT_IO, EXIT_NO_INPUT


class _RecoveryCLIError(Exception):
    """One classified refusal at the public recovery argv boundary."""

    def __init__(self, exit_code: int, message: str) -> None:
        super().__init__(message)
        self.exit_code = exit_code

def _recovery_root(value: str) -> tuple[Path, int]:
    """Descriptor-walk and retain one authoritative real repository root."""

    from gnd.recovery.inventory import RecoveryInventoryError, _open_real_directory

    try:
        _evolve_reject_unsafe_spelling(value, label="recovery repository root")
    except _EvolutionCLIError as error:
        raise _RecoveryCLIError(error.exit_code, str(error)) from error
    if "\\" in value:
        raise _RecoveryCLIError(EXIT_IO, "recovery repository root must use POSIX path separators")
    supplied = Path(value)
    candidate = supplied if supplied.is_absolute() else Path.cwd() / supplied
    try:
        root_fd, root = _open_real_directory(candidate)
    except RecoveryInventoryError as error:
        exit_code = EXIT_NO_INPUT if _recovery_cause_is(error, FileNotFoundError) else EXIT_IO
        raise _RecoveryCLIError(exit_code, str(error)) from error
    return root, root_fd

def _recovery_relative_argv(root: Path, value: str, *, label: str) -> str:
    """Normalize an argv path to one portable path beneath ``root``."""

    from pathlib import PurePosixPath, PureWindowsPath

    if not value or not value.strip() or "\x00" in value:
        raise _RecoveryCLIError(EXIT_IO, f"{label} must be a nonempty path")
    if value != value.strip() or "\\" in value:
        raise _RecoveryCLIError(EXIT_IO, f"{label} must use normalized POSIX path spelling")
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    if ".." in posix.parts or ".." in windows.parts:
        raise _RecoveryCLIError(EXIT_IO, f"{label} contains a refused '..' component")
    if windows.drive and not windows.is_absolute():
        raise _RecoveryCLIError(EXIT_IO, f"{label} is a refused drive-relative path")

    supplied = Path(value)
    candidate = supplied if supplied.is_absolute() else root.joinpath(*posix.parts)
    try:
        relative = candidate.relative_to(root)
    except ValueError as error:
        raise _RecoveryCLIError(EXIT_IO, f"{label} escapes recovery root {root}") from error
    relative_posix = PurePosixPath(*relative.parts)
    normalized = relative_posix.as_posix()
    if not relative.parts or normalized in {"", "."}:
        raise _RecoveryCLIError(EXIT_IO, f"{label} must name a leaf beneath {root}")
    if not supplied.is_absolute() and posix.as_posix() != value:
        raise _RecoveryCLIError(EXIT_IO, f"{label} is not in canonical POSIX form")
    return normalized

def _recovery_required_canonical_leaf(
    root: Path,
    root_fd: int,
    value: str,
    *,
    label: str,
    canonical_name: str,
) -> Path:
    """Require an explicit argv leaf to identify one canonical bundle sibling."""

    relative = _recovery_relative_argv(root, value, label=label)
    if relative != canonical_name:
        raise _RecoveryCLIError(
            EXIT_IO,
            f"{label} must be the canonical sibling {root / canonical_name}",
        )
    path = root / relative
    try:
        info = os.stat(canonical_name, dir_fd=root_fd, follow_symlinks=False)
    except FileNotFoundError as error:
        raise _RecoveryCLIError(EXIT_NO_INPUT, f"required {label} {path} is missing") from error
    except OSError as error:
        raise _RecoveryCLIError(
            EXIT_IO, f"{label} {path} could not be inspected: {error}"
        ) from error
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise _RecoveryCLIError(EXIT_IO, f"{label} {path} is not a real regular file")
    return path

def _recovery_cause_is(error: BaseException, kind: type[BaseException]) -> bool:
    """Whether one closed error chain contains ``kind`` (without prose parsing)."""

    seen: set[int] = set()
    current: BaseException | None = error
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if isinstance(current, kind):
            return True
        current = current.__cause__ or current.__context__
    return False

def _recovery_json(value: Any) -> str:
    """Canonical public JSON for frozen recovery records."""

    document = value.model_dump(mode="json")
    return json.dumps(
        document,
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
        allow_nan=False,
    )

def _recovery_open_output_parent(root_fd: int, relative: str) -> tuple[int, str]:
    """Return a descriptor-bound existing real output parent and leaf name."""

    from pathlib import PurePosixPath

    parts = PurePosixPath(relative).parts
    current = os.dup(root_fd)
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        for part in parts[:-1]:
            before = os.stat(part, dir_fd=current, follow_symlinks=False)
            if stat.S_ISLNK(before.st_mode) or not stat.S_ISDIR(before.st_mode):
                raise _RecoveryCLIError(
                    EXIT_IO, f"inventory output crosses non-directory component {part!r}"
                )
            child = os.open(part, flags, dir_fd=current)
            actual = os.fstat(child)
            if (before.st_dev, before.st_ino) != (actual.st_dev, actual.st_ino):
                os.close(child)
                raise _RecoveryCLIError(
                    EXIT_IO, f"inventory output component {part!r} changed before open"
                )
            os.close(current)
            current = child
        return current, parts[-1]
    except FileNotFoundError as error:
        os.close(current)
        raise _RecoveryCLIError(
            EXIT_IO, "inventory output parent must already exist beneath ROOT"
        ) from error
    except OSError as error:
        os.close(current)
        raise _RecoveryCLIError(
            EXIT_IO, f"inventory output parent could not be opened safely: {error}"
        ) from error
    except BaseException:
        os.close(current)
        raise

_RECOVERY_DIRECTORY_NAME_OBSERVATION_CAP = 10_000

def _recovery_canonical_directory_parts(
    root_fd: int,
    parts: tuple[str, ...],
) -> tuple[str, ...]:
    """Resolve existing directory components to their stored names by identity."""

    current = os.dup(root_fd)
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    canonical: list[str] = []
    try:
        for supplied in parts:
            before = os.stat(supplied, dir_fd=current, follow_symlinks=False)
            if stat.S_ISLNK(before.st_mode) or not stat.S_ISDIR(before.st_mode):
                raise _RecoveryCLIError(
                    EXIT_IO, f"directory component {supplied!r} is not a real directory"
                )
            child = os.open(supplied, flags, dir_fd=current)
            actual = os.fstat(child)
            if (before.st_dev, before.st_ino) != (actual.st_dev, actual.st_ino):
                os.close(child)
                raise _RecoveryCLIError(
                    EXIT_IO, f"directory component {supplied!r} changed before open"
                )
            stored_names: list[str] = []
            observations = 0
            with os.scandir(current) as entries:
                for entry in entries:
                    observations += 1
                    if observations > _RECOVERY_DIRECTORY_NAME_OBSERVATION_CAP:
                        os.close(child)
                        raise _RecoveryCLIError(
                            EXIT_IO,
                            f"directory contains too many entries to resolve {supplied!r} safely",
                        )
                    try:
                        observed = entry.stat(follow_symlinks=False)
                    except OSError:
                        continue
                    if (observed.st_dev, observed.st_ino) == (
                        actual.st_dev,
                        actual.st_ino,
                    ):
                        stored_names.append(entry.name)
            if len(stored_names) != 1:
                os.close(child)
                raise _RecoveryCLIError(
                    EXIT_IO,
                    f"directory component {supplied!r} has no unique stored identity",
                )
            canonical.append(stored_names[0])
            os.close(current)
            current = child
        return tuple(canonical)
    except FileNotFoundError as error:
        raise _RecoveryCLIError(
            EXIT_NO_INPUT, f"directory component is missing: {error}"
        ) from error
    except OSError as error:
        raise _RecoveryCLIError(
            EXIT_IO, f"directory component could not be resolved safely: {error}"
        ) from error
    finally:
        os.close(current)

def _recovery_require_absent_output(root_fd: int, relative: str) -> None:
    parent_fd, name = _recovery_open_output_parent(root_fd, relative)
    try:
        try:
            os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            return
        except OSError as error:
            raise _RecoveryCLIError(
                EXIT_IO, f"inventory output {relative} could not be inspected: {error}"
            ) from error
        raise _RecoveryCLIError(
            EXIT_IO, f"inventory output {relative} already exists; refusing to overwrite it"
        )
    finally:
        os.close(parent_fd)

def _recovery_require_existing_exclusion(root_fd: int, relative: str) -> None:
    """Require one user-declared exclusion to exist beneath the bound root."""

    parent_fd, name = _recovery_open_output_parent(root_fd, relative)
    try:
        try:
            os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError as error:
            raise _RecoveryCLIError(
                EXIT_NO_INPUT, f"explicit exclusion {relative} does not exist"
            ) from error
        except OSError as error:
            raise _RecoveryCLIError(
                EXIT_IO, f"explicit exclusion {relative} could not be inspected: {error}"
            ) from error
    finally:
        os.close(parent_fd)

def _recovery_root_still_bound(root: Path, root_fd: int) -> None:
    """Refuse publication if argv ROOT no longer names the scanned directory."""

    from gnd.recovery.inventory import RecoveryInventoryError, _open_real_directory

    expected = os.fstat(root_fd)
    try:
        check_fd, _ = _open_real_directory(root)
    except RecoveryInventoryError as error:
        raise _RecoveryCLIError(
            EXIT_IO, f"recovery repository root {root} changed during operation: {error}"
        ) from error
    try:
        actual = os.fstat(check_fd)
        if (actual.st_dev, actual.st_ino) != (expected.st_dev, expected.st_ino):
            raise _RecoveryCLIError(
                EXIT_IO, f"recovery repository root {root} changed during inventory"
            )
    finally:
        os.close(check_fd)

def _recovery_publish_absent(root_fd: int, relative: str, data: bytes) -> None:
    """Publish one absent leaf relative to the retained repository descriptor."""

    parent_fd, name = _recovery_open_output_parent(root_fd, relative)
    staging = f".gnd-recovery-{os.urandom(8).hex()}"
    staged = False
    try:
        handle_fd = os.open(
            staging,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o644,
            dir_fd=parent_fd,
        )
        staged = True
        with os.fdopen(handle_fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(
                staging,
                name,
                src_dir_fd=parent_fd,
                dst_dir_fd=parent_fd,
                follow_symlinks=False,
            )
        except FileExistsError as error:
            raise _RecoveryCLIError(
                EXIT_IO,
                f"inventory output {relative} changed before publication; refusing overwrite",
            ) from error
        os.unlink(staging, dir_fd=parent_fd)
        staged = False
    except _RecoveryCLIError:
        raise
    except OSError as error:
        raise _RecoveryCLIError(
            EXIT_IO, f"inventory output {relative} could not be published: {error}"
        ) from error
    finally:
        if staged:
            try:
                os.unlink(staging, dir_fd=parent_fd)
            except OSError:
                pass
        os.close(parent_fd)

def _parse_recovery_exclusion(value: str) -> Any:
    """Parse ``REASON=PATH`` into the closed public exclusion record."""

    from pydantic import ValidationError

    from gnd.recovery.report import ExcludedRoot, ExclusionReason

    if "=" not in value:
        raise _RecoveryCLIError(
            3,
            f"exclusion {value!r} must use REASON=PATH with a closed exclusion reason",
        )
    reason_value, path = value.split("=", 1)
    try:
        reason = ExclusionReason(reason_value)
    except ValueError as error:
        raise _RecoveryCLIError(3, f"invalid exclusion reason {reason_value!r}") from error
    try:
        return ExcludedRoot(
            exclusion_id=(
                "cli-exclusion-"
                + hashlib.sha256(f"{reason.value}\0{path}".encode()).hexdigest()[:16]
            ),
            path=path,
            reason=reason,
        )
    except ValidationError as error:
        raise _RecoveryCLIError(EXIT_IO, f"unsafe exclusion path in {value!r}: {error}") from error

def _cmd_recovery_inventory(
    root_value: str,
    sources: list[str],
    tests: list[str],
    docs: list[str],
    configs: list[str],
    schemas: list[str],
    exclusions: list[str],
    max_file_bytes: int,
    max_total_bytes: int,
    max_files: int,
    out_value: str,
) -> int:
    """Inventory explicit repository roots as inert, bounded static evidence."""

    from pydantic import ValidationError

    from gnd.recovery.inventory import (
        _CONTROLLER_BUNDLE_PATHS,
        RecoveryInventoryError,
        _controller_reserved_exclusion,
        _is_canonical_bundle_alias,
        scan_recovery_scope,
    )
    from gnd.recovery.report import (
        RootCategory,
        SelectedRoot,
    )

    try:
        root, root_fd = _recovery_root(root_value)
        try:
            output_relative = _recovery_relative_argv(root, out_value, label="inventory output")
            canonical_bundle_names = _CONTROLLER_BUNDLE_PATHS
            if _is_canonical_bundle_alias(output_relative):
                raise _RecoveryCLIError(
                    3,
                    "inventory --out cannot replace a canonical recovery bundle artifact",
                )
            output_path = root / output_relative
            _recovery_require_absent_output(root_fd, output_relative)
            from pathlib import PurePosixPath

            output_parts = PurePosixPath(output_relative).parts
            canonical_output_parent = _recovery_canonical_directory_parts(
                root_fd, output_parts[:-1]
            )

            categorized = (
                (RootCategory.source, sources),
                (RootCategory.test, tests),
                (RootCategory.docs, docs),
                (RootCategory.config, configs),
                (RootCategory.schema, schemas),
            )
            if not any(values for _, values in categorized):
                raise _RecoveryCLIError(3, "at least one categorized recovery root is required")
            try:
                selected = tuple(
                    sorted(
                        (
                            SelectedRoot(category=category, path=path)
                            for category, values in categorized
                            for path in values
                        ),
                        key=lambda item: (item.path, item.category.value),
                    )
                )
            except ValidationError as error:
                raise _RecoveryCLIError(
                    EXIT_IO, f"unsafe selected recovery root: {error}"
                ) from error
            selected_bindings = tuple(
                (
                    item,
                    () if item.path == "." else PurePosixPath(item.path).parts,
                    _recovery_canonical_directory_parts(
                        root_fd,
                        () if item.path == "." else PurePosixPath(item.path).parts,
                    ),
                )
                for item in selected
            )
            selected_parts = sorted(canonical for _item, _supplied, canonical in selected_bindings)
            if any(
                other[: len(parts)] == parts
                for index, parts in enumerate(selected_parts)
                for other in selected_parts[index + 1 :]
            ):
                raise _RecoveryCLIError(3, "selected recovery roots must not overlap")
            parsed_exclusions = tuple(
                sorted(
                    (_parse_recovery_exclusion(value) for value in exclusions),
                    key=lambda item: (item.path, item.reason.value),
                )
            )
            for item in parsed_exclusions:
                _recovery_require_existing_exclusion(root_fd, item.path)
            output_scope_matches = tuple(
                (item, supplied, canonical)
                for item, supplied, canonical in selected_bindings
                if canonical_output_parent[: len(canonical)] == canonical
            )
            if len(output_scope_matches) > 1:
                raise _RecoveryCLIError(
                    3, "inventory output resolves beneath overlapping selected roots"
                )
            controller_output_path: str | None = None
            if output_scope_matches:
                _selected, supplied, canonical = output_scope_matches[0]
                controller_output_path = PurePosixPath(
                    *supplied,
                    *canonical_output_parent[len(canonical) :],
                    output_parts[-1],
                ).as_posix()
            reserved_paths: list[tuple[str, str]] = []
            if controller_output_path is not None:
                reserved_paths.append(("output", controller_output_path))
            if any(not canonical for _item, _supplied, canonical in selected_bindings):
                reserved_paths.extend(("bundle", name) for name in canonical_bundle_names)
            reserved_path_names = {path for _role, path in reserved_paths}
            conflicting_user_exclusions = sorted(
                item.path for item in parsed_exclusions if item.path in reserved_path_names
            )
            if conflicting_user_exclusions:
                raise _RecoveryCLIError(
                    3,
                    "controller-generated recovery paths cannot also be user exclusions: "
                    f"{conflicting_user_exclusions}",
                )
            controller_exclusions = tuple(
                _controller_reserved_exclusion(role, path)
                for role, path in sorted(reserved_paths, key=lambda item: item[1])
            )
            scan_exclusions = tuple(
                sorted((*parsed_exclusions, *controller_exclusions), key=lambda item: item.path)
            )
            inventory = scan_recovery_scope(
                root,
                selected,
                excluded_roots=scan_exclusions,
                max_file_bytes=max_file_bytes,
                max_total_bytes=max_total_bytes,
                max_files=max_files,
                expected_root_identity=(
                    os.fstat(root_fd).st_dev,
                    os.fstat(root_fd).st_ino,
                ),
            )
            observed_exclusions = {item.path for item in inventory.scope.excluded_roots}
            blocking_output_exclusions = sorted(
                item.path
                for item in inventory.scope.excluded_roots
                if controller_output_path is not None
                and controller_output_path.startswith(f"{item.path}/")
            )
            if blocking_output_exclusions:
                raise _RecoveryCLIError(
                    3,
                    "inventory output cannot sit below an excluded tree: "
                    f"{blocking_output_exclusions}",
                )
            missing_exclusions = sorted(
                item.path for item in parsed_exclusions if item.path not in observed_exclusions
            )
            if missing_exclusions:
                raise _RecoveryCLIError(
                    EXIT_NO_INPUT,
                    f"explicit exclusions disappeared before inventory: {missing_exclusions}",
                )
            rendered = (_recovery_json(inventory) + "\n").encode("utf-8")
            _recovery_root_still_bound(root, root_fd)
            _recovery_publish_absent(root_fd, output_relative, rendered)
        finally:
            os.close(root_fd)
    except _RecoveryCLIError as error:
        print(f"RECOVERY INVENTORY REFUSED ({error.exit_code}): {error}")
        return error.exit_code
    except FileNotFoundError as error:
        print(f"RECOVERY INVENTORY REFUSED ({EXIT_NO_INPUT}): missing selected root: {error}")
        return EXIT_NO_INPUT
    except RecoveryInventoryError as error:
        if _recovery_cause_is(error, FileNotFoundError):
            exit_code = EXIT_NO_INPUT
        else:
            exit_code = EXIT_IO
        print(f"RECOVERY INVENTORY REFUSED ({exit_code}): {error}")
        return exit_code
    except ValidationError as error:
        print(f"RECOVERY INVENTORY REFUSED (3): {error}")
        return 3
    except (install_module.InstallError, install_module.InstallPathError, OSError) as error:
        print(f"RECOVERY INVENTORY REFUSED ({EXIT_IO}): {error}")
        return EXIT_IO
    except (TypeError, ValueError) as error:
        print(f"RECOVERY INVENTORY REFUSED (3): {error}")
        return 3

    print(f"recovery inventory wrote {output_path}")
    return 0

def _cmd_recovery_verify(
    root_value: str,
    report_value: str,
    model_value: str,
    verbalization_value: str,
) -> int:
    """Verify one canonical three-artifact recovery bundle without mutation."""

    from gnd.recovery.verify import verify_recovery_bundle

    try:
        root, root_fd = _recovery_root(root_value)
        try:
            _recovery_required_canonical_leaf(
                root,
                root_fd,
                report_value,
                label="recovery report",
                canonical_name="model.recovery.json",
            )
            _recovery_required_canonical_leaf(
                root,
                root_fd,
                model_value,
                label="recovered model",
                canonical_name="model.orm.yaml",
            )
            _recovery_required_canonical_leaf(
                root,
                root_fd,
                verbalization_value,
                label="model verbalization",
                canonical_name="model.verbalization.txt",
            )
            root_info = os.fstat(root_fd)
            result = verify_recovery_bundle(
                root,
                expected_root_identity=(root_info.st_dev, root_info.st_ino),
            )
            _recovery_root_still_bound(root, root_fd)
        finally:
            os.close(root_fd)
    except _RecoveryCLIError as error:
        print(f"RECOVERY VERIFY REFUSED ({error.exit_code}): {error}")
        return error.exit_code

    print(_recovery_json(result))
    if result.ok:
        return 0
    if any(error.startswith("missing-artifact:") for error in result.errors):
        return EXIT_NO_INPUT
    if any(error.startswith(("unsafe-artifact:", "parent-traversal:")) for error in result.errors):
        return EXIT_IO
    return 3

_RecoveryCLIError.__module__ = "gnd.cli"
_recovery_root.__module__ = "gnd.cli"
_recovery_relative_argv.__module__ = "gnd.cli"
_recovery_required_canonical_leaf.__module__ = "gnd.cli"
_recovery_cause_is.__module__ = "gnd.cli"
_recovery_json.__module__ = "gnd.cli"
_recovery_open_output_parent.__module__ = "gnd.cli"
_recovery_canonical_directory_parts.__module__ = "gnd.cli"
_recovery_require_absent_output.__module__ = "gnd.cli"
_recovery_require_existing_exclusion.__module__ = "gnd.cli"
_recovery_root_still_bound.__module__ = "gnd.cli"
_recovery_publish_absent.__module__ = "gnd.cli"
_parse_recovery_exclusion.__module__ = "gnd.cli"
_cmd_recovery_inventory.__module__ = "gnd.cli"
_cmd_recovery_verify.__module__ = "gnd.cli"
