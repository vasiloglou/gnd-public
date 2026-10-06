"""The model -> file-tree emitter: deterministic, self-parsing, provider-free.

``gnd extract`` is the only shipped model -> files-on-disk emitter, and it writes
FLAT into ``--out``. Nested-tree emission is the gap this module fills, keeping
every discipline that command established: the ``canonical`` JSON helper (sorted
keys, ``allow_nan=False``, trailing newline) so two runs agree to the byte, the
``synth.paths.safe_output_path`` traversal guard on every destination, and a
staging directory made durable before anything is published.

**The layout, stated because two later plans key on it.** Plan 04's manifest
keys on these relpaths and plan 06's assertion #3 scans them, so this is a
contract, not a formatting choice:

.. code-block:: text

    <out>/
      <package>/__init__.py                       derived
      <package>/tools.py                          derived
      artifacts/<stem>.projection.schema.json     derived
      artifacts/<stem>.verbalization.txt          derived
      artifacts/<stem>.applicable.json            derived
      artifacts/<stem>.artifacts.json             derived (the digest index)
      SKILL.md                                    derived
      architecture.contract.yaml                 EXTENSION (create-once)
      references/<skill>-notes.md                 EXTENSION (create-once)
      pyproject.toml                              EXTENSION (create-once)

``<package>`` is :func:`gnd.codegen.identifiers.module_name` of the model's
stem; ``<stem>`` is ``gnd extract``'s slugged stem, so the four bundle files are
byte-identical to what ``gnd extract MODEL --out artifacts/`` produces and the
generated project's verifier half is the SHIPPED ``gnd verify``.

**No second derivation (G-03).** ``project``, ``render_verbalization``,
``applicable_set`` and the ``header_template`` owner are CALLED. An emitter that
re-derived any of them would fork the source of truth and drift from it, and the
drift would surface as a generated project whose projection disagrees with the
one ``gnd verify`` composes.

**The whole ``SKILL.md`` is emitted by code, frontmatter included.** RESEARCH
§3.3 candidate 2 is decisive: the frontmatter is discovery-critical, GND has no
frontmatter validator anywhere else, and declaring the file an extension would
leave the one artifact deciding whether the generated agent is discoverable at
all unchecked. The skill half authors ``references/<skill>-notes.md`` instead —
the shipped ``gnd-extract`` + ``references/extraction-contract.md`` pattern. The
emitted frontmatter is round-tripped through
:func:`gnd.exp.frontmatter.read_frontmatter` DURING emission, so an unparseable
skill document cannot reach disk.

**``pyproject.toml`` is a CREATE-ONCE EXTENSION, and this is the one file where
G-06's two rules genuinely conflict.** "Derived files are rewritten" and
"regeneration never overwrites an extension file" cannot both hold for it,
because G-02 explicitly allows the user to add a provider client and that lands
in its dependencies. Extension wins: losing a user's dependency list is
unrecoverable, while a stale generated skeleton is visible and fixable. Recorded
here rather than left for plan 04's classifier to rediscover.

**The banner deters; the digest detects.** :data:`GENERATED_BANNER` is Go's
machine-readable convention (``^// Code generated .*DO NOT EDIT\\.$``, Go 1.9+)
in Python comment syntax, anchored at line 1. It is CORROBORATION only — a
banner can always be forged, and a checker that scans the whole file can be
fooled by a string literal. Detection is plan 04's manifest digest. Nothing in
this module or downstream may treat the banner as the gate.

**Four gates run in production, not only in tests** (the
``ProjectionGateError`` precedent): every emitted ``.py`` is ``ast.parse``d
before any byte reaches disk (T-03-14 — a hostile model can never leave broken
or truncated Python waiting to be executed), the emitted text is scanned for
provider/network imports (T-03-16 — G-02 binds the default template), the skill
frontmatter round-trips, and the architecture skeleton loads. All raise
:class:`EmitGateError`, which the CLI maps to ``EXIT_INTERNAL``: a gate
violation in GND's own emitter over an already-valid model is never the caller's
input error.

Codegen never imports or executes what it emits.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import tempfile
from collections.abc import Iterable, Mapping
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from gnd.architecture import ArchitectureContractError, parse_architecture_contract_bytes
from gnd.codegen.docstrings import DOCSTRING_DELIMITER, tool_docstring
from gnd.codegen.identifiers import (
    module_name,
    smoke_discriminator,
    symbol_table,
    tool_symbol,
)
from gnd.exp.frontmatter import FrontmatterError, read_frontmatter, render_frontmatter
from gnd.extract.bundle import bundle_stem, header_template
from gnd.extract.projection import project
from gnd.extract.refscheme import applicable_set
from gnd.extract.vocabulary import reading_text, render_verbalization
from gnd.model import structured_derivation_ids
from gnd.synth import paths as _paths
from gnd.verbalize import _neutralize, line_text

__all__ = [
    "ARCHITECTURE_CONTRACT_DOCUMENT",
    "ARTIFACTS_DIR",
    "BANNER_LINE",
    "GENERATED_BANNER",
    "PROVIDER_AND_NETWORK_LIBS",
    "REFERENCES_DIR",
    "EmitGateError",
    "GeneratedFile",
    "GeneratedProject",
    "ProjectExistsError",
    "SkillNameError",
    "assert_emitted_python_parses",
    "emit_project",
    "extract_stem",
    "provider_import_offenders",
    "render_architecture_contract",
    "render_skill_document",
    "render_smoke_module",
    "render_tools_module",
    "scan_tree_for_provider_imports",
    "smoke_module_pattern",
    "smoke_module_relpath",
    "write_project",
]

ARCHITECTURE_CONTRACT_DOCUMENT = "architecture.contract.yaml"

#: The banner TEMPLATE. One ``{source}`` field, filled with the model path the
#: caller named on argv (neutralized). Published beside the regex so the two
#: cannot drift — the emitter formats this, and every check matches that.
BANNER_LINE = "# Code generated by gnd codegen from {source}; DO NOT EDIT."

#: Go's machine-readable generated-file convention (``golang/go`` #41196),
#: transliterated to Python comment syntax and ANCHORED: ``fullmatch`` semantics
#: via ``$``, checked at line 1 only. Go permits the line anywhere in the file,
#: which is precisely why a whole-file scan can be fooled by a string literal —
#: so this is corroboration and the manifest digest (plan 04) is the detection.
GENERATED_BANNER = re.compile(r"^# Code generated by gnd codegen from .*; DO NOT EDIT\.$")

#: Provider SDKs and network libraries the EMITTED template must not import
#: (G-02, T-03-16). A superset of ``tests/test_measure_offline.py``'s two
#: tuples, deliberately restated here rather than imported from the test suite:
#: this table gates PRODUCTION emission, and a production gate that imports its
#: rule from a test file inverts the dependency and vanishes from a wheel.
#: G-02's boundary in one line — GND's default template ships no client; a user
#: adding one to their own project is their extension and lands in an extension
#: file, which this scan never reaches because it only sees what codegen emits.
PROVIDER_AND_NETWORK_LIBS = frozenset(
    {
        "anthropic",
        "openai",
        "cohere",
        "mistralai",
        "ollama",
        "litellm",
        "google.generativeai",
        "vertexai",
        "boto3",
        "httpx",
        "requests",
        "aiohttp",
        "urllib3",
        "urllib.request",
        "http.client",
        "socket",
    }
)

#: Layout constants. Published because plan 04's manifest and plan 06's
#: assertion #3 both key on these relpaths; a string literal buried in a builder
#: would make the contract invisible to the plans that depend on it.
ARTIFACTS_DIR = "artifacts"
REFERENCES_DIR = "references"
SKILL_DOCUMENT = "SKILL.md"
PYPROJECT_DOCUMENT = "pyproject.toml"
TOOLS_MODULE = "tools.py"

#: File-ownership vocabulary (G-04: a "region" is a FILE).
DERIVED = "derived"
EXTENSION = "extension"

_MODEL_SUFFIXES = (".orm.yaml", ".orm.yml", ".yaml", ".yml", ".json")
SKILL_NAME_MAX_LENGTH = 64
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class EmitGateError(RuntimeError):
    """The emitter built a tree that violates one of its own invariants.

    Raised by :func:`emit_project` itself — in production, not only in a test
    (the ``ProjectionGateError`` discipline) — for a module that does not parse,
    a provider import in the default template, or a skill document whose
    frontmatter will not round-trip, or an architecture skeleton that does not
    round-trip to its complete artifact inventory. All four are breaches by GND's emitter
    over a model that already loaded clean, so the CLI maps this to
    ``EXIT_INTERNAL`` rather than to the ill-formed-input band: sending the user
    to fix a valid model would be a lie about where the fault is.
    """


class ProjectExistsError(FileExistsError):
    """The target directory exists and is not empty.

    This plan refuses outright and destroys nothing. The six-state
    derived/extension/unmanaged classifier with ``--force`` — the shape
    ``install.py:784`` ships for skill placement — is plan 04's, and it is
    deliberately NOT approximated here: a half-built classifier that overwrote
    the wrong file once would be worse than a flat refusal.
    """


class SkillNameError(ValueError):
    """A generated skill name violates the Agent Skills directory contract."""


# --------------------------------------------------------------------------
# The two production gates
# --------------------------------------------------------------------------


def _imported_roots(source: str) -> set[str]:
    """Every dotted module name imported by ``source``, via the AST.

    An AST walk rather than a regex: the emitted tree is ours and always parses,
    so precision is free here, and a regex would flag the word ``socket`` inside
    a docstring while missing ``import  anthropic`` with odd spacing.
    """
    roots: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            roots.add(node.module)
    return roots


def provider_import_offenders(sources: Mapping[str, str]) -> dict[str, list[str]]:
    """``{relpath: [library, ...]}`` for every provider/network import found.

    ONE predicate, TWO callers — :func:`emit_project` runs it over the emitted
    TEXT before anything is written, and :func:`scan_tree_for_provider_imports`
    runs it over a tree on disk (which is how the mandatory red-making mutation
    in ``tests/test_codegen_emit.py`` plants ``import anthropic`` into a COPY and
    proves the scan names the file). Two copies of this rule would let the
    production gate and the test gate disagree.
    """
    offenders: dict[str, list[str]] = {}
    for relpath, source in sources.items():
        if not relpath.endswith(".py"):
            continue
        try:
            imported = _imported_roots(source)
        except SyntaxError:
            # Unparseable modules are the OTHER gate's finding; reporting them
            # here as "no provider imports" would be a scan that passed by
            # failing to look.
            continue
        hits = sorted(
            library
            for library in PROVIDER_AND_NETWORK_LIBS
            if any(name == library or name.startswith(library + ".") for name in imported)
        )
        if hits:
            offenders[relpath] = hits
    return offenders


def scan_tree_for_provider_imports(root: str | Path) -> dict[str, list[str]]:
    """:func:`provider_import_offenders` over every ``.py`` under ``root``."""
    base = Path(root)
    sources = {
        str(path.relative_to(base)): path.read_text(encoding="utf-8")
        for path in sorted(base.rglob("*.py"))
    }
    return provider_import_offenders(sources)


def assert_emitted_python_parses(files: Iterable[GeneratedFile]) -> None:
    """``ast.parse`` every emitted ``.py``, or raise :class:`EmitGateError`.

    T-03-14: the emitted tree is code the user will execute later. Asserting it
    parses at EMISSION time means a hostile model cannot leave broken syntax on
    disk waiting to be run. Parsing is not executing — nothing emitted is ever
    imported by codegen.
    """
    broken: list[str] = []
    for file in files:
        if not file.relpath.endswith(".py"):
            continue
        try:
            ast.parse(file.text, filename=file.relpath)
        except SyntaxError as error:
            broken.append(f"{file.relpath}: {error}")
    if broken:
        raise EmitGateError(
            "the emitter built Python that does not parse, and refused to write "
            "it — a generated project is code the user executes, so broken "
            f"syntax must never reach disk (T-03-14): {'; '.join(broken)}"
        )


# --------------------------------------------------------------------------
# The project description
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class GeneratedFile:
    """One emitted file: its relpath, its whole text, and who owns it."""

    relpath: str
    text: str
    ownership: str


@dataclass(frozen=True)
class GeneratedProject:
    """Everything ``gnd codegen`` would write, before anything is written."""

    model_path: str
    package: str
    stem: str
    skill_name: str
    files: tuple[GeneratedFile, ...]

    @property
    def relpaths(self) -> tuple[str, ...]:
        return tuple(file.relpath for file in self.files)

    @property
    def derived(self) -> tuple[GeneratedFile, ...]:
        return tuple(file for file in self.files if file.ownership == DERIVED)

    @property
    def extensions(self) -> tuple[GeneratedFile, ...]:
        return tuple(file for file in self.files if file.ownership == EXTENSION)


def extract_stem(model_path: str) -> str:
    """The slugged filename stem the artifact bundle's four files share.

    Delegates to :func:`gnd.extract.bundle.bundle_stem`, the ONE owner. This
    function used to re-implement the rule by hand so a codegen bundle and a
    ``gnd extract`` bundle would name the same files — which is the two-copies
    arrangement that agrees only until one of them is corrected. Kept as a name
    because ``emit_project`` and plan 06's assertion #3 read better with it.
    """
    return bundle_stem(model_path)


def _canonical(payload: Any) -> str:
    """``_cmd_extract``'s byte-determinism helper, verbatim in discipline.

    Sorted keys and ``allow_nan=False`` so two runs over one model agree to the
    byte — which is what makes plan 04's zero-write idempotence assertion even
    possible to state.
    """
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n"


# --------------------------------------------------------------------------
# Renderers
# --------------------------------------------------------------------------


def _docstring_lines(text: str) -> list[str]:
    """A ``tool_docstring`` body as PHYSICAL lines inside a function body.

    Returns lines rather than one embedded-newline string on purpose: the
    renderers run every emitted line through ``verbalize.line_text``, which
    escapes newlines — so a multi-line string handed to it would come back with
    literal ``\\n`` sequences and the whole docstring collapsed onto one line.
    """
    lines = text.split("\n")
    if len(lines) == 1:
        return [f"    {DOCSTRING_DELIMITER}{lines[0]}{DOCSTRING_DELIMITER}"]
    return [
        f"    {DOCSTRING_DELIMITER}{lines[0]}",
        *(f"    {line}".rstrip() for line in lines[1:]),
        f"    {DOCSTRING_DELIMITER}",
    ]


def _constructor_fact_types(model: Any) -> tuple[list[Any], list[str]]:
    """The fact types that get a constructor tool, in declared order.

    A structured-rule derived fact type is COMPUTED by the model, never
    constructed by a tool (v5.0 Phase 3, T3.1): a general population claims its
    exact extension and ``gnd check`` decides the claim. A document extraction
    omits that extension and uses the filtered extraction header. A legacy free-text
    rule keeps its constructor and its pre-v5 bytes (r2 A10). The filter is
    :func:`gnd.model.structured_derivation_ids` — the one published predicate,
    shared with conformance's expected surface — so the two surfaces cannot
    disagree about what exists.
    """
    structured = set(structured_derivation_ids(model))
    kept = [
        fact_type for fact_type in model.fact_types if str(fact_type.get("id")) not in structured
    ]
    return kept, [str(fact_type.get("id")) for fact_type in kept]


def render_tools_module(model: Any, *, model_path: str, package: str) -> str:
    """``tools.py``: one module-level function per fact type, 100% derived.

    Signatures come from the model's roles in DECLARED order (parameter names
    through :func:`gnd.codegen.identifiers.python_symbol`, function names
    through :func:`~gnd.codegen.identifiers.tool_symbol`), and docstrings come
    from :func:`gnd.codegen.docstrings.tool_docstring`. Nothing in this file is
    skill-authored, which is exactly what lets G-04 keep file-level ownership
    without an in-file sentinel.

    Each tool returns ONE fact in the population interchange shape — a mapping
    keyed by the model's RAW role names, not the sanitized Python ones, because
    JSON keys are unconstrained and the projection schema enumerates the raw
    names. Keys are emitted through ``repr``, so Python's own escaping is what
    quotes them rather than a hand-rolled rule.
    """
    kept_fact_types, fact_ids = _constructor_fact_types(model)
    structured = structured_derivation_ids(model)
    tools = symbol_table(fact_ids, kind="fact type", symbol=tool_symbol)
    delimiter = DOCSTRING_DELIMITER
    verifier = "`gnd check`." if structured else "`gnd verify`."

    lines: list[str] = [
        BANNER_LINE.format(source=_neutralize(Path(model_path).as_posix())),
        (f"{delimiter}Derived tools for the ORM model {_neutralize(Path(model_path).name)}."),
        "",
        "One function per fact type, named by",
        "gnd.codegen.identifiers.tool_symbol and taking the fact type's roles in",
        "declared order. Each returns one fact in the population interchange",
        f"shape that {ARTIFACTS_DIR}/'s projection schema accepts, so a",
        "population is assembled by calling these and checked by the shipped",
        verifier,
    ]
    if structured:
        lines.extend(
            [
                "",
                "Fact types with a structured derivation rule get NO tool here:",
                "the model computes their facts. A general population lists each",
                "claimed type in `covers`, publishes the exact extension, and uses",
                "`gnd check`; a document extraction omits these computed rows and",
                "uses the filtered extraction header with `gnd verify`.",
                "Computed, not constructed:",
                *(f"  - {_neutralize(fact_id)}" for fact_id in structured),
            ]
        )
    lines.extend(
        [
            "",
            "DERIVED FILE. Regenerate with `gnd codegen`; edits are lost, and the",
            f"codegen manifest digest detects them.{delimiter}",
            "",
            "from __future__ import annotations",
            "",
            "__all__ = [",
        ]
    )
    lines.extend(f"    {symbol!r}," for symbol in tools.values())
    lines.append("]")

    for fact_type in kept_fact_types:
        fact_id = str(fact_type.get("id"))
        roles = [str(role.get("role_name")) for role in (fact_type.get("roles") or [])]
        parameters = symbol_table(roles, kind=f"role of fact type '{fact_id}'")
        signature = ", ".join(parameters.values())
        payload = ", ".join(f"{role!r}: {parameters[role]}" for role in roles)
        lines.extend(
            [
                "",
                "",
                f"def {tools[fact_id]}({signature}):",
                *_docstring_lines(tool_docstring(model, fact_type)),
                f"    return {{{payload}}}",
            ]
        )

    # `line_text` per PHYSICAL line, which is why `_docstring_lines` returns a
    # list rather than one embedded-newline string: passing multi-line text
    # through it would escape the emitter's OWN newlines into a literal `\n`
    # and collapse every docstring onto one line. The guard stays because it
    # costs nothing and catches a control character that reached a line by a
    # route nobody anticipated; the neutralization that actually matters
    # already happened at each interpolation site.
    return "\n".join(line_text(line) for line in lines) + "\n"


def render_package_init(model: Any, *, model_path: str, package: str) -> str:
    """The generated package's ``__init__.py`` — a re-export, nothing more."""
    delimiter = DOCSTRING_DELIMITER
    _, fact_ids = _constructor_fact_types(model)
    tools = symbol_table(fact_ids, kind="fact type", symbol=tool_symbol)
    lines = [
        BANNER_LINE.format(source=_neutralize(Path(model_path).as_posix())),
        (
            f"{delimiter}The derived agent package for "
            f"{_neutralize(Path(model_path).name)}.{delimiter}"
        ),
        "",
        "from __future__ import annotations",
    ]
    # A model whose every fact type is structured-derived exports no tool; an
    # empty import block would not parse, so the re-export is conditional.
    if tools:
        lines.extend(
            [
                "",
                f"from {package}.{TOOLS_MODULE[:-3]} import (",
                *(f"    {symbol}," for symbol in tools.values()),
                ")",
            ]
        )
    lines.extend(
        [
            "",
            "__all__ = [",
            *(f"    {symbol!r}," for symbol in tools.values()),
            "]",
        ]
    )
    return "\n".join(line_text(line) for line in lines) + "\n"


def _validated_skill_name(name: str) -> str:
    if len(name) > SKILL_NAME_MAX_LENGTH or not SKILL_NAME_PATTERN.fullmatch(name):
        raise SkillNameError(
            f"generated skill name {name!r} must be at most "
            f"{SKILL_NAME_MAX_LENGTH} characters and match "
            f"{SKILL_NAME_PATTERN.pattern}"
        )
    return name


def _skill_name(stem: str) -> str:
    """The generated skill's frontmatter ``name``: lowercase-hyphenated.

    The Agent Skills spec requires the name to match the directory it ships in
    and to be lowercase-hyphenated, so underscores from the model stem become
    hyphens here — this is a FILENAME-space transform and deliberately not
    :mod:`gnd.codegen.identifiers`' Python-symbol one.
    """
    segment = re.sub(r"[^a-z0-9]+", "-", stem.strip().lower()).strip("-") or "x"
    return _validated_skill_name(f"gnd-{segment}")


def _cell(text: Any) -> str:
    """One markdown table cell: neutralized, with ``|`` escaped.

    ``_neutralize`` closes quote and line-structure escapes; the pipe is
    markdown-specific and would otherwise let model text forge extra columns.
    """
    return _neutralize(text).replace("|", "\\|")


def render_skill_document(
    model: Any,
    *,
    model_path: str,
    package: str,
    stem: str,
    skill_name: str | None = None,
) -> str:
    """The whole ``SKILL.md``, frontmatter included, emitted by code.

    The ``references/`` note is what the skill half authors and extends — the
    shipped ``gnd-extract`` + ``references/extraction-contract.md`` pattern —
    so this document stays fully derived and digest-gateable.

    The constraint-blind verbalization is LINKED, not inlined: it is already an
    emitted, digest-gated artifact, and inlining it would both duplicate its
    bytes and put model-supplied prose inside a markdown fence that model text
    could close.
    """
    name = _validated_skill_name(skill_name) if skill_name is not None else _skill_name(stem)
    notes_name = _skill_name(stem)
    kept_fact_types, fact_ids = _constructor_fact_types(model)
    structured = set(structured_derivation_ids(model))
    tools = symbol_table(fact_ids, kind="fact type", symbol=tool_symbol)

    if structured:
        description = (
            f"Runs the derived GND agent for the ORM model "
            f"{_neutralize(Path(model_path).name)}: build facts with the derived "
            f"tools in {package}/{TOOLS_MODULE}, assemble a population against "
            f"{ARTIFACTS_DIR}/{stem}.projection.schema.json, then use `gnd check` "
            f"for a general structured claim or `gnd verify` for a bound document "
            f"extraction. Use when asked to extract, assemble or check a population "
            f"for this model. Fully offline — no provider client and no API key; "
            f"the agent reading this skill IS the model call."
        )
    else:
        description = (
            f"Runs the derived GND agent for the ORM model "
            f"{_neutralize(Path(model_path).name)}: build facts with the derived "
            f"tools in {package}/{TOOLS_MODULE}, assemble a population against "
            f"{ARTIFACTS_DIR}/{stem}.projection.schema.json, then check it with "
            f"`gnd verify`. Use when asked to extract, assemble or check a "
            f"population for this model. Fully offline — no provider client and no "
            f"API key; the agent reading this skill IS the model call."
        )

    population_validator = (
        "`gnd check` for a general claim; the manifest-bound `gnd verify` "
        "workflow below for a document extraction"
        if structured
        else "the manifest-bound `gnd verify` workflow below"
    )
    verify_heading = (
        "### Verify a document extraction" if structured else "### Verify the population"
    )
    verify_intro = (
        "Run this only after the `gnd-extract` workflow wrote `population.json` "
        "and its extraction sidecar. The document extraction copies the emitted "
        "header template verbatim and never publishes a structured-derived row. "
        "The command reads the model reference from `.gnd-codegen.json`, searches "
        "from the project through its ancestor directories when that reference is "
        "relative, and accepts only a file whose SHA-256 matches the manifest."
        if structured
        else (
            "Run this from the generated project directory. It reads the model "
            "reference from `.gnd-codegen.json`, searches from the project through "
            "its ancestor directories when that reference is relative, and accepts "
            "only a file whose SHA-256 matches the manifest."
        )
    )
    summary_verifier = (
        "the shipped `gnd check` / `gnd verify` lanes" if structured else "the shipped `gnd verify`"
    )

    body_lines = [
        f"# {_neutralize(name)}",
        "",
        "<!-- Code generated by gnd codegen; DO NOT EDIT. The prose you may",
        f"     edit lives in {REFERENCES_DIR}/{notes_name}-notes.md. -->",
        "",
        "## Summary",
        "",
        (
            "**You are the agent.** There is no provider client and no network call "
            "anywhere in this project: the deterministic half is plain Python plus "
            f"{summary_verifier}, and you are the language half."
        ),
        "",
        "| You write | A validator checks it |",
        "|---|---|",
        f"| `population.json` | {population_validator} |",
        "",
        verify_heading,
        "",
        verify_intro,
        "",
        "```sh",
        "MODEL_PATH=\"$(python - <<'PY'",
        "import hashlib",
        "import json",
        "from pathlib import Path",
        "",
        "root = Path.cwd().resolve()",
        "manifest = json.loads((root / '.gnd-codegen.json').read_text())",
        "reference = manifest['model']",
        "recorded = Path(reference['path'])",
        "anchors = (root, *root.parents)",
        "candidates = [recorded] if recorded.is_absolute() else [a / recorded for a in anchors]",
        "for candidate in candidates:",
        "    if candidate.is_file() and hashlib.sha256(candidate.read_bytes()).hexdigest() == reference['sha256']:",
        "        print(candidate.resolve())",
        "        break",
        "else:",
        "    raise SystemExit('the manifest model path is missing or its digest changed')",
        "PY",
        ')"',
        'gnd verify "$MODEL_PATH" population.json --artifacts artifacts',
        "```",
    ]
    if structured:
        body_lines.extend(
            [
                "",
                "### Check a general population",
                "",
                (
                    "The emitted header template is extraction-only. For a general "
                    "population, use it only as a starting point: add every structured "
                    "fact type whose extension you publish to `covers`, then check the "
                    "claim directly. This lane is not a document extraction and does "
                    "not use an extraction sidecar."
                ),
                "",
                "```sh",
                'gnd check "$MODEL_PATH" population.json',
                "```",
            ]
        )
    body_lines.extend(
        [
            "",
            "## Derived tools",
            "",
            (
                f"One function per fact type in `{package}/{TOOLS_MODULE}`. Each returns "
                f"one fact in the population interchange shape."
            ),
            "",
            "| Tool | Fact type | Reading | Roles |",
            "|---|---|---|---|",
        ]
    )
    for fact_type in kept_fact_types:
        fact_id = str(fact_type.get("id"))
        roles = ", ".join(_cell(role.get("role_name")) for role in (fact_type.get("roles") or []))
        body_lines.append(
            f"| `{_cell(tools[fact_id])}` | `{_cell(fact_id)}` | "
            f"{_cell(reading_text(fact_type.get('reading')))} | {roles} |"
        )

    if structured:
        body_lines.extend(
            [
                "",
                "## Derived fact types",
                "",
                (
                    "These fact types carry a structured derivation rule, so NO tool "
                    "constructs them: the model computes their facts. In a general "
                    "population, list every type whose exact extension you publish in "
                    "`covers` and use `gnd check`; an omitted computed fact is incomplete "
                    "and an invented one is unsound. In a document extraction, omit "
                    "these rows and keep the emitted extraction header verbatim."
                ),
                "",
                "| Fact type | Reading |",
                "|---|---|",
            ]
        )
        for fact_type in model.fact_types:
            fact_id = str(fact_type.get("id"))
            if fact_id not in structured:
                continue
            body_lines.append(
                f"| `{_cell(fact_id)}` | {_cell(reading_text(fact_type.get('reading')))} |"
            )

    body_lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "| File | What it gives you |",
            "|---|---|",
            (
                f"| `{ARTIFACTS_DIR}/{stem}.projection.schema.json` | the closed, "
                f"shape-only schema your population must satisfy |"
            ),
            (
                f"| `{ARTIFACTS_DIR}/{stem}.verbalization.txt` | the "
                f"constraint-blind model rendering |"
            ),
            (
                f"| `{ARTIFACTS_DIR}/{stem}.applicable.json` | which fact types are "
                f"measurable under their reference schemes |"
            ),
            (
                f"| `{ARTIFACTS_DIR}/{stem}.artifacts.json` | sha256 digests and the "
                f"document-extraction header template; copy it verbatim only in that "
                f"lane |"
            )
            if structured
            else (
                f"| `{ARTIFACTS_DIR}/{stem}.artifacts.json` | sha256 digests and the "
                f"header template to copy verbatim |"
            ),
            "",
            "## Domain notes",
            "",
            (
                f"Domain-specific guidance lives in "
                f"[`{REFERENCES_DIR}/{notes_name}-notes.md`]"
                f"({REFERENCES_DIR}/{notes_name}-notes.md)"
                f" — that file is YOURS to write and `gnd codegen` never rewrites it."
            ),
            "",
        ]
    )

    body = "\n".join(line_text(line) for line in body_lines)
    return render_frontmatter({"name": name, "description": description}, body)


def _render_pyproject(package: str, stem: str) -> str:
    """The create-once ``pyproject.toml`` skeleton.

    No banner: a banner would claim a derived file, and this one is an
    extension the user owns from the moment it is created (see the module
    docstring for why extension wins the G-06 conflict here).
    """
    return "\n".join(
        [
            "# Created once by `gnd codegen`. This file is YOURS: regeneration",
            "# never rewrites it, because your dependencies live here — including",
            "# a provider client if you add one (G-02 allows it in your project;",
            "# the generated template ships none).",
            "[project]",
            f'name = "{_paths.slug(stem)}"',
            'version = "0.1.0"',
            'requires-python = ">=3.11"',
            "dependencies = []",
            "",
            "[dependency-groups]",
            'dev = ["get-nick-done", "pytest"]',
            "",
            "[build-system]",
            'requires = ["hatchling"]',
            'build-backend = "hatchling.build"',
            "",
            "[tool.hatch.build.targets.wheel]",
            f'packages = ["{package}"]',
            "",
        ]
    )


def _render_notes(name: str) -> str:
    """The extension seed the skill half writes into."""
    return "\n".join(
        [
            f"# {name} — domain notes",
            "",
            "Created once by `gnd codegen` and never rewritten. This is the",
            "EXTENSION half of the generated skill: everything an LLM authors",
            "lives here, because LLM-authored text is not byte-reproducible and",
            "therefore cannot be digest-gated (G-05).",
            "",
            "Write here: domain vocabulary, worked examples, the traps a reader",
            "of this model falls into. `SKILL.md` links to this file.",
            "",
        ]
    )


def render_architecture_contract(artifact_relpaths: Iterable[str]) -> str:
    """Render the create-once contract seeded from emitted artifact paths."""

    paths = sorted(artifact_relpaths)
    lines = [
        "# Created once by gnd codegen. This file is yours: regeneration never rewrites it.",
        "# Add modules, required_by links, entry points and smoke rows as the project grows.",
        "contract_version: 1",
        "modules: []",
    ]
    if paths:
        lines.append("artifacts:")
        for relpath in paths:
            lines.extend((f"  - path: {relpath}", "    required_by: []"))
    else:
        lines.append("artifacts: []")
    lines.extend(("entry_points: []", "smoke: []"))
    return "\n".join(lines) + "\n"


def render_smoke_module() -> str:
    """Render the create-once smoke module: three lines, all behaviour delegated.

    The blank line between the import block and the executable assignment is
    what ``ruff``'s I001 wants of any module a user later edits
    (``OQ-V5-P4-2``); the module is otherwise identical for every project,
    because everything that varies lives in ``architecture.contract.yaml``.
    """

    return (
        '"""Smoke rows declared in architecture.contract.yaml, run by gnd.archsmoke."""\n'
        "from gnd.archsmoke import build_smoke_module\n"
        "\n"
        "test_smoke, test_smoke_declares_rows, _smoke_floor = build_smoke_module(__file__)\n"
    )


def smoke_module_relpath(discriminator: str) -> str:
    """The one home for the emitted smoke module's path.

    The basename carries the PROJECT-SCOPED discriminator — the slugged
    ``model_id``, see :func:`gnd.codegen.identifiers.smoke_discriminator` —
    because pytest's default import mode requires unique test-module basenames
    across rootdirs without ``__init__``: two projects emitting one shared
    basename abort collection outright, and a create-once file cannot be
    renamed afterwards without overwriting bytes regeneration must never touch
    (v4.0 D-P3.6). The package will not serve: GND's convention names every
    model ``model.orm.yaml``, so every package is ``model`` (v5.1 D-P1.8).
    """

    return f"test_architecture_smoke_{discriminator}.py"


def smoke_module_pattern() -> str:
    """The glob every emitted smoke module matches, whatever its project.

    One home for the shape the migration scan (v5.1 D-P1.8) refuses over: the
    scan is provenance-blind, so it needs to recognise a smoke module by name
    alone, whether GND emitted it or a hand wrote it.
    """

    return "test_architecture_smoke_*.py"


# --------------------------------------------------------------------------
# The emitter
# --------------------------------------------------------------------------


def emit_project(model: Any, model_path: str, *, skill_name: str | None = None) -> GeneratedProject:
    """Describe the whole tree for ``model`` — WITHOUT writing anything.

    The split from :func:`write_project` is load-bearing rather than tidy:
    conformance assertion #3 (plan 06) must recompute the expected surface FROM
    the model to prove the generator emitted something model-relative rather
    than well-formed nothing, and it must be able to do that without producing
    a directory as a side effect.

    Four gates run before returning — every ``.py`` parses, no provider or
    network import is present, the skill document's frontmatter round-trips,
    and the create-once architecture skeleton loads — each raising
    :class:`EmitGateError`.
    """
    from gnd.terms import require_non_temporal

    require_non_temporal(model, "codegen")
    stem = extract_stem(model_path)
    package = module_name(stem)
    posix_model = Path(model_path).as_posix()

    header = header_template(model_path, model)
    artifacts: dict[str, str] = {
        f"{stem}.projection.schema.json": _canonical(project(model)),
        f"{stem}.verbalization.txt": render_verbalization(model),
        f"{stem}.applicable.json": _canonical(applicable_set(model)),
    }
    digests = {
        rel: hashlib.sha256(text.encode("utf-8")).hexdigest() for rel, text in artifacts.items()
    }
    from gnd import resolve_version

    index = _canonical(
        {
            "gnd_version": resolve_version(),
            "model": {
                "path": posix_model,
                "sha256": hashlib.sha256(Path(model_path).read_bytes()).hexdigest(),
            },
            "artifacts": {rel: {"sha256": digest} for rel, digest in digests.items()},
            "header_template": header,
        }
    )
    artifacts[f"{stem}.artifacts.json"] = index
    architecture_artifact_paths = tuple(
        sorted(f"{ARTIFACTS_DIR}/{relpath}" for relpath in artifacts)
    )
    architecture_contract = GeneratedFile(
        relpath=ARCHITECTURE_CONTRACT_DOCUMENT,
        text=render_architecture_contract(architecture_artifact_paths),
        ownership=EXTENSION,
    )

    name = _validated_skill_name(skill_name) if skill_name is not None else _skill_name(stem)
    notes_name = _skill_name(stem)
    files: list[GeneratedFile] = [
        GeneratedFile(
            relpath=f"{package}/__init__.py",
            text=render_package_init(model, model_path=model_path, package=package),
            ownership=DERIVED,
        ),
        GeneratedFile(
            relpath=f"{package}/{TOOLS_MODULE}",
            text=render_tools_module(model, model_path=model_path, package=package),
            ownership=DERIVED,
        ),
        *(
            GeneratedFile(relpath=f"{ARTIFACTS_DIR}/{rel}", text=text, ownership=DERIVED)
            for rel, text in artifacts.items()
        ),
        GeneratedFile(
            relpath=SKILL_DOCUMENT,
            text=render_skill_document(
                model,
                model_path=model_path,
                package=package,
                stem=stem,
                skill_name=name,
            ),
            ownership=DERIVED,
        ),
        architecture_contract,
        GeneratedFile(
            relpath=smoke_module_relpath(
                smoke_discriminator(getattr(model, "model_id", None), package=package)
            ),
            text=render_smoke_module(),
            ownership=EXTENSION,
        ),
        GeneratedFile(
            relpath=f"{REFERENCES_DIR}/{notes_name}-notes.md",
            text=_render_notes(notes_name),
            ownership=EXTENSION,
        ),
        GeneratedFile(
            relpath=PYPROJECT_DOCUMENT,
            text=_render_pyproject(package, stem),
            ownership=EXTENSION,
        ),
    ]

    assert_emitted_python_parses(files)

    offenders = provider_import_offenders({file.relpath: file.text for file in files})
    if offenders:
        raise EmitGateError(
            f"the default generated template imports a provider or network "
            f"library: {offenders}. G-02 permits a USER to add a client to "
            f"their own project; the template GND emits ships none, so this is "
            f"an emitter breach (T-03-16)"
        )

    _assert_frontmatter_round_trips(
        next(file for file in files if file.relpath == SKILL_DOCUMENT),
        expected_name=name,
    )
    try:
        loaded_architecture = parse_architecture_contract_bytes(
            architecture_contract.text.encode("utf-8"),
            source=ARCHITECTURE_CONTRACT_DOCUMENT,
        )
    except ArchitectureContractError as error:
        raise EmitGateError(
            f"the generated {ARCHITECTURE_CONTRACT_DOCUMENT} does not load: {error}"
        ) from error
    expected_architecture_artifacts = tuple(
        (relpath, ()) for relpath in architecture_artifact_paths
    )
    actual_architecture_artifacts = tuple(
        (artifact.path, artifact.required_by) for artifact in loaded_architecture.artifacts
    )
    if (
        loaded_architecture.modules != ()
        or actual_architecture_artifacts != expected_architecture_artifacts
        or loaded_architecture.entry_points != ()
        or loaded_architecture.smoke != ()
    ):
        raise EmitGateError(
            f"the generated {ARCHITECTURE_CONTRACT_DOCUMENT} artifact inventory "
            "does not round-trip to the complete emitted skeleton"
        )

    return GeneratedProject(
        model_path=posix_model,
        package=package,
        stem=stem,
        skill_name=name,
        files=tuple(files),
    )


def _assert_frontmatter_round_trips(skill: GeneratedFile, *, expected_name: str) -> None:
    """Read the emitted ``SKILL.md`` back with the shipped reader, or raise.

    The frontmatter decides whether the generated agent is DISCOVERABLE at all,
    and GND validates frontmatter nowhere else. Emitting it and hoping would
    leave the single most consequential artifact unchecked (RESEARCH §3.3
    candidate 2). Round-tripping through the shipped reader — a temp file,
    because ``read_frontmatter`` guards a PATH (byte cap, then read, then alias
    guard) and reusing that whole posture beats duplicating a slice of it.
    """
    with tempfile.TemporaryDirectory(prefix="gnd-codegen-frontmatter-") as staging:
        probe = Path(staging) / SKILL_DOCUMENT
        probe.write_text(skill.text, encoding="utf-8")
        try:
            mapping, body = read_frontmatter(probe)
        except FrontmatterError as error:
            raise EmitGateError(
                f"the generated {SKILL_DOCUMENT}'s frontmatter does not read "
                f"back ({error}); an undiscoverable skill document must never "
                f"reach disk"
            ) from error
    missing = {"name", "description"} - set(mapping)
    if missing or not body.strip():
        raise EmitGateError(
            f"the generated {SKILL_DOCUMENT} is missing frontmatter keys "
            f"{sorted(missing)} or has an empty body — both make the generated "
            f"agent undiscoverable"
        )
    actual_name = mapping.get("name")
    if actual_name != expected_name:
        raise EmitGateError(
            f"the generated {SKILL_DOCUMENT} declares name {actual_name!r}, not "
            f"its authoritative directory name {expected_name!r}"
        )
    try:
        _validated_skill_name(expected_name)
    except SkillNameError as error:
        raise EmitGateError(str(error)) from error


def _write_staged_file(root_fd: int, relpath: str, text: str) -> PurePosixPath:
    """Write and fsync one planned leaf below a private staging descriptor."""
    from gnd.safefs import FILE_MODE
    from gnd.safefs import descend as _descend
    from gnd.safefs import reject_unsafe_relpath as _reject_unsafe_relpath

    posix = _reject_unsafe_relpath(relpath, source="codegen staging path")
    destination_parent = _descend(root_fd, posix.parts[:-1], create=True)
    handle_fd: int | None = None
    created = False
    try:
        handle_fd = os.open(
            posix.parts[-1],
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            FILE_MODE,
            dir_fd=destination_parent,
        )
        created = True
        try:
            handle = os.fdopen(handle_fd, "wb")
        except BaseException:
            os.close(handle_fd)
            handle_fd = None
            raise
        handle_fd = None  # ownership transferred to ``handle``
        with handle:
            handle.write(text.encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        if created:
            with suppress(OSError):
                os.unlink(posix.parts[-1], dir_fd=destination_parent)
        raise
    finally:
        if handle_fd is not None:
            os.close(handle_fd)
        os.close(destination_parent)
    return posix


def _fsync_directory(fd: int, label: str) -> None:
    """Run one required directory durability barrier with useful context."""
    try:
        os.fsync(fd)
    except OSError as error:
        raise OSError(
            error.errno,
            f"directory durability barrier failed for {label}: {error}",
        ) from error


def _fsync_staged_directories(
    root_fd: int,
    relpaths: list[PurePosixPath],
) -> None:
    """Fsync every staging directory with created entries, bottom-up."""
    from gnd.safefs import descend as _descend

    directories = {posix.parts[:depth] for posix in relpaths for depth in range(len(posix.parts))}
    for parts in sorted(directories, key=lambda value: (-len(value), value)):
        directory_fd = _descend(root_fd, parts, create=False)
        try:
            label = PurePosixPath(*parts).as_posix() if parts else "."
            _fsync_directory(directory_fd, f"staging:{label}")
        finally:
            os.close(directory_fd)


def write_project(
    project_: GeneratedProject,
    out_root: str | Path,
    *,
    manifest_text: str | None = None,
    parent_fd: int | None = None,
    parent_path: Path | None = None,
    root_parts: tuple[str, ...] | None = None,
    root_fd: int | None = None,
) -> list[Path]:
    """Publish ``project_`` under ``out_root`` atomically, or raise.

    Refuses a non-empty target (:class:`ProjectExistsError`) and destroys
    nothing. The nearest existing parent is retained by descriptor, every
    missing directory and staged file is created relative to that identity,
    each file is fsynced, and only then is the whole staged tree published with
    one descriptor-relative ``rename`` — so an interrupted codegen leaves no
    half-written project. ``_cmd_extract`` replaces file by file with its index
    last because its consumers validate that index; a nested tree has no such
    single gate, so directory-granular publication is the equivalent guarantee.

    ``manifest_text`` — plan 03-04's codegen manifest — is staged LAST, after
    every artifact, and published in the SAME directory rename. Both halves of
    that sentence matter. Last, because ``_cmd_extract``'s index-last ordering
    is load-bearing and a manifest describing files that do not exist is worse
    than no manifest. Same replace, because on this path a crash leaves the
    whole staging directory unlinked, so there is no window in which a partial
    tree survives without its record — which is a strictly stronger guarantee
    than ordering alone, and the reason this FRESH path is kept rather than
    folded into ``plan.apply_codegen``'s in-place writer.
    """
    from gnd.codegen.plan import (
        _assert_root_path_bound,
        _bind_codegen_parent,
        _open_codegen_root,
    )
    from gnd.safefs import (
        NO_REPLACE_CONFLICT_ERRNOS as _NO_REPLACE_CONFLICT_ERRNOS,
    )
    from gnd.safefs import (
        InstallPathError as InstallPathError,  # noqa: PLC0414 -- compatibility surface
    )
    from gnd.safefs import (
        descend as _descend,
    )
    from gnd.safefs import (
        reject_unsafe_relpath as _reject_unsafe_relpath,
    )
    from gnd.safefs import (
        rename_noreplace as _rename_noreplace,
    )
    from gnd.safefs import (
        temp_name as _temp_name,
    )

    root = Path(out_root)
    directory_name = Path(os.path.abspath(root)).name
    if directory_name != project_.skill_name:
        raise SkillNameError(
            f"the generated {SKILL_DOCUMENT} declares name {project_.skill_name!r}, "
            f"but its containing directory would be {directory_name!r}; Agent "
            "Skills requires those names to match exactly"
        )

    owned_parent = parent_fd is None
    owned_root = False
    if parent_fd is None:
        parent_path, root_parts, parent_fd = _bind_codegen_parent(root)
        try:
            root_fd = _open_codegen_root(root)
        except FileNotFoundError:
            root_fd = None
        except BaseException:
            os.close(parent_fd)
            raise
        else:
            owned_root = True
    elif parent_path is None or root_parts is None:
        raise ValueError("a retained parent descriptor requires its path and root parts")

    try:
        assert parent_fd is not None
        assert parent_path is not None
        assert root_parts is not None
        if not root_parts:
            raise ValueError("root_parts must name the final output directory")
        if Path(os.path.abspath(root)) != parent_path.joinpath(*root_parts):
            raise InstallPathError(f"output root {root} does not match its retained parent binding")
        current_parent = os.dup(parent_fd)
    except BaseException:
        if owned_root and root_fd is not None:
            os.close(root_fd)
        if owned_parent:
            os.close(parent_fd)
        raise
    staging_fd: int | None = None
    staging_name: str | None = None
    published = False
    created_output_parts: list[tuple[str, ...]] = []
    staged_relpaths: list[PurePosixPath] = []
    try:
        _assert_root_path_bound(parent_path, parent_fd)
        descended_parts: list[str] = []
        for part in root_parts[:-1]:
            try:
                os.mkdir(part, dir_fd=current_parent)
            except FileExistsError as error:
                raise InstallPathError(
                    f"output path component {part!r} appeared after parent binding"
                ) from error
            descended_parts.append(part)
            created_output_parts.append(tuple(descended_parts))
            next_parent = os.open(
                part,
                os.O_RDONLY
                | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_NONBLOCK", 0),
                dir_fd=current_parent,
            )
            os.close(current_parent)
            current_parent = next_parent

        while True:
            candidate = f".{root_parts[-1]}.staging-{_temp_name()[9:]}"
            try:
                os.mkdir(candidate, dir_fd=current_parent)
            except FileExistsError:
                continue
            staging_name = candidate
            break
        try:
            staging_fd = os.open(
                staging_name,
                os.O_RDONLY
                | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_NONBLOCK", 0),
                dir_fd=current_parent,
            )
        except BaseException:
            with suppress(OSError):
                os.rmdir(staging_name, dir_fd=current_parent)
            raise

        written: list[Path] = []
        staged: list[tuple[str, str]] = [(file.relpath, file.text) for file in project_.files]
        if manifest_text is not None:
            from gnd.codegen.manifest import MANIFEST_FILENAME

            staged.append((MANIFEST_FILENAME, manifest_text))
        staged_relpaths = [
            _reject_unsafe_relpath(relpath, source="codegen staging path")
            for relpath, _text in staged
        ]
        for posix, (relpath, text) in zip(staged_relpaths, staged, strict=True):
            _write_staged_file(staging_fd, relpath, text)
            written.append(root / relpath)
        _fsync_staged_directories(staging_fd, staged_relpaths)

        _assert_root_path_bound(root.parent, current_parent)
        root_name = root_parts[-1]
        try:
            current_root_fd = os.open(
                root_name,
                os.O_RDONLY
                | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_NONBLOCK", 0),
                dir_fd=current_parent,
            )
        except FileNotFoundError:
            if root_fd is not None:
                raise InstallPathError(f"output root {root} disappeared before fresh publication")
        except OSError as error:
            raise InstallPathError(
                f"output root {root} became a non-directory or symlink before publication"
            ) from error
        else:
            try:
                if root_fd is None:
                    raise ProjectExistsError(
                        f"{root} appeared before fresh publication; refusing to replace it"
                    )
                expected_info = os.fstat(root_fd)
                current_info = os.fstat(current_root_fd)
                if (current_info.st_dev, current_info.st_ino) != (
                    expected_info.st_dev,
                    expected_info.st_ino,
                ):
                    raise InstallPathError(f"output root {root} changed before fresh publication")
                _assert_root_path_bound(root, current_root_fd)
                if os.listdir(current_root_fd):
                    raise ProjectExistsError(
                        f"{root} exists and is not empty; `gnd codegen` refuses rather "
                        "than writing into an occupied directory"
                    )
            finally:
                os.close(current_root_fd)
            os.rmdir(root_name, dir_fd=current_parent)

        try:
            _rename_noreplace(current_parent, staging_name, current_parent, root_name)
        except OSError as error:
            if error.errno in _NO_REPLACE_CONFLICT_ERRNOS:
                raise ProjectExistsError(
                    f"{root} was claimed during fresh publication; refusing to "
                    "replace the concurrent owner"
                ) from error
            raise
        published = True
        _fsync_directory(current_parent, "publication-parent")
        created_entry_parents = {parts[:-1] for parts in created_output_parts}
        for parts in sorted(created_entry_parents, key=lambda value: (-len(value), value)):
            ancestor_fd = _descend(parent_fd, parts, create=False)
            try:
                label = PurePosixPath(*parts).as_posix() if parts else "."
                _fsync_directory(ancestor_fd, f"output-parent:{label}")
            finally:
                os.close(ancestor_fd)
    finally:
        if staging_fd is not None and not published:
            for posix in reversed(staged_relpaths):
                with suppress(OSError, InstallPathError):
                    cleanup_parent = _descend(staging_fd, posix.parts[:-1], create=False)
                    try:
                        os.unlink(posix.parts[-1], dir_fd=cleanup_parent)
                    finally:
                        os.close(cleanup_parent)
            staged_directories = {
                posix.parts[:depth]
                for posix in staged_relpaths
                for depth in range(1, len(posix.parts))
            }
            for parts in sorted(staged_directories, key=len, reverse=True):
                with suppress(OSError, InstallPathError):
                    cleanup_parent = _descend(staging_fd, parts[:-1], create=False)
                    try:
                        os.rmdir(parts[-1], dir_fd=cleanup_parent)
                    finally:
                        os.close(cleanup_parent)
            if staging_name is not None:
                with suppress(OSError):
                    observed_staging = os.open(
                        staging_name,
                        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
                        dir_fd=current_parent,
                    )
                    try:
                        expected_info = os.fstat(staging_fd)
                        observed_info = os.fstat(observed_staging)
                        if (expected_info.st_dev, expected_info.st_ino) == (
                            observed_info.st_dev,
                            observed_info.st_ino,
                        ):
                            os.rmdir(staging_name, dir_fd=current_parent)
                    finally:
                        os.close(observed_staging)
        if not published:
            for parts in reversed(created_output_parts):
                with suppress(OSError, InstallPathError):
                    cleanup_parent = _descend(parent_fd, parts[:-1], create=False)
                    try:
                        os.rmdir(parts[-1], dir_fd=cleanup_parent)
                    finally:
                        os.close(cleanup_parent)
        if staging_fd is not None:
            os.close(staging_fd)
        os.close(current_parent)
        if owned_root and root_fd is not None:
            os.close(root_fd)
        if owned_parent:
            os.close(parent_fd)
    return written
