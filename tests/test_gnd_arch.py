"""Tests for tools/gnd_arch.py (code-refactoring milestone, phase RF0).

Case ids follow notes/phase-RF0-spec.md section 8.1. Fixture packages are
generated in tmp_path so hostile or unparsable sources never reach the
repository's lint or manifest surfaces.
"""

import importlib.util
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location("gnd_arch", ROOT / "tools" / "gnd_arch.py")
arch = importlib.util.module_from_spec(_SPEC)
sys.modules["gnd_arch"] = arch
_SPEC.loader.exec_module(arch)

LAYERS = [
    {"name": "infrastructure", "rank": 0},
    {"name": "model", "rank": 1},
    {"name": "checking", "rank": 2},
    {"name": "semantics", "rank": 3},
    {"name": "lanes", "rank": 4},
    {"name": "entry", "rank": 5},
]


def make_map(modules, patterns=None, lanes=("alpha", "beta")):
    entries = {}
    for name, value in modules.items():
        if isinstance(value, tuple):
            entries[name] = {"layer": value[0], "lane": value[1]}
        else:
            entries[name] = {"layer": value}
    return {
        "schema_version": 1,
        "excluded": ["src/gnd/examples/**", "src/gnd/skills/**"],
        "layers": LAYERS,
        "lanes": list(lanes),
        "modules": entries,
        "declared_clean": [],
        "allow_list": [],
        "helper_patterns": patterns or {},
    }


def make_tree(tmp_path, files, layer_map=None, layers=None):
    """files: repo-relative path -> text. Modules under src/gnd default to infrastructure."""
    root = tmp_path / "repo"
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    if layer_map is None:
        modules = arch.discover_modules(root, ["src/gnd/examples/**", "src/gnd/skills/**"])
        layer_map = make_map({m: (layers or {}).get(m, "infrastructure") for m in modules})
    map_path = tmp_path / "layers.json"
    map_path.write_text(json.dumps(layer_map) if not isinstance(layer_map, str) else layer_map)
    return root, map_path


def run_measure(root, map_path, out):
    return arch.main(["measure", "--root", str(root), "--layers", str(map_path), "--out", str(out)])


def measured(tmp_path, files, **kwargs):
    root, map_path = make_tree(tmp_path, files, **kwargs)
    out = tmp_path / "out.json"
    assert run_measure(root, map_path, out) == 0
    return json.loads(out.read_text())


def line_of(text, snippet):
    return next(i for i, line in enumerate(text.splitlines(), 1) if snippet in line)


def edge_set(data, source):
    return {(e["to"], e["kind"], e["line"]) for e in data["edges"] if e["from"] == source}


# ---------------------------------------------------------------- T1, T12


def test_t1_t12_repository_measure_is_deterministic_and_bounded(tmp_path):
    first, second = tmp_path / "a.json", tmp_path / "b.json"
    started = time.monotonic()
    assert arch.main(["measure", "--out", str(first)]) == 0
    elapsed = time.monotonic() - started
    assert arch.main(["measure", "--out", str(second)]) == 0
    assert first.read_bytes() == second.read_bytes()
    assert elapsed <= 30, elapsed
    data = json.loads(first.read_text())
    assert data["skills"]["module_citations"], "repository skills cite modules"
    assert data["query_sites"]["fact_types_reads"] and data["query_sites"]["get_roles_calls"]


# ---------------------------------------------------------------- T2 edge kinds

A_SOURCE = """\
import gnd.b
from gnd import c
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gnd import d
try:
    from gnd import e
except ImportError:
    e = None
class K:
    from gnd import f
def g():
    from gnd import h
    return h
x = __import__("gnd.i")
import importlib
y = importlib.import_module("gnd.j")
def dyn(name):
    return importlib.import_module(name)
def query(model, row):
    return model.fact_types, row.get("roles")
"""


def edge_files():
    files = {"src/gnd/__init__.py": "", "src/gnd/a.py": A_SOURCE}
    for name in "bcdefhij":
        files[f"src/gnd/{name}.py"] = ""
    files["src/gnd/skills/s/SKILL.md"] = "See src/gnd/a.py and gnd.b here.\n"
    files["src/gnd/skills/s/scripts/tool.py"] = "import gnd.b\n"
    return files


def test_t2a_to_t2h_edge_kinds(tmp_path):
    data = measured(tmp_path, edge_files())
    at = lambda snippet: line_of(A_SOURCE, snippet)
    assert edge_set(data, "gnd.a") == {
        ("gnd.b", "module", at("import gnd.b")),
        ("gnd.c", "module", at("from gnd import c")),
        ("gnd.d", "type_only", at("from gnd import d")),
        ("gnd.e", "module", at("from gnd import e")),
        ("gnd.f", "module", at("from gnd import f")),
        ("gnd.h", "lazy", at("from gnd import h")),
        ("gnd.i", "dynamic", at('__import__("gnd.i")')),
        ("gnd.j", "dynamic", at('import_module("gnd.j")')),
    }
    assert data["unresolved_dynamic"] == [{"from": "gnd.a", "line": at("import_module(name)")}]
    assert data["query_sites"]["fact_types_reads"] == [
        {"module": "gnd.a", "line": at("fact_types")}
    ]
    assert data["query_sites"]["get_roles_calls"] == [{"module": "gnd.a", "line": at("fact_types")}]
    assert data["skills"]["module_citations"] == [
        {"file": "src/gnd/skills/s/SKILL.md", "line": 1, "cites": "gnd.b"},
        {"file": "src/gnd/skills/s/SKILL.md", "line": 1, "cites": "src/gnd/a.py"},
    ]
    assert "gnd.skills.s.scripts.tool" not in {m["module"] for m in data["modules"]}


def test_t2_relative_imports(tmp_path):
    files = {
        "src/gnd/__init__.py": "",
        "src/gnd/pkg/__init__.py": "from . import x\n",
        "src/gnd/pkg/x.py": "def thing():\n    return 1\n",
        "src/gnd/pkg/sub/__init__.py": "",
        "src/gnd/pkg/sub/y.py": "from ..x import thing\nfrom .. import x\n",
    }
    data = measured(tmp_path, files)
    assert edge_set(data, "gnd.pkg") == {("gnd.pkg.x", "module", 1)}
    assert edge_set(data, "gnd.pkg.sub.y") == {
        ("gnd.pkg.x", "module", 1),
        ("gnd.pkg.x", "module", 2),
    }


def test_t2i_relative_import_above_root_exits_3(tmp_path, capsys):
    files = {"src/gnd/__init__.py": "", "src/gnd/top.py": "from .. import nothing\n"}
    root, map_path = make_tree(tmp_path, files)
    assert run_measure(root, map_path, tmp_path / "out.json") == 3
    assert "src/gnd/top.py" in capsys.readouterr().err
    assert not (tmp_path / "out.json").exists()


def test_t2j_from_import_targets_submodule_or_package(tmp_path):
    files = {
        "src/gnd/__init__.py": "",
        "src/gnd/x/__init__.py": "def func():\n    return 1\n",
        "src/gnd/x/y.py": "",
        "src/gnd/user.py": "from gnd.x import y\nfrom gnd.x import func\n",
    }
    data = measured(tmp_path, files)
    assert edge_set(data, "gnd.user") == {("gnd.x.y", "module", 1), ("gnd.x", "module", 2)}


# ---------------------------------------------------------------- T3 SCC


def scc_files(b_source):
    return {"src/gnd/__init__.py": "", "src/gnd/a.py": "import gnd.b\n", "src/gnd/b.py": b_source}


def test_t3a_lazy_cycle_is_runtime_only(tmp_path):
    data = measured(tmp_path, scc_files("def f():\n    import gnd.a\n"))
    assert data["sccs"] == {"runtime": [["gnd.a", "gnd.b"]], "module_only": []}


def test_t3b_type_only_cycle_is_ignored(tmp_path):
    source = "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    import gnd.a\n"
    data = measured(tmp_path, scc_files(source))
    assert data["sccs"] == {"runtime": [], "module_only": []}


def test_t3c_module_cycle_is_in_both(tmp_path):
    data = measured(tmp_path, scc_files("import gnd.a\n"))
    assert data["sccs"] == {"runtime": [["gnd.a", "gnd.b"]], "module_only": [["gnd.a", "gnd.b"]]}


# ---------------------------------------------------------------- T4 private imports


def test_t4_private_imports(tmp_path):
    files = {
        "src/gnd/__init__.py": "",
        "src/gnd/q.py": "_x = 1\n__y__ = 2\n_w = 3\n",
        "src/gnd/p.py": (
            "from gnd.q import _x, __y__\nfrom gnd.p import _z\nimport gnd.q as qq\n_z = qq._w\n"
        ),
    }
    data = measured(tmp_path, files)
    assert data["private_imports"] == [
        {"from": "gnd.p", "to": "gnd.q", "name": "_x", "line": 1, "kind": "from_import"},
        {"from": "gnd.p", "to": "gnd.q", "name": "_w", "line": 4, "kind": "attribute"},
    ]


# ---------------------------------------------------------------- T5 duplicates


def test_t5_duplicates_and_families(tmp_path):
    files = {
        "src/gnd/__init__.py": "",
        "src/gnd/d1.py": 'def fam_one(a):\n    """doc"""\n    return a + 1\n',
        "src/gnd/d2.py": "def fam_two(a):\n    return a + 1\n",
        "src/gnd/d3.py": "def fam_three(a):\n    return a + 2\n",
    }
    root, _ = make_tree(tmp_path, files)
    modules = arch.discover_modules(root, [])
    map_path = tmp_path / "layers2.json"
    map_path.write_text(
        json.dumps(make_map({m: "infrastructure" for m in modules}, {"fam": "^fam_"}))
    )
    out = tmp_path / "out.json"
    assert run_measure(root, map_path, out) == 0
    data = json.loads(out.read_text())
    groups = [g["sites"] for g in data["duplicates"]["ast_identical"]]
    assert groups == [["gnd.d1:fam_one:1", "gnd.d2:fam_two:1"]]  # T5a, T5b
    (family,) = data["duplicates"]["families"]
    assert family["family"] == "fam" and len(family["sites"]) == 3
    assert family["distinct_hashes"] == 2  # T5c


# ---------------------------------------------------------------- T6 layering


def test_t6_layering(tmp_path):
    files = {
        "src/gnd/__init__.py": "",
        "src/gnd/low.py": "import gnd.mid\nimport gnd.peer\n",
        "src/gnd/peer.py": "",
        "src/gnd/mid.py": "",
        "src/gnd/la.py": "import gnd.lb\n",
        "src/gnd/lb.py": "",
    }
    layers = {
        "gnd": "infrastructure",
        "gnd.low": "infrastructure",
        "gnd.peer": "infrastructure",
        "gnd.mid": "checking",
        "gnd.la": ("lanes", "alpha"),
        "gnd.lb": ("lanes", "beta"),
    }
    root, map_path = make_tree(tmp_path, files, layer_map=make_map(layers))
    out = tmp_path / "out.json"
    assert run_measure(root, map_path, out) == 0
    layering = json.loads(out.read_text())["layering"]
    assert [(e["from"], e["to"]) for e in layering["wrong_way"]] == [("gnd.low", "gnd.mid")]
    assert layering["wrong_way"][0]["from_layer"] == "infrastructure"
    assert [(e["from"], e["to"]) for e in layering["cross_lane"]] == [("gnd.la", "gnd.lb")]
    assert "infrastructure" not in layering["clean_layers"]
    assert set(layering["clean_layers"]) == {"model", "checking", "semantics", "lanes", "entry"}


# ---------------------------------------------------------------- T7 layer map

BASIC = {"src/gnd/__init__.py": "", "src/gnd/a.py": ""}


@pytest.mark.parametrize(
    "mutate, needle",
    [
        (lambda m: m["modules"].pop("gnd.a"), "misses modules: gnd.a"),  # T7a
        (lambda m: m["modules"].update({"gnd.ghost": {"layer": "model"}}), "gnd.ghost"),  # T7b
        (lambda m: m["modules"].update({"gnd.a": {"layer": "nowhere"}}), "unknown layer"),  # T7c
        (lambda m: m["modules"].update({"gnd.a": {"layer": "model", "lane": "alpha"}}), "lane"),
        (lambda m: m["modules"].update({"gnd.a": {"layer": "lanes"}}), "known lane"),
        (
            lambda m: m["modules"].update({"gnd.a": {"layer": "lanes", "lane": "zeta"}}),
            "known lane",
        ),
    ],
)
def test_t7a_to_t7c_invalid_maps_exit_3(tmp_path, capsys, mutate, needle):
    layer_map = make_map({"gnd": "infrastructure", "gnd.a": "infrastructure"})
    mutate(layer_map)
    root, map_path = make_tree(tmp_path, BASIC, layer_map=layer_map)
    assert run_measure(root, map_path, tmp_path / "out.json") == 3
    assert needle in capsys.readouterr().err


def test_t7d_t7f_repository_map_covers_every_module(tmp_path):
    layer_map = json.loads((ROOT / "tools" / "gnd_layers.json").read_text())
    assert layer_map["excluded"] == ["src/gnd/examples/**", "src/gnd/skills/**"]
    discovered = arch.discover_modules(ROOT, layer_map["excluded"])
    assert set(discovered) == set(layer_map["modules"])
    assert not any(
        path.startswith(("src/gnd/skills/", "src/gnd/examples/")) for path in discovered.values()
    )


def test_t7e_repository_map_missing_entry_exits_3(tmp_path, capsys):
    layer_map = json.loads((ROOT / "tools" / "gnd_layers.json").read_text())
    layer_map["modules"].pop("gnd.cli")
    map_path = tmp_path / "layers.json"
    map_path.write_text(json.dumps(layer_map))
    out = tmp_path / "out.json"
    assert arch.main(["measure", "--layers", str(map_path), "--out", str(out)]) == 3
    assert "gnd.cli" in capsys.readouterr().err


@pytest.mark.parametrize(
    "raw",
    [
        "[]",
        '{"schema_version": 1, "schema_version": 1}',
        '{"schema_version": NaN}',
        (
            '{"schema_version": 1, "excluded": [], "layers": 7, "lanes": [], "modules": {}, '
            '"declared_clean": [], "allow_list": [], "helper_patterns": {}}'
        ),
        (
            '{"schema_version": 1, "excluded": [], "layers": [{"name": "x", "rank": 0}], '
            '"lanes": [], "modules": {}, "declared_clean": [], "allow_list": [], '
            '"helper_patterns": {"bad": "("}}'
        ),
        " " * (2 * 1024 * 1024),
    ],
)
def test_t7g_hostile_maps_exit_3_without_traceback(tmp_path, raw):
    root, map_path = make_tree(tmp_path, BASIC, layer_map=raw)
    assert run_measure(root, map_path, tmp_path / "out.json") == 3


# ---------------------------------------------------------------- T8, T9 test inventory

TEST_SOURCE = """\
import os
import sys
import inspect
from pathlib import Path
import gnd.a as m
from gnd.b import C
from gnd.a import _private_helper


def test_x(monkeypatch):
    monkeypatch.setattr("gnd.a.f", 1)
    monkeypatch.setattr(m, "_g", 1)
    monkeypatch.setattr(C, "meth", 1)
    monkeypatch.setattr(thing, "attr", 1)
    monkeypatch.setattr(os, "sep", "/")
    inspect.getsource(m)
    Path("src/gnd/cli.py").read_text()
    assert "gnd.cli" not in sys.modules
    code = "import sys; print('gnd.cli' in sys.modules)"
"""


def test_t8_t9_test_inventory(tmp_path):
    files = {
        "src/gnd/__init__.py": "",
        "src/gnd/a.py": "def f():\n    return 1\n_private_helper = 1\n",
        "src/gnd/b.py": "class C:\n    def meth(self):\n        return 1\n",
        "tests/test_p.py": TEST_SOURCE,
    }
    data = measured(tmp_path, files)
    at = lambda snippet: line_of(TEST_SOURCE, snippet)
    patches = {(p["line"], p["target"], p["resolved"]) for p in data["tests"]["patches"]}
    assert patches == {
        (at('"gnd.a.f"'), "gnd.a.f", True),  # T8a
        (at('(m, "_g"'), "gnd.a._g", True),  # T8b
        (at('(C, "meth"'), "gnd.b.C.meth", True),  # T8c
        (at('(thing, "attr"'), "thing.attr", False),  # T8d
    }
    scans = {(s["line"], s["kind"]) for s in data["tests"]["source_scans"]}
    assert scans == {
        (at("getsource"), "getsource"),
        (at("cli.py"), "cli_path"),
        (at("not in sys.modules"), "sys_modules"),
        (at("code ="), "sys_modules"),
    }
    assert data["tests"]["private_imports"] == [
        {
            "file": "tests/test_p.py",
            "line": at("_private_helper"),
            "target": "gnd.a._private_helper",
        }
    ]


# ---------------------------------------------------------------- T10, T11, T13 exits


def test_t10a_existing_out_exits_11_unchanged(tmp_path):
    root, map_path = make_tree(tmp_path, BASIC)
    out = tmp_path / "out.json"
    out.write_text("keep")
    assert run_measure(root, map_path, out) == 11
    assert out.read_text() == "keep"


def test_t10b_existing_out_wins_over_invalid_map(tmp_path):
    root, map_path = make_tree(tmp_path, BASIC, layer_map="[]")
    out = tmp_path / "out.json"
    out.write_text("keep")
    assert run_measure(root, map_path, out) == 11


def test_t11_syntax_error_exits_3_naming_file(tmp_path, capsys):
    files = {"src/gnd/__init__.py": "", "src/gnd/broken.py": "def oops(:\n"}
    root, map_path = make_tree(tmp_path, files)
    assert run_measure(root, map_path, tmp_path / "out.json") == 3
    assert "src/gnd/broken.py" in capsys.readouterr().err


def test_t13_pathological_nesting_exits_3(tmp_path):
    files = {"src/gnd/__init__.py": "", "src/gnd/deep.py": "x = " + "-" * 200000 + "1\n"}
    root, map_path = make_tree(tmp_path, files)
    assert run_measure(root, map_path, tmp_path / "out.json") == 3


# ---------------------------------------------------------------- T14 compare


def git(repo, *args):
    subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
        check=True,
        capture_output=True,
    )


def test_t14a_compare_counts_moved_lines(tmp_path):
    repo = tmp_path / "g"
    (repo / "src/gnd").mkdir(parents=True)
    git(repo, "init", "-q")
    moved = "def helper(value):\n    total = value * 3\n    return total - 1\n"
    (repo / "src/gnd/a.py").write_text("keep = 1\nedited = 1\n\n" + moved)
    (repo / "src/gnd/b.py").write_text("other = 2\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base")
    (repo / "src/gnd/a.py").write_text("keep = 1\nedited = 2\n")
    (repo / "src/gnd/b.py").write_text("other = 2\n\n" + moved)
    git(repo, "commit", "-q", "-am", "head")
    out = tmp_path / "cmp.json"
    assert arch.main(["compare", "HEAD~1", "HEAD", "--root", str(repo), "--out", str(out)]) == 0
    rows = {r["path"]: r for r in json.loads(out.read_text())["files"]}
    assert rows["src/gnd/b.py"]["moved_in"] == 3
    assert rows["src/gnd/a.py"]["moved_out"] == 3
    assert rows["src/gnd/a.py"]["moved_in"] == 0
    assert rows["src/gnd/a.py"]["added"] == 1  # the edited line is not a move


def test_t14b_compare_unknown_revision_exits_3(tmp_path):
    repo = tmp_path / "g"
    repo.mkdir()
    git(repo, "init", "-q")
    out = tmp_path / "cmp.json"
    assert arch.main(["compare", "nope", "HEAD", "--root", str(repo), "--out", str(out)]) == 3
    assert not out.exists()


def test_cli_entry_point_runs_as_script(tmp_path):
    out = tmp_path / "m.json"
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "gnd_arch.py"), "measure", "--out", str(out)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert shutil.which("git")


# ---------------------------------------------------------------- review regressions (RF0 codex review)


def test_r01_more_edge_and_patch_forms(tmp_path):
    source = (
        "import typing\n"
        "if typing.TYPE_CHECKING:\n"
        "    import gnd.b\n"
        "f = lambda: __import__('gnd.c')\n"
    )
    files = {
        "src/gnd/__init__.py": "",
        "src/gnd/a.py": source,
        "src/gnd/b.py": "",
        "src/gnd/c.py": "",
    }
    data = measured(tmp_path, files)
    assert edge_set(data, "gnd.a") == {("gnd.b", "type_only", 3), ("gnd.c", "dynamic", 4)}


def test_r01_patch_object_mock_and_delattr(tmp_path):
    test_source = (
        "from unittest import mock\n"
        "from unittest.mock import patch\n"
        "import gnd.a as m\n"
        "def test_x(monkeypatch):\n"
        "    monkeypatch.delattr(m, '_g')\n"
        "    monkeypatch.delattr('gnd.a.f')\n"
        "    patch.object(m, 'f')\n"
        "    mock.patch('gnd.a._h')\n"
        "    monkeypatch.setattr(target='gnd.a._k', value=1)\n"
    )
    files = {"src/gnd/__init__.py": "", "src/gnd/a.py": "", "tests/test_q.py": test_source}
    data = measured(tmp_path, files)
    rows = {(p["line"], p["api"], p["target"], p["resolved"]) for p in data["tests"]["patches"]}
    assert rows == {
        (5, "delattr", "gnd.a._g", True),
        (6, "delattr", "gnd.a.f", True),
        (7, "patch.object", "gnd.a.f", True),
        (8, "patch", "gnd.a._h", True),
        (9, "setattr", "gnd.a._k", True),
    }


def test_r01_compare_counts_a_renamed_file_as_moved(tmp_path):
    repo = tmp_path / "g"
    (repo / "src/gnd").mkdir(parents=True)
    git(repo, "init", "-q")
    (repo / "src/gnd/old.py").write_text("alpha = 1\nbeta = 2\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base")
    git(repo, "mv", "src/gnd/old.py", "src/gnd/new.py")
    git(repo, "commit", "-q", "-m", "rename")
    out = tmp_path / "cmp.json"
    assert arch.main(["compare", "HEAD~1", "HEAD", "--root", str(repo), "--out", str(out)]) == 0
    totals = json.loads(out.read_text())["totals"]
    assert totals["moved_in"] == 2 and totals["moved_out"] == 2


@pytest.mark.parametrize(
    "entry",
    [{"layer": []}, {"layer": "lanes", "lane": []}, {"layer": "model", "lane": 3}, []],
)
def test_r02_wrongly_typed_map_values_exit_3(tmp_path, entry):
    layer_map = make_map({"gnd": "infrastructure", "gnd.a": "infrastructure"})
    layer_map["modules"]["gnd.a"] = entry
    root, map_path = make_tree(tmp_path, BASIC, layer_map=layer_map)
    assert run_measure(root, map_path, tmp_path / "out.json") == 3


def test_r03_missing_out_parent_exits_3_without_measuring(tmp_path, capsys):
    root, map_path = make_tree(tmp_path, BASIC)
    assert run_measure(root, map_path, tmp_path / "absent" / "out.json") == 3
    assert "--out" in capsys.readouterr().err


def test_r04_oversized_or_unreadable_source_exits_3(tmp_path, monkeypatch):
    files = {
        "src/gnd/__init__.py": "",
        "src/gnd/big.py": "x = 1\n" * (arch.SOURCE_READ_CAP // 6 + 1),
    }
    root, map_path = make_tree(tmp_path, files)
    assert run_measure(root, map_path, tmp_path / "out.json") == 3
    root2, map2 = make_tree(tmp_path / "second", BASIC)
    (root2 / "src/gnd/a.py").chmod(0)
    try:
        assert run_measure(root2, map2, tmp_path / "out2.json") == 3
    finally:
        (root2 / "src/gnd/a.py").chmod(0o644)


def test_r05_r06_type_checking_matches_precisely_and_guards_dynamic(tmp_path):
    source = (
        "import foo\n"
        "from typing import TYPE_CHECKING\n"
        "import importlib\n"
        "if foo.TYPE_CHECKING:\n"
        "    import gnd.b\n"
        "if TYPE_CHECKING:\n"
        "    importlib.import_module('gnd.c')\n"
    )
    files = {
        "src/gnd/__init__.py": "",
        "src/gnd/a.py": source,
        "src/gnd/b.py": "",
        "src/gnd/c.py": "import gnd.a\n",
    }
    data = measured(tmp_path, files)
    assert edge_set(data, "gnd.a") == {("gnd.b", "module", 5), ("gnd.c", "type_only", 7)}
    assert data["sccs"]["runtime"] == []


def test_r07_private_submodule_import_is_recorded(tmp_path):
    files = {
        "src/gnd/__init__.py": "",
        "src/gnd/pkg/__init__.py": "",
        "src/gnd/pkg/_hidden.py": "",
        "src/gnd/user.py": "from gnd.pkg import _hidden\n",
    }
    data = measured(tmp_path, files)
    assert data["private_imports"] == [
        {"from": "gnd.user", "to": "gnd.pkg", "name": "_hidden", "line": 1, "kind": "from_import"}
    ]


def test_r08_alias_bindings_are_scoped(tmp_path):
    source = (
        "import gnd.a as m\n"
        "def f():\n"
        "    import gnd.b as m\n"
        "    return m._inside\n"
        "value = m._outside\n"
    )
    files = {
        "src/gnd/__init__.py": "",
        "src/gnd/a.py": "_outside = 1\n",
        "src/gnd/b.py": "_inside = 1\n",
        "src/gnd/user.py": source,
    }
    data = measured(tmp_path, files)
    found = {(p["to"], p["name"]) for p in data["private_imports"]}
    assert found == {("gnd.b", "_inside"), ("gnd.a", "_outside")}


def test_r10_compare_reads_triple_dash_lines_inside_hunks(tmp_path):
    repo = tmp_path / "g"
    (repo / "src/gnd").mkdir(parents=True)
    git(repo, "init", "-q")
    (repo / "src/gnd/a.py").write_text("x = 1\n-- important\nother = 2\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base")
    (repo / "src/gnd/a.py").write_text("x = 1\n")
    git(repo, "commit", "-q", "-am", "head")
    out = tmp_path / "cmp.json"
    assert arch.main(["compare", "HEAD~1", "HEAD", "--root", str(repo), "--out", str(out)]) == 0
    rows = json.loads(out.read_text())["files"]
    assert rows == [
        {"path": "src/gnd/a.py", "added": 0, "removed": 2, "moved_in": 0, "moved_out": 0}
    ]
