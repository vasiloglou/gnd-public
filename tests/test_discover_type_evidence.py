"""TS1: ``gnd discover --type-evidence`` writes the evidence the judgement skills read."""

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import jsonschema
import pytest

from gnd.artifacts import canonical_json_bytes

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "src/gnd/type-evidence.schema.json").read_text())
CANARY = "colour-7f3a"


def digest_of(value):
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


SIZE_DIGEST = digest_of("size")
HEADER = """version: 2
model_id: urn:gnd-fixture:ts1-evidence@1
source: {kind: text-conversation, confidence: standard, mode: one-shot}
object_types:
  - {id: item, name: Item, kind: value, primitive: String}
  - {id: attribute_name, name: AttributeName, kind: value, primitive: String}
  - {id: attribute_value, name: AttributeValue, kind: value, primitive: String}
  - {id: shelf, name: Shelf, kind: value, primitive: String}
fact_types:
  - id: item_has_attribute
    reading: "{Item} has attribute {AttributeName} with value {AttributeValue}"
    roles:
      - {object_type: item, role_name: item}
      - {object_type: attribute_name, role_name: name}
      - {object_type: attribute_value, role_name: value}
    provenance:
      generic: {entity: item, attribute: name, value: value}
"""
INDUCED = """  - id: item_has_attribute_induced_0
    reading: "{Item} has induced item_has_attribute attribute 0 {AttributeValue}"
    roles: [{object_type: item, role_name: entity}, {object_type: attribute_value, role_name: value}]
    provenance:
      induced_from: %(origin)s
  - id: item_is_on_shelf_at
    reading: "{Item} is on {Shelf} at {AttributeValue}"
    inverse_reading: "{Shelf} holds {Item} at {AttributeValue}"
    roles:
      - {object_type: item, role_name: item}
      - {object_type: shelf, role_name: shelf}
      - {object_type: attribute_value, role_name: slot}
  - id: item_has_label
    reading: "{Item} has label {AttributeValue}"
    roles: [{object_type: item, role_name: item}, {object_type: attribute_value, role_name: label}]
"""
FOOTER = "constraints: []\nrejected_proposals: []\n"
ORIGIN = f"{{generic: item_has_attribute, attribute_sha256: {SIZE_DIGEST}}}"


def generic_rows(n=24):
    out = [{"item": f"I-{i:02d}", "name": "size", "value": f"s{i}"} for i in range(n)]
    out += [{"item": f"I-{i:02d}", "name": CANARY, "value": f"c{i}"} for i in range(n)]
    out += [{"item": f"I-{i:02d}", "name": "tag", "value": f"t{i}"} for i in range(n)]
    out += [{"item": "I-00", "name": "tag", "value": "t-extra"}, {"item": "I-01", "name": "tag", "value": "t1"}]
    out += [{"item": f"I-{i:02d}", "name": "rare", "value": f"r{i}"} for i in range(3)]
    return out


def build(tmp_path, *, origin=ORIGIN, induced=True, redact=False, facts=None):
    text = HEADER + (INDUCED % {"origin": origin} if induced else "") + FOOTER
    if redact:
        text = text.replace("{object_type: attribute_name, role_name: name}",
                            "{object_type: attribute_name, role_name: name, redact: true}", 1)
    model = tmp_path / "model.orm.yaml"
    model.write_text(text)
    all_facts = {"item_has_attribute": generic_rows() if facts is None else facts}
    if induced:
        all_facts["item_has_attribute_induced_0"] = [{"entity": f"I-{i:02d}", "value": f"s{i}"} for i in range(24)]
        all_facts["item_is_on_shelf_at"] = [{"item": f"I-{i:02d}", "shelf": "A", "slot": f"x{i}"} for i in range(10)]
        all_facts["item_has_label"] = [{"item": f"J-{i:02d}", "label": f"s{i}"} for i in range(24)]
    population = tmp_path / "items.population.json"
    population.write_text(json.dumps({
        "population": {"model": "model.orm.yaml", "source": "fixture", "covers": sorted(all_facts)},
        "instances": {}, "facts": all_facts,
    }))
    return model, population


def discover(cwd, *extra, env=None, name="run", evidence="run.evidence.json", families="fact-type"):
    """Run in ``cwd`` with relative paths, so two directories give comparable bytes."""
    argv = [sys.executable, "-m", "gnd", "discover", "model.orm.yaml", "items.population.json",
            "--out", f"{name}.proposal.json", "--report", f"{name}.report.json", "--actor", "test",
            "--requested-at", "2026-11-05T00:00:00+00:00", "--families", families, "--format", "json",
            *([] if evidence is None else ["--type-evidence", evidence]), *extra]
    base = {k: v for k, v in os.environ.items() if k != "GND_DISCLOSURE"}
    run = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, check=False, env={**base, **(env or {})})
    return run, cwd / f"{name}.proposal.json", cwd / f"{name}.report.json", (None if evidence is None else cwd / evidence)


def load(path):
    document = json.loads(path.read_text())
    jsonschema.validate(document, SCHEMA)  # T18: every written evidence validates
    return document


def by_value(document):
    return {group["value"]: group for group in document["groups"]}


@pytest.fixture
def shown(tmp_path):
    build(tmp_path)
    run, _out, report, evidence = discover(tmp_path, "--show-values")
    assert run.returncode == 0, run.stderr
    return load(evidence), json.loads(report.read_text())["fact_type_proposals"]


# T1, T2
def test_every_group_once_with_the_reports_counts(shown):
    document, family = shown
    statuses = [group["status"] for group in document["groups"]]
    assert [group["group"] for group in document["groups"]] == [f"g{n}" for n in range(len(statuses))]
    assert statuses.count("below_support") == family["skipped"]["below_support"] == 1
    assert statuses.count("multi_valued") == family["skipped"]["multi_valued"] == 1
    assert statuses.count("shape_match") == len(family["shape_matches"]) == 2
    assert statuses.count("proposed") == len(family["proposed"]) == 0
    # Family order: groups are formed in first-appearance order of the attribute.
    assert [group["value"] for group in document["groups"]] == ["size", CANARY, "tag", "rare"]
    assert by_value(document)["size"]["signature"] == '["attribute_value","item"]'
    assert by_value(document)["rare"]["signature"] is None


def test_proposed_and_over_budget_statuses(tmp_path, monkeypatch):
    from gnd.discover import service, type_evidence

    model, population = build(tmp_path, induced=False)
    monkeypatch.setattr(service, "MAX_EVOLUTION_PROPOSAL_BYTES", service.BUDGET_MARGIN + 2 * len(model.read_bytes()) + 4000)
    result = service.discover(model, population, families=("fact-type",), max_values=20, max_pairs=256)
    proposals = result["type_proposals"]
    document = type_evidence.build_evidence(
        result["view"], proposals, model_sha256="0" * 64, population_sha256="0" * 64, min_support=20,
        show_values=True, show_digests=True, redacted_generics=[])
    jsonschema.validate(document, SCHEMA)
    groups = by_value(document)
    assert groups["size"]["status"] == "proposed" and groups["size"]["fact_type"] == "item_has_attribute_induced_0"
    assert groups[CANARY]["status"] == "over_budget" and groups[CANARY]["fact_type"] is None
    assert result["fields"]["fact_type_proposals"]["skipped"]["over_budget"] == 1


def test_a_mixed_type_group(tmp_path):
    # A validated population cannot hold two JSON types in one typed role (CT4-C2).
    from gnd.discover import type_evidence, types
    from gnd.discover.support import PopulationView, Work
    from gnd.model import load_model
    from gnd.population import load_population

    facts = [{"item": f"I-{i:02d}", "name": "mixed", "value": (i if i % 2 else f"v{i}")} for i in range(25)]
    model, population = build(tmp_path, induced=False, facts=facts)
    view = PopulationView(load_model(model), load_population(population), Work())
    found = types.propose(view, ["item_has_attribute"], min_support=20, show_values=False,
                          redacted=frozenset(), envelope={})
    document = type_evidence.build_evidence(view, found, model_sha256="0" * 64, population_sha256="0" * 64,
                                            min_support=20, show_values=False, show_digests=True,
                                            redacted_generics=[])
    jsonschema.validate(document, SCHEMA)
    [group] = document["groups"]
    assert group["status"] == "mixed_type" and group["value_primitive"] is None and group["signature"] is None


# T3, T4
def test_candidates_and_overlaps(shown):
    document, _family = shown
    size = by_value(document)["size"]
    candidates = {c["fact_type"]: c for c in size["candidates"]}
    assert list(candidates) == ["item_has_attribute_induced_0", "item_is_on_shelf_at", "item_has_label"]
    induced = candidates["item_has_attribute_induced_0"]
    assert induced["signature_equal"] is True and induced["rows"] == 24
    assert induced["overlap"] == {"entities": 24, "pairs": 24}
    assert candidates["item_has_label"]["signature_equal"] is True
    assert candidates["item_has_label"]["overlap"] == {"entities": 0, "pairs": 0}
    shelf = candidates["item_is_on_shelf_at"]
    assert shelf["overlap"] == {"entities": 10, "pairs": None} and shelf["signature_equal"] is False
    assert shelf["readings"] == ["{Item} is on {Shelf} at {AttributeValue}", "{Shelf} holds {Item} at {AttributeValue}"]
    assert by_value(document)[CANARY]["candidates"][0]["overlap"] == {"entities": 24, "pairs": 0}


# T5
def test_multi_valued_counts(shown):
    tag = by_value(shown[0])["tag"]
    assert tag["status"] == "multi_valued" and tag["multi"] == {"entities": 1, "max": 2}
    assert tag["exact_repeats"] == 1 and tag["rows"] == 26 and tag["support"] == 24
    assert tag["value_primitive"] == "String" and tag["signature"] is None
    assert len(tag["row_ids"]) == 26 and tag["row_ids"][0] == "ft0#48"


def test_row_ids_are_capped(tmp_path):
    facts = [{"item": f"I-{i:02d}", "name": "size", "value": f"s{i}"} for i in range(40)]
    build(tmp_path, induced=False, facts=facts)
    _run, _out, _report, evidence = discover(tmp_path)
    [group] = load(evidence)["groups"]
    assert group["rows"] == 40 and len(group["row_ids"]) == 32


# T6
def test_a_redacted_attribute_role_forms_no_group(tmp_path):
    build(tmp_path, redact=True)
    run, _out, _report, evidence = discover(tmp_path)
    assert run.returncode == 0, run.stderr
    document = load(evidence)
    assert document["groups"] == [] and document["redacted_generics"] == ["item_has_attribute"]


# T7, T7b
@pytest.mark.parametrize("mode", ["internal", "customer"])
def test_origin_is_read_back(tmp_path, mode):
    build(tmp_path)
    run, _out, _report, evidence = discover(tmp_path, env={"GND_DISCLOSURE": mode})
    assert run.returncode == 0, run.stderr
    groups = load(evidence)["groups"]
    size, colour = groups[0], groups[1]
    assert size["candidates"][0]["origin"]["same_attribute"] is True
    assert colour["candidates"][0]["origin"]["same_attribute"] is False
    assert size["candidates"][1]["origin"] is None
    if mode == "internal":
        assert size["candidates"][0]["origin"]["attribute_sha256"] == SIZE_DIGEST
        assert size["attribute_sha256"] == SIZE_DIGEST
    else:
        assert "attribute_sha256" not in size["candidates"][0]["origin"] and "attribute_sha256" not in size
        assert SIZE_DIGEST not in evidence.read_text()


# T8
@pytest.mark.parametrize("bad", [
    "[item_has_attribute]",
    "size",
    "{generic: item_has_attribute}",
    f"{{generic: item_has_attribute, attribute_sha256: {SIZE_DIGEST}, extra: 1}}",
    "{generic: item_has_attribute, attribute_sha256: abc}",
    f"{{generic: 7, attribute_sha256: {SIZE_DIGEST}}}",
    "{generic: item_has_attribute, attribute_sha256: {nested: 1}}",
    "12",
])
def test_a_malformed_origin_exits_3_and_writes_nothing(tmp_path, bad):
    build(tmp_path, origin=bad)
    run, out, report, evidence = discover(tmp_path)
    assert run.returncode == 3, run.stdout + run.stderr
    assert "item_has_attribute_induced_0: invalid induced_from" in run.stderr
    assert "Traceback" not in run.stderr
    assert not out.exists() and not report.exists() and not evidence.exists()


def test_a_malformed_origin_is_ignored_without_the_option(tmp_path):
    build(tmp_path, origin="[x]")
    run, *_ = discover(tmp_path, evidence=None)
    assert run.returncode == 0, run.stderr


# T9, T9b
@pytest.mark.parametrize(("mode", "flag", "code", "present"), [
    (None, False, 0, False), ("customer", False, 0, False), ("internal", False, 0, True),
    (None, True, 0, True), ("customer", True, 3, None),
])
def test_values_follow_the_disclosure_mode(tmp_path, mode, flag, code, present):
    build(tmp_path)
    run, _out, _report, evidence = discover(tmp_path, *(["--show-values"] if flag else []),
                                            env={} if mode is None else {"GND_DISCLOSURE": mode})
    assert run.returncode == code, run.stderr
    if present is None:
        assert not evidence.exists()
        return
    text = evidence.read_text()
    assert (CANARY in text) is present and load(evidence)["show_values"] is present


def test_customer_evidence_carries_no_attribute_digest(tmp_path):
    build(tmp_path)
    run, _out, _report, evidence = discover(tmp_path, env={"GND_DISCLOSURE": "customer"})
    assert run.returncode == 0, run.stderr
    document = load(evidence)
    assert document["show_digests"] is False
    hexes = set(re.findall(r"[0-9a-f]{64}", evidence.read_text()))
    assert hexes == {document["model_sha256"], document["population_sha256"]}
    for value in ("size", CANARY, "tag", "rare"):
        assert digest_of(value) not in hexes


# T10..T13
def test_the_option_needs_the_family(tmp_path):
    build(tmp_path)
    run, *_ = discover(tmp_path, families="uniqueness")
    assert run.returncode == 64
    assert "--type-evidence need --families fact-type" in run.stderr


@pytest.mark.parametrize("same", ["run.proposal.json", "run.report.json", "model.orm.yaml", "items.population.json"])
def test_the_evidence_path_must_differ(tmp_path, same):
    build(tmp_path)
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    run, *_ = discover(tmp_path, evidence=same)
    assert run.returncode == 64
    assert "five different paths" in run.stderr
    assert {p.name: p.read_bytes() for p in tmp_path.iterdir()} == before


def test_an_existing_evidence_file_is_refused_before_the_model_is_read(tmp_path):
    model, _population = build(tmp_path)
    (tmp_path / "run.evidence.json").write_text("old")
    run, out, report, evidence = discover(tmp_path)
    assert run.returncode == 11 and evidence.read_text() == "old"
    assert not out.exists() and not report.exists()
    model.write_text("not: [a model")
    assert discover(tmp_path)[0].returncode == 11


def test_a_symlinked_evidence_path_is_refused(tmp_path):
    build(tmp_path)
    target = tmp_path / "elsewhere.json"
    (tmp_path / "run.evidence.json").symlink_to(target)
    run, out, report, _evidence = discover(tmp_path)
    assert run.returncode == 74 and not target.exists()
    assert not out.exists() and not report.exists()


# T14
def test_the_cap_trims_candidates_from_the_tail(tmp_path, monkeypatch):
    from gnd.discover import service, type_evidence

    model, population = build(tmp_path)
    def run(name):
        return service._cmd_discover(str(model), str(population), out=str(tmp_path / f"{name}.p.json"),
                                     report=str(tmp_path / f"{name}.r.json"), actor="test",
                                     requested_at=datetime(2026, 11, 5, tzinfo=UTC), families=("fact-type",),
                                     max_values=20, max_pairs=256, output_format="text",
                                     type_evidence=str(tmp_path / f"{name}.e.json"))
    assert run("full") == 0
    full = load(tmp_path / "full.e.json")
    size = len((tmp_path / "full.e.json").read_bytes())
    monkeypatch.setattr(type_evidence, "MAX_EVIDENCE_BYTES", size - 200)
    assert run("trimmed") == 0
    trimmed = load(tmp_path / "trimmed.e.json")
    assert len((tmp_path / "trimmed.e.json").read_bytes()) <= size - 200
    assert trimmed["truncated"] > 0
    kept = sum(len(g["candidates"]) for g in trimmed["groups"])
    assert kept + trimmed["truncated"] == sum(len(g["candidates"]) for g in full["groups"])
    assert trimmed["groups"][0]["candidates"] == full["groups"][0]["candidates"]  # the tail goes first
    monkeypatch.setattr(type_evidence, "MAX_EVIDENCE_BYTES", 100)
    assert run("overflow") == 70
    assert not (tmp_path / "overflow.r.json").exists()


# T14b
def test_written_bytes_trimming_marks_over_budget(tmp_path, monkeypatch):
    from gnd.discover import service

    facts = [{"item": f"I-{i:02d}", "name": f"attr-{a:03d}", "value": f"v{i}"} for a in range(60) for i in range(20)]
    model, population = build(tmp_path, induced=False, facts=facts)
    def run(name):
        return service._cmd_discover(str(model), str(population), out=str(tmp_path / f"{name}.p.json"),
                                     report=str(tmp_path / f"{name}.r.json"), actor="test",
                                     requested_at=datetime(2026, 11, 5, tzinfo=UTC), families=("fact-type",),
                                     max_values=20, max_pairs=256, output_format="text",
                                     type_evidence=str(tmp_path / f"{name}.e.json"))
    assert run("full") == 0
    cap = len((tmp_path / "full.p.json").read_bytes()) // 2
    monkeypatch.setattr(service, "MAX_EVOLUTION_PROPOSAL_BYTES", cap)
    monkeypatch.setattr(service, "BUDGET_MARGIN", -10 * cap)
    assert run("capped") == 0
    family = json.loads((tmp_path / "capped.r.json").read_text())["fact_type_proposals"]
    document = load(tmp_path / "capped.e.json")
    proposed = [g["fact_type"] for g in document["groups"] if g["status"] == "proposed"]
    assert proposed == [entry["fact_type"] for entry in family["proposed"]]
    assert sum(g["status"] == "over_budget" for g in document["groups"]) == family["skipped"]["over_budget"] > 0
    assert all(g["fact_type"] is None for g in document["groups"] if g["status"] == "over_budget")


# T16
@pytest.mark.parametrize("mode", [None, "internal", "customer"])
@pytest.mark.parametrize("variant", ["main", "plain", "redacted"])
def test_the_option_leaves_the_other_outputs_unchanged(tmp_path, mode, variant):
    left, right = tmp_path / "left", tmp_path / "right"
    for side in (left, right):
        side.mkdir()
        build(side, induced=variant != "plain", redact=variant == "redacted")
    env = {} if mode is None else {"GND_DISCLOSURE": mode}
    with_run, with_out, with_report, _ = discover(left, env=env)
    without_run, without_out, without_report, _ = discover(right, env=env, evidence=None)
    assert with_run.returncode == without_run.returncode == 0, with_run.stderr + without_run.stderr
    assert with_report.read_bytes() == without_report.read_bytes()
    assert with_run.stdout == without_run.stdout
    assert with_out.exists() == without_out.exists()
    if with_out.exists():
        assert with_out.read_bytes() == without_out.read_bytes()
    assert sorted(p.name for p in left.iterdir()) == sorted([*(p.name for p in right.iterdir()), "run.evidence.json"])


# T19
def test_evidence_is_written_when_nothing_is_proposed(tmp_path):
    build(tmp_path)
    run, out, report, evidence = discover(tmp_path)
    assert run.returncode == 0, run.stderr
    assert not out.exists() and json.loads(report.read_text())["proposal"] is None
    assert load(evidence)["groups"]


def test_the_evidence_binds_the_input_digests(tmp_path):
    model, population = build(tmp_path)
    document = load(discover(tmp_path)[3])
    assert document["model_sha256"] == hashlib.sha256(model.read_bytes()).hexdigest()
    assert document["population_sha256"] == hashlib.sha256(population.read_bytes()).hexdigest()
    assert document["min_support"] == 20 and document["format"] == "gnd-type-evidence/1"


# T20
def test_evidence_time_is_bounded(tmp_path):
    from gnd.discover import service

    extra = "".join(
        f"  - id: item_fact_{k}\n    reading: \"{{Item}} fact {k} {{AttributeValue}}\"\n"
        f"    roles: [{{object_type: item, role_name: item}}, {{object_type: attribute_value, role_name: v}}]\n"
        for k in range(60))
    model = tmp_path / "model.orm.yaml"
    model.write_text(HEADER + extra + FOOTER)
    entities = 50
    facts = {"item_has_attribute": [{"item": f"I-{i:03d}", "name": f"a{a}", "value": f"v{i}"}
                                    for a in range(1200) for i in range(entities)]}
    for k in range(60):
        facts[f"item_fact_{k}"] = [{"item": f"I-{i:03d}", "v": f"v{i}"} for i in range(1000)]
    population = tmp_path / "items.population.json"
    population.write_text(json.dumps({"population": {"model": "model.orm.yaml", "source": "fixture",
                                                     "covers": sorted(facts)}, "instances": {}, "facts": facts}))
    started = time.monotonic()
    code = service._cmd_discover(str(model), str(population), out=str(tmp_path / "p.json"),
                                 report=str(tmp_path / "r.json"), actor="test",
                                 requested_at=datetime(2026, 11, 5, tzinfo=UTC), families=("fact-type",),
                                 max_values=20, max_pairs=256, output_format="json",
                                 type_evidence=str(tmp_path / "e.json"))
    elapsed = time.monotonic() - started
    assert code == 0
    document = load(tmp_path / "e.json")
    assert len(document["groups"]) == 1200 and document["truncated"] > 0
    assert len((tmp_path / "e.json").read_bytes()) <= 10 * 1024 * 1024
    assert elapsed < 60, elapsed  # the stated ceiling (spec standing rule 2)


# Review regressions (one reviewer, findings F1..F7). Each failed before its fix.
def _cmd(tmp_path, model, population, name="run", **extra):
    from gnd.discover import service

    return service._cmd_discover(str(model), str(population), out=str(tmp_path / f"{name}.p.json"),
                                 report=str(tmp_path / f"{name}.r.json"), actor="test",
                                 requested_at=datetime(2026, 11, 5, tzinfo=UTC),
                                 max_values=20, max_pairs=256, output_format="json",
                                 type_evidence=str(tmp_path / f"{name}.e.json"),
                                 **{"families": ("fact-type",), **extra})


def test_f1_many_small_groups_truncate_instead_of_exit_70(tmp_path, monkeypatch):
    # Each group costs far more evidence than population, so a valid 1.6 MB
    # population produced more than 10 MiB of groups (refuted premise P2).
    from gnd.discover import type_evidence

    facts = [{"item": "I-0", "name": f"n{a:05d}", "value": "v"} for a in range(40000)]
    model, population = build(tmp_path, induced=False, facts=facts)
    whole = []
    original = type_evidence.canonical_json_bytes
    monkeypatch.setattr(type_evidence, "canonical_json_bytes",
                        lambda value: whole.append(isinstance(value, dict) and "format" in value) or original(value))
    assert _cmd(tmp_path, model, population) == 0
    # Built within the cap: the document is serialised once, never trimmed after.
    assert sum(whole) == 2  # the empty header's size, then the file
    document = load(tmp_path / "run.e.json")
    assert len((tmp_path / "run.e.json").read_bytes()) <= 10 * 1024 * 1024
    assert document["truncated_groups"] > 0
    assert len(document["groups"]) + document["truncated_groups"] == 40000
    assert [g["group"] for g in document["groups"][:2]] == ["g0", "g1"]


def test_f2_candidate_entries_are_bounded_by_the_cap(tmp_path, monkeypatch):
    # Work and memory follow the cap, not groups x candidates (standing rule 2).
    import tracemalloc

    from gnd.discover import type_evidence

    extra = "".join(
        f"  - id: item_fact_{k}\n    reading: \"{{Item}} fact {k} {{AttributeValue}}\"\n"
        f"    roles: [{{object_type: item, role_name: item}}, {{object_type: attribute_value, role_name: v}}]\n"
        for k in range(100))
    (tmp_path / "model.orm.yaml").write_text(HEADER + extra + FOOTER)
    facts = {"item_has_attribute": [{"item": f"I-{i}", "name": f"a{a}", "value": "v"} for a in range(3000) for i in range(2)]}
    facts.update({f"item_fact_{k}": [{"item": "I-0", "v": "v"}] for k in range(100)})
    (tmp_path / "items.population.json").write_text(json.dumps({"population": {
        "model": "model.orm.yaml", "source": "fixture", "covers": sorted(facts)}, "instances": {}, "facts": facts}))
    monkeypatch.setattr(type_evidence, "MAX_EVIDENCE_BYTES", 1_500_000)
    built = []
    original = type_evidence.canonical_json_bytes
    monkeypatch.setattr(type_evidence, "canonical_json_bytes", lambda value: built.append(1) or original(value))
    tracemalloc.start()
    try:
        assert _cmd(tmp_path, tmp_path / "model.orm.yaml", tmp_path / "items.population.json") == 0
        peak = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    document = load(tmp_path / "run.e.json")
    kept = sum(len(g["candidates"]) for g in document["groups"])
    assert kept + document["truncated"] == 3000 * 100 and kept < 3000
    assert len(built) < 3 * (3000 + kept) + 10  # one sizing per group and kept candidate, not per candidate
    assert peak < 150 * 1024 * 1024, peak


def test_f3_datetime_groups_count_pairs(tmp_path):
    (tmp_path / "model.orm.yaml").write_text(HEADER.replace(
        "{id: attribute_value, name: AttributeValue, kind: value, primitive: String}",
        "{id: attribute_value, name: AttributeValue, kind: value, primitive: DateTime}") + """  - id: item_created_at
    reading: "{Item} was created at {AttributeValue}"
    roles: [{object_type: item, role_name: item}, {object_type: attribute_value, role_name: at}]
""" + FOOTER)
    stamp = [f"2026-01-{i + 1:02d}T00:00:00+00:00" for i in range(24)]
    facts = {"item_has_attribute": [{"item": f"I{i}", "name": "created", "value": stamp[i]} for i in range(24)],
             "item_created_at": [{"item": f"I{i}", "at": stamp[i]} for i in range(24)]}
    (tmp_path / "items.population.json").write_text(json.dumps({"population": {
        "model": "model.orm.yaml", "source": "fixture", "covers": sorted(facts)}, "instances": {}, "facts": facts}))
    run, *_, evidence = discover(tmp_path)
    assert run.returncode == 0, run.stderr
    [candidate] = load(evidence)["groups"][0]["candidates"]
    assert candidate["overlap"] == {"entities": 24, "pairs": 24}


@pytest.mark.parametrize("mode", [None, "customer"])
def test_f4_a_redacted_candidate_value_role_gets_no_pair_count(tmp_path, mode):
    model, _population = build(tmp_path)
    model.write_text(model.read_text().replace("{object_type: attribute_value, role_name: label}",
                                               "{object_type: attribute_value, role_name: label, redact: true}", 1))
    run, *_, evidence = discover(tmp_path, env={} if mode is None else {"GND_DISCLOSURE": mode})
    assert run.returncode == 0, run.stderr
    label = [c for c in load(evidence)["groups"][0]["candidates"] if c["fact_type"] == "item_has_label"]
    assert label[0]["overlap"] == {"entities": 0, "pairs": None}


def test_f7_the_service_refuses_evidence_without_the_family(tmp_path):
    model, population = build(tmp_path)
    assert _cmd(tmp_path, model, population, families=("uniqueness",)) == 64
    assert not (tmp_path / "run.r.json").exists() and not (tmp_path / "run.e.json").exists()


def test_the_fallback_trim_is_not_quadratic(monkeypatch):
    # A document built past the cap is trimmed in a few passes (found while
    # mutating the budget away: one-at-a-time trimming did not finish).
    from gnd.discover import type_evidence

    candidate = {"fact_type": "x" * 40, "readings": [], "roles": [], "signature_equal": False, "rows": 0,
                 "overlap": {"entities": 0, "pairs": None}, "origin": None}
    document = {"groups": [{"group": f"g{n}", "candidates": [dict(candidate) for _ in range(50)]}
                           for n in range(2000)], "truncated": 0, "truncated_groups": 0}
    passes = []
    original = type_evidence.canonical_json_bytes
    monkeypatch.setattr(type_evidence, "canonical_json_bytes",
                        lambda value: passes.append(value is document) or original(value))
    raw = type_evidence.evidence_bytes(document, cap=200_000)
    assert len(raw) <= 200_000 and document["truncated"] > 0
    assert sum(passes) < 10
    kept = sum(len(g["candidates"]) for g in document["groups"])
    assert kept + document["truncated"] == 2000 * 50
    tiny = {"groups": [{"group": "g0", "candidates": []}] * 3, "truncated": 0, "truncated_groups": 0}
    assert len(type_evidence.evidence_bytes(tiny, cap=60)) <= 60 and tiny["truncated_groups"] > 0
    with pytest.raises(type_evidence.TypeEvidenceOverflow):
        type_evidence.evidence_bytes({"groups": [], "truncated": 0, "truncated_groups": 0, "pad": "x" * 99}, cap=10)
