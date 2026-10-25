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
        # A validation refusal's text names no rule id; the cause's issues do.
        rule_ids = [issue.rule_id for issue in getattr(error.__cause__, "issues", ())]
        return _evolve_service_exit(error), " ".join([str(error), *rule_ids])
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


# ---- implementation tests (spec section 8, T6-T13) --------------------------

MINIMAL_INDUCTION = CASES["loader"][0]["constraint"]["provenance"]["induction"]
REVIEW = ".gnd-planning/milestones/demo/003-review.md"


def _induced(status: str = "proposed", modality: str = "deontic", **provenance: Any) -> dict:
    return {
        "type": "uniqueness",
        "roles": ["title"],
        "source": "induced",
        "status": status,
        "modality": modality,
        "provenance": {"induction": copy.deepcopy(MINIMAL_INDUCTION), **provenance},
    }


@pytest.mark.parametrize("reason", sorted(EXPECTED["reasons"]))
def test_t6_every_named_refusal_maps_to_exit_3(reason: str) -> None:
    from gnd.evolve import EvolutionError
    from gnd.evolve.cli_service import _evolve_service_exit

    assert _evolve_service_exit(EvolutionError(EXPECTED["reasons"][reason])) == 3


def test_t7_audit_refusal_precedes_the_induction_refusal() -> None:
    before = _evolution_before()
    candidate = copy.deepcopy(before)
    smuggled = {
        "type": "uniqueness",
        "roles": ["title"],
        "source": "explicit",
        "status": "confirmed",
        "modality": "alethic",
        "provenance": {"user_quote": "q", "induction": {}, "actor_id": "owner:fixture"},
    }
    candidate["fact_types"][0]["constraints"].append(smuggled)
    assert _gate_outcome(before, candidate) == (
        "operation audit actor/origin/time fields cannot enter constraint provenance"
    )


def test_t7_refusals_keep_candidate_order() -> None:
    # The first defective constraint in candidate order is reported, as before
    # IK2: an older-branch refusal ahead of an induced one wins, and vice versa.
    before = _evolution_before()
    explicit = {
        "type": "uniqueness",
        "roles": ["title"],
        "source": "explicit",
        "status": "confirmed",
        "modality": "alethic",
        "provenance": {"user_quote": "q"},
    }
    induced_alethic = _induced("proposed", "alethic")
    for first, second, expected in (
        (explicit, induced_alethic, "new or changed constraints must be"),
        (induced_alethic, explicit, "new induced constraints must be proposed/deontic"),
    ):
        candidate = copy.deepcopy(before)
        candidate["fact_types"][0]["constraints"].extend([first, second])
        assert _gate_outcome(before, candidate).startswith(expected)


@pytest.mark.parametrize(
    "provenance",
    [[], "text", 7, None, {"induction": []}, {"induction": "x"}, {"induction": None}],
    ids=["list", "str", "int", "null", "induction-list", "induction-str", "induction-null"],
)
@pytest.mark.parametrize("source", ["induced", "explicit", "llm-inferred"])
def test_t8_gate_is_total_over_hostile_provenance(source: str, provenance: Any) -> None:
    before = _evolution_before()
    for status in ("proposed", "confirmed", None):
        candidate = copy.deepcopy(before)
        constraint: dict[str, Any] = {"type": "uniqueness", "roles": ["title"], "source": source}
        if status is not None:
            constraint["status"] = status
        constraint["provenance"] = provenance
        candidate["fact_types"][0]["constraints"].append(constraint)
        _gate_outcome(before, candidate)  # raises nothing but EvolutionError


def test_t9_status_change_matching_is_linear(monkeypatch: pytest.MonkeyPatch) -> None:
    from gnd.evolve import service

    count = 2000
    before = _evolution_before()
    candidate = copy.deepcopy(before)
    for index in range(count):
        induction = copy.deepcopy(MINIMAL_INDUCTION)
        induction["examples"] = [f"case-{index:05d}"]
        proposed = _induced()
        proposed["provenance"]["induction"] = induction
        confirmed = _induced("confirmed", "alethic", reviewed_in=REVIEW)
        confirmed["provenance"]["induction"] = copy.deepcopy(induction)
        before["fact_types"][0]["constraints"].append(proposed)
        candidate["fact_types"][0]["constraints"].append(confirmed)
    calls = 0
    real = service.canonical_json_text

    def counted(value: Any) -> str:
        nonlocal calls
        calls += 1
        return real(value)

    monkeypatch.setattr(service, "canonical_json_text", counted)
    assert _gate_outcome(before, candidate) == "admitted"
    total = len(service._constraints(before)) + len(service._constraints(candidate))
    assert calls <= 2 * total


def test_t10_modality_policy_messages() -> None:
    from gnd.model._validation import _rule_modality_policy

    document = _evolution_before()
    rules = document["fact_types"][0]["constraints"]
    rules.append(_induced("proposed", "alethic"))
    for source in ("llm-inferred", "common-sense"):
        rules.append(
            {"type": "frequency", "roles": ["title"], "source": source, "status": "proposed",
             "modality": "alethic"}
        )
    messages = [issue.message for issue in _rule_modality_policy(document)]
    # The llm-inferred/common-sense sentences are byte-identical to base commit B.
    tail = "unconfirmed llm-inferred/common-sense constraints default to deontic until user-confirmed (D-03)"
    assert messages == [
        (
            "unconfirmed induced uniqueness constraint carries modality 'alethic' — induced "
            "constraints default to deontic until reviewed (D-03)"
        ),
        f"unconfirmed llm-inferred frequency constraint carries modality 'alethic' — {tail}",
        f"unconfirmed common-sense frequency constraint carries modality 'alethic' — {tail}",
    ]


def _coverage(tmp_path: Path, document: dict[str, Any]) -> tuple[dict[str, Any], str]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    model = tmp_path / "model.orm.json"
    model.write_text(json.dumps(document), encoding="utf-8")
    payload = run_main(["coverage", str(model), "--format", "json"], capture_stderr=False)
    text = run_main(["coverage", str(model)], capture_stderr=False)
    assert payload.returncode == 0 and text.returncode == 0
    return json.loads(payload.stdout), text.stdout.decode("utf-8")


def _coverage_validator() -> Any:
    from jsonschema import Draft202012Validator

    schema = json.loads((REPO_ROOT / "src/gnd/coverage.schema.json").read_text(encoding="utf-8"))
    return Draft202012Validator(schema)


EXPECTED_INDUCED_ROW = {
    "address": "fact_types[work_item_has_title].constraints[1]",
    "status": "proposed",
    "modality": "deontic",
    "inducer": {"name": "gnd-discover", "version": "0.1.0"},
    "method": "gnd-discover",
    "manifest_sha256": "a" * 64,
    "support": {"numerator": 2, "denominator": 3},
    "evidence": [{"ref": "populations/p1.json", "sha256": "b" * 64}],
}


def test_t11_coverage_lists_induced_constraints_under_v5(tmp_path: Path) -> None:
    document = _evolution_before()
    document["fact_types"][0]["constraints"].append(_induced())
    payload, text = _coverage(tmp_path, document)
    assert payload["schema_version"] == 5
    assert payload["induced"] == [EXPECTED_INDUCED_ROW]
    assert list(_coverage_validator().iter_errors(payload)) == []
    assert "\nINDUCED\n" in text
    assert (
        "  fact_types[work_item_has_title].constraints[1] proposed/deontic inducer=gnd-discover@0.1.0 "
        "method=gnd-discover support=2/3 manifest=" + "a" * 64
    ) in text
    assert f"    evidence populations/p1.json {'b' * 64}" in text


def test_t11_coverage_without_induced_keeps_v3_and_no_section(tmp_path: Path) -> None:
    payload, text = _coverage(tmp_path, _evolution_before())
    assert payload["schema_version"] == 3
    assert "induced" not in payload
    assert "INDUCED" not in text
    assert list(_coverage_validator().iter_errors(payload)) == []


def test_t11_coverage_with_derivation_and_induced_is_v6(tmp_path: Path) -> None:
    corpus = REPO_ROOT / "tests" / "fixtures" / "phase3-consumers"
    document = YAML(typ="safe").load((corpus / "eligibility.orm.yaml").read_text(encoding="utf-8"))
    host = next(item for item in document["fact_types"] if "derivation_rule" not in item)
    constraint = _induced()
    constraint["roles"] = [host["roles"][0]["role_name"]]
    host.setdefault("constraints", []).append(constraint)
    payload, _ = _coverage(tmp_path, document)
    assert payload["schema_version"] == 6
    assert "derivation" in payload["census"]
    assert len(payload["induced"]) == 1
    assert list(_coverage_validator().iter_errors(payload)) == []


def test_t11_coverage_schema_refuses_induced_on_v3_and_its_absence_on_v5(tmp_path: Path) -> None:
    validator = _coverage_validator()
    plain, _ = _coverage(tmp_path / "plain", _evolution_before())
    document = _evolution_before()
    document["fact_types"][0]["constraints"].append(_induced())
    induced, _ = _coverage(tmp_path / "induced", document)
    with_key = {**plain, "induced": induced["induced"]}
    without_key = {key: value for key, value in induced.items() if key != "induced"}
    assert list(validator.iter_errors(with_key))
    assert list(validator.iter_errors(without_key))


def test_t12_verbalization_carries_the_induction_block(tmp_path: Path) -> None:
    from gnd.model_verbalization import render_model_verbalization

    document = _evolution_before()
    document["fact_types"][0]["constraints"].append(_induced())
    model = tmp_path / "model.orm.json"
    model.write_text(json.dumps(document), encoding="utf-8")
    text = render_model_verbalization(str(model))
    assert "[from induced, proposed; modality=deontic]" in text
    assert '"manifest_sha256":"' + "a" * 64 + '"' in text


def test_t12_session_verdicts_accept_the_induced_source() -> None:
    from gnd.exp.session_eval import VerifierVerdict

    fields = VerifierVerdict.model_fields
    assert "induced" in str(fields["source"].annotation)


def test_t12_check_report_over_an_induced_model_validates(tmp_path: Path) -> None:
    from jsonschema import Draft202012Validator

    from gnd.report import load_report_schema

    document = _evolution_before()
    document["fact_types"][0]["constraints"].append(_induced())
    model = tmp_path / "model.orm.json"
    model.write_text(json.dumps(document), encoding="utf-8")
    population = tmp_path / "population.yaml"
    population.write_text(
        "population:\n  model: model.orm.json\n  source: fixture\n"
        "  covers: [work_item_has_title]\ninstances: {}\nfacts:\n  work_item_has_title: []\n",
        encoding="utf-8",
    )
    result = run_main(["check", str(model), str(population), "--format", "json"],
                      capture_stderr=False)
    report = json.loads(result.stdout)
    sources = {verdict["source"] for verdict in report["verdicts"]}
    assert "induced" in sources
    assert list(Draft202012Validator(load_report_schema()).iter_errors(report)) == []


def test_t13_rai_import_default_modality_follows_the_d03_row() -> None:
    from gnd.rai_import import RaiImportError, _default_modality

    proposed = _induced()
    assert _default_modality(proposed, "/c") == "deontic"
    assert _default_modality(_induced("confirmed", reviewed_in=REVIEW), "/c") == "alethic"
    with pytest.raises(RaiImportError, match="induced/confirmed requires reviewed_in"):
        _default_modality(_induced("confirmed"), "/c")


# ---- adversarial-review regressions (notes/phase-IK2-agent-review.md) -------
# Successor cases beside the approved corpus: they add inputs, never change an
# approved answer.


def _validate(tmp_path: Path, document: dict[str, Any], *, yaml_text: str | None = None) -> str:
    path = tmp_path / ("model.orm.yaml" if yaml_text is not None else "model.orm.json")
    path.write_text(yaml_text if yaml_text is not None else json.dumps(document), encoding="utf-8")
    result = run_main(["validate", str(path)])
    return f"{result.returncode} " + (result.stdout + result.stderr).decode("utf-8")


@pytest.mark.parametrize(
    "support",
    [{"numerator": 10.0, "denominator": 1.0}, {"numerator": 2.0, "denominator": 3}],
    ids=["both-float", "numerator-float"],
)
def test_r1_float_support_counts_are_refused(tmp_path: Path, support: dict) -> None:
    document = _evolution_before()
    constraint = _induced()
    constraint["provenance"]["induction"]["support"] = support
    constraint["provenance"]["induction"]["examples"] = [f"case-{i}" for i in range(10)]
    document["fact_types"][0]["constraints"].append(constraint)
    outcome = _validate(tmp_path, document)
    assert outcome.startswith("3 ") and "[semantic:induced-provenance]" in outcome, outcome


def test_r2_induction_key_under_another_source_validates_as_at_base(tmp_path: Path) -> None:
    # IK2-D3: validate is unchanged for every source but induced, so a model
    # valid at B (an llm-inferred provenance carrying an `induction` key with a
    # NaN) stays valid; only the evolve gate refuses such a block.
    document = _evolution_before()
    document["fact_types"][0]["constraints"].append({
        "type": "uniqueness", "roles": ["title"], "source": "llm-inferred",
        "status": "proposed", "modality": "deontic", "rationale": "r",
        "provenance": {"rationale_world_fact": "w", "induction": {"conf": "__NAN__"}},
    })
    text = json.dumps(document).replace('"__NAN__"', ".nan")
    assert _validate(tmp_path, document, yaml_text=text).startswith("0 ")


def _two_title_facts() -> dict[str, Any]:
    document = _evolution_before()
    second = copy.deepcopy(document["fact_types"][0])
    second.update(id="work_item_has_alt_title", reading="{WorkItem} has alt {Title}", constraints=[])
    document["fact_types"].append(second)
    return document


@pytest.mark.parametrize("target", ["other-fact-type", "top-level"])
def test_r3_confirmation_cannot_move_the_rule(target: str) -> None:
    before = _two_title_facts()
    candidate = copy.deepcopy(before)
    before["fact_types"][0]["constraints"].append(_induced())
    confirmed = _induced("confirmed", "alethic", reviewed_in=REVIEW)
    if target == "top-level":
        candidate["constraints"].append(confirmed)
    else:
        candidate["fact_types"][1]["constraints"].append(confirmed)
    assert _gate_outcome(before, candidate) == EXPECTED["reasons"]["R-I3"]


def test_r3_confirmation_in_place_is_still_admitted() -> None:
    before = _two_title_facts()
    candidate = copy.deepcopy(before)
    before["fact_types"][0]["constraints"].append(_induced())
    candidate["fact_types"][0]["constraints"].append(
        _induced("confirmed", "alethic", reviewed_in=REVIEW)
    )
    assert _gate_outcome(before, candidate) == "admitted"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("inducer.name", "gnd-discover\n"),
        ("inducer.version", "0.1.0\n"),
        ("method", "gnd-discover\n"),
        ("counterexamples", ["case-1\n"]),
    ],
)
def test_r5_trailing_newline_in_every_patterned_field_is_refused(
    tmp_path: Path, field: str, value: Any
) -> None:
    document = _evolution_before()
    constraint = _induced()
    induction = constraint["provenance"]["induction"]
    if field.startswith("inducer."):
        induction["inducer"][field.split(".")[1]] = value
    else:
        induction[field] = value
    document["fact_types"][0]["constraints"].append(constraint)
    outcome = _validate(tmp_path, document)
    assert outcome.startswith("3 ") and "[semantic:induced-provenance]" in outcome, outcome


def test_r5_raw_counterexample_value_is_refused(tmp_path: Path) -> None:
    document = _evolution_before()
    constraint = _induced()
    constraint["provenance"]["induction"]["counterexamples"] = ["Jane Doe"]
    document["fact_types"][0]["constraints"].append(constraint)
    assert _validate(tmp_path, document).startswith("3 ")


def test_r5_top_level_induction_nan_is_screened(tmp_path: Path) -> None:
    document = _evolution_before()
    constraint = _induced()
    constraint["provenance"]["induction"]["confidence"] = {"value": "__NAN__", "formula": "f"}
    document["fact_types"][0]["constraints"].append(constraint)
    text = json.dumps(document).replace('"__NAN__"', ".nan")
    # The same block at the top level, where constraints[0] is the host path.
    top = json.loads(json.dumps(document).replace('"__NAN__"', "0.5"))
    top["constraints"] = [top["fact_types"][0]["constraints"].pop()]
    top_text = json.dumps(top).replace('"value": 0.5', '"value": .nan')
    for yaml_text in (text, top_text):
        outcome = _validate(tmp_path, document, yaml_text=yaml_text)
        assert outcome.startswith("3 ") and "provenance.induction.confidence.value" in outcome


def test_r5_reconfirming_a_confirmed_rule_is_refused() -> None:
    before = _evolution_before()
    candidate = copy.deepcopy(before)
    before["fact_types"][0]["constraints"].append(
        _induced("confirmed", "alethic", reviewed_in=REVIEW)
    )
    candidate["fact_types"][0]["constraints"].append(
        _induced("confirmed", "alethic", reviewed_in=REVIEW + ".2")
    )
    assert _gate_outcome(before, candidate) == EXPECTED["reasons"]["R-I3"]


def _top_level_induced() -> dict[str, Any]:
    constraint = _induced()
    del constraint["roles"]
    constraint.update(
        scope="external",
        role_refs=[
            {"fact_type": "work_item_has_title", "role": "title"},
            {"fact_type": "work_item_has_alt_title", "role": "title"},
        ],
    )
    return constraint


def test_r5_coverage_rows_carry_status_address_and_location(tmp_path: Path) -> None:
    document = _two_title_facts()
    named = _induced("confirmed", "alethic", reviewed_in=REVIEW)
    named["id"] = "ik_title"
    document["fact_types"][0]["constraints"].append(named)
    document["constraints"].append(_top_level_induced())
    payload, _ = _coverage(tmp_path, document)
    assert [(row["address"], row["status"], row["modality"]) for row in payload["induced"]] == [
        ("constraint:ik_title", "confirmed", "alethic"),
        ("constraints[0]", "proposed", "deontic"),
    ]


def test_r5_schema_v1_session_verdict_accepts_induced() -> None:
    from gnd.exp.session_eval import _VerifierVerdictV1

    assert "induced" in str(_VerifierVerdictV1.model_fields["source"].annotation)


def test_r5_coverage_schema_refuses_an_empty_induced_list(tmp_path: Path) -> None:
    document = _evolution_before()
    document["fact_types"][0]["constraints"].append(_induced())
    payload, _ = _coverage(tmp_path, document)
    assert list(_coverage_validator().iter_errors({**payload, "induced": []}))


@pytest.mark.parametrize("numerator", ["0", "1_0", "0x0"], ids=["zero", "underscore", "hex"])
def test_r1_followup_yaml_integer_forms_are_exact_integers(tmp_path: Path, numerator: str) -> None:
    # IK4 review: ruamel's round-trip loader reads `0`, `1_0` and hex as
    # ScalarInt, an int subclass; R1's fix refused them as non-integers.
    document = _evolution_before()
    constraint = _induced()
    constraint["provenance"]["induction"]["support"] = {"numerator": "__N__", "denominator": 10}
    document["fact_types"][0]["constraints"].append(constraint)
    text = json.dumps(document).replace('"__N__"', numerator)
    assert _validate(tmp_path, document, yaml_text=text).startswith("0 ")
