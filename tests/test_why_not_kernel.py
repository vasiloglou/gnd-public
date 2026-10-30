"""WN1: the why-not kernel (spec notes/phase-WN1-spec.md, section 8)."""

from __future__ import annotations

import pytest

from gnd import checker
from gnd.witness import why_not
from gnd.witness.why_not import (
    WhyNotInputError,
    WhyNotInternalError,
    WhyNotLimits,
    WhyNotWorkError,
    explain,
)
from tests.why_not_support import atom, build, cells, fact_type, population, strings

DIV = {"fn": "div", "args": [1, "$a"]}


# -- fixtures -----------------------------------------------------------------

def claim_model(extra=(), author_rows=None, quote_rows=None):
    fts = [
        fact_type("quote", [("q", "code"), ("work", "code")]),
        fact_type("author", [("work", "code"), ("person", "code")]),
        fact_type("claim", [("q", "code"), ("person", "code")], {
            "body": [atom("quote", q="$q", work="$w"), atom("author", work="$w", person="$p")],
            "head": {"q": "$q", "person": "$p"},
        }),
        *extra,
    ]
    model, doc = build(fts)
    facts = {
        "quote": quote_rows if quote_rows is not None else [{"q": "q1", "work": "w1"}, {"q": "q2", "work": "w2"}],
        "author": author_rows if author_rows is not None else [{"work": "w9", "person": "x"}],
    }
    pop, pdoc = population(model, doc, facts)
    return model, pop, doc, pdoc


def run(fts, facts, target, row=None, **kwargs):
    model, doc = build(fts)
    pop, _ = population(model, doc, facts)
    return explain(model, pop, target, row=row, **kwargs).to_dict()


PRICE = {"price": [{"item": "x", "amount": 1.0}, {"item": "y", "amount": 0.0}]}


def unavailable_cases():
    body = [atom("price", item="$i", amount="$a")]
    ok = fact_type("ok", [("item", "code")], {"body": body, "where": [{"operator": ">", "left": DIV, "right": 0}], "head": {"item": "$i"}})
    yield "own-comparison", [fact_type("price", [("item", "code"), ("amount", "num")]), ok], PRICE, "ok"
    yield "computed-head", [
        fact_type("price", [("item", "code"), ("amount", "num")]),
        fact_type("inv", [("item", "code"), ("value", "num")], {"body": body, "head": {"item": "$i", "value": {"fn": "round", "args": [DIV, 2]}}}),
    ], PRICE, "inv"
    # A non-integral head cannot reach the exact path from a validated model
    # (WN1 finding F3): the validator requires round, and a rounded value derives.
    top = fact_type("top", [("item", "code")], {"body": [atom("ok", item="$i")], "head": {"item": "$i"}})
    yield "positive-dependency", [fact_type("price", [("item", "code"), ("amount", "num")]), ok, top], PRICE, "top"
    neg = fact_type("neg", [("item", "code")], {"body": body, "negate": [atom("ok", item="$i")], "head": {"item": "$i"}})
    yield "negated-dependency", [fact_type("price", [("item", "code"), ("amount", "num")]), ok, neg], PRICE, "neg"
    two = fact_type("two", [("item", "code")], {"head": {"item": "$i"}, "clauses": [
        {"body": body}, {"body": body, "where": [{"operator": ">", "left": DIV, "right": 0}]}]})
    yield "two-clause", [fact_type("price", [("item", "code"), ("amount", "num")]), two], PRICE, "two"


# -- T1: status first ---------------------------------------------------------

@pytest.mark.parametrize("name,fts,facts,target", list(unavailable_cases()), ids=lambda v: v if isinstance(v, str) else "")
def test_t1_unavailable_comes_from_production(name, fts, facts, target):
    result = run(fts, facts, target)
    assert result["status"] == "unavailable", name
    assert result["unavailable"]["reason"].startswith("term:")
    assert result["clauses"] == []
    if name in {"positive-dependency", "negated-dependency"}:
        assert result["unavailable"]["source_relation"] == "ok"
    # A row that a seeded walk would derive is still unavailable.
    row = cells(("String", "x")) if target in {"ok", "top", "neg", "two"} else None
    if row is not None:
        assert run(fts, facts, target, row=row)["status"] == "unavailable"


# -- T2..T6: the walk ---------------------------------------------------------

def test_t2_second_atom_blocks():
    model, pop, _, _ = claim_model()
    result = explain(model, pop, "claim").to_dict()
    assert result["status"] == "blocked" and result["mode"] == "rule" and result["order"] == "declared"
    (clause,) = result["clauses"]
    assert [s["count"] for s in clause["steps"]] == [2, 0]
    blocker = clause["blocker"]
    assert blocker == {
        "kind": "atom", "index": 1, "fact_type": "author", "derivation": "base",
        "ground": False, "asserted_not_read": False,
        "roles": {"work": {"variable": "$w", "bound": True}, "person": {"variable": "$p", "bound": False}},
        "sample_count": 2, "samples": [{"work": "w1"}, {"work": "w2"}],
    }
    assert clause["steps_after_blocker"] == "not-evaluated"
    assert clause["descent_stopped"] == "not-derived"


def test_t3_first_atom_empty_and_constant_filter():
    model, pop, _, _ = claim_model(quote_rows=[])
    clause = explain(model, pop, "claim").to_dict()["clauses"][0]
    assert [s["count"] for s in clause["steps"]] == [0]
    assert clause["blocker"]["index"] == 0 and clause["blocker"]["sample_count"] == 1
    fts = [
        fact_type("quote", [("q", "code"), ("work", "code")]),
        fact_type("pinned", [("q", "code")], {"body": [atom("quote", q="$q", work="w9")], "head": {"q": "$q"}}),
    ]
    clause = run(fts, {"quote": [{"q": "q1", "work": "w1"}]}, "pinned")["clauses"][0]
    assert clause["blocker"]["roles"]["work"] == {"constant": "w9"}
    assert clause["blocker"]["index"] == 0


def test_t4_negation_removes_everything():
    fts = [
        fact_type("quote", [("q", "code"), ("work", "code")]),
        fact_type("banned", [("q", "code")]),
        fact_type("ok", [("q", "code")], {"body": [atom("quote", q="$q", work="$w")], "negate": [atom("banned", q="$q")], "head": {"q": "$q"}}),
    ]
    clause = run(fts, {"quote": [{"q": "q1", "work": "w"}], "banned": [{"q": "q1"}]}, "ok")["clauses"][0]
    assert clause["blocker"]["kind"] == "negated" and clause["blocker"]["count"] == 0
    assert clause["blocker"]["reads"] == ["$q"]
    assert clause["blocker"]["samples"] == [{"q": "q1"}]


def test_t5_comparison_removes_everything():
    fts = [
        fact_type("score", [("q", "code"), ("n", "int")]),
        fact_type("high", [("q", "code")], {"body": [atom("score", q="$q", n="$n")], "where": [{"operator": ">", "left": "$n", "right": 5}], "head": {"q": "$q"}}),
    ]
    clause = run(fts, {"score": [{"q": "a", "n": 1}, {"q": "b", "n": 2}]}, "high")["clauses"][0]
    assert clause["blocker"]["kind"] == "comparison" and clause["blocker"]["reads"] == ["$n"]
    assert clause["blocker"]["sample_count"] == 2


def test_t6_two_clauses_each_with_its_blocker():
    rule = {"head": {"q": "$q"}, "clauses": [
        {"body": [atom("author", work="$q", person="$p")]},
        {"body": [atom("quote", q="$q", work="$w"), atom("quote", q="$q", work="$v"), atom("author", work="$w", person="$p")]},
    ]}
    fts = [fact_type("quote", [("q", "code"), ("work", "code")]), fact_type("author", [("work", "code"), ("person", "code")]),
           fact_type("either", [("q", "code")], rule)]
    result = run(fts, {"quote": [{"q": "q1", "work": "w1"}], "author": []}, "either")
    assert [c["blocker"]["index"] for c in result["clauses"]] == [0, 2]


# -- T7: row mode ---------------------------------------------------------------

def test_t7_row_mode_branches():
    model, pop, _, _ = claim_model(author_rows=[{"work": "w1", "person": "x"}])
    assert explain(model, pop, "claim", row=strings("q1", "x")).status == "derived"
    blocked = explain(model, pop, "claim", row=strings("q2", "x")).to_dict()
    assert blocked["status"] == "blocked" and blocked["mode"] == "row"
    assert blocked["clauses"][0]["blocker"]["ground"] is True
    same = fact_type("same", [("a", "code"), ("b", "code")], {"body": [atom("quote", q="$x", work="$w")], "head": {"a": "$x", "b": "$x"}})
    fixed = fact_type("fixed", [("a", "code"), ("b", "code")], {"body": [atom("quote", q="$x", work="$w")], "head": {"a": "$x", "b": "tag"}})
    plus = fact_type("plus", [("q", "code"), ("n", "int")], {"body": [atom("score", q="$q", n="$n")], "head": {"q": "$q", "n": {"fn": "add", "args": ["$n", 1]}}})
    fts = [fact_type("quote", [("q", "code"), ("work", "code")]), fact_type("score", [("q", "code"), ("n", "int")]), same, fixed, plus]
    facts = {"quote": [{"q": "q1", "work": "w1"}], "score": [{"q": "a", "n": 1}]}
    assert run(fts, facts, "same", row=strings("q1", "q2"))["clauses"][0]["blocker"]["kind"] == "head-bind:variable"
    assert run(fts, facts, "fixed", row=strings("q1", "other"))["clauses"][0]["blocker"]["kind"] == "head-bind:constant"
    head = run(fts, facts, "plus", row=cells(("String", "a"), ("Integer", 99)))["clauses"][0]
    assert [s["kind"] for s in head["steps"]] == ["atom", "head"] and head["blocker"]["kind"] == "head"
    assert head["blocker"]["reads"] == ["$n", "$q"]
    rule_mode = run(fts, {"quote": [], "score": []}, "plus")["clauses"][0]
    assert [s["kind"] for s in rule_mode["steps"]] == ["atom"]


# -- T8: agreement with check and the oracle ---------------------------------

def check_status(model, pop, target, row):
    extensions, verdicts = checker._evaluate_derivations_dispatch(model, pop)
    verdict = next((v for v in verdicts if v.fact_type == target), None)
    if verdict is None:
        return None  # check emits no derivation verdict for this target (WN1 finding F10)
    if verdict.verdict == "unchecked":
        reason = verdict.reason_code or ""
        if reason.startswith("term:") or reason == "dependency-unavailable":
            return "unavailable"
        if reason in {"opaque-value", "derivation-rule-opaque"}:
            return "unsupported"
        if reason == "derivation-not-covered":
            return None
        raise AssertionError(f"unmapped unchecked reason {reason!r}")
    assert verdict.verdict in {"pass", "fail"}
    relation = extensions.get(target)
    rows = relation.rows if relation is not None else ()
    if row is None:
        return "derived" if rows else "blocked"
    claimed = tuple(checker._identity_token(c["value"]) for c in row)
    return "derived" if any(tuple(checker._identity_token(v) for v in r) == claimed for r in rows) else "blocked"


def _claim_types():
    return [
        fact_type("quote", [("q", "code"), ("work", "code")]),
        fact_type("author", [("work", "code"), ("person", "code")]),
        fact_type("claim", [("q", "code"), ("person", "code")], {
            "body": [atom("quote", q="$q", work="$w"), atom("author", work="$w", person="$p")],
            "head": {"q": "$q", "person": "$p"}}),
    ]


AGREEMENT = [
    ("claim-blocked", _claim_types(), {"quote": [{"q": "q1", "work": "w1"}], "author": [{"work": "w9", "person": "x"}]}, "claim", None),
    ("claim-derived", _claim_types(), {"quote": [{"q": "q1", "work": "w1"}], "author": [{"work": "w1", "person": "x"}]}, "claim", None),
    ("claim-row-derived", _claim_types(), {"quote": [{"q": "q1", "work": "w1"}], "author": [{"work": "w1", "person": "x"}]}, "claim", strings("q1", "x")),
    ("claim-row-blocked", _claim_types(), {"quote": [{"q": "q1", "work": "w1"}], "author": [{"work": "w1", "person": "x"}]}, "claim", strings("q1", "y")),
    *[(name, fts, facts, target, None) for name, fts, facts, target in unavailable_cases()],
]


@pytest.mark.parametrize("name,fts,facts,target,row", AGREEMENT, ids=[case[0] for case in AGREEMENT])
def test_t8_status_agrees_with_check(name, fts, facts, target, row):
    from tests.why_not_oracle import Oracle

    model, doc = build(fts)
    pop, pdoc = population(model, doc, facts)
    ours = explain(model, pop, target, row=row).status
    expected = check_status(model, pop, target, row)
    assert expected is None or ours == expected, name
    if ours in {"derived", "blocked"} and not any("fn" in str(ft.get("derivation_rule")) for ft in fts):
        oracle = Oracle(doc, pdoc["facts"])
        assert (ours == "derived") == oracle.derived(target, row), name


def test_t8_semiderived_and_covers():
    p = fact_type("p", [("v", "code")], {"body": [atom("b", v="$x")], "head": {"v": "$x"}}, derivation="semiderived")
    q = fact_type("q", [("v", "code")], {"body": [atom("p", v="$x")], "head": {"v": "$x"}})
    fts = [fact_type("b", [("v", "code")]), p, q]
    facts = {"b": [{"v": "a"}], "p": [{"v": "a"}, {"v": "z"}]}
    model, doc = build(fts)
    pop, _ = population(model, doc, facts)
    # Dependents never read asserted semiderived rows, so q(z) is not derived.
    assert explain(model, pop, "q", row=strings("z")).status == check_status(model, pop, "q", strings("z")) == "blocked"
    assert explain(model, pop, "p", row=strings("z")).status == "blocked"
    # Uncovered targets are explained normally; check reports them not covered.
    pop2 = pop.model_copy(update={"covers": []})
    assert check_status(model, pop2, "q", None) is None
    assert explain(model, pop2, "q").status == "derived"


def test_t8b_internal_defects_raise(monkeypatch):
    model, pop, _, _ = claim_model(author_rows=[{"work": "w1", "person": "x"}])
    real = checker._evaluate_stratified_extensions

    def dropping(*args, **kwargs):
        result = real(*args, **kwargs)
        extensions = result.extensions
        kept = type(extensions)({k: v for k, v in extensions.items() if k != "claim"}, unavailable=extensions.unavailable)
        return type(result)(kept, result.counted_operations)

    monkeypatch.setattr(checker, "_evaluate_stratified_extensions", dropping)
    with pytest.raises(WhyNotInternalError):
        explain(model, pop, "claim")
    monkeypatch.undo()

    fts = [fact_type("b", [("v", "code")]),
           fact_type("q", [("v", "code")], {"body": [atom("b", v="$x")], "head": {"v": "$x"}}),
           fact_type("p", [("v", "code")], {"body": [atom("q", v="$x")], "head": {"v": "$x"}})]
    model, doc = build(fts)
    pop, _ = population(model, doc, {"b": [{"v": "a"}]})

    def drop_p(*args, **kwargs):
        result = real(*args, **kwargs)
        extensions = result.extensions
        kept = type(extensions)({k: v for k, v in extensions.items() if k != "p"}, unavailable=extensions.unavailable)
        return type(result)(kept, result.counted_operations)

    real_facts = checker._relation_facts

    def hide_q(view):
        return real_facts({k: (v if k != "q" else type(v)(v.fact_type, v.roles, ())) for k, v in view.items()})

    monkeypatch.setattr(checker, "_evaluate_stratified_extensions", drop_p)
    monkeypatch.setattr(checker, "_relation_facts", hide_q)
    with pytest.raises(WhyNotInternalError, match="descent"):
        explain(model, pop, "p", row=strings("a"))


# -- T10, T11: descent ----------------------------------------------------------

def wrote_types():
    return [
        fact_type("quote", [("q", "code"), ("work", "code")]),
        fact_type("author", [("work", "code"), ("person", "code")]),
        fact_type("wrote", [("work", "code"), ("person", "code")], {"body": [atom("author", work="$w", person="$p")], "head": {"work": "$w", "person": "$p"}}),
        fact_type("claim", [("q", "code"), ("person", "code")], {
            "body": [atom("quote", q="$q", work="$w"), atom("wrote", work="$w", person="$p")],
            "head": {"q": "$q", "person": "$p"}}),
    ]


def test_t10_descent_names_the_base_predicate():
    result = run(wrote_types(), {"quote": [{"q": "q1", "work": "w1"}], "author": []}, "claim", row=strings("q1", "x"))
    clause = result["clauses"][0]
    assert clause["blocker"]["fact_type"] == "wrote" and clause["blocker"]["derivation"] == "derived"
    nested = clause["descent"]
    assert nested["fact_type"] == "wrote" and nested["mode"] == "row"
    assert nested["clauses"][0]["blocker"]["fact_type"] == "author"
    assert nested["clauses"][0]["descent_stopped"] == "not-derived"


def test_t10_recursive_descent_continues():
    rule = {"head": {"x": "$x", "z": "$z"}, "clauses": [
        {"body": [atom("parent", x="$x", z="$z")]},
        {"body": [atom("parent", x="$x", z="$y"), atom("anc", x="$y", z="$z")]},
    ]}
    fts = [fact_type("parent", [("x", "code"), ("z", "code")]), fact_type("anc", [("x", "code"), ("z", "code")], rule)]
    result = run(fts, {"parent": [{"x": "a", "z": "b"}, {"x": "b", "z": "c"}]}, "anc", row=strings("a", "d"))
    level1 = result["clauses"][1]["descent"]
    assert level1["clauses"][1]["blocker"]["fact_type"] == "anc"
    level2 = level1["clauses"][1]["descent"]
    assert level2 is not None and level2["clauses"][1]["blocker"]["index"] == 0


def test_t10_asserted_semiderived_row_is_flagged():
    p = fact_type("p", [("v", "code")], {"body": [atom("b", v="$x")], "head": {"v": "$x"}}, derivation="semiderived")
    q = fact_type("q", [("v", "code")], {"body": [atom("p", v="$x")], "head": {"v": "$x"}})
    result = run([fact_type("b", [("v", "code")]), p, q], {"b": [{"v": "a"}], "p": [{"v": "z"}]}, "q", row=strings("z"))
    blocker = result["clauses"][0]["blocker"]
    assert blocker["derivation"] == "semiderived" and blocker["asserted_not_read"] is True
    assert result["clauses"][0]["descent"]["clauses"][0]["blocker"]["fact_type"] == "b"


def chain(levels):
    fts = [fact_type("base", [("v", "code")])]
    for i in range(levels):
        source = f"d{i + 1}" if i + 1 < levels else "base"
        fts.append(fact_type(f"d{i}", [("v", "code")], {"body": [atom(source, v="$x")], "head": {"v": "$x"}}))
    return fts


def test_t11_descent_stops():
    rule_mode = run(wrote_types(), {"quote": [{"q": "q1", "work": "w1"}], "author": []}, "claim")
    assert rule_mode["clauses"][0]["descent_stopped"] == "not-ground"
    loop = fact_type("loop", [("v", "code")], {"head": {"v": "$x"}, "clauses": [
        {"body": [atom("seed", v="$x")]}, {"body": [atom("loop", v="$x")]}]})
    cyc = run([fact_type("seed", [("v", "code")]), loop], {"seed": []}, "loop", row=strings("a"))
    assert cyc["clauses"][1]["descent"]["clauses"][1]["descent_stopped"] == "cycle"
    deep = run(chain(10), {"base": []}, "d0", row=strings("a"))
    node, depth = deep, 0
    while node["clauses"][0]["descent"] is not None:
        node, depth = node["clauses"][0]["descent"], depth + 1
    assert depth == why_not.MAX_DESCENT and node["clauses"][0]["descent_stopped"] == "depth"
    # A structured rule over a string-rule predicate is refused by validation
    # (WN1 finding F2), so that descent stop is reached only by base blockers.


# -- T12, T13: budgets ----------------------------------------------------------

@pytest.mark.parametrize("field,value", [("pre_joins", 1), ("joins", 1), ("binding_cells", 1), ("probes", 1)])
def test_t12_each_ceiling(field, value):
    model, pop, _, _ = claim_model()
    with pytest.raises(WhyNotWorkError) as raised:
        explain(model, pop, "claim", limits=WhyNotLimits(**{field: value}))
    assert raised.value.work[field] > value


def test_t12_proof_depth_and_budget_inside_descent():
    model, doc = build(chain(10))
    pop, _ = population(model, doc, {"base": []})
    with pytest.raises(WhyNotWorkError, match="proof_depth"):
        explain(model, pop, "d0", row=strings("a"), limits=WhyNotLimits(proof_depth=3))
    # Each level probes one index lookup; the shared budget breaches at level 3.
    with pytest.raises(WhyNotWorkError) as raised:
        explain(model, pop, "d0", row=strings("a"), limits=WhyNotLimits(probes=3))
    assert raised.value.work["probes"] == 4


def test_t12_limits_cannot_be_raised():
    model, pop, _, _ = claim_model()
    with pytest.raises(WhyNotInputError):
        explain(model, pop, "claim", limits=WhyNotLimits(joins=10**9))


def bridged(n):
    fts = [
        fact_type("a1", [("x", "code")]), fact_type("a2", [("y", "code")]),
        fact_type("a3", [("x", "code"), ("y", "code")]), fact_type("a4", [("x", "code")]),
        fact_type("t", [("x", "code")], {"body": [atom("a1", x="$x"), atom("a2", y="$y"), atom("a3", x="$x", y="$y"), atom("a4", x="$x")], "head": {"x": "$x"}}),
    ]
    facts = {"a1": [{"x": f"s{i}"} for i in range(n)], "a2": [{"y": f"t{i}"} for i in range(n)],
             "a3": [{"x": "s0", "y": "t0"}], "a4": []}
    return fts, facts


def explain_work(fts, facts, target):
    model, doc = build(fts)
    pop, _ = population(model, doc, facts)
    try:
        return explain(model, pop, target).to_dict(), None
    except WhyNotWorkError as error:
        return None, error


def test_t13a_walk_breaches_joins_at_320_rows():
    result, error = explain_work(*bridged(320), "t")
    assert result is None and "joins" in str(error)
    assert error.work["joins"] == 100_001
    assert error.work["binding_cells"] == 199_680
    assert error.work["pre_joins"] < 1_000


def test_t13b_twin_completes_at_310_rows():
    result, error = explain_work(*bridged(310), "t")
    assert error is None
    assert [s["count"] for s in result["clauses"][0]["steps"]] == [310, 96_100, 1, 0]
    assert result["work"]["joins"] == 96_411
    assert result["work"]["binding_cells"] == 192_512
    assert result["work"]["probes"] == 96_722
    assert result["work"]["pre_joins"] < 1_000


def test_t13c_zero_output_join_is_charged_per_probe():
    fts = [fact_type("b1", [("x", "code")]), fact_type("b2", [("x", "code")]),
           fact_type("t", [("x", "code")], {"body": [atom("b1", x="$x"), atom("b2", x="$x")], "head": {"x": "$x"}})]
    facts = {"b1": [{"x": f"l{i}"} for i in range(5000)], "b2": [{"x": f"r{i}"} for i in range(300)]}
    result, error = explain_work(fts, facts, "t")
    assert error is None
    assert result["work"]["probes"] == 10_300
    assert result["work"]["joins"] == 5_000


def test_t13d_blow_up_inside_a_derived_body_predicate():
    fts = [fact_type("a1", [("x", "code")]), fact_type("a2", [("y", "code")]), fact_type("a4", [("x", "code")]),
           fact_type("p", [("x", "code"), ("y", "code")], {"body": [atom("a1", x="$x"), atom("a2", y="$y")], "head": {"x": "$x", "y": "$y"}}),
           fact_type("t", [("x", "code")], {"body": [atom("p", x="$x", y="$y"), atom("a4", x="$x")], "head": {"x": "$x"}})]
    facts = {"a1": [{"x": f"s{i}"} for i in range(500)], "a2": [{"y": f"t{i}"} for i in range(500)], "a4": []}
    result, error = explain_work(fts, facts, "t")
    assert result is None and "pre_joins" in str(error)
    assert error.work["pre_joins"] == 200_001


def test_t13e_linear_growth():
    small, _ = explain_work(*bridged(155), "t")
    large, _ = explain_work(*bridged(310), "t")
    assert small["work"]["joins"] == 155 + 155 * 155 + 1 == 24_181
    assert large["work"]["joins"] == 96_411


# -- T14: refusals and order ------------------------------------------------------

def test_t14_unsupported_fragments():
    agg = fact_type("count_q", [("q", "code"), ("n", "int")], {
        "body": [atom("quote", q="$q", work="$w")],
        "aggregate": {"fn": "count", "of": "$w", "over": ["$w"], "as": "$n"},
        "head": {"q": "$q", "n": "$n"}})
    base = [fact_type("quote", [("q", "code"), ("work", "code")])]
    assert run(base + [agg], {"quote": []}, "count_q")["reason"] == "aggregate"
    prose = fact_type("prose", [("q", "code")], "said in prose")
    assert run(base + [prose], {"quote": []}, "prose")["reason"] == "rule-opaque"
    up = [fact_type("b", [("v", "code")]),
          fact_type("m", [("v", "code")], {"body": [atom("b", v="$x")], "head": {"v": "$x"}}),
          fact_type("t", [("v", "code")], {"body": [atom("m", v="$x")], "head": {"v": "$x"}})]
    two_strata = run(up, {"b": [{"v": {"$opaque": "hidden"}}]}, "t")
    assert two_strata["status"] == "unsupported" and two_strata["reason"] == "opaque-value"
    claimed = run(up, {"b": [{"v": "a"}], "t": [{"v": {"$opaque": "hidden"}}]}, "t")
    assert claimed["reason"] == "opaque-value"
    outside = up + [fact_type("other", [("v", "code")])]
    assert run(outside, {"b": [{"v": "a"}], "other": [{"v": {"$opaque": "hidden"}}]}, "t")["status"] == "derived"


def test_t14_input_errors_and_order():
    model, pop, _, _ = claim_model()
    for target in ("missing", "quote"):
        with pytest.raises(WhyNotInputError):
            explain(model, pop, target)
    with pytest.raises(WhyNotInputError, match="malformed row"):
        explain(model, pop, "claim", row=strings("only-one"))
    prose = [fact_type("quote", [("q", "code"), ("work", "code")]), fact_type("prose", [("q", "code")], "said in prose")]
    model, doc = build(prose)
    pop, _ = population(model, doc, {"quote": []})
    # A malformed row is reported before the unsupported fragment (WN-D14).
    with pytest.raises(WhyNotInputError, match="malformed row"):
        explain(model, pop, "prose", row=strings("a", "b"))


# -- T15b: an outer witness trace is untouched -------------------------------------

def test_t15b_outer_trace_is_isolated():
    class Recorder:
        def __init__(self):
            self.charges, self.rows = 0, 0

        def charge(self, amount=1):
            self.charges += amount

        def row(self, *args):
            self.rows += 1

    outer = Recorder()
    token = checker._WITNESS_TRACE.set(outer)
    try:
        model, pop, _, _ = claim_model(author_rows=[{"work": "w1", "person": "x"}])
        assert explain(model, pop, "claim").status == "derived"
        assert checker._WITNESS_TRACE.get() is outer
    finally:
        checker._WITNESS_TRACE.reset(token)
    assert (outer.charges, outer.rows) == (0, 0)


# -- review regressions (notes/phase-WN1-claude-review.md) ------------------------

def test_review_r1_duplicate_rows_do_not_multiply_walk_work(monkeypatch):
    calls = []
    real = why_not._Walk._store

    def counting(self, bindings, binding):
        calls.append(1)
        return real(self, bindings, binding)

    monkeypatch.setattr(why_not._Walk, "_store", counting)
    fts = [fact_type("a1", [("x", "code")]), fact_type("a3", [("z", "code")]),
           fact_type("a4", [("x", "code"), ("z", "code")]),
           fact_type("t", [("x", "code"), ("z", "code")], {
               "body": [atom("a1", x="$x"), atom("a3", z="$z"), atom("a4", x="$x", z="$z")],
               "head": {"x": "$x", "z": "$z"}})]
    facts = {"a1": [{"x": f"s{i}"} for i in range(50)], "a3": [{"z": "k"}] * 50, "a4": []}
    result = run(fts, facts, "t")
    assert [s["count"] for s in result["clauses"][0]["steps"]] == [50, 50, 0]
    assert len(calls) == 100


def test_review_r2_samples_are_distinct_by_identity():
    fts = [fact_type("r", [("v", "num"), ("k", "code")]), fact_type("s", [("v", "num")]),
           fact_type("t", [("v", "num"), ("k", "code")], {
               "body": [atom("r", v="$x", k="$k"), atom("s", v="$x")], "head": {"v": "$x", "k": "$k"}})]
    blocker = run(fts, {"r": [{"v": 1, "k": "a"}, {"v": 1.0, "k": "b"}], "s": []}, "t")["clauses"][0]["blocker"]
    assert blocker["sample_count"] == 2
    assert len(blocker["samples"]) == 1


@pytest.mark.parametrize("value", [float("nan"), float("inf")])
def test_review_r3_non_finite_row_values_are_refused(value):
    fts = [fact_type("r", [("v", "num")]), fact_type("t", [("v", "num")], {"body": [atom("r", v="$x")], "head": {"v": "$x"}})]
    model, doc = build(fts)
    pop, _ = population(model, doc, {"r": []})
    with pytest.raises(WhyNotInputError, match="malformed row"):
        explain(model, pop, "t", row=cells(("Number", value)))


def test_review_r4_depth_stop_wins_at_proof_depth_8():
    model, doc = build(chain(10))
    pop, _ = population(model, doc, {"base": []})
    node = explain(model, pop, "d0", row=strings("a"), limits=WhyNotLimits(proof_depth=8)).to_dict()
    while node["clauses"][0]["descent"] is not None:
        node = node["clauses"][0]["descent"]
    assert node["clauses"][0]["descent_stopped"] == "depth"


def test_review_r5_sample_cap_descent_choice_and_flag_negative():
    model, pop, _, _ = claim_model(quote_rows=[{"q": f"q{i}", "work": f"w{i}"} for i in range(7)])
    blocker = explain(model, pop, "claim").to_dict()["clauses"][0]["blocker"]
    assert blocker["sample_count"] == 7 and len(blocker["samples"]) == 5
    assert blocker["samples"][0] == {"work": "w0"}
    two = run(wrote_types(), {"quote": [{"q": "q1", "work": "w2"}, {"q": "q1", "work": "w1"}], "author": []},
              "claim", row=strings("q1", "x"))
    nested = two["clauses"][0]["descent"]["clauses"][0]["blocker"]
    assert nested["samples"] == [{"work": "w1", "person": "x"}]
    p = fact_type("p", [("v", "code")], {"body": [atom("b", v="$x")], "head": {"v": "$x"}}, derivation="semiderived")
    q = fact_type("q", [("v", "code")], {"body": [atom("p", v="$x")], "head": {"v": "$x"}})
    other = run([fact_type("b", [("v", "code")]), p, q], {"b": [], "p": [{"v": "y"}]}, "q", row=strings("z"))
    assert other["clauses"][0]["blocker"]["asserted_not_read"] is False


def test_review_r5_negation_probe_charges_are_exact():
    fts = [
        fact_type("quote", [("q", "code"), ("work", "code")]),
        fact_type("banned", [("q", "code")]),
        fact_type("ok", [("q", "code")], {"body": [atom("quote", q="$q", work="$w")], "negate": [atom("banned", q="$q")], "head": {"q": "$q"}}),
    ]
    result = run(fts, {"quote": [{"q": "q1", "work": "w"}], "banned": [{"q": "q1"}]}, "ok")
    # one quote row scanned, one banned row scanned, one negation lookup
    assert result["work"]["probes"] == 3


def test_review_r5_walk_under_an_outer_trace_sends_it_nothing():
    class Recorder:
        def __init__(self):
            self.charges, self.rows = 0, 0

        def charge(self, amount=1):
            self.charges += amount

        def row(self, *args):
            self.rows += 1

    outer = Recorder()
    token = checker._WITNESS_TRACE.set(outer)
    try:
        model, pop, _, _ = claim_model()
        assert explain(model, pop, "claim", row=strings("q1", "x")).status == "blocked"
        assert checker._WITNESS_TRACE.get() is outer
    finally:
        checker._WITNESS_TRACE.reset(token)
    assert (outer.charges, outer.rows) == (0, 0)


def test_review_r5_ceiling_counter_stops_at_limit_plus_one():
    model, pop, _, _ = claim_model()
    for field in ("pre_joins", "joins", "probes"):
        with pytest.raises(WhyNotWorkError) as raised:
            explain(model, pop, "claim", limits=WhyNotLimits(**{field: 1}))
        assert raised.value.work[field] == 2, field


def test_review_r5_t13b_wall_cap():
    import time

    start = time.monotonic()
    _result, error = explain_work(*bridged(310), "t")
    assert error is None and time.monotonic() - start < 10


def _more_agreement():
    p = fact_type("p", [("v", "code")], {"body": [atom("b", v="$x")], "head": {"v": "$x"}}, derivation="semiderived")
    q = fact_type("q", [("v", "code")], {"body": [atom("p", v="$x")], "head": {"v": "$x"}})
    rule = {"head": {"x": "$x", "z": "$z"}, "clauses": [
        {"body": [atom("parent", x="$x", z="$z")]},
        {"body": [atom("parent", x="$x", z="$y"), atom("anc", x="$y", z="$z")]}]}
    up = [fact_type("b", [("v", "code")]),
          fact_type("m", [("v", "code")], {"body": [atom("b", v="$x")], "head": {"v": "$x"}}),
          fact_type("t", [("v", "code")], {"body": [atom("m", v="$x")], "head": {"v": "$x"}})]
    return [
        ("descent", wrote_types(), {"quote": [{"q": "q1", "work": "w1"}], "author": []}, "claim", strings("q1", "x")),
        ("recursive", [fact_type("parent", [("x", "code"), ("z", "code")]), fact_type("anc", [("x", "code"), ("z", "code")], rule)],
         {"parent": [{"x": "a", "z": "b"}, {"x": "b", "z": "c"}]}, "anc", strings("a", "c")),
        ("recursive-blocked", [fact_type("parent", [("x", "code"), ("z", "code")]), fact_type("anc", [("x", "code"), ("z", "code")], rule)],
         {"parent": [{"x": "a", "z": "b"}]}, "anc", strings("a", "d")),
        ("semiderived", [fact_type("b", [("v", "code")]), p, q], {"b": [{"v": "a"}], "p": [{"v": "z"}]}, "q", strings("z")),
        ("opaque-upstream", up, {"b": [{"v": {"$opaque": "hidden"}}]}, "t", None),
        ("prose-target", [fact_type("quote", [("q", "code"), ("work", "code")]), fact_type("prose", [("q", "code")], "said in prose")],
         {"quote": []}, "prose", None),
    ]


@pytest.mark.parametrize("name,fts,facts,target,row", _more_agreement(), ids=[c[0] for c in _more_agreement()])
def test_review_r5_t8_covers_descent_and_refusal_cases(name, fts, facts, target, row):
    test_t8_status_agrees_with_check(name, fts, facts, target, row)
