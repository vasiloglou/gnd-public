# Close reading one: completion predicates against evidence and bytes

Reader: close reader ONE (predicates lens). Bytes read: worktree HEAD `85880f5`
(branch `claude/ik-milestone-close`), with untracked `.agents/skills/` and
`.claude/launch.json` ignored. Read-only. I ran targeted pytest nodes and small
CLI reproductions only. Scratch files are under this `readers/` directory
(`r1-excl/`, `r1-date/`, `mutant-excl/`).

## Verdict table

| Item | Verdict | Evidence |
|---|---|---|
| **P1 IK1 descriptions** | MET WITH RESIDUAL | T1–T14 and the q1 cases exist. I ran `tests/test_object_type_description.py -k "t7 or t8 or t9"`: 13 passed. T7 checks rows 1–7 against `ik1-baseline.json` (base `1d6eee0`), so it still holds on HEAD. T8 compares the diff exit with the identical-model exit (`test_object_type_description.py:380-384`). The close fix IK1-Q2 adds annotations to text-format diff (`commands/checking.py:284-290`), and `test_ik_close.py:199` covers it. **Residual (finding 3):** the predicate says the "fixed core keys render in … generated tool docstrings". The shipped code renders `summary` only, which plan §2 intends and `test_t4_docstrings_render_summary_only` (`:249`) pins. |
| IK1-C1 | MET | T1, T2 and q1 cases; record 002 table; amendment 004 adds the 64-level cap |
| IK1-C2 | MET WITH RESIDUAL | Same wording gap as P1. C2 says codegen docstrings render "the neutralized core keys", but only `summary` renders (finding 3) |
| IK1-C3 | MET | T8, T10, T11; diff schema `if/then` checked by `test_t8_diff_schema_refuses_mismatched_version_and_annotations` |
| IK1-C4 | MET | T7, rerun green on HEAD (above) |
| IK1-C5 | MET WITH RESIDUAL | T9 green. Reference updates are review-checked only, as the plan says. Close fix IK1-Q5 now pins the surface list in `evolution-contract.md` (`test_ik_close.py:215`) |
| **P2 IK2 induced provenance** | MET | `tests/test_ik_close.py` plus `tests/test_induced_provenance.py`: 173 passed (my run). The record 003 corpus covers A01–A17, the T5 27-row D-12 baseline and T15 coverage goldens (`test_public_coverage_goldens.py` is in `evidence/IK2/gate-files.txt:48`). Caveats already recorded: induction blocks are recorded claims, single-token raw values are indistinguishable from ids, and `rejected_proposals` is unchecked by owner ruling |
| IK2-C1 | MET | record 003 C1 row; L01–L38 |
| IK2-C2 | MET | A01–A17, T5–T9, R3 |
| IK2-C3 | MET | T11, T15 |
| IK2-C4 | MET | B01–B34 |
| **P3 IK3 measure, two modes** | MET WITH RESIDUAL | Class cells all carry numerator/denominator. Reproduced on the refunds example: `gnd measure model.orm.yaml --labels labels.json --format json` gave exit 0, schema 5, and six cells each with `numerator`/`denominator`. Synth byte identity is a real golden test: `test_public_measurement_publication.py::test_each_committed_payload_reproduces_byte_for_byte`, which is in `evidence/IK3/gate-files.txt:38`. **Residual (finding 5):** IK3-C2 "identical" is narrowed by owner ruling C-F2. X1 ignores `wrong_attribution` and `set_attributed_evidence` (`ik3-corpus/expected.json` X1 `ignored_row_fields`; `phase-IK3-spec.md:300-302`) |
| IK3-C1 | MET | T1, T2, R1–R3; close fix IK3-Q2 (`measure/labels.py:305-312`) |
| IK3-C2 | MET WITH RESIDUAL | parity holds except the two C-F2 fields (finding 5) |
| IK3-C3 | MET | C1, C2, N1 per record 006 |
| IK3-C4 | MET | golden test above; N1 work counter |
| **P4 IK4 discover** | MET WITH RESIDUAL | Pass plus support > 0: T3 (`test_discover.py:216-222`), and the T4 seeded wrong discoverer (`:225-239`). N1 near-cap: the generated population is 9,349,598 bytes, about 89% of 10,485,760, and I ran `test_ik4_corpus[N1]` (1 passed). The ceiling `74531600` is fixed in the answer key. **Residual (finding 2):** "an evolve proposal that IK2's gate admits" is false for any model that holds a YAML-only value. I reproduced `gnd evolve preview` on a discover proposal for a date-bearing valid model: exit **70**, "Object of type date is not JSON serializable". This is carried as IK4-Q3 |
| IK4-C1 | **NOT MET as worded** | "Every family has a positive case": the **exclusion** family has none. No corpus case or test emits an exclusion (finding 1) |
| IK4-C2 | MET WITH RESIDUAL | holds only for models evolve can preview (finding 2) |
| IK4-C3 | **NOT MET as worded** | T5's oracle cases K01, K02, K03, K05, K06 and K08 cover six families; none emits exclusion. An exclusion-support mutant survives all 160 discover tests (finding 1) |
| IK4-C4 | MET | N1, R11, R13 |
| IK4-C5 | MET | K09, R12, R13 |
| **P5 IK5 bridge** | MET WITH RESIDUAL | `test_d1_export_is_the_same_under_two_hash_seeds` (`test_ilp_bridge.py:121-132`) compares the X1 Popper tree under seeds 0 and 1 with the committed `expected-export/popper` tree, which holds both `neutral.json` and `popper/*.pl`. The X1 answer also pins `export_sha256` (`0ee67d23…`). Import refusal on set mismatch: M1 and M2. **Residuals:** no real Popper ran (IK5-Q5), and learner fixtures are hand-authored, not "recorded" (D13 (a)). Scope limits the close spec omits (finding 6): Integer comparisons only; value types other than Integer/String/Boolean are refused; reference-bearing models are refused; the export writes raw non-redacted values to the learner's input |
| IK5-C1 | MET | as above |
| IK5-C2 | MET | F01–F20, R5, R8. Close fix IK5-Q3 now names compound aggregates `aggregate` (`test_ik_close.py:109-124`) |
| IK5-C3 | MET | M1, M2 |
| IK5-C4 | MET WITH RESIDUAL | B1–B5 refuse mismatched bindings. The fixtures are hand-authored (D13 (a)) |
| **P6 IK6 walk** | MET WITH RESIDUAL | `tests/test_ik6_walk.py`: 30 passed (my run). The runner uses `bash -euo pipefail` (`tools/run_tutorials.py:164`), so piped `| grep` blocks cannot hide a gnd failure. **Residual (finding 4):** the walk deliberately contains `expect=3` (`docs/how-to/learn-rules-commands.md:108`), so "exits 0 at every step" holds only for the predicate's four named steps. The learn step is a stand-in learner on `--target neutral`; the walk never exercises the Popper adapter. **"Each listed census row has a check" is stale (finding 7)** |
| IK6-C1 | MET WITH RESIDUAL | T1 and T2; same caveat as P6 |
| IK6-C2 | MET WITH RESIDUAL | census test green (9 passed), but blind to the close edit (finding 7) |
| IK6-C3 | CANNOT TELL for the final bytes | The IK6 gate and T7 installed check passed on IK6 bytes. The close commit edits RF6/RF7 controls, `tools/run_tutorials.py` and five `src/gnd` modules, and `evidence/close/` holds no gate output yet. My targeted runs: `test_rf6_query_policy.py` plus `test_rf7_structure.py` gave 19 passed. The close gate (C-G1) is still running |
| **P7 per-phase protocol** | MET WITH RESIDUAL (phase half) / NOT YET MET (close half) | Phases IK1–IK6 and IK4-Q2 each have a spec gate, a gate run, one reviewer, a refactoring section and a record. Residuals the close spec omits (finding 8): the **IK4 gate exited 1** (`005-phase-IK4.md:9-10`, a pre-existing failure); the **IK2 gate missed `test_rf8_structure.py`** (README:56-59, repaired afterwards); amendments 004 and 008 and the IK2 repair had **no adversarial or refactoring review** (`004:52-53`, `008:45-46`). Close half: four-reviewer evidence is in progress, the question sweep is present (§5), and no PR or owner acceptance exists yet |

## Findings

### 1. Exclusion has no positive case and no oracle row (completeness; IK4-C1 and IK4-C3 false as recorded)

**Claim.** Record 005 marks IK4-C1 ("every family has a positive case and a counterexample case") and IK4-C3 ("support … per family match an independent brute-force oracle") as met. No committed test ever emits an `exclusion` candidate, so exclusion support is untested.

**Reproduction.**
- Families emitted per corpus case, from `ik4-corpus/expected.json`:
  - K01 uniqueness; K02 mandatory; K03 and K04 value; K05 frequency;
  - K06 equality and subset, with all exclusions rejected as `warning`;
  - K07 subset;
  - K08 uniqueness, mandatory, value, frequency, subset and equality;
  - K09 uniqueness, mandatory and equality.
  - No case emits exclusion.
- `grep exclusion tests/test_discover.py` finds only `test_r13_exclusion_needs_both_sides`, which asserts `emitted == []`.
- T5's oracle list is `["K01","K02","K03","K05","K06","K08"]` (`test_discover.py:297`).
- The behaviour itself is correct. On two disjoint fact types (`readers/r1-excl/`), `gnd discover … --families exclusion` gives `EMITTED 2 … exclusion support=4`, and |a ∪ b| = 4 as the spec defines.
- **Mutant.** In a scratch copy (`readers/mutant-excl/gnd`), `support.exclusion_subjects` was changed to iterate over side A only. The changed line was `order = list(a.items())`. The same CLI run then gave `support=2`. `PYTHONPATH=<mutant> uv run pytest -q -p no:randomly tests/test_discover.py tests/test_ik4_indexed_set_families.py --deselect "tests/test_discover.py::test_ik4_corpus[N1]"` gave `160 passed`. The mutant survives.

**Suggested disposition.** Add one positive exclusion case to `test_discover.py`, either a new fixture or `_discover` with AMOUNT_MODEL and disjoint sides, and add it to T5's oracle list. The oracle already handles exclusion as `len(a | b)`. Alternatively, record IK4-C1/C3 as met for six families, with exclusion as an owner-accepted residual.

### 2. P4 "a proposal IK2's gate admits" fails with exit 70 on YAML-only values (hardening; known, carried)

**Claim.** The close spec's verdict, "met for models that evolve can preview", is honest. But the failure mode is an **internal exit 70**, the same crash class the close fixed for IK4-Q2-Q2. Record 005 had IK4-Q3 owner-targeted at "milestone close", and C-D2 moves it to a follow-up PR.

**Reproduction** (`readers/r1-date/`). Take `ik4-corpus/staff.orm.yaml` with `created: 2024-01-01` added under `source:`.
- `gnd validate` gives `OK`.
- `gnd discover … --families uniqueness` gives exit 0.
- `gnd evolve preview staff.orm.yaml p.json --workspace … --records … --out …` gives `EVOLUTION PREVIEW REFUSED (70): Object of type date is not JSON serializable`, exit=70.

**Suggested disposition.** Keep the carry-forward, but have the close record name the exit (70, not a named refusal). Optionally, ask the owner whether a named exit 3 should land now, mirroring F3.

### 3. P1 and IK1-C2 wording versus the shipped docstrings (completeness: wording)

**Claim.** P1 says the "fixed core keys render in … generated tool docstrings", and IK1-C2 says the docstrings "render the neutralized core keys". The shipped codegen appends only `— <summary>`. This matches plan §2 ("Codegen: adds `summary`") and review R5.

**Reproduction.** `tests/test_object_type_description.py:249-254` asserts that `R-mark`, `SRC-mark` and `N-mark` are absent from docstrings. Record 002:118 reads "codegen docstrings append ` — <summary>`".

**Suggested disposition.** Have the close record state that P1's docstring clause is met as plan §2 scopes it (summary only). Do not edit the plan.

### 4. P6 "exits 0 at every step" versus the walk's deliberate exit 3 (completeness: wording)

**Reproduction.** `docs/how-to/learn-rules-commands.md:108` reads `<!-- gnd-run expect=3 output=stderr -->`, the faulty over-claim import. The other nine blocks are `expect=0`, and the runner uses `bash -euo pipefail` (`tools/run_tutorials.py:164`).

**Assessment.** The close spec already says this (§3 row 6), and I agree with "met for the predicate's steps". One addition for the close record: the "learn" step uses `stand_in_learner.py` with `--target neutral`. The Popper adapter is exercised only by the IK5 corpus, never by the public walk.

### 5. IK3-C2 "identical" is narrowed by C-F2, and the close spec omits it (completeness)

**Reproduction.** In `tests/fixtures/induced_knowledge/ik3-corpus/expected.json`, X1 has `ignored_row_fields: ['wrong_attribution','set_attributed_evidence']`. `phase-IK3-spec.md:300-302` says "This narrows T3's 'byte for byte'". Close spec §3 row 3 says "met" with no caveat.

**Suggested disposition.** Add "(owner-narrowed by C-F2: two fields excluded)" to the close record's P3 row.

### 6. P5 scope limits are missing from the close spec (completeness)

**Reproduction.** Record 007:208-219 lists:
- Integer comparisons only;
- value types other than Integer, String and Boolean refused;
- models with reference populations refused;
- non-printable string constants refused;
- octal-escaped Popper output unparsable;
- the export writing raw non-redacted population values into the learner's input.

Close spec §3 row 5 says only "met; no learner ran", and §5b carries only the reference refusal (IK4Q2-D3) and IK5-Q2.

**Suggested disposition.** Have the close record's P5 row cite record 007's boundary list.

### 7. The skill census is stale for the close edit, and its check cannot see close commits (completeness)

**Claim.** IK6-C2/P6 says "each listed census row has a check". The close commit edits a packaged skill file, but its census row still names only IK1, IK2 and IK4-Q2. The census test passes because its phase regex cannot match the close commit's scope.

**Reproduction.**
- `git show 85880f5 --stat -- src/gnd/skills` gives `src/gnd/skills/gnd-model-evolve/references/evolution-contract.md | 2 +-`.
- `skill-census.md:36` lists that file as changed in `IK1, IK2, IK4-Q2`.
- `tests/test_ik6_skill_census.py:11`: `PHASE = re.compile(r"IK[1-6](?:-Q\d+)?")`. `git_phases` (`:58-64`) extracts phases from commit-subject scopes, and `fix(IK-close)` yields none.
- `uv run pytest -q tests/test_ik6_skill_census.py` gives `9 passed`.

**Suggested disposition.** Add a `close` label to the census row and to the test's phase grammar, or state in the close record that the census describes IK1–IK6 only, and that the close's one skill edit (IK1-Q5) is recorded in close spec §9.

### 8. P7 residuals the close spec's "phase half met" omits (completeness)

**Reproduction.**
- `005-phase-IK4.md:9-10`: `exit: 1`, `1 failed, 6640 passed`. This is the pre-existing `test_prepared_policy_rechecks_live_hashability` (IK4-Q5).
- `README.md:56-59`: the IK2 gate missed `tests/test_rf8_structure.py`, and the runtime import cycle was repaired afterwards (`evidence/IK2-repair/`).
- `004-amendment-IK1-Q1.md:52-53` and `008-amendment-IK5-Q1.md:45-46`: "No adversarial review ran". Neither has a refactoring review.
- Each phase review is "one reviewer is one reviewer" (every record). That satisfies "independent diff review" only in the single-agent sense.

**Suggested disposition.** List these in the close record's P7 row. Amendments are not phases, so this is not a predicate failure.

### 9. Ceiling moved at close (IK5-Q6): IK-R12 arithmetic was never shown to the owner, and the quoted ruling is not the owner's words (hardening; process)

**Claim.** IK-R12 says a bound is never moved after measurement "without an owner-recorded amendment that states its arithmetic". The close raised the import work ceiling from P × (1 + K) to P × (1 + K) + K + 2:
- `export/ilp_service.py:436-439`;
- `docs/reference/ilp-bridge.md:191`;
- two test expectations moved, T9 by + 34 and R6 from 24 to 29 (`tests/test_ilp_bridge.py:370-371,525`).

The arithmetic appears only in close spec §9 F2, which was appended **after** the owner gate. The approved bytes are r1 plus the IK4Q2-D3 row, and §5a's IK5-Q6 row states no formula. F2 also presents `("count the reloads in the work counter")` as the C-D1 ruling text. `grep -rn "count the reloads" .gnd-planning/` finds only close-spec.md:182, and the owner's recorded words are "Approve close spec r1 with C-D1 to C-D4 and C-G1 as proposed." (close-spec.md:148-149).

The earlier precedents each had an owner ruling on stated arithmetic: 004 (IK1-Q1), 008 (IK5-Q1) and the IK4 R11 ceiling correction.

Separately, the new term equals the count by construction: `reloads` is one per `_load_candidate` call, and the term is exactly K + 2. So the term cannot trigger the ceiling check unless the call count changes.

**Suggested disposition.** Ask the owner to ratify the new formula explicitly, ideally in the close record's owner-decisions entry. Replace the parenthetical quote with the owner's actual words, or mark it as a paraphrase of §5a.

### 10. The IK6-R1 exemption's stated rationale is factually wrong (hardening: documentation accuracy)

**Claim.** `tests/support/scan_scope.py:3-4` says packaged examples "read no model through GND's modules", and record 010:147 says the same. That is false:
- `src/gnd/examples/plan_apps/core.py:47-49` does `from gnd.model import load_model; loaded = load_model(...)` and reads `loaded.operations`;
- `examples/expense/extension.py:15` imports `gnd.api.check`.

**Assessment.** Behaviour is unchanged in practice, because each such script was already listed in RF7's standalone list and counted in RF6. But the RF6 model-query scan now silently ignores any future example that queries a model outside ModelIndex.

**Suggested disposition.** Correct the docstring to the ruled scope ("examples are teaching scripts outside the layer map, exempt by owner ruling IK6-R1"), or keep the exemption for parsing only.

### 11. Close spec §2 binding counts predate the close commit (completeness, minor)

**Reproduction.** I recomputed every `path`/`sha256` pair in records 002–010 against HEAD. Results: 002 has **11** mismatches (the spec says 10); 003 has **12** (the spec says 11); 005 has 17; 006–010 have 0. The extra mismatches are `evolution-contract.md` (002) and `rai_import.py`/`evolution-contract.md` (003), all edited by `85880f5`.

**Suggested disposition.** Recompute the counts on the final bytes in the close record.

## What I did not check

- The whole default lane and the close gate (C-G1), which run concurrently. No close gate output exists in `evidence/close/` yet.
- `tools/check_installed_docs.py` and the docs build on the final bytes.
- Each IK2 corpus row's refusal names, each IK5 refusal name (F01–F20), and the "counterexample case per family" half of IK4-C1 for families other than uniqueness and exclusion.
- Reproducing earlier gate counts. I trusted the records' verbatim outputs.
- Privacy and anonymity of the walk outputs (reader three's lens), and ledger consistency beyond the items above (reader two's).
- The approved-bytes digest `be048c88…` in close spec §8.
- RF1 CLI pins on Python 3.11 and 3.13. Records 006 and 007 note goldens captured on 3.14 only, or derived from 3.12.
