"""Bind the close verification suite and its deselections to a clean candidate."""

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

TESTS = """
test_synth_guarded_cases test_synth_conforming test_synth_expectation_independence
test_synth_mutate test_measure_coverage test_synth_false_pass_quarantine
test_discover_guarded_join test_discover test_ilp_amie_constants test_ilp_amie
test_ih1_counting test_ih2_ownref test_ilp_learners test_public_guarded_consequent_matrix
test_guarded_diagnostics test_rule_edition_comparison test_rf1_cli_pins test_rf1_layering
test_rf5_commands test_rf6_query_policy test_query_budget_headroom test_development_scaffold
""".split()


def main():
    repo, receipt = (Path(value).resolve() for value in sys.argv[1:3])
    expected = sys.argv[3]

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()

    assert git("rev-parse", "HEAD") == expected
    assert not git("status", "--porcelain", "--untracked-files=all")
    environment = dict(os.environ, PYTHONPATH=str(repo / "src"), UV_OFFLINE="1", PYTHONDONTWRITEBYTECODE="1")
    arguments = ["-q", *(f"tests/{name}.py" for name in TESTS), "-p", "no:cacheprovider", "--tb=short"]
    run = subprocess.run([sys.executable, "-m", "pytest", *arguments], cwd=repo, env=environment,
                         capture_output=True, check=False)
    sys.stdout.buffer.write(run.stdout)
    sys.stderr.buffer.write(run.stderr)
    assert run.returncode == 0
    summaries = re.findall(r"^.*\bpassed\b.*$", run.stdout.decode(), re.MULTILINE)
    assert summaries
    deselections = subprocess.check_output(
        [sys.executable, "-c", """
import contextlib
import io
import json
import sys
import pytest
class Observe:
    def pytest_deselected(self, items):
        self.rows = [{"node_id": item.nodeid, "markers": sorted({m.name for m in item.iter_markers()})}
                     for item in items]
observer = Observe()
observer.rows = []
with contextlib.redirect_stdout(io.StringIO()):
    result = pytest.main(["--collect-only", *sys.argv[1:]], plugins=[observer])
assert result == 0
print(json.dumps(observer.rows))
""", *arguments],
        cwd=repo, env=environment, text=True,
    )
    assert not git("status", "--porcelain", "--untracked-files=all")
    receipt.write_text(json.dumps({
        "source_commit": expected,
        "clean_tree_before_and_after": True,
        "python": sys.version.split()[0],
        "lock_sha256": hashlib.sha256((repo / "uv.lock").read_bytes()).hexdigest(),
        "argv": ["python", "-m", "pytest", *arguments],
        "environment": {"PYTHONPATH": "source/src", "UV_OFFLINE": "1", "PYTHONDONTWRITEBYTECODE": "1"},
        "exit": run.returncode,
        "summary": summaries[-1],
        "stdout_sha256": hashlib.sha256(run.stdout).hexdigest(),
        "stderr_sha256": hashlib.sha256(run.stderr).hexdigest(),
        "deselected": json.loads(deselections),
    }, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
