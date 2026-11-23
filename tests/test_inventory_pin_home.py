"""The packaged-skill inventory has one home (pins-and-review-check PF1).

The file count, skill names and file set used to be copied into four test
files. A new packaged file was then counted in some copies and not others, and
two of them sat red on main. ``tests/test_packaged_skills.py`` now defines the
inventory and checks the packaged tree against it; every other test imports it.
This file fails when a test module binds one of the inventory names, in any
scope and by any binding form, other than by importing it from the home.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = "tests/test_packaged_skills.py"
NAMES = frozenset({"EXPECTED_SKILL_FILE_COUNT", "EXPECTED_SKILL_NAMES", "EXPECTED_SKILL_FILES"})
#: Files allowed to bind an inventory name of their own, with the reason (plan D5).
EXCEPTIONS = {
    "tests/test_public_distribution_runtime.py": "pins the inventory of a released wheel, not of the tree",
}


#: Type-parameter nodes exist from Python 3.12; on older versions the tuple is empty.
_TYPE_PARAMS = tuple(getattr(ast, kind) for kind in ("TypeVar", "TypeVarTuple", "ParamSpec") if hasattr(ast, kind))


def _bindings(tree: ast.AST) -> list[tuple[str, str | None]]:
    """Every name the source binds, in any scope, with the module it is imported from.

    The binding constructs are those of the language reference, "Naming and
    binding" (section 4.2.1): a target in store context (assignment, augmented
    and walrus targets, ``for``, ``with`` and comprehension targets, ``global``
    writes), a function or lambda parameter, a type parameter, an import alias,
    a ``def`` or ``class`` name, an ``except ... as`` name and a ``match``
    capture. A bare annotation (``X: int``) binds nothing, so its target is
    skipped. The second item is the importing module for an import alias and
    None for every other binding.
    """
    bare_annotations = {
        id(node.target) for node in ast.walk(tree) if isinstance(node, ast.AnnAssign) and node.value is None
    }
    found: list[tuple[str, str | None]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Store) and id(node) not in bare_annotations:
                found.append((node.id, None))
        elif isinstance(node, ast.Import):
            found.extend(((alias.asname or alias.name).split(".")[0], None) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            origin = node.module if node.level == 0 else None
            found.extend((alias.asname or alias.name, origin if alias.asname in (None, alias.name) else None)
                         for alias in node.names)
        elif isinstance(node, ast.arg):
            found.append((node.arg, None))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, *_TYPE_PARAMS)):
            found.append((node.name, None))
        elif isinstance(node, (ast.ExceptHandler, ast.MatchAs, ast.MatchStar)):
            if node.name:
                found.append((node.name, None))
        elif isinstance(node, ast.MatchMapping) and node.rest:
            found.append((node.rest, None))
    return found


def inventory_bindings(source: str) -> set[str]:
    """Inventory names the source binds other than by importing them, unrenamed, from the home."""
    home = Path(HOME).stem
    return {name for name, origin in _bindings(ast.parse(source)) if name in NAMES and origin != home}


def test_the_inventory_has_one_home() -> None:
    offenders = {}
    for path in sorted((ROOT / "tests").rglob("*.py")):
        name = path.relative_to(ROOT).as_posix()
        if name in (HOME, *EXCEPTIONS):
            continue
        pins = inventory_bindings(path.read_text(encoding="utf-8"))
        if pins:
            offenders[name] = sorted(pins)
    assert not offenders, (
        f"import the packaged-skill inventory from {HOME} instead of defining it: {offenders}"
    )
    assert inventory_bindings((ROOT / HOME).read_text(encoding="utf-8")) == NAMES


def test_every_exception_still_exists() -> None:
    missing = [name for name in EXCEPTIONS if not (ROOT / name).is_file()]
    assert not missing, f"remove stale exceptions: {missing}"


def test_the_guard_sees_every_binding_form() -> None:
    bound = [
        "EXPECTED_SKILL_FILE_COUNT = 1",
        "EXPECTED_SKILL_NAMES: frozenset[str] = frozenset()",
        "OTHER, EXPECTED_SKILL_FILES = 1, set()",
        "[EXPECTED_SKILL_NAMES, *REST] = [1, 2]",
        "EXPECTED_SKILL_FILES |= {'a'}",
        "if True:\n    EXPECTED_SKILL_FILE_COUNT = 1",
        "try:\n    pass\nexcept ImportError:\n    EXPECTED_SKILL_NAMES = frozenset()",
        "(EXPECTED_SKILL_FILE_COUNT := 1)",
        # Review round 1, F1 and F2: binding forms the first guard missed.
        "def helper(value=(EXPECTED_SKILL_FILE_COUNT := 999)):\n    pass",
        "for EXPECTED_SKILL_FILE_COUNT in (999,):\n    pass",
        "with open('x') as EXPECTED_SKILL_NAMES:\n    pass",
        "match 1:\n    case EXPECTED_SKILL_FILES:\n        pass",
        "match {}:\n    case {**EXPECTED_SKILL_FILES}:\n        pass",
        "match []:\n    case [*EXPECTED_SKILL_FILES]:\n        pass",
        "def EXPECTED_SKILL_NAMES():\n    pass",
        "class EXPECTED_SKILL_NAMES:\n    pass",
        "try:\n    pass\nexcept Exception as EXPECTED_SKILL_NAMES:\n    pass",
        "def f():\n    global EXPECTED_SKILL_FILE_COUNT\n    EXPECTED_SKILL_FILE_COUNT = 1",
        "[(EXPECTED_SKILL_FILES := x) for x in (1,)]",
        # A copy in any scope is a copy.
        "def f():\n    EXPECTED_SKILL_FILE_COUNT = 1",
        "class C:\n    EXPECTED_SKILL_NAMES = frozenset()",
        # Imported, but not from the home or under another name.
        "from test_install import EXPECTED_SKILL_FILE_COUNT",
        "from test_packaged_skills import EXPECTED_SKILL_NAMES as EXPECTED_SKILL_FILES",
        "import EXPECTED_SKILL_NAMES",
        "from test_packaged_skills import EXPECTED_SKILL_FILE_COUNT\nEXPECTED_SKILL_FILE_COUNT = 1",
        # Review round 2, F1: parameters of every kind.
        "def f(EXPECTED_SKILL_FILE_COUNT=999):\n    return EXPECTED_SKILL_FILE_COUNT",
        "def f(EXPECTED_SKILL_FILE_COUNT, /):\n    pass",
        "def f(*, EXPECTED_SKILL_NAMES):\n    pass",
        "def f(*EXPECTED_SKILL_FILES):\n    pass",
        "def f(**EXPECTED_SKILL_FILES):\n    pass",
        "async def f(EXPECTED_SKILL_NAMES):\n    pass",
        "g = lambda EXPECTED_SKILL_FILE_COUNT: 0",
        # Review round 2, F3: one good alias does not excuse another in the same statement.
        (
            "from test_packaged_skills import (\n    EXPECTED_SKILL_FILE_COUNT,\n"
            "    EXPECTED_SKILL_NAMES as EXPECTED_SKILL_FILE_COUNT,\n)"
        ),
        "from .test_packaged_skills import EXPECTED_SKILL_FILE_COUNT",
    ]
    if sys.version_info >= (3, 12):
        # Review round 2, F2: type parameters.
        bound += [
            "def f[EXPECTED_SKILL_FILES]():\n    return EXPECTED_SKILL_FILES",
            "class C[*EXPECTED_SKILL_NAMES]:\n    pass",
            "type Alias[**EXPECTED_SKILL_FILE_COUNT] = int",
        ]
    for source in bound:
        assert inventory_bindings(source), source
    not_bound = [
        "from test_packaged_skills import EXPECTED_SKILL_FILE_COUNT",
        "from test_packaged_skills import EXPECTED_SKILL_FILES, EXPECTED_SKILL_NAMES",
        "from test_packaged_skills import (\n    EXPECTED_SKILL_FILE_COUNT,\n    EXPECTED_SKILL_NAMES,\n)",
        "from test_packaged_skills import EXPECTED_SKILL_NAMES as EXPECTED_SKILL_NAMES",
        "def f(count=EXPECTED_SKILL_FILE_COUNT):\n    return count",
        # Review round 1, F3: a bare annotation binds nothing.
        "from test_packaged_skills import EXPECTED_SKILL_FILE_COUNT\nEXPECTED_SKILL_FILE_COUNT: int",
        "assert len(found) == EXPECTED_SKILL_FILE_COUNT",
        "del EXPECTED_SKILL_NAMES",
        "OTHER_COUNT = 71",
        "x = 'EXPECTED_SKILL_FILE_COUNT = 1'",
    ]
    for source in not_bound:
        assert not inventory_bindings(source), source
