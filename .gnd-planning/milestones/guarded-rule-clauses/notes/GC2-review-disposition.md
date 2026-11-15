# GC2 independent review disposition

Claude Code Opus at high effort exited 0 on the runtime and test diff of
`b4e84af4`. It received the diff on stdin, with tools disabled, and ran
no reproduction commands. [One reviewer is one reviewer](phase-GC2-claude-review.md).

| Finding | Disposition |
|---|---|
| Incomplete negated atoms bypass exclusion | The proposed admitted-model defect did not reproduce. The shared guarded role-claim check covers negative atoms, and the regression confirms validation refuses a partial bind before evaluating any filter. |
| Temporal guard routing | Hardening within scope. Filtered temporal consequents now use the existing temporal evaluator over surviving bindings. Temporal where terms carry a bounded date-function counter. A concrete date-add regression covers both surfaces and observes the post-filter count in the message. Model-version 11 retains its existing diagnostics-flag refusal. |
| Computed negative relation | Blocking. An unavailable-only semiderived relation with a raw claim caused check to exit 70 during origin projection. The checker now builds the effective view even when it has only unavailable heads, and the filter ignores raw claims for uncalculated semiderived relations. The pure reference evaluates the given effective snapshot. |
| Synthesis and work | The representative exclusion witness was already present. Confirmation now charges negative lookup and where work. A grounded exception can exclude every potential binding, so additive witness construction remains bounded. Unsupported derived negative shapes remain explicit in the synth manifest. |
| Duplicate membership error | The reported duplicate did not reproduce. The older walk emits role-domain warnings, while the new where rule owns the static membership-list refusal. The added fixture observes one refusal at the exact member-list path. |
| Work-exhausted count | Hardening within scope. An exhausted filter no longer reports a known zero count. Counts are null if the filter cannot finish; coverage or term uncertainty with a completed filter still reports the number of definite survivors. |

The final compatibility check retained the original legacy numeric report
bytes. The initial compatibility run showed four unrelated assurance scope
IDs on the existing fixture. The filter-specific variant resolves that
regression by selecting those branches only for new syntax. A counted
query-policy successor covers the single typed snapshot traversal used to
prepare negative relation role indexes.
