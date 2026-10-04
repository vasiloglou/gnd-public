"""Original temporary corpus materializer and patch proposal helpers only."""
from __future__ import annotations

import atexit
import copy
import gzip
import hashlib
import io
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

import pytest

from gnd.artifacts import canonical_json_bytes
from gnd.exp.session_contract import DataDrivenContract
from gnd.exp.session_store import SessionStore
from tests.support import v71_session_cases as public_session_helper


def _materialize():
    packed = (Path(__file__).parent / "fixtures/public-v72-session-staging/closure.json.gz").read_bytes()
    assert len(packed) <= 8192
    assert hashlib.sha256(packed).hexdigest() == "07cc89197814c63bfed796c42e6035f0c1816d74e182cd882b438a7ef2e8d278"
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(65537)
    assert len(raw) <= 65536
    assert hashlib.sha256(raw).hexdigest() == "ed86e1e932dcc48316674d37c1e7633e1a01970d809a8e4a58a2b478a2ff2d6f"
    documents = json.loads(raw)
    assert set(documents) == {'tests/fixtures/v71/phase4/dispatch/legacy-no-request-wire.json', 'tests/fixtures/v71/phase4/release/owned-model.orm.yaml', 'tests/fixtures/v71/phase4/release/contract-v7.json', 'domains.json', 'tests/fixtures/v71/phase4/release/legacy-v10-wire.json', 'tests/fixtures/v71/phase4/release/candidate.pop.json', 'tests/fixtures/v71/phase4/dispatch/contract-v7.json', 'tests/fixtures/v71/phase4/dispatch/reference-model.orm.yaml', 'tests/fixtures/v71/phase4/release/legacy-no-request-wire.json', 'tests/fixtures/v71/phase4/release/reference-model.orm.yaml', 'tests/fixtures/v71/phase4/dispatch/owned-model.orm.yaml', 'tests/fixtures/v71/phase4/dispatch/model.orm.yaml', 'tests/fixtures/v71/phase4/dispatch/legacy-v10-wire.json', 'tests/fixtures/v71/phase4/release/references/catalog.pop.json', 'tests/fixtures/v71/phase4/dispatch/candidate.pop.json', 'tests/fixtures/v71/phase4/release/model.orm.yaml', 'tests/fixtures/v71/phase4/dispatch/references/catalog.pop.json'}
    temporary = tempfile.TemporaryDirectory(prefix="gnd-public-v72-session-staging-")
    root = Path(temporary.name).resolve()
    for name, text in documents.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return temporary, root, json.loads(documents["domains.json"])

_TEMPORARY, ROOT, INPUTS = _materialize()
CORPUS = ROOT / "tests/fixtures/v71/phase4"
atexit.register(_TEMPORARY.cleanup)

def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))

def bundle(domain: str, root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    source = CORPUS / domain
    shutil.copytree(source, root, dirs_exist_ok=True)
    return {
        "root": root,
        "ids": copy.deepcopy(INPUTS["domains"][domain]),
        "model": json.loads((source / "model.orm.yaml").read_text()),
        "population": json.loads((source / "candidate.pop.json").read_text()),
        "contract": json.loads((source / "contract-v7.json").read_text()),
    }

def patch_contract(b: dict) -> DataDrivenContract:
    doc = copy.deepcopy(b["contract"])
    doc["candidate_edits"] = {
        "patch_path": ".gnd-patch.json",
        "artifacts": b["ids"]["artifacts"],
    }
    return DataDrivenContract.model_validate(doc)

def base_files(b: dict) -> tuple[Path, str, dict[str, bytes]]:
    base = b["root"] / "base"
    base.mkdir(exist_ok=True)
    (base / "candidate.pop.json").write_bytes(canonical_json_bytes(b["population"]))
    write_json(base / "notes.json", {"note": "unchanged"})
    write_json(base / "kept.json", {"keep": True})
    store = SessionStore(b["root"] / "store", run_id="corpus")
    digest = store.inventory_candidate(base).tree_sha256
    return base, digest, {p.name: p.read_bytes() for p in base.iterdir()}

def proposal(b: dict, operations: list[dict], digest: str | None) -> dict:
    ops = copy.deepcopy(operations)
    for op in ops:
        if op["op"] != "replace-artifact":
            op.setdefault("artifact", "candidate.pop.json")
            op.setdefault("collection", ["facts", b["ids"]["fact"]])
    return {"schema_version": 1, "base_candidate_sha256": digest, "operations": ops}

@pytest.fixture(autouse=True)
def _exact_session_materializer(monkeypatch):
    for name in ("write_json", "bundle", "patch_contract", "base_files", "proposal"):
        monkeypatch.setattr(public_session_helper, name, globals()[name])
