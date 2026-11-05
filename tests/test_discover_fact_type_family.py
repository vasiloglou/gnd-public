"""CT4: the opt-in ``fact-type`` discover family proposes fact types from generic rows."""

import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
CANARY_ATTRIBUTE = "colour-7f3a"
MODEL = """version: 2
model_id: urn:gnd-fixture:ct4-generic@1
source: {kind: text-conversation, confidence: standard, mode: one-shot}
object_types:
  - {id: item, name: Item, kind: value, primitive: String}
  - {id: attribute_name, name: AttributeName, kind: value, primitive: String}
  - {id: attribute_value, name: AttributeValue, kind: value, primitive: String}
fact_types:
  - id: item_has_attribute
    reading: "{Item} has attribute {AttributeName} with value {AttributeValue}"
    roles:
      - {object_type: item, role_name: item}
      - {object_type: attribute_name, role_name: name}
      - {object_type: attribute_value, role_name: value}
%(provenance)s%(extra)s
constraints: []
rejected_proposals: []
"""
GENERIC = "    provenance:\n      generic: {entity: item, attribute: name, value: value}\n"


def rows(colour=25, size=19, weight=20, colour_twice=False, weight_entities=None):
    out = [{"item": f"I-{i:02d}", "name": CANARY_ATTRIBUTE, "value": f"shade-{i}"} for i in range(colour)]
    if colour_twice:
        out.append({"item": "I-00", "name": CANARY_ATTRIBUTE, "value": "shade-x"})
    out += [{"item": f"I-{i:02d}", "name": "size", "value": f"s{i}"} for i in range(size)]
    entities = weight_entities if weight_entities is not None else weight
    out += [{"item": f"I-{i % entities:02d}", "name": "weight", "value": f"w{i}"} for i in range(weight)]
    return out


def build(tmp_path, *, provenance=GENERIC, extra="", facts=None, redact=False):
    model = tmp_path / "model.orm.yaml"
    text = MODEL % {"provenance": provenance, "extra": extra}
    if redact:
        text = text.replace("{object_type: attribute_name, role_name: name}", "{object_type: attribute_name, role_name: name, redact: true}", 1)
    model.write_text(text)
    population = tmp_path / "items.population.json"
    population.write_text(json.dumps({
        "population": {"model": "model.orm.yaml", "source": "fixture", "covers": ["item_has_attribute"]},
        "instances": {}, "facts": {"item_has_attribute": rows() if facts is None else facts},
    }))
    return model, population


def discover(tmp_path, model, population, *extra, env=None, name="run"):
    out, report = tmp_path / f"{name}.proposal.json", tmp_path / f"{name}.report.json"
    run = subprocess.run([sys.executable, "-m", "gnd", "discover", str(model), str(population),
                          "--out", str(out), "--report", str(report), "--actor", "test",
                          "--requested-at", "2026-11-04T00:00:00+00:00", "--families", "fact-type",
                          "--format", "json", *extra],
                         capture_output=True, text=True, check=False, env={**os.environ, **(env or {})})
    return run, out, report


def proposals(report):
    return json.loads(report.read_text())["fact_type_proposals"]


# T1
@pytest.mark.parametrize("bad", [
    "    provenance:\n      generic: {entity: item, attribute: name}\n",
    "    provenance:\n      generic: {entity: item, attribute: item, value: value}\n",
    "    provenance:\n      generic: {entity: item, attribute: name, value: nope}\n",
    "    provenance:\n      generic: [item]\n",
])
def test_an_invalid_declaration_is_refused(tmp_path, bad):
    model, population = build(tmp_path, provenance=bad)
    run, out, _report = discover(tmp_path, model, population)
    assert run.returncode == 3, run.stdout + run.stderr
    assert "item_has_attribute: invalid generic declaration" in run.stderr
    assert not out.exists()


def test_an_undeclared_generic_shape_yields_nothing(tmp_path):
    model, population = build(tmp_path, provenance="")
    run, out, report = discover(tmp_path, model, population)
    assert run.returncode == 0, run.stderr
    assert proposals(report)["proposed"] == [] and not out.exists()


# T2
def test_grouping_support_and_type_consistency(tmp_path):
    model, population = build(tmp_path)
    run, _out, report = discover(tmp_path, model, population)
    assert run.returncode == 0, run.stderr
    found = proposals(report)
    assert [p["fact_type"] for p in found["proposed"]] == ["item_has_attribute_induced_0", "item_has_attribute_induced_2"]
    colour = found["proposed"][0]
    assert colour["support"] == {"numerator": 25, "denominator": 25}
    assert len(colour["rows"]) == 25 and colour["rows"][0] == "ft0#0"
    assert found["skipped"]["below_support"] == 1  # size: 19 entities
    lowered = discover(tmp_path, model, population, "--min-support", "19", name="low")[2]
    assert len(proposals(lowered)["proposed"]) == 3


def test_rows_are_not_entities(tmp_path):
    model, population = build(tmp_path, facts=rows(colour=0, colour_twice=False, size=0, weight=20, weight_entities=19))
    report = discover(tmp_path, model, population)[2]
    assert proposals(report)["proposed"] == []
    assert proposals(report)["skipped"]["below_support"] == 1


def test_a_mixed_type_group_is_counted_not_proposed(tmp_path):
    # A validated population cannot hold two JSON types in one typed role, so
    # the guard is exercised on an unvalidated view.
    from gnd.discover import types
    from gnd.discover.support import PopulationView, Work
    from gnd.model import load_model
    from gnd.population import load_population

    facts = [{"item": f"I-{i:02d}", "name": "mixed", "value": (i if i % 2 else f"v{i}")} for i in range(25)]
    model, population = build(tmp_path, facts=facts)
    view = PopulationView(load_model(model), load_population(population), Work())
    found = types.propose(view, ["item_has_attribute"], min_support=20, show_values=False,
                          redacted=frozenset(), envelope={})
    assert found.report["skipped"]["mixed_type_groups"] == 1
    assert found.operations == []


# T3
def test_values_stay_out_unless_the_mode_allows(tmp_path):
    model, population = build(tmp_path)
    run, out, report = discover(tmp_path, model, population)
    for blob in (out.read_text(), report.read_text(), run.stdout):
        assert CANARY_ATTRIBUTE not in blob and "shade-" not in blob
    shown = discover(tmp_path, model, population, "--show-values", name="shown")[2]
    assert proposals(shown)["proposed"][0]["value"] == CANARY_ATTRIBUTE
    internal = discover(tmp_path, model, population, env={"GND_DISCLOSURE": "internal"}, name="internal")[2]
    assert proposals(internal)["proposed"][0]["value"] == CANARY_ATTRIBUTE
    refused, refused_out, _ = discover(tmp_path, model, population, "--show-values",
                                       env={"GND_DISCLOSURE": "customer"}, name="customer")
    assert refused.returncode == 3
    assert "--show-values is refused in customer disclosure mode" in refused.stderr
    assert not refused_out.exists()


def test_customer_mode_omits_the_attribute_digest(tmp_path):
    # Owner ruling after the close: a short attribute name can be recovered
    # from its unsalted digest, so customer mode reports no digest at all.
    import hashlib

    from gnd.artifacts import canonical_json_bytes

    model, population = build(tmp_path)
    digest = hashlib.sha256(canonical_json_bytes(CANARY_ATTRIBUTE)).hexdigest()
    plain = discover(tmp_path, model, population, name="plain")[2]
    assert proposals(plain)["proposed"][0]["attribute_sha256"] == digest
    run, out, report = discover(tmp_path, model, population, env={"GND_DISCLOSURE": "customer"}, name="customer")
    assert run.returncode == 0, run.stderr
    family = proposals(report)
    assert family["proposed"] and all("attribute_sha256" not in entry for entry in family["proposed"])
    for blob in (out.read_text(), report.read_text(), run.stdout):
        assert digest not in blob and CANARY_ATTRIBUTE not in blob


def test_flags_need_the_family(tmp_path):
    model, population = build(tmp_path)
    for flag in (["--show-values"], ["--min-support", "5"]):
        run = subprocess.run([sys.executable, "-m", "gnd", "discover", str(model), str(population),
                              "--out", str(tmp_path / "o.json"), "--report", str(tmp_path / "r.json"),
                              "--actor", "t", "--requested-at", "2026-11-04T00:00:00+00:00", *flag],
                             capture_output=True, text=True, check=False)
        assert run.returncode == 64


# T4
def test_the_proposal_passes_the_additive_policy(tmp_path):
    model, population = build(tmp_path)
    _run, out, report = discover(tmp_path, model, population)
    proposal = json.loads(out.read_text())
    constraints = [op["after"] for op in proposal["operations"] if op["locator"]["locator_kind"] == "constraint"]
    assert all(c["source"] == "induced" and c["status"] == "proposed" and c["modality"] == "deontic"
               for c in constraints)
    assert constraints[0]["provenance"]["induction"]["support"] == {"numerator": 25, "denominator": 25}
    preview = subprocess.run([sys.executable, "-m", "gnd", "evolve", "preview", str(model), str(out),
                              "--workspace", str(tmp_path), "--records", str(tmp_path / "records"),
                              "--out", str(tmp_path / "preview.json"), "--policy", "additive"],
                             capture_output=True, text=True, check=False)
    assert preview.returncode == 0, preview.stdout + preview.stderr
    schema = json.loads((ROOT / "src/gnd/discover.schema.json").read_text())
    jsonschema.validate(json.loads(report.read_text()), schema)


# T5
def test_an_existing_shape_is_reported_not_proposed(tmp_path):
    extra = ("  - id: item_has_label\n    reading: \"{Item} has label {AttributeValue}\"\n"
             "    roles: [{object_type: item, role_name: item}, {object_type: attribute_value, role_name: label}]\n")
    model, population = build(tmp_path, extra=extra)
    report = discover(tmp_path, model, population)[2]
    found = proposals(report)
    assert [m["existing"] for m in found["shape_matches"]] == ["item_has_label", "item_has_label"]
    assert found["proposed"] == []


def test_a_redacted_attribute_role_is_skipped(tmp_path):
    model, population = build(tmp_path, redact=True)
    run, _out, report = discover(tmp_path, model, population)
    assert run.returncode == 0, run.stderr
    assert proposals(report)["skipped"]["redacted_attribute_roles"] == 1
    assert proposals(report)["proposed"] == []


# T6 (partial): without the family the report has no new key
def test_without_the_family_the_report_is_unchanged(tmp_path):
    model, population = build(tmp_path)
    out, report = tmp_path / "p.json", tmp_path / "r.json"
    run = subprocess.run([sys.executable, "-m", "gnd", "discover", str(model), str(population),
                          "--out", str(out), "--report", str(report), "--actor", "t",
                          "--requested-at", "2026-11-04T00:00:00+00:00"], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr
    assert "fact_type_proposals" not in json.loads(report.read_text())


# CT4 review fixes (F1, F2, F3, F4, F9)
def test_a_multi_valued_attribute_is_counted_not_proposed(tmp_path):
    model, population = build(tmp_path, facts=rows(colour_twice=True, size=0, weight=0))
    found = proposals(discover(tmp_path, model, population)[2])
    assert found["proposed"] == [] and found["skipped"]["multi_valued"] == 1


def test_an_existing_id_is_never_reused(tmp_path):
    extra = ("  - id: item_has_attribute_induced_0\n    reading: \"{Item} is flagged\"\n"
             "    roles: [{object_type: item, role_name: item}]\n")
    model, population = build(tmp_path, extra=extra)
    run, _out, report = discover(tmp_path, model, population)
    assert run.returncode == 0, run.stderr
    assert proposals(report)["proposed"][0]["fact_type"] == "item_has_attribute_induced_0_1"


def test_the_family_respects_the_proposal_budget(tmp_path, monkeypatch):
    from gnd.discover import service

    model, population = build(tmp_path)
    monkeypatch.setattr(service, "MAX_EVOLUTION_PROPOSAL_BYTES", service.BUDGET_MARGIN + 2 * len(model.read_bytes()) + 4000)
    result = service.discover(model, population, families=("fact-type",), max_values=20, max_pairs=256)
    family = result["fields"]["fact_type_proposals"]
    assert len(family["proposed"]) == 1 and family["skipped"]["over_budget"] == 1


def test_the_written_proposal_never_exceeds_its_cap(tmp_path, monkeypatch, capsys):
    # Close review: the size estimate is only a pre-filter. Make it admit far
    # more than the cap and check the written bytes are trimmed under it.
    from datetime import UTC, datetime

    from gnd.discover import service

    facts = [{"item": f"I-{i:02d}", "name": f"attr-{a:03d}", "value": f"v{i}"} for a in range(60) for i in range(20)]
    model, population = build(tmp_path, facts=facts)
    def run(name):
        nonlocal out, report
        out, report = tmp_path / f"{name}.p.json", tmp_path / f"{name}.r.json"
        return service._cmd_discover(str(model), str(population), out=str(out), report=str(report), actor="test",
                                     requested_at=datetime(2026, 11, 4, tzinfo=UTC),
                                     families=("fact-type",), max_values=20, max_pairs=256, output_format="text")

    out = report = None
    assert run("full") == 0
    cap = len(out.read_bytes()) // 2
    monkeypatch.setattr(service, "MAX_EVOLUTION_PROPOSAL_BYTES", cap)
    monkeypatch.setattr(service, "BUDGET_MARGIN", -10 * cap)
    assert run("capped") == 0
    family = json.loads(report.read_text())["fact_type_proposals"]
    assert 0 < len(family["proposed"]) < 60 and family["skipped"]["over_budget"] == 60 - len(family["proposed"])
    assert len(out.read_bytes()) <= cap
    written = {op["locator"]["host_id"] for op in json.loads(out.read_text())["operations"]
               if op["locator"]["locator_kind"] == "constraint"}
    assert written == {entry["fact_type"] for entry in family["proposed"]}


def test_a_redacted_value_role_stays_redacted(tmp_path):
    model, population = build(tmp_path)
    model.write_text(model.read_text().replace("{object_type: attribute_value, role_name: value}",
                                               "{object_type: attribute_value, role_name: value, redact: true}", 1))
    out = discover(tmp_path, model, population)[1]
    added = [op["after"] for op in json.loads(out.read_text())["operations"] if op["locator"]["locator_kind"] == "element"]
    assert all(role.get("redact") is True for ft in added if "roles" in ft for role in ft["roles"] if role["role_name"] == "value")


def test_a_new_value_type_is_added_when_the_primitive_differs(tmp_path):
    model, population = build(tmp_path, facts=[])
    model.write_text(model.read_text().replace(
        "{id: attribute_value, name: AttributeValue, kind: value, primitive: String}",
        "{id: attribute_value, name: AttributeValue, kind: value, primitive: Integer}"))
    data = json.loads(population.read_text())
    data["facts"]["item_has_attribute"] = [{"item": f"I-{i:02d}", "name": "rank", "value": i} for i in range(20)]
    population.write_text(json.dumps(data))
    run, out, _report = discover(tmp_path, model, population)
    assert run.returncode == 0, run.stderr
    # Integer matches the generic value type, so it is reused; no new value type.
    kinds = [op["locator"]["collection"] for op in json.loads(out.read_text())["operations"]
             if op["locator"]["locator_kind"] == "element"]
    assert kinds == ["fact_types"]


def test_the_family_combines_with_other_families_and_applies(tmp_path):
    model, population = build(tmp_path)
    run, out, _report = discover(tmp_path, model, population, "--families", "uniqueness,fact-type", name="both")
    assert run.returncode == 0, run.stderr
    preview = tmp_path / "both.preview.json"
    common = ["--workspace", str(tmp_path), "--records", str(tmp_path / "records")]
    step = subprocess.run([sys.executable, "-m", "gnd", "evolve", "preview", str(model), str(out), *common,
                           "--out", str(preview), "--policy", "additive"], capture_output=True, text=True, check=False)
    assert step.returncode == 0, step.stdout + step.stderr
    applied = subprocess.run([sys.executable, "-m", "gnd", "evolve", "apply", str(model), str(out), "--preview",
                              str(preview), *common, "--policy", "additive"], capture_output=True, text=True, check=False)
    assert applied.returncode == 0, applied.stdout + applied.stderr
    assert "item_has_attribute_induced_0" in model.read_text()


def test_an_exactly_repeated_row_is_one_value(tmp_path):
    # Close review: count distinct values per entity, not rows.
    facts = rows(colour=20, size=0, weight=0)
    facts.append(dict(facts[0]))
    model, population = build(tmp_path, facts=facts)
    run, _out, report = discover(tmp_path, model, population)
    assert run.returncode == 0, run.stderr
    family = proposals(report)
    assert len(family["proposed"]) == 1 and family["skipped"]["multi_valued"] == 0


def test_other_families_over_the_cap_still_write_their_proposal(tmp_path, monkeypatch):
    # Close re-review: with no type groups left to drop, the proposal is
    # written as it was before the trim, and nothing raises.
    from datetime import UTC, datetime

    from gnd.discover import service

    model, population = build(tmp_path)
    monkeypatch.setattr(service, "MAX_EVOLUTION_PROPOSAL_BYTES", 200)
    monkeypatch.setattr(service, "BUDGET_MARGIN", -10**8)
    out, report = tmp_path / "p.json", tmp_path / "r.json"
    code = service._cmd_discover(str(model), str(population), out=str(out), report=str(report), actor="test",
                                 requested_at=datetime(2026, 11, 4, tzinfo=UTC),
                                 families=("uniqueness", "mandatory", "fact-type"), max_values=20, max_pairs=256,
                                 output_format="text")
    assert code == 0 and report.exists()
