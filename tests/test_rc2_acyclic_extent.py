"""RC2 (rule-check-adoption): the full extent of an acyclic violation, report version 15.

The corpus under tests/fixtures/rc2-acyclic is the phase's approval
instrument; its README tells each case and expected/ holds the answers.
"""

from __future__ import annotations

import importlib.util
import json
import random
import re
import time

import pytest
from jsonschema import Draft202012Validator
from support.cli_runner import run_main
from support.repository import REPO_ROOT

from gnd.graphs import strongly_connected_components

CORPUS = REPO_ROOT / "tests" / "fixtures" / "rc2-acyclic"
EXPECTED = CORPUS / "expected"
REPORT_SCHEMA = json.loads((REPO_ROOT / "src" / "gnd" / "report.schema.json").read_text())

CASES = {
    "two-groups": "models/graph.orm.yaml",
    "add-disjoint": "models/graph.orm.yaml",
    "self-loop": "models/graph.orm.yaml",
    "clean": "models/graph.orm.yaml",
    "composite": "models/graph-composite.orm.yaml",
}


def _exits() -> dict[str, int]:
    return json.loads((EXPECTED / "exits.json").read_text())


def _check(case: str, *flags: str):
    return run_main(["check", CASES[case], f"populations/{case}.pop.yaml", *flags], cwd=CORPUS)


def test_corpus_lists_every_case_once() -> None:
    assert set(_exits()) == {*CASES, "text-two-groups"}


@pytest.mark.parametrize("case", sorted(CASES))
def test_rule_ids_case_matches_answer_key(case: str) -> None:
    result = _check(case, "--rule-ids", "--format", "json")
    assert result.returncode == _exits()[case]
    assert result.stdout == (EXPECTED / f"{case}.json").read_bytes()
    Draft202012Validator(REPORT_SCHEMA).validate(json.loads(result.stdout))


@pytest.mark.parametrize("case", sorted(CASES))
def test_version_7_is_unchanged(case: str) -> None:
    result = _check(case, "--format", "json")
    assert result.returncode == _exits()[case]
    assert result.stdout == (EXPECTED / f"{case}.v7.json").read_bytes()


def test_text_case_matches_answer_key() -> None:
    result = _check("two-groups", "--rule-ids")
    assert result.returncode == _exits()["text-two-groups"]
    assert result.stdout == (EXPECTED / "two-groups.txt").read_bytes()


def test_a_disjoint_loop_leaves_the_existing_rows_in_place() -> None:
    """RC2-C2: every row of case 1 is still a row, in the same order, after case 2 adds a loop."""
    before = json.loads(_check("two-groups", "--rule-ids", "--format", "json").stdout)
    after = json.loads(_check("add-disjoint", "--rule-ids", "--format", "json").stdout)
    old = before["verdicts"][0]["offending_facts"]
    new = after["verdicts"][0]["offending_facts"]
    assert old and [row for row in new if row in old] == old


# --- Direct tests (spec §8, T6-T10) -------------------------------------------------


def _generator():
    spec = importlib.util.spec_from_file_location("rc2_generate", CORPUS / "generate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _scalars(edges):
    from gnd.semantic_ir import Scalar

    def scalar(value):
        return Scalar("string", value, 0, 1, False, "string")

    return [(scalar(a), scalar(b)) for a, b in edges]


@pytest.mark.parametrize(
    ("sizes", "edges", "others", "expected"),
    [
        ([2], 2, [], "1 strongly connected group (size 2) holds 2 edges."),
        ([1], 1, [], "1 strongly connected group (size 1) holds 1 edge."),
        ([3, 2, 2], 7, [], "3 strongly connected groups (sizes 3, 2, 2) hold 7 edges."),
        ([2], 2, [("r", "s", "t")], "1 strongly connected group (size 2) holds 2 edges; acyclic broken by ('r', 's', 't')."),
    ],
)
def test_t6_extent_message_grammar(sizes, edges, others, expected) -> None:
    from gnd.verbalize import ring_extent_message

    assert ring_extent_message("acyclic", "uses", sizes, edges, others) == (
        f"The relation 'uses' is acyclic — violated: {expected}"
    )


def test_t7_the_planning_fixture_within_its_time_bound() -> None:
    """RC2-C4 and RC2-C5: 2,047 edges, groups 90, 19, 13, 7, 3, 3, 2, 2, under 0.5 s."""
    from gnd.semantic_spec import acyclic_extent, canonical_distinct_rows

    edges = _generator().edges()
    assert len(edges) == 2047
    pairs = canonical_distinct_rows(_scalars(edges))
    started = time.perf_counter()
    rows, sizes = acyclic_extent(pairs)
    elapsed = time.perf_counter() - started
    assert elapsed < 0.5, elapsed
    assert sizes == [90, 19, 13, 7, 3, 3, 2, 2]
    assert len(rows) == 780


def _retired_strata(heads, reads):
    """pyrel_rules._strata before RC2, kept as the order oracle."""
    order, index, low, stack = [], {}, {}, []
    for root in heads:
        if root in index:
            continue
        work = [(root, 0)]
        while work:
            node, i = work.pop()
            if i == 0:
                index[node] = low[node] = len(index)
                stack.append(node)
            if i < len(reads[node]):
                work.append((node, i + 1))
                nxt = reads[node][i]
                if nxt not in index:
                    work.append((nxt, 0))
                elif nxt in stack:
                    low[node] = min(low[node], index[nxt])
                continue
            if low[node] == index[node]:
                while True:
                    member = stack.pop()
                    order.append(member)
                    if member == node:
                        break
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
    return order


def _retired_components(dependencies):
    """_validation._derivation_components (Kosaraju) before RC2, kept as the membership oracle."""
    nodes = set(dependencies)
    outgoing = {node: sorted(dependencies[node] & nodes) for node in nodes}
    incoming = {node: [] for node in nodes}
    for node, children in outgoing.items():
        for child in children:
            incoming[child].append(node)
    seen, finish = set(), []
    for root in sorted(nodes):
        if root in seen:
            continue
        seen.add(root)
        stack = [(root, iter(outgoing[root]))]
        while stack:
            node, children = stack[-1]
            child = next(children, None)
            if child is None:
                finish.append(node)
                stack.pop()
            elif child not in seen:
                seen.add(child)
                stack.append((child, iter(outgoing[child])))
    seen.clear()
    result = []
    for root in reversed(finish):
        if root in seen:
            continue
        component, pending = [], [root]
        seen.add(root)
        while pending:
            node = pending.pop()
            component.append(node)
            for parent in incoming[node]:
                if parent not in seen:
                    seen.add(parent)
                    pending.append(parent)
        result.append(tuple(sorted(component)))
    return tuple(result)


def _random_graph(rng: random.Random):
    nodes = [f"n{index}" for index in range(rng.randint(1, 25))]
    density = rng.random() * 0.3
    return {node: [other for other in nodes if rng.random() < density] for node in nodes}


def test_t8_the_shared_home_matches_every_retired_body() -> None:
    """RC2-C6: same order as the PyRel strata, same groups as the derivation walks."""
    from gnd.export.pyrel_rules import _strata
    from gnd.model import _derivation_components

    rng = random.Random(209)
    for _ in range(200):
        reads = _random_graph(rng)
        heads = {head: {"derivation_rule": {"body": [{"fact_type": read} for read in reads[head]]}} for head in reads}
        assert _strata(heads) == _retired_strata(heads, reads)
        dependencies = {node: set(children) for node, children in reads.items()}
        assert set(_derivation_components(dependencies)) == set(_retired_components(dependencies))
        cycles = sorted(
            sorted(component) for component in _retired_components(dependencies)
            if len(component) > 1 or component[0] in dependencies[component[0]]
        )
        found = sorted(
            sorted(component) for component in strongly_connected_components(sorted(reads), {k: sorted(v) for k, v in reads.items()})
            if len(component) > 1 or component[0] in reads[component[0]]
        )
        assert found == cycles


def test_t8_no_scc_walk_left_outside_the_shared_home() -> None:
    walk = re.compile(r"\blow\[|\blowlink\b|\bon_stack\b|reversed\(finish\)")
    offenders = [
        path.relative_to(REPO_ROOT).as_posix()
        for path in sorted((REPO_ROOT / "src" / "gnd").rglob("*.py"))
        if path.name != "graphs.py" and walk.search(path.read_text())
    ]
    assert offenders == []


def test_t9_version_7_never_computes_the_extent(monkeypatch) -> None:
    from gnd import correspondence

    def refuse(*_args, **_kwargs):
        raise AssertionError("version 7 read the extent")

    monkeypatch.setattr(correspondence, "acyclic_extents", refuse)
    result = _check("two-groups", "--format", "json")
    assert result.returncode == 1
    assert result.stdout == (EXPECTED / "two-groups.v7.json").read_bytes()


def test_t10_long_chain_and_long_cycle_need_no_recursion() -> None:
    size = 100_000
    chain = {index: [index + 1] for index in range(size - 1)}
    assert len(strongly_connected_components(range(size), chain)) == size
    ring = {index: [(index + 1) % size] for index in range(size)}
    (component,) = strongly_connected_components(range(size), ring)
    assert sorted(component) == list(range(size))


# --- Review regressions (notes/phase-RC2-codex-review.md, Q1-Q4) -------------------


def test_q1_extent_reads_the_coverage_the_checker_evaluates(tmp_path) -> None:
    """Without a coverage assertion the ring is still judged, so its extent must be too."""
    population = (CORPUS / "populations" / "two-groups.pop.yaml").read_text()
    population = population.replace("covers: [uses]", "covers: []").replace(
        "../models/graph.orm.yaml", str(CORPUS / "models" / "graph.orm.yaml")
    )
    (tmp_path / "uncovered.pop.yaml").write_text(population)
    result = run_main(
        ["check", "models/graph.orm.yaml", str(tmp_path / "uncovered.pop.yaml"), "--rule-ids", "--format", "json"],
        cwd=CORPUS,
    )
    expected = json.loads((EXPECTED / "two-groups.json").read_text())["verdicts"][0]
    verdict = json.loads(result.stdout)["verdicts"][0]
    assert (verdict["offending_facts"], verdict["message"]) == (expected["offending_facts"], expected["message"])


def test_q2_derivation_components_preparation_is_linear() -> None:
    from gnd.model import _derivation_components

    dependencies = {f"h{index}": set() for index in range(20_000)}
    started = time.perf_counter()
    assert len(_derivation_components(dependencies)) == 20_000
    assert time.perf_counter() - started < 1.0


def test_q3_no_extent_pass_without_an_acyclic_rule(monkeypatch) -> None:
    """A failing ring rule of another variant must not pay for a second snapshot."""
    import gnd.semantic_adapter as adapter
    from gnd.correspondence import acyclic_extents
    from gnd.model import load_model_bytes
    from gnd.population import load_population_bytes

    model_text = (CORPUS / "models" / "graph.orm.yaml").read_text().replace("variant: acyclic", "variant: asymmetric")
    model = load_model_bytes(model_text.encode(), source=CORPUS / "models" / "graph.orm.yaml")
    population = load_population_bytes(
        (CORPUS / "populations" / "two-groups.pop.yaml").read_bytes(),
        source=CORPUS / "populations" / "two-groups.pop.yaml", model=model,
    )

    def refuse(*_args, **_kwargs):
        raise AssertionError("snapshot adapted for a non-acyclic rule")

    monkeypatch.setattr(adapter, "adapt_snapshot_observed", refuse)
    assert acyclic_extents(model, population, ["fact_types[uses].constraints[0]"]) == {}


def test_q4_derivation_cycles_keeps_its_groups() -> None:
    from gnd.model import _derivation_cycles

    def head(name, reads):
        return {
            "id": name, "reading": f"{{Item}} {name}",
            "roles": [{"object_type": "item", "role_name": "item"}],
            "derivation": "derived",
            "derivation_rule": {"head": {"item": "$x"}, "body": [{"fact_type": read, "bind": {"item": "$x"}} for read in reads]},
        }

    doc = {"fact_types": [head("p", ["q"]), head("q", ["p"]), head("r", ["r"]), head("s", ["p"])]}
    assert _derivation_cycles(doc) == [["p", "q"], ["r"]]
