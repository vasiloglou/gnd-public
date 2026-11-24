# 25: Unmatchable identification

**The model says.** State is identified by its Country and code. District is identified by its State and a number. That is a composite inside a composite, which `refscheme` does not resolve.

**A Halpin reader expects.** State still maps: a table keyed by its two columns. Country has no table, so there is no foreign key. District and everything placed in it, its fact types, their constraints and its external uniqueness, are listed as `identification-unmatchable`. The Rmap returns; it does not raise.
