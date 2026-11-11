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
        for case in rule["cases"]:
            assert case["binding_count"] > 0
            assert (out / case["population"]).is_file()
    ordinary = out / "ordinary/corpus"
    index = json.loads((ordinary / "index.json").read_bytes())
    assert all(name in json.dumps(index) for name in expected["mixed"]["ordinary"])
    for candidate, outcome in [
        (model, "measure_full"),
        (out / "ordinary/scoped.orm.yaml", "measure_scoped"),
    ]:
        measured = run_main(["measure", str(candidate), "--populations", str(ordinary)])
        assert measured.returncode == expected["mixed"][outcome], (measured.stdout, measured.stderr)
