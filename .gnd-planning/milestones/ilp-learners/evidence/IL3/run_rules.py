"""IL3 live run: one wittgenstein RIPPER run over the refunds feature table (evidence only).

Spec: .gnd-planning/milestones/ilp-learners/notes/phase-IL3-spec.md §6 "Live run",
§12, §13 (IL3-D1 to IL3-D12 approved 2026-10-28). Not a GND command and not a
test lane (IL-R2, plan D3 (a) (o)).

Usage, from the repository root:

    uv run python .gnd-planning/milestones/ilp-learners/evidence/IL3/run_rules.py \
        --scratch SCRATCH (--probe | --invocation N)

SCRATCH holds the IL3-D2 install: ``venv/`` (CPython 3.13.12 with the verified
wheels) and ``wittgenstein-0.3.5/`` (the extracted sdist). ``--probe`` runs the
driver once on the IL3-D8 toy table and writes evidence/IL3/probe/. An invocation
exports ``--target rules``, runs the driver through gnd.process.run_bounded_process,
and writes under evidence/IL3/live/invocation-N/ the raw streams and the process
record first, then the rule set, the learner's run record, the import result and
outcome.json. tests/test_ilp_rules.py T9 replays it.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from live_common import (
    Sanitizer,
    environment,
    export,
    import_outcome,
    run_import,
    termination,
    write_json,
)

from gnd.export.ilp_rules import ADAPTER_VERSION, extract_ruleset
from gnd.process import ProcessLimits, run_bounded_process

HERE = Path(__file__).resolve().parent
DRIVER = HERE / "learn_rules.py"
LIMITS = ProcessLimits(timeout_seconds=600, terminate_grace_seconds=10, stdin_limit_bytes=0,
                       stdout_limit_bytes=16 * 1024 * 1024, stderr_limit_bytes=4 * 1024 * 1024,
                       total_output_limit_bytes=20 * 1024 * 1024)
#: The fixed import arguments (§6), relative to the import directory.
IMPORT_ARGS = ("import", "ilp-rules", "model.orm.yaml", "ruleset.txt", "--labels", "labels.json",
               "--reported-coverage", "run.json", "--target", "rules", "--out", "proposal.json",
               "--actor", "ilp-live", "--requested-at", "2026-01-01T00:00:00Z", "--format", "json")
#: IL3-D8 (o): the toy table, in the IL3-F2 column grammar.
PROBE = {"schema_version": "gnd-ilp-features/1",
         "columns": [{"name": "a__1__2__gt_t_x__1"}, {"name": "b__1__2__gt_t_x__1"}],
         "rows": [{"example": "p1", "label": "pos", "values": [1, 0]},
                  {"example": "p2", "label": "pos", "values": [1, 1]},
                  {"example": "n1", "label": "neg", "values": [0, 1]},
                  {"example": "n2", "label": "neg", "values": [0, 0]}]}
_LEARNER = re.compile(r"learner wittgenstein ([A-Za-z0-9][A-Za-z0-9._+-]{0,63})")
_COVERS = re.compile(r"COVERS (0|[1-9][0-9]{0,2}) (\[.*\])")

__all__ = ["covers", "import_outcome", "read_ruleset", "termination"]


def read_ruleset(stdout: str, ended: str) -> str:
    """The extracted rule set, or "" for a cut-off run (IL5-Q1 (o))."""
    return "" if ended == "output-limit" else extract_ruleset(stdout)


def covers(stdout: str) -> list[list[str]]:
    """The learner's own per-rule coverage, in rule order; a malformed line is not a row."""
    rows: dict[int, list[str]] = {}
    for line in stdout.split("\n"):
        match = _COVERS.fullmatch(line.removesuffix("\r"))
        if match is None:
            continue
        try:
            ids = json.loads(match.group(2))
        except ValueError:
            continue
        if isinstance(ids, list) and all(isinstance(i, str) for i in ids):
            rows.setdefault(int(match.group(1)), ids)
    return [rows[k] for k in range(len(rows)) if k in rows]


def learner(stdout: str) -> dict[str, str]:
    for line in stdout.split("\n"):
        match = _LEARNER.fullmatch(line.removesuffix("\r"))
        if match:
            return {"name": "wittgenstein", "version": match.group(1)}
    return {"name": "wittgenstein", "version": "unreported"}


def drive(scratch: Path, cwd: Path, table: str) -> Any:
    argv = (str(scratch / "venv" / "bin" / "python"), "-I", str(DRIVER), str(scratch / "wittgenstein-0.3.5"),
            table)
    return argv, asyncio.run(run_bounded_process(argv, cwd=cwd, env=environment(scratch), limits=LIMITS))


def probe(scratch: Path, clean: Sanitizer) -> int:
    out = HERE / "probe"
    if out.exists():
        raise SystemExit(f"{out} exists")
    work = scratch / "il3-probe"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir()
    write_json(work / "features.json", PROBE)
    argv, result = drive(scratch, work, "features.json")
    out.mkdir()
    write_json(out / "features.json", PROBE)
    (out / "raw-stdout.txt").write_text(clean(result.stdout.decode("utf-8", "replace")), encoding="utf-8")
    (out / "raw-stderr.txt").write_text(clean(result.stderr.decode("utf-8", "replace")), encoding="utf-8")
    write_json(out / "invocation.json", json.loads(clean(result.model_dump_json())))
    stdout = result.stdout.decode("utf-8", "replace")
    write_json(out / "probe.json", {"argv": [clean(a) for a in argv], "status": result.status,
                                    "learner": learner(stdout), "ruleset": extract_ruleset(stdout),
                                    "covers": covers(stdout)})
    print(f"probe: {result.status}, ruleset {extract_ruleset(stdout)!r}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scratch", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--probe", action="store_true")
    mode.add_argument("--invocation", type=int)
    args = parser.parse_args()
    scratch = args.scratch.resolve()
    clean = Sanitizer(scratch)
    if args.probe:
        return probe(scratch, clean)
    out = HERE / "live" / f"invocation-{args.invocation}"
    if out.exists():
        raise SystemExit(f"{out} exists: every invocation is retained, never overwritten (IL-R9)")
    work = scratch / f"il3-work-{args.invocation}"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir()
    digest, export_stdout = export("rules", work / "export")

    argv, result = drive(scratch, work / "export", "rules/features.json")
    stdout, stderr = result.stdout.decode("utf-8", "replace"), result.stderr.decode("utf-8", "replace")
    process = json.loads(clean(result.model_dump_json()))
    out.mkdir(parents=True)
    # Written before anything else can fail (IL2-F6).
    (out / "raw-stdout.txt").write_text(clean(stdout), encoding="utf-8")
    (out / "raw-stderr.txt").write_text(clean(stderr), encoding="utf-8")
    write_json(out / "invocation.json", process)
    ended = termination(process)
    who = learner(stdout)
    write_json(out / "run-meta.json", {"learner": who, "python": "CPython 3.13.12 (scratch venv)",
                                       "settings": "RIPPER(random_state=0, n_discretize_bins=None)",
                                       "reproducibility": "single run, reproducibility not measured"})
    outcome: dict[str, Any] = {
        "invocation": args.invocation,
        "run_of_record": args.invocation == 1,
        "termination": ended,
        "import": "none",
        "export_sha256": digest,
        "export_stdout": clean(export_stdout),
        "adapter_version": ADAPTER_VERSION,
        "learner": who,
        "process": process,
        "argv": [clean(a) for a in argv],
        "limits": LIMITS.model_dump(),
        "import_args": list(IMPORT_ARGS),
        "licence": "wittgenstein MIT; numpy's CC0-1.0 part accepted (IL3-D3 (o))",
        "numbers": {
            "export_sha256": "computed by GND's export",
            "ruleset": "printed by the learner, kept verbatim in raw-stdout.txt",
            "run.json coverage": "learner predict (wittgenstein Rule.covers), per rule",
            "import report": "computed by GND's import",
        },
        "seeds": {"random_state": 0},
        "reproducibility": "single run, reproducibility not measured",
    }
    if ended == "output-limit":
        outcome["ruleset"] = "not read: the output was cut off (IL5-Q1 (o))"
    ruleset = read_ruleset(stdout, ended)
    if ruleset:
        (out / "ruleset.txt").write_text(ruleset, encoding="utf-8")
        run = {"schema_version": "gnd-ilp-run/1", "learner": who, "export_sha256": digest,
               "clauses_sha256": hashlib.sha256(ruleset.encode("utf-8")).hexdigest(),
               "coverage": [{"clause": k, "covered": ids} for k, ids in enumerate(covers(stdout))]}
        write_json(out / "run.json", run)
        outcome["import_exit"], outcome["import"] = run_import(
            work, out, ("ruleset.txt", "run.json"), IMPORT_ARGS, clean)
    write_json(out / "outcome.json", outcome)
    print(f"invocation {args.invocation}: termination {outcome['termination']}, import {outcome['import']}")
    return 0


if __name__ == "__main__":
    os.umask(0o022)
    sys.exit(main())
