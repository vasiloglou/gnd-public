"""Build the literature lineage rule model from its declared path policy."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src/gnd/examples/literature"
LINEAGE = ROOT / "lineage"
ENDPOINTS = {"descendant": "participant_name", "ancestor": "participant_name"}
STEP = {**ENDPOINTS, "assertion": "passage_id"}


def fact(name, reading, roles, clauses, **extra):
    return {"id": name, "reading": reading,
            "roles": [{"role_name": key, "object_type": value} for key, value in roles.items()],
            "derivation": "derived", "derivation_rule": {"clauses": clauses}, **extra}


def atom(name, **bind):
    return {"fact_type": name, "bind": bind}


def clause(body, **head):
    return {"body": body, "head": head}


def closure(relation, direct):
    extras = {"assertion": "$p"} if direct.endswith("_step") else {}
    return [
        clause([atom(direct, descendant="$d", ancestor="$a", **extras)], descendant="$d", ancestor="$a"),
        clause([atom(direct, descendant="$d", ancestor="$m", **extras),
                atom(relation, descendant="$m", ancestor="$a")], descendant="$d", ancestor="$a"),
    ]


def model_from_policy(policy: dict, base: dict) -> dict:
    """Emit both path families from the same table and an admitted statement vocabulary."""
    derived = []
    primary = next(row for row in base["fact_types"] if row["id"] == "assertion_statement")
    all_roles = {row["role_name"]: "$" + row["role_name"] for row in primary["roles"]}
    for kind in ("lineage", "transfer"):
        step = f"{kind}_step"
        path = f"{kind}_ancestor"
        direct = "lineage_arc" if kind == "lineage" else step
        clauses = []
        for predicate in policy["chainable"]:
            bind = {**all_roles, "passage": "$p", "actor": "$d", "object": "$a", "predicate": predicate,
                    "actor_kind": "sense", "object_kind": "sense", "polarity": "asserts",
                    "attribution": "own-finding"}
            conditions = []
            if kind == "transfer":
                fields = policy["transfer"]
                bind.update(qualification=fields["qualification"])
                for arm in ("assumption_role", "interface_role"):
                    name = fields[arm]
                    variable = f"${name}"
                    bind[name] = variable
                    conditions.extend({"operator": "!=", "left": variable, "right": sentinel}
                                      for sentinel in policy["absence_words"])
            step_clause = clause([atom("assertion_statement", **bind)],
                                 descendant="$d", ancestor="$a", assertion="$p")
            if conditions:
                step_clause["where"] = conditions
            clauses.append(step_clause)
        derived.extend([
            fact(step, f"{{ParticipantName:descendant}} has {kind} step to "
                 "{ParticipantName:ancestor} in {PassageId}", STEP, clauses),
            fact(path, f"{{ParticipantName:descendant}} has {kind} ancestor {{ParticipantName:ancestor}}",
                 ENDPOINTS, closure(path, direct)),
        ])
    derived.append(fact(
        "lineage_arc", "{ParticipantName:descendant} is directly derived from {ParticipantName:ancestor}",
        ENDPOINTS, [clause([atom("lineage_step", descendant="$d", ancestor="$a", assertion="$p")], descendant="$d", ancestor="$a")],
        constraints=[{"type": "ring", "variant": "acyclic", "source": "explicit", "status": "confirmed",
                      "modality": "deontic", "provenance": {"user_quote": "Report cycles in documented lineage."}}],
    ))
    return {**base, "model_id": "urn:gnd-example:literature-qualified-lineage@1", "fact_types": base["fact_types"] + derived}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=LINEAGE / "model.orm.yaml")
    args = parser.parse_args()
    policy = json.loads((LINEAGE / "path-policy.json").read_bytes())
    base = json.loads((ROOT / "assertions/model.orm.yaml").read_bytes())
    args.out.write_text(json.dumps(model_from_policy(policy, base), indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
