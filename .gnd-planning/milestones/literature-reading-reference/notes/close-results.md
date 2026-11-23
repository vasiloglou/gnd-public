# literature-reading-reference: close results

What the milestone delivered against plan r4 and its close amendments
A1–A5 (§13), at the LR3 branch head. Each row names the evidence; the phase
records hold the gates verbatim.

## Goal predicates

| Predicate | Result | Evidence |
|---|---|---|
| LR1: for a source `gnd verify` fails, a host lists the failing constraints and their rows from one documented place; a test holds the steps on a packaged failing source | met | `docs/guides/documents.md` "Reading a failed verification"; its runnable block, executed by `tests/test_documentation_tutorials.py::test_documented_learning_path[failed-verification]`; `tests/test_lr1_verify_failure_listing.py` T1–T11 |
| LR2: the pages state one rule for where a quoted span may lie, what it means for a host that shows one section at a time, and a test holds both sides | met | `docs/reference/anchors.md` "Where a span may lie"; `docs/literature/commands.md` (Act 2), `docs/literature/index.md:11`; `tests/test_lr2_quote_scope.py` T1–T5 |
| LR3: a labelled set ships with the literature example; a recorded run reports recall and precision per stage setting, names producer and settings, replays with zero producer calls | met | `src/gnd/examples/literature/reference_set.py`, `reference_fixture/` (labels, run, `run-record.json`, `score.json`); `tests/test_lr3_reference_set.py` T1–T9 |
| Close: phase records, green focused gates, guards, lint, component check, a drafted reply to #226, a close review | met | records 002, 003, 005, each with its lane, the guard block, `uv run ruff check` and the component-index check at exit 0; at the LR3 branch head the same four run again in the close record; `notes/issue-reply.md`; the full panel's close round (`evidence/close-review/`) |

## Criteria

| Criterion | Result | Evidence |
|---|---|---|
| LR1-C1 | met | T1: one `uniqueness` failure at `fact_types[subject_label].constraints[0]`, two rows, mapped to `subject_has_one_label` through the flattening record (A1) |
| LR1-C2 | met | T2 |
| LR1-C3 | **met in part**: for every name the page's code reads and every listed name; a field named only in the prose is unchecked (X3) | T3: keys the page's `failed()` reads equal the listed set; each in `report.schema.json` at its level and in a live report |
| LR1-C4 | met | T4 (deontic warning), T5 (markers; `--unredacted` and `GND_DISCLOSURE=internal` show the rows) |
| LR1-C5 | met | T6: default text and JSON SHA-256 equal the base's |
| LR1-C6 | met | T1, T8 (derivation), T10 (mandatory bare instance), T11 (ring) |
| LR2-C1 | met | T4: the rule sentence on one page; the literature pages link it |
| LR2-C2 | met | T1, with `block_id` naming the other section |
| LR2-C3 | met | T2 (`source span or excerpt differs`), told apart from T3 (`digest differs`) |
| LR2-C4 | met | no reading-example code or fixture changed; `tests/test_ld3_reading_workflow.py` in every lane |
| LR2-C5 | met | T4, T5 |
| LR3-C1 | met | T1: a licence per source in `labels.json` (`Apache-2.0`, with the work each paraphrases; X12), counts 11/8/12 (A2), the corpus's files unchanged and digest-checked |
| LR3-C2 | met | T2 (replay guarded against any `ProducerCall`), T3 (score byte for byte) |
| LR3-C3 | met | `score.json` per pass with numerator and denominator; `run-record.json` names model, CLI, flags, prompt digest, budget, spend; roster split in `roster.json` |
| LR3-C4 | met | T6 (changed gold fact changes the score), T7 (changed response, changed source byte refuse replay), T4 (found against wrong predicate, reversed roles, wrong section) |
| LR3-C5 | met | T5: page figures equal `score.json`; R0.2's sentence; #226's figures |
| LR3-C6 | met | `notes/issue-reply.md`: all three requests; says nothing is merged or released on 2026-11-23 |

## Standing rules (plan §0)

R0.1: no anchor or verify format change (LR1-C5, no code change in LR2).
R0.2: the page and README carry the one-run sentence. R0.3: no rate in the
verify payload. R0.4: no packaged fixture changed; the corpus's bytes are
held by LR3 T1. R0.5: the recorder is outside every gate; tests replay.
R0.6: one home each (documents guide, anchors reference, reference README).

## The measurement

Set: the reference set (12 development documents, 46 sections, 31 labels).
Producer: `claude-sonnet-5-5` via the `claude` CLI and the owner's login,
under the owner's rulings D3 ("sonnet 50$", 004-ruling-D3.md) and the
transport ("Claude CLI login", A5). One prompt for both passes, no question
asked. Settings: `budget_bytes` 7,708 (X6), scenario `full`, default
`ReadingLimits`. 46 calls, USD 0.290965, plus a USD 0.012956 probe before
the run (X11) under the same ruling: USD 0.30 of USD 50.

| Pass | Produced | Found | Wrong predicate (D4's companion) | Outside every gold scope | Precision | Recall after |
|---|---|---|---|---|---|---|
| broad | 10 | 9 | 0 | 0 | 9/10 | 9/31 |
| targeted | 23 | 18 | 2 | 0 | 18/23 | 27/31 |

A row outside every gold scope counts against precision (LR3-D3); none
occurred. `score.json` carries every column; `docs/literature/index.md`
shows recall and precision beside #226's figures and links the rule.

## Reviews

Plan: full GND panel, two rounds (r2, r3). LR1: Codex, two rounds, eight
findings, seven fixed, one deferred. LR2: Codex, one round, one finding,
fixed. LR3: Codex, one round, five findings, fixed. Close: the full panel,
one round; its fixes and the phases' last repairs (LR1 `60306a5c`, LR2
`45551cf1`, LR3 `aec93739`) are read by a final Codex round over the whole
diff, recorded in the close record (X13).

Other §5 deliverables: release-notes entries, one per phase, under the
unreleased heading of `docs/release-notes.md`; the `gnd-extract`
extraction contract's citing cell with an absolute URL (H25), held by
`tests/test_packaged_skills.py` (guard block) and LR1 T7.

## Merge state

None of PRs 243 (LR1), 244 (LR2), 252 (LR3) is merged; nothing is
released. They are stacked: 243 is LR1 and the plan records on `main`; 244
adds LR2 on 243's branch; 252 adds LR3 and the close on 244's. Merging 243
alone ships LR1; each later one needs the one before (X14). Each branch has
`main` `6b0a7e5` merged in.
