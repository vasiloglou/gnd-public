"""How expected/*.txt were derived (run from the corpus directory with PYTHONPATH set to the
source of main 12daa5b7: it needs the plain renderer as it was, because ROF1 turns
``_print_report`` into an adapter over the new row renderer).

For each case: run the JSON route (today's code, main 12daa5b7), keep the
report under reports/, then render the report's rows with the PLAIN route's
own renderer (gnd.output._print_report over a namespace rebuilt from the
rows, with the attributes that renderer reads) and add the layout's header / issue / OK lines. Nothing here calls the
projected renderer this phase adds.
"""

from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from gnd import output

CASES = {
    "redacted-fail": ["check", "models/contacts-redacted.orm.yaml", "populations/contacts-fail.pop.yaml"],
    "redacted-fail-unredacted": ["check", "models/contacts-redacted.orm.yaml", "populations/contacts-fail.pop.yaml", "--unredacted"],
    "redacted-visible-canary": ["check", "models/directory-redacted.orm.yaml", "populations/directory-fail.pop.yaml"],
    "redacted-pass": ["check", "models/contacts-redacted.orm.yaml", "populations/contacts-pass.pop.yaml"],
    "redacted-rule-ids": ["check", "models/contacts-redacted.orm.yaml", "populations/contacts-pass.pop.yaml", "--rule-ids"],
    "redacted-ill-formed": ["check", "models/contacts-redacted.orm.yaml", "populations/contacts-ill-formed.pop.yaml"],
    "temporal-pass": ["check", "models/service-temporal.orm.yaml", "populations/service-pass.pop.yaml"],
    "temporal-advisory": ["check", "models/service-temporal.orm.yaml", "populations/service-advisory.pop.yaml"],
    "temporal-derivation": ["check", "models/terms-temporal.orm.yaml", "populations/terms-unchecked.pop.yaml"],
    "validate-redacted": ["validate", "models/contacts-redacted.orm.yaml"],
    "validate-redacted-unredacted": ["validate", "models/contacts-redacted.orm.yaml", "--unredacted"],
    "validate-temporal": ["validate", "models/service-temporal.orm.yaml"],
    "validate-invalid": ["validate", "models/contacts-invalid.orm.yaml"],
}


def header(report: dict) -> list[str]:
    meta = report.get("redaction") or {}
    coords = sorted(
        {f"{d['fact_type']}.{r}" for d in meta.get("declarations", []) for r in d.get("roles", [])}
    )
    return [f"REDACTION {meta['mode']}: {', '.join(coords)}"] if coords else []


def body(report: dict, model: str) -> list[str]:
    lines = [f"WARNING at {w['path']}: {w['message']} [{w['rule_id']}]" for w in report["warnings"]]
    if report["issues"]:
        return lines + [f"ERROR at {i['path']}: {i['message']} [{i['rule_id']}]" for i in report["issues"]]
    if report["command"] == "validate":
        return lines + [f"OK: {model} is a valid GND ORM model"]
    ns = SimpleNamespace
    rebuilt = ns(
        verdicts=[ns(**v) for v in report["verdicts"]],
        derivations=[
            ns(**{**v, "findings": [ns(**f) for f in v["findings"]]})
            for v in report["derivations"] or []
        ],
        coverage={k: ns(**v) for k, v in report["coverage"].items()},
        counts=lambda: report["counts"],
    )
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        output._print_report(rebuilt)
    return lines + buffer.getvalue().splitlines()


def main() -> None:
    exits = {}
    Path("expected/reports").mkdir(exist_ok=True)
    for case, argv in CASES.items():
        done = subprocess.run(
            [sys.executable, "-m", "gnd", *argv, "--format", "json"],
            capture_output=True, text=True, stdin=subprocess.DEVNULL, check=False,
        )
        report = json.loads(done.stdout)
        assert report["exit_code"] == done.returncode, case
        Path(f"expected/reports/{case}.json").write_text(done.stdout)
        model = argv[1]
        lines = header(report) + body(report, model)
        Path(f"expected/{case}.txt").write_text("\n".join(lines) + "\n")
        exits[case] = {"argv": argv, "exit": done.returncode, "schema_version": report["schema_version"]}
    Path("expected/exits.json").write_text(json.dumps(exits, indent=2) + "\n")


main()
