---
milestone: unattended-model-growth
station: "phase-UG3b"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-UG3b
date: 2026-11-09
gate:
  command: "uv run pytest -q -p no:cacheprovider <99 modules: both UG3 files, the plan §9 UG1 gate, RF1 CLI pins and harness, layering, arch, RF6 packages and query policy, disclosure, packaged-skill pins, documentation tutorials, unattended mode, and every test module importing gnd.evolve, the RF6 successor chain, the report schema or the validate API> --tb=short --junitxml=<scratch>/ug3-junit.xml"
  exit: 0
  output: "4007 passed, 42 deselected in 469.54s (0:07:49)"
  base: "5c6a0c5f (main after PR 147)"
selection:
  - {obligation: "G-phase (part B): corpus B1 to B8, B9, the B7 control, successor cases B10 to B16, review regressions R3, R5; B13 is test_t14", disposition: run, command: "uv run pytest -q -p no:cacheprovider tests/test_evolve_source_document.py tests/test_evolve_additive_policy.py::test_t14_the_cell_literal_the_contract_table_and_the_walk_agree --tb=short", exit: 0, note: "25 passed in 1.32s"}
  - {obligation: "G-ug1, G-ug2, G-rf1, G-layers, G-arch, G-packages, G-rf6, G-evolve-consumers (discover included), G-disclosure, G-skills, G-docs (spec §8 ledger)", disposition: run, command: "the gate above", exit: 0}
  - {obligation: "G-lint, G-components, G-anon", disposition: run, note: "as in 004-phase-UG3a.md, over the same tree"}
  - {obligation: "phase-diff review", disposition: run, note: "one reviewer, Codex CLI, over both parts; notes/phase-UG3-codex-review.md"}
  - {obligation: "full default lane; -m 'evidence or census'; distribution lane; certification", disposition: cadence, note: "not selected (verification-selection: no explicit owner request)"}
evidence:
  - {path: src/gnd/evolve/models.py, sha256: f908834b4bbe121eb9dfa553ff4d57f744bd46dbc5cc92c9959672e79a2a5160}
  - {path: src/gnd/evolve/service.py, sha256: c4e48356785009bccdebc6207eb45ea11503dfef40890de3ed03f96ca2a2cdbb}
  - {path: src/gnd/evolve/policy.py, sha256: 8da581d9fa32bff5ad33746d029e8145ca81544b340df20a84f03690f3013322}
  - {path: tests/test_evolve_source_document.py, sha256: ddf161ef4021c887585409152ae86bba1e9df0d39ccc9610fe27f39ff88ad2d2}
  - {path: tests/fixtures/unattended-model-growth/ug3/expected.json, sha256: a46dc7dcdc702aa4c361024990d10e8f97179345a38099ab03ac9e0feebd7358, note: "the approved answer key, unchanged since its approval"}
  - {path: tests/fixtures/unattended-model-growth/ug3/parity-baseline.json, sha256: 6b84dfb57a5475dbf21d6cacbf60bbc6b10a3634e2fc9c31c596106bc4957035, note: "captured on 5c6a0c5f before the first source edit"}
  - {path: .gnd-planning/milestones/unattended-model-growth/evidence/UG3b/dynamic-query-successor.json, sha256: 6e0048d0d4bd31a05c6be56db79b1076da3dd5dba9d803860c455eebb2a9237e}
  - {path: .gnd-planning/milestones/unattended-model-growth/notes/phase-UG3-codex-review.md, sha256: 3b7b6921a8685ceeaaf215f2e7728d7a16559c8eb96b992e11e45674eab2bf34}
  - {path: "junit report of the gate run (scratch, not committed)", sha256: 24fd15464cb7ddc1934769a850ad495b32e20b8da8f67845d2f2bafaf0787eaa}
---

# Claim

A growth round of an unattended model can declare the document its new spans cite, inside the
round (issue 104, UG-D9 (b)). A `source-document` operation locator in `gnd evolve` addresses one
`source.documents` entry by its digest. `add` appends it after refusing a duplicate; `modify`
changes only its label; `delete` removes it; `rename` is refused; a `modify` or `delete` needs
exactly one entry with the digest. Under `--policy additive` the add is admitted, and a modify or
delete is refused (`source_document.modify`, `source_document.delete`, exit 3). A locator kind the
policy has no rule for is refused by type (exit 3), never admitted. The locator exists in proposal
and record `schema_version` 3 only; a v1 or v2 document carrying it is refused when read (3). No
blast-radius entry is added. Locator-free proposals keep their bytes, `proposal_sha256`, preview
bytes and exits (B9, six rows against `5c6a0c5f`). The release note says GND 0.2.0 cannot read a
proposal that declares a source document.

Authority: spec r1 approved `(o)` 2026-11-09 ("approved", all of UG3-D1 to D14 as proposed);
corpus approved `(o)` the same day ("Approve the corpus"). `auto=false`. Not merged; merge needs
the owner.

## Gate output

`4007 passed, 42 deselected in 469.54s` over 99 modules, exit 0; the part B file and `test_t14`
`25 passed`. The twelve part B corpus cases give their approved answers; the answer key's digest
is unchanged since approval.

## Review

The same single Codex review as part A ([phase-UG3-codex-review.md](notes/phase-UG3-codex-review.md)).
**One reviewer is one reviewer.** Part B's three findings, all reproduced and fixed with a
regression test:

- **3 (blocking):** records share `EvolutionOperation`, so a v1 or v2 record accepted the locator.
  Fixed: one helper refuses it in the proposal and the record validators (dict and JSON readers).
- **5 (hardening):** with a digest declared twice, a `modify` or `delete` silently took the first
  entry. Fixed: exactly one entry is required; two are ambiguous (3).
- **6 (hardening):** each `add` rescanned the growing list (quadratic). Fixed: the replay reads the
  declared digests once and keeps the set current; B16 now counts that work.

## Refactoring review

Refactors EXECUTED, behaviour-preserving behind the same gates:

- **Explicit locator branches** replace the constraint fall-throughs at every site that dispatches
  on the locator (`_operation_target`, `_delta_element_ids`, `_shape_and_digests`, the policy),
  and the policy's last branch now fails closed instead of admitting an unknown kind.
- **One version rule** (`_refuse_source_documents_before_v3`) shared by both readers that carry
  operations (review finding 3).
- **One target helper** for the source documents (`_source_document_target` with
  `_declared_positions` and `_declared_digests`), reached through the replay's generic path, so
  the append, compare and delete code is not duplicated.

Seen and deferred: the replay refusals reuse `_evolve_service_exit`'s message families ("add
target", "stable locator"); their variable text is a validated digest, so no operator text can move
the band, but the substring mapping itself is UG2-Q2's open refactor. Whether layer one should
refuse a digest declared twice is UG3-Q2.

## Size

Estimate (spec §10): about 300 source lines and 700 test lines for both parts. Part B measured:
152 source lines added and 4 removed (`models.py` 65, `service.py` 68, `policy.py` 11), 163 test
lines added after the corpus commit plus 13 in `test_evolve_additive_policy.py`, 44 contract and
reference doc lines. Both parts together: 312 source lines, within the estimate.

## Departures from the spec, each recorded in the spec's findings

- F-c2: the B7 answer depends on refusing the locator while the proposal is read; the control pins
  that v1 and v2 previews otherwise exit 70.
- F-i2: B15 re-shaped onto the service's re-run (the CLI refuses a `--policy` mismatch first).
- F-i3: the replay refusals use the existing message families.
- F-i4: UG1 T12 (a)'s message is unchanged; only its comment is updated.
- F-i6 (review): the v3-only rule covers records; `modify` and `delete` need exactly one entry.

## Boundary

- Part B only. Part A is [004-phase-UG3a.md](004-phase-UG3a.md). UG4 is not done: the
  out-of-band step in `unattended-growth.md` is not retired and the skill does not point at the
  operation yet.
- Issue 104 is not commented on or closed.
- A declared document is bound by digest only; nothing checks the label against the file.
- Not merged, released or certified.

## Open questions

| ID | Question | Target |
|---|---|---|
| UG3-Q2 | Layer one (U1) accepts a digest declared twice in `source.documents`; UG3 refuses a `modify` or `delete` of it as ambiguous, but refusing the duplicate itself would change validation of existing unattended models | owner; UG4 or the milestone close |
| UG2-Q2 | `_evolve_service_exit` maps refusals by message substring; UG3's two replay refusals use the existing families | the milestone close sweep (refactoring candidate) |
| UG-Q6, UG-Q7 | carried from the plan | owner |
