# V4: an unbound fact type and an extension role

**Model.** 14 again.

**Binding.** The same tables, but `city` has only its id, and the binding
says nothing about "City is in State". "State has Population" is bound under
`extension_roles` instead of `roles`.

**Semantic model.** `city` has one field. Only `state__country` remains as a
relationship.

**Mapping.**
- **No link for "City is in State".** City still has an object mapping,
  because `city` is its home table.
- **No link for "State has Population".** What an extension role means is
  not settled, so nothing is mapped from it.

**Extension.**
- `city_in_state` and its two constraints carry the reason `unbound`.
- `state_has_population` and its constraint carry `extension-role`, and the
  `extension_roles` list shows where its two roles were bound.
- An unbound fact type is not an error: the run succeeds.
