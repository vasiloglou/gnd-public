"""Prepare the tutorial's meal-cap proposal for ``gnd evolve``; never apply it.

The proposal changes one number in one rule: ``policy_meals`` allows meals up to
75 EUR today and the proposal lowers that to the cap you pass. It binds the exact
model bytes it was written against, carries the complete candidate model, and
records the rule before and after, so ``gnd evolve preview`` can replay the
change independently before anything is applied.

Usage: python prepare_meal_cap.py --model model.orm.json --cap 50 --output meal-cap.proposal.json
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

from gnd.evolve.models import EvolutionProposal, canonical_sha256


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--cap", type=int, required=True, help="the new meals cap in EUR")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    model_bytes = args.model.read_bytes()
    before_model = json.loads(model_bytes)
    rule_before = next(rule for rule in before_model["constraints"] if rule["id"] == "policy_meals")
    rule_after = copy.deepcopy(rule_before)
    rule_after["consequent"]["comparison"]["right"] = args.cap
    rule_after["source"] = "user-supplied"
    rule_after["provenance"] = {"user_quote": f"Meals expenses cost at most {args.cap} EUR."}
    after_model = copy.deepcopy(before_model)
    after_model["constraints"] = [rule_after if rule["id"] == "policy_meals" else rule
                                  for rule in after_model["constraints"]]
    candidate_text = json.dumps(after_model, indent=2) + "\n"
    proposal = EvolutionProposal.model_validate({
        "schema_version": 3,
        "proposal_id": f"meal-cap-{args.cap}",
        "expected_model_sha256": hashlib.sha256(model_bytes).hexdigest(),
        "candidate_model": {"media_type": "application/yaml", "encoding": "utf-8",
                            "text": candidate_text,
                            "sha256": hashlib.sha256(candidate_text.encode("utf-8")).hexdigest()},
        "operations": [{
            "operation_id": "lower-meal-cap",
            "kind": "modify",
            "locator": {"locator_kind": "constraint", "host": "model", "family": "guarded",
                        "canonical_before_sha256": canonical_sha256(rule_before),
                        "duplicate_occurrence": 0},
            "before": rule_before,
            "after": rule_after,
        }],
        "rationale": f"Finance lowered the meals cap from {rule_before['consequent']['comparison']['right']} to {args.cap} EUR.",
        "audit": {"actor_id": "tutorial-reader", "origin": "expense-tutorial",
                  "requested_at": "2026-10-14T00:00:00Z"},
        "linked_projects": [],
        "artifacts": [],
    })
    args.output.write_text(json.dumps(proposal.model_dump(mode="json"), indent=2) + "\n", encoding="utf-8")
    print(f"Proposal {proposal.proposal_id}: policy_meals {rule_before['consequent']['comparison']['right']} -> {args.cap} EUR")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
