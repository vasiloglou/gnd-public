"""Build a physical binding shaped like delivered DDL from a model's own Rmap schema.

For the OB4 scale and totality tests: every table, key and foreign key of the Rmap
becomes a binding table, and every role placement a `roles` entry. ``keep`` chooses
the fact types to bind; the others are left unbound.
"""

from __future__ import annotations

_SQL = {"String": "VARCHAR(100)", "Integer": "BIGINT", "Boolean": "BOOLEAN", "Float": "DOUBLE PRECISION"}


def binding_from_rmap(model, keep=lambda fact_type: True) -> dict:
    from gnd.rmap import map_model

    schema = map_model(model)
    tables = {}
    for table in schema.tables:
        columns = {}
        for column in table.columns:
            columns[column.name] = {"sql_type": _SQL[column.datatype]} if column.datatype in _SQL else {}
        for key in table.foreign_keys:
            for name in key.columns:
                columns[name]["references"] = {"table": key.target_table, "columns": list(key.target_columns)}
        if table.subject[0] == "object_type":
            for name in table.primary_key:
                columns[name]["targets"] = [{"kind": "identifier", "object_type": table.subject[1]}]
        tables[table.name] = {"columns": columns, "primary_key": list(table.primary_key)}
    roles: dict[str, dict[str, list[dict[str, str]]]] = {}
    for placement in schema.roles:
        if keep(placement.fact_type):
            roles.setdefault(placement.fact_type, {})[placement.role] = [
                {"table": placement.table, "column": column} for column in placement.columns
            ]
    return {"schema": "gnd-physical-binding/1", "tables": tables, "roles": roles}
