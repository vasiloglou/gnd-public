"""Distribution and evidence boundaries for v6.0 Phase 3."""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_runtime_package_has_no_proof_toolchain_import() -> None:
    forbidden = {'nagini', 'viper', 'isabelle', 'proof'}
    evidence_root = ROOT / 'src' / 'gnd' / '_assurance_evidence'
    findings: list[str] = []

    def is_runtime_source(path: Path) -> bool:
        return not path.is_relative_to(evidence_root)
    runtime_sources = [path for path in (ROOT / 'src/gnd').rglob('*.py') if is_runtime_source(path)]
    assert is_runtime_source(ROOT / 'src' / 'gnd' / 'cli.py')
    assert not is_runtime_source(evidence_root / 'planted.py')
    for path in runtime_sources:
        tree = ast.parse(path.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = {alias.name.split('.', 1)[0].lower() for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                roots = {node.module.split('.', 1)[0].lower()}
            else:
                continue
            if roots & forbidden:
                findings.append(path.relative_to(ROOT).as_posix())
    assert findings == []

def test_default_project_dependencies_exclude_proof_runtimes() -> None:
    text = (ROOT / 'pyproject.toml').read_text(encoding='utf-8').lower()
    project = text.split('[project.optional-dependencies]', 1)[0]
    assert all(token not in project for token in ('nagini', 'viper', 'isabelle'))
