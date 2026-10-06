Retained reviewer output edited only to replace absolute machine paths with <worktree> / <home>.

## RF5 initial adversarial review

I reviewed `29915d9..d8dd49d` and reproduced **two hardening findings in the new entrypoint gate**. I found no reproduced behavior regression in the current production diff.

1. **A command can import another lane’s service without an exception.** In [gnd_arch.py](<worktree>/tools/gnd_arch.py:802), all 13 service targets are allowed for every command group. I injected an in-memory edge from `gnd.commands.verify` to `gnd.synth.service`; `entrypoint_rule()` returned `violations: []`, although no source/target exception authorizes that edge. This refutes the lane-specific boundary asserted in claim 4 and weakens RF5-C2’s negative gate. The current measured graph has no such edge. The policy also contains an unused `gnd.commands.exp → gnd.solve` exception at [gnd_entrypoints.json](<worktree>/tools/gnd_entrypoints.json:209), which could authorize that edge later without a new review.

2. **`measure()` can silently omit the entrypoint check when `commands.checking` is missing.** The conditional at [gnd_arch.py](<worktree>/tools/gnd_arch.py:765) skips the rule in that case. In a read-only, in-memory fault injection that removed `gnd.commands.checking` from discovery and the corresponding map entry, `measure()` returned metrics for 212 modules with **no `entrypoints` field and no error**. This refutes claim 4’s missing-group rejection through the measurement path. The direct negative controls in [test_rf5_commands.py](<worktree>/tests/test_rf5_commands.py:111) call `entrypoint_rule()` and do not exercise this skip.

Both findings concern the phase’s own verification instrument, so they warrant repair and a negative control before the RF5 record. This is the initial review; the approved workflow permits at most one repair re-review.

## Claims checked and held

- **Moves and compatibility:** The predecessor snapshot exactly matches `29915d9:src/gnd/cli.py`. Its 116 definitions match the ASTs in their planned homes; the catalogue also contains 18 constants. Static checks found every catalogue name re-exported from its planned home, every moved definition stamped `gnd.cli`, and all 56 predecessor import bindings retained. The retained tests cover runtime alias and class pickle identity; I did not rerun them.
- **Routing and source scope:** [cli.py](<worktree>/src/gnd/cli.py:623) parses once and calls `args.handler(args)`. The source scope includes all 34 introduced production modules. The retained direct and successor gates report the 52 parser paths and 43 handler observations.
- **Frozen inputs and adaptations:** All 434 listed frozen input hashes match. The successor case and answer hashes match their freeze record. Comparing the 167 RF1 mutation rows as parsed JSON found exactly 28 changed `file` fields and no changed stimuli or expected reds. The 46 added or adapted curated manifest rows match current file hashes; the source-owned ledger and distribution test are unchanged.
- **Present architecture and budgets:** The retained current metrics show 213 mapped modules, 19 entrypoint modules, zero recorded entrypoint violations, zero wrong-way edges and allowances, and only the RF8 session SCC. Private imports rise from 124 to 319 as disclosed. `cli.py` is 667 lines; the recorded source comparison yields 8,141 moved and 2,023 added nonrelocated production lines, within the approved limits.
- **Gate evidence:** I inspected the retained G1, routing-impact, G2, repaired G4, G5 and lint outputs, as well as the initial doctor failures and the frozen-base P2-054/055/056 instrument failures. They support the reported selected-run counts and repairs, subject to the verification limits below.

**Verification limit:** This was one reviewer, not a panel. I used read-only diff inspection and bounded Python/AST fault injections; I did not run pytest, invoke native or provider functionality, or establish remote CI or installed acceptance. No repository files were changed, and the RF5 completion record remains pending.
