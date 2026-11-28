**The files changed while I was reviewing.** All eleven hashes matched the brief when I started. Partway through, another session edited the worktree:

| File | Now |
|---|---|
| `src/gnd/evolve/consolidation.py` | `5723ead4…` |
| `tests/test_consolidation_loop.py` | `426641ef…` |
| `src/gnd/skills/gnd-consolidate/SKILL.md` | `0ea0bc20…` |
| `tests/support/pyrel_application_successors.py` | now modified |
| `.gnd-planning/…/evidence/CG3/` | new |

My file reads came before the change. For the probes I rebuilt the briefed `consolidation.py` in scratch by removing the two added blocks. The rebuilt copy hashes to exactly the briefed `62e44beb…`, and every probe ran against it. Line numbers below refer to the briefed bytes. The live copy already fixes F1 and F2; F3–F6 are still in it.

## 1. Findings

**F1. A merge can delete fact types outside the group** (`consolidation.py:117-121`)
- **What's wrong:** a removed fact type is refused only if it has sample rows and no move. Any unsampled fact type, whatever group it belongs to, can be deleted inside a "merge" decision.
- **What you'd see:** the model had `listed` and `archived` (sampled duplicates) plus an unrelated `retired` fact type with its own `provenance.spans`. A fact-group merge proposal that also deleted `retired` returned `completed` and published. The facts left were `['archived']`, so `retired` and its role reference and spans are gone.
- **Live tree:** adds an "an unrelated fact was removed" check.

**F2. An object merge can point a removed member's roles at a non-member** (`consolidation.py:89-92`)
- **What's wrong:** nothing requires roles played by the removed object to move to the surviving member.
- **What you'd see:** objects `custcode` and `custcodes` (near-name group) plus an unrelated `zipcode`. A merge deleted `custcodes` and repointed `f1.c` to `zipcode`. It returned `completed`, and `f1.c` now plays `zipcode`.
- **Live tree:** adds a "must reference a surviving group member" check.

**F3. Fact-level source spans of removed members are lost** (`consolidation.py:53-62, 130-133`)
- **What's wrong:** the transfer check compares sample rows and their `sample_spans` only. Neither `provenance.spans` on the removed fact type nor spans on a removed object type need to survive anywhere.
- **What you'd see:** `listed` had an extra fact-level span ("listed only fact-level witness"). After a normal merge into `archived` the result was `completed`, and that span exists nowhere in the model. The committed test passes only because it asserts on `sample_spans`.
- **Live tree:** still present.

**F4. Duplicate `sample_spans` entries for one row collapse to one** (`consolidation.py:54-57`)
- **What's wrong:** the dict comprehension keeps only the last span per row. U6, which rejects repeated rows, applies only to `source.mode: unattended`, so a fixture or prose model can legally give one row two spans.
- **What you'd see:** `listed` row 0 had spans A and B. The merge moved only B. It returned `completed`, and span A appears nowhere in the model.
- **Fix direction:** build a multiset of the spans for each row, not a dict keyed by row.

**F5. An interrupted decision can never be recovered or replaced** (`consolidation.py:195-196, 269-273`)
- **What's wrong:** if the model changes between the journal's pending write and the apply, there is no public way out.
- **What you'd see:**
  - Resuming without a decision fails with `stale model CAS: model changed after preview`.
  - Submitting any new decision fails with `recover the pending decision before submitting another`.
  - The workflow is wedged until someone edits `.gnd-consolidation/…/decisions.json` by hand. The SKILL gives no other route.
- **To reproduce:** make `EvolutionService.apply` raise once, edit the model, then run both calls.

**F6. An absolute model path through a symlinked directory is refused** (`consolidation.py:165`)
- **What's wrong:** the module uses `Path.absolute()`, while `EvolutionService` compares against the resolved root.
- **What you'd see:** on macOS, `python -m gnd.evolve.consolidation /tmp/x/codes.json` gives `consolidation refused: model path is outside its trusted anchor` (exit 3). The same model works with a relative path after `cd /tmp/x`.

**S1 (style, no consequence I could show).** On resume (line 269 on), the pending decision is checked only against its own hash. `_check_mutation` and the group/model match are not re-run. A hand-edited journal would publish any preview that `apply` accepts. The journal is local trusted state, so this is hardening only.

## 2. What I checked and found true
- **Concurrent submissions:** the journal uses `publish_leaf_atomic(expected=stamp)`, a real compare-and-swap (exchange then verify). Two different decisions submitted at once cannot both become pending.
- **Concurrent resumes (P7):** I ran four threads resuming one pending merge. Exactly one returned `completed`; three refused with stale-model CAS. The journal ended with one completed entry and no pending decision, and the next step said `no-eligible-group`.
- **Crash after finalize, before the completion write (P5):** resuming returned `completed`, with `after` matching the live model hash. Repeating the decision returned `already-completed`.
- **No unreviewed publication through the preview:** `EvolutionService.apply` re-derives the candidate from the operations. It also recomputes validation, verbalization and blast radius, and rechecks model CAS. A tampered candidate cannot be published past the checked one.
- **Earlier probes:**
  - A merge that drops a moved row is refused: "lost a required…".
  - A stale `model_sha256` is refused.
  - Work limits and the decision limit stop the run.
- **The SKILL's installed example**, run through the briefed `main` from a terminal: three commands, exit 0. The third returned a different group.
- **The `population_check` refactor:** `verified_sample_appends` behaves the same; the `PopulationLoadError` catch moved around the new helper.

**Standing check (code fitted to its examples):**
- `^[a-f0-9]{64}$` states the whole grammar of a digest. Fine.
- The row→span dict in `_located_rows` is fitted to the fixtures, which have one span per row. It breaks on the legal duplicate-span input in F4.
- The journal folder name is a hash of the file name. Fine.
- There is no regex over text the project renders itself.

## 3. What I could not check
- `demote-to-row` and `link-subtype` end to end: no test covers them and I did not build fixtures.
- Whether the `not touched` rule at line 147 refuses too often when the model has unrelated constraints with no subjects.
- Multi-process (not thread) races, and real power-loss behaviour.
- The live-tree changes beyond confirming they address F1 and F2.

Scratch probes are in `/private/tmp/cg3probe`, outside the repo; delete that folder when done. I changed nothing in the repository.

VERDICT: CHANGES_REQUESTED
