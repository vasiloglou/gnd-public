"""MG2 parity capture (spec T4): every evolve fixture previewed, and applied
where apply succeeds today, WITHOUT the new options.

Run from the repository root:
    uv run python .gnd-planning/milestones/model-growth-guardrails/evidence/MG2/capture_parity.py OUT.json
Writes, per fixture, the exit and the SHA-256 of the preview document (the
scratch workspace path replaced by <WS>), and for the applied fixtures the
apply exit, the SHA-256 of the published model bytes and of the normalized
apply stdout. Each fixture is run twice; `stable` says whether the two runs
agree, so a nondeterministic field is visible rather than compared.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "tests"))

import test_model_evolution as evolution
from support.cli_runner import run_main


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _norm(data: bytes, work: Path) -> bytes:
    return data.replace(str(work).encode(), b"<WS>").replace(str(work.resolve()).encode(), b"<WS>")


def _preview(work: Path, model: Path, proposal: Path, out: Path) -> dict:
    result = run_main(["evolve", "preview", str(model), str(proposal), "--workspace", str(work),
                       "--records", str(work / "records"), "--out", str(out), "--format", "json"])
    row = {"preview_exit": result.returncode}
    if out.is_file():
        row["preview_sha256"] = _sha(_norm(out.read_bytes(), work))
    else:
        row["preview_stderr"] = _norm(result.stderr, work).decode("utf-8", "replace")[-300:]
    return row


def _apply(work: Path, model: Path, proposal: Path, preview: Path) -> dict:
    result = run_main(["evolve", "apply", str(model), str(proposal), "--preview", str(preview),
                       "--workspace", str(work), "--records", str(work / "records"), "--format", "json"])
    return {
        "apply_exit": result.returncode,
        "apply_stdout_sha256": _sha(_norm(result.stdout, work)),
        "published_model_sha256": _sha(model.read_bytes()),
    }


def _phase4(tmp: Path, case: str, *, apply: bool) -> dict:
    paths = evolution._write_cli_workspace(tmp, case_name=case, breaking=not apply)
    work = paths["workspace"]
    (work / "records").mkdir(exist_ok=True)
    row = _preview(work, paths["model"], paths["proposal_path"], paths["preview"])
    if apply and row["preview_exit"] == 0:
        row.update(_apply(work, paths["model"], paths["proposal_path"], paths["preview"]))
    return row


def _ik5(tmp: Path) -> dict:
    work = tmp / "ws"
    shutil.copytree(ROOT / "tests/fixtures/induced_knowledge/ik5-corpus", work)
    (work / "records").mkdir()
    proposal = work / "i1.proposal.json"
    imported = run_main(["import", "ilp-rules", str(work / "orders.orm.yaml"), str(work / "i1.clauses.json"),
                         "--labels", str(work / "m.labels.json"), "--reported-coverage", str(work / "i1.run.json"),
                         "--target", "neutral", "--out", str(proposal), "--requested-at", "2026-10-26T00:00:00+00:00"])
    assert imported.returncode == 0, imported.stderr
    row = _preview(work, work / "orders.orm.yaml", proposal, work / "preview.json")
    row.update(_apply(work, work / "orders.orm.yaml", proposal, work / "preview.json"))
    return row


def _discover_proposal(work: Path, model: Path, host: str, role: str, prefix: str) -> Path:
    from gnd.discover import output
    from gnd.evolve.service import _parse_model_text

    model_bytes = model.read_bytes()
    document = _parse_model_text(model_bytes.decode("utf-8"))
    constraint = {"type": "mandatory", "role": role, "source": "user-supplied", "status": "confirmed",
                  "modality": "deontic", "rationale": "MG2 parity probe",
                  "provenance": {"user_quote": "parity"}}
    ops = output.add_operations([(host, constraint)], prefix=prefix)
    built = output.proposal(model_bytes=model_bytes, document=output.candidate_document(document, ops), ops=ops,
                            actor="mg2-parity", requested_at=datetime(2026, 11, 4, tzinfo=UTC),
                            origin="mg2 parity", prefix=prefix, rationale="one mandatory constraint")
    path = work / "proposal.json"
    path.write_bytes(output.canonical_bytes(built.model_dump(mode="json")))
    return path


def _dispatch(tmp: Path) -> dict:
    work = tmp / "ws"
    shutil.copytree(ROOT / "tests/fixtures/reference-corpus/dispatch", work)
    (work / "records").mkdir()
    model = work / "model.orm.yaml"
    proposal = _discover_proposal(work, model, "dispatch_subject_warehouse", "warehouse", "q2")
    row = _preview(work, model, proposal, work / "preview.json")
    row.update(_apply(work, model, proposal, work / "preview.json"))
    return row


def _ik4(tmp: Path) -> dict:
    work = tmp / "ws"
    work.mkdir()
    (work / "records").mkdir()
    src = ROOT / "tests/fixtures/induced_knowledge/ik4-corpus"
    shutil.copyfile(src / "staff.orm.yaml", work / "staff.orm.yaml")
    shutil.copyfile(src / "staff.population.yaml", work / "staff.population.yaml")
    model = work / "staff.orm.yaml"
    from ruamel.yaml import YAML
    document = YAML(typ="safe").load(model.read_text(encoding="utf-8"))
    fact = document["fact_types"][0]
    proposal = _discover_proposal(work, model, fact["id"], fact["roles"][0]["role_name"], "ld")
    row = _preview(work, model, proposal, work / "preview.json")
    row.update(_apply(work, model, proposal, work / "preview.json"))
    return row


def _example(tmp: Path, example: str, model_name: str, proposal_name: str) -> dict:
    work = tmp / "ws"
    shutil.copytree(ROOT / "src/gnd/examples" / example, work)
    (work / "records").mkdir(exist_ok=True)
    model = work / model_name
    proposal = work / proposal_name
    row = _preview(work, model, proposal, work / "preview.json")
    row.update(_apply(work, model, proposal, work / "preview.json"))
    return row


def _v2(tmp: Path) -> dict:
    import copy

    import test_model_v2 as v2

    from gnd.evolve import ElementLocator, EvolutionOperation, EvolutionOperationKind

    work = tmp / "ws"
    work.mkdir()
    (work / "records").mkdir()
    before_text = v2.OPERATIONS_MODEL.read_text(encoding="utf-8")
    model = work / "model.orm.yaml"
    model.write_text(before_text, encoding="utf-8")
    candidate = v2._operations_doc()
    candidate["operations"].append(copy.deepcopy(v2.NEW_OPERATION))
    proposal, _ = v2._proposal(before_text, candidate, (EvolutionOperation(
        operation_id="add-close-operation", kind=EvolutionOperationKind.ADD,
        locator=ElementLocator(collection="operations", element_id="close_work_item"),
        before=None, after=copy.deepcopy(v2.NEW_OPERATION)),))
    path = work / "proposal.json"
    path.write_text(json.dumps(proposal.model_dump(mode="json"), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    row = _preview(work, model, path, work / "preview.json")
    row.update(_apply(work, model, path, work / "preview.json"))
    return row


FIXTURES = {
    "phase4/evolution-safe-additive": lambda t: _phase4(t, "evolution-safe-additive", apply=True),
    "phase4/evolution-rename-delete-blast-radius": lambda t: _phase4(t, "evolution-rename-delete-blast-radius", apply=False),
    "induced_knowledge/ik5-corpus": _ik5,
    "reference-corpus/dispatch": _dispatch,
    "induced_knowledge/ik4-corpus": _ik4,
    "examples/bookrec/genre-proposal": lambda t: _example(t, "bookrec", "model.orm.yaml", "genre-proposal.json"),
    "examples/plan_apps/course/credit-cap-proposal": lambda t: _example(t, "plan_apps/course", "model.orm.json", "credit-cap-proposal.json"),
    "models/v2_operations": _v2,
}


def main(out: str) -> None:
    rows = {}
    for name, build in FIXTURES.items():
        runs = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as temp:
                runs.append(build(Path(temp).resolve()))
        row = dict(runs[0])
        row["stable"] = runs[0] == runs[1]
        rows[name] = row
    Path(out).write_text(json.dumps(rows, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for name, row in rows.items():
        print(name, row["preview_exit"], row.get("apply_exit"), "stable" if row["stable"] else "UNSTABLE")


if __name__ == "__main__":
    main(sys.argv[1])
