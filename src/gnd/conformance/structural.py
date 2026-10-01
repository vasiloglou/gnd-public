"""Assertion #3 — does the emitted surface still name the MODEL's fact types?

**This is the anti-tautology gate, and it is the only one of the three that is
not self-referential.** Assertion #1 compares a derived file against a digest the
generator wrote. Assertion #2 compares the model against a digest the generator
wrote. Both are exact, cheap and corroborating — and both are green on a project
that is 100% derived and 0% useful, because "regenerate and diff" passes whenever
codegen is deterministic, which it is by construction. A generator emitting
well-formed nothing satisfies them completely.

This module compares the **model** against the **filesystem**. Nothing it reads
was written by the generator, which is why a syntactically perfect module with no
derived tools is caught here — with one finding per model fact type, each naming
that fact type — and nowhere else (G-07; RESEARCH §2.2 case B measured 16
findings over ``full_vocabulary``).

Three stages, in RESEARCH §2.1's order:

#. :func:`expected_surface` — from the model ONLY. No manifest is read and no
   previous generation is read. A check built over the manifest is TAUTOLOGICAL:
   the generator wrote the manifest, so a generator emitting empty files with a
   correct manifest would pass (§2.3).
#. :func:`observed_surface` — by ``ast.parse`` over every ``*.py`` in the tree.
#. :func:`check_structural` — the assertion, plus the partition that gives it its
   honest scope.

Four properties are load-bearing rather than incidental.

**One published symbol mapping, never two (G-21).** The expected symbol is
:func:`gnd.codegen.identifiers.tool_symbol`, the same function
:mod:`gnd.codegen.emit` calls. Re-deriving the sanitization here would eventually
disagree with the emitter, and the disagreement would red the gate on CORRECT
output — the worst failure available, because it trains a reader to ignore the
report. Concretely: ``tests/fixtures/models/keywords.orm.yaml`` declares a fact
type ``import``; the emitter writes ``def import_(from_, return_)`` and this
module expects exactly that. RESEARCH's prototype, which re-derived ``fact_<id>``
itself, reported 7 findings over correctly generated output. That difference IS
G-21.

A Python-keyword id is therefore **not** a finding — the shared mapping handles
it, and reporting it would be reporting a hazard that was already mitigated. What
IS a finding is a keyword hazard the mapping cannot resolve: two ids that
sanitize to ONE symbol (``import`` and ``import_``). :func:`symbol_table` refuses
that model rather than merging, and the refusal arrives here as
``identifier-hazard`` rather than as a traceback.

**Module level only (T-03-34).** The walk is over ``tree.body``, never
``ast.walk``. A ``def`` nested inside a function, or inside a dead ``if False:``
branch, is not the public surface, and ``ast.walk`` would let either one satisfy a
fact type. RESEARCH Common Pitfall 6.

**The tree is never imported (T-03-30).** ``ast.parse`` is the whole mechanism.
Importing a generated module to inspect it would execute arbitrary user code on
every CI run, which is an arbitrary-code-execution gate wearing a conformance
check's clothes (ASVS V1). A ``SyntaxError`` is a FINDING, not a crash; so is a
file over :data:`~gnd.conformance.integrity.MAX_CONFORMANCE_BYTES`, which is
reported from its ``lstat`` and never read.

**Discovery is manifest-independent, but satisfaction is CLASSIFIED (G-08).**
Every ``*.py`` under the root is scanned, not just the manifest's file list —
otherwise a generator hides a missing tool simply by omitting the file from the
manifest, which is the tautology in a different costume (§2.4). Whole-tree
scanning means a hand-written EXTENSION file could satisfy a fact type; that is
not forbidden, it is REPORTED. Each satisfied fact type carries the file that
satisfied it plus that file's ownership from the plan-04 manifest, and a fact
type satisfied only outside the derived surface is a finding the payload states
rather than a silent pass. This is G-08's checked/unchecked partition applied to
assertion #3, and it is strictly stronger than either forbidding or ignoring the
case.

**Object types are corroboration, not the gate (R-07′).** Only fact types map to
a natural code symbol — a callable taking the fact type's roles. An object type
maps to a *type name* the emitted template does not declare, so an assertion over
object types would be a claim about a convention rather than about the model, and
blending it into the gate would hide which half did the work. Object-type
coverage is therefore recorded as :attr:`StructuralResult.object_types` and never
produces a finding. R-07′'s rule is that the primary gate and its corroboration
are STATED apart, not averaged together.

**What a green assertion #3 does NOT say.** It binds NAMES and SIGNATURES. A tool
whose name and parameters match the model may still have a wrong body, and this
module cannot see that — ``limits.unchecked[structural-surface-only]`` publishes
the bound in the payload, because a limitation that lives only in a docstring is
one skim away from not existing (R-13′).
"""

from __future__ import annotations

import ast
import os
import stat
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

from gnd.artifacts import ArtifactError, read_regular_bounded_at
from gnd.codegen.emit import TOOLS_MODULE
from gnd.codegen.identifiers import IdentifierError, module_name, symbol_table, tool_symbol
from gnd.codegen.manifest import CodegenManifest
from gnd.conformance import ConformanceError, Finding
from gnd.conformance.integrity import MAX_CONFORMANCE_BYTES, open_project_root
from gnd.extract.bundle import bundle_stem
from gnd.model import structured_derivation_ids

__all__ = [
    "DERIVED_TOOL_MODULE",
    "ExpectedTool",
    "ObservedString",
    "ObservedSymbol",
    "SatisfiedBy",
    "SourceObservation",
    "SourceObservationError",
    "StructuralResult",
    "check_structural",
    "derived_tool_relpath",
    "expected_surface",
    "observe_source_bytes",
    "observed_surface",
]

#: The file basename that DEFINES the derived tool namespace, imported from the
#: emitter rather than re-spelled (``emit.py:162``'s comment says this constant is
#: published because "plan 06's assertion #3 keys on these relpaths").
#:
#: It exists because :func:`tool_symbol` carries no prefix: the emitted tool for
#: ``employee_has_name`` is ``employee_has_name``, so "a symbol claiming the
#: derived namespace" cannot be recognised by its NAME. It is recognised by its
#: LOCATION — a module-level ``def`` at the exact model-derived relpath
#: ``<package>/tools.py``. The package is recomputed from the MODEL argument,
#: never inferred from a basename or read from the manifest, so an unrelated
#: extension ``tools.py`` cannot claim the generated namespace.
#:
#: The asymmetry with the MISSING direction is deliberate. A fact type may be
#: satisfied from ANYWHERE in the tree (so a generator cannot hide a gap by moving
#: a file), while an orphan is only reported inside the tool module (so a user's
#: own helper in their own file is never called drift).
DERIVED_TOOL_MODULE = TOOLS_MODULE


def derived_tool_relpath(model_path: str | Path) -> str:
    """The exact generated tool module path, derived from the model path only."""
    return f"{module_name(bundle_stem(str(model_path)))}/{DERIVED_TOOL_MODULE}"


@dataclass(frozen=True)
class ExpectedTool:
    """What the MODEL says the emitted surface must contain, for one fact type.

    ``parameters`` are the role names in DECLARED order, mapped through the same
    :func:`~gnd.codegen.identifiers.symbol_table` call the emitter makes, so a
    role named ``from`` is expected as ``from_`` here exactly as it is emitted
    there.
    """

    fact_type_id: str
    symbol: str
    parameters: tuple[str, ...]


@dataclass(frozen=True)
class ObservedSymbol:
    """One module-level ``def`` found on disk, with where it was found.

    ``lineno`` is carried so an orphan finding can send a reader to the line
    rather than to the file — RESEARCH §2.2 case C's finding names both.
    """

    symbol: str
    relpath: str
    lineno: int
    parameters: tuple[str, ...]
    in_tool_module: bool
    is_async: bool = False
    positional_only: tuple[str, ...] = ()
    keyword_only: tuple[str, ...] = ()
    vararg: str | None = None
    kwarg: str | None = None
    positional_defaults: int = 0
    keyword_defaults: tuple[bool, ...] = ()
    decorators: int = 0


@dataclass(frozen=True)
class ObservedString:
    """One string constant from the complete AST, including nested bodies."""

    value: str
    lineno: int


@dataclass(frozen=True)
class SourceObservation:
    """The one parsed observation shared by structural and architecture checks."""

    tree: ast.Module
    symbols: tuple[ObservedSymbol, ...]
    strings: tuple[ObservedString, ...]
    path_candidates: tuple[ast.expr, ...]


class SourceObservationError(ValueError):
    """A source's bytes could not become a static AST observation."""

    def __init__(self, cause: str, *, lineno: int | None = None) -> None:
        self.cause = cause
        self.lineno = lineno
        super().__init__(cause)


@dataclass(frozen=True)
class SatisfiedBy:
    """A fact type, the file that satisfied it, and who owns that file.

    ``ownership`` is ``derived``, ``extension`` or ``unmanaged`` — the manifest's
    own vocabulary plus the honest third value for a file GND has no record of
    placing (which is also what every file is when no manifest was supplied). A
    fourth value meaning "we did not look" is deliberately absent: this record
    exists only for fact types that WERE satisfied.
    """

    fact_type_id: str
    symbol: str
    relpath: str
    ownership: str


@dataclass(frozen=True)
class StructuralResult:
    """Findings, the satisfied-by partition, and what the assertion actually read.

    A separate type from :class:`~gnd.conformance.ConformanceResult` for the same
    reason :func:`~gnd.conformance.currency.check_currency` returns a bare tuple:
    each assertion returns the shape it can honestly fill. ``ConformanceResult``
    carries ``examined``/``unexamined`` over *manifest entries with digests*,
    which assertion #3 neither reads nor produces; reusing it would mean
    populating two fields with empty tuples that a reader could not tell from
    "nothing was skipped".

    ``expected`` and ``scanned`` are the non-vacuity evidence. Zero findings over
    zero expectations is not a passing gate, and neither is zero findings over an
    unread tree — the control test asserts both floors, because plan 05 measured
    that an always-firing check passes every mutation and fails only the control.
    """

    findings: tuple[Finding, ...] = ()
    satisfied: tuple[SatisfiedBy, ...] = ()
    expected: tuple[ExpectedTool, ...] = ()
    scanned: tuple[str, ...] = ()
    #: Corroboration only, never a finding — see the module docstring's R-07′
    #: paragraph. The model's object-type ids, in declared order.
    object_types: tuple[str, ...] = field(default=())


# --------------------------------------------------------------------------- #
# stage 1 — the expected surface, from the MODEL only
# --------------------------------------------------------------------------- #


def expected_surface(model: Any) -> tuple[tuple[ExpectedTool, ...], tuple[Finding, ...]]:
    """``(tools, findings)`` computed from ``model`` and from nothing else.

    No manifest is opened, no previous generation is read, and no filesystem call
    is made. That is the property the whole assertion rests on: an expectation
    derived from the generator's own output cannot catch the generator.

    The findings this stage can produce are :data:`IdentifierError` refusals —
    two fact-type ids, or two role names within one fact type, that sanitize to a
    single Python symbol. ``gnd codegen`` refuses such a model at exit 3 rather
    than emitting one tool for two fact types; here the same refusal is reported
    as an ``identifier-hazard`` finding instead of a traceback, because a
    conformance run over an ungeneratable model should say so rather than abort.
    """
    findings: list[Finding] = []
    fact_types = list(getattr(model, "fact_types", ()) or ())
    # v5.0 Phase 3 (T3.2): a structured-rule derived fact type is COMPUTED, so
    # no tool is expected for it. The filter is the same published predicate
    # gnd.codegen.emit consumes — the two surfaces cannot disagree (G-21).
    structured = set(structured_derivation_ids(model)) if fact_types else set()
    fact_types = [
        fact_type
        for fact_type in fact_types
        if str(fact_type.get("id")) not in structured
    ]
    fact_ids = [str(fact_type.get("id")) for fact_type in fact_types]

    try:
        tool_names = symbol_table(fact_ids, kind="fact type", symbol=tool_symbol)
    except IdentifierError as error:
        return (), (
            Finding(
                kind="identifier-hazard",
                target="fact_types",
                message=(
                    f"the model cannot be mapped to a distinct Python surface, so "
                    f"no expectation could be computed: {error}"
                ),
            ),
        )

    tools: list[ExpectedTool] = []
    for fact_type, fact_id in zip(fact_types, fact_ids, strict=True):
        roles = [str(role.get("role_name")) for role in (fact_type.get("roles") or [])]
        try:
            parameters = symbol_table(roles, kind=f"role of fact type '{fact_id}'")
        except IdentifierError as error:
            findings.append(
                Finding(
                    kind="identifier-hazard",
                    target=fact_id,
                    message=(
                        f"fact type {fact_id} has roles that cannot both keep "
                        f"their name in Python, so no signature could be expected "
                        f"for it: {error}"
                    ),
                )
            )
            continue
        tools.append(
            ExpectedTool(
                fact_type_id=fact_id,
                symbol=tool_names[fact_id],
                parameters=tuple(parameters[role] for role in roles),
            )
        )
    return tuple(tools), tuple(findings)


# --------------------------------------------------------------------------- #
# stage 2 — the observed surface, by AST, module level only
# --------------------------------------------------------------------------- #


def _unreadable(relpath: str, message: str) -> Finding:
    return Finding(kind="unparseable-source", target=relpath, message=message)


def _directory_identity(info: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        info.st_dev,
        info.st_ino,
        info.st_mode,
        info.st_size,
        info.st_mtime_ns,
    )


def _safe_coordinate(value: str) -> str:
    """Make a relative filesystem coordinate JSON-safe without losing its shape."""

    return value.encode("utf-8", "backslashreplace").decode("utf-8")


def _stat_at(name: str, directory_fd: int) -> os.stat_result:
    """No-follow stat seam for deterministic race and refusal tests."""

    return os.stat(name, dir_fd=directory_fd, follow_symlinks=False)


def observe_source_bytes(
    data: bytes,
    relpath: str,
    *,
    tool_relpath: str = "",
) -> SourceObservation:
    """Parse once and collect effective bindings plus whole-AST observations."""

    try:
        source = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise SourceObservationError("decode") from error
    try:
        tree = ast.parse(source, filename=relpath)
    except SyntaxError as error:
        raise SourceObservationError("syntax", lineno=error.lineno) from error
    except ValueError as error:
        raise SourceObservationError("value") from error

    def assigned_names(target: ast.expr) -> tuple[str, ...]:
        if isinstance(target, ast.Name):
            return (target.id,)
        if isinstance(target, ast.Starred):
            return assigned_names(target.value)
        if isinstance(target, ast.Tuple | ast.List):
            return tuple(name for item in target.elts for name in assigned_names(item))
        return ()

    bindings: dict[str, ast.AST | None] = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            bindings[node.name] = node
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                for name in assigned_names(target):
                    bindings[name] = None
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            for name in assigned_names(node.target):
                bindings[name] = None
        elif isinstance(node, ast.Import):
            for alias in node.names:
                bindings[alias.asname or alias.name.partition(".")[0]] = None
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name != "*":
                    bindings[alias.asname or alias.name] = None

    symbols: list[ObservedSymbol] = []
    for node in bindings.values():
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        arguments = node.args
        symbols.append(
            ObservedSymbol(
                symbol=node.name,
                relpath=relpath,
                lineno=node.lineno,
                parameters=tuple(argument.arg for argument in arguments.args),
                in_tool_module=relpath == tool_relpath,
                is_async=isinstance(node, ast.AsyncFunctionDef),
                positional_only=tuple(argument.arg for argument in arguments.posonlyargs),
                keyword_only=tuple(argument.arg for argument in arguments.kwonlyargs),
                vararg=arguments.vararg.arg if arguments.vararg else None,
                kwarg=arguments.kwarg.arg if arguments.kwarg else None,
                positional_defaults=len(arguments.defaults),
                keyword_defaults=tuple(default is not None for default in arguments.kw_defaults),
                decorators=len(node.decorator_list),
            )
        )

    strings: list[ObservedString] = []
    path_candidates: list[ast.expr] = []

    class WholeAstCollector(ast.NodeVisitor):
        def visit_Constant(self, node: ast.Constant) -> None:
            if isinstance(node.value, str):
                strings.append(ObservedString(node.value, node.lineno))
            self.generic_visit(node)

        def visit_BinOp(self, node: ast.BinOp) -> None:
            path_candidates.append(node)
            self.generic_visit(node)

        def visit_Call(self, node: ast.Call) -> None:
            path_candidates.append(node)
            self.generic_visit(node)

    WholeAstCollector().visit(tree)

    return SourceObservation(
        tree=tree,
        symbols=tuple(symbols),
        strings=tuple(strings),
        path_candidates=tuple(path_candidates),
    )


def observed_surface(
    project_root: str | Path,
    *,
    tool_relpath: str,
    root_fd: int | None = None,
) -> tuple[tuple[ObservedSymbol, ...], tuple[Finding, ...]]:
    """``(symbols, findings)`` for every ``*.py`` under ``project_root``.

    Discovery is a whole-tree ``rglob``, never the manifest's file list (§2.4).
    Collection is over ``tree.body`` and never ``ast.walk``, so only module-level
    ``FunctionDef`` / ``AsyncFunctionDef`` count; parameters come from
    ``posonlyargs + args + kwonlyargs`` in that order.

    Every abnormal state is a FINDING rather than a raise, because raising would
    abort the assertion over the whole tree and let one broken file deny the
    answer for every other fact type. A symlink is skipped and never followed, an
    occupant over :data:`MAX_CONFORMANCE_BYTES` is reported from its ``lstat`` and
    never read, and a path that resolves outside the root — reachable through a
    symlinked DIRECTORY, which ``rglob`` walks — is refused before it is opened.
    """
    symbols: list[ObservedSymbol] = []
    findings: list[Finding] = []
    owned_root_fd = root_fd is None
    retained_root_fd = open_project_root(project_root) if root_fd is None else root_fd

    def parse_source(relpath: str, data: bytes) -> None:
        try:
            observation = observe_source_bytes(
                data,
                relpath,
                tool_relpath=tool_relpath,
            )
        except SourceObservationError as error:
            if error.cause == "decode":
                message = f"{relpath} could not be decoded (cause: source-utf8)"
            elif error.cause == "syntax":
                message = (
                    f"{relpath}: SyntaxError line {error.lineno} "
                    f"(cause: source-syntax). A file that does not parse cannot "
                    f"satisfy any fact type, and conformance reports it rather "
                    f"than crashing on it"
                )
            else:
                message = f"{relpath} could not be parsed (cause: source-value)"
            findings.append(_unreadable(relpath, message))
            return
        symbols.extend(observation.symbols)

    def walk(directory_fd: int, prefix: tuple[str, ...]) -> None:
        before = os.fstat(directory_fd)
        try:
            names = sorted(os.listdir(directory_fd), key=os.fsencode)
        except OSError as error:
            raise ConformanceError(
                "structural directory could not be enumerated "
                "(cause: directory-enumeration)"
            ) from error
        if _directory_identity(os.fstat(directory_fd)) != _directory_identity(before):
            raise ConformanceError(
                "structural directory changed while enumerated "
                "(cause: directory-race)"
            )
        for name in names:
            parts = (*prefix, name)
            raw_relative = PurePosixPath(*parts).as_posix()
            relpath = _safe_coordinate(raw_relative)
            try:
                info = _stat_at(name, directory_fd)
            except OSError:
                findings.append(
                    _unreadable(
                        relpath,
                        f"{relpath} could not be inspected (cause: source-stat)",
                    )
                )
                continue
            if stat.S_ISLNK(info.st_mode):
                continue
            if stat.S_ISDIR(info.st_mode):
                child_fd = -1
                try:
                    child_fd = os.open(
                        name,
                        os.O_RDONLY
                        | getattr(os, "O_DIRECTORY", 0)
                        | getattr(os, "O_NOFOLLOW", 0),
                        dir_fd=directory_fd,
                    )
                    opened = os.fstat(child_fd)
                    if _directory_identity(opened) != _directory_identity(info):
                        raise ConformanceError(
                            "structural directory changed before opening "
                            "(cause: directory-race)"
                        )
                    walk(child_fd, parts)
                    current = _stat_at(name, directory_fd)
                    if (
                        _directory_identity(os.fstat(child_fd))
                        != _directory_identity(opened)
                        or _directory_identity(current) != _directory_identity(opened)
                    ):
                        raise ConformanceError(
                            "structural directory changed while scanned "
                            "(cause: directory-race)"
                        )
                except OSError as error:
                    raise ConformanceError(
                        "structural directory could not be opened safely "
                        "(cause: directory-open)"
                    ) from error
                finally:
                    if child_fd >= 0:
                        os.close(child_fd)
                continue
            if not stat.S_ISREG(info.st_mode) or not name.endswith(".py"):
                continue
            if info.st_size > MAX_CONFORMANCE_BYTES:
                findings.append(
                    _unreadable(
                        relpath,
                        f"{relpath} is over the {MAX_CONFORMANCE_BYTES}-byte cap "
                        "(cause: source-too-large)",
                    )
                )
                continue
            try:
                data, _snapshot = read_regular_bounded_at(
                    retained_root_fd,
                    raw_relative,
                    max_bytes=MAX_CONFORMANCE_BYTES,
                )
            except ArtifactError:
                findings.append(
                    _unreadable(
                        relpath,
                        f"{relpath} could not be read (cause: source-read)",
                    )
                )
                continue
            parse_source(relpath, data)
        if _directory_identity(os.fstat(directory_fd)) != _directory_identity(before):
            raise ConformanceError(
                "structural directory changed while scanned (cause: directory-race)"
            )

    try:
        walk(retained_root_fd, ())
    finally:
        if owned_root_fd:
            os.close(retained_root_fd)

    return tuple(symbols), tuple(findings)


# --------------------------------------------------------------------------- #
# stage 3 — the assertion
# --------------------------------------------------------------------------- #


def _ownership(manifest: CodegenManifest | None, relpath: str) -> str:
    """The manifest's ownership for ``relpath``, or ``unmanaged``.

    ``unmanaged`` is the literal truth for a file GND has no record of placing,
    and it is also the truth for EVERY file when no manifest was supplied. One
    value rather than two, because "GND did not place this" is the same fact in
    both cases and a second value would only invite a reader to treat one of them
    as reassuring.
    """
    if manifest is None:
        return "unmanaged"
    entry = manifest.entries().get(relpath)
    return entry.ownership if entry is not None else "unmanaged"


def check_structural(
    model: Any,
    project_root: str | Path,
    manifest: CodegenManifest | None = None,
    *,
    model_path: str | Path,
    root_fd: int | None = None,
) -> StructuralResult:
    """Assertion #3: does the tree at ``project_root`` name ``model``'s fact types?

    A pure function of a loaded model and a directory — no argv, no CLI, nothing
    written — so Phase 4's MODEL-02 can call it from a third entry point, the same
    property :func:`~gnd.conformance.currency.check_currency` was designed for.

    ``manifest`` is OPTIONAL and only classifies ownership; it is never consulted
    for discovery. Passing ``None`` weakens the report (every satisfying file
    reads as ``unmanaged``) and cannot weaken the gate, which is the right way
    round: the manifest can add information about who wrote a file, never about
    whether the model is covered.

    Five findings are possible, and each answers a different question:

    ``fact-type-unimplemented``
        the model declares a fact type and NOTHING in the tree defines its tool.
        This is the anti-tautology catch — 16 of these over ``full_vocabulary``
        against a generator that emitted well-formed nothing.
    ``tool-signature-mismatch``
        the symbol is there and its parameters are not the model's role names in
        declared order. A name check alone cannot see this.
    ``orphan-tool-symbol``
        a module-level ``def`` in the derived tool module that no model fact type
        names. Paired with the first kind, this is what proves the assertion read
        the model and the filesystem independently: a consistent rename produces
        BOTH, and neither could be produced by comparing either side against the
        manifest.
    ``fact-type-satisfied-by-non-derived``
        the fact type IS covered, but only by a file GND did not emit. Reported
        rather than forbidden (G-08), with the file and its ownership.
    ``identifier-hazard``
        the model cannot be mapped to a distinct Python surface at all.
    """
    root = Path(project_root)
    expected, findings_list = expected_surface(model)
    findings: list[Finding] = list(findings_list)

    symbols, observation_findings = observed_surface(
        root,
        tool_relpath=derived_tool_relpath(model_path),
        root_fd=root_fd,
    )
    findings.extend(observation_findings)

    scanned = tuple(sorted({symbol.relpath for symbol in symbols}))

    by_name: dict[str, list[ObservedSymbol]] = {}
    for symbol in symbols:
        by_name.setdefault(symbol.symbol, []).append(symbol)

    satisfied: list[SatisfiedBy] = []
    for tool in expected:
        candidates = by_name.get(tool.symbol, [])
        if not candidates:
            findings.append(
                Finding(
                    kind="fact-type-unimplemented",
                    target=tool.fact_type_id,
                    message=(
                        f"the model declares fact type {tool.fact_type_id} and no "
                        f"module-level tool {tool.symbol} exists anywhere "
                        f"under {root.name or root}; the generated surface does "
                        f"not cover the model, which is what regeneration repairs"
                    ),
                )
            )
            continue

        # Prefer a DERIVED definition when one exists: a duplicate helper in an
        # extension file is not drift, and reporting it as such would fire the
        # gate on a project that is entirely correct.
        ranked = sorted(
            candidates,
            key=lambda candidate: (
                _ownership(manifest, candidate.relpath) != "derived",
                not candidate.in_tool_module,
                candidate.relpath,
                candidate.lineno,
            ),
        )
        chosen = ranked[0]
        ownership = _ownership(manifest, chosen.relpath)
        satisfied.append(
            SatisfiedBy(
                fact_type_id=tool.fact_type_id,
                symbol=tool.symbol,
                relpath=chosen.relpath,
                ownership=ownership,
            )
        )

        if ownership != "derived":
            findings.append(
                Finding(
                    kind="fact-type-satisfied-by-non-derived",
                    target=tool.fact_type_id,
                    message=(
                        f"fact type {tool.fact_type_id} is satisfied only by "
                        f"{chosen.relpath} [{ownership}], which GND did not emit. "
                        f"That is not forbidden and nothing here has changed it — "
                        f"but conformance reports it rather than passing silently, "
                        f"because a derived surface that no longer covers the "
                        f"model is repaired by regeneration and a hand-written one "
                        f"is not (G-08)"
                    ),
                )
            )

        shape_mismatch = (
            chosen.parameters != tool.parameters
            or chosen.is_async
            or bool(chosen.positional_only)
            or bool(chosen.keyword_only)
            or chosen.vararg is not None
            or chosen.kwarg is not None
            or chosen.positional_defaults != 0
            or any(chosen.keyword_defaults)
            or chosen.decorators != 0
        )
        if shape_mismatch:
            observed_shape = (
                f"async={chosen.is_async}, positional_only={chosen.positional_only}, "
                f"parameters={chosen.parameters}, keyword_only={chosen.keyword_only}, "
                f"vararg={chosen.vararg!r}, kwarg={chosen.kwarg!r}, "
                f"defaults={chosen.positional_defaults}, "
                f"keyword_defaults={chosen.keyword_defaults}, "
                f"decorators={chosen.decorators}"
            )
            findings.append(
                Finding(
                    kind="tool-signature-mismatch",
                    target=tool.fact_type_id,
                    message=(
                        f"{chosen.relpath}:{chosen.lineno} defines "
                        f"{tool.symbol} with shape [{observed_shape}], but fact "
                        f"type {tool.fact_type_id} declares roles "
                        f"({', '.join(tool.parameters)}) as an undecorated synchronous "
                        f"positional signature; the runtime binding and the model "
                        f"disagree about the shape of the fact"
                    ),
                )
            )

    # v5.0 Phase 3 (D-P3.5): a constructor PRESENT for a computed fact type is
    # drift wherever it lives — a callable invites the agent to assert a fact
    # the model derives. Assertion #2 already reds a project that was simply
    # not regenerated (model-digest-mismatch, measured before this check was
    # written); this catches the constructor that survives regeneration, i.e.
    # one somebody wrote back. Reported under its own kind, not as an orphan:
    # the orphan message says "the model no longer declares this fact", and for
    # a derived fact type the model very much declares it.
    structured = (
        structured_derivation_ids(model)
        if getattr(model, "fact_types", None)
        else ()
    )
    # An EXPECTED tool's symbol can never be attributed to a structured fact
    # type: when sanitization collides (structured `import` and asserted
    # `import_` both reaching `import_`), the asserted fact type owns the
    # emitted constructor, and reporting it as a derived constructor would red
    # a correctly regenerated project — the false-red class G-21 exists to
    # prevent (adversarial review finding 5, reproduced before this guard).
    expected_symbols = {tool.symbol for tool in expected}
    computed_symbols: dict[str, str] = {}
    for fact_id in structured:
        with suppress(IdentifierError):
            symbol = tool_symbol(fact_id)
            if symbol not in expected_symbols:
                computed_symbols[symbol] = fact_id
    for symbol in symbols:
        fact_id = computed_symbols.get(symbol.symbol)
        if fact_id is None:
            continue
        findings.append(
            Finding(
                kind="derived-fact-type-constructed",
                target=fact_id,
                message=(
                    f"{symbol.relpath}:{symbol.lineno} defines {symbol.symbol}, "
                    f"but fact type {fact_id} carries a structured derivation "
                    f"rule: the model computes its facts and no constructor may "
                    f"exist for it. Delete the definition — the population claims "
                    f"the derived extension directly and gnd verify decides the "
                    f"claim"
                ),
            )
        )

    known = {tool.symbol for tool in expected}
    for symbol in symbols:
        if not symbol.in_tool_module or symbol.symbol in known:
            continue
        if symbol.symbol in computed_symbols:
            continue  # already reported above under its own kind
        findings.append(
            Finding(
                kind="orphan-tool-symbol",
                target=symbol.symbol,
                message=(
                    f"{symbol.relpath}:{symbol.lineno} defines {symbol.symbol} "
                    f"in the derived tool module, and no fact type in the model "
                    f"maps to that symbol; the code is describing a fact the model "
                    f"no longer declares"
                ),
            )
        )

    return StructuralResult(
        findings=tuple(findings),
        satisfied=tuple(satisfied),
        expected=expected,
        scanned=scanned,
        object_types=tuple(
            str(object_type.get("id"))
            for object_type in (getattr(model, "object_types", ()) or ())
        ),
    )
