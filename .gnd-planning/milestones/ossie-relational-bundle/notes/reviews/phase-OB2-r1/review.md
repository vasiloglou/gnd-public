<!-- Sanitized 2026-11-24 under the project.md rule on retained reviewer output: absolute paths
     replaced by <worktree>, <scratch>, <tmp> or <home>. Nothing else was changed. See SANITIZATION.md. -->
All 16 SHA-256 hashes match the brief. **C3, C4 and C5 fail on admitted models.** All findings below were reproduced using models validated through `load_model_bytes`.

1. **F1 — External identification ignores eligibility and preference.** [rmap.py:167](<worktree>/src/gnd/rmap.py:167)  
   In case 14, append a nonpreferred external uniqueness over `state_in_country.country` and `state_has_population.population`. Reversing the top-level constraints changes State’s PK from `(country_country_code, code)` to `(country_country_code, population)` under both variants, despite the original identifier remaining preferred. Separately, changing the original uniqueness to `modality: deontic` still produces its identifying key, while listing that constraint as `uniqueness-not-confirmed`. Identifier selection violates both determinism and the confirmed-alethic requirement.

2. **F2 — Deduplication discards the preferred-key designation.** [rmap.py:232](<worktree>/src/gnd/rmap.py:232)  
   In case 13, remove existing `preferred` flags and append a preferred duplicate of the `(slot, lecturer)` uniqueness. With the duplicate last, the PK is `(room_room_nr, slot_slot_code)`; reversing constraints produces `(slot_slot_code, lecturer_staff_nr)`. Keeping the first duplicate loses the later constraint’s preference. Both variants fail.

3. **F3 — Unique-key order follows declaration order.** [rmap.py:623](<worktree>/src/gnd/rmap.py:623)  
   Extend case 13 with all three two-role candidate keys, preferring `(room, slot)`. Reversing constraints reverses the two entries in `unique_keys`, making the schemas unequal under both variants. Reversing fact-type declarations also changes unique-key order when multiple 1:1 facts land in the same table.

4. **F4 — External uniqueness within one table is discarded.** [rmap.py:648](<worktree>/src/gnd/rmap.py:648)  
   Extend case 01 with functional `customer_has_phone`, then add confirmed alethic external uniqueness over its `phone` role and `customer_has_email.email`. Both columns reside in `customer`, but the mapper returns `spans-tables` and creates no unique key. D4 requires `unique_keys=(("email", "phone"),)`.

5. **F5 — Objectification reports unenforced uniqueness as carried.** [rmap.py:608](<worktree>/src/gnd/rmap.py:608)  
   Add confirmed alethic uniqueness on `student` alone to case 17’s objectified fact. The enrolment PK remains `(student_student_nr, course_course_code)`, with no unique key on `student_student_nr`. Nevertheless, dispositions report the new constraint as `primary_key`. The resulting schema permits multiple courses per student, contrary to that constraint.

6. **F6 — ALTERNATE drops the required subtype foreign key.** [rmap.py:301](<worktree>/src/gnd/rmap.py:301)  
   In case 15, retain only `student_has_gpa`. ALTERNATE produces a `student` table with no foreign keys and no `person` table. The required inherited-key FK is silently discarded because its target was never allocated.

7. **F7 — References to tabled value types receive no FK.** [rmap.py:509](<worktree>/src/gnd/rmap.py:509)  
   Extend case 20 with value type `tag` and an unconstrained binary `entry_tag`. Although `entry` already has a table, `entry_tag` receives no FK to it under either variant. The unconditional value-type branch bypasses FK-group creation.

8. **F8 — Absorbed unary columns remain non-nullable.** [rmap.py:444](<worktree>/src/gnd/rmap.py:444)  
   Add unary `student_active` to case 15. HALPIN places it in `person` with `nullable=False`. The subtype rule requires absorbed placement columns to be nullable.

9. **F9 — Composite identification has superlinear mapping cost.** [rmap.py:167](<worktree>/src/gnd/rmap.py:167)  
   Generate independent externally identified entities, each with two mandatory functional binary facts to shared value types and one preferred external uniqueness across those roles. HALPIN mapping times, excluding loading, were:

   | Entities | Fact types | Seconds |
   |---:|---:|---:|
   | 40 | 80 | 0.008 |
   | 80 | 160 | 0.034 |
   | 160 | 320 | 0.214 |
   | 320 | 640 | 1.634 |

   Profiling counted 900 full fact-map rebuilds at 40 entities and 3,400 at 80. Composite identification still repeatedly scans constraints and rebuilds model-wide maps. The existing benchmark’s direct-reference entities miss this case.

**Checked and found true**

- The 57 tests runnable without temporary files passed, including corpus answers, repository admitted-model mapping, disposition partitions and precedence pins.
- Both existing adversarial cases passed in memory under both variants.
- In-memory declaration reversals passed for 61 existing census/corpus inputs; all 25 corpus models also passed source-path comparisons under both variants.
- No mapper exception or missing disposition row was reproduced after successful loading. This supports C1 and C2 for the exercised inputs, without proving universal totality.
- Matcher checks covered `split("=")`/`split(",")` with legal role `room_2_10`; address `split("/")` with 12 inline unmapped constraints and fact id `room_slot_lecturer_10`; answer-name splitting and two-character prefixes; and generator slicing with `e10000`. No breaking legal input was found. Names containing `=` or `,` were rejected by the loader.

**Could not check**

The complete pytest gate includes temporary-file tests, which the read-only environment cannot run. I ran applicable in-memory equivalents, but did not reproduce the filesystem-relocation tests or original large-model timing fixtures. No files were created or changed.

VERDICT: CHANGES_REQUESTED