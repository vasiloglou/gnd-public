"""Current derivation comparison, event ledger, isolation and CLI controls."""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
from typing import Any

import pytest

from gnd import checker, extensions
from gnd import cli as cli_module
from gnd.checker import (
    DerivationFinding,
    _base_relations,
    _constraint_view,
    _evaluate_derivations,
    _python_extension_calculator,
    _TypedRelation,
    band,
)
from gnd.model import ModelValidationError, load_model
from gnd.population import PopulationValidationError, load_population
from gnd.report import MODEL_BOUND_DERIVATION_PAYLOAD_SCHEMA_VERSION, legacy_report_projection
from gnd.transition import model_digest

REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS = REPO_ROOT / "tests/fixtures/public-derivation-evaluator-controls"
CASES = json.loads((CORPUS / "cases.json").read_text())
A8_MIGRATED_BRANCHES = frozenset({"obligation:unlisted-derived-nonempty-computed", "obligation:unlisted-semiderived-nonempty-computed", "constraint:unlisted-derived-claim-inert", "constraint:mandatory-uncovered-vacuous-plus-band4"})

def _paths(case: dict[str, Any]) -> tuple[Path, Path]:
    root = CORPUS / str(case["path"])
    return root / "model.orm.yaml", root / "population.yaml"


def _structured_rules(model: Any) -> list[Any]:
    return [
        fact_type.get("derivation_rule")
        for fact_type in model.fact_types
        if isinstance(fact_type.get("derivation_rule"), dict)
    ]


def _assert_preconditions(case: dict[str, Any]) -> tuple[Any | None, Any | None]:
    """Establish this case's legal input/refusal shape before any RED sentinel."""
    model_path, population_path = _paths(case)
    profile = str(case["profile"])

    if profile == "invalid-model":
        with pytest.raises(ModelValidationError):
            load_model(model_path)
        return None, None

    model = load_model(model_path)
    if profile in {"nonstructured", "string-only"}:
        assert not _structured_rules(model), case["id"]
    else:
        assert _structured_rules(model), case["id"]

    if profile == "population-refusal" or str(case["branch"]) in A8_MIGRATED_BRANCHES:
        with pytest.raises(PopulationValidationError) as excinfo:
            load_population(population_path, model=model)
        if str(case["branch"]) in A8_MIGRATED_BRANCHES:
            assert [issue.rule_id for issue in excinfo.value.issues] == [
                "population:uncovered-structured-derived-facts"
            ]
        return model, None

    population = load_population(population_path, model=model)
    assert population.matches_validation_marker(model)

    if profile == "string-only":
        assert all(
            not isinstance(fact_type.get("derivation_rule"), dict) for fact_type in model.fact_types
        )
    if profile.startswith("mixed-"):
        rules = [fact_type.get("derivation_rule") for fact_type in model.fact_types]
        assert any(isinstance(rule, dict) for rule in rules)
        assert any(isinstance(rule, str) for rule in rules)
        assert ("legacy_result" in population.covers) == (profile == "mixed-listed")
    if profile.startswith("unlisted-"):
        assert "result" not in population.covers
        if profile.endswith("-empty"):
            assert population.facts["seed"] == []
        else:
            assert population.facts["seed"]
    if profile == "dollar-literal":
        assert any(
            atom.get("bind", {}).get("tag") == "$"
            for fact_type in model.fact_types
            for atom in (
                fact_type.get("derivation_rule", {}).get("body", [])
                if isinstance(fact_type.get("derivation_rule"), dict)
                else []
            )
        )
    if profile == "chain":
        assert [fact_type["id"] for fact_type in model.fact_types][-3:] == [
            "low",
            "middle",
            "top",
        ]
    if profile == "disconnected":
        rule = next(
            fact_type["derivation_rule"]
            for fact_type in model.fact_types
            if fact_type["id"] == "result"
        )
        assert len(rule["body"]) == 2
    if profile == "unresolved":
        from gnd.popvalidate import resolve_primitive

        assert resolve_primitive("mass", model) is None
    if profile == "primitives":
        primitives = {
            object_type.get("primitive")
            for object_type in model.object_types
            if object_type.get("primitive") is not None
        }
        assert primitives == {
            "String",
            "Integer",
            "Float",
            "Number",
            "Date",
            "DateTime",
            "Boolean",
            "Binary",
        }
    return model, population


def _loaded(case: dict[str, Any]) -> tuple[Any, Any]:
    model, population = _assert_preconditions(case)
    assert model is not None and population is not None
    return model, population


def test_comparison_mutation_receipts(monkeypatch: pytest.MonkeyPatch) -> None:
    """Silenced comparison reds missing/surplus; always-fire reds exact claims."""
    cases = {
        branch: next(case for case in CASES if case["branch"] == branch)
        for branch in (
            "obligation:derived-exact",
            "obligation:derived-missing",
            "obligation:derived-surplus",
        )
    }
    original = extensions._derivation_obligation

    def silenced(fact_type: dict[str, Any], population: Any, computed: Any):
        row = original(fact_type, population, computed)
        # Keep the mutant structurally consistent so this still challenges
        # comparison semantics rather than only the branch metadata guard.
        return row.model_copy(
            update={
                "scope_id": f"derivation:extension:{row.derivation}:clean",
                "verdict": "pass",
                "findings": [],
                "reason_code": None,
            }
        )

    with monkeypatch.context() as mutation:
        mutation.setattr(extensions, "_derivation_obligation", silenced)
        for branch in ("obligation:derived-missing", "obligation:derived-surplus"):
            model, population = _loaded(cases[branch])
            assert band(checker.check(model, population)) == 0

    def always_fires(fact_type: dict[str, Any], population: Any, computed: Any):
        row = original(fact_type, population, computed)
        return row.model_copy(
            update={
                "scope_id": f"derivation:extension:{row.derivation}:violated:alethic",
                "verdict": "fail",
                "findings": [
                    DerivationFinding(
                        kind="derived-extension-incomplete",
                        message="mutated",
                        witness={},
                    )
                ],
                "reason_code": None,
            }
        )

    with monkeypatch.context() as mutation:
        mutation.setattr(extensions, "_derivation_obligation", always_fires)
        model, population = _loaded(cases["obligation:derived-exact"])
        assert band(checker.check(model, population)) == 1


def test_counted_costs_are_separate_from_guarded_work() -> None:
    case = next(case for case in CASES if case["branch"] == "cost:disconnected-counted")
    model, population = _loaded(case)
    calculated = _python_extension_calculator(model, _base_relations(model, population))
    before = vars(calculated.counted_operations).copy()
    guarded = next(item for item in CASES if item["branch"] == "constraint:one-final-walk")
    guarded_model, guarded_population = _loaded(guarded)
    checker.check(guarded_model, guarded_population)
    assert vars(calculated.counted_operations) == before


def test_disconnected_component_mutations_red(monkeypatch: pytest.MonkeyPatch) -> None:
    case = next(case for case in CASES if case["branch"] == "eval:disconnected-product")
    model, population = _loaded(case)
    relations = _base_relations(model, population)
    expected = _python_extension_calculator(model, relations).extensions["result"].rows
    assert len(expected) == 4
    original = extensions._component_atoms

    for kept_component in (0, 1):

        def drop_other(rule: dict[str, Any], slot: int = kept_component):
            return [original(rule)[slot]]

        with monkeypatch.context() as mutation:
            mutation.setattr(extensions, "_component_atoms", drop_other)
            with pytest.raises(KeyError):
                _python_extension_calculator(model, relations)

    def refuse_disconnection(rule: dict[str, Any]):
        components = original(rule)
        return [[atom for component in components for atom in component]]

    with monkeypatch.context() as mutation:
        mutation.setattr(extensions, "_component_atoms", refuse_disconnection)
        with pytest.raises(checker.JoinDisconnectedError):
            _python_extension_calculator(model, relations)


def test_evaluator_exception_is_internal(monkeypatch: pytest.MonkeyPatch) -> None:
    case = next(case for case in CASES if case["branch"] == "wire:v4-check-internal")
    model_path, population_path = _paths(case)

    def explode(_model: Any, _population: Any):
        raise RuntimeError("seeded evaluator defect")

    output = io.StringIO()
    monkeypatch.setattr(extensions, "evaluate_derivations", explode)
    with contextlib.redirect_stdout(output):
        exit_code = cli_module._cmd_check(str(model_path), str(population_path), "json")
    payload = json.loads(output.getvalue())
    assert exit_code == payload["exit_code"] == 70
    payload = legacy_report_projection(payload, MODEL_BOUND_DERIVATION_PAYLOAD_SCHEMA_VERSION)
    assert payload["schema_version"] == MODEL_BOUND_DERIVATION_PAYLOAD_SCHEMA_VERSION
    assert payload["derivations"] == []
    assert payload["model_digest"] == model_digest(load_model(model_path))


def test_witness_order() -> None:
    case = next(case for case in CASES if case["branch"] == "witness:missing-canonical")
    model, population = _loaded(case)
    fact_type = next(item for item in model.fact_types if item.get("id") == "result")
    roles = (("item", "String"),)
    computed = _TypedRelation("result", roles, (("beta",), ("alpha",)))
    missing = extensions._derivation_obligation(
        fact_type,
        population.model_copy(update={"facts": population.facts | {"result": []}}),
        computed,
    )
    surplus = extensions._derivation_obligation(
        fact_type,
        population.model_copy(
            update={"facts": population.facts | {"result": [{"item": "beta"}, {"item": "alpha"}]}}
        ),
        _TypedRelation("result", roles, ()),
    )
    assert missing.findings[0].witness == surplus.findings[0].witness == {"item": "alpha"}


def test_semiderived_surplus_cannot_satisfy_guard() -> None:
    case = next(case for case in CASES if case["branch"] == "constraint:one-final-walk")
    model, population = _loaded(case)
    report = checker.check(model, population)
    semi = next(row for row in report.derivations if row.fact_type == "semi_result")
    guarded = report.verdicts[0]
    assert semi.verdict == "pass"
    assert guarded.verdict == "fail"
    assert "bindings=1" in guarded.message
    assert "alpha" in guarded.message and "surplus" not in guarded.message


@pytest.mark.parametrize(
    ("branch", "expected"),
    [
        (
            "cost:chain-counted",
            {
                "atom_role_terms_read": 3,
                "positive_candidate_rows_emitted": 3,
                "join_candidates_indexed": 0,
                "join_left_bindings_probed": 0,
                "join_matches_merged": 0,
                "component_product_rows_emitted": 3,
                "negation_rows_indexed": 0,
                "negation_bindings_probed": 0,
                "head_cells_projected": 3,
            },
        ),
        (
            "cost:disconnected-counted",
            {
                "atom_role_terms_read": 4,
                "positive_candidate_rows_emitted": 4,
                "join_candidates_indexed": 0,
                "join_left_bindings_probed": 0,
                "join_matches_merged": 0,
                "component_product_rows_emitted": 6,
                "negation_rows_indexed": 0,
                "negation_bindings_probed": 4,
                "head_cells_projected": 8,
            },
        ),
    ],
    ids=["chain-small-head", "disconnected-pair"],
)
def test_counted_cost(branch: str, expected: dict[str, int]) -> None:
    case = next(case for case in CASES if case["branch"] == branch)
    model, population = _loaded(case)
    result = _python_extension_calculator(model, _base_relations(model, population))
    assert vars(result.counted_operations) == expected


def test_constraints_run_once_after_all_extensions(monkeypatch: pytest.MonkeyPatch) -> None:
    case = next(case for case in CASES if case["branch"] == "constraint:one-final-walk")
    model, population = _loaded(case)
    calls: list[str] = []
    original_evaluate = extensions.evaluate_derivations
    original_message = checker._correspondence_message

    def traced_evaluate(*args: Any, **kwargs: Any):
        result = original_evaluate(*args, **kwargs)
        calls.extend(f"extension:{fact_type}" for fact_type in result[0])
        calls.extend(f"comparison:{row.fact_type}" for row in result[1])
        return result

    def traced_message(*args: Any, **kwargs: Any):
        calls.append(f"constraint:{args[2].constraint_id}")
        return original_message(*args, **kwargs)

    monkeypatch.setattr(extensions, "evaluate_derivations", traced_evaluate)
    monkeypatch.setattr(checker, "_correspondence_message", traced_message)
    report = checker.check(model, population)
    assert len(report.verdicts) == 1
    assert calls == [
        "extension:result",
        "extension:semi_result",
        "comparison:result",
        "comparison:semi_result",
        "constraint:constraints[0]",
    ]


def test_ruled_views_are_isolated() -> None:
    case = next(case for case in CASES if case["branch"] == "constraint:one-final-walk")
    model, population = _loaded(case)
    base = _base_relations(model, population)
    extensions, _verdicts = _evaluate_derivations(model, population)
    view = _constraint_view(model, population, extensions)
    assert base["result"].rows == base["semi_result"].rows == ()
    assert [dict(row) for row in view.facts["semi_result"]] == [{"item": "alpha"}]
    assert population.facts["semi_result"] == [
        {"item": "alpha"},
        {"item": "surplus"},
    ]
    with pytest.raises(TypeError):
        view.facts["semi_result"] = ()  # type: ignore[index]


