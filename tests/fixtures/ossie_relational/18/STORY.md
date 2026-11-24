# 18: derived fact types

**Model.** A Person has a name, a birth year, a nickname and an age. The
age is **computed** from the birth year and never stored. The birth year is
derived but stored. The nickname is partly derived.

**Semantic model.** One dataset, `person`, with `person_id`, `birth_year`,
`name` and `nickname`. There is **no** `age` field: nothing would fill it.

**Mapping.**
- Three link trees: name, birth year, nickname.
- **No tree for "Person has Age".** The ontology still declares that
  relationship, but no column holds it.

**Extension.** `person_has_age` and its uniqueness constraint are listed
with the reason `derived-computed`. The other three are carried as columns.
