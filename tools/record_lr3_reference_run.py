"""Record LR3's one live reading run over the literature reference set.

Owner rulings (milestone literature-reading-reference): producer Claude Sonnet
through the owner's Claude Code login ("Claude CLI login"), a USD 50 ceiling
("sonnet 50$"). This tool is not part of any gate: it spends paid calls. The
gates replay the folder it writes with zero producer calls.

    uv run python tools/record_lr3_reference_run.py --out DIR

writes DIR/run (the literature-reading-run/2 folder), DIR/run-record.json and
DIR/score.json. Nothing is written into the package; copying the result in is
a separate, reviewed step.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from gnd.artifacts import canonical_json_bytes
from gnd.examples.literature import reading, reference_set

MODEL_ID = "claude-sonnet-5-5"
CEILING_USD = 50.0
PER_CALL_USD = 1.0
CALL_SECONDS = 300
PROMPT = """You read one section of a scientific paper and report the facts it states, in a fixed vocabulary.

Fact types (report only these):
{fact_types}

Rules:
- Report a fact only if this section itself states it. Do not use outside knowledge.
- Write each value as this section writes the name, without adding or changing words.
- A work is named by the identifier the section gives for it (for example an arXiv identifier).
- If the section states none of these facts, report no facts.

Section {section} of source {source}:
<section>
{text}
</section>
"""


def _vocabulary(model: dict) -> list[dict]:
    """The fact types a producer may report: the model's asserted ones, never a derived one."""
    return [row for row in model["fact_types"] if row.get("derivation") is None]


def _schema(fact_types: list[dict]) -> dict:
    properties = {}
    for row in fact_types:
        roles = [role["role_name"] for role in row["roles"]]
        properties[row["id"]] = {"type": "array", "items": {
            "type": "object", "properties": {name: {"type": "string"} for name in roles},
            "required": roles, "additionalProperties": False}}
    return {"type": "object", "properties": {"facts": {"type": "object", "properties": properties,
                                                       "additionalProperties": False}},
            "required": ["facts"], "additionalProperties": False}


def _fact_type_lines(fact_types: list[dict]) -> str:
    return "\n".join(f"- {row['id']}: \"{row['reading']}\", roles " + ", ".join(
        role["role_name"] for role in row["roles"]) for row in fact_types)


class SpendError(RuntimeError):
    pass


class ClaudeCliProducer:
    """A reading producer that asks Claude Sonnet through the ``claude`` CLI, one call per section."""

    def __init__(self, model: dict, *, command: tuple[str, ...] = ("claude",), ceiling: float = CEILING_USD):
        self.fact_types = _vocabulary(model)
        self.roles = {row["id"]: {role["role_name"] for role in row["roles"]} for row in self.fact_types}
        self.schema = _schema(self.fact_types)
        self.template = PROMPT.replace("{fact_types}", _fact_type_lines(self.fact_types))
        self.command, self.ceiling = command, ceiling
        self.spent, self.calls, self.models = 0.0, [], set()

    def _ask(self, prompt: str) -> dict:
        if self.spent + PER_CALL_USD > self.ceiling:
            raise SpendError(f"the next call could pass the USD {self.ceiling} ceiling (spent {self.spent:.4f})")
        argv = [*self.command, "-p", "--model", MODEL_ID, "--safe-mode", "--tools", "",
                "--no-session-persistence", "--output-format", "json", "--max-budget-usd", str(PER_CALL_USD),
                "--json-schema", json.dumps(self.schema)]
        with tempfile.TemporaryDirectory(prefix="lr3-producer-") as empty:
            done = subprocess.run(argv, input=prompt, capture_output=True, text=True, cwd=empty,
                                  timeout=CALL_SECONDS, check=False)
        if done.returncode != 0:
            raise RuntimeError(f"claude exited {done.returncode}: {done.stderr[-500:]}")
        result = json.loads(done.stdout)
        self.spent += float(result.get("total_cost_usd") or 0.0)
        models = set(result.get("modelUsage") or {})
        self.models |= models
        if result.get("is_error") or result.get("subtype") != "success":
            raise RuntimeError(f"claude returned {result.get('subtype')!r}")
        if not models <= {MODEL_ID}:
            raise RuntimeError(f"claude used models {sorted(models)}, not {MODEL_ID}")
        output = result.get("structured_output")
        if not isinstance(output, dict) or not isinstance(output.get("facts"), dict):
            raise RuntimeError("claude returned no structured facts")
        return output

    def produce(self, call: reading.ProducerCall) -> dict:
        prompt = (self.template.replace("{section}", call.section).replace("{source}", call.source)
                  .replace("{text}", call.excerpt.decode("utf-8")))
        output = self._ask(prompt)
        facts = {}
        for fact_type, rows in output["facts"].items():
            names = self.roles.get(fact_type)
            if names is None or not isinstance(rows, list):
                continue
            kept = [row for row in rows if isinstance(row, dict) and set(row) == names
                    and all(isinstance(value, str) and value.strip() for value in row.values())]
            if kept:
                facts[fact_type] = kept
        self.calls.append({"stage": call.stage, "section": call.section, "excerpt_sha256": call.excerpt_sha256,
                           "spent_usd": round(self.spent, 6)})
        if facts:
            return {"outcome": "accepted", "facts": facts, "proposal_keys": []}
        return {"outcome": "empty", "facts": {}, "proposal_keys": []}


def record(out: Path, root: Path = reference_set.ROOT, *, command: tuple[str, ...] = ("claude",)) -> dict:
    out.mkdir(parents=True, exist_ok=False)
    model = json.loads((root / reference_set.MODEL).read_bytes())
    producer = ClaudeCliProducer(model, command=command)
    budget = sum((root / f"{source}.txt").stat().st_size
                 for source in (row["id"] for row in json.loads((root / "roster.json").read_bytes())["sources"]))
    report = reading.run(out / "run", fixture=root, producer=producer, budget=budget)
    version = subprocess.run([*command, "--version"], capture_output=True, text=True, check=False).stdout.strip()
    run_record = {
        "format": "literature-reference-run-record/1",
        "producer": {"transport": "claude CLI, the owner's login", "cli_version": version,
                     "model": MODEL_ID, "models_seen": sorted(producer.models),
                     "flags": ["--safe-mode", "--tools", "", "--no-session-persistence",
                               "--output-format", "json", "--max-budget-usd", str(PER_CALL_USD), "--json-schema"]},
        "prompt_template": producer.template,
        "prompt_template_sha256": hashlib.sha256(producer.template.encode("utf-8")).hexdigest(),
        "schema": producer.schema,
        "budget": {"ceiling_usd": CEILING_USD, "spent_usd": round(producer.spent, 6), "calls": len(producer.calls)},
        "reading": {"budget_bytes": budget, "producer_calls": report["producer_calls"], "stop": report["stop"],
                    "read_denominator": report["read_denominator"]},
        "evidence_sha256": report["evidence_sha256"],
        "calls": producer.calls,
    }
    (out / "run-record.json").write_bytes(canonical_json_bytes(run_record))
    (out / "score.json").write_bytes(canonical_json_bytes(reference_set.score(out / "run", root)))
    return run_record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=reference_set.ROOT)
    args = parser.parse_args(argv)
    summary = record(args.out, args.root)
    print(json.dumps(summary["budget"]), json.dumps(summary["reading"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
