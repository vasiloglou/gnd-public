"""v4.0 Phase 1: codegen seeds the create-once architecture contract."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from gnd.architecture import (
    ArchitectureContractError,
    ArchitectureIssue,
    load_architecture_contract,
    parse_architecture_contract_bytes,
)
from gnd.cli import main
from gnd.codegen.emit import (
    ARCHITECTURE_CONTRACT_DOCUMENT,
    ARTIFACTS_DIR,
    EXTENSION,
    EmitGateError,
    emit_project,
    render_architecture_contract,
)
from gnd.model import load_model

REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL = REPO_ROOT / "tests" / "fixtures" / "models" / "full_vocabulary.orm.yaml"


def _project():
    return emit_project(load_model(MODEL), str(MODEL))


def _tree_digests(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_fresh_codegen_emits_a_loader_valid_extension_contract() -> None:
    project = _project()
    emitted = next(file for file in project.files if file.relpath == ARCHITECTURE_CONTRACT_DOCUMENT)

    assert emitted.ownership == EXTENSION
    parsed = parse_architecture_contract_bytes(emitted.text.encode("utf-8"), source=emitted.relpath)
    assert parsed.contract_version == 1
    assert parsed.modules == parsed.entry_points == parsed.smoke == ()


def test_skeleton_contains_the_complete_sorted_artifact_inventory() -> None:
    project = _project()
    emitted = next(file for file in project.files if file.relpath == ARCHITECTURE_CONTRACT_DOCUMENT)
    parsed = parse_architecture_contract_bytes(emitted.text.encode("utf-8"), source=emitted.relpath)
    expected = sorted(
        file.relpath for file in project.derived if file.relpath.startswith(f"{ARTIFACTS_DIR}/")
    )

    assert [artifact.path for artifact in parsed.artifacts] == expected
    assert all(artifact.required_by == () for artifact in parsed.artifacts)
    assert emitted.text.endswith("\n")


def test_renderer_stays_loader_valid_for_an_empty_artifact_inventory() -> None:
    parsed = parse_architecture_contract_bytes(
        render_architecture_contract(()).encode("utf-8"), source=ARCHITECTURE_CONTRACT_DOCUMENT
    )

    assert parsed.artifacts == ()


def test_contract_and_skeleton_have_no_model_sha256() -> None:
    emitted = next(
        file for file in _project().files if file.relpath == ARCHITECTURE_CONTRACT_DOCUMENT
    )
    assert "model_sha256" not in emitted.text
    assert "contract-model-stale" not in emitted.text


def test_unchanged_second_run_writes_zero_and_preserves_every_digest(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "project"
    command = ["codegen", str(MODEL), "--out", str(out)]
    assert main(command) == 0
    capsys.readouterr()
    before = _tree_digests(out)
    manifest_before = (out / ".gnd-codegen.json").read_bytes()

    assert main(command) == 0
    output = capsys.readouterr().out

    assert "0 written" in output
    assert _tree_digests(out) == before
    assert (out / ".gnd-codegen.json").read_bytes() == manifest_before
    assert load_architecture_contract(out).contract_version == 1


def test_authored_contract_survives_rerun_and_force_at_exit_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "project"
    command = ["codegen", str(MODEL), "--out", str(out)]
    assert main(command) == 0
    capsys.readouterr()

    contract = out / ARCHITECTURE_CONTRACT_DOCUMENT
    authored = contract.read_bytes().replace(b"modules: []", b"modules: []\n# authored")
    contract.write_bytes(authored)
    manifest_before = (out / ".gnd-codegen.json").read_bytes()

    assert main(command) == 0
    ordinary_output = capsys.readouterr().out
    assert "0 written" in ordinary_output
    assert contract.read_bytes() == authored
    assert (out / ".gnd-codegen.json").read_bytes() == manifest_before

    assert main([*command, "--force"]) == 0
    force_output = capsys.readouterr().out
    assert "0 written" in force_output
    assert contract.read_bytes() == authored
    assert (out / ".gnd-codegen.json").read_bytes() == manifest_before


def test_broken_skeleton_is_an_emitter_gate_breach(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from gnd.codegen import emit as emit_module

    def refuse(*args, **kwargs):
        issue = ArchitectureIssue("contract_version", "planted refusal", "architecture:shape")
        raise ArchitectureContractError("planted refusal", (issue,))

    monkeypatch.setattr(emit_module, "parse_architecture_contract_bytes", refuse)
    with pytest.raises(EmitGateError, match="architecture.contract.yaml does not load"):
        _project()


def test_loader_valid_skeleton_with_missing_inventory_is_an_emitter_gate_breach(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from gnd.codegen import emit as emit_module

    empty_skeleton = render_architecture_contract(())
    monkeypatch.setattr(
        emit_module,
        "render_architecture_contract",
        lambda _artifact_relpaths: empty_skeleton,
    )

    with pytest.raises(EmitGateError, match="artifact inventory"):
        _project()
