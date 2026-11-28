# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Check shared setup and per-target accounting and the soundness of finite negative evidence and independent replay, including coverage, correlated multi-role bindings, reference inputs and disclosure. Exercise original single-target compatibility.

## The change under review

The work from `11c75ea9` to the working tree at `7c118a72c787`. Its diff is `.gnd-planning/milestones/python-snapshot-evaluation/notes/reviews/PS3-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/python-snapshot-evaluation/notes/reviews/PS3-r1/diff.patch` | `3e7c69ba66065b0b40642a46d7da674f3ea3ae54e840e2cce566d25ba50569f9` |
| `.gnd-planning/milestones/python-snapshot-evaluation/evidence/PS3/dynamic-query-successor.json` | `26bfdd84c42dcbde69ebbb3df2076fcdd23c50c94cf97096124acbe917507940` |
| `dev/components/COMPONENTS.md` | `d66995f08b9e48d1121e4105be234584b59fe8af1ae03468fa4bd5ef4087a129` |
| `dev/components/graph.md` | `37cf8bd8d6f5e9bed66c3256c53f044ccc28f707961ff3d701fe1593ead9e20f` |
| `dev/components/modules/witness.md` | `dec31cd8429d1f4b6fcf117310ec4d38f37dda57dc023ee9c415a9512768427e` |
| `docs/reference/python-api.md` | `8ea954b15b9d27178251d54fa45f442a375635c5073bfd0534e9c2e040e26789` |
| `docs/reference/why-not.md` | `646809bdac04c52e3ff97b5c7ae74fefc85147134c0d22b611fe3eded1befbd5` |
| `src/gnd/why-not.schema.json` | `33361ab9559517709fd8d4d1433ff87db5d7f325fd10358de2fe7e261fffebc3` |
| `src/gnd/witness/cli.py` | `b02f2ef1996189bc0474682dbb7d6919648f949d4218f9fb1017a3c8482d4f97` |
| `src/gnd/witness/io.py` | `74f1483abf766874a2bf6f0339c269d5c8b4fb457ca05f701708851896b39960` |
| `src/gnd/witness/kernel.py` | `af12fc3d0c58f44e57e22f1ee5aa791bd0b636bdbee41aed527de47dd98404db` |
| `src/gnd/witness/producer.py` | `1227fa90264dc7e3d43e15b4e3962a28826196d60c38d38087abf48162e33065` |
| `src/gnd/witness/service.py` | `746fc199ec7a5df11a4801e7fed1bfffaced75068faa626b30dce44ac51212b8` |
| `src/gnd/witness/types.py` | `91a6a1a1000c85faf582d60b3ebaf228a75f4f6bc7cc8fac8d410fc6784458fc` |
| `src/gnd/witness/view.py` | `83419dcc68f303e9d9c63feed1df4a01b03b9a80581344bdbf1163690ce2c6d3` |
| `src/gnd/witness/why_not.py` | `8757089b099cc17eff6015c16a192d175a4ad66275a048ea96942c2ce628ea46` |
| `tests/fixtures/why_not/cases.json` | `deb5f3990fd4e1d4826828587871f27fd9dd6b5d61ecc00bc41cdf4569fd04f1` |
| `tests/fixtures/why_not/goldens/g11-two-targets.json` | `10bd95f7b879177e3942dd05a4474b5bc8f8adee3fcf4389a06443da8fabad53` |
| `tests/fixtures/why_not/goldens/g11-two-targets.raw.json` | `dc36501c63e5088879f1cb379bdb7207be903653fb78e976e472ef32e79ebe36` |
| `tests/support/pyrel_application_successors.py` | `2a0424f9e80e89e0a4a8e8a5034ed25e816eddc8094ce9709bfca4e794c6d40d` |
| `tests/test_public_api.py` | `9d40cd03d6ad60489cb12f9a7e59b193f8dbbb224e5e930e565a4a8c0c913275` |
| `tests/test_public_reference_signatures.py` | `5e862c23455f04d98843b146de8274f0dcaba585a8243daa34c8fc0331e2958f` |
| `tests/test_public_why_not.py` | `745200e1ab65675e8707bcd1f3b414578222fdee529dac639722781e26cab333` |
| `tests/test_snapshot_explanations.py` | `bcec9e739725493069b5ab87564f21aa77426841c0bd90cd3c06db2804161489` |
| `.gnd-planning/milestones/python-snapshot-evaluation/notes/phase-PS3-spec.md` | `2cc347de6b017eb04931d178f9abf8e90259b5be28629107da14ebbc63f16ed5` |

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
