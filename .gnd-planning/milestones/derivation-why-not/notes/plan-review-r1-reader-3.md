# Reader 3 -- protocol, authority, compatibility and privacy

Retained text of the reader's returned report. No local edits.

Digests matched: plan `77928fb2...cc70` and WN1 spec `cbc99f26...1f03`. Both are byte-identical to the snapshots in `evidence/plan-review-r1/`.

**Verdict: approve-with-fixes**

**Scope.** I read the plan, the WN1 spec, the README and issue #66 in full. I checked them against start-milestone SKILL.md, the four process-phase references, AGENTS.md, and the plans of transition-check-performance, induction-skill and ilp-learners. I also compared the plan's claims with the current code and docs: `api.py`, `witness/{cli,io,view,types}.py`, `extensions.py`, `docs/reference/{cli,python-api,capabilities}.md`, `docs/compatibility.md`, `docs/release-notes.md`, `tools/gnd_layers.json` and the public pin tests.

What holds up:
- Sections 0-10 are all present and in order. Completion predicates, the baseline, the obligation-to-gate map, the closure section and a declared round budget are present too.
- The WN1 spec has all 11 required sections, and its §4 binds WN-R1..R8 and standing rules 1-6 by name.
- Proposals are clearly separated from rulings. Only WN-D8 carries `(o)`, and it says it is "instrument only".
- No downstream repository is named anywhere in the milestone directory (grep checked). The issue names one; the plan correctly does not repeat it.
- These code anchors exist at the cited lines: `__all__` at api.py:119 with 11 names, `_WITNESS_TRACE` at extensions.py:454, `_clause_bindings` :921, `_joined_bindings` :683. The `WitnessLimits` fields `joins`, `binding_cells` and `proof_depth` exist, as do the witness CLI flags `--targets`, `--reference-root` and `--raw`.

## Findings

**R3-F1 -- blocking, medium confidence.** Where: spec §6.2 step 4, §6.3 last paragraph, §7 D6; plan WN-D5 and WN-R2.
- What is wrong: an `unavailable` comparison is folded into top-level `blocked`, which WN-D5 maps to exit 0 ("explanation produced"). `check` reports unavailable data as band `4` indeterminate (cli.md:96-97). So why-not would claim a definite explanation exactly where `check` claims it cannot decide. That is the disagreement WN-R2 calls a defect, and the "blocked read as false" risk in plan §6.
- The spec also covers only unavailable comparisons. `RelationUnavailable` (extensions.py:241) is carried out of band on `_ExactExtensions`, so a derived body relation can also be unavailable. If that relation reads as empty, why-not would wrongly name it as a missing fact. I did not run this; the class and its out-of-band mapping are verified by reading.
- Fix: give the result a top-level status `unavailable`, mapped to exit 4 with a reason distinct from `work-limit`, or add this as an explicit reading in WN-D5 with its exit cost. Make unavailable body relations a stated case with a test in T5 or T14.

**R3-F2 -- hardening, high confidence.** Where: plan §2 surface, WN-R5, WN-D4.
- What is wrong: the plan says the API redacts by default "as with `witness`" (`raw=False`). That does not match the shipped witness API. python-api.md:270-274 says `api.witness` has no `raw` parameter and returns raw values in the certificate; only the CLI view removes them. So either the analogy is wrong, or the new API sets a different privacy default from its sibling without saying so.
- Separately, witness redaction is a "closed metadata selection, never a walk" (view.py, `witness_view`/`result_view`). The why-not payload has more places where values could leak: the claimed row, nested `descent` rows built from raw samples (spec §6.4), `sample_bindings`, and error and reason text. `RelationUnavailable.binding` carries values.
- Fix: in WN-D4, state the API default explicitly as a deliberate difference from `api.witness`, with its cost. Bind WN2 to a closed allow-list view that covers nested descent and the claimed row. Add a WN2 test that no population value appears anywhere in the redacted payload or the error text.

**R3-F3 -- hardening, high confidence.** Where: plan §2 CLI and API signatures; spec §5 `row=None`.
- What is wrong: `--fact-type ID` plus `--targets REQUEST` does not fit the witness request format. `load_targets` accepts 1..256 targets, and each one names its own `fact_type` (io.py:136-153). The kernel takes a single `row`. The plan does not say what happens when a target names a different fact type, or when there are several targets with mixed derived and blocked outcomes, or how that maps to one exit code.
- Fix: decide (as a WN-D1 sub-decision) either a single-target request with a matching fact type (anything else is exit 3), or per-target results with a stated rule for combining them into one exit. Add the cases to WN2-C1.

**R3-F4 -- hardening, high confidence.** Where: plan §3 schema home, completion predicate 3, WN3-C4.
- What is wrong: the plan puts the output schema at `src/gnd/why-not.schema.json`. The witness lane's schemas live in `src/gnd/schema/` (`witness.schema.json`, `witness-result.schema.json`), with a vendored copy at `src/gnd/skills/gnd-export/references/witness.schema.json` pinned in `EXPECTED_SKILL_FILES` (test_packaged_skills.py:23, test_verification_fixes.py:17). Predicate 3 says "vendored", but there is no second home and no identity test.
- WN3-C4 also considers routing from `gnd-dev-session` or `gnd-induce`, but leaves out `gnd-export`, the packaged skill that owns the witness workflow (its SKILL.md runs `gnd witness`). `gnd-induce` is not a packaged skill at this baseline (`src/gnd/skills/` has no such entry).
- Fix: pick the home under `src/gnd/schema/`, and decide whether a vendored copy goes into `gnd-export/references`, with its sync test and both `EXPECTED_SKILL_FILES` pins. Add `gnd-export` to WN3-C4.

**R3-F5 -- hardening, high confidence.** Where: plan WN2-C3, WN2-C4, §5.
- What is wrong: the pin and docs harvest is incomplete.
  - `api.__all__` is also pinned at tests/test_v61_phase2_api.py:38, which WN2-C3 does not name.
  - tests/test_public_runtime.py:52 pins a ten-name tuple without `EvaluationSession`, so it is already out of step with current bytes. I did not check whether it runs against an older wheel.
  - The stable-API count is stated as "seven-function" in cli.md:108, tour.md:29 and runtimes/decision.md:93, while python-api.md:8-9 lists eight functions. Adding a ninth makes this worse, and standing rule 5 says one home must yield in the phase. Note that python-api.md's eight functions match the issue's "eighth function", so the plan's "older pin" explanation (plan :41-43) is only half right: it counts `__all__` names (12), while the docs count functions (9).
  - docs/compatibility.md:7 requires release notes for contract changes, and only WN3 schedules a release note, after WN2 has already shipped the surface.
- Fix: list every pin site by path:line in WN2-C3. Make one count sentence the home, cite it from the others and fix them in WN2. Say which unit (`__all__` names or functions) the plan uses. Move the release-note row into WN2, or say why WN3 is soon enough.

**R3-F6 -- hardening, medium confidence.** Where: plan WN-D5.
- What is wrong: exit 2 merges `derived` ("nothing to explain", a good outcome for the host) with `unsupported` (a refusal). Exit 0 here means the opposite of witness exit 0 (proved). A host loop that branches on exit codes, which is the issue's use case, cannot tell a derived claim from an unsupported rule without parsing `status`. The readings table does not cost this.
- Fix: add a reading (c) that separates derived from unsupported (for example, derived = 0 with status `derived`, blocked = 0 with status `blocked`, unsupported = 2), with each reading's exit-code cost. Extend the cli.md exit paragraph with a why-not sentence, as is already done for witness.

**R3-F7 -- hardening, high confidence.** Where: spec §11; plan §8.
- What is wrong: review-convergence.md ("Prefer the executable instrument") makes corpus-first the default for serialized formats, exit-code contracts and validation predicates, and says choosing prose "requires stating why". WN2 ships all three. WN1's step and blocker records become the payload. Spec §11 picks prose without giving a reason, and the plan does not say what instrument WN2 will use. induction-skill recorded this as D15 with an argument.
- Fix: add a decision row for the approval instrument in spec §7 with the reason for prose in WN1. In plan §4/§8, state that WN2 defaults to corpus-first: golden payloads, expected exits and redacted views committed red before code.

**R3-F8 -- completeness, high confidence.** Where: spec §1 vs §7; plan §4 WN1 line 232.
- What is wrong: the lists of decisions WN1 is blocked on do not agree. Spec §1 says it is blocked on WN-D2, D3, D4, D6, D7 and D9, but the spec §7 decision table has no rows for WN-D4 or WN-D7. Plan line 232 lists "D2..D4, D6, D7", which leaves out D9. The spec-note contract requires every ruling the owner must make to appear in §7.
- Fix: put the same set in all three places, and add the D4 and D7 rows, or drop them from §1 if the kernel does not depend on them (it returns raw values either way).

**R3-F9 -- completeness, high confidence.** Where: plan §8 and the WN-D8 row; README line 21.
- What is wrong: the ruling quoted covers plan and close review only. §8 states "one independent local diff reader" per phase as protocol, while §10 marks it "(proposed)". review-and-record.md step 4 names a different default instrument. In transition-check-performance (TP-D7) this was an owner ruling. The ruling also has a date but no digest; start-milestone asks for dates, scope and hashes.
- Fix: mark the per-phase reader as proposed in §8 too. Record the r1 digests (which do match the snapshots) next to the WN-D8 ruling.

**R3-F10 -- completeness, high confidence.** Where: plan completion predicates 1 and 5; spec T13, T17.
- What is wrong:
  - T13's "fixed wall bound" has no value. TP1's D5 chose a counter bound instead of wall time to avoid flaky tests.
  - "Generated corpus" has no size and no seeds.
  - T17, "diff reviewer confirms", cannot fail. standing-rules.md says a check that cannot fail is not a test case. transition-check-performance used an allowed-values check for its anonymity rule.
- Fix: give T13 a counter bound (charged bindings ≤ `joins`) plus a generous wall cap. State the corpus seeds and minimum case counts. Replace T17 with a mechanical denylist test over new files (the names come from owner configuration, not the plan text), and keep the review lens as an addition.

Unverified: the claim that GR-T5 is "not filed in this repository" (O15). I did not check it, to stay within the one-issue network budget.
