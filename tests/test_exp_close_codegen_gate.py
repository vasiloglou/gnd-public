






























from __future__ import annotations

import copy
import json
import shutil
from collections.abc import Sequence
from pathlib import Path

import pytest

from gnd import cli, resolve_version
from gnd.cli import main
from gnd.codegen.emit import emit_project, write_project
from gnd.codegen.manifest import (
    build_manifest,
    manifest_path,
    read_manifest,
    render_manifest,
)
from gnd.conformance.architecture import check_architecture
from gnd.conformance.currency import check_currency, model_digest
from gnd.conformance.integrity import check_integrity
from gnd.conformance.report import build_conformance_payload, canonical
from gnd.conformance.structural import check_structural
from gnd.exp.close import (
    CONFORMANCE_EVIDENCE,
    CONFORMANCE_GATED_KIND,
    evaluate_close,
)
from gnd.exp.conclusions import read_conclusions
from gnd.exp.frontmatter import render_frontmatter
from gnd.exp.spec import read_spec
from gnd.model import load_model

REPO_ROOT = Path(__file__).resolve().parent.parent
FULL_VOCABULARY = REPO_ROOT / "tests" / "fixtures" / "models" / "full_vocabulary.orm.yaml"







def _experiment(
    parent: Path,
    *,
    kind: str = CONFORMANCE_GATED_KIND,
    outcome: str = "answered",
    conformance: str | None = None,
    subject: tuple[Path, Path] | None = None,
    experiment_id: str = "EXP-001-drift",
) -> Path:







    root = parent / experiment_id
    (root / "results").mkdir(parents=True)
    (root / "results" / "run.json").write_text("{}\n", encoding="utf-8")

    spec_mapping = {
        "id": experiment_id,
        "kind": kind,
        "title": "does the generated project still agree with its model",
        "questions": [{"id": "Q1", "text": "what did the emitter produce?"}],
        "follows": [],
    }
    if subject is not None:
        source_model, source_project = subject
        artifacts = root / "artifacts"
        artifacts.mkdir()
        shutil.copyfile(source_model, artifacts / "model.orm.yaml")
        shutil.copytree(source_project, artifacts / "project")
        spec_mapping.update(
            {"model": "artifacts/model.orm.yaml", "project": "artifacts/project"}
        )

    (root / "SPEC.md").write_text(
        render_frontmatter(
            spec_mapping,
            f"# {experiment_id}\n",
        ),
        encoding="utf-8",
    )

    resolution = {"id": "Q1", "outcome": outcome, "evidence": "results/run.json"}
    if outcome != "answered":
        resolution["reason"] = "the run was stopped before this case, so nothing was measured"
    (root / "CONCLUSIONS.md").write_text(
        render_frontmatter(
            {"id": experiment_id, "resolves": [resolution]},
            f"# {experiment_id} conclusions\n",
        ),
        encoding="utf-8",
    )

    if conformance is not None:
        (root / CONFORMANCE_EVIDENCE).write_text(conformance, encoding="utf-8")
    return root


def _generated(tmp_path: Path) -> tuple[Path, Path]:

    workspace = tmp_path / "generated"
    workspace.mkdir(parents=True, exist_ok=True)
    model_path = workspace / "model.orm.yaml"
    shutil.copyfile(FULL_VOCABULARY, model_path)
    root = workspace / "project"
    model = load_model(str(model_path))
    project = emit_project(model, str(model_path), skill_name=root.resolve().name)
    write_project(
        project,
        str(root),
        manifest_text=render_manifest(build_manifest(project, str(model_path))),
    )
    return model_path, root


def _payload(model_path: Path, root: Path) -> dict:
    manifest = read_manifest(manifest_path(root))
    return build_conformance_payload(
        model_path,
        manifest,
        check_integrity(root, manifest),
        check_currency(model_path, manifest),
        structural=check_structural(
            load_model(str(model_path)), root, manifest, model_path=model_path
        ),
        architecture=check_architecture(
            load_model(str(model_path)), root, manifest, model_path=model_path
        ),
        actual_model_sha256=model_digest(model_path),
        gnd_version=resolve_version(),
    )


def _pair(tmp_path: Path) -> tuple[dict, dict, Path, Path]:









    model_path, root = _generated(tmp_path)

    
    
    manifest = read_manifest(manifest_path(root))
    target = min(
        relpath
        for relpath, entry in manifest.entries().items()
        if entry.ownership == "derived"
    )
    edited = root / target
    edited.write_text(edited.read_text(encoding="utf-8") + " ", encoding="utf-8")

    refusing = _payload(model_path, root)
    assert refusing["findings"], "the drifted fixture reported no findings"

    closing = copy.deepcopy(refusing)
    closing["findings"] = []
    for assertion in closing["assertions"]:
        assertion["findings"] = 0
    return refusing, closing, model_path, root


def _clean(tmp_path: Path) -> tuple[dict, Path, Path]:
    model_path, root = _generated(tmp_path)
    return _payload(model_path, root), model_path, root


def _close(root: Path) -> Sequence:
    spec_path = root / "SPEC.md"
    return evaluate_close(
        read_spec(spec_path), read_conclusions(root / "CONCLUSIONS.md"), spec_path
    ).findings


def _kinds(findings: Sequence) -> set[str]:
    return {finding.kind for finding in findings}







def test_a_codegen_experiment_with_a_non_empty_findings_array_is_refused_at_fourteen(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    refusing, _, model_path, project = _pair(tmp_path)
    root = _experiment(
        tmp_path, conformance=canonical(refusing), subject=(model_path, project)
    )

    capsys.readouterr()
    assert main(["exp", "close", str(root)]) == cli.EXIT_EXPERIMENT_OPEN
    printed = capsys.readouterr().out

    assert "unmet-conformance" in printed
    assert CONFORMANCE_EVIDENCE in printed, (
        "the refusal does not name the artifact the author has to produce or "
        "repair; 'one obligation is undischarged' is not something anyone can act on"
    )
    assert "drift finding" in printed


def test_emptying_a_recorded_findings_array_cannot_forge_a_green_close(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:

    _, closing, model_path, project = _pair(tmp_path)
    root = _experiment(
        tmp_path, conformance=canonical(closing), subject=(model_path, project)
    )

    capsys.readouterr()
    assert main(["exp", "close", str(root)]) == cli.EXIT_EXPERIMENT_OPEN
    assert "stale or belongs to a different subject" in capsys.readouterr().out


def test_a_current_clean_live_subject_closes_at_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    payload, model_path, project = _clean(tmp_path)
    root = _experiment(
        tmp_path, conformance=canonical(payload), subject=(model_path, project)
    )

    capsys.readouterr()
    assert main(["exp", "close", str(root)]) == 0
    assert "CLOSED" in capsys.readouterr().out


def test_a_project_edited_after_the_recorded_run_is_refused(
    tmp_path: Path,
) -> None:
    payload, model_path, project = _clean(tmp_path)
    root = _experiment(
        tmp_path, conformance=canonical(payload), subject=(model_path, project)
    )
    manifest = read_manifest(manifest_path(root / "artifacts" / "project"))
    target = next(
        entry.relpath for entry in manifest.files if entry.ownership == "derived"
    )
    edited = root / "artifacts" / "project" / target
    edited.write_text(edited.read_text(encoding="utf-8") + " ", encoding="utf-8")

    findings = _close(root)
    assert _kinds(findings) == {"unmet-conformance"}
    assert "stale or belongs to a different subject" in findings[0].message


def test_the_pair_differs_in_the_findings_array_alone(tmp_path: Path) -> None:






    refusing, closing, _, _ = _pair(tmp_path)

    differing = {
        key for key in set(refusing) | set(closing) if refusing.get(key) != closing.get(key)
    }
    assert differing == {"findings", "assertions"}, differing
    assert closing["findings"] == [] and refusing["findings"]
    
    
    assert [entry["id"] for entry in refusing["assertions"]] == [
        entry["id"] for entry in closing["assertions"]
    ]
    assert all(entry["ran"] for entry in refusing["assertions"])
    assert all(entry["ran"] for entry in closing["assertions"])
    assert sum(entry["findings"] for entry in closing["assertions"]) == 0







def test_a_codegen_experiment_with_no_conformance_evidence_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:


    root = _experiment(tmp_path, conformance=None)

    capsys.readouterr()
    assert main(["exp", "close", str(root)]) == cli.EXIT_EXPERIMENT_OPEN
    printed = capsys.readouterr().out
    assert "unmet-conformance" in printed
    assert "absent measurement is not a passing one" in printed


def test_an_empty_conformance_file_is_refused_rather_than_read_as_no_findings(
    tmp_path: Path,
) -> None:


    root = _experiment(tmp_path, conformance="")
    assert _kinds(_close(root)) == {"unmet-conformance"}


def test_a_conformance_file_that_is_not_json_is_refused(tmp_path: Path) -> None:
    root = _experiment(tmp_path, conformance="{ not json")
    findings = _close(root)
    assert _kinds(findings) == {"unmet-conformance"}
    assert "could not be read as JSON" in findings[0].message







def test_a_hand_written_look_alike_is_refused_by_schema_validation(
    tmp_path: Path,
) -> None:



    root = _experiment(tmp_path, conformance=json.dumps({"findings": []}))
    findings = _close(root)
    assert _kinds(findings) == {"unmet-conformance"}
    assert "not a valid conformance payload" in findings[0].message


def test_a_real_payload_with_one_required_key_removed_is_refused(
    tmp_path: Path,
) -> None:


    _, closing, _, _ = _pair(tmp_path)
    mutilated = copy.deepcopy(closing)
    del mutilated["unexamined"]

    root = _experiment(tmp_path, conformance=canonical(mutilated))
    findings = _close(root)
    assert _kinds(findings) == {"unmet-conformance"}
    assert "conformance.schema.json" in findings[0].message


def test_a_payload_omitting_required_architecture_evidence_is_refused(
    tmp_path: Path,
) -> None:

    payload, model_path, project = _clean(tmp_path)
    del payload["architecture"]
    payload["assertions"] = [row for row in payload["assertions"] if row["id"] != "architecture"]
    root = _experiment(
        tmp_path,
        conformance=canonical(payload),
        subject=(model_path, project),
    )

    findings = _close(root)
    assert _kinds(findings) == {"unmet-conformance"}
    assert "not a valid conformance payload" in findings[0].message


def test_stale_architecture_binding_cannot_open_the_close_gate(tmp_path: Path) -> None:

    payload, model_path, project = _clean(tmp_path)
    payload["architecture"]["contract"]["sha256"] = "0" * 64
    root = _experiment(
        tmp_path,
        conformance=canonical(payload),
        subject=(model_path, project),
    )

    findings = _close(root)
    assert _kinds(findings) == {"unmet-conformance"}
    assert "stale or belongs to a different subject" in findings[0].message


def test_a_payload_whose_assertions_did_not_run_is_refused_despite_zero_findings(
    tmp_path: Path,
) -> None:








    model_path, root_project = _generated(tmp_path)
    payload = build_conformance_payload(
        model_path,
        None,
        None,
        None,
        actual_model_sha256=None,
        gnd_version=resolve_version(),
        error="no codegen manifest at the target",
    )
    assert payload["findings"] == [], "the fixture does not exercise the shape it names"

    root = _experiment(
        tmp_path,
        conformance=canonical(payload),
        subject=(model_path, root_project),
    )
    findings = _close(root)
    assert _kinds(findings) == {"unmet-conformance"}
    assert "NOT HAVING RUN" in findings[0].message
    assert "integrity" in findings[0].message and "structural" in findings[0].message
    assert root_project.exists()


def test_a_conformance_pointer_may_not_escape_the_experiment_directory(
    tmp_path: Path,
) -> None:


    _, closing, _, _ = _pair(tmp_path)
    outside = tmp_path / "elsewhere.json"
    outside.write_text(canonical(closing), encoding="utf-8")

    root = _experiment(tmp_path, conformance=None)
    (root / CONFORMANCE_EVIDENCE).symlink_to(outside)

    findings = _close(root)
    assert _kinds(findings) == {"unmet-conformance"}







@pytest.mark.parametrize("kind", ["analysis", "roundtrip"])
def test_a_non_codegen_experiment_closes_without_any_conformance_evidence(
    tmp_path: Path, kind: str
) -> None:


    root = _experiment(tmp_path, kind=kind, conformance=None)
    assert _close(root) == []


def test_a_non_codegen_experiment_is_still_refused_for_a_forgotten_question(
    tmp_path: Path,
) -> None:



    root = _experiment(tmp_path, kind="analysis", conformance=None)
    (root / "CONCLUSIONS.md").write_text(
        render_frontmatter(
            {"id": "EXP-001-drift", "resolves": []}, "# EXP-001-drift conclusions\n"
        ),
        encoding="utf-8",
    )
    assert _kinds(_close(root)) == {"forgotten-question"}


def test_an_all_unanswered_codegen_experiment_with_clean_conformance_closes_at_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:








    closing, model_path, project = _clean(tmp_path)
    root = _experiment(
        tmp_path,
        outcome="unanswered",
        conformance=canonical(closing),
        subject=(model_path, project),
    )

    capsys.readouterr()
    assert main(["exp", "close", str(root)]) == 0
    printed = capsys.readouterr().out
    assert "CLOSED" in printed
    assert "unanswered" in printed


def test_the_gate_reads_no_verdict_field_because_the_payload_has_none(
    tmp_path: Path,
) -> None:




    closing, _, _ = _clean(tmp_path)
    for forbidden in ("passed", "verdict", "drift", "acceptance_ready", "exit_code"):
        assert forbidden not in closing, (
            f"the conformance payload gained a {forbidden!r} field; the close gate "
            f"would then have two sources of truth for one fact (G-15)"
        )


def test_the_pass_rule_is_stated_as_a_comment_at_the_branch() -> None:


    from gnd.exp import close as close_module

    source = Path(close_module.__file__).read_text(encoding="utf-8")
    assert "THE PASS RULE" in source
    assert "findings" in source and "ran:true" in source
    assert "G-17 = SC4" in source
