---
milestone: model-growth-guardrails
station: milestone-close
skill: "n/a -- repository development under process-milestone auto=true (from MG3), not a gnd-solve station"
scope: MG-close
date: 2026-11-04
source_base: 9b069e2
gate:
  command: "bash .gnd-planning/milestones/model-growth-guardrails/evidence/close/close-gate.sh"
  exit: 0
  output: "3897 passed, 72 deselected in 578.14s; 267 tutorial blocks passed; strict build; 13393 links; ruff clean"
  note: >-
    The union of the six phase gates and their impact closures, the docs
    gates and ruff, over the final closing tree (b213b08). The IL6 census
    runs after the commit by design: 9 passed.
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "the broad historical lanes are outside the milestone's impact closure"
evidence:
  - path: .gnd-planning/milestones/model-growth-guardrails/notes/model-growth-guardrails-plan.md
    sha256: 7f502d102cae2c261b34ab284e2337bc947aad131ddd665cc07751d3a4d4a339
  - path: .gnd-planning/milestones/model-growth-guardrails/notes/close-review-reader-1.md
    sha256: ea178d067194f472f6ebfd6450fc12057e49049628397d466bd9d1cf065e206e
  - path: .gnd-planning/milestones/model-growth-guardrails/notes/close-review-reader-2.md
    sha256: 39197febcd24806a8cf168fa50d3ab62c79fa848a61c8ca306b50c0b1e50f07a
  - path: .gnd-planning/milestones/model-growth-guardrails/notes/close-review-reader-3.md
    sha256: 2d6bdab9a9db353eea49a0020b044f00da62a6cd3acba58d568efa41488e3d89
  - path: .gnd-planning/milestones/model-growth-guardrails/notes/close-review-reader-4.md
    sha256: ef6bd1e4932ec83b8539babdfe19c7cf9e97e0012b322d93ec218c5f0c1624c7
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/close/mutants.json
    sha256: 7ffbf00b16f51fedba4d1838ddf10f9bf3c8e0babf79b1c6977dcefa1ec4c59d
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/close/mutants-results.txt
    sha256: 85d17418c6f7385751348127dfc4ac4afcf7f3a85d041bbc1b0cc734bcd54d94
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/close/parity-evolve.json
    sha256: 8abffb5bc88ed2b64c2ccdfa60b2c1f7be65c1ec457f6c28e1df849dd8bac88f
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/close/parity-extract.json
    sha256: 6e401cd813697a84973e50d068398804e0808d46b1297cc6761e1350b191f07a
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/close/parity-validate.json
    sha256: bde9366ba6b0aaa11d52d84f0981ec522a59434e251253be9da3f16b408cd16b
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/close/dynamic-query-successor.json
    sha256: 9cccff8542d47a3bd2c6c84d167c7e2e4b299ecb10af4d1459f108a699b5c1ee
  - path: .gnd-planning/milestones/model-growth-guardrails/notes/phase-MG3-claude-review.md
    sha256: 8385a3c89adfc4559b1ca9ad4d07eb88e62aa5371eba7bcd7d310bb5807c7636
  - path: .gnd-planning/milestones/model-growth-guardrails/notes/phase-MG5-claude-review.md
    sha256: 1c5404ca76d4c99f449a2606fecfeaaff268ae68fa003396901f382dfb6daf85
  - path: src/gnd/evolve/policy.py
    sha256: 15907e6fee15a8a9c921d65bf3c7509715b190d5fe0e60f0a516104ded9d3bfd
  - path: src/gnd/evolve/shapes.py
    sha256: 6d9bb573a57cfd1e13a219f7683f8ec310fddf45c20b5447b79dba7cfafb314b
  - path: src/gnd/extract/guidelines.py
    sha256: c8b3d68bc339c7f7eb7f5bf55801ae4b9b190983e3155112969aec00350dccfe
  - path: src/gnd/model/_validation.py
    sha256: 150d09f9604b4bd94bfa7c90c8a4614bd58ec7083a61d6f9b673945437027b5d
  - path: src/gnd/commands/checking.py
    sha256: 2e74fee2d0ed2a8ab659fca85c2794bb766fb2c27ac8c332c861ee3b74824183
  - path: src/gnd/commands/extract.py
    sha256: 7a01070c5168af699fdf26ac7aaea2ee6ed4f7d0c0d3871055e2656e25856c4e
  - path: src/gnd/refscheme.py
    sha256: 8a94071f3585e93344e678cb612e97c5b4929ca2ac39caf6c4d2633f0e85ac4e
  - path: src/gnd/schema/orm-meta.schema.json
    sha256: eb626252f7eaf5ce8dc2580b9b387289a46d66da923358d2a4fcbb4a81292353
  - path: docs/release-notes.md
    sha256: 2ed1b6b41674ba709f8cf4ca8365721fca486beabd1ffc1161242766a22fd35a
  - path: docs/how-to/grow-a-model.md
    sha256: a6e565efd06f9d9efe7e3f1b2b388270324c7b7fff337795a3c108a54e8bd08e
  - path: tests/support/pyrel_application_successors.py
    sha256: bb320913b41b0704dea70d0f9061c160eb7db83cd00c54c2e99a01a3cee76c1e
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/close/close-gate.sh
    sha256: 2728baf8742e62b08f8febbf3ec16e66356ae59c77895d25eead0c188d0c7f13
  - path: .gnd-planning/milestones/model-growth-guardrails/evidence/close/close-gate.txt
    sha256: 9151bdc5fdc259e9de1b2af9a72a15ae3241396a60ced83ac0825e825f15af2e
---

# Model growth guardrails -- milestone close

**Claim.** The five requests of issues #72, #74, #75, #76 and #78 now live
in GND: rule read-back (`gnd.api.verbalize_rules`), the additive evolve
policy, the duplicate-shape report, extraction guidelines and the
unattended source mode, each behind an opt-in option or mode, with GND's
existing refusal and exit conventions. Without the new options, and for
models without `source.mode: unattended`, previews, applies, extract
bundles and validation results over the corpus are byte-identical to
`9b069e2` (one stated exception, MG1's fix for inputs that used to raise).
The close gate exits 0 after the close-review fixes.

**Authority.** Plan r3 approved by the owner `(a1)`. MG1 and MG2 ran
`auto=false` with owner gates `(s1)`. From MG3 on, the owner's
"process-milestone model-growth-guardrails auto" (2026-11-04) delegated
spec, amendment and close rulings within this milestone; every such
ruling is recorded as a **delegated approval (auto=true)**, an agent ruling,
never the owner's reading. Close review instrument: four local readers
(MG-D1 `(o1)`, confirmed at the plan gate).

## Phase records

| Phase | Record | Commit | Focused gate |
|---|---|---|---|
| MG1 rule rendering | [002-phase-MG1.md](002-phase-MG1.md) | `92dc3f8` (PR #81) | 701 passed |
| MG2 additive policy | [003-phase-MG2.md](003-phase-MG2.md) | `d8e8a3a` (PR #82) | 1895 passed |
| MG3 shape report | [004-phase-MG3.md](004-phase-MG3.md) | `41be029` | 1941 passed |
| MG4 guidelines | [005-phase-MG4.md](005-phase-MG4.md) | `9e36e70` | 1533 passed |
| MG5 unattended mode | [006-phase-MG5.md](006-phase-MG5.md) | `7961119` | 3006 passed |
| MG6 documentation | [007-phase-MG6.md](007-phase-MG6.md) | `2ed15f8` | docs gates, 127 passed |
| close fixes | this record | `60b6f79`, `b213b08` | the close gate |

Each phase had one independent diff reviewer (one reviewer is one
reviewer); every finding is dispositioned in its spec.

## Completion predicates

| # | Predicate | Result |
|---|---|---|
| 1 | `verbalize_rules` renders every structured rule as the full verbalization does, reports prose as `unsupported`, other fallbacks unreachable, path crash fixed | holds (MG1). Reader 2 re-checked 108 models and 280 rules: 0 misses, 19 prose |
| 2 | `--policy additive` refuses and admits per §2.2; apply repeats and re-runs; flag-free parity | holds after the close repair of MG-D17 (reader 1 F1: object-scoped constraints were admitted on populated data; now refused, cases and mutants C1, C2). Constraint RENAME cells are pre-empted at read (MG2-Q2). Parity over the eight evolve fixtures byte-identical at the close (`evidence/close/parity-evolve.json`) |
| 3 | `--shape-report` deterministic, never refusing, flag-free unchanged | holds (MG3, group layout `(d2)`); reader 1 found MG-R4 equal across 255 models |
| 4 | `--guidelines` artifact digest-recorded; flag-free bundles byte-identical; constraint-blind | holds (MG4); close parity over 238 extract models unchanged, one new fixture row. The identifying external uniqueness is reference content, stated in the docs |
| 5 | unattended mode refused per §2.5; corpus validates as before; skill documents the mode | holds (MG5), with the close repairs: no MG-R1 exception (reader 4 F1, induced spans refused outside the mode), U8 over obligations (reader 3 F2), near-miss spelling warns (reader 3 F1). Close parity over 322 validate models unchanged; reader 3 also checked the 27 models under `src/gnd/examples` against `9b069e2`: identical |
| 6 | every page dispositioned, docs gates 0 | holds (MG6), with the disposition rows reader 4 F5 found added below |
| 7 | focused gates, diff reviews, sweep, PR | holds: six phase gates, six diff reviews, four close readers, this close gate, the sweep below and the PR. **Owner acceptance is separate and pending** |

## Close review (four local readers, MG-D1)

[Reader 1](notes/close-review-reader-1.md) (policy and shape report),
[reader 2](notes/close-review-reader-2.md) (rule rendering and guidelines),
[reader 3](notes/close-review-reader-3.md) (unattended mode as a security
control, disclosure), [reader 4](notes/close-review-reader-4.md) (protocol,
evidence, records). All four approve-with-fixes. Two blocking findings, both
fixed with regressions and mutants.

| Finding | Severity | Disposition |
|---|---|---|
| R1-F1 object-scoped model-hosted constraints admitted on populated data | blocking | fixed: the subject rule includes fact types the object type, a subtype or an identified entity plays in; plan close note repairs MG-D17 (delegated); cases and mutants C1, C2 |
| R1-F2 a re-added id reported its first ADD's index | completeness | fixed: last ADD; case and mutant C6 |
| R1-F3 parity baseline `d5f6e9e` for `1446f90` | completeness | stated in the plan close note; evolve code unchanged between them |
| R2-1 the guideline did not print the reference mode | completeness | fixed: `- Reference mode:` for entities; composite components not listed (MG-close-Q2) |
| R2-2 extract help and SKILL said four files | completeness | fixed; RF1 goldens for `gnd extract` recaptured under py311/313/314 |
| R2-3 docs omitted the identifying external uniqueness | completeness | fixed on three pages |
| R2-4 a proposed external uniqueness prints as identification | hardening | inherited from the verbalization; MG-close-Q3 |
| R2-5 derived fact types not marked | hardening | fixed: `- Derived by a rule: not extracted from documents` |
| R2-6 raw HTML passes through | known | MG4-Q1 |
| R3-1 a near-miss mode spelling switches the rules off | hardening | fixed: a `semantic:unattended-u1` warning; mutant C5 |
| R3-2 alethic obligations pass | hardening | fixed: U8 walks every provenance-bearing element; mutant C4 |
| R3-3 `rejected_proposals` may claim a human | hardening | MG-close-Q4 (inactive claims) |
| R3-4 `--document` may check nothing and exit 0 | hardening | MG5-Q3 |
| R3-5 parity table missed `src/gnd/examples` | completeness | reader 3's comparison (identical) cited in predicate 5 |
| R3-6 / R4-F1 MG-R1 exception taken without an owner ruling | blocking | fixed in code: the exit is 3 again outside the mode (case and mutant C3); no exception remains |
| R3-7 MG-R5 wording versus a per-command table | completeness | stated: the disclosure table rows are per leaf command; every new option is on a leaf that has its row, and no new message carries a value or document text |
| R3-8 three branches tested only at the rule | completeness | accepted: reader 3 confirmed the operation and induced cases end to end |
| R4-F2 local paths in committed evidence | hardening | sanitized to `<repo>`, `<scratch>`, `<home-path>`; the MG3 and MG5 review notes and MG3 probes therefore differ from the digests their records cite (stale by design; current digests below) |
| R4-F3 pre-tag approval digests unverifiable; `(d2)` names no digest; MG6 budget | hardening | accepted and stated: the approved-bytes digests are of the spec before its own approval tag, which was never committed separately; `(d2)`'s bytes are those of the committed MG3 spec |
| R4-F4 mutant results not committed | hardening | `evidence/close/mutants-results.txt`: 36 mutants over MG3, MG4, MG5 and the close, all killed, with bytecode disabled |
| R4-F5 disposition table misses five files | completeness | below |
| R4-F6 PR, DC1/DC2, question rows, stale plan lines | completeness | PR opened; DC1 missed, DC2 owner viewing pending; the sweep below; the plan close note |
| R4-F7 record text: "87 cases" (80 collected after the close), MG6 spec build-script path, README pending line, the IL6 patch in MG4 | completeness | corrected here: records are append-only; the build script is `tools/build_growth_example.py`; README updated |
| R4-F8 one commit subject over 65 characters; noun-phrase subjects | completeness | accepted; history is not rewritten |

**Additional disposition rows (R4-F5)** for the MG6 table: the
`gnd-model-from-code` SKILL.md and `references/recovery-contract.md` name
`evolve` as the next station only (no change); `gnd-orm-core/references/
constraint-inference.md` and `halpin-posture.md` name One-shot as a dialogue
mode (no change, MG-D10); `gnd-orm-core/references/orm-meta.schema.json` is
the schema twin (changed in MG5, sync-pinned).

## Close gate

| Command | Result |
|---|---|
| `bash evidence/close/close-gate.sh`: pytest over the union of the six phase gates and their impact closures (the file list is in the script) | `3897 passed, 72 deselected in 578.14s (0:09:38)`, exit 0, no failure |
| `uv run python tools/run_tutorials.py` | `267 tutorial blocks passed` |
| `uv run --group docs zensical build --strict` | no issues |
| `uv run python tools/check_docs.py site` | `13393 local links/assets/anchors checked` |
| ruff over the changed source, tests and tool | `All checks passed!` |
| `tests/test_il6_skill_census.py` after `60b6f79` | `9 passed` (it reads committed skill bytes, so it fails on an uncommitted skill edit by design) |
| close parity: evolve, extract, validate captures | evolve byte-identical to `9b069e2`; extract and validate identical on every pre-existing model, one new fixture row each |
| mutants, `PYTHONDONTWRITEBYTECODE=1` | 36 of 36 killed (`evidence/close/mutants-results.txt`) |
| anonymity scan over the milestone diff | 0 matches |

An earlier run of the same gate, before `b213b08`, reported `5 failed`: three
IL6 census tests (uncommitted skill edits) and two RF6 census tests (the
R1-F2 change post-dated the close successor). Both were fixed; the run above
is on the final bytes.

## Question sweep

| ID | Question | Disposition |
|---|---|---|
| MG1-Q1, MG1-Q2 | fallback reachability; root aggregate with clauses | resolved in the MG1 spec r2 |
| MG1-Q3 | merge `_run_verbalize`'s `failure` closure with the module helper | deferred to a later refactoring pass touching `api.py` handlers (owner) |
| MG1-Q4 | re-validation cost of `render_rule_verbalizations` | accepted residual |
| MG2-Q1 | `--policy` plus `--shape-report` applies | resolved (MG3 T5) |
| MG2-Q2 | constraint RENAME cells pre-empted | resolved: plan close note |
| MG2-Q3, MG2-Q4 | merge before-model walks; RF6 headroom | resolved (MG3 D4; 364 of 365 at the close) |
| MG3-Q1 / NM2-Q3 / O23 | RF1 fresh capture drifts in about 60 unrelated goldens | deferred to a maintenance pass (owner); each phase took only its own goldens and recorded it |
| MG3-Q2 | a proposal of only ADD/DELETE pairs fails `BlastRadiusReport` (`too_short`) | deferred: a defect independent of this milestone, for a follow-up issue (owner) |
| MG4-Q1 | escape raw HTML in guideline descriptions | accepted residual: the file is documented as plain text, not to be rendered |
| MG4-Q2 | `reference_identity` cost with many external uniqueness constraints | accepted residual; shared with the flag-free verbalization |
| MG5-Q1 | `--document` re-hash cost per full-length span | accepted residual (bounded by the 10 MiB cap) |
| MG5-Q2 | schema for the unattended `source` keys | accepted: the semantic rule is the header rule's one home |
| MG5-Q3 / R3-4 | report spans over unsupplied documents | deferred (owner): an output change for a later pass |
| MG6-Q1 | `verbalization-patterns.md` CSDP header lists `guided\|one-shot` | deferred to a docs maintenance pass (pre-existing; also misses `mvp-fast`) |
| MG-close-Q2 | composite identity components in the guideline | deferred (owner) |
| MG-close-Q3 | a proposed external uniqueness shown as identification | deferred (owner); inherited from the verbalization |
| MG-close-Q4 | `rejected_proposals` claiming a human in unattended mode | deferred (owner); rejected claims are inactive |
| O20 | a description can restate a constraint | resolved: documented (MG4 contract §4a) |
| O21 | a description can forge a role line | resolved (MG4 T4) |
| O22 | `apply` rewrites as one-line JSON | refuted (MG6 R-F1); plan close note |
| O26 | visible checkpoints | DC1 missed; DC2 retained, owner viewing **pending** |
| O27 | reporter acceptance | carried to the reporter, after merge; no issue comment is posted without the owner |

## Refuted premises

- §2.2's subject rule for model-hosted constraints missed object-scoped
  families (reader 1 F1); repaired.
- §2.3's per-ADD layout is quadratic (MG3 R-F1); repaired by `(d2)`.
- MG5's "one MG-R1 exception" was avoidable; the exit is restored.
- O22 (MG6 R-F1).

## Boundary -- what the milestone does NOT establish

- **Owner acceptance, merge and the DC2 viewing are pending.** No merge,
  release, publication or certification is claimed.
- **The broad historical lanes** (`-m "evidence or census"`) did not run.
- **Each phase review is one reader**; the four close readers read the tree
  at `2ed15f8`. The close fixes carry no review opinion.
- **A shape match is a candidate**, never a duplicate verdict; **a span
  proves an excerpt exists**, not that it supports the claim; **the
  guideline digest is recorded, not verified**.
- RF1 goldens were updated by hand-selected files because a fresh capture
  drifts (MG3-Q1).

## Delegated close ruling

**Delegated approval (auto=true)**, 2026-11-04, under the owner's
"process-milestone model-growth-guardrails auto": the milestone is closed
locally on the evidence above, with the plan close note `(c1)` (plan SHA-256
in the evidence list) and the question dispositions above. This is an agent
ruling under the delegation, not the owner's acceptance. **Merge, owner
acceptance and the DC2 viewing remain the owner's.**
