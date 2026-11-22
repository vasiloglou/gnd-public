"""Recompute close evidence against the named published source and main commit."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
MILESTONE = ROOT / ".gnd-planning/milestones/release-0.4.0"
ACCEPTED = "648cc6e07fc6ea0e4d8791a2a33a0d005f4e106a"
PUBLISHED = "9371d8e39e661d4953a228670a36411063f2aa74"
BASELINE = "cc4c8bf05ae8720b1ec5814b3709bfadb8643b16"


def run(*args: str) -> None:
    print("$ " + " ".join(args), flush=True)
    result = subprocess.run(args, cwd=ROOT, text=True, check=False)
    print(f"exit {result.returncode}", flush=True)
    assert result.returncode == 0


run("git", "diff", "--exit-code", BASELINE, PUBLISHED, "--", ".github")
run("git", "diff", "--exit-code", ACCEPTED, PUBLISHED, "--",
    "src", "pyproject.toml", "uv.lock", "LICENSE", "NOTICE")
run("git", "diff", "--exit-code", BASELINE, PUBLISHED, "--", "src/gnd/examples")

for name in ("005-phase-RV1.md", "008-phase-RV2.md", "010-phase-RV3.md", "011-publication.md"):
    text = (MILESTONE / name).read_text()
    citations = re.findall(r"  - path: ([^\n]+)\n    sha256: ([a-f0-9]{64})", text)
    assert citations
    for relative, expected in citations:
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected, relative
    print(f"{name}: {len(citations)} cited evidence digests match.")

lane = (MILESTONE / "evidence/close/default-lane.txt").read_text()
assert PUBLISHED in lane
assert "Python 3.13.18" in lane and "uv 0.13.7" in lane and "27.0.1" in lane
assert sum(map(int, re.findall(r"(\d+) passed,", lane))) == 19699
sections = lane.split("Shard ")[1:]
assert len(sections) == 6
assert sections[0].startswith("0 exit 1\n")
expected_errors = {
    "ERROR tests/test_public_optional.py::test_base_wheel_refuses_missing_synth_extra_and_still_checks",
    "ERROR tests/test_public_optional.py::test_declared_synth_extra_is_seeded_and_loader_valid",
}
assert {line for line in sections[0].splitlines() if line.startswith("ERROR ")} == expected_errors
assert "2489 passed, 125 deselected, 2 errors" in sections[0]
assert all(section.startswith(f"{number} exit 0\n") for number, section in enumerate(sections[1:], 1))
assert not any(line.startswith("FAILED ") for line in lane.splitlines())
print("Shard 0 exit 1 is accounted for by the two named baseline setup errors.")
print("Other five shards exit 0; no FAILED IDs in the retained summaries.")

review_status = (MILESTONE / "evidence/close/phase-review-status.txt").read_text()
assert "Three completed phase reviews with no ledger problems." in review_status
metadata = json.loads(subprocess.check_output(
    ["git", "show", f"{PUBLISHED}:.claude-plugin/plugin.json"], cwd=ROOT, text=True))
assert metadata["version"] == "0.4.0"
print("Publication tree .claude-plugin/plugin.json version 0.4.0 verified.")
