"""Fresh collection must agree with the public snapshot and stay target-owned."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from support.public_migration import load_case_map

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / ".gnd-planning/milestones/public-launch/migration"


def _assert_collection_matches(observed: dict, expected: dict) -> None:
    assert set(observed) == set(expected) == {"status", "selected", "deselected"}
    assert observed["status"] == expected["status"] == "collection-only; not execution"
    seen: set[str] = set()
    for lane in ("selected", "deselected"):
        rows = observed[lane]
        assert isinstance(rows, list)
        for row in rows:
            assert set(row) == {"node", "markers"}
            assert row["node"] not in seen, "duplicate collected node"
            seen.add(row["node"])
            path = Path(row["node"].split("::", 1)[0])
            assert not path.is_absolute() and ".." not in path.parts
            assert path.parts[0] == "tests", "non-public test root"
            assert row["markers"] == sorted(set(row["markers"]))
        assert rows == expected[lane], f"{lane} collection differs from recorded snapshot"


def collect_current(tmp_path: Path) -> dict:
    output = tmp_path / "collection.json"
    script = r'''
import json, pathlib, sys, pytest
root = pathlib.Path(sys.argv[1]).resolve()
output = pathlib.Path(sys.argv[2])
class Collector:
    def __init__(self): self.deselected = []
    def pytest_deselected(self, items): self.deselected.extend(items)
    def pytest_collection_finish(self, session):
        for name, module in tuple(sys.modules.items()):
            if name == 'gnd' or name.startswith('gnd.'):
                filename = getattr(module, '__file__', None)
                if filename:
                    assert pathlib.Path(filename).resolve().is_relative_to(root / 'src' / 'gnd'), name
        hooks = {name for name in sys.modules if name.endswith('conftest')}
        for name in hooks:
            assert pathlib.Path(sys.modules[name].__file__).resolve().is_relative_to(root / 'tests'), name
        def row(item):
            assert pathlib.Path(item.path).resolve().is_relative_to(root / 'tests'), item.nodeid
            return {'node': item.nodeid, 'markers': sorted({m.name for m in item.iter_markers()})}
        data = {'status': 'collection-only; not execution', 'selected': [row(x) for x in session.items], 'deselected': [row(x) for x in self.deselected]}
        output.write_text(json.dumps(data))
raise SystemExit(pytest.main(['--collect-only', '-q', '--rootdir', str(root), '-c', str(root / 'pyproject.toml'), '--confcutdir', str(root / 'tests'), str(root / 'tests')], plugins=[Collector()]))
'''
    env = os.environ.copy()
    for name in ("PYTHONPATH", "PYTHONHOME", "PYTEST_ADDOPTS", "PYTEST_PLUGINS", "VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT"):
        env.pop(name, None)
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    result = subprocess.run([sys.executable, "-c", script, str(ROOT), str(output)], cwd=ROOT, env=env, capture_output=True, text=True, timeout=60, check=False)
    assert result.returncode == 0, result.stdout[-4000:] + result.stderr[-4000:]
    return json.loads(output.read_text())


def test_current_collection_has_target_owned_modules_and_hooks(tmp_path):
    observed = collect_current(tmp_path)
    nodes = [row["node"] for row in observed["selected"]]
    assert nodes and len(nodes) == len(set(nodes))
    assert "tests/test_public_collection.py::test_current_collection_has_target_owned_modules_and_hooks" in nodes


@pytest.mark.evidence
def test_fresh_target_collection_matches_exact_nodes_markers_and_origins(tmp_path):
    expected, = load_case_map(MIGRATION / "collection.json.gz")
    _assert_collection_matches(collect_current(tmp_path), expected)


@pytest.mark.parametrize("mutation", ["missing", "extra", "marker", "duplicate", "private-root", "lane"])
def test_collection_comparison_rejects_drift(mutation: str) -> None:
    import copy
    expected = {"status": "collection-only; not execution", "selected": [{"node": "tests/test_example.py::test_example", "markers": []}], "deselected": []}
    observed = copy.deepcopy(expected)
    if mutation == "missing": observed["selected"] = []
    elif mutation == "extra": observed["selected"].append({"node": "tests/test_extra.py::test_extra", "markers": []})
    elif mutation == "marker": observed["selected"][0]["markers"] = ["slow"]
    elif mutation == "duplicate": observed["selected"] *= 2
    elif mutation == "private-root": observed["selected"][0]["node"] = "../private/test_example.py::test_example"
    elif mutation == "lane": observed["deselected"] = observed["selected"]; observed["selected"] = []
    with pytest.raises(AssertionError):
        _assert_collection_matches(observed, expected)


def test_public_bootstrap_has_no_historical_session_or_collection_hooks() -> None:
    for path in (ROOT / "tests").rglob("conftest.py"):
        tree = ast.parse(path.read_text())
        names = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        assert not names & {"pytest_sessionstart", "pytest_collection_modifyitems", "pytest_collect_file"}, path.relative_to(ROOT)
