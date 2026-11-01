# Confirmation round (round 2), reader 2 -- implementability, pins and homes

Retained text of the reader's returned report, lightly edited for layout.
Scratch paths read `<scratch>`.

Both digests matched (plan r2 `211d9e01…0a665de`, NM1 spec r2 `1b739a57…5d72`);
baseline `33c260e`. Nothing written in the repository. Probes in
`<scratch>/nm-review2/reader2/`: `probe_discovery.py`, `probe_view_idem.py`.

**Verdict:** approve-with-fixes. NM1 is implementable as written; NM2's wiring
and site table need C2-F1..F5 before the NM2 spec.

## Theme status

| Theme | Status | Reason |
|---|---|---|
| A | repaired | §2.1:199-207, spec:101-110 mirror `_joined_atom_candidates`; T10-T10c, T19 |
| B | repaired | flag default off; the `WhyNotLimits` field is harmless (`checked_why_not_limits` iterates `fields()`, `why_not.py:57-65`; `_why_not_intake_limits` reads named fields, `service.py:95-107`; T3 at `test_public_why_not.py:124-135` names them; no test enumerates the dataclass); `api.why_not` signature pin untouched |
| C | repaired | outside lens |
| D | partly | fail-open path (C2-F2); projection site unbuildable as worded (C2-F3) |
| E | repaired (ruling) | neighbouring contradiction C2-F5 |
| F | partly | flagged sites complete (15 CLI actions, 13 API keyword sites match NM2-C2); default-raw sites invisible (C2-F1) |
| G | repaired, wording defect | consistent with `session_eval.py:964-970`, `discover/candidates.py:131-132`, `ilp.py:156-158`; Outcome 2 and NM-D12 contradict (C2-F5) |

## Findings

### C2-F1 -- Discovery cannot see default-raw API sites; one-directional (high, self-inflicted)

- `api.witness`, `api.replay`, `api.why_not` have no `raw`/`unredacted`
  parameter; `api.judgments` is not in `__all__` (`api.py:122`); ILP export,
  `discover`, and `admission` (absent from `emitter_specs()`, which yields 12
  kinds) are invisible; hand rows are never checked against live code;
  `api.why_not` is missing from the known rows; NM-R6's surface excludes
  `api.judgments` and `gnd.export.service`; NM-R4's "one site table" is a test
  artifact, not a runtime home.
- **Reproduction:** `probe_discovery.py`: `api.__all__ members WITHOUT
  raw/unredacted: ['witness', 'replay', 'why_not']`; `judgments in __all__:
  False`; `emitter_specs()` 12 kinds, no `admission`.
- **Fix:** every parser path (57) and every public callable of `gnd.api` (module
  level), its classes and `gnd.export.service` must have a row, even "no
  population values"; a reverse check that every row resolves to live code; add
  `api.why_not` and `admission`; align NM-R6; the runtime home is
  `gnd.disclosure`, the test verifies coverage.

### C2-F2 -- Invalid variable plus `--disclosure internal` fails open (medium-high, self-inflicted)

- `GND_DISCLOSURE=Customer gnd --disclosure internal witness … --raw`: the option
  sets the context variable, the environment is never read, raw values flow.
- **Fix:** the CLI validates `GND_DISCLOSURE` first; invalid exits 3 on a
  disclosure-site command even with `--disclosure`; NM2-C1 case.

### C2-F3 -- Projection point unspecified; the obvious place breaks the CLI (medium, self-inflicted)

- `gnd.api.witness/replay/why_not` are identity re-exports of
  `gnd.witness.service.*` (`api.py:109-118`); the CLI calls the service
  (`witness/cli.py:6,46,59,67`). Projecting in the shared function breaks
  `gnd witness`: `result_view` has no `certificate` (`view.py:78-90`) and
  `witness/cli.py:68` raises `KeyError`, uncaught at `:81`. Check-family handlers
  call private `api._run_validate` etc. (`commands/checking.py:34`).
  `why_not_view` is idempotent (22/22 goldens).
- **Fix:** name the projection point per lane (service with CLI changes, or
  `gnd.api` wrappers ending the identity alias, recorded in the shim inventory)
  and the check-family handler resolution point.

### C2-F4 -- Child forwarding misses an agent path and conflicts with the layer map (medium, self-inflicted)

- Schema-v6 command policies build their environment from the policy allowlist
  reading `os.environ` (`exp/adapter_policy.py:303-312`), so an option-set mode
  never reaches them. `gnd.agents` is `infrastructure` (rank 0) and
  `gnd.disclosure` would be `checking` (rank 2): the value must be passed down
  from `exp`. `solve` mechanism unspecified (argv is recorded, `solve.py:298`;
  no `env=` at 506-515). Forwarding is a default, not a lock.
- **Fix:** cover both agent paths; pass the value as a parameter from `gnd.exp`
  with `EnvironmentFact` provenance `supplied` (`process.py:31`); choose env or
  argv for `solve` and state the record effect; docs say forwarding does not bind
  agents.

### C2-F5 -- "Every value in export outputs" contradicts "ILP export unchanged" (medium, self-inflicted)

- `gnd export ilp` writes raw undeclared values (`ilp.py:11, 235`). "An explicit
  raw request on these is still refused" is vacuous: no `--raw`/`--unredacted` on
  `discover`, `export ilp`, `exp`.
- **Fix:** "witness-lane, `lean` and `souffle*` export outputs"; drop or recast
  the vacuous sentence.

### C2-F6 -- Smaller wiring gaps (low, self-inflicted)

- `run_main` calls `cli.main` in process (`tests/support/cli_runner.py:67-78`; 19
  direct calls): without `finally: reset(token)` a customer-mode CLI test leaks
  into later API calls. A root option is accepted only before the subcommand;
  `gnd check … --disclosure customer` exits 64.
- **Fix:** reset the token; NM2-C1 case; a `cli.md` sentence.

### C2-F7 -- RF1 regeneration list omits the manifest pin (low, pre-existing)

- `tests/fixtures/rf1-pins/goldens.sha256` is pinned at
  `tests/test_rf1_pin_harness.py:29`; `test_rf1_cli_pins.py:118-123` overlays the
  `compiled-snapshot-cli` successor on `tree.json`.
- **Fix:** add `goldens.sha256` and `MANIFEST_SHA256` to NM2-C5; add
  `tests/test_rf1_pin_harness.py` to the NM2 gate.
