from __future__ import annotations

from pathlib import Path

from support.v70_phase4 import _derivation, _unknown_positive, _write

from gnd import api


def test_constraint_reading_unknown_is_unchecked_and_definite_failure_wins(tmp_path: Path) -> None:
    model, population = _unknown_positive()
    model["fact_types"][0]["constraints"] = [{
        "type": "uniqueness", "roles": ["record"], "modality": "alethic",
        "source": "explicit", "status": "confirmed",
        "provenance": {"user_quote": "A record has one observation."},
    }]
    model["fact_types"][1]["constraints"] = [{
        "type": "uniqueness", "roles": ["item"], "modality": "alethic",
        "source": "explicit", "status": "confirmed",
        "provenance": {"user_quote": "An item occurs at most once."},
    }]
    paths = _write(tmp_path, model, population)
    payload = api.check(*paths, admission=True)
    assert payload["exit_code"] == 4
    assert [row["reason_code"] for row in payload["verdicts"]] == [None, "derived-unknown"]
    assert _derivation(payload)["verdict"] == "pass"

    opaque = population["facts"]["observed"].pop()
    paths = _write(tmp_path, model, population)
    assert [row["verdict"] for row in api.check(*paths, admission=True)["verdicts"]] == [
        "pass", "pass"
    ]
    population["facts"]["observed"].append(opaque)

    population["facts"]["observed"].append({"record": "R2", "item": "A"})
    population["facts"]["inferred"].append({"record": "R2", "item": "A"})
    paths = _write(tmp_path, model, population)
    payload = api.check(*paths, admission=True)
    assert payload["exit_code"] == 1
    assert payload["verdicts"][1]["verdict"] == "fail"

def test_subset_failure_with_possible_superset_is_unchecked(tmp_path: Path) -> None:
    model, population = _unknown_positive()
    model["fact_types"][1]["derivation_rule"]["where"] = [
        {"operator": "=", "left": "$i", "right": "B"}
    ]
    model["fact_types"].append({
        "id": "required", "reading": "{Record} requires {Item}",
        "roles": [{"object_type": "record", "role_name": "record"},
                  {"object_type": "item", "role_name": "item"}],
    })
    model["constraints"] = [{
        "type": "subset",
        "subset_role_seq": [{"fact_type": "required", "role": role} for role in ("record", "item")],
        "superset_role_seq": [{"fact_type": "inferred", "role": role} for role in ("record", "item")],
        "source": "explicit", "status": "confirmed", "modality": "alethic",
        "provenance": {"user_quote": "Required pairs are inferred."},
    }]
    population["population"]["covers"].append("required")
    population["facts"]["observed"] = [
        {"record": "R0", "item": "B"},
        {"record": "R1", "item": {"$opaque": "unknown"}},
    ]
    population["facts"]["inferred"] = [{"record": "R0", "item": "B"}]
    population["facts"]["required"] = [{"record": "R1", "item": "B"}]
    payload = api.check(*_write(tmp_path, model, population), admission=True)
    assert payload["verdicts"][0]["verdict"] == "unchecked"
    assert payload["verdicts"][0]["reason_code"] == "derived-unknown"

def test_known_uniqueness_key_stays_pass_with_unknown_other_role(tmp_path: Path) -> None:
    model, population = _unknown_positive()
    model["fact_types"][1]["constraints"] = [{
        "type": "uniqueness", "roles": ["record"], "modality": "alethic",
        "source": "explicit", "status": "confirmed",
        "provenance": {"user_quote": "Each record has one inferred item."},
    }]
    payload = api.check(*_write(tmp_path, model, population), admission=True)
    assert payload["verdicts"][0]["verdict"] == "pass"
