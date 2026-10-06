"""Conservative static inventory for one-time brownfield model recovery.

The repository is untrusted.  Traversal is descriptor-bound and no-follow,
source is parsed only as data, and every selected leaf is represented in the
closed census as parsed evidence, an exclusion, an ambiguity, or frontier.
No source from the inspected tree is imported or executed.
"""

from __future__ import annotations

import ast
import json
import math
import os
import re
import stat
import sys
import unicodedata
from collections import Counter, defaultdict, deque
from collections.abc import Iterator
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from ruamel.yaml import YAML, YAMLError
from ruamel.yaml.tokens import AliasToken, AnchorToken

from gnd import input_policy as _rf7_input
from gnd.artifacts import canonical_json_text, sha256_hex
from gnd.recovery.report import (
    AmbiguousProposal,
    CensusEntry,
    EvidenceRecord,
    ExcludedRoot,
    FrontierItem,
    JsonPointerLocator,
    LineLocator,
    PythonSymbolLocator,
    RecoveryInventory,
    RecoveryScope,
    RootCategory,
    SelectedRoot,
    YamlPathLocator,
)

__all__ = ["RecoveryInventoryError", "scan_recovery_scope"]

DEFAULT_MAX_FILE_BYTES = 2 * 1024 * 1024
DEFAULT_MAX_TOTAL_BYTES = 32 * 1024 * 1024
DEFAULT_MAX_FILES = 10_000
MAX_DEPTH = 64
MAX_DIRECTORIES = 10_000
MAX_OBSERVATIONS = 10_000
MAX_STRUCTURE_NODES = 20_000
MAX_YAML_TOKENS = 100_000
MAX_ALIAS_EDGES = 2 * MAX_STRUCTURE_NODES
_CONTROLLER_BUNDLE_PATHS = (
    "model.orm.yaml",
    "model.verbalization.txt",
    "model.recovery.json",
)

_YAML = YAML(typ="safe")
# ``ruamel.yaml`` defers a few of its own imports until the first load.  Prime
# those imports over a package-owned constant while this trusted module is
# imported, before callers install the no-import guard around repository scans.
list(_YAML.scan("{}\n"))
_YAML.load("{}\n")
# Pydantic likewise resolves the discriminated evidence-locator collection on
# first validation.  Exercise that package-owned schema once at import time so
# repository traversal itself never crosses an import boundary.
_EVIDENCE_SCHEMA_PRIMER = EvidenceRecord(
    evidence_id="schema-primer",
    path="schema-primer",
    sha256="0" * 64,
    byte_length=0,
    media_type="text/plain",
    encoding="utf-8",
    locator=LineLocator(line_start=1, line_end=1),
    excerpt_sha256="0" * 64,
)
del _EVIDENCE_SCHEMA_PRIMER
_PROPOSAL_MARKER = r"recovery-proposal:\s*(?P<claim>[^\r\n#]+)"
_MIXED_MARKER = r"recovery-language:\s*[^\r\n]*(?:\+|mixed)"
_DDL = r"^\s*CREATE\s+(?:TABLE|TYPE|DOMAIN)\b"
_DYNAMIC_CALLS = frozenset(
    {
        "__import__",
        "compile",
        "delattr",
        "eval",
        "exec",
        "globals",
        "getattr",
        "import_module",
        "locals",
        "make_dataclass",
        "namedtuple",
        "new_class",
        "prepare_class",
        "setattr",
        "type",
        "vars",
    }
)

_DEFAULT_EXCLUSIONS: dict[str, str] = {
    ".git": "cache",
    ".hg": "cache",
    ".svn": "cache",
    ".cache": "cache",
    ".mypy_cache": "cache",
    ".pytest_cache": "cache",
    ".ruff_cache": "cache",
    "__pycache__": "cache",
    ".venv": "dependency",
    "venv": "dependency",
    "node_modules": "dependency",
    "site-packages": "dependency",
    "vendor": "vendored",
    "vendored": "vendored",
    "third_party": "vendored",
    "third-party": "vendored",
    "generated": "generated",
    "build": "build",
    "dist": "build",
    "out": "build",
    "target": "build",
    ".env": "sensitive-tree",
    ".aws": "sensitive-tree",
    ".ssh": "sensitive-tree",
}

_MEDIA_TYPES = {
    ".py": "text/x-python",
    ".md": "text/markdown",
    ".rst": "text/x-rst",
    ".txt": "text/plain",
    ".yaml": "application/yaml",
    ".yml": "application/yaml",
    ".json": "application/json",
    ".sql": "application/sql",
}


class RecoveryInventoryError(ValueError):
    """The requested recovery scope cannot be inventoried safely or fully."""


def _controller_reserved_exclusion(role: str, path: str) -> ExcludedRoot:
    """Build one deterministic controller-owned prospective exclusion."""

    if role not in {"output", "bundle"}:
        raise RecoveryInventoryError(f"unknown controller exclusion role {role!r}")
    if role == "bundle" and path not in _CONTROLLER_BUNDLE_PATHS:
        raise RecoveryInventoryError(f"unknown canonical recovery bundle path {path!r}")
    return ExcludedRoot(
        exclusion_id=(
            f"controller-{role}-" + sha256_hex(path.encode())[:16]
        ),
        path=path,
        reason="generated",
    )


def _is_canonical_bundle_alias(path: str) -> bool:
    """Whether one direct leaf aliases a canonical artifact portably."""

    posix = PurePosixPath(path)
    if len(posix.parts) != 1:
        return False
    key = unicodedata.normalize("NFKC", posix.name).casefold()
    return key in {
        unicodedata.normalize("NFKC", name).casefold()
        for name in _CONTROLLER_BUNDLE_PATHS
    }


def _portable_path_parts(path: str) -> tuple[str, ...]:
    """Normalize a relative path for case/normalization-alias comparisons."""

    return tuple(
        unicodedata.normalize("NFKC", part).casefold()
        for part in PurePosixPath(path).parts
    )


def _controller_reservation_role(entry: ExcludedRoot) -> str | None:
    """Return the validated prospective role encoded by a controller ID."""

    for role in ("output", "bundle"):
        if role == "bundle" and entry.path not in _CONTROLLER_BUNDLE_PATHS:
            continue
        expected = _controller_reserved_exclusion(role, entry.path)
        if entry.exclusion_id == expected.exclusion_id:
            if entry.reason != expected.reason:
                raise RecoveryInventoryError(
                    f"controller exclusion {entry.exclusion_id} has the wrong reason"
                )
            return role
    if entry.exclusion_id.startswith("controller-"):
        raise RecoveryInventoryError(
            f"controller exclusion identity {entry.exclusion_id!r} is malformed"
        )
    return None


def _validate_controller_reservation_set(
    selected_roots: tuple[SelectedRoot, ...],
    exclusions: tuple[ExcludedRoot, ...],
    *,
    required_for_bundle: bool,
) -> None:
    """Require prospective rows to be exactly a set the public CLI can emit."""

    reservations = tuple(
        (entry, role)
        for entry in exclusions
        if (role := _controller_reservation_role(entry)) is not None
    )
    dot_selected = any(root.path == "." for root in selected_roots)
    if not reservations:
        if required_for_bundle and dot_selected:
            raise RecoveryInventoryError(
                "whole-root recovery verification requires controller artifact reservations"
            )
        return

    outputs = tuple(entry for entry, role in reservations if role == "output")
    bundles = tuple(entry for entry, role in reservations if role == "bundle")
    if len(outputs) > 1:
        raise RecoveryInventoryError("at most one controller output reservation is allowed")
    if dot_selected:
        if len(outputs) != 1 or {entry.path for entry in bundles} != set(
            _CONTROLLER_BUNDLE_PATHS
        ):
            raise RecoveryInventoryError(
                "whole-root controller reservations require one output and all bundle leaves"
            )
    elif bundles:
        raise RecoveryInventoryError(
            "bundle reservations are allowed only when the whole repository is selected"
        )

    portable_paths: dict[tuple[str, ...], str] = {}
    for entry in exclusions:
        portable = _portable_path_parts(entry.path)
        previous = portable_paths.setdefault(portable, entry.path)
        if previous != entry.path:
            raise RecoveryInventoryError(
                f"controller exclusions have portable path aliases {previous!r} and {entry.path!r}"
            )

    if outputs:
        output = outputs[0]
        if _is_canonical_bundle_alias(output.path):
            raise RecoveryInventoryError(
                "controller output cannot reuse a canonical bundle path"
            )
        output_parts = _portable_path_parts(output.path)
        for entry in exclusions:
            if entry.exclusion_id == output.exclusion_id:
                continue
            other_parts = _portable_path_parts(entry.path)
            if (
                other_parts[: len(output_parts)] == output_parts
                or output_parts[: len(other_parts)] == other_parts
            ):
                raise RecoveryInventoryError(
                    "controller output cannot contain or sit beneath another exclusion"
                )


def _slug(value: str) -> str:
    words = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", value)
    slug = re.sub(r"[^a-z0-9]+", "-", words.lower()).strip("-")
    return slug or "item"


def _safe_relative(value: str, *, field: str) -> tuple[str, ...]:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise RecoveryInventoryError(f"{field} must be a nonempty relative path")
    if value == ".":
        return ()
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    if (
        posix.is_absolute()
        or windows.is_absolute()
        or bool(windows.drive)
        or value.startswith(("/", "\\"))
        or "\\" in value
        or not posix.parts
        or any(part in {"", ".", ".."} for part in posix.parts)
    ):
        raise RecoveryInventoryError(f"{field} must be a normalized repository-relative path")
    if posix.as_posix() != value:
        raise RecoveryInventoryError(f"{field} is not in canonical POSIX form")
    return posix.parts


def _open_real_directory(path: Path) -> tuple[int, Path]:
    """Open an absolute directory by walking every component without links."""

    absolute = Path(os.path.abspath(os.fspath(path)))
    anchor = absolute.anchor or os.path.sep
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        current = os.open(anchor, flags)
    except OSError as error:
        raise RecoveryInventoryError(f"repository root could not be opened: {error}") from error
    try:
        for part in absolute.parts[1:]:
            try:
                before = os.stat(part, dir_fd=current, follow_symlinks=False)
            except OSError as error:
                raise RecoveryInventoryError(
                    f"repository directory component {part!r} could not be inspected: {error}"
                ) from error
            if stat.S_ISLNK(before.st_mode) or not stat.S_ISDIR(before.st_mode):
                raise RecoveryInventoryError(
                    f"repository directory component {part!r} is not a real directory"
                )
            try:
                opened = os.open(part, flags, dir_fd=current)
            except OSError as error:
                raise RecoveryInventoryError(
                    f"repository directory component {part!r} could not be opened safely: {error}"
                ) from error
            actual = os.fstat(opened)
            if (actual.st_dev, actual.st_ino) != (before.st_dev, before.st_ino):
                os.close(opened)
                raise RecoveryInventoryError(
                    f"repository directory component {part!r} changed before it opened"
                )
            os.close(current)
            current = opened
        return current, absolute
    except BaseException:
        os.close(current)
        raise


def _open_child_directory(parent_fd: int, name: str, before: os.stat_result) -> int:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        child = os.open(name, flags, dir_fd=parent_fd)
    except OSError as error:
        raise RecoveryInventoryError(
            f"directory {name!r} could not be opened safely: {error}"
        ) from error
    actual = os.fstat(child)
    if not stat.S_ISDIR(actual.st_mode) or (actual.st_dev, actual.st_ino) != (
        before.st_dev,
        before.st_ino,
    ):
        os.close(child)
        raise RecoveryInventoryError(f"directory {name!r} changed before it opened")
    return child


def _descend(root_fd: int, parts: tuple[str, ...]) -> int:
    current = os.dup(root_fd)
    try:
        for part in parts:
            before = os.stat(part, dir_fd=current, follow_symlinks=False)
            if stat.S_ISLNK(before.st_mode) or not stat.S_ISDIR(before.st_mode):
                raise RecoveryInventoryError(
                    f"selected root component {part!r} is not a real directory"
                )
            child = _open_child_directory(current, part, before)
            os.close(current)
            current = child
        return current
    except BaseException:
        os.close(current)
        raise


def _read_regular(
    parent_fd: int,
    name: str,
    *,
    relative: str,
    before: os.stat_result,
    cap: int,
) -> bytes:
    try:
        descriptor = os.open(
            name,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
    except OSError as error:
        raise RecoveryInventoryError(
            f"selected file {relative} could not be opened: {error}"
        ) from error
    try:
        opened = os.fstat(descriptor)
        bound_fields = (
            "st_dev",
            "st_ino",
            "st_mode",
            "st_size",
            "st_mtime_ns",
            "st_ctime_ns",
        )
        if not stat.S_ISREG(opened.st_mode) or any(
            getattr(opened, field) != getattr(before, field) for field in bound_fields
        ):
            raise RecoveryInventoryError(f"selected file {relative} changed before it opened")
        chunks = bytearray()
        while chunk := os.read(descriptor, min(64 * 1024, cap + 1 - len(chunks))):
            chunks.extend(chunk)
            if len(chunks) > cap:
                raise RecoveryInventoryError(f"selected file {relative} grew over its byte cap")
        after = os.fstat(descriptor)
        fields = ("st_dev", "st_ino", "st_mode", "st_size", "st_mtime_ns", "st_ctime_ns")
        if any(getattr(opened, field) != getattr(after, field) for field in fields):
            raise RecoveryInventoryError(f"selected file {relative} changed while it was read")
        if len(chunks) != opened.st_size:
            raise RecoveryInventoryError(f"selected file {relative} changed size while it was read")
        return bytes(chunks)
    finally:
        os.close(descriptor)


def _frontier_id(path: str, reason: str) -> str:
    stem = PurePosixPath(path).stem
    suffix = "-symlink" if reason in {"symlink", "symlink-cycle"} else ""
    return f"frontier:{_slug(stem)}{suffix}"


def _evidence_id(path: str, label: str, kind: str, used: set[str]) -> str:
    base = f"ev-{_slug(label)}-{_slug(kind)}"
    candidate = base
    if candidate in used:
        suffix = sha256_hex(f"{path}\0{label}\0{kind}".encode())[:8]
        candidate = f"{base}-{suffix}"
        ordinal = 2
        while candidate in used:
            candidate = f"{base}-{suffix}-{ordinal}"
            ordinal += 1
    used.add(candidate)
    return candidate


def _line_bytes(data: bytes, start: int, end: int) -> bytes:
    lines = data.splitlines(keepends=True)
    return b"".join(lines[start - 1 : end])


def _python_symbols(tree: ast.Module) -> list[tuple[str, ast.AST, str]]:
    observations: list[tuple[str, ast.AST, str]] = []

    def visit_body(body: list[ast.stmt], prefix: tuple[str, ...] = ()) -> None:
        for node in body:
            if isinstance(node, ast.ClassDef):
                qualname = ".".join((*prefix, node.name))
                is_enum = any(
                    (isinstance(base, ast.Name) and base.id == "Enum")
                    or (isinstance(base, ast.Attribute) and base.attr == "Enum")
                    for base in node.bases
                )
                observations.append((qualname, node, "enum" if is_enum else "class"))
                visit_body(node.body, (*prefix, node.name))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qualname = ".".join((*prefix, node.name))
                observations.append(
                    (qualname, node, "test" if node.name.startswith("test_") else "function")
                )
            elif isinstance(node, ast.Assert):
                observations.append(("assertion", node, "assertion"))

    visit_body(tree.body)
    return observations


def _iter_ast_nodes(tree: ast.AST) -> Iterator[ast.AST]:
    pending: list[ast.AST] = [tree]
    while pending:
        node = pending.pop()
        yield node
        pending.extend(ast.iter_child_nodes(node))


def _has_dynamic_construct(tree: ast.Module) -> bool:
    nodes = tuple(_iter_ast_nodes(tree))
    alias_edges: dict[str, set[str]] = defaultdict(set)
    dynamic_aliases = set(_DYNAMIC_CALLS)
    edge_count = 0
    edge_cap_exceeded = False

    def assigned_names(target: ast.AST) -> set[str]:
        names: set[str] = set()
        pending_targets = [target]
        while pending_targets:
            current = pending_targets.pop()
            if isinstance(current, ast.Name):
                names.add(current.id)
            elif isinstance(current, (ast.List, ast.Tuple)):
                pending_targets.extend(current.elts)
        return names

    def alias_sources(value: ast.AST) -> tuple[set[str], bool]:
        sources: set[str] = set()
        is_dynamic = False
        pending_values = [value]
        while pending_values:
            current = pending_values.pop()
            if isinstance(current, ast.Name):
                sources.add(current.id)
            elif isinstance(current, ast.Attribute):
                is_dynamic = is_dynamic or current.attr in _DYNAMIC_CALLS
            elif isinstance(current, ast.NamedExpr):
                sources.update(assigned_names(current.target))
                pending_values.append(current.value)
            elif isinstance(current, (ast.List, ast.Tuple)):
                pending_values.extend(current.elts)
        return sources, is_dynamic

    def add_edge(source: str, target: str) -> None:
        nonlocal edge_count, edge_cap_exceeded
        if edge_cap_exceeded or target in alias_edges[source]:
            return
        if edge_count >= MAX_ALIAS_EDGES:
            edge_cap_exceeded = True
            return
        alias_edges[source].add(target)
        edge_count += 1

    def connect_aliases(
        targets: set[str],
        sources: set[str],
        is_dynamic: bool,
        group: str,
    ) -> None:
        if not targets:
            return
        if is_dynamic:
            dynamic_aliases.update(targets)
            return
        if len(sources) == 1:
            source = next(iter(sources))
            for target in targets:
                add_edge(source, target)
            return
        if sources:
            aggregate = f"\0alias-group:{group}"
            for source in sources:
                add_edge(source, aggregate)
            for target in targets:
                add_edge(aggregate, target)

    def record_assignment(target: ast.AST, value: ast.AST, group: str) -> None:
        pending_pairs: list[tuple[ast.AST, ast.AST, str]] = [(target, value, group)]
        while pending_pairs and not edge_cap_exceeded:
            current_target, current_value, current_group = pending_pairs.pop()
            if (
                isinstance(current_target, (ast.List, ast.Tuple))
                and isinstance(current_value, (ast.List, ast.Tuple))
                and len(current_target.elts) == len(current_value.elts)
            ):
                pending_pairs.extend(
                    (target_item, value_item, f"{current_group}:{index}")
                    for index, (target_item, value_item) in enumerate(
                        zip(current_target.elts, current_value.elts, strict=True)
                    )
                )
                continue
            sources, is_dynamic = alias_sources(current_value)
            connect_aliases(
                assigned_names(current_target),
                sources,
                is_dynamic,
                current_group,
            )

    for node_index, node in enumerate(nodes):
        if isinstance(node, ast.ImportFrom):
            for imported in node.names:
                if imported.name.rsplit(".", 1)[-1] in _DYNAMIC_CALLS:
                    dynamic_aliases.add(imported.asname or imported.name)
        if isinstance(node, ast.Assign):
            for target_index, target in enumerate(node.targets):
                record_assignment(target, node.value, f"{node_index}:{target_index}")
        elif isinstance(node, (ast.AnnAssign, ast.NamedExpr)):
            if node.value is not None:
                record_assignment(node.target, node.value, str(node_index))
        else:
            continue
        if edge_cap_exceeded:
            return True

    pending = deque(dynamic_aliases)
    while pending:
        source = pending.popleft()
        for alias in alias_edges[source]:
            if alias not in dynamic_aliases:
                dynamic_aliases.add(alias)
                pending.append(alias)

    for node in nodes:
        if isinstance(node, ast.ClassDef) and any(
            keyword.arg == "metaclass" for keyword in node.keywords
        ):
            return True
        if not isinstance(node, ast.Call):
            continue
        target = node.func
        if isinstance(target, ast.Name) and target.id in dynamic_aliases:
            return True
        if isinstance(target, ast.Attribute) and target.attr in _DYNAMIC_CALLS:
            return True
        if isinstance(target, ast.NamedExpr) and (
            isinstance(target.target, ast.Name) and target.target.id in dynamic_aliases
        ):
            return True
    return False


def _assertion_label(node: ast.Assert) -> str:
    for candidate in _iter_ast_nodes(node.test):
        value = candidate
        while isinstance(value, ast.Attribute):
            value = value.value
        if isinstance(value, ast.Name) and value.id not in {"True", "False", "None"}:
            return value.id
    return "assertion"


def _module_exists(
    repository_fd: int, source_roots: tuple[tuple[str, ...], ...], module: str
) -> bool:
    module_parts = tuple(part for part in module.split(".") if part)
    if not module_parts:
        return True
    for source_root in source_roots:
        parent_parts = (*source_root, *module_parts[:-1])
        parent = -1
        try:
            parent = _descend(repository_fd, parent_parts)
            leaf = module_parts[-1]
            for candidate in (leaf, f"{leaf}.py"):
                try:
                    info = os.stat(candidate, dir_fd=parent, follow_symlinks=False)
                except OSError:
                    continue
                if not stat.S_ISLNK(info.st_mode) and (
                    stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)
                ):
                    return True
        except (OSError, RecoveryInventoryError):
            pass
        finally:
            if parent >= 0:
                os.close(parent)
    return False


def _has_unresolved_import(
    tree: ast.Module,
    repository_fd: int,
    source_roots: tuple[tuple[str, ...], ...],
) -> bool:
    for node in _iter_ast_nodes(tree):
        modules: list[str] = []
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                return True
            if node.module:
                modules.append(node.module)
        for module in modules:
            root = module.split(".", 1)[0]
            if root in sys.stdlib_module_names:
                continue
            if not _module_exists(repository_fd, source_roots, module):
                return True
    return False


def _first_nonempty_line(data: bytes) -> tuple[int, bytes]:
    for index, line in enumerate(data.splitlines(keepends=True), start=1):
        if line.strip():
            return index, line
    return 1, b""


def _structured_values(
    value: Any,
    prefix: tuple[str | int, ...] = (),
) -> tuple[list[tuple[tuple[str | int, ...], Any]], list[tuple[tuple[str | int, ...], Any]]]:
    collections: list[tuple[tuple[str | int, ...], Any]] = []
    scalars: list[tuple[tuple[str | int, ...], Any]] = []
    pending: list[tuple[tuple[str | int, ...], Any]] = [(prefix, value)]
    while pending:
        current_prefix, current = pending.pop()
        if isinstance(current, dict):
            if not current and current_prefix:
                collections.append((current_prefix, current))
            for key in sorted(current, key=lambda item: str(item), reverse=True):
                pending.append(((*current_prefix, str(key)), current[key]))
        elif isinstance(current, list):
            if current_prefix:
                collections.append((current_prefix, current))
        elif current_prefix:
            scalars.append((current_prefix, current))
    return collections, scalars


def _validate_structured_data(value: Any) -> None:
    pending: list[tuple[Any, int]] = [(value, 0)]
    seen: set[int] = set()
    observations = 0
    while pending:
        current, depth = pending.pop()
        observations += 1
        if observations > MAX_STRUCTURE_NODES:
            raise ValueError("structured input exceeds the observation cap")
        if depth > MAX_DEPTH:
            raise ValueError("structured input exceeds the nesting cap")
        if isinstance(current, dict):
            identity = id(current)
            if identity in seen:
                raise ValueError("structured aliases or cycles are unsupported")
            seen.add(identity)
            if any(not isinstance(key, str) for key in current):
                raise ValueError("structured mapping keys must be strings")
            pending.extend((item, depth + 1) for item in current.values())
        elif isinstance(current, list):
            identity = id(current)
            if identity in seen:
                raise ValueError("structured aliases or cycles are unsupported")
            seen.add(identity)
            pending.extend((item, depth + 1) for item in current)
        elif isinstance(current, float) and not math.isfinite(current):
            raise ValueError("non-finite structured numbers are unsupported")
        elif current is not None and not isinstance(current, (str, int, float, bool)):
            raise ValueError(f"unsupported structured scalar {type(current).__name__}")


def _load_yaml_static(text: str) -> Any:
    for token_count, token in enumerate(_YAML.scan(text), start=1):
        if token_count > MAX_YAML_TOKENS:
            raise ValueError("YAML input exceeds the token cap")
        if isinstance(token, (AliasToken, AnchorToken)):
            raise TypeError("YAML aliases and anchors are unsupported")
    loaded = _YAML.load(text)
    _validate_structured_data(loaded)
    return loaded


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant {value!r} is unsupported")


def _first_addressable_value(value: Any) -> tuple[tuple[str | int, ...], Any]:
    collections, scalars = _structured_values(value)
    candidates = collections or scalars
    return candidates[0] if candidates else ((), value)


def _meaningful_doc_line(data: bytes) -> tuple[int, bytes]:
    fallback = _first_nonempty_line(data)
    for index, line in enumerate(data.splitlines(keepends=True), start=1):
        stripped = line.strip()
        if stripped and not stripped.startswith(b"#"):
            return index, line
    return fallback


def _singular_label(value: str) -> str:
    lowered = value.lower()
    if lowered.endswith("ses"):
        return value[:-2]
    if lowered.endswith("s") and not lowered.endswith(("is", "ss", "us")):
        return value[:-1]
    return value


def _json_pointer(parts: tuple[str | int, ...]) -> str:
    encoded = [str(part).replace("~", "~0").replace("/", "~1") for part in parts]
    return "" if not encoded else "/" + "/".join(encoded)


def _default_exclusion(path_parts: tuple[str, ...]) -> tuple[str, str] | None:
    for part in path_parts:
        if part in _DEFAULT_EXCLUSIONS:
            return part, _DEFAULT_EXCLUSIONS[part]
    return None


def scan_recovery_scope(
    repository_root: str | Path,
    selected_roots: tuple[SelectedRoot, ...] | list[SelectedRoot],
    *,
    excluded_roots: tuple[ExcludedRoot, ...] | list[ExcludedRoot] = (),
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    max_files: int = DEFAULT_MAX_FILES,
    expected_root_identity: tuple[int, int] | None = None,
    require_controller_reservations: bool = False,
) -> RecoveryInventory:
    """Inventory explicit roots as inert bytes and closed static observations."""

    if min(max_file_bytes, max_total_bytes, max_files) <= 0:
        raise RecoveryInventoryError("recovery inventory limits must be positive")
    roots = tuple(
        item if isinstance(item, SelectedRoot) else SelectedRoot.model_validate(item)
        for item in selected_roots
    )
    if not roots:
        raise RecoveryInventoryError("at least one selected recovery root is required")
    explicit_exclusions = tuple(
        item if isinstance(item, ExcludedRoot) else ExcludedRoot.model_validate(item)
        for item in excluded_roots
    )
    if len({entry.path for entry in explicit_exclusions}) != len(explicit_exclusions):
        raise RecoveryInventoryError("explicit exclusion paths must be unique")
    if len({entry.exclusion_id for entry in explicit_exclusions}) != len(explicit_exclusions):
        raise RecoveryInventoryError("explicit exclusion identifiers must be unique")
    _validate_controller_reservation_set(
        roots,
        explicit_exclusions,
        required_for_bundle=require_controller_reservations,
    )

    root_parts = [(root, _safe_relative(root.path, field="selected root")) for root in roots]
    ordered_paths = sorted(parts for _, parts in root_parts)
    for index, parts in enumerate(ordered_paths):
        for other in ordered_paths[index + 1 :]:
            if other[: len(parts)] == parts:
                raise RecoveryInventoryError("selected recovery roots must not overlap")

    explicit_parts = tuple(
        (entry, _safe_relative(entry.path, field="excluded root"))
        for entry in explicit_exclusions
    )
    for entry, parts in explicit_parts:
        containing = [
            selected_parts
            for _selected, selected_parts in root_parts
            if parts[: len(selected_parts)] == selected_parts
        ]
        if len(containing) != 1 or parts == containing[0]:
            raise RecoveryInventoryError(
                f"explicit exclusion {entry.path} must be strictly beneath one selected root"
            )

    repository_fd, absolute_root = _open_real_directory(Path(repository_root))
    if expected_root_identity is not None:
        bound = os.fstat(repository_fd)
        if (bound.st_dev, bound.st_ino) != expected_root_identity:
            os.close(repository_fd)
            raise RecoveryInventoryError(
                "repository root identity differs from the caller's retained authority"
            )
    evidence: list[EvidenceRecord] = []
    frontier: list[FrontierItem] = []
    census: list[CensusEntry] = []
    actual_exclusions: dict[str, ExcludedRoot] = {}
    proposal_evidence: dict[str, list[str]] = defaultdict(list)
    pending_ambiguous_paths: dict[str, set[str]] = defaultdict(set)
    used_evidence_ids: set[str] = set()
    used_frontier_ids: set[str] = set()
    used_exclusion_ids: set[str] = set()
    visited_directories: set[tuple[int, int]] = set()
    total_bytes = 0
    file_count = 0
    path_observations = 0
    source_roots = tuple(
        parts for root, parts in root_parts if root.category == RootCategory.source
    )

    explicit_by_path = {entry.path: entry for entry in explicit_exclusions}

    def exclusion_for(path: str) -> tuple[str, str] | None:
        for excluded_path, entry in explicit_by_path.items():
            if path == excluded_path or path.startswith(f"{excluded_path}/"):
                return entry.exclusion_id, str(entry.reason)
        default = _default_exclusion(PurePosixPath(path).parts)
        if default is None:
            return None
        marker, reason = default
        return f"exclusion:{_slug(marker)}", reason

    def add_exclusion(path: str, base_identifier: str, reason: str) -> None:
        identifier = base_identifier
        existing = actual_exclusions.get(path)
        if existing is not None:
            return
        if identifier in used_exclusion_ids:
            identifier = f"{identifier}-{sha256_hex(path.encode())[:8]}"
        used_exclusion_ids.add(identifier)
        entry = ExcludedRoot(exclusion_id=identifier, path=path, reason=reason)
        actual_exclusions[path] = entry
        census.append(CensusEntry(path=path, disposition="excluded", reference_ids=(identifier,)))

    def add_frontier(path: str, reason: str, digest: str | None, detail: str) -> None:
        identifier = _frontier_id(path, reason)
        if identifier in used_frontier_ids:
            identifier = f"{identifier}-{sha256_hex(path.encode())[:8]}"
        used_frontier_ids.add(identifier)
        frontier.append(
            FrontierItem(
                frontier_id=identifier,
                path=path,
                reason=reason,
                sha256=digest,
                detail=detail,
            )
        )
        census.append(CensusEntry(path=path, disposition="frontier", reference_ids=(identifier,)))

    # Only deterministic controller reservations are prospective declarations.
    # User exclusions remain observations: if they disappear before traversal,
    # they are omitted and the CLI's post-scan gate refuses publication.
    for explicit in explicit_exclusions:
        if _controller_reservation_role(explicit) is not None:
            add_exclusion(explicit.path, explicit.exclusion_id, str(explicit.reason))

    def add_evidence(
        path: str,
        data: bytes,
        *,
        label: str,
        kind: str,
        media_type: str,
        locator: Any,
        excerpt: bytes,
    ) -> str:
        identifier = _evidence_id(path, label, kind, used_evidence_ids)
        evidence.append(
            EvidenceRecord(
                evidence_id=identifier,
                path=path,
                sha256=sha256_hex(data),
                byte_length=len(data),
                media_type=media_type,
                encoding="utf-8",
                locator=locator,
                excerpt_sha256=sha256_hex(excerpt),
            )
        )
        return identifier

    def classify_file(
        path: str,
        data: bytes,
        category: RootCategory,
    ) -> tuple[str, tuple[str, ...]]:
        digest = sha256_hex(data)
        if len(evidence) >= MAX_OBSERVATIONS:
            add_frontier(
                path,
                "aggregate-limit",
                digest,
                "recovery evidence exceeds the aggregate observation cap",
            )
            return "handled", ()
        if b"\x00" in data:
            add_frontier(path, "binary", digest, "selected file contains a NUL byte")
            return "handled", ()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            add_frontier(path, "binary", digest, "selected file is not UTF-8 text")
            return "handled", ()

        suffix = PurePosixPath(path).suffix.lower()
        media_type = _MEDIA_TYPES.get(suffix, "application/octet-stream")
        if path.endswith(".schema.json"):
            media_type = "application/schema+json"

        tree: ast.Module | None = None
        structured: Any = None
        if suffix == ".py":
            if re.search(_MIXED_MARKER, text, re.IGNORECASE):
                add_frontier(
                    path,
                    "mixed-language",
                    digest,
                    "selected file declares mixed embedded languages",
                )
                return "handled", ()
            try:
                tree = ast.parse(text, filename=path)
            except (SyntaxError, ValueError) as error:
                add_frontier(
                    path,
                    "parse-error",
                    digest,
                    f"Python syntax could not be parsed: {type(error).__name__}",
                )
                return "handled", ()
            if sum(1 for _, _node in zip(range(MAX_STRUCTURE_NODES + 1), _iter_ast_nodes(tree))) > (
                MAX_STRUCTURE_NODES
            ):
                add_frontier(
                    path,
                    "parse-error",
                    digest,
                    "Python syntax exceeds the static observation cap",
                )
                return "handled", ()
            if _has_dynamic_construct(tree):
                add_frontier(
                    path,
                    "dynamic-construct",
                    digest,
                    "dynamic namespace construction cannot be recovered statically",
                )
                return "handled", ()
            if _has_unresolved_import(tree, repository_fd, source_roots):
                add_frontier(
                    path,
                    "unresolved-import",
                    digest,
                    "an imported project module cannot be resolved statically in the selected source roots",
                )
                return "handled", ()
        elif suffix in {".yaml", ".yml"}:
            try:
                structured = _load_yaml_static(text)
            except (OverflowError, RecursionError, TypeError, ValueError, YAMLError) as error:
                add_frontier(
                    path, "parse-error", digest, f"YAML could not be parsed: {type(error).__name__}"
                )
                return "handled", ()
        elif suffix == ".json":
            try:
                structured = _rf7_input.loads(text, parse_constant=_reject_json_constant)
                _validate_structured_data(structured)
            except (
                json.JSONDecodeError,
                OverflowError,
                RecursionError,
                TypeError,
                ValueError,
            ) as error:
                add_frontier(
                    path, "parse-error", digest, f"JSON could not be parsed: {type(error).__name__}"
                )
                return "handled", ()
        elif suffix in {".md", ".rst", ".txt"} or (
            suffix == ".sql" and re.search(_DDL, text, re.IGNORECASE | re.MULTILINE)
        ):
            pass
        else:
            add_frontier(
                path,
                "unsupported-language",
                digest,
                "selected file format is outside the conservative static parser set",
            )
            return "handled", ()

        marker_rows: dict[str, tuple[int, bytes]] = {}
        for line_number, line in enumerate(data.splitlines(keepends=True), start=1):
            try:
                decoded_line = line.decode("utf-8")
            except UnicodeDecodeError:
                continue
            for match in re.finditer(_PROPOSAL_MARKER, decoded_line, re.IGNORECASE):
                claim = match.group("claim").strip()
                marker_rows.setdefault(claim, (line_number, line))
        new_marker_count = sum(claim not in proposal_evidence for claim in marker_rows)
        if len(proposal_evidence) + new_marker_count > MAX_OBSERVATIONS:
            add_frontier(
                path,
                "aggregate-limit",
                digest,
                "semantic proposal markers exceed the aggregate observation cap",
            )
            return "handled", ()

        refs: list[str] = []
        if tree is not None:
            observations = _python_symbols(tree)
            if len(observations) > MAX_OBSERVATIONS or (
                len(evidence) + len(observations) > MAX_OBSERVATIONS
            ):
                add_frontier(
                    path,
                    "parse-error",
                    digest,
                    "Python declarations exceed the observation cap",
                )
                return "handled", ()
            symbol_counts = Counter(symbol for symbol, _node, _kind in observations)
            for symbol, node, observation_kind in observations:
                start = int(getattr(node, "lineno", 1))
                end = int(getattr(node, "end_lineno", start))
                label = symbol.split(".", 1)[0]
                if observation_kind == "test" and symbol.startswith("test_"):
                    label = symbol.removeprefix("test_").split("_", 1)[0]
                elif observation_kind == "assertion" and isinstance(node, ast.Assert):
                    label = _assertion_label(node)
                refs.append(
                    add_evidence(
                        path,
                        data,
                        label=label,
                        kind=observation_kind,
                        media_type=media_type,
                        locator=(
                            LineLocator(kind="line", line_start=start, line_end=end)
                            if observation_kind == "assertion" or symbol_counts[symbol] > 1
                            else PythonSymbolLocator(
                                kind="python-symbol",
                                symbol=symbol,
                                line_start=start,
                                line_end=end,
                            )
                        ),
                        excerpt=_line_bytes(data, start, end),
                    )
                )
        elif suffix in {".md", ".rst", ".txt"}:
            if marker_rows:
                line_number = 1
                line_end = max(1, len(data.splitlines()))
                line = data
                label = PurePosixPath(path).stem.split(".", 1)[0]
            else:
                line_number, line = _meaningful_doc_line(data)
                line_end = line_number
                words = re.findall(r"[A-Za-z][A-Za-z0-9_]*", line.decode("utf-8"))
                label = next(
                    (word for word in words if word.lower() not in {"a", "an", "the"}),
                    PurePosixPath(path).stem.split(".", 1)[0],
                )
            refs.append(
                add_evidence(
                    path,
                    data,
                    label=label,
                    kind="doc",
                    media_type=media_type,
                    locator=LineLocator(kind="line", line_start=line_number, line_end=line_end),
                    excerpt=line,
                )
            )
        elif suffix in {".yaml", ".yml"}:
            yaml_path, value = _first_addressable_value(structured)
            label = _singular_label(str(yaml_path[-1] if yaml_path else PurePosixPath(path).stem))
            if yaml_path:
                locator: Any = YamlPathLocator(kind="yaml-path", path=yaml_path)
                excerpt = canonical_json_text(value).encode("utf-8")
            else:
                line_number, excerpt = _first_nonempty_line(data)
                locator = LineLocator(kind="line", line_start=line_number, line_end=line_number)
            refs.append(
                add_evidence(
                    path,
                    data,
                    label=label,
                    kind="config",
                    media_type=media_type,
                    locator=locator,
                    excerpt=excerpt,
                )
            )
        elif suffix == ".json":
            pointer_parts, value = _first_addressable_value(structured)
            label = PurePosixPath(path).name.split(".", 1)[0]
            if "$defs" in pointer_parts:
                definition_index = pointer_parts.index("$defs") + 1
                if definition_index < len(pointer_parts):
                    label = str(pointer_parts[definition_index])
            if pointer_parts:
                locator = JsonPointerLocator(
                    kind="json-pointer", pointer=_json_pointer(pointer_parts)
                )
                excerpt = canonical_json_text(value).encode("utf-8")
            else:
                line_number, excerpt = _first_nonempty_line(data)
                locator = LineLocator(kind="line", line_start=line_number, line_end=line_number)
            refs.append(
                add_evidence(
                    path,
                    data,
                    label=label,
                    kind="schema" if media_type == "application/schema+json" else "config",
                    media_type=media_type,
                    locator=locator,
                    excerpt=excerpt,
                )
            )
        elif suffix == ".sql" and re.search(_DDL, text, re.IGNORECASE | re.MULTILINE):
            line_number, line = _first_nonempty_line(data)
            refs.append(
                add_evidence(
                    path,
                    data,
                    label=PurePosixPath(path).stem,
                    kind="ddl",
                    media_type=media_type,
                    locator=LineLocator(kind="line", line_start=line_number, line_end=line_number),
                    excerpt=line,
                )
            )
        if not refs:
            if marker_rows:
                _, (line_number, line) = min(marker_rows.items())
            else:
                line_number, line = _first_nonempty_line(data)
            refs.append(
                add_evidence(
                    path,
                    data,
                    label=PurePosixPath(path).stem,
                    kind="declaration",
                    media_type=media_type,
                    locator=LineLocator(kind="line", line_start=line_number, line_end=line_number),
                    excerpt=line,
                )
            )
        if marker_rows:
            for claim in sorted(marker_rows):
                proposal_evidence[claim].extend(refs)
                pending_ambiguous_paths[path].add(claim)
            return "ambiguous", tuple(sorted(refs))
        return "parsed", tuple(sorted(refs))

    def walk(
        directory_fd: int,
        prefix: tuple[str, ...],
        category: RootCategory,
        depth: int,
    ) -> None:
        nonlocal total_bytes, file_count, path_observations
        if depth > MAX_DEPTH:
            raise RecoveryInventoryError(
                f"selected directory {'/'.join(prefix)} exceeds the depth cap"
            )
        identity = os.fstat(directory_fd)
        key = (identity.st_dev, identity.st_ino)
        if key in visited_directories:
            raise RecoveryInventoryError(
                f"selected directory {'/'.join(prefix)} repeats a directory identity"
            )
        visited_directories.add(key)
        if len(visited_directories) > MAX_DIRECTORIES:
            raise RecoveryInventoryError(
                f"recovery inventory exceeds the {MAX_DIRECTORIES}-directory cap"
            )
        try:
            names: list[str] = []
            with os.scandir(directory_fd) as entries:
                for entry in entries:
                    names.append(entry.name)
                    if len(names) > MAX_OBSERVATIONS:
                        raise RecoveryInventoryError(
                            "selected directory exceeds the entry observation cap"
                        )
            names.sort()
        except OSError as error:
            raise RecoveryInventoryError(
                f"selected directory {'/'.join(prefix)} could not be listed: {error}"
            ) from error
        for name in names:
            path_observations += 1
            if path_observations > MAX_OBSERVATIONS:
                raise RecoveryInventoryError(
                    "recovery inventory exceeds the selected-path observation cap"
                )
            path_parts = (*prefix, name)
            relative = PurePosixPath(*path_parts).as_posix()
            try:
                before = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            except OSError as error:
                raise RecoveryInventoryError(
                    f"selected path {relative} could not be inspected: {error}"
                ) from error
            excluded = exclusion_for(relative)
            explicit_entry = explicit_by_path.get(relative)
            controller_role = (
                _controller_reservation_role(explicit_entry)
                if explicit_entry is not None
                else None
            )
            if controller_role is not None and not stat.S_ISREG(before.st_mode):
                raise RecoveryInventoryError(
                    f"controller {controller_role} reservation {relative} "
                    "must be absent or a regular file"
                )
            if stat.S_ISLNK(before.st_mode):
                if excluded is not None:
                    exclusion_id, reason = excluded
                    add_exclusion(relative, exclusion_id, reason)
                    continue
                file_count += 1
                if file_count > max_files:
                    add_frontier(
                        relative,
                        "file-limit",
                        None,
                        "selected symlink exceeds the configured file-count budget",
                    )
                    continue
                try:
                    target = os.readlink(name, dir_fd=directory_fd)
                except OSError:
                    target = ""
                target_bytes = os.fsencode(target)
                reason = (
                    "symlink-cycle"
                    if target in {".", ".."} or target.startswith("../")
                    else "symlink"
                )
                add_frontier(
                    relative,
                    reason,
                    sha256_hex(target_bytes),
                    "selected symlink was recorded but never followed",
                )
                continue
            if stat.S_ISDIR(before.st_mode):
                if excluded is not None:
                    exclusion_id, reason = excluded
                    add_exclusion(relative, exclusion_id, reason)
                    continue
                child = _open_child_directory(directory_fd, name, before)
                try:
                    walk(child, path_parts, category, depth + 1)
                finally:
                    os.close(child)
                continue
            if not stat.S_ISREG(before.st_mode):
                file_count += 1
                if file_count > max_files:
                    add_frontier(
                        relative,
                        "file-limit",
                        None,
                        "selected path exceeds the configured file-count budget",
                    )
                    continue
                add_frontier(relative, "binary", None, "selected path is not a regular file")
                continue

            if excluded is not None:
                exclusion_id, reason = excluded
                add_exclusion(relative, exclusion_id, reason)
                continue
            file_count += 1
            if file_count > max_files:
                add_frontier(
                    relative,
                    "file-limit",
                    None,
                    "selected file exceeds the configured file-count budget",
                )
                continue
            if before.st_size > max_file_bytes:
                add_frontier(
                    relative,
                    "oversize",
                    None,
                    "selected file exceeds the configured byte budget and was not read",
                )
                continue
            if total_bytes + before.st_size > max_total_bytes:
                add_frontier(
                    relative,
                    "aggregate-limit",
                    None,
                    "selected file exceeds the remaining aggregate byte budget",
                )
                continue
            data = _read_regular(
                directory_fd,
                name,
                relative=relative,
                before=before,
                cap=min(max_file_bytes, max_total_bytes - total_bytes),
            )
            if total_bytes + len(data) > max_total_bytes:
                raise RecoveryInventoryError(
                    f"selected file {relative} exceeds the remaining aggregate byte budget"
                )
            total_bytes += len(data)
            disposition, refs = classify_file(relative, data, category)
            if disposition == "parsed":
                census.append(CensusEntry(path=relative, disposition="parsed", reference_ids=refs))

    try:
        for selected, parts in root_parts:
            selected_fd = _descend(repository_fd, parts)
            try:
                walk(selected_fd, parts, selected.category, 0)
            finally:
                os.close(selected_fd)
    finally:
        os.close(repository_fd)

    ambiguities: list[AmbiguousProposal] = []
    proposal_ids: dict[str, str] = {}
    used_proposal_ids: set[str] = set()
    for claim in sorted(proposal_evidence):
        slug = _slug(claim)
        base_proposal_id = f"proposal:{slug}"
        proposal_id = base_proposal_id
        if proposal_id in used_proposal_ids:
            suffix = sha256_hex(claim.encode("utf-8"))[:8]
            proposal_id = f"{base_proposal_id}-{suffix}"
            ordinal = 2
            while proposal_id in used_proposal_ids:
                proposal_id = f"{base_proposal_id}-{suffix}-{ordinal}"
                ordinal += 1
        used_proposal_ids.add(proposal_id)
        proposal_ids[claim] = proposal_id
        ambiguities.append(
            AmbiguousProposal(
                proposal_id=proposal_id,
                element_id=f"fact:{slug}",
                element_kind="fact-type",
                source="llm-inferred",
                status="proposed",
                modality="deontic",
                rationale=(
                    "A repository naming/documentation hint is semantic evidence, not a "
                    "mechanically declared invariant; owner review is required."
                ),
                evidence_ids=tuple(sorted(proposal_evidence[claim])),
                prior_proposal_id=None,
            )
        )
    for path in sorted(pending_ambiguous_paths):
        references = tuple(sorted(proposal_ids[claim] for claim in pending_ambiguous_paths[path]))
        census.append(CensusEntry(path=path, disposition="ambiguous", reference_ids=references))

    scope = RecoveryScope(
        repository_root=str(absolute_root),
        selected_roots=roots,
        excluded_roots=tuple(actual_exclusions[path] for path in sorted(actual_exclusions)),
        max_file_bytes=max_file_bytes,
        max_total_bytes=max_total_bytes,
        max_files=max_files,
    )
    return RecoveryInventory(
        scope=scope,
        evidence=tuple(sorted(evidence, key=lambda item: (item.path, item.evidence_id))),
        ambiguities=tuple(sorted(ambiguities, key=lambda item: item.proposal_id)),
        frontier=tuple(sorted(frontier, key=lambda item: (item.path, item.frontier_id))),
        census=tuple(sorted(census, key=lambda item: item.path)),
    )
