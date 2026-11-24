# 23: Unit-based reference (S9)

**The model says.** Each Person has at most one Height, measured in cm. `refscheme` cannot resolve a unit-based reference, so the Rmap handles it first.

**A Halpin reader expects.** Height has no table. `person` gets a nullable Number column named after the role and Height's value column.
