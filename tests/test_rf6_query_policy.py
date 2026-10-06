"""Exact, live exemptions for RF6-C1; no implicit package-wide bypasses."""
import ast
import json
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / '.gnd-planning/milestones/code-refactoring/evidence/RF6/query-allow-list.json'


def reads(sources, *, include_subscriptions=True):
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
            if direct or getter or (include_subscriptions and subscription):
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
    assert_policy(reads(sources()), json.loads(POLICY.read_text()))


@pytest.mark.parametrize('damage', ['new-read', 'missing-row', 'stale-row', 'extra-occurrence'])
def test_policy_rejects_each_direction(damage):
    policy = json.loads(POLICY.read_text())
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
    policy = json.loads(POLICY.read_text())
    found = reads(sources())
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
    assert found == Counter({tuple(row[:3]): row[3] for row in rows})


def test_dynamic_candidate_inventory_is_complete_and_live():
    rows = json.loads((POLICY.parent / 'dynamic-query-candidates.json').read_text())['rows']
    found = dynamic_reads(sources())
    assert_dynamic_inventory(found, rows)
    found.update(dynamic_reads({'src/gnd/injected.py': 'def injected(model, key):\n    return model[key]\n'}))
    with pytest.raises(AssertionError):
        assert_dynamic_inventory(found, rows)


def test_original_query_metric_remains_below_its_original_target():
    policy = json.loads(POLICY.read_text())
    metric = policy['original_attribute_get_metric']
    count = sum(reads(sources(), include_subscriptions=False).values())
    assert count == metric['current']
    assert count <= metric['ceiling'] < metric['baseline']
    assert (metric['ceiling'], metric['baseline']) == (310, 320)
