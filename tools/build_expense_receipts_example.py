"""Build the expense receipts example: three documents, one checked claim.

    uv run python tools/build_expense_receipts_example.py src/gnd/examples/expense/receipts

A travel approval, a hotel folio and a card statement are each read with the
reading model, verified, and handed to the checking model. A reviewer's
identity decisions join the card's vendor names to the folio's. Three
composition directories are written:

    claim/          the reviewer's four decisions (same, same, unresolved, different)
    claim-flat/     no decisions: names joined exactly as printed
    claim-missing/  the Café Central decision left out, so gnd compose refuses

The approved vendor list is a fixed reference population declared by both
models. Every digest is computed here. Deterministic: fixed texts and
canonical JSON. docs/expense/05-receipts.md reports what these inputs give.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from gnd.anchors import bind_anchors, parse_anchor_sidecar, vocabulary_digest
from gnd.artifacts import canonical_json_bytes, sha256_hex
from gnd.extract.bundle import bundle_stem
from gnd.model import load_model
from gnd.population import load_population_bytes

GENERATED = ("vocabulary", "reference", "artifacts", "extracted", "claim", "claim-flat", "claim-missing")
SRC = {"kind": "text-conversation", "confidence": "standard", "mode": "one-shot"}
POLICY = "Finance policy for travel claims, fictional exercise brief."


def prov(quote):
    return {"source": "explicit", "status": "confirmed", "modality": "alethic",
            "provenance": {"user_quote": quote}}


def anchored(role, quote):
    return {"type": "anchored", "role": role, **prov(quote)}


VOCABULARY = {
    "version": 2, "source": SRC,
    "object_types": [
        {"id": "expense", "name": "Expense", "kind": "value", "primitive": "String"},
        {"id": "receipt", "name": "Receipt", "kind": "value", "primitive": "String"},
        {"id": "vendor", "name": "Vendor", "kind": "value", "primitive": "String"},
        {"id": "trip", "name": "Trip", "kind": "value", "primitive": "String"},
        {"id": "amount", "name": "Amount", "kind": "value", "primitive": "Integer"},
        {"id": "day", "name": "Day", "kind": "value", "primitive": "Date"},
    ],
    "fact_types": [
        {"id": "expense_paid_to_vendor", "reading": "{Expense} was paid to {Vendor}",
         "roles": [{"object_type": "expense", "role_name": "expense"}, {"object_type": "vendor", "role_name": "vendor"}],
         "constraints": [anchored("vendor", "Every card line names the vendor as printed on the statement.")]},
        {"id": "expense_has_amount", "reading": "{Expense} costs {Amount} euros",
         "roles": [{"object_type": "expense", "role_name": "expense"}, {"object_type": "amount", "role_name": "amount"}]},
        {"id": "expense_incurred_on", "reading": "{Expense} was incurred on {Day}",
         "roles": [{"object_type": "expense", "role_name": "expense"}, {"object_type": "day", "role_name": "day"}]},
        {"id": "expense_claimed_for_trip", "reading": "{Expense} is claimed for {Trip}",
         "roles": [{"object_type": "expense", "role_name": "expense"}, {"object_type": "trip", "role_name": "trip"}]},
        {"id": "receipt_issued_by_vendor", "reading": "{Receipt} was issued by {Vendor}",
         "roles": [{"object_type": "receipt", "role_name": "receipt"}, {"object_type": "vendor", "role_name": "vendor"}],
         "constraints": [anchored("vendor", "Every receipt line names the vendor as printed on the folio.")]},
        {"id": "trip_starts_on", "reading": "{Trip} starts on {Day}",
         "roles": [{"object_type": "trip", "role_name": "trip"}, {"object_type": "day", "role_name": "day"}]},
        {"id": "trip_ends_on", "reading": "{Trip} ends on {Day}",
         "roles": [{"object_type": "trip", "role_name": "trip"}, {"object_type": "day", "role_name": "day"}]},
        {"id": "approved_vendor", "reading": "{Vendor} is on the approved vendor list",
         "roles": [{"object_type": "vendor", "role_name": "vendor"}]},
    ],
    "constraints": [],
}

CATALOG = {"population": {"covers": ["approved_vendor"], "model": "catalog", "source": "fixture"},
           "facts": {"approved_vendor": [{"vendor": v} for v in ("Hotel Lumière", "TAXI G7", "Café Central")]}}


def date_rule(rule_id, bound_fact, op, quote):
    return {
        "id": rule_id, "type": "guarded", **prov(quote),
        "remedy": "Remove the line from the claim or attach the approval for the extra day.",
        "antecedent": [
            {"fact_type": "expense_claimed_for_trip", "bind": {"expense": "$e", "trip": "$t"}},
            {"fact_type": "expense_incurred_on", "bind": {"expense": "$e", "day": "$d"}},
            {"fact_type": bound_fact, "bind": {"trip": "$t", "day": "$b"}},
        ],
        "consequent": {"comparison": {"left": "$d", "operator": op, "right": "$b"}},
    }


CHECKING_RULES = [
    {"id": "card_line_has_receipt", "type": "subset", **prov("Every card charge needs a receipt from the same vendor."),
     "subset_role_seq": [{"fact_type": "expense_paid_to_vendor", "role": "vendor"}],
     "superset_role_seq": [{"fact_type": "receipt_issued_by_vendor", "role": "vendor"}]},
    {"id": "vendor_is_approved", "type": "subset", **prov("Only vendors on the approved list can be claimed."),
     "subset_role_seq": [{"fact_type": "expense_paid_to_vendor", "role": "vendor"}],
     "superset_role_seq": [{"fact_type": "approved_vendor", "role": "vendor"}]},
    date_rule("not_before_trip", "trip_starts_on", ">=", "A claimed expense falls inside the approved trip dates."),
    date_rule("not_after_trip", "trip_ends_on", "<=", "A claimed expense falls inside the approved trip dates."),
]

DOCUMENTS = {
    "approval": (
        "Travel approval TA-2026-031\n"
        "Trip T-114: A. Martin to Paris for the client workshop.\n"
        "Approved from 2026-03-02 to 2026-03-06.\n",
        {"trip_starts_on": [{"trip": "T-114", "day": "2026-03-02"}],
         "trip_ends_on": [{"trip": "T-114", "day": "2026-03-06"}]},
    ),
    "folio": (
        "Hotel Lumière, 12 rue des Lilas, Paris\n"
        "Folio 7781, guest A. Martin, 2026-03-02 to 2026-03-05\n"
        "R1 Hotel Lumière: room, 3 nights, 612.00 EUR\n"
        "R2 Spa Lumière: massage, charged to room, 95.00 EUR\n"
        "R3 Café Central (lobby café): breakfast, charged to room, 18.50 EUR\n"
        "R4 Taxi booked by the concierge, paid by card: 42.00 EUR\n",
        {"receipt_issued_by_vendor": [
            {"receipt": "R1", "vendor": "Hotel Lumière"},
            {"receipt": "R2", "vendor": "Spa Lumière"},
            {"receipt": "R3", "vendor": "Café Central"},
            {"receipt": "R4", "vendor": "Taxi"},
        ]},
    ),
    "card": (
        "Corporate card statement, March 2026, lines claimed for trip T-114\n"
        "C1 2026-03-05 HTL LUMIERE PARIS 612.00 EUR\n"
        "C2 2026-03-04 SPA LUMIERE 95.00 EUR\n"
        "C3 2026-03-05 TAXI G7 42.00 EUR\n"
        "C4 2026-03-09 Café Central, Vienna 23.00 EUR\n",
        {"expense_paid_to_vendor": [
            {"expense": "C1", "vendor": "HTL LUMIERE PARIS"},
            {"expense": "C2", "vendor": "SPA LUMIERE"},
            {"expense": "C3", "vendor": "TAXI G7"},
            {"expense": "C4", "vendor": "Café Central"},
        ],
         "expense_has_amount": [{"expense": e, "amount": a} for e, a in (("C1", 612), ("C2", 95), ("C3", 42), ("C4", 23))],
         "expense_incurred_on": [{"expense": e, "day": d} for e, d in
                                 (("C1", "2026-03-05"), ("C2", "2026-03-04"), ("C3", "2026-03-05"), ("C4", "2026-03-09"))],
         "expense_claimed_for_trip": [{"expense": e, "trip": "T-114"} for e in ("C1", "C2", "C3", "C4")]},
    ),
}

# A reviewer's identity decisions between the card statement's and the folio's vendor names.
DECISIONS = [
    ("same", "HTL LUMIERE PARIS", "Hotel Lumière", None, "Hotel Lumière"),
    ("same", "SPA LUMIERE", "Spa Lumière", None, "Spa Lumière"),
    ("unresolved", "TAXI G7", "Taxi", ("TAXI G7 (unresolved)", "Taxi (unresolved)"), None),
    ("different", "Café Central", "Café Central", None, None),
]
RENAME_DIFFERENT = {"Café Central": "Café Central, Vienna"}


def dump(path: Path, obj) -> bytes:
    raw = canonical_json_bytes(obj)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return raw


def gnd(run: Path, *args, ok=(0,)):
    proc = subprocess.run([sys.executable, "-m", "gnd", *args], cwd=run, capture_output=True, text=True)
    if proc.returncode not in ok:
        raise SystemExit(f"gnd {' '.join(args)} -> {proc.returncode}\n{proc.stdout}\n{proc.stderr}")
    return proc


def anchors_for(facts, text):
    rows = []
    for fact_type, items in facts.items():
        roles = [c["role"] for f in VOCABULARY["fact_types"] if f["id"] == fact_type for c in f.get("constraints", [])
                 if c["type"] == "anchored"]
        for row in items:
            for role in roles:
                value = row[role]
                start = text.index(value)
                rows.append({"fact_key": {"fact_type": fact_type, "roles": row}, "role": role,
                             "span": {"start": start, "end": start + len(value)}, "occurrence": 0,
                             "excerpt_sha256": sha256_hex(value.encode())})
    return rows


def main(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    for name in GENERATED:
        target = out / name
        if target.is_dir():
            shutil.rmtree(target)
    vocab = dump(out / "vocabulary/expense-travel.orm.json", VOCABULARY)
    catalog = dump(out / "reference/approved-vendors.json", CATALOG)
    include = [{"id": "travel", "path": "vocabulary/expense-travel.orm.json", "sha256": sha256_hex(vocab)}]
    refs = [{"id": "approved-vendors", "fact_types": ["approved_vendor"], "path": "reference/approved-vendors.json",
             "sha256": sha256_hex(catalog)}]
    base = {"version": 5, "source": SRC, "includes": include, "reference_populations": refs,
            "object_types": [], "fact_types": []}
    dump(out / "reading.orm.json", {**base, "model_id": "urn:gnd-example:expense-receipts-reading@1", "constraints": []})
    dump(out / "checking.orm.json", {**base, "model_id": "urn:gnd-example:expense-receipts-checking@1",
                                     "constraints": CHECKING_RULES})
    gnd(out, "validate", "reading.orm.json")
    gnd(out, "validate", "checking.orm.json")
    gnd(out, "extract", "reading.orm.json", "--out", "artifacts")
    stem = bundle_stem("reading.orm.json")
    index = json.loads((out / f"artifacts/{stem}.artifacts.json").read_text())
    reading = load_model(str(out / "reading.orm.json"))
    checking = load_model(str(out / "checking.orm.json"))
    populations = {}
    for name, (text, facts) in DOCUMENTS.items():
        src = out / "extracted" / name
        src.mkdir(parents=True)
        (src / "document.txt").write_text(text)
        pop = dump(src / "population.json", {"population": index["header_template"], "facts": facts})
        dump(src / "population.json.anchors.json", {
            "schema_version": 2, "population_sha256": sha256_hex(pop), "document_sha256": sha256_hex(text.encode()),
            "vocabulary_digest": vocabulary_digest(reading), "anchors": anchors_for(facts, text)})
        dump(src / "population.extraction.json", {
            "schema_version": 1, "model": "reading.orm.json", "model_sha256": index["model"]["sha256"],
            "population": "population.json", "population_sha256": sha256_hex(pop),
            "document": "document.txt", "document_sha256": sha256_hex(text.encode()),
            "projection_sha256": index["artifacts"][f"{stem}.projection.schema.json"]["sha256"],
            "skill": "gnd-extract", "skill_version": "1", "executing_model": "saved-example-reading"})
        gnd(out, "verify", "reading.orm.json", f"extracted/{name}/population.json", "--artifacts", "artifacts", ok=(0, 2))
        # Hand the verified reading to the checking model: same facts, checking header, rebound anchors.
        comp = out / "claim" / name
        comp.mkdir(parents=True)
        (comp / "document.txt").write_text(text)
        header = {**index["header_template"], "model": "checking.orm.json", "model_id": checking.model_id}
        rebound = dump(comp / "population.json", {"population": header, "facts": facts})
        anchors = json.loads((src / "population.json.anchors.json").read_text())
        anchors.update(population_sha256=sha256_hex(rebound), vocabulary_digest=vocabulary_digest(checking))
        anchor_raw = dump(comp / "population.json.anchors.json", anchors)
        validated = load_population_bytes(rebound, source="population.json", model=checking)
        bind_anchors(parse_anchor_sidecar(anchor_raw), checking, rebound, text.encode(), validated)
        populations[name] = (rebound, facts, anchors["anchors"])
    # Identity decisions and the manifest.
    card_raw, card_facts, card_anchors = populations["card"]
    folio_raw, folio_facts, folio_anchors = populations["folio"]

    def coordinate(key, source, fact_type, facts, anchors, value):
        rows = facts[fact_type]
        idx = next(i for i, r in enumerate(rows) if r["vendor"] == value)
        span = next(a["span"] for a in anchors if a["fact_key"]["roles"] == rows[idx] and a["role"] == "vendor")
        return {"key": key, "source": source, "fact_type": fact_type, "fact_index": idx, "role": "vendor", "span": span}

    decisions, renamings = [], []
    for i, (kind, card_value, folio_value, placeholders, target) in enumerate(DECISIONS):
        decisions.append({
            "decision": kind,
            "keys": [{"source": "card", "object_type": "vendor", "value": card_value},
                     {"source": "folio", "object_type": "vendor", "value": folio_value}],
            "evidence": [coordinate(0, "card", "expense_paid_to_vendor", card_facts, card_anchors, card_value),
                         coordinate(1, "folio", "receipt_issued_by_vendor", folio_facts, folio_anchors, folio_value)],
            "producer": {"kind": "reviewer", "id": "finance-reviewer"},
            "input_sha256": {"card": sha256_hex(card_raw), "folio": sha256_hex(folio_raw)},
            "placeholders": list(placeholders) if placeholders else None,
        })
        if kind == "same" and card_value != target:
            renamings.append({"source": "card", "fact_type": "expense_paid_to_vendor", "role": "vendor",
                              "from": card_value, "to": target, "decision": i})
        if kind == "unresolved":
            renamings.append({"source": "card", "fact_type": "expense_paid_to_vendor", "role": "vendor",
                              "from": card_value, "to": placeholders[0], "decision": i})
            renamings.append({"source": "folio", "fact_type": "receipt_issued_by_vendor", "role": "vendor",
                              "from": folio_value, "to": placeholders[1], "decision": i})
        if kind == "different":
            renamings.append({"source": "card", "fact_type": "expense_paid_to_vendor", "role": "vendor",
                              "from": card_value, "to": RENAME_DIFFERENT[card_value], "decision": i})
    resolution = dump(out / "claim/resolution.json",
                      {"schema": "gnd-resolution/1", "object_types": ["vendor"], "decisions": decisions})
    dump(out / "claim/manifest.json", {
        "schema": "gnd-composition-manifest/1", "sources": ["approval", "card", "folio"], "scope_tags": [],
        "deduplications": "identical-rows", "renamings": renamings,
        "resolution": {"path": "resolution.json", "sha256": sha256_hex(resolution)}})
    shutil.copytree(out / "claim", out / "claim-flat")
    (out / "claim-flat/resolution.json").unlink()
    dump(out / "claim-flat/manifest.json", {
        "schema": "gnd-composition-manifest/1", "sources": ["approval", "card", "folio"], "scope_tags": [],
        "deduplications": "identical-rows", "renamings": []})
    shutil.copytree(out / "claim", out / "claim-missing")
    raw = dump(out / "claim-missing/resolution.json",
               {"schema": "gnd-resolution/1", "object_types": ["vendor"], "decisions": decisions[:3]})
    dump(out / "claim-missing/manifest.json", {
        "schema": "gnd-composition-manifest/1", "sources": ["approval", "card", "folio"], "scope_tags": [],
        "deduplications": "identical-rows", "renamings": [r for r in renamings if r["decision"] < 3],
        "resolution": {"path": "resolution.json", "sha256": sha256_hex(raw)}})


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
