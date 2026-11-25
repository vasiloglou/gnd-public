# Describe your delivered tables in an Ossie export

Your warehouse already has a refunds table. Its name and columns are not the
ones GND would choose. You want the Ossie files to describe the table your
partner will actually query, and to say which of its columns holds each fact
of the model.

A **binding file** does that. It lists your tables and says which columns
hold which roles. With it, the export describes your tables. Without it,
nothing about the export changes.

!!! info "Files on GitHub"

    [Example binding](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/refunds/physical-binding.json) ·
    [Binding schema](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/schema/physical-binding.schema.json) ·
    [Binding rules](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/representation-format.md#physical-binding)

With the `/gnd` skill, give it this prompt:

> Export the refunds example as an Ossie ontology, described by the tables
> in its example binding. Show me the refunds table it writes and list
> anything in the model the binding leaves out.

## Read the binding

The refunds example ships inside GND with a binding for a small warehouse.
The first command copies the example into a `refunds` folder. The second
prints the binding.

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / 'examples/refunds', 'refunds', dirs_exist_ok=True)"
cat refunds/physical-binding.json
```

```text
{
  "schema": "gnd-physical-binding/1",
  "tables": {
    "crm.customers": {
      "columns": {
        "cust_code": {
          "sql_type": "VARCHAR(12)",
          "targets": [{"kind": "identifier", "object_type": "customer"}]
        }
      },
      "primary_key": ["cust_code"]
    },
    "fin.refunds": {
      "columns": {
        "refund_id": {
          "sql_type": "BIGINT",
          "targets": [{"kind": "identifier", "object_type": "refund"}]
        },
        "cust_code": {
          "sql_type": "VARCHAR(12)",
          "references": {"table": "crm.customers", "columns": ["cust_code"]}
        },
        "amount_cents": {"sql_type": "INTEGER"},
        "pay_channel": {"sql_type": "VARCHAR(20)"},
        "loaded_at": {"sql_type": "TIMESTAMP"}
      },
      "primary_key": ["refund_id"]
    }
  },
  "roles": {
    "refund_by": {
      "refund": ["fin.refunds.refund_id"],
      "customer": ["fin.refunds.cust_code"]
    },
    "refund_amount": {
      "refund": ["fin.refunds.refund_id"],
      "amount": ["fin.refunds.amount_cents"]
    }
  }
}
```

It has two parts:

- **`tables`** is your schema: each table, its columns in order, their SQL
  types, the primary key, and each foreign key as a `references` entry. A
  column that holds the key of a business object says so with an
  `identifier` target. Here `refund_id` identifies a refund.
- **`roles`** connects the model to those columns. For each fact type, each
  role names the column that holds it. `refund_by` says the refund is in
  `refund_id` and the requesting customer is in `cust_code`.

A column the model knows nothing about, such as `loaded_at`, needs no
entry in `roles`. It is still described as part of the table.

## Export with the binding

<!-- gnd-run expect=0 -->
```sh
gnd export ossie refunds/model.orm.yaml --out warehouse.ossie.yaml --physical-binding refunds/physical-binding.json
```

The semantic model now describes your tables, under your names, and the
foreign key becomes one link between them:

<!-- gnd-run expect=0 output=stdout -->
```sh
tail -9 warehouse.ossie.yaml.semantic_model.yaml
```

```text
    data: '{"source_kind":"physical"}'
relationships:
- name: fin.refunds__crm.customers
  from: fin.refunds
  to: crm.customers
  from_columns:
  - cust_code
  to_columns:
  - cust_code
```

Each table is marked `"source_kind":"physical"`: it is a table you
delivered, not one GND proposed. The ontology, the sidecar and the loss
report are the same files, byte for byte, as an export without the binding.

## See what the binding leaves out

The binding does not have to cover the whole model. The mapping file lists
whatever it leaves out, with a reason:

<!-- gnd-run expect=0 output=stdout -->
```sh
grep -o '"id":"[a-z_/0-9]*","kind":"[a-z_]*","reason":"[a-z-]*"' warehouse.ossie.yaml.mapping.yaml
```

```text
"id":"constraints/0","kind":"constraint","reason":"not-relational"
"id":"refund_channel","kind":"fact_type","reason":"unbound"
```

- `refund_channel` is `unbound`: the binding names a `pay_channel` column
  but never says which fact it holds. To fix it, add this entry under
  `roles` and export again under a new name:

    ```json
    "refund_channel": {
      "refund": ["fin.refunds.refund_id"],
      "channel": ["fin.refunds.pay_channel"]
    }
    ```

- The policy about refund amounts is `not-relational`, as it is without a
  binding. No table definition can carry it.

The mapping also records the SHA-256 of the binding file, so a reader can
tell which binding an export was made from.

## When a binding is refused

GND checks the binding against the model before it writes anything. A
binding that names something the model does not have is refused. This
command makes a copy with a misspelled role name and tries it:

<!-- gnd-run expect=3 output=stderr -->
```sh
sed 's/"customer":/"custmer":/' refunds/physical-binding.json > broken.json
gnd export ossie refunds/model.orm.yaml --out broken.ossie.yaml --physical-binding broken.json
```

```text
invalid Ossie export input: binding:unknown-role: refund_by has no role 'custmer'
```

The run stops and writes no file. The message starts with a rule
id, here `binding:unknown-role`. Fix the binding and run again. Do not
change the model to fit a binding. The
[binding rules](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/representation-format.md#physical-binding)
list every rule id and the order GND checks them in.

## Limits

- **Surrogate keys.** A role has to be bound to columns that hold the
  model's own identifier for the object, such as the refund number. A fact
  that a table holds only through a generated id cannot be bound. Leave it
  out of `roles` and it is listed as `unbound`. The table and its foreign
  key are still described.
- **Size.** A binding file can be at most 10 MiB.
- **Not with `--ontology-only`.** That option writes no tables, so the two
  together are a usage error.

[Read the Ossie interchange scope](../explanation/ossie.md).
