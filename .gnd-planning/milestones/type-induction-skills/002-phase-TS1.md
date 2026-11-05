---
milestone: type-induction-skills
station: "phase-TS1"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-TS1
date: 2026-11-05
gate:
  command: "uv run pytest -q tests/test_discover_fact_type_family.py tests/test_discover.py tests/test_evolve_additive_policy.py tests/test_evolve_shape_matches.py tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py"
  exit: 0
  output: "529 passed in 90.32s (0:01:30)"
  note: >-
    The plan section 9 TS1 row (the CT4 gate), run after the review fixes.
    The direct file tests/test_discover_type_evidence.py: 52 passed, exit 0.
    Packaging, schema sync, parity, ruff and docs are in the body and in
    evidence/TS1/gate.txt.
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request or the milestone close"
  reason: "the broad historical lanes are outside TS1's impact closure"
evidence:
  - path: .gnd-planning/milestones/type-induction-skills/notes/phase-TS1-spec.md
    sha256: 1d3719286dfb834f7574bb09c23287cc622f1d56b5e77921e9e3dac15dc476b6
  - path: .gnd-planning/milestones/type-induction-skills/notes/phase-TS1-claude-review.md
    sha256: 4e927fa60238891f666958c9a09b986a9cbc7b0540e3831a73e471f8679aeb14
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS1/dynamic-query-successor.json
    sha256: d4a3f4ddc2541f9ada7d8f9070f9362f2d710b34203934ced5030c22be5eed2a
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS1/gate.txt
    sha256: 82936a519c52e3ead2bb3e026f370d7e46a258cf6a5e8f9058ef07caae72c1dc
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS1/mutations.txt
    sha256: a83a5bcacf380866f7c56e7a3f777d096204e7c9f4215341e7e7f466e126a657
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS1/parity-after.json
    sha256: 4061906db53757824984dc82eefa43cb865b069cf2ac9e18adffa57cdc8bbe48
  - path: .gnd-planning/milestones/type-induction-skills/evidence/TS1/parity-b733b2a.json
    sha256: a093457d2119fc05d83a29650335c09419206f2167605e7e075d200ce98a312c
  - path: src/gnd/discover/type_evidence.py
    sha256: 819714656ba11662aa3d594a9ac65874e15ffedd9344d346d62a16df8dc96ff1
  - path: src/gnd/discover/types.py
    sha256: 97c40ff421510c7fabf71fcb488f6e657702539fb0488825fb6b98b0445d3f54
  - path: src/gnd/discover/service.py
    sha256: f2e7008aed2e6b8ca78d7614a9c68e3b2597659761c7ead37a97846ba0d7b4d8
  - path: src/gnd/commands/discover.py
    sha256: 4cab5abcf2319d260867b644ae2a6860882a99d0fd2daaafe24980ea8e9309f6
  - path: src/gnd/type-evidence.schema.json
    sha256: b561876934520b283019618bb6de7df3fd48acd15b9007e586e7ce08e4c6c699
  - path: tests/test_discover_type_evidence.py
    sha256: 80f2ea032d03436aa2c46929c0eb34f7697a08bf4c92c3b29b574d38fa4ab743
  - path: docs/reference/discover.md
    sha256: f67f921439dc170d3b58606d6f7f12a6a84eaa11275e18397e4c2bcdcb9aaebe
---

# TS1: type evidence from the fact-type family

**Claim.** `gnd discover MODEL POP --families fact-type --type-evidence E`
writes `E` as `gnd-type-evidence/1`, valid against
`src/gnd/type-evidence.schema.json`, while `--out`, `--report`, stdout and
exits are byte-identical to the same run without the option, in the three
disclosure modes and three fixture variants (T16). Without the option, the
IK4 discover corpus gives `b733b2a`'s exits and bytes on all 20 cases except
E6, whose stderr usage text names the new option (T17). Spec r2 was approved
`(a1)` 2026-11-05 on the prose instrument, D1–D7 as proposed.

## What shipped

- **`src/gnd/discover/types.py`:** a `GroupRecord` per group formed, in order,
  with its final status (`proposed`, `shape_match`, `multi_valued`,
  `below_support`, `mixed_type`, `over_budget`). `drop_last` marks the groups
  it drops `over_budget`. `redacted_generics` lists the skipped generics. The
  proposal and report fields are unchanged.
- **`src/gnd/discover/type_evidence.py` (new):** `origins` validates every
  fact type's `provenance.induced_from` (exit 3). `build_evidence` fills
  within the 10 MiB cap: group entries first, then candidates in model
  order until the bytes run out, with the rest counted in `truncated_groups`
  and `truncated`. `evidence_bytes` is a batch-wise fallback trim. Pair sets
  are built once per candidate. Pairs are counted only against a binary
  candidate whose value cells hold the group's kind and whose value role is
  not redacted.
- **`src/gnd/discover/service.py`:** the proposal-bytes trim now runs before
  any write. The evidence is then built (3 or 70 here writes nothing), and
  the writes happen in order: proposal, report, evidence. Path checks give
  64, 74 and 11 before any read. The service refuses the option without the
  family (64).
- **`src/gnd/commands/discover.py`:** the `--type-evidence PATH` option; the
  family-flags usage message names it.
- **`src/gnd/type-evidence.schema.json` (new):** closed objects, listed in
  both runtime schema inventories.
- **Docs:** a type-evidence section in `docs/reference/discover.md`, one
  sentence in `docs/reference/disclosure.md`, one release-note line.
- **Pins:** the RF1 `discover` goldens (help, exit, and the tree's
  `discover` subtree only), `goldens.sha256` and its digest. The RF6
  dynamic-read successor is `evidence/TS1/dynamic-query-successor.json`
  (32 rows added, none removed); the live RF6 query policy is unchanged.
  `tools/gnd_layers.json` maps `gnd.discover.type_evidence` to lane
  `discover`.

## Gate output (verbatim)

From `evidence/TS1/gate.txt`:

```
$ uv run pytest -q tests/test_discover_type_evidence.py
52 passed in 19.93s
exit 0
$ uv run pytest -q <CT4 gate: 11 files>
529 passed in 90.32s (0:01:30)
exit 0
$ uv run pytest -q tests/test_schema_sync.py
4 passed in 0.06s
exit 0
$ uv run pytest -q -m distribution tests/test_public_built_inventory.py::test_wheel_carries_every_vendored_runtime_schema
1 passed in 0.63s
exit 0
$ uv run ruff check <changed modules and tests>
All checks passed!
$ uv run pytest -q tests/test_discover_type_evidence.py   (after the ruff fix)
52 passed in 18.90s
exit 0
$ uv run zensical build --strict
No issues found
$ uv run python tools/check_docs.py site
14297 local links/assets/anchors checked
exit 0
```

Parity (T17), `capture_parity.py` over the IK4 corpus: `20 rows [0, 3, 64,
66, 74]` for both trees. The only differing case is E6 (`exit 64`, stdout
empty), whose stderr is the usage block now listing
`[--type-evidence PATH]`; checked by diffing the two stderrs. The
`b733b2a` capture's digest equals CT4's recorded `parity-after.json`.

## Measured criteria

- **T20 time bound** (standing rule 2): 1,200 groups × 60 candidates near
  the population cap ran in 9.1 s against a stated ceiling of 60 s.
- **Review F2 input** (20,000 groups × 200 candidates, model 33,728 B,
  population 809,030 B): 27.7 s and 4.0 GB RSS before the fix; 2.6 s and
  156 MB after, with `truncated` 3,986,818 and a 10,485,392-byte file.
- **Review F1 input** (40,000 one-entity attributes, 1.6 MB): exit 70 before
  the fix; exit 0 after, with report and evidence written.
- **Mutations** (`evidence/TS1/mutations.txt`): 14 mutations of the new
  branches. 13 were killed in the first run. M8b (no group budget) survived
  because the fallback trim gave the same file. The F1 test then also
  asserts a single serialisation, and M8b was killed.

## Adversarial review

One reviewer is one reviewer: a general-purpose subagent with shell access,
which ran its reproductions against the working tree and could run tests.
Findings are retained in `notes/phase-TS1-claude-review.md` (scratch path
redacted, declared there). All seven were reproduced and fixed, each with a
regression test shown failing first (`test_f1`…`test_f7`; spec §12 I1–I5,
I7, I9). Triage:
- **Blocking:** F1 (exit 70 on valid input), F2 (cost groups × candidates),
  F5 (RF6 gate red) and F6 (RF1 manifest red).
- **Hardening:** F3 (DateTime pairs), F4 (pair count on a redacted value role)
  and F7 (service guard).

A further defect (I6, a quadratic fallback trim) was found while mutating.
It has a test that did not finish in 120 s against the old loop.

**What the reviewer confirmed:**
- With the option absent, a 29-case run against `HEAD` (three fixtures, three
  modes, both value settings, error paths, the `drop_last` path) showed equal
  exits, stdout, stderr and bytes.
- None of the totality shapes produced a traceback: unary, ring, 4-ary, two
  generics, an empty population, a null or list `induced_from`.
- Under `customer`, the evidence carries no attribute digest.
- The cap loop terminates.

**Own coverage audit against §8:** T1–T20 each have a case. T7 and T7b run
as one parametrized test over internal and customer. T18 runs inside every
loader. T15 is the RF1 pin run. T17 is the parity run, not a pytest case.

## Refactoring review

- **Executed:** `_cmd_discover` now computes the proposal bytes (with the
  written-bytes trim) before, and apart from, the writes. That was needed
  for validation order. It is behaviour-preserving for runs without the
  option, by parity and the reviewer's 29-case comparison.
- **Seen, deferred:** `type_evidence` uses `types._kind` across modules,
  and the kind vocabulary (declared primitive vs cell identity kind) has no
  public home. The CT4 DateTime defect below comes from the same gap.
  Target: TS2, which renders value types from these kinds, or a
  maintenance change.

## Boundary — what this phase does NOT establish

- **Counts only.** The evidence judges nothing: `signature_equal` and the
  overlaps are counts, not duplicate verdicts (TS-R2). Nothing reads the file
  yet; TS2 and the skills will.
- **Group ids are local to one file.** A reader must bind the file's digest;
  the ids mean nothing across runs.
- **Truncation is by order.** Under the cap, later groups lose candidates
  first and the last groups may be absent. Which candidates matter most is
  not considered.
- **Kind matching is by the candidate's observed cell kinds.** A candidate
  whose cells mix kinds gets `pairs: null`.
- **Stated limits.** The time bound is one measurement on one machine
  against a stated ceiling, not a complexity proof. The evidence's own memory
  is bounded by the cap; the candidate pair sets built for kept candidates
  are bounded by the population.
- **One reviewer is one reviewer.** No panel reviewed the spec or the diff.
- **Not run:** the broad historical lanes (`evidence or census`) and the full
  default lane.

## Open questions

- **TS-Q3 (inherited, for TS2):** what `induced_from` stores under
  `customer`.
- **CT4 DateTime kind (found here, out of scope):** a DateTime-valued group
  is typed with a minted String value type, because a DateTime cell held as a
  JSON string has identity kind `string` while `_kind("DateTime")` is
  `datetime`. Target: TS2 or maintenance; the CT4 family's behaviour is
  unchanged here.
- **Pre-existing (reviewer):** a malformed YAML model (`not: [a`) gives a
  traceback and exit 1 in `gnd discover`, with or without the option, on
  `HEAD` too. Target: maintenance.
- **Plan repairs at the close:** P2, TS-R7's "expected growth zero" (I7), and
  the ledger's packaging test name (I8).

## Refuted premises

- **P2:** "if the groups alone exceed it, `DiscoveryDefect` (exit 70), argued
  in the record from the population cap" (spec §6.2). Refuted by review F1:
  a group costs about 260 evidence bytes against about 40 population bytes,
  so a 1.6 MB population exceeds the cap. Repaired within C7 by
  `truncated_groups`.
- **TS-R7, "expected growth zero"** for RF6. The live query policy did not
  grow, but the dynamic-read inventory did (32 rows), as for CT4.
