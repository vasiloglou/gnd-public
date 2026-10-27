"""IK4-Q2: gnd evolve over models that declare reference populations.

Spec: .gnd-planning/milestones/induced-knowledge/notes/phase-IK4-Q2-spec.md
(§8, T1-T7). The fixture is a scratch copy of the synthetic
tests/fixtures/reference-corpus/dispatch/ model and its reference file.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

import pytest
from support.cli_runner import run_main

REPO_ROOT = Path(__file__).resolve().parent.parent
DISPATCH = REPO_ROOT / "tests" / "fixtures" / "reference-corpus" / "dispatch"
REFERENCE = Path("references") / "catalog.pop.json"


def _workspace(tmp_path: Path) -> Path:
    work = tmp_path / "ws"
    shutil.copytree(DISPATCH, work)
    (work / "records").mkdir()
    return work


def _proposal(work: Path, name: str = "proposal.json") -> Path:
    from gnd.discover import output
    from gnd.evolve.service import _parse_model_text

    model_bytes = (work / "model.orm.yaml").read_bytes()
    document = _parse_model_text(model_bytes.decode("utf-8"))
    constraint = {"type": "mandatory", "role": "warehouse", "source": "user-supplied",
                  "status": "confirmed", "modality": "deontic", "rationale": "IK4-Q2 probe",
                  "provenance": {"user_quote": "Every shipment names a warehouse."}}
    ops = output.add_operations([("dispatch_subject_warehouse", constraint)], prefix="q2")
    built = output.proposal(
        model_bytes=model_bytes, document=output.candidate_document(document, ops), ops=ops,
        actor="ik4-q2", requested_at=datetime(2026, 10, 26, tzinfo=UTC), origin="ik4-q2 test",
        prefix="q2", rationale="IK4-Q2: one mandatory constraint")
    path = work / name
    path.write_bytes(output.canonical_bytes(built.model_dump(mode="json")))
    return path


def _preview(work: Path, proposal: Path, out: str = "preview.json"):
    return run_main(["evolve", "preview", str(work / "model.orm.yaml"), str(proposal),
                     "--workspace", str(work), "--records", str(work / "records"),
                     "--out", str(work / out), "--format", "json"])


def _apply(work: Path, proposal: Path, preview: str = "preview.json"):
    return run_main(["evolve", "apply", str(work / "model.orm.yaml"), str(proposal),
                     "--preview", str(work / preview), "--workspace", str(work),
                     "--records", str(work / "records"), "--format", "json"])


def _text(result) -> str:
    return (result.stdout + result.stderr).decode("utf-8", errors="replace")


def test_t1_preview_of_a_reference_bearing_model(tmp_path):
    work = _workspace(tmp_path)
    result = _preview(work, _proposal(work))
    assert result.returncode == 0, _text(result)
    assert (work / "preview.json").is_file()


def test_t2_apply_and_finalize_publish_the_candidate(tmp_path):
    work = _workspace(tmp_path)
    proposal = _proposal(work)
    assert _preview(work, proposal).returncode == 0
    result = _apply(work, proposal)
    assert result.returncode == 0, _text(result)
    candidate = json.loads(proposal.read_text())["candidate_model"]["text"]
    assert (work / "model.orm.yaml").read_text(encoding="utf-8") == candidate


# Owner ruling I-F2 (2026-10-26): a missing reference file is evolve's
# missing-input exit 66; a digest mismatch stays 3 (spec §15).
@pytest.mark.parametrize(("damage", "exit_code"), [("missing", 66), ("changed", 3)])
def test_t3_an_unbindable_reference_is_a_named_refusal(tmp_path, damage, exit_code):
    work = _workspace(tmp_path)
    proposal = _proposal(work)
    reference = work / REFERENCE
    if damage == "missing":
        reference.unlink()
    else:
        reference.write_bytes(reference.read_bytes() + b"\n")
    result = _preview(work, proposal)
    assert result.returncode == exit_code, _text(result)
    assert not (work / "preview.json").exists()


def test_t4_a_linked_reference_is_refused_not_followed(tmp_path):
    work = _workspace(tmp_path)
    proposal = _proposal(work)
    reference = work / REFERENCE
    outside = tmp_path / "outside.pop.json"
    outside.write_bytes(reference.read_bytes())
    reference.unlink()
    reference.symlink_to(outside)
    result = _preview(work, proposal)
    # Owner ruling I-F2: a linked reference is evolve's refused-path exit 74.
    assert result.returncode == 74, _text(result)
    assert not (work / "preview.json").exists()


def test_t5_a_discover_proposal_on_the_model_previews(tmp_path):
    work = _workspace(tmp_path)
    discovered = run_main([
        "discover", str(work / "model.orm.yaml"), str(work / "candidate.pop.json"),
        "--out", str(work / "discovered.json"), "--report", str(work / "report.json"),
        "--actor", "ik4-q2", "--requested-at", "2026-10-26T00:00:00+00:00"])
    assert discovered.returncode == 0, _text(discovered)
    assert (work / "discovered.json").is_file(), "discovery emitted nothing to preview"
    result = _preview(work, work / "discovered.json")
    assert result.returncode == 0, _text(result)


def test_t6_reference_free_previews_are_unchanged(tmp_path):
    """The IK5 corpus proposal (no references) previews to the bytes committed
    at B (8f89af4), after the workspace path is normalized."""
    corpus = REPO_ROOT / "tests" / "fixtures" / "induced_knowledge" / "ik5-corpus"
    work = tmp_path / "ws"
    shutil.copytree(corpus, work)
    (work / "records").mkdir()
    proposal = work / "i1.proposal.json"
    imported = run_main([
        "import", "ilp-rules", str(work / "orders.orm.yaml"), str(work / "i1.clauses.json"),
        "--labels", str(work / "m.labels.json"), "--reported-coverage", str(work / "i1.run.json"),
        "--target", "neutral", "--out", str(proposal),
        "--requested-at", "2026-10-26T00:00:00+00:00"])
    assert imported.returncode == 0, _text(imported)
    result = run_main(["evolve", "preview", str(work / "orders.orm.yaml"), str(proposal),
                       "--workspace", str(work), "--records", str(work / "records"),
                       "--out", str(work / "preview.json"), "--format", "json"])
    assert result.returncode == 0, _text(result)
    observed = (work / "preview.json").read_bytes().replace(str(work).encode(), b"<WS>")
    golden = REPO_ROOT / "tests" / "fixtures" / "induced_knowledge" / "ik4-q2-preview-at-b.json"
    assert hashlib.sha256(observed).hexdigest() == hashlib.sha256(golden.read_bytes()).hexdigest()


# test_r1_a_json_named_reference_free_model_previews_as_at_b pinned B's YAML
# parse of a .json-named model. The owner ruled strict JSON (evolve-loading
# follow-up, D2-A, 2026-10-27); its successor is test_evolve_loading.py J1.


def test_r2_a_candidate_that_changes_its_references_is_refused_before_binding(tmp_path):
    """Review R2: a candidate whose reference declarations differ from the
    current model's is a malformed proposal (3), refused before any of its
    declared files is read."""
    work = _workspace(tmp_path)
    proposal = _proposal(work)
    data = json.loads(proposal.read_text())
    text = data["candidate_model"]["text"].replace(
        "references/catalog.pop.json", "references/other.pop.json")
    assert text != data["candidate_model"]["text"]
    data["candidate_model"]["text"] = text
    data["candidate_model"]["sha256"] = hashlib.sha256(text.encode()).hexdigest()
    from gnd.discover import output
    proposal.write_bytes(output.canonical_bytes(data))
    result = _preview(work, proposal)
    assert result.returncode == 3, _text(result)
    assert "reference populations" in _text(result)


def test_r3_every_load_site_binds(tmp_path, monkeypatch):
    """Review R3: preview binds twice (current, candidate). Apply first rebuilds
    the accepted preview (two more), then binds current, candidate and staged,
    and its chained finalize binds the staged before and candidate: nine."""
    import gnd.model

    calls = []
    real = gnd.model.bind_references

    def counting(model, *, root):
        calls.append(root)
        return real(model, root=root)

    monkeypatch.setattr(gnd.model, "bind_references", counting)
    work = _workspace(tmp_path)
    proposal = _proposal(work)
    assert _preview(work, proposal).returncode == 0
    assert len(calls) == 2
    assert _apply(work, proposal).returncode == 0
    assert len(calls) == 9
    assert set(calls) == {work}


def test_r3_finalize_binds_the_staged_models(tmp_path):
    """Review R3: finalize refuses (66) while a reference is missing, and
    completes once it is restored."""
    work = _workspace(tmp_path)
    proposal = _proposal(work)
    assert _preview(work, proposal).returncode == 0
    assert _apply(work, proposal).returncode == 0
    (pending,) = sorted((work / "records").rglob("pending.json"))
    reference = work / REFERENCE
    kept = reference.read_bytes()
    reference.unlink()

    def finalize():
        return run_main(["evolve", "finalize", str(work / "model.orm.yaml"), str(pending),
                         "--workspace", str(work), "--records", str(work / "records"),
                         "--format", "json"])

    missing = finalize()
    assert missing.returncode == 66, _text(missing)
    reference.write_bytes(kept)
    restored = finalize()
    assert restored.returncode == 0, _text(restored)


def test_t7_a_reference_changed_after_preview_refuses_apply(tmp_path):
    work = _workspace(tmp_path)
    proposal = _proposal(work)
    assert _preview(work, proposal).returncode == 0
    reference = work / REFERENCE
    reference.write_bytes(reference.read_bytes() + b"\n")
    result = _apply(work, proposal)
    assert result.returncode == 3, _text(result)
    assert (work / "model.orm.yaml").read_bytes() == (DISPATCH / "model.orm.yaml").read_bytes()
