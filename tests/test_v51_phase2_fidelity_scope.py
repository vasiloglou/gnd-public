from __future__ import annotations

from gnd.extract.refscheme import applicable_set
from gnd.extraction_scope import STRUCTURED_DERIVATION_INAPPLICABLE_REASON
from gnd.model import Model


def test_structured_scope_precedes_unmatchable_reference_identity() -> None:
    model = Model(version=1, object_types=[{'id': 'mass', 'kind': 'entity', 'reference': {'mode': 'unit-based', 'unit': 'kg', 'measure_type': 'decimal'}}], fact_types=[{'id': 'derived_mass', 'roles': [{'object_type': 'mass', 'role_name': 'mass'}], 'derivation_rule': {'kind': 'structured'}}])
    row = applicable_set(model)['fact_types'][0]
    assert row == {'id': 'derived_mass', 'applicable': False, 'reason': STRUCTURED_DERIVATION_INAPPLICABLE_REASON}

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def test_matcher_and_report_do_not_reimplement_structured_scope() -> None:
    for relative in ('src/gnd/fidelity/match.py', 'src/gnd/fidelity/report.py'):
        source = (REPO_ROOT / relative).read_text(encoding='utf-8')
        assert 'structured_derivation_ids' not in source
        assert 'STRUCTURED_DERIVATION_INAPPLICABLE_REASON' not in source
