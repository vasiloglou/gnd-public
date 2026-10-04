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
EXPENSE = REPO_ROOT / "examples/expense-tracker"
MODEL_PATH = EXPENSE / "model.orm.yaml"
POLICY_LIMITS = {"meals": 75, "training": 1500, "travel": 2000, "equipment": 3000}
POLICY_IDS = {category: f"policy_limit_{category}" for category in POLICY_LIMITS}
POLICY_ID_SET = set(POLICY_IDS.values())
OLD_TEXTUAL_EXPRESSION = "Each Expense in ExpenseCategory 'meals' has AmountEur at most 75; in 'training' at most 1500; in 'travel' at most 2000; in 'equipment' at most 3000."
def _read_json(path: Path) -> JsonObject:
    """Read one committed JSON object."""
    value = json.loads(path.read_text(encoding='utf-8'))
    assert isinstance(value, dict), path
    return value

def _read_model_document() -> JsonObject:
    """Read the model as the YAML mapping the Phase 4 helper consumes."""
    value = YAML(typ='safe').load(MODEL_PATH.read_text(encoding='utf-8'))
    assert isinstance(value, dict)
    return value

def _run_gnd_json(*args: str) -> tuple[int, JsonObject]:
    """Run GND through its subprocess interface and parse its JSON payload."""
    completed = subprocess.run([sys.executable, '-m', 'gnd', *args, '--format', 'json'], cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=15)
    assert completed.stdout, completed.stderr
    payload = json.loads(completed.stdout)
    assert isinstance(payload, dict)
    return (completed.returncode, payload)

def _run_check(path: Path) -> tuple[int, JsonObject]:
    """Run ``gnd check`` and require a schema-valid report."""
    code, payload = _run_gnd_json('check', str(MODEL_PATH), str(path))
    REPORT_VALIDATOR.validate(payload)
    return (code, payload)

def _policy_verdicts(model: Mapping[str, Any], report: Mapping[str, Any]) -> JsonObject:
    """Resolve positional report references to the four stable policy IDs."""
    ids = ref_to_id(model)
    resolved = {ids[str(verdict['constraint_ref'])]: verdict for verdict in report['verdicts'] if str(verdict['constraint_ref']) in ids and ids[str(verdict['constraint_ref'])] in POLICY_ID_SET}
    assert set(resolved) == POLICY_ID_SET
    return resolved

def _expected_policy_constraints() -> list[JsonObject]:
    """Return the four complete canonical policy fragments from section 6.1."""
    return [{'id': POLICY_IDS[category], 'type': 'guarded', 'source': 'user-supplied', 'status': 'confirmed', 'modality': 'alethic', 'antecedent': [{'fact_type': 'expense_in_category', 'bind': {'expense': '$e', 'category': category}}, {'fact_type': 'expense_has_amount', 'bind': {'expense': '$e', 'amount': '$a'}}], 'consequent': {'comparison': {'operator': '<=', 'left': '$a', 'right': limit}}, 'provenance': {'added_at_step': '7d', 'user_quote': f"Each Expense in ExpenseCategory '{category}' has AmountEur at most {limit}."}} for category, limit in POLICY_LIMITS.items()]
def test_policy_prose_became_exactly_four_alethic_guarded_literal_comparisons() -> None:
    """Exclude a valid-looking model that retained prose or changed a policy detail."""
    load_model(MODEL_PATH)
    document = _read_model_document()
    policies = [constraint for constraint in document['constraints'] if str(constraint.get('id', '')).startswith('policy_limit_')]
    assert policies == _expected_policy_constraints()
    assert OLD_TEXTUAL_EXPRESSION not in MODEL_PATH.read_text(encoding='utf-8')
    assert all(constraint.get('expression') != OLD_TEXTUAL_EXPRESSION for constraint in document['constraints'])

def test_a_ninety_euro_meal_is_blocking_and_names_the_binding() -> None:
    """Exclude a conversion that still accepts 90 EUR or blames another binding."""
    model = _read_model_document()
    code, report = _run_check(EXPENSE / 'population.policy-meal-90.json')
    policies = _policy_verdicts(model, report)
    assert code == 1
    assert policies['policy_limit_meals']['verdict'] == 'fail'
    assert policies['policy_limit_meals']['offending_facts'] == [{'$e': 9001, '$a': 90}]

def test_conforming_policy_population_exercises_every_guard(tmp_path: Path) -> None:
    """Exclude zero-binding passes that masquerade as exercised policy guards."""
    model = _read_model_document()
    population_path = EXPENSE / 'population.policy-conforming.json'
    population = _read_json(population_path)
    code, report = _run_check(population_path)
    policies = _policy_verdicts(model, report)
    counts = guarded_binding_counts(model, population)
    assert code == 0
    assert all(policies[constraint_id]['verdict'] == 'pass' for constraint_id in POLICY_ID_SET)
    assert {constraint_id: counts[constraint_id] for constraint_id in POLICY_ID_SET} == {constraint_id: 1 for constraint_id in POLICY_ID_SET}
    dirty = copy.deepcopy(population)
    dirty['facts']['expense_in_category'] = [row for row in dirty['facts']['expense_in_category'] if row['category'] != 'meals']
    dirty_path = tmp_path / 'without-meals.population.json'
    dirty_path.write_text(json.dumps(dirty), encoding='utf-8')
    _, dirty_report = _run_check(dirty_path)
    dirty_policies = _policy_verdicts(model, dirty_report)
    dirty_counts = guarded_binding_counts(model, dirty)
    assert dirty_policies['policy_limit_meals']['verdict'] == 'pass'
    assert dirty_counts['policy_limit_meals'] == 0
    assert not all(dirty_counts[constraint_id] > 0 for constraint_id in POLICY_ID_SET)
