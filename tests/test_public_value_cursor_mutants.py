"""Generic runtime value mutation counterexamples; no formal tools execute."""
import inspect
import runpy
from pathlib import Path

import pytest
from test_v6_phase2_value_helpers import constraint, fact, snapshot

from gnd import semantic_spec as spec
from gnd.semantic_adapter import canonical_scalar
from gnd.semantic_ir import IRRelation, IRRole, IRRoster


def object_case(values, variant="enum", **changes):
    changes.setdefault("object_type", "score")
    rule = constraint(variant, **changes)
    return rule, snapshot(rosters=(IRRoster("score", tuple(values), ()),))


def role_case(rows, variant="enum-role", **changes):
    roles = (
        IRRole("decoy", "score", "Integer"),
        IRRole("quantity", "score", "Integer"),
    )
    rule = constraint(variant, role_refs=(("observed", "quantity"),), **changes)
    data = snapshot(
        fact_types=(fact("observed", roles),),
        relations=(IRRelation("observed", tuple(rows), ()),),
    )
    return rule, data


@pytest.mark.parametrize(
    "name",
    [
        "cursor-object-selection",
        "cursor-role-column",
        "cursor-witness-omission",
        "cursor-witness-duplication",
        "cursor-witness-reorder",
        "cursor-unknown-to-fail",
    ],
)
def test_direct_cursor_mutants_have_concrete_counterexamples(tmp_path, name):
    source = Path(inspect.getfile(spec))
    proof = runpy.run_path(str(source.parents[2] / "tests/test_v6_phase2_spec_proof.py"))
    _, function, before, after = next(
        row for row in proof["VALUE_MUTATIONS"] if row[0] == name
    )
    mutant = tmp_path / "mutant.py"
    mutant.write_text(proof["_mutated_source"](source.read_text(), function, before, after))
    changed = runpy.run_path(str(mutant))
    good = canonical_scalar(20, None)
    first = canonical_scalar(130, None)
    second = canonical_scalar(120, None)
    if name == "cursor-object-selection":
        rule, data = object_case((good,), allowed=(good,))
        args, expected, wrong = (rule, data), (1, 0, -1), (0, -1, -1)
    elif name == "cursor-role-column":
        rule, data = role_case(((first, good),), allowed=(good,))
        args, expected, wrong = (rule, data), (2, 0, 1), (2, 0, 0)
    elif name == "cursor-unknown-to-fail":
        rule, data = object_case((None,), allowed=(good,))
        args, expected, wrong = ((1, 0, -1), rule, data, 0), -1, 0
    else:
        rule, data = object_case((first, second), allowed=(good,))
        args = ((1, 0, -1), rule, data)
        expected = [first, second]
        wrong = {
            "cursor-witness-omission": [first],
            "cursor-witness-duplication": [first, first, second, second],
            "cursor-witness-reorder": [second, first],
        }[name]
    assert getattr(spec, function)(*args) == expected
    assert changed[function](*args) == wrong

