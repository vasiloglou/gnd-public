"""Original closed-version graph guard with disclosed generic locator fixture adaptation."""
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


def _public_graph():
    packed=(Path(__file__).parent / "fixtures/public-version-graph/closure.json.gz").read_bytes()
    assert len(packed)<=65536
    assert hashlib.sha256(packed).hexdigest()=='847642af0f79088ed7c8497986e48cfd62a9728b8a148972c1f6410c2c61a23b'
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw=stream.read(131073)
    assert len(raw)<=131072
    assert hashlib.sha256(raw).hexdigest()=='57720c2fb3effa0a5026886cc84464ba1e1feb8285a6ed1db1dbf22e4c2bfe88'
    documents=json.loads(raw)
    assert set(documents)=={'v1-pending.json', 'v2-pending.json', 'v1-conformance.json', 'v2-preview.json', 'v2-record.json', 'v2-conformance.json', 'v1-preview.json', 'clean-payload.json', 'v1-intent.json', 'v2-intent.json', 'v1-record.json'}
    temporary=tempfile.TemporaryDirectory(prefix="gnd-public-version-graph-")
    root=Path(temporary.name)
    for name,text in documents.items():
        (root/name).write_text(text,encoding="utf-8")
    return temporary,root

_TEMPORARY,_ROOT=_public_graph()
atexit.register(_TEMPORARY.cleanup)
RETAINED_RECORD=_ROOT/"v2-record.json"
RETAINED_CONFORMANCE=_ROOT/"v2-conformance.json"
RETAINED_PREVIEW=_ROOT/"v2-preview.json"
RETAINED_INTENT=_ROOT/"v2-intent.json"
CLEAN_CONFORMANCE_PAYLOAD=_ROOT/"clean-payload.json"


def _pre_migration_document(path: Path) -> dict[str,Any]:
    # Public-owned schema1 graph replaces the source-private historical Git lookup.
    return json.loads((_ROOT/path.name.replace("v2-","v1-",1)).read_text(encoding="utf-8"))

def _current_proposal_document() -> dict[str, Any]:
    preview = json.loads(RETAINED_PREVIEW.read_text(encoding="utf-8"))
    return preview["proposal"]

def _current_preview_document() -> dict[str, Any]:
    return json.loads(RETAINED_PREVIEW.read_text(encoding="utf-8"))

def _current_intent_document() -> dict[str, Any]:
    return json.loads(RETAINED_INTENT.read_text(encoding="utf-8"))

def _current_clean_record_documents() -> tuple[dict[str, Any], dict[str, Any]]:
    from gnd.evolve import canonical_sha256, conformance_payload_sha256

    record = json.loads(RETAINED_RECORD.read_text(encoding="utf-8"))
    conformance = json.loads(RETAINED_CONFORMANCE.read_text(encoding="utf-8"))
    conformance["payload"] = json.loads(
        CLEAN_CONFORMANCE_PAYLOAD.read_text(encoding="utf-8")
    )
    conformance["payload_sha256"] = conformance_payload_sha256(conformance["payload"])
    conformance["exit_code"] = 0
    record["linked_conformance"] = [conformance]
    record["conformance_exit_code"] = 0
    record["published_with_drift"] = False
    record["record_identity_sha256"] = canonical_sha256(
        {key: value for key, value in record.items() if key != "record_identity_sha256"}
    )
    return record, conformance

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

def test_envelope_version_dispatch_selects_one_closed_nested_graph(
    tmp_path: Path,
) -> None:
    from gnd.cli import _evolve_read_claim
    from gnd.evolve import (
        EvolutionIntent,
        EvolutionPreview,
        EvolutionProposal,
        EvolutionRecord,
        read_evolution_proposal,
        read_evolution_record,
        read_linked_project_conformance_document,
    )
    from gnd.evolve.models import read_evolution_intent_document

    current_proposal = _current_proposal_document()
    current_preview = _current_preview_document()
    current_intent = _current_intent_document()
    current_record, current_conformance = _current_clean_record_documents()

    assert EvolutionProposal.model_validate(current_proposal).model_dump(
        mode="json"
    ) == current_proposal
    assert EvolutionProposal.model_validate_json(
        json.dumps(current_proposal)
    ).model_dump(mode="json") == current_proposal
    assert EvolutionPreview.model_validate(current_preview).model_dump(
        mode="json"
    ) == current_preview
    assert EvolutionIntent.model_validate(current_intent).model_dump(
        mode="json"
    ) == current_intent
    assert EvolutionRecord.model_validate(current_record).model_dump(
        mode="json"
    ) == current_record
    assert EvolutionRecord.model_validate_json(json.dumps(current_record)).model_dump(
        mode="json"
    ) == current_record
    assert read_linked_project_conformance_document(
        current_conformance, envelope_version=2
    ).locator.path == "project"

    proposal_path = tmp_path / "proposal.json"
    record_path = tmp_path / "record.json"
    intent_path = tmp_path / "intent.json"
    proposal_path.write_text(json.dumps(current_proposal), encoding="utf-8")
    record_path.write_text(json.dumps(current_record), encoding="utf-8")
    intent_path.write_text(json.dumps(current_intent), encoding="utf-8")
    assert read_evolution_proposal(proposal_path).schema_version == 2
    assert read_evolution_record(record_path).schema_version == 2
    assert read_evolution_intent_document(json.loads(intent_path.read_text())).schema_version == 2
    assert _evolve_read_claim(record_path, EvolutionRecord, label="record").schema_version == 2

    legacy_preview = _pre_migration_document(RETAINED_PREVIEW)
    legacy_proposal = legacy_preview["proposal"]
    legacy_record, legacy_conformance = _legacy_clean_record_documents()
    legacy_intent = _pre_migration_document(RETAINED_INTENT)

    mixed_documents = [
        (EvolutionProposal, {**legacy_proposal, "schema_version": 2}),
        (EvolutionProposal, {**current_proposal, "schema_version": 1}),
        (EvolutionPreview, {**legacy_preview, "schema_version": 2}),
        (EvolutionIntent, {**legacy_intent, "schema_version": 2}),
        (EvolutionIntent, {**current_intent, "schema_version": 1}),
        (EvolutionRecord, {**legacy_record, "schema_version": 2}),
        (EvolutionRecord, {**current_record, "schema_version": 1}),
    ]
    for model_type, document in mixed_documents:
        with pytest.raises(ValidationError):
            model_type.model_validate(document)
        with pytest.raises(ValidationError):
            model_type.model_validate_json(json.dumps(document))

    current_without_locator = {
        key: value for key, value in current_conformance.items() if key != "locator"
    }
    with pytest.raises(ValidationError):
        read_linked_project_conformance_document(
            current_without_locator, envelope_version=2
        )
    current_with_root = {**current_conformance, "root": legacy_conformance["root"]}
    with pytest.raises(ValidationError):
        read_linked_project_conformance_document(current_with_root, envelope_version=2)

