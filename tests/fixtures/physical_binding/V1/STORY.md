# V1: renamed table and columns

**Model.** 01: a Customer has an id and exactly one Email.

**Binding.** One delivered table, `cust`, with `cust_id INTEGER` (the key)
and `email_addr VARCHAR(320)`. `cust_id` is marked as the identifier of
Customer, so `cust` is Customer's home table. Both roles of "Customer has
Email" are bound to the table's two columns.

**Semantic model.** One dataset named `cust`, not `customer`: the names are
the caller's. `INTEGER` becomes Integer and `VARCHAR(320)` becomes String,
and each field keeps its raw SQL type in a `GND` extension. The dataset is
marked `source_kind: physical`.

**Mapping.** The same shape as the built-in mapping for this model, over the
caller's names: a Customer from `cust.cust_id`, its Email from
`cust.email_addr`.

**Extension.** The fact type is carried in `cust`. Its uniqueness is the
table's primary key. Its mandatory constraint is `not-relational`: a binding
says nothing about NULLs. `binding_sha256` is the digest of `binding.json`.
