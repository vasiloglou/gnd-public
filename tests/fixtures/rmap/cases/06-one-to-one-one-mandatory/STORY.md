# 06: 1:1 with one mandatory role

**The model says.** An Employee drives at most one Car, and each Car has exactly one driver: uniqueness on both roles, mandatory on the car role.

**A Halpin reader expects.** The mandatory side decides the placement. The fact goes into `car` as a non-null driver column with a foreign key to `employee`, and the employee-side uniqueness becomes a unique key on that column.
