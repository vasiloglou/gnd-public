import hashlib
from dataclasses import replace
from pathlib import Path

from gnd.api import check
from gnd.extract.anchors import read_anchor_sidecar, recognised_ranges

FIXTURE = Path(__file__).parent / "fixtures/v70-phase1"

def test_date_suffix_does_not_pass_a_bound_anchor():
    raw = (FIXTURE / "document.txt").read_bytes().replace(b"2024-02-29,", b"2024-02-29-", 1)
    sidecar = replace(
        read_anchor_sidecar(FIXTURE / "population.pop.json.anchors.json"),
        document_sha256=hashlib.sha256(raw).hexdigest(),
    )
    result = check(
        FIXTURE / "model.orm.yaml",
        FIXTURE / "population.pop.json",
        anchors=sidecar,
        document=raw,
    )
    assert result["exit_code"] == 1
    date_row = next(row for row in result["verdicts"] if row["constraint_ref"].startswith("fact_types[date_has_value]"))
    assert date_row["verdict"] == "fail"

def test_timezone_form_does_not_pass_a_bound_date_anchor():
    raw = (FIXTURE / "document.txt").read_bytes().replace(
        b"2024-02-29, a le", b"2024-02-29+01:00", 1,
    )
    sidecar = replace(
        read_anchor_sidecar(FIXTURE / "population.pop.json.anchors.json"),
        document_sha256=hashlib.sha256(raw).hexdigest(),
    )
    result = check(FIXTURE / "model.orm.yaml", FIXTURE / "population.pop.json",
                   anchors=sidecar, document=raw)
    assert result["exit_code"] == 1

def test_repeated_value_reuses_recogniser_occurrence_lookup(tmp_path):
    import json
    from unittest.mock import patch

    from ruamel.yaml import YAML

    from gnd.extract.anchors import vocabulary_digest

    model = YAML(typ="safe").load((FIXTURE / "model.orm.yaml").read_text())
    model["fact_types"] = [fact for fact in model["fact_types"] if fact["id"] == "invoice_has_quantity"]
    model_path = tmp_path / "model.orm.yaml"
    with model_path.open("w") as stream:
        YAML().dump(model, stream)
    population = json.loads((FIXTURE / "population.pop.json").read_text())
    population["population"]["covers"] = ["invoice_has_quantity"]
    population["facts"] = {"invoice_has_quantity": [
        {"invoice": "I-7", "quantity": 1234},
        {"invoice": "I-8", "quantity": 1234},
    ]}
    population_path = tmp_path / "population.pop.json"
    population_path.write_text(json.dumps(population) + "\n")
    source_path = tmp_path / "document.txt"
    source_path.write_bytes((FIXTURE / "document.txt").read_bytes())
    anchors = json.loads((FIXTURE / "population.pop.json.anchors.json").read_text())
    original = next(row for row in anchors["anchors"] if row["fact_key"]["fact_type"] == "invoice_has_quantity")
    other = json.loads(json.dumps(original))
    other["fact_key"]["roles"]["invoice"] = "I-8"
    anchors["anchors"] = [original, other]
    anchors["population_sha256"] = hashlib.sha256(population_path.read_bytes()).hexdigest()
    anchors["vocabulary_digest"] = vocabulary_digest(model)
    anchor_path = tmp_path / "population.pop.json.anchors.json"
    anchor_path.write_text(json.dumps(anchors))
    with patch("gnd.extract.anchors.recognised_ranges", wraps=recognised_ranges) as lookup:
        result = check(model_path, population_path, anchors=anchor_path, document=source_path)
    assert result["exit_code"] == 0
    assert lookup.call_count == 1

def test_absent_sidecar_precedes_empty_subject_vacuity():
    import json

    from gnd.model import load_model
    from gnd.population import load_population_bytes

    model = load_model(FIXTURE / "model.orm.yaml")
    document = json.loads((FIXTURE / "population.pop.json").read_text())
    document["facts"] = {name: [] for name in document["facts"]}
    population = load_population_bytes(
        (json.dumps(document) + "\n").encode(),
        source=FIXTURE / "population.pop.json",
        model=model,
    )
    result = check(model, population)
    assert result["exit_code"] == 4
    assert {row["verdict"] for row in result["verdicts"]} == {"unchecked"}
    assert {row["reason_code"] for row in result["verdicts"]} == {"anchor-sidecar-absent"}

def test_all_role_deontic_violation_has_its_own_scoped_warning(tmp_path):
    import json

    from ruamel.yaml import YAML

    from gnd.extract.anchors import vocabulary_digest

    model = YAML(typ="safe").load((FIXTURE / "model.orm.yaml").read_text())
    model["fact_types"] = [fact for fact in model["fact_types"] if fact["id"] == "pair_has_names"]
    model["fact_types"][0]["constraints"][0]["modality"] = "deontic"
    model_path = tmp_path / "model.orm.yaml"
    with model_path.open("w") as stream:
        YAML().dump(model, stream)
    population = json.loads((FIXTURE / "population.pop.json").read_text())
    population["population"]["covers"] = ["pair_has_names"]
    population["facts"] = {"pair_has_names": [{"left": "Absent", "right": "Right"}]}
    population_path = tmp_path / "population.pop.json"
    population_path.write_text(json.dumps(population) + "\n")
    source_path = tmp_path / "document.txt"
    source_path.write_bytes((FIXTURE / "document.txt").read_bytes())
    sidecar = json.loads((FIXTURE / "population.pop.json.anchors.json").read_text())
    sidecar["anchors"] = [anchor for anchor in sidecar["anchors"] if anchor["fact_key"]["fact_type"] == "pair_has_names"]
    for anchor in sidecar["anchors"]:
        anchor["fact_key"]["roles"]["left"] = "Absent"
    sidecar["population_sha256"] = hashlib.sha256(population_path.read_bytes()).hexdigest()
    sidecar["vocabulary_digest"] = vocabulary_digest(model)
    sidecar_path = tmp_path / "population.pop.json.anchors.json"
    sidecar_path.write_text(json.dumps(sidecar))
    result = check(model_path, population_path, anchors=sidecar_path, document=source_path)
    assert result["exit_code"] == 0
    assert [(row["constraint_ref"], row["verdict"], row["reason_code"]) for row in result["verdicts"]] == [
        ("fact_types[pair_has_names].constraints[0]", "warning", None),
    ]


from ruamel.yaml import YAML


def test_population_is_valid_under_existing_non_anchor_rules(tmp_path):
    """Remove only future constraints; the base population must already load."""
    from gnd.model import load_model
    from gnd.population import load_population

    model = YAML(typ="safe").load((FIXTURE / "model.orm.yaml").read_text())
    for fact in model["fact_types"]:
        fact.pop("constraints", None)
    model_path = tmp_path / "model.orm.yaml"
    with model_path.open("w") as stream:
        YAML().dump(model, stream)
    loaded = load_model(model_path)
    population = load_population(FIXTURE / "population.pop.json", model=loaded)
    assert len(population.facts) == 7
