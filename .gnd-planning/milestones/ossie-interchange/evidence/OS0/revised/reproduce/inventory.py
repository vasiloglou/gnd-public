import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

repo, out = map(Path, sys.argv[1:])
schema_path = repo / "src/gnd/schema/orm-meta.schema.json"
schema = json.loads(schema_path.read_bytes())
validator = Draft202012Validator(schema)
paths = (
    subprocess.check_output(
        [
            "git",
            "-C",
            str(repo),
            "ls-files",
            "-z",
            "--",
            *(
                f":(glob){root}/**/*.orm.{suffix}"
                for root in ("src/gnd/examples", "src/gnd/skills/gnd-model-from-text/examples")
                for suffix in ("yaml", "yml", "json")
            ),
        ],
        text=True,
    )
    .strip("\0")
    .split("\0")
)


def write(name, value):
    (out / name).write_text(json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n")


def pointer(parts):
    return "".join("/" + str(part).replace("~", "~0").replace("/", "~1") for part in parts)


def children(value):
    if isinstance(value, dict):
        return value.items()
    if isinstance(value, list):
        return enumerate(value)
    return ()


class UniqueKeysLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                raise ValueError(f"duplicate key {key!r}")
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping


def load(raw):
    return yaml.load(raw, Loader=UniqueKeysLoader)


def schemas_by_path(value, shape, path=()):
    ref = shape.get("$ref")
    if ref and ref.startswith("#/$defs/"):
        name = ref.rsplit("/", 1)[-1]
        yield path, name
        yield from schemas_by_path(value, schema["$defs"][name], path)
    for keyword in ("allOf", "oneOf", "anyOf"):
        for branch in shape.get(keyword, []):
            if keyword == "allOf" or validator.evolve(schema=branch).is_valid(value):
                yield from schemas_by_path(value, branch, path)
    if "if" in shape:
        branch = "then" if validator.evolve(schema=shape["if"]).is_valid(value) else "else"
        yield from schemas_by_path(value, shape.get(branch, {}), path)
    for key, item in children(value):
        if isinstance(key, int):
            child_shape = shape.get("items")
        else:
            child_shape = shape.get("properties", {}).get(key, shape.get("additionalProperties"))
        if isinstance(child_shape, dict):
            yield from schemas_by_path(item, child_shape, path + (key,))


def bound_reading(reading, names, labels, order, *, inverse=False):
    tokens = re.compile(r"\{([^{}]+)\}")
    matches = list(tokens.finditer(reading))
    qualified = {label: i for i, label in enumerate(labels)}
    if inverse and not matches and len(names) == 2:
        reading = f"{{{names[1]}:{labels[1]}}} {reading} {{{names[0]}:{labels[0]}}}"
        matches = list(tokens.finditer(reading))
    if len(matches) != len(names):
        raise ValueError("reading omits a role")
    indices = (
        [qualified.get(match[1].partition(":")[2].strip()) for match in matches]
        if inverse
        else list(range(len(names)))
    )
    if set(indices) != set(range(len(names))):
        raise ValueError("reading role binding is ambiguous")
    parts = []
    offset = 0
    for match, index in zip(matches, indices, strict=True):
        token = names[index]
        if index != order[0]:
            token += ":" + labels[index]
        parts.extend((reading[offset : match.start()], "{" + token + "}"))
        offset = match.end()
    parts.append(reading[offset:])
    return "".join(parts), [labels[i] for i in indices]


def check_readings(fact, names, labels, order, new_order):
    keys = [key for key in ("reading", "inverse_reading") if fact.get(key)]
    observations = {}
    for key in keys:
        old_pattern, old_roles = bound_reading(
            fact[key], names, labels, order, inverse=key == "inverse_reading"
        )
        new_pattern, new_roles = bound_reading(
            fact[key], names, labels, new_order, inverse=key == "inverse_reading"
        )
        assert old_roles == new_roles
        observations[key] = {
            "original_order_pattern": old_pattern,
            "projected_order_pattern": new_pattern,
            "roles": old_roles,
        }
    return observations


def uniqueness(fact, objects):
    roles = fact["roles"]
    names = [objects[r["object_type"]]["name"] for r in roles]
    labels = [r.get("role_name", name) for r, name in zip(roles, names)]
    order = list(range(len(roles)))
    prefix = frozenset(labels[:-1])
    unique = [
        (("constraints", i), frozenset(c.get("roles", [])))
        for i, c in enumerate(fact.get("constraints", []))
        if c["type"] == "uniqueness" and c.get("scope", "internal") == "internal"
    ]
    candidates = {
        roles
        for _, roles in unique
        if len(labels) > 1 and len(roles) == len(labels) - 1 and roles <= set(labels)
    }
    result = {
        "role_order": labels,
        "determinants": [sorted(roles) for _, roles in unique],
        "non_prefix_determinants": [sorted(roles) for _, roles in unique if roles != prefix],
        "not_expressible_as_n_minus_one": [
            sorted(roles) for _, roles in unique if roles not in candidates
        ],
    }
    multiplicity = None
    new_order = order
    selected = set()
    if len(labels) == 2 and len(candidates) == 2:
        multiplicity = "OneToOne"
        selected = {path for path, roles in unique if roles in candidates}
    elif candidates:
        target = (
            prefix
            if prefix in candidates
            else min(
                candidates,
                key=lambda group: [i for i, label in enumerate(labels) if label in group],
            )
        )
        new_order = [i for i in order if labels[i] in target] + [
            i for i in order if labels[i] not in target
        ]
        multiplicity = "ManyToOne"
        selected = {path for path, roles in unique if roles == target}
    if multiplicity:
        result["multiplicity"] = multiplicity
    if new_order != order:
        result["reordered_roles"] = [labels[i] for i in new_order]
    if result["not_expressible_as_n_minus_one"]:
        result["non_native_determinants"] = [
            {
                "roles": roles,
                "reason": "full-tuple-set-semantics"
                if len(roles) == len(labels)
                else "determinant-size",
            }
            for roles in result["not_expressible_as_n_minus_one"]
        ]
    try:
        result["readings"] = check_readings(fact, names, labels, order, new_order)
    except ValueError as error:
        result["exception"] = str(error)
        return result, set()
    return result, selected


def classify(path, value, native_constraints, model):
    if (path[:1] == ("fact_types",) and path[2:3] == ("sample_population",)) or path[:1] == (
        "reference_populations",
    ):
        return "refused", "population:out-of-scope"
    if path[:1] == ("includes",):
        return "refused", "include:unsupported-route"
    for prefix in native_constraints:
        if path[: len(prefix)] == prefix and path[len(prefix) : len(prefix) + 1] in (
            (),
            ("type",),
            ("scope",),
            ("roles",),
        ):
            return "native", "multiplicity"
    if path[:1] == ("object_types",):
        native_fields = {("name",), ("kind",), ("primitive",), ("subtype_of",)}
        if (len(path) <= 2 or path[2:3] in native_fields) and (
            path[2:] != ("primitive",) or value != "Duration"
        ):
            return "native", "concept"
        if len(path) >= 3 and path[2] == "reference":
            reference = model["object_types"][path[1]]["reference"]
            if reference.get("mode") in {"popular", "general"} and path[3:] in (
                (),
                ("value_type",),
            ):
                return "native", "identify-by"
        if path[2:] == ("description", "summary"):
            return "native", "concept-description"
    if path[:1] == ("fact_types",):
        if path[2:3] == ("roles",) and len(path) > 4:
            if path[4] == "object_type" or (path[4] == "role_name" and path[3] > 0):
                return "native", "relationship-role"
        elif len(path) <= 2 or path[2:3] in {
            ("id",),
            ("roles",),
            ("reading",),
            ("inverse_reading",),
        }:
            return "native", "relationship"
    return "extension", "source-shape-or-unproved-native-mapping"


def walk(model, native, definitions, refusal):
    def visit(value, path=(), owner=None):
        if isinstance(value, dict) and "id" in value:
            owner = value["id"]
        disposition, reason = (
            ("refused", refusal) if refusal else classify(path, value, native, model)
        )
        kinds = sorted(definitions.get(path, ()))
        yield [pointer(path), owner, kinds, disposition, reason]
        for key, item in children(value):
            yield from visit(item, path + (key,), owner)

    yield from visit(model)


def check_mode_coverage(expected, rows, *, disposition):
    actual = {row[0]: row[3] for row in rows}
    wrong = [location for location in expected if actual.get(location) != disposition]
    if wrong:
        raise ValueError("missing or incorrectly classified modality: " + ", ".join(wrong))


def check_pointers(document, rows):
    # Count nodes independently of address construction, then resolve every
    # emitted pointer against the document using RFC 6901 decoding.
    def node_count(value):
        if isinstance(value, dict):
            return 1 + sum(map(node_count, value.values()))
        if isinstance(value, list):
            return 1 + sum(map(node_count, value))
        return 1

    assert node_count(document) == len({row[0] for row in rows}) == len(rows)
    for location, *_ in rows:
        value = document
        if not location:
            continue
        assert location[0] == "/"
        for part in location[1:].split("/"):
            decoded = part.replace("~1", "/").replace("~0", "~")
            value = value[int(decoded) if isinstance(value, list) else decoded]


inventory = []
def_counts = Counter()
modality = Counter()
refused_modality = Counter()
references = []
admissions = {
    row["command"][-1]: row["exit"]
    for row in json.loads((out / "gnd-validation.json").read_bytes())
}
assert list(admissions) == paths
constraints = defaultdict(list)
facts = []
for filename in paths:
    data = (repo / filename).read_bytes()
    doc = load(data)
    refusal = (
        "include:unsupported-route"
        if "includes" in doc
        else "model:invalid"
        if admissions[filename] != 0
        else None
    )
    objects = {ob["id"]: ob for ob in doc.get("object_types", [])}
    # Validate the parsed source shape and retain any schema errors without
    # suppressing their pointers or counting them as matched branches.
    errors = [
        {"pointer": pointer(error.path), "message": error.message}
        for error in validator.iter_errors(doc)
    ]
    definitions = defaultdict(set)
    for path, definition in schemas_by_path(doc, schema):
        definitions[path].add(definition)
    def_counts.update(definition for names in definitions.values() for definition in names)
    native = set()
    if not refusal:
        for i, fact in enumerate(doc.get("fact_types", [])):
            prefix = ("fact_types", i)
            result, selected = uniqueness(fact, objects)
            facts.append({"model": filename, "fact": fact["id"], **result})
            native.update(prefix + path for path in selected)
        for entry in objects.values():
            if (entry.get("reference") or {}).get("mode") in {"popular", "general"}:
                references.append(
                    {"model": filename, "object_type": entry["id"], "multiplicity": "OneToOne"}
                )
    mode_locations = []
    constraint_rows = [(("constraints", i), c) for i, c in enumerate(doc.get("constraints", []))]
    for i, fact in enumerate(doc.get("fact_types", [])):
        constraint_rows.extend(
            (("fact_types", i, "constraints", j), c)
            for j, c in enumerate(fact.get("constraints", []))
        )
    for path, constraint in constraint_rows:
        constraints[constraint["type"]].append((filename, pointer(path)))
        if "modality" in constraint:
            mode_locations.append(pointer(path + ("modality",)))
            counts = refused_modality if refusal else modality
            counts[constraint["modality"]] += 1
    rows = list(walk(doc, native, definitions, refusal))
    check_pointers(doc, rows)
    check_mode_coverage(mode_locations, rows, disposition="refused" if refusal else "extension")
    inventory.append(
        {
            "model": filename,
            "sha256": sha256(data).hexdigest(),
            "gnd_validation_exit": admissions[filename],
            "export_route_refusal": refusal,
            "schema_errors": errors,
            "rows": rows,
        }
    )

assert paths and set(def_counts) <= set(schema["$defs"])
assert classify(("reference_populations", 0, "path"), "example", set(), {})[:2] == (
    "refused",
    "population:out-of-scope",
)
assert classify(("fact_types", 1, "sample_population", 0), {}, set(), {})[0] == "refused"
assert (
    classify(
        ("fact_types", 1, "constraints", 0, "modality"),
        "deontic",
        {("fact_types", 1, "constraints", 0)},
        {},
    )[0]
    == "extension"
)
assert pointer(("a/b", "~c")) == "/a~1b/~0c"
positive = {
    "id": "related",
    "roles": [{"object_type": "a", "role_name": "a"}, {"object_type": "b", "role_name": "b"}],
    "reading": "{A} relates to {B}",
    "constraints": [{"type": "uniqueness", "roles": ["a"]}, {"type": "uniqueness", "roles": ["b"]}],
}
players = {"a": {"name": "A"}, "b": {"name": "B"}}
assert uniqueness(positive, players)[0]["multiplicity"] == "OneToOne"
positive["constraints"].pop(0)
assert uniqueness(positive, players)[0]["multiplicity"] == "ManyToOne"
assert uniqueness(positive, players)[0]["reordered_roles"] == ["b", "a"]
assert uniqueness(positive, players)[0]["readings"]["reading"]["roles"] == ["a", "b"]
positive["reading"] = "{A} relates to an unknown party"
assert "exception" in uniqueness(positive, players)[0]

mode = "/constraints/0/modality"
check_mode_coverage([mode], [[mode, None, [], "extension", "control"]], disposition="extension")
for broken in ([], [[mode, None, [], "native", "control"]]):
    try:
        check_mode_coverage([mode], broken, disposition="extension")
    except ValueError:
        pass
    else:
        raise AssertionError("missing or native modality passed the control")
try:
    load(b"version: 1\nversion: 2\n")
except ValueError:
    pass
else:
    raise AssertionError("duplicate YAML key passed the control")

(out / "census.txt").write_text("\n".join(paths) + "\n")
# Keep one row per line while retaining a standard JSON container.
with (out / "inventory.json").open("w") as stream:
    header = {
        "row_fields": ["pointer", "nearest_id", "schema_definitions", "disposition", "reason"],
        "schema_sha256": sha256(schema_path.read_bytes()).hexdigest(),
        "schema_definition_census_counts": {name: def_counts[name] for name in schema["$defs"]},
    }
    stream.write(json.dumps(header, indent=2)[:-2] + ',\n  "models": [\n')
    for index, model in enumerate(inventory):
        rows = model.pop("rows")
        stream.write("    " + json.dumps(model)[:-1] + ', "rows": [\n')
        stream.write(",\n".join("      " + json.dumps(row, ensure_ascii=False) for row in rows))
        stream.write("    ]}" + ("," if index < len(inventory) - 1 else "") + "\n")
    stream.write("  ]\n}\n")
write(
    "E4.json",
    {
        "limits": "Source reading bindings and n-1 determinants; OSSIE consumer interpretation is separate.",
        "fact_types": len(facts),
        "non_prefix": [f for f in facts if f["non_prefix_determinants"]],
        "reorders": [f for f in facts if "reordered_roles" in f],
        "exceptions": [f for f in facts if "exception" in f],
        "reading_checks": [
            {"model": f["model"], "fact": f["fact"], "readings": f["readings"]}
            for f in facts
            if "readings" in f
        ],
        "controls": {
            "reordered_roles": ["b", "a"],
            "preserved_reading_roles": ["a", "b"],
            "incomplete_reading": "refused",
        },
    },
)
write(
    "E6.json",
    {
        "limits": "Inventory and ontology.md Multiplicities semantics; no exported document or population run.",
        "one_to_one": [f for f in facts if f.get("multiplicity") == "OneToOne"],
        "projected_direct_identifiers": references,
        "constraint_modality_extensions": modality,
        "constraint_modality_unprojected": refused_modality,
        "controls": {
            "two_uniqueness_directions": "OneToOne",
            "one_uniqueness_direction": "ManyToOne",
            "omitted_modality": "refused",
            "native_modality": "refused",
        },
    },
)
write(
    "constraint-census.json",
    {kind: {"count": len(rows), "first": rows[0]} for kind, rows in sorted(constraints.items())},
)
parsed = json.loads((out / "inventory.json").read_bytes())
print(
    f"{len(parsed['models'])} models, {sum(len(m['rows']) for m in parsed['models'])} unique pointers, {sum(bool(n) for n in def_counts.values())}/{len(schema['$defs'])} observed schema definitions"
)
