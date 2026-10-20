"""IE5 measurement preparation: balanced modes and complete typed oracle."""
from tests.test_incremental_baseline import tool


def test_session_timing_uses_balanced_uninstrumented_distinct_modes(monkeypatch):
    reached = []

    def replay(workload, *, receipts, incremental=False):
        reached.append((receipts, incremental))
        return []

    monkeypatch.setattr(tool, 'replay_full', replay)
    result = tool.measure_session_modes('localized', repeat=3)
    assert result['order'] == ['ABC', 'BCA', 'CAB']
    assert result['positionally_balanced']
    assert all(len(rows) == 3 for rows in result['samples'].values())
    assert reached[3:] == [(False, False), (True, False), (True, True),
                           (True, False), (True, True), (False, False),
                           (True, True), (False, False), (True, False)]


def test_complete_calculation_key_rejects_typed_metadata_mutation():
    from dataclasses import replace

    from gnd import extensions

    m, p = next(tool.localized_inputs())
    original = extensions._python_extension_calculator(m, extensions.base_relations(m, p))
    key = tool.complete_calculation_key(original)
    relation = original.extensions['left_copy']
    changed = dict(original.extensions)
    changed['left_copy'] = replace(relation, roles=tuple(reversed(relation.roles)) + ('wrong',))
    assert key != tool.complete_calculation_key(replace(original, extensions=changed))
