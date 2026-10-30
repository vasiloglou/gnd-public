"""Authenticated phase deltas; historical source/query evidence stays immutable."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / '.gnd-planning/milestones/pyrel-applications/evidence'
PHASES = ['PA1', 'PA2', 'PA3', 'PA4', 'PA5R']
QUERY_SUCCESSORS = [
    ROOT / '.gnd-planning/milestones/incremental-evaluation/evidence/IE3/query-successor.json',
]


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
    paths = [EVIDENCE / phase / 'query-successor.json' for phase in PHASES] + QUERY_SUCCESSORS
    for path in paths:
        data = json.loads(path.read_text())
        assert data['schema_version'] == 1 and data['reason']
        assert data['predecessor'] == predecessor.relative_to(ROOT).as_posix()
        assert data['predecessor_sha256'] == hashlib.sha256(predecessor.read_bytes()).hexdigest()
        rows = [[r['path'], r['owner'], r['expression'], r['count']] for r in policy['rows']]
        reasons = {(r['path'], r['owner'], r['expression']): r['reason'] for r in policy['rows']}
        for row in data['added']:
            reasons[tuple(row[:3])] = data['reason']
        policy['rows'] = [dict(zip(['path', 'owner', 'expression', 'count'], row, strict=True),
                               reason=reasons[tuple(row[:3])]) for row in delta(rows, data)]
        policy['original_attribute_get_metric']['current'] = data['original_metric_current']
        predecessor = path
    return policy


#: Later authenticated dynamic-query deltas, outside the PyRel application phases.
DYNAMIC_SUCCESSORS = [
    ROOT / '.gnd-planning/maintenance/2026-10-17-main-ci-repair/dynamic-query-successor.json',
    ROOT / '.gnd-planning/milestones/incremental-evaluation/evidence/IE1/dynamic-query-successor.json',
    ROOT / '.gnd-planning/milestones/incremental-evaluation/evidence/IE2/dynamic-query-successor.json',
    ROOT / '.gnd-planning/milestones/incremental-evaluation/evidence/IE3/dynamic-query-successor.json',
    ROOT / '.gnd-planning/milestones/incremental-evaluation/evidence/IE4/dynamic-query-successor.json',
    ROOT / '.gnd-planning/milestones/incremental-evaluation/evidence/IE5/dynamic-query-successor.json',
    ROOT / '.gnd-planning/milestones/induced-knowledge/evidence/IK1/dynamic-query-successor.json',
    ROOT / '.gnd-planning/milestones/induced-knowledge/evidence/IK2/dynamic-query-successor.json',
    ROOT / '.gnd-planning/milestones/induced-knowledge/evidence/IK4/dynamic-query-successor.json',
    ROOT / '.gnd-planning/milestones/induced-knowledge/evidence/IK3/dynamic-query-successor.json',
    ROOT / '.gnd-planning/milestones/induced-knowledge/evidence/IK5/dynamic-query-successor.json',
    ROOT / '.gnd-planning/milestones/induced-knowledge/evidence/IK6/dynamic-query-successor.json',
    ROOT / '.gnd-planning/milestones/induced-knowledge/evidence/close/dynamic-query-successor.json',
    ROOT / '.gnd-planning/milestones/induced-knowledge/evidence/evolve-loading/dynamic-query-successor.json',
    ROOT / '.gnd-planning/maintenance/2026-10-27-carried-defects/dynamic-query-successor.json',
    ROOT / '.gnd-planning/milestones/ilp-learners/evidence/IL1/dynamic-query-successor.json',
    ROOT / '.gnd-planning/milestones/ilp-learners/evidence/IL2/dynamic-query-successor.json',
    ROOT / '.gnd-planning/milestones/ilp-learners/evidence/IL5/dynamic-query-successor.json',
    ROOT / '.gnd-planning/milestones/ilp-learners/evidence/IL3/dynamic-query-successor.json',
    ROOT / '.gnd-planning/milestones/ilp-learners/evidence/IL4/dynamic-query-successor.json',
    ROOT / '.gnd-planning/milestones/ilp-learners/evidence/IL-close/dynamic-query-successor.json',
    ROOT / '.gnd-planning/milestones/ilp-import-hardening/evidence/IH0/dynamic-query-successor.json',
    ROOT / '.gnd-planning/milestones/ilp-import-hardening/evidence/IH1/dynamic-query-successor.json',
    ROOT / '.gnd-planning/milestones/ilp-import-hardening/evidence/IH2/dynamic-query-successor.json',
]


def dynamic_rows(rows, predecessor):
    for phase in PHASES:
        rows = delta(rows, authenticated('dynamic-query-successor.json', predecessor, phase))
        predecessor = EVIDENCE / phase / 'dynamic-query-successor.json'
    for path in DYNAMIC_SUCCESSORS:
        data = json.loads(path.read_text())
        assert data['schema_version'] == 1 and data['reason']
        assert data['predecessor'] == predecessor.relative_to(ROOT).as_posix()
        assert data['predecessor_sha256'] == hashlib.sha256(predecessor.read_bytes()).hexdigest()
        rows = delta(rows, data)
        predecessor = path
    return rows


def rendered_bytes(expected, predecessor):
    for phase in PHASES:
        data = authenticated('pyrel-successor.json', predecessor, phase)
        assert data['before'] == expected
        expected = data['after']
        predecessor = EVIDENCE / phase / 'pyrel-successor.json'
    return expected
