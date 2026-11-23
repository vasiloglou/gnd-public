"""The packaged-skill inventory has one home (pins-and-review-check PF1).

The file count, skill names and file set used to be copied into four test
files. A new packaged file was then counted in some copies and not others, and
two of them sat red on main. ``tests/test_packaged_skills.py`` now defines the
inventory and checks the packaged tree against it; every other test imports it.
This file fails when a test module binds one of the inventory names again.
"""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = "tests/test_packaged_skills.py"
NAMES = frozenset({"EXPECTED_SKILL_FILE_COUNT", "EXPECTED_SKILL_NAMES", "EXPECTED_SKILL_FILES"})
#: Files allowed to bind an inventory name of their own, with the reason (plan D5).
EXCEPTIONS = {
    "tests/test_public_distribution_runtime.py": "pins the inventory of a released wheel, not of the tree",
}


def _bound_names(target: ast.expr) -> set[str]:
    if isinstance(target, ast.Name):
        return {target.id}
    if isinstance(target, (ast.Tuple, ast.List)):
        return set().union(*(_bound_names(element) for element in target.elts))
    if isinstance(target, ast.Starred):
        return _bound_names(target.value)
    return set()


_NEW_SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)


def _module_scope(node: ast.AST):
    """Every node in the module's own scope: nested blocks yes, function and class bodies no."""
    for child in ast.iter_child_nodes(node):
        if isinstance(child, _NEW_SCOPES):
            continue
        yield child
        yield from _module_scope(child)


def module_level_pins(source: str) -> set[str]:
    """Inventory names bound in module scope by an assignment of any form."""
    found: set[str] = set()
    for node in _module_scope(ast.parse(source)):
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign, ast.NamedExpr)):
            targets = [node.target]
        else:
            continue
        for target in targets:
            found |= _bound_names(target) & NAMES
    return found


def test_the_inventory_has_one_home() -> None:
    offenders = {}
    for path in sorted((ROOT / "tests").rglob("*.py")):
        name = path.relative_to(ROOT).as_posix()
        if name in (HOME, *EXCEPTIONS):
            continue
        pins = module_level_pins(path.read_text(encoding="utf-8"))
        if pins:
            offenders[name] = sorted(pins)
    assert not offenders, (
        f"import the packaged-skill inventory from {HOME} instead of defining it: {offenders}"
    )
    assert module_level_pins((ROOT / HOME).read_text(encoding="utf-8")) == NAMES


def test_every_exception_still_exists() -> None:
    missing = [name for name in EXCEPTIONS if not (ROOT / name).is_file()]
    assert not missing, f"remove stale exceptions: {missing}"


def test_the_guard_sees_every_assignment_form() -> None:
    bound = [
        "EXPECTED_SKILL_FILE_COUNT = 1",
        "EXPECTED_SKILL_NAMES: frozenset[str] = frozenset()",
        "OTHER, EXPECTED_SKILL_FILES = 1, set()",
        "[EXPECTED_SKILL_NAMES, *REST] = [1, 2]",
        "EXPECTED_SKILL_FILES |= {'a'}",
        "if True:\n    EXPECTED_SKILL_FILE_COUNT = 1",
        "try:\n    pass\nexcept ImportError:\n    EXPECTED_SKILL_NAMES = frozenset()",
        "(EXPECTED_SKILL_FILE_COUNT := 1)",
    ]
    for source in bound:
        assert module_level_pins(source), source
    not_bound = [
        "from test_packaged_skills import EXPECTED_SKILL_FILE_COUNT",
        "def f():\n    EXPECTED_SKILL_FILE_COUNT = 1",
        "class C:\n    EXPECTED_SKILL_NAMES = frozenset()",
        "assert len(found) == EXPECTED_SKILL_FILE_COUNT",
        "OTHER_COUNT = 71",
    ]
    for source in not_bound:
        assert not module_level_pins(source), source
