import json
import subprocess
from copy import deepcopy
from pathlib import Path

import yaml

out = Path(".")
base = yaml.safe_load((out / "refunds.yaml").read_bytes())
for concept in base["ontology"]:
    for relationship in concept.get("relationships", []):
        relationship.pop("requires", None)


def entity(name, *, parents=(), relations=()):
    result = {"concept": name, "type": "EntityType"}
    if parents:
        result["extends"] = list(parents)
    if relations:
        result["relationships"] = list(relations)
    return result


def value(name):
    return {"concept": name, "type": "ValueType", "extends": ["String"]}


def relationship(owner, name, player, *, role=None):
    declared = {"concept": player}
    if role is not None:
        declared["name"] = role
    token = player if role is None else player + ":" + role
    return {
        "name": name,
        "roles": [declared],
        "verbalizes": ["{" + owner + "} " + name + " {" + token + "}"],
    }


base["ontology"].extend(
    [
        entity("Expense", relations=[relationship("Expense", "status", "ExpenseStatus")]),
        value("ExpenseStatus"),
        entity(
            "Enrolment",
            relations=[
                relationship("Enrolment", "student", "Student"),
                relationship("Enrolment", "course", "Course"),
            ],
        ),
        entity("Student"),
        entity("Course"),
        entity(
            "Component",
            relations=[relationship("Component", "imports", "Component", role="imported")],
        ),
        entity("LibraryItem"),
        entity(
            "BookItem",
            parents=["LibraryItem"],
            relations=[
                relationship("BookItem", "book_type", "BookType"),
                relationship("BookItem", "checkout", "Borrower"),
            ],
        ),
        entity("PeriodicalItem", parents=["LibraryItem"]),
        entity("Borrower"),
        value("BookType"),
        value("Contract"),
        value("Party"),
        entity("Shipment", relations=[relationship("Shipment", "dispatch_request", "Warehouse")]),
        entity(
            "Warehouse",
            relations=[
                {"name": "dispatch_allowed", "verbalizes": ["{Warehouse} is approved for dispatch"]}
            ],
        ),
        entity(
            "Employee",
            relations=[
                {
                    "name": "approved_by",
                    "roles": [
                        {"concept": "Employee", "name": "employee"},
                        {"concept": "System", "name": "system"},
                    ],
                    "verbalizes": ["{Employee} approves {Employee:employee} for {System:system}"],
                },
                relationship("Employee", "management_chain", "Employee", role="manager"),
            ],
        ),
        entity("System"),
        entity(
            "Student",
            relations=[
                {
                    "name": "enrolls",
                    "roles": [{"concept": "Course"}, {"concept": "Term"}],
                    "verbalizes": ["{Student} enrolls in {Course} in {Term}"],
                },
            ],
        ),
        entity("Course"),
        entity("Term"),
    ]
)
next(c for c in base["ontology"] if c["concept"] == "Contract")["relationships"] = [
    relationship("Contract", "has_party", "Party")
]


def scope_for(doc, scope):
    if scope == "top":
        return doc
    kind, name = scope.split(":")
    owner, _, property_name = name.partition(".")
    concept = next(c for c in doc["ontology"] if c["concept"] == owner)
    return (
        concept
        if kind == "concept"
        else next(r for r in concept["relationships"] if r["name"] == property_name)
    )


def check(name, doc):
    path = Path("input") / ("e2-" + name + ".yaml")
    path.write_text(yaml.safe_dump(doc, sort_keys=False))
    cmd = ["b/bin/python", "parse.py", str(path)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=False)
    return {
        "command": cmd,
        "exit": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


observations = {
    "limits": "These are parser and scope probes. Acceptance does not establish formula equivalence."
}
observations["positive_control"] = check("control", base)
bad = deepcopy(base)
scope_for(bad, "concept:Refund")["requires"] = ["COUNT[Refund.refund_by >"]
observations["negative_control"] = check("malformed", bad)
assert observations["positive_control"]["exit"] == 0, observations["positive_control"]
assert observations["negative_control"]["exit"] == 1, observations["negative_control"]
probes = json.loads((out / "formulas.json").read_bytes())
observations["probes"] = {}
for kind, probe in probes.items():
    doc = deepcopy(base)
    scope_for(doc, probe["scope"])["requires"] = [probe["formula"]]
    observations["probes"][kind] = check(kind, doc)
assert {kind.split("-internal")[0].split("-external")[0] for kind in probes} == set(
    json.loads((out / "constraint-census.json").read_bytes())
)
(out / "E2.json").write_text(json.dumps(observations, indent=2) + "\n")
print(
    "E2 controls 0/1;",
    ", ".join(f"{name}: {result['exit']}" for name, result in observations["probes"].items()),
)
