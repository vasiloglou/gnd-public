import hashlib
import json
from copy import deepcopy

import duckdb
import pytest

from gnd import api
from gnd.duckdb_check import _open


def rule(family, **fields):
    return {"type": family, "source": "explicit", "status": "confirmed", "modality": "alethic",
            "provenance": {"user_quote": "Validate checked rows."}, **fields}


def fixture(root):
    keys = {"object_type": "key", "role_name": "key"}
    listed = {"id": "listed", "reading": "{Key} is listed", "roles": [keys]}
    pair = {"id": "pair", "reading": "{Key} carries {Label}", "roles": [keys, {"object_type": "label", "role_name": "label"}],
            "constraints": [rule("uniqueness", roles=["key"]), rule("mandatory", role="key")]}
    subset = rule("subset", id="listed_keys", subset_role_seq=[{"fact_type": "pair", "role": "key"}],
                  superset_role_seq=[{"fact_type": "listed", "role": "key"}])
    model = root / "model.orm.json"
    model.write_text(json.dumps({"version": 1, "model_id": "db",
        "object_types": [{"id": name.lower(), "name": name, "kind": "value", "primitive": primitive}
                         for name, primitive in (("Key", "Integer"), ("Label", "String"))],
        "fact_types": [pair, listed], "constraints": [subset]}))
    source = root / "snapshot.duckdb"
    with duckdb.connect(str(source)) as db:
        db.execute('CREATE TABLE "Pair.data" ("Key ID" INTEGER, "a""b" VARCHAR)')
        db.execute('INSERT INTO "Pair.data" VALUES (7, \'b\'), (7, \'a\'), (7, \'a\')')
        db.execute("CREATE TABLE listed (id INTEGER)")
        db.execute("INSERT INTO listed VALUES (11)")
        db.execute("CREATE TABLE roster (id INTEGER)")
        db.execute("INSERT INTO roster VALUES (7), (11)")
    bindings = {"version": 1, "facts": {"pair": {"table": "Pair.data", "roles": {"key": "Key ID", "label": 'a"b'}},
                                         "listed": {"table": "listed", "roles": {"key": "id"}}},
                "instances": {"key": {"table": "roster", "column": "id"}}}
    return model, source, bindings


def test_live_rules_and_witness_limits(tmp_path):
    model, db, bindings = fixture(tmp_path)
    before = hashlib.sha256(db.read_bytes()).hexdigest()
    result = api.check_duckdb(model, db, bindings=bindings, max_examples=1)
    assert result["exit_code"] == 1, result
    unique, mandatory, subset = result["verdicts"]
    assert [r["verdict"] for r in (unique, mandatory, subset)] == ["fail"] * 3
    assert unique["examples"] == [[7, "a"]] and unique["truncated"] and unique["violation_count"] == 3
    assert mandatory["examples"] == [[11]] and subset["examples"] == [[7]]
    zero = api.check_duckdb(model, db, bindings=bindings, max_examples=0)
    assert all(r["examples"] == [] and r["truncated"] for r in zero["verdicts"])
    assert result["snapshot_sha256"] == before == hashlib.sha256(db.read_bytes()).hexdigest()
    with _open(duckdb, db) as conn, pytest.raises(duckdb.Error):
        conn.execute("INSERT INTO listed VALUES (99)")
    with duckdb.connect(str(db)) as conn:
        conn.execute('DELETE FROM "Pair.data"')
        conn.execute('INSERT INTO "Pair.data" VALUES (7, \'a\'), (11, \'b\')')
        conn.execute("INSERT INTO listed VALUES (7)")
    repaired = api.check_duckdb(model, db, bindings=bindings)
    assert repaired["exit_code"] == 0 and all(r["verdict"] == "pass" for r in repaired["verdicts"])
    assert repaired["projection_sha256"] == result["projection_sha256"]
    assert repaired["snapshot_sha256"] != before


def test_refusals_and_disclosure(tmp_path, monkeypatch):
    model, db, bindings = fixture(tmp_path)
    for field, value, reason in (("table", "missing", "missing-base-table"),
                                 ("roles", {"key": "Key ID"}, "incomplete-role-projection"),
                                 ("roles", {"key": 'a"b', "label": "Key ID"}, "incompatible-column-type")):
        bad = deepcopy(bindings)
        bad["facts"]["pair"][field] = value
        assert api.check_duckdb(model, db, bindings=bad)["error"] == reason
    unbound = deepcopy(bindings)
    del unbound["facts"]["pair"]
    result = api.check_duckdb(model, db, bindings=unbound)
    assert result["exit_code"] == 4 and all(r["verdict"] == "unchecked" for r in result["verdicts"])
    monkeypatch.setenv("GND_DISCLOSURE", "customer")
    projected = api.check_duckdb(model, db, bindings=bindings)
    assert all("examples" not in r and "violation_count" not in r for r in projected["verdicts"])
    with duckdb.connect(str(db)) as conn:
        conn.execute("INSERT INTO listed VALUES (NULL)")
    assert api.check_duckdb(model, db, bindings=bindings)["error"] == "null-in-bound-column"
