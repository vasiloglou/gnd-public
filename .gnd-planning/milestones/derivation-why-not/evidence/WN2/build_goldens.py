"""Write tests/fixtures/why_not/cases.json and goldens/ (corpus-first, WN-D10).

    uv run python .gnd-planning/milestones/derivation-why-not/evidence/WN2/build_goldens.py

Clause bodies and work counters come from the WN1 kernel. The envelope (spec
§6.3) and the redaction (§6.4) are written out here independently of the WN2
service, view and CLI, which did not exist when these goldens were committed.
Each golden is the exact CLI stdout: sorted-key JSON on one line.
"""

from __future__ import annotations

import json
from pathlib import Path

from gnd.model import bind_declared_references, load_model
from gnd.population import load_population
from gnd.witness.why_not import WhyNotWorkError, explain

FX = Path("tests/fixtures/why_not")
EX = Path("src/gnd/examples/dispatch")
SCHEMA = "gnd-why-not/1"


def envelope(exit_code, body):
    return {"schema_version": SCHEMA, "exit_code": exit_code, **body}


def refused(reason, exit_code, work=None):
    return envelope(exit_code, {
        "status": "refused", "reason": reason, "fact_type": None, "mode": None,
        "order": None, "unavailable": None, "clauses": [], "work": work or {},
    })


EXITS = {"blocked": 0, "derived": 0, "unsupported": 2, "unavailable": 4}


def redact_role(spec):
    if "constant" in spec:
        return {"constant": "redacted"}
    return {"variable": spec["variable"], "bound": spec["bound"]}


def redact_blocker(blocker):
    out = {}
    for key in ("kind", "index", "fact_type", "count", "derivation", "ground",
                "asserted_not_read", "reads", "sample_count"):
        if key in blocker:
            out[key] = list(blocker[key]) if key == "reads" else blocker[key]
    if "roles" in blocker:
        out["roles"] = {role: redact_role(spec) for role, spec in blocker["roles"].items()}
    out["samples"] = "redacted"
    return out


def redact_explanation(payload):
    out = {key: payload[key] for key in ("status", "reason", "fact_type", "mode", "order")}
    unavailable = payload["unavailable"]
    out["unavailable"] = None if unavailable is None else {
        "reason": unavailable["reason"],
        "source_relation": unavailable["source_relation"],
        "binding": "redacted",
    }
    out["clauses"] = [
        {
            "clause_index": clause["clause_index"],
            "steps": [
                {key: step[key] for key in ("kind", "index", "fact_type", "count") if key in step}
                for step in clause["steps"]
            ],
            "blocker": redact_blocker(clause["blocker"]),
            "steps_after_blocker": clause["steps_after_blocker"],
            "descent": None if clause["descent"] is None else redact_explanation(clause["descent"]),
            "descent_stopped": clause["descent_stopped"],
        }
        for clause in payload["clauses"]
    ]
    out["work"] = dict(payload["work"])
    return out


def redact(payload):
    out = {"schema_version": payload["schema_version"], "exit_code": payload["exit_code"]}
    out.update(redact_explanation(payload))
    return out


def raw_payload(model_path, population_path, fact_type, row_path=None, root=None):
    model = load_model(model_path)
    candidate = load_population(population_path, model=model)
    context = bind_declared_references(model, root=Path(root or Path(model_path).parent))
    row = None
    if row_path is not None:
        row = json.loads(Path(row_path).read_text())["targets"][0]["tuple"]
    try:
        result = explain(model, candidate, fact_type, row=row, references=context).to_dict()
    except WhyNotWorkError as error:
        return refused("work-limit", 4, error.work)
    return envelope(EXITS[result["status"]], result)


C, R = "<fx>/claims", "<fx>/rows"
CASES = [
    # id, argv after "why-not", expected payload source
    ("g1-rule-blocked", [f"{C}/model.orm.json", f"{C}/gap.pop.json", "--fact-type", "credited"]),
    ("g2-row-descent", [f"{C}/model.orm.json", f"{C}/gap.pop.json", "--fact-type", "claim",
                        "--row", f"{R}/claim-w1-p1.json"]),
    ("g3-derived", [f"{C}/model.orm.json", f"{C}/repaired.pop.json", "--fact-type", "claim",
                    "--row", f"{R}/claim-w1-p1.json"]),
    ("g4-rule-opaque", [f"{C}/model.orm.json", f"{C}/gap.pop.json", "--fact-type", "note"]),
    ("g5-aggregate", [f"{C}/model.orm.json", f"{C}/gap.pop.json", "--fact-type", "tally"]),
    ("g6-opaque-value", [f"{C}/model.orm.json", f"{C}/opaque.pop.json", "--fact-type", "claim"]),
    ("g7-unavailable", [f"{C}/model.orm.json", f"{C}/gap.pop.json", "--fact-type", "ratio"]),
    ("g8-work-limit", [f"{C}/model.orm.json", f"{C}/big.pop.json", "--fact-type", "lonely"]),
    ("g9-references", ["<ex>/model.orm.json", "<ex>/seed.pop.json", "--fact-type",
                       "dispatch_reachable", "--row", f"{R}/reach-a-e.json"]),
    ("g10-unknown-fact-type", [f"{C}/model.orm.json", f"{C}/gap.pop.json", "--fact-type", "nope"]),
    ("g10-not-derived", [f"{C}/model.orm.json", f"{C}/gap.pop.json", "--fact-type", "listed"]),
    ("g11-zero-targets", [f"{C}/model.orm.json", f"{C}/gap.pop.json", "--fact-type", "claim",
                          "--row", f"{R}/zero.json"]),
    ("g11-two-targets", [f"{C}/model.orm.json", f"{C}/gap.pop.json", "--fact-type", "claim",
                         "--row", f"{R}/two.json"]),
    ("g11-other-fact-type", [f"{C}/model.orm.json", f"{C}/gap.pop.json", "--fact-type", "claim",
                             "--row", f"{R}/other-fact-type.json"]),
    ("g11-primitive-mismatch", [f"{C}/model.orm.json", f"{C}/gap.pop.json", "--fact-type",
                                "claim", "--row", f"{R}/primitive-mismatch.json"]),
    ("g13-malformed-row-first", [f"{C}/model.orm.json", f"{C}/gap.pop.json", "--fact-type",
                                 "tally", "--row", f"{R}/tally-malformed.json"]),
]
INPUT_INVALID = {"g10-unknown-fact-type", "g10-not-derived", "g11-zero-targets",
                 "g11-two-targets", "g11-other-fact-type", "g11-primitive-mismatch",
                 "g13-malformed-row-first"}


def resolve(argv):
    return [a.replace("<fx>", str(FX)).replace("<ex>", str(EX)) for a in argv]


def line(payload):
    return json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n"


def main():
    goldens = FX / "goldens"
    goldens.mkdir(parents=True, exist_ok=True)
    cases = []
    for case_id, argv in CASES:
        if case_id in INPUT_INVALID:
            raw = refused("input-invalid", 3)
        else:
            args = resolve(argv)
            row = args[args.index("--row") + 1] if "--row" in args else None
            raw = raw_payload(args[0], args[1], args[args.index("--fact-type") + 1], row)
        (goldens / f"{case_id}.json").write_text(line({**redact(raw), "view": "redacted"}))
        (goldens / f"{case_id}.raw.json").write_text(line({**raw, "view": "raw"}))
        cases.append({"id": case_id, "argv": ["why-not", *argv], "exit": raw["exit_code"]})
    (FX / "cases.json").write_text(json.dumps(cases, indent=2) + "\n")
    (goldens / "refused-input.json").write_text(
        line({**redact(refused("input-invalid", 3)), "view": "redacted"}))


if __name__ == "__main__":
    main()
