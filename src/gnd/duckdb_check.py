"""Read-only constraint checks over explicitly bound, local DuckDB base tables."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from threading import Timer

from gnd import disclosure, input_policy
from gnd.anchors import read_regular_path
from gnd.artifacts import ArtifactError
from gnd.errors import ModelLoadError, ModelValidationError
from gnd.model import load_model_bytes
from gnd.model_index import ModelIndex
from gnd.redaction import RedactionPolicy

_TYPES = {"String": {"VARCHAR"}, "Boolean": {"BOOLEAN"},
          "Integer": {"TINYINT", "SMALLINT", "INTEGER", "BIGINT", "HUGEINT"}}


class BindingError(ValueError):
    """A fixed refusal code suitable for a projected report."""


def _identifier(name):
    if not isinstance(name, str) or not name or "\0" in name:
        raise BindingError("invalid-identifier")
    return '"' + name.replace('"', '""') + '"'


def _open(backend, path):
    return backend.connect(str(path), read_only=True, config={
        "enable_external_access": "false", "autoload_known_extensions": "false",
        "autoinstall_known_extensions": "false", "threads": "1", "memory_limit": "256MB",
        "max_temp_directory_size": "0B",
    })


def _snapshot_digest(path, deadline):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            if time.monotonic() >= deadline:
                raise BindingError("deadline-exceeded")
            digest.update(block)
    return digest.hexdigest()


def _projection(execute, table, columns, primitives):
    """Validate exact catalog identity before quoting each identifier into SQL."""
    _identifier(table)
    metadata = execute(
        "SELECT c.column_name, c.data_type FROM information_schema.columns c "
        "JOIN information_schema.tables t USING (table_catalog, table_schema, table_name) "
        "WHERE c.table_catalog = current_database() AND c.table_schema = 'main' "
        "AND c.table_name = ? AND t.table_type = 'BASE TABLE'", [table]).fetchall()
    schema = dict(metadata)
    if not schema:
        raise BindingError("missing-base-table")
    fields = []
    for position, (column, primitive) in enumerate(zip(columns, primitives, strict=True)):
        quoted = _identifier(column)
        if column not in schema:
            raise BindingError("missing-column")
        if schema[column] not in _TYPES.get(primitive, ()):
            raise BindingError("incompatible-column-type")
        fields.append(f"{quoted} AS c{position}")
    source = f"(SELECT {', '.join(fields)} FROM main.{_identifier(table)})"
    nulls = " OR ".join(f"c{i} IS NULL" for i in range(len(fields)))
    if execute(f"SELECT EXISTS (SELECT 1 FROM {source} WHERE {nulls})").fetchone()[0]:
        raise BindingError("null-in-bound-column")
    return source


def _relations(execute, index, bindings):
    roles = index.role_object_types()
    facts, rosters = {}, {}
    for name, spec in bindings["facts"].items():
        if name not in roles or not isinstance(spec, dict) or set(spec) != {"table", "roles"}:
            raise BindingError("invalid-fact-binding")
        mapping = spec["roles"]
        if not isinstance(mapping, dict) or set(mapping) != set(roles[name]):
            raise BindingError("incomplete-role-projection")
        facts[name] = _projection(execute, spec["table"], [mapping[r] for r in roles[name]],
                                  [index.primitive(t, variant="strict") for t in roles[name].values()])
    for obj, spec in bindings.get("instances", {}).items():
        if index.object_type(obj) is None or not isinstance(spec, dict) or set(spec) != {"table", "column"}:
            raise BindingError("invalid-roster-binding")
        rosters[obj] = _projection(execute, spec["table"], [spec["column"]], [index.primitive(obj, variant="strict")])
    return roles, facts, rosters


def _queries(index, constraint, parent, roles, facts, rosters):
    family = constraint["type"]

    def source(fact):
        if fact not in facts:
            raise BindingError("uncovered-fact")
        return facts[fact]

    def column(fact, role):
        return f"c{list(roles[fact]).index(role)}"

    if family == "subset" and parent is None:
        parts, sources = [], []
        for seq in (constraint["subset_role_seq"], constraint["superset_role_seq"]):
            names = {item["fact_type"] for item in seq}
            if len(names) != 1:
                raise BindingError("unsupported-role-sequence")
            name = names.pop()
            projected = ", ".join(column(name, item["role"]) for item in seq)
            sources.append(source(name))
            parts.append(f"SELECT {projected} FROM {source(name)}")
        return " EXCEPT ".join(parts), sources

    if parent is None or family not in {"mandatory", "uniqueness"}:
        raise BindingError("unsupported-constraint")
    fact = parent["id"]
    bound = source(fact)
    if family == "uniqueness":
        roles_of_key = index.constraint_roles(constraint)
        if constraint.get("scope") == "external" or not roles_of_key:
            raise BindingError("unsupported-uniqueness-scope")
        keys = ", ".join(column(fact, r) for r in roles_of_key)
        return f"SELECT * FROM {bound} QUALIFY count(*) OVER (PARTITION BY {keys}) > 1", [bound]

    role = constraint["role"]
    obj = roles[fact][role]
    if obj not in rosters:
        raise BindingError("uncovered-instance-roster")
    universe = [f"SELECT c0 FROM {rosters[obj]}"]
    for name, types in roles.items():
        for referenced, owner in types.items():
            if owner == obj:
                universe.append(f"SELECT {column(name, referenced)} FROM {source(name)}")
    return " UNION ".join(universe) + f" EXCEPT SELECT {column(fact, role)} FROM {bound}", [bound]


def _evaluate(execute, index, bindings, limit, hide):
    roles, facts, rosters = _relations(execute, index, bindings)
    rows = []
    for ref, constraint, parent in index.iter_constraints_shared():
        modality = constraint["modality"]
        row = {"constraint_ref": ref, "constraint_type": constraint["type"], "modality": modality}
        rows.append(row)
        try:
            query, sources = _queries(index, constraint, parent, roles, facts, rosters)
        except BindingError as exc:
            row.update(verdict="unchecked", reason_code=str(exc))
            continue
        if not any(execute(f"SELECT EXISTS (SELECT 1 FROM {table})").fetchone()[0] for table in sources):
            row.update(verdict="vacuous", reason_code="empty-scope")
            continue
        count = execute(f"SELECT count(*) FROM ({query})").fetchone()[0]
        row["verdict"] = ("fail" if modality == "alethic" else "warning") if count else "pass"
        if not hide:
            examples = execute(f"SELECT * FROM ({query}) ORDER BY ALL LIMIT ?", [limit]).fetchall() if count and limit else []
            row.update(violation_count=count, examples=[list(item) for item in examples], truncated=count > limit)
    return rows


def run(model, database, bindings, max_examples, timeout_seconds):
    report = {"schema_version": "gnd-duckdb-check/1", "exit_code": 3, "verdicts": []}
    try:
        import duckdb
    except ImportError:
        return {**report, "error": "duckdb-unavailable"}
    try:
        if not isinstance(bindings, dict) or set(bindings) - {"version", "facts", "instances"} or (
            type(bindings.get("version")) is not int or bindings["version"] != 1
            or not isinstance(bindings.get("facts"), dict) or not isinstance(bindings.get("instances", {}), dict)
        ):
            raise BindingError("invalid-bindings")
        if type(max_examples) is not int or not 0 <= max_examples <= 100:
            raise BindingError("invalid-example-limit")
        if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 120:
            raise BindingError("invalid-deadline")
        deadline = time.monotonic() + timeout_seconds
        model_path = Path(model).resolve(strict=True)
        raw = read_regular_path(model_path, label="database check model", max_bytes=input_policy.MAX_BYTES)
        loaded = load_model_bytes(raw, source=model_path)
        index = ModelIndex.for_model(loaded)
        if loaded.reference_populations or any(
            row.get("derivation") in {"derived", "semiderived"} for row in index.iter_fact_types_shared()
        ) or any(o.get("kind") != "value" or o.get("subtype_of") for o in index.object_types_by_id().values()):
            raise BindingError("unsupported-model")
        db_path = Path(database).resolve(strict=True)
        if not db_path.is_file():
            raise BindingError("invalid-database")
        before = db_path.stat()
        normalized = json.dumps(bindings, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        with _open(duckdb, db_path) as db:
            timer = Timer(max(0, deadline - time.monotonic()), db.interrupt)
            timer.start()
            try:
                def execute(sql, params=()):
                    if time.monotonic() >= deadline:
                        raise BindingError("deadline-exceeded")
                    return db.execute(sql, params)

                execute("BEGIN TRANSACTION")
                digest = _snapshot_digest(db_path, deadline)
                if db_path.with_name(db_path.name + ".wal").exists():
                    raise BindingError("uncheckpointed-database")
                hidden = disclosure.resolve() == "customer" or RedactionPolicy.from_model(loaded).active
                rows = _evaluate(execute, index, bindings, max_examples, hidden)
                after = db_path.stat()
                if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
                    after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns
                ):
                    raise BindingError("snapshot-changed")
                execute("COMMIT")
            finally:
                timer.cancel()
                timer.join()
        verdicts = {r["verdict"] for r in rows}
        undecided = any(r["verdict"] == "unchecked" and r["modality"] == "alethic" for r in rows)
        code = 1 if "fail" in verdicts else 4 if undecided or not rows else 2 if "vacuous" in verdicts else 0
        return {**report, "exit_code": code, "verdicts": rows, "model_sha256": hashlib.sha256(raw).hexdigest(),
                "snapshot_sha256": digest, "projection_sha256": hashlib.sha256(normalized).hexdigest(),
                "duckdb_version": duckdb.__version__}
    except BindingError as exc:
        return {**report, "error": str(exc)}
    except duckdb.InterruptException:
        return {**report, "error": "deadline-exceeded"}
    except duckdb.OutOfMemoryException:
        return {**report, "error": "memory-limit"}
    except (ArtifactError, OSError, ValueError, TypeError, ModelLoadError, ModelValidationError, duckdb.Error):
        return {**report, "error": "invalid-input"}
