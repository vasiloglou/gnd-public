# Reader 2 -- implementability, pins and artifact homes

Retained text of the reader's returned report, lightly edited for layout.
Scratch paths read `<scratch>`.

Both digests matched: plan `ec9cea0e…db63`, NM1 spec `e3855ca5…b670`.

**Verdict:** request-changes

**Scope.** Plan (457 lines) and NM1 spec (172 lines) in full against `33c260e`,
with emphasis on NM2's disclosure sites and wiring. Probes under
`<scratch>/nm-review/reader2/`. Nothing written to the repository.

**What holds.**

- Homes are right: `_candidates`, `_join`, `_atom_blocker`, `_samples`,
  `_Budget` in `witness/why_not.py` (366, 379, 481, 474, 112); the view's closed
  allow-list (`view.py:93-97`) drops unknown keys.
- Layer map: `allow_list` empty; `gnd.redaction` in `checking` (line 723); a
  `gnd.disclosure` beside it is importable by witness, export and `api`.
- `why-not.schema.json` is already in `VENDORED_SCHEMAS`
  (`tests/support/runtime_schema_inventory.py:3`); closed schema justifies NM-D8.
- `environ` only in process plumbing; `_add_unredacted_argument` on 6 parsers
  plus `judgments.py:15`.
- RF1 `EXPECTED_PARSERS = 57` unchanged by a root option; subcommand help
  unaffected.
- The oracle AST import test exists (`tests/test_why_not_oracle.py:21`); every
  named gate file and tool exists; doc citations are accurate.

## Findings

### R2-F1 -- Near-miss charges can turn exit 0 into exit 4; not linear (blocking)

- **Where:** Outcome 1, NM-R1, NM-R3; spec D2, charges, Goal.
- **Reproduction:** `probe_quadratic.py`: 512 `quote` and 512 `author` rows
  with case/punctuation variants of one `work` value. Baseline `blocked`, probes
  1536; with the spec's charges `WhyNotWorkError probes ceiling {'probes':
  200001, …}`.
- **Fix:** a separate search cap that truncates (`near_miss_count` a lower bound
  with `near_miss_truncated`, or a fixed counting bound), so exits really are
  unchanged; restate NM-R3. Or amend NM-R1 and the predicates explicitly.

### R2-F2 -- Repeated free variable raises `WhyNotInternalError` (blocking)

- **Where:** §2.1 "Free roles are unconstrained"; spec index and invariant.
- **What is wrong:** production rejects inconsistent repeated variables
  (`extensions.py:660-663`); the index ignores free roles; `differing` is empty
  and the spec raises. Seeds 0..199 of the generated corpus raised 0 errors, so
  the bug would ship.
- **Reproduction:** `probe_repeat_free.py`: `quote(q=$q, work=$w), author(work=$w,
  person=$p, editor=$p)`, author `{w1, x, y}`, quote `{q1, w1}` →
  `WhyNotInternalError`.
- **Fix:** require repeated free variables consistent within the row; apply the
  invariant only to rows passing it; kernel and oracle tests for repeated free
  and bound variables.

### R2-F3 -- NM1's T15 cannot pass; public `work.probes` changes (blocking)

- **Reproduction:** `probe_public_probes.py`: g1 4→6, g2 5→7, g14 4→6, g19 3→6.
  The strip is recursive (blockers nest in `descent.clauses`), not one line.
- **Fix:** (a) do not run the search on the service path until NM3; or (b)
  accept and list the changed goldens and `gnd-run` outputs, adding docs gates to
  NM1.

### R2-F4 -- NM2 site list incomplete; the table test cannot enumerate API sites (blocking)

- **What is wrong:** 4 witness views (`witness-view --raw`,
  `witness/cli.py:27-30`); 4 export raw parsers (`lean`, `souffle`,
  `souffle-run`, `souffle-witness`) and their Python functions
  (`export/service.py:5,21,33,64`); `emitter_specs()` lacks `admission`,
  `api.check_with_receipt`, `EvaluationSession` methods (`api.py:1023-1051`),
  `api.judgments`, `api.witness`, `api.replay`. `export ilp` refuses redacted
  roles (`export/ilp.py:156`) and `discover` skips them
  (`discover/candidates.py:163`); their meaning under the modes is undefined.
- **Reproduction:** `probe_api_unredacted.py`: public callables taking
  `unredacted` include three `EvaluationSession` methods and `check_with_receipt`
  with no emitter spec.
- **Fix:** list every site; build the table from the parser walk,
  `inspect.signature` over `gnd.api.__all__` (and class methods) plus
  `gnd.export.service`, and `emitter_specs()`; rule on ILP export and discover.

### R2-F5 -- Session outputs cannot be unredacted without a wire change (blocking)

- **What is wrong:** `SessionRedaction.mode` is `Literal["applied"]`
  (`exp/session_eval.py:964-970`); `case_redaction` always builds `applied`
  (`exp/session.py:433`); payload v9 when the policy is active
  (`exp/session.py:405`); `commands/exp.py` has no `unredacted` path; feedback
  goes to the agent.
- **Fix:** keep the three session kinds applied in every mode, with the reason;
  or accept a session wire change and drop "no schema bump".

### R2-F6 -- Option precedence defeats the lock; wiring unspecified (hardening)

- **What is wrong:** `--disclosure internal` beats `customer`; the CLI calls
  public `api.why_not` (`witness/cli.py:46`), which would re-read the variable,
  so CLI precedence needs a context variable or an unresolved internal entry; an
  invalid choice exits 64 via `_BandSafeParser` (`_arguments.py:11-18`), a
  repeated option should use `_StoreOnce`; unspecified whether a bad variable
  fails `install`, `codegen`, `--version`; refusal payloads unspecified and some
  enums closed (`judgment.schema.json` `error.reason`).
- **Fix:** tighten-only; one context-variable resolver; 64 for usage, 3 for a bad
  variable, resolve only on disclosure-bearing commands; per-emitter refusal
  payloads.

### R2-F7 -- The root option changes RF1 exit goldens (hardening)

- **Reproduction:** 12 cli-exit goldens contain `usage: gnd [-h] [--version]`
  (`gnd`, `gnd_install`, `gnd_doctor`, `gnd_uninstall` × py311/313/314), plus
  `cli/tree.json` and three `cli-help/gnd.py31{1,3,4}.json`.
- **Fix:** carve root help/usage out of NM-R5; list the regenerated goldens in
  NM2-C4.

### R2-F8 -- WN2-R1 obligation is stale (completeness)

- **Reproduction:** `probe_schema_view.py`: 10/10 raw goldens relabelled
  `redacted` fail validation.
- **Fix:** NM3-C2 adds `near_misses: const "redacted"` to
  `redacted_clause.blocker` and the two fields to `$defs/blocker`; drop the
  carryovers.

### R2-F9 -- NM4 docs gates would not execute the new pages; ambient environment leaks (hardening)

- **What is wrong:** `tools/run_tutorials.py:200-221` `groups()` is closed, so
  new pages never run unless registered; `test_documented_learning_path`
  (`tests/test_documentation_tutorials.py:93`) excludes `why-not`; no packaged
  example declares `redact: true` (needs a home and an entry in
  `check_installed_docs.py:58`); `run_pages` copies `os.environ`
  (`run_tutorials.py:127`).
- **Fix:** register groups and parametrization in NM4; add the redaction example
  to §3; pop `GND_DISCLOSURE` in `run_pages` and conftest (NM2).

### R2-F10 -- Size estimates and pin lists incomplete (completeness)

- **What is wrong:** no NM2-NM4 estimates (NM2 touches about 12 modules); also
  literal: `tests/test_why_not_kernel.py:373` (breach at `probes == 4`) and
  `:416` (`96_722`); §3 says goldens under `tests/fixtures/why_not/`, the spec
  inline; `tests/fixtures/rf5-handlers/answers.json` carries `gnd-why-not/1`.
- **Fix:** per-phase sizes; full literal list; reconcile golden home; list the
  RF5 fixture under NM3-C2.
