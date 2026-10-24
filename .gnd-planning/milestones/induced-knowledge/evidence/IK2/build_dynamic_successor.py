"""Write IK2's chained RF6 dynamic-candidate delta from the live source census.

Run from the repository root AFTER the final source edit, before the
successor file is appended to tests/support/pyrel_application_successors.py
DYNAMIC_SUCCESSORS (rerunning with it appended recomputes against itself):
    uv run python <this file>
"""

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))

from support.pyrel_application_successors import DYNAMIC_SUCCESSORS
from test_rf6_query_policy import dynamic_reads, sources, successor_dynamic_rows

OUT = ROOT / ".gnd-planning/milestones/induced-knowledge/evidence/IK2/dynamic-query-successor.json"
PREDECESSOR = ROOT / ".gnd-planning/milestones/induced-knowledge/evidence/IK1/dynamic-query-successor.json"


def main() -> None:
    chain = [path for path in DYNAMIC_SUCCESSORS if path != OUT]
    assert chain[-1] == PREDECESSOR, "IK1's delta must be the chain head before IK2"
    expected = Counter({tuple(row[:3]): row[3] for row in successor_dynamic_rows()})
    found = dynamic_reads(sources())
    removed, added = expected - found, found - expected
    document = {
        "schema_version": 1,
        "predecessor": PREDECESSOR.relative_to(ROOT).as_posix(),
        "predecessor_sha256": hashlib.sha256(PREDECESSOR.read_bytes()).hexdigest(),
        "reason": (
            "Owner-approved induced-knowledge IK2 (2026-10-24): induced provenance admission "
            "(the D-12 status-change index), the coverage induced view and its shared "
            "constraint-address walk add type-annotation and induction-key subscripts. Syntax "
            "census only; no model-query exception widening."
        ),
        "removed": [list(key) + [count] for key, count in sorted(removed.items())],
        "added": [list(key) + [count] for key, count in sorted(added.items())],
        "result_distinct_rows": len(found),
        "result_occurrences": sum(found.values()),
    }
    OUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"removed {len(removed)} added {len(added)} -> {len(found)} rows")


if __name__ == "__main__":
    main()
