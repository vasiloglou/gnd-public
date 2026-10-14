"""Authenticated phase deltas; historical source/query evidence stays immutable."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / '.gnd-planning/milestones/pyrel-applications/evidence'
PHASES = ['PA1', 'PA2', 'PA3', 'PA4', 'PA5R']


def authenticated(name, predecessor, phase):
    data = json.loads((EVIDENCE / phase / name).read_text())
    assert data['schema_version'] == 1 and data['reason']
    assert data['predecessor'] == predecessor.relative_to(ROOT).as_posix()
    assert data['predecessor_sha256'] == hashlib.sha256(predecessor.read_bytes()).hexdigest()
    return data


def delta(rows, data):
    def counted(values):
        result = Counter()
        for row in values:
            assert len(row) == 4 and type(row[3]) is int and row[3] > 0
            key = tuple(row[:3])
            assert all(isinstance(value, str) for value in key) and key not in result
            result[key] = row[3]
        return result
    result = counted(rows)
    removed, added = counted(data['removed']), counted(data['added'])
    assert not (removed.keys() & added.keys())
    for key, count in removed.items():
        assert result[key] >= count
        result[key] -= count
        if not result[key]:
            del result[key]
    result.update(added)
    assert len(result) == data['result_distinct_rows']
    assert sum(result.values()) == data['result_occurrences']
    return [list(key) + [count] for key, count in sorted(result.items())]


def query_policy(predecessor):
    policy = json.loads(predecessor.read_text())
    for phase in PHASES:
        data = authenticated('query-successor.json', predecessor, phase)
        rows = [[r['path'], r['owner'], r['expression'], r['count']] for r in policy['rows']]
        reasons = {(r['path'], r['owner'], r['expression']): r['reason'] for r in policy['rows']}
        for row in data['added']:
            reasons[tuple(row[:3])] = data['reason']
        policy['rows'] = [dict(zip(['path', 'owner', 'expression', 'count'], row, strict=True),
                               reason=reasons[tuple(row[:3])]) for row in delta(rows, data)]
        policy['original_attribute_get_metric']['current'] = data['original_metric_current']
        predecessor = EVIDENCE / phase / 'query-successor.json'
    return policy


def dynamic_rows(rows, predecessor):
    for phase in PHASES:
        rows = delta(rows, authenticated('dynamic-query-successor.json', predecessor, phase))
        predecessor = EVIDENCE / phase / 'dynamic-query-successor.json'
    return rows


def rendered_bytes(expected, predecessor):
    for phase in PHASES:
        data = authenticated('pyrel-successor.json', predecessor, phase)
        assert data['before'] == expected
        expected = data['after']
        predecessor = EVIDENCE / phase / 'pyrel-successor.json'
    return expected
