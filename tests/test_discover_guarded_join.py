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
    assert result["rejected"]["warning"] == 4
    preview = run_main(
        [
            "evolve",
            "preview",
            str(model),
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


def test_joined_discovery_refuses_missing_ambiguous_and_uncovered_inputs(tmp_path):
    for option, reason in (
        ("missing", "missing-classification"),
        ("ambiguous", "ambiguous-classification"),
        ("uncovered", "uncovered-fact-type"),
    ):
        folder = tmp_path / option
        folder.mkdir()
        model, population = _population(folder, **{option: True})
        proposal, report = _discover(folder, model, population, *SELECTORS)
        assert report["joined_rules"]["reason"] == reason
        assert report["emitted"] == report["near_misses"] == []
        assert not proposal.exists()


def test_joined_work_limit_preserves_other_families(tmp_path, monkeypatch):
    from gnd.discover import joined

    model, population = _population(tmp_path)
    monkeypatch.setattr(joined, "MAX_WORK", 55)
    flags = [*SELECTORS]
    flags[1] += ",uniqueness"
    _, report = _discover(tmp_path, model, population, *flags)
    family = report["joined_rules"]
    assert family["reason"] == "work-limit"
    assert family["compared"] == 2 and family["first_omitted_ordinal"] == 2
    assert family["work"]["visits"] <= family["work"]["ceiling"] == 55
    assert report["bounds"]["families"] == ["uniqueness", "guarded-join"]
    assert all(row["family"] == "uniqueness" for row in report["emitted"])
    assert report["work"]["uniqueness"] > 0


def test_joined_discovery_declared_rule_is_suppressed(tmp_path):
    import shutil

    from ruamel.yaml import YAML

    first, second = tmp_path / "first", tmp_path / "second"
    first.mkdir()
    second.mkdir()
    model, population = _population(first)
    _, initial = _discover(first, model, population, *SELECTORS)
    document = YAML(typ="safe").load(model)
    declared = initial["emitted"][0]["constraint"]
    declared["id"] = "authored_guard"
    names = {"$a": "$source", "$b": "$target"}
    declared["antecedent"].reverse()
    for atom in [*declared["antecedent"], declared["consequent"]["absence"]]:
        atom["bind"] = {role: names.get(term, term) for role, term in atom["bind"].items()}
    document["constraints"].append(declared)
    existing = second / model.name
    with existing.open("w", encoding="utf-8") as stream:
        YAML(typ="safe").dump(document, stream)
    copied = second / population.name
    shutil.copyfile(population, copied)
    proposal, report = _discover(second, existing, copied, *SELECTORS)
    assert report["suppressed"]["declared"] == 1
    assert report["emitted"] == []
    assert not proposal.exists()


def test_unmarked_same_class_is_admitted_for_all_inside_edges(tmp_path):
    model, population = _population(tmp_path)
    document = json.loads(population.read_bytes())
    del document["facts"][RELATION][20]
    population.write_text(json.dumps(document), encoding="utf-8")
    _, report = _discover(tmp_path, model, population, *SELECTORS)
    same = [row for row in report["emitted"] if "atom" in row["constraint"]["consequent"]]
    assert len(same) == 1
    assert same[0]["support"] == {"numerator": 21, "denominator": 21}
    assert same[0]["constraint"]["id"].startswith("gj_")


def test_bad_joined_marker_is_a_usage_error_before_input_reads(tmp_path):
    result = run_main(
        [
            "discover",
            "missing.model",
            "missing.population",
            *SELECTORS,
            "--joined-marker",
            f'{MARKER}:component:owner="$variable"',
            "--actor",
            "ga2-test",
            "--requested-at",
            "2026-11-11T00:00:00Z",
            "--out",
            str(tmp_path / "proposal.json"),
            "--report",
            str(tmp_path / "report.json"),
        ]
    )
    assert result.returncode == 64
    assert b"reserved dollar" in result.stderr
    assert list(tmp_path.iterdir()) == []


def test_joined_service_rejects_family_and_settings_mismatches(tmp_path):
    import pytest

    from gnd.discover import joined, service

    model, population = _population(tmp_path)
    settings = joined.configure(SELECTORS[3], SELECTORS[5], None, None)
    for families, config in [(("value",), settings), ((joined.FAMILY,), None)]:
        with pytest.raises(ValueError, match="guarded-join"):
            service.discover(
                model,
                population,
                families=families,
                max_values=20,
                max_pairs=256,
                joined_settings=config,
            )


def test_joined_discovery_rejects_checker_witness_disagreement(tmp_path, monkeypatch):
    import pytest

    from gnd.discover import joined, service

    model, population = _population(tmp_path)
    settings = joined.configure(SELECTORS[3], SELECTORS[5], None, None)
    original = service.check

    def wrong_witness(*args, **kwargs):
        report = original(*args, **kwargs)
        warning = next(
            row
            for row in report.verdicts
            if row.binding_count == 21 and len(row.offending_facts) == 1
        )
        warning.offending_facts = [{**warning.offending_facts[0], "$b": "core0"}]
        return report

    monkeypatch.setattr(service, "check", wrong_witness)
    with pytest.raises(service.DiscoveryDefect, match="disagrees"):
        service.discover(
            model,
            population,
            families=(joined.FAMILY,),
            max_values=20,
            max_pairs=256,
            joined_settings=settings,
        )
