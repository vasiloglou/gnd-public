# 20: A value type as the determining player (S7)

**The model says.** Two value types: each Entry has at most one Elapsed. No entity is involved.

**A Halpin reader expects.** Entry determines the fact, so it gets a value-type table `entry`, keyed by its own value, with a nullable elapsed column.
