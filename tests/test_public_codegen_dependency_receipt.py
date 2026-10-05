"""Generated development dependencies match their explicit template receipt."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ANSWERS = REPO_ROOT / "tests/fixtures/v51-generated-project/answers"


def _gnd(*argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, '-m', 'gnd', *argv], cwd=REPO_ROOT, check=False, capture_output=True, text=True)

def _model_arg(case: str) -> str:
    """The corpus model path AS THE RECEIPT WAS MEASURED: relative to the repo.

    The emitted banner in `model/__init__.py` and `model/tools.py` records the
    model path exactly as it was passed, so an absolute path here would produce
    different bytes for the same model -- the same class of path dependence
    IF-P1-3 recorded for `.gnd-codegen.json` (IF-P1-4).
    """
    return f'tests/fixtures/v51-generated-project/{case}/model.orm.yaml'

def test_the_emitted_pyproject_declares_the_test_time_dependency(tmp_path: Path) -> None:
    """The emitted module IS a pytest module importing gnd.archsmoke, so both
    names are declared; runtime `dependencies` stays empty on purpose."""
    import tomllib
    root = tmp_path / 'alpha'
    assert _gnd('codegen', _model_arg('alpha'), '--out', str(root)).returncode == 0
    config = tomllib.loads((root / 'pyproject.toml').read_text(encoding='utf-8'))
    assert config['project']['dependencies'] == []
    assert config['dependency-groups']['dev'] == ['get-nick-done', 'pytest']
    assert (root / 'pyproject.toml').read_bytes() == (ANSWERS / 'goldens' / 'pyproject.toml').read_bytes()
