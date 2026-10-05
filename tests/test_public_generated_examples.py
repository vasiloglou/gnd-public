"""Owned public example successors over fresh real codegen and conformance."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from gnd.architecture import load_architecture_contract
from gnd.archsmoke import build_smoke_module, run_row, smoke_rows
from gnd.checker import band, check
from gnd.model import load_model
from gnd.population import load_population

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/public-generated-examples"


def run(argv, root):
    env = os.environ.copy()
    for key in ("PYTHONPATH", "PYTHONHOME", "PYTEST_ADDOPTS", "PYTEST_PLUGINS"):
        env.pop(key, None)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    return subprocess.run(argv, cwd=root, env=env, capture_output=True, text=True,
                          check=False, timeout=300)


def create_project(case, tmp_path):
    source = FIXTURES / case
    root = tmp_path / case
    result = run([sys.executable, "-m", "gnd", "codegen", str(source / "model.orm.yaml"),
                  "--out", str(root)], ROOT)
    assert result.returncode == 0, result.stdout + result.stderr
    for name in ("model.orm.yaml", "seed.population.json", "architecture.contract.yaml"):
        shutil.copy2(source / name, root / name)
    package = root / ("bookrec" if case == "bookrec" else "cli")
    package.mkdir()
    (package / "__init__.py").write_text("")
    shutil.copy2(source / "extension.py", package / ("cli.py" if case == "bookrec" else "expense_cli.py"))
    conformance = run([sys.executable, "-m", "gnd", "conformance", str(root / "model.orm.yaml"),
                      str(root)], ROOT)
    assert conformance.returncode == 0, conformance.stdout + conformance.stderr
    return case, root


@pytest.fixture(params=["bookrec", "expense"])
def project(request, tmp_path):
    return create_project(request.param, tmp_path)


def test_generated_example_runs_both_declared_smoke_rows_and_floor(project):
    case, root = project
    modules = list(root.glob("test_architecture_smoke_*.py"))
    assert len(modules) == 1
    rows = smoke_rows(root)
    assert [(r.id, r.expect_exit) for r in rows] == (
        [("known-user-recommend", 0), ("unknown-user-refused", 3)] if case == "bookrec"
        else [("report-smoke", 0), ("unknown-expense-refused", 1)]
    )
    _, declares_rows, _ = build_smoke_module(str(modules[0]))
    declares_rows()
    result = run([sys.executable, "-m", "pytest", "-q", modules[0].name], root)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "3 passed" in result.stdout
    assert "skipped" not in result.stdout
    contract = load_architecture_contract(root)
    assert len(contract.smoke) == 2


def test_generated_examples_have_concrete_acceptance_and_nondestructive_refusal(project, tmp_path):
    case, root = project
    rows = smoke_rows(root)
    before = (root / "seed.population.json").read_bytes()
    accepted = run_row(rows[0], project_root=root, tmp=tmp_path / "accept")
    assert accepted.passed and accepted.actual_exit == 0, accepted.message
    if case == "bookrec":
        output = tmp_path / "accept/recommendations.json"
        assert json.loads(output.read_text())["facts"]["recommendation"] == [
            {"user": "reader-1", "book": "book-2"}
        ]
        model = load_model(root / "model.orm.yaml")
        assert band(check(model, load_population(output, model=model))) == 0
    else:
        assert json.loads(accepted.stdout) == {"submitted": 1, "total": 25}
    refused = run_row(rows[1], project_root=root, tmp=tmp_path / "refuse")
    assert refused.passed and refused.actual_exit == (3 if case == "bookrec" else 1)
    assert "unknown user" in refused.stderr if case == "bookrec" else "no submission fact" in refused.stderr
    assert not (tmp_path / "refuse/recommendations.json").exists()
    assert (root / "seed.population.json").read_bytes() == before


def test_owned_extension_accepting_and_refusing_branches(project):
    case, root = project
    if case == "bookrec":
        argv = [sys.executable, "-m", "bookrec.cli", "recommend", "--model", "model.orm.yaml",
                "--input", "seed.population.json", "--output", "unused.json", "--user", "reader-1",
                "--limit", "0"]
        result = run(argv, root)
        assert result.returncode == 2 and "limit must be positive" in result.stderr
        assert not (root / "unused.json").exists()
        model_path = root / "model.orm.yaml"
        model_document = json.loads(model_path.read_text())
        model_document["fact_types"][2]["constraints"] = [{
            "type": "uniqueness", "roles": ["user"], "source": "explicit",
            "status": "confirmed", "modality": "alethic",
            "provenance": {"user_quote": "Only one recommendation per user."}
        }]
        model_path.write_text(json.dumps(model_document))
        population_path = root / "seed.population.json"
        document = json.loads(population_path.read_text())
        document["facts"]["book_has_title"].append({"book": "book-3", "title": "Third book"})
        population_path.write_text(json.dumps(document))
        argv[-1] = "2"
        blocked = run(argv, root)
        assert blocked.returncode == 1, blocked.stdout + blocked.stderr
        assert not (root / "unused.json").exists()
        assert not (root / "unused.candidate.json").exists()
    else:
        argv = [sys.executable, "-m", "cli.expense_cli", "approve", "--population",
                "seed.population.json", "--expense", "1", "--chain", "CH-1"]
        accepted = run(argv, root)
        assert accepted.returncode == 0, accepted.stdout + accepted.stderr
        document = json.loads((root / "seed.population.json").read_text())
        assert document["facts"]["expense_is_approved"] == [{"expense": 1}]
        assert document["facts"]["expense_approved_by_chain"] == [{"expense": 1, "chain": "CH-1"}]
        before = (root / "seed.population.json").read_bytes()
        refused = run(argv, root)
        assert refused.returncode == 1 and "already approved" in refused.stderr
        assert (root / "seed.population.json").read_bytes() == before
        model = load_model(root / "model.orm.yaml")
        assert band(check(model, load_population(root / "seed.population.json", model=model))) == 0


def test_both_generated_smoke_modules_collect_and_execute_under_one_root(tmp_path):
    modules = []
    for case in ("bookrec", "expense"):
        _, root = create_project(case, tmp_path)
        emitted, = root.glob("test_architecture_smoke_*.py")
        modules.append(str(emitted))
    assert Path(modules[0]).name != Path(modules[1]).name
    result = run([sys.executable, "-m", "pytest", "-q", *modules], tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "6 passed" in result.stdout
    assert "skipped" not in result.stdout
    assert "import file mismatch" not in result.stdout + result.stderr
