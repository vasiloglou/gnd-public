# Plan review -- round 1 disposition

2026-11-03. Instrument: four local reviewer agents (MG-D1 and CT-D1, ruled
`(o1)` for plan review). One round covered both milestones; the
[composition-and-type-induction disposition](../../composition-and-type-induction/notes/plan-review-r1-disposition.md)
points here. The instrument choice approves no plan or spec bytes.

## Subjects and limits

| Subject | SHA-256 | Retained snapshot |
|---|---|---|
| MG plan r1 | `32a851f0e7e935e149b14b3999e7ba303a3c770ed72d90c9a76169451681759c` | `evidence/plan-review-r1/model-growth-guardrails-plan.md.snapshot` |
| MG1 spec r1 | `d44bf94e68556bc4095d3291175bafb89b75f55343e27d8d40b8cafc8cd73dc6` | `evidence/plan-review-r1/phase-MG1-spec.md.snapshot` |
| CT plan r1 | `48430d1a317c11ee2be83d0d35876fb5c80e22e5d9e7bb678b3bd233c420fa49` | `../composition-and-type-induction/evidence/plan-review-r1/composition-and-type-induction-plan.md.snapshot` |
| CT1 spec r1 | `51dd694817fee77650a1154c70865dfad0dd29ee7f339fa54a38c9813a035bb0` | `../composition-and-type-induction/evidence/plan-review-r1/phase-CT1-spec.md.snapshot` |

All four readers verified all four digests. They ran concurrently as local
model agents with fresh context and one lens each. They used no paid tools or
credentials, and their only network reads were `gh issue view`. Probes ran
only in the session scratchpad. No reader wrote to the repository: after all
four returned, `git status` showed only the coordinator's planning files.

## Opinions

| Reader | Lens | Verdict | Blocking | Hardening | Completeness |
|---|---|---|---|---|---|
| [1](plan-review-r1-reader-1.md) | correctness against production semantics | request-changes | 5 | 5 | 2 |
| [2](plan-review-r1-reader-2.md) | implementability, pins and homes | request-changes (CT1 approve-with-fixes) | 3 | 6 | 5 |
| [3](plan-review-r1-reader-3.md) | protocol, authority, compatibility, privacy, docs | request-changes | 1 | 5 | 7 |
| [4](plan-review-r1-reader-4.md) | test design, falsifiability | request-changes | 6 | 7 | 3 |

Total: 55 findings, 15 marked blocking. They collapse into **10 distinct
blocking themes (A–J)** and 13 hardening or completeness themes (K–W). None
was refuted.

## Coordinator reproduction

Run from the repository root at `1446f90`:

- `evolve/service.py:1263-1267`: preview refuses any proposal not at
  `EVOLUTION_SCHEMA_VERSION`. `evolve/models.py:792`: "preview and proposal
  versions must match". `:817-819`: `preview_sha256` is `canonical_sha256` of
  the body, recomputable by anyone. Confirms theme D.
- `anchors.py:70-72`: `sidecar exceeds 1 MiB`. Confirms theme H.
- `schema/orm-meta.schema.json` `$defs.object_type` and `$defs.fact_type`
  have no `source` property and `additionalProperties: false`. Confirms
  theme G.
- `render_model_verbalization("tests/fixtures/v62-phase4/models/aggregates.orm.yaml")`
  raises `AttributeError: 'str' object has no attribute 'get'`. Confirms
  theme B.
- MG1 T3's end-of-line claim contradicts `model_verbalization.py:567-574`
  (three readers, one reproduced over 98 rules). Confirms theme A.

## Themes and proposed repairs

"Owner" marks a decision the plan author must not make.

### Blocking

| Theme | Findings | Defect | Proposed repair |
|---|---|---|---|
| **A** | R1-F1, R2-F1, R4-F1 | MG1 T3 cannot pass (the line continues after the rule and passes through `line_text`), and its loose substring form cannot fail on a truncated rendering. | `text` is `line_text(_derivation_cnl(rule, model))`. T3 asserts the fact-type line contains `"This fact type is derived: " + text` followed immediately by ` Admission depends on`, a redaction sentence, or ` reading=`. Add a truncation mutation control and a control-character constant case. |
| **B** | R2-F2 | `render_model_verbalization(path)` crashes on structured aggregates, because the raw path reaches `analyze_declared_aggregate`. Five corpus models are affected, three of them packaged examples. | Proposed: MG1 fixes the shared path (coerce once, pass the loaded model down). No digest moves, since that input crashes today. Recorded as a finding with a path-input case. **Owner** may carry it instead. |
| **C** | R1-F4, R2-F5, R4-F2, R4-F3 | The MG1 branch table misses a non-dict atom, a non-dict `aggregate`, the `date_add` unpack and a non-dict `head`, and the root-key paths are wrong. MG1-Q1 is left to the implementer, though reader 4 shows the schema refuses three mutations. D6 has no test row. | List every fallback and raising path. Each one validation forbids becomes a falsifiable "refused by `load_model`" test, and MG1-Q1 is settled in the spec. Root keys copied into clauses report `/derivation_rule/<key>`. D6 gets a T row with one expected outcome, fixed before the gate. |
| **D** | R1-F5, R1-F6, R2-F3, R4-F6 | Preview, proposal and finalize versions are tied, so a "new preview version" breaks v3 apply. The policy lives in a preview whose digest anyone can recompute: deleting `policy` applies as a no-policy preview. MG2-C3's tamper case is caught by the digest check, not by the re-run. | **Owner.** Readings: (i) proposal v4 carries the policy and the reviewer approves it by digest; (ii) separate preview and proposal versions; (iii) **proposed:** v3 stays. New preview fields are optional and omitted when unset, so old bytes are unchanged. `apply` must repeat `--policy additive` and `--populated`, and refuses when its policy differs from the preview's in either direction. Tests: a digest-consistent preview the re-run rejects; a policy-stripped preview applied with `--policy` (exit 3). A refusing preview still writes its document. |
| **E** | R3-F1 | `shape_matches` has no option, so every preview with a fact-type ADD changes, contradicting MG-R1 and predicate 2. | Proposed: behind `gnd evolve preview --shape-report`, an optional preview field under theme D (iii). **Owner** may instead accept the change for all previews, with a migration note. |
| **F** | R4-F5, R4-F7 | §2.2 misses a role ADD on an existing fact type (already gated, `service.py:634-637`), `ModelIdentityLocator` MODIFY and the `operations` collection. "One case per class" lets one RENAME cover four locators. `proposed`→`confirmed` is both a D3 strengthening and a D5 provenance edit. Gate order (exit 18 vs 3) is unpinned. | §2.2 becomes an operation-kind × locator-kind matrix with one case per cell, plus a two-fault order case. D5 is narrowed to description and rationale text. **Owner:** confirming an existing constraint counts as strengthening (proposed: yes, refused on populated fact types). |
| **G** | R1-F7, R3-F4, R4-F13 | Object types and fact types have no `source`, so MG5's span rule selects only constraints and leaves "every elementary fact" ungated. `explicit` requires `confirmed` (`_validation.py:884`), so it is impossible in unattended mode. D-03 is only a warning and does not cover `sample`. | **Owner.** Proposed: spans are required on every object type and fact type unconditionally, and on each `sample_population` row. `explicit` and `user-supplied` are refused in unattended mode. In this mode the D-03 warning becomes an error and extends to `sample`. C2 is spelled out as a refusal matrix. C3 gains a passing re-hash and an out-of-range span. |
| **H** | R1-F9 | CT1's 10,000 anchors exceed the 1 MiB sidecar cap (5,000 parse; 7,000 are refused). | Use 4,000 anchors on one role, measured below the cap. The cap is unchanged. |
| **I** | R4-F9 | A JSON Schema cannot express per-key uniqueness or `start < end`, so CT1 T11 ("schema and parser agree") fails or needs a silent exemption. | List the parser-only rules (uniqueness, span order, version-dependent duplicate identity) and assert that schema and parser disagree on exactly those cases. |
| **J** | R1-F12, R2-F10, R3-F2, R4-F12 | CT §2.2 and CT2-C4 refuse cross-source functional conflicts with exit 3, while CT-D4 proposes (b): compose, and let check report. | **Owner** rules CT-D4. Proposed (b): §2.2 and CT2-C4 rewritten so composition succeeds and `gnd check` reports the violation with lineage. |

### Hardening and completeness

| Theme | Findings | Repair |
|---|---|---|
| K | R1-F3, R2-F4 | MG1 payload uses `exit_code` and the `error` object. A malformed `fact_types` raises `TypeError`, like other `gnd.api` functions. D1 is reworded. |
| L | R1-F8, R2-F7, R3-F5 | Paths: `src/gnd/schema/orm-meta.schema.json` with its twin `skills/gnd-orm-core/references/orm-meta.schema.json`; `src/gnd/refscheme.py:97`; witness schema twin `skills/gnd-export/references/witness.schema.json` and `witness-contract.md`. "SKILL.md twins" is replaced by the real schema twins. MG4 amends `gnd-extract/SKILL.md:41,63`. MG5 routes the skill to `gnd validate`. `EXPECTED_SKILL_FILES` is named. MG-D7 pins the `primitive` variant. |
| M | R1-F2, R4-F4a | The MG1 corpus is every `*.orm.yaml` and `*.orm.json` that `load_model` accepts. Recorded floor: 118 models, 301 rules, 19 prose; construct floors asserted. |
| N | R3-F6, R3-F7, R2-F12 | Gates list test files explicitly: `test_model_evolution.py`, `test_evolution_conformance.py`, the `test_public_*evolution*` files, and `tests/test_rf1_cli_pins.py` wherever a CLI changes. Disclosure leaf counts (`test_disclosure_mode.py:218,498`) are named for CT2. Docs page is `docs/reference/python-api.md`, with its count line at `:9`. A new Unreleased release-note entry replaces editing `:56`. `__all__` tail order: MG1's name, then CT2's. |
| O | R2-F6 | Model reads go through `ModelIndex.iter_fact_types_shared`. CT1 states its RF6 row move in `code-refactoring/evidence/RF9-repair/query-allow-list.json` as a recorded, count-preserving change. |
| P | R1-F10, R1-F11, R2-F13, R4-F10, R4-F11 | CT1: at most one failed entry per (row, role), as today. The lexical index requests a set of occurrences. T12 expects distinct excerpts per role. The top-level key check stays first (rule 3 restated). Size is 120. T3 uses two bad anchors. T8 uses 1,000 rows × 4 anchors and counts key lookups. T5 puts the max-occurrence anchor first. D2 gets "same span, different occurrence" (accepted) and "same identity, different `excerpt_sha256`" (refused as a duplicate). T7's comparison lives in `evidence/CT1/`. |
| Q | R4-F4c, R4-F8 | Time bounds count comparisons, bucket probes, dedupe probes, fact-type visits and index constructions, not calls. MG3 pins (A,A,B) vs (A,B,B) and says whether two identical ADDs match each other (proposed: yes, reported). |
| R | R4-F16 | Parity claims use a recorded before/after digest table over the corpus (previews, bundles, validation results, verbalizations), stored in each phase's evidence. CT3-C2 states the replay mismatch exit. |
| S | R4-F14, R3-F8 (IK1-Q4), R4-F4b | MG4: nothing reads the guideline digest today, so the claim becomes "recorded and verified by `gnd extract --verify-bundle`"; otherwise it is downgraded to "recorded". **Owner** picks; proposed: downgrade. The injection test covers value constraints and every constraint kind. Descriptions are escaped, with a structure test against forged role lines. MG1 T5 gains a positive subset, out-of-order ids, `[]`, duplicate ids and an invalid model. |
| T | R1-F12b, R2-F8, R2-F9, R3-F10, R3-F11 | CT2: each composed fact is checked as source value against source span in the source document, which needs a named `_core` change. The record refers to renamings by manifest index and is value-free. `gnd compose` and `api:compose` are `value-free` disclosure rows. Refusal messages never quote values. CT3 introduces witness version 2, plus `--composition` on `gnd witness` and `api.witness`. Souffle witness and why-not consumers are listed. Sidecar v2 through `gnd.api` (`api.py:801`) is listed in CT §5. The writer is `write_anchor_sidecar` in `gnd/anchors.py`. |
| U | R2-F11, R3-F3, R3-F12, R4-F15 | **Owner** on CT-D9. Proposed (b'): the migration report carries a SHA-256 of the attribute value, and the raw value appears only with `--show-values` under `internal` disclosure. Under `customer` it is refused. CT4 scope: fact types from attribute names only; object types and relation names are scoped out in §7. MG-D7 states that "compatible reference modes" is read as exact reference identity. CT4 fixtures for rows vs distinct entities, an undeclared generic shape, a canary scan over proposal bytes, and suppressed vs proposed string attributes. |
| V | R3-F8 | Inherited rows added with dispositions: IK1-Q4 → MG4 (theme S); IK close "Reader four" → the MG6 how-to notes it; NM2-Q3 → each RF1-golden-changing phase recaptures and records; IKE-Q3 → CT4 handles `ArtifactError`. |
| W | R3-F9, R3-F13 | The MG1 spec binds MG-R8; the CT1 spec binds CT-R3..R7, CT-R7 with a sentence on `gnd check --anchors`. The CT §8 stop rule is written in its own bytes, and MG §8 adds the same-seat trend. MG-D5 (b) and MG-D7 (a) state their costs. The README next action is updated. |

## Stop rule for round 2

Declared before round 2: at most one more plan round, a confirmation round
over r2 restricted to the blocking themes. Stop after it, or earlier if the
self-inflicted ratio (round-2 findings attacking text r2 created, over all
round-2 findings) exceeds one half.

## Owner decisions requested

| Theme | Question | Proposal |
|---|---|---|
| B | Fix the existing path crash in MG1, or carry it | fix in MG1 |
| D | Where `apply` gets the policy; version scheme | (iii): optional v3 fields; `apply` repeats `--policy` and `--populated` |
| E | Shape report behind an option, or for all previews | option `--shape-report` |
| F | Is confirming an existing constraint a strengthening? | yes |
| G | Span scope and strictness in unattended mode | every OT/FT and sample row; `explicit`/`user-supplied` refused; D-03 an error, including `sample` |
| J | CT-D4 | (b): compose; check reports |
| S | Guideline digest verifier or "recorded" | "recorded" |
| U | CT-D9 | (b'): value digest in the report; raw value only with `--show-values` under `internal` |
