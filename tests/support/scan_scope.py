"""The one rule for which sources the RF6 query and RF7 parser scans read (IK6-R1).

Packaged examples are standalone teaching code, not GND modules: the RF6 and
RF7 inventories govern how GND's own modules read models and JSON, and an
example that calls a public loader (``plan_apps/core.py`` calls ``load_model``)
is a consumer of that API, not part of it. ``tools/gnd_layers.json`` already
excludes them from layering, so the scans exclude them by the same entry
instead of listing each script.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = "src/gnd/examples/**"


def exempt(path: str) -> bool:
    """True for a repository-relative path that the scans do not read."""
    return path.startswith(EXAMPLES.removesuffix("**"))


def module_sources() -> dict[str, str]:
    """Every ``src/gnd`` Python source the scans read, keyed by repository path."""
    excluded = json.loads((ROOT / "tools/gnd_layers.json").read_text())["excluded"]
    assert EXAMPLES in excluded, "the scans follow the layer map's examples exclusion"
    found = {}
    for path in sorted((ROOT / "src/gnd").rglob("*.py")):
        relative = path.relative_to(ROOT).as_posix()
        if not exempt(relative):
            found[relative] = path.read_text()
    return found
