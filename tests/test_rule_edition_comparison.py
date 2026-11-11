"""GW2 controls for comparing findings across rule editions."""

import copy
import json

import pytest
from jsonschema import Draft202012Validator
from ruamel.yaml import YAML
from support.cli_runner import run_main
from support.repository import REPO_ROOT

from gnd.report import load_report_schema

EXAMPLE = REPO_ROOT / "src/gnd/examples/rule_check"
ANSWER = json.loads((REPO_ROOT / (
    ".gnd-planning/milestones/guarded-rule-workflows/corpus/GW2/expected.json"
)).read_text())
IMPORT = "component_imports_component"
AREA = "component_is_in_area"


def _write(tmp_path, *, rename=False, collision=False):
    yaml = YAML(typ="safe")
    base = yaml.load((EXAMPLE / "model.orm.yaml").read_text())
    base["fact_types"] = base["fact_types"][:2]
    base["fact_types"][0].pop("constraints")
    guard = base["constraints"][0]
    guard.update(
        id="local_imports",
        antecedent=[{"fact_type": IMPORT, "bind": {"importer": "$source", "imported": "$target"}}],
        consequent={"comparison": {"operator": "=", "left": "$source", "right": "$target"}},
    )
    base["constraints"] = [guard]
    head = copy.deepcopy(base)
    guard = head["constraints"][0]
    source = "$renamed" if rename else "$source"
    guard["antecedent"][0]["bind"]["importer"] = source
    guard["consequent"]["comparison"]["left"] = source
    guard["antecedent"].append({"fact_type": AREA, "bind": {"component": source, "area": "$extra"}})
    population = yaml.load((EXAMPLE / "head.population.yaml").read_text())
    population["population"]["covers"] = [IMPORT, AREA]
    population["facts"] = {
        IMPORT: [{"importer": f"caller{i}", "imported": "api"} for i in range(43)],
        AREA: [{"component": "caller0", "area": "core"}],
    }
    if collision:
        population["facts"][AREA].append({"component": "caller0", "area": "other"})
    for name, doc in (("base.orm.yaml", base), ("head.orm.yaml", head), ("population.yaml", population)):
        (tmp_path / name).write_text(json.dumps(doc))
    return base, head


def _compare(tmp_path, *, reverse=False, output="json"):
    base, head = ("head.orm.yaml", "base.orm.yaml") if reverse else ("base.orm.yaml", "head.orm.yaml")
    result = run_main(
        ["check", head, "population.yaml", "--baseline-model", base, "--format", output],
        cwd=tmp_path,
    )
    if output == "json":
        Draft202012Validator(load_report_schema()).validate(json.loads(result.stdout))
    return result


@pytest.mark.parametrize("rename", [False, True])
def test_same_band_narrowing_and_reverse(tmp_path, rename):
    _write(tmp_path, rename=rename)
    for side in ("base", "head"):
        check = run_main(
            ["check", f"{side}.orm.yaml", "population.yaml", "--rule-ids", "--format", "json"],
            cwd=tmp_path,
        )
        verdict = json.loads(check.stdout)["verdicts"][0]
        assert {"exit": check.returncode, "offending": len(verdict["offending_facts"])} == ANSWER[f"{side}_check"]
    for direction in ("forward", "reverse"):
        result = _compare(tmp_path, reverse=direction == "reverse")
        assert result.returncode == 0
        report = json.loads(result.stdout)
        assert report["schema_version"] == "gnd-rule-edition-comparison/1"
        assert report["base"]["exit_code"] == report["head"]["exit_code"] == 1
        row, = report["rules"]
        assert row["address"] == "constraint:local_imports"
        assert row["pairing"] == "paired"
        assert {"exit": result.returncode, **{name: len(rows) for name, rows in row["delta"].items()}} == ANSWER[direction]


def test_projection_collision_withholds_the_rule_delta(tmp_path):
    _write(tmp_path, collision=True)
    result = _compare(tmp_path)
    assert result.returncode == 4
    row, = json.loads(result.stdout)["rules"]
    assert row["reason"] == "binding-projection-collision"
    assert row["delta"] is None


def test_edition_comparison_reports_added_removed_and_anonymous(tmp_path):
    base, head = _write(tmp_path)
    removed = copy.deepcopy(base["constraints"][0])
    removed["id"] = "removed_rule"
    base["constraints"].append(removed)
    anonymous = copy.deepcopy(head["constraints"][0])
    del anonymous["id"]
    added = copy.deepcopy(head["constraints"][0])
    added["id"] = "added_rule"
    added["modality"] = "deontic"
    head["constraints"] = [added, anonymous, *head["constraints"]]
    (tmp_path / "base.orm.yaml").write_text(json.dumps(base))
    (tmp_path / "head.orm.yaml").write_text(json.dumps(head))
    result = _compare(tmp_path)
    assert result.returncode == 0
    rules = {row["address"]: row for row in json.loads(result.stdout)["rules"]}
    assert len(rules["constraint:removed_rule"]["delta"]["base_only"]) == 43
    assert rules["constraint:removed_rule"]["pairing"] == "removed"
    assert len(rules["constraint:added_rule"]["delta"]["head_only"]) == 1
    assert rules["constraint:added_rule"]["head"]["verdict"] == "warning"
    assert rules["constraint:added_rule"]["pairing"] == "added"
    assert len(rules["constraint:local_imports"]["delta"]["standing"]) == 1
    assert rules["constraints[1]"]["pairing"] == "unpaired"
    assert rules["constraints[1]"]["delta"] is None


@pytest.mark.parametrize("side", ["base", "head"])
def test_ill_formed_side_is_reported(tmp_path, side):
    _write(tmp_path)
    (tmp_path / f"{side}.orm.yaml").write_text("{}")
    result = _compare(tmp_path)
    assert result.returncode == 3
    report = json.loads(result.stdout)
    assert report["reason"] == f"{side}-model-ill-formed"
    assert report["rules"] == []


def test_mismatched_vocabulary_precedes_population_io(tmp_path):
    _, head = _write(tmp_path)
    head["object_types"].pop()
    (tmp_path / "head.orm.yaml").write_text(json.dumps(head))
    (tmp_path / "population.yaml").unlink()
    result = _compare(tmp_path)
    assert result.returncode == 3
    assert json.loads(result.stdout)["reason"] == "vocabulary-mismatch"


def test_invalid_population_bytes(tmp_path):
    _write(tmp_path)
    (tmp_path / "population.yaml").write_text("{")
    result = _compare(tmp_path)
    assert result.returncode == 3
    assert json.loads(result.stdout)["reason"] == "base-population-ill-formed"


def test_population_is_read_once_and_work_exhaustion_has_no_partial_delta(tmp_path, monkeypatch):
    from gnd import baseline, checking_service

    _write(tmp_path)
    original = checking_service.read_population_bytes
    visits = []

    def read(path):
        visits.append(path)
        return original(path)

    monkeypatch.setattr(checking_service, "read_population_bytes", read)
    monkeypatch.setattr(baseline, "EDITION_COMPARISON_WORK", 10)
    result = _compare(tmp_path)
    assert result.returncode == 4
    assert visits == ["population.yaml"]
    report = json.loads(result.stdout)
    assert report["reason"] == "comparison-work-limit"
    assert report["rules"] == []


@pytest.mark.parametrize("conflict", [
    ["--baseline", "missing.pop"], ["--populations", "missing"], ["--allow-vacuous"], ["--guarded-diagnostics"],
])
def test_edition_option_conflicts_before_io(tmp_path, conflict):
    result = run_main(
        ["check", "missing.orm.yaml", "missing.pop", "--baseline-model", "missing-base.orm.yaml", *conflict],
        cwd=tmp_path,
    )
    assert result.returncode == 64
    assert b"--baseline-model excludes" in result.stderr


def _verdict(state, rows=()):
    return {
        "address": "constraint:test", "addressing": "declared-id", "constraint_ref": "constraints[0]",
        "constraint_type": "value", "verdict": state, "modality": "alethic", "offending_facts": rows,
    }


def test_rowless_typed_and_unknown_outcomes():
    from gnd.baseline import compare_editions

    rows, incomplete = compare_editions([_verdict("fail")], [_verdict("vacuous")], {}, {})
    assert not incomplete
    assert rows[0]["delta"]["base_only"] == [None]
    rows, incomplete = compare_editions(
        [_verdict("fail", [1, True])], [_verdict("fail", [1.0])], {}, {},
    )
    assert not incomplete
    assert rows[0]["delta"] == {
        "base_only": [True], "head_only": [], "standing": [{"base": 1, "head": 1.0}],
    }
    rows, incomplete = compare_editions([_verdict("unchecked")], [_verdict("unchecked")], {}, {})
    assert incomplete
    assert rows[0]["reason"] == "unchecked"
    assert rows[0]["delta"] is None


def test_text_reports_direction_and_bands(tmp_path):
    _write(tmp_path)
    result = _compare(tmp_path, output="text")
    assert result.returncode == 0
    assert b"base check exit 1" in result.stdout
    assert b"head check exit 1" in result.stdout
    assert b"42 base-only, 0 head-only, 1 standing" in result.stdout
    assert b'base-only {"$source":"caller1","$target":"api"}' in result.stdout


def test_conflicting_role_alignment_is_incomparable(tmp_path):
    base, head = _write(tmp_path)
    base["constraints"][0]["antecedent"].append({
        "fact_type": AREA, "bind": {"component": "$source", "area": "$extra"},
    })
    head["constraints"][0]["antecedent"][1]["bind"]["component"] = "$target"
    (tmp_path / "base.orm.yaml").write_text(json.dumps(base))
    (tmp_path / "head.orm.yaml").write_text(json.dumps(head))
    population_path = tmp_path / "population.yaml"
    population = json.loads(population_path.read_text())
    population["facts"][AREA].append({"component": "api", "area": "core"})
    population_path.write_text(json.dumps(population))
    result = _compare(tmp_path)
    assert result.returncode == 4
    row, = json.loads(result.stdout)["rules"]
    assert row["reason"] == "binding-alignment-ambiguous"
    assert row["delta"] is None


def test_population_header_is_validated_against_each_edition(tmp_path):
    _, head = _write(tmp_path)
    head["model_id"] = "urn:gnd-example:rule-check@2"
    (tmp_path / "head.orm.yaml").write_text(json.dumps(head))
    result = _compare(tmp_path)
    assert result.returncode == 3
    report = json.loads(result.stdout)
    assert report["reason"] == "head-population-ill-formed"
    assert report["issues"][0]["rule_id"] == "population:model-id-mismatch"
    population_path = tmp_path / "population.yaml"
    population = json.loads(population_path.read_text())
    del population["population"]["model_id"]
    population_path.write_text(json.dumps(population))
    assert _compare(tmp_path).returncode == 0
