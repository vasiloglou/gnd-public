"""Write the induced-knowledge close's chained RF6 dynamic-candidate delta from the live source census.

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

OUT = ROOT / ".gnd-planning/milestones/induced-knowledge/evidence/close/dynamic-query-successor.json"
PREDECESSOR = ROOT / ".gnd-planning/milestones/induced-knowledge/evidence/IK6/dynamic-query-successor.json"


def main() -> None:
    chain = [path for path in DYNAMIC_SUCCESSORS if path != OUT]
    assert chain[-1] == PREDECESSOR, "IK6's delta must be the chain head before the close"
    expected = Counter({tuple(row[:3]): row[3] for row in successor_dynamic_rows()})
    found = dynamic_reads(sources())
    removed, added = expected - found, found - expected
    document = {
        "schema_version": 1,
        "predecessor": PREDECESSOR.relative_to(ROOT).as_posix(),
        "predecessor_sha256": hashlib.sha256(PREDECESSOR.read_bytes()).hexdigest(),
        "reason": (
            "Owner-approved induced-knowledge close (2026-10-27, close spec C-D1): IK6-R1 "
            "exempts src/gnd/examples/** from this scan by one shared rule "
            "(tests/support/scan_scope.py, tied to the layer map's exclusion), which removes "
            "every packaged example's rows; IK2-Q2's table-driven D-03 default in rai_import "
            "and IK1-Q2's text annotations add subscripts over their own tables and report "
            "rows, IK5-Q3's aggregate goal parser adds an operator-table read, and IK5-Q6 "
            "adds a type annotation for its reload count. Syntax "
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
