"""How expected/*.txt were derived.

Run from the corpus directory with PYTHONPATH set to the source of the ROF2 base
(branch claude/plan-report-output-fidelity-6d5b5d at e1fb6a18 or f1a57836, whose
src/gnd is identical): it needs the plain renderers as they were, because ROF2
turns ``_print_transition`` into an adapter over a new row renderer.

For each case: run the JSON route (the base code), keep the report under
reports/, then render the report's rows with the PLAIN route's own renderers:
``gnd.output._print_transition`` over namespaces rebuilt from the rows for a
walk, ``gnd.output.render_check_rows`` (ROF1's plain check renderer) for the
check layout,
``gnd.output._print_admission_text`` for the admission trailer, and the
verify route's extraction line as ``_cmd_verify`` spells it. The header,
warning and issue lines follow the spec's section 6 order. The reason suffix
rule (ROF1-O1, extended to walk lines by ROF2 D3) is applied to each row's
message before rendering; no row in this corpus carries a reason code, so it
changes nothing here. Nothing here calls code ROF2 adds.
"""

from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace as ns

from gnd import output

PRE = ["--pre", "populations/accounts-start.pop.yaml"]
ACCOUNTS = "models/accounts-redacted.orm.yaml"
CASES = {
    "transition-plan": ["check", ACCOUNTS, *PRE, "--steps", "steps/add-email.steps.json"],
    "transition-plan-unredacted": ["check", ACCOUNTS, *PRE, "--steps", "steps/add-email.steps.json", "--unredacted"],
    "transition-full": ["check", ACCOUNTS, *PRE, "--steps", "steps/add-email.steps.json", "--post", "populations/accounts-end-missing.pop.yaml"],
    "transition-full-unredacted": ["check", ACCOUNTS, *PRE, "--steps", "steps/add-email.steps.json", "--post", "populations/accounts-end-missing.pop.yaml", "--unredacted"],
    "transition-step-fail": ["check", ACCOUNTS, *PRE, "--steps", "steps/add-second-email.steps.json"],
    "transition-precondition": ["check", ACCOUNTS, "--pre", "populations/accounts-fail.pop.yaml", "--steps", "steps/add-nickname-unregistered.steps.json"],
    "transition-refused": ["check", ACCOUNTS, *PRE, "--steps", "steps/add-email-stale-digest.steps.json"],
    "transition-temporal": ["check", "models/service-temporal.orm.yaml", "--pre", "populations/service-start.pop.yaml", "--steps", "steps/set-window.steps.json"],
    "transition-derived": ["check", "models/dynamic.orm.yaml", "--pre", "populations/pre-open.pop.yaml", "--steps", "steps/ticket.steps.json", "--post", "populations/post-resolved.pop.yaml"],
    "admission": ["check", ACCOUNTS, "populations/accounts-fail.pop.yaml", "--admission"],
    "admission-unredacted": ["check", ACCOUNTS, "populations/accounts-fail.pop.yaml", "--admission", "--unredacted"],
    "verify": ["verify", ACCOUNTS, "populations/accounts-fail.pop.yaml", "--no-extraction"],
    "verify-unredacted": ["verify", ACCOUNTS, "populations/accounts-fail.pop.yaml", "--no-extraction", "--unredacted"],
    "verify-refused": ["verify", ACCOUNTS, "populations/accounts-ill-formed.pop.yaml", "--no-extraction"],
}


def header(report: dict) -> list[str]:
    meta = report.get("redaction") or {}
    coords = sorted(
        {f"{d['fact_type']}.{r}" for d in meta.get("declarations", []) for r in d.get("roles", [])}
    )
    return [f"REDACTION {meta['mode']}: {', '.join(coords)}"] if coords else []


def with_reason(row: dict) -> dict:
    code = row.get("reason_code")
    if code and code not in row["message"]:
        return {**row, "message": f"{row['message']} [reason: {code}]"}
    return row


def snapshot(block: dict | None) -> ns:
    return ns(verdicts=[ns(**with_reason(v)) for v in (block or {}).get("verdicts") or []])


def rows(values) -> list[ns]:
    return [ns(**with_reason(v)) for v in values or []]


def printed(function, *args, **kwargs) -> list[str]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        function(*args, **kwargs)
    return buffer.getvalue().splitlines()


def check_layout(report: dict) -> list[str]:
    # The plain route's check renderer at the base (ROF1 made ``_print_report`` an
    # adapter over it); called without ``show_reason`` because ``with_reason``
    # has already applied the suffix rule to the messages.
    return output.render_check_rows(
        {
            "verdicts": [with_reason(v) for v in report["verdicts"]],
            "derivations": [with_reason(v) for v in report["derivations"] or []],
            "counts": report["counts"],
            "coverage": report["coverage"],
        }
    )


def walk_layout(report: dict) -> list[str]:
    block = report["transition"]
    walk = ns(
        pre_snapshot=snapshot(block["pre_snapshot"]),
        pre_snapshot_verdicts=rows(block["pre_snapshot_verdicts"]),
        steps=[
            ns(
                index=step["index"],
                operation=step["operation"],
                derived_changes=step.get("derived_changes") or [],
                verdicts=rows(step["verdicts"]),
                intermediate=snapshot(step["intermediate"]),
            )
            for step in block["steps"]
        ],
        frame_grading=[ns(**g) for g in block["frame_grading"] or []],
        frame_verdicts=rows(block["frame_verdicts"]),
        post_snapshot=snapshot(block["post_snapshot"]),
    )
    computed = block["computed_post"] if report["post"] == "computed" else None
    return printed(output._print_transition, walk, [], computed_post=computed)


def body(report: dict) -> list[str]:
    lines = [f"WARNING at {w['path']}: {w['message']} [{w['rule_id']}]" for w in report["warnings"]]
    if report["issues"]:
        return lines + [f"ERROR at {i['path']}: {i['message']} [{i['rule_id']}]" for i in report["issues"]]
    if report["command"] == "verify":
        extraction = report["extraction"]
        reason = f" ({extraction['reason']})" if extraction["reason"] else ""
        return lines + [f"EXTRACTION: state={extraction['state']}{reason}"] + check_layout(report)
    if isinstance(report.get("transition"), dict) and report["transition"].get("evaluated"):
        return lines + walk_layout(report)
    lines += check_layout(report)
    if "admission" in report:
        lines += printed(output._print_admission_text, report)
    return lines


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
        lines = header(report) + body(report)
        Path(f"expected/{case}.txt").write_text("\n".join(lines) + "\n")
        exits[case] = {"argv": argv, "exit": done.returncode, "schema_version": report["schema_version"]}
    Path("expected/exits.json").write_text(json.dumps(exits, indent=2) + "\n")


main()
