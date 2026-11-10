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
            ":(glob)src/gnd/examples/*/*.orm.yaml",
            ":(glob)src/gnd/skills/gnd-model-from-text/examples/*.orm.yaml",
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


def bound_reading(reading, names, labels, order):
    available = list(range(len(names)))
    bindings = []

    def bind(match):
        token = match.group(1)
        choices = [
            i for i in available if token in (names[i], labels[i], f"{names[i]}:{labels[i]}")
        ]
        if not choices:
            raise ValueError(f"unmatched placeholder {token}")
        index = choices[0]
        available.remove(index)
        bindings.append(index)
        new_token = names[index]
        if names.count(new_token) > 1 and index != order[0]:
            new_token += ":" + labels[index]
        return "{" + new_token + "}"

    verbalizes = re.sub(r"\{([^{}]+)\}", bind, reading)
    if available:
        raise ValueError("reading omits a role")
    return verbalizes, bindings


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
    if len(labels) == 2 and len(candidates) == 2:
        return dict(result, multiplicity="OneToOne"), {
            path for path, roles in unique if roles in candidates
        }
    if not candidates:
        return result, set()
    target = (
        prefix
        if prefix in candidates
        else min(
            candidates, key=lambda group: [i for i, label in enumerate(labels) if label in group]
        )
    )
    new_order = [i for i in order if labels[i] in target] + [
        i for i in order if labels[i] not in target
    ]
    if target != prefix:
        result["reordered_roles"] = [labels[i] for i in new_order]
        try:
            readings = [
                bound_reading(fact[k], names, labels, new_order)
                for k in ("reading", "inverse_reading")
                if fact.get(k)
            ]
            result["verbalizes"] = [pattern for pattern, _ in readings]
            result["reading_roles"] = [[labels[i] for i in indices] for _, indices in readings]
        except ValueError as exc:
            return dict(result, exception=str(exc)), set()
    return dict(result, multiplicity="ManyToOne"), {
        path for path, roles in unique if roles == target
    }


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


def walk(model, native, definitions):
    def visit(value, path=(), owner=None):
        if isinstance(value, dict) and "id" in value:
            owner = value["id"]
        disposition, reason = classify(path, value, native, model)
        if path and path[-1] == "modality":
            assert disposition == "extension"
            if "constraints" in path:
                modality[value] += 1
        kinds = sorted(definitions.get(path, ()))
        yield [pointer(path), owner, kinds, disposition, reason]
        for key, item in children(value):
            yield from visit(item, path + (key,), owner)

    yield from visit(model)


inventory = []
def_counts = Counter()
modality = Counter()
constraints = defaultdict(list)
facts = []
for filename in paths:
    data = (repo / filename).read_bytes()
    doc = yaml.safe_load(data)
    objects = {ob["id"]: ob for ob in doc["object_types"]}
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
    for i, fact in enumerate(doc["fact_types"]):
        prefix = ("fact_types", i)
        result, selected = uniqueness(fact, objects)
        facts.append({"model": filename, "fact": fact["id"], **result})
        native.update(prefix + path for path in selected)
    for i, constraint in enumerate(doc.get("constraints", [])):
        constraints[constraint["type"]].append((filename, pointer(("constraints", i))))
    for i, fact in enumerate(doc["fact_types"]):
        for j, constraint in enumerate(fact.get("constraints", [])):
            constraints[constraint["type"]].append(
                (filename, pointer(("fact_types", i, "constraints", j)))
            )

    rows = list(walk(doc, native, definitions))
    # Decode the pointers independently and check that every container child
    # appears, including empty containers and the root.
    by_pointer = {r[0]: r for r in rows}
    assert len(by_pointer) == len(rows)
    checked = set()
    todo = [("", doc)]
    while todo:
        address, value = todo.pop()
        assert address in by_pointer
        checked.add(address)
        for key, item in children(value):
            todo.append((address + pointer((key,)), item))
    assert checked == by_pointer.keys()
    inventory.append(
        {
            "model": filename,
            "sha256": sha256(data).hexdigest(),
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
assert uniqueness(positive, players)[0]["reading_roles"] == [["a", "b"]]
positive["reading"] = "{A} relates to {X}"
assert "exception" in uniqueness(positive, players)[0]

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
        "synthetic_control": "B determines A; preserved reading order A, B. Unknown role refuses.",
    },
)
write(
    "E6.json",
    {
        "limits": "Inventory and ontology.md Multiplicities semantics; no exported document or population run.",
        "one_to_one": [f for f in facts if f.get("multiplicity") == "OneToOne"],
        "constraint_modality_extensions": modality,
        "controls": "Both uniqueness directions produce OneToOne. Dropping one produces ManyToOne.",
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
