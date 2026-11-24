# 02: Reference fact type carried as the key (rule 1, S4)

**The model says.** Country(.country_code) uses a popular reference, and the model also spells out that reference as a fact type: a Country has a CountryCode, with uniqueness both ways and the country role mandatory. Countries also have a name.

**A Halpin reader expects.** One table, `country`, keyed by the code. The explicit reference fact type adds no second code column: it **is** the key. Its three constraints are carried by the primary key. The name is a nullable column.
