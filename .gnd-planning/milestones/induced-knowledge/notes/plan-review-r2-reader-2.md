# Confirmation reader 2 — implementability, dependency homes and layers

Plan r2 SHA-256 `d1a40a89…7c85` and IK1 spec r2 SHA-256 `4f4cb8b5…3cac1` — both
match at `b554f3f`.

**Verdict: approve-with-fixes.** Both round-1 blockers resolved; no new blocking
defect; all four new findings are r2-introduced.

## Round-1 findings in this lens

| ID | Status | Evidence |
|---|---|---|
| R2-F1 projection allowlist (blocking) | resolved | spec 91–96 moves the description to `gnd.vocabulary.render_verbalization` and leaves the projection alone; `_build_projection` (extract/projection.py:246–249) copies only object-type `id`s, so a described model never reaches `_ALLOWED_KEYWORDS`; T6 pins it |
| R2-F2 diff vocabulary mismatch (blocking) | resolved | D11 comprehension (spec 102–109) works on `model.object_types` (plain dicts; vocabulary.py:105 uses `.get`); only callers diff.py:280, api.py:716 (via extract.anchors re-export) and anchors.py:222; digest unchanged for undescribed models, so the RF1 sem-diff golden keeps its vocabulary_digest |
| R2-F3 cap vs `_neutralize` | partial | cap now 512 and double rendering declared intended (spec 81–88), but the cap applies after escaping (C2-F1) |
| R2-F4 `BlastRadiusEntry.surface` | resolved | spec 137–142 extends the `Literal` (evolve/models.py:635–651) and the contract; `_surface_index` (service.py:264+) supports a key-conditional surface |
| R2-F5 report-schema copy, redaction, RF1 anchor | resolved, one follow-on | `$defs.diff_reference_report` equals diff.schema.json today (probe `True`), so T10 is sound; redaction deep-copies and redacts only populations (redaction.py:774–786); `M-SEM-diff-schema` replaces `"schema_version": "gnd-diff/1",` with a count check (rf1_pins.py:169, 289) — the kept line plus a separate constant keeps exactly one match and the mutation stays killed; follow-on C2-F2 |
| R2-F6 lanes, RF5, RF6 | resolved | plan 96 (IK-R7), 121, 296, IK6-C3 name the closed `lanes`, `RF5_COMMAND_GROUPS`, `gnd_entrypoints.json`, `discover/service.py`, RF6 ceiling; fits gnd_arch.py:155–156, 825–828; `discover` (rank 4) importing checker (rank 2) is not a wrong-way edge |

## New findings

- **C2-F1** (correctness, medium; r2-introduced: yes). Spec 81–82 / plan 156–157
  claim the 512 cap means `_neutralize` "never elides"; spec 51 and IK1-C2 promise
  "untruncated". verbalize.py:57–61 escapes `\`, `'`, controls and U+2028 first,
  then caps at 512. Any description with an escapable character up to 512 is
  truncated; T3 passes only for plain text; T5's 512-char hostile mix is
  truncated, contradicting C2. Reproduce: `_neutralize("'"*512)` returns 536
  characters ending `… (+512 more characters)`; `_neutralize("a"*511+"'")` elides 1.
  Fix: render with escaping but no cap, cap the schema at worst-case expansion,
  or declare truncation; add a hostile 512-char case to T3.
- **C2-F2** (completeness, medium; r2-introduced: yes). Spec 127–129 makes both diff
  schemas a top-level `oneOf`. tests/test_conformance_payload.py:652 indexes
  `report_schema["$defs"]["diff_reference_report"]["properties"]["command"]`; a
  top-level `oneOf` removes `properties`, so this existing test raises `KeyError`.
  Fix: keep a closed top-level `properties` with optional `annotations` plus an
  `if`/`then` on `schema_version`, or name the test edit.
- **C2-F3** (completeness, low; r2-introduced: yes). D11 changes what
  `vocabulary_digest` hashes, but spec 144–148 / IK1-C5 omit the prose defining its
  composition: constraint-reference.md:47 lists exactly what is hashed/omitted;
  representation-format.md:272 lists only `depends_on` as excluded. Both become
  wrong after IK1.
- **C2-F4** (accuracy, low; r2-introduced: yes). Spec 93–94: "the module docstring's
  list of read keys" in `src/gnd/vocabulary.py` — that list lives in the shim
  `src/gnd/extract/vocabulary.py:3–10`; the home docstring is one RF3 line. Name
  the shim docstring or move the list.

Counts: 4 new findings, all r2-introduced, none blocking.

## Limits

Static reading plus `python -I` probes of `_neutralize` and the schema comparison;
no other gnd code run. T7 baseline feasibility unchecked (including `gnd diff` on
`v2_worked_example` itself). IK2–IK5 checked only for homes/lanes. A possible
cross-lane edge in unchanged r1 text (IK5 export lane reading IK3 `measure`-lane
manifests; gnd_arch.py:718 records `cross_lane`) was not raised; fixable in the
IK5 spec. No files created or modified.
