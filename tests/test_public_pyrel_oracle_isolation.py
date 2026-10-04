"""Design-rule invariants for the PyRel constraint-oracle seat (default suite).

The agreement lane itself is opt-in (``pytest -m pyrel_oracle``) because it needs
``uv`` and, on a cold cache, the network. That leaves the seat's two design rules
with no case in the default gate:

- **R1 code independence** -- the oracle imports no ``gnd`` module, and reads YAML
  with 1.2 semantics of its own, so a shared loader bug cannot make both sides
  agree.
- **R4 isolation** -- the oracle pins ``relationalai`` exactly, redirects its
  build directory out of the repository, and ``relationalai`` never enters this
  project's environment (it pins ``pydantic<2.13.0``; GND pins ``pydantic==2.13.4``).

These tests run unmarked so the rules hold wherever the suite runs. They are
deliberately structural rather than behavioural: each guards an invariant that is
*itself* textual -- a pin literal, an absent import, a marker exclusion -- and the
lane, not this file, is the behavioural evidence.

**Accepted residuals, stated rather than argued away.** These assertions do NOT
fail on every conceivable rule-breaking edit, and the list is written down rather
than covered by a blanket claim:

- a dependency taken through ``importlib.import_module("gnd.checker")``, or a
  production module loading the oracle under a computed name, defeats any static
  walk;
- a production module that executes the oracle by literal PATH rather than by
  import is not an import and is not seen here;
- ``RAI_BUILD_DIR`` is honoured if a CALLER exports it into the repository -- the
  assertion proves the redirect exists, not that the destination is outside the
  tree;
- the ``addopts`` check is a substring test, so a deliberately perverse marker
  expression such as ``not pyrel_oracle or pyrel_oracle`` would satisfy it while
  selecting the lane.

Each is a real gap; none is closed by this phase. They are repeated in the phase
record's boundary.

Precedent: ``tests/test_derivation_parity.py`` keeps the equivalent DuckDB pin and
absence assertions in the default suite for the same reason.
"""

from __future__ import annotations

import ast
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ORACLE = REPO / "tests" / "oracles" / "pyrel_constraint_oracle.py"
RUNTIME = REPO / "src/gnd/export/pyrel_runtime.py"
PYPROJECT = REPO / "pyproject.toml"
UV_LOCK = REPO / "uv.lock"
PRODUCTION = REPO / "src" / "gnd"

#: The exact PEP 723 pin the seat ships. R4: exact, never a range.
EXPECTED_SCRIPT_DEPENDENCIES = ["relationalai==1.30.1", "ruamel.yaml==0.19.1"]


def _oracle_tree() -> ast.Module:
    return ast.parse(RUNTIME.read_text(encoding="utf-8"), filename=str(RUNTIME))


def _imported_top_level_packages(tree: ast.Module) -> set[str]:
    """Every top-level package name this module imports, at any nesting depth.

    An AST walk, not a substring scan: the oracle's own docstring contains the
    words "imports nothing from gnd", so a text search for ``from gnd`` reports a
    violation against a file that has none.

    Named for the segments it returns, NOT ``_imported_roots``, because
    ``gnd.codegen.emit._imported_roots`` already owns that name and returns
    something different -- the full dotted module name (``gnd.checker``) where
    this returns the first segment (``gnd``). Two functions sharing one name and
    disagreeing on its meaning is how a later reader picks the wrong one. The
    consolidation is a named deferred refactor, not a private cross-boundary
    import.
    """
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def _calls(tree: ast.Module) -> list[ast.Call]:
    return [node for node in ast.walk(tree) if isinstance(node, ast.Call)]


def _script_metadata() -> dict:
    """The PEP 723 inline metadata block, parsed as the TOML it is."""
    lines = ORACLE.read_text(encoding="utf-8").splitlines()
    start = lines.index("# /// script")
    end = next(i for i in range(start + 1, len(lines)) if lines[i].strip() == "# ///")
    body = "\n".join(line[2:] if line.startswith("# ") else line[1:]
                     for line in lines[start + 1:end])
    return tomllib.loads(body)


def test_pyrel_oracle_imports_no_gnd_module() -> None:
    """R1(a): the oracle shares no code with the implementation it checks."""
    wrapper = ast.parse(ORACLE.read_text())
    assert "gnd" not in _imported_top_level_packages(wrapper)
    tree = _oracle_tree()
    assert "gnd" not in _imported_top_level_packages(tree)

    # R1(a), the other half: YAML 1.2 safe semantics of its own, so that the role
    # name `on` loads as the string "on" rather than as a boolean. Scoped to
    # _load_yaml: a safe call anywhere in the file would let the actual loader
    # use an unsafe one and still pass.
    loader = next((node for node in ast.walk(tree)
                   if isinstance(node, ast.FunctionDef) and node.name == "_parse_document"), None)
    assert loader is not None, "the runtime must define _parse_document"
    safe_loads = [
        call for call in ast.walk(loader)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Name) and call.func.id == "YAML"
        and any(kw.arg == "typ" and getattr(kw.value, "value", None) == "safe"
                for kw in call.keywords)
    ]
    assert safe_loads, '_parse_document must load with YAML(typ="safe")'


def test_pyrel_oracle_is_pinned_and_absent_from_the_project_env() -> None:
    """R4: exact pin in the script, and no trace in the project environment."""
    assert _script_metadata()["dependencies"] == EXPECTED_SCRIPT_DEPENDENCIES

    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    # Parsed, not substring-scanned: the pytest marker description names
    # `relationalai` in prose, so a whole-file search false-reds on this repo.
    declared: list[str] = list(project.get("project", {}).get("dependencies", []))
    for group in project.get("dependency-groups", {}).values():
        declared += [entry for entry in group if isinstance(entry, str)]
    for extra in project.get("project", {}).get("optional-dependencies", {}).values():
        declared += list(extra)
    assert not [entry for entry in declared if "relationalai" in entry]
    assert "relationalai" not in UV_LOCK.read_text(encoding="utf-8")

    # R4: no oracle run may litter the repository with PyRel build output.
    redirects = [
        call for call in _calls(_oracle_tree())
        if isinstance(call.func, ast.Attribute) and call.func.attr == "setdefault"
        and call.args and getattr(call.args[0], "value", None) == "RAI_BUILD_DIR"
    ]
    assert redirects, "the oracle must redirect RAI_BUILD_DIR out of the repository"


def test_pyrel_lane_is_deselected_by_default() -> None:
    """The lane's cost is opt-in, the same way the Souffle oracle seat's is."""
    ini = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["tool"]["pytest"]["ini_options"]
    assert "not pyrel_oracle" in ini["addopts"]
    assert any(marker.startswith("pyrel_oracle:") for marker in ini["markers"])


def test_no_production_module_references_the_oracle() -> None:
    """Production purity -- the REVERSE direction of R1, and named as such.

    R1 is about the oracle not depending on GND. This asserts GND does not depend
    on the oracle: nothing shipped may import a test-side instrument. Both
    directions matter; conflating them (as an earlier draft did) hides the fact
    that neither one implies the other.
    """
    offenders: list[str] = []
    for path in sorted(PRODUCTION.rglob("*.py")):
        names: set[str] = set()
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.add(node.module)
                # `from tests.oracles import pyrel_constraint_oracle` names the
                # module in the ALIAS, not in node.module. Recording only the
                # module missed it entirely.
                names.update(f"{node.module}.{alias.name}" for alias in node.names)
        if any("pyrel_constraint_oracle" in name for name in names):
            offenders.append(str(path.relative_to(REPO)))
    assert offenders == []
