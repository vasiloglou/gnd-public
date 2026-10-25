"""The two outputs of ``gnd discover``: the evolve proposal and the report (IK4 §6).

The report is ``gnd-discover/1`` (``src/gnd/discover.schema.json``, closed); every
key is always present. The proposal is an ordinary schema-3 evolve proposal of
ADD constraint operations, built with evolve's own replay so the candidate it
carries is exactly what ``gnd evolve preview`` will recompute.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from gnd.discover.candidates import Candidate
from gnd.evolve.models import (
    CommittedText,
    ConstraintLocator,
    EvolutionOperation,
    EvolutionOperationAudit,
    EvolutionOperationKind,
    EvolutionProposal,
)
from gnd.evolve.service import _apply_declared_operations

REPORT_SCHEMA_VERSION = "gnd-discover/1"
INDUCER = "gnd-discover"


def canonical_bytes(document: Any) -> bytes:
    return (json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
            + "\n").encode("utf-8")


def induced(candidate: Candidate, *, version: str, digest: str, ref: str) -> dict[str, Any]:
    """The candidate as an induced, proposed, deontic constraint (IK2 envelope)."""
    subjects = candidate.subjects
    assert subjects is not None and subjects.count > 0
    induction = {
        "inducer": {"name": INDUCER, "version": version},
        "method": INDUCER,
        "manifest_sha256": digest,
        "examples": list(subjects.examples),
        "support": {"numerator": subjects.count - subjects.violations,
                    "denominator": subjects.count},
        "counterexamples": list(subjects.counterexamples),
        "evidence": [{"ref": ref, "sha256": digest}],
    }
    return {**candidate.core, "source": "induced", "status": "proposed", "modality": "deontic",
            "provenance": {"induction": induction}}


def operations(constraints: list[tuple[Candidate, dict[str, Any]]]) -> tuple[EvolutionOperation, ...]:
    result = []
    for number, (candidate, constraint) in enumerate(constraints):
        locator = (
            ConstraintLocator(host="fact_type", host_id=candidate.host, family=candidate.core["type"])
            if candidate.host is not None
            else ConstraintLocator(host="model", family=candidate.core["type"])
        )
        result.append(
            EvolutionOperation(
                operation_id=f"discover-{number:04d}",
                kind=EvolutionOperationKind.ADD,
                locator=locator,
                after=constraint,
            )
        )
    return tuple(result)


def candidate_document(before: dict[str, Any], ops: tuple[EvolutionOperation, ...]) -> dict[str, Any]:
    return _apply_declared_operations(before, ops)


def candidate_text(document: dict[str, Any]) -> str:
    """JSON is a YAML subset; the shipped proposal fixtures carry the same form."""
    return json.dumps(document, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n"


def proposal(
    *,
    model_bytes: bytes,
    document: dict[str, Any],
    ops: tuple[EvolutionOperation, ...],
    actor: str,
    requested_at: datetime,
    population_name: str,
) -> EvolutionProposal:
    text = candidate_text(document)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return EvolutionProposal(
        proposal_id=f"discover-{digest[:16]}",
        expected_model_sha256=hashlib.sha256(model_bytes).hexdigest(),
        candidate_model=CommittedText.from_text(text, media_type="application/yaml"),
        operations=ops,
        rationale=f"gnd discover: {len(ops)} candidate constraints observed in {population_name}",
        audit=EvolutionOperationAudit(
            actor_id=actor, origin="gnd discover", requested_at=requested_at
        ),
    )


def write(path: Path, data: bytes) -> None:
    """Write one output; a symbolic link at ``path`` is refused, never followed."""
    if path.is_symlink():
        raise PermissionError(f"refusing to write through symbolic link {path}")
    path.write_bytes(data)


def render_text(report: dict[str, Any]) -> str:
    lines = [
        "GND DISCOVER",
        f"MODEL {report['model']['path']}",
        f"POPULATION {report['population']['path']}",
        f"EMITTED {len(report['emitted'])}",
    ]
    lines.extend(f"  {row['ref']} {row['family']} support={row['support']['numerator']}"
                 for row in report["emitted"])
    lines.append(f"NEAR MISSES {len(report['near_misses'])}")
    lines.extend(
        f"  {row['family']} violations={row['violations']}/{row['subjects']}"
        for row in report["near_misses"]
    )
    lines.append("REJECTED " + " ".join(f"{k}={v}" for k, v in report["rejected"].items()))
    lines.append("SUPPRESSED " + " ".join(f"{k}={v}" for k, v in report["suppressed"].items() if v))
    lines.append(f"WORK total={report['work']['total']}")
    lines.append(f"PROPOSAL {report['proposal'] or '(none)'}")
    return "\n".join(lines) + "\n"
