"""Current checker behavior over reviewed synthetic example fixtures."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from public_example_helpers import materialize_example_fixture

from gnd.model import load_model
from gnd.report import load_report_schema

REPO_ROOT = materialize_example_fixture(Path(__file__).parent)
REPORT_VALIDATOR = Draft202012Validator(load_report_schema())
JsonObject = dict[str, Any]
import pytest

from gnd.checker import _constraint_view, _evaluate_derivations
from gnd.population import load_population

CORPUS = REPO_ROOT / "tests/fixtures/v5-phase4-bookrec"
MODEL_PATH = CORPUS / "bookrec-v2.orm.yaml"
def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding='utf-8'))
    assert isinstance(value, dict), path
    return value

def _run(arguments: Sequence[str], *, timeout: float=60.0, cwd: Path=REPO_ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(part) for part in arguments], cwd=cwd, check=False, capture_output=True, text=True, timeout=timeout)

def _run_gnd_json(*arguments: str) -> tuple[int, dict[str, Any]]:
    completed = _run([sys.executable, '-m', 'gnd', *arguments, '--format', 'json'])
    assert completed.stdout, completed.stderr
    payload = json.loads(completed.stdout)
    assert isinstance(payload, dict)
    return (completed.returncode, payload)

def _relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()

def _case_paths(case: Mapping[str, Any]) -> tuple[Path, Path]:
    model_path = CORPUS / str(case.get('model', 'bookrec-v2.orm.yaml'))
    population_path = CORPUS / str(case['population'])
    return (model_path, population_path)

def _load_case(case: Mapping[str, Any]) -> tuple[Any, Any]:
    model_path, population_path = _case_paths(case)
    model = load_model(model_path)
    population = load_population(population_path, model=model)
    assert population.matches_validation_marker(model)
    return (model, population)

def _constraint_id_by_ref(model: Any) -> dict[str, str]:
    result: dict[str, str] = {}
    for index, constraint in enumerate(model.constraints):
        result[f'constraints[{index}]'] = str(constraint['id'])
    for fact_type in model.fact_types:
        fact_type_id = str(fact_type['id'])
        for index, constraint in enumerate(fact_type.get('constraints') or []):
            result[f'fact_types[{fact_type_id}].constraints[{index}]'] = str(constraint.get('id') or f'{fact_type_id}:{index}')
    return result

def _check_projection(payload: Mapping[str, Any], model: Any) -> dict[str, Any]:
    ids = _constraint_id_by_ref(model)
    failed_constraints = []
    for verdict in payload['verdicts']:
        if verdict['verdict'] != 'fail':
            continue
        reference = str(verdict['constraint_ref'])
        failed_constraints.append({'id': ids[reference], 'ref': reference, 'offending_facts': verdict['offending_facts']})
    derivations = []
    for verdict in payload['derivations']:
        derivations.append({'ref': verdict['derivation_ref'], 'verdict': verdict['verdict'], 'findings': [{'kind': finding['kind'], 'witness': finding['witness']} for finding in verdict['findings']]})
    return {'outcome': payload['outcome'], 'counts': payload['counts'], 'failed_constraints': failed_constraints, 'derivations': derivations}

def _expected_check_projection(case: Mapping[str, Any]) -> dict[str, Any]:
    return {key: copy.deepcopy(case[key]) for key in ('outcome', 'counts', 'failed_constraints', 'derivations')}

CHECK_ANSWER = _read_json(CORPUS / "answers/checks.expected.json")
CHECK_CASES = CHECK_ANSWER["cases"]
BOOKREC_CASES = [case for case in CHECK_CASES if "model" not in case]
REGRESSION_CASE = next(case for case in CHECK_CASES if case["id"] == "immutable-mapping")
def test_check_answers_are_closed_bijective_and_separate_from_questions() -> None:
    assert set(CHECK_ANSWER) == {'schema_version', 'cases'}
    assert CHECK_ANSWER['schema_version'] == 1
    assert len(CHECK_CASES) == 4
    ids = [str(case['id']) for case in CHECK_CASES]
    populations = [str(case['population']) for case in CHECK_CASES]
    assert len(ids) == len(set(ids)) == 4
    assert len(populations) == len(set(populations)) == 4
    assert set(ids) == {'derivation-incomplete', 'completeness-missing', 'complete', 'immutable-mapping'}
    common = {'id', 'population', 'expected_exit', 'outcome', 'counts', 'failed_constraints', 'derivations'}
    for case in CHECK_CASES:
        expected_keys = common | ({'model'} if case['id'] == 'immutable-mapping' else set())
        assert set(case) == expected_keys
        assert case['expected_exit'] in {0, 1}
        model_path, population_path = _case_paths(case)
        assert model_path.is_file() and population_path.is_file()
    question = (CORPUS / 'README.md').read_text(encoding='utf-8')
    assert 'b-safe-fantasy' not in question
    assert 'derived-extension-incomplete' not in question
    assert 'constraints[3]' not in question

def test_candidate_models_and_all_population_inputs_are_shape_valid() -> None:
    for case in CHECK_CASES:
        model, population = _load_case(case)
        assert model.version == 2
        assert population.model_id == model.model_id
    model = load_model(MODEL_PATH)
    structured = {str(fact_type['id']): fact_type['derivation_rule'] for fact_type in model.fact_types if isinstance(fact_type.get('derivation_rule'), dict)}
    assert set(structured) == {'book_is_blocked_for', 'book_is_eligible'}
    eligibility = structured['book_is_eligible']
    assert [atom['fact_type'] for atom in eligibility['body']] == ['user_prefers_genre', 'book_has_genre']
    assert [atom['fact_type'] for atom in eligibility['negate']] == ['book_is_blocked_for', 'user_rated_book']
    completeness = next(constraint for constraint in model.constraints if constraint['id'] == 'recommendation_covers_every_eligible_book')
    assert completeness['antecedent'][0]['fact_type'] == 'book_is_eligible'
    assert completeness['consequent']['atom']['fact_type'] == 'recommendation'

def test_the_three_bookrec_populations_differ_only_at_the_declared_story_cell() -> None:
    complete = _read_json(CORPUS / 'populations' / 'complete.population.json')
    derivation = _read_json(CORPUS / 'populations' / 'derivation-incomplete.population.json')
    completeness = _read_json(CORPUS / 'populations' / 'completeness-missing.population.json')

    def facts_without(document: dict[str, Any], fact_type: str) -> dict[str, Any]:
        value = copy.deepcopy(document['facts'])
        del value[fact_type]
        return value
    assert facts_without(derivation, 'book_is_eligible') == facts_without(complete, 'book_is_eligible')
    assert derivation['facts']['book_is_eligible'] == [{'book': 'b-safe-sf', 'user': 'u-ada'}]
    assert complete['facts']['book_is_eligible'] == [{'book': 'b-safe-fantasy', 'user': 'u-minor'}, {'book': 'b-safe-sf', 'user': 'u-ada'}]
    assert facts_without(completeness, 'recommendation') == facts_without(complete, 'recommendation')
    assert completeness['facts']['recommendation'] == [{'book': 'b-safe-sf', 'user': 'u-ada'}]
    assert complete['facts']['recommendation'] == [{'book': 'b-safe-fantasy', 'user': 'u-minor'}, {'book': 'b-safe-sf', 'user': 'u-ada'}]

@pytest.mark.parametrize('case', BOOKREC_CASES, ids=[str(case['id']) for case in BOOKREC_CASES])
def test_bookrec_target_projection_is_green(case: dict[str, Any]) -> None:
    """The three approved projections stay fixed after the Mapping repair."""
    model, _population = _load_case(case)
    model_path, population_path = _case_paths(case)
    code, payload = _run_gnd_json('check', _relative(model_path), _relative(population_path))
    REPORT_VALIDATOR.validate(payload)
    assert code == case['expected_exit']
    assert _check_projection(payload, model) == _expected_check_projection(case)

def test_isolated_immutable_mapping_regression_is_green() -> None:
    """The one-token Mapping regression stays independently exercised."""
    case = REGRESSION_CASE
    model, population = _load_case(case)
    extensions, derivations = _evaluate_derivations(model, population)
    assert [verdict.verdict for verdict in derivations] == ['pass']
    constraint_view = _constraint_view(model, population, extensions)
    immutable_row = constraint_view.facts['asserted_hit'][0]
    assert isinstance(immutable_row, Mapping)
    assert not isinstance(immutable_row, dict)
    model_path, population_path = _case_paths(case)
    code, payload = _run_gnd_json('check', _relative(model_path), _relative(population_path))
    REPORT_VALIDATOR.validate(payload)
    assert code == case['expected_exit']
    assert _check_projection(payload, model) == _expected_check_projection(case)
