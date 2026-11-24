# 16: Subtype with its own identifier

**The model says.** Employee is a subtype of Person, identified by its own EmpNr, and has a Salary.

**A Halpin reader expects.** In both variants, `employee` is its own table keyed by the emp number. Its key is not the person key, so there is no foreign key to `person`.
