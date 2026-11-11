"""Named CI successors; historical evidence is immutable."""
import hashlib
import json
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parents[2] / '.gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair'
SOURCE_SUCCESSORS = EVIDENCE.parents[2] / 'compiled-snapshot-obligations/evidence/CI/source-successors.json'
RETIRED_NAMES = SOURCE_SUCCESSORS.parent / 'retired-names.json'
PHASE_SUCCESSORS = (
    Path(__file__).resolve().parents[2] / '.gnd-planning/milestones/model-composition/evidence/MC1/source-successors.json',
    Path(__file__).resolve().parents[2] / '.gnd-planning/milestones/model-composition/evidence/MC2/source-successors.json',
    Path(__file__).resolve().parents[2] / '.gnd-planning/milestones/release-0.3.0/evidence/RN0/source-successors.json',
)


def retired_names(path=RETIRED_NAMES):
    """Owner-approved retired (module, name) pairs; a listed name still bound fails."""
    import importlib

    document = json.loads(path.read_text())
    assert document['schema_version'] == 1 and document['reason']
    rows = document['retired']
    keys = [(row['module'], row['name']) for row in rows]
    assert len(set(keys)) == len(keys), 'duplicate retired name'
    for row in rows:
        assert row['home'] and row['issue'] and row['phase'] and row['ruling'], row
        for module in (row['module'], row['home']):
            assert not hasattr(importlib.import_module(module), row['name']), (
                f"retired name still bound: {module}.{row['name']}")
    return frozenset(keys)


def coupling_sites(metrics):
    """Separate only exact inventoried compatibility aliases; unknown sites count."""
    from collections import Counter

    def key(row):
        return tuple(row.get(k) for k in ('from', 'to', 'name', 'kind'))
    retired = retired_names()
    aliases = Counter(key(row) for row in json.loads((EVIDENCE / 'compatibility-private-sites.json').read_text())['sites']
                      if (row['from'], row['name']) not in retired)
    import ast

    root = EVIDENCE.parents[4]
    explicit = set()
    for module in {identity[0] for identity in aliases}:
        path = root / ('src/' + module.replace('.', '/') + '.py')
        if not path.is_file():
            path = path.with_suffix('') / '__init__.py'
        for node in ast.parse(path.read_bytes()).body:
            if isinstance(node, ast.ImportFrom) and node.level == 0:
                explicit.update((module, node.module, a.name, 'from_import') for a in node.names
                                if a.name == a.asname)
    assert set(aliases) <= explicit, set(aliases) - explicit
    actual = Counter(key(row) for row in metrics['private_imports'])
    assert not aliases - actual, aliases - actual
    remaining = []
    for row in metrics['private_imports']:
        identity = key(row)
        if aliases[identity]:
            aliases[identity] -= 1
        else:
            remaining.append(row)
    return remaining


def _unique(rows, predicate):
    found = [row for row in rows if predicate(row)]
    assert len(found) <= 1
    return found[0] if found else None


def _current_rows():
    """One row per identity; a later change to the same body appends a chained row.

    Rows sharing an identity must follow each other in file order (each one's
    before equals the previous one's after, same home); they collapse to one
    row spanning the first before to the last after, keeping the last reason.
    """
    document = json.loads(SOURCE_SUCCESSORS.read_text())
    assert document['schema_version'] == 1
    rows = document['successors']
    root = Path(__file__).resolve().parents[2]
    for path in PHASE_SUCCESSORS:
        phase = json.loads(path.read_text())
        assert phase['schema_version'] == 1 and phase['reason']
        assert phase['predecessor'] == '.gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/source-successors.json'
        assert hashlib.sha256((root / phase['predecessor']).read_bytes()).hexdigest() == phase['predecessor_sha256']
        rows = [*rows, *phase['successors']]
    assert all(row['kind'] in {'RF4', 'RF5', 'RF6b'} and row['reason'] and row['home']
               for row in rows)
    collapsed = {}
    for row in rows:
        identity = (row['kind'], row.get('old', row.get('module')), row['name'])
        previous = collapsed.get(identity)
        if previous is not None:
            assert row['home'] == previous['home'] and row['before'] == previous['after'], (
                'duplicate current source successor')
            row = {**row, 'before': previous['before']}
        collapsed[identity] = row
    return list(collapsed.values())


def body_successor(kind, name, old=None):
    def match(row):
        return row['kind'] == kind and row['name'] == name and (old is None or row.get('old') == old)

    frozen = _unique(json.loads((EVIDENCE / 'body-successors.json').read_text()), match)
    current = _unique(_current_rows(), match)
    if frozen is not None and current is not None:
        assert current['home'] == frozen['home']
        assert current['before'] == frozen['after'], 'unchained body successor'
        return {**current, 'before': frozen['before']}
    return current if current is not None else frozen


def definition_successor(module, name):
    frozen = _unique(json.loads((EVIDENCE.parent / 'RF7/definition-successors.json').read_text()),
                     lambda row: (row['module'], row['name']) == (module, name))
    current = _unique(_current_rows(), lambda row: row['kind'] == 'RF6b'
                      and (row['module'], row['name']) == (module, name))
    if frozen is not None and current is not None:
        assert current['home'] == frozen['home']
        assert current['before'] == frozen['after'], 'unchained definition successor'
        return {**current, 'before': frozen['before']}
    return current if current is not None else frozen
