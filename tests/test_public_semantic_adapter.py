"""Canonical adapter controls over complete reviewed generic branch subjects."""
from __future__ import annotations

import dataclasses
import json
import math
import shutil
from pathlib import Path

import pytest
import test_public_branch_runtime as corpus
from test_public_slice_runtime import CORPUS as SLICE_CORPUS

from gnd import semantic_adapter as adapter
from gnd import semantic_ir as ir
from gnd.model import load_model
from gnd.population import Population, load_population, load_population_bytes

ROOT = corpus.REPO_ROOT


@pytest.fixture(autouse=True)
def _generic_adapter_root(tmp_path, monkeypatch):
    root = tmp_path / "adapter-root"
    shutil.copytree(corpus.REPO_ROOT, root)
    fixture = root / "proof/v6/phase1/corpus/fixtures/c01"
    fixture.mkdir(parents=True, exist_ok=True)
    for name in ("model.orm.yaml", "population.yaml"):
        shutil.copyfile(SLICE_CORPUS / "fixtures/c01" / name, fixture / name)
    monkeypatch.setattr(__import__(__name__), "ROOT", root)
ADMITTED = tuple(
    key for key, row in corpus.BUILD_BY_ID.items() if row.get("admission") != "unvalidated"
)


def _immutable(value):
    if dataclasses.is_dataclass(value):
        assert value.__dataclass_params__.frozen
        for field in dataclasses.fields(value):
            _immutable(getattr(value, field.name))
    elif isinstance(value, tuple):
        for item in value:
            _immutable(item)
    else:
        assert value is None or type(value) in (str, int, bool), type(value)


@pytest.mark.parametrize("case_id", ADMITTED)
def test_every_admitted_corpus_pair_has_an_immutable_complete_ir(case_id, tmp_path):
    model, population = corpus._build(case_id, tmp_path)
    snapshot = adapter.adapt_snapshot(model, population)
    assert isinstance(snapshot, ir.SnapshotIR)
    _immutable(snapshot)
    assert tuple(fact.id for fact in snapshot.fact_types) == tuple(
        fact["id"] for fact in model.fact_types
    )
    assert len(snapshot.constraints) == sum(
        len(ft.get("constraints", [])) for ft in model.fact_types
    ) + len(model.constraints)
    assert snapshot.covers == tuple(population.covers)
    by_id = {row.fact_type: row for row in snapshot.relations}
    for ft in model.fact_types:
        original = population.facts.get(ft["id"], [])
        relation = by_id[ft["id"]]
        assert len(relation.rows) == len(original)
        for before, after in zip(original, relation.rows, strict=True):
            assert len(after) == len(ft["roles"])
            for role, scalar in zip(ft["roles"], after, strict=True):
                expected = adapter.canonical_scalar(
                    before[role["role_name"]], adapter.resolve_primitive(role["object_type"], model)
                )
                assert scalar == expected
    for constraint in snapshot.constraints:
        assert constraint.refused in ("", *adapter.ADAPTER_REFUSALS)


def test_adapter_requires_a_current_admission_marker():
    directory = ROOT / "proof/v6/phase1/corpus/fixtures/c01"
    model = load_model(directory / "model.orm.yaml")
    population = load_population(directory / "population.yaml", model=model)
    unstamped = Population.model_validate(population.model_dump())
    with pytest.raises(adapter.UnvalidatedPopulationError):
        adapter.adapt_snapshot(model, unstamped)
    population.instances["reviewer"].append("changed")
    with pytest.raises(adapter.UnvalidatedPopulationError):
        adapter.adapt_snapshot(model, population)


def observe_adapter_refusals(tmp_path):
    from gnd.semantic_registry import capture_branches

    model, _ = corpus._build("P2-161", tmp_path)
    host = model.fact_types[0]
    cardinality = {
        "type": "cardinality",
        "scope": "object",
        "object_type": "opaque",
        "modality": "alethic",
    }
    cases = (
        ("malformed-constraint", [], None),
        ("unregistered-family", {"type": "not-a-family"}, None),
        (
            "unresolvable-role",
            {"type": "mandatory", "role": "missing", "modality": "alethic"},
            host,
        ),
        ("boolean-in-numeric-role", {**cardinality, "bound": {"min": True}}, None),
        ("non-finite-number", {**cardinality, "bound": {"min": math.inf}}, None),
        (
            "untyped-string-ordering",
            {
                "type": "value",
                "object_type": "opaque",
                "range": {"min": "a"},
                "modality": "alethic",
            },
            None,
        ),
    )
    assert {reason for reason, _, _ in cases} == set(adapter.ADAPTER_REFUSALS) - {"opaque-value"}
    with capture_branches() as reached:
        for reason, source, fact_type in cases:
            with capture_branches() as one:
                result = adapter.adapt_constraint(source, fact_type, "fixture", model)
            assert result.refused == reason
            assert one == {"applicability:adapter:n-a:" + reason}
    assert reached == {
        "applicability:adapter:n-a:" + reason
        for reason in adapter.ADAPTER_REFUSALS if reason != "opaque-value"
    }
    phase3 = Path(__file__).parent / "fixtures/v70-phase3"
    opaque_model = load_model(phase3 / "model.orm.yaml")
    opaque_document = json.loads((phase3 / "population.pop.json").read_text())
    opaque_document["facts"]["record_has_amount"][0]["amount"] = {"$opaque": "unread"}
    opaque_population = load_population_bytes(
        json.dumps(opaque_document).encode(), source="opaque.json", model=opaque_model,
    )
    with capture_branches() as opaque_reached:
        snapshot = adapter.adapt_snapshot(opaque_model, opaque_population)
    assert "applicability:adapter:n-a:opaque-value" in opaque_reached
    assert any(row.refused == "opaque-value" for row in snapshot.constraints)


def test_all_adapter_refusals_have_distinguishing_inputs(tmp_path):
    observe_adapter_refusals(tmp_path)


@pytest.mark.parametrize(
    "source",
    [
        None,
        False,
        10,
        "mandatory",
        {},
        {"type": []},
        {"type": "value", "modality": []},
        {"type": "guarded", "modality": "alethic", "antecedent": [None]},
        {"type": "subset", "modality": "alethic", "subset_role_seq": [1]},
    ],
)
def test_constraint_adapter_is_total_over_bad_json_shapes(source):
    model = load_model(ROOT / "proof/v6/phase1/corpus/fixtures/c01/model.orm.yaml")
    result = adapter.adapt_constraint(source, None, "bad-json", model)
    assert result.refused == "malformed-constraint"
    _immutable(result)


def test_guard_consequents_and_variants_remain_distinct(tmp_path):
    root = ROOT / "tests/fixtures/guarded"
    model = load_model(root / "models/alethic.orm.yaml")
    population = load_population(root / "cases/a-a1.yaml", model=model)
    result = adapter.adapt_snapshot(model, population)
    assert [row.consequent_kind for row in result.constraints] == ["comparison", "atom", "absence"]
    assert result.constraints[0].operator == "<="
    assert result.constraints[1].consequent[0].fact_type == "expense_has_status"
    assert dict(result.constraints[1].consequent[0].bindings)["status"].literal.token == "review"
    assert dict(result.constraints[2].consequent[0].bindings)["status"].literal.token == "blocked"
    model, _ = corpus._build("P2-004", tmp_path)
    host = model.fact_types[0]
    for variant in ("acyclic", "irreflexive", "symmetric"):
        constraint = adapter.adapt_constraint(
            {
                "type": "ring",
                "modality": "alethic",
                "variant": variant,
                "roles": [role["role_name"] for role in host["roles"]],
            },
            host,
            "ring",
            model,
        )
        assert not constraint.refused
        assert constraint.variant == variant


@pytest.mark.parametrize("case_id", tuple(key for key in corpus.BUILD_BY_ID if key not in ADMITTED))
def test_in_process_corpus_models_with_population_markers_are_total(case_id, tmp_path):
    model, population = corpus._build(case_id, tmp_path)
    assert population.matches_validation_marker(model)
    result = adapter.adapt_snapshot(model, population)
    _immutable(result)
    assert all(row.refused in ("", *ir.ADAPTER_REFUSALS) for row in result.constraints)

