# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this change re-derive a caller's reading run from its folder and root as the LH2 spec writes it, while packaged replay is unchanged, and what folder or root does it get wrong?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. replay() of a literature-reading-run/2 folder makes no producer or reviewer call and returns the run's report, or refuses with ExampleError or ArtifactError.
- C2. Any changed byte in a caller run's files, any changed input, or any manifest setting above its ceiling refuses; only a consistently rewritten folder replays, and not when expected_evidence_sha256 names another run.
- C3. Every file of a caller run is read under the retained-file cap the run recorded, and every file a completed run writes can be read back under it.
- C4. A malformed manifest refuses before any run file other than run.json is read.
- C5. Replay of a packaged run, test_ld3, test_ld4 and test_ld5 are unchanged.
- C6. Every regular expression, string split, slice and special-case branch this change adds handles the whole class of input it is given, not only the examples in the tests and fixtures, and none reads structured text that a parser or an existing reader in this repository already reads.

## The change under review

The work from `33fe059b` to the working tree at `0b330eb5b34f`. Its diff is `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH2-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH2-r1/diff.patch` | `2967cb8b614dca1998c395c073f274dbf5e90da9d6175e2775423c2b788a98d6` |
| `.gnd-planning/milestones/literature-host-interfaces/notes/phase-LH2-spec.md` | `ec41cccdf7bb099e1129e11fb141126b35b4b2e60887ac8996e3abfadbaed647` |
| `dev/components/COMPONENTS.md` | `dc5af1363756da073730e2969e5f55eed3d3e99e0ed2e5fe362c3ab3df4ec725` |
| `dev/components/graph.md` | `1446be7aa1dd36f99662086212d1dc549f89d3933f342d6c10b792408ebfc888` |
| `dev/components/modules/examples.md` | `f3748467305400e85237d4ca07c99c0fe4c284b0a8501a6ebbc687b022f650cc` |
| `docs/literature/commands.md` | `9d7f3d092c276124d8df27689abbad397d912922f7d34ee8f7b3c72a60470181` |
| `docs/release-notes.md` | `3fde981b1b7c920b17cae776352b7bdda18a358df90b40b37e601e4270a3f62e` |
| `src/gnd/examples/literature/assurance_report.py` | `eb5bf73f97b9a7f400ae4c68348334fd8dfba932ceea5b585341f74da3d56078` |
| `src/gnd/examples/literature/reading.py` | `317f1a115751f72df878a0172b3f1d7e2b371c4b91e5a2938cc91c57b1a12b7a` |
| `src/gnd/examples/literature/reading_fixture/README.md` | `797c060777fd392dee286322c38b45ac4faf79df08847f50dbe46acf449c57c7` |
| `tests/test_lh1_reading_host.py` | `c0db56071a7f2f5c17ff521949c748b3aaf7f5b2656950b698741ff1b19cc5fe` |
| `tests/test_lh2_reading_replay.py` | `dbc533cb82f315d6f377d6b02c0461a494f6ed97dc9180ab1e4e94d7f8ac240a` |

You may read anything else in the repository that helps you answer.

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
