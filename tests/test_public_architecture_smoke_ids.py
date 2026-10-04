from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path

import pytest

from gnd.architecture import load_architecture_contract

_ARCHIVE = Path(__file__).parent / "fixtures/public-architecture-smoke-ids/contracts.json.gz"

@pytest.fixture(autouse=True)
def _committed_contract_subjects(tmp_path, monkeypatch):
    packed = _ARCHIVE.read_bytes()
    assert len(packed) <= 65536
    assert hashlib.sha256(packed).hexdigest() == '103388c76d8244ebf6dfd1566180133448f4426ca124b84503783bb52c8db99e'
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(65537)
    assert len(raw) <= 65536
    assert hashlib.sha256(raw).hexdigest() == 'dffba8f09ff54ff6a2d6c4bd72dca68e05f8e95560aac80a86ef8d4dbc74f764'
    documents = json.loads(raw)
    assert set(documents) == {"examples/expense-tracker/project/architecture.contract.yaml", "examples/bookrec/project/architecture.contract.yaml"}
    for relative, text in documents.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    monkeypatch.setitem(globals(), "__file__", str(tmp_path / "tests/test_public_architecture_smoke_ids.py"))

def test_every_committed_example_contract_survives_the_smoke_id_rule() -> None:
    """P4-33, the real-seam half. A synthetic id passing proves the rule admits a
    string; this proves it admits the two contracts this repository ships."""
    repo_root = Path(__file__).resolve().parents[1]
    contracts = [
        repo_root / "examples" / "expense-tracker" / "project",
        repo_root / "examples" / "bookrec" / "project",
    ]

    for project in contracts:
        loaded = load_architecture_contract(project)
        assert loaded.smoke, f"{project.name} declares no smoke row to protect"
        for row in loaded.smoke:
            assert not any(c in "[]" or c.isspace() for c in row.id), (project.name, row.id)

