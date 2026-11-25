"""SI1: authenticated seeded projections and standalone refusals."""

import hashlib
import json
import time
from pathlib import Path

import pytest
import vg3_cases
from support.cli_runner import run_main
from test_vg5_seeded_growth_example import _copy, _round

from gnd.errors import ModelValidationError, ValidationIssue
from gnd.model import load_model
from gnd.model.flattening import flatten_model

FLATTENING_ROUTES = ("flatten", "extract", "pyrel", "duckdb", "lqp")
MODEL_ROUTES = ("validate", "check", *FLATTENING_ROUTES)


def _run(route: str, model: Path, out: Path, population: Path | None = None):
    if route == "validate":
        args = ["validate", str(model)]
    elif route == "check":
        args = ["check", str(model), str(population)]
    elif route in ("flatten", "extract"):
        args = [route, str(model), "--out", str(out)]
    else:
        args = ["export", "pyrel", str(model), "--out", str(out.with_suffix(".py"))]
        if route != "pyrel":
            args += ["--rules", route]
    result = run_main(args)
    combined = (result.stdout + result.stderr).decode()
    assert "Traceback" not in combined, combined
    return result.returncode, combined


@pytest.fixture(scope="module", params=("packaged", "grown"))
def example(request, tmp_path_factory):
    work = _copy(tmp_path_factory.mktemp("si1-example"))
    population = work / "population.json"
    if request.param == "grown":
        for round_number in (1, 2):
            assert _round(work, round_number) == (0, 0)
    else:
        seed_population = json.loads(population.read_bytes())
        seed_population["facts"].pop("author_writes_work")
        seed_population["instances"].pop("author")
        seed_population["population"]["covers"].remove("author_writes_work")
        population.write_text(json.dumps(seed_population))
    return work / "root.orm.yaml", population


@pytest.mark.parametrize("route", MODEL_ROUTES)
def test_seeded_root_and_standalone_route_matrix(example, route, tmp_path):
    root, population = example
    code, output = _run(route, root, tmp_path / "accepted", population)
    assert code == 0, output

    destination = tmp_path / "projection"
    code, output = _run("flatten", root, destination)
    assert code == 0, output
    (flat,) = destination.glob("*.flat.orm.json")
    renamed = tmp_path / "standalone.yaml"
    renamed.write_bytes(flat.read_bytes())
    for index, model in enumerate((flat, renamed)):
        code, output = _run(route, model, tmp_path / f"refused-{index}", population)
        assert code == 3, output
        assert "unattended:flat-without-root" in output
        assert "load the root that declares the reviewed includes" in output


@pytest.mark.parametrize("route", FLATTENING_ROUTES)
def test_reentry_validation_refusal_reports_rule_and_writes_nothing(example, route, tmp_path, monkeypatch):
    from gnd.model import flattening

    def refuse(data, root):
        raise ModelValidationError([ValidationIssue(path="$", rule_id="test:re-entry", message="probe")])

    monkeypatch.setattr(flattening, "_load_projection", refuse)
    destination = tmp_path / "projection"
    code, output = _run(route, example[0], destination)
    assert code == 3
    assert "flattening:re-entry" in output and "test:re-entry" in output
    assert not destination.exists() and not destination.with_suffix(".py").exists()


@pytest.fixture
def two_seed_root(tmp_path):
    seed = vg3_cases.seed()
    fact = seed["fact_types"][0]
    fact["sample_population"] = [{"work": "w", "version": "v"}]
    fact["constraints"].append({
        "type": "mandatory", "role": "work", "source": "llm-inferred", "status": "confirmed",
        "modality": "alethic", "rationale": "Reviewed",
        "provenance": {"rationale_world_fact": "A version is of a work."},
    })
    own = {"id": "author", "kind": "value", "primitive": "String",
           "provenance": {"spans": [vg3_cases.span("An author writes works")]}}
    root = vg3_cases.write(tmp_path.resolve(), seed_doc=seed, object_types=[own])
    second = root.parent / "language.orm.json"
    second.write_text(json.dumps({
        "version": 4, "object_types": [{"id": "language", "kind": "value", "primitive": "String"}],
        "fact_types": [],
    }))
    doc = json.loads(root.read_bytes())
    doc["includes"].append({"id": "linguistic", "path": second.name,
                            "sha256": hashlib.sha256(second.read_bytes()).hexdigest()})
    root.write_text(json.dumps(doc))
    return root


@pytest.mark.parametrize("route", MODEL_ROUTES)
def test_two_seeds_keep_exemptions_and_validate_owned_elements(two_seed_root, route, tmp_path):
    root = two_seed_root
    population = tmp_path / "population.json"
    population.write_text(json.dumps({
        "population": {"model": root.name, "model_id": "urn:example:growth", "source": "fixture",
                       "covers": ["work_has_version"]},
        "facts": {"work_has_version": [{"work": "w", "version": "v"}]},
    }))
    code, output = _run(route, root, tmp_path / "accepted", population)
    assert code == 0, output
    flat = flatten_model(load_model(root))
    doc = json.loads(root.read_bytes())
    forged_origins = [{"origin": "includes[seed]", "composed_address": "$.object_types[0]"}]
    doc["object_types"][0].pop("provenance")
    doc["source"]["origins"] = forged_origins
    root.write_text(json.dumps(doc))
    code, output = _run(route, root, tmp_path / "refused-root", population)
    assert code == 3 and "semantic:unattended-u4" in output
    assert "object_types[id=author]" in output and "object_types[id=language]" not in output

    doc = json.loads(flat.model_bytes)
    doc["source"]["origins"] = forged_origins
    next(row for row in doc["object_types"] if row["id"] == "author").pop("provenance")
    standalone = tmp_path / "pretend-flat.json"
    standalone.write_text(json.dumps(doc))
    code, output = _run(route, standalone, tmp_path / "refused-flat", population)
    assert code == 3 and "semantic:unattended-u4" in output
    assert "object_types[id=author]" in output
    assert "semantic:unattended-u6" in output and "semantic:unattended-u8" in output


def test_projection_validation_of_large_seed_is_bounded(tmp_path):
    seed = vg3_cases.seed()
    seed["object_types"].extend({"id": f"value_{i}", "kind": "value", "primitive": "String"}
                                for i in range(2000))
    fact = seed["fact_types"][0]
    constraint = fact["constraints"][0]
    seed["fact_types"].extend({**fact, "id": f"fact_{i}", "constraints": [{**constraint, "id": f"unique_{i}"}]}
                              for i in range(1000))
    loaded = load_model(vg3_cases.write(tmp_path.resolve(), seed_doc=seed))
    start = time.monotonic()
    model = flatten_model(loaded).model
    assert len(model.object_types) == 2002
    assert sum(len(fact["constraints"]) for fact in model.fact_types) == 1001
    assert time.monotonic() - start < 10


def test_representation_format_lists_rooted_witness_and_replay():
    page = Path(__file__).resolve().parents[1] / (
        "src/gnd/skills/gnd-orm-core/references/representation-format.md"
    )
    section = page.read_text().split("### Extraction flattening record\n", 1)[1]
    paragraph = section.split("The flat model is canonical JSON.", 1)[1].split("\n\n", 1)[0]
    assert "rooted witness and replay" in paragraph


def test_witness_and_verifier_rederive_seeded_projection(example, tmp_path):
    from gnd.extract.service import _verify_artifact_index

    root, population = example
    bundle = tmp_path / "artifacts"
    assert _run("extract", root, bundle)[0] == 0
    _verify_artifact_index(str(root), str(bundle), ())
    (flat,) = bundle.glob("*.flat.orm.json")
    (record,) = bundle.glob("*.flattening.json")
    targets = tmp_path / "targets.json"
    targets.write_text(json.dumps({"version": 1, "targets": [{
        "fact_type": "work_has_version",
        "tuple": [{"primitive": "String", "value": value} for value in ("W-1", "V-1")],
    }]}))
    certificate = tmp_path / "certificate.json"
    common = [str(root), str(population), "--raw", "--flat-model", str(flat),
              "--flattening-record", str(record)]
    result = run_main(["witness", *common, "--targets", str(targets), "--out", str(certificate)])
    assert result.returncode == 0, result.stdout + result.stderr
    replay = run_main(["replay", *common, str(certificate)])
    assert replay.returncode == 0, replay.stdout + replay.stderr
