<!-- Edited by review_tool.py sanitize: 5 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All supplied SHA-256 hashes matched. I found five issues.

1. **F1 — Composite identifiers read the wrong columns.** [rmap.py:637](<repo>/src/gnd/rmap.py:637) records original key names rather than the actual, collision-resolved columns.

   Reproduce from corpus case 14: change `state_in_country`’s second player to `state_code`, rename its role to `code`, update its reading and external `role_ref`. Both identifying binaries now legally have a component named `code`.

   **Observed:** under both variants, the table key is `('code', 'code_2')`, but `Identification.columns` is `('code', 'code')`. State’s object mapping consequently reads `"STATE"."CODE"` for both referents. A row identified by `(A, B)` becomes `(A, A)`. This falsifies C5 and the mapping’s key correspondence.

2. **F2 — An admitted high-arity fact crashes the default export.** [ossie_relational.py:308](<repo>/src/gnd/export/ossie_relational.py:308) recursively validates the generated link tree without accommodating admitted arities.

   Reproduce from case 01: replace its facts with one fact having 250 `email` roles named `r0` through `r249`, a reading joining `{Email:rN}` placeholders, and no explicit constraints.

   **Observed:** model loading and ontology-only rendering succeed. Default rendering raises `RecursionError: maximum recursion depth exceeded` in mapping validation; the command returns **70** before publication. With `--ontology-only`, it returns **0**. This violates totality.

3. **F3 — Legal names produce duplicate semantic relationships.** [ossie_relational.py:115](<repo>/src/gnd/export/ossie_relational.py:115) copies foreign-key names without ensuring document-wide uniqueness.

   Reproduce with four independent, popular-reference entities: `a`, `a__b`, `b__c`, and `c`, each keyed by `<id>_id`. Add confirmed alethic functional binaries `a → b__c` and `a__b → c`.

   **Observed:** rendering succeeds, but both semantic relationships are named `a__b__c`. The change’s own `cross_check` rejects the result with `AssertionError: duplicate relationship name`. The inherited Rmap naming ambiguity now reaches the new default output.

4. **F4 — Output filenames are inserted as unescaped IRIs.** [ossie.py:488](<repo>/src/gnd/export/ossie.py:488) treats a filesystem basename as an IRI path.

   Reproduce with case 01 and `--out 'report#1.json' --format json`, or the library’s `document_name="report#1.json"`.

   **Observed:** the ontology reference is `./report#1.json`. URI resolution identifies file `report` with fragment `1.json`, rather than the written filename. The semantic-model reference has the same problem. I also reproduced incorrect resolution with `?` and literal `%2F` in filenames. These path characters need IRI encoding. Resolution was checked with `urllib.parse`; the external validator was not run.

5. **F5 — The no-table fallback omits the required relational dispositions.** [ossie.py:475](<repo>/src/gnd/export/ossie.py:475) returns before building either relational document.

   Reproduce from case 01 by marking its fact `derivation: derived`, `storage: computed`, with a textual derivation rule.

   **Observed:** the command returns **0** and supplies only three files for publication. There is no relational extension listing the fact and its two constraints. This is the documented IF1 departure, but it remains inconsistent with approved §6’s five-file default and disposition-totality requirement. The normative prose now describes that departure; it does not establish owner approval for it.

Checks that passed:

- **194 tests passed** across two runs, including approved corpus comparisons, census schema/cross-reference/disposition checks, OB1 byte baselines, and corpus role coverage under both variants.
- Offline validation completed with socket operations blocked and **zero network attempts**.
- Both new artifacts rejected a byte cap of size minus one and succeeded at the exact size.
- Seven corpus cases, both formats: all five artifacts were identical across repeated runs and substituted source paths.
- Non-functional identifier components were rejected under both Rmap variants. Adding population rows changed only the mapping’s identity.
- Matcher checks passed for `_quoted`, `quoted_identifiers`, and `expression_fields` using reserved words, `a__b`, a 200-character identifier, doubled quotes, Unicode/newline helper inputs, and unary `CASE WHEN` expressions.

I could not run the external oracle or real filesystem publication/rollback checks. Five selected pytest cases could not initialize temporary files in this read-only environment. Adversarial inputs were validated and rendered in memory; command publication was intercepted without writing files. The normal scale test measured **0.665 s → 3.319 s** for 5× input, which supports that generator’s scaling but does not establish universal linearity.

VERDICT: CHANGES_REQUESTED