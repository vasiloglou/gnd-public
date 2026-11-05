# TS4 adversarial review (one reviewer)

One reviewer is one reviewer. The report is kept below verbatim, except that
the session scratch path is written `<scratch>` and the worktree path
`<worktree>`, as the reviewer was asked to write them. The reviewer ran as a
subagent over commit `3fe48d2a` (diff `16d478ad..3fe48d2a`), before the
recorded runs. It edited nothing in the worktree and made no paid model call.
Its probe scripts lived under `<scratch>/review-ts4` and are not kept; the
phase record names the regression test for each finding.

---

One reviewer is one reviewer.

TS4 review of commit 3fe48d2a (diff 16d478ad..3fe48d2a). I found four issues. None of them stops the planned recording from passing. F1 and F2 are rule defects in the skill that the fixture never reaches. F3 is a gap in what the tests and fixture can detect. F4 is left over from TS3 F5, and the TS4 recorder entry inherits it. None repeats a TS3 finding that was already fixed. `<scratch>` is `<scratch>/review-ts4`. The probe scripts are `<scratch>/bin/{judge.py,run.sh,mutate.py,popscan.py}`. `judge.py` applies S1–S4 literally to an evidence file and writes `shapes.json`. `run.sh DIR ev|judge FILE` runs `gnd discover` with `--type-evidence` or with `--type-evidence-in` + `--shape-judgements`.

## Findings

**F1 — `src/gnd/skills/gnd-model-multivalued/SKILL.md:137-138` (with spec D3) — hardening.** The skill says a `null` pair overlap "does not stop S3" because the candidate's other role "is not of the value's kind, so it cannot hold these pairs". That reason is false when the candidate's value role is redacted. `docs/reference/discover.md:202` states the overlap is "always `null` when that role is redacted", and `type_evidence.py:85` agrees. In that case S3 gives `many-to-many` for an attribute the candidate already holds completely, and the CLI accepts it. The result is a duplicate fact type, which is what S2 is meant to prevent. Ternary candidates and reflexive binary candidates also get `null`, for structural reasons, not because the kind differs.
- Repro: copy the `multi-valued` fixture into `<scratch>/redact` and add `redact: true` to `item_has_label`'s `label` role. Then run `run.sh <scratch>/redact ev; python3 -I <scratch>/bin/judge.py <scratch>/redact; run.sh <scratch>/redact judge shapes.json`.
- Observed: g1's only holder `item_has_label` now has `pairs: None` (it held 48 of 48 before). The rules give g1 S3 `many-to-many`, discover exits 0 and proposes `item_has_attribute_induced_1` (support 48/48), a copy of `item_has_label`.
- Expected: a `null` overlap on a binary candidate whose other role is redacted should go to S4 (ask), not S3. The candidate's roles are in the evidence and `redact` is in the model, so the skill can tell this case apart.

**F2 — `SKILL.md:117-121` (S1) — completeness.** S1 always gives `skip` and says the attribute is "already induced… from this very attribute". It never checks which uniqueness the earlier fact type carries. Suppose round one induced the attribute as a functional binary, with a uniqueness on the entity role only, and the data is now multi-valued. S1 skips silently, and the CLI refuses the only other verdict. The model keeps a single-role uniqueness that the population now violates, and the skill gives the user no route: neither "the shape changed, evolve that fact type's uniqueness via gnd-model-evolve" nor "fix the population".
- Repro: in `<scratch>/functional` (the fixture with `each_tag_once_per_item.roles: [entity]`), run `run.sh . ev; judge.py .; run.sh . judge shapes.json`, then repeat with g0 set to `many-to-many`. Separately run `gnd check model.orm.yaml items.population.json`.
- Observed: `skip` exits 0; `many-to-many` exits 3 ("already induced as item_has_attribute_induced_0"); `gnd check` reports `[fail] … constraints[0] … entity 'I-00' has 2 facts`.
- Expected: S1 should read the induced fact type's uniqueness in the model. When that uniqueness is single-role, S1 should still give `skip` but tell the user the attribute is now multi-valued and point to gnd-model-evolve or to fixing the population.

**F3 — `tests/test_model_multivalued_skill.py:63-80` and `tests/fixtures/type-judgements/multi-valued/` — completeness.** I mutated the skill in the clone and ran the TS4 test file, `test_packaged_skills.py` and `test_skill_prose_sync.py`, excluding T14/T15 (`python3 -I <scratch>/bin/mutate.py <scratch>/repo <scratch>/mt`).
- **Survived, 11 of 13:**
  - S2's verdict flipped to `many-to-many`;
  - S3's "times ten" changed to "times two";
  - S3's "no candidate's `overlap.pairs` is above 0" deleted;
  - `kind: shapes` changed to `duplicates`;
  - `judge.skill` set to `gnd-judge-fact-types`;
  - "in order" deleted from step 3;
  - "never over an existing file" deleted;
  - S4's "correct the population and make new evidence" deleted;
  - S4's truncation clause deleted;
  - "there is no `of`" replaced by an `of` instruction;
  - the null-overlap paragraph reversed.
- **Caught:** S3's verdict changed to `skip`, and S1 moved after S3.
- **After recording:** the manifest's source digest will catch any byte change. But a re-recording over a mutated skill would still match the key for several of these mutations, because the fixture never decides them. No group has a partial overlap (so the S4-partial branch and S3's no-overlap clause are never exercised). No group is truncated or has a `null` overlap. g2 (12 of 24) and g3 (1 of 24) sit on the same side of any threshold between 1/24 and 1/2.
- Expected: pin the S2 verdict, S3's no-overlap clause and multiplier, `kind: shapes` and `judge.skill` as key clauses. Add a partial-overlap group to the fixture, or record it as a declared branch with no case.

**F4 — `tools/record_judge_sessions.py:222-224` (the TS4 entry reuses it) — hardening, left over from TS3 F5.** The needles in `no_population_access` only match paths that contain `population`, `answer-key`, the fixture directory, the evidence directory or `ROOT/tests`. `Read`, `Glob` and `Grep` are allowed on any path (`record_skill_sessions.TOOLS`), and `kept_stream` replaces tool output from outside the workspace with its size. The canary check therefore cannot see a read from outside the workspace either.
- Repro: `<scratch>/repo/.venv/bin/python -I <scratch>/bin/popscan.py <scratch>/repo`. It runs synthetic tool calls through the real `forbidden_calls`.
- Observed as missed: `Grep {"pattern":"m5q","path":ROOT,"glob":"**/*.json"}` (reads the population and the answer key), `Glob {"pattern":"**/multi-valued/*","path":ROOT}`, a `Read` of ROOT's parent, and `Grep` over `<home>`. Only the full fixture path in a Bash command was flagged.
- Expected: also flag any tool call whose path is outside the workspace and the plugin copy, or confine Read, Glob and Grep to the workspace.

## Checked and found sound
- **Gate list (TS3's list plus the new file):** 856 passed and 5 failed, all 5 being the expected T14/T15 recording tests.
- **Other tests:** the 24 further test files that read skills, AGENTS.md or the counts all pass (1043 passed). These include `test_public_built_inventory`, `test_public_distribution` and `test_release_acceptance`. I left out `test_rf7_structure`, which is known red at base. No pin was missed. Both discovery links exist, and the AGENTS.md, `docs/agents/index.md` and orm-core rows are present.
- **Recorder generalization:**
  - The TS3 entry keeps its defaults: `--skill` defaults to `judge-fact-types`; `results.json` still has `fixture: "round-two"` and the same skill string; the manifest sources still name `gnd-judge-fact-types/SKILL.md` and round-two; and the module-level `CANARIES` and `FIXTURE` are still exported.
  - `--help` works.
  - The TS3 entry accepts the TS4 spec as its gate, as spec §6.6 allows.
  - The checks for edited inputs (per-file SHA-256) and the population copy deleted before turn 1 still hold for TS4.
  - The TS3 recording's manifest was already stale against the current skill and recorder bytes at base, and the TS3 test does not compare source digests. That is TS3-Q3 / §6.7, not a regression.
- **Rules against the CLI:**
  - S1 matches the CLI's D4 check (generic and `same_attribute`), so the TS3 F4 lesson is applied.
  - Where the evidence lists no candidate but the model's `induced_from` still names the attribute, `truncated>0` sends S3 to S4. A user answer there is refused (exit 3), as documented.
  - "Distinct pairs" is `rows - exact_repeats`, which matches `types.py:193`.
  - With no candidates, S3 applies vacuously, and that is accepted.
- **Disclosure and value probes:**
  - Customer mode (`GND_DISCLOSURE=customer`): `same_attribute` is still given, the key's verdicts are reproduced and the run exits 0.
  - Values that are numeric strings (`<scratch>/numeric`), with rationales in the skill's style ("half the items", group and rule ids): exits 0.
- **Fixture:** it reproduces §6.5 (g0 S1, g1 S2 48/48, g2 S3 12 of 24 with one repeat, g3 S4 1 of 24), and the key's verdicts give discover exit 0.
- **Anonymity:** no absolute path, user name, email or downstream application name in 16d478ad..3fe48d2a. T17 now covers the whole `evidence/TS4` directory, which addresses the TS3 F8 gap.

## Hygiene
- I edited nothing in the worktree, and `git status` there is clean.
- Everything I wrote is under `<scratch>/review-ts4/`: the `repo/` clone at 3fe48d2a (its skill restored, plus a `.venv` symlink to the worktree's venv), the `redact/`, `functional/`, `customer/`, `numeric/` probe directories, `bin/` scripts, `mt/`, `pt/`, `pt2/`, `tmp/` (pytest and TMPDIR), and `other_tests.out`.
- I made no `claude` or paid model call, ran the recorder only with `--help`, and read no `.env`.
- I did not run T19 (the zensical build plus `check_docs`), because it writes a site.
