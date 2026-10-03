import hashlib
import json
import subprocess
import sys
from pathlib import Path

from gnd.api import check
from gnd.extract.anchors import read_anchor_sidecar, vocabulary_digest, write_anchor_sidecar
from gnd.extract.bundle import header_template
from gnd.model import load_model
from gnd.population import load_population

FIXTURE = Path(__file__).parent / "fixtures/v70-phase1"

MODEL = FIXTURE / "model.orm.yaml"

POPULATION = FIXTURE / "population.pop.json"

DOCUMENT = FIXTURE / "document.txt"

SIDECAR = FIXTURE / "population.pop.json.anchors.json"

def test_api_paths_and_exact_in_memory_bytes_agree():
    path_report = check(MODEL, POPULATION, anchors=SIDECAR, document=DOCUMENT)
    model = load_model(MODEL)
    population = load_population(POPULATION, model=model)
    typed = read_anchor_sidecar(SIDECAR)
    memory_report = check(model, population, anchors=typed,
                          document=DOCUMENT.read_bytes(), population_bytes=POPULATION.read_bytes())
    assert path_report["exit_code"] == memory_report["exit_code"] == 0
    assert [row["verdict"] for row in path_report["verdicts"]] == ["pass"] * 7
    assert [row["verdict"] for row in memory_report["verdicts"]] == ["pass"] * 7

def test_typed_sidecar_without_original_population_bytes_refuses():
    model = load_model(MODEL)
    population = load_population(POPULATION, model=model)
    report = check(model, population, anchors=read_anchor_sidecar(SIDECAR), document=DOCUMENT.read_bytes())
    assert report["exit_code"] == 3
    assert "anchor:binding-mismatch" in json.dumps(report)

def test_writer_publishes_adjacent_sidecar_atomically(tmp_path):
    copy = tmp_path / "population.json"
    copy.write_bytes(POPULATION.read_bytes())
    typed = read_anchor_sidecar(SIDECAR)
    destination = write_anchor_sidecar(typed, copy)
    assert destination == Path(str(copy) + ".anchors.json")
    assert read_anchor_sidecar(destination) == typed

def test_verify_without_extraction_retains_anchor_uncertainty():
    run = subprocess.run([sys.executable, "-m", "gnd", "verify", str(MODEL),
                          str(POPULATION), "--no-extraction", "--format", "json"],
                         capture_output=True, text=True, check=False)
    assert run.returncode == 3
    payload = json.loads(run.stdout)
    assert "anchor:binding-mismatch" in json.dumps(payload)
    assert payload["acceptance_ready"] is False

def test_verify_without_adjacent_anchor_is_unchecked(tmp_path):
    model_path = tmp_path / "model.orm.yaml"
    population_path = tmp_path / "population.pop.json"
    model_path.write_bytes(MODEL.read_bytes())
    population_path.write_bytes(POPULATION.read_bytes())
    run = subprocess.run(
        [sys.executable, "-m", "gnd", "verify", str(model_path), str(population_path),
         "--no-extraction", "--format", "json"],
        capture_output=True, text=True, check=False,
    )
    assert run.returncode == 4, run.stdout + run.stderr
    assert {row["reason_code"] for row in json.loads(run.stdout)["verdicts"]} == {"anchor-sidecar-absent"}

def _verified_anchor_bundle(tmp_path, *, anchor_document=None):
    model_path = tmp_path / "model.orm.yaml"
    model_path.write_bytes(MODEL.read_bytes())
    document_path = tmp_path / "document.txt"
    document_path.write_bytes(DOCUMENT.read_bytes())
    population_path = tmp_path / "population.pop.json"
    population = json.loads(POPULATION.read_text())
    population["population"] = header_template(str(model_path), load_model(model_path))
    population_path.write_text(json.dumps(population, ensure_ascii=False) + "\n")
    anchors = json.loads(SIDECAR.read_text())
    anchors["population_sha256"] = hashlib.sha256(population_path.read_bytes()).hexdigest()
    if anchor_document is not None:
        anchors["document_sha256"] = hashlib.sha256(anchor_document).hexdigest()
    (tmp_path / "population.pop.json.anchors.json").write_text(json.dumps(anchors))
    artifacts = tmp_path / "artifacts"
    extracted = subprocess.run([sys.executable, "-m", "gnd", "extract", str(model_path),
                                "--out", str(artifacts)], capture_output=True, text=True, check=False)
    assert extracted.returncode == 0, extracted.stderr
    projection = artifacts / "model.projection.schema.json"
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = {
        "schema_version": 1,
        "population": population_path.name,
        "population_sha256": digest(population_path),
        "model": model_path.name,
        "model_sha256": digest(model_path),
        "projection_sha256": digest(projection),
        "document": document_path.name,
        "document_sha256": digest(document_path),
        "skill": "gnd-extract",
        "skill_version": "1",
        "executing_model": "test-fixture",
    }
    population_path.with_suffix(".extraction.json").write_text(json.dumps(manifest))
    return model_path, population_path, document_path, artifacts

def test_verify_uses_adjacent_anchor_with_extraction_document(tmp_path):
    model_path, population_path, _document_path, artifacts = _verified_anchor_bundle(tmp_path)
    checked = subprocess.run([sys.executable, "-m", "gnd", "verify", str(model_path),
                              str(population_path), "--artifacts", str(artifacts), "--format", "json"],
                             capture_output=True, text=True, check=False)
    assert checked.returncode == 0, checked.stdout + checked.stderr
    payload = json.loads(checked.stdout)
    assert payload["extraction"]["state"] == "ran"
    assert [row["verdict"] for row in payload["verdicts"]] == ["pass"] * 7

def test_verify_rejects_document_changed_between_extraction_and_anchor_reads(tmp_path, monkeypatch, capsys):
    from contextlib import contextmanager

    from gnd.cli import main
    from gnd.extract import manifest as manifest_module

    changed_document = DOCUMENT.read_bytes() + b"\n"
    model_path, population_path, document_path, artifacts = _verified_anchor_bundle(
        tmp_path, anchor_document=changed_document,
    )
    original_open = manifest_module.open_manifest_relative_path
    swapped = False

    @contextmanager
    def swap_after_verified_document(*args, **kwargs):
        nonlocal swapped
        with original_open(*args, **kwargs) as opened:
            yield opened
        if kwargs.get("field") == "document" and not swapped:
            document_path.write_bytes(changed_document)
            swapped = True

    monkeypatch.setattr(manifest_module, "open_manifest_relative_path", swap_after_verified_document)
    code = main(["verify", str(model_path), str(population_path), "--artifacts", str(artifacts),
                 "--format", "json"])
    payload = json.loads(capsys.readouterr().out)
    assert swapped
    assert code == 3
    assert payload["extraction"]["state"] == "ran"
    assert "anchor:binding-mismatch" in json.dumps(payload)

def test_existing_snapshot_without_anchors_does_not_infer_source_witness():
    report = check(MODEL, POPULATION)
    assert report["exit_code"] == 4
    assert {row["reason_code"] for row in report["verdicts"]} == {"anchor-sidecar-absent"}

def test_failed_anchor_redacts_sensitive_role_value(tmp_path):
    from ruamel.yaml import YAML

    model = YAML(typ="safe").load(MODEL.read_text())
    model["fact_types"] = [model["fact_types"][0]]
    model["fact_types"][0]["roles"][1]["redact"] = True
    model_path = tmp_path / "model.orm.yaml"
    with model_path.open("w") as stream:
        YAML().dump(model, stream)
    population = json.loads(POPULATION.read_text())
    population["population"]["covers"] = ["record_has_label"]
    population["facts"] = {"record_has_label": [{"record": "R-1", "label": "SECRET-LEAK"}]}
    population_path = tmp_path / "population.pop.json"
    population_path.write_text(json.dumps(population) + "\n")
    document_path = tmp_path / "document.txt"
    document_path.write_bytes(DOCUMENT.read_bytes())
    anchors = json.loads(SIDECAR.read_text())
    anchors["anchors"] = [anchors["anchors"][0]]
    anchors["anchors"][0]["fact_key"]["roles"]["label"] = "SECRET-LEAK"
    anchors["population_sha256"] = hashlib.sha256(population_path.read_bytes()).hexdigest()
    anchors["vocabulary_digest"] = vocabulary_digest(model)
    anchor_path = tmp_path / "population.pop.json.anchors.json"
    anchor_path.write_text(json.dumps(anchors))
    applied = check(model_path, population_path, anchors=anchor_path, document=document_path)
    raw = check(model_path, population_path, anchors=anchor_path, document=document_path,
                unredacted=True)
    assert applied["exit_code"] == raw["exit_code"] == 1
    assert "SECRET-LEAK" not in json.dumps(applied)
    assert "SECRET-LEAK" in json.dumps(raw)
