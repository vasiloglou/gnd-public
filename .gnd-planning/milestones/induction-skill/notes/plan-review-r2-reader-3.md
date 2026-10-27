# Round 2, reader 3 -- protocol, authority, compatibility and privacy

Retained text of the reader's returned report. Local edits: headings demoted one
level.

**Digest check: both match.**
- The plan snapshot hashes to `7329cbd2…3dc3df` and the spec snapshot to `f81590b0…41f938`. Both are byte-identical to their working copies in `notes/`. Both were committed in `0c777e3`.
- `git diff --stat 077f46e 45c8603 -- src tests tools docs AGENTS.md` is empty, which confirms spec §2's claim that the r1 measurements still hold.

**Verdict: approve-with-fixes**

All 12 of my round-1 findings were addressed: 11 are resolved and R3-F3 is partly resolved. No new finding is blocking. The most important new one is R3-N1: two skill-count literals that move are missing from the pin table, which claims to list every one.

The authority claims are sound:
- The owner's acceptance is quoted and dated (plan 13-16).
- D1..D12 and D14..D16 are still marked as proposed (448-449).
- The statements made only in conversation are labelled that way (88, 129-132, 143, 150, 438).
- No plan approval is claimed.
- No downstream names, absolute paths or email addresses appear in either subject (checked with grep).

## Round-1 status

| Finding | Status | Evidence (snapshot lines) |
|---|---|---|
| R3-F1, the `ilp-learners` sibling | resolved | Plan re-baselined on `45c8603` (6-7). `ilp-learners` r3 and IL1 r3 harvested (102-103); r3 is approved by `ilp-learners/001-plan-gate.md`. IS-O18 (155). Prerequisites and ordering (243-248); D17 (443); risk row (364). |
| R3-F2, census pin vs. the IK-close edit | resolved | D8 now reads `skill-census.md` with `git show` at one 40-hex commit (plan 434; spec 220). New issue, see N3. |
| R3-F3, verification selection | **partial** | A ledger now exists (spec 272-281). The deselected `test_public_distribution_runtime.py` is gone from gate line 1 (286). The `-m distribution` run is an owner-selected lane (293-297). But the ledger lacks fields the protocol requires (N2). |
| R3-F4, frozen-skill test that cannot fail | resolved | Spec T13 (260) diffs against the IS1 base, with a seeded control; plan IS-R9 (91) and IS1-C9 (278-279). Minor: the closed test that compares frozen skills is `test_t16`, not `test_t25`. |
| R3-F5, recording authority | resolved | Plan IS2-C1 (286-296): a new IS-scoped gate record, Claude Code's own login, declared turns, a run bound and a cost ceiling. Also 237, 369 and D11 (437). Residual in N5. |
| R3-F6, actor and git identity | resolved | IS-R5 (87); inputs (179); IS2-C1 (297-299); spec 117 and 137; T14 (261). |
| R3-F7, replay pins | resolved | IS-O20 (157) and IS2-C2 (304-306). The `test_ik6_walk.py:74` rglob does cover the refunds recording home. |
| R3-F8, T9 red-first claim | resolved | Two controls (spec 87-94; plan 57-59). Small inconsistencies remain (N8). |
| R3-F9, two byte sets called "r1" | resolved | The revision is labelled r2 (plan 3). r1 is bound by digest in the disposition and its `manifest.json` (18-19). The snapshots are committed (`db374d7`, `0c777e3`). |
| R3-F10, undated owner statements | resolved | Plan 88, 129-132, 143, 150; D12 dated 2026-10-26 (438). The `(o)` tag is limited to dated rulings (12). |
| R3-F11, plan rules not bound in the spec | resolved | Spec §4 binds IS-R1..IS-R11 by name (69-83). |
| R3-F12, stale wording and citation | resolved | Citation fixed (43-46). The "Once one is chosen" wording is gone. The round budget is in the plan's own bytes (390-393). |

## New findings

**R3-N1** (hardening, high confidence; pre-existing, with r2's new "every literal" claim): **two skill-count literals that move are missing from §6.3.**
- *Where:* spec 204 ("Every literal that moves") and 280.
- *Evidence:*
  - `tests/test_public_distribution.py:315` asserts `len(paths) == 16` over the wheel's `SKILL.md` files.
  - `tests/test_release_acceptance.py:77` asserts `... endswith('/SKILL.md') ... == 16`.
  - Both files are in the distribution lane. Both become 17 once `gnd-induce` ships.
  - The ledger marks `test_public_distribution.py` as "inherit … not IS1's" (280). After IS1 that file gains a failure that is IS1's, hidden behind the 6 failures it already has at baseline.
- *Fix:* add both literals to §6.3. Re-dispose `test_public_distribution.py` as "red at baseline; IS1 moves :315", or move the edit into D20's lane.

**R3-N2** (hardening, medium; self-inflicted): **the ledger does not have the shape `verification-selection.md:39-50` requires.**
- *Where:* spec 274-281.
- *Evidence:*
  - The required fields Obligation, Command or evidence, and Justification are missing.
  - The `inherit` row has no path, SHA-256, source identity, command or result, and its input boundary is "—".
  - The `cadence` row names no CI job or milestone-close lane, although the reference requires one.
- *Fix:* add the three missing columns. Turn the "inherit" row into an explicit "red at baseline, not claimed" row that cites evidence. Name the lane that the cadence row belongs to.

**R3-N3** (hardening, medium; self-inflicted): **D8 makes IS1 wait on #50 and #51, but the prerequisites and D17 say IS1 may land at any time.**
- *Where:* plan D8 (434, "after #50 and #51 land"); prerequisites (243-245, "IS1: plan approval"); D17 (443); spec §1 (5-8).
- *Evidence:*
  - `gh pr view 51` shows that #51 touches only `induced-knowledge/016-*` and evidence files. It changes neither the census nor a packaged skill, so waiting for it adds nothing to the pin.
  - "The last IK-scoped change" has no fixed end. #52 (IKE-Q3) is open and also edits IK records, and more IK follow-ups may come.
- *Fix:* define the D8 commit by a checkable criterion: the IS1 base commit, provided it contains #50's census edit. Drop the #51 dependency, or list the D8 wait as an IS1 prerequisite in both the plan and the spec.

**R3-N4** (hardening, low; self-inflicted): **the spec's distribution lane goes beyond what the owner accepted for D20.**
- *Where:* spec 279, 296 and §5 control 1 (90-91, which includes T16).
- *Evidence:*
  - The accepted D20 text (plan 446) names only `test_public_built_inventory.py`, run once at the gate.
  - The spec's lane also runs `test_public_distribution_runtime.py`. That test runs `uv build`, then `uv pip install` of the wheel, which may resolve from the network (lines 39 and 53-54).
  - Control 1 needs a second distribution run on the pre-IS1 tree.
- *Fix:* either keep the lane to the accepted text, or record the addition and the extra red-control run as a D20 amendment for the owner to rule on.

**R3-N5** (hardening, low; self-inflicted): **the gate-record parameter for the recorder could weaken its scope check.**
- *Where:* plan IS2-C1 (288-289, "replacing the hardcoded PL18 check").
- *Evidence:*
  - `record_skill_sessions.py:233-234` checks for one named gate.
  - A bare file parameter would accept any file passed to it.
  - `--runs` is hard-coded to 1..2 (:235-236), described there as "the gate's bound", which may not match the run bound D11 declares.
- *Fix:* say that the recorder checks the gate record's scope string against the example being recorded, keeps the PL18 check for the course example, and enforces the run bound declared in the gate record.

**R3-N6** (hardening, low; self-inflicted): **the risk row's claim about IL6's census edit has no support.**
- *Where:* plan 364.
- *Evidence:*
  - The `ilp-learners` plan (109, 545, 665) says "the skill census is extended, with a check per row" without naming which census.
  - The only skill census in the repository is `induced-knowledge/skill-census.md`. D8 freezes the test that reads it at a pinned commit, so IL6 rows added later would have no test.
- *Fix:* record this as a coordination note for IL6's gate (IL6 owns its own census test), or ask which census IL6 means.

**R3-N7** (completeness, high; self-inflicted): **the milestone README is stale.**
- *Where:* `induction-skill/README.md`, unchanged since `db374d7`.
- *Evidence:* it still says r1, baseline `077f46e`, and "Not reviewed". It lists D9 as pending and gives "owner accepts… D17..D20" as the next action. This contradicts plan r2 (3-9, 435, 443-451).
- *Fix:* update the status, baseline, readiness, pending decisions and next action.

**R3-N8** (completeness, low; self-inflicted): **the definitions of the two red controls do not match their uses.**
- *Where:* spec 92-94 vs. T17 (264) and T16 (263).
- *Evidence:*
  - Control 2 is defined as the *unchanged* T5 and T9, but T17 is a new test that is also marked "control 2 red".
  - T16 is in control 1 but runs only in the distribution lane.
- *Fix:* add T17 to control 2 as a new-test case, and note that T16's red evidence comes from the owner-selected lane.

**R3-N9** (completeness, low; self-inflicted): **the accepted rulings are not tied to fixed bytes.**
- *Where:* plan 13-16 and D17-D20 (443-446).
- *Evidence:*
  - start-milestone:106-108 asks for dates, scope and hashes for actual approvals.
  - The acceptance is quoted and dated, but the disposition it accepts is not identified by commit or digest. It is committed at `db374d7`, SHA-256 `d4a7e8b0…9e61`, unchanged since.
- *Fix:* cite the disposition's commit or digest next to the quote.

**R3-N10** (completeness, low; pre-existing): **one open sibling PR is not named.**
- *Where:* plan 104-108 and IS-O16 (153).
- *Evidence:* #52, `fix(IKE-Q3)`, edits `gnd discover` (`commands/discover.py`, the cli-help and cli-exit goldens) and `docs/reference/discover.md`. That page is one of IS-R3's one-home pages, and T7 reads `gnd discover`'s help output. #52 was opened at about the same time r2 was committed.
- *Fix:* name #52 in §1 and IS-O16, and rebase IS1 after it if it merges first.

**Tally:** 10 new findings, 0 blocking, 6 hardening, 4 completeness. 8 of the 10 are self-inflicted (0.8).

Scratch writes: none. Repository writes: none.
