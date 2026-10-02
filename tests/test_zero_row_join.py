from __future__ import annotations

import json
import subprocess
import sys

import pytest
from support.cli_runner import completed_text, run_process
from support.repository import REPO_ROOT

CORPUS = REPO_ROOT / 'tests' / 'fixtures' / 'adversarial'
MODELS = CORPUS / 'models'
POPS = CORPUS / 'populations'
PROBE_MODELS = ['f05_uniqueness_external.orm.yaml', 'f05_frequency_external.orm.yaml', 'f05_setfam_join.orm.yaml']

def _run(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return completed_text(run_process([sys.executable, '-m', 'gnd', *argv], cwd=REPO_ROOT))

def _check(model: str, population: str) -> tuple[int, dict]:
    result = _run(['check', str(MODELS / model), str(POPS / population), '--format', 'json'])
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        pytest.fail(f'no json payload for {model} / {population}: {error}\n{result.stdout}')
    return (result.returncode, payload)

@pytest.mark.parametrize('model', PROBE_MODELS)
def test_probe_models_are_valid(model: str) -> None:
    result = _run(['validate', str(MODELS / model), '--format', 'json'])
    assert result.returncode == 0, 'Assertion did not hold.'
CASES = [('f05_uniqueness_external.orm.yaml', 'f05_uniqueness_both_empty.yaml', 2, 'uniqueness', 'vacuous', 'control'), ('f05_uniqueness_external.orm.yaml', 'f05_uniqueness_one_side_empty.yaml', 2, 'uniqueness', 'vacuous', 'property'), ('f05_uniqueness_external.orm.yaml', 'f05_uniqueness_anchors_disjoint.yaml', 2, 'uniqueness', 'vacuous', 'property'), ('f05_uniqueness_external.orm.yaml', 'f05_uniqueness_join_rows_clean.yaml', 0, 'uniqueness', 'pass', 'control'), ('f05_uniqueness_external.orm.yaml', 'f05_uniqueness_join_rows_duplicate.yaml', 1, 'uniqueness', 'fail', 'control'), ('f05_frequency_external.orm.yaml', 'f05_frequency_one_side_empty.yaml', 2, 'frequency', 'vacuous', 'property'), ('f05_frequency_external.orm.yaml', 'f05_frequency_join_rows_clean.yaml', 0, 'frequency', 'pass', 'control'), ('f05_setfam_join.orm.yaml', 'f05_setfam_subset_superset_zero_row.yaml', 1, 'subset', 'fail', 'control'), ('f05_setfam_join.orm.yaml', 'f05_setfam_subset_subject_zero_row.yaml', 0, 'subset', 'pass', 'control'), ('f05_setfam_join.orm.yaml', 'f05_setfam_exclusion_one_side_zero_row.yaml', 0, 'exclusion', 'pass', 'control'), ('f05_setfam_join.orm.yaml', 'f05_setfam_equality_both_zero_row.yaml', 2, 'equality', 'vacuous', 'property'), ('f05_setfam_join.orm.yaml', 'f05_setfam_all_zero_row.yaml', 2, 'equality', 'vacuous', 'property'), ('f05_setfam_join.orm.yaml', 'f05_setfam_value_comparison_disjoint_anchors.yaml', 2, 'value-comparison', 'vacuous', 'property'), ('f05_setfam_join.orm.yaml', 'f05_setfam_value_comparison_join_rows_clean.yaml', 0, 'value-comparison', 'pass', 'control')]

@pytest.mark.parametrize('model,population,exit_code,ctype,verdict,role', CASES, ids=[c[1].replace('f05_', '').replace('.yaml', '') for c in CASES])
def test_zero_row_join_verdict(model: str, population: str, exit_code: int, ctype: str, verdict: str, role: str) -> None:
    rc, payload = _check(model, population)
    assert rc == exit_code, 'Assertion did not hold.'
    assert payload['acceptance_ready'] == (exit_code == 0), 'Assertion did not hold.'
    targeted = [v for v in payload['verdicts'] if v['constraint_type'] == ctype]
    assert targeted, 'Assertion did not hold.'
    observed = {v['verdict'] for v in targeted}
    assert verdict in observed, 'Assertion did not hold.'
    if role == 'property':
        assert 'pass' not in observed, 'Assertion did not hold.'

def test_anchors_disjoint_is_the_stronger_red() -> None:
    rc, payload = _check('f05_uniqueness_external.orm.yaml', 'f05_uniqueness_anchors_disjoint.yaml')
    coverage = {k: c['facts'] for k, c in payload['coverage'].items()}
    assert coverage == {'person_has_fname': 2, 'person_has_lname': 2}, 'Assertion did not hold.'
    assert rc == 2, 'Assertion did not hold.'
ANCHORS_01_1 = [('probe-1-omission', 'omission.orm.yaml', 'omission.missing_role.yaml', 3, None), ('probe-2-textual-alethic', 'textual_alethic.orm.yaml', 'textual_alethic.violating.yaml', 4, 'textual-not-mechanical'), ('probe-3-multirole-xor', 'xor_multirole.orm.yaml', 'xor_multirole.neither.yaml', 4, 'xor-disjunctive-undefined'), ('probe-5-subtype-mandatory', 'subtype_mandatory.orm.yaml', 'subtype_mandatory.no_plate.yaml', 1, None), ('type-invalid-range', 'typed_range.orm.yaml', 'typed_range.string_value.yaml', 3, None)]

@pytest.mark.parametrize('anchor_id,model,population,exit_code,reason_code', ANCHORS_01_1, ids=[a[0] for a in ANCHORS_01_1])
def test_01_1_probe_anchor_still_closes(anchor_id: str, model: str, population: str, exit_code: int, reason_code: str | None) -> None:
    rc, payload = _check(model, population)
    assert rc == exit_code, 'Assertion did not hold.'
    if reason_code is not None:
        observed = [v.get('reason_code') for v in payload.get('verdicts', [])]
        assert reason_code in observed, 'Assertion did not hold.'

def test_ring_pass_is_the_withdrawn_probe_4_regression() -> None:
    checker_dir = REPO_ROOT / 'tests' / 'fixtures' / 'checker'
    result = _run(['check', str(checker_dir / 'ring.orm.yaml'), str(checker_dir / 'population.ring_pass.yaml'), '--format', 'json'])
    assert result.returncode == 0, 'Assertion did not hold.'
    payload = json.loads(result.stdout)
    assert payload['counts'] == {'pass': 13, 'fail': 0, 'warning': 0, 'unchecked': 0, 'vacuous': 0}, 'Assertion did not hold.'

def test_misc_pass_still_exits_4() -> None:
    checker_dir = REPO_ROOT / 'tests' / 'fixtures' / 'checker'
    result = _run(['check', str(checker_dir / 'misc.orm.yaml'), str(checker_dir / 'population.misc_pass.yaml'), '--format', 'json'])
    assert result.returncode == 4, 'Assertion did not hold.'
