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
