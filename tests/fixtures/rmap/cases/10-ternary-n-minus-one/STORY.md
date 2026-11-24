# 10: Ternary with an n−1 uniqueness (rule 6, S5)

**The model says.** A Person played a Sport for a Country, and each person and sport pair has one country.

**A Halpin reader expects.** This is a compound uniqueness, so it gets its own table, keyed by person and sport. Only Person has a table, so only the person column is a foreign key. Plan rule 2 would have grouped this into an entity table; S5 corrects that.
