"""The expense receipts example rebuilds byte-identically and gives the results its page reports.

docs/expense/05-receipts.md states which card lines each rule flags under the
reviewer's decisions and under a join by printed name, and quotes the refusal
when a decision is missing. These tests run the real commands and pin those
statements.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "src/gnd/examples/expense/receipts"
BUILD = ROOT / "tools/build_expense_receipts_example.py"
PAGE = ROOT / "docs/expense/05-receipts.md"


def _files(root: Path) -> list[str]:
    return sorted(str(path.relative_to(root)) for path in root.rglob("*")
                  if path.is_file() and "__pycache__" not in path.parts)


def _gnd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "gnd", *args], cwd=EXAMPLE, capture_output=True, text=True)


def _offenders(directory: str, tmp_path: Path) -> dict[str, list]:
    population, record = tmp_path / f"{directory}.population.json", tmp_path / f"{directory}.composition.json"
    composed = _gnd("compose", "checking.orm.json", directory, "--out", str(population), "--record", str(record))
    assert composed.returncode == 0, composed.stderr
    checked = _gnd("check", "checking.orm.json", str(population), "--composition", str(record),
                   "--sources", directory, "--format", "json")
    assert checked.returncode == 1, checked.stderr
    verdicts = json.loads(checked.stdout)["report"]["verdicts"]
    return {v["constraint_ref"]: v["offending_facts"] for v in verdicts if v["verdict"] == "fail"}


def test_rebuilds_byte_identically(tmp_path: Path) -> None:
    subprocess.run([sys.executable, str(BUILD), str(tmp_path)], check=True)
    assert _files(tmp_path) == _files(EXAMPLE)
    for name in _files(EXAMPLE):
        assert (tmp_path / name).read_bytes() == (EXAMPLE / name).read_bytes(), name


def test_reviewed_decisions_flag_the_right_lines(tmp_path: Path) -> None:
    assert _offenders("claim", tmp_path) == {
        "constraints[0]": [["Café Central, Vienna"], ["TAXI G7 (unresolved)"]],
        "constraints[1]": [["Café Central, Vienna"], ["Spa Lumière"], ["TAXI G7 (unresolved)"]],
        "constraints[3]": [{"$e": "C4", "$t": "T-114", "$d": "2026-03-09", "$b": "2026-03-06"}],
    }


def test_printed_names_get_it_wrong_both_ways(tmp_path: Path) -> None:
    assert _offenders("claim-flat", tmp_path) == {
        "constraints[0]": [["HTL LUMIERE PARIS"], ["SPA LUMIERE"], ["TAXI G7"]],
        "constraints[1]": [["HTL LUMIERE PARIS"], ["SPA LUMIERE"]],
        "constraints[3]": [{"$e": "C4", "$t": "T-114", "$d": "2026-03-09", "$b": "2026-03-06"}],
    }


def test_a_missing_decision_is_refused_as_the_page_quotes(tmp_path: Path) -> None:
    result = _gnd("compose", "checking.orm.json", "claim-missing", "--out", str(tmp_path / "p.json"),
                  "--record", str(tmp_path / "r.json"))
    assert result.returncode == 3
    message = " ".join(result.stderr.split())
    page = " ".join(PAGE.read_text().split())
    assert "joined without a same decision" in message
    assert message in page
