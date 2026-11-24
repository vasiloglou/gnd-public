---
milestone: literature-reading-reference
station: phase-LR3
skill: "n/a -- repository development via process-phase auto=true, not a gnd-solve station over a domain model"
scope: phase-LR3
date: 2026-11-23
gates:
  - command: "uv run pytest -q tests/test_lr3_reference_set.py tests/test_ld3_reading_workflow.py tests/test_ld4_revision.py tests/test_ld5_verdict.py tests/test_li1_literature_corpus.py tests/test_li1_assurance_report.py tests/test_lh1_reading_host.py tests/test_lh2_reading_replay.py tests/test_lh3_admission_shape.py tests/test_lh4_admission_rules.py tests/test_lr1_verify_failure_listing.py tests/test_lr2_quote_scope.py tests/test_documentation_tutorials.py --tb=short"
    exit: 0
    output: "475 passed in 860.62s (0:14:20)"
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 224.52s (0:03:44)"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base origin/main --strict"
    exit: 0
    output: "changed against origin/main (f7fad6a): 172 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "LR3 adds an example module, a fixture, a tool and tests; it changes no existing package code"
evidence:
  - path: .gnd-planning/milestones/literature-reading-reference/notes/phase-LR3-spec.md
    sha256: e86e601c9adfe2ebce66da918d28c7c92db87a9459118bc87f52dcf3aab00b2d
  - path: .gnd-planning/milestones/literature-reading-reference/notes/issue-reply.md
    sha256: 67788371d142b20f29ea167cd3427c60bc8cfede292b12d41fc05bf1e7d09af2
  - path: .gnd-planning/milestones/literature-reading-reference/evidence/LR3/final-gate.txt
    sha256: b7d46023a5823d14bb68677143cca904ad6ed9c002e3acb4b9543eb58f3ebc18
  - path: .gnd-planning/milestones/literature-reading-reference/evidence/LR3/pr245-replay.txt
    sha256: b3f69dba90db00d5e84163d6b5c5b6609158c1cacad8094ec29cb1bb9648071f
  - path: .gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR3-r1/review.md
    sha256: c24cfd951a84c66a2df2262e33da5f129e6060cc18baf067e13cacffd464fb44
  - path: .gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR3-r1/FINDINGS.md
    sha256: 7c97a8a2d5b2dc7a4749a179030d47fa1d80fec6249d5a07aafe2b8bc066c5d0
  - path: src/gnd/examples/literature/reference_set.py
    sha256: 0c00d99c632b6290e694e3f6832a3c56dc2a1b1f95dd3edbccf4b22bf5b3c850
  - path: src/gnd/examples/literature/reference_fixture/README.md
    sha256: 4b347474d65808130d774bbb799785574e52c9eaae58f4525cdd5bb045dc0aab
  - path: src/gnd/examples/literature/reference_fixture/labels.json
    sha256: 3883b73366a9512c8b334c79422ba0510c222f8ca1f57f7f665427c3294eef8f
  - path: src/gnd/examples/literature/reference_fixture/roster.json
    sha256: 18eb3ae95da5f02e98d2c75a76440d3954794cc3f51426625e3337655a4e399c
  - path: src/gnd/examples/literature/reference_fixture/run-record.json
    sha256: ba9c72866b1a682f9e8f66acd400f9713437145deefb5c256266008f5cd4956f
  - path: src/gnd/examples/literature/reference_fixture/score.json
    sha256: 08c4830c3fefe901f6452aa62af4ceddf86b3a281cc14b264d162adbe3bec2dc
  - path: src/gnd/examples/literature/reference_fixture/run/run.json
    sha256: b903f36284000757372c156332f111bfbaf62368b155d790af55a4e10839b192
  - path: tools/record_lr3_reference_run.py
    sha256: 38ba4fe00ff81e9a78ddd725f29b8c728723d287988a2bd5dacd5c5e292dfb60
  - path: tests/test_lr3_reference_set.py
    sha256: 87672bd42a2581c3e3f2bbe816c5d047a79e249ec45336d0376d4efabb605978
  - path: docs/literature/index.md
    sha256: aaf8dcd83beddf9b750f16d1e8d165bd2f2eb16ae7302d007f0b7744e6412ad8
---

# Phase LR3: a labelled reference set and one recorded run

Branch `claude/lr3-reference-set`: the LR2 branch (PR 244) with `origin/main`
merged twice, last at `f7fad6a1` (PRs 241, 245, 239 and 240 merged).
Implementation commits `bebd3b8b`, the run and page commit after it, and the
review fixes `aec93739`. Started on the coordinator's "GO LR3" of
2026-11-23, which sequences and approves nothing.

## Spec gate and rulings

Delegated approval (`auto=true`), 2026-11-23, under
[001-plan-gate.md](001-plan-gate.md). Gated bytes: `notes/phase-LR3-spec.md`
r1 with §12, SHA-256
`63f5fd0207f16170876ebaefd9356719ddd55f2d34ab1c61f288b1ec5edd8970`; §13 was
appended after the gate. §7's rulings (D1 (d), the set, precision counting
rows outside every gold scope, exact normalized names, a label-free
schedule) are the gate's: delegated, not the owner's reading.

Owner rulings this phase rests on, not delegated:

- D3, "sonnet 50$" ([004-ruling-D3.md](004-ruling-D3.md)).
- The credential, asked in this phase on 2026-11-23: "Claude CLI login".
  The producer runs `claude -p` with the owner's Claude Code login. No key
  was read or printed.

## What shipped

- `src/gnd/examples/literature/reference_set.py`: `build()` writes the
  reference root from the packaged corpus without changing it; `score()`
  applies the scoring rule; a `build` and `score` CLI.
- `src/gnd/examples/literature/reference_fixture/`: the root (12 documents,
  the model as JSON, roster, profile, 31 labels), `README.md` (the scoring
  rule's one home), the recorded `run/`, `run-record.json` and `score.json`.
- `tools/record_lr3_reference_run.py`: the Claude CLI producer and recorder.
  It is outside every gate, and it spends paid calls.
- `tests/test_lr3_reference_set.py`: T1–T9, 20 cases.
- `docs/literature/index.md`: "How much does the reading find?", with the
  figures beside #226's. There is also a release-notes bullet.
- `notes/issue-reply.md`: the reply draft for all three requests. **Not
  posted.**
- `dev/components/COMPONENTS.md`: a new entry,
  `examples.literature_reference_set`.

## The measurement

One live run, 2026-11-23, `claude-sonnet-5-5` only, through `claude` CLI
2.1.322. It made 46 calls (12 broad, 34 targeted) and read all 7,708 bytes.

- Spend: USD 0.290965, plus one USD 0.012956 probe before it. That is USD
  0.30 of the owner's USD 50 ceiling.
- Recall: 9/31 after the broad pass, 27/31 after the targeted pass.
- Precision: 9/10 on the broad pass, 18/23 on the targeted pass. Two of the
  targeted pass's misses are the right pair of names under another fact type.

The run replays with zero producer calls (T2, guarded).

**The run predates PR 245's rule.** It was recorded on `main` `a0270591`,
before PR 245's rule that a fact type may not map to an empty list. It
satisfies that rule: the adapter never sends such a response. It replays to
the same evidence under PR 245's `reading.py` (`evidence/LR3/pr245-replay.txt`),
and the lane above passed on `main` `f7fad6a1`, which has PR 245 merged.
Whether to re-record is the owner's call; nothing here requires it.

## Criteria

| Criterion | Evidence |
|---|---|
| LR3-C1 | T1 (licence note, counts 11/8/12, corpus bytes unchanged) |
| LR3-C2 | T2, T3 |
| LR3-C3 | T3; `score.json`, `run-record.json` |
| LR3-C4 | T4 (found, wrong predicate, wrong section, reversed roles), T6, T7 |
| LR3-C5 | T5 |
| LR3-C6 | `notes/issue-reply.md` |

## Review

One round, one reviewer: Codex through the review helper, under the owner's
"Review helper, both". **One reviewer is one reviewer.** It confirmed the
figures, the overlay, the hashes and the refusals by reading files and
running in memory, without writing any. Five findings, all reproduced and all
fixed in `aec93739`, each with a regression test that fails on the pre-fix
code:

- codex-1 (blocking): wrong predicate counted reversed roles under the same
  fact type.
- codex-2: prompt fields were filled in sequence.
- codex-3: malformed attempts escaped the scorer's error handling.
- codex-4: T2 did not guard against producer calls.
- codex-5: the README and the reply predicted beyond the run.

The figures and the recorded prompts are unchanged; the codex-2 fix yields
byte-identical prompts for all 46 sections. The fixed bytes have not been
re-reviewed.

## Refactoring review

None needed. LR3 adds a module, a fixture and a tool, and changes no
existing code. One observation goes to the milestone close: the scorer reads
`payload-1.json` and `payload-3.json` by name. A public `reading` accessor
for a run's attempts would serve it and the assurance scorer alike. That
belongs to `reading.py`, which has its own writer.

## Boundary: what this phase does NOT establish

- Any figure for real papers, other models, other prompts or other settings.
  The set is 12 short synthetic paraphrases.
- Comparability with #226's figures, which scored quotes. LR3 scores at
  section grain, and the page says so.
- Model determinism. The run was recorded once and replays; a new live run
  could differ.
- The labels are one author's (`answers/README.md`: not independent ground
  truth).
- The review-fixed bytes are unreviewed.

## Open questions

- A public run-attempts accessor in `reading.py` (above). Target: a later
  literature milestone, owner's choice.
- Re-recording after PR 245: not needed by the evidence; the owner's call.
