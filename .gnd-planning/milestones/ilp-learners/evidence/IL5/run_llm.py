"""IL5 live run: one real agent proposal over the IK6 refunds prompt (evidence only).

Spec: .gnd-planning/milestones/ilp-learners/notes/phase-IL5-spec.md §6 "Live run",
§12 (IL5-D8 (a) (o): one run with claude, provider terms recorded first). Not a
GND command and not a test lane (IL-R2, plan D3 (a) (o)).

Usage, from the repository root, after the owner has confirmed the provider
terms (provider-terms-confirmed.json beside this file):

    uv run python .gnd-planning/milestones/ilp-learners/evidence/IL5/run_llm.py \
        --scratch SCRATCH --invocation N

SCRATCH holds SWI-Prolog.app (the IL1-D3 install), the independent evaluator
(IL-R4). The agent runs through gnd.agents.invoke_agent in an empty directory
under SCRATCH; SWI runs through gnd.process.run_bounded_process. The script
writes, under evidence/IL5/live/invocation-N/, the prompt, the raw streams and
the invocation record first (IL2-F6), then the answer, the SWI run record, the
import result and outcome.json, with the scratch, repository and home paths and
the user name replaced by placeholders (IL-R10). The import runs from a fixed
working directory with fixed arguments, so tests/test_ilp_llm.py T9 can replay it.
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
from typing import Any

from gnd.agents import AgentAdapterId, invoke_agent
from gnd.export.ilp import refusal_name
from gnd.export.ilp_popper import quote
from gnd.export.ilp_prompt import PROMPT_VERSION, build_prompt, extract_answer, extract_model
from gnd.model import load_model
from gnd.process import ProcessLimits, run_bounded_process

REPO = Path(__file__).resolve().parents[5]
EXAMPLE = REPO / "src" / "gnd" / "examples" / "refunds"
HERE = Path(__file__).resolve().parent
OUT = HERE / "live"
CONFIRMED = HERE / "provider-terms-confirmed.json"
#: IL5-D8 (a) (o).
ADAPTER = AgentAdapterId.claude
TIMEOUT_SECONDS = 600.0
OUTPUT_LIMIT_BYTES = 1024 * 1024
GRACE_SECONDS = 10.0
SWI_LIMITS = ProcessLimits(timeout_seconds=60, terminate_grace_seconds=5, stdin_limit_bytes=0,
                           stdout_limit_bytes=1024 * 1024, stderr_limit_bytes=1024 * 1024,
                           total_output_limit_bytes=2 * 1024 * 1024)
#: The fixed import arguments (§6), relative to the import directory.
IMPORT_ARGS = ("import", "ilp-rules", "model.orm.yaml", "answer.json", "--labels", "labels.json",
               "--reported-coverage", "run.json", "--target", "llm", "--out", "proposal.json",
               "--actor", "ilp-live", "--requested-at", "2026-01-01T00:00:00Z", "--format", "json")
#: SWI spellings of the neutral comparison operators (IL5-D6 (o)).
SWI_OPERATORS = {">": ">", "<": "<", ">=": ">=", "<=": "=<"}
_VERSION = re.compile(r"[A-Za-z0-9][A-Za-z0-9._+-]{0,63}")
_VARIABLE = re.compile(r"[A-Z][A-Za-z0-9_]{0,63}")
_NAME = re.compile(r"[a-z]+(?:-[a-z]+)*")

SCRATCH_PATH = re.compile(r"(?:/private)?/tmp/claude-\d+/\S*?/scratchpad/il[0-9]-live")


class Sanitizer:
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


def swi_environment(scratch: Path) -> dict[str, str]:
    home, tmp = scratch / "home", scratch / "tmp"
    home.mkdir(exist_ok=True)
    tmp.mkdir(exist_ok=True)
    return {"PATH": "/usr/bin:/bin", "HOME": str(home), "USER": getpass.getuser(),
            "TMPDIR": str(tmp), "LANG": "C.UTF-8"}


def termination(invocation: dict[str, Any]) -> str:
    """IL5-D7 (o); neither agent has a timeout of its own, so learner-timeout is unreachable."""
    if invocation["stdout_truncated"] or invocation["stderr_truncated"]:
        return "output-limit"
    if invocation["status"] == "timed-out":
        return "wall-clock-kill"
    if invocation["status"] == "failed":
        return "rendering-rejected"
    return "completed"


def read_answer(stdout: str, ended: str) -> str:
    """The extracted answer, or "" for a cut-off run: what follows the cut is unknown (IL5-Q1 (o))."""
    return "" if ended == "output-limit" else extract_answer(stdout)


def import_outcome(refusal: str) -> str:
    """The clauses reader's refusals name the file ("clauses PATH ...") or a cap: unparsable (§6)."""
    name = "" if refusal.startswith("clauses ") else refusal_name(refusal)
    return f"refused:{name}" if _NAME.fullmatch(name) else "refused:unparsable"


def publishable_answer(answer: str, clean: Sanitizer) -> str:
    """The answer, or "" when it holds a private string: answer.json is bound by digest (IL-R10)."""
    return answer if clean(answer) == answer else ""


def unevaluated_coverage(document: Any) -> list[dict[str, Any]]:
    """Empty rows, one per clause where the shape allows, so GND's own refusal is the one recorded."""
    clauses = document.get("clauses") if isinstance(document, dict) else None
    count = len(clauses) if isinstance(clauses, list) and clauses else 1
    return [{"clause": index, "covered": []} for index in range(count)]


def _term(term: dict[str, Any]) -> str:
    if "var" in term:
        if not isinstance(term["var"], str) or not _VARIABLE.fullmatch(term["var"]):
            raise ValueError(f"not evaluated: variable {term['var']!r}")
        return term["var"]
    value = term["const"]
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return quote(value)


def _literal(literal: dict[str, Any]) -> str:
    if "atom" in literal:
        atom = literal["atom"]
        return f"{atom['predicate']}({', '.join(_term(t) for t in atom['args'])})"
    if "compare" in literal:
        compare = literal["compare"]
        return f"{_term(compare['left'])} {SWI_OPERATORS[compare['operator']]} {_term(compare['right'])}"
    if "not" in literal:
        return f"\\+ {_literal(literal['not'])}"
    raise ValueError(f"no Prolog spelling for {sorted(literal)}")


def prolog_clause(clause: dict[str, Any]) -> str:
    """One clause as Prolog, written by this script, not by GND (IL-R4)."""
    head = clause["head"]
    body = ", ".join(_literal(literal) for literal in clause["body"])
    return f"{head['predicate']}({', '.join(_term(t) for t in head['args'])}) :- {body}."


def comparison_program(neutral: dict[str, Any]) -> str:
    """Arithmetic comparison definitions from the neutral operators (IL5-D6 (o))."""
    return "".join(f"{row['name']}(X, T) :- integer(X), integer(T), X {SWI_OPERATORS[row['operator']]} T.\n"
                   for row in neutral["comparisons"])


def _check(neutral: dict[str, Any], clause: dict[str, Any]) -> None:
    """Only wrong/1 over the export's own predicates reaches SWI; the answer is untrusted (IL-R6)."""
    known = {row["name"] for row in neutral["predicates"]} | {row["name"] for row in neutral["comparisons"]}
    if clause["head"]["predicate"] != "wrong" or len(clause["head"]["args"]) != 1:
        raise ValueError("not evaluated: the head is not wrong/1")
    for literal in clause["body"]:
        if "atom" in literal and literal["atom"]["predicate"] not in known:
            raise ValueError(f"not evaluated: {literal['atom']['predicate']!r} is not in the export")
        if "compare" in literal and literal["compare"]["operator"] not in SWI_OPERATORS:
            raise ValueError("not evaluated: an unknown comparison operator")


def swi_coverage(swipl: Path, popper: Path, neutral: dict[str, Any], document: dict[str, Any]
                 ) -> list[dict[str, Any]]:
    """Each clause's covered examples, by SWI over popper/bk.pl plus cmp.pl -- not GND."""
    programs = []
    for clause in document["clauses"]:
        _check(neutral, clause)
        programs.append(prolog_clause(clause))
    scratch = popper.parent
    work = popper / "swi"
    work.mkdir(exist_ok=True)
    shutil.copy(popper / "popper" / "bk.pl", work / "bk.pl")
    (work / "cmp.pl").write_text(comparison_program(neutral), encoding="utf-8")
    ids = [example["id"] for example in neutral["examples"]]
    listed = ",".join(quote(i) for i in ids)
    rows = []
    for index, program in enumerate(programs):
        (work / "clause.pl").write_text(program + "\n", encoding="utf-8")
        (work / "cover.pl").write_text(
            ":- initialization(main, main).\n:- style_check(-singleton).\n"
            ":- consult('bk.pl').\n:- consult('cmp.pl').\n:- consult('clause.pl').\n"
            f"main :- forall(nth0(I, [{listed}], E), (catch(wrong(E), _, fail) -> (write(I), nl) ; true)).\n",
            encoding="utf-8")
        result = asyncio.run(run_bounded_process((str(swipl), "-q", "cover.pl"), cwd=work,
                                                 env=swi_environment(scratch), limits=SWI_LIMITS))
        if result.return_code != 0:
            raise ValueError(f"not evaluated: SWI exited {result.return_code} on clause {index}")
        covered = sorted({int(line) for line in result.stdout.decode().split()})
        rows.append({"clause": index, "covered": [ids[i] for i in covered]})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scratch", required=True, type=Path)
    parser.add_argument("--invocation", required=True, type=int)
    args = parser.parse_args()
    if not CONFIRMED.is_file():
        raise SystemExit(f"{CONFIRMED.name} is missing: the owner has not confirmed the provider "
                         "terms (provider-terms.md, IL5-D8 (o))")
    scratch = args.scratch.resolve()
    clean = Sanitizer(scratch)
    out = OUT / f"invocation-{args.invocation}"
    if out.exists():
        raise SystemExit(f"{out} exists: every invocation is retained, never overwritten (IL-R9)")
    swipl = scratch / "SWI-Prolog.app" / "Contents" / "MacOS" / "swipl"
    work = scratch / f"il5-work-{args.invocation}"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)

    exports = {}
    for target in ("neutral", "popper"):
        exports[target] = subprocess.run(
            [sys.executable, "-m", "gnd", "export", "ilp", str(EXAMPLE / "model.orm.yaml"), "--labels",
             str(EXAMPLE / "labels.json"), "--target", target, "--out", str(work / target)],
            capture_output=True, text=True, check=True)
    digest = hashlib.sha256((work / "neutral" / "export.json").read_bytes()).hexdigest()
    neutral = json.loads((work / "neutral" / "neutral.json").read_text(encoding="utf-8"))
    assert (work / "popper" / "neutral.json").read_bytes() == (work / "neutral" / "neutral.json").read_bytes()
    prompt = build_prompt(neutral, load_model(EXAMPLE / "model.orm.yaml"))
    prompt_sha = hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    agent_cwd = work / "agent"
    agent_cwd.mkdir()
    out.mkdir(parents=True)
    (out / "prompt.txt").write_text(prompt, encoding="utf-8")
    result = asyncio.run(invoke_agent(ADAPTER, prompt=prompt, cwd=agent_cwd, timeout_seconds=TIMEOUT_SECONDS,
                                      output_limit_bytes=OUTPUT_LIMIT_BYTES,
                                      terminate_grace_seconds=GRACE_SECONDS))
    stdout, stderr = result.stdout.decode("utf-8", "replace"), result.stderr.decode("utf-8", "replace")
    invocation = json.loads(clean(result.model_dump_json()))
    # Written before anything else can fail (IL2-F6).
    (out / "raw-stdout.txt").write_text(clean(stdout), encoding="utf-8")
    (out / "raw-stderr.txt").write_text(clean(stderr), encoding="utf-8")
    (out / "invocation.json").write_text(json.dumps(invocation, indent=1, sort_keys=True) + "\n",
                                         encoding="utf-8")
    written = sorted(clean(str(path.relative_to(agent_cwd))) for path in agent_cwd.rglob("*"))
    version = _VERSION.match(result.version.strip())
    learner = {"name": ADAPTER.value, "version": version.group(0) if version else "unreported"}
    ended = termination(invocation)
    extracted = read_answer(stdout, ended)
    answer = publishable_answer(extracted, clean)
    model = extract_model(stdout)
    (out / "run-meta.json").write_text(json.dumps({
        "model_reported": model, "model_note": "the agent's own model: line, unverified (IL5-D4 (o))",
        "cli_version": clean(result.version), "learner": learner,
        "files_written_by_agent": written, "files_note": "listed and discarded, never imported",
        "reproducibility": "single run, not repeatable"}, indent=1, sort_keys=True) + "\n", encoding="utf-8")

    outcome = {
        "invocation": args.invocation,
        "run_of_record": args.invocation == 1,
        "termination": ended,
        "import": "none",
        "export_sha256": digest,
        "export_stdout": {target: clean(done.stdout) for target, done in exports.items()},
        "prompt_sha256": prompt_sha,
        "prompt_version": PROMPT_VERSION,
        "agent": {"adapter": ADAPTER.value, "learner": learner, "model_reported": model,
                  "invocation": invocation, "files_written_by_agent": written},
        "limits": {"timeout_seconds": TIMEOUT_SECONDS, "terminate_grace_seconds": GRACE_SECONDS,
                   "stdin_limit_bytes": 0, "stdout_limit_bytes": OUTPUT_LIMIT_BYTES,
                   "stderr_limit_bytes": OUTPUT_LIMIT_BYTES,
                   "total_output_limit_bytes": 2 * OUTPUT_LIMIT_BYTES,
                   "note": "invoke_agent derives these; its version probe spends at most 5 s of the timeout"},
        "import_args": list(IMPORT_ARGS),
        "numbers": {
            "export_sha256": "computed by GND's export",
            "prompt": "built by gnd.export.ilp_prompt, kept in prompt.txt",
            "agent_output": "printed by the agent, kept verbatim in raw-stdout.txt",
            "run.json coverage": "independent evaluation (SWI-Prolog): popper/bk.pl + cmp.pl + clause, per example",
            "import report": "computed by GND's import",
        },
        "reproducibility": "single run, not repeatable",
    }
    if ended == "output-limit":
        outcome["answer"] = "not read: the output was cut off (IL5-Q1 (o))"
    if extracted and not answer:
        outcome["answer"] = "withheld: the block holds a private string (IL-R10)"
    if answer:
        (out / "answer.json").write_text(answer, encoding="utf-8")
        answer_sha = hashlib.sha256(answer.encode("utf-8")).hexdigest()
        document = None
        try:
            document = json.loads(answer)
            coverage = swi_coverage(swipl, work / "popper", neutral, document)
            outcome["swi"] = "evaluated"
        except (ValueError, TypeError, KeyError, AttributeError) as error:
            # Not evaluable here: GND's import still decides, from its own readers first.
            coverage = unevaluated_coverage(document)
            outcome["swi"] = f"not evaluated: {type(error).__name__}"
        run = {"schema_version": "gnd-ilp-run/1", "learner": learner, "export_sha256": digest,
               "clauses_sha256": answer_sha, "coverage": coverage}
        (out / "run.json").write_text(json.dumps(run, indent=1) + "\n", encoding="utf-8")
        imports = work / "import"
        shutil.copytree(EXAMPLE, imports, ignore=shutil.ignore_patterns("*.py", "README.md"))
        shutil.copy(out / "answer.json", imports / "answer.json")
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
            outcome["import"] = import_outcome(refusal)
            (out / "import-stderr.txt").write_text(refusal + "\n", encoding="utf-8")
    (out / "outcome.json").write_text(json.dumps(outcome, indent=1, sort_keys=True) + "\n",
                                      encoding="utf-8")
    print(f"invocation {args.invocation}: termination {outcome['termination']}, import {outcome['import']}")
    return 0


if __name__ == "__main__":
    os.umask(0o022)
    sys.exit(main())
