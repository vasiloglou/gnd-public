# literature-reading-reference: close delta

Every departure from plan r4 as approved, with where it is recorded.

| # | Departure | Why | Recorded in |
|---|---|---|---|
| X1 | The LR1 guide maps `constraint_ref` through the `gnd flatten` record instead of reading the constraint's id at that address in its declaring file | the address is in the composed model; the plan's sentence was false for include roots (review round 2, finding codex-1) | 002-phase-LR1.md refuted premises; plan A1 |
| X2 | The LR1 guide names witness shapes as examples, not a closed list | witnesses vary by constraint kind (row object, bare instance, positional array) | 002-phase-LR1.md; T10, T11 |
| X3 | The LR1 page's field check reads the page's executed code, not its prose | the default environment has no Markdown parser; a field named only in prose is unchecked (deferred residual) | 002-phase-LR1.md boundary and open questions |
| X4 | `tools/run_tutorials.py` gains a tutorial group | the page's example is executed by the existing runner | 002-phase-LR1.md; PR 243 body |
| X5 | LR3's labels are 31 facts, not 38 | `work_builds_on_method` is derived | plan A2; LR3 spec §13 F1 |
| X6 | LR3's run sets the byte budget to every source byte | the default 4,096 bytes stops the targeted pass after two sections | LR3 spec §13 F2; `run-record.json` |
| X7 | LR3's one prompt, used by both stages, is named in `run-record.json`, not in LH2's run settings | LH2 records no prompt | plan A3 |
| X8 | LR3's run was recorded before PR 245's empty-list rule | it ran on `main` `a0270591`; it satisfies the rule and replays identically under it | 005-phase-LR3.md; `evidence/LR3/pr245-replay.txt` |
| X9 | The fixture folder is `reference_fixture/`, and the module `reference_set.py` | naming beside `reading_fixture/` | LR3 spec §13 F3 |
| X10 | The interim reply drafted in LR2 became the full draft in LR3, one file | plan §5's two drafts share `notes/issue-reply.md` | 003-phase-LR2.md, 005-phase-LR3.md |
| X11 | Spend: one USD 0.013 probe outside the recorded run | to learn the CLI's output shape; under D3's ruling and counted against its ceiling; not inside the run's USD 0.29 | 005-phase-LR3.md |
| X12 | LR3-C1's licence: one licence entry per source in `labels.json`, the repository's Apache-2.0, with the work each paraphrases | the sources are paraphrases written for the repository (close review) | `reference_set.py`; LR3 T1 |
| X13 | The phases' last repairs were read by no phase reviewer; a final Codex round over the whole diff reads them at close | plan §8 asks one reviewer per phase diff; the repairs followed each review | close record |
| X14 | Three stacked pull requests (243, 244, 252), not one or two | LR3 waited for another milestone; each phase went out when done, LR2 on LR1, LR3 on LR2 | close-results, merge state |
| X15 | The scorer does its own matching and only shares `assurance_report.py`'s `(numerator, denominator)` shape, not its counting | the assurance scorer matches whole claims against passages, not reading attempts (D4) | LR3 spec §6 reuse table |
| X16 | Both passes use one prompt and ask no question; the roster's questions only schedule the targeted reads | the producer adapter is host-agnostic; the stages pass `questions` that it does not use | reference README; index.md; reply |
| X17 | A label's scope adds every section of its document that holds one of its values to its anchored sections; anchors are keyed by document | two labels' work identifiers lie only in the opening section (close review); the figures did not change | reference README, scoring rule; LR3 T1 |
| X18 | `build()` checks the corpus's document, model and answer-key digests | it read the corpus without the existing reader's binding checks (close review) | `reference_set.py`; LR3 T1 |

No phase was dropped. LR1-C3 is met in part (X3); no other criterion was
relaxed.
