"""VG1 (reviewed-vocabulary-growth): ``gnd check`` cost in the number of object types.

The three universe walks of ``gnd.universe`` read per-model tables on
``ModelIndex`` instead of rebuilding a map, or resolving every object type, on
each call (issue 221). The spec is
``.gnd-planning/milestones/reviewed-vocabulary-growth/notes/phase-VG1-spec.md``;
the test names below are its section 8 rows.

T1, T2, T9, T10, T12 and T13 read no clock; T1, T9 and T10 are the required
regression gates. T11 compares two sizes on one machine. T3-T8 are absolute
bounds, about 8 times above the figures of the scratch prototype.
"""
from __future__ import annotations

import cProfile
import json
import pstats
import shutil
import time
from hashlib import sha256
from pathlib import Path

import pytest
from support.cli_runner import run_main

from gnd import universe
from gnd.documents import Model
from gnd.errors import ModelValidationError, ReferenceInputError
from gnd.model import load_model
from gnd.model_index import ModelIndex, index_scope
from gnd.universe import (
    _denoting_types,
    _descendant_closure,
    _kind_of,
    _universe_types,
    resolve_reference_value_type,
)

REPO = Path(__file__).resolve().parents[1]
CHRONOLOGY = "vocabulary/chronology.orm.json"
ROOTS = ("checking.orm.json", "extraction.orm.json")
BOUND = 10.0
RATIO = 3.0


# --- frozen copies of the base bodies (4ad0d216; unchanged at 1f403b07) -----


def frozen_descendant_closure(object_type_id, model):
    parents = {
        str(object_type.get("id")): [str(s) for s in object_type.get("subtype_of") or []]
        for object_type in model.object_types
        if object_type.get("id") is not None
    }
    members = {object_type_id}
    changed = True
    while changed:
        changed = False
        for declared_id, supertypes in parents.items():
            if declared_id not in members and members.intersection(supertypes):
                members.add(declared_id)
                changed = True
    return members


def frozen_denoting_types(covered, model):
    return {
        str(object_type.get("id"))
        for object_type in model.object_types
        if object_type.get("id") is not None
        and str(object_type.get("id")) not in covered
        and resolve_reference_value_type(str(object_type.get("id")), model) in covered
    }


def frozen_kind_of(object_type_id, model):
    for object_type in model.object_types:
        if str(object_type.get("id")) == object_type_id:
            kind = object_type.get("kind")
            return str(kind) if kind is not None else None
    return None


def frozen_universe_types(object_type_id, model):
    covered = frozen_descendant_closure(object_type_id, model)
    if frozen_kind_of(object_type_id, model) == "value":
        return covered | frozen_denoting_types(covered, model)
    return covered


# --- the growth helper (spec section 8) ------------------------------------


def _value(identifier):
    return {"id": identifier, "kind": "value", "primitive": "String"}


def _entity(identifier, value_type):
    return {"id": identifier, "kind": "entity", "reference": {"mode": "popular", "value_type": value_type}}


def _subtype(identifier, parent):
    return {"id": identifier, "kind": "entity", "subtype_of": [parent], "inherits_reference": True}


def extra_rows(shape, count):
    """(object types, fact types) the shape adds for COUNT extra types."""
    if shape == "values":
        return [_value(f"extra_{i}") for i in range(count)], []
    if shape == "entities":
        half = count // 2
        return ([_value(f"extra_v{i}") for i in range(half)]
                + [_entity(f"extra_e{i}", f"extra_v{i}") for i in range(half)]), []
    if shape == "shared":
        return [_value("extra_v")] + [_entity(f"extra_e{i}", "extra_v") for i in range(count)], []
    if shape == "tree":
        rows = [_value("extra_v")]
        for r in range(count // 100):
            rows.append(_entity(f"extra_r{r}", "extra_v"))
            for s in range(9):
                rows.append(_subtype(f"extra_r{r}_s{s}", f"extra_r{r}"))
                rows.extend(_subtype(f"extra_r{r}_s{s}_t{t}", f"extra_r{r}_s{s}") for t in range(10))
        return rows, []
    if shape == "both":
        values = [_value(f"extra_{i}") for i in range(count)]
        facts = [{"id": f"extra_ft_{i}", "reading": f"{{Extra{i}}} pairs with {{Extra{(i + 1) % count}}}",
                  "roles": [{"object_type": f"extra_{i}", "role_name": "left"},
                            {"object_type": f"extra_{(i + 1) % count}", "role_name": "right"}]}
                 for i in range(count)]
        return values, facts
    raise ValueError(f"unknown shape {shape!r}")


def grow(root, rows):
    """Append ROWS to the chronology include and re-pin both roots."""
    object_types, fact_types = rows
    path = root / CHRONOLOGY
    doc = json.loads(path.read_bytes())
    doc["object_types"].extend(object_types)
    doc["fact_types"].extend(fact_types)
    path.write_text(json.dumps(doc))
    digest = sha256(path.read_bytes()).hexdigest()
    for name in ROOTS:
        model = json.loads((root / name).read_bytes())
        for entry in model["includes"]:
            if entry["path"] == CHRONOLOGY:
                entry["sha256"] = digest
        (root / name).write_text(json.dumps(model))


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    from gnd.examples.literature.interop import build

    out = tmp_path_factory.mktemp("vg1").resolve() / "interop"
    build(out)
    return out


def _case(built, tmp_path, shape=None, count=0):
    root = tmp_path.resolve() / f"case-{shape}-{count}"
    shutil.copytree(built, root)
    if count:
        grow(root, extra_rows(shape, count))
    return root


def _check(root):
    """(exit, verdicts, seconds) of one in-process ``gnd check`` on the checking root."""
    argv = ["check", str(root / "checking.orm.json"), str(root / "composed.population.json"), "--format", "json"]
    started = time.perf_counter()
    result = run_main(argv)
    elapsed = time.perf_counter() - started
    payload = json.loads(result.stdout)
    report = payload.get("report", payload)
    return result.returncode, report["verdicts"], elapsed


@pytest.fixture(scope="module")
def baseline(built, tmp_path_factory):
    code, verdicts, _ = _check(_case(built, tmp_path_factory.mktemp("vg1-base")))
    assert code == 4 and len(verdicts) == 3
    return code, verdicts


# --- T1: the tables and the walks equal the base bodies on every fixture ----


def _loadable_models():
    for base in ("src/gnd/examples", "tests/fixtures"):
        for path in sorted((REPO / base).rglob("*")):
            if path.is_file() and path.name.endswith((".orm.yaml", ".orm.yml", ".orm.json")):
                try:
                    yield path, load_model(path)
                except (ModelValidationError, ReferenceInputError):
                    continue


def _branch(row, resolved):
    if resolved is None:
        return "unresolvable"
    if row.get("kind") == "value":
        return "value"
    if isinstance(row.get("reference"), dict):
        return "own-reference"
    return "inherits"


def test_T1_tables_and_walks_equal_the_base_bodies_on_every_loadable_model():
    models = branches = 0
    seen: set[str] = set()
    for path, model in _loadable_models():
        models += 1
        index = ModelIndex.for_model(model)
        table = index.reference_value_types()
        rows = {str(row.get("id")): row for row in model.object_types if row.get("id") is not None}
        assert set(table) == set(rows), path
        for identifier, row in rows.items():
            resolved = resolve_reference_value_type(identifier, model)
            assert table[identifier] == resolved, (path, identifier)
            seen.add(_branch(row, resolved))
            closure = frozen_descendant_closure(identifier, model)
            assert _descendant_closure(identifier, model) == closure, (path, identifier)
            assert _denoting_types(closure, model) == frozen_denoting_types(closure, model), (path, identifier)
            assert _kind_of(identifier, model) == frozen_kind_of(identifier, model), (path, identifier)
            assert _universe_types(identifier, model) == frozen_universe_types(identifier, model), (path, identifier)
            branches += 1
    assert models >= 200, models
    assert seen == {"value", "own-reference", "inherits", "unresolvable"}, seen
    assert branches > 1000, branches


# --- T2: hostile shapes built in code ---------------------------------------


def _built_in_code(object_types):
    return Model(version=1, object_types=object_types, fact_types=[])


T2_MODELS = {
    "cycle": [_subtype("a", "b"), _subtype("b", "a"), _value("tag")],
    "undeclared-supertype": [_subtype("orphan", "ghost"), _value("tag")],
    "entity-without-reference": [{"id": "lonely", "kind": "entity"}, _value("tag")],
    "two-supertypes-two-value-types": [
        _value("left_id"), _value("right_id"), _entity("left", "left_id"), _entity("right", "right_id"),
        {"id": "both", "kind": "entity", "subtype_of": ["left", "right"], "inherits_reference": True}],
    "duplicate-id": [_value("dup"), {"id": "dup", "kind": "entity", "reference": {"mode": "popular",
                                                                                    "value_type": "v"}},
                     _value("v"), _entity("user", "dup")],
}


@pytest.mark.parametrize("name", sorted(T2_MODELS))
def test_T2_hostile_shapes_answer_as_the_base_bodies(name):
    model = _built_in_code(T2_MODELS[name])
    identifiers = [str(row["id"]) for row in model.object_types] + ["ghost", "missing", "None"]
    for identifier in identifiers:
        closure = frozen_descendant_closure(identifier, model)
        assert _descendant_closure(identifier, model) == closure, identifier
        assert _denoting_types(closure, model) == frozen_denoting_types(closure, model), identifier
        assert _kind_of(identifier, model) == frozen_kind_of(identifier, model), identifier
        assert _universe_types(identifier, model) == frozen_universe_types(identifier, model), identifier
        if identifier in ModelIndex.for_model(model).reference_value_types():
            assert (ModelIndex.for_model(model).reference_value_types()[identifier]
                    == resolve_reference_value_type(identifier, model)), identifier


def test_T2_the_cycle_and_two_supertype_cases_take_their_branches():
    cycle = _built_in_code(T2_MODELS["cycle"])
    assert _descendant_closure("a", cycle) == {"a", "b"}
    assert ModelIndex.for_model(cycle).reference_value_types()["a"] is None
    both = _built_in_code(T2_MODELS["two-supertypes-two-value-types"])
    assert ModelIndex.for_model(both).reference_value_types()["both"] is None
    assert _denoting_types({"left_id"}, both) == {"left"}
    duplicate = _built_in_code(T2_MODELS["duplicate-id"])
    assert _kind_of("dup", duplicate) == "value"  # first match, as the base body
    assert ModelIndex.for_model(duplicate).reference_value_types()["dup"] == "v"  # last duplicate


# --- T3-T7: absolute bounds at 1,000 extra types ----------------------------


@pytest.mark.parametrize("shape", ["values", "entities", "shared", "tree", "both"])
def test_T3_to_T7_check_at_1000_extra_types_keeps_its_verdicts_within_the_bound(built, tmp_path, baseline, shape):
    code, verdicts, elapsed = _check(_case(built, tmp_path, shape, 1000))
    assert (code, verdicts) == baseline
    assert elapsed < BOUND, elapsed


# --- T9: the supertype map is built a number of times that does not grow ----


def _supertype_parent_calls(root):
    profile = cProfile.Profile()
    profile.enable()
    try:
        run_main(["check", str(root / "checking.orm.json"), str(root / "composed.population.json"),
                  "--format", "json"])
    finally:
        profile.disable()
    stats = pstats.Stats(profile).stats
    return sum(entry[1] for (filename, _line, name), entry in stats.items()
               if name == "_supertype_parents" and filename.endswith("model_queries.py"))


def test_T9_supertype_map_builds_do_not_grow_with_the_model(built, tmp_path):
    small = _supertype_parent_calls(_case(built, tmp_path, "values", 300))
    large = _supertype_parent_calls(_case(built, tmp_path, "values", 600))
    assert small == large, (small, large)
    assert 0 < small <= 100, small


def test_T9_negative_control_the_base_walk_builds_the_map_per_object_type(built, tmp_path, monkeypatch):
    monkeypatch.setattr(universe, "_denoting_types", frozen_denoting_types)
    monkeypatch.setattr(universe, "denoting_types", frozen_denoting_types)
    # At 100 extra value types, not the spec's 300: the base walk under the
    # profiler took 36 s at 300 and builds the map 21,677 times at 100 (spec,
    # implementation findings).
    assert _supertype_parent_calls(_case(built, tmp_path, "values", 100)) > 1000


# --- T11: doubling costs at most three times ---------------------------------


@pytest.mark.parametrize("shape", ["values", "entities", "shared", "tree"])
def test_T11_doubling_the_extra_types_costs_at_most_three_times(built, tmp_path, shape):
    def fastest(count):
        root = _case(built, tmp_path, shape, count)
        return min(_check(root)[2] for _ in range(3))

    small, large = fastest(1000), fastest(2000)
    assert large <= RATIO * small, (small, large)


# --- T12: outside any scope, and over an equal model object -----------------


def test_T12_direct_calls_outside_a_scope_and_over_an_equal_model(built, tmp_path):
    root = _case(built, tmp_path, "entities", 20)
    path = root / "checking.orm.json"
    first = load_model(path)
    second = load_model(path)
    assert first is not second
    for identifier in [str(row["id"]) for row in first.object_types]:
        expected = frozen_universe_types(identifier, first)
        assert _universe_types(identifier, first) == expected
        assert _universe_types(identifier, second) == expected
        with index_scope():
            assert _universe_types(identifier, second) == expected


# --- T13: the tables cannot be written through ------------------------------


def test_T13_tables_refuse_writes_and_denoted_by_returns_a_new_set():
    model = _built_in_code(T2_MODELS["two-supertypes-two-value-types"])
    index = ModelIndex.for_model(model)
    with pytest.raises(TypeError):
        index.reference_value_types()["left"] = "right_id"
    with pytest.raises(TypeError):
        index.subtype_children()["left"] = frozenset({"x"})
    answer = index.denoted_by({"left_id"})
    answer.add("intruder")
    assert index.denoted_by({"left_id"}) == {"left_id", "left"}  # a value type denotes itself
    assert "intruder" not in index.denoted_by({"left_id"})


# --- review round 1 (notes/reviews/phase-VG1-r1), regression cases ----------


def test_R1_F1_a_cached_index_never_answers_for_a_model_whose_values_differ():
    """F1: a str-enum ``kind`` and the plain string share a canonical JSON form and a cache key."""
    from enum import Enum

    class Kind(str, Enum):
        VALUE = "value"

    def model(kind):
        return Model(version=2, object_types=[{"id": "v", "kind": kind, "primitive": "String"},
                                               _entity("e", "v")], fact_types=[])

    warm = model(Kind.VALUE)
    _kind_of("v", warm)
    _universe_types("v", warm)
    plain = model("value")
    assert ModelIndex.for_model(plain).digest == ModelIndex.for_model(warm).digest  # the shared key
    assert _kind_of("v", plain) == frozen_kind_of("v", plain) == "value"
    assert _universe_types("v", plain) == frozen_universe_types("v", plain) == {"v", "e"}


def test_R1_F2_a_malformed_reference_in_a_code_built_model_does_not_raise():
    """F2: the base body resolved only uncovered types; the table resolves every type, so it is total."""
    model = Model(version=2, object_types=[_value("v"), {"id": "e", "kind": "entity", "reference": "bad"}],
                  fact_types=[])
    assert _denoting_types({"v", "e"}, model) == frozen_denoting_types({"v", "e"}, model) == set()
    assert ModelIndex.for_model(model).reference_value_types()["e"] is None
