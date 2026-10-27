"""Add the induced-knowledge close's RF5 body successor for _cmd_diff.

Run from the repository root after the final source edit:
    uv run python <this file>
The digests are computed exactly as tests/test_rf5_commands.py computes them
(AST dump after the RF7 reader seam), following IK2's rf5_row.
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
NAME = "_cmd_diff"
REASON = (
    "Owner-approved induced-knowledge close (2026-10-27, close spec C-D1, IK1-Q2): the text "
    "format of gnd diff ends with one ANNOTATION block per description change, each side "
    "printed as ASCII-escaped canonical JSON; a diff without annotations prints the same "
    "text, and every other branch is unchanged."
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
