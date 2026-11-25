All SHA-256 hashes match the brief.

1. **Findings:** None.

2. **Checked and found true:**

   - **C1:** Schema inspection and adversarial inputs found no unskipped location where `bind` or `head` incorrectly selects role-map behavior.
   - **C2:** Compared against `102110b2`: 105 schema-valid fixtures preserved shared-node order; removed nodes were confined to documented exclusions. Added nodes also occur for roles named `bind` and `head`, whose term roots the old suffix check skipped.
   - **C3:** The three release-note bullets cover the observed behavior changes. Version fields, `TAGGED`, tag-only wording, install command, and retained 0.5.0 install pins agree.
   - **Executed:** 34 tests passed, plus 165 head/role/term combinations and 250 metadata/data cases.
   - **Standing matcher check:** Tested `_ROLE_MAPS` and `_NOT_SYNTAX` with all colliding names, nested objects, nested temporal functions, Unicode, quotes, and line breaks. No breaking input found. No new regex, split, or slice was introduced.

3. **Could not check:** Tests requiring temporary files and an actual tag installation were excluded by the read-only requirement. Relevant validation behavior was exercised directly in memory. Remote tag/publication state was not verified.

VERDICT: APPROVE