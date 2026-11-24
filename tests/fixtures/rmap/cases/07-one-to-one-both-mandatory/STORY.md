# 07: 1:1 with both roles mandatory (D5 variant)

**The model says.** Each Country has exactly one capital City, and the model records only capital cities, so both roles are mandatory and unique.

**A Halpin reader expects.** **HALPIN** places the fact toward the player whose id sorts first: City. So `city` gets a non-null, unique country column with a foreign key to `country`. **ALTERNATE** places it toward the player with more functional roles: Country, with 2. Then `country` gets a non-null, unique capital column, and City has no table, so there is no foreign key. In each variant, the mandatory on the side that does not hold the column cannot be stated relationally and is listed.
