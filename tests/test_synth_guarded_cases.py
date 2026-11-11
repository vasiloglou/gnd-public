import json
from copy import deepcopy
from pathlib import Path

from ruamel.yaml import YAML
from support.cli_runner import run_main

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "src/gnd/examples/rule_check/model.orm.yaml"
EXPECTED = ROOT / ".gnd-planning/milestones/guarded-rule-authoring/corpus/GA1/expected.json"


def test_guarded_pairs_and_ordinary_corpus(tmp_path):
    document = YAML(typ="safe").load(EXAMPLE)
    template = document["constraints"][0]
    antecedent = {"fact_type": "component_is_in_area", "bind": {"component": "$c", "area": "core"}}
    witness = {
        "fact_type": "component_ships_in_release",
        "bind": {"component": "$c", "release": "v1"},
    }
    consequents = {
        "atom": {"atom": witness},
        "absence": {"absence": witness},
        "exists": {"exists": {"atoms": [deepcopy(witness)]}},
        "comparison": template["consequent"],
        "unserved": {"atom": antecedent},
    }
    consequents["exists"]["exists"]["atoms"][0]["bind"]["release"] = "$r"
    document["constraints"] = [
        {
            **template,
            "id": kind,
            "modality": "deontic" if kind == "exists" else "alethic",
            "antecedent": template["antecedent"] if kind == "comparison" else [antecedent],
            "consequent": consequent,
        }
        for kind, consequent in consequents.items()
    ]
    model = tmp_path / "model.orm.json"
    model.write_text(json.dumps(document), encoding="utf-8")
    out = tmp_path / "out"
    expected = json.loads(EXPECTED.read_bytes())

    run = run_main(["synth", str(model), "--out", str(out), "--guarded-cases", "--seed", "17"])
    assert run.returncode == expected["mixed"]["exit"], (run.stdout, run.stderr)

    report = json.loads((out / "guarded-cases.json").read_bytes())
    assert report["schema_version"] == "gnd-guarded-cases/1"
    assert [rule["rule_id"] for rule in report["rules"]] == list(consequents)
    for rule in report["rules"]:
        answer = expected[rule["rule_id"]]
        if "reason" in answer:
            assert {field: rule[field] for field in answer} == answer
            continue
        assert rule["reason"] is None
        assert {case["kind"]: case["verdict"] for case in rule["cases"]} == answer
        antecedent_rows = []
        for case in rule["cases"]:
            assert case["binding_count"] > 0
            population = out / case["population"]
            rows = json.loads(population.read_bytes())["facts"]["component_is_in_area"]
            antecedent_rows.append(rows)
            assert "other_findings" in case
        if rule["rule_id"] != "comparison":
            assert antecedent_rows[0] == antecedent_rows[1]
            assert [row["area"] for row in antecedent_rows[0]] == ["core"]
    assert report["ordinary"]["omitted_guarded_refs"] == [
        row["constraint_ref"] for row in report["rules"]
    ]
    ordinary = out / "ordinary/corpus"
    index = json.loads((ordinary / "index.json").read_bytes())
    assert all(name in json.dumps(index) for name in expected["mixed"]["ordinary"])
    for candidate, outcome in [
        (model, "measure_full"),
        (out / "ordinary/scoped.orm.yaml", "measure_scoped"),
    ]:
        measured = run_main(["measure", str(candidate), "--populations", str(ordinary)])
        assert measured.returncode == expected["mixed"][outcome], (measured.stdout, measured.stderr)


def _guarded_run(model, out, *args):
    return run_main(
        ["synth", str(model), "--out", str(out), "--guarded-cases", "--format", "json", *args]
    )


def test_guarded_case_bytes_repeat_and_existing_root_is_preserved(tmp_path):
    one, two = tmp_path / "one", tmp_path / "two"
    assert _guarded_run(EXAMPLE, one).returncode == 0
    assert _guarded_run(EXAMPLE, two, "--seed", "0").returncode == 0

    def artifacts(root):
        return {
            path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()
        }

    expected = artifacts(one)
    assert expected == artifacts(two)
    assert _guarded_run(EXAMPLE, one).returncode == 74
    assert artifacts(one) == expected


def test_guarded_unavailable_rules_and_run_limit(tmp_path, monkeypatch):
    from gnd.synth import guarded_cases

    document = YAML(typ="safe").load(EXAMPLE)
    no_id, unreachable, disjoint = [deepcopy(document["constraints"][0]) for _ in range(3)]
    del no_id["id"]
    unreachable["id"] = "literal_outside_domain"
    unreachable["antecedent"].append(
        {
            "fact_type": "component_is_in_area",
            "bind": {"component": "$c", "area": "legacy"},
        }
    )
    disjoint["id"] = "disconnected"
    disjoint["antecedent"].append(
        {
            "fact_type": "component_ships_in_release",
            "bind": {"component": "$d", "release": "$r"},
        }
    )
    template = document["constraints"][1]
    document["constraints"] = [
        {
            "type": "value",
            "object_type": "area",
            "allowed": ["core"],
            "provenance": {"user_quote": "Area is core."},
            "modality": "alethic",
            "source": "user-supplied",
            "status": "confirmed",
        },
        no_id,
        unreachable,
        disjoint,
        template,
        {**template, "id": "after_limit"},
    ]
    model = tmp_path / "rules.json"
    model.write_text(json.dumps(document), encoding="utf-8")
    out = tmp_path / "out"
    monkeypatch.setattr(guarded_cases, "RUN_WORK", 32)
    result = _guarded_run(model, out)
    assert result.returncode == 0, (result.stdout, result.stderr)
    manifest = json.loads((out / "guarded-cases.json").read_bytes())
    assert [(row["rule_id"], row["reason"]) for row in manifest["rules"]] == [
        (None, "missing-id"),
        ("literal_outside_domain", "antecedent-unreachable"),
        ("disconnected", "unsupported-shape"),
        ("no_draft_releases", "search-limit"),
        ("after_limit", "search-limit"),
    ]
    assert manifest["rules"][0]["constraint_ref"] == "constraints[1]"
    assert manifest["ordinary"]["constraint_refs"]["constraints[0]"] == "constraints[0]"
    assert (out / manifest["ordinary"]["corpus"] / "index.json").exists()


def test_checker_disagreement_publishes_only_quarantine(tmp_path, monkeypatch):
    from gnd.synth import guarded_service

    original = guarded_service.check

    def wrong_count(model, population):
        report = original(model, population)
        guarded = next(row for row in report.verdicts if row.constraint_type == "guarded")
        guarded.binding_count = 0
        return report

    monkeypatch.setattr(guarded_service, "check", wrong_count)
    out = tmp_path / "out"
    run = _guarded_run(EXAMPLE, out)
    assert run.returncode == 6
    quarantine = Path(json.loads(run.stdout)["quarantine"])
    assert list(out.iterdir()) == [out / "quarantine"]
    evidence = json.loads(quarantine.read_bytes())
    assert evidence["expected"]["binding_count"] == 1
    assert evidence["observed"]["binding_count"] == 0
    assert evidence["rule_id"] == "no_legacy_components"


def test_malformed_guarded_input_leaves_no_output(tmp_path):
    model = tmp_path / "malformed.orm.yaml"
    model.write_text("constraints: [", encoding="utf-8")
    out = tmp_path / "out"
    assert _guarded_run(model, out).returncode == 3
    assert not out.exists()


def test_run_limit_preserves_a_served_pair(tmp_path, monkeypatch):
    from random import Random

    from gnd.model import load_model
    from gnd.model_index import ModelIndex
    from gnd.synth import guarded_cases
    from gnd.synth.guarded import _WorkBudget

    model = load_model(EXAMPLE)
    index = ModelIndex.for_model(model)
    guards = [row for row in index.iter_constraints() if row[1]["type"] == "guarded"]
    first_rule = guards[0][1]
    budget = _WorkBudget()
    pair, reason = guarded_cases.build_pair(model, index, first_rule, Random(0), budget)
    assert pair and reason is None
    guarded_cases.confirmation_work(pair, guards, budget)
    monkeypatch.setattr(guarded_cases, "RUN_WORK", budget.used)
    out = tmp_path / "out"
    assert _guarded_run(EXAMPLE, out).returncode == 0
    report = json.loads((out / "guarded-cases.json").read_bytes())
    served, refused = report["rules"]
    assert len(served["cases"]) == 2
    assert refused["reason"] == "search-limit"
    assert (out / report["ordinary"]["corpus"] / "index.json").is_file()


def test_guarded_case_invariant_failure_aborts_before_publication(tmp_path, monkeypatch):
    from gnd.errors import PopulationLoadError
    from gnd.synth import guarded_service

    def refuse(*args, **kwargs):
        raise PopulationLoadError("injected case admission failure")

    monkeypatch.setattr(guarded_service, "load_population_bytes", refuse)
    out = tmp_path / "out"
    result = _guarded_run(EXAMPLE, out)
    assert result.returncode == 5
    assert b"injected case admission failure" in result.stdout
    assert not out.exists()


def test_comparison_between_two_integer_variables_can_generate_equality(tmp_path):
    document = YAML(typ="safe").load(EXAMPLE)
    for object_type in document["object_types"]:
        if object_type["id"] in {"area", "release"}:
            object_type["primitive"] = "Integer"
    rule = document["constraints"][0]
    rule["antecedent"].append(
        {
            "fact_type": "component_ships_in_release",
            "bind": {"component": "$c", "release": "$r"},
        }
    )
    rule["consequent"] = {"comparison": {"operator": "=", "left": "$a", "right": "$r"}}
    document["constraints"] = [rule]
    model = tmp_path / "integer-model.json"
    model.write_text(json.dumps(document), encoding="utf-8")
    out = tmp_path / "out"
    assert _guarded_run(model, out).returncode == 0
    result = json.loads((out / "guarded-cases.json").read_bytes())["rules"][0]
    assert result["reason"] is None
    assert [case["verdict"] for case in result["cases"]] == ["fail", "pass"]


def test_explosive_collateral_guard_is_refused_before_checker(tmp_path, monkeypatch):
    from gnd.synth import guarded_service

    document = YAML(typ="safe").load(EXAMPLE)
    target = document["constraints"][0]
    target["antecedent"][0]["bind"]["area"] = "core"
    target["consequent"] = {
        "atom": {
            "fact_type": "component_is_in_area",
            "bind": {"component": "$c", "area": "extra"},
        }
    }
    collateral = {
        **deepcopy(target),
        "id": "wide_collateral_join",
        "antecedent": [
            {"fact_type": "component_is_in_area", "bind": {"component": "$c", "area": f"$v{i}"}}
            for i in range(18)
        ],
        "consequent": {"comparison": {"operator": "=", "left": "$v0", "right": "$v1"}},
    }
    document["constraints"] = [target, collateral]
    model = tmp_path / "wide.json"
    model.write_text(json.dumps(document), encoding="utf-8")
    original = guarded_service.check

    def bounded_check(model, population):
        assert len(population.facts.get("component_is_in_area", [])) < 2, (
            "candidate allows 2**18 bindings in another guard"
        )
        return original(model, population)

    monkeypatch.setattr(guarded_service, "check", bounded_check)
    out = tmp_path / "out"
    assert _guarded_run(model, out).returncode == 0
    manifest = json.loads((out / "guarded-cases.json").read_bytes())
    assert manifest["rules"][0]["reason"] == "search-limit"
    assert manifest["rules"][0]["cases"] == []
    assert (out / manifest["ordinary"]["corpus"] / "index.json").is_file()
