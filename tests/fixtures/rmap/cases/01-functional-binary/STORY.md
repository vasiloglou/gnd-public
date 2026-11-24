# 01: Functional binary (rule 5)

**The model says.** Each Customer, identified by a CustomerId, has exactly one Email. The uniqueness is on the customer role, and the role is mandatory.

**A Halpin reader expects.** One table, `customer`, keyed by the customer id, with a non-null email column. Email is a plain value type, so it gets no table.
