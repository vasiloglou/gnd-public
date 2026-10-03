from __future__ import annotations

from support.v62_phase5_corpus import document, population_path

from gnd.checker import band, check
from gnd.model import Model
from gnd.population import load_population


def _report(name: str):
    model = Model.model_validate(document())
    population = load_population(population_path(name), model=model)
    return (model, check(model, population))

def test_e01_e06_d01_clean_population_checks_clean_with_exact_values() -> None:
    _, report = _report('clean')
    assert band(report) == 0
    rows = {row.fact_type: row for row in report.derivations}
    assert rows['sample_rate_kbps'].verdict == 'pass'
    assert rows['sample_margin_sqrt'].verdict == 'pass'
    assert rows['sample_rate_floor'].verdict == 'pass'
    assert rows['sample_rate_ceil'].verdict == 'pass'
    assert rows['sample_serving_distance_km'].verdict == 'pass'
    assert rows['sample_handover_close'].verdict == 'pass'
    assert rows['scenario_avg_rb'].verdict == 'pass'
    assert all(v.verdict == 'pass' for v in report.verdicts)

def test_k17_a_float_only_rule_routes_through_the_exact_calculator() -> None:
    _, report = _report('clean')
    row = next(r for r in report.derivations if r.fact_type == 'sample_serving_distance_km')
    assert row.verdict == 'pass'

def test_u01_u02_u05_div_zero_and_sqrt_negative_are_relation_level_unavailable() -> None:
    _, report = _report('div_margin_undefined')
    assert band(report) == 4
    rows = {row.fact_type: row for row in report.derivations}
    assert rows['sample_rate_kbps'].verdict == 'unchecked'
    assert 'term:div-zero' in rows['sample_rate_kbps'].message
    assert rows['sample_rate_kbps'].reason_code == 'term:div-zero'
    assert rows['sample_rate_floor'].verdict == 'unchecked'
    assert rows['sample_rate_ceil'].verdict == 'unchecked'
    assert rows['sample_margin_sqrt'].verdict == 'unchecked'
    assert 'term:sqrt-negative' in rows['sample_margin_sqrt'].message
    assert rows['sample_margin_sqrt_doubled'].verdict == 'unchecked'
    constraint = report.verdicts[0]
    assert constraint.verdict == 'unchecked'
    assert constraint.reason_code == 'term:div-zero'
    assert 'term:div-zero' in constraint.message

def test_u03_u04_haversine_coordinate_range_both_axes() -> None:
    for name in ('lat_undefined', 'lon_undefined'):
        _, report = _report(name)
        assert band(report) == 4
        rows = {row.fact_type: row for row in report.derivations}
        assert rows['sample_serving_distance_km'].verdict == 'unchecked'
        assert 'term:haversine-coordinate-range' in rows['sample_serving_distance_km'].message
        assert rows['sample_handover_close'].verdict == 'unchecked'
        assert 'term:haversine-coordinate-range' in rows['sample_handover_close'].message
