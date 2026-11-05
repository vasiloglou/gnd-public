"""CT3: witness version 2 names each base fact's source facts in a composition."""

import copy
import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest
import test_composition as tc

from gnd import api

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "src/gnd/schema/witness.schema.json").read_text())
DERIVED = """  - id: contract_is_in_city
    reading: "{Contract} is in {City}"
    roles: [{object_type: contract, role_name: contract}, {object_type: city, role_name: city}]
    derivation: derived
    derivation_rule:
      body:
        - {fact_type: contract_has_party, bind: {contract: "$c", party: "$p"}}
        - {fact_type: party_is_based_in_city, bind: {party: "$p", city: "$x"}}
      head: {contract: "$c", city: "$x"}
constraints: []
"""


def _sources():
    # A's contract names the party; only B says where the party is based.
    sources = copy.deepcopy(tc.SOURCES)
    del sources["contract-a"]["facts"]["party_is_based_in_city"]
    return sources


def composed(tmp_path, monkeypatch):
    monkeypatch.setattr(tc, "MODEL", tc.MODEL.replace("constraints: []\n", DERIVED, 1))
    model_path, directory, out, record, run = tc.composed(tmp_path, sources=_sources())
    assert run.returncode == 0, run.stderr
    targets = tmp_path / "targets.json"
    targets.write_text(json.dumps({"version": 1, "targets": [{"fact_type": "contract_is_in_city", "tuple": [
        {"primitive": "String", "value": "C-1"}, {"primitive": "String", "value": "Lyon"}]}]}))
    return model_path, directory, out, record, targets


def gnd(*argv, env=None):
    return subprocess.run([sys.executable, "-m", "gnd", *map(str, argv)], capture_output=True, text=True,
                          check=False, env={**os.environ, **(env or {})})


def produce(tmp_path, monkeypatch):
    model_path, directory, out, record, targets = composed(tmp_path, monkeypatch)
    certificate = tmp_path / "witness.json"
    run = gnd("witness", model_path, out, "--targets", targets, "--composition", record, "--raw", "--out", certificate)
    assert run.returncode == 0, run.stdout + run.stderr
    return model_path, directory, out, record, targets, certificate


# T2, T3, T5
def test_a_composed_witness_traces_each_premise_to_its_source(tmp_path, monkeypatch):
    _model_path, directory, _out, record, _targets, certificate = produce(tmp_path, monkeypatch)
    witness = json.loads(certificate.read_text())
    jsonschema.validate(witness, SCHEMA)
    assert witness["version"] == 2
    assert witness["binding"]["composition_sha256"] == tc._sha(record.read_bytes())
    bases = {node["fact_type"]: node["sources"] for node in witness["nodes"] if node["kind"] == "base"}
    assert bases["contract_has_party"] == [{"source": "contract-a", "fact_type": "contract_has_party", "fact_index": 0}]
    assert bases["party_is_based_in_city"] == [{"source": "contract-b", "fact_type": "party_is_based_in_city", "fact_index": 0}]
    # Following a source fact to its own sidecar gives a span in its own document.
    entry = bases["contract_has_party"][0]
    folder = directory / entry["source"]
    sidecar = json.loads((folder / "population.json.anchors.json").read_text())
    row = json.loads((folder / "population.json").read_text())["facts"][entry["fact_type"]][entry["fact_index"]]
    anchor = next(a for a in sidecar["anchors"] if a["fact_key"]["roles"] == row)
    text = (folder / "document.txt").read_text()
    assert text[anchor["span"]["start"]:anchor["span"]["end"]] == "Acme Corp."


def test_a_deduplicated_premise_lists_both_source_facts(tmp_path, monkeypatch):
    monkeypatch.setattr(tc, "MODEL", tc.MODEL.replace("constraints: []\n", DERIVED, 1))
    model_path, _directory, out, record, _run = tc.composed(tmp_path)
    targets = tmp_path / "targets.json"
    targets.write_text(json.dumps({"version": 1, "targets": [{"fact_type": "contract_is_in_city", "tuple": [
        {"primitive": "String", "value": "C-2"}, {"primitive": "String", "value": "Lyon"}]}]}))
    certificate = tmp_path / "witness.json"
    produced = gnd("witness", model_path, out, "--targets", targets, "--composition", record, "--raw", "--out", certificate)
    assert produced.returncode == 0, produced.stdout
    city = next(n for n in json.loads(certificate.read_text())["nodes"] if n.get("fact_type") == "party_is_based_in_city")
    assert [s["source"] for s in city["sources"]] == ["contract-a", "contract-b"]


def test_schema_ties_the_new_fields_to_version_2(tmp_path, monkeypatch):
    *_, certificate = produce(tmp_path, monkeypatch)
    witness = json.loads(certificate.read_text())
    without_digest = copy.deepcopy(witness)
    del without_digest["binding"]["composition_sha256"]
    without_sources = copy.deepcopy(witness)
    del next(n for n in without_sources["nodes"] if n["kind"] == "base")["sources"]
    as_version_1 = dict(copy.deepcopy(witness), version=1)
    for bad in (without_digest, without_sources, as_version_1):
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(bad, SCHEMA)


# T4
def _replay(model_path, out, certificate, *extra):
    run = gnd("replay", model_path, out, certificate, "--raw", "--json", *extra)
    return run.returncode, json.loads(run.stdout)


def test_replay_checks_the_lineage(tmp_path, monkeypatch):
    model_path, _directory, out, record, _targets, certificate = produce(tmp_path, monkeypatch)
    assert _replay(model_path, out, certificate, "--composition", record)[0] == 0
    code, payload = _replay(model_path, out, certificate)
    assert (code, payload["reason"]) == (3, "composition-required")
    witness = json.loads(certificate.read_text())
    edited = copy.deepcopy(witness)
    next(n for n in edited["nodes"] if n["kind"] == "base")["sources"][0]["fact_index"] = 7
    bad = tmp_path / "edited.json"
    bad.write_text(json.dumps(edited))
    code, payload = _replay(model_path, out, bad, "--composition", record)
    assert (code, payload["reason"]) == (1, "proof-invalid")
    stale = copy.deepcopy(witness)
    stale["binding"]["composition_sha256"] = "0" * 64
    bad.write_text(json.dumps(stale))
    code, payload = _replay(model_path, out, bad, "--composition", record)
    assert (code, payload["reason"]) == (3, "binding-stale")
    other = tmp_path / "other-record.json"
    other.write_text(record.read_text().replace('"2024-agreement"', '"other"'))
    code, _ = _replay(model_path, out, certificate, "--composition", other)
    assert code == 3


def test_a_version_1_witness_with_a_composition_is_stale(tmp_path, monkeypatch):
    model_path, _directory, out, record, targets = composed(tmp_path, monkeypatch)
    certificate = tmp_path / "v1.json"
    produced = gnd("witness", model_path, out, "--targets", targets, "--raw", "--out", certificate)
    assert produced.returncode == 0
    assert json.loads(certificate.read_text())["version"] == 1
    assert _replay(model_path, out, certificate)[0] == 0
    code, payload = _replay(model_path, out, certificate, "--composition", record)
    assert (code, payload["reason"]) == (3, "binding-stale")


def test_witness_refuses_a_record_for_other_inputs(tmp_path, monkeypatch):
    model_path, _directory, out, record, targets = composed(tmp_path, monkeypatch)
    edited = tmp_path / "edited.population.json"
    edited.write_bytes(out.read_bytes() + b"\n")
    run = gnd("witness", model_path, edited, "--targets", targets, "--composition", record, "--raw")
    assert run.returncode == 3


def test_composition_excludes_reference_root(tmp_path, monkeypatch):
    model_path, _directory, out, record, targets = composed(tmp_path, monkeypatch)
    run = gnd("witness", model_path, out, "--targets", targets, "--composition", record, "--reference-root", tmp_path)
    assert run.returncode == 64


# T6
def test_views_show_sources_and_no_value(tmp_path, monkeypatch):
    model_path, _directory, out, record, targets, certificate = produce(tmp_path, monkeypatch)
    view = gnd("witness-view", certificate, "--json")
    payload = json.loads(view.stdout)
    bases = [n for n in payload["nodes"] if n["kind"] == "base"]
    assert all(n["sources"] for n in bases)
    for value in ("Acme", "Lyon", "C-1"):
        assert value not in view.stdout
    customer = gnd("witness", model_path, out, "--targets", targets, "--composition", record,
                   env={"GND_DISCLOSURE": "customer"})
    assert customer.returncode == 0
    for value in ("Acme", "Lyon", "C-1"):
        assert value not in customer.stdout


def test_api_witness_and_replay_take_a_composition(tmp_path, monkeypatch):
    model_path, _directory, out, record, targets, certificate = produce(tmp_path, monkeypatch)
    result = api.witness(model_path, out, targets, composition=record)
    assert result["exit_code"] == 0 and result["certificate"]["version"] == 2
    assert api.replay(model_path, out, certificate, composition=record)["exit_code"] == 0
    assert api.replay(model_path, out, certificate)["exit_code"] == 3


# T7
def test_souffle_witness_and_why_not_read_no_certificate(tmp_path, monkeypatch):
    model_path, _directory, out, _record, _targets = composed(tmp_path, monkeypatch)
    copy_path = tmp_path / "plain.population.json"
    copy_path.write_bytes(out.read_bytes())
    for argv in (("why-not", model_path, "{}", "--fact-type", "contract_is_in_city"),):
        runs = [gnd(argv[0], argv[1], population, *argv[3:]) for population in (out, copy_path)]
        assert runs[0].returncode == runs[1].returncode
        assert runs[0].stdout == runs[1].stdout


# CT3 review fixes (F1, F2, F4, F6)
def test_unreadable_or_incomplete_records_are_input_refusals(tmp_path, monkeypatch):
    model_path, _directory, out, record, targets, certificate = produce(tmp_path, monkeypatch)
    missing = tmp_path / "missing.json"
    for argv in (("witness", model_path, out, "--targets", targets, "--composition", missing, "--raw"),
                 ("replay", model_path, out, certificate, "--composition", missing, "--raw", "--json")):
        run = gnd(*argv)
        assert run.returncode == 3, run.stdout + run.stderr
        assert "Traceback" not in run.stderr
    assert api.replay(model_path, out, certificate, composition=missing)["exit_code"] == 3
    trimmed = json.loads(record.read_text())
    trimmed["facts"] = [f for f in trimmed["facts"] if f["fact_type"] != "party_is_based_in_city"]
    partial = tmp_path / "partial.json"
    partial.write_text(json.dumps(trimmed))
    run = gnd("witness", model_path, out, "--targets", targets, "--composition", partial, "--raw")
    assert run.returncode == 3, run.stdout + run.stderr
    other_model = tmp_path / "other.orm.yaml"
    other_model.write_text(model_path.read_text() + "\n")
    assert gnd("witness", other_model, out, "--targets", targets, "--composition", record, "--raw").returncode == 3


def test_replay_checks_every_base_node(tmp_path, monkeypatch):
    model_path, _directory, out, record, _targets, certificate = produce(tmp_path, monkeypatch)
    witness = json.loads(certificate.read_text())
    bases = [n for n in witness["nodes"] if n["kind"] == "base"]
    assert len(bases) == 2
    bases[-1]["sources"][0]["fact_index"] = 5
    bad = tmp_path / "last.json"
    bad.write_text(json.dumps(witness))
    assert _replay(model_path, out, bad, "--composition", record)[0] == 1
    bases[-1]["sources"][0]["fact_index"] = 0.0
    bad.write_text(json.dumps(witness))
    assert _replay(model_path, out, bad, "--composition", record)[0] == 3


def test_expanded_view_keeps_sources(tmp_path, monkeypatch):
    *_, certificate = produce(tmp_path, monkeypatch)
    payload = json.loads(gnd("witness-view", certificate, "--expand", "--json").stdout)

    def walk(nodes):
        for node in nodes:
            yield node
            yield from walk(node["premises"])
    assert all(node["sources"] for node in walk(payload["expanded"]) if node["kind"] == "base")


def test_a_stamped_witness_over_the_byte_ceiling_is_a_work_refusal(tmp_path, monkeypatch):
    from dataclasses import replace

    from gnd.witness import service, types

    model_path, _directory, out, record, targets = composed(tmp_path, monkeypatch)
    plain = service.witness_result(model_path, out, targets)
    lineage = service._composition_lineage(record, model_path, out)
    size = len(json.dumps(plain["certificate"]))
    # Only the stamped certificate's own budget is lowered; the inputs were read already.
    monkeypatch.setattr(types, "DEFAULT_LIMITS", replace(types.DEFAULT_LIMITS, bytes=size + 40))
    result = service._stamp_composition(plain, lineage)
    assert (result["exit_code"], result["reason"]) == (4, "work-limit")


def test_api_signatures_take_composition():
    import inspect

    assert tuple(inspect.signature(api.witness).parameters) == (
        "model_path", "population_path", "targets_path", "reference_root", "composition")
    assert tuple(inspect.signature(api.replay).parameters) == (
        "model_path", "population_path", "certificate_path", "reference_root", "composition")


def test_the_result_envelope_schema_accepts_version_2(tmp_path, monkeypatch):
    # Close review: the result schema embeds the certificate schema; keep them in step.
    result_schema = json.loads((ROOT / "src/gnd/schema/witness-result.schema.json").read_text())
    assert result_schema["$defs"]["certificate"] == {
        key: value for key, value in SCHEMA.items() if key not in ("$schema", "$id", "title", "description", "$defs")}
    assert all(result_schema["$defs"][key] == value for key, value in SCHEMA["$defs"].items())
    model_path, _directory, out, record, targets, _certificate = produce(tmp_path, monkeypatch)
    result = api.witness(model_path, out, targets, composition=record)
    jsonschema.validate(result, result_schema)


def test_a_source_id_outside_the_record_id_form_is_refused(tmp_path, monkeypatch):
    # Close review: a hand-edited source string never reaches a view.
    model_path, _directory, out, record, _targets, certificate = produce(tmp_path, monkeypatch)
    witness = json.loads(certificate.read_text())
    next(node for node in witness["nodes"] if node["kind"] == "base")["sources"][0]["source"] = "Acme Corp. SECRET"
    certificate.write_text(json.dumps(witness))
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(witness, SCHEMA)
    code, payload = _replay(model_path, out, certificate, "--composition", record)
    assert code == 3 and "SECRET" not in json.dumps(payload)
    view = gnd("witness-view", certificate, env={"GND_DISCLOSURE": "customer"})
    assert "SECRET" not in view.stdout
