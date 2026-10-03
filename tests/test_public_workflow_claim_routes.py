from pathlib import Path


def test_render_doc_skill_names_the_constraint_blind_seed() -> None:
    skill = (Path(__file__).parents[1] / "src/gnd/skills/gnd-render-doc/SKILL.md").read_text()
    assert "gnd verbalize population MODEL POPULATION --format text" in skill
    assert "paraphrase it into a human document" in skill
    assert "If the command exits 3, report the refusal" in skill
    assert "Do not read `model.orm.yaml`" in skill
    assert "gnd extract MODEL --out DIR" in skill

def test_reviewer_export_handoffs_and_core_table_are_present():
    from pathlib import Path

    for name in ("gnd-extract", "gnd-render-doc", "gnd-solve"):
        assert (
            "](../gnd-export/SKILL.md)" in (Path("src/gnd/skills") / name / "SKILL.md").read_text()
        )
    text = Path("src/gnd/skills/gnd-orm-core/SKILL.md").read_text()
    before = text.split("| [`../gnd-export/SKILL.md`]")[0]
    assert before.endswith("|\n")
