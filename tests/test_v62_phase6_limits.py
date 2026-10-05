from __future__ import annotations

import json
import time
from dataclasses import replace
from pathlib import Path

from ruamel.yaml import YAML
from support.v62_phase6_corpus import ANSWERS, assert_answer, document

from gnd.correspondence import (
    GUARDED_EXISTS_WORK_LIMIT,
    _indexed_guarded_bindings,
    _indexed_guarded_exists_verdict,
)
from gnd.model import load_model
from gnd.population import load_population
from gnd.semantic_adapter import adapt_snapshot_observed
from gnd.terms import compare_terms, evaluate_term


def _prepared(tmp_path: Path, *, rows: int, disconnected: bool=False, include_where: bool=False):
    model_doc = document()
    exists = model_doc['constraints'][0]['consequent']['exists']
    if not include_where:
        exists.pop('where', None)
    facts: dict[str, list[dict]]
    if disconnected:
        exists['atoms'][1]['bind'] = {'cell': '$cell2', 'pci': '$neighbor_pci2', 'modulus': '$modulus2'}
        facts = {'radio_sample': [{'sample': 's0', 'monitor': 'm0', 'pci': 29, 'token': 't0'}], 'neighbor_seen': [{'sample': 's0', 'neighbor': f'n{index}'} for index in range(rows)], 'neighbor_cell': [{'cell': f'c{index}', 'pci': 59, 'modulus': 30} for index in range(rows)]}
    else:
        facts = {'radio_sample': [{'sample': f's{index}', 'monitor': f'm{index}', 'pci': 29, 'token': f't{index}'} for index in range(rows)], 'neighbor_seen': [{'sample': f's{index}', 'neighbor': f'n{index}'} for index in range(rows)], 'neighbor_cell': [{'cell': f'n{index}', 'pci': 59, 'modulus': 30} for index in range(rows)]}
    tmp_path.mkdir(parents=True, exist_ok=True)
    model_path = tmp_path / 'model.orm.yaml'
    with model_path.open('w', encoding='utf-8') as handle:
        YAML(typ='safe').dump(model_doc, handle)
    population_path = tmp_path / 'population.pop.json'
    population_path.write_text(json.dumps({'population': {'model': 'model.orm.yaml', 'model_id': model_doc['model_id'], 'source': 'fixture', 'label': 'boundary', 'covers': ['radio_sample', 'neighbor_seen', 'neighbor_cell']}, 'facts': facts}, separators=(',', ':')), encoding='utf-8')
    model = load_model(model_path)
    population = load_population(population_path, model=model)
    adapted = adapt_snapshot_observed(model, population)
    constraint = adapted.snapshot.constraints[0]
    valid, names, bindings = _indexed_guarded_bindings(constraint, adapted.snapshot)
    assert valid
    return (adapted, constraint, names, bindings)

def _run(adapted, constraint, names, bindings, counts):
    return _indexed_guarded_exists_verdict(constraint, adapted.snapshot, names, bindings, adapted.snapshot.covers, work_counts=counts)

def test_exists_join_is_bounded(tmp_path: Path) -> None:
    adapted, constraint, names, bindings = _prepared(tmp_path, rows=20000)
    counts: dict[str, int] = {}
    started = time.perf_counter()
    verdict = _run(adapted, constraint, names, bindings, counts)
    elapsed = time.perf_counter() - started
    assert verdict[:2] == ('pass', None)
    assert len(bindings) == 20000
    assert counts == {'candidate_rows': 40000, 'index_probes': 40000, 'merged_bindings': 40000, 'term_nodes': 0, 'term_operations': 0, 'maximum_value_bits': 0, 'total_work': 120000}
    for name in ('candidate_rows', 'index_probes', 'merged_bindings', 'term_nodes', 'term_operations', 'maximum_value_bits', 'total_work'):
        assert counts[name] == ANSWERS['E21'][name]
    assert counts['total_work'] <= GUARDED_EXISTS_WORK_LIMIT
    elapsed_limit = ANSWERS['E21']['elapsed_seconds_max']
    assert elapsed < elapsed_limit, f'existential join took {elapsed:.3f}s (measured locally)'
    term_adapted, term_constraint, term_names, term_bindings = _prepared(tmp_path / 'term-work', rows=20000, include_where=True)
    term_constraint = replace(term_constraint, exists_where=term_constraint.exists_where * 5)
    term_counts: dict[str, int] = {}
    term_result = _run(term_adapted, term_constraint, term_names, term_bindings, term_counts)
    term_verdict, term_reason, term_witnesses = term_result
    assert term_verdict == 'unchecked' and term_reason == 'guarded-exists-work-limit'
    assert term_witnesses == ()
    assert term_counts['total_work'] > GUARDED_EXISTS_WORK_LIMIT
    term_control = {'verdict': term_verdict, 'reason': term_reason, 'term_nodes_positive': term_counts['term_nodes'] > 0, 'term_operations_positive': term_counts['term_operations'] > 0, 'maximum_value_bits_positive': term_counts['maximum_value_bits'] > 0, 'total_work': term_counts['total_work'], 'partial_witness_suppressed': term_witnesses == ()}
    assert_answer('E21', exit=0, input_rows=20000, candidate_rows=counts['candidate_rows'], index_probes=counts['index_probes'], merged_bindings=counts['merged_bindings'], term_nodes=counts['term_nodes'], term_operations=counts['term_operations'], maximum_value_bits=counts['maximum_value_bits'], total_work=counts['total_work'], work='within-budget', elapsed_seconds_max=elapsed_limit, term_work_control=term_control)

def test_exists_work_limit_is_unchecked(tmp_path: Path) -> None:
    adapted, constraint, names, bindings = _prepared(tmp_path, rows=500, disconnected=True)
    counts: dict[str, int] = {}
    verdict, reason, witnesses = _run(adapted, constraint, names, bindings, counts)
    assert verdict == 'unchecked'
    assert reason == 'guarded-exists-work-limit'
    assert witnesses == ()
    for name in ('candidate_rows', 'index_probes', 'merged_bindings', 'total_work'):
        assert counts[name] == ANSWERS['E24'][name]
    assert_answer('E24', exit=4, verdict=verdict, reason=reason, candidate_rows=counts['candidate_rows'], index_probes=counts['index_probes'], merged_bindings=counts['merged_bindings'], total_work=counts['total_work'], partial_witness_suppressed=witnesses == ())

def test_e41_rejects_a_later_malformed_antecedent_binding(tmp_path: Path) -> None:
    adapted, constraint, names, bindings = _prepared(tmp_path, rows=1)
    short_row = tuple(bindings[0][:-1])
    null_cell_row = list(bindings[0])
    null_cell_row[names.index('$sample')] = None
    malformed_rows = (short_row, tuple(null_cell_row))
    for malformed_row in malformed_rows:
        result = _run(adapted, constraint, names, [tuple(bindings[0]), malformed_row], {})
        assert result == ('unchecked', 'malformed-constraint', ())
    assert_answer('E41', exit=0, verdict='unchecked', reason='malformed-constraint', malformed_binding_indices=[1, 1], malformed_binding_kinds=['wrong-length', 'non-scalar-cell'], uncaught_exception=False)

def test_e42_failed_term_work_counts_later_siblings() -> None:
    term = {'fn': 'add', 'args': [{'fn': 'mod', 'args': [1, 0]}, {'fn': 'mul', 'args': ['$pci', '$pci']}]}
    result = evaluate_term(term, {'pci': 8})
    assert not result.available
    assert result.reason == 'term:mod-zero'
    assert result.nodes == 7
    assert result.operations == 2
    assert result.max_value_bits > 0
    assert_answer('E42', exit=0, reason=result.reason, term_nodes=result.nodes, term_operations=result.operations, maximum_value_bits_positive=result.max_value_bits > 0, later_sibling_work_accounted=result.nodes == 7 and result.operations == 2)

def test_e43_failed_comparison_counts_both_evaluated_terms() -> None:
    comparison = compare_terms('=', {'fn': 'mul', 'args': ['$pci', '$pci']}, {'fn': 'mod', 'args': [1, 0]}, {'pci': 8})
    assert not comparison.available
    assert comparison.reason == 'term:mod-zero'
    assert comparison.nodes == 6
    assert comparison.operations == 2
    assert comparison.max_value_bits == 7
    assert_answer('E43', exit=0, reason=comparison.reason, term_nodes=comparison.nodes, term_operations=comparison.operations, maximum_value_bits=comparison.max_value_bits, left_term_work_accounted=comparison.nodes == 6 and comparison.operations == 2)
