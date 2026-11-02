"""WN1 T9: the kernel agrees with an independent oracle on a discriminating corpus."""

from __future__ import annotations

import ast
import json
import random
from pathlib import Path

import jsonschema
import pytest

from gnd.model import ModelValidationError
from gnd.witness import why_not
from gnd.witness.why_not import WhyNotLimits, explain
from tests.test_why_not_kernel import CASES, NEAR, _misplaced_near_keys, check_status, spelled
from tests.why_not_oracle import Oracle, canonical, identity
from tests.why_not_support import atom, build, cells, fact_type, population

ORACLE = Path(__file__).with_name("why_not_oracle.py")
BANNED = ("gnd.extensions", "gnd.terms", "gnd.values", "gnd.checker", "gnd.witness")


def test_oracle_imports_nothing_from_the_kernel_side():
    tree = ast.parse(ORACLE.read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
    assert not [name for name in imported if name == "gnd" or name.startswith("gnd.")]
    assert not [name for name in imported if name.startswith(BANNED)]


def _samples_identity(samples):
    return [tuple(sorted((role, identity(value)) for role, value in s.items())) for s in samples]


def compare(model, doc, pop, pdoc, target, row=None):
    """Assert kernel and oracle agree on status, steps and the blocker record."""
    ours = explain(model, pop, target, row=row).to_dict()
    oracle = Oracle(doc, pdoc["facts"])
    assert (ours["status"] == "derived") == oracle.derived(target, row)
    # Close review C2-1: every corpus case also agrees with check's verdict.
    expected = check_status(model, pop, target, row)
    assert expected is not None and ours["status"] == expected
    if ours["status"] != "blocked":
        return ours
    for got, want in zip(ours["clauses"], oracle.walk(target, row), strict=True):
        assert got["steps"] == want["steps"]
        blocker, expected = got["blocker"], want["blocker"]
        assert expected is not None
        if expected["kind"] != "atom":
            assert {k: blocker[k] for k in ("kind", "index", "count")} == {
                k: expected[k] for k in ("kind", "index", "count")
            }
            continue
        for key in ("kind", "index", "fact_type", "derivation", "ground", "roles", "sample_count"):
            assert blocker[key] == expected[key], key
        assert _samples_identity(blocker["samples"]) == _samples_identity(expected["samples"])
    return ours


def case(fts, facts, target, row=None):
    model, doc = build(fts)
    pop, pdoc = population(model, doc, facts)
    return compare(model, doc, pop, pdoc, target, row)


# -- named discriminators, each with its census property ------------------------

def test_identity_duplicates_count_once():
    fts = [fact_type("r", [("v", "num")]), fact_type("s", [("v", "num")]),
           fact_type("t", [("v", "num")], {"body": [atom("r", v="$x"), atom("s", v="$x")], "head": {"v": "$x"}})]
    rows = [{"v": 1}, {"v": 1.0}, {"v": 1}, {"v": 2}]
    result = case(fts, {"r": rows, "s": []}, "t")
    assert len(rows) > result["clauses"][0]["steps"][0]["count"] == 2


def test_boolean_and_number_stay_apart():
    # Python equates True and 1; GND identity does not. A shared variable across
    # Boolean and Number roles is refused by validation, so the buildable form is
    # a constant of the other domain in the atom.
    assert hash(True) == hash(1) and identity(True) != identity(1)
    for name, ot, constant, rows in (
        ("n", "num", True, [{"k": "a", "v": 1}]),
        ("b", "flag", 1, [{"k": "a", "v": True}]),
    ):
        fts = [fact_type(name, [("k", "code"), ("v", ot)]),
               fact_type("t", [("k", "code")], {"body": [atom(name, k="$k", v=constant)], "head": {"k": "$k"}})]
        result = case(fts, {name: rows}, "t")
        assert result["clauses"][0]["steps"] == [{"kind": "atom", "index": 0, "fact_type": name, "count": 0}]
        assert result["clauses"][0]["blocker"]["roles"]["v"] == {"constant": constant}


def test_declared_order_differs_from_the_evaluator_order():
    rule = {"body": [atom("a1", x="$x"), atom("a2", y="$y"), atom("a3", x="$x", y="$y")], "head": {"x": "$x"}}
    fts = [fact_type("a1", [("x", "code")]), fact_type("a2", [("y", "code")]),
           fact_type("a3", [("x", "code"), ("y", "code")]), fact_type("t", [("x", "code")], rule)]
    # The evaluator's rule (extensions.py:710-725): start at atom 0, then take the
    # earliest remaining atom sharing a bound variable.
    variables = [set(a["bind"].values()) for a in rule["body"]]
    order, bound, remaining = [0], set(variables[0]), [1, 2]
    while remaining:
        nxt = next(i for i in remaining if variables[i] & bound)
        order.append(nxt)
        bound |= variables[nxt]
        remaining.remove(nxt)
    assert order != [0, 1, 2]
    result = case(fts, {"a1": [{"x": "p"}, {"x": "q"}], "a2": [{"y": "r"}], "a3": []}, "t")
    assert [s["count"] for s in result["clauses"][0]["steps"]] == [2, 2, 0]


def test_constants_repeated_and_shared_variables():
    fts = [fact_type("e", [("a", "code"), ("b", "code")]),
           fact_type("loopy", [("a", "code")], {"body": [atom("e", a="$x", b="$x"), atom("e", a="$x", b="k")], "head": {"a": "$x"}})]
    facts = {"e": [{"a": "m", "b": "m"}, {"a": "n", "b": "o"}, {"a": "o", "b": "k"}]}
    rule = fts[1]["derivation_rule"]
    assert rule["body"][0]["bind"]["a"] == rule["body"][0]["bind"]["b"]
    assert "k" in rule["body"][1]["bind"].values()
    result = case(fts, facts, "loopy")
    assert [s["count"] for s in result["clauses"][0]["steps"]] == [1, 0]


def test_negation_and_comparison_empty_everything():
    fts = [fact_type("s", [("q", "code"), ("n", "int")]), fact_type("x", [("q", "code")]),
           fact_type("neg", [("q", "code")], {"body": [atom("s", q="$q", n="$n")], "negate": [atom("x", q="$q")], "head": {"q": "$q"}}),
           fact_type("cmp", [("q", "code")], {"body": [atom("s", q="$q", n="$n")], "where": [{"operator": "<", "left": "$n", "right": 0}], "head": {"q": "$q"}})]
    facts = {"s": [{"q": "a", "n": 1}], "x": [{"q": "a"}]}
    assert case(fts, facts, "neg")["clauses"][0]["blocker"]["kind"] == "negated"
    assert case(fts, facts, "cmp")["clauses"][0]["blocker"]["kind"] == "comparison"


def test_two_clauses_with_different_blockers():
    rule = {"head": {"q": "$q"}, "clauses": [{"body": [atom("x", q="$q")]},
                                             {"body": [atom("s", q="$q", n="$n"), atom("x", q="$q")]}]}
    fts = [fact_type("s", [("q", "code"), ("n", "int")]), fact_type("x", [("q", "code")]), fact_type("t", [("q", "code")], rule)]
    result = case(fts, {"s": [{"q": "a", "n": 1}], "x": []}, "t")
    assert [c["blocker"]["index"] for c in result["clauses"]] == [0, 1]


def test_derived_and_recursive_body_predicates():
    m = fact_type("m", [("v", "code")], {"body": [atom("b", v="$x")], "head": {"v": "$x"}})
    t = fact_type("t", [("v", "code")], {"body": [atom("m", v="$x"), atom("c", v="$x")], "head": {"v": "$x"}})
    fts = [fact_type("b", [("v", "code")]), fact_type("c", [("v", "code")]), m, t]
    facts = {"b": [{"v": "a"}], "c": []}
    model, doc = build(fts)
    pop, pdoc = population(model, doc, facts)
    assert Oracle(doc, pdoc["facts"]).rounds >= 2
    compare(model, doc, pop, pdoc, "t")
    rule = {"head": {"x": "$x", "z": "$z"}, "clauses": [
        {"body": [atom("e", x="$x", z="$z")]},
        {"body": [atom("e", x="$x", z="$y"), atom("reach", x="$y", z="$z")]}]}
    fts = [fact_type("e", [("x", "code"), ("z", "code")]), fact_type("reach", [("x", "code"), ("z", "code")], rule)]
    facts = {"e": [{"x": "a", "z": "b"}, {"x": "b", "z": "c"}, {"x": "c", "z": "d"}]}
    model, doc = build(fts)
    pop, pdoc = population(model, doc, facts)
    assert Oracle(doc, pdoc["facts"]).rounds >= 3
    compare(model, doc, pop, pdoc, "reach", cells(("String", "a"), ("String", "z")))


# -- the generated corpus ---------------------------------------------------------

DOMAINS = {"code": ["a", "b", "c"], "int": [0, 1, 2, 3]}
PRIMITIVE = {"code": "String", "int": "Integer"}


def generate(seed, domains=DOMAINS):
    rng = random.Random(seed)
    bases = []
    for i in range(3):
        types = [rng.choice(["code", "int"]) for _ in range(rng.randint(1, 2))]
        bases.append((f"r{i}", [(f"c{j}", t) for j, t in enumerate(types)]))
    fts = [fact_type(name, roles) for name, roles in bases]
    facts = {
        name: [{role: rng.choice(domains[t]) for role, t in roles} for _ in range(rng.randint(0, 12))]
        for name, roles in bases
    }
    relations = list(bases)
    if rng.random() < 0.3:
        name, roles = bases[0]
        fts.append(fact_type("m", roles, {"body": [atom(name, **{r: f"$v{k}" for k, (r, _) in enumerate(roles)})],
                                         "head": {r: f"$v{k}" for k, (r, _) in enumerate(roles)}}))
        relations.append(("m", roles))
    var_types, body = {}, []
    for _ in range(rng.randint(1, 4)):
        name, roles = rng.choice(relations)
        bind = {}
        for position, (role, t) in enumerate(roles):
            # Every atom keeps at least one variable, so its component can feed the head.
            if position and rng.random() < 0.1:
                bind[role] = rng.choice(domains[t])
                continue
            same = [v for v, vt in var_types.items() if vt == t]
            if same and rng.random() < 0.6:
                bind[role] = "$" + rng.choice(same)
            else:
                fresh = f"x{len(var_types)}"
                var_types[fresh] = t
                bind[role] = "$" + fresh
        body.append({"fact_type": name, "bind": bind})
    if not var_types:
        return None
    rule = {"body": body}
    if rng.random() < 0.25:
        name, roles = rng.choice(bases)
        typed = {t: [v for v, vt in var_types.items() if vt == t] for t in domains}
        if all(typed[t] for _, t in roles):
            rule["negate"] = [{"fact_type": name, "bind": {r: "$" + rng.choice(typed[t]) for r, t in roles}}]
    ints = [v for v, t in var_types.items() if t == "int"]
    if ints and rng.random() < 0.3:
        rule["where"] = [{"operator": rng.choice(["<", "<=", ">", ">=", "=", "!="]), "left": "$" + rng.choice(ints), "right": rng.randint(0, 3)}]
    # Every variable reaches the head: validation refuses a body component that
    # feeds no head role.
    head_vars = sorted(var_types)
    rule["head"] = {f"h{i}": "$" + v for i, v in enumerate(head_vars)}
    fts.append(fact_type("t", [(f"h{i}", var_types[v]) for i, v in enumerate(head_vars)], rule))
    row = [{"primitive": PRIMITIVE[var_types[v]], "value": rng.choice(domains[var_types[v]])} for v in head_vars]
    return fts, facts, row


def test_generated_corpus_agrees_with_the_oracle():
    valid = blocked = 0
    for seed in range(200):
        generated = generate(seed)
        if generated is None:
            continue
        fts, facts, row = generated
        try:
            model, doc = build(fts)
        except ModelValidationError:
            continue
        pop, pdoc = population(model, doc, facts)
        valid += 1
        for target_row in (None, row):
            result = compare(model, doc, pop, pdoc, "t", target_row)
            blocked += result["status"] == "blocked"
    assert valid >= 150
    assert blocked >= 100


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_generator_is_deterministic(seed):
    assert generate(seed) == generate(seed)


# -- NM1: near-misses against the oracle (why-not-near-misses NM1 spec) -------------

# Measured on the first run (recorded in the NM1 phase record); the generator
# is deterministic and SPELLING is ASCII, so the census is exact.
NONZERO_FLOOR, TRUNCATED_FLOOR = 46, 15
SPELLING = {"code": ["a", "A", "a.", " a ", "b", "B-", "c"], "int": [0, 1, 2, 3]}


def strip_near(value):
    if isinstance(value, dict):
        return {k: strip_near(v) for k, v in value.items() if k not in NEAR}
    if isinstance(value, list):
        return [strip_near(v) for v in value]
    return value


def atom_blockers(result):
    for clause in result["clauses"]:
        if clause["blocker"]["kind"] == "atom":
            yield clause["blocker"]
        if clause["descent"] is not None:
            yield from atom_blockers(clause["descent"])


def compare_near(model, doc, pop, pdoc, target, row=None, limits=None):
    """T9 plus the NM1 comparison rule; returns the top-level atom blockers."""
    kwargs = {"limits": limits} if limits is not None else {}
    ours = explain(model, pop, target, row=row, near_misses=True, **kwargs).to_dict()
    plain = explain(model, pop, target, row=row, **kwargs).to_dict()
    assert strip_near(ours) == plain
    assert not list(_misplaced_near_keys(ours))
    for blocker in atom_blockers(ours):
        assert set(NEAR) <= set(blocker)
    if ours["status"] != "blocked":
        return []
    blockers = []
    walked = Oracle(doc, pdoc["facts"]).walk(target, row, near_misses=True)
    for got, want in zip(ours["clauses"], walked, strict=True):
        got, want = got["blocker"], want["blocker"]
        if want["kind"] != "atom":
            continue
        assert want["near_miss_truncated"] is False
        if got["near_miss_truncated"]:
            assert got["near_miss_count"] <= want["near_miss_count"]
            every = {canonical(pair) for pair in want["all_near_misses"]}
            assert {canonical(pair) for pair in got["near_misses"]} <= every
        else:
            assert got["near_miss_count"] == want["near_miss_count"]
            assert canonical(got["near_misses"]) == canonical(want["near_misses"])
        blockers.append(got)
    return blockers


@pytest.mark.parametrize("name", [n for n in CASES if n != "T4"])
def test_nm1_t17_hand_written_cases_agree(name):
    fts, facts, target, row, limits = CASES[name]
    model, doc = build(fts)
    pop, pdoc = population(model, doc, facts)
    (blocker,) = compare_near(model, doc, pop, pdoc, target, row, limits)
    assert blocker["near_miss_truncated"] is False


def test_nm1_t17_descent_top_level_agrees():
    fts, facts, target, row, limits = CASES["T4"]
    model, doc = build(fts)
    pop, pdoc = population(model, doc, facts)
    assert compare_near(model, doc, pop, pdoc, target, row, limits)[0]["near_miss_count"] == 1


@pytest.mark.parametrize("name,cap", [("T12", 4), ("T12b", 199)])
def test_nm1_t17b_truncated_hand_written_cases_are_subsets(name, cap):
    fts, facts, target, row, _limits = CASES[name]
    model, doc = build(fts)
    pop, pdoc = population(model, doc, facts)
    (blocker,) = compare_near(model, doc, pop, pdoc, target, row, WhyNotLimits(near_miss_inspections=cap))
    assert blocker["near_miss_truncated"] is True and blocker["near_misses"]


def _spelling_corpus():
    for seed in range(200):
        generated = generate(seed, SPELLING)
        if generated is None:
            continue
        fts, facts, row = generated
        try:
            model, doc = build(fts)
        except ModelValidationError:
            continue
        pop, pdoc = population(model, doc, facts)
        yield model, doc, pop, pdoc, row


def test_nm1_t18_spelling_corpus_agrees():
    nonzero = 0
    for model, doc, pop, pdoc, row in _spelling_corpus():
        compare(model, doc, pop, pdoc, "t", None)
        for target_row in (None, row):
            blockers = compare_near(model, doc, pop, pdoc, "t", target_row)
            nonzero += sum(b["near_miss_count"] > 0 for b in blockers)
    assert nonzero >= NONZERO_FLOOR


def test_nm1_t18b_truncated_reports_are_lower_bounds():
    truncated = 0
    limits = WhyNotLimits(near_miss_inspections=3)
    for model, doc, pop, pdoc, _row in _spelling_corpus():
        blockers = compare_near(model, doc, pop, pdoc, "t", None, limits)
        truncated += sum(b["near_miss_truncated"] for b in blockers)
    # None of these truncated reports carries a pair (bindings are inspected
    # first); T17b exercises the subset half with content (NM1 finding F2).
    assert truncated >= TRUNCATED_FLOOR


def test_nm1_t9_flag_is_inert_on_the_original_corpus():
    for seed in range(200):
        generated = generate(seed)
        if generated is None:
            continue
        fts, facts, row = generated
        try:
            model, doc = build(fts)
        except ModelValidationError:
            continue
        pop, _ = population(model, doc, facts)
        for target_row in (None, row):
            ours = explain(model, pop, "t", row=target_row, near_misses=True).to_dict()
            assert strip_near(ours) == explain(model, pop, "t", row=target_row).to_dict()
            assert not list(_misplaced_near_keys(ours))


def test_nm1_t19_eligibility_equals_production_with_nothing_bound(monkeypatch):
    walks = []
    original = why_not._Walk.explain

    def capture(self, *args, **kwargs):
        walks.append(self)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(why_not._Walk, "explain", capture)
    atoms = 0
    for generated in (generate(seed, d) for seed in range(200) for d in (DOMAINS, SPELLING)):
        if generated is None:
            continue
        fts, facts, _row = generated
        try:
            model, doc = build(fts)
        except ModelValidationError:
            continue
        pop, _ = population(model, doc, facts)
        walks.clear()
        explain(model, pop, "t")
        walk = walks[0]
        for body_atom in doc["fact_types"][-1]["derivation_rule"]["body"]:
            variables = {
                role: term[1:] for role, term in body_atom["bind"].items()
                if isinstance(term, str) and term.startswith("$")
            }
            ours = {
                why_not._binding_key({name: fact[role] for role, name in variables.items()})
                for fact in walk._eligible_rows(body_atom, frozenset())
            }
            theirs = {why_not._binding_key(c) for c in walk._candidates(body_atom)}
            assert ours == theirs
            atoms += 1
    assert atoms >= 300


# Measured on the first run (NM1 review R4); the census is exact.
TRUNCATED_WITH_PAIRS_FLOOR = 3


def test_nm1_review_r4_truncated_reports_with_content_are_subsets():
    with_pairs = 0
    corpus = list(_spelling_corpus())
    for cap in (4, 5, 6):
        for model, doc, pop, pdoc, _row in corpus:
            blockers = compare_near(model, doc, pop, pdoc, "t", None, WhyNotLimits(near_miss_inspections=cap))
            with_pairs += sum(b["near_miss_truncated"] and bool(b["near_misses"]) for b in blockers)
    assert with_pairs >= TRUNCATED_WITH_PAIRS_FLOOR


@pytest.mark.parametrize("n", [200, 400])
def test_nm1_review_r6_larger_spelled_cases_agree(n):
    fts, facts = spelled(n)
    model, doc = build(fts)
    pop, pdoc = population(model, doc, facts)
    (blocker,) = compare_near(model, doc, pop, pdoc, "t")
    assert blocker["near_miss_count"] == n * n


def test_nm3_t13_kernel_reports_validate_against_the_v2_blocker():
    """NM3 T13 (D2): every T18 report satisfies the /2 blocker rule, count tie included."""
    schema = json.loads((Path(__file__).resolve().parents[1]
                         / "src/gnd/why-not.schema.json").read_text())
    validator = jsonschema.Draft202012Validator(
        {"$defs": schema["$defs"], "$ref": "#/$defs/blocker"})
    nonzero = 0
    for model, _doc, pop, _pdoc, row in _spelling_corpus():
        for target_row in (None, row):
            result = explain(model, pop, "t", row=target_row, near_misses=True).to_dict()
            for blocker in atom_blockers(result):
                validator.validate(blocker)
                nonzero += blocker["near_miss_count"] > 0
    assert nonzero >= NONZERO_FLOOR
