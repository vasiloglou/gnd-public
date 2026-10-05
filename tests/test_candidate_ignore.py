"""Release output ignore rules must not hide committed candidate fixtures."""
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_only_root_candidate_output_is_ignored(tmp_path):
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    shutil.copy2(ROOT / '.gitignore', tmp_path / '.gitignore')
    for relative, expected in [('candidate/release/example.whl', 0),
                               ('tests/fixtures/session/candidate/steps.json', 1)]:
        result = subprocess.run(['git', 'check-ignore', '--no-index', relative],
                                cwd=tmp_path, capture_output=True, check=False)
        assert result.returncode == expected, result.stdout
