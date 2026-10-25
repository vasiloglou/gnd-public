"""Write the IK2 approval corpus (spec IK2-D1): cases.json and expected.json.

The expected answers below are authored from the approved spec r1 (sections 6
and 8), not computed from any implementation. Run from the repository root:
    uv run python <this file> tests/fixtures/induced_knowledge/ik2-corpus
"""

import copy
import json
import sys
from pathlib import Path

H64A = "a" * 64
H64B = "b" * 64
REVIEW = ".gnd-planning/milestones/demo/003-review.md"
MAX_SAFE = 2**53 - 1

MINIMAL = {
    "inducer": {"name": "gnd-discover", "version": "0.1.0"},
    "method": "gnd-discover",
    "manifest_sha256": H64A,
    "examples": [],
    "support": {"numerator": 2, "denominator": 3},
    "counterexamples": [],
    "evidence": [{"ref": "populations/p1.json", "sha256": H64B}],
}


def block(**changes):
    result = copy.deepcopy(MINIMAL)
    for dotted, value in changes.items():
        target = result
        parts = dotted.split("__")
        for part in parts[:-1]:
            target = target[part]
        target[parts[-1]] = value
    return result


def induced(status="proposed", modality="deontic", induction=None, reviewed_in=None, **extra):
    provenance = {"induction": copy.deepcopy(MINIMAL) if induction is None else induction}
    if reviewed_in is not None:
        provenance["reviewed_in"] = reviewed_in
    constraint = {
        "type": "uniqueness",
        "roles": ["title"],
        "source": "induced",
        "status": status,
        "modality": modality,
        "provenance": provenance,
    }
    constraint.update(extra)
    return constraint


def ids(prefix, count):
    return [f"{prefix}-{index:04d}" for index in range(count)]


loader = []
expected_loader = {}


def L(case_id, story, exit_code, rule=None, *, constraint=None, constraint_yaml=None, base="evolution", set_=None):
    case = {"id": case_id, "base": base, "story": story}
    if constraint is not None:
        case["constraint"] = constraint
    if constraint_yaml is not None:
        case["constraint_yaml"] = constraint_yaml
    if set_ is not None:
        case["set"] = set_
    loader.append(case)
    expected_loader[case_id] = {"exit": exit_code, "rule_id": rule}


# ---- T2: loader cases ------------------------------------------------------
L("L01", "minimal induced block, proposed and deontic", 0, constraint=induced())
L("L02", "maximal block: examples, counterexamples, two evidence items, confidence", 0,
  constraint=induced(induction=block(
      examples=["case-0001", "case-0002"], counterexamples=["case-0003"],
      evidence=[{"ref": "populations/p1.json", "sha256": H64B},
                {"ref": "labels/manifest.json", "sha256": H64A}],
      confidence={"value": 0.67, "formula": "numerator / denominator"})))
L("L03", "confirmed and alethic, with the review record named", 0,
  constraint=induced("confirmed", "alethic", reviewed_in=REVIEW))
L("L04", "proposed but claiming alethic modality", 0, "semantic:modality-policy",
  constraint=induced("proposed", "alethic"))
L("L05", "provenance present but without an induction block", 3, "jsonschema:required",
  constraint={**induced(), "provenance": {}})
L("L06", "induction block with an unknown key", 3, "jsonschema:additionalProperties",
  constraint=induced(induction=block(notes="host notes")))
L("L07", "an extra provenance key next to induction", 3, "jsonschema:additionalProperties",
  constraint={**induced(), "provenance": {"induction": block(), "host_path": "x"}})
L("L08", "induced source with no provenance at all", 3, "jsonschema:required",
  constraint={key: value for key, value in induced().items() if key != "provenance"})
for case_id, ref, story in (
    ("L09", "/home/user/x.json", "evidence ref is an absolute POSIX path"),
    ("L10", "C:\\data\\x.json", "evidence ref is a Windows path"),
    ("L11", "../x.json", "evidence ref climbs out of the manifest directory"),
    ("L12", "a/../b.json", "evidence ref has a parent segment in the middle"),
    ("L13", ".hidden", "evidence ref segment starts with a dot"),
    ("L14", "a b.json", "evidence ref contains a space"),
):
    L(case_id, story, 3, "jsonschema:pattern",
      constraint=induced(induction=block(evidence=[{"ref": ref, "sha256": H64B}])))
L("L15", "evidence ref ends in a newline", 3, "semantic:induced-provenance",
  constraint=induced(induction=block(evidence=[{"ref": "a\n", "sha256": H64B}])))
for case_id, value, story in (
    ("L16", "Jane Doe", "example id is a raw two-word value"),
    ("L17", "a/b", "example id contains a path separator"),
    ("L18", "", "example id is empty"),
):
    L(case_id, story, 3, "jsonschema:pattern",
      constraint=induced(induction=block(examples=[value])))
L("L19", "example id ends in a newline", 3, "semantic:induced-provenance",
  constraint=induced(induction=block(examples=["a\n"])))
L("L20", "manifest digest in upper case", 3, "jsonschema:pattern",
  constraint=induced(induction=block(manifest_sha256="A" * 64)))
L("L21", "manifest digest one character short", 3, "jsonschema:pattern",
  constraint=induced(induction=block(manifest_sha256="a" * 63)))
L("L22", "evidence digest followed by a newline", 3, "semantic:induced-provenance",
  constraint=induced(induction=block(evidence=[{"ref": "p.json", "sha256": H64B + "\n"}])))
L("L23", "support numerator larger than its denominator", 3, "semantic:induced-provenance",
  constraint=induced(induction=block(support={"numerator": 4, "denominator": 3})))
L("L24", "more listed examples than the support numerator", 3, "semantic:induced-provenance",
  constraint=induced(induction=block(examples=ids("case", 3))))
L("L25", "more counterexamples than the support gap allows", 3, "semantic:induced-provenance",
  constraint=induced(induction=block(counterexamples=ids("neg", 2))))
L("L26", "one id listed as both an example and a counterexample", 3, "semantic:induced-provenance",
  constraint=induced(induction=block(examples=["case-0001"], counterexamples=["case-0001"])))
L("L27", "confirmed without a review record", 3, "jsonschema:required",
  constraint=induced("confirmed", "alethic"))
L("L28", "confirmed with a whitespace-only review record", 3, "semantic:induced-confirmed-reviewed",
  constraint=induced("confirmed", "alethic", reviewed_in="  "))
L("L29", "the same example id listed twice", 3, "jsonschema:uniqueItems",
  constraint=induced(induction=block(examples=["case-0001", "case-0001"])))

FLOW = (
    "{{type: uniqueness, roles: [title], source: induced, status: proposed, modality: deontic, "
    "provenance: {{induction: {{inducer: {{name: gnd-discover, version: {version}}}, method: gnd-discover, "
    "manifest_sha256: " + H64A + ", examples: [], support: {{numerator: {numerator}, denominator: 3}}, "
    "counterexamples: [], evidence: [{{ref: populations/p1.json, sha256: " + H64B + "}}]{confidence}}}}}}}"
)
L("L30", "YAML: confidence value is .nan", 3, "jsonschema:type",
  constraint_yaml=FLOW.format(version="0.1.0", numerator=2, confidence=", confidence: {value: .nan, formula: f}"))
L("L31", "YAML: confidence value is .inf", 3, "jsonschema:type",
  constraint_yaml=FLOW.format(version="0.1.0", numerator=2, confidence=", confidence: {value: .inf, formula: f}"))
L("L32", "YAML: support numerator is an anchored true", 3, "jsonschema:type",
  constraint_yaml=FLOW.format(version="0.1.0", numerator="&n true", confidence=""))
L("L33", "YAML: inducer version is an unquoted date", 3, "jsonschema:type",
  constraint_yaml=FLOW.format(version="2024-01-01", numerator=2, confidence=""))
OP_PROVENANCE = {"induction": copy.deepcopy(MINIMAL)}
L("L34", "induced source on an operation", 3, "jsonschema:not", base="v2_operations",
  set_=[["/operations/0/source", "induced"], ["/operations/0/status", "proposed"],
        ["/operations/0/provenance", OP_PROVENANCE]])
L("L35", "induced source on an operation precondition", 3, "jsonschema:not", base="v2_operations",
  set_=[["/operations/0/preconditions/0/source", "induced"],
        ["/operations/0/preconditions/0/status", "proposed"],
        ["/operations/0/preconditions/0/modality", "deontic"],
        ["/operations/0/preconditions/0/provenance", OP_PROVENANCE]])
L("L36", "induced source on an operation dynamic rule", 3, "jsonschema:not", base="v2_operations",
  set_=[["/operations/0/dynamic_rules/0/source", "induced"],
        ["/operations/0/dynamic_rules/0/status", "proposed"],
        ["/operations/0/dynamic_rules/0/provenance", OP_PROVENANCE]])
L("L37", "an induction block under source explicit", 0,
  constraint={"type": "uniqueness", "roles": ["title"], "source": "explicit", "status": "confirmed",
              "modality": "alethic",
              "provenance": {"user_quote": "Each title has one item.", "induction": block()}})
L("L38", "confidence without its formula", 3, "jsonschema:required",
  constraint=induced(induction=block(confidence={"value": 0.5})))

# ---- T3: bounds -------------------------------------------------------------
def B(case_id, story, exit_code, rule, induction, **kwargs):
    L(case_id, story, exit_code, rule, constraint=induced(induction=induction, **kwargs))


B("B01", "inducer name of 1 character", 0, None, block(inducer__name="g"))
B("B02", "inducer name of 64 characters", 0, None, block(inducer__name="g" * 64))
B("B03", "inducer name of 65 characters", 3, "jsonschema:pattern", block(inducer__name="g" * 65))
B("B04", "empty inducer name", 3, "jsonschema:pattern", block(inducer__name=""))
B("B05", "inducer version of 64 characters", 0, None, block(inducer__version="1" * 64))
B("B06", "inducer version of 65 characters", 3, "jsonschema:pattern", block(inducer__version="1" * 65))
B("B07", "method of 64 characters", 0, None, block(method="m" * 64))
B("B08", "method of 65 characters", 3, "jsonschema:pattern", block(method="m" * 65))
B("B09", "empty method", 3, "jsonschema:pattern", block(method=""))
B("B10", "example id of 64 characters", 0, None, block(examples=["e" * 64]))
B("B11", "example id of 65 characters", 3, "jsonschema:pattern", block(examples=["e" * 65]))
B("B12", "256 examples", 0, None,
  block(examples=ids("case", 256), support={"numerator": 300, "denominator": 400}))
B("B13", "257 examples", 3, "jsonschema:maxItems",
  block(examples=ids("case", 257), support={"numerator": 300, "denominator": 400}))
B("B14", "32 counterexamples", 0, None,
  block(counterexamples=ids("neg", 32), support={"numerator": 2, "denominator": 40}))
B("B15", "33 counterexamples", 3, "jsonschema:maxItems",
  block(counterexamples=ids("neg", 33), support={"numerator": 2, "denominator": 40}))
B("B16", "no evidence items", 3, "jsonschema:minItems", block(evidence=[]))
B("B17", "32 evidence items", 0, None,
  block(evidence=[{"ref": f"p/{index}.json", "sha256": H64B} for index in range(32)]))
B("B18", "33 evidence items", 3, "jsonschema:maxItems",
  block(evidence=[{"ref": f"p/{index}.json", "sha256": H64B} for index in range(33)]))
B("B19", "evidence ref of 256 characters", 0, None, block(evidence=[{"ref": "r" * 256, "sha256": H64B}]))
B("B20", "evidence ref of 257 characters", 3, "jsonschema:maxLength",
  block(evidence=[{"ref": "r" * 257, "sha256": H64B}]))
B("B21", "negative support numerator", 3, "jsonschema:minimum", block(support={"numerator": -1, "denominator": 3}))
B("B22", "numerator and denominator at 2^53 - 1", 0, None,
  block(support={"numerator": MAX_SAFE, "denominator": MAX_SAFE}))
B("B23", "numerator at 2^53", 3, "jsonschema:maximum",
  block(support={"numerator": MAX_SAFE + 1, "denominator": MAX_SAFE}))
B("B24", "denominator of 0", 3, "jsonschema:minimum", block(support={"numerator": 0, "denominator": 0}))
B("B25", "denominator at 2^53", 3, "jsonschema:maximum", block(support={"numerator": 2, "denominator": MAX_SAFE + 1}))
B("B26", "confidence value 0", 0, None, block(confidence={"value": 0, "formula": "f"}))
B("B27", "confidence value 1", 0, None, block(confidence={"value": 1, "formula": "f"}))
B("B28", "confidence value -0.01", 3, "jsonschema:minimum", block(confidence={"value": -0.01, "formula": "f"}))
B("B29", "confidence value 1.01", 3, "jsonschema:maximum", block(confidence={"value": 1.01, "formula": "f"}))
B("B30", "empty confidence formula", 3, "jsonschema:minLength", block(confidence={"value": 0.5, "formula": ""}))
B("B31", "confidence formula of 256 characters", 0, None, block(confidence={"value": 0.5, "formula": "f" * 256}))
B("B32", "confidence formula of 257 characters", 3, "jsonschema:maxLength",
  block(confidence={"value": 0.5, "formula": "f" * 257}))
B("B33", "review record of 256 characters", 0, None, block(), status="confirmed", modality="alethic",
  reviewed_in="r" * 256)
B("B34", "review record of 257 characters", 3, "jsonschema:maxLength", block(), status="confirmed",
  modality="alethic", reviewed_in="r" * 257)

# ---- T4: admission (gate and preview) --------------------------------------
P = induced()
CONF = induced("confirmed", "deontic", reviewed_in=REVIEW)
CONF_ALETHIC = induced("confirmed", "alethic", reviewed_in=REVIEW)
CHANGED = block(examples=["case-0009"])

admission = []
expected_admission = {}


def A(case_id, story, gate, preview_exit, before, candidate, preview_reason=None):
    # preview_reason: the refusal text a preview must carry. It defaults to the
    # gate reason, so a preview refused for some other cause cannot pass.
    if preview_exit == 3 and preview_reason is None:
        preview_reason = gate
    admission.append({"id": case_id, "story": story, "before": before, "candidate": candidate,
                      "preview": preview_exit is not None})
    expected_admission[case_id] = {"gate": gate, "preview_exit": preview_exit,
                                   "preview_reason": preview_reason}


A("A01", "a new induced rule, proposed and advisory", "admitted", 0, [], [P])
A("A02", "a new induced rule claiming alethic modality", "R-I4", 3, [], [induced("proposed", "alethic")])
A("A03", "a new induced rule arriving already confirmed", "R-I3", 3, [], [CONF_ALETHIC])
A("A04", "a new proposed induced rule that already names a review record", "R-I2", 3, [],
  [induced(reviewed_in=REVIEW)])
A("A05", "an existing proposed induced rule confirmed by review, kept advisory", "admitted", 0, [P], [CONF])
A("A06", "an existing proposed induced rule confirmed by review and made alethic", "admitted", 0, [P],
  [CONF_ALETHIC])
A("A07", "confirmation that also edits the rule's rationale", "R-I3", 3, [P],
  [induced("confirmed", "deontic", reviewed_in=REVIEW, rationale="Edited while confirming.")])
A("A08", "an induction block under a new llm-inferred rule", "R-I1", 3, [],
  [{"type": "uniqueness", "roles": ["title"], "source": "llm-inferred", "status": "proposed",
    "modality": "deontic", "rationale": "Titles name one item.",
    "provenance": {"rationale_world_fact": "Titles name one item.", "induction": block()}}])
A("A09", "an induction block under a new user-supplied rule", "R-I1", 3, [],
  [{"type": "uniqueness", "roles": ["title"], "source": "user-supplied", "status": "confirmed",
    "modality": "alethic", "provenance": {"user_note": "Owner rule.", "induction": block()}}])
A("A10", "an already confirmed induced rule left unchanged", "admitted", None, [CONF_ALETHIC],
  [CONF_ALETHIC])
A("A11", "two confirmations claiming the same single proposed predecessor", "R-I3", None, [P],
  [CONF, CONF])
A("A12", "the proposed predecessor kept unchanged next to a confirmed copy", "R-I3", None, [P],
  [P, CONF])
A("A13", "confirmation with a whitespace-only review record", "R-I3", 3, [P],
  [induced("confirmed", "deontic", reviewed_in="  ")],
  preview_reason="semantic:induced-confirmed-reviewed")
A("A14", "a confirmed induced rule whose evidence changes, returned to proposed", "admitted", 0,
  [CONF_ALETHIC], [induced(induction=CHANGED)])
A("A15", "a confirmed induced rule whose evidence changes, still confirmed", "R-I3", 3,
  [CONF_ALETHIC], [induced("confirmed", "alethic", induction=CHANGED, reviewed_in=REVIEW)])
A("A16", "confirmation whose predecessor was llm-inferred, not induced", "R-I3", 3,
  [{"type": "uniqueness", "roles": ["title"], "source": "llm-inferred", "status": "proposed",
    "modality": "deontic", "rationale": "Titles name one item.",
    "provenance": {"rationale_world_fact": "Titles name one item."}}],
  [CONF])
A("A17", "a hostile induction value (a string) under source explicit", "R-I1", None, [],
  [{"type": "uniqueness", "roles": ["title"], "source": "explicit", "status": "confirmed",
    "modality": "alethic", "provenance": {"user_quote": "q", "induction": "not a block"}}])


def main(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    cases = {
        "version": 1,
        "spec": ".gnd-planning/milestones/induced-knowledge/notes/phase-IK2-spec.md (r1)",
        "bases": {
            "evolution": "tests/fixtures/phase4_reference/evolution.json#evolution-safe-additive/before_model",
            "v2_operations": "tests/fixtures/models/v2_operations.orm.yaml",
        },
        "host": "constraints are appended to fact_types[0].constraints of the base",
        "loader": loader,
        "admission": admission,
    }
    expected = {
        "version": 1,
        "reasons": {
            "R-I1": "provenance.induction is allowed only under source induced (D-12)",
            "R-I2": "new induced constraints cannot carry provenance.reviewed_in (D-12)",
            "R-I3": "induced constraints become confirmed only as a reviewed status change of an existing proposed induced constraint (D-12)",
            "R-I4": "new induced constraints must be proposed/deontic (D-12)",
        },
        "loader": expected_loader,
        "admission": expected_admission,
    }
    for name, document in (("cases.json", cases), ("expected.json", expected)):
        (out_dir / name).write_text(json.dumps(document, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
