# 05: A fact type with no declared uniqueness (S1)

**The model says.** A Person likes Colors. The fact type declares no uniqueness at all, as 119 of the census's 226 fact types do.

**A Halpin reader expects.** The implied spanning uniqueness applies, since a fact is recorded once. So `person_likes_color` is its own table keyed by both columns, with a foreign key to `person`. The fact type carries no constraint, so it has no constraint dispositions.
