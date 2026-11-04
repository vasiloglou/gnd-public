"""MG5 parity capture (spec T4): `gnd validate MODEL --format json` over every
*.orm.yaml and *.orm.json under tests/fixtures, examples and src/gnd/skills.

Run from the repository root:
    uv run python .gnd-planning/milestones/model-growth-guardrails/evidence/MG5/capture_parity.py OUT.json
Writes, per model, the exit and the SHA-256 of stdout. Paths are passed
repository-relative, so no scratch path enters a digest.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "tests"))

from support.cli_runner import run_main


def main(out: str) -> None:
    patterns = ("tests/fixtures/**/*.orm.yaml", "tests/fixtures/**/*.orm.json", "examples/**/*.orm.yaml",
                "examples/**/*.orm.json", "src/gnd/skills/**/*.orm.yaml", "src/gnd/skills/**/*.orm.json")
    models = sorted({path for pattern in patterns for path in ROOT.glob(pattern)})
    rows = {}
    for model in models:
        rel = model.relative_to(ROOT).as_posix()
        result = run_main(["validate", rel, "--format", "json"], cwd=ROOT)
        rows[rel] = {"exit": result.returncode, "stdout_sha256": hashlib.sha256(result.stdout).hexdigest()}
    Path(out).write_text(json.dumps({"models": rows}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    exits = {}
    for row in rows.values():
        exits[row["exit"]] = exits.get(row["exit"], 0) + 1
    print(len(rows), "models; exits", exits)


if __name__ == "__main__":
    main(sys.argv[1])
