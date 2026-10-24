"""IK2: induced provenance and admission (induced-knowledge milestone).

Spec: .gnd-planning/milestones/induced-knowledge/notes/phase-IK2-spec.md. Test
ids are that spec's section 8. Under IK2-D1 the loader, bounds and admission
cases (T2-T4) are an owner-approved corpus: the inputs live in
tests/fixtures/induced_knowledge/ik2-corpus/cases.json, the answers in
expected.json, and the stories in that directory's README.md.
"""

from __future__ import annotations

import copy
import importlib.util
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML
from support.cli_runner import run_main

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS = REPO_ROOT / "tests" / "fixtures" / "induced_knowledge" / "ik2-corpus"
D12_BASELINE = REPO_ROOT / "tests" / "fixtures" / "induced_knowledge" / "ik2-d12-baseline.json"
D12_CAPTURE = (
    REPO_ROOT
    / ".gnd-planning/milestones/induced-knowledge/evidence/IK2/capture_ik2_d12_baseline.py"
)
EVOLUTION_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "phase4_reference" / "evolution.json"
V2_OPERATIONS = REPO_ROOT / "tests" / "fixtures" / "models" / "v2_operations.orm.yaml"
HOST_FACT = "work_item_has_title"

CASES = json.loads((CORPUS / "cases.json").read_text(encoding="utf-8"))
EXPECTED = json.loads((CORPUS / "expected.json").read_text(encoding="utf-8"))


def _evolution_before() -> dict[str, Any]:
    cases = json.loads(EVOLUTION_FIXTURE.read_text(encoding="utf-8"))["cases"]
    row = next(item for item in cases if item["name"] == "evolution-safe-additive")
    return json.loads(row["inputs"]["before_model"]["text"])


def _set_pointer(document: Any, pointer: str, value: Any) -> None:
    parts = [part for part in pointer.split("/") if part]
    target = document
    for part in parts[:-1]:
        target = target[int(part)] if isinstance(target, list) else target[part]
    last = parts[-1]
    if isinstance(target, list):
        target[int(last)] = value
    else:
        target[last] = value


def _loader_model(tmp_path: Path, case: dict[str, Any]) -> Path:
    if case["base"] == "v2_operations":
        document = YAML(typ="safe").load(V2_OPERATIONS.read_text(encoding="utf-8"))
        for pointer, value in case["set"]:
            _set_pointer(document, pointer, copy.deepcopy(value))
        path = tmp_path / f"{case['id']}.orm.json"
        path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
        return path
    document = _evolution_before()
    host = document["fact_types"][0]["constraints"]
    if "constraint_yaml" in case:
        # JSON is a YAML flow document, so the base stays JSON and the case's
        # YAML-only fragment (an anchor, .nan, an unquoted date) is spliced in.
        host.append("__IK2_CASE__")
        text = json.dumps(document, ensure_ascii=False).replace(
            '"__IK2_CASE__"', case["constraint_yaml"]
        )
        path = tmp_path / f"{case['id']}.orm.yaml"
        path.write_text(text, encoding="utf-8")
        return path
    host.append(copy.deepcopy(case["constraint"]))
    path = tmp_path / f"{case['id']}.orm.json"
    path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
    return path


@pytest.mark.parametrize("case", CASES["loader"], ids=lambda case: case["id"])
def test_t2_t3_loader_corpus(tmp_path: Path, case: dict[str, Any]) -> None:
    answer = EXPECTED["loader"][case["id"]]
    result = run_main(["validate", str(_loader_model(tmp_path, case))])
    output = (result.stdout + result.stderr).decode("utf-8")
    assert result.returncode == answer["exit"], output
    if answer["rule_id"] is not None:
        assert f"[{answer['rule_id']}]" in output, output


def test_corpus_answer_key_covers_every_case() -> None:
    assert set(EXPECTED["loader"]) == {case["id"] for case in CASES["loader"]}
    assert set(EXPECTED["admission"]) == {case["id"] for case in CASES["admission"]}
    for answer in EXPECTED["admission"].values():
        assert answer["gate"] == "admitted" or answer["gate"] in EXPECTED["reasons"]


def _admission_documents(case: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    before = _evolution_before()
    candidate = copy.deepcopy(before)
    before["fact_types"][0]["constraints"].extend(copy.deepcopy(case["before"]))
    candidate["fact_types"][0]["constraints"].extend(copy.deepcopy(case["candidate"]))
    return before, candidate


def _gate_outcome(before: dict[str, Any], candidate: dict[str, Any]) -> str:
    from gnd.evolve import EvolutionError
    from gnd.evolve.service import _enforce_d12

    try:
        _enforce_d12(before, candidate)
    except EvolutionError as error:
        return str(error)
    return "admitted"


@pytest.mark.parametrize("case", CASES["admission"], ids=lambda case: case["id"])
def test_t4_admission_gate(case: dict[str, Any]) -> None:
    answer = EXPECTED["admission"][case["id"]]
    expected = "admitted" if answer["gate"] == "admitted" else EXPECTED["reasons"][answer["gate"]]
    assert _gate_outcome(*_admission_documents(case)) == expected


def _model_text(document: dict[str, Any]) -> str:
    return json.dumps(document, sort_keys=False, separators=(",", ":"), ensure_ascii=False) + "\n"


def _preview_outcome(
    tmp_path: Path, before: dict[str, Any], candidate: dict[str, Any]
) -> tuple[int, str]:
    """Preview a one-operation fact-type modify; return (public exit, refusal text)."""
    from gnd.evolve import (
        CommittedText,
        ElementLocator,
        EvolutionError,
        EvolutionOperation,
        EvolutionOperationAudit,
        EvolutionOperationKind,
        EvolutionProposal,
        EvolutionService,
    )
    from gnd.evolve.cli_service import _evolve_service_exit

    before_text = _model_text(before)
    candidate_text = _model_text(candidate)
    tmp_path.mkdir(parents=True, exist_ok=True)
    model_path = tmp_path / "model.orm.yaml"
    model_path.write_text(before_text, encoding="utf-8")
    verbalization_path = tmp_path / "model.verbalization.txt"
    verbalization_path.write_text("pre-existing verbalization\n", encoding="utf-8")
    service = EvolutionService(
        model_path=model_path,
        evidence_root=tmp_path / "evolution-evidence",
        verbalization_path=verbalization_path,
        allowed_project_root=tmp_path,
    )
    host_before = next(item for item in before["fact_types"] if item["id"] == HOST_FACT)
    host_after = next(item for item in candidate["fact_types"] if item["id"] == HOST_FACT)
    proposal = EvolutionProposal(
        proposal_id="proposal-ik2-admission",
        expected_model_sha256=CommittedText.from_text(
            before_text, media_type="application/yaml"
        ).sha256,
        candidate_model=CommittedText.from_text(candidate_text, media_type="application/yaml"),
        operations=(
            EvolutionOperation(
                operation_id="modify-host-fact",
                kind=EvolutionOperationKind.MODIFY,
                locator=ElementLocator(collection="fact_types", element_id=HOST_FACT),
                before=host_before,
                after=host_after,
            ),
        ),
        rationale="IK2 admission corpus case.",
        audit=EvolutionOperationAudit(
            actor_id="owner:fixture",
            origin="ik2-admission-corpus",
            requested_at=datetime(2026, 10, 24, 12, 0, tzinfo=UTC),
        ),
    )
    # A fact-type modify is not breaking, so no accepted blast radius is passed.
    try:
        service.preview(proposal)
    except EvolutionError as error:
        return _evolve_service_exit(error), str(error)
    return 0, ""


@pytest.mark.parametrize(
    "case",
    [case for case in CASES["admission"] if case["preview"]],
    ids=lambda case: case["id"],
)
def test_t4_admission_preview(tmp_path: Path, case: dict[str, Any]) -> None:
    answer = EXPECTED["admission"][case["id"]]
    exit_code, refusal = _preview_outcome(tmp_path, *_admission_documents(case))
    assert exit_code == answer["preview_exit"], refusal
    reason = answer["preview_reason"]
    if reason is not None:
        assert EXPECTED["reasons"].get(reason, reason) in refusal


def test_t5_d12_outcomes_equal_the_base_commit_table() -> None:
    spec = importlib.util.spec_from_file_location("ik2_d12_capture", D12_CAPTURE)
    assert spec is not None and spec.loader is not None
    capture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(capture)
    baseline = json.loads(D12_BASELINE.read_text(encoding="utf-8"))
    before = capture.base()
    rows: dict[str, str] = {}
    for source in capture.SOURCES:
        for status in ("proposed", "confirmed"):
            for modality in ("alethic", "deontic"):
                constraint = capture.new_constraint(source, status, modality)
                rows[f"new:{source}:{status}:{modality}"] = capture.outcome(
                    before, capture.with_constraint(before, constraint)
                )
    rows["unchanged"] = capture.outcome(before, copy.deepcopy(before))
    smuggled = capture.new_constraint("llm-inferred", "proposed", "deontic")
    smuggled["provenance"]["actor_id"] = "owner:fixture"
    rows["audit-smuggling"] = capture.outcome(before, capture.with_constraint(before, smuggled))
    unknown = capture.new_constraint("llm-inferred", "proposed", "deontic")
    unknown["source"] = "oracle"
    rows["unknown-source"] = capture.outcome(before, capture.with_constraint(before, unknown))
    assert len(baseline["rows"]) == 27
    assert rows == baseline["rows"]
