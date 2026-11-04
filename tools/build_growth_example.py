"""Build the growth how-to's two evolve proposals over src/gnd/examples/growth/model.orm.yaml.

    uv run python tools/build_growth_example.py src/gnd/examples/growth

round-1.proposal.json adds a fact type shaped like order_arrives_via_channel
(admitted by --policy additive; the shape report names the match).
round-2.proposal.json binds the model as round 1 publishes it and adds a
mandatory constraint on the populated order_placed_by_customer (refused by
--policy additive, exit 3). The notes each round reads (round-N.document.txt)
are prose shown by the how-to; this script does not read them.
Deterministic: fixed ids, actor and timestamp.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from ruamel.yaml import YAML

from gnd.discover import output
from gnd.evolve import (
    CommittedText,
    ConstraintLocator,
    ElementLocator,
    EvolutionOperation,
    EvolutionOperationAudit,
    EvolutionOperationKind,
    EvolutionProposal,
)

RETURNED = {"id": "order_returned_via_channel", "reading": "{Order} is returned via {Channel}",
            "roles": [{"object_type": "order", "role_name": "order"},
                      {"object_type": "channel", "role_name": "channel"}]}
MANDATORY = {"type": "mandatory", "role": "order", "source": "llm-inferred", "status": "proposed",
             "modality": "deontic", "rationale": "Every order seems to name a customer.",
             "provenance": {"rationale_world_fact": "Shops record who placed each order."}}


def proposal(text: str, proposal_id: str, operation: EvolutionOperation) -> EvolutionProposal:
    candidate = output.candidate_document(YAML(typ="safe").load(text), (operation,))
    return EvolutionProposal(
        proposal_id=proposal_id,
        expected_model_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        candidate_model=CommittedText.from_text(output.candidate_text(candidate), media_type="application/yaml"),
        operations=(operation,), rationale="One round of growing the shop model.",
        audit=EvolutionOperationAudit(actor_id="agent:grower", origin="docs/how-to/grow-a-model.md",
                                      requested_at=datetime(2026, 11, 4, 12, 0, tzinfo=UTC)))


def main(directory: str) -> None:
    root = Path(directory)
    text = (root / "model.orm.yaml").read_text(encoding="utf-8")
    round_1 = proposal(text, "round-1", EvolutionOperation(
        operation_id="add-returned", kind=EvolutionOperationKind.ADD,
        locator=ElementLocator(collection="fact_types", element_id=RETURNED["id"]), after=RETURNED))
    round_2 = proposal(round_1.candidate_model.text, "round-2", EvolutionOperation(
        operation_id="add-mandatory", kind=EvolutionOperationKind.ADD,
        locator=ConstraintLocator(host="fact_type", host_id="order_placed_by_customer", family="mandatory"),
        after=MANDATORY))
    for name, value in (("round-1.proposal.json", round_1), ("round-2.proposal.json", round_2)):
        (root / name).write_text(json.dumps(value.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
                                 encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
