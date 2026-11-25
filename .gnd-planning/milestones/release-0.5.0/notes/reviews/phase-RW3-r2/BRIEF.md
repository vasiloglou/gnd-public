# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Round 1 returned five findings. Do the repairs in tools/release_text.py and evidence/RW3/dossier.md fix each of them without a new defect, and does stale_lines now judge wrapped and oddly spaced prose the way Markdown reads it?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. stale_lines reports each stale statement of a paragraph exactly once, however its lines wrap and whatever spaces or tabs separate its words, and reports nothing a standing entry covers on the line as written or on the joined lines a phrase spans.
- C2. The lines a spanned phrase is judged on are the lines the match actually covers, for a phrase split over two lines, over three lines, and at the first or last line of a paragraph.
- C3. Every command block of the dossier stops at its first failing command and exits non-zero, and each runs from a directory in which its commands work.

## The change under review

The work from `dcb3aa0f` to the working tree at `f7181173f5cb`. Its diff is `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW3-r2/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW3-r2/diff.patch` | `edee8ce7eeb6221011658f0967ab6de30a92bd7f5543ee71a3a92f9e3823a0a6` |
| `.gnd-planning/milestones/release-0.5.0/evidence/RW3/dossier.md` | `64bacd030f85dbe62d1c37c11d4156e198b1e405939a5fb2941636256655b36e` |
| `.gnd-planning/milestones/release-0.5.0/evidence/RW3/scratch-verification.txt` | `a7a76dc3db3d3f3a80c09387946987cb3833854db731a14ef6c912d7f5db4a3d` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW3-r1/BRIEF.md` | `811454f3ff690dac444e222cef7ecafb7381b8b40de53c8c2d026317e125ceb0` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW3-r1/FINDINGS.md` | `84780394706db284184687780b913334543026ff82d52d94759386b96e3ea4b2` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW3-r1/brief.json` | `58bad275a5db3cd07296e1291e5956347148537e3f5b37470dd29881fa7a09aa` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW3-r1/diff.patch` | `246ddebc1f101bd0019a66f21aaf45bd85446252aabf7b49522615ffa453f5df` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW3-r1/review.md` | `afe0387e1cae3c2a30e4203feee68a5e4139bc36d07d112654c6a03ec1b273f6` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW3-r1/run.json` | `fa47b3589801df57eb717dc8f23cf0bdc53123b4b1f66d1a7bd9c3afed0efeb9` |
| `dev/components/modules/tools.md` | `1119822bb3b9d91bbc92f3326d3ef37db57687cfe77281d205cc1af5db75a914` |
| `tests/test_release_text.py` | `4572add30a3cb8abe5b1033f180ba3502a3bad1e298cf1403cedb5bcb042ded1` |
| `tools/release_text.py` | `c8611c4207293f6af11a722c5ac168892c615d40ab82035937c111356e428b47` |
| `.gnd-planning/milestones/release-0.5.0/notes/phase-RW3-spec.md` | `e8067584aa901fd5e0c1a0340bad8acaff23f4e9b4805748cdbc5d6bbdeca031` |

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
