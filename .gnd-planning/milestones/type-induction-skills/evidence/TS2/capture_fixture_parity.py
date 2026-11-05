"""TS2 T26: digest the TS1 fixture's discover runs without the judgement options.

Usage: python capture_fixture_parity.py SRC_DIR WORK_DIR OUT.json
Runs from the repository root whose tests/ supplies the TS1 fixture; SRC_DIR/src
is the gnd tree under test. Each case runs in three disclosure modes, with and
without --show-values, with and without --type-evidence, over the three TS1
fixture variants (applied induction, none, redacted attribute role).
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

src, work, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
sys.path.insert(0, str(Path.cwd() / "tests"))
import test_discover_type_evidence as fixture  # noqa: E402

base = {k: v for k, v in os.environ.items() if k != "GND_DISCLOSURE"}
base.update({"PYTHONPATH": str(src / "src"), "PYTHONDONTWRITEBYTECODE": "1"})
rows = {}
for variant, options in (("induced", {}), ("plain", {"induced": False}), ("redacted", {"redact": True})):
    for mode in ("unset", "internal", "customer"):
        for values in (False, True):
            for with_evidence in (False, True):
                key = f"{variant}-{mode}-{'values' if values else 'novalues'}-{'evidence' if with_evidence else 'plain'}"
                root = work / key
                root.mkdir(parents=True)
                fixture.build(root, **options)
                env = {**base, **({} if mode == "unset" else {"GND_DISCLOSURE": mode})}
                argv = [sys.executable, "-m", "gnd", "discover", "model.orm.yaml", "items.population.json",
                        "--out", "run.proposal.json", "--report", "run.report.json", "--actor", "test",
                        "--requested-at", "2026-11-05T00:00:00+00:00", "--families", "fact-type",
                        "--format", "json", *(["--show-values"] if values else []),
                        *(["--type-evidence", "run.evidence.json"] if with_evidence else [])]
                done = subprocess.run(argv, cwd=root, capture_output=True, env=env, timeout=300, check=False)
                files = {name: (hashlib.sha256((root / name).read_bytes()).hexdigest()
                                if (root / name).exists() else None)
                         for name in ("run.proposal.json", "run.report.json", "run.evidence.json")}
                rows[key] = {"exit": done.returncode, "stdout_sha256": hashlib.sha256(done.stdout).hexdigest(),
                             "stderr_sha256": hashlib.sha256(done.stderr).hexdigest(), **files}
out.write_text(json.dumps(rows, indent=1, sort_keys=True) + "\n")
