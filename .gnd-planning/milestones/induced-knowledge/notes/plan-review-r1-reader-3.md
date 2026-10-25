# Reader 3 — protocol, authority, compatibility and privacy

Reviewed plan SHA-256 `26fa91632e5ee637b1949ad4e8dd6ba25daac57180280328e3d04c1e050a1814`
and IK1 spec SHA-256 `f79d6375630e8706a9a3fe88af7669b3f0a81fcbb446ec0e1d55d4df22b8cec0`
— both match the bytes at HEAD `0e2ba79`.

**Verdict: approve-with-fixes** within the protocol/authority/compatibility/privacy lens.

Scope: plan, IK1 spec, milestone README and the new PROJECT.md section; issue #34;
start-milestone SKILL.md, spec-note contract, standing-rules headings,
review-convergence (grep), the head of the incremental-evaluation plan. Read-only:
`gh pr view 35`, `git log a22ccde..HEAD`, `evolve/service.py` `_enforce_d12`/`_surface_index`,
`population.py` cap, `exits.py`, `diff.schema.json`, `extract/projection.py`.
No files created or modified. (The untracked `evidence/` directory observed was
created by the coordinator's review snapshot.)

## Findings

- **R3-F1** (completeness, medium): Request 2 is presented as discharged while
  its PR is open. Plan L75 "Request 2 discharged outside this milestone"; L90
  IK-O2 owner "none"; L211 "discharged by PR #35"; README L13 "was fixed in PR #35";
  PROJECT.md "was fixed separately". `gh pr view 35` → `state: OPEN, mergedAt: null`;
  `git log a22ccde..HEAD` shows only `0e2ba79`, so the stated "plus PR #35" baseline
  (L5–6) is not an ancestor of the reviewed branch. If #35 is rejected or reworked,
  request 2 has no owner, and IK1 T7's "byte-identical to baseline" (spec L99) is
  ambiguous because #35 re-pins frozen goldens (`c792f2c`). Fix: "fix proposed in
  PR #35 (open)", a fallback owner, and an exact T7 baseline commit.
- **R3-F2** (hardening, medium): `src/gnd/diff.schema.json` pins `schema_version` to
  `const "gnd-diff/1"` with top-level `additionalProperties: false`. Spec L71–74 adds
  optional `annotations` with no version change; IK-R3 (L58) routes "any version bump"
  to D1, but D1 (L285) covers only the model version. Any consumer validating
  against the current gnd-diff/1 schema rejects new output containing `annotations`.
  IK1-D2 (L86) should state the version reading and its cost.
- **R3-F3** (hardening, medium): Absent-description compatibility is incompletely
  pinned. T7 (spec L99) covers verbalization and codegen/conformance fixtures only;
  the extraction projection digest (bound into extraction sidecars; spec L68–69),
  `gnd diff` output, and the evolve surface index (spec L76–77 adds
  `object_types[<id>].description` without saying "only when present") are not
  covered. Existing extraction sidecars or evolve blast-radius evidence could change
  for description-free models with no failing test, contradicting IK-R3 and
  predicate 1 (L25–26).
- **R3-F4** (hardening, medium, privacy): L116 puts `evidence: [{path, sha256}]`,
  `examples` and `counterexamples` in model provenance, and IK4 (L132–134) emits
  counterexamples from real populations. IK-R10 (L65) covers fixtures/names only.
  Host filesystem paths and proprietary values would be persisted into model files
  and evolve proposals. Add a rule (relative/opaque ids, values by digest) to IK2-C1/IK4.
- **R3-F5** (completeness, medium, privacy): The source issue itself names the
  downstream application and its parent repository in its Context paragraph. The
  plan correctly does not repeat them and links the issue (L74), but IK-O14 (L102)
  governs only future text; there is no recorded owner disposition of the source.
- **R3-F6** (completeness, low): Two issue notes have no disposition: the
  "1,880 uniqueness constraints" (no import/reconcile obligation or scale target)
  and the "Without it" fallbacks (no compatibility or migration statement for text
  in `provenance`/`deontic_note` or host sidecars).
- **R3-F7** (completeness, low): IK1 spec section order differs from the contract:
  Goal is §3 and standing rules §4 (L24, L33); the contract orders standing rules (4)
  before goal (5).
- **R3-F8** (completeness, low): IK1 has no docs/skill row. Standing rule 5 names
  `representation-format.md` as the normative home (spec L41) and IK1 changes the
  gnd-extract projection, yet obligations (L14–22) and design (L44–79) contain no
  reference or skill edit; plan §5 (L222–223) promises an inspection IK1 never binds.
- **R3-F9** (completeness, low): Plan L281 "All rows are proposed/open"; README L16
  and PROJECT.md list D7 pending; next action (L293–294) orders owner review of D1–D7
  before plan review. The owner selected the instrument on 2026-10-23 and review is
  running before D1–D6. An amendment must record D7 as owner-selected with date and
  scope, and state that amended bytes carry no review opinion.

## Reasons supporting the verdict

- Sections 0–10 present (L52–294); obligation table cites sources (L85–102); the
  implementability sweep is labelled author inspection (L267–277); exact commands
  are honestly unresolved (L265).
- D1–D7 explicitly proposed/open (L281) with costs and blocking points.
- No invented approval or status: "No review has run; no approval exists" (L6),
  repeated in the spec (L9), README and PROJECT.md.
- `auto=false` (L4, L246); planning only; topic branch and PR (L251); merge,
  release and certification are separate owner acts (L251–252, L242).
- IK-R1 and D2 keep induced elements proposed/deontic; IK-O10 matches `_enforce_d12`.
- IK-R3/IK3-C3 synth-sidecar byte identity; D5 keeps positional refs; IK6-C3
  covers API/CLI pins and RF source-scan controls; IK-R4 schema twins.
- Only IK1 is detailed; it has status line (L3), discharge column, six standing
  rules by name, tests with exits (T2, T9) and decisions with exit-code costs.
- Requests 1 and 3–6 each map to a phase; D-12 and GR-12 gaps are surfaced as decisions.

## Limits

Advisory, one lens; not approval of plan bytes. No tests run, no fixtures
validated, `gnd measure --labels` signature not checked. PR #35 state as observed
2026-10-23. ILP and discovery technical merits not assessed.
