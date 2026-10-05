"""PKG-03 guard: every packaged skill instructs the interface a user actually has.

Three regressions this catches, all of which shipped once:

1. A skill telling the reader to run GND **as a Python module**. That only works
   inside a checkout with an activated environment; the installed interface is
   the ``gnd`` console script (D-03, D-13). ``python -m gnd`` keeps working and
   ``__main__.py`` is untouched — it just stops being *documented*.
2. A skill **branching on where the reader is standing** ("inside the repo do
   this, elsewhere do that"). A skill has exactly one instruction for a given
   task (D-13). Two arms means one of them is wrong for whoever is reading.
3. A **working-directory-relative** path to the bundled fallback validator. An
   agent following that instruction from an arbitrary project directory either
   cannot find the script or runs whatever same-named script that project
   supplies (T-01.2-11, rated high). The fix is a skill-relative location the
   agent resolves against the skill's own directory.

Traversal reads the *resource* tree — ``files("gnd") / "skills"`` — with a
``Traversable``-only walk (``iterdir`` / ``is_dir`` / ``read_bytes``, D-19) and
never a repository-relative path, so the guard sees exactly what an installed
user sees. The walk is deliberately local rather than imported from
``tests/test_packaged_skills.py`` or from ``gnd.install``: each guard keeps its
own walk so a bug in one cannot hide inside the other, and importing
``gnd.install`` would make an unordered pair of same-wave plans ordered.
"""
from __future__ import annotations

import re
import shlex
import shutil
import subprocess
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from functools import cache
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path

import pytest

README = Path(__file__).resolve().parent.parent / 'README.md'
MODULE_INVOCATION_RE = re.compile(b'python -m gnd')
BRANCH_RE = re.compile(b'(in|out)side the GND repo|anywhere else', re.IGNORECASE)
FALLBACK_INVOCATION_RE = re.compile(b'(?:uv\\s+run|python3?)\\s+(?:--\\S+\\s+)*([^\\s`\'"]*validate_model\\.py)')
SKILL_RELATIVE_PREFIX = b'<skill-dir>/'
FALLBACK_SCRIPT = 'gnd-model-from-text/scripts/validate_model.py'
NO_INPUT_CODE = b'66'
CAPABILITY_LIMITS = {'layer-2 semantic model rules': b'layer-2 semantic model rules', 'population checking of any kind': b'population checking of any kind', 'model-relative population validation': b'model-relative population validation', 'exit band 4 (indeterminate)': b'band 4', '--format json': b'--format json', 'acceptance_ready': b'acceptance_ready'}
PEP723_REQUIRED_LINES = (b'# /// script', b'# requires-python = ">=3.11"', b'#   "jsonschema==4.26.0",', b'#   "ruamel.yaml==0.19.1",', b'# ///')

def iter_skill_files(root: Traversable, prefix: str='') -> Iterator[tuple[str, Traversable]]:
    """Yield ``(posix-relative-path, Traversable)`` for every file beneath root."""
    for entry in root.iterdir():
        rel = f'{prefix}{entry.name}'
        if entry.is_dir():
            yield from iter_skill_files(entry, f'{rel}/')
        else:
            yield (rel, entry)

def _skills_root() -> Traversable:
    return files('gnd') / 'skills'

def _collect() -> dict[str, Traversable]:
    root = _skills_root()
    if not root.is_dir():
        return {}
    return dict(sorted(iter_skill_files(root)))
SKILL_RESOURCES = _collect()

def _offending_lines(resource: Traversable, pattern: re.Pattern[bytes]) -> list[str]:
    hits = []
    for number, line in enumerate(resource.read_bytes().splitlines(), start=1):
        if pattern.search(line):
            hits.append(f"    line {number}: {line.decode('utf-8', 'replace').strip()}")
    return hits

def test_the_packaged_resource_set_is_non_empty() -> None:
    """Existence asserted separately from content, so an empty walk cannot pass."""
    assert SKILL_RESOURCES, "no resources were found under files('gnd') / 'skills'. Every content assertion below would vacuously pass. The skill tree must live under src/gnd/skills/ so it ships inside the wheel (D-04)."

@pytest.mark.parametrize('rel', sorted(SKILL_RESOURCES))
def test_no_skill_document_instructs_the_module_invocation(rel: str) -> None:
    hits = _offending_lines(SKILL_RESOURCES[rel], MODULE_INVOCATION_RE)
    assert not hits, f'{rel} tells the reader to run GND as a Python module:\n' + '\n'.join(hits) + '\n  Repair: name the installed console script instead — `gnd validate` / `gnd check`. The module form only resolves inside a checkout with an activated environment, and a user who installed GND without cloning it has no such directory (PKG-03, D-13). Drop any `uv run` wrapper too: the binary is on PATH after installation, and a project runner in front of it reintroduces the project-directory assumption by the back door.'

@pytest.mark.parametrize('rel', sorted(SKILL_RESOURCES))
def test_no_skill_document_branches_on_where_the_reader_is(rel: str) -> None:
    hits = _offending_lines(SKILL_RESOURCES[rel], BRANCH_RE)
    assert not hits, f'{rel} branches on whether the reader is inside this repository:\n' + '\n'.join(hits) + '\n  Repair: delete the branch and leave ONE instruction. A skill has exactly one instruction for a given task (D-13). The binary is the instruction; the bundled script is named separately as a zero-install fallback with its limits stated — not as a parallel equal, and never as a condition on where the reader happens to be standing.'

@pytest.mark.parametrize('rel', sorted(SKILL_RESOURCES))
def test_fallback_invocations_are_skill_relative(rel: str) -> None:
    hits = []
    for number, line in enumerate(SKILL_RESOURCES[rel].read_bytes().splitlines(), start=1):
        for match in FALLBACK_INVOCATION_RE.finditer(line):
            path = match.group(1)
            if not path.startswith(SKILL_RELATIVE_PREFIX):
                hits.append(f"    line {number}: {path.decode('utf-8', 'replace')}  (in: {line.decode('utf-8', 'replace').strip()})")
    assert not hits, f'{rel} names the bundled validator by a path that does not resolve from an installed skill directory:\n' + '\n'.join(hits) + f"\n  Repair: name the script by its skill-relative location — `uv run {SKILL_RELATIVE_PREFIX.decode()}scripts/validate_model.py` — and instruct the reader to resolve the skill directory to this skill's own directory. A working-directory-relative path resolves only when the reader happens to be standing in the skill directory; from an arbitrary project it either fails or executes whatever same-named script that project supplies (T-01.2-11, high)."

def test_the_fallback_script_ships_where_the_instructions_point() -> None:
    assert FALLBACK_SCRIPT in SKILL_RESOURCES, f'{FALLBACK_SCRIPT} is absent from the packaged skill tree, so every skill-relative instruction pointing at it is a dead reference.'

def test_packaged_csdp_documents_use_only_steps_zero_through_seven() -> None:
    offenders = []
    for rel, resource in SKILL_RESOURCES.items():
        if not rel.startswith('gnd-model-from-text/') or not rel.endswith('.md'):
            continue
        for number, line in enumerate(resource.read_bytes().splitlines(), start=1):
            if re.search(b'\\bStep 8\\b', line, re.IGNORECASE):
                offenders.append(f"{rel}:{number}: {line.decode('utf-8', 'replace')}")
    assert offenders == [], 'packaged CSDP documents exceed the 0-7 contract:\n' + '\n'.join(offenders)

def _fallback_source() -> bytes:
    assert FALLBACK_SCRIPT in SKILL_RESOURCES, 'see the sibling existence test'
    return SKILL_RESOURCES[FALLBACK_SCRIPT].read_bytes()

def test_fallback_schema_missing_exit_is_outside_the_verdict_bands() -> None:
    source = _fallback_source()
    assert NO_INPUT_CODE in source, f"{FALLBACK_SCRIPT} does not mention exit code {NO_INPUT_CODE.decode()} (EX_NOINPUT). The schema-missing branch must return it and the docstring's exit-code table must list it."
    assert b'EX_NOINPUT' in source, f'{FALLBACK_SCRIPT} returns a bare literal rather than a named constant. Repair: define EX_NOINPUT = 66 so the reason for the choice has somewhere to live next to the value.'
    assert b'EX_USAGE' in source, f"{FALLBACK_SCRIPT} has no EX_USAGE constant, so its argparse usage errors exit 2 — normatively 'vacuous population'. Repair: give it the band-safe parser gnd.cli uses (CR-03)."

@pytest.mark.parametrize('limitation', sorted(CAPABILITY_LIMITS))
def test_fallback_capability_statement_is_complete(limitation: str) -> None:
    source = _fallback_source()
    assert re.search(CAPABILITY_LIMITS[limitation], source, re.IGNORECASE), f"{FALLBACK_SCRIPT}'s capability statement does not name the limitation {limitation!r}. D-14 requires the list in full, and it grew during Phase 01.1 — model-relative population validation, the indeterminate band, the JSON payload and the acceptance flag all postdate the original 'layer 1 only' sentence. Repair: state this limitation explicitly in the module docstring. A fallback whose limits are understated reads as an equivalent of `gnd validate`, which it is not."
FENCE_RE = re.compile('^\\s*```')
PROMPT_RE = re.compile('^\\$\\s+')
GROUPED_COMMANDS = frozenset({'evolve', 'exp', 'recovery', 'review'})
MEASURED_EXECUTABLE_SNIPPETS = 29
MEASURED_SNIPPETS_PER_SKILL = {'gnd-codegen': 5, 'gnd-conformance': 4, 'gnd-dev-session': 1, 'gnd-extract': 2, 'gnd-model-evolve': 6, 'gnd-model-from-code': 4, 'gnd-model-from-text': 1, 'gnd-render-doc': 2, 'gnd-review-panel': 2, 'gnd-review-panel-light': 2}
SKILLS_WITH_EXECUTABLE_SNIPPETS = frozenset(MEASURED_SNIPPETS_PER_SKILL)

@dataclass(frozen=True)
class Snippet:
    """One executable `gnd` command as a packaged document prints it."""
    rel: str
    line: int
    command: str
    skill: str
    tokens: tuple[str, ...]

    @property
    def subcommand_path(self) -> tuple[str, ...]:
        """`('evolve', 'preview')`, `('validate',)` — the help-addressable path."""
        path = [self.tokens[1]]
        if self.tokens[1] in GROUPED_COMMANDS and len(self.tokens) > 2 and (not self.tokens[2].startswith('-')):
            path.append(self.tokens[2])
        return tuple(path)

    @property
    def safe_argv(self) -> tuple[str, ...]:
        """The ONLY form this module ever executes. Nothing document-supplied."""
        return ('gnd', *self.subcommand_path, '--help')

    @property
    def long_options(self) -> tuple[str, ...]:
        return tuple(token.split('=', 1)[0] for token in self.tokens[1:] if token.startswith('--') and token != '--')

    @property
    def ident(self) -> str:
        return f'{self.rel}:{self.line}'

def _iter_executable_snippets() -> Iterator[Snippet]:
    """Every fenced line that runs `gnd`, across the whole packaged tree.

    Fenced blocks only. Inline backticks are deliberately out of scope: the tree
    says "the gnd checker" and "gnd is not a linter" in prose, and a scanner that
    swept those would have to be narrowed with exceptions until it caught
    nothing. A fenced line is what a reader copies.
    """
    for rel, resource in SKILL_RESOURCES.items():
        if not rel.endswith('.md'):
            continue
        in_fence = False
        pending: str | None = None
        pending_line = 0
        for number, raw in enumerate(resource.read_bytes().decode('utf-8', 'replace').splitlines(), start=1):
            if FENCE_RE.match(raw):
                in_fence = not in_fence
                pending = None
                continue
            if not in_fence:
                continue
            text = raw.strip()
            if pending is not None:
                pending = f'{pending[:-1].strip()} {text}'
                if text.endswith('\\'):
                    continue
                command, start = (pending, pending_line)
                pending = None
            else:
                text = PROMPT_RE.sub('', text)
                if not text.startswith('gnd '):
                    continue
                if text.endswith('\\'):
                    pending, pending_line = (text, number)
                    continue
                command, start = (text, number)
            command = re.sub('\\s+#.*$', '', command)
            command = re.split('\\s>\\s*', command)[0]
            command = command.strip()
            yield Snippet(rel=rel, line=start, command=command, skill=rel.split('/')[0], tokens=tuple(shlex.split(command)))
EXECUTABLE_SNIPPETS = tuple(_iter_executable_snippets())

def _gnd_argv() -> list[str]:
    """The installed console script, or the module form as a harness fallback.

    The console script is the documented interface (D-03, D-13) and is what runs
    under `uv run`. The fallback exists so this exerciser can never turn into a
    skip: a skipped safety gate reports green, which is the failure mode this
    whole module is written against.
    """
    executable = shutil.which('gnd')
    if executable is not None:
        return [executable]
    return [sys.executable, '-m', 'gnd']

@cache
def _help(path: tuple[str, ...]) -> tuple[int, str, str]:
    """`gnd <path> --help`, memoised per subcommand path.

    Memoised because 26 snippets resolve to ~13 distinct paths and this module
    runs in the fast lane; the cache keeps the whole exerciser under a second.
    """
    result = subprocess.run([*_gnd_argv(), *path, '--help'], capture_output=True, text=True, check=False)
    return (result.returncode, result.stdout, result.stderr)

def test_executable_snippet_discovery_meets_its_measured_floor() -> None:
    """The gate that stops every gate below from silently disappearing.

    Parametrized tests over an empty sequence report green. If the fence scanner,
    the resource walk or the continuation join breaks, the cases below vanish and
    nothing else in this file notices — so the count is asserted here, in a test
    that has no parameters to lose.
    """
    assert len(EXECUTABLE_SNIPPETS) >= MEASURED_EXECUTABLE_SNIPPETS, f'discovered {len(EXECUTABLE_SNIPPETS)} executable `gnd` snippets in the packaged tree, expected at least {MEASURED_EXECUTABLE_SNIPPETS} (measured 2026-08-14). Either documented commands were deleted, or — far more likely — snippet discovery broke and every invocation case in this module is now passing over an empty list. Repair the scanner; do not lower this floor.'

@pytest.mark.parametrize('snippet', EXECUTABLE_SNIPPETS, ids=[s.ident for s in EXECUTABLE_SNIPPETS])
def test_no_normalized_invocation_carries_anything_the_document_supplied(snippet: Snippet) -> None:
    """T-04-13-03, stated as a property of the normalizer rather than a habit.

    Safety here rests entirely on `safe_argv` discarding every operand, path and
    flag the document printed. That is one line of code and exactly the line a
    future "let's actually run these" change would relax, so it is asserted
    directly: the argv is the literal `gnd`, one or two subcommand words drawn
    from the CLI's own vocabulary, and `--help`. Nothing else, ever.
    """
    argv = snippet.safe_argv
    assert argv[0] == 'gnd'
    assert argv[-1] == '--help', f'{snippet.ident} normalizes to {argv}, which is not a help invocation. Every packaged command must be exercised in help form; the tree documents `gnd review panel` and `gnd exp run`, which spawn reviewer CLIs and session agents respectively.'
    assert len(argv) in (3, 4), f'{snippet.ident} normalizes to {argv}: more than a subcommand path plus `--help`, so something the document supplied is being executed.'
    assert set(argv[1:-1]) <= set(snippet.tokens[1:3]), f"{snippet.ident} normalizes to {argv} with a token drawn from neither of the snippet's two leading positions."
    forbidden = [token for token in argv[1:-1] if token.startswith('-') or '/' in token or '.' in token]
    assert not forbidden, f'{snippet.ident} normalizes to {argv}, which passes {forbidden} through to the process. Subcommand words only: a path, a flag or an operand from a packaged document is untrusted input to a real command.'

@pytest.mark.parametrize('line', PEP723_REQUIRED_LINES)
def test_fallback_pep723_header_is_intact(line: bytes) -> None:
    source = _fallback_source()
    assert line in source, f'{FALLBACK_SCRIPT} is missing the PEP 723 header line {line.decode()!r}. The zero-dependency, zero-install property is the entire reason this file exists: `uv run` reads that header to resolve the two pinned dependencies with no project installation, and the project constraint that a user never runs a package-install step depends on it. Do not edit or unpin the header.'


def test_every_skill_that_documents_commands_still_contributes_snippets() -> None:
    """A per-skill floor and an exact skill SET.

    The total above is satisfied by one skill growing while another's examples
    disappear. This names the skill, and the set half asserts that `gnd-orm-core`
    contributes nothing: it is the references-only library, and a command
    appearing there is a workflow instruction that has leaked onto the reference
    shelf (04-12).
    """
    per_skill: dict[str, int] = {}
    for snippet in EXECUTABLE_SNIPPETS:
        per_skill[snippet.skill] = per_skill.get(snippet.skill, 0) + 1

    assert set(per_skill) == SKILLS_WITH_EXECUTABLE_SNIPPETS, (
        f"skills carrying executable commands are {sorted(per_skill)}, expected "
        f"{sorted(SKILLS_WITH_EXECUTABLE_SNIPPETS)}.\n"
        f"  stopped contributing: {sorted(SKILLS_WITH_EXECUTABLE_SNIPPETS - set(per_skill))}\n"
        f"  newly contributing:   {sorted(set(per_skill) - SKILLS_WITH_EXECUTABLE_SNIPPETS)}\n"
        "gnd-orm-core is absent on purpose — it is references-only."
    )
    short = {
        skill: (count, MEASURED_SNIPPETS_PER_SKILL[skill])
        for skill, count in per_skill.items()
        if count < MEASURED_SNIPPETS_PER_SKILL[skill]
    }
    assert not short, (
        "skills now document fewer runnable commands than were measured "
        f"(found, expected at least): {short}. A skill losing its examples is a "
        "documentation regression that no count over the whole tree catches."
    )
