"""Build the seeded-growth example's proposals and judgment inputs.

    uv run python tools/build_seeded_growth_example.py src/gnd/examples/seeded_growth

The example (src/gnd/examples/seeded_growth/) grows an unattended root that
includes an owner-reviewed seed and starts with no source document.

- round-1.proposal.json declares round-1.document.txt as the first source
  document and adds an Author value type and "Author writes WorkKey", with
  spans and two sample rows.
- round-2.proposal.json binds the root as round 1 publishes it, declares
  round-2.document.txt and attaches a sample, proposed, deontic mandatory
  constraint to the seed's included fact type.
- population.json is a population of the grown root; policy.json and
  receipts.json bind it, and the grown root's bytes, for gnd judgments check.

Deterministic: fixed ids, actor and timestamp. Spans are computed from the
documents' canonical text (NFC code points of the strict UTF-8 decoding).
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from ruamel.yaml import YAML

from gnd.anchors import canonical_document_text
from gnd.artifacts import canonical_json_bytes
from gnd.discover import output
from gnd.evolve import (
    CommittedText,
    ConstraintLocator,
    ElementLocator,
    EvolutionOperation,
    EvolutionOperationAudit,
    EvolutionOperationKind,
    EvolutionProposal,
    SourceDocumentLocator,
)
from gnd.judgments import judgment_fact_digest

ROUND_DOCUMENTS = ("round-1.document.txt", "round-2.document.txt")
TARGET = "author_writes_work"
JUDGES = ("a", "b")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def span(raw: bytes, quote: str) -> dict:
    """The span of QUOTE, which must occur exactly once in the document's canonical text."""
    text = canonical_document_text(raw)
    start = text.find(quote)
    if start < 0 or text.find(quote, start + 1) >= 0:
        raise SystemExit(f"quote {quote!r} must occur exactly once")
    end = start + len(quote)
    return {"document_sha256": _sha(raw), "start": start, "end": end,
            "excerpt_sha256": _sha(text[start:end].encode("utf-8"))}


def _op(operation_id: str, locator, after: dict) -> EvolutionOperation:
    return EvolutionOperation(operation_id=operation_id, kind=EvolutionOperationKind.ADD, locator=locator,
                              after=after)


def _declare(raw: bytes, label: str) -> EvolutionOperation:
    digest = _sha(raw)
    return _op(f"declare-{label}", SourceDocumentLocator(sha256=digest), {"sha256": digest, "label": label})


def proposal(text: str, proposal_id: str, operations: tuple) -> EvolutionProposal:
    candidate = output.candidate_document(YAML(typ="safe").load(text), operations)
    return EvolutionProposal(
        schema_version=3, proposal_id=proposal_id,
        expected_model_sha256=_sha(text.encode("utf-8")),
        candidate_model=CommittedText.from_text(output.candidate_text(candidate), media_type="application/yaml"),
        operations=operations, rationale="One unattended growth round from a reviewed seed.",
        audit=EvolutionOperationAudit(actor_id="agent:grower", origin="unattended-growth.md",
                                      requested_at=datetime(2026, 11, 23, 12, 0, tzinfo=UTC)))


def rounds(root: Path) -> tuple[EvolutionProposal, EvolutionProposal]:
    one, two = ((root / name).read_bytes() for name in ROUND_DOCUMENTS)
    author = {"id": "author", "kind": "value", "name": "Author", "primitive": "String",
              "provenance": {"spans": [span(one, "An author writes works")]}}
    writes = {"id": TARGET, "reading": "{Author} writes {WorkKey}",
              "roles": [{"object_type": "author", "role_name": "author"},
                        {"object_type": "work", "role_name": "work"}],
              "sample_population": [{"author": "Ana", "work": "W-1"}, {"author": "Ben", "work": "W-2"}],
              "provenance": {"spans": [span(one, "An author writes works")],
                             "sample_spans": [{"row": 0, "span": span(one, "Ana wrote the work W-1")},
                                              {"row": 1, "span": span(one, "Ben wrote the work W-2")}]}}
    every_work = {"type": "mandatory", "role": "work", "source": "sample", "status": "proposed",
                  "modality": "deontic", "rationale": "Every work in the catalogue rows has a version.",
                  "provenance": {"sample_size": 2, "spans": [span(two, "Every work we hold has a version")]}}
    text = (root / "root.orm.yaml").read_text(encoding="utf-8")
    round_1 = proposal(text, "round-1", (
        _declare(one, ROUND_DOCUMENTS[0]),
        _op("add-author", ElementLocator(collection="object_types", element_id="author"), author),
        _op("add-writes", ElementLocator(collection="fact_types", element_id=TARGET), writes)))
    round_2 = proposal(round_1.candidate_model.text, "round-2", (
        _declare(two, ROUND_DOCUMENTS[1]),
        _op("attach-every-work", ConstraintLocator(host="included_fact_type", host_id="work_has_version",
                                                   family="mandatory"), every_work)))
    return round_1, round_2


def population() -> dict:
    return {
        "population": {"source": "fixture", "model": "root.orm.yaml", "model_id": "urn:example:seeded-growth",
                       "covers": ["work_has_version", TARGET]},
        "instances": {"work": ["W-1", "W-2"], "author": ["Ana", "Ben"]},
        "facts": {"work_has_version": [{"work": "W-1", "version": "V-1"}, {"work": "W-2", "version": "V-2"}],
                  TARGET: [{"author": "Ana", "work": "W-1"}, {"author": "Ben", "work": "W-2"}]},
    }


def judgments(model_bytes: bytes, population_bytes: bytes, evidence: bytes) -> tuple[dict, dict]:
    """A two-judge consumer-pinned policy and approving receipts for the first authorship fact."""
    fact = json.loads(population_bytes)["facts"][TARGET][0]
    receipts = [{
        "receipt_id": f"r-{judge}", "judge_id": judge, "verdict": "approve", "trust": "consumer-pinned",
        "subject": {"model_sha256": _sha(model_bytes), "population_sha256": _sha(population_bytes),
                    # The check report carries no reference_binding for a model without
                    # reference populations, so the subject binds none.
                    "reference_identity": None,
                    "fact_type": TARGET, "index": 0, "fact_sha256": judgment_fact_digest(TARGET, 0, fact)},
        "sources": [{"path": ROUND_DOCUMENTS[0], "sha256": _sha(evidence), "quote": None}],
        "external_evidence": None,
    } for judge in JUDGES]
    policy = {
        "admission": {"evidence_floor": None, "minimum_approvals": 2}, "judges": list(JUDGES),
        "policy_id": "seeded-growth", "repair": {"evidence_floor": None, "minimum_rejections": 1},
        "schema_version": 1, "targets": [{"fact_type": TARGET, "index": 0}], "trust_mode": "consumer-pinned",
        "trusted_receipts": [{"judge_id": r["judge_id"],
                              "receipt_sha256": _sha(canonical_json_bytes(r, exact_numbers=True))}
                             for r in receipts],
    }
    return policy, {"schema_version": 1, "receipts": receipts}


def _json(value) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main(directory: str) -> None:
    root = Path(directory)
    round_1, round_2 = rounds(root)
    files = {"round-1.proposal.json": _json(round_1.model_dump(mode="json")),
             "round-2.proposal.json": _json(round_2.model_dump(mode="json")),
             "population.json": _json(population())}
    grown = round_2.candidate_model.text.encode("utf-8")
    policy, receipts = judgments(grown, files["population.json"].encode("utf-8"),
                                 (root / ROUND_DOCUMENTS[0]).read_bytes())
    files["policy.json"] = _json(policy)
    files["receipts.json"] = _json(receipts)
    for name, text in files.items():
        (root / name).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
