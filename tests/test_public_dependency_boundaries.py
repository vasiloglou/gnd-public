import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_formal_verifiers_are_not_public_dependencies() -> None:
    pyproject = tomllib.loads((ROOT / 'pyproject.toml').read_text())
    runtime = pyproject['project']['dependencies']
    extras = pyproject['project'].get('optional-dependencies', {})
    assert all('nagini' not in item.lower() and 'isabelle' not in item.lower() for item in runtime)
    assert all('nagini' not in item.lower() and 'isabelle' not in item.lower() for items in extras.values() for item in items)
