"""Compare the census probe run with the base run: tests red only under the probe."""
import re
import sys
from pathlib import Path

here = Path(__file__).parent


def failed(name: str) -> set[str]:
    text = (here / name).read_text(errors="replace")
    return set(re.findall(r"^(?:FAILED|ERROR) (\S+)", text, re.M))


base, probe = failed("census-base.txt"), failed("census-probe.txt")
print(f"base failures: {len(base)}; probe failures: {len(probe)}")
print("probe-only (pins of projected-JSON text on the ROF2 routes):")
for test in sorted(probe - base):
    print("  ", test)
print("base-only (should be empty):", sorted(base - probe))
sys.exit(0)
