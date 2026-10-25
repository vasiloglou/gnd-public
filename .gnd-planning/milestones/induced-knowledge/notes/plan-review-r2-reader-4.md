# Confirmation reader 4 — measurability, falsifiability and reproducibility

Plan r2 SHA-256 `d1a40a89…7c85` and IK1 spec r2 SHA-256 `4f4cb8b5…3cac1` — both
match at `b554f3f`.

**Verdict: approve-with-fixes.** All five round-1 blockers in this lens are
resolved at plan level; two r2-introduced defects (C4-F1, C4-F2) are cheap text
fixes.

IK-R12 judgement: acceptable. IK-R12 (L101) enumerates every bound R4-F4 named,
requires each fixed before implementation, and requires an owner-recorded
amendment with arithmetic for any later move. That closes the post-hoc-threshold
risk at plan level.

## Round-1 findings

| Finding | Status | Citation |
|---|---|---|
| R4-F1 (B) | resolved | plan L56–58, IK4-C1 L329: per-ref `pass`, support > 0, vacuous never emitted (L235), seeded wrong-discoverer test |
| R4-F2 (B) | resolved, minor residual | two label modes (L204–222); class-mode cells named but per-cell denominators (e.g. vacuous excluded?) undefined |
| R4-F3 | resolved | L116, L225; IK3-C2 L323 parity test |
| R4-F4 (B) | resolved | IK-R12 L101; work counters in IK3-C4, IK4-C4 |
| R4-F5 (B) | resolved | L246–247; IK-R2 L91; brute-force oracle IK4-C3 L331; discovery "confidence" dropped |
| R4-F6 | resolved | IK5-C1, C3–C4 (L337–340); L271 "necessary, not sufficient" |
| R4-F7 (B) | resolved, see C4-F1/C4-F3 | spec T7 L178; all four fixtures exist under tests/fixtures/models/; `evolution-safe-additive` exists (evolution.json L6) |
| R4-F8 | resolved | T7 covers projection, self-diff, evolve preview, seeded `annotations: []` negative |
| R4-F9 | resolved | T2 L173 1/512 discriminators; T5 512 case; T1 L172 no-op |
| R4-F10 | partial | IK2-C3, IK4-C5, IK6-C1 now have goldens/counts; IK6-C2 "checked by the existing skill sync tests" (L345) — those check twin identity, not a census table |

IK1 tests discriminate: T1, T2, T3, T7, T8, T10, T11, T12. T6's `audit_allowlist`
half passes on a no-op (only line presence discriminates). Mapping: T12 (RF1 diff
anchor) is mapped to C5 but belongs to C3; C5's "references updated" maps to
"reference diffs in the review", not a test.

## New findings

- **C4-F1** (blocking, high; r2-introduced: yes). T7 pins `a22ccde` digests and
  forbids regeneration (spec L150–154; plan L40, L92, L310), but IK1-D4 proposes
  merging PR #35 first (spec L166). #35's `9137bd7` changes
  `model_verbalization._constraint_cnl` for value constraints (reads `allowed`,
  adds role scope); `full_vocabulary.orm.yaml` has an `allowed` enum (L357–359) and
  a `role_ref` value constraint (L376–379); `library.orm.yaml` has value
  constraints too. T7 fails on a correct IK1, and the only way through is a
  post-measurement re-pin, which IK-R12 and the spec forbid. Reproduce:
  `git show 9137bd7 -- src/gnd/model_verbalization.py`; grep `allowed` in the
  fixture. Fix: pin at IK1's actual base (spec-gate commit after #35) or record
  #35's delta explicitly.
- **C4-F2** (hardening, medium; r2-introduced: yes). "512 equals the cap, so
  `_neutralize` never elides" (spec L81–82; plan L156–157, L460) is false:
  `_neutralize` escapes `\`, `'` and controls *before* the 512 cap (verbalize.py
  L37–60). A valid ≤512-char description with apostrophes or newlines renders
  truncated with "… (+N more characters)", violating IK1-C2; T3 (plain 512) does
  not detect it and T5 checks only delimiters. Reproduce: `_neutralize("'"*300)`
  exceeds 512 and elides. Fix: bound the escaped length, render outside the cap,
  or extend T3 to escapable input.
- **C4-F3** (completeness, medium; r2-introduced: yes). T7 and the baseline capture
  name outputs, not commands. "The pinned commands" (spec L151) are never listed;
  the codegen tree manifest and conformance payload need a generated project and
  flags, and the payload embeds `gnd_version` from `resolve_version()`; evolve
  preview needs a proposal and workspace, and which bytes are hashed is unstated.
  Two implementers would pin different digests. Fix: exact argv, hashed artefact
  and normalization for each of the seven outputs.
- **C4-F4** (completeness, low; r2-introduced: yes). The criterion↔test table maps
  T12 to C5 and satisfies C5's reference updates with "reference diffs in the
  review" (spec L193), so "every criterion maps to tests" is false for C5's docs
  clause. Remap T12 to C3; add a docs check or mark that clause review-only.

Counts: 4 new findings, all r2-introduced (1 blocking).

## Limits

Static reading; no tests or CLIs run; PR #35 inspected through local commits
`9137bd7`/`c792f2c`; host-path content of conformance/evolve outputs unverified;
IK2–IK6 criteria checked at plan level only.
