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


@pytest.mark.parametrize("relative", CENSUS)
def test_external_census(oracle, tmp_path, relative):
    try:
        bundle = render_ossie(ROOT / relative, output_format="yaml")
    except ModelValidationError as error:
        assert "/expense/teams/" in relative
        assert "include:unsupported-route" in str(error)
        return
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
