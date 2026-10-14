# Phase PL6 spec: installed acceptance and milestone disposition

## Status and authority

Prepared on 2026-10-14 while PL5's independent review remains pending. Existing
001 milestone delegation covers this spec's approval; PL5 completion remains a
hard prerequisite to claiming PL6 complete. No live recording is repeated and no
merge, publication or certification is selected.

## Obligations and implementability

| Source | Obligation | Discharge |
|---|---|---|
| Plan §4 PL6-C1, §9 | Fresh-wheel acceptance with current resources and block counts | Run tools/accept_pyrel_applications_install.py against final frozen source bytes; verify receipt hashes and command exits |
| Plan §4 PL6-C2, inherited residual | Classify the default-suite failures against main | Retain prior full run's actual pytest summary; rerun its eight failed nodes on baseline a9a2f08 and current isolated candidate; do not repeat the broad suite merely for closure |
| Plan §4 PL6-C3, AGENTS | PR against main | Push only the topic branch and create/update its PR; no merge |
| Plan §0 PL-R1–R8 | Shell equivalence, no live models, authentic excerpts, labelled equivalents, pinned witnesses, honest recordings, prose, resource pins | PL5 gates and installed chapter receipts; recording replay tests; wheel inventory |
| Plan §5 | No skill changes; runner and environment documentation | Inherit PL1 bytes and current focused consumers; no discovery-link edits |
| Plan §6 | Block-count drift, review repair hazard, recorded first-try outcomes | 71/10 BookRec and 57/11 Expense measured from actual step records; bounded independent review after repairs |
| Plan §7 | No Snowflake, rule changes to shipped models, release, certification or publication | Preserve these boundaries in records and PR |
| Plan §8 | Independent close review and question sweep | Four local readers after phase records; no claim that a single reader is a panel |
| PL4 006 | Claude Code recording absent; PL4 lacked independent review | Keep PL4-Q1 open to owner; close readers must cover recorder and wrapper, and cannot retroactively establish a Claude recording |
| PL5 resume findings | All shown task/transcript/candidate/feedback bytes checked; accurate coverage wording; actual accepted Expense candidate reported | Tamper controls, both chapter lanes and install receipt |

Standing rules: totality and validation order use existing refusal controls;
algorithm bounds remain the existing finite cap and corpus; one policy walk is
verify_learning_paths; one resource inventory derives from shipped files;
measure counts and exact hashes rather than inferring them. No new parser or
runtime algorithm is introduced by these count changes.

## Verification-selection ledger

| Gate | Disposition | Command / expected outcome | Inputs and invalidation |
|---|---|---|---|
| Resource/count controls | run | python -m pytest -q tests/test_pyrel_applications_install.py; exit 0 | harness, examples, count pins; rerun on changes |
| Fresh installation | run | python tools/accept_pyrel_applications_install.py --out FRESH; exit 0 | source identity, wheel, docs, runtime lock, config and tools; rerun if any recorded source changes |
| Main failure classification | run | prior eight failed test nodes on clean a9a2f08 and candidate; seven known refactoring failures, reference closure passes clean | isolated trees, test/runtime identity; changes invalidate comparison |
| Full default suite | inherit with limit | prior retained summary: 8 failed, 14643 passed, 521 deselected | pre-resume source; wrapper lost exit code; not a verdict over repaired pages; current impact closed by focused tests |
| Chapter and agents tutorials | run / inherit final PL5 evidence | bookrec and expense offline/native, agent-recorded/session/model; exit 0 | all page and shipped-example bytes; receipt binds selected runs |
| Site | run | zensical build --strict; check_docs.py site; exit 0 | docs, assets, config, overrides |
| Historical broad lanes | cadence | explicit owner request or separately selected CI | not part of this milestone's current impact closure |

## Decisions and unresolved gates

Delegated approval (auto=true), 2026-10-14, scope pyrel-agent-loop under 001.
No spec panel. The already completed broad suite is classified, not rerun;
the wrapper's successful process exit is explicitly not pytest success.
Independent review authority is currently pending after automatic approval review
rejected the gpt-6-sol payload/destination. The continuation request does not
by itself override that rejection. No reviewer result may be fabricated.

## Out of scope and close limits

Do not fix the seven main-inherited refactoring failures here. Defer to GND
maintainers' already named refactoring follow-up. No real Claude recording is
claimed. Completion predicate 4's literal requirement for Claude evidence remains
unmet unless the owner explicitly accepts the Codex-only boundary or authorizes
and completes that recording under its separate gate. A prepared PR is not
milestone acceptance, merge authority, release authority or publication.
