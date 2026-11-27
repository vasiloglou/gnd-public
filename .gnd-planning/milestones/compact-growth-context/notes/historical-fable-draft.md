## Historical draft reviewed by Fable

**Draft for owner review, 2026-11-27, based on GND 6560f440.** The plan panel has not run. The owner requested milestone design and has not selected a review instrument or approved implementation. Default delegation is off.

**Goal.** A host can give its grower a reproducible, compact inventory of the composed model. When the inventory exceeds the host's prompt budget, the host can ask GND for a bounded set of relevant existing elements, see exactly what it supplied, and resolve proposed IDs against the full snapshot before evolution. A separate evaluation determines how well a host finds claims throughout a document.

**Completion.** A fresh installation renders complete and bounded views for an include-backed example. Independent processes reproduce the bytes. The ordinary verbalization and existing growth gates retain their contracts. The guide explains both prompt forms and their limits. Quality claims have occurrence-level evidence; a failed quality gate leaves the corresponding strategy experimental.

## 0. Binding design rules

Use the composed model loader, ModelIndex and registered constraint-family semantics. Keep one projection shared by the complete and bounded routes. Preserve role order and identity. Allowlist prompt fields; source evidence belongs to the host and validator. A missing candidate licenses a full-index lookup or deferral. Only the existing additive evolution route can write. Keep default installation and normative tests credential-free.

## 1. Scope, sources and obligations

| Source and status | Obligation | Owner and evidence |
|---|---|---|
| [Issue 295, request 1](https://github.com/vasiloglou/gnd-public/issues/295), product request | Complete deterministic rendering including included IDs, roles, subtypes and constraint signatures | GC1 projection corpus; GC2 installed CLI/API byte parity |
| Issue 295, requests 2–3 | Document what the grower sees, how to handle omitted elements and how to act on shape matches | GC3 omission receipts; GC4 packaged host example and guidance |
| Issue 295, reporter's 200-round figures | Distinguish schema context bytes from total host tokens and inference cost | GC2 reports exact compact/full bytes on generated snapshots; GC5 reports whole-run accounting |
| Unattended growth guide, “What one round is”; UG close §Boundary; MG and GO close records | Reuse by ID, source validation, population checks, additive preview/apply and truthful round outcomes | GC4 exercises these existing contracts |
| EXP-295 and EXP-299 conclusions, local observations | Graph neighbors sometimes recover omitted IDs; bounded selection can still miss most matches | GC3 lexical rank plus typed neighbors, explicit budgets and deterministic fallback |
| EXP-298 and EXP-300 conclusions, local observations | Pilot with supplied matches scored 20/22; ordinary hybrid and lexical plus graph both scored 2/22. Only 178/19,954 reusable mentions overlapped the four chosen passages per paper | GC5 measures discovery and selection separately; dense retrieval has no production dependency |
| EXP-300 occurrence audit | Same-occurrence replay yielded five correct lexical reuses, two hybrid, zero fully bound facts in either arm | GC4 requires role-specific evidence and deferral; GC5 owns occurrence-level reporting |

The 48 historical rounds and eight-paper pilot are development evidence. The 48 rounds include the pilot papers. An experiment-claim census cannot establish installed framework behavior. Product acceptance uses distributable fixtures and fresh evaluation material.

## 2. Product contract proposed for approval

- **Complete view.** Proposed CLI `gnd verbalize model MODEL --for-growth` and API `gnd.api.verbalize_model(MODEL, for_growth=True)`. Emit versioned canonical UTF-8 JSON. The prompt-visible text excludes evidence, sample values and rationale. A host can hash exact returned bytes and retain the full pre-round model identity separately. Evidence-only edits may leave the view digest unchanged.
- **Bounded view.** Proposed library entry `growth_candidates(model, *, passage, kind, limit=5, max_bytes)`. Query the full composed snapshot. Return numbered IDs, ordered role signatures, supporting typed neighbors within budget, total and shown counts, completeness, canonical view digest and an explicit budget outcome. The byte limit covers the entire serialized packet including its envelope. Refuse an impossible envelope budget. A host wanting provider token limits must measure its final serialized prompt with its own tokenizer.
- **Host decisions.** Candidates reference the snapshot and exact document occurrence. Host records reuse, propose-new, or defer. For a fact, check named roles, direction, units, conditions and the occurrence supporting each argument. A span containing every value may still describe a different relation. A larger lookup precedes a novelty proposal after a subset miss. Ambiguous equivalence goes to open questions. No library call in this milestone autonomously mutates the model.

## 3. Dependencies and homes

Start with `src/gnd/model_verbalization.py`, `model_index.py`, `api.py`, `commands/checking.py`, the composed loader and the family registry. New projection/retrieval code belongs below API and CLI. Register new modules in `tools/gnd_layers.json` and the component inventory. Reuse the existing additive gate and source locator. Historical experiment scripts remain evaluation references. Their private data, model weights and temporary paths cannot be runtime inputs.

## 4. Phases and exit criteria

| Phase | Depends on | Deliverable and falsifiable exit |
|---|---|---|
| GC1 · Complete projection | Plan and phase approval | One composed model produces stable version-1 bytes with all expected object, fact, subtype and constraint signatures; evidence sentinels never appear. See first spec. |
| GC2 · Product entry points | GC1 | Existing command keeps its original bytes; new CLI and API produce identical view bytes across processes and on an installed wheel. Record size at 1×, 2× and 4× schema size and verify evidence-only growth does not enlarge the rendering. |
| GC3 · Bounded retrieval | GC1–2 | Index the complete view once per schema snapshot; query by passage, lexical relevance and typed neighbors. Deterministic ties and complete packet size obey the declared cap. Fixtures force a useful neighbor, a dropped dependency, an empty retrieval and a stale-snapshot rejection. |
| GC4 · Grounded host integration | GC2–3 | Ship a two-round include-backed example and update the packaged guide. Demonstrate supported reuse, genuinely new schema, and defer. Swapped roles, repeated text, unavailable IDs, changed documents and stale snapshots cannot become accepted reuse. Replay validates the documents and exercises the actual additive preview/apply path on disposable copies. |
| GC5 · Discovery and quality evaluation | GC3–4 | Compare claim discovery over a whole document at fixed total reading budgets, including prose, tables and repeated statements. Use public CI fixtures for correctness and a separately frozen, authorized held-out corpus for quality claims. Record same-occurrence recall, false merges, correct fact bindings, novelty/defer counts and total cost. Publish negative results. |

## 5. Documentation, packaging and compatibility

GC2 owns API docs, CLI help, default-output snapshots and wheel import checks. GC4 owns the unattended-growth guide paragraph, example, and links from the rendering and evolution docs. Describe model-view completeness, byte budgeting, lookup after omission and shape-equivalence adjudication at the point where hosts build a round. GC5 owns evaluation instructions and limitations.

## 6. Risks and controls

Included-element collision or stale cache → loader refusal or snapshot mismatch. Dangling graph context → mark truncation and allow deterministic full lookup. UTF-8 overflow → measure final bytes. Sensitive evidence copied through an extensible payload → explicit field projection and sentinel tests on nested fields. Role-value occurrence mistaken for a supported relation → adversarial source pair plus explicit deferral. Cost shifted to repeated calls → record index construction, total selector input/output, calls and latency. Unaligned predictions remain a separate count.

## 7. Scope boundary

A graph database, hosted growth service, mandatory embedding model, general ontology alignment, autonomous merge policy, release publication and recertification belong to separate decisions. GC1–4 can satisfy the original product request even if GC5 finds no better discovery strategy.

## 8. Execution and review

Each phase has its own approved spec, focused implementation, regression tests, independent diff and refactoring review, and record. Use the maintained plan/close panel only after explicit selection under the project hook. Record review digest, findings and owner ruling. Work on a topic branch through PR. The owner decides approval, merge and release independently.

## 9. Verification and closure

GC1 covers projection contract, includes and failure order. GC2 covers CLI/API/installed parity and measured size. GC3 covers graph, byte cap, replay identity and repeated-query scaling. GC4 covers ordinary full-view hosts, bounded hosts, occurrence-level evidence and old examples. GC5 freezes disjoint development and holdout documents by content hash, schema snapshots, baseline, total budgets and scorer before inference. Evaluate whether more reusable mentions are found at their cited occurrence at equal total input, without an increase in false merges or a loss of correctly bound facts. Report per-document paired results and uncertainty. Owner must approve the corpus, numerical promotion margin and budget before unblinding. Without fresh evidence, ship only demonstrated deterministic capabilities and report research status separately.

Close record requires phase records, exact API/CLI artifacts, test summaries, full-repo Ruff, relevant layer and component checks, installed example receipts, compact/full sizes, and separate deterministic and empirical verdicts. Actual paid evaluation is opt-in. No acceptance lanes ran during planning.

## 10. Decisions for the owner

1. Approve the complete versioned JSON view and opt-in verbalization flag as the first shipping increment.
2. Approve an exact byte budget and read-only lexical/graph subset API as the oversized-schema route. An optional tokenizer adapter would expand compatibility obligations.
3. Decide whether to ship GC1–4 before GC5's quality evaluation. Recommended: yes. Keep automatic discovery experimental until the occurrence-level gate is met.
