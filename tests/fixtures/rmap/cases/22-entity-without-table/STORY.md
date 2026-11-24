# 22: An entity with no placements (S7)

**The model says.** Articles have headlines and are tagged with Tags, many-to-many. Nothing else is said about Tag.

**A Halpin reader expects.** Tag gets no table. The junction table `article_tagged_with_tag` holds the tag name as a plain column, and the only foreign key goes to `article`.
