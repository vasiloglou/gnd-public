"""Current registry construction, CLI and partial-precondition guards."""
import atexit
import importlib
import json
import shutil
import tempfile
from pathlib import Path

import pytest
from test_public_slice_runtime import CASES
from test_public_slice_runtime import CORPUS as SLICE_CORPUS
from test_public_transition_walks import MODEL

import gnd
from gnd.commands import checking as patched_service


def _generic_registry_root():
    temporary = tempfile.TemporaryDirectory(prefix="gnd-public-registry-")
    root = Path(temporary.name)
    package_dir = Path(gnd.__file__).resolve().parent
    for name in ("correspondence.py",):
        target = root / "src/gnd" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(package_dir / name, target)
    shutil.copytree(package_dir / "checker", root / "src/gnd/checker", ignore=shutil.ignore_patterns("__pycache__"))
    corpus = root / "proof/v6/phase1/corpus"
    corpus.mkdir(parents=True)
    (corpus / "cases.json").write_text(json.dumps(CASES), encoding="utf-8")
    fixture = corpus / "fixtures/c01"
    fixture.mkdir(parents=True)
    for name in ("model.orm.yaml", "population.yaml"):
        shutil.copyfile(SLICE_CORPUS / "fixtures/c01" / name, fixture / name)
    model = root / "tests/fixtures/transition/expense/v2_expense.orm.yaml"
    model.parent.mkdir(parents=True)
    shutil.copyfile(MODEL, model)
    alias = root / "tests/test_public_registry_runtime.py"
    alias.touch()
    return temporary, str(alias)

_TEMPORARY, _GENERIC_FILE = _generic_registry_root()
atexit.register(_TEMPORARY.cleanup)


@pytest.fixture(autouse=True)
def _generic_module_coordinates(monkeypatch):
    monkeypatch.setitem(globals(), "__file__", _GENERIC_FILE)
@pytest.fixture
def registry():
    return importlib.import_module("gnd.semantic_registry")


def test_unknown_branch_maps_to_cli_internal_error(registry, monkeypatch, capsys):
    import json
    from pathlib import Path

    from gnd import cli

    def broken(*args, **kwargs):
        registry.record_branch("snapshot:invented:n-a:clean")

    monkeypatch.setattr(patched_service, "check", broken)
    root = Path(__file__).resolve().parents[1]
    corpus = root / "proof/v6/phase1/corpus"
    case = json.loads((corpus / "cases.json").read_text())["cases"][0]
    result = cli._cmd_check(str(corpus / case["model"]), str(corpus / case["population"]), "json")
    assert result == 70
    payload = json.loads(capsys.readouterr().out)
    assert payload["exit_code"] == 70
    assert payload["acceptance_ready"] is False


def test_every_correspondence_finding_site_requires_an_explicit_scope():
    import ast
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    tree = ast.parse((root / "src/gnd/correspondence.py").read_text())
    sites = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "CorrespondedFinding"
    ]
    # Phase 3 deliberately replaces the checker's distributed result sites
    # with one correspondence construction boundary.
    assert len(sites) == 1
    assert all(any(key.arg == "scope_id" for key in site.keywords) for site in sites)
    paths = set((root / "src/gnd/checker").rglob("*.py"))
    assert {p.name for p in paths} == {"__init__.py", "_core.py", "_reports.py"}
    checker = ast.Module(body=[node for path in paths for node in ast.parse(path.read_text()).body], type_ignores=[])
    assert not any(
        isinstance(node, ast.FunctionDef) and node.name == "result"
        for node in ast.walk(checker)
    )


def test_partial_precondition_does_not_record_a_clean_obligation(registry):
    from pathlib import Path

    from gnd.model import load_model
    from gnd.transition import _evaluate_step

    root = Path(__file__).resolve().parents[1]
    model = load_model(root / "tests/fixtures/transition/expense/v2_expense.orm.yaml")
    operation = {
        "id": "test",
        "effects": [],
        "preconditions": [
            {
                "id": "both-statuses",
                "modality": "alethic",
                "require": [
                    {
                        "fact_type": "expense_has_status",
                        "bind": {"expense": "$expense", "status": "draft"},
                    },
                    {
                        "fact_type": "expense_has_status",
                        "bind": {"expense": "$expense", "status": "approved"},
                    },
                ],
            }
        ],
    }
    with registry.capture_branches() as reached:
        result, _ = _evaluate_step(
            1,
            {"bindings": {"expense": 41}},
            operation,
            model,
            {"expense_has_status": [{"expense": 41, "status": "draft"}]},
            None,
        )
    assert [row.verdict for row in result.verdicts] == ["fail"]
    assert "transition:precondition:n-a:clean" not in reached

