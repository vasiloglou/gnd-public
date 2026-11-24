# V6: role names and SQL types in other spellings

**Model.** 01 again.

**Binding.** The same table as V1, written differently:
- The roles are named `CUSTOMER ` (capitals and a trailing space) and
  `Ｅ－Mail` (a full-width E and a full-width hyphen).
- The SQL types are `integer` and `character varying (320)`.
- The columns are given as strings.

**What must happen.** Role names match after Unicode compatibility
normalization, ignoring case and anything that is not a letter or digit, so
both names find the model's `customer` and `email`. The two SQL types map to
Integer and String, as in V1.

**Expected files.** The mapping's shape and the dispositions equal V1's. The
semantic model differs only in the raw SQL types it keeps, and the extension
in its two digests.
