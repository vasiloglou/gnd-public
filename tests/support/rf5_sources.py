"""Complete defining-source scope for the RF5 CLI relocation."""
import importlib
import json
import sys
from pathlib import Path

from support.repository import REPO_ROOT

HOMES = json.loads((REPO_ROOT / '.gnd-planning/milestones/code-refactoring/evidence/RF5/planned-homes.json').read_text())

def owner(name):
    return sys.modules.get(HOMES[name]) or importlib.import_module(HOMES[name])

def cli_source_paths():
    modules = set(HOMES.values())
    modules.update("gnd.commands." + name for name in (
        "checking", "verify", "synth", "measure", "extract", "export", "codegen",
        "conformance", "recovery", "evolve", "doccheck", "fidelity", "review", "exp",
        "solve", "lifecycle", "judgments", "witness",
    ))
    modules.update('gnd.commands.' + p.stem for p in (REPO_ROOT / 'src/gnd/commands').glob('*.py'))
    paths = [REPO_ROOT / 'src/gnd/cli.py'] + [REPO_ROOT / 'src' / Path(*module.split('.')).with_suffix('.py') for module in sorted(modules)]
    assert all(path.is_file() for path in paths)
    return paths

def cli_sources(paths=None):
    expected = set(cli_source_paths())
    selected = expected if paths is None else set(paths)
    if selected != expected:
        raise AssertionError('incomplete CLI defining-source scope')
    return '\n'.join(path.read_text(encoding='utf-8') for path in sorted(selected))
