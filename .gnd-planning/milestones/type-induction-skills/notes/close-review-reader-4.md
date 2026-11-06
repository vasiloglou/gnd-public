# Close review, reader 4 of 4: compatibility, packaging, documentation

Subject: `git diff b733b2a..3665e28f` (type-induction-skills), HEAD 3665e28f, branch claude/ts4-spec.

## Verdict: approve-with-fixes

Packaging, the CLI surface, the wheel contents and the how-to all hold up against the code and the recordings. Every finding is minor or a nit: stale exit-code text, release-notes placement, and wording. None blocks the close.

## Findings

**F1 (minor): `gnd discover --help` exit-code text is stale for the new options.** `src/gnd/commands/discover.py`, the parser description (not in the diff). The help says "3 on an invalid model or population" and "11 when --out already exists". I reproduced two cases it does not cover. `--type-evidence` on an existing file exits 11 ("--type-evidence ev.json already exists"). A judgements file of the wrong kind exits 3 ("--shape-judgements: kind is 'duplicates', expected 'shapes'"). Fix: add "or a refused judgements file" to the 3 clause, and "--out or --type-evidence" to the 11 clause. Then regenerate the rf1 cli-help golden.

**F2 (minor): the exit table in discover.md still lists 11 for `--out` only.** `docs/reference/discover.md:333` reads "`--out` already exists". The Type evidence bullet ("An existing file is refused (11)") documents the `--type-evidence` case, but the table does not. Fix: "`--out` or `--type-evidence` already exists; nothing was written".

**F3 (minor): the release notes file the milestone under the previous milestone's heading.** `docs/release-notes.md:40-62`. The three new bullets (Type evidence, Type judgements, Two judgement skills) sit under "## Unreleased: composition and type induction", whose lead is about composing documents. They also cite internal phase labels ("(type-induction-skills TS1)") where the sibling entries cite a public issue (`#73`, `#77`). Fix: give the milestone its own "Unreleased" section with a one-line lead and a link to the how-to. Cite the governing issue if there is one, and drop the phase labels from public text.

**F4 (nit): one sentence in the how-to mixes the two rounds.** `docs/how-to/judge-induced-fact-types.md:521` says "g2's `distinct` and g3's `skip`". The `distinct` is g2 of the duplicates round and the `skip` is g3 of the multi-valued round, but the sentence names no round. Fix: "the duplicates round's g2 `distinct` and the multi-valued round's g3 `skip`".

**F5 (nit): the how-to says "Claude Code" skills.** `docs/how-to/judge-induced-fact-types.md:12-13` calls the skills "two packaged Claude Code skills". They also install under `.codex/skills` (doctor shows codex/project current=18). The recordings are Claude Code sessions, so "packaged skills, recorded here in Claude Code" would be accurate.

**F6 (nit, existed before this milestone): a stale comment in test_install.py.** `tests/test_install.py:53-55` says "The fifteen directory names … WHICH fourteen were placed", but the frozenset now has 18. The milestone touched the set next to it, so this is a good moment to fix the comment.

**F7 (hypothesis, out of the milestone's stated scope but justified): the IL6 census test is now frozen.** `tests/test_il6_skill_census.py` pins its git reads to `MILESTONE_LAST = 7818be1b…` and drops the `CURRENT`/dirty-file crediting. The reason is stated (spec D4: a new packaged skill must not fail a closed census). The cost is that the test no longer checks the live tree, and a shallow clone without that commit would fail it. I accept this as recorded. I did not test a shallow clone.

## What I checked and found clean

- **Skill inventory:** 18 directories under `src/gnd/skills`. `.claude/skills` and `.codex/skills` each hold exactly 18 relative symlinks `../../src/gnd/skills/<name>`, the two new ones included, with no strays. `uv run gnd doctor --project` reports both project scopes "installed (symlink mode) current=18" and the global scopes not installed. The AGENTS.md table (+2 rows) and the docs/agents/index.md table (+2 rows) match the shipped names, and the commands and exit codes in those rows match the CLI.
- **Pinned counts:**
  - EXPECTED_SKILL_FILE_COUNT is 69 in test_install and test_doctor_uninstall, which equals `find src/gnd/skills -type f | wc -l` = 69.
  - EXPECTED_RELATIVE_LINK_COUNT is 228.
  - Skill-name counts are 16 to 18 everywhere: marketplace, scaffold, public inventory, distribution.
  - VENDORED_SCHEMAS gains both type schemas, and the MANIFEST_SHA256 note is updated.
  - The marketplace `plugin.json` points `skills` at the source tree and needs no edit.
- **Tests:** test_packaged_skills, test_install, test_marketplace_plugins, test_doctor_uninstall, test_il6_skill_census, test_public_built_inventory, test_public_distribution, test_schema_sync, test_type_judgements_example, test_judge_fact_types_skill, test_model_multivalued_skill and test_rf1_pin_harness: 413 passed. test_rf1_layering, test_documentation_tutorials and test_tutorial_output_blocks: 128 passed. Layer, scaffold and distribution-runtime tests: 84 passed.
- **Wheel:** I built it into scratch only. It contains both SKILL.md files, `gnd/type-evidence.schema.json`, `gnd/type-judgements.schema.json`, their vendored copies under gnd-orm-core/references, and the whole `gnd/examples/type_judgements/` tree, so the how-to's `copytree` step works from an installed package.
- **CLI surface:** `gnd discover --help` lists exactly four new options, and docs/reference/cli.md and discover.md document all four. I reproduced each documented refusal:
  - a judgement option without `--type-evidence-in`, or `--type-evidence-in` alone: 64;
  - `--type-evidence` with `--type-evidence-in`: 64;
  - a non-distinct fifth path: 64;
  - the new options without `--families fact-type`: 64;
  - an existing evidence file: 11;
  - a symbolic link: 74;
  - a missing judgements or evidence file: 66;
  - the wrong kind: 3;
  - a binding mismatch under `GND_DISCLOSURE=customer`: 3, with the message naming `show_digests`.

  None of these is undocumented.
- **Tutorial:** `uv run python tools/run_tutorials.py --group type-judgements` passed 16 blocks. The printed outputs in the how-to match a live run, including the binding digest 75c734f8…, `support 36 of 37`, counterexample `ft0#132` and the preview's `affected` lines.
- **Recordings against the docs:**
  - Every agent quote in the how-to appears verbatim in the recorded streams. The duplicates quotes come from `evidence/TS3/recording-2` and the multi-valued quotes from `evidence/TS4/recording`.
  - The shipped `duplicates.judgements.json` is byte-identical to recording-2's (sha 9f4b7bfd…), and `shapes.judgements.json` to TS4's (cc11bd21…).
  - The example model and population files are byte-identical to `tests/fixtures/type-judgements/*`.
  - recording-2's manifest sources all match the current bytes. TS4's matches except `tools/record_judge_sessions.py`, which changed after that recording. The how-to's "false alarm" paragraph and `results.json` (`no_population_access: false`) disclose this accurately.
- **Leaks:** I checked every string value of both example populations, other than tokens that also appear in the model, against the how-to, the three SVGs, the example README and both judgements files. None appears. There are no absolute paths in the changed docs, skills, examples or SVGs, and no downstream consumer is named.
- **Links:** every relative link and anchor in the changed docs and skills resolves (`#type-evidence`, `#type-judgements`, `#proposing-fact-types-from-generic-rows`, the SVG assets, `evolve-policy.md`, `grow-a-model.md`). Every GitHub blob/tree link points to a file that exists in the tree. The zensical nav entry is added.
- **Claims against the code:** discover.md, the release notes, capabilities.md, compose-documents.md, disclosure.md and the gnd-orm-core and gnd-model-evolve skill edits describe what the CLI does, including the distinct and duplicate rendering, many-to-many with a spanning uniqueness, `judged_skip`, and refusal on truncated evidence. "rai-orm-from-schema" is the repository's existing dialect name. I found no promised behaviour that the CLI lacks.
- **Outside scope:** beyond F7, the diff only adds two modules to `tools/gnd_layers.json`, adds two successor files to `tests/support/pyrel_application_successors.py`, regenerates the rf1 goldens for the new options, and adds the tutorial group. All of these follow from the milestone.

The untracked `.gnd-planning/milestones/type-induction-skills/evidence/close/` is not mine; I wrote nothing in the repository.
