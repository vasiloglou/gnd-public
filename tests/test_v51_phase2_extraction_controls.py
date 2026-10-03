from __future__ import annotations

from pathlib import Path

import pytest
from support.cli_runner import run_main
from support.repository import REPO_ROOT


def _run(arguments: list[str], *, cwd: Path=REPO_ROOT) -> tuple[int, str]:
    result = run_main(arguments, cwd=cwd, capture_stderr=False)
    return (result.returncode, result.stdout.decode('utf-8', errors='surrogatepass'))

def test_control_guard_rejects_a_broken_command(tmp_path: Path) -> None:
    code, _stdout = _run(['extract', str(tmp_path / 'missing.orm.yaml'), '--out', str(tmp_path / 'out')])
    assert code != 0
    with pytest.raises(AssertionError):
        assert code == 0
