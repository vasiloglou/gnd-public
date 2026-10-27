"""Chain the evolve-loading follow-up's RF5 body successor for _evolve_service_exit.

Run from the repository root after the final source edit:
    uv run python <this file>
The digests are computed exactly as tests/test_rf5_commands.py computes them
(AST dump after the RF7 reader seam), following IK2's rf5_row; the IK2 row is replaced by one carrying both reasons.
"""

import ast
import hashlib
import importlib
import inspect
import json
import sys
from pathlib import Path

ROOT = Path.cwd()
SUCCESSORS = ROOT / ".gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/source-successors.json"
NAME = "_evolve_service_exit"
REASON = (
    "Owner-approved induced-knowledge IK2 (2026-10-24): three D-12 refusal markers for "
    "induced provenance (spec R-I1..R-I4) map to exit 3 beside the existing D-12 markers; "
    "the evolve-loading follow-up (2026-10-27, spec D3-A, review H1) adds one marker so a "
    "YAML refusal of any model, current or staged, maps to exit 3 as a candidate's already "
    "did; every other branch unchanged."
)


def rf5_row() -> dict:
    sys.path.insert(0, str(ROOT / "tests"))
    import test_rf5_commands as rf5
    from support.rf8_sources import portable_dump

    value = getattr(importlib.import_module(rf5.HOMES[NAME]), NAME)
    source = inspect.getsource(value)
    node = ast.parse(source).body[0]

    def digest(tree) -> str:
        return hashlib.sha256(portable_dump(tree).encode()).hexdigest()

    predecessor = rf5.DEFINITIONS[NAME]
    predecessor_raw = ast.get_source_segment((rf5.EVIDENCE / "predecessor-cli.py.txt").read_text(), predecessor)
    return {
        "kind": "RF5",
        "old": "gnd.cli",
        "name": NAME,
        "home": rf5.HOMES[NAME],
        "before": {
            "raw_sha256": hashlib.sha256(predecessor_raw.encode()).hexdigest(),
            "algorithm_sha256": digest(predecessor),
        },
        "after": {
            "raw_sha256": hashlib.sha256(source.encode()).hexdigest(),
            "algorithm_sha256": digest(node),
        },
        "reason": REASON,
    }


def main() -> None:
    document = json.loads(SUCCESSORS.read_text())
    rows = document["successors"]
    row = rf5_row()
    rows[:] = [r for r in rows if not (r["kind"] == "RF5" and r["name"] == NAME)]
    rows.append(row)
    SUCCESSORS.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
