---
milestone: unattended-model-growth
station: "phase-UG4"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-UG4
date: 2026-11-09
gate:
  command: "uv run pytest -q -p no:cacheprovider tests/test_documentation_tutorials.py tests/test_packaged_skills.py tests/test_skill_prose_sync.py tests/test_ik_close.py tests/test_public_binding_prose.py tests/test_install.py tests/test_doctor_uninstall.py tests/test_public_installer.py tests/test_ik6_skill_census.py tests/test_il6_skill_census.py tests/test_unattended_growth_guidance.py tests/test_unattended_model_growth_acceptance.py tests/test_unattended_mode.py --tb=short"
  exit: 0
  output: "501 passed in 95.35s (0:01:35)"
  base: "ad454305 (main after PR 149)"
selection:
  - {obligation: "UG4-C2 G-docs: the growth tutorial", disposition: run, command: "uv run python tools/run_tutorials.py --group growth", exit: 0, note: "12 tutorial blocks passed"}
  - {obligation: "UG4-C2 G-docs: the site build", disposition: run, command: "uv run --group docs zensical build --strict", exit: 0, note: "Build finished"}
  - {obligation: "UG4-C2 G-docs: links and anchors", disposition: run, command: "uv run python tools/check_docs.py site", exit: 0, note: "15231 local links/assets/anchors checked"}
  - {obligation: "UG4-C3 G-skills, G-ug, T3, T4", disposition: run, command: "the gate above", exit: 0}
  - {obligation: "G-skills: gnd doctor --project", disposition: run, command: "uv run gnd doctor --project", exit: 11, note: "machine-local: this worktree's link receipt (placed 2026-10-13) records 2 collisions under .claude/skills and 18 under .codex/skills; UG4 adds, renames and removes no packaged file, and the install and doctor tests in the gate pass (spec F-i3)"}
  - {obligation: "G-lint", disposition: run, command: "uv run ruff check tests/test_unattended_growth_guidance.py", exit: 0, note: "All checks passed!"}
  - {obligation: "G-components", disposition: run, command: "python3 scripts/components_index.py changed --base main --strict", exit: 0, note: "14 files differ; 0 to fix, 0 warnings, 0 to reread"}
  - {obligation: "G-anon", disposition: run, note: "UG1's digest-set method over every file changed since ad454305 and the commit messages; 0 hits; positive control found"}
  - {obligation: "phase-diff review", disposition: run, note: "one reviewer, Codex CLI; notes/phase-UG4-codex-review.md"}
  - {obligation: "full tutorial run, full default lane, distribution lane, certification", disposition: cadence, note: "not selected: no explicit owner request; the growth group is the only tutorial whose page changed"}
evidence:
  - {path: src/gnd/skills/gnd-model-from-text/references/unattended-growth.md, sha256: 65e3c19e7ad675db522b5d2e098a57bbe76a4a9b95f21a735599102b6a0a1647}
  - {path: tests/test_unattended_growth_guidance.py, sha256: bf0e8ef1d18296276fec09e6fa351e43738e5c7a1bcc49b0c6e35667d184a005}
  - {path: tests/test_packaged_skills.py, sha256: 1d65afbc10939c0aa014ce3285d7a41e52b812c165cd997177424c0c71c55222}
  - {path: .gnd-planning/milestones/unattended-model-growth/notes/ug4-issue-followups.md, sha256: 701a3e0acf41256dc78a80a91cce431798d7715df3d8d12696371f1073135d2d}
  - {path: .gnd-planning/milestones/unattended-model-growth/notes/phase-UG4-codex-review.md, sha256: c318822c8baaf4ca08e841a43d6b2a28d87de51da7b9a98efa2bc31370755406}
---

# Claim

The packaged skill now describes the unattended loop as shipped (plan §2.4, §4 UG4). A round
declares its new document with a `source-document` add in its proposal; the old out-of-band
header edit is named as earlier behavior. The gate is `gnd validate --document ...
--require-documents`, then `gnd evolve preview --policy additive --shape-report` (with
`--check-population` for a constraint on populated data) and `apply` repeating the policy
options. A host acts on a shape match in one of three logged ways (UG-D6 (a), issue 76). The
section on constraints over populated fact types gives the `--check-population` route (issue
104 item 5). Every page that states the additive guarantee says it covers the facts GND can
see, the contract's own sentence included (UG4-C5). Follow-ups for issues 74, 76 and 104 are
drafted and not posted.

Authority: spec r1 approved `(o)` 2026-11-09 ("Approve all as proposed"), UG4-D1 to D7.
`auto=false`. Not merged; merge needs the owner.

## Named criteria

| Criterion | Result |
|---|---|
| UG4-C1 one home | Every new sentence links its home: the contract for the policy, the population check and the locator; `representation-format.md` for the counts; `unattended-growth.md` for the procedure. No matrix row is restated (author check against the spec §6 table) |
| UG4-C2 docs gates | the three G-docs commands exit 0 |
| UG4-C3 skill pins | the gate exits 0; the routing pin moved knowingly (spec F-i1) |
| UG4-C4 dispositions | each drafted follow-up checked against the UG1 matrix and the UG2/UG3 records; #74's condition corrected by review finding 5 |
| UG4-C5 wording | `git grep -n -i "interpretable\|keeps every fact\|invalidate facts\|invalidate the facts" -- docs src/gnd/skills`, release notes excepted as history: `docs/agents/evolve.md:38-39` ("earlier facts it can see"), `docs/reference/evolve-policy.md:4-6`, `gnd-model-evolve/SKILL.md:125-127`, the contract `:229-231` and `:339`; each qualified |

## Review

Instrument: one reviewer in a different tool (Codex CLI, `gpt-6.1-sol`, reasoning `xhigh`,
read-only sandbox, prompt on stdin). **One reviewer is one reviewer; this is not a panel.** Three
blocking and two hardening findings, all reproduced and fixed:

- **1:** "then `apply` with the same options" after a preview with `--shape-report` would make
  apply exit 64; the sentence predates UG4. Fixed.
- **2:** the guard missed wrapped spans, fenced lines and invalid literal values. Fixed, with six
  mutation cases; three of the four new inputs pass the old guard silently (measured).
- **3:** the "Constraints travel with their fact type" paragraph still stated the refusal without
  the clean-population exception. Fixed by scoping both statements.
- **4, 5:** the how-to's sample-rows sentence and #74's warning condition were too broad. Fixed.

Verbatim output and dispositions: [phase-UG4-codex-review.md](notes/phase-UG4-codex-review.md).
The fixes were not re-reviewed; the gate above runs over them.

## Refactoring review

None needed, argued from what the phase touched: Markdown in ten files, one test guard and one
pinned inventory. The guard reuses RF1's parser walk (`test_rf1_cli_pins._walk`) instead of a
second CLI model. One structure the review exposed is a doc-structure point, not code: the
reference stated the policy's refusal in its own words in two places, which is how finding 3
arose; the fix scopes both to a link instead of adding a third statement.

## Size

Spec §10 estimate: 80 to 120 Markdown lines, about 40 for the note, about 30 test lines.
Measured against `ad454305` under `docs`, `src` and `tests`: 182 lines added, 35 removed (the
guard, with its mutation table, is about 100 of them); the follow-ups note is 70 lines. Above
the estimate in tests, because of review finding 2.

## Departures from the spec, each recorded in its findings

- F-i1: the routing pin moved (235 to 238 links).
- F-i3: `gnd doctor --project` exits 11 for machine-local reasons in this worktree.
- F-i4: §6.1 (b)'s "same options" and the guard's scope corrected after review.

## Boundary

- UG4 only. The milestone close (record, question sweep, close review, close parity table) is
  not done.
- The follow-ups are drafted, not posted; no issue is commented on or closed (UG-D0).
- UG3-Q1, UG3-Q2, UG3-Q3, UG2-Q1 and UG2-Q2 stay with the close sweep.
- Not merged, released or certified.

## Open questions

| ID | Question | Target |
|---|---|---|
| UG4-Q1 | This worktree's discovery-link receipts are stale (doctor exit 11); re-adopting them is a local, not a repository, change | owner, local |
| UG3-Q1 to Q3, UG2-Q1, UG2-Q2, UG-Q6, UG-Q7 | carried | as recorded |
