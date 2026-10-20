Retention annotation: exact reviewer response follows; machine repository root replaced with <REPO> if present. Original response SHA256 6aab301e671ba0c8685910a45c5cfdba32bd3955ec622d842d80856da51394d4.

# IE6 amendment review — measurement

Verdict: approve the bounded IE6 amendment/spec for its delegated gate, with the execution hardening below. No concrete blocking measurement contradiction found. This is an independent read-only review of the proposed instruments, not an implementation, test run, timing reproduction or acceptance of future performance claims.

## Exact reviewed subjects

- notes/incremental-evaluation-plan.md SHA256 cd8ee3c10dee17d516b7670c125dbdb6993ce9dfbfd6db556e64be57e95ea29c, particularly the appended IE6 reopening amendment.
- notes/phase-IE6-spec.md SHA256 e72c1f127c6e587d27e1a37b700bef40041fb749f43dfc78b2ff88c2846c34eb.
- Read retained Astra summary, relevant 008-phase-IE5.md and 009-milestone-close.md measurement/closure material, and current tools/measure_evaluation_sessions.py and tools/measure_incremental_evaluation.py measurement implementations. The milestone-relative paths above identify subjects; original historical opinions are not inherited by IE6.

## Checked claims and required execution boundaries

1. Deterministic gates are falsifiable. IE6-C1 retains full payload/exit/branch parity and ordered complete calculation requests, with the original reporter denominator 4878 and strictly lower session body count. Current integrated tool actually rejects incorrect census/exits, empty traces, semantic mismatches and reporter denominator drift. New accounting tests are expressly required to fail against d0ffd9a and pass after each optimization; that distinguishes saved bookkeeping from merely relabeling counters. Optimization of repeated policy visits must be demonstrated with repeated distinct units, warm hits and dirty misses, not only the already reduced derivation counter.

2. Timing is separated from correctness and instrumented work. Existing measurement makes fresh input replay part of the timing boundary, warms each arm, rotates ABC/BCA/CAB, refuses cProfile and tracemalloc, and authenticates source/fixture bytes before and after its whole run. The spec additionally requires serial baseline/final comparison using an archived d0ffd9a tree, the same interpreter, actual import-path verification, raw samples/ranges and a full-receipt control. These are implementable without changing historical denominators. Three samples on a shared host remain descriptive, not evidence of a reliable general speedup; the prose explicitly preserves this limit and D7.

3. Existing oracle liveness weaknesses are understood. 008 records ordered/multiplicity and equal-error repairs, plus observer fingerprint contamination. The IE6 spec preserves frozen expected exits, typed ordered complete envelopes and observer separation. New visit counters must observe the actual measurement/policy lookup owners and include positive and negative controls. The current DIAGNOSTIC_WORK exclusion remains necessary if adding counters near shared fingerprint machinery.

4. Memory semantics remain conservative. Prepared metadata cannot remove charging of full policy storage, backing mappings, actual detached clones, metadata or relevant generations. The spec explicitly retains node/depth/cycle/finite refusal and unchanged row/byte limits. Projected retained footprint is neither RSS nor total process memory. A performance result cannot be obtained by silently discarding those charges.

5. Privacy and claim limits are appropriate. Workloads remain public/synthetic; no credentials, providers, proprietary SQL/question text or missing 547-program bundle are required. Diagnostic profile paths are local temporary references, not a source of downstream acceptance. Original timings are historical observations; final current-byte evidence must replace only the affected claims. The Astra experiment is accurately labeled a small process-only result rather than shipped improvement.

## Nonblocking execution hardening / completeness

- Before the new temporary timing driver is used, retain its exact bytes and identity, an explicit A/B/C arm map (baseline session, final session, full receipts), interpreter/options/environment, per-arm cwd/import provenance, fixture hashes and raw order. Verify that its full-receipt control is semantically the same in both source trees. Existing tool A/B/C meanings differ from this new three-arm comparison, so labels alone are insufficient. This is already consistent with the specified recorded-driver requirement; it is a concrete completion checklist, not a request for another owner decision.
- Give each adopted optimization its own deterministic assertion, with a named operation denominator and its actual d0ffd9a RED observation. If only one proposed optimization is implemented, explicitly defer the others. Avoid asserting a global performance win from a local builtin fast path or a lowered node counter that omits new metadata work.
- Do not compare IE5's historical 6.7885 seconds directly to a new run to claim IE6 speedup. Use the same-host serial archived-baseline/final run; report the current integrated full-versus-session ratio separately. A final session can improve versus baseline while remaining slower than full receipts.
- Instrumentation itself can perturb allocations and control flow. Keep footprint/visit probes separate from uninstrumented timing, check positive-control liveness at the actual public lookup owner, and retain source/fixture identities across both baseline and final experimental runs.

## Review limits

No commands imported candidate GND code, ran product tests, ran benchmark/profile providers, accessed credentials or altered production/tests. File reads and SHA256 identification only; this opinion was saved to the parent-requested temporary review file. I do not certify prospective counter thresholds, optimization safety, speedup, installed artifact behavior or future implementation bytes. Those require the declared pre-code RED corpus, final affected gates, independent diff review and renewed close evidence.
