# V3: a composite key and a two-column foreign key

**Model.** 14: a State is identified by its Country and its code; a City
lies in one State.

**Binding.** `state` has the key (`country_cd`, `state_cd`). `city` holds its
State in two columns, `st_country_cd` and `st_cd`, and both carry the same
`references` block naming `state (country_cd, state_cd)`.

**Semantic model.** `city__state` is **one** relationship over two columns,
not two relationships. The city columns pair with the referenced columns in
the table's column order: `st_country_cd` with `country_cd`, `st_cd` with
`state_cd`.

**Mapping.**
- A State is found by two referent mappings, in the ontology's
  `identify_by` order: its Country (from `state.country_cd`), then its code.
- The role "State" of "City is in State" lists two columns in that same
  order, so the City's State is read from `city.st_country_cd` and
  `city.st_cd`.

**Extension.** All five fact types are carried. The external uniqueness is
`state`'s primary key.
