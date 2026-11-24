"""Authoring checks for the OB3 corpus (tests/fixtures/ossie_relational).

The expected semantic models and mappings there are hand-derived and were approved
before any renderer existed. This module does not render them. It only:

- writes a mapping's ``GND`` extension string from the case's hand-written
  ``expected.extension.json`` (``assemble``), because that string is canonical JSON and
  is folded by the YAML dumper;
- checks each case against the pinned schemas, the real ontology export, and the
  owner-approved OB2 Rmap answer (``check``).

Run: ``uv run python -m tests.support.ossie_relational_corpus``
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from io import StringIO
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012
from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "tests/fixtures/ossie_relational"
RMAP = ROOT / "tests/fixtures/rmap"
SCHEMAS = ROOT / "src/gnd/schema/ossie"
UPSTREAM = "https://raw.githubusercontent.com/apache/ossie/main/"
OUT_NAME = "ontology.yaml"  # the corpus convention for OUT's basename

# The two shapes of expression the export writes, with each quoted identifier
# replaced by a placeholder: dataset.field, optionally inside a unary's CASE WHEN.
_SHAPES = {"?.?": 1, "CASE WHEN ?.? THEN ?.? END": 2}


def dump_yaml(document) -> bytes:
    """The ontology export's YAML settings (gnd.export.ossie.render_ossie)."""
    yaml = YAML(typ="safe", pure=True)
    yaml.version = (1, 1)
    yaml.default_flow_style = False
    yaml.sort_base_mapping_type_on_output = False
    stream = StringIO()
    yaml.dump(document, stream)
    return stream.getvalue().encode("utf-8")


def load_yaml(path: Path):
    return YAML(typ="safe", pure=True).load(path.read_text(encoding="utf-8"))


def load_yaml_bytes(data: bytes):
    return YAML(typ="safe", pure=True).load(data.decode("utf-8"))


def extension_data(payload) -> str:
    """Canonical JSON without its trailing newline."""
    from gnd.artifacts import canonical_json_bytes

    return canonical_json_bytes(payload).decode("utf-8").rstrip("\n")


def cases() -> list[str]:
    return sorted(path.name for path in CORPUS.iterdir() if path.is_dir())


def rmap_case(number: str) -> Path:
    (case,) = [path for path in (RMAP / "cases").iterdir() if path.name.startswith(number + "-")]
    return case / "model.yaml"


def assemble(number: str) -> None:
    """Write the extension string of expected.mapping.yaml from expected.extension.json."""
    directory = CORPUS / number
    mapping = load_yaml(directory / "expected.mapping.yaml")
    payload = json.loads((directory / "expected.extension.json").read_text(encoding="utf-8"))
    mapping["custom_extensions"] = [{"vendor_name": "GND", "data": extension_data(payload)}]
    (directory / "expected.mapping.yaml").write_bytes(dump_yaml(mapping))


def _validators(mapping_schema: Path):
    core = json.loads((SCHEMAS / "core-spec.json").read_text(encoding="utf-8"))
    ontology = json.loads((SCHEMAS / "ontology.json").read_text(encoding="utf-8"))
    mapping = json.loads(mapping_schema.read_text(encoding="utf-8"))
    registry = Registry().with_resources([
        (UPSTREAM + "core-spec/ossie-schema.json", Resource.from_contents(core, default_specification=DRAFT202012)),
        (UPSTREAM + "ontology/ontology.json", Resource.from_contents(ontology, default_specification=DRAFT202012)),
    ])
    return (
        Draft202012Validator(core, registry=registry),
        Draft202012Validator(mapping, registry=registry),
    )


def quoted_identifiers(expression: str) -> tuple[list[str], str]:
    """Lex SQL quoted identifiers: the names, and the text with each replaced by ``?``.

    Inside quotes a doubled quote is one quote character; an unclosed quote fails.
    """
    names, shape, position = [], [], 0
    while position < len(expression):
        if expression[position] != '"':
            shape.append(expression[position])
            position += 1
            continue
        name, position = [], position + 1
        while True:
            assert position < len(expression), f"unclosed identifier in {expression!r}"
            if expression[position] != '"':
                name.append(expression[position])
                position += 1
            elif expression[position + 1:position + 2] == '"':
                name.append('"')
                position += 2
            else:
                position += 1
                break
        names.append("".join(name))
        shape.append("?")
    return names, "".join(shape)


def expression_fields(expression: str) -> list[tuple[str, str]]:
    """The (dataset, field) pairs an exported expression names."""
    names, shape = quoted_identifiers(expression)
    assert shape in _SHAPES, f"expression outside the export's grammar: {expression!r}"
    return [(names[i], names[i + 1]) for i in range(0, len(names), 2)]


def cross_check(ontology, semantic, mapping) -> list[str]:
    """Check a mapping against its ontology and semantic model, from the documents alone.

    Returns the relationships its link mappings name, in document order.
    """
    names = [d["name"] for d in semantic["datasets"]]
    assert len(names) == len(set(names)), "duplicate dataset name"
    fields = {}
    for dataset in semantic["datasets"]:
        own = [f["name"] for f in dataset["fields"]]
        assert len(own) == len(set(own)), f"duplicate field in {dataset['name']}"
        fields[dataset["name"]] = set(own)
        for key in [dataset.get("primary_key", []), *dataset.get("unique_keys", [])]:
            assert set(key) <= set(own), (dataset["name"], key)
        for field in dataset["fields"]:
            assert quoted_identifiers(field["expression"]["sql"]) == ([field["name"].upper()], "?")
    related = [r["name"] for r in semantic.get("relationships", [])]
    assert len(related) == len(set(related)), "duplicate relationship name"
    for r in semantic.get("relationships", []):
        assert set(r["from_columns"]) <= fields[r["from"]] and set(r["to_columns"]) <= fields[r["to"]], r["name"]
        assert len(r["from_columns"]) == len(r["to_columns"]), r["name"]

    assert mapping["ontology_ref"]["name"] == ontology["name"]
    assert mapping["semantic_model_ref"]["name"] == semantic["name"]
    declared = {(d.upper(), f.upper()) for d, own in fields.items() for f in own}
    components = {c["concept"]: c for c in ontology["ontology"]}

    def ancestors(concept):
        seen, pending = [], [concept]
        while pending:
            current = pending.pop(0)
            if current in components and current not in seen:
                seen.append(current)
                pending += components[current].get("extends", [])
        return seen

    def relationship(concept, name):
        for owner in ancestors(concept):
            for candidate in components[owner].get("relationships", []):
                if candidate["name"] == name:
                    return candidate
        raise AssertionError(f"{name} is not declared on {concept}")

    def identify_by(concept):
        for owner in ancestors(concept):
            if components[owner].get("identify_by"):
                return components[owner]["identify_by"]
        return []

    def check_referents(node, concept):
        listed = [referent["relationship"] for referent in node["referent_mappings"]]
        assert listed == identify_by(concept), (concept, listed)
        for referent in node["referent_mappings"]:
            target = relationship(concept, referent["relationship"])["roles"][-1]["concept"]
            check_object(referent, target, nested=True)

    def check_object(node, concept, nested=False):
        assert ("expression" in node) != ("referent_mappings" in node)
        if "expression" in node:
            for field in expression_fields(node["expression"]):
                assert field in declared, field
            entity = components[concept]["type"] == "EntityType"
            # A bare expression finds an entity only through a one-relationship identifier.
            assert nested or not entity or len(identify_by(concept)) == 1, concept
            return
        check_referents(node, concept)

    linked = []

    def check_link(node, concept, level, prefix):
        if level > 1:
            object_concept = node["object_mapping"]["concept"]
        else:
            object_concept = concept
            assert "concept" not in node["object_mapping"]
        check_object(node["object_mapping"], object_concept)
        if "relationship" in node:
            roles = relationship(concept, node["relationship"]).get("roles", [])
            assert len(roles) + 1 == level, node["relationship"]
            assert [*prefix, object_concept][1:] == [role["concept"] for role in roles]
            linked.append(node["relationship"])
        for child in node.get("children", []):
            check_link(child, concept, level + 1, [*prefix, object_concept])

    mapped_concepts = [entry["concept"] for entry in mapping["concept_mappings"]]
    order = [c["concept"] for c in ontology["ontology"]]
    assert mapped_concepts == [c for c in order if c in set(mapped_concepts)]
    for entry in mapping["concept_mappings"]:
        concept = entry["concept"]
        if "object_mappings" in entry:
            assert components[concept]["type"] == "EntityType", concept
        for node in entry.get("object_mappings", []):
            check_object(node, concept)
        own = [r["name"] for r in components[concept].get("relationships", [])]
        named = []
        for node in entry.get("link_mappings", []):
            before = len(linked)
            check_link(node, concept, 1, [])
            assert len(linked) == before + 1, "one fact type per tree"
            named.append(linked[-1])
        assert named == [name for name in own if name in set(named)], "ontology relationship order"
    return linked


def check(number: str, mapping_schema: Path) -> None:
    from gnd.export.ossie import render_ossie
    from gnd.model import load_model
    from gnd.values import model_identity

    directory = CORPUS / number
    model_path = rmap_case(number)
    semantic_bytes = (directory / "expected.semantic_model.yaml").read_bytes()
    mapping_bytes = (directory / "expected.mapping.yaml").read_bytes()
    semantic = load_yaml(directory / "expected.semantic_model.yaml")
    mapping = load_yaml(directory / "expected.mapping.yaml")
    payload = json.loads((directory / "expected.extension.json").read_text(encoding="utf-8"))
    answer = json.loads((RMAP / "answers" / f"{number}.json").read_text(encoding="utf-8"))
    ontology_bytes = render_ossie(model_path, output_format="yaml", relational=False).document
    ontology = YAML(typ="safe", pure=True).load(ontology_bytes.decode("utf-8"))

    # 1. The files are in the exporter's own YAML form, byte for byte.
    assert dump_yaml(semantic) == semantic_bytes, "semantic model is not in dumper form"
    assert dump_yaml(mapping) == mapping_bytes, "mapping is not in dumper form"

    # 2. The pinned schemas accept them.
    core_validator, mapping_validator = _validators(mapping_schema)
    assert not list(core_validator.iter_errors(semantic))
    assert not list(mapping_validator.iter_errors(mapping))

    # 3. The semantic model is the owner-approved OB2 answer, table for table.
    tables = answer["tables"]
    assert [d["name"] for d in semantic["datasets"]] == [t["name"] for t in tables]
    relationships = []
    for dataset, table in zip(semantic["datasets"], tables):
        assert dataset["source"] == table["name"]
        assert dataset.get("primary_key", []) == table["primary_key"]
        assert dataset.get("unique_keys", []) == table["unique_keys"]
        assert [(f["name"], f.get("datatype")) for f in dataset["fields"]] == [
            (c["name"], c["datatype"]) for c in table["columns"]
        ]
        assert [f["expression"] for f in dataset["fields"]] == [
            {"sql": f'"{c["name"].upper()}"'} for c in table["columns"]
        ]
        assert dataset["custom_extensions"] == [{"vendor_name": "GND", "data": '{"source_kind":"logical"}'}]
        relationships += [
            {"name": k["name"], "from": table["name"], "to": k["target_table"],
             "from_columns": k["columns"], "to_columns": k["target_columns"]}
            for k in table["foreign_keys"]
        ]
    assert semantic.get("relationships", []) == relationships
    assert "relationships" in semantic or not relationships

    # 4. The references name the documents they point at.
    assert mapping["ontology_ref"] == {"name": ontology["name"], "iri": f"./{OUT_NAME}"}
    assert mapping["semantic_model_ref"] == {
        "name": semantic["name"], "iri": f"./{OUT_NAME}.semantic_model.yaml"}
    assert semantic["name"] == ontology["name"] + "_relational"
    assert mapping["name"] == ontology["name"] + "_mapping"

    # 5, 6. Expressions name declared fields; links and referents name the ontology's
    # relationships at the right level.
    linked = cross_check(ontology, semantic, mapping)
    components = {c["concept"]: c for c in ontology["ontology"]}
    order = list(components)
    mapped_concepts = [entry["concept"] for entry in mapping["concept_mappings"]]

    # 7. Totality: the carried fact types are exactly the link-mapped relationships.
    carried = [d["id"] for d in answer["dispositions"] if d["kind"] == "fact_type" and d["reason"] is None]
    assert sorted(linked) == sorted(carried), (linked, carried)

    # 8. The extension is bound to the real ontology, the expected semantic model and the model.
    (extension,) = mapping["custom_extensions"]
    assert extension["vendor_name"] == "GND"
    assert extension["data"] == extension_data(payload)
    assert json.loads(extension["data"]) == payload
    assert payload["schema"] == "gnd-ossie-relational/1"
    assert payload["rmap_variant"] == "halpin"
    assert payload["ontology_sha256"] == hashlib.sha256(ontology_bytes).hexdigest()
    assert payload["semantic_model_sha256"] == hashlib.sha256(semantic_bytes).hexdigest()
    assert payload["model_identity"] == model_identity(load_model(model_path))
    assert payload["dispositions"] == answer["dispositions"]
    absorbed = sorted(c for c in order if components[c]["type"] == "EntityType"
                      and c not in mapped_concepts
                      or c in mapped_concepts and "object_mappings" not in
                      next(e for e in mapping["concept_mappings"] if e["concept"] == c))
    assert sorted(entry["concept"] for entry in payload["concepts"]) == absorbed


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--mapping-schema", type=Path, default=SCHEMAS / "mapping.json")
    parser.add_argument("--assemble", action="store_true")
    arguments = parser.parse_args(argv)
    for number in cases():
        if arguments.assemble:
            assemble(number)
        check(number, arguments.mapping_schema)
        print(f"{number}: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
