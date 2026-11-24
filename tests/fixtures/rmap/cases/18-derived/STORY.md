# 18: Derived fact types (rule 0, S3)

**The model says.** A Person's age is derived and computed. The birth year is derived but stored. The nickname is semiderived.

**A Halpin reader expects.** Age has no column and is listed as `derived-computed`, together with its uniqueness. The birth year and the nickname are ordinary nullable columns in `person`.
