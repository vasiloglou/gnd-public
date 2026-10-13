# Phase12 Astra/high round2

Retained reviewer response; edited only to sanitize absolute paths.

**ROUND2: no new demonstrated blocking or hardening defect.** The two R1 repairs are supported by source inspection and retained evidence, with one requested coverage limitation below.

- **Aggregate allocation guard repaired.** [population_shape.py:22](<GND_WORKTREE>/src/gnd/population_shape.py:22) charges container punctuation, every key/string occurrence, integers, floats, booleans and null before serialization. Strings allow 12 ASCII bytes per character; integers use `bit_length()` without string conversion; 32 bytes conservatively covers finite floats. Over-budget input falls back, and core errors remain contained.
- **R1 condition/enum controls are now unmasked.** [Tests:211](<GND_WORKTREE>/tests/test_m3_population_shape.py:211) exercise integral `2.0`, then/else selection, missing properties, Boolean/integer inequality, and standalone `{"enum":[1]}` rejecting `True`. Each retained targeted mutant produces its intended assertion failure.
- **Compatibility remains intact by inspection.** Intersections and conditions receive the original input; core outputs are discarded. Bundled schemas are unchanged and byte-identical. Absent/version-1 scalar facts, version-2 opaque facts, scalar-only instances, content-sensitive cache bounded at eight, unsupported-schema fallback, loader/Draft patch seams, and exact ordered diagnostics remain. Parsing, layer 2, markers and public API are unchanged. Layer allowances remain zero; no population/evaluator cache was added.

**Coverage limitation:** the unmasked condition tests contain no fractional float such as `2.5`. For `conditional_schema(2)`, the requested distinguishing inputs would be `{"v":2.5,"p":7}` → accept and `{"v":2.5,"p":"then"}` → reject. Current source compares the original numeric value directly and supports those outcomes, but no retained test proves them. This is an unverified coverage claim, not a reproduced runtime defect or grounds for another completeness-only review round.

The retained evidence reports:

- Original RED: **45 failed, 2 passed**, committed in `3235814` before runtime implementation.
- Actual R1 aggregate RED: **4 failures** against retained runtime whose SHA-256 matches `dda4de8…`.
- Numeric-condition, Boolean-condition and enum mutants: **one intended failure each**.
- Current shape/focused checks: **66 passed / 214 passed**; runtime lint passed.

The earlier author-hardening receipt concerns an explicitly **reconstructed pre-hardening implementation**, not retained original historical bytes. The [command/provenance record](<GND_WORKTREE>/.gnd-planning/milestones/analytics-m3-repairs/evidence/phase-12-implementation-commands.txt) distinguishes it from actual R1 evidence.

Reviewed accelerator SHA-256: `ec8e028f1ec23d668a0c5412701f7e14eec539d65cc4a472212a07e196d822bf`.

I ran no tests or mutants, changed no files, and accessed no credentials, environment files or providers. Fresh current-byte native 3+3 load/root and app90 acceptance remain unverified; pre-review timings concern earlier bytes. All-cap8/109-development agreement and successful 29-heldout median ≤15s remain unmet.

One reviewer is one reviewer. The two-round review bound is exhausted; this review grants no source merge or milestone closure authority.
