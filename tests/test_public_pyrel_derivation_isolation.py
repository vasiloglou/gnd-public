"""Default-lane isolation controls; no real foreign process is invoked."""

from __future__ import annotations

import ast
import json
import runpy
import shlex
import tomllib

import pytest
import test_public_pyrel_oracle_isolation as isolation
from _pytest.mark.expression import Expression
from support import public_pyrel_derivation_isolation as live
from support.public_pyrel_derivation_isolation import ORACLE, ROOT, require_driver


def _assert_independent(source):
    tree = ast.parse(source)
    roots = isolation._imported_top_level_packages(tree)
    assert not roots.intersection(
        {"gnd", "test_derivation_parity", "pyrel_derivation_corpus_support"}
    )
    assert not any(isinstance(n, ast.ImportFrom) and n.level for n in ast.walk(tree))
    literals = {
        n.value.replace("\\", "/")
        for n in ast.walk(tree)
        if isinstance(n, ast.Constant) and isinstance(n.value, str)
    }
    assert not any(
        value.startswith(("gnd.", "gnd/"))
        or "/answers/" in value
        or "oracle-receipt.json" in value
        or "test_derivation_parity" in value
        for value in literals
    )


def _metadata(source):
    lines = source.splitlines()
    start = lines.index("# /// script")
    end = lines.index("# ///", start + 1)
    return tomllib.loads("\n".join(line.removeprefix("# ") for line in lines[start + 1 : end]))


def test_pyrel_derivation_pin_and_import_independence():
    require_driver()
    source = ORACLE.read_text()
    assert _metadata(source)["dependencies"] == ["relationalai==1.30.1", "ruamel.yaml==0.19.1"]
    _assert_independent(source)
    for injected in [
        "import gnd.checker\n",
        "from gnd import model\n",
        "from . import local\n",
        "import test_derivation_parity\n",
        'import runpy\n_cheat = runpy.run_module("gnd.checker")\n',
        '_cheat = Path("tests/fixtures/v52-pyrel-derivation/answers/cases.json").read_text()\n',
    ]:
        with pytest.raises(AssertionError):
            _assert_independent(source + "\n" + injected)
    changed = source.replace("relationalai==1.30.1", "relationalai>=1.30.1")
    assert _metadata(changed)["dependencies"] != _metadata(source)["dependencies"]
    assert "relationalai" not in (ROOT / "uv.lock").read_text()
    assert not any(
        "relationalai" in p
        for p in tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["dependencies"]
    )


def test_order_and_binary_float_controls_distinguish_plausible_mutants():
    runtime = runpy.run_path(str(ORACLE))
    facts = {
        "upper": {
            "derivation_rule": {"body": [{"fact_type": "lower"}], "negate": []}
        },
        "lower": {"derivation_rule": {"body": [], "negate": []}},
    }
    observed_order = runtime["_ordered_heads"](facts)
    assert observed_order == ["lower", "upper"]
    assert observed_order != list(facts), "declaration-order mutation must be distinguishable"

    observed_token = runtime["_identity"](0.1, "Number")
    exact_token = '["number",[3602879701896397,36028797018963968]]'
    decimal_spelling_mutant = '["number",[1,10]]'
    assert observed_token == exact_token
    assert observed_token != decimal_spelling_mutant


def test_pyrel_live_marker_is_excluded_by_actual_default_expression():
    require_driver()
    marker = live.pytestmark
    assert marker.name == "pyrel_oracle"
    args = shlex.split(
        tomllib.loads((ROOT / "pyproject.toml").read_text())["tool"]["pytest"]["ini_options"][
            "addopts"
        ]
    )
    expression = Expression.compile(args[args.index("-m") + 1])
    assert not expression.evaluate(lambda name, **_: name == marker.name)
    assert expression.evaluate(lambda name, **_: False)
    assert Expression.compile("pyrel_oracle").evaluate(lambda name, **_: name == marker.name)


def test_pyrel_absence_skips_but_selected_failure_is_not_skipped(monkeypatch):
    driver = require_driver()
    monkeypatch.setattr(live.shutil, "which", lambda _: None)
    with pytest.raises(pytest.skip.Exception, match="uv executable absent"):
        live._available_driver()
    monkeypatch.setattr(live.shutil, "which", lambda _: "/mock/uv")
    assert live._available_driver() is driver

    def failure(*_args):
        raise RuntimeError("fixture runtime failure")

    monkeypatch.setattr(live, "require_driver", lambda: failure)
    with pytest.raises(RuntimeError, match="fixture runtime failure"):
        live._available_driver()(None, None)


def test_pyrel_default_receipt_checks_cannot_launch_foreign_process(monkeypatch):
    require_driver()
    import test_derivation_parity as parity

    receipt = json.loads(parity.RECEIPT.read_text())
    assert all("pyrel" in row["results"] for row in receipt["cases"])

    def forbidden(*_args, **_kwargs):
        raise AssertionError("default receipt check launched a foreign process")

    monkeypatch.setattr(parity.subprocess, "run", forbidden)
    monkeypatch.setattr(parity, "_pyrel_extensions", forbidden)
    parity.test_oracle_receipt_is_canonical_and_current()
