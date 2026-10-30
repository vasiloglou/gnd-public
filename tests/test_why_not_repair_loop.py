"""WN3: a host repairs a missing claim using only why-not's payload (issue #66).

The loop holds the model, a population with two missing base facts and one
claimed row. It asks why-not, builds the missing fact from the payload alone
(fact type, role map, raw sample) plus an extracted table for roles no binding
reaches, and asks again until the row derives and a witness proves it.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gnd import api

EXAMPLE = Path(__file__).resolve().parents[1] / "src/gnd/examples/quoted_claims"
MODEL = EXAMPLE / "model.orm.json"
CLAIM = EXAMPLE / "claim.json"
EXTRACTED = json.loads((EXAMPLE / "extracted.json").read_text())


def population(tmp_path, name, extra):
    document = json.loads((EXAMPLE / "gap.pop.json").read_text())
    for fact_type, row in extra:
        document["facts"].setdefault(fact_type, []).append(row)
    path = tmp_path / name
    path.write_text(json.dumps(document))
    return path


def why_not(path):
    return api.why_not(MODEL, path, "certified", row_path=CLAIM)


def blocker(payload):
    (clause,) = payload["clauses"]
    return clause["blocker"]


def key(payload):
    found = blocker(payload)
    return found["kind"], found["index"], found["fact_type"]


def repair(payload):
    """The missing fact, from the payload alone plus the extracted table."""
    found = blocker(payload)
    bound = {role for role, spec in found["roles"].items() if spec.get("bound")}
    extracted = EXTRACTED.get(found["fact_type"], {})
    # The extracted table only supplies roles no binding reaches.
    assert not bound & set(extracted)
    sample = found["samples"][0]
    row = {role: sample[role] if role in bound else extracted[role] for role in found["roles"]}
    return found["fact_type"], row


def check_verdict(path):
    report = api.check(MODEL, path)
    (verdict,) = [d for d in report["derivations"] if d["derivation_ref"] == "derivation:certified"]
    return report["exit_code"], verdict["verdict"]


def test_two_gap_repair_loop(tmp_path):
    gap = EXAMPLE / "gap.pop.json"
    # Before repair: check passes (the population asserts no certified rows,
    # and none derive) while the claimed row is absent.
    assert check_verdict(gap) == (0, "pass")
    assert [r["status"] for r in api.witness(MODEL, gap, CLAIM)["results"]] == ["missing"]

    first = why_not(gap)
    assert (first["exit_code"], first["status"]) == (0, "blocked")
    assert key(first) == ("atom", 1, "authored")
    assert blocker(first)["ground"] is True
    # Gap 1 has a bound role whose value comes only from the sample.
    assert blocker(first)["samples"][0]["work"] == "Field Notes"
    fact_1 = repair(first)
    assert fact_1 == ("authored", {"work": "Field Notes", "person": "Ada Byrne"})

    once = population(tmp_path, "once.pop.json", [fact_1])
    second = why_not(once)
    assert (second["exit_code"], second["status"]) == (0, "blocked")
    assert key(second) == ("atom", 2, "reviewed")
    assert blocker(second)["roles"]["reviewer"] == {"variable": "$r", "bound": False}
    fact_2 = repair(second)
    assert fact_2 == ("reviewed", {"work": "Field Notes", "reviewer": "Cora Lind"})

    twice = population(tmp_path, "twice.pop.json", [fact_1, fact_2])
    done = why_not(twice)
    assert (done["exit_code"], done["status"]) == (0, "derived")
    proved = api.witness(MODEL, twice, CLAIM)
    assert proved["exit_code"] == 0 and proved["results"][0]["status"] == "proved"
    certificate = tmp_path / "certificate.json"
    certificate.write_text(json.dumps(proved["certificate"]))
    assert api.replay(MODEL, twice, certificate)["exit_code"] == 0
    # Review WN3-R2: the population covers certified, so once the row derives
    # check fails until the row is asserted too.
    assert check_verdict(twice) == (1, "fail")
    asserted = population(tmp_path, "asserted.pop.json",
                          [fact_1, fact_2, ("certified", {"quote": "q-17", "person": "Ada Byrne"})])
    assert check_verdict(asserted) == (0, "pass")


@pytest.mark.parametrize("name, extra", [
    # The repair's values written onto the previous step's predicate, positionally.
    ("previous-predicate", [("quote", {"quote": "Field Notes", "work": "Ada Byrne"})]),
    # The right predicate with a wrong bound value.
    ("wrong-bound-value", [("authored", {"work": "Letters Home", "person": "Ada Byrne"})]),
])
def test_negative_controls_leave_the_blocker_unchanged(tmp_path, name, extra):
    before = why_not(EXAMPLE / "gap.pop.json")
    after = why_not(population(tmp_path, f"{name}.pop.json", extra))
    assert (after["exit_code"], after["status"]) == (0, "blocked")
    assert key(after) == key(before) == ("atom", 1, "authored")
