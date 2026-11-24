# 15: Subtype inheriting its supertype's identifier (D5 variant)

**The model says.** Student is a subtype of Person that inherits the person id, and each Student has a Gpa.

**A Halpin reader expects.** **HALPIN** absorbs the subtype: the gpa is a nullable column in `person`. **ALTERNATE** gives `student` its own table, keyed by the inherited person id, which is also a foreign key to `person`.
