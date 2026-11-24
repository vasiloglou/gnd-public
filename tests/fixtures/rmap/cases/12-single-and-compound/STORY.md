# 12: A single-role and a compound uniqueness on one fact type (plan F9)

**The model says.** An Employee works in one Department, and the model also declares the redundant uniqueness spanning both roles.

**A Halpin reader expects.** The single-role uniqueness wins, so the fact is a nullable column in `employee`. The spanning one is implied by it and is recorded as `implied`. Department has no table, so the column has no foreign key.
