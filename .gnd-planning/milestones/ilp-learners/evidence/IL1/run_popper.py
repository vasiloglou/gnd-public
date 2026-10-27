"""IL1 live run: one real Popper run over the IK6 refunds export (evidence only).

Spec: .gnd-planning/milestones/ilp-learners/notes/phase-IL1-spec.md §6 "Live run",
§12-§15 (invocation 2 is the IL1-A1 run (o)). Not a GND command and not a test lane (IL-R2, IK5-D12 (o)).

Usage, from the repository root, after the approved scratch install (§12):

    uv run python .gnd-planning/milestones/ilp-learners/evidence/IL1/run_popper.py \
        --scratch SCRATCH --invocation N

SCRATCH holds SWI-Prolog.app and venv/ (Popper v5.0.1 at commit 578a4e2). The
script writes, under evidence/IL1/live/invocation-N/, the raw logs, the extracted
program, the SWI run record, the import result and outcome.json. Every file it
writes has the scratch, repository and home paths and the user name replaced by
placeholders (IL-R10). Popper and SWI run through gnd.process.run_bounded_process
with an explicit environment; the import runs from a fixed working directory with
fixed arguments, so tests/test_ilp_learners.py T9 can replay it.
"""

from __future__ import annotations

import argparse
import asyncio
import getpass
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from gnd.export.ilp_popper import extract_program, quote
from gnd.process import ProcessLimits, run_bounded_process

REPO = Path(__file__).resolve().parents[5]
EXAMPLE = REPO / "src" / "gnd" / "examples" / "refunds"
OUT = Path(__file__).resolve().parent / "live"
POPPER_COMMIT = "578a4e26a22006b9325fe819486242f7fafc3195"
LEARNER = {"name": "popper", "version": "5.0.1+578a4e2"}
#: Popper's own timeout, below the wall clock (§6).
POPPER_TIMEOUT = "540"
LIMITS = ProcessLimits(timeout_seconds=600, terminate_grace_seconds=10, stdin_limit_bytes=0,
                       stdout_limit_bytes=16 * 1024 * 1024, stderr_limit_bytes=4 * 1024 * 1024,
                       total_output_limit_bytes=20 * 1024 * 1024)
SWI_LIMITS = ProcessLimits(timeout_seconds=60, terminate_grace_seconds=5, stdin_limit_bytes=0,
                           stdout_limit_bytes=1024 * 1024, stderr_limit_bytes=1024 * 1024,
                           total_output_limit_bytes=2 * 1024 * 1024)
#: Popper v5.0.1's own popper.py entry point (MIT, upstream), run with -c because
#: the package installs no console script.
ENTRY = ("from popper.util import Settings, print_prog_score\n"
         "from popper.loop import popper\n"
         "settings = Settings.from_args()\n"
         "prog, score = popper(settings)\n"
         "print_prog_score(prog, score, settings, settings.noisy) if prog else print('NO SOLUTION')\n")
#: The fixed import arguments (§6), relative to the import directory.
IMPORT_ARGS = ("import", "ilp-rules", "model.orm.yaml", "program.pl", "--labels", "labels.json",
               "--reported-coverage", "run.json", "--target", "popper", "--out", "proposal.json",
               "--actor", "ilp-live", "--requested-at", "2026-01-01T00:00:00Z", "--format", "json")


SCRATCH_PATH = re.compile(r"(?:/private)?/tmp/claude-\d+/\S*?/scratchpad/il1-live")


class Sanitizer:
    def __init__(self, scratch: Path) -> None:
        self.pairs = [(str(scratch.resolve()), "<scratch>"), (str(scratch), "<scratch>"),
                      (str(REPO), "<repo>"), (str(Path.home()), "<home>")]
        self.user = getpass.getuser()

    def __call__(self, text: str) -> str:
        for old, new in self.pairs:
            text = text.replace(old, new)
        # run_bounded_process redacts environment values (the user name) to a
        # mask before this runs, so the scratch path can also arrive with its
        # user component masked; any scratchpad path collapses to <scratch>.
        text = SCRATCH_PATH.sub("<scratch>", text)
        return text.replace(self.user, "<user>")


def environment(scratch: Path) -> dict[str, str]:
    home, tmp = scratch / "home", scratch / "tmp"
    home.mkdir(exist_ok=True)
    tmp.mkdir(exist_ok=True)
    return {"PATH": f"{scratch / 'SWI-Prolog.app' / 'Contents' / 'MacOS'}:/usr/bin:/bin",
            "HOME": str(home), "USER": getpass.getuser(), "TMPDIR": str(tmp), "LANG": "C.UTF-8"}


def termination(result) -> str:
    if result.status == "timed-out":
        return "wall-clock-kill"
    if result.stdout_truncated or result.stderr_truncated:
        return "output-limit"
    if result.return_code != 0:
        return "rendering-rejected"
    if result.elapsed_seconds >= float(POPPER_TIMEOUT):
        return "learner-timeout"
    return "completed"


def swi_coverage(scratch: Path, kb: Path, program: str, ids: list[str]) -> list[dict]:
    """Each clause's covered examples, by SWI over bk.pl -- an evaluator that is not GND."""
    rows = []
    swipl = str(scratch / "SWI-Prolog.app" / "Contents" / "MacOS" / "swipl")
    for index, clause in enumerate(line for line in program.splitlines() if line):
        (kb / "clause.pl").write_text(clause + "\n", encoding="utf-8")
        listed = ",".join(quote(i) for i in ids)
        (kb / "cover.pl").write_text(
            ":- initialization(main, main).\n"
            ":- consult('bk.pl').\n:- consult('clause.pl').\n"
            f"main :- forall(nth0(I, [{listed}], E), (catch(wrong(E), _, fail) -> (write(I), nl) ; true)).\n",
            encoding="utf-8")
        result = asyncio.run(run_bounded_process((swipl, "-q", "cover.pl"), cwd=kb,
                                                 env=environment(scratch), limits=SWI_LIMITS))
        if result.return_code != 0:
            raise SystemExit(f"SWI coverage failed for clause {index}: {result.stderr[-400:]!r}")
        covered = sorted({int(line) for line in result.stdout.decode().split()})
        rows.append({"clause": index, "covered": [ids[i] for i in covered]})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scratch", required=True, type=Path)
    parser.add_argument("--invocation", required=True, type=int)
    args = parser.parse_args()
    scratch = args.scratch.resolve()
    clean = Sanitizer(scratch)
    out = OUT / f"invocation-{args.invocation}"
    if out.exists():
        raise SystemExit(f"{out} exists: every invocation is retained, never overwritten (IL-R9)")
    work = scratch / f"work-{args.invocation}"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)

    exported = subprocess.run([sys.executable, "-m", "gnd", "export", "ilp", str(EXAMPLE / "model.orm.yaml"),
                               "--labels", str(EXAMPLE / "labels.json"), "--target", "popper",
                               "--out", str(work / "export")], capture_output=True, text=True, check=True)
    index = (work / "export" / "export.json").read_bytes()
    digest = hashlib.sha256(index).hexdigest()
    neutral = json.loads((work / "export" / "neutral.json").read_text(encoding="utf-8"))
    ids = [example["id"] for example in neutral["examples"]]

    python = str(scratch / "venv" / "bin" / "python")
    argv = (python, "-c", ENTRY, "popper", "--timeout", POPPER_TIMEOUT)
    result = asyncio.run(run_bounded_process(argv, cwd=work / "export", env=environment(scratch),
                                             limits=LIMITS))
    stdout, stderr = result.stdout.decode("utf-8", "replace"), result.stderr.decode("utf-8", "replace")
    program = extract_program(stderr)

    out.mkdir(parents=True)
    (out / "raw-stdout.txt").write_text(clean(stdout), encoding="utf-8")
    (out / "raw-stderr.txt").write_text(clean(stderr), encoding="utf-8")
    (out / "program.pl").write_text(program, encoding="utf-8")
    outcome = {
        "invocation": args.invocation,
        "run_of_record": args.invocation == 1,
        "termination": termination(result),
        "import": "none",
        "export_sha256": digest,
        "adapter_version": json.loads(index)["adapter_version"],
        "export_stdout": clean(exported.stdout),
        "popper": {"commit": POPPER_COMMIT, "package_metadata_version": "5.0.0",
                   "learner": LEARNER, "timeout": POPPER_TIMEOUT,
                   "argv": [clean(part) if part != ENTRY else "<ENTRY>" for part in argv],
                   "entry": ENTRY, "process": json.loads(result.model_dump_json())},
        "limits": json.loads(LIMITS.model_dump_json()),
        "import_args": list(IMPORT_ARGS),
        "numbers": {
            "export_sha256": "computed by GND's export",
            "popper_scores": "printed by Popper, kept verbatim in raw-stderr.txt",
            "run.json coverage": "independent evaluation (SWI): each clause over bk.pl, per example",
            "import report": "computed by GND's import",
        },
        "reproducibility": "single run, reproducibility not measured",
    }
    if program:
        run = {"schema_version": "gnd-ilp-run/1", "learner": LEARNER, "export_sha256": digest,
               "clauses_sha256": hashlib.sha256(program.encode("utf-8")).hexdigest(),
               "coverage": swi_coverage(scratch, work / "export" / "popper", program, ids)}
        (out / "run.json").write_text(json.dumps(run, indent=1) + "\n", encoding="utf-8")
        imports = work / "import"
        shutil.copytree(EXAMPLE, imports, ignore=shutil.ignore_patterns("*.py", "README.md"))
        shutil.copy(out / "program.pl", imports / "program.pl")
        shutil.copy(out / "run.json", imports / "run.json")
        imported = subprocess.run([sys.executable, "-m", "gnd", *IMPORT_ARGS], cwd=imports,
                                  capture_output=True, text=True, check=False)
        outcome["import_exit"] = imported.returncode
        if imported.returncode == 0:
            outcome["import"] = "admitted"
            (out / "import-report.json").write_text(clean(imported.stdout), encoding="utf-8")
            shutil.copy(imports / "proposal.json", out / "proposal.json")
        else:
            refusal = clean(imported.stderr).strip()
            name = refusal.split(": ")[1] if refusal.startswith("clause ") else refusal.split(":")[0]
            outcome["import"] = f"refused:{name}"
            (out / "import-stderr.txt").write_text(refusal + "\n", encoding="utf-8")
    (out / "outcome.json").write_text(json.dumps(outcome, indent=1, sort_keys=True) + "\n",
                                      encoding="utf-8")
    print(f"invocation {args.invocation}: termination {outcome['termination']}, import {outcome['import']}")
    return 0


if __name__ == "__main__":
    os.umask(0o022)
    sys.exit(main())
