"""Behavioral controls for the installed synthetic expense application."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from importlib.resources import files

import pytest

from gnd.api import check


@pytest.fixture
def resources(tmp_path):
    root = tmp_path / "expense-demo"
    root.mkdir()
    for resource in files("gnd").joinpath("examples", "expense").iterdir():
        if resource.is_file():
            (root / resource.name).write_bytes(resource.read_bytes())
    return root


def run(args, cwd):
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    return subprocess.run(
        [sys.executable, *args], cwd=cwd, env=env,
        capture_output=True, text=True, timeout=30, check=False,
    )


@pytest.fixture
def project(resources, tmp_path):
    root = tmp_path / "expense-project"
    generated = run(["-m", "gnd", "codegen", str(resources / "model.orm.json"),
                     "--out", str(root)], tmp_path)
    assert generated.returncode == 0, generated.stdout + generated.stderr
    (root / "cli").mkdir()
    (root / "cli/__init__.py").write_text("")
    for source, target in [
        ("model.orm.json", "model.orm.json"),
        ("seed.population.json", "seed.population.json"),
        ("architecture.contract.yaml", "architecture.contract.yaml"),
        ("extension.py", "cli/expense_cli.py"),
        ("reporting.py", "cli/reporting.py"),
    ]:
        shutil.copy2(resources / source, root / target)
    return root


def approve(root, expense, chain, population="seed.population.json", output="result.json"):
    return run(["-m", "cli.expense_cli", "approve", "--model", "model.orm.json",
                "--population", population, "--expense", str(expense),
                "--chain", chain, "--output", output], root)


def test_report_and_approval_produce_concrete_results(project, resources):
    result = run(["-m", "cli.expense_cli", "report", "--model", "model.orm.json",
                  "--population", "seed.population.json"], project)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"approved": 1, "submitted": 3, "total_eur": 2260}
    original = (project / "seed.population.json").read_bytes()
    accepted = approve(project, 101, "team-lead")
    assert accepted.returncode == 0, accepted.stderr
    assert json.loads((project / "result.json").read_text()) == json.loads(
        (resources / "approved.population.json").read_text()
    )
    assert (project / "seed.population.json").read_bytes() == original
    assert check(project / "model.orm.json", project / "result.json")["exit_code"] == 0
    conformity = run(["-m", "gnd", "conformance", str(resources / "model.orm.json"),
                      str(project)], project.parent)
    assert conformity.returncode == 0, conformity.stdout + conformity.stderr


@pytest.mark.parametrize("expense,chain,message", [
    (999, "finance", "no submission fact"),
    (103, "finance", "already approved"),
    (102, "team-lead", "GND withheld acceptance"),
    (101, "fast-track", "GND withheld acceptance"),
])
def test_refusals_preserve_input_and_existing_output(project, expense, chain, message):
    before = (project / "seed.population.json").read_bytes()
    output = project / "result.json"
    output.write_text("existing result must survive a refused candidate")
    result = approve(project, expense, chain)
    assert result.returncode == 1, result.stdout + result.stderr
    assert message in result.stderr
    assert (project / "seed.population.json").read_bytes() == before
    assert output.read_text() == "existing result must survive a refused candidate"
    assert not list(project.glob("tmp*.json"))


def test_output_cannot_replace_the_input_checkpoint(project):
    before = (project / "seed.population.json").read_bytes()
    result = approve(project, 101, "team-lead", output="seed.population.json")
    assert result.returncode == 2
    assert "separate file" in result.stderr
    assert (project / "seed.population.json").read_bytes() == before


def test_report_does_not_publish_a_total_for_invalid_input(project, resources):
    shutil.copy2(resources / "invalid-meal.population.json", project / "invalid.json")
    result = run(["-m", "cli.expense_cli", "report", "--model", "model.orm.json",
                  "--population", "invalid.json"], project)
    assert result.returncode == 1
    assert result.stdout == ""
    assert json.loads(result.stderr)["exit_code"] == 1


@pytest.mark.parametrize("category,limit", [
    ("meals", 75), ("training", 1500), ("travel", 2000), ("equipment", 3000),
])
def test_category_limits_accept_the_boundary_and_refuse_one_more(resources, category, limit):
    population = json.loads((resources / "seed.population.json").read_text())
    population["facts"]["expense_in_category"][0]["category"] = category
    population["facts"]["expense_has_amount"][0]["amount"] = limit
    target = resources / "boundary.json"
    target.write_text(json.dumps(population))
    assert check(resources / "model.orm.json", target)["exit_code"] == 0
    population["facts"]["expense_has_amount"][0]["amount"] = limit + 1
    target.write_text(json.dumps(population))
    report = check(resources / "model.orm.json", target, unredacted=True)
    assert report["exit_code"] == 1
    failures = [row for row in report["verdicts"] if row["verdict"] == "fail"]
    assert len(failures) == 1
    assert failures[0]["offending_facts"] == [{"$e": 101, "$a": limit + 1}]


def test_currency_distinguishes_missing_coverage_missing_values_and_migration(resources):
    model = resources / "currency.orm.json"
    assert check(model, resources / "seed.population.json")["exit_code"] == 2
    partial = check(model, resources / "currency-missing.population.json", unredacted=True)
    assert partial["exit_code"] == 1
    failures = [row for row in partial["verdicts"] if row["verdict"] == "fail"]
    assert len(failures) == 1 and failures[0]["constraint_type"] == "mandatory"
    assert "expense_has_currency" in failures[0]["constraint_ref"]
    assert check(model, resources / "currency.population.json")["exit_code"] == 0
    unsupported = json.loads((resources / "currency.population.json").read_text())
    unsupported["facts"]["expense_has_currency"][0]["currency"] = "USD"
    target = resources / "unsupported.json"
    target.write_text(json.dumps(unsupported))
    report = check(model, target)
    assert report["exit_code"] == 1
    assert any(row["constraint_type"] == "value" and row["verdict"] == "fail"
               for row in report["verdicts"])


def test_evolved_report_uses_currency_and_preserves_check_gate(project, resources):
    for source, target in [
        ("currency.orm.json", "model.orm.json"),
        ("currency.population.json", "seed.population.json"),
        ("currency_reporting.py", "cli/reporting.py"),
    ]:
        shutil.copy2(resources / source, project / target)
    result = run(["-m", "cli.expense_cli", "report", "--model", "model.orm.json",
                  "--population", "seed.population.json"], project)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {
        "approved": 1, "submitted": 3, "totals_by_currency": {"EUR": 2260},
    }
    shutil.copy2(resources / "currency-missing.population.json", project / "incomplete.json")
    result = run(["-m", "cli.expense_cli", "report", "--model", "model.orm.json",
                  "--population", "incomplete.json"], project)
    assert result.returncode == 1
    assert result.stdout == ""
    accepted = approve(project, 101, "team-lead")
    assert accepted.returncode == 0, accepted.stderr
    assert check(project / "model.orm.json", project / "result.json")["exit_code"] == 0
