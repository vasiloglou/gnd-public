# Plan review -- round 2 (confirmation) disposition

2026-11-03. Instrument: four local reviewer agents (MG-D1, CT-D1, `(o1)`),
fresh context, one lens each, as in round 1. One round covered both
milestones. The owner directed this round in `(p1)`. It approves no plan or
spec bytes.

## Subjects and limits

| Subject | SHA-256 | Retained snapshot |
|---|---|---|
| MG plan r2 | `b0294807cb4268afb188d084414e418d75ca8338960ae1283ebefdb44d7f63df` | `evidence/plan-review-r2/model-growth-guardrails-plan.md.snapshot` |
| MG1 spec r2 | `553724f84783b224b71bb9f9f26362f46271151f5059737c0abfdb8b782ce4cf` | `evidence/plan-review-r2/phase-MG1-spec.md.snapshot` |
| CT plan r2 | `506b285d8fa4bba50e877b9c0ce31d25d24970c857a38adb3e68fe64333c9edd` | `../composition-and-type-induction/evidence/plan-review-r2/composition-and-type-induction-plan.md.snapshot` |
| CT1 spec r2 | `0a31dad55a52c18a8b498c9d02e46d08fdad759d425de50e9ec303bc7f56a38b` | `../composition-and-type-induction/evidence/plan-review-r2/phase-CT1-spec.md.snapshot` |

All four readers verified all four digests and wrote nothing to the
repository. Probes ran only in the session scratchpad. Scope, declared in the
plans' §8: the status of blocking themes A–J, and new defects tagged
r2-introduced or pre-existing.

## Opinions and the stop rule

| Reader | Lens | Verdict | Findings | r2-introduced |
|---|---|---|---|---|
| [1](plan-review-r2-reader-1.md) | correctness | approve-with-fixes | 9 | 9 |
| [2](plan-review-r2-reader-2.md) | implementability | request-changes (D, E); otherwise approve-with-fixes | 12 | 9 |
| [3](plan-review-r2-reader-3.md) | protocol, privacy, docs | approve-with-fixes | 10 | 7 |
| [4](plan-review-r2-reader-4.md) | test design | request-changes | 12 | 11 |

**Self-inflicted ratio: 36 / 43 = 0.84**, above one half. Same-seat counts
fell on every seat (12→9, 14→12, 13→10, 16→12) while severity also fell: no
round-1 theme remains unresolved on every seat. The declared stop rule
applies: **no further plan round.** The repairs below are applied as r3,
and **r3 bytes carry no review opinion.** The next instrument is the owner's
plan gate, then each phase spec's gate, then code.

## Theme status (A–J)

| Theme | R1 | R2 | R3 | R4 | Outcome |
|---|---|---|---|---|---|
| A rule-text oracle | resolved | resolved | resolved | partly | resolved; fixtures hardened (theme R2-C) |
| B path crash | resolved | resolved | resolved | resolved | resolved (23 models, reproduced by three seats) |
| C fallback table | partly | resolved | resolved | partly | repaired in r3 (R2-C) |
| D evolve policy and versions | resolved | partly | resolved | partly | repaired in r3 (R2-A) |
| E shape report | resolved | partly | resolved | resolved | repaired in r3 (R2-A) |
| F policy matrix | partly | partly | partly | partly | repaired in r3 (R2-B) |
| G unattended scope | partly | resolved | resolved | partly | repaired in r3 (R2-D) |
| H anchor count | resolved | resolved | resolved | resolved | resolved; template pinned (R2-F) |
| I parser-only rules | partly | resolved | partly | partly | repaired in r3 (R2-F) |
| J CT-D4 | resolved | resolved | resolved | resolved | resolved |

## Coordinator reproduction

At `1446f90`:

- `evolve/cli_service.py:643-647`: `fresh = service.preview(proposal)`; `if
  reviewed != fresh: raise _EvolutionCLIError(EXIT_COLLISION, …)`, before
  `service.apply`. Confirms C2-F1 and C2-F2.
- `model_index.py:29`: `from gnd.model_queries import primitive_for`. A
  helper in `model_queries` importing `ModelIndex` cycles. Confirms C2-F4.
- `model_verbalization.py:474-477`: `_coerce_model` returns a `Model`
  unvalidated. Confirms C1-F3 and C4-F8.
- `disclosure.py:46-55` `values_allowed`: customer refuses a request,
  internal always emits, unset emits as requested. This bears on C3-F1.
- `anchors.py:209-215`: anchor text is the NFC normalization of the UTF-8
  document; spans count its code points. This bears on C3-F10.

## Themes and repairs applied in r3

"Owner" marks a point for the plan gate. r3 applies the proposal and labels
it proposed.

| Theme | Findings | Defect | r3 repair |
|---|---|---|---|
| **R2-A** apply path | C2-F1, C2-F2, C4-F4, C1-F8, C2-F8, C3-F7 | The CLI rebuilds the preview and refuses any difference (11) before the service; `--shape-report` previews cannot apply; MG2-C3's exit-3 cases cannot be told apart; omission must be in the serializer; `populated` is ambiguous; the guarantee needs the caller to repeat `--policy` | `_cmd_evolve_apply` compares apply's `--policy` and `--populated` with the reviewed preview's **first**, before the retry branch and the fresh/reviewed equality (3, message names the option). The fresh preview is built with apply's options and with `--shape-report` exactly when the reviewed preview carries `shape_matches`. A tampered preview is then refused by the equality (11) on the CLI path. `EvolutionService.apply` is tested directly, where the re-run is the only guard (3, message names operation index and cell), with a mutation control. The omission lives in the preview serializer (`_serialize_wire_version`, `models.py:786`), and the V3 reader declares the fields. The preview records `populated_args` and the effective `populated` set separately, and apply compares the argument set. The docs state that the guarantee holds when apply repeats `--policy`. |
| **R2-B** policy matrix | C1-F1, C1-F2, C2-F3, C3-F3, C4-F1, C4-F2, C4-F3 | MODIFY cells not total; an element MODIFY replaces embedded constraints; `objectification` and fact-type `description` are not schema keys; role ADD is not "already gated"; operations cells are pre-empted by 18; model-hosted constraints have no row | MODIFY is an **allow-list**. An object-type MODIFY is admitted only when the diff is confined to `description` and `provenance.rationale`. A fact-type MODIFY is admitted only when the diff is confined to `provenance.rationale`. Everything else is refused, including constraints changed inside an element MODIFY. A role ADD on an existing fact type is refused by the policy itself (3), tested on a model with no operations. Operations MODIFY, RENAME and DELETE are marked pre-empted by 18, with no policy case. Model-hosted constraints get a row: populated if **any** fact type a `role_ref` names is populated (**Owner**, proposed). |
| **R2-C** MG1 in-memory models and fixtures | C1-F3, C1-F4, C2-F12, C4-F5..F8, C4-F12 | A `Model` input skips semantic validation, so partial renders are reachable; table lines and one dead row; the `date_add` row cannot fail on bookrec; two continuations have no case; T3c cannot fail; T7 and T11 are weak | `verbalize_rules` re-validates a `Model` with `validate_model_object` (as `_run_verbalize` does, `api.py:833-834`): failure gives `exit_code` 3. `render_rule_verbalizations` raises `VerbalizationError` instead of rendering through a fallback. T4c mutates a loaded `Model` in place per row. Table: lines corrected; `:168-172` marked dead (`atom_bind` is total); rows added for a missing or non-dict `bind`, a non-dict `where` item and a missing `head`; a nearest-valid control per row; `date_add` on a version-3 model. T3d covers ` Admission depends on ` and the redaction sentence. T3c uses a variable holding U+0007. T7 records path-input digests for all models. T11 runs with 2,000 ids, reversed and duplicated. `render_model_verbalization` keeps its behavior for invalid in-memory models (out of scope). |
| **R2-D** unattended sources | C1-F5, C4-F9, C3-F6, C3-F10 | `induced` and `imported` constraints unspanned; U8 omits `induced`; U3 subsumed; per-branch cases; MG-D8 claims more than ruled; span units undefined | Spans required for every constraint source except `common-sense` (**Owner**, proposed). U8 includes `induced`. U3 is recorded as subsumed by U2 and `semantic:status-source`, kept as a named rule id with no separate case. One case per branch, asserting `semantic:unattended-*` ids. MG-D8 separates the ruled part from the proposed part. Units: `start` and `end` count code points of `canonical_document_text` (NFC of the UTF-8 document), and `excerpt_sha256` is the SHA-256 of the UTF-8 encoding of that slice, as for anchors. The `common-sense` exemption is presented as a scoping of #74 (**Owner**). |
| **R2-E** signature helper | C2-F4, C2-F11 | `model_queries` would cycle; "value types by primitive" cannot fail | Home: `src/gnd/refscheme.py` (layer `model`), which may import `model_index`. The signature is the multiset of role-player object-type ids; equal ids imply equal reference schemes, so "compatible reference modes" adds no separate test. The "value types by primitive" case is removed. |
| **R2-F** CT1 parser and sizes | C1-F6, C1-F7, C2-F9, C3-F4, C4-F10, C4-F11 | Parser-only rules incomplete; size depends on the template; no check-time growth case | Parser-only rules P1–P9 (duplicate identity, `start < end`, 1 MiB cap, duplicate JSON keys, non-JSON constants, integer length > 18, depth > 32, `type(...) is int` against integer-valued floats, invalid UTF-8), with one T2 and one T11 case each. T2 pins the canonical form written by `write_anchor_sidecar` and uses 3,500 anchors. T8b: 3,500 anchors on one (row, role) at check time. |
| **R2-G** disclosure rows | C3-F1, C2-F5, C3-F2 | An option cannot have its own row; `gnd discover` resolves no mode; compose emits the caller's values | `gnd compose` and `api:compose` are `every-mode` (the caller's own population), with a note that the record is value-free. For `--show-values`, **Owner**: (a) proposed: `gnd discover` becomes a `site` leaf using `values_allowed`. Customer refuses `--show-values`, unset emits raw values only when it is passed, and internal emits them always. All other discover output is unchanged in every mode. This supersedes NM-D13 for that one option, and T26's arithmetic and `disclosure.md` change. (b) Keep "raw value only with the flag under internal" literally: a custom check unlike every other site. |
| **R2-H** pins and records | C2-F6, C2-F7, C2-F10, C3-F5, C3-F8, C3-F9, C1-F9 | Schema inventories and a fifth `__all__` pin unnamed; `__all__` order not enforced; RF6 headroom; witness twin unpinned; stale records; #78 scoping; CT2-C4 exit | New schema files are named with `tests/support/runtime_schema_inventory.py`, `tests/test_public_built_inventory.py` and `tests/test_conformance_payload.py`. `tools/run_public_acceptance.py:373` is named (stale at baseline; MG1 fixes it and records it). `__all__` names are appended in merge order. RF6 reads must not grow past the ceiling of 365 (363 at baseline). CT3 adds `witness.schema.json` to `SCHEMA_PAIRS`. `PROJECT.md` and the CT pointer are updated. MG §7 scopes out value constraints in the guideline (MG-D6, **Owner** confirms). The CT2-C4 fixture uses an alethic uniqueness constraint. |

## Questions for the plan gate

| # | Question | Proposal |
|---|---|---|
| G1 | `gnd discover --show-values` disclosure | (a) standard site behavior, superseding NM-D13 for this option |
| G2 | Unattended spans for `induced` and `imported` constraints | spans required for every source except `common-sense` |
| G3 | Model-hosted constraint "populated" | any named fact type populated |
| G4 | Scoping: #74's common-sense exemption; #78's value constraints omitted | confirm both |
