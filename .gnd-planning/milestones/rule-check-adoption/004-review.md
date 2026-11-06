---
milestone: rule-check-adoption
station: "plan-review-r5"
instrument: single reviewer, different tool (Codex), re-check of the r4 findings
scope: plan r5 and RC1 spec r5, scoped to the r4 -> r5 diff
date: 2026-11-06
gate:
  command: "codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort=\"xhigh\" --sandbox read-only --color never --skip-git-repo-check - < review-prompt.txt"
  exit: 0
  note: "codex-cli 0.163.0; run at 2a2625a7 with a clean tree (`git status --short` empty before and after); prompt on stdin; 148,158 tokens."
evidence:
  - path: .gnd-planning/milestones/rule-check-adoption/notes/rule-check-adoption-plan.md
    commit: 2a2625a7
    sha256: e8a3a1548e38cf112b3ea5b84e9fa28e4a8692750f43ca7cf3dd3223c9e50a31
  - path: .gnd-planning/milestones/rule-check-adoption/notes/phase-RC1-spec.md
    commit: 2a2625a7
    sha256: a068f4e59dab2002f00d67085e0ce9149ccc82f45bf35f2e3b09338022b2f5fc
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/plan-review-r5/review-prompt.txt
    sha256: 36334383a0a15d55118673aaa6e6b885f7d5ec282de4b99535a5f12c51062bbf
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/plan-review-r5/codex-output.txt
    sha256: bbc3f603f532066c6b67a3602cf4a00fd5bff140bd404d2e7818a553225979f9
---

# Claim

The owner ruled RC-D15 on 2026-11-06: "Codex re-check r5". The same
reviewer profile re-checked r5 against S1-S4 and the r4 -> r5 diff. It
returned `DISPOSITION: block` with 2 findings (1 high, 1 low) and confirmed
S1, S3 and S4 resolved and S2's conditional rules preserved. Both findings
were reproduced; neither is rejected.

The output is retained unedited in
[codex-output.txt](evidence/plan-review-r5/codex-output.txt); it contains no
local path. The prompt is [review-prompt.txt](evidence/plan-review-r5/review-prompt.txt).

## Reproduction

| Finding | Severity | Reproduced by | Result |
|---|---|---|---|
| T1 v15 derivations typed as `derivation_verdict` alone reject exact-arithmetic reasons such as `term:mod-zero` | high | `derivation_verdict.reason_code` (`report.schema.json:1035-1041`) admits three reasons; `extensions.py:2628-2649` can emit `term:*` reasons; the existing report branch types `derivations` as `anyOf` `derivation_verdict` / `derivation_verdict_v10` / null (`report.schema.json:2316-2334`), and `derivation_verdict_v10` admits the `term:*` reasons | confirmed |
| T2 plan §8 says "r4 is unreviewed"; spec §1 says "Draft r4" | low | plan line 514; spec line 5 | confirmed |

Driving agent's addition while reproducing T1: the r5 plan's claim that
version-15 derivations are "unchanged from version 7" is correct only if
version 15 reuses the existing branch's whole `derivations` `anyOf`, not
`derivation_verdict` alone. The verdict side is unaffected: on the plain
snapshot path verdicts use `verdict` (value rows); `verdict_v10` is the
admission shape, and admission is excluded from `--rule-ids`.

## Boundary

One reviewer is one reviewer; this is not a panel and does not meet the
project's plan-review bar, which the owner set aside for r3 to r5 by the
RC-D0, RC-D14 and RC-D15 rulings. The reviewer did not run tests; its code
claims were checked by reading. Advisory only; no fix is applied and r5 is
unchanged.
