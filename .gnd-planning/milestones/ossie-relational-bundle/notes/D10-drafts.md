# D10 drafts: the three issues and the questions for the reporter

**Status: drafts for the owner, 2026-11-25. Nothing here has been sent or
filed.** Each text needs the owner's confirmation before it goes out
(plan D10). The texts name no downstream project or customer; the reporter's
case is "a large composed model".

## Issue 1 (to file, then close against PR 266)

**Title:** `gnd export ossie`: make the 10 MiB output bound a parameter

**Body:**

`gnd export ossie` applied a fixed 10 MiB bound to each file it writes. A
large composed model (about 1,400 entity types and 4,500 fact types) needs
about 32 MiB for its sidecar and loss report, so the export was refused.

Requested: a parameter such as `--max-output-bytes N`, with 10 MiB as the
default so that nothing changes without it, applied to every written file.

Acceptance:

- Without the flag the output is byte-identical to before.
- With `--max-output-bytes 33554432`, a model above 10 MiB exports
  completely.
- A test covers both.

Delivered in PR 266: `--max-output-bytes N` on export and
`--max-input-bytes N` on `gnd import ossie`, from 1 byte to 256 MiB. An
export above the bound is refused whole (`ossie:output-size`, exit 3); no
file is truncated. The model file itself stays capped at 10 MiB.

## Issue 2 (to file, then close against PRs 270 and 271)

**Title:** `gnd export ossie`: also write the Ossie semantic model and mapping

**Body:**

`gnd export ossie` wrote only the ontology. A consumer of an Ossie bundle
also needs the semantic model (datasets, fields, keys, relationships) and
the mapping from concepts and roles onto them. Without them the ontology
cannot be connected to tables.

Requested: write `OUT.semantic_model.<fmt>` and `OUT.mapping.<fmt>` beside
the ontology, derived by the Halpin relational mapping; validate both
against the pinned Ossie schemas; list what the relational form cannot carry
under a `GND` extension of the mapping; keep the three-file output under
`--ontology-only`.

Acceptance:

- 0 schema errors for all three files against the pinned schemas.
- Every fact type is mapped or listed in the extension.
- The output is byte-for-byte reproducible.
- `--ontology-only` output equals the earlier output.

Delivered in PRs 270 (the relational mapping, `gnd.rmap`) and 271 (the two
files). Two points the request left open are decided: a confirmed alethic
uniqueness inside one table is written as a unique key; and a model's sample
population is never written to a relational file. A model that maps to no
table writes the three ontology files and a note.

## Issue 3 (to file, then close against PRs 272 and 273)

**Title:** `gnd export ossie`: describe delivered tables with `--physical-binding`

**Body:**

The tables of the built-in mapping are named after the model. When a team
delivers its own relational schema, the names differ, so the semantic model
and mapping do not describe the tables a consumer receives.

Requested: `--physical-binding FILE`, a JSON document under a schema shipped
with GND, listing the delivered tables (columns, SQL types, primary keys,
foreign keys) and, per fact type and role, the columns that hold it. Refuse
a binding that names an unknown fact type, role, object type, table or
column. List an unbound fact type in the mapping's extension with the
binding's SHA-256. Without the flag, change nothing.

Acceptance:

- The datasets equal the delivered schema, and the relationships equal its
  foreign keys.
- A contradicting binding is refused with a clear message.
- Tests cover a valid binding, an unknown name and an unbound fact type.

Delivered in PR 272, with a fix in PR 273 so that a table name that is not a
plain identifier, such as a schema-qualified `fin.refunds`, is written the
way Ossie's validator matches it. The schema is `gnd-physical-binding/1`.
Known limit: a fact held only through a surrogate key cannot be bound.

## Message to the reporter

The three requests are on `main` and will be in the next release. Before we
call them done we would like your answers to a few questions, because the
binding format was built from the issue's prose.

1. **Your binding file.** Would you run your existing file through
   `gnd export ossie --physical-binding` and send the outcome? Set
   `"schema": "gnd-physical-binding/1"`. In our schema a foreign key is a
   `references` member of the **column** (`{table, columns}`), beside
   `targets`. If yours puts it inside a target, tell us and we will look at
   accepting that form.
2. **`extension_roles`.** We read it as bindings for roles that are checked
   and listed but not mapped. Is that what you meant?
3. **Surrogate keys.** Are any of your tables linked only through generated
   ids, with no column holding the business identifier? Such a fact type
   cannot be bound today and is listed as unbound.
4. **Table names.** Are your table names schema-qualified or otherwise not
   plain identifiers?
5. **Source size.** How large is your flattened model file? Export still
   needs the model itself to be at most 10 MiB.
6. **Your acceptance checks.** Can you run them on `main` and share the
   result: datasets against your schema, relationships against your foreign
   keys, and the two counts?
7. **Your three local changes.** If you can share them, we would read them
   for reference only.

One change to expect: a default export now writes five files. Add
`--ontology-only` for the earlier three.
