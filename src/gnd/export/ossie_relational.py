"""Build the Ossie semantic model and mapping that accompany an exported ontology.

The normative rules have one home: "Semantic model and mapping" under "Ossie
interchange" in ``gnd-orm-core/references/representation-format.md``. This module
turns a :class:`gnd.rmap.RelationalSchema` into an Ossie core-spec semantic model,
and maps the ontology's concepts and relationships onto it. It builds documents
only; :func:`gnd.export.ossie.render_ossie` encodes and binds them.

Nothing here refuses a model. A fact type the relational layer cannot express is
listed in the mapping's ``GND`` extension with a closed reason.
"""

from __future__ import annotations

import itertools
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import files
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from gnd.artifacts import canonical_json_bytes
from gnd.input_policy import loads
from gnd.rmap import Disposition, Identification, RelationalSchema, RolePlacement

__all__ = [
    "DATATYPES",
    "EXTENSION_SCHEMA",
    "MAX_LINK_ARITY",
    "OntologyView",
    "build_mapping",
    "build_semantic_model",
    "extension_data",
    "validate_relational",
]

VERSION = "0.3.0.dev0"
VENDOR = "GND"
EXTENSION_SCHEMA = "gnd-ossie-relational/1"
_UPSTREAM = "https://raw.githubusercontent.com/apache/ossie/main/"

#: A link mapping nests one level per role. A fact type with more roles than this is
#: listed, not nested: the bound keeps every mapping document shallow enough for a
#: recursive reader, whatever arity the model admits.
MAX_LINK_ARITY = 32

#: GND value primitive -> Ossie core-spec data type (OB3 E6). ``Opaque`` keeps the
#: primitive in the field's ``GND`` extension.
DATATYPES: dict[str, str] = {
    "String": "String",
    "Integer": "Integer",
    "Float": "Float",
    "Boolean": "Boolean",
    "Date": "Date",
    "DateTime": "DateTime",
    "Number": "Decimal",
    "Binary": "Opaque",
    "Duration": "Opaque",
}


@dataclass(frozen=True)
class OntologyView:
    """What the mapping reads from the ontology the same export run built.

    ``identification`` gives, per object type id, how the ontology identifies it:
    ``("simple", relationship)`` or ``("composite", (relationship, ...))`` in
    ``identify_by`` order. ``relations`` gives, per fact type id, the concept that
    owns its relationship and its roles in the relationship's order.
    """

    name: str
    concepts: Mapping[str, str]  # object type id -> concept, in component order
    kinds: Mapping[str, str]  # object type id -> "entity" | "value"
    identification: Mapping[str, tuple[str, Any]]
    relations: Mapping[str, tuple[str, tuple[str, ...], Mapping[str, str]]]


def extension_data(payload: Any) -> str:
    """An extension's ``data``: canonical JSON without its trailing newline."""
    return canonical_json_bytes(payload).decode("utf-8").removesuffix("\n")


#: ASCII punctuation that cannot stand in an unquoted identifier: all of it but ``$`` and ``_``.
_NOT_IN_REGULAR = frozenset("!\"#%&'()*+,-./:;<=>?@[\\]^`{|}~")
#: The two words Ossie's reader never takes as an unquoted name, in any case.
_NEVER_REGULAR = frozenset({"NOT", "SELECT"})


def is_regular_identifier(name: str) -> bool:
    """Whether Ossie reads NAME as a regular identifier, one that can be written unquoted.

    Ossie compares a regular identifier by its uppercased form and keeps any other
    name exactly as written (core-spec expression_language.md, "normalized
    identifier"). The class is the pinned validator's, measured over every character
    (OB5): no white space, no ASCII punctuation but ``$`` and ``_``, no leading ASCII
    digit, and not the word NOT or SELECT.
    """
    return (
        bool(name)
        and name[0] not in "0123456789"
        and not any(character.isspace() or character in _NOT_IN_REGULAR for character in name)
        and name.upper() not in _NEVER_REGULAR
    )


def _quoted(identifier: str) -> str:
    """One SQL identifier, quoted, in Ossie's normalized form: a regular identifier
    uppercased, so that it never reads as a keyword (OB3 E5), and any other name as
    written, which is the only form that names it (OB5)."""
    name = identifier.upper() if is_regular_identifier(identifier) else identifier
    return '"' + name.replace('"', '""') + '"'


def _extension(payload: Any) -> list[dict[str, str]]:
    return [{"vendor_name": VENDOR, "data": extension_data(payload)}]


def build_semantic_model(
    schema: RelationalSchema, name: str,
    *, physical: Mapping[tuple[str, str], tuple[str | None, str | None]] | None = None,
) -> dict[str, Any]:
    """One dataset per table, one field per column, one relationship per foreign key.

    ``physical`` is given for a delivered schema (a physical binding): per
    (table, column), the Ossie data type or None, and the raw SQL type or None.
    """
    datasets = []
    relationships = []
    for table in schema.tables:
        dataset: dict[str, Any] = {"name": table.name, "source": table.name}
        if table.primary_key:
            dataset["primary_key"] = list(table.primary_key)
        if table.unique_keys:
            dataset["unique_keys"] = [list(key) for key in table.unique_keys]
        fields = []
        for column in table.columns:
            field: dict[str, Any] = {"name": column.name, "expression": {"sql": _quoted(column.name)}}
            if physical is not None:
                datatype, sql_type = physical[(table.name, column.name)]
                if datatype is not None:
                    field["datatype"] = datatype
                if sql_type is not None:
                    field["custom_extensions"] = _extension({"sql_type": sql_type})
            elif column.datatype is not None:
                field["datatype"] = DATATYPES[column.datatype]
                if field["datatype"] == "Opaque":
                    field["custom_extensions"] = _extension({"gnd_primitive": column.datatype})
            fields.append(field)
        dataset["fields"] = fields
        dataset["custom_extensions"] = _extension({"source_kind": "logical" if physical is None else "physical"})
        datasets.append(dataset)
        relationships += [
            {
                "name": key.name,
                "from": table.name,
                "to": key.target_table,
                "from_columns": list(key.columns),
                "to_columns": list(key.target_columns),
            }
            for key in table.foreign_keys
        ]
    document: dict[str, Any] = {"version": VERSION, "name": name, "datasets": datasets}
    if relationships:
        document["relationships"] = relationships
    return document


class _Mapping:
    def __init__(self, schema: RelationalSchema, view: OntologyView) -> None:
        self.view = view
        self.tables = {table.name for table in schema.tables}
        self.identifications: dict[str, Identification] = {i.object_type: i for i in schema.identifications}
        self.placements: dict[tuple[str, str], RolePlacement] = {(p.fact_type, p.role): p for p in schema.roles}

    def referents(
        self, object_type: str, table: str, columns: Sequence[str], wrap: Callable[[str], str]
    ) -> list[dict[str, Any]] | None:
        """Referent mappings that find one object of an entity type from ``columns`` of
        ``table``, or None when the ontology does not identify it as the Rmap does."""
        rmap = self.identifications.get(object_type)
        ontology = self.view.identification.get(object_type)
        if rmap is None or ontology is None or len(columns) != len(rmap.columns):
            return None
        form, payload = ontology
        if rmap.kind == "direct" and form == "simple":
            return [{"relationship": payload, "expression": wrap(self.reference(table, columns[0]))}]
        if rmap.kind != "composite" or form != "composite":
            return None
        by_fact: dict[str, tuple[str, list[str]]] = {}
        for column, component in zip(columns, rmap.components):
            assert component is not None
            by_fact.setdefault(component[0], (component[1], []))[1].append(column)
        if set(by_fact) != set(payload):
            return None
        result = []
        for relationship in payload:  # the ontology's identify_by order
            role, held = by_fact[relationship]
            player = self.view.relations[relationship][2][role]
            if self.view.kinds[player] == "value":
                result.append({"relationship": relationship, "expression": wrap(self.reference(table, held[0]))})
                continue
            nested = self.referents(player, table, held, wrap)
            if nested is None:
                return None
            result.append({"relationship": relationship, "referent_mappings": nested})
        return result

    @staticmethod
    def reference(table: str, column: str) -> str:
        return f"{_quoted(table)}.{_quoted(column)}"

    def object_mapping(
        self, object_type: str, table: str, columns: Sequence[str], *,
        named: bool, wrap: Callable[[str], str] = str,
    ) -> dict[str, Any] | None:
        """How ``columns`` of ``table`` give one object of ``object_type``."""
        node: dict[str, Any] = {"concept": self.view.concepts[object_type]} if named else {}
        if self.view.kinds[object_type] == "value":
            if len(columns) != 1:
                return None
            node["expression"] = wrap(self.reference(table, columns[0]))
            return node
        referents = self.referents(object_type, table, columns, wrap)
        if referents is None:
            return None
        if self.identifications[object_type].kind == "direct":
            node["expression"] = referents[0]["expression"]
        else:
            node["referent_mappings"] = referents
        return node

    def link_tree(self, fact_type: str) -> dict[str, Any] | str:
        """One tree per fact type: a node per role in the relationship's order, the
        last one naming the relationship. Otherwise the reason there is no tree."""
        _, order, players = self.view.relations[fact_type]
        if len(order) > MAX_LINK_ARITY:
            return "arity-over-limit"
        # A unary stored as a Boolean flag: a row is a link only where the flag is true.
        first = self.placements[(fact_type, order[0])]
        flag = self.reference(first.table, first.flag) if first.flag is not None else None

        def wrap(expression: str) -> str:
            return expression if flag is None else f"CASE WHEN {flag} THEN {expression} END"

        nodes = []
        for level, role in enumerate(order):
            placement = self.placements[(fact_type, role)]
            node = self.object_mapping(
                players[role], placement.table, placement.columns, named=level > 0, wrap=wrap)
            if node is None:
                return "identification-differs"
            nodes.append({"object_mapping": node})
        nodes[-1]["relationship"] = fact_type
        for parent, child in itertools.pairwise(nodes):
            parent["children"] = [child]
        return nodes[0]


def build_mapping(
    schema: RelationalSchema,
    dispositions: Sequence[Disposition],
    view: OntologyView,
    *,
    name: str,
    ontology_iri: str,
    semantic_model_name: str,
    semantic_model_iri: str,
    bindings: Mapping[str, str],
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Map the ontology's concepts and relationships onto the semantic model.

    ``bindings`` are the digests and identity the ``GND`` extension carries. Every
    disposition is listed there, so a reader can check from the file alone that each
    fact type and constraint is carried or has a reason.
    """
    mapper = _Mapping(schema, view)
    trees: dict[str, list[dict[str, Any]]] = {}
    unmapped_links = []
    carried = {d.id for d in dispositions if d.kind == "fact_type" and d.reason is None}
    for fact_type, (owner, _order, _players) in view.relations.items():  # the ontology's relationship order
        if fact_type not in carried:
            continue
        tree = mapper.link_tree(fact_type)
        if isinstance(tree, str):
            unmapped_links.append({"fact_type": fact_type, "reason": tree})
        else:
            trees.setdefault(owner, []).append(tree)

    concept_mappings = []
    concepts = []
    for object_type, concept in view.concepts.items():
        entry: dict[str, Any] = {"concept": concept}
        identification = mapper.identifications.get(object_type)
        table = identification.table if identification is not None else None
        if view.kinds[object_type] == "entity" and table is not None:
            if identification.absorbed:
                concepts.append({"concept": concept, "reason": "subtype-absorbed"})
            else:
                node = mapper.object_mapping(object_type, table, identification.columns, named=False)
                if node is None:
                    concepts.append({"concept": concept, "reason": "identification-differs"})
                else:
                    entry["object_mappings"] = [node]
        if object_type in trees:
            entry["link_mappings"] = trees[object_type]
        if len(entry) > 1:
            concept_mappings.append(entry)

    payload: dict[str, Any] = {
        "schema": EXTENSION_SCHEMA,
        **bindings,
        **({"rmap_variant": schema.variant.value} if schema.variant is not None else {}),
        "dispositions": [
            {"kind": d.kind, "id": d.id, "carried_as": list(d.carried_as), "reason": d.reason}
            for d in dispositions
        ],
        "concepts": concepts,
        **(extra or {}),
    }
    if unmapped_links:
        payload["unmapped_links"] = sorted(unmapped_links, key=lambda row: row["fact_type"])
    return {
        "version": VERSION,
        "name": name,
        "ontology_ref": {"name": view.name, "iri": ontology_iri},
        "semantic_model_ref": {"name": semantic_model_name, "iri": semantic_model_iri},
        "concept_mappings": concept_mappings,
        "custom_extensions": _extension(payload),
    }


@lru_cache(maxsize=1)
def _validators() -> tuple[Draft202012Validator, Draft202012Validator]:
    root = files("gnd").joinpath("schema", "ossie")
    core = loads(root.joinpath("core-spec.json").read_bytes())
    ontology = loads(root.joinpath("ontology.json").read_bytes())
    mapping = loads(root.joinpath("mapping.json").read_bytes())
    # The pinned schemas reference each other through upstream URLs. Registry() refuses
    # any retrieval that is not registered here, so validation never opens a connection.
    registry = Registry().with_resources([
        (_UPSTREAM + "core-spec/ossie-schema.json", Resource.from_contents(core, default_specification=DRAFT202012)),
        (_UPSTREAM + "ontology/ontology.json", Resource.from_contents(ontology, default_specification=DRAFT202012)),
    ])
    return Draft202012Validator(core, registry=registry), Draft202012Validator(mapping, registry=registry)


def validate_relational(semantic_model: Mapping[str, Any], mapping: Mapping[str, Any]) -> None:
    """Check both documents against the pinned schemas; a failure is a renderer defect."""
    semantic_validator, mapping_validator = _validators()
    semantic_validator.validate(semantic_model)
    mapping_validator.validate(mapping)
