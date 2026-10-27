# Reader 2 -- implementability, pins and homes

Retained text of the reader's returned report. Local edits: scratch paths read
`<scratch>`, and quoted Markdown link syntax is escaped as `]\(` so the
repository's reference check does not read it as a live link.

Reviewed plan SHA-256 526ab075473ab60cf2e8090fe7c0f177aa54e4a82b7fce83af1cb50d1919c411 and spec SHA-256 0510b5275622f8b38aff8865500d40601c9ea4e3ce3b2e58ed2fcf5b9363515a. Both match.

**Verdict: request-changes**

Scope: I read both subjects in full and inspected every pin file named in the brief, plus `test_public_packaged_command_help.py`, `test_development_scaffold.py`, `test_contributor_preparation.py`, `test_public_workflow_claim_routes.py`, `test_public_distribution.py`, `src/gnd/install.py` usage, the plugin manifests, `docs/agents/index.md` and the docs CI workflow.

All probes ran in local clones under `<scratch>/reader2/`:
- `repo` is the baseline at 3b3dc36.
- `probe` adds only a dummy `gnd-induce/SKILL.md`, committed.
- `probe2` is a spec-shaped implementation: a skill with the four fenced `gnd` lines and every out-edge of §6.2, the five sibling route sentences, the vendored labels schema (D3), D9, the D8 census pin, all §6.3 pin edits, the AGENTS.md row, and links from `gnd install --symlink --project --force`.

On `probe2`, the 14-file gate subset passed (609 tests). `gnd doctor --project` reported current=17. `uv run --group docs zensical build --strict` reported "No issues found". `tools/check_docs.py site` ran clean (11417 links checked). The 54 skill-related test files passed except the items noted below. Getting there needed pin edits the spec does not list (F2, F3). I did not finish a full 16k-test run: the machine was shared, so I stopped it and ran the 53/54 skill-related files instead.

## Findings

- **R2-F1** (blocking, high): R-g cannot satisfy T8's "each appears once in the packaged tree and only in gnd-induce/SKILL.md".
  - Where: spec 99, 89, 191.
  - Evidence: `src/gnd/skills/gnd-export/SKILL.md:27` already reads "This skill never touches git." word for word. The spec's own "Record and commit" row (line 89) repeats the same sentence inside the new skill, so it would appear twice in that file too.
  - Background: the shared denial is deliberately repeated, because `RECORD_ROUTES` (test_packaged_skills.py:203) matches `never touches git` in 13 skills.
  - Fix: drop R-g from T8's one-home set (RECORD_ROUTES already covers it), or limit T8 to R-a..R-f.

- **R2-F2** (blocking, high): the §6.3 pin table misses literals that go red when one skill is added. The gate cannot go green with only the edits the spec names. Reproduced on `probe`/`probe2`:
  - `tests/test_install.py:51` `EXPECTED_SKILL_FILE_COUNT = 65` breaks 6 install tests.
  - `tests/test_doctor_uninstall.py:47` `EXPECTED_SKILL_FILE_COUNT = 65`. The spec names only the doctor name set and the link maps.
  - `tests/test_verification_fixes.py:18` `EXPECTED_SKILL_FILE_COUNT = 65`. The spec names only `EXPECTED_SKILL_FILES`.
  - `tests/test_public_built_inventory.py:306-312` has `== 65` twice and `== 16` twice. With the spec's pins applied, it fails "assert 67 == 65" under `-m distribution`.
  - `tests/test_development_scaffold.py:109` `assert len(names) == 16`. This fails `test_twins_modes_and_generated_links` even after the installer runs (confirmed on `probe2`: "17 == 16"). This file is not in the gate either.
  - Also stale: the test name `test_the_packaged_tree_holds_exactly_the_fifteen_named_skills` and its messages saying "fifteen".
  - Fix: add all of these to §6.3 and T3/T4/T16, add `test_development_scaffold.py` to the gate, and re-size §10. It is more than 8 files.

- **R2-F3** (blocking, high): the planning tree already turns a default-lane test red.
  - Where: spec 115-119, 163.
  - Evidence: `tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap` fails at baseline 3b3dc36. `check_references` walks every `.md`, including `.gnd-planning`. The committed `notes/phase-IS1-spec.md` carries live links `]\(../gnd-induce/SKILL.md)` (×5) and `]\(src/gnd/skills/gnd-induce/SKILL.md)`, which never resolve from `notes/`, even after IS1 lands.
  - The untracked `evidence/plan-review-r1/` snapshots add the same links. They also add `../../../../docs/tutorials/learn-rules.md` from the plan copy, which is broken because the copy sits one level deeper.
  - Fix: write the proposed sentences in the spec without live link syntax (escape or describe them), and repair the snapshot links (or keep them out of `.md` link form) before they are committed.

- **R2-F4** (blocking, medium): the alternative in D9 ("leave both unexercised", plan 337) is not available once the skill has fenced `gnd export ilp` / `gnd import ilp-rules` lines.
  - Evidence: without D9, `test_public_packaged_command_help.py::test_every_documented_option_exists_on_the_subcommand_it_is_used_with` fails for both lines. `gnd export --help` does not list `--labels/--target/--out`, and `gnd import --help` does not list `--reported-coverage/--actor/--requested-at`.
  - With D9, all 317 guard/help cases pass, apart from the expected per-skill pin.
  - The plan's stated cost is wrong: none of the 30 fenced snippets at baseline start with `gnd export` or `gnd import` (all mentions are inline). D9 therefore changes no existing snippet.
  - Fix: make D9 mandatory, or say the alternative requires no fenced export/import lines, and correct the cost text.

- **R2-F5** (hardening, high): T7's help-exit claim is checked by a file outside the gate.
  - Where: spec 190, 208.
  - Evidence: help-form execution and option checking live in `tests/test_public_packaged_command_help.py`. `test_public_packaged_invocation_guards.py` only discovers snippets, normalises them and checks the floors.
  - Fix: add `test_public_packaged_command_help.py` to gate line 1.

- **R2-F6** (hardening, medium): gate line 1 lists `tests/test_public_distribution_runtime.py`, which contributes nothing there.
  - Evidence: it is `pytestmark = distribution`, so the default addopts deselect it ("no tests collected (20 deselected)").
  - Fix: move it to the `-m distribution` line.
  - Do not add `test_public_distribution.py` to that line: it has 6 failures at baseline, from its stale b3 attribution manifest.
  - The docs gate (spec 64, 194) must be `uv run --group docs zensical build --strict`, as `.github/workflows/docs.yml:26` does. Bare `zensical` is not on the default environment's path.

- **R2-F7** (hardening, medium): two new `ROUTING_MATRIX` rows would pass on text that already exists. `_routing_text` searches the whole file.
  - In `gnd-orm-core/SKILL.md:16`, "Routing only." already exists.
  - In `gnd-export/SKILL.md:37`, "learner" already exists.
  - Those rows therefore prove only that the link exists.
  - The `gnd-induce→gnd-export` boundary `not this skill` has no sentence anywhere in §6.1; the description says "Not for … (gnd-export)". The implementer would have to invent one.
  - Fix: add the exact out-route sentences to §6.1 (e.g. "Derivation and Lean exports are not this skill: [gnd-export]\(../gnd-export/SKILL.md).") and tie each regex to its new sentence, e.g. `host labels.{0,200}never applies`.

- **R2-F8** (hardening, low): the orm-core route is written as a prose sentence, but the workflow index (`gnd-orm-core/SKILL.md:18-36`) is a three-column table where each row states its trigger, claim and "never".
  - `tests/test_public_workflow_claim_routes.py:19-21` requires the line just before the `gnd-export` row to end with `|\n`. Prose inserted between rows breaks it.
  - Reproduced: a table row `| [\`../gnd-induce/SKILL.md\`]\(../gnd-induce/SKILL.md) | … host labels … | … Routing only |` passes every test.
  - Fix: specify a table row, and add that test to the gate.

- **R2-F9** (hardening, medium): T15/D3 does not fit `tests/test_schema_sync.py`.
  - That file pairs the canonical copy in `gnd-orm-core/references/` with a vendored copy in `src/gnd/schema/`, and its doctrine is "edit the CANONICAL (skill) copy, regenerate the vendored one".
  - The runtime file is `src/gnd/labels.schema.json` (loaded at `measure/labels.py:146`), not `src/gnd/schema/`. D3 reverses which copy is the source of truth.
  - The orm-core Reference index also labels every schema there "Canonical machine spec … (vendored copy)".
  - Fix: state which copy is canonical, add a separate pair (not a `SCHEMA_PAIRS` entry), and say whether orm-core's Reference index gets a row.

- **R2-F10** (completeness, medium): the red-first claim for T9 cannot hold as written.
  - Where: spec 61, 179, 192.
  - Reasoning: once the D8 pin is committed before the skill exists, the pinned census passes both before and after. Only the unpinned census goes red when the skill is added.
  - Reproduced: the unpinned census fails 6 cases on `probe`. My pinned variant (ls-tree, diff and log at 077f46e, no dirty credit) passes 56/56 with `test_ik_close` and `test_ik6_walk`, both with uncommitted and with committed `(IS1)` sibling edits.
  - So D8 works.
  - Fixes:
    - Define T9's red evidence as "the unmodified census with the skill present".
    - Use the full 40-hex SHA, as `MILESTONE_FIRST` does.
    - Keep `test_t5`, which reads the working tree and still passes after the additive edits.

- **R2-F11** (completeness, low): small inaccuracies.
  - Spec 15 says "29-snippet floor measured". 29 is the pinned floor; the measured count at 077f46e is 30, so the new floor should be 34.
  - Plan 315 says docs are cited by "GitHub URL (as gnd-export does)". `gnd-export` cites `--help` only; no packaged skill links a repo docs page by URL.
  - The `docs/agents/index.md` row (IS1-C7) has no test pinning it.

Confirmed satisfiable as written:
- 13 new edges with D3 (12 without), giving 211 → 224 link occurrences and 65 → 67 files.
- The `RECORD_ROUTES` and denials additions.
- The orm-core index test.
- The frontmatter parses: two keys, 847-character description.
- Every out-edge resolves inside the tree.
- No `FROZEN_SKILLS` member is touched.
- The plugin manifests point at `./src/gnd/skills/`, so no manifest edit is needed.
- The installer creates `.claude/skills/gnd-induce` and `.codex/skills/gnd-induce`, which must then be `git add`ed (the doctor test requires tracked symlinks).
- T14 can import `ABSOLUTE` and `DOWNSTREAM` from `test_ik6_walk.py`.
