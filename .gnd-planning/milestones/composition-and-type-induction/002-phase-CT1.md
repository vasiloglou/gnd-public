---
milestone: composition-and-type-induction
station: "phase-CT1"
skill: "n/a -- repository development under process-milestone auto=true, not a gnd-solve station"
scope: phase-CT1
date: 2026-11-04
gate:
  command: "uv run pytest -q tests/test_anchor_sidecar_v2.py tests/test_v70_phase1_adversarial.py tests/test_v70_phase1_surfaces.py tests/test_v70_phase5_adversarial.py tests/test_v70_phase5_corpus.py tests/test_rf1_semantic_pins.py tests/test_disclosure_mode.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py tests/test_conformance_payload.py tests/test_public_built_inventory.py tests/test_skill_prose_sync.py tests/test_packaged_skills.py tests/test_disclosure_docs.py tests/test_public_extraction_prose_policy.py"
  exit: 0
  output: "473 passed, 16 deselected in 60.99s"
  note: >-
    The spec's verification selection plus the skill, disclosure-docs and
    extraction-prose pins its reference edits touch. Run after the review
    fixes. Docs: strict build clean; 13682 links checked; ruff clean on the
    changed modules.
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "outside CT1's impact closure: one parser version and one evaluation loop"
evidence:
  - path: .gnd-planning/milestones/composition-and-type-induction/notes/phase-CT1-spec.md
    sha256: f67a7da5348a3134d0589157efe5fe3304a352f884b5205ee4d3286384ac4602
  - path: .gnd-planning/milestones/composition-and-type-induction/notes/phase-CT1-claude-review.md
    sha256: ff892f4272d0bd6d60ef602ec65884c83756fb2ee339c02af4af9be464ea1b2d
  - path: .gnd-planning/milestones/composition-and-type-induction/evidence/CT1/capture_parity.py
    sha256: 6484957b96817264079d5824b8bd4560c0e94c317986cc7ea862c1fda7eae9fb
  - path: .gnd-planning/milestones/composition-and-type-induction/evidence/CT1/parity-1446f90.json
    sha256: cb1800fa28e028b768d10de6df9c6b0cea381ade85e23fffabc544674f9574f2
  - path: .gnd-planning/milestones/composition-and-type-induction/evidence/CT1/parity-a2e44f8.json
    sha256: cb1800fa28e028b768d10de6df9c6b0cea381ade85e23fffabc544674f9574f2
  - path: .gnd-planning/milestones/composition-and-type-induction/evidence/CT1/parity-after.json
    sha256: cb1800fa28e028b768d10de6df9c6b0cea381ade85e23fffabc544674f9574f2
  - path: src/gnd/anchors.py
    sha256: da54ee2824a74eb8c461c1e77454f1916123876a2353a86dcdce86bbad08f4c4
  - path: src/gnd/checker/_core.py
    sha256: dc4a28c6dbdb3b41ebff241bed97be17cf70f491115ab2ef736f5a547f65a7a4
  - path: src/gnd/anchor-sidecar.schema.json
    sha256: 44189a0ea62ba0df5a2be631262fcd1d610cf8af40039edc00558f8e53a0a84a
  - path: tests/test_anchor_sidecar_v2.py
    sha256: 3810caaca21ce208c42da7eac92983d43361d81a16e78a8885b03b381ae93dc5
  - path: docs/reference/anchors.md
    sha256: be03d49d7ed6cfa403ff06eb075eb61fa282a9fe305de51e40449de41e613b15
  - path: src/gnd/skills/gnd-orm-core/references/constraint-reference.md
    sha256: 2def9c147b75872adac4a0d508dd96c8544fd91e8139a1303e1685a396cfcbdc
---

# Phase CT1: several anchors per fact role

**Claim.** `parse_anchor_sidecar` accepts `schema_version: 2`, where one
anchor is identified by fact key, role, span and occurrence, so several
anchors per fact role are allowed and an exact repeat is refused with
`duplicate anchor`. `gnd check --anchors --document` passes a role only
when every one of its anchors holds, and reports a failing fact once per
role. Every v1 input gives byte-identical `gnd check` (text and JSON) and
`gnd verbalize population` output and exits at `1446f90`, `a2e44f8` and
after (33 rows, one digest). The focused gate exits 0.

**Authority.** Plan r3 `(a1)`. Spec r3 under **delegated approval
(auto=true)** `(d1)` 2026-11-04 over SHA-256
`0c2f3d22948f3f8aa27f35dd1f26c5e71e14c5a7ae61abe659cb5663599bfd88`; an
agent ruling under the owner's "Yes, run it auto", not the owner's
personal reading.

## What changed

- `src/gnd/anchors.py`: `SUPPORTED_SIDECAR_VERSIONS = (1, 2)`; v2 identity
  adds span start, end and occurrence; the version check still precedes the
  per-anchor checks.
- `src/gnd/checker/_core.py` `_anchored_verdicts`: records grouped per key
  in sidecar order, the lexical index and recogniser limits read every record,
  and the evaluation loops over a role's records and stops at the first
  failure, so the failed list gains the row once.
- `src/gnd/anchor-sidecar.schema.json` (new), registered in both schema
  inventories.
- `docs/reference/anchors.md` (new, in the nav); citations in
  `docs/guides/documents.md` and the `gnd-orm-core` constraint reference;
  an Unreleased release-note entry.
- `tests/test_anchor_sidecar_v2.py` (25 tests, T1 to T13 plus the review's
  union case).

## Criteria

| Criterion | Evidence | Result |
|---|---|---|
| CT1-C1 v2 parse, repeats refused, v1 refusals unchanged, 3,500 anchors under the cap | T2 tests | holds |
| CT1-C2 every anchor must bind, order independent | T3, T4 with one good and two bad anchors | holds |
| CT1-C3 verbalization and export verification on v2 | T12 (two excerpts, then one; `gnd verify` exit 0) | holds |
| CT1-C4 schema and parser agree except P1 to P9 | T11 | holds; P7 (depth) is refused by the closed schema too, so it is in the agreed set |
| CT1-C5 recorded v1 table | `evidence/CT1/parity-*.json`, identical at three commits | holds |

**Deviations, recorded.** T7's "before" column is captured at both
`1446f90` and `a2e44f8` (main moved; `(d1)`). T8 measures span reads
(3,000) and one `lexical_ranges` call; record-dictionary lookups are not
counted: the loop does one `records.get` per (row, role) by inspection
(review F5). The spec's P6 row says `1e400` falls under the 18-digit rule;
the parser refuses it as a number too large for a float (P5-like); the
reference page states the real rule (review F3).

## Review

One local reviewer agent, read-only, over the uncommitted diff:
**approve-with-fixes**, no correctness bug, eight findings
([review](notes/phase-CT1-claude-review.md)). Eight mutants, seven killed
before the fixes.

| Finding | Disposition |
|---|---|
| F1 the occurrence union is untested (a mutant survived) | fixed: `test_anchors_asking_for_different_occurrences_all_bind`; the mutant is now killed |
| F2 the schema accepts a digest with a trailing newline | fixed: digest `minLength`/`maxLength` 64. A leading BOM stays a parser-only refusal |
| F3 the docs' integer rule | fixed on the reference page; the spec's wording is recorded above |
| F4 the parity script ignored `unredacted` and had no failing-anchor case | fixed: the flag is passed and a binding-but-failing v1 case added; all three columns recaptured (33 rows, identical) |
| F5 T8 does not count dictionary lookups | accepted as a recorded deviation |
| F6 the constraint reference keeps its own copy of the rules | accepted: the packaged skill is installed without the docs site, so it cannot cite `docs/reference/anchors.md`; it names the schema and the parser as the authority |
| F7 "bind" used for both the digest match and the span check | fixed on the reference page |
| F8 excerpt hashing costs anchors times span length | accepted residual: v1 already allowed the same total under the same caps |

## Refactoring review

The grouping is built once, inline, where the old dictionary was (rule 4);
no second loop or per-version copy. The RF6 census is unchanged: the new
local carries no subscript annotation, so no successor file is needed. No
new module, so the layer map is unchanged.

## Questions

None opened. CT-Q1 stays closed (no test asserted the v1 message).

## Boundary

Not merged, released or certified. `gnd extract` still writes v1.
