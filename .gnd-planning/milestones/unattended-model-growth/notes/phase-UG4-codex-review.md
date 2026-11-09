# UG4 phase diff: Codex CLI review (one reviewer)

2026-11-09. Instrument: one reviewer in a different tool, as for UG1 to UG3:
`codex exec --sandbox read-only -c model_reasoning_effort=xhigh` (model `gpt-6.1-sol`), prompt
on stdin, repository read-only. **One reviewer, not a panel.** Subject: `git diff
478ea2a2..ff49a713`.

**Edited from the reviewer's output in one way:** the operator's absolute worktree path was
replaced by `<repo>/`. Nothing else in "Reviewer output" is changed. The reviewer ran
read-only CLI and service probes and called the guard tests directly; it wrote no files.

## Dispositions

Each finding was reproduced by the author before it was believed.

| # | Class | Reproduced | Disposition | Regression |
|---|---|---|---|---|
| 1 | blocking | yes: `gnd evolve apply`'s parser has no `--shape-report`. The sentence "then `apply` with the same options" after a preview with `--shape-report` predates UG4 (it was in the reference at `ad454305`); UG4 kept it | fixed: apply repeats `--policy`, `--populated` and `--check-population`; `--shape-report` is preview-only (exit 64 on apply) | the guard's new "option of the wrong command" mutation case; the sentence itself is prose |
| 2 | blocking | yes: the old guard returned `[]` for a misspelt option inside the wrapped span, for `--policy banana`, and for a fenced block | fixed: spans may wrap, fenced lines are checked, and a literal value must be one of the option's choices; six mutation cases | three of the four new mutation inputs return `[]` under the old `_drift` (measured), all six are reported by the new one |
| 3 | blocking | yes: the paragraph "Constraints travel with their fact type" still said such a constraint is refused, and "admitted only when every one of them is new or empty", without the clean-population exception | fixed: both statements scoped ("unless a clean population clears it", "without that population") with a link to the section | prose |
| 4 | hardening | yes: a fact type the same proposal adds is never populated, so "never admits a rule over a fact type that carries sample rows" was too broad; round 2's own refusal is correct (`population: sample-rows`) | fixed: "carries two sample rows in the current model, and the population check never clears a rule over such a fact type" | prose; the tutorial replay still passes |
| 5 | hardening | yes: the counts are per span, so a declared document no span cites produces no entry | fixed in the #74 draft: "when at least one source span was not re-hashed" | prose |

None rejected. The fixes were not re-reviewed.

## Reviewer output (verbatim, path sanitized)

Found **3 blocking defects and 2 hardening issues**. No files changed. Verification used read-only CLI/service probes and direct calls to the new guard tests.

1. **Blocking — “same options” makes apply fail.**  
   [unattended-growth.md:53](<repo>/src/gnd/skills/gnd-model-from-text/references/unattended-growth.md:53) includes `--shape-report` on preview, then instructs apply with “the same options.” Apply does not accept that flag, as the contract’s “Shape report” section explicitly states.  
   **Reproduced:** a complete `gnd evolve apply … --policy additive --shape-report` invocation exits **64**, reporting `unrecognized arguments: --shape-report`.  
   **Minimal fix:** specify that apply repeats `--policy`, `--populated`, and any `--check-population`; `--shape-report` belongs only to preview. Correct the corresponding wording in spec §6.1(b).

2. **Blocking — the guard misses an actual procedure command and does not enforce parsing.**  
   [test_unattended_growth_guidance.py:195](<repo>/tests/test_unattended_growth_guidance.py:195) excludes newlines from code spans. Consequently, the newly added command at reference lines 284–285 is unchecked. `_drift` also checks option names without parsing arguments.  
   **Reproduced:** changing that actual multiline command’s `--check-population` to `--check-populations` returns `_drift == []`. Changing the actual single-line preview’s policy value to `banana` also returns `[]`, while the real parser exits **64**. A fenced command with an invalid flag likewise goes undetected. Both committed guard tests pass.  
   **Minimal fix:** extract multiline spans and fenced commands, normalize their whitespace, and parse complete invocations with the real parser. Add mutation controls covering those representations and invalid option values.

3. **Blocking — the retained refusal rule contradicts the newly documented admission route.**  
   [unattended-growth.md:75](<repo>/src/gnd/skills/gnd-model-from-text/references/unattended-growth.md:75) still says a new constraint on an already populated fact type is refused, and line 80 says admission occurs **only** when every subject is new or empty. Those absolute statements contradict the new “Constraints on fact types that already hold facts” section and the normative population-check exception.  
   **Reproduced:** UG2 corpus case C01, with `customer_places_order` explicitly populated, produces `constraint.populated.add` without the population option and **no policy issues** with `populations/clean.json`.  
   **Minimal fix:** replace this duplicated policy summary with timing advice and a citation to “Population check,” or explicitly scope the refusal statements to runs without the exception.

4. **Hardening — the tutorial’s sample-row prohibition is broader than shipped behavior.**  
   [grow-a-model.md:272](<repo>/docs/how-to/grow-a-model.md:272) says the policy “never admits a rule over a fact type that carries sample rows.” Newly added fact types are excluded from the effective populated set, even when they contain samples.  
   **Reproduced:** service preview under additive policy admits a newly added fact type containing both sample rows and a proposed uniqueness constraint. Separately, the tutorial’s actual round 2 produces `population: sample-rows`, so **its refusal claim is correct**.  
   **Minimal fix:** say that the population-check exception cannot clear this refusal because the fact type has sample rows **in the current model**.

5. **Hardening — the #74 draft confuses missing documents with unchecked spans.**  
   [ug4-issue-followups.md:23](<repo>/.gnd-planning/milestones/unattended-model-growth/notes/ug4-issue-followups.md:23) promises a warning when a declared document is not supplied. The implementation counts spans; an omitted document cited by no span produces no warning or error.  
   **Reproduced:** validating UG3’s `rounds.orm.yaml` with only `ledger.txt`, omitting its declared but unused `annex.txt`, exits **0** without `spans-unchecked`, including with `--require-documents`.  
   **Minimal fix:** change the condition to “when at least one source span was not re-hashed.”

**Nits:** none.

Claims checked and found true:

- Document-add followed by citing elements previews successfully; the candidate’s new span is unchecked when its new document is omitted.
- `--require-documents` without `--document` exits 3 on the cited unattended fixture; supplying both documents exits 0.
- Apply requires repeating `--check-population`; a population digest mismatch exits 11.
- New anchors resolve. Routing changes are exactly two new distinct edges, three additional link occurrences, and no removals.
- The guarantee-wording scan found the required qualifications; the downstream-name scan found no hits and its positive control succeeded.
