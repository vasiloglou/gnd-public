# 04: Many-to-many binary (rule 6)

**The model says.** Students and courses each have a name or title. A student takes many courses and a course has many students, and the uniqueness spans both roles.

**A Halpin reader expects.** Three tables: `student` and `course`, plus `student_takes_course`, keyed by both columns, with a foreign key to each entity table.
