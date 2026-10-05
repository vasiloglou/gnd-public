"""Concrete current checker observations; no formal correspondence claim."""
import json

import pytest
from support import public_snapshot_counterexamples as corpus

from gnd import checker
from gnd.model import ModelValidationError, load_model
from gnd.population import load_population

CASES = {"cases": corpus.DOCUMENT["cases"]}
EXPECTED = corpus.DOCUMENT["answers"]

@pytest.mark.parametrize('case', [row for row in CASES['cases'] if row['kind'] == 'snapshot'], ids=lambda row: row['id'])
def test_source_review_snapshot_observations(case, tmp_path):
    model_doc, population_doc = corpus._documents(case['base'])
    model_doc = corpus._apply(model_doc, case.get('model_patch', []))
    population_doc = corpus._apply(population_doc, case.get('population_patch', []))
    model_path, population_path = (tmp_path / 'model.orm.yaml', tmp_path / 'population.json')
    model_path.write_text(json.dumps(model_doc))
    population_path.write_text(json.dumps(population_doc))
    expected = EXPECTED[case['id']]
    if case.get('load_refused'):
        with pytest.raises(ModelValidationError):
            load_model(model_path)
        assert corpus._observe(case['base'], tmp_path)['reason_code'] == expected['defensive_reason']
        return
    model = load_model(model_path)
    population = load_population(population_path, model=model)
    report = checker.check(model, population)
    verdict = next(row for row in report.verdicts if row.constraint_ref == corpus.BUILD_BY_ID[case['base']]['ref'])
    observed = expected
    assert verdict.verdict == observed['verdict']
    assert verdict.reason_code == observed['reason_code']
    actual = [item if isinstance(item, (dict, list)) else [item] for item in verdict.offending_facts]
    assert actual == observed['public_witness']
    if 'band' in expected:
        assert checker.band(report) == expected['band']
    if 'aggregate_witness' in expected:
        assert [[member] for member in expected['aggregate_witness'][0]] == actual
