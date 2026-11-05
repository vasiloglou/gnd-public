---
milestone: composition-and-type-induction
station: milestone-close
skill: "n/a -- repository development under process-milestone auto=true, not a gnd-solve station"
scope: CT-close
date: 2026-11-04
source_base: a2e44f8
gate:
  command: "bash .gnd-planning/milestones/composition-and-type-induction/evidence/close/close-gate.sh"
  exit: 0
  output: "1900 passed, 42 deselected; 16 passed (distribution); 287 tutorial blocks passed; strict build; 14292 links; ruff clean"
  note: >-
    The union of the CT1 to CT4 phase gates (CT3's witness selection
    recomputed), the example and composed-witness tests, the distribution
    inventory, the full docs runner, the docs gates and ruff, over the
    closing tree. Ruff found two lint issues in new tests on the first run;
    they were fixed and ruff rerun clean.
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "the broad historical lanes are outside the milestone's impact closure"
evidence:
  - path: .gnd-planning/milestones/composition-and-type-induction/notes/composition-and-type-induction-plan.md
    sha256: 946e0c80b46bfc752f50dbfac32ce948caf857fbe9bf776058160f5334d021fa
  - path: .gnd-planning/milestones/composition-and-type-induction/notes/close-review-reader-1.md
    sha256: b0ec6f559768da99395aa14dda6b88fdf1130e41a476faf4a562c060d1a571b0
  - path: .gnd-planning/milestones/composition-and-type-induction/notes/close-review-reader-2.md
    sha256: c9b8dcdd0044b386fa91b706e613580895a05e692c9e2978cef86ac3ab7ea4ce
  - path: .gnd-planning/milestones/composition-and-type-induction/notes/close-review-reader-3.md
    sha256: 89c4d622b5e937cfba73e1df48a2f1b25baf7eb49fd211e4756d856db0f845ed
  - path: .gnd-planning/milestones/composition-and-type-induction/notes/close-review-reader-4.md
    sha256: 9d7fb92cc28829996d9604649dac0fe6d2f7fc24743944147617b358f42ed538
  - path: .gnd-planning/milestones/composition-and-type-induction/notes/close-review-fixes.md
    sha256: 2b5d66359a51880a7e4eb27abd5d002d63c7a865562897b476740dd6162352b2
  - path: .gnd-planning/milestones/composition-and-type-induction/evidence/close/close-gate.sh
    sha256: a072cc13b58469ce7fa2405ab0f94cf498fefdf0a0ecaadcbf43d3918cc769e3
  - path: .gnd-planning/milestones/composition-and-type-induction/evidence/close/close-gate.txt
    sha256: 92e2ee85d8226f99119e767ba7ecb85a99315031652585c39e72ab7f87e2389e
  - path: .gnd-planning/milestones/composition-and-type-induction/evidence/close/parity-anchors.json
    sha256: b1ad697616e2d96ac56f14277b419c5fffd4ff5fa7882292a8eaef4e12412a7b
  - path: .gnd-planning/milestones/composition-and-type-induction/evidence/close/parity-witness.json
    sha256: 4af54a97bac7e73094c49364b82a52bd3b1ce548a7a284aae85644b27fed9b23
  - path: .gnd-planning/milestones/composition-and-type-induction/evidence/close/parity-discover.json
    sha256: a093457d2119fc05d83a29650335c09419206f2167605e7e075d200ce98a312c
  - path: .gnd-planning/milestones/composition-and-type-induction/evidence/close/dynamic-query-successor.json
    sha256: 7777b54db540db6d427c5f75295094ddd95c8cc1a1e5fcdeb37df249b8935265
  - path: .gnd-planning/milestones/composition-and-type-induction/notes/CT5-dispositions.md
    sha256: a41abcef5329311bc0ff8281494a588551bfdc522e36d44443d60d47fc5c590a
  - path: src/gnd/composition.py
    sha256: 4c84b4c95189311bbd71fabda0d99fcb4004a97c3c95f76bb8d382a757d8e540
  - path: src/gnd/commands/checking.py
    sha256: 59f50cf7c1725efd5613f1bd4eaefc0ad1df5a165fa6e30b8957e3c735216065
  - path: src/gnd/api.py
    sha256: da3f00a7fcf0f172ef024ab24ef3c39537bb263e0e7bef3d45496516f9b7c4d9
  - path: src/gnd/discover/types.py
    sha256: 19aab56282ab2ad052258c451e3f644a5f5716818de629b068cad09ed4ccdf34
  - path: src/gnd/discover/service.py
    sha256: 086ff82e19c36e504da115a3c42a8b5c855f520c8950ab947d58e4f9de667c6e
  - path: src/gnd/witness/io.py
    sha256: 179ff8689888f7104d45122e089d44e73a4070ba3ba06a457a42734beca565ee
  - path: src/gnd/schema/witness.schema.json
    sha256: b06401a2c52e2471059acd4559ab9221d3406cc02b1bf507c17cee3e0e50da36
  - path: src/gnd/schema/witness-result.schema.json
    sha256: 4c887b64760d61baa18f843838c1fcb03f202865b606dd0441652011a049267f
  - path: src/gnd/skills/gnd-export/references/witness.schema.json
    sha256: b06401a2c52e2471059acd4559ab9221d3406cc02b1bf507c17cee3e0e50da36
  - path: src/gnd/skills/gnd-export/references/witness-contract.md
    sha256: 5aeb551d84d6717d4e160cb3b90d4f31d7da689dd68e603314c4d3d7c3ff996f
  - path: docs/reference/composition.md
    sha256: 0fcb0f1c94ee4006d0662cfb2bece0902aea9f4eb3852c9c2ece5614720543da
  - path: docs/reference/discover.md
    sha256: 01104834ee5ef77230701a60069177268bd7a5839da2c524fc70fada30ff6e05
  - path: docs/reference/python-api.md
    sha256: 887ce386f79ad46f799bc6a92aca7ba4c634b213ecca03cfc09ceab9b5638ea2
  - path: docs/reference/capabilities.md
    sha256: ca1d867bc80e364fea6a23d9a65c03365e71cc288933385c7660d14a532f2433
  - path: docs/how-to/compose-documents.md
    sha256: 8a4c6915e101fdb2256d2f80a86a3a826467b71faced4a8e2afc6f0aa24beaef
  - path: tests/test_composition.py
    sha256: 85ccfb32955d82eeda1778170c9e25056d8a1ba23e0774d9f7fa7c52864b4c53
  - path: tests/test_discover_fact_type_family.py
    sha256: 6a81062e3e18c8da8639f777f2a6a2eea150647d8d73f8a31cd7b935fa81a204
  - path: tests/test_witness_composition.py
    sha256: 780ac6675c8a74a825a03ced86c4906f5fe418540db6e4f9bcc0bffb28401421
  - path: tests/test_composition_example.py
    sha256: c27edf338cd9a2221eb204d064f1afcf5f06175bb5e315f5eaf4f00aa5e784a2
  - path: tests/support/pyrel_application_successors.py
    sha256: 0a1269d859f61d835e72859cef0fd0d8d6c96f2574f7aecabcdc26e4c9d0f9b9
---

# Composition and type induction -- milestone close

**Claim.** Issue #73's three requests and issue #77 now live in GND:
version-2 anchor sidecars with several anchors per fact role (every one must
hold); `gnd compose` / `gnd.api.compose` building one population from several
anchored sources under an explicit manifest, with a value-free lineage
record, and `gnd check --composition --sources` re-deriving it and checking
each anchored value against its own document; version-2 witnesses whose base
nodes name their source facts, replayed against the record; and the opt-in
`fact-type` discover family. A how-to walks two contracts through all of it.
Without the new options, version-1 sidecars, version-1 witnesses and the
seven default discover families give the recorded outputs of `a2e44f8`
(stated usage-line differences only). The close gate exits 0 after the close
fixes.

**Authority.** Plan r3 approved by the owner `(a1)`. The owner's "Yes, run
it auto" (2026-11-04) delegated spec, amendment and close rulings within
this milestone; every such ruling is a **delegated approval (auto=true)**,
an agent ruling, never the owner's reading. The owner answered the DC2
checkpoint "Yes, finish it". Close review instrument: four local readers
(CT-D1 `(o1)`). Not merged, released or certified; merge needs the owner.

## Phase records

| Phase | Record | Commit | Focused gate |
|---|---|---|---|
| CT1 several anchors per role | [002-phase-CT1.md](002-phase-CT1.md) | `f20f5c3` | 473 passed |
| CT2 composition | [003-phase-CT2.md](003-phase-CT2.md) | `2c25ba4` | 663 passed |
| CT3 witness lineage | [004-phase-CT3.md](004-phase-CT3.md) | `4584415` | 1341 passed |
| CT4 fact-type proposals | [005-phase-CT4.md](005-phase-CT4.md) | `077a611` | 579 passed |
| CT5 documentation | [006-phase-CT5.md](006-phase-CT5.md) | `2bc4047` | docs gates, 124 passed |
| close fixes | this record | the commit adding this record | the close gate |

Each phase had one independent diff reviewer (one reviewer is one reviewer).
Reviews named the uncommitted tree, not a digest (reader 3 F6), and phase
fixes were not re-reviewed before the close; the four close readers are the
first review of the committed bytes at `2bc4047`, and one further reader
reviewed the close fixes ([note](notes/close-review-fixes.md)).

## Completion predicates

| # | Predicate | Result |
|---|---|---|
| 1 | v2 sidecars, every anchor binds, v1 table | holds (CT1); close parity `evidence/close/parity-anchors.json` equals CT2's table (CT1's plus U01's usage line) |
| 2 | compose, record, check re-derives, per-source spans, conflicts with lineage | holds (CT2) with the close repairs: instance-only renamings, contradictory and splitting instance renamings, case-colliding ids and non-canonical records are refused; outputs compared by identity |
| 3 | witness v2 sources, replay verifies, v1 unchanged | holds (CT3); close parity `parity-witness.json` identical; the result envelope schema now accepts v2 (reader 4 F1); a test now follows the answer to a span in **each** document (reader 3 F4). CT3-C4 is **partly met**: why-not is tested; `gnd export souffle` refuses the example model (input-invalid), so souffle-witness is argued from code only |
| 4 | fact-type family, additive proposal, shape match reported | holds as stated, with limits: the written proposal is now trimmed under its cap (reader 2 F1); exactly repeated rows are one value; but the family proposes **once per generic fact type** across runs (reader 3 F1: every group shares one role-player signature, so after one is applied the rest are shape matches). CT4-C4's "a second group in the same run is proposed" never arises on a validated population. Both are documented in `discover.md`; CT-close-Q1, Q2 |
| 5 | dispositions, pages executed, docs gates | holds (CT5) with `capabilities.md` added at the close (reader 3 F10; 52 rows, 12 updated). DC1 **not met** (missed, agent ruling D2); DC2 met. CT-close-Q3 |
| 6 | focused gates, diff reviews, sweep, PR | holds: five phase gates, five diff reviews, four close readers, a fix re-review, this gate, the sweep below and the PR. **Owner acceptance is separate and pending** |

## Close review (four local readers, CT-D1)

[Reader 1](notes/close-review-reader-1.md) (anchor and composition core),
[reader 2](notes/close-review-reader-2.md) (witness lineage and discover),
[reader 3](notes/close-review-reader-3.md) (predicates and evidence),
[reader 4](notes/close-review-reader-4.md) (compatibility and docs). All four
approve-with-fixes; no blockers.

| Finding | Severity | Disposition |
|---|---|---|
| R1-1 an instance-only renaming counted as used and could hide a mandatory violation | major | fixed: only fact-row hits count; test |
| R1-2 instance renaming inferred first-wins; split entities | major | fixed: different targets refused; renaming an instance another role still uses refused; tests. Per-role splits without instances documented (fix review 3, CT-close-Q4) |
| R1-3 output staging not all-or-nothing; mode 0600 | minor | fixed: a directory target exits 74 before writing; umask mode; tests |
| R1-4 an output could overwrite the model | minor | fixed: refused (64), by file identity after the fix review; tests |
| R1-5 `..` and symlinked ancestors refused, reported as "invalid model" | minor | behaviour kept (the shared safe reader); read failure now says "could not be read safely"; documented |
| R1-6 case-colliding source ids | minor | fixed: case-folded distinctness; test |
| R1-7 the check path reads the model twice | hypothesis | residual, CT-close-Q5 |
| R2-1 the type budget underestimated the written proposal | major | fixed: written bytes measured, groups dropped from the tail; tests (and fix review 1) |
| R2-2 identical readings across generic fact types | minor | fixed: the reading names the generic fact type |
| R2-3 one repeated row marked a group multi-valued | minor | fixed: distinct values per entity; test |
| R2-4 unvalidated `sources` strings reached views | nit | fixed: the record's id form in io and the schemas; test |
| R2-5 row visits outside the work ceiling | nit | documented in `discover.md` |
| R2-6 composed replay hashes and parses in two reads | hypothesis | residual, CT-close-Q5 |
| R3-F1 once per generic fact type | medium | documented; CT-close-Q1 |
| R3-F2 D5 narrows O6 without an amendment | medium | recorded here as a delegated amendment; distinct-value counting narrows it less; CT-close-Q2 asks the owner |
| R3-F3 CT5-C2 recorded "holds" with DC1 missed | medium | corrected above: DC1 not met; CT-close-Q3 |
| R3-F4 CT3-C3/C4 recorded too strongly | low-medium | both-document span test added; CT3-C4 partly met (above) |
| R3-F5 CT2 to CT5 spec approval digests unverifiable | low | residual: the pre-tag bytes were not committed; later milestones should commit a pre-tag snapshot |
| R3-F6 reviews not tied to bytes | low | stated under Phase records |
| R3-F7 stale status text | low | README lines marked superseded; the frozen plan's header ("no code is written", "CT4 is blocked") and §10's open CT-Q2, CT-Q3 are superseded by this record (both resolved, below) |
| R3-F8 CT-R4 departures not in records | low | listed here: CT2 D6 uses `canonical_json_bytes` for the record identity; CT3 D3 binds the record's raw bytes. The close makes the two coincide by refusing non-canonical records (R4-F2); the attribute digest now uses `canonical_json_bytes` too (R4-F3) |
| R3-F9 owners of carried questions | low | in the sweep below |
| R3-F10 `capabilities.md` not dispositioned | low | updated and added |
| R4-F1 result envelope schema v1 only | low-medium | fixed: embeds the current witness schema; sync test |
| R4-F2 one record, two identities | low | fixed: non-canonical record files refused; test |
| R4-F3 attribute digest not recomputable | low | fixed: SHA-256 of canonical JSON, documented |
| R4-F4 stale `check()` signature | low | fixed, with the v1/v2 sentence and the exclusions |
| R4 nit disclosure sentence in the how-to | nit | fixed |

## Parity at the close

`evidence/close/parity-{anchors,witness,discover}.json`, captured on the
closing tree with the phase scripts: byte-identical to the CT2, CT3 and CT4
"after" tables. The fact-type family's changes (digest form, reading,
trimming) do not reach runs without it.

## Question sweep

| ID | Question | Resolution or owner |
|---|---|---|
| CT-Q1 | tests asserting "duplicate fact-role anchor" | closed (CT1) |
| CT-Q2 | witness digest form against raw-byte sidecar digests | resolved (CT3 D3): raw-byte digests throughout; reader 2 P14 |
| CT-Q3 | replay mismatch exit; Souffle and why-not | resolved (CT3 D2, D4): forged sources exit 1; neither reads a certificate; Souffle untested end to end (predicate 3) |
| CT2-Q1 | `gnd compose` RF1 goldens on py311/py313 | residual; owner: the next milestone that recaptures RF1 pins (with MG3-Q1) |
| CT2-Q2 | `test_prepared_policy_rechecks_live_hashability` fails on main and here | residual; owner, to file as a maintenance issue (not filed: outward-facing) |
| CT4-Q1 | salt or omit the attribute digest | owner, with the disclosure policy; now a canonical-JSON digest, still guessable for low-entropy names |
| CT-close-Q1 | a duplicate key for the family that is not the role-player signature, so it can propose after an applied induction | owner |
| CT-close-Q2 | D5: propose a uniqueness-failing fact type for multi-valued attributes, or keep counting them | owner ruling requested |
| CT-close-Q3 | accept DC1 as missed | owner acceptance |
| CT-close-Q4 | refuse per-role renamings that split a value with no listed instance | owner |
| CT-close-Q5 | read model and population once on the check and replay paths | maintenance (hypotheses, unreproduced) |
| O18 | reporter acceptance in its own pipeline | carried: the reporter, after merge |

## Refuted premises

The plan's §2.3 says the Souffle witness export and why-not handle
witness version 2; neither reads a certificate (CT3, D4).

## Boundary

Local completion only. Not merged, released or certified. Owner acceptance,
the questions above and O18 remain.
