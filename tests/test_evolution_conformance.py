"""Live linked-project conformance contract for published evolution."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML

from gnd.codegen.emit import emit_project, write_project
from gnd.codegen.manifest import build_manifest, read_manifest, render_manifest
from gnd.conformance.report import canonical
from gnd.model import load_model

REPO_ROOT = Path(__file__).resolve().parent.parent
EVOLUTION_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "phase4_reference" / "evolution.json"


def _case() -> dict[str, Any]:
    fixture = json.loads(EVOLUTION_FIXTURE.read_text(encoding="utf-8"))
    return next(
        row
        for row in fixture["cases"]
        if row["name"] == "evolution-clean-and-drift-linked-conformance"
    )


def _tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relpath = path.relative_to(root).as_posix().encode("utf-8")
        if path.is_symlink():
            digest.update(b"L\0" + relpath + b"\0" + path.readlink().as_posix().encode("utf-8"))
        elif path.is_file():
            digest.update(b"F\0" + relpath + b"\0" + path.read_bytes())
        elif path.is_dir():
            digest.update(b"D\0" + relpath + b"\0")
    return digest.hexdigest()
def _roster(root: Path) -> dict[str, Any]:
    """Identity fields for every leaf; production derives none, so a test does."""
    from gnd.artifacts import snapshot_tracked_roster
    from gnd.evolve import TrackedRoster
    leaves = (item for item in root.rglob("*") if item.is_symlink() or item.is_file())
    paths = tuple(sorted(item.relative_to(root).as_posix() for item in leaves))
    return {
        "tracked_roster": TrackedRoster(paths=paths),
        "expected_tracked_tree_sha256": snapshot_tracked_roster(root, paths, label="linked")[1],
    }


def _generated_project(model_path: Path, root: Path) -> None:
    model = load_model(str(model_path))
    project = emit_project(model, str(model_path), skill_name=root.name)
    write_project(
        project,
        str(root),
        manifest_text=render_manifest(build_manifest(project, str(model_path))),
    )


def _proposal(candidate_text: str, before_sha256: str, projects: tuple[Any, ...]) -> Any:
    from gnd.evolve import (
        EVOLUTION_SCHEMA_VERSION,
        CommittedText,
        ElementLocator,
        EvolutionOperation,
        EvolutionOperationAudit,
        EvolutionOperationKind,
        EvolutionProposal,
    )

    candidate = YAML(typ="safe").load(candidate_text)
    priority = next(item for item in candidate["object_types"] if item["id"] == "priority")
    fact = next(item for item in candidate["fact_types"] if item["id"] == "work_item_has_priority")
    return EvolutionProposal(
        schema_version=EVOLUTION_SCHEMA_VERSION,
        proposal_id="proposal-linked-conformance",
        expected_model_sha256=before_sha256,
        candidate_model=CommittedText.from_text(candidate_text, media_type="application/yaml"),
        operations=(
            EvolutionOperation(
                operation_id="add-priority-type",
                kind=EvolutionOperationKind.ADD,
                locator=ElementLocator(collection="object_types", element_id="priority"),
                after=priority,
            ),
            EvolutionOperation(
                operation_id="add-priority-fact",
                kind=EvolutionOperationKind.ADD,
                locator=ElementLocator(
                    collection="fact_types", element_id="work_item_has_priority"
                ),
                after=fact,
            ),
        ),
        rationale="Publish a valid additive model and inspect only explicitly linked projects.",
        audit=EvolutionOperationAudit(
            actor_id="owner:fixture",
            origin="phase4-reference-test",
            requested_at=datetime(2026, 8, 13, 12, 0, tzinfo=UTC),
        ),
        linked_projects=projects,
    )


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


def _json_strings(value: Any, *, json_path: str = "$") -> list[tuple[str, str]]:
    strings: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, item in value.items():
            strings.append((f"{json_path}.<key>", str(key)))
            strings.extend(_json_strings(item, json_path=f"{json_path}.{key}"))
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            strings.extend(_json_strings(item, json_path=f"{json_path}[{index}]"))
    elif isinstance(value, str):
        strings.append((json_path, value))
    return strings


def _assert_operator_neutral(value: Any, *, paths: dict[str, Any]) -> None:
    forbidden = {
        str(paths["workspace"].resolve()),
        str(paths["project_root"].resolve()),
        "HOME-PREFIX-SENTINEL",
        "USERNAME-SENTINEL",
        "OPERATOR-HOST-SENTINEL",
    }
    strings = _json_strings(value)
    leaks = [
        (json_path, text, token)
        for json_path, text in strings
        for token in forbidden
        if token in text
    ]
    assert leaks == []
    root_keys = [json_path for json_path, text in strings if text == "root"]
    assert root_keys == []


def _cli_workspace(tmp_path: Path, *, drift: bool = False) -> dict[str, Any]:
    """One workspace-relative evolution request with exactly one linked project."""

    from gnd.evolve import LinkedProject, ProjectLocator

    row = _case()
    before = row["inputs"]["before_model"]
    candidate = row["inputs"]["candidate_model"]
    workspace = (
        tmp_path
        / "HOME-PREFIX-SENTINEL"
        / "USERNAME-SENTINEL"
        / "OPERATOR-HOST-SENTINEL"
        / "workspace"
    )
    workspace.mkdir(parents=True, exist_ok=True)
    model_path = workspace / "model.orm.yaml"
    model_path.write_text(before["text"], encoding="utf-8")
    verbalization_path = workspace / "model.verbalization.txt"
    verbalization_path.write_text("pre-existing verbalization\n", encoding="utf-8")
    candidate_path = workspace / "candidate.orm.yaml"
    candidate_path.write_text(candidate["text"], encoding="utf-8")
    project_root = workspace / "linked-project"
    _generated_project(candidate_path, project_root)
    if drift:
        manifest = read_manifest(project_root / ".gnd-codegen.json")
        entry = next(item for item in manifest.files if item.ownership == "derived")
        derived_path = project_root / entry.relpath
        derived_path.write_bytes(derived_path.read_bytes() + b"\n# deliberate drift\n")
    project = LinkedProject(
        project_id="linked",
        locator=ProjectLocator(
            base="allowed-project-root",
            path="linked-project",
        ),
        **_roster(project_root),
    )
    proposal = _proposal(candidate["text"], before["sha256"], (project,))
    proposal_path = workspace / "proposal.json"
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
        "preview": workspace / "review" / "preview.json",
        "records": workspace / "records",
        "project_root": project_root,
        "project_tree": _tree_sha256(project_root),
        "project_roster": project.expected_tracked_tree_sha256,
        "candidate_bytes": candidate["text"].encode("utf-8"),
    }


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


def _forbid_codegen(monkeypatch: Any) -> None:
    def forbidden(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("evolution must never invoke code generation")

    monkeypatch.setattr("gnd.codegen.emit.emit_project", forbidden)
    monkeypatch.setattr("gnd.codegen.emit.write_project", forbidden)


def test_apply_publishes_and_rechecks_conformance_in_one_command(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: Any,
) -> None:
    """MODEL-02's downstream recheck runs because publication and recheck are one command.

    R-02 found that ``run_conformance`` had one call site, inside ``finalize``,
    while ``apply`` and ``finalize`` were separate user-facing subcommands. This
    is the receipt that a single public ``gnd evolve apply`` invocation leaves
    both the live conformance envelope and the D-13 record behind.
    """

    from gnd.cli import main
    from gnd.evolve import EvolutionFinalizationState, EvolutionRecord

    paths = _cli_workspace(tmp_path)
    _forbid_codegen(monkeypatch)

    assert main(_preview_argv(paths)) == 0
    capsys.readouterr()

    assert main(_apply_argv(paths)) == 0
    claims = _claims(capsys.readouterr().out)
    assert len(claims) == 2, "publication and conformance stay two payloads (D-24)"
    pending = EvolutionFinalizationState.model_validate(claims[0])
    record = EvolutionRecord.model_validate(claims[1])

    proposal_dir = paths["records"] / pending.proposal_id
    assert (proposal_dir / "record.json").is_file()
    assert (proposal_dir / "conformance" / "linked.json").is_file()
    assert EvolutionRecord.model_validate_json(
        (proposal_dir / "record.json").read_text(encoding="utf-8")
    ) == record
    assert record.finalization_state_sha256 == pending.state_identity_sha256
    assert [item.exit_code for item in record.linked_conformance] == [0]
    assert record.conformance_exit_code == 0
    assert record.published_with_drift is False
    assert record.affected_code.generated_code_written is False
    assert paths["model"].read_bytes() == paths["candidate_bytes"]
    assert _tree_sha256(paths["project_root"]) == paths["project_tree"]

    evidence_paths = (
        paths["proposal_path"],
        paths["preview"],
        proposal_dir / "proposal.json",
        proposal_dir / "intent.json",
        proposal_dir / "conformance" / "linked.json",
        proposal_dir / "record.json",
    )
    documents = {path.name: json.loads(path.read_text(encoding="utf-8")) for path in evidence_paths}
    for document in documents.values():
        _assert_operator_neutral(document, paths=paths)
    assert documents["proposal.json"]["schema_version"] == 3
    assert documents["preview.json"]["schema_version"] == 3
    assert documents["intent.json"]["schema_version"] == 3
    assert documents["record.json"]["schema_version"] == 3
    assert documents["proposal.json"]["linked_projects"][0]["locator"] == {
        "base": "allowed-project-root",
        "path": "linked-project",
    }
    assert documents["intent.json"]["linked_projects"][0]["locator"] == {
        "base": "allowed-project-root",
        "path": "linked-project",
    }
    assert documents["linked.json"]["locator"] == {
        "base": "allowed-project-root",
        "path": "linked-project",
    }
    assert documents["record.json"]["linked_conformance"][0]["locator"] == {
        "base": "allowed-project-root",
        "path": "linked-project",
    }
    assert pending.schema_version == 3
    assert pending.intent_sha256 == hashlib.sha256(
        (proposal_dir / "intent.json").read_bytes()
    ).hexdigest()


def test_apply_returns_the_raw_aggregate_conformance_exit_for_a_drifted_project(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: Any,
) -> None:
    """Drift is a published model with a reported problem, not a failed apply (D-11)."""

    from gnd import cli
    from gnd.cli import main
    from gnd.evolve import EvolutionFinalizationState, EvolutionRecord

    paths = _cli_workspace(tmp_path, drift=True)
    _forbid_codegen(monkeypatch)

    assert main(_preview_argv(paths)) == 0
    capsys.readouterr()

    assert main(_apply_argv(paths)) == cli.EXIT_MODEL_CODE_DRIFT
    claims = _claims(capsys.readouterr().out)
    pending = EvolutionFinalizationState.model_validate(claims[0])
    record = EvolutionRecord.model_validate(claims[1])
    assert record.conformance_exit_code == cli.EXIT_MODEL_CODE_DRIFT
    assert record.published_with_drift is True
    assert paths["model"].read_bytes() == paths["candidate_bytes"], "no rollback (D-11)"
    assert _tree_sha256(paths["project_root"]) == paths["project_tree"]

    pending_path = paths["records"] / pending.proposal_id / "pending.json"
    assert main(_finalize_argv(paths, pending_path)) == cli.EXIT_MODEL_CODE_DRIFT
    assert EvolutionRecord.model_validate_json(capsys.readouterr().out) == record


def test_apply_retains_supported_io_exit_in_operator_neutral_evidence(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: Any,
) -> None:
    from gnd.cli import EXIT_IO, main
    from gnd.conformance import ConformanceError
    from gnd.evolve import EvolutionFinalizationState, EvolutionRecord

    paths = _cli_workspace(tmp_path)
    _forbid_codegen(monkeypatch)

    def unreadable_integrity(*_args: Any, **_kwargs: Any) -> None:
        raise ConformanceError("file-io for generated/linked_tools.py")

    monkeypatch.setattr(
        "gnd.conformance.service.check_integrity",
        unreadable_integrity,
    )

    assert main(_preview_argv(paths)) == 0
    capsys.readouterr()
    assert main(_apply_argv(paths)) == EXIT_IO
    pending_claim, record_claim = _claims(capsys.readouterr().out)
    pending = EvolutionFinalizationState.model_validate(pending_claim)
    record = EvolutionRecord.model_validate(record_claim)
    proposal_dir = paths["records"] / pending.proposal_id
    conformance_document = json.loads(
        (proposal_dir / "conformance" / "linked.json").read_text(encoding="utf-8")
    )
    record_document = json.loads(
        (proposal_dir / "record.json").read_text(encoding="utf-8")
    )

    assert record.conformance_exit_code == EXIT_IO
    assert record.linked_conformance[0].exit_code == EXIT_IO
    assert (
        record.linked_conformance[0].model_dump(mode="json")["payload"]
        == conformance_document["payload"]
    )
    assert record.linked_conformance[0].payload_sha256 == hashlib.sha256(
        canonical(conformance_document["payload"]).encode("utf-8")
    ).hexdigest()
    assert record.affected_code.generated_code_written is False
    assert record.affected_code.extension_code_written is False
    assert paths["model"].read_bytes() == paths["candidate_bytes"]
    assert _tree_sha256(paths["project_root"]) == paths["project_tree"]
    assert record_document["linked_conformance"] == [conformance_document]
    _assert_operator_neutral(conformance_document, paths=paths)
    _assert_operator_neutral(record_document, paths=paths)

    pending_path = proposal_dir / "pending.json"
    assert main(_finalize_argv(paths, pending_path)) == EXIT_IO
    assert EvolutionRecord.model_validate_json(capsys.readouterr().out) == record


def test_final_rebind_mutation_never_publishes_a_green_linked_envelope(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from gnd.conformance import service as conformance_service
    from gnd.evolve import EvolutionError, EvolutionService
    from gnd.evolve import service as evolution_service

    paths = _cli_workspace(tmp_path)
    service = EvolutionService(
        model_path=paths["model"],
        evidence_root=paths["records"],
        verbalization_path=paths["verbalization"],
        allowed_project_root=paths["workspace"],
    )
    preview = service.preview(paths["proposal"])
    pending = service.apply(preview)
    manifest = read_manifest(paths["project_root"] / ".gnd-codegen.json")
    target = next(
        entry.relpath
        for entry in manifest.files
        if entry.ownership == "derived" and entry.relpath.endswith("/tools.py")
    )
    real_bind = conformance_service.bind_project_root
    real_run = evolution_service.run_conformance
    captured_exits: list[int] = []
    injected = False

    def mutate_after_rebind(*args: Any, **kwargs: Any) -> tuple[int, int]:
        nonlocal injected
        identity = real_bind(*args, **kwargs)
        if not injected:
            injected = True
            leaf = paths["project_root"] / target
            leaf.write_bytes(leaf.read_bytes() + b"\n# mutation at final rebind\n")
        return identity

    def capture_run(*args: Any, **kwargs: Any):
        result = real_run(*args, **kwargs)
        captured_exits.append(result.exit_code)
        return result

    monkeypatch.setattr(conformance_service, "bind_project_root", mutate_after_rebind)
    monkeypatch.setattr(evolution_service, "run_conformance", capture_run)

    with pytest.raises(EvolutionError, match="changed during conformance"):
        service.finalize(pending)

    proposal_dir = paths["records"] / pending.proposal_id
    assert injected is True
    assert captured_exits and captured_exits[-1] in {13, 74}
    assert not (proposal_dir / "conformance" / "linked.json").exists()
    assert not (proposal_dir / "record.json").exists()


def test_public_apply_emits_operator_neutral_evidence_for_clean_drift_and_error_paths(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: Any,
) -> None:
    """The public workflow retains stable coordinates for every supported outcome."""

    from gnd.cli import EXIT_IO, EXIT_MODEL_CODE_DRIFT, main
    from gnd.conformance import ConformanceError
    from gnd.evolve import EvolutionFinalizationState, EvolutionRecord

    workflows = {
        "clean": _cli_workspace(tmp_path / "clean"),
        "drift": _cli_workspace(tmp_path / "drift", drift=True),
        "error": _cli_workspace(tmp_path / "error"),
    }
    _forbid_codegen(monkeypatch)

    expected_exits = {
        "clean": 0,
        "drift": EXIT_MODEL_CODE_DRIFT,
        "error": EXIT_IO,
    }
    results: dict[str, tuple[EvolutionFinalizationState, EvolutionRecord]] = {}

    for outcome in ("clean", "drift"):
        paths = workflows[outcome]
        assert main(_preview_argv(paths)) == 0
        capsys.readouterr()
        assert main(_apply_argv(paths)) == expected_exits[outcome]
        pending_claim, record_claim = _claims(capsys.readouterr().out)
        results[outcome] = (
            EvolutionFinalizationState.model_validate(pending_claim),
            EvolutionRecord.model_validate(record_claim),
        )

    def unreadable_integrity(*_args: Any, **_kwargs: Any) -> None:
        raise ConformanceError("file-io for generated/linked_tools.py")

    monkeypatch.setattr("gnd.conformance.service.check_integrity", unreadable_integrity)
    error_paths = workflows["error"]
    assert main(_preview_argv(error_paths)) == 0
    capsys.readouterr()
    assert main(_apply_argv(error_paths)) == EXIT_IO
    pending_claim, record_claim = _claims(capsys.readouterr().out)
    results["error"] = (
        EvolutionFinalizationState.model_validate(pending_claim),
        EvolutionRecord.model_validate(record_claim),
    )

    for outcome, paths in workflows.items():
        pending, record = results[outcome]
        proposal_dir = paths["records"] / pending.proposal_id
        family_paths = {
            "proposal": proposal_dir / "proposal.json",
            "preview": proposal_dir / "preview.json",
            "intent": proposal_dir / "intent.json",
            "record": proposal_dir / "record.json",
        }
        conformance_paths = tuple(sorted((proposal_dir / "conformance").glob("*.json")))
        assert len(conformance_paths) == 1
        documents = {
            family: json.loads(path.read_text(encoding="utf-8"))
            for family, path in family_paths.items()
        }
        documents["conformance"] = json.loads(
            conformance_paths[0].read_text(encoding="utf-8")
        )

        for family, document in documents.items():
            _assert_operator_neutral(document, paths=paths)
            strings = _json_strings(document)
            assert not [
                (json_path, text)
                for json_path, text in strings
                if text in {"$HOME", "$USER"}
                or text.startswith(str(Path.home()))
                or (
                    Path.home().name
                    and Path.home().name in text
                    and "USERNAME-SENTINEL" not in text
                )
            ], family

        locator = {
            "base": "allowed-project-root",
            "path": "linked-project",
        }
        assert documents["proposal"]["schema_version"] == 3
        assert documents["preview"]["schema_version"] == 3
        assert documents["intent"]["schema_version"] == 3
        assert documents["record"]["schema_version"] == 3
        assert documents["proposal"]["linked_projects"][0]["locator"] == locator
        assert documents["preview"]["proposal"]["linked_projects"][0]["locator"] == locator
        assert documents["intent"]["linked_projects"][0]["locator"] == locator
        assert documents["conformance"]["locator"] == locator
        assert documents["record"]["linked_conformance"][0]["locator"] == locator

        conformance = documents["conformance"]
        assert conformance["exit_code"] == expected_exits[outcome]
        assert conformance["before_tracked_tree_sha256"] == paths["project_roster"]
        assert conformance["after_tracked_tree_sha256"] == paths["project_roster"]
        assert conformance["payload_sha256"] == hashlib.sha256(
            canonical(conformance["payload"]).encode("utf-8")
        ).hexdigest()
        assert documents["record"]["linked_conformance"] == [conformance]
        assert (
            record.linked_conformance[0].model_dump(mode="json")["payload"]
            == conformance["payload"]
        )
        assert record.finalization_state_sha256 == pending.state_identity_sha256
        assert record.conformance_exit_code == expected_exits[outcome]
        assert record.published_with_drift is (outcome == "drift")
        assert record.affected_code.generated_code_written is False
        assert record.affected_code.extension_code_written is False
        assert paths["model"].read_bytes() == paths["candidate_bytes"]
        assert _tree_sha256(paths["project_root"]) == paths["project_tree"]

        findings = conformance["payload"]["findings"]
        if outcome == "drift":
            assert findings
            assert all(not Path(item["target"]).is_absolute() for item in findings)
        elif outcome == "clean":
            assert findings == []
            assert conformance["payload"]["error"] is None
        else:
            assert conformance["payload"]["error"] == (
                "the generated project integrity assertion could not run "
                "(cause: file-io)"
            )


def test_a_pending_finalization_blocks_a_new_evolution(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: Any,
) -> None:
    """A published model with no completed record must not read as healthy.

    The chained apply still has an interruptible window between the model CAS
    and record publication. A pending state left in that window blocks the next
    evolution rather than being inherited in silence, on BOTH apply paths — the
    fresh-preview path and the candidate-already-live retry path, which never
    calls ``service.preview`` and is exactly the branch a user reaches after an
    interrupted apply. D-11 governs: the state is reported, never completed,
    repaired, or rolled back by the refusing command.
    """

    from gnd import cli
    from gnd.cli import EXIT_COLLISION, main
    from gnd.evolve import EvolutionPreview, EvolutionService

    paths = _cli_workspace(tmp_path)
    _forbid_codegen(monkeypatch)
    assert main(_preview_argv(paths)) == 0
    capsys.readouterr()

    # A second, distinct evolution reviewed while the first is still healthy.
    second = json.loads(paths["proposal_path"].read_text(encoding="utf-8"))
    second["proposal_id"] = "proposal-second-evolution"
    second_path = paths["workspace"] / "second.proposal.json"
    second_path.write_text(
        json.dumps(second, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    second_preview = paths["workspace"] / "review" / "second.preview.json"
    second_preview_argv = [
        "evolve",
        "preview",
        str(paths["model"]),
        str(second_path),
        "--workspace",
        str(paths["workspace"]),
        "--records",
        str(paths["records"]),
        "--out",
        str(second_preview),
        "--format",
        "json",
    ]
    second_apply_argv = [
        "evolve",
        "apply",
        str(paths["model"]),
        str(second_path),
        "--preview",
        str(second_preview),
        "--workspace",
        str(paths["workspace"]),
        "--records",
        str(paths["records"]),
        "--format",
        "json",
    ]
    assert main(second_preview_argv) == 0
    capsys.readouterr()

    # Simulate the crash window: the API-level apply publishes the model CAS and
    # returns before any recheck. This is deliberately the unguaranteed path.
    service = EvolutionService(
        model_path=paths["model"],
        evidence_root=paths["records"],
        allowed_project_root=paths["workspace"],
    )
    staged = EvolutionPreview.model_validate_json(
        paths["preview"].read_text(encoding="utf-8")
    )
    pending = service.apply(staged)
    assert paths["model"].read_bytes() == paths["candidate_bytes"]
    assert not (paths["records"] / pending.proposal_id / "record.json").exists()
    workspace_before = _tree_sha256(paths["workspace"])

    assert main(second_preview_argv) == EXIT_COLLISION
    refused = capsys.readouterr()
    assert refused.out == ""
    assert pending.proposal_id in refused.err
    assert "finalize" in refused.err
    assert not (paths["records"] / "proposal-second-evolution").exists()
    assert _tree_sha256(paths["workspace"]) == workspace_before

    # The retry branch: the model on disk already equals this candidate, so the
    # command would go straight to `service.apply` without previewing. The
    # refusal is installed ahead of the branch split for exactly that reason.
    previewed: list[Any] = []
    real_preview = EvolutionService.preview

    def spy(self: Any, *args: Any, **kwargs: Any) -> Any:
        previewed.append(args)
        return real_preview(self, *args, **kwargs)

    monkeypatch.setattr("gnd.evolve.EvolutionService.preview", spy)
    assert main(second_apply_argv) == EXIT_COLLISION
    refused_apply = capsys.readouterr()
    assert refused_apply.out == ""
    assert pending.proposal_id in refused_apply.err
    assert "finalize" in refused_apply.err
    assert previewed == [], "the candidate-already-live retry branch never previews"
    assert not (paths["records"] / "proposal-second-evolution").exists()
    assert _tree_sha256(paths["workspace"]) == workspace_before
    assert paths["model"].read_bytes() == paths["candidate_bytes"], "no rollback (D-11)"

    # Control: the refusal is the operative gate and it lifts once the pending
    # state is completed. The same command then reaches a different refusal.
    pending_path = paths["records"] / pending.proposal_id / "pending.json"
    assert main(_finalize_argv(paths, pending_path)) == 0
    capsys.readouterr()
    assert service.pending_finalization() is None
    assert main(second_preview_argv) == cli.EXIT_COLLISION
    lifted = capsys.readouterr()
    assert pending.proposal_id not in lifted.err
    assert "stale expected model identity" in lifted.err


def test_interrupted_apply_is_completable_by_finalize_without_repair(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: Any,
) -> None:
    """Over-correction control: chaining must not strand an interrupted apply.

    Chaining publication and recheck into one command must not remove the only
    way to complete a transaction that was interrupted after the model CAS. This
    test never invokes ``gnd evolve apply`` and therefore passes with and without
    the chaining; it controls resumability, not chaining.
    """

    from gnd.cli import main
    from gnd.evolve import EvolutionPreview, EvolutionRecord, EvolutionService

    paths = _cli_workspace(tmp_path)
    _forbid_codegen(monkeypatch)
    assert main(_preview_argv(paths)) == 0
    capsys.readouterr()

    service = EvolutionService(
        model_path=paths["model"],
        evidence_root=paths["records"],
        allowed_project_root=paths["workspace"],
    )
    staged = EvolutionPreview.model_validate_json(
        paths["preview"].read_text(encoding="utf-8")
    )
    pending = service.apply(staged)
    proposal_dir = paths["records"] / pending.proposal_id
    assert paths["model"].read_bytes() == paths["candidate_bytes"]
    assert not (proposal_dir / "record.json").exists()
    assert not (proposal_dir / "conformance").exists()
    assert service.pending_finalization() == pending

    pending_path = proposal_dir / "pending.json"
    assert main(_finalize_argv(paths, pending_path)) == 0
    record = EvolutionRecord.model_validate_json(capsys.readouterr().out)
    assert record.finalization_state_sha256 == pending.state_identity_sha256
    assert (proposal_dir / "conformance" / "linked.json").is_file()
    assert record.conformance_exit_code == 0
    assert record.affected_code.generated_code_written is False
    assert record.affected_code.extension_code_written is False
    assert paths["model"].read_bytes() == paths["candidate_bytes"], "no rollback (D-11)"
    assert paths["verbalization"].read_text(encoding="utf-8") == staged.verbalization.text
    assert _tree_sha256(paths["project_root"]) == paths["project_tree"]
    assert service.pending_finalization() is None


def test_reusable_conformance_service_preserves_raw_payload_and_exit_semantics(
    tmp_path: Path,
) -> None:
    from gnd.conformance.service import run_conformance

    row = _case()
    model_path = tmp_path / "candidate.orm.yaml"
    model_path.write_text(row["inputs"]["candidate_model"]["text"], encoding="utf-8")
    root = tmp_path / "project"
    _generated_project(model_path, root)

    clean = run_conformance(model_path, root)
    assert clean.exit_code == 0
    assert clean.payload["findings"] == []
    assert "exit_code" not in clean.payload

    manifest = read_manifest(root / ".gnd-codegen.json")
    derived = next(entry for entry in manifest.files if entry.ownership == "derived")
    derived_path = root / derived.relpath
    derived_path.write_bytes(derived_path.read_bytes() + b"\n# drift\n")

    drift = run_conformance(model_path, root)
    assert drift.exit_code == 13
    assert drift.payload["findings"]
    assert drift.payload != clean.payload
    assert "exit_code" not in drift.payload


def test_finalize_checks_each_explicit_project_once_after_cas_without_writes(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    import gnd.evolve.service as evolution_module
    from gnd.evolve import EvolutionService, LinkedProject, ProjectLocator

    row = _case()
    before = row["inputs"]["before_model"]
    candidate = row["inputs"]["candidate_model"]

    target_model = tmp_path / "model.orm.yaml"
    target_model.write_text(before["text"], encoding="utf-8")
    candidate_model = tmp_path / "candidate.orm.yaml"
    candidate_model.write_text(candidate["text"], encoding="utf-8")

    clean_root = tmp_path / "clean-project"
    drift_root = tmp_path / "drift-project"
    _generated_project(candidate_model, clean_root)
    _generated_project(candidate_model, drift_root)
    drift_manifest = read_manifest(drift_root / ".gnd-codegen.json")
    drift_entry = next(entry for entry in drift_manifest.files if entry.ownership == "derived")
    drift_path = drift_root / drift_entry.relpath
    drift_path.write_bytes(drift_path.read_bytes() + b"\n# deliberate drift\n")

    before_trees = {
        "clean": _tree_sha256(clean_root),
        "drift": _tree_sha256(drift_root),
    }
    projects = (
        LinkedProject(
            project_id="clean",
            locator=ProjectLocator(
                base="allowed-project-root",
                path="clean-project",
            ),
            **_roster(clean_root),
        ),
        LinkedProject(
            project_id="drift",
            locator=ProjectLocator(
                base="allowed-project-root",
                path="drift-project",
            ),
            **_roster(drift_root),
        ),
    )
    proposal = _proposal(candidate["text"], before["sha256"], projects)
    service = EvolutionService(
        model_path=target_model,
        evidence_root=tmp_path / "evidence",
        allowed_project_root=tmp_path,
    )
    preview = service.preview(proposal)

    real_run = evolution_module.run_conformance
    calls: list[Path] = []

    def counted_run(model_path: Path, project_root: Path) -> Any:
        calls.append(Path(project_root).resolve())
        return real_run(model_path, project_root)

    monkeypatch.setattr(evolution_module, "run_conformance", counted_run)
    def forbidden_codegen(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("evolution must not invoke code generation")

    monkeypatch.setattr("gnd.codegen.emit.emit_project", forbidden_codegen)
    monkeypatch.setattr("gnd.codegen.emit.write_project", forbidden_codegen)

    pending = service.apply(preview)

    assert target_model.read_bytes() == candidate["text"].encode("utf-8")
    assert calls == []
    assert _tree_sha256(clean_root) == before_trees["clean"]
    assert _tree_sha256(drift_root) == before_trees["drift"]

    record = service.finalize(pending)
    assert calls == [clean_root.resolve(), drift_root.resolve()]
    assert [item.exit_code for item in record.linked_conformance] == [0, 13]
    assert record.conformance_exit_code == 13
    assert record.published_with_drift is True
    assert _tree_sha256(clean_root) == before_trees["clean"]
    assert _tree_sha256(drift_root) == before_trees["drift"]

    for item in record.linked_conformance:
        assert item.locator is not None
        assert item.root is None
        assert item.before_tracked_tree_sha256 == item.after_tracked_tree_sha256
        assert item.expected_tracked_tree_sha256 == item.before_tracked_tree_sha256
        assert (
            item.payload_sha256
            == hashlib.sha256(canonical(item.payload).encode("utf-8")).hexdigest()
        )
        assert "exit_code" not in item.payload

    assert record.affected_code.generated_code_written is False
    assert record.affected_code.extension_code_written is False
    assert service.finalize(pending) == record
    assert calls == [clean_root.resolve(), drift_root.resolve()]


@pytest.mark.parametrize(
    "crash_point",
    [
        "after-model-cas",
        "after-verbalization",
        "after-conformance",
        "after-record",
    ],
)
def test_interrupted_finalization_recovers_only_exact_missing_leaves(
    tmp_path: Path,
    monkeypatch: Any,
    crash_point: str,
) -> None:
    import gnd.evolve.service as evolution_module
    from gnd.evolve import EvolutionService, LinkedProject, ProjectLocator

    row = _case()
    before = row["inputs"]["before_model"]
    candidate = row["inputs"]["candidate_model"]
    target_model = tmp_path / "model.orm.yaml"
    target_model.write_text(before["text"], encoding="utf-8")
    verbalization_path = tmp_path / "model.verbalization.txt"
    verbalization_path.write_text("pre-existing verbalization\n", encoding="utf-8")
    candidate_path = tmp_path / "candidate.orm.yaml"
    candidate_path.write_text(candidate["text"], encoding="utf-8")
    project_root = tmp_path / "linked-project"
    _generated_project(candidate_path, project_root)
    project_tree = _tree_sha256(project_root)
    proposal = _proposal(
        candidate["text"],
        before["sha256"],
        (
            LinkedProject(
                project_id="linked",
                locator=ProjectLocator(
                    base="allowed-project-root",
                    path="linked-project",
                ),
                **_roster(project_root),
            ),
        ),
    )
    evidence_root = tmp_path / "evidence"
    service = EvolutionService(
        model_path=target_model,
        evidence_root=evidence_root,
        verbalization_path=verbalization_path,
        allowed_project_root=tmp_path,
    )
    preview = service.preview(proposal)

    real_run = evolution_module.run_conformance
    conformance_calls: list[Path] = []

    def counted_run(model_path: Path, root: Path) -> Any:
        conformance_calls.append(Path(root).resolve())
        return real_run(model_path, root)

    monkeypatch.setattr(evolution_module, "run_conformance", counted_run)
    pending = service.apply(preview)
    assert target_model.read_bytes() == candidate["text"].encode("utf-8")
    assert verbalization_path.read_text(encoding="utf-8") == "pre-existing verbalization\n"
    assert _tree_sha256(project_root) == project_tree

    if crash_point == "after-verbalization":
        failed_once = False

        def fail_before_conformance(model_path: Path, root: Path) -> Any:
            nonlocal failed_once
            if not failed_once:
                failed_once = True
                raise RuntimeError("simulated crash before conformance")
            return counted_run(model_path, root)

        monkeypatch.setattr(evolution_module, "run_conformance", fail_before_conformance)
        with pytest.raises(RuntimeError, match="before conformance"):
            service.finalize(pending)
        assert verbalization_path.read_text(encoding="utf-8") == preview.verbalization.text
        monkeypatch.setattr(evolution_module, "run_conformance", counted_run)
    elif crash_point in {"after-conformance", "after-record"}:
        real_write_once = service._write_once

        def fail_at_record(relpath: str, data: bytes) -> Path:
            if relpath.endswith("/record.json"):
                if crash_point == "after-record":
                    real_write_once(relpath, data)
                raise RuntimeError(f"simulated crash {crash_point}")
            return real_write_once(relpath, data)

        monkeypatch.setattr(service, "_write_once", fail_at_record)
        with pytest.raises(RuntimeError, match=crash_point):
            service.finalize(pending)
        assert conformance_calls == [project_root.resolve()]

    recovered = EvolutionService(
        model_path=target_model,
        evidence_root=evidence_root,
        verbalization_path=verbalization_path,
        allowed_project_root=tmp_path,
    )
    assert recovered.apply(preview) == pending

    if crash_point in {"after-conformance", "after-record"}:

        def forbidden_rerun(_model_path: Path, _root: Path) -> Any:
            raise AssertionError("durable conformance evidence must be reused")

        monkeypatch.setattr(evolution_module, "run_conformance", forbidden_rerun)

    record = recovered.finalize(pending)
    record_bytes = recovered.record_path(proposal.proposal_id).read_bytes()
    assert recovered.finalize(pending) == record
    assert recovered.record_path(proposal.proposal_id).read_bytes() == record_bytes
    assert target_model.read_bytes() == candidate["text"].encode("utf-8")
    assert verbalization_path.read_text(encoding="utf-8") == preview.verbalization.text
    assert _tree_sha256(project_root) == project_tree
    assert conformance_calls == [project_root.resolve()]


def test_finalization_refuses_divergent_locator_evidence_without_repair(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    from gnd.evolve import EvolutionError, EvolutionService

    paths = _cli_workspace(tmp_path)
    _forbid_codegen(monkeypatch)
    service = EvolutionService(
        model_path=paths["model"],
        evidence_root=paths["records"],
        verbalization_path=paths["verbalization"],
        allowed_project_root=paths["workspace"],
    )
    preview = service.preview(paths["proposal"])
    pending = service.apply(preview)
    real_write_once = service._write_once

    def interrupt_record(relpath: str, data: bytes) -> Path:
        if relpath.endswith("/record.json"):
            raise RuntimeError("simulated crash before record publication")
        return real_write_once(relpath, data)

    monkeypatch.setattr(service, "_write_once", interrupt_record)
    with pytest.raises(RuntimeError, match="before record publication"):
        service.finalize(pending)
    monkeypatch.setattr(service, "_write_once", real_write_once)

    conformance_path = (
        paths["records"]
        / pending.proposal_id
        / "conformance"
        / "linked.json"
    )
    document = json.loads(conformance_path.read_text(encoding="utf-8"))
    document["locator"]["path"] = "different-linked-project"
    conformance_path.write_text(
        json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    divergent_bytes = conformance_path.read_bytes()

    with pytest.raises(EvolutionError, match="linked conformance identity changed"):
        service.finalize(pending)

    assert conformance_path.read_bytes() == divergent_bytes
    assert not service.record_path(pending.proposal_id).exists()
    assert paths["model"].read_bytes() == paths["candidate_bytes"]
    assert _tree_sha256(paths["project_root"]) == paths["project_tree"]


def test_finalization_refuses_divergent_linked_project_without_repair(
    tmp_path: Path,
) -> None:
    from gnd.evolve import EvolutionError, EvolutionService, LinkedProject, ProjectLocator

    row = _case()
    before = row["inputs"]["before_model"]
    candidate = row["inputs"]["candidate_model"]
    target_model = tmp_path / "model.orm.yaml"
    target_model.write_text(before["text"], encoding="utf-8")
    candidate_path = tmp_path / "candidate.orm.yaml"
    candidate_path.write_text(candidate["text"], encoding="utf-8")
    project_root = tmp_path / "linked-project"
    _generated_project(candidate_path, project_root)
    proposal = _proposal(
        candidate["text"],
        before["sha256"],
        (
            LinkedProject(
                project_id="linked",
                locator=ProjectLocator(
                    base="allowed-project-root",
                    path="linked-project",
                ),
                **_roster(project_root),
            ),
        ),
    )
    service = EvolutionService(
        model_path=target_model,
        evidence_root=tmp_path / "evidence",
        allowed_project_root=tmp_path,
    )
    preview = service.preview(proposal)
    pending = service.apply(preview)
    from gnd.evolve import canonical_sha256
    proposal_dir = tmp_path / "evidence" / proposal.proposal_id
    staged = {name: (proposal_dir / name).read_bytes() for name in ("pending.json", "intent.json")}
    def restage(document: dict[str, Any], name: str = "pending.json") -> Any:
        if name == "pending.json":
            identity = {k: v for k, v in document.items() if k != "state_identity_sha256"}
            document["state_identity_sha256"] = canonical_sha256(identity)
        (proposal_dir / name).write_text(json.dumps(document, sort_keys=True) + "\n")
        return document
    forged = json.loads(staged["pending.json"])
    forged["linked_projects"][0]["expected_tracked_tree_sha256"] = "0" * 64
    with pytest.raises(EvolutionError, match="do not match staged intent"):
        service.finalize(type(pending).model_validate(restage(forged)))
    intent = json.loads(staged["intent.json"])
    intent["linked_projects"][0]["project_id"] = "smuggled"
    restage(intent, "intent.json")
    forged["linked_projects"] = intent["linked_projects"]
    forged["intent_sha256"] = hashlib.sha256((proposal_dir / "intent.json").read_bytes()).hexdigest()
    with pytest.raises(EvolutionError, match="do not match the proposal"):
        service.finalize(type(pending).model_validate(restage(forged)))
    assert not service.verbalization_path.exists()
    for name, original in staged.items():
        (proposal_dir / name).write_bytes(original)
    marker = project_root / ".gnd-codegen.json"
    marker.write_text("owner changed this project after model CAS\n", encoding="utf-8")
    divergent_tree = _tree_sha256(project_root)

    with pytest.raises(EvolutionError, match="linked project.*changed|stale"):
        service.finalize(pending)

    assert _tree_sha256(project_root) == divergent_tree
    assert marker.read_text(encoding="utf-8") == "owner changed this project after model CAS\n"
    assert not service.record_path(proposal.proposal_id).exists()
    from gnd.artifacts import snapshot_tracked_roster
    (project_root / "spaced").symlink_to("  target  ")
    assert snapshot_tracked_roster(project_root, ["spaced"], label="s")[0][0].target == "  target  "


@pytest.mark.parametrize("escape", [False, True], ids=["in-root", "escaping"])
def test_linked_project_locator_refuses_every_intermediate_symlink(
    tmp_path: Path,
    escape: bool,
) -> None:
    from gnd.evolve import EvolutionError, EvolutionService, LinkedProject, ProjectLocator

    row = _case()
    before = row["inputs"]["before_model"]
    candidate = row["inputs"]["candidate_model"]
    model_path = tmp_path / "model.orm.yaml"
    model_path.write_text(before["text"], encoding="utf-8")
    candidate_path = tmp_path / "candidate.orm.yaml"
    candidate_path.write_text(candidate["text"], encoding="utf-8")
    target_parent = (tmp_path.parent / "outside-target") if escape else (tmp_path / "real")
    target_parent.mkdir()
    target = target_parent / "project"
    _generated_project(candidate_path, target)
    (tmp_path / "alias").symlink_to(target_parent, target_is_directory=True)
    proposal = _proposal(
        candidate["text"],
        before["sha256"],
        (
            LinkedProject(
                project_id="linked",
                locator=ProjectLocator(
                    base="allowed-project-root",
                    path="alias/project",
                ),
                **_roster(target),
            ),
        ),
    )
    service = EvolutionService(
        model_path=model_path,
        evidence_root=tmp_path / "evidence",
        allowed_project_root=tmp_path,
    )
    preview = service.preview(proposal)

    with pytest.raises(EvolutionError, match="component 'alias' is a symlink"):
        service.apply(preview)

    assert model_path.read_bytes() == before["text"].encode("utf-8")
    assert not (tmp_path / "evidence" / proposal.proposal_id).exists()


@pytest.mark.parametrize(
    ("case", "locator_path", "error_pattern"),
    [
        ("missing", "missing-project", "could not be resolved"),
        ("symlink-escape", "alias/project", "escapes allowed root"),
    ],
)
def test_linked_project_locator_requires_strict_resolution_and_resolved_containment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    case: str,
    locator_path: str,
    error_pattern: str,
) -> None:
    from gnd.evolve import (
        EvolutionError,
        EvolutionService,
        LinkedProject,
        ProjectLocator,
        TrackedRoster,
    )
    row = _case()
    before = row["inputs"]["before_model"]
    candidate = row["inputs"]["candidate_model"]
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    model_path = workspace / "model.orm.yaml"
    model_path.write_text(before["text"], encoding="utf-8")
    verbalization_path = workspace / "model.verbalization.txt"
    verbalization_path.write_text("retained verbalization\n", encoding="utf-8")
    evidence_root = workspace / "evidence"
    expected_tree = "a" * 64

    if case == "symlink-escape":
        outside = tmp_path / "outside"
        target = outside / "project"
        target.mkdir(parents=True)
        (workspace / "alias").symlink_to(outside, target_is_directory=True)

    proposal = _proposal(
        candidate["text"],
        before["sha256"],
        (
            LinkedProject(
                project_id="linked",
                locator=ProjectLocator(
                    base="allowed-project-root",
                    path=locator_path,
                ),
                tracked_roster=TrackedRoster(),
                expected_tracked_tree_sha256=expected_tree,
            ),
        ),
    )
    service = EvolutionService(
        model_path=model_path,
        evidence_root=evidence_root,
        verbalization_path=verbalization_path,
        allowed_project_root=workspace,
    )
    preview = service.preview(proposal)
    before_model = model_path.read_bytes()
    before_verbalization = verbalization_path.read_bytes()
    descriptor_calls: list[tuple[Path, str | None, list[str]]] = []
    def substitute_expected_tree(
        root: Path, _paths: Any, *, relative: str | None = None, **caps: Any
    ) -> tuple[tuple[Any, ...], str]:
        descriptor_calls.append((root, relative, sorted(caps)))  # caps too
        return (), expected_tree
    monkeypatch.setattr(
        "gnd.evolve.service.snapshot_tracked_roster", substitute_expected_tree
    )
    with pytest.raises(EvolutionError, match=error_pattern):
        service.apply(preview)
    caps = ["label", "max_total_bytes"]  # notably NOT max_entries: no widened cap
    assert descriptor_calls == [(service.allowed_project_root, locator_path, caps)]
    assert model_path.read_bytes() == before_model
    assert verbalization_path.read_bytes() == before_verbalization
    assert not evidence_root.exists()
