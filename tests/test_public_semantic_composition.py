"""Current semantic family controls on reviewed generic branch inputs."""
from __future__ import annotations

import ast
import runpy
from pathlib import Path

import pytest
import test_public_branch_runtime as corpus

from gnd import semantic_spec as spec
from gnd.semantic_adapter import adapt_snapshot, canonical_scalar

CASES = tuple(
    f"P2-{index:03d}"
    for index in range(1, 190)
    if corpus.CASE_BY_ID[f"P2-{index:03d}"].get("ref") is not None
)


def _case(case_id: str, tmp_path: Path):
    model, population = corpus._build(case_id, tmp_path)
    snapshot = adapt_snapshot(model, population)
    reference = corpus.CASE_BY_ID[case_id]["ref"]
    constraint = next(row for row in snapshot.constraints if row.ref == reference)
    return constraint, snapshot, corpus.EXPECTED["answers"][case_id]


def _token(value) -> str:
    scalar = canonical_scalar(value, None)
    assert scalar is not None
    return scalar.token


def _expected_witness(constraint, expected) -> list[list[str]]:
    result: list[list[str]] = []
    names = spec.guarded_variable_names(constraint) if constraint.family == "guarded" else ()
    for item in expected["witness"]:
        if isinstance(item, dict):
            values = [item[name] for name in names] if names else list(item.values())
            result.append([_token(value) for value in values])
        else:
            values = item if isinstance(item, list) else [item]
            result.append([_token(value) for value in values])
    return result


@pytest.mark.parametrize("case_id", CASES)
def test_verdict_composition_matches_every_frozen_constraint_case(
    case_id: str, tmp_path: Path
) -> None:
    constraint, snapshot, expected = _case(case_id, tmp_path)
    before = hash(snapshot)
    verdict, reason, witness = spec.verdict_of(constraint, snapshot)
    assert verdict == expected["verdict"]
    assert reason == expected.get("reason_code")
    actual = [[value.token for value in row] for row in witness]
    assert sorted(actual) == sorted(_expected_witness(constraint, expected))
    state, family_rows = spec.snapshot_family_result(constraint, snapshot)
    if state == 0:
        assert witness == tuple(tuple(row) for row in family_rows)
    assert isinstance(witness, tuple)
    assert all(isinstance(row, tuple) for row in witness)
    assert hash(snapshot) == before


@pytest.mark.parametrize("case_id", tuple(f"P2-{index:03d}" for index in range(165, 190)))
def test_shared_applicability_cases_hit_the_exact_resolution_stage(
    case_id: str, tmp_path: Path
) -> None:
    constraint, snapshot, expected = _case(case_id, tmp_path)
    reason = expected.get("slice_reason") or expected.get("reason_code")
    if reason == "coverage-omission" or reason == "empty-subject":
        wanted = "vacuous-" + reason
    elif reason == "no-observable-subjects" or reason == "zero-row-join":
        wanted = "evaluate"
    else:
        wanted = "unchecked-" + reason
    assert spec.applicability_of(constraint, snapshot) == wanted


@pytest.mark.parametrize(
    "case_id,function,before,after",
    [
        (
            "P2-165",
            "applicability_of",
            "if subjects[index] not in snapshot.covers:",
            "if False:",
        ),
        (
            "P2-169",
            "applicability_of",
            'if constraint.family == "guarded" and empty_count > 0:',
            "if False:",
        ),
        (
            "P2-164",
            "applicability_of",
            'if constraint.family == "textual":',
            "if False:",
        ),
        (
            "P2-180",
            "sequence_join_reason",
            'return "join-disconnected"',
            'return ""',
        ),
        (
            "P2-188",
            "sequence_join_reason",
            'return "join-anchor-ambiguous"',
            'return ""',
        ),
        (
            "P2-170",
            "verdict_of",
            "if roster_position >= 0 and len(snapshot.rosters[roster_position].members) == 0:",
            "if False:",
        ),
        (
            "P2-175",
            "verdict_of",
            "if joined_pass_is_empty(constraint, snapshot):",
            "if False:",
        ),
        (
            "P2-153",
            "verdict_of",
            'if constraint.modality == "deontic":',
            "if False:",
        ),
        (
            "P2-152",
            "verdict_of",
            "witness = tuple(tuple(row) for row in rows)",
            "witness = ()",
        ),
        (
            "P2-046",
            "snapshot_family_result",
            'if constraint.family == "ring":',
            "if False:",
        ),
    ],
    ids=[
        "coverage-before-empty",
        "guarded-any-empty",
        "textual-precedence",
        "join-disconnected",
        "anchor-ambiguous",
        "object-pass-vacuity",
        "joined-pass-vacuity",
        "modality",
        "witness-preservation",
        "exact-family-dispatch",
    ],
)
def test_resolution_stage_mutations_have_frozen_counterexamples(
    case_id: str, function: str, before: str, after: str, tmp_path: Path
) -> None:
    constraint, snapshot, _ = _case(case_id, tmp_path)
    mutant = _mutant(tmp_path, function, before, after)
    assert mutant["verdict_of"](constraint, snapshot) != spec.verdict_of(constraint, snapshot)


def _mutant(tmp_path: Path, function: str, before: str, after: str):
    source = Path(spec.__file__).read_text()
    node = next(
        item
        for item in ast.parse(source).body
        if isinstance(item, ast.FunctionDef) and item.name == function
    )
    segment = ast.get_source_segment(source, node)
    assert segment is not None and segment.count(before) == 1
    lines = source.splitlines(keepends=True)
    start = sum(len(line) for line in lines[: node.lineno - 1])
    end = sum(len(line) for line in lines[: node.end_lineno])
    path = tmp_path / "composition_mutant.py"
    path.write_text(source[:start] + segment.replace(before, after) + source[end:])
    return runpy.run_path(str(path))

