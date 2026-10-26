"""Write the IK3 approval corpus manifests and answer key (spec IK3-D1).

Answers are hand-written from the approved spec r1 (§5, §6, §8); the existing
`gnd check` was used only to confirm the verdicts per population. Run from the
repository root:
    uv run python <this file>
"""

import hashlib
import json
from pathlib import Path

C = Path("tests/fixtures/induced_knowledge/ik3-corpus")
MODEL_SHA = hashlib.sha256((C / "labels.orm.yaml").read_bytes()).hexdigest()
U, M, F = "id:u_person_team", "id:m_person_grade", "fact_types[person_has_skill].constraints[0]"
RU = "fact_types[person_in_team].constraints[0]"
RM = "fact_types[person_has_grade].constraints[0]"
RF = F


def sha(name: str) -> str:
    return hashlib.sha256((C / "pops" / name).read_bytes()).hexdigest()


def es(gt: str, v: str) -> dict:
    return {"ground_truth": gt, "expected_verdict": v}


SAT = es("satisfied", "pass")


def pop(pid: str, name: str, **body) -> dict:
    return {"id": pid, "path": f"pops/{name}", "sha256": sha(name), **body}


def manifest(mode: str, populations: list, rules: dict | None = None, **over) -> dict:
    doc = {"schema_version": "gnd-labels/1", "model_sha256": MODEL_SHA, "mode": mode,
           "populations": populations}
    if rules is not None:
        doc["rules"] = rules
    doc.update(over)
    return doc


def labels(u, m, f) -> dict:
    return {"expectations": {U: u, M: m, F: f}}


cases, answers = [], {}


def case(cid: str, story: str, document, answer: dict, *, argv=None, file_text=None) -> None:
    name = f"{cid.lower()}.labels.json"
    if document is not None:
        text = json.dumps(document, indent=1) + "\n"
    else:
        text = file_text
    if text is not None:
        (C / name).write_text(text, encoding="utf-8")
    cases.append({"id": cid, "story": story, "manifest": name if text is not None else None,
                  "argv": argv or []})
    answers[cid] = answer


def cells(**kw):
    base = {"correct": 0, "false_pass": 0, "false_fail": 0, "undecided": 0,
            "masked_by_vacuity": 0, "tool_defect": 0}
    base.update(kw)
    return base


# ---- expected-state mode ----------------------------------------------------
E1_POPS = [pop("ok", "ok.yaml", **labels(SAT, SAT, SAT)),
           pop("dup", "dup.yaml", **labels(es("violated", "fail"), SAT, SAT)),
           pop("nograde", "nograde.yaml", **labels(SAT, es("violated", "warning"), SAT))]
case("E1", "three populations, every rule labelled to match what a correct checker says",
     manifest("expected-state", E1_POPS),
     {"exit": 0, "schema_version": 4, "cells": {RU: cells(correct=3), RM: cells(correct=3),
                                                 RF: cells(correct=3)}, "defects": []})
E2_POPS = [E1_POPS[0], pop("dup", "dup.yaml", **labels(SAT, SAT, SAT)), E1_POPS[2]]
case("E2", "the duplicate-team population is mislabelled as satisfying the alethic uniqueness rule",
     manifest("expected-state", E2_POPS),
     {"exit": 6, "schema_version": 4,
      "cells": {RU: cells(correct=2, false_fail=1), RM: cells(correct=3), RF: cells(correct=3)},
      "defects": [{"kind": "false-fail", "constraint_ref": RU, "modality": "alethic",
                   "population": "pops/dup.yaml", "expected_verdict": "pass",
                   "observed_verdict": "fail"}]})
case("E3", "labels that expect no subjects and an unevaluable cell",
     manifest("expected-state", [
         pop("ok", "ok.yaml", **labels(SAT, SAT, SAT)),
         pop("noskill", "noskill.yaml", **labels(SAT, SAT, es("no-subjects", "vacuous"))),
         pop("opaque", "opaque.yaml",
             **labels(SAT, es("satisfied", "unchecked"), es("satisfied", "unchecked")))]),
     {"exit": 0, "schema_version": 4,
      "cells": {RU: cells(correct=3), RM: cells(correct=3), RF: cells(correct=3)}, "defects": []})
case("E4", "a label whose expected verdict contradicts its own ground truth",
     manifest("expected-state", [pop("ok", "ok.yaml", **labels(es("satisfied", "fail"), SAT, SAT))]),
     {"exit": 3})
case("E5", "one population leaves the frequency rule unlabelled",
     manifest("expected-state", [pop("ok", "ok.yaml", expectations={U: SAT, M: SAT})]),
     {"exit": 3})
case("E6", "a positional ref names a rule that has an id",
     manifest("expected-state", [pop("ok", "ok.yaml", expectations={RU: SAT, M: SAT, F: SAT})]),
     {"exit": 3})
case("E7", "an id that no rule carries",
     manifest("expected-state", [pop("ok", "ok.yaml", expectations={"id:nope": SAT, U: SAT, M: SAT, F: SAT})]),
     {"exit": 3})
case("E8", "the manifest was written for a different model",
     manifest("expected-state", [E1_POPS[0]], model_sha256="0" * 64), {"exit": 3})
bad = dict(E1_POPS[0])
bad["sha256"] = "f" * 64
case("E9", "a population whose bytes do not match the manifest's digest",
     manifest("expected-state", [bad]), {"exit": 3})
esc = dict(E1_POPS[0])
esc["path"] = "../ok.yaml"
case("E10", "a population path that climbs out of the manifest's directory",
     manifest("expected-state", [esc]), {"exit": 3})
case("E11", "a population that fails to load",
     manifest("expected-state", [pop("broken", "broken.yaml", **labels(SAT, SAT, SAT))]),
     {"exit": 5})
case("E12", "a population path that is a symbolic link (made by the harness)",
     manifest("expected-state", [{"id": "link", "path": "pops/link.yaml", "sha256": sha("ok.yaml"),
                                  **labels(SAT, SAT, SAT)}]), {"exit": 74})
case("E13", "both --labels and --populations", manifest("expected-state", [E1_POPS[0]]),
     {"exit": 64}, argv=["--populations", "."])
case("E14", "neither --labels nor --populations", None, {"exit": 64}, argv=["NO-SOURCE"])
case("E15", "the manifest file does not exist", None, {"exit": 66}, argv=["MISSING"])
case("E16", "a manifest that is not JSON: a NaN and a duplicate key", None, {"exit": 3},
     file_text='{"schema_version": "gnd-labels/1", "mode": "class", "mode": "class", "x": NaN}\n')
case("E17", "a manifest over the 1 MiB cap (made by the harness)", None, {"exit": 3},
     argv=["OVER-CAP"])
deep = {"x": 0}
for _ in range(70):
    deep = {"x": deep}
case("E18", "a manifest nested deeper than 64 levels",
     manifest("expected-state", [E1_POPS[0]], extra=deep), {"exit": 3})
case("E19", "a manifest with a field the schema does not know",
     manifest("expected-state", [E1_POPS[0]], notes="hello"), {"exit": 3})
absolute = dict(E1_POPS[0])
absolute["path"] = "/etc/hosts"
case("E20", "an absolute population path", manifest("expected-state", [absolute]), {"exit": 3})
case("E21", "a positional ref past the end of its fact type's constraints",
     manifest("expected-state", [pop("ok", "ok.yaml", expectations={
         U: SAT, M: SAT, F: SAT, "fact_types[person_has_skill].constraints[1]": SAT})]),
     {"exit": 3})
case("E22", "a reason longer than 256 characters",
     manifest("expected-state", [pop("ok", "ok.yaml", **labels({**SAT, "reason": "r" * 257}, SAT, SAT))]),
     {"exit": 3})
case("E23", "an expected-state manifest whose population carries a class",
     manifest("expected-state", [pop("ok", "ok.yaml", **labels(SAT, SAT, SAT), **{"class": "positive"})]),
     {"exit": 3})
case("E24", "a manifest with no populations", manifest("expected-state", []), {"exit": 3})

# ---- class mode -------------------------------------------------------------
C1_POPS = [pop("ok", "ok.yaml", **{"class": "positive"}),
           pop("dup", "dup.yaml", **{"class": "negative"}),
           pop("nograde", "nograde.yaml", **{"class": "negative"}),
           pop("noskill", "noskill.yaml", **{"class": "positive"}),
           pop("opaque", "opaque.yaml", **{"class": "negative"})]
NEG = {"fires_on": "negative"}


def ag(fn, fp, sn, sp, vac, unc):
    def cell(pair):
        return {"numerator": pair[0], "denominator": pair[1]}
    return {"fired_on_negative": cell(fn), "fired_on_positive": cell(fp),
            "silent_on_negative": cell(sn), "silent_on_positive": cell(sp),
            "vacuous": cell(vac), "unchecked": cell(unc)}


case("C1", "five populations, three rules that should each fire on the negative class",
     manifest("class", C1_POPS, {U: NEG, M: NEG, F: NEG}),
     {"exit": 0, "schema_version": 5, "rules": {
         RU: {"fires_on": "negative", "cells": ag((1, 3), (0, 2), (2, 3), (2, 2), (0, 5), (0, 5))},
         RM: {"fires_on": "negative", "cells": ag((1, 2), (0, 2), (1, 2), (2, 2), (0, 5), (1, 5))},
         RF: {"fires_on": "negative", "cells": ag((0, 2), (0, 1), (2, 2), (1, 1), (1, 5), (1, 5))}}})
case("C2", "the control: a rule that fires exactly on the negative population, and a wrong rule",
     manifest("class", [C1_POPS[0], C1_POPS[1]], {U: NEG, M: NEG}),
     {"exit": 0, "schema_version": 5, "rules": {
         RU: {"fires_on": "negative", "cells": ag((1, 1), (0, 1), (0, 1), (1, 1), (0, 2), (0, 2))},
         RM: {"fires_on": "negative", "cells": ag((0, 1), (0, 1), (1, 1), (1, 1), (0, 2), (0, 2))}}})
case("C3", "a class-mode rule that names an unknown id",
     manifest("class", [C1_POPS[0]], {"id:nope": NEG}), {"exit": 3})
case("C4", "a class manifest with no rules",
     manifest("class", [C1_POPS[0]]), {"exit": 3})
case("C5", "a class manifest with 1,025 rules, one over the bound (made by the harness)",
     None, {"exit": 3}, argv=["RULES-OVER"])
case("N1", "near-cap: 8,000 class-mode entries under 1 MiB, alternating classes (made by the harness)",
     None, {"exit": 0, "schema_version": 5, "manifest_bytes_max": 1048576,
            "work_ceiling": 32000, "ceiling_arithmetic": "P x (1 + C) = 8000 x (1 + 3) = 32000",
            "rules": {r: {"fires_on": "negative", "cells": ag((0, 4000), (0, 4000), (4000, 4000),
                                                             (4000, 4000), (0, 8000), (0, 8000))}
                      for r in (RU, RM, RF)}},
     argv=["NEAR-CAP"])
case("X1", "parity: the committed movie/faker synth corpus, its sidecar labels converted to a manifest",
     None, {"exit": 0, "schema_version": 4,
            "per_constraint_equals": "tests/fixtures/public-launch-phase-3/measurement/measurements/movie.faker.json",
            "ignored_row_fields": ["wrong_attribution", "set_attributed_evidence"]},
     argv=["PARITY"])
case("D1", "determinism: C1 run twice gives byte-identical reports", None,
     {"exit": 0, "deterministic_over": "C1"}, argv=["DETERMINISM"])

(C / "cases.json").write_text(json.dumps({"version": 1, "model": "labels.orm.yaml",
                                          "command": "gnd measure labels.orm.yaml --labels <manifest> --format json",
                                          "cases": cases}, indent=1) + "\n")
(C / "expected.json").write_text(json.dumps({"version": 1,
    "note": "Hand-written from spec r1. cells keys are the checker's positional refs; "
            "defect rows omit the synth-only sidecar and seed fields (C-F2).",
    "cases": answers}, indent=1) + "\n")
print(len(cases), "cases")
