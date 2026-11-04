"""MG4 parity capture (spec T5): `gnd extract MODEL --out DIR` WITHOUT
--guidelines over every *.orm.yaml under tests/fixtures and examples.

Run from the repository root:
    uv run python .gnd-planning/milestones/model-growth-guardrails/evidence/MG4/capture_parity.py OUT.json
Writes, per model, the exit and the SHA-256 of every bundle file. The index
records the model path as given (repository-relative), so no scratch path
enters a digest.
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "tests"))

from support.cli_runner import run_main


def main(out: str) -> None:
    models = sorted({*ROOT.glob("tests/fixtures/**/*.orm.yaml"), *ROOT.glob("examples/**/*.orm.yaml")})
    rows = {}
    with tempfile.TemporaryDirectory() as scratch:
        for index, model in enumerate(models):
            rel = model.relative_to(ROOT).as_posix()
            bundle = Path(scratch) / str(index)
            result = run_main(["extract", rel, "--out", str(bundle)], cwd=ROOT)
            files = {}
            if bundle.is_dir():
                files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(bundle.iterdir())}
            rows[rel] = {"exit": result.returncode, "files": files}
    Path(out).write_text(json.dumps({"models": rows}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    exits = {}
    for row in rows.values():
        exits[row["exit"]] = exits.get(row["exit"], 0) + 1
    print(len(rows), "models; exits", exits)


if __name__ == "__main__":
    main(sys.argv[1])
