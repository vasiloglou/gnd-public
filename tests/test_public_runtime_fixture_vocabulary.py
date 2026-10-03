from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_production_does_not_special_case_fixture_vocabulary():
    forbidden = ["dispatch_request", "release_request", "SHIP-0", "REL-0", "WH-A", "DEP-D"]
    for path in (ROOT / "src/gnd").rglob("*.py"):
        text = path.read_text()
        assert not any(value in text for value in forbidden), path
