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
