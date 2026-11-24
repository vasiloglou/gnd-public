# V2: schema-qualified tables and two foreign keys

**Model.** 04: Students take Courses, many to many.

**Binding.** Three tables in a schema: `uni.student`, `uni.course` and
`uni.enrolled`. Each column of `uni.enrolled` has a `references` block. The
roles of the two attribute fact types are written as strings
(`uni.student.nr`); those of the many-to-many as objects.

**Semantic model.**
- The datasets come out sorted (`uni.course`, `uni.enrolled`, `uni.student`),
  whatever order the binding lists them in.
- Two relationships, `uni.enrolled__uni.student` and
  `uni.enrolled__uni.course`, in the order of their columns in the table.

**Mapping.** A table name with a dot is quoted whole:
`"UNI.ENROLLED"."STUDENT_NR"`. The string `uni.student.nr` is not split on
its dots; it is looked up among the declared tables and columns.

**Extension.** All three fact types are carried, and each uniqueness is its
table's primary key.
