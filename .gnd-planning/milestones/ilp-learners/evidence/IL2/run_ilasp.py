"""IL2 live run: one real ILASP run over the IK6 refunds export (evidence only).

Spec: .gnd-planning/milestones/ilp-learners/notes/phase-IL2-spec.md §6 "Live run",
§13 and §14 (IL2-D12 (o) and the IL2-F5 probe corrections). Not a GND command and
not a test lane (IL-R2, plan D3 (a) (o)).

Usage, from the repository root, after the approved scratch installs:

    uv run python .gnd-planning/milestones/ilp-learners/evidence/IL2/run_ilasp.py \
        --scratch SCRATCH --clingo-python PYTHON --invocation N

SCRATCH holds ilasp/ILASP (4.4.1), py310/ (python-build-standalone 3.10.20) and
fw/ (the framework-path shim). PYTHON is a Python with clingo 5.8.2, the
independent evaluator (IL-R4). The script writes, under
evidence/IL2/live/invocation-N/, the raw logs, the extracted hypothesis, the
clingo run record, the import result and outcome.json, with the scratch,
repository and home paths and the user name replaced by placeholders (IL-R10).
ILASP and clingo run through gnd.process.run_bounded_process with an explicit
environment; the import runs from a fixed working directory with fixed
arguments, so tests/test_ilp_asp.py T9 can replay it.
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

from gnd.export.ilp_asp import extract_hypothesis, refusal_name, split_task
from gnd.process import ProcessLimits, run_bounded_process

REPO = Path(__file__).resolve().parents[5]
EXAMPLE = REPO / "src" / "gnd" / "examples" / "refunds"
OUT = Path(__file__).resolve().parent / "live"
LEARNER = {"name": "ilasp", "version": "4.4.1"}
ILASP_SHA256 = "7e9fd1ccbafa3241558c1f70a868b1c3e141de52dbdc76d26396b70f492cd75c"
PYTHON310_SHA256 = "83a95278567c1f5fea1e886684895c24f467e66f3e9ab3a20321402f54409d14"
#: The approved argv after the executable (§6; confirmed by the IL2-D4 probe).
ARGS = ("--version=4", "task.las")
LIMITS = ProcessLimits(timeout_seconds=600, terminate_grace_seconds=10, stdin_limit_bytes=0,
                       stdout_limit_bytes=16 * 1024 * 1024, stderr_limit_bytes=4 * 1024 * 1024,
                       total_output_limit_bytes=20 * 1024 * 1024)
CLINGO_LIMITS = ProcessLimits(timeout_seconds=60, terminate_grace_seconds=5, stdin_limit_bytes=0,
                              stdout_limit_bytes=1024 * 1024, stderr_limit_bytes=1024 * 1024,
                              total_output_limit_bytes=2 * 1024 * 1024)
#: The fixed import arguments (§6), relative to the import directory.
IMPORT_ARGS = ("import", "ilp-rules", "model.orm.yaml", "hypothesis.las", "--labels", "labels.json",
               "--reported-coverage", "run.json", "--target", "ilasp", "--out", "proposal.json",
               "--actor", "ilp-live", "--requested-at", "2026-01-01T00:00:00Z", "--format", "json")

#: Invocation 1's process result was lost when the script's evaluator step
#: crashed (IL2-F6). Its termination rests on the retained output instead.
RETAINED_TERMINATION = "completed"
PROCESS_LOST = ("not recorded: the script crashed in its clingo step after ILASP exited and before "
                "outcome.json was written (IL2-F6). termination 'completed' rests on the retained "
                "output: the closing %% Total timing block and the hypothesis, which ILASP prints "
                "only when it finishes; 123.685 s is below the 600 s wall clock, and 712 bytes of "
                "stdout and an empty stderr are far below the output limits. The exit status was "
                "not observed.")

SCRATCH_PATH = re.compile(r"(?:/private)?/tmp/claude-\d+/\S*?/scratchpad/il[12]-live")


class Sanitizer:
    def __init__(self, *scratch: Path) -> None:
        self.pairs = [(str(path.resolve()), "<scratch>") for path in scratch]
        self.pairs += [(str(path), "<scratch>") for path in scratch]
        self.pairs += [(str(REPO), "<repo>"), (str(Path.home()), "<home>")]
        self.user = getpass.getuser()

    def __call__(self, text: str) -> str:
        for old, new in self.pairs:
            text = text.replace(old, new)
        # run_bounded_process may mask the user name inside a scratch path
        # before this runs; any scratchpad path collapses to <scratch>.
        text = SCRATCH_PATH.sub("<scratch>", text)
        return text.replace(self.user, "<user>")


def environment(scratch: Path, *, ilasp: bool) -> dict[str, str]:
    home, tmp = scratch / "home", scratch / "tmp"
    home.mkdir(exist_ok=True)
    tmp.mkdir(exist_ok=True)
    env = {"PATH": f"{scratch / 'ilasp'}:/usr/bin:/bin", "HOME": str(home), "USER": getpass.getuser(),
           "TMPDIR": str(tmp), "LANG": "C.UTF-8"}
    if ilasp:
        # IL2-D12 (o): ILASP links a Python 3.10 framework; the shim supplies it.
        # Never for clingo's Python, which PYTHONHOME would break (IL2-F6).
        env |= {"DYLD_FRAMEWORK_PATH": str(scratch / "fw"), "PYTHONHOME": str(scratch / "py310")}
    return env


def termination(result) -> str:
    # ILASP has no timeout option (IL2-F5), so learner-timeout is unreachable.
    if result.status == "timed-out":
        return "wall-clock-kill"
    if result.stdout_truncated or result.stderr_truncated:
        return "output-limit"
    if result.return_code != 0:
        return "rendering-rejected"
    return "completed"


def clingo_coverage(scratch: Path, python: str, work: Path, task: str, hypothesis: str,
                    ids: list[str]) -> list[dict]:
    """Each rule's covered examples, by clingo -- an evaluator that is not GND."""
    background, contexts = split_task(task)
    rows = []
    for index, rule in enumerate(line for line in hypothesis.splitlines() if line):
        covered = []
        for position, context in enumerate(contexts):
            program = work / "cover.lp"
            program.write_text(background + context + rule + "\n", encoding="utf-8")
            result = asyncio.run(run_bounded_process((python, "-m", "clingo", "--outf=2", "cover.lp"),
                                                     cwd=work, env=environment(scratch, ilasp=False),
                                                     limits=CLINGO_LIMITS))
            # python -m clingo exits 0; the clingo binary's codes are 10, 20 and 30.
            report = json.loads(result.stdout) if result.return_code in (0, 10, 20, 30) else {}
            if report.get("Result") not in ("SATISFIABLE", "UNSATISFIABLE"):
                raise SystemExit(f"clingo failed for rule {index}: {result.stderr[-400:]!r}")
            calls = report["Call"]
            witnesses = calls[0].get("Witnesses", []) if calls else []
            if witnesses and "wrong" in witnesses[0]["Value"]:
                covered.append(ids[position])
        rows.append({"clause": index, "covered": covered})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scratch", required=True, type=Path)
    parser.add_argument("--clingo-python", required=True)
    parser.add_argument("--invocation", required=True, type=int)
    parser.add_argument("--complete-retained", action="store_true",
                        help="finish an invocation whose ILASP output is retained but whose "
                             "post-processing failed; ILASP is not run again (IL2-F6)")
    args = parser.parse_args()
    scratch = args.scratch.resolve()
    clean = Sanitizer(scratch, Path(args.clingo_python).parents[2])
    out = OUT / f"invocation-{args.invocation}"
    if args.complete_retained:
        if (out / "outcome.json").exists() or not (out / "raw-stdout.txt").exists():
            raise SystemExit(f"{out}: nothing retained to complete, or already complete")
    elif out.exists():
        raise SystemExit(f"{out} exists: every invocation is retained, never overwritten (IL-R9)")
    binary = scratch / "ilasp" / "ILASP"
    work = scratch / f"work-{args.invocation}"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)

    exported = subprocess.run([sys.executable, "-m", "gnd", "export", "ilp", str(EXAMPLE / "model.orm.yaml"),
                               "--labels", str(EXAMPLE / "labels.json"), "--target", "ilasp",
                               "--out", str(work / "export")], capture_output=True, text=True, check=True)
    index = (work / "export" / "export.json").read_bytes()
    digest = hashlib.sha256(index).hexdigest()
    neutral = json.loads((work / "export" / "neutral.json").read_text(encoding="utf-8"))
    ids = [example["id"] for example in neutral["examples"]]
    task = (work / "export" / "ilasp" / "task.las").read_text(encoding="utf-8")

    argv = (str(binary), *ARGS)
    if args.complete_retained:
        # The learner already ran; its sanitized output is the record. Its
        # process result was never written, so it is recorded as absent.
        result = None
        stdout = (out / "raw-stdout.txt").read_text(encoding="utf-8")
        hypothesis = extract_hypothesis(stdout)
        if hypothesis != (out / "hypothesis.las").read_text(encoding="utf-8"):
            raise SystemExit("the retained hypothesis does not re-extract")
    else:
        result = asyncio.run(run_bounded_process(argv, cwd=work / "export" / "ilasp",
                                                 env=environment(scratch, ilasp=True), limits=LIMITS))
        stdout, stderr = result.stdout.decode("utf-8", "replace"), result.stderr.decode("utf-8", "replace")
        hypothesis = extract_hypothesis(stdout)
        out.mkdir(parents=True)
        (out / "raw-stdout.txt").write_text(clean(stdout), encoding="utf-8")
        (out / "raw-stderr.txt").write_text(clean(stderr), encoding="utf-8")
        (out / "hypothesis.las").write_text(hypothesis, encoding="utf-8")
    outcome = {
        "invocation": args.invocation,
        "run_of_record": args.invocation == 1,
        "termination": termination(result) if result else RETAINED_TERMINATION,
        "import": "none",
        "export_sha256": digest,
        "adapter_version": json.loads(index)["adapter_version"],
        "export_stdout": clean(exported.stdout),
        "ilasp": {"learner": LEARNER, "archive_sha256": ILASP_SHA256,
                  "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
                  "python310_archive_sha256": PYTHON310_SHA256,
                  "licence": "non-commercial research and education; owner ruled this use "
                             "non-commercial research (IL2-D1 (o))",
                  "timeout": None,
                  "argv": [clean(part) for part in argv],
                  "process": json.loads(result.model_dump_json()) if result else None},
        "limits": json.loads(LIMITS.model_dump_json()),
        "import_args": list(IMPORT_ARGS),
        "numbers": {
            "export_sha256": "computed by GND's export",
            "ilasp_output": "printed by ILASP, kept verbatim in raw-stdout.txt",
            "run.json coverage": "independent evaluation (clingo 5.8.2): background + context + rule, per example",
            "import report": "computed by GND's import",
        },
        "reproducibility": "single run, reproducibility not measured",
    }
    if result is None:
        outcome["process_record"] = PROCESS_LOST
    if hypothesis:
        run = {"schema_version": "gnd-ilp-run/1", "learner": LEARNER, "export_sha256": digest,
               "clauses_sha256": hashlib.sha256(hypothesis.encode("utf-8")).hexdigest(),
               "coverage": clingo_coverage(scratch, args.clingo_python, work, task, hypothesis, ids)}
        (out / "run.json").write_text(json.dumps(run, indent=1) + "\n", encoding="utf-8")
        imports = work / "import"
        shutil.copytree(EXAMPLE, imports, ignore=shutil.ignore_patterns("*.py", "README.md"))
        shutil.copy(out / "hypothesis.las", imports / "hypothesis.las")
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
            outcome["import"] = f"refused:{refusal_name(refusal)}"
            (out / "import-stderr.txt").write_text(refusal + "\n", encoding="utf-8")
    (out / "outcome.json").write_text(json.dumps(outcome, indent=1, sort_keys=True) + "\n",
                                      encoding="utf-8")
    print(f"invocation {args.invocation}: termination {outcome['termination']}, import {outcome['import']}")
    return 0


if __name__ == "__main__":
    os.umask(0o022)
    sys.exit(main())
