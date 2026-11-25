# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this diff meet the criteria of the RW1 spec as ruled in its section 7 and section 13, and is each statement in the 0.5.0 section of docs/release-notes.md true of the code at this commit?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. The version is 0.5.0 in pyproject.toml, the uv.lock entry for get-nick-done and the three plugin manifests, and nowhere else is the version typed as the current version; the install pins stay at 0.4.0.
- C2. Each of the 26 bullets that origin/main held under its five Unreleased headings is in the 0.5.0 section exactly once with its wording and links unchanged, and no Unreleased section remains.
- C3. Every new bullet in the 0.5.0 section (the PyRel block, the two new Ossie bullets, the COUNT block, the four new bullets under Other changes) states only what the code, the reference pages or the retained probes at this commit show.
- C4. Every user-visible change in git diff v0.4.0 HEAD over src, docs, README.md and the manifests is either noted in the 0.5.0 section or given a reason in notes-reconciliation.md.
- C5. Nothing in the notes, compatibility, support or plugin pages reads as if 0.5.0 were published, or as if a RelationalAI engine had run or enforced the exported rules programs.
- C6. A behaviour that differs from 0.4.0 in a way a script could notice is stated as a difference in its block.

## The change under review

The work from `3219c082` to the working tree at `cc8cdb6594cc`. Its diff is `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW1-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW1-r1/diff.patch` | `4f92142f2b6c3ab9650d88194dde857ba991f08541cee5220606832d7aa4aab5` |
| `.claude-plugin/marketplace.json` | `f0724655e0e373311f65c5ef102a11f41ad493c1d3c8f5156aad752f9d9b2c1e` |
| `.claude-plugin/plugin.json` | `2b021b3206ceca1778fd8011e9997f9ae7d7b2fc6437e669082309301ce3a85d` |
| `.codex-plugin/plugin.json` | `21c44d7a1e8cd88cf5b8f3259574a7709cd325925f9df171e0b2cea2f115df48` |
| `docs/compatibility.md` | `ee61db381c81252795befebc1abc04033dd16b65a195a654f82a3b991e82c66b` |
| `docs/marketplace-plugins.md` | `a760dac10f89ccd4ce93c99f771cca57f90e92e9ac039cf81995b2f79336c8f7` |
| `docs/release-notes.md` | `5b28ba132d6acbf96b3b873a7a4987d38b0343a4b1684bb464c15099c5e4786b` |
| `docs/support.md` | `af5e248dee386a23418111f7717115b7a735dbb3da704b2e625ab19d41824c3d` |
| `pyproject.toml` | `031acf62df8f7a8aa074eeca4976fa56396e61aa53c4f30a71dbdd61e4c7a4a2` |
| `tests/test_release_version.py` | `a09670902e2756ba37ae2a074fc776d30915f54b22fb2efa29dc42ec8c6ad00c` |
| `uv.lock` | `e96d80125673b6b3dbd6203caedcda1e5871ed47da45bd4b2ab3c35804f9496f` |
| `.gnd-planning/milestones/release-0.5.0/notes/phase-RW1-spec.md` | `aac415c539b5c79a567ae5775c2d92863be621933cc923b3a82d2fc4429458ce` |
| `.gnd-planning/milestones/release-0.5.0/evidence/RW1/notes-reconciliation.md` | `f62b442652622d3234f29a5f6c45a5dc905c96f27879aac5902a9ccfb5c9696a` |
| `.gnd-planning/milestones/release-0.5.0/evidence/RW1/old-version-probes.md` | `698de3702de336f61d198bca8b029029329a42a6390ebb095bc26cba90079599` |
| `.gnd-planning/milestones/release-0.5.0/evidence/RW1/e1-summary.md` | `8b2bef0619c07767a5f5bd6c475d4e4c98c3a8e052116ec4a694b74c16139d09` |

You may read anything else in the repository that helps you answer.

## A standing check: code fitted to its examples

Whatever the question above, also look in the code this change adds or changes for a
solution that handles the examples in its tests and fixtures, and not the whole class of
input it is given:

- a regular expression, string split, slice or index over structured text (JSON, YAML,
  TOML, source code, paths, command lines) that a parser or an existing reader in this
  repository already reads;
- a pattern over output this project renders itself (a report, a table, a log line), where
  the code could have been handed the data instead;
- a pattern fitted to the fixtures: it matches every committed example and fails on a
  legal input with other whitespace, quoting, casing, nesting, Unicode or a line break;
- a branch on one literal name, file or message, added to make one case pass;
- a second matcher for something an existing helper already does.

A regular expression is not a finding in itself: one that states the whole grammar of a
flat token (an identifier, a version number, a hex digest) is the right tool. For each
suspect, build a legal input that the tests and fixtures lack and run the code on it.
Report a finding only with that input: what the code returned and what it should have
returned. A suspicion with no breaking input is style: label it so. In your list of what
you checked, name each matcher you tried and the input you tried it with.

## Rules

- Read only. Do not edit, create, stage, commit, push or post anything.
- Do not open `.env` files, keys, tokens, `auth.json` or any other credential file, and do
  not print environment variables. If you need one, name it and go on without it.
- A finding names its file and line and the consequence someone would observe. Run what
  you can to show it; where you only read, say so.

## What to return

1. Findings, each with an id (F1, F2, ...), file and line, what is wrong, the observable
   consequence, and how to reproduce it. A finding with no observable consequence is
   style: label it so.
2. What you checked and found true.
3. What you could not check, and why.
4. A last line: `VERDICT: APPROVE` or `VERDICT: CHANGES_REQUESTED`.
