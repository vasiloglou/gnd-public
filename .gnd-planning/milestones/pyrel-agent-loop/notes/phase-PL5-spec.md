# Phase PL5 spec: the pages

## 1. Status

owner-decided (2026-10-14): delegated approval under
[`001-plan-gate.md`](../001-plan-gate.md). Implementable; PL1–PL4 landed.

## 2. Provenance

Plan r1 §4 PL5 row, §5, §9 PL5 row, PL-R1, PL-R3, PL-R4, PL-R5, PL-R7. Content
design from the planning session (section plan per chapter; agents-section
edits). A2 D4 order and D7 gate carried over. No review round yet.

## 3. Obligations

| Source | Obligation | Discharge |
|---|---|---|
| Owner review: pedagogy, how rules are written, rules in PyRel | step 3 "The rules, three ways" per chapter: quote → verbalizer → ORM → hand-written PyRel → run → rule table → predict-then-run | §6.1 |
| Owner review: show the LLM, what it outputs, how GND checks it, what it feeds back | step 5: 5a recorded session (task, SAID/RAN excerpt printed from SHA-256-checked bytes, candidate, feedback), 5b stand-in loop with the feedback printed, 5c same candidates through the app | §6.1 |
| Owner review: show the skills and reasoning | four `text`-fence prompts beside their checkpoints, skill steps paraphrased from each `SKILL.md`, a "Skills used" table, two reasoning callouts | §6.1 |
| Completion predicates 1, 2, 5 | commands `python <project>/app.py ...`; one copy; skills in place | §6.1 |
| PL-R3 | excerpts printed by runnable blocks | 5a blocks |
| PL-R4 | equivalents labelled | step 3 prose |
| PL-R5 | pinned witnesses shown | steps 3, 5, 6, 7 |
| PL-R7 | prose gate on every touched page | `tests/test_pyrel_learning_path.py` |
| A2 D4, D7 | order and gate | kept; step 5 renamed "An agent in the loop" |
| Plan §5 | agents pages cross-reference without duplicating | §6.2 |

## 4. Standing rules, bound

1. Totality: page blocks read shipped files only. 2. Bounds: n/a. 3.
Validation order: n/a. 4. One walk: the excerpt test checks every marked block
with one rule. 5. One home: the loop is explained in the chapters; agents pages
link. 6. Measurement: both lanes, strict build, prose tests.

## 5. Goal

Both tutorial groups exit 0 in both lanes (BookRec 71 blocks, 10 PyRel;
Expense 57 blocks, 11 PyRel); `docs/agents` groups exit 0; prose tests exit 0;
`zensical build --strict` and `check_docs` exit 0.

## 6. Design

### 6.1 Chapters

`docs/bookrec/07-native.md`, `docs/expense/04-native.md`, sections 1–8 plus
Troubleshooting, Next steps and the two `??? note` includes (`native_query`
and `rules_in_pyrel` twins). Illustrative python excerpts in step 3 carry
`<!-- gnd-excerpt source=FILE -->`; the test verifies them line by line
against the shipped file. Recorded excerpts are printed by a block that checks
the SHA-256 first; the admonition says "recorded, not re-run".

### 6.2 Overview and agents pages

`docs/pyrel-apps.md`: cleaner setup, "How a rule becomes a PyRel check",
"Where the coding assistant fits". `docs/agents/index.md`: "Follow the skills
through one application" table. `docs/agents/dev-session.md`: one paragraph on
the facts loop. `docs/agents/recorded-sessions.md`: "BookRec and Expense"
section with a digest-check-and-replay block. One pointer line each in
`model-from-text.md`, `codegen-conformance.md`, `evolve.md`. Nav titles only in
`zensical.toml`.

## 7. Decisions

| # | Question | Ruling |
|---|---|---|
| D1 | BookRec conformance block | dropped: the raw example is not a generated project; conformance is demonstrated on Expense, and BookRec points to its chapter 3 |
| D2 | Recorded refusal absent | pages say the assistant was never refused and show the refusal with the stand-in |

## 8. Tests

`tests/test_pyrel_learning_path.py` (marker-based excerpt rule),
`tests/test_tutorial_output_blocks.py`, `tests/test_pyrel_tutorial_experience.py`,
`tests/test_documentation_tutorials.py`, `tests/test_development_scaffold.py`,
runner groups `bookrec`, `expense`, `agent-recorded`, `agent-session`,
`agent-model`, both lanes where applicable; strict build; `check_docs`.

## 9. Out of scope

Earlier chapters; graphics changes; new nav pages.

## 10. Size

Three pages rewritten (~1,100 lines), five agents pages touched.

## 11. Approval instrument

This prose plus the gates in §8.

## Owner gate

Delegated approval (auto=true), 2026-10-14. No spec panel.

## Resume amendment and findings, 2026-10-14

Resumed in Codex from Claude session fd814110-b392-4c16-8294-2db75ff438c9,
base 1495ba2. Existing milestone delegation in 001 remains the phase-gate
instrument; the user requested continuation of this same work. Changes below
preserve the approved rules and candidate meanings.

- F1 (blocking, PL-R3): task blocks and candidate/feedback blocks printed bytes
  without a hash check. Eight tamper controls cover task, transcript, candidate
  and feedback in both chapters. Observe red before repair. Session artifacts
  use the retained manifest; tasks, absent from that historical manifest, use
  the exact committed task SHA-256 pinned in the page. Retained recordings and
  their manifests remain unchanged.
- F2 (blocking, honesty): the BookRec coverage floor counts all recommendation
  facts, not recommendations for Ada. Correct the printed claim and explain
  that these contracts do not check task-specific coverage or preserve seed
  facts. The app's later check is a separate boundary, and neither check
  establishes real-world truth or approval authority.
- F3 (blocking, completion predicate 4): Expense must run its accepted session
  candidate through the PyRel app. Use that retained candidate as the report's
  input instead of only reporting on a separately reconstructed snapshot.
- F4 (hardening, pedagogy): printed messages were cut mid-sentence. Print whole
  assistant messages; visibly mark shortened commands with an ellipsis.

Delegated amendment approval (auto=true), 2026-10-14, under 001; no new runtime
acceptance predicate, rule meaning, paid recording or certification is selected.
Focused gates: tests/test_pyrel_learning_path.py (including the tamper controls),
tests/test_tutorial_output_blocks.py, tests/test_pyrel_tutorial_experience.py,
tests/test_documentation_tutorials.py, tests/test_development_scaffold.py;
both chapter groups in both lanes; agent-recorded, agent-session, agent-model;
strict build and local link checker. PL6 acceptance must bind the final page bytes.
The prior fresh-install receipt describes the pre-repair pages only.
