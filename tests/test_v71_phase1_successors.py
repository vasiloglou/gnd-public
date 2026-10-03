import json
from copy import deepcopy
from datetime import date

import pytest
from b11_temporal_helpers import CORPUS, _cli, _load, _write
from jsonschema import Draft202012Validator

from gnd import api, semantic_spec
from gnd.exp.session_eval import VerifierPayloadError, validate_verifier_payload
from gnd.model import load_model
from gnd.report import load_report_schema


def _report(tmp_path):
    model, population = _load("dispatch")
    mp, pp = _write(tmp_path, model, population)
    return mp, pp, api.check(mp, pp)

def test_api_cli_and_closed_v11(tmp_path):
    mp, pp, payload = _report(tmp_path)
    result = _cli("check", str(mp), str(pp), "--format", "json")
    assert result.returncode == 0
    assert json.loads(result.stdout) == payload
    validator = Draft202012Validator(load_report_schema())
    assert not list(validator.iter_errors(payload))
    assert payload["redaction"] == {"mode": "applied", "declarations": []}
    assert "admission" not in payload
    for key in ("post", "transition", "redaction", "assurance"):
        altered = deepcopy(payload)
        del altered[key]
        assert list(validator.iter_errors(altered)), key
    altered = deepcopy(payload)
    altered["admission"] = None
    assert list(validator.iter_errors(altered))


def test_temporal_redaction_removes_witness_and_messages(tmp_path):
    model, population = _load("dispatch")
    for fact in model["fact_types"]:
        for role in fact["roles"]:
            if role["object_type"] == "dispatch_shipment":
                role["redact"] = True
    population["facts"]["dispatch_pickup_on"][0]["pickup"] = "2026-10-03"
    mp, pp = _write(tmp_path, model, population)
    payload = api.check(mp, pp)
    assert payload["exit_code"] == 1
    assert "SHIP-17" not in json.dumps(payload)
    assert payload["schema_version"] == 11
    assert not list(Draft202012Validator(load_report_schema()).iter_errors(payload))
    raw = api.check(mp, pp, unredacted=True)
    assert raw["redaction"]["mode"] == "unredacted"
    assert "SHIP-17" in json.dumps(raw)

def test_reader_requires_v11_and_checks_assurance(tmp_path):
    mp, pp, payload = _report(tmp_path)
    digest = "a" * 64
    kwargs = {
        "case_id": "temporal",
        "role": "required",
        "process_exit": 0,
        "expected_command": "check",
        "expected_subject": str(pp),
        "expected_model": str(mp),
        "candidate_sha256": digest,
        "contract_sha256": digest,
        "evidence_candidate_sha256": digest,
        "evidence_contract_sha256": digest,
    }
    validate_verifier_payload(json.dumps(payload).encode(), expected_schema_version=11, **kwargs)
    with pytest.raises(VerifierPayloadError, match="schema_version"):
        validate_verifier_payload(json.dumps(payload).encode(), expected_schema_version=7, **kwargs)
    forged = deepcopy(payload)
    forged["assurance"]["semantic_decision"] = "refuse"
    with pytest.raises(VerifierPayloadError, match="assurance"):
        validate_verifier_payload(json.dumps(forged).encode(), expected_schema_version=11, **kwargs)

def test_consumer_api_refuses_before_output(tmp_path):
    from gnd.codegen.emit import emit_project
    from gnd.extract.projection import project
    from gnd.model import ModelValidationError

    model = load_model(CORPUS / "dispatch/model.orm.yaml")
    with pytest.raises(ModelValidationError, match="temporal"):
        project(model)
    with pytest.raises(ModelValidationError, match="temporal"):
        emit_project(model, tmp_path / "generated")
    assert not (tmp_path / "generated").exists()

def test_opaque_join_key_cannot_become_a_definite_temporal_failure(tmp_path):
    model, population = _load("dispatch")
    population["facts"]["dispatch_pickup_on"][0]["shipment"] = {"$opaque": "unknown shipment"}
    population["facts"]["dispatch_pickup_on"][0]["pickup"] = "2026-10-03"
    mp, pp = _write(tmp_path, model, population)
    payload = api.check(mp, pp)
    guarded = next(row for row in payload["verdicts"] if row["constraint_ref"] == "constraints[0]")
    assert guarded["verdict"] == "unchecked"
    assert guarded["reason_code"] == "opaque-value"
    assert payload["exit_code"] == 4

def test_duplicate_rows_do_not_multiply_temporal_join(tmp_path):
    from unittest.mock import patch

    model, population = _load("dispatch")
    for name in ("dispatch_pickup_on", "dispatch_allowance_days", "dispatch_shipping_deadline"):
        population["facts"][name] *= 30
    mp, pp = _write(tmp_path, model, population)
    # Count the actual leaf visits, rather than asserting a host-dependent time.
    import gnd.temporal_guarded as temporal

    with (
        patch.object(
            semantic_spec, "scalar_identical", wraps=semantic_spec.scalar_identical
        ) as identity,
        patch.object(temporal, "evaluate_term", wraps=temporal.evaluate_term) as evaluate,
    ):
        payload = api.check(mp, pp)
    assert payload["exit_code"] == 0
    assert evaluate.call_count == 2
    assert identity.call_count < 500

def test_model_verbalization_names_calendar_day_direction():
    from gnd.model_verbalization import render_model_verbalization

    prose = render_model_verbalization(CORPUS / "dispatch/model.orm.yaml")
    assert "2 calendar days after $pickup" in prose
    from gnd.model_verbalization import _guarded_term

    assert (
        _guarded_term({"fn": "date_sub", "args": [{"date": "2024-03-01"}, {"duration_days": 1}]})
        == "(1 calendar days before date 2024-03-01)"
    )

def test_legacy_date_role_name_is_not_a_temporal_literal(tmp_path):
    model, population = _load("dispatch")
    model["version"] = 2
    for object_type in model["object_types"]:
        if object_type.get("primitive") == "Duration":
            object_type["primitive"] = "Integer"
    comparison = model["constraints"][0]["consequent"]["comparison"]
    comparison["left"] = "$pickup"
    for fact_type in model["fact_types"]:
        if fact_type["id"] == "dispatch_pickup_on":
            fact_type["roles"][1]["role_name"] = "date"
    atom = model["constraints"][0]["antecedent"][0]
    atom["bind"]["date"] = atom["bind"].pop("pickup")
    row = population["facts"]["dispatch_pickup_on"][0]
    row["date"] = row.pop("pickup")
    mp, pp = _write(tmp_path, model, population)
    assert api.check(mp, pp)["exit_code"] == 0
    assert api.check(mp, pp)["schema_version"] == 7

def test_duration_unification_is_refused_for_noncomparison_guards(tmp_path):
    model, population = _load("dispatch")
    constraint = model["constraints"][0]
    constraint["antecedent"].append(
        {
            "fact_type": "dispatch_allowance_days",
            "bind": {"shipment": "$shipment", "days": "$pickup"},
        }
    )
    constraint["consequent"] = {
        "absence": {
            "fact_type": "dispatch_pickup_on",
            "bind": {"shipment": "$shipment", "pickup": "$pickup"},
        }
    }
    mp, _ = _write(tmp_path, model, population)
    assert api.validate(mp)["exit_code"] == 3

def _duration_pair_model(primitive="Duration", right=2):
    model, population = _load("dispatch")
    model["object_types"].append(
        {"id": "other_days", "name": "OtherDays", "kind": "value", "primitive": primitive}
    )
    prototype = model["constraints"][0]
    constraint = {
        key: deepcopy(prototype[key]) for key in ("modality", "source", "status", "provenance")
    }
    constraint.update(type="value-comparison", role_a="duration", role_b="count", operator="<=")
    fact = {
        "id": "duration_pair",
        "reading": "{DispatchAllowance} pairs with {OtherDays}",
        "roles": [
            {"role_name": "duration", "object_type": "dispatch_allowance"},
            {"role_name": "count", "object_type": "other_days"},
        ],
        "constraints": [constraint],
    }
    model["fact_types"] = [fact]
    model["constraints"] = []
    population["population"]["covers"] = ["duration_pair"]
    population["facts"] = {"duration_pair": [{"duration": 2, "count": right}]}
    return model, population

def test_value_comparison_refuses_duration_integer_mixing(tmp_path):
    model, population = _duration_pair_model("Integer")
    mp, pp = _write(tmp_path, model, population)
    assert api.validate(mp)["exit_code"] == 3
    assert api.check(mp, pp)["exit_code"] == 3

def test_value_comparison_keeps_duration_domain_ordering(tmp_path):
    model, population = _duration_pair_model()
    mp, pp = _write(tmp_path, model, population)
    assert api.check(mp, pp)["exit_code"] == 0
    population["facts"]["duration_pair"][0]["count"] = 1
    mp, pp = _write(tmp_path, model, population)
    assert api.check(mp, pp)["exit_code"] == 1

def test_yaml_alias_cannot_authorize_a_forbidden_temporal_site(tmp_path):
    from b11_temporal_helpers import _forbidden_site

    model, population = _load("dispatch")
    _forbidden_site(model, "derivation-head")
    shared = model["fact_types"][-1]["derivation_rule"]["head"]["day"]
    model["constraints"][0]["consequent"]["comparison"]["left"] = shared
    mp, _ = _write(tmp_path, model, population)
    assert "&id" in mp.read_text()
    assert api.validate(mp)["exit_code"] == 3

def test_aliased_comparison_keeps_each_host_domain(tmp_path):
    model, population = _duration_pair_model("Integer")
    first = model["fact_types"][0]
    second = deepcopy(first)
    second["id"] = "integer_pair"
    second["reading"] = "{OtherDays} pairs with {OtherDays}"
    second["roles"][0]["object_type"] = "other_days"
    second["constraints"] = first["constraints"]
    model["fact_types"].append(second)
    mp, _ = _write(tmp_path, model, population)
    assert "&id" in mp.read_text()
    assert api.validate(mp)["exit_code"] == 3

def test_calendar_primitive_off_by_one_mutations_are_killed(tmp_path):
    from unittest.mock import patch

    from gnd import terms

    model, population = _load("dispatch")
    mp, pp = _write(tmp_path, model, population)
    assert api.check(mp, pp)["exit_code"] == 0
    for shift, pickup, expected_mutant in ((1, "2026-10-02", 1), (-1, "2026-10-03", 0)):

        class ShiftedDate(date):
            @classmethod
            def fromordinal(cls, ordinal, offset=shift):
                return date.fromordinal(ordinal + offset)

        population["facts"]["dispatch_pickup_on"][0]["pickup"] = pickup
        mp, pp = _write(tmp_path, model, population)
        expected = 0 if shift == 1 else 1
        assert api.check(mp, pp)["exit_code"] == expected
        with patch.object(terms, "date", ShiftedDate):
            mutated = api.check(mp, pp)["exit_code"]
        assert mutated == expected_mutant
        assert mutated != expected
