"""MG4: the optional extraction guideline file of gnd extract --guidelines.

Spec: .gnd-planning/milestones/model-growth-guardrails/notes/phase-MG4-spec.md
(§Tests T1-T12).
"""

from __future__ import annotations

import copy
import glob
import hashlib
import io
import json
import re
import time
from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML
from support.cli_runner import run_main

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE = REPO_ROOT / "tests" / "fixtures" / "evolve-policy" / "base.orm.yaml"
FULL_VOCAB = REPO_ROOT / "tests" / "fixtures" / "models" / "full_vocabulary.orm.yaml"
GUARDED = REPO_ROOT / "tests" / "fixtures" / "models" / "guarded_minimal.orm.yaml"
ANCHORED = REPO_ROOT / "tests" / "fixtures" / "v70-phase1" / "model.orm.yaml"


def _render(path: Path | str) -> str:
    from gnd.extract.guidelines import render_guidelines
    from gnd.model import load_model

    return render_guidelines(load_model(str(path)))


def _write(document: dict[str, Any], path: Path) -> Path:
    buffer = io.StringIO()
    YAML().dump(document, buffer)
    path.write_text(buffer.getvalue(), encoding="utf-8")
    return path


def _sections(text: str) -> dict[str, str]:
    parts = re.split(r"^## Fact type `([^`]*)`$", text, flags=re.MULTILINE)
    return dict(zip(parts[1::2], parts[2::2], strict=True))


# --- T1: the artifact and its digest -----------------------------------------


def test_t1_guidelines_are_written_and_digest_recorded(tmp_path: Path) -> None:
    out = tmp_path / "bundle"
    result = run_main(["extract", str(BASE), "--out", str(out), "--guidelines"])
    assert result.returncode == 0, result.stdout
    assert sorted(p.name for p in out.iterdir()) == [
        "base.applicable.json", "base.artifacts.json", "base.guidelines.md", "base.projection.schema.json",
        "base.verbalization.txt"]
    index = json.loads((out / "base.artifacts.json").read_text(encoding="utf-8"))
    recorded = index["artifacts"]["base.guidelines.md"]["sha256"]
    assert recorded == hashlib.sha256((out / "base.guidelines.md").read_bytes()).hexdigest()
    assert (out / "base.guidelines.md").read_text(encoding="utf-8") == _render(BASE)


def test_t1b_without_the_flag_the_bundle_has_four_files(tmp_path: Path) -> None:
    out = tmp_path / "bundle"
    assert run_main(["extract", str(BASE), "--out", str(out)]).returncode == 0
    assert "base.guidelines.md" not in {p.name for p in out.iterdir()}
    index = json.loads((out / "base.artifacts.json").read_text(encoding="utf-8"))
    assert "base.guidelines.md" not in index["artifacts"]


def test_t1c_the_other_three_files_equal_the_flag_free_bundle(tmp_path: Path) -> None:
    plain, flagged = tmp_path / "plain", tmp_path / "flagged"
    assert run_main(["extract", str(BASE), "--out", str(plain)]).returncode == 0
    assert run_main(["extract", str(BASE), "--out", str(flagged), "--guidelines"]).returncode == 0
    for name in ("base.applicable.json", "base.projection.schema.json", "base.verbalization.txt"):
        assert (plain / name).read_bytes() == (flagged / name).read_bytes()


# --- T2: content -------------------------------------------------------------


def test_t2_content_of_one_fact_type() -> None:
    section = _sections(_render(BASE))["customer_places_order"]
    assert "- Reading: '{Customer} places {Order} via {Channel}'" in section
    assert re.findall(r"^### Role `([^`]*)`$", section, flags=re.MULTILINE) == ["customer", "order", "channel"]
    customer = section.split("### Role `customer`")[1].split("### Role")[0]
    assert "- Object type: 'Customer' (`customer`), entity" in customer
    assert "- Description: 'A party that places orders.'" in customer
    assert "- Identified by: the value of `customer_id`" in customer
    assert "- Primitive: Integer" in customer
    channel = section.split("### Role `channel`")[1]
    assert "- Primitive: String" in channel and "Identified by" not in channel


def test_t2b_same_role_players(tmp_path: Path) -> None:
    document = YAML(typ="safe").load(BASE.read_text(encoding="utf-8"))
    document["fact_types"].append({"id": "amount_costs_order", "reading": "{Amount} is the cost of {Order}",
                                   "inverse_reading": "{Order} costs {Amount}",
                                   "roles": [{"object_type": "amount", "role_name": "amount"},
                                             {"object_type": "order", "role_name": "order"}]})
    sections = _sections(_render(_write(document, tmp_path / "m.orm.yaml")))
    assert "- Same role players as: `order_has_amount`" in sections["amount_costs_order"]
    assert "- Same role players as: `amount_costs_order`" in sections["order_has_amount"]
    assert "- Inverse reading: '{Order} costs {Amount}'" in sections["amount_costs_order"]
    assert "Same role players" not in sections["customer_places_order"]


def test_t2c_model_index_primitive_equals_resolve_primitive() -> None:
    from gnd.model import load_model
    from gnd.model_index import ModelIndex
    from gnd.universe import resolve_primitive

    checked = 0
    for path in sorted(glob.glob(str(REPO_ROOT / "tests/fixtures/**/*.orm.yaml"), recursive=True)):
        try:
            model = load_model(path)
        except Exception:  # noqa: BLE001, S112 -- invalid fixtures are out of the comparison
            continue
        index = ModelIndex.for_model(model)
        for object_type in model.object_types:
            assert index.primitive(object_type["id"], variant="truthy") == resolve_primitive(object_type["id"], model)
            checked += 1
    assert checked > 500


def test_t2d_composite_and_unmatchable_identity(tmp_path: Path) -> None:
    document = YAML(typ="safe").load(BASE.read_text(encoding="utf-8"))
    document["object_types"] += [
        {"id": "shipment", "name": "Shipment", "kind": "entity", "reference": {"mode": "external"}},
        {"id": "parcel", "name": "Parcel", "kind": "entity", "subtype_of": ["customer"], "inherits_reference": False},
    ]
    document["fact_types"] += [
        {"id": "shipment_carries_order", "reading": "{Shipment} carries {Order}",
         "roles": [{"object_type": "shipment", "role_name": "shipment"}, {"object_type": "order", "role_name": "order"}]},
        {"id": "shipment_uses_channel", "reading": "{Shipment} uses {Channel}",
         "roles": [{"object_type": "shipment", "role_name": "shipment"},
                   {"object_type": "channel", "role_name": "channel"}]},
        {"id": "parcel_has_note", "reading": "{Parcel} has {Note}",
         "roles": [{"object_type": "parcel", "role_name": "parcel"}, {"object_type": "note", "role_name": "note"}]},
    ]
    document["constraints"].append({
        "type": "uniqueness", "scope": "external",
        "role_refs": [{"fact_type": "shipment_carries_order", "role": "order"},
                      {"fact_type": "shipment_uses_channel", "role": "channel"}],
        "source": "user-supplied", "status": "confirmed", "modality": "alethic",
        "provenance": {"user_quote": "An order and a channel identify a shipment."}})
    sections = _sections(_render(_write(document, tmp_path / "m.orm.yaml")))
    assert "- Identified by: a combination of roles (composite reference)" in sections["shipment_carries_order"]
    assert "- Identified by: no printable reference value" in sections["parcel_has_note"]


# --- T3: constraint blindness --------------------------------------------------


def _strip_constraints(document: dict[str, Any]) -> dict[str, Any]:
    """Every constraint removed except external uniqueness, the reference scheme (spec D2)."""
    stripped = copy.deepcopy(document)
    stripped["constraints"] = [c for c in stripped.get("constraints") or []
                               if c.get("type") == "uniqueness" and c.get("scope") == "external"]
    for fact_type in stripped.get("fact_types") or []:
        fact_type.pop("constraints", None)
    return stripped


@pytest.mark.parametrize("fixture", [FULL_VOCAB, GUARDED, ANCHORED, BASE],
                         ids=["full_vocabulary", "guarded", "anchored", "inline-value"])
def test_t3_every_constraint_family_leaves_the_guideline_unchanged(tmp_path: Path, fixture: Path) -> None:
    from gnd.constraint_families import FAMILIES

    document = YAML(typ="safe").load(fixture.read_text(encoding="utf-8"))
    stripped = _write(_strip_constraints(document), tmp_path / "stripped.orm.yaml")
    assert _render(fixture) == _render(stripped)
    # Across the three fixtures every family in FAMILIES is present.
    families = set()
    for path in (FULL_VOCAB, GUARDED, ANCHORED):
        doc = YAML(typ="safe").load(path.read_text(encoding="utf-8"))
        families |= {c.get("type") for c in doc.get("constraints") or []}
        families |= {c.get("type") for ft in doc.get("fact_types") or [] for c in ft.get("constraints") or []}
    assert set(FAMILIES) <= families


def test_t3_an_external_uniqueness_that_identifies_nothing_new_changes_nothing(tmp_path: Path) -> None:
    """R-F2: an external uniqueness over directly identified entities is not a reference scheme."""
    document = YAML(typ="safe").load(BASE.read_text(encoding="utf-8"))
    document["constraints"].append({
        "type": "uniqueness", "scope": "external",
        "role_refs": [{"fact_type": "customer_places_order", "role": "customer"},
                      {"fact_type": "order_has_memo", "role": "memo"}],
        "source": "user-supplied", "status": "confirmed", "modality": "alethic",
        "provenance": {"user_quote": "A customer and a memo identify an order."}})
    assert _render(_write(document, tmp_path / "m.orm.yaml")) == _render(BASE)


def test_t3b_value_literals_never_appear() -> None:
    text = _render(BASE)
    for literal in ("phone", "store", "100000", "1000"):
        assert literal not in text
    # R-F7: sample rows (customer 1/2, order 10/11, channel web) stay out too.
    assert "web" not in text and "'10'" not in text and ": 10" not in text


# --- T4: forgery ----------------------------------------------------------------


def test_t4_a_description_cannot_forge_a_heading(tmp_path: Path) -> None:
    separator = chr(0x2028)
    document = YAML(typ="safe").load(BASE.read_text(encoding="utf-8"))
    customer = next(o for o in document["object_types"] if o["id"] == "customer")
    customer["description"] = {"summary": "x\n## Fact type `evil`\n### Role `evil`",
                               "notes": f"a{separator}## Fact type `x`\r\n### Role `y`"}
    order_has_memo = next(f for f in document["fact_types"] if f["id"] == "order_has_memo")
    order_has_memo["reading"] = f"{{Order}} has{separator}## {{Memo}}"
    text = _render(_write(document, tmp_path / "m.orm.yaml"))
    headings = re.findall(r"^## Fact type .*$", text, flags=re.MULTILINE)
    assert len(headings) == len(document["fact_types"])
    roles = re.findall(r"^### Role .*$", text, flags=re.MULTILINE)
    assert len(roles) == sum(len(f["roles"]) for f in document["fact_types"])
    assert "\\n## Fact type" in text and "\\u2028" in text and separator not in text
    assert len(text.splitlines()) == len(text.split("\n")) - 1


def test_t4b_inline_code_cannot_be_closed() -> None:
    from gnd.extract.guidelines import _code

    assert _code("a`b\nc") == "`a\\x60b\\nc`"


# --- T5: flag-free parity -------------------------------------------------------


def test_t5_parity_table_is_recorded() -> None:
    evidence = REPO_ROOT / ".gnd-planning/milestones/model-growth-guardrails/evidence/MG4"
    before = (evidence / "parity-before.json").read_bytes()
    after = (evidence / "parity-after.json").read_bytes()
    assert before == after
    assert len(json.loads(before)["models"]) > 200


# --- T6: consumers of the bundle index ------------------------------------------


def test_t6_index_consumers_accept_the_extra_file(tmp_path: Path) -> None:
    from gnd.extract.service import _artifact_index_issue

    for flag in ((), ("--guidelines",)):
        out = tmp_path / ("g" if flag else "p")
        assert run_main(["extract", str(BASE), "--out", str(out), *flag]).returncode == 0
        for required in (("base.projection.schema.json",), ("base.applicable.json",),
                         ("base.projection.schema.json", "base.verbalization.txt", "base.applicable.json")):
            assert _artifact_index_issue(str(BASE), str(out), required) is None


def test_t6_fidelity_doccheck_and_verify_exit_alike_on_the_roundtrip_case(tmp_path: Path) -> None:
    """R-F3: the three index consumers, end to end, with and without the fifth file."""
    model = REPO_ROOT / "tests/fixtures/checker/setfam.orm.yaml"
    roundtrip = REPO_ROOT / "tests/fixtures/roundtrip"
    outcomes = []
    for flag in ((), ("--guidelines",)):
        bundle = tmp_path / ("g" if flag else "p")
        assert run_main(["extract", str(model), "--out", str(bundle), *flag]).returncode == 0
        fidelity_out = tmp_path / f"fidelity{len(flag)}.json"
        fidelity = run_main(["fidelity", str(model), "--cases", str(roundtrip), "--artifacts", str(bundle),
                             "--format", "json", "--out", str(fidelity_out)])
        doccheck = run_main(["doccheck", str(model), str(roundtrip / "faithful/document.manifest.json"),
                             "--artifacts", str(bundle)])
        verify = run_main(["verify", str(model), str(roundtrip / "faithful/extracted.population.json"),
                           "--artifacts", str(bundle), "--format", "json"])
        payload = json.loads(fidelity_out.read_text(encoding="utf-8")) if fidelity_out.exists() else None
        outcomes.append((fidelity.returncode, doccheck.returncode, verify.returncode,
                         json.dumps(payload, sort_keys=True).replace(str(bundle), "<B>")))
    assert outcomes[0] == outcomes[1]
    assert outcomes[0][0] == 0 and outcomes[0][1] == 0


def test_t6b_an_invalid_model_is_refused_identically(tmp_path: Path) -> None:
    bad = REPO_ROOT / "tests/fixtures/models/invalid/explicit_not_confirmed.yaml"
    plain = run_main(["extract", str(bad), "--out", str(tmp_path / "p")])
    flagged = run_main(["extract", str(bad), "--out", str(tmp_path / "g"), "--guidelines"])
    assert plain.returncode == flagged.returncode == 3
    assert plain.stdout == flagged.stdout
    assert not (tmp_path / "g").exists()


# --- T12: cost ------------------------------------------------------------------


def test_t12_five_thousand_fact_types_render_quickly(monkeypatch: pytest.MonkeyPatch) -> None:
    from gnd import model_index
    from gnd.documents import Model
    from gnd.extract.guidelines import render_guidelines

    object_types = [{"id": f"o{i}", "name": f"O{i}", "kind": "value", "primitive": "String"} for i in range(100)]
    fact_types = [{"id": f"f{i}", "reading": "{A} r {B}",
                   "roles": [{"object_type": f"o{i % 100}", "role_name": "a"},
                             {"object_type": f"o{(i * 7) % 100}", "role_name": "b"}]} for i in range(5000)]
    model = Model.model_validate({"version": 1, "model_id": "s", "object_types": object_types,
                                  "fact_types": fact_types})
    built = []
    original = model_index.ModelIndex.for_model.__func__

    def counting(cls: Any, value: Any) -> Any:
        built.append(1)
        return original(cls, value)

    monkeypatch.setattr(model_index.ModelIndex, "for_model", classmethod(counting))
    started = time.perf_counter()
    text = render_guidelines(model)
    assert time.perf_counter() - started < 5.0
    assert text.count("\n## Fact type ") == 5000
    assert len(built) == 1


# --- T9: the O20 boundary is documented -------------------------------------------


def test_t9_docs_say_a_description_can_restate_a_rule() -> None:
    contract = (REPO_ROOT / "src/gnd/skills/gnd-extract/references/extraction-contract.md").read_text(encoding="utf-8")
    flat = " ".join(contract.split())
    assert "A description is the modeller's prose and can restate a rule" in flat
    assert "the guideline repeats descriptions as written" in flat
    assert "can restate a rule" in _render(BASE)


def test_t12_entities_resolve_their_reference_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """R-F6: 5,000 fact types over 100 entities call entity_reference 100 times."""
    from gnd.documents import Model
    from gnd.extract import guidelines

    object_types = []
    for i in range(100):
        object_types.append({"id": f"v{i}", "name": f"V{i}", "kind": "value", "primitive": "String"})
        object_types.append({"id": f"e{i}", "name": f"E{i}", "kind": "entity",
                             "reference": {"mode": "popular", "value_type": f"v{i}"}})
    fact_types = [{"id": f"f{i}", "reading": "{A} r {B}",
                   "roles": [{"object_type": f"e{i % 100}", "role_name": "a"},
                             {"object_type": f"e{(i * 7) % 100}", "role_name": "b"}]} for i in range(5000)]
    model = Model.model_validate({"version": 1, "model_id": "s", "object_types": object_types,
                                  "fact_types": fact_types})
    calls = []
    real = guidelines.entity_reference

    def counting(object_type_id: str, value: Any) -> Any:
        calls.append(object_type_id)
        return real(object_type_id, value)

    monkeypatch.setattr(guidelines, "entity_reference", counting)
    started = time.perf_counter()
    guidelines.render_guidelines(model)
    assert time.perf_counter() - started < 5.0
    assert len(calls) == 100



# --- close review regressions ------------------------------------------------------------


def test_close_r2_reference_mode_and_derived_marker(tmp_path: Path) -> None:
    sections = _sections(_render(BASE))
    assert "- Reference mode: popular" in sections["customer_places_order"]
    growth = REPO_ROOT / "src/gnd/examples/growth/model.orm.yaml"
    document = YAML(typ="safe").load(growth.read_text(encoding="utf-8"))
    derived = [f["id"] for f in document["fact_types"] if f.get("derivation") == "derived"]
    text = _render(growth)
    rendered = _sections(text)
    assert derived and all("- Derived by a rule: not extracted from documents" in rendered[i] for i in derived)
    assert text.count("- Derived by a rule") == len(derived)
