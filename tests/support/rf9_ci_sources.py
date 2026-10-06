"""Named CI successors; historical evidence is immutable."""
import json
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parents[2] / '.gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair'


def coupling_sites(metrics):
    """Separate only exact inventoried compatibility aliases; unknown sites count."""
    from collections import Counter

    def key(row):
        return tuple(row.get(k) for k in ('from', 'to', 'name', 'kind'))
    aliases = Counter(key(row) for row in json.loads((EVIDENCE / 'compatibility-private-sites.json').read_text())['sites'])
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


def body_successor(kind, name, old=None):
    rows = json.loads((EVIDENCE / 'body-successors.json').read_text())
    found = [r for r in rows if r['kind'] == kind and r['name'] == name and (old is None or r.get('old') == old)]
    assert len(found) <= 1
    return found[0] if found else None
