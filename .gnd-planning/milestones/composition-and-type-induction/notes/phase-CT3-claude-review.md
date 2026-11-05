# CT3 review: witness lineage (uncommitted tree on 2c25ba4)

Reviewer: one local reviewer agent. I only read the repository. I made no edits and touched no git state. All probes and mutants ran from the scratchpad, using `PYTHONPATH=<scratch>/src` copies.

## Verdict: approve-with-fixes

The core design holds. The record is checked against the model and population bytes. The raw-byte record digest is bound. Replay compares every base node's `sources` with the record's lineage, and `certificate_shape` is total and strict on hostile v2 input. Version-1 output is byte-identical: I re-ran the parity capture myself. One fix is needed before commit (F1): composed witness and replay raise uncaught exceptions on ordinary bad paths, which breaks standing rule 1 (totality). The other findings are smaller.

Focused gate (the 13 files in the brief): **697 passed**. The rest of the spec's selection (`test_public_api`, `test_v61_phase2_api`, `test_rf1_layering`, `test_packaged_skills`, `test_skill_prose_sync`): **119 passed**.

## Findings

### F1 (blocking): composed witness/replay crash with exit 1 and a traceback on unreadable, symlinked, missing or `..` paths, and on an incomplete record
`src/gnd/witness/service.py:660-675` (`_composition_lineage`), `:698-699` (`_INPUT_ERRORS`), `:677-688` (`_stamp_composition`).

- `read_regular_path` raises `gnd.artifacts.ArtifactError`, which subclasses `Exception` directly, not `ValueError` or `OSError`. `_INPUT_ERRORS` does not catch it. Reproduced on the CLI. Each case printed a traceback and exited **1**, the code that means `proof-invalid`:
  - `gnd replay M P CERT --composition missing.json` gives exit 1 (`ArtifactError ... No such file or directory`). It should give 3.
  - `--composition` naming a symlinked record gives exit 1. So does a record path containing `sub/../`.
  - `gnd witness M LINK.population.json --targets T --composition R`, where the population path is a symlink, gives exit 1. The same command without `--composition` exits 0. On macOS, `/tmp` and `/var` are symlinks, so any absolute path under them hits this.
  - `api.replay(..., composition=symlink)` raises `ArtifactError` to the caller.
- `_stamp_composition` indexes `lineage[(fact_type, fact_index)]` outside any try. A schema-valid record whose digests match but which omits a fact gives `KeyError: ('contract_has_party', 0)`, a traceback, and exit 1. `parse_record` checks shape only, and D1 says the record is not re-derived, so a hand-edited record is a legitimate input this path must handle.
- **Fix:** add `ArtifactError` to the caught set, or wrap the reads the way `checking_service.read` does (`raise CompositionError(...) from error`). In `_stamp_composition`, use `lineage.get(...)` and refuse with 3 `input-invalid` (or raise `WitnessInputError` inside the try) when a base fact has no lineage entry. Add tests for a missing record, a symlinked input, and a record that lacks a fact.

### F2 (non-blocking): stamping happens after the producer's wire-ceiling check, so a v2 certificate can exceed the ceiling replay accepts
`service.py:677-688`, against `producer.py:247` (`validate_witness_structure(...) >= limits.bytes`, which turns into the `work-limit` exit 4).

The ceiling check runs on the v1 certificate. `_stamp_composition` then adds the digest and roughly 95 bytes per base node, with no second check. Measured on the T3 fixture: 1213 bytes before stamping, 1473 after, for 2 base nodes. Deduplicated lineage can make it larger. A v1 certificate just under 10 MiB becomes a v2 certificate over the ceiling. `gnd witness` exits 0 and `--out` writes it, but `gnd replay` refuses it in `read_wire` (3). So a successful witness yields a certificate that cannot be replayed. **Fix:** after stamping, run `validate_witness_structure(certificate)` again (keeping the final-newline accounting). On overflow, return `WitnessResult(4, ..., reason="work-limit")` as the producer does.

### F3 (non-blocking): replay success does not mean the lineage is true; the docs should say so (CT-R2)
`docs/reference/composition.md` (new "Trace a derived fact back to its sources" section) and `witness-contract.md` §Version 2.

I forged a record by replacing every fact's `sources` with `{contract-b, bogus, 99}`, keeping its digests valid. `gnd witness --composition` exited 0 and `gnd replay --composition` exited **0**. `gnd check --composition --sources` exited 3. This follows from D1 (no re-derivation). But the reference page says a derived fact "traces to the passages of every document it drew on", and a reader may take replay 0 as confirming that. **Fix:** add one sentence to both documents: replay checks the certificate against the record, not the record against its sources. To check the record, run `gnd check --composition RECORD --sources DIR`.

### F4 (non-blocking): the producer accepts a model with reference populations and stamps reference-origin bases with candidate lineage
`service.py:702-710`, `:687`.

`composed_witness_result` calls `witness_result(...)` with the default `reference_root=None`, which still binds the model's declared references from the model's directory. The stamp key `(fact_type, origin.fact_index)` ignores `origin.kind`. So a reference-origin base node would get the lineage of the candidate fact with the same index, or a `KeyError` (F1). `composed_replay_result` passes no reference inputs, so such a certificate always replays `binding-stale`. Compose refuses reference models (CT-D11), so this needs a hand-made record. It is still unguarded. **Fix:** refuse (3) when `model.reference_populations` is non-empty, or when any base node has `origin.kind != "candidate"`.

### F5 (non-blocking): the record digest check and the witness read the input files separately (TOCTOU) and with different read rules
`service.py:670-673` uses `read_regular_path` with cap `MAX_DOCUMENT_BYTES` (10 MiB) and refuses symlinks. `_witness_inputs` reads again with `Path.open` and `DEFAULT_LIMITS.bytes`.

The digest that is checked is not taken from the bytes that are proved. **Fix (optional):** read once, then hash and parse the same bytes. For example, give `_witness_inputs` a raw-bytes entry point, or return `mr` and `pr` from it.

### F6 (non-blocking): test gaps (surviving mutants)
See the mutant table. Each of these survives `tests/test_witness_composition.py`:
- The model-digest check removed (m3): no test passes a record built for a different model.
- Replay checks only the first base node (m2): the edit test always edits the first base node. Edit the last one, or each one in turn.
- The `fact_index` integer check removed from the shape (m6): no hostile-shape tests for `sources` or `composition_sha256`. I checked by hand that the shape is total (table below), but nothing pins it.
- The producer looks up lineage at index 0 regardless (m9): every asserted premise has composed index 0. Use a premise with a composed index of 1 or more.
- `witness-view --expand` drops `sources` (m10): only the plain view is tested.
- T7 tests only `why-not`. The spec's `gnd export souffle-witness` case is missing.
- T9: no test pins the signatures of `api.witness` and `api.replay`, even though the spec says they are "updated and passing". The `composition=` keyword is exercised only through calls.

### F7 (nit): the JSON Schema is looser than `certificate_shape` on a few values
Probe table below: shape rejects and the schema accepts `fact_index: 0.0`, a 400-digit `fact_index`, a `composition_sha256` ending in a trailing newline (`^…$` lets a final `\n` through under Python `re.search`), and `version: 2.0`. Shape is the stricter side, which is safe. Most of this exists already for v1 (`version: 1.0`, the other digest patterns). Optional: anchor the pattern with `\\A…\\z`-equivalent wording, or record in the contract that shape is authoritative.

### F8 (nit): the contract's replay paragraph leaves out the `input-invalid` row
`witness-contract.md` §Version 2 gives "a different record digest is `binding-stale`". It does not say that a record which fails to bind the replay inputs is `input-invalid` (3), as the spec's table does. Add the row.

### F9 (nit): the T1 parity capture covers success paths only
`evidence/CT3/capture_parity.py` records 20 rows, all with exit 0: witness, replay and view over the two v71 cases. It includes no failure-path v1 replays (stale binding, edited premise, shape refusal), and none of the why-not or replay-admission fixtures that the spec's T1 row names. Those paths are covered by the gate suites, which pass, but the before/after table does not record them. The v1 kernel path is unchanged by inspection (`binding != identity(...)` with no composition key), so the risk is low.

## Reproductions run

- Gate: 697 passed. Extra selection: 119 passed.
- Parity: I exported `a2e44f8:src` with `git archive` into the scratchpad and ran `capture_parity.py` against it and against the worktree. My two outputs match each other byte for byte, and each matches the committed `parity-a2e44f8.json` and `parity-after.json` (20 rows, all exit 0).
- Probes (`scratchpad/probe/test_probe.py`):
  - A: a record missing a fact gives a `KeyError` traceback and exit 1 (F1).
  - B: a forged lineage gives witness 0, replay 0, and `check --composition` 3 (F3).
  - D: a node that no root reaches is rejected by the shape (3), so every base node in a shape-valid certificate is reachable, and the kernel loop visits all of them. A reference-origin base gives 1 `proof-invalid`. Swapping `sources` between two bases gives 1. A record re-serialized with the same content but different bytes gives 3 `binding-stale`, as raw-byte D3 intends.
  - E: under `GND_DISCLOSURE=customer`, replay (plain and `--json`) and witness-view (plain and `--expand --json`) leak none of `Acme`, `Lyon`, `C-1` or the canary. `witness --raw` is refused (3).
  - H and J: symlinked, missing and `..` paths crash with exit 1 (F1).
  - I: stamping grew the certificate from 1213 to 1473 bytes (F2). `ArtifactError`'s MRO is `Exception` only.
- Shape/schema agreement on hostile v2 input. Rows are probe cases, columns the two checkers' results:

| case | shape | schema |
|---|---|---|
| sources "x" / [] / {} / [[1]] | reject | reject |
| entry with an extra key / missing `source` / `source`: 1 | reject | reject |
| fact_index true / -1 | reject | reject |
| fact_index 0.0 / 10**400 | reject | accept |
| digest uppercase / int / `sha256:`-prefixed | reject | reject |
| digest with a trailing `\n` | reject | accept |
| v1 with sources / v1 with the digest / v2 without sources | reject | reject |
| `sources` on a rule node | reject | reject |
| version 2.0 | reject | accept |
| version true | reject | reject |
| 200k source entries | accept | accept (bounded by the 10 MiB wire cap at load) |

## Mutants (against tests/test_witness_composition.py)

| id | mutation | result |
|---|---|---|
| m1 | kernel: lineage mismatch no longer raises | killed |
| m2 | kernel: checks only the first base node | **survived** |
| m3 | service: model digest not checked | **survived** |
| m4 | service: population digest not checked | killed |
| m5 | kernel: `composition_sha256` not compared | killed |
| m6 | io: `fact_index` integer check removed | **survived** |
| m7 | io: v1 base keys include `sources` | killed (trivially: exact key set) |
| m8 | kernel: v1 plus `--composition` accepted | killed |
| m9 | service: lineage looked up at index 0 | **survived** |
| m10 | view: expanded view drops `sources` | **survived** |
| m11 | order-insensitive compare | discarded (the mutant did not parse) |

## Not checked

- Full test suite. I ran only the gate and the rest of the spec's selection.
- The anonymity scan tool. I grepped the changed files for the downstream app names and found none.
- The RF1 golden contents beyond their tests passing. RF6 successor evidence is checked only through the gate.
- A real near-10 MiB composed witness for F2. That finding rests on the measured growth and the order of the code, not an end-to-end run.
