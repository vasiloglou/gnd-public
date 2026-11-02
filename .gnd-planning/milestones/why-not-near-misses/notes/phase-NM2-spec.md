# Phase NM2: the disclosure mode

**Status: r1, approved by the owner 2026-11-01 `(s2)`; implementation in progress.**

`(s2)` Owner approval, 2026-11-01, quoted: "yes", in answer to "Do you approve
the NM2 spec with D1-D7 as proposed, including installing Python 3.11 with uv
and no review panel over the spec?" Approved bytes: SHA-256
`76d594e34518a2e4b23e5046933ccb499ee5c0e8fe408f6e34f4c46895b79717` (before this
tag). Rulings: D1 (b), D2 (a), D3 (a), D4 (a), D5 (a), D6 (a) including the uv
download of Python 3.11, D7 (a) prose; no spec review panel; go-ahead to
implement.

## Provenance

- Plan: [why-not-near-misses-plan.md](why-not-near-misses-plan.md) r3, approved
  `(a1)`: §0 (NM-R4..R7), §2.2, §3, §4 NM2 (NM2-C1..C7), §6, §9 NM2 row, and
  §10 rulings NM-D2, D7, D10, D12, D13, D16 and D17.
- Prior phase: [001-phase-NM1.md](../001-phase-NM1.md). It carries nothing into
  NM2. Its open questions belong to NM3 and NM4.
- Harvest: three read-only code surveys at `acfb9ae`, one each for the CLI, the
  API and export functions, and the spawners and test isolation. Their findings
  are cited by `file:line` below, and every citation used in a design decision
  was re-read by the author. No review has read this spec.

## Corrections to the plan, found at harvest

These are recorded as refuted premises with a repair in this spec. The plan
itself is repaired at milestone close.

| ID | Plan sentence | What the code shows | Repair here |
|---|---|---|---|
| H1 | §4 NM2-C2: "Every leaf of the root parser tree (57 at `33c260e`)" | 57 is every parser: the root, 8 group parsers and 48 leaves (`tests/test_rf1_cli_pins.py:21`, `cli/tree.json`) | The table covers the 48 leaves; the 9 non-leaf parsers are named as such |
| H2 | §2.2: witness-lane projection "in thin `gnd.api` wrappers … ending the identity aliases" | `tests/test_rf4_peripheral.py:75-79` pins `gnd.api.witness is gnd.witness.service.witness` (and `replay`, and the seven export functions) for every `moves.json` row; `moves.json` is immutable RF4 evidence | D1 |
| H3 | §2.2: "Check-family resolution happens in the shared `api._run_*` helpers" | `api.judgments` calls `check(..., unredacted=True)` internally (`api.py:958`), and `EvaluationSession.check_with_feedback` calls `check(...)` in applied mode (`api.py:1072`). Resolving inside the shared helpers would refuse the first under `customer` and unredact the second under `internal`. | D3 |
| H4 | §2.2: forwarding adds `GND_DISCLOSURE=customer` to child environments | `run_bounded_process` masks every supplied environment value of 4 or more characters out of child stdout and stderr (`process.py:277-286, 351-352`). `customer` would become `***` everywhere in agent output. | D4 |
| H5 | §9 NM2 gate lists the RF1 goldens to regenerate | `tools/rf1_pins.py merge` needs captures from Python 3.11, 3.13 and 3.14 (`rf1_pins.py:333-367`). 3.11 is not installed on this machine (`uv python list`). | D6 |

## Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| Plan O6, NM2-C1 | one mode, resolved once; resolution order; tighten-only option; context variable reset; refusals and bands; hostile values | `gnd.disclosure`; `cli.main`; T1–T12 |
| NM2-C2 | a total disclosure table over the 48 leaves and the public callables of `gnd.api`, its classes and `gnd.export.service`, plus the output kinds; a reverse check | `gnd.disclosure.SURFACES`; T13–T15 |
| NM2-C3, O7 | per-site leak and refusal tests; `internal` raw; every-mode rows byte-identical; `gnd witness` still writes its certificate | T16–T27 |
| NM2-C4, O17, NM-D16 | spawners: a mechanical list with a rule each; `customer` forwarded on both `exp run` agent paths and in `solve`; child environments otherwise identical; the verifier never carries the mode | §Spawners; T28–T34 |
| NM2-C5, NM-R5 | unset parity; regenerated RF1 goldens listed | T35, T36 |
| NM2-C6 | environment isolation; negative control | T37, T38 |
| NM2-C7 | a packaged redaction example; `--disclosure` help | `examples/disclosure/`; T39, T40 |
| NM-R6 | refuse, never downgrade; option tightens only; threat model | T7–T12; the docs claim is NM4's |
| NM-R7 | layering: `gnd.disclosure` in `checking`; lower layers take parameters; RF6 allow-list unchanged | T41 |
| NM-R8 | anonymity | T42 |
| §9 NM2 row | the gate command | Verification selection |
| H1–H5 | harvest corrections | D1, D3, D4, D6; T13 |

## Standing rules bound to this phase

1. **Totality.** `disclosure.resolve()` is total over any environment string:
   empty, 64 KiB, non-ASCII, mixed case and trailing space each give exactly one
   outcome, either a mode or a refusal (T3). A value containing NUL cannot
   reach `os.environ`.
2. **Input cap bounds the algorithm.** The resolver does constant work: one
   environment read and one comparison against two literals. The table check
   is one pass over the parser tree and the module. Nothing scales with
   untrusted input, so there is no time-bound test, by argument.
3. **Validation order**, pinned by tests:
   1. On a disclosure-bearing leaf, a malformed `GND_DISCLOSURE` is refused
      first.
   2. Then an option that tries to loosen the mode.
   3. Then raw requests.
   4. Only then does the handler run.

   Usage errors (exit 64) come before all of these, because argparse runs
   first. T9 and T10 pin each adjacent pair.
4. **One walk.**
   - One resolver, `disclosure.resolve`.
   - One CLI walk over the parsed namespace, for every `raw` and `unredacted`
     dest.
   - One API helper, `disclosure.values_allowed(requested, option)`, called by
     every API site.
   - One table, `SURFACES`, with one totality test.
5. **One home.**
   - The mode's normative text is this spec until NM4 moves it to
     `docs/reference/disclosure.md`.
   - The table lives in code (`gnd.disclosure.SURFACES`), and NM4 generates the
     docs table from it.
6. **Measurement over argument.** Unset parity is shown by running the
   unchanged contract suites and the golden diff (T35), not argued.

## Goal

The resolver must behave as follows:

- With `GND_DISCLOSURE` unset and no `--disclosure`, every existing test and
  golden passes unchanged, except the RF1 root-usage and root-help goldens
  listed in T36.
- Under `customer`, every raw or unredacted request on a site exits 3 in the
  CLI or raises `DisclosureRefused` in the API.
- Under `internal`, every site returns what its raw option returns.
- The rows that emit values in every mode return identical bytes in all three
  states.
- Under `customer` only, child processes that run GND or an agent receive
  `GND_DISCLOSURE=customer`.

`uv run pytest -q tests/test_disclosure_mode.py` exits 0, and so does the NM2
gate in Verification selection.

## Design

### `src/gnd/disclosure.py` (new, layer `checking`, about 150 lines)

```python
MODES = ("internal", "customer")
ENVIRONMENT = "GND_DISCLOSURE"

class DisclosureRefused(ValueError):
    """A request for values refused by policy. ``str(error)`` names the option
    or the variable, never a value."""

def resolve(environ: Mapping[str, str] | None = None) -> str | None:
    """The effective mode for an API call: 'internal', 'customer' or None.
    Raises DisclosureRefused for a malformed GND_DISCLOSURE."""

def values_allowed(requested: bool, option: str) -> bool:
    """The one API decision. customer: False, or DisclosureRefused(option) if
    requested. internal: True. unset: requested."""

def forward(environ: Mapping[str, str] | None = None) -> dict[str, str]:
    """{'GND_DISCLOSURE': 'customer'} when the resolved mode is customer,
    else {}. Spawners merge it into the child environment they already build."""

@contextmanager
def invocation(mode: str | None) -> Iterator[None]:
    """Set the CLI's mode for one in-process invocation; reset the token on exit."""

SURFACES: Mapping[str, Surface]   # the disclosure table
```

**Resolution in `resolve`** (NM-D2, plan §2.2):

1. Read the context-variable mode, `ctx`, and `env = environ.get(ENVIRONMENT)`.
2. If `env` is not `None` and not in `MODES`, raise
   `DisclosureRefused("GND_DISCLOSURE must be 'internal' or 'customer'")`.
3. If `ctx` or `env` is `"customer"`, return `"customer"`.
4. Otherwise return `ctx`, or else `env` (`"internal"` or `None`).

`Surface` is a frozen dataclass with these fields:

- `kind`: `"site"`, `"value-free"` or `"every-mode"`.
- `convention`: `"declared"`, `"view"` or `None`.
- `spawns`: a bool.
- `note`: a string.

`SURFACES` is keyed by one of:

- a CLI leaf path, such as `"gnd why-not"`;
- `"api:<name>"` for every public callable bound in `gnd.api`;
- `"api:EvaluationSession.<method>"`;
- `"export.service:<name>"`;
- `"kind:<OutputKind>"`.

It imports only the standard library: `contextvars`, `os`, `dataclasses` and
`typing`.

### `src/gnd/cli.py` (about 40 lines)

**The root option.** It is added after `--version` (`cli.py:633-638`):

```python
parser.add_argument("--disclosure", choices=MODES, action=_StoreOnce,
                    help="disclosure mode for this invocation: internal or customer "
                         "(a root option: give it before the subcommand; it can only "
                         "tighten GND_DISCLOSURE=customer)")
```

`choices` and `_StoreOnce` route a bad or repeated value to exit 64 through
`_BandSafeParser.error`.

**Dispatch.** `cli.py:668-669` becomes:

```python
args = parser.parse_args(argv)
refusal, mode = _disclosure(args)
if refusal is not None:
    print(f"gnd: error: {refusal}", file=sys.stderr)
    return EXIT_INPUT        # 3, NM-D10
with disclosure.invocation(mode):
    return args.handler(args)
```

`_disclosure(args)` runs only when `SURFACES[_leaf(args)]` is a site or
spawns. It runs these steps in order:

1. A malformed environment is refused.
2. If the environment says `customer` and the option says `internal`, the
   refusal reads "--disclosure internal is refused when GND_DISCLOSURE=customer".
3. The mode is the option, or else the environment.
4. Under `customer`, if any of the namespace's `raw` or `unredacted` dests is
   true, the refusal reads "--raw is refused in customer disclosure mode"
   (or `--unredacted`).
5. Under `internal`, every `raw` and `unredacted` dest present on the namespace
   is set to `True`.

For other leaves the environment is ignored and the mode is `None`. This is
D3's one CLI walk: no handler changes for the check family or the export lane.

### `src/gnd/api.py` (about 30 lines)

Each public check-family function begins with:

```python
unredacted = values_allowed(unredacted, "unredacted=True")
```

The functions are `validate`, `check`, `diff`, `verbalize`, `transition`,
`check_with_receipt` and `judgments`. They then call the unchanged `_run_*`
helpers.

- **Internal calls bypass the public functions.**
  - `judgments`' two internal checks (`api.py:958-963`) call
    `checking_service._run_check` directly with fixed flags. A new private
    `_check_unresolved` holds `check`'s current body, and `check` calls it after
    resolving.
  - `EvaluationSession.check_with_feedback` calls `_check_unresolved(...,
    unredacted=False)`: session feedback is applied in every mode (NM-D13).
- **Delegating methods.** `EvaluationSession.check`, `check_with_receipt` and
  `transition` delegate to the public functions, so they resolve through them.
- **No public signature changes**, so `tests/test_public_api.py` and
  `test_public_reference_signatures.py` pins hold.

### `src/gnd/witness/service.py` (D1 (b), about 30 lines)

- **New raw functions.** The current bodies of `witness` and `replay` move
  unchanged to new public raw functions `witness_result` and `replay_result`.
  `why_not`'s body moves to `why_not_result`.
- **Mode-aware public functions.** `witness`, `replay` and `why_not` keep their
  names, signatures and `__module__ = 'gnd.api'`, and become:

```python
def witness(model_path, population_path, ...):   # signature unchanged
    result = witness_result(model_path, population_path, ...)
    return result_view(result) if resolve() == "customer" else result
```

`replay` and `why_not` follow the same pattern. The behaviour is fixed by
T19–T21:

| Function | Unset or `internal` | `customer` |
|---|---|---|
| `witness`, `replay` | the raw result, as today | `view.result_view(raw)` |
| `why_not` | the raw envelope, as today, with no `view` key | `{**why_not_view(raw), "view": "redacted"}` |

- **Identity and the body pin.** The `gnd.api` aliases at `api.py:109-117`
  stay identity aliases, so `test_rf4_peripheral.py:75-79` holds.
  `test_moved_algorithm_preserves_base_body` sees the changed bodies of
  `witness` and `replay`. Each gets a current source-successor row (`kind`
  `RF4`, before and after algorithm digests and imports) in
  `compiled-snapshot-obligations/evidence/CI/source-successors.json`, which is
  the established mutable successor file (`tests/support/rf9_ci_sources.py:47-68`).
- **`witness/cli.py` calls the raw functions.** It calls `witness_result`,
  `replay_result` and `why_not_result` and keeps its own projection
  (`cli.py:53-55, 78-79`). That is the plan's "projection in the CLI after it
  has read the certificate". `gnd witness --out` therefore writes its
  certificate from the raw result in every mode in which `--raw` is allowed.

### `src/gnd/export/service.py` (about 12 lines)

`export_lean`, `export_souffle`, `run_souffle` and `souffle_witness` begin with
`raw = values_allowed(raw, "raw=True")`. That gives four more current
source-successor rows, because they are RF4 moves. `verify_lean`,
`verify_souffle` and `compile_lean` are value-free.

### Child processes (NM2-C4, NM-D16)

**Mechanical list.** A grep at `acfb9ae` for `run_bounded_process`,
`subprocess.*`, `asyncio.create_subprocess_*` and `os.exec*/spawn*/system/popen`
over `src/gnd` (T28 re-runs it as an AST walk and fails on a site not in this
table):

| # | Site | Runs | Rule |
|---|---|---|---|
| 1 | `process.py:483` `run_bounded_process` | the neutral runner | parameter only; D4 |
| 2, 3 | `agents.py:372, 412` `invoke_agent` | agent CLI | **forwards**: new keyword `extra_environment: Mapping[str,str] = {}` merged after the fixed names, each with `EnvironmentFact(provenance="supplied")`; passed by `gnd.exp.session.run_session` from `disclosure.forward()` |
| 4, 5 | `declared_adapter.py:323, 369` `_invoke_command` | declared command agent | **forwards**: `disclosure.forward()` merged into `resolved.environment` in `gnd.exp` before the call |
| 6 | `exp/session.py:493` `run_gnd_verifier` | GND verifier | **never**: `verifier_environment()` is unchanged, so session kinds stay `applied` |
| 7 | `exp/tests_runner.py:942` | the caller's tests | **never**: runs under `verifier_environment()` |
| 8, 9 | `review/adapters.py:551, 589` | reviewer agent CLI | **forwards** (D5): merged into `seat_environment` in `gnd.review` |
| 10 | `export/applications.py:121` | PyRel interpreter | does not run GND or an agent; unchanged |
| 11 | `export/souffle_runtime.py:55` | `souffle` | does not run GND or an agent; unchanged (it inherits `os.environ`, as today) |
| 12 | `export/lean_runtime.py:64` | `lake`/`lean` | as 11 |
| 13 | `solve.py:506` `_run_child` | `python -m gnd <station>` | **forwards**: under `customer`, `env={**os.environ, **forward()}`; otherwise no `env` keyword, as today. Recorded argv unchanged. |
| 14 | `archsmoke.py:323` | generated-project code from its tests | does not run under a `gnd` command; unchanged |
| 15–17 | `examples/plan_apps/core.py:222, 312`; `skills/gnd-update-review-panel/scripts/update_harnesses.py:86` | example and maintainer scripts outside the layer map | not GND runtime; unchanged |

**D4, the masking fix.**

- `run_bounded_process` gains `disclosed_names: frozenset[str] = frozenset()`.
  Values of those names are not masked (`_sensitive_values` skips them). The
  default is empty, so the runner's output is unchanged for every existing
  caller.
- Forwarding callers pass `frozenset({"GND_DISCLOSURE"})`. This is a parameter
  to infrastructure, so NM-R7 holds.

Under `internal` or unset, `forward()` returns `{}` and no caller passes a name,
so every child environment, fact list and output is byte-identical to `33c260e`
(T29).

### Disclosure table (`SURFACES`, NM2-C2)

**CLI leaves (48):**

| Class | Leaves |
|---|---|
| site, declared | `check`, `validate`, `diff`, `verbalize population`, `measure`, `verify`, `judgments check` |
| site, view | `witness`, `witness-view`, `replay`, `why-not`, `export lean`, `export souffle`, `export souffle-run`, `export souffle-witness` |
| spawns (`spawns=True`) | `exp run` (kind every-mode: its session kinds), `solve`, `review panel`, `review panel-light` (kind value-free) |
| every-mode | `discover`, `export ilp`, `fidelity` |
| value-free | the other 26: `codegen`, `conformance`, `coverage`, `doccheck`, `doctor`, `evolve apply`, `evolve finalize`, `evolve preview`, `exp author-expectation`, `exp close`, `exp init`, `exp validate`, `export lean-compile`, `export lean-verify`, `export pyrel`, `export souffle-verify`, `extract`, `import ilp-rules`, `import mined-rules`, `import rai-orm`, `install`, `recovery inventory`, `recovery verify`, `review finalize`, `synth`, `uninstall` |

Non-leaf parsers are not rows: `gnd`, `gnd evolve`, `gnd exp`, `gnd export`,
`gnd import`, `gnd judgments`, `gnd recovery`, `gnd review` and
`gnd verbalize`. A class may move during implementation only with a recorded
finding.

**API: 49 public callables bound in `gnd.api`, plus `EvaluationSession`
methods.**

| Class | Names |
|---|---|
| site, declared | `validate`, `check`, `diff`, `verbalize`, `transition`, `check_with_receipt`, `judgments`; `EvaluationSession.check`, `.check_with_receipt`, `.transition` |
| site, view | `witness`, `replay`, `why_not`, `export_lean`, `export_souffle`, `run_souffle`, `souffle_witness` |
| every-mode | `EvaluationSession.check_with_feedback` (applied always); `EvaluationSession.observe` (returns the caller's own population object) |
| value-free | the rest, each with a note: the classes `CheckReceipt`, `ReceiptRefused`, `EvaluationSession`; `verify_lean`, `verify_souffle`, `compile_lean`; library bindings (`load_model`, `load_population`, `certify_result`, …, and typing and stdlib names) |

`export.service:` rows mirror the seven export functions.

`kind:` rows cover the 13 `OutputKind`s:

- `session-feedback`, `session-attempt` and `session-result` are every-mode.
- The other 10 are site, declared.

**Totality test (T13).**

- **Forward checks:**
  - the set of leaves walked by the RF1 helper `_paths()` equals the CLI keys;
  - `{n for n in dir(gnd.api) if not n.startswith("_") and callable(...)}`
    equals the `api:` names;
  - `redaction.OutputKind` equals the `kind:` keys.
- **Reverse check:** every key resolves to a live leaf, attribute or enum
  member.

### Refusals (D2)

| Situation | CLI | API |
|---|---|---|
| bad or repeated `--disclosure` value | exit 64, argparse usage on stderr, empty stdout | n/a |
| `--disclosure` after the subcommand | exit 64 (unrecognized arguments) | n/a |
| malformed `GND_DISCLOSURE`, disclosure-bearing leaf | exit 3, `gnd: error: GND_DISCLOSURE must be 'internal' or 'customer'`, empty stdout | `DisclosureRefused`, same text |
| `--disclosure internal` with `GND_DISCLOSURE=customer` | exit 3, `gnd: error: --disclosure internal is refused when GND_DISCLOSURE=customer` | n/a |
| raw request under `customer` | exit 3, `gnd: error: --raw is refused in customer disclosure mode` (or `--unredacted`), empty stdout | `DisclosureRefused("raw=True is refused in customer disclosure mode")` (or `unredacted=True`) |

No schema or enum changes. `DisclosureRefused` subclasses `ValueError`, so
existing callers that catch `ValueError` keep working.

### Packaged example: `src/gnd/examples/disclosure/` (NM2-C7)

The example has the following files:

- `model.orm.yaml`: `customer` has email (`redact: true` on the email role),
  plus a mandatory-role or uniqueness constraint so a check reports a violation
  that names a value.
- `population.json`: one violating row.
- `README.md`.

It is listed in `tools/check_installed_docs.py`. NM4's how-to and DC1b run it.

### Isolation (NM2-C6)

- `tests/conftest.py` gains an autouse function fixture,
  `monkeypatch.delenv("GND_DISCLOSURE", raising=False)`. Autouse fixtures are
  allowed (`test_public_collection.py:98-102` forbids only hooks).
- `tools/run_tutorials.py:130` adds `GND_DISCLOSURE` to the popped names.

### Layer and entry-point maps (NM-R7)

- `tools/gnd_layers.json` gets `"gnd.disclosure": {"layer": "checking"}`, with
  zero allowances.
- `tools/gnd_entrypoints.json` gets one exception, `gnd.cli → gnd.disclosure`,
  for the root option and dispatch.
- Importers: `gnd.api` (entry), `gnd.witness.service` and `gnd.export.service`
  (lanes), `gnd.exp.session` and the declared-adapter call site (lanes),
  `gnd.review` (lanes), `gnd.solve` (entry).
- Not importers: `gnd.agents` and `gnd.process`, which take parameters.
- Census successors (RF6 dynamic query, RF1 layering ratchet) are added if the
  tests demand them, as in NM1 F3.

## Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 `(s2)` | Where the witness-lane API projects (H2) | (a) thin `gnd.api` wrappers, as in the plan: breaks the RF4 identity pin for `witness` and `replay`, so it needs a new exemption mechanism in `test_rf4_peripheral.py` or an edit to frozen `moves.json`, and two objects then claim `gnd.api.witness`. (b) The public service functions become mode-aware and the raw bodies move to `*_result` functions that the CLI calls: identity and qualification kept, at the cost of 6 rows in the existing source-successor file. Both leave the CLI projecting raw results itself. | **(b)** |
| D2 `(s2)` | Refusal output | (a) CLI: empty stdout, one stderr line naming the option or variable, exit 3; API: `DisclosureRefused(ValueError)`. No schema change; precedent: `diff` and `verbalize` refusals (`checking.py:239-263`). (b) Per-lane JSON envelopes: a new reason in `why-not.schema.json` and the witness schemas (a closed enum change in `/1`), plus a payload the check-family report schema cannot express without a model. | **(a)** |
| D3 `(s2)` | Where the mode applies (H3) | (a) CLI: one walk in `cli.main` over the namespace (refuse under customer, set to true under internal); API: one call per public site; internal callers bypass. (b) The plan's `_run_*` helpers: `judgments` is refused under customer and session feedback unredacted under internal. | **(a)** |
| D4 `(s2)` | Runner masking (H4) | (a) a `disclosed_names` parameter on `run_bounded_process` (infrastructure gains a parameter, NM-R7). (b) Forward without it: agent and reviewer output loses every "customer". (c) Forward a short token instead of `customer`: contradicts NM-D2's values. | **(a)** |
| D5 `(s2)` | Review-panel reviewers under customer | (a) forward, by the plan's rule "every spawner that runs GND or an agent". (b) do not forward: reviewers read plans, not populations. | **(a)** |
| D6 `(s2)` | RF1 goldens need Python 3.11 (H5) | (a) `uv python install 3.11` here (downloads a uv-managed interpreter). (b) capture 3.11 on beast-3, if it has one. (c) skip 3.11: the merge tool refuses a partial set. | **(a)**, with your yes, since it downloads |
| D7 `(s2)` | Approval instrument | NM2 includes an exit-code contract, so corpus-first is the default. (a) This prose. The table under Refusals and the T1–T12 rows are the exit corpus; the harness for them is committed red as the first implementation commit, before any source file changes. (b) A separate committed corpus and README, authored before this gate. | **(a)**: the exits are few and fully listed above; a separate corpus would restate them |

## Tests

Unless stated, tests are in `tests/test_disclosure_mode.py`. CLI cases use
`run_main` in-process with `monkeypatch.setenv`/`delenv`. Every expected exit is
literal.

| ID | Case | Expected |
|---|---|---|
| T1 | `resolve` matrix: (ctx, env) ∈ {None, internal, customer}² | customer if either says so; else ctx, then env |
| T2 | `values_allowed` matrix: requested ∈ {F, T} × mode ∈ {None, internal, customer} | unset → requested; internal → True; customer → False, or `DisclosureRefused` when requested |
| T3 | Hostile `GND_DISCLOSURE`: `""`, `"Customer"`, `"customer "`, `"CUSTOMER"`, `"ïnternal"`, 65,536 × `"x"` | `DisclosureRefused` from `resolve`; CLI `gnd check M P` exits 3 with the variable message and empty stdout |
| T4 | Malformed env on a value-free leaf (`gnd coverage M`) and an every-mode leaf (`gnd discover …`) | exit and bytes as without the variable |
| T5 | `gnd --disclosure bogus check M P`; `gnd --disclosure customer --disclosure customer check M P` | exit 64, empty stdout |
| T6 | `gnd check M P --disclosure customer` | exit 64 |
| T7 | `GND_DISCLOSURE=customer gnd --disclosure internal check M P` | exit 3, loosening message |
| T8 | `GND_DISCLOSURE=customer gnd --disclosure customer check M P`; `GND_DISCLOSURE=internal gnd --disclosure customer check M P` | runs under customer (the T16 assertions) |
| T9 | Order: malformed env plus `--disclosure internal` | exit 3, the **variable** message |
| T10 | Order: `GND_DISCLOSURE=customer`, `--disclosure internal` and `--unredacted` | exit 3, the **loosening** message |
| T11 | Every raw dest under customer: `--unredacted` on the 7 declared leaves, `--raw` on the 8 view leaves | exit 3, the option's message, empty stdout; handler not called (a patched handler counter stays 0) |
| T12 | Token reset: `run_main([... "--disclosure", "internal", ...])`, then `disclosure.resolve()` in the same process | `None` |
| T13 | `SURFACES` totality and reverse check (Design) | equal sets; every key live |
| T14 | Negative control for T13: an injected leaf or API name, and a stale key | the check fails |
| T15 | Every `site` row is named by a T16–T25 case, and every `every-mode` row by T26 or, for `exp run` and the `kind:session-*` rows, by T34 plus the unchanged RF1 session pins | asserted over `SURFACES` against a case-to-key map in the test file |
| T16 | Customer leak, check family, over `examples/disclosure`: `check`, `validate`, `diff`, `verbalize population`, `measure`, `verify`, `judgments check` (CLI JSON) and the 7 API functions | the declared email values absent from stdout and payload; exit as unset |
| T17 | Internal, the same sites | equal to the same call with `--unredacted` / `unredacted=True` under unset |
| T18 | Unset, the same sites | equal to the call with no variable (parity) |
| T19 | `api.why_not` over the quoted-claims gap case: unset, internal, customer | raw with no `view` key (unset and internal, equal bytes); customer equals `{**why_not_view(raw), "view": "redacted"}` and contains no population value |
| T20 | `api.witness` and `api.replay`: unset, internal, customer | raw; raw; `result_view(raw)` |
| T21 | `api.witness is gnd.witness.service.witness` (and `replay`, `why_not`) | true (D1 (b)) |
| T22 | CLI view leaves under customer, default flags | equal bytes to unset default output |
| T23 | CLI view leaves under internal, no `--raw` | equal bytes to unset output with `--raw` |
| T24 | `gnd --disclosure internal witness … --out F` | exit as unset with `--raw --out F`; F written with the same bytes |
| T25 | Export functions and leaves: customer `raw=True` raises; internal without `raw` equals unset with `raw=True` (`run_souffle` `extensions` present; `souffle_witness` certificate present); customer default equals unset default | as stated; tests needing `souffle` or `lake` skip only when the tool is absent, and the skip is counted in the record |
| T26 | Every-mode rows across the three states: `discover`, `export ilp`, `fidelity` (CLI); `check_with_feedback` | identical bytes in all three |
| T27 | `api.judgments(unredacted=False)` under customer | returns (not refused); `judgment_policy` redacted, as unset |
| T28 | Spawner AST walk over `src/gnd` (excluded paths as in the layer map) | equals the spawner table's sites |
| T29 | Unset and internal: `invoke_agent` facts and env; declared-adapter env; review `seat_environment`; solve `Popen` kwargs | byte-identical to the pinned RF1 goldens; solve gets no `env` keyword |
| T30 | Customer: `invoke_agent` (fake agent CLI that prints its environment) | `GND_DISCLOSURE=customer` present; fact `(GND_DISCLOSURE, supplied)` |
| T31 | Customer: declared command adapter (fake) | as T30 |
| T32 | Customer: `solve` (patched `Popen`) | `env` contains `GND_DISCLOSURE=customer`; argv as unset |
| T33 | Customer: review adapter (fake reviewer) | as T30 |
| T34 | `verifier_environment()` and `tests_environment()` under customer | no `GND_DISCLOSURE` |
| T34b | D4: a fake agent printing `customer` under customer | stdout keeps `customer`; a `run_bounded_process` call without `disclosed_names` still masks a ≥4-character value (existing `test_agent_cli.py:318-355` unchanged) |
| T35 | Unset parity: the §9 NM2 suites with no edit except T36's files | exit 0 |
| T36 | RF1 goldens regenerated with `tools/rf1_pins.py capture` (3.11, 3.13, 3.14) and `merge`: 12 cli-exit goldens with the root usage line, 3 `cli-help/gnd.py31{1,3,4}.json`, `cli/tree.json`, `goldens.sha256`, `MANIFEST_SHA256` | the diff touches only those files; each diff is the `--disclosure` usage and help text |
| T37 | Isolation fixture: a test that reads `os.environ` | no `GND_DISCLOSURE` even when the outer process sets it |
| T38 | Negative control: a subprocess `pytest` over `tests/test_rf1_cli_pins.py` and T18 with `GND_DISCLOSURE=customer` in its environment | exit 0 |
| T39 | `examples/disclosure` validates and its check exits 1 with a redacted marker under unset | as stated |
| T40 | `gnd --help` mentions `--disclosure` and "root option" | as stated |
| T41 | `tests/test_rf1_layering.py`, `tests/test_rf6_query_policy.py`, `tests/test_gnd_arch.py`, `tests/test_rf4_peripheral.py`, `tests/test_rf8_structure.py` | exit 0, zero allowances, one entry-point exception |
| T42 | `tests/test_why_not_anonymity.py` | exit 0 |

### Verification selection

| Obligation | Disposition | Command | Input boundary | Justification | Invalidation |
|---|---|---|---|---|---|
| Plan §9 NM2 row (mandated) | run | `uv run pytest -q tests/test_why_not_kernel.py tests/test_why_not_oracle.py tests/test_public_why_not.py tests/test_why_not_anonymity.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py tests/test_disclosure_mode.py tests/test_public_api.py tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_rf5_commands.py tests/test_rf5_handler_pins.py`, exit 0 | as Design | the NM1 gate plus the disclosure, API, CLI-pin and RF5 suites the plan names | any source or golden in Design |
| The "redaction, session and agent-environment tests the NM2 spec names" (plan §9) | run | `uv run pytest -q tests/test_rf1_agent_cli_pins.py tests/test_rf1_session_pins.py tests/test_rf2_instrument.py tests/test_agent_cli.py tests/test_review_runner.py tests/test_solve.py tests/test_rf8_sessions.py tests/test_public_tests_mode_corpus.py tests/test_public_local_command_adapter_controls.py tests/test_rf4_peripheral.py tests/test_rf8_structure.py tests/test_rf2_pre_move_pins.py tests/test_public_reference_signatures.py tests/test_v61_phase2_api.py tests/test_public_runtime.py`, `tests/test_public_redaction_reports.py tests/test_public_report_redaction_metadata.py tests/test_v62_phase{1,2,3,4,5,6}_redaction.py tests/test_v70_phase3_redaction.py`, exit 0 | `process.py`, `agents.py`, `exp/*`, `review/adapters.py`, `solve.py`, `api.py`, `witness/*`, `export/service.py` | each pins an environment, a session record, an API signature or a redaction output this phase can change | a change to any of those modules |
| Docs runner isolation | run | `uv run pytest -q tests/test_documentation_tutorials.py -k "quickstart or api"`, exit 0 | `tools/run_tutorials.py` | one changed line in the runner; two groups exercise it | a runner change |
| Broad default suite | cadence | milestone close, on explicit owner selection | whole repository | NM2 touches about 18 modules but every changed path is covered above | an owner selection |

### Implementability sweep (before the gate)

Each requirement was checked against `acfb9ae`:

- **The root option before the subcommand**: argparse places it on the root
  parser (`cli.py:633-639`). The same option after the subcommand is an
  unknown argument, and `_BandSafeParser` turns that into exit 64.
- **The CLI walk can see every raw dest**: the namespace carries `raw` or
  `unredacted` exactly on the 15 site leaves (survey, `_arguments.py:60-65`,
  `judgments.py:15`, `witness/cli.py:18-40`, `lean_cli.py:18`,
  `souffle_cli.py:19-20`). T11 enumerates them from the parser tree, not from
  this list.
- **D1 (b) keeps identity**: the API aliases are untouched. The body test
  accepts a current successor row (`rf9_ci_sources.py:58-68`), and an existing
  frozen RF9 row for the same name is chained by construction.
- **D3**: `_check_unresolved` holds `check`'s current body, so the public
  signature pins (`test_public_api.py:15-35`) are unchanged.
- **D4**: `_sensitive_values` takes the environment mapping. Filtering by a
  name set before it is a local change, and the default keeps every existing
  caller's output.
- **The forwarding sites can import `gnd.disclosure`**: they are rank ≥ 2
  (`gnd.exp.*`, `gnd.review.*` lanes; `gnd.solve` entry, outside the
  entry-point scope). `gnd.agents` and `gnd.process` (rank 0) take parameters.
- **T29 can compare against goldens**: the RF1 agent and session goldens exist
  and pin facts and attempt records (`test_rf1_agent_cli_pins.py:139-173`,
  `test_rf1_session_pins.py`).
- **T36 needs Python 3.11** (D6). Without it, T36 cannot run and NM2 cannot
  pass its gate.

No requirement was found that no implementation can satisfy, given D6.

## Out of scope for this phase

- Why-not near-misses on the public path, and the `/2` schema (NM3).
- All documentation pages (NM4; DC1b follows this phase).
- Redacting undeclared check-family values.
- A configuration file or per-tenant modes.
- Re-projecting retained evidence.
- Binding an agent's own environment.
- Any change to session kinds, `discover`, ILP export or `fidelity` output.

## Size

About 330 source lines across 14 modules (`disclosure`, `cli`, `api`,
`witness/service`, `witness/cli`, `export/service`, `process`, `agents`,
`exp/session`, the declared-adapter call site, `review/adapters`, `solve`, and
the two tool maps). About 650 test lines. Plus the example, about 18 regenerated
RF1 golden files, six source-successor rows and any census successors.

## Approval instrument

This prose (D7 (a)).

## Implementation findings

Recorded as found, 2026-11-01.

- **F1 (refutes H5).** `uv python install 3.11` reported that 3.11 was already
  installed, so nothing was downloaded. The RF1 captures ran in two scratch
  virtual environments (3.11.15 and 3.13.12) and the project environment
  (3.14.3), as WN2 did.
- **F2 (RF5 pin; no behaviour change).** `test_rf5_commands.py:111` pins
  `main()`'s last statement to `return args.handler(args)`. The mode is
  therefore applied by replacing `args.handler` with a wrapper (`_disclosed`)
  that sets and resets the context variable. The walk and the refusal keep the
  order of the Refusals table.
- **F3 (more successor rows than designed).** `run_bounded_process`, its
  `_result` and `invoke_agent` are RF4 moves out of `gnd.agent_cli`, so D4 and
  the agent forwarding add three current source-successor rows. That makes nine
  rows, not six.
- **F4 (no new public name).** `gnd.api` imports the helper as
  `_values_allowed`. T13 caught the public `values_allowed` binding.
- **F5 (table rows).** `EvaluationSession.reset`, `close` and `stats` were
  missing from the spec's table. They are value-free, and T13 caught them.
- **F6 (forwarding site).** Declared-adapter forwarding sits in
  `gnd.declared_adapter._invoke_command`, which is in the same `exp` lane and
  layer as `gnd.exp`. One site covers the schema-v6 command policy and the
  v7/v8 declared sessions. The legacy path passes `extra_environment` only when
  it is non-empty, so injected test invokers and unset calls are unchanged.
- **F7 (spawner walk).** T28 counts callers of `run_bounded_process` as spawn
  sites, so table rows 2–10 are found. `lean_runtime` spawns through
  `souffle_runtime.command`, which is covered by row 11.
- **F8 (test reach; recorded, not hidden).** Coverage per case:
  - T16 runs end to end for `check` (CLI) and for `check`, `verbalize`,
    `check_with_receipt` and the two delegating `EvaluationSession` methods
    (API).
  - For `validate`, `diff`, `transition` and `judgments`, T16 covers the
    customer refusal plus the generic CLI walk test over all 15 site leaves.
    That walk shows each dest is set to the mode's value; no leak run was made
    for these four.
  - T25 tests raw resolution at the I/O seam (`souffle_io.export_souffle`,
    `souffle_runtime.run_souffle`) rather than with a real `souffle` or `lake`.
    `souffle_witness` and `export_lean` are covered only by the customer
    refusal.
- **F9.** Three `cli.py` imports lost their `noqa: F401`, because the new code
  uses them.
- **F10 (review R1, refutes a table row; owner-visible).** `gnd doccheck`
  prints the population values a rendered document misses, declared `redact`
  roles included, in every mode. The spec's table classed it value-free. It is
  now **every-mode**, beside `fidelity`, under NM-D13's "any further row NM2-C2
  classifies every-mode". It is not made a site: that would change the fidelity
  family, which NM-D13 keeps unchanged. `disclosure.md` (NM4) must list it.
- **F11 (review R3).** `invoke_agent` takes `disclosed_names` as well as
  `extra_environment`, so only names the caller declares non-secret are
  unmasked. A name that overrides an inherited one is recorded once, as
  supplied.
- **F12 (review R9).** The isolation scrub runs when `tests/conftest.py` is
  imported, not as a function fixture, so fixtures of every scope see no
  ambient mode.
- **F13 (review R4).** The CLI walk treats an enclosing in-process customer
  context like `GND_DISCLOSURE=customer`, as `gnd.api` does.
