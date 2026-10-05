"""Generic runtime value mutation counterexamples; no formal tools execute."""
from dataclasses import replace

import pytest

from gnd import semantic_spec as spec
from gnd.semantic_adapter import canonical_scalar
from gnd.semantic_ir import IRConstraint, IRFactType, IRRelation, IRRole, IRRoster, SnapshotIR


def constraint(variant, **changes):
    value = IRConstraint(
        ref="value-test",
        family="value",
        variant=variant,
        modality="alethic",
        fact_type="",
        roles=(),
        role_refs=(),
        sequences=(),
        object_type="score",
        subtypes=(),
        flags=(),
        minimum=None,
        maximum=None,
        allowed=(),
        ranges=(),
        operator="",
        literal=None,
        operands=(),
        consequent_kind="",
        antecedent=(),
        consequent=(),
        scope_fact_types=(),
        expression="",
        refused="",
    )
    return replace(value, **changes)


def snapshot(**changes):
    value = SnapshotIR(
        object_types=(),
        fact_types=(),
        relations=(),
        rosters=(),
        constraints=(),
        finite=True,
        covers=(),
        explicit_rosters=(),
        derivations=(),
        derivation_order=(),
        refusals=(),
    )
    return replace(value, **changes)


def fact(name, roles=()):
    return IRFactType(
        id=name,
        roles=roles,
        declared=True,
        derivation="",
        structured_rule=False,
        relation_source="claimed",
        opaque_rule="",
    )


@pytest.mark.parametrize(
    "name",
    [
        "value-enum-state",
        "value-range-flags",
        "value-range-inclusivity",
        "value-ranges-state",
        "snapshot-roster-index-tail",
        "snapshot-fact-index-tail",
        "snapshot-relation-index-tail",
        "fact-role-index-tail",
        "projection-tail",
        "projection-cell-omission",
        "projection-wrong-column",
        "projection-refusal",
    ],
)
def test_helper_mutants_have_concrete_counterexamples(tmp_path, name):
    import runpy
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    proof = runpy.run_path(str(root / "tests/test_v6_phase2_spec_proof.py"))
    mutations = proof["MUTATIONS"]
    _, function, before, after = next(row for row in mutations if row[0] == name)
    source = Path(spec.__file__).read_text()
    mutant_path = tmp_path / "mutant.py"
    mutant_path.write_text(proof["_mutated_source"](source, function, before, after))
    mutated = runpy.run_path(str(mutant_path))
    number, text = canonical_scalar(0, None), canonical_scalar("text", None)
    if name == "value-range-flags":
        rule = constraint("range", flags=(True,) * 3)
        assert spec.value_cell_state(number, rule) == -1
        with pytest.raises(IndexError):
            mutated[function](number, rule)
        return
    if name.startswith("value-"):
        rule = {
            "value-enum-state": constraint("enum", allowed=(number,)),
            "value-range-inclusivity": constraint(
                "range", minimum=number, flags=(True, True, True, False)
            ),
            "value-ranges-state": constraint("ranges", ranges=((None, None, True, True),)),
        }[name]
        args, expected, wrong = (number, rule), 1, 0
    elif name == "snapshot-roster-index-tail":
        args, expected, wrong = (snapshot(rosters=(IRRoster("last", (), ()),)), "last"), 0, -1
    elif name == "snapshot-fact-index-tail":
        args, expected, wrong = (snapshot(fact_types=(fact("last"),)), "last"), 0, -1
    elif name == "snapshot-relation-index-tail":
        args, expected, wrong = (snapshot(relations=(IRRelation("last", (), ()),)), "last"), 0, -1
    elif name == "fact-role-index-tail":
        args, expected, wrong = (fact("f", (IRRole("last", "score", "Integer"),)), "last"), 0, -1
    elif name == "projection-refusal":
        args, expected, wrong = (((number,),), 1), (False, []), (True, [])
    elif name == "projection-tail":
        args, expected, wrong = (((number,),), 0), (True, [number]), (True, [])
    else:
        # Exercise the selected append helper through its actual caller.
        function = "project_optional_column"
        args, expected = (((text, number),), 1), (True, [number])
        wrong = (True, [None if name == "projection-cell-omission" else text])
    assert getattr(spec, function)(*args) == expected
    assert mutated[function](*args) == wrong

