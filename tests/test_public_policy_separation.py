from __future__ import annotations

from gnd.assurance import _assurance_policy, assurance_prerequisites


def test_infrastructure_cannot_supply_its_own_result_coverage():
    required = frozenset(assurance_prerequisites('snapshot', 'report'))
    assert _assurance_policy(required, required, required=required, proved_infrastructure=required, guards_valid=True) == 'none'
