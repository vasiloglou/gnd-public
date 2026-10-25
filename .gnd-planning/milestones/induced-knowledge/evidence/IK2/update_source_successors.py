"""Point IK2's RF6b definition successors at the current bodies.

Run from the repository root after the final source edit:
    uv run python <this file>
The body digest is computed exactly as tests/test_rf6_packages.py does.
"""

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path.cwd()
SUCCESSORS = ROOT / ".gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/source-successors.json"
HOME = ROOT / "src/gnd/model/_validation.py"
ROWS = {
    "_layer1_structural": (
        None,  # IK1's row keeps its original `before`
        (
            "Owner-approved induced-knowledge IK1-D6 (2026-10-24): the layer-1 screen refuses "
            "description values with no faithful JSON form (NaN, infinity, lone surrogates, "
            "anchored YAML booleans); IK2 (2026-10-24) applies the same screen to constraint "
            "provenance.induction blocks through one tuple of screened paths; every other path "
            "unchanged."
        ),
    ),
    "_rule_modality_policy": (
        "bd83f28b3fb7bfe2e679853f9c4a789097f987031e199709b540356557bd5a46",
        (
            "Owner-approved induced-knowledge IK2 (2026-10-24): the D-03 modality-policy warning "
            "also covers an unconfirmed induced constraint claiming alethic, with its own "
            "message; the llm-inferred/common-sense message is byte-identical."
        ),
    ),
}


def body_sha(name: str) -> str:
    source = HOME.read_text()
    (node,) = [
        n for n in ast.parse(source).body
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name
    ]
    start = min([node.lineno] + [d.lineno for d in node.decorator_list])
    body = "".join(source.splitlines(keepends=True)[start - 1 : node.end_lineno])
    return hashlib.sha256(body.encode()).hexdigest()


def rf5_row() -> dict:
    """The RF5 body successor for _evolve_service_exit, digested as
    tests/test_rf5_commands.py digests it (AST dump after the RF7 reader seam)."""
    import importlib
    import inspect
    import sys

    sys.path.insert(0, str(ROOT / "tests"))
    import test_rf5_commands as rf5
    from support.rf8_sources import portable_dump

    name = "_evolve_service_exit"
    value = getattr(importlib.import_module(rf5.HOMES[name]), name)
    source = inspect.getsource(value)
    node = ast.parse(source).body[0]

    def digest(tree) -> str:
        return hashlib.sha256(portable_dump(tree).encode()).hexdigest()

    predecessor = rf5.DEFINITIONS[name]
    predecessor_raw = ast.get_source_segment(
        (rf5.EVIDENCE / "predecessor-cli.py.txt").read_text(), predecessor
    )
    return {
        "kind": "RF5",
        "old": "gnd.cli",
        "name": name,
        "home": rf5.HOMES[name],
        "before": {
            "raw_sha256": hashlib.sha256(predecessor_raw.encode()).hexdigest(),
            "algorithm_sha256": digest(predecessor),
        },
        "after": {
            "raw_sha256": hashlib.sha256(source.encode()).hexdigest(),
            "algorithm_sha256": digest(node),
        },
        "reason": (
            "Owner-approved induced-knowledge IK2 (2026-10-24): three D-12 refusal markers "
            "for induced provenance (spec R-I1..R-I4) map to exit 3 beside the existing "
            "D-12 markers; every other branch unchanged."
        ),
    }


def main() -> None:
    document = json.loads(SUCCESSORS.read_text())
    rows = document["successors"]
    rf5 = rf5_row()
    rows[:] = [row for row in rows if not (row["kind"] == "RF5" and row["name"] == rf5["name"])]
    rows.append(rf5)
    for name, (before, reason) in ROWS.items():
        matches = [
            row for row in rows
            if row["kind"] == "RF6b" and (row["module"], row["name"]) == ("gnd.model", name)
        ]
        assert len(matches) <= 1
        if matches:
            row = matches[0]
        else:
            assert before is not None
            row = {"kind": "RF6b", "module": "gnd.model", "name": name,
                   "home": "gnd.model._validation", "before": before}
            rows.append(row)
        row["after"] = body_sha(name)
        row["reason"] = reason
    SUCCESSORS.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
