# 08: 1:1 with neither role mandatory (D5 variant)

**The model says.** A Person holds at most one Passport, and a Passport has at most one holder. Neither role is mandatory.

**A Halpin reader expects.** **HALPIN** puts a nullable, unique holder column into `passport` (Passport sorts before Person), with a foreign key to `person`. **ALTERNATE** puts a nullable, unique passport column into `person`. Passport then has no table, so there is no foreign key.
