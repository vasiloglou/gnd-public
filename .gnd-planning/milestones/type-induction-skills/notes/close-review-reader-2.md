# Close review, reader 2: TS3/TS4 skills and recorded evidence

Range `b733b2a..3665e28f`, HEAD `3665e28f`. Read-only. No paid calls, the recorder was not run live, no `.env` was read. Scratch work is under `close/r2/`.

## Verdict: approve-with-fixes

Both skills agree with the "Type judgements" contract on every branch their fixtures exercise. Both answer keys match evidence recomputed from the fixtures. Both recordings are clean: no leaked path, value or canary. Two rule gaps remain, both outside the fixtures. One lets a wrong verdict through (F1). The other leaves a dead end with no route (F2). The records also overstate two recorder claims (F3, F4).

## Findings

**F1 (major): R3 in gnd-judge-fact-types has no redacted-null guard. TS4's F1 fix was never ported to it.**
- File: `src/gnd/skills/gnd-judge-fact-types/SKILL.md:106-112`.
- The problem: R3 returns `distinct` when "at least one candidate has a non-null `overlap.pairs` and every such candidate has 0". It ignores `null` overlaps. A candidate whose other role is redacted always gets `null` (discover.md:207-208), yet it may hold every pair. `gnd-model-multivalued` S3 was fixed for exactly this (SKILL.md:143-145, TS4 F1). R3 was not. The plan's §2.3 says the judge should ask when the evidence is too thin.
- Reproduction (`close/r2/redact/`): add `redact: true` to `item_has_colour` in the round-two model and rebuild the evidence. The candidates per group become `g1: [(induced_0, 0), (item_has_colour, None)]`, and the same for g3. The key says g1 is `duplicate` of item_has_colour by R2, and g3 is an R4 ask. R3 now decides both as `distinct`, and the CLI accepts `distinct`. The result is a proposed fact type that duplicates item_has_colour. Only review would stop it.
- Fix: add S3's clause to R3: "a `null` overlap on a candidate whose other role is redacted in the model stops R3; ask". Pin it in the T9 clause table, as TS4 did.

**F2 (minor): a retyped induced fact type leaves a group with no verdict the CLI accepts, and the skill gives no route.**
- Files: `src/gnd/discover/type_judgements.py:129-136` (D4 uses `induced` from the whole model) and `SKILL.md:98-112`. Candidates are only "fact types the group's entity type plays" (discover.md:203).
- Reproduction (`close/r2/retype/`): retype `item_has_attribute_induced_0`'s entity role to a new `gadget` type. discover.md:154 itself suggests retyping. The evidence for g0 then shows only `(item_has_colour, 0, origin None)`, so R3 gives `distinct`. The CLI exits 3 with "group g0 was already induced as item_has_attribute_induced_0". `duplicate` can only name a candidate, and the induced fact type is not one, so g0 has no valid duplicates verdict. The skill's handoff ("fix the judgements file") has nowhere to go.
- Fix: either have the evidence carry an `already_induced` list per group, or add a skill sentence. The sentence would say that this refusal names a fact type outside the candidates; the user then reverts the retype or routes through gnd-model-evolve. Mostly a CLI-owner question.

**F3 (minor): the TS4 record claims the manifest binds the current recorder. It does not.**
- Files: `005-phase-TS4.md:144-146` says "both recordings' manifests bind the recorder's bytes and the tests check those sources are current".
- Reproduction: the script `close/r2_manifest.py` re-hashes every manifest entry. For `evidence/TS4/recording/manifest.json`, `tools/record_judge_sessions.py` is a MISMATCH; every other entry is OK. The recorder changed after the run (b7dfc9b1, R1). `tests/test_model_multivalued_skill.py:184-186` explicitly skips that source. TS3 `recording-2` does bind the current bytes: all OK.
- Also unbound in both manifests: `tools/record_skill_sessions.py`, which supplies `TOOLS`, `redact`, `kept_stream` and `leaks`; the plugin's other skills; and the CLI sources. I checked that the CLI and `record_skill_sessions.py` are unchanged since the recordings. `gnd-model-evolve/SKILL.md` changed in TS5 and is not bound, which does not matter.
- Fix: correct the sentence, for example: "TS4's recorder digest is stale by design (R1) and exempted in T14". Optionally add `record_skill_sessions.py` to `sources` on the next recording.

**F4 (minor): `no_population_access` and `outside_calls` are lexical checks, weaker than "read nothing outside its workspace".**
- File: `tools/record_judge_sessions.py:107-152, 265-267`.
- Reproduction: a small script calls the real functions with workspace and plugin roots. None of these is flagged:
  - `Glob {path:"../.."}`
  - `Grep {path:"../../"}`
  - `Bash "find / -name 'items.*.json'"`
  - `Bash "cat ../judge-evidence-*/*.json"`
  - a `python3 -c` glob that spells out no repository or home path.
- Why it matters: the `--allowedTools` `Bash(shasum *)` limit is not what contains Bash. The recorded run executed `ls`, `cat` and `grep | head`, which Claude Code allows as read-only. So relative or wildcard escapes were possible, and only lexical matching guards them.
- Re-checking the kept streams offline is also partial. Redaction turns every path needle into `<repo>`, `<tmp>` or `<workspace>`. T15 re-runs only `["evolve apply","population"]`, and `outside_calls` is trivially empty over redacted streams. The real basis for the claim is the transcript itself. I read it: TS3 made one `ls && shasum && cat evidence.json` call and one Write; TS4 made that call, one `grep` of `model.orm.yaml`, and one Write. That basis holds.
- Fix: flag any path argument containing `..` and any Bash command containing `..`, `/` at a word start, or a glob outside the workspace. Have the records cite the transcript, not the check.

**F5 (nit): no fixture tests the 90% line in R2/S2.**
- Both fixtures' overlaps are 100% or 50% (round-two g1 24/24 and g3 12/24; multi-valued g1 48/48 and g4 24/48). An agent using any threshold between 51% and 100% records the same run. TS4's boundary names the S3 one-in-ten line but not the 90% line, and TS3's boundary names neither.
- Fix: add one sentence to each boundary, or add a 90-95% overlap group.

**F6 (nit): `asked_before_writing` only shows that no file existed after turn 1, not that the agent asked.**
- File: `record_judge_sessions.py:249-250`.
- The kept `assistant_last` text does show the questions in both runs.

## What I checked and found sound

- **Skill vs contract.**
  - Eligible statuses match the `ELIGIBLE` sets.
  - R1/S1 match D4 for listed candidates.
  - `of` is used only on a duplicate and names a candidate.
  - Shapes files carry no `of` and no `functional`.
  - `truncated_groups > 0` is refused before judging.
  - R3/S3 do not apply when `truncated > 0`.
  - Under `show_values=false`, no stand-alone number may appear, which matches the free-text scan.
  - Hashing raw bytes matches `check_binding`.
  - The handoff commands parse.
  - Nothing in either skill names a verdict the CLI refuses, except F2.
- **Answer keys.** I rebuilt both evidence files with the recorder's settings (unset disclosure). The SHA-256 values equal the recorded `evidence_sha256`: `75c734f8…` for TS3 and `24c9df25…` for TS4. Applying the rules by hand gives exactly the keys:
  - round-two: R1, R2 (24/24), R3 (all 0), R4 (12/24);
  - multi-valued: S1, S2 (48/48), S3 (multi.entities 12, 12×10 ≥ 24, no overlap), S4 (one entity), S4 (24/48 partial).
- **Recordings.**
  - Every `files` digest matches in both manifests.
  - The kept judgements equal the keys.
  - `workspace.json` shows the inputs unchanged and only the judgements file added.
  - discover and preview exit 0; TS4 makes one many-to-many proposal with `judged_skip` 4.
  - No absolute path, `/var/folders`, home or user name, git identity, `sk-` key, tempdir name, canary or session id appears in any kept file.
  - Tool outputs are dropped from the streams.
  - Rationales carry no counts: they say "every distinct pair", "well over one entity in ten", "one item".
  - The TS4 `no_population_access:false` is the R1 false positive, as recorded: the word "population" sits in the written S4 rationale.
- **Tests.** `pytest tests/test_judge_fact_types_skill.py tests/test_model_multivalued_skill.py` passes (124 tests). Both skills pin their clauses, including R3 truncation, 90%, other generic, `judge.skill` and stand-alone numbers.
- **Routing.** The gnd-orm-core rows and the schema-direction note match where the schemas live.
- **Plan rules.** TS-R6 holds in both skills, with no fenced `apply`. TS-R5 holds in the prose and the recordings. Predicates 3 and 4 hold for the recorded branches, with F1 and F2 outside them.
