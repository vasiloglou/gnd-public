---
milestone: pins-and-review-check
station: "phase-PF2"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-PF2
date: 2026-11-23
gate:
  command: "uv run -q python evidence/PF2/gen/grade.py <scratch>/pf2 <scratch>/grade2  (E5: every input the reviews reported, run on both versions of its capability)"
  exit: 0
  output: "64 rows; planted 4 of 4 found, every reported input wrong as reported, 0 missed; controls 0 false findings, 2 true findings (evidence/PF2/GRADING.md, key/grade-runs.json)"
  base: "ec538cc7 (PF1 head); corpus base origin/main 6b0a7e5a"
gates:
  - {name: "E1 corpus tests, each change in its worktree", command: "uv run -q pytest -q -p no:cacheprovider tests/test_<module>.py", exit: 0, output: "change-a 2 passed, b 2, c 2, d 2, e 3, f 2, g 3, h 2"}
  - {name: "E2/E3 answer key", command: "uv run -q python evidence/PF2/gen/run_key.py <scratch>/pf2", exit: 0, output: "each planted version wrong on its three inputs; each control right on all twelve (key/key-runs.json)"}
  - {name: "E4 key fixed before the runs", command: "cd evidence/PF2 && shasum -a 256 -c KEY-SHA256SUMS (committed in 36ca151e, before the runs)", exit: 0, output: "key/ANSWER-KEY.md: OK, key/branch-map.json: OK, key/key-runs.json: OK, gen/make_corpus.py: OK, gen/run_key.py: OK"}
  - {name: "PF2-C2 runs", command: "review_tool.py run --reviewer codex --wait .review-round, per change", exit: 0, output: "eight of eight exited 0 with a verdict: APPROVE b, d; CHANGES_REQUESTED a, c, e, f, g, h"}
selection:
  - {obligation: "PF2-C1..C4, E1-E5", disposition: run, command: "the gates above"}
  - {obligation: "guard block, ruff", disposition: "not applicable", note: "PF2 changes only files under .gnd-planning/ (project.md, issue 171 rule)"}
evidence:
  - {path: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/GRADING.md}
  - {path: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/KEY-SHA256SUMS}
  - {path: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/key/grade-runs.json}
  - {path: .gnd-planning/milestones/pins-and-review-check/notes/phase-PF2-spec.md}
---

# Claim

On a corpus of eight small diffs built for it, the standing "code fitted to
its examples" check in the review helper's brief, with a neutral question
and no `--claim`, led one Codex reviewer to report all four planted
fitted-code defects, each with an input that reproduces, and to make no
false finding on the four controls. It also found two real faults in the
controls, one of them a defect on `main`. This is the first evidence for
PR 235's and PR 246's "Not established" line. It is eight runs, not a rate.

Authority: plan r1 (owner, `001-plan.md`), D2 `codex` over about eight diffs
(owner); spec r1 by delegated approval (auto=true), spec §12. The runs used
`review_tool.py` as delivered on `main`, unchanged (R0.2).

## Named criteria

| Criterion | Result |
|---|---|
| PF2-C1 committed before the runs | corpus diffs, briefs and the key's sha256 in `36ca151e`; the reviews started after it; E4 checks |
| PF2-C2 a review per diff | eight of eight; no failure, no retry |
| PF2-C3 counts and limits | planted found 4, missed 0; controls false 0, true 2. Limits: spec §6 "Limits", restated below |
| PF2-C4 each miss and the brief | no miss; `GRADING.md` names the brief bullet each finding matches |

## Result

See `evidence/PF2/GRADING.md`. In short:

- K1 (regex over YAML), K2 (splits over frontmatter), K3 (literal parent
  names), K4 (regex over TOML): each planted version drew a finding with
  inputs that break it, and each finding named the repository reader that
  already does the job.
- K1 and K4 controls: APPROVE.
- K2 control: the reviewer found that the reused reader,
  `gnd.exp.frontmatter._split`, takes an indented `---` inside a block scalar
  as the closing fence and drops the rest of the frontmatter. Reproduced in
  this repository. Its callers include `gnd exp`'s spec and conclusions
  readers and codegen's SKILL.md round trip (OQ4).
- K3 control: `Path.relative_to` is lexical, so `gnd-solve/../gnd-adopt/SKILL.md`
  returns `gnd-solve`. A flaw in the control as written.

## Limits

- Eight diffs, one reviewer, one run each. It shows the check can find these
  defects; it does not estimate how often it does.
- One author wrote the planted defects, the controls and the grading. The
  planted defects are common and fairly visible forms; subtler fitting was
  not tried.
- The reviewer could read `AGENTS.md`, which states the rule, as in real use.
- **Blindness was by arrangement, not enforced** (phase review F1, spec
  correction c1). The eight worktrees shared one clone, so a reviewer could
  have shown the other version's branch, and the held key was readable on
  disk. The retained logs show neither route used.
- Codex output is not deterministic.

## Review

Instrument: the review helper, one reviewer in a different tool (Codex,
read-only, reasoning high), plan D3. **One reviewer is one reviewer; this is
not a panel.** Brief `notes/reviews/phase-PF2-r1/` over the PF2 diff from
`ec538cc7`, asking it to refute the grades, the key's timing, the blindness
and the limits.

CHANGES_REQUESTED, three findings, each reproduced before it was believed:

- **F1, blindness not enforced.** True: one shared clone let `git show` reach
  the other version, and the held key was readable. The logs show neither
  used. Spec correction c1; the record's limits restate it.
- **F2, E5 incomplete.** True: the first grading ran a subset of the
  reported inputs. `gen/grade.py` now runs all of them on both versions
  (64 rows); every one reproduces as reported and no grade changed.
- **F3, the checksum manifest did not check.** True: the scripts sat at the
  evidence root while `KEY-SHA256SUMS` names `gen/`. Moved to `gen/`; the
  committed manifest now checks as written (E4).

The reviewer reproduced all 32 first-pass grading rows and the 24 key rows,
and agreed with the grades and the stated limits. **The repairs carry no
review opinion.** No finding changed a result, so no second round ran; the
milestone close review reads the repaired bytes.

## Refactoring review

None needed: PF2 added no code to the repository. The corpus lives in a
scratch clone; its scripts are kept as evidence.

## Open questions

| # | Question | Next owner |
|---|---|---|
| OQ4 | `gnd.exp.frontmatter._split` (`src/gnd/exp/frontmatter.py:102`) takes `lines[i].strip() == "---"` as the closing fence, so an indented `---` inside a block scalar ends the frontmatter early. A defect on `main`, outside this milestone's scope | the owner: a fix of its own with a regression test |

## Boundary -- what this result did NOT establish

- A detection rate, or how the check does with other reviewers, other
  questions or subtler fitted code.
- That the brief needs no change: with no miss, nothing here argues for one,
  and no dev-tools proposal was drafted.
- No change to `src/`; OQ4 is reported, not fixed.
