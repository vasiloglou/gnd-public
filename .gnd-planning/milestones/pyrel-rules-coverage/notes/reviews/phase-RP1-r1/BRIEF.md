# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does the RP1 diff lower GND's external uniqueness (shared-entity join, semantic_spec.role_sequence_rows and checker/_core.py _join_rows) into the rules programs with the same verdict and witness as gnd check on every accepted input, and refuse by name what it cannot represent?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. RP1-C1: assertions/ and lineage/ export under --rules duckdb and lqp, exit 0
- C2. RP1-C2: both programs state the one external Requirement (Check same over anchor pairs) from the shared IR
- C3. RP1-C3: the DuckDB program agrees with gnd check on the packaged assertions population (0), a duplicate pair (1) and an empty join (2)
- C4. RP1-C4/D4: a non-string value of an externally identified entity is refused (exit 3) by name, where GND exits 0
- C5. RP1-C6: a disconnected join is listed not checked (exit 4) with facts, and vacuous (exit 2) only when every referenced list is empty, as measured
- C6. RP1-C7: an ambiguous join is an invalid model at export, exit 3, as gnd check refuses it
- C7. RP1-C8/C9: numeric anchors 1 and 1.0 join as GND joins them; a three-fact-type join agrees
- C8. Within one fact type the anchors are its roles (GND projects); across fact types they are object types
- C9. The Ossie export of assertions and the three-way fixture keeps its pre-phase bytes; for models without external uniqueness or external entities, the report template's new branches never fire, so every other family keeps its verdicts

## The change under review

The work from `6cfeed33` to the working tree at `6cfeed33433a` with uncommitted changes. Its diff is `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/diff.patch`.
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP2-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/ambiguous.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/assertions-duplicate.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/assertions-empty-join.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/assertions-integer-id.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/disconnected-empty.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/disconnected-facts.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/disconnected-partial.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/disconnected.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/numeric-anchor.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/numeric-duplicate.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/renamed-anchor.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/renamed-duplicate.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/three-way-duplicate.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/three-way-pass.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/three-way.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/test_rp1_external_uniqueness.py (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/diff.patch` | `dce5ed910fc49e7e445b9a50c569eaa3d72a93dbf2f4328e5e2907b1a2146dc3` |
| `docs/runtimes/pyrel.md` | `38712ee499852a45d9539c82edbbe915f2b8689a10501e670d57e6caa60daefb` |
| `src/gnd/export/pyrel_rules.py` | `5ca0cbb270740ea2a6fedfd6a87d676f966f21444a3a300f3e47df28c798e856` |
| `tests/test_pyrel_rules_families.py` | `3389b5662e5153c46ef6ee01fa3875e7677dcf98df02770a3d0cfe11d3f01aa1` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log` | `29e5bb8e3df4449f059bde94dbd0978425590735c205e106fae0f99f46c272ef` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log` | `ad6e15580205508df8f33356314f9f7072521cf01bd493151e42dba41e697b48` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log` | `5da792cfb6c988e2a9f21c01ad7f4f2d55010781af2f27579e4e03c156c7a5a5` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP2-r1/review.log` | `c2bf65c347c1197196e91a95d0bbec8e1b7ed9565d8ddf94b0da0392a58e96e3` |
| `tests/fixtures/pyrel-rules-coverage/rp1/ambiguous.orm.json` | `f3f03f1637adf5e8b93bfe45235d038a3917de186b4cd7364b3390353aa01e99` |
| `tests/fixtures/pyrel-rules-coverage/rp1/assertions-duplicate.population.json` | `8a5d7f5276f673a6ef11a31dcb78b7ec08a5ff1d42295d5b12cc60dae84e6a60` |
| `tests/fixtures/pyrel-rules-coverage/rp1/assertions-empty-join.population.json` | `baa942110dd260f6cbf432d0fa50130c027e66751b7376202bfa36125ef1ff24` |
| `tests/fixtures/pyrel-rules-coverage/rp1/assertions-integer-id.population.json` | `2a309fb0f0d47e3d6cf13b4a4cec42b138977fe5b33a521d2aac5caba8dc0afe` |
| `tests/fixtures/pyrel-rules-coverage/rp1/disconnected-empty.population.json` | `4233be1a90c2bc42a5bc0282280dce817af058bfe1190694f8bf6626d21c2bc3` |
| `tests/fixtures/pyrel-rules-coverage/rp1/disconnected-facts.population.json` | `9e2f8da3eba0920f8a85c02799babda5e3fac0c44684981779ec2f6ceb58323f` |
| `tests/fixtures/pyrel-rules-coverage/rp1/disconnected-partial.population.json` | `69511dd3fa9360f4a364af91afafa579ca49327fe7f03503d378f022be5ee409` |
| `tests/fixtures/pyrel-rules-coverage/rp1/disconnected.orm.json` | `3d2c1de99b1837846295d5cdd0d62091a62a6d32000e2c0abf5f6679d846273e` |
| `tests/fixtures/pyrel-rules-coverage/rp1/numeric-anchor.orm.json` | `b3eddc57affb401533190862e74a6a6149ffb48f5b17e9e596aac81bd30b37da` |
| `tests/fixtures/pyrel-rules-coverage/rp1/numeric-duplicate.population.json` | `179bf97f2e3a0fe3de23f3c89136d285bc443649f0b9d379af5f9665e315ec4c` |
| `tests/fixtures/pyrel-rules-coverage/rp1/renamed-anchor.orm.json` | `6f6d4191965111f29dd891735ae6790183e682bdbe7426ff87a8434ee51639ff` |
| `tests/fixtures/pyrel-rules-coverage/rp1/renamed-duplicate.population.json` | `21d6b09b43d37ee4700b2b8e729324c59b8e8f02dc66cee7ecfe86ef5180e6db` |
| `tests/fixtures/pyrel-rules-coverage/rp1/three-way-duplicate.population.json` | `459d7f4c776c7eeafe67028edbcd9e2f00a5bc80fa735957eef98c995ff91935` |
| `tests/fixtures/pyrel-rules-coverage/rp1/three-way-pass.population.json` | `1a96a6509b3471a71d24e3d1638d806dcdc0e529128e33441fe540068b8eccd0` |
| `tests/fixtures/pyrel-rules-coverage/rp1/three-way.orm.json` | `2f683881401a274e9a093e94756772eab373706ddaeb9db366fc74925bc015d9` |
| `tests/test_rp1_external_uniqueness.py` | `54db27cccca3ee71b70884ddc9f131544c06c3382eebe4caae592d7f1e93f7e0` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/phase-RP1-spec.md` | `de95894e6e26c4b78f7d982a0b029f38d0534878d0aea80efd13ad3ed4619818` |

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
