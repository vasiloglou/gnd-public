# 04: many-to-many

**Model.** Students and Courses each have an identifier and one attribute.
A Student takes many Courses, and a Course is taken by many Students.

**Semantic model.** Three datasets: `course`, `student`, and
`student_takes_course`. The last holds one row per (student, course) pair,
and both columns form its primary key. Two relationships say that each
column is a foreign key: `student_takes_course__student` and
`student_takes_course__course`. Each goes **from** the table holding the
foreign key **to** the table it references.

**Mapping.**
- **Student** gets two link trees. "Student has StudentName" reads the
  `student` table. "Student takes Course" reads `student_takes_course`: the
  Student from `student_student_nr`, then the Course from
  `course_course_code`.
- **Course** is named as `concept: Course` in the second node, because below
  the root a node says which concept its expression produces.
- The relationship is listed under Student, because the ontology groups
  "Student takes Course" under Student.

**Extension.** The many-to-many fact type is carried as a table, and its
spanning uniqueness as that table's primary key.
