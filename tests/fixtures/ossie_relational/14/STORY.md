# 14: external identification

**Model.** A Country has a code. A State is identified by its Country
together with its StateCode. A City has an id and lies in one State.

**Semantic model.** Three datasets.
- `state` has a two-column primary key: `country_country_code` and `code`.
- `city` carries both of those as `state_country_country_code` and
  `state_code`.
- Two relationships: `city__state` is one foreign key over **two** columns,
  in key order; `state__country` is the single-column one.

**Mapping.**
- **State objects** need both parts, so the object mapping is a list of
  referent mappings in the order of the ontology's `identify_by`:
  - `state_in_country` leads to a Country, which is itself an entity. The
    mapping therefore nests one level and names Country's own identifier,
    `gnd_reference`, from `state.country_country_code`.
  - `state_has_code` is a value, read from `state.code`.
- **State links.** Its three fact types each get a tree whose root repeats
  that object mapping. The two identifying fact types are mapped like any
  other.
- **City in State.** The City comes from `city.city_id`. The State comes
  from the same two-part pattern, but reading the **city** table's columns.

**Extension.** The two identifying fact types are carried as key columns,
and the external uniqueness as `state`'s primary key.
