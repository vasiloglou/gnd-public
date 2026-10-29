"""Re-derive the IL4 AMIE run records under ILC-D3 (o): no learner runs (IL-R9).

Each retained ``reported.json`` gains ``facts_sha256``, the digest of the
``facts.tsv`` that invocation's AMIE read, which is retained beside it. The run
record as the run wrote it is kept as ``reported-r0.json``. An admitted
invocation's import is replayed from its own ``outcome.json`` argv, since its
proposal and report bind the record by digest; their originals are kept as
``*-r0.json``. The shipped staffing copies take the derived records.

Usage, from the repository root::

    uv run python .gnd-planning/milestones/ilp-learners/evidence/IL-close/rederive.py

Idempotent: a second run finds the ``-r0`` files and changes nothing.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
LIVE = ROOT / ".gnd-planning/milestones/ilp-learners/evidence/IL4/live"
FIXTURE = ROOT / "tests/fixtures/ilp_learners/il4"
SHIPPED = {1: "amie", 2: "amie-2"}


def _write_json(path: Path, document: object) -> None:
    path.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def _keep(path: Path) -> None:
    original = path.with_name(f"{path.stem}-r0{path.suffix}")
    if not original.exists():
        shutil.copy(path, original)


def main() -> int:
    for invocation, name in SHIPPED.items():
        live = LIVE / f"invocation-{invocation}"
        _keep(live / "reported.json")
        record = json.loads((live / "reported-r0.json").read_text(encoding="utf-8"))
        record["facts_sha256"] = hashlib.sha256((live / "facts.tsv").read_bytes()).hexdigest()
        _write_json(live / "reported.json", record)
        outcome = json.loads((live / "outcome.json").read_text(encoding="utf-8"))
        if outcome["import"] == "admitted":
            with tempfile.TemporaryDirectory() as scratch:
                work = Path(scratch)
                for source in (FIXTURE / "model.orm.yaml", FIXTURE / "population.yaml",
                               live / "rules.txt", live / "reported.json"):
                    shutil.copy(source, work / source.name)
                completed = subprocess.run([sys.executable, "-m", "gnd", *outcome["import_args"]],
                                           cwd=work, capture_output=True, check=False)
                if completed.returncode != outcome["import_exit"]:
                    print(completed.stderr.decode(), file=sys.stderr)
                    return 1
                for kept, data in (("proposal.json", (work / "proposal.json").read_bytes()),
                                   ("import-report.json", completed.stdout)):
                    _keep(live / kept)
                    (live / kept).write_bytes(data)
        shutil.copy(live / "reported.json",
                    ROOT / "src/gnd/examples/staffing/learners" / name / "reported.json")
        print(f"invocation {invocation}: facts_sha256 {record['facts_sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
