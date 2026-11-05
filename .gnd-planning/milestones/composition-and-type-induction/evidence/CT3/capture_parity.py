"""CT3 T1: digest version-1 witness production, replay and view over the v71 witness corpus.

Usage: python capture_parity.py SRC_DIR CORPUS_GZ WORK_DIR OUT.json
"""
import gzip
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

src, corpus, work, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
files = json.loads(gzip.open(corpus).read())
for name, content in files.items():
    target = work / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content if isinstance(content, str) else json.dumps(content, indent=2) + "\n")
env = {**os.environ, "PYTHONPATH": str(src / "src"), "PYTHONDONTWRITEBYTECODE": "1"}
env.pop("GND_DISCLOSURE", None)
rows = {}
for case in ("dispatch", "release"):
    root = work / case
    model, population, targets = root / "model.orm.yaml", root / "candidate.pop.json", root / "targets.json"
    commands = {
        "witness-raw": ["witness", model, population, "--targets", targets, "--raw"],
        "witness-view": ["witness", model, population, "--targets", targets],
    }
    for kind in ("direct", "recursive"):
        certificate = root / f"{kind}.witness.json"
        commands[f"replay-{kind}"] = ["replay", model, population, certificate, "--raw", "--json"]
        commands[f"replay-{kind}-view"] = ["replay", model, population, certificate]
        commands[f"view-{kind}"] = ["witness-view", certificate, "--json"]
        commands[f"view-{kind}-expand"] = ["witness-view", certificate, "--expand", "--json"]
    for name, argv in commands.items():
        result = subprocess.run([sys.executable, "-m", "gnd", *map(str, argv)], capture_output=True, env=env,
                                cwd=root, timeout=120, check=False)
        rows[f"{case}:{name}"] = {
            "exit": result.returncode,
            "stdout_sha256": hashlib.sha256(result.stdout.replace(str(work).encode(), b"<work>")).hexdigest(),
            "stderr_sha256": hashlib.sha256(result.stderr.replace(str(work).encode(), b"<work>")).hexdigest(),
        }
out.write_text(json.dumps(rows, indent=1, sort_keys=True) + "\n")
print(len(rows), "rows", sorted({r["exit"] for r in rows.values()}))
