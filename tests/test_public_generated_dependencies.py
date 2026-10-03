"""Generated-project dependency boundary."""
from pathlib import Path


def test_generated_projects_declare_no_dependency_at_all() -> None:
    """T53. `gnd codegen` emits `dependencies = []`, so a generated project
    cannot acquire Nagini, Viper or a JVM through GND."""
    repo = Path(__file__).resolve().parents[1]
    emit = (repo / "src/gnd/codegen/emit.py").read_text(encoding="utf-8")
    assert '"dependencies = []",' in emit
    assert "nagini" not in emit.lower()
