"""Reviewed complete generic semantic-owner fixtures, pinned and bounded."""
import atexit
import gzip
import hashlib
import io
import json
import tempfile
from pathlib import Path

import pytest

from tests.support import v71_witness_cases as witness_helper


def _materialize():
    packed = (Path(__file__).parent / "fixtures/public-v72-semantic-owners/closure.json.gz").read_bytes()
    assert len(packed) <= 16384
    assert hashlib.sha256(packed).hexdigest() == "5c2dbddbf5e3c2b7996500a51f3a87c3665dea650e4f6bb9ec57263a25aade53"
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(131073)
    assert len(raw) <= 131072
    assert hashlib.sha256(raw).hexdigest() == "050063848165d84906108effccf4c1c6c7a0e3be2b7a7eaf4c0e85b9dfec3847"
    documents = json.loads(raw)
    assert set(documents) == {'.gnd-planning/milestones/v7.2/evidence/phase-6/baseline-before-r2.json', '.gnd-planning/milestones/v7.2/evidence/phase-6/inventory.py', 'domains.json', 'tests/fixtures/v71/phase3/release/recursive.witness.json', 'tests/fixtures/v71/phase3/release/model.orm.yaml', 'tests/fixtures/v71/phase3/release/targets.json', 'tests/fixtures/v71/phase3/release/candidate.pop.json', '.gnd-planning/milestones/v7.2/evidence/phase-6/refresh-before.json', 'tests/fixtures/v72/phase6/inputs.json', 'tests/fixtures/v72/phase6/answers.json', '.gnd-planning/milestones/v7.2/evidence/phase-6/dense-before.json', '.gnd-planning/milestones/v7.2/evidence/phase-6/characterize.py', 'tests/fixtures/v71/phase3/release/references/links.pop.json'}
    temporary = tempfile.TemporaryDirectory(prefix="gnd-public-v72-semantic-owners-")
    root = Path(temporary.name).resolve()
    for name, text in documents.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for name, digest in {'tests/fixtures/v70-phase2/model.orm.yaml': '543f0c024980f2d119db542e0839b5b6009f40d6e157d8f31481769a651b6b55', 'tests/fixtures/v71/phase3/dispatch/model.orm.yaml': '30f4bb81917960230bae6e25bae64173d05437bce85760c413a39b34bb455564', 'tests/fixtures/v71/phase3/dispatch/candidate.pop.json': '37283b94b0537b4aa87da5a56cf25518c08e34fa863ba71116fff6ac07707dd8', 'tests/fixtures/v71/phase3/dispatch/references/links.pop.json': 'b725da445dbf93befd7a465eb047ae4b5268fe4dcbf658069a07f2c3ea55a8e9', 'tests/fixtures/v71/phase3/dispatch/recursive.witness.json': '1ca91b038312cb4944f876d19a117966f388bd5c4bef74ef75104371b6428e1f', 'tests/fixtures/v71/phase3/dispatch/targets.json': '8f6e9e290ebbef4668602dec1a29d0f1462112a474ca0649176f4e4c494ff954'}.items():
        raw_member = (Path(witness_helper.ROOT) / name).read_bytes()
        assert hashlib.sha256(raw_member).hexdigest() == digest
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw_member)
    return temporary, root

_TEMPORARY, ROOT = _materialize()
atexit.register(_TEMPORARY.cleanup)

@pytest.fixture(autouse=True)
def _complete_witness_domains(monkeypatch):
    monkeypatch.setattr(witness_helper, "CORPUS", ROOT / "tests/fixtures/v71/phase3")
    monkeypatch.setattr(witness_helper, "INPUTS", json.loads((ROOT / "domains.json").read_text()))
