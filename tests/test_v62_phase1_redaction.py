

from __future__ import annotations

import json

from support.v62_phase1_corpus import ANSWERS, FIXTURE, document, population, steps

from gnd.api import transition
from gnd.model import Model
from gnd.redaction import RedactionPolicy, project_output


def _run(*, unredacted: bool, failing: bool = False) -> dict[str, object]:
    return transition(
        FIXTURE / "models/static.orm.yaml",
        population("pre_fail" if failing else "pre_clean"),
        steps(),
        population("post_exact"),
        unredacted=unredacted,
    )


def test_redaction_case_r01_r02_direct_and_transitive_taint() -> None:
    payload = _run(unredacted=False)
    assert payload["transition"]["evaluated"] is True
    raw = json.dumps(payload, sort_keys=True)
    assert ANSWERS["R01"]["forbidden"] not in raw
    assert ANSWERS["R02"]["forbidden"] not in raw


def test_redaction_case_r04_scrubs_precondition_message() -> None:
    payload = _run(unredacted=False, failing=True)
    assert payload["exit_code"] == ANSWERS["R04"]["exit"]
    assert ANSWERS["R04"]["forbidden"] not in json.dumps(payload, sort_keys=True)


def test_redaction_case_r03_negated_dependency_taint_is_live() -> None:
    doc = document("base")
    evidence_role = doc["fact_types"][0]["roles"][0]
    blocked_role = doc["fact_types"][1]["roles"][0]
    evidence_role.pop("redact", None)
    blocked_role["redact"] = True
    policy = RedactionPolicy.from_model(Model.model_validate(doc))
    assert ("eligible", "item") in policy.effective_roles
    assert ("final_eligible", "item") in policy.effective_roles


def test_redaction_case_r05_trusted_contrast() -> None:
    payload = _run(unredacted=True, failing=True)
    assert payload["exit_code"] == ANSWERS["R05"]["exit"]
    assert ANSWERS["R05"]["required"] in json.dumps(payload, sort_keys=True)


def test_redaction_case_r06_all_public_emitters() -> None:
    for failing in (False, True):
        payload = _run(unredacted=False, failing=failing)
        assert payload["transition"]["evaluated"] is True
        assert ANSWERS["R06"]["forbidden"] not in json.dumps(payload, sort_keys=True)


def test_create_freshness_verdict_redacts_tainted_operation_parameter() -> None:
    model = Model.model_validate(document("base"))
    policy = RedactionPolicy.from_model(model)
    secret = "SECRET-FRESHNESS-271828"
    payload = {
        "transition": {
            "evaluated": True,
            "steps": [
                {
                    "operation": "activate",
                    "bindings": {"item": secret},
                    "verdicts": [
                        {
                            "kind": "create-freshness",
                            "locator": "$.steps[1].effects[0].create",
                            "message": f"identity {secret} already exists",
                            "value": secret,
                        }
                    ],
                }
            ],
        }
    }
    projected = project_output("transition", payload, policy=policy, mode="applied")
    assert secret not in json.dumps(projected, sort_keys=True)


def test_operation_taint_is_transitive_and_independent_of_declaration_order() -> None:
    doc = document("base")
    doc["fact_types"].extend(
        [
            {
                "id": fact_type,
                "roles": [
                    {
                        "object_type": "item",
                        "role_name": "item",
                        **({"redact": True} if fact_type == "secret_a" else {}),
                    }
                ],
            }
            for fact_type in ("secret_a", "copied_b", "copied_c")
        ]
    )

    def copy_operation(identifier: str, source: str, target: str, parameter: str):
        return {
            "id": identifier,
            "parameters": [{"name": parameter, "object_type": "item"}],
            "preconditions": [
                {"require": [{"fact_type": source, "bind": {"item": f"${parameter}"}}]}
            ],
            "effects": [{"assert": {"fact_type": target, "bind": {"item": f"${parameter}"}}}],
        }

    doc["operations"] = [
        copy_operation("second", "copied_b", "copied_c", "y"),
        copy_operation("first", "secret_a", "copied_b", "x"),
    ]
    policy = RedactionPolicy.from_model(Model.model_validate(doc))
    assert ("copied_c", "item") in policy.effective_roles
