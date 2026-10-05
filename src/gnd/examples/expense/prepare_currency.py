"""Prepare this tutorial's additive currency proposal; never apply it.

Evolution proposal types and roster tooling are versioned CLI support contracts,
not part of the seven-function stable gnd.api application surface.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from gnd.artifacts import snapshot_tracked_roster
from gnd.evolve import EvolutionProposal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    before = json.loads(args.model.read_text(encoding="utf-8"))
    candidate_text = args.candidate.read_text(encoding="utf-8")
    after = json.loads(candidate_text)
    # Complete added elements are retained in the proposal, not reconstructed
    # from prose. GND preview independently replays them against the candidate.
    operations = []
    for collection in ("object_types", "fact_types"):
        ids = {row["id"] for row in before[collection]}
        for row in after[collection]:
            if row["id"] not in ids:
                operations.append({
                    "operation_id": "add-" + row["id"].replace("_", "-"),
                    "kind": "add",
                    "locator": {"locator_kind": "element", "collection": collection,
                                "element_id": row["id"]},
                    "after": row,
                })
    for row in after["constraints"]:
        if row not in before["constraints"]:
            operations.append({
                "operation_id": "add-" + row["id"].replace("_", "-"),
                "kind": "add",
                "locator": {"locator_kind": "constraint", "host": "model",
                            "family": row["type"]},
                "after": row,
            })
    manifest = json.loads((args.project / ".gnd-codegen.json").read_text(encoding="utf-8"))
    paths = sorted({row["relpath"] for row in manifest["files"]} | {
        ".gnd-codegen.json", "cli/__init__.py", "cli/expense_cli.py", "cli/reporting.py",
        "model.orm.json", "seed.population.json",
    })
    # Explicit roster excludes temporary outputs and interpreter caches.
    _, digest = snapshot_tracked_roster(args.project, paths, label="expense tutorial")
    proposal = EvolutionProposal.model_validate({
        "schema_version": 3,
        "proposal_id": "expense-currency",
        "expected_model_sha256": hashlib.sha256(args.model.read_bytes()).hexdigest(),
        "candidate_model": {
            "media_type": "application/yaml", "encoding": "utf-8", "text": candidate_text,
            "sha256": hashlib.sha256(candidate_text.encode("utf-8")).hexdigest(),
        },
        "operations": operations,
        "rationale": "Make the existing EUR denomination explicit on every expense.",
        "audit": {"actor_id": "tutorial-reader", "origin": "synthetic-expense-tutorial",
                  "requested_at": "2026-10-03T12:00:00Z"},
        "linked_projects": [{
            "project_id": "expense-application",
            "locator": {"base": "allowed-project-root", "path": args.project.as_posix()},
            "tracked_roster": {"schema_version": 1, "paths": paths},
            "expected_tracked_tree_sha256": digest,
        }],
        "artifacts": [],
    })
    args.output.write_text(proposal.model_dump_json(indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(operations)} additive operations; review with gnd evolve preview.")


if __name__ == "__main__":
    main()
