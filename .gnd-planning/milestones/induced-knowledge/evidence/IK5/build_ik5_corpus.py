"""Write the IK5 approval corpus inputs and answer key (spec IK5-D1).

The expected export files, constraints, exits and refusal names below are
written by hand from the approved spec r1 (§6, §8); this script only fills in
real file digests and writes the files. The existing `gnd check` was used only
to confirm the verdicts each learned rule draws per population. The learner
outputs are hand-authored in Popper's printed syntax (IK5-D13 (a)); no learner
ran. Run from the repository root:
    uv run python <this file>
"""

import hashlib
import json
from pathlib import Path

C = Path("tests/fixtures/induced_knowledge/ik5-corpus")
MODEL = "orders.orm.yaml"
LEARNER = {"name": "popper", "version": "0.0.0+authored"}
ORDER = ["n1", "n2", "n3", "p1", "p2", "v1"]
CLASS = {"n1": "negative", "n2": "negative", "n3": "negative",
         "p1": "positive", "p2": "positive", "v1": "positive"}


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def canonical(document) -> bytes:
    return (json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def write(name: str, data: bytes | str) -> Path:
    path = C / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if isinstance(data, bytes) else data.encode())
    return path


MODEL_SHA = sha(C / MODEL)


def pop(pid: str, name: str | None = None, **body) -> dict:
    name = name or f"{pid}.yaml"
    return {"id": pid, "path": f"pops/{name}", "sha256": sha(C / "pops" / (
        "n1.yaml" if name == "link.yaml" else name)), **body}


def manifest(mode: str, populations: list, rules: dict | None = None) -> dict:
    doc = {"schema_version": "gnd-labels/1", "model_sha256": MODEL_SHA, "mode": mode,
           "populations": populations}
    if rules is not None:
        doc["rules"] = rules
    return doc


RULES = {"id:u_order_customer": {"fires_on": "negative"}}
MAIN = write("m.labels.json", json.dumps(manifest(
    "class", [pop(p, **{"class": CLASS[p]}) for p in ORDER], RULES), indent=1) + "\n")
MANIFEST_SHA = sha(MAIN)
write("es.labels.json", json.dumps(manifest("expected-state", [pop("n1", expectations={
    "id:u_order_customer": {"ground_truth": "satisfied", "expected_verdict": "pass"}})]),
    indent=1) + "\n")
write("opaque.labels.json", json.dumps(manifest("class", [
    pop("n1", **{"class": "negative"}), pop("opaque", **{"class": "negative"})], RULES),
    indent=1) + "\n")
write("link.labels.json", json.dumps(manifest("class", [
    pop("n1", "link.yaml", **{"class": "negative"})], RULES), indent=1) + "\n")

# ---- The expected export, written by hand (spec §6 "Neutral form", "Popper rendering").
FACTS = [  # (example, predicate, values), already in the spec's order
    ("n1", "f_order_amount", [1, 50]), ("n1", "f_order_amount", [2, 150]),
    ("n1", "f_order_by", [1, "c1"]), ("n1", "f_order_by", [2, "c2"]),
    ("n2", "f_customer_blocked", ["c3"]),
    ("n2", "f_order_amount", [3, 200]), ("n2", "f_order_amount", [4, 20]),
    ("n2", "f_order_by", [3, "c1"]), ("n2", "f_order_by", [4, "c3"]),
    ("n2", "f_order_flagged", [4]),
    ("n3", "f_order_amount", [8, 10]), ("n3", "f_order_by", [8, "c2"]),
    ("n3", "f_order_flagged", [8]),
    ("p1", "f_order_amount", [5, 30]), ("p1", "f_order_amount", [6, 90]),
    ("p1", "f_order_by", [5, "c1"]), ("p1", "f_order_by", [6, "c2"]),
    ("p2", "f_customer_blocked", ["c3"]), ("p2", "f_order_amount", [7, 100]),
    ("p2", "f_order_by", [7, "c3"]),
    ("v1", "f_customer_blocked", ["c1"]),
]
NEUTRAL = {
    "schema_version": "gnd-ilp/1",
    "model_sha256": MODEL_SHA,
    "manifest_sha256": MANIFEST_SHA,
    "target": {"predicate": "wrong", "arity": 1, "covers_class": "negative"},
    "types": [
        {"name": "t_amount", "object_type": "amount", "primitive": "integer"},
        {"name": "t_customer", "object_type": "customer", "primitive": None},
        {"name": "t_order", "object_type": "order", "primitive": None},
    ],
    "predicates": [
        {"name": "f_customer_blocked", "fact_type": "customer_blocked",
         "roles": ["customer"], "types": ["ex", "t_customer"]},
        {"name": "f_order_amount", "fact_type": "order_amount",
         "roles": ["order", "amount"], "types": ["ex", "t_order", "t_amount"]},
        {"name": "f_order_by", "fact_type": "order_by",
         "roles": ["order", "customer"], "types": ["ex", "t_order", "t_customer"]},
        {"name": "f_order_flagged", "fact_type": "order_flagged",
         "roles": ["order"], "types": ["ex", "t_order"]},
    ],
    "comparisons": [
        {"name": "ge_t_amount", "operator": ">=", "type": "t_amount"},
        {"name": "gt_t_amount", "operator": ">", "type": "t_amount"},
        {"name": "le_t_amount", "operator": "<=", "type": "t_amount"},
        {"name": "lt_t_amount", "operator": "<", "type": "t_amount"},
    ],
    "examples": [{"id": p, "class": CLASS[p], "label": "pos" if CLASS[p] == "negative" else "neg"}
                 for p in ORDER],
    "facts": [{"example": e, "predicate": p, "values": v} for e, p, v in FACTS],
    "skipped": {"derived_fact_types": []},
}


def prolog(value) -> str:
    return str(value) if isinstance(value, int) else "'" + value.replace("\\", "\\\\").replace(
        "'", "\\'") + "'"


BK = "".join(f"{p}('{e}',{','.join(prolog(v) for v in vs)}).\n" for e, p, vs in FACTS) + (
    "ge_t_amount(A,B) :- A >= B.\n"
    "gt_t_amount(A,B) :- A > B.\n"
    "le_t_amount(A,B) :- A =< B.\n"
    "lt_t_amount(A,B) :- A < B.\n")
EXS = "".join(f"{'pos' if CLASS[p] == 'negative' else 'neg'}(wrong('{p}')).\n" for p in ORDER)
BIAS = """head_pred(wrong,1).
type(wrong,(ex,)).
body_pred(f_customer_blocked,2).
type(f_customer_blocked,(ex,t_customer)).
body_pred(f_order_amount,3).
type(f_order_amount,(ex,t_order,t_amount)).
body_pred(f_order_by,3).
type(f_order_by,(ex,t_order,t_customer)).
body_pred(f_order_flagged,2).
type(f_order_flagged,(ex,t_order)).
body_pred(ge_t_amount,2).
type(ge_t_amount,(t_amount,t_amount)).
body_pred(gt_t_amount,2).
type(gt_t_amount,(t_amount,t_amount)).
body_pred(le_t_amount,2).
type(le_t_amount,(t_amount,t_amount)).
body_pred(lt_t_amount,2).
type(lt_t_amount,(t_amount,t_amount)).
magic_value_type(t_amount).
max_vars(6).
max_body(5).
max_clauses(4).
"""


def export_tree(target: str, files: dict[str, bytes]) -> str:
    index = {"schema_version": "gnd-ilp-export/1", "target": target, "adapter_version": "1",
             "files": [{"path": path, "sha256": sha_bytes(data), "bytes": len(data)}
                       for path, data in sorted(files.items())]}
    for path, data in {**files, "export.json": canonical(index)}.items():
        write(f"expected-export/{target}/{path}", data)
    return sha_bytes(canonical(index))


NEUTRAL_BYTES = canonical(NEUTRAL)
E_POPPER = export_tree("popper", {"neutral.json": NEUTRAL_BYTES, "popper/bk.pl": BK.encode(),
                                  "popper/exs.pl": EXS.encode(), "popper/bias.pl": BIAS.encode()})
E_NEUTRAL = export_tree("neutral", {"neutral.json": NEUTRAL_BYTES})

# ---- Learned clauses (hand-authored learner output) ----


def var(name):
    return {"var": name}


def const(value):
    return {"const": value}


def atom(predicate, *args):
    return {"atom": {"predicate": predicate, "args": list(args)}}


def compare(op, left, right):
    return {"compare": {"operator": op, "left": left, "right": right}}


def clause(*body):
    return {"head": {"predicate": "wrong", "args": [var("A")]}, "body": list(body)}


A, B, CV = var("A"), var("B"), var("C")
AMOUNT = atom("f_order_amount", A, B, CV)
RULE_A = clause(AMOUNT, compare(">", CV, const(100)))
RULE_B = clause(AMOUNT, atom("f_order_flagged", A, B))
RULE_C = clause(AMOUNT, compare(">", CV, const(80)))
POPPER_ABC = ("wrong(A):- f_order_amount(A,B,C),gt_t_amount(C,100).\n"
              "wrong(A):- f_order_amount(A,B,C),f_order_flagged(A,B).\n"
              "wrong(A):- f_order_amount(A,B,C),gt_t_amount(C,80).\n")
COVER = {"A": ["n1", "n2"], "B": ["n2", "n3"], "C": ["n1", "n2", "p1", "p2"]}


def clauses_json(*cl) -> str:
    return json.dumps({"schema_version": "gnd-ilp-clauses/1", "clauses": list(cl)}, indent=1) + "\n"


cases, answers = [], {}


def run_record(cid: str, clause_path: Path, covered: list, *, export_sha: str, learner=LEARNER,
               coverage=None) -> Path:
    doc = {"schema_version": "gnd-ilp-run/1", "learner": learner, "export_sha256": export_sha,
           "clauses_sha256": sha(clause_path),
           "coverage": coverage if coverage is not None else [
               {"clause": k, "covered": ids} for k, ids in enumerate(covered)]}
    return write(f"{cid.lower()}.run.json", json.dumps(doc, indent=1) + "\n")


def import_case(cid: str, story: str, answer: dict, *, target: str, text: str,
                covered: list, manifest_name: str = "m.labels.json", **run) -> None:
    suffix = "clauses.json" if target == "neutral" else "popper.pl"
    clause_path = write(f"{cid.lower()}.{suffix}", text)
    export_sha = E_NEUTRAL if target == "neutral" else E_POPPER
    run_path = run_record(cid, clause_path, covered, **{"export_sha": export_sha, **run})
    cases.append({"id": cid, "story": story, "command": "import", "target": target,
                  "manifest": manifest_name, "clauses": clause_path.name, "run": run_path.name})
    answers[cid] = answer


def refuse(name: str, clause_index: int | None = None) -> dict:
    answer = {"exit": 3, "refusal": name}
    if clause_index is not None:
        answer["clause"] = clause_index
    return answer


# ---- Export cases (C1) ----
cases.append({"id": "X1", "story": "the Popper export of six labelled populations",
              "command": "export", "target": "popper", "manifest": "m.labels.json"})
answers["X1"] = {"exit": 0, "export_sha256": E_POPPER, "tree": "expected-export/popper"}
cases.append({"id": "X2", "story": "the neutral export alone (finding C-F2)", "command": "export",
              "target": "neutral", "manifest": "m.labels.json"})
answers["X2"] = {"exit": 0, "export_sha256": E_NEUTRAL, "tree": "expected-export/neutral"}
for cid, story, name, answer in [
    ("XE1", "an expected-state manifest carries no classes to learn from", "es.labels.json",
     refuse("expected-state")),
    ("XE2", "a population with a hidden amount cannot be rendered", "opaque.labels.json",
     refuse("opaque")),
    ("XE3", "the output directory already exists", "m.labels.json", {"exit": 11}),
    ("XE4", "the manifest is missing", "absent.labels.json", {"exit": 66}),
    ("XE5", "a population path is a symbolic link", "link.labels.json", {"exit": 74}),
]:
    cases.append({"id": cid, "story": story, "command": "export", "target": "popper",
                  "manifest": name})
    answers[cid] = answer


# ---- Admitted imports (C2, C3, C4) ----
def learned(op: str, right: int | None, k: int, ids: list, method: str, clause_sha: str,
            run_sha: str, export_sha: str, absence: bool = False) -> dict:
    negatives = [i for i in ids if CLASS[i] == "negative"]
    positives = [i for i in ids if CLASS[i] == "positive"]
    consequent = ({"absence": {"fact_type": "order_flagged", "bind": {"order": "$v_b"}}}
                  if absence else
                  {"comparison": {"operator": op, "left": "$v_c", "right": right}})
    return {
        "type": "guarded",
        "antecedent": [{"fact_type": "order_amount", "bind": {"order": "$v_b", "amount": "$v_c"}}],
        "consequent": consequent,
        "source": "induced", "status": "proposed", "modality": "deontic",
        "rationale": (f"learned by popper 0.0.0+authored from manifest {MANIFEST_SHA[:8]}, "
                      f"clause {k}"),
        "provenance": {"induction": {
            "inducer": LEARNER, "method": method, "manifest_sha256": MANIFEST_SHA,
            "examples": negatives, "counterexamples": positives,
            "support": {"numerator": len(negatives), "denominator": len(ids)},
            "evidence": [{"ref": "ilp/export.json", "sha256": export_sha},
                         {"ref": "ilp/clauses", "sha256": clause_sha},
                         {"ref": "ilp/run", "sha256": run_sha}]}},
    }


def admitted(cid: str, story: str, target: str, text: str) -> None:
    import_case(cid, story, {}, target=target, text=text,
                covered=[COVER["A"], COVER["B"], COVER["C"]])
    suffix = "clauses.json" if target == "neutral" else "popper.pl"
    clause_sha = sha(C / f"{cid.lower()}.{suffix}")
    run_sha = sha(C / f"{cid.lower()}.run.json")
    export_sha = E_NEUTRAL if target == "neutral" else E_POPPER
    method = f"ilp-{target}"
    answers[cid] = {"exit": 0, "constraints": [
        learned("<=", 100, 0, COVER["A"], method, clause_sha, run_sha, export_sha),
        learned(None, None, 1, COVER["B"], method, clause_sha, run_sha, export_sha, absence=True),
        learned("<=", 80, 2, COVER["C"], method, clause_sha, run_sha, export_sha),
    ], "vacuous": {"0": ["v1"], "1": ["v1"], "2": ["v1"]}}


admitted("I1", "three learned clauses in the neutral form; every reported set matches",
         "neutral", clauses_json(RULE_A, RULE_B, RULE_C))
admitted("I2", "the same three clauses as Popper prints them", "popper", POPPER_ABC)
cases.append({"id": "I3", "story": "gnd evolve preview of I1's proposal", "command": "preview",
              "from": "I1"})
answers["I3"] = {"exit": 0}
cases.append({"id": "I4", "story": "the proposal path already exists", "command": "import",
              "target": "neutral", "manifest": "m.labels.json", "clauses": "i1.clauses.json",
              "run": "i1.run.json", "out_exists": True})
answers["I4"] = {"exit": 11}

# ---- Set comparison (C3) ----
ABC = clauses_json(RULE_A, RULE_B, RULE_C)
import_case("M1", "rule A reported as covering n1 and n3: the same count, a different set",
            refuse("coverage-mismatch", 0), target="neutral", text=ABC,
            covered=[["n1", "n3"], COVER["B"], COVER["C"]])
import_case("M2", "rule A reported as also covering v1, where GND finds it vacuous",
            refuse("coverage-mismatch", 0), target="neutral", text=ABC,
            covered=[["n1", "n2", "v1"], COVER["B"], COVER["C"]])
import_case("M3", "rule A reported as covering an example the manifest does not list",
            refuse("unknown-example", 0), target="neutral", text=ABC,
            covered=[["n1", "n2", "zz"], COVER["B"], COVER["C"]])
import_case("M4", "a rule that covers nothing at all, reported as covering nothing",
            refuse("covers-nothing", 0), target="neutral",
            text=clauses_json(clause(AMOUNT, compare(">", CV, const(1000)))), covered=[[]])

# ---- Binding (C4) ----
import_case("B1", "the run record names a different export", refuse("export-mismatch"),
            target="neutral", text=ABC, covered=[COVER["A"], COVER["B"], COVER["C"]],
            export_sha="0" * 64)
clause_path = write("b2.clauses.json", ABC)
doc = {"schema_version": "gnd-ilp-run/1", "learner": LEARNER, "export_sha256": E_NEUTRAL,
       "clauses_sha256": "1" * 64,
       "coverage": [{"clause": k, "covered": COVER[r]} for k, r in enumerate("ABC")]}
write("b2.run.json", json.dumps(doc, indent=1) + "\n")
cases.append({"id": "B2", "story": "the run record names different clause bytes",
              "command": "import", "target": "neutral", "manifest": "m.labels.json",
              "clauses": "b2.clauses.json", "run": "b2.run.json"})
answers["B2"] = refuse("clauses-mismatch")
import_case("B3", "a Popper import whose run record names another learner",
            refuse("learner-mismatch"), target="popper", text=POPPER_ABC,
            covered=[COVER["A"], COVER["B"], COVER["C"]],
            learner={"name": "aleph", "version": "5"})
import_case("B4", "the run record leaves clause 1 out", refuse("coverage-shape"),
            target="neutral", text=ABC, covered=[],
            coverage=[{"clause": 0, "covered": COVER["A"]}, {"clause": 2, "covered": COVER["C"]}])
import_case("B5", "the run record lists clause 0 twice", refuse("coverage-shape"),
            target="neutral", text=ABC, covered=[],
            coverage=[{"clause": 0, "covered": COVER["A"]}, {"clause": 0, "covered": COVER["A"]},
                      {"clause": 1, "covered": COVER["B"]}, {"clause": 2, "covered": COVER["C"]}])

# ---- The fragment (C2): one case per refusal name ----
FRAGMENT = [
    ("F01", "head-shape", "a head with two arguments",
     "wrong(A,B):- f_order_amount(A,B,C),gt_t_amount(C,100).\n"),
    ("F02", "negation-as-failure", "a negated atom, as Popper would print it",
     "wrong(A):- f_order_amount(A,B,C),\\+ f_order_flagged(A,B).\n"),
    ("F04", "disjunction", "a disjunction inside the body",
     "wrong(A):- f_order_amount(A,B,C),(gt_t_amount(C,100);f_order_flagged(A,B)).\n"),
    ("F06", "aggregate", "a count over another relation",
     "wrong(A):- f_order_by(A,B,C),aggregate_all(count,f_order_amount(A,B,D),N),N > 1.\n"),
    ("F08", "unknown-predicate", "a predicate the export never declared",
     "wrong(A):- f_order_amount(A,B,C),f_order_total(A,B,D).\n"),
    ("F09", "arity", "the amount relation with one role missing",
     "wrong(A):- f_order_amount(A,B),f_order_flagged(A,B).\n"),
    ("F10", "recursion", "the head predicate used in its own body",
     "wrong(A):- f_order_amount(A,B,C),wrong(A).\n"),
    ("F11", "example-variable", "an atom whose first argument is not the example",
     "wrong(A):- f_order_amount(B,A,C),gt_t_amount(C,100).\n"),
    ("F12", "multiple-comparisons", "two comparisons, which a guarded antecedent cannot hold",
     "wrong(A):- f_order_amount(A,B,C),gt_t_amount(C,100),lt_t_amount(C,500).\n"),
    ("F13", "comparison-type", "a comparison over customer codes, which are not integers",
     "wrong(A):- f_order_by(A,B,C),C > 'c1'.\n"),
    ("F14", "non-ground-absence", "two atoms sharing no variable, so neither can be the absence",
     "wrong(A):- f_order_by(A,B,C),f_order_amount(A,D,E).\n"),
    ("F15", "empty-antecedent", "one ground atom and nothing else",
     "wrong(A):- f_order_flagged(A,8).\n"),
    ("F16", "disconnected-body", "a comparison over an antecedent of two unjoined atoms",
     "wrong(A):- f_order_amount(A,B,C),f_customer_blocked(A,D),gt_t_amount(C,100).\n"),
    ("F17", "unbound-comparison", "a comparison over a variable no atom binds",
     "wrong(A):- f_order_amount(A,B,C),gt_t_amount(D,100).\n"),
    ("F18", "constant-spelling", "a constant that guarded would read as a variable",
     "wrong(A):- f_order_by(A,B,'$x'),f_order_flagged(A,B).\n"),
    ("F19", "invalid-guarded", "an amount compared with a string, refused by the validator",
     "wrong(A):- f_order_amount(A,B,C),gt_t_amount(C,'x').\n"),
    ("F20", "unparsable", "a missing comma between two literals",
     "wrong(A):- f_order_amount(A,B,C) gt_t_amount(C,1).\n"),
]
for cid, name, story, text in FRAGMENT:
    import_case(cid, story, refuse(name, None if name == "unparsable" else 0),
                target="popper", text=text, covered=[[]])
NEUTRAL_FRAGMENT = [
    ("F03", "negation-as-failure", "a not literal in the neutral form",
     clause(AMOUNT, {"not": atom("f_order_flagged", A, B)})),
    ("F05", "disjunction", "an or literal in the neutral form",
     clause(AMOUNT, {"or": [[compare(">", CV, const(100))], [atom("f_order_flagged", A, B)]]})),
    ("F07", "aggregate", "an aggregate literal in the neutral form",
     clause(AMOUNT, {"aggregate": {"name": "count", "args": [atom("f_order_flagged", A, B),
                                                              var("N")]}})),
]
for cid, name, story, cl in NEUTRAL_FRAGMENT:
    import_case(cid, story, refuse(name, 0), target="neutral", text=clauses_json(cl),
                covered=[[]])

cases.sort(key=lambda case: (case["id"][0] != "X", case["id"][0] != "I", case["id"]))
write("cases.json", json.dumps({"version": 1, "model": MODEL, "cases": cases}, indent=1) + "\n")
write("expected.json", json.dumps({
    "version": 1,
    "note": ("Hand-written from spec r1. Constraints are the exact guarded constraints the "
             "proposal adds, in clause order; refusals name the spec's construct or binding "
             "reason and, for fragment refusals, the clause index."),
    "export_sha256": {"popper": E_POPPER, "neutral": E_NEUTRAL},
    "cases": answers}, indent=1) + "\n")
print(f"{len(cases)} cases; E popper {E_POPPER[:12]}, E neutral {E_NEUTRAL[:12]}")
