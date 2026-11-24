# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Refute PF2's result. (1) Does each grade in evidence/PF2/GRADING.md follow from the retained review (evidence/PF2/reviews/change-*/review.md) and from key/grade-runs.json under the spec's pre-registered rules in §6 'Grading'? (2) Was the answer key fixed before the runs: do the hashes in KEY-SHA256SUMS (committed in 36ca151e, before the reviews existed) match the files now in evidence/PF2? (3) Was the reviewer blind: could anything in the corpus diffs or briefs (evidence/PF2/corpus, evidence/PF2/briefs) tell it which version is planted? (4) Are the spec's stated limits honest, and does any claim in GRADING.md or the spec's findings overstate what eight runs show? You may run evidence/PF2/grade.py's checks yourself only in memory.

## The change under review

The work from `ec538cc7` to the working tree at `36ca151e5383` with uncommitted changes. Its diff is `.gnd-planning/milestones/pins-and-review-check/notes/reviews/phase-PF2-r1/diff.patch`.
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/GRADING.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/grade.py (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/key/ANSWER-KEY.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/key/branch-map.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/key/grade-runs.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/key/key-runs.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/make_corpus.py (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-a/FINDINGS.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-a/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-a/review.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-a/run.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-b/FINDINGS.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-b/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-b/review.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-b/run.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-c/FINDINGS.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-c/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-c/review.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-c/run.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-d/FINDINGS.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-d/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-d/review.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-d/run.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-e/FINDINGS.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-e/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-e/review.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-e/run.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-f/FINDINGS.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-f/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-f/review.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-f/run.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-g/FINDINGS.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-g/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-g/review.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-g/run.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-h/FINDINGS.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-h/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-h/review.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-h/run.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pins-and-review-check/evidence/PF2/run_key.py (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/pins-and-review-check/notes/reviews/phase-PF2-r1/diff.patch` | `52b0b3c38d31751cf097a7a46b454162e9ad988e835349fd66e707cf1cade562` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/KEY-SHA256SUMS` | `6cc1672a5d9fc523b91182c1dac99e8e02eeba7df515d241350918c87cdbdc0e` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/briefs/change-a/BRIEF.md` | `04f8b9fed5f2ca9a917d4a8fa2e275763d49d96881d03d08255145aa1da734b9` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/briefs/change-a/brief.json` | `2984e815965d5a1c93ae97fbb15e9b8b657c036e6baaa062c6bc20781b3f5ddd` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/briefs/change-b/BRIEF.md` | `75ca40fa19d110d73656d06416706a525222b9dc7009d12f457b058f01afe36f` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/briefs/change-b/brief.json` | `d3cbddbeee68f8378b2a3c14bd1e4034705d00d5a64e230664182345485bc8b8` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/briefs/change-c/BRIEF.md` | `aabc18c03346cf6381d6a39ac7f60f278606720ecc1b015555ccf194484a9c4c` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/briefs/change-c/brief.json` | `7d6dcd21f9c4cced8544608c2944a572a942feb1a97d9d28ff60f26592a249bd` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/briefs/change-d/BRIEF.md` | `22da890fe05ea9a58316fb4351285df9a3ae4425e86f5e84e9708fa744d381a7` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/briefs/change-d/brief.json` | `f991c76538ae80409225040f32efb762a781cbddd5e89b9fd286a85c79a3c06a` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/briefs/change-e/BRIEF.md` | `5a1acb081de2818f38d02eada5393f0202f496509cca437e7d15d76e8ad27dfb` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/briefs/change-e/brief.json` | `a680141fae3ddea3be581dedb9713eced1a5a264fdf53442bef20d5b8d6f5c4f` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/briefs/change-f/BRIEF.md` | `1fceb3a6cb4a77a5655f8a0528ff0c0ee7e0605b48723237a049c852e2b7d680` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/briefs/change-f/brief.json` | `b60e1401425384ea34b76bd35939a774dd1936b2c66b8c61c66d0f6a767b5c2b` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/briefs/change-g/BRIEF.md` | `58f50c2023e67b94311fc654bbf020878782fc58c3fc94db975067141e67b511` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/briefs/change-g/brief.json` | `e8be23241b18c1662600b13e0e4f4f5ad18cd08b49368cc9422f28c5184b5a2d` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/briefs/change-h/BRIEF.md` | `98ea94a727c0da5ea3ff62efdc90843822288ca3a9a9e06e381f2fb680aff9ca` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/briefs/change-h/brief.json` | `679c52990eea01b8b1ae9f99f5ba148d9e07a9472ce9c65084eeb04da0f79a59` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/corpus/change-a.patch` | `407ad163ab6eb2cab925637653d5e9690747337a3deac40420ffd429fe4c9395` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/corpus/change-b.patch` | `f3eb5e9ba9494b1af562585af0d6f2c918675abe3b414355688f544a2ad60e9b` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/corpus/change-c.patch` | `bbe9bbdd11d343342320ac59121ef58069d642dc5d6731641f12aefc3af79565` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/corpus/change-d.patch` | `073351b86f75840e9ace423da605270c5ec50fbee0d981b54e971b711062b3e8` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/corpus/change-e.patch` | `19205ac748dd1d417e3cf44bc129ef6fa2b1077737e58499afc8fcc2b18d098b` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/corpus/change-f.patch` | `526bd626c733dc7d183d7f63135d10a1dc881871d2c13bc5bcc20723a8178bdb` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/corpus/change-g.patch` | `df6055d84ddedb0754c020f5229fcfd0176fae0e09feac89955f99032ffd42b0` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/corpus/change-h.patch` | `40fb9121508324c65f4be37fc3c548a840ca62f2fb97e3c7939db6b55e9db6f5` |
| `.gnd-planning/milestones/pins-and-review-check/notes/phase-PF2-spec.md` | `bcc54d82483074f2049f1e65603d4a88ee9b39bc1b9968afd637550f941c069b` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/GRADING.md` | `86ee0bd436b57f6f6e63f439bdefe0c1da7691e32ee7684df8c6130259eec262` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/grade.py` | `def7224e0753a088e7c5e9e90c3ef8fee638d4fc6dc4daa8fde90e097e471e3a` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/key/ANSWER-KEY.md` | `3c8b789cf61ccc5c193774c393350dc6600d51c9f6e5206639d22fe9ab79f830` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/key/branch-map.json` | `9cc6dd3636f6a238956e873a44f80e05e3516bfd90f2a553393d863604b043c6` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/key/grade-runs.json` | `903d3ae8df4422ac3514b1a718b8c85c60c5181fac181813f72f2b403391e3ab` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/key/key-runs.json` | `d57859ec0c917bcbff7d05fb485912edfe31e01682f7362b7acabad5288254d5` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/make_corpus.py` | `9c9366963301b04b6ff2569b21a9cceff7d39a86f6ec1d80403e95fe32b5647b` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-a/FINDINGS.md` | `6503806d9b8eae205286ebcda7ff6b9cb30531d7609345e8cb7eb8cfb77a7699` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-a/review.log` | `067e3d6fcaaa0d80b7187d2cf8816f4eba06b1d04e8dbe3b38256e16e05b3388` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-a/review.md` | `985d31c39101cedcd13951ae6c8444146fff0df629f9b0f11e5d5a6789ae8359` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-a/run.json` | `9ee06adda391975f6efe47b1de55e9fbd887f3d07cb6d82a4551f3668460460d` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-b/FINDINGS.md` | `6503806d9b8eae205286ebcda7ff6b9cb30531d7609345e8cb7eb8cfb77a7699` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-b/review.log` | `6b15db271afef533ffb6855838d9480f83a6fd781be28340211e45cda91cc6ae` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-b/review.md` | `00b7e5236c5dbaf673b5b34d2f4fe92fa2fc7d0214a768ce991f3e9d33974ba1` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-b/run.json` | `88ea6dbb5b17a0200a2376cc43841c4691d9f2a1901f4155731a9e2a805173fd` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-c/FINDINGS.md` | `6503806d9b8eae205286ebcda7ff6b9cb30531d7609345e8cb7eb8cfb77a7699` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-c/review.log` | `d69a7701583fc83e21198299653a620fb31517b08ae12e4aec8e16f6a917da11` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-c/review.md` | `d030482a0182f56d10dee5db53805ccb49e4b2ee3c2727a1f287ecd6a26872b7` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-c/run.json` | `b887be5b3303d2b741610c97d862b733dab10d4b63ce95a9221943b417b261da` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-d/FINDINGS.md` | `6503806d9b8eae205286ebcda7ff6b9cb30531d7609345e8cb7eb8cfb77a7699` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-d/review.log` | `75ce653331ef0f0c712123dc586d303b9fd8174d53abd4fe0a9394f6c2fd8c56` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-d/review.md` | `8f83426e1f8345190139c2b1fd9a54f3059dd731086d87aadec38331b7818bc3` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-d/run.json` | `dd69f93adb4bc03036cccb08580ed642e8afc686306ccf78396abebdf51742e6` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-e/FINDINGS.md` | `6503806d9b8eae205286ebcda7ff6b9cb30531d7609345e8cb7eb8cfb77a7699` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-e/review.log` | `0c9daf632b629b0998014060ae488512cbc008fc53e0caa2d8982510e473ec2a` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-e/review.md` | `821ef2081f8c95c10c75c69b32b410f7ad2e81296d209163dd2c0df6e9f3aa4c` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-e/run.json` | `153daf0680d06b5092451c673b6091d90e98fdbafd190f9508e109ceed56635e` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-f/FINDINGS.md` | `6503806d9b8eae205286ebcda7ff6b9cb30531d7609345e8cb7eb8cfb77a7699` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-f/review.log` | `54e1ad5e8a5f94d8aefc876705f06dfe290a3acc87256f31efc12dfcff04c653` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-f/review.md` | `cc5a66143bf6a37410b4f03f2094e4c0f38d707de8012c5d4e2fbe72dc1dbf86` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-f/run.json` | `a664ea58f79b30d11098ae26cbd2614b08f1b89fcdfc2485e5c510a02089191c` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-g/FINDINGS.md` | `6503806d9b8eae205286ebcda7ff6b9cb30531d7609345e8cb7eb8cfb77a7699` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-g/review.log` | `c852d074e63abd8d27736084d83e6edad3508d60efe9a92ac8c18dc195f1bb41` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-g/review.md` | `815a65efe427a13bdd8b397dd44ea9a2612480afe5d39f220d6be1246aa1b2ba` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-g/run.json` | `265e6af87b5e39df21e51964f98676a4d4425185dd617faa29d5e879c993c19c` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-h/FINDINGS.md` | `6503806d9b8eae205286ebcda7ff6b9cb30531d7609345e8cb7eb8cfb77a7699` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-h/review.log` | `c741773d54463c7ef6f824afa11fca5d79d446b499b8e33f76b1ac8d6eff2382` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-h/review.md` | `22fbb473d83581a380e2f80b0d8819aa7cea2f7227fbd343543136ae55a9fa2f` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/reviews/change-h/run.json` | `d7cb65844ec33504ffa1fe314628e872b8df91131a517281370e7843d6a323db` |
| `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/run_key.py` | `02379cdf61ef260da345ae6a9afc800ae627c6d155fb172b8126d52778c6bdc1` |

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
