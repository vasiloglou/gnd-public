"""IL4 live run: one AMIE 4.0.0 run over the staffing fixture's triples (evidence only).

Spec: .gnd-planning/milestones/ilp-learners/notes/phase-IL4-spec.md §6 "Live run",
§12, §13 (IL4-D1 to IL4-D13 approved 2026-10-28). Not a GND command and not a
test lane (IL-R2, plan D3 (a) (o)).

Usage, from the repository root:

    uv run python .gnd-planning/milestones/ilp-learners/evidence/IL4/run_amie.py \\
        --scratch SCRATCH (--probe | --invocation N)

SCRATCH holds the IL4-D2 download, ``amie4.0.0.jar``, checked against its size and
SHA-256 before every run. The JVM is the installed Homebrew OpenJDK, read only.
``--probe`` runs AMIE once on the IL4-D10 toy TSV and writes evidence/IL4/probe/.
An invocation exports ``--target amie`` over the IL4-D4 fixture, runs AMIE through
gnd.process.run_bounded_process, and writes under evidence/IL4/live/invocation-N/
the raw streams and the process record first, then the exported triples, the rule
lines, the run record, the import result and outcome.json. tests/test_ilp_amie.py
T9 replays it.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from live_common import (
    REPO,
    Sanitizer,
    environment,
    import_outcome,
    run_import,
    termination,
    write_json,
)

from gnd.export.ilp_amie import ADAPTER_VERSION, extract_rules
from gnd.process import ProcessLimits, run_bounded_process

HERE = Path(__file__).resolve().parent
FIXTURE = REPO / "tests" / "fixtures" / "ilp_learners" / "il4"
JAVA = Path("/opt/homebrew/bin/java")
JAVA_HOME = Path("/opt/homebrew/opt/openjdk")
JAR = "amie4.0.0.jar"
JAR_BYTES = 96_104_317
JAR_SHA256 = "bbf65ef5b54f896a7c6d05e3faeaf5b58262e3828e61ae6dc3f3c71c932b8485"
#: Each invocation's AMIE settings. 1, IL4-D11 (o): no -const, -mins 1, defaults
#: otherwise. 2, IL6-D6 (o): the same plus standard confidence, kept at 1 (IL4-Q4).
SETTINGS = {1: ("-maxad", "3", "-mins", "1"),
            2: ("-maxad", "3", "-mins", "1", "-enstd", "-minc", "1")}
LIMITS = ProcessLimits(timeout_seconds=600, terminate_grace_seconds=10, stdin_limit_bytes=0,
                       stdout_limit_bytes=16 * 1024 * 1024, stderr_limit_bytes=4 * 1024 * 1024,
                       total_output_limit_bytes=20 * 1024 * 1024)
#: The fixed import arguments (§6), relative to the import directory.
IMPORT_ARGS = ("import", "mined-rules", "model.orm.yaml", "rules.txt", "--population", "population.yaml",
               "--reported", "reported.json", "--target", "amie", "--out", "proposal.json",
               "--actor", "ilp-live", "--requested-at", "2026-01-01T00:00:00Z", "--format", "json")
#: IL4-D10 (o): r and s agree on both facts, so r => s and s => r hold.
PROBE = "a:1\tr\ta:2\na:2\tr\ta:3\na:1\ts\ta:2\na:2\ts\ta:3\n"
#: The licence line as outcome.json records it.
LICENCE = ("AMIE CC-BY-4.0 and its Javatools CC-BY-3.0, accepted (IL4-D3 (o)); attribution: "
           "AMIE by the DIG team, Telecom Paris (github.com/dig-team/AMIE); OpenJDK GPL-2.0 "
           "with the Classpath Exception, installed, used read only")
#: AMIE prints no version; this is the verified release asset's (IL4-D2 (o)).
LEARNER = {"name": "amie", "version": "4.0.0"}

__all__ = ["IMPORT_ARGS", "LEARNER", "LICENCE", "LIMITS", "SETTINGS", "import_outcome", "java_argv",
           "java_environment", "learner", "read_rules", "recorded_argv", "termination"]


def read_rules(stdout: str, ended: str) -> str:
    """The extracted rule lines, or "" for a cut-off run (IL5-Q1 (o))."""
    return "" if ended == "output-limit" else extract_rules(stdout)


def learner(stdout: str) -> dict[str, str]:
    """AMIE's stdout names no version, so the record names the verified asset's."""
    del stdout
    return dict(LEARNER)


def java_argv(jar: Path, invocation: int) -> list[str]:
    return [str(JAVA), "-Xmx2G", "-jar", str(jar), *SETTINGS[invocation]]


def recorded_argv(invocation: int) -> list[str]:
    """The argv as outcome.json records it, the scratch placeholder substituted."""
    return [*java_argv(Path(f"<scratch>/{JAR}"), invocation), "amie/facts.tsv"]


def java_environment(scratch: Path) -> dict[str, str]:
    return {**environment(scratch), "JAVA_HOME": str(JAVA_HOME)}


def verified_jar(scratch: Path) -> Path:
    jar = scratch / JAR
    data = jar.read_bytes()
    if len(data) != JAR_BYTES or hashlib.sha256(data).hexdigest() != JAR_SHA256:
        raise SystemExit(f"{jar} is not the IL4-D2 download")
    return jar


def jvm_version(scratch: Path) -> str:
    done = subprocess.run([str(JAVA), "-version"], env=java_environment(scratch), capture_output=True,
                          text=True, check=True)
    return done.stderr.splitlines()[0]


def mine(scratch: Path, cwd: Path, tsv: str, invocation: int) -> tuple[list[str], Any]:
    argv = [*java_argv(verified_jar(scratch), invocation), tsv]
    return argv, asyncio.run(run_bounded_process(argv, cwd=cwd, env=java_environment(scratch),
                                                 limits=LIMITS))


def probe(scratch: Path, clean: Sanitizer) -> int:
    out = HERE / "probe"
    if out.exists():
        raise SystemExit(f"{out} exists")
    work = scratch / "il4-probe"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir()
    (work / "toy.tsv").write_text(PROBE, encoding="utf-8")
    argv, result = mine(scratch, work, "toy.tsv", 1)
    usage = subprocess.run([*java_argv(verified_jar(scratch), 1)[:4], "-h"], cwd=work,
                           env=java_environment(scratch), capture_output=True, text=True, check=False)
    out.mkdir()
    (out / "toy.tsv").write_text(PROBE, encoding="utf-8")
    (out / "raw-stdout.txt").write_text(clean(result.stdout.decode("utf-8", "replace")), encoding="utf-8")
    (out / "raw-stderr.txt").write_text(clean(result.stderr.decode("utf-8", "replace")), encoding="utf-8")
    (out / "help.txt").write_text(clean(usage.stdout + usage.stderr), encoding="utf-8")
    write_json(out / "invocation.json", json.loads(clean(result.model_dump_json())))
    stdout = result.stdout.decode("utf-8", "replace")
    write_json(out / "probe.json", {"argv": [clean(a) for a in argv], "status": result.status,
                                    "help_exit": usage.returncode, "jvm": jvm_version(scratch),
                                    "rules": extract_rules(stdout)})
    print(f"probe: {result.status}, rules {extract_rules(stdout)!r}")
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
    if args.invocation not in SETTINGS:
        raise SystemExit(f"invocation {args.invocation} has no owner-ruled settings (IL-R9)")
    if out.exists():
        raise SystemExit(f"{out} exists: every invocation is retained, never overwritten (IL-R9)")
    work = scratch / f"il4-work-{args.invocation}"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir()
    population = FIXTURE / "population.yaml"
    exported = subprocess.run(
        [sys.executable, "-m", "gnd", "export", "ilp", str(FIXTURE / "model.orm.yaml"), "--population",
         str(population), "--target", "amie", "--out", str(work / "export")],
        capture_output=True, text=True, check=True)
    digest = hashlib.sha256((work / "export" / "export.json").read_bytes()).hexdigest()
    jvm = jvm_version(scratch)

    argv, result = mine(scratch, work / "export", "amie/facts.tsv", args.invocation)
    stdout, stderr = result.stdout.decode("utf-8", "replace"), result.stderr.decode("utf-8", "replace")
    process = json.loads(clean(result.model_dump_json()))
    out.mkdir(parents=True)
    # Written before anything else can fail (IL2-F6).
    (out / "raw-stdout.txt").write_text(clean(stdout), encoding="utf-8")
    (out / "raw-stderr.txt").write_text(clean(stderr), encoding="utf-8")
    write_json(out / "invocation.json", process)
    shutil.copy(work / "export" / "amie" / "facts.tsv", out / "facts.tsv")
    ended = termination(process)
    outcome: dict[str, Any] = {
        "invocation": args.invocation,
        "run_of_record": args.invocation == 1,
        "termination": ended,
        "import": "none",
        "export_sha256": digest,
        "export_stdout": clean(exported.stdout),
        "population_sha256": hashlib.sha256(population.read_bytes()).hexdigest(),
        "adapter_version": ADAPTER_VERSION,
        "learner": learner(stdout),
        "jar_sha256": JAR_SHA256,
        "jvm": jvm,
        "process": process,
        "argv": [clean(a) for a in argv],
        "limits": LIMITS.model_dump(),
        "import_args": list(IMPORT_ARGS),
        "licence": LICENCE,
        "numbers": {
            "export_sha256": "computed by GND's export",
            "rules.txt": "printed by AMIE, kept verbatim in raw-stdout.txt",
            "Support per rule": "printed by AMIE in each rule line (the learner's claim, IL-R4)",
            "import report": "computed by GND's import",
        },
        "seeds": "none: AMIE takes no seed",
        "threads": "AMIE's default, all cores (its stdout names the count)",
        "reproducibility": "single run, reproducibility not measured",
    }
    if ended == "output-limit":
        outcome["rules"] = "not read: the output was cut off (IL5-Q1 (o))"
    rules = read_rules(stdout, ended)
    if rules:
        (out / "rules.txt").write_text(rules, encoding="utf-8")
        write_json(out / "reported.json", {
            "schema_version": "gnd-mined-run/1", "learner": learner(stdout),
            "rules_sha256": hashlib.sha256(rules.encode("utf-8")).hexdigest(),
            "population_sha256": outcome["population_sha256"],
            # ILC-D3 (o): the facts AMIE read, retained beside the record.
            "facts_sha256": hashlib.sha256((out / "facts.tsv").read_bytes()).hexdigest()})
        outcome["import_exit"], outcome["import"] = run_import(
            work, out, ("rules.txt", "reported.json"), IMPORT_ARGS, clean, source=FIXTURE,
            ignore=("expected", "rules.json"))
    write_json(out / "outcome.json", outcome)
    print(f"invocation {args.invocation}: termination {outcome['termination']}, import {outcome['import']}")
    return 0


if __name__ == "__main__":
    os.umask(0o022)
    sys.exit(main())
