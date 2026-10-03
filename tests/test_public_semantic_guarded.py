"""Current semantic family controls on reviewed generic branch inputs."""
from __future__ import annotations

import ast
import dataclasses
import runpy
from pathlib import Path

import pytest
import test_public_branch_runtime as corpus

from gnd import semantic_spec as spec
from gnd.semantic_adapter import adapt_snapshot


def _case(case_id: str, tmp_path: Path):
    model, population = corpus._build(case_id, tmp_path)
    snapshot = adapt_snapshot(model, population)
    reference = corpus.CASE_BY_ID[case_id]["ref"]
    return next(row for row in snapshot.constraints if row.ref == reference), snapshot


EXPECTED = {
    "P2-151": (1, []),
    "P2-152": (0, [["e1", "2500/1"]]),
    "P2-153": (0, [["e1", "2500/1"]]),
    "P2-154": (1, []),
    "P2-155": (0, [["e1"]]),
    "P2-156": (0, [["e1"]]),
    "P2-157": (1, []),
    "P2-158": (0, [["e1"]]),
    "P2-159": (0, [["e1"]]),
    "P2-160": (1, []),
    "P2-161": (-1, []),
    "P2-162": (-1, []),
    "P2-163": (-1, []),
}


@pytest.mark.parametrize("case_id", tuple(EXPECTED))
def test_frozen_guarded_cases_match_active_clauses(case_id: str, tmp_path: Path) -> None:
    constraint, snapshot = _case(case_id, tmp_path)
    state, witness = EXPECTED[case_id]
    before = hash(snapshot)
    assert spec.guarded_state(constraint, snapshot) == state
    assert spec.guarded_holds(constraint, snapshot) is (state == 1)
    actual = spec.guarded_witness(constraint, snapshot)
    assert [[value.token for value in row] for row in actual] == witness
    assert hash(snapshot) == before


def _replace_relation(snapshot, fact_type: str, rows):
    position = spec.snapshot_relation_index(snapshot, fact_type)
    relations = list(snapshot.relations)
    relations[position] = dataclasses.replace(relations[position], rows=tuple(rows))
    return dataclasses.replace(snapshot, relations=tuple(relations))


def test_duplicate_bindings_collapse_before_witness_selection(tmp_path: Path) -> None:
    constraint, snapshot = _case("P2-152", tmp_path)
    position = spec.snapshot_relation_index(snapshot, "expense_has_amount")
    rows = snapshot.relations[position].rows
    duplicated = _replace_relation(snapshot, "expense_has_amount", (*rows, rows[-1]))
    expected = spec.guarded_witness(constraint, snapshot)
    assert spec.guarded_witness(constraint, duplicated) == expected
    mutant = _mutant(
        tmp_path,
        "guarded_bindings",
        "return True, names, canonical_distinct_rows(rows)",
        "return True, names, rows",
    )
    assert mutant["guarded_witness"](constraint, duplicated) != expected


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
    path = tmp_path / "guarded_mutant.py"
    path.write_text(source[:start] + segment.replace(before, after) + source[end:])
    return runpy.run_path(str(path))

