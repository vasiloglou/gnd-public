"""ilp-import-hardening close: regressions for the close review's findings.

Record: .gnd-planning/milestones/ilp-import-hardening/005-milestone-close.md.
Each test was red before its repair (evidence/close/red.txt).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOL = REPO_ROOT / "tools" / "ilp_comparison.py"
LLM = "IL5/live/invocation-1"


def _root(tmp_path: Path) -> tuple[Path, str]:
    import importlib.util

    spec = importlib.util.spec_from_file_location("ilp_comparison", TOOL)
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)  # type: ignore[union-attr]
    for relative in (tool.EVIDENCE, tool.STAFFING, tool.GOLDEN, tool.BRIDGE):
        source, target = REPO_ROOT / relative, tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        (shutil.copytree if source.is_dir() else shutil.copy)(source, target)
    return tmp_path, str(tool.EVIDENCE)


@pytest.mark.parametrize("answer", ['{"schema_version": "gnd-ilp-clauses/1"}', "[1, 2]"],
                         ids=["no-clauses", "not-an-object"])
def test_r2_1_an_llm_answer_without_clauses_fails_the_tool_by_name(tmp_path, answer):
    """Close reader 2, finding 1: valid JSON that is not a clauses document exits 2,
    naming its directory, not 1 with a traceback (1 means the table is stale)."""
    root, evidence = _root(tmp_path)
    live = root / evidence / LLM
    (live / "answer.json").write_text(answer, encoding="utf-8")
    (live / "import-stderr.txt").write_text("clauses fails gnd-ilp-clauses/1 at (root): x\n", encoding="utf-8")
    outcome = json.loads((live / "outcome.json").read_text(encoding="utf-8"))
    (live / "outcome.json").write_text(json.dumps({**outcome, "import_exit": 3}), encoding="utf-8")
    completed = subprocess.run([sys.executable, str(TOOL), "--root", str(root)], capture_output=True,
                               text=True, timeout=300, check=False, cwd=REPO_ROOT)
    assert completed.returncode == 2, completed.stderr
    assert f"{LLM}: " in completed.stderr and "Traceback" not in completed.stderr
