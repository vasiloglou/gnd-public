<!-- Edited by review_tool.py sanitize: 8 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All 21 listed SHA-256 hashes match. **Changes are required.** The original repair examples pass, but broader loader-admitted inputs still break the claims.

All reproductions below use existing corpus documents, serialize the mutations as JSON, and validate them through `load_model_bytes`. Findings affect both variants unless stated otherwise.

1. **F1 — An unresolvable objectification can crash mapping.** [rmap.py:480](<repo>/src/gnd/rmap.py:480)  
   Combine cases 14 and 17. Add mandatory functional binary `a_enrolment_in_state(enrolment, state)`, and replace the course component of Enrolment’s preferred identifier with its `state` role. Enrolment now has an unresolved nested composite identifier, while its objectification still permits the documented fallback. Both variants instead raise `AttributeError: 'NoneType' object has no attribute 'origins'`. The rule-2 path dereferences a missing key, violating totality and preventing dispositions from being returned.

2. **F2 — Tied identifiers still depend on declaration order.** [rmap.py:163](<repo>/src/gnd/rmap.py:163)  
   In case 14, duplicate the preferred external uniqueness and reverse the duplicate’s `role_refs`. Reversing the top-level constraints changes State’s PK from `(country_country_code, code)` to `(code, country_country_code)`. The sorted references tie, so the first declaration wins. C1’s declaration-order independence remains false.

3. **F3 — Duplicate external uniqueness constraints produce separate keys and dispositions.** [rmap.py:711](<repo>/src/gnd/rmap.py:711)  
   Extend case 01 as regression R4 does, with `customer_has_phone` and external uniqueness over `phone` and `email`. Append a duplicate with reversed `role_refs`. The schema contains both `("email", "phone")` and `("phone", "email")`; their dispositions differ too. They constrain the same roles and should form one key with one shared disposition, as C2 requires.

4. **F4 — ALTERNATE cannot inherit a composite identifier.** [rmap.py:184](<repo>/src/gnd/rmap.py:184)  
   Add entity `special_state`, with `subtype_of: [state]` and `inherits_reference: true`, to case 14, plus unary `special_active`. ALTERNATE lists the subtype and unary as `identification-unmatchable`, creating neither its table nor its supertype FK. It should inherit State’s two-column key. HALPIN maps this input successfully.

5. **F5 — Composite value components still miss required foreign keys.** [rmap.py:231](<repo>/src/gnd/rmap.py:231)  
   In case 14, give `state_code` a table by adding functional binary `state_code_label(code: state_code, label: label)`, uniquely determined by `code`. State’s identifying `code` column receives no FK to `state_code`, although that table exists. Value components record `None` instead of an FK component, bypassing RR7’s repair.

6. **F6 — A selected identifier bypasses unmapped-reason propagation.** [rmap.py:700](<repo>/src/gnd/rmap.py:700)  
   In case 14, mark `state_has_code` as `derivation: derived`, `storage: computed`, with a derivation rule. That fact is correctly `derived-computed`, but its identifying external uniqueness remains carried as `("primary_key", "state")`. The normative external-uniqueness rule requires it to take the referenced fact’s unmapped reason.

7. **F7 — External uniqueness over unary roles constrains Boolean flags.** [rmap.py:692](<repo>/src/gnd/rmap.py:692)  
   Add unary `other_flag(subject: person)` to case 09 and external uniqueness over `person_smokes.person` and `other_flag.subject`. The mapper creates `unique_keys=(("person_smokes", "other_flag"),)`. Those columns store predicate truth, whereas the referenced roles contain person identifiers. The result imposes uniqueness on flag combinations instead of the referenced values.

8. **F8 — External-key deduplication is quadratic.** [rmap.py:676](<repo>/src/gnd/rmap.py:676)  
   Extend case 01 with *N* functional phone facts using distinct role names, and *N* external keys pairing each phone with `email`. Each insertion scans all previous keys. Equivalent in-memory comparison instrumentation counted 19,900 comparisons at N=200 and 319,600 at N=800, under both variants: exactly N(N−1)/2. Uninstrumented HALPIN times rose from 0.109 seconds at N=3,200 to 1.016 seconds at N=12,800; the latter model loads within the 10 MiB cap. C5’s linear-time claim therefore remains false.

Checks that passed:

- **57 pytest tests**, including corpus answers, admitted-model mapping, disposition partitions and precedence.
- All **14 RR1–RR8 regression cases**, using an in-memory replacement for their filesystem helper.
- RR9’s composite benchmark under both variants: approximately 4× mapping time for 4× entities.
- The existing large benchmark under both variants: approximately 0.09 seconds at 1× and 0.54–0.57 seconds at 5×.
- Declaration reversals for 63 census/corpus models; source-path comparisons for all 25 corpus models; both existing adversarial cases.
- All 66 rows of the recorded variant measurement reproduced exactly.
- Matcher checks: address `split("/")` with fact ID `room_slot_lecturer_10` and constraint indices above 9; role dictionary and tuple slicing with role `room_2_10` and multiline Unicode provenance; answer-name splitting with `25.alternate.json`; and case-prefix slicing with `25-nested-composite`. No breaking input was found in those checks.

The complete filesystem-dependent pytest gate and physical relocation tests could not run in this read-only environment. Three include-bearing models were excluded from the in-memory declaration-reversal check. No files were changed and no credentials were accessed.

VERDICT: CHANGES_REQUESTED