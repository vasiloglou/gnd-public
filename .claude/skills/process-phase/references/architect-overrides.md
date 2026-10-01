# Opt-in recertification and architect override

The owner ruled on 2026-09-28 that certification and recertification are not
automatic phase or milestone gates. Run them only when the owner explicitly
requests one for a particular subject and scope. A changed source, stale
installed bundle, completed phase, milestone close, or historical plan clause
is not such a request. Do not ask for a waiver each time: absent the explicit
request, there is no recertification prerequisite to waive. Focused tests,
owner gates, and other applicable completion criteria remain in force.

An earlier certificate stays bound to its original bytes. If changed bytes
cause the installed reader to withhold assurance, report that state; do not
call the older certificate current or bypass the reader. Record a decision to
omit a formerly planned recertification in the phase or close record with the
source and claim boundaries stated. This policy supersedes the v6.3 plan
gate's D10 one-matrix-per-milestone default for future work.

The rest of this reference applies only when a currently requested,
scope-specific recertification is later explicitly overridden.

## Authority and effect

The repository architect may explicitly override a recertification
prerequisite. The project identifies who holds that role. An applicable
architect override makes the recertification prerequisite **satisfied for
process sequencing**: stop requesting that recertification and continue with
the next otherwise-authorized phase step.

The architect accepts the residual risk carried by the changed bytes. The
override is a governance decision, not a new technical proof. Keep the earlier
certificate bound to the bytes it actually certified; do not call it current,
regenerated, or broadened. Downstream records cite the earlier certificate and
the override separately.

## Valid override instrument

An override is valid when the architect explicitly uses `override` or `waive`
and identifies the recertification being skipped with enough context to avoid
confusing it with another gate. Record, before continuing:

- architect role and identity as the project defines them;
- exact architect wording and date;
- certificate or completed phase being relied upon;
- known changed files or change class that triggered recertification;
- boundary: recertification was skipped by architect decision and the prior
  evidence still speaks only for its original bytes.

No new review, proof run, impact analysis, or repeated confirmation is required
unless the architect's override asks for one. Existing read-only facts already
known may be recorded, but they are not preconditions that can silently defeat
the override.

## Scope and lifecycle

Never infer an override of an explicitly requested run from `approved`,
`continue`, cost concerns, or a request to clean up an attempted run. It is
instance-specific unless the architect explicitly names a broader class. A
later source change outside its scope does not create an automatic
recertification prerequisite under the default policy; the owner may request
a new run. The architect may withdraw an override explicitly, restoring only
the specific prerequisite that override had set aside.
