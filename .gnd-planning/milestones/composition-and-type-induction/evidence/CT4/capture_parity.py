"""CT4 T6: digest every IK4 discover corpus run (without the fact-type family).

Usage: python capture_parity.py SRC_DIR WORK_DIR OUT.json
Runs from the repository root whose tests/ supplies the corpus and its
argv builder; SRC_DIR/src is the gnd tree under test.
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

src, work, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
sys.path.insert(0, str(Path.cwd() / "tests"))
import test_discover as corpus  # noqa: E402

env = {**os.environ, "PYTHONPATH": str(src / "src"), "PYTHONDONTWRITEBYTECODE": "1"}
env.pop("GND_DISCLOSURE", None)


def digest(data: bytes, root: Path) -> str:
    return hashlib.sha256(data.replace(str(root).encode(), b"<work>")).hexdigest()


rows = {}
for case in corpus.CASES["cases"]:
    root = work / case["id"]
    root.mkdir(parents=True, exist_ok=True)
    argv, _model, proposal, report = corpus._prepare(root, case)
    result = subprocess.run([sys.executable, "-m", "gnd", *argv], capture_output=True, env=env,
                            timeout=300, check=False)
    rows[case["id"]] = {
        "exit": result.returncode,
        "stdout_sha256": digest(result.stdout, root),
        "stderr_sha256": digest(result.stderr, root),
        "report_sha256": digest(report.read_bytes(), root) if report.exists() else None,
        "proposal_sha256": digest(proposal.read_bytes(), root) if proposal.exists() and not proposal.is_symlink() else None,
    }
out.write_text(json.dumps(rows, indent=1, sort_keys=True) + "\n")
print(len(rows), "rows", sorted({r["exit"] for r in rows.values()}))
