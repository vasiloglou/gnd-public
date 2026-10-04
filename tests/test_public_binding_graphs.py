from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests/fixtures/public-binding-graphs/graphs.json.gz"
FIXTURE_SHA256 = 'f5784ec847f05dc80a645ab1c1acbf0d7b7faef922fdd90c3445c59f974c881f'
EXPECTED = {'evolution': {'mixed_cases': {'preview-v2-envelope-v1-proposal': {'post_phase': {'message_contains': ['proposal'], 'reason': 'nested-version-disagreement', 'refused': True}, 'pre_phase': {'message_contains': ['proposal.schema_version', 'Input should be 2'], 'refused': True}, 'reader': 'preview'}, 'preview-v3-envelope-v2-proposal': {'post_phase': {'message_contains': ['proposal'], 'reason': 'nested-version-disagreement', 'refused': True}, 'pre_phase': {'message_contains': ['schema_version', 'Input should be 1 or 2'], 'refused': True}, 'reader': 'preview'}, 'proposal-v1-new-project-fields': {'post_phase': {'message_contains': ['linked_projects'], 'reason': 'new-field-name-in-old-version', 'refused': True}, 'pre_phase': {'message_contains': ['linked_projects.0.root', 'Extra inputs are not permitted'], 'refused': True}, 'reader': 'proposal'}, 'proposal-v3-old-project-fields': {'post_phase': {'message_contains': ['linked_projects'], 'reason': 'old-field-name-in-new-version', 'refused': True}, 'pre_phase': {'message_contains': ['schema_version', 'Input should be 1 or 2'], 'refused': True}, 'reader': 'proposal'}, 'record-v2-envelope-v1-conformance': {'post_phase': {'message_contains': ['linked_conformance'], 'reason': 'nested-version-disagreement', 'refused': True}, 'pre_phase': {'message_contains': ['linked_conformance.0.locator', 'Extra inputs are not permitted'], 'refused': True}, 'reader': 'record'}, 'record-v3-envelope-v2-conformance': {'post_phase': {'message_contains': ['linked_conformance'], 'reason': 'nested-version-disagreement', 'refused': True}, 'pre_phase': {'message_contains': ['schema_version', 'Input should be 1 or 2'], 'refused': True}, 'reader': 'record'}}, 'unknown_envelope_version_token': 'Input should be 1 or 2'}}
GRAPH_DOCUMENTS = ("proposal.json", "preview.json", "intent.json", "pending.json", "conformance.json", "record.json")


def _fixture_documents() -> dict[str, Any]:
    assert not FIXTURE.is_symlink()
    with FIXTURE.open("rb") as stream:
        packed = stream.read(64 * 1024 + 1)
    assert len(packed) <= 64 * 1024
    assert hashlib.sha256(packed).hexdigest() == FIXTURE_SHA256
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(512 * 1024 + 1)
    assert len(raw) <= 512 * 1024
    documents = json.loads(raw)
    assert len(documents) == 24
    return documents


def _graph(version: int, name: str) -> dict[str, Any]:
    return _fixture_documents()[f"v{version}/{name}"]


def _mixed(name: str) -> dict[str, Any]:
    return _fixture_documents()[f"mixed/{name}.json"]


def _public_readers() -> dict[str, Any]:
    from gnd.evolve.models import (
        EvolutionFinalizationState,
        EvolutionIntent,
        EvolutionPreview,
        EvolutionProposal,
        EvolutionRecord,
    )
    return {'proposal.json': EvolutionProposal.model_validate, 'preview.json': EvolutionPreview.model_validate, 'intent.json': EvolutionIntent.model_validate, 'pending.json': EvolutionFinalizationState.model_validate, 'record.json': EvolutionRecord.model_validate}


def _refusal(callable_: Any, *arguments: Any, **keywords: Any) -> str:
    """Return the refusal text, or fail because nothing was refused."""
    try:
        callable_(*arguments, **keywords)
    except Exception as error:  # noqa: BLE001 - refusal is the observation
        return f'{type(error).__name__}: {error}'
    raise AssertionError('the reader accepted a document the corpus requires it to refuse')


@pytest.mark.parametrize('version', [1, 2])
@pytest.mark.parametrize('name', GRAPH_DOCUMENTS)
def test_the_frozen_v1_and_v2_graphs_round_trip_byte_identically(version: int, name: str) -> None:
    """CONTROL. Old readers keep their exact meaning at both gates."""
    document = _graph(version, name)
    if name == 'conformance.json':
        from gnd.evolve.models import read_linked_project_conformance_document
        parsed = read_linked_project_conformance_document(document, envelope_version=version)
    else:
        parsed = _public_readers()[name](document)
    assert json.loads(json.dumps(parsed.model_dump(mode='json'))) == document


@pytest.mark.parametrize('name', GRAPH_DOCUMENTS)
def test_the_v3_graph_is_readable_and_round_trips_byte_identically(name: str) -> None:
    """INTENDED RED. Every v3 envelope parses through the public reader and
    serializes back to exactly the committed bytes."""
    document = _graph(3, name)
    if name == 'conformance.json':
        from gnd.evolve.models import read_linked_project_conformance_document
        parsed = read_linked_project_conformance_document(document, envelope_version=3)
    else:
        parsed = _public_readers()[name](document)
    assert json.loads(json.dumps(parsed.model_dump(mode='json'))) == document


@pytest.mark.parametrize('case_id', sorted(EXPECTED['evolution']['mixed_cases']))
def test_every_mixed_graph_is_refused_for_nested_version_disagreement(case_id: str) -> None:
    """INTENDED RED for the v3 cases. A cross-labelled edge must be refused
    because the versions disagree, never because a version is unknown."""
    case = EXPECTED['evolution']['mixed_cases'][case_id]
    message = _refusal(_public_readers()[f"{case['reader']}.json"], _mixed(case_id))
    unknown = EXPECTED['evolution']['unknown_envelope_version_token']
    assert unknown not in message, f'a cross-labelled graph must be refused for its nested disagreement, not because version 3 is unknown: {message}'
    for token in case['post_phase']['message_contains']:
        assert token in message, message


@pytest.mark.parametrize(('version', 'name', 'key'), [(1, 'pending.json', 'linked_projects'), (2, 'pending.json', 'linked_projects'), (2, 'conformance.json', 'root'), (3, 'pending.json', 'root'), (3, 'conformance.json', 'expected_tree_sha256'), (2, 'record.json', 'root')])
def test_wire_reader_refuses_cross_version_keys_even_when_null(version: int, name: str, key: str) -> None:
    """P3R-1: byte-distinct wires cannot share an identity through omitted nulls."""
    from gnd.evolve.models import (
        read_evolution_finalization_state_document,
        read_evolution_record_document,
        read_linked_project_conformance_document,
    )
    document = _graph(version, name)
    target = document
    if name == 'record.json':
        target = document['linked_conformance'][0]
    elif version == 3 and name == 'pending.json':
        target = document['linked_projects'][0]
    target[key] = None
    if name == 'conformance.json':
        _refusal(read_linked_project_conformance_document, document, envelope_version=version)
    elif name == 'record.json':
        _refusal(read_evolution_record_document, document)
    else:
        _refusal(read_evolution_finalization_state_document, document)
