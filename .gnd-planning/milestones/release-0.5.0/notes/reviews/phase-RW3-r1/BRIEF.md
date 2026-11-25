# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does the change to tools/release_text.py report every page line that would still describe the state before a release was published, without reporting lines that stay true, and is the hand-over dossier accurate and safe to follow as written?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. After this change, stale_lines reports a where-this-ships note however its sentences wrap across lines, and reports nothing for a paragraph whose only matches are standing lines.
- C2. The STANDING entry for the token-route sentence of docs/releasing.md accepts exactly the sentences of that form and no other line.
- C3. The two phrases added to STALE match no line of README.md or docs/ at this commit that stays true after 0.5.0 is published.
- C4. Every command in evidence/RW3/dossier.md does what the text beside it says, in the order the plan's section 11 gives (upload; served-file comparison and fresh install; tag; GitHub release; pages pull request; issue comments), and no command there would publish, tag or release if it were only read.
- C5. The dossier's figures (digests, byte sizes, test counts, profiles, the snapshot comparison) agree with evidence/RW2 and evidence/RW3/pre-publication-state.txt.
- C6. The supplemental patch changes only the seven lines the tool-only preview lists, and each replacement is true of the repository at this commit.

## The change under review

The work from `14b875c6` to the working tree at `56c173cdfe49`. Its diff is `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW3-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW3-r1/diff.patch` | `246ddebc1f101bd0019a66f21aaf45bd85446252aabf7b49522615ffa453f5df` |
| `.gnd-planning/milestones/release-0.5.0/evidence/RW3/dossier.md` | `923f2d3c84152c6a6179b8888072f3df51fad3d689e5cf0d7979e0028066ed07` |
| `.gnd-planning/milestones/release-0.5.0/evidence/RW3/github-release-notes.md` | `e75450c9e0555894c98823415a5224aaaa6f0f0c110a9599fba19dc8b63046b6` |
| `.gnd-planning/milestones/release-0.5.0/evidence/RW3/post-publication-supplement.patch` | `e9a7b4ded7207d412737d5da394053e995754687c82fd39ebe6948aceea920c2` |
| `.gnd-planning/milestones/release-0.5.0/evidence/RW3/pre-publication-state.txt` | `2b6b2a3a24df87bfd511426f36dd97bdde247128273a54a6667c90e176e6f393` |
| `.gnd-planning/milestones/release-0.5.0/evidence/RW3/rehearse-publication.sh` | `b18f0a3782caf9cc4e17743a98387fc19e2e682c9ad4a319efd202841bcd4de3` |
| `.gnd-planning/milestones/release-0.5.0/evidence/RW3/scratch-verification.txt` | `f8017ef87c8ca33b13ffbc26a3312d2c7f48cb32a447aec6528cebb3a350358d` |
| `.gnd-planning/milestones/release-0.5.0/evidence/RW3/tool-only-preview.txt` | `d9d5702a02cf6e56d9268771343473acc40779d45f63bcbab5895487d241b456` |
| `dev/components/modules/tools.md` | `4edf83b047786e6f1324cb3c509455c9d09613cbe6dfdd2d90d6db62cfcacfc1` |
| `docs/releasing.md` | `f89ce81a98c984200f2fada0aa04ab0d338915e8ec00890e7e715f25df35075c` |
| `tests/test_release_text.py` | `e147e0b986016a253a4195f6ae257294e0b45243fe8ccef3d005255f8dc64f65` |
| `tools/release_text.py` | `0909fee43c99009a17abb74d45e2db07e6256ccbd8526d8c247797ebb8703872` |
| `.gnd-planning/milestones/release-0.5.0/notes/phase-RW3-spec.md` | `e8067584aa901fd5e0c1a0340bad8acaff23f4e9b4805748cdbc5d6bbdeca031` |
| `.gnd-planning/milestones/release-0.5.0/004-phase-RW2.md` | `3b801257361ad1a537ea3003c9da7eab65cf6278e1824ed4d6dbb88cd031e7f5` |
| `docs/release-notes.md` | `7526c08e8ac8281e48d4b6cf8c138f9bb24aa6b4b833f834468c30a1254e1d25` |

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
