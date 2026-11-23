# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this AC1 implementation prove the exact covered COUNT roster for a caller-selected group and preserve ordinary aggregate semantics under untrusted inputs and configured work limits?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Replay scans the authenticated relation independently and checks the caller's expected request, all distinct contributions, ordering and the first supporting row.
- C2. An empty covered group certifies zero, undeclared or opaque coverage refuses, and ordinary aggregate rows retain nonempty group semantics.
- C3. Wire limits, raw snapshot sizes, scan budget, projection and export are bounded and fail in the specified order.
- C4. The added commands follow disclosure policy and never replace an existing certificate path.

## The change under review

The work from `4d909883` to the working tree at `c56ce7515a7d`. Its diff is `.gnd-planning/milestones/aggregate-count-certificates/notes/reviews/phase-AC1-r1/diff.patch`.
- deleted: tests/fixtures/count-certificates/empty-group.json
- deleted: tests/fixtures/count-certificates/group.json
- deleted: tests/fixtures/count-certificates/member-targets.json
- deleted: tests/fixtures/count-certificates/model.orm.yaml
- deleted: tests/fixtures/count-certificates/population.json

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/aggregate-count-certificates/notes/reviews/phase-AC1-r1/diff.patch` | `15446f3df7bc8f5e30e858d5f9beba524de37ff2454c5fe129a3cfb850d06b7b` |
| `.gnd-planning/milestones/aggregate-count-certificates/evidence/AC1/dynamic-query-successor.json` | `fa91ff3cbff2cfe6d9e903a2c3ac7ff08e21895f6b4a275f70b41e5e18d97a8b` |
| `dev/components/COMPONENTS.md` | `9a633f5b49b4d244381e0116f5d7683a461d6280000a0def59d1daf43787d7a2` |
| `dev/components/graph.md` | `40fedb042498c0615013f4d1f5c8c982f2ff45019cba6e762697383fb60e56f9` |
| `dev/components/modules/_root.md` | `df4c6f18bc33550e4bf0f73c23f7d433bef3723684d22f250d7d8d11422c1976` |
| `dev/components/modules/commands.md` | `01f57b13d4a86e156709df04c244e793b5e1cdf30471daabd602dbfdc9e1817f` |
| `dev/components/modules/witness.md` | `80ea10ffbf0737a347254a9715d665bb497e890f37d20ec41e0bd12acb2479aa` |
| `docs/reference/cli.md` | `dc02c11af31aef45a0deb6527abfe7e0623a574080890482559cc5f8cc2a9b8c` |
| `docs/reference/disclosure.md` | `3517e94e75d7c10994eeb0a4dbb118c2d5bf6ed6fa6888826e1b76cfb5827cb8` |
| `src/gnd/artifacts.py` | `d1b80cd64f4509caadbdc2120d456da80113ba077a33afc6ac92f1845f759643` |
| `src/gnd/commands/witness.py` | `cebd5edc70342382e1384c24ed66d474eba516f50b74a1a3d2a548e325b135ea` |
| `src/gnd/disclosure.py` | `35652a1e93679b0adb813cbe272b5d082f2d466cdc43d20e9d286d9e6ad4c390` |
| `src/gnd/examples/literature/count_fixture/README.md` | `c051669375f2215cbdc9a7378453e279792f874c88af07eedfbeba81f271b67a` |
| `src/gnd/examples/literature/count_fixture/empty-group.json` | `98460aa95a1e03526a5182563286084b56f1674652544154e5dc0f257c96045e` |
| `src/gnd/examples/literature/count_fixture/group.json` | `ff174c391221d8f4320b40750e5039121e8a75819e57a19a36989a1daed4c807` |
| `src/gnd/examples/literature/count_fixture/member-targets.json` | `3915303cdd0817c4f7adeca98e9f7706423bee040637723e58cd634e7b5cd6d8` |
| `src/gnd/examples/literature/count_fixture/model.orm.yaml` | `abf5eaa487a2eafb379a30ba7a04278a9bbf9ba85e904aeddf07ad190bb569bb` |
| `src/gnd/examples/literature/count_fixture/population.json` | `aeb688b5b147ceeebfca60672995ca51bddd09b5ae5547c5bc984228ddc3bf72` |
| `src/gnd/skills/gnd-export/references/count-witness-contract.md` | `ec30349249cd3a9b010f6dda4b6a1d471c242e520c29dbb232dfd5507ab72803` |
| `src/gnd/skills/gnd-export/references/witness-contract.md` | `9f4cfe5876cc3eddff92171aacbe64e69a39c7362db6e0f336321086d0238278` |
| `src/gnd/witness/count_cli.py` | `4695860361f22024a43b0b3fbef322d3640cb7595e321463c680a3879653d7f9` |
| `src/gnd/witness/count_membership.py` | `58930450c93016b1c7f5fc8322c1845bcc05c0888c8ba4f1850a93a398361ce7` |
| `src/gnd/witness/count_producer.py` | `2bc4c0cfac1ab375db2df0d50427e00cdbe1d37db82101a1bae8c47f1d0f2ac1` |
| `src/gnd/witness/count_replay.py` | `f7f06c1b7ab41ff21937e04b94add56b0740e64bb080dcfead92a0ea0d9f18db` |
| `tests/fixtures/count-certificates/README.md` | `3d5c78f56cadcece7c3abfee27f20412ed143264f7a93107e9be45d5fe96c036` |
| `tests/support/pyrel_application_successors.py` | `a33966318dfd8c913618f6504578aa330660b1b3603fdfefea51abc2ab475f77` |
| `tests/test_count_certificates.py` | `ea617d2321f4cf0c554373cb1b10770d3e1b415560f134b6ceba3da8b73da327` |
| `tests/test_disclosure_mode.py` | `d5fced7f71a6fcaf772d0269a150447c00b232decd09fbc70d36edda7ff11c0f` |
| `tests/test_packaged_skills.py` | `5900ce3b675c6ad6fc25a7bd0c0ff0e75f6f2ec87b307ca46bce320576c9abf3` |
| `tests/test_rf1_cli_pins.py` | `06d2c70996608204cb4f88090f1fa409733de42a943489ea3bdb96f9515f6943` |
| `tests/test_rf5_commands.py` | `9fc8a63d7c3fc8d6fb171b7223ace7e8b42d4af6f35e035eda82fd55733ff4d7` |
| `tools/gnd_entrypoints.json` | `cca2fc0cc873ec831ed379162d885b9bd0ddfe04219095d99b3634ef74c3a5ef` |
| `tools/gnd_layers.json` | `2fee13e2fc06bbd546e2f49237267b44f48d5ab1c9abf53d35384048185e5ea8` |
| `.gnd-planning/milestones/aggregate-count-certificates/notes/aggregate-count-certificates-plan.md` | `cd4f3b24b3c1427ce4b214fee08b81111bc832da0ca51f9c94189c905cd74a0c` |
| `.gnd-planning/milestones/aggregate-count-certificates/notes/phase-AC1-spec.md` | `ffde3900151bdc6bc6a87ce5d7f0cfc9f972d965cb7d13e2bf4b28b9160c85e0` |
| `.gnd-planning/milestones/aggregate-count-certificates/002-phase-AC1-spec-gate.md` | `38db868c385b0b7e1a2be39278d3292f9fb2da1000518aaaf59c5da0a4e9c3d5` |
| `tests/fixtures/count-certificates/expected.json` | `8bc8a16dd19500c81fd55109920549e3ecbedcf3c544b94781839baa7b855a55` |

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
