"""Exact legacy reader/refusal guards with public generic schema1/2 graph subjects."""
from __future__ import annotations

import atexit
import gzip
import hashlib
import io
import json
import tempfile
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError
from test_model_evolution import _additive_operations, _case, _proposal, _service, _tree_sha256


def _materialize_public_legacy():
    packed = (Path(__file__).parent / "fixtures/public-legacy-readers/closure.json.gz").read_bytes()
    assert len(packed) <= 65536
    assert hashlib.sha256(packed).hexdigest() == '99ae1dd097ca617a26366c4116cf38c9a639827e8f8a1c332a933e8b07d8aff8'
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(131073)
    assert len(raw) <= 131072
    assert hashlib.sha256(raw).hexdigest() == '0b6357e91a84789e0735fa8dc360785c25c027b8df12dde3aa40092affe681b5'
    documents = json.loads(raw)
    assert set(documents) == {'current-conformance.json', 'legacy-preview.json', 'legacy-conformance.json', 'legacy-record.json'}
    temporary = tempfile.TemporaryDirectory(prefix="gnd-public-legacy-readers-")
    root = Path(temporary.name).resolve()
    for name, text in documents.items():
        (root / name).write_text(text, encoding="utf-8")
    clean = json.loads((root / "legacy-conformance.json").read_bytes())["payload"]
    (root / "clean-payload.json").write_text(json.dumps(clean,ensure_ascii=False),encoding="utf-8")
    return temporary, root

_TEMPORARY, _ROOT = _materialize_public_legacy()
atexit.register(_TEMPORARY.cleanup)
RETAINED_CONFORMANCE = _ROOT / "current-conformance.json"
RETAINED_RECORD = _ROOT / "current-record.json"
RETAINED_PREVIEW = _ROOT / "current-preview.json"
CLEAN_CONFORMANCE_PAYLOAD = _ROOT / "clean-payload.json"


def _pre_migration_document(path: Path) -> dict[str, Any]:
    # Public-owned compatibility fixtures replace source-private git coordinates.
    # Exact original tests exercise the same version-dispatched document shapes;
    # no claim is made about the source commit or its expense-tracker lineage.
    names = {RETAINED_RECORD:"legacy-record.json", RETAINED_CONFORMANCE:"legacy-conformance.json", RETAINED_PREVIEW:"legacy-preview.json"}
    return json.loads((_ROOT / names[path]).read_text(encoding="utf-8"))


def _legacy_clean_record_documents() -> tuple[dict[str, Any], dict[str, Any]]:
    from gnd.evolve import canonical_sha256, conformance_payload_sha256

    conformance = _pre_migration_document(RETAINED_CONFORMANCE)
    conformance["payload"] = json.loads(
        CLEAN_CONFORMANCE_PAYLOAD.read_text(encoding="utf-8")
    )
    conformance["payload_sha256"] = conformance_payload_sha256(conformance["payload"])
    conformance["exit_code"] = 0

    record = _pre_migration_document(RETAINED_RECORD)
    record["linked_conformance"] = [conformance]
    record["conformance_exit_code"] = 0
    record["published_with_drift"] = False
    record["record_identity_sha256"] = canonical_sha256(
        {key: value for key, value in record.items() if key != "record_identity_sha256"}
    )
    return record, conformance

def test_v1_conformance_leaf_raises_through_v2_reader() -> None:
    from gnd.evolve import read_linked_project_conformance_document

    before = RETAINED_CONFORMANCE.read_bytes()
    document = _pre_migration_document(RETAINED_CONFORMANCE)

    with pytest.raises(ValidationError):
        read_linked_project_conformance_document(document, envelope_version=2)
    with pytest.raises(ValidationError):
        read_linked_project_conformance_document(document, envelope_version=0)

    assert RETAINED_CONFORMANCE.read_bytes() == before

def test_v1_record_and_conformance_load_through_v1_readers_at_exit_zero(
    tmp_path: Path,
) -> None:
    from gnd.artifacts import canonical_json_bytes
    from gnd.evolve import (
        read_evolution_record,
        read_evolution_record_document,
        read_linked_project_conformance,
        read_linked_project_conformance_document,
    )

    record_document, conformance_document = _legacy_clean_record_documents()
    record_path = tmp_path / "record.json"
    conformance_path = tmp_path / "conformance" / "project.json"
    conformance_path.parent.mkdir()
    record_path.write_bytes(canonical_json_bytes(record_document))
    conformance_path.write_bytes(canonical_json_bytes(conformance_document))
    before = {path: path.read_bytes() for path in (record_path, conformance_path)}

    record = read_evolution_record_document(record_document)
    conformance = read_linked_project_conformance_document(
        conformance_document, envelope_version=1
    )
    assert read_evolution_record(record_path) == record
    assert read_linked_project_conformance(conformance_path, envelope_version=1) == conformance
    assert record.schema_version == 1
    assert record.conformance_exit_code == 0
    assert conformance.exit_code == 0
    assert conformance.root

    missing_root = {key: value for key, value in conformance_document.items() if key != "root"}
    with pytest.raises(ValidationError):
        read_linked_project_conformance_document(missing_root, envelope_version=1)
    legacy_with_locator = {
        **conformance_document,
        "locator": {"base": "allowed-project-root", "path": "project"},
    }
    with pytest.raises(ValidationError):
        read_linked_project_conformance_document(legacy_with_locator, envelope_version=1)

    assert {path: path.read_bytes() for path in before} == before

def test_fresh_v1_preview_and_apply_are_refused_without_publishing_evidence(
    tmp_path: Path,
) -> None:
    from gnd.evolve import EvolutionError, EvolutionPreview, EvolutionProposal, LinkedProject

    row = _case()
    before = row["inputs"]["before_model"]
    candidate = row["inputs"]["candidate_model"]
    project_root = tmp_path / "linked-project"
    project_root.mkdir()
    (project_root / "payload.txt").write_text("linked bytes\n", encoding="utf-8")
    service, model_path, _verbalization_path = _service(tmp_path, before["text"])
    legacy = EvolutionProposal(
        schema_version=1,
        proposal_id="legacy-new-write",
        expected_model_sha256=before["sha256"],
        candidate_model=_proposal(
            candidate["text"], expected_sha256=before["sha256"]
        ).candidate_model,
        operations=_additive_operations(candidate["text"]),
        rationale="A legacy-shaped proposal must remain read-only.",
        audit=_proposal(candidate["text"], expected_sha256=before["sha256"]).audit,
        linked_projects=(
            LinkedProject(
                project_id="linked",
                root=Path("linked-project"),
                expected_tree_sha256=_tree_sha256(project_root),
            ),
        ),
    )
    before_model = model_path.read_bytes()
    with pytest.raises(EvolutionError, match="versions 1 and 2 are read-only"):
        service.preview(legacy)

    preview_document = _pre_migration_document(RETAINED_PREVIEW)
    legacy_preview = EvolutionPreview.model_validate(preview_document)
    with pytest.raises(EvolutionError, match="versions 1 and 2 are read-only"):
        service.apply(legacy_preview)

    assert model_path.read_bytes() == before_model
    assert not service.evidence_root.exists()

