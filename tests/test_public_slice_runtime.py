"""Slice/checker regression controls over reviewed generic bounded inputs.
Pure policy return values are test observations, never renewed certificates.
"""
from __future__ import annotations

import atexit
import gzip
import hashlib
import io
import json
import re
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from gnd.address import positional_constraint_ref
from gnd.checker import band, check
from gnd.model import load_model
from gnd.population import load_population


def _public_corpus():
    path = Path(__file__).parent / "fixtures/public-slice-runtime/corpus.json.gz"
    assert path.is_file() and not path.is_symlink()
    with path.open("rb") as stream:
        packed = stream.read(65537)
    assert len(packed) <= 65536
    assert hashlib.sha256(packed).hexdigest() == "22f8d3ed0caddc2598ad131eb6aab55ea59208ed3295aded9ed0ec9739beb1ff"
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(262145)
    assert len(raw) <= 262144
    documents = json.loads(raw)
    assert isinstance(documents, dict) and len(documents) == 34
    temporary = tempfile.TemporaryDirectory(prefix="gnd-public-slice-")
    root = Path(temporary.name)
    for name, text in documents.items():
        assert name in {"cases.json", "expected.json"} or re.fullmatch(r"fixtures/c(?:0[1-9]|1[0-6])/(?:model\.orm\.yaml|population\.yaml)", name)
        assert isinstance(text, str) and len(text.encode("utf-8")) <= 32768
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(text.encode("utf-8"))
    return temporary, root

_TEMPORARY, CORPUS = _public_corpus()
atexit.register(_TEMPORARY.cleanup)
CASES: dict[str, Any] = json.loads((CORPUS / "cases.json").read_text(encoding="utf-8"))
EXPECTED: dict[str, Any] = json.loads((CORPUS / "expected.json").read_text(encoding="utf-8"))
CASE_IDS = tuple(f"C{index:02d}" for index in range(1, 17))


CASE_BY_ID = {row["id"]: row for row in CASES["cases"]}


def _lane():
    """Return the Phase 1 slice surface, or red naming exactly what is absent.

    Two modules, one surface: the verified kernel and the two admitted-value
    bridges that submit to it. The split is section 5.7's price -- a definition
    the pinned verifier cannot translate cannot sit in the file whose erasure
    identity the proof depends on -- and the corpus does not care which module a
    name came from, only that the lane answers.
    """
    try:
        from gnd import proof_bridge, proof_kernel
    except ImportError as error:  # pragma: no cover - the intended RED path
        pytest.fail(
            "INTENDED RED -- the Phase 1 proof lane does not exist. "
            "Specification sections 5.2, 5.3 and 5.5 place phase1_in_scope, "
            "evaluate_phase1_slice, compose_phase1_band and "
            "decide_phase1_assurance in src/gnd/proof_kernel.py, and "
            "adapt_phase1_slice and project_phase1_result in "
            f"src/gnd/proof_bridge.py, which are not importable: {error}"
        )
    return SimpleNamespace(
        **{name: getattr(proof_kernel, name) for name in dir(proof_kernel)},
        adapt_phase1_slice=proof_bridge.adapt_phase1_slice,
        project_phase1_result=proof_bridge.project_phase1_result,
    )


def _fixture_paths(case_id: str) -> tuple[Path, Path]:
    row = CASE_BY_ID[case_id]
    return CORPUS / row["model"], CORPUS / row["population"]


def _load(case_id: str):
    model_path, population_path = _fixture_paths(case_id)
    model = load_model(model_path)
    return model, load_population(population_path, model=model)


def _declared_constraints(model) -> list[tuple[dict[str, Any], str, dict[str, Any] | None]]:
    """Every constraint in the order production constructs its verdicts."""
    rows: list[tuple[dict[str, Any], str, dict[str, Any] | None]] = []
    for fact_type in model.fact_types:
        for index, constraint in enumerate(fact_type.get("constraints") or []):
            rows.append(
                (constraint, positional_constraint_ref(str(fact_type.get("id")), index), fact_type)
            )
    for index, constraint in enumerate(model.constraints):
        rows.append((constraint, positional_constraint_ref(None, index), None))
    return rows


def _normalize_public_witness(offending: list[Any]) -> list[list[str]]:
    """Project today's public witness onto the slice's uniform tuple shape.

    Finding F3: production spells a mandatory witness as flat scalars and a
    frequency witness as one-element lists. This function is the corpus's
    record of that divergence, not a decision about which shape wins.
    """
    rows: list[list[str]] = []
    for item in offending:
        values = item if isinstance(item, (list, tuple)) else [item]
        rows.append([str(value) for value in values])
    return rows


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_every_fixture_admits_under_ordinary_loading(case_id: str) -> None:
    model, population = _load(case_id)
    assert population.matches_validation_marker(model)


def test_declared_siblings_differ_by_exactly_one_fact_row() -> None:
    for child_id, parent_id in (("C02", "C01"), ("C07", "C06")):
        assert CASE_BY_ID[child_id]["mutation_of"] == parent_id
        assert CASE_BY_ID[parent_id]["mutation_sibling"] == child_id
        child_model, child = _load(child_id)
        parent_model, parent = _load(parent_id)
        assert (
            (CORPUS / CASE_BY_ID[child_id]["model"]).read_bytes()
            == (CORPUS / CASE_BY_ID[parent_id]["model"]).read_bytes()
        ), f"{child_id} and {parent_id} must differ in the population alone"
        assert sorted(child.covers) == sorted(parent.covers)
        assert child.instances == parent.instances
        removed = [
            fact
            for fact_type_id, facts in parent.facts.items()
            for fact in facts
            if facts.count(fact) > child.facts.get(fact_type_id, []).count(fact)
        ]
        assert len(removed) == 1, f"{child_id} is not one change from {parent_id}: {removed}"
        assert child_model.fact_types == parent_model.fact_types


def test_the_answer_key_names_the_production_constraint_refs() -> None:
    for case_id in CASE_IDS:
        model, _ = _load(case_id)
        declared = [ref for _, ref, _ in _declared_constraints(model)]
        answered = [row["constraint_ref"] for row in EXPECTED["cases"][case_id]["verdicts"]]
        assert declared == answered, case_id
        assert len(declared) == CASE_BY_ID[case_id]["constraint_count"]


def test_the_amended_cardinality_bound_admits_c10_and_still_refuses_c16() -> None:
    """Finding F1's repair, pinned as data rather than left in prose.

    A14.1 raised the constraint bound from two to three and moved nothing else.
    C10 now sits exactly ON the raised bound, and C16 still exceeds a different
    dimension, so the amendment is measured on both sides: a bound that admitted
    everything would be the other way to make F1 go away.
    """
    admitted = CASES["admitted_cardinality"]
    assert admitted["constraints"] == 3
    assert "section 14" in admitted["source"]
    assert admitted["universe_members"] == 2
    model, _ = _load("C10")
    assert len(_declared_constraints(model)) == admitted["constraints"]
    assert CASE_BY_ID["C10"]["at_admitted_cardinality"] == ["constraints"]
    assert EXPECTED["cases"]["C10"]["contested_by_finding"] == "F1"
    assert EXPECTED["cases"]["C10"]["whole_result_in_scope"] is True
    assert CASE_BY_ID["C16"]["exceeds_admitted_cardinality"] == ["universe_members"]
    assert EXPECTED["cases"]["C16"]["whole_result_in_scope"] is False


PUBLIC_VERDICT_KEYS = (
    "constraint_ref",
    "constraint_type",
    "modality",
    "verdict",
    "public_reason_code",
    "witness",
)


def _public_observation(case_id: str) -> dict[str, Any]:
    """What the CURRENT production path returns, in answer-key shape."""
    model, population = _load(case_id)
    report = check(model, population)
    return {
        "band": band(report),
        "counts": report.counts(),
        "coverage": [
            [fact_type_id, entry.declared, entry.facts]
            for fact_type_id, entry in report.coverage.items()
        ],
        "verdicts": [
            {
                "constraint_ref": verdict.constraint_ref,
                "constraint_type": verdict.constraint_type,
                "modality": verdict.modality,
                "verdict": verdict.verdict,
                "public_reason_code": verdict.reason_code,
                "witness": _normalize_public_witness(verdict.offending_facts),
            }
            for verdict in report.verdicts
        ],
    }


def _public_answer(case_id: str) -> dict[str, Any]:
    answer = EXPECTED["cases"][case_id]
    return {
        "band": answer["band"],
        "counts": answer["counts"],
        "coverage": [list(row) for row in answer["coverage"]],
        "verdicts": [
            {key: row[key] for key in PUBLIC_VERDICT_KEYS} for row in answer["verdicts"]
        ],
    }


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_the_public_answer_holds_against_the_current_checker(case_id: str) -> None:
    """The hand-authored public half, measured against production TODAY.

    This is the corpus's liveness proof: an answer key nothing can contradict
    is not an answer key. It is also the invariant half of the phase -- section
    5.4 moves which code decides an in-scope verdict, not the public result.
    """
    assert _public_observation(case_id) == _public_answer(case_id), case_id


@pytest.mark.parametrize(
    ("case_id", "field", "replacement"),
    [
        ("C02", "band", 0),
        ("C03", "counts", {"pass": 1, "fail": 0, "warning": 0, "unchecked": 0, "vacuous": 0}),
        ("C05", "coverage", [["reviewer_signs_report", "declared", 1]]),
        ("C07", "verdicts", []),
    ],
)
def test_one_change_to_an_answer_breaks_the_public_control(
    case_id: str, field: str, replacement: Any
) -> None:
    """The control above discriminates -- it is not equality with itself.

    Each row mutates one field of one answer IN MEMORY, never on disk, and the
    comparison must reject it. Without this, a comparison that silently
    compared production with production would read exactly the same green.
    """
    mutated = dict(_public_answer(case_id))
    assert mutated[field] != replacement
    mutated[field] = replacement
    assert _public_observation(case_id) != mutated


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_the_slice_result_matches_the_answer_key(case_id: str) -> None:
    """INTENDED RED. The adapter, the in-scope predicate, the evaluator, the
    band composition, the projection and the assurance decision do not exist."""
    lane = _lane()
    answer = EXPECTED["cases"][case_id]
    model, population = _load(case_id)
    verdicts = []
    for row, (constraint, ref, fact_type) in zip(
        answer["verdicts"], _declared_constraints(model), strict=True
    ):
        value = lane.adapt_phase1_slice(model, population, constraint, fact_type, ref)
        if not row["in_scope"]:
            assert value is None, f"{case_id} {ref} must take the refusal branch"
            continue
        assert value is not None, f"{case_id} {ref} is inside the slice"
        assert lane.phase1_in_scope(value) is True
        verdict = lane.evaluate_phase1_slice(value)
        assert verdict.constraint_ref == ref
        assert verdict.family == row["slice_family"]
        assert verdict.modality == row["modality"]
        assert verdict.verdict == row["verdict"]
        assert verdict.reason_code == row["slice_reason_code"]
        assert [list(item) for item in verdict.witness] == row["witness"]
        verdicts.append(verdict)

    if answer["whole_result_in_scope"]:
        assert lane.compose_phase1_band(tuple(verdicts)) == answer["band"]
        projection = lane.project_phase1_result(
            tuple(verdicts),
            band=answer["band"],
            coverage=tuple(tuple(row) for row in answer["coverage"]),
            applicable=answer["applicable"],
            current=answer["current"],
            in_scope=answer["whole_result_in_scope"],
        )
        assert projection["exit_code"] == answer["band"]
        assert projection["acceptance_ready"] == answer["acceptance_ready"]
        assert projection["counts"] == answer["counts"]

    decision, assurance = lane.decide_phase1_assurance(
        band=answer["band"],
        applicable=answer["applicable"],
        current=answer["current"],
        in_scope=answer["whole_result_in_scope"],
    )
    assert decision == answer["decision"], case_id
    assert assurance == answer["assurance"], case_id


def test_modality_alone_separates_the_twin_rows() -> None:
    """INTENDED RED. C02 and C03 read one population file; only the modality
    word differs, and it must move the verdict and the band and nothing else."""
    lane = _lane()
    results = {}
    for case_id in ("C02", "C03"):
        model, population = _load(case_id)
        constraint, ref, fact_type = _declared_constraints(model)[0]
        value = lane.adapt_phase1_slice(model, population, constraint, fact_type, ref)
        assert value is not None
        verdict = lane.evaluate_phase1_slice(value)
        results[case_id] = (verdict, lane.compose_phase1_band((verdict,)))
    fail_verdict, fail_band = results["C02"]
    warn_verdict, warn_band = results["C03"]
    assert (fail_verdict.verdict, fail_band) == ("fail", 1)
    assert (warn_verdict.verdict, warn_band) == ("warning", 0)
    assert fail_verdict.witness == warn_verdict.witness


def test_each_precedence_edge_is_reachable_through_the_lane() -> None:
    """INTENDED RED. 1 > 4 > 2 > 0, each edge decided by the composition."""
    lane = _lane()
    for case_id, expected_band in (("C10", 1), ("C11", 4), ("C12", 2), ("C01", 0)):
        model, population = _load(case_id)
        verdicts = []
        for constraint, ref, fact_type in _declared_constraints(model):
            value = lane.adapt_phase1_slice(model, population, constraint, fact_type, ref)
            assert value is not None, f"{case_id} {ref}"
            verdicts.append(lane.evaluate_phase1_slice(value))
        assert lane.compose_phase1_band(tuple(verdicts)) == expected_band, case_id

