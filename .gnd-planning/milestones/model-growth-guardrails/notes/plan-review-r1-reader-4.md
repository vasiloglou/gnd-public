# Reader 4 -- test design, falsifiability

Retained text of the reader's returned report, lightly edited for layout.
One review round covered both milestones. Scratch paths read `<scratch>`.

**Digest check:** all four snapshots match their stated SHA-256. HEAD
`1446f909`.

**Verdict:** request-changes. Five blocking: two oracles that cannot pass or
pass on a wrong implementation (F1, F9), three declared branches no case can
fail (F2, F5, F6).

**Scope.** Every completion predicate, phase criterion and the MG1 and CT1
test tables walked against the declared branch tables; anchors confirmed at
`1446f90`. Probes: `<scratch>/plan-review/reader4/sweep.py`,
`probe_branches.py`.

**What holds.** MG1 sweep reproduced (61, 116, 18, 0 exceptions). CT1 T3
discriminates "every" from "any"; T4 first- from last-match; T2's v1 row the
v1 from the v2 rule. T6's list matches the five sidecar test files; only 3
fixture sidecars exist, so T7 is feasible. MG5-C4 has discriminators: 112
corpus models carry `source.mode`, 16 one-shot models carry `confirmed` or
`user-supplied`. CT4-C2 tests threshold edges; CT2-C5 and MG1 T11 are
counter-based.

**Findings.**

**R4-F1 (blocking) -- MG1 T3, Goal.** The line continues after the rule
(`model_verbalization.py:569-573`, plus `depends_on`/redaction sentences), so
"ending at the line's end" fails on every structured rule, while "is a
substring" cannot fail on a truncated rendering. Reproduced: all 98 structured
rules have content after the rule. Repair: assert `"This fact type is
derived: " + text` is followed by a known continuation, or compare with
`_derivation_cnl(rule, model)` with the collector `None`; add a truncation
mutation control.

**R4-F2 (blocking) -- MG1 branch table.** Undeclared: `_guarded_atom` non-dict
atom (`:165-167`); non-dict `aggregate` dropped. Reproduced on bookrec with a
no-op control: a string atom in `body`, `aggregate: "sum"` and a dict term in
`where` are each refused by the model JSON schema. Repair: list every
fallback; T4b as a falsifiable "refused by load" test; settle MG1-Q1 in the
spec.

**R4-F3 (hardening) -- MG1 D6.** No test row; outcome depends on what is
found. Repair: a T row with one pinned expected outcome decided before the
gate.

**R4-F4 (hardening) -- MG1 T2, T5, T11.** (a) T2's counts disagree with the
spec's own sweep; "floor recorded" is not asserted. (b) T5 lacks a positive
subset, out-of-order ids, `[]`, duplicate ids, and an existing-but-invalid
model. (c) T11 counting renderer calls cannot see a per-rule full render or
index rebuild; count fact-type visits or index constructions. (d) The Goal
says two pins; T6 names four plus release notes.

**R4-F5 (blocking) -- MG §2.2, MG2-C1.** `RoleLocator` ADD on an existing fact
type (gated at `service.py:634-637`) has no refused row; `ModelIdentityLocator`
MODIFY and the `operations` collection are unclassified; one RENAME case can
cover four locator kinds; order against the operations gate (18 vs 3) is
unpinned. Repair: an operation-kind × locator-kind matrix, one case per cell;
a two-fault order case.

**R4-F6 (blocking) -- MG2-C3.** Under MG-D2 (a) a removed issue fails at the
digest check even with no re-run wired; deleting `policy` sends apply down the
"no policy" path. Unproved (from §2.2 and `service.py:1553-1577`). Repair: a
digest-consistent preview where the before-model or populated set makes the
re-run disagree; a policy-stripped preview case with a stated exit.
**Owner:** whether `apply --policy additive` forces the policy.

**R4-F7 (hardening) -- MG-D3 vs MG-D5.** `proposed`→`confirmed` is both a D3
strengthening and a D5 provenance edit. Fixtures: description-only (admitted)
vs description plus `object_type` (refused); weakening or rationale-only on a
populated type (admitted); one per D3 item; one per D4 populated source plus
an unpopulated control. **Owner:** classify the confirm transition.

**R4-F8 (hardening) -- MG3-C4, CT2-C5.** Counting signature reads or row
visits misses 500 × 5,000 comparisons or a quadratic dedupe. Count
comparisons or bucket probes and assert ≤ k·n. Pin the (A,A,B) vs (A,B,B)
multiset discriminator; say whether two identical ADDs match each other.

**R4-F9 (blocking) -- CT1 T11.** JSON Schema cannot express per-key
uniqueness or `start < end`; on T2's "same fact role twice in v1" the schema
accepts and the parser refuses. Repair: list the parser-only rules and assert
disagreement on exactly those.

**R4-F10 (hardening) -- CT1 T3, T8.** (a) Use two bad anchors on one role.
(b) T8's index count is trivially one `lexical_ranges` call; use 1,000 rows ×
10 anchors and count key lookups. (c) T5 puts the maximum-occurrence anchor
first.

**R4-F11 (hardening) -- CT1 D2.** The v2 key excludes `excerpt_sha256`,
`block_id`, `unit_id`, but the plan says "exact duplicates". Add same span
different occurrence (accepted) and same identity different `excerpt_sha256`
(state the outcome).

**R4-F12 (blocking) -- CT plan.** §2.2 and CT2-C4 test a refusal CT-D4
rejects. Repair after the **Owner** rules CT-D4.

**R4-F13 (hardening) -- MG5.** D-03 is a warning (`_validation.py:1384-1420`)
and covers llm-inferred and common-sense only; "stay deontic" has no case.
Add an alethic-proposed case with a stated exit; a passing re-hash case in
C3; an out-of-range span case; the C2 refusal matrix (element kind × source ×
missing/undeclared span; missing `reviewer`; missing `documents`).
**Owner:** escalate the warning to an error in unattended mode?

**R4-F14 (completeness) -- MG4-C1, O12.** `_artifact_index_issue` verifies
only required artifacts (`extract/service.py:67-82`), so nothing checks the
guideline digest. Name a verifier with a tamper case, or say "recorded".
MG4-C2's injection must cover value constraints and every kind.

**R4-F15 (completeness) -- CT4.** (a) A group reaching the threshold by rows
but not distinct entities. (b) An undeclared generic-shaped type with high
support yields nothing. (c) A canary-value scan over the proposal bytes. (d)
Under MG-D7, an existing Entity→string binary may suppress every string
proposal; add one suppressed, one not. **Owner.**

**R4-F16 (hardening) -- parity claims.** MG2-C4, MG4-C1, MG5-C4, MG1 T7 and
CT3-C1 rest on suites, not a recorded before/after. Use CT1 T7's pattern over
previews, bundles, validation results and verbalizations. State CT3-C2's
exit.
