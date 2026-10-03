from __future__ import annotations

import json
from pathlib import Path

from gnd.exp.session_eval import (
    DERIVATION_FEEDBACK_SCHEMA_VERSION,
    FEEDBACK_SCHEMA_VERSION,
    DerivationFeedback,
)

CORPUS = Path(__file__).parent / 'fixtures/phase3-consumers'
ANSWER = json.loads((CORPUS / 'answers/feedback-derivation-rows.json').read_text(encoding='utf-8'))
import pytest

from gnd.exp.session_eval import derivation_feedback_rows


def test_an_unchecked_verdict_becomes_one_row_with_reason_and_no_kind() -> None:
    rows = derivation_feedback_rows([{'derivation_ref': 'derivation:book_is_eligible', 'derivation': 'derived', 'modality': 'alethic', 'verdict': 'unchecked', 'message': 'not covered', 'findings': [], 'reason_code': 'derivation-not-covered'}])
    row, = rows
    assert row.kind is None
    assert row.reason_code == 'derivation-not-covered'
    assert row.witness is None

def test_the_projector_is_total_over_malformed_rows() -> None:
    with pytest.raises(ValueError, match='not closed repair rows'):
        derivation_feedback_rows([{}])
    with pytest.raises(ValueError, match='not closed repair rows'):
        derivation_feedback_rows([{'derivation_ref': 'derivation:x', 'verdict': 'fail', 'findings': [{'kind': 'derived-extension-unsound', 'message': 'm', 'witness': None}]}])

def _payload(name: str) -> dict:
    return json.loads((CORPUS / name).read_text(encoding='utf-8'))

def _dumped(rows: tuple[DerivationFeedback, ...]) -> list[dict]:
    return [row.model_dump(mode='json') for row in rows]

def test_the_derivation_feedback_wire_is_version_three() -> None:
    assert DERIVATION_FEEDBACK_SCHEMA_VERSION == ANSWER['schema_version'] == 3
    assert FEEDBACK_SCHEMA_VERSION == 2

def test_a_pass_verdict_contributes_no_feedback_row() -> None:
    rows = derivation_feedback_rows(_payload('check-v4.exact.payload.json')['derivations'])
    assert _dumped(rows) == ANSWER['exact'] == []

def test_an_incomplete_finding_becomes_one_row_with_address_and_witness() -> None:
    rows = derivation_feedback_rows(_payload('check-v4.incomplete.payload.json')['derivations'])
    assert _dumped(rows) == ANSWER['incomplete']
    row, = rows
    assert row.derivation_ref == 'derivation:book_is_eligible'
    assert row.kind == 'derived-extension-incomplete'
    assert row.witness == {'book': 'alpha'}
    assert row.reason_code is None

def test_feedback_rows_carry_the_counterexample_and_nothing_more() -> None:
    rows = derivation_feedback_rows(_payload('check-v4.incomplete.payload.json')['derivations'])
    encoded = json.dumps(_dumped(rows), sort_keys=True)
    payload = _payload('check-v4.incomplete.payload.json')
    for verdict in payload['derivations']:
        for finding in verdict['findings']:
            assert json.dumps(finding['witness'], sort_keys=True)[1:-1] in encoded
    assert 'computed' not in encoded
