from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_skill_routes_name_the_command_without_copying_the_format() -> None:
    recovery = (ROOT / "src/gnd/skills/gnd-model-from-code/SKILL.md").read_text()
    core = (ROOT / "src/gnd/skills/gnd-orm-core/SKILL.md").read_text()
    assert "gnd import rai-orm MODEL --out OUT_DIR" in recovery
    assert "gnd import rai-orm MODEL --out OUT_DIR" in core
    assert "provenance-and-modality.md" in recovery
    assert "schema_version" not in recovery + core
