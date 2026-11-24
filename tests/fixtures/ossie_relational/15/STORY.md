# 15: a subtype that inherits its identifier

**Model.** A Person has an id and a name. A Student is a Person and may
have a Gpa.

**Semantic model.** One dataset, `person`. Under the HALPIN variant the
Student has no table of its own: its `gpa` lands in `person` as a nullable
column.

**Mapping.**
- **Person** has an object mapping and its name link, as usual.
- **Student has no object mapping.** Nothing in `person` says which rows are
  Students, so the mapping does not claim to list them. The extension
  records this as `subtype-absorbed`.
- **Student has Gpa is still mapped**, under Student: the Student from
  `person.person_id`, then the Gpa from `person.gpa`. A row with no gpa
  gives no link (decision E8), so only actual Students appear.

**Extension.** Both fact types are carried as columns of `person`. Its
`concepts` list holds Student with the reason `subtype-absorbed`.
