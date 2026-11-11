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


def test_bad_literals_and_recursion_preserve_atomic_refusal(tmp_path):
    line = RULES.splitlines()[0]
    for index, (rule, reason) in enumerate(
        (
            (line.replace("area:cli", "component:cli", 1), "constant-atom"),
            (line.replace("area:cli", r"area:cli\q", 1), "constant-atom"),
            (line.replace("area:cli", "area:$cli", 1), "constant-spelling"),
            (RULES.splitlines()[2].replace("rank:7", "rank:07", 1), "constant-atom"),
            (RULES.splitlines()[2].replace("flag:true", "flag:True", 1), "constant-atom"),
            (line.replace("area:cli", "?c"), "recursion"),
            (
                line.replace(
                    line.split("\t")[0],
                    "?a f_component_in_area area:cli => ?a f_component_in_area area:cli",
                ),
                "recursion",
            ),
        )
    ):
        work = tmp_path / str(index)
        work.mkdir()
        result, proposal = _import(work, _prepare(work, rule + "\n"))
        assert result.returncode == 3
        assert f"rule 0: {reason}:".encode() in result.stderr
        assert not proposal.exists()


def test_literal_count_uses_distinct_pairs_and_requires_full_confidence(tmp_path):
    line = RULES.splitlines()[0].split("\t")
    wrong_support = tmp_path / "wrong-support"
    wrong_support.mkdir()
    line[4] = "2"
    result, proposal = _import(wrong_support, _prepare(wrong_support, "\t".join(line) + "\n"))
    assert result.returncode == 3 and b"support-mismatch" in result.stderr
    assert not proposal.exists()

    population = json.loads((CORPUS / "population.json").read_bytes())
    population["facts"]["component_in_area"][0]["area"] = "core"
    wrong_head = tmp_path / "wrong-head"
    wrong_head.mkdir()
    line[4] = "0"
    result, proposal = _import(wrong_head, _prepare(wrong_head, "\t".join(line) + "\n", population))
    assert result.returncode == 3 and b"does-not-hold" in result.stderr
    assert not proposal.exists()


def test_amie_per_rule_and_aggregate_work_are_bounded_before_count(tmp_path, monkeypatch):
    from gnd.export import ilp_amie

    inputs = _prepare(tmp_path)
    original = ilp_amie.count

    def count_was_reached(*args, **kwargs):
        raise AssertionError("a join ran before work admission")

    monkeypatch.setattr(ilp_amie, "count", count_was_reached)
    monkeypatch.setattr(ilp_amie, "MAX_JOIN_ROWS", 19)
    result, proposal = _import(tmp_path, inputs)
    assert result.returncode == 3 and b"rule 0: too-large" in result.stderr
    assert not proposal.exists()
    monkeypatch.setattr(ilp_amie, "MAX_JOIN_ROWS", 20)
    monkeypatch.setattr(ilp_amie, "MAX_RECOUNT_WORK", 125)
    result, proposal = _import(tmp_path, inputs)
    assert result.returncode == 3 and b"rule 2: too-large: aggregate" in result.stderr
    assert not proposal.exists()
    monkeypatch.setattr(ilp_amie, "count", original)
    monkeypatch.setattr(ilp_amie, "MAX_RECOUNT_WORK", 126)
    result, proposal = _import(tmp_path, inputs)
    assert result.returncode == 0, result.stderr
    assert proposal.is_file()


def test_constant_first_extraction_and_escaped_text_roundtrip(tmp_path):
    from gnd.export import ilp_amie

    assert ilp_amie.extract_rules("AMIE settings\n" + RULES + "done\n") == RULES
    population = json.loads((CORPUS / "population.json").read_bytes())
    literal = "cli:team\tteam\\name\n"
    population["facts"]["component_in_area"][1]["area"] = literal
    line = RULES.splitlines()[1].replace("area:cli", r"area:cli:team\tteam\\name\n")
    result, proposal = _import(tmp_path, _prepare(tmp_path, line + "\n", population))
    assert result.returncode == 0, result.stderr
    core = json.loads(proposal.read_bytes())["operations"][0]["after"]
    assert core["consequent"]["atom"]["bind"]["area"] == literal


def test_mined_candidate_reports_wrong_category_on_fresh_population(tmp_path):
    result, proposal = _import(tmp_path, _prepare(tmp_path))
    assert result.returncode == 0, result.stderr
    candidate = tmp_path / "candidate.orm.yaml"
    candidate.write_text(
        json.loads(proposal.read_bytes())["candidate_model"]["text"], encoding="utf-8"
    )
    wrong = json.loads((CORPUS / "population.json").read_bytes())
    wrong["facts"]["component_in_area"][0]["area"] = "core"
    population = tmp_path / "wrong.json"
    population.write_text(json.dumps(wrong), encoding="utf-8")
    checked = run_main(
        [
            "check",
            str(candidate),
            str(population),
            "--guarded-diagnostics",
            "--format",
            "json",
        ]
    )
    assert checked.returncode == 0, (checked.stdout, checked.stderr)
    report = json.loads(checked.stdout)
    warnings = [row for row in report["verdicts"] if row["verdict"] == "warning"]
    assert len(warnings) == 1
    assert warnings[0]["offending_facts"] == [{"$a": "a", "$b": "b"}, {"$a": "a", "$b": "c"}]
