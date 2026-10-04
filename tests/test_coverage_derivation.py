from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator
from support.cli_runner import run_main
from support.repository import REPO_ROOT

CORPUS = Path(__file__).parent / 'fixtures/phase3-consumers'
EXPECTED = (CORPUS / 'answers/coverage-v4.json').read_text(encoding='utf-8')
import pytest

from gnd.address import derivation_address, parse_address


def test_parse_address_learns_the_derivation_class() -> None:
    parsed = parse_address(derivation_address('book_is_eligible'))
    assert parsed is not None
    assert parsed.element_class == 'derivation'
    assert parsed.addressing == 'declared-id'
    assert parsed.identifier == 'book_is_eligible'

@pytest.mark.parametrize('hostile', ['derivation:', 'derivation: x', 'derivation:x ', 'derivation', 'derivations:x'])
def test_parse_address_stays_total_over_hostile_derivation_strings(hostile: str) -> None:
    assert parse_address(hostile) is None

def test_derivation_and_fact_type_addresses_are_distinct() -> None:
    assert derivation_address('x') != 'fact_type:x'
    fact = parse_address('fact_type:x')
    derived = parse_address('derivation:x')
    assert fact is not None and derived is not None
    assert fact.element_class != derived.element_class

def _run(arguments: list[str], *, cwd: Path) -> tuple[int, str]:
    result = run_main(arguments, cwd=cwd, capture_stderr=False)
    return (result.returncode, result.stdout.decode('utf-8', errors='surrogatepass'))

def _mask_version(raw: str) -> str:
    return re.sub('"gnd_version": "[^"]*"', '"gnd_version": "MASKED"', raw)

def test_coverage_consumes_v4_evidence_and_emits_the_answer_payload() -> None:
    code, stdout = _run(['coverage', 'eligibility.orm.yaml', '--check', 'check-v4.exact.payload.json', '--format', 'json'], cwd=CORPUS)
    assert code == 0
    assert _mask_version(stdout).strip() == EXPECTED.strip()

def test_coverage_census_counts_the_derivation_obligation_exactly_once() -> None:
    code, stdout = _run(['coverage', 'eligibility.orm.yaml', '--check', 'check-v4.exact.payload.json', '--format', 'json'], cwd=CORPUS)
    assert code == 0
    payload = json.loads(_mask_version(stdout))
    assert payload['schema_version'] == 4
    assert payload['census']['derivation']['in_model'] == 1
    rows = [row for row in payload['elements'] if row['class'] == 'derivation']
    assert [row['address'] for row in rows] == ['derivation:book_is_eligible']
    fact_rows = [row for row in payload['elements'] if row['address'] == 'fact_type:book_is_eligible']
    assert len(fact_rows) == 1

def test_legacy_model_coverage_keeps_schema_version_one() -> None:
    code, stdout = _run(['coverage', 'legacy-derived.orm.yaml', '--format', 'json'], cwd=CORPUS)
    assert code == 0
    payload = json.loads(stdout)
    assert payload['schema_version'] == 3
    assert 'derivation' not in payload['census']
    assert all(row['class'] != 'derivation' for row in payload['elements'])

def _coverage_schema() -> dict:
    return json.loads((REPO_ROOT / 'src/gnd/coverage.schema.json').read_text(encoding='utf-8'))

def test_the_published_coverage_schema_admits_both_variants() -> None:
    validator = Draft202012Validator(_coverage_schema())
    answer = json.loads(EXPECTED)
    assert list(validator.iter_errors(answer)) == []
    code, stdout = _run(['coverage', 'legacy-derived.orm.yaml', '--format', 'json'], cwd=CORPUS)
    assert code == 0
    assert list(validator.iter_errors(json.loads(stdout))) == []

def test_the_published_coverage_schema_refuses_what_the_product_refuses() -> None:
    validator = Draft202012Validator(_coverage_schema())
    answer = json.loads(EXPECTED)
    non_derivation_version_with_derivation_census = json.loads(EXPECTED)
    non_derivation_version_with_derivation_census['schema_version'] = 3
    assert list(validator.iter_errors(non_derivation_version_with_derivation_census)) != []
    derivation_version_without_derivation_census = json.loads(EXPECTED)
    del derivation_version_without_derivation_census['census']['derivation']
    assert list(validator.iter_errors(derivation_version_without_derivation_census)) != []
    frozen_with_unbound = json.loads(EXPECTED)
    frozen_with_unbound['schema_version'] = 2
    assert list(validator.iter_errors(frozen_with_unbound)) != []
    current_without_unbound = json.loads(EXPECTED)
    del current_without_unbound['sources']['unbound']
    assert list(validator.iter_errors(current_without_unbound)) != []
    bad_class = json.loads(EXPECTED)
    bad_class['elements'][-1]['class'] = 'derivations'
    assert list(validator.iter_errors(bad_class)) != []
    assert hashlib.sha256(json.dumps(answer, sort_keys=True).encode()).hexdigest()
