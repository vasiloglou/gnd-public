"""Reviewed corpus, exact formula placements and sidecar fallback for OS2."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from time import monotonic

import pytest

from gnd.export.ossie import _ontology, render_ossie
from gnd.model import load_model

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / ".gnd-planning/milestones/ossie-interchange/evidence/OS2/corpus-r2"
SOURCE = CORPUS / "model.orm.json"


def _formula_counts(ontology):
    result = Counter(("ontology", "requires", text) for text in ontology.get("requires", ()))
    for concept in ontology["ontology"]:
        owner = concept["concept"]
        for key in ("requires", "derived_by"):
            result.update((f"concept:{owner}", key, text) for text in concept.get(key, ()))
        for relation in concept.get("relationships", ()):
            scope = f"relationship:{owner}.{relation['name']}"
            for key in ("requires", "derived_by"):
                result.update((scope, key, text) for text in relation.get(key, ()))
    return result


def _rows(bundle):
    return {
        row["pointer"]: row["disposition"] for row in json.loads(bundle.loss_report)["dispositions"]
    }


def test_approved_corpus_artifact_identities():
    manifest = json.loads((CORPUS / "manifest.json").read_bytes())
    for name, expected in manifest.items():
        assert hashlib.sha256((CORPUS / name).read_bytes()).hexdigest() == expected, name


def test_checker_matches_approved_corpus():
    run = subprocess.run(
        [sys.executable, str(CORPUS / "replay.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert "29 hand-authored verdicts matched" in run.stdout


def test_exact_approved_formula_groups_and_dispositions():
    approved = json.loads((CORPUS / "expected.json").read_bytes())
    distinct = {row["rule"]: row for row in approved.values() if row["projection"] == "formula"}
    expected = Counter(
        (
            placement["scope"],
            "derived_by" if rule.startswith("derivation:") else "requires",
            placement["formula"],
        )
        for rule, row in distinct.items()
        for placement in row["placements"]
    )
    result = render_ossie(SOURCE, output_format="json")
    assert _formula_counts(json.loads(result.document)) == expected
    rows = _rows(result)
    for index in range(6):
        pointer = f"/constraints/{index}"
        assert rows[pointer] == rows[f"{pointer}/type"] == "requires"
        assert (
            rows[f"{pointer}/modality"] == rows[f"{pointer}/provenance/user_quote"] == "extension"
        )
    assert rows["/fact_types/0/constraints/0"] == "extension"
    assert rows["/fact_types/0/constraints/1"] == "extension"
    assert rows["/fact_types/4/constraints/0"] == "requires"
    assert rows["/fact_types/7/derivation_rule/body/0/bind/account"] == "requires"
    sidecar = json.loads(result.sidecar)
    assert sidecar["elements"]["balance_ceiling"]["/constraints/0/consequent/comparison/right"] == {
        "kind": "literal",
        "value": 100,
    }


@pytest.mark.parametrize(
    "variation",
    (
        "deontic",
        "proposed",
        "computed",
        "invalid-string",
        "reserved-name",
        "binary-membership",
        "partial-group",
        "reversed-join",
    ),
)
def test_unreviewed_shapes_keep_their_source_in_the_sidecar(tmp_path, variation):
    authored = json.loads(SOURCE.read_bytes())
    constraint = authored["constraints"][0]
    pointer = "/constraints/0"
    absent = ("relationship:Account.account_balance", "requires", "balance <= 100")
    if variation == "deontic":
        constraint["modality"] = "deontic"
    elif variation == "proposed":
        constraint.update(
            source="llm-inferred",
            status="proposed",
            rationale="Draft model proposal.",
            provenance={"rationale_world_fact": "Possible upper balance bound."},
        )
    elif variation == "computed":
        authored["version"] = 3
        constraint["consequent"]["comparison"]["left"] = {"fn": "add", "args": ["$n", 1]}
    elif variation == "invalid-string":
        authored["constraints"][4]["allowed"].append("Merchant's Choice")
        pointer = "/constraints/4"
        absent = ("concept:Category", "requires", "Category == 'Retail' OR Category == 'Business'")
    elif variation == "reserved-name":
        authored["object_types"][3]["name"] = "COUNT"
        authored["constraints"][5]["object_type"] = "band"
        pointer = "/constraints/5"
        absent = ("ontology", "requires", "COUNT[COUNT] <= 2")
    elif variation == "binary-membership":
        relation = authored["fact_types"][2]
        relation["reading"] = "{Account} is registered as {Category}"
        relation["roles"].append({"role_name": "category", "object_type": "category"})
        pointer = "/constraints/2"
        absent = ("relationship:Account.account_registered", "requires", "Account.account_active")
    elif variation == "partial-group":
        authored["constraints"][5]["bound"]["min"] = 1
        pointer = "/constraints/5"
        absent = ("ontology", "requires", "COUNT[Account] <= 2")
    else:
        authored["fact_types"][7]["derivation_rule"]["body"].reverse()
        pointer = "/fact_types/7/derivation_rule"
        absent = (
            "relationship:Account.account_band",
            "derived_by",
            "Account.account_classified.category_band",
        )
    path = tmp_path / "model.orm.json"
    path.write_text(json.dumps(authored))
    result = render_ossie(path, output_format="json")
    assert absent not in _formula_counts(json.loads(result.document))
    assert _rows(result)[pointer] == "extension"
    assert pointer in {
        key for group in json.loads(result.sidecar)["elements"].values() for key in group
    }


def test_scaled_formula_projection_time_bound(tmp_path):
    authored = json.loads(SOURCE.read_bytes())
    prototype = authored["constraints"][4]
    authored["constraints"] = [dict(prototype, id=f"value_{i}") for i in range(1_000)]
    source_fact = authored["fact_types"][5]
    authored["fact_types"] = [dict(source_fact, id=f"classification_{i}") for i in range(1_000)]
    path = tmp_path / "many.orm.json"
    path.write_text(json.dumps(authored))
    model = load_model(path)
    start = monotonic()
    ontology, _ = _ontology(authored, model)
    assert sum(len(concept.get("requires", ())) for concept in ontology["ontology"]) == 1_000
    assert monotonic() - start < 4.0


def _render_authored(tmp_path, document):
    path = tmp_path / "changed.orm.json"
    path.write_text(json.dumps(document))
    return render_ossie(path, output_format="json")


def test_formula_excludes_governance_fields(tmp_path):
    authored = json.loads(SOURCE.read_bytes())
    authored["constraints"][0].update(owner="host", allowed_fixes=["add-fact"])
    rows = _rows(_render_authored(tmp_path, authored))
    assert rows["/constraints/0"] == "requires"
    for child in ("owner", "allowed_fixes", "allowed_fixes/0"):
        assert rows[f"/constraints/0/{child}"] == "extension"


@pytest.mark.parametrize("variant", ("entity", "subtype", "supertype", "multi_clause"))
def test_reviewed_player_and_clause_boundary(tmp_path, variant):
    authored = json.loads(SOURCE.read_bytes())
    account = authored["object_types"][0]
    if variant == "entity":
        account.pop("primitive")
        account.update(kind="entity", reference={"mode": "general", "value_type": "category"})
    elif variant == "subtype":
        account.update(subtype_of=["category"], inherits_reference=False)
    elif variant == "supertype":
        authored["object_types"].append(
            dict(account, id="member", name="Member", subtype_of=["account"], inherits_reference=False)
        )
    else:
        rule = authored["fact_types"][7]["derivation_rule"]
        body = rule.pop("body")
        rule["clauses"] = [{"body": body}, {"body": body}]
    rows = _rows(_render_authored(tmp_path, authored))
    assert rows["/fact_types/7/derivation_rule"] == "extension"
    if variant != "multi_clause":
        for i in (0, 1, 2, 3, 5):
            assert rows[f"/constraints/{i}"] == "extension"
        assert rows["/fact_types/4/constraints/0"] == "extension"
    assert rows["/constraints/4"] == ("extension" if variant == "subtype" else "requires")


def test_equality_rolls_back_a_successful_first_direction(tmp_path, monkeypatch):
    from gnd.export.ossie_formulas import ProjectedRelation, _Unprojected

    original = ProjectedRelation.path
    attempted = []

    def refuse_second(relation):
        attempted.append(relation.target["name"])
        if len(attempted) == 2:
            raise _Unprojected
        return original(relation)

    authored = json.loads(SOURCE.read_bytes())
    authored["constraints"] = [authored["constraints"][2]]
    authored["fact_types"] = authored["fact_types"][:5]
    monkeypatch.setattr(ProjectedRelation, "path", refuse_second)
    result = _render_authored(tmp_path, authored)
    assert len(attempted) == 2 and len(set(attempted)) == 2
    assert _rows(result)["/constraints/0"] == "extension"
    assert not any(text.startswith("Account.") for _, _, text in _formula_counts(json.loads(result.document)))


def test_projected_roles_bind_guard_and_chain_after_determinant_reordering(tmp_path):
    authored = json.loads(SOURCE.read_bytes())
    for i, first, reading in (
        (0, "account", "{Amount} is the balance of {Account}"),
        (5, "account", "{Category} classifies {Account}"),
        (6, "category", "{Band} groups {Category}"),
        (7, "account", "{Band} contains {Account}"),
    ):
        fact = authored["fact_types"][i]
        fact["roles"].reverse()
        fact["reading"] = reading
        fact.setdefault("constraints", []).append({
            "id": f"determinant_{i}", "type": "uniqueness", "roles": [first],
            "modality": "alethic", "source": "explicit", "status": "confirmed",
            "provenance": {"user_quote": "An authored determinant."},
        })
    result = _render_authored(tmp_path, authored)
    formulas = _formula_counts(json.loads(result.document))
    baseline = _formula_counts(json.loads(render_ossie(SOURCE, output_format="json").document))
    assert formulas == baseline
    rows = _rows(result)
    assert rows["/constraints/0"] == rows["/fact_types/7/derivation_rule"] == "requires"


def test_shared_requirement_entry_points_keep_named_parts():
    from gnd.export.pyrel_rules import constraint_context, constraint_requirements

    source = json.loads(SOURCE.read_bytes())
    context = constraint_context(source)
    assert constraint_requirements(context, source["constraints"][0])[0].check.compare.right == 100
    equality = constraint_requirements(context, source["constraints"][2])
    assert [requirement.domain[0].relation for requirement in equality] == [
        "account_active", "account_registered",
    ]
    ring = constraint_requirements(context, source["fact_types"][4]["constraints"][0], "account_recommends")
    assert ring[0].check.compare.operator == "!="


def test_comparison_kind_is_checked_before_emission(tmp_path, monkeypatch):
    from dataclasses import replace

    from gnd.export import ossie_formulas

    lower = ossie_formulas.constraint_requirements

    def unsupported_kind(*args):
        requirements = lower(*args)
        return [
            replace(row, check=replace(row.check, kind="absent"))
            if row.check.kind == "compare" else row
            for row in requirements
        ]

    monkeypatch.setattr(ossie_formulas, "constraint_requirements", unsupported_kind)
    rows = _rows(_render_authored(tmp_path, json.loads(SOURCE.read_bytes())))
    assert rows["/constraints/0"] == rows["/constraints/5"] == "extension"
    assert rows["/fact_types/4/constraints/0"] == "extension"


def test_derived_on_derived_source_is_an_extension(tmp_path):
    authored = json.loads(SOURCE.read_bytes())
    derived = dict(authored["fact_types"][5], id="classification_claim", derivation="derived")
    authored["fact_types"][7]["derivation_rule"]["body"][0]["fact_type"] = derived["id"]
    derived["derivation_rule"] = {
        "body": [{"fact_type": "account_classified", "bind": {"account": "$a", "category": "$c"}}],
        "head": {"account": "$a", "category": "$c"},
    }
    authored["fact_types"].append(derived)
    rows = _rows(_render_authored(tmp_path, authored))
    assert rows["/fact_types/7/derivation_rule"] == "extension"
    assert rows["/fact_types/8/derivation_rule"] == "extension"


def test_shared_index_and_lowering_work_for_scaled_mixed_formulas(tmp_path, monkeypatch):
    from gnd.export import ossie_formulas

    authored = json.loads(SOURCE.read_bytes())
    count = 180
    guarded, subset, *_, value, cardinality = authored["constraints"]
    authored["constraints"] = [
        dict(rule, id=f"rule_{index}_{rule['id']}")
        for index in range(count)
        for rule in (guarded, subset, value, cardinality)
    ]
    ring, chain = (authored["fact_types"][index] for index in (4, 7))
    for i in range(count):
        ring_rule = dict(ring["constraints"][0], id=f"ring_rule_{i}")
        authored["fact_types"].extend(
            (dict(ring, id=f"ring_{i}", constraints=[ring_rule]), dict(chain, id=f"chain_{i}"))
        )
    calls = Counter()
    index = ossie_formulas.constraint_context
    lower = ossie_formulas.constraint_requirements

    def indexed(*args):
        calls["indexed"] += 1
        return index(*args)

    def lowered(*args):
        calls[args[1]["type"]] += 1
        return lower(*args)

    monkeypatch.setattr(ossie_formulas, "constraint_context", indexed)
    monkeypatch.setattr(ossie_formulas, "constraint_requirements", lowered)
    result = _render_authored(tmp_path, authored)
    assert calls == {
        "indexed": 1, "guarded": count, "subset": count, "value": count,
        "cardinality": count, "ring": count + 1,
    }
    formulas = _formula_counts(json.loads(result.document))
    assert sum(formulas.values()) == 6 * count + 2
