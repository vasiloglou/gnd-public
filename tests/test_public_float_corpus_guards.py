from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML as RuamelYAML
from support.v62_phase5_corpus import CASES_DOC, FIXTURE, document, population_path

from gnd.checker import check
from gnd.model import Model, semantic_validate
from gnd.population import load_population
from gnd.transition import band, evaluate, model_digest, operations_digest

YAML = RuamelYAML(typ="safe")

CASES_DOC = {**CASES_DOC, "steps": "walks/flag.steps.json"}


def test_walk_digests_bind_the_future_loaded_model_bytes() -> None:
    model = Model.model_validate(document())
    walk = json.loads((FIXTURE / CASES_DOC['steps']).read_text(encoding='utf-8'))
    assert walk['model_digest'] == model_digest(model)
    assert walk['operations_digest'] == operations_digest(model.operations)

def test_canonical_and_vendored_schemas_still_match() -> None:
    root = Path(__file__).resolve().parents[1]
    canonical = (root / 'src/gnd/schema/orm-meta.schema.json').read_bytes()
    vendored = (root / 'src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json').read_bytes()
    assert canonical == vendored

def test_story_model_validates_cleanly() -> None:
    assert semantic_validate(document()) == []

def test_g01_bare_avg_head_still_refused_while_round_wrapped_is_accepted() -> None:
    mutated = copy.deepcopy(document())
    for fact_type in mutated['fact_types']:
        if fact_type['id'] == 'scenario_avg_rb':
            fact_type['derivation_rule']['head']['mean_rb'] = '$mean'
    issues = {issue.rule_id for issue in semantic_validate(mutated)}
    assert 'semantic:aggregate-head-needs-round' in issues

def test_q01_unquantized_float_head_refused_at_validate() -> None:
    mutated = copy.deepcopy(document())
    for fact_type in mutated['fact_types']:
        if fact_type['id'] == 'sample_serving_distance_km':
            fact_type['derivation_rule']['head']['distance_km'] = fact_type['derivation_rule']['head']['distance_km']['args'][0]
    issues = {issue.rule_id for issue in semantic_validate(mutated)}
    assert 'semantic:derivation-float-head-unquantized' in issues

def test_clean_population_checks_clean_and_matches_every_claim() -> None:
    model = Model.model_validate(document())
    population = load_population(population_path('clean'), model=model)
    report = check(model, population)
    assert report.derivations, 'expected at least one derivation verdict'
    assert all(row.verdict == 'pass' for row in report.derivations)
    assert all(v.verdict == 'pass' for v in report.verdicts)

def test_div_margin_undefined_population_reports_named_reasons() -> None:
    model = Model.model_validate(document())
    population = load_population(population_path('div_margin_undefined'), model=model)
    report = check(model, population)
    reasons = {row.fact_type: row.message for row in report.derivations}
    assert 'term:div-zero' in reasons['sample_rate_kbps']
    assert 'term:sqrt-negative' in reasons['sample_margin_sqrt']
    constraint_messages = ' '.join(v.message for v in report.verdicts)
    assert 'term:div-zero' in constraint_messages
    assert all(row.verdict == 'unchecked' for row in report.derivations)

def test_lat_and_lon_undefined_populations_report_coordinate_range() -> None:
    model = Model.model_validate(document())
    for name in ('lat_undefined', 'lon_undefined'):
        population = load_population(population_path(name), model=model)
        report = check(model, population)
        distance_row = next(row for row in report.derivations if row.fact_type == 'sample_serving_distance_km')
        assert 'term:haversine-coordinate-range' in distance_row.message


def population_document(name: str='clean') -> dict[str, Any]:
    path = CASES_DOC['populations'][name]
    return copy.deepcopy(YAML.load((FIXTURE / path).read_text(encoding='utf-8')))


def test_d01_flag_close_handover_walk_accepts_only_the_close_ue() -> None:
    model = Model.model_validate(document())
    pre_doc = population_document('clean')
    pre = load_population_from_doc(pre_doc, model)
    post_doc = copy.deepcopy(pre_doc)
    assert 'handover_flag' in post_doc['population']['covers']
    post_doc['facts']['handover_flag'] = [{'ue': 'ue1'}]
    post = load_population_from_doc(post_doc, model)
    walk = json.loads((FIXTURE / CASES_DOC['steps']).read_text(encoding='utf-8'))
    report = evaluate(model, pre, post, walk['steps'])
    assert band(report) == 0
    assert all(v.verdict == 'pass' for v in report.frame_verdicts)

def load_population_from_doc(doc: dict, model: Model):
    import tempfile
    from pathlib import Path

    from ruamel.yaml import YAML
    writer = YAML(typ='safe')
    writer.default_flow_style = False
    tmp_path = Path(tempfile.mktemp(suffix='.pop.yaml'))
    with open(tmp_path, 'w') as handle:
        writer.dump(doc, handle)
    return load_population(tmp_path, model=model)
