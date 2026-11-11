"""Ordinary static controls for the optional consumer comparison."""

from tools.ossie_consumer import call_counts, ontology_declarations, pyrel_declarations


def test_compare_exact_names_parents_relationships_and_identifiers():
    ontology = {
        "ontology": [
            {"concept": "Code", "extends": ["String"]},
            {
                "concept": "Model",
                "relationships": [{"name": "code"}, {"name": "alternate"}],
                "identify_by": ["code"],
            },
            {"concept": "Preferred", "extends": ["Model"]},
        ],
    }
    source = b"""
Model_2 = m.Concept("Model")
Code = m.Concept("Code", extends=[String])
Preferred = m.Concept("Preferred", extends=[Model_2])
Model_2.code = m.Property(f"{Model_2} has {Code}")
Model_2.alternate = m.Relationship(f"{Model_2} also uses {Code}")
Model_2.identify_by(Model_2.code)
m.where(Preferred(x)).require(Code(x))
"""
    expected = ontology_declarations(ontology)
    assert not expected.difference(pyrel_declarations(source))
    assert call_counts(source)["require"] == 1
    altered = source.replace(b"extends=[Model_2]", b"extends=[Code]").replace(
        b"Model_2.alternate = m.Relationship", b"Model_2.other = m.Relationship"
    ).replace(b"identify_by(Model_2.code)", b"identify_by(Model_2.other)")
    assert expected.difference(pyrel_declarations(altered)) == {
        "parents": {"missing": [("Preferred", "Model")], "extra": [("Preferred", "Code")]},
        "relationships": {"missing": [("Model", "alternate")], "extra": [("Model", "other")]},
        "identifiers": {"missing": [("Model", "code")], "extra": [("Model", "other")]},
    }


def test_os0_refund_snapshot_is_compared_without_a_converter():
    from pathlib import Path

    from ruamel.yaml import YAML

    evidence = (
        Path(__file__).resolve().parents[1]
        / ".gnd-planning/milestones/ossie-interchange/evidence/OS0"
    )
    ontology = YAML(typ="safe").load((evidence / "refunds.yaml").read_bytes())
    snapshot = (evidence / "E3-refunds.pyrel.txt").read_bytes()
    assert not ontology_declarations(ontology).difference(pyrel_declarations(snapshot))
