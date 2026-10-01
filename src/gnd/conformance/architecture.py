"""Assertion #4 -- do authored architecture declarations match static reality?

The assertion never imports or executes the generated project. It reads one
loader-valid architecture contract, builds one unique source roster, parses each
regular source at most once, and uses the shared structural source observer for
effective module bindings and whole-AST string/path observations.

Artifact-path recognition is deliberately closed. Supported pathlib forms begin
at ``Path(__file__)``, admit one lexical ``resolve()`` and repeated ``parent`` /
literal joins. Supported os.path forms use nested ``dirname(__file__)`` anchors
and ``join`` with literal components. Variables, aliases, f-strings, computed
components, escapes above the project root, package inference and cross-module
indirection are not guessed.
"""

from __future__ import annotations

import ast
import keyword
import os
import stat
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

from gnd.architecture import (
    ARCHITECTURE_CONTRACT_FILENAME,
    ArchitectureContract,
    ArchitectureContractError,
    ArchitectureContractNotFoundError,
    parse_architecture_contract_bytes,
    read_architecture_contract_bytes,
)
from gnd.artifacts import (
    ArtifactError,
    ArtifactIdentityError,
    read_regular_bounded_at,
    stat_leaf_at,
)
from gnd.codegen.manifest import CodegenManifest
from gnd.conformance import ConformanceError, Finding, FindingKind
from gnd.conformance.integrity import MAX_CONFORMANCE_BYTES, open_project_root
from gnd.conformance.structural import (
    SourceObservation,
    SourceObservationError,
    observe_source_bytes,
)

__all__ = [
    "MAX_ARCHITECTURE_SOURCES",
    "MAX_ARCHITECTURE_SOURCE_BYTES",
    "ArchitectureContractBinding",
    "ArchitectureDeclaredCounts",
    "ArchitectureResult",
    "check_architecture",
]

MAX_ARCHITECTURE_SOURCES = 1_024
MAX_ARCHITECTURE_SOURCE_BYTES = 64 * 1024 * 1024


@dataclass(frozen=True)
class ArchitectureContractBinding:
    relpath: str
    sha256: str


@dataclass(frozen=True)
class ArchitectureDeclaredCounts:
    modules: int
    symbols: int
    artifacts: int
    artifact_requirements: int
    entry_points: int
    smoke_rows: int


@dataclass(frozen=True)
class ArchitectureResult:
    findings: tuple[Finding, ...] = ()
    contract: ArchitectureContractBinding | None = None
    declared: ArchitectureDeclaredCounts | None = None
    scanned: tuple[str, ...] = ()
    contract_absent: bool = False


@dataclass
class _SourceRoles:
    module: bool = False
    requirement: bool = False
    entry_modules: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class _SourceState:
    info: os.stat_result | None
    reason: str | None = None


@dataclass(frozen=True)
class _LexicalPath:
    parts: tuple[str, ...]
    escaped: bool = False

    def parent(self) -> _LexicalPath:
        if self.escaped or not self.parts:
            return _LexicalPath((), escaped=True)
        return _LexicalPath(self.parts[:-1])

    def join(self, value: str) -> _LexicalPath:
        if self.escaped or "\\" in value:
            return _LexicalPath((), escaped=True)
        path = PurePosixPath(value)
        if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
            return _LexicalPath((), escaped=True)
        return _LexicalPath((*self.parts, *path.parts))

    def render(self) -> str | None:
        if self.escaped:
            return None
        return PurePosixPath(*self.parts).as_posix() if self.parts else "."


def _finding(kind: FindingKind, target: str, message: str) -> Finding:
    return Finding(kind=kind, target=target, message=message)


def _declared_counts(contract: ArchitectureContract) -> ArchitectureDeclaredCounts:
    return ArchitectureDeclaredCounts(
        modules=len(contract.modules),
        symbols=sum(len(module.symbols) for module in contract.modules),
        artifacts=len(contract.artifacts),
        artifact_requirements=sum(len(artifact.required_by) for artifact in contract.artifacts),
        entry_points=len(contract.entry_points),
        smoke_rows=len(contract.smoke),
    )


def _manifest_lists_contract(manifest: CodegenManifest | None) -> bool:
    return manifest is not None and ARCHITECTURE_CONTRACT_FILENAME in manifest.entries()


def _entry_relpath(module: str) -> str | None:
    parts = module.split(".")
    if not parts or any(
        not part or not part.isidentifier() or keyword.iskeyword(part) for part in parts
    ):
        return None
    return PurePosixPath(*parts).with_suffix(".py").as_posix()


def _source_roster(
    contract: ArchitectureContract,
) -> tuple[dict[str, _SourceRoles], dict[str, str | None]]:
    roster: dict[str, _SourceRoles] = {}
    entry_paths: dict[str, str | None] = {}
    for module in contract.modules:
        roster.setdefault(module.path, _SourceRoles()).module = True
    for artifact in contract.artifacts:
        for required_by in artifact.required_by:
            roster.setdefault(required_by, _SourceRoles()).requirement = True
    for entry in contract.entry_points:
        relpath = _entry_relpath(entry.module)
        entry_paths[entry.module] = relpath
        if relpath is not None:
            roster.setdefault(relpath, _SourceRoles()).entry_modules.append(entry.module)
    return roster, entry_paths


def _artifact_error_reason(error: ArtifactError) -> str:
    message = str(error)
    cause: BaseException | None = error
    while cause is not None:
        if isinstance(cause, FileNotFoundError):
            return "missing"
        cause = cause.__cause__
    if "directory component" in message and "symlink" in message:
        return "symlinked ancestor"
    if "symlink" in message:
        return "symlink"
    if "not a directory" in message:
        return "non-regular ancestor"
    if "changed" in message or "Bad file descriptor" in message:
        raise ConformanceError(
            "architecture source directory changed during observation "
            "(cause: architecture-directory-race)"
        ) from error
    raise ConformanceError(
        "architecture source or artifact could not be statted "
        "(cause: architecture-stat-io)"
    ) from error


def _stat_source(root_fd: int, relpath: str) -> _SourceState:
    try:
        info = stat_leaf_at(root_fd, relpath)
    except ArtifactError as error:
        return _SourceState(None, _artifact_error_reason(error))
    if stat.S_ISLNK(info.st_mode):
        return _SourceState(info, "symlink")
    if not stat.S_ISREG(info.st_mode):
        return _SourceState(info, "not a regular file")
    return _SourceState(info)


def _missing_role_findings(
    relpath: str,
    roles: _SourceRoles,
    reason: str,
) -> list[Finding]:
    findings: list[Finding] = []
    if roles.module or roles.requirement:
        findings.append(
            _finding(
                "declared-module-missing",
                relpath,
                f"declared source {relpath} is unavailable: {reason}",
            )
        )
    for module in roles.entry_modules:
        findings.append(
            _finding(
                "entry-point-module-missing",
                module,
                f"entry point {module} resolves to {relpath}, which is unavailable: {reason}",
            )
        )
    return findings


def _is_name(node: ast.AST, *parts: str) -> bool:
    current: ast.AST = node
    for part in reversed(parts[1:]):
        if not isinstance(current, ast.Attribute) or current.attr != part:
            return False
        current = current.value
    return isinstance(current, ast.Name) and current.id == parts[0]


def _literal(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _pathlib_path(node: ast.AST, source_relpath: str) -> _LexicalPath | None:
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "Path"
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Name)
        and node.args[0].id == "__file__"
        and not node.keywords
    ):
        return _LexicalPath(PurePosixPath(source_relpath).parts)
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "resolve"
        and not node.args
        and not node.keywords
    ):
        return _pathlib_path(node.func.value, source_relpath)
    if isinstance(node, ast.Attribute) and node.attr == "parent":
        base = _pathlib_path(node.value, source_relpath)
        return None if base is None else base.parent()
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        base = _pathlib_path(node.left, source_relpath)
        literal = _literal(node.right)
        return None if base is None or literal is None else base.join(literal)
    return None


def _os_path(node: ast.AST, source_relpath: str) -> _LexicalPath | None:
    if isinstance(node, ast.Name) and node.id == "__file__":
        return _LexicalPath(PurePosixPath(source_relpath).parts)
    if (
        isinstance(node, ast.Call)
        and _is_name(node.func, "os", "path", "dirname")
        and len(node.args) == 1
        and not node.keywords
    ):
        base = _os_path(node.args[0], source_relpath)
        return None if base is None else base.parent()
    if (
        isinstance(node, ast.Call)
        and _is_name(node.func, "os", "path", "join")
        and len(node.args) >= 2
        and not node.keywords
    ):
        base = _os_path(node.args[0], source_relpath)
        if base is None:
            return None
        for argument in node.args[1:]:
            literal = _literal(argument)
            if literal is None:
                return None
            base = base.join(literal)
        return base
    return None


def _resolved_expression(node: ast.expr, source_relpath: str) -> str | None:
    resolved = _pathlib_path(node, source_relpath)
    if resolved is None:
        resolved = _os_path(node, source_relpath)
    return None if resolved is None else resolved.render()


def _read_contract(
    project_root: str | Path,
    manifest: CodegenManifest | None,
    *,
    root_fd: int,
) -> ArchitectureResult | tuple[ArchitectureContract, ArchitectureContractBinding]:
    try:
        data, snapshot = read_architecture_contract_bytes(project_root, root_fd=root_fd)
    except ArchitectureContractNotFoundError:
        if _manifest_lists_contract(manifest):
            return ArchitectureResult(
                findings=(
                    _finding(
                        "contract-missing",
                        ARCHITECTURE_CONTRACT_FILENAME,
                        "manifest lists architecture.contract.yaml but the contract is missing",
                    ),
                )
            )
        return ArchitectureResult(contract_absent=True)
    except ArchitectureContractError as error:
        if isinstance(error.__cause__, OSError):
            raise ConformanceError(
                "architecture contract could not be read through the retained "
                "project descriptor (cause: architecture-descriptor)"
            ) from error
        return ArchitectureResult(
            findings=(
                _finding(
                    "contract-unreadable",
                    ARCHITECTURE_CONTRACT_FILENAME,
                    f"architecture contract could not be read: {error}",
                ),
            )
        )

    binding = ArchitectureContractBinding(
        relpath=ARCHITECTURE_CONTRACT_FILENAME,
        sha256=snapshot.sha256,
    )
    try:
        contract = parse_architecture_contract_bytes(
            data,
            source=ARCHITECTURE_CONTRACT_FILENAME,
        )
    except ArchitectureContractError as error:
        return ArchitectureResult(
            findings=(
                _finding(
                    "contract-unreadable",
                    ARCHITECTURE_CONTRACT_FILENAME,
                    f"architecture contract is invalid: {error}",
                ),
            ),
            contract=binding,
            scanned=(ARCHITECTURE_CONTRACT_FILENAME,),
        )
    return contract, binding


def check_architecture(
    model: Any,
    project_root: str | Path,
    manifest: CodegenManifest | None = None,
    *,
    model_path: str | Path,
    root_fd: int | None = None,
) -> ArchitectureResult:
    """Statically compare one architecture contract to its declared project tree."""

    del model_path  # the callable retains the assertion-family common signature
    owned_root_fd = root_fd is None
    retained_root_fd = open_project_root(project_root) if root_fd is None else root_fd
    try:
        loaded = _read_contract(project_root, manifest, root_fd=retained_root_fd)
        if isinstance(loaded, ArchitectureResult):
            return loaded
        contract, binding = loaded
        declared = _declared_counts(contract)
        scanned: set[str] = {ARCHITECTURE_CONTRACT_FILENAME}
        findings: list[Finding] = []

        roster, entry_paths = _source_roster(contract)
        if len(roster) > MAX_ARCHITECTURE_SOURCES:
            return ArchitectureResult(
                findings=(
                    _finding(
                        "contract-unreadable",
                        ARCHITECTURE_CONTRACT_FILENAME,
                        f"unique source budget exceeds {MAX_ARCHITECTURE_SOURCES}: "
                        f"declared {len(roster)} unique sources",
                    ),
                ),
                contract=binding,
                declared=declared,
                scanned=(ARCHITECTURE_CONTRACT_FILENAME,),
            )

        states = {relpath: _stat_source(retained_root_fd, relpath) for relpath in roster}
        aggregate_bytes = sum(
            state.info.st_size
            for state in states.values()
            if state.info is not None and stat.S_ISREG(state.info.st_mode)
        )
        if aggregate_bytes > MAX_ARCHITECTURE_SOURCE_BYTES:
            return ArchitectureResult(
                findings=(
                    _finding(
                        "contract-unreadable",
                        ARCHITECTURE_CONTRACT_FILENAME,
                        f"aggregate source byte budget exceeds "
                        f"{MAX_ARCHITECTURE_SOURCE_BYTES}: observed {aggregate_bytes}",
                    ),
                ),
                contract=binding,
                declared=declared,
                scanned=(ARCHITECTURE_CONTRACT_FILENAME,),
            )

        fact_ids = {
            str(fact_type.get("id")) for fact_type in (getattr(model, "fact_types", ()) or ())
        }
        for entry in contract.entry_points:
            for side, values in (
                ("consumes", entry.consumes),
                ("produces", entry.produces),
            ):
                for fact_type_id in values:
                    if fact_type_id not in fact_ids:
                        findings.append(
                            _finding(
                                "contract-fact-type-unknown",
                                fact_type_id,
                                f"entry point {entry.module} {side} unknown fact type "
                                f"{fact_type_id}",
                            )
                        )

        observations: dict[str, SourceObservation] = {}
        remaining_source_bytes = MAX_ARCHITECTURE_SOURCE_BYTES
        for relpath, roles in roster.items():
            state = states[relpath]
            if state.reason is not None:
                findings.extend(_missing_role_findings(relpath, roles, state.reason))
                continue
            assert state.info is not None
            available_source_bytes = remaining_source_bytes
            remaining_source_bytes -= state.info.st_size
            assert remaining_source_bytes >= 0
            if state.info.st_size > MAX_CONFORMANCE_BYTES:
                findings.append(
                    _finding(
                        "unparseable-source",
                        relpath,
                        f"{relpath} exceeds the per-source cap "
                        "(cause: architecture-source-oversized)",
                    )
                )
                continue
            try:
                data, _snapshot = read_regular_bounded_at(
                    retained_root_fd,
                    relpath,
                    max_bytes=min(MAX_CONFORMANCE_BYTES, available_source_bytes),
                    expected_stat=state.info,
                )
            except ArtifactIdentityError as error:
                raise ConformanceError(
                    f"architecture source {relpath} changed after the aggregate "
                    "budget pass (cause: architecture-source-race)"
                ) from error
            except ArtifactError:
                findings.append(
                    _finding(
                        "unparseable-source",
                        relpath,
                        f"{relpath} could not be read (cause: architecture-source-read)",
                    )
                )
                continue
            scanned.add(relpath)
            try:
                observations[relpath] = observe_source_bytes(data, relpath)
            except SourceObservationError as error:
                cause = (
                    "architecture-source-decode"
                    if error.cause == "decode"
                    else "architecture-source-parse"
                )
                findings.append(
                    _finding(
                        "unparseable-source",
                        relpath,
                        f"{relpath} could not be statically parsed (cause: {cause})",
                    )
                )

        symbols_by_source = {
            relpath: {symbol.symbol: symbol for symbol in observation.symbols}
            for relpath, observation in observations.items()
        }
        strings_by_source = {
            relpath: frozenset(string.value for string in observation.strings)
            for relpath, observation in observations.items()
        }
        literal_basenames_by_source = {
            relpath: frozenset(PurePosixPath(value).name for value in values)
            for relpath, values in strings_by_source.items()
        }
        resolved_paths_by_source: dict[str, dict[str, list[tuple[str, int]]]] = {}
        for relpath, observation in observations.items():
            by_basename: dict[str, list[tuple[str, int]]] = {}
            for expression in observation.path_candidates:
                observed_path = _resolved_expression(expression, relpath)
                if observed_path is None:
                    continue
                by_basename.setdefault(PurePosixPath(observed_path).name, []).append(
                    (observed_path, expression.lineno)
                )
            resolved_paths_by_source[relpath] = by_basename

        for module in contract.modules:
            observation = observations.get(module.path)
            if observation is None:
                continue
            by_name = symbols_by_source[module.path]
            for symbol in module.symbols:
                observed = by_name.get(symbol.name)
                target = f"{module.path}:{symbol.name}"
                if observed is None:
                    findings.append(
                        _finding(
                            "declared-symbol-missing",
                            target,
                            f"{module.path} has no effective function {symbol.name}",
                        )
                    )
                elif observed.parameters != symbol.parameters:
                    findings.append(
                        _finding(
                            "symbol-shape-mismatch",
                            target,
                            f"effective function {symbol.name} in {module.path} declares "
                            f"{observed.parameters}, expected {symbol.parameters}",
                        )
                    )

        for artifact in contract.artifacts:
            artifact_state = _stat_source(retained_root_fd, artifact.path)
            if artifact_state.reason is not None:
                findings.append(
                    _finding(
                        "declared-artifact-missing",
                        artifact.path,
                        f"declared artifact {artifact.path} is unavailable: "
                        f"{artifact_state.reason}",
                    )
                )

        for artifact in contract.artifacts:
            basename = PurePosixPath(artifact.path).name
            for required_by in dict.fromkeys(artifact.required_by):
                observation = observations.get(required_by)
                if observation is None:
                    continue
                literal_found = basename in literal_basenames_by_source[required_by]
                if not literal_found:
                    findings.append(
                        _finding(
                            "artifact-reference-unfound",
                            required_by,
                            f"{required_by} has no literal basename {basename} for "
                            f"declared artifact {artifact.path}",
                        )
                    )
                for observed_path, lineno in resolved_paths_by_source[required_by].get(
                    basename, ()
                ):
                    if observed_path != artifact.path:
                        findings.append(
                            _finding(
                                "artifact-path-mismatch",
                                required_by,
                                f"{required_by} declares path {artifact.path} but observes "
                                f"{observed_path} at line {lineno}",
                            )
                        )

        for entry in contract.entry_points:
            relpath = entry_paths[entry.module]
            if relpath is None:
                findings.append(
                    _finding(
                        "entry-point-module-missing",
                        entry.module,
                        f"{entry.module} is an invalid dotted module spelling",
                    )
                )
                continue
            observation = observations.get(relpath)
            if observation is None:
                continue
            strings = strings_by_source[relpath]
            for token in entry.subcommands:
                if token not in strings:
                    findings.append(
                        _finding(
                            "entry-point-flag-unfound",
                            f"{entry.module}:{token}",
                            f"entry point {entry.module} lacks subcommand string {token}",
                        )
                    )
            for token in entry.flags:
                if token not in strings:
                    findings.append(
                        _finding(
                            "entry-point-flag-unfound",
                            f"{entry.module}:{token}",
                            f"entry point {entry.module} lacks flag string {token}",
                        )
                    )

        return ArchitectureResult(
            findings=tuple(findings),
            contract=binding,
            declared=declared,
            scanned=tuple(sorted(scanned)),
        )
    finally:
        if owned_root_fd:
            os.close(retained_root_fd)
