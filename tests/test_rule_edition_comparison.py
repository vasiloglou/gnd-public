"""GW2 controls for comparing findings across rule editions."""

import copy
import json

import pytest
from ruamel.yaml import YAML

from support.cli_runner import run_main
from support.repository import REPO_ROOT

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
    return run_main(
        ["check", head, "population.yaml", "--baseline-model", base, "--format", output],
        cwd=tmp_path,
    )


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
