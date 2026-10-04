"""Applicability of structured, opaque and transition obligations on generic inputs."""
from __future__ import annotations

import atexit
import copy
import shutil
import tempfile
from pathlib import Path

from test_public_slice_runtime import CORPUS as SLICE_CORPUS
from test_public_transition_walks import MODEL as TRANSITION_MODEL
from test_public_transition_walks import WALKS

import gnd
from gnd import checker
from gnd import semantic_registry as registry
from gnd.model import load_model
from gnd.population import load_population

_PUBLIC_FIXTURES = ('tests/fixtures/derivation-evaluation/cases/obligation-semiderived-surplus/model.orm.yaml', 'tests/fixtures/derivation-evaluation/cases/obligation-semiderived-surplus/population.yaml', 'tests/fixtures/derivation-evaluation/cases/obligation-opaque-mixed-listed/model.orm.yaml', 'tests/fixtures/derivation-evaluation/cases/obligation-opaque-mixed-listed/population.yaml', 'tests/fixtures/v62-phase4/models/aggregates.orm.yaml', 'tests/fixtures/v62-phase4/populations/aggregate-input.pop.yaml', 'tests/fixtures/v62-phase2/models/dynamic.orm.yaml', 'tests/fixtures/v62-phase2/populations/pre-open.pop.yaml', 'tests/fixtures/v62-phase3/models/exact-terms.orm.yaml', 'tests/fixtures/v62-phase3/populations/term-input.pop.yaml', 'tests/fixtures/v62-phase5/models/floats.orm.yaml', 'tests/fixtures/v62-phase5/populations/float-clean.pop.yaml')


def _generic_obligation_root():
    temporary = tempfile.TemporaryDirectory(prefix="gnd-public-applicability-")
    root = Path(temporary.name)
    installed = Path(gnd.__file__).resolve().parents[2]
    for name in _PUBLIC_FIXTURES:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(installed / name, path)
    for case in ("c01", "c02"):
        for name in ("model.orm.yaml", "population.yaml"):
            path = root / "proof/v6/phase1/corpus/fixtures" / case / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SLICE_CORPUS / "fixtures" / case / name, path)
    model = root / "tests/fixtures/transition/expense/v2_expense.orm.yaml"
    model.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(TRANSITION_MODEL, model)
    pre = root / "tests/fixtures/transition/expense/walks/dynamic-untouched-silent/pre.pop.yaml"
    pre.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(WALKS / "dynamic-untouched-silent/pre.pop.yaml", pre)
    return temporary, root

_TEMPORARY, ROOT = _generic_obligation_root()
atexit.register(_TEMPORARY.cleanup)
def _mandatory_inputs():
    root = ROOT / "proof/v6/phase1/corpus/fixtures"
    model = load_model(root / "c01/model.orm.yaml")
    return model, [
        load_population(root / f"{case}/population.yaml", model=model) for case in ("c01", "c02")
    ]


def test_structured_effective_view_and_opaque_obligations_are_in_scope(monkeypatch):
    root = ROOT / "tests/fixtures/derivation-evaluation/cases"
    for case in ("obligation-semiderived-surplus", "obligation-opaque-mixed-listed"):
        model = load_model(root / case / "model.orm.yaml")
        population = load_population(root / case / "population.yaml", model=model)
        # Claim comparison must not run just to discover its own obligations.
        with monkeypatch.context() as context:

            def forbidden(*args, **kwargs):
                raise AssertionError("claim verdicts do not determine applicability")

            context.setattr(checker, "_derivation_obligation", forbidden)
            with registry.capture_branches() as classified:
                applicable = registry.applicable_scope_ids(model, population)
        assert not classified
        with registry.capture_branches() as reached:
            checker.check(model, population)
        assert reached <= set(applicable), sorted(reached - set(applicable))
        assert any(scope.startswith("derivation:") for scope in applicable)


def test_declared_operations_include_transition_obligations():
    root = ROOT / "tests/fixtures/transition/expense"
    model = load_model(root / "v2_expense.orm.yaml")
    population_path = next((root / "walks").glob("*/pre.pop.yaml"))
    population = load_population(population_path, model=model)
    applicable = set(registry.applicable_scope_ids(model, population))
    aggregate_root = ROOT / "tests/fixtures/v62-phase4"
    aggregate_model = load_model(aggregate_root / "models/aggregates.orm.yaml")
    aggregate_population = load_population(
        aggregate_root / "populations/aggregate-input.pop.yaml", model=aggregate_model
    )
    applicable.update(registry.applicable_scope_ids(aggregate_model, aggregate_population))
    dynamic_root = ROOT / "tests/fixtures/v62-phase2"
    dynamic_model = load_model(dynamic_root / "models/dynamic.orm.yaml")
    dynamic_population = load_population(
        dynamic_root / "populations/pre-open.pop.yaml", model=dynamic_model
    )
    applicable.update(registry.applicable_scope_ids(dynamic_model, dynamic_population))
    exact_root = ROOT / "tests/fixtures/v62-phase3"
    exact_model = load_model(exact_root / "models/exact-terms.orm.yaml")
    exact_operations = copy.deepcopy(exact_model.operations)
    exact_operations[0]["dynamic_rules"] = [
        {
            "id": "residue_never_decreases",
            "subject": {
                "fact_type": "residue",
                "value_role": "residue",
                "bind": {"ticket": "$ticket"},
            },
            "op": ">=",
            "modality": "alethic",
            "source": "user-supplied",
            "status": "confirmed",
            "provenance": {"user_quote": "Computed residue never decreases."},
        }
    ]
    exact_dynamic_model = exact_model.model_copy(update={"operations": exact_operations})
    exact_population = load_population(
        exact_root / "populations/term-input.pop.yaml", model=exact_dynamic_model
    )
    applicable.update(registry.applicable_scope_ids(exact_dynamic_model, exact_population))
    float_root = ROOT / "tests/fixtures/v62-phase5"
    float_model = load_model(float_root / "models/floats.orm.yaml")
    float_operations = copy.deepcopy(float_model.operations)
    float_operations[0]["dynamic_rules"] = [
        {
            "id": "sample_rate_never_decreases",
            "subject": {
                "fact_type": "sample_rate_kbps",
                "value_role": "rate",
                "bind": {"ue": "$ue"},
            },
            "op": ">=",
            "modality": "alethic",
            "source": "user-supplied",
            "status": "confirmed",
            "provenance": {"user_quote": "Computed sample rate never decreases."},
        }
    ]
    float_dynamic_model = float_model.model_copy(update={"operations": float_operations})
    float_population = load_population(
        float_root / "populations/float-clean.pop.yaml", model=float_dynamic_model
    )
    applicable.update(registry.applicable_scope_ids(float_dynamic_model, float_population))
    transitions = {row.scope_id for row in registry.REGISTRY if row.surface == "transition"}
    assert transitions and transitions <= applicable
    plain_model, (plain, _) = _mandatory_inputs()
    assert transitions.isdisjoint(registry.applicable_scope_ids(plain_model, plain))

