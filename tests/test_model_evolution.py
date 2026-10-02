"""Staged evolution, CAS, and D-12 provenance contract tests."""

from __future__ import annotations

import copy
import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError
from ruamel.yaml import YAML

REPO_ROOT = Path(__file__).resolve().parent.parent
EVOLUTION_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "phase4_reference" / "evolution.json"




def _case(name: str = "evolution-safe-additive") -> dict[str, Any]:
    fixture = json.loads(EVOLUTION_FIXTURE.read_text(encoding="utf-8"))
    return next(row for row in fixture["cases"] if row["name"] == name)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_model_text(document: dict[str, Any]) -> str:
    return json.dumps(document, sort_keys=False, separators=(",", ":"), ensure_ascii=False) + "\n"


def _parse(text: str) -> dict[str, Any]:
    return YAML(typ="safe").load(text)


def _additive_operations(candidate_text: str) -> tuple[Any, ...]:
    from gnd.evolve import ElementLocator, EvolutionOperation, EvolutionOperationKind

    candidate = _parse(candidate_text)
    priority = next(item for item in candidate["object_types"] if item["id"] == "priority")
    fact = next(item for item in candidate["fact_types"] if item["id"] == "work_item_has_priority")
    return (
        EvolutionOperation(
            operation_id="add-priority-type",
            kind=EvolutionOperationKind.ADD,
            locator=ElementLocator(collection="object_types", element_id="priority"),
            before=None,
            after=priority,
        ),
        EvolutionOperation(
            operation_id="add-priority-fact",
            kind=EvolutionOperationKind.ADD,
            locator=ElementLocator(collection="fact_types", element_id="work_item_has_priority"),
            before=None,
            after=fact,
        ),
    )


def _proposal(
    candidate_text: str,
    *,
    expected_sha256: str,
    operations: tuple[Any, ...] | None = None,
    artifacts: tuple[Any, ...] = (),
    projects: tuple[Any, ...] = (),
    proposal_id: str = "proposal-safe-additive",
) -> Any:
    from gnd.evolve import (
        CommittedText,
        EvolutionOperationAudit,
        EvolutionProposal,
    )

    return EvolutionProposal(
        proposal_id=proposal_id,
        expected_model_sha256=expected_sha256,
        candidate_model=CommittedText.from_text(candidate_text, media_type="application/yaml"),
        operations=operations if operations is not None else _additive_operations(candidate_text),
        rationale="Add an inferred priority vocabulary without changing existing metadata.",
        audit=EvolutionOperationAudit(
            actor_id="owner:fixture",
            origin="phase4-reference-test",
            requested_at=datetime(2026, 8, 13, 12, 0, tzinfo=UTC),
        ),
        linked_projects=projects,
        artifacts=artifacts,
    )


def _breaking_operations(before_text: str, candidate_text: str) -> tuple[Any, ...]:
    from gnd.evolve import ElementLocator, EvolutionOperation, EvolutionOperationKind

    before = _parse(before_text)
    candidate = _parse(candidate_text)
    title = next(item for item in before["object_types"] if item["id"] == "title")
    summary = next(item for item in candidate["object_types"] if item["id"] == "summary")
    title_fact = next(
        item for item in before["fact_types"] if item["id"] == "work_item_has_title"
    )
    return (
        EvolutionOperation(
            operation_id="rename-title-to-summary",
            kind=EvolutionOperationKind.RENAME,
            locator=ElementLocator(collection="object_types", element_id="title"),
            before=title,
            after=summary,
        ),
        EvolutionOperation(
            operation_id="delete-title-fact",
            kind=EvolutionOperationKind.DELETE,
            locator=ElementLocator(
                collection="fact_types", element_id="work_item_has_title"
            ),
            before=title_fact,
        ),
    )


def _artifact_locators(row: dict[str, Any]) -> tuple[Any, ...]:
    from gnd.evolve import ArtifactLocator

    return tuple(
        ArtifactLocator(
            artifact_id=item["artifact_id"],
            artifact_kind=item["artifact_kind"],
            path=item["path"],
            sha256=item["sha256"],
            references=tuple(item["references"]),
        )
        for item in row["inputs"]["supplied_artifacts"]
    )


def _breaking_proposal(row: dict[str, Any]) -> Any:
    before = row["inputs"]["before_model"]
    candidate = row["inputs"]["candidate_model"]
    return _proposal(
        candidate["text"],
        expected_sha256=before["sha256"],
        operations=_breaking_operations(before["text"], candidate["text"]),
        artifacts=_artifact_locators(row),
        proposal_id="proposal-rename-delete",
    )


def _accepted_preview(service: Any, proposal: Any) -> Any:
    preview = service.preview(proposal)
    return service.preview(
        proposal,
        accepted_blast_radius_sha256=preview.blast_radius.report_sha256,
    )


def _service(tmp_path: Path, before_text: str) -> tuple[Any, Path, Path]:
    from gnd.evolve import EvolutionService

    tmp_path.mkdir(parents=True, exist_ok=True)
    model_path = tmp_path / "model.orm.yaml"
    verbalization_path = tmp_path / "model.verbalization.txt"
    model_path.write_text(before_text, encoding="utf-8")
    verbalization_path.write_text("pre-existing verbalization\n", encoding="utf-8")
    service = EvolutionService(
        model_path=model_path,
        evidence_root=tmp_path / "evolution-evidence",
        verbalization_path=verbalization_path,
        allowed_project_root=tmp_path,
    )
    return service, model_path, verbalization_path


def _tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        if path.is_symlink():
            digest.update(b"L\0" + relative + b"\0" + path.readlink().as_posix().encode("utf-8"))
        elif path.is_file():
            digest.update(b"F\0" + relative + b"\0" + path.read_bytes())
        elif path.is_dir():
            digest.update(b"D\0" + relative + b"\0")
    return digest.hexdigest()


def _linked_v3(project_id: str, root: Path, **coordinate: Any) -> Any:
    """A linked project over every leaf; production derives none, so a test does."""
    from gnd.artifacts import snapshot_tracked_roster
    from gnd.evolve import LinkedProject, TrackedRoster
    leaves = (item for item in root.rglob("*") if item.is_symlink() or item.is_file())
    paths = tuple(sorted(item.relative_to(root).as_posix() for item in leaves))
    return LinkedProject(
        project_id=project_id,
        tracked_roster=TrackedRoster(paths=paths),
        expected_tracked_tree_sha256=snapshot_tracked_roster(root, paths, label="linked")[1],
        **coordinate,
    )
def _write_cli_workspace(
    tmp_path: Path,
    *,
    case_name: str = "evolution-safe-additive",
    breaking: bool = False,
    projects: tuple[Any, ...] = (),
    proposal_id: str | None = None,
) -> dict[str, Any]:
    row = _case(case_name)
    before = row["inputs"]["before_model"]
    candidate = row["inputs"]["candidate_model"]
    workspace = tmp_path / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    model_path = workspace / "model.orm.yaml"
    verbalization_path = workspace / "model.verbalization.txt"
    proposal_path = workspace / "proposal.json"
    preview_path = workspace / "review" / "preview.json"
    records_path = workspace / "records"
    model_path.write_text(before["text"], encoding="utf-8")
    verbalization_path.write_text("pre-existing verbalization\n", encoding="utf-8")
    (workspace / "owner-note.txt").write_text("owner bytes stay put\n", encoding="utf-8")
    if breaking:
        proposal = _breaking_proposal(row)
    else:
        proposal = _proposal(
            candidate["text"],
            expected_sha256=before["sha256"],
            projects=projects,
            proposal_id=proposal_id or "proposal-safe-additive",
        )
    proposal_path.write_text(
        json.dumps(
            proposal.model_dump(mode="json"),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "row": row,
        "workspace": workspace,
        "model": model_path,
        "verbalization": verbalization_path,
        "proposal": proposal,
        "proposal_path": proposal_path,
        "preview": preview_path,
        "records": records_path,
    }


def _claims(text: str) -> list[Any]:
    """Split the concatenated public claim payloads one command emitted.

    D-24 keeps the publication claim and the conformance claim as two separate
    payloads, so a chained ``gnd evolve apply`` writes two JSON documents rather
    than one merged verdict.
    """

    decoder = json.JSONDecoder()
    values: list[Any] = []
    index = 0
    while True:
        while index < len(text) and text[index].isspace():
            index += 1
        if index >= len(text):
            return values
        value, index = decoder.raw_decode(text, index)
        values.append(value)


def _preview_argv(paths: dict[str, Any]) -> list[str]:
    return [
        "evolve",
        "preview",
        str(paths["model"]),
        str(paths["proposal_path"]),
        "--workspace",
        str(paths["workspace"]),
        "--records",
        str(paths["records"]),
        "--out",
        str(paths["preview"]),
        "--format",
        "json",
    ]


def _apply_argv(paths: dict[str, Any]) -> list[str]:
    return [
        "evolve",
        "apply",
        str(paths["model"]),
        str(paths["proposal_path"]),
        "--preview",
        str(paths["preview"]),
        "--workspace",
        str(paths["workspace"]),
        "--records",
        str(paths["records"]),
        "--format",
        "json",
    ]


def _finalize_argv(paths: dict[str, Any], pending: Path) -> list[str]:
    return [
        "evolve",
        "finalize",
        str(paths["model"]),
        str(pending),
        "--workspace",
        str(paths["workspace"]),
        "--records",
        str(paths["records"]),
        "--format",
        "json",
    ]


def test_exact_four_row_evolution_corpus_commits_every_input_byte() -> None:
    fixture = json.loads(EVOLUTION_FIXTURE.read_text(encoding="utf-8"))
    rows = fixture["cases"]
    assert [row["name"] for row in rows] == [
        "evolution-safe-additive",
        "evolution-rename-delete-blast-radius",
        "evolution-concurrent-cas-refusal",
        "evolution-clean-and-drift-linked-conformance",
    ]

    for row in rows:
        for name in ("before_model", "candidate_model"):
            blob = row["inputs"][name]
            assert _sha(blob["text"]) == blob["sha256"]
        for blob in row["inputs"].get("supplied_artifacts", ()):
            assert _sha(blob["text"]) == blob["sha256"]

    assert not any("interruption" in row["name"] for row in rows)


def test_rename_delete_requires_exact_complete_blast_radius_acceptance(tmp_path: Path) -> None:
    from gnd.evolve import EvolutionError

    row = _case("evolution-rename-delete-blast-radius")
    before = row["inputs"]["before_model"]
    candidate = row["inputs"]["candidate_model"]
    service, model_path, verbalization_path = _service(tmp_path, before["text"])
    proposal = _breaking_proposal(row)
    original_model = model_path.read_bytes()
    original_verbalization = verbalization_path.read_bytes()

    preview = service.preview(proposal)
    actual_inventory = [
        {"surface": item.surface, "reference": item.reference}
        for item in preview.blast_radius.entries
    ]
    assert actual_inventory == row["expected"]["blast_radius"]
    assert len({item.reference for item in preview.blast_radius.entries}) == len(
        preview.blast_radius.entries
    )
    assert preview.breaking is True
    assert preview.accepted_blast_radius_sha256 is None
    assert preview.blast_radius.proposal_sha256 == proposal.proposal_sha256
    assert preview.blast_radius.before_model_sha256 == before["sha256"]
    assert preview.blast_radius.candidate_model_sha256 == candidate["sha256"]

    with pytest.raises(EvolutionError, match="explicit acceptance"):
        service.apply(preview)
    with pytest.raises(EvolutionError, match="accepted blast radius"):
        service.preview(proposal, accepted_blast_radius_sha256="0" * 64)

    accepted = _accepted_preview(service, proposal)
    mismatched_proposal = proposal.model_copy(update={"rationale": "A different proposal."})
    mismatched_preview = accepted.model_copy(update={"proposal": mismatched_proposal})
    with pytest.raises(EvolutionError, match="preview identity|proposal identity"):
        service.apply(mismatched_preview)

    assert model_path.read_bytes() == original_model
    assert verbalization_path.read_bytes() == original_verbalization

    pending = service.apply(accepted)
    assert model_path.read_bytes() == candidate["text"].encode("utf-8")
    assert verbalization_path.read_bytes() == original_verbalization
    assert set(pending.model_dump(mode="json")) == set(
        row["expected"]["finalization_state"]
    ) | {"linked_projects"}
    record = service.finalize(pending)
    dumped = record.model_dump(mode="json")
    for field in row["expected"]["final_record_identity"]:
        assert dumped[field] is not None
    assert record.operations == proposal.operations
    assert record.rationale == proposal.rationale
    assert record.audit == proposal.audit
    assert record.validation == accepted.validation
    assert record.cas.published is True
    assert record.affected_code.blast_radius == tuple(
        item.reference for item in accepted.blast_radius.entries
    )
    assert record.accepted_blast_radius_sha256 == accepted.blast_radius.report_sha256


def test_rename_delete_rejects_undeclared_dependent_deletion(tmp_path: Path) -> None:
    from gnd.evolve import EvolutionError

    row = _case("evolution-rename-delete-blast-radius")
    before = row["inputs"]["before_model"]
    candidate = row["inputs"]["candidate_model"]
    service, _model_path, _verbalization_path = _service(tmp_path, before["text"])
    proposal = _proposal(
        candidate["text"],
        expected_sha256=before["sha256"],
        operations=_breaking_operations(before["text"], candidate["text"])[:1],
        artifacts=_artifact_locators(row),
        proposal_id="proposal-undeclared-dependent-delete",
    )

    with pytest.raises(EvolutionError, match="declared operations"):
        service.preview(proposal)


def test_preview_apply_finalize_binds_every_stage_and_is_identity_stable(tmp_path: Path) -> None:
    row = _case()
    before = row["inputs"]["before_model"]
    candidate = row["inputs"]["candidate_model"]
    service, model_path, verbalization_path = _service(tmp_path, before["text"])
    proposal = _proposal(candidate["text"], expected_sha256=before["sha256"])

    preview = service.preview(proposal)
    assert preview.before_model.sha256 == before["sha256"]
    assert preview.candidate_model.sha256 == candidate["sha256"]
    assert preview.validation.valid is True
    assert preview.validation.model_sha256 == candidate["sha256"]
    assert preview.affected_references == (
        "fact_types[work_item_has_priority]",
        "object_types[priority]",
    )

    prior_verbalization = verbalization_path.read_bytes()
    pending = service.apply(preview)
    assert model_path.read_bytes() == candidate["text"].encode("utf-8")
    assert verbalization_path.read_bytes() == prior_verbalization
    assert pending.proposal_sha256 == proposal.proposal_sha256
    assert pending.preview_sha256 == preview.preview_sha256
    assert pending.old_model_sha256 == before["sha256"]
    assert pending.new_model_sha256 == candidate["sha256"]

    record = service.finalize(pending)
    assert verbalization_path.read_text(encoding="utf-8") == preview.verbalization.text
    assert record.old_model_sha256 == before["sha256"]
    assert record.new_model_sha256 == candidate["sha256"]
    assert record.model_commit_point == "model-cas"
    assert record.cas.published is True
    assert record.affected_code.generated_code_written is False
    assert record.affected_code.extension_code_written is False

    record_path = service.record_path(proposal.proposal_id)
    first_bytes = record_path.read_bytes()
    assert hashlib.sha256(first_bytes).hexdigest() == service.final_record_file_sha256(record)

    assert service.finalize(pending) == record
    assert record_path.read_bytes() == first_bytes


def test_preview_rejects_undeclared_candidate_changes(tmp_path: Path) -> None:
    from gnd.evolve import EvolutionError

    row = _case()
    before = row["inputs"]["before_model"]
    candidate = row["inputs"]["candidate_model"]
    service, _model_path, _verbalization_path = _service(tmp_path, before["text"])
    incomplete = _additive_operations(candidate["text"])[:1]
    proposal = _proposal(
        candidate["text"],
        expected_sha256=before["sha256"],
        operations=incomplete,
    )

    with pytest.raises(EvolutionError, match="declared operations"):
        service.preview(proposal)


def test_explicit_modify_operation_preserves_unrelated_constraint_metadata(tmp_path: Path) -> None:
    from gnd.evolve import (
        ElementLocator,
        EvolutionOperation,
        EvolutionOperationKind,
    )

    row = _case()
    before = row["inputs"]["before_model"]
    before_document = _parse(before["text"])
    candidate_document = copy.deepcopy(before_document)
    before_title = next(item for item in before_document["object_types"] if item["id"] == "title")
    after_title = next(item for item in candidate_document["object_types"] if item["id"] == "title")
    after_title["provenance"] = {"user_quote": "Title remains an authored value type."}
    candidate_text = _canonical_model_text(candidate_document)
    operation = EvolutionOperation(
        operation_id="document-title-provenance",
        kind=EvolutionOperationKind.MODIFY,
        locator=ElementLocator(collection="object_types", element_id="title"),
        before=before_title,
        after=after_title,
    )
    service, model_path, _verbalization_path = _service(tmp_path, before["text"])

    preview = service.preview(
        _proposal(
            candidate_text,
            expected_sha256=before["sha256"],
            operations=(operation,),
        )
    )
    service.apply(preview)

    published = _parse(model_path.read_text(encoding="utf-8"))
    assert published == candidate_document
    assert (
        published["fact_types"][0]["constraints"][0]
        == before_document["fact_types"][0]["constraints"][0]
    )


def test_model_identity_locator_is_closed_atomic_and_modify_only() -> None:
    from gnd.evolve import (
        EvolutionOperation,
        EvolutionOperationKind,
        ModelIdentityLocator,
    )

    locator = ModelIdentityLocator()
    assert locator.model_dump(mode="json") == {"locator_kind": "model-identity"}
    assert locator.reference() == "model.identity"
    with pytest.raises(ValidationError):
        ModelIdentityLocator.model_validate({"locator_kind": "model-identity", "field": "version"})

    before = {"version": 1, "model_id": "evolution-demo"}
    after = {"version": 2, "model_id": "evolution-demo-v2"}
    operation = EvolutionOperation(
        operation_id="bump-model-identity",
        kind=EvolutionOperationKind.MODIFY,
        locator=locator,
        before=before,
        after=after,
    )
    round_tripped = EvolutionOperation.model_validate_json(operation.model_dump_json())
    assert isinstance(round_tripped.locator, ModelIdentityLocator)
    assert round_tripped.reference() == "model.identity"
    assert round_tripped.before == before and round_tripped.after == after

    invalid_operations = (
        {
            "kind": EvolutionOperationKind.ADD,
            "before": None,
            "after": after,
        },
        {
            "kind": EvolutionOperationKind.DELETE,
            "before": before,
            "after": None,
        },
        {
            "kind": EvolutionOperationKind.RENAME,
            "before": before,
            "after": after,
        },
        {
            "kind": EvolutionOperationKind.MODIFY,
            "before": {"version": 1},
            "after": after,
        },
        {
            "kind": EvolutionOperationKind.MODIFY,
            "before": before,
            "after": {"model_id": "evolution-demo-v2"},
        },
        {
            "kind": EvolutionOperationKind.MODIFY,
            "before": {**before, "source": "hidden"},
            "after": after,
        },
        {
            "kind": EvolutionOperationKind.MODIFY,
            "before": before,
            "after": {**after, "source": "hidden"},
        },
    )
    for index, values in enumerate(invalid_operations):
        with pytest.raises(ValidationError):
            EvolutionOperation(
                operation_id=f"invalid-model-identity-{index}",
                locator=locator,
                **values,
            )


def test_model_identity_replay_is_atomic_and_refuses_stale_or_hidden_changes(
    tmp_path: Path,
) -> None:
    import gnd.evolve.service as evolution_service
    from gnd.evolve import (
        EvolutionError,
        EvolutionOperation,
        EvolutionOperationKind,
        ModelIdentityLocator,
    )

    row = _case()
    before = row["inputs"]["before_model"]
    before_document = _parse(before["text"])
    candidate_document = copy.deepcopy(before_document)
    candidate_document.update({"version": 2, "model_id": "evolution-demo-v2"})
    candidate_text = _canonical_model_text(candidate_document)
    operation = EvolutionOperation(
        operation_id="bump-model-identity",
        kind=EvolutionOperationKind.MODIFY,
        locator=ModelIdentityLocator(),
        before={"version": 1, "model_id": "evolution-demo"},
        after={"version": 2, "model_id": "evolution-demo-v2"},
    )

    assert evolution_service._delta_element_ids(operation) == frozenset()
    assert (
        evolution_service._apply_declared_operations(before_document, (operation,))
        == candidate_document
    )
    assert before_document["version"] == 1
    assert before_document["model_id"] == "evolution-demo"

    service, model_path, _verbalization_path = _service(tmp_path / "accepted", before["text"])
    proposal = _proposal(
        candidate_text,
        expected_sha256=before["sha256"],
        operations=(operation,),
        proposal_id="proposal-model-identity",
    )
    preview = service.preview(proposal)
    assert preview.affected_references == ("model.identity",)
    identity_radius = next(
        entry for entry in preview.blast_radius.entries if entry.reference == "model.identity"
    )
    assert identity_radius.surface == "model"
    assert identity_radius.change == "modified"
    assert identity_radius.operation_ids == ("bump-model-identity",)
    service.apply(preview)
    assert _parse(model_path.read_text(encoding="utf-8")) == candidate_document

    stale_operation = EvolutionOperation(
        operation_id="stale-model-identity",
        kind=EvolutionOperationKind.MODIFY,
        locator=ModelIdentityLocator(),
        before={"version": 0, "model_id": "stale"},
        after={"version": 2, "model_id": "evolution-demo-v2"},
    )
    stale_service, stale_model, _ = _service(tmp_path / "stale", before["text"])
    with pytest.raises(EvolutionError, match=r"declared before.*model\.identity"):
        stale_service.preview(
            _proposal(
                candidate_text,
                expected_sha256=before["sha256"],
                operations=(stale_operation,),
                proposal_id="proposal-stale-model-identity",
            )
        )
    assert stale_model.read_text(encoding="utf-8") == before["text"]

    hidden_document = copy.deepcopy(candidate_document)
    next(item for item in hidden_document["object_types"] if item["id"] == "title")["name"] = (
        "HiddenTitle"
    )
    hidden_service, hidden_model, _ = _service(tmp_path / "hidden", before["text"])
    with pytest.raises(EvolutionError, match="declared operations"):
        hidden_service.preview(
            _proposal(
                _canonical_model_text(hidden_document),
                expected_sha256=before["sha256"],
                operations=(operation,),
                proposal_id="proposal-hidden-model-change",
            )
        )
    assert hidden_model.read_text(encoding="utf-8") == before["text"]


def test_invalid_candidate_preserves_model_and_verbalization_bytes(tmp_path: Path) -> None:
    from gnd.evolve import EvolutionError

    row = _case()
    before = row["inputs"]["before_model"]
    candidate_doc = _parse(row["inputs"]["candidate_model"]["text"])
    candidate_doc["fact_types"][-1]["constraints"][0]["source"] = "oracle"
    candidate_text = _canonical_model_text(candidate_doc)
    service, model_path, verbalization_path = _service(tmp_path, before["text"])
    original_verbalization = verbalization_path.read_bytes()

    with pytest.raises(EvolutionError, match="candidate model"):
        service.preview(_proposal(candidate_text, expected_sha256=before["sha256"]))

    assert model_path.read_bytes() == before["text"].encode("utf-8")
    assert verbalization_path.read_bytes() == original_verbalization


def test_stale_model_cas_preserves_concurrent_bytes_and_verbalization(tmp_path: Path) -> None:
    from gnd.evolve import EvolutionError

    row = _case("evolution-concurrent-cas-refusal")
    before = row["inputs"]["before_model"]
    candidate = row["inputs"]["candidate_model"]
    service, model_path, verbalization_path = _service(tmp_path, before["text"])
    preview = service.preview(_proposal(candidate["text"], expected_sha256=before["sha256"]))
    original_verbalization = verbalization_path.read_bytes()

    concurrent_doc = _parse(before["text"])
    concurrent_doc["source"]["concurrent_writer"] = "won"
    concurrent_bytes = _canonical_model_text(concurrent_doc).encode("utf-8")
    model_path.write_bytes(concurrent_bytes)

    with pytest.raises(EvolutionError, match="stale|CAS|changed"):
        service.apply(preview)

    assert model_path.read_bytes() == concurrent_bytes
    assert verbalization_path.read_bytes() == original_verbalization


def test_pending_finalization_refuses_divergent_model_without_rollback(tmp_path: Path) -> None:
    from gnd.evolve import EvolutionError

    row = _case()
    before = row["inputs"]["before_model"]
    candidate = row["inputs"]["candidate_model"]
    service, model_path, verbalization_path = _service(tmp_path, before["text"])
    preview = service.preview(_proposal(candidate["text"], expected_sha256=before["sha256"]))
    pending = service.apply(preview)
    original_verbalization = verbalization_path.read_bytes()

    divergent = _parse(candidate["text"])
    divergent["source"]["concurrent_writer"] = "post-cas"
    divergent_bytes = _canonical_model_text(divergent).encode("utf-8")
    model_path.write_bytes(divergent_bytes)

    with pytest.raises(EvolutionError, match="stale finalization|divergent"):
        service.finalize(pending)

    assert model_path.read_bytes() == divergent_bytes
    assert verbalization_path.read_bytes() == original_verbalization
    assert not service.record_path(pending.proposal_id).exists()


def _breaking_lifecycle_candidate(document: dict[str, Any]) -> dict[str, Any]:
    title = next(item for item in document["object_types"] if item["id"] == "title")
    title.update({"id": "summary", "name": "Summary"})
    title_fact = next(
        item for item in document["fact_types"] if item["id"] == "work_item_has_title"
    )
    title_fact["reading"] = "{WorkItem} has {Summary}"
    title_role = next(item for item in title_fact["roles"] if item["role_name"] == "title")
    title_role.update({"object_type": "summary", "role_name": "summary"})
    return document


def _breaking_lifecycle_operations(before_text: str, candidate_text: str) -> tuple[Any, ...]:
    from gnd.evolve import ElementLocator, EvolutionOperation, EvolutionOperationKind

    before = _parse(before_text)
    candidate = _parse(candidate_text)
    before_title = next(item for item in before["object_types"] if item["id"] == "title")
    after_summary = next(item for item in candidate["object_types"] if item["id"] == "summary")
    before_fact = next(
        item for item in before["fact_types"] if item["id"] == "work_item_has_title"
    )
    after_fact = next(
        item for item in candidate["fact_types"] if item["id"] == "work_item_has_title"
    )
    return (
        EvolutionOperation(
            operation_id="rename-title-to-summary",
            kind=EvolutionOperationKind.RENAME,
            locator=ElementLocator(collection="object_types", element_id="title"),
            before=before_title,
            after=after_summary,
        ),
        EvolutionOperation(
            operation_id="retarget-title-fact",
            kind=EvolutionOperationKind.MODIFY,
            locator=ElementLocator(
                collection="fact_types", element_id="work_item_has_title"
            ),
            before=before_fact,
            after=after_fact,
        ),
        *_additive_operations(candidate_text),
    )


@pytest.mark.parametrize(
    ("lifecycle", "mutate", "accepted"),
    [
        ("unchanged", lambda doc: doc, True),
        ("newly-inferred", lambda doc: doc, True),
        (
            "owner-approved",
            lambda doc: _mutate_new_constraint(
                doc,
                source="user-supplied",
                status="confirmed",
                modality="alethic",
                provenance={"user_note": "Owner approved this constraint."},
            ),
            True,
        ),
        (
            "forbidden-sixth-source",
            lambda doc: _mutate_new_constraint(doc, source="oracle"),
            False,
        ),
        (
            "audit-provenance-smuggling",
            lambda doc: _mutate_new_constraint(
                doc,
                provenance={
                    "rationale_world_fact": "A priority is singular at a point in time.",
                    "actor_id": "owner:fixture",
                    "origin": "audit-log",
                    "requested_at": "2026-08-13T12:00:00Z",
                },
            ),
            False,
        ),
    ],
)
def test_d12_constraint_lifecycle_is_independent_of_operation_audit(
    tmp_path: Path,
    monkeypatch: Any,
    lifecycle: str,
    mutate: Any,
    accepted: bool,
) -> None:
    import gnd.evolve.service as evolution_module
    from gnd.evolve import EvolutionError

    row = _case()
    before = row["inputs"]["before_model"]
    candidate_doc = _breaking_lifecycle_candidate(
        mutate(copy.deepcopy(_parse(row["inputs"]["candidate_model"]["text"])))
    )
    candidate_text = _canonical_model_text(candidate_doc)
    service, model_path, _verbalization_path = _service(tmp_path / lifecycle, before["text"])
    proposal = _proposal(
        candidate_text,
        expected_sha256=before["sha256"],
        operations=_breaking_lifecycle_operations(before["text"], candidate_text),
        proposal_id=f"proposal-d12-{lifecycle}",
    )
    real_enforce = evolution_module._enforce_d12
    calls: list[tuple[dict[str, Any], dict[str, Any]]] = []

    def counted_enforce(
        before_document: dict[str, Any], candidate_document: dict[str, Any]
    ) -> None:
        calls.append((before_document, candidate_document))
        real_enforce(before_document, candidate_document)

    monkeypatch.setattr(evolution_module, "_enforce_d12", counted_enforce)

    if accepted:
        preview = _accepted_preview(service, proposal)
        pending = service.apply(preview)
        record = service.finalize(pending)
        original_constraint = _parse(before["text"])["fact_types"][0]["constraints"][0]
        candidate_constraint = _parse(preview.candidate_model.text)["fact_types"][0]["constraints"][
            0
        ]
        assert candidate_constraint == original_constraint
        assert model_path.read_text(encoding="utf-8") == candidate_text
        assert record.audit == proposal.audit
        assert record.operations == proposal.operations
        assert len(calls) == 4  # initial preview, accepted preview, apply, finalize
        new_constraint = _parse(preview.candidate_model.text)["fact_types"][-1]["constraints"][0]
        if lifecycle == "owner-approved":
            assert (new_constraint["source"], new_constraint["status"]) == (
                "user-supplied",
                "confirmed",
            )
        else:
            assert (
                new_constraint["source"],
                new_constraint["status"],
                new_constraint["modality"],
            ) == ("llm-inferred", "proposed", "deontic")
    else:
        with pytest.raises(EvolutionError):
            service.preview(proposal)
        assert model_path.read_text(encoding="utf-8") == before["text"]
        assert len(calls) <= 1  # schema validation may reject a sixth source first


def _mutate_new_constraint(document: dict[str, Any], **changes: Any) -> dict[str, Any]:
    document["fact_types"][-1]["constraints"][0].update(changes)
    return document


def test_operation_audit_is_closed_and_cannot_pose_as_constraint_provenance() -> None:
    from gnd.evolve import ArtifactLocator, ElementLocator, EvolutionOperationAudit, LinkedProject

    with pytest.raises(ValidationError):
        EvolutionOperationAudit.model_validate(
            {
                "actor_id": "owner:fixture",
                "origin": "test",
                "requested_at": "2026-08-13T12:00:00Z",
                "source": "user-supplied",
                "status": "confirmed",
                "modality": "alethic",
            }
        )

    with pytest.raises(ValidationError):
        ElementLocator.model_validate(
            {"collection": "object_types", "element_id": "title", "index": 2}
        )
    with pytest.raises(ValidationError):
        LinkedProject(
            project_id="escape",
            root=Path("../outside"),
            expected_tree_sha256="0" * 64,
        )
    with pytest.raises(ValidationError):
        ArtifactLocator(
            artifact_id="escape",
            artifact_kind="supplied-artifact",
            path="../outside.txt",
            sha256="0" * 64,
            references=("object_types[title]",),
        )
    with pytest.raises(ValidationError):
        ArtifactLocator(
            artifact_id="duplicates",
            artifact_kind="supplied-artifact",
            path="notes/consumer.txt",
            sha256="0" * 64,
            references=("object_types[title]", "object_types[title]"),
        )


def test_nested_operation_evidence_is_recursively_immutable() -> None:
    operation = _additive_operations(_case()["inputs"]["candidate_model"]["text"])[0]

    with pytest.raises(TypeError, match="immutable"):
        operation.after["name"] = "Mutated"  # type: ignore[index]














@pytest.mark.parametrize(
    "mutation",
    ["rationale", "validation", "cas", "affected-code"],
)
def test_idempotent_finalize_reconstructs_the_complete_record_lineage(
    tmp_path: Path,
    mutation: str,
) -> None:
    from gnd.evolve import EvolutionError, canonical_sha256

    row = _case()
    before = row["inputs"]["before_model"]
    candidate = row["inputs"]["candidate_model"]
    service, _model_path, _verbalization = _service(tmp_path, before["text"])
    proposal = _proposal(candidate["text"], expected_sha256=before["sha256"])
    preview = service.preview(proposal)
    pending = service.apply(preview)
    service.finalize(pending)
    record_path = service.record_path(proposal.proposal_id)
    document = json.loads(record_path.read_text(encoding="utf-8"))
    if mutation == "rationale":
        document["rationale"] += " forged"
    elif mutation == "validation":
        document["validation"]["model_sha256"] = "0" * 64
    elif mutation == "cas":
        document["cas"]["conflict"] = "forged-conflict"
    else:
        document["affected_code"]["ordered_references"] = ["forged-reference"]
    document["record_identity_sha256"] = canonical_sha256(
        {key: value for key, value in document.items() if key != "record_identity_sha256"}
    )
    record_path.write_text(
        json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(EvolutionError, match="reconstructed staged lineage"):
        service.finalize(pending)


def test_project_locator_round_trips_one_closed_base_qualified_coordinate() -> None:
    from gnd.evolve import ProjectLocator

    document = {"base": "allowed-project-root", "path": "project"}
    locator = ProjectLocator.model_validate(document)

    assert locator.model_dump(mode="json") == document
    assert json.loads(locator.model_dump_json()) == document
    with pytest.raises(ValidationError):
        ProjectLocator.model_validate({**document, "operator": "host"})
    with pytest.raises(ValidationError):
        ProjectLocator.model_validate({**document, "base": "workspace"})
    with pytest.raises(ValidationError):
        locator.path = "other"  # type: ignore[misc]


@pytest.mark.parametrize(
    "path",
    [
        "",
        ".",
        "./project",
        "project/.",
        "project//nested",
        "../outside",
        "project/../outside",
        "/absolute",
        "C:/absolute",
        "C:\\absolute",
        "C:relative",
        "\\\\server\\share",
        " project",
        "project ",
        "project\\nested",
        "project\x00nested",
    ],
)
def test_project_locator_rejects_non_normal_or_host_qualified_spelling(path: str) -> None:
    from gnd.evolve import ProjectLocator

    with pytest.raises(ValidationError):
        ProjectLocator(base="allowed-project-root", path=path)






def test_new_proposals_default_to_current_schema_and_require_locator_coordinates() -> None:
    from gnd.evolve import EvolutionProposal, LinkedProject, ProjectLocator, TrackedRoster
    row = _case()
    before = row["inputs"]["before_model"]
    candidate = row["inputs"]["candidate_model"]
    locator = ProjectLocator(base="allowed-project-root", path="project")
    proposal = _proposal(
        candidate["text"],
        expected_sha256=before["sha256"],
        projects=(
            LinkedProject(
                project_id="linked",
                locator=locator,
                tracked_roster=TrackedRoster(),
                expected_tracked_tree_sha256="0" * 64,
            ),
        ),
    )
    assert proposal.schema_version == 3
    assert proposal.linked_projects[0].locator == locator
    with pytest.raises(ValidationError, match="version 3 linked projects require locator"):
        EvolutionProposal(
            proposal_id=proposal.proposal_id,
            expected_model_sha256=proposal.expected_model_sha256,
            candidate_model=proposal.candidate_model,
            operations=proposal.operations,
            rationale=proposal.rationale,
            audit=proposal.audit,
            linked_projects=(
                LinkedProject(
                    project_id="legacy-coordinate",
                    root=Path("project"),
                    expected_tree_sha256="0" * 64,
                ),
            ),
        )






@pytest.mark.parametrize(
    ("subcommand", "required_options"),
    [
        ("preview", ("--workspace", "--records", "--out", "--format")),
        ("apply", ("--preview", "--workspace", "--records", "--format")),
        ("finalize", ("--workspace", "--records", "--format")),
    ],
)
def test_public_evolve_help_exposes_only_the_staged_file_contract(
    capsys: pytest.CaptureFixture[str],
    subcommand: str,
    required_options: tuple[str, ...],
) -> None:
    from gnd.cli import main

    with pytest.raises(SystemExit) as raised:
        main(["evolve", subcommand, "--help"])
    assert raised.value.code == 0
    help_text = capsys.readouterr().out
    for option in required_options:
        assert option in help_text
    for forbidden in ("--provider", "--model-id", "--api-key", "--codegen", "--force"):
        assert forbidden not in help_text


def test_public_additive_preview_apply_finalize_is_exact_and_non_regenerative(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from gnd.cli import main
    from gnd.evolve import EvolutionFinalizationState, EvolutionPreview, EvolutionRecord

    paths = _write_cli_workspace(tmp_path)
    # Records are an independently authoritative argv root, not an implicit
    # child of --workspace. Finalize must bind PENDING beneath this exact root.
    paths["records"] = tmp_path / "evolution-records"
    before_model = paths["model"].read_bytes()
    before_verbalization = paths["verbalization"].read_bytes()
    before_owner_note = (paths["workspace"] / "owner-note.txt").read_bytes()

    def forbidden_codegen(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("the staged evolution CLI must never invoke code generation")

    monkeypatch.setattr("gnd.codegen.emit.emit_project", forbidden_codegen)
    monkeypatch.setattr("gnd.codegen.emit.write_project", forbidden_codegen)

    assert main(_preview_argv(paths)) == 0
    preview_stdout = capsys.readouterr().out
    preview = EvolutionPreview.model_validate_json(preview_stdout)
    assert paths["preview"].read_bytes() == preview_stdout.encode("utf-8")
    assert preview.proposal_sha256 == paths["proposal"].proposal_sha256
    assert paths["model"].read_bytes() == before_model
    assert paths["verbalization"].read_bytes() == before_verbalization
    assert not paths["records"].exists()

    # One command, one whole operation (R-02): apply publishes the model CAS and
    # then completes the verbalization, live conformance, and D-13 record in the
    # same invocation. The two claims stay two payloads (D-24).
    assert main(_apply_argv(paths)) == 0
    apply_stdout = capsys.readouterr().out
    pending_claim, record_claim = _claims(apply_stdout)
    pending = EvolutionFinalizationState.model_validate(pending_claim)
    record = EvolutionRecord.model_validate(record_claim)
    pending_path = paths["records"] / pending.proposal_id / "pending.json"
    record_path = paths["records"] / pending.proposal_id / "record.json"
    assert EvolutionFinalizationState.model_validate_json(pending_path.read_text()) == pending
    assert EvolutionRecord.model_validate_json(record_path.read_text()) == record
    assert record.finalization_state_sha256 == pending.state_identity_sha256
    assert paths["model"].read_bytes() == paths["row"]["inputs"]["candidate_model"][
        "text"
    ].encode("utf-8")
    assert paths["verbalization"].read_bytes() != before_verbalization
    assert paths["verbalization"].read_text(encoding="utf-8") == preview.verbalization.text
    assert main(_apply_argv(paths)) == 0
    assert capsys.readouterr().out == apply_stdout

    # The standalone finalize command survives for exactly one purpose —
    # completing a pending state left behind by an interrupted apply — and stays
    # idempotent over an already completed record.
    assert main(_finalize_argv(paths, pending_path)) == 0
    record_stdout = capsys.readouterr().out
    assert EvolutionRecord.model_validate_json(record_stdout) == record
    assert record.record_identity_sha256
    assert record.conformance_exit_code == 0
    assert record.affected_code.generated_code_written is False
    assert record.affected_code.extension_code_written is False
    assert (paths["workspace"] / "owner-note.txt").read_bytes() == before_owner_note
    record_bytes = record_path.read_bytes()
    assert main(_finalize_argv(paths, pending_path)) == 0
    assert capsys.readouterr().out == record_stdout
    assert record_path.read_bytes() == record_bytes


def test_public_breaking_apply_requires_the_exact_interactive_blast_radius_digest(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from gnd.cli import main
    from gnd.evolve import EvolutionFinalizationState, EvolutionPreview

    wrong = _write_cli_workspace(
        tmp_path / "wrong",
        case_name="evolution-rename-delete-blast-radius",
        breaking=True,
    )
    assert main(_preview_argv(wrong)) == 0
    wrong_preview = EvolutionPreview.model_validate_json(capsys.readouterr().out)
    before_model = wrong["model"].read_bytes()
    monkeypatch.setattr("builtins.input", lambda: "0" * 64)
    assert main(_apply_argv(wrong)) == 11
    failure = capsys.readouterr()
    assert failure.out == ""
    assert "blast radius" in failure.err.lower()
    assert wrong["model"].read_bytes() == before_model
    assert not wrong["records"].exists()

    accepted = _write_cli_workspace(
        tmp_path / "accepted",
        case_name="evolution-rename-delete-blast-radius",
        breaking=True,
    )
    assert main(_preview_argv(accepted)) == 0
    accepted_preview = EvolutionPreview.model_validate_json(capsys.readouterr().out)
    monkeypatch.setattr(
        "builtins.input", lambda: accepted_preview.blast_radius.report_sha256
    )
    assert main(_apply_argv(accepted)) == 0
    accepted_stdout = capsys.readouterr().out
    pending = EvolutionFinalizationState.model_validate(_claims(accepted_stdout)[0])
    assert pending.preview_sha256 != wrong_preview.preview_sha256
    staged_preview = EvolutionPreview.model_validate_json(
        (
            accepted["records"] / accepted["proposal"].proposal_id / "preview.json"
        ).read_text(encoding="utf-8")
    )
    assert (
        staged_preview.accepted_blast_radius_sha256
        == staged_preview.blast_radius.report_sha256
    )

    def forbidden_second_prompt() -> str:
        raise AssertionError("an exact post-CAS retry must reuse durable acceptance")

    monkeypatch.setattr("builtins.input", forbidden_second_prompt)
    assert main(_apply_argv(accepted)) == 0
    assert capsys.readouterr().out == accepted_stdout

    staged_preview_path = (
        accepted["records"] / accepted["proposal"].proposal_id / "preview.json"
    )
    staged_preview_path.write_bytes(accepted["preview"].read_bytes())
    assert main(_apply_argv(accepted)) == 11
    assert capsys.readouterr().out == ""


def test_public_apply_refuses_stale_model_and_differing_preview_output_without_mutation(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from gnd.cli import main

    stale = _write_cli_workspace(tmp_path / "stale")
    assert main(_preview_argv(stale)) == 0
    capsys.readouterr()
    concurrent = stale["model"].read_bytes() + b"\n# concurrent owner edit\n"
    stale["model"].write_bytes(concurrent)
    assert main(_apply_argv(stale)) == 11
    assert capsys.readouterr().out == ""
    assert stale["model"].read_bytes() == concurrent
    assert not stale["records"].exists()

    collision = _write_cli_workspace(tmp_path / "collision")
    collision["preview"].parent.mkdir(parents=True)
    collision["preview"].write_text("owner bytes\n", encoding="utf-8")
    before_model = collision["model"].read_bytes()
    assert main(_preview_argv(collision)) == 11
    assert capsys.readouterr().out == ""
    assert collision["preview"].read_text(encoding="utf-8") == "owner bytes\n"
    assert collision["model"].read_bytes() == before_model


def test_public_preview_collision_reader_refuses_a_leaf_swap(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import gnd.artifacts as artifact_module
    from gnd.cli import main

    paths = _write_cli_workspace(tmp_path)
    assert main(_preview_argv(paths)) == 0
    capsys.readouterr()
    outside = tmp_path / "outside-preview.json"
    outside.write_bytes(paths["preview"].read_bytes())
    parent_inode = paths["preview"].parent.stat().st_ino
    real_open = artifact_module.os.open
    injected = False

    def swap_preview(path: Any, flags: int, *args: Any, **kwargs: Any) -> int:
        nonlocal injected
        if (
            not injected
            and path == paths["preview"].name
            and kwargs.get("dir_fd") is not None
            and os.fstat(kwargs["dir_fd"]).st_ino == parent_inode
            and not flags & getattr(os, "O_DIRECTORY", 0)
        ):
            injected = True
            paths["preview"].unlink()
            paths["preview"].symlink_to(outside)
        return real_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(artifact_module.os, "open", swap_preview)

    assert main(_preview_argv(paths)) == 74
    assert capsys.readouterr().out == ""
    assert injected is True
    assert paths["preview"].is_symlink()
    assert not paths["records"].exists()


@pytest.mark.parametrize("stage", ["proposal", "preview", "pending"])
def test_public_evolve_malformed_documents_exit_three_without_mutation(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    stage: str,
) -> None:
    from gnd.cli import main

    paths = _write_cli_workspace(tmp_path)
    before_model = paths["model"].read_bytes()
    if stage == "proposal":
        paths["proposal_path"].write_text("{not-json\n", encoding="utf-8")
        argv = _preview_argv(paths)
    elif stage == "preview":
        paths["preview"].parent.mkdir(parents=True)
        paths["preview"].write_text("{}\n", encoding="utf-8")
        argv = _apply_argv(paths)
    else:
        pending = paths["records"] / "malformed" / "pending.json"
        pending.parent.mkdir(parents=True)
        pending.write_text("[]\n", encoding="utf-8")
        argv = _finalize_argv(paths, pending)
    assert main(argv) == 3
    assert capsys.readouterr().out == ""
    assert paths["model"].read_bytes() == before_model
    if stage == "pending":
        assert set(paths["records"].rglob("*")) == {pending.parent, pending}
    else:
        assert not paths["records"].exists()


def test_public_evolve_missing_and_unsafe_paths_are_disjoint_and_write_nothing(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from gnd.cli import main

    missing = _write_cli_workspace(tmp_path / "missing")
    missing["proposal_path"].unlink()
    before_model = missing["model"].read_bytes()
    assert main(_preview_argv(missing)) == 66
    assert capsys.readouterr().out == ""
    assert missing["model"].read_bytes() == before_model
    assert not missing["preview"].exists()

    unsafe = _write_cli_workspace(tmp_path / "unsafe")
    outside = tmp_path / "outside-proposal.json"
    outside.write_bytes(unsafe["proposal_path"].read_bytes())
    unsafe["proposal_path"] = outside
    before_workspace = _tree_sha256(unsafe["workspace"])
    assert main(_preview_argv(unsafe)) == 74
    assert capsys.readouterr().out == ""
    assert _tree_sha256(unsafe["workspace"]) == before_workspace

    symlinked = _write_cli_workspace(tmp_path / "symlinked")
    target = symlinked["workspace"] / "proposal-target.json"
    target.write_bytes(symlinked["proposal_path"].read_bytes())
    symlinked["proposal_path"].unlink()
    symlinked["proposal_path"].symlink_to(target)
    before_model = symlinked["model"].read_bytes()
    assert main(_preview_argv(symlinked)) == 74
    assert capsys.readouterr().out == ""
    assert symlinked["model"].read_bytes() == before_model
    assert not symlinked["preview"].exists()


@pytest.mark.parametrize("stage", ["preview", "apply", "finalize"])
@pytest.mark.parametrize("attack", ["intermediate", "leaf"])
def test_public_evolve_claim_reads_refuse_component_and_leaf_swaps(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    stage: str,
    attack: str,
) -> None:
    import gnd.artifacts as artifact_module
    from gnd.cli import main
    from gnd.evolve import EvolutionService

    paths = _write_cli_workspace(tmp_path / "case")
    if stage == "preview":
        claims = paths["workspace"] / "claims"
        claims.mkdir()
        relocated = claims / "proposal.json"
        paths["proposal_path"].rename(relocated)
        paths["proposal_path"] = relocated
        target = relocated
        argv = _preview_argv(paths)
    elif stage == "apply":
        assert main(_preview_argv(paths)) == 0
        capsys.readouterr()
        target = paths["preview"]
        argv = _apply_argv(paths)
    else:
        service = EvolutionService(
            model_path=paths["model"],
            evidence_root=paths["records"],
            verbalization_path=paths["verbalization"],
            allowed_project_root=paths["workspace"],
        )
        preview = service.preview(paths["proposal"])
        pending = service.apply(preview)
        target = paths["records"] / pending.proposal_id / "pending.json"
        argv = _finalize_argv(paths, target)

    outside_parent = tmp_path / f"outside-{stage}-{attack}"
    outside_parent.mkdir()
    outside_leaf = outside_parent / target.name
    outside_leaf.write_bytes(target.read_bytes())
    before_model = paths["model"].read_bytes()
    real_open = artifact_module.os.open
    injected = False

    if attack == "intermediate":
        victim_parent = target.parent
        trusted_parent = victim_parent.parent
        victim_inode = trusted_parent.stat().st_ino
        displaced = trusted_parent / f"displaced-{victim_parent.name}"

        def swap_claim(path: Any, flags: int, *args: Any, **kwargs: Any) -> int:
            nonlocal injected
            if (
                not injected
                and path == victim_parent.name
                and kwargs.get("dir_fd") is not None
                and os.fstat(kwargs["dir_fd"]).st_ino == victim_inode
                and flags & getattr(os, "O_DIRECTORY", 0)
            ):
                injected = True
                victim_parent.rename(displaced)
                victim_parent.symlink_to(outside_parent, target_is_directory=True)
            return real_open(path, flags, *args, **kwargs)

    else:
        parent_inode = target.parent.stat().st_ino

        def swap_claim(path: Any, flags: int, *args: Any, **kwargs: Any) -> int:
            nonlocal injected
            if (
                not injected
                and path == target.name
                and kwargs.get("dir_fd") is not None
                and os.fstat(kwargs["dir_fd"]).st_ino == parent_inode
                and not flags & getattr(os, "O_DIRECTORY", 0)
            ):
                injected = True
                target.unlink()
                target.symlink_to(outside_leaf)
            return real_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(artifact_module.os, "open", swap_claim)

    assert main(argv) == 74
    output = capsys.readouterr()
    assert output.out == ""
    assert injected is True
    assert paths["model"].read_bytes() == before_model
    assert outside_leaf.read_bytes()
    if stage == "preview":
        assert not paths["preview"].exists()
        assert not paths["records"].exists()
    elif stage == "apply":
        assert not paths["records"].exists()
    else:
        record = paths["records"] / paths["proposal"].proposal_id / "record.json"
        assert not record.exists()


@pytest.mark.parametrize("semantic_error", ["candidate-media-type", "d12-lifecycle"])
def test_public_evolve_semantically_malformed_requests_exit_three(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    semantic_error: str,
) -> None:
    from gnd.cli import main

    paths = _write_cli_workspace(tmp_path)
    proposal = paths["proposal"].model_dump(mode="json")
    if semantic_error == "candidate-media-type":
        proposal["candidate_model"]["media_type"] = "application/json"
    else:
        candidate = _parse(paths["row"]["inputs"]["candidate_model"]["text"])
        candidate["fact_types"][-1]["constraints"][0]["status"] = "confirmed"
        candidate_text = _canonical_model_text(candidate)
        proposal = _proposal(
            candidate_text,
            expected_sha256=paths["row"]["inputs"]["before_model"]["sha256"],
        ).model_dump(mode="json")
    paths["proposal_path"].write_text(
        json.dumps(proposal, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    before_model = paths["model"].read_bytes()
    assert main(_preview_argv(paths)) == 3
    assert capsys.readouterr().out == ""
    assert paths["model"].read_bytes() == before_model
    assert not paths["preview"].exists()
    assert not paths["records"].exists()


def test_public_evolve_internal_defect_is_exit_seventy_without_publication(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from gnd.cli import main

    paths = _write_cli_workspace(tmp_path)
    before_model = paths["model"].read_bytes()

    def internal_defect(*_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("simulated internal invariant failure")

    monkeypatch.setattr("gnd.evolve.EvolutionService.preview", internal_defect)
    assert main(_preview_argv(paths)) == 70
    output = capsys.readouterr()
    assert output.out == ""
    assert "(70)" in output.err
    assert paths["model"].read_bytes() == before_model
    assert not paths["preview"].exists()
    assert not paths["records"].exists()


def test_public_finalize_preserves_raw_linked_drift_exit_and_project_bytes(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from gnd.cli import main
    from gnd.codegen.emit import emit_project, write_project
    from gnd.codegen.manifest import build_manifest, read_manifest, render_manifest
    from gnd.evolve import (
        EvolutionFinalizationState,
        EvolutionRecord,
        ProjectLocator,
    )
    from gnd.model import load_model

    row = _case("evolution-clean-and-drift-linked-conformance")
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    candidate_path = workspace / "candidate.orm.yaml"
    candidate_path.write_text(row["inputs"]["candidate_model"]["text"], encoding="utf-8")
    project_root = workspace / "linked-project"
    generated = emit_project(
        load_model(candidate_path),
        str(candidate_path),
        skill_name=project_root.name,
    )
    write_project(
        generated,
        str(project_root),
        manifest_text=render_manifest(build_manifest(generated, str(candidate_path))),
    )
    manifest = read_manifest(project_root / ".gnd-codegen.json")
    derived = next(item for item in manifest.files if item.ownership == "derived")
    derived_path = project_root / derived.relpath
    derived_path.write_bytes(derived_path.read_bytes() + b"\n# deliberate drift\n")
    project = _linked_v3(
        "drift",
        project_root,
        locator=ProjectLocator(base="allowed-project-root", path="linked-project"),
    )
    paths = _write_cli_workspace(
        tmp_path,
        case_name="evolution-clean-and-drift-linked-conformance",
        projects=(project,),
        proposal_id="proposal-linked-drift",
    )

    def forbidden_codegen(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("evolution must not regenerate linked projects")

    monkeypatch.setattr("gnd.codegen.emit.emit_project", forbidden_codegen)
    monkeypatch.setattr("gnd.codegen.emit.write_project", forbidden_codegen)

    assert main(_preview_argv(paths)) == 0
    capsys.readouterr()
    # Apply now returns the raw aggregate conformance exit finalize returns, and
    # the model stays published: D-11 forbids rollback, so drift is a published
    # model with a reported problem rather than a failed apply.
    assert main(_apply_argv(paths)) == 13
    apply_output = capsys.readouterr()
    pending_claim, record_claim = _claims(apply_output.out)
    pending = EvolutionFinalizationState.model_validate(pending_claim)
    record = EvolutionRecord.model_validate(record_claim)
    assert record.conformance_exit_code == 13
    assert record.published_with_drift is True
    assert "success" not in apply_output.out.lower()
    assert paths["model"].read_bytes() == row["inputs"]["candidate_model"]["text"].encode(
        "utf-8"
    )
    pending_path = paths["records"] / pending.proposal_id / "pending.json"
    assert main(_finalize_argv(paths, pending_path)) == 13
    output = capsys.readouterr()
    assert EvolutionRecord.model_validate_json(output.out) == record
    assert "success" not in output.out.lower()
    assert _linked_v3("drift", project_root, locator=project.locator) == project
