---
milestone: reviewed-vocabulary-growth
station: "phase-VG5"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-VG5
date: 2026-11-23
gates:
  - command: "uv run pytest -q tests/test_vg5_seeded_growth_example.py tests/test_growth_example.py tests/test_unattended_growth_guidance.py tests/test_ir1_judgments_includes.py --tb=short"
    exit: 0
    output: "49 passed in 7.89s"
    note: "the plan's section 9 VG5 lane with the new file, at 0fc30381"
  - command: "uv run pytest -q tests/test_agent_recordings.py tests/test_discover.py tests/test_ik_close.py tests/test_il6_walk.py tests/test_mc1_guards.py tests/test_pyrel_application_corpus.py tests/test_pyrel_learning_path.py tests/test_pyrel_native_seam.py tests/test_pyrel_rules_calendar.py tests/test_pyrel_rules_derivations.py tests/test_pyrel_tutorial_experience.py tests/test_ready_projects.py tests/test_rule_verbalization.py tests/test_vg1_object_type_scaling.py --tb=line -p no:cacheprovider"
    exit: 0
    output: "536 passed, 111 deselected in 162.84s (0:02:42)"
    note: "every test that scans the packaged examples, at b36b446d; the two new models enter their scans"
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=line"
    exit: 0
    output: "679 passed, 2 deselected in 100.50s (0:01:40)"
  - command: "uv run ruff check src tests tools"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base 5265f476 --strict"
    exit: 0
    output: "changed against 5265f476 (5265f47): 41 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request, or the milestone-close default lane"
  reason: "VG5 adds an example, a builder, pages and test inventory entries; no rule or route changes"
evidence:
  - path: src/gnd/examples/seeded_growth/root.orm.yaml
    sha256: 5bc77662bebc77c7dbd2ccb7dbf712f21add117d4b4787547da1e026a24a147f
  - path: src/gnd/examples/seeded_growth/seed.orm.yaml
    sha256: 69c31805fc53de4c2b6717bb10c00ecda1b4e8a523661ffc27428c8e5dc82457
  - path: src/gnd/examples/seeded_growth/round-2.proposal.json
    sha256: a962864bbe733754e24ab1933c8ab17e26f9ede63fef868058b88f8c0c976d56
  - path: src/gnd/examples/seeded_growth/README.md
    sha256: 43aa2f437b0e8a977a51f229781a5dd4f40c29f4e14f0794e5265368ed24c35e
  - path: tools/build_seeded_growth_example.py
    sha256: 6ca03d5a5051ab77fbdd9c188f995a0876b22a7c79415b5b2c23064405efa397
  - path: src/gnd/skills/gnd-model-from-text/references/unattended-growth.md
    sha256: 3356dd23dae636f79c531d5e372719769e5c7cc7fc834afaaab7a13265832c06
  - path: src/gnd/skills/gnd-orm-core/references/representation-format.md
    sha256: ef2997c3a71f32cbaa41ea76eb11162fad910ef4766406e69e9b698cfe05c680
  - path: tests/test_vg5_seeded_growth_example.py
    sha256: 63467451a12dad655df74340b34c5feb4bfaf23119de8883567c4febc3bd5bed
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/issue-replies.md
    sha256: 972f2af3dd59fe786220296a247569ab72237510085a9fcf83ae72f2ba612044
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/phase-VG5-spec.md
    sha256: 0437e85bf6573f09665879b56831edf85bb1d76d6f8f5de34f516ab5b6b5e481
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG5-r1/review.md
    sha256: 77f430f431fbb7534bfdd294c5ad59a071c6d0affdf941c38891b65ee3eb36e7
  - path: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG5-r1/FINDINGS.md
    sha256: fd8faee72eccbc2480846f79ae927ee2320b573e9852b6de49249f7d64eb7040
---

# Claim

At `0fc30381`, the VG5 lane exited 0 (49 passed), the guard block exited 0
(679 passed), `uv run ruff check src tests tools` exited 0 and the
component-index check exited 0. The packaged seeded-growth example's built
files rebuild byte-identically; its two rounds preview and apply, exit 0;
the grown root validates with both documents and `--require-documents`,
`gnd check` over its population exits 0, and `gnd judgments check` admits
(outcome 0).

## What shipped

- `src/gnd/examples/seeded_growth/`: `seed.orm.yaml` (issue 222's reviewed
  seed), `root.orm.yaml` (unattended, includes the seed, nothing of its own,
  no document), two round documents and proposals, `population.json`,
  `policy.json`, `receipts.json` and a README with the eight commands.
- `tools/build_seeded_growth_example.py`: builds the proposals, the
  population and the judgment inputs, deterministically; spans come from the
  documents' canonical text.
- Pages: `unattended-growth.md`, "Starting from a reviewed vocabulary",
  citing the two homes; the include route list gains `gnd coverage`,
  `gnd evolve` and `gnd discover` (review r1, F1); `docs/agents/model-from-text.md`
  and `docs/agents/evolve.md` link the section; one release-notes entry.
- `notes/issue-replies.md`: replies to issues 221, 222 and 218, drafted for
  the owner, naming pull requests 239 and 240 and that none is released.
- Inventories (named for literature-reading-reference LR3's rebase):
  `tests/test_mc1_guards.py` R30 lists `seeded_growth/root.orm.yaml` among
  the packaged include roots; `tests/test_packaged_skills.py` adds the
  growth section's two citations as `VG5_GROWTH_EDGES`.
- `tests/test_vg5_seeded_growth_example.py`: T1–T5 and two review
  regressions; `tests/support/markdown_sections.py`: the fence-aware section
  reader, moved from VG2's test and used by both (review r1, F2).

Measured size: 821 lines added and 40 removed under `src`, `tests` and
`tools` (`git diff --stat 5265f476 0fc30381`), most of it the example's
built JSON; the builder is 170 lines, against an estimate of 150.

## Gate output (verbatim)

    $ uv run pytest -q tests/test_vg5_seeded_growth_example.py tests/test_growth_example.py tests/test_unattended_growth_guidance.py tests/test_ir1_judgments_includes.py --tb=short
    49 passed in 7.89s
    $ uv run pytest -q <the 14 test files that scan the packaged examples> --tb=line -p no:cacheprovider
    536 passed, 111 deselected in 162.84s (0:02:42)
    $ uv run pytest -q <the project.md guard block> --tb=line
    679 passed, 2 deselected in 100.50s (0:01:40)
    $ uv run ruff check src tests tools
    All checks passed!
    $ python3 scripts/components_index.py changed --base 5265f476 --strict
    changed against 5265f476 (5265f47): 41 file(s) differ; 0 to fix, 0 warning(s), 0 to reread

## The criteria

| Criterion | Test | Result |
|---|---|---|
| VG5-C1 | T1: rebuild the five built files; both rounds; the published root equals round 2's candidate | byte-identical; preview and apply exit 0 |
| VG5-C2 | T2: validate with both documents and `--require-documents`; `gnd check`; `gnd judgments check` | exit 0 with the `INCLUDE` line; two constraints pass; outcome 0, admission true |
| VG5-C3 | T3, R1-F1: the list names `gnd coverage`, `gnd evolve` and `gnd discover`; coverage, evolve preview and discover resolve the example root; `gnd codegen` refuses it | as stated (narrower than the row, spec finding 4) |
| VG5-C4 | T4: one reply per issue naming its pull request and "release" | present |
| pages | T5: the section cites both homes and the example; both agents pages link it | present |

## Review

One reviewer is one reviewer: Codex (default model, effort high, read-only)
through the review helper, round `notes/reviews/phase-VG5-r1/`, over the
diff from `5265f476` to the working tree at `b36b446d`. Verdict
`CHANGES_REQUESTED`, two findings, both reproduced and fixed at `0fc30381`
with regression tests that failed first:

- F1, completeness: the route list omitted `gnd discover`, which resolves
  an include root.
- F2, hardening: T4 read a heading inside a fenced block as a section
  boundary.

The reviewer checked and found true: the five built files rebuild in
memory; the starting root validates; both previews give valid candidates
with no policy issue; the grown candidate validates with both documents,
checks, judges (admission true) and covers, exit 0; codegen refuses the root;
the page links and the link inventory; span probes over canonical Unicode,
multi-line excerpts, missing and overlapping quotes. It could not run apply
or finalize, or the fixture suite, because the brief forbids writes; it
substituted the grown candidate in memory. `review.md` and `review.log`
were sanitized by the helper.

## Refactoring review

Refactor executed: the fence-aware Markdown section reader moved from
`tests/test_vg2_evolve_sources.py` to `tests/support/markdown_sections.py`,
so VG2's page test and VG5's reply test read sections one way. Behaviour
preserved: VG2's tests pass unchanged on it.

## Boundary -- what this phase does NOT establish

- One reviewer is one reviewer. The fix commit `0fc30381` carries no review
  opinion; the round read `b36b446d`.
- The replies are drafts; nothing was posted.
- T3 does not run every listed route on the example (spec finding 4); the
  route list was checked against the reviewer's probe and the existing
  include-root tests, not a census of every CLI command.
- The README's commands run from a copy whose path crosses no symlink;
  `gnd evolve` refuses one that does.

## Open questions

- A census of every CLI route against include roots would make the route
  list mechanical rather than reviewed. Target: the milestone close, or a
  maintenance pass if the owner wants one.
