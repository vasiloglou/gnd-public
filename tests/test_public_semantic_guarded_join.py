"""Guarded join, literal, typed identity and priority negative controls."""
from __future__ import annotations

import ast
import atexit
import dataclasses
import gzip
import hashlib
import io
import json
import runpy
import tempfile
from pathlib import Path

import pytest
import test_public_branch_runtime as corpus

from gnd import semantic_spec as spec
from gnd.model import load_model
from gnd.population import load_population
from gnd.semantic_adapter import adapt_snapshot


def _generic_join_root():
    path = Path(__file__).parent / "fixtures/public-branch-runtime/guarded-join.json.gz"
    assert path.is_file() and not path.is_symlink()
    with path.open("rb") as stream:
        packed = stream.read(32769)
    assert len(packed) <= 32768
    assert hashlib.sha256(packed).hexdigest() == "4486bcab36bbd962d852758bf7e896e966bd9b5f2b1b06b1ccb1fda2e066baf4"
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(131073)
    assert len(raw) <= 131072
    documents = json.loads(raw)
    assert len(documents) == 16
    temporary = tempfile.TemporaryDirectory(prefix="gnd-public-guarded-")
    root = Path(temporary.name)
    for name, text in documents.items():
        assert not Path(name).is_absolute() and ".." not in Path(name).parts
        assert name == "expected.json" or name.startswith(("models/", "cases/"))
        assert isinstance(text, str) and len(text.encode()) <= 16384
        target = root / "tests/fixtures/guarded" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return temporary, root

_TEMPORARY, ROOT = _generic_join_root()
atexit.register(_TEMPORARY.cleanup)
def _case(case_id: str, tmp_path: Path):
    model, population = corpus._build(case_id, tmp_path)
    snapshot = adapt_snapshot(model, population)
    reference = corpus.CASE_BY_ID[case_id]["ref"]
    return next(row for row in snapshot.constraints if row.ref == reference), snapshot


def _fixture(case_id: str):
    root = ROOT / "tests/fixtures/guarded"
    rows = json.loads((root / "expected.json").read_text())["cases"]
    row = next(item for item in rows if item["id"] == case_id)
    model = load_model(root / row["model"])
    population = load_population(root / row["population"], model=model)
    snapshot = adapt_snapshot(model, population)
    index = int(row["constraint_ref"].removeprefix("constraints[").removesuffix("]"))
    return snapshot.constraints[index], snapshot


@pytest.mark.parametrize(
    "case_id,state,witness",
    [
        ("J-1", 0, [["a", "5/1", "1/1"]]),
        ("J-2", 0, [["b", "100/1", "1/1"]]),
        ("J-3", 1, []),
        ("U-G3", -1, []),
        ("X-L1", 0, [[]]),
        ("X-L2", 1, []),
        ("Z-1", 1, []),
        ("A-B5", 0, [["e1"]]),
        ("A-B6", 0, [["e1"]]),
        ("S-1", 1, []),
        ("S-2", 0, [["e1"]]),
    ],
)
def test_direct_join_grounding_and_priority_cases(case_id: str, state: int, witness) -> None:
    constraint, snapshot = _fixture(case_id)
    assert spec.guarded_state(constraint, snapshot) == state
    assert [
        [value.token for value in row] for row in spec.guarded_witness(constraint, snapshot)
    ] == witness


def _replace_relation(snapshot, fact_type: str, rows):
    position = spec.snapshot_relation_index(snapshot, fact_type)
    relations = list(snapshot.relations)
    relations[position] = dataclasses.replace(relations[position], rows=tuple(rows))
    return dataclasses.replace(snapshot, relations=tuple(relations))


def test_shared_variables_use_typed_identity(tmp_path: Path) -> None:
    constraint, snapshot = _fixture("J-2")
    position = spec.snapshot_relation_index(snapshot, "q")
    rows = list(snapshot.relations[position].rows)
    assert rows[1][0] is not None
    rows[1] = (dataclasses.replace(rows[1][0], identity_kind="number"), rows[1][1])
    changed = _replace_relation(snapshot, "q", rows)
    assert spec.guarded_witness(constraint, changed) == []
    mutant = _mutant(
        tmp_path,
        "guarded_bindings",
        "elif not scalar_identical(candidate[position], value):",
        "elif candidate[position].token != value.token:",
    )
    assert mutant["guarded_witness"](constraint, changed) != []


@pytest.mark.parametrize(
    "case_id,function,before,after",
    [
        (
            "J-2",
            "guarded_bindings",
            "elif not scalar_identical(candidate[position], value):",
            "elif False:",
        ),
        (
            "J-3",
            "guarded_bindings",
            "elif not scalar_identical(candidate[position], value):",
            "elif False:",
        ),
        (
            "Z-1",
            "guarded_bindings",
            "or not scalar_identical(value, term.literal)",
            "or False",
        ),
        (
            "P2-152",
            "guarded_result",
            "else comparison_pair_state(left, right, constraint.operator)",
            "else 1",
        ),
        ("P2-155", "guarded_atom_state", "return 0", "return 1"),
        (
            "P2-158",
            "guarded_result",
            'if state >= 0 and constraint.variant == "absence":',
            "if False:",
        ),
        ("U-G3", "guarded_result", "if undecidable:", "if False:"),
        (
            "J-1",
            "guarded_variable_names",
            "names.append(term.variable)",
            "names.insert(0, term.variable)",
        ),
    ],
    ids=[
        "shared-variable-join",
        "repeated-variable",
        "literal-filter",
        "comparison-polarity",
        "atom-polarity",
        "absence-polarity",
        "unknown-priority",
        "first-introduction-order",
    ],
)
def test_guarded_mutations_have_counterexamples(
    case_id: str, function: str, before: str, after: str, tmp_path: Path
) -> None:
    if case_id.startswith("P2-"):
        constraint, snapshot = _case(case_id, tmp_path)
    else:
        constraint, snapshot = _fixture(case_id)
    if case_id == "U-G3":
        constraint = dataclasses.replace(constraint, refused="")
    mutant = _mutant(tmp_path, function, before, after)
    assert mutant["guarded_result"](constraint, snapshot) != spec.guarded_result(
        constraint, snapshot
    )


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

