"""Partial migration accounting cannot masquerade as phase acceptance."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from support.public_migration import MigrationRefusal, load_case_map, strict_json, validate_case_map

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / ".gnd-planning/milestones/public-launch/migration"


def reviewed_rows():
    return tuple(row for name in ("b3-initial", "b3-reviewed", "b3-extra")
                 for row in load_case_map(MIGRATION / f"{name}-case-map.jsonl.gz"))


def original_identities():
    raw = (MIGRATION / "original-identities.json").read_bytes()
    progress = strict_json((MIGRATION / "progress.json").read_text())
    assert hashlib.sha256(raw).hexdigest() == progress["original_identities_sha256"]
    originals = strict_json(raw.decode())
    assert len(originals) == 5331
    assert set(originals) == {f"source-case-{index:05d}" for index in range(5331)}
    return originals


def test_partial_slices_refuse_complete_original_accounting():
    rows = reviewed_rows()
    originals = original_identities()
    selected = {node for row in rows for node in row["target_nodes"]}
    with pytest.raises(MigrationRefusal, match="missing-original"):
        validate_case_map(rows, originals=originals, collected=selected)


def test_progress_retains_unresolved_cases_and_refuses_handoff():
    rows = reviewed_rows()
    originals = original_identities()
    progress = json.loads((MIGRATION / "progress.json").read_text())
    assert len(rows) == len({row["source_node"] for row in rows}) == 357
    assert {row["source_node"] for row in rows} <= set(originals)
    assert progress["reviewed_dispositions"] == len(rows)
    assert progress["unresolved_definitions"] == len(originals) - len(rows) == 4974
    assert progress["status"] == "incomplete"
    assert progress["handoff_authorized"] is False
    validate_case_map(rows, originals={row["source_node"]: originals[row["source_node"]]
                                     for row in rows},
                      collected={node for row in rows for node in row["target_nodes"]})


def test_static_target_selectors_resolve_to_actual_test_definitions():
    import ast
    for row in reviewed_rows():
        for node in row["target_nodes"]:
            relative, name = node.split("::")
            name = name.split("[", 1)[0]
            tree = ast.parse((ROOT / relative).read_text())
            assert name in {item.name for item in tree.body if isinstance(item, ast.FunctionDef)}
