"""Run the three milestone routes with a separately installed GND wheel."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from ruamel.yaml import YAML


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, document):
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def main():
    repo, wheel, root, receipt = (Path(value).resolve() for value in sys.argv[1:])
    root.mkdir()
    environment = dict(os.environ)
    environment.pop("PYTHONPATH", None)
    capture = subprocess.run(
        [sys.executable, "-I", "-c", "import pathlib,gnd,sys; "
         "assert pathlib.Path(gnd.__file__).resolve().is_relative_to(pathlib.Path(sys.prefix)); "
         "print(sys.version.split()[0])"],
        cwd=root, env=environment, check=True, capture_output=True,
    )
    runs = []

    def gnd(lane, *args, expected=0):
        completed = subprocess.run(
            [sys.executable, "-I", "-m", "gnd", *args],
            cwd=lane, env=environment, capture_output=True, timeout=60, check=False,
        )
        assert completed.returncode == expected, (args, completed.stdout, completed.stderr)
        runs.append({
            "cwd": lane.name,
            "args": args,
            "exit": completed.returncode,
            "stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(),
        })
        return completed.stdout

    corpus = repo / ".gnd-planning/milestones/guarded-rule-authoring/corpus/GA3"
    ga1 = root / "ga1"
    ga1.mkdir()
    shutil.copyfile(repo / "src/gnd/examples/rule_check/model.orm.yaml", ga1 / "model.orm.yaml")
    gnd(ga1, "synth", "model.orm.yaml", "--guarded-cases", "--out", "corpus", "--format", "json")
    manifest_path = ga1 / "corpus/guarded-cases.json"
    manifest = json.loads(manifest_path.read_bytes())
    assert len(manifest["rules"]) == 2
    for rule in manifest["rules"]:
        assert [case["verdict"] for case in rule["cases"]] == ["fail", "pass"]
        assert all(case["binding_count"] > 0 for case in rule["cases"])
    measured = json.loads(gnd(
        ga1, "measure", "corpus/ordinary/scoped.orm.yaml", "--populations",
        "corpus/ordinary/corpus", "--format", "json",
    ))
    assert measured["population_count"] == 15 and measured["checker_defects"] == []
    gnd(ga1, "measure", "model.orm.yaml", "--populations", "corpus/ordinary/corpus", expected=3)

    isolated = YAML(typ="safe").load(corpus / "model.orm.yaml")
    isolated["constraints"] = [{
        "id": "isolated",
        "type": "guarded",
        "modality": "alethic",
        "source": "user-supplied",
        "status": "confirmed",
        "antecedent": [{"fact_type": "component_uses", "bind": {"source": "$c", "target": "$c"}}],
        "consequent": {"atom": {"fact_type": "component_in_area",
                                "bind": {"component": "$c", "area": "cli"}}},
        "provenance": {"user_quote": "A component that uses itself is in the CLI area."},
    }]
    write_json(ga1 / "isolated.json", isolated)
    gnd(ga1, "synth", "isolated.json", "--guarded-cases", "--out", "isolated")
    isolated_manifest = ga1 / "isolated/guarded-cases.json"
    isolated_cases = json.loads(isolated_manifest.read_bytes())["rules"][0]["cases"]
    assert [case["verdict"] for case in isolated_cases] == ["fail", "pass"]
    for case in isolated_cases:
        assert case["binding_count"] == 1 and case["other_findings"] == []
        rows = json.loads((ga1 / "isolated" / case["population"]).read_bytes())["facts"]["component_uses"]
        assert len(rows) == 1 and rows[0]["source"] == rows[0]["target"]

    ga2, ga3 = root / "ga2", root / "ga3"
    for lane in (ga2, ga3):
        lane.mkdir()
        for name in ("model.orm.yaml", "population.json"):
            shutil.copyfile(corpus / name, lane / name)
    actor = ("--actor", "smoke", "--requested-at", "2026-11-11T00:00:00Z")
    gnd(
        ga2, "discover", "model.orm.yaml", "population.json", "--families", "guarded-join",
        "--joined-relation", "component_uses:source:target",
        "--joined-classifier", "component_in_area:component:area", *actor,
        "--out", "proposal.json", "--report", "report.json", "--format", "json",
    )
    discover_report = ga2 / "report.json"
    joined = json.loads(discover_report.read_bytes())
    assert joined["joined_rules"]["reason"] is None
    assert any(row["support"] == {"numerator": 1, "denominator": 1} for row in joined["emitted"])
    gnd(ga2, "evolve", "preview", "model.orm.yaml", "proposal.json",
        "--workspace", ".", "--records", "records", "--out", "preview.json")

    shutil.copyfile(corpus / "rules.tsv", ga3 / "rules.tsv")
    gnd(ga3, "export", "ilp", "model.orm.yaml", "--population", "population.json",
        "--target", "amie", "--out", "export")
    facts = ga3 / "export/amie/facts.tsv"
    write_json(ga3 / "reported.json", {
        "schema_version": "gnd-mined-run/1",
        "learner": {"name": "amie", "version": "4.0.0"},
        "rules_sha256": digest(ga3 / "rules.tsv"),
        "population_sha256": digest(ga3 / "population.json"),
        "facts_sha256": digest(facts),
    })
    imported = json.loads(gnd(
        ga3, "import", "mined-rules", "model.orm.yaml", "rules.tsv", "--population",
        "population.json", "--reported", "reported.json", "--target", "amie",
        "--out", "proposal.json", *actor, "--format", "json",
    ))
    assert [row["support"] for row in imported["rules"]] == [{"numerator": 1, "denominator": 1}] * 3
    gnd(ga3, "evolve", "preview", "model.orm.yaml", "proposal.json",
        "--workspace", ".", "--records", "records", "--out", "preview.json")
    proposal = ga3 / "proposal.json"
    core = json.loads(proposal.read_bytes())["operations"][0]["after"]
    assert core["consequent"]["atom"]["bind"] == {"component": "$a", "area": "cli"}

    artifacts = [manifest_path, isolated_manifest, discover_report, ga2 / "proposal.json",
                 proposal, facts, ga3 / "reported.json"]
    inputs = [ga1 / "model.orm.yaml", ga1 / "isolated.json", ga2 / "model.orm.yaml",
              ga2 / "population.json", ga3 / "model.orm.yaml", ga3 / "population.json", ga3 / "rules.tsv"]
    write_json(receipt, {
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
        "wheel": wheel.name,
        "wheel_sha256": digest(wheel),
        "lock_sha256": digest(repo / "uv.lock"),
        "python": capture.stdout.decode().strip(),
        "imported_from_installed_environment": True,
        "inputs": {str(path.relative_to(root)): digest(path) for path in inputs},
        "commands": runs,
        "artifacts": {str(path.relative_to(root)): digest(path) for path in artifacts},
    })
    print("Installed smoke passed: GA1 scoped and isolated cases, GA2 proposal preview, GA3 typed AMIE import and preview.")


if __name__ == "__main__":
    main()
