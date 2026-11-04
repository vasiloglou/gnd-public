---
milestone: composition-and-type-induction
station: "phase-CT4"
skill: "n/a -- repository development under process-milestone auto=true, not a gnd-solve station"
scope: phase-CT4
date: 2026-11-04
gate:
  command: "uv run pytest -q tests/test_discover_fact_type_family.py tests/test_discover.py tests/test_ike_q3.py tests/test_evolve_additive_policy.py tests/test_evolve_shape_matches.py tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py tests/test_conformance_payload.py"
  exit: 0
  output: "579 passed in 87.22s"
  note: >-
    The spec's verification selection (the discover test files expand to
    test_discover and the new family file) plus test_ike_q3 for O16. Run
    after the review fixes. Docs: strict build clean; 13933 links; ruff clean
    on the changed modules.
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "outside CT4's impact closure"
evidence:
  - path: .gnd-planning/milestones/composition-and-type-induction/notes/phase-CT4-spec.md
    sha256: 3403c43eff5249bef8141c7517c4966e3e56030ff1a1f8d743fbe6eec35fb9f7
  - path: .gnd-planning/milestones/composition-and-type-induction/notes/phase-CT4-claude-review.md
    sha256: f06d48a36916c92a361cefaa40d92b6a43cf62a17a5771483dd26a0e871ba704
  - path: .gnd-planning/milestones/composition-and-type-induction/evidence/CT4/capture_parity.py
    sha256: df7a6d5058f6d79e4458e91b87ece092d6cd77dfc18728ccc50a42193603a209
  - path: .gnd-planning/milestones/composition-and-type-induction/evidence/CT4/parity-a2e44f8.json
    sha256: a5275efeabbf7fadca05a35bdf5cb3be9a221aac8f481f0c5521e2b8b8c8ec40
  - path: .gnd-planning/milestones/composition-and-type-induction/evidence/CT4/parity-after.json
    sha256: a093457d2119fc05d83a29650335c09419206f2167605e7e075d200ce98a312c
  - path: .gnd-planning/milestones/composition-and-type-induction/evidence/CT4/dynamic-query-successor.json
    sha256: 32a4351de30079a17f54b7923c61838bb27fe5a45c5cf6f98de02d4b14e3388c
  - path: src/gnd/discover/types.py
    sha256: 4f8ba1313360003157ed6f506589f87b6cd3b19bb985df36b4cd75af76e0b13b
  - path: src/gnd/discover/service.py
    sha256: 9962b417658252fdc5fff853769cd0be472527217d2a30e287ca92f5ae7d476f
  - path: src/gnd/discover/output.py
    sha256: dc187b1beb99f069cf71baf10172f4605f892fd70c65d3c97588b68161f9ace7
  - path: src/gnd/commands/discover.py
    sha256: 72f4734db5ab2f48c941360b0a00bb48ba349f274337d5206117a3af659b0ba6
  - path: src/gnd/discover.schema.json
    sha256: c4c62cb27a0b6bb132c854e8d99604d067a858bd6a1bb7d6643271133a95795a
  - path: src/gnd/disclosure.py
    sha256: 4d17febd1db670d67712ac576d11ea4134b5379f97bd9cdacd7479dcb9bd6687
  - path: tests/test_discover_fact_type_family.py
    sha256: 6206122c537d796464e00e7eaaec2ded9347739db60cf87f9a4447b9a86e7173
  - path: docs/reference/discover.md
    sha256: cf1d12c5c2b66d2ab487ece96cbe680fba7229e233cddd42636c4b4a4a20eab5
  - path: tests/fixtures/rf1-pins/goldens.sha256
    sha256: 8303920f5034054dc9c5ce195b1e352702bf7945d24b3cb3f3c294620a8c2c10
---

# Phase CT4: fact-type proposals in discover

**Claim.** `gnd discover --families fact-type` on a model with a declared
generic fact type proposes, for each attribute value whose rows cover at
least `--min-support` distinct entities (default 20) with one value type and
one value per entity, an `ADD` of a binary fact type with an opaque id and a
placeholder reading plus a deontic induced uniqueness on its entity role.
The proposal passes `gnd evolve preview --policy additive` and applies, alone
or with other families. The report's `fact_type_proposals` lists opaque row
ids and the attribute's SHA-256; the raw value appears only as
`values_allowed(--show-values)` decides. Without the family, the 20-row IK4
discover table is identical to `a2e44f8` except E1 and E6, usage errors
whose usage text lists the new options (E1: CT2's `compose`; E6: the two new
discover options); same exits and stdout. The focused gate exits 0.

**Authority.** Plan r3 `(a1)`. Spec r1 under **delegated approval
(auto=true)** `(d1)` 2026-11-04 (digest in the spec); an agent ruling under
the owner's "Yes, run it auto", not the owner's personal reading. D2
re-argues the plan's "co-proposed" clause, as the plan gate allows.

## What changed

- `src/gnd/discover/types.py` (new, lane `discover`): `generic_declarations`,
  `propose`.
- `gnd.discover.service`, `gnd.discover.output`, `gnd.commands.discover`:
  the opt-in family, `--min-support`, `--show-values`, the report key, a
  text line, the proposal budget.
- `discover.schema.json`: the optional key and `fact-type` in
  `bounds.families`.
- Disclosure: `gnd discover` is a `site` row with a new `option`
  convention (CT-D13 (a)); the generated table, `T15`'s case map and a
  discharging test; T26 arithmetic `49 - 16 - 4`.
- Docs: discover reference section; release note. Pins: RF1 `discover`
  goldens and `tree.json`; manifest digest; RF6 successor (30 added, 1
  removed); layer map row.

## Criteria

| Criterion | Evidence | Result |
|---|---|---|
| CT4-C1 declaration parsed and validated; undeclared yields nothing | four invalid forms (3); undeclared test | holds |
| CT4-C2 support at threshold - 1 and threshold; rows not entities; mixed type | grouping tests | holds; mixed type shown on an unvalidated view (a validated typed role cannot hold two JSON types) |
| CT4-C3 migration report; canary; unset, internal, customer | values test | holds |
| CT4-C4 additive preview passes; deontic envelope; shape match reported | additive, shape and combined-apply tests | holds |
| CT4-C5 redacted attribute skipped and counted | redaction test | holds |
| CT4-C6 without the family unchanged | `evidence/CT4/parity-*.json` | holds, two usage lines as stated |
| CT4-C7 IKE-Q3 | `tests/test_ike_q3.py` (already resolved at `a2e44f8`) | holds |

**Deviations, recorded.** Standing rule 2 says the family adds its row
visits to discover's `work` counters; it reports `row_visits` in its own key
instead, so the `work` totals keep their meaning (docs say so). The shape
test reports both proposed-together groups against the existing fact type;
"another group proposed" is covered by the combined-families test instead.
The new-value-type branch is unreachable on a validated population (a
group's JSON type always agrees with the typed value role) and stays as a
guard.

## Review

One local reviewer agent, read-only: **approve-with-fixes**
([review](notes/phase-CT4-claude-review.md)); 17 mutants, 13 killed.

| Finding | Disposition |
|---|---|
| F1 an existing `<generic>_induced_<n>` id crashed discover | fixed: a clash takes the next suffix; test |
| F2 the family ignored the proposal size budget | fixed: counted `over_budget` within the same budget as the other families; test |
| F3 a multi-valued attribute proposed a failing uniqueness | ruled D5 under the delegation: counted `multi_valued`, not proposed, as the other families emit only passing candidates; test |
| F4 redaction of the entity or value role was dropped | fixed: copied to the new roles; test |
| F5 `declared` convention described discover wrongly | fixed: new `option` convention with its own table text and case |
| F6 E1 and E6 differences | confirmed usage text only; recorded |
| F7 text output and rationale | fixed: a `FACT TYPES` text line; rationale says "operations" only when the family adds any (the old wording is kept otherwise, CT-R1) |
| F8 rule 2 deviation | recorded above and in the docs |
| F9 test gaps | combined preview and apply, collision, budget, redaction, multi-valued tests added; the `Number`/`Integer` and new-value-type mutants stay alive on the unreachable branch |
| F10 informational | accepted: gaps in `n` follow skipped groups and are stable; the digest is unsalted, so a low-entropy attribute can be guessed from it, which matches the other families' SHA-256 evidence |

## Refactoring review

One grouping pass feeds support, type consistency and migration rows. The
family reuses discover's induction envelope fields and evolve's ADD
operations; no second proposal builder. One new module, mapped at `lanes`.

## Questions

| ID | Question | Owner |
|---|---|---|
| CT4-Q1 | Salt or omit the attribute SHA-256 for low-entropy attribute names | owner, with the disclosure policy |

## Boundary

Not merged, released or certified.
