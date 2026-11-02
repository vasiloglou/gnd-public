"""Write the gnd-why-not/2 goldens before the NM3 code exists (corpus-first, NM3 D1).

    uv run python .gnd-planning/milestones/why-not-near-misses/evidence/NM3/build_goldens.py

Reuses the WN2 builder, which derives each payload from the kernel and writes the
envelope and redaction itself, independently of the service, view and CLI. NM3
changes three things only: the schema version, the kernel's near-miss search
switched on, and the redacted view of the three near-miss fields (spec, Design).
The new case g20 runs the spelling-gap population.
"""

from __future__ import annotations

import functools
import importlib.util
from pathlib import Path

WN2 = Path(".gnd-planning/milestones/derivation-why-not/evidence/WN2/build_goldens.py")
spec = importlib.util.spec_from_file_location("wn2_build_goldens", WN2)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

builder.SCHEMA = "gnd-why-not/2"
builder.explain = functools.partial(builder.explain, near_misses=True)
_redact_blocker = builder.redact_blocker


def redact_blocker(blocker):
    out = _redact_blocker(blocker)
    if "near_misses" in blocker:
        out["near_miss_count"] = blocker["near_miss_count"]
        out["near_miss_truncated"] = blocker["near_miss_truncated"]
        out["near_misses"] = "redacted"
    return out


builder.redact_blocker = redact_blocker
S = "<fx>/spelling"
builder.CASES.append(("g20-spelling-gap", [
    f"{S}/model.orm.json", f"{S}/spelling-gap.pop.json", "--fact-type", "certified",
    "--row", f"{S}/claim.json"]))

if __name__ == "__main__":
    builder.main()
