"""Public single-model consolidation candidate discovery."""

import json
from copy import deepcopy
from pathlib import Path

import pytest
from ruamel.yaml import YAML
from support.cli_runner import run_main


def corpus():
    fixture = Path(__file__).parent / "fixtures/unattended/conforming.orm.yaml"
    original = YAML(typ="safe").load(fixture)
    original["source"].pop("mode")
    original["source"].pop("reviewer")
    objects = original["object_types"]
    proto = next(x for x in objects if x["id"] == "order_no")
    for name in ("LatencyMs", "LatencySeconds", "WeightKg", "FailedOrderCount", "FailedPaymentCount", "SuccessCount"):
        objects.append(dict(deepcopy(proto), id=name.lower(), name=name))
    fact = original["fact_types"][0]
    single = deepcopy(fact)
    single.update(id="purchase_placed_by_customer", reading="{Order} is placed by {Customer}")
    single["sample_population"] = single["sample_population"][:1]
    single["provenance"]["sample_spans"] = single["provenance"]["sample_spans"][:1]
    fact["sample_population"][1]["customer"] = fact["sample_population"][0]["customer"]
    # One type has a single observed value across both facts.
    original["fact_types"].append(single)
    return original


def run(tmp_path, doc, *args):
    path = tmp_path / "model.json"
    path.write_text(json.dumps(doc))
    before = path.read_bytes()
    result = run_main(["consolidate", "candidates", str(path), *args])
    assert result.returncode == 0, (result.stderr, result.stdout)
    assert path.read_bytes() == before
    return json.loads(result.stdout)


def test_signals_and_controls(tmp_path):
    groups = run(tmp_path, corpus())["groups"]
    by_signal = {}
    for group in groups:
        by_signal.setdefault(group["signal"], []).append(group["members"])
    assert ["customer"] in by_signal["singleton"]
    assert ["order"] not in by_signal["singleton"]
    pair = ["order_placed_by_customer", "purchase_placed_by_customer"]
    assert pair in by_signal["role-players"]
    assert pair in by_signal["reading-shape"]
    assert ["latencyms", "latencyseconds"] in by_signal["unit"]
    assert ["failedordercount", "failedpaymentcount"] in by_signal["counted-noun"]
    assert ["customer", "customer_no"] in by_signal["near-name"]
    assert all("weightkg" not in members for members in by_signal["unit"])
    assert all("successcount" not in members for members in by_signal["counted-noun"])


def test_permutations_and_changed_source(tmp_path):
    doc = corpus()
    first = run(tmp_path, doc)
    for name in ("object_types", "fact_types"):
        doc[name].reverse()
    assert first == run(tmp_path, doc)
    item = doc["fact_types"][0]
    span = deepcopy(item["provenance"]["spans"][0])
    span["document_sha256"] = "a" * 64
    item["provenance"]["spans"].append(span)
    old = {g["group_id"]: g["evidence_sha256"] for g in first["groups"] if item["id"] in g["members"]}
    new = {g["group_id"]: g["evidence_sha256"] for g in run(tmp_path, doc)["groups"] if item["id"] in g["members"]}
    assert old.keys() == new.keys() and old and all(old[k] != new[k] for k in old)


@pytest.mark.parametrize("kind", ["items", "pairs"])
def test_budget_frontier(tmp_path, kind):
    doc = corpus()
    unrestricted = run(tmp_path, doc)
    needed = unrestricted["work"][kind]
    assert needed > 0
    assert run(tmp_path, doc, "--max-" + kind, str(needed)) == unrestricted
    limited = run(tmp_path, doc, "--max-" + kind, str(needed-1))
    assert not limited["complete"] and limited["reason"] == kind + "-limit"
    assert limited["work"][kind] < needed


def test_cross_document_shape_and_incompatible_players(tmp_path):
    doc = corpus()
    source, copied = doc["fact_types"][0], doc["fact_types"][-1]
    other = deepcopy(next(o for o in doc["object_types"] if o["id"] == "order"))
    other.update(id="booking", name="Booking")
    other["provenance"]["spans"][0]["document_sha256"] = "a" * 64
    doc["object_types"].append(other)
    copied["id"] = source["id"] + "s"
    copied["roles"][0]["object_type"] = "booking"
    copied["reading"] = "{Booking:order} is placed by {Customer}"
    pair = sorted([source["id"], copied["id"]])
    groups = {g["signal"]: g for g in run(tmp_path, doc)["groups"] if g["members"] == pair}
    assert "reading-shape" in groups and "near-name" in groups and "role-players" not in groups
    assert len({tuple(e["role_players"]) for e in groups["near-name"]["evidence"]}) == 2
    extra = deepcopy(other["provenance"]["spans"][0])
    extra["document_sha256"] = "b" * 64
    other["provenance"]["spans"].append(extra)
    assert all(g["members"] != pair or g["signal"] != "reading-shape" for g in run(tmp_path, doc)["groups"])


def test_explicit_units(tmp_path):
    doc = corpus()
    by_id = {o["id"]: o for o in doc["object_types"]}
    for key, unit in (("latencyms", "milliseconds"), ("latencyseconds", "seconds")):
        by_id[key]["reference"] = {"mode": "unit-based", "unit": unit, "measure_type": "duration"}
    matches = [g for g in run(tmp_path, doc)["groups"] if g["signal"] == "unit"]
    assert len(matches) == 1
    assert {e["unit"] for e in matches[0]["evidence"]} == {"milliseconds", "seconds"}


def test_invalid_model_reports_failure_without_traceback(tmp_path):
    path = tmp_path / "broken.yaml"
    path.write_text("[")
    result = run_main(["consolidate", "candidates", str(path)])
    assert result.returncode == 3
    assert b"Traceback" not in result.stderr


def test_value_free_evidence_survives_value_substitution(tmp_path):
    doc = corpus()
    first = run(tmp_path, doc)
    for fact in doc["fact_types"]:
        for row in fact.get("sample_population", []):
            for role in row:
                row[role] += 2000
    assert run(tmp_path, doc) == first


def test_pair_budget_counts_distinct_comparisons(tmp_path):
    types = [{"id": key, "kind": "value", "primitive": "Integer"} for key in ("distance_longitude", "distance_longitudes")]
    doc = {"version": 1, "object_types": types, "fact_types": []}
    report = run(tmp_path, doc, "--max-pairs", "1")
    assert report["work"]["pairs"] == 1 and report["complete"]


def test_unicode_equivalent_readings(tmp_path):
    doc = corpus()
    one, two = doc["fact_types"][0], doc["fact_types"][-1]
    one["reading"] += " in café"
    two["reading"] += " in cafe\u0301"
    assert sorted([one["id"], two["id"]]) in [
        g["members"] for g in run(tmp_path, doc)["groups"] if g["signal"] == "reading-shape"
    ]


def test_lexical_unit_controls(tmp_path):
    doc = corpus()
    proto = doc["object_types"][1]
    for name in ("TTLSeconds", "TTLMinutes", "Lag2Ms", "Lag2Seconds", "SizeS", "SizeM"):
        doc["object_types"].append(dict(deepcopy(proto), id=name.lower(), name=name))
    units = [g["members"] for g in run(tmp_path, doc)["groups"] if g["signal"] == "unit"]
    assert ["ttlminutes", "ttlseconds"] in units and ["lag2ms", "lag2seconds"] in units
    assert ["sizem", "sizes"] not in units


def test_explicit_unit_entity_without_lexical_suffix(tmp_path):
    doc = corpus()
    for name, unit in (("FirstDuration", "milliseconds"), ("SecondDuration", "seconds")):
        doc["object_types"].append({"id": name.lower(), "kind": "entity", "name": name,
            "reference": {"mode": "unit-based", "unit": unit, "measure_type": "duration"}})
    assert sorted(["firstduration", "secondduration"]) in [
        g["members"] for g in run(tmp_path, doc)["groups"] if g["signal"] == "unit"
    ]


def test_included_candidates_are_read_only_context(tmp_path):
    from hashlib import sha256

    doc = corpus()
    library = tmp_path / "library.json"
    library.write_text(json.dumps(doc))
    root = {"version": 5, "source": {"kind": "fixture"}, "includes": [
        {"id": "library", "path": library.name, "sha256": sha256(library.read_bytes()).hexdigest()}],
        "fact_types": [], "object_types": []}
    assert run(tmp_path, root)["groups"] == []
