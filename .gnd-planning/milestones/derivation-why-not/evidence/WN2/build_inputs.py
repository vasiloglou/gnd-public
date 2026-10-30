"""Write the WN2 corpus inputs under tests/fixtures/why_not/ (run once, from the repo root).

    uv run python .gnd-planning/milestones/derivation-why-not/evidence/WN2/build_inputs.py

Inputs only: the cases and goldens are written separately. Values carry a
``val-`` prefix or exceed 1000 so the leak test cannot collide with identifiers.
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path("tests/fixtures/why_not")
MODEL_ID = "urn:gnd-fixture:why-not-claims@1"


def ft(fact_id, roles, rule=None):
    row = {
        "id": fact_id,
        "reading": " ".join("{" + ot + "}" for _, ot in roles) + f" {fact_id}",
        "roles": [{"object_type": ot, "role_name": name} for name, ot in roles],
    }
    if rule is not None:
        row["derivation"] = "derived"
        row["derivation_rule"] = rule
    return row


def atom(fact_id, **bind):
    return {"fact_type": fact_id, "bind": bind}


MODEL = {
    "version": 2,
    "model_id": MODEL_ID,
    "source": {"kind": "text-conversation", "confidence": "standard", "mode": "one-shot"},
    "object_types": [
        {"id": "code", "name": "Code", "kind": "value", "primitive": "String"},
        {"id": "int", "name": "Int", "kind": "value", "primitive": "Integer"},
        {"id": "num", "name": "Num", "kind": "value", "primitive": "Number"},
    ],
    "fact_types": [
        ft("listed", [("work", "code")]),
        ft("wrote", [("work", "code"), ("person", "code")]),
        ft("credited", [("work", "code"), ("person", "code")], {
            "body": [atom("listed", work="$w"), atom("wrote", work="$w", person="$p")],
            "head": {"work": "$w", "person": "$p"}}),
        ft("claim", [("work", "code"), ("person", "code")], {
            "body": [atom("credited", work="$w", person="$p"), atom("listed", work="$w")],
            "head": {"work": "$w", "person": "$p"}}),
        ft("note", [("work", "code")], "A work is noted when an editor says so."),
        ft("tally", [("person", "code"), ("n", "int")], {
            "body": [atom("wrote", work="$w", person="$p")],
            "aggregate": {"fn": "count", "of": "$w", "over": ["$w"], "as": "$n"},
            "head": {"person": "$p", "n": "$n"}}),
        ft("score", [("work", "code"), ("points", "int")]),
        ft("ratio", [("work", "code"), ("r", "num")], {
            "body": [atom("score", work="$w", points="$a")],
            "head": {"work": "$w", "r": {"fn": "round", "args": [{"fn": "div", "args": [1, "$a"]}, 2]}}}),
        ft("left", [("x", "code")]),
        ft("right", [("y", "code")]),
        ft("pair", [("x", "code"), ("y", "code")], {
            "body": [atom("left", x="$x"), atom("right", y="$y")],
            "head": {"x": "$x", "y": "$y"}}),
        ft("lonely", [("x", "code")], {
            "body": [atom("pair", x="$x", y="$y"), atom("listed", work="$x")],
            "head": {"x": "$x"}}),
        # Review WN2-R3: a constant in an atom, and negated, comparison, head
        # and head-bind blockers.
        ft("pinned", [("work", "code")], {
            "body": [atom("listed", work="$w"), atom("wrote", work="$w", person="val-const-atom")],
            "head": {"work": "$w"}}),
        ft("delisted", [("work", "code")], {
            "body": [atom("score", work="$w", points="$a")],
            "negate": [atom("listed", work="$w")],
            "head": {"work": "$w"}}),
        ft("top_score", [("work", "code")], {
            "body": [atom("score", work="$w", points="$a")],
            "where": [{"operator": ">", "left": "$a", "right": 5000}],
            "head": {"work": "$w"}}),
        ft("doubled", [("work", "code"), ("n", "int")], {
            "body": [atom("score", work="$w", points="$a")],
            "head": {"work": "$w", "n": {"fn": "mul", "args": ["$a", 2]}}}),
        ft("tagged", [("work", "code"), ("tag", "code")], {
            "body": [atom("listed", work="$w")],
            "head": {"work": "$w", "tag": "val-const-head"}}),
    ],
}
DERIVED = [f["id"] for f in MODEL["fact_types"] if "derivation" in f]


def population(facts):
    return {
        "format_version": 2,
        "instances": {},
        "facts": facts,
        "population": {"model": "model.orm.json", "model_id": MODEL_ID,
                       "source": "fixture", "covers": DERIVED},
    }


def request(*targets):
    return {"version": 1, "targets": list(targets)}


def target(fact_type, *values):
    return {"fact_type": fact_type, "tuple": [{"primitive": "String", "value": v} for v in values]}


def write(path, document):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")


def main():
    claims = OUT / "claims"
    write(claims / "model.orm.json", MODEL)
    gap = {"listed": [{"work": "val-w1"}, {"work": "val-w2"}], "wrote": [],
           "score": [{"work": "val-w1", "points": 0}, {"work": "val-w2", "points": 1004}]}
    write(claims / "gap.pop.json", population(gap))
    write(claims / "repaired.pop.json", population(
        {**gap, "wrote": [{"work": "val-w1", "person": "val-p1"}]}))
    write(claims / "opaque.pop.json", population(
        {**gap, "listed": [{"work": {"$opaque": "val-hidden"}}]}))
    write(claims / "big.pop.json", population({
        "listed": [], "left": [{"x": f"val-l{i}"} for i in range(500)],
        "right": [{"y": f"val-r{i}"} for i in range(500)]}))
    rows = OUT / "rows"
    write(rows / "claim-w1-p1.json", request(target("claim", "val-w1", "val-p1")))
    write(rows / "zero.json", request())
    write(rows / "two.json", request(target("claim", "val-w1", "val-p1"),
                                     target("claim", "val-w2", "val-p1")))
    write(rows / "other-fact-type.json", request(target("credited", "val-w1", "val-p1")))
    write(rows / "primitive-mismatch.json", request(
        {"fact_type": "claim", "tuple": [{"primitive": "String", "value": "val-w1"},
                                         {"primitive": "Integer", "value": 1001}]}))
    write(rows / "tally-malformed.json", request(
        {"fact_type": "tally", "tuple": [{"primitive": "String", "value": "val-p1"}]}))
    write(rows / "doubled-w2.json", request(
        {"fact_type": "doubled", "tuple": [{"primitive": "String", "value": "val-w2"},
                                           {"primitive": "Integer", "value": 9999}]}))
    write(rows / "tagged-w1.json", request(target("tagged", "val-w1", "val-other")))
    write(rows / "reach-a-e.json", request(
        {"fact_type": "dispatch_reachable",
         "tuple": [{"primitive": "String", "value": "WH-A"},
                   {"primitive": "String", "value": "DEST-E"}]}))


if __name__ == "__main__":
    main()
