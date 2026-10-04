"""Transition report composition controls over approved public walk inputs."""
from __future__ import annotations

import atexit
import io
import json
import shutil
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

import pytest
from test_public_transition_walks import CORPUS

from gnd.semantic_registry import REGISTRY, capture_branches

_TEMPORARY = tempfile.TemporaryDirectory(prefix="gnd-public-transition-consumer-")
atexit.register(_TEMPORARY.cleanup)
_ROOT = Path(_TEMPORARY.name)
_BASE = _ROOT / "tests/fixtures/transition/expense"
_BASE.mkdir(parents=True)
shutil.copyfile(CORPUS / "v2_expense.orm.yaml", _BASE / "v2_expense.orm.yaml")
for _case in ("clean-walk", "broken-post", "vacuous-pre", "tag-unchecked"):
    shutil.copytree(CORPUS / "walks" / _case, _BASE / "walks" / _case)
_ALIAS = _ROOT / "tests/test_public_consumer_transition.py"
_ALIAS.touch()

@pytest.fixture(autouse=True)
def _generic_module_coordinates(monkeypatch):
    monkeypatch.setitem(globals(), "__file__", str(_ALIAS))

def observe_transition_compositions():
    from gnd.cli import main

    root = Path(__file__).parent / "fixtures/transition/expense"
    required = {
        row.scope_id
        for row in REGISTRY
        if row.surface == "composition" and row.variant == "transition"
    }
    with capture_branches() as reached:
        for name, expected in (
            ("clean-walk", 0),
            ("broken-post", 1),
            ("vacuous-pre", 2),
            ("tag-unchecked", 4),
        ):
            directory = root / "walks" / name
            assert json.loads((directory / "expected.json").read_text())["exit"] == expected
            output = io.StringIO()
            with redirect_stdout(output):
                observed = main(
                    [
                        "check",
                        str(root / "v2_expense.orm.yaml"),
                        "--pre",
                        str(directory / "pre.pop.yaml"),
                        "--steps",
                        str(directory / "steps.json"),
                        "--post",
                        str(directory / "post.pop.yaml"),
                        "--format",
                        "json",
                    ]
                )
            assert observed == expected, (name, output.getvalue())
            assert json.loads(output.getvalue())["exit_code"] == expected
            assert '"scope_id"' not in output.getvalue()
    assert required <= reached, sorted(required - reached)

def test_transition_band_cases_reach_all_four_composition_branches():
    observe_transition_compositions()
