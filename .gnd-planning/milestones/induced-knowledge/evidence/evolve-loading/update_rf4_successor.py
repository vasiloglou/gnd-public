"""Chain the evolve-loading follow-up's RF4 body successor for _witness_inputs.

Run from the repository root after the final source edit:
    uv run python <this file>
The algorithm digest and import bindings are computed exactly as
tests/test_rf4_peripheral.py computes them; the row chains from the frozen
RF9 body successor, whose "after" is this row's "before".
"""

import ast
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path.cwd()
SUCCESSORS = ROOT / ".gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/source-successors.json"
FROZEN = ROOT / ".gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair/body-successors.json"
OLD, NAME, HOME = "gnd.api", "_witness_inputs", "gnd.witness.service"
REASON = (
    "RF7 C1/C2/C4/C5 and branch-local R2 successor; the owner-approved evolve-loading "
    "follow-up (2026-10-27, spec D6-A) binds declared references through "
    "gnd.model.bind_declared_references, which returns None for a model that declares "
    "none and passes the binder's errors through unwrapped; every outcome is pinned "
    "unchanged by tests/test_evolve_loading.py H3."
)


def main() -> None:
    sys.path.insert(0, str(ROOT / "tests"))
    import test_rf4_peripheral as rf4

    (frozen,) = [r for r in json.loads(FROZEN.read_text())
                 if (r["kind"], r.get("old"), r["name"]) == ("RF4", OLD, NAME)]
    source = rf4._source(HOME).read_text()
    node = rf4._definition(source, NAME)
    raw = ast.get_source_segment(source, node)
    after = {
        "raw_sha256": hashlib.sha256(raw.encode()).hexdigest(),
        "algorithm_sha256": hashlib.sha256(rf4._algorithm(node).encode()).hexdigest(),
        "imports": rf4._import_bindings(node),
    }
    document = json.loads(SUCCESSORS.read_text())
    rows = [r for r in document["successors"]
            if not (r["kind"] == "RF4" and r.get("old") == OLD and r["name"] == NAME)]
    rows.append({"kind": "RF4", "old": OLD, "name": NAME, "home": HOME, "base": frozen["base"],
                 "before": frozen["after"], "after": after, "reason": REASON})
    document["successors"] = rows
    SUCCESSORS.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{NAME}: {frozen['after']['algorithm_sha256']} -> {after['algorithm_sha256']}")


if __name__ == "__main__":
    main()
