"""Verify the revised reading cases through the pinned Ossie parser."""

import ast
import json
import re
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml
from ossie_ontology.parser import OssieParser

repo, evidence, original = map(Path, sys.argv[1:])
e4 = json.loads((evidence / "E4.json").read_bytes())
cached_docs = {}


def source_fact(case):
    model = case["model"]
    if model not in cached_docs:
        cached_docs[model] = yaml.safe_load((repo / model).read_bytes())
    doc = cached_docs[model]
    return (
        next(f for f in doc["fact_types"] if f["id"] == case["fact"]),
        {item["id"]: item["name"] for item in doc["object_types"]},
    )


def parsed_relationship(path, labels, alias_for_role, patterns, multiplicity):
    owner, *additional = labels
    first = alias_for_role[owner]
    concepts = {name: {"concept": name, "type": "EntityType"} for name in alias_for_role.values()}
    relationship = {
        "name": "related",
        "roles": [{"concept": alias_for_role[label], "name": label} for label in additional],
        "verbalizes": patterns,
    }
    if multiplicity:
        relationship["multiplicity"] = multiplicity
    concepts[first]["relationships"] = [relationship]
    spec = {"version": "0.3.0.dev0", "name": "OrderControl", "ontology": list(concepts.values())}
    path.write_text(yaml.safe_dump(spec, sort_keys=False))
    (result,) = OssieParser().parse(path).ontology.relationships
    return result


def verify_roles(path, labels, aliases, patterns, expected, multiplicity=None):
    relation = parsed_relationship(path, labels, aliases, patterns, multiplicity)
    assert [role.player.name for role in relation.roles] == [aliases[label] for label in labels]
    actual = [
        [role.name or labels[0] for role in reading.roles] for reading in relation.verbalizations
    ]
    assert actual == expected, (labels, patterns, actual, expected)
    assert (relation.multiplicity.value if relation.multiplicity else None) == multiplicity


def count_require(source):
    return sum(
        isinstance(node, ast.Call)
        and (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "require"
            or isinstance(node.func, ast.Name)
            and node.func.id == "require"
        )
        for node in ast.walk(ast.parse(source))
    )


assert count_require("m.where(x).require(y)\nrequire(z)\n") == 2
assert count_require("value = x.require\ntext = '.require(x)'\n") == 0
for model in ("flights", "refunds"):
    assert count_require((original / f"E3-{model}.pyrel.txt").read_text()) == 0

reordered = {(case["model"], case["fact"]): case["reordered_roles"] for case in e4["reorders"]}
with TemporaryDirectory() as scratch:
    path = Path(scratch) / "order.ontology.yaml"
    for case in e4["reading_checks"]:
        fact, names = source_fact(case)
        ids = dict.fromkeys(role["object_type"] for role in fact["roles"])
        by_id = {oid: f"CaseType{i}" for i, oid in enumerate(ids)}
        by_name = {names[oid]: alias for oid, alias in by_id.items()}
        assert len(by_name) == len(by_id), (case["model"], case["fact"])
        labels = [role["role_name"] for role in fact["roles"]]
        aliases = {role["role_name"]: by_id[role["object_type"]] for role in fact["roles"]}

        def rewrite(match, by_name=by_name):
            name, separator, label = match[1].partition(":")
            return "{" + by_name[name] + separator + label + "}"

        for pattern_key, order in (
            ("original_order_pattern", labels),
            ("projected_order_pattern", reordered.get((case["model"], case["fact"]), labels)),
        ):
            readings = list(case["readings"].values())
            patterns = [
                re.sub(r"\{([^{}]+)\}", rewrite, reading[pattern_key]) for reading in readings
            ]
            verify_roles(path, order, aliases, patterns, [reading["roles"] for reading in readings])

    for multiplicity in ("ManyToOne", "OneToOne"):
        verify_roles(
            path,
            ["b", "a"],
            {"a": "Node", "b": "Node"},
            ["{Node:a} relates to {Node}"],
            [["a", "b"]],
            multiplicity,
        )
    try:
        parsed_relationship(
            path, ["b", "a"], {"a": "Node", "b": "Node"}, ["{Node} relates to {Node}"], "ManyToOne"
        )
    except ValueError:
        pass
    else:
        raise AssertionError("ambiguous repeated-role reading was accepted")

result = {
    "reading_cases": len(e4["reading_checks"]),
    "original_and_projected_orders_checked": len(e4["reading_checks"]) * 2,
    "reordered_cases": len(reordered),
    "control_multiplicities": ["ManyToOne", "OneToOne"],
    "ambiguous_repeated_role": "refused",
    "require_call_counter_positive": 2,
    "require_call_counter_negative": 0,
    "retained_pyrel_require_counts": {"flights": 0, "refunds": 0},
}
(evidence / "controls.json").write_text(json.dumps(result, indent=2) + "\n")
print(
    f"Parser verified {result['original_and_projected_orders_checked']} reading orders, "
    f"including {result['reordered_cases']} changed declaration orders."
)
print("OneToOne, ManyToOne, repeated-role refusal and require counter controls passed.")
