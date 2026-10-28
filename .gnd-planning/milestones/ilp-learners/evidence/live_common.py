"""Shared pieces of the ilp-learners live-run scripts (IL5-Q4, IL3-D10 (o)).

IL1's, IL2's and IL5's scripts each carry their own copy of these; their bytes are
bound by digest in their records, so they are left as they are. From IL3 on, a
live-run script imports this module: the sanitizer (IL-R10), the bounded
environment (IL-R2), the export step that records E, the termination and import
mappings (IL-R9, IL5-Q1 (o)), and the fixed-argument import.
"""

from __future__ import annotations

import getpass
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from gnd.export.ilp import refusal_name

REPO = Path(__file__).resolve().parents[4]
EXAMPLE = REPO / "src" / "gnd" / "examples" / "refunds"
SCRATCH_PATH = re.compile(r"(?:/private)?/tmp/claude-\d+/\S*?/scratchpad/il[0-9]-live")
_NAME = re.compile(r"[a-z]+(?:-[a-z]+)*")


class Sanitizer:
    """Scratch, repository and home paths and the user name, as placeholders (IL-R10)."""

    def __init__(self, *scratch: Path) -> None:
        self.pairs = [(str(path.resolve()), "<scratch>") for path in scratch]
        self.pairs += [(str(path), "<scratch>") for path in scratch]
        self.pairs += [(str(REPO), "<repo>"), (str(Path.home()), "<home>")]
        self.user = getpass.getuser()

    def __call__(self, text: str) -> str:
        for old, new in self.pairs:
            text = text.replace(old, new)
        text = SCRATCH_PATH.sub("<scratch>", text)
        return text.replace(self.user, "<user>")


def environment(scratch: Path) -> dict[str, str]:
    """An explicit environment: system PATH only, home and temp under the scratch prefix."""
    home, tmp = scratch / "home", scratch / "tmp"
    home.mkdir(exist_ok=True)
    tmp.mkdir(exist_ok=True)
    return {"PATH": "/usr/bin:/bin", "HOME": str(home), "USER": getpass.getuser(),
            "TMPDIR": str(tmp), "LANG": "C.UTF-8"}


def export(target: str, out: Path) -> tuple[str, str]:
    """``gnd export ilp`` over the refunds example; E and the command's stdout."""
    done = subprocess.run([sys.executable, "-m", "gnd", "export", "ilp", str(EXAMPLE / "model.orm.yaml"),
                           "--labels", str(EXAMPLE / "labels.json"), "--target", target, "--out", str(out)],
                          capture_output=True, text=True, check=True)
    return hashlib.sha256((out / "export.json").read_bytes()).hexdigest(), done.stdout


def termination(process: dict[str, Any]) -> str:
    """IL-R9's closed list; truncation first (IL5-Q1 (o)); no learner has its own timeout (IL2-Q4)."""
    if process["stdout_truncated"] or process["stderr_truncated"]:
        return "output-limit"
    if process["status"] == "timed-out":
        return "wall-clock-kill"
    if process["status"] != "succeeded":
        return "rendering-rejected"
    return "completed"


def import_outcome(refusal: str) -> str:
    """``refused:<name>``; a file-level or capped refusal is ``refused:unparsable``."""
    name = "" if refusal.startswith("clauses ") else refusal_name(refusal)
    return f"refused:{name}" if _NAME.fullmatch(name) else "refused:unparsable"


def write_json(path: Path, document: Any) -> None:
    path.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def run_import(work: Path, out: Path, files: tuple[str, ...], args: tuple[str, ...],
               clean: Sanitizer) -> tuple[int, str]:
    """The fixed-argument import from a fixed directory (IL-R9); retains its result in ``out``."""
    imports = work / "import"
    shutil.copytree(EXAMPLE, imports, ignore=shutil.ignore_patterns("*.py", "README.md"))
    for name in files:
        shutil.copy(out / name, imports / name)
    imported = subprocess.run([sys.executable, "-m", "gnd", *args], cwd=imports,
                              capture_output=True, text=True, check=False)
    if imported.returncode == 0:
        (out / "import-report.json").write_text(clean(imported.stdout), encoding="utf-8")
        shutil.copy(imports / "proposal.json", out / "proposal.json")
        return 0, "admitted"
    refusal = clean(imported.stderr).strip()
    (out / "import-stderr.txt").write_text(refusal + "\n", encoding="utf-8")
    return imported.returncode, import_outcome(refusal)
