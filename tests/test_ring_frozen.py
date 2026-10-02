"""Behavioral invariants for Amendment A's local ring semantics.

ORM 2 reflexivity is local to values participating in the relation; unrelated
roster members do not need self-pairs. These tests pin that contract without
coupling correctness to function source text.
"""

from __future__ import annotations

import pytest
from conftest import make_population

from gnd.checker import check
from gnd.model import Model


def _ring_model(variant: str) -> Model:
    return Model(
        version=1,
        object_types=[{"id": "node", "kind": "value", "primitive": "String"}],
        fact_types=[
            {
                "id": "relates",
                "reading": "{source} relates to {target}",
                "roles": [
                    {"object_type": "node", "role_name": "source"},
                    {"object_type": "node", "role_name": "target"},
                ],
                "constraints": [
                    {"type": "ring", "variant": variant, "modality": "alethic"}
                ],
            }
        ],
    )


def _verdict(variant: str, pairs: list[tuple[str, str]]):
    model = _ring_model(variant)
    population = make_population(
        model,
        model="ring.orm.yaml",
        source="fixture",
        covers=["relates"],
        instances={"node": ["A", "B", "roster_only"]},
        facts={
            "relates": [
                {"source": source, "target": target} for source, target in pairs
            ]
        },
    )
    return check(model, population).verdicts[0]


def test_local_reflexivity_ignores_roster_only_members():
    assert _verdict(
        "reflexive", [("A", "B"), ("A", "A"), ("B", "B")]
    ).verdict == "pass"


def test_local_reflexivity_requires_self_pair_for_each_participant():
    verdict = _verdict("reflexive", [("A", "B"), ("B", "B")])
    assert verdict.verdict == "fail"
    assert ["A"] in verdict.offending_facts
    assert ["roster_only"] not in verdict.offending_facts


def test_purely_reflexive_ignores_roster_only_members():
    assert _verdict("purely-reflexive", [("A", "A"), ("B", "B")]).verdict == "pass"


@pytest.mark.parametrize("pair", [("A", "B"), ("B", "A")])
def test_purely_reflexive_rejects_every_off_diagonal_pair(pair):
    verdict = _verdict("purely-reflexive", [pair])
    assert verdict.verdict == "fail"
    assert list(pair) in verdict.offending_facts
