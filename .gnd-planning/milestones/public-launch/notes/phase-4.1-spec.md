# Phase 4.1 — Explain GND and teach application development

Status: owner-decided (2026-10-03); implementation authorized by the complete
plan reproduced in the owner's “PLEASE IMPLEMENT THIS PLAN” message. The
technical decomposition below records that approval; it is not a claim that
the owner read these later bytes. Spec prose is the approval instrument because
this phase teaches existing runtime contracts; no new public format or exit
contract is introduced. Existing accepting/refusing fixtures and negative
controls verify the tutorial instrumentation before relying on its output.

## Provenance and obligations

Target base: e88d477d32b46c63c367719e3abe8e74adabc96a. Effective plan is r1 plus
r2/r3 and the owner-approved r4 documentation amendment. Source P4 preparation
006 and P3 acceptance 007 (public counterparts 003/004) remain historical.
No panel has reviewed this specification. Source archives/current dirty work
are excluded; a dedicated target worktree contains this phase only.

| Source | Obligation and discharge |
|---|---|
| Thesis, sections 1/4, r4 C1 | Product overview, concepts, workflow diagram and independent reader review |
| r4 C2, P4-C1 | Six BookRec chapters, three expense chapters, checked Markdown commands and installed tutorial resources |
| r4 C3, P4-C3 | Capability matrix and seven-function API reference; existing normative skill sources stay authoritative |
| r4 C4, section 9 | Strict site build, internal links, desktop/mobile/search/diagram inspection |
| r4 C5, P4-C2/C4/C5 | Candidate identity, affected wheel checks, updated current status, clear publication handoff |
| Sections 2/3, r2 A3/A4 | Source amendment/spec with public copy digests; preserve unit authority and historical records |
| Section 5 | Site links to packaged skills; no edits to installer links or unmanaged skill twins |
| Section 6 | Source-independent examples, accurate claims, bounded resources, no private run archives or duplicate publisher |
| Section 7 | No semantics redesign, private product migration, archive campaign, native/provider run or certification |
| Section 8 | Spec before implementation; one independent terminal reviewer, reproduction, refactoring and record |
| Section 10 PL-D5/D9/D10 | Preserve package names/version; describe measured profiles; no outreach/trials/publication inferred |
| P3 record | Acceptance binds old artifacts; changed resources require affected checks and later candidate sign-off |
| R1/R2 | Preserve old checkouts; selected synthetic public inputs, no archive copies |
| R3/R4 | No runtime authority/API/exit changes; public-owned documentation/examples only |
| R5/R6 | Installed tutorials independent of source; behavioral expected results and instrument negative controls |
| R7/R8 | Honest current evidence and explicit agent handoffs; installer/skill trees unchanged |
| R9/R10 | Focused tests; local build, package download, terminal review and preview only |
| R11/R12 | Compact evidence; site build-only CI and a disabled-by-default publication condition |

## Standing rules

Totality: tutorial runners reject missing blocks, unexpected exits and bad links.
Input caps: command timeouts and bounded tutorial fixtures; no arbitrary tree crawl.
Validation order: validate/check before tutorial output publication.
One policy walk: examples call existing GND APIs, not a second rule evaluator.
One normative home: canonical skills/code define schemas; guides teach and link.
Measure representation: verify installed wheel resources and outputs, not just
source-tree execution. One reviewer is one reviewer; model agreement is advisory.

## Goal and design

P4.1-C1–C5 discharge through the gates below, with actual exits in the record.

- Site: zensical.toml, docs/ and README.md, local CSS/SVG diagrams. Dedicated
  locked docs dependency group; build command uv run --group docs zensical build
  --strict. Curated navigation: Overview, Getting started, BookRec, Expense,
  Guides, Reference, Contributing. GitHub Pages build artifacts only until P5.
- BookRec: src/gnd/examples/bookrec/ synthetic models/populations, CLI/library
  extension, architecture contract and evolution checkpoint/proposal. Public
  base successor expanded to unread/adult guards, genre warnings, changed rule,
  derived eligibility and all-eligible completeness. No ranking-quality claim.
- Expense: src/gnd/examples/expense/ synthetic model, approval/report CLI,
  architecture contract, valid/invalid state checks and currency evolution.
  Explain explicit post-operation checks; no storage/UI product claim.
- Both paths use package resource copying, gnd codegen/conformance, explicit
  skill prompts, complete checkpoints and exercises. Application code calls the
  stable gnd.api where suitable. No new runtime public API or semantic family.
- Reference: all seven gnd.api exports and capability groups in the approved
  plan; callable illustrative examples are executable or explicitly contextual.
- Tests: execute marked tutorial shell/Python fences in document order with
  expected exits; assert concrete populations, verdicts, repairs and conformance.
  Reuse source fixtures as prior art, not mandatory old-checkout inputs.

## Decisions

D1 owner (2026-10-03): developers building applications; BookRec flagship plus
expense tutorial. D2 owner: Zensical site plus README; publish in P5.
D3 owner: agent-assisted prompts plus credential-free checkpoints.
D4 owner: existing semantics, no live-provider prerequisite or certification.
D5 implementation: existing stable API, synthetic public inputs and local assets;
no auto-generated API documentation import of private surfaces.
D6 implementation: one terminal Codex reviewer (xhigh), at most one follow-up;
reproduce blocking findings, defer unrelated completeness. No new plan panel:
this records the direct owner amendment, not a new milestone plan review claim.

## Verification selection

| Obligation | Disposition / command and expected result | Boundary / invalidation |
|---|---|---|
| C2/C3/C5 | run: uv run pytest -q tests/test_documentation_tutorials.py tests/test_release_docs.py tests/test_release_examples.py tests/test_public_generated_examples.py --tb=short; exit 0 | Docs, examples and installed API use; any changed command/model/output |
| C4 | run: uv run --group docs zensical build --strict; exit 0; internal link checker and negative controls | Navigation, assets, links, docs dependency lock |
| C2/C5 | run: build release wheel/sdist and separate sdist wheel; tutorial tests in fresh installed environments outside both repos; exit 0 | Changed packaged examples/build lock; retain artifact hashes |
| C1/C4 | run: independent terminal review and rendered desktop/mobile/search check | Reviewed pages and built bytes; no claim about outside trial users |
| Changed Python | run: uv run ruff check new tutorial/support/test code; exit 0 | Authored Python only |
| Runtime regression | cadence: existing explicitly configured CI selection; no new local full-suite claim | Runtime unchanged; docs group/runtime lock diff inspected |
| Candidate sign-off | cadence: Phase 4 exact-artifact sign-off | New artifacts are preparation artifacts until sign-off |

Meaningful tutorial cases: valid output, unread/adult rejection, advisory genre
warning, same population rejected after tightening a rule, eligible recommendation
omitted, valid/invalid expense approval, currency absent/present after evolution,
conformance success and deliberate derived-file drift. Instrument negative controls:
missing tutorial block, wrong expected exit, broken link and changed output.
No full historical suite, recertification, native compiler or paid provider lane.

## Out of scope and size

No public release/site deployment, source retirement, new GND runtime features,
application hosting or paid model calls. Existing external-user trial gap remains.
Estimate: 35–50 documentation pages/assets (up to 6,000 prose/config lines),
up to 1,800 tutorial/test/tool Python lines and 2,500 model/checkpoint lines.
These are planning estimates, not reasons to cut useful explanations or tests;
report measured differences. Existing repository/package size ceilings remain.

## Implementability sweep and approval

Existing public codegen/application fixtures, source BookRec models and currency
proposals establish feasible primitives. Zensical supports Markdown, navigation,
search and strict builds. No criterion requires a paid call, publication, new
runtime semantics or a later optional phase. The approved plan's scope is
implementable. Approval is the explicit owner implementation request above.

## Implementation findings

Record discoveries and changed estimates here as work proceeds.

- Rendering finding: custom runnable fence suffixes were accepted by the test
  parser but confused Zensical's Markdown parser. Reproduced in the quickstart
  browser view; changed metadata to HTML comments adjacent to ordinary fences.
  Both document execution and rendered structure are checked.
- Expense evolution: missing coverage returns 2; partial currency facts return
  1; complete currency facts return 0. The tutorial teaches these existing
  distinctions. BookRec's explicit evolution returns conformance drift before
  regeneration, as expected.
- The browser skill's legacy IAB connection was unavailable. The current CUA
  browser surface opened the same local preview successfully.

- Installed identity checks must compare path components rather than string
  prefixes: a sibling candidate directory starts with the checkout's name.
  The failed first instrument run and positive/negative containment test
  establish the corrected boundary.
- Final measurement: 44 docs/assets/config files, 3,755 lines; 15 changed/new
  Python files, 1,172 whole-file lines; 20 model/checkpoint resources, 3,326 lines.
  The resource estimate grows by 826 lines (33.04%) because both evolving models
  and complete synthetic populations are supplied as readable checkpoints.
  Wheel payload is 5,691,929 bytes, below the 12 MiB preparation ceiling.
- The independent terminal attempt failed before review (unsupported model).
  Automatic approval review blocked the supported-model retry over the private
  repository; owner permission was requested. No completed terminal opinion
  or panel is inferred from that attempt.
