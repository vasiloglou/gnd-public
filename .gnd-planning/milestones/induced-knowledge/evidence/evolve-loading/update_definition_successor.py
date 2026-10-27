"""Add the evolve-loading follow-up's RF6b definition successor for gnd.model.load_model_bytes.

Run from the repository root after the final source edit:
    uv run python <this file>
The body digest is computed exactly as tests/test_rf6_packages.py computes it,
chained from the frozen RF7 row whose "after" is this row's "before".
"""

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path.cwd()
SUCCESSORS = ROOT / ".gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/source-successors.json"
FROZEN = ROOT / ".gnd-planning/milestones/code-refactoring/evidence/RF7/definition-successors.json"
MODULE, NAME, HOME = "gnd.model", "load_model_bytes", "gnd.model"
REASON = (
    "Owner-approved evolve-loading follow-up (2026-10-27, spec D3-A): the parse half of "
    "load_model_bytes (the input cap, strict JSON for a .json source, the alias/event "
    "guard and the round-trip reader) moves verbatim into parse_model_document, which "
    "evolve shares; load_model_bytes calls it and validates exactly as before."
)


def body_sha256() -> str:
    source = (ROOT / "src/gnd/model/__init__.py").read_text()
    (node,) = [n for n in ast.parse(source).body
               if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == NAME]
    start = min([node.lineno] + [d.lineno for d in node.decorator_list])
    body = "".join(source.splitlines(keepends=True)[start - 1:node.end_lineno])
    return hashlib.sha256(body.encode()).hexdigest()


def main() -> None:
    (frozen,) = [r for r in json.loads(FROZEN.read_text()) if (r["module"], r["name"]) == (MODULE, NAME)]
    document = json.loads(SUCCESSORS.read_text())
    rows = [r for r in document["successors"]
            if not (r["kind"] == "RF6b" and (r.get("module"), r["name"]) == (MODULE, NAME))]
    rows.append({"kind": "RF6b", "module": MODULE, "name": NAME, "home": HOME,
                 "before": frozen["after"], "after": body_sha256(), "reason": REASON})
    document["successors"] = rows
    SUCCESSORS.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{NAME}: {frozen['after']} -> {rows[-1]['after']}")


if __name__ == "__main__":
    main()
