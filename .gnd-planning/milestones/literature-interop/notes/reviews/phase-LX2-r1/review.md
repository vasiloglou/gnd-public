I reviewed LX2 (`ac157120` → `1274776436b6`) and am requesting changes: one finding breaks claim C3, the legacy compatibility claim, and three are low severity. All 26 files match the hashes in the brief. The focused test gate passes (`316 passed in 45.14s`). I wrote nothing to the repository; my repro scripts are in `/private/tmp/lx2rev/`.

## Findings

**F1 — Model files that aren't regular files now fail on the old include-free route (breaks C3).**
- **Where:** `src/gnd/witness/flattening.py:33`.
- **What's wrong:** `resolved_projection` now reads the root model with `read_regular_path` before it hands an include-free root to the unchanged legacy functions. That reader refuses anything that isn't a regular file, and it uses up a stream.
- **Who it affects:** the CLI and `gnd.api.witness`/`replay`, which now go through `rooted_*_result` (`service.py:150`, `:418`, `:432`).
- **Consequence:** a model given as a pipe (FIFO), `/dev/fd/N` or `<(…)` used to work and now exits 3 with `input-invalid`.
- **Reproduced:** same model and population passed through a FIFO: `witness_result` gives `0`, `rooted_witness_result` gives `3 input-invalid`.

**F2 — Stale bindings during `gnd witness` report `input-invalid`; replay reports `binding-stale` (low).**
- **Where:** `service.py:150-170`, and `composed_witness_result` around line 275.
- **What's wrong:** `StaleWitnessBinding` is a `ValueError`. Only the replay functions catch it by name (`service.py:250`, `:311`).
- **Reproduced:** a stale `--flat-model` or a changed pinned include makes `gnd witness` exit `3 input-invalid` and `gnd replay` exit `3 binding-stale`.
- **Why it matters:** the spec says "wrong bound bytes … yield binding-stale" and does not limit that to replay.

**F3 — The include route refuses symlinked population and artifact paths (low).**
- **Where:** `service.py:107` and `flattening.py:62`. `read_regular_path` refuses a symlink anywhere in the path.
- **Mismatch:** the root path is resolved through symlinks first, and the include-free route follows symlinks.
- **Reproduced:** a population or `--flat-model` path through a symlinked directory exits `3 input-invalid`. On macOS that covers any `/tmp/...` path.
- **Why tests miss it:** they use `tmp_path.resolve()`.

**F4 — Witness production now checks the model before the targets (low, close to style).**
- **Where:** `service.py:158` resolves the model before `load_targets` at `:127`; the legacy path parses targets first (`:182`).
- **Reproduced:** with a missing include and malformed targets, the legacy function gives `input-invalid` and the new one gives `include:unreadable`. Both exit 3.
- **Why it's minor:** the spec pins the order only for replay.

## Checked and true
- **C1 (independent re-derivation):** `kernel.py:315-343` re-derives each node's model origin from the authenticated projection, after the flattening, composition and identity binding checks and before the proof graph. Model origins and fact occurrences (`base.origin` and `sources`) stay separate. Comparison nodes use their rule's fact type. The origin map covers every fact type.
- **C2 (refusal order), replay side:**
  - A malformed certificate is refused before a stale include.
  - A stale input wins over a forged origin.
  - Unpaired `--flat-model`/`--flattening-record` exits 64.
  - An oversized record gives `input-invalid`.
  - Cross-version replays, v3 on an include-free root or v1 on an include root, give `binding-stale`.
  - The byte ceiling is rechecked after the model origins are stamped in.
- **Schemas:** both certificate schemas and the result schema accept a real v3 result. They reject:
  - v3 without `model_origin`;
  - v1 with `model_origin`;
  - v3 without `flattening_sha256`;
  - v3 with `sources` but no composition.

  The v1 and v2 key sets are unchanged.
- **Weaker legacy coverage (not a defect):** the edits to `test_mc2_consumers.py` and `test_li0_witness_wire.py` follow decision D3, but no test now checks the include guard on a composed `witness` call with valid targets.

## Not checked
I didn't rerun the structural guard lane, whole-tree Ruff, the strict component check, or the full and historical lanes. I didn't check pre-change v1/v2 byte goldens beyond what the focused tests assert, or T8 timing beyond the test's 5-second bound.

VERDICT: CHANGES_REQUESTED
