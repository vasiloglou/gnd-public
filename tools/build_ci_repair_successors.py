"""Write the 2026-11-16 main CI repair's chained successor rows from the current sources.

    uv run python tools/build_ci_repair_successors.py

Each row's ``before`` is the digest the existing ledgers currently expect, read
through the same helpers the pinning tests use, and ``after`` is the digest of
the merged source. Nothing is typed by hand. The reasons name the phases that
changed each body. Two files are written under
``.gnd-planning/maintenance/2026-11-16-main-ci-repair/``:

- ``source-successors.json``, chained after the compiled-snapshot-obligations CI
  registry like every phase successor file (RF4 and RF6b rows);
- ``definition-successors.json``, chained after MC3, for the two definitions
  whose pins run through the model-composition chain.
"""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".gnd-planning/maintenance/2026-11-16-main-ci-repair"
CI = ".gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/source-successors.json"
MC3 = ".gnd-planning/milestones/model-composition/evidence/MC3/definition-successors.json"

GC1 = "GC1 (62c45016, 270303c0) literal set membership"
GC2 = "GC2 (b4e84af4, 6ebd39a7) guarded antecedent filters"
GC3 = "GC3 (20172ace, b89a1f00) disjunctive guarded consequents"
GW0 = "GW0 (24c72d86) guarded antecedent and literal domain reports"
LX = "LX3 review (9e1c1d29) catalog validation and mixed witness intake"
LD2 = "LD2 (07a2bb06) time dimensions and exact decimal replay"

DEFINITION_REASONS = {
    "_rule_anchored_role_and_recogniser": LD2,
    "_iter_guarded_atoms": f"{GC2}; {GC3}",
    "_iter_guarded_consequent_terms": f"{GC1}; {GC2}; {GC3}",
    "_rule_guarded_consequent_ground": f"{GC2}; {GC3}",
    "_rule_guarded_exists_range": GC3,
    "_rule_guarded_exists_where_bound": GC3,
    "_rule_guarded_comparison_type": f"{GC1}; {GC3}",
    "_rule_guarded_exists_where_type": f"{GC1}; {GC3}",
    "_derivation_variable_primitives": GC1,
    "_derivation_head_term_issues": GC1,
    "_rule_term_non_finite_number": GC3,
    "_rule_temporal_language": f"{GC1}; {GC2}; {GC3}",
    "_load_model_no_follow": LX,
    "_bind_at": LX,
    "ConstraintVerdict": f"{GW0}; {GC3}",
    "check_legacy": f"{GW0}; {GC2}; {GC3}",
    "_correspondence_message": GC3,
    "_family_message_guarded": f"{GC2}; {GC3}",
}

RF4_REASONS = {
    "_phase3_target": ("This repair excludes GC2 filtered and GC3 any_of guarded rows from the frozen "
                       "Phase 3 denominator, as Phase 6 excluded guarded exists."),
}
RF4_REASON = ("Literature interop LX1-LX4 and the LX3 review route witness, replay and "
              "check through include roots and fixed reference catalogs.")


def _dump(path: Path, document: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def _sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main() -> int:
    sys.path.insert(0, str(ROOT / "tests"))
    import test_rf4_peripheral as rf4
    import test_rf6_packages as rf6
    from support.rf9_ci_sources import body_successor, definition_successor

    if any((OUT / name).exists() for name in ("source-successors.json", "definition-successors.json")):
        if "--rewrite" not in sys.argv[1:]:
            print("already recorded; pass --rewrite to rebuild this unmerged record", file=sys.stderr)
            return 1
        # Start from empty chained files so the ledgers read the predecessors' state.
        for name, predecessor in (("source-successors.json", CI), ("definition-successors.json", MC3)):
            _dump(OUT / name, {"schema_version": 1, "reason": "rebuilding", "predecessor": predecessor,
                               "predecessor_sha256": _sha(predecessor), "successors": []})

    rows, mc_rows = [], []
    for row in rf6.inventory():
        mc = rf6.mc1_definition(row["module"], row["name"])
        home = mc["home"] if mc else rf6.homes().get((row["module"], row["name"]), row["module"])
        path = rf4._source(home)
        source = path.read_text()
        nodes = [n for n in ast.parse(source).body
                 if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == row["name"]]
        if len(nodes) != 1:
            continue
        node = nodes[0]
        start = min([node.lineno] + [d.lineno for d in node.decorator_list])
        body = "".join(source.splitlines(keepends=True)[start - 1:node.end_lineno])
        actual = hashlib.sha256(body.encode()).hexdigest()
        successor = definition_successor(row["module"], row["name"])
        expected = successor["after"] if successor else row["sha256"]
        if mc:
            expected = mc["after"]
        if actual == expected:
            continue
        entry = {"kind": "RF6b", "module": row["module"], "name": row["name"], "home": home,
                 "before": expected, "after": actual,
                 "reason": f"Body changed by {DEFINITION_REASONS[row['name']]}."}
        if mc:
            entry["home"] = mc["home"]
            mc_rows.append(entry)
        else:
            entry["home"] = successor["home"] if successor else home
            rows.append(entry)

    for move in rf4.MOVES["names"]:
        if move["name"].isupper():
            continue
        successor = body_successor("RF4", move["name"], move["old"])
        after = rf4._definition(rf4._source(move["new"]).read_text(), move["name"])
        if after is None:
            continue
        algorithm = hashlib.sha256(rf4._algorithm(after).encode()).hexdigest()
        imports = rf4._import_bindings(after)
        if successor:
            before = successor["after"]
        else:
            path = "src/" + move["old"].replace(".", "/") + ".py"
            import subprocess
            original = subprocess.check_output(["git", "show", f"{rf4.BASE}:{path}"], cwd=ROOT, text=True)
            node = rf4._definition(original, move["name"])
            if node is None:
                continue  # the test covers constants and aliases by identity
            before = {"algorithm_sha256": hashlib.sha256(rf4._algorithm(node).encode()).hexdigest(),
                      "imports": rf4._import_bindings(node)}
        if before["algorithm_sha256"] == algorithm and before["imports"] == imports:
            continue
        current = rf4._source(move["new"]).read_text()
        raw = ast.get_source_segment(current, after)
        rows.append({"kind": "RF4", "old": move["old"], "name": move["name"], "home": move["new"],
                     "before": before,
                     "after": {"algorithm_sha256": algorithm, "imports": imports,
                               "raw_sha256": hashlib.sha256(raw.encode()).hexdigest()},
                     "reason": RF4_REASONS.get(move["name"], RF4_REASON)})

    _dump(OUT / "source-successors.json", {
        "schema_version": 1,
        "reason": ("Main CI repair 2026-11-16: bodies changed by the guarded-rule and literature "
                   "milestones without a recorded successor; each row names its phases."),
        "predecessor": CI, "predecessor_sha256": _sha(CI), "successors": rows,
    })
    _dump(OUT / "definition-successors.json", {
        "schema_version": 1,
        "reason": ("Main CI repair 2026-11-16: two model-composition definitions changed again "
                   "after MC3; each row names its phases."),
        "predecessor": MC3, "predecessor_sha256": _sha(MC3), "successors": mc_rows,
    })
    print(f"{len(rows)} source successors, {len(mc_rows)} definition successors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
