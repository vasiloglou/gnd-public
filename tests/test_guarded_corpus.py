from __future__ import annotations

import json
import signal
import subprocess
import sys
import time
from collections import Counter
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
from conftest import make_population
from ruamel.yaml import YAML

from gnd import checker, semantic_spec
from gnd.checker import band, check
from gnd.model import load_model
from gnd.population import load_population
from gnd.semantic_adapter import adapt_snapshot_observed
from gnd.synth.assemble import _direct_subtypes
from gnd.synth.boundary import derive_boundary_cases
from gnd.synth.mutate import expected_state, operators_for

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS = REPO_ROOT / 'tests' / 'fixtures' / 'guarded'
EXPECTED = json.loads((CORPUS / 'expected.json').read_text(encoding='utf-8'))
CASES = EXPECTED['cases']

def _case_path(case: dict[str, Any], field: str) -> Path:
    return CORPUS / str(case[field])

def _target(case: dict[str, Any]):
    model = load_model(_case_path(case, 'model'))
    population = load_population(_case_path(case, 'population'), model=model)
    report = check(model, population)
    verdict = next((item for item in report.verdicts if item.constraint_ref == case['constraint_ref']))
    return (model, population, report, verdict)

def _run_cli(case: dict[str, Any]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, '-m', 'gnd', 'check', str(_case_path(case, 'model')), str(_case_path(case, 'population')), '--format', 'json'], cwd=REPO_ROOT, capture_output=True, text=True, check=False)

@pytest.mark.parametrize('case', CASES, ids=[case['id'] for case in CASES])
def test_guarded_corpus_case(case: dict[str, Any]) -> None:
    _model, _population, report, verdict = _target(case)
    assert verdict.verdict == case['verdict']
    assert verdict.reason_code == case['reason_code']
    assert verdict.offending_facts == case['offending_facts']
    if case['binding_count'] is not None:
        assert f"bindings={case['binding_count']}" in verdict.message
    assert band(report) == case['band']
    completed = _run_cli(case)
    assert completed.returncode == case['exit'], 'Assertion did not hold.'
    payload = json.loads(completed.stdout)
    cli_verdict = next((item for item in payload['verdicts'] if item['constraint_ref'] == case['constraint_ref']))
    assert cli_verdict['verdict'] == case['verdict']
    assert cli_verdict['reason_code'] == case['reason_code']
    assert cli_verdict['offending_facts'] == case['offending_facts']

def _document(path: Path) -> dict[str, Any]:
    return YAML(typ='safe').load(path.read_text(encoding='utf-8'))

def _fact_multiset(path: Path) -> Counter[tuple[str, str]]:
    facts = _document(path).get('facts') or {}
    return Counter(((str(fact_type), json.dumps(fact, sort_keys=True, separators=(',', ':'))) for fact_type, rows in facts.items() for fact in rows or []))

def _multiset_delta_size(left: Counter[Any], right: Counter[Any]) -> int:
    return sum((left - right).values()) + sum((right - left).values())

def test_every_exit_zero_case_has_a_one_fact_nonzero_sibling() -> None:
    for case in CASES:
        if case['exit'] != 0:
            continue
        assert case['sibling'], 'Assertion did not hold.'
        original = _case_path(case, 'population')
        sibling = CORPUS / case['sibling']
        assert sibling.is_file(), 'Assertion did not hold.'
        assert _multiset_delta_size(_fact_multiset(original), _fact_multiset(sibling)) == 1
        model = load_model(_case_path(case, 'model'))
        sibling_population = load_population(sibling, model=model)
        assert band(check(model, sibling_population)) != 0
REQUIRED_BRANCHES = {'alethic|comparison|holds', 'alethic|comparison|violated', 'alethic|atom|holds', 'alethic|atom|violated', 'alethic|absence|holds', 'alethic|absence|violated', 'deontic|comparison|holds', 'deontic|comparison|violated', 'deontic|atom|holds', 'deontic|atom|violated', 'deontic|absence|holds', 'deontic|absence|violated', 'vacuous|alethic|any-empty', 'vacuous|deontic|any-empty', 'vacuous|mixed-empty|any-not-all', 'zero-bindings|alethic', 'zero-bindings|deontic', 'unchecked|alethic|values-not-comparable', 'unchecked|deontic|values-not-comparable', 'unchecked|precedence-over-offending', 'unchecked|alethic|literal-type-ambiguous', 'unchecked|deontic|literal-type-ambiguous', 'join|three-atom|violated', 'join|shared-variable|exact-offending', 'join|repeated-variable|holds', 'unchecked|alethic|join-disconnected', 'literal-literal|violated', 'literal-literal|holds', 'band|fail-over-vacuous', 'absence|consequent-populated-nonmatching|holds', 'absence|other-subject-not-credited|holds', 'absence|consequent-populated-multi|violated', 'absence|exact-offending-binding', 'absence|unary-consequent|holds', 'absence|unary-consequent|violated'}

def _missing_branches(cases: list[dict[str, Any]]) -> set[str]:
    actual = {branch for case in cases for branch in case['branches']}
    return REQUIRED_BRANCHES - actual

def test_branch_table_is_complete_against_an_independent_literal() -> None:
    assert _missing_branches(CASES) == set()
    actual = {branch for case in CASES for branch in case['branches']}
    assert actual == REQUIRED_BRANCHES

def test_branch_completeness_oracle_has_a_negative_control() -> None:
    edited = json.loads(json.dumps(CASES))
    edited[0]['branches'] = []
    assert _missing_branches(edited) == {'alethic|comparison|holds'}

@contextmanager
def _deadline(seconds: float, what: str) -> Iterator[None]:

    def _fire(signum: int, frame: object) -> None:
        raise TimeoutError(f'{what} did not return within {seconds}s')
    previous = signal.signal(signal.SIGALRM, _fire)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)

def _performance_population(total_facts: int):
    model = load_model(CORPUS / 'models' / 'join.orm.yaml')
    joined = total_facts // 3
    extra = total_facts - joined * 3
    facts = {'p': [{'x': f'k{index}', 'y': index % 10} for index in range(joined)] + [{'x': f'extra{index}', 'y': 0} for index in range(extra)], 'q': [{'x': f'k{index}', 'z': 10} for index in range(joined)], 'tagged': [{'x': f'k{index}'} for index in range(joined)], 'repeated': [], 'literal_trigger': []}
    population = make_population(model, model='join.orm.yaml', model_id='urn:gnd-fixture:guarded-corpus-join@1', source='fixture', label='boundary', covers=list(facts), facts=facts, instances={})
    return (model, population, joined)

def _best_check_time(total_facts: int) -> float:
    model, population, expected_bindings = _performance_population(total_facts)
    durations: list[float] = []
    with _deadline(10, f'guarded check over {total_facts} facts'):
        for _ in range(3):
            started = time.perf_counter()
            report = check(model, population)
            durations.append(time.perf_counter() - started)
    verdict = next((item for item in report.verdicts if item.constraint_ref == 'constraints[0]'))
    assert verdict.verdict == 'pass'
    assert f'bindings={expected_bindings}' in verdict.message
    return min(durations)

def test_connected_three_atom_join_meets_the_declared_bound() -> None:
    t10k = _best_check_time(10000)
    t20k = _best_check_time(20000)
    assert t10k < 2.0
    assert t20k < 2.0
    assert t20k <= max(2 * t10k, 0.2)

def test_zero_bindings_precede_consequent_literal_interpretation() -> None:
    model = load_model(CORPUS / 'models' / 'undecidable.orm.yaml')
    population = make_population(model, model='undecidable.orm.yaml', model_id='urn:gnd-fixture:guarded-corpus-undecidable@1', source='fixture', label='boundary', covers=['observed_pair'], facts={'observed_pair': [{'mode': 'matches-none', 'left': 'heavy', 'right': 'ignored'}]}, instances={})
    report = check(model, population)
    verdicts = {verdict.constraint_ref: verdict for verdict in report.verdicts if verdict.constraint_ref in {'constraints[3]', 'constraints[4]'}}
    assert set(verdicts) == {'constraints[3]', 'constraints[4]'}
    for verdict in verdicts.values():
        assert verdict.verdict == 'pass'
        assert verdict.reason_code is None
        assert verdict.offending_facts == []
        assert 'bindings=0' in verdict.message
    assert band(report) == 0

def test_guarded_evaluator_is_total_on_hostile_internal_shapes() -> None:
    model = load_model(CORPUS / 'models' / 'alethic.orm.yaml')
    good = load_population(CORPUS / 'cases' / 'a-c1.yaml', model=model)
    adapted = adapt_snapshot_observed(model, good)
    constraint = adapted.snapshot.constraints[0]
    assert not hasattr(checker, '_check_guarded')
    hostile_constraints = (replace(constraint, antecedent=()), replace(constraint, variant='banana'), replace(constraint, consequent_kind='', consequent=()))
    for hostile in hostile_constraints:
        state, witness = semantic_spec.guarded_result(hostile, adapted.snapshot)
        assert state == -1
        assert witness == []
    first = adapted.snapshot.relations[0]
    hostile_snapshot = replace(adapted.snapshot, relations=(replace(first, rows=((),)), *adapted.snapshot.relations[1:]))
    state, witness = semantic_spec.guarded_result(constraint, hostile_snapshot)
    assert state == -1
    assert witness == []

def test_synth_oracle_mirrors_guarded_any_empty_vacuity() -> None:
    model = load_model(CORPUS / 'models' / 'alethic.orm.yaml')
    document = _document(CORPUS / 'cases' / 'v-3.yaml')
    state = expected_state(model.constraints[0], None, document, model, _direct_subtypes(model))
    assert state is not None
    assert (state.ground_truth, state.expected_verdict, state.reason) == ('no-subjects', 'vacuous', 'fact-types-empty')

def test_synth_names_the_guarded_post_mvp_witness_gap() -> None:
    model = load_model(CORPUS / 'models' / 'alethic.orm.yaml')
    document = _document(CORPUS / 'cases' / 'a-c1.yaml')
    mutations, mutation_gaps = operators_for(model, 'constraints[0]', document)
    boundaries, boundary_gaps = derive_boundary_cases(model, 'constraints[0]', document)
    assert mutations == []
    assert boundaries == []
    assert len(mutation_gaps) == len(boundary_gaps) == 1
    assert 'post-MVP frontier' in mutation_gaps[0]['mechanism']
    assert 'post-MVP frontier' in boundary_gaps[0].reason
SRC = REPO_ROOT / 'src' / 'gnd'
ABSENCE_CASE_IDS = frozenset({'A-B1', 'A-B2', 'A-B3', 'A-B4', 'A-B5', 'A-B6', 'D-B1', 'D-B2', 'S-1', 'S-2'})

def _constraint_for(case: dict[str, Any]) -> dict[str, Any] | None:
    ref = str(case['constraint_ref'])
    if not (ref.startswith('constraints[') and ref.endswith(']')):
        return None
    model = load_model(_case_path(case, 'model'))
    return model.constraints[int(ref[len('constraints['):-1])]

def _derived_absence_case_ids() -> frozenset[str]:
    found = set()
    for case in CASES:
        constraint = _constraint_for(case)
        if isinstance(constraint, dict) and 'absence' in (constraint.get('consequent') or {}):
            found.add(str(case['id']))
    return frozenset(found)

def _literal_positions(atom: dict[str, Any], role_names: list[str]) -> tuple[int, ...]:
    binds = atom.get('bind') or {}
    return tuple((index for index, role_name in enumerate(role_names) if checker._guarded_variable(binds.get(role_name)) is None))

def _subject_blind_rows(positions: tuple[int, ...]) -> type[set]:

    class _Rows(set):

        def __contains__(self, item: object) -> bool:
            row = tuple(item)
            key = tuple((row[index] for index in positions))
            return any((tuple((other[index] for index in positions)) == key for other in set.__iter__(self)))
    return _Rows

def _committed_absence_outcomes() -> dict[str, tuple[str, list[Any]]]:
    return {str(case['id']): (str(case['verdict']), case['offending_facts']) for case in CASES if case['id'] in ABSENCE_CASE_IDS}

def _mutated_guarded_atom_state(mode: str):

    def state(atom, names, binding, snapshot):
        fact_position = semantic_spec.snapshot_fact_index(snapshot, atom.fact_type)
        relation_position = semantic_spec.snapshot_relation_index(snapshot, atom.fact_type)
        if fact_position < 0 or relation_position < 0:
            return -1
        fact = snapshot.fact_types[fact_position]
        relation = snapshot.relations[relation_position]
        if mode == 'membership-blind':
            return int(bool(relation.rows))
        for row in relation.rows:
            matches = True
            for role, term in atom.bindings:
                column = semantic_spec.fact_role_index(fact, role)
                if column < 0 or column >= len(row) or row[column] is None:
                    return -1
                if term.kind == 'literal' and (term.literal is None or not semantic_spec.scalar_identical(row[column], term.literal)):
                    matches = False
            if matches:
                return 1
        return 0
    return state

def _absence_outcomes_under(monkeypatch, mode: str) -> dict[str, tuple[str, list[Any]]]:
    monkeypatch.setattr(semantic_spec, 'guarded_atom_state', _mutated_guarded_atom_state(mode))
    outcomes: dict[str, tuple[str, list[Any]]] = {}
    for case in CASES:
        if case['id'] not in ABSENCE_CASE_IDS:
            continue
        _model, _population, _report, verdict = _target(case)
        outcomes[str(case['id'])] = (verdict.verdict, verdict.offending_facts)
    return outcomes

def _partition(monkeypatch, mode: str) -> tuple[set[str], set[str]]:
    committed = _committed_absence_outcomes()
    measured = _absence_outcomes_under(monkeypatch, mode)
    assert set(measured) == ABSENCE_CASE_IDS
    disagree = {cid for cid, outcome in measured.items() if outcome != committed[cid]}
    return (ABSENCE_CASE_IDS - disagree, disagree)

def test_the_graded_absence_set_is_derived_and_pinned() -> None:
    assert _derived_absence_case_ids() == ABSENCE_CASE_IDS

def test_absence_membership_mutant_dies_only_on_the_new_cases(monkeypatch) -> None:
    agree, disagree = _partition(monkeypatch, 'membership-blind')
    assert disagree == {'A-B3', 'A-B4', 'A-B6', 'S-1'}
    assert agree == {'A-B1', 'A-B2', 'A-B5', 'D-B1', 'D-B2', 'S-2'}

def test_absence_subject_blind_mutant_dies_on_the_wrong_subject_cases(monkeypatch) -> None:
    agree, disagree = _partition(monkeypatch, 'subject-blind')
    assert disagree == {'A-B4', 'A-B6', 'S-1'}
    assert agree == {'A-B1', 'A-B2', 'A-B3', 'A-B5', 'D-B1', 'D-B2', 'S-2'}
CLOSED_WORLD_SENTENCE = 'Both use the population as a closed world regardless of `covers`; this intentionally differs from the coverage-omission rule for mandatory constraints.'

def _normalized(text: str) -> str:
    return ' '.join(text.split())

def _homes_among(texts: dict[str, str]) -> set[str]:
    needle = _normalized(CLOSED_WORLD_SENTENCE)
    return {name for name, text in texts.items() if needle in _normalized(text)}

def test_the_guarded_closed_world_sentence_occurs_once_and_is_cited() -> None:
    control = _homes_among({'a': CLOSED_WORLD_SENTENCE, 'b': 'prefix ' + CLOSED_WORLD_SENTENCE})
    assert control == {'a', 'b'}, 'Assertion did not hold.'
    candidates = [*(SRC / 'skills').rglob('*.md'), *SRC.rglob('*.py')]
    texts = {str(path.relative_to(REPO_ROOT)): path.read_text(encoding='utf-8') for path in candidates}
    assert _homes_among(texts) == {'src/gnd/skills/gnd-orm-core/references/representation-format.md'}
    source = (SRC / 'correspondence.py').read_text(encoding='utf-8')
    start = source.index('def _indexed_guarded_verdict(')
    body = source[start:source.index('\ndef ', start + 1)]
    assert 'representation-format.md' in body, 'Assertion did not hold.'
PHASE_TWO_ANSWER_KEY = (('A-C1', 'pass', None, [], 0, 0), ('A-C2', 'fail', None, [{'$e': 'e1', '$a': 2500}], 1, 1), ('A-A1', 'pass', None, [], 0, 0), ('A-A2', 'fail', None, [{'$e': 'e1'}], 1, 1), ('A-B1', 'pass', None, [], 0, 0), ('A-B2', 'fail', None, [{'$e': 'e1'}], 1, 1), ('D-C1', 'pass', None, [], 0, 0), ('D-C2', 'warning', None, [{'$e': 'e1', '$a': 2500}], 0, 0), ('D-A1', 'pass', None, [], 0, 0), ('D-A2', 'warning', None, [{'$e': 'e1'}], 0, 0), ('D-B1', 'pass', None, [], 0, 0), ('D-B2', 'warning', None, [{'$e': 'e1'}], 0, 0), ('V-1', 'vacuous', None, [], 2, 2), ('V-2', 'vacuous', None, [], 2, 2), ('V-3', 'vacuous', None, [], 2, 2), ('Z-1', 'pass', None, [], 0, 0), ('Z-2', 'pass', None, [], 0, 0), ('U-G1', 'unchecked', 'values-not-comparable', [], 4, 4), ('U-G2', 'unchecked', 'values-not-comparable', [], 0, 0), ('U-G3', 'unchecked', 'values-not-comparable', [], 4, 4), ('U-G4', 'unchecked', 'literal-type-ambiguous', [], 4, 4), ('U-G5', 'unchecked', 'literal-type-ambiguous', [], 0, 0), ('J-1', 'fail', None, [{'$x': 'a', '$y': 5, '$z': 1}], 1, 1), ('J-2', 'fail', None, [{'$x': 'b', '$y': 100, '$z': 1}], 1, 1), ('J-3', 'pass', None, [], 0, 0), ('X-D1', 'unchecked', 'join-disconnected', [], 4, 4), ('X-L1', 'fail', None, [{}], 1, 1), ('X-L2', 'pass', None, [], 0, 0), ('X-B1', 'fail', None, [{'$x': 'a', '$y': 5, '$z': 1}], 1, 1))

def test_phase_two_answer_key_is_unmoved() -> None:
    by_id = {str(case['id']): case for case in CASES}
    for case_id, verdict, reason_code, offending, band_value, exit_code in PHASE_TWO_ANSWER_KEY:
        case = by_id[case_id]
        actual = (str(case['verdict']), case['reason_code'], case['offending_facts'], case['band'], case['exit'])
        assert actual == (verdict, reason_code, offending, band_value, exit_code), 'Assertion did not hold.'
    assert len(PHASE_TWO_ANSWER_KEY) == 29

def test_the_subject_blind_mutant_is_not_bind_order_dependent() -> None:
    forward = {'fact_type': 'expense_has_status', 'bind': {'expense': '$e', 'status': 'blocked'}}
    swapped = {'fact_type': 'expense_has_status', 'bind': {'status': 'blocked', 'expense': '$e'}}
    assert _literal_positions(forward, ['expense', 'status']) == (1,)
    assert _literal_positions(swapped, ['status', 'expense']) == (0,)
    unary = {'fact_type': 'expense_is_submitted', 'bind': {'expense': '$e'}}
    assert _literal_positions(unary, ['expense']) == ()
    rows = _subject_blind_rows((1,))({('e1', 'blocked')})
    assert ('e9', 'blocked') in rows, 'Assertion did not hold.'
    assert ('e1', 'review') not in rows, 'Assertion did not hold.'
GUARDED_MINIMAL = REPO_ROOT / 'tests' / 'fixtures' / 'models' / 'guarded_minimal.orm.yaml'

def test_r_empty_was_already_killed_outside_the_corpus_but_r_blind_was_not(tmp_path: Path, monkeypatch) -> None:
    fact_types = ['expense_in_category', 'expense_has_amount', 'expense_has_status']
    document = {'population': {'model': 'guarded_minimal.orm.yaml', 'model_id': 'urn:gnd-fixture:guarded-minimal@1', 'source': 'fixture', 'covers': fact_types}, 'instances': {}, 'facts': {'expense_in_category': [{'expense': 1, 'category': 'travel'}], 'expense_has_amount': [{'expense': 1, 'amount': 1500}], 'expense_has_status': [{'expense': 1, 'status': 'review'}]}}
    path = tmp_path / 'populated.yaml'
    with path.open('w', encoding='utf-8') as handle:
        YAML().dump(document, handle)
    model = load_model(GUARDED_MINIMAL)
    population = load_population(path, model=model)

    def _absence_verdict() -> tuple[str, int]:
        report = check(model, population)
        verdict = next((item for item in report.verdicts if item.constraint_ref == 'constraints[2]'))
        return (verdict.verdict, band(report))
    real = semantic_spec.guarded_atom_state
    assert _absence_verdict() == ('pass', 0)
    monkeypatch.setattr(semantic_spec, 'guarded_atom_state', _mutated_guarded_atom_state('membership-blind'))
    assert _absence_verdict() == ('fail', 1), 'Assertion did not hold.'
    monkeypatch.setattr(semantic_spec, 'guarded_atom_state', real)
    monkeypatch.setattr(semantic_spec, 'guarded_atom_state', _mutated_guarded_atom_state('subject-blind'))
    assert _absence_verdict() == ('pass', 0), 'Assertion did not hold.'
