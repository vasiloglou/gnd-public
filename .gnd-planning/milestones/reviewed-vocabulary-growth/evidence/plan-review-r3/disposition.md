# Plan review r3: no panel result

Reviewed bytes: `notes/reviewed-vocabulary-growth-plan.md` r3, sha256
`96acc9bf0ad324802f882b863fe75e5c6910bede25f3ac86fa68032f8ae1f7ff`, commit
`28f94c58`. Instrument: GND panel light, a new run the owner asked for on
2026-11-23 ("try again") after round 2 ended below quorum. `reviewer_effort`
high, bound per run for Claude and Codex only. The tree was clean at
`28f94c58` apart from the request file; the panel implementation was equal
to HEAD. The reviewed artifact digest was equal before and after.

    uv run python tools/run_gnd_review_panel.py --light .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/plan-review-r3/review-request.json --out panel-run --effort high --reviewer-timeout 600 --overall-timeout 900
    exit 16, run_sha256 e0680a1fad9b54ae8ba6e5f19a18096811a08f73055d6c9b52e52407d811f09b

**Exit 16: six seats were attempted and two succeeded. Quorum is three. No
panel result exists for r3.** There is no synthesis and no `PANEL-REVIEW.md`,
and `gnd review finalize` was not run. The run was not repeated.

| Seat | Status | Reason retained in the envelope |
|---|---|---|
| claude | `success` | `revise`, 7 concerns, all anchored, response complete, 252 s |
| codex | `success` | `revise`, 1 concern, anchored, response complete, 102 s |
| qwen | `timeout` | "reviewer invocation exceeded its shared deadline", 600 s |
| gemini | `malformed` | "output contains no JSON object", after 15 s |
| kimi | `timeout` | the same deadline, 599 s. It had written 264,633 bytes of stream output and no final response |
| glm | `timeout` | the same deadline, 600 s, with nothing on stdout |

Three seats ran into the 600-second reviewer timeout. Over the three runs
the slow seats took: kimi 244 s, 584 s, then over 600 s; glm 535 s, not
invoked, then over 600 s; qwen never returned a response; gemini returned no
JSON each time. The Claude probe failure of round 2 did not recur: before
this run the CLI's help was run eight times in its own process group and
left nothing behind.

This folder keeps the request, `run.json` and the two `response.json` files,
copied unedited; none names a local path. The rest of `panel-run/` is
outside history; its digest is `run_sha256` above.

## The two reviews that returned

These are two individual reviews. They are not agreed concerns and not a
panel finding. Claude's summary says "Plan r3 has no blocking concern" and
lists what it checked and found to hold: the cited lines of H13, H27 and
H31–H35, that VG3-C9 is testable, that the first-document rule names every
top-level property of the schema, that VG3-C2 and VG3-C3 cover U2–U8, and
that every lane file exists. That is one seat's statement.

Each concern was checked against the code at `28f94c58`. The record was
written with no repair applied; the owner then asked for one ("Repair to
r4"), and what r4 carries is under "Repair" below.

| Reviewer | Concern | Reproduced | Class | What a repair would be |
|---|---|---|---|---|
| codex | d3b-completion-predicates | yes, by reading: the goal's VG3 and VG5 predicates require the include; §3's D3 (b) fallback keeps today's refusal, so it cannot meet them | completeness. It bites only if the owner rules D3 (b) | §3 says a D3 (b) ruling needs a plan amendment that replaces the VG3 and VG5 predicates and criteria before those phases run |
| claude | d14-malformed-included-span-counted-unchecked | yes: `_span_walk` counts every visited span and re-hashes it only when `_span_issue` returns nothing (`_unattended.py:284-293`). With U7 exempt, an included span over a declared document with `start >= end` leaves only `unattended:spans-unchecked`, whose message tells the user to supply documents they already supplied | hardening | D14 says what a malformed included span over a declared document gets: its own diagnostic, at the include's address. One case in VG3-C5 |
| claude | d5-span-walk-diagnostics-not-remapped | yes: `remap_issues` is called only in `_model_warnings` (`model/__init__.py:302`, `:305`). The span walk's issues are built in `commands/checking.py:84-85` and go to `_run_validate_with_documents` (`api.py:608`) as they are, so a re-hash diagnostic on an included span has a composed address and no `includes[ID]:` prefix | hardening. D5 promises the prefix on every diagnostic | the span walk's issues pass through `remap_issues`; one criterion, an included span with a wrong excerpt digest exits 3 under `includes[ID]:` |
| claude | d5-json-carrier-vs-frozen-validate-payload | yes: `build_validate_payload`'s docstring says the payload stays on the frozen variants (`payloads.py:702-706`), and it carries issues and warnings only. The plan leaves the JSON form of the attribution to the spec and also says no schema version changes | hardening: a decision the plan should make | the plan picks the carrier: text output only, with JSON unchanged, or warning entries, or a payload field. §5 and VG3-C10 say the same |
| claude | d4-rule-scope-without-includes | yes, by reading: the rule as written admits an unattended model with no includes, no documents and no elements; today U1 refuses it (`_unattended.py:84-86`) | hardening | D4 says the rule applies only to a root that declares `includes`; one VG4-C3 case holds a model without includes to today's U1 |
| claude | d4-rule-on-file-vs-composed-doc | yes: `_rule_unattended` reads the composed document (plan H16), in which `_merge` has already added the included object types, fact types, constraints and notes (`_includes.py:136-138`). "Absent or empty" is false there for every include root. The origin table has no entry for `rejected_proposals` or `reference_populations` (`_includes.py:119-127`) | hardening: §2 names two tests, "on the file" and "the origin test", and they are not the same | §2 names one: the rule reads the root's own document before the merge. The two sections with no origin entry are the root's by construction, since an include cannot declare them (R0.5) |
| claude | d13-include-carried-content-unstated | yes: `_merge` copies each included fact type whole (`_includes.py:138`), its `sample_population` rows with it; U6 is exempt for them and D5 does not count them | completeness | §6's limit and "Unattended source" name sample rows; D5 may add a count |
| claude | s8-stale-round-budget | yes: §8 still says "one round is planned, a second only if the first blocks" beside a bullet that says the budget was two | completeness | the r1 sentence is replaced |

## The convergence numbers

Computed over two seats, not over a panel.

- Self-inflicted: of 8 concerns, 4 quote only text that r2 or r3 created
  (the two D4 concerns, the malformed-span concern, the sample-row concern);
  2 quote r1 text together with text a repair added (the two D5 concerns);
  2 quote r1 text alone (the D3 (b) fallback, the §8 sentence). Counting the
  mixed ones as half, that is 5 of 8, over the stop rule's half.
- Same-seat trend: claude 10 in round 1, 7 here; codex 4, 3, then 1.
- Severity: nothing above medium. One concern is called blocking by its
  reviewer (codex), and it applies only under a ruling the plan does not
  propose.

Three instrument runs have been made: one with a panel result, two below
quorum. Whether the plan gate proceeds, the points above are repaired, or
another run is made with a longer reviewer timeout, is the owner's decision.

## Repair

Plan r4, sha256
`72710267b2dcdacc82b46014037ba0df74c345439e96f62b4ba5db52617f7ec7`, applies
all eight rows, tagged `(s3)` at their site. No review has read r4. Where r4
differs from the last column:

- **d3b-completion-predicates.** As proposed. The goal, §3 and the D3 row
  say that a D3 (b) ruling comes with a plan amendment, approved before VG3
  starts, that replaces the VG3, VG4 and VG5 predicates and the VG3 and VG4
  criteria. The plan does not write the (b) criteria, because it proposes
  (a).
- **d14-malformed-included-span-counted-unchecked.** No new diagnostic. An
  included span that names a root-declared document keeps U7's shape check,
  as today, so a malformed one is refused at load under `includes[ID]:` and
  never reaches the walk. An included span that names any other document is
  read by no rule. D3 now says "exempt from U2–U6, from U7 as D14 rules".
  VG3-C5 gains the case. New row H39 holds the walk's behaviour.
- **d5-span-walk-diagnostics-not-remapped.** As proposed: the span walk's
  issues pass through `remap_issues` with the loaded model's origins. New
  row H37 and criterion VG3-C11. §5 now says the address of such an issue
  changes on a root 0.4.0 already admits.
- **d5-json-carrier-vs-frozen-validate-payload.** The plan proposes text
  output only, with the JSON payload unchanged, and lists the two
  alternatives in D5: a `warnings` entry per include, or a new payload
  field. New row H38. §5 says no report variant changes; VG3-C6 and VG3-C10
  say the JSON payload has no entry and is byte-identical. The owner rules
  it with D5.
- **d4-rule-scope-without-includes.** As proposed: the rule applies only to
  a root that declares at least one include. VG4-C3 gains the case.
- **d4-rule-on-file-vs-composed-doc.** As proposed: the test is read on the
  root's own document before the merge, and §2 says why that agrees with
  VG3's origin test. `src/gnd/model/__init__.py` joins VG4's homes; how the
  document reaches U1 is a VG4 spec question.
- **d13-include-carried-content-unstated.** §6 names sample rows in the
  limit, and D5's line counts them.
- **s8-stale-round-budget.** The sentence is replaced, and §8 gains a bullet
  for this run and the repair.

The VG1 spec changes two sentences to name plan r4; its content is the r2
content, sha256 `f96702b49b2d6c039a1965acdc73991fc1ee117bd5703e8db10b441ccba3c5d0`.
