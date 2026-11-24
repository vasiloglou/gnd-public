"""Authoring checks for the OB4 corpus (tests/fixtures/physical_binding).

The bindings, their expected files and the refusal table there are hand-written and
were approved before any binding reader existed. This module reads no binding the way
the product will: it checks the corpus against the packaged schema, the pinned Ossie
schemas, the real ontology export and the model.

Run: ``uv run python -m tests.support.physical_binding_corpus``
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

from tests.support import ossie_relational_corpus as relational

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "tests/fixtures/physical_binding"
SCHEMA = ROOT / "src/gnd/schema/physical-binding.schema.json"

#: The rule ids of OB4 spec §6.7, by step. Steps 2 and 3 need no model.
SYNTAX_RULES = ("binding:not-a-file", "binding:size", "binding:syntax")
SCHEMA_RULES = ("binding:schema",)
MODEL_RULES = (
    "binding:name-collision", "binding:unknown-table", "binding:unknown-column", "binding:ambiguous-column",
    "binding:unknown-fact-type", "binding:role-name", "binding:unknown-role", "binding:unknown-object-type",
    "binding:reference-group", "binding:reference-not-a-key", "binding:partial-fact-type", "binding:role-arity",
    "binding:target-mismatch", "binding:key-role", "binding:incompatible-keys",
)
RULES = (*SYNTAX_RULES, *SCHEMA_RULES, *MODEL_RULES)
BINDING_REASONS = {"unbound", "extension-role", "not-in-binding", "spans-tables", "not-relational",
                   "uniqueness-not-confirmed", "identification-differs"}


def cases() -> list[str]:
    return sorted(path.name for path in CORPUS.iterdir() if path.is_dir())


def model_path(case: str) -> Path:
    number = json.loads((CORPUS / case / "case.json").read_text(encoding="utf-8"))["model"]
    return relational.rmap_case(number)


def binding_schema() -> Draft202012Validator:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _token(part: str) -> str:
    return part.replace("~1", "/").replace("~0", "~")


def apply_patch(document, patch):
    """RFC 6902 `add`, `remove` and `replace` over RFC 6901 pointers; other ops are not used."""
    document = copy.deepcopy(document)
    for operation in patch:
        parts = [_token(part) for part in operation["path"].split("/")[1:]]
        parent = document
        for part in parts[:-1]:
            parent = parent[int(part)] if isinstance(parent, list) else parent[part]
        last = parts[-1]
        if isinstance(parent, list):
            index = len(parent) if last == "-" else int(last)
            if operation["op"] == "add":
                parent.insert(index, operation["value"])
            elif operation["op"] == "remove":
                del parent[index]
            else:
                assert operation["op"] == "replace" and index < len(parent)
                parent[index] = operation["value"]
        elif operation["op"] == "remove":
            del parent[last]
        else:
            assert operation["op"] in ("add", "replace")
            assert (last in parent) == (operation["op"] == "replace"), operation
            parent[last] = operation["value"]
    return document


def generated(kind: str) -> bytes | None:
    """The file text of a `generate` row; None for the directory row."""
    if kind == "directory":
        return None
    if kind == "oversize":
        return b"{" + b" " * (10 * 1024 * 1024) + b"}"
    if kind == "deep":
        return b"[" * 65 + b"]" * 65
    if kind == "long-integer":
        return b'{"schema": ' + b"9" * 5000 + b', "tables": {"t": {"columns": {"c": {}}}}, "roles": {}}'
    assert kind == "not-utf8", kind
    return b'{"schema": "gnd-physical-binding/1", "tables": {"t\xff": {"columns": {"c": {}}}}, "roles": {}}'


def refusal_rows() -> list[dict]:
    return json.loads((CORPUS / "refusals.json").read_text(encoding="utf-8"))["rows"]


def refusal_bytes(row) -> bytes | None:
    if "generate" in row:
        return generated(row["generate"])
    if "raw" in row:
        return row["raw"].encode("utf-8")
    base = json.loads((CORPUS / row["base"] / "binding.json").read_text(encoding="utf-8"))
    return json.dumps(apply_patch(base, row["patch"])).encode("utf-8")


def check_refusals() -> None:
    """Every rule id has a row, and each row fails at the step its rule belongs to."""
    from gnd.input_policy import MAX_BYTES, loads

    validator = binding_schema()
    rows = refusal_rows()
    ids = [row["id"] for row in rows]
    assert len(ids) == len(set(ids)), "duplicate row id"
    assert {row["rule"] for row in rows} == set(RULES), sorted(set(RULES) - {row["rule"] for row in rows})
    for row in rows:
        assert sum(key in row for key in ("base", "raw", "generate")) == 1, row["id"]
        data = refusal_bytes(row)
        if data is None:
            assert row["rule"] == "binding:not-a-file", row["id"]
            continue
        if len(data) > MAX_BYTES:
            assert row["rule"] == "binding:size", row["id"]
            continue
        try:
            document = loads(data, max_bytes=MAX_BYTES)
        except (ValueError, RecursionError, UnicodeDecodeError):
            assert row["rule"] == "binding:syntax", (row["id"], "does not parse")
            continue
        assert row["rule"] != "binding:syntax", (row["id"], "parses")
        valid = not list(validator.iter_errors(document))
        assert valid == (row["rule"] in MODEL_RULES), (row["id"], "schema-valid" if valid else "schema-invalid")
        if "base" in row:
            assert document != json.loads((CORPUS / row["base"] / "binding.json").read_text(encoding="utf-8"))


def check_valid(case: str) -> None:
    from gnd.export.ossie import render_ossie
    from gnd.export.ossie_relational import validate_relational
    from gnd.model import load_model
    from gnd.model_index import ModelIndex
    from gnd.values import model_identity

    directory = CORPUS / case
    binding_bytes = (directory / "binding.json").read_bytes()
    binding = json.loads(binding_bytes)
    assert not list(binding_schema().iter_errors(binding)), "binding is not schema-valid"
    semantic_bytes = (directory / "expected.semantic_model.yaml").read_bytes()
    mapping_bytes = (directory / "expected.mapping.yaml").read_bytes()
    semantic = relational.load_yaml_bytes(semantic_bytes)
    mapping = relational.load_yaml_bytes(mapping_bytes)
    payload = json.loads((directory / "expected.extension.json").read_text(encoding="utf-8"))
    model = load_model(model_path(case))
    ontology_bytes = render_ossie(model_path(case), output_format="yaml", relational=False).document
    ontology = relational.load_yaml_bytes(ontology_bytes)

    # 1. Exporter form, and the pinned Ossie schemas.
    assert relational.dump_yaml(semantic) == semantic_bytes
    assert relational.dump_yaml(mapping) == mapping_bytes
    validate_relational(semantic, mapping)

    # 2. The semantic model is the binding's tables: names, order, keys, foreign keys.
    tables = binding["tables"]
    assert [d["name"] for d in semantic["datasets"]] == sorted(tables)
    expected_relationships = []
    for dataset in semantic["datasets"]:
        table = tables[dataset["name"]]
        assert dataset["source"] == dataset["name"]
        assert [f["name"] for f in dataset["fields"]] == list(table["columns"])
        assert dataset.get("primary_key") == table.get("primary_key")
        if "unique_keys" in table:
            assert dataset.get("unique_keys", []) == table["unique_keys"]
        assert dataset["custom_extensions"] == [{"vendor_name": "GND", "data": '{"source_kind":"physical"}'}]
        for field in dataset["fields"]:
            column = table["columns"][field["name"]]
            wanted = ([{"vendor_name": "GND", "data": relational.extension_data({"sql_type": column["sql_type"]})}]
                      if "sql_type" in column else None)
            assert field.get("custom_extensions") == wanted, field["name"]
        groups: dict[tuple[str, tuple[str, ...]], list[str]] = {}
        for name, column in table["columns"].items():  # document order pairs with references.columns
            if "references" in column:
                key = (column["references"]["table"], tuple(column["references"]["columns"]))
                groups.setdefault(key, []).append(name)
        expected_relationships += [
            (dataset["name"], target, columns, list(target_columns)) for (target, target_columns), columns in groups.items()
        ]
    actual = [(r["from"], r["to"], r["from_columns"], r["to_columns"]) for r in semantic.get("relationships", [])]
    assert actual == expected_relationships
    assert len({r["name"] for r in semantic.get("relationships", [])}) == len(actual)

    # 3. The mapping is consistent with the real ontology and the semantic model.
    assert mapping["ontology_ref"] == {"name": ontology["name"], "iri": f"./{relational.OUT_NAME}"}
    linked = relational.cross_check(ontology, semantic, mapping)

    # 4. One walk: every fact type and constraint once; carried fact types are the linked ones.
    expected = []
    for fact in ModelIndex.for_model(model).iter_fact_types_shared():
        expected.append(("fact_type", fact["id"]))
        expected += [("constraint", f"fact_types/{fact['id']}/constraints/{i}")
                     for i, _ in enumerate(fact.get("constraints") or ())]
    expected += [("constraint", f"constraints/{i}") for i, _ in enumerate(model.constraints or ())]
    rows = payload["dispositions"]
    assert [(row["kind"], row["id"]) for row in rows] == sorted(expected)
    assert all(bool(row["carried_as"]) != (row["reason"] is not None) for row in rows)
    assert {row["reason"] for row in rows} - {None} <= BINDING_REASONS
    carried = {row["id"] for row in rows if row["kind"] == "fact_type" and row["reason"] is None}
    assert set(linked) == carried and len(linked) == len(set(linked))
    bound = set(binding["roles"])
    extension_only = set(binding.get("extension_roles", {})) - bound
    for row in rows:
        if row["kind"] == "fact_type":
            wanted = None if row["id"] in bound else "extension-role" if row["id"] in extension_only else "unbound"
            assert row["reason"] == wanted, row["id"]

    # 5. The extension is bound to the real ontology, the expected semantic model, the model
    #    and the binding file.
    (extension,) = mapping["custom_extensions"]
    assert extension["data"] == relational.extension_data(payload)
    assert set(payload) == {"schema", "model_identity", "ontology_sha256", "semantic_model_sha256",
                            "binding_sha256", "dispositions", "concepts", "extension_roles"}
    assert payload["schema"] == "gnd-ossie-relational/1"
    assert payload["ontology_sha256"] == hashlib.sha256(ontology_bytes).hexdigest()
    assert payload["semantic_model_sha256"] == hashlib.sha256(semantic_bytes).hexdigest()
    assert payload["binding_sha256"] == hashlib.sha256(binding_bytes).hexdigest()
    assert payload["model_identity"] == model_identity(model)
    listed = [(row["fact_type"], row["role"]) for row in payload["extension_roles"]]
    assert listed == sorted(listed) and {fact for fact, _ in listed} == set(binding.get("extension_roles", {}))
    fields = {d["name"]: {f["name"] for f in d["fields"]} for d in semantic["datasets"]}
    for row in payload["extension_roles"]:
        assert set(row["columns"]) <= fields[row["table"]]


def main() -> int:
    for case in cases():
        check_valid(case)
        print(f"{case}: ok")
    check_refusals()
    print(f"refusals: ok ({len(refusal_rows())} rows, {len(RULES)} rule ids)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
