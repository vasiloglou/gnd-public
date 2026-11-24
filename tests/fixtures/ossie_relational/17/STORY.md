# 17: objectification

**Model.** A Student enrols in a Course, and each enrolment is itself a
thing, an Enrolment, which may have a Grade. An Enrolment is identified by
its Student and its Course.

**Semantic model.** Three datasets. `enrolment` has one row per enrolment,
keyed by `student_student_nr` and `course_course_code`, plus the nullable
`grade`. Two relationships make each key column a foreign key, to `student`
and to `course`.

**Mapping.**
- **Enrolment objects** use two referent mappings, one per identifying
  relationship. Each leads to an entity, so each nests that entity's own
  identifier.
- **"Student enrolled in Course"** is listed under Student and reads the
  `enrolment` table: the same rows that are Enrolments are the links of the
  objectified fact type.
- **Enrolment's own fact types** (for Student, for Course, has Grade) each
  get a tree rooted at the Enrolment.

**Extension.** The objectified fact type and the two identifying ones are
carried as key columns of `enrolment`. The grade is a column.
