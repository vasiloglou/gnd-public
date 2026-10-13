"""Exact, live exemptions for RF6-C1; no implicit package-wide bypasses."""
import ast
import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / '.gnd-planning/milestones/code-refactoring/evidence/RF9-repair/query-allow-list.json'
DYNAMIC_SUCCESSOR = ROOT / '.gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/dynamic-query-successor.json'


def effective_policy():
    from support.pyrel_application_successors import query_policy
    return query_policy(POLICY)


def reads(sources, *, include_subscriptions=True, include_literal_getattr=True):
    counts = Counter()
    for path, source in sources.items():
        if path == 'src/gnd/model.py' or path.startswith('src/gnd/model/') or path == 'src/gnd/model_index.py':
            continue
        tree = ast.parse(source)
        parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
        for node in ast.walk(tree):
            direct = isinstance(node, ast.Attribute) and node.attr == 'fact_types' and isinstance(node.ctx, ast.Load)
            getter = (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                      and node.func.attr == 'get' and node.args and isinstance(node.args[0], ast.Constant)
                      and node.args[0].value in ('fact_types', 'roles'))
            subscription = (isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Load)
                            and isinstance(node.slice, ast.Constant)
                            and node.slice.value in ('fact_types', 'roles'))
            literal_getattr = (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                               and node.func.id == 'getattr' and len(node.args) > 1
                               and isinstance(node.args[1], ast.Constant)
                               and node.args[1].value in ('fact_types', 'roles'))
            if (direct or getter or (include_subscriptions and subscription)
                    or (include_literal_getattr and literal_getattr)):
                owner = node
                while owner in parents and not isinstance(owner, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    owner = parents[owner]
                counts[(path, getattr(owner, 'name', '<module>'), ast.unparse(node))] += 1
    return counts


def sources():
    return {p.relative_to(ROOT).as_posix(): p.read_text() for p in (ROOT / 'src/gnd').rglob('*.py')}


def assert_policy(found, policy):
    approved = Counter()
    for row in policy['rows']:
        assert row['reason'] and row['count'] > 0
        key = row['path'], row['owner'], row['expression']
        assert key not in approved
        approved[key] = row['count']
    assert found == approved, (found - approved, approved - found)
    assert sum(found.values()) <= policy['ceiling'] < policy['baseline']


def test_exact_live_query_policy():
    assert_policy(reads(sources()), effective_policy())


@pytest.mark.parametrize('damage', ['new-read', 'missing-row', 'stale-row', 'extra-occurrence'])
def test_policy_rejects_each_direction(damage):
    policy = effective_policy()
    found = reads(sources())
    if damage == 'new-read':
        found.update(reads({'src/gnd/new.py': 'def new(model):\n    return model.fact_types\n'}))
    elif damage == 'missing-row':
        policy['rows'].pop()
    elif damage == 'stale-row':
        policy['rows'].append({'path': 'absent', 'owner': 'absent', 'expression': 'absent',
                               'count': 1, 'reason': 'dirty control'})
    else:
        found[next(iter(found))] += 1
    with pytest.raises(AssertionError):
        assert_policy(found, policy)


def test_literal_subscription_cannot_escape_direct_read_policy():
    policy = effective_policy()
    found = reads(sources())
    assert_policy(found, policy)
    found.update(reads({'src/gnd/injected.py': 'def injected(model):\n    return model["fact_types"]\n'}))
    with pytest.raises(AssertionError):
        assert_policy(found, policy)


def dynamic_reads(all_sources):
    """Syntax candidates only: no claim to resolve dynamic selector meanings."""
    counts = Counter()
    for path, source in all_sources.items():
        if path == 'src/gnd/model.py' or path.startswith('src/gnd/model/') or path == 'src/gnd/model_index.py':
            continue
        tree = ast.parse(source)
        parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
        for node in ast.walk(tree):
            candidate = (isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Load)
                         and not isinstance(node.slice, ast.Constant))
            if isinstance(node, ast.Call) and node.args:
                candidate |= (isinstance(node.func, ast.Attribute) and node.func.attr == 'get'
                              and not isinstance(node.args[0], ast.Constant))
                candidate |= (isinstance(node.func, ast.Name) and node.func.id == 'getattr'
                              and len(node.args) > 1 and not isinstance(node.args[1], ast.Constant))
            if candidate:
                owner = node
                while owner in parents and not isinstance(owner, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    owner = parents[owner]
                counts[(path, getattr(owner, 'name', '<module>'), ast.unparse(node))] += 1
    return counts


def assert_dynamic_inventory(found, rows):
    approved = Counter()
    for row in rows:
        assert len(row) == 4 and isinstance(row[3], int) and row[3] > 0
        key = tuple(row[:3])
        assert key not in approved
        approved[key] = row[3]
    assert found == approved


def successor_dynamic_rows(successor=None):
    """Apply an exact counted delta without rewriting historical RF9 evidence."""
    successor = json.loads(DYNAMIC_SUCCESSOR.read_text()) if successor is None else successor
    assert successor['schema_version'] == 1
    assert successor['reason']
    predecessor = POLICY.parent / 'dynamic-query-candidates.json'
    assert successor['predecessor'] == predecessor.relative_to(ROOT).as_posix()
    assert successor['predecessor_sha256'] == hashlib.sha256(predecessor.read_bytes()).hexdigest()

    def counted(rows):
        result = Counter()
        for row in rows:
            assert len(row) == 4 and type(row[3]) is int and row[3] > 0
            key = tuple(row[:3])
            assert all(isinstance(value, str) for value in key)
            assert key not in result
            result[key] = row[3]
        return result

    approved = counted(json.loads(predecessor.read_text())['rows'])
    removed, added = counted(successor['removed']), counted(successor['added'])
    assert not (removed.keys() & added.keys())
    for key, count in removed.items():
        assert approved[key] >= count
        approved[key] -= count
        if approved[key] == 0:
            del approved[key]
    approved.update(added)
    assert len(approved) == successor['result_distinct_rows']
    assert sum(approved.values()) == successor['result_occurrences']
    from support.pyrel_application_successors import dynamic_rows
    return dynamic_rows([list(key) + [count] for key, count in sorted(approved.items())], DYNAMIC_SUCCESSOR)


def test_dynamic_candidate_inventory_is_complete_and_live():
    rows = successor_dynamic_rows()
    found = dynamic_reads(sources())
    assert_dynamic_inventory(found, rows)
    found.update(dynamic_reads({'src/gnd/injected.py': 'def injected(model, key):\n    return model[key]\n'}))
    with pytest.raises(AssertionError):
        assert_dynamic_inventory(found, rows)


def test_original_query_metric_remains_below_its_original_target():
    policy = effective_policy()
    metric = policy['original_attribute_get_metric']
    count = sum(reads(sources(), include_subscriptions=False, include_literal_getattr=False).values())
    assert count == metric['current']
    assert count <= metric['ceiling'] < metric['baseline']
    assert (metric['ceiling'], metric['baseline']) == (310, 320)


def test_subscription_negative_refuses_reverted_scanner(monkeypatch):
    original = reads
    monkeypatch.setitem(globals(), 'reads', lambda source: original(source, include_subscriptions=False))
    with pytest.raises(AssertionError):
        test_literal_subscription_cannot_escape_direct_read_policy()


def test_dynamic_duplicate_inventory_row_is_refused():
    rows = successor_dynamic_rows()
    found = dynamic_reads(sources())
    assert_dynamic_inventory(found, rows)
    with pytest.raises(AssertionError):
        assert_dynamic_inventory(found, rows + [rows[0]])


@pytest.mark.parametrize('damage', ['duplicate-added', 'duplicate-removed', 'stale-predecessor',
                                   'missing-addition', 'extra-addition', 'invalid-removal'])
def test_dynamic_successor_rejects_inventory_damage(damage):
    successor = json.loads(DYNAMIC_SUCCESSOR.read_text())
    if damage == 'duplicate-added':
        successor['added'].append(successor['added'][0])
    elif damage == 'duplicate-removed':
        successor['removed'].append(successor['removed'][0])
    elif damage == 'stale-predecessor':
        successor['predecessor_sha256'] = '0' * 64
    elif damage == 'missing-addition':
        successor['added'].pop()
    elif damage == 'extra-addition':
        successor['added'].append(['src/gnd/absent.py', 'absent', 'absent[key]', 1])
    else:
        successor['removed'][0][3] += 100
    with pytest.raises(AssertionError):
        rows = successor_dynamic_rows(successor)
        assert_dynamic_inventory(dynamic_reads(sources()), rows)


def test_dynamic_live_successor_rejects_vanished_source_candidate():
    rows = successor_dynamic_rows()
    found = dynamic_reads(sources())
    added = json.loads(DYNAMIC_SUCCESSOR.read_text())['added'][0]
    key = tuple(added[:3])
    found[key] -= 1
    with pytest.raises(AssertionError):
        assert_dynamic_inventory(found, rows)
