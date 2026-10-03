from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from gnd import api

CORPUS = Path(__file__).parent / 'fixtures/v71/phase2'
INPUTS = {'domains': {'dispatch': {'subject': 'shipment', 'left': 'warehouse', 'right': 'product', 'a': 'dispatch_subject_warehouse', 'b': 'dispatch_subject_product', 'catalog': 'dispatch_catalog_allows', 'extra': 'dispatch_catalog_label', 'rule': 'dispatch_catalog_membership', 'object_subject': 'dispatch_shipment', 'object_left': 'dispatch_warehouse', 'object_right': 'dispatch_product', 'left_value': 'WH-A', 'right_value': 'GEAR-2', 'subject_value': 'SHIP-17'}}}

def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def _bytes(doc: Any) -> bytes:
    return (json.dumps(doc, ensure_ascii=False, separators=(',', ':')) + '\n').encode()

def _write_json(path: Path, doc: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_bytes(doc))

def _bundle(domain: str, root: Path) -> dict[str, Any]:
    shutil.copytree(CORPUS / domain, root)
    return {'root': root, 'ids': INPUTS['domains'][domain], 'model': YAML(typ='safe').load((root / 'model.orm.yaml').read_text()), 'candidate': json.loads((root / 'candidate.pop.json').read_bytes()), 'catalog': json.loads((root / 'references/catalog.pop.json').read_bytes())}

def _save(b: dict[str, Any], *, rehash: bool=True) -> None:
    root = b['root']
    _write_json(root / 'candidate.pop.json', b['candidate'])
    _write_json(root / 'references/catalog.pop.json', b['catalog'])
    if rehash:
        for declaration in b['model'].get('reference_populations', []):
            path = root / declaration.get('path', 'references/catalog.pop.json')
            if path.is_file() and (not path.is_symlink()):
                declaration['sha256'] = _digest(path.read_bytes())
    with (root / 'model.orm.yaml').open('w') as stream:
        YAML().dump(b['model'], stream)

def _reference_budget_report(tmp_path):
    bundle = _bundle('dispatch', tmp_path / 'dispatch')
    ids = bundle['ids']
    size = 225
    left = [f'W{i}' for i in range(size)]
    right = [f'P{i}' for i in range(size)]
    bundle['candidate']['facts'][ids['a']] = [{ids['subject']: 'S', ids['left']: value} for value in left]
    bundle['candidate']['facts'][ids['b']] = [{ids['subject']: 'S', ids['right']: value} for value in right]
    bundle['catalog']['facts'][ids['catalog']] = [{ids['left']: a, ids['right']: b} for a in left for b in right]
    _save(bundle)
    report = api.check(bundle['root'] / 'model.orm.yaml', bundle['root'] / 'candidate.pop.json')
    return report

def test_exists_consequent_shares_antecedent_join_ceiling(tmp_path):
    report = _reference_budget_report(tmp_path)
    assert report['exit_code'] == 4
    assert any(row['reason_code'] == 'reference-join-work-limit' for row in report['report']['verdicts'])
