---
milestone: public-launch
station: phase-4.1
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-4.1-preparation
date: 2026-10-03
gate:
  command: ".venv/bin/python -m pytest -q tests/test_documentation_tutorials.py tests/test_bookrec_tutorial.py tests/test_expense_tutorial.py tests/test_release_docs.py tests/test_release_examples.py tests/test_public_generated_examples.py tests/test_contributor_preparation.py tests/test_development_scaffold.py::test_readme_links_to_executable_getting_started --tb=short"
  exit: 0
  output: "66 passed in 26.25s"
slow_cadence:
  command: "existing repository CI selection"
  trigger: "separately configured CI on the candidate pull request"
  reason: "runtime core unchanged; selected tutorial, packaging, documentation and downstream controls run locally; no local full-suite or certification claim"
evidence:
  - path: evidence/phase-4.1/implementation-sha256.json
    sha256: bfb2280ac35df47e6ea7e1652b2d0035ee764b9cf4e5943b4149e7d7d6ec8263
  - path: evidence/phase-4.1/evidence-sha256.json
    sha256: f154d0ecb64a092640668a95f93bc440c1accdd113d589161044f4cbe24b62f5
  - path: notes/phase-4.1-spec.md
    sha256: c0097e9b864d27f3002c1a4afcfef68fe0245ea31a014209c79ede92226548af
  - path: notes/public-launch-plan-r4-amendments.md
    sha256: 3cd39b5150c064bd3077701ae90d6ec227359ed2d41c0e6c9868d866caf01e73
---
# Phase 4.1 — documentation and application preparation

The focused implementation gate passes. This record does **not** close the
phase protocol: its independent terminal review remains unavailable pending
owner permission after automatic approval review blocked the retry. The owner
approved implementation of the full Phase 4.1 plan; no new runtime semantics,
publication or certification is inferred. This is an append-only preparation
record, preserving earlier public records 001–004 and source records 001–007.

## What shipped

- Zensical 0.0.67 in a dedicated locked docs group, with responsive navigation,
  search, light/dark palettes, code copy, local diagrams and system fonts.
  README and overview explain purpose, developer/agent roles and applications.
- Six connected BookRec chapters with deterministic library/CLI, hard unread/age
  failures, advisory genre fit, a real modify-only evolution, and a separate
  derived eligibility/all-eligible completeness checkpoint. No top-k claim.
- Three expense chapters with policy checks, approval/report CLI, an additive
  currency evolution linked to a generated project, drift and explicit repair.
- Dispatch first check and repair; release transfer example; nine task guides;
  capability/CLI/formats references; executable examples for all seven API
  functions. Optional provider/native prerequisites and limits are adjacent.
- Tests execute Markdown and README code directly, including concrete assertions
  and deliberate nonzero exits. Instrument controls reject missing/malformed
  blocks, wrong exits, failed shell intermediates, missing sites, bad anchors,
  fence leakage and source-checkout import origins.
- CI builds and retains documentation previews with SOURCE_COMMIT. Pages deploy
  is gated by manual dispatch, an explicit publish input, main and the repository
  variable GND_DOCS_PUBLISH. This phase did not enable it or deploy the site.
- Source-owned r4 amendment/spec/authorization with public counterparts. The
  pre-implementation spec is retained separately; authorization describes the
  owner's approved plan, not an invented approval of later implementation bytes.

## Gate output (verbatim summaries)

Focused command is in the header. Its complete selected output is retained:

```text
66 passed in 26.25s
```

`.venv/bin/python tools/check_installed_docs.py --out <new-candidate-directory>`:

```text
97 tutorial blocks passed
Both installed wheel origins passed the documented learning paths.
```

Each origin separately ran 97 blocks (README/dispatch 7, release 5, BookRec 46,
expense 30, Python API 8, walkthrough 1). Fresh Python 3.13.12 environments ran
outside the checkout, importing only their installed wheel. No editable install,
source PYTHONPATH, historical application checkout or provider call was needed.
The direct and sdist-built wheel digests match; all three artifact hashes and
payload size are in candidate.json. Artifact files are retained locally under
/private/tmp/gnd-phase41-final; they are preparation artifacts, not promoted files.

`NO_COLOR=1 .venv/bin/zensical build --strict`:

```text
Build started
No issues found
Build finished in 0.14s
```

`.venv/bin/python tools/check_docs.py site`:

```text
3499 local links/assets/anchors checked
```

`.venv/bin/ruff check tools/run_tutorials.py tools/check_docs.py tools/check_installed_docs.py tests/test_documentation_tutorials.py tests/test_bookrec_tutorial.py tests/test_expense_tutorial.py src/gnd/examples/bookrec src/gnd/examples/expense`:

```text
All checks passed!
```

No pre-existing locked dependency changed. Added packages belong to the docs
closure. No core src/gnd module or stable API changed.

## Criteria and review

C1 has a supplemental reader explanation retained in independent-reader.md.
That agent had authored the references, but not the overview; it is not the
protocol's separate terminal harness. C2/C3 have actual behavioral and installed
execution evidence. C4 has strict build, all local link/anchor/asset checks, and
sampled 1440x980/390x844 rendered inspection, including search, mobile navigation,
themes, diagrams and code. C5 has exact candidate identities, unchanged prior
acceptance, corrected current status and an explicit publication boundary.

The terminal command used stdin and a read-only sandbox but its initial model
was refused before review. The supported-model retry was blocked by automatic
approval review over private repository disclosure. Verification identified
OpenAI as the selected standard provider and confirmed the repository is private.
Explicit owner permission was requested; no rejected action was bypassed.
One completed reader audit is one audit, not a panel, external user trial or
completed terminal opinion. Review-attempt.txt records the limits.

## Measurements

44 documentation/assets/config files, 3,755 lines; 15 changed/new Python files,
1,172 whole-file lines; 20 model/checkpoint files, 3,326 lines. Resource lines
exceed the 2,500 estimate by 826 (33.04%) to retain complete readable evolution
models and populations. Wheel payload 5,691,929 bytes is below 12 MiB. Counts
exclude evidence/records and dependency lock data. They measure delivered files,
not authored semantic novelty.

## Refactoring review

What did this phase reveal about existing structure that should change?
No runtime refactor needed: tutorial applications call the existing stable
checker; versioned proposal helpers are explicitly labeled support contracts.
The phase adds one shared Markdown executor used by local tests and installed
validation, avoiding a second separately maintained tutorial script. The earlier
custom fence syntax was removed after its rendered failure, keeping one format.
Static current-status phrase tests were replaced by link/execution checks.

## Boundary — what this phase does NOT establish

No final Phase 4 sign-off, Phase 5 publication, production service, new GND API
or runtime semantics, live-provider/native run, external-user trial or certification.
Prior acceptance stays tied to its original bytes; changed resources have focused
checks, not inherited broad assurance. The apps use reviewed synthetic teaching
inputs and do not prove ranking quality, financial policy validity, actor identity,
concurrent transaction safety or facts' real-world truth. Conformance is static
agreement; session outcomes and verifier reports remain separate claims.

## Open questions

| Obligation | Target / resolution |
|---|---|
| Independent terminal review | Phase 4.1; awaits explicit permission after automatic review rejection; append a discharge record after review/fixes |
| Affected Ubuntu validation and required CI | Candidate PR; report actual result when available |
| Final exact candidate sign-off | Phase 4; retain/promote selected artifacts only after affected validation |
| Public site/package/service and external trials | Phase 5 and owner-selected trial scope; not activated here |

## Refuted premises

The test parser accepting custom fence suffixes did not prove rendered code was
usable: the site visibly leaked fences. Comment markers and a rendered negative
control repair that premise. String-prefix path exclusion incorrectly rejected a
sibling candidate directory; path-component containment now tests installed origin.
Neither discovery implied a runtime semantic change.
