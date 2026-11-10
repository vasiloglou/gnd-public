"""Documentation integration controls; runtime semantics remain MC3's contract."""
import copy
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from gnd.evolve import EvolutionError, EvolutionService, read_evolution_proposal_document


def test_byte_and_path_only_repin_still_requires_acceptance(tmp_path):
    source = Path(__file__).resolve().parents[1] / 'src/gnd/examples/expense/teams'
    work = tmp_path / 'teams'
    shutil.copytree(source, work)
    old = work / 'shared/expense-v1.orm.json'
    alternate = work / 'shared/expense-v1-reformatted.orm.json'
    alternate.write_bytes(old.read_bytes() + b'\n')
    authored = json.loads((work / 'sales.orm.json').read_text())
    proposal = json.loads((work / 'sales-repin.proposal.json').read_text())
    new_pin = copy.deepcopy(authored['includes'][0])
    new_pin.update(path='shared/expense-v1-reformatted.orm.json',
                   sha256=hashlib.sha256(alternate.read_bytes()).hexdigest())
    authored['includes'] = [new_pin]
    text = json.dumps(authored, indent=2) + '\n'
    proposal['candidate_model'].update(text=text, sha256=hashlib.sha256(text.encode()).hexdigest())
    proposal['operations'][0]['after'] = new_pin
    service = EvolutionService(model_path=work / 'sales.orm.json', evidence_root=work / 'records',
                               allowed_project_root=work)
    parsed = read_evolution_proposal_document(proposal)
    preview = service.preview(parsed)
    assert preview.breaking is True and preview.accepted_blast_radius_sha256 is None
    with pytest.raises(EvolutionError, match="explicit acceptance"):
        service.apply(preview)
    accepted = service.preview(parsed, accepted_blast_radius_sha256=preview.blast_radius.report_sha256)
    assert accepted.accepted_blast_radius_sha256 == preview.blast_radius.report_sha256
    assert old.read_bytes() == (source / 'shared/expense-v1.orm.json').read_bytes()


def test_retained_entry_points_link_current_source():
    root = Path(__file__).resolve().parents[1] / 'docs'
    for name in ['how-to/share-a-vocabulary.md', 'tutorials/shared-component-vocabulary.md']:
        text = (root / name).read_text()
        assert 'tree/main/src/gnd/examples/expense/teams' in text
        assert 'codex/model-composition-docs-draft' not in text
