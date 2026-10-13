Retained reviewer output; edited only to replace any operator home path with <operator-home>. One reviewer is one reviewer. Disclosed interpreter-version invocation violated no-execution instruction; no project code/tests/native runtime ran.

# PA2 repair review (single reviewer, final bounded round)

**Verdict:** The R1 repair holds for everything it covers. I found one new false-accept path. It sits next to R1, involves the same "computed rows instead of claims" choice, and is outside the frozen corpus. The other three repairs check out within the limits you stated.

**Process deviation:** I accidentally invoked the Python interpreter once. A command included `python3 --version >/dev/null 2>&1`. No project code, tests or native runtime ran. Everything else was read/search, read-only `git diff`/`status`, `jq`, `stat`, `shasum` and `diff`. I made no edits and wrote nothing.

## Finding N1 (blocker-class, outside the corpus): duplicate claimed rows on a derived head with a key can be falsely accepted

GND and native evaluate constraints on a derived head over different data:

- **GND uses the claimed rows.** For a covered `derived` head, `constraint_view_legacy` takes `population.facts`, the claims (`src/gnd/extensions.py:2365-2369`). The checker feeds that view to the correspondence path (`src/gnd/checker/_core.py:347-350, 369`).
  - GND uniqueness keeps duplicates: identical rows count separately toward a key group (`src/gnd/semantic_spec.py:1052-1081`).
  - The derivation check itself compares sets, so duplicate claims pass it (`representation-format.md:1128`).
- **Native uses the computed rows only.** Constraints run over the deduplicated computed rows (`pyrel_runtime.py:1524`). Claims are compared as keyed sets, so duplicates collapse (`:1682-1684`). The inline key (`:357`) sees one row.

**Case:**
- `raw(label: String)` is asserted.
- `out(label)` is derived and computed, with body `[raw{label:$x}]` and head `{label:$x}`.
- `out` has an inline `uniqueness [label]`.
- Population: `raw=[{a}]`, `out=[{a},{a}]`, with everything covered.

| Engine | Derivation row | Key on `out` | Exit |
|---|---|---|---|
| GND | pass (sets equal) | fail (key `a` occurs twice) | 1 |
| Native | satisfied | satisfied (one computed row) | 0, accepted |

**Scope:**
- Inline uniqueness is the only admitted family that counts rows. Guarded, mandatory, value and subset all work on sets.
- When claims and computed rows are equal as sets, the universes are the same in both engines. So R1 itself is sound for accept decisions.
- `admit_population` (`:1082-1101`) does not refuse duplicate rows. I found no duplicate-fact refusal in GND either.
- I checked the frozen corpus with `jq`: none of the 20 BookRec-complete populations has duplicate rows for a derived head, and BookRec's derived heads carry no inline constraints. So this cannot move 2323/2321.

**Bounded repair:** In `_profile_admit`, refuse with exit 2 when a derived head's supplied rows contain exact duplicates. Add the case above as a native control, and if possible confirm GND's exit 1 the way the R1 test does.

**Limit:** This is traced from code. I did not run GND on the case.

## Related limit (no false accept)

When claims and computed rows differ as sets, both engines reject on the derivation row. However:

- Witnesses and row verdicts can differ, because GND's universes come from claims and native's come from computed rows.
- If computed rows make a native universe empty, native reports vacuous and exits 2 where GND exits 1.

This stays inside the A1 statement "selected frozen rows only." The spec comment "never from supplied head claims" describes a deliberate departure from GND's constraint view. It is not parity with GND.

## Claims checked and not refuted

- **R1 (cache clear):**
  - The only universe-cache writes before the clear are `universe_values` calls from the parent constructor (`:154-164`). Nothing builds a `_universes` relation before `:1485`, and `_derive` never calls `universe()`.
  - Neighbours are covered: the clear rebuilds every object type, including supertype `party`. Value types were never cached eagerly. `instances` are unaffected.
  - Empty heads leave `facts[name]=[]`, so the vacuity checks at `:1616-1621` read computed state.
  - Head failure: a `ProfileRefusal` from the constructor makes every row incomplete with exit 2. A native exception gives exit 70.
  - `entity_concepts` stays stale, defined from asserted rows only, but nothing on the profile path reads it. That is a latent trap if a later feature starts using it.
  - Ordering: red at 16:25:49 came before the runtime change at 16:29:56, and green followed at 16:30:46. The reconstructed pre-cache file differs from the current runtime by exactly the 3-line fix.
- **Typing:** The diff makes no change to `_profile_guard`'s primitive-only check (`:1247-1254`). Export runs only `admit_model` (`emit.py:30`), so "GND-valid declarations required" is an obligation on callers, not something the code enforces. A GND-invalid model can still be accepted with exit 0, and the spec should say so plainly. Nothing was silently added.
- **Provenance:**
  - Source and tool digests, plus the start/end comparison, are in place (`measure_pyrel_applications.py:174-176, 252-260`).
  - The negative control changes only the runtime file. The tool-changed branch has no control.
  - The start/end comparison cannot detect a change that is reverted before the end.
  - The program is rendered from `files("gnd.export")` in whatever `gnd` is installed (`emit.py:31`). That means `runtime_source_sha256` alone does not prove what executed; `program_sha256` plus re-rendering is the real binding, as you said.
  - Current digests: runtime `9ba8784e…`, tool `301d7a3a…`.
- **Computed-key check:** A missing key now fails (`:105-107`). Every one of the 40 derivation verdict refs in `answers.json` has an expected-derivations entry, so no derivation row can skip the computed check. The expected values come from claims plus missing minus extra. Fixtures, PA1 evidence, the plan and A1 have no diff.
- **Successors:** The PA2 query successor shows 359 occurrences and 304 for the original metric, chained from PA1. `pyrel-successor.json` was refreshed at 16:32:34, before the repaired focused run at 16:32:53. The evidence files record no commands, so I can't show which tests that 354-test run included.

## Evidence status

- Native direct 25 passed, focused 354 passed, provenance negative 1 passed and lint clean all have timestamps after the final runtime and tool bytes.
- `native-repaired.txt` had 112 of 137 lines, all `matches=True`, when I read it. It is **pending and not credited**.
- `native.json` (16:17:33) predates the repair and is historical only.
