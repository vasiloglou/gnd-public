# Plan review — round 1 disposition

2026-10-27. Owner-selected instrument (plan D5, selected 2026-10-27 in reply to
the review question (o)): **four local reviewer agents**, as in the
induced-knowledge milestone. The selection names the instrument only. It does
not approve the plan or spec bytes or authorize implementation.

## Subjects and limits

- Reviewed plan r1 SHA-256:
  `6cb10d973862fabfe3bd21833d1d2a69541b33646c12b8e37e39b4137198e463`.
- Supporting IL1 spec r1 SHA-256:
  `596291739134f66c113b5800a50535e9c89e8506f9d7a4f7689ee2663e46b027`.
- Inspection HEAD: `63f7f1f` on `claude/ilp-packages-integration-cf0a0f`.

Retained exact snapshots: the [plan](../evidence/plan-review-r1/ilp-learners-plan.md)
and the [IL1 spec](../evidence/plan-review-r1/phase-IL1-spec.md). The readers'
line citations refer to these snapshots. The
[manifest](../evidence/plan-review-r1/manifest.json) records the snapshot and
reader-note digests.

**How the readers ran:**
- Each started with fresh context and received the subject digests and a
  different lens. Each verified both digests and read the whole plan and spec
  plus the relevant sources.
- All four ran concurrently as local model agents of one model family. They
  were not humans or a provider panel, and no vendor diversity is claimed.
- No installs, credentials, network or paid tools were used.

**Side effects:**
- Readers 1, 2 and 4 wrote probe files only under the session scratchpad.
- Reader 4's first `uv run` created a gitignored `.venv/` in the worktree. No
  tracked file changed.

**Edits to the retained notes:**
- Reader 4's note had an absolute scratch path containing the host username.
  It was replaced with `<scratchpad>` (IK-R10).
- Otherwise each note keeps the reader's returned text.

## Opinions

| Reader | Lens | Verdict | Blocking | Hardening | Completeness |
|---|---|---|---|---|---|
| [1](plan-review-r1-reader-1.md) | semantics and admission safety | request-changes | 4 | 5 | 3 |
| [2](plan-review-r1-reader-2.md) | implementability, homes and layers | request-changes | 6 | 3 | 3 |
| [3](plan-review-r1-reader-3.md) | protocol, authority, compatibility, privacy | request-changes | 2 | 7 | 2 |
| [4](plan-review-r1-reader-4.md) | measurability and reproducibility | request-changes | 2 | 7 | 3 |

That is 47 findings and 14 blocking, with overlaps. Reader 1 confirmed the
admission gate holds: nothing an adapter emits can become `confirmed` or
`alethic` without review (`_enforce_d12`, `_envelope`).

## Coordinator reproduction

I checked each blocking finding against the reviewed bytes and the code at
`63f7f1f`.

| Finding | Check | Result |
|---|---|---|
| R3-F1, R2-F3, R4-F4 | `grep -rln "{popper,neutral}" tests/fixtures/rf1-pins/goldens` hits 8 help and exit goldens; `commands/export.py:108` and `checking.py:452` declare `("popper", "neutral")` in that order | reproduced |
| R2-F1 | `tests/test_ik6_walk.py:118,138,158` export with `--target neutral` | reproduced |
| R2-F2 | `tools/gnd_entrypoints.json` binds the export commands to `gnd.export.ilp_service`; `tools/gnd_arch.py:861` flags any other import ("entry-point imports a non-service module") unless an exception row exists. The spec names neither a row nor a route through the service | reproduced |
| R2-F4, R4-F2 | `parse_program("wrong(A):- f(A,B,'\001\').")` and `'\101\'` both exit 3 `unexpected "'"`: the tokenizer fails before `_unquote` runs | reproduced |
| R1-F11, R2-F5, R4-F1 | `int('4000000', 8)` is `0x100000`, a valid scalar; `oct(0x10FFFF)` is `0o4177777` | reproduced |
| R2-F6, R4-F12 | `ilp-import.schema.json:30–34` and `ilp.schema.json:254–258` enumerate `target` as `popper`, `neutral` | reproduced |
| R1-F2 | `uv run gnd validate` on reader 1's scratch model, which binds `$x` as a refund amount and as a refund in one guarded antecedent: exit 0, "is a valid GND ORM model". The same model also loads `inducer: popper` with `method: ilp-neutral` (R1-F7) | reproduced. **This gap is in the shipped bridge today**, for `--target neutral` |
| R1-F3 | `ilp_rewrite.py:147–157`: with one atom and no comparison, no other atom binds its variables, so designation refuses `non-ground-absence` | reproduced by reading |
| R1-F1, R4-F10 | the plan defines neither side of "support" for IL4; guarded evaluation enumerates full antecedent bindings (`representation-format.md:535–547`) | reproduced as a documented gap |
| R3-F3 | `gnd.agents` forwards provider credentials (`agents.py:178–205`); the owner's live-run answer named Prolog and ASP tools, not an agent, model or spend | reproduced by reading |
| R4-F7 | plan:38–40 is satisfied by any run that has a record; T6 decides no gate | reproduced by reading |

No finding was refuted. Medium and low findings are accepted on their
citations. Two readers' "verified correct" lists agree with the author's
earlier checks (`LEARNER` has no outside user; the `live` marker exists).

## Findings grouped by repair

| Theme | Findings | Proposed repair (r2) | Owner ruling |
|---|---|---|---|
| A. IL1 registry and CLI compatibility | R3-F1, R2-F1, R2-F2, R2-F3, R4-F4, R4-F5, R2-F11 | The registry keeps declaration order (`popper`, `neutral`, later targets appended), and `neutral` stays exportable. The commands keep their literal `choices=`, so there is no new entry-point edge and no import at parser-construction time; a T2 test asserts by parser introspection that they equal the registry tuples. A monkeypatched fake entry shows the registry is actually consulted (render, method, learner check). The IL1 gate becomes a literal file list: the readers' seven control files plus `test_ik_close.py`, a named consumer. The source-order tokens in `test_ilp_bridge.py:393–409` are kept | none |
| B. Octal escapes | R1-F11, R2-F4, R2-F5, R4-F1, R4-F2, R4-F3 | The change goes into `_TOKEN` (octal alternative before `\\.`) and into `_unquote`. Fixed T4 cases: `'\4200000\'` refuses as beyond Unicode, `'\4177777\'` is accepted, `'\154000\'` refuses as a surrogate, and a token-boundary case is added. The refusal message is octal-specific. `'\101'` (unclosed) is labelled deliberate strictness. The complete escape list is taken from the pinned SWI version at the gate | none |
| C. Live-run honesty and falsifiability | R4-F7, R4-F8, R4-F9, R1-F8, R1-F12, R3-F10, R3-F11, R2-F9 | **Before the run, a closed outcome list:** rendering-rejected, no-solution, learner-timeout, wall-clock-kill, unparsable, named refusal, admitted. **Popper's own timeout** is set below the wall clock, and all six `ProcessLimits` fields are fixed. **The script** extracts the program block and keeps raw stdout separately. **Coverage** comes from an evaluator that is not GND (SWI), named in the record and called "independent evaluation"; Popper's printed counts are kept verbatim and compared. **Every invocation** is numbered and retained, and the first one after the gate is the run of record. **A rendering or settings fix** is an owner-recorded amendment that names the golden changes and the `adapter_version` bump; a parser-only fix stays in scope. **A default-gate replay test** re-imports the committed program and run record and asserts the recorded exit. **Each record states** where each number came from, its seeds and threads, and "single run, reproducibility not measured" | none |
| D. Wire enums | R2-F6, R4-F12 | Plan §5 states the per-phase enum change. IL1 adds a test that both schema enums equal the registry targets | **D9** |
| E. Semantics of the new adapters | R1-F1, R4-F10, R1-F2, R1-F3, R1-F4, R1-F5, R1-F6, R1-F9, R1-F10, R4-F11, R2-F7 | **Joins:** a `type-confused-join` fragment check in the shared rewriter, for every target (D12). **IL2:** background holds comparisons only; each population's facts go, untagged, into its own context; `#modeb` arity is predicate arity minus 1; the ASP refusal list adds classical negation, arithmetic, intervals and pools, and directives; a constants row covers three kinds. **IL3:** thresholded features only, or unthresholded ones counted as expected `non-ground-absence`; a polarity table (negated literal → `negation-as-failure`); the schema declares each column's meaning. **IL4:** support and confidence fixed over distinct head pairs; pair ids are opaque fact ids; head fact types outside `covers` are flagged; its CLI shape (`--population`, no labels) and RF1/RF5 effects are named now. **Registry:** the `contract` and `render` input are open to sibling contracts. **IL6:** columns are proposed, import exit, first refusal and its clause index, clauses not evaluated; AMIE gets its own unlabelled row; a "no output" row; each live run is bound to a named refunds export digest | **D10**, **D11**, **D12** |
| F. IL5 (LLM) | R3-F3, R1-F7, R2-F8 | IL5 gets its own registry entry: `target: llm`, `method: ilp-llm`, learner name equal to the agent adapter id. A neutral run record naming a registered learner refuses `learner-mismatch`. The prompt builder gets a source home in the `export` lane. The model id is recorded as reported. IL5-C3 is blocked until D8 | **D8** |
| G. Authority and protocol | R3-F2, R3-F4, R3-F5, R3-F6, R2-F12 | **Owner words:** quoted verbatim in the README and in D1/D2. "Popper included", "never in CI" and "neural out" are labelled proposed. IK5-D13 (a) and 012:151 are cited as superseded by the 2026-10-27 answer. **Installs** stay in a scratch prefix: no system package manager, no `sudo`, no profile edits. Prebuilt binaries and jars are downloads, approved per gate with URL, name, size and SHA-256. **D5** is recorded as selected, without the "none" option. **The review budget** and stop rule are declared below. **Approval** is recorded in `001-plan-gate.md`, binding digests. **The spec's §4** binds every IL-R and IK-R rule by name. **The DAG** shows the serial chain | **D2** confirmation |
| H. Privacy, licences, inputs | R3-F7, R3-F8, R3-F9 | **An IL1 test T8** scans this milestone directory for home paths, usernames and the downstream digests, with a negative control. **Evidence scripts** pass `HOME`, `USER` and `TMPDIR` into the bounded environment. **A new IL-R rule:** every live run reads only the IK6 refunds example or a committed synthetic fixture. **Licences** are recorded from a cited upstream URL before any download; anything that is not a permissive OSI licence, or that has a click-through, stops for the owner. **T7** also reads the built wheel's `Requires-Dist` | none |
| I. Join space | R4-F6, R2-F10 | IL1-C5 is restated: the importer half is already closed by IK5 case I2. A fixture is added on which the stand-in learner yields a join candidate, or the stand-in row stays carried | none |

## Decisions the repairs need

| ID | Question | Readings and cost | Proposed |
|---|---|---|---|
| D2 (confirm) | Does "Yes, one recorded run each" cover a JVM plus AMIE, ILASP/FastLAS binaries and a Python rule-set package, which the question did not name? Installs confined to a scratch prefix, with each download approved at its gate | **Yes:** proceeds as planned. **Popper/SWI/clingo only:** IL2–IL4 use hand-written fixtures, as IK5 did | ask at the plan gate |
| D8 | The IL5 live run: agent adapter and model, credential source (imported by name from the documented trusted environment), call or cost ceiling, prompt limited to the synthetic IK6 export, provider output terms | Ruled at the IL5 gate; IL5-C3 stays blocked until then | at IL5 gate |
| D9 | New `--target` values widen two closed `target` enums | **Widen within `/1`:** every existing document stays valid, but a consumer pinned to the old schema rejects new documents. **Bump to `/2`:** explicit, but it costs a second schema version and moves the goldens | widen within `/1`, recorded per IL-R7 |
| D10 | Admission granularity for the new adapters | **All-or-nothing everywhere** (IK5-D9 unchanged); the comparison table reports the first refusal. **Per disjunct for IL3 rule sets:** sound for unordered DNF, but it mixes refusal with exit 0 | all-or-nothing |
| D11 | IL4: which mined rules are admitted | **Holds only** (parity with `gnd discover`); no number to choose. **A confidence floor** fixed now (for example ≥ 0.9): admits more, with counterexamples, but a deontic warning fires on the mined population | holds only |
| D12 | A `type-confused-join` check in the shared rewriter | **Add it in IL1, for every target, `neutral` included:** this changes shipped import behaviour; a clause that joins different object types is refused. IK5 goldens stay unchanged unless a corpus case is type-confused. **Defer it to IL2:** leaves the shipped gap open longer | add in IL1 |

## Convergence budget (declared before any round two)

- **Round 1:** self-inflicted ratio 0 / 47 (first round over a first draft).
  Severity ceiling: high. Same-seat counts: 12 / 12 / 11 / 12.
- **Budget:** one repair revision (r2), after the owner rules D2 and D8–D12,
  then **at most one** confirmation round by the same four lenses. That round
  is restricted to whether the reproduced blocking findings are resolved.
- **Stop rule,** exactly as in
  `.claude/skills/process-phase/references/review-convergence.md`: stop when
  the self-inflicted ratio exceeds one half, or when same-seat counts are flat
  or rising for two consecutive rounds while severity falls.
- **After review:** any remaining design questions move into the phase specs,
  where the code is the instrument.

## Boundary

- **r1 is not approved.** No r2 bytes exist yet, and r2 will carry no review
  opinion until the confirmation round reads it.
- **One model family.** The readers are one model family, run locally; each is
  one reading.
- **Licences are unverified.** No reader checked a licence upstream. They stay
  open under IL-R5.
