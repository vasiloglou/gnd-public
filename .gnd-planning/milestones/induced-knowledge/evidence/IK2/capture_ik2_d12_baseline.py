"""Capture the D-12 gate outcome table (IK2 spec T5) from the repo in cwd.

Each row appends one new constraint to the first fact type of the
evolution-safe-additive before model and calls evolve.service._enforce_d12
directly. The outcome is "admitted" or the exact EvolutionError message.
Run from the repository root:  uv run python <this file> OUT.json
"""

import copy
import json
import subprocess
import sys
from pathlib import Path

from gnd.evolve import EvolutionError
from gnd.evolve.service import _enforce_d12

ROOT = Path.cwd()
FIXTURE = ROOT / "tests" / "fixtures" / "phase4_reference" / "evolution.json"

SOURCES = ("explicit", "sample", "common-sense", "llm-inferred", "user-supplied", "imported")
PROVENANCE = {
    "explicit": {"user_quote": "Each title belongs to one work item."},
    "sample": {"sample_size": 5},
    "common-sense": {"library_entry": "fixture-entry"},
    "llm-inferred": {"rationale_world_fact": "Titles name one work item."},
    "user-supplied": {"user_note": "Owner added this rule."},
    "imported": {
        "framework": "fixture",
        "artifact": "docs/REQUIREMENTS.md",
        "commit": "0" * 40,
        "sha256": "0" * 64,
        "anchor": "Each title belongs to one work item.",
    },
}


def base() -> dict:
    cases = json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"]
    row = next(item for item in cases if item["name"] == "evolution-safe-additive")
    return json.loads(row["inputs"]["before_model"]["text"])


def new_constraint(source: str, status: str, modality: str) -> dict:
    constraint = {
        "type": "uniqueness",
        "roles": ["title"],
        "source": source,
        "status": status,
        "modality": modality,
        "rationale": "Fixture rule for the D-12 baseline.",
        "provenance": copy.deepcopy(PROVENANCE[source]),
    }
    if source == "imported" and status == "confirmed":
        constraint["provenance"]["reviewed_in"] = "records/001-review.md"
    return constraint


def outcome(before: dict, candidate: dict) -> str:
    try:
        _enforce_d12(before, candidate)
    except EvolutionError as error:
        return str(error)
    return "admitted"


def with_constraint(document: dict, constraint: dict) -> dict:
    candidate = copy.deepcopy(document)
    candidate["fact_types"][0]["constraints"].append(constraint)
    return candidate


def main(out: Path) -> None:
    before = base()
    rows: dict[str, str] = {}
    for source in SOURCES:
        for status in ("proposed", "confirmed"):
            for modality in ("alethic", "deontic"):
                key = f"new:{source}:{status}:{modality}"
                rows[key] = outcome(before, with_constraint(before, new_constraint(source, status, modality)))
    rows["unchanged"] = outcome(before, copy.deepcopy(before))
    smuggled = new_constraint("llm-inferred", "proposed", "deontic")
    smuggled["provenance"]["actor_id"] = "owner:fixture"
    rows["audit-smuggling"] = outcome(before, with_constraint(before, smuggled))
    unknown = new_constraint("llm-inferred", "proposed", "deontic")
    unknown["source"] = "oracle"
    rows["unknown-source"] = outcome(before, with_constraint(before, unknown))
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()
    document = {
        "base_commit": commit,
        "function": "gnd.evolve.service._enforce_d12",
        "fixture": "tests/fixtures/phase4_reference/evolution.json#evolution-safe-additive",
        "rows": rows,
    }
    out.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
