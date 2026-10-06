# Initial native RF9 repair review

Edited retained evidence: absolute worktree/home prefixes sanitized; remaining final assessment retained verbatim. Reviewed commit ef0fe9f09edf5c170e5103b926a0539fa4be97a4, read-only native Codex gpt-6-sol/xhigh, exit0. One reviewer is one reviewer.

**Assessment:** I found two actionable issues, neither a demonstrated false acceptance by the work gate.

| Class | Finding |
|---|---|
| **Hardening** | [session_replay.py:488](<worktree>/src/gnd/exp/session_replay.py:488) checks the feedback and evaluation only when the terminal result says `accepted`. From the code, changing an honestly accepted result to a valid nonaccepted disposition while keeping its count and identities would let terminal reconstruction succeed and publish caches despite disagreement with final operator feedback. The work close gate would refuse that result. This is a static inference; I did not run the mutation. Check acceptance in both directions and add a negative control. |
| **Completeness** | [gates.json:38](<worktree>/.gnd-planning/milestones/code-refactoring/evidence/RF9-repair/gates.json:38) records `git diff --check` as passing. That command checks the working-tree diff; the requested base-to-implementation diff exits **2** on trailing whitespace in retained logs, including [red.txt:94](<worktree>/.gnd-planning/milestones/code-refactoring/evidence/RF9-repair/red.txt:94). Correct or qualify the whitespace gate claim. |

**Supported within this review:** I independently confirmed the expanded RF6 counts of **354 current, 375 RF6 base, and 374 pre-refactor**, the separate original count of **299**, all four reasoned literal-`getattr` rows, **432** matching frozen controls, **18** exact manifest adaptations with preserved source identities, and the byte-for-byte output move. The focused logs report **480 passed**, session impact **278 passed with one warning**, legacy pins **28 passed** under the stated environment change, and **4 passed** on each native minor. The added contract-acceptance negative has a retained exact-base red and current green record; production `src` bytes are unchanged from `f5979ca`.

I inspected the F1–F9 code and targeted tests, including no-best, cache observer, aliases, import edges, annotations, and offline AST scans. I did not rerun their session probes or broad suites, verify remote CI, or assess dynamic imports and the open source-owned import-walk question. This is one read-only reviewer’s assessment, not certification or milestone close.