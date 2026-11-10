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
