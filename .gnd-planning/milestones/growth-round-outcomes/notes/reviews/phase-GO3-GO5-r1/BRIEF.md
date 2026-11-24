# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

This diff adds GO3 (narrow_proposal) and GO5 (gnd evolve summary and its round file), and repairs GO2 review r2 and GO4 review r1. Find the proposal, outcome list, round file, artifact set or page edit where narrowing keeps a refused operation or drops an admitted one, the narrowed proposal fails to preview for a reason the first pass did not mask, a summary miscounts or binds the wrong artifacts, a hostile input crashes or is not refused by name, a proposal without narrowed_from changes bytes, or a repaired finding still reproduces.

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. GO3-C1/C2: narrow_proposal keeps exactly the admitted and unassessed operations, drops refused-* and dropped-with ones and re-runs GO2's closure over any outcome list; the narrowed proposal previews and applies like any other.
- C2. GO3-C3/R0.3: the narrowed proposal has its own proposal_id and narrowed_from; a proposal without narrowed_from keeps its bytes and proposal_sha256 under every schema version; narrowing writes nothing.
- C3. GO3 refusals: anything but a proposal and a preview/outcome report, another proposal's outcomes, a preview with no outcomes, a before model that is not expected_model_sha256, or rows that do not cover the operations, each by name in that order.
- C4. GO5-C1..C3: the summary's proposed total equals the sum of outcomes when present; added comes from the evolution record only; reused and host drops are the round file's, reported verbatim; every artifact is bound to the one before it.
- C5. GO5 round file: the reader refuses an oversize file, NaN, deep nesting, a huge integer, an extra or duplicate key and a duplicate reused row, each as RoundFileError; gnd evolve summary exits 3 on a refusal with nothing on stdout, and 64 on a usage error.
- C6. GO2 r2 repairs: _needs reads a reference key only where the ORM meta-schema declares that property (never in a sample row or provenance), depends_on included; a role step by position or name is located; a constraint issue is never pinned on a host-only change; the constraint index is linear.
- C7. GO4 r1 repairs: the guard fails when any rule sentence is reversed, deleted or narrowed, or hidden in an HTML comment, and passes on equivalent Markdown (unpadded tables, closed headings, tilde fences, reflowed lines); the page no longer tells a host to write facts against an existing fact type.
- C8. Every regular expression, string split, slice and special-case branch this change adds handles the whole class of input it is given, not only the examples in the tests and fixtures, and none reads structured text that a parser or an existing reader in this repository already reads.

## The change under review

The work from `9bf8bf3e` to the working tree at `b2d67b8e8a95`. Its diff is `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO3-GO5-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO3-GO5-r1/diff.patch` | `b81871aad0eead5a5f65a030a2f9d1b89befc066006a06b5dea489ab2d30eb07` |
| `.gnd-planning/milestones/growth-round-outcomes/evidence/GO3-GO5/dynamic-query-successor.json` | `ec4150966c353e865606471d9db1e28c9922b90a4334346c6b67228e92608142` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/issue-replies.md` | `67f110fd470d4626ba884062edfb0819822272c2feace217149631de66de11d1` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/phase-GO2-spec.md` | `a5e4b6e3c79c311817d0cb9a4a297207ee4443f51e961f683c3ccb425d220f85` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/phase-GO3-spec.md` | `dace370951dde109693d10bef4eca57d2696632b5b6c8ab20d9f1c5aea1b6f4a` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/phase-GO5-spec.md` | `c351b1eaf4ba6cf0f091f0fece582447fee2d3e09e2dcedec19f83f05e3b0431` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO2-r2/BRIEF.md` | `0fdb30d46ab733feab4b818a44c85aef0a90a0984403ea1caccf7e735cffa473` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO2-r2/FINDINGS.md` | `17b788fa840e386f9a75876012a7ceabfeb55fe72db557b7efe287c7e2fee45f` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO2-r2/brief.json` | `5ca759eee44bb1830b8060485a9be0fc8e63ade0a1b90fbe1378d2e5ac04d5ea` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO2-r2/diff.patch` | `1b59ab939b9e697b6adf346dd3d6290af33119d5fea4fd7a8b4ed04003f56eb9` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO2-r2/review.log` | `cf4c53a8b34fed44b2f70378f4d058d5669ea5948a55666b2bea5a785642dd4a` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO2-r2/review.md` | `f8860ee1136a0a3aaed11b6c6b4df7a0ed09adf12d58ca81e4f66d22e99b990a` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO2-r2/run.json` | `c563c999d3f8ac4cb45d436dd559f50098951cd47764f41475e5433e65b46bf5` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO4-r1/BRIEF.md` | `9adfcf8058dfb7c18f279a15159e84e754904275dcee80c159138dfcb578593d` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO4-r1/FINDINGS.md` | `78da75496e2452928f01413503e80270aae667d4c23a1c7c37b99f4c138b8814` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO4-r1/brief.json` | `0caaa150264537c45e85181102165b786ad23792e061585339c33f49cc5cdfd8` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO4-r1/diff.patch` | `e5bba9bdf67db0e5ae398256b46e19d595012e355c753447abca1c8d25e1d287` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO4-r1/review.log` | `abb497d25f19ee0fc48ccdad1c87d0ad11efae468c50415b9aafd4e172772136` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO4-r1/review.md` | `69f5848fa92183fb80d2f6bec971288d4e667d57eb9c0272dc17afa8c1b56751` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO4-r1/run.json` | `2806e8311c45bb804886813775fcdb5469c27432fa4a56405082bfb6e96e2ae0` |
| `dev/components/COMPONENTS.md` | `cb1e92054000adb845ddccd15af50dc3d5942eb34b190676a5241d596dcfd2d9` |
| `dev/components/graph.md` | `edb6fb647175a90c03862c5bc7298ba4aceccbdfc989c84d2112fe6aa57bb17a` |
| `dev/components/modules/discover.md` | `910529879983dfed42aaad574061e5e617406a6760e2bff8966a915b793d1308` |
| `dev/components/modules/evolve.md` | `c0801e1ed1cf716b9b09da2a0f3e3dfab7acecf4ce7d3ec38e8d6107605f7601` |
| `docs/reference/disclosure.md` | `0353f6dfaacf45f471f5e79eb8a0d607771390cd84032ffd3381dc533e7799e1` |
| `docs/release-notes.md` | `5be7a896c5184589224cb970373fdd07a4e5d555df10a315831de329eaa094e1` |
| `src/gnd/commands/evolve.py` | `9882d818a31363a0993f0470f010607d985542d9f5cf8d413012431ccfacc69b` |
| `src/gnd/disclosure.py` | `2068729ead18c619e45d25ef404be0ea5701263b93bbaf9df2502459fe77e331` |
| `src/gnd/discover/narrow.py` | `79faed0eba38e2ecaac1078bb4044e97216df57fed2b92bfa3a2261f413e3c6c` |
| `src/gnd/evolve/__init__.py` | `a4714d3a3e6851b7231970e3c0bf74be5c6f6978c51d416aa390b885aafb4a0a` |
| `src/gnd/evolve/cli_service.py` | `78be1663446c8df4331179f4306d249a7b53ad34303e7563fa32aa1e58de237f` |
| `src/gnd/evolve/models.py` | `e3cad91c0b36787e266a93fa1a36c78223e5935ad67108fd6b488416f28802be` |
| `src/gnd/evolve/outcomes.py` | `b41fb7a01f53d9039428fc5fee074dd2e839150dfe38c268755e37bebe400bd8` |
| `src/gnd/evolve/summary.py` | `d902511e5a35d5b5478f6b8584071cabafb97dfeefd6a9cd9c0384ce076174bc` |
| `src/gnd/skills/gnd-model-evolve/references/evolution-contract.md` | `cf6442fd60e9b92d609cf5ef87c8fdddf86d75c880d560417ae6b02069c1a7c1` |
| `src/gnd/skills/gnd-model-from-text/references/unattended-growth.md` | `396bf5ef138218ea41ffc1ce768759a441943a45ad575a7160e88616a9eea630` |
| `tests/fixtures/round-summary/README.md` | `a458083a1c7aceabf3a045e27b4d11ac9c1899ef8e815c353fb2f016c8843b26` |
| `tests/fixtures/round-summary/known-mix.expected.json` | `cf36bc939a39d49369074ac3f5b1e7c3c38a1265ed3ffc60feb3d766d3f765c5` |
| `tests/fixtures/round-summary/known-mix.round.json` | `ff7b4c2b4c5c59c7343a4e0e24f9b0351b4a235f459d9692d5a0b552c10c1605` |
| `tests/support/markdown_sections.py` | `6b87d38ecc7b96fdd0743ac6afcb3a93aff2b7ead93fbd6c8e2a03523dee2a25` |
| `tests/support/pyrel_application_successors.py` | `25178b93d459ceabda3ef362c197c0b3f6b1f45471f35e518a35f22b16ba2a9d` |
| `tests/test_disclosure_mode.py` | `d4719804f7de54cb08027f692636d57068895e59929ea0ec2fe4975f6828a993` |
| `tests/test_go2_operation_outcomes.py` | `077cce68655468a9431563bb0afac7d163f0a143848ee0568d00143d81e629ae` |
| `tests/test_go3_narrowed_proposal.py` | `d897afabc1e85d48df4bdc5b29647550c7e947261400e45ec16f7a45af9273bf` |
| `tests/test_go5_round_summary.py` | `bb8b95ba5c45083cde4f69ce4976ddee8fa34d37bbc7de480a461e7d029e4e0f` |
| `tests/test_rf1_cli_pins.py` | `f59d3ec3f91dae6661bc06f2b78e795c89310cb64bb341c93e60893cc7654f8b` |
| `tests/test_rf5_commands.py` | `7a10dbac1b4f9d5dbc43e9f052076511a7fec29ed2bb34a93b60e0ef3a484536` |
| `tests/test_unattended_growth_guidance.py` | `15fe5071ac3eb2ee798615d8dfb4e178655bfdef46339fd0fb909ab194d85f93` |
| `tools/gnd_layers.json` | `30bc9af043366eaa80ce5aea73fe2bb1233eb226f8df6405c09e92e2edc1aaeb` |

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
