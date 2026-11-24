# Rmap answer keys

Hand-derived expected results for the cases in [`../cases`](../README.md).
Nothing here was produced by `gnd.rmap`. The keys were written before it
existed, from the OB2 spec's rules, and then checked only against
structural invariants. Those checks are: every fact type and constraint
appears exactly once; lists are sorted; key and foreign-key columns exist;
and each foreign key targets an existing table's primary key.

`NN.json` is the HALPIN answer. `NN.alternate.json` is the ALTERNATE answer,
present only where the variants differ. Each file is canonical JSON (sorted
keys) of the following object; the `variant` field is left out.

| Member | Content |
|---|---|
| `tables` | sorted by `name`. Each table has: `name`; `subject` (`["object_type", id]` or `["fact_type", id]`); `columns` (key columns first, then placed columns by fact type id and role position; each column is `{name, datatype, nullable, origin}`); `primary_key`; `unique_keys`; and `foreign_keys` (each `{name, columns, target_table, target_columns}`, in column order) |
| `unmapped` | sorted by (`kind`, `id`). Each entry is `{kind, id, reason, detail}`, where `detail` is the constraint type for `not-relational` and otherwise empty |
| `dispositions` | sorted by (`kind`, `id`). Each entry is `{kind, id, carried_as, reason}`. Exactly one of `carried_as` and `reason` is set. |

Every id is compared as a string, so `constraints/10` sorts before
`constraints/2`. A constraint id is `fact_types/<fact type>/constraints/<n>`
for an inline constraint, or `constraints/<n>` for a top-level one.

`carried_as` uses these forms:

| Form | Meaning |
|---|---|
| `["table", T]` | the fact type is table `T` (rule 6) |
| `["columns", T, c…]` | the fact type adds columns `c…` to table `T` (rules 4 and 5) |
| `["key", T, c…]` | the fact type is key columns `c…` of `T`: a reference fact type (rule 1), an identification component (rule 2), or an objectified fact type whose roles match the key (rule 3) |
| `["placement", T]` | the single-role uniqueness that placed its fact type in `T` |
| `["primary_key", T]` | a constraint carried by `T`'s primary key: the uniqueness that is the key, or a uniqueness or mandatory on an identifying fact type |
| `["unique_key", T, c…]` | a uniqueness that is a unique key over `c…` |
| `["implied", T]` | a uniqueness that is implied by a shorter one on the same fact type (placed in `T`) |
| `["not_null", T, c…]` | a mandatory, carried as `nullable: false` on `c…` |
