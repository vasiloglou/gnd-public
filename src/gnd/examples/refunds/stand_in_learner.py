"""A stand-in rule learner for the refunds tutorial. It is not a GND command and not Popper.

Usage: python stand_in_learner.py EXPORT_DIR OUT_DIR [--also-claim BATCH]

--also-claim plays a faulty learner: it adds BATCH to what the first rule is
claimed to cover, so the tutorial can show GND refusing a claim it cannot
reproduce.

It reads the learner-neutral export that `gnd export ilp --target neutral` wrote
to EXPORT_DIR/neutral.json, and searches a small, fixed space of rules for
"this batch is wrong":

    wrong(A) :- P(A, ...), V > t     V an integer argument of P, t a value seen for it
    wrong(A) :- P(A, ...), V < t
    wrong(A) :- P(A, ...), Q(A, ...)  every argument of Q joined to one of P's

It keeps rules that hold in at least one flagged batch and in no clean batch,
then picks a small program by greedy cover. It writes two files to OUT_DIR:

- learned.clauses.json: the rules, in GND's neutral clause form (gnd-ilp-clauses/1);
- learned.run.json: what this learner claims each rule covers (gnd-ilp-run/1).

The coverage is this program's own claim. `gnd import ilp-rules` does not trust
it: GND re-evaluates every rule and refuses the import if the sets differ.
Standard library only; the output depends only on the export's bytes.
"""

import hashlib
import json
import sys
from pathlib import Path

NAME, VERSION = "refunds-stand-in-learner", "1"
OPERATORS = {">": lambda value, bound: value > bound, "<": lambda value, bound: value < bound}


def load(export: Path):
    neutral = json.loads((export / "neutral.json").read_text(encoding="utf-8"))
    rows: dict[tuple[str, str], list[list]] = {}
    for fact in neutral["facts"]:
        rows.setdefault((fact["example"], fact["predicate"]), []).append(fact["values"])
    integer = {t["name"] for t in neutral["types"] if t["primitive"] == "integer"}
    predicates = {p["name"]: p["types"][1:] for p in neutral["predicates"]}
    return neutral, rows, integer, predicates


def atom(predicate: str, names: list[str]) -> dict:
    return {"atom": {"predicate": predicate, "args": [{"var": "A"}] + [{"var": n} for n in names]}}


def candidates(rows, integer, predicates):
    """Yield (text, clause, covers) for every rule in the search space, in a fixed order."""
    head = {"predicate": "wrong", "args": [{"var": "A"}]}
    for p, p_types in sorted(predicates.items()):
        names = [f"V{i}" for i in range(len(p_types))]
        for i, t in enumerate(p_types):
            if t not in integer:
                continue
            seen = sorted({row[i] for (_, q), found in rows.items() if q == p for row in found})
            for op in OPERATORS:
                for bound in seen:
                    def covers(example, p=p, i=i, op=op, bound=bound):
                        return any(OPERATORS[op](row[i], bound) for row in rows.get((example, p), []))
                    clause = {"head": head, "body": [atom(p, names), {"compare": {
                        "operator": op, "left": {"var": names[i]}, "right": {"const": bound}}}]}
                    yield f"wrong(A) :- {p}(A,{','.join(names)}), {names[i]} {op} {bound}", clause, covers
        for q, q_types in sorted(predicates.items()):
            if q == p:
                continue
            joins = [p_types.index(t) for t in q_types if t in p_types]
            if len(joins) != len(q_types):
                continue
            def covers(example, p=p, q=q, joins=tuple(joins)):
                wanted = {tuple(row) for row in rows.get((example, q), [])}
                return any(tuple(row[j] for j in joins) in wanted for row in rows.get((example, p), []))
            q_names = [names[j] for j in joins]
            clause = {"head": head, "body": [atom(p, names), atom(q, q_names)]}
            yield f"wrong(A) :- {p}(A,{','.join(names)}), {q}(A,{','.join(q_names)})", clause, covers


def main() -> None:
    export, out = Path(sys.argv[1]), Path(sys.argv[2])
    extra = sys.argv[4] if sys.argv[3:4] == ["--also-claim"] else None
    neutral, rows, integer, predicates = load(export)
    flagged = [e["id"] for e in neutral["examples"] if e["label"] == "pos"]
    clean = [e["id"] for e in neutral["examples"] if e["label"] == "neg"]
    searched, kept = 0, []
    for text, clause, covers in candidates(rows, integer, predicates):
        searched += 1
        hits = [e for e in flagged if covers(e)]
        if hits and not any(covers(e) for e in clean):
            kept.append((text, clause, covers, hits))
    print(f"searched {searched} rules; {len(kept)} hold in some flagged batch and in no clean one")
    program, uncovered = [], set(flagged)
    while uncovered and kept:
        best = max(kept, key=lambda k: (len(uncovered & set(k[3])), -kept.index(k)))
        if not uncovered & set(best[3]):
            break
        program.append(best)
        uncovered -= set(best[3])
    for text, _, _, hits in program:
        print(f"learned: {text}   covers {', '.join(hits)}")
    out.mkdir(parents=True, exist_ok=True)
    clauses_path = out / "learned.clauses.json"
    clauses = {"schema_version": "gnd-ilp-clauses/1", "clauses": [k[1] for k in program]}
    clauses_path.write_text(json.dumps(clauses, indent=1) + "\n", encoding="utf-8")
    examples = [e["id"] for e in neutral["examples"]]
    coverage = [{"clause": k, "covered": [e for e in examples if covers(e) or (k == 0 and e == extra)]}
                for k, (_, _, covers, _) in enumerate(program)]
    if extra:
        print(f"deliberate mistake: also claiming that rule 0 covers {extra}")
    run = {
        "schema_version": "gnd-ilp-run/1",
        "learner": {"name": NAME, "version": VERSION},
        "export_sha256": hashlib.sha256((export / "export.json").read_bytes()).hexdigest(),
        "clauses_sha256": hashlib.sha256(clauses_path.read_bytes()).hexdigest(),
        "coverage": coverage,
    }
    (out / "learned.run.json").write_text(json.dumps(run, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
