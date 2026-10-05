from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parents[1]

CORPUS = ROOT / "tests/fixtures/v71/phase1"

yaml = YAML(typ="safe")

def _load(domain: str) -> tuple[dict, dict]:
    model = yaml.load((CORPUS / domain / "model.orm.yaml").read_text())
    population = json.loads((CORPUS / domain / "population.pop.json").read_text())
    return model, population

def _write(tmp_path: Path, model: dict, population: dict) -> tuple[Path, Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    model_path = tmp_path / "model.orm.yaml"
    population_path = tmp_path / "population.pop.json"
    with model_path.open("w") as stream:
        YAML().dump(model, stream)
    population_path.write_text(json.dumps(population, ensure_ascii=False) + "\n")
    return model_path, population_path

def _cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "gnd", *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=20,
    )

def _forbidden_site(model: dict, site: str) -> None:
    date_term = {"fn": "date_add", "args": ["$pickup", {"duration_days": 1}]}
    # Remove the admitted guarded use; otherwise a broken site-specific check
    # could be masked by the ordinary temporal path.
    model["constraints"][0]["consequent"]["comparison"]["left"] = "$pickup"
    if site in {"derivation-head", "derivation-where"}:
        rule = {
            "body": [
                {
                    "fact_type": "dispatch_pickup_on",
                    "bind": {"shipment": "$shipment", "pickup": "$pickup"},
                }
            ],
            "head": {"shipment": "$shipment", "day": "$pickup"},
        }
        if site == "derivation-head":
            rule["head"]["day"] = date_term
        else:
            rule["where"] = [{"operator": "<=", "left": date_term, "right": "$pickup"}]
        model["fact_types"].append(
            {
                "id": "dispatch_computed_day",
                "reading": "{DispatchShipment} has computed day {DispatchCalendarDay}",
                "roles": [
                    {"object_type": "dispatch_shipment", "role_name": "shipment"},
                    {"object_type": "dispatch_calendar_day", "role_name": "day"},
                ],
                "derivation": "derived",
                "derivation_rule": rule,
            }
        )
    elif site == "operation-binding":
        model["operations"] = [
            {
                "id": "reschedule",
                "reading": "{DispatchShipment} reschedules",
                "parameters": [
                    {"name": "shipment", "object_type": "dispatch_shipment"},
                    {"name": "pickup", "object_type": "dispatch_calendar_day"},
                ],
                "preconditions": [],
                "effects": [
                    {
                        "assert": {
                            "fact_type": "dispatch_pickup_on",
                            "bind": {"shipment": "$shipment", "pickup": date_term},
                        }
                    }
                ],
                "frame": {"modality": "alethic"},
                "source": "user-supplied",
                "status": "confirmed",
                "provenance": {"user_quote": "A reschedule changes pickup."},
            }
        ]
    else:
        model["constraints"][0]["consequent"] = {
            "exists": {
                "atoms": [
                    {
                        "fact_type": "dispatch_pickup_on",
                        "bind": {"shipment": "$shipment", "pickup": "$witness"},
                    }
                ],
                "where": [{"operator": "<=", "left": date_term, "right": "$witness"}],
            }
        }
