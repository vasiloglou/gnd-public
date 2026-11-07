# Phase RC4: vacuous acceptance (`--allow-vacuous`)

## 1. Status

**r1, 2026-11-06. Draft, awaiting the owner gate (process-phase step 2).**
No implementation file is created or edited before the owner approves this
spec or its corpus (§11). `auto=false`.

## 2. Provenance

- Plan: [rule-check-adoption-plan.md](rule-check-adoption-plan.md) r6,
  sha256 `6f0056b31b8df7eae5c85d6d32eb09395a8240bc137a7300de85bab71639f138`,
  approved with every §10 proposal ([005-plan.md](../005-plan.md)); RC-D7
  (a run-wide flag, no per-constraint control) is ruled.
- RC1 fixed `allow_vacuous` (boolean) in the version-15 shape; RC3 gave
  `band()` its optional baseline argument and the uncertified assurance
  route. Records: [006](../006-phase-RC1.md), [007](../007-phase-RC2.md),
  [008](../008-phase-RC3.md). Base: main at `4713fc8a`.

## 3. Obligations (step 0 harvest)

| Source | Obligation | Discharged by |
|---|---|---|
| plan §4 RC4-C1 | a vacuous-only run exits 0 with the option, 2 without | corpus `vacuous-only`, `vacuous-only-plain` |
| RC4-C2 | a fail or an alethic unchecked verdict still decides the band | corpus `fail-and-vacuous` (1), `unchecked-and-vacuous` (4) |
| RC4-C3 | `allow_vacuous: true` in version 15; vacuous verdicts still listed; the option implies `--rule-ids`; no existing variant's bytes change | every corpus golden; V3 |
| RC4-C4 | with `--baseline`: head vacuous (2, or 0 with the option); base vacuous contributes no rows; base fail with head vacuous resolves the rows (2, or 0 with the option) | corpus `baseline-head-vacuous`, `baseline-base-vacuous`; RC3's `head-vacuous` (2) unchanged |
| plan §2.4 | run-wide; verdicts and counts unchanged; recorded in version 15 only | M1-M3 |
| plan §0 rule 3 | the flag is validated with the other arguments (64) | T2 |
| plan §0 rule 5 / §6 | RC4 extends `band()`, the one implementation, after RC3 | M1 |
| plan §0 rule 7 | no existing variant moves; full suite vs base | V3 |
| plan §0 rule 8 | stop rule at 1.5 times about 60 source, 200 test lines | §10 |
| RC3 F2 / D5 | a band that differs from the plain band is not certified | M2 |
| AGENTS.md, RC1-RC3 | guard registries record changed bodies; CLI help successor; component index updated | V4, V6 |

## 4. Standing rules bound to this phase

- **Validation order (3).** `--allow-vacuous` joins `--rule-ids`'s conflict
  set: exit 64 before the model is read.
- **One band (5).** `band()` gains `allow_vacuous`; no caller decides a band.
- **Frozen variants (7).** The flag implies `--rule-ids`, so every effect is
  in version 15.

## 5. Goal

`gnd check ... --allow-vacuous` exits 0 when the only shortfall is vacuous
verdicts, still lists them, and records `allow_vacuous: true`, so a CI gate
can ship a rule before the data it will judge.

## 6. Design

**Reuse table** (searched 2026-11-06 at `4713fc8a`: `components_index.py
search` for `vacuous`, `exit band`).

| Capability | Found | Decision |
|---|---|---|
| exit band | `band(report, baseline=None)` (`checker/_reports.py`) | **adapt**: `allow_vacuous` |
| vacuous predicate | `CheckReport.has_vacuous` | **reuse** |
| uncertified assurance for a band the plain check does not give | RC3's `--baseline` route in `_run_check_raw` | **reuse** |
| the version-15 key | `payload["allow_vacuous"] = False` (`payloads.py`, RC1) | **adapt**: set from the flag |

**M1. `band(report, baseline=None, allow_vacuous=False)`, ~4 lines.** After
the existing computation (either route), a band of 2 becomes 0 when
`allow_vacuous`. Since the precedence is 1 > 4 > 2 > 0, band 2 means vacuous
verdicts are the only shortfall, so RC4-C2 holds by construction. Without
the argument, unchanged.

**M2. Service, ~12 lines.** `_run_check_raw(..., allow_vacuous=False)`
implies `rule_ids`; passes the flag to `band()` (with or without a
baseline) and to the payload. When the flag turned a 2 into a 0, the
assurance block is the uncertified one for band 0 (as RC3's D5), since the
certified path attests the plain decision.

**M3. Payload, ~3 lines.** `allow_vacuous: true` when the flag is given,
whatever the band; `exit_code`, `outcome`, `acceptance_ready` follow the
band.

**M4. CLI and text, ~12 lines.** `--allow-vacuous` (implies `--rule-ids`,
joins the conflict set). Text (D3): when the flag is given, one closing line
`vacuous accepted: N rules have nothing to judge yet (--allow-vacuous).`
with N the vacuous count, printed only when N > 0.

## 7. Decisions (owner rules at step 2)

| D | Question | Proposal |
|---|---|---|
| D1 | Approval instrument | **corpus-first** (an exit-code contract) |
| D2 | Assurance when the flag changed the band | uncertified block for band 0, level `none` (RC3 D5's rule) |
| D3 | Text output | one closing line naming the vacuous count and the option, only when the option is given and a verdict is vacuous |
| D4 | Review over the spec bytes | none |

## 8. Tests and verification ledger

**Corpus** (`tests/fixtures/rc4-allow-vacuous/`, §11) plus
`tests/test_rc4_allow_vacuous.py`:

| T | Case | Expected |
|---|---|---|
| T1 | `band()` truth table: every combination of fail / alethic unchecked / vacuous / clean, with and without the flag, with and without a baseline | 2 → 0 only; every other band unchanged |
| T2 | `--allow-vacuous` with each other arm | exit 64 before the model is read |
| T3 | the flag on a run with no vacuous verdict | same bytes as `--rule-ids` except `allow_vacuous: true` |

**Verification-selection ledger.**

| # | Obligation | Disposition | Command or evidence | Invalidation |
|---|---|---|---|---|
| V1 | merge-base record | run before any source edit | focused list at `4713fc8a`; full-suite base from RC3's record (main eac81cf8) unless main moved in tested code | a new base |
| V2 | plan §9 RC4 row | run | `uv run pytest -q tests/test_rc4_allow_vacuous.py tests/test_rc3_baseline.py tests/test_rc1_rule_ids.py tests/test_exp_bands.py --tb=short -p no:cacheprovider` | any RC4 edit |
| V3 | full suite vs base | run, sharded on beast-3 as in RC3 | failure set equal to the base's | any source edit after the run |
| V4 | impact closure | run | RC3's V4 file list (guards, every `band(` caller) | edits to those surfaces |
| V5 | lint | run | changed Python files clean | any Python edit |
| V6 | component index | run at record time | `components_index.py changed --base 4713fc8a --strict` | any edit |
| V7 | broad lanes | cadence: not run | milestone close if selected | owner request |

## 9. Out of scope for this phase

Per-constraint vacuous control (RC-D7); the population source (RC5);
documentation (RC6); vacuous acceptance outside version 15.

## 10. Size

Plan estimate: about 60 source and 200 test lines; rule 8 pauses past 90
source or 300 test lines. This design: about 35 source lines and about 150
test lines plus the corpus.

## 11. Approval instrument

Proposed (D1): **corpus-first** at `tests/fixtures/rc4-allow-vacuous/`,
reusing RC3's model (`models/graph.orm.yaml`, copied) and landing red before
code:

- `vacuous-only`: no areas recorded, so the legacy rule is vacuous;
  everything else passes → exit 0 with the flag, `allow_vacuous: true`, the
  vacuous verdict still listed;
- `vacuous-only-plain`: the same with `--rule-ids` and no flag → exit 2,
  `allow_vacuous: false`;
- `fail-and-vacuous`: plus a loop → exit 1 with the flag;
- `unchecked-and-vacuous`: plus an unreadable value under an alethic rule
  → exit 4 with the flag;
- `baseline-head-vacuous`: RC3's `head-vacuous` pair with the flag → exit 0,
  base rows resolved;
- `baseline-base-vacuous`: base vacuous, head clean → exit 0, no rows from
  base;
- `text-vacuous-only` (text): the closing line;
- `conflict-populations`: exit 64.

## Implementability sweep (step 1, author inspection)

- Every criterion has a case that can fail (§3).
- `band()`'s precedence makes "2 → 0" exactly "vacuous is the only
  shortfall"; T1 checks the full table.
- No new dependency, key or report version.
