"""Executable contract for complete, deterministic model verbalization."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from gnd.model import load_model

REPO_ROOT = Path(__file__).resolve().parent.parent
EVOLUTION_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "phase4_reference" / "evolution.json"
FULL_VOCABULARY = REPO_ROOT / "tests" / "fixtures" / "models" / "full_vocabulary.orm.yaml"

CASE_NAMES = [
    "evolution-safe-additive",
    "evolution-rename-delete-blast-radius",
    "evolution-concurrent-cas-refusal",
    "evolution-clean-and-drift-linked-conformance",
]
EXPECTED_EVIDENCE = {
    "proposal",
    "preview",
    "before_model",
    "candidate_model",
    "verbalization",
    "validation",
    "cas",
    "linked_project_conformance",
    "affected_code",
    "final_record_identity",
}


def _fixture() -> dict[str, Any]:
    return json.loads(EVOLUTION_FIXTURE.read_text(encoding="utf-8"))


def _constraint_inventory(model: Any) -> list[tuple[str, dict[str, Any]]]:
    inventory: list[tuple[str, dict[str, Any]]] = []
    for fact_type in model.fact_types:
        host = f"fact_types[{fact_type['id']}]"
        inventory.extend((host, item) for item in fact_type.get("constraints", []))
    inventory.extend(("model", item) for item in model.constraints)
    return inventory


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def test_exact_four_case_corpus_is_digest_bound_and_inventory_complete(tmp_path: Path) -> None:
    """Fixture integrity runs before any deliberately missing production import."""

    fixture = _fixture()
    rows = fixture["cases"]
    assert fixture["machine_label_owner"] == "cases[].name"
    assert [row["name"] for row in rows] == CASE_NAMES
    assert len({row["name"] for row in rows}) == 4

    for row_index, row in enumerate(rows):
        assert EXPECTED_EVIDENCE <= set(row["expected"])
        for blob_name in ("before_model", "candidate_model"):
            blob = row["inputs"][blob_name]
            assert set(blob) == {"media_type", "encoding", "text", "sha256"}
            assert blob["media_type"] == "application/yaml"
            assert blob["encoding"] == "utf-8"
            actual = hashlib.sha256(blob["text"].encode(blob["encoding"])).hexdigest()
            assert actual == blob["sha256"]

            path = tmp_path / f"{row_index}-{blob_name}.orm.yaml"
            path.write_bytes(blob["text"].encode(blob["encoding"]))
            load_model(str(path))

    rename_row = rows[1]
    assert "Plan 04-06" in rename_row["expected"]["extension_owner"]
    assert all("interruption" not in row["name"] for row in rows)


def test_full_vocabulary_rendering_is_byte_stable_and_has_one_terminal_newline() -> None:
    from gnd.model_verbalization import render_model_verbalization

    model = load_model(str(FULL_VOCABULARY))
    first = render_model_verbalization(model)
    second = render_model_verbalization(model)

    assert first.encode("utf-8") == second.encode("utf-8")
    assert first.endswith("\n")
    assert not first.endswith("\n\n")


def test_full_vocabulary_coverage_is_derived_from_the_loaded_model() -> None:
    from gnd.model_verbalization import render_model_verbalization

    model = load_model(str(FULL_VOCABULARY))
    rendered = render_model_verbalization(model)

    for object_type in model.object_types:
        assert rendered.count(f"[object-type:{object_type['id']}]") == 1
    for fact_type in model.fact_types:
        assert rendered.count(f"[fact-type:{fact_type['id']}]") == 1
        for role in fact_type.get("roles", []):
            locator = f"[role:{fact_type['id']}:{role['role_name']}]"
            assert rendered.count(locator) == 1

    expected_constraints = _constraint_inventory(model)
    rendered_constraint_lines = [
        line for line in rendered.splitlines() if line.startswith("[constraint:")
    ]
    assert len(rendered_constraint_lines) == len(expected_constraints)

    # Compare multisets so even byte-identical duplicate constraints remain visible.
    expected_canonical = Counter(_canonical(item) for _, item in expected_constraints)
    rendered_canonical = Counter(
        line.split(" canonical=", 1)[1] for line in rendered_constraint_lines
    )
    assert rendered_canonical == expected_canonical


def test_constraint_lifecycle_and_archived_proposals_are_not_conflated() -> None:
    from gnd.model_verbalization import render_model_verbalization

    model = load_model(str(FULL_VOCABULARY))
    rendered = render_model_verbalization(model)

    for _host, constraint in _constraint_inventory(model):
        canonical = _canonical(constraint)
        line = next(line for line in rendered.splitlines() if f" canonical={canonical}" in line)
        for field in ("source", "status", "modality"):
            assert f"{field}={constraint[field]}" in line
        if constraint.get("rationale"):
            assert f"rationale={json.dumps(constraint['rationale'], ensure_ascii=False)}" in line

    archived_lines = [
        line for line in rendered.splitlines() if line.startswith("[archived-proposal:")
    ]
    assert len(archived_lines) == len(model.rejected_proposals)
    assert all("archived=true" in line and "status=rejected" in line for line in archived_lines)


def test_complete_render_includes_model_relationship_and_population_surfaces() -> None:
    from gnd.model_verbalization import render_model_verbalization

    model = load_model(str(FULL_VOCABULARY))
    rendered = render_model_verbalization(model)

    for object_type in model.object_types:
        canonical = _canonical(object_type)
        assert canonical in rendered
        if object_type.get("subtype_of"):
            assert "subtype_of=" in next(
                line
                for line in rendered.splitlines()
                if line.startswith(f"[object-type:{object_type['id']}]")
            )
        if object_type.get("derivation_rule"):
            assert "derivation_rule=" in rendered
        if object_type.get("reference"):
            assert "reference=" in rendered

    for fact_type in model.fact_types:
        line = next(
            line
            for line in rendered.splitlines()
            if line.startswith(f"[fact-type:{fact_type['id']}]")
        )
        assert f"reading={json.dumps(fact_type['reading'], ensure_ascii=False)}" in line
        if fact_type.get("objectification"):
            assert "objectification=" in line
        if fact_type.get("derivation_rule"):
            assert "derivation_rule=" in line
        if fact_type.get("sample_population"):
            assert "sample_population=" in line
