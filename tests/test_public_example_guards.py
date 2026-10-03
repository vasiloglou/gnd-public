"""Current checker behavior over reviewed synthetic example fixtures."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from public_example_helpers import guarded_binding_counts, materialize_example_fixture, ref_to_id
from ruamel.yaml import YAML

from gnd.model import load_model
from gnd.report import load_report_schema

REPO_ROOT = materialize_example_fixture(Path(__file__).parent)
REPORT_VALIDATOR = Draft202012Validator(load_report_schema())
JsonObject = dict[str, Any]
import re
from collections import Counter

BOOKREC = REPO_ROOT / "examples/bookrec"
MODEL_PATH = BOOKREC / "model.orm.yaml"
EXPENSE = REPO_ROOT / "examples/expense-tracker"
RATED_GUARD = "recommendation_excludes_rated_books"
MINOR_ADULT_GUARD = "recommendation_excludes_adult_books_for_minors"
GENRE_GUARD = "recommendation_matches_preferred_genre"
ELIGIBILITY_COMPLETENESS_GUARD = "recommendation_covers_every_eligible_book"
BOOKREC_GUARDS = {RATED_GUARD, MINOR_ADULT_GUARD, GENRE_GUARD}
BOOKREC_DERIVED_FACT_TYPES = {"book_is_blocked_for", "book_is_eligible"}
def _read_json(path: Path) -> JsonObject:
    """Read one committed JSON object."""
    value = json.loads(path.read_text(encoding='utf-8'))
    assert isinstance(value, dict), path
    return value

def _read_model(path: Path=MODEL_PATH) -> JsonObject:
    """Read a model as the YAML mapping used by the independent helper."""
    value = YAML(typ='safe').load(path.read_text(encoding='utf-8'))
    assert isinstance(value, dict), path
    return value

def _run_gnd_json(*args: str) -> tuple[int, JsonObject]:
    """Run GND through the required subprocess interface and parse stdout."""
    completed = subprocess.run([sys.executable, '-m', 'gnd', *args, '--format', 'json'], cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=15)
    assert completed.stdout, completed.stderr
    payload = json.loads(completed.stdout)
    assert isinstance(payload, dict)
    return (completed.returncode, payload)

def _run_check(model_path: Path, population_path: Path) -> tuple[int, JsonObject]:
    """Run ``gnd check`` and require a schema-valid report."""
    code, report = _run_gnd_json('check', str(model_path), str(population_path))
    REPORT_VALIDATOR.validate(report)
    return (code, report)

def _guard_verdicts(model: Mapping[str, Any], report: Mapping[str, Any], expected_ids: set[str]=BOOKREC_GUARDS) -> JsonObject:
    """Resolve positional verdict references to stable guarded IDs."""
    ids = ref_to_id(model)
    resolved = {ids[str(verdict['constraint_ref'])]: verdict for verdict in report['verdicts'] if str(verdict['constraint_ref']) in ids and ids[str(verdict['constraint_ref'])] in expected_ids}
    assert set(resolved) == expected_ids
    return resolved

def _all_constraints(model: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    """Return model-level and fact-type constraint fragments."""
    constraints = list(model.get('constraints') or [])
    for fact_type in model.get('fact_types') or []:
        constraints.extend(fact_type.get('constraints') or [])
    return constraints

def _all_nonvacuous_pass(model: Mapping[str, Any], population: Mapping[str, Any], report: Mapping[str, Any], constraint_ids: set[str]) -> bool:
    """Require both structured pass verdicts and independently nonempty joins."""
    verdicts = _guard_verdicts(model, report, constraint_ids)
    counts = guarded_binding_counts(model, population)
    return all(verdicts[constraint_id]['verdict'] == 'pass' and counts[constraint_id] > 0 for constraint_id in constraint_ids)
def test_bookrec_model_provenance_and_modality_story_is_auditable() -> None:
    """Exclude a valid-looking model that loses source, confirmation, or CAS history."""
    load_model(MODEL_PATH)
    model = _read_model()
    constraints = _all_constraints(model)
    source_counts = Counter(str(constraint['source']) for constraint in constraints)
    story_counts = Counter((str(constraint['source']), str(constraint['status']), str(constraint['modality'])) for constraint in constraints)
    genre = next(constraint for constraint in model['constraints'] if constraint['id'] == GENRE_GUARD)
    assert model['source'] == {'kind': 'text-conversation', 'confidence': 'standard', 'mode': 'mvp-fast'}
    assert source_counts == {'explicit': 4, 'common-sense': 1, 'user-supplied': 2}
    assert story_counts == {('explicit', 'confirmed', 'alethic'): 4, ('common-sense', 'confirmed', 'alethic'): 1, ('user-supplied', 'confirmed', 'alethic'): 2}
    assert any(constraint['source'] == 'explicit' and constraint['status'] == 'confirmed' for constraint in constraints)
    assert any(constraint['source'] in {'common-sense', 'llm-inferred'} and constraint['status'] == 'confirmed' for constraint in constraints)
    assert genre['rationale'] == 'Owner promoted the observed preferred-genre guideline after the v1-to-v2 tuning evidence.'
    assert genre['provenance'] == {'csdp_step': 7, 'added_at_step': '7d', 'user_note': 'Confirmed as a hard rule during Phase 4 Act 4.'}
    assert not {'document', 'document_sha256', 'anchor', 'anchors'} & set(model['source'])

def test_spec_and_model_share_one_exact_predicate_polarity_graph() -> None:
    """Exclude swapping a positive premise, a negation, or the completeness arrow."""
    spec = (BOOKREC / 'SPEC.md').read_text(encoding='utf-8')
    rule_matches = re.findall('(?ms)^([5-7])\\. \\*\\*(.*?)\\*\\*', spec)
    assert [int(number) for number, _ in rule_matches] == [5, 6, 7]
    normative_rules = {int(number): ' '.join(sentence.split()) for number, sentence in rule_matches}
    assert normative_rules == {5: 'A book is blocked for a user exactly when the book is adult-rated and the user is a minor.', 6: 'A book is eligible for a user exactly when its primary genre is preferred, it is not blocked for that user, and that user has not rated it.', 7: 'Every eligible book must be recommended to that user.'}
    model = _read_model()
    fact_types = {fact_type['id']: fact_type for fact_type in model['fact_types']}
    assert set(fact_types) == {'recommendation', 'user_rated_book', 'user_is_minor', 'book_rated_adult', 'book_has_genre', 'user_prefers_genre', *BOOKREC_DERIVED_FACT_TYPES}
    expected_derivations = {'book_is_blocked_for': {'body': [{'fact_type': 'book_rated_adult', 'bind': {'book': '$b'}}, {'fact_type': 'user_is_minor', 'bind': {'user': '$u'}}], 'head': {'book': '$b', 'user': '$u'}}, 'book_is_eligible': {'body': [{'fact_type': 'user_prefers_genre', 'bind': {'user': '$u', 'genre': '$g'}}, {'fact_type': 'book_has_genre', 'bind': {'book': '$b', 'genre': '$g'}}], 'negate': [{'fact_type': 'book_is_blocked_for', 'bind': {'book': '$b', 'user': '$u'}}, {'fact_type': 'user_rated_book', 'bind': {'user': '$u', 'book': '$b'}}], 'head': {'book': '$b', 'user': '$u'}}}
    actual_derivations = {fact_type_id: fact_types[fact_type_id]['derivation_rule'] for fact_type_id in sorted(BOOKREC_DERIVED_FACT_TYPES)}
    assert actual_derivations == expected_derivations
    for fact_type_id in BOOKREC_DERIVED_FACT_TYPES:
        assert fact_types[fact_type_id]['derivation'] == 'derived'
        assert fact_types[fact_type_id]['storage'] == 'computed'
    completeness = next(constraint for constraint in model['constraints'] if constraint['id'] == ELIGIBILITY_COMPLETENESS_GUARD)
    expected_completeness = {'antecedent': [{'fact_type': 'book_is_eligible', 'bind': {'book': '$b', 'user': '$u'}}], 'consequent': {'atom': {'fact_type': 'recommendation', 'bind': {'user': '$u', 'book': '$b'}}}}
    actual_completeness = {'antecedent': completeness['antecedent'], 'consequent': completeness['consequent']}
    assert actual_completeness == expected_completeness
    assert completeness['modality'] == 'alethic'
    assert completeness['provenance']['user_quote'] == normative_rules[7]

    def agrees(derivations: Mapping[str, Any], completeness_rule: Mapping[str, Any]) -> bool:
        return derivations == expected_derivations and completeness_rule == expected_completeness
    dirty_polarity = copy.deepcopy(actual_derivations)
    moved = dirty_polarity['book_is_eligible']['negate'].pop(0)
    dirty_polarity['book_is_eligible']['body'].append(moved)
    dirty_multiplicity = copy.deepcopy(actual_derivations)
    dirty_multiplicity['book_is_blocked_for']['body'].append(copy.deepcopy(dirty_multiplicity['book_is_blocked_for']['body'][0]))
    dirty_binding = copy.deepcopy(actual_derivations)
    dirty_binding['book_is_eligible']['head']['user'] = '$b'
    reversed_arrow = copy.deepcopy(actual_completeness)
    antecedent_atom = reversed_arrow['antecedent'][0]
    consequent_atom = reversed_arrow['consequent']['atom']
    reversed_arrow['antecedent'] = [consequent_atom]
    reversed_arrow['consequent'] = {'atom': antecedent_atom}
    assert agrees(actual_derivations, actual_completeness)
    assert not agrees(dirty_polarity, actual_completeness)
    assert not agrees(dirty_multiplicity, actual_completeness)
    assert not agrees(dirty_binding, actual_completeness)
    assert not agrees(actual_derivations, reversed_arrow)

def test_already_rated_recommendation_is_blocking() -> None:
    """Exclude a rated-book absence guard that accepts or blames another pair."""
    model = _read_model()
    population_path = BOOKREC / 'populations' / 'violates-rated.population.json'
    population = _read_json(population_path)
    code, report = _run_check(MODEL_PATH, population_path)
    verdicts = _guard_verdicts(model, report)
    assert population['facts']['recommendation'] == [{'user': 'u-ada', 'book': 'b-dune'}]
    assert {'user': 'u-ada', 'book': 'b-dune'} in population['facts']['user_rated_book']
    assert code == report['exit_code'] == 1
    assert verdicts[RATED_GUARD]['constraint_type'] == 'guarded'
    assert verdicts[RATED_GUARD]['verdict'] == 'fail'
    assert verdicts[RATED_GUARD]['offending_facts'] == [{'$u': 'u-ada', '$b': 'b-dune'}]

def test_adult_recommendation_to_minor_is_blocking() -> None:
    """Exclude a minor/adult guard that accepts or names the wrong subjects."""
    model = _read_model()
    population_path = BOOKREC / 'populations' / 'violates-minor-adult.population.json'
    population = _read_json(population_path)
    code, report = _run_check(MODEL_PATH, population_path)
    verdicts = _guard_verdicts(model, report)
    assert {'user': 'u-minor'} in population['facts']['user_is_minor']
    assert {'book': 'b-redroom'} in population['facts']['book_rated_adult']
    assert {'user': 'u-minor', 'book': 'b-redroom'} in population['facts']['recommendation']
    assert code == report['exit_code'] == 1
    assert verdicts[MINOR_ADULT_GUARD]['constraint_type'] == 'guarded'
    assert verdicts[MINOR_ADULT_GUARD]['verdict'] == 'fail'
    assert verdicts[MINOR_ADULT_GUARD]['offending_facts'] == [{'$u': 'u-minor', '$b': 'b-redroom'}]

def test_every_alethic_guard_binds_on_the_conforming_populations() -> None:
    """Exclude a structured pass whose independently recomputed antecedent is empty."""
    cases = [(_read_model(EXPENSE / 'model.orm.yaml'), EXPENSE / 'model.orm.yaml', EXPENSE / 'population.policy-conforming.json'), (_read_model(MODEL_PATH), MODEL_PATH, BOOKREC / 'populations' / 'conforming.population.json')]
    for model, model_path, population_path in cases:
        population = _read_json(population_path)
        code, report = _run_check(model_path, population_path)
        alethic_ids = {str(constraint['id']) for constraint in model['constraints'] if constraint.get('type') == 'guarded' and constraint.get('modality') == 'alethic'}
        assert alethic_ids
        assert code == 0
        assert _all_nonvacuous_pass(model, population, report, alethic_ids)
    negative_path = BOOKREC / 'populations' / 'violates-rated.population.json'
    negative = _read_json(negative_path)
    negative_model = _read_model(MODEL_PATH)
    _, negative_report = _run_check(MODEL_PATH, negative_path)
    negative_verdicts = _guard_verdicts(negative_model, negative_report)
    negative_counts = guarded_binding_counts(negative_model, negative)
    assert negative_verdicts[MINOR_ADULT_GUARD]['verdict'] == 'pass'
    assert negative_counts[MINOR_ADULT_GUARD] == 0
    assert not _all_nonvacuous_pass(negative_model, negative, negative_report, {MINOR_ADULT_GUARD})
