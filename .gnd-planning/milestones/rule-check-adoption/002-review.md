---
milestone: rule-check-adoption
station: "plan-review-r3"
instrument: single reviewer, different tool (Codex)
scope: plan r3 and RC1 spec r3
date: 2026-11-06
gate:
  command: "codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort=\"xhigh\" --sandbox read-only --color never --skip-git-repo-check - < review-prompt.txt"
  exit: 0
  note: "codex-cli 0.163.0; run at e0bf31f5 with a clean tree (`git status --short` empty before and after); prompt on stdin; 135,060 tokens."
evidence:
  - path: .gnd-planning/milestones/rule-check-adoption/notes/rule-check-adoption-plan.md
    commit: e0bf31f5
    sha256: f00ffcf3b6d90637b945d1bdbc8160bb97f02894878ad85de48da19a52aea59e
  - path: .gnd-planning/milestones/rule-check-adoption/notes/phase-RC1-spec.md
    commit: e0bf31f5
    sha256: ba486fc9925fb7d30161005e3ed6262f5ebcf8c9c8530fff99a3bf1289ed27aa
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/plan-review-r3/review-prompt.txt
    sha256: b3aa6627cba0fbe0e24f83973d1067f1a82a85a49a8def7d7d2b83002a6316b8
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/plan-review-r3/codex-output.txt
    sha256: 4d51de09c6a95f0f6c338d510856c49c25169288ceba29e33cd705962bbd986d
---

# Claim

The owner ruled RC-D0 on 2026-11-06: "One reviewer on r3". One reviewer
(Codex, gpt-6-sol, xhigh, read-only sandbox) read plan r3 and RC1 spec r3
against the r2 panel's 22 fixes and returned `DISPOSITION: block` with 13
findings (4 high, 8 medium, 1 low). Every finding was reproduced by the
driving agent; none is rejected. The reviewer confirmed 15 fix dispositions
(F1, F3, F5-F9, F14-F16, F18-F22) and contested F2, F4, F10-F13 and F17.

The output is retained unedited in
[codex-output.txt](evidence/plan-review-r3/codex-output.txt); it contains no
local path. The prompt is [review-prompt.txt](evidence/plan-review-r3/review-prompt.txt).

## Reproduction

| Finding | Severity | Reproduced by | Result |
|---|---|---|---|
| R1 `allOf` over closed `verdict` cannot take new keys | high | `report.schema.json:1151-1165` `additionalProperties: false`; `verdict_v10` (line 532) is a separate closed object | confirmed |
| R2 reference-population models wrap the report as v12 | high | `checking_service._reference_wrap` (line 594), wrapper `schema_version` 12/14 (line 648); `report` `oneOf` admits only existing report defs (lines 85-93) | confirmed |
| R3 row-aligned `novelty` gives no verdict-level label | high | plan §2.3 text: row-less one-element list breaks the stated alignment | confirmed (reasoning) |
| R4 derivations have no place for novelty | high | `derivation_verdict` closed (`report.schema.json:991-1003`); RC1 M2 extends only `verdict_v15` | confirmed |
| R5 RC3 gate lacks the full suite | medium | plan §9 RC3 row and §6 first row omit RC3 | confirmed |
| R6 `tests/test_rc1_*.py` cannot run at the merge base | medium | no such file at e0bf31f5 | confirmed |
| R7 `band()` gives 4 for `reference-join-work-limit` regardless of modality | medium | `checker/_reports.py:159-163` | confirmed |
| R8 `iter_constraints()` deep-copies the fact type per constraint | medium | `model_index.py:279-285`: quadratic in constraints per fact type | confirmed |
| R9 RC5 note has no maximum or field | medium | plan RC5-C1, RC-D8 | confirmed |
| R10 text output renders `CheckReport`, not the payload | medium | `commands/checking.py:273-276` → `output._print_report` (`output.py:167`) | confirmed |
| R11 SCC caller migration is advisory | medium | plan RC-D10 wording | confirmed |
| R12 self-loop singleton not required in RC2-C1 | low | `graphlib` reports `{'a': ['a']}` as cycle `['a', 'a']`; today's checker flags it | confirmed |
| R13 no RC3 refusal criterion for `--baseline` | medium | plan RC3 criteria | confirmed |

## Boundary

One reviewer is one reviewer: this is not a panel and does not meet the
project's plan-review bar, which the owner waived for r3 by the RC-D0
ruling. The reviewer ran in a read-only sandbox and did not run tests; its
code claims were checked by reading, and the driving agent reproduced them
by reading code and one `graphlib` probe. Advisory only; no fix is applied
and r3 is unchanged. Repaired bytes (r4) will carry no review opinion.
