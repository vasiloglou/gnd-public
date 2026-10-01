"""Tagged value-comparison operands stay coherent through synth and measure."""

from __future__ import annotations

import io
import json
from pathlib import Path
from random import Random

import pytest
from ruamel.yaml import YAML
from support.documents import write_model

from gnd.cli import main
from gnd.model import load_model
from gnd.synth.assemble import assemble_conforming
from gnd.synth.boundary import enumerate_boundary
from gnd.synth.comparison import _UNTYPEABLE, normalize_operands


def _write_model(
    tmp_path: Path,
    primitive: str,
    operator: str,
    role_a: object,
    role_b: object,
) -> Path:
    document = {
        "version": 1,
        "source": {
            "kind": "text-conversation",
            "confidence": "standard",
            "mode": "guided",
        },
        "object_types": [
            {"id": "datum_type", "name": "Datum", "kind": "value", "primitive": primitive}
        ],
        "fact_types": [
            {
                "id": "sample_fact",
                "reading": "{Datum} is sampled",
                "roles": [{"object_type": "datum_type", "role_name": "datum"}],
                "constraints": [
                    {
                        "type": "value-comparison",
                        "operator": operator,
                        "role_a": role_a,
                        "role_b": role_b,
                        "source": "explicit",
                        "status": "confirmed",
                        "modality": "alethic",
                        "provenance": {"user_quote": "A tagged comparison."},
                    }
                ],
            }
        ],
    }
    encoded = io.StringIO()
    YAML().dump(document, encoded)
    return write_model(tmp_path, encoded.getvalue(), name=f"{primitive.lower()}.orm.yaml")


def _synth_and_measure(model_path: Path, out: Path) -> tuple[int, list[object]]:
    assert main(["synth", str(model_path), "--out", str(out), "--seed", "17"]) == 0
    index = json.loads((out / "index.json").read_text(encoding="utf-8"))
    population_path = out / index["populations"][0]["population"]
    population = json.loads(population_path.read_text(encoding="utf-8"))
    values = [fact["datum"] for fact in population["facts"]["sample_fact"]]
    measure_code = main(["measure", str(model_path), "--populations", str(out), "--format", "json"])
    return measure_code, values


@pytest.mark.parametrize(
    "primitive,literal",
    [
        pytest.param("String", "001", id="string"),
        pytest.param("Boolean", True, id="boolean"),
        pytest.param("Integer", 7, id="numeric"),
        pytest.param("Date", "2035-06-15", id="date"),
    ],
)
def test_tagged_role_and_literal_synthesize_and_measure(
    primitive: str, literal: object, tmp_path: Path
) -> None:
    model_path = _write_model(tmp_path, primitive, "=", {"role": "datum"}, {"literal": literal})

    measure_code, values = _synth_and_measure(model_path, tmp_path / "corpus")

    assert measure_code == 0
    assert values and all(value == literal for value in values)


def test_tagged_literal_on_the_left_reverses_the_operator(tmp_path: Path) -> None:
    model_path = _write_model(tmp_path, "Integer", "<=", {"literal": 7}, {"role": "datum"})

    measure_code, values = _synth_and_measure(model_path, tmp_path / "corpus")

    assert measure_code == 0
    assert values and all(value >= 7 for value in values)


def test_tagged_numeric_literal_derives_boundary_cases(tmp_path: Path) -> None:
    model_path = _write_model(tmp_path, "Integer", "<=", {"role": "datum"}, {"literal": 7})
    model = load_model(model_path)
    baseline = assemble_conforming(model, 17, model_ref=model_path.name)

    cases, _downs = enumerate_boundary(model, baseline.doc, Random(17))

    comparison_cases = [case for case in cases if case.family == "value-comparison"]
    assert {case.side for case in comparison_cases} == {"inside", "outside"}


def test_tagged_untypeable_literal_is_measured_as_unchecked(tmp_path: Path) -> None:
    model_path = _write_model(tmp_path, "Integer", "<=", {"role": "datum"}, {"literal": "seven"})
    model = load_model(model_path)
    fact_type = model.fact_types[0]
    constraint = fact_type["constraints"][0]
    _role, literal = normalize_operands(model, constraint, fact_type)

    measure_code, _values = _synth_and_measure(model_path, tmp_path / "corpus")

    assert literal.kind == "literal" and literal.value is _UNTYPEABLE
    assert measure_code == 0


def test_legacy_bare_string_operands_remain_supported(tmp_path: Path) -> None:
    model_path = _write_model(tmp_path, "String", "=", "datum", "001")

    measure_code, values = _synth_and_measure(model_path, tmp_path / "corpus")

    assert measure_code == 0
    assert values and all(value == "001" for value in values)
