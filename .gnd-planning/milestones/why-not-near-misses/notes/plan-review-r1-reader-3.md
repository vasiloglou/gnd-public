# Reader 3 -- protocol, authority, compatibility, privacy, documentation plan

Retained text of the reader's returned report, lightly edited for layout.
Scratch paths read `<scratch>`.

Both digests matched: plan `ec9cea0e…db63`, NM1 spec `e3855ca5…b670`.

**Verdict:** request-changes

**Scope.** Plan (457 lines) and NM1 spec (172 lines) in full, against
`redaction.py`, `api.py`, `witness/cli.py`, `export/{service,souffle_cli,lean_cli}.py`,
`commands/*`, `discover/candidates.py`, `agents.py`, `solve.py`, `exp/session.py`,
`why-not.schema.json`, `tools/run_tutorials.py`, the derivation-why-not records,
`standing-rules.md`, `docs/compatibility.md`, `docs/development/documentation.md`
and issue #70. Probes wrote only to `<scratch>/nm-review/reader3/`.

**What holds.**

- The NM-D6 caveat (plan:450, spec:13) is honest; the `(o2)` reading discloses
  its ambiguity and revert condition; "a direction is not approval" is stated;
  `auto=false`; merge needs the owner.
- No downstream application is named.
- Current-state facts check out: 13 OutputKinds; `--unredacted` on 6 parsers
  plus `judgments.py:15`; no env-driven configuration.
- The `/2` bump is argued correctly under `compatibility.md:7-9`.
- NM1 D1 keeps public bytes stable (but see R1-F2/R4-F1 on `work.probes`).
- DC1 drafts are illustrative and outside `docs/`; NM4-C5 controls docs drift.

## Findings

### R3-F1 -- The CLI option overrides the variable; `customer` is not a lock (blocking)

- **Where:** NM-D2 (plan:218-224), NM-R6, NM2-C1.
- **What is wrong:** `gnd --disclosure internal why-not … --raw` beats
  `GND_DISCLOSURE=customer`. No threat model is stated: an in-process caller can
  set `os.environ` or call `gnd.witness.service`, the kernel or
  `checking_service.run_check_raw` (re-exported at `api.py:64-66`), so the lock
  holds only against out-of-process callers who control neither environment nor
  process.
- **Fix:** the variable wins; the CLI option may only tighten, or conflicts are
  refused. State the threat model in §2.2 and `disclosure.md`. Scope the leak
  test to the public CLI and `gnd.api.__all__`.

### R3-F2 -- "customer withholds population values" contradicts declared redaction (blocking)

- **Where:** plan:72-73, predicate 3, §2.2 table, NM2-C3.
- **What is wrong:** `applied` hides only `redact: true` roles
  (`redaction.py:91-107`); issue messages, witnesses for undeclared roles and
  `discover` `allowed` lists (`discover/candidates.py:166-179`) still carry
  values. `(o1)` supports two readings; the plan uses both.
- **Reproduction:** `gnd check` over quoted_claims with `quote.work=12345`, mode
  unset: exit 0, no `redaction` block, message "supplies '12345' (int) for role
  'work'". No packaged example declares `redact`.
- **Fix:** an explicit owner question: (a) declared roles plus witness-lane
  redacted views; (b) every population value everywhere, a new whole-value
  projection with real cost. Not "ruled".

### R3-F3 -- The site inventory is incomplete and the enumerating test cannot see the gaps (blocking)

- **What is wrong:** four witness-lane views (missing `witness-view --raw`,
  `witness/cli.py:27-31`); four export raw parsers (`souffle`, `souffle-run`,
  `souffle-witness`, `lean`; `souffle-witness --out` publishes a raw certificate,
  `export/service.py:43-49`); Python raw keywords (`export_souffle`,
  `run_souffle`, `souffle_witness`, `export_lean` `raw=True`, `api.py:68-88`;
  `EvaluationSession.check/check_with_receipt/transition(unredacted=)`,
  `api.py:1022-1051`; `api.judgments(unredacted=)`, `api.py:900`);
  `api.witness` returns a raw certificate by construction; `discover` emits
  values; `emitter_specs()` (`redaction.py:412-536`) has none of these rows.
- **Fix:** enumerate all; derive the table test from the root parser tree
  (`--raw`/`--unredacted` actions) and `inspect.signature` over `gnd.api`;
  decide per site what `customer` does.

### R3-F4 -- `internal` would send declared-sensitive values to external agent providers (hardening)

- **What is wrong:** session feedback goes to the agent's stdin
  (`session-v7-contract.md:36-38`); agents may be third-party providers
  (`agents.py:179-197`). Session redaction is fixed at `applied`
  (`exp/session.py:433`) and the feedback schema version depends on it
  (`session_profile.py:26-35`). The 2026-10-25 owner ruling that redacted roles
  never get value candidates (`discover/candidates.py:131-132`) is not cited.
- **Fix:** exclude agent-bound streams and `discover` from `internal`, or ask
  the owner; cite the ruling.

### R3-F5 -- The mode does not reach child processes (hardening)

- **What is wrong:** `solve` re-invokes `python -m gnd` (`solve.py:201,506`)
  without the root option; `exp run` agents get an environment allowlist without
  `GND_DISCLOSURE` (`agents.py:179-197`), so an agent can run `why-not --raw`
  under a customer deployment and its output is retained.
- **Fix:** specify propagation, or refuse `exp run` and `solve` in `customer`;
  one test per spawner.

### R3-F6 -- "Unset is byte-identical / opt-in only" is contradicted, including a new exit-4 path (hardening)

- **What is wrong:** unset why-not gains fields, new probes, `/2`; search
  charged to the fixed `probes` ceiling (`why_not.py:49`) can turn exit 0 into
  exit 4, against NM-R1 -- an unrecorded compatibility change.
- **Fix:** scope NM-R5; fix §5; decide whether the search can fail a request or
  record the exit-4 exposure with a release note.

### R3-F7 -- Refusal band and envelopes underspecified (hardening)

- **What is wrong:** root options use `_BandSafeParser`, where a bad choice exits
  64 (`_arguments.py:11-18`); NM-D10 omits 64. Check-family exit 3 means
  `ill_formed`, which misdescribes a policy refusal; why-not reasons are only
  `input-invalid`/`work-limit`; no refusal envelope per lane; case handling
  unstated.
- **Fix:** specify per-lane refusal payloads; add 64 to NM-D10; state case
  handling.

### R3-F8 -- Provenance mis-states inherited state and ruling coverage (hardening)

- **What is wrong:** WN2-R1 (both bullets), R2, R3 were fixed in WN2
  (`003-phase-WN2.md:119`; schema 272-294, 596-660). §1 says `(o1)` yields
  NM-D2..D6 but §10 has D2 proposed and D6 uncovered; §2.1 tags NM-D6 `(o1)`;
  NM-D9 "Ruled" rests on a "yes" to an either/or question.
- **Fix:** reword O8/NM3-C2; drop the carryovers; fix plan:123, 162; mark NM-D9
  provisional, confirmed at the gate.

### R3-F9 -- Tests and docs gates not isolated from an ambient `GND_DISCLOSURE` (hardening)

- **What is wrong:** `tools/run_tutorials.py:129` copies `os.environ`;
  `tests/conftest.py` does not scrub.
- **Fix:** autouse fixture and runner scrub; blocks set it inline; a negative
  control.

### R3-F10 -- Docs phase ownership contradictory; one-home gap (completeness)

- **What is wrong:** predicates 4-5 give docs, release note and the how-to step
  to NM3; NM3-C4, §5 and the NM4 table give them to NM4; spec rule 5 moves the
  normalization home in NM3, plan:333 in NM4 -- the wire field would ship with
  its only normative text in a planning spec.
- **Fix:** one owner per page/section; e.g. NM3 writes the normative near-miss
  section, NM4 the rest.

### R3-F11 -- NM4 inventory misses grep hits and a required example (completeness)

- **What is wrong:** 28 grep hits at `33c260e`; six lack rows:
  `docs/development/architecture-audit.md`, `docs/reference/discover.md`,
  `docs/reference/ilp-bridge.md`,
  `src/gnd/skills/gnd-model-evolve/references/evolution-contract.md`,
  `src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json`,
  `src/gnd/skills/gnd-orm-core/references/representation-format.md` (the home of
  the `redact` declaration). The disclosure how-to needs a packaged example with
  a declared-sensitive role; none exists.
- **Fix:** add the rows and a packaged redaction example; note DC1 cannot be a
  real run; consider a real-run checkpoint after NM1.
