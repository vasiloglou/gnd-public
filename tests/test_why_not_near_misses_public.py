"""NM3: near-misses on the public why-not surface (why-not-near-misses NM3 spec).

The /2 goldens were written before the NM3 code by
.gnd-planning/milestones/why-not-near-misses/evidence/NM3/build_goldens.py.
"""

from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path

import jsonschema
import pytest

from gnd import api, disclosure
from gnd.cli import main
from gnd.witness.view import why_not_view

ROOT = Path(__file__).resolve().parents[1]
FX = ROOT / "tests/fixtures/why_not"
GOLDENS = FX / "goldens"
EXAMPLE = ROOT / "src/gnd/examples/quoted_claims"
SPELLING = FX / "spelling"
CASES = json.loads((FX / "cases.json").read_text())
SCHEMA = json.loads((ROOT / "src/gnd/why-not.schema.json").read_text())
VALIDATOR = jsonschema.Draft202012Validator(SCHEMA)
NEAR = ("near_miss_count", "near_miss_truncated", "near_misses")
BASE = "23e4a99"
G20 = [str(SPELLING / "model.orm.json"), str(SPELLING / "spelling-gap.pop.json"),
       "--fact-type", "certified", "--row", str(SPELLING / "claim.json")]
VALUES = ("FIELD NOTES", "Field notes", "Field Notes", "Ada Byrne", "Bo Lin", "Letters Home")
PAIR = {"roles": ["work"],
        "sample": {"person": "Ada Byrne", "work": "Field Notes"},
        "candidate": {"person": "Ada Byrne", "work": "FIELD NOTES"}}


def golden(name):
    return json.loads((GOLDENS / f"{name}.json").read_text())


def blockers(payload):
    for clause in payload["clauses"]:
        yield clause["blocker"]
        if clause["descent"] is not None:
            yield from blockers(clause["descent"])


def run_cli(argv, capsys):
    capsys.readouterr()
    code = main(argv)
    captured = capsys.readouterr()
    return code, captured.out


# -- T1: census over the WN2 corpus (NM-R1, NM1-Q3) ------------------------------

@pytest.mark.parametrize("case", [c for c in CASES if c["id"] != "g20-spelling-gap"],
                         ids=lambda case: case["id"])
@pytest.mark.parametrize("view", ["", ".raw"])
def test_t1_census_adds_only_the_version_and_empty_near_misses(case, view):
    new = golden(f"{case['id']}{view}")
    old = json.loads(subprocess.run(
        ["git", "show", f"{BASE}:tests/fixtures/why_not/goldens/{case['id']}{view}.json"],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout)
    assert new["schema_version"] == "gnd-why-not/2"
    for blocker in blockers(new):
        if blocker["kind"] == "atom":
            shown = [] if view else "redacted"
            assert (blocker.pop("near_miss_count"), blocker.pop("near_miss_truncated"),
                    blocker.pop("near_misses")) == (0, False, shown)
        else:
            assert not set(NEAR) & set(blocker)
    new["schema_version"] = "gnd-why-not/1"
    assert new == old


def test_t2_spelling_fixture_copies_equal_the_example():
    for name in ("model.orm.json", "spelling-gap.pop.json", "claim.json"):
        assert (SPELLING / name).read_bytes() == (EXAMPLE / name).read_bytes()


# -- T3, T4: g20 in both views ---------------------------------------------------

def test_t3_g20_raw_reports_one_spelling_near_miss():
    found = golden("g20-spelling-gap.raw")["clauses"][0]["blocker"]
    assert (found["kind"], found["index"], found["fact_type"]) == ("atom", 1, "authored")
    assert (found["near_miss_count"], found["near_miss_truncated"]) == (1, False)
    assert found["near_misses"] == [PAIR]


def test_t4_g20_redacted_view_keeps_counts_and_no_values(capsys):
    code, out = run_cli(["why-not", *G20], capsys)
    assert code == 0
    found = json.loads(out)["clauses"][0]["blocker"]
    assert (found["near_miss_count"], found["near_miss_truncated"], found["near_misses"]) == (
        1, False, "redacted")
    assert not [value for value in VALUES if value in out]


# -- T5: the disclosure mode over g20 --------------------------------------------

def _api_g20():
    return api.why_not(G20[0], G20[1], "certified", row_path=G20[5])


def test_t5_api_follows_the_mode(monkeypatch):
    raw = golden("g20-spelling-gap.raw")
    raw.pop("view")
    monkeypatch.delenv("GND_DISCLOSURE", raising=False)
    assert _api_g20() == raw
    monkeypatch.setenv("GND_DISCLOSURE", "internal")
    assert _api_g20() == raw
    monkeypatch.setenv("GND_DISCLOSURE", "customer")
    assert _api_g20() == golden("g20-spelling-gap")


def test_t5_cli_follows_the_mode(monkeypatch, capsys):
    monkeypatch.delenv("GND_DISCLOSURE", raising=False)
    code, out = run_cli(["--disclosure", "internal", "why-not", *G20], capsys)
    assert (code, out) == (0, (GOLDENS / "g20-spelling-gap.raw.json").read_text())
    monkeypatch.setenv("GND_DISCLOSURE", "customer")
    code, out = run_cli(["why-not", *G20, "--raw"], capsys)
    assert (code, out) == (3, "")


# -- T6, T7: schema --------------------------------------------------------------

def test_t6_schema_accepts_every_golden_and_the_mode_payloads(monkeypatch):
    for path in sorted(GOLDENS.glob("*.json")):
        VALIDATOR.validate(json.loads(path.read_text()))
    for mode in ("internal", "customer"):
        monkeypatch.setenv("GND_DISCLOSURE", mode)
        VALIDATOR.validate(_api_g20())


def _blocker(payload, path=(0,)):
    clause = payload["clauses"][path[0]]
    for index in path[1:]:
        clause = clause["descent"]["clauses"][index]
    return clause["blocker"]


def _mutated(name, edit, path=(0,)):
    payload = golden(name)
    edit(payload, _blocker(payload, path))
    return payload


def _pairs(n):
    return [{**PAIR, "candidate": {**PAIR["candidate"], "work": f"FIELD NOTES {i}"}}
            for i in range(n)]


NEGATIVES = {
    "N1 raw list under view redacted": lambda: _mutated(
        "g20-spelling-gap", lambda p, b: b.update(near_misses=[PAIR])),
    "N2 raw list in a nested redacted descent": lambda: _mutated(
        "g2-row-descent", lambda p, b: b.update(near_misses=[]), (0, 0)),
    "N3 count missing": lambda: _mutated(
        "g20-spelling-gap.raw", lambda p, b: b.pop("near_miss_count")),
    "N4 truncated missing": lambda: _mutated(
        "g20-spelling-gap.raw", lambda p, b: b.pop("near_miss_truncated")),
    "N5 list missing": lambda: _mutated(
        "g20-spelling-gap.raw", lambda p, b: b.pop("near_misses")),
    "N6 count on a negated blocker": lambda: _mutated(
        "g15-negated.raw", lambda p, b: b.update(near_miss_count=0)),
    "N7 count 0 with one pair": lambda: _mutated(
        "g20-spelling-gap.raw", lambda p, b: b.update(near_miss_count=0)),
    "N8 six pairs": lambda: _mutated(
        "g20-spelling-gap.raw", lambda p, b: b.update(near_miss_count=6, near_misses=_pairs(6))),
    "N9 count 3 with one pair": lambda: _mutated(
        "g20-spelling-gap.raw", lambda p, b: b.update(near_miss_count=3)),
    "N10 empty roles": lambda: _mutated(
        "g20-spelling-gap.raw", lambda p, b: b.update(near_misses=[{**PAIR, "roles": []}])),
    "N11 an extra pair key": lambda: _mutated(
        "g20-spelling-gap.raw", lambda p, b: b.update(near_misses=[{**PAIR, "x": 1}])),
    "N12 version 1": lambda: {**golden("g20-spelling-gap.raw"), "schema_version": "gnd-why-not/1"},
}


# Each negative's unmutated golden, which must be valid, so a negative cannot pass
# because the base payload was already rejected.
BASE_OF = {name: ("g2-row-descent" if name.startswith("N2 ") else
                  "g15-negated.raw" if name.startswith("N6 ") else
                  "g20-spelling-gap" if name.startswith("N1 ") else "g20-spelling-gap.raw")
           for name in NEGATIVES}


@pytest.mark.parametrize("name", NEGATIVES)
def test_t7_schema_refuses_each_negative(name):
    VALIDATOR.validate(golden(BASE_OF[name]))
    assert not VALIDATOR.is_valid(NEGATIVES[name]())


@pytest.mark.parametrize("name, edit", [
    ("five pairs, count 5", lambda p, b: b.update(near_miss_count=5, near_misses=_pairs(5))),
    ("five pairs, count 9", lambda p, b: b.update(near_miss_count=9, near_misses=_pairs(5))),
    ("truncated", lambda p, b: b.update(near_miss_truncated=True)),
])
def test_t7_controls_are_valid(name, edit):
    VALIDATOR.validate(_mutated("g20-spelling-gap.raw", edit))


# -- T9: the view projection -----------------------------------------------------

def test_t9_view_keeps_truncation_and_never_adds_fields():
    payload = golden("g20-spelling-gap.raw")
    clause = payload["clauses"][0]
    clause["blocker"].update(near_miss_count=9, near_miss_truncated=True, near_misses=_pairs(5))
    negated = copy.deepcopy(golden("g15-negated.raw")["clauses"][0])
    payload["clauses"].append({**negated, "clause_index": 1})
    viewed = why_not_view(payload)
    first, second = (c["blocker"] for c in viewed["clauses"])
    assert (first["near_miss_count"], first["near_miss_truncated"], first["near_misses"]) == (
        9, True, "redacted")
    assert not set(NEAR) & set(second)


# -- T10: DisclosureRefused from gnd.api (D4) ------------------------------------

def test_t10_disclosure_refused_is_public():
    assert api.DisclosureRefused is disclosure.DisclosureRefused
    assert "DisclosureRefused" in api.__all__
    assert api.__all__[api.__all__.index("why_not") + 1] == "DisclosureRefused"
    assert disclosure.SURFACES["api:DisclosureRefused"].kind == "value-free"


# -- T11: rule mode over the spelling-gap population -----------------------------

def test_t11_rule_mode_blocks_at_reviewed_without_near_misses():
    payload = api.why_not(G20[0], G20[1], "certified")
    assert (payload["exit_code"], payload["status"]) == (0, "blocked")
    found = payload["clauses"][0]["blocker"]
    assert found["fact_type"] == "reviewed"
    assert (found["near_miss_count"], found["near_miss_truncated"], found["near_misses"]) == (
        0, False, [])
