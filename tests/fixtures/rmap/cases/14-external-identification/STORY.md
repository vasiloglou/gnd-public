# 14: Composite external identification and a composite foreign key (rule 2)

**The model says.** A State is identified by its Country and its state code, through a preferred external uniqueness. A City lies in one State.

**A Halpin reader expects.** `state` is keyed by two columns, the country and the code, and the country column is a foreign key to `country`. Its identifying fact types are carried as the key. `city` holds a two-column foreign key to `state`, in the order of the identification.
