from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / 'src' / 'gnd'
TRANSITION_LANE_ROOTS = (SRC / 'transition.py', SRC / 'patterns.py', SRC / 'exp' / 'junit.py', SRC / 'exp' / 'tests_runner.py', SRC / 'solve.py', SRC / 'coverage.py', SRC / 'address.py')
_NETWORK_LIBS = frozenset({'httpx', 'requests', 'aiohttp', 'urllib', 'socket', 'http', 'ftplib', 'telnetlib'})
_PROVIDER_CLIENTS = frozenset({'anthropic', 'openai', 'google', 'cohere', 'mistralai', 'ollama'})

def _imports_forbidden_library(name: str, library: str) -> bool:
    if name.split('.')[0] != library:
        return False
    return not (library == 'urllib' and (name == 'urllib.parse' or name.startswith('urllib.parse.')))

def _closure(roots: tuple[Path, ...]) -> set[Path]:
    seen: set[Path] = set()
    queue = list(roots)
    while queue:
        path = queue.pop()
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        tree = ast.parse(path.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module)
            elif isinstance(node, ast.Import):
                modules += [alias.name for alias in node.names]
            for module in modules:
                if not module.startswith('gnd'):
                    continue
                relative = module.split('.')[1:]
                if not relative:
                    continue
                candidate = SRC.joinpath(*relative).with_suffix('.py')
                package = SRC.joinpath(*relative, '__init__.py')
                queue += [p for p in (candidate, package) if p.is_file()]
    return seen

def test_every_root_of_this_scan_exists() -> None:
    for root in TRANSITION_LANE_ROOTS:
        assert root.is_file(), f'scan root {root} does not exist; a missing root is silent, so the lane would drop out of the closure without any test going red'

def test_the_closure_leaves_its_roots() -> None:
    closure = _closure(TRANSITION_LANE_ROOTS)
    for expected in ('checker/__init__.py', 'checker/_core.py', 'checker/_reports.py', 'model/__init__.py', 'model/_validation.py', 'model/_operations.py',  'population.py'):
        assert SRC / expected in closure, f'the closure never reached {expected}'

@pytest.mark.parametrize('library', sorted(_NETWORK_LIBS | _PROVIDER_CLIENTS))
def test_no_network_library_is_reachable_from_the_transition_lane(library: str) -> None:
    for path in sorted(_closure(TRANSITION_LANE_ROOTS)):
        tree = ast.parse(path.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.ImportFrom) and node.module:
                names.append(node.module)
            elif isinstance(node, ast.Import):
                names += [alias.name for alias in node.names]
            for name in names:
                assert not _imports_forbidden_library(name, library), f'{path.relative_to(REPO_ROOT)} imports {name}: a transition verdict must be computable from committed documents alone'

def test_offline_import_classifier_allows_parsing_but_refuses_transport() -> None:
    assert not _imports_forbidden_library('urllib.parse', 'urllib')
    assert _imports_forbidden_library('urllib.request', 'urllib')
    assert _imports_forbidden_library('requests', 'requests')
