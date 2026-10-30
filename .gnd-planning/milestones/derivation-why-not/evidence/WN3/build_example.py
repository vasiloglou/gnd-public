"""Write src/gnd/examples/quoted_claims/ (run once, from the repo root)."""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path("src/gnd/examples/quoted_claims")
MODEL_ID = "urn:gnd-example:quoted-claims@1"


def ft(fact_id, reading, roles, rule=None):
    row = {"id": fact_id, "reading": reading,
           "roles": [{"object_type": ot, "role_name": name} for name, ot in roles]}
    if rule is not None:
        row["derivation"] = "derived"
        row["derivation_rule"] = rule
    return row


MODEL = {
    "version": 2,
    "model_id": MODEL_ID,
    "source": {"kind": "text-conversation", "confidence": "standard", "mode": "one-shot"},
    "object_types": [
        {"id": "quote_id", "name": "Quotation", "kind": "value", "primitive": "String"},
        {"id": "work", "name": "Work", "kind": "value", "primitive": "String"},
        {"id": "person", "name": "Person", "kind": "value", "primitive": "String"},
    ],
    "fact_types": [
        ft("quote", "{Quotation} appears in {Work}", [("quote", "quote_id"), ("work", "work")]),
        ft("authored", "{Work} was written by {Person}", [("work", "work"), ("person", "person")]),
        ft("reviewed", "{Work} was reviewed by {Person}", [("work", "work"), ("reviewer", "person")]),
        ft("certified", "{Quotation} is certified as said by {Person}",
           [("quote", "quote_id"), ("person", "person")], {
               "body": [
                   {"fact_type": "quote", "bind": {"quote": "$q", "work": "$w"}},
                   {"fact_type": "authored", "bind": {"work": "$w", "person": "$p"}},
                   {"fact_type": "reviewed", "bind": {"work": "$w", "reviewer": "$r"}},
               ],
               "head": {"quote": "$q", "person": "$p"}}),
    ],
}


def write(name, document):
    (OUT / name).write_text(json.dumps(document, indent=2) + "\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    write("model.orm.json", MODEL)
    write("gap.pop.json", {
        "format_version": 2, "instances": {},
        "facts": {"quote": [{"quote": "q-17", "work": "Field Notes"},
                            {"quote": "q-18", "work": "Letters Home"}],
                  "authored": [], "reviewed": []},
        "population": {"model": "model.orm.json", "model_id": MODEL_ID,
                       "source": "fixture", "covers": ["certified"]},
    })
    write("claim.json", {"version": 1, "targets": [{
        "fact_type": "certified",
        "tuple": [{"primitive": "String", "value": "q-17"},
                  {"primitive": "String", "value": "Ada Byrne"}]}]})
    write("extracted.json", {"reviewed": {"reviewer": "Cora Lind"}})


if __name__ == "__main__":
    main()
