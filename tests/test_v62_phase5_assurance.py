from __future__ import annotations

from support.v62_phase5_corpus import document, population_path

from gnd import api
from gnd.assurance import phase3_scope_ids
from gnd.checker import EXACT_DERIVATION_REASON_CODES
from gnd.model import Model
from gnd.population import load_population
from gnd.semantic_registry import REGISTRY, applicable_scope_ids, is_registered

PHASE5_REASONS = frozenset({'term:div-zero', 'term:sqrt-negative', 'term:haversine-coordinate-range', 'term:float-overflow'})

def _phase3_fixture() -> tuple[str, str]:
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    cases_doc = json.loads((root / 'tests/fixtures/v62-phase3/cases.json').read_text())
    return (str(root / 'tests/fixtures/v62-phase3' / cases_doc['model']), str(root / 'tests/fixtures/v62-phase3' / cases_doc['population']))

def _load_phase3_model_and_population() -> tuple[Model, object]:
    from ruamel.yaml import YAML
    model_path, population_path_str = _phase3_fixture()
    yaml = YAML(typ='safe')
    from pathlib import Path
    model = Model.model_validate(yaml.load(Path(model_path).read_text()))
    population = load_population(Path(population_path_str), model=model)
    return (model, population)

def test_a01_a_float_free_model_marks_no_float_only_scope_applicable() -> None:
    model, population = _load_phase3_model_and_population()
    applicable = applicable_scope_ids(model, population)
    float_only_applicable = [scope_id for scope_id in applicable if any(name in scope_id for name in ('div-zero', 'sqrt-negative', 'haversine', 'float-overflow'))]
    assert float_only_applicable == []

def test_a01_the_public_check_api_assurance_output_carries_no_float_only_id() -> None:
    model_path, population_path_str = _phase3_fixture()
    result = api.check(model_path, population_path_str)
    assurance = result.get('assurance') or {}
    uncovered = assurance.get('uncovered_applicable_scope_ids', [])
    float_only_uncovered = [scope_id for scope_id in uncovered if any(name in scope_id for name in ('div-zero', 'sqrt-negative', 'haversine', 'float-overflow'))]
    assert float_only_uncovered == []

def test_a01_positive_control_the_float_fixture_does_mark_them_applicable() -> None:
    model = Model.model_validate(document())
    population = load_population(population_path('clean'), model=model)
    applicable = applicable_scope_ids(model, population)
    float_only_applicable = [scope_id for scope_id in applicable if any(name in scope_id for name in ('div-zero', 'sqrt-negative', 'haversine', 'float-overflow'))]
    assert len(float_only_applicable) > 0


def test_a01_no_phase5_reason_code_reaches_the_frozen_denominator() -> None:
    assert PHASE5_REASONS <= set(EXACT_DERIVATION_REASON_CODES)
    denominator = set(phase3_scope_ids())
    tainted = {row.scope_id for row in REGISTRY if row.reason_code in PHASE5_REASONS and row.scope_id in denominator}
    assert tainted == set()

def test_a01_every_phase5_reason_code_is_registered_and_excluded_consistently() -> None:
    for reason in PHASE5_REASONS:
        matching = [row for row in REGISTRY if row.reason_code == reason]
        assert matching, f'no registry row carries reason {reason!r}'
        for row in matching:
            assert is_registered(row.scope_id)
