"""Explicitly selected external Ossie validation against the OS0 pin."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from gnd.errors import ModelValidationError
from gnd.export.ossie import render_ossie
from tools.ossie_oracle import OssieOracle

pytestmark = pytest.mark.ossie_oracle
ROOT = Path(__file__).resolve().parents[1]
CENSUS = (
    (ROOT / ".gnd-planning/milestones/ossie-interchange/evidence/OS0/revised/census.txt")
    .read_text()
    .splitlines()
)


@pytest.fixture(scope="module")
def oracle():
    raw = os.environ.get("GND_OSSIE_ORACLE_ROOT")
    if not raw:
        pytest.fail("set GND_OSSIE_ORACLE_ROOT to the pinned scratch oracle environments")
    result = OssieOracle(Path(raw).resolve())
    result.check_pins()
    return result


INCLUDE_ROOTS = {
    "src/gnd/examples/expense/teams/engineering.orm.json",
    "src/gnd/examples/expense/teams/sales-v2.orm.json",
    "src/gnd/examples/expense/teams/sales.orm.json",
}


@pytest.mark.parametrize("relative", CENSUS)
def test_external_census(oracle, tmp_path, relative):
    if relative in INCLUDE_ROOTS:
        with pytest.raises(ModelValidationError, match="include:unsupported-route"):
            render_ossie(ROOT / relative, output_format="yaml")
        return
    bundle = render_ossie(ROOT / relative, output_format="yaml")
    path = tmp_path / "ontology.yaml"
    path.write_bytes(bundle.document)
    for read in (oracle.validate, oracle.parse):
        result = read(path)
        assert result.returncode == 0, result.stdout + result.stderr


def test_external_refusal_is_live(oracle, tmp_path):
    document = {
        "version": "0.3.0.dev0",
        "name": "BadReference",
        "ontology": [
            {
                "concept": "A",
                "type": "EntityType",
                "relationships": [
                    {
                        "name": "rel",
                        "roles": [{"concept": "Missing"}],
                        "verbalizes": ["{A} relates {Missing}"],
                    }
                ],
            }
        ],
    }
    path = tmp_path / "unknown.json"
    path.write_text(json.dumps(document))
    for read in (oracle.validate, oracle.parse):
        result = read(path)
        assert result.returncode == 1
        assert "Missing" in result.stdout + result.stderr


def test_yaml_role_name_is_a_string_in_both_upstream_readers(oracle, tmp_path):
    model = tmp_path / "source.json"
    model.write_text(
        json.dumps(
            {
                "version": 1,
                "object_types": [
                    {"id": "a", "name": "A", "kind": "value", "primitive": "String"},
                    {"id": "b", "name": "B", "kind": "value", "primitive": "String"},
                ],
                "fact_types": [
                    {
                        "id": "paired",
                        "reading": "{A} pairs {B}",
                        "roles": [
                            {"object_type": "a", "role_name": "first"},
                            {"object_type": "b", "role_name": "on"},
                        ],
                    }
                ],
            }
        )
    )
    output = tmp_path / "ontology.yaml"
    output.write_bytes(render_ossie(model, output_format="yaml").document)
    for read in (oracle.validate, oracle.parse):
        result = read(output)
        assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("scope", ("ontology", "concept", "relationship", "derivation"))
def test_pinned_parser_accepts_exported_os2_corpus(oracle, tmp_path, scope):
    source = (
        ROOT / ".gnd-planning/milestones/ossie-interchange/evidence/OS2/corpus-r2/model.orm.json"
    )
    result = render_ossie(source, output_format="json")
    path = tmp_path / "ontology.json"
    path.write_bytes(result.document)
    for read in (oracle.validate, oracle.parse):
        accepted = read(path)
        assert accepted.returncode == 0, accepted.stdout + accepted.stderr

    document = json.loads(result.document)
    concepts = document["ontology"]
    relationships = [rel for concept in concepts for rel in concept.get("relationships", ())]
    targets = {
        "ontology": document["requires"],
        "concept": next(concept["requires"] for concept in concepts if "requires" in concept),
        "relationship": next(rel["requires"] for rel in relationships if "requires" in rel),
        "derivation": next(rel["derived_by"] for rel in relationships if "derived_by" in rel),
    }
    targets[scope][0] = "COUNT[Account >"
    path.write_text(json.dumps(document))
    refused = oracle.parse(path)
    assert refused.returncode == 1 and "Unable to parse" in refused.stderr


def test_pinned_formula_keywords_are_case_sensitive(oracle, tmp_path):
    from tests.test_ossie_formulas import SOURCE

    document = json.loads(SOURCE.read_bytes())
    balance = document["fact_types"][0]
    balance["roles"][1]["role_name"] = "count"
    document["constraints"][0]["antecedent"][0]["bind"]["count"] = (
        document["constraints"][0]["antecedent"][0]["bind"].pop("balance")
    )
    for constraint in document["constraints"]:
        for key in ("role_seq_a", "role_seq_b"):
            for role in constraint.get(key, ()):
                if role["fact_type"] == "account_active":
                    role["fact_type"] = "exists"
    document = json.loads(json.dumps(document).replace('"account_active"', '"exists"'))
    source = tmp_path / "source.orm.json"
    source.write_text(json.dumps(document))
    ontology = json.loads(render_ossie(source, output_format="json").document)
    account = ontology["ontology"][0]
    assert account["relationships"][0]["requires"] == ["count <= 100"]
    assert any(
        "Account.exists" in rel.get("requires", ()) for rel in account["relationships"]
    )
    path = tmp_path / "ontology.json"
    path.write_text(json.dumps(ontology))
    accepted = oracle.parse(path)
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr

    relationship = account["relationships"][0]
    relationship["roles"][0]["name"] = "COUNT"
    relationship["verbalizes"][0] = relationship["verbalizes"][0].replace(":count", ":COUNT")
    relationship["requires"] = ["COUNT <= 100"]
    path.write_text(json.dumps(ontology))
    refused = oracle.parse(path)
    assert refused.returncode == 1 and "Unable to parse" in refused.stderr
