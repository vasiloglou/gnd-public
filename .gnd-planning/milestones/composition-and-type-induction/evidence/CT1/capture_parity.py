"""CT1 T7: digest gnd check and verbalize outputs over every v1 anchor input.

Usage: python capture_parity.py SRC_DIR FIXTURE_ROOT OUT.json
SRC_DIR is the gnd source tree to run (its src/ goes first on sys.path);
FIXTURE_ROOT holds tests/fixtures from the tree under test, so every column
reads the same input bytes.
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

src, fixtures, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
env = {**os.environ, "PYTHONPATH": str(src / "src"), "PYTHONDONTWRITEBYTECODE": "1"}
env.pop("GND_DISCLOSURE", None)
phase5 = fixtures / "v70-phase5"
cases = json.loads((phase5 / "cases.json").read_text())["cases"]
inputs = [dict(case, root=phase5) for case in cases]
inputs.append({"id": "v70-phase1", "root": fixtures / "v70-phase1", "model": "model.orm.yaml",
               "population": "population.pop.json", "anchors": "population.pop.json.anchors.json",
               "document": "document.txt"})
# A v1 sidecar that binds but whose label anchor points past the value, so
# the failing-anchor path (exit 1) is in the table too.
failing = out.parent / "v1-failing"
failing.mkdir(exist_ok=True)
phase1 = fixtures / "v70-phase1"
for name in ("model.orm.yaml", "population.pop.json", "document.txt"):
    (failing / name).write_bytes((phase1 / name).read_bytes())
sidecar = json.loads((phase1 / "population.pop.json.anchors.json").read_text())
source = (phase1 / "document.txt").read_text(encoding="utf-8")
for anchor in sidecar["anchors"]:
    if anchor["fact_key"]["fact_type"] == "record_has_label":
        anchor["span"] = {"start": 40, "end": 60}
        anchor["excerpt_sha256"] = hashlib.sha256(source[40:60].encode("utf-8")).hexdigest()
(failing / "population.pop.json.anchors.json").write_text(json.dumps(sidecar))
inputs.append({"id": "v1-failing", "root": failing, "model": "model.orm.yaml",
               "population": "population.pop.json", "anchors": "population.pop.json.anchors.json",
               "document": "document.txt"})
rows = {}
for case in inputs:
    root = case["root"]
    tail = []
    if "anchors" in case:
        tail += ["--anchors", str(root / case["anchors"])]
    if "document" in case:
        tail += ["--document", str(root / case["document"])]
    commands = {
        "check-text": ["check", str(root / case["model"]), str(root / case["population"]), *tail],
        "check-json": ["check", str(root / case["model"]), str(root / case["population"]), *tail, "--format", "json"],
        "verbalize-text": ["verbalize", "population", str(root / case["model"]), str(root / case["population"]), *tail, "--format", "text"],
    }
    if case.get("unredacted"):
        commands = {name: [*argv, "--unredacted"] for name, argv in commands.items()}
    for name, argv in commands.items():
        result = subprocess.run([sys.executable, "-m", "gnd", *argv], capture_output=True, env=env, timeout=60, check=False)
        rows[f"{case['id']}:{name}"] = {
            "exit": result.returncode,
            "stdout_sha256": hashlib.sha256(result.stdout.replace(str(failing).encode(), b"<failing>").replace(str(fixtures).encode(), b"<fixtures>")).hexdigest(),
            "stderr_sha256": hashlib.sha256(result.stderr.replace(str(failing).encode(), b"<failing>").replace(str(fixtures).encode(), b"<fixtures>")).hexdigest(),
        }
out.write_text(json.dumps(rows, indent=1, sort_keys=True) + "\n")
print(len(rows), "rows")
