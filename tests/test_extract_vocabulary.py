from __future__ import annotations

import copy
import io
from pathlib import Path

from ruamel.yaml import YAML

from gnd.extract.vocabulary import render_verbalization
from gnd.model import load_model

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).parent / 'fixtures'
FULL_VOCAB = FIXTURES / 'models' / 'full_vocabulary.orm.yaml'

def _is_derived_and_unedited(path: Path) -> bool:
    import hashlib
    import json
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    intent_candidates = (path.parent / 'intent.json', *sorted(path.parent.glob('records/*/intent.json')))
    for intent_path in intent_candidates:
        if not intent_path.is_file():
            continue
        try:
            intent = json.loads(intent_path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            continue
        if intent.get('verbalization_sha256') == digest:
            return True

    def _recorded_digest(manifest: dict, relpath: str) -> str | None:
        for entry in manifest.get('files', []):
            if entry.get('relpath') == relpath:
                if entry.get('ownership') != 'derived':
                    return None
                return entry.get('sha256')
        artifacts = manifest.get('artifacts')
        if isinstance(artifacts, dict):
            entry = artifacts.get(relpath)
            if isinstance(entry, dict):
                return entry.get('sha256')
        return None
    for ancestor in path.parents:
        for manifest_name in ('.gnd-codegen.json', 'model.artifacts.json'):
            manifest_path = ancestor / manifest_name
            if not manifest_path.is_file():
                continue
            try:
                manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            except (OSError, ValueError):
                return False
            recorded = _recorded_digest(manifest, path.relative_to(ancestor).as_posix())
            if recorded is None:
                return False
            return recorded == hashlib.sha256(path.read_bytes()).hexdigest()
        if ancestor == REPO_ROOT:
            return False
    return False

def _injected(constraint_type: str, **fields: object) -> dict[str, object]:
    base: dict[str, object] = {'type': constraint_type, 'source': 'explicit', 'status': 'confirmed', 'modality': 'alethic', 'provenance': {'user_quote': 'injected for the constraint-blindness mutation check'}}
    base.update(fields)
    return base

def test_vocabulary_is_constraint_blind(tmp_path: Path) -> None:
    yaml = YAML(typ='safe')
    doc = yaml.load(FULL_VOCAB.read_text(encoding='utf-8'))
    baseline = render_verbalization(load_model(str(FULL_VOCAB)))
    mutated = copy.deepcopy(doc)
    fact_types = {str(ft['id']): ft for ft in mutated['fact_types']}
    fact_types['assignment_has_overtime_hours'].setdefault('constraints', []).append(_injected('uniqueness', roles=['assignment']))
    fact_types['employee_has_gender']['constraints'].append(_injected('mandatory', role='employee'))
    fact_types['employee_reports_to_employee']['constraints'].append(_injected('ring', variant='intransitive'))
    fact_types['employee_works_on_project']['constraints'].append(_injected('frequency', scope='internal', roles=['employee'], bound={'max': 9}))
    mutated['constraints'].append(_injected('value', object_type='hours', range={'min': 5, 'max': 10}))
    mutated_path = tmp_path / 'mutated_full_vocabulary.orm.yaml'
    buffer = io.StringIO()
    yaml.dump(mutated, buffer)
    mutated_path.write_text(buffer.getvalue(), encoding='utf-8')
    rerendered = render_verbalization(load_model(str(mutated_path)))
    assert rerendered.encode('utf-8') == baseline.encode('utf-8'), 'Assertion did not hold.'

def test_the_evolution_record_exemption_requires_an_exact_adjacent_digest(tmp_path) -> None:
    import hashlib
    import json
    record_dir = tmp_path / 'p001'
    record_dir.mkdir()
    candidate = record_dir / 'candidate.verbalization.txt'
    candidate.write_text('mechanical rendering\n', encoding='utf-8')
    (record_dir / 'intent.json').write_text(json.dumps({'verbalization_sha256': hashlib.sha256(candidate.read_bytes()).hexdigest()}), encoding='utf-8')
    assert _is_derived_and_unedited(candidate)
    candidate.write_text('mechanical rendering, then edited\n', encoding='utf-8')
    assert not _is_derived_and_unedited(candidate)
    tracker = tmp_path / 'tracker'
    (tracker / 'records' / 'p001').mkdir(parents=True)
    live = tracker / 'model.verbalization.txt'
    live.write_text('mechanical rendering\n', encoding='utf-8')
    (tracker / 'records' / 'p001' / 'intent.json').write_text(json.dumps({'verbalization_sha256': hashlib.sha256(live.read_bytes()).hexdigest()}), encoding='utf-8')
    assert _is_derived_and_unedited(live)
    stray = tmp_path / 'stray.verbalization.txt'
    stray.write_text('mechanical rendering\n', encoding='utf-8')
    assert not _is_derived_and_unedited(stray)

def test_the_derived_exemption_catches_a_hand_edited_generated_verbalization(tmp_path) -> None:
    import hashlib
    import json
    root = tmp_path / 'proj'
    (root / 'artifacts').mkdir(parents=True)
    derived = root / 'artifacts' / 'x.verbalization.txt'
    derived.write_text('=== Object Types ===\n', encoding='utf-8')
    hand = root / 'artifacts' / 'hand.verbalization.txt'
    hand.write_text('written by a person\n', encoding='utf-8')

    def write_manifest(ownership: str) -> None:
        (root / '.gnd-codegen.json').write_text(json.dumps({'manifest_version': 1, 'files': [{'relpath': 'artifacts/x.verbalization.txt', 'sha256': hashlib.sha256(derived.read_bytes()).hexdigest(), 'ownership': ownership}]}), encoding='utf-8')
    write_manifest('derived')
    assert _is_derived_and_unedited(derived), 'Assertion did not hold.'
    assert not _is_derived_and_unedited(hand), 'Assertion did not hold.'
    write_manifest('extension')
    assert not _is_derived_and_unedited(derived), 'Assertion did not hold.'
    write_manifest('derived')
    derived.write_text('=== Object Types ===\n# edited by hand\n', encoding='utf-8')
    assert not _is_derived_and_unedited(derived), 'Assertion did not hold.'
    (root / '.gnd-codegen.json').unlink()
    assert not _is_derived_and_unedited(hand), 'Assertion did not hold.'
