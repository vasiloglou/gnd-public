# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does the public Python snapshot verdict accessor preserve run status, disclosure and refusal semantics across its declared envelopes, and does the opt-in vacuity policy match the CLI? Reproduce specific failures using legal inputs.

## The change under review

The work from `4962a4e1` to the working tree at `974cd754f852`. Its diff is `.gnd-planning/milestones/python-snapshot-evaluation/notes/reviews/PS1-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/python-snapshot-evaluation/notes/reviews/PS1-r1/diff.patch` | `a92c13c886a49664c071f656539f61be7a1af30f5b932c4e07b1fdf85885707a` |
| `.gnd-planning/milestones/python-snapshot-evaluation/evidence/PS1/dynamic-query-successor.json` | `536357630bf7adac6f809815a8799832444f9f211ae5150ba8466a383474e988` |
| `dev/components/COMPONENTS.md` | `ce5535b3a857d33a9efeab5a3678deb251c237501f172a2e101025c3bb0c7cdb` |
| `dev/components/graph.md` | `a534e61d42fca0826fc127e258dc0a2fa1a9573c6739413d21d775288b538b0d` |
| `dev/components/modules/_root.md` | `8619dd4c0441df1fd0d0212da23b311569c6963aca2f02451588a37cecf2c66c` |
| `docs/reference/disclosure.md` | `16c51e1151e34be69751168881f5bd9f6d96452181d274c54b7c93e622e9278b` |
| `docs/reference/python-api.md` | `5e3677bb75ce0970e2310fadc460f03637a0c51c0307536dea75c459a368c5c3` |
| `src/gnd/api.py` | `1d4f4832c61ff271935dd0ea36929392a57eedac31fde3b2d2b505c7d623cfe4` |
| `src/gnd/disclosure.py` | `ddc7ce17e9e87d24b3f31fd8168bba6cc77a0f42f9bbd3dafe50fc9d5ace0a24` |
| `tests/support/pyrel_application_successors.py` | `10df189e22ca8545a8ea55550fc77293acd38e426192adfc8e889fd4f5700b22` |
| `tests/test_public_api.py` | `1c993d41efc81738df271c5fc952352f11c02d9bf7704234b6ac3b4b5d6c6d3e` |
| `tests/test_python_snapshot_evaluation_phase1.py` | `9d07fe9001d441d831c7bbcf207f589242c09dc51d78f9f8763902053935a951` |
| `tests/test_v61_phase2_api.py` | `e483a7b50479d08be6d268fb41bc6676467f4bb6132f30e09049bb969d8b2861` |
| `.gnd-planning/milestones/python-snapshot-evaluation/notes/phase-PS1-spec.md` | `8b3c6531f3ae19f506ffc1ee31dd2ee73f4df3de8599b93ea0453a35689e6383` |

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
