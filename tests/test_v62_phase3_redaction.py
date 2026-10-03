

from __future__ import annotations

import json
from copy import deepcopy

from support.v62_phase3_corpus import FIXTURE

from gnd.api import check
from gnd.model import Model, load_model, semantic_validate
from gnd.redaction import INSTANCE_DETAIL, RedactionPolicy, _project_transition, project_output


def test_r01_r05_term_taint_reaches_every_presence_and_upper_role() -> None:
    policy = RedactionPolicy.from_model(load_model(FIXTURE / "models/exact-terms.orm.yaml"))
    assert {
        ("input", "value"),
        ("residue", "ticket"),
        ("residue", "residue"),
        ("doubled_residue", "ticket"),
        ("doubled_residue", "doubled"),
        ("permitted", "ticket"),
        ("ticket_status", "ticket"),
    } <= policy.effective_roles
    assert ("input", "ticket") not in policy.effective_roles
    assert ("input", "divisor") not in policy.effective_roles
    assert policy.verdict_roles({"constraint_ref": "constraints[0]"}) == frozenset(
        {("input", "value")}
    )


def test_r05_term_taint_projects_transition_delta_and_computed_post_rows() -> None:
    policy = RedactionPolicy.from_model(load_model(FIXTURE / "models/exact-terms.orm.yaml"))
    block = {
        "steps": [
            {
                "operation": "approve",
                "bindings": {},
                "verdicts": [],
                "derived_changes": [
                    {
                        "fact_type": "ticket_status",
                        "added": [{"ticket": "SECRET-TERM-314159", "status": "approved"}],
                        "removed": [],
                    }
                ],
            }
        ],
        "computed_post": {
            "facts": {"ticket_status": [{"ticket": "SECRET-TERM-314159", "status": "approved"}]}
        },
    }

    _project_transition(block, policy)

    encoded = json.dumps(block, sort_keys=True)
    assert "SECRET-TERM-314159" not in encoded
    assert encoded.count('"redacted": true') == 2
    assert encoded.count("ticket_status.ticket") == 2


def test_r04_unavailable_derivation_message_does_not_leak_binding() -> None:
    model = load_model(FIXTURE / "models/exact-terms.orm.yaml")
    payload = {
        "derivations": [
            {
                "fact_type": "residue",
                "message": "term:mod-zero for {'ticket': 'zero', 'value': 7, 'divisor': 0}",
                "findings": [],
            }
        ]
    }

    redacted = project_output(
        "check",
        payload,
        policy=RedactionPolicy.from_model(model),
        mode="applied",
    )

    assert redacted["derivations"][0]["message"] == INSTANCE_DETAIL
    assert "zero" not in str(redacted)
    assert "7" not in str(redacted)


def test_r04_r06_public_check_redacts_bindings_but_keeps_public_metadata() -> None:
    model = FIXTURE / "models/exact-terms.orm.yaml"
    population = FIXTURE / "populations/term-input.pop.yaml"

    applied = check(model, population)
    unredacted = check(model, population, unredacted=True)
    applied_bytes = json.dumps(applied, sort_keys=True)
    unredacted_bytes = json.dumps(unredacted, sort_keys=True)

    assert "binding={'ticket': 'zero', 'value': 7, 'divisor': 0}" not in applied_bytes
    assert "binding={'ticket': 'zero', 'value': 7, 'divisor': 0}" in unredacted_bytes
    assert {row["reason_code"] for row in applied["derivations"]} == {"term:mod-zero"}
    assert applied["model_digest"] == unredacted["model_digest"]


def test_unavailable_message_redacts_sensitive_body_binding_not_used_by_head() -> None:
    document = deepcopy(
        load_model(FIXTURE / "models/exact-terms.orm.yaml").model_dump(exclude={"warnings"})
    )
    document["fact_types"][0]["roles"].append(
        {"object_type": "ticket", "role_name": "secret", "redact": True}
    )
    document["fact_types"][0]["roles"][1]["redact"] = False
    document["fact_types"][0]["reading"] = (
        "{Ticket} has value {Integer}, divisor {Integer}, and secret {Ticket}"
    )
    document["fact_types"][1]["derivation_rule"]["body"][0]["bind"]["secret"] = "$secret"
    document["constraints"][0]["antecedent"][0]["bind"]["secret"] = "$secret"
    assert semantic_validate(document) == []
    model = Model.model_validate(document)
    policy = RedactionPolicy.from_model(model)
    assert policy.fact_roles("residue") == frozenset()
    assert ("input", "secret") in policy.derivation_roles("residue")
    payload = {
        "derivations": [
            {
                "fact_type": "residue",
                "message": "term unavailable; binding={'secret': 'SECRET-LEAK'}",
                "findings": [],
            }
        ]
    }

    redacted = project_output(
        "check",
        payload,
        policy=policy,
        mode="applied",
    )

    assert redacted["derivations"][0]["message"] == INSTANCE_DETAIL
    assert "SECRET-LEAK" not in json.dumps(redacted)


def test_guarded_unavailable_message_redacts_sensitive_unused_antecedent() -> None:
    document = deepcopy(
        load_model(FIXTURE / "models/exact-terms.orm.yaml").model_dump(exclude={"warnings"})
    )
    document["fact_types"][0]["roles"].append(
        {"object_type": "ticket", "role_name": "secret", "redact": True}
    )
    document["fact_types"][0]["reading"] = (
        "{Ticket} has value {Integer}, divisor {Integer}, and secret {Ticket}"
    )
    document["fact_types"][1]["derivation_rule"]["body"][0]["bind"]["secret"] = "$secret"
    document["constraints"][0]["antecedent"][0]["bind"]["secret"] = "$secret"
    assert semantic_validate(document) == []
    policy = RedactionPolicy.from_model(Model.model_validate(document))
    payload = {
        "verdicts": [
            {
                "constraint_ref": "constraints[0]",
                "message": "term unavailable; binding={'secret': 'SECRET-LEAK'}",
            }
        ]
    }

    redacted = project_output("check", payload, policy=policy, mode="applied")

    assert redacted["verdicts"][0]["message"] == INSTANCE_DETAIL
    assert "SECRET-LEAK" not in json.dumps(redacted)

    transition = {
        "steps": [
            {
                "operation": "approve",
                "verdicts": [
                    {
                        "fact_type": "permitted",
                        "message": "unavailable binding={'secret': 'SECRET-TRANSITION'}",
                    }
                ],
            }
        ]
    }
    _project_transition(transition, policy)
    assert transition["steps"][0]["verdicts"][0]["message"] == INSTANCE_DETAIL
    assert "SECRET-TRANSITION" not in json.dumps(transition)
