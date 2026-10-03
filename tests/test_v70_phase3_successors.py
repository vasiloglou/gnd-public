from __future__ import annotations

import copy
import json
import time
import tracemalloc
from pathlib import Path
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator
from ruamel.yaml import YAML
from support.cli_runner import run_gnd_text
from test_v70_phase3_opaque import CASES, FIXTURE, _patch, run_case

from gnd import admission, api, redaction
from gnd.checker import CheckReport, UnvalidatedPopulationError, check
from gnd.coverage import read_evidence_document
from gnd.model import load_model
from gnd.model_verbalization import render_model_verbalization
from gnd.population import MAX_POPULATION_BYTES, PopulationLoadError, load_population
from gnd.report import load_report_schema


def _files(tmp_path: Path, case_id: str | None = None) -> tuple[Path, Path]:
    model = YAML(typ="safe").load((FIXTURE / "model.orm.yaml").read_text())
    population = json.loads((FIXTURE / "population.pop.json").read_text())
    if case_id is not None:
        case = CASES[case_id]
        model = _patch(model, case.get("model_edits", []))
        population = _patch(population, case.get("population_edits", []))
    model_path = tmp_path / "model.orm.yaml"
    population_path = tmp_path / "population.pop.json"
    with model_path.open("w") as stream:
        YAML().dump(model, stream)
    population_path.write_text(json.dumps(population))
    return model_path, population_path

def test_yaml_json_marker_parity(tmp_path: Path) -> None:
    model_path, json_path = _files(tmp_path, "A03-unchecked-transitive-block")
    yaml_path = tmp_path / "population.pop.yaml"
    with yaml_path.open("w") as stream:
        YAML().dump(json.loads(json_path.read_text()), stream)
    json_payload = api.check(model_path, json_path)
    yaml_payload = api.check(model_path, yaml_path)
    assert json_payload["exit_code"] == yaml_payload["exit_code"] == 4
    assert [row["reason_code"] for row in json_payload["verdicts"]] == [
        row["reason_code"] for row in yaml_payload["verdicts"]
    ]

def test_v10_verdict_addresses_come_from_occurrences(tmp_path: Path) -> None:
    payload = run_case("A02-explicit-transitive-block", tmp_path)
    failed = next(row for row in payload["verdicts"] if row["verdict"] == "fail")
    assert failed["offending_facts"] == [
        {"fact_type": "record_has_amount", "index": 0}
    ]
    assert failed["refused_facts"] == []
    assert failed["witnesses"] == [99]
    unchecked = run_case("A03-unchecked-transitive-block", tmp_path)
    refused = next(row for row in unchecked["verdicts"] if row["verdict"] == "unchecked")
    assert refused["offending_facts"] == []
    assert refused["refused_facts"] == [
        {"fact_type": "record_has_amount", "index": 0},
        {"fact_type": "record_has_amount", "index": 1},
    ]

def test_v10_does_not_address_unasserted_derived_tuple(tmp_path: Path) -> None:
    model_path, population_path = _files(tmp_path, "O06-derived-opaque-refusal")
    model = YAML(typ="safe").load(model_path.read_text())
    derived = next(row for row in model["fact_types"] if row["id"] == "holder_is_known")
    derived["derivation"] = "semiderived"
    derived["constraints"] = [{
        "type": "value", "object_type": "record",
        "role_ref": {"fact_type": "holder_is_known", "role": "record"},
        "allowed": ["R2"], "source": "explicit", "status": "confirmed",
        "modality": "alethic", "provenance": {"user_quote": "Only R2 is allowed."},
    }]
    with model_path.open("w") as stream:
        YAML().dump(model, stream)
    population = json.loads(population_path.read_text())
    population["facts"]["record_has_holder"][0]["holder"] = "Alice"
    population_path.write_text(json.dumps(population))
    payload = api.check(model_path, population_path, admission=True)
    assert payload["exit_code"] == 1
    failed = next(row for row in payload["verdicts"] if row["verdict"] == "fail")
    assert failed["witnesses"] == ["R1"]
    assert failed["offending_facts"] == []
    assert payload["admission"]["blocked"] == []
    population["facts"]["holder_is_known"] = [{"record": "R2"}]
    population_path.write_text(json.dumps(population))
    asserted = api.check(model_path, population_path, admission=True)
    failed = next(row for row in asserted["verdicts"] if row["verdict"] == "fail")
    assert failed["witnesses"] == ["R1"]
    assert failed["offending_facts"] == []
    assert {tuple(row["fact_ref"].values()) for row in asserted["admission"]["admitted"]} >= {
        ("holder_is_known", 0),
    }

def test_legacy_versions_refuse_admission_and_v10_verdict_fields(tmp_path: Path) -> None:
    validator = Draft202012Validator(load_report_schema())
    for case_id in ("L01-absent-version-scalar", "W01-redacted-legacy-version"):
        payload = run_case(case_id, tmp_path)
        dirty = copy.deepcopy(payload)
        dirty["admission"] = {"admitted": [], "blocked": []}
        assert list(validator.iter_errors(dirty))
        dirty = copy.deepcopy(payload)
        dirty["verdicts"][0]["refused_facts"] = []
        assert list(validator.iter_errors(dirty))

def test_admission_text_lists_sorted_occurrences(tmp_path: Path) -> None:
    model_path, population_path = _files(tmp_path)
    result = run_gnd_text(
        "check", str(model_path), str(population_path), "--admission", "--format", "text",
    )
    assert result.returncode == 0
    lines = [line for line in result.stdout.splitlines() if line.startswith("ADMITTED ")]
    assert len(lines) == 10
    assert lines == sorted(lines)
    assert "ADMITTED record_key[0]" in lines

def test_admission_flag_refuses_transition_arm_without_report() -> None:
    result = run_gnd_text(
        "check", str(FIXTURE / "model.orm.yaml"),
        "--pre", str(FIXTURE / "population.pop.json"),
        "--steps", str(FIXTURE / "cases.json"),
        "--post", str(FIXTURE / "population.pop.json"),
        "--admission", "--format", "json",
    )
    assert result.returncode == 64
    assert result.stdout == ""

@pytest.mark.parametrize("hostile", ("nonfinite", "huge-integer", "deep", "oversize"))
def test_hostile_version_two_input_is_bounded_refusal(tmp_path: Path, hostile: str) -> None:
    model_path, population_path = _files(tmp_path)
    source = population_path.read_text()
    if hostile == "nonfinite":
        source = source.replace('"amount": 10', '"amount": NaN', 1)
    elif hostile == "huge-integer":
        source = source.replace('"amount": 10', '"amount": ' + '9' * 5000, 1)
    elif hostile == "deep":
        source = source.replace('"amount": 10', '"amount": ' + '[' * 300 + '0' + ']' * 300, 1)
    else:
        source += " " * (10 * 1024 * 1024)
    population_path.write_text(source)
    payload = api.check(model_path, population_path, admission=True)
    assert payload["exit_code"] == 3
    assert payload["schema_version"] == 10
    assert payload["admission"] == {"admitted": [], "blocked": []}

def test_huge_integer_direct_loader_uses_closed_error_type(tmp_path: Path) -> None:
    model_path, population_path = _files(tmp_path)
    population_path.write_text(
        population_path.read_text().replace('"amount": 10', '"amount": ' + '9' * 5000, 1)
    )
    with pytest.raises(PopulationLoadError):
        load_population(population_path, model=load_model(model_path))

def test_projection_failure_is_closed_v10(tmp_path: Path, monkeypatch) -> None:
    model_path, population_path = _files(tmp_path, "W02-redacted-admission-version")

    def fail_projection(*_args, **_kwargs):
        raise redaction.RedactionProjectionError("synthetic failure")

    monkeypatch.setattr(redaction, "project_output", fail_projection)
    payload = api.check(model_path, population_path, admission=True)
    assert payload["exit_code"] == 70
    assert payload["schema_version"] == 10
    assert payload["admission"] == {"admitted": [], "blocked": []}
    assert not list(Draft202012Validator(load_report_schema()).iter_errors(payload))

def test_admission_graph_failure_is_closed_v10(tmp_path: Path, monkeypatch) -> None:
    model_path, population_path = _files(tmp_path)

    def fail_graph(*_args, **_kwargs):
        raise ValueError("opaque-source-label-canary")

    monkeypatch.setattr(admission, "build_admission", fail_graph)
    payload = api.check(model_path, population_path, admission=True)
    assert payload["exit_code"] == 70
    assert payload["admission"] == {"admitted": [], "blocked": []}
    assert "opaque-source-label-canary" not in json.dumps(payload)
    assert not list(Draft202012Validator(load_report_schema()).iter_errors(payload))

def test_opaque_anchored_role_refuses_without_label_or_sidecar_guess(tmp_path: Path) -> None:
    model_path, population_path = _files(tmp_path, "A03-unchecked-transitive-block")
    model = YAML(typ="safe").load(model_path.read_text())
    model["fact_types"][2]["constraints"].append({
        "type": "anchored", "role": "amount", "source": "explicit",
        "status": "confirmed", "modality": "alethic",
        "provenance": {"user_quote": "The amount appears in the source."},
    })
    with model_path.open("w") as stream:
        YAML().dump(model, stream)
    payload = api.check(model_path, population_path, admission=True)
    assert payload["exit_code"] == 4
    anchored = next(row for row in payload["verdicts"] if row["constraint_type"] == "anchored")
    assert anchored["reason_code"] == "opaque-value"
    assert anchored["refused_facts"] == [
        {"fact_type": "record_has_amount", "index": 0},
    ]
    assert "amount-unread" not in json.dumps(payload)

def test_anchored_opaque_refusal_addresses_only_opaque_occurrence(tmp_path: Path) -> None:
    model_path, population_path = _files(tmp_path, "A03-unchecked-transitive-block")
    population = json.loads(population_path.read_text())
    population["facts"]["record_has_amount"][1]["amount"] = 20
    population_path.write_text(json.dumps(population))
    model = YAML(typ="safe").load(model_path.read_text())
    model["fact_types"][2]["constraints"].append({
        "type": "anchored", "role": "amount", "source": "explicit",
        "status": "confirmed", "modality": "alethic",
        "provenance": {"user_quote": "The amount appears in the source."},
    })
    with model_path.open("w") as stream:
        YAML().dump(model, stream)
    payload = api.check(model_path, population_path, admission=True)
    anchored = next(row for row in payload["verdicts"] if row["constraint_type"] == "anchored")
    assert anchored["reason_code"] == "opaque-value"
    assert anchored["refused_facts"] == [
        {"fact_type": "record_has_amount", "index": 0},
    ]

def test_opaque_frequency_family_refuses_in_its_actual_scope(tmp_path: Path) -> None:
    model_path, population_path = _files(tmp_path, "A03-unchecked-transitive-block")
    model = YAML(typ="safe").load(model_path.read_text())
    model["fact_types"][2]["constraints"].append({
        "type": "frequency", "scope": "internal", "roles": ["amount"],
        "bound": {"max": 1}, "source": "explicit", "status": "confirmed",
        "modality": "alethic", "provenance": {"user_quote": "Amounts occur once."},
    })
    with model_path.open("w") as stream:
        YAML().dump(model, stream)
    payload = api.check(model_path, population_path, admission=True)
    assert payload["exit_code"] == 4
    frequency = next(row for row in payload["verdicts"] if row["constraint_type"] == "frequency")
    assert frequency["reason_code"] == "opaque-value"
    assert frequency["refused_facts"] == [
        {"fact_type": "record_has_amount", "index": 0},
        {"fact_type": "record_has_amount", "index": 1},
    ]

def test_opaque_in_unselected_role_preserves_selected_constraints(tmp_path: Path) -> None:
    model_path, population_path = _files(tmp_path)
    population = json.loads(population_path.read_text())
    population["facts"]["record_has_holder"][0]["record"] = {
        "$opaque": "record-hidden",
    }
    population_path.write_text(json.dumps(population))
    payload = api.check(model_path, population_path, admission=True)
    assert payload["exit_code"] == 0
    for reference in (
        "fact_types[record_key].constraints[0]",
        "fact_types[record_has_holder].constraints[0]",
    ):
        verdict = next(row for row in payload["verdicts"] if row["constraint_ref"] == reference)
        assert verdict["verdict"] == "pass"

def test_admission_does_not_change_source_report(tmp_path: Path) -> None:
    model_path, population_path = _files(tmp_path, "A02-explicit-transitive-block")
    base = api._run_check_raw(model_path, population_path)
    projected = api._run_check(model_path, population_path, admission=True)
    assert base.report is not None and projected.report is not None
    assert base.report.model_dump() == projected.report.model_dump()
    assert base.report.has_vacuous == projected.report.has_vacuous
    for field in ("exit_code", "outcome", "acceptance_ready", "counts", "coverage"):
        assert base.payload[field] == projected.payload[field]

def test_dependency_ignores_shared_nonidentifying_value(tmp_path: Path) -> None:
    model_path, population_path = _files(tmp_path, "A02-explicit-transitive-block")
    model = YAML(typ="safe").load(model_path.read_text())
    approval = next(row for row in model["fact_types"] if row["id"] == "approval_for_record")
    approval["reading"] = "{Record} has approval {Approval} for amount {Amount}"
    approval["roles"].append({"object_type": "amount", "role_name": "amount"})
    with model_path.open("w") as stream:
        YAML().dump(model, stream)
    population = json.loads(population_path.read_text())
    population["facts"]["approval_for_record"][0]["amount"] = 20
    population["facts"]["approval_for_record"][1]["amount"] = 99
    population_path.write_text(json.dumps(population))
    payload = api.check(model_path, population_path, admission=True)
    assert payload["exit_code"] == 1
    blocked = {tuple(row["fact_ref"].values()) for row in payload["admission"]["blocked"]}
    assert ("approval_for_record", 0) in blocked
    assert ("approval_for_record", 1) not in blocked

def test_blocker_crosses_cycle_closing_edge(tmp_path: Path) -> None:
    model_path, population_path = _files(tmp_path)
    model = YAML(typ="safe").load(model_path.read_text())
    amount = next(row for row in model["fact_types"] if row["id"] == "record_has_amount")
    notice = next(row for row in model["fact_types"] if row["id"] == "notice_for_record")
    amount["depends_on"] = ["notice_for_record"]
    notice["constraints"] = [{
        "type": "value", "object_type": "notice",
        "role_ref": {"fact_type": "notice_for_record", "role": "notice"},
        "allowed": ["sent"], "source": "explicit", "status": "confirmed",
        "modality": "alethic", "provenance": {"user_quote": "Notice is sent."},
    }]
    with model_path.open("w") as stream:
        YAML().dump(model, stream)
    population = json.loads(population_path.read_text())
    population["facts"]["notice_for_record"][0]["notice"] = "bad"
    population_path.write_text(json.dumps(population))
    cyclic = api.check(model_path, population_path, admission=True)
    assert cyclic["exit_code"] == 1
    cyclic_blocked = {tuple(row["fact_ref"].values()) for row in cyclic["admission"]["blocked"]}
    assert {("record_has_amount", 0), ("approval_for_record", 0), ("notice_for_record", 0)} <= cyclic_blocked
    assert ("record_has_amount", 1) not in cyclic_blocked
    amount.pop("depends_on")
    with model_path.open("w") as stream:
        YAML().dump(model, stream)
    acyclic = api.check(model_path, population_path, admission=True)
    acyclic_blocked = {tuple(row["fact_ref"].values()) for row in acyclic["admission"]["blocked"]}
    assert ("record_has_amount", 0) not in acyclic_blocked

def test_version_two_is_bound_to_population_validation_stamp(tmp_path: Path) -> None:
    model_path, population_path = _files(tmp_path)
    model = load_model(model_path)
    population = load_population(population_path, model=model)
    assert population.format_version == 2
    assert population.matches_validation_marker(model)
    mutated = population.model_copy(update={"format_version": 1})
    assert not mutated.matches_validation_marker(model)
    try:
        check(model, mutated)
    except UnvalidatedPopulationError:
        pass
    else:
        raise AssertionError("changing the admitted format version must invalidate the stamp")

def test_dependency_is_verbalized_and_v10_is_readable_evidence(tmp_path: Path) -> None:
    model_path, _population_path = _files(tmp_path)
    verbalization = render_model_verbalization(model_path)
    assert "Admission depends on record_has_amount." in verbalization
    payload = run_case("A01-clean-partition", tmp_path)
    report_path = tmp_path / "check-v10.json"
    report_path.write_text(json.dumps(payload))
    document, binding = read_evidence_document(
        report_path, kind="check", payload_version=3,
    )
    assert document["schema_version"] == 10
    assert binding == "model-bound"

@pytest.mark.slow
def test_admission_projection_near_cap_chain_and_wide_unrelated_set(tmp_path: Path) -> None:
    model_path, population_path = _files(tmp_path)
    model = load_model(model_path)
    population = load_population(population_path, model=model)
    chain_types = [
        {
            "id": f"chain_{index:03d}",
            "roles": [
                {"object_type": "record", "role_name": "record"},
                {"object_type": "holder", "role_name": "holder"},
            ],
            "depends_on": [f"chain_{index - 1:03d}"] if index else [],
        }
        for index in range(80)
    ]
    wide_type = {"id": "wide", "roles": [
        {"object_type": "record", "role_name": "record"},
        {"object_type": "holder", "role_name": "holder"},
    ]}
    model = model.model_copy(update={"fact_types": [*chain_types, wide_type]})
    facts = {
        row["id"]: [{"record": "R-chain", "holder": "payload"}]
        for row in chain_types
    }
    facts["chain_000"][0]["holder"] = {"$opaque": "source"}
    facts["wide"] = [
        {"record": f"R-{index}", "holder": "x" * 110}
        for index in range(55_000)
    ]
    population = population.model_copy(update={"facts": facts})
    document_size = len(json.dumps({"facts": facts}).encode())
    assert 0.75 * MAX_POPULATION_BYTES < document_size < MAX_POPULATION_BYTES
    report = CheckReport(admission_projection=SimpleNamespace(findings=[]))
    started = time.perf_counter()
    projected = admission.build_admission(model, population, report)
    elapsed = time.perf_counter() - started
    assert elapsed < 20.0, f"indexed projection took {elapsed:.2f}s"
    assert len(projected["admitted"]) == 55_080
    assert projected["blocked"] == []
    assert projected["admitted"][0]["opaque_deps"] == [
        {"fact_ref": {"fact_type": "chain_000", "index": 0}, "role": "holder"},
    ]
    assert projected["admitted"][79]["opaque_deps"] == [
        {"fact_ref": {"fact_type": "chain_000", "index": 0}, "role": "holder"},
    ]

def test_dense_reference_key_does_not_materialize_pairwise_edges(tmp_path: Path) -> None:
    model_path, population_path = _files(tmp_path)
    model = load_model(model_path)
    population = load_population(population_path, model=model)
    roles = [
        {"object_type": "record", "role_name": "record"},
        {"object_type": "holder", "role_name": "holder"},
    ]
    model = model.model_copy(update={"fact_types": [
        {"id": "source", "roles": roles},
        {"id": "target", "roles": roles, "depends_on": ["source"]},
    ]})
    count = 1_000
    population = population.model_copy(update={"facts": {
        "source": [{"record": "R1", "holder": f"S{index}"} for index in range(count)],
        "target": [{"record": "R1", "holder": f"T{index}"} for index in range(count)],
    }})
    report = CheckReport(admission_projection=SimpleNamespace(findings=[]))
    tracemalloc.start()
    try:
        projected = admission.build_admission(model, population, report)
        _current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert len(projected["admitted"]) == 2 * count
    assert peak < 8_000_000, f"dense key materialized pairwise edges: {peak} bytes"
