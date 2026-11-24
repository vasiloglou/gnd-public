"""Profile boundaries for the guarded clause syntax."""
import json
import os
import subprocess
from pathlib import Path

import pytest
from ruamel.yaml import YAML

BASE = Path(__file__).resolve().parent / "fixtures/models/guarded_minimal.orm.yaml"


@pytest.fixture(scope="module")
def native_python():
    native = os.environ.get("GND_PYREL_PYTHON")
    if not native:
        pytest.skip("set GND_PYREL_PYTHON to the pinned local runtime")
    versions = subprocess.check_output(
        [native, "-I", "-c", "from importlib.metadata import version; print(version('relationalai'), version('duckdb'))"],
        text=True, timeout=10,
    )
    assert versions.strip() == "1.30.1 1.5.5"
    return native


def _model(tmp_path, shape):
    model = YAML(typ="safe").load(BASE)
    rule = model["constraints"][0]
    model["constraints"] = [rule]
    if shape == "membership":
        rule["consequent"]["comparison"].update(operator="in", right=[1500, 1600])
    elif shape == "filters":
        rule["negate"] = [{
            "fact_type": "expense_has_status",
            "bind": {"expense": "$e", "status": "exempt"},
        }]
        rule["where"] = [{"operator": ">=", "left": "$a", "right": 1000}]
    elif shape == "disjunction":
        rule["consequent"] = {"any_of": [
            rule["consequent"], {"comparison": {"operator": ">=", "left": "$a", "right": 2600}},
        ]}
    path = tmp_path / "model.orm.json"
    path.write_text(json.dumps(model))
    return path


@pytest.mark.parametrize("shape", ["membership", "filters"])
def test_readable_rules_translate_supported_guarded_clauses(tmp_path, shape):
    from gnd.export.pyrel_rules import render

    model = _model(tmp_path, shape)
    for target in ("duckdb", "lqp"):
        program = render(model, target)
        compile(program, "export.py", "exec")
        assert "policy_limit_travel" in program


@pytest.mark.parametrize(("shape", "reason"), [
    ("membership", "membership-unsupported"),
    ("filters", "guarded-antecedent-filters-unsupported"),
    ("disjunction", "guarded-disjunction-unsupported"),
])
def test_embedded_checker_refuses_unsupported_guarded_clauses(tmp_path, shape, reason):
    from gnd.export.emit import render_pyrel
    from gnd.export.pyrel_runtime import ExportInputError

    with pytest.raises(ExportInputError, match=reason):
        render_pyrel(_model(tmp_path, shape))


@pytest.mark.parametrize(("shape", "reason"), [
    ("membership", "membership-unsupported"),
    ("filters", "guarded-antecedent-filters-unsupported"),
    ("disjunction", "guarded-disjunction-unsupported"),
])
def test_ossie_identifies_rule_left_in_its_source_sidecar(tmp_path, shape, reason):
    from gnd.export.ossie import OssieInputError, render_ossie

    model = _model(tmp_path, shape)
    rendered = render_ossie(model, output_format="json")
    loss = json.loads(rendered.loss_report)
    assert any(row["pointer"] == "/constraints/0" and row["reason"] == reason for row in loss["dispositions"])
    with pytest.raises(OssieInputError, match=reason):
        render_ossie(model, output_format="json", strict=True)


def test_existing_export_bytes_are_stable(monkeypatch):
    from hashlib import sha256

    from gnd.export.emit import render_pyrel
    from gnd.export.pyrel_rules import render

    monkeypatch.chdir(BASE.parents[3])
    model = BASE.relative_to(Path.cwd())
    embedded = render_pyrel(Path("tests/fixtures/pyrel-oracle/basics.orm.yaml"))
    assert sha256(embedded.encode()).hexdigest() == "60a263a116a50f60070fa7d4c5b8affbc8d34ae163e4e4d7e8ef0476df82ea6f"
    # The two rules programs were pinned at GC4 and held through IR3 (6aacb928). The
    # pyrel-rules-coverage milestone then changed the program every model gets, on
    # purpose, in RP2 (6e04fe7f), RP1 (1350db9a), RP3 (33bd03db) and its close
    # (825078c8); these are the bytes since that close. The embedded program above
    # did not change.
    assert sha256(render(model, "duckdb").encode()).hexdigest() == "68bfe280d721a8fde82e06f0f537c5d19be603da000d8885108bb8980055c4c4"
    assert sha256(render(model, "lqp").encode()).hexdigest() == "2c99fa4e3c59cf9048c2d67c4304fe329be1e90bae62bbcc572db9f628403e2a"


def test_readable_rules_refuse_function_shaped_antecedent_filters(tmp_path):
    from gnd.export.pyrel_rules import ExportInputError, render

    path = _model(tmp_path, "filters")
    document = json.loads(path.read_bytes())
    document["constraints"][0]["where"][0]["left"] = {"fn": "add", "args": ["$a", 1]}
    path.write_text(json.dumps(document))
    with pytest.raises(ExportInputError, match="^guarded-where-term-unsupported$"):
        render(path, "duckdb")


@pytest.mark.parametrize(("shape", "operator", "amount", "status", "expected"), [
    ("membership", "in", 1500, None, "OK"),
    ("membership", "in", 2100, None, "violated"),
    ("membership", "not in", 1500, None, "violated"),
    ("membership", "not in", 2100, None, "OK"),
    ("filters", None, 2500, None, "violated"),
    ("filters", None, 2500, "exempt", "vacuous"),
    ("filters", None, 500, None, "vacuous"),
    ("filters", None, 1500, None, "OK"),
])
def test_readable_rule_duckdb_matches_public_checker(tmp_path, native_python, shape, operator, amount, status, expected):
    from support.cli_runner import run_main

    from gnd.export.pyrel_rules import render

    model_path = _model(tmp_path, shape)
    if operator is not None:
        document = json.loads(model_path.read_bytes())
        document["constraints"][0]["consequent"]["comparison"]["operator"] = operator
        model_path.write_text(json.dumps(document))
    facts = {
        "expense_in_category": [{"expense": 1, "category": "travel"}],
        "expense_has_amount": [{"expense": 1, "amount": amount}],
        "expense_has_status": [{"expense": 1, "status": status}] if status else [],
    }
    population = {
        "population": {"model": model_path.name, "source": "fixture", "covers": list(facts)},
        "facts": facts,
    }
    source = tmp_path / "program.py"
    source.write_text(render(model_path, "duckdb"))
    data = tmp_path / "population.json"
    data.write_text(json.dumps(population))
    core = run_main(["check", str(model_path), str(data), "--rule-ids", "--format", "json"])
    expected_verdict = {"OK": "pass", "vacuous": "vacuous", "violated": "fail"}[expected]
    row, = json.loads(core.stdout)["verdicts"]
    assert row["verdict"] == expected_verdict
    translated = subprocess.run(
        [native_python, "-I", str(source), str(data)], cwd=tmp_path, capture_output=True, text=True, timeout=35,
        check=False,
    )
    assert translated.returncode == core.returncode, (translated.stdout, translated.stderr)
    assert translated.stdout.startswith(f"policy_limit_travel  {expected}")
    if expected == "violated":
        witness = json.loads(translated.stdout.split("violated  ", 1)[1])
        assert row["offending_facts"] == [witness]
    if shape == "filters":
        population["population"]["covers"].remove("expense_has_status")
        data.write_text(json.dumps(population))
        core = run_main(["check", str(model_path), str(data), "--rule-ids", "--format", "json"])
        native_check = subprocess.run(
            [native_python, "-I", str(source), str(data)], cwd=tmp_path, capture_output=True, text=True,
            timeout=35, check=False,
        )
        assert native_check.returncode == core.returncode
        row, = json.loads(core.stdout)["verdicts"]
        if expected == "vacuous":
            assert row["verdict"] == "vacuous"
            assert "vacuous" in native_check.stdout
        else:
            assert row["verdict"] == "unchecked"
            assert "guarded-filter-coverage-missing" in native_check.stdout



@pytest.mark.parametrize("shape", ["membership", "filters", "derived-membership"])
def test_readable_clauses_compile_to_lqp_requirements_locally(tmp_path, native_python, shape):
    from gnd.export.pyrel_rules import render

    path = _model(tmp_path, "membership" if shape == "derived-membership" else shape)
    if shape == "derived-membership":
        _derive_membership(path)
    source = tmp_path / "rules.py"
    source.write_text(render(path, "lqp"))
    compiled = subprocess.run(
        [native_python, "-I", str(source), "--compile"], cwd=tmp_path, capture_output=True,
        text=True, timeout=35, check=False,
    )
    assert compiled.returncode == 0, (compiled.stdout, compiled.stderr)
    assert "requirements compiled" in compiled.stdout


def _derive_membership(path):
    source = json.loads(path.read_bytes())
    rule, = source["constraints"]
    source["constraints"] = []
    source["fact_types"].append({
        "id": "eligible_expense",
        "reading": "{Expense} is eligible",
        "roles": [{"object_type": "expense", "role_name": "expense"}],
        "derivation": "derived",
        "derivation_rule": {
            "body": rule["antecedent"], "where": [rule["consequent"]["comparison"]],
            "head": {"expense": "$e"},
        },
    })
    path.write_text(json.dumps(source))


@pytest.mark.parametrize("amount", [1500, 2100])
def test_readable_derivation_membership_agrees_with_deterministic_claim_check(tmp_path, native_python, amount):
    from support.cli_runner import run_main

    from gnd.export.pyrel_rules import render

    path = _model(tmp_path, "membership")
    _derive_membership(path)
    facts = {
        "expense_in_category": [{"expense": 1, "category": "travel"}],
        "expense_has_amount": [{"expense": 1, "amount": amount}],
        "expense_has_status": [],
        "eligible_expense": [{"expense": 1}],
    }
    population = {
        "population": {"model": path.name, "source": "fixture", "covers": list(facts)},
        "facts": facts,
    }
    data = tmp_path / "population.json"
    data.write_text(json.dumps(population))
    source = tmp_path / "program.py"
    source.write_text(render(path, "duckdb"))
    native_run = subprocess.run(
        [native_python, "-I", str(source), str(data)], cwd=tmp_path, capture_output=True,
        text=True, timeout=35, check=False,
    )
    core = run_main(["check", str(path), str(data)])
    assert native_run.returncode == core.returncode == (0 if amount == 1500 else 1), native_run.stderr
    assert ("violated" in native_run.stdout) == (amount == 2100)


def test_membership_helper_refuses_a_raw_relation_name_collision(tmp_path):
    from gnd.export.pyrel_rules import ExportInputError, render

    model = _model(tmp_path, "membership")
    document = json.loads(model.read_bytes())
    relation = next(fact for fact in document["fact_types"] if fact["id"] == "expense_has_status")
    relation["id"] = "policy_limit_travel_membership"
    model.write_text(json.dumps(document))
    with pytest.raises(ExportInputError, match="^membership-helper-name-collision$"):
        render(model, "duckdb")


@pytest.mark.parametrize("exporter", ["lean", "souffle"])
def test_finite_exports_refuse_guarded_antecedent_filters_by_name(tmp_path, exporter):
    from gnd.export.lean import render_lean
    from gnd.export.souffle import render_souffle

    model = _model(tmp_path, "filters").read_bytes()
    facts = {
        "expense_in_category": [{"expense": 1, "category": "travel"}],
        "expense_has_amount": [{"expense": 1, "amount": 2500}],
        "expense_has_status": [],
    }
    population = json.dumps({
        "population": {"model": "model.orm.json", "source": "fixture", "covers": list(facts)},
        "facts": facts,
    }).encode()
    if exporter == "lean":
        result = render_lean(model, population, toolchain="leanprover/lean4:v4.34.0")
    else:
        result = render_souffle(model, population, model_format="json")
    assert (result.exit_code, result.reason) == (2, "guarded-antecedent-filters-unsupported")
