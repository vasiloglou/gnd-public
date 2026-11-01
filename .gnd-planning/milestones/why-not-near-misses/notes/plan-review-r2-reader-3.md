# Confirmation round (round 2), reader 3 -- protocol, authority, compatibility, privacy, docs

Retained text of the reader's returned report, lightly edited for layout.
Scratch paths read `<scratch>`.

Both digests matched (plan r2 `211d9e01…5de`, NM1 spec r2 `1b739a57…1d72`);
both byte-identical to `notes/`.

**Verdict:** approve-with-fixes; C3-F1 must be fixed before the plan gate.

**Scope.** r2 plan (555 lines) and NM1 spec (231 lines) in full, diffed against
r1; the disposition and the r1 note; checked against `api.py`,
`witness/{cli,service,view}.py`, `export/{service,souffle_io,souffle_types,ilp,ilp_service,ilp_prompt}.py`,
`redaction.py`, `agents.py`, `solve.py`, `exp/session.py`,
`session_environment.py`, `evaluation_feedback.py`, `fidelity/report.py`,
`discover/candidates.py`, `commands/_arguments.py`, `tools/run_tutorials.py`,
`docs/compatibility.md`, `003-phase-WN2.md`, `tests/test_why_not_anonymity.py`.
Re-ran the 28-file grep. Probe `<scratch>/nm-review2/reader3/anon.py`: the
anonymity scanner over the milestone directory, 12 files, 0 hits.

## Theme status

| Theme | Status | Reason |
|---|---|---|
| A | repaired (in lens) | plan:199-207; spec:101-110, T10/T10b/T10c/T19 |
| B | repaired | plan:250-252, NM-D15; spec Goal, T15 |
| C | repaired | NM-R1/R3; own cap; NM-D14 |
| D | partly | context variable outranks the environment (C3-F3); invalid-value ordering can fail open (C3-F2); threat model self-contradictory for API callers (C3-F4) |
| E | partly | "every value in export outputs" conflicts with ILP "unchanged in every mode"; ruled NM-D12 text broader than the accepted proposal (C3-F5) |
| F | partly | discovery sees only flagged sites (C3-F6) |
| G | partly | theme-L forwarding sends `internal` to agents (C3-F1); spawner list incomplete; verifier environment unpinned (C3-F7) |

H-Q applied in text (H plan:173-174, 381-382; I 22-24, 183, 547; J 126, 366-368,
478-479, with §5 overclaim C3-F8; K 288-296, 548; L 298-300, conflicting with G;
M 369-371; N 107-110, 321, 390-395; O all 28 hits have rows, DC1b moved without
a recorded deviation C3-F11; P/Q spec T1-T20).

**Reading of "yes":** faithful and bounded -- it answers the first alternative of
a two-way question; only D12-D15 are ruled; D2/D6/D9 stay proposed/provisional;
`(p1)` text carries no opinion; a direction is not approval. One overreach:
C3-F5.

## Findings

### C3-F1 -- `exp run`/`solve` forward `internal` to agents: a new agent-bound leak (blocking, self-inflicted)

- **Where:** plan:298-300, NM2-C4 vs O17 (171), NM-D13 (269-272).
- **What is wrong:** the agent allowlist (`agents.py:179-197`) lacks
  `GND_DISCLOSURE`, so an agent's `gnd check` applies declared redaction
  (`api.py:641-671`). Forwarding `internal` lifts it for agents that may be
  external providers; `solve` children inherit the full environment (no `env=`
  at `solve.py:506`).
- **Fix:** forward only `customer`; test both directions; or put it to the owner
  under NM-D13.

### C3-F2 -- Invalid variable plus `--disclosure internal` can fail open (hardening, self-inflicted)

- `GND_DISCLOSURE=Customer` or `customer ` with `--disclosure internal`: read
  literally, the option wins. **Fix:** validate the environment first on every
  disclosure-site command; add the case to NM2-C1.

### C3-F3 -- Context variable outranks the environment (hardening, self-inflicted)

- A context value `internal` overrides `GND_DISCLOSURE=customer` on the API path.
  **Fix:** the resolver returns `customer` whenever either source says so.

### C3-F4 -- Threat model self-contradictory for the API; agent "inherits the lock" too strong (low, self-inflicted)

- Every `gnd.api` caller runs code in the process; an agent controls its own
  environment. **Fix:** protect end users whose requests an operator-controlled
  wrapper forwards into argv or API keywords; in-process the mode is a guard, not
  a lock; "inherits the default".

### C3-F5 -- "Export outputs" scope broader than the accepted proposal; conflicts with ILP (hardening, self-inflicted)

- The accepted proposal was declared roles + all witness-lane values; r2 rules
  "+ export outputs". ILP export writes raw undeclared values
  (`export/ilp.py:11-13`) into an LLM prompt data section (`ilp_prompt.py:1-7`)
  and is unchanged in every mode. Lean/souffle default results are value-free
  (`souffle_types.py:47-56`, `export/service.py:21-56`).
- **Fix:** say "exports `lean`, `souffle*`"; record the export extension as the
  author's reading, not covered by `(p1)`.

### C3-F6 -- Discovery misses commands that print values without a flag (hardening, pre-existing)

- `gnd fidelity` quotes a verbatim extracted fact (`fidelity/report.py:6-9, 202,
  223`) in every mode; ILP export likewise. **Fix:** walk every leaf command and
  public `gnd.api` callable; each is a site, value-free, or "emits values in
  every mode".

### C3-F7 -- Spawner list incomplete; verifier environment unpinned (hardening, self-inflicted)

- Also spawning: `exp/session.py:470` (verifier `gnd check`),
  `declared_adapter.py:326,372`, `review/adapters.py`, `exp/tests_runner.py`.
  Session kinds stay `applied` because `verifier_environment()`
  (`exp/session_environment.py:7-14`) excludes the variable.
- **Fix:** enumerate spawners mechanically (callers of `run_bounded_process`,
  `Popen`, `create_subprocess_exec`); per-spawner rule; a test pinning that the
  verifier environment does not carry the mode.

### C3-F8 -- §5 overclaims compatibility (low, partly pre-existing)

- Under `customer`, `api.witness`/`api.replay` change shape, check-family raw
  requests exit 3, enums may grow. **Fix:** scope §5 to "mode unset"; list
  customer-mode contract changes for the release note.

### C3-F9 -- Redacted near-miss count is a normalized membership oracle (low, pre-existing)

- With `--row`, a count > 0 reveals a spelling variant exists. **Fix:** name it
  in the threat model, or show only a boolean; owner-visible choice.

### C3-F10 -- NM1 spec no longer binds NM-R2 by name (low, self-inflicted)

- **Fix:** add an NM-R2 row.

### C3-F11 -- DC1b move not recorded as a deviation (low, self-inflicted)

- **Fix:** one sentence with the reason (NM1 has no public path).

**Holds:** anonymity clean; all 28 grep hits dispositioned; cited lines verified;
why-not error envelopes carry only enum reasons; the invariant message has no
values.
