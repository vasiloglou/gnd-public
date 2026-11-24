# 17: Objectification (rule 3, S8)

**The model says.** A Student enrolled in a Course is objectified as Enrolment. As in GND's own example, Enrolment is identified externally by its student and course, and an Enrolment has a Grade.

**A Halpin reader expects.** One table, `enrolment`, keyed by the student and course columns, each a foreign key. The objectified fact type's roles match the identification's components by player, so the objectified fact type is the key itself, not extra columns. The grade is a nullable column.
