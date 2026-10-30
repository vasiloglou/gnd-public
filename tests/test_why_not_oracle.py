"""WN1 T9: the kernel agrees with an independent oracle on a discriminating corpus."""

from __future__ import annotations

import ast
import random
from pathlib import Path

import pytest

from gnd.model import ModelValidationError
from gnd.witness.why_not import explain
from tests.test_why_not_kernel import check_status
from tests.why_not_oracle import Oracle, identity
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


def generate(seed):
    rng = random.Random(seed)
    bases = []
    for i in range(3):
        types = [rng.choice(["code", "int"]) for _ in range(rng.randint(1, 2))]
        bases.append((f"r{i}", [(f"c{j}", t) for j, t in enumerate(types)]))
    fts = [fact_type(name, roles) for name, roles in bases]
    facts = {
        name: [{role: rng.choice(DOMAINS[t]) for role, t in roles} for _ in range(rng.randint(0, 12))]
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
                bind[role] = rng.choice(DOMAINS[t])
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
        typed = {t: [v for v, vt in var_types.items() if vt == t] for t in DOMAINS}
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
    row = [{"primitive": PRIMITIVE[var_types[v]], "value": rng.choice(DOMAINS[var_types[v]])} for v in head_vars]
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
