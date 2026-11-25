# release-0.5.0: close question sweep

Every open question of records 002 to 006, every decision of plan §10, and
the carried register RC-01 to RC-07 of the
[0.4.0 close](../../release-0.4.0/notes/close-question-sweep.md), each with a
disposition: **closed** (with its evidence), **repaired** (a plan amendment,
plan §15), **carried** (with a named owner and trigger) or **accepted** (a
stated residual). Swept on 2026-11-25 at main `75c9ef52`.

## Open questions of the records

| ID | Question | Source | Disposition |
|---|---|---|---|
| Q1 | Issue links for the Ossie notes bullets (276 to 280) | 002 | **closed**: the owner chose "Leave as written" (RW2 spec D6) |
| Q2 | One structure-guard test fails in the working checkout because of an untracked, locally excluded skill mirror | 002 to 006 | **accepted**: machine state, not the repository's; the same test passed in every clean-clone lane on beast-3 (RW1 to RW2, the pages commit and the close lane). Target for the mirror: the owner, as local maintenance |
| Q3 | `ossie_oracle` at the freeze commit, and a fifth installed probe | 002 | **closed**: the owner chose both; the lane ran at `85d076ba` (91 passed, the consumer test deselected) and P5 is in the acceptance file (004) |
| Q4 | E1 changes the version fields only and cannot see the notes' own readers | 002, refuted premise | **repaired**: plan §15, R1 |
| Q5 | The review round budget was not declared before RW1's round 2 | 002 | **closed**: stated in 002; RW2 and RW3 declared it before round 2 (003, 005) |
| Q6 | `gnd flatten` writes `checking.orm.flat.orm.json` where the notes and the help say `<stem>.flat.orm.json` | 003 | **carried**: to the owner, for the include-roots wording; trigger: the next edit of that command's help or the notes |
| Q7 | The shared test reader `markdown_blocks` splits lines at U+2028 and other separators Markdown does not use | 003 | **carried**: to the owner, as test-support maintenance; trigger: the next change to `tests/support/markdown_sections.py` |
| Q8 | Do the five added families files pass from an installed wheel with the source denied? | 003 | **closed**: all five passed in the acceptance run (004, 33 passed) |
| Q9 | Is the Ossie oracle root used at the freeze the Ossie milestone's? | 004 | **accepted**: it held both upstream repositories at the pinned commits and passed the lane's own pin check; its origin was not confirmed |
| Q10 | The Ossie oracle root is in a scratch folder and not durable | 004 | **carried**: to the owner, as maintenance; trigger: the next `ossie_oracle` run, which rebuilds it from the OS0 receipt if it is gone |
| Q11 | The dossier lists what was not measured | 004 | **closed**: [dossier](../evidence/RW3/dossier.md), "What was not measured" |
| Q12 | `release_text.py check` reads lines, so a phrase split over a line break is not reported | 005 | **carried** as RC-08 (below) |
| Q13 | The literature page's "GND 0.4.0" (RW3 spec D3) | 005 | **closed**: the owner chose to drop the version; applied in PR 287 |
| Q14 | Issue comments after publication (RW-D10, RW3 spec D5) | 005, 006 | **accepted**: not requested by the owner; none posted |
| Q15 | The owner's review of repository content and history (RC-07) | 005, 006 | **carried**: RC-07, narrowed (below) |
| Q16 | `docs/releasing.md` named token-published releases through 0.4.0 | 006 | **closed**: PR 288 names 0.5.0 (RC-06) |
| Q17 | The GitHub release body is the RW3 draft | 006 | **closed**: published as written; the owner may edit it on the release page |
| Q18 | The owner's `~/.pypirc` is readable by other users of the machine | 006 | **carried**: to the owner, on their machine; not a repository matter |
| Q19 | The full default lane at the pages commit `6e980af9` had not finished when 006 was written | 006 | **closed**: 22,033 passed, 0 failed, the two RC-02 errors ([close-results](close-results.md)) |

## Plan §10 decisions

| ID | Disposition |
|---|---|
| RW-D0 | **closed**: the standard GND panel reviewed the plan (001) and the close (008) |
| RW-D1 | **closed**: 0.5.0 published (006) |
| RW-D2 | **closed**: the owner extended it three times (plan §12 to §14); all four milestones merged before the bump |
| RW-D3 | **repaired**: the owner chose the Ossie relational files as the headline (RW1 spec D4); plan §15, R2 |
| RW-D4 | **closed**: the pins moved at publication (PR 287) |
| RW-D5 | **closed**: token upload of the retained files (006) |
| RW-D6 | **repaired**: the owner chose six probes and five families files (RW2 spec D2); plan §15, R3 |
| RW-D7 | **closed**: `-o addopts=''` for the acceptance file on beast-3 (004) |
| RW-D8 | **closed**: `pyrel_oracle` 345 passed at the freeze commit; `ossie_oracle` 91 passed on the owner's selection (004) |
| RW-D9 | **closed**: wheel, sdist and `SHA256SUMS.txt` attached and verified (006) |
| RW-D10 | **accepted**: as Q14 |
| RW-D11 | **accepted**: no RelationalAI engine ran an exported program; the notes and the dossier say so |
| RW-D12 | **carried**: as RC-07 |
| RW-D13 | **closed**: superseded; `uv run ruff check` exits 0 on main (plan §12), and every phase gate used exit 0 |
| RW-D14 | **accepted**: the workflow's prepare job was not run; only the macOS profile is observed |

## The carried register

| ID | Owner | Disposition |
|---|---|---|
| RC-01 | dev-tools source owner | **closed**: `uv run ruff check` exits 0 on main; the inherited findings are gone |
| RC-02 | optional-test tooling owner | **carried**: the two `tests/test_public_optional.py` setup errors under uv 0.13.7 appear in every lane of this milestone |
| RC-03 | release tooling maintainer | **closed**: the helper reports the two missed phrases, with negative controls (005); its successor is RC-08 |
| RC-04 | model-query policy maintainer | **carried** unchanged: this milestone added no runtime model query |
| RC-05 | disclosure maintainer | **carried** unchanged: this milestone did not assess the Ossie export's interaction with `redact`; the Ossie milestone changed the disclosure page for the new files |
| RC-06 | release procedure maintainer | **closed**: PR 288 |
| RC-07 | repository and PyPI account owner | **carried, narrowed**: on 2026-11-25 the owner stated "get-nick-done is mine"; the review of repository content and history was not stated and stays the owner's before the next publication |
| RC-08 (new) | release tooling maintainer | **carried**: `release_text.py check` reads lines, so a phrase split over a line break is not reported. The RW3 paragraph pass was withdrawn after two review rounds found six defects in it; `evidence/RW3/split-phrase-search.py` prints such blocks for a person. Trigger: the next change to the helper; the question is the unit it judges, not a pattern to add |

## Issues the 0.5.0 notes link

All are closed except 227 and 228, which the notes link for the parts the
growth milestones delivered; their remaining work belongs to those
milestones, not to this one. 279 and 280 are the Ossie milestone's two open
design questions. 286 was filed after the publication and is fixed in the
tag-only 0.5.1, which is outside this milestone (close-results).
