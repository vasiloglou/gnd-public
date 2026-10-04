from __future__ import annotations

from pathlib import Path

import pytest

from gnd import checker
from gnd.checker import (
    CheckReport,
    ConstraintVerdict,
    DerivationFinding,
    DerivationVerdict,
    _evaluate_derivations,
    band,
)
from gnd.model import load_model
from gnd.population import load_population

REPO_ROOT = Path(__file__).resolve().parents[1]

def _constraint_verdict(verdict: str) -> ConstraintVerdict:
    return ConstraintVerdict(scope_id=f'composition:oracle-verdict:n-a:{verdict}', constraint_ref='constraints[0]', constraint_type='guarded', modality='alethic', source='explicit', status='confirmed', verdict=verdict, message='fixture')

def _pass_derivation() -> DerivationVerdict:
    return DerivationVerdict(derivation_ref='derivation:result', fact_type='result', derivation='derived', verdict='pass', message='fixture', scope_id='derivation:extension:derived:clean')

def _fail_derivation() -> DerivationVerdict:
    return DerivationVerdict(derivation_ref='derivation:result', fact_type='result', derivation='derived', verdict='fail', message='fixture', findings=[DerivationFinding(kind='derived-extension-incomplete', message='fixture', witness={'item': 'alpha'})], scope_id='derivation:extension:derived:violated:alethic')

def _unchecked_derivation() -> DerivationVerdict:
    return DerivationVerdict(derivation_ref='derivation:result', fact_type='result', derivation='derived', verdict='unchecked', message='fixture', reason_code='derivation-not-covered', scope_id='derivation:extension:derived:unchecked-not-covered')

def test_derivation_literals_are_closed() -> None:
    assert set(checker.DERIVATION_REASON_CODES) == {'derivation-not-covered', 'derivation-rule-opaque', 'opaque-value', 'derived-unknown'}
    assert DerivationFinding.model_fields['kind'].annotation == checker.DerivationKind
    with pytest.raises(ValueError, match='pass derivations'):
        DerivationVerdict(derivation_ref='derivation:result', fact_type='result', derivation='derived', verdict='pass', message='bad', reason_code='derivation-not-covered', scope_id='derivation:extension:derived:clean')
    with pytest.raises(ValueError, match='canonically ordered'):
        DerivationVerdict(derivation_ref='derivation:result', fact_type='result', derivation='derived', verdict='fail', message='bad', findings=[DerivationFinding(kind='derived-extension-unsound', message='bad', witness={}), DerivationFinding(kind='derived-extension-incomplete', message='bad', witness={})], scope_id='derivation:extension:derived:violated:alethic')

def test_identity_codec_vectors() -> None:
    assert checker._identity_token('λ') == b'["string","' + 'λ'.encode() + b'"]'
    assert checker._identity_token(1) == b'["number",[1,1]]'
    assert checker._identity_token(1.0) == b'["number",[1,1]]'
    assert checker._identity_token(-0.0) == b'["number",[0,1]]'
    assert checker._identity_token(True) == b'["boolean",true]'
    assert checker._identity_token(True) != checker._identity_token(1)

def test_normative_reference_no_longer_denies_structured_evaluation() -> None:
    reference = (REPO_ROOT / 'src/gnd/skills/gnd-orm-core/references/representation-format.md').read_text(encoding='utf-8')
    assert 'nothing in this version EVALUATES a derived extension' not in reference

@pytest.mark.parametrize(('report', 'expected'), [(CheckReport(derivations=[_pass_derivation()]), 0), (CheckReport(derivations=[_fail_derivation()]), 1), (CheckReport(derivations=[_fail_derivation(), _unchecked_derivation()]), 1), (CheckReport(verdicts=[_constraint_verdict('vacuous')], derivations=[_unchecked_derivation()]), 4), (CheckReport(verdicts=[_constraint_verdict('vacuous')]), 2)], ids=['0', '1', '1-over-4', '4-over-2', '2'])
def test_band_boundaries(report: CheckReport, expected: int) -> None:
    assert band(report) == expected

def test_semiderived_surplus_cannot_feed_upper(tmp_path: Path) -> None:
    model_path = tmp_path / 'model.orm.yaml'
    population_path = tmp_path / 'population.yaml'
    model_path.write_text('version: 1\nmodel_id: urn:gnd-test:semiderived-upper@1\nsource: {kind: text-conversation, confidence: standard, mode: one-shot}\nobject_types:\n  - {id: item, name: Item, kind: value, primitive: String}\nfact_types:\n  - id: seed\n    reading: "{Item} is seeded"\n    roles: [{object_type: item, role_name: item}]\n  - id: semi\n    reading: "{Item} is partly derived"\n    roles: [{object_type: item, role_name: item}]\n    derivation: semiderived\n    derivation_rule:\n      body: [{fact_type: seed, bind: {item: "$i"}}]\n      head: {item: "$i"}\n  - id: upper\n    reading: "{Item} is upper derived"\n    roles: [{object_type: item, role_name: item}]\n    derivation: derived\n    derivation_rule:\n      body: [{fact_type: semi, bind: {item: "$i"}}]\n      head: {item: "$i"}\nconstraints: []\nrejected_proposals: []\n', encoding='utf-8')
    population_path.write_text('population:\n  model: model.orm.yaml\n  model_id: urn:gnd-test:semiderived-upper@1\n  source: fixture\n  covers: [seed, semi, upper]\ninstances: {}\nfacts:\n  seed: []\n  semi: [{item: surplus}]\n  upper: [{item: surplus}]\n', encoding='utf-8')
    model = load_model(model_path)
    population = load_population(population_path, model=model)
    extensions, verdicts = _evaluate_derivations(model, population)
    assert extensions['semi'].rows == extensions['upper'].rows == ()
    assert [row.verdict for row in verdicts] == ['pass', 'fail']
    assert verdicts[1].findings[0].kind == 'derived-extension-unsound'
