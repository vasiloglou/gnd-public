# Confirmation reader 2 -- implementability, pins and homes

Retained text of the reader's returned report, lightly edited for layout.
Confirmation round (round 2) over r2 of both milestones. Scratch paths read
`<scratch>`.

All four r2 snapshots match. HEAD `1446f909`. Probes in
`<scratch>/plan-review-r2/reader2/` (`mg1_probe.py`, `mg1_mut.py`,
`evolve_tamper.py`, `rf6.py`, `pkga/`, `pkgb/`). Nothing written to the
repository.

**Verdict: request-changes**, for a narrow cause: themes D and E break at the
CLI apply path. `_cmd_evolve_apply` builds a fresh preview and refuses any
difference from the reviewed preview with exit 11 before `service.apply`
runs; the r2 evolve design never mentions this. Everything else is
approve-with-fixes.

## Theme status

| Theme | Status | Evidence |
|---|---|---|
| A | resolved | corpus probe: 282 loaded, 118 with rules, 301 rules, 19 prose, 97 with `clauses`; T3 fails 0; T3b rejects `text[:-1]` for every rule |
| B | resolved | 23 path crashes, 0 loaded (the disposition said 5) |
| C | resolved | all 8 table mutations refused by `load_model` (`mg1_mut.py`); control loads; low note C2-F12 |
| D | partly | optional v3 fields buildable, with the omission in the `EvolutionPreview` serializer because `_bindings_match` recomputes from `model_dump` (`models.py:815-817`); apply exits do not hold (C2-F1) |
| E | partly | a `--shape-report` preview cannot be applied (C2-F2) |
| F | partly | no model-hosted constraint row; role-ADD "already gated" wrong (C2-F3) |
| G | resolved | `provenance` on object and fact types is free-form, so `provenance.spans` fits; owner-ruled |
| H | resolved | cap unchanged at 4,000; 961 KB not re-measured |
| I | resolved | parser-only list incomplete (C2-F9) |
| J | resolved | §2.2, CT2-C4, CT-D4 (b) agree |

## Findings

**C2-F1 (blocking; r2-introduced) -- MG §2.2 "Apply", MG2-C3, MG-R3.**
`cli_service.py:643-647` builds `fresh = service.preview(proposal)` and, if
`reviewed != fresh`, raises `EXIT_COLLISION` (11) before `service.apply`
(`:661`). MG2-C3's four exit-3 cases (policy in preview only, in apply only,
different `--populated`, stripped `policy_issues`) all make documents that
differ from the fresh preview, so all exit 11; "caught only by the re-run" is
false on the CLI path. The plan does not place the option comparison against
the retry branch (`:618-641`), where the candidate is already live.
Reproduced (`evolve_tamper.py`): an extra `affected_references` entry with a
recomputed `preview_sha256` gives `EVOLUTION APPLY REFUSED (11): reviewed
preview is stale…`. Repair: the option comparison runs in
`_cmd_evolve_apply` before the fresh/reviewed equality and the branch split,
and the fresh preview is built with apply's options; or re-pin to 11. Either
way, test `EvolutionService.apply` separately, where the re-run is the only
guard.

**C2-F2 (blocking; r2-introduced) -- MG §2.3, MG-R4, MG3-C3.** Apply takes no
`--shape-report`, so its fresh preview lacks `shape_matches`, `reviewed !=
fresh`, and apply exits 11: advice blocks apply, contradicting MG-R4. Code
read. Repair: apply accepts `--shape-report`, or the equality excludes
`shape_matches` as `_evolve_same_review_identity` excludes fields
(`:426-437`); an MG3-C3 case where a `--shape-report` preview applies (0).

**C2-F3 (medium; r2-introduced) -- MG §2.2 matrix.** `ConstraintLocator.host`
can be `"model"` (`models.py:245-262`); a model-level subset or exclusion
over populated fact types has no row. "Role ADD … already gated today at
`service.py:634-637`" is wrong: that refuses only when the delta intersects
an existing operation's reference set (`:631-638`); without operations, a
role ADD is admitted. Repair: model-hosted rows (refuse ADD or strengthening
when any `role_ref` touches a populated fact type); the role-ADD refusal is
the policy's own; a case on a model without operations.

**C2-F4 (medium; r2-introduced) -- MG §3, signature-helper home.**
`model_index.py:29` and `universe.py:12,28,113` import `model_queries`; a
top-level import of `ModelIndex` or `reference_identity` inside
`model_queries.py` creates a cycle. Reproduced in patched copies (`pkga`,
`pkgb`): importing `gnd.model_index`, `gnd.model_queries`, `gnd.universe` or
`gnd.api` raises "ImportError … partially initialized module". Repair: put the
helper in `gnd/refscheme.py` or a new layer-`model` module registered in
`tools/gnd_layers.json`.

**C2-F5 (medium; r2-introduced) -- MG-R5, CT-R7.** The table is keyed by leaf
and callable, and `test_t13` asserts exact key equality
(`test_disclosure_mode.py:213-219`); an option row fails as stale. Making
`gnd discover` a `site` breaks NM-D13. Repair: keep leaf rows; refuse the
option through the existing named-option refusal (`disclosure.py:47-52`),
noted on the row; a CT4-C3 assertion on the `DisclosureRefused` message.

**C2-F6 (medium; pre-existing) -- unnamed pins.** Four new
`src/gnd/*.schema.json` files (MG1, CT1, CT2 ×2) each fail
`tests/test_conformance_payload.py:685-703` unless
`tests/support/runtime_schema_inventory.py:3` and
`tests/test_public_built_inventory.py:248-269` grow; no gate lists them.
`tools/run_public_acceptance.py:373` is a fifth exact `__all__` pin, stale at
baseline (lacks `DisclosureRefused`); MG1 T6 says "no other pin changes".
Repair: name these in MG1, CT1, CT2.

**C2-F7 (low; r2-introduced) -- CT §3, `__all__` order.** "CT2's `compose`
after MG1's `verbalize_rules`" is not enforced: CT2 needs only CT1. Repair:
CT2 depends on MG1 merged, or "append in merge order".

**C2-F8 (low; r2-introduced) -- MG §2.2 `populated`.** Unsaid whether the field
records the `--populated` argument or the effective set; apply's comparison
cannot be specified. Repair: record both; compare the argument set.

**C2-F9 (low; r2-introduced) -- CT1 parser-only rules.** Also duplicate keys
(`anchors.py:57-60`), non-JSON constants (`:65-66`), integers over 18 digits
(`:73-75`), nesting over 32 (`:79-80`); no T11 case breaks P3. Repair: list
all; an over-cap and a duplicate-key case in T11.

**C2-F10 (low; pre-existing) -- RF6 headroom.** RF6 finds 363 reads against a
ceiling of 365 (baseline 375) (`rf6.py`), so CT-R8's "update the row" path has
2 reads of slack while CT2 adds a resolver to `_anchored_verdicts`. Repair:
state the ceiling; counts do not grow.

**C2-F11 (low; pre-existing) -- MG3-C1 "value types by primitive".** The
signature includes the object-type id, so two value types never match and
the same id always does; the case has no falsifiable outcome. Repair: say
whether value-typed roles contribute their primitive instead of their id.

**C2-F12 (low; r2-introduced) -- MG1 table, `:168-172`.** `atom_bind` is total
(`atoms.py:30-43`), so the branch is dead; a non-dict `bind` renders `ft()`.
Citations off by 1–4 lines (`:154`→`:158`, `:189`→`:192`, `:570`→`:571`).
Repair: mark dead; fix citations.

**Stop rule:** 9 of 12 attack r2 text (F1–F5, F7–F9, F12); the ratio exceeds
one half, so stop and repair without another round. F1 and F2 should be
repaired, and checked against `cli_service.py:549-666`, before the MG2 and
MG3 specs are approved.
