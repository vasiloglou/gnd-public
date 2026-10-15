# Registrar rules

These are the rules as the registrar would say them. `/gnd:gnd-model-from-text`
turns this file into `model.orm.json`.

- A student can't take a course before passing every course it needs,
  directly or through a chain of prerequisites.
- A student doesn't enroll in a course they have already passed.
- A student takes at most 6 courses in a term.
- A student takes at most 18 credits in a term.
- A student has one grade per course, and once a grade is recorded it never
  changes.
- Only courses offered that term can be taken.

## What the registrar does

- Enroll a student in a course for a term.
- Drop a course, or every course in a term.
- Record a grade, which also marks the course as passed.
- Admit a new student.

## The spring catalogue

| Course | Credits | Needs | Offered |
|---|---|---|---|
| CS101 Intro to Programming | 4 | | spring |
| MATH120 Calculus | 4 | | |
| MATH220 Linear Algebra | 4 | MATH120 | spring |
| STAT210 Probability | 3 | MATH120 | spring |
| CS230 Data Structures | 4 | CS101 | spring |
| CS250 Databases | 3 | CS101 | fall |
| CS340 Machine Learning | 4 | CS230, MATH220, STAT210 | spring |
| PHIL101 Logic | 3 | | spring |

Maya has passed CS101, MATH120 and CS230.
