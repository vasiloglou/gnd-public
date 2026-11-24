"""OB2: the Halpin relational mapping (gnd.rmap) against its owner-approved corpus.

The corpus and its hand-derived answers (tests/fixtures/rmap) were approved at the
OB2 corpus gate before any gnd.rmap code existed.
"""

from __future__ import annotations

import copy
import dataclasses
import json
import shutil
import sys
from pathlib import Path
from time import monotonic

import pytest

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests/fixtures/rmap"
CASES = sorted(path.name for path in (CORPUS / "cases").iterdir() if path.is_dir())
ALTERNATE = sorted(path.stem.split(".")[0] for path in (CORPUS / "answers").glob("*.alternate.json"))


def _answer(schema, dispositions):
    """The canonical answer shape of tests/fixtures/rmap/answers/README.md."""
    def table(t):
        return {
            "name": t.name,
            "subject": list(t.subject),
            "columns": [
                {"name": c.name, "datatype": c.datatype, "nullable": c.nullable, "origin": list(c.origin)}
                for c in t.columns
            ],
            "primary_key": list(t.primary_key),
            "unique_keys": [list(u) for u in t.unique_keys],
            "foreign_keys": [
                {"name": f.name, "columns": list(f.columns), "target_table": f.target_table,
                 "target_columns": list(f.target_columns)}
                for f in t.foreign_keys
            ],
        }

    return {
        "tables": [table(t) for t in schema.tables],
        "unmapped": [{"kind": u.kind, "id": u.id, "reason": u.reason, "detail": u.detail} for u in schema.unmapped],
        "dispositions": [
            {"kind": d.kind, "id": d.id, "carried_as": list(d.carried_as), "reason": d.reason}
            for d in dispositions
        ],
    }


def _map(case, variant_name):
    from gnd.model import load_model
    from gnd.rmap import RmapVariant, dispositions, map_model

    model = load_model(CORPUS / "cases" / case / "model.yaml")
    schema = map_model(model, variant=RmapVariant[variant_name])
    return _answer(schema, dispositions(model, schema))


@pytest.mark.parametrize("case", CASES)
def test_t6_halpin_matches_the_approved_answer(case):
    expected = json.loads((CORPUS / "answers" / f"{case[:2]}.json").read_text())
    assert _map(case, "HALPIN") == expected


@pytest.mark.parametrize("number", ALTERNATE)
def test_t6_alternate_matches_the_approved_answer(number):
    (case,) = [name for name in CASES if name.startswith(number)]
    expected = json.loads((CORPUS / "answers" / f"{number}.alternate.json").read_text())
    assert _map(case, "ALTERNATE") == expected


@pytest.mark.parametrize("case", sorted(set(CASES) - {c for c in CASES if c[:2] in ALTERNATE}))
def test_t6_variants_agree_where_no_alternate_answer_exists(case):
    assert _map(case, "ALTERNATE") == _map(case, "HALPIN")


def test_t8_public_surface():
    from gnd import rmap

    assert [member.name for member in rmap.RmapVariant] == ["HALPIN", "ALTERNATE"]
    assert set(rmap.UnmappedReason.__args__) == {
        "derived-computed", "uniqueness-not-confirmed", "identification-unmatchable", "spans-tables", "not-relational",
    }
    for cls in (rmap.Column, rmap.ForeignKey, rmap.Table, rmap.Unmapped, rmap.RelationalSchema, rmap.Disposition):
        assert dataclasses.is_dataclass(cls) and cls.__dataclass_params__.frozen


# --- T1-T5, T7 -------------------------------------------------------------------------------


CENSUS = (ROOT / ".gnd-planning/milestones/ossie-interchange/evidence/OS0/revised/census.txt").read_text().splitlines()


def _all_model_paths():
    found = set()
    for base in (ROOT / "src/gnd", ROOT / "tests/fixtures"):
        for pattern in ("*.orm.yaml", "*.orm.json"):
            found.update(base.rglob(pattern))
    found.update((CORPUS / "cases").glob("*/model.yaml"))  # A14
    return sorted(found)


def _loaded(path):
    from gnd.model import load_model

    try:
        return load_model(path)
    except Exception:  # noqa: BLE001 -- only models the loader admits are in scope (spec §4 rule 1)
        return None


def test_t1_every_admitted_model_maps_under_both_variants():
    from gnd.rmap import RmapVariant, dispositions, map_model

    mapped = 0
    for path in _all_model_paths():
        model = _loaded(path)
        if model is None:
            continue
        for variant in RmapVariant:
            dispositions(model, map_model(model, variant=variant))
        mapped += 1
    assert mapped >= 400  # 443 on 2026-11-24; a collapse of the scan fails here


def _k(typ, **kw):
    return {"type": typ, **kw, "source": "explicit", "status": "confirmed", "modality": "alethic",
            "provenance": {"user_quote": "adversarial"}}


def _ft(i, reading, roles, cons=(), **kw):
    return {"id": i, "reading": reading, "roles": [{"object_type": o, "role_name": r} for o, r in roles],
            **({"constraints": list(cons)} if cons else {}), **kw}


def _adversarial():
    from ruamel.yaml import YAML

    src = {"kind": "text-conversation", "confidence": "standard", "mode": "guided"}
    cycle = {"version": 1, "source": src, "object_types": [
        {"id": "a", "name": "A", "kind": "entity", "reference": {"mode": "external"}},
        {"id": "b", "name": "B", "kind": "entity", "reference": {"mode": "external"}},
        {"id": "code", "name": "Code", "kind": "value", "primitive": "String"}],
        "fact_types": [
            _ft("a_has_b", "{A} has {B}", [("a", "a"), ("b", "b")], [_k("uniqueness", roles=["a"]), _k("mandatory", role="a")]),
            _ft("a_has_code", "{A} has {Code}", [("a", "a"), ("code", "code")], [_k("uniqueness", roles=["a"]), _k("mandatory", role="a")]),
            _ft("b_has_a", "{B} has {A}", [("b", "b"), ("a", "a")], [_k("uniqueness", roles=["b"]), _k("mandatory", role="b")]),
            _ft("b_has_code", "{B} has {Code}", [("b", "b"), ("code", "code")], [_k("uniqueness", roles=["b"]), _k("mandatory", role="b")])],
        "constraints": [
            _k("uniqueness", scope="external", preferred=True,
               role_refs=[{"fact_type": "a_has_b", "role": "b"}, {"fact_type": "a_has_code", "role": "code"}]),
            _k("uniqueness", scope="external", preferred=True,
               role_refs=[{"fact_type": "b_has_a", "role": "a"}, {"fact_type": "b_has_code", "role": "code"}])]}
    # Regression (found 2026-11-24): an identifiable objectification one of whose roles is
    # played by an unmatchable entity raised AttributeError before the guard covered rule 3.
    visit = YAML(typ="safe").load((CORPUS / "cases/25-nested-composite/model.yaml").read_text())
    visit["object_types"] += [
        {"id": "visit", "name": "Visit", "kind": "entity", "reference": {"mode": "external"}},
        {"id": "person", "name": "Person", "kind": "entity", "reference": {"mode": "popular", "value_type": "person_id"}},
        {"id": "person_id", "name": "PersonId", "kind": "value", "primitive": "Integer"},
        {"id": "visit_nr", "name": "VisitNr", "kind": "value", "primitive": "Integer"}]
    visit["fact_types"] += [
        _ft("person_visits_district", "{Person} visits {District}", [("person", "person"), ("district", "district")],
            [_k("uniqueness", roles=["person", "district"])], objectified_as="visit"),
        _ft("visit_by_person", "{Visit} by {Person}", [("visit", "visit"), ("person", "person")],
            [_k("uniqueness", roles=["visit"]), _k("mandatory", role="visit")]),
        _ft("visit_has_nr", "{Visit} has {VisitNr}", [("visit", "visit"), ("visit_nr", "nr")],
            [_k("uniqueness", roles=["visit"]), _k("mandatory", role="visit")])]
    visit["constraints"].append(_k("uniqueness", scope="external", preferred=True, role_refs=[
        {"fact_type": "visit_by_person", "role": "person"}, {"fact_type": "visit_has_nr", "role": "nr"}]))
    return {"cycle": (cycle, {"a", "b"}), "objectified-unmatchable-role": (visit, {"district"})}


@pytest.mark.parametrize("name", ["cycle", "objectified-unmatchable-role"])
def test_t1b_adversarial_models_return_with_unmatchable_rows(tmp_path, name):
    from gnd.model import load_model
    from gnd.rmap import RmapVariant, dispositions, map_model

    document, unmatchable = _adversarial()[name]
    path = tmp_path / "model.json"
    path.write_text(json.dumps(document))
    model = load_model(path)
    for variant in RmapVariant:
        schema = map_model(model, variant=variant)
        dispositions(model, schema)
        listed = {u.id for u in schema.unmapped if u.kind == "object_type"}
        assert unmatchable <= listed
        assert all(u.reason == "identification-unmatchable" for u in schema.unmapped if u.kind == "object_type")
    if name == "objectified-unmatchable-role":
        assert ("fact_type", "person_visits_district") in {(u.kind, u.id) for u in schema.unmapped}


def _census_and_corpus():
    paths = [ROOT / p for p in CENSUS] + sorted((CORPUS / "cases").glob("*/model.yaml"))
    return [(p, m) for p in paths if (m := _loaded(p)) is not None]


def test_t2_dispositions_partition_every_fact_type_and_constraint():
    from gnd.rmap import RmapVariant, dispositions, map_model

    for path, model in _census_and_corpus():
        expected = {("fact_type", str(f["id"])) for f in model.fact_types}
        for f in model.fact_types:
            expected |= {("constraint", f"fact_types/{f['id']}/constraints/{i}") for i, _ in enumerate(f.get("constraints") or ())}
        expected |= {("constraint", f"constraints/{i}") for i, _ in enumerate(model.constraints or ())}
        for variant in RmapVariant:
            rows = dispositions(model, map_model(model, variant=variant))
            keys = [(r.kind, r.id) for r in rows]
            assert len(keys) == len(set(keys)) and set(keys) == expected, path
            assert all((r.reason is None) == bool(r.carried_as) for r in rows), path


def _reversed(document):
    """Object types, fact types and both constraint lists in reversed order; roles kept."""
    out = copy.deepcopy(document)
    out["object_types"] = list(reversed(out["object_types"]))
    out["fact_types"] = list(reversed(out["fact_types"]))
    for fact in out["fact_types"]:
        if fact.get("constraints"):
            fact["constraints"] = list(reversed(fact["constraints"]))
    if out.get("constraints"):
        out["constraints"] = list(reversed(out["constraints"]))
    return out


def _readdress(model, schema):
    """Unmapped rows with constraint addresses replaced by their (owner, reversed index)."""
    sizes = {str(f["id"]): len(f.get("constraints") or ()) for f in model.fact_types}
    top = len(model.constraints or ())

    def flip(identifier):
        parts = identifier.split("/")
        if parts[0] == "constraints":
            return f"constraints/{top - 1 - int(parts[1])}"
        return f"fact_types/{parts[1]}/constraints/{sizes[parts[1]] - 1 - int(parts[3])}"

    return sorted((u.kind, flip(u.id) if u.kind == "constraint" else u.id, u.reason, u.detail) for u in schema.unmapped)


def test_t3_order_and_path_independence(tmp_path):
    from gnd.model import json_document, load_model, parse_model_document
    from gnd.rmap import RmapVariant, map_model

    for index, (path, model) in enumerate(_census_and_corpus()):
        document = json_document(parse_model_document(path.read_bytes(), source=path))
        if "includes" in document:
            continue
        # Copy the model's folder: version-4 reference populations live beside it.
        home = tmp_path / f"m{index}"
        shutil.copytree(path.parent, home, ignore=shutil.ignore_patterns("*.orm.*", "model.yaml", "__pycache__"))
        moved = home / "reordered.json"
        moved.write_text(json.dumps(_reversed(document)))
        reordered = load_model(moved)
        for variant in RmapVariant:
            first, second = map_model(model, variant=variant), map_model(reordered, variant=variant)
            assert first.tables == second.tables, path
            assert _readdress(model, first) == sorted(
                (u.kind, u.id, u.reason, u.detail) for u in second.unmapped
            ), path


def test_t3b_primary_key_tie_break_ignores_declaration_order(tmp_path):
    from ruamel.yaml import YAML

    from gnd.model import load_model
    from gnd.rmap import map_model

    document = YAML(typ="safe").load((CORPUS / "cases/13-candidate-keys/model.yaml").read_text())
    for constraint in document["fact_types"][0]["constraints"]:
        constraint.pop("preferred", None)
    keys = set()
    for order in (lambda c: c, lambda c: list(reversed(c))):
        variant = copy.deepcopy(document)
        variant["fact_types"][0]["constraints"] = order(variant["fact_types"][0]["constraints"])
        path = tmp_path / "m.json"
        path.write_text(json.dumps(variant))
        (table,) = map_model(load_model(path)).tables
        keys.add(table.primary_key)
    assert keys == {("room_room_nr", "slot_slot_code")}


def _timed(scale):
    sys.path.insert(0, str(ROOT / "tests"))
    from support.rmap_large import large_rmap_model

    from gnd.model import load_model
    from gnd.rmap import dispositions, map_model

    return large_rmap_model, load_model, map_model, dispositions


@pytest.fixture(scope="module")
def large_models(tmp_path_factory):
    large_rmap_model, load_model, _, _ = _timed(1)
    root = tmp_path_factory.mktemp("rmap-large")
    models = {}
    for scale in (1, 5):
        path = root / f"x{scale}.json"
        path.write_text(json.dumps(large_rmap_model(1400 * scale, 4500 * scale)))
        models[scale] = load_model(path)
    return models


def _best(model, repeats=3):
    _, _, map_model, dispositions = _timed(1)
    best = float("inf")
    for _ in range(repeats):
        start = monotonic()
        dispositions(model, map_model(model))
        best = min(best, monotonic() - start)
    return best


def test_t4_reporter_scale_time_bound(large_models):
    """1,400 entities and 4,500 fact types. Measured 0.067 s on 2026-11-24; bound 30x that."""
    assert _best(large_models[1]) < 2.0


def test_t4b_growth_is_not_quadratic(large_models):
    """5x the size (10x exceeds MAX_MODEL_BYTES). Linear is about 5, quadratic about 25.

    Measured 5.47 after the fix; 27.2 before it (spec finding).
    """
    assert _best(large_models[5]) / _best(large_models[1]) < 12


def test_t5_variant_measurement_covers_census_and_corpus(tmp_path):
    sys.path.insert(0, str(ROOT / "tools"))
    import rmap_variant_measurement as measurement

    data = measurement.rows()
    assert len(data) == len(CENSUS) + len(CASES)
    assert all(row.get("HALPIN", {}).get("agrees", "yes") == "yes" for row in data if row["origin"] == "corpus")
    text = measurement.render(data)
    assert text.count("\n| `") == len(data)


@pytest.mark.parametrize(
    "case, fact, expected",
    [
        ("02-popular-reference-fact", "country_has_country_code", ("key", "country", "country_code")),  # 1 over 5
        ("12-single-and-compound", "employee_works_in_department", ("columns", "employee", "department_dept_code")),  # 5 over 6
        ("17-objectification", "student_enrolled_in_course", ("key", "enrolment", "student_student_nr", "course_course_code")),  # 3 over 6
        ("18-derived", "person_has_age", ()),  # 0 over 5
    ],
)
def test_t7_precedence_pins(case, fact, expected):
    from gnd.model import load_model
    from gnd.rmap import dispositions, map_model

    model = load_model(CORPUS / "cases" / case / "model.yaml")
    (row,) = [r for r in dispositions(model, map_model(model)) if r.kind == "fact_type" and r.id == fact]
    assert row.carried_as == expected


# --- Review round 1 regressions (notes/reviews/phase-OB2-r1, F1-F9) --------------------------


def _case(number):
    from ruamel.yaml import YAML

    (case,) = [c for c in CASES if c.startswith(number)]
    return YAML(typ="safe").load((CORPUS / "cases" / case / "model.yaml").read_text())


def _schema(tmp_path, document, variant="HALPIN", name="m.json"):
    from gnd.model import load_model
    from gnd.rmap import RmapVariant, dispositions, map_model

    path = tmp_path / name
    path.write_text(json.dumps(document))
    model = load_model(path)
    schema = map_model(model, variant=RmapVariant[variant])
    return schema, {(d.kind, d.id): d for d in dispositions(model, schema)}


def _table(schema, name):
    (table,) = [t for t in schema.tables if t.name == name]
    return table


@pytest.mark.parametrize("variant", ["HALPIN", "ALTERNATE"])
def test_r1_identification_uses_the_preferred_confirmed_external_uniqueness(tmp_path, variant):
    document = _case("14")
    document["fact_types"][3]["constraints"].append(_k("mandatory", role="state"))
    document["constraints"].append(_k("uniqueness", scope="external", role_refs=[
        {"fact_type": "state_in_country", "role": "country"}, {"fact_type": "state_has_population", "role": "population"}]))
    for order in (lambda c: c, lambda c: list(reversed(c))):
        variant_doc = copy.deepcopy(document)
        variant_doc["constraints"] = order(variant_doc["constraints"])
        schema, _ = _schema(tmp_path, variant_doc, variant)
        assert _table(schema, "state").primary_key == ("country_country_code", "code")
    deontic = copy.deepcopy(_case("14"))
    deontic["constraints"][0]["modality"] = "deontic"
    schema, rows = _schema(tmp_path, deontic, variant)
    assert "state" not in {t.name for t in schema.tables}
    assert rows[("constraint", "constraints/0")].reason == "uniqueness-not-confirmed"


@pytest.mark.parametrize("variant", ["HALPIN", "ALTERNATE"])
def test_r2_a_preferred_duplicate_keeps_its_preference(tmp_path, variant):
    document = _case("13")
    constraints = document["fact_types"][0]["constraints"]
    for c in constraints:
        c.pop("preferred", None)
    constraints.append(_k("uniqueness", roles=["slot", "lecturer"], preferred=True))
    keys = set()
    for order in (lambda c: c, lambda c: list(reversed(c))):
        doc = copy.deepcopy(document)
        doc["fact_types"][0]["constraints"] = order(doc["fact_types"][0]["constraints"])
        schema, _ = _schema(tmp_path, doc, variant)
        keys.add(_table(schema, "room_slot_lecturer").primary_key)
    assert keys == {("slot_slot_code", "lecturer_staff_nr")}


@pytest.mark.parametrize("variant", ["HALPIN", "ALTERNATE"])
def test_r3_unique_key_order_ignores_declaration_order(tmp_path, variant):
    document = _case("13")
    constraints = document["fact_types"][0]["constraints"]
    constraints[0]["preferred"] = True
    constraints[1].pop("preferred", None)
    constraints.append(_k("uniqueness", roles=["room", "lecturer"]))
    found = set()
    for order in (lambda c: c, lambda c: list(reversed(c))):
        doc = copy.deepcopy(document)
        doc["fact_types"][0]["constraints"] = order(doc["fact_types"][0]["constraints"])
        schema, _ = _schema(tmp_path, doc, variant)
        found.add(_table(schema, "room_slot_lecturer").unique_keys)
    assert len(found) == 1


@pytest.mark.parametrize("variant", ["HALPIN", "ALTERNATE"])
def test_r4_external_uniqueness_within_one_table_is_a_unique_key(tmp_path, variant):
    document = _case("01")
    document["object_types"].append({"id": "phone", "name": "Phone", "kind": "value", "primitive": "String"})
    document["fact_types"].append(_ft("customer_has_phone", "{Customer} has {Phone}",
                                      [("customer", "customer"), ("phone", "phone")], [_k("uniqueness", roles=["customer"])]))
    document["constraints"] = [_k("uniqueness", scope="external", role_refs=[
        {"fact_type": "customer_has_phone", "role": "phone"}, {"fact_type": "customer_has_email", "role": "email"}])]
    schema, rows = _schema(tmp_path, document, variant)
    # Columns follow table order, not role_refs order (review r2 F3 changed this pin).
    assert _table(schema, "customer").unique_keys == (("email", "phone"),)
    assert rows[("constraint", "constraints/0")].carried_as == ("unique_key", "customer", "email", "phone")


@pytest.mark.parametrize("variant", ["HALPIN", "ALTERNATE"])
def test_r5_objectified_uniqueness_narrower_than_the_key_is_a_unique_key(tmp_path, variant):
    document = _case("17")
    objectified = next(f for f in document["fact_types"] if f["id"] == "student_enrolled_in_course")
    objectified["constraints"].append(_k("uniqueness", roles=["student"]))
    schema, rows = _schema(tmp_path, document, variant)
    assert ("student_student_nr",) in _table(schema, "enrolment").unique_keys
    assert rows[("constraint", "fact_types/student_enrolled_in_course/constraints/1")].carried_as == (
        "unique_key", "enrolment", "student_student_nr")


def test_r6_alternate_subtype_keeps_its_supertype_foreign_key(tmp_path):
    document = _case("15")
    document["fact_types"] = [f for f in document["fact_types"] if f["id"] == "student_has_gpa"]
    schema, _ = _schema(tmp_path, document, "ALTERNATE")
    student = _table(schema, "student")
    assert [(f.target_table, f.columns) for f in student.foreign_keys] == [("person", ("person_id",))]
    assert _table(schema, "person").primary_key == ("person_id",)


@pytest.mark.parametrize("variant", ["HALPIN", "ALTERNATE"])
def test_r7_a_role_played_by_a_tabled_value_type_is_a_foreign_key(tmp_path, variant):
    document = _case("20")
    document["object_types"].append({"id": "tag", "name": "Tag", "kind": "value", "primitive": "String"})
    document["fact_types"].append(_ft("entry_tag", "{Entry} tagged {Tag}", [("entry", "entry"), ("tag", "tag")]))
    schema, _ = _schema(tmp_path, document, variant)
    assert [(f.columns, f.target_table) for f in _table(schema, "entry_tag").foreign_keys] == [(("entry",), "entry")]


def test_r8_an_absorbed_unary_is_nullable(tmp_path):
    document = _case("15")
    document["fact_types"].append(_ft("student_active", "{Student} is active", [("student", "student")]))
    schema, _ = _schema(tmp_path, document, "HALPIN")
    (column,) = [c for c in _table(schema, "person").columns if c.name == "student_active"]
    assert column.nullable


def _composite_model(entities):
    objects = [{"id": "code", "name": "Code", "kind": "value", "primitive": "String"},
               {"id": "nr", "name": "Nr", "kind": "value", "primitive": "Integer"}]
    facts, constraints = [], []
    for e in range(entities):
        eid = f"x{e:05d}"
        objects.append({"id": eid, "name": f"X{e:05d}", "kind": "entity", "reference": {"mode": "external"}})
        for value in ("code", "nr"):
            facts.append(_ft(f"{eid}_has_{value}", f"{{X{e:05d}}} has {{{value.title()}}}", [(eid, eid), (value, value)],
                             [_k("uniqueness", roles=[eid]), _k("mandatory", role=eid)]))
        constraints.append(_k("uniqueness", scope="external", preferred=True, role_refs=[
            {"fact_type": f"{eid}_has_code", "role": "code"}, {"fact_type": f"{eid}_has_nr", "role": "nr"}]))
    return {"version": 1, "source": {"kind": "text-conversation", "confidence": "standard", "mode": "guided"},
            "object_types": objects, "fact_types": facts, "constraints": constraints}


def test_r9_composite_identification_is_not_superlinear(tmp_path):
    from gnd.model import load_model
    from gnd.rmap import map_model

    times = {}
    for entities in (100, 400):
        path = tmp_path / f"c{entities}.json"
        path.write_text(json.dumps(_composite_model(entities)))
        model = load_model(path)
        best = float("inf")
        for _ in range(3):
            start = monotonic()
            schema = map_model(model)
            best = min(best, monotonic() - start)
        assert len(schema.tables) == entities
        times[entities] = best
    assert times[400] / times[100] < 8  # linear about 4; quadratic about 16


# --- Review round 2 regressions (notes/reviews/phase-OB2-r2, F1-F8) --------------------------


def _with_states(document):
    """Add case 14's Country, State and StateCode, with State's composite identification."""
    states = _case("14")
    known = {o["id"] for o in document["object_types"]}
    document["object_types"] += [o for o in states["object_types"] if o["id"] not in known and o["id"] != "city"
                                 and o["id"] != "city_id"]
    document["fact_types"] += [f for f in states["fact_types"] if f["id"] in ("state_in_country", "state_has_code")]
    document.setdefault("constraints", []).extend(states["constraints"])
    return document


@pytest.mark.parametrize("variant", ["HALPIN", "ALTERNATE"])
def test_r2_f1_unresolved_objectification_identification_falls_back(tmp_path, variant):
    document = _with_states(_case("17"))
    document["fact_types"].append(_ft("a_enrolment_in_state", "{Enrolment} in {State}",
                                      [("enrolment", "enrolment"), ("state", "state")],
                                      [_k("uniqueness", roles=["enrolment"]), _k("mandatory", role="enrolment")]))
    enrolment_id = next(c for c in document["constraints"] if c["role_refs"][0]["fact_type"] == "enrolment_for_student")
    enrolment_id["role_refs"][1] = {"fact_type": "a_enrolment_in_state", "role": "state"}
    schema, rows = _schema(tmp_path, document, variant)
    enrolment = _table(schema, "enrolment")
    assert enrolment.primary_key == ("student_student_nr", "course_course_code")
    index = document["constraints"].index(enrolment_id)
    assert rows[("constraint", f"constraints/{index}")].reason == "identification-unmatchable"
    assert rows[("fact_type", "a_enrolment_in_state")].carried_as[:2] == ("columns", "enrolment")


@pytest.mark.parametrize("variant", ["HALPIN", "ALTERNATE"])
def test_r2_f2_tied_identifiers_ignore_declaration_order(tmp_path, variant):
    document = _case("14")
    duplicate = copy.deepcopy(document["constraints"][0])
    duplicate["role_refs"].reverse()
    document["constraints"].append(duplicate)
    found = set()
    for order in (lambda c: c, lambda c: list(reversed(c))):
        doc = copy.deepcopy(document)
        doc["constraints"] = order(doc["constraints"])
        schema, rows = _schema(tmp_path, doc, variant)
        found.add(_table(schema, "state").primary_key)
        assert {rows[("constraint", f"constraints/{i}")].carried_as for i in (0, 1)} == {("primary_key", "state")}
    assert len(found) == 1


def _customer_with_phone(phones=1):
    document = _case("01")
    document["object_types"].append({"id": "phone", "name": "Phone", "kind": "value", "primitive": "String"})
    document["constraints"] = []
    for n in range(phones):
        fid = "customer_has_phone" if phones == 1 else f"customer_has_phone_{n:05d}"
        role = "phone" if phones == 1 else f"phone_{n:05d}"
        document["fact_types"].append(_ft(fid, "{Customer} has {Phone}", [("customer", "customer"), ("phone", role)],
                                          [_k("uniqueness", roles=["customer"])]))
        document["constraints"].append(_k("uniqueness", scope="external", role_refs=[
            {"fact_type": fid, "role": role}, {"fact_type": "customer_has_email", "role": "email"}]))
    return document


@pytest.mark.parametrize("variant", ["HALPIN", "ALTERNATE"])
def test_r2_f3_duplicate_external_uniqueness_is_one_key(tmp_path, variant):
    document = _customer_with_phone()
    duplicate = copy.deepcopy(document["constraints"][0])
    duplicate["role_refs"].reverse()
    document["constraints"].append(duplicate)
    schema, rows = _schema(tmp_path, document, variant)
    assert _table(schema, "customer").unique_keys == (("email", "phone"),)
    assert rows[("constraint", "constraints/0")].carried_as == rows[("constraint", "constraints/1")].carried_as


def test_r2_f4_alternate_subtype_inherits_a_composite_identifier(tmp_path):
    document = _case("14")
    document["object_types"].append({"id": "special_state", "name": "SpecialState", "kind": "entity",
                                     "subtype_of": ["state"], "inherits_reference": True})
    document["fact_types"].append(_ft("special_active", "{SpecialState} is active", [("special_state", "special_state")]))
    schema, rows = _schema(tmp_path, document, "ALTERNATE")
    special = _table(schema, "special_state")
    assert special.primary_key == ("country_country_code", "code")
    assert ("state", ("country_country_code", "code")) in {(f.target_table, f.columns) for f in special.foreign_keys}
    assert rows[("fact_type", "special_active")].reason is None


@pytest.mark.parametrize("variant", ["HALPIN", "ALTERNATE"])
def test_r2_f5_a_tabled_value_component_of_a_composite_key_is_a_foreign_key(tmp_path, variant):
    document = _case("14")
    document["object_types"].append({"id": "label", "name": "Label", "kind": "value", "primitive": "String"})
    document["fact_types"].append(_ft("state_code_label", "{StateCode} has {Label}",
                                      [("state_code", "code"), ("label", "label")], [_k("uniqueness", roles=["code"])]))
    schema, _ = _schema(tmp_path, document, variant)
    assert (("code",), "state_code") in {(f.columns, f.target_table) for f in _table(schema, "state").foreign_keys}


@pytest.mark.parametrize("variant", ["HALPIN", "ALTERNATE"])
def test_r2_f6_identification_over_a_computed_fact_type_takes_its_reason(tmp_path, variant):
    document = _case("14")
    code = next(f for f in document["fact_types"] if f["id"] == "state_has_code")
    code.update({"derivation": "derived", "derivation_rule": "Computed.", "storage": "computed"})
    schema, rows = _schema(tmp_path, document, variant)
    assert rows[("constraint", "constraints/0")].reason == "derived-computed"
    assert all(c.origin[0] != "state_has_code" for t in schema.tables for c in t.columns)


@pytest.mark.parametrize("variant", ["HALPIN", "ALTERNATE"])
def test_r2_f7_external_uniqueness_over_unary_roles_is_not_a_flag_key(tmp_path, variant):
    document = _case("09")
    document["fact_types"].append(_ft("other_flag", "{Person} is flagged", [("person", "subject")]))
    document["constraints"] = [_k("uniqueness", scope="external", role_refs=[
        {"fact_type": "person_smokes", "role": "person"}, {"fact_type": "other_flag", "role": "subject"}])]
    schema, rows = _schema(tmp_path, document, variant)
    assert _table(schema, "person").unique_keys == ()
    assert rows[("constraint", "constraints/0")].carried_as == ("primary_key", "person")


def test_r2_f8_external_unique_keys_are_not_quadratic(tmp_path):
    from gnd.model import load_model
    from gnd.rmap import map_model

    times = {}
    for phones in (1000, 4000):
        path = tmp_path / f"p{phones}.json"
        path.write_text(json.dumps(_customer_with_phone(phones)))
        model = load_model(path)
        best = float("inf")
        for _ in range(3):
            start = monotonic()
            schema = map_model(model)
            best = min(best, monotonic() - start)
        assert len(_table(schema, "customer").unique_keys) == phones
        times[phones] = best
    assert times[4000] / times[1000] < 6  # linear about 4; quadratic about 16
