"""Current executable mutation and foundation guards; no formal proof invocation."""
import importlib
import json
import runpy
from pathlib import Path

import pytest

from gnd.semantic_adapter import canonical_scalar

ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture
def spec():
    return importlib.import_module("gnd.semantic_spec")


@pytest.mark.parametrize(
    "name",
    [
        "missing-duplicates",
        "range-min-inclusivity",
        "range-max-inclusivity",
        "range-incomparability",
        "ranges-tail",
        "ranges-inclusion-precedence",
        "aggregate-row-omission",
    ],
)
def test_formal_mutants_have_concrete_counterexamples(spec, tmp_path, name):
    proof = runpy.run_path(str(ROOT / "tests/test_v6_phase2_spec_proof.py"))
    mutations = proof["MUTATIONS"]
    _, function, before, after = next(row for row in mutations if row[0] == name)
    source = Path(spec.__file__).read_text()
    mutant_path = tmp_path / "semantic_mutant.py"
    mutant_path.write_text(proof["_mutated_source"](source, function, before, after))
    namespace = runpy.run_path(str(mutant_path))
    value, text = canonical_scalar(0, None), canonical_scalar("text", None)
    inside, unknown = (None, None, True, True), (text, None, True, True)
    cases = {
        "missing-duplicates": (((value, value), ()), [value], [value, value]),
        "range-min-inclusivity": ((value, value, None, True, True), 1, 0),
        "range-max-inclusivity": ((value, None, value, True, True), 1, 0),
        "range-incomparability": ((value, None, text, True, True), -1, 1),
        "ranges-tail": ((value, (inside,)), 1, 0),
        "ranges-inclusion-precedence": ((value, (unknown, inside)), 1, -1),
        "aggregate-row-omission": (([],), [[]], []),
    }
    args, expected, wrong = cases[name]
    assert getattr(spec, function)(*args) == expected
    assert namespace[function](*args) == wrong


def test_formal_foundation_matches_source_review_answers(spec):
    directory = ROOT / "proof/v6/semantics"
    cases = json.loads((directory / "source-review-cases.json").read_text())["cases"]
    expected = json.loads((directory / "source-review-expected.json").read_text())["answers"]
    for case in cases:
        answer = expected[case["id"]]
        if case["kind"] == "temporal":
            left, right = [canonical_scalar(case[key], "DateTime") for key in ("left", "right")]
            assert spec.scalar_order(left, right) == answer["instant_comparison"]
            assert spec.scalar_identical(left, right) == answer["identity_equal"]
        elif case["kind"] == "assurance":
            assert (
                spec.assurance_for_route(
                    case["applicable"],
                    case["current"],
                    case["in_scope"],
                    True,
                    True,
                    case["route"] == "verify",
                    case["authenticated"],
                )
                == answer["assurance"]
            )

