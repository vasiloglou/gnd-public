import json
from pathlib import Path

from support.cli_runner import run_main

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "src/gnd/examples/rule_check/model.orm.yaml"
EXPECTED = json.loads(
    (ROOT / ".gnd-planning/milestones/guarded-rule-authoring/corpus/GA2/expected.json").read_bytes()
)
RELATION = EXPECTED["relation"]
CLASSIFIER = EXPECTED["classifier"]
MARKER = EXPECTED["marker"]
SELECTORS = [
    "--families",
    "guarded-join",
    "--joined-relation",
    f"{RELATION}:importer:imported",
    "--joined-classifier",
    f"{CLASSIFIER}:component:area",
]


def _population(tmp_path, *, missing=False, ambiguous=False, uncovered=False):
    components = [f"core{i}" for i in range(21)]
    edges = [{"importer": "source", "imported": name} for name in components[:20]]
    edges += [{"importer": "source", "imported": "app2"}, {"importer": "app1", "imported": "app2"}]
    classes = [{"component": name, "area": "core"} for name in ["source", *components]]
    classes += [{"component": "app1", "area": "app"}, {"component": "app2", "area": "app"}]
    if missing:
        classes.pop()
    if ambiguous:
        classes.append({"component": "source", "area": "app"})
    covers = [RELATION, MARKER] if uncovered else [RELATION, CLASSIFIER, MARKER]
    model = tmp_path / MODEL.name
    model.write_bytes(MODEL.read_bytes())
    path = tmp_path / "relations.population.json"
    path.write_text(
        json.dumps(
            {
                "population": {"model": model.name, "source": "fixture", "covers": covers},
                "facts": {
                    RELATION: edges + [edges[0]],
                    CLASSIFIER: [] if uncovered else classes + [classes[0]],
                    MARKER: [{"component": "core0", "owner": "private"}],
                },
            }
        ),
        encoding="utf-8",
    )
    return model, path


def _discover(tmp_path, model, population, *flags):
    proposal, report = tmp_path / "proposal.json", tmp_path / "report.json"
    run = run_main(
        [
            "discover",
            str(model),
            str(population),
            *flags,
            "--actor",
            "ga2-test",
            "--requested-at",
            "2026-11-11T00:00:00+00:00",
            "--out",
            str(proposal),
            "--report",
            str(report),
            "--format",
            "json",
        ]
    )
    assert run.returncode == 0, (run.stdout, run.stderr)
    return proposal, json.loads(report.read_bytes())


def _forbidden_pair(constraint):
    return (
        constraint["antecedent"][1]["bind"]["area"],
        constraint["consequent"]["absence"]["bind"]["area"],
    )


def test_joined_discovery_counts_directed_pairs_and_marks_counterexamples(tmp_path):
    model, population = _population(tmp_path)
    proposal, result = _discover(tmp_path, model, population, *SELECTORS)
    forbidden = {_forbidden_pair(row["constraint"]): row["support"] for row in result["emitted"]}
    assert forbidden == {("app", "core"): EXPECTED["unmarked"]["forbidden_app_core"]}
    misses = {}
    for row in result["near_misses"]:
        constraint = row["constraint"]
        key = "forbidden_core_app" if "absence" in constraint["consequent"] else "same_class"
        if key == "forbidden_core_app":
            assert _forbidden_pair(constraint) == ("core", "app")
        misses[key] = {name: row[name] for name in ("subjects", "violations", "counterexamples")}
    assert misses == {k: v for k, v in EXPECTED["unmarked"].items() if k != "forbidden_app_core"}
    assert result["joined_rules"]["reason"] is None
    preview = run_main(
        ["evolve", "preview", str(model), str(proposal), "--workspace", str(tmp_path)]
    )
    assert preview.returncode == 0, (preview.stdout, preview.stderr)


def test_joined_discovery_marker_and_separate_directed_cap(tmp_path):
    model, population = _population(tmp_path)
    _, result = _discover(
        tmp_path,
        model,
        population,
        *SELECTORS,
        "--max-pairs",
        "0",
        "--max-directed-pairs",
        "1",
        "--joined-marker",
        f'{MARKER}:component:owner="private"',
    )
    joined = result["joined_rules"]
    assert {key: joined[key] for key in EXPECTED["directed_cap_1"]} == EXPECTED["directed_cap_1"]
    assert result["bounds"]["max_pairs"] == 0
    assert len(result["emitted"]) == 1
    row = result["emitted"][0]
    assert row["support"] == EXPECTED["marked"]["same_class"]
    assert row["constraint"]["antecedent"][-1]["fact_type"] == MARKER
