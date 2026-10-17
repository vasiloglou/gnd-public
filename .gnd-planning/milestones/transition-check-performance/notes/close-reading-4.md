# Milestone close review, reader 4 of 4: are the performance claims true?

- Milestone: `transition-check-performance` (issue #24)
- Subject: `origin/main` at `2689ab3` (merge of PR #30), scratch detached checkout
- Comparison base: `369f161` (TP0 commit; the runtime code is unchanged from before the milestone)
- Lens: are the performance claims true, honestly stated, and reproducible on main?
- Environment: arm64 Darwin, CPython 3.14.3 (the interpreter the evidence used), `uv run`.
  A full test suite ran at the same time in another checkout. Absolute times are inflated about
  2 to 3 times, so I rely on counters, function-call counts and interleaved ratios.
- One reader is one reader.

## Reproduced numbers

### 1. Counters and digest parity (deterministic)

Command, from the main checkout:
`uv run python tools/measure_transition_cost.py --out <scratch>/r4-out --repeat 3`

| Check | Result |
|---|---|
| `digests.json` vs `evidence/TP0/digests.json` | **identical** (`diff` of the sorted JSON is empty) |
| `digests.json` vs `evidence/TP3/digests.json` | identical |
| `counters.json` vs `evidence/TP3/counters.json` | identical, every workload and surface |
| reporter replay: `checker_runs` | 25 (TP0 25) |
| reporter replay: `model_index_key_paths` | **26** (TP0 540) |
| reporter replay: `model_dumps_other` | 457 (TP0 457, so no increase) |
| reporter replay: `deepcopy_nodes` | **115,294** (TP0 2,760,394; −95.8%, meets the ≤1,380,197 bound) |
| course control | 5 checker runs; `attempt-3` exits 0 |

Command: a scratch script that calls `replay('reporter')` and `replay('reporter-receipts')`,
does one warm-up run, then one run under `counting()`.

| Counter | reporter | reporter-receipts | committed `receipt_replay.json` (receipts) |
|---|---|---|---|
| `checker_runs` | 25 | **19** | 19 |
| `model_index_key_paths` | 26 | 26 | 26 |
| `deepcopy_nodes` | 115,294 | 105,196 | 105,196 |
| `model_dumps_other` | 457 | 422 | 422 |
| `model_index_calls` | 540 | **482** | **475** (see finding H1) |

All 13 payloads are identical with and without receipts. They also equal the committed
`receipt_replay.json` `payload_digests`.

### 2. Wall time, cross-version interleaved A/B

Each sample is a fresh process: one warm-up replay, then the faster of 2 timed replays. The
order rotates TP0 (`369f161`), main default, main with receipts, three rounds, so drift in machine
load hits all three arms about equally.

| Round | TP0 (s) | main default (s) | main + receipts (s) | default vs TP0 | receipts vs TP0 |
|---|---|---|---|---|---|
| 1 | 9.66 | 6.61 | 5.59 | −31.5% | −42.2% |
| 2 | 8.10 | 4.74 | 4.30 | −41.5% | −46.8% |
| 3 | 7.47 | 5.03 | 4.58 | −32.7% | −38.7% |
| median | | | | **−32.7%** | **−42.2%** |

The same tool's `timings.json` gave a reporter median of 6.92 s on main today. The committed TP3
figure is 2.55 s and TP0 is 5.09 s. Medians from separate sessions are not comparable: drift here
is about 2.7 times, much larger than the 20% the plan anticipated.

### 3. Load-independent proxy: profiled function calls (cProfile, one warm replay)

| Arm | Function calls | Profiled time | `extensions.prepared` cumulative |
|---|---|---|---|
| TP0, reporter | 80.46 M | 21.08 s | 5.03 s (24%) |
| main, reporter | 38.72 M (−52%) | 12.26 s | 5.18 s (42%) |
| main, reporter-receipts | 33.58 M (−58%) | 11.56 s | 4.93 s (43%) |

On main, the extension calculation (`extensions.prepared`, `extension_preparation.calculate`,
`freeze` with 1.1 to 1.4 M recursive calls) costs about as much in absolute terms as it did at
TP0. It is now the dominant remaining cost. The milestone did not touch it; the plan defers it
as TP4/TP-D4. `freeze` is not counted by `deepcopy_nodes`. The 96% deep-copy reduction therefore
does not mean that copying-like tree walks are gone.

### 4. Claim assessment

- **Counters: true and reproducible.** 25 → 19 checker runs with receipts, 540 → 26 key paths,
  2.76 M → 115 k deep-copied nodes. Every TP0 parity digest is unchanged on main.
- **"About 40% less GND time": true only with receipts.** My cross-version A/B gives about
  −42% with receipts and about −33% on the default path. The phase A/Bs chain to the same
  result: TP1 0.701 × TP2 0.916 = 0.642, so −36% by default; × TP3 0.90 = 0.578, so −42% with
  receipts. Both are within the plan's ceiling of about −44% (−38% for TP1 + TP2). A
  "~40%" headline with no qualifier overstates the default path by about 5 to 8 points.
- **Limits stated so far:** TP1 records the session drift. Each phase reports its in-process
  A/B method. TP3 says wall time is evidence only. No record yet rolls the results up against
  the 44% ceiling (completion predicate 6), separates the default path from the receipt path, or
  says that extension work is now the dominant remaining cost.

## Findings

| ID | Class | Severity | Finding | Evidence | Required action |
|---|---|---|---|---|---|
| C1 | completeness | medium | Completion predicate 6 ("wall-time results are reported against the about-44% ceiling, with their limits") is not yet met. TP2 compares against −38% for TP1 + TP2. TP3 gives only its own −10%. No overall roll-up exists anywhere on main. | `004-phase-TP2.md:50`, `005-phase-TP3.md` Measurements; no other match for "ceiling" or "44%" in records 002–005 | The close record must state an overall roll-up: default path about −33 to −36%, with receipts about −40 to −42%, against the about −44% ceiling. It must also name the method and its limits (next row). |
| C2 | completeness | medium | Nothing yet says that, after the milestone, the extension calculation is the largest remaining cost, now about 42% of profiled replay time and unchanged in absolute terms. Nothing says GND will still dominate the reporter's step time. | Section 3 profile; plan Problem ("extension re-derivation is then the largest remaining cost") | Close record and carryover: name the TP4/TP-D4 successor as the next lever and include the profile share. |
| H1 | hardening | low | `evidence/TP3/receipt_replay.json` predates fix `cea184c`. That fix added one `ModelIndex.for_model` call per `check_with_receipt`, so main reproduces `model_index_calls` 482, not the committed 475. The gated counters (`checker_runs` 19, `model_index_key_paths` 26) are unaffected. The committed evidence describes the earlier bytes. | `git diff a33334a cea184c -- src/gnd/api.py`; section 1 table | Regenerate `receipt_replay.json` on main bytes in the close evidence, or add a note on what changed and why. |
| H2 | hardening | low | TP2 says "TP1 and TP2 together, measured in-process: about −35%". Neither script measured that pair in one process: it chains `ab_scope` no_scope (4.01 s) with `ab_shared` shared (2.59 s) from two runs. The `ab_shared` copying stand-in also only re-copies `fact_types`. The number is right (chained ratios give −35.8%; my cross-version A/B gives −33%), but the label "measured in-process" is wrong. | `evidence/TP1/ab_scope.py`, `evidence/TP2/ab_shared.py`, `004-phase-TP2.md:49-50` | Close record: say "chained from per-phase in-process A/Bs". Cite the cross-version interleaved A/B as the end-to-end check. |
| H3 | hardening | low | Wall time from separate sessions drifts far more than the plan's 20% (2.55 s committed vs 6.92 s today for identical bytes). The tool's `timings.json` has no A/B mode, so a successor milestone cannot reproduce end-to-end gains without hand scripts. | section 2 | Carryover (optional): add an interleaved base-vs-head option to `tools/measure_transition_cost.py`, or commit the cross-version script with the close evidence. |
| C3 | completeness | low | All 13 reporter calls return `inadequate` (exit 2; batch `inadequate: 7`). That is faithful: `import.json` `equal: true`. Gains measured on an inadequate-outcome workload may not carry over once the reporter's model reaches accepted outcomes and evaluates more. The control (`attempt-3`, exit 0) also improved, but it is tiny. | `evidence/TP0/digests.json` `cli.batch.summary`; `import.json` | One sentence in the close record and in the issue reply. |
| C4 | completeness | info | The release notes mention only `check_with_receipt`, not the default-path reduction from TP1 and TP2. | `docs/release-notes.md` diff | Optional: one release-note line with the counter-backed claim. |
| C5 | completeness | info | `README.md` still says "Plan … not approved" and "First phase spec … awaiting owner review", which contradicts its own "Done" line. | milestone `README.md` lines 6–9 | Fix in the close commit. |

No blocking findings. Every gated claim reproduced exactly on main.

## What the close record and the reply to the reporter should say

Suggested close-record wording:

> On the reporter's 13-call replay, counted work fell as follows. ModelIndex key computations went
> from 540 to 26. Deep-copied nodes went from 2.76 M to 115 k. With the opt-in receipts, checker
> runs went from 25 to 19. Every TP0 parity digest is unchanged. Wall time, compared in interleaved
> runs (not across sessions, which drift up to about 2.7 times): about −33% on the default path and
> about −42% with `check_with_receipt` / `pre_receipt`, against the planned ceiling of about −44%.
> Wall time was never a gate. The extension calculation is now the largest remaining cost, about
> 40% of the replay, and is deferred to the TP4 successor.

Suggested gist of the reply to the issue reporter (no promises beyond the measurement):

- If you upgrade with no code changes, expect GND time per step on your bundle to fall by about
  a third (roughly 1.5 times faster).
- If you mint the pre-state with `api.check_with_receipt` and pass `pre_receipt=` to the next
  `api.transition`, expect about 40% (roughly 1.7 times faster). Receipts are in-process only and
  work with default options only. Intermediate and post checks still run.
- GND will still dominate your step wall time, because SQL takes about 1 ms per step. The rest
  of the cost is the extension calculation, which a successor milestone targets.
- Figures come from your anonymized bundle as captured, where every check is `inadequate`. Your
  gains may differ as your model or populations change. Results are byte-identical.

## Verdict

**close-with-carryovers**

Before close, fix C1, C2 and H1–H2 in the close record and evidence. Carry over the TP4
extension-calculation milestone, and optionally H3 (an A/B mode in the measurement tool).
