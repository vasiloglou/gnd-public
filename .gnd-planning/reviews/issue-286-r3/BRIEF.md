# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Is the final temporal walk in src/gnd/terms.py right: does it read every piece of authored syntax in a model document and nothing else, with bind and head read as role-keyed containers only where the schema puts them; and do the notes and the 0.5.1 tag-only bump state and do exactly that?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. After skipping provenance, source, rejected_proposals, description and sample_population, every remaining map under a key named bind or head in a schema-valid model document is an atom binding or a derivation head.
- C2. Compared with the walk on main, the final walk yields fewer nodes only inside descriptions, sample rows and role-keyed maps, and more nodes only for terms under a head or bind role named like a skipped key.
- C3. The release notes' three 0.5.1 bullets describe every behaviour change the comparison above finds, and nothing more.

## The change under review

The work from `102110b2` to the working tree at `60e42d7e2310`. Its diff is `.gnd-planning/reviews/issue-286-r3/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/reviews/issue-286-r3/diff.patch` | `d6988b7224cf687b3ecd5db6a530027ea5594903bb191e2eb1ab28e6da1a1c10` |
| `.claude-plugin/marketplace.json` | `585c84e020e683462b827668de77e97c7401b091364ba2c47896eb7fda29861e` |
| `.claude-plugin/plugin.json` | `bfcfc5dddfe807e1562e9bc77fadd25e9a4f7a6db0e57f9d01a5a8364ec9b1e5` |
| `.codex-plugin/plugin.json` | `4db81f701fcf043f837f9ce8653c2130983aa2c0e91c113e893b1449a9ab3c83` |
| `.gnd-planning/reviews/issue-286-r1/BRIEF.md` | `3ea6accf1d0206dc9a87c382c395149080392856c597ff9312d834ab4b404609` |
| `.gnd-planning/reviews/issue-286-r1/FINDINGS.md` | `7ca0f3acffb69e09d5af5ffdb81ac9a0b6ad2848eb393453af2c80b3ce2339b2` |
| `.gnd-planning/reviews/issue-286-r1/brief.json` | `bd83d1087cd051c67a19fc007826690902d8a5dcf6acb1783ed191ef174f847a` |
| `.gnd-planning/reviews/issue-286-r1/diff.patch` | `68b9342072c0413f08875da521651414f7af7b2dc9539f3a75567e03e3d9ac0a` |
| `.gnd-planning/reviews/issue-286-r1/review.md` | `823559ede4d1127e29308d2facb5a110b65960eee1fb99bc7d2fcf7023f5de61` |
| `.gnd-planning/reviews/issue-286-r1/run.json` | `e225334b0ed3085ffbb260687266a941b88f06e72b7c956d174cc42cc2f3d958` |
| `.gnd-planning/reviews/issue-286-r2/BRIEF.md` | `1f63244110c65d97a3c8fa2b46f44963840f6b6e6cd626e08de6136e54bd7d63` |
| `.gnd-planning/reviews/issue-286-r2/FINDINGS.md` | `de32a295387d70df5f59f3893b51b4945dc65d65f870cd45744230d41ec71946` |
| `.gnd-planning/reviews/issue-286-r2/brief.json` | `1cabcb5317e03ad65ab9fb3799d0733229a19c28d6ac0eb58f3012682dd51415` |
| `.gnd-planning/reviews/issue-286-r2/diff.patch` | `005f1c0c56e949af511a19e0bfdbed4ded31c9b1e74e232b9d0ea0dc379216a1` |
| `.gnd-planning/reviews/issue-286-r2/review.md` | `fd311c3e27922d2026415c9b0742e42a560c79cc9c02676abf46981b73eab1ad` |
| `.gnd-planning/reviews/issue-286-r2/run.json` | `e4bee773dc5506116ccee740326ff9aec7870501b8b2eb596e9de3ce9a462ae0` |
| `dev/components/COMPONENTS.md` | `7110bf5d091c2345bc5d718c800cd9782a600dd946258d956943a8cae89a1097` |
| `dev/components/modules/_root.md` | `7e6451dfa84e162549f6e098e1032115c1d39842ff0b535d182f64a42ec3764c` |
| `docs/compatibility.md` | `f1997225a730e83bbb52ffe98f6cdc7e3084b9f2c6c481b0c26d861b532b5915` |
| `docs/release-notes.md` | `742fa90292e233fc8ad5f21090fa74b1f8412200629328771a0e902e761af449` |
| `pyproject.toml` | `ad19198871890329fd5eaf64f08fd256dabecca0bbd1ee5e1cb01dd7d2273ab5` |
| `src/gnd/terms.py` | `0df1756a70dc47250656cd919e991ab1bacd658630ea8dce70abbcb108781100` |
| `tests/test_issue_286_role_keyed_maps.py` | `5d6198cb2a35ed73897fbcaa298e868ae4310ebb4aa4065a0ba3f78e837c7f8d` |
| `tests/test_release_version.py` | `2c69d01015a3557f7db5dbbf742b6b3773014fbfbe35018dd58aac6554ddc151` |
| `uv.lock` | `93d1735c2dbd70f0625072b77ca1068545f4043688730b9b672feec59888b4ab` |
| `src/gnd/schema/orm-meta.schema.json` | `0cab9e99afbc048afe328d57009062bb46932d8790688f3e4a8f27e75ef0cc62` |
| `src/gnd/skills/gnd-orm-core/references/representation-format.md` | `594ec58970647df4abeca920579f2088b671fdd65f0ee473354c1ebd204ca92a` |

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
