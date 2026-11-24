# 01: a functional binary

**Model.** A Customer is identified by a CustomerId and has exactly one Email.

**Semantic model.** One dataset, `customer`, with two fields:
`customer_id` (Integer) and `email` (String). Its primary key is
`customer_id`. There are no relationships, because nothing references
another table. The dataset is marked `source_kind: logical`: `customer` is a
table name GND chose, not a table that exists anywhere.

**Mapping.**
- **Objects.** A Customer comes from `customer.customer_id`. Customer has a
  simple identifier, so the object mapping is one expression.
- **Links.** "Customer has Email" is one tree: the Customer from
  `customer.customer_id`, then the Email from `customer.email`. The second
  node names the relationship, because a binary is named at level 2.
- **No mapping for CustomerId and Email.** They are value types with no
  table, and Ossie allows object mappings only on entity types.
- **No link for `gnd_reference`.** That relationship is how the ontology
  writes "Customer is identified by CustomerId". The object mapping already
  says it.

**Extension.** The fact type is carried as a column, its uniqueness as the
placement, and its mandatory constraint as NOT NULL.
