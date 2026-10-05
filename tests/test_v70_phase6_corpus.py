from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path

import pytest

from gnd import api
from gnd.artifacts import canonical_json_bytes
from gnd.extract.anchors import vocabulary_digest
from gnd.model import load_model
from gnd.population import load_population_bytes

FIXTURE = Path(__file__).parent / "fixtures/v70-phase6"

CASES = json.loads((FIXTURE / "cases.json").read_text(encoding="utf-8"))

ANSWERS = json.loads((FIXTURE / "answers.json").read_text(encoding="utf-8"))

CASE_IDS = (
    "R01-range-provided",
    "N01-negation-provided",
    "V01-vocabulary-refused",
    "S01-other-model-boundary",
    "S02-structured-synth-refused",
)

def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def test_models_populations_and_baseline_bands_are_valid() -> None:
    for left, right, names in (
        ("range-a", "range-b", ("range-a.pop.json", "range-b-boundary.pop.json")),
        ("negation-a", "negation-b", (
            "negation-blocked.pop.json", "negation-opaque.pop.json", "negation-waived.pop.json",
        )),
    ):
        model_a, model_b = (load_model(FIXTURE / f"{stem}.orm.yaml") for stem in (left, right))
        assert vocabulary_digest(model_a) == vocabulary_digest(model_b)
        for name in names:
            raw = (FIXTURE / name).read_bytes()
            for model in (model_a, model_b):
                assert load_population_bytes(raw, source=FIXTURE / name, model=model)
    assert vocabulary_digest(load_model(FIXTURE / "range-a.orm.yaml")) != vocabulary_digest(
        load_model(FIXTURE / "negation-a.orm.yaml")
    )
    for case_id, bands in (
        ("R01-range-provided", ((0, 0), (1, 0))),
        ("N01-negation-provided", ((1, 0), (4, 0), (0, 1))),
    ):
        case = next(row for row in CASES["cases"] if row["id"] == case_id)
        for name, expected in zip(case["populations"], bands, strict=True):
            observed = tuple(
                api.check(FIXTURE / case[key], FIXTURE / name, admission=True)["exit_code"]
                for key in ("model_a", "model_b")
            )
            assert observed == expected

@pytest.mark.parametrize("case_id", CASE_IDS[:2])
def test_provided_report_is_red_until_diff_exists(case_id: str) -> None:
    module = importlib.import_module("gnd.diff")
    case = next(row for row in CASES["cases"] if row["id"] == case_id)
    report = module.diff_models(
        load_model(FIXTURE / case["model_a"]), load_model(FIXTURE / case["model_b"]),
        populations=tuple((name, (FIXTURE / name).read_bytes()) for name in case["populations"]),
        synthesize=False, seed=0,
    )
    expected = ANSWERS["cases"][case_id]
    assert report == expected["report"]
    assert _sha(canonical_json_bytes(report)) == expected["report_sha256"]

def test_vocabulary_refusal_is_red_until_diff_exists() -> None:
    module = importlib.import_module("gnd.diff")
    case = CASES["cases"][2]
    with pytest.raises(module.DiffError, match=ANSWERS["cases"][case["id"]]["error_rule"]):
        module.diff_models(
            load_model(FIXTURE / case["model_a"]), load_model(FIXTURE / case["model_b"]),
            synthesize=False,
        )

def test_other_model_boundary_is_red_until_diff_exists() -> None:
    module = importlib.import_module("gnd.diff")
    case = CASES["cases"][3]
    answer = ANSWERS["cases"][case["id"]]
    report = module.diff_models(
        load_model(FIXTURE / case["model_a"]), load_model(FIXTURE / case["model_b"]),
        synthesize=True, seed=0,
    )
    assert any(
        row["origin"] == answer["required_origin"]
        and row[answer["source_model"]]["band"] == answer["source_band"]
        and row[answer["target_model"]]["band"] == answer["target_band"]
        and any(gap["target_ref"] == answer["target_ref"] for gap in row["b_to_a"])
        for row in report["populations"]
    )

def test_structured_synth_refusal_is_red_until_diff_exists() -> None:
    module = importlib.import_module("gnd.diff")
    case = CASES["cases"][4]
    answer = ANSWERS["cases"][case["id"]]
    report = module.diff_models(
        load_model(FIXTURE / case["model_a"]), load_model(FIXTURE / case["model_b"]),
        synthesize=True, seed=0,
    )
    assert sorted(row["source"] for row in report["not_derivable"]) == answer["not_derivable_sources"]
    assert all(answer["reason_contains"] in row["reason"] for row in report["not_derivable"])

import copy

ANSWERS["file_sha256"] = json.loads((FIXTURE / "public-input-sha256.json").read_text())

EXPECTED_EXITS = dict.fromkeys(CASE_IDS, 0) | {'V01-vocabulary-refused': 3}

REF0 = 'fact_types[invoice_amount].constraints[0]'

REF1 = 'fact_types[invoice_amount].constraints[1]'

def verify_answer_key(cases: dict, answers: dict) -> None:
    """Assert independent case meanings plus byte-bound proposed reports."""
    assert cases['schema_version'] == answers['schema_version'] == 1
    rows = cases['cases']
    assert tuple(row['id'] for row in rows) == CASE_IDS
    assert set(answers['cases']) == set(CASE_IDS)
    assert {name: answers['cases'][name]['exit'] for name in CASE_IDS} == EXPECTED_EXITS
    names = {path.name for path in FIXTURE.iterdir() if path.is_file() and path.name not in {'answers.json', 'public-input-sha256.json'}}
    assert set(answers['file_sha256']) == names
    for name in names:
        assert answers['file_sha256'][name] == _sha((FIXTURE / name).read_bytes())
    by_id = {row['id']: row for row in rows}
    assert by_id['R01-range-provided']['populations'] == ['range-a.pop.json', 'range-b-boundary.pop.json']
    assert by_id['N01-negation-provided']['populations'] == ['negation-blocked.pop.json', 'negation-opaque.pop.json', 'negation-waived.pop.json']
    assert by_id['V01-vocabulary-refused']['model_b'] == 'negation-a.orm.yaml'
    assert not by_id['R01-range-provided']['synthesize']
    assert not by_id['N01-negation-provided']['synthesize']
    assert by_id['S01-other-model-boundary']['synthesize']
    assert by_id['S02-structured-synth-refused']['synthesize']
    for case_id in CASE_IDS[:2]:
        answer = answers['cases'][case_id]
        report = answer['report']
        assert answer['report_sha256'] == _sha(canonical_json_bytes(report))
        assert report['schema_version'] == 'gnd-diff/1'
        assert report['command'] == 'diff'
        assert report['assurance'] == 'none'
        assert report['seed'] == 0
        assert report['not_derivable'] == []
        assert 'SECRET-OPAQUE-CANARY' not in canonical_json_bytes(report).decode()
    range_report = answers['cases']['R01-range-provided']['report']
    assert len(range_report['entailment']) == 4
    assert {tuple(row[key] for key in ('from_model', 'to_model', 'family', 'result')) for row in range_report['entailment']} == {('a', 'b', 'uniqueness', 'implies'), ('b', 'a', 'uniqueness', 'undecided'), ('a', 'b', 'value', 'implies'), ('b', 'a', 'value', 'undecided')}
    assert all(row['left_ref'] == row['right_ref'] for row in range_report['entailment'])
    range_pops = range_report['populations']
    assert [(row['a']['band'], row['b']['band']) for row in range_pops] == [(0, 0), (1, 0)]
    assert range_pops[1]['a_to_b'] == []
    assert range_pops[1]['b_to_a'] == [{'target_ref': REF1, 'verdict': 'fail', 'offending_facts': [21], 'witness_sentence': None}]
    neg_report = answers['cases']['N01-negation-provided']['report']
    assert neg_report['entailment'] == []
    neg_pops = neg_report['populations']
    assert [(row['a']['band'], row['b']['band']) for row in neg_pops] == [(1, 0), (4, 0), (0, 1)]
    assert [(row['derivations'][0]['a_status'], row['derivations'][0]['b_status']) for row in neg_pops] == [('out', 'in'), ('unknown', 'in'), ('in', 'out')]
    assert [bool(row['a_to_b']) for row in neg_pops] == [False, False, True]
    assert [bool(row['b_to_a']) for row in neg_pops] == [True, True, False]
    assert neg_pops[1]['derivations'][0]['outcome'] == 'unresolved'
    assert answers['cases']['V01-vocabulary-refused']['before_synthesis'] is True
    assert answers['cases']['S01-other-model-boundary']['target_band'] == 1
    assert answers['cases']['S02-structured-synth-refused']['not_derivable_sources'] == ['a', 'b']

def test_answer_key_is_bound_and_discriminating() -> None:
    verify_answer_key(CASES, ANSWERS)

def test_known_dirty_answer_is_rejected() -> None:
    dirty = copy.deepcopy(ANSWERS)
    dirty['cases']['R01-range-provided']['report']['entailment'][0]['from_model'] = 'b'
    with pytest.raises(AssertionError):
        verify_answer_key(CASES, dirty)
    dirty = copy.deepcopy(ANSWERS)
    dirty['cases']['N01-negation-provided']['report']['populations'][1]['a']['band'] = 0
    with pytest.raises(AssertionError):
        verify_answer_key(CASES, dirty)
    dirty = copy.deepcopy(ANSWERS)
    dirty['cases']['V01-vocabulary-refused']['exit'] = 0
    with pytest.raises(AssertionError):
        verify_answer_key(CASES, dirty)
    dirty = copy.deepcopy(ANSWERS)
    dirty['cases']['N01-negation-provided']['report']['populations'][1]['b_to_a'][0]['witness_sentence'] = 'SECRET-OPAQUE-CANARY'
    with pytest.raises(AssertionError):
        verify_answer_key(CASES, dirty)

def test_known_dirty_input_is_rejected() -> None:
    dirty = copy.deepcopy(CASES)
    dirty['cases'][0]['populations'][0] = 'negation-blocked.pop.json'
    with pytest.raises(AssertionError):
        verify_answer_key(dirty, ANSWERS)
    dirty = copy.deepcopy(ANSWERS)
    dirty['file_sha256']['range-a.orm.yaml'] = '0' * 64
    with pytest.raises(AssertionError):
        verify_answer_key(CASES, dirty)
