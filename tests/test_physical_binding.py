"""OB4: `gnd export ossie --physical-binding` against its owner-approved corpus.

The corpus (tests/fixtures/physical_binding), its refusal table and the packaged
schema were approved at the OB4 corpus gate before any binding reader existed.
"""

from __future__ import annotations

import json

import pytest
from support import ossie_relational_corpus as relational
from support import physical_binding_corpus as corpus

CASES = corpus.cases()
ROWS = corpus.refusal_rows()


def _render(case, output_format="yaml", **extra):
    from gnd.export.ossie import render_ossie

    return render_ossie(
        corpus.model_path(case), output_format=output_format,
        physical_binding=corpus.CORPUS / case / "binding.json", **extra,
    )


def _argv(model, out, *extra):
    return ["export", "ossie", str(model), "--out", str(out), *extra]


@pytest.mark.parametrize("case", CASES)
def test_t1_yaml_equals_the_approved_files(case):
    bundle = _render(case)
    directory = corpus.CORPUS / case
    assert bundle.semantic_model == (directory / "expected.semantic_model.yaml").read_bytes()
    assert bundle.mapping == (directory / "expected.mapping.yaml").read_bytes()


@pytest.mark.parametrize("case", CASES)
def test_t1_extension_parses_to_the_readable_copy(case):
    mapping = relational.load_yaml_bytes(_render(case).mapping)
    (extension,) = mapping["custom_extensions"]
    expected = json.loads((corpus.CORPUS / case / "expected.extension.json").read_text(encoding="utf-8"))
    assert json.loads(extension["data"]) == expected


def _write_refusal(row, directory):
    """The row's binding file under ``directory``; a directory for the not-a-file row."""
    path = directory / "binding.json"
    data = corpus.refusal_bytes(row)
    if data is None:
        path.mkdir()
    else:
        path.write_bytes(data)
    return path


@pytest.mark.parametrize("row", ROWS, ids=[row["id"] for row in ROWS])
def test_t4_each_bad_binding_is_refused_by_its_rule(row, tmp_path, capsys):
    from gnd import cli

    binding = _write_refusal(row, tmp_path)
    model = corpus.model_path(row.get("base", "V1"))
    out = tmp_path / "out"
    out.mkdir()
    assert cli.main(_argv(model, out / "o.yaml", "--physical-binding", str(binding))) == 3
    captured = capsys.readouterr()
    assert row["rule"] in captured.err, captured.err
    assert "Traceback" not in captured.err
    assert not list(out.iterdir())


# --- T2, T3: the valid cases beyond their bytes -------------------------------------------------


@pytest.mark.parametrize("case", CASES)
@pytest.mark.parametrize("output_format", ("yaml", "json"))
def test_t2_valid_cases_are_consistent_and_leave_the_legacy_files_alone(case, output_format):
    from gnd.export.ossie import render_ossie
    from gnd.export.ossie_relational import validate_relational

    bundle = _render(case, output_format)
    load = json.loads if output_format == "json" else relational.load_yaml_bytes
    ontology, semantic, mapping = load(bundle.document), load(bundle.semantic_model), load(bundle.mapping)
    validate_relational(semantic, mapping)
    relational.cross_check(ontology, semantic, mapping)
    plain = render_ossie(corpus.model_path(case), output_format=output_format)
    assert (bundle.document, bundle.sidecar, bundle.loss_report) == (plain.document, plain.sidecar, plain.loss_report)
    assert bundle.semantic_model != plain.semantic_model
    payload = json.loads(mapping["custom_extensions"][0]["data"])
    assert "rmap_variant" not in payload and "binding_sha256" in payload
    assert "binding_sha256" not in json.loads(load(plain.mapping)["custom_extensions"][0]["data"])


def test_t2_the_corpus_checker_accepts_what_the_reader_writes():
    for case in CASES:
        corpus.check_valid(case)


def test_t3_a_two_column_foreign_key_is_one_relationship():
    semantic = relational.load_yaml_bytes(_render("V3").semantic_model)
    (city_state,) = [r for r in semantic["relationships"] if r["from"] == "city"]
    assert city_state == {
        "name": "city__state", "from": "city", "to": "state",
        "from_columns": ["st_country_cd", "st_cd"], "to_columns": ["country_cd", "state_cd"],
    }


# --- T5: one order --------------------------------------------------------------------------------


def test_t5_the_rule_order_is_the_source_order():
    """The checks appear in the module in the order RULE_ORDER states."""
    import ast
    import inspect

    from gnd.export import physical_binding

    tree = ast.parse(inspect.getsource(physical_binding))
    functions = {node.name: node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    raised = []
    for name in ("read_binding", "check_names", "check_contradictions"):
        for node in sorted(ast.walk(functions[name]), key=lambda n: (getattr(n, "lineno", 0), getattr(n, "col_offset", 0))):
            if (isinstance(node, ast.Call) and getattr(node.func, "id", None) == "BindingError"
                    and isinstance(node.args[0], ast.Constant) and node.args[0].value not in raised):
                raised.append(node.args[0].value)
    assert tuple(raised) == physical_binding.RULE_ORDER
    assert physical_binding.RULE_ORDER == corpus.RULES


def _combined(first, second):
    """Two refusal rows' edits in one binding, or None when they cannot be combined."""
    if first.get("base") is None or first.get("base") != second.get("base"):
        return None
    for one in first["patch"]:
        for other in second["patch"]:  # an edit inside or over the other would undo it
            shorter, longer = sorted((one["path"], other["path"]), key=len)
            if longer == shorter or longer.startswith(shorter + "/"):
                return None
    base = json.loads((corpus.CORPUS / first["base"] / "binding.json").read_text(encoding="utf-8"))
    try:
        document = corpus.apply_patch(corpus.apply_patch(base, first["patch"]), second["patch"])
    except (AssertionError, KeyError, IndexError, ValueError):
        return None
    if list(corpus.binding_schema().iter_errors(document)):
        return None
    return document


def test_t5_an_earlier_rule_wins_over_every_later_one(tmp_path):
    """Every pair of refusal rows that can share one binding reports the earlier rule."""
    from gnd.export.ossie import render_ossie
    from gnd.export.physical_binding import RULE_ORDER, BindingError

    rank = {rule: number for number, rule in enumerate(RULE_ORDER)}
    rows = [row for row in ROWS if row["rule"] in corpus.MODEL_RULES]
    earlier_rules = set()
    cancelled = []
    checked = 0
    for first in rows:
        for second in rows:
            if rank[first["rule"]] >= rank[second["rule"]]:
                continue
            document = _combined(first, second)
            if document is None:
                continue
            path = tmp_path / f"{checked}.json"
            path.write_text(json.dumps(document))
            checked += 1
            try:
                render_ossie(corpus.model_path(first["base"]), output_format="yaml", physical_binding=path)
            except BindingError as error:
                # A later defect may be masked by the combination, never reported first.
                assert rank[error.rule] <= rank[first["rule"]], (first["id"], second["id"], error.rule)
                if error.rule == first["rule"]:
                    earlier_rules.add(first["rule"])
            else:
                cancelled.append((first["id"], second["id"]))
    assert checked >= 150
    # Two edits can repair each other: a role added under a second spelling, then the
    # first spelling removed, is a valid binding again.
    assert cancelled == [("role-names-collide", "one-role-missing"), ("compatibility-form-collides", "one-role-missing")]
    # Every model-step rule was seen winning over a later one, except the three the
    # table cannot pair; test_t5_hand_built_order_witnesses covers those.
    assert earlier_rules == set(corpus.MODEL_RULES) - {
        "binding:role-arity", "binding:key-role", "binding:incompatible-keys"}


def test_t5_hand_built_order_witnesses(tmp_path):
    """Bindings with two defects, for the adjacent rules the refusal table cannot pair."""
    from gnd.export.ossie import render_ossie
    from gnd.export.physical_binding import BindingError

    def rule(case, patch):
        base = json.loads((corpus.CORPUS / case / "binding.json").read_text(encoding="utf-8"))
        path = tmp_path / "binding.json"
        path.write_text(json.dumps(corpus.apply_patch(base, patch)))
        with pytest.raises(BindingError) as caught:
            render_ossie(corpus.model_path(case), output_format="yaml", physical_binding=path)
        return caught.value.rule

    arity = {"op": "replace", "path": "/roles/city_in_state/state", "value": ["city.st_cd"]}
    mismatch = {"op": "add", "path": "/tables/country/columns/name/targets",
                "value": [{"kind": "role", "fact_type": "country_has_name", "role": "country"}]}
    assert rule("V3", [arity, mismatch]) == "binding:role-arity"
    assert rule("V3", [mismatch]) == "binding:target-mismatch"
    # One column of a home table's key holding another entity: a key-role defect and an
    # incompatible-keys defect at once. Without the home, only the second remains.
    both = {"op": "replace", "path": "/roles/course_has_title/course", "value": ["uni.student.nr"]}
    no_home = {"op": "remove", "path": "/tables/uni.student/columns/nr/targets"}
    assert rule("V2", [both]) == "binding:key-role"
    assert rule("V2", [both, no_home]) == "binding:incompatible-keys"
    wrong_player = {"op": "replace", "path": "/tables/uni.enrolled/columns/student_nr/targets/0/object_type",
                    "value": "course"}
    assert rule("V2", [wrong_player, both]) == "binding:target-mismatch"


def test_t5_binding_syntax_and_schema_come_before_the_model(tmp_path, capsys):
    from gnd import cli

    broken_model = tmp_path / "model.yaml"
    broken_model.write_text("not: [a model")
    missing_model = tmp_path / "absent.yaml"
    for row_id in ("truncated", "missing-roles"):
        row = next(r for r in ROWS if r["id"] == row_id)
        directory = tmp_path / row_id
        directory.mkdir()
        binding = _write_refusal(row, directory)
        for model in (broken_model, missing_model):
            assert cli.main(_argv(model, directory / "o.yaml", "--physical-binding", str(binding))) == 3
            assert row["rule"] in capsys.readouterr().err
    # The model's own refusals come before the binding's names.
    row = next(r for r in ROWS if r["id"] == "unknown-fact-type")
    directory = tmp_path / "names"
    directory.mkdir()
    binding = _write_refusal(row, directory)
    assert cli.main(_argv(broken_model, directory / "o.yaml", "--physical-binding", str(binding))) == 3
    assert "binding:" not in capsys.readouterr().err
    assert cli.main(_argv(missing_model, directory / "o.yaml", "--physical-binding", str(binding))) == 66


def test_t5_a_binding_refusal_comes_before_strict_and_size(tmp_path, capsys):
    from gnd import cli

    document = relational.load_yaml(corpus.model_path("V1"))
    document["fact_types"][0]["sample_population"] = [{"customer": 1, "email": "a@example.org"}]
    model = tmp_path / "model.json"
    model.write_text(json.dumps(document))
    good = corpus.CORPUS / "V1" / "binding.json"
    bad = _write_refusal(next(r for r in ROWS if r["id"] == "unknown-role"), tmp_path)
    argv = _argv(model, tmp_path / "o.yaml", "--strict", "--max-output-bytes", "1")
    assert cli.main([*argv, "--physical-binding", str(bad)]) == 3
    assert "binding:unknown-role" in capsys.readouterr().err
    assert cli.main([*argv, "--physical-binding", str(good)]) == 3
    assert "population:out-of-scope" in capsys.readouterr().err


def test_t5_usage_and_missing_file(tmp_path, capsys):
    from gnd import cli

    model = corpus.model_path("V1")
    binding = corpus.CORPUS / "V1" / "binding.json"
    with pytest.raises(SystemExit) as caught:
        cli.main(_argv(model, tmp_path / "o.yaml", "--ontology-only", "--physical-binding", str(binding)))
    assert caught.value.code == 64
    assert "--ontology-only" in capsys.readouterr().err
    assert cli.main(_argv(model, tmp_path / "o.yaml", "--physical-binding", str(tmp_path / "absent.json"))) == 66
    assert not list(tmp_path.iterdir())
    from gnd.export.ossie import render_ossie

    with pytest.raises(ValueError, match="relational"):
        render_ossie(model, output_format="yaml", relational=False, physical_binding=binding)


# --- T6: unbound fact types and the shared walk ---------------------------------------------------


def _generated(tmp_path, entities, fact_types, keep=lambda fact_type: True):
    from support.binding_large import binding_from_rmap
    from support.rmap_large import large_rmap_model

    from gnd.model import load_model

    model = tmp_path / f"model{entities}.json"
    model.write_text(json.dumps(large_rmap_model(entities, fact_types), separators=(",", ":")))
    binding = tmp_path / f"binding{entities}.json"
    binding.write_text(json.dumps(binding_from_rmap(load_model(model), keep), separators=(",", ":")))
    return model, binding


def test_t6_unbound_fact_types_are_listed_and_the_rmap_is_not_run(tmp_path, monkeypatch):
    import hashlib

    from gnd.export import ossie
    from gnd.model import load_model
    from gnd.model_index import ModelIndex

    model, binding = _generated(tmp_path, 40, 120, keep=lambda fact_type: int(fact_type[1:]) % 2 == 0)

    def refuse(*_args, **_kwargs):
        raise AssertionError("the Rmap ran on a binding run")

    monkeypatch.setattr(ossie, "map_model", refuse)
    bundle = ossie.render_ossie(model, output_format="json", physical_binding=binding)
    ontology, semantic, mapping = (json.loads(part) for part in (bundle.document, bundle.semantic_model, bundle.mapping))
    payload = json.loads(mapping["custom_extensions"][0]["data"])
    assert payload["binding_sha256"] == hashlib.sha256(binding.read_bytes()).hexdigest()
    loaded = load_model(model)
    expected = []
    for fact in ModelIndex.for_model(loaded).iter_fact_types_shared():
        expected.append(("fact_type", fact["id"]))
        expected += [("constraint", f"fact_types/{fact['id']}/constraints/{i}")
                     for i, _ in enumerate(fact.get("constraints") or ())]
    assert sorted((row["kind"], row["id"]) for row in payload["dispositions"]) == sorted(expected)
    facts = {row["id"]: row for row in payload["dispositions"] if row["kind"] == "fact_type"}
    assert len(facts) == 120
    for fact_type, row in facts.items():
        assert row["reason"] == (None if int(fact_type[1:]) % 2 == 0 else "unbound"), fact_type
    linked = relational.cross_check(ontology, semantic, mapping)
    assert sorted(linked) == sorted(f for f, row in facts.items() if row["reason"] is None)
    constraints = [row for row in payload["dispositions"] if row["kind"] == "constraint"]
    assert {row["reason"] for row in constraints} == {None, "unbound"}


# --- T7: without the flag nothing changes ---------------------------------------------------------

OB4_BASELINE = json.loads((corpus.ROOT / "tests/fixtures/ossie_ob4_baseline.json").read_bytes())


@pytest.mark.parametrize("key", sorted(OB4_BASELINE))
def test_t7_without_the_flag_the_relational_files_equal_the_baseline(key):
    import hashlib

    from gnd.export.ossie import render_ossie

    relative, _, output_format = key.partition("::")
    try:
        bundle = render_ossie(corpus.ROOT / relative, output_format=output_format)
        actual = {
            name: None if getattr(bundle, name) is None else hashlib.sha256(getattr(bundle, name)).hexdigest()
            for name in ("semantic_model", "mapping")
        }
    except Exception as error:  # noqa: BLE001 -- the baseline records refusals by type and text
        actual = {"refused": f"{type(error).__name__}: {error}"}
    assert actual == OB4_BASELINE[key]


# --- T8, T9: hostile input ------------------------------------------------------------------------


def _pointers(value, path=()):
    yield path
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _pointers(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _pointers(child, (*path, index))


def test_t8_a_wrong_value_anywhere_is_a_binding_refusal_or_harmless(tmp_path):
    """Every node of a valid binding replaced by each kind of JSON value in turn."""
    from gnd.export.ossie import render_ossie
    from gnd.export.physical_binding import RULE_ORDER, BindingError

    base = json.loads((corpus.CORPUS / "V3" / "binding.json").read_text(encoding="utf-8"))
    model = corpus.model_path("V3")
    path = tmp_path / "binding.json"
    outcomes = {"accepted": 0}
    for pointer in list(_pointers(base))[1:]:
        for replacement in (None, True, 7, 1.5, "x", "", [], ["x"], {}, {"x": 1}):
            document = json.loads(json.dumps(base))
            parent = document
            for part in pointer[:-1]:
                parent = parent[part]
            parent[pointer[-1]] = replacement
            path.write_text(json.dumps(document))
            try:
                render_ossie(model, output_format="yaml", physical_binding=path)
                outcomes["accepted"] += 1
            except BindingError as error:
                assert error.rule in RULE_ORDER
                outcomes[error.rule] = outcomes.get(error.rule, 0) + 1
    # 910 replacements on 2026-11-24: 843 refused by the schema, 19 harmless, the rest by name.
    assert sum(outcomes.values()) >= 900
    assert outcomes["binding:schema"] >= 800 and len(outcomes) >= 6, outcomes


def test_t8_arbitrary_bytes_are_refused_by_name(tmp_path):
    from gnd.export.physical_binding import BindingError, read_binding

    path = tmp_path / "binding.json"
    samples = [b"", b"\x00", b"\xff\xfe", b"null", b"0", b'"text"', b"[", b"{" * 100, b'{"a":' * 70 + b"1" + b"}" * 70,
               b'{"schema": Infinity}', b'{"schema": -Infinity}', b"1e400", b"\xef\xbb\xbf{}", b"{}\n{}"]
    for sample in samples:
        path.write_bytes(sample)
        with pytest.raises(BindingError) as caught:
            read_binding(path)
        assert caught.value.rule in ("binding:syntax", "binding:schema"), sample
    with pytest.raises(FileNotFoundError):
        read_binding(tmp_path / "absent.json")


@pytest.mark.parametrize(("written", "normal"), [
    ("email", "email"), ("E-Mail", "email"), (" e_mail ", "email"), ("ｅｍａｉｌ", "email"), ("ﬁle", "file"),
    ("Straße", "strasse"), ("room２", "room2"), ("İd", "i̇d".replace("̇", "")), ("--", ""), ("", ""), ("  ", ""),
])
def test_t9_role_name_normalization(written, normal):
    from gnd.export.physical_binding import normalize_role_name

    if written == "İd":  # the dot above is a combining mark, which is neither a letter nor a digit
        assert normalize_role_name(written) == "id"
    else:
        assert normalize_role_name(written) == normal


def test_t9_role_names_that_collide_in_the_model_are_refused(tmp_path):
    from gnd.export.ossie import render_ossie
    from gnd.export.physical_binding import BindingError

    document = relational.load_yaml(corpus.model_path("V1"))
    fact = document["fact_types"][0]
    fact["roles"][0]["role_name"] = "e_mail"
    for constraint in fact["constraints"]:
        if "roles" in constraint:
            constraint["roles"] = ["e_mail"]
        else:
            constraint["role"] = "e_mail"
    model = tmp_path / "model.json"
    model.write_text(json.dumps(document))
    binding = json.loads((corpus.CORPUS / "V1" / "binding.json").read_text(encoding="utf-8"))
    binding["roles"]["customer_has_email"] = {"e_mail": ["cust.cust_id"], "email": ["cust.email_addr"]}
    del binding["tables"]["cust"]["columns"]["email_addr"]["targets"]
    path = tmp_path / "binding.json"
    path.write_text(json.dumps(binding))
    with pytest.raises(BindingError) as caught:
        render_ossie(model, output_format="yaml", physical_binding=path)
    assert caught.value.rule == "binding:role-name"
    # Unbound, the same fact type is no obstacle.
    del binding["roles"]["customer_has_email"]
    path.write_text(json.dumps(binding))
    assert render_ossie(model, output_format="yaml", physical_binding=path).mapping is not None


# --- T10: scale -----------------------------------------------------------------------------------


def test_t10_binding_time_is_bounded_and_not_quadratic(tmp_path):
    from time import monotonic

    from gnd.export.ossie import render_ossie
    from gnd.input_policy import MAX_BYTES

    times = {}
    for scale in (1, 5):
        model, binding = _generated(tmp_path, 280 * scale, 900 * scale)
        best = float("inf")
        for _ in range(2):
            start = monotonic()
            bundle = render_ossie(model, output_format="json", max_output_bytes=268435456, physical_binding=binding)
            best = min(best, monotonic() - start)
        assert bundle.mapping is not None
        times[scale] = best
    # 1,400 entities and 4,500 fact types (2,950 tables): 4.1 s with the binding against 3.4 s with
    # the Rmap, ratio 5.0 to one fifth of that scale; the binding file is 1.2 MB. 2026-11-24.
    assert binding.stat().st_size < MAX_BYTES // 2
    assert times[5] < 60
    assert times[5] / times[1] < 12  # linear about 5; quadratic about 25


# --- T11, T12: the type map and the schema --------------------------------------------------------


def test_t11_the_sql_type_map_is_closed_and_literal():
    from gnd.export.physical_binding import SQL_TYPES, sql_datatype

    table = {
        "String": ["char", "character", "varchar", "character varying", "nchar", "nvarchar", "text", "string", "uuid"],
        "Integer": ["smallint", "integer", "int", "bigint", "tinyint", "int2", "int4", "int8", "serial", "bigserial",
                    "long", "short", "byte"],
        "Decimal": ["numeric", "decimal", "dec", "number"],
        "Float": ["real", "float", "float4", "float8", "double", "double precision"],
        "Boolean": ["boolean", "bool"],
        "Date": ["date"],
        "Time": ["time", "time without time zone"],
        "DateTime": ["timestamp", "timestamp without time zone", "timestamp_ntz", "datetime"],
        "DateTimeTz": ["timestamp with time zone", "timestamptz", "timestamp_ltz"],
        "Opaque": ["bytea", "binary", "varbinary", "blob", "json", "jsonb"],
    }
    assert SQL_TYPES == {name: datatype for datatype, names in table.items() for name in names}
    core = json.loads((corpus.ROOT / "src/gnd/schema/ossie/core-spec.json").read_text())
    assert set(table) <= set(core["$defs"]["DataType"]["enum"])
    for datatype, names in table.items():
        for name in names:
            assert sql_datatype(name) == sql_datatype(name.upper()) == sql_datatype(f"  {name}  ") == datatype


@pytest.mark.parametrize(("sql_type", "datatype"), [
    ("VARCHAR(20)", "String"), ("varchar ( 20 )", "String"), ("NUMERIC(10,2)", "Decimal"), ("numeric(10, 2)", "Decimal"),
    ("TIMESTAMP(6) WITH TIME ZONE", "DateTimeTz"), ("timestamp   with time  zone", "DateTimeTz"),
    ("Double Precision", "Float"), ("character varying (320)", "String"),
    ("INTEGER[]", None), ('"char"', None), ("varchar(20)(3)", None), ("(20) varchar", None), ("varchar(", None),
    ("varchar()", None), ("varchar(a)", None), ("varchar(1,)", None), ("geography", None), ("int unsigned", None),
    ("", None), ("   ", None), ("numeric(-1)", None), ("var-char", None), ("ｉｎｔ", None),
])
def test_t11_sql_types_are_lexed_not_pattern_matched(sql_type, datatype):
    from gnd.export.physical_binding import sql_datatype

    assert sql_datatype(sql_type) == datatype


def test_t11_an_unknown_type_is_kept_and_not_refused(tmp_path):
    binding = json.loads((corpus.CORPUS / "V1" / "binding.json").read_text(encoding="utf-8"))
    binding["tables"]["cust"]["columns"]["email_addr"]["sql_type"] = "CITEXT[]"
    del binding["tables"]["cust"]["columns"]["cust_id"]["sql_type"]
    path = tmp_path / "binding.json"
    path.write_text(json.dumps(binding))
    from gnd.export.ossie import render_ossie

    semantic = json.loads(render_ossie(corpus.model_path("V1"), output_format="json", physical_binding=path).semantic_model)
    key, email = semantic["datasets"][0]["fields"]
    assert "datatype" not in email and email["custom_extensions"] == [{"vendor_name": "GND", "data": '{"sql_type":"CITEXT[]"}'}]
    assert "datatype" not in key and "custom_extensions" not in key


def test_t12_the_packaged_schema_is_closed_and_names_the_documented_members():
    from importlib.resources import files

    from jsonschema import Draft202012Validator

    schema = json.loads(files("gnd").joinpath("schema", "physical-binding.schema.json").read_bytes())
    Draft202012Validator.check_schema(schema)
    assert schema["$id"] == "urn:gnd:physical-binding:1"
    assert schema["properties"]["schema"] == {"const": "gnd-physical-binding/1"}
    members = set()

    def walk(node):
        if isinstance(node, dict):
            if "properties" in node:
                assert node.get("additionalProperties") is False, node
                members.update(node["properties"])
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(schema)
    assert members == {"schema", "tables", "roles", "extension_roles", "columns", "primary_key", "unique_keys",
                       "sql_type", "targets", "references", "table", "kind", "object_type", "fact_type", "role", "column"}


# --- Rules implementation settled (OB4 spec section 12) -------------------------------------------


def _bound(tmp_path, case, patch):
    from gnd.export.ossie import render_ossie

    base = json.loads((corpus.CORPUS / case / "binding.json").read_text(encoding="utf-8"))
    path = tmp_path / "binding.json"
    path.write_text(json.dumps(corpus.apply_patch(base, patch)))
    bundle = render_ossie(corpus.model_path(case), output_format="json", physical_binding=path)
    mapping = json.loads(bundle.mapping)
    return json.loads(bundle.semantic_model), mapping, json.loads(mapping["custom_extensions"][0]["data"])


def test_a_fact_type_bound_across_tables_is_listed_not_refused(tmp_path):
    """G14: the fact type's State role is bound in `city` and its population in `state`."""
    patch = [{"op": "replace", "path": "/roles/state_has_population/state", "value": ["city.st_country_cd", "city.st_cd"]}]
    _semantic, mapping, payload = _bound(tmp_path, "V3", patch)
    rows = {(row["kind"], row["id"]): row for row in payload["dispositions"]}
    assert rows[("fact_type", "state_has_population")]["reason"] == "spans-tables"
    assert rows[("constraint", "fact_types/state_has_population/constraints/0")]["reason"] == "spans-tables"
    state = next(e for e in mapping["concept_mappings"] if e["concept"] == "State")
    assert [tree["children"][0]["relationship"] for tree in state["link_mappings"]] == ["state_in_country", "state_has_code"]


def test_an_extension_role_across_tables_is_listed_with_each_column_table(tmp_path):
    patch = [{"op": "add", "path": "/extension_roles", "value": {"city_in_state": {
        "city": ["city.id"], "state": ["state.country_cd", "city.st_cd"]}}},
        {"op": "remove", "path": "/roles/city_in_state"}]
    _semantic, _mapping, payload = _bound(tmp_path, "V3", patch)
    assert payload["extension_roles"] == [
        {"fact_type": "city_in_state", "role": "city", "table": "city", "columns": ["id"]},
        {"fact_type": "city_in_state", "role": "state", "table": None,
         "columns": [{"table": "state", "column": "country_cd"}, {"table": "city", "column": "st_cd"}]},
    ]


def test_an_ambiguous_spelling_is_refused_only_when_it_is_used(tmp_path):
    patch = [{"op": "add", "path": "/tables/a", "value": {"columns": {"b.c": {}}}},
             {"op": "add", "path": "/tables/a.b", "value": {"columns": {"c": {}}}}]
    semantic, _mapping, _payload = _bound(tmp_path, "V1", patch)
    assert [d["name"] for d in semantic["datasets"]] == ["a", "a.b", "cust"]


def test_a_declared_home_whose_key_is_not_the_identifier_gets_no_object_mapping(tmp_path):
    """V5 with `timetable` marked as Room's home: its key is (slot, staff), not a room number."""
    patch = [{"op": "add", "path": f"/tables/timetable/columns/{column}/targets",
              "value": [{"kind": "identifier", "object_type": "room"}]} for column in ("slot_cd", "staff_no")]
    from gnd.export.physical_binding import BindingError

    with pytest.raises(BindingError) as caught:
        _bound(tmp_path, "V5", patch)
    assert caught.value.rule == "binding:key-role"  # the key columns hold a Slot and a Lecturer


def test_two_homes_for_one_object_type_use_the_first_table(tmp_path):
    patch = [{"op": "add", "path": "/tables/archive", "value": {
        "columns": {"old_id": {"targets": [{"kind": "identifier", "object_type": "customer"}]}}, "primary_key": ["old_id"]}}]
    _semantic, mapping, _payload = _bound(tmp_path, "V1", patch)
    (customer,) = mapping["concept_mappings"]
    assert customer["object_mappings"] == [{"expression": '"ARCHIVE"."OLD_ID"'}]


def test_an_entity_the_ontology_does_not_identify_is_listed_as_identification_differs(tmp_path):
    """A nonfunctional external key has no identifier in the ontology."""
    from gnd.export.ossie import render_ossie

    model = relational.load_yaml(relational.rmap_case("14"))
    code = next(fact for fact in model["fact_types"] if fact["id"] == "state_has_code")
    code["constraints"] = [row for row in code["constraints"] if row["type"] != "uniqueness"]
    source = tmp_path / "model.orm.json"
    source.write_text(json.dumps(model))
    binding = {"schema": "gnd-physical-binding/1",
               "tables": {"p": {"columns": {"id": {}, "pop": {}, "extra": {}}, "primary_key": ["id"]}},
               "roles": {"state_has_population": {"state": ["p.id", "p.extra"], "population": ["p.pop"]}}}
    path = tmp_path / "binding.json"
    path.write_text(json.dumps(binding))
    mapping = json.loads(render_ossie(source, output_format="json", physical_binding=path).mapping)
    payload = json.loads(mapping["custom_extensions"][0]["data"])
    assert payload["unmapped_links"] == [{"fact_type": "state_has_population", "reason": "identification-differs"}]


@pytest.mark.parametrize("width", [1, 2])
def test_physical_binding_checks_the_projected_unit_key_arity(tmp_path, width):
    from gnd.export.ossie import render_ossie
    from gnd.export.physical_binding import BindingError

    binding = {"schema": "gnd-physical-binding/1",
               "tables": {"p": {"columns": {"id": {}, "cm": {}, "extra": {}}, "primary_key": ["id"]}},
               "roles": {"person_has_height": {"person": ["p.id"], "height": ["p.cm", "p.extra"][:width]}}}
    path = tmp_path / "binding.json"
    path.write_text(json.dumps(binding))
    source = relational.rmap_case("23")
    if width == 2:
        with pytest.raises(BindingError) as caught:
            render_ossie(source, output_format="json", physical_binding=path)
        assert caught.value.rule == "binding:role-arity"
    else:
        bundle = render_ossie(source, output_format="json", physical_binding=path)
        mapping = json.loads(bundle.mapping)
        payload = json.loads(mapping["custom_extensions"][0]["data"])
        assert "unmapped_links" not in payload
        linked = relational.cross_check(json.loads(bundle.document), json.loads(bundle.semantic_model), mapping)
        assert "person_has_height" in linked


# --- Review round 1 regressions (notes/reviews/phase-OB4-r1, F1-F6) -----------------------------


@pytest.mark.parametrize("where", ("sql_type", "table", "column", "role"))
def test_r1_f1_a_lone_surrogate_anywhere_is_a_syntax_refusal(tmp_path, where, capsys):
    from gnd import cli

    texts = {
        "sql_type": '{"schema":"gnd-physical-binding/1","tables":{"t":{"columns":{"c":{"sql_type":"\\ud800"}}}},"roles":{}}',
        "table": '{"schema":"gnd-physical-binding/1","tables":{"t\\udc00":{"columns":{"c":{}}}},"roles":{}}',
        "column": '{"schema":"gnd-physical-binding/1","tables":{"t":{"columns":{"\\ud83d":{}}}},"roles":{}}',
        "role": '{"schema":"gnd-physical-binding/1","tables":{"t":{"columns":{"c":{}}}},'
                '"roles":{"customer_has_email":{"\\udfff":["t.c"]}}}',
    }
    binding = tmp_path / "binding.json"
    binding.write_text(texts[where])
    for output_format in ("yaml", "json"):
        argv = _argv(corpus.model_path("V1"), tmp_path / f"o.{output_format}", "--format", output_format)
        assert cli.main([*argv, "--physical-binding", str(binding)]) == 3
        assert "binding:syntax" in capsys.readouterr().err
    assert [p.name for p in tmp_path.iterdir()] == ["binding.json"]


def _chain_model(depth):
    """Entity e0 is identified through e1, which is identified through e2, and so on."""
    modality = {"source": "explicit", "status": "confirmed", "modality": "alethic", "provenance": {"user_quote": "x"}}
    objects = [{"id": "code", "name": "Code", "kind": "value", "primitive": "String"}]
    facts, constraints = [], []
    for level in range(depth + 1):
        name, label = f"e{level:04d}", f"E{level:04d}"
        if level == depth:
            objects.append({"id": name, "name": label, "kind": "entity", "reference": {"mode": "popular", "value_type": "code"}})
            break
        objects.append({"id": name, "name": label, "kind": "entity", "reference": {"mode": "external"}})
        for role, target, target_label in (("next", f"e{level + 1:04d}", f"E{level + 1:04d}"), ("code", "code", "Code")):
            facts.append({"id": f"{name}_{role}", "reading": "{" + label + "} has {" + target_label + "}",
                          "roles": [{"object_type": name, "role_name": "self"}, {"object_type": target, "role_name": role}],
                          "constraints": [{"type": "uniqueness", "roles": ["self"], **modality},
                                          {"type": "mandatory", "role": "self", **modality}]})
        constraints.append({"type": "uniqueness", "scope": "external", "preferred": True, **modality, "role_refs": [
            {"fact_type": f"{name}_next", "role": "next"}, {"fact_type": f"{name}_code", "role": "code"}]})
    return {"version": 1, "source": {"kind": "text-conversation", "confidence": "standard", "mode": "guided"},
            "object_types": objects, "fact_types": facts, "constraints": constraints}


def test_r1_f2_a_deep_identifier_chain_is_listed_not_followed(tmp_path):
    from gnd.export.ossie import render_ossie
    from gnd.export.physical_binding import MAX_IDENTIFIER_DEPTH

    assert MAX_IDENTIFIER_DEPTH == 8
    model = tmp_path / "model.json"
    model.write_text(json.dumps(_chain_model(1100)))
    binding = tmp_path / "binding.json"
    # e1099 is one level above the simple end of the chain; e0000 is 1100 levels above it.
    binding.write_text(json.dumps({
        "schema": "gnd-physical-binding/1",
        "tables": {"t": {"columns": {"a": {}, "b": {}, "c": {}}}},
        "roles": {
            "e1099_code": {"self": ["t.a", "t.b"], "code": ["t.b"]},
            "e0000_code": {"self": ["t.a"], "code": ["t.c"]},
        },
    }))
    bundle = render_ossie(model, output_format="json", physical_binding=binding, max_output_bytes=268435456)
    mapping = json.loads(bundle.mapping)
    payload = json.loads(mapping["custom_extensions"][0]["data"])
    assert {"fact_type": "e0000_code", "reason": "identification-differs"} in payload["unmapped_links"]
    linked = relational.cross_check(json.loads(bundle.document), json.loads(bundle.semantic_model), mapping)
    assert linked == ["e1099_code"]


def test_r1_f2_the_depth_limit_itself_is_mapped(tmp_path):
    from gnd.export.ossie import render_ossie
    from gnd.export.physical_binding import MAX_IDENTIFIER_DEPTH, BindingError

    depth = MAX_IDENTIFIER_DEPTH
    model = tmp_path / "model.json"
    model.write_text(json.dumps(_chain_model(depth + 1)))
    columns = [f"k{n}" for n in range(depth + 1)]

    def binding(fact, width):
        path = tmp_path / f"{fact}.json"
        path.write_text(json.dumps({
            "schema": "gnd-physical-binding/1", "tables": {"t": {"columns": {name: {} for name in [*columns, "v"]}}},
            "roles": {fact: {"self": [f"t.{c}" for c in columns[:width]], "code": ["t.v"]}}}))
        return path

    # e0001 nests exactly `depth` levels: its identifier is depth + 1 columns wide.
    bundle = render_ossie(model, output_format="json", physical_binding=binding("e0001_code", depth + 1))
    assert "unmapped_links" not in json.loads(json.loads(bundle.mapping)["custom_extensions"][0]["data"])
    with pytest.raises(BindingError) as caught:
        render_ossie(model, output_format="json", physical_binding=binding("e0001_code", depth))
    assert caught.value.rule == "binding:role-arity"
    # e0000 nests one level more: any column count is accepted, and the link is listed.
    bundle = render_ossie(model, output_format="json", physical_binding=binding("e0000_code", 1))
    payload = json.loads(json.loads(bundle.mapping)["custom_extensions"][0]["data"])
    assert payload["unmapped_links"] == [{"fact_type": "e0000_code", "reason": "identification-differs"}]


def test_r1_f3_an_external_uniqueness_is_placed_by_its_own_roles(tmp_path):
    """Both identifying fact types span tables, but the roles the uniqueness names sit in `state`."""
    move = [{"op": "replace", "path": f"/roles/{fact}/state", "value": ["city.st_country_cd", "city.st_cd"]}
            for fact in ("state_in_country", "state_has_code")]
    _semantic, _mapping, payload = _bound(tmp_path, "V3", move)
    rows = {(row["kind"], row["id"]): row for row in payload["dispositions"]}
    assert rows[("fact_type", "state_in_country")]["reason"] == "spans-tables"
    assert rows[("constraint", "constraints/0")]["carried_as"] == ["primary_key", "state"]
    # Without that primary key, the same uniqueness is derived as a unique key.
    semantic, _mapping, payload = _bound(tmp_path, "V3", [
        *move,
        {"op": "remove", "path": "/tables/state/primary_key"},
        {"op": "remove", "path": "/tables/state/columns/country_cd/targets"},
        {"op": "remove", "path": "/tables/state/columns/state_cd/targets"},
        {"op": "remove", "path": "/tables/city/columns/st_country_cd/references"},
        {"op": "remove", "path": "/tables/city/columns/st_cd/references"},
    ])
    rows = {(row["kind"], row["id"]): row for row in payload["dispositions"]}
    assert rows[("constraint", "constraints/0")]["carried_as"] == ["unique_key", "state", "country_cd", "state_cd"]
    assert next(d for d in semantic["datasets"] if d["name"] == "state")["unique_keys"] == [["country_cd", "state_cd"]]


@pytest.mark.parametrize("order", (("z", "a"), ("a", "z")))
def test_r1_f4_the_reported_foreign_key_does_not_depend_on_member_order(tmp_path, order):
    from gnd.export.ossie import render_ossie
    from gnd.export.physical_binding import BindingError

    references = {"z": ["x", "y"], "a": ["x", "y", "w"]}
    binding = {"schema": "gnd-physical-binding/1", "roles": {}, "tables": {
        "target": {"columns": {"x": {}, "y": {}, "w": {}}, "primary_key": ["x", "y", "w"]},
        "source": {"columns": {name: {"references": {"table": "target", "columns": references[name]}} for name in order}},
    }}
    path = tmp_path / "binding.json"
    path.write_text(json.dumps(binding))
    with pytest.raises(BindingError) as caught:
        render_ossie(corpus.model_path("V1"), output_format="yaml", physical_binding=path)
    assert caught.value.rule == "binding:reference-group"
    assert "1 column(s) reference 3 column(s)" in str(caught.value)  # the group of column `a`


@pytest.mark.parametrize("sql_type", ("double(2)precision", "timestamp(6)with time zone", "varchar(20)x", "numeric(1)2"))
def test_r1_f5_a_word_after_the_list_needs_a_space(sql_type):
    from gnd.export.physical_binding import sql_datatype

    assert sql_datatype(sql_type) is None
    assert sql_datatype("timestamp(6) with time zone") == "DateTimeTz"
    assert sql_datatype("double precision(2)") == "Float"


def test_r1_f6_a_schema_refusal_names_an_escaped_pointer_in_sorted_order(tmp_path):
    from gnd.export.physical_binding import BindingError, read_binding

    path = tmp_path / "binding.json"
    path.write_text(json.dumps({"schema": "gnd-physical-binding/1", "roles": {},
                                "tables": {"a/b": {"columns": {}}, "a~b": {"columns": {}}}}))
    with pytest.raises(BindingError) as caught:
        read_binding(path)
    assert caught.value.rule == "binding:schema"
    assert "at /tables/a~0b/columns:" in str(caught.value)


# --- OB5: table and column names that are not regular identifiers ---------------------------


def irregular_binding(tmp_path):
    """Corpus case V1 with its table and one column renamed to names Ossie keeps as written."""
    binding = json.loads((corpus.CORPUS / "V1" / "binding.json").read_text(encoding="utf-8"))
    table = binding["tables"].pop("cust")
    table["columns"] = {("e-mail addr" if name == "email_addr" else name): body
                        for name, body in table["columns"].items()}
    binding["tables"]["Sales Dept.cust-2024"] = table
    binding["roles"] = {
        "customer_has_email": {
            "customer": [{"table": "Sales Dept.cust-2024", "column": "cust_id"}],
            "email": [{"table": "Sales Dept.cust-2024", "column": "e-mail addr"}],
        }
    }
    path = tmp_path / "binding.json"
    path.write_text(json.dumps(binding), encoding="utf-8")
    return path


def test_ob5_names_that_are_not_regular_identifiers_are_quoted_as_written(tmp_path):
    from gnd.export.ossie import render_ossie
    from gnd.export.ossie_relational import validate_relational

    bundle = render_ossie(corpus.model_path("V1"), output_format="yaml", physical_binding=irregular_binding(tmp_path))
    semantic = relational.load_yaml_bytes(bundle.semantic_model)
    mapping = relational.load_yaml_bytes(bundle.mapping)
    validate_relational(semantic, mapping)
    (dataset,) = semantic["datasets"]
    assert [field["expression"]["sql"] for field in dataset["fields"]] == ['"CUST_ID"', '"e-mail addr"']
    (concept,) = mapping["concept_mappings"]
    assert concept["object_mappings"] == [{"expression": '"Sales Dept.cust-2024"."CUST_ID"'}]
    (link,) = concept["link_mappings"]
    assert link["children"][0]["object_mapping"]["expression"] == '"Sales Dept.cust-2024"."e-mail addr"'
    relational.cross_check(relational.load_yaml_bytes(bundle.document), semantic, mapping)


def test_close_names_collide_by_ossies_normalized_form(tmp_path):
    """Close review: two names that are not regular identifiers and differ only in case are
    distinct to Ossie, which keeps each as written, so they are two tables. Two regular
    names that differ only in case are one identifier and are still refused."""
    from gnd.export.ossie import INPUT_REFUSALS, render_ossie
    from gnd.export.ossie_relational import validate_relational

    def render(rename):
        binding = json.loads((corpus.CORPUS / "V1" / "binding.json").read_text(encoding="utf-8"))
        binding["tables"][rename["cust"]] = binding["tables"].pop("cust")
        binding["tables"][rename["other"]] = {"columns": {"note": {}, "Note": {}} if rename["columns"] else {"note": {}}}
        binding["roles"] = {"customer_has_email": {
            "customer": [{"table": rename["cust"], "column": "cust_id"}],
            "email": [{"table": rename["cust"], "column": "email_addr"}]}}
        path = tmp_path / f"{len(list(tmp_path.iterdir()))}.json"
        path.write_text(json.dumps(binding), encoding="utf-8")
        return render_ossie(corpus.model_path("V1"), output_format="yaml", physical_binding=path)

    bundle = render({"cust": "fin.cust", "other": "FIN.CUST", "columns": False})
    semantic = relational.load_yaml_bytes(bundle.semantic_model)
    mapping = relational.load_yaml_bytes(bundle.mapping)
    validate_relational(semantic, mapping)
    assert [dataset["name"] for dataset in semantic["datasets"]] == ["FIN.CUST", "fin.cust"]
    assert mapping["concept_mappings"][0]["object_mappings"] == [{"expression": '"fin.cust"."CUST_ID"'}]
    for rename in ({"cust": "cust", "other": "Cust", "columns": False},      # regular tables: one identifier
                   {"cust": "cust", "other": "fin.x", "columns": True}):     # regular columns note / Note
        with pytest.raises(INPUT_REFUSALS, match="binding:name-collision"):
            render(rename)
