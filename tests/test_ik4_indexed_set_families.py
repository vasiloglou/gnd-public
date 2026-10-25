"""IK4: indexed equality, exclusion and frequency must equal the specification exactly.

Owner rulings 2026-10-24 (IK4 spec §16, F2): the quadratic specification paths
made ``gnd discover`` infeasible on a near-cap population, so equality,
exclusion and (by a second ruling) frequency gain production fast paths like
subset's. Every verdict, reason and witness must
equal ``semantic_spec.verdict_of``.
"""

from __future__ import annotations

import json
import random
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from gnd import api, semantic_rows, semantic_spec
from gnd.constraint_families import FAMILIES, resolve_hook
from gnd.model import load_model
from gnd.population import load_population
from gnd.semantic_adapter import adapt_snapshot

INDEXED = {
    "equality": semantic_rows.indexed_equality_verdict,
    "exclusion": semantic_rows.indexed_exclusion_verdict,
    "frequency": semantic_rows.indexed_frequency_verdict,
}

# Values whose typed identities differ though Python calls some of them equal.
POOL: list[Any] = [True, 1, 1.0, 0, False, 0.0, "1", "a", "b", 2, "2020-01-01", None]


def _model(joined: bool) -> dict[str, Any]:
    object_types = [
        {"id": "item", "name": "Item", "kind": "value", "primitive": "String"},
        {"id": "tag", "name": "Tag", "kind": "value", "primitive": "String"},
    ]
    fact_types = [
        {"id": f"f{i}", "reading": f"{{Item}} f{i} {{Tag}}",
         "roles": [{"object_type": "item", "role_name": "item"},
                   {"object_type": "tag", "role_name": "tag"}]}
        for i in range(3)
    ]
    if joined:
        # f2 joins f0 on `item`, so a two-role sequence spans two fact types.
        a = [{"fact_type": "f0", "role": "tag"}, {"fact_type": "f2", "role": "tag"}]
    else:
        a = [{"fact_type": "f0", "role": "item"}]
    b = [{"fact_type": "f1", "role": "item"}] if not joined else [
        {"fact_type": "f1", "role": "tag"}, {"fact_type": "f2", "role": "tag"}]
    constraints = []
    for family, modality in (("equality", "alethic"), ("exclusion", "deontic"),
                             ("equality", "deontic"), ("exclusion", "alethic")):
        constraints.append({"type": family, "role_seq_a": a, "role_seq_b": b, "source": "explicit",
                            "status": "confirmed", "modality": modality,
                            "provenance": {"user_quote": "fixture"}})
    bounds = ({"min": 2}, {"max": 1}, {"min": 1, "max": 2}, {"min": 2, "max": 3})
    for bound in bounds:
        fact_types[0].setdefault("constraints", []).append(
            {"type": "frequency", "scope": "internal", "roles": ["item"], "bound": bound,
             "source": "explicit", "status": "confirmed", "modality": "deontic",
             "provenance": {"user_quote": "fixture"}})
        constraints.append(
            {"type": "frequency", "scope": "external", "bound": bound, "source": "explicit",
             "status": "confirmed", "modality": "alethic", "provenance": {"user_quote": "fixture"},
             "role_refs": [{"fact_type": "f0", "role": "tag"}, {"fact_type": "f1", "role": "tag"}]})
    return {"version": 1, "object_types": object_types, "fact_types": fact_types,
            "constraints": constraints}


def _population(rng: random.Random) -> dict[str, Any]:
    facts = {}
    for i in range(3):
        rows = rng.randint(0, 6)
        facts[f"f{i}"] = [
            {"item": rng.choice(["x", "y", "z", "1", "1.0", "true"]), "tag": rng.choice(["p", "q", "1"])}
            for _ in range(rows)
        ]
    return {"population": {"model": "m.orm.json", "source": "fixture", "covers": ["f0", "f1", "f2"]},
            "instances": {}, "facts": facts}


def _snapshot(tmp_path: Path, model: dict[str, Any], population: dict[str, Any]):
    (tmp_path / "m.orm.json").write_text(json.dumps(model))
    (tmp_path / "p.population.json").write_text(json.dumps(population))
    loaded = load_model(tmp_path / "m.orm.json")
    return loaded, adapt_snapshot(loaded, load_population(tmp_path / "p.population.json", model=loaded))


@pytest.mark.parametrize("joined", [False, True], ids=["single", "joined"])
@pytest.mark.parametrize("seed", range(40))
def test_indexed_set_families_equal_the_specification(tmp_path: Path, joined: bool, seed: int) -> None:
    rng = random.Random(seed * 2 + joined)
    _, snapshot = _snapshot(tmp_path, _model(joined), _population(rng))
    checked = [c for c in snapshot.constraints if c.family in INDEXED]
    assert len(checked) == 12
    for constraint in checked:
        assert INDEXED[constraint.family](constraint, snapshot) == semantic_spec.verdict_of(
            constraint, snapshot
        )


@pytest.mark.parametrize("family", ["equality", "exclusion", "frequency"])
@pytest.mark.parametrize(
    "changes", [{"variant": "unknown"}, {"sequences": ()}, {"refused": "opaque-value"}],
)
def test_invalid_shapes_refuse_like_the_specification(tmp_path: Path, family: str, changes) -> None:
    _, snapshot = _snapshot(tmp_path, _model(False), _population(random.Random(7)))
    constraint = next(c for c in snapshot.constraints if c.family == family)
    constraint = replace(constraint, **changes)
    assert INDEXED[family](constraint, snapshot) == semantic_spec.verdict_of(constraint, snapshot)


@pytest.mark.parametrize("family", ["equality", "exclusion"])
def test_typed_identities_are_distinct_rows(tmp_path: Path, family: str) -> None:
    # A single-role pair over a value type whose cells mix 1, True and "1".
    model = _model(False)
    model["object_types"][0]["primitive"] = "String"
    population = {"population": {"model": "m.orm.json", "source": "fixture",
                                 "covers": ["f0", "f1", "f2"]},
                  "instances": {},
                  "facts": {"f0": [{"item": "1", "tag": "p"}, {"item": "a", "tag": "p"}],
                            "f1": [{"item": "1", "tag": "q"}, {"item": "b", "tag": "q"}],
                            "f2": []}}
    _, snapshot = _snapshot(tmp_path, model, population)
    for constraint in (c for c in snapshot.constraints if c.family == family):
        assert INDEXED[family](constraint, snapshot) == semantic_spec.verdict_of(constraint, snapshot)


def test_public_check_never_reaches_the_quadratic_providers(tmp_path: Path, monkeypatch) -> None:
    model = _model(False)
    population = _population(random.Random(3))
    (tmp_path / "m.orm.json").write_text(json.dumps(model))
    (tmp_path / "p.population.json").write_text(json.dumps(population))
    expected = api.check(tmp_path / "m.orm.json", tmp_path / "p.population.json")

    def reject(*args):
        raise AssertionError("quadratic pure set-family provider reached")

    monkeypatch.setattr(semantic_spec, "_family_result_equality", reject)
    monkeypatch.setattr(semantic_spec, "_family_result_exclusion", reject)
    monkeypatch.setattr(semantic_spec, "_family_result_frequency", reject)
    assert api.check(tmp_path / "m.orm.json", tmp_path / "p.population.json") == expected


def test_production_hooks_are_registered_for_the_four_counting_families() -> None:
    for family in ("subset", "equality", "exclusion", "frequency"):
        assert FAMILIES[family].production == f"indexed_{family}_verdict"
        assert callable(resolve_hook(FAMILIES[family].production, vars(semantic_rows)))
