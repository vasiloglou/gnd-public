# WN3 diff review

Retained text of the single reviewer's returned report (one local reviewer
agent; one reviewer is one reviewer). Local edits: scratch paths read
`<scratch>`.

## Scope
I read the whole WN3 spec, including its gate section, plan §4 WN3 (C1 to C4), `docs/reference/why-not.md`, the full working-tree diff, all five example files, `build_example.py`, the loop test, the how-to, `tests/test_why_not_anonymity.py` and the two skill-census tests.

What I ran:
- `run_tutorials.py --group why-not`: 5 blocks passed.
- The loop test: 3 passed.
- The skill and packaged tests, `test_documentation_tutorials.py`, the anonymity test, and the IK6/IL6 walk tests: 550 passed, 2 failed (the IK6 census, explained below).
- One probe: `<scratch>/wn3-review/p1.py`.

What I did not run: the full suite, the v71 witness corpus, a docs build, `tools/check_docs.py`, and `tools/check_installed_docs.py` (it builds wheels and venvs). I did not try a population that needs a reference root.

## Claims checked and found true
- **Example.** The model validates. Gap 1 is `(atom, 1, authored)`: ground, with `work` taken from the sample. Gap 2 is `(atom, 2, reviewed)`: `work` is bound and `reviewer` is free. Once both facts are added, why-not says `derived`, witness says `proved`, and replay exits 0.
- **Repair uses only the payload.** `repair()` reads only `fact_type`, `roles` and `samples[0]`, plus `extracted.json` for free roles. It asserts that the bound roles and the extracted roles do not overlap. Both repaired facts are compared with hard-coded expected tuples, so the test cannot pass vacuously.
- **Negative controls have teeth.** I traced each against a broken kernel; I did not run these as mutation tests.
  - A kernel that ignores bound values (it only asks "does `authored` have rows?") moves to `reviewed` under the wrong-bound-value control, which the test catches.
  - A kernel that ignores the claimed row (rule mode) also moves past `authored` there, because `q-18` joins `Letters Home`.
  - A kernel that does not seed `$p` from the claimed row loses ground `person`, so `repair()` raises a KeyError.
  - The previous-predicate control is weaker. In row mode its row cannot join anyway, but it matches the plan's wording.
  - Both controls assert `blocked`, so the claimed row stays underived.
- **Before repair.** `check` gives exit 0 with `pass` for `derivation:certified`, and witness gives `missing`. That is the variant the spec names.
- **How-to blocks.** Every runnable block asserts its output with exact line matching.
- **Packaging.** Packaging is unaffected: everything under `src/gnd/` ships and nothing in the example is git-ignored. The example list is updated in both places.
- **IK6 census.** The two failures are `wrong phase: src/gnd/skills/gnd-export/SKILL.md`. The cause is that an uncommitted edit is credited to `CURRENT = "IK-close"`. After the commit, `git_phases` for this file is `{IK6}` (the IL6 subject does not match the IK regex), which equals its census cell `IK6`. So this resolves on commit, as you said, as long as the WN3 commit subject has no `(IK…)` scope. The IL6 census passes.

## Findings

### WN3-R1 — The how-to says "`gnd check` passes" without running it (completeness, high)
**Where:** `docs/how-to/repair-a-missing-claim.md`, the paragraph after the copy and validate block.

**What is wrong:** No `gnd-run` block backs this claim. That breaks the spec's §4 standing rule 6: every claim in the how-to is a `gnd-run` block with asserted output.

**Reproduction:** The page has five `gnd-run` blocks, and none of them calls `gnd check`. The claim is true (the probe gives `gap check exit 0 … 'verdict': 'pass'`), but the page does not show it.

**Fix:** Add a `gnd-run expect=0` block that runs `gnd check` on `gap.pop.json` and prints the `certified` verdict.

### WN3-R2 — After the repair, the population fails `gnd check`, and nothing says so (hardening, high)
**Where:** `gap.pop.json` has `covers: ["certified"]` and no asserted rows. This affects the how-to's last section, the README, and the end state of the loop test.

**What is wrong:** After both repairs the row derives. The population still covers `certified` and asserts none, so `check` now fails. A reader who follows the page and then runs `gnd check` gets exit 1. Neither the page nor the README warns about this.

**Reproduction** (probe `p1.py`):
```
twice check exit 1 [('fail', {... 'kind': 'derived-extension-incomplete', 'message': "The derived extension of 'certified' is incomplete — missing {\"quote\":\"q-17\",\"person\":\"Ada Byrne\"}." ...})]
```

**Fix:** Either option keeps the "pass with the row absent" variant before repair:
- add a sentence and a `gnd-run expect=1` block after the witness step, saying a covered fact type must now assert the derived row; or
- append `certified(q-17, Ada Byrne)` and show `check` passing.

Optionally, have the loop test assert the check exit code after the repair, so this behaviour is pinned.

### WN3-R3 — The skill route sentence can hand why-not a request it refuses (hardening, medium)
**Where:** `src/gnd/skills/gnd-export/SKILL.md`, the sentence added to step 2.

**What is wrong:**
- `REQUEST` in steps 1 and 2 is a "nonempty version-1 target request", so it can hold several targets. Why-not's `--row` needs exactly one target whose `fact_type` matches (`docs/reference/why-not.md`, "Ask the question"). Following the sentence literally with a multi-target request gets exit 3.
- The sentence also drops `--reference-root ROOT`, which the witness command in the same step passes, and the reference says reference populations bind as they do for witness. I did not reproduce this part.

**Reproduction** (probe `p1.py`, two-target request over `gap.pop.json`):
```
witness multi exit 2 ['missing', 'missing']
why-not multi 3 refused input-invalid
```

**Fix:** Say "with a one-target request for that `missing` row", and add `--reference-root ROOT` to the command.

No other defects were reproduced. The README is hand-written, and `build_example.py` does not regenerate it, which is harmless.
