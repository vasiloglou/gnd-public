"""Full reference corpus byte integrity and known-dirty controls."""
from __future__ import annotations

import atexit
import gzip
import hashlib
import io
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

import pytest


def _materialize_public_corpus():
    packed = (Path(__file__).parent / "fixtures/public-v71-reference-integrity/closure.json.gz").read_bytes()
    assert len(packed) <= 16384
    assert hashlib.sha256(packed).hexdigest() == "16dd02519df086123e76b4b1630c4e5283567df6c605e423c640a7b6accde424"
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(262145)
    assert len(raw) <= 262144
    assert hashlib.sha256(raw).hexdigest() == "544f40567ad95657b40f1ea5529c5ad6381f7eca4a62329ffcd97423356d9344"
    documents = json.loads(raw)
    assert set(documents) == {'dispatch/model.orm.yaml', 'release/model.orm.yaml', 'dispatch/references/catalog.pop.json', 'README.md', 'release/candidate.pop.json', 'inputs.json', 'answers.json', 'release/references/catalog.pop.json', 'manifest.json', 'dispatch/candidate.pop.json'}
    temporary = tempfile.TemporaryDirectory(prefix="gnd-public-reference-integrity-")
    root = Path(temporary.name).resolve()
    for name, text in documents.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return temporary, root

_TEMPORARY, CORPUS = _materialize_public_corpus()
atexit.register(_TEMPORARY.cleanup)

def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _bytes(doc: Any) -> bytes:
    return (json.dumps(doc, ensure_ascii=False, separators=(",", ":")) + "\n").encode()


def _write_json(path: Path, doc: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_bytes(doc))


def _audit_corpus(root: Path = CORPUS) -> None:
    manifest = json.loads((root / "manifest.json").read_text())
    actual = {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and p.name != "manifest.json"
    }
    assert set(manifest["files"]) == actual
    for name, expected in manifest["files"].items():
        data = (root / name).read_bytes()
        assert len(data) == expected["bytes"] and _digest(data) == expected["sha256"]
    inputs = json.loads((root / "inputs.json").read_text())["cases"]
    answers = json.loads((root / "answers.json").read_text())["cases"]
    ids = [row["id"] for row in inputs]
    assert len(ids) == len(set(ids))
    assert set(ids) == {row["id"] for row in answers}
    assert len(answers) == len(ids)
    for domain in ("dispatch", "release"):
        assert {r["branch"] for r in inputs if r["domain"] == domain} == {
            f"B{x:02d}" for x in range(1, 25)
        }
    assert all(r["scenario"] and r["story"] for r in inputs)


def test_phase2_corpus_manifest() -> None:
    _audit_corpus()


@pytest.mark.parametrize("mutation", ["input", "answer", "inventory"])
def test_phase2_corpus_dirty_control(tmp_path: Path, mutation: str) -> None:
    copied = tmp_path / "copied"
    shutil.copytree(CORPUS, copied)
    if mutation == "input":
        (copied / "inputs.json").write_text("{}\n")
    elif mutation == "answer":
        doc = json.loads((copied / "answers.json").read_text())
        doc["cases"][0]["exit_code"] = 3
        _write_json(copied / "answers.json", doc)
    else:
        (copied / "unregistered.json").write_text("{}\n")
    with pytest.raises(AssertionError):
        _audit_corpus(copied)

