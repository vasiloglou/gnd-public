"""Exercise time quantity admission and exact replay at the public boundary."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from gnd.anchors import recognised_ranges, recognition_index, vocabulary_digest
from gnd.artifacts import canonical_json_bytes, sha256_hex

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "src/gnd/examples/literature/quantity_fixture"
DECIMAL = EXAMPLE.parent / "depth_fixture"
EXPECTED = json.loads((Path(__file__).parent / "fixtures/ld2-quantities/expected.json").read_bytes())


def _cli(folder, *args):
    command = subprocess.run(
        [sys.executable, "-m", "gnd", *args], cwd=folder,
        capture_output=True, check=False, timeout=20,
    )
    return command.returncode, json.loads(command.stdout)


@pytest.fixture
def example(tmp_path):
    folder = tmp_path / "case"
    shutil.copytree(EXAMPLE, folder)
    return folder


def _anchors(folder, span, occurrence=0):
    document = (folder / "source.txt").read_bytes()
    start = document.index(span.encode())
    end = start + len(span)
    population = (folder / "time.population.json").read_bytes()
    roles = json.loads(population)["facts"]["time_step"][0]
    model = YAML(typ="safe").load((folder / "time.orm.yaml").read_text())
    sidecar = {
        "schema_version": 2, "population_sha256": sha256_hex(population),
        "vocabulary_digest": vocabulary_digest(model), "document_sha256": sha256_hex(document),
        "anchors": [{
            "fact_key": {"fact_type": "time_step", "roles": roles}, "role": "coefficient",
            "span": {"start": start, "end": end}, "occurrence": occurrence,
            "excerpt_sha256": sha256_hex(document[start:end]),
        }],
    }
    (folder / "time.anchors.json").write_bytes(canonical_json_bytes(sidecar))


def _check(folder):
    return _cli(folder, "check", "time.orm.yaml", "time.population.json",
                "--document", "source.txt", "--anchors", "time.anchors.json", "--format", "json")


@pytest.mark.parametrize(("span", "occurrence", "expected_exit"), EXPECTED["spans"])
def test_time_dimension_through_public_check(example, span, occurrence, expected_exit):
    _anchors(example, span, occurrence)
    code, result = _check(example)
    assert code == expected_exit, result
    verdict = next(row for row in result["verdicts"] if row["constraint_type"] == "anchored")
    assert verdict["verdict"] == ("pass" if expected_exit == 0 else "fail")


@pytest.mark.parametrize("source", ["2eV", "2 fs2", "2 ps_extra", "2.0.0 fs", "2 fs-1",
                                    "2\nfs", "2% fs", "2,00 fs", "1e3 fs", "9999999999999999999 fs"])
def test_time_quantity_refuses_malformed_or_out_of_range_tokens(source):
    assert recognition_index(source, {"time-fs"}) == {"time-fs": {}}


def test_selector_requires_integer(example):
    path = example / "time.orm.yaml"
    model = YAML(typ="safe").load(path.read_text())
    model["object_types"][0]["primitive"] = "String"
    path.write_bytes(canonical_json_bytes(model))
    code, result = _cli(example, "validate", path.name, "--format", "json")
    assert code == 3
    assert any(row["rule_id"] == "semantic:anchored-invalid" for row in result["issues"])


def test_time_range_prefix_and_large_input():
    document = ("2 eV; 0.002 ps; 2 fs; " * 40_000) + "0.000002 ns"
    code = (
        "from gnd.anchors import recognition_index; import sys; "
        "index = recognition_index(sys.stdin.read(), {'time-fs'}, limits={'time-fs': {2: 2}}); "
        "assert index == {'time-fs': {2: [(6, 14), (16, 20), (28, 36)]}}, index"
    )
    result = subprocess.run([sys.executable, "-c", code], input=document, text=True,
                            capture_output=True, timeout=12, check=False)
    assert result.returncode == 0, result.stderr
    assert recognised_ranges(recognition_index("-0.002 ps", {"time-fs"}), "time-fs", -2) == [(0, 9)]


def test_exact_witness_tuple_replays(example):
    _anchors(example, "0.002 ps", 1)
    assert _check(example)[0] == 0
    files = ("time.orm.yaml", "time.population.json")
    code, response = _cli(example, "witness", *files, "--targets", "time.targets.json", "--raw", "--out", "proof.json")
    assert code == 0, response
    code, replay = _cli(example, "replay", *files, "proof.json", "--raw")
    assert code == 0, replay
    coefficient, places, unit = [cell["value"] for cell in replay["results"][0]["target"]["tuple"]]
    assert [coefficient, places, unit] == EXPECTED["tuple"]
    assert str(Decimal(coefficient).scaleb(-places)) == EXPECTED["exact_decimal"]
    proof = example / "proof.json"
    certificate = json.loads(proof.read_bytes())
    certificate["nodes"][0]["tuple"][1]["value"] = 4
    proof.write_bytes(canonical_json_bytes(certificate))
    assert _cli(example, "replay", *files, "proof.json", "--raw")[0] != 0


@pytest.mark.parametrize(("field", "wrong"), [("unit", "fs"), ("places", 4)])
def test_fixed_scale_and_unit_are_checked(example, field, wrong):
    path = example / "time.population.json"
    population = json.loads(path.read_bytes())
    population["facts"]["time_step"][0][field] = wrong
    path.write_bytes(canonical_json_bytes(population))
    _anchors(example, "2 fs")
    code, report = _check(example)
    assert code == 1, report
    assert any(row["constraint_type"] == "value" and row["verdict"] == "fail" for row in report["verdicts"])


@pytest.mark.parametrize("primitive", ["Number", "Float"])
def test_native_fractional_witness_refusal(tmp_path, primitive):
    for source in DECIMAL.glob("decimal.*.json"):
        name = source.name
        (tmp_path / name).write_text(source.read_text().replace('"Number"', f'"{primitive}"'))
    files = ("decimal.orm.json", "decimal.population.json")
    assert _cli(tmp_path, "check", *files, "--format", "json")[0] == 0
    code, report = _cli(tmp_path, "witness", *files, "--targets", "decimal.targets.json", "--raw")
    assert code == 2
    assert report["results"][0]["reason"] == EXPECTED["native_refusal"]
