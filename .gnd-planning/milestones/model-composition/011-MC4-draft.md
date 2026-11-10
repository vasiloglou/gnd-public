---
milestone: model-composition
station: "MC4-draft early owner documentation checkpoint"
skill: "n/a -- repository development checkpoint, not a gnd-solve station"
scope: MC4-draft
date: 2026-11-10
gates:
  - command: ".venv/bin/python .gnd-planning/milestones/model-composition/evidence/MC4-draft/run.py /tmp/mc4-draft-final-receipt.json"
    exit: 0
    output: "6 tutorial blocks passed"
  - command: ".venv/bin/zensical build -f .mc4-draft-zensical.toml"
    exit: 0
    note: "Temporary root config uses retained render-config.toml bytes; project-local output copied to /private/tmp/mc4-draft-site, then the temporary config/output removed."
  - command: ".venv/bin/pytest -q tests/test_mc1_guards.py::test_R30_examples_do_not_declare_includes --tb=short"
    exit: 1
    output: "1 failed in 0.14s"
    note: "New draft include example invalidates MC1's temporary blanket scan. Final MC4 successor remains owed; this preview is unmerged."
  - command: "python3 scripts/components_index.py changed --base origin/main --strict"
    exit: 0
    note: "No runtime module changes or assignments; no failures/warnings/rereads."
  - command: "git diff --check"
    exit: 0
evidence:
  - path: .gnd-planning/milestones/model-composition/evidence/MC4-draft/manifest.json
    sha256: ecb60c439ebb3966a60ff9292d6bc81a921ddb4b9b286adf13a0122856451280
  - path: .gnd-planning/milestones/model-composition/notes/model-composition-plan.md
    sha256: 775b5f16b81283cb5634124254c8ec6df8a53735192af946887db369dda1efe9
---

# Claim

After the owner-authorized MC1 merge, the early how-to's six command blocks exit as narrated and compare their shown output; the rendered review copy is prepared for the owner's actual reaction.

## Gate output (verbatim)

    share-a-vocabulary.md: selected executable blocks passed
    6 tutorial blocks passed

    Build started
    Build finished in 0.51s
    No issues found

The separate temporary R30 scan exits1; its exact output is retained losslessly in example-scan-red.json. Whitespace checking exits0. Catalog checking exits0 with zero failures, warnings or rereads. This is a checkpoint, not a completed MC4 phase.

## Scope and provenance

The owner explicitly answered “Approve merging this fixed head” for PR154 at55a7d89a12a5500775602e137ee97bf9559c544c. The PR head matched; GitHub returned no review threads or submitted reviews. The SHA-guarded merge succeeded as d5ca5d9a77d07778ce37a1a00dec20eaa2faadb3, which was fetched before this checkpoint branch was created.

Plan amendment a1 selects this early review copy after MC1 merges. The new data splits the existing rule_check vocabulary/rule example. The project owns no_import_loops and its original rationale/remedy; the scanner vocabulary has no project rules. The first data-authoring attempt retained an empty rejected_proposals section from the old example and correctly refused include:forbidden-section; the vocabulary now omits it and the authentic pin was recomputed. No loader policy changed. The staged check also caught a trailing space emitted by the YAML authoring tool before any checkpoint commit. The vocabulary was normalized, its authentic pin and displayed project file updated, and the six blocks/render repeated on those exact final bytes.

Browser-use's in-app backend was unavailable. The separate Playwright fallback opened the generated page from a localhost-only server and captured the rendered result; no external site or account was modified. Screenshot/HTML identities and their outside-history limitation are explicit in the manifest. The page covers MC1 validate/check only and visibly marks the MC3 re-pin half as pending. Nav, runner group registration, release notes, the full update figure and final documentation gates belong to MC4.

## Refuted premise and integration obligation

MC1's R30 temporary assertion that no packaged example declares includes is invalidated by this required draft example. The checkpoint preserves that failing observation rather than silently weakening the guard in a docs/data-only change. Before integration, MC4 must replace the blanket assertion with an exact rooted example successor, exercise validate/check on it, and retain all legacy raw-example negative controls. The preview PR remains draft and is not selected for merge. This changes no main-branch assurance claim.

## Boundary

The owner has not yet reacted to the rendered copy. Preparation, six executed blocks and a browser inspection do not manufacture that reaction. It remains a hard prerequisite before MC4 continues. There is no independent checkpoint reviewer opinion, finished re-pin story, business tutorial decision, new runtime code, milestone close, publication or certification. MC2's separate spec/corpus and red harness remain on their own topic branch.

## Open questions

- Owner: react to the rendered review copy; record the actual reply in the MC4 spec before its implementation.
- MC4: finish the re-pin half after MC3, exact R30 successor, final figure, nav/runner/release integration and all documentation gates; dispose MD17 explicitly.
- Close: retain the guard-scan integration finding and ensure the final full candidate comparison covers actual integrated bytes.
