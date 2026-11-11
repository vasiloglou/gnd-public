import hashlib
import json
import shutil
from pathlib import Path

from support.cli_runner import run_main

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / ".gnd-planning/milestones/guarded-rule-authoring/corpus/GA3"
RULES = (CORPUS / "rules.tsv").read_text(encoding="utf-8")


def _prepare(work, rules=RULES, population=None):
    model = work / "model.orm.yaml"
    shutil.copyfile(CORPUS / model.name, model)
    facts = work / "population.json"
    if population is None:
        shutil.copyfile(CORPUS / facts.name, facts)
    else:
        facts.write_text(json.dumps(population), encoding="utf-8")
    rules_path = work / "rules.tsv"
    rules_path.write_text(rules, encoding="utf-8")
    export = work / "export"
    result = run_main(
        [
            "export",
            "ilp",
            str(model),
            "--population",
            str(facts),
            "--target",
            "amie",
            "--out",
            str(export),
        ]
    )
    assert result.returncode == 0, (result.stdout, result.stderr)
    record = work / "reported.json"
    record.write_text(
        json.dumps(
            {
                "schema_version": "gnd-mined-run/1",
                "learner": {"name": "amie", "version": "4.0.0"},
                "rules_sha256": hashlib.sha256(rules_path.read_bytes()).hexdigest(),
                "population_sha256": hashlib.sha256(facts.read_bytes()).hexdigest(),
                "facts_sha256": hashlib.sha256(
                    (export / "amie/facts.tsv").read_bytes()
                ).hexdigest(),
            }
        ),
        encoding="utf-8",
    )
    return model, facts, rules_path, record


def _import(work, inputs):
    model, facts, rules, record = inputs
    proposal = work / "proposal.json"
    result = run_main(
        [
            "import",
            "mined-rules",
            str(model),
            str(rules),
            "--population",
            str(facts),
            "--reported",
            str(record),
            "--target",
            "amie",
            "--out",
            str(proposal),
            "--actor",
            "ga3-test",
            "--requested-at",
            "2026-11-11T00:00:00Z",
            "--format",
            "json",
        ]
    )
    return result, proposal


def test_amie_literals_in_all_positions_and_shared_head_relation(tmp_path):
    inputs = _prepare(tmp_path)
    result, proposal = _import(tmp_path, inputs)
    assert result.returncode == 0, (result.stdout, result.stderr)
    report = json.loads(result.stdout)
    assert [row["support"] for row in report["rules"]] == [{"numerator": 1, "denominator": 1}] * 3
    rules = [op["after"] for op in json.loads(proposal.read_bytes())["operations"]]
    assert rules[0]["antecedent"][1]["bind"] == {"component": "$b", "area": "cli"}
    assert rules[0]["consequent"]["atom"]["bind"] == {"component": "$a", "area": "cli"}
    assert rules[1]["antecedent"][0]["bind"] == {"source": "a", "target": "b"}
    assert rules[1]["consequent"]["atom"]["bind"] == {"component": "b", "area": "cli"}
    assert rules[2]["antecedent"][0]["bind"] == {"rank": 7, "flag": True}
    assert rules[2]["consequent"]["atom"]["bind"] == {"rank": 7, "flag": True}
    preview = run_main(
        [
            "evolve",
            "preview",
            str(inputs[0]),
            str(proposal),
            "--workspace",
            str(tmp_path),
            "--records",
            str(tmp_path / "records"),
            "--out",
            str(tmp_path / "preview.json"),
        ]
    )
    assert preview.returncode == 0, (preview.stdout, preview.stderr)
