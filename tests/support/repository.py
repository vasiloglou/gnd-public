"""Explicit synthetic Git-root reader for test-controlled fixture repositories."""
from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

def git_blob(commit: str, relative_path: str, *, root: Path) -> bytes:
    completed = subprocess.run(['git', 'show', f'{commit}:{relative_path}'], cwd=root, check=True, capture_output=True)
    return completed.stdout
