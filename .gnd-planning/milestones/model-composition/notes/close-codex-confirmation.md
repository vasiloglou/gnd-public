Retained independent Codex CLI narrow confirmation; operator/repository paths sanitized and trailing Markdown spaces removed. Other wording unchanged.

**APPROVE — conditional local close readiness at `86ad71f138bb85d681ec00984530769a9b67a58a`.** No unresolved findings within the two-finding repair scope.

1. **Finding 1 resolved in both actual adapters.** [Witness service](<REPO>/src/gnd/witness/service.py:164) now forwards only `include:*` reasons and otherwise returns `3/input-invalid`. Fresh probes reproduced the pre-fix `semantic:cross-ref`, confirmed baseline `459ca8d2` bodies return `input-invalid`, and passed both corrected adapters. Canonical records bind actual model/population bytes; certificate validation remained real. Only record storage was supplied in memory. Included controls retain `include:unsupported-route` before dependency reads. The rejected hash-mismatch oracle remains documented.

2. **Finding 2 resolved.** The [anchored guard](<REPO>/tests/test_model_v2.py:345) binds `proposal.candidate_model` as the first call argument. Both wrong-argument controls incorrectly pass the old guard and are rejected by the corrected guard. Existing ordering assertions remain, whitespace variation passes, and runtime candidate binding is unchanged. No production parser or helper was added.

Executed read-only checks verified:

- Seven current direct controls, baseline/pre-fix adapter comparisons, and both dirty-guard comparisons.
- **46 evidence bindings**, five source bindings, and the repair gate’s current hash/original prefix.
- All **4,698 nonplanning paths, bytes and modes** equal measured `b7da04b1`; tracked working status is empty.
- MC2 **110/375 source, 585/600 tests**; MC3 **1109/1400 source, 1239/1400 tests**; MC4 **120/120 unchanged**. Combined support is **163 = 120 + 22 + 21**, with four production additions separate.
- Fresh uncached lint reproduces exactly **13 retained positions**. Bound outputs retain **466 passes/11 deselections** and **125 source/architecture passes**.

The corrected retained full result is **exit 1: 6 failed, 18,801 passed, 801 deselected, one warning, 2545.10s**—exactly the six frozen failure identities. Census artifact hashes, all **400 original observations**, **23 dispositioned additions**, and the **2-pass/15.80s** result check out. This remains a known-red comparison.

Unfiltered reference traversal encountered an ignored nested worktree. Traversal over every tracked Markdown file and the actual twin/mode checks passed; this is a local workspace limitation.

Verified local `origin/main`/recorded main `a9b67d8b` remains nine files behind the corrected candidate. Its 229-pass smoke is pre-repair. Fixed-head PR158 merge, final main equality and issue95 closure remain pending separate authority. Later ruling/record metadata is outside these reviewed bytes.

No broad suites were rerun; no network, credential files, subagents, changes or merge were used. **One reviewer; close-call budget 2/2 consumed.**
